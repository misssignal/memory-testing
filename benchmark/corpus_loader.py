"""Load and index the synthetic corpus for ground-truth lookups."""
from __future__ import annotations

import json
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CorpusIndex:
    """Pre-computed indexes over the corpus for ground-truth construction."""
    records: list[dict[str, Any]]
    by_id: dict[str, dict[str, Any]]
    by_subject: dict[str, list[dict[str, Any]]]
    by_predicate: dict[str, list[dict[str, Any]]]
    by_subject_predicate: dict[tuple[str, str], list[dict[str, Any]]]
    by_status: dict[str, list[dict[str, Any]]]
    by_expected_behavior: dict[str, list[dict[str, Any]]]
    by_source_id: dict[str, list[dict[str, Any]]]
    by_text: dict[str, list[dict[str, Any]]]
    supersession_chains: dict[tuple[str, str], list[dict[str, Any]]]
    conflict_groups: dict[tuple[str, str], list[dict[str, Any]]]
    alias_map: dict[str, list[str]]
    duplicate_clusters: dict[str, list[str]]
    corpus_hash: str = ""

    @property
    def subjects(self) -> list[str]:
        return sorted(self.by_subject.keys())

    @property
    def projects(self) -> list[str]:
        return [s for s in self.subjects if self._is_project(s)]

    @property
    def people(self) -> list[str]:
        return [s for s in self.subjects if not self._is_project(s)]

    def _is_project(self, subject: str) -> bool:
        return any(
            r["memory_type"] == "project_event" or r["predicate"] == "created"
            for r in self.by_subject.get(subject, [])
        )

    def active_latest(self, subject: str, predicate: str) -> dict[str, Any] | None:
        recs = self.by_subject_predicate.get((subject, predicate), [])
        active = [r for r in recs if r["status"] == "active"]
        if not active:
            return None
        return max(active, key=lambda r: r["timestamp"])

    def timeline(self, subject: str, predicate: str) -> list[dict[str, Any]]:
        recs = self.by_subject_predicate.get((subject, predicate), [])
        return sorted(recs, key=lambda r: r["timestamp"])


def load_corpus(path: str | Path) -> CorpusIndex:
    path = Path(path)
    if path.is_dir():
        path = path / "memories.jsonl"

    raw = path.read_bytes()
    corpus_hash = hashlib.sha256(raw).hexdigest()[:16]

    records = [json.loads(line) for line in raw.decode().strip().split("\n") if line.strip()]

    by_id: dict[str, dict] = {}
    by_subject: dict[str, list] = defaultdict(list)
    by_predicate: dict[str, list] = defaultdict(list)
    by_sp: dict[tuple, list] = defaultdict(list)
    by_status: dict[str, list] = defaultdict(list)
    by_eb: dict[str, list] = defaultdict(list)
    by_source: dict[str, list] = defaultdict(list)
    by_text: dict[str, list] = defaultdict(list)
    alias_map: dict[str, list[str]] = defaultdict(list)

    for r in records:
        rid = r["id"]
        by_id[rid] = r
        by_subject[r["subject"]].append(r)
        by_predicate[r["predicate"]].append(r)
        by_sp[(r["subject"], r["predicate"])].append(r)
        by_status[r["status"]].append(r)
        by_eb[r["expected_behavior"]].append(r)
        by_source[r["source_id"]].append(r)
        by_text[r["text"]].append(r)

        for alias in r.get("aliases", []):
            if alias not in alias_map[r["subject"]]:
                alias_map[r["subject"]].append(alias)

    # build supersession chains: for each (subject, predicate) with
    # latest_valid_fact_wins, order by timestamp
    chains: dict[tuple, list] = {}
    for r in by_eb.get("latest_valid_fact_wins", []):
        key = (r["subject"], r["predicate"])
        if key not in chains:
            chains[key] = []
        chains[key].append(r)
    for key in chains:
        chains[key].sort(key=lambda r: r["timestamp"])

    # build conflict groups from disputed records sharing (subject, predicate)
    conflict_groups: dict[tuple, list] = {}
    for r in by_status.get("disputed", []):
        key = (r["subject"], r["predicate"])
        if key not in conflict_groups:
            conflict_groups[key] = []
        conflict_groups[key].append(r)

    # build exact duplicate clusters
    dup_clusters: dict[str, list[str]] = {}
    for text, recs in by_text.items():
        if len(recs) >= 2:
            dup_clusters[text] = [r["id"] for r in recs]

    return CorpusIndex(
        records=records,
        by_id=by_id,
        by_subject=dict(by_subject),
        by_predicate=dict(by_predicate),
        by_subject_predicate=dict(by_sp),
        by_status=dict(by_status),
        by_expected_behavior=dict(by_eb),
        by_source_id=dict(by_source),
        by_text=dict(by_text),
        supersession_chains=chains,
        conflict_groups=conflict_groups,
        alias_map=dict(alias_map),
        duplicate_clusters=dup_clusters,
        corpus_hash=corpus_hash,
    )
