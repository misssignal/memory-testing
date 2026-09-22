#!/usr/bin/env python3
"""Exp19 Round 4 expansion: ~151 → ~210 memories, ~50 → ~78 queries."""

import json, hashlib, os, sys
from datetime import datetime, timedelta, timezone

d = sys.argv[1] if len(sys.argv) > 1 else "experiment_19_repeated_exposure"

with open(os.path.join(d, "memories.jsonl")) as f:
    memories = [json.loads(l) for l in f if l.strip()]
with open(os.path.join(d, "queries.jsonl")) as f:
    queries = [json.loads(l) for l in f if l.strip()]

UTC = timezone.utc
T0 = datetime(2030, 6, 1, tzinfo=UTC)

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

mid_counter = 600

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp19-r4-{mid_counter}".encode()).hexdigest()[:8]
    mid_counter += 1
    ev = T0 + timedelta(days=ev_off)
    ob = T0 + timedelta(days=ev_off + obs_off)
    au = T0 + timedelta(days=ev_off + obs_off + auth_off)
    ig = T0 + timedelta(days=ev_off + obs_off + auth_off + ing_off)
    return {
        "memory_id": f"E19-{_hash}",
        "experiment": "exp19_repeated_exposure",
        "story_id": story,
        "event_time": ts(ev), "observation_time": ts(ob),
        "authored_time": ts(au), "ingestion_time": ts(ig),
        "subject": subj, "predicate": pred, "object": obj, "text": text,
        "memory_type": etype, "truth_role": truth_role,
        "belief_holder": holder, "confidence": conf,
        "source_id": src_id, "source_type": src_type,
        "derived_from": derived or [], "supersedes": supersedes or [],
        "contradicts": contradicts or [], "duplicates": duplicates or [],
        "aliases": aliases or [], "scope": scope, "tags": tags
    }

new_memories = []
new_queries = []

# --- C01 additional memories ---
new_memories.append(M(
    "C01", "MV Atropatene", "inspected_by", "port state control officer",
    "Port state control officer conducted a follow-up inspection of MV Atropatene in September 2033, finding no deficiencies and rating the vessel 'satisfactory.' This independent inspection confirms the classification society's assessment.",
    "report", "ground_truth", "port state control", 0.95,
    "psc-reinspection-2033-09", "official_record", 120, 75, 2, 1,
    ["C01", "primary_source"]
))

new_memories.append(M(
    "C01", "broker network", "circulated", "MV Atropatene risk advisory",
    "A cargo broker circulated a risk advisory to charterers warning that MV Atropatene had 'ongoing hull integrity issues cited by multiple maritime authorities,' recommending higher insurance rates. This advisory was based on trade publication summaries, not original inspection data.",
    "report", "inflated_claim", "cargo broker", 0.40,
    "broker-risk-advisory", "commercial", 120, 55, 2, 1,
    ["C01", "repeated"]
))

new_memories.append(M(
    "C01", "MV Atropatene", "insurance_premium", "increased 15%",
    "Dmitri Volkov reported that MV Atropatene's insurance premium was increased by 15% at renewal due to 'multiple reports of hull concerns from diverse sources.' The premium increase was based on source quantity rather than the actual inspection finding.",
    "report", "contextual_true", "Dmitri Volkov", 0.80,
    "insurance-renewal-2034", "commercial", 120, 180, 10, 5,
    ["C01"]
))

# --- C02 additional memories ---
new_memories.append(M(
    "C02", "MV Turkmenbashi", "cargo_survey_by", "independent surveyor",
    "An independent cargo surveyor hired by the consignee measured MV Turkmenbashi's discharged cargo at 4,710 tonnes, consistent with the draft survey (4,705) and confirming the B/L weight (4,850) was the outlier. This is the 9th document recording the same discrepancy.",
    "report", "repeated_claim", "independent surveyor", 0.75,
    "consignee-survey", "commercial", 200, 8, 3, 1,
    ["C02", "repeated"]
))

new_memories.append(M(
    "C02", "cargo weight standards", "explained_by", "Leyla Hasanova",
    "Leyla Hasanova explained in a training document that B/L weights are often shipper-declared estimates, while draft surveys are physical measurements. A variance under 5% is standard and does not indicate fraud, tampering, or negligence.",
    "fact", "ground_truth", "Leyla Hasanova", 0.95,
    "cargo-training-doc", "institutional", 0, 0, 1, 1,
    ["C02", "primary_source"]
))

# --- C03 additional memories ---
new_memories.append(M(
    "C03", "MV Khazar Star", "fuel_tested_at", "Kuryk Terminal",
    "The fuel sample from MV Khazar Star was drawn at Kuryk Terminal on 2031-06-15 from the bunker delivery pipeline. The terminal's fuel supply certificate showed sulfur content at 0.48%, suggesting the elevated initial reading was a sampling or testing anomaly.",
    "fact", "ground_truth", "Kuryk Terminal operations", 0.90,
    "kuryk-fuel-cert-2031", "commercial", 365, 0, 1, 1,
    ["C03", "primary_source"]
))

new_memories.append(M(
    "C03", "MV Khazar Star fuel", "insurance_implications", "premium review",
    "MV Khazar Star's insurer placed the vessel under premium review citing 'fuel compliance concerns documented by 5 regulatory sources.' The insurer was not aware of the retest clearing the vessel.",
    "report", "contextual_true", "Dmitri Volkov", 0.70,
    "insurance-premium-review", "commercial", 365, 45, 5, 2,
    ["C03", "repeated"]
))

# --- C04 additional memories ---
new_memories.append(M(
    "C04", "MV Khazar Star", "delayed_at", "Astara Anchorage",
    "MV Khazar Star was among the 4 vessels detained at Astara Anchorage during Storm SA-2032-019. Its delay report was filed separately with the Kazakh Maritime Administration, making it the 5th vessel-specific report for the same event.",
    "report", "repeated_claim", "MV Khazar Star master", 0.70,
    "khazar-star-delay", "commercial", 472, 4, 2, 1,
    ["C04", "repeated"]
))

new_memories.append(M(
    "C04", "Astara storm", "meteorological_data", "wind speed records",
    "Caspian Meteorological Service recorded sustained winds of 58-65 knots and significant wave height of 4.2-4.8 meters at Astara from September 15-18, 2032. This is the primary source data underlying all 17 subsequent reports.",
    "fact", "ground_truth", "Caspian Met Service", 0.95,
    "met-data-2032-09", "official_record", 472, 0, 1, 1,
    ["C04", "primary_source"]
))

new_memories.append(M(
    "C04", "insurance industry", "claimed", "rising storm frequency",
    "An insurance industry white paper cited the Astara storm incident as evidence of 'increasing severe weather frequency in the Caspian,' listing '15 weather delay claims in a single quarter' without noting these all stemmed from one event.",
    "report", "inflated_claim", "insurance industry analyst", 0.40,
    "insurance-white-paper", "trade_publication", 472, 180, 20, 10,
    ["C04", "repeated"]
))

# --- C05 additional memories ---
new_memories.append(M(
    "C05", "forklift incident", "investigation_report", "root cause analysis",
    "Port of Baku's internal root cause analysis for the March 15 forklift fender-bender determined the cause was a blind corner in Warehouse 7. Corrective action: installation of convex mirrors at 12 intersections. Total repair cost: $800.",
    "report", "ground_truth", "safety investigation team", 0.95,
    "rca-forklift-2033", "official_record", 560, 5, 3, 1,
    ["C05", "primary_source"]
))

new_memories.append(M(
    "C05", "chemical spill", "investigation_report", "root cause analysis",
    "The July 22 chemical spill root cause was a cracked hydraulic line on a container crane. 15 liters of hydraulic fluid were released and contained within 20 minutes using pre-positioned absorbent materials. No environmental impact.",
    "report", "ground_truth", "safety investigation team", 0.95,
    "rca-spill-2033", "official_record", 600, 5, 3, 1,
    ["C05", "primary_source"]
))

new_memories.append(M(
    "C05", "Port of Baku", "safety_comparison", "regional peers",
    "When compared to regional peers, Port of Baku's 2 OSHA-recordable incidents in 2033 places it at the median — the Caspian port average is 2.3 incidents per year for ports of similar size. The 'below average' rating was based on document count, not incident count.",
    "fact", "ground_truth", "Fatima Guliyeva", 0.90,
    "regional-safety-comparison", "institutional", 600, 150, 10, 5,
    ["C05", "primary_source"]
))

# --- C06 additional memories ---
new_memories.append(M(
    "C06", "sanctions screening", "how_it_works", "name matching algorithm",
    "Sanctions screening databases use automated name-matching algorithms that flag partial matches. 'MV Caspian Dawn' triggered a match with 'Caspian Dawn Holdings LLC' despite being unrelated — the vessel is a 2015-built Russian-flagged cargo ship, while the sanctioned entity is an Iranian shell company.",
    "fact", "ground_truth", "Reza Ahmadi", 0.95,
    "sanctions-screening-explainer", "institutional", 0, 0, 1, 1,
    ["C06", "primary_source"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn", "operational_impact", "cargo booking delays",
    "Leyla Hasanova reported that MV Caspian Dawn lost 3 cargo bookings in Q2 2033 because shippers' compliance departments flagged the vessel based on unresolved sanctions entries in GTCS and Bank of Baku records.",
    "report", "ground_truth", "Leyla Hasanova", 0.85,
    "booking-loss-report", "commercial", 680, 90, 5, 2,
    ["C06"]
))

new_memories.append(M(
    "C06", "false positive rate", "sanctions_screening", "12% industry average",
    "Industry data shows that maritime sanctions screening produces approximately 12% false positives, primarily from name-matching algorithms. Most false positives are resolved within 48 hours, but database update propagation can take weeks to months.",
    "fact", "ground_truth", "compliance industry report", 0.90,
    "sanctions-false-positive-study", "trade_publication", 0, 0, 1, 1,
    ["C06", "background"]
))

# --- C07 additional memories ---
new_memories.append(M(
    "C07", "Caspian Shipping Weekly", "issued_correction", "for $2.1M typo",
    "Caspian Shipping Weekly issue #851 published a correction notice: 'In issue #847, MV Atropatene grounding damage was incorrectly reported as $2.1 million. The correct figure is approximately $210,000 based on surveyor assessments.' However, 7 publications had already republished the erroneous figure.",
    "report", "corrected", "Caspian Shipping Weekly editor", 0.90,
    "csw-correction-851", "trade_publication", 730, 30, 2, 1,
    ["C07", "correction"],
    supersedes=[]
))

new_memories.append(M(
    "C07", "trade publications", "did_not_correct", "$2.1M figure",
    "Of the 7 publications that reprinted the $2.1M error, none published a correction after Caspian Shipping Weekly's retraction in issue #851. The incorrect figure remains in their archives and continues to appear in search results.",
    "fact", "ground_truth", "Aynur Karimova", 0.85,
    "correction-tracking-2034", "internal_memo", 730, 60, 10, 3,
    ["C07"]
))

new_memories.append(M(
    "C07", "Viktor Kovalenko", "estimated_salvage", "not needed for Atropatene",
    "Salvage & Emergency Response Chief Viktor Kovalenko confirmed that MV Atropatene's grounding was minor enough that no salvage operation was required — the vessel refloated on the next high tide with tug assistance. Total tug cost: $12,000.",
    "fact", "ground_truth", "Viktor Kovalenko", 0.95,
    "salvage-assessment", "official_record", 730, 2, 1, 1,
    ["C07", "primary_source"]
))

# --- Cross-case analysis memories ---
new_memories.append(M(
    "background", "Timur Nazarov", "monitors", "vessel traffic patterns",
    "VTS Controller Timur Nazarov manages real-time vessel traffic in the Baku approach channel, coordinating with port authority and coast guard. His traffic logs are primary-source data for vessel movements.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Dmitri Volkov", "handles", "insurance claims for CME vessels",
    "Insurance Underwriter Dmitri Volkov serves as the Lloyd's of London liaison for Caspian maritime insurance. He processes claims from all Caspian-flagged vessels and has noted that repeated reports frequently inflate claim severity assessments.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Fatima Guliyeva", "ensures", "regulatory compliance",
    "Regulatory Compliance Manager Fatima Guliyeva oversees CME's compliance with IMO regulations, OSHA standards, environmental requirements, and sanctions screening. She interfaces with 4 national maritime administrations.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Leyla Hasanova", "coordinates", "cargo logistics",
    "Cargo Logistics Director Leyla Hasanova manages cargo booking, container tracking, and multimodal transport coordination for CME. She works directly with shippers, consignees, and freight forwarders across 5 Caspian states.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "C01", "MV Atropatene", "charterer_concern", "elevated rates",
    "A potential charterer for MV Atropatene requested an additional pre-charter survey 'due to widely reported hull concerns.' The pre-charter survey found the vessel in good condition, further confirming that the original paint degradation finding had been exaggerated through repetition.",
    "report", "ground_truth", "Nargiz Mammadova", 0.90,
    "pre-charter-survey-2034", "commercial", 120, 200, 5, 2,
    ["C01", "primary_source"]
))

new_memories.append(M(
    "C02", "MV Turkmenbashi", "cargo_dispute", "resolved by arbitration",
    "The 3% cargo weight discrepancy on MV Turkmenbashi was eventually resolved through standard commercial arbitration. The arbitrator noted that 'the number of documents recording this discrepancy should not be confused with the severity of the discrepancy itself.'",
    "report", "ground_truth", "arbitration panel", 0.95,
    "arbitration-ruling-2033", "official_record", 200, 30, 15, 5,
    ["C02", "primary_source"]
))

new_memories.append(M(
    "C03", "Kuryk Terminal", "fuel_quality_program", "enhanced testing",
    "Following the MV Khazar Star incident, Kuryk Terminal implemented enhanced fuel quality testing with duplicate samples tested at two independent laboratories simultaneously, reducing the risk of single-test errors.",
    "report", "ground_truth", "Kuryk Terminal management", 0.90,
    "kuryk-quality-improvement", "institutional", 365, 90, 10, 5,
    ["C03"]
))

new_memories.append(M(
    "C05", "Port of Baku", "PR_release_1", "safety culture initiative",
    "Port of Baku PR Release #1 (May 2033) announced a 'comprehensive safety culture initiative,' stating that 'following recent events, the port is investing in employee safety training.' The 'recent events' refers to the single forklift fender-bender from March.",
    "report", "repeated_claim", "Port of Baku PR", 0.60,
    "baku-pr-release-1", "press_release", 560, 30, 2, 1,
    ["C05", "repeated"]
))

new_memories.append(M(
    "C05", "Port of Baku", "PR_release_2", "equipment upgrade announcement",
    "Port of Baku PR Release #2 (September 2033) announced a $500,000 equipment safety upgrade, referencing 'the safety incidents earlier this year' — the same 2 incidents now being used as motivation for a third time.",
    "report", "repeated_claim", "Port of Baku PR", 0.60,
    "baku-pr-release-2", "press_release", 600, 30, 2, 1,
    ["C05", "repeated"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn", "owned_by", "Volga Maritime LLC",
    "MV Caspian Dawn is owned and operated by Volga Maritime LLC, a legitimate Russian shipping company established in 2008 with no sanctions history. The company's name has no connection to 'Caspian Dawn Holdings LLC,' the sanctioned Iranian entity.",
    "fact", "ground_truth", "vessel registry", 0.95,
    "vessel-registry-caspian-dawn", "official_record", 0, 0, 1, 1,
    ["C06", "primary_source"]
))

new_memories.append(M(
    "C07", "surveyor reports", "methodology", "three independent assessments",
    "The three surveyor assessments of MV Atropatene's grounding damage were conducted independently: Surveyor A (marine engineering firm from Baku), Surveyor B (classification society surveyor), Surveyor C (insurer-appointed surveyor from Istanbul). Their convergent $180K-$210K range reflects genuine independent agreement.",
    "fact", "ground_truth", "Dmitri Volkov", 0.95,
    "surveyor-methodology-note", "official_record", 730, 10, 2, 1,
    ["C07", "primary_source"]
))

# --- Additional queries ---
qid = len(queries) + 1

def Q(query, cat, expected, acceptable, forbidden, rel_ids, dist_ids,
      diff, uncertainty=False, conflict=False, disambig=False,
      scope=False, abstain=False, notes=""):
    global qid
    q = {
        "query_id": f"Q19-{qid:02d}",
        "query": query,
        "category": cat,
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": rel_ids,
        "distractor_memory_ids": dist_ids,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambig,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "difficulty": diff,
        "notes": notes
    }
    qid += 1
    return q

new_queries.append(Q(
    "What was the real-world financial impact of the inflated hull reports on MV Atropatene?",
    "confidence_calibration",
    ["A 15% insurance premium increase and a charterer demanding an additional pre-charter survey, both driven by derivative reports rather than actual hull condition"],
    ["Insurance rate increase and extra survey requirement caused by inflated repetition of a minor finding"],
    ["No financial impact from the reports", "The premium increase was justified by actual hull problems"],
    [], [],
    "hard",
    notes="C01: Concrete financial consequences of confidence inflation"
))

new_queries.append(Q(
    "How was the MV Turkmenbashi cargo discrepancy ultimately resolved?",
    "factual_recall",
    ["Through standard commercial arbitration, with the arbitrator noting that document count should not be confused with discrepancy severity"],
    ["Arbitration resolved it; the 3% variance was within normal tolerance"],
    ["It remains unresolved due to 8 conflicting records", "The discrepancy required criminal investigation"],
    [], [],
    "medium",
    notes="C02: Resolution through proper process, not document counting"
))

new_queries.append(Q(
    "What operational improvements resulted from the MV Khazar Star fuel testing incident?",
    "factual_recall",
    ["Kuryk Terminal implemented enhanced fuel testing with duplicate samples at two independent laboratories"],
    ["Dual-laboratory testing protocol was implemented to prevent single-test errors"],
    ["No changes were made", "MV Khazar Star was banned from Kuryk Terminal"],
    [], [],
    "easy",
    notes="C03: Positive outcome from the incident"
))

new_queries.append(Q(
    "Did Caspian Shipping Weekly publish a correction for the $2.1M figure?",
    "correction_handling",
    ["Yes, in issue #851 they corrected the $210,000 → $2.1M typo, but none of the 7 publications that republished the error issued corrections"],
    ["The original source corrected it, but derivative sources did not"],
    ["No correction was ever published", "All publications corrected the error"],
    [], [],
    "medium",
    notes="C07: Correction exists but didn't propagate"
))

new_queries.append(Q(
    "Was salvage required for MV Atropatene's grounding?",
    "factual_recall",
    ["No; the vessel refloated on the next high tide with tug assistance costing $12,000"],
    ["No salvage needed; minor grounding resolved with tug assistance"],
    ["Yes, a $2.1M salvage operation was conducted", "Major salvage was required"],
    [], [],
    "easy",
    notes="C07: Primary source (salvage chief) confirms minor incident"
))

new_queries.append(Q(
    "How many cargo bookings did MV Caspian Dawn lose due to the unresolved sanctions flags?",
    "status_tracking",
    ["3 cargo bookings in Q2 2033, because shippers' compliance departments flagged the vessel based on outdated sanctions entries"],
    ["Lost bookings due to GTCS and Bank of Baku still showing sanctions flags"],
    ["No bookings were lost", "The vessel was banned from all ports"],
    [], [],
    "medium",
    notes="C06: Quantifiable business impact of false positive persistence"
))

new_queries.append(Q(
    "What is the industry false-positive rate for maritime sanctions screening?",
    "factual_recall",
    ["Approximately 12%, primarily from name-matching algorithms"],
    ["About 12% false positive rate; most resolved within 48 hours but database updates can take weeks"],
    ["Maritime sanctions screening has near-zero false positives", "False positives are extremely rare"],
    [], [],
    "easy",
    notes="C06: Background context for the false-positive case"
))

new_queries.append(Q(
    "Were the three surveyor assessments of MV Atropatene truly independent of each other?",
    "source_quality",
    ["Yes; three different parties (Baku marine engineering firm, classification society surveyor, Istanbul insurer-appointed surveyor) conducted independent assessments"],
    ["Three independent surveyors from different organizations each assessed the damage separately"],
    ["The surveyors coordinated their estimates", "They all copied from the same source"],
    [], [],
    "medium",
    notes="C07: Unlike the derivative publications, the three surveyors ARE independent sources"
))

new_queries.append(Q(
    "What does the MV Atropatene pre-charter survey tell us about the hull condition?",
    "source_quality",
    ["The pre-charter survey found the vessel in good condition, providing additional independent confirmation that the 'structural concerns' narrative was unfounded"],
    ["Another independent inspection confirmed good hull condition"],
    ["The pre-charter survey confirmed structural concerns", "The survey found hull problems consistent with trade reports"],
    [], [],
    "medium",
    notes="C01: Independent verification contradicts the inflated narrative"
))

new_queries.append(Q(
    "How does Port of Baku's actual safety record compare to Caspian regional peers?",
    "confidence_calibration",
    ["Baku's 2 incidents is at the regional median (average 2.3 per year for similar-sized ports), contradicting the 'below average' rating based on document count"],
    ["Port of Baku's safety record is average for the region; the poor rating was inflated by counting duplicate records"],
    ["Baku has the worst safety record in the region", "11 documents prove systemic safety failures"],
    [], [],
    "hard",
    notes="C05: Document count vs. actual performance"
))

new_queries.append(Q(
    "Who is the owner of MV Caspian Dawn, and are they related to the sanctioned entity?",
    "factual_recall",
    ["Volga Maritime LLC, a Russian company established in 2008 with no sanctions history; they have no connection to Caspian Dawn Holdings LLC"],
    ["Owned by a legitimate Russian shipping company unrelated to the sanctioned Iranian entity"],
    ["Owned by a sanctions-listed entity", "The vessel and sanctioned company are related"],
    [], [],
    "easy",
    notes="C06: Basic factual recall to distinguish vessel from sanctioned entity"
))

new_queries.append(Q(
    "What does the Kuryk Terminal fuel supply certificate show about the fuel provided to MV Khazar Star?",
    "source_quality",
    ["The terminal's fuel supply certificate showed sulfur content at 0.48%, below the 0.50% limit, suggesting the initial 0.52% reading was a sampling or testing anomaly"],
    ["Terminal certificate shows compliant fuel; initial test was likely anomalous"],
    ["The certificate confirmed non-compliant fuel", "Terminal fuel was above the sulfur limit"],
    [], [],
    "medium",
    notes="C03: Terminal certificate as primary source supporting the retest"
))

new_queries.append(Q(
    "What impact did the insurance industry white paper have on the perception of Caspian weather risk?",
    "confidence_calibration",
    ["It inflated perception by characterizing one storm's 15 delay claims as '15 weather delay claims in a single quarter,' implying increasing severe weather frequency"],
    ["The white paper confused claim count with event count, overstating weather risk"],
    ["The white paper accurately reflected increasing storm frequency", "15 separate storms occurred that quarter"],
    [], [],
    "hard",
    notes="C04: Derivative source inflating perception of event frequency"
))

new_queries.append(Q(
    "What is the root cause of the forklift incident at Port of Baku?",
    "factual_recall",
    ["A blind corner in Warehouse 7; corrective action was installation of convex mirrors at 12 intersections; repair cost $800"],
    ["Blind corner caused the fender-bender; mirrors were installed as prevention"],
    ["Systemic safety failures", "Poor safety culture", "Multiple contributing factors across the port"],
    [], [],
    "easy",
    notes="C05: Primary source root cause analysis"
))

new_queries.append(Q(
    "In the MV Atropatene grounding case, how do the number of sources supporting each damage estimate compare to the quality of those sources?",
    "source_quality",
    ["7 sources cite $2.1M but all derive from one typo; 3 sources cite ~$195K and include independent surveyors, the actual repair cost confirms ~$187K-195K. Source quality decisively favors the lower figure despite being outnumbered."],
    ["Primary sources (surveyors, repair invoice) all show ~$195K; the $2.1M has more mentions but zero primary sources"],
    ["The 7-to-3 ratio favors $2.1M", "More sources means more reliable"],
    [], [],
    "hard",
    conflict=True,
    notes="C07: Definitive source quality vs source count test"
))

new_queries.append(Q(
    "How did the PR releases from Port of Baku contribute to the perception of its safety record?",
    "provenance_tracking",
    ["3 PR releases each referenced the same 2 incidents as motivation for improvements, creating the impression of ongoing/multiple safety events when only 2 minor incidents occurred"],
    ["PR repetition amplified 2 incidents into a pattern that was then picked up by trade press and benchmarking services"],
    ["PR releases accurately communicated numerous safety incidents", "The PR releases each described different incidents"],
    [], [],
    "hard",
    notes="C05: Provenance chain from 2 incidents → 8 records → 3 PR → trade press → benchmark"
))

# Write output
memories.extend(new_memories)
queries.extend(new_queries)

with open(os.path.join(d, "memories.jsonl"), "w") as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")
with open(os.path.join(d, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

# Update manifest
manifest_path = os.path.join(d, "manifest.json")
with open(manifest_path) as f:
    manifest = json.load(f)
for entry in manifest["files"]:
    fp = os.path.join(d, entry["path"])
    entry["sha256"] = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
    entry["bytes"] = os.path.getsize(fp)
manifest["total_memories"] = len(memories)
manifest["total_queries"] = len(queries)
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

print(f"Round 4: {len(memories)} memories, {len(queries)} queries")
