#!/usr/bin/env python3
"""Integrity checker for Experiment 20 — Cross-Context Transfer / Scope Boundary Violation."""

import json, hashlib, os, sys

corpus_dir = sys.argv[1] if len(sys.argv) > 1 else "experiment_20_scope_boundary"

with open(os.path.join(corpus_dir, "memories.jsonl")) as f:
    memories = [json.loads(l) for l in f]
with open(os.path.join(corpus_dir, "queries.jsonl")) as f:
    queries = [json.loads(l) for l in f]
with open(os.path.join(corpus_dir, "manifest.json")) as f:
    manifest = json.load(f)

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  PASS  {name}")
        PASS += 1
    else:
        print(f"  FAIL  {name}  {detail}")
        FAIL += 1

MEMORY_KEYS = {
    "memory_id","experiment","story_id","event_time","observation_time",
    "authored_time","ingestion_time","subject","predicate","object","text",
    "memory_type","truth_role","belief_holder","confidence","source_id",
    "source_type","derived_from","supersedes","contradicts","duplicates",
    "aliases","scope","tags"
}
QUERY_KEYS = {
    "query_id","query","category","expected_claims","acceptable_claims",
    "forbidden_claims","relevant_memory_ids","distractor_memory_ids",
    "difficulty","must_surface_uncertainty","must_surface_conflict",
    "must_disambiguate","must_preserve_scope","should_abstain","notes"
}

print("=== Experiment 20 Integrity Check ===\n")

# 1. Memory schema completeness
missing_keys = []
for m in memories:
    diff = MEMORY_KEYS - set(m.keys())
    if diff:
        missing_keys.append((m["memory_id"], diff))
check("1. Memory schema completeness", not missing_keys,
      f"{len(missing_keys)} memories missing keys")

# 2. Unique memory IDs
mids = [m["memory_id"] for m in memories]
check("2. Unique memory IDs", len(mids) == len(set(mids)),
      f"{len(mids) - len(set(mids))} duplicates")

# 3. Unique query IDs
qids = [q["query_id"] for q in queries]
check("3. Unique query IDs", len(qids) == len(set(qids)),
      f"{len(qids) - len(set(qids))} duplicates")

# 4. Four-clock temporal ordering
bad_clocks = []
for m in memories:
    times = [m["event_time"], m["observation_time"], m["authored_time"], m["ingestion_time"]]
    if times != sorted(times):
        bad_clocks.append(m["memory_id"])
check("4. Four-clock temporal ordering", not bad_clocks,
      f"{len(bad_clocks)} violations: {bad_clocks[:5]}")

# 5. Query schema completeness
missing_qkeys = []
for q in queries:
    diff = QUERY_KEYS - set(q.keys())
    if diff:
        missing_qkeys.append((q["query_id"], diff))
check("5. Query schema completeness", not missing_qkeys,
      f"{len(missing_qkeys)} queries missing keys")

# 6a/6b. Corpus size
check("6a. Corpus >= 200 memories", len(memories) >= 200, f"got {len(memories)}")
check("6b. Corpus >= 75 queries", len(queries) >= 75, f"got {len(queries)}")

# 7. Case coverage
all_tags = set()
for m in memories:
    all_tags.update(m.get("tags", []))
expected_cases = {"C01","C02","C03","C04","C05","C06","C07","background"}
check("7. Case coverage (C01-C07 + background)", expected_cases <= all_tags,
      f"missing: {expected_cases - all_tags}")

# 8. Case distribution (each case >= 10 memories)
case_counts = {}
for m in memories:
    for t in m.get("tags", []):
        if t.startswith("C0") or t == "background":
            case_counts[t] = case_counts.get(t, 0) + 1
low_cases = {k: v for k, v in case_counts.items() if v < 10}
check("8. Case distribution (each >= 10)", not low_cases,
      f"low: {low_cases}")

# 9. Query category diversity (>= 7 categories)
cats = set(q["category"] for q in queries)
check("9. Query category diversity (>= 7)", len(cats) >= 7,
      f"got {len(cats)}: {cats}")

# 10. Query category distribution (each >= 2)
cat_counts = {}
for q in queries:
    c = q["category"]
    cat_counts[c] = cat_counts.get(c, 0) + 1
low_cats = {k: v for k, v in cat_counts.items() if v < 2}
check("10. Query category distribution (each >= 2)", not low_cats,
      f"low: {low_cats}")

# 11. SHA-256 checksums
checksum_ok = True
for entry in manifest["files"]:
    path = os.path.join(corpus_dir, entry["path"])
    with open(path, "rb") as ff:
        actual = hashlib.sha256(ff.read()).hexdigest()
    if actual != entry["sha256"]:
        checksum_ok = False
check("11. SHA-256 checksums match manifest", checksum_ok)

# 12. No truth-role leakage in text
leak_words = ["ground_truth", "scoped_true", "out_of_scope", "scope_violation", "supporting_belief", "contextual_true"]
leaks = []
for m in memories:
    txt = m.get("text", "").lower()
    for w in leak_words:
        if w in txt:
            leaks.append((m["memory_id"], w))
check("12. No truth-role leakage in text", not leaks,
      f"{len(leaks)} leaks: {leaks[:5]}")

# 13. Truth role diversity (>= 4)
roles = set(m["truth_role"] for m in memories)
check("13. Truth role diversity (>= 4)", len(roles) >= 4,
      f"got {len(roles)}: {roles}")

# 14. Confidence values in [0,1]
bad_conf = [m["memory_id"] for m in memories if not (0 <= m["confidence"] <= 1)]
check("14. Confidence values in [0,1]", not bad_conf,
      f"{len(bad_conf)} out of range")

# --- Scope-specific checks ---

# 15. scoped:project tags >= 20
scoped_proj = sum(1 for m in memories if "scoped:project" in m.get("tags",[]))
check("15. >= 20 scoped:project tags", scoped_proj >= 20, f"got {scoped_proj}")

# 16. scoped:jurisdiction tags >= 10
scoped_jur = sum(1 for m in memories if "scoped:jurisdiction" in m.get("tags",[]))
check("16. >= 10 scoped:jurisdiction tags", scoped_jur >= 10, f"got {scoped_jur}")

# 17. scoped:role tags >= 10
scoped_role = sum(1 for m in memories if "scoped:role" in m.get("tags",[]))
check("17. >= 10 scoped:role tags", scoped_role >= 10, f"got {scoped_role}")

# 18. scoped:temporal tags >= 10
scoped_temp = sum(1 for m in memories if "scoped:temporal" in m.get("tags",[]))
check("18. >= 10 scoped:temporal tags", scoped_temp >= 10, f"got {scoped_temp}")

# 19. scoped:record_status tags >= 5
scoped_rec = sum(1 for m in memories if "scoped:record_status" in m.get("tags",[]))
check("19. >= 5 scoped:record_status tags", scoped_rec >= 5, f"got {scoped_rec}")

# 20. >= 5 out_of_scope truth role
oos_count = sum(1 for m in memories if m["truth_role"] == "out_of_scope")
check("20. >= 5 out_of_scope truth role", oos_count >= 5, f"got {oos_count}")

# 21. >= 5 scope_violation truth role
sv_count = sum(1 for m in memories if m["truth_role"] == "scope_violation")
check("21. >= 5 scope_violation truth role", sv_count >= 5, f"got {sv_count}")

# 22. >= 10 confidential tags
conf_count = sum(1 for m in memories if "confidential" in m.get("tags",[]))
check("22. >= 10 confidential tags", conf_count >= 10, f"got {conf_count}")

# 23. >= 3 off_record tags
offr_count = sum(1 for m in memories if "off_record" in m.get("tags",[]))
check("23. >= 3 off_record tags", offr_count >= 3, f"got {offr_count}")

# 24. Phase tags present (phase_1, phase_2, phase_3 each >= 3)
for phase in ["phase_1", "phase_2", "phase_3"]:
    pc = sum(1 for m in memories if phase in m.get("tags",[]))
    check(f"24{phase[-1]}. >= 3 {phase} tags", pc >= 3, f"got {pc}")

# 25. Belief holder diversity (>= 8)
holders = set(m.get("belief_holder","") for m in memories)
check("25. Belief holder diversity (>= 8)", len(holders) >= 8,
      f"got {len(holders)}")

# 26. All memory IDs match E20- prefix
bad_prefix = [m["memory_id"] for m in memories if not m["memory_id"].startswith("E20-")]
check("26. Memory ID prefix E20-", not bad_prefix,
      f"{len(bad_prefix)} bad: {bad_prefix[:5]}")

# 27. All query IDs match Q20- prefix
bad_qprefix = [q["query_id"] for q in queries if not q["query_id"].startswith("Q20-")]
check("27. Query ID prefix Q20-", not bad_qprefix,
      f"{len(bad_qprefix)} bad: {bad_qprefix[:5]}")

print(f"\n=== Results: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
