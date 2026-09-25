#!/usr/bin/env python3
"""Exp19 Round 3 expansion: ~123 → ~175 memories, ~36 → ~55 queries."""

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

mid_counter = 400

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp19-r3-{mid_counter}".encode()).hexdigest()[:8]
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

# --- More background ---
new_memories.append(M(
    "background", "Sergei Petrov", "oversees", "coast guard operations",
    "Coast Guard Liaison Officer Sergei Petrov coordinates between CME and the Azerbaijan Coast Guard, overseeing maritime safety inspections, search and rescue coordination, and incident reporting for the Baku sector.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Viktor Kovalenko", "leads", "salvage response team",
    "Viktor Kovalenko heads the Caspian Salvage & Emergency Response unit based at Port of Baku, with 3 tugs and specialized equipment for grounding, collision, and pollution response across the Caspian.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Reza Ahmadi", "facilitates", "Iran-Azerbaijan trade",
    "Iranian Trade Representative Reza Ahmadi manages the bilateral trade agreements between Iran and Azerbaijan for Caspian maritime commerce, including cargo routing, tariff negotiations, and sanctions compliance verification.",
    "fact", "ground_truth", "CME_system", 0.95,
    "CME-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_memories.append(M(
    "background", "Caspian Sea", "has_characteristic", "enclosed body of water",
    "The Caspian Sea is the world's largest enclosed inland body of water, bordered by five nations. Its legal status as neither sea nor lake affects maritime regulations, insurance underwriting, and vessel classification standards applied to shipping.",
    "fact", "ground_truth", "CME_system", 0.95,
    "caspian-regulatory-guide", "institutional", 0, 0, 1, 1,
    ["background"]
))

# --- C01 more repetition chain ---
new_memories.append(M(
    "C01", "MV Atropatene", "mentioned_in", "Baku port authority advisory",
    "Baku Port Authority issued a routine advisory listing MV Atropatene among vessels with 'open inspection observations,' a standard administrative notice. The advisory was distributed to all port users.",
    "report", "repeated_claim", "Baku Port Authority", 0.65,
    "bpa-advisory-2033-07", "official_record", 120, 15, 2, 1,
    ["C01", "repeated"]
))

new_memories.append(M(
    "C01", "MV Atropatene hull", "discussed_at", "CME operations meeting",
    "At the weekly CME operations meeting, Nargiz Mammadova raised MV Atropatene's hull status, noting that 'multiple sources have flagged structural concerns.' Captain Aliyev objected, saying only paint degradation was found.",
    "report", "contextual_true", "Nargiz Mammadova", 0.70,
    "cme-meeting-minutes-2033-08", "internal_memo", 120, 40, 1, 1,
    ["C01"],
    derived=[]
))

new_memories.append(M(
    "C01", "Captain Aliyev", "disputed", "structural concerns characterization",
    "Captain Yusif Aliyev formally objected to the characterization of MV Atropatene's hull condition as involving 'structural concerns,' stating in a written memo that the original inspection found only paint degradation and that the term 'structural' was introduced by secondary sources.",
    "report", "ground_truth", "Captain Yusif Aliyev", 0.90,
    "aliyev-memo-2033-08", "internal_memo", 120, 42, 1, 1,
    ["C01", "primary_source"]
))

# --- C02 more copies and analysis ---
new_memories.append(M(
    "C02", "MV Turkmenbashi cargo", "reported_in", "port authority database",
    "Baku Port Authority's vessel database records MV Turkmenbashi's cargo as '4,850 tonnes (B/L) / 4,705 tonnes (draft survey)' — the same two measurements appearing in yet another administrative system.",
    "report", "repeated_claim", "Baku Port Authority", 0.70,
    "bpa-vessel-db", "official_record", 200, 3, 1, 1,
    ["C02", "repeated"]
))

new_memories.append(M(
    "C02", "cargo weight discrepancy", "analyzed_by", "Karimova analytics team",
    "Aynur Karimova's analytics team investigated the MV Turkmenbashi cargo weight discrepancy and determined all 8 records trace to the same 2 original measurements (B/L and draft survey). The team recommended reducing the anomaly score from 0.89 to 0.15.",
    "report", "corrected", "Aynur Karimova", 0.90,
    "analytics-dedup-report", "internal_memo", 200, 10, 3, 1,
    ["C02", "primary_source", "correction"]
))

new_memories.append(M(
    "C02", "CME anomaly score", "reduced_for", "MV Turkmenbashi",
    "Following Karimova's provenance analysis, CME's anomaly score for MV Turkmenbashi's cargo discrepancy was reduced from 0.89 to 0.15, reflecting that 8 records of the same measurement do not constitute 8 independent data points.",
    "report", "corrected", "Aynur Karimova", 0.90,
    "cme-score-update", "system_generated", 200, 12, 1, 1,
    ["C02", "correction"],
    supersedes=[]
))

# --- C03 more unreceived corrections ---
new_memories.append(M(
    "C03", "MV Khazar Star", "flagged_in", "regional emissions database",
    "The Caspian Regional Emissions Monitoring database lists MV Khazar Star with a sulfur exceedance event dated 2031, based on the initial test. Status: 'open/unresolved.' No retest data has been entered.",
    "report", "repeated_claim", "emissions monitoring system", 0.60,
    "crem-database", "system_generated", 365, 20, 1, 1,
    ["C03", "repeated"]
))

new_memories.append(M(
    "C03", "MV Khazar Star fuel", "discussed_by", "Leyla Hasanova",
    "Cargo Logistics Director Leyla Hasanova noted in a logistics planning memo that MV Khazar Star 'has a fuel compliance issue' based on the port state control records she reviewed. She was unaware of the retest clearing the vessel.",
    "report", "supporting_belief", "Leyla Hasanova", 0.65,
    "hasanova-logistics-memo", "internal_memo", 365, 40, 2, 1,
    ["C03", "repeated"]
))

new_memories.append(M(
    "C03", "MV Khazar Star fuel retest", "confirms", "within spec at 0.49%",
    "The independent laboratory that conducted the MV Khazar Star fuel retest provided a certified analysis report showing sulfur content at 0.49% ± 0.01%, with the note that the original test's 0.52% reading falls within the expected measurement uncertainty range.",
    "report", "ground_truth", "certified laboratory", 0.95,
    "lab-retest-certified", "official_record", 365, 5, 1, 1,
    ["C03", "primary_source"]
))

# --- C04 more storm reports ---
new_memories.append(M(
    "C04", "MV Caspian Dawn", "filed_delay_report", "72 hours at Astara",
    "MV Caspian Dawn filed a delay report citing 72-hour weather detention at Astara Anchorage beginning September 15, 2032. The report references Storm Advisory SA-2032-019 issued by CME.",
    "report", "repeated_claim", "MV Caspian Dawn master", 0.70,
    "caspian-dawn-delay-report", "commercial", 472, 4, 2, 1,
    ["C04", "repeated"]
))

new_memories.append(M(
    "C04", "MV Turkmenbashi", "filed_delay_report", "72 hours at Astara",
    "MV Turkmenbashi filed a separate delay report for the same 72-hour weather event at Astara Anchorage. The ship's agent submitted it to CME, insurance, and the Turkmen Maritime Administration independently.",
    "report", "repeated_claim", "MV Turkmenbashi agent", 0.70,
    "turkmenbashi-delay-report", "commercial", 472, 4, 2, 1,
    ["C04", "repeated"]
))

new_memories.append(M(
    "C04", "Astara storm reports", "total_count", "17 documents",
    "A CME internal audit counted 17 separate documents referencing Storm SA-2032-019: 4 vessel delay reports, 4 insurance claims, 3 authority advisories, 2 coast guard logs, 2 VTS records, 1 met office report, and 1 insurance industry summary. All describe the same 72-hour event.",
    "fact", "ground_truth", "Aynur Karimova", 0.95,
    "storm-document-audit", "internal_memo", 472, 30, 5, 2,
    ["C04", "primary_source"]
))

# --- C05 more incident copies ---
new_memories.append(M(
    "C05", "forklift incident", "reported_to", "insurance company",
    "Port of Baku's insurance broker filed Incident Report IR-2033-015 for the March 15, 2033 forklift fender-bender. Estimated damage: $1,200. No injuries. The same incident already recorded in the port's internal log, OSHA report, and port authority database.",
    "report", "repeated_claim", "insurance broker", 0.70,
    "insurance-ir-2033-015", "commercial", 560, 2, 3, 1,
    ["C05", "repeated"]
))

new_memories.append(M(
    "C05", "chemical spill", "reported_to", "environmental agency",
    "Port of Baku reported the July 22 chemical spill to the Azerbaijan Environmental Protection Agency, filing form EPA-HAZ-2033-0089. The spill involved 15 liters of hydraulic fluid, contained within 20 minutes. Same incident in 3 other systems.",
    "report", "repeated_claim", "Fatima Guliyeva", 0.70,
    "epa-haz-2033-0089", "regulatory", 600, 5, 2, 1,
    ["C05", "repeated"]
))

new_memories.append(M(
    "C05", "Port of Baku safety", "characterized_by", "industry benchmarking report",
    "An industry benchmarking report ranked Port of Baku's safety record as 'below average' based on '11 safety-related documents in 2033,' without noting that these 11 documents correspond to only 2 actual incidents.",
    "report", "inflated_claim", "industry benchmarking service", 0.45,
    "industry-benchmark-2033", "trade_publication", 600, 120, 15, 5,
    ["C05", "repeated"],
    derived=[]
))

# --- C06 more database propagation ---
new_memories.append(M(
    "C06", "MV Caspian Dawn", "screening_result", "CME compliance check",
    "CME's internal compliance screening on 2033-04-10 flagged MV Caspian Dawn with a 'potential sanctions match' alert, generated automatically from the same name-match algorithm that triggered the other databases.",
    "report", "repeated_claim", "CME compliance system", 0.60,
    "cme-compliance-alert", "system_generated", 680, 1, 1, 1,
    ["C06", "repeated"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn clearance", "forwarded_to", "CME and flag state",
    "The OFAC clearance for MV Caspian Dawn was forwarded to CME, the vessel owner, the flag state (Russia), and one of the two banks involved in the transaction. The other bank, GTCS, and the port state control were not updated.",
    "fact", "ground_truth", "Reza Ahmadi", 0.90,
    "clearance-distribution-log", "internal_memo", 680, 3, 2, 1,
    ["C06", "primary_source"]
))

new_memories.append(M(
    "C06", "MV Caspian Dawn", "delayed_at", "Turkmenbashi Port",
    "MV Caspian Dawn experienced a 6-hour delay at Turkmenbashi Port in June 2033 when the port's compliance check flagged the vessel based on outdated sanctions data from GTCS. The delay was resolved after the vessel owner produced the OFAC clearance letter.",
    "report", "ground_truth", "Leyla Hasanova", 0.85,
    "turkmenbashi-delay-2033", "commercial", 680, 60, 3, 1,
    ["C06"]
))

# --- C07 more derivative sources ---
new_memories.append(M(
    "C07", "MV Atropatene grounding", "cited_in", "Caspian shipping annual review",
    "The Caspian Shipping Annual Review 2034 listed MV Atropatene's grounding as a '$2.1 million incident,' citing trade media sources. The review did not consult the original surveyor reports.",
    "report", "inflated_claim", "annual review editor", 0.50,
    "caspian-annual-review-2034", "trade_publication", 730, 90, 10, 5,
    ["C07", "repeated"],
    derived=[]
))

new_memories.append(M(
    "C07", "MV Atropatene grounding", "damage_repair_cost", "$187,000",
    "The actual repair of MV Atropatene's grounding damage was completed at Baku Shipyard for $187,000, slightly below the lowest survey estimate of $180,000 due to efficient drydock scheduling. This final cost confirms the ~$195K estimate range, not the $2.1M.",
    "fact", "ground_truth", "Viktor Kovalenko", 0.95,
    "repair-invoice-2034", "commercial", 730, 120, 5, 2,
    ["C07", "primary_source"]
))

new_memories.append(M(
    "C07", "MV Atropatene damage", "reported_in", "insurer's loss summary",
    "Dmitri Volkov's Lloyd's liaison office issued a loss summary for MV Atropatene grounding citing the surveyor average of $195,000 and noting that 'widely circulated reports of $2.1M damage are based on an error in a broker newsletter.'",
    "report", "corrected", "Dmitri Volkov", 0.90,
    "lloyds-loss-summary", "commercial", 730, 30, 5, 2,
    ["C07", "primary_source", "correction"]
))

new_memories.append(M(
    "C07", "MV Atropatene $2.1M", "repeated_in", "social media maritime forum",
    "A popular Caspian maritime forum had 3 threads discussing MV Atropatene's '$2.1 million grounding damage,' with users citing the trade publications. No forum participant referenced the actual surveyor reports.",
    "report", "inflated_claim", "forum users", 0.35,
    "maritime-forum-threads", "social_media", 730, 60, 1, 1,
    ["C07", "repeated"]
))

# --- Cross-case provenance observations ---
new_memories.append(M(
    "background", "Nargiz Mammadova", "proposed", "provenance tracking system",
    "COO Nargiz Mammadova proposed implementing a provenance tracking system at CME that would tag each report with its original source and mark derivative copies, preventing confidence inflation from repeated reports of the same event.",
    "report", "ground_truth", "Nargiz Mammadova", 0.85,
    "mammadova-proposal-2034", "internal_memo", 800, 0, 5, 2,
    ["background"]
))

new_memories.append(M(
    "background", "CME", "processes", "6,000+ documents per month",
    "CME's data analytics platform processes over 6,000 maritime documents per month, including vessel reports, insurance filings, regulatory submissions, trade publications, and port authority notifications. Approximately 40% are derivative or duplicate reports of the same underlying events.",
    "fact", "ground_truth", "Aynur Karimova", 0.90,
    "cme-data-volume-report", "internal_memo", 500, 10, 3, 1,
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
    "How many times was MV Atropatene's hull condition reported by different parties?",
    "deduplication",
    ["At least 6-8 different parties reported the hull condition, but all trace back to one inspection finding minor paint degradation"],
    ["Multiple parties reported but from a single inspection event"],
    ["6-8 independent inspections found problems", "Each report represents an independent assessment"],
    [], [],
    "hard",
    notes="C01: One inspection → 6+ derivative reports"
))

new_queries.append(Q(
    "Did Captain Aliyev agree with the characterization of MV Atropatene having 'structural concerns'?",
    "factual_recall",
    ["No; Captain Aliyev formally objected, stating the original inspection found only paint degradation and that 'structural' was introduced by secondary sources"],
    ["Aliyev disputed the structural concerns characterization in a written memo"],
    ["Yes, Aliyev confirmed structural concerns", "Aliyev did not comment on the hull issue"],
    [], [],
    "medium",
    notes="C01: Aliyev's objection is a key primary source correcting the inflated narrative"
))

new_queries.append(Q(
    "What did Aynur Karimova's team conclude about the MV Turkmenbashi cargo anomaly score?",
    "correction_handling",
    ["Karimova's team found all 8 records trace to 2 original measurements and recommended reducing the anomaly score from 0.89 to 0.15"],
    ["The high anomaly score was based on counting duplicates as independent data; it was corrected downward"],
    ["The anomaly score of 0.89 was confirmed by the investigation", "8 independent sources validate the high score"],
    [], [],
    "hard",
    notes="C02: Deduplication analysis revealed inflated confidence scoring"
))

new_queries.append(Q(
    "Who was NOT notified of MV Khazar Star's fuel retest results?",
    "status_tracking",
    ["Port state control, Kazakh Maritime Administration, flag state inspector, environmental database, and insurance were not notified of the retest"],
    ["5 of 7 parties that received the initial result were never sent the retest"],
    ["All parties were notified", "Only 1 party missed the update"],
    [], [],
    "hard",
    notes="C03: Retest only went to chief engineer and owner; 5 parties still have outdated data"
))

new_queries.append(Q(
    "How many separate documents reference Storm SA-2032-019 at Astara Anchorage?",
    "factual_recall",
    ["17 documents: 4 vessel delay reports, 4 insurance claims, 3 authority advisories, 2 coast guard logs, 2 VTS records, 1 met office report, 1 insurance industry summary"],
    ["At least 15-17 documents, all referencing the same single storm event"],
    ["17 separate storm events occurred", "Each document represents a different weather incident"],
    [], [],
    "medium",
    notes="C04: CME audit counted 17 documents for 1 event"
))

new_queries.append(Q(
    "What was the actual cost to repair MV Atropatene's grounding damage?",
    "factual_recall",
    ["$187,000, completed at Baku Shipyard"],
    ["Approximately $187K-195K, confirming the surveyor estimates of ~$195K average"],
    ["$2.1 million", "$2,100,000", "Over $2 million"],
    [], [],
    "medium",
    notes="C07: Actual repair cost $187K confirms surveyors, refutes the $2.1M typo"
))

new_queries.append(Q(
    "What proportion of CME's monthly documents are derivative or duplicate?",
    "factual_recall",
    ["Approximately 40% of CME's 6,000+ monthly documents are derivative or duplicate reports"],
    ["About 40% are duplicates of underlying events"],
    ["CME has no duplicate documents", "All documents represent unique events"],
    [], [],
    "easy",
    notes="Background: CME data volume report"
))

new_queries.append(Q(
    "What real-world consequence did the unresolved sanctions flag have on MV Caspian Dawn?",
    "status_tracking",
    ["A 6-hour delay at Turkmenbashi Port in June 2033, when the port's compliance check used outdated GTCS data"],
    ["Delayed at Turkmenbashi due to outdated sanctions database; resolved when owner produced OFAC clearance"],
    ["No consequences resulted from the false flag", "The vessel was impounded for sanctions violations"],
    [], [],
    "medium",
    notes="C06: Real operational impact of unresolved false positive"
))

new_queries.append(Q(
    "Which parties received the OFAC clearance for MV Caspian Dawn, and which did not?",
    "provenance_tracking",
    ["Received: CME, vessel owner, Russian flag state, one bank. Not received: Bank of Baku, GTCS, port state control"],
    ["4 of 7 databases were updated; 3 were not"],
    ["All 7 databases received the clearance", "Only the vessel owner was notified"],
    [], [],
    "hard",
    notes="C06: Asymmetric clearance distribution"
))

new_queries.append(Q(
    "How does the industry benchmarking report's characterization of Port of Baku's safety compare to reality?",
    "confidence_calibration",
    ["The report rated Baku 'below average' based on 11 safety documents, but these represent only 2 actual incidents — the report conflated document count with incident count"],
    ["The benchmarking inflated the safety concern by counting duplicate records"],
    ["The report accurately reflects 11 safety incidents", "11 documents prove systemic safety failures"],
    [], [],
    "hard",
    notes="C05: 11 documents ≠ 11 incidents"
))

new_queries.append(Q(
    "What systemic improvement did Nargiz Mammadova propose for CME?",
    "factual_recall",
    ["A provenance tracking system that would tag reports with original sources and mark derivative copies to prevent confidence inflation"],
    ["A system to track information provenance and prevent duplicate reports from inflating confidence"],
    ["Mammadova proposed no improvements", "Mammadova proposed hiring more staff"],
    [], [],
    "easy",
    notes="Background: Mammadova's proposal addresses the core experiment theme"
))

new_queries.append(Q(
    "In the MV Atropatene hull case, how many sources describe 'structural concerns' vs. how many describe only 'paint degradation'?",
    "confidence_calibration",
    ["Multiple derivative sources mention 'structural concerns' but only the primary sources (classification society, captain) report the actual finding of paint degradation with no structural implications"],
    ["The structural concerns label was introduced by secondary sources; primary inspection found only cosmetic issues"],
    ["More sources say structural, so structural concerns are confirmed", "The majority of reports establish structural issues"],
    [], [],
    "hard",
    conflict=True,
    notes="C01: Source count vs source quality — derivative inflation"
))

new_queries.append(Q(
    "Should a system weight the 5 sources saying MV Khazar Star fuel is out-of-spec more heavily than the 2 sources saying it's within spec?",
    "source_quality",
    ["No; the 2 sources with the retest result (0.49%) supersede the 5 sources with the initial result (0.52%), regardless of count. The 5 sources all derive from one initial test; the 2 sources include a retest that corrects it."],
    ["Source count is irrelevant; the retest is more recent and authoritative than the initial test"],
    ["Yes, 5 sources outweigh 2", "The 5-to-2 ratio indicates non-compliance is more likely"],
    [], [],
    "hard",
    conflict=True,
    notes="C03: Classic repeated exposure vs. correction handling"
))

new_queries.append(Q(
    "What evidence supports the $2.1 million damage figure for MV Atropatene, and what evidence contradicts it?",
    "source_quality",
    ["No primary evidence supports $2.1M — it originated from a single typo. Three independent surveyor reports ($180K-$210K), the actual repair cost ($187K), and Lloyd's loss summary all contradict it."],
    ["The $2.1M figure traces to one newsletter typo; all primary sources show ~$195K"],
    ["7 sources confirm $2.1M vs only 3 saying $195K", "The weight of evidence supports the higher figure"],
    [], [],
    "hard",
    notes="C07: 7 derivative sources with typo vs 3 primary + 1 actual repair cost"
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

print(f"Round 3: {len(memories)} memories, {len(queries)} queries")
