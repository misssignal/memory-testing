from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


BENCHMARK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCHMARK))

from epistemic.compiler import canonical_scope, compile_memories, normalize_text


EXP05 = (
    BENCHMARK.parents[0]
    / "adversarial_memory_benchmark_exp05_contested_reality_v0.1"
    / "experiment_05_contested_reality"
)


class CompilerUnitTests(unittest.TestCase):
    def memory(self, memory_id: str, **changes):
        base = {
            "memory_id": memory_id,
            "subject_entity_id": "Entity A",
            "predicate": "Has Status",
            "object": "Working",
            "event_time": "2027-01-01",
            "observation_time": "2027-01-02",
            "ingestion_time": "2027-01-03",
            "scope": {"region": "North", "team": None},
            "derived_from": [],
            "supersedes": [],
            "contradicts": [],
        }
        base.update(changes)
        return base

    def test_normalization_is_stable(self):
        self.assertEqual(normalize_text("  CAFÉ\tProject  "), "café project")
        self.assertEqual(
            canonical_scope({"team": None, "Region": " NORTH  "}),
            '{"region":"north"}',
        )

    def test_derivation_collapses_copies_to_original_root(self):
        graph = compile_memories(
            [
                self.memory("root"),
                self.memory("copy-1", derived_from=["root"]),
                self.memory("copy-2", derived_from=["copy-1"]),
            ]
        )
        self.assertEqual(graph.evidence_roots_by_memory["copy-2"], ("root",))
        claim = next(iter(graph.claims.values()))
        self.assertEqual(claim.evidence_root_ids, ["root"])

    def test_multiple_parents_preserve_independent_roots(self):
        graph = compile_memories(
            [
                self.memory("root-a"),
                self.memory("root-b"),
                self.memory("summary", derived_from=["root-b", "root-a"]),
            ]
        )
        self.assertEqual(graph.evidence_roots_by_memory["summary"], ("root-a", "root-b"))

    def test_missing_reference_fails(self):
        with self.assertRaisesRegex(ValueError, "references missing memory"):
            compile_memories([self.memory("copy", derived_from=["missing"])])

    def test_oracle_fields_do_not_affect_output(self):
        clean = self.memory("root")
        annotated = dict(clean, _oracle={"claim_id": "SECRET"}, truth_role="globally_true")
        self.assertEqual(compile_memories([clean]).to_dict(), compile_memories([annotated]).to_dict())


class Experiment05IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.memories = [
            json.loads(line)
            for line in (EXP05 / "memories.jsonl").read_text().splitlines()
            if line.strip()
        ]
        cls.graph = compile_memories(cls.memories)

    def test_corpus_compiles_without_cycles(self):
        self.assertEqual(len(self.graph.memories), 202)
        self.assertEqual(self.graph.derivation_cycles, [])

    def test_claim_keys_do_not_mix_oracle_claims(self):
        oracle_by_memory = {
            memory["memory_id"]: memory.get("_oracle", {}).get("claim_id")
            for memory in self.memories
        }
        for claim in self.graph.claims.values():
            oracle_claims = {
                oracle_by_memory[memory_id]
                for memory_id in claim.memory_ids
                if oracle_by_memory[memory_id]
            }
            self.assertLessEqual(len(oracle_claims), 1)

    def test_each_oracle_claim_maps_to_one_public_claim_key(self):
        public_ids_by_oracle = {}
        for public_id, claim in self.graph.claims.items():
            for memory_id in claim.memory_ids:
                memory = next(m for m in self.memories if m["memory_id"] == memory_id)
                oracle_id = memory.get("_oracle", {}).get("claim_id")
                if oracle_id:
                    public_ids_by_oracle.setdefault(oracle_id, set()).add(public_id)
        self.assertEqual(len(public_ids_by_oracle), 25)
        self.assertTrue(all(len(ids) == 1 for ids in public_ids_by_oracle.values()))


if __name__ == "__main__":
    unittest.main()
