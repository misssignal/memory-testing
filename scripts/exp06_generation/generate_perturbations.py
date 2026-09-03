#!/usr/bin/env python3
"""Experiment 06 -- perturbation_plan.json (Stage 6), grounded in real generated IDs."""
import json, os
from collections import defaultdict

BUILD_DIR = os.environ.get("EXP06_OUT", "/tmp/claude-0/exp06_build")
memories = [json.loads(l) for l in open(os.path.join(BUILD_DIR, "memories.jsonl"))]
by_id = {m["memory_id"]: m for m in memories}
instances = json.load(open(os.path.join(BUILD_DIR, "instances_registry.json")))
by_family = defaultdict(list)
for inst in instances:
    by_family[inst["family_key"]].append(inst)

def first(family_key, **filt):
    for inst in by_family[family_key]:
        if all(inst["instance_meta"].get(k) == v for k, v in filt.items()):
            return inst
    raise KeyError((family_key, filt))

fanout1 = first("fanout", fanout_n=1)
fanout5 = first("fanout", fanout_n=5)
fanout25 = first("fanout", fanout_n=25)

depth_insts = {d: [i for i in by_family["depth_chain"] if i["instance_meta"]["depth"] == d] for d in (1,2,4,8)}

partial_loss_ex = by_family["partial_loss"][0]

unsupported_ex = [i for i in by_family["unsupported"] if i["instance_meta"].get("control") == "G_partially_unsupported"][0]

circ_cyclic = [i for i in by_family["circular"] if i["instance_meta"]["cyclic"]][0]
circ_acyclic = [i for i in by_family["circular"] if not i["instance_meta"]["cyclic"]][0]

reentry_ex = by_family["reentry"][0]

disappearance_ex = by_family["disappearance"][0]

root_sub_pair0 = [i for i in by_family["root_sub"] if i["instance_meta"]["index"] == 0]
world_a = [i for i in root_sub_pair0 if i["instance_meta"]["world"] == "A"][0]
world_b = [i for i in root_sub_pair0 if i["instance_meta"]["world"] == "B"][0]

plan = {
    "experiment": "06",
    "dimensions": {
        "derivative_copy_count": [1, 4, 5, 25],
        "graph_depth": [1, 2, 4, 8],
        "graph_breadth_fanout": [1, 4, 5, 25],
        "independent_root_count": [1, 2, 3, 5],
        "provenance_metadata_visibility": ["exposed_in_derived_from", "hidden_pending__oracle_strip"],
        "provenance_completeness": ["complete", "partial_citation_drop", "root_inaccessible"],
        "source_disappearance": [False, True],
        "unsupported_claim_injection": [False, True],
        "cycle_presence": [False, True],
        "reingestion_depth": [0, 1, 2],
    },
    "perturbations": [
        {
            "id": "P06-A",
            "name": "Fan-out manipulation",
            "description": "One evidence root produces 1 / 5 / 25 derivative write-ups. No new evidence enters "
                            "at any fan-out level.",
            "instances": {
                "fanout_1": {"fact_id": fanout1["fact_id"], "root": fanout1["memory_ids"][0],
                              "descendant_count": 1, "memory_ids": fanout1["memory_ids"]},
                "fanout_5": {"fact_id": fanout5["fact_id"], "root": fanout5["memory_ids"][0],
                              "descendant_count": 5, "memory_ids": fanout5["memory_ids"]},
                "fanout_25": {"fact_id": fanout25["fact_id"], "root": fanout25["memory_ids"][0],
                               "descendant_count": 25, "memory_ids": fanout25["memory_ids"]},
            },
            "expected_independent_evidence_count": 1,
            "naive_failure_mode": "Scoring confidence/independent-root-count proportional to document count "
                                   "(e.g. reporting 25 independent observations for fanout_25).",
            "metric": "Derivative Inflation Rate, Fan-out Robustness",
        },
        {
            "id": "P06-B",
            "name": "Independent-root substitution",
            "description": "Replace a 5-copies-of-1-root world (World A) with a 5-genuinely-independent-roots "
                            "world (World B), holding claim wording and document count constant.",
            "world_a": {"fact_id": world_a["fact_id"], "root": world_a["memory_ids"][0],
                         "memory_ids": world_a["memory_ids"], "independent_root_count": 1},
            "world_b": {"fact_id": world_b["fact_id"], "roots": world_b["memory_ids"][:5],
                         "memory_ids": world_b["memory_ids"], "independent_root_count": 5},
            "expected_effect": "Confidence/independent-root-count should increase from World A to World B "
                                "despite both surfacing 5 documents.",
            "naive_failure_mode": "Treating World A and World B identically because both retrieve 5 similar "
                                   "documents (surface-level retrieval count used as a confidence proxy).",
            "metric": "Independent Evidence Count Error",
        },
        {
            "id": "P06-C",
            "name": "Derivation depth",
            "description": "Same claim and same root; vary derivation depth 1 / 2 / 4 / 8 across otherwise "
                            "parallel chains, holding wording pattern constant.",
            "instances": {
                str(d): [{"fact_id": i["fact_id"], "root": i["memory_ids"][0], "leaf": i["memory_ids"][-1],
                           "chain": i["memory_ids"]} for i in depth_insts[d]]
                for d in (1, 2, 4, 8)
            },
            "expected_effect": "Root recovery accuracy should not degrade with depth in this corpus -- every "
                                "edge is intact end to end (Control D, deep-but-complete lineage).",
            "naive_failure_mode": "Root-recovery accuracy dropping as depth increases, or the system silently "
                                   "truncating lineage at some fixed hop limit.",
            "metric": "Depth Robustness, Root Recovery Accuracy",
        },
        {
            "id": "P06-D",
            "name": "Provenance-edge removal",
            "description": "Remove exactly one lineage edge from an otherwise complete chain and ask whether "
                            "the system reports incomplete lineage or invents the missing connection.",
            "base_instance": {"fact_id": partial_loss_ex["fact_id"], "memory_ids": partial_loss_ex["memory_ids"]},
            "edge_removed": {
                "from_node": partial_loss_ex["memory_ids"][1],
                "to_node": partial_loss_ex["memory_ids"][3],
                "description": "The 'late' derivative (index 3) drops its citation to the second evidence "
                                "root (index 1) that the 'mid' derivative (index 2) still carries.",
            },
            "expected_effect": "A query against the 'late' node alone should report partial/incomplete "
                                "provenance (one root, not two), not silently assume completeness and not "
                                "fabricate the missing edge.",
            "naive_failure_mode": "Reporting 'complete provenance' for 'late' because a similarly-worded "
                                   "sibling record ('mid') happens to have both citations, without noticing "
                                   "'late' itself only cites one.",
            "metric": "Provenance Path Accuracy, Provenance Hallucination Rate",
        },
        {
            "id": "P06-E",
            "name": "Circularity injection",
            "description": "Take an acyclic citation graph (root -> A -> B -> C) and add one backward "
                            "citation (C -> A) producing a 3-cycle. No new evidence enters.",
            "acyclic_base": {"fact_id": circ_acyclic["fact_id"], "root": circ_acyclic["memory_ids"][0],
                               "memory_ids": circ_acyclic["memory_ids"], "independent_root_count": 1},
            "cyclic_variant": {"fact_id": circ_cyclic["fact_id"], "memory_ids": circ_cyclic["memory_ids"],
                                 "independent_root_count": 0,
                                 "note": "root node removed / replaced by the backward citation; A, B, C "
                                         "cite only each other"},
            "expected_effect": "must_detect_cycle=true and independent-root count drops to 0 for the cyclic "
                                "variant, even though the wording of A/B/C is nearly identical to the acyclic "
                                "base.",
            "naive_failure_mode": "Treating the cycle as three corroborating sources because each individual "
                                   "citation edge looks like normal support.",
            "metric": "Circularity Detection Rate",
        },
        {
            "id": "P06-F",
            "name": "Unsupported sentence insertion",
            "description": "Add one unsupported causal assertion to an otherwise fully-sourced summary.",
            "instance": {"fact_id": unsupported_ex["fact_id"], "memory_ids": unsupported_ex["memory_ids"],
                          "summary_node": unsupported_ex["memory_ids"][2]},
            "control_f_sibling_family": "unsupported claims flagged control=F_fully_supported in "
                                          "instances_registry.json (grounded-only variants of this same motif)",
            "expected_effect": "Claim-level provenance discrimination: the pump-stop and temperature-rise "
                                "clauses remain supported; the firmware-bug clause is flagged unsupported, "
                                "without downgrading or upgrading the sourced clauses.",
            "naive_failure_mode": "Document-level provenance scoring that marks the whole summary 'sourced' "
                                   "because most of it is, silently inheriting support for the firmware clause.",
            "metric": "Unsupported Claim Detection, Claim-Level Provenance Accuracy",
        },
        {
            "id": "P06-G",
            "name": "Reingested model summary",
            "description": "Insert a previously-generated derived summary as though it were a new memory "
                            "object, then let a further report derive from that reingested memory.",
            "instance": {"fact_id": reentry_ex["fact_id"], "chain": reentry_ex["memory_ids"],
                          "model_generated_node": reentry_ex["memory_ids"][2],
                          "reingested_node": reentry_ex["memory_ids"][3]},
            "expected_effect": "new_memory_object=true for the reingested node, but new_evidence_root=false; "
                                "the whole chain still resolves to the single original sensor-log root.",
            "naive_failure_mode": "Treating the reingested wiki copy of the AI summary as a second, "
                                   "corroborating observation because it has its own memory_id and source_id.",
            "metric": "Provenance Hallucination Rate, Independent Evidence Count Error",
        },
        {
            "id": "P06-H",
            "name": "Root becomes inaccessible",
            "description": "Keep the provenance edge (derived_from / citation by name and source_id) but "
                            "tombstone the source's retrievable content.",
            "instance": {"fact_id": disappearance_ex["fact_id"], "memory_ids": disappearance_ex["memory_ids"],
                          "tombstoned_root": disappearance_ex["memory_ids"][0]},
            "three_distinct_questions": [
                "Where did the claim originate? (answerable -- historically sourced, root identified by id)",
                "Can the underlying evidence currently be inspected? (no -- content withheld/tombstoned)",
                "How strong is the surviving support? (reduced-confidence, not zero and not full -- a "
                "preserved citation chain to a known-but-unverifiable root)",
            ],
            "naive_failure_mode": "Collapsing all three questions into one answer -- either claiming the root "
                                   "is still fully verifiable, or claiming the claim is now baseless because "
                                   "the root can't be reread.",
            "metric": "Provenance Hallucination Rate, Root Recovery Accuracy",
        },
    ],
    "recommended_first_perturbation": "P06-A using the fanout_1 / fanout_5 / fanout_25 triple "
                                       f"({fanout1['fact_id']} / {fanout5['fact_id']} / {fanout25['fact_id']}) "
                                       "-- cheapest to score and most diagnostic of the central research "
                                       "question (citation count vs. evidence independence).",
}

os.makedirs(os.path.join(BUILD_DIR, "perturbations"), exist_ok=True)
with open(os.path.join(BUILD_DIR, "perturbations", "perturbation_plan.json"), "w") as f:
    json.dump(plan, f, indent=2)
print("wrote perturbation_plan.json")
