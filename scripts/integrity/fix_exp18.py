#!/usr/bin/env python3
"""Exp18 Round 1 expansion: 44 → ~110 memories, 10 → ~30 queries."""

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

mid_counter = len(memories) + 1

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp18-r1-{mid_counter}".encode()).hexdigest()[:8]
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

# More background
new_mem.append(M("bg", "Priya Sharma", "holds_role", "Data Analytics Lead",
    "Priya Sharma is the Data Analytics Lead at MGI, responsible for biostatistics and trial data analysis.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG11", "hr_record",
    10, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Dr. Ravi Patel", "holds_role", "Computational Biology Lead",
    "Dr. Ravi Patel heads the computational biology division at MGI.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG12", "hr_record",
    10, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Morgan Hale", "holds_role", "Quality Assurance Manager",
    "Morgan Hale manages quality assurance at MGI, overseeing GMP compliance.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG13", "hr_record",
    10, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Lisa Cartwright", "holds_role", "Patient Advocacy Director",
    "Lisa Cartwright serves as Patient Advocacy Director at MGI.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG14", "hr_record",
    10, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MERIT-1", "was_a", "Phase II trial for MGT-401",
    "MERIT-1 was the Phase II clinical trial for MGT-401, enrolling 24 DMD patients aged 6-14.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG15", "trial_registry",
    200, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MERIT-1", "demonstrated", "functional improvement",
    "MERIT-1 demonstrated statistically significant improvement in the 6-minute walk test (mean +38 meters, p<0.01) at 12 months.",
    "observation", "ground_truth", "Dr. Amara Obi", 0.95, "SRC-BG16", "trial_results",
    600, 2, 5, 2, ["background"]))

new_mem.append(M("bg", "MGT-710", "is_based_on", "CRISPR gene editing",
    "MGT-710 uses CRISPR-Cas9 gene editing to correct the sickle cell mutation in HBB gene.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG17", "program_record",
    200, 0, 1, 1, ["background"]))

# C01 expansion: more details about the trial that never launched
new_mem.append(M("C01", "MERIT-2", "had_primary_endpoint_of", "North Star Ambulatory Assessment",
    "MERIT-2's primary endpoint was a 2-point improvement on the North Star Ambulatory Assessment at 18 months.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-8", "protocol_document",
    200, 1, 3, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "MERIT-2", "had_planned_enrollment_of", "120 patients",
    "MERIT-2 planned to enroll 120 patients across 3 sites, randomized 2:1 treatment to placebo.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-9", "protocol_document",
    200, 1, 3, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "Genexis Corp", "published_data_showing", "similar DMD endpoint improvement",
    "Genexis Corp published Phase II data showing their GNX-201 achieved a 2.3-point NSAA improvement, making MERIT-2's chosen endpoint potentially outdated.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.9, "SRC-C01-10", "publication",
    700, 2, 5, 2, ["C01"]))

new_mem.append(M("C01", "MERIT-2 budget", "was_reallocated_to", "MGT-502 development",
    "After MERIT-2 cancellation, $18 million of the $34.2M budget was reallocated to accelerate MGT-502 SMA program development.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.95, "SRC-C01-11", "budget_record",
    750, 1, 2, 1, ["C01"]))

# C02 expansion
new_mem.append(M("C02", "VP-5", "was_developed_by", "NanoVec Therapeutics",
    "VP-5 was developed by NanoVec Therapeutics and licensed to MGI for evaluation as a delivery vector.",
    "fact", "ground_truth", "system", 1.0, "SRC-C02-5", "licensing_record",
    100, 0, 1, 1, ["C02"]))

new_mem.append(M("C02", "VP-5", "showed_in_animal_tests", "liver accumulation",
    "In biodistribution studies, VP-5 showed 4x higher liver accumulation than VP-3, raising hepatotoxicity concerns.",
    "observation", "ground_truth", "Dr. Felix Brennan", 0.9, "SRC-C02-6", "biodistribution_report",
    170, 2, 4, 1, ["C02"]))

new_mem.append(M("C02", "Dr. Marcus Chen", "advocated_for", "VP-5 adoption",
    "Dr. Chen was the sole dissenting voice on the advisory board, arguing VP-5's efficiency advantages outweighed the inflammatory risk.",
    "event", "ground_truth", "Dr. Marcus Chen", 0.85, "SRC-C02-7", "board_minutes",
    210, 1, 2, 1, ["C02"]))

new_mem.append(M("C02", "VP-5 license", "was_returned_to", "NanoVec Therapeutics",
    "Following the rejection decision, MGI returned the VP-5 license to NanoVec Therapeutics in November 2029.",
    "event", "ground_truth", "Jordan Reeves", 1.0, "SRC-C02-8", "contract_record",
    240, 1, 2, 1, ["C02", "negation"]))

# C03 expansion
new_mem.append(M("C03", "hepatotoxicity risk", "was_based_on", "AAV8 literature",
    "The hepatotoxicity concern for MGT-401 was based on published literature showing AAV8 liver toxicity in high-dose NHP studies.",
    "observation", "contextual_true", "Dr. Felix Brennan", 0.8, "SRC-C03-5", "literature_review",
    90, 2, 5, 2, ["C03"]))

new_mem.append(M("C03", "MERIT-1", "used_dose_below", "hepatotoxicity threshold",
    "MERIT-1 used doses 10x below the threshold associated with hepatotoxicity in NHP studies, which may explain the clean safety profile.",
    "observation", "contextual_true", "Dr. Felix Brennan", 0.85, "SRC-C03-6", "dose_analysis",
    665, 2, 4, 1, ["C03"]))

new_mem.append(M("C03", "Dr. Felix Brennan", "recommended_continuing", "liver monitoring in future trials",
    "Despite clean MERIT-1 results, Dr. Brennan recommended continuing hepatotoxicity monitoring in all future MGT-401 trials as a precautionary measure.",
    "event", "ground_truth", "Dr. Felix Brennan", 0.95, "SRC-C03-7", "safety_recommendation",
    690, 1, 2, 1, ["C03"]))

# C04 expansion
new_mem.append(M("C04", "BLA for MGT-401", "contained_sections_on", "chemistry, manufacturing, controls",
    "The draft BLA for MGT-401 contained completed sections on chemistry, manufacturing, and controls (CMC), nonclinical studies, and clinical data from MERIT-1.",
    "event", "counterfactual", "Jordan Reeves", 0.9, "SRC-C04-6", "regulatory_record",
    700, 1, 3, 1, ["C04", "counterfactual"]))

new_mem.append(M("C04", "FDA", "acknowledged", "MERIT-1 efficacy data was promising",
    "During the pre-submission meeting, FDA acknowledged the MERIT-1 efficacy data was promising but insufficient alone for approval.",
    "event", "ground_truth", "Jordan Reeves", 0.95, "SRC-C04-7", "meeting_minutes",
    930, 0, 2, 1, ["C04"]))

new_mem.append(M("C04", "revised BLA timeline", "targets", "Q2 2033",
    "The revised BLA submission timeline targets Q2 2033, after 3-year MERIT-1 follow-up data is available.",
    "event", "ground_truth", "Jordan Reeves", 0.9, "SRC-C04-8", "regulatory_plan",
    960, 1, 2, 1, ["C04"]))

# C05 expansion
new_mem.append(M("C05", "MGT-603 feasibility study", "estimated_cost_of", "$52 million over 5 years",
    "The MGT-603 feasibility study projected total program cost of $52 million over 5 years, including Phase I and Phase II trials.",
    "event", "counterfactual", "Priya Sharma", 0.85, "SRC-C05-6", "budget_projection",
    430, 1, 3, 1, ["C05", "counterfactual"]))

new_mem.append(M("C05", "MGT-603", "would_have_used", "VP-3 vector platform",
    "The MGT-603 proposal specified using the VP-3 AAV vector platform, modified for lung epithelial targeting.",
    "event", "counterfactual", "Dr. Marcus Chen", 0.85, "SRC-C05-7", "proposal_document",
    395, 1, 3, 1, ["C05", "counterfactual"]))

new_mem.append(M("C05", "Lisa Cartwright", "supported", "MGT-603 program",
    "Lisa Cartwright advocated for MGT-603 before the board, citing unmet need in the CF patient community.",
    "event", "ground_truth", "Lisa Cartwright", 0.9, "SRC-C05-8", "board_minutes",
    450, 1, 2, 1, ["C05"]))

# C06 expansion
new_mem.append(M("C06", "NOVA-1 adverse events", "were_classified_as", "immune-mediated reactions",
    "The 3 NOVA-1 adverse events were classified as immune-mediated reactions to the CRISPR delivery complex, manifesting as elevated CRP, transient fever, and joint inflammation.",
    "observation", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C06-6", "ae_classification",
    545, 1, 3, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 patients", "recovered_fully", "within 2 weeks",
    "All 3 NOVA-1 patients who experienced adverse events recovered fully within 2 weeks with corticosteroid treatment.",
    "observation", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C06-7", "follow_up_report",
    560, 2, 3, 1, ["C06"]))

new_mem.append(M("C06", "MGT-710 program", "was_suspended", "pending reformulation",
    "Following NOVA-1 termination, the MGT-710 program was suspended pending development of a less immunogenic CRISPR delivery system.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.95, "SRC-C06-8", "program_status",
    640, 1, 2, 1, ["C06"]))

new_mem.append(M("C06", "5 enrolled NOVA-1 patients", "were_offered", "alternative treatment referrals",
    "The 5 enrolled but untreated NOVA-1 patients were offered referrals to competing sickle cell treatment trials.",
    "event", "ground_truth", "Lisa Cartwright", 1.0, "SRC-C06-9", "patient_care_record",
    640, 1, 2, 1, ["C06"]))

# C07 expansion
new_mem.append(M("C07", "TRX-88", "is_a", "small-molecule protein chaperone",
    "TRX-88 is a small-molecule protein chaperone developed at MIT, shown to stabilize misfolded proteins in neurodegenerative disease models.",
    "fact", "ground_truth", "system", 1.0, "SRC-C07-5", "literature",
    780, 1, 3, 1, ["C07"]))

new_mem.append(M("C07", "Vasquez whitepaper", "was_presented_at", "MGI quarterly science meeting",
    "Dr. Vasquez presented the combination therapy whitepaper at the Q3 2031 science meeting. It was received as an interesting theoretical direction but no action items were assigned.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.9, "SRC-C07-6", "meeting_minutes",
    850, 1, 2, 1, ["C07"]))

new_mem.append(M("C07", "Dr. Ravi Patel", "noted_limitations_of", "in silico results",
    "Dr. Patel explicitly cautioned that in silico results cannot predict in vivo outcomes and recommended in vitro validation before any clinical consideration.",
    "event", "ground_truth", "Dr. Ravi Patel", 0.9, "SRC-C07-7", "meeting_minutes",
    850, 1, 2, 1, ["C07"]))

# Cross-cutting memories
new_mem.append(M("bg", "MGI", "has_total_active_programs", "two (MGT-401 and MGT-502)",
    "As of 2032, MGI has two active therapeutic programs: MGT-401 for DMD and MGT-502 for SMA. MGT-603 was never started and MGT-710 is suspended.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG18", "program_registry",
    1100, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "has_completed_trials", "only MERIT-1",
    "As of 2032, MERIT-1 is the only clinical trial MGI has completed. MERIT-2 was cancelled before launch and NOVA-1 was terminated early.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG19", "trial_registry",
    1100, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI annual review 2031", "summarized", "one completion, two failures",
    "The 2031 annual review noted MGI completed MERIT-1 successfully but faced setbacks: MERIT-2 cancelled, NOVA-1 terminated, BLA withdrawn, and MGT-603 not approved.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.95, "SRC-BG20", "annual_report",
    1050, 1, 3, 1, ["background"]))

# Additional queries
new_q.append(Q(
    "What vector platform does MGI use for its gene therapy programs?",
    "factual_recall",
    ["MGI uses the VP-3 AAV delivery vector",
     "VP-5 lipid nanoparticle was evaluated but rejected"],
    ["VP-3 is the adopted vector; VP-5 was rejected due to inflammatory concerns"],
    ["VP-5 is used", "MGI uses lipid nanoparticles", "VP-5 is the primary vector"],
    [m["memory_id"] for m in memories if "VP-3" in m.get("subject","") or "VP-5" in m.get("subject","")][:4],
    [],
    "medium"
))

new_q.append(Q(
    "Did the BLA for MGT-401 get submitted to the FDA?",
    "negation_detection",
    ["The BLA was never formally submitted to FDA",
     "It was withdrawn before submission after FDA raised concerns about durability data"],
    ["The BLA was drafted but withdrawn; resubmission is planned for Q2 2033"],
    ["The BLA was submitted", "FDA is reviewing the BLA", "The BLA was rejected"],
    [m["memory_id"] for m in memories if "BLA" in m.get("subject","") and "never" in m.get("predicate","")][:2] +
    [m["memory_id"] for m in memories if "was_withdrawn" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if "BLA" in m.get("subject","") and "was_drafted" in m.get("predicate","")][:1],
    "medium"
))

new_q.append(Q(
    "What were the adverse events in NOVA-1 and were they related to liver toxicity?",
    "confusion_resistance",
    ["NOVA-1 adverse events were immune-mediated reactions (CRP, fever, joint pain)",
     "They were NOT hepatotoxicity or liver-related"],
    ["The events were classified as immune reactions to the CRISPR delivery complex"],
    ["NOVA-1 caused liver damage", "Hepatotoxicity was observed in NOVA-1",
     "NOVA-1 adverse events were liver-related"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "adverse" in m.get("text","").lower()][:3],
    [m["memory_id"] for m in memories if m.get("story_id") == "C03"][:2],
    "hard",
    conflict=True,
    notes="Must distinguish immune reactions from hepatotoxicity across C03/C06"
))

new_q.append(Q(
    "Was there any evidence that TRX-88 improves dystrophin function?",
    "scope_preservation",
    ["In silico simulations predicted 35% protein stability improvement",
     "No experimental evidence exists — results are computational only"],
    ["Simulations suggested potential benefit but no in vitro or in vivo confirmation"],
    ["Clinical evidence shows improvement", "Animal studies confirmed benefit",
     "TRX-88 was tested in patients"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C07"][:4],
    [],
    "hard",
    scope=True,
    notes="Must correctly scope results as in silico only"
))

new_q.append(Q(
    "Why was the MGT-603 CF program not pursued?",
    "factual_recall",
    ["Bioethics committee raised concerns about patient population size",
     "Board voted to redirect resources to MGT-401 and MGT-502"],
    ["Ethics concerns and resource prioritization led to the decision"],
    ["MGT-603 failed clinical trials", "MGT-603 was unsafe",
     "MGT-603 was technically infeasible"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C05" and ("not_approved" in m.get("predicate","") or "raised_concerns" in m.get("predicate",""))][:2],
    [m["memory_id"] for m in memories if m.get("story_id") == "C05" and "feasibility" in m.get("text","").lower()][:1],
    "medium"
))

new_q.append(Q(
    "How many clinical sites were selected for the MERIT-2 trial?",
    "counterfactual_distinction",
    ["Three sites were selected: Duke, Johns Hopkins, and CHOP",
     "However, MERIT-2 was cancelled before any site activated or enrolled patients"],
    ["Sites were selected but the trial never launched"],
    ["Patients were enrolled at these sites", "The sites conducted the trial",
     "MERIT-2 ran at three locations"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and ("selected_sites" in m.get("predicate","") or "was_cancelled" in m.get("predicate",""))][:2],
    [],
    "medium",
    notes="Must clarify sites were selected but never activated"
))

new_q.append(Q(
    "What happened to the 5 NOVA-1 patients who didn't receive treatment?",
    "factual_recall",
    ["They were offered referrals to competing sickle cell treatment trials"],
    ["The untreated patients were redirected to alternative care"],
    ["All patients received treatment", "The 5 patients completed the trial"],
    [n["memory_id"] for n in new_mem if "offered" in n.get("predicate","") and "NOVA" in n.get("subject","")][:1] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "did_not_complete" in m.get("predicate","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Did Dr. Chen support or oppose the VP-5 rejection?",
    "factual_recall",
    ["Dr. Chen was the sole dissenting voice, advocating for VP-5 adoption",
     "He argued the efficiency advantages outweighed the inflammatory risk"],
    ["Chen opposed the rejection but was outvoted 7-1"],
    ["Chen supported the rejection", "Chen agreed VP-5 was dangerous"],
    [n["memory_id"] for n in new_mem if "Chen" in n.get("subject","") and "VP-5" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and "was_rejected" in m.get("predicate","")][:1],
    "easy"
))

new_q.append(Q(
    "What is the current status of the MGT-710 sickle cell program?",
    "status_tracking",
    ["MGT-710 is suspended pending reformulation of the CRISPR delivery system",
     "NOVA-1 trial was terminated after adverse events"],
    ["The program is on hold, not cancelled, but inactive"],
    ["MGT-710 is in active trials", "MGT-710 has been approved",
     "NOVA-1 is ongoing"],
    [n["memory_id"] for n in new_mem if "suspended" in n.get("predicate","")][:1] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "was_terminated" in m.get("predicate","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "was_initiated" in m.get("predicate","")][:1],
    "medium"
))

new_q.append(Q(
    "Has MGI ever had a safety concern about liver toxicity?",
    "evidence_absence",
    ["Hepatotoxicity was identified as a theoretical risk for MGT-401",
     "However, no hepatotoxicity events were ever observed in trials",
     "All liver panels in MERIT-1 were normal"],
    ["Concern existed based on AAV8 literature but was not realized in practice"],
    ["Liver toxicity was observed", "Patients had liver damage",
     "Hepatotoxicity was confirmed"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C03"][:4],
    [],
    "hard",
    notes="Must distinguish theoretical risk from actual observed events"
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

print(f"Round 1: {len(memories)} memories, {len(queries)} queries")
