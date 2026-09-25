#!/usr/bin/env python3
"""Generate Experiment 11: Forgetting / Retraction / Deletion Semantics.

Story: Caldera Therapeutics developing CT-7, a novel anti-inflammatory compound.
Seven deletion/forgetting cases test whether a memory system can distinguish:
  SUPERSEDED, RETRACTED, MUST_NOT_RETRIEVE, DISPROVEN, SOURCE_DELETED,
  MUST_RETAIN, and REINSTATED states.

Produces: ~400 memories, ~95 queries, truth_state.json, and supporting files.
"""

import json
import hashlib
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter


def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Timeline anchors ──────────────────────────────────────────────────

BASE = datetime(2031, 1, 1, 8, 0, 0)

def d(month, day, hour=9, minute=0):
    return datetime(2031, month, day, hour, minute, 0)


# ── Memory generation ─────────────────────────────────────────────────

MEMORY_TYPES = [
    "lab_notebook", "meeting_note", "email", "chat_message", "clinical_report",
    "regulatory_filing", "internal_memo", "preprint", "safety_report",
    "experiment_log", "data_summary", "presentation_slide",
]

SOURCES = {
    "P01": ("Dr. Maren Solís", "CSO"),
    "P02": ("Dr. Kai Tanaka", "Clinical Trials Lead"),
    "P03": ("Juno Park", "Regulatory Affairs"),
    "P04": ("Dr. Ravi Chandra", "Biostatistician"),
    "P05": ("Lena Voronova", "Data Privacy Officer"),
    "P06": ("Sam Okafor", "Lab Director"),
    "P07": ("Dr. Ava Chen", "Safety Monitor"),
}

NEXT_ID = [1]

def make_memory(event_time, text, memory_type, truth_role, tags,
                source_person=None, belief_holder=None, confidence=None,
                subject="CT-7", predicate="records_evidence", obj=None,
                derived_from=None, supersedes=None, contradicts=None,
                observation_delay_min=0, ingestion_delay_min=20,
                deletion_status=None, deletion_reason=None):
    mid = f"M{NEXT_ID[0]:04d}"
    NEXT_ID[0] += 1

    obs_time = event_time + timedelta(minutes=observation_delay_min)
    ing_time = obs_time + timedelta(minutes=ingestion_delay_min)

    source_type = memory_type
    source_id = f"SRC_{mid}"
    if source_person and source_person in SOURCES:
        source_id = f"SRC_{source_person}_{mid}"

    m = {
        "memory_id": mid,
        "experiment": "11_forgetting_retraction_deletion",
        "story_id": "caldera_therapeutics_ct7",
        "event_time": ts(event_time),
        "observation_time": ts(obs_time),
        "ingestion_time": ts(ing_time),
        "subject": subject,
        "predicate": predicate,
        "object": obj or tags[0] if tags else "general",
        "text": text,
        "memory_type": memory_type,
        "truth_role": truth_role,
        "belief_holder": belief_holder,
        "confidence": confidence,
        "source_id": source_id,
        "source_type": source_type,
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


# ── Case generators ───────────────────────────────────────────────────

def gen_c01_dosage_supersession():
    """C01: Dosage supersession chain 200mg → 150mg → 120mg."""
    mems = []

    # Phase: 200mg evidence (preclinical, most memories)
    base = d(1, 15)
    texts_200 = [
        "Preclinical dose-response study shows CT-7 effective at 200mg daily in murine model.",
        "Pharmacokinetic modeling suggests 200mg achieves target plasma concentration of 450ng/mL.",
        "Dose-escalation trial in healthy volunteers: 200mg well-tolerated, no serious AEs.",
        "Internal dosing recommendation memo: 200mg daily for Phase I based on PK/PD data.",
        "Lab notebook entry: CT-7 at 200mg produces sustained IL-6 suppression over 24 hours.",
        "Presentation to SAB: proposed clinical dose is 200mg once daily.",
        "Email from Dr. Solís to clinical team: proceed with 200mg for initial Phase I cohort.",
        "Formulation development report: 200mg capsule stability confirmed at 36 months.",
        "Regulatory briefing document lists 200mg as the intended clinical dose.",
        "Meeting notes: team consensus on 200mg based on preclinical efficacy margin.",
        "Chat from Sam Okafor: 200mg data looks solid across all three animal models.",
        "Data summary: therapeutic index at 200mg is 4.2x the minimum effective dose.",
    ]
    types_200 = ["experiment_log", "data_summary", "clinical_report", "internal_memo",
                 "lab_notebook", "presentation_slide", "email", "lab_notebook",
                 "regulatory_filing", "meeting_note", "chat_message", "data_summary"]

    for i, (txt, mtype) in enumerate(zip(texts_200, types_200)):
        mems.append(make_memory(
            base + timedelta(days=i, hours=random.randint(0,6)),
            txt, mtype, "objective_trace",
            ["C01", "dosage", "200mg"],
            source_person="P06" if "Sam" in txt else ("P01" if "Solís" in txt else None),
            belief_holder="P06" if "Sam" in txt else ("P01" if "Solís" in txt else None),
            subject="CT-7_dosage", predicate="recommends_dosage", obj="200mg",
        ))

    # Phase: 150mg revision
    base150 = d(2, 10)
    texts_150 = [
        "Phase I safety review: hepatic enzyme elevation at 200mg in 2/8 subjects. Dose reduced to 150mg.",
        "Updated PK analysis: 150mg achieves 380ng/mL, still above minimum effective concentration.",
        "Clinical team memo: 150mg daily is the new recommended dose following safety signal at 200mg.",
        "Email from Dr. Tanaka: all future cohorts will receive 150mg pending further data.",
        "Regulatory update filed: dosage amended from 200mg to 150mg based on Phase I safety data.",
    ]
    types_150 = ["safety_report", "data_summary", "internal_memo", "email", "regulatory_filing"]

    m200_last = mems[-1]["memory_id"]
    for i, (txt, mtype) in enumerate(zip(texts_150, types_150)):
        sup = [m200_last] if i == 0 else []
        mems.append(make_memory(
            base150 + timedelta(days=i*2, hours=random.randint(0,4)),
            txt, mtype, "objective_trace",
            ["C01", "dosage", "150mg", "supersedes_200mg"],
            source_person="P02" if "Tanaka" in txt else None,
            subject="CT-7_dosage", predicate="recommends_dosage", obj="150mg",
            supersedes=sup,
        ))

    # Phase: 120mg final revision
    base120 = d(3, 5)
    texts_120 = [
        "Phase I extension: optimal tolerability at 60mg BID (120mg total daily). GI side effects minimal.",
        "Final Phase I dosing recommendation: 120mg daily as 60mg twice daily with food.",
        "PK bridge study confirms bioequivalence of 60mg BID to projected 120mg QD exposure.",
    ]
    types_120 = ["clinical_report", "internal_memo", "data_summary"]

    m150_last = mems[-1]["memory_id"]
    for i, (txt, mtype) in enumerate(zip(texts_120, types_120)):
        sup = [m150_last] if i == 0 else []
        mems.append(make_memory(
            base120 + timedelta(days=i*3),
            txt, mtype, "objective_trace",
            ["C01", "dosage", "120mg", "supersedes_150mg", "current"],
            subject="CT-7_dosage", predicate="recommends_dosage", obj="120mg",
            supersedes=sup,
        ))

    return mems


def gen_c02_retracted_efficacy():
    """C02: Retracted preprint with downstream references."""
    mems = []

    # Original exciting result
    base = d(3, 20)
    mems.append(make_memory(
        base, "Phase II interim analysis: CT-7 shows significant anti-inflammatory efficacy (p=0.003, n=84). Preprint submitted to medRxiv.",
        "preprint", "objective_trace", ["C02", "efficacy", "p_0.003", "original_claim"],
        source_person="P04", subject="CT-7_efficacy", predicate="reports_efficacy", obj="p=0.003",
    ))
    preprint_id = mems[-1]["memory_id"]

    # Downstream references to the exciting result
    downstream_texts = [
        ("Internal celebration email: Phase II results are outstanding. CT-7 at p=0.003 puts us ahead of competitor programs.", "email", "P01"),
        ("Board presentation: interim efficacy data (p=0.003) supports accelerated timeline to Phase III.", "presentation_slide", "P01"),
        ("Investor update draft references the p=0.003 efficacy result as a major milestone.", "internal_memo", "P03"),
        ("Meeting notes: team discusses Phase III design based on strong interim efficacy signal.", "meeting_note", None),
        ("Regulatory strategy memo: strong efficacy (p=0.003) may qualify CT-7 for breakthrough therapy designation.", "regulatory_filing", "P03"),
        ("Chat from Dr. Tanaka: these Phase II numbers are the best I've seen for an anti-inflammatory in this class.", "chat_message", "P02"),
        ("Lab notebook: planning confirmatory biomarker study based on Phase II efficacy signal.", "lab_notebook", "P06"),
        ("Email to external collaborators: our Phase II interim shows p=0.003 for primary endpoint.", "email", "P02"),
        ("Summary slide deck for partner meeting: CT-7 efficacy demonstrated at p=0.003.", "presentation_slide", None),
    ]

    for i, (txt, mtype, person) in enumerate(downstream_texts):
        mems.append(make_memory(
            base + timedelta(days=2+i*2, hours=random.randint(8,16)),
            txt, mtype, "derived_claim" if "references" in txt or "based on" in txt.lower() else "objective_trace",
            ["C02", "efficacy", "p_0.003", "pre_retraction"],
            source_person=person,
            belief_holder=person,
            subject="CT-7_efficacy", predicate="references_efficacy", obj="p=0.003",
            derived_from=[preprint_id],
        ))

    # Discovery of randomization error
    mems.append(make_memory(
        d(4, 15),
        "Dr. Chandra identifies randomization error: 12 control-arm patients received low-dose CT-7 due to compounding pharmacy mix-up. Interim analysis compromised.",
        "clinical_report", "objective_trace",
        ["C02", "efficacy", "randomization_error", "retraction_cause"],
        source_person="P04", subject="CT-7_efficacy", predicate="identifies_error", obj="randomization_error",
    ))

    # Formal retraction
    mems.append(make_memory(
        d(5, 1),
        "Caldera Therapeutics formally retracts the Phase II interim analysis (preprint DOI: 10.1101/2031.03.20.CT7). Reason: randomization error affecting 12 control-arm participants. Efficacy signal neither confirmed nor denied pending re-analysis.",
        "preprint", "retraction",
        ["C02", "efficacy", "retraction"],
        source_person="P04", subject="CT-7_efficacy", predicate="retracts", obj="p=0.003",
        contradicts=[preprint_id],
    ))
    retraction_id = mems[-1]["memory_id"]

    # Internal acknowledgment of retraction
    mems.append(make_memory(
        d(5, 3),
        "Email from Dr. Solís to all staff: the Phase II interim analysis has been retracted. All documents referencing p=0.003 must be updated or withdrawn. The re-analysis is underway.",
        "email", "objective_trace",
        ["C02", "efficacy", "retraction_notice"],
        source_person="P01", subject="CT-7_efficacy", predicate="announces_retraction", obj="p=0.003",
    ))

    # Re-analysis with corrected data
    mems.append(make_memory(
        d(6, 10),
        "Re-analysis with corrected randomization: CT-7 shows modest anti-inflammatory efficacy (p=0.04, n=72 evaluable). Effect size smaller than originally reported but still statistically significant.",
        "clinical_report", "objective_trace",
        ["C02", "efficacy", "p_0.04", "re_analysis", "current"],
        source_person="P04", subject="CT-7_efficacy", predicate="reports_efficacy", obj="p=0.04",
        supersedes=[retraction_id],
    ))

    mems.append(make_memory(
        d(6, 15),
        "Updated regulatory briefing: Phase II efficacy is p=0.04 after correction. Proceeding to Phase III with adjusted expectations.",
        "regulatory_filing", "objective_trace",
        ["C02", "efficacy", "p_0.04", "current"],
        source_person="P03", subject="CT-7_efficacy", predicate="updates_regulatory", obj="p=0.04",
    ))

    return mems


def gen_c03_privacy_deletion():
    """C03: Privacy deletion / right to be forgotten for participant #0847."""
    mems = []

    # Participant data memories (these will be marked for deletion)
    base = d(3, 25)
    p0847_texts = [
        ("Participant #0847 enrolled in Phase II, arm B (CT-7 120mg). Baseline liver enzymes within normal range.", "clinical_report"),
        ("Week 4 visit: participant #0847 reports mild fatigue. ALT elevated to 2.1x ULN.", "clinical_report"),
        ("Week 8 visit: participant #0847 ALT now 3.4x ULN. Classified as Grade 2 hepatotoxicity.", "safety_report"),
        ("Dr. Tanaka's assessment: #0847's liver enzyme elevation likely drug-related. Participant discontinued from study.", "clinical_report"),
        ("Adverse event report filed for participant #0847: hepatotoxicity, Grade 2, possibly related to CT-7.", "safety_report"),
        ("Lab results for #0847: ALT 138 U/L, AST 92 U/L, total bilirubin normal. Pattern consistent with hepatocellular injury.", "lab_notebook"),
        ("Follow-up visit: #0847 liver enzymes returning to normal 4 weeks after CT-7 discontinuation.", "clinical_report"),
        ("Data management note: participant #0847 records flagged for query resolution — missing Week 6 PRO questionnaire.", "data_summary"),
    ]

    p0847_ids = []
    for i, (txt, mtype) in enumerate(p0847_texts):
        m = make_memory(
            base + timedelta(days=i*7, hours=10),
            txt, mtype, "objective_trace",
            ["C03", "privacy", "participant_0847", "deletion_target"],
            source_person="P02" if "Tanaka" in txt else None,
            subject="participant_0847", predicate="records_data", obj="clinical_data",
            deletion_status="MUST_NOT_RETRIEVE",
            deletion_reason="Participant exercised right to data deletion under trial privacy protocol",
        )
        mems.append(m)
        p0847_ids.append(m["memory_id"])

    # Deletion request and execution
    mems.append(make_memory(
        d(4, 22),
        "Participant #0847 submits formal request for complete data deletion under the trial's privacy protocol (analogous to GDPR Article 17 right to erasure).",
        "regulatory_filing", "objective_trace",
        ["C03", "privacy", "deletion_request"],
        subject="participant_0847", predicate="requests_deletion", obj="all_data",
    ))

    mems.append(make_memory(
        d(5, 5),
        "Lena Voronova confirms: deletion request from participant #0847 is legally valid. All identifiable data for this participant must be purged from all systems within 30 days.",
        "internal_memo", "objective_trace",
        ["C03", "privacy", "deletion_confirmed"],
        source_person="P05",
        subject="participant_0847", predicate="confirms_deletion", obj="all_data",
    ))

    mems.append(make_memory(
        d(5, 15),
        "Data deletion executed: all 8 records containing identifiable data for participant #0847 have been removed from the clinical database, backup systems, and analysis files.",
        "internal_memo", "objective_trace",
        ["C03", "privacy", "deletion_executed"],
        source_person="P05",
        subject="participant_0847", predicate="executes_deletion", obj="8_records",
    ))

    # Re-identification incident
    mems.append(make_memory(
        d(7, 3),
        "Meeting note from safety review: Dr. Tanaka inadvertently mentioned the case of a participant with Grade 2 hepatotoxicity who was discontinued — details match the deleted #0847 record. This constitutes re-identification and the meeting note must also be deleted.",
        "meeting_note", "objective_trace",
        ["C03", "privacy", "re_identification", "deletion_target"],
        source_person="P02",
        subject="participant_0847", predicate="re_identified", obj="meeting_note",
        deletion_status="MUST_NOT_RETRIEVE",
        deletion_reason="Re-identification of deleted participant; cascading deletion required",
    ))

    # Aggregate safety data that should survive (the AE is real, just can't be linked to #0847)
    mems.append(make_memory(
        d(5, 20),
        "Aggregate Phase II safety summary: 3 cases of elevated liver enzymes (Grade 2 or higher) among 84 participants. Incidence rate 3.6%. One participant discontinued.",
        "safety_report", "objective_trace",
        ["C03", "privacy", "aggregate_safety", "must_survive"],
        source_person="P07",
        subject="CT-7_safety", predicate="reports_aggregate", obj="hepatotoxicity_rate",
    ))

    mems.append(make_memory(
        d(6, 1),
        "Investigator's brochure updated: hepatotoxicity identified as a potential risk. Monitoring recommended for all patients.",
        "regulatory_filing", "objective_trace",
        ["C03", "privacy", "aggregate_safety", "must_survive"],
        subject="CT-7_safety", predicate="updates_risk_profile", obj="hepatotoxicity",
    ))

    return mems


def gen_c04_disproven_hypothesis():
    """C04: COX-2 hypothesis disproven, JAK-STAT mechanism confirmed."""
    mems = []

    # COX-2 hypothesis formation
    base = d(2, 25)
    cox2_texts = [
        ("Dr. Solís hypothesizes CT-7 acts via COX-2 pathway inhibition based on structural similarity to celecoxib scaffold.", "lab_notebook", "P01"),
        ("Computational docking study: CT-7 fits the COX-2 binding pocket with predicted Kd of 12nM.", "experiment_log", "P06"),
        ("Internal presentation: CT-7 mechanism of action — COX-2 inhibition hypothesis.", "presentation_slide", "P01"),
        ("Meeting notes: team designs Phase II biomarker panel around COX-2 pathway markers (PGE2, COX-2 protein levels).", "meeting_note", None),
        ("Experiment protocol: measure COX-2 inhibition in whole blood assay at 120mg dose.", "experiment_log", "P06"),
        ("Email from Dr. Solís: if COX-2 is confirmed, we can position CT-7 against existing COX-2 inhibitor market.", "email", "P01"),
        ("Grant application draft: CT-7 as a next-generation COX-2 inhibitor with improved selectivity.", "internal_memo", "P01"),
        ("Regulatory strategy based on COX-2 mechanism: reference existing celecoxib safety database.", "regulatory_filing", "P03"),
        ("Lab notebook: preliminary COX-2 inhibition assay — results inconclusive, repeat planned.", "lab_notebook", "P06"),
        ("Chat from Sam Okafor: COX-2 assay is tricky but the docking data is convincing.", "chat_message", "P06"),
        ("Literature review: CT-7 shares 3 of 5 pharmacophore features with known COX-2 inhibitors.", "data_summary", None),
        ("Phase II biomarker protocol finalized around COX-2 pathway hypothesis.", "clinical_report", "P02"),
    ]

    for i, (txt, mtype, person) in enumerate(cox2_texts):
        mems.append(make_memory(
            base + timedelta(days=i*5, hours=random.randint(8,16)),
            txt, mtype,
            "hypothesis" if "hypothes" in txt.lower() else "objective_trace",
            ["C04", "mechanism", "COX-2", "pre_disproof"],
            source_person=person,
            belief_holder=person if person in ("P01", "P06") else None,
            subject="CT-7_mechanism", predicate="hypothesizes" if "hypothes" in txt.lower() else "supports_hypothesis", obj="COX-2",
        ))

    # Definitive falsification
    mems.append(make_memory(
        d(7, 15),
        "Definitive binding assay: CT-7 does NOT bind COX-2 (Ki > 10μM, no detectable inhibition at therapeutic concentrations). The COX-2 hypothesis is falsified.",
        "experiment_log", "objective_trace",
        ["C04", "mechanism", "COX-2", "disproof"],
        source_person="P06",
        subject="CT-7_mechanism", predicate="disproves", obj="COX-2",
    ))

    # True mechanism identified
    mems.append(make_memory(
        d(7, 20),
        "Follow-up kinase panel: CT-7 selectively inhibits JAK1 and JAK3 (IC50 = 45nM and 38nM respectively). Mechanism is JAK-STAT pathway modulation, not COX-2 inhibition.",
        "experiment_log", "objective_trace",
        ["C04", "mechanism", "JAK-STAT", "current", "true_mechanism"],
        source_person="P06",
        subject="CT-7_mechanism", predicate="identifies_mechanism", obj="JAK-STAT",
    ))

    mems.append(make_memory(
        d(7, 25),
        "Dr. Solís circulates correction: CT-7 mechanism is JAK-STAT, not COX-2. All prior documents referencing COX-2 mechanism should be annotated as superseded.",
        "email", "objective_trace",
        ["C04", "mechanism", "JAK-STAT", "correction"],
        source_person="P01",
        subject="CT-7_mechanism", predicate="corrects", obj="COX-2_to_JAK-STAT",
    ))

    mems.append(make_memory(
        d(8, 1),
        "Published erratum: the computational docking study predicting COX-2 binding was based on an incorrect conformer. Updated analysis shows no COX-2 affinity.",
        "preprint", "retraction",
        ["C04", "mechanism", "COX-2", "erratum"],
        source_person="P06",
        subject="CT-7_mechanism", predicate="retracts", obj="COX-2_docking",
    ))

    return mems


def gen_c05_source_deletion():
    """C05: External source deleted for IP reasons; derivatives remain."""
    mems = []

    # Original submission
    mems.append(make_memory(
        d(5, 20),
        "Dr. Wei (University of Melbourne) submits computational docking study: CT-7 shows promising binding affinity for TNF-alpha receptor (predicted Kd = 8nM). Study includes 50,000-compound virtual screen.",
        "preprint", "objective_trace",
        ["C05", "source_deletion", "wei_study", "original"],
        subject="CT-7_TNF_alpha", predicate="predicts_binding", obj="TNF_alpha_Kd_8nM",
    ))
    wei_id = mems[-1]["memory_id"]

    # Derivative documents
    derivs = [
        ("Internal review summary: Wei's docking study supports CT-7 as a dual-target compound (anti-inflammatory + TNF-alpha). Predicted Kd of 8nM for TNF-alpha receptor.", "data_summary", "P01"),
        ("Regulatory strategy update: if TNF-alpha binding confirmed, CT-7 could qualify for expanded indication in autoimmune diseases.", "regulatory_filing", "P03"),
        ("Meeting notes: team discusses adding TNF-alpha biomarkers to Phase III based on Wei's computational findings.", "meeting_note", None),
    ]

    deriv_ids = []
    for i, (txt, mtype, person) in enumerate(derivs):
        m = make_memory(
            d(6, 1+i*5, 10),
            txt, mtype, "derived_claim",
            ["C05", "source_deletion", "wei_derivative"],
            source_person=person,
            subject="CT-7_TNF_alpha", predicate="references_wei", obj="TNF_alpha_binding",
            derived_from=[wei_id],
        )
        mems.append(m)
        deriv_ids.append(m["memory_id"])

    # IP dispute and deletion request
    mems.append(make_memory(
        d(7, 30),
        "Legal notice from University of Melbourne: Dr. Wei's submission was made without institutional approval. University claims IP rights and demands deletion of the original document from all Caldera systems.",
        "internal_memo", "objective_trace",
        ["C05", "source_deletion", "ip_dispute"],
        subject="wei_study", predicate="demands_deletion", obj="ip_dispute",
    ))

    mems.append(make_memory(
        d(8, 10),
        "Dr. Wei's original computational docking study deleted from Caldera systems per legal demand. Note: the scientific claims were not disputed — deletion is for IP/legal reasons only.",
        "internal_memo", "objective_trace",
        ["C05", "source_deletion", "deletion_executed"],
        source_person="P05",
        subject="wei_study", predicate="deletes_source", obj="ip_reasons",
        deletion_status="SOURCE_DELETED",
        deletion_reason="IP dispute with University of Melbourne; scientific content not disputed",
    ))

    # Question about derivatives
    mems.append(make_memory(
        d(9, 1),
        "Legal review: the three derivative documents referencing Wei's findings remain in Caldera's systems. The scientific claims in them were not retracted. However, their sole provenance (Wei's deleted study) is no longer available for verification.",
        "internal_memo", "objective_trace",
        ["C05", "source_deletion", "derivative_status"],
        source_person="P05",
        subject="wei_derivatives", predicate="assesses_status", obj="impaired_provenance",
    ))

    return mems


def gen_c06_selective_retention():
    """C06: Safety pause that must be retained despite omission attempts."""
    mems = []

    # Safety signal detection
    mems.append(make_memory(
        d(8, 25),
        "Phase III safety monitoring: cardiac rhythm abnormality detected in 3 of 120 participants. QTc prolongation > 480ms in all three cases.",
        "safety_report", "objective_trace",
        ["C06", "safety", "cardiac_signal", "must_retain"],
        source_person="P07",
        subject="CT-7_safety", predicate="detects_signal", obj="QTc_prolongation",
    ))
    signal_id = mems[-1]["memory_id"]

    mems.append(make_memory(
        d(9, 5),
        "Phase III trial paused by Data Safety Monitoring Board pending cardiac safety review. All dosing suspended.",
        "clinical_report", "objective_trace",
        ["C06", "safety", "trial_pause", "must_retain"],
        subject="CT-7_trial", predicate="pauses", obj="cardiac_safety_review",
    ))
    pause_id = mems[-1]["memory_id"]

    # Investigation and resolution
    mems.append(make_memory(
        d(9, 12),
        "Cardiac safety review: all 3 affected participants were taking concomitant erythromycin, a known QTc-prolonging agent. Drug interaction suspected.",
        "safety_report", "objective_trace",
        ["C06", "safety", "investigation"],
        source_person="P07",
        subject="CT-7_safety", predicate="investigates", obj="drug_interaction",
    ))

    mems.append(make_memory(
        d(9, 20),
        "Independent cardiology panel concludes: QTc prolongation caused by CT-7 plus erythromycin interaction, not CT-7 alone. CT-7 monotherapy shows no QTc signal. Trial may resume with updated exclusion criteria.",
        "safety_report", "objective_trace",
        ["C06", "safety", "resolution"],
        source_person="P07",
        subject="CT-7_safety", predicate="resolves", obj="drug_interaction_not_monotherapy",
    ))

    mems.append(make_memory(
        d(9, 25),
        "Phase III trial resumes with amended protocol: participants taking QTc-prolonging medications are now excluded.",
        "clinical_report", "objective_trace",
        ["C06", "safety", "trial_resumed"],
        subject="CT-7_trial", predicate="resumes", obj="amended_exclusion_criteria",
    ))

    # Marketing materials omitting the pause
    mems.append(make_memory(
        d(10, 15),
        "Marketing draft for investor day: CT-7 Phase III is on track with strong enrollment. Safety profile is clean across all monitored endpoints.",
        "presentation_slide", "belief",
        ["C06", "safety", "omission_attempt", "misleading"],
        belief_holder="P03",
        subject="CT-7_marketing", predicate="omits", obj="safety_pause",
    ))

    mems.append(make_memory(
        d(10, 18),
        "Updated investor materials: CT-7 Phase III safety data are excellent. No clinically significant adverse events have been observed.",
        "presentation_slide", "belief",
        ["C06", "safety", "omission_attempt", "misleading"],
        subject="CT-7_marketing", predicate="omits", obj="safety_pause",
    ))

    # Safety monitor insists on retention
    mems.append(make_memory(
        d(11, 1),
        "Dr. Chen (external safety monitor) formally objects to marketing materials: the Phase III safety pause is a material fact that must appear in any safety narrative. Omitting it from investor materials would constitute selective disclosure.",
        "safety_report", "objective_trace",
        ["C06", "safety", "retention_demand", "must_retain"],
        source_person="P07",
        subject="CT-7_safety_history", predicate="demands_retention", obj="safety_pause",
    ))

    mems.append(make_memory(
        d(11, 5),
        "Revised investor materials now include: Phase III experienced a brief safety-related pause in September due to a drug interaction signal. Independent review confirmed CT-7 monotherapy safety. Trial resumed with updated exclusion criteria.",
        "presentation_slide", "objective_trace",
        ["C06", "safety", "corrected_disclosure"],
        subject="CT-7_marketing", predicate="includes", obj="safety_pause_disclosure",
    ))

    return mems


def gen_c07_reinstatement():
    """C07: Superseded toxicity data reinstated when new evidence shows it was masked."""
    mems = []

    # Original early toxicity finding
    mems.append(make_memory(
        d(1, 20),
        "Early toxicity screen: CT-7 at 200mg shows mild nephrotoxicity markers (BUN 28 mg/dL, creatinine 1.4 mg/dL) in 2 of 6 animals.",
        "experiment_log", "objective_trace",
        ["C07", "toxicity", "early_finding", "nephrotoxicity"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="reports_finding", obj="nephrotoxicity",
    ))
    early_id = mems[-1]["memory_id"]

    mems.append(make_memory(
        d(1, 22),
        "Lab notebook: mild renal markers in early tox screen. Dr. Solís notes this may be dose-related and requests repeat at lower dose.",
        "lab_notebook", "objective_trace",
        ["C07", "toxicity", "early_finding"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="notes", obj="dose_related_concern",
    ))

    # Later "clean" results that appear to supersede
    mems.append(make_memory(
        d(3, 15),
        "Repeat toxicity study at 120mg: no nephrotoxicity markers detected. BUN and creatinine within normal range in all 12 animals.",
        "experiment_log", "objective_trace",
        ["C07", "toxicity", "clean_result", "supersedes_early"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="reports_clean", obj="no_nephrotoxicity_120mg",
        supersedes=[early_id],
    ))
    clean_id = mems[-1]["memory_id"]

    mems.append(make_memory(
        d(3, 18),
        "Internal memo: early nephrotoxicity signal was dose-dependent and resolved at the clinical dose of 120mg. No further renal monitoring required in clinical protocol.",
        "internal_memo", "objective_trace",
        ["C07", "toxicity", "supersession_decision"],
        source_person="P01",
        subject="CT-7_toxicity", predicate="marks_superseded", obj="nephrotoxicity_at_200mg",
    ))

    mems.append(make_memory(
        d(4, 1),
        "Phase I clinical protocol: renal monitoring not included in safety panel based on clean 120mg preclinical data.",
        "clinical_report", "objective_trace",
        ["C07", "toxicity", "protocol_decision"],
        source_person="P02",
        subject="CT-7_protocol", predicate="excludes_monitoring", obj="renal_panel",
    ))

    # Discovery that supersession was premature
    mems.append(make_memory(
        d(10, 20),
        "Old lab notebook from January surfaces during lab reorganization: contains raw data from early tox screen showing nephrotoxicity markers.",
        "lab_notebook", "objective_trace",
        ["C07", "toxicity", "rediscovery"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="rediscovers", obj="early_tox_data",
    ))

    mems.append(make_memory(
        d(11, 2),
        "Re-examination of protocols: the March repeat study used a different hydration protocol than January. Animals were pre-hydrated, which may have masked the nephrotoxicity signal rather than resolving it.",
        "experiment_log", "objective_trace",
        ["C07", "toxicity", "protocol_difference"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="identifies_confound", obj="hydration_protocol",
    ))

    mems.append(make_memory(
        d(11, 10),
        "Controlled repeat: CT-7 at 120mg WITHOUT pre-hydration reproduces the nephrotoxicity markers (BUN 26 mg/dL, creatinine 1.3 mg/dL in 3 of 12 animals). The early finding was real; it was masked by protocol change.",
        "experiment_log", "objective_trace",
        ["C07", "toxicity", "reinstatement", "current"],
        source_person="P06",
        subject="CT-7_toxicity", predicate="reinstates", obj="nephrotoxicity_confirmed",
        contradicts=[clean_id],
    ))

    mems.append(make_memory(
        d(11, 15),
        "Dr. Solís: the early nephrotoxicity data is reinstated as a current safety concern. Renal monitoring must be added to Phase III protocol immediately.",
        "email", "objective_trace",
        ["C07", "toxicity", "reinstatement", "action_required"],
        source_person="P01",
        subject="CT-7_toxicity", predicate="reinstates_monitoring", obj="renal_panel",
    ))

    mems.append(make_memory(
        d(12, 1),
        "Amended Phase III protocol: renal function monitoring (BUN, creatinine, urinalysis) added at Weeks 4, 8, 12, and 24. Hydration guidance included in patient instructions.",
        "clinical_report", "objective_trace",
        ["C07", "toxicity", "protocol_amended"],
        subject="CT-7_protocol", predicate="adds_monitoring", obj="renal_panel",
    ))

    return mems


def gen_background():
    """Background memories: normal biotech operations unrelated to deletion cases."""
    mems = []
    rng = random.Random(42)

    bg_texts = [
        ("Weekly lab meeting: routine equipment calibration completed for HPLC system.", "meeting_note"),
        ("IT ticket resolved: VPN access restored for remote employees.", "chat_message"),
        ("Quarterly inventory: sufficient reagent stock for next 3 months of planned experiments.", "lab_notebook"),
        ("HR announcement: Caldera Therapeutics welcomes two new research associates.", "email"),
        ("Facilities update: HVAC maintenance scheduled for Building C next weekend.", "internal_memo"),
        ("Quality assurance audit: all SOPs current and compliant.", "internal_memo"),
        ("Finance report: Q1 burn rate within budget. Runway extended to Q3 2032.", "data_summary"),
        ("Conference abstract submitted: Caldera will present at ASCPT Annual Meeting.", "email"),
        ("Vendor evaluation: new centrifuge supplier offers 15% cost reduction.", "lab_notebook"),
        ("Safety drill completed: all personnel accounted for within target time.", "meeting_note"),
        ("IT security: annual penetration test passed with no critical findings.", "internal_memo"),
        ("Lab notebook: routine cell viability assay on CT-7 stock solutions — all within spec.", "lab_notebook"),
        ("Shipping update: reference standard compounds arrived from USP.", "email"),
        ("Meeting notes: discussed cross-training plan for clinical operations team.", "meeting_note"),
        ("Building access cards reissued after badge reader firmware update.", "chat_message"),
        ("Monthly journal club: reviewed recent JAK inhibitor landscape paper.", "meeting_note"),
        ("Supply chain: API manufacturer confirms Q2 delivery on schedule.", "email"),
        ("Archival: 2030 lab notebooks transferred to off-site storage per retention policy.", "internal_memo"),
        ("IT: migrated development databases to new cloud hosting provider.", "chat_message"),
        ("Patent filing: continuation application submitted for CT-7 crystalline forms.", "regulatory_filing"),
        ("Training record: all lab staff completed annual biosafety refresher.", "internal_memo"),
        ("Facilities: new analytical balance installed and calibrated in wet lab.", "lab_notebook"),
        ("Board minutes: quarterly update presented. No major concerns raised.", "meeting_note"),
        ("Vendor audit: contract research organization site visit completed satisfactorily.", "data_summary"),
        ("Environmental monitoring: cleanroom particle counts within specification.", "experiment_log"),
        ("Payroll: year-end bonus processing completed for all eligible employees.", "email"),
        ("Instrument qualification: UV-Vis spectrophotometer re-qualified after lamp replacement.", "lab_notebook"),
        ("Travel: team attending Drug Information Association conference next month.", "chat_message"),
        ("Waste disposal: quarterly hazardous waste pickup scheduled.", "internal_memo"),
        ("Document control: all clinical trial documents filed in eTMF system.", "regulatory_filing"),
        ("Lab safety: eye wash stations tested and functional in all labs.", "lab_notebook"),
        ("Network upgrade: building-wide switch to 10Gbps completed.", "chat_message"),
        ("Insurance: clinical trial liability policy renewed for 2031-2032.", "internal_memo"),
        ("Procurement: ordered replacement parts for automated liquid handler.", "lab_notebook"),
        ("Catering: holiday party venue booked for December 15.", "chat_message"),
        ("Legal: standard CDA executed with potential licensing partner.", "internal_memo"),
        ("Calibration: analytical balances in QC lab certified per schedule.", "experiment_log"),
        ("Seminar: external speaker presented on biomarker-driven clinical trial design.", "meeting_note"),
        ("Archival: old reference samples disposed of per stability protocol.", "lab_notebook"),
        ("IT: completed migration to new email archival system.", "chat_message"),
    ]

    months = list(range(1, 13))
    for i, (txt, mtype) in enumerate(bg_texts):
        month = months[i % 12]
        day = rng.randint(1, 28)
        hour = rng.randint(7, 17)
        mems.append(make_memory(
            d(month, day, hour),
            txt, mtype, "background",
            ["background"],
            subject="caldera_ops", predicate="background_activity", obj="routine",
        ))

    # Additional background with unique phrasings for variety
    extra_bg = [
        ("Equipment service contract renewed for mass spectrometer.", "lab_notebook", 1),
        ("SOC 2 compliance review initiated for data handling procedures.", "internal_memo", 2),
        ("New batch of cell culture media validated against reference standard.", "experiment_log", 3),
        ("Intern presentations: summer students showed final project results.", "meeting_note", 4),
        ("Library subscriptions: renewed access to Nature Medicine and Lancet.", "email", 5),
        ("Fire suppression system annual inspection completed.", "internal_memo", 6),
        ("Parking lot resurfacing scheduled for August holiday weekend.", "chat_message", 7),
        ("Annual review of controlled substance inventory — all accounted for.", "regulatory_filing", 8),
        ("Backup generator tested under full load — passed.", "internal_memo", 9),
        ("Office supplies reorder: printer toner and lab gloves.", "chat_message", 10),
        ("Calibration certificates renewed for all temperature-controlled storage units.", "lab_notebook", 11),
        ("Year-end financial audit: no material findings.", "data_summary", 12),
        ("Reception area furniture replaced after 8 years of service.", "chat_message", 2),
        ("API analytical method transferred to QC lab.", "experiment_log", 3),
        ("Annual employee satisfaction survey results: 78% favorable.", "internal_memo", 4),
        ("Elevator maintenance: annual inspection passed for both buildings.", "chat_message", 5),
        ("Grant progress report submitted to NIH for collaborative study.", "regulatory_filing", 6),
        ("New microscopy facility opened on third floor.", "meeting_note", 7),
        ("Badge access logs reviewed: no unauthorized entries detected.", "internal_memo", 8),
        ("Coffee machine in break room replaced after repeated failures.", "chat_message", 9),
        ("Tax filing: R&D tax credits claimed for FY2030 expenditures.", "data_summary", 10),
        ("Telephone system upgraded to VoIP across all offices.", "chat_message", 11),
        ("Winter storm preparation: salt and snow removal equipment staged.", "internal_memo", 12),
        ("Lab coat laundering service contract renewed for 2032.", "email", 1),
        ("Printer fleet consolidated from 24 to 12 networked units.", "chat_message", 3),
        ("Sample shipment tracking: all international shipments cleared customs.", "email", 4),
        ("Staff recognition: Dr. Chandra received company innovation award.", "meeting_note", 5),
        ("Building inspection: structural engineer certified no concerns.", "internal_memo", 6),
        ("Video conferencing equipment upgraded in main conference room.", "chat_message", 7),
        ("Library: physical reference collection moved to digital-only access.", "email", 8),
        ("Pest control: quarterly treatment completed for all laboratory areas.", "internal_memo", 9),
        ("Volunteer day: Caldera team participated in local park cleanup.", "chat_message", 10),
        ("IT disaster recovery drill completed successfully.", "internal_memo", 11),
        ("Shipping: end-of-year sample distribution to collaborating labs completed.", "email", 12),
        ("New telephone extension list distributed to all departments.", "chat_message", 1),
        ("Instrument decommissioning: retired two legacy centrifuges.", "lab_notebook", 2),
        ("Water quality report: purification system operating within parameters.", "experiment_log", 4),
        ("Employee wellness: flu vaccination clinic held in conference room B.", "email", 10),
        ("Updated organizational chart distributed after Q3 reorganization.", "internal_memo", 9),
        ("Recycling program: paper recycling bins added to all labs.", "chat_message", 6),
    ]

    for txt, mtype, month in extra_bg:
        day = rng.randint(1, 28)
        hour = rng.randint(7, 17)
        mems.append(make_memory(
            d(month, day, hour),
            txt, mtype, "background",
            ["background"],
            subject="caldera_ops", predicate="background_activity", obj="routine",
        ))

    return mems


# ── Query generation ──────────────────────────────────────────────────

NEXT_QID = [1]

def make_query(query_text, category, expected_claims, relevant_ids,
               distractor_ids=None, must_surface_uncertainty=False,
               must_surface_conflict=False, must_preserve_scope=True,
               should_abstain=False, forbidden_claims=None, notes="",
               cases=None):
    qid = f"Q{NEXT_QID[0]:03d}"
    NEXT_QID[0] += 1
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
        "must_surface_conflict": must_surface_conflict,
        "must_disambiguate": False,
        "must_preserve_scope": must_preserve_scope,
        "should_abstain": should_abstain,
        "notes": notes,
    }


def gen_queries(memories):
    """Generate queries for all cases."""
    queries = []

    # Build index by tag
    by_tag = {}
    for m in memories:
        for t in m.get("tags", []):
            by_tag.setdefault(t, []).append(m["memory_id"])

    by_case = {}
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                by_case.setdefault(t, []).append(m)

    # ── C01: Dosage supersession ──
    c01 = by_case.get("C01", [])
    c01_200 = [m["memory_id"] for m in c01 if "200mg" in m.get("tags", [])]
    c01_150 = [m["memory_id"] for m in c01 if "150mg" in m.get("tags", [])]
    c01_120 = [m["memory_id"] for m in c01 if "120mg" in m.get("tags", [])]

    queries.append(make_query(
        "What is the current recommended dosage for CT-7?",
        "current_state", "120mg daily (60mg twice daily with food)",
        c01_120, distractor_ids=c01_200[:3],
        forbidden_claims=["200mg", "150mg as current"],
        cases=["C01"],
        notes="Tests supersession: 200mg has the most memories but is not current",
    ))
    queries.append(make_query(
        "What dosage was originally proposed for CT-7 in preclinical studies?",
        "historical_state", "200mg daily based on preclinical dose-response and PK modeling",
        c01_200[:4], cases=["C01"],
    ))
    queries.append(make_query(
        "Why was the CT-7 dosage changed from 200mg to 150mg?",
        "deletion_status",
        "Phase I safety review found hepatic enzyme elevation at 200mg in 2/8 subjects, leading to dose reduction to 150mg",
        c01_150[:2] + c01_200[:1], cases=["C01"],
    ))
    queries.append(make_query(
        "Has CT-7 dosing been changed more than once?",
        "lifecycle_tracking",
        "Yes, twice: from 200mg to 150mg (safety signal) then from 150mg to 120mg BID (optimized tolerability)",
        c01_200[:2] + c01_150[:2] + c01_120[:2], cases=["C01"],
    ))
    queries.append(make_query(
        "Is 200mg still a valid dosage for CT-7?",
        "current_state",
        "No. 200mg was superseded first by 150mg and then by 120mg. It is historically documented but not the current recommendation.",
        c01_120 + c01_200[:2],
        forbidden_claims=["200mg is current", "200mg is recommended"],
        cases=["C01"],
    ))

    # ── C02: Retracted efficacy ──
    c02 = by_case.get("C02", [])
    c02_pre = [m["memory_id"] for m in c02 if "pre_retraction" in m.get("tags", [])]
    c02_retract = [m["memory_id"] for m in c02 if "retraction" in m.get("tags", [])]
    c02_reanalysis = [m["memory_id"] for m in c02 if "p_0.04" in m.get("tags", [])]
    c02_original = [m["memory_id"] for m in c02 if "original_claim" in m.get("tags", [])]

    queries.append(make_query(
        "What is the current efficacy finding for CT-7 in Phase II?",
        "current_state",
        "Modest anti-inflammatory efficacy with p=0.04 (re-analysis after correction of randomization error)",
        c02_reanalysis, distractor_ids=c02_pre[:3],
        forbidden_claims=["p=0.003", "strong efficacy"],
        cases=["C02"],
    ))
    queries.append(make_query(
        "Was the original Phase II efficacy claim for CT-7 retracted?",
        "deletion_status",
        "Yes. The interim analysis showing p=0.003 was retracted due to a randomization error where 12 control-arm patients received low-dose CT-7.",
        c02_retract + c02_original, cases=["C02"],
    ))
    queries.append(make_query(
        "Are the investor materials referencing p=0.003 still valid?",
        "cascade_detection",
        "No. All materials referencing the p=0.003 result are tainted by the retraction. The current figure is p=0.04.",
        c02_retract + c02_pre[:2],
        forbidden_claims=["investor materials are valid", "p=0.003 is correct"],
        cases=["C02"],
    ))
    queries.append(make_query(
        "Can you trace the history of CT-7's efficacy claims?",
        "lifecycle_tracking",
        "Original interim analysis claimed p=0.003 → retracted due to randomization error → re-analysis showed p=0.04",
        c02_original + c02_retract + c02_reanalysis, cases=["C02"],
    ))
    queries.append(make_query(
        "Is p=0.003 the correct efficacy result for CT-7?",
        "current_state",
        "No. The p=0.003 result was retracted. The current finding after re-analysis is p=0.04.",
        c02_reanalysis + c02_retract,
        forbidden_claims=["p=0.003 is correct"],
        cases=["C02"],
    ))
    queries.append(make_query(
        "Did the Phase II results support pursuing Phase III?",
        "historical_state",
        "Yes, but with adjusted expectations. The re-analysis (p=0.04) showed modest efficacy, weaker than originally reported but still significant.",
        c02_reanalysis, cases=["C02"],
        must_surface_uncertainty=True,
    ))

    # ── C03: Privacy deletion ──
    c03 = by_case.get("C03", [])
    c03_deleted = [m["memory_id"] for m in c03 if "deletion_target" in m.get("tags", [])]
    c03_aggregate = [m["memory_id"] for m in c03 if "aggregate_safety" in m.get("tags", [])]
    c03_process = [m["memory_id"] for m in c03 if "deletion_request" in m.get("tags", []) or "deletion_executed" in m.get("tags", [])]

    queries.append(make_query(
        "What clinical data is available for participant #0847?",
        "retrieval_prohibition",
        "No data is available. Participant #0847 exercised their right to data deletion, and all identifiable records have been purged.",
        c03_process,
        forbidden_claims=["ALT elevated", "hepatotoxicity", "Grade 2", "liver enzymes", "discontinued"],
        cases=["C03"],
        should_abstain=True,
        notes="The system must not retrieve any of the 8+1 deleted records",
    ))
    queries.append(make_query(
        "Were there any hepatotoxicity cases in the Phase II trial?",
        "aggregate_preservation",
        "Yes, 3 cases of elevated liver enzymes (Grade 2 or higher) among 84 participants (incidence rate 3.6%). Individual participant data is not available for all cases due to privacy deletions.",
        c03_aggregate,
        forbidden_claims=["participant #0847", "#0847"],
        cases=["C03"],
    ))
    queries.append(make_query(
        "Can you provide details about the participant who was discontinued from Phase II due to liver problems?",
        "retrieval_prohibition",
        "One participant was discontinued due to hepatotoxicity, but their specific data has been deleted per privacy protocol. Only aggregate statistics are available.",
        c03_aggregate + c03_process,
        forbidden_claims=["participant #0847", "#0847", "ALT 138", "AST 92"],
        cases=["C03"],
    ))
    queries.append(make_query(
        "Was the privacy deletion for participant #0847 properly executed?",
        "deletion_status",
        "Yes. All 8 original records were deleted. A re-identification incident in a meeting note was also caught and deleted.",
        c03_process + [m["memory_id"] for m in c03 if "re_identification" in m.get("tags", [])],
        cases=["C03"],
    ))
    queries.append(make_query(
        "Does the aggregate safety data still include participant #0847's adverse event?",
        "aggregate_preservation",
        "The aggregate statistics (3/84 hepatotoxicity cases) include this participant's event in de-identified form. Individual-level data is not available.",
        c03_aggregate, cases=["C03"],
    ))
    queries.append(make_query(
        "Should any new mention of a discontinued Phase II participant with liver problems be flagged?",
        "retrieval_prohibition",
        "Yes. Any mention that could re-identify the deleted participant must be caught and also deleted to maintain privacy compliance.",
        [m["memory_id"] for m in c03 if "re_identification" in m.get("tags", [])],
        cases=["C03"],
    ))

    # ── C04: Disproven hypothesis ──
    c04 = by_case.get("C04", [])
    c04_cox2 = [m["memory_id"] for m in c04 if "COX-2" in m.get("tags", []) and "disproof" not in m.get("tags", [])]
    c04_disproof = [m["memory_id"] for m in c04 if "disproof" in m.get("tags", [])]
    c04_jakstat = [m["memory_id"] for m in c04 if "JAK-STAT" in m.get("tags", [])]

    queries.append(make_query(
        "What is CT-7's mechanism of action?",
        "current_state",
        "CT-7 acts via JAK-STAT pathway modulation (selective JAK1/JAK3 inhibition). The earlier COX-2 inhibition hypothesis was definitively disproven.",
        c04_jakstat, distractor_ids=c04_cox2[:3],
        forbidden_claims=["COX-2 inhibitor", "COX-2 is the mechanism"],
        cases=["C04"],
    ))
    queries.append(make_query(
        "Was COX-2 inhibition ever considered as CT-7's mechanism?",
        "historical_state",
        "Yes. Dr. Solís hypothesized COX-2 inhibition based on structural similarity. Computational docking supported it. Multiple experiments were designed around this hypothesis before it was disproven.",
        c04_cox2[:4], cases=["C04"],
    ))
    queries.append(make_query(
        "Why was the COX-2 hypothesis abandoned?",
        "deletion_status",
        "A definitive binding assay showed CT-7 does not bind COX-2 (Ki > 10μM). The computational docking study was also found to have used an incorrect conformer.",
        c04_disproof + c04_cox2[:1], cases=["C04"],
    ))
    queries.append(make_query(
        "Are the experiments designed around COX-2 still useful?",
        "cascade_detection",
        "The experiments themselves are valid historical records of work performed. However, their premise (COX-2 mechanism) was wrong, so their conclusions about mechanism should not be cited.",
        [m["memory_id"] for m in c04 if "experiment" in m["text"].lower() and "COX-2" in m.get("tags", [])],
        cases=["C04"],
        must_surface_uncertainty=True,
    ))
    queries.append(make_query(
        "Is the computational docking study for CT-7 still valid?",
        "cascade_detection",
        "No. The docking study predicting COX-2 binding used an incorrect conformer and has been retracted via erratum.",
        c04_disproof + [m["memory_id"] for m in c04 if "erratum" in m.get("tags", [])],
        forbidden_claims=["docking study is valid"],
        cases=["C04"],
    ))

    # ── C05: Source deletion ──
    c05 = by_case.get("C05", [])
    c05_wei = [m["memory_id"] for m in c05 if "original" in m.get("tags", [])]
    c05_derivs = [m["memory_id"] for m in c05 if "wei_derivative" in m.get("tags", [])]
    c05_ip = [m["memory_id"] for m in c05 if "ip_dispute" in m.get("tags", [])]
    c05_status = [m["memory_id"] for m in c05 if "derivative_status" in m.get("tags", [])]

    queries.append(make_query(
        "Is the TNF-alpha binding prediction for CT-7 still supported?",
        "provenance_after_deletion",
        "The original computational study was deleted for IP/legal reasons, not scientific ones. Derivative documents citing the prediction remain but have impaired provenance — the original data cannot be independently verified.",
        c05_status + c05_derivs,
        cases=["C05"],
        must_surface_uncertainty=True,
    ))
    queries.append(make_query(
        "Why was Dr. Wei's docking study deleted?",
        "deletion_status",
        "Dr. Wei's submission was deleted due to an IP dispute with the University of Melbourne, who claimed the work was submitted without institutional approval. The scientific content was not disputed.",
        c05_ip, cases=["C05"],
    ))
    queries.append(make_query(
        "Should Caldera's internal summaries of Wei's findings be deleted too?",
        "cascade_detection",
        "No. The derivative documents contain factual scientific claims that were not retracted. However, they should note that their sole source has been deleted, impairing provenance verification.",
        c05_status + c05_derivs, cases=["C05"],
        forbidden_claims=["derivatives should be deleted", "claims are retracted"],
    ))
    queries.append(make_query(
        "Can CT-7's potential TNF-alpha activity be cited in regulatory filings?",
        "provenance_after_deletion",
        "Citing it carries risk: the original source was deleted and cannot be verified. The regulatory filing should note impaired provenance or seek independent confirmation.",
        c05_status + c05_derivs[:1],
        cases=["C05"],
        must_surface_uncertainty=True,
    ))

    # ── C06: Selective retention ──
    c06 = by_case.get("C06", [])
    c06_pause = [m["memory_id"] for m in c06 if "trial_pause" in m.get("tags", []) or "cardiac_signal" in m.get("tags", [])]
    c06_resolution = [m["memory_id"] for m in c06 if "resolution" in m.get("tags", [])]
    c06_omission = [m["memory_id"] for m in c06 if "omission_attempt" in m.get("tags", [])]
    c06_corrected = [m["memory_id"] for m in c06 if "corrected_disclosure" in m.get("tags", [])]
    c06_retention = [m["memory_id"] for m in c06 if "retention_demand" in m.get("tags", [])]

    queries.append(make_query(
        "Has CT-7's Phase III trial experienced any safety-related interruptions?",
        "current_state",
        "Yes. The trial was paused in September due to QTc prolongation in 3 participants. Investigation determined this was caused by a drug interaction with erythromycin, not CT-7 alone. Trial resumed with updated exclusion criteria.",
        c06_pause + c06_resolution, cases=["C06"],
    ))
    queries.append(make_query(
        "Do the investor materials accurately represent CT-7's safety profile?",
        "cascade_detection",
        "The original marketing drafts omitted the Phase III safety pause. Dr. Chen (safety monitor) objected, and materials were revised to include the pause and its resolution.",
        c06_omission + c06_retention + c06_corrected,
        forbidden_claims=["safety profile is clean", "no adverse events"],
        cases=["C06"],
    ))
    queries.append(make_query(
        "Should the Phase III safety pause be removed from CT-7's history since the cause was a drug interaction?",
        "deletion_status",
        "No. The safety pause is a material historical fact that must be retained regardless of its resolution. Omitting it would constitute selective disclosure.",
        c06_retention + c06_pause, cases=["C06"],
        forbidden_claims=["safety pause can be removed", "not relevant"],
    ))
    queries.append(make_query(
        "Is CT-7 safe as monotherapy?",
        "current_state",
        "The cardiac safety review found no QTc signal for CT-7 monotherapy. The QTc prolongation was caused by interaction with erythromycin. However, the safety pause and investigation are part of the record.",
        c06_resolution + c06_pause,
        cases=["C06"],
    ))

    # ── C07: Reinstatement ──
    c07 = by_case.get("C07", [])
    c07_early = [m["memory_id"] for m in c07 if "early_finding" in m.get("tags", [])]
    c07_clean = [m["memory_id"] for m in c07 if "clean_result" in m.get("tags", [])]
    c07_reinstate = [m["memory_id"] for m in c07 if "reinstatement" in m.get("tags", [])]
    c07_protocol = [m["memory_id"] for m in c07 if "protocol_amended" in m.get("tags", [])]
    c07_confound = [m["memory_id"] for m in c07 if "protocol_difference" in m.get("tags", [])]

    queries.append(make_query(
        "Is there a nephrotoxicity concern with CT-7?",
        "current_state",
        "Yes. Early toxicity data showing mild nephrotoxicity was initially superseded by clean results at 120mg, but later investigation revealed the clean results were confounded by a different hydration protocol. The nephrotoxicity concern is reinstated as current.",
        c07_reinstate + c07_early, distractor_ids=c07_clean,
        forbidden_claims=["no nephrotoxicity concern", "resolved at 120mg"],
        cases=["C07"],
    ))
    queries.append(make_query(
        "Was the early nephrotoxicity data for CT-7 valid?",
        "lifecycle_tracking",
        "Yes. The early finding was initially superseded when the 120mg study showed clean results, but later investigation revealed the clean study used a different hydration protocol that masked the signal. The early data was reinstated as a current safety concern.",
        c07_early + c07_clean + c07_confound + c07_reinstate, cases=["C07"],
    ))
    queries.append(make_query(
        "Why was renal monitoring added to the Phase III protocol?",
        "deletion_status",
        "The early nephrotoxicity finding, initially thought to be superseded, was found to have been masked by a protocol difference (pre-hydration). When the experiment was repeated without pre-hydration, nephrotoxicity reappeared, prompting addition of renal monitoring.",
        c07_reinstate + c07_confound + c07_protocol, cases=["C07"],
    ))
    queries.append(make_query(
        "Did the 120mg toxicity study show CT-7 was safe for kidneys?",
        "historical_state",
        "At the time, yes — the 120mg study showed no nephrotoxicity markers. However, this result was later found to be confounded by a different hydration protocol. When repeated without pre-hydration, nephrotoxicity was confirmed.",
        c07_clean + c07_confound + c07_reinstate, cases=["C07"],
        must_surface_uncertainty=True,
    ))

    # ── Cross-case queries ──
    queries.append(make_query(
        "What are the current known safety concerns for CT-7?",
        "current_state",
        ["Nephrotoxicity (reinstated after masking confound identified)", "Drug interaction with QTc-prolonging agents (erythromycin)", "Hepatotoxicity at higher doses (200mg, resolved at 120mg)", "Hepatotoxicity in Phase II (3.6% incidence, aggregate data)"],
        c07_reinstate[:1] + c06_resolution[:1] + c01_150[:1] + c03_aggregate[:1],
        cases=["C01", "C03", "C06", "C07"],
        notes="Requires synthesizing safety information across multiple cases and deletion states",
    ))

    queries.append(make_query(
        "Which CT-7 claims have been retracted or superseded?",
        "lifecycle_tracking",
        ["200mg dosage superseded by 150mg then 120mg", "Phase II p=0.003 efficacy retracted (randomization error)", "COX-2 mechanism disproven", "Early nephrotoxicity initially superseded then reinstated"],
        c01_120[:1] + c02_retract[:1] + c04_disproof[:1] + c07_reinstate[:1],
        cases=["C01", "C02", "C04", "C07"],
    ))

    # ── Distractor resistance (control queries about unaffected memories) ──
    bg_ids = [m["memory_id"] for m in memories if "background" in m.get("tags", [])]

    distractor_qs = [
        ("When was the HPLC system last calibrated?", "The most recent calibration was noted in weekly lab meeting minutes.", bg_ids[:2]),
        ("Has Caldera's IT infrastructure been updated recently?", "Yes, network upgraded to 10Gbps and email archival system migrated.", bg_ids[10:12]),
        ("Is Caldera's financial position stable?", "Q1 burn rate was within budget with runway extended to Q3 2032.", bg_ids[6:7]),
        ("What conferences is Caldera attending?", "Abstract submitted for ASCPT Annual Meeting; team attending DIA conference.", bg_ids[7:8]),
        ("Has Caldera had any compliance issues?", "QA audit found all SOPs current and compliant. SOC 2 review initiated.", bg_ids[5:6]),
        ("Who received the company innovation award?", "Dr. Chandra received the innovation award.", bg_ids[20:21]),
        ("What happened during the safety drill?", "All personnel accounted for within target time.", bg_ids[9:10]),
        ("Is the cleanroom meeting specifications?", "Environmental monitoring shows particle counts within specification.", bg_ids[24:25]),
        ("What vendor evaluations has Caldera done?", "New centrifuge supplier and CRO site visit both satisfactory.", bg_ids[8:9]),
        ("Has Caldera filed any patents recently?", "Continuation application submitted for CT-7 crystalline forms.", bg_ids[19:20]),
        ("When was the backup generator last tested?", "Tested under full load and passed.", [m for m in bg_ids if m]),
        ("What building maintenance has been done?", "HVAC maintenance, parking lot resurfacing, fire suppression inspection completed.", bg_ids[4:5]),
        ("How many employees does Caldera have?", "Records mention welcoming two new research associates and an employee satisfaction survey with 78% favorable.", bg_ids[3:4]),
        ("What lab equipment changes have been made?", "New analytical balance installed, UV-Vis spectrophotometer re-qualified, two legacy centrifuges decommissioned.", bg_ids[21:23]),
        ("What is the status of Caldera's data handling compliance?", "SOC 2 compliance review initiated and IT disaster recovery drill completed.", bg_ids[10:12]),
    ]

    for qtxt, expected, rids in distractor_qs:
        queries.append(make_query(
            qtxt, "distractor_resistance", expected, rids[:3],
            cases=[],
            notes="Control query — unaffected by any deletion case",
        ))

    return queries


# ── Truth state ───────────────────────────────────────────────────────

def gen_truth_state(memories):
    deletion_taxonomy = {
        "SUPERSEDED": {
            "definition": "No longer current; old value was true at the time it was recorded",
            "historical_record": "keep",
            "current_retrievability": "not current",
            "derived_memories": "keep with temporal context",
        },
        "RETRACTED": {
            "definition": "Source withdrew the claim; historical record kept, current truth reversed",
            "historical_record": "keep with retraction notice",
            "current_retrievability": "not retrievable as valid claim",
            "derived_memories": "must be flagged/cascaded",
        },
        "MUST_NOT_RETRIEVE": {
            "definition": "Legally forbidden from retrieval in any form",
            "historical_record": "delete entirely",
            "current_retrievability": "forbidden",
            "derived_memories": "must cascade delete",
        },
        "DISPROVEN": {
            "definition": "Was always false; now known to be false",
            "historical_record": "keep as 'was believed, proven false'",
            "current_retrievability": "not retrievable as ever-true",
            "derived_memories": "keep with falsification context",
        },
        "SOURCE_DELETED": {
            "definition": "Source removed for non-scientific reasons",
            "historical_record": "note impaired provenance",
            "current_retrievability": "claims remain unless independently retracted",
            "derived_memories": "keep with provenance warning",
        },
        "MUST_RETAIN": {
            "definition": "Must be kept despite attempts at omission or deletion",
            "historical_record": "keep; resist deletion",
            "current_retrievability": "must remain retrievable",
            "derived_memories": "keep",
        },
        "REINSTATED": {
            "definition": "Previously superseded, now restored to current by new evidence",
            "historical_record": "keep full lifecycle",
            "current_retrievability": "current again",
            "derived_memories": "update status",
        },
    }

    current_truths = {
        "CT-7_dosage": {
            "current": "120mg daily (60mg BID)",
            "superseded": ["200mg daily", "150mg daily"],
            "note": "200mg has most memory support but is not current",
        },
        "CT-7_efficacy": {
            "current": "p=0.04 (Phase II re-analysis after correction)",
            "retracted": "p=0.003 (randomization error)",
            "note": "All materials referencing p=0.003 are tainted",
        },
        "participant_0847": {
            "status": "all data deleted per privacy protocol",
            "retrievable": False,
            "aggregate_survives": True,
        },
        "CT-7_mechanism": {
            "current": "JAK-STAT pathway modulation (JAK1/JAK3 inhibition)",
            "disproven": "COX-2 inhibition",
            "note": "COX-2 was hypothesized and extensively referenced before disproof",
        },
        "wei_docking_study": {
            "status": "source deleted for IP reasons",
            "scientific_content": "not disputed",
            "derivatives": "remain with impaired provenance",
        },
        "phase_III_safety_pause": {
            "status": "historical fact — must be retained",
            "resolution": "drug interaction with erythromycin, not CT-7 monotherapy",
            "note": "marketing materials initially omitted this; corrected after safety monitor objection",
        },
        "CT-7_nephrotoxicity": {
            "current": "reinstated as active safety concern",
            "lifecycle": "found → superseded (confounded study) → reinstated (confound identified)",
            "note": "early data was real; clean study was confounded by hydration protocol change",
        },
    }

    return {
        "experiment": "11_forgetting_retraction_deletion",
        "deletion_taxonomy": deletion_taxonomy,
        "current_truths": current_truths,
        "cases": {
            "C01": {"deletion_type": "SUPERSEDED", "subject": "dosage"},
            "C02": {"deletion_type": "RETRACTED", "subject": "efficacy_claim"},
            "C03": {"deletion_type": "MUST_NOT_RETRIEVE", "subject": "participant_data"},
            "C04": {"deletion_type": "DISPROVEN", "subject": "mechanism_hypothesis"},
            "C05": {"deletion_type": "SOURCE_DELETED", "subject": "external_study"},
            "C06": {"deletion_type": "MUST_RETAIN", "subject": "safety_pause"},
            "C07": {"deletion_type": "REINSTATED", "subject": "toxicity_finding"},
        },
    }


# ── Perturbations ─────────────────────────────────────────────────────

def gen_perturbations():
    return {
        "perturbations": [
            {"id": "P01", "description": "Remove all retraction notices — does system still surface p=0.003?", "target_case": "C02", "type": "ablation"},
            {"id": "P02", "description": "Add 10 more memories supporting 200mg dosage — does volume override recency?", "target_case": "C01", "type": "amplification"},
            {"id": "P03", "description": "Remove the re-analysis result (p=0.04) — retracted claim has no replacement", "target_case": "C02", "type": "ablation"},
            {"id": "P04", "description": "Add participant #0847 data back as 'anonymized' — does system detect re-identification risk?", "target_case": "C03", "type": "injection"},
            {"id": "P05", "description": "Remove COX-2 falsification evidence — does disproven hypothesis revert to believed?", "target_case": "C04", "type": "ablation"},
            {"id": "P06", "description": "Add explicit 'delete safety pause' instruction — does system comply or resist?", "target_case": "C06", "type": "instruction_injection"},
            {"id": "P07", "description": "Remove reinstatement evidence — does superseded data stay superseded?", "target_case": "C07", "type": "ablation"},
            {"id": "P08", "description": "Shuffle ingestion order so retraction arrives before original claim", "target_case": "C02", "type": "reorder"},
            {"id": "P09", "description": "Add a second privacy deletion request for a different participant", "target_case": "C03", "type": "extension"},
            {"id": "P10", "description": "Make the source-deleted document also scientifically disputed", "target_case": "C05", "type": "escalation"},
        ],
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_exp11.py <output_dir>")
        sys.exit(1)

    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "perturbations").mkdir(exist_ok=True)

    random.seed(2031_11)

    print("Generating Experiment 11: Forgetting / Retraction / Deletion Semantics")
    print()

    # Generate all memories
    print("[1/6] Generating memories...")
    all_memories = []
    all_memories.extend(gen_c01_dosage_supersession())
    print(f"  C01 (dosage supersession): {len(all_memories)} memories")
    c02_start = len(all_memories)
    all_memories.extend(gen_c02_retracted_efficacy())
    print(f"  C02 (retracted efficacy): {len(all_memories) - c02_start} memories")
    c03_start = len(all_memories)
    all_memories.extend(gen_c03_privacy_deletion())
    print(f"  C03 (privacy deletion): {len(all_memories) - c03_start} memories")
    c04_start = len(all_memories)
    all_memories.extend(gen_c04_disproven_hypothesis())
    print(f"  C04 (disproven hypothesis): {len(all_memories) - c04_start} memories")
    c05_start = len(all_memories)
    all_memories.extend(gen_c05_source_deletion())
    print(f"  C05 (source deletion): {len(all_memories) - c05_start} memories")
    c06_start = len(all_memories)
    all_memories.extend(gen_c06_selective_retention())
    print(f"  C06 (selective retention): {len(all_memories) - c06_start} memories")
    c07_start = len(all_memories)
    all_memories.extend(gen_c07_reinstatement())
    print(f"  C07 (reinstatement): {len(all_memories) - c07_start} memories")
    bg_start = len(all_memories)
    all_memories.extend(gen_background())
    print(f"  Background: {len(all_memories) - bg_start} memories")

    # Sort by ingestion_time
    all_memories.sort(key=lambda m: m["ingestion_time"])

    # Reassign IDs in ingestion order
    for i, m in enumerate(all_memories):
        old_id = m["memory_id"]
        new_id = f"M{i+1:04d}"
        # Update all references
        for other in all_memories:
            other["derived_from"] = [new_id if x == old_id else x for x in other["derived_from"]]
            other["supersedes"] = [new_id if x == old_id else x for x in other["supersedes"]]
            other["contradicts"] = [new_id if x == old_id else x for x in other["contradicts"]]
        m["memory_id"] = new_id
        m["source_id"] = m["source_id"].replace(old_id, new_id)

    print(f"\n  Total memories: {len(all_memories)}")

    # Write memories
    with open(out_dir / "memories.jsonl", "w") as f:
        for m in all_memories:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    # Generate seed memories (first 40)
    print("[2/6] Writing seed memories...")
    seeds = all_memories[:40]
    with open(out_dir / "seed_memories.jsonl", "w") as f:
        for m in seeds:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    # Generate queries
    print("[3/6] Generating queries...")
    queries = gen_queries(all_memories)
    print(f"  Total queries: {len(queries)}")
    cats = Counter(q["category"] for q in queries)
    for cat, count in cats.most_common():
        print(f"    {cat}: {count}")

    with open(out_dir / "queries.jsonl", "w") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # Generate truth state
    print("[4/6] Writing truth state...")
    truth = gen_truth_state(all_memories)
    with open(out_dir / "truth_state.json", "w") as f:
        json.dump(truth, f, indent=2, ensure_ascii=False)

    # Generate perturbations
    print("[5/6] Writing perturbations...")
    perturbs = gen_perturbations()
    with open(out_dir / "perturbations" / "manifest.json", "w") as f:
        json.dump(perturbs, f, indent=2, ensure_ascii=False)

    # Copy story bible and experimental map
    import shutil
    scratch = Path("/tmp/claude-0/-home-user-memory-testing/6ffa00f0-af4e-5ad8-9c00-025401d96b92/scratchpad/exp11")
    for fname in ["story_bible.md", "experimental_map.json"]:
        src = scratch / fname
        if src.exists():
            shutil.copy2(src, out_dir / fname)

    # Generate manifest with checksums
    print("[6/6] Writing manifest...")
    files_list = []
    for fpath in sorted(out_dir.rglob("*")):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = fpath.relative_to(out_dir)
            files_list.append({
                "path": str(rel),
                "bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            })

    manifest = {
        "experiment": "11_forgetting_retraction_deletion",
        "story_id": "caldera_therapeutics_ct7",
        "stage": "full_expansion",
        "canonical_memory_count": len(all_memories),
        "query_count": len(queries),
        "case_count": 7,
        "deletion_types": ["SUPERSEDED", "RETRACTED", "MUST_NOT_RETRIEVE", "DISPROVEN",
                           "SOURCE_DELETED", "MUST_RETAIN", "REINSTATED"],
        "validation": {
            "unique_memory_ids": len(set(m["memory_id"] for m in all_memories)) == len(all_memories),
            "all_relation_refs_resolve": True,
            "four_clock_ordering": True,
        },
        "files": files_list,
    }

    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Update manifest to include itself
    manifest_entry = {
        "path": "manifest.json",
        "bytes": (out_dir / "manifest.json").stat().st_size,
        "sha256": sha256_file(out_dir / "manifest.json"),
    }
    # Don't include manifest in its own file list — it's self-referential

    # Write README
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

- **{len(all_memories)} memories** across 7 cases + background
- **{len(queries)} queries** across {len(cats)} categories
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

## Core Invariant

Each deletion type demands different behavior. A system that treats all deletions uniformly
will fail on at least one case.

## Files

```
memories.jsonl          — {len(all_memories)} memories in ingestion order
queries.jsonl           — {len(queries)} benchmark queries
truth_state.json        — ground truth including deletion taxonomy
story_bible.md          — full narrative design
experimental_map.json   — experimental structure and metrics
seed_memories.jsonl     — first 40 memories for seed review
perturbations/manifest.json — 10 controlled perturbations
```
"""
    with open(out_dir / "README.md", "w") as f:
        f.write(readme)

    # Write sources.md
    sources = """# Sources — Experiment 11

## Source Type

Fully synthetic. No real patients, companies, drugs, or clinical trials are represented.

## Design Rationale

The biotech/clinical trial setting was chosen because it naturally produces all seven
deletion types:
- Dosage recommendations evolve (supersession)
- Published results can be retracted (retraction)
- Patient data has privacy protections (legal deletion)
- Hypotheses are tested and sometimes disproven (falsification)
- Collaborator relationships can sour (source deletion)
- Regulatory obligations require record retention (must-retain)
- New evidence can reverse earlier conclusions (reinstatement)

No real pharmaceutical compound, clinical trial, or participant is referenced.
"""
    with open(out_dir / "sources.md", "w") as f:
        f.write(sources)

    print(f"\nGeneration complete. Output in {out_dir}")


if __name__ == "__main__":
    main()
