#!/usr/bin/env python3
"""Suite-wide integrity checker for all 20 adversarial memory benchmark experiments.

Validates:
  - Schema compliance (24-key memories, 15-key queries)
  - ID format and uniqueness
  - Timestamp validity (ISO 8601) and temporal ordering
  - Cross-reference integrity (derived_from, supersedes, contradicts, duplicates)
  - Query reference integrity (relevant_memory_ids, distractor_memory_ids)
  - Corpus size thresholds (200+ memories, 75+ queries)
  - Extension alignment (extensions.jsonl covers all memories)
  - Manifest checksum verification
"""

import json, os, sys, hashlib
from datetime import datetime
from collections import Counter
from pathlib import Path

NORMALIZED = Path(__file__).resolve().parent.parent / "normalized"

MEMORY_KEYS = {
    "memory_id", "experiment", "story_id",
    "event_time", "observation_time", "authored_time", "ingestion_time",
    "subject", "predicate", "object", "text",
    "memory_type", "truth_role", "belief_holder", "confidence",
    "source_id", "source_type",
    "derived_from", "supersedes", "contradicts", "duplicates",
    "aliases", "scope", "tags",
}

QUERY_KEYS = {
    "query_id", "query", "category",
    "expected_claims", "acceptable_claims", "forbidden_claims",
    "relevant_memory_ids", "distractor_memory_ids",
    "difficulty", "must_surface_uncertainty", "must_surface_conflict",
    "must_disambiguate", "must_preserve_scope", "should_abstain", "notes",
}

MIN_MEMORIES = 200
MIN_QUERIES = 75

CROSS_REF_FIELDS = ["derived_from", "supersedes", "contradicts", "duplicates"]
QUERY_REF_FIELDS = ["relevant_memory_ids", "distractor_memory_ids"]


def parse_iso(ts):
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        datetime.fromisoformat(ts)
        return True
    except (ValueError, AttributeError):
        return False


def check_experiment(exp_dir):
    name = exp_dir.name
    errors = []
    warnings = []

    mem_path = exp_dir / "memories.jsonl"
    query_path = exp_dir / "queries.jsonl"

    if not mem_path.exists():
        errors.append("memories.jsonl missing")
        return name, errors, warnings
    if not query_path.exists():
        errors.append("queries.jsonl missing")
        return name, errors, warnings

    # Load memories
    mems = []
    for i, line in enumerate(open(mem_path), 1):
        try:
            mems.append(json.loads(line))
        except json.JSONDecodeError:
            errors.append(f"memories.jsonl line {i}: invalid JSON")

    # Load queries
    qs = []
    for i, line in enumerate(open(query_path), 1):
        try:
            qs.append(json.loads(line))
        except json.JSONDecodeError:
            errors.append(f"queries.jsonl line {i}: invalid JSON")

    # --- Corpus size ---
    if len(mems) < MIN_MEMORIES:
        errors.append(f"Only {len(mems)} memories (need {MIN_MEMORIES}+)")
    if len(qs) < MIN_QUERIES:
        errors.append(f"Only {len(qs)} queries (need {MIN_QUERIES}+)")

    # --- Memory schema ---
    mem_ids = set()
    for m in mems:
        keys = set(m.keys())
        missing = MEMORY_KEYS - keys
        extra = keys - MEMORY_KEYS
        if missing:
            errors.append(f"{m.get('memory_id', '?')}: missing keys {missing}")
        if extra:
            warnings.append(f"{m.get('memory_id', '?')}: extra keys {extra}")

        mid = m.get("memory_id", "")
        if mid in mem_ids:
            errors.append(f"Duplicate memory_id: {mid}")
        mem_ids.add(mid)

        # ID format
        exp_num = name.split("_")[1]
        prefix = f"E{exp_num}-"
        if not mid.startswith(prefix):
            warnings.append(f"{mid}: expected prefix {prefix}")

        # Timestamp validity
        for ts_field in ["event_time", "observation_time", "authored_time", "ingestion_time"]:
            val = m.get(ts_field, "")
            if val and not parse_iso(val):
                errors.append(f"{mid}: invalid {ts_field} = {val!r}")

        # Temporal ordering: event <= observation <= authored <= ingestion
        ts_vals = {}
        for ts_field in ["event_time", "observation_time", "authored_time", "ingestion_time"]:
            val = m.get(ts_field, "")
            if val and parse_iso(val):
                ts_vals[ts_field] = val

        ordering = ["event_time", "observation_time", "authored_time", "ingestion_time"]
        for i in range(len(ordering) - 1):
            a, b = ordering[i], ordering[i + 1]
            if a in ts_vals and b in ts_vals:
                if ts_vals[a] > ts_vals[b]:
                    warnings.append(f"{mid}: {a} ({ts_vals[a]}) > {b} ({ts_vals[b]})")

    # --- Cross-reference integrity ---
    for m in mems:
        mid = m.get("memory_id", "")
        for field in CROSS_REF_FIELDS:
            refs = m.get(field, [])
            if not isinstance(refs, list):
                errors.append(f"{mid}: {field} is not a list")
                continue
            for ref in refs:
                if ref not in mem_ids:
                    errors.append(f"{mid}: {field} references nonexistent {ref}")

    # --- Query schema ---
    q_ids = set()
    for q in qs:
        keys = set(q.keys())
        missing = QUERY_KEYS - keys
        extra = keys - QUERY_KEYS
        if missing:
            errors.append(f"{q.get('query_id', '?')}: missing keys {missing}")
        if extra:
            warnings.append(f"{q.get('query_id', '?')}: extra keys {extra}")

        qid = q.get("query_id", "")
        if qid in q_ids:
            errors.append(f"Duplicate query_id: {qid}")
        q_ids.add(qid)

    # --- Query reference integrity ---
    for q in qs:
        qid = q.get("query_id", "")
        for field in QUERY_REF_FIELDS:
            refs = q.get(field, [])
            if not isinstance(refs, list):
                errors.append(f"{qid}: {field} is not a list")
                continue
            for ref in refs:
                if ref and ref not in mem_ids:
                    warnings.append(f"{qid}: {field} references nonexistent memory {ref}")

    # --- Extensions alignment ---
    ext_path = exp_dir / "extensions.jsonl"
    if ext_path.exists():
        exts = [json.loads(l) for l in open(ext_path)]
        ext_ids = {e["memory_id"] for e in exts}
        missing_ext = mem_ids - ext_ids
        orphan_ext = ext_ids - mem_ids
        if missing_ext:
            warnings.append(f"extensions.jsonl missing {len(missing_ext)} memory IDs")
        if orphan_ext:
            errors.append(f"extensions.jsonl has {len(orphan_ext)} orphan IDs")

    # --- Query extensions alignment ---
    qext_path = exp_dir / "query_extensions.jsonl"
    if qext_path.exists():
        qexts = [json.loads(l) for l in open(qext_path)]
        qext_ids = {e["query_id"] for e in qexts if "query_id" in e}
        if qext_ids:
            missing_qext = q_ids - qext_ids
            orphan_qext = qext_ids - q_ids
            if missing_qext:
                warnings.append(f"query_extensions.jsonl missing {len(missing_qext)} query IDs")
            if orphan_qext:
                errors.append(f"query_extensions.jsonl has {len(orphan_qext)} orphan IDs")

    # --- Manifest checksum verification ---
    manifest_path = exp_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.load(open(manifest_path))
        for fentry in manifest.get("files", []):
            fpath = exp_dir / fentry["path"]
            if fentry["path"] == "manifest.json":
                continue
            if not fpath.exists():
                errors.append(f"manifest references missing file: {fentry['path']}")
                continue
            actual_size = fpath.stat().st_size
            if actual_size != fentry.get("bytes", actual_size):
                errors.append(f"{fentry['path']}: size mismatch (manifest={fentry['bytes']}, actual={actual_size})")
            actual_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            if actual_hash != fentry.get("sha256", actual_hash):
                errors.append(f"{fentry['path']}: SHA-256 mismatch")
    else:
        warnings.append("manifest.json missing")

    return name, errors, warnings, len(mems), len(qs), dict(Counter(m["truth_role"] for m in mems)), dict(Counter(q["category"] for q in qs))


def main():
    exp_dirs = sorted(NORMALIZED.glob("experiment_*"))
    if not exp_dirs:
        print(f"No experiments found in {NORMALIZED}")
        sys.exit(1)

    total_errors = 0
    total_warnings = 0
    summary = []

    print(f"Checking {len(exp_dirs)} experiments in {NORMALIZED}\n")
    print("=" * 80)

    for exp_dir in exp_dirs:
        result = check_experiment(exp_dir)
        name = result[0]
        errors = result[1]
        warnings = result[2]
        mem_count = result[3] if len(result) > 3 else 0
        q_count = result[4] if len(result) > 4 else 0
        roles = result[5] if len(result) > 5 else {}
        cats = result[6] if len(result) > 6 else {}

        status = "PASS" if not errors else "FAIL"
        total_errors += len(errors)
        total_warnings += len(warnings)

        summary.append({
            "name": name,
            "status": status,
            "memories": mem_count,
            "queries": q_count,
            "errors": len(errors),
            "warnings": len(warnings),
            "truth_roles": len(roles),
            "query_categories": len(cats),
        })

        icon = "PASS" if not errors else "FAIL"
        warn_str = f" ({len(warnings)} warnings)" if warnings else ""
        print(f"\n{icon}  {name} — {mem_count} memories, {q_count} queries{warn_str}")

        if errors:
            for e in errors[:10]:
                print(f"  ERROR: {e}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")

        if warnings and ("--verbose" in sys.argv or "-v" in sys.argv):
            for w in warnings[:10]:
                print(f"  WARN:  {w}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more warnings")

    print("\n" + "=" * 80)
    print(f"\nSuite summary: {len(exp_dirs)} experiments")
    print(f"  Passed: {sum(1 for s in summary if s['status'] == 'PASS')}")
    print(f"  Failed: {sum(1 for s in summary if s['status'] == 'FAIL')}")
    print(f"  Total errors: {total_errors}")
    print(f"  Total warnings: {total_warnings}")

    total_mems = sum(s["memories"] for s in summary)
    total_qs = sum(s["queries"] for s in summary)
    print(f"  Total memories: {total_mems}")
    print(f"  Total queries: {total_qs}")

    if "--json" in sys.argv:
        print("\n" + json.dumps(summary, indent=2))

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
