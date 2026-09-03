#!/usr/bin/env python3
"""
Experiment 06 — queries.jsonl generator (Stage 7).
Builds ground-truth queries per spec section 9 (categories 9.1-9.8), with the
experiment-specific fields from section 7's worked example:
  required_source_roots, expected_independent_root_count, expected_lineage_paths,
  must_detect_cycle, must_report_missing_provenance
"""
import json, os
from collections import defaultdict

BUILD_DIR = os.environ.get("EXP06_OUT", "/tmp/claude-0/exp06_build")

memories = [json.loads(l) for l in open(os.path.join(BUILD_DIR, "memories.jsonl"))]
by_id = {m["memory_id"]: m for m in memories}
prov_nodes = json.load(open(os.path.join(BUILD_DIR, "provenance_graph.json")))["nodes"]
prov_by_id = {n["node_id"]: n for n in prov_nodes}
claims = json.load(open(os.path.join(BUILD_DIR, "claim_lineage.json")))["claims"]
claims_by_memory = defaultdict(list)
for c in claims:
    claims_by_memory[c["memory_id"]].append(c)
instances = json.load(open(os.path.join(BUILD_DIR, "instances_registry.json")))
by_fact = {inst["fact_id"]: inst for inst in instances}

queries = []
qseq = 0
def qid():
    global qseq
    qseq += 1
    return f"e06q_{qseq:03d}"

def base_query(category, text, mem_ids, notes, **kw):
    m0 = by_id[mem_ids[0]]
    q = {
        "query_id": qid(),
        "query": text,
        "category": category,
        "target_entity_ids": sorted({by_id[mid]["subject_entity_id"] for mid in mem_ids}),
        "forbidden_entity_ids": [],
        "expected_claims": kw.pop("expected_claims", []),
        "acceptable_claims": kw.pop("acceptable_claims", []),
        "forbidden_claims": kw.pop("forbidden_claims", []),
        "required_scope": m0["scope"],
        "relevant_memory_ids": mem_ids,
        "distractor_memory_ids": kw.pop("distractor_memory_ids", []),
        "must_disambiguate": kw.pop("must_disambiguate", False),
        "must_preserve_scope": kw.pop("must_preserve_scope", False),
        "must_surface_multiple_states": kw.pop("must_surface_multiple_states", False),
        "should_abstain": kw.pop("should_abstain", False),
        "notes": notes,
        "required_source_roots": kw.pop("required_source_roots", []),
        "expected_independent_root_count": kw.pop("expected_independent_root_count", None),
        "expected_lineage_paths": kw.pop("expected_lineage_paths", []),
        "must_detect_cycle": kw.pop("must_detect_cycle", False),
        "must_report_missing_provenance": kw.pop("must_report_missing_provenance", False),
    }
    assert not kw, f"unused kwargs: {kw}"
    return q

def chain_path(mem_ids_ordered):
    return mem_ids_ordered

# ---------------------------------------------------------------------------
by_family = defaultdict(list)
for inst in instances:
    by_family[inst["family_key"]].append(inst)

# 06.1 cascade -> 9.1 root tracing + 9.3 path reconstruction
for inst in by_family["cascade"]:
    ids = inst["memory_ids"]  # E1,N1,C1,S1,S2,S3 in order
    e1, s3 = ids[0], ids[-1]
    unit = by_id[e1]["subject_text"]
    queries.append(base_query("9.1",
        f"What original evidence supports the leadership-deck claim about {unit}?",
        ids, f"Cascade instance {inst['fact_id']}: single root E1, five-hop derivation to S3.",
        expected_claims=[by_id[e1]["text"]],
        required_source_roots=[e1],
        expected_independent_root_count=1,
        expected_lineage_paths=[chain_path(ids)],
        must_report_missing_provenance=False))
    queries.append(base_query("9.3",
        f"How did the sensor-log reading about {unit} become the leadership-deck bullet? "
        f"List the intermediate documents that transmitted the claim.",
        ids, f"Cascade instance {inst['fact_id']}: full chain must be reconstructable in order.",
        expected_claims=[by_id[s3]["text"]],
        required_source_roots=[e1],
        expected_independent_root_count=1,
        expected_lineage_paths=[chain_path(ids)]))

# 06.2 fanout -> 9.2 independence (key trap: fan-out != corroboration)
for inst in by_family["fanout"]:
    ids = inst["memory_ids"]
    root = ids[0]
    n = inst["instance_meta"].get("fanout_n", 4)
    unit = by_id[root]["subject_text"]
    fake_claim = f"{n} independent write-ups confirm the {unit} vibration excursion, so confidence should scale with {n}."
    queries.append(base_query("9.2",
        f"How many independent observations support the vibration-excursion finding on {unit}? "
        f"There are {n} write-ups referencing it.",
        ids, f"Fan-out instance {inst['fact_id']} (fanout_n={n}). Ground truth independent-root count "
             f"is 1 regardless of n. {inst['instance_meta'].get('perturbation','')}",
        expected_claims=[by_id[root]["text"]],
        forbidden_claims=[fake_claim],
        required_source_roots=[root],
        expected_independent_root_count=1,
        expected_lineage_paths=[[root, ids[1]]]))

# P06-A explicit comparison across the three fanout-size instances
fanout_pert = [i for i in by_family["fanout"] if "perturbation" in i["instance_meta"]]
if len(fanout_pert) == 3:
    fanout_pert = sorted(fanout_pert, key=lambda i: i["instance_meta"]["fanout_n"])
    all_ids = [mid for i in fanout_pert for mid in i["memory_ids"]]
    queries.append(base_query("9.8",
        "Compare the strength of evidence across three write-ups of the same finding that were copied "
        "1 time, 5 times, and 25 times respectively. Does the 25-copy version have stronger support?",
        all_ids,
        "P06-A fan-out manipulation: no new evidence enters at any fan-out level; independent-root count "
        "stays 1 in all three cases. A system that scores confidence by document count fails this.",
        required_source_roots=[fanout_pert[0]["memory_ids"][0], fanout_pert[1]["memory_ids"][0],
                                fanout_pert[2]["memory_ids"][0]],
        expected_independent_root_count=1,
        forbidden_claims=["The 25-copy version is better supported than the 1-copy version."]))

# 06.3 convergent -> 9.2 independence (Control B, positive control)
for inst in by_family["convergent"]:
    ids = inst["memory_ids"]
    roots = ids[:3]
    concl = ids[3]
    unit = by_id[roots[0]]["subject_text"]
    queries.append(base_query("9.2",
        f"Are the three sources behind the overtemperature conclusion on {unit} truly independent, "
        f"or do they trace back to a single origin?",
        ids, f"Convergent instance {inst['fact_id']} (Control B): three genuinely independent instruments/observers.",
        expected_claims=[by_id[concl]["text"]],
        required_source_roots=roots,
        expected_independent_root_count=3,
        expected_lineage_paths=[[r, concl] for r in roots]))

# 06.4 hidden_root -> 9.2 independence trap
for inst in by_family["hidden_root"]:
    ids = inst["memory_ids"]  # E1, path1_note, reportA, path2_note, reportB
    e1, reportA, reportB = ids[0], ids[2], ids[4]
    queries.append(base_query("9.2",
        "Do the two site postmortems about the relay dropout independently corroborate the firmware-push "
        "theory, given they come from different sites and different authors?",
        ids, f"Hidden shared root instance {inst['fact_id']}: both postmortems ultimately trace to the same "
             f"unattributed ops-channel message (E1), not to independent investigation.",
        expected_claims=[by_id[e1]["text"]],
        forbidden_claims=["Report A and Report B are two independent confirmations of the firmware-push theory."],
        required_source_roots=[e1],
        expected_independent_root_count=1,
        expected_lineage_paths=[[e1, ids[1], reportA], [e1, ids[3], reportB]]))

# 06.5 depth_chain -> 9.1 / P06-C depth robustness
for inst in by_family["depth_chain"]:
    ids = inst["memory_ids"]
    root, leaf = ids[0], ids[-1]
    depth = inst["instance_meta"]["depth"]
    queries.append(base_query("9.1",
        f"What original evidence supports the flow-rate-drop claim carried in this depth-{depth} derivation "
        f"chain, and can it still be traced back that far?",
        ids, f"Depth-chain instance {inst['fact_id']} (P06-C, depth={depth}). All edges are preserved; "
             f"root recovery should not degrade with depth in this corpus.",
        expected_claims=[by_id[root]["text"]],
        required_source_roots=[root],
        expected_independent_root_count=1,
        expected_lineage_paths=[chain_path(ids)]))

# 06.6 partial_loss -> 9.6 provenance completeness (Control E-flavored)
for inst in by_family["partial_loss"]:
    ids = inst["memory_ids"]  # E1, E2, mid, late
    e1, e2, mid, late = ids
    queries.append(base_query("9.6",
        f"Is the complete source lineage available for the overcurrent-event claim as stated in the wiki "
        f"summary, or does the wiki summary under-cite relative to what the rest of the corpus shows?",
        ids, f"Partial-loss instance {inst['fact_id']}: 'mid' cites both {e1} and {e2}; the later 'late' "
             f"derivative only carries forward {e1}. {e2} is still retrievable elsewhere in the corpus — "
             f"the gap is in the derivative's own citation, not in overall corpus retrievability.",
        expected_claims=[by_id[mid]["text"]],
        required_source_roots=[e1, e2],
        expected_independent_root_count=2,
        expected_lineage_paths=[[e1, mid], [e2, mid]],
        must_report_missing_provenance=True))
    queries.append(base_query("9.1",
        "What supports this specific claim, as cited by the memory itself (not the wider corpus)?",
        [late], f"Partial-loss instance {inst['fact_id']}: direct-citation-only reading of 'late' should "
                f"return only {e1}, distinct from the completeness question above.",
        expected_claims=[by_id[late]["text"]],
        required_source_roots=[e1],
        expected_independent_root_count=1,
        expected_lineage_paths=[[e1, late]]))

# 06.7 unsupported -> 9.4 unsupported claim detection (+ Control F contrast)
for inst in by_family["unsupported"]:
    ids = inst["memory_ids"]
    a, b, s = ids
    is_grounded = inst["instance_meta"].get("control") == "F_fully_supported"
    s_claims = claims_by_memory[s]
    if is_grounded:
        queries.append(base_query("9.4",
            "Is every material claim in this postmortem grounded in cited evidence?",
            ids, f"Unsupported-injection instance {inst['fact_id']} (Control F: fully grounded sibling). "
                 f"Every sentence maps to {a} or {b}.",
            expected_claims=[c["claim_text"] for c in s_claims],
            required_source_roots=[a, b],
            expected_independent_root_count=2,
            expected_lineage_paths=[[a, s], [b, s]]))
    else:
        unsupported_c = [c for c in s_claims if not c["supported"]][0]
        supported_c = [c for c in s_claims if c["supported"]][0]
        queries.append(base_query("9.4",
            "What supports the firmware-bug explanation in this postmortem?",
            ids, f"Unsupported-injection instance {inst['fact_id']} (Control G). The pump-stop and "
                 f"temperature-rise portions are sourced from {a}/{b}; the firmware-bug causal claim has "
                 f"no supporting root anywhere in the corpus and must not inherit provenance from its "
                 f"sourced neighbors (Invariant 06-E).",
            expected_claims=[supported_c["claim_text"]],
            forbidden_claims=[unsupported_c["claim_text"]],
            required_source_roots=[a, b],
            expected_independent_root_count=2,
            expected_lineage_paths=[[a, s], [b, s]],
            should_abstain=False))
        queries.append(base_query("9.4",
            "Which specific assertion in this postmortem lacks evidentiary support, even though the "
            "surrounding sentences are well-sourced?",
            ids, f"Unsupported-injection instance {inst['fact_id']} (Control G): claim-level, not "
                 f"document-level, provenance discrimination.",
            expected_claims=[unsupported_c["claim_text"]],
            required_source_roots=[],
            expected_independent_root_count=0,
            should_abstain=True))

# 06.8 circular -> 9.5 circularity (+ P06-E acyclic sibling contrast)
for inst in by_family["circular"]:
    ids = inst["memory_ids"]
    cyclic = inst["instance_meta"]["cyclic"]
    unit = by_id[ids[0]]["subject_text"]
    if cyclic:
        queries.append(base_query("9.5",
            f"Ticket A, Wiki B, and Retro C about {unit} all cite each other for the stuck-relay-valve "
            f"finding. Do these three documents provide independent support for the finding, or is the "
            f"apparent corroboration circular?",
            ids, f"Circular instance {inst['fact_id']}: A->cites C, B->cites A, C->cites B (3-cycle), no "
                 f"external evidence root in this cluster (Invariant 06-C).",
            forbidden_claims=[f"Ticket A, Wiki B, and Retro C independently confirm the stuck relay valve "
                               f"finding on {unit}."],
            required_source_roots=[],
            expected_independent_root_count=0,
            must_detect_cycle=True,
            should_abstain=True))
    else:
        root = ids[0]
        queries.append(base_query("9.5",
            f"Ticket A, Wiki B, and Retro C about {unit} form a citation chain for the stuck-relay-valve "
            f"finding. Is this apparent corroboration circular, or does it trace to an external root?",
            ids, f"Acyclic sibling of a circular instance (P06-E paired comparison, {inst['fact_id']}): "
                 f"same wording pattern, but the chain terminates at an external field-note root instead "
                 f"of looping back.",
            required_source_roots=[root],
            expected_independent_root_count=1,
            expected_lineage_paths=[chain_path(ids)],
            must_detect_cycle=False))

# 06.9 provenance contradiction
for inst in by_family["contradiction"]:
    ids = inst["memory_ids"]
    e7, d = ids
    queries.append(base_query("9.6",
        "Does the status email's claim about extended downtime match what its cited source actually says?",
        ids, f"Contradiction instance {inst['fact_id']}: memory {d} declares derived_from=[{e7}] but its "
             f"text materially contradicts {e7}'s content (unit was reported ONLINE throughout).",
        expected_claims=[by_id[e7]["text"]],
        forbidden_claims=[by_id[d]["text"]],
        required_source_roots=[e7],
        expected_independent_root_count=1,
        must_surface_multiple_states=True,
        must_report_missing_provenance=False))

# 06.10 root_sub worlds -> 9.2 + 9.8 comparison (Control C, P06-B)
root_sub_by_idx = defaultdict(dict)
for inst in by_family["root_sub"]:
    root_sub_by_idx[inst["instance_meta"]["index"]][inst["instance_meta"]["world"]] = inst

for idx, worlds in root_sub_by_idx.items():
    a_inst, b_inst = worlds["A"], worlds["B"]
    a_ids, b_ids = a_inst["memory_ids"], b_inst["memory_ids"]
    a_root = a_ids[0]
    b_roots = b_ids[:5]
    unit = by_id[a_root]["subject_text"]
    queries.append(base_query("9.2",
        f"World A: five reports describe an intermittent pressure fault on {unit}. How many independent "
        f"observations actually support the claim?",
        a_ids, f"Root-substitution World A, pair {idx}: 5 reports, 1 root (Control C baseline low end).",
        required_source_roots=[a_root],
        expected_independent_root_count=1,
        expected_lineage_paths=[[a_root, r] for r in a_ids[1:]]))
    queries.append(base_query("9.2",
        f"World B: five reports describe an intermittent pressure fault on {unit}. How many independent "
        f"observations actually support the claim?",
        b_ids, f"Root-substitution World B, pair {idx}: 5 independently instrumented roots converging on "
               f"one postmortem (P06-B target state after independent-root substitution).",
        required_source_roots=b_roots,
        expected_independent_root_count=5,
        expected_lineage_paths=[[r, b_ids[-1]] for r in b_roots]))
    queries.append(base_query("9.8",
        f"World A and World B each have five write-ups about the same kind of pressure-fault claim on "
        f"{unit}-class hardware. Which world's conclusion has stronger, more independent evidentiary "
        f"support, despite equal document counts?",
        a_ids + b_ids,
        f"P06-B paired comparison, pair {idx}: World B (5 independent roots) is strictly better-supported "
        f"than World A (1 root, 5 copies), even though both surface 5 documents.",
        forbidden_claims=["World A and World B have equally strong evidence because both have 5 reports."],
        expected_independent_root_count=5))

# 06.11 disappearance -> 9.7 source-loss (three distinct sub-questions, P06-H)
for inst in by_family["disappearance"]:
    ids = inst["memory_ids"]  # root(tombstoned), note, report
    root, note, report = ids
    unit = by_id[report]["subject_text"]
    queries.append(base_query("9.7",
        f"Where did the component-limitation explanation for the {unit} failure originate?",
        ids, f"Source-disappearance instance {inst['fact_id']}: root is historically known (cited by name "
             f"and source_id) but its content is tombstoned/unretrievable.",
        expected_claims=[by_id[note]["text"]],
        required_source_roots=[root],
        expected_independent_root_count=1,
        expected_lineage_paths=[chain_path(ids)]))
    queries.append(base_query("9.7",
        "Can the underlying evidence for this claim currently be inspected in full, or only referenced?",
        ids, f"Source-disappearance instance {inst['fact_id']} (P06-H): correct answer distinguishes "
             f"'historically sourced' from 'currently inspectable' — {root} is the former, not the latter. "
             f"Must not fabricate reconstructed content for {root}.",
        required_source_roots=[root],
        expected_independent_root_count=1,
        should_abstain=True,
        must_report_missing_provenance=True))
    queries.append(base_query("9.7",
        "Given that the original test-bench report is no longer retrievable, how strong is the surviving "
        "support for the component-limitation claim?",
        ids, f"Source-disappearance instance {inst['fact_id']} (P06-H): surviving support is a preserved "
             f"citation chain (note, report) to a known-but-unverifiable root — weaker than a currently "
             f"inspectable root, but not absent. Must be represented as reduced-confidence, not silently "
             f"treated as either fully verified or fully unsupported.",
        required_source_roots=[root],
        expected_independent_root_count=1,
        must_report_missing_provenance=True))

# 06.12 reentry -> generated-output re-entry (P06-G)
for inst in by_family["reentry"]:
    ids = inst["memory_ids"]  # E1, S1, M1(model), M2(reingested), R1
    e1, s1, m1, m2, r1 = ids
    unit = by_id[e1]["subject_text"]
    queries.append(base_query("9.2",
        f"The status email about {unit}'s restart cycles cites a wiki page, which was pasted from an AI "
        f"assistant summary, which was based on a postmortem. Does the wiki page constitute a new, "
        f"independent piece of evidence?",
        ids, f"Reentry instance {inst['fact_id']} (P06-G): E1(sensor log) -> S1(postmortem) -> "
             f"M1(model-generated summary) -> M2(reingested as a new memory) -> R1. New memory object at "
             f"each step, but zero new evidence roots after E1.",
        forbidden_claims=[f"The wiki page is a new source of evidence about {unit}'s restart cycles, "
                            f"independent of the original postmortem."],
        required_source_roots=[e1],
        expected_independent_root_count=1,
        expected_lineage_paths=[chain_path(ids)]))
    queries.append(base_query("9.3",
        f"Trace how the {unit} restart-cycle finding moved from the original sensor log to the final "
        f"status email, noting any point where an AI-generated summary was reingested as if it were a "
        f"new source.",
        ids, f"Reentry instance {inst['fact_id']}: path reconstruction should flag {m1}->{m2} as "
             f"reingestion, not new observation.",
        expected_claims=[by_id[r1]["text"]],
        required_source_roots=[e1],
        expected_independent_root_count=1,
        expected_lineage_paths=[chain_path(ids)]))

with open(os.path.join(BUILD_DIR, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

print(f"Wrote {len(queries)} queries")
from collections import Counter
print(Counter(q["category"] for q in queries))
