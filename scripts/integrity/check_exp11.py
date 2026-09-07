#!/usr/bin/env python3
"""Integrity checker for Experiment 11: Forgetting / Retraction / Deletion Semantics."""

import json
import hashlib
import sys
from pathlib import Path
from collections import Counter


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def check(exp_dir):
    exp_dir = Path(exp_dir)
    errors = []
    warnings = []

    def err(msg):
        errors.append(msg)
        print(f"  ERROR: {msg}")

    def warn(msg):
        warnings.append(msg)
        print(f"  WARN:  {msg}")

    # ── Load files ────────────────────────────────────────────────────
    print("Loading files...")
    required_files = [
        "memories.jsonl", "queries.jsonl", "truth_state.json",
        "manifest.json", "seed_memories.jsonl", "story_bible.md",
        "experimental_map.json", "sources.md", "README.md",
        "perturbations/manifest.json",
    ]
    for f in required_files:
        if not (exp_dir / f).exists():
            err(f"Missing required file: {f}")

    if errors:
        return False

    memories = []
    with open(exp_dir / "memories.jsonl") as f:
        for line in f:
            memories.append(json.loads(line))

    queries = []
    with open(exp_dir / "queries.jsonl") as f:
        for line in f:
            queries.append(json.loads(line))

    with open(exp_dir / "truth_state.json") as f:
        truth = json.load(f)

    with open(exp_dir / "manifest.json") as f:
        manifest = json.load(f)

    seeds = []
    with open(exp_dir / "seed_memories.jsonl") as f:
        for line in f:
            seeds.append(json.loads(line))

    print(f"  Loaded: {len(memories)} memories, {len(queries)} queries, {len(seeds)} seeds")

    # ── 1. Manifest checksums ─────────────────────────────────────────
    print("\n[1] Manifest checksums...")
    for entry in manifest.get("files", []):
        fpath = exp_dir / entry["path"]
        if not fpath.exists():
            err(f"Manifest lists {entry['path']} but file missing")
            continue
        actual_size = fpath.stat().st_size
        actual_hash = sha256_file(fpath)
        if actual_size != entry["bytes"]:
            err(f"{entry['path']}: size mismatch (manifest={entry['bytes']}, actual={actual_size})")
        if actual_hash != entry["sha256"]:
            err(f"{entry['path']}: SHA-256 mismatch")

    manifest_paths = {e["path"] for e in manifest.get("files", [])}
    for fpath in exp_dir.rglob("*"):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = str(fpath.relative_to(exp_dir))
            if rel not in manifest_paths:
                warn(f"File not in manifest: {rel}")

    # ── 2. Memory IDs ─────────────────────────────────────────────────
    print("\n[2] Memory IDs...")
    ids = [m["memory_id"] for m in memories]
    id_set = set(ids)

    if len(ids) != len(id_set):
        dupes = [mid for mid, c in Counter(ids).items() if c > 1]
        err(f"Duplicate memory IDs: {dupes[:5]}")

    expected_ids = {f"M{i+1:04d}" for i in range(len(memories))}
    missing = expected_ids - id_set
    extra = id_set - expected_ids
    if missing:
        err(f"Missing IDs: {sorted(missing)[:5]}...")
    if extra:
        err(f"Extra IDs: {sorted(extra)[:5]}...")

    if manifest.get("canonical_memory_count") != len(memories):
        err(f"Manifest memory count ({manifest.get('canonical_memory_count')}) != actual ({len(memories)})")

    # ── 3. Unique texts ───────────────────────────────────────────────
    print("\n[3] Unique texts...")
    texts = [m["text"] for m in memories]
    text_counts = Counter(texts)
    dupes = [(t[:60], c) for t, c in text_counts.items() if c > 1]
    if dupes:
        err(f"{len(dupes)} duplicate texts: {dupes[0][0]}... (×{dupes[0][1]})")

    # ── 4. Four-clock ordering ────────────────────────────────────────
    print("\n[4] Four-clock ordering...")
    clock_violations = 0
    for m in memories:
        et = m.get("event_time", "")
        ot = m.get("observation_time", "")
        at = m.get("authored_time", "")
        it = m.get("ingestion_time", "")
        if et > ot:
            clock_violations += 1
            err(f"{m['memory_id']}: event_time > observation_time")
        if ot > at:
            clock_violations += 1
            err(f"{m['memory_id']}: observation_time > authored_time")
        if at > it:
            clock_violations += 1
            err(f"{m['memory_id']}: authored_time > ingestion_time")
    if clock_violations == 0:
        print("  All memories pass four-clock ordering.")

    # Check ingestion order
    ing_times = [m["ingestion_time"] for m in memories]
    if ing_times != sorted(ing_times):
        err("Memories not in ingestion order")

    # ── 5. Relation references ────────────────────────────────────────
    print("\n[5] Relation references...")
    bad_refs = 0
    for m in memories:
        for field in ["derived_from", "supersedes", "contradicts"]:
            for ref in m.get(field, []):
                if ref not in id_set:
                    bad_refs += 1
                    err(f"{m['memory_id']} {field} -> {ref} (not found)")
    if bad_refs == 0:
        print("  All relation references resolve.")

    # ── 6. Query references ───────────────────────────────────────────
    print("\n[6] Query references...")
    qids = [q["query_id"] for q in queries]
    if len(qids) != len(set(qids)):
        err(f"Duplicate query IDs")

    bad_qrefs = 0
    empty_relevant = 0
    for q in queries:
        rids = q.get("relevant_memory_ids", [])
        if not rids:
            empty_relevant += 1
            warn(f"{q['query_id']}: empty relevant_memory_ids")
        for rid in rids:
            if rid not in id_set:
                bad_qrefs += 1
                err(f"{q['query_id']} relevant -> {rid} (not found)")
        for rid in q.get("distractor_memory_ids", []):
            if rid not in id_set:
                bad_qrefs += 1
                err(f"{q['query_id']} distractor -> {rid} (not found)")
    if bad_qrefs == 0:
        print("  All query references resolve.")
    if empty_relevant > 0:
        warn(f"{empty_relevant} queries have empty relevant_memory_ids")

    if manifest.get("query_count") != len(queries):
        err(f"Manifest query count ({manifest.get('query_count')}) != actual ({len(queries)})")

    # ── 7. Deletion status coverage ───────────────────────────────────
    print("\n[7] Deletion status coverage...")
    del_counts = Counter()
    for m in memories:
        ds = m.get("deletion_status")
        if ds:
            del_counts[ds] += 1

    expected_types = {"SUPERSEDED", "RETRACTED", "MUST_NOT_RETRIEVE", "DISPROVEN",
                      "SOURCE_DELETED", "MUST_RETAIN", "REINSTATED"}
    present_types = set(del_counts.keys())
    missing_types = expected_types - present_types
    if missing_types:
        err(f"Missing deletion types: {missing_types}")
    extra_types = present_types - expected_types
    if extra_types:
        warn(f"Unexpected deletion types: {extra_types}")

    for dtype, count in sorted(del_counts.items()):
        print(f"  {dtype}: {count}")

    # ── 8. Case coverage ──────────────────────────────────────────────
    print("\n[8] Case coverage...")
    case_counts = Counter()
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0") and len(t) == 3:
                case_counts[t] += 1

    expected_cases = {"C01", "C02", "C03", "C04", "C05", "C06", "C07"}
    present_cases = set(case_counts.keys())
    missing_cases = expected_cases - present_cases
    if missing_cases:
        err(f"Missing cases: {missing_cases}")

    for case, count in sorted(case_counts.items()):
        print(f"  {case}: {count} memories")

    bg_count = sum(1 for m in memories if "background" in m.get("tags", []))
    print(f"  Background: {bg_count} memories")

    # ── 9. Seed consistency ───────────────────────────────────────────
    print("\n[9] Seed consistency...")
    mem_by_id = {m["memory_id"]: m for m in memories}
    seed_mismatches = 0
    for s in seeds:
        sid = s["memory_id"]
        if sid not in mem_by_id:
            err(f"Seed {sid} not in memories")
            continue
        if s["text"] != mem_by_id[sid]["text"]:
            seed_mismatches += 1
            err(f"Seed {sid}: text differs from memory")
    if seed_mismatches == 0:
        print(f"  All {len(seeds)} seeds match their memory counterparts.")

    # ── 10. Truth state ───────────────────────────────────────────────
    print("\n[10] Truth state...")
    if "deletion_taxonomy" not in truth:
        err("truth_state.json missing deletion_taxonomy")
    else:
        tax_types = set(truth["deletion_taxonomy"].keys())
        if tax_types != expected_types:
            err(f"Taxonomy types mismatch: missing={expected_types - tax_types}, extra={tax_types - expected_types}")

    if "current_truths" not in truth:
        err("truth_state.json missing current_truths")

    if "cases" not in truth:
        err("truth_state.json missing cases")
    else:
        truth_cases = set(truth["cases"].keys())
        if truth_cases != expected_cases:
            err(f"Truth cases mismatch: {truth_cases} vs {expected_cases}")

    # ── 11. Memory schema fields ──────────────────────────────────────
    print("\n[11] Memory schema completeness...")
    required_fields = [
        "memory_id", "experiment", "story_id", "event_time", "observation_time",
        "authored_time", "ingestion_time", "subject", "predicate", "object",
        "text", "memory_type", "truth_role", "source_id", "source_type",
        "derived_from", "supersedes", "contradicts", "duplicates", "aliases",
        "scope", "tags",
    ]
    field_missing = Counter()
    for m in memories:
        for f in required_fields:
            if f not in m:
                field_missing[f] += 1
    if field_missing:
        for f, c in field_missing.most_common():
            err(f"Field '{f}' missing from {c} memories")
    else:
        print("  All required fields present.")

    # ── 12. Query schema fields ───────────────────────────────────────
    print("\n[12] Query schema completeness...")
    required_q_fields = [
        "query_id", "query", "category", "expected_claims",
        "relevant_memory_ids", "forbidden_claims",
    ]
    q_field_missing = Counter()
    for q in queries:
        for f in required_q_fields:
            if f not in q:
                q_field_missing[f] += 1
    if q_field_missing:
        for f, c in q_field_missing.most_common():
            err(f"Query field '{f}' missing from {c} queries")
    else:
        print("  All required query fields present.")

    # ── 13. Adversarial trap validation ───────────────────────────────
    print("\n[13] Adversarial trap validation...")

    # C01: 200mg should have MORE memories than 120mg
    c01_200_count = sum(1 for m in memories if "200mg" in m.get("tags", []))
    c01_120_count = sum(1 for m in memories if "120mg" in m.get("tags", []))
    if c01_200_count <= c01_120_count:
        warn(f"C01 trap weakened: 200mg ({c01_200_count}) should outnumber 120mg ({c01_120_count})")
    else:
        print(f"  C01: 200mg ({c01_200_count}) > 120mg ({c01_120_count}) — volume-vs-recency trap intact")

    # C02: pre-retraction derivatives should outnumber post-retraction
    c02_pre = sum(1 for m in memories if "pre_retraction" in m.get("tags", []))
    c02_post = sum(1 for m in memories if "p_0.04" in m.get("tags", []))
    print(f"  C02: pre-retraction ({c02_pre}) vs post ({c02_post}) — retraction cascade trap")

    # C03: deleted memories should exist but be marked
    c03_deleted = sum(1 for m in memories if m.get("deletion_status") == "MUST_NOT_RETRIEVE")
    print(f"  C03: {c03_deleted} memories marked MUST_NOT_RETRIEVE")

    # C04: COX-2 memories should outnumber JAK-STAT
    c04_cox2 = sum(1 for m in memories if "COX-2" in m.get("tags", []))
    c04_jak = sum(1 for m in memories if "JAK-STAT" in m.get("tags", []))
    if c04_cox2 <= c04_jak:
        warn(f"C04 trap weakened: COX-2 ({c04_cox2}) should outnumber JAK-STAT ({c04_jak})")
    else:
        print(f"  C04: COX-2 ({c04_cox2}) > JAK-STAT ({c04_jak}) — disproven-majority trap intact")

    # ── 14. Answer-key leakage check ──────────────────────────────────
    print("\n[14] Answer-key leakage check...")
    leakage_patterns = [
        "must not revert", "should not affect", "not independent",
        "must be retained", "should be deleted", "is retracted",
        "is superseded", "is disproven", "must not be retrievable",
    ]
    leaky = 0
    for m in memories:
        txt_lower = m["text"].lower()
        for pat in leakage_patterns:
            if pat in txt_lower:
                leaky += 1
                warn(f"{m['memory_id']}: text contains evaluative phrase '{pat}'")
                break
    if leaky == 0:
        print("  No answer-key language detected in memory texts.")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"ERRORS:   {len(errors)}")
    print(f"WARNINGS: {len(warnings)}")
    if errors:
        print("\nERROR DETAILS:")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print("\nWARNING DETAILS:")
        for w in warnings:
            print(f"  - {w}")

    ok = len(errors) == 0
    print(f"\nVERDICT: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check_exp11.py <experiment_dir>")
        sys.exit(1)
    ok = check(sys.argv[1])
    sys.exit(0 if ok else 1)
