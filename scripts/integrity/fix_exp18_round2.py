#!/usr/bin/env python3
"""Exp18 Round 2 expansion: 78 → ~145 memories, 20 → ~45 queries."""

import json, hashlib, os, sys
from datetime import datetime, timedelta, timezone

d = sys.argv[1] if len(sys.argv) > 1 else "experiment_18_counterfactual_negative"

with open(os.path.join(d, "memories.jsonl")) as f:
    memories = [json.loads(l) for l in f if l.strip()]
with open(os.path.join(d, "queries.jsonl")) as f:
    queries = [json.loads(l) for l in f if l.strip()]

UTC = timezone.utc
T0 = datetime(2029, 3, 1, tzinfo=UTC)

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

mid_counter = 200

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp18-r2-{mid_counter}".encode()).hexdigest()[:8]
    mid_counter += 1
    ev = T0 + timedelta(days=ev_off)
    ob = T0 + timedelta(days=ev_off + obs_off)
    au = T0 + timedelta(days=ev_off + obs_off + auth_off)
    ig = T0 + timedelta(days=ev_off + obs_off + auth_off + ing_off)
    return {
        "memory_id": f"E18-{_hash}",
        "experiment": "exp18",
        "story_id": story,
        "event_time": ts(ev),
        "observation_time": ts(ob),
        "authored_time": ts(au),
        "ingestion_time": ts(ig),
        "subject": subj,
        "predicate": pred,
        "object": obj,
        "text": text,
        "memory_type": etype,
        "truth_role": truth_role,
        "belief_holder": holder,
        "confidence": conf,
        "source_id": src_id,
        "source_type": src_type,
        "derived_from": derived or [],
        "supersedes": supersedes or [],
        "contradicts": contradicts or [],
        "duplicates": duplicates or [],
        "aliases": aliases or [],
        "scope": scope,
        "tags": tags
    }

qid_counter = len(queries)

def Q(query, cat, expected, acceptable, forbidden, rel, dist, difficulty,
      uncertainty=False, conflict=False, disambiguate=False,
      scope=False, abstain=False, notes=""):
    global qid_counter
    qid_counter += 1
    return {
        "query_id": f"Q18-{qid_counter:02d}",
        "query": query,
        "category": cat,
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": rel,
        "distractor_memory_ids": dist,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambiguate,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "difficulty": difficulty,
        "notes": notes
    }

mem_by_id = {m["memory_id"]: m for m in memories}
new_mem = []
new_q = []

# --- More C01 detail ---
new_mem.append(M("C01", "MERIT-2 protocol", "specified_duration_of", "24 months treatment + 12 months follow-up",
    "MERIT-2 protocol specified a 24-month treatment period with 12 months of post-treatment follow-up.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-12", "protocol_document",
    200, 1, 3, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "MERIT-2", "would_have_used", "VP-3 vector at 1.5x MERIT-1 dose",
    "MERIT-2 planned to use VP-3 vector at 1.5x the dose used in MERIT-1, based on dose-response modeling.",
    "event", "counterfactual", "Dr. Marcus Chen", 0.85, "SRC-C01-13", "dose_modeling_report",
    210, 2, 4, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "Duke site coordinator", "completed_staff_training_for", "MERIT-2",
    "The Duke site completed staff training and facility preparation for MERIT-2 before learning of the cancellation.",
    "event", "ground_truth", "Dr. Amara Obi", 0.9, "SRC-C01-14", "site_report",
    520, 1, 2, 1, ["C01"]))

new_mem.append(M("C01", "MERIT-2 patient screening", "never_began", "at any site",
    "Patient screening for MERIT-2 never began at any of the three selected clinical sites.",
    "event", "negation", "Dr. Amara Obi", 1.0, "SRC-C01-15", "trial_registry",
    740, 0, 1, 1, ["C01", "negation"]))

# --- More C02 detail ---
new_mem.append(M("C02", "VP-5 first evaluation report", "showed", "promising in vitro data",
    "The first VP-5 evaluation report showed promising transfection results in HEK293 and myoblast cell lines, with 23% improvement over VP-3.",
    "observation", "contextual_true", "Dr. Marcus Chen", 0.85, "SRC-C02-9", "lab_report",
    130, 2, 4, 1, ["C02"]))

new_mem.append(M("C02", "VP-5 second evaluation", "raised", "immunogenicity concerns",
    "The second VP-5 evaluation report revealed dose-dependent immunogenicity in the murine model, with anti-PEG antibodies detected in 60% of animals.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.9, "SRC-C02-10", "immunology_report",
    165, 2, 4, 1, ["C02"]))

new_mem.append(M("C02", "VP-5", "was_never_tested_in", "non-human primates",
    "VP-5 evaluation was halted before non-human primate studies. All data is from murine models and cell culture only.",
    "event", "negation", "Dr. Felix Brennan", 1.0, "SRC-C02-11", "research_record",
    220, 0, 1, 1, ["C02", "negation"]))

# --- More C03 detail ---
new_mem.append(M("C03", "MERIT-1 patient 007", "had_elevated_ALT_at_week_4", "but within normal range",
    "MERIT-1 patient 007 showed mildly elevated ALT at week 4 (42 U/L, upper normal 45 U/L). This was within normal limits and resolved spontaneously.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.95, "SRC-C03-8", "lab_result",
    330, 1, 2, 1, ["C03"]))

new_mem.append(M("C03", "MERIT-1 DSMB", "reviewed_liver_data_and_found", "no safety signal",
    "The MERIT-1 DSMB reviewed all liver function data at interim analysis and found no safety signal. They recommended continuing without protocol modification.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C03-9", "dsmb_report",
    450, 1, 2, 1, ["C03"]))

new_mem.append(M("C03", "hepatotoxicity risk", "was_downgraded_to", "low probability for MGT-401",
    "Following MERIT-1 clean safety data, the hepatotoxicity risk for MGT-401 was downgraded from 'moderate' to 'low probability' in the risk register.",
    "event", "ground_truth", "Dr. Felix Brennan", 0.95, "SRC-C03-10", "risk_register",
    690, 1, 2, 1, ["C03"],
    supersedes=[m["memory_id"] for m in memories if "was_assessed_for_risk_of" in m.get("predicate","")][:1]))

# --- More C04 detail ---
new_mem.append(M("C04", "BLA CMC section", "was_completed_by", "Morgan Hale",
    "Morgan Hale led the completion of the Chemistry, Manufacturing, and Controls section of the MGT-401 BLA.",
    "event", "counterfactual", "Morgan Hale", 0.9, "SRC-C04-9", "regulatory_record",
    750, 1, 3, 1, ["C04", "counterfactual"]))

new_mem.append(M("C04", "BLA clinical section", "was_completed_by", "Priya Sharma",
    "Priya Sharma compiled the clinical data section of the BLA, including all MERIT-1 efficacy and safety results.",
    "event", "counterfactual", "Priya Sharma", 0.9, "SRC-C04-10", "regulatory_record",
    780, 1, 3, 1, ["C04", "counterfactual"]))

new_mem.append(M("C04", "pre-submission FDA meeting", "was_attended_by", "Reeves, Vasquez, and Obi",
    "The Type B pre-submission meeting with FDA was attended by Jordan Reeves, Dr. Vasquez, and Dr. Obi from MGI.",
    "event", "ground_truth", "Jordan Reeves", 1.0, "SRC-C04-11", "meeting_record",
    930, 0, 1, 1, ["C04"]))

new_mem.append(M("C04", "FDA reviewer", "requested_additional", "immunogenicity data",
    "The FDA reviewer also requested additional immunogenicity data for the anti-AAV antibody response in the BLA.",
    "event", "ground_truth", "Jordan Reeves", 0.95, "SRC-C04-12", "fda_feedback",
    930, 0, 2, 1, ["C04"]))

# --- More C05 detail ---
new_mem.append(M("C05", "MGT-603", "targeted_CFTR_gene_with", "full-length replacement strategy",
    "MGT-603 proposed full-length CFTR gene replacement using a dual-vector AAV approach, a technically ambitious strategy.",
    "event", "counterfactual", "Dr. Marcus Chen", 0.85, "SRC-C05-9", "proposal_document",
    395, 1, 3, 1, ["C05", "counterfactual"]))

new_mem.append(M("C05", "Dr. Suki Tanaka", "noted_that", "CF patient population is small but has high unmet need",
    "Dr. Tanaka acknowledged the high unmet need in CF but noted that the target subpopulation (specific CFTR mutations) numbered fewer than 5,000 patients in the US.",
    "event", "ground_truth", "Dr. Suki Tanaka", 0.9, "SRC-C05-10", "committee_minutes",
    440, 1, 2, 1, ["C05"]))

new_mem.append(M("C05", "board vote on MGT-603", "was", "6-2 against proceeding",
    "The board voted 6-2 against proceeding with MGT-603, with Dr. Chen and Lisa Cartwright dissenting.",
    "event", "ground_truth", "Dr. Elena Vasquez", 1.0, "SRC-C05-11", "board_minutes",
    460, 1, 2, 1, ["C05"]))

# --- More C06 detail ---
new_mem.append(M("C06", "NOVA-1 dose level 1", "treated", "3 patients at 5e12 vg/kg",
    "The first 3 NOVA-1 patients received dose level 1 at 5e12 vector genomes per kilogram.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-10", "dosing_record",
    510, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 dose level 2", "was_never_administered", "to any patient",
    "Dose level 2 (1e13 vg/kg) was never administered. The trial was terminated before dose escalation.",
    "event", "negation", "Dr. Amara Obi", 1.0, "SRC-C06-11", "trial_record",
    635, 0, 1, 1, ["C06", "negation"]))

new_mem.append(M("C06", "NOVA-1 patient 004", "experienced", "grade 2 fever and joint pain",
    "NOVA-1 patient 004 experienced grade 2 fever (39.2°C) and joint pain beginning 48 hours post-infusion.",
    "observation", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C06-12", "ae_report",
    525, 1, 2, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 patients 001-003", "received_treatment", "without adverse events",
    "NOVA-1 patients 001, 002, and 003 all received treatment at dose level 1. Patients 001-003 did not experience adverse events initially, but patients 004, 005, 006 (the next three in the cohort) had immune reactions. Only 3 of the first enrolled 8 were treated.",
    "observation", "ground_truth", "Dr. Amara Obi", 0.95, "SRC-C06-13", "trial_record",
    520, 1, 3, 1, ["C06"]))

# --- More C07 detail ---
new_mem.append(M("C07", "Patel simulations", "used_parameters_from", "published dystrophin crystal structure",
    "Dr. Patel's molecular dynamics simulations used the published dystrophin spectrin-like repeat crystal structure (PDB: 1DXX) as the starting conformation.",
    "event", "counterfactual", "Dr. Ravi Patel", 0.8, "SRC-C07-8", "simulation_methods",
    830, 2, 4, 1, ["C07", "counterfactual"]))

new_mem.append(M("C07", "TRX-88 binding affinity", "was_predicted_at", "Kd = 2.3 nM in simulation",
    "Simulations predicted TRX-88 binding to dystrophin with an affinity of Kd = 2.3 nM, suggesting tight binding if confirmed experimentally.",
    "observation", "counterfactual", "Dr. Ravi Patel", 0.6, "SRC-C07-9", "simulation_output",
    835, 1, 2, 1, ["C07", "counterfactual"]))

new_mem.append(M("C07", "combination therapy proposal", "was_not_included_in", "MGI strategic plan",
    "The MGT-401 + TRX-88 combination therapy was not included in MGI's 2032-2035 strategic plan. It remains a theoretical concept only.",
    "event", "negation", "Dr. Elena Vasquez", 1.0, "SRC-C07-10", "strategic_plan",
    1100, 1, 2, 1, ["C07", "negation"]))

# --- Cross-cutting: planned-vs-executed summary memories ---
new_mem.append(M("bg", "MGI", "has_had_four_proposed_programs", "MGT-401, MGT-502, MGT-603, MGT-710",
    "MGI has proposed four gene therapy programs: MGT-401 (DMD, active), MGT-502 (SMA, active), MGT-603 (CF, never started), and MGT-710 (sickle cell, suspended).",
    "fact", "ground_truth", "system", 1.0, "SRC-BG21", "program_registry",
    1100, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "has_evaluated_two_vector_platforms", "VP-3 (adopted) and VP-5 (rejected)",
    "MGI evaluated two vector platforms: VP-3 (AAV, adopted and used in all trials) and VP-5 (lipid nanoparticle, rejected after evaluation).",
    "fact", "ground_truth", "system", 1.0, "SRC-BG22", "technical_record",
    250, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI regulatory submissions", "total", "zero approved, one withdrawn",
    "As of 2032, MGI has made zero approved regulatory submissions. The sole BLA attempt for MGT-401 was withdrawn before formal filing.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG23", "regulatory_status",
    1100, 0, 1, 1, ["background"]))

# --- Additional negation/counterfactual memories for depth ---
new_mem.append(M("C01", "MERIT-2 enrollment criteria", "included", "ambulatory boys aged 4-12 with confirmed DMD",
    "MERIT-2 would have enrolled ambulatory boys aged 4-12 with genetically confirmed DMD and NSAA score between 15 and 35.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-16", "protocol_document",
    200, 1, 3, 1, ["C01", "counterfactual"]))

new_mem.append(M("C02", "VP-5 evaluation cost", "was", "$2.8 million over 6 months",
    "The total cost of the VP-5 evaluation program was $2.8 million over 6 months, covering cell culture, animal studies, and advisory board review.",
    "event", "ground_truth", "Priya Sharma", 0.9, "SRC-C02-12", "budget_record",
    220, 1, 2, 1, ["C02"]))

new_mem.append(M("C03", "Dr. Brennan", "testified_to_DSMB_that", "no hepatotoxicity signal existed",
    "Dr. Brennan testified to the MERIT-1 DSMB that after 12 months of weekly monitoring, there was no hepatotoxicity signal in any patient.",
    "event", "negation", "Dr. Felix Brennan", 1.0, "SRC-C03-11", "dsmb_testimony",
    650, 1, 2, 1, ["C03", "negation"]))

new_mem.append(M("C04", "Reeves", "estimated_BLA_revision_cost", "$3.5 million additional",
    "Jordan Reeves estimated that revising the BLA with 3-year data would cost an additional $3.5 million.",
    "event", "ground_truth", "Jordan Reeves", 0.85, "SRC-C04-13", "budget_estimate",
    960, 1, 2, 1, ["C04"]))

new_mem.append(M("C06", "MGT-710 reformulation", "is_expected_to_take", "18-24 months",
    "The reformulation of MGT-710's CRISPR delivery system to reduce immunogenicity is expected to take 18-24 months.",
    "event", "supporting_belief", "Dr. Marcus Chen", 0.7, "SRC-C06-14", "program_plan",
    650, 1, 2, 1, ["C06"]))

new_mem.append(M("C07", "TRX-88 developer", "has_not_been_contacted", "by MGI",
    "MGI has not contacted the TRX-88 developer at MIT about licensing or collaboration. The compound remains in academic research only.",
    "event", "negation", "system", 1.0, "SRC-C07-11", "business_record",
    900, 0, 1, 1, ["C07", "negation"]))

# Additional queries
new_q.append(Q(
    "What dose was used in NOVA-1 and were higher doses ever tested?",
    "negation_detection",
    ["Dose level 1 was 5e12 vg/kg",
     "Dose level 2 (1e13 vg/kg) was never administered"],
    ["Only the lowest dose was used before termination"],
    ["Higher doses were tested", "Dose escalation was completed",
     "Multiple dose levels were evaluated in patients"],
    [m["memory_id"] for m in memories + new_mem if "dose_level" in m.get("subject","").lower() or "dose level" in m.get("text","").lower()][:3],
    [],
    "medium"
))

new_q.append(Q(
    "What is the estimated timeline for MGT-401 regulatory approval?",
    "temporal_reasoning",
    ["The revised BLA targets Q2 2033",
     "The current BLA was withdrawn pending 3-year follow-up data"],
    ["Approval timeline depends on durability data collection"],
    ["The BLA has been submitted", "Approval is imminent",
     "MGT-401 is already approved"],
    [m["memory_id"] for m in memories if "revised BLA" in m.get("subject","") or "was_withdrawn" in m.get("predicate","")][:2],
    [m["memory_id"] for m in memories if "was_drafted" in m.get("predicate","")][:1],
    "medium"
))

new_q.append(Q(
    "Was VP-5 ever tested in non-human primates?",
    "negation_detection",
    ["VP-5 was never tested in non-human primates",
     "All VP-5 data comes from murine models and cell culture only"],
    ["Evaluation was halted before NHP studies"],
    ["VP-5 was tested in primates", "NHP studies were completed",
     "VP-5 showed safety in primates"],
    [n["memory_id"] for n in new_mem if "non-human primates" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and "animal" in m.get("text","").lower()][:1],
    "easy"
))

new_q.append(Q(
    "How much did the VP-5 evaluation cost and what was the outcome?",
    "factual_recall",
    ["The VP-5 evaluation cost $2.8 million over 6 months",
     "VP-5 was rejected by the Scientific Advisory Board"],
    ["$2.8M spent, vector rejected due to inflammatory and immunogenicity concerns"],
    ["VP-5 was adopted", "The evaluation led to clinical use"],
    [n["memory_id"] for n in new_mem if "VP-5 evaluation cost" in n.get("subject","")][:1] +
    [m["memory_id"] for m in memories if "was_rejected_by" in m.get("predicate","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Who worked on the BLA for MGT-401 and what sections did they handle?",
    "factual_recall",
    ["Morgan Hale led the CMC section",
     "Priya Sharma compiled the clinical data section",
     "Jordan Reeves managed the overall regulatory process"],
    ["Multiple team members contributed to the draft BLA"],
    ["The BLA was completed by one person", "External consultants wrote the BLA"],
    [n["memory_id"] for n in new_mem if "BLA" in n.get("subject","") and ("Morgan" in n.get("text","") or "Priya" in n.get("text",""))][:2],
    [m["memory_id"] for m in memories if m.get("story_id") == "C04" and "was_drafted" in m.get("predicate","")][:1],
    "easy"
))

new_q.append(Q(
    "Is the MGT-401 + TRX-88 combination therapy in MGI's strategic plan?",
    "negation_detection",
    ["The combination therapy was NOT included in MGI's 2032-2035 strategic plan",
     "It remains a theoretical concept"],
    ["It was discussed but is not planned for development"],
    ["It is in the strategic plan", "Development is underway",
     "Clinical testing is planned"],
    [n["memory_id"] for n in new_mem if "strategic_plan" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "was_never_tested" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "simulations" in m.get("subject","")][:1],
    "medium"
))

new_q.append(Q(
    "How did the board vote on the MGT-603 proposal?",
    "factual_recall",
    ["The board voted 6-2 against proceeding with MGT-603",
     "Dr. Chen and Lisa Cartwright dissented"],
    ["Majority opposed; only two members supported the program"],
    ["The board approved MGT-603", "The vote was unanimous",
     "MGT-603 was approved with conditions"],
    [n["memory_id"] for n in new_mem if "board vote" in n.get("subject","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C05" and "not_approved" in m.get("predicate","")][:1],
    "easy"
))

new_q.append(Q(
    "Did any MERIT-1 patient show abnormal liver function tests?",
    "evidence_absence",
    ["Patient 007 had mildly elevated ALT at week 4 but within normal limits",
     "No patient showed clinically significant liver abnormalities",
     "The DSMB found no safety signal"],
    ["One borderline elevation resolved spontaneously; no hepatotoxicity signal"],
    ["Hepatotoxicity was detected", "Liver damage occurred",
     "ALT elevations were clinically significant"],
    [n["memory_id"] for n in new_mem if "patient 007" in n.get("subject","").lower() or "DSMB" in n.get("subject","")][:2] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "zero_cases" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "risk" in m.get("predicate","")][:1],
    "hard",
    notes="Tests ability to report borderline findings without catastrophizing"
))

new_q.append(Q(
    "How many gene therapy programs has MGI proposed vs. how many are currently active?",
    "counterfactual_distinction",
    ["Four programs proposed: MGT-401, MGT-502, MGT-603, MGT-710",
     "Only two are currently active: MGT-401 and MGT-502",
     "MGT-603 was never started; MGT-710 is suspended"],
    ["Half of proposed programs are active; one never started, one suspended"],
    ["All four are active", "Three programs are active",
     "MGT-603 is in development"],
    [n["memory_id"] for n in new_mem if "four_proposed" in n.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if "total_active" in m.get("predicate","")][:1],
    [],
    "medium"
))

new_q.append(Q(
    "What happened at the FDA pre-submission meeting for MGT-401?",
    "temporal_reasoning",
    ["FDA acknowledged promising efficacy data",
     "FDA raised concerns about insufficient long-term durability data",
     "FDA also requested additional immunogenicity data"],
    ["The meeting led to the BLA withdrawal decision"],
    ["FDA approved the BLA", "FDA rejected the application",
     "No concerns were raised"],
    [m["memory_id"] for m in memories if "pre_submission" in m.get("predicate","") or "raised_concerns" in m.get("predicate","")][:2] +
    [n["memory_id"] for n in new_mem if "immunogenicity" in n.get("text","") and "FDA" in n.get("subject","")][:1],
    [],
    "medium"
))

new_q.append(Q(
    "Has MGI ever submitted any regulatory filing that was accepted by the FDA?",
    "negation_detection",
    ["MGI has zero approved regulatory submissions",
     "The only BLA attempt was withdrawn before formal filing"],
    ["No regulatory filings have been formally submitted or accepted"],
    ["The BLA was accepted", "FDA approved MGT-401",
     "A regulatory submission is under review"],
    [n["memory_id"] for n in new_mem if "zero approved" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if "was_never" in m.get("predicate","") and "BLA" in m.get("subject","")][:1],
    [m["memory_id"] for m in memories if "was_drafted" in m.get("predicate","")][:1],
    "medium"
))

new_q.append(Q(
    "What is the expected timeline for reformulating MGT-710?",
    "temporal_reasoning",
    ["Reformulation is expected to take 18-24 months"],
    ["The CRISPR delivery system needs redesign to reduce immunogenicity"],
    ["MGT-710 is ready for trials", "Reformulation is complete",
     "MGT-710 has resumed"],
    [n["memory_id"] for n in new_mem if "reformulation" in n.get("subject","").lower()][:1],
    [],
    "easy"
))

new_q.append(Q(
    "What were the reasons for the 7-1 vote against VP-5?",
    "factual_recall",
    ["Inflammatory response in animal tests (elevated IL-6 and TNF-alpha)",
     "Immunogenicity concerns (anti-PEG antibodies in 60% of animals)",
     "High liver accumulation raising hepatotoxicity concerns"],
    ["Multiple safety concerns from animal studies drove the rejection"],
    ["VP-5 was rejected for business reasons", "Cost was the main factor",
     "VP-5 lacked efficacy"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and ("inflammatory" in m.get("text","") or "rejected" in m.get("predicate",""))][:2] +
    [n["memory_id"] for n in new_mem if "immunogenicity" in n.get("text","").lower() and "VP-5" in n.get("subject","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and "transfection" in m.get("text","")][:1],
    "medium",
    conflict=True,
    notes="Must weigh positive efficacy data against safety concerns that drove rejection"
))

memories.extend(new_mem)
queries.extend(new_q)

# Rewrite
with open(os.path.join(d, "memories.jsonl"), "w") as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")
with open(os.path.join(d, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

files_info = []
for fname in ["memories.jsonl", "queries.jsonl"]:
    fp = os.path.join(d, fname)
    data = open(fp, 'rb').read()
    files_info.append({"path": fname, "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})

with open(os.path.join(d, "manifest.json")) as f:
    manifest = json.load(f)
manifest["files"] = files_info
with open(os.path.join(d, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Round 2: {len(memories)} memories, {len(queries)} queries")
