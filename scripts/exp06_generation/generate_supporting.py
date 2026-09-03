#!/usr/bin/env python3
"""
Experiment 06 — supporting files generator (Stage 6/7).
Consumes memories.jsonl / provenance_graph.json / claim_lineage.json /
instances_registry.json produced by generate_corpus.py and produces:

  - ingestion_chronological.jsonl / ingestion_shuffled.jsonl / ingestion_late_arrival.jsonl
  - queries.jsonl  (Stage 7 ground truth, section 9 categories)
  - sources.md
  - truth_state.json
  - provenance.json  (flat node/source mapping, exp03/04-compatible shape)
"""
import json, random, os
from collections import defaultdict, deque

random.seed(20260614)

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

# ---------------------------------------------------------------------------
# Ingestion order variants
# ---------------------------------------------------------------------------

chrono = sorted(memories, key=lambda m: (m["event_time"], m["memory_id"]))
with open(os.path.join(BUILD_DIR, "ingestion_chronological.jsonl"), "w") as f:
    for m in chrono:
        f.write(json.dumps({"memory_id": m["memory_id"], "ingest_order_time": m["ingestion_time"]}) + "\n")

shuffled = memories[:]
random.Random(7).shuffle(shuffled)
with open(os.path.join(BUILD_DIR, "ingestion_shuffled.jsonl"), "w") as f:
    for m in shuffled:
        f.write(json.dumps({"memory_id": m["memory_id"]}) + "\n")

# late_arrival: evidence roots ingested first as usual, but for ~15% of instances,
# a root's memory record does not arrive in the corpus until AFTER several of its
# descendants have already been ingested -- tests whether provenance is retroactively
# corrected once the root shows up, versus permanently anchored to "unknown".
late_order = []
root_ids_by_fact = defaultdict(list)
for m in memories:
    if m["_oracle"]["is_evidence_root"]:
        root_ids_by_fact[m["_oracle"]["fact_id"]].append(m["memory_id"])

late_facts = set(random.Random(11).sample(sorted({m["_oracle"]["fact_id"] for m in memories}), 13))
deferred_roots = []
main_seq = []
for m in chrono:
    if m["_oracle"]["fact_id"] in late_facts and m["_oracle"]["is_evidence_root"]:
        deferred_roots.append(m["memory_id"])
        continue
    main_seq.append(m["memory_id"])
# insert deferred roots after 80% of the main sequence
insert_point = int(len(main_seq) * 0.8)
late_order = main_seq[:insert_point] + deferred_roots + main_seq[insert_point:]
assert set(late_order) == set(by_id.keys())
with open(os.path.join(BUILD_DIR, "ingestion_late_arrival.jsonl"), "w") as f:
    for mid in late_order:
        f.write(json.dumps({
            "memory_id": mid,
            "late_arrival_root": mid in deferred_roots,
        }) + "\n")

print(f"late_arrival: {len(deferred_roots)} evidence roots deferred, from {len(late_facts)} fact instances")

# ---------------------------------------------------------------------------
# sources.md
# ---------------------------------------------------------------------------

lines = ["# Sources — Experiment 06\n",
         "One row per memory's originating artifact. `retrievable=false` sources are tombstoned in "
         "`memories.jsonl` (content withheld) but remain listed here for the historical record.\n",
         "| source_id | memory_id | memory_type | author/system | fact_id | retrievable |",
         "|---|---|---|---|---|---|"]
for m in memories:
    lines.append(f"| {m['source_id']} | {m['memory_id']} | {m['memory_type']} | "
                  f"{m['_oracle']['author']} | {m['_oracle']['fact_id']} | {m['_oracle']['retrievable']} |")
with open(os.path.join(BUILD_DIR, "sources.md"), "w") as f:
    f.write("\n".join(lines) + "\n")

# ---------------------------------------------------------------------------
# provenance.json (flat, exp03/04-compatible)
# ---------------------------------------------------------------------------

flat_nodes = [{"memory_id": m["memory_id"], "fact_id": m["_oracle"]["fact_id"],
               "source_id": m["source_id"]} for m in memories]
with open(os.path.join(BUILD_DIR, "provenance.json"), "w") as f:
    json.dump({"nodes": flat_nodes}, f, indent=2)

# ---------------------------------------------------------------------------
# truth_state.json
# ---------------------------------------------------------------------------

sites = sorted({m["scope"]["facility"] for m in memories})
units = sorted({m["subject_entity_id"] for m in memories})
families = sorted({m["_oracle"]["family_key"] for m in memories})

evidence_roots = [m["memory_id"] for m in memories if m["_oracle"]["is_evidence_root"]]
cycle_members = [n["node_id"] for n in prov_nodes if n.get("ultimate_evidence_roots_note")]
unsupported_claims = [c["claim_id"] for c in claims if not c["supported"] and not by_id[c["memory_id"]]["_oracle"]["is_evidence_root"]]
inaccessible_roots = [m["memory_id"] for m in memories if m["_oracle"]["is_evidence_root"] and not m["_oracle"]["retrievable"]]
reentry_nodes = [m["memory_id"] for m in memories if m["_oracle"]["family_key"] == "reentry"]
contradiction_nodes = [m["memory_id"] for m in memories if m["contradicts"]]

truth_state = {
    "story_id": "thornfield_sentinel",
    "company": "Thornfield Systems",
    "product_line": "Sentinel",
    "sites": sites,
    "units": units,
    "families": families,
    "family_legend": {
        "cascade": "06.1 citation cascade",
        "fanout": "06.2 branching descendants",
        "convergent": "06.3 convergent independent evidence (Control B)",
        "hidden_root": "06.4 hidden shared root",
        "depth_chain": "06.5 summary-of-summary depth (1/2/4/8) (P06-C)",
        "partial_loss": "06.6 partial provenance loss (Control E)",
        "unsupported": "06.7 unsupported claim injection (Control G / F)",
        "circular": "06.8 circular citation (P06-E paired with acyclic sibling)",
        "contradiction": "06.9 provenance contradiction",
        "root_sub": "06.10 root substitution worlds A/B (Control C, P06-B)",
        "disappearance": "06.11 source disappearance (P06-H)",
        "reentry": "06.12 generated-output re-entry (P06-G)",
    },
    "counts": {
        "total_memories": len(memories),
        "total_claims": len(claims),
        "total_fact_instances": len({m['_oracle']['fact_id'] for m in memories}),
        "evidence_root_count": len(evidence_roots),
        "cycle_member_count": len(cycle_members),
        "unsupported_claim_count": len(unsupported_claims),
        "inaccessible_root_count": len(inaccessible_roots),
        "reentry_node_count": len(reentry_nodes),
        "provenance_contradiction_count": len(contradiction_nodes),
    },
    "evidence_roots": evidence_roots,
    "cycle_member_nodes": cycle_members,
    "unsupported_claim_ids": unsupported_claims,
    "inaccessible_root_ids": inaccessible_roots,
    "reentry_node_ids": reentry_nodes,
    "provenance_contradiction_ids": contradiction_nodes,
    "invariants": {
        "06-A": "Derivation is not corroboration.",
        "06-B": "Evidence roots must remain walkable where retained.",
        "06-C": "Circular support provides no new evidence (see cycle_member_nodes; ultimate_evidence_roots is [] for these).",
        "06-D": "Transformation must not erase lineage (see family=cascade, family=depth_chain chains).",
        "06-E": "Unsupported additions stay unsupported (see unsupported_claim_ids; sibling claim on the same memory is supported).",
        "06-F": "Unknown lineage must remain unknown, never fabricated (see inaccessible_root_ids; source disappearance family).",
    },
}
with open(os.path.join(BUILD_DIR, "truth_state.json"), "w") as f:
    json.dump(truth_state, f, indent=2)

print("Wrote sources.md, provenance.json, truth_state.json, ingestion_*.jsonl")
