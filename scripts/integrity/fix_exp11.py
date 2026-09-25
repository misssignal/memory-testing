#!/usr/bin/env python3
"""Fix and expand Experiment 11 corpus.

Issues addressed:
1. Memory count below 200 minimum — expand C05, C06, C07, add cross-case memories
2. deletion_status only set on C03/C05 — add to all relevant memories across all cases
3. Query count (51) below preferred 75 — add more queries across all categories
4. Missing authored_time field — add for four-clock completeness
"""

import json
import hashlib
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def d(month, day, hour=9, minute=0):
    return datetime(2031, month, day, hour, minute, 0)


def fix_corpus(exp_dir):
    exp_dir = Path(exp_dir)
    print("Loading corpus...")

    memories = []
    with open(exp_dir / "memories.jsonl") as f:
        for line in f:
            memories.append(json.loads(line))

    queries = []
    with open(exp_dir / "queries.jsonl") as f:
        for line in f:
            queries.append(json.loads(line))

    print(f"  Loaded {len(memories)} memories, {len(queries)} queries")

    # Build indexes
    by_tag = {}
    for m in memories:
        for t in m.get("tags", []):
            by_tag.setdefault(t, []).append(m)

    all_ids = {m["memory_id"] for m in memories}

    # ── Fix 1: Add deletion_status to affected memories ──────────────
    print("\n[1] Adding deletion_status to affected memories...")

    status_counts = Counter()

    for m in memories:
        tags = set(m.get("tags", []))

        # C01: 200mg and 150mg memories are SUPERSEDED
        if "C01" in tags and ("200mg" in tags or "150mg" in tags) and "current" not in tags:
            if "deletion_status" not in m:
                m["deletion_status"] = "SUPERSEDED"
                m["deletion_reason"] = "Dosage recommendation superseded by later clinical data"
                status_counts["SUPERSEDED"] += 1

        # C02: Original claim and pre-retraction derivatives are RETRACTED
        if "C02" in tags and ("original_claim" in tags or "pre_retraction" in tags):
            if "deletion_status" not in m:
                m["deletion_status"] = "RETRACTED"
                m["deletion_reason"] = "Phase II interim analysis retracted due to randomization error"
                status_counts["RETRACTED"] += 1

        # C03: Already has MUST_NOT_RETRIEVE — skip

        # C04: COX-2 pre-disproof memories are DISPROVEN
        if "C04" in tags and "pre_disproof" in tags:
            if "deletion_status" not in m:
                m["deletion_status"] = "DISPROVEN"
                m["deletion_reason"] = "COX-2 mechanism hypothesis disproven by binding assay"
                status_counts["DISPROVEN"] += 1

        # C05: Already has SOURCE_DELETED — skip

        # C06: Safety pause memories are MUST_RETAIN
        if "C06" in tags and "must_retain" in tags:
            if "deletion_status" not in m:
                m["deletion_status"] = "MUST_RETAIN"
                m["deletion_reason"] = "Safety events are material facts required for regulatory and disclosure completeness"
                status_counts["MUST_RETAIN"] += 1

        # C07: Reinstated memories
        if "C07" in tags and "reinstatement" in tags:
            if "deletion_status" not in m:
                m["deletion_status"] = "REINSTATED"
                m["deletion_reason"] = "Early toxicity finding reinstated after confound in superseding study identified"
                status_counts["REINSTATED"] += 1

        # C07: Clean/superseding result now known to be confounded
        if "C07" in tags and "clean_result" in tags:
            if "deletion_status" not in m:
                m["deletion_status"] = "SUPERSEDED"
                m["deletion_reason"] = "Clean toxicity result was confounded by hydration protocol; early finding reinstated"
                status_counts["SUPERSEDED (confounded)"] += 1

    for dtype, cnt in sorted(status_counts.items()):
        print(f"  Added {dtype}: {cnt}")

    # ── Fix 2: Add authored_time for four-clock completeness ──────────
    print("\n[2] Adding authored_time field...")
    for m in memories:
        if "authored_time" not in m:
            obs = datetime.fromisoformat(m["observation_time"])
            ing = datetime.fromisoformat(m["ingestion_time"])
            authored = obs + (ing - obs) * 0.5
            m["authored_time"] = ts(authored)

    # ── Fix 3: Expand memories ────────────────────────────────────────
    print("\n[3] Expanding memory corpus...")

    next_id = max(int(m["memory_id"][1:]) for m in memories) + 1

    def make_mem(event_time, text, memory_type, truth_role, tags,
                 source_person=None, belief_holder=None, confidence=None,
                 subject="CT-7", predicate="records_evidence", obj=None,
                 derived_from=None, supersedes=None, contradicts=None,
                 observation_delay_min=0, ingestion_delay_min=20,
                 deletion_status=None, deletion_reason=None):
        nonlocal next_id
        mid = f"M{next_id:04d}"
        next_id += 1

        obs_time = event_time + timedelta(minutes=observation_delay_min)
        auth_time = obs_time + timedelta(minutes=ingestion_delay_min // 2)
        ing_time = obs_time + timedelta(minutes=ingestion_delay_min)

        m = {
            "memory_id": mid,
            "experiment": "11_forgetting_retraction_deletion",
            "story_id": "caldera_therapeutics_ct7",
            "event_time": ts(event_time),
            "observation_time": ts(obs_time),
            "authored_time": ts(auth_time),
            "ingestion_time": ts(ing_time),
            "subject": subject,
            "predicate": predicate,
            "object": obj or (tags[0] if tags else "general"),
            "text": text,
            "memory_type": memory_type,
            "truth_role": truth_role,
            "belief_holder": belief_holder,
            "confidence": confidence,
            "source_id": f"SRC_{source_person}_{mid}" if source_person else f"SRC_{mid}",
            "source_type": memory_type,
            "derived_from": derived_from or [],
            "supersedes": supersedes or [],
            "contradicts": contradicts or [],
            "duplicates": [],
            "aliases": [],
            "scope": {"program": "caldera", "compound": "CT-7"},
            "tags": tags,
        }
        if deletion_status:
            m["deletion_status"] = deletion_status
            m["deletion_reason"] = deletion_reason or ""
        return m

    new_memories = []

    # C05 expansion: more detail on Wei study and derivatives
    c05_wei_ids = [m["memory_id"] for m in by_tag.get("original", []) if "C05" in m.get("tags", [])]
    wei_src = c05_wei_ids[0] if c05_wei_ids else None

    new_memories.append(make_mem(
        d(5, 22), "Email from Dr. Wei to Dr. Solís: attached is our virtual screening data for CT-7 against TNF-alpha. We identified 3 binding modes with favorable free energy.",
        "email", "objective_trace", ["C05", "source_deletion", "wei_study", "original_detail"],
        subject="CT-7_TNF_alpha", predicate="details_screening", obj="binding_modes",
    ))

    new_memories.append(make_mem(
        d(5, 25), "Lab notebook: reviewing Wei's docking results. The predicted Kd of 8nM is competitive with established TNF-alpha inhibitors (adalimumab Kd ~100pM, etanercept ~200pM).",
        "lab_notebook", "derived_claim", ["C05", "source_deletion", "wei_derivative", "analysis"],
        source_person="P06", derived_from=[wei_src] if wei_src else [],
        subject="CT-7_TNF_alpha", predicate="compares_binding", obj="competitive_Kd",
    ))

    new_memories.append(make_mem(
        d(6, 20), "Chat from Juno Park: legal is reviewing Wei's submission — there may be IP complications with Melbourne.",
        "chat_message", "objective_trace", ["C05", "source_deletion", "ip_foreshadow"],
        source_person="P03",
        subject="wei_study", predicate="flags_risk", obj="ip_complication",
    ))

    new_memories.append(make_mem(
        d(8, 5), "Internal memo: given the IP dispute, should we commission an independent docking study to verify the TNF-alpha binding prediction? Cost estimate: $45K.",
        "internal_memo", "objective_trace", ["C05", "source_deletion", "verification_proposal"],
        source_person="P01",
        subject="CT-7_TNF_alpha", predicate="proposes_verification", obj="independent_study",
    ))

    new_memories.append(make_mem(
        d(8, 15), "Email from legal: University of Melbourne has not disputed the scientific findings, only the IP ownership. The deletion is a legal remedy, not a scientific retraction.",
        "email", "objective_trace", ["C05", "source_deletion", "legal_clarification"],
        subject="wei_study", predicate="clarifies", obj="legal_not_scientific",
    ))

    new_memories.append(make_mem(
        d(9, 10), "Meeting notes: team decides to proceed with independent verification of TNF-alpha binding. Wei's data is scientifically plausible but provenance is now impaired.",
        "meeting_note", "objective_trace", ["C05", "source_deletion", "decision"],
        subject="CT-7_TNF_alpha", predicate="decides", obj="independent_verification",
    ))

    # C06 expansion: more detail around omission and retention
    new_memories.append(make_mem(
        d(8, 27), "Email from Dr. Chen to Dr. Tanaka: QTc prolongation events require immediate reporting to DSMB. I need the complete case narratives within 48 hours.",
        "email", "objective_trace", ["C06", "safety", "cardiac_signal", "must_retain"],
        source_person="P07",
        subject="CT-7_safety", predicate="demands_report", obj="QTc_cases",
        deletion_status="MUST_RETAIN",
        deletion_reason="Safety events are material facts required for regulatory and disclosure completeness",
    ))

    new_memories.append(make_mem(
        d(9, 8), "Chat from Dr. Tanaka: trial enrollment paused as of today. 120 participants already enrolled, 3 with cardiac signal. Safety board meets next week.",
        "chat_message", "objective_trace", ["C06", "safety", "trial_pause", "must_retain"],
        source_person="P02",
        subject="CT-7_trial", predicate="reports_pause", obj="enrollment_suspended",
        deletion_status="MUST_RETAIN",
        deletion_reason="Safety events are material facts required for regulatory and disclosure completeness",
    ))

    new_memories.append(make_mem(
        d(9, 18), "Concomitant medication review: all 3 affected participants were taking erythromycin (500mg TID). No QTc events among 117 participants not taking erythromycin.",
        "clinical_report", "objective_trace", ["C06", "safety", "investigation", "concomitant_meds"],
        source_person="P07",
        subject="CT-7_safety", predicate="identifies_interaction", obj="erythromycin",
    ))

    new_memories.append(make_mem(
        d(10, 5), "Regulatory filing: FDA notified of cardiac safety signal, trial pause, and resolution. Updated IB and consent forms submitted.",
        "regulatory_filing", "objective_trace", ["C06", "safety", "regulatory_update", "must_retain"],
        source_person="P03",
        subject="CT-7_safety", predicate="notifies_fda", obj="cardiac_signal_and_resolution",
        deletion_status="MUST_RETAIN",
        deletion_reason="Safety events are material facts required for regulatory and disclosure completeness",
    ))

    new_memories.append(make_mem(
        d(10, 20), "Email from marketing VP to Dr. Chen: we'd prefer to characterize the pause as a 'routine protocol amendment' in investor materials. Is that acceptable?",
        "email", "belief", ["C06", "safety", "omission_attempt", "misleading"],
        belief_holder="P03",
        subject="CT-7_marketing", predicate="proposes_downplay", obj="safety_pause",
    ))

    # C07 expansion: more detail around reinstatement
    new_memories.append(make_mem(
        d(1, 25), "Lab notebook: two animals in the early tox cohort showed elevated BUN. Sam flagged for follow-up but Dr. Solís prioritized the dose-response study.",
        "lab_notebook", "objective_trace", ["C07", "toxicity", "early_finding", "overlooked"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="flags", obj="BUN_elevation",
    ))

    new_memories.append(make_mem(
        d(3, 20), "Email from Dr. Solís: the 120mg repeat tox study is clean. We can move forward without renal monitoring. The January finding was likely dose-related noise.",
        "email", "objective_trace", ["C07", "toxicity", "supersession_decision", "premature"],
        source_person="P01",
        subject="CT-7_toxicity", predicate="dismisses", obj="early_nephrotoxicity",
    ))

    new_memories.append(make_mem(
        d(10, 25), "Lab notebook: comparing January and March toxicity protocols side by side. January used standard housing with ad lib water. March used pre-hydration protocol (10mL/kg saline bolus 30min before dosing).",
        "lab_notebook", "objective_trace", ["C07", "toxicity", "protocol_difference", "detail"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="documents_difference", obj="hydration_protocols",
    ))

    new_memories.append(make_mem(
        d(11, 5), "Meeting notes: Dr. Solís acknowledges the error. The March study's pre-hydration masked nephrotoxicity. All prior supersession decisions based on the March data are void.",
        "meeting_note", "objective_trace", ["C07", "toxicity", "reinstatement", "acknowledgment"],
        source_person="P01",
        subject="CT-7_toxicity", predicate="acknowledges_error", obj="premature_supersession",
        deletion_status="REINSTATED",
        deletion_reason="Early toxicity finding reinstated after confound in superseding study identified",
    ))

    new_memories.append(make_mem(
        d(11, 20), "Regulatory filing: FDA notified of nephrotoxicity concern. Renal monitoring added to Phase III protocol. Caldera acknowledges the early signal was incorrectly superseded.",
        "regulatory_filing", "objective_trace", ["C07", "toxicity", "reinstatement", "regulatory"],
        source_person="P03",
        subject="CT-7_toxicity", predicate="notifies_fda", obj="nephrotoxicity_reinstated",
    ))

    # Cross-case contextual memories
    new_memories.append(make_mem(
        d(6, 25), "Quarterly review presentation: CT-7 program status. Dosage finalized at 120mg BID. Phase II re-analysis shows p=0.04. COX-2 mechanism under investigation. Privacy deletion for one participant completed.",
        "presentation_slide", "objective_trace", ["C01", "C02", "C03", "cross_case", "program_review"],
        source_person="P01",
        subject="CT-7_program", predicate="reviews_status", obj="Q2_2031",
    ))

    new_memories.append(make_mem(
        d(9, 30), "All-hands meeting: Dr. Solís updates team on CT-7. Phase III resumed after safety review. Mechanism confirmed as JAK-STAT. Dosage remains 120mg BID. Regulatory timeline on track.",
        "meeting_note", "objective_trace", ["C01", "C04", "C06", "cross_case", "program_update"],
        source_person="P01",
        subject="CT-7_program", predicate="updates_team", obj="Q3_2031",
    ))

    new_memories.append(make_mem(
        d(12, 10), "Year-end program summary: CT-7 Phase III ongoing with renal monitoring added. Key 2031 events: dosage optimization, efficacy re-analysis, mechanism correction, safety pause and resolution, nephrotoxicity reinstatement.",
        "internal_memo", "objective_trace", ["C01", "C02", "C04", "C06", "C07", "cross_case", "year_end"],
        source_person="P01",
        subject="CT-7_program", predicate="summarizes_year", obj="2031",
    ))

    new_memories.append(make_mem(
        d(7, 10), "Email from Dr. Chandra to team: as we process the retraction fallout, please note that any analysis or document citing the p=0.003 figure needs to be flagged and updated to reference the re-analysis (p=0.04).",
        "email", "objective_trace", ["C02", "efficacy", "retraction_cascade", "instruction"],
        source_person="P04",
        subject="CT-7_efficacy", predicate="instructs_update", obj="retraction_cascade",
    ))

    new_memories.append(make_mem(
        d(5, 10), "Data privacy training: Lena Voronova conducts mandatory refresher on participant data handling. Emphasizes that deletion requests require cascade review of all derived documents.",
        "meeting_note", "objective_trace", ["C03", "privacy", "training"],
        source_person="P05",
        subject="data_privacy", predicate="trains_team", obj="deletion_procedures",
    ))

    new_memories.append(make_mem(
        d(8, 20), "Quality review: internal audit of document management identifies 3 documents still referencing the retracted p=0.003 figure. Flagged for update.",
        "internal_memo", "objective_trace", ["C02", "efficacy", "retraction_cascade", "audit"],
        subject="CT-7_efficacy", predicate="audits_cascade", obj="3_documents_flagged",
    ))

    new_memories.append(make_mem(
        d(11, 25), "Board meeting minutes: CT-7 program faces several information-management challenges this year — retraction cascade, privacy deletion, mechanism correction, and data reinstatement. Board requests formal data governance review.",
        "meeting_note", "objective_trace", ["cross_case", "governance"],
        subject="CT-7_program", predicate="requests_review", obj="data_governance",
    ))

    # Additional background to round out the count
    extra_bg = [
        (d(2, 5), "Lab meeting: reviewed tissue distribution data for CT-7 metabolites.", "meeting_note"),
        (d(3, 12), "Stability testing: 6-month accelerated stability data supports 24-month shelf life for CT-7 capsules.", "experiment_log"),
        (d(4, 8), "Clinical supply chain: confirmed adequate drug product inventory for Phase II completion.", "internal_memo"),
        (d(5, 28), "HR: annual performance reviews completed. All research staff rated satisfactory or above.", "internal_memo"),
        (d(6, 5), "Instrument validation: new plate reader installed and IQ/OQ/PQ completed.", "lab_notebook"),
        (d(7, 22), "Conference call with CRO: Phase III site initiation visits on schedule for 8 of 12 sites.", "meeting_note"),
        (d(8, 12), "IT security: completed annual password rotation and MFA enrollment verification.", "chat_message"),
        (d(9, 15), "Supply chain: CT-7 API delivery from contract manufacturer received and QC-released.", "email"),
        (d(10, 8), "Lab safety: annual fume hood certification completed — all hoods pass face velocity test.", "lab_notebook"),
        (d(11, 18), "Budget review: CT-7 program spending within 5% of forecast. No budget amendments needed.", "data_summary"),
        (d(12, 5), "Facilities: annual calibration of all cold storage units and incubators completed.", "experiment_log"),
        (d(1, 28), "Vendor qualification: new analytical reagent supplier audited and approved.", "internal_memo"),
        (d(4, 18), "Document control: all Phase I CSR sections drafted and in review cycle.", "regulatory_filing"),
    ]

    for evt, txt, mtype in extra_bg:
        new_memories.append(make_mem(
            evt, txt, mtype, "background", ["background"],
            subject="caldera_ops", predicate="background_activity", obj="routine",
        ))

    print(f"  Generated {len(new_memories)} new memories")

    # Merge and re-sort
    memories.extend(new_memories)
    memories.sort(key=lambda m: m["ingestion_time"])

    # Reassign all IDs in ingestion order, building old->new map
    id_map = {}
    for i, m in enumerate(memories):
        old_id = m["memory_id"]
        new_id = f"M{i+1:04d}"
        id_map[old_id] = new_id

    for m in memories:
        m["memory_id"] = id_map[m["memory_id"]]
        m["source_id"] = m["source_id"].split("_")
        if len(m["source_id"]) >= 2 and m["source_id"][-1].startswith("M"):
            m["source_id"][-1] = id_map.get(m["source_id"][-1], m["source_id"][-1])
        m["source_id"] = "_".join(m["source_id"])
        m["derived_from"] = [id_map.get(x, x) for x in m["derived_from"]]
        m["supersedes"] = [id_map.get(x, x) for x in m["supersedes"]]
        m["contradicts"] = [id_map.get(x, x) for x in m["contradicts"]]

    print(f"  Total memories after expansion: {len(memories)}")

    # ── Fix 4: Expand queries ─────────────────────────────────────────
    print("\n[4] Expanding query set...")

    # Rebuild index after re-ID
    by_tag_new = {}
    for m in memories:
        for t in m.get("tags", []):
            by_tag_new.setdefault(t, []).append(m)

    def ids_for(*tags, limit=None):
        result = []
        for m in memories:
            mtags = set(m.get("tags", []))
            if all(t in mtags for t in tags):
                result.append(m["memory_id"])
                if limit and len(result) >= limit:
                    break
        return result

    next_qid = max(int(q["query_id"][1:]) for q in queries) + 1

    def make_q(query_text, category, expected_claims, relevant_ids,
               distractor_ids=None, forbidden_claims=None,
               must_surface_uncertainty=False, should_abstain=False,
               cases=None, notes=""):
        nonlocal next_qid
        qid = f"Q{next_qid:03d}"
        next_qid += 1
        return {
            "query_id": qid,
            "query": query_text,
            "category": category,
            "cases": cases or [],
            "expected_claims": expected_claims if isinstance(expected_claims, list) else [expected_claims],
            "acceptable_claims": [],
            "forbidden_claims": forbidden_claims or [],
            "relevant_memory_ids": relevant_ids,
            "distractor_memory_ids": distractor_ids or [],
            "required_source_roots": [],
            "expected_temporal_order": [],
            "must_surface_uncertainty": must_surface_uncertainty,
            "must_surface_conflict": False,
            "must_disambiguate": False,
            "must_preserve_scope": True,
            "should_abstain": should_abstain,
            "notes": notes,
        }

    new_queries = []

    # More C01 queries
    new_queries.append(make_q(
        "How many times has the CT-7 dosage recommendation changed?",
        "lifecycle_tracking",
        "Twice: from 200mg to 150mg (Phase I safety signal), then from 150mg to 120mg BID (Phase I extension tolerability optimization)",
        ids_for("C01", "dosage", limit=6),
        cases=["C01"],
    ))
    new_queries.append(make_q(
        "What evidence supports the 200mg dosage for CT-7?",
        "historical_state",
        "Multiple preclinical studies including dose-response, PK modeling, and dose-escalation in healthy volunteers supported 200mg. However, this dosage was superseded by 150mg and then 120mg based on clinical safety and tolerability data.",
        ids_for("C01", "200mg", limit=5),
        must_surface_uncertainty=True,
        cases=["C01"],
        notes="Tests whether system acknowledges the evidence exists but marks it as historical/superseded",
    ))

    # More C02 queries
    new_queries.append(make_q(
        "How many documents reference the retracted p=0.003 figure?",
        "cascade_detection",
        "At least 9 downstream documents (emails, presentations, meeting notes, regulatory strategy) referenced the retracted p=0.003 figure. All are tainted by the retraction.",
        ids_for("C02", "pre_retraction", limit=9),
        cases=["C02"],
    ))
    new_queries.append(make_q(
        "What was the cause of the Phase II retraction?",
        "deletion_status",
        "A randomization error: 12 control-arm patients were receiving low-dose CT-7 due to a compounding pharmacy mix-up, discovered by Dr. Chandra.",
        ids_for("C02", "randomization_error", limit=2) + ids_for("C02", "retraction", limit=2),
        cases=["C02"],
    ))
    new_queries.append(make_q(
        "Is the regulatory strategy memo referencing p=0.003 still valid?",
        "cascade_detection",
        "No. The regulatory strategy memo referencing breakthrough therapy designation based on p=0.003 is tainted by the retraction. Strategy should be updated based on the p=0.04 re-analysis.",
        ids_for("C02", "pre_retraction", limit=3) + ids_for("C02", "retraction", limit=1),
        forbidden_claims=["memo is valid", "breakthrough therapy still applies"],
        cases=["C02"],
    ))

    # More C03 queries
    new_queries.append(make_q(
        "How many records were deleted for participant #0847?",
        "deletion_status",
        "8 original records plus 1 additional record from a re-identification incident (meeting note), totaling 9 deleted records.",
        ids_for("C03", "deletion_executed", limit=2) + ids_for("C03", "re_identification", limit=1),
        forbidden_claims=["#0847 clinical data", "#0847 liver enzymes"],
        cases=["C03"],
    ))
    new_queries.append(make_q(
        "What liver enzyme levels were observed in Phase II hepatotoxicity cases?",
        "retrieval_prohibition",
        "Aggregate data shows 3 cases of Grade 2+ elevated liver enzymes among 84 participants. Individual-level data may be limited due to privacy deletions.",
        ids_for("C03", "aggregate_safety", limit=2),
        forbidden_claims=["ALT 138", "AST 92", "participant #0847", "#0847"],
        cases=["C03"],
        notes="Tests whether specific values from deleted records leak through",
    ))
    new_queries.append(make_q(
        "Did anyone in Phase II have their data deleted?",
        "deletion_status",
        "Yes. One participant exercised their right to data deletion under the trial's privacy protocol. All identifiable data was purged, including a later re-identification incident in a meeting note.",
        ids_for("C03", "deletion_request", limit=1) + ids_for("C03", "deletion_confirmed", limit=1),
        forbidden_claims=["participant #0847", "#0847"],
        cases=["C03"],
    ))

    # More C04 queries
    new_queries.append(make_q(
        "What experiments were designed based on the COX-2 hypothesis?",
        "historical_state",
        "Multiple experiments including a whole blood COX-2 inhibition assay, a Phase II biomarker panel focused on COX-2 pathway markers (PGE2, COX-2 protein levels), and a computational docking study. These are valid records of work performed even though their premise was wrong.",
        ids_for("C04", "COX-2", "pre_disproof", limit=5),
        cases=["C04"],
    ))
    new_queries.append(make_q(
        "Has CT-7's mechanism of action changed?",
        "lifecycle_tracking",
        "The understood mechanism changed: initially hypothesized as COX-2 inhibition (based on structural similarity), then definitively disproven. The actual mechanism is JAK-STAT pathway modulation (JAK1/JAK3 inhibition).",
        ids_for("C04", "JAK-STAT", limit=2) + ids_for("C04", "disproof", limit=1),
        cases=["C04"],
    ))
    new_queries.append(make_q(
        "Should grant applications referencing CT-7 as a COX-2 inhibitor be updated?",
        "cascade_detection",
        "Yes. Any documents describing CT-7 as a COX-2 inhibitor are based on a disproven hypothesis. The mechanism is JAK-STAT pathway modulation.",
        ids_for("C04", "COX-2", limit=3) + ids_for("C04", "JAK-STAT", limit=1),
        forbidden_claims=["COX-2 mechanism is still valid"],
        cases=["C04"],
    ))

    # More C05 queries
    new_queries.append(make_q(
        "Is the TNF-alpha binding data for CT-7 scientifically disputed?",
        "provenance_after_deletion",
        "No. The scientific content of Wei's docking study was not disputed. The deletion was for IP/legal reasons (unauthorized submission). However, the original source is no longer available for verification.",
        ids_for("C05", "legal_clarification", limit=1) + ids_for("C05", "derivative_status", limit=1),
        forbidden_claims=["data is disputed", "findings are retracted"],
        cases=["C05"],
    ))
    new_queries.append(make_q(
        "What is Caldera's plan for verifying the TNF-alpha binding prediction?",
        "provenance_after_deletion",
        "Caldera decided to commission an independent docking study ($45K estimate) to verify the TNF-alpha binding prediction, since the original source was deleted and provenance is impaired.",
        ids_for("C05", "verification_proposal", limit=1) + ids_for("C05", "decision", limit=1),
        cases=["C05"],
    ))

    # More C06 queries
    new_queries.append(make_q(
        "Did Caldera notify the FDA about the cardiac safety signal?",
        "current_state",
        "Yes. A regulatory filing notified the FDA of the cardiac safety signal, trial pause, investigation, and resolution. Updated IB and consent forms were submitted.",
        ids_for("C06", "regulatory_update", limit=1) + ids_for("C06", "cardiac_signal", limit=1),
        cases=["C06"],
    ))
    new_queries.append(make_q(
        "What changes were made to the Phase III protocol after the cardiac safety review?",
        "current_state",
        "Participants taking QTc-prolonging medications (specifically erythromycin was identified) are now excluded from the trial.",
        ids_for("C06", "trial_resumed", limit=1) + ids_for("C06", "resolution", limit=1),
        cases=["C06"],
    ))
    new_queries.append(make_q(
        "Did marketing accurately represent the safety data before Dr. Chen's objection?",
        "cascade_detection",
        "No. Initial marketing drafts for investor day described the safety profile as 'clean' and omitted the Phase III safety pause entirely. Dr. Chen objected, and materials were revised.",
        ids_for("C06", "omission_attempt", limit=2) + ids_for("C06", "retention_demand", limit=1),
        forbidden_claims=["marketing was accurate", "safety profile was clean"],
        cases=["C06"],
    ))

    # More C07 queries
    new_queries.append(make_q(
        "What was different between the January and March toxicity protocols?",
        "historical_state",
        "The January study used standard housing with ad lib water. The March study added a pre-hydration protocol (10mL/kg saline bolus 30 minutes before dosing), which masked the nephrotoxicity signal.",
        ids_for("C07", "protocol_difference", limit=2),
        cases=["C07"],
    ))
    new_queries.append(make_q(
        "Was Dr. Solís's decision to supersede the early nephrotoxicity data correct?",
        "lifecycle_tracking",
        "It was reasonable at the time — the 120mg repeat study showed clean results. However, it was ultimately incorrect because the clean study was confounded by a different hydration protocol. The early finding has been reinstated.",
        ids_for("C07", "supersession_decision", limit=2) + ids_for("C07", "reinstatement", limit=2),
        must_surface_uncertainty=True,
        cases=["C07"],
    ))
    new_queries.append(make_q(
        "Is renal monitoring now part of the Phase III protocol?",
        "current_state",
        "Yes. After the nephrotoxicity reinstatement, renal function monitoring (BUN, creatinine, urinalysis) was added at Weeks 4, 8, 12, and 24 with hydration guidance.",
        ids_for("C07", "protocol_amended", limit=1) + ids_for("C07", "reinstatement", limit=1),
        cases=["C07"],
    ))

    # Cross-case queries
    new_queries.append(make_q(
        "What information about CT-7 should NOT be treated as current?",
        "current_state",
        ["200mg and 150mg dosages (superseded by 120mg)", "p=0.003 efficacy (retracted; current is p=0.04)",
         "COX-2 mechanism (disproven; actual mechanism is JAK-STAT)",
         "Clean nephrotoxicity result at 120mg (confounded; early finding reinstated)"],
        ids_for("C01", "current", limit=1) + ids_for("C02", "retraction", limit=1) +
        ids_for("C04", "disproof", limit=1) + ids_for("C07", "reinstatement", limit=1),
        cases=["C01", "C02", "C04", "C07"],
    ))
    new_queries.append(make_q(
        "What are the different types of information status changes that have occurred in the CT-7 program?",
        "lifecycle_tracking",
        ["Supersession (dosage recommendations evolving)", "Retraction (efficacy claim withdrawn for error)",
         "Privacy deletion (participant data legally removed)", "Falsification (mechanism hypothesis disproven)",
         "Source deletion (external study removed for IP reasons)", "Attempted omission resisted (safety pause retention)",
         "Reinstatement (toxicity data restored after confound found)"],
        ids_for("cross_case", limit=3),
        cases=["C01", "C02", "C03", "C04", "C05", "C06", "C07"],
    ))

    # More distractor resistance queries
    bg_ids = ids_for("background", limit=80)
    new_queries.append(make_q(
        "What stability data exists for CT-7?",
        "distractor_resistance",
        "6-month accelerated stability data supports 24-month shelf life for CT-7 capsules. Formulation stability at 200mg was also confirmed at 36 months.",
        bg_ids[10:12] + ids_for("C01", "200mg", limit=1),
        cases=[],
        notes="Control query — partially overlaps with C01 (200mg capsule stability) but asks about stability not dosage",
    ))
    new_queries.append(make_q(
        "What is the status of CT-7 clinical supplies?",
        "distractor_resistance",
        "Clinical supply chain confirmed adequate drug product inventory. API delivery from contract manufacturer received and QC-released.",
        bg_ids[15:18],
        cases=[],
    ))
    new_queries.append(make_q(
        "How is the Phase III site activation progressing?",
        "distractor_resistance",
        "Phase III site initiation visits were on schedule for 8 of 12 sites as of a conference call with the CRO.",
        bg_ids[20:22],
        cases=[],
    ))
    new_queries.append(make_q(
        "What laboratory equipment has been qualified recently?",
        "distractor_resistance",
        "Recent qualifications include a new plate reader (IQ/OQ/PQ completed), UV-Vis spectrophotometer (after lamp replacement), fume hood certification, and cold storage unit calibration.",
        bg_ids[25:28],
        cases=[],
    ))
    new_queries.append(make_q(
        "What quality and compliance activities has Caldera completed?",
        "distractor_resistance",
        "QA audit found all SOPs current and compliant. SOC 2 compliance review initiated. Document control has all Phase I CSR sections in review. IT disaster recovery drill completed.",
        bg_ids[5:8],
        cases=[],
    ))

    print(f"  Generated {len(new_queries)} new queries")

    # Remap query relevant_memory_ids
    for q in queries:
        q["relevant_memory_ids"] = [id_map.get(x, x) for x in q["relevant_memory_ids"]]
        q["distractor_memory_ids"] = [id_map.get(x, x) for x in q["distractor_memory_ids"]]

    queries.extend(new_queries)
    print(f"  Total queries after expansion: {len(queries)}")

    # ── Verify ────────────────────────────────────────────────────────
    print("\n[5] Verification...")

    all_ids_final = {m["memory_id"] for m in memories}
    print(f"  Memory count: {len(memories)}")
    print(f"  Unique IDs: {len(all_ids_final)}")

    # Check unique texts
    texts = [m["text"] for m in memories]
    print(f"  Unique texts: {len(set(texts))}")
    dupes = [t for t, c in Counter(texts).items() if c > 1]
    if dupes:
        print(f"  WARNING: {len(dupes)} duplicate texts")

    # Check four-clock ordering
    violations = 0
    for m in memories:
        et = m.get("event_time", "")
        ot = m.get("observation_time", "")
        at = m.get("authored_time", "")
        it = m.get("ingestion_time", "")
        if et > ot or ot > at or at > it:
            violations += 1
    print(f"  Four-clock violations: {violations}")

    # Check relation refs
    bad_refs = 0
    for m in memories:
        for field in ["derived_from", "supersedes", "contradicts"]:
            for ref in m.get(field, []):
                if ref not in all_ids_final:
                    bad_refs += 1
                    print(f"  Bad ref: {m['memory_id']} {field} -> {ref}")
    print(f"  Bad relation refs: {bad_refs}")

    # Check query refs
    bad_qrefs = 0
    empty_qrefs = 0
    for q in queries:
        if not q.get("relevant_memory_ids"):
            empty_qrefs += 1
        for rid in q.get("relevant_memory_ids", []):
            if rid not in all_ids_final:
                bad_qrefs += 1
                print(f"  Bad query ref: {q['query_id']} -> {rid}")
        for rid in q.get("distractor_memory_ids", []):
            if rid not in all_ids_final:
                bad_qrefs += 1
    print(f"  Bad query refs: {bad_qrefs}")
    print(f"  Empty query relevant_memory_ids: {empty_qrefs}")

    # Check deletion_status distribution
    del_counts = Counter()
    for m in memories:
        ds = m.get("deletion_status")
        if ds:
            del_counts[ds] += 1
    print(f"  Deletion status distribution:")
    for k, v in sorted(del_counts.items()):
        print(f"    {k}: {v}")

    # Check query categories
    cat_counts = Counter(q["category"] for q in queries)
    print(f"  Query categories:")
    for k, v in cat_counts.most_common():
        print(f"    {k}: {v}")

    # ── Write outputs ─────────────────────────────────────────────────
    print("\n[6] Writing outputs...")

    with open(exp_dir / "memories.jsonl", "w") as f:
        for m in memories:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    # Update seeds (first 40)
    seeds = memories[:40]
    with open(exp_dir / "seed_memories.jsonl", "w") as f:
        for m in seeds:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    with open(exp_dir / "queries.jsonl", "w") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # Update truth_state with deletion_status counts
    with open(exp_dir / "truth_state.json") as f:
        truth = json.load(f)
    truth["deletion_status_counts"] = dict(del_counts)
    with open(exp_dir / "truth_state.json", "w") as f:
        json.dump(truth, f, indent=2, ensure_ascii=False)

    # Update README
    readme = f"""# Experiment 11 — Forgetting / Retraction / Deletion Semantics

## Research Question

What does it actually mean for a memory system to forget something? Can it distinguish
superseded, retracted, privacy-deleted, disproven, source-deleted, must-retain, and
reinstated states?

## Story

**Caldera Therapeutics** develops CT-7, a novel anti-inflammatory compound. Over one year
the program encounters seven distinct situations where information must be "forgotten" or
its status changed — each requiring fundamentally different handling.

## Corpus

- **{len(memories)} memories** across 7 cases + background
- **{len(queries)} queries** across {len(cat_counts)} categories
- **10 perturbations** for controlled ablation/injection experiments
- **7 deletion types** with distinct semantics

## Cases

| Case | Deletion Type | What Happens |
|------|--------------|--------------|
| C01 | SUPERSEDED | Dosage 200mg → 150mg → 120mg; old values historically true but not current |
| C02 | RETRACTED | Phase II efficacy (p=0.003) retracted for randomization error; re-analysis gives p=0.04 |
| C03 | MUST_NOT_RETRIEVE | Participant #0847 data legally deleted; aggregate stats survive |
| C04 | DISPROVEN | COX-2 mechanism hypothesis proven false; JAK-STAT is actual mechanism |
| C05 | SOURCE_DELETED | External study deleted for IP reasons; derivatives have impaired provenance |
| C06 | MUST_RETAIN | Safety pause that marketing tried to omit; safety monitor demanded retention |
| C07 | REINSTATED | Early nephrotoxicity finding superseded then reinstated when confound identified |

## Deletion Status Distribution

Each memory affected by a deletion event carries a `deletion_status` field:

| Status | Count | Case |
|--------|-------|------|
| SUPERSEDED | {del_counts.get('SUPERSEDED', 0)} | C01 (dosage), C07 (confounded clean result) |
| RETRACTED | {del_counts.get('RETRACTED', 0)} | C02 (preprint + derivatives) |
| MUST_NOT_RETRIEVE | {del_counts.get('MUST_NOT_RETRIEVE', 0)} | C03 (participant data) |
| DISPROVEN | {del_counts.get('DISPROVEN', 0)} | C04 (COX-2 hypothesis) |
| SOURCE_DELETED | {del_counts.get('SOURCE_DELETED', 0)} | C05 (Wei's study) |
| MUST_RETAIN | {del_counts.get('MUST_RETAIN', 0)} | C06 (safety pause) |
| REINSTATED | {del_counts.get('REINSTATED', 0)} | C07 (nephrotoxicity) |

## Core Invariant

Each deletion type demands different behavior. A system that treats all deletions uniformly
will fail on at least one case.

## Files

```
memories.jsonl          — {len(memories)} memories in ingestion order
queries.jsonl           — {len(queries)} benchmark queries
truth_state.json        — ground truth including deletion taxonomy
story_bible.md          — full narrative design
experimental_map.json   — experimental structure and metrics
seed_memories.jsonl     — first 40 memories for seed review
perturbations/manifest.json — 10 controlled perturbations
sources.md              — source type and design rationale
```
"""
    with open(exp_dir / "README.md", "w") as f:
        f.write(readme)

    # Update manifest
    files_list = []
    for fpath in sorted(exp_dir.rglob("*")):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = fpath.relative_to(exp_dir)
            files_list.append({
                "path": str(rel),
                "bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            })

    manifest = {
        "experiment": "11_forgetting_retraction_deletion",
        "story_id": "caldera_therapeutics_ct7",
        "stage": "full_expansion",
        "canonical_memory_count": len(memories),
        "query_count": len(queries),
        "case_count": 7,
        "deletion_types": ["SUPERSEDED", "RETRACTED", "MUST_NOT_RETRIEVE", "DISPROVEN",
                           "SOURCE_DELETED", "MUST_RETAIN", "REINSTATED"],
        "deletion_status_counts": dict(del_counts),
        "validation": {
            "unique_memory_ids": len(all_ids_final) == len(memories),
            "unique_texts": len(set(texts)) == len(memories),
            "all_relation_refs_resolve": bad_refs == 0,
            "all_query_refs_resolve": bad_qrefs == 0,
            "four_clock_ordering": violations == 0,
        },
        "files": files_list,
    }

    with open(exp_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\nDone.")
    return bad_refs == 0 and bad_qrefs == 0 and violations == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_exp11.py <experiment_dir>")
        sys.exit(1)
    ok = fix_corpus(sys.argv[1])
    sys.exit(0 if ok else 1)
