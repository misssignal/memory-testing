#!/usr/bin/env python3
"""Exp19 Round 2 expansion: ~92 → ~145 memories, ~22 → ~42 queries."""

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

mid_counter = 200

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp19-r2-{mid_counter}".encode()).hexdigest()[:8]
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

# --- More background memories ---
new_memories.append(M(
    "background", "CME", "operates_in", "Caspian Sea region",
    "The Caspian Maritime Exchange coordinates vessel traffic, cargo logistics, insurance, and regulatory compliance for maritime trade across the Caspian Sea, connecting Azerbaijan, Kazakhstan, Turkmenistan, Iran, and Russia.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-charter", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Captain Yusif Aliyev", "has_experience", "25 years",
    "Captain Yusif Aliyev has served as Senior Harbor Pilot at the Port of Baku for 25 years, making him the most experienced pilot in the Caspian region.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Aynur Karimova", "manages", "CME data systems",
    "Aynur Karimova manages CME's data analytics platform, which aggregates reports from port authorities, insurance, coast guard, and vessel traffic services into a unified maritime intelligence dashboard.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Port of Baku", "processes", "1,200 vessel calls per year",
    "The Port of Baku processed approximately 1,200 vessel calls in 2032, handling cargo volumes of 8.2 million tonnes across its 12 berths.",
    "fact", "ground_truth", "CME_system", 0.95,
    "port-stats-2032", "institutional", 365, 0, 5, 2,
    ["background"]
))

new_memories.append(M(
    "background", "Kuryk Terminal", "exports", "crude oil",
    "Kuryk Terminal is Kazakhstan's primary Caspian oil export facility, handling 40% of Kazakhstan's seaborne crude exports with dedicated tanker berths and pipeline connections to the Tengiz and Kashagan fields.",
    "fact", "ground_truth", "CME_system", 0.95,
    "kuryk-profile", "institutional", 0, 0, 1, 1,
    ["background"]
))

# --- C01 additional derivatives: hull rumor keeps spreading ---
new_memories.append(M(
    "C01", "MV Atropatene", "reported_by", "P&I Club newsletter",
    "The P&I Club's quarterly newsletter mentioned that MV Atropatene underwent hull inspection at Baku with 'noted structural observations requiring monitoring,' citing the insurance surveyor's report.",
    "report", "repeated_claim", "P&I Club editor", 0.65,
    "pni-newsletter-2033Q3", "trade_publication", 120, 30, 5, 3,
    ["C01", "repeated"],
    derived=["E19-" + hashlib.md5(b"exp19-r0-7").hexdigest()[:8]]
))

new_memories.append(M(
    "C01", "MV Atropatene", "described_as", "vessel with hull issues",
    "A cargo broker's market report listed MV Atropatene among 'vessels with known hull issues' in the Caspian fleet, noting it had been flagged by multiple parties including classification society and insurance.",
    "report", "inflated_claim", "cargo broker network", 0.55,
    "broker-market-report-2033", "trade_publication", 120, 45, 3, 2,
    ["C01", "repeated"],
    derived=["E19-" + hashlib.md5(b"exp19-r0-7").hexdigest()[:8]]
))

new_memories.append(M(
    "C01", "MV Atropatene hull", "clarified_by", "classification society follow-up",
    "The classification society issued a follow-up letter confirming MV Atropatene's hull rating remains 'satisfactory' and that the original inspection found only cosmetic paint degradation with no structural implications.",
    "report", "corrected", "ClassNK surveyor", 0.95,
    "classnk-followup-2033", "official_record", 120, 60, 2, 1,
    ["C01", "primary_source", "correction"],
    contradicts=["E19-" + hashlib.md5(b"exp19-r0-7").hexdigest()[:8]]
))

# --- C02 additional cargo weight documents ---
new_memories.append(M(
    "C02", "MV Turkmenbashi cargo", "recorded_in", "freight forwarder's log",
    "The freight forwarder's log for MV Turkmenbashi shipment TKM-2033-0447 records cargo weight as 4,850 tonnes per bill of lading, with a handwritten note: 'draft survey variance 145t - see customs declaration.'",
    "report", "repeated_claim", "freight forwarder", 0.70,
    "ff-log-TKM0447", "commercial", 200, 2, 1, 1,
    ["C02", "repeated"]
))

new_memories.append(M(
    "C02", "MV Turkmenbashi cargo", "flagged_by", "CME analytics",
    "CME's automated analytics system flagged MV Turkmenbashi for cargo weight discrepancy, counting 8 separate records that each mention the variance between 4,850 and 4,705 tonnes, and assigned it a 'high confidence anomaly' score of 0.89.",
    "report", "inflated_claim", "Aynur Karimova", 0.60,
    "cme-analytics-alert", "system_generated", 200, 5, 1, 1,
    ["C02", "repeated"],
    derived=[]
))

new_memories.append(M(
    "C02", "cargo weight discrepancy", "is_within", "normal commercial tolerance",
    "Industry standard allows up to 5% variance between bill of lading weight and draft survey for bulk cargo. The 3% discrepancy on MV Turkmenbashi (145 tonnes on 4,850) falls within accepted tolerances per IMO guidelines.",
    "fact", "ground_truth", "IMO guidelines", 0.95,
    "imo-cargo-guidelines", "regulatory", 0, 0, 1, 1,
    ["C02", "primary_source"]
))

# --- C03 fuel quality additional forwarding ---
new_memories.append(M(
    "C03", "MV Khazar Star fuel", "reported_to", "Kazakh Maritime Administration",
    "The Kazakh Maritime Administration received notification of MV Khazar Star's initial fuel test result showing sulfur content at 0.52%, above the 0.50% limit. The notification was forwarded by the flag state inspector.",
    "report", "repeated_claim", "Kazakh Maritime Admin", 0.70,
    "kma-notification-2031", "regulatory", 365, 3, 2, 1,
    ["C03", "repeated"]
))

new_memories.append(M(
    "C03", "MV Khazar Star fuel", "retest_not_received_by", "port state control",
    "Port state control records for MV Khazar Star still show the initial fuel test result of 0.52% sulfur. The retest result of 0.49% was communicated only to the chief engineer and vessel owner, and was never forwarded to port state authorities.",
    "fact", "ground_truth", "Fatima Guliyeva", 0.90,
    "psc-records-review", "regulatory", 365, 10, 3, 1,
    ["C03", "primary_source"]
))

new_memories.append(M(
    "C03", "MV Khazar Star", "listed_as", "sulfur non-compliant",
    "A regional environmental compliance database lists MV Khazar Star as having a sulfur non-compliance record from 2031, based on the initial test result. The retest clearing the vessel was never entered into the database.",
    "report", "repeated_claim", "environmental database", 0.65,
    "env-compliance-db", "system_generated", 365, 30, 1, 1,
    ["C03", "repeated"],
    derived=[]
))

# --- C04 weather delay more documents ---
new_memories.append(M(
    "C04", "Astara storm", "reported_by", "CME weather service",
    "CME's weather monitoring service issued Storm Advisory SA-2032-019, warning of severe weather conditions at Astara Anchorage with sustained winds of 65 knots and wave heights of 4.5 meters, effective for 72 hours beginning 2032-09-15.",
    "report", "ground_truth", "Timur Nazarov", 0.95,
    "cme-storm-advisory", "official_record", 472, 0, 1, 1,
    ["C04", "primary_source"]
))

new_memories.append(M(
    "C04", "MV Atropatene", "filed_claim", "weather delay insurance",
    "MV Atropatene's P&I insurer received a weather delay claim for the 72-hour detention at Astara Anchorage due to Storm SA-2032-019. The claim references the same storm event documented in 14 other filings.",
    "report", "repeated_claim", "Dmitri Volkov", 0.70,
    "insurance-claim-atropatene", "commercial", 472, 5, 3, 2,
    ["C04", "repeated"]
))

new_memories.append(M(
    "C04", "Astara storm", "caused", "anchorage congestion for 5 days",
    "Although the storm itself lasted 72 hours, the resulting backlog at Astara Anchorage took an additional 48 hours to clear, causing total delays of up to 5 days for vessels arriving during the storm period.",
    "fact", "ground_truth", "Sergei Petrov", 0.90,
    "coast-guard-report-2032", "official_record", 472, 6, 2, 1,
    ["C04", "primary_source"]
))

new_memories.append(M(
    "C04", "weather delays 2032", "aggregated_by", "insurance industry report",
    "An insurance industry report counted 15 separate delay claims from the September 2032 Astara storm, characterizing it as '15 weather delay incidents' rather than recognizing them as a single weather event affecting multiple vessels.",
    "report", "inflated_claim", "insurance industry", 0.50,
    "insurance-annual-2032", "trade_publication", 472, 90, 10, 5,
    ["C04", "repeated"]
))

# --- C05 safety record additional documents ---
new_memories.append(M(
    "C05", "Port of Baku", "incident_recorded_in", "annual safety review",
    "The Port of Baku Annual Safety Review for 2033 documented 2 OSHA-recordable incidents: a forklift fender-bender on March 15 and a chemical spill on July 22. The review noted both were promptly addressed with no injuries.",
    "report", "ground_truth", "Fatima Guliyeva", 0.95,
    "baku-safety-review-2033", "official_record", 600, 30, 10, 5,
    ["C05", "primary_source"]
))

new_memories.append(M(
    "C05", "Port of Baku", "safety_mentioned_in", "trade press article",
    "Caspian Trade Weekly ran an article titled 'Baku Port Invests in Safety Overhaul After Multiple Incidents,' citing the port's PR releases about safety improvements and referencing 'a series of safety incidents in 2033.'",
    "report", "inflated_claim", "trade press", 0.50,
    "caspian-trade-weekly", "trade_publication", 600, 60, 5, 3,
    ["C05", "repeated"],
    derived=[]
))

new_memories.append(M(
    "C05", "Port of Baku", "PR_release_3", "safety certification achievement",
    "Port of Baku PR Release #3 announced the port achieved ISO 45001 safety certification, noting that 'following recent safety events, the port has invested $2.3 million in safety infrastructure.' This is the same 2 incidents being used as justification.",
    "report", "repeated_claim", "Port of Baku PR", 0.60,
    "baku-pr-release-3", "press_release", 600, 50, 2, 1,
    ["C05", "repeated"]
))

# --- C06 sanctions compliance additional records ---
new_memories.append(M(
    "C06", "MV Caspian Dawn", "flagged_in", "trade compliance service",
    "Global Trade Compliance Service (GTCS) flagged MV Caspian Dawn on 2033-04-10 due to a name match with sanctioned entity 'Caspian Dawn Holdings LLC.' The flag was generated automatically and has not been manually reviewed.",
    "report", "repeated_claim", "GTCS automated system", 0.60,
    "gtcs-flag-2033", "system_generated", 680, 1, 1, 1,
    ["C06", "repeated"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn", "cleared_by", "OFAC verification",
    "The US Treasury Department's OFAC office confirmed that MV Caspian Dawn (IMO 9876543) is not affiliated with Caspian Dawn Holdings LLC and is not subject to sanctions. Clearance issued 2033-04-11.",
    "report", "corrected", "OFAC", 0.95,
    "ofac-clearance-2033", "regulatory", 680, 2, 1, 1,
    ["C06", "primary_source", "correction"],
    supersedes=[]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn", "still_flagged_in", "Bank of Baku records",
    "Bank of Baku's compliance department still shows MV Caspian Dawn with an active sanctions concern flag as of 2033-06-01. The OFAC clearance was sent to CME and the vessel owner but was never forwarded to Bank of Baku.",
    "fact", "ground_truth", "bank compliance officer", 0.85,
    "bank-baku-records", "financial", 680, 55, 3, 1,
    ["C06", "repeated"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn", "still_flagged_in", "GTCS database",
    "Global Trade Compliance Service still lists MV Caspian Dawn with a sanctions concern as of 2033-07-01. The service was not among the 4 databases that received the clearance update.",
    "fact", "ground_truth", "Reza Ahmadi", 0.85,
    "gtcs-status-check", "system_generated", 680, 85, 1, 1,
    ["C06", "repeated"]
))

# --- C07 salvage value additional copies of the typo ---
new_memories.append(M(
    "C07", "MV Atropatene grounding", "reported_in", "maritime insurance digest",
    "The Maritime Insurance Digest reported that MV Atropatene's grounding damage was estimated at $2.1 million, citing 'industry sources.' This figure matches the broker newsletter's decimal-point error, not the actual surveyor estimates.",
    "report", "inflated_claim", "insurance digest editor", 0.55,
    "maritime-insurance-digest", "trade_publication", 730, 20, 5, 3,
    ["C07", "repeated"],
    derived=[]
))

new_memories.append(M(
    "C07", "MV Atropatene grounding", "estimated_at", "$195,000 average",
    "The three independent surveyors who inspected MV Atropatene's grounding damage submitted their reports directly to the vessel owner and insurer: Survey A: $180,000, Survey B: $195,000, Survey C: $210,000. Average estimate: $195,000.",
    "report", "ground_truth", "Dmitri Volkov", 0.95,
    "surveyor-summary-report", "official_record", 730, 5, 3, 1,
    ["C07", "primary_source"]
))

new_memories.append(M(
    "C07", "$2.1M figure", "originated_from", "broker newsletter typo",
    "Investigation revealed that the $2.1 million figure for MV Atropatene's grounding originated from Caspian Shipping Weekly newsletter issue #847, where editor Mehdi Rahimov mistyped '$210,000' as '$2,100,000' (decimal point shifted). All subsequent publications citing '$2.1M' trace back to this single error.",
    "fact", "ground_truth", "Aynur Karimova", 0.95,
    "provenance-investigation", "internal_memo", 730, 60, 5, 2,
    ["C07", "primary_source"]
))

new_memories.append(M(
    "C07", "MV Atropatene damage", "cited_in", "regulatory filing at $2.1M",
    "The Azerbaijan Maritime Safety Authority's quarterly incident summary listed MV Atropatene grounding damage at '$2.1 million,' sourced from media reports rather than the official surveyor assessments.",
    "report", "inflated_claim", "AMSA regulatory clerk", 0.50,
    "amsa-quarterly-2034", "regulatory", 730, 45, 10, 5,
    ["C07", "repeated"],
    derived=[]
))

# --- Cross-case: system-level observations ---
new_memories.append(M(
    "background", "Aynur Karimova", "identified", "provenance tracking gap",
    "Data Analytics Manager Aynur Karimova submitted an internal memo identifying that CME's data systems do not track the provenance chain of information, meaning derivative reports are weighted equally with primary source documents in confidence scoring.",
    "report", "ground_truth", "Aynur Karimova", 0.90,
    "karimova-memo-2033", "internal_memo", 500, 0, 2, 1,
    ["background"]
))

new_memories.append(M(
    "background", "CME data platform", "has_weakness", "no deduplication",
    "CME's maritime intelligence dashboard aggregates reports from all sources without deduplication. When the same event is reported by 5 different parties, it appears as 5 separate entries, potentially inflating the perceived significance of routine events.",
    "fact", "ground_truth", "CME_system", 0.90,
    "system-audit-2033", "internal_memo", 500, 5, 3, 1,
    ["background"]
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
    "How many independent safety incidents occurred at Port of Baku in 2033?",
    "deduplication",
    ["2 incidents: a forklift fender-bender and a chemical spill"],
    ["2 OSHA-recordable incidents in 2033"],
    ["8 incidents", "11 incidents", "multiple incidents suggesting systemic problems"],
    [], [],
    "hard",
    notes="C05: 2 incidents recorded in 8 separate systems + 3 PR mentions = 11 documents, but only 2 actual incidents"
))

new_queries.append(Q(
    "What is the current sanctions status of MV Caspian Dawn as of mid-2033?",
    "status_tracking",
    ["Cleared by OFAC; no longer subject to sanctions concern"],
    ["Initial flag was a false positive; cleared within 24 hours", "Cleared but some databases not yet updated"],
    ["Currently sanctioned", "Under active sanctions investigation", "Sanctions status uncertain due to conflicting reports"],
    [], [],
    "hard",
    uncertainty=True,
    notes="C06: 7 databases flagged, only 4 updated with clearance. System must recognize OFAC clearance supersedes the automated flags."
))

new_queries.append(Q(
    "Who originally authored the $2.1 million damage estimate for MV Atropatene, and how did it spread?",
    "provenance_tracking",
    ["The $2.1M figure was a typo in Caspian Shipping Weekly newsletter by editor Mehdi Rahimov, mistyping $210,000 as $2,100,000"],
    ["Originated from a broker newsletter decimal point error, then propagated to 7 publications"],
    ["Multiple independent surveyors estimated $2.1M", "The $2.1M estimate came from official surveyors"],
    [], [],
    "hard",
    notes="C07: Provenance chain from single typo to 7 derivative sources"
))

new_queries.append(Q(
    "Is the cargo weight discrepancy on MV Turkmenbashi cause for concern?",
    "confidence_calibration",
    ["No; the 3% variance (145 tonnes on 4,850) is within the industry-standard 5% tolerance for bulk cargo"],
    ["The discrepancy is within normal commercial tolerance per IMO guidelines"],
    ["Yes, 8 separate records confirm a significant discrepancy", "The number of records mentioning the discrepancy indicates a serious issue"],
    [], [],
    "hard",
    notes="C02: 8 documents all record the same 2 measurements; repetition should not inflate concern"
))

new_queries.append(Q(
    "How many separate weather delay incidents occurred at Astara Anchorage in September 2032?",
    "deduplication",
    ["1 storm event (SA-2032-019) affecting 4 vessels, producing 15+ reports"],
    ["One severe storm caused delays for multiple vessels"],
    ["15 separate weather incidents", "15 independent delay events"],
    [], [],
    "hard",
    notes="C04: 1 event reported 15+ times across vessels, authorities, and insurers"
))

new_queries.append(Q(
    "What did the classification society conclude about MV Atropatene's hull condition?",
    "source_quality",
    ["Classification society rated hull as 'satisfactory with observations' for minor paint degradation; follow-up confirmed no structural implications"],
    ["Hull condition is satisfactory; only cosmetic paint degradation was found"],
    ["Structural concerns identified", "Multiple sources confirm hull issues", "Classification society found structural problems"],
    [], [],
    "medium",
    notes="C01: Primary source (classification society) says satisfactory; derivative sources inflated to 'structural concerns'"
))

new_queries.append(Q(
    "What is the correct sulfur content result for MV Khazar Star's fuel?",
    "correction_handling",
    ["Retest showed 0.49%, within the 0.50% limit; the initial 0.52% result was likely a testing error"],
    ["Final retest: 0.49% sulfur, within spec"],
    ["0.52% sulfur, non-compliant", "5 sources confirm non-compliance vs only 2 saying compliant"],
    [], [],
    "hard",
    conflict=True,
    notes="C03: 5 sources have the initial out-of-spec result, only 2 have the retest. System must weight retest over source count."
))

new_queries.append(Q(
    "Does CME's data platform distinguish between primary and derivative sources?",
    "factual_recall",
    ["No; CME's platform aggregates all sources equally without provenance tracking or deduplication"],
    ["CME's system treats all reports equally; Karimova identified this as a gap"],
    ["Yes, CME uses provenance tracking", "CME has sophisticated deduplication"],
    [], [],
    "medium",
    notes="Background: Karimova's memo and system audit both confirm this weakness"
))

new_queries.append(Q(
    "How many databases still show MV Caspian Dawn as sanctions-flagged despite the clearance?",
    "status_tracking",
    ["3 databases still show the flag: the 7 original minus 4 that updated"],
    ["At least 2 databases (Bank of Baku, GTCS) still show active sanctions concern"],
    ["All databases now show cleared", "0 databases still flagged"],
    [], [],
    "hard",
    uncertainty=True,
    notes="C06: 7 flagged, 4 cleared, 3 still showing false flag"
))

new_queries.append(Q(
    "What was the total duration of disruption at Astara Anchorage from the September 2032 storm?",
    "temporal_reasoning",
    ["Up to 5 days total: 72-hour storm plus 48-hour backlog clearance"],
    ["Storm lasted 72 hours but full clearance took about 5 days"],
    ["72 hours exactly", "15 separate delays of varying duration"],
    [], [],
    "medium",
    notes="C04: Storm was 72 hours, but anchorage congestion lasted additional 48 hours"
))

new_queries.append(Q(
    "Is the insurance industry report's characterization of '15 weather delay incidents' at Astara accurate?",
    "confidence_calibration",
    ["No; it was 1 weather event affecting multiple vessels, not 15 separate incidents"],
    ["The insurance report conflates 15 claims/reports with 15 distinct events; there was only one storm"],
    ["Yes, 15 separate weather incidents occurred", "The high number of reports confirms many incidents"],
    [], [],
    "hard",
    notes="C04: Insurance report counted 15 claims as 15 incidents"
))

new_queries.append(Q(
    "Which sources about MV Atropatene's hull should be considered authoritative?",
    "source_quality",
    ["The classification society's original inspection report and follow-up letter are the primary authoritative sources"],
    ["The original surveyor's report and classification society follow-up, not broker reports or trade publications"],
    ["All sources are equally reliable", "The broker report is authoritative because it aggregates multiple sources"],
    [], [],
    "medium",
    notes="C01: Classification society is the authoritative primary source; broker/trade publications are derivative"
))

new_queries.append(Q(
    "How did Port of Baku's PR strategy affect the perception of its safety record?",
    "confidence_calibration",
    ["3 PR releases about 'safety improvements' referencing the same 2 incidents created the impression of more safety events than actually occurred"],
    ["PR releases amplified the perception of safety issues by repeatedly referencing 2 incidents as motivation for improvements"],
    ["The PR releases accurately reflected numerous safety incidents", "11 documents about safety prove a poor safety record"],
    [], [],
    "hard",
    notes="C05: 2 real incidents + 8 records + 3 PR mentions = inflated perception"
))

new_queries.append(Q(
    "Should the fuel quality allegation against MV Khazar Star be considered resolved?",
    "correction_handling",
    ["Yes; the retest showed 0.49% sulfur (within the 0.50% limit), superseding the initial 0.52% result"],
    ["The retest cleared the vessel, but several databases have not been updated"],
    ["No, 5 sources still show non-compliance", "The matter is unresolved due to conflicting data"],
    [], [],
    "hard",
    uncertainty=True,
    notes="C03: 1 retest supersedes 1 initial test regardless of how many copies of each exist"
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
import hashlib as hl
manifest_path = os.path.join(d, "manifest.json")
with open(manifest_path) as f:
    manifest = json.load(f)
for entry in manifest["files"]:
    fp = os.path.join(d, entry["path"])
    entry["sha256"] = hl.sha256(open(fp, 'rb').read()).hexdigest()
    entry["bytes"] = os.path.getsize(fp)
manifest["total_memories"] = len(memories)
manifest["total_queries"] = len(queries)
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

print(f"Round 2: {len(memories)} memories, {len(queries)} queries")
