#!/usr/bin/env python3
"""Generate Experiment 18 — Counterfactual / Negative Evidence.

Setting: Meridian Genomics Institute (MGI), Research Triangle Park, NC (2029-2034).
Gene therapy research institute where many programs were proposed but never executed,
trials were planned but cancelled, and side effects were feared but never observed.

Cases:
  C01: The Trial That Never Launched (MERIT-2 Phase III)
  C02: The Rejected Vector (VP-5 lipid nanoparticle)
  C03: The Side Effect That Never Materialized (hepatotoxicity)
  C04: The Withdrawn FDA Submission (BLA for MGT-401)
  C05: The Cancelled Program (MGT-603 CF therapy)
  C06: The Terminated Trial (NOVA-1 Phase I)
  C07: The Hypothetical Combination Therapy (in silico only)
"""

import json, hashlib, os, sys
from datetime import datetime, timedelta, timezone

OUT = sys.argv[1] if len(sys.argv) > 1 else "experiment_18_counterfactual_negative"
os.makedirs(OUT, exist_ok=True)

UTC = timezone.utc
T0 = datetime(2029, 3, 1, tzinfo=UTC)

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

mid_counter = 0
def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    mid_counter += 1
    _hash = hashlib.md5(f"exp18-r0-{mid_counter}".encode()).hexdigest()[:8]
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

qid_counter = 0
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

memories = []
queries = []

# === BACKGROUND ===
memories.append(M("bg", "Meridian Genomics Institute", "is_located_in", "Research Triangle Park, NC",
    "Meridian Genomics Institute (MGI) is a gene therapy research center in Research Triangle Park, North Carolina, founded in 2028.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG1", "institutional_record",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "Dr. Elena Vasquez", "holds_role", "Chief Scientific Officer",
    "Dr. Elena Vasquez serves as Chief Scientific Officer at MGI, overseeing all research programs.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG2", "hr_record",
    10, 0, 1, 1, ["background"]))

memories.append(M("bg", "Dr. Marcus Chen", "holds_role", "Lead Gene Therapy Researcher",
    "Dr. Marcus Chen leads the gene therapy research division at MGI.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG3", "hr_record",
    10, 0, 1, 1, ["background"]))

memories.append(M("bg", "Dr. Amara Obi", "holds_role", "Clinical Trial Director",
    "Dr. Amara Obi is Clinical Trial Director at MGI, responsible for all trial operations.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG4", "hr_record",
    10, 0, 1, 1, ["background"]))

memories.append(M("bg", "Jordan Reeves", "holds_role", "Regulatory Affairs Manager",
    "Jordan Reeves manages regulatory affairs at MGI, handling FDA submissions and compliance.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG5", "hr_record",
    10, 0, 1, 1, ["background"]))

memories.append(M("bg", "MGT-401", "is_program_for", "Duchenne muscular dystrophy",
    "MGT-401 is MGI's flagship gene therapy program targeting Duchenne muscular dystrophy (DMD).",
    "fact", "ground_truth", "system", 1.0, "SRC-BG6", "program_record",
    30, 0, 1, 1, ["background"]))

memories.append(M("bg", "MGT-502", "is_program_for", "spinal muscular atrophy",
    "MGT-502 is a gene therapy program for spinal muscular atrophy (SMA) in active development at MGI.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG7", "program_record",
    30, 0, 1, 1, ["background"]))

memories.append(M("bg", "VP-3", "is_a", "AAV delivery vector",
    "Vector Platform VP-3 is an adeno-associated virus (AAV) delivery vector adopted by MGI for clinical use.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG8", "technical_record",
    60, 0, 1, 1, ["background"]))

memories.append(M("bg", "Dr. Suki Tanaka", "holds_role", "Bioethics Committee Chair",
    "Dr. Suki Tanaka chairs the MGI Bioethics Committee.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG9", "hr_record",
    10, 0, 1, 1, ["background"]))

memories.append(M("bg", "Dr. Felix Brennan", "holds_role", "Toxicology Specialist",
    "Dr. Felix Brennan is the toxicology specialist at MGI, responsible for safety assessments.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG10", "hr_record",
    10, 0, 1, 1, ["background"]))

# === C01: The Trial That Never Launched (MERIT-2) ===
c01_design = M("C01", "MERIT-2", "was_designed_as", "Phase III trial for MGT-401",
    "MERIT-2 was designed as a Phase III randomized controlled trial for MGT-401 in DMD patients aged 4-12.",
    "event", "counterfactual", "Dr. Amara Obi", 0.95, "SRC-C01-1", "protocol_document",
    200, 1, 2, 1, ["C01", "counterfactual"])
memories.append(c01_design)

c01_irb = M("C01", "MERIT-2", "received_approval_from", "MGI IRB",
    "MERIT-2 protocol received IRB approval on June 15, 2030.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C01-2", "irb_record",
    470, 1, 2, 1, ["C01"])
memories.append(c01_irb)

c01_sites = M("C01", "MERIT-2", "selected_sites", "Duke, Johns Hopkins, CHOP",
    "Three clinical sites were selected for MERIT-2: Duke University Medical Center, Johns Hopkins, and Children's Hospital of Philadelphia.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-3", "site_selection_memo",
    480, 1, 3, 1, ["C01", "counterfactual"])
memories.append(c01_sites)

c01_budget = M("C01", "MERIT-2", "had_budget_of", "$34.2 million",
    "The approved budget for MERIT-2 was $34.2 million over 3 years.",
    "event", "counterfactual", "Jordan Reeves", 0.9, "SRC-C01-4", "budget_document",
    490, 1, 2, 1, ["C01", "counterfactual"])
memories.append(c01_budget)

c01_delay = M("C01", "MERIT-2", "was_delayed_by", "vector manufacturing problems",
    "MERIT-2 launch was delayed when VP-3 manufacturing at the contract facility encountered yield problems, reducing available vector supply by 60%.",
    "event", "ground_truth", "Dr. Marcus Chen", 0.95, "SRC-C01-5", "manufacturing_report",
    550, 2, 3, 1, ["C01"])
memories.append(c01_delay)

c01_cancel = M("C01", "MERIT-2", "was_cancelled", "before enrollment",
    "MERIT-2 was formally cancelled on March 8, 2031, before any patient was enrolled. The cancellation was due to manufacturing delays and competing data from Genexis Corp making the primary endpoint outdated.",
    "event", "ground_truth", "Dr. Elena Vasquez", 1.0, "SRC-C01-6", "decision_memo",
    740, 1, 2, 1, ["C01", "negation"],
    contradicts=[c01_design["memory_id"]])
memories.append(c01_cancel)

c01_neg = M("C01", "MERIT-2", "never_enrolled", "any patients",
    "MERIT-2 never enrolled a single patient. Zero subjects received treatment under this protocol.",
    "event", "negation", "Dr. Amara Obi", 1.0, "SRC-C01-7", "trial_registry",
    740, 0, 1, 1, ["C01", "negation"])
memories.append(c01_neg)

# === C02: The Rejected Vector (VP-5) ===
c02_eval = M("C02", "VP-5", "was_evaluated_as", "lipid nanoparticle vector",
    "VP-5, a lipid nanoparticle delivery vector, was evaluated over 6 months as a potential alternative to VP-3 for MGT-401 delivery.",
    "event", "counterfactual", "Dr. Marcus Chen", 0.9, "SRC-C02-1", "research_report",
    120, 1, 3, 1, ["C02", "counterfactual"])
memories.append(c02_eval)

c02_test = M("C02", "VP-5", "showed_in_tests", "higher transfection efficiency than VP-3",
    "In cell culture tests, VP-5 showed 23% higher transfection efficiency compared to VP-3.",
    "observation", "contextual_true", "Dr. Marcus Chen", 0.85, "SRC-C02-2", "lab_report",
    150, 2, 3, 1, ["C02"])
memories.append(c02_test)

c02_inflam = M("C02", "VP-5", "caused_in_animal_tests", "inflammatory response",
    "VP-5 caused significant inflammatory responses in the murine model, with elevated IL-6 and TNF-alpha levels 3x above baseline.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.95, "SRC-C02-3", "toxicology_report",
    180, 2, 4, 1, ["C02"])
memories.append(c02_inflam)

c02_reject = M("C02", "VP-5", "was_rejected_by", "Scientific Advisory Board",
    "The Scientific Advisory Board voted 7-1 against adopting VP-5 due to inflammatory response concerns. VP-5 was never used in any patient or clinical trial.",
    "event", "ground_truth", "Dr. Elena Vasquez", 1.0, "SRC-C02-4", "board_minutes",
    210, 1, 2, 1, ["C02", "negation"],
    contradicts=[c02_eval["memory_id"]])
memories.append(c02_reject)

# === C03: The Side Effect That Never Materialized ===
c03_risk = M("C03", "MGT-401", "was_assessed_for_risk_of", "hepatotoxicity",
    "Pre-clinical data suggested potential hepatotoxicity risk for MGT-401 due to liver tropism of the AAV vector.",
    "observation", "contextual_true", "Dr. Felix Brennan", 0.8, "SRC-C03-1", "risk_assessment",
    100, 1, 3, 1, ["C03"])
memories.append(c03_risk)

c03_protocol = M("C03", "MERIT-1", "implemented_monitoring_for", "hepatotoxicity",
    "Weekly liver function panels were mandated for all MERIT-1 participants as a hepatotoxicity monitoring protocol.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C03-2", "monitoring_protocol",
    300, 0, 2, 1, ["C03"])
memories.append(c03_protocol)

c03_results = M("C03", "MERIT-1 liver panels", "showed", "all normal results",
    "All 24 MERIT-1 participants completed weekly liver function panels over 12 months. Every result was within normal limits. Zero hepatotoxicity events were recorded.",
    "observation", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C03-3", "safety_report",
    660, 2, 5, 1, ["C03", "negation"])
memories.append(c03_results)

c03_neg = M("C03", "MERIT-1", "had_zero_cases_of", "hepatotoxicity",
    "The final MERIT-1 safety report confirmed zero cases of hepatotoxicity across all 24 participants and all monitoring timepoints.",
    "event", "negation", "Dr. Felix Brennan", 1.0, "SRC-C03-4", "final_safety_report",
    680, 1, 3, 1, ["C03", "negation"],
    supersedes=[c03_risk["memory_id"]])
memories.append(c03_neg)

# === C04: The Withdrawn FDA Submission ===
c04_draft = M("C04", "BLA for MGT-401", "was_drafted_over", "8 months",
    "The Biologics License Application (BLA) for MGT-401 was drafted over 8 months, from January to August 2031.",
    "event", "counterfactual", "Jordan Reeves", 0.95, "SRC-C04-1", "regulatory_record",
    670, 1, 2, 1, ["C04", "counterfactual"])
memories.append(c04_draft)

c04_presub = M("C04", "MGI", "held_pre_submission_meeting_with", "FDA CBER",
    "MGI held a Type B pre-submission meeting with FDA's Center for Biologics Evaluation and Research on September 12, 2031.",
    "event", "ground_truth", "Jordan Reeves", 1.0, "SRC-C04-2", "meeting_minutes",
    930, 1, 3, 1, ["C04"])
memories.append(c04_presub)

c04_fda = M("C04", "FDA", "raised_concerns_about", "long-term durability data",
    "At the pre-submission meeting, FDA expressed concern that 18-month follow-up data was insufficient. They recommended 3-year durability data before BLA submission.",
    "event", "ground_truth", "Jordan Reeves", 1.0, "SRC-C04-3", "fda_feedback",
    930, 0, 2, 1, ["C04"])
memories.append(c04_fda)

c04_withdraw = M("C04", "BLA for MGT-401", "was_withdrawn", "before formal submission",
    "The BLA for MGT-401 was withdrawn before formal submission to FDA. The decision was made on October 3, 2031, to wait for 3-year follow-up data.",
    "event", "ground_truth", "Dr. Elena Vasquez", 1.0, "SRC-C04-4", "decision_memo",
    950, 1, 2, 1, ["C04", "negation"],
    contradicts=[c04_draft["memory_id"]])
memories.append(c04_withdraw)

c04_neg = M("C04", "BLA for MGT-401", "was_never", "formally filed with FDA",
    "The BLA for MGT-401 was never formally filed with FDA. It remains in draft status pending 3-year durability data.",
    "event", "negation", "Jordan Reeves", 1.0, "SRC-C04-5", "regulatory_status",
    960, 0, 1, 1, ["C04", "negation"])
memories.append(c04_neg)

# === C05: The Cancelled Program (MGT-603) ===
c05_proposal = M("C05", "Dr. Marcus Chen", "proposed", "MGT-603 CF gene therapy program",
    "Dr. Marcus Chen proposed MGT-603, a gene therapy program for cystic fibrosis, in a formal proposal submitted April 2030.",
    "event", "counterfactual", "Dr. Marcus Chen", 0.9, "SRC-C05-1", "proposal_document",
    395, 1, 3, 1, ["C05", "counterfactual"])
memories.append(c05_proposal)

c05_feasibility = M("C05", "MGT-603", "had_feasibility_study_showing", "technical viability",
    "A feasibility study for MGT-603 concluded that the CFTR gene correction approach was technically viable using the VP-3 vector platform.",
    "observation", "counterfactual", "Dr. Marcus Chen", 0.85, "SRC-C05-2", "feasibility_report",
    425, 2, 4, 1, ["C05", "counterfactual"])
memories.append(c05_feasibility)

c05_ethics = M("C05", "Bioethics Committee", "raised_concerns_about", "MGT-603 patient population",
    "The Bioethics Committee raised concerns about the small target patient population for MGT-603 and potential informed consent challenges with pediatric CF patients.",
    "event", "ground_truth", "Dr. Suki Tanaka", 0.95, "SRC-C05-3", "committee_minutes",
    440, 1, 2, 1, ["C05"])
memories.append(c05_ethics)

c05_reject = M("C05", "MGT-603", "was_not_approved", "by the board",
    "The MGI board voted not to proceed with MGT-603. Resources were redirected to MGT-401 Phase III preparation and MGT-502 development.",
    "event", "ground_truth", "Dr. Elena Vasquez", 1.0, "SRC-C05-4", "board_minutes",
    460, 1, 2, 1, ["C05", "negation"],
    contradicts=[c05_proposal["memory_id"]])
memories.append(c05_reject)

c05_neg = M("C05", "MGT-603", "never_entered", "development",
    "MGT-603 never entered development. No IND was filed, no preclinical studies were initiated, and no patients were ever treated under this program.",
    "event", "negation", "system", 1.0, "SRC-C05-5", "program_registry",
    460, 0, 1, 1, ["C05", "negation"])
memories.append(c05_neg)

# === C06: The Terminated Trial (NOVA-1) ===
c06_start = M("C06", "NOVA-1", "was_initiated_as", "Phase I trial for MGT-710",
    "NOVA-1 was initiated as a Phase I dose-escalation trial for MGT-710, a CRISPR-based sickle cell treatment, enrolling 8 patients.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-1", "trial_registry",
    500, 0, 1, 1, ["C06"])
memories.append(c06_start)

c06_ae = M("C06", "NOVA-1", "observed_adverse_events_in", "3 of 8 patients",
    "Three of the first 8 NOVA-1 patients developed immune reactions: elevated CRP, fever, and joint pain. These were immune-mediated, NOT hepatotoxicity.",
    "observation", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C06-2", "adverse_event_report",
    540, 1, 2, 1, ["C06"])
memories.append(c06_ae)

c06_dsmb = M("C06", "DSMB", "recommended_pausing", "NOVA-1",
    "The Data Safety Monitoring Board recommended pausing NOVA-1 enrollment after reviewing the 3 adverse events.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-3", "dsmb_report",
    545, 0, 1, 1, ["C06"])
memories.append(c06_dsmb)

c06_term = M("C06", "NOVA-1", "was_terminated", "after DSMB review",
    "NOVA-1 was terminated on November 22, 2030, following DSMB review. Only 3 patients had received treatment; the remaining 5 enrolled patients did NOT receive the investigational product.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-4", "termination_report",
    630, 1, 3, 1, ["C06", "negation"])
memories.append(c06_term)

c06_neg = M("C06", "NOVA-1", "did_not_complete", "planned enrollment",
    "NOVA-1 did not complete its planned enrollment of 24 patients. Only 8 were enrolled and only 3 received treatment.",
    "event", "negation", "Dr. Amara Obi", 1.0, "SRC-C06-5", "trial_closure_report",
    635, 0, 1, 1, ["C06", "negation"])
memories.append(c06_neg)

# === C07: The Hypothetical Combination Therapy ===
c07_paper = M("C07", "Dr. Elena Vasquez", "authored_whitepaper_on", "MGT-401 combination therapy",
    "Dr. Vasquez authored a speculative whitepaper proposing combining MGT-401 with the small-molecule chaperone compound TRX-88 to enhance protein folding.",
    "event", "counterfactual", "Dr. Elena Vasquez", 0.7, "SRC-C07-1", "whitepaper",
    800, 1, 3, 1, ["C07", "counterfactual"])
memories.append(c07_paper)

c07_sim = M("C07", "Dr. Ravi Patel", "ran_simulations_of", "MGT-401 + TRX-88 combination",
    "Dr. Patel ran computational molecular dynamics simulations of the MGT-401 + TRX-88 combination, modeling protein-chaperone interactions over 500 nanoseconds.",
    "event", "counterfactual", "Dr. Ravi Patel", 0.75, "SRC-C07-2", "simulation_report",
    830, 2, 4, 1, ["C07", "counterfactual"])
memories.append(c07_sim)

c07_results = M("C07", "simulations", "showed", "35% improvement in protein stability",
    "In silico simulations showed a predicted 35% improvement in dystrophin protein stability when co-administered with TRX-88. These results are computational only — no in vitro or in vivo testing was performed.",
    "observation", "counterfactual", "Dr. Ravi Patel", 0.6, "SRC-C07-3", "simulation_output",
    835, 1, 2, 1, ["C07", "counterfactual"])
memories.append(c07_results)

c07_neg = M("C07", "MGT-401 + TRX-88 combination", "was_never_tested", "in vitro or in vivo",
    "The MGT-401 + TRX-88 combination therapy has never been tested in cell cultures, animal models, or human subjects. All results are from computational simulations only.",
    "event", "negation", "system", 1.0, "SRC-C07-4", "program_registry",
    840, 0, 1, 1, ["C07", "negation"])
memories.append(c07_neg)

# === QUERIES ===

# Q1: Factual recall — what happened with MERIT-2?
queries.append(Q(
    "What happened with the MERIT-2 clinical trial?",
    "status_tracking",
    ["MERIT-2 was designed but cancelled before enrolling any patients",
     "Manufacturing delays and competing data led to cancellation"],
    ["MERIT-2 received IRB approval but never launched"],
    ["MERIT-2 enrolled patients", "MERIT-2 showed positive results",
     "MERIT-2 completed", "MERIT-2 is ongoing"],
    [c01_design["memory_id"], c01_cancel["memory_id"], c01_neg["memory_id"]],
    [c01_irb["memory_id"], c01_sites["memory_id"], c01_budget["memory_id"]],
    "hard",
    notes="Must report cancellation, not just planning activities"
))

# Q2: Negation detection — VP-5 usage
queries.append(Q(
    "Was VP-5 ever used in a clinical trial at MGI?",
    "negation_detection",
    ["VP-5 was never used in any patient or clinical trial",
     "VP-5 was evaluated but rejected by the Scientific Advisory Board"],
    ["VP-5 showed higher transfection but was rejected due to inflammatory response"],
    ["VP-5 was used in MERIT-1", "VP-5 delivered MGT-401",
     "VP-5 is the current vector platform"],
    [c02_reject["memory_id"], c02_eval["memory_id"]],
    [c02_test["memory_id"], c02_inflam["memory_id"]],
    "medium"
))

# Q3: Confusion resistance — hepatotoxicity vs immune reactions
queries.append(Q(
    "Were there any hepatotoxicity events in MGI's clinical trials?",
    "confusion_resistance",
    ["No hepatotoxicity events were recorded in MERIT-1",
     "All liver function panels were normal"],
    ["The NOVA-1 adverse events were immune reactions, not hepatotoxicity"],
    ["Hepatotoxicity was observed", "Liver damage occurred",
     "NOVA-1 patients had hepatotoxicity"],
    [c03_results["memory_id"], c03_neg["memory_id"], c06_ae["memory_id"]],
    [c03_risk["memory_id"], c03_protocol["memory_id"]],
    "hard",
    conflict=True,
    notes="Must distinguish hepatotoxicity concern/monitoring from NOVA-1 immune adverse events"
))

# Q4: Counterfactual distinction — BLA status
queries.append(Q(
    "What is the status of the BLA for MGT-401?",
    "counterfactual_distinction",
    ["The BLA was drafted but withdrawn before formal submission",
     "FDA recommended 3-year durability data before submission"],
    ["The BLA remains in draft pending longer follow-up data"],
    ["The BLA was submitted", "The BLA is under FDA review",
     "The BLA was approved", "The BLA was rejected by FDA"],
    [c04_withdraw["memory_id"], c04_neg["memory_id"], c04_fda["memory_id"]],
    [c04_draft["memory_id"], c04_presub["memory_id"]],
    "hard",
    notes="Must report withdrawal, not just drafting or pre-submission activities"
))

# Q5: Scope preservation — combination therapy results
queries.append(Q(
    "What are the results of the MGT-401 + TRX-88 combination therapy?",
    "scope_preservation",
    ["Computational simulations showed 35% protein stability improvement",
     "No in vitro or in vivo testing has been performed"],
    ["Results are from in silico simulations only"],
    ["Clinical trial showed improvement", "Animal studies confirmed",
     "Patients showed improvement", "The combination was tested in humans"],
    [c07_results["memory_id"], c07_neg["memory_id"]],
    [c07_paper["memory_id"], c07_sim["memory_id"]],
    "hard",
    scope=True,
    notes="Must specify results are computational only, not experimental"
))

# Q6: Status tracking — MGT-603
queries.append(Q(
    "What is the current status of the MGT-603 cystic fibrosis program?",
    "status_tracking",
    ["MGT-603 was proposed but never approved",
     "The board voted not to proceed"],
    ["MGT-603 never entered development"],
    ["MGT-603 is in development", "MGT-603 is in clinical trials",
     "MGT-603 treats CF patients"],
    [c05_reject["memory_id"], c05_neg["memory_id"]],
    [c05_proposal["memory_id"], c05_feasibility["memory_id"]],
    "medium"
))

# Q7: Evidence absence — side effects
queries.append(Q(
    "What side effects were observed in MERIT-1 participants?",
    "evidence_absence",
    ["No hepatotoxicity events were observed despite monitoring",
     "All liver panels were within normal limits"],
    ["MERIT-1 had a clean safety profile for hepatotoxicity"],
    ["Hepatotoxicity was observed", "Liver damage was reported",
     "Serious adverse events occurred in MERIT-1"],
    [c03_results["memory_id"], c03_neg["memory_id"]],
    [c03_risk["memory_id"], c03_protocol["memory_id"]],
    "medium",
    notes="Must correctly report absence of adverse findings"
))

# Q8: Temporal reasoning — NOVA-1
queries.append(Q(
    "How many patients were treated in the NOVA-1 trial?",
    "factual_recall",
    ["Only 3 patients received treatment",
     "8 were enrolled but 5 did not receive the investigational product"],
    ["The trial was terminated after adverse events in 3 patients"],
    ["All 8 patients were treated", "24 patients completed the trial",
     "NOVA-1 completed enrollment"],
    [c06_term["memory_id"], c06_neg["memory_id"], c06_ae["memory_id"]],
    [c06_start["memory_id"], c06_dsmb["memory_id"]],
    "medium"
))

# Q9: Counterfactual distinction — what trials ran vs didn't
queries.append(Q(
    "Which clinical trials at MGI actually enrolled and treated patients?",
    "counterfactual_distinction",
    ["MERIT-1 enrolled and treated 24 patients",
     "NOVA-1 enrolled 8 but only treated 3 before termination",
     "MERIT-2 never enrolled any patients"],
    ["Only MERIT-1 completed; NOVA-1 was terminated early; MERIT-2 was cancelled"],
    ["MERIT-2 enrolled patients", "All three trials treated patients",
     "NOVA-1 treated all 8 enrolled patients"],
    [c01_neg["memory_id"], c03_results["memory_id"], c06_term["memory_id"], c06_neg["memory_id"]],
    [c01_design["memory_id"], c06_start["memory_id"]],
    "hard",
    notes="Must distinguish between trials that ran vs. were only planned"
))

# Q10: Negation detection — what programs are active
queries.append(Q(
    "Which gene therapy programs at MGI are currently active?",
    "negation_detection",
    ["MGT-401 and MGT-502 are active programs",
     "MGT-603 was never started", "MGT-710 was terminated"],
    ["Only MGT-401 and MGT-502 remain active"],
    ["MGT-603 is active", "MGT-710 is ongoing",
     "All four programs are active"],
    [c05_neg["memory_id"], c06_term["memory_id"]],
    [c05_proposal["memory_id"], c06_start["memory_id"]],
    "medium",
    notes="Must correctly exclude cancelled/terminated programs"
))

# Write outputs
with open(os.path.join(OUT, "memories.jsonl"), "w") as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")

with open(os.path.join(OUT, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

files_info = []
for fname in ["memories.jsonl", "queries.jsonl"]:
    fp = os.path.join(OUT, fname)
    data = open(fp, 'rb').read()
    files_info.append({
        "path": fname,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest()
    })

manifest = {
    "experiment": "exp18",
    "title": "Counterfactual / Negative Evidence",
    "description": "Tests whether memory systems correctly handle things that did NOT happen, plans that were cancelled, and conditions that failed to materialize.",
    "files": files_info,
    "generated": datetime.now(UTC).isoformat()
}
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Generated {len(memories)} memories, {len(queries)} queries")
print(f"Output: {OUT}/")
