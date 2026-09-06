"""Oracle-side verification for the deterministic Experiment 05 compiler.

This file may read benchmark oracle fields.  The production compiler in
``epistemic/compiler.py`` must never import this module.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from epistemic import compile_memories


ROOT = (
    Path(__file__).resolve().parents[1]
    / "adversarial_memory_benchmark_exp05_contested_reality_v0.1"
    / "experiment_05_contested_reality"
)


def main() -> None:
    memories = [
        json.loads(line)
        for line in (ROOT / "memories.jsonl").read_text().splitlines()
        if line.strip()
    ]
    graph = compile_memories(memories)
    by_id = {memory["memory_id"]: memory for memory in memories}
    ledger = {
        claim["claim_id"]: claim
        for claim in json.loads((ROOT / "claim_ledger.json").read_text())["claims"]
    }

    public_claims_by_oracle: dict[str, set[str]] = {}
    root_comparisons = []
    mixed_public_claims = []
    for public_id, claim in graph.claims.items():
        oracle_ids = {
            by_id[memory_id].get("_oracle", {}).get("claim_id")
            for memory_id in claim.memory_ids
        } - {None}
        if len(oracle_ids) > 1:
            mixed_public_claims.append({"public_claim_id": public_id, "oracle_claim_ids": sorted(oracle_ids)})
        for oracle_id in oracle_ids:
            public_claims_by_oracle.setdefault(oracle_id, set()).add(public_id)
            expected = ledger[oracle_id]["independent_evidence_roots"]
            actual = len(claim.evidence_root_ids)
            root_comparisons.append(
                {
                    "oracle_claim_id": oracle_id,
                    "public_claim_id": public_id,
                    "expected_independent_roots": expected,
                    "provenance_leaf_roots": actual,
                    "delta": actual - expected,
                }
            )

    split_oracle_claims = {
        oracle_id: sorted(public_ids)
        for oracle_id, public_ids in public_claims_by_oracle.items()
        if len(public_ids) > 1
    }
    exact = sum(row["delta"] == 0 for row in root_comparisons)
    report = {
        "memory_count": len(memories),
        "public_claim_count": len(graph.claims),
        "oracle_claim_count": len(public_claims_by_oracle),
        "mixed_public_claims": mixed_public_claims,
        "split_oracle_claims": split_oracle_claims,
        "root_count": {
            "exact": exact,
            "total": len(root_comparisons),
            "mean_absolute_error": (
                sum(abs(row["delta"]) for row in root_comparisons) / len(root_comparisons)
            ),
            "delta_distribution": dict(sorted(Counter(row["delta"] for row in root_comparisons).items())),
        },
        "root_comparisons": sorted(root_comparisons, key=lambda row: row["oracle_claim_id"]),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
