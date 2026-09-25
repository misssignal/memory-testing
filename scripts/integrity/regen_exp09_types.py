#!/usr/bin/env python3
"""Regenerate Exp09 case memories so each variant's text matches its memory_type.

Problem: The original generator assigned memory_type round-robin, so the same
base sentence appears as a test_log, meeting_note, experiment_result, etc. with
identical (or suffix-only-different) text. A provenance-aware system can't
distinguish types because the text carries no type signal.

Fix: For each multi-variant group, keep the first occurrence's text as-is.
Rewrite each subsequent variant in the voice/register of its memory_type,
preserving the factual content. Also adjust voice for belief_holder where set.
"""

import json
import re
import hashlib
import sys
from collections import defaultdict
from pathlib import Path


# --- Type voice templates ---
# Each type gets a transformation that reformats a factual statement
# into the register appropriate for that document type.

TYPE_TEMPLATES = {
    "test_log": [
        "TEST {seq}: {fact} [status: observed]",
        "Run {seq} — {fact} Result logged.",
        "Test observation #{seq}: {fact}",
        "[T-{seq}] {fact} — logged during test execution.",
    ],
    "meeting_note": [
        "Meeting item: team discussed that {fact_lower}",
        "Action item from standup: {fact_lower} — follow-up assigned.",
        "Minutes: {fact} Discussion noted for record.",
        "Review meeting: {fact_lower} Consensus to investigate further.",
    ],
    "engineering_note": [
        "Eng note: {fact_lower} See attached trace.",
        "Engineering assessment: {fact}",
        "Technical note — {fact_lower} Requires root-cause analysis.",
        "Design review note: {fact_lower}",
    ],
    "chat_message": [
        "hey, fyi — {fact_lower}",
        "quick update: {fact_lower}",
        "heads up — {fact_lower} thoughts?",
        "just noticed: {fact_lower} lmk if you've seen this before",
    ],
    "issue_comment": [
        "Update on this issue: {fact_lower}",
        "Adding context — {fact_lower}",
        "Observed during triage: {fact_lower}",
        "Comment: {fact} Linking to related ticket.",
    ],
    "experiment_result": [
        "Experiment result: {fact}",
        "Trial outcome — {fact_lower}",
        "Controlled test shows: {fact_lower}",
        "Result: {fact} Conditions documented in lab notebook.",
    ],
    "telemetry_summary": [
        "TELEMETRY: {fact} [automated summary]",
        "System telemetry indicates: {fact_lower}",
        "Telemetry digest: {fact_lower} Period: test window.",
        "Auto-generated: {fact_lower} Source: onboard telemetry.",
    ],
    "postmortem_draft": [
        "Postmortem finding: {fact}",
        "Root-cause analysis draft: {fact_lower}",
        "Incident review notes: {fact_lower} Contributing factors under investigation.",
        "Draft postmortem — {fact_lower} Timeline section.",
    ],
    "release_note": [
        "Release note: {fact}",
        "Known behavior in this build: {fact_lower}",
        "Changelog entry: {fact_lower}",
        "v{seq} release observation: {fact_lower}",
    ],
    "lab_notebook": [
        "Lab entry: {fact_lower} Bench setup as documented.",
        "Notebook #{seq}: {fact}",
        "Lab observation — {fact_lower} Conditions: standard test rig.",
        "Recorded in lab notebook: {fact_lower}",
    ],
}

# --- Belief-holder voice adjustments ---
# When a memory has a belief_holder, prepend a short attribution.
HOLDER_PREFIXES = {
    "P01": "{holder} (lead engineer) notes: ",
    "P02": "{holder} (systems analyst) reports: ",
    "P03": "{holder} (test engineer) observes: ",
    "P04": "{holder} (integration lead) states: ",
    "P05": "{holder} (field engineer) flags: ",
    "P06": "{holder} (program manager) summarizes: ",
    "P07": "{holder} (safety reviewer) records: ",
}


def strip_suffix(text):
    suffixes = [
        "The note distinguishes observation from explanation.",
        "This is a measurement, not an interpretation.",
        "The analyst flagged this for follow-up.",
        "Included for completeness; relevance TBD.",
    ]
    result = text
    for s in suffixes:
        result = result.replace(s, "").strip()
    return result


def fact_lower(text):
    """Lowercase first char for embedding in a sentence, unless it's an acronym."""
    if not text:
        return text
    if text[0].isupper() and (len(text) < 2 or not text[1].isupper()):
        return text[0].lower() + text[1:]
    return text


def stable_hash(text, memory_id):
    """Deterministic index from text + id for template selection."""
    h = hashlib.md5((text + memory_id).encode()).hexdigest()
    return int(h, 16)


def rewrite_text(base_text, memory_type, memory_id, belief_holder=None, seq=1):
    """Rewrite base_text in the voice of memory_type."""
    templates = TYPE_TEMPLATES.get(memory_type)
    if not templates:
        return base_text

    idx = stable_hash(base_text, memory_id) % len(templates)
    template = templates[idx]

    result = template.format(
        fact=base_text.rstrip(".") + "." if not base_text.endswith(".") else base_text,
        fact_lower=fact_lower(base_text.rstrip(".") + "." if not base_text.endswith(".") else base_text),
        seq=seq,
        holder=belief_holder or "team",
    )

    if belief_holder and belief_holder in HOLDER_PREFIXES:
        prefix = HOLDER_PREFIXES[belief_holder].format(holder=belief_holder)
        # For chat_message, the prefix replaces the informal opener
        if memory_type == "chat_message":
            result = re.sub(r"^(hey, fyi|quick update|heads up|just noticed)[^—]*— ", prefix, result)
        else:
            result = prefix + result[0].lower() + result[1:] if result[0].isupper() else prefix + result

    return result


def regenerate(exp_dir):
    memories_path = exp_dir / "memories.jsonl"

    with open(memories_path) as f:
        memories = [json.loads(line) for line in f]

    case_memories = [m for m in memories if "background" not in m.get("tags", [])]

    # Group by base text
    base_groups = defaultdict(list)
    for m in case_memories:
        base = strip_suffix(m["text"])
        base_groups[base].append(m)

    # Track what we rewrite
    rewritten = 0
    type_counts = defaultdict(int)

    # Build a memory_id -> memory index for fast lookup
    id_to_idx = {m["memory_id"]: i for i, m in enumerate(memories)}

    for base, group in base_groups.items():
        if len(group) <= 1:
            continue

        # First occurrence keeps its text
        for seq, m in enumerate(group[1:], start=2):
            idx = id_to_idx[m["memory_id"]]
            new_text = rewrite_text(
                base,
                m["memory_type"],
                m["memory_id"],
                belief_holder=m.get("belief_holder"),
                seq=seq,
            )
            if new_text != memories[idx]["text"]:
                memories[idx]["text"] = new_text
                rewritten += 1
                type_counts[m["memory_type"]] += 1

    print(f"  Memories rewritten with type-appropriate text: {rewritten}")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {t}: {c}")

    # Verify no exact duplicates were introduced
    texts = [m["text"] for m in memories]
    dupes = len(texts) - len(set(texts))
    if dupes > 0:
        print(f"  WARNING: {dupes} duplicate texts after rewrite")
        # Find and fix duplicates by appending memory_id
        seen = set()
        fixed = 0
        for m in memories:
            if m["text"] in seen:
                m["text"] = m["text"].rstrip(".") + f" [{m['memory_id']}]."
                fixed += 1
            seen.add(m["text"])
        print(f"  Fixed {fixed} duplicates by appending memory_id")
    else:
        print(f"  No duplicate texts introduced.")

    with open(memories_path, "w") as f:
        for m in memories:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    return rewritten


def update_checksums(exp_dir):
    """Recompute SHA-256 checksums in manifest."""
    manifest_path = exp_dir / "manifest.json"

    with open(manifest_path) as f:
        manifest = json.load(f)

    updated = 0
    for entry in manifest.get("files", []):
        file_path = exp_dir / entry["path"]
        if file_path.exists():
            h = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            new_hash = h.hexdigest()
            new_size = file_path.stat().st_size
            if new_hash != entry.get("sha256") or new_size != entry.get("bytes"):
                entry["sha256"] = new_hash
                entry["bytes"] = new_size
                updated += 1

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  Manifest: updated {updated} file checksums")


def verify(exp_dir):
    """Post-rewrite verification."""
    with open(exp_dir / "memories.jsonl") as f:
        memories = [json.loads(line) for line in f]

    case = [m for m in memories if "background" not in m.get("tags", [])]

    base_groups = defaultdict(list)
    for m in case:
        base = strip_suffix(m["text"])
        base_groups[base].append(m)

    # Check: how many base texts still appear under multiple types with same text?
    same_text_diff_type = 0
    for base, group in base_groups.items():
        if len(group) <= 1:
            continue
        texts = [m["text"] for m in group]
        types = [m["memory_type"] for m in group]
        if len(set(texts)) < len(set(types)):
            same_text_diff_type += 1

    print(f"\n  Verification:")
    print(f"    Multi-variant groups with identical text across types: {same_text_diff_type}")

    # Check: all texts still unique across entire corpus?
    all_texts = [m["text"] for m in memories]
    dupes = len(all_texts) - len(set(all_texts))
    print(f"    Duplicate texts in full corpus: {dupes}")

    # Check: type distribution still balanced?
    from collections import Counter
    type_dist = Counter(m["memory_type"] for m in case)
    print(f"    Case memory type distribution: {dict(sorted(type_dist.items()))}")


def main():
    if len(sys.argv) < 2:
        print("Usage: regen_exp09_types.py <experiment_09_dir>")
        sys.exit(1)

    exp_dir = Path(sys.argv[1])
    if not (exp_dir / "memories.jsonl").exists():
        print(f"Error: {exp_dir}/memories.jsonl not found")
        sys.exit(1)

    print("Regenerating Exp09 case memories with type-appropriate text...")
    print()

    print("[1/3] Rewriting variant memories...")
    rewritten = regenerate(exp_dir)

    print("\n[2/3] Updating manifest checksums...")
    update_checksums(exp_dir)

    print("\n[3/3] Verifying...")
    verify(exp_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
