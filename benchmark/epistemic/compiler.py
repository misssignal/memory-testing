"""Compile structured memories into claims, relations, and evidence roots.

This module deliberately does not inspect ``_oracle`` or ``truth_role``.  It is
the production side of the benchmark: identical public input always produces
identical graph output without an LLM or embedding model.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable


SPACE = re.compile(r"\s+")
RELATION_FIELDS = ("derived_from", "supersedes", "contradicts")


def normalize_text(value: Any) -> str:
    """Canonicalize a scalar for identity comparison, not display."""
    text = unicodedata.normalize("NFKC", str(value))
    return SPACE.sub(" ", text).strip().casefold()


def canonical_scope(scope: dict[str, Any] | None) -> str:
    """Return a stable JSON identity for non-null scope dimensions."""
    normalized = {
        normalize_text(key): _normalize_value(value)
        for key, value in (scope or {}).items()
        if value is not None
    }
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            normalize_text(key): _normalize_value(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    return normalize_text(value)


@dataclass(frozen=True, order=True)
class ClaimKey:
    subject: str
    predicate: str
    object: str
    scope: str

    @classmethod
    def from_memory(cls, memory: dict[str, Any]) -> "ClaimKey":
        return cls(
            subject=normalize_text(memory["subject_entity_id"]),
            predicate=normalize_text(memory["predicate"]),
            object=normalize_text(memory["object"]),
            scope=canonical_scope(memory.get("scope")),
        )

    @property
    def id(self) -> str:
        raw = json.dumps(
            [self.subject, self.predicate, self.object, self.scope],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()
        return "claim_" + hashlib.sha256(raw).hexdigest()[:20]

    def to_dict(self) -> dict[str, str]:
        return {
            "claim_id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "scope": self.scope,
        }


@dataclass(frozen=True, order=True)
class Edge:
    source: str
    relation: str
    target: str

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "relation": self.relation, "target": self.target}


@dataclass
class ClaimNode:
    key: ClaimKey
    memory_ids: list[str] = field(default_factory=list)
    evidence_root_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = self.key.to_dict()
        result.update(
            memory_ids=sorted(self.memory_ids),
            evidence_root_ids=sorted(self.evidence_root_ids),
            independent_root_count=len(set(self.evidence_root_ids)),
        )
        return result


@dataclass
class EpistemicGraph:
    memories: dict[str, dict[str, Any]]
    claims: dict[str, ClaimNode]
    edges: list[Edge]
    evidence_roots_by_memory: dict[str, tuple[str, ...]]
    derivation_cycles: list[tuple[str, ...]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1.0",
            "counts": {
                "memories": len(self.memories),
                "claims": len(self.claims),
                "edges": len(self.edges),
                "derivation_cycles": len(self.derivation_cycles),
            },
            "claims": [self.claims[key].to_dict() for key in sorted(self.claims)],
            "edges": [edge.to_dict() for edge in sorted(self.edges)],
            "evidence_roots_by_memory": {
                key: list(self.evidence_roots_by_memory[key])
                for key in sorted(self.evidence_roots_by_memory)
            },
            "derivation_cycles": [list(cycle) for cycle in sorted(self.derivation_cycles)],
        }


def compile_memories(memories: Iterable[dict[str, Any]]) -> EpistemicGraph:
    """Compile public structured memory fields into a deterministic graph."""
    records: dict[str, dict[str, Any]] = {}
    for raw in memories:
        memory = _public_memory(raw)
        memory_id = memory["memory_id"]
        if memory_id in records:
            raise ValueError(f"duplicate memory_id: {memory_id}")
        records[memory_id] = memory

    edges: list[Edge] = []
    for memory_id, memory in records.items():
        for relation in RELATION_FIELDS:
            for target in memory[relation]:
                if target not in records:
                    raise ValueError(f"{memory_id}.{relation} references missing memory {target}")
                edges.append(Edge(memory_id, relation, target))

    roots, cycles = _compute_evidence_roots(records)
    claims: dict[str, ClaimNode] = {}
    for memory_id, memory in records.items():
        key = ClaimKey.from_memory(memory)
        node = claims.setdefault(key.id, ClaimNode(key=key))
        node.memory_ids.append(memory_id)
        node.evidence_root_ids.extend(roots[memory_id])
    for node in claims.values():
        node.evidence_root_ids = sorted(set(node.evidence_root_ids))

    return EpistemicGraph(
        memories=records,
        claims=claims,
        edges=edges,
        evidence_roots_by_memory=roots,
        derivation_cycles=cycles,
    )


def _public_memory(raw: dict[str, Any]) -> dict[str, Any]:
    required = (
        "memory_id",
        "subject_entity_id",
        "predicate",
        "object",
        "event_time",
        "observation_time",
        "ingestion_time",
    )
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"memory missing required fields: {', '.join(missing)}")
    return {
        "memory_id": str(raw["memory_id"]),
        "subject_entity_id": str(raw["subject_entity_id"]),
        "subject_text": str(raw.get("subject_text", "")),
        "predicate": str(raw["predicate"]),
        "object": str(raw["object"]),
        "text": str(raw.get("text", "")),
        "scope": dict(raw.get("scope") or {}),
        "event_time": str(raw["event_time"]),
        "observation_time": str(raw["observation_time"]),
        "ingestion_time": str(raw["ingestion_time"]),
        "source_id": str(raw.get("source_id", "")),
        "source_type": str(raw.get("source_type", "")),
        "memory_type": str(raw.get("memory_type", "")),
        "derived_from": sorted(set(map(str, raw.get("derived_from") or []))),
        "supersedes": sorted(set(map(str, raw.get("supersedes") or []))),
        "contradicts": sorted(set(map(str, raw.get("contradicts") or []))),
        "aliases_used": sorted(set(map(str, raw.get("aliases_used") or []))),
        "tags": sorted(set(map(str, raw.get("tags") or []))),
    }


def _compute_evidence_roots(
    records: dict[str, dict[str, Any]],
) -> tuple[dict[str, tuple[str, ...]], list[tuple[str, ...]]]:
    memo: dict[str, tuple[str, ...]] = {}
    cycles: set[tuple[str, ...]] = set()

    def visit(memory_id: str, path: tuple[str, ...]) -> tuple[str, ...]:
        if memory_id in memo:
            return memo[memory_id]
        if memory_id in path:
            start = path.index(memory_id)
            cycle = path[start:] + (memory_id,)
            cycles.add(_canonical_cycle(cycle))
            return ()
        parents = records[memory_id]["derived_from"]
        if not parents:
            result = (memory_id,)
        else:
            result = tuple(
                sorted({root for parent in parents for root in visit(parent, path + (memory_id,))})
            )
        memo[memory_id] = result
        return result

    for memory_id in sorted(records):
        visit(memory_id, ())
    return memo, sorted(cycles)


def _canonical_cycle(cycle: tuple[str, ...]) -> tuple[str, ...]:
    body = cycle[:-1]
    rotations = [body[index:] + body[:index] for index in range(len(body))]
    canonical = min(rotations)
    return canonical + (canonical[0],)
