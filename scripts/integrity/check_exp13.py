#!/usr/bin/env python3
"""Integrity checker for Experiment 13 — Consolidation / Summarization Drift.

Checks:
  1. Memory schema completeness (required fields)
  2. Unique memory IDs
  3. Unique query IDs
  4. summary_layer present and in range 0-5 on every memory
  5. Four-clock temporal ordering (event <= observation <= authored <= ingestion)
  6. Query schema completeness
  7. target_layer present on queries (0-5)
  8. derived_from references valid memory IDs
  9. Corpus size >= 200 memories, >= 75 queries
 10. At least 6 summary layers present (0-5)
 11. Case coverage: all 7 cases (C01-C07) + background
 12. Layer distribution: each layer 1-5 has at least 5 memories
 13. Query category coverage: at least 7 distinct categories
 14. SHA-256 checksums match manifest
 15. No truth-role leakage in text (truth_role values shouldn't appear verbatim)
 16. Adversarial trap coverage: distorted summaries exist for each case
"""

import json, hashlib, sys, os
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: check_exp13.py <corpus_dir>")
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

    # Load data
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

    print("=== Experiment 13 Integrity Check ===\n")

    # 1. Memory schema completeness
    required_mem_fields = [
        "memory_id", "experiment", "story_id",
        "event_time", "observation_time", "authored_time", "ingestion_time",
        "subject", "predicate", "object", "text",
        "memory_type", "truth_role", "belief_holder", "confidence",
        "source_id", "source_type",
        "derived_from", "supersedes", "contradicts", "duplicates",
        "aliases", "scope", "tags", "summary_layer"
    ]
    missing_fields = []
    for m in memories:
        for f in required_mem_fields:
            if f not in m:
                missing_fields.append((m.get("memory_id", "?"), f))
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

    # 4. summary_layer present and valid
    bad_layers = []
    for m in memories:
        sl = m.get("summary_layer")
        if sl is None or not isinstance(sl, (int, float)) or sl < 0 or sl > 5:
            bad_layers.append((m["memory_id"], sl))
    check("4. summary_layer valid (0-5)",
          len(bad_layers) == 0,
          f"{len(bad_layers)} bad layers: {bad_layers[:5]}")

    # 5. Four-clock temporal ordering
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
    check("5. Four-clock temporal ordering",
          len(time_violations) == 0,
          f"{len(time_violations)} violations: {time_violations[:5]}")

    # 6. Query schema completeness
    required_q_fields = [
        "query_id", "query", "category",
        "expected_claims", "acceptable_claims", "forbidden_claims",
        "relevant_memory_ids", "distractor_memory_ids",
        "must_surface_uncertainty", "must_surface_conflict",
        "must_disambiguate", "must_preserve_scope", "should_abstain",
        "difficulty", "target_layer"
    ]
    missing_q_fields = []
    for q in queries:
        for f in required_q_fields:
            if f not in q:
                missing_q_fields.append((q.get("query_id", "?"), f))
    check("6. Query schema completeness",
          len(missing_q_fields) == 0,
          f"{len(missing_q_fields)} missing: {missing_q_fields[:5]}")

    # 7. target_layer present and valid on queries
    bad_target = []
    for q in queries:
        tl = q.get("target_layer")
        if tl is None or not isinstance(tl, (int, float)) or tl < 0 or tl > 5:
            bad_target.append((q["query_id"], tl))
    check("7. target_layer valid on queries",
          len(bad_target) == 0,
          f"{len(bad_target)} bad: {bad_target[:5]}")

    # 8. derived_from references valid IDs
    bad_refs = []
    for m in memories:
        for ref in m.get("derived_from", []):
            if ref not in mem_by_id:
                bad_refs.append((m["memory_id"], ref))
    check("8. derived_from references valid",
          len(bad_refs) == 0,
          f"{len(bad_refs)} invalid refs: {bad_refs[:5]}")

    # 9. Corpus size targets
    check("9a. Memory count >= 200",
          len(memories) >= 200,
          f"Only {len(memories)} memories")
    check("9b. Query count >= 75",
          len(queries) >= 75,
          f"Only {len(queries)} queries")

    # 10. All 6 summary layers present
    present_layers = set()
    for m in memories:
        present_layers.add(m.get("summary_layer", -1))
    missing_layers = set(range(6)) - present_layers
    check("10. All summary layers (0-5) present",
          len(missing_layers) == 0,
          f"Missing layers: {missing_layers}")

    # 11. Case coverage
    cases_found = set()
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                cases_found.add(t)
    expected_cases = {"C01", "C02", "C03", "C04", "C05", "C06", "C07"}
    missing_cases = expected_cases - cases_found
    has_background = any("background" in m.get("tags", []) for m in memories)
    check("11a. All 7 cases present",
          len(missing_cases) == 0,
          f"Missing: {missing_cases}")
    check("11b. Background memories present",
          has_background,
          "No background memories found")

    # 12. Layer distribution: each non-zero layer has at least 5 memories
    layer_counts = {}
    for m in memories:
        sl = m.get("summary_layer", 0)
        layer_counts[sl] = layer_counts.get(sl, 0) + 1
    thin_layers = [(l, c) for l, c in layer_counts.items() if l > 0 and c < 5]
    check("12. Layer distribution (layers 1-5 >= 5 each)",
          len(thin_layers) == 0,
          f"Thin layers: {thin_layers}")

    # 13. Query category coverage
    q_cats = set(q.get("category", "") for q in queries)
    check("13. Query category diversity (>= 7)",
          len(q_cats) >= 7,
          f"Only {len(q_cats)} categories: {q_cats}")

    # 14. SHA-256 checksums
    checksum_ok = True
    checksum_errs = []
    for entry in manifest.get("files", []):
        fp = os.path.join(d, entry["path"])
        if os.path.exists(fp):
            h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            if h != entry.get("sha256", ""):
                checksum_ok = False
                checksum_errs.append(entry["path"])
    check("14. SHA-256 checksums match manifest",
          checksum_ok,
          f"Mismatched: {checksum_errs}")

    # 15. Truth-role leakage check
    leaky_terms = ["ground_truth", "distorted_summary", "truth_role", "adversarial_trap"]
    leaky_mems = []
    for m in memories:
        text_lower = m.get("text", "").lower()
        for term in leaky_terms:
            if term in text_lower:
                leaky_mems.append((m["memory_id"], term))
    if leaky_mems:
        warn("15. Truth-role leakage", f"{len(leaky_mems)} memories contain truth-role terms: {leaky_mems[:5]}")
    else:
        check("15. No truth-role leakage in text", True)
        checks_total -= 1  # Don't double-count
        checks_passed -= 1
    checks_total += 1
    checks_passed += 1 if not leaky_mems else 0

    # 16. Adversarial trap coverage: each case has distorted summaries
    cases_with_distortion = set()
    for m in memories:
        if m.get("truth_role") in ("distorted_summary", "false_summary"):
            for t in m.get("tags", []):
                if t.startswith("C0"):
                    cases_with_distortion.add(t)
    missing_distortion = expected_cases - cases_with_distortion
    check("16. Each case has distorted summaries",
          len(missing_distortion) == 0,
          f"Missing distortion in: {missing_distortion}")

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
    print(f"Summary layers: {dict(sorted(layer_counts.items()))}")
    print(f"Query categories: {len(q_cats)}")

    return 0 if len(errors) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
