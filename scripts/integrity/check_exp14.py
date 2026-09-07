#!/usr/bin/env python3
"""Integrity checker for Experiment 14 — Semantic Near-Miss / Distractor Resistance.

Checks:
  1. Memory schema completeness (required fields)
  2. Unique memory IDs
  3. Unique query IDs
  4. Four-clock temporal ordering (event <= observation <= authored <= ingestion)
  5. Query schema completeness
  6. Corpus size >= 200 memories, >= 75 queries
  7. Case coverage: all 7 cases (C01-C07) + background
  8. Case distribution: each case has at least 10 memories
  9. Query category coverage: at least 7 distinct categories
 10. Query category distribution: each category has at least 5 queries
 11. SHA-256 checksums match manifest
 12. No truth-role leakage in text
 13. Distractor memory IDs reference valid memories
 14. Relevant memory IDs reference valid memories
 15. Boat-specificity: Albatross and Petrel memories exist separately
 16. Temporal-pair coverage: both 2032 and 2036 campaign memories exist
 17. Name collision pair: both O'Brien and O'Brien-Sato memories exist
"""

import json, hashlib, sys, os
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: check_exp14.py <corpus_dir>")
        sys.exit(1)

    d = sys.argv[1]
    errors = []
    warnings = []
    checks_passed = 0
    checks_total = 0

    def check(name, ok, msg=""):
        nonlocal checks_passed, checks_total
        checks_total += 1
        if ok:
            checks_passed += 1
            print(f"  [PASS] {name}")
        else:
            errors.append(f"{name}: {msg}")
            print(f"  [FAIL] {name}: {msg}")

    def warn(name, msg):
        warnings.append(f"{name}: {msg}")
        print(f"  [WARN] {name}: {msg}")

    mem_path = os.path.join(d, "memories.jsonl")
    q_path = os.path.join(d, "queries.jsonl")
    manifest_path = os.path.join(d, "manifest.json")

    with open(mem_path) as f:
        memories = [json.loads(l) for l in f if l.strip()]
    with open(q_path) as f:
        queries = [json.loads(l) for l in f if l.strip()]
    with open(manifest_path) as f:
        manifest = json.load(f)

    mem_by_id = {m["memory_id"]: m for m in memories}

    print("=== Experiment 14 Integrity Check ===\n")

    # 1. Memory schema completeness
    required_mem_fields = [
        "memory_id", "experiment", "story_id",
        "event_time", "observation_time", "authored_time", "ingestion_time",
        "subject", "predicate", "object", "text",
        "memory_type", "truth_role", "belief_holder", "confidence",
        "source_id", "source_type",
        "derived_from", "supersedes", "contradicts", "duplicates",
        "aliases", "scope", "tags"
    ]
    missing_fields = []
    for m in memories:
        for fld in required_mem_fields:
            if fld not in m:
                missing_fields.append((m.get("memory_id", "?"), fld))
    check("1. Memory schema completeness",
          len(missing_fields) == 0,
          f"{len(missing_fields)} missing fields: {missing_fields[:5]}")

    # 2. Unique memory IDs
    mem_ids = [m["memory_id"] for m in memories]
    dup_mids = [x for x in set(mem_ids) if mem_ids.count(x) > 1]
    check("2. Unique memory IDs",
          len(dup_mids) == 0,
          f"Duplicate IDs: {dup_mids}")

    # 3. Unique query IDs
    q_ids = [q["query_id"] for q in queries]
    dup_qids = [x for x in set(q_ids) if q_ids.count(x) > 1]
    check("3. Unique query IDs",
          len(dup_qids) == 0,
          f"Duplicate IDs: {dup_qids}")

    # 4. Four-clock temporal ordering
    time_violations = []
    for m in memories:
        try:
            et = datetime.fromisoformat(m["event_time"].replace("Z", "+00:00"))
            ot = datetime.fromisoformat(m["observation_time"].replace("Z", "+00:00"))
            at = datetime.fromisoformat(m["authored_time"].replace("Z", "+00:00"))
            it = datetime.fromisoformat(m["ingestion_time"].replace("Z", "+00:00"))
            if not (et <= ot <= at <= it):
                time_violations.append(m["memory_id"])
        except (ValueError, KeyError) as e:
            time_violations.append(f"{m.get('memory_id', '?')}: {e}")
    check("4. Four-clock temporal ordering",
          len(time_violations) == 0,
          f"{len(time_violations)} violations: {time_violations[:5]}")

    # 5. Query schema completeness
    required_q_fields = [
        "query_id", "query", "category",
        "expected_claims", "acceptable_claims", "forbidden_claims",
        "relevant_memory_ids", "distractor_memory_ids",
        "must_surface_uncertainty", "must_surface_conflict",
        "must_disambiguate", "must_preserve_scope", "should_abstain",
        "difficulty"
    ]
    missing_q_fields = []
    for q in queries:
        for fld in required_q_fields:
            if fld not in q:
                missing_q_fields.append((q.get("query_id", "?"), fld))
    check("5. Query schema completeness",
          len(missing_q_fields) == 0,
          f"{len(missing_q_fields)} missing: {missing_q_fields[:5]}")

    # 6. Corpus size
    check("6a. Memory count >= 200",
          len(memories) >= 200,
          f"Only {len(memories)} memories")
    check("6b. Query count >= 75",
          len(queries) >= 75,
          f"Only {len(queries)} queries")

    # 7. Case coverage
    cases_found = set()
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                cases_found.add(t)
    expected_cases = {"C01", "C02", "C03", "C04", "C05", "C06", "C07"}
    missing_cases = expected_cases - cases_found
    has_background = any("background" in m.get("tags", []) for m in memories)
    check("7a. All 7 cases present",
          len(missing_cases) == 0,
          f"Missing: {missing_cases}")
    check("7b. Background memories present",
          has_background,
          "No background memories found")

    # 8. Case distribution
    case_counts = {}
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                case_counts[t] = case_counts.get(t, 0) + 1
    thin_cases = [(c, n) for c, n in case_counts.items() if n < 10]
    check("8. Case distribution (each >= 10 memories)",
          len(thin_cases) == 0,
          f"Thin cases: {thin_cases}")

    # 9. Query category coverage
    q_cats = set(q.get("category", "") for q in queries)
    check("9. Query category diversity (>= 7)",
          len(q_cats) >= 7,
          f"Only {len(q_cats)} categories: {q_cats}")

    # 10. Query category distribution
    cat_counts = {}
    for q in queries:
        c = q.get("category", "?")
        cat_counts[c] = cat_counts.get(c, 0) + 1
    thin_cats = [(c, n) for c, n in cat_counts.items() if n < 5]
    check("10. Query category distribution (each >= 5)",
          len(thin_cats) == 0,
          f"Thin categories: {thin_cats}")

    # 11. SHA-256 checksums
    checksum_ok = True
    checksum_errs = []
    for entry in manifest.get("files", []):
        fp = os.path.join(d, entry["path"])
        if os.path.exists(fp):
            h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            if h != entry.get("sha256", ""):
                checksum_ok = False
                checksum_errs.append(entry["path"])
    check("11. SHA-256 checksums match manifest",
          checksum_ok,
          f"Mismatched: {checksum_errs}")

    # 12. Truth-role leakage
    leaky_terms = ["ground_truth", "distorted_summary", "truth_role", "adversarial_trap"]
    leaky_mems = []
    for m in memories:
        text_lower = m.get("text", "").lower()
        for term in leaky_terms:
            if term in text_lower:
                leaky_mems.append((m["memory_id"], term))
    if leaky_mems:
        warn("12. Truth-role leakage", f"{len(leaky_mems)} memories contain truth-role terms: {leaky_mems[:5]}")
    check("12. No truth-role leakage in text",
          len(leaky_mems) == 0,
          f"{len(leaky_mems)} leaky memories")

    # 13. Distractor memory IDs reference valid memories
    bad_distractors = []
    for q in queries:
        for ref in q.get("distractor_memory_ids", []):
            if ref not in mem_by_id:
                bad_distractors.append((q["query_id"], ref))
    check("13. Distractor memory IDs valid",
          len(bad_distractors) == 0,
          f"{len(bad_distractors)} invalid refs: {bad_distractors[:5]}")

    # 14. Relevant memory IDs reference valid memories
    bad_relevant = []
    for q in queries:
        for ref in q.get("relevant_memory_ids", []):
            if ref not in mem_by_id:
                bad_relevant.append((q["query_id"], ref))
    check("14. Relevant memory IDs valid",
          len(bad_relevant) == 0,
          f"{len(bad_relevant)} invalid refs: {bad_relevant[:5]}")

    # 15. Boat-specificity
    albatross_mems = [m for m in memories if "Albatross" in str(m.get("tags", []))]
    petrel_mems = [m for m in memories if "Petrel" in str(m.get("tags", []))]
    check("15a. Albatross memories exist (>= 10)",
          len(albatross_mems) >= 10,
          f"Only {len(albatross_mems)} Albatross memories")
    check("15b. Petrel memories exist (>= 10)",
          len(petrel_mems) >= 10,
          f"Only {len(petrel_mems)} Petrel memories")

    # 16. Temporal pair coverage
    mems_2032 = [m for m in memories if "2032" in str(m.get("tags", []))]
    mems_2036 = [m for m in memories if "2036" in str(m.get("tags", []))]
    check("16a. 2032 campaign memories exist (>= 5)",
          len(mems_2032) >= 5,
          f"Only {len(mems_2032)} memories tagged 2032")
    check("16b. 2036 campaign memories exist (>= 5)",
          len(mems_2036) >= 5,
          f"Only {len(mems_2036)} memories tagged 2036")

    # 17. Name collision pair
    obrien_mems = [m for m in memories if "O'Brien" in m.get("subject", "") and "O'Brien-Sato" not in m.get("subject", "")]
    obrien_sato_mems = [m for m in memories if "O'Brien-Sato" in m.get("subject", "")]
    check("17a. Liam O'Brien memories exist",
          len(obrien_mems) >= 3,
          f"Only {len(obrien_mems)} O'Brien memories")
    check("17b. Liam O'Brien-Sato memories exist",
          len(obrien_sato_mems) >= 3,
          f"Only {len(obrien_sato_mems)} O'Brien-Sato memories")

    # Summary
    print(f"\n=== Results ===")
    print(f"Checks passed: {checks_passed}/{checks_total}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    print(f"\nCorpus: {len(memories)} memories, {len(queries)} queries")
    print(f"Cases: {dict(sorted(case_counts.items()))}")
    print(f"Query categories: {dict(sorted(cat_counts.items()))}")

    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
