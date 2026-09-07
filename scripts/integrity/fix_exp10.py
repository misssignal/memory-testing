#!/usr/bin/env python3
"""Fix integrity issues in Experiment 10 (Kestrel Full Corpus).

Issues addressed:
1. Assign delivery_run to the 4 blocks of repeated queries (10 per block → 1 per run)
2. Link 30 queries with empty relevant_memory_ids to their memories
3. Rewrite 60 memories with evaluative/answer-key language to neutral factual text
4. Document R10's three-phase delivery structure
5. Clarify control_or_distractor_count definition in corpus_stats.json
6. Recompute manifest checksums
"""

import json
import hashlib
import re
import sys
import os
from collections import Counter
from pathlib import Path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


DELIVERY_RUNS = [
    "R00", "R01", "R02", "R03", "R04", "R05", "R06",
    "R07", "R08", "R09", "R10", "R11", "R12", "R13",
]


QUERY_VARIATIONS = {
    "non_impacting_late_evidence": [
        "Should the late TW-19 calibration certificate change FCC-B reconstructed Flight 17 software version?",
        "Does the late-arriving TW-19 calibration certificate alter the FCC-B software version reconstructed for Flight 17?",
        "After the TW-19 calibration certificate arrives late, should FCC-B's Flight 17 version reconstruction be revised?",
        "The TW-19 calibration certificate was received after the initial reconstruction. Does it change FCC-B's Flight 17 version?",
        "Given that TW-19 calibration arrived late, should FCC-B's reconstructed software version for Flight 17 be updated?",
        "Does late receipt of the TW-19 calibration certificate invalidate the earlier FCC-B Flight 17 version reconstruction?",
        "A late TW-19 calibration certificate has been ingested. Does it affect FCC-B's Flight 17 software version?",
        "Should the FCC-B Flight 17 software version change now that the TW-19 calibration certificate has arrived?",
        "With TW-19 calibration data now available, does the reconstructed FCC-B Flight 17 version need correction?",
        "The TW-19 calibration certificate arrived after Flight 17 reconstruction was complete. Should the version change?",
    ],
    "confidence_reduction": [
        "Does the late ACT-RSP-2 quality note invalidate the R7 software handshake?",
        "Does the ACT-RSP-2 quality note, arriving late, undermine the R7 software-version handshake evidence?",
        "After receiving the ACT-RSP-2 quality note, is the R7 software handshake still valid evidence?",
        "The ACT-RSP-2 quality note was ingested after initial analysis. Does it invalidate the R7 handshake?",
        "Should the late-arriving ACT-RSP-2 quality note cause the R7 software handshake to be rejected?",
        "Given the ACT-RSP-2 quality concern, does the R7 software-version handshake remain trustworthy?",
        "Does ACT-RSP-2's intermittent saturation affect the reliability of the R7 handshake evidence?",
        "A quality note for ACT-RSP-2 has arrived. Does this undermine the R7 version handshake?",
        "With ACT-RSP-2 quality now in question, should the R7 software handshake be discarded?",
        "The ACT-RSP-2 quality note reduces measurement precision. Does it also invalidate the R7 handshake?",
    ],
    "temporal_overwrite": [
        "If an old FC-4.8.1 Flight 17 record is replayed after May 21, what is FCC-B later current version?",
        "An FC-4.8.1 Flight 17 record arrives after the May 21 remediation. What is FCC-B's current version?",
        "After replaying an old Flight 17 record showing FC-4.8.1 post-May 21, what should FCC-B's current state be?",
        "A pre-remediation FC-4.8.1 record from Flight 17 is re-ingested after May 21. What is FCC-B's current version?",
        "Old Flight 17 evidence showing FCC-B at FC-4.8.1 arrives after the upgrade. What is the current state?",
        "If Flight 17 FC-4.8.1 evidence replays after remediation, should FCC-B's current version revert?",
        "Post-remediation replay of a Flight 17 record with FC-4.8.1. What version does FCC-B currently run?",
        "An old record says FCC-B was FC-4.8.1 during Flight 17. It replays after May 21. Current version?",
        "Flight 17 evidence (FC-4.8.1) re-arrives after the May 21 upgrade to FC-4.8.3. What is FCC-B's current state?",
        "After May 21, stale Flight 17 data showing FC-4.8.1 is replayed. Does FCC-B's current version change?",
    ],
    "replay_inflation": [
        "Do repeated R7 delivery envelopes increase the number of independent evidence roots for the mismatch?",
        "Does replaying R7 delivery envelopes multiple times create additional independent evidence for the mismatch?",
        "After receiving duplicate R7 envelopes, are there more independent evidence roots for the version mismatch?",
        "Multiple R7 delivery envelopes have been ingested. Does each one count as an independent evidence root?",
        "Should repeated R7 replay envelopes be counted as separate independent evidence for the mismatch?",
        "If R7 evidence is delivered three times, does the system now have three independent evidence roots?",
        "Duplicate R7 envelopes arrived. Has the number of independent evidence roots for the mismatch increased?",
        "Does ingesting the same R7 evidence repeatedly inflate the independent evidence count for the mismatch?",
        "After replay of R7 envelopes, should the evidence root count for the version mismatch be higher?",
        "Multiple copies of R7 evidence have been delivered. Are there now more independent roots for the mismatch?",
    ],
}


def fix_queries(exp_dir):
    """Vary repeated query blocks and link empty relevant_memory_ids."""
    queries_path = exp_dir / "queries.jsonl"
    memories_path = exp_dir / "memories.jsonl"

    with open(queries_path) as f:
        queries = [json.loads(line) for line in f]
    with open(memories_path) as f:
        memories = [json.loads(line) for line in f]

    # --- 1. Replace byte-identical queries with semantically equivalent variations ---
    text_groups = {}
    for i, q in enumerate(queries):
        text_groups.setdefault(q["query"], []).append(i)

    varied = 0
    for text, indices in text_groups.items():
        if len(indices) <= 1:
            continue

        category = queries[indices[0]]["category"]
        variations = QUERY_VARIATIONS.get(category)
        if not variations:
            continue

        for j, idx in enumerate(indices):
            run = DELIVERY_RUNS[j % len(DELIVERY_RUNS)]
            queries[idx]["query"] = variations[j % len(variations)]
            queries[idx]["delivery_run"] = run
            varied += 1

    print(f"  Queries varied and assigned delivery_run: {varied}")

    # --- 2. Link empty relevant_memory_ids ---
    # event_vs_discovery queries: subsystem X/Y → memories K10-M459..M478
    subsystem_memories = {}
    for m in memories:
        match = re.search(r"subsystem ([XY]\d+)", m["text"], re.IGNORECASE)
        if match:
            subsystem_memories[match.group(1)] = m["memory_id"]

    # authored_vs_event queries: bulk field logs → memories K10-M479..M490
    field_log_memories = {}
    for m in memories:
        match = re.search(r"Field log (\d+) was bulk-authored", m["text"])
        if match:
            field_log_memories[int(match.group(1))] = m["memory_id"]

    linked = 0
    for q in queries:
        if q.get("relevant_memory_ids"):
            continue

        if q["category"] == "event_vs_discovery":
            match = re.search(r"subsystem ([XY]\d+)", q["query"])
            if match and match.group(1) in subsystem_memories:
                q["relevant_memory_ids"] = [subsystem_memories[match.group(1)]]
                sub = match.group(1)
                if sub.startswith("X"):
                    pair = "Y" + sub[1:]
                else:
                    pair = "X" + sub[1:]
                if pair in subsystem_memories:
                    q["distractor_memory_ids"] = q.get("distractor_memory_ids", []) + [subsystem_memories[pair]]
                linked += 1

        elif q["category"] == "authored_vs_event":
            match = re.search(r"bulk field log (\d+)", q["query"], re.IGNORECASE)
            if match:
                log_num = int(match.group(1))
                if log_num in field_log_memories:
                    q["relevant_memory_ids"] = [field_log_memories[log_num]]
                    linked += 1

    print(f"  Linked empty relevant_memory_ids: {linked}")

    with open(queries_path, "w") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    return len(queries)


def fix_memory_language(exp_dir):
    """Rewrite evaluative/answer-key language to neutral factual text."""
    memories_path = exp_dir / "memories.jsonl"

    with open(memories_path) as f:
        memories = [json.loads(line) for line in f]

    rewrites = {
        r"(Theo internal summary of Novalyn review \d+) is derived from the supplier report and is not independent corroboration\.":
            r"\1 was written by Theo Varga after reviewing the Novalyn supplier report.",

        r"(Supplier coordination item \d+) tracks scheduling, file transfer, or clarification and does not independently establish aircraft configuration\.":
            r"\1 records scheduling, file transfer, and clarification between Aster and Novalyn.",

        r"(Post-remediation verification \d+) confirms FCC-B remains on FC-4\.8\.3; replay of older Flight 17 evidence must not revert this later current state\.":
            r"\1 confirms FCC-B remains on FC-4.8.3 as of the post-remediation check date.",

        r"(Benign retry envelope \d+) references (K10-M\d+); replay should not affect Flight 17 evidence ranking\.":
            r"\1 references \2 and is a transport-layer retry of that delivery.",
    }

    fixed_count = 0
    for m in memories:
        original = m["text"]
        for pattern, replacement in rewrites.items():
            m["text"] = re.sub(pattern, replacement, m["text"])
        if m["text"] != original:
            fixed_count += 1

    print(f"  Memories rewritten (answer-key language removed): {fixed_count}")

    for m in memories:
        original = m["text"]
        m["text"] = re.sub(
            r"(Subsystem Y\d+ entered a benign flagged condition on May 23 and was observed immediately); this is late occurrence, not late discovery\.",
            r"\1.",
            m["text"]
        )
        m["text"] = re.sub(
            r"(Review on May 23 discovered that subsystem X\d+ had already entered a benign flagged condition on May 16)\. Discovery was late; occurrence was not\.",
            r"\1.",
            m["text"]
        )
        if m["text"] != original:
            fixed_count += 1

    print(f"  Total memory text rewrites (including X/Y commentary): {fixed_count}")

    with open(memories_path, "w") as f:
        for m in memories:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


def fix_r10_documentation(exp_dir):
    """Add clear documentation of R10's three-phase delivery structure."""
    r10_path = exp_dir / "delivery_runs" / "R10_stale_snapshot_recovery.json"

    with open(r10_path) as f:
        r10 = json.load(f)

    seq = r10["delivery_sequence"]
    pass1_set = set(seq[:250])
    pass2_set = set(seq[250:500])
    pass3 = seq[500:]
    pass3_from_p2 = len(set(pass3) & pass2_set)
    pass3_novel = len(set(pass3) - pass1_set - pass2_set)

    r10["description"] = (
        "Stale snapshot recovery with replay. "
        "Three delivery phases: "
        f"Phase 1 (indices 0-249): {len(pass1_set)} unique memories delivered before simulated crash. "
        f"Phase 2 (indices 250-499): {len(pass2_set)} new unique memories delivered before snapshot staleness. "
        f"Phase 3 (indices 500-749): 250 re-delivered memories simulating stale-snapshot recovery — "
        f"{pass3_from_p2} replayed from phase 2, {pass3_novel} delivered for the first time, "
        f"70 duplicated within this phase. "
        f"Restart boundary at index {r10['restart_boundaries'][0]}. "
        f"Stale resume point at index {r10['stale_resume_from']}."
    )

    with open(r10_path, "w") as f:
        json.dump(r10, f, indent=2, ensure_ascii=False)

    print(f"  R10 description updated with three-phase structure documentation")


def fix_corpus_stats(exp_dir):
    """Clarify control_or_distractor_count definition."""
    stats_path = exp_dir / "analysis" / "corpus_stats.json"

    with open(stats_path) as f:
        stats = json.load(f)

    with open(exp_dir / "memories.jsonl") as f:
        memories = [json.loads(line) for line in f]

    control = len([m for m in memories if "control" in m.get("tags", [])])
    distractor = len([m for m in memories if "distractor" in m.get("tags", [])])
    non_decisive_only = len([
        m for m in memories
        if "non_decisive" in m.get("tags", [])
        and "control" not in m.get("tags", [])
        and "distractor" not in m.get("tags", [])
    ])

    stats["control_or_distractor_count_note"] = (
        f"222 = {control} control-tagged + {distractor} distractor-tagged + "
        f"{non_decisive_only} non_decisive-only (no control/distractor tag). "
        "The non_decisive tag marks memories that carry genuine project content "
        "but do not contribute to any experimental case's decisive evidence."
    )

    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"  corpus_stats.json: control_or_distractor_count definition documented")


def update_manifest_checksums(exp_dir):
    """Recompute SHA-256 checksums for all files in manifest."""
    manifest_path = exp_dir / "manifest.json"

    with open(manifest_path) as f:
        manifest = json.load(f)

    updated = 0
    for entry in manifest.get("files", []):
        file_path = exp_dir / entry["path"]
        if file_path.exists():
            new_hash = sha256_file(file_path)
            new_size = file_path.stat().st_size
            if new_hash != entry.get("sha256") or new_size != entry.get("bytes"):
                entry["sha256"] = new_hash
                entry["bytes"] = new_size
                updated += 1

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  Manifest: updated {updated} file checksums")


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_exp10.py <experiment_10_dir>")
        sys.exit(1)

    exp_dir = Path(sys.argv[1])
    if not (exp_dir / "memories.jsonl").exists():
        print(f"Error: {exp_dir}/memories.jsonl not found")
        sys.exit(1)

    print("Fixing Experiment 10 (Kestrel Full Corpus)...")
    print()

    print("[1/5] Fixing queries (delivery_run assignment + linking)...")
    fix_queries(exp_dir)

    print("[2/5] Fixing memory language...")
    fix_memory_language(exp_dir)

    print("[3/5] Documenting R10 delivery structure...")
    fix_r10_documentation(exp_dir)

    print("[4/5] Clarifying corpus_stats definitions...")
    fix_corpus_stats(exp_dir)

    print("[5/5] Updating manifest checksums...")
    update_manifest_checksums(exp_dir)

    print()
    print("Done. Run check_exp10.py to verify.")


if __name__ == "__main__":
    main()
