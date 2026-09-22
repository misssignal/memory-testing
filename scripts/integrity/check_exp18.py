#!/usr/bin/env python3
"""Integrity checker for Experiment 18 — Counterfactual / Negative Evidence.

Checks:
  1. Memory schema completeness
  2. Unique memory IDs
  3. Unique query IDs
  4. Four-clock temporal ordering
  5. Query schema completeness
  6. Corpus size >= 200 memories, >= 75 queries
  7. Case coverage: all 7 cases (C01-C07) + background
  8. Case distribution: each case has at least 10 memories
  9. Query category coverage: at least 7 distinct categories
 10. Query category distribution: each category has at least 2 queries
 11. SHA-256 checksums match manifest
 12. No truth-role leakage in text
 13. Truth role diversity: at least 4 distinct truth roles
 14. Confidence values in [0,1]
 15. At least 10 memories with contradicts links
 16. At least 5 memories with supersedes links
 17. Negation tag coverage: at least 15 memories tagged 'negation'
 18. Counterfactual tag coverage: at least 15 memories tagged 'counterfactual'
 19. Belief holder diversity: at least 8 distinct holders
"""

import json, hashlib, sys, os
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: check_exp18.py <corpus_dir>")
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

    print("=== Experiment 18 Integrity Check ===\n")

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

    # 5. Query schema
    required_q = [
        "query_id", "query", "category",
        "expected_claims", "acceptable_claims", "forbidden_claims",
        "relevant_memory_ids", "distractor_memory_ids",
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
    check("9. Query category diversity (>= 7)", len(qcats) >= 7,
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
    leaky = ["ground_truth", "belief_only", "truth_role", "contextual_true",
             "supporting_belief", "counterfactual"]
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

    # 13. Truth role diversity
    roles = set(m.get("truth_role", "") for m in memories)
    check("13. Truth role diversity (>= 4)", len(roles) >= 4,
          f"Only {len(roles)}: {roles}")

    # 14. Confidence values
    bad_conf = []
    for m in memories:
        c = m.get("confidence")
        if c is None or not isinstance(c, (int, float)) or c < 0 or c > 1:
            bad_conf.append((m["memory_id"], c))
    check("14. Confidence values in [0,1]", len(bad_conf) == 0,
          f"{len(bad_conf)} bad: {bad_conf[:5]}")

    # 15. Contradicts links
    contra_count = sum(1 for m in memories if m.get("contradicts"))
    check("15. >= 10 memories with contradicts", contra_count >= 10,
          f"Only {contra_count}")

    # 16. Supersedes links
    sup_count = sum(1 for m in memories if m.get("supersedes"))
    check("16. >= 5 memories with supersedes", sup_count >= 5,
          f"Only {sup_count}")

    # 17. Negation tag coverage
    neg_count = sum(1 for m in memories if "negation" in m.get("tags", []))
    check("17. >= 15 memories tagged 'negation'", neg_count >= 15,
          f"Only {neg_count}")

    # 18. Counterfactual tag coverage
    cf_count = sum(1 for m in memories if "counterfactual" in m.get("tags", []))
    check("18. >= 15 memories tagged 'counterfactual'", cf_count >= 15,
          f"Only {cf_count}")

    # 19. Belief holder diversity
    holders = set(m.get("belief_holder", "") for m in memories)
    check("19. Belief holder diversity (>= 8)", len(holders) >= 8,
          f"Only {len(holders)}: {holders}")

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
    print(f"Truth roles: {sorted(roles)}")
    print(f"Belief holders: {sorted(holders)}")
    print(f"Contradicts: {contra_count}, Supersedes: {sup_count}")
    print(f"Negation tagged: {neg_count}, Counterfactual tagged: {cf_count}")

    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
