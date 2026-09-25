#!/usr/bin/env python3
"""Exp18 Round 4 expansion: 143 → 205+ memories, 44 → 76+ queries."""

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

mid_counter = 600

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp18-r4-{mid_counter}".encode()).hexdigest()[:8]
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

new_mem = []
new_q = []

# Build existing ID set for contradiction/supersedes references
existing_ids = [m["memory_id"] for m in memories]

# === More C01 memories ===
new_mem.append(M("C01", "MERIT-2 CRO", "was_contracted", "Parexel International",
    "Parexel International was contracted as the CRO for MERIT-2. The contract was terminated with a $1.2M penalty after cancellation.",
    "event", "ground_truth", "Jordan Reeves", 0.9, "SRC-C01-21", "contract_record",
    490, 1, 2, 1, ["C01"]))

new_mem.append(M("C01", "MERIT-2 Data Management Plan", "was_finalized", "by Priya Sharma",
    "Priya Sharma finalized the MERIT-2 data management plan, including eCRF design and statistical analysis plan, none of which were ever used.",
    "event", "counterfactual", "Priya Sharma", 0.9, "SRC-C01-22", "data_plan",
    220, 2, 4, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "MERIT-2 cancellation", "saved_MGI", "approximately $32 million in direct trial costs",
    "Cancelling MERIT-2 before enrollment saved MGI approximately $32 million in direct trial costs, though $2.1M had been spent on preparation.",
    "event", "ground_truth", "Priya Sharma", 0.85, "SRC-C01-23", "financial_analysis",
    760, 2, 4, 1, ["C01"]))

new_mem.append(M("C01", "MERIT-2 comparator arm", "would_have_used", "placebo plus standard of care",
    "MERIT-2 planned a placebo-controlled design with standard of care as the comparator arm.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-24", "protocol_document",
    200, 1, 3, 1, ["C01", "counterfactual"]))

# === More C02 memories ===
new_mem.append(M("C02", "VP-3", "remained", "sole vector platform after VP-5 rejection",
    "After VP-5 rejection, VP-3 remained MGI's sole delivery vector platform. No other alternatives have been evaluated since.",
    "event", "ground_truth", "Dr. Marcus Chen", 1.0, "SRC-C02-16", "program_record",
    250, 0, 1, 1, ["C02"]))

new_mem.append(M("C02", "NanoVec Therapeutics", "subsequently_reported", "VP-5 success in oncology application",
    "NanoVec Therapeutics subsequently reported successful use of VP-5 in an oncology application in 2031, suggesting the vector may be viable in different contexts.",
    "event", "ground_truth", "system", 0.8, "SRC-C02-17", "publication",
    730, 2, 5, 2, ["C02"], scope="public"))

new_mem.append(M("C02", "VP-5 inflammatory dose", "was", "1e12 particles/kg in mice",
    "The VP-5 inflammatory response was observed at doses of 1e12 particles/kg in mice, which would extrapolate to clinically relevant doses in humans.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.9, "SRC-C02-18", "toxicology_data",
    185, 2, 3, 1, ["C02"]))

# === More C03 memories ===
new_mem.append(M("C03", "MERIT-1 patients", "had_no_liver_biopsies", "performed",
    "No liver biopsies were performed on MERIT-1 patients. Monitoring relied solely on blood-based liver function panels.",
    "event", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C03-16", "monitoring_record",
    660, 1, 2, 1, ["C03"]))

new_mem.append(M("C03", "liver monitoring costs", "totaled", "$180,000 for MERIT-1",
    "Weekly liver monitoring for all 24 MERIT-1 patients over 12 months cost approximately $180,000 in lab fees.",
    "event", "ground_truth", "Priya Sharma", 0.85, "SRC-C03-17", "cost_report",
    660, 1, 3, 1, ["C03"]))

new_mem.append(M("C03", "AAV liver tropism", "is_well_documented_in", "gene therapy literature",
    "AAV liver tropism is well-documented in gene therapy literature, making hepatotoxicity monitoring standard practice for all AAV-based trials.",
    "fact", "ground_truth", "system", 1.0, "SRC-C03-18", "medical_literature",
    0, 0, 1, 1, ["C03"]))

# === More C04 memories ===
new_mem.append(M("C04", "BLA pre-submission package", "was", "2,300 pages",
    "The complete BLA pre-submission package totaled 2,300 pages across CMC, nonclinical, and clinical modules.",
    "event", "counterfactual", "Jordan Reeves", 0.9, "SRC-C04-17", "regulatory_record",
    920, 1, 2, 1, ["C04", "counterfactual"]))

new_mem.append(M("C04", "FDA Type B meeting", "had_outcome_of", "proceed with caution",
    "The official outcome of the FDA Type B meeting was 'proceed with caution' — FDA did not reject the program but recommended additional data before filing.",
    "event", "ground_truth", "Jordan Reeves", 1.0, "SRC-C04-18", "meeting_outcome",
    930, 0, 2, 1, ["C04"]))

new_mem.append(M("C04", "MGI board", "approved_the", "BLA withdrawal decision unanimously",
    "The MGI board unanimously approved the BLA withdrawal decision, agreeing that premature submission risked a complete response letter.",
    "event", "ground_truth", "Dr. Elena Vasquez", 1.0, "SRC-C04-19", "board_minutes",
    950, 1, 2, 1, ["C04"]))

# === More C05 memories ===
new_mem.append(M("C05", "Dr. Chen", "was_disappointed_by", "MGT-603 rejection",
    "Dr. Chen expressed disappointment at the MGT-603 board decision, noting it represented 6 months of his research team's work.",
    "event", "ground_truth", "Dr. Marcus Chen", 0.9, "SRC-C05-15", "personal_record",
    465, 1, 2, 1, ["C05"]))

new_mem.append(M("C05", "MGT-603 research materials", "were_archived", "in MGI research library",
    "All MGT-603 proposal materials, feasibility data, and technical designs were archived in the MGI research library for potential future reference.",
    "event", "ground_truth", "system", 1.0, "SRC-C05-16", "archive_record",
    470, 0, 1, 1, ["C05"]))

new_mem.append(M("C05", "CF gene therapy field", "has_not_produced", "any approved product as of 2032",
    "As of 2032, no company has received regulatory approval for a CF gene therapy, suggesting the field remains challenging.",
    "fact", "ground_truth", "system", 1.0, "SRC-C05-17", "industry_report",
    1100, 0, 1, 1, ["C05"]))

# === More C06 memories ===
new_mem.append(M("C06", "NOVA-1 site", "was", "MGI's own clinical facility",
    "NOVA-1 was conducted at MGI's own on-site clinical facility, not at an external academic medical center.",
    "fact", "ground_truth", "system", 1.0, "SRC-C06-19", "trial_registry",
    305, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "MGT-710 IP", "was_developed_with", "CRISPR licensing from Broad Institute",
    "MGT-710 was developed under a CRISPR licensing agreement with the Broad Institute. The license remains active despite program suspension.",
    "fact", "ground_truth", "Jordan Reeves", 0.95, "SRC-C06-20", "license_record",
    200, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 termination report", "was_filed_with", "ClinicalTrials.gov",
    "The NOVA-1 termination was reported to ClinicalTrials.gov with status 'Terminated' and reason 'Safety (immune-mediated adverse events).'",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-21", "regulatory_filing",
    640, 1, 2, 1, ["C06"], scope="public"))

new_mem.append(M("C06", "NOVA-1 cost", "was", "approximately $4.5 million before termination",
    "NOVA-1 cost approximately $4.5 million before termination, including patient recruitment, treatment, and monitoring.",
    "event", "ground_truth", "Priya Sharma", 0.85, "SRC-C06-22", "financial_record",
    640, 1, 3, 1, ["C06"]))

# === More C07 memories ===
new_mem.append(M("C07", "TRX-88", "has_IC50_of", "12 nM for protein stabilization in vitro",
    "Published academic studies show TRX-88 has an IC50 of 12 nM for protein stabilization in cell-free assays.",
    "fact", "ground_truth", "system", 1.0, "SRC-C07-15", "academic_paper",
    780, 1, 3, 1, ["C07"]))

new_mem.append(M("C07", "MGI", "did_not_allocate_any_budget_for", "combination therapy research",
    "No budget was allocated for MGT-401 + TRX-88 combination therapy research in any fiscal year. The simulations used existing compute allocation.",
    "event", "negation", "Priya Sharma", 1.0, "SRC-C07-16", "budget_record",
    860, 0, 1, 1, ["C07", "negation"]))

new_mem.append(M("C07", "combination therapy concept", "was_rated_as", "TRL 2 (technology concept formulated)",
    "The MGT-401 + TRX-88 combination was assessed at Technology Readiness Level 2 — concept formulated but no experimental proof of concept.",
    "observation", "ground_truth", "Dr. Elena Vasquez", 0.9, "SRC-C07-17", "technology_assessment",
    855, 1, 2, 1, ["C07"]))

# === Background fill ===
new_mem.append(M("bg", "MGI GMP facility", "produces", "VP-3 vector for clinical use",
    "MGI operates a GMP manufacturing facility for VP-3 vector production, with an annual capacity of 200 clinical doses.",
    "fact", "ground_truth", "Morgan Hale", 0.95, "SRC-BG32", "manufacturing_record",
    180, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "received", "FDA Orphan Drug Designation for MGT-401",
    "MGT-401 received FDA Orphan Drug Designation in 2029, providing regulatory advantages including tax credits and market exclusivity.",
    "event", "ground_truth", "Jordan Reeves", 1.0, "SRC-BG33", "regulatory_record",
    60, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "was_founded_by", "Dr. Vasquez and Dr. Chen in 2028",
    "MGI was co-founded by Dr. Elena Vasquez and Dr. Marcus Chen in 2028, backed by $150 million in Series A funding.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG34", "corporate_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI Series B funding", "raised", "$220 million in 2031",
    "MGI raised $220 million in Series B funding in 2031, primarily to support MGT-401 Phase III development and MGT-502 IND preparation.",
    "event", "ground_truth", "system", 1.0, "SRC-BG35", "financial_record",
    730, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "holds_patents_on", "VP-3 vector modifications and MGT-401 construct",
    "MGI holds 14 patents related to VP-3 vector modifications and the MGT-401 gene therapy construct.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG36", "ip_record",
    365, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI Scientific Advisory Board", "includes", "7 external experts and 3 internal members",
    "MGI's Scientific Advisory Board consists of 7 external academic experts and 3 internal senior scientists.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG37", "governance_record",
    30, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "is_classified_as", "clinical-stage biotechnology company",
    "MGI is classified as a clinical-stage biotechnology company with one completed Phase II trial and no approved products.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG38", "corporate_classification",
    1100, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "DMD gene therapy market", "is_projected_at", "$5.2 billion by 2035",
    "The global DMD gene therapy market is projected to reach $5.2 billion by 2035.",
    "fact", "ground_truth", "system", 0.8, "SRC-BG39", "market_report",
    730, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MERIT-1 primary endpoint", "was_met", "6-minute walk test improvement",
    "MERIT-1 met its primary endpoint: statistically significant improvement in the 6-minute walk test at 12 months.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-BG40", "trial_results",
    600, 2, 5, 2, ["background"]))

new_mem.append(M("bg", "MERIT-1 secondary endpoints", "showed", "improved muscle biopsy dystrophin levels",
    "MERIT-1 secondary endpoints showed increased dystrophin protein levels in muscle biopsies (mean 28% of normal vs 3% at baseline).",
    "observation", "ground_truth", "Dr. Marcus Chen", 0.95, "SRC-BG41", "trial_results",
    600, 3, 6, 2, ["background"]))

new_mem.append(M("bg", "MGI Quality Management System", "is_certified_to", "ISO 13485",
    "MGI's quality management system is certified to ISO 13485, covering design, development, and manufacturing of gene therapy products.",
    "fact", "ground_truth", "Morgan Hale", 1.0, "SRC-BG42", "quality_record",
    180, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI data infrastructure", "uses", "REDCap for clinical data capture",
    "MGI uses REDCap (Research Electronic Data Capture) for all clinical trial data management.",
    "fact", "ground_truth", "Priya Sharma", 1.0, "SRC-BG43", "it_record",
    90, 0, 1, 1, ["background"]))

# Extra contradiction/supersedes links
c01_cancel_id = [m["memory_id"] for m in memories if m.get("story_id") == "C01" and "was_cancelled" in m.get("predicate","")][0]
new_mem.append(M("C01", "MERIT-2", "has_status_of", "cancelled — never executed",
    "MERIT-2 has a final status of 'cancelled.' All planning artifacts (protocol, sites, budget) exist but no trial activities were ever executed.",
    "event", "ground_truth", "system", 1.0, "SRC-C01-25", "trial_registry",
    740, 0, 1, 1, ["C01", "negation"],
    supersedes=[m["memory_id"] for m in memories if m.get("story_id") == "C01" and "was_designed" in m.get("predicate","")][:1]))

c05_reject_id = [m["memory_id"] for m in memories if m.get("story_id") == "C05" and "not_approved" in m.get("predicate","")][0]
new_mem.append(M("C05", "MGT-603", "has_status_of", "rejected — proposal only",
    "MGT-603 has a final status of 'rejected at proposal stage.' No development work was initiated beyond feasibility analysis.",
    "event", "ground_truth", "system", 1.0, "SRC-C05-18", "program_registry",
    460, 0, 1, 1, ["C05", "negation"],
    supersedes=[m["memory_id"] for m in memories if m.get("story_id") == "C05" and "proposed" in m.get("predicate","")][:1]))

new_mem.append(M("C06", "MGT-710", "has_status_of", "suspended — pending reformulation",
    "MGT-710 has a status of 'suspended pending reformulation.' No timeline for resumption has been set.",
    "event", "ground_truth", "system", 1.0, "SRC-C06-23", "program_registry",
    650, 0, 1, 1, ["C06", "negation"],
    supersedes=[m["memory_id"] for m in memories if m.get("story_id") == "C06" and "was_initiated" in m.get("predicate","")][:1]))

new_mem.append(M("C04", "BLA for MGT-401", "has_status_of", "withdrawn — pending 3-year data",
    "The MGT-401 BLA has a status of 'withdrawn pending 3-year data.' Target resubmission is Q2 2033.",
    "event", "ground_truth", "system", 1.0, "SRC-C04-20", "regulatory_status",
    960, 0, 1, 1, ["C04", "negation"],
    supersedes=[m["memory_id"] for m in memories if m.get("story_id") == "C04" and "was_drafted" in m.get("predicate","")][:1]))

# Additional queries to reach 76+
new_q.append(Q(
    "What CRO was contracted for MERIT-2 and what happened to the contract?",
    "factual_recall",
    ["Parexel International was contracted",
     "The contract was terminated with a $1.2M penalty after cancellation"],
    ["The CRO contract was cancelled along with the trial"],
    ["Parexel conducted the trial", "The CRO completed the work"],
    [n["memory_id"] for n in new_mem if "Parexel" in n.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "How much money was spent on MERIT-2 preparation before cancellation?",
    "counterfactual_distinction",
    ["Approximately $2.1 million was spent on preparation",
     "The cancellation saved approximately $32 million in direct costs"],
    ["A fraction of the $34.2M budget was spent before cancellation"],
    ["$34.2 million was spent", "The full budget was used",
     "MERIT-2 ran to completion"],
    [n["memory_id"] for n in new_mem if "$32 million" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and "budget" in m.get("predicate","")][:1],
    [],
    "medium"
))

new_q.append(Q(
    "Has NanoVec Therapeutics had any success with VP-5 since MGI rejected it?",
    "scope_preservation",
    ["NanoVec reported successful VP-5 use in an oncology application in 2031",
     "The vector may be viable in different therapeutic contexts"],
    ["VP-5 found success elsewhere despite being rejected for gene therapy"],
    ["VP-5 failed everywhere", "MGI's rejection proved VP-5 was worthless"],
    [n["memory_id"] for n in new_mem if "NanoVec" in n.get("text","") and "oncology" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if "was_rejected_by" in m.get("predicate","")][:1],
    "medium",
    scope=True
))

new_q.append(Q(
    "What is the Technology Readiness Level of the MGT-401 + TRX-88 combination?",
    "scope_preservation",
    ["TRL 2 — technology concept formulated but no experimental proof of concept"],
    ["Very early stage with only computational results"],
    ["TRL 6 or higher", "Clinical readiness", "Experimental proof exists"],
    [n["memory_id"] for n in new_mem if "TRL" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "simulations" in m.get("subject","")][:1],
    "medium",
    scope=True
))

new_q.append(Q(
    "How much did NOVA-1 cost before it was terminated?",
    "factual_recall",
    ["Approximately $4.5 million"],
    ["$4.5M including recruitment, treatment, and monitoring"],
    ["The trial was free", "NOVA-1 completed within budget"],
    [n["memory_id"] for n in new_mem if "NOVA-1 cost" in n.get("subject","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "What is the final status of all four MGI gene therapy programs?",
    "status_tracking",
    ["MGT-401: active, Phase II complete, BLA pending",
     "MGT-502: active, late preclinical, IND expected Q1 2033",
     "MGT-603: rejected at proposal stage, never started",
     "MGT-710: suspended pending CRISPR delivery reformulation"],
    ["Two active, one never started, one suspended"],
    ["All four are in trials", "Three are active",
     "MGT-603 is in development", "MGT-710 is in trials"],
    [n["memory_id"] for n in new_mem if "has_status_of" in n.get("predicate","")][:4] +
    [m["memory_id"] for m in memories if "MGT-502" in m.get("subject","") and "preclinical" in m.get("text","")][:1],
    [],
    "hard",
    notes="Comprehensive status query requiring synthesis across all programs"
))

new_q.append(Q(
    "What data management tools and systems does MGI use for clinical trials?",
    "factual_recall",
    ["MGI uses REDCap for clinical data capture"],
    ["REDCap-based electronic data management"],
    ["MGI uses a custom system", "No data management system exists"],
    [n["memory_id"] for n in new_mem if "REDCap" in n.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "How was MERIT-1's efficacy demonstrated and what were the key results?",
    "factual_recall",
    ["Primary endpoint met: 6-minute walk test improvement (+38 meters, p<0.01)",
     "Secondary: dystrophin levels increased to 28% of normal from 3% baseline"],
    ["Significant functional and molecular improvement demonstrated"],
    ["MERIT-1 failed", "No efficacy was shown", "Results were inconclusive"],
    [m["memory_id"] for m in memories if "demonstrated" in m.get("predicate","") and "MERIT-1" in m.get("subject","")][:1] +
    [n["memory_id"] for n in new_mem if "primary endpoint" in n.get("predicate","").lower() or "secondary" in n.get("subject","").lower()][:2],
    [],
    "easy"
))

new_q.append(Q(
    "What regulatory designations does MGT-401 have?",
    "factual_recall",
    ["MGT-401 has FDA Orphan Drug Designation (granted 2029)"],
    ["The designation provides tax credits and market exclusivity"],
    ["MGT-401 is FDA approved", "No designations have been granted"],
    [n["memory_id"] for n in new_mem if "Orphan Drug" in n.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Is MGI's CRISPR license for MGT-710 still active?",
    "status_tracking",
    ["Yes, the CRISPR license from the Broad Institute remains active",
     "It continues despite program suspension"],
    ["The license is maintained for potential future use"],
    ["The license was terminated", "MGI lost CRISPR rights"],
    [n["memory_id"] for n in new_mem if "Broad Institute" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "suspended" in m.get("predicate","")][:1],
    "easy"
))

new_q.append(Q(
    "What happened to the MERIT-2 budget after cancellation?",
    "factual_recall",
    ["$18 million was reallocated to accelerate MGT-502 SMA program development"],
    ["Funds were redirected to other programs after cancellation"],
    ["The budget was returned to investors", "All money was lost",
     "The budget funded MERIT-2 operations"],
    [m["memory_id"] for m in memories if "reallocated" in m.get("predicate","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Did any MGI program ever reach Phase III?",
    "negation_detection",
    ["No MGI program has reached Phase III",
     "MERIT-2 (Phase III for MGT-401) was designed but cancelled before enrollment"],
    ["Phase III was planned but never executed"],
    ["MERIT-2 was a completed Phase III trial", "MGT-401 Phase III is underway",
     "Phase III showed positive results"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and ("was_designed" in m.get("predicate","") or "was_cancelled" in m.get("predicate",""))][:2],
    [],
    "medium"
))

new_q.append(Q(
    "Were the MGT-603 proposal materials preserved or destroyed?",
    "factual_recall",
    ["All materials were archived in the MGI research library for potential future reference"],
    ["The work was preserved despite the program not proceeding"],
    ["Materials were destroyed", "No record exists of MGT-603"],
    [n["memory_id"] for n in new_mem if "archived" in n.get("predicate","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "What liver function tests were included in MERIT-1 monitoring and what were the results?",
    "evidence_absence",
    ["ALT, AST, total bilirubin, and GGT were monitored weekly",
     "All results were within normal limits for all 24 patients"],
    ["Comprehensive liver monitoring showed no abnormalities"],
    ["Abnormal results were found", "Liver biopsies showed damage",
     "Monitoring was inadequate"],
    [m["memory_id"] for m in memories if "ALT, AST" in m.get("text","") or "all normal" in m.get("text","").lower()][:2],
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "risk" in m.get("text","")][:1],
    "medium"
))

new_q.append(Q(
    "Has any company achieved regulatory approval for a CF gene therapy?",
    "factual_recall",
    ["No company has received regulatory approval for a CF gene therapy as of 2032"],
    ["The CF gene therapy field remains challenging without approved products"],
    ["A CF gene therapy has been approved", "MGI's MGT-603 was approved"],
    [n["memory_id"] for n in new_mem if "no company" in n.get("text","").lower() and "CF" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C05" and "never_entered" in m.get("predicate","")][:1],
    "easy"
))

new_q.append(Q(
    "Where was NOVA-1 conducted and how does that differ from MERIT-1?",
    "confusion_resistance",
    ["NOVA-1 was conducted at MGI's own clinical facility",
     "MERIT-1 was conducted at Duke University Medical Center"],
    ["Different locations for different trials"],
    ["Both were at Duke", "Both were at MGI's facility",
     "NOVA-1 was multi-site"],
    [n["memory_id"] for n in new_mem if "own clinical facility" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if "conducted_at" in m.get("predicate","") and "MERIT-1" in m.get("subject","")][:1],
    [],
    "easy",
    disambiguate=True
))

new_q.append(Q(
    "Was any budget specifically allocated for the TRX-88 combination therapy research?",
    "negation_detection",
    ["No budget was allocated for combination therapy research",
     "Simulations used existing compute allocation"],
    ["The research used no dedicated funding"],
    ["Budget was allocated", "Significant investment was made",
     "A dedicated team was funded"],
    [n["memory_id"] for n in new_mem if "did_not_allocate" in n.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "simulations" in m.get("subject","")][:1],
    "medium"
))

new_q.append(Q(
    "How much total funding has MGI raised?",
    "factual_recall",
    ["$150 million Series A (2028) and $220 million Series B (2031)",
     "Total: $370 million"],
    ["Over $350 million across two funding rounds"],
    ["MGI is publicly traded", "MGI has no funding"],
    [n["memory_id"] for n in new_mem if "Series A" in n.get("text","") or "Series B" in n.get("text","")][:2],
    [],
    "easy"
))

new_q.append(Q(
    "What is the complete list of things MGI planned but never executed?",
    "counterfactual_distinction",
    ["MERIT-2 Phase III trial — cancelled before enrollment",
     "MGT-603 CF program — rejected at proposal",
     "VP-5 vector adoption — rejected after evaluation",
     "BLA submission for MGT-401 — withdrawn before filing",
     "MGT-401 + TRX-88 combination — theoretical only"],
    ["Multiple plans across trials, programs, vectors, and regulatory filings were not executed"],
    ["All plans were executed", "Only one plan was cancelled",
     "Everything MGI planned succeeded"],
    [n["memory_id"] for n in new_mem if "has_status_of" in n.get("predicate","")][:4] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "was_never_tested" in m.get("predicate","")][:1],
    [],
    "hard",
    notes="Comprehensive counterfactual synthesis across all cases"
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

print(f"Round 4: {len(memories)} memories, {len(queries)} queries")
