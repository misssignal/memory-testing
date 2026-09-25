#!/usr/bin/env python3
"""Integrity checker for Experiment 12: Privacy Boundaries / Namespace Isolation."""

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
        err(f"{len(dupes)} duplicate texts: {dupes[0][0]}... (x{dupes[0][1]})")

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
        err("Duplicate query IDs")

    bad_qrefs = 0
    for q in queries:
        for rid in q.get("relevant_memory_ids", []):
            if rid not in id_set:
                bad_qrefs += 1
                err(f"{q['query_id']} relevant -> {rid} (not found)")
        for rid in q.get("distractor_memory_ids", []):
            if rid not in id_set:
                bad_qrefs += 1
                err(f"{q['query_id']} distractor -> {rid} (not found)")
    if bad_qrefs == 0:
        print("  All query references resolve.")

    if manifest.get("query_count") != len(queries):
        err(f"Manifest query count ({manifest.get('query_count')}) != actual ({len(queries)})")

    # ── 7. Scope field coverage ───────────────────────────────────────
    print("\n[7] Scope field coverage...")
    no_scope = 0
    tenant_counts = Counter()
    level_counts = Counter()
    for m in memories:
        scope = m.get("scope")
        if not scope:
            no_scope += 1
            err(f"{m['memory_id']}: missing scope field")
            continue
        tenant_counts[scope.get("tenant", "MISSING")] += 1
        level_counts[scope.get("access_level", "MISSING")] += 1

    expected_tenants = {"T-PR", "T-VB", "T-HE", "T-CL", "shared"}
    present_tenants = set(tenant_counts.keys())
    missing_tenants = expected_tenants - present_tenants
    if missing_tenants:
        err(f"Missing tenants: {missing_tenants}")

    expected_levels = {"facility_admin", "tenant_admin", "member", "guest"}
    present_levels = set(level_counts.keys())
    missing_levels = expected_levels - present_levels
    if missing_levels:
        err(f"Missing access levels: {missing_levels}")

    for t, c in sorted(tenant_counts.items()):
        print(f"  Tenant {t}: {c}")
    for l, c in sorted(level_counts.items()):
        print(f"  Level {l}: {c}")

    # ── 8. Case coverage ──────────────────────────────────────────────
    print("\n[8] Case coverage...")
    case_counts = Counter()
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0") and len(t) == 3:
                case_counts[t] += 1

    expected_cases = {"C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"}
    present_cases = set(case_counts.keys())
    missing_cases = expected_cases - present_cases
    if missing_cases:
        err(f"Missing cases: {missing_cases}")

    for case, count in sorted(case_counts.items()):
        print(f"  {case}: {count} memories")

    bg_count = sum(1 for m in memories if "background" in m.get("tags", []))
    print(f"  Background: {bg_count} memories")

    min_per_case = 6
    for case in expected_cases:
        if case_counts.get(case, 0) < min_per_case:
            warn(f"{case} has only {case_counts.get(case, 0)} memories (minimum {min_per_case})")

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
    if "cases" not in truth:
        err("truth_state.json missing cases")
    else:
        truth_cases = set(truth["cases"].keys())
        if truth_cases != expected_cases:
            err(f"Truth cases mismatch: {truth_cases} vs {expected_cases}")

    if "namespace_rules" not in truth:
        warn("truth_state.json missing namespace_rules")

    # ── 11. Memory schema completeness ────────────────────────────────
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

    # ── 12. Query schema completeness ─────────────────────────────────
    print("\n[12] Query schema completeness...")
    required_q_fields = [
        "query_id", "query", "category", "expected_claims",
        "relevant_memory_ids", "forbidden_claims", "query_context",
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

    # ── 13. Query context validation ──────────────────────────────────
    print("\n[13] Query context validation...")
    ctx_issues = 0
    ctx_tenants = Counter()
    ctx_levels = Counter()
    for q in queries:
        ctx = q.get("query_context", {})
        if "tenant" not in ctx:
            ctx_issues += 1
            err(f"{q['query_id']}: query_context missing tenant")
        else:
            ctx_tenants[ctx["tenant"]] += 1
        if "access_level" not in ctx:
            ctx_issues += 1
            err(f"{q['query_id']}: query_context missing access_level")
        else:
            ctx_levels[ctx["access_level"]] += 1

    if ctx_issues == 0:
        print("  All queries have valid query_context.")

    print("  Query context tenant distribution:")
    for t in sorted(ctx_tenants):
        print(f"    {t}: {ctx_tenants[t]}")
    print("  Query context access level distribution:")
    for l in sorted(ctx_levels):
        print(f"    {l}: {ctx_levels[l]}")

    # ── 14. Adversarial trap validation ───────────────────────────────
    print("\n[14] Adversarial trap validation...")

    # C02: Both tenants should have Phoenix memories
    prism_phoenix = sum(1 for m in memories
                        if m.get("scope", {}).get("tenant") == "T-PR"
                        and "Phoenix" in m.get("tags", []))
    helios_phoenix = sum(1 for m in memories
                         if m.get("scope", {}).get("tenant") == "T-HE"
                         and "Phoenix" in m.get("tags", []))
    if prism_phoenix == 0:
        err("C02 trap broken: no Prism Phoenix memories")
    if helios_phoenix == 0:
        err("C02 trap broken: no Helios Phoenix memories")
    print(f"  C02: Prism Phoenix ({prism_phoenix}) vs Helios Phoenix ({helios_phoenix}) — alias collision trap")

    # C03: Should have both member-visible and admin-only budget memories
    admin_budget = sum(1 for m in memories if "admin_only" in m.get("tags", []))
    member_budget = sum(1 for m in memories if "member_visible" in m.get("tags", []))
    print(f"  C03: admin-only ({admin_budget}) vs member-visible ({member_budget}) — access level trap")

    # C04: Jordan Kim memories should span both tenants
    jordan_prism = sum(1 for m in memories
                       if "Jordan_Kim" in m.get("tags", [])
                       and m.get("scope", {}).get("tenant") == "T-PR")
    jordan_cirrus = sum(1 for m in memories
                        if "Jordan_Kim" in m.get("tags", [])
                        and m.get("scope", {}).get("tenant") == "T-CL")
    jordan_shared = sum(1 for m in memories
                        if "Jordan_Kim" in m.get("tags", [])
                        and m.get("scope", {}).get("tenant") == "shared")
    print(f"  C04: Jordan@Prism ({jordan_prism}), Jordan@Cirrus ({jordan_cirrus}), "
          f"Jordan@shared ({jordan_shared}) — revocation trap")

    # C06: AgroViz memories should be shared between T-PR and T-VB only
    agroviz_mems = [m for m in memories if "AgroViz" in m.get("tags", [])]
    agroviz_wrong_tenant = [m for m in agroviz_mems
                            if m.get("scope", {}).get("tenant") in ("T-HE", "T-CL")
                            and "T-PR" not in m.get("scope", {}).get("shared_with", [])
                            and "T-VB" not in m.get("scope", {}).get("shared_with", [])]
    if agroviz_wrong_tenant:
        err(f"C06 trap broken: AgroViz memories accessible to wrong tenants")
    print(f"  C06: {len(agroviz_mems)} AgroViz memories, {len(agroviz_wrong_tenant)} wrongly scoped")

    # C05/C08: Should have both public summaries and private source data
    newsletter_public = sum(1 for m in memories
                            if "published" in m.get("tags", [])
                            and m.get("scope", {}).get("access_level") == "guest")
    newsletter_private = sum(1 for m in memories
                             if ("redaction" in m.get("tags", [])
                                 or "editorial" in m.get("tags", []))
                             and m.get("scope", {}).get("access_level") != "guest")
    print(f"  C05: public summaries ({newsletter_public}) vs private editorial ({newsletter_private}) — leakage trap")

    # ── 15. Answer-key leakage check ──────────────────────────────────
    print("\n[15] Answer-key leakage check...")
    leakage_patterns = [
        "should not be visible", "must not access", "privacy boundary",
        "should be blocked", "must not surface", "access denied",
        "forbidden to", "must not leak", "scope violation",
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

    # ── 16. Same-query-different-context pairs ────────────────────────
    print("\n[16] Same-query-different-context pairs...")
    query_texts = Counter(q["query"] for q in queries)
    paired = {t: c for t, c in query_texts.items() if c > 1}
    print(f"  {len(paired)} queries appear with multiple contexts:")
    for qt, count in sorted(paired.items(), key=lambda x: -x[1]):
        contexts = [q.get("query_context", {}).get("tenant", "?")
                    for q in queries if q["query"] == qt]
        print(f"    '{qt[:60]}...' x{count} contexts: {contexts}")

    if len(paired) < 3:
        warn(f"Only {len(paired)} query pairs with different contexts — expected at least 3 for robustness")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
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
        print("Usage: check_exp12.py <experiment_dir>")
        sys.exit(1)
    ok = check(sys.argv[1])
    sys.exit(0 if ok else 1)
