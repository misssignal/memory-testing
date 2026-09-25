#!/usr/bin/env python3
"""Integrity checker for Experiment 16 — Multi-hop Dependencies.

Checks:
  1. Memory schema completeness
  2. Unique memory IDs
  3. Unique query IDs
  4. Four-clock temporal ordering
  5. Query schema completeness (including hop_count)
  6. Corpus size >= 200 memories, >= 75 queries
  7. Case coverage: all 7 cases (C01-C07) + background
  8. Case distribution: each case has at least 10 memories
  9. Query category coverage: at least 5 distinct categories
 10. Query category distribution: each category has at least 2 queries
 11. SHA-256 checksums match manifest
 12. No truth-role leakage in text
 13. derived_from references valid memory IDs
 14. At least 30 memories with non-empty derived_from
 15. hop_count present on all queries and >= 1
 16. Multi-hop queries present (hop_count >= 3)
 17. Chain connectivity: derived_from chains traceable
 18. Confidence values in [0,1]
"""

import json, hashlib, sys, os
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: check_exp16.py <corpus_dir>")
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

    print("=== Experiment 16 Integrity Check ===\n")

    # 1. Memory schema
    required_mem_fields = [
        "memory_id", "experiment", "story_id",
        "event_time", "observation_time", "authored_time", "ingestion_time",
        "subject", "predicate", "object", "text",
        "memory_type", "truth_role", "belief_holder", "confidence",
        "source_id", "source_type",
        "derived_from", "supersedes", "contradicts", "duplicates",
        "aliases", "scope", "tags"
    ]
    missing = []
    for m in memories:
        for fld in required_mem_fields:
            if fld not in m:
                missing.append((m.get("memory_id", "?"), fld))
    check("1. Memory schema completeness", len(missing) == 0,
          f"{len(missing)} missing: {missing[:5]}")

    # 2. Unique memory IDs
    mids = [m["memory_id"] for m in memories]
    dups = [x for x in set(mids) if mids.count(x) > 1]
    check("2. Unique memory IDs", len(dups) == 0, f"Duplicates: {dups}")

    # 3. Unique query IDs
    qids = [q["query_id"] for q in queries]
    qdups = [x for x in set(qids) if qids.count(x) > 1]
    check("3. Unique query IDs", len(qdups) == 0, f"Duplicates: {qdups}")

    # 4. Four-clock ordering
    violations = []
    for m in memories:
        try:
            et = datetime.fromisoformat(m["event_time"].replace("Z", "+00:00"))
            ot = datetime.fromisoformat(m["observation_time"].replace("Z", "+00:00"))
            at = datetime.fromisoformat(m["authored_time"].replace("Z", "+00:00"))
            it = datetime.fromisoformat(m["ingestion_time"].replace("Z", "+00:00"))
            if not (et <= ot <= at <= it):
                violations.append(m["memory_id"])
        except Exception as e:
            violations.append(f"{m.get('memory_id', '?')}: {e}")
    check("4. Four-clock temporal ordering", len(violations) == 0,
          f"{len(violations)} violations: {violations[:5]}")

    # 5. Query schema (including hop_count)
    required_q = [
        "query_id", "query", "category",
        "expected_claims", "acceptable_claims", "forbidden_claims",
        "relevant_memory_ids", "distractor_memory_ids",
        "hop_count",
        "must_surface_uncertainty", "must_surface_conflict",
        "must_disambiguate", "must_preserve_scope", "should_abstain",
        "difficulty"
    ]
    qmissing = []
    for q in queries:
        for fld in required_q:
            if fld not in q:
                qmissing.append((q.get("query_id", "?"), fld))
    check("5. Query schema completeness", len(qmissing) == 0,
          f"{len(qmissing)} missing: {qmissing[:5]}")

    # 6. Corpus size
    check("6a. Memory count >= 200", len(memories) >= 200, f"Only {len(memories)}")
    check("6b. Query count >= 75", len(queries) >= 75, f"Only {len(queries)}")

    # 7. Case coverage
    cases = set()
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                cases.add(t)
    expected = {"C01", "C02", "C03", "C04", "C05", "C06", "C07"}
    check("7a. All 7 cases present", expected - cases == set(), f"Missing: {expected - cases}")
    has_bg = any("background" in m.get("tags", []) for m in memories)
    check("7b. Background present", has_bg, "No background")

    # 8. Case distribution
    cc = {}
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                cc[t] = cc.get(t, 0) + 1
    thin = [(c, n) for c, n in cc.items() if n < 10]
    check("8. Case distribution (each >= 10)", len(thin) == 0, f"Thin: {thin}")

    # 9. Query categories
    qcats = set(q.get("category", "") for q in queries)
    check("9. Query category diversity (>= 5)", len(qcats) >= 5,
          f"Only {len(qcats)}: {qcats}")

    # 10. Query category distribution
    qcc = {}
    for q in queries:
        c = q.get("category", "?")
        qcc[c] = qcc.get(c, 0) + 1
    thin_q = [(c, n) for c, n in qcc.items() if n < 2]
    check("10. Query category distribution (each >= 2)", len(thin_q) == 0,
          f"Thin: {thin_q}")

    # 11. SHA-256
    ck_ok = True
    ck_errs = []
    for entry in manifest.get("files", []):
        fp = os.path.join(d, entry["path"])
        if os.path.exists(fp):
            h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            if h != entry.get("sha256", ""):
                ck_ok = False
                ck_errs.append(entry["path"])
    check("11. SHA-256 checksums", ck_ok, f"Mismatched: {ck_errs}")

    # 12. Truth-role leakage
    leaky = ["ground_truth", "distorted_summary", "truth_role", "adversarial_trap"]
    leak_found = []
    for m in memories:
        txt = m.get("text", "").lower()
        for term in leaky:
            if term in txt:
                leak_found.append((m["memory_id"], term))
    if leak_found:
        warn("12. Leakage", f"{len(leak_found)}: {leak_found[:5]}")
    check("12. No truth-role leakage", len(leak_found) == 0,
          f"{len(leak_found)} leaky")

    # 13. derived_from refs valid
    bad_derived = []
    for m in memories:
        for ref in m.get("derived_from", []):
            if ref not in mem_by_id:
                bad_derived.append((m["memory_id"], ref))
    check("13. derived_from refs valid", len(bad_derived) == 0,
          f"{len(bad_derived)} invalid: {bad_derived[:5]}")

    # 14. Enough derived_from links
    derived_count = sum(1 for m in memories if m.get("derived_from"))
    check("14. >= 30 memories with derived_from", derived_count >= 30,
          f"Only {derived_count}")

    # 15. hop_count present on all queries
    bad_hop = []
    for q in queries:
        hc = q.get("hop_count")
        if hc is None or not isinstance(hc, int) or hc < 1:
            bad_hop.append((q["query_id"], hc))
    check("15. hop_count present and >= 1", len(bad_hop) == 0,
          f"{len(bad_hop)} bad: {bad_hop[:5]}")

    # 16. Multi-hop queries
    multi_hop = sum(1 for q in queries if q.get("hop_count", 0) >= 3)
    check("16. >= 10 queries with hop_count >= 3", multi_hop >= 10,
          f"Only {multi_hop}")

    # 17. Chain connectivity
    chains_found = 0
    for m in memories:
        if m.get("derived_from"):
            chain_len = 1
            current = m
            visited = {current["memory_id"]}
            while current.get("derived_from"):
                parent_id = current["derived_from"][0]
                if parent_id in visited or parent_id not in mem_by_id:
                    break
                visited.add(parent_id)
                current = mem_by_id[parent_id]
                chain_len += 1
            if chain_len >= 3:
                chains_found += 1
    check("17. >= 5 chains of length >= 3", chains_found >= 5,
          f"Only {chains_found}")

    # 18. Confidence values
    bad_conf = []
    for m in memories:
        c = m.get("confidence")
        if c is None or not isinstance(c, (int, float)) or c < 0 or c > 1:
            bad_conf.append((m["memory_id"], c))
    check("18. Confidence values in [0,1]", len(bad_conf) == 0,
          f"{len(bad_conf)} bad: {bad_conf[:5]}")

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
    print(f"Cases: {dict(sorted(cc.items()))}")
    print(f"Query categories: {dict(sorted(qcc.items()))}")
    print(f"Memories with derived_from: {derived_count}")
    print(f"Multi-hop queries (>= 3): {multi_hop}")
    print(f"Chains of length >= 3: {chains_found}")

    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
