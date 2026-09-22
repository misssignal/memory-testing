#!/usr/bin/env python3
"""Exp19 Round 5 expansion: ~181 → ~210 memories, ~66 → ~78 queries."""

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

mid_counter = 800

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp19-r5-{mid_counter}".encode()).hexdigest()[:8]
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

# --- C01 final memories ---
new_memories.append(M(
    "C01", "MV Atropatene", "paint_type", "marine epoxy coating",
    "The MV Atropatene hull uses a marine epoxy anti-fouling coating system applied during the 2029 drydocking. The classification society inspector noted that the paint degradation observed was consistent with normal wear for a vessel of this age and service pattern.",
    "fact", "ground_truth", "ClassNK surveyor", 0.95,
    "classnk-coating-note", "official_record", 120, 0, 1, 1,
    ["C01", "primary_source"]
))

new_memories.append(M(
    "C01", "hull rumor", "timeline", "6 weeks from inspection to broker advisory",
    "The MV Atropatene hull narrative evolved over 6 weeks: Day 0 — inspection finds paint degradation; Day 7 — port inspector notes 'observations'; Day 14 — insurance surveyor logs 'minor concern'; Day 21 — broker newsletter uses 'structural observations'; Day 35 — trade magazine says 'structural concerns'; Day 42 — broker advisory warns of 'hull integrity issues.'",
    "fact", "ground_truth", "Aynur Karimova", 0.90,
    "narrative-timeline-analysis", "internal_memo", 120, 60, 5, 2,
    ["C01", "primary_source"]
))

# --- C02 final memories ---
new_memories.append(M(
    "C02", "draft survey methodology", "explained", "physical measurement",
    "A draft survey measures cargo weight by calculating the displacement of the vessel before and after loading, using calibrated draft marks and hydrostatic tables. It is a physical measurement, inherently more accurate than shipper-declared weights on bills of lading.",
    "fact", "ground_truth", "Captain Yusif Aliyev", 0.95,
    "draft-survey-methodology", "institutional", 0, 0, 1, 1,
    ["C02", "primary_source"]
))

new_memories.append(M(
    "C02", "MV Turkmenbashi", "cargo_weight_in", "insurance certificate",
    "The insurance certificate for MV Turkmenbashi's cargo lists the insured weight as 4,850 tonnes, matching the B/L. This is the 10th document containing the same cargo weight data from the same 2 original measurements.",
    "report", "repeated_claim", "insurer", 0.70,
    "insurance-cert-TKM0447", "commercial", 200, 3, 2, 1,
    ["C02", "repeated"]
))

# --- C03 final memories ---
new_memories.append(M(
    "C03", "fuel sulfur testing", "measurement_uncertainty", "±0.02%",
    "Standard fuel sulfur content testing by X-ray fluorescence has a measurement uncertainty of ±0.02%. This means a reading of 0.52% could represent true values anywhere from 0.50% to 0.54%, and the retest reading of 0.49% (true range 0.47%-0.51%) overlaps with the limit.",
    "fact", "ground_truth", "certified laboratory", 0.95,
    "test-methodology-note", "institutional", 0, 0, 1, 1,
    ["C03", "primary_source"]
))

new_memories.append(M(
    "C03", "MV Khazar Star", "chief_engineer_confirmed", "retest within spec",
    "MV Khazar Star's Chief Engineer confirmed receipt of the retest results showing 0.49% sulfur and updated the vessel's bunker quality log. He did not forward the results to regulatory authorities, considering it the owner's responsibility.",
    "report", "ground_truth", "MV Khazar Star chief engineer", 0.90,
    "chief-engineer-log", "vessel_record", 365, 6, 1, 1,
    ["C03", "primary_source"]
))

# --- C04 final memories ---
new_memories.append(M(
    "C04", "Coast Guard", "issued", "storm navigation warning",
    "Azerbaijan Coast Guard issued Navigation Warning NW-2032-047 for Storm SA-2032-019, advising all vessels to seek shelter and prohibiting departure from Astara Anchorage until winds subsided below 30 knots.",
    "report", "ground_truth", "Sergei Petrov", 0.95,
    "coast-guard-nw-2032-047", "official_record", 472, 0, 1, 1,
    ["C04", "primary_source"]
))

new_memories.append(M(
    "C04", "VTS Baku", "logged", "4 vessels sheltering at Astara",
    "Vessel Traffic Service logged 4 vessels sheltering at Astara Anchorage during Storm SA-2032-019: MV Atropatene, MV Khazar Star, MV Turkmenbashi, and MV Caspian Dawn. All were routine transits diverted by the weather advisory.",
    "report", "ground_truth", "Timur Nazarov", 0.95,
    "vts-log-2032-09-15", "official_record", 472, 0, 1, 1,
    ["C04", "primary_source"]
))

# --- C05 final memories ---
new_memories.append(M(
    "C05", "OSHA report", "forklift_incident", "Form 301",
    "OSHA Form 301 for the March 15 forklift incident at Port of Baku records: no injury, $800 property damage, corrective action taken. This is one of the 2 OSHA-recordable events that generated 11 total documents.",
    "report", "ground_truth", "Fatima Guliyeva", 0.95,
    "osha-form-301-forklift", "regulatory", 560, 3, 2, 1,
    ["C05", "primary_source"]
))

new_memories.append(M(
    "C05", "OSHA report", "chemical_spill", "Form 301",
    "OSHA Form 301 for the July 22 chemical spill at Port of Baku records: no injury, 15 liters hydraulic fluid, contained in 20 minutes, $400 cleanup cost. This is the second of the 2 OSHA-recordable events.",
    "report", "ground_truth", "Fatima Guliyeva", 0.95,
    "osha-form-301-spill", "regulatory", 600, 3, 2, 1,
    ["C05", "primary_source"]
))

new_memories.append(M(
    "C05", "Port of Baku safety", "total_document_count", "13 documents for 2 incidents",
    "Aynur Karimova's audit identified 13 documents related to Port of Baku's 2033 safety record: 2 incident logs, 2 OSHA forms, 2 insurance notifications, 1 environmental report, 1 annual safety review, 3 PR releases, 1 trade press article, and 1 benchmarking report. All trace to 2 original incidents.",
    "fact", "ground_truth", "Aynur Karimova", 0.90,
    "safety-document-audit", "internal_memo", 600, 180, 10, 5,
    ["C05", "primary_source"]
))

# --- C06 final memories ---
new_memories.append(M(
    "C06", "MV Caspian Dawn", "flag_state", "Russian Federation",
    "MV Caspian Dawn is registered under the Russian flag (port of registry: Astrakhan). The Russian Maritime Register of Shipping confirmed the vessel has no sanctions history and is in good standing.",
    "fact", "ground_truth", "Russian Maritime Register", 0.95,
    "russian-registry-caspian-dawn", "official_record", 0, 0, 1, 1,
    ["C06", "primary_source"]
))

new_memories.append(M(
    "C06", "Reza Ahmadi", "recommended", "bilateral clearance protocol",
    "Iranian Trade Representative Reza Ahmadi proposed a bilateral clearance protocol where sanctions false-positive resolutions would be automatically forwarded to all screening databases, preventing the asymmetric update problem seen with MV Caspian Dawn.",
    "report", "ground_truth", "Reza Ahmadi", 0.85,
    "ahmadi-proposal-2033", "internal_memo", 680, 120, 10, 5,
    ["C06"]
))

# --- C07 final memories ---
new_memories.append(M(
    "C07", "MV Atropatene grounding", "location", "Sangachal approach",
    "MV Atropatene's grounding occurred in the Sangachal approach channel at position 40°11'N 049°28'E, in soft mud at 4.2 meters depth. The vessel was inbound with ballast (no cargo) when it deviated from the channel due to a radar malfunction.",
    "fact", "ground_truth", "Captain Yusif Aliyev", 0.95,
    "grounding-incident-report", "official_record", 730, 0, 1, 1,
    ["C07", "primary_source"]
))

new_memories.append(M(
    "C07", "grounding investigation", "found", "radar malfunction",
    "The maritime investigation board determined MV Atropatene's grounding was caused by a temporary radar malfunction that misled the pilot. The grounding was in soft mud, resulting in minor bottom plate indentation with no breach of hull integrity.",
    "report", "ground_truth", "maritime investigation board", 0.95,
    "investigation-report-2034", "official_record", 730, 15, 10, 5,
    ["C07", "primary_source"]
))

# --- Cross-case connections ---
new_memories.append(M(
    "background", "CME board", "approved", "data quality improvement project",
    "The CME board approved a $1.2 million data quality improvement project in 2034, following Karimova and Mammadova's presentations showing how repeated reports were inflating risk assessments, increasing insurance premiums, and causing unnecessary operational delays across the Caspian fleet.",
    "report", "ground_truth", "Nargiz Mammadova", 0.90,
    "board-approval-2034", "institutional", 900, 0, 5, 2,
    ["background"]
))

new_memories.append(M(
    "background", "repeated exposure effect", "observed_in", "CME operations",
    "Aynur Karimova's analysis of 7 cases in 2031-2034 showed a consistent pattern: when the same information appeared in 5+ sources, CME's risk assessment scores increased by an average of 340%, even when all sources traced to a single origin. She termed this 'the echo chamber effect.'",
    "fact", "ground_truth", "Aynur Karimova", 0.90,
    "echo-chamber-analysis", "internal_memo", 900, 5, 10, 3,
    ["background", "primary_source"]
))

new_memories.append(M(
    "C01", "MV Atropatene", "current_status", "fully operational",
    "As of Q1 2035, MV Atropatene remains fully operational with all classification society certifications current. The vessel has completed 14 voyages since the hull inspection without any hull-related issues.",
    "fact", "ground_truth", "Captain Yusif Aliyev", 0.95,
    "atropatene-status-2035", "vessel_record", 120, 600, 5, 2,
    ["C01", "primary_source"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn sanctions", "fully_resolved", "all databases updated",
    "By January 2034, all 7 sanctions screening databases had been updated to clear MV Caspian Dawn, following CME's implementation of Ahmadi's bilateral clearance protocol as a pilot program.",
    "report", "corrected", "Reza Ahmadi", 0.90,
    "sanctions-resolution-2034", "institutional", 680, 270, 5, 2,
    ["C06", "correction"]
))

new_memories.append(M(
    "C03", "MV Khazar Star fuel", "all_databases_updated", "by 2032",
    "Following a CME-initiated data reconciliation effort in early 2032, all regulatory databases were updated with MV Khazar Star's retest results, clearing the vessel's fuel compliance record.",
    "report", "corrected", "Fatima Guliyeva", 0.90,
    "fuel-reconciliation-2032", "regulatory", 365, 180, 10, 5,
    ["C03", "correction"]
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
    "What caused MV Atropatene's grounding?",
    "factual_recall",
    ["A temporary radar malfunction that misled the pilot, causing the vessel to deviate from the Sangachal approach channel into soft mud"],
    ["Radar malfunction led to channel deviation; grounding in soft mud with minor bottom plate indentation"],
    ["Structural hull failure caused the grounding", "The grounding was caused by hull integrity issues"],
    [], [],
    "easy",
    notes="C07: Primary source grounding cause"
))

new_queries.append(Q(
    "How long did it take for the MV Atropatene hull narrative to evolve from 'paint degradation' to 'hull integrity issues'?",
    "temporal_reasoning",
    ["6 weeks: from Day 0 (paint degradation) through progressive embellishment to Day 42 (hull integrity issues)"],
    ["About 6 weeks of progressive exaggeration through derivative reporting"],
    ["The change happened instantly", "Multiple independent inspections found escalating problems over 6 weeks"],
    [], [],
    "medium",
    notes="C01: Timeline of narrative inflation"
))

new_queries.append(Q(
    "What is the measurement uncertainty of standard fuel sulfur testing?",
    "factual_recall",
    ["±0.02% by X-ray fluorescence, meaning a reading of 0.52% could represent true values from 0.50% to 0.54%"],
    ["About ±0.02%, which means the initial and retest readings overlap within measurement error"],
    ["Fuel testing is exact with no uncertainty", "±10% measurement uncertainty"],
    [], [],
    "easy",
    notes="C03: Context that explains why initial and retest can differ"
))

new_queries.append(Q(
    "How many total documents did Karimova identify related to Port of Baku's 2033 safety record?",
    "deduplication",
    ["13 documents, all tracing to 2 original incidents"],
    ["13 documents from 2 incidents: incident logs, OSHA forms, insurance, environmental, annual review, PR, trade press, benchmarking"],
    ["13 separate safety incidents", "13 documents prove widespread safety failures"],
    [], [],
    "hard",
    notes="C05: Complete document audit"
))

new_queries.append(Q(
    "What was the outcome of Karimova's analysis of the 'echo chamber effect' across CME operations?",
    "factual_recall",
    ["When information appeared in 5+ sources, risk assessments inflated by 340% on average, even when all sources traced to a single origin. This led to board approval of a $1.2M data quality project."],
    ["340% inflation in risk scores from repeated reports; board approved improvement project"],
    ["No echo chamber effect was found", "Repeated reports improved accuracy"],
    [], [],
    "medium",
    notes="Background: Quantified impact of repeated exposure on CME operations"
))

new_queries.append(Q(
    "Is MV Atropatene still operational as of 2035?",
    "status_tracking",
    ["Yes; fully operational with all certifications current, having completed 14 voyages since the hull inspection without hull-related issues"],
    ["Fully operational; the hull concerns were entirely unfounded"],
    ["No, the vessel was decommissioned due to hull problems", "The vessel is under repair for structural issues"],
    [], [],
    "easy",
    notes="C01: Final status contradicts the inflated narrative"
))

new_queries.append(Q(
    "Were all sanctions screening databases eventually updated for MV Caspian Dawn?",
    "correction_handling",
    ["Yes; by January 2034, all 7 databases were updated following CME's implementation of Ahmadi's bilateral clearance protocol"],
    ["All databases eventually cleared; Ahmadi's protocol was implemented as a pilot"],
    ["Some databases still show the flag", "The sanctions concern was never fully resolved"],
    [], [],
    "medium",
    notes="C06: Full resolution after systemic fix"
))

new_queries.append(Q(
    "Why is a draft survey generally more accurate than a bill of lading weight?",
    "source_quality",
    ["A draft survey is a physical measurement using vessel displacement and hydrostatic tables, while B/L weights are shipper-declared estimates"],
    ["Draft survey measures actual displacement; B/L weight is declared by the shipper"],
    ["B/L weights are more accurate than draft surveys", "Both are equally reliable"],
    [], [],
    "easy",
    notes="C02: Understanding source quality for cargo weight"
))

new_queries.append(Q(
    "What systemic solution did Reza Ahmadi propose for the sanctions false-positive problem?",
    "factual_recall",
    ["A bilateral clearance protocol where sanctions false-positive resolutions would be automatically forwarded to all screening databases"],
    ["Automatic propagation of clearances to all databases that received the initial flag"],
    ["Ahmadi proposed no solution", "Ahmadi recommended stopping all sanctions screening"],
    [], [],
    "easy",
    notes="C06: Systemic fix for asymmetric clearance distribution"
))

new_queries.append(Q(
    "Were all regulatory databases eventually updated with MV Khazar Star's fuel retest results?",
    "correction_handling",
    ["Yes; a CME-initiated data reconciliation effort in early 2032 updated all regulatory databases with the retest results"],
    ["All databases were updated following a reconciliation effort; the vessel's fuel record was cleared"],
    ["Some databases still show non-compliance", "The fuel issue was never resolved"],
    [], [],
    "medium",
    notes="C03: Full resolution after data reconciliation"
))

new_queries.append(Q(
    "How should a memory system handle the MV Atropatene hull case — should it weight source count or source quality?",
    "confidence_calibration",
    ["Source quality over source count: the classification society and captain (primary sources) say paint degradation only; derivative sources progressively inflated to 'structural concerns' through repetition, not through independent verification"],
    ["Weight primary sources (original inspectors) over derivative sources regardless of count"],
    ["Weight source count — more sources saying structural concerns means it's more likely true"],
    [], [],
    "hard",
    conflict=True,
    notes="C01: Meta-question about the experiment's core thesis"
))

new_queries.append(Q(
    "Across the 7 cases documented at CME, what is the common pattern of confidence inflation?",
    "provenance_tracking",
    ["A single finding or event is reported by multiple parties, each adding slight embellishment. Derivative sources are treated as independent evidence, inflating confidence scores. Corrections and retests propagate to fewer parties than the original finding."],
    ["Repeated reports from a single origin are mistaken for independent corroboration; corrections don't propagate as widely as initial reports"],
    ["Each case represents genuinely independent corroboration", "More sources always means more reliable information"],
    [], [],
    "hard",
    notes="Cross-case: The overarching pattern across all 7 cases"
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

print(f"Round 5: {len(memories)} memories, {len(queries)} queries")
