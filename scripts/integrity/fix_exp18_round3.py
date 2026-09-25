#!/usr/bin/env python3
"""Exp18 Round 3 expansion: 111 → ~170 memories, 33 → ~55 queries."""

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

mid_counter = 400

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp18-r3-{mid_counter}".encode()).hexdigest()[:8]
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

# Build lookup
mem_by_story = {}
for m in memories:
    s = m.get("story_id", "")
    mem_by_story.setdefault(s, []).append(m)

# === More C01 depth ===
new_mem.append(M("C01", "MERIT-2 statistician", "designed_sample_size_of", "120 with 80% power",
    "Priya Sharma calculated that 120 patients (80:40 randomization) would provide 80% power to detect a 2-point NSAA improvement.",
    "event", "counterfactual", "Priya Sharma", 0.9, "SRC-C01-17", "statistical_design",
    210, 2, 4, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "CHOP site", "had_completed", "regulatory approvals for MERIT-2",
    "Children's Hospital of Philadelphia completed all local regulatory and ethics approvals for MERIT-2 by July 2030.",
    "event", "ground_truth", "Dr. Amara Obi", 0.9, "SRC-C01-18", "site_report",
    510, 1, 2, 1, ["C01"]))

new_mem.append(M("C01", "Johns Hopkins site", "had_identified", "potential MERIT-2 patients",
    "Johns Hopkins identified 32 potential MERIT-2 candidates from their DMD registry, but none were ever contacted for screening.",
    "event", "counterfactual", "Dr. Amara Obi", 0.85, "SRC-C01-19", "site_report",
    530, 1, 2, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "VP-3 manufacturing yield", "dropped_to", "40% of target",
    "VP-3 manufacturing yield at the contract facility dropped to 40% of the target needed for MERIT-2 supply.",
    "event", "ground_truth", "Morgan Hale", 0.95, "SRC-C01-20", "manufacturing_report",
    550, 1, 2, 1, ["C01"]))

# === More C02 depth ===
new_mem.append(M("C02", "VP-5 third evaluation", "tested", "dose-response in murine model",
    "The third VP-5 report characterized dose-dependent inflammatory markers at 3 dose levels in mice, confirming a clear dose-toxicity relationship.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.9, "SRC-C02-13", "toxicology_report",
    190, 2, 4, 1, ["C02"]))

new_mem.append(M("C02", "advisory board meeting", "lasted", "4 hours with extensive debate",
    "The advisory board meeting on VP-5 lasted 4 hours. Dr. Chen argued for conditional adoption with dose optimization; the majority cited unacceptable risk.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.95, "SRC-C02-14", "board_minutes",
    210, 1, 2, 1, ["C02"]))

new_mem.append(M("C02", "VP-5 evaluation data", "was_published_in", "Journal of Gene Medicine",
    "VP-5 evaluation data was published in the Journal of Gene Medicine as a negative result, contributing to the scientific literature on lipid nanoparticle vector safety.",
    "event", "ground_truth", "Dr. Marcus Chen", 0.9, "SRC-C02-15", "publication_record",
    300, 2, 5, 2, ["C02"], scope="public"))

# === More C03 depth ===
new_mem.append(M("C03", "AAV8 hepatotoxicity", "was_reported_in", "Sparks et al. 2028",
    "Sparks et al. (2028) reported dose-dependent hepatotoxicity in NHP receiving AAV8 at doses above 1e14 vg/kg, the primary basis for MGT-401 risk assessment.",
    "fact", "ground_truth", "system", 1.0, "SRC-C03-12", "literature",
    0, 0, 1, 1, ["C03"]))

new_mem.append(M("C03", "MERIT-1 dose", "was", "1e13 vg/kg — 10x below NHP toxicity threshold",
    "MERIT-1 used MGT-401 at 1e13 vg/kg, a full order of magnitude below the 1e14 vg/kg threshold associated with hepatotoxicity in the Sparks NHP study.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.95, "SRC-C03-13", "dose_comparison",
    300, 1, 3, 1, ["C03"]))

new_mem.append(M("C03", "MERIT-1 liver monitoring", "included", "ALT, AST, bilirubin, GGT weekly",
    "MERIT-1 liver monitoring included weekly ALT, AST, total bilirubin, and GGT panels for all 24 participants.",
    "event", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C03-14", "monitoring_protocol",
    300, 0, 2, 1, ["C03"]))

new_mem.append(M("C03", "no MERIT-1 patient", "required", "dose modification for liver concerns",
    "No MERIT-1 patient required dose modification, treatment delay, or early discontinuation due to liver function concerns.",
    "event", "negation", "Dr. Amara Obi", 1.0, "SRC-C03-15", "safety_report",
    660, 1, 2, 1, ["C03", "negation"]))

# === More C04 depth ===
new_mem.append(M("C04", "BLA nonclinical section", "included", "12 preclinical studies",
    "The nonclinical section of the draft BLA included data from 12 preclinical studies spanning biodistribution, toxicology, and pharmacology.",
    "event", "counterfactual", "Jordan Reeves", 0.9, "SRC-C04-14", "regulatory_record",
    770, 1, 3, 1, ["C04", "counterfactual"]))

new_mem.append(M("C04", "BLA team", "spent_8400_hours_on", "BLA preparation",
    "The MGI regulatory team logged approximately 8,400 person-hours on BLA preparation before the withdrawal decision.",
    "event", "ground_truth", "Jordan Reeves", 0.85, "SRC-C04-15", "time_tracking",
    950, 1, 2, 1, ["C04"]))

new_mem.append(M("C04", "BLA withdrawal", "did_not_result_in", "any FDA penalty or prejudice",
    "Since the BLA was withdrawn before formal submission, there was no FDA penalty, refusal-to-file, or negative precedent for future MGT-401 submissions.",
    "event", "negation", "Jordan Reeves", 1.0, "SRC-C04-16", "regulatory_analysis",
    960, 1, 2, 1, ["C04", "negation"]))

# === More C05 depth ===
new_mem.append(M("C05", "MGT-603 dual-vector approach", "was_novel_and", "untested in CF",
    "The dual-vector AAV approach proposed for MGT-603 had not been previously tested in any CF model. It was a novel technical approach without proof-of-concept.",
    "observation", "counterfactual", "Dr. Marcus Chen", 0.8, "SRC-C05-12", "technical_review",
    400, 2, 4, 1, ["C05", "counterfactual"]))

new_mem.append(M("C05", "existing CF therapies", "had_improved", "median survival to 56 years",
    "The board noted that existing CF therapies (CFTR modulators) had already improved median survival to 56 years, reducing the urgency for gene therapy.",
    "fact", "ground_truth", "Dr. Suki Tanaka", 0.9, "SRC-C05-13", "medical_review",
    455, 1, 2, 1, ["C05"]))

new_mem.append(M("C05", "MGT-603 IND", "was_never_filed", "with FDA",
    "No IND (Investigational New Drug) application was ever filed for MGT-603. The program stopped at the proposal stage.",
    "event", "negation", "system", 1.0, "SRC-C05-14", "regulatory_record",
    460, 0, 1, 1, ["C05", "negation"]))

# === More C06 depth ===
new_mem.append(M("C06", "NOVA-1 enrollment period", "was", "January to March 2030",
    "NOVA-1 enrolled 8 patients between January and March 2030.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-15", "enrollment_record",
    305, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 treatment period", "was", "March to May 2030 for 3 patients",
    "NOVA-1 treatment was administered to 3 patients between March and May 2030 before the DSMB pause.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-16", "treatment_record",
    365, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 informed consent", "mentioned", "potential immune reactions as risk",
    "The NOVA-1 informed consent form listed immune reactions as a potential risk, based on preclinical CRISPR delivery data.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C06-17", "consent_document",
    300, 0, 2, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 did_not_test", "efficacy", "due to early termination",
    "NOVA-1 was terminated before any efficacy assessment could be made. No efficacy data exists for MGT-710 in humans.",
    "event", "negation", "Dr. Amara Obi", 1.0, "SRC-C06-18", "trial_report",
    635, 0, 1, 1, ["C06", "negation"]))

# === More C07 depth ===
new_mem.append(M("C07", "Patel simulations", "ran_on", "MGI high-performance computing cluster",
    "Dr. Patel's simulations ran for 720 hours on MGI's HPC cluster, consuming approximately $15,000 in compute resources.",
    "event", "ground_truth", "Dr. Ravi Patel", 0.9, "SRC-C07-12", "compute_log",
    830, 2, 3, 1, ["C07"]))

new_mem.append(M("C07", "simulation", "did_not_model", "immune response or toxicity",
    "The Patel simulations modeled only protein-chaperone binding dynamics. They did not model immune response, toxicity, pharmacokinetics, or delivery.",
    "event", "negation", "Dr. Ravi Patel", 1.0, "SRC-C07-13", "simulation_limitations",
    835, 1, 2, 1, ["C07", "negation"]))

new_mem.append(M("C07", "Dr. Vasquez", "acknowledged_that", "combination therapy is years away from testing",
    "At the Q3 2031 meeting, Dr. Vasquez acknowledged that even if funded, combination therapy testing would require 2-3 years of preclinical work before any human trial.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.9, "SRC-C07-14", "meeting_minutes",
    850, 1, 2, 1, ["C07"]))

# === Cross-cutting and background ===
new_mem.append(M("bg", "MGI safety record", "shows", "no serious treatment-related adverse events in DMD trials",
    "MGI's safety record shows no serious treatment-related adverse events in its DMD program. MERIT-1 had a clean safety profile.",
    "fact", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-BG24", "safety_summary",
    700, 1, 3, 1, ["background"]))

new_mem.append(M("bg", "MGI annual budget", "is_approximately", "$85 million",
    "MGI's total annual operating budget is approximately $85 million, split between research, clinical operations, and manufacturing.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG25", "financial_record",
    365, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "employs", "approximately 340 staff",
    "MGI employs approximately 340 staff across research, clinical, regulatory, and administrative divisions.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG26", "hr_record",
    365, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "partners_with", "UNC Chapel Hill for basic research",
    "MGI maintains a research partnership with UNC Chapel Hill for basic gene therapy vector biology research.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG27", "partnership_record",
    180, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGT-502 SMA program", "is_in", "preclinical development",
    "As of 2032, MGT-502 is in late preclinical development, with an IND filing expected in Q1 2033.",
    "event", "ground_truth", "Dr. Marcus Chen", 0.9, "SRC-BG28", "program_status",
    1100, 1, 2, 1, ["background"]))

new_mem.append(M("bg", "DMD", "affects_approximately", "1 in 3,600 male births",
    "Duchenne muscular dystrophy affects approximately 1 in 3,600 male births worldwide.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG29", "medical_literature",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MERIT-1", "was_conducted_at", "Duke University Medical Center",
    "MERIT-1 was conducted at a single site: Duke University Medical Center.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG30", "trial_registry",
    200, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MERIT-1", "enrolled", "24 patients between June 2029 and January 2030",
    "MERIT-1 enrolled 24 DMD patients between June 2029 and January 2030.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-BG31", "enrollment_record",
    90, 0, 1, 1, ["background"]))

# Additional queries for round 3
new_q.append(Q(
    "Where was MERIT-1 conducted and how many patients participated?",
    "factual_recall",
    ["MERIT-1 was conducted at Duke University Medical Center",
     "24 patients were enrolled"],
    ["Single-site Phase II trial at Duke with 24 DMD patients"],
    ["MERIT-1 was a multi-site trial", "MERIT-1 had 120 patients",
     "MERIT-1 was conducted at three sites"],
    [m["memory_id"] for m in memories + new_mem if "MERIT-1" in m.get("subject","") and ("conducted" in m.get("predicate","") or "enrolled" in m.get("text",""))][:3],
    [m["memory_id"] for m in memories if "MERIT-2" in m.get("subject","") and "selected_sites" in m.get("predicate","")][:1],
    "easy",
    notes="Must not confuse MERIT-1 (single site, 24 patients) with MERIT-2 (3 planned sites, 120 planned)"
))

new_q.append(Q(
    "Were there any negative consequences from withdrawing the BLA?",
    "evidence_absence",
    ["No FDA penalty, refusal-to-file, or negative precedent resulted",
     "The BLA was withdrawn before formal submission"],
    ["No regulatory consequences since the BLA was never formally filed"],
    ["FDA penalized MGI", "The withdrawal damaged future submission prospects",
     "FDA rejected the BLA"],
    [n["memory_id"] for n in new_mem if "did_not_result_in" in n.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if "was_withdrawn" in m.get("predicate","")][:1],
    [],
    "medium"
))

new_q.append(Q(
    "Does any human efficacy data exist for MGT-710?",
    "negation_detection",
    ["No efficacy data exists for MGT-710 in humans",
     "NOVA-1 was terminated before efficacy assessment"],
    ["The trial ended too early to generate efficacy data"],
    ["MGT-710 showed efficacy", "NOVA-1 demonstrated treatment benefit",
     "Sickle cell patients improved"],
    [n["memory_id"] for n in new_mem if "did_not_test" in n.get("subject","") and "efficacy" in n.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if "was_terminated" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "was_initiated" in m.get("predicate","")][:1],
    "medium"
))

new_q.append(Q(
    "What were the limitations of the TRX-88 simulation study?",
    "scope_preservation",
    ["Simulations only modeled protein-chaperone binding dynamics",
     "Immune response, toxicity, pharmacokinetics, and delivery were NOT modeled"],
    ["The study was purely computational with major gaps"],
    ["The simulation was comprehensive", "All drug properties were modeled",
     "The results are clinically validated"],
    [n["memory_id"] for n in new_mem if "did_not_model" in n.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "noted_limitations" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C07" and "simulations" in m.get("subject","")][:1],
    "hard",
    scope=True
))

new_q.append(Q(
    "Did the VP-5 inflammatory response data contribute to any publications?",
    "factual_recall",
    ["VP-5 data was published in the Journal of Gene Medicine as a negative result"],
    ["The evaluation data was shared with the scientific community"],
    ["The data was never published", "VP-5 results were kept confidential"],
    [n["memory_id"] for n in new_mem if "Journal of Gene Medicine" in n.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "How many person-hours went into the BLA that was never submitted?",
    "counterfactual_distinction",
    ["Approximately 8,400 person-hours were spent on BLA preparation",
     "The BLA was withdrawn before formal submission"],
    ["Significant effort was invested in a submission that never materialized"],
    ["The BLA was submitted", "The hours resulted in an approved application"],
    [n["memory_id"] for n in new_mem if "8,400" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if "was_never" in m.get("predicate","") and "BLA" in m.get("subject","")][:1],
    [],
    "medium",
    notes="Tests ability to connect effort spent with unrealized outcome"
))

new_q.append(Q(
    "Was the hepatotoxicity risk for MGT-401 based on actual observations or preclinical literature?",
    "scope_preservation",
    ["Based on published NHP studies (Sparks et al. 2028) of AAV8 at high doses",
     "MERIT-1 used a dose 10x below the toxicity threshold"],
    ["Theoretical risk from literature, never observed in MGI's own trials"],
    ["Hepatotoxicity was observed at MGI", "MGI's own studies showed liver toxicity",
     "Patients had hepatotoxicity"],
    [n["memory_id"] for n in new_mem if "Sparks" in n.get("text","") or "10x below" in n.get("text","")][:2] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "zero_cases" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "risk" in m.get("predicate","")][:1],
    "hard",
    scope=True,
    notes="Must correctly attribute the risk source and distinguish from actual observations"
))

new_q.append(Q(
    "Were any DMD patients ever treated under the MERIT-2 protocol?",
    "negation_detection",
    ["No patients were ever treated under MERIT-2",
     "Patient screening never began at any site",
     "The trial was cancelled before enrollment"],
    ["Zero patients received treatment under MERIT-2"],
    ["Patients were treated", "MERIT-2 enrolled patients",
     "120 patients participated"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and ("never_enrolled" in m.get("predicate","") or "was_cancelled" in m.get("predicate",""))][:2] +
    [n["memory_id"] for n in new_mem if "never_began" in n.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and ("sites" in m.get("predicate","") or "was_designed" in m.get("predicate",""))][:2],
    "medium"
))

new_q.append(Q(
    "What is the prevalence of DMD and why is gene therapy important for it?",
    "factual_recall",
    ["DMD affects approximately 1 in 3,600 male births",
     "MGT-401 is MGI's flagship gene therapy program targeting DMD"],
    ["DMD is a rare disease with significant unmet need"],
    ["DMD is a common disease", "Gene therapy has already cured DMD"],
    [n["memory_id"] for n in new_mem if "3,600" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if "is_program_for" in m.get("predicate","") and "DMD" in m.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "What informed consent information did NOVA-1 patients receive about immune reaction risks?",
    "factual_recall",
    ["The consent form listed immune reactions as a potential risk",
     "This was based on preclinical CRISPR delivery data"],
    ["Patients were warned about potential immune reactions"],
    ["Patients were not warned", "Immune reactions were unexpected",
     "No consent was obtained"],
    [n["memory_id"] for n in new_mem if "informed consent" in n.get("subject","").lower()][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "adverse" in m.get("text","").lower()][:1],
    "easy"
))

new_q.append(Q(
    "Compare the cost and outcomes of MERIT-2 preparation vs VP-5 evaluation.",
    "counterfactual_distinction",
    ["MERIT-2 had a $34.2M budget but was cancelled before launch",
     "VP-5 evaluation cost $2.8M and the vector was rejected",
     "Neither resulted in a product advancing to patients"],
    ["Both were significant investments that did not lead to patient treatment"],
    ["MERIT-2 treated patients", "VP-5 is in clinical use",
     "Both investments paid off"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and "budget" in m.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and "was_cancelled" in m.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if "VP-5 evaluation cost" in m.get("subject","")][:1] +
    [m["memory_id"] for m in memories if "was_rejected_by" in m.get("predicate","")][:1],
    [],
    "hard",
    notes="Cross-case comparison of counterfactual investments"
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

print(f"Round 3: {len(memories)} memories, {len(queries)} queries")
