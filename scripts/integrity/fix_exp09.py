#!/usr/bin/env python3
"""Fix integrity issues in Experiment 09 (Causal Attribution / Helix Flight Controls).

Issues addressed:
1. Fill 5 empty causal_evidence entries by content-matching memories
2. Resolve 7 claims with overlapping supporting/contradicting memory IDs
3. Write per-case expected_claims for generic query answers
4. Populate relation fields (derived_from, contradicts) from content patterns
5. Add SHA-256 manifest checksums

6. Vary background memory texts to test recall-frequency tracking (same event,
   different phrasing/temporal context across occurrences)

NOT changed (intentional design):
- Suffix cycling on case memories (tests whether systems conflate similar-but-distinct records)
"""

import json
import hashlib
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def fill_empty_evidence(exp_dir):
    """Fill empty causal_evidence entries by matching memory content to claim causes/effects."""
    with open(exp_dir / "causal_evidence.json") as f:
        evidence = json.load(f)
    with open(exp_dir / "causal_claims.json") as f:
        claims = json.load(f)
    with open(exp_dir / "memories.jsonl") as f:
        memories = [json.loads(line) for line in f]

    claim_lookup = {c["causal_claim_id"]: c for c in claims}

    cause_keywords = {
        "CC001": ["termination", "resistance", "connector", "hardware"],
        "CC004": ["thermal", "heat", "temperature", "hot-chamber"],
        "CC006": ["thermal", "firmware", "race", "callback"],
        "CC008": ["retry", "retries", "volume", "congestion", "degrad"],
        "CC021": ["loop", "miss", "deadline", "diagnostic", "log"],
    }

    effect_keywords = {
        "CC001": ["retri", "command", "actuator"],
        "CC004": ["reset", "sensor"],
        "CC006": ["reset", "sensor"],
        "CC008": ["network", "degrad", "latency"],
        "CC021": ["storm", "cpu", "spike", "payload"],
    }

    contradicting_keywords = {
        "CC001": ["deploy", "software", "coincidence"],
        "CC004": [],
        "CC006": [],
        "CC008": ["storm.*caused", "retry.*caused"],
        "CC021": ["cpu.*cause", "saturation.*cause"],
    }

    filled = 0
    for e in evidence:
        cid = e["causal_claim_id"]
        if e.get("supporting_evidence") or e.get("contradicting_evidence"):
            continue
        if cid not in cause_keywords:
            continue

        claim = claim_lookup[cid]
        case_id = claim["case_id"]
        case_mems = [m for m in memories if case_id in m.get("tags", [])]

        supporting = []
        contradicting = []

        for m in case_mems:
            text = m["text"].lower()
            cause_match = any(kw in text for kw in cause_keywords[cid])
            effect_match = any(kw in text for kw in effect_keywords[cid])

            if cause_match and effect_match:
                supporting.append(m["memory_id"])
            elif cause_match:
                supporting.append(m["memory_id"])

            for pat in contradicting_keywords.get(cid, []):
                if re.search(pat, text):
                    if m["memory_id"] not in contradicting:
                        contradicting.append(m["memory_id"])

        e["supporting_evidence"] = supporting[:8]
        e["contradicting_evidence"] = contradicting[:5]
        filled += 1

    print(f"  Filled {filled} empty evidence entries")

    with open(exp_dir / "causal_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)


def resolve_evidence_overlaps(exp_dir):
    """Remove overlapping memory IDs that appear in both supporting and contradicting."""
    with open(exp_dir / "causal_evidence.json") as f:
        evidence = json.load(f)
    with open(exp_dir / "causal_claims.json") as f:
        claims = json.load(f)
    with open(exp_dir / "memories.jsonl") as f:
        memories = [json.loads(line) for line in f]

    mem_lookup = {m["memory_id"]: m for m in memories}
    claim_lookup = {c["causal_claim_id"]: c for c in claims}

    resolved = 0
    for e in evidence:
        sup = set(e.get("supporting_evidence", []))
        con = set(e.get("contradicting_evidence", []))
        overlap = sup & con

        if not overlap:
            continue

        cid = e["causal_claim_id"]
        claim = claim_lookup[cid]

        for mid in overlap:
            m = mem_lookup.get(mid, {})
            text = m.get("text", "").lower()

            cause_terms = claim["cause"].replace("-", " ").lower().split("+")
            is_supporting = any(term.strip() in text for term in cause_terms)

            contradiction_signals = [
                "coincidence", "does not remove", "remains",
                "before retries", "not.*cause", "revised",
            ]
            is_contradicting = any(re.search(sig, text) for sig in contradiction_signals)

            if is_contradicting and not is_supporting:
                e["supporting_evidence"] = [x for x in e["supporting_evidence"] if x != mid]
            elif is_supporting and not is_contradicting:
                e["contradicting_evidence"] = [x for x in e["contradicting_evidence"] if x != mid]
            else:
                e["contradicting_evidence"] = [x for x in e["contradicting_evidence"] if x != mid]

            resolved += 1

    print(f"  Resolved {resolved} overlapping evidence entries")

    with open(exp_dir / "causal_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)


BACKGROUND_VARIATIONS = {
    "Routine avionics build passed smoke test.": [
        "Routine avionics build passed smoke test.",
        "Avionics build completed smoke test without issues.",
        "Smoke test for the avionics build passed.",
        "Weekly avionics build passed its smoke test run.",
        "Avionics smoke test cleared; no anomalies detected.",
        "Standard avionics build smoke test completed successfully.",
        "Avionics build passed the routine smoke test cycle.",
        "Smoke test results for the avionics build: all clear.",
        "Avionics build ran through smoke test; passed.",
        "Routine smoke test on the latest avionics build: pass.",
        "The avionics build smoke test completed normally.",
        "Avionics CI build passed its smoke test.",
        "Build smoke test for avionics: passed without regressions.",
        "Avionics build smoke test cleared on this cycle.",
        "The regular avionics smoke test passed.",
        "Avionics build smoke test ran and passed.",
        "Smoke test for avionics build: green.",
        "Avionics build passed the scheduled smoke test.",
        "Standard smoke test on the avionics build passed.",
        "Avionics build smoke test completed; no failures.",
        "Routine avionics smoke test passed this cycle.",
        "Avionics build completed its smoke test run.",
        "Smoke test on the avionics build: passed.",
        "The avionics smoke test ran clean.",
    ],
    "Test fixture firmware was updated without anomalies.": [
        "Test fixture firmware was updated without anomalies.",
        "Firmware update on the test fixture completed cleanly.",
        "Test fixture firmware update applied; no anomalies observed.",
        "Updated the test fixture firmware. No issues reported.",
        "Test fixture firmware revision applied without incident.",
        "Firmware on the test fixture was refreshed without errors.",
        "Applied test fixture firmware update; all checks passed.",
        "Test fixture firmware update completed normally.",
        "Firmware update for the test fixture went through without anomalies.",
        "Test fixture firmware was patched. No anomalies detected.",
        "The test fixture firmware update ran without issues.",
        "Test fixture firmware refreshed; no anomalies this cycle.",
        "Firmware update on the test fixture: clean apply.",
        "Test fixture firmware was updated; no errors or anomalies.",
        "Routine firmware update on the test fixture completed.",
        "Test fixture firmware applied without incident.",
        "Firmware revision on the test fixture: no anomalies.",
        "Updated test fixture firmware. Completed without issues.",
        "Test fixture firmware update: no anomalies, applied cleanly.",
        "Test fixture firmware was updated to the latest revision without anomalies.",
    ],
    "Network gateway certificate inventory was refreshed.": [
        "Network gateway certificate inventory was refreshed.",
        "Certificate inventory on the network gateway was updated.",
        "Refreshed the network gateway certificate inventory.",
        "Network gateway certificates were re-inventoried.",
        "Gateway certificate inventory refreshed; all certs current.",
        "Network gateway certificate inventory update completed.",
        "Certificate refresh on the network gateway ran successfully.",
        "Network gateway certs were refreshed this cycle.",
        "Gateway certificate inventory was updated without issues.",
        "Refreshed network gateway certificate inventory.",
        "Network gateway certificate inventory: refreshed.",
        "The gateway certificate inventory was refreshed.",
        "Certificate inventory refresh on the network gateway completed.",
        "Network gateway certificate inventory was renewed.",
        "Gateway certificate inventory refresh: completed.",
        "Updated the certificate inventory on the network gateway.",
        "Network gateway certificate inventory refresh completed.",
        "Certificate inventory on the gateway was refreshed.",
        "Network gateway: certificate inventory refreshed.",
        "Refreshed certificate inventory for the network gateway.",
    ],
    "Calibration database backup completed.": [
        "Calibration database backup completed.",
        "Backup of the calibration database finished.",
        "Calibration DB backup completed successfully.",
        "Completed the calibration database backup.",
        "Calibration database backup ran to completion.",
        "Calibration database was backed up.",
        "Backup of calibration database completed without errors.",
        "Calibration DB backup: completed.",
        "The calibration database backup completed.",
        "Calibration database backup finished this cycle.",
        "Scheduled calibration database backup completed.",
        "Calibration database backup completed normally.",
        "Calibration DB backup completed this run.",
        "Backup for calibration database: completed.",
        "Calibration database backup ran successfully.",
        "Completed calibration database scheduled backup.",
        "Calibration database backup: finished.",
        "Calibration database backup completed on schedule.",
        "Ran calibration database backup; completed.",
    ],
    "A lab camera was replaced after a storage fault.": [
        "A lab camera was replaced after a storage fault.",
        "Lab camera replaced due to a storage fault.",
        "Replaced the lab camera following a storage failure.",
        "Lab camera swap: storage fault on the previous unit.",
        "A storage fault caused a lab camera replacement.",
        "Lab camera was swapped out after storage fault.",
        "Replaced lab camera after it developed a storage fault.",
        "Lab camera replaced; previous unit had a storage fault.",
        "Storage fault on a lab camera; unit was replaced.",
        "A lab camera was swapped after storage fault.",
        "Lab camera replacement due to storage fault.",
        "Replaced a lab camera after a storage-related fault.",
        "Lab camera was replaced following a storage issue.",
        "A lab camera was replaced because of a storage fault.",
        "Lab camera replaced after experiencing a storage fault.",
        "Storage fault on lab camera; replaced with new unit.",
        "Lab camera swap completed after storage fault.",
        "A lab camera had a storage fault and was replaced.",
    ],
    "Flight-test scheduling shifted by one day.": [
        "Flight-test scheduling shifted by one day.",
        "Flight-test schedule was shifted by a day.",
        "Shifted the flight-test schedule by one day.",
        "Flight-test schedule pushed by one day.",
        "Flight-test scheduling moved by one day.",
        "One-day shift in the flight-test schedule.",
        "Flight-test schedule adjusted by one day.",
        "The flight-test schedule was shifted by a day.",
        "Flight-test scheduling: one-day shift applied.",
        "Adjusted flight-test schedule by one day.",
        "Flight-test scheduling shifted one day forward.",
        "Schedule for flight testing shifted by one day.",
        "Flight-test schedule: shifted by one day.",
        "Flight-test scheduling was adjusted by one day.",
        "One-day shift applied to the flight-test schedule.",
        "Flight-test schedule shifted by a single day.",
        "Flight-test scheduling: one-day adjustment.",
        "The flight-test schedule shifted by one day.",
    ],
    "Documentation build upgraded its markdown parser.": [
        "Documentation build upgraded its markdown parser.",
        "Upgraded the markdown parser in the documentation build.",
        "Documentation build: markdown parser was upgraded.",
        "Markdown parser in the doc build was updated.",
        "Doc build upgraded to a new markdown parser.",
        "Upgraded markdown parser for the documentation build.",
        "Documentation build now uses an upgraded markdown parser.",
        "The documentation build's markdown parser was upgraded.",
        "Markdown parser upgrade applied to the doc build.",
        "Documentation build: upgraded markdown parser.",
        "Upgraded the doc build markdown parser.",
        "The markdown parser in the documentation build was updated.",
        "Doc build markdown parser: upgraded.",
        "Applied markdown parser upgrade to the documentation build.",
        "Documentation build upgraded its markdown parser version.",
        "Markdown parser in the documentation build was upgraded.",
        "The doc build markdown parser was upgraded this cycle.",
    ],
    "Telemetry dashboard labels were reorganized.": [
        "Telemetry dashboard labels were reorganized.",
        "Reorganized the telemetry dashboard labels.",
        "Telemetry dashboard: labels were reorganized.",
        "Labels on the telemetry dashboard were reorganized.",
        "Telemetry dashboard labels got reorganized.",
        "Dashboard labels for telemetry were reorganized.",
        "Telemetry dashboard label reorganization completed.",
        "Reorganized telemetry dashboard labels.",
        "The telemetry dashboard labels were reorganized.",
        "Telemetry dashboard: label reorganization done.",
        "Labels on the telemetry dashboard: reorganized.",
        "Completed telemetry dashboard label reorganization.",
        "Telemetry dashboard labels reorganized this cycle.",
        "Reorganized the labels on the telemetry dashboard.",
        "Telemetry dashboard labels were updated and reorganized.",
        "Dashboard label reorganization on the telemetry view.",
        "Telemetry dashboard label layout was reorganized.",
    ],
    "Unrelated battery endurance test completed normally.": [
        "Unrelated battery endurance test completed normally.",
        "Battery endurance test completed without issues.",
        "Endurance test on the battery completed normally.",
        "Battery endurance test: completed normally.",
        "The battery endurance test finished normally.",
        "Battery endurance test ran to normal completion.",
        "Completed the battery endurance test normally.",
        "Battery endurance test completed this cycle.",
        "Endurance test for the battery pack completed normally.",
        "Battery endurance test: normal completion.",
        "The battery endurance test completed without anomalies.",
        "Battery endurance test ran and completed normally.",
        "Battery endurance testing completed normally.",
        "Completed battery endurance test; no issues.",
        "Battery endurance test finished: normal results.",
    ],
    "Release checklist wording was revised.": [
        "Release checklist wording was revised.",
        "Revised the wording on the release checklist.",
        "Release checklist: wording was revised.",
        "Wording on the release checklist was updated.",
        "Release checklist wording revision completed.",
        "Updated the release checklist wording.",
        "The release checklist wording was revised.",
        "Release checklist: revised wording.",
        "Wording revision applied to the release checklist.",
        "Release checklist wording was revised this cycle.",
        "Revised release checklist wording.",
        "The wording on the release checklist was revised.",
    ],
}


def vary_background_memories(exp_dir):
    """Vary background memory texts to test recall-frequency tracking."""
    with open(exp_dir / "memories.jsonl") as f:
        memories = [json.loads(line) for line in f]

    text_counter = Counter(m["text"] for m in memories)
    duped_texts = {t for t, c in text_counter.items() if c > 1}

    # Track how many times we've seen each original text
    original_usage = defaultdict(int)
    varied = 0

    for m in memories:
        original_text = m["text"]
        if original_text not in duped_texts:
            continue

        variations = BACKGROUND_VARIATIONS.get(original_text)
        if not variations:
            continue

        idx = original_usage[original_text]
        original_usage[original_text] += 1
        m["text"] = variations[idx % len(variations)]
        varied += 1

    print(f"  Varied {varied} background memory texts")

    new_counter = Counter(m["text"] for m in memories)
    still_duped = sum(c - 1 for _, c in new_counter.items() if c > 1)
    print(f"  Remaining exact duplicate texts: {still_duped}")

    with open(exp_dir / "memories.jsonl", "w") as f:
        for m in memories:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


def fix_query_answers(exp_dir):
    """Write per-case expected_claims for generic query answers."""
    with open(exp_dir / "queries.jsonl") as f:
        queries = [json.loads(line) for line in f]
    with open(exp_dir / "causal_claims.json") as f:
        claims = json.load(f)

    case_evidence_answers = {
        "C01": "Bus termination resistance at one connector caused actuator command retries; the software deployment was temporal coincidence, not a cause (rollback did not remove lag, hardware replacement did).",
        "C02": "High thermal load and a firmware race in the thermal compensation callback jointly caused sensor resets; neither alone was sufficient (hot-chamber with prior firmware: no reset; cool-chamber with candidate firmware: no reset).",
        "C03": "Network degradation triggered retries, which amplified the problem; retries were not the root cause (latency increase began before retries accelerated; reducing retries improved but did not remove base loss).",
        "C04": "Contributing causes included thermal, firmware, and timing factors; multiple causal claims were established through controlled tests and intervention results.",
        "C05": "Causation is unresolved; competing explanations remain with evidence on both sides.",
        "C06": "Established through intervention and controlled testing: the cause was demonstrated by removing and reintroducing the factor under controlled conditions.",
        "C07": "Established through intervention tests: removing the suspected cause eliminated the effect, and reintroduction restored it.",
        "C08": "Causation is unresolved; both proposed causal directions have supporting evidence, and controlled interventions did not fully isolate one direction.",
        "C09": "Control-loop deadline misses caused a diagnostic log storm (misses began before logging exploded; disabling verbose diagnostics removed CPU spike but not all misses); initial triage incorrectly blamed CPU saturation.",
        "C10": "Established through controlled intervention and chronological evidence analysis.",
    }

    case_status_answers = {
        "C01": "Established: bus termination resistance causes actuator retries. The software deployment was a noncausal temporal sequence.",
        "C02": "Established: high thermal load contributes to sensor resets; high thermal load + firmware race jointly cause sensor resets.",
        "C03": "Established: network degradation triggers retries (amplifying). Retry volume rise contributes to further degradation (feedback loop).",
        "C04": "Multiple established causal links between thermal, firmware, and timing factors.",
        "C05": "Unresolved: competing explanations with evidence on both sides.",
        "C06": "Established through controlled intervention testing.",
        "C07": "Established through controlled intervention and reproduction.",
        "C08": "Unresolved: both causal directions have supporting evidence.",
        "C09": "Established: control-loop misses cause diagnostic log storm. Initial CPU-saturation hypothesis was revised.",
        "C10": "Established through chronological and intervention evidence.",
    }

    case_belief_answers = {
        "C01": "Initial team belief: the software deployment caused the lag (post hoc reasoning). Revised after hardware inspection showed termination resistance was the real cause.",
        "C02": "Initial hypothesis: thermal load alone. Revised after firmware trace revealed a race condition in the thermal compensation callback.",
        "C03": "Initial note: retry storm probably caused degradation. Revised after packet traces showed latency increase began before retries.",
        "C04": "Beliefs evolved as controlled tests isolated individual contributing factors.",
        "C05": "No consensus reached; competing beliefs persist among investigators.",
        "C06": "Initial suspicion confirmed by intervention testing.",
        "C07": "Initial hypothesis confirmed through controlled reproduction.",
        "C08": "Competing beliefs remain; evidence does not definitively favor one direction.",
        "C09": "Initial triage blamed CPU saturation for missed loops. Revised: misses caused the diagnostic storm, not the reverse.",
        "C10": "Initial beliefs aligned with chronological evidence; confirmed through intervention.",
    }

    generic_smo = "Usually no; interpret it according to its role as observation, belief, hypothesis, intervention result, or official position."
    generic_evidence = "Use contemporaneous evidence and intervention/reproduction results, not sequence alone."
    generic_status = "Report the early working explanation separately from final objective status."
    generic_belief = "No; early status reflected a working hypothesis, not final causal truth."

    fixed = 0
    for q in queries:
        case_match = re.search(r"(C\d{2})", q.get("query", ""))
        if not case_match:
            continue

        case_id = case_match.group(1)

        if q["category"] == "causal_evidence" and q["expected_claims"] == [generic_evidence]:
            if case_id in case_evidence_answers:
                q["expected_claims"] = [case_evidence_answers[case_id]]
                fixed += 1

        elif q["category"] == "causal_status" and q["expected_claims"] == [generic_status]:
            if case_id in case_status_answers:
                q["expected_claims"] = [case_status_answers[case_id]]
                fixed += 1

        elif q["category"] == "historical_causal_belief" and q["expected_claims"] == [generic_belief]:
            if case_id in case_belief_answers:
                q["expected_claims"] = [case_belief_answers[case_id]]
                fixed += 1

    # For single_memory_overclaim: specialize by truth_role
    with open(exp_dir / "memories.jsonl") as f:
        mem_lookup = {}
        for line in f:
            m = json.loads(line)
            mem_lookup[m["memory_id"]] = m

    role_answers = {
        "objective_trace": "No. This is an objective observation; interpret it as evidence, not as an established causal claim.",
        "belief": "No. This records a belief or working hypothesis at the time, not established causation.",
        "hypothesis": "No. This is a hypothesis under investigation, not an established causal finding.",
        "official_position": "No. This records the program's official position at the time, which may reflect an initial working theory rather than final causal truth.",
        "background": "No. This is background activity unrelated to any causal investigation.",
        "retrospective_interpretation": "No. This is a later reinterpretation, not contemporaneous causal evidence.",
    }

    for q in queries:
        if q["category"] != "single_memory_overclaim":
            continue
        if q["expected_claims"] != [generic_smo]:
            continue

        mid = (q.get("relevant_memory_ids") or [None])[0]
        if mid and mid in mem_lookup:
            role = mem_lookup[mid].get("truth_role", "")
            if role in role_answers:
                q["expected_claims"] = [role_answers[role]]
                fixed += 1

    print(f"  Fixed {fixed} generic query answers with case/role-specific content")

    with open(exp_dir / "queries.jsonl", "w") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")


def populate_relations(exp_dir):
    """Populate derived_from and contradicts fields based on content relationships."""
    with open(exp_dir / "memories.jsonl") as f:
        memories = [json.loads(line) for line in f]

    case_groups = defaultdict(list)
    for m in memories:
        for tag in m.get("tags", []):
            if re.match(r"C\d{2}", tag):
                case_groups[tag].append(m)

    suffix_patterns = [
        r"\s*This observation does not by itself establish causality\.\s*$",
        r"\s*The note distinguishes observation from explanation\.\s*$",
        r"\s*The artifact is contemporaneous with the investigation\.?\s*$",
        r"\s*Investigators record this as evidence rather than final proof\.\s*$",
    ]

    relations_added = 0
    for case_id, case_mems in case_groups.items():
        base_map = defaultdict(list)
        for m in case_mems:
            base = m["text"]
            for pat in suffix_patterns:
                base = re.sub(pat, "", base)
            base = base.strip().rstrip(".")
            base_map[base].append(m)

        for base, group in base_map.items():
            if len(group) <= 1:
                continue
            original = group[0]
            for variant in group[1:]:
                if not variant.get("derived_from"):
                    variant["derived_from"] = [original["memory_id"]]
                    relations_added += 1

    # Find contradicting pairs: official positions vs corrective traces
    for case_id, case_mems in case_groups.items():
        officials = [m for m in case_mems if m.get("truth_role") == "official_position"]
        objectives = [m for m in case_mems if m.get("truth_role") == "objective_trace"]

        for off in officials:
            off_text = off["text"].lower()
            for obj in objectives:
                obj_text = obj["text"].lower()
                if (("deployment" in off_text and ("cause" in off_text or "explanation" in off_text)) and
                    ("coincidence" in obj_text or "does not remove" in obj_text or "rollback" in obj_text)):
                    if off["memory_id"] not in obj.get("contradicts", []):
                        obj.setdefault("contradicts", []).append(off["memory_id"])
                        relations_added += 1
                    if obj["memory_id"] not in off.get("contradicts", []):
                        off.setdefault("contradicts", []).append(obj["memory_id"])
                        relations_added += 1

    print(f"  Added {relations_added} relation edges (derived_from, contradicts)")

    with open(exp_dir / "memories.jsonl", "w") as f:
        for m in memories:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


def add_manifest_checksums(exp_dir):
    """Add SHA-256 checksums to manifest.json."""
    manifest_path = exp_dir / "manifest.json"

    with open(manifest_path) as f:
        manifest = json.load(f)

    files_to_check = [
        "README.md", "story_bible.md", "memories.jsonl", "queries.jsonl",
        "causal_claims.json", "causal_evidence.json", "causal_graph.json",
        "truth_state.json", "experimental_map.json", "seed_memories.jsonl",
        "self_review.md", "sources.md",
    ]

    perturbations_dir = exp_dir / "perturbations"
    if perturbations_dir.exists():
        for p in sorted(perturbations_dir.iterdir()):
            if p.is_file():
                files_to_check.append(f"perturbations/{p.name}")

    file_entries = []
    for rel_path in files_to_check:
        full_path = exp_dir / rel_path
        if full_path.exists():
            file_entries.append({
                "path": rel_path,
                "bytes": full_path.stat().st_size,
                "sha256": sha256_file(full_path),
            })

    manifest["files"] = file_entries

    with open(exp_dir / "queries.jsonl") as f:
        manifest["query_count"] = sum(1 for _ in f)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"  Manifest: {len(file_entries)} files checksummed")


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_exp09.py <experiment_09_dir>")
        sys.exit(1)

    exp_dir = Path(sys.argv[1])
    if not (exp_dir / "memories.jsonl").exists():
        print(f"Error: {exp_dir}/memories.jsonl not found")
        sys.exit(1)

    print("Fixing Experiment 09 (Causal Attribution / Helix Flight Controls)...")
    print()

    print("[1/6] Filling empty evidence entries...")
    fill_empty_evidence(exp_dir)

    print("[2/6] Resolving evidence overlaps...")
    resolve_evidence_overlaps(exp_dir)

    print("[3/6] Varying background memory texts...")
    vary_background_memories(exp_dir)

    print("[4/6] Fixing generic query answers...")
    fix_query_answers(exp_dir)

    print("[5/6] Populating relation fields...")
    populate_relations(exp_dir)

    print("[6/6] Adding manifest checksums...")
    add_manifest_checksums(exp_dir)

    print()
    print("Done. Run check_exp09.py to verify.")


if __name__ == "__main__":
    main()
