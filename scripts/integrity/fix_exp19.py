#!/usr/bin/env python3
"""Exp19 Round 1 expansion: 48 → ~110 memories, 10 → ~28 queries."""

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

mid_counter = len(memories) + 1

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp19-r1-{mid_counter}".encode()).hexdigest()[:8]
    mid_counter += 1
    ev = T0 + timedelta(days=ev_off)
    ob = T0 + timedelta(days=ev_off + obs_off)
    au = T0 + timedelta(days=ev_off + obs_off + auth_off)
    ig = T0 + timedelta(days=ev_off + obs_off + auth_off + ing_off)
    return {
        "memory_id": f"E19-{_hash}", "experiment": "exp19", "story_id": story,
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

qid_counter = len(queries)

def Q(query, cat, expected, acceptable, forbidden, rel, dist, difficulty,
      uncertainty=False, conflict=False, disambiguate=False,
      scope=False, abstain=False, notes=""):
    global qid_counter
    qid_counter += 1
    return {
        "query_id": f"Q19-{qid_counter:02d}", "query": query, "category": cat,
        "expected_claims": expected, "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": rel, "distractor_memory_ids": dist,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambiguate,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "difficulty": difficulty, "notes": notes
    }

new_mem = []
new_q = []
by_story = {}
for m in memories:
    by_story.setdefault(m.get("story_id",""), []).append(m)

# More background
new_mem.append(M("bg", "Fatima Guliyeva", "holds_role", "Regulatory Compliance Manager",
    "Fatima Guliyeva manages regulatory compliance at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG11", "hr_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Reza Ahmadi", "holds_role", "Iranian Trade Representative",
    "Reza Ahmadi serves as Iranian Trade Representative at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG12", "hr_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Timur Nazarov", "holds_role", "Vessel Traffic Service Controller",
    "Timur Nazarov is the Vessel Traffic Service Controller at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG13", "hr_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Aynur Karimova", "holds_role", "Data Analytics Manager",
    "Aynur Karimova is the Data Analytics Manager at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG14", "hr_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Viktor Kovalenko", "holds_role", "Salvage & Emergency Response Chief",
    "Viktor Kovalenko is the Salvage and Emergency Response Chief at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG15", "hr_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Port of Baku", "has", "12 berths and handles 8M tonnes annually",
    "The Port of Baku has 12 commercial berths and handles approximately 8 million tonnes of cargo annually.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG16", "port_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Kuryk Terminal", "is_a", "Kazakh oil export terminal",
    "Kuryk Terminal is the primary Kazakh oil export terminal on the eastern Caspian coast.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG17", "port_record",
    0, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "Caspian Sea", "has", "5 littoral states",
    "The Caspian Sea is bordered by 5 littoral states: Azerbaijan, Iran, Kazakhstan, Russia, and Turkmenistan.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG18", "reference",
    0, 0, 1, 1, ["background"]))

# C01 more repetitions
c01_orig_id = by_story["C01"][0]["memory_id"]

new_mem.append(M("C01", "classification society report", "rated", "MV Atropatene satisfactory with observations",
    "Classification society survey report rated MV Atropatene as 'satisfactory with observations' — the second-highest rating on a 4-point scale.",
    "observation", "ground_truth", "system", 1.0, "SRC-C01-6", "class_report",
    287, 1, 3, 1, ["C01", "primary_source"]))

new_mem.append(M("C01", "charterer inquiry", "asked_about", "MV Atropatene hull condition",
    "A prospective charterer inquired about MV Atropatene hull condition after seeing the broker newsletter report about 'hull condition concerns.'",
    "event", "repeated_claim", "Leyla Hasanova", 0.75, "SRC-C01-7", "commercial_inquiry",
    287, 12, 14, 1, ["C01", "repeated"],
    derived=[c01_orig_id]))

new_mem.append(M("C01", "owner's response", "clarified", "MV Atropatene has minor paint issue only",
    "MV Atropatene's owner responded to the charterer inquiry clarifying that the hull has minor paint degradation only, with classification society confirmation of satisfactory condition.",
    "event", "corrected", "Captain Yusif Aliyev", 1.0, "SRC-C01-8", "owner_letter",
    287, 14, 15, 1, ["C01", "correction"],
    contradicts=[by_story["C01"][-1]["memory_id"]]))

# C02 more document copies
c02_bl_id = by_story["C02"][0]["memory_id"]

new_mem.append(M("C02", "shipper's manifest", "lists_cargo", "4,850 tonnes per B/L",
    "Shipper's manifest for MV Turkmenbashi lists cargo weight as 4,850 tonnes, matching the bill of lading.",
    "fact", "repeated_claim", "Leyla Hasanova", 0.9, "SRC-C02-7", "shipper_manifest",
    400, 0, 1, 1, ["C02", "repeated"],
    derived=[c02_bl_id]))

new_mem.append(M("C02", "consignee receipt", "acknowledges", "4,850 tonnes cargo per B/L",
    "Consignee at Port of Baku acknowledged receipt of cargo per B/L weight of 4,850 tonnes.",
    "fact", "repeated_claim", "Leyla Hasanova", 0.9, "SRC-C02-8", "consignee_receipt",
    403, 0, 1, 1, ["C02", "repeated"],
    derived=[c02_bl_id]))

new_mem.append(M("C02", "3% discrepancy", "is_within", "normal commercial tolerance",
    "A 3% cargo weight discrepancy between B/L and draft survey is within normal commercial tolerance for bulk cargoes and does not typically trigger a claim.",
    "fact", "ground_truth", "Dmitri Volkov", 0.95, "SRC-C02-9", "industry_standard",
    405, 2, 3, 1, ["C02"]))

# C03 more forwarded notifications
c03_test1_id = by_story["C03"][0]["memory_id"]

new_mem.append(M("C03", "owner notification", "received", "MV Khazar Star fuel non-compliance report",
    "MV Khazar Star owner received notification of fuel sulfur non-compliance from chief engineer.",
    "event", "repeated_claim", "system", 0.85, "SRC-C03-8", "owner_communication",
    180, 1, 2, 1, ["C03", "repeated"],
    derived=[c03_test1_id]))

new_mem.append(M("C03", "owner", "received_retest", "fuel within spec confirmation",
    "MV Khazar Star owner received the retest confirmation showing fuel sulfur at 0.49%, within spec.",
    "event", "corrected", "system", 0.95, "SRC-C03-9", "owner_communication",
    183, 1, 2, 1, ["C03", "correction"],
    derived=[by_story["C03"][1]["memory_id"]]))

new_mem.append(M("C03", "flag state record", "was_not_updated", "with retest result",
    "The Kazakhstan flag state record was not updated with the retest result. Their database still shows the initial 0.52% non-compliance.",
    "event", "ground_truth", "Fatima Guliyeva", 0.9, "SRC-C03-10", "compliance_record",
    200, 1, 2, 1, ["C03"]))

new_mem.append(M("C03", "port state record", "was_not_updated", "with retest result",
    "The port state control record was not updated with the retest result.",
    "event", "ground_truth", "Sergei Petrov", 0.9, "SRC-C03-11", "compliance_record",
    200, 1, 2, 1, ["C03"]))

new_mem.append(M("C03", "insurance record", "was_not_updated", "with retest result",
    "The insurance notification record was not updated with the retest result.",
    "event", "ground_truth", "Dmitri Volkov", 0.9, "SRC-C03-12", "compliance_record",
    200, 1, 2, 1, ["C03"]))

# C04 more reports of same storm
c04_storm_id = by_story["C04"][0]["memory_id"]

new_mem.append(M("C04", "MV Turkmenbashi", "filed_delay_report", "72 hours weather delay at Astara",
    "MV Turkmenbashi filed delay report: 72-hour weather delay at Astara Anchorage.",
    "event", "repeated_claim", "system", 1.0, "SRC-C04-6", "delay_report",
    555, 0, 1, 1, ["C04", "repeated"],
    derived=[c04_storm_id]))

new_mem.append(M("C04", "MV Caspian Dawn", "filed_delay_report", "72 hours weather delay at Astara",
    "MV Caspian Dawn filed delay report: 72-hour weather delay at Astara Anchorage.",
    "event", "repeated_claim", "system", 1.0, "SRC-C04-7", "delay_report",
    555, 0, 1, 1, ["C04", "repeated"],
    derived=[c04_storm_id]))

new_mem.append(M("C04", "insurance claim 1", "filed_for", "MV Atropatene weather delay",
    "Insurance claim filed for MV Atropatene 72-hour weather delay at Astara.",
    "event", "repeated_claim", "Dmitri Volkov", 0.95, "SRC-C04-8", "insurance_claim",
    558, 1, 3, 1, ["C04", "repeated"],
    derived=[c04_storm_id]))

new_mem.append(M("C04", "insurance claim 2", "filed_for", "MV Khazar Star weather delay",
    "Insurance claim filed for MV Khazar Star 72-hour weather delay at Astara.",
    "event", "repeated_claim", "Dmitri Volkov", 0.95, "SRC-C04-9", "insurance_claim",
    558, 1, 3, 1, ["C04", "repeated"],
    derived=[c04_storm_id]))

new_mem.append(M("C04", "port authority", "recorded", "4 vessels delayed by storm at Astara",
    "Port authority recorded 4 vessels delayed by the December 8-10 storm at Astara Anchorage.",
    "event", "repeated_claim", "Nargiz Mammadova", 1.0, "SRC-C04-10", "port_record",
    558, 0, 2, 1, ["C04", "repeated"],
    derived=[c04_storm_id]))

new_mem.append(M("C04", "weather service", "confirmed", "65-knot sustained winds Dec 8-10",
    "National weather service confirmed sustained winds of 65 knots at Astara Anchorage, December 8-10, 2031.",
    "fact", "ground_truth", "system", 1.0, "SRC-C04-11", "weather_record",
    555, 0, 1, 1, ["C04", "primary_source"]))

# C05 more copies
c05_inc1_id = by_story["C05"][0]["memory_id"]
c05_inc2_id = by_story["C05"][1]["memory_id"]

new_mem.append(M("C05", "insurance notification 1", "recorded", "forklift incident at Port of Baku",
    "Insurance carrier notified of forklift collision at Port of Baku warehouse 3.",
    "event", "repeated_claim", "Dmitri Volkov", 1.0, "SRC-C05-5", "insurance_notification",
    1045, 1, 3, 1, ["C05", "repeated"],
    derived=[c05_inc1_id]))

new_mem.append(M("C05", "OSHA report 2", "recorded", "chemical spill at Port of Baku",
    "OSHA report #2033-BK-0603 recorded the chemical spill at Port of Baku berth 7.",
    "fact", "repeated_claim", "Fatima Guliyeva", 1.0, "SRC-C05-6", "osha_report",
    1098, 1, 3, 1, ["C05", "repeated"],
    derived=[c05_inc2_id]))

new_mem.append(M("C05", "insurance notification 2", "recorded", "chemical spill at Port of Baku",
    "Insurance carrier notified of chemical spill at Port of Baku berth 7.",
    "event", "repeated_claim", "Dmitri Volkov", 1.0, "SRC-C05-7", "insurance_notification",
    1098, 1, 3, 1, ["C05", "repeated"],
    derived=[c05_inc2_id]))

new_mem.append(M("C05", "port authority annual report", "mentioned", "2 OSHA-recordable incidents in 2033",
    "Port of Baku annual report mentioned 2 OSHA-recordable incidents in 2033, both classified as minor.",
    "fact", "repeated_claim", "Nargiz Mammadova", 0.95, "SRC-C05-8", "annual_report",
    1150, 2, 5, 2, ["C05", "repeated"],
    derived=[c05_inc1_id, c05_inc2_id]))

new_mem.append(M("C05", "PR release 2", "highlighted", "new safety training program",
    "Second PR release highlighted new mandatory safety training program implemented after 2033 incidents.",
    "event", "inflated_claim", "Nargiz Mammadova", 0.8, "SRC-C05-9", "press_release",
    1110, 2, 5, 2, ["C05", "repeated"],
    derived=[c05_inc1_id, c05_inc2_id]))

new_mem.append(M("C05", "PR release 3", "announced", "zero-incident target for 2034",
    "Third PR release announced Port of Baku's zero-incident target for 2034, referencing 2033 as a baseline year.",
    "event", "inflated_claim", "Nargiz Mammadova", 0.8, "SRC-C05-10", "press_release",
    1130, 2, 5, 2, ["C05", "repeated"],
    derived=[c05_inc1_id, c05_inc2_id]))

# C06 more compliance echoes
c06_flag_id = by_story["C06"][0]["memory_id"]
c06_clear_id = by_story["C06"][1]["memory_id"]

new_mem.append(M("C06", "bank 2", "flagged", "MV Caspian Dawn in sanctions screening",
    "Second Caspian Commercial Bank flagged MV Caspian Dawn in trade finance sanctions screening.",
    "event", "repeated_claim", "system", 0.75, "SRC-C06-6", "bank_compliance",
    700, 0, 2, 1, ["C06", "repeated"],
    derived=[c06_flag_id]))

new_mem.append(M("C06", "CME compliance", "flagged", "MV Caspian Dawn in internal screening",
    "CME's internal compliance system flagged MV Caspian Dawn for sanctions concern.",
    "event", "repeated_claim", "Fatima Guliyeva", 0.8, "SRC-C06-7", "cme_compliance",
    700, 0, 1, 1, ["C06", "repeated"],
    derived=[c06_flag_id]))

new_mem.append(M("C06", "port state", "updated_record", "MV Caspian Dawn cleared",
    "Port state control updated their record: MV Caspian Dawn sanctions flag cleared, false positive confirmed.",
    "event", "corrected", "Sergei Petrov", 1.0, "SRC-C06-8", "port_state_record",
    701, 0, 2, 1, ["C06", "correction"],
    supersedes=[c06_flag_id]))

new_mem.append(M("C06", "insurance", "updated_record", "MV Caspian Dawn cleared",
    "Insurance compliance database updated: MV Caspian Dawn sanctions flag cleared.",
    "event", "corrected", "Dmitri Volkov", 1.0, "SRC-C06-9", "insurance_record",
    701, 1, 2, 1, ["C06", "correction"],
    supersedes=[c06_flag_id]))

new_mem.append(M("C06", "CME compliance", "updated_record", "MV Caspian Dawn cleared",
    "CME compliance system updated: MV Caspian Dawn cleared of sanctions concern.",
    "event", "corrected", "Fatima Guliyeva", 1.0, "SRC-C06-10", "cme_record",
    701, 0, 1, 1, ["C06", "correction"],
    supersedes=[c06_flag_id]))

new_mem.append(M("C06", "bank 1 record", "still_shows", "MV Caspian Dawn flagged",
    "First Caspian Bank's compliance record still shows MV Caspian Dawn as flagged — record was not updated after clearance.",
    "event", "ground_truth", "system", 0.9, "SRC-C06-11", "bank_record",
    730, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "bank 2 record", "still_shows", "MV Caspian Dawn flagged",
    "Second Caspian Commercial Bank's record still shows MV Caspian Dawn as flagged.",
    "event", "ground_truth", "system", 0.9, "SRC-C06-12", "bank_record",
    730, 0, 1, 1, ["C06"]))

new_mem.append(M("C06", "trade compliance service", "still_shows", "MV Caspian Dawn as concern",
    "The international trade compliance service still lists MV Caspian Dawn with a sanctions concern flag — their record was never updated.",
    "event", "ground_truth", "system", 0.85, "SRC-C06-13", "compliance_service",
    730, 0, 1, 1, ["C06"]))

# C07 more copies of typo
c07_typo_id = [m["memory_id"] for m in by_story["C07"] if "inflated_claim" in m.get("truth_role","")][0]
c07_surv1_id = by_story["C07"][0]["memory_id"]

new_mem.append(M("C07", "trade publication 3", "reported", "$2.1M Atropatene grounding damage",
    "Lloyd's List reported $2.1 million damage for MV Atropatene grounding, citing Caspian Shipping Weekly.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-7", "trade_publication",
    800, 12, 16, 3, ["C07", "repeated"],
    derived=[c07_typo_id], contradicts=[c07_surv1_id]))

new_mem.append(M("C07", "trade publication 4", "mentioned", "$2.1M Atropatene incident",
    "Fairplay Magazine mentioned the $2.1 million MV Atropatene grounding incident in a roundup article.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-8", "trade_publication",
    800, 15, 20, 3, ["C07", "repeated"],
    derived=[c07_typo_id], contradicts=[c07_surv1_id]))

new_mem.append(M("C07", "insurance newsletter 1", "cited", "$2.1M Atropatene damage",
    "Marine Insurance Quarterly cited $2.1 million Atropatene grounding damage in market loss analysis.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-9", "insurance_newsletter",
    800, 14, 18, 3, ["C07", "repeated"],
    derived=[c07_typo_id], contradicts=[c07_surv1_id]))

new_mem.append(M("C07", "insurance newsletter 2", "referenced", "$2.1M Atropatene claim",
    "P&I Club newsletter referenced $2.1 million Atropatene grounding claim.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-10", "insurance_newsletter",
    800, 16, 22, 3, ["C07", "repeated"],
    derived=[c07_typo_id], contradicts=[c07_surv1_id]))

new_mem.append(M("C07", "regulatory filing", "used", "$2.1M figure for Atropatene incident",
    "A regulatory filing referenced the $2.1 million damage figure for the MV Atropatene grounding.",
    "fact", "inflated_claim", "Fatima Guliyeva", 0.6, "SRC-C07-11", "regulatory_filing",
    800, 20, 25, 3, ["C07", "repeated"],
    derived=[c07_typo_id], contradicts=[c07_surv1_id]))

# Queries
new_q.append(Q(
    "How many separate weather events caused delays at Astara Anchorage in 2031?",
    "deduplication",
    ["One storm (December 8-10) caused all delays",
     "15+ documents all describe the same single weather event"],
    ["There was only one weather delay event despite multiple reports"],
    ["15 weather events occurred", "Multiple storms hit",
     "Each vessel experienced a different delay"],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C04" and "primary_source" in m.get("tags",[])][:2],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C04" and "repeated" in m.get("tags",[])][:5],
    "medium"
))

new_q.append(Q(
    "How many compliance databases flagged MV Caspian Dawn, and how many have been updated?",
    "status_tracking",
    ["7 databases flagged the vessel", "4 have been updated to show clearance",
     "3 still show the vessel as flagged despite the false positive being resolved"],
    ["Majority of records are updated but some lag behind"],
    ["All databases are updated", "The vessel is still under sanctions",
     "Zero databases cleared the flag"],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C06"][:10],
    [],
    "hard",
    notes="Must track update status across multiple databases"
))

new_q.append(Q(
    "Was the MV Khazar Star fuel retest communicated to all parties who received the initial result?",
    "provenance_tracking",
    ["No — only the chief engineer and owner received the retest result",
     "Flag state, port state, and insurance records were NOT updated"],
    ["3 of 5 notified parties still have outdated non-compliance records"],
    ["All parties were informed", "The retest was widely communicated"],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C03" and "was_not_updated" in m.get("predicate","")][:3] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "retest" in m.get("predicate","")][:1],
    [],
    "hard"
))

new_q.append(Q(
    "Is a 3% cargo weight discrepancy for MV Turkmenbashi significant?",
    "confidence_calibration",
    ["A 3% discrepancy is within normal commercial tolerance for bulk cargoes",
     "It does not typically trigger an insurance claim"],
    ["The discrepancy is commercially normal"],
    ["The discrepancy is alarming", "8 documents confirm a major problem",
     "This indicates cargo theft"],
    [n["memory_id"] for n in new_mem if "normal commercial tolerance" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and "repeated" in m.get("tags",[])][:4],
    "medium"
))

new_q.append(Q(
    "What is MV Atropatene's classification society rating?",
    "source_quality",
    ["Satisfactory with observations — the second-highest rating on a 4-point scale"],
    ["The vessel passed inspection with minor notes"],
    ["The vessel has structural problems", "The classification was downgraded",
     "Multiple sources report serious hull issues"],
    [n["memory_id"] for n in new_mem if "classification society" in n.get("subject","").lower() and "satisfactory" in n.get("text","")][:1],
    [m["memory_id"] for m in memories if m.get("story_id") == "C01" and "inflated_claim" in m.get("truth_role","")][:2],
    "medium"
))

new_q.append(Q(
    "How many PR releases did Port of Baku issue about safety in 2033?",
    "deduplication",
    ["Three PR releases, all referencing the same 2 incidents"],
    ["Multiple PR releases about the same underlying events"],
    ["3 separate safety incidents prompted 3 releases",
     "Each PR was about a different event"],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C05" and "PR" in m.get("subject","")][:3],
    [m["memory_id"] for m in memories if m.get("story_id") == "C05" and "primary_source" in m.get("tags",[])][:2],
    "medium"
))

new_q.append(Q(
    "Which databases still show MV Caspian Dawn as sanctions-flagged?",
    "status_tracking",
    ["First Caspian Bank, Second Caspian Commercial Bank, and the trade compliance service",
     "These 3 databases were never updated after the clearance"],
    ["3 of 7 original flagging databases remain uncorrected"],
    ["All databases are cleared", "No database shows a flag anymore"],
    [n["memory_id"] for n in new_mem if "still_shows" in n.get("predicate","")][:3],
    [m["memory_id"] for m in memories if m.get("story_id") == "C06" and "corrected" in m.get("truth_role","")][:2],
    "medium"
))

new_q.append(Q(
    "Did MV Atropatene's owner respond to the hull condition rumors?",
    "factual_recall",
    ["Yes — the owner clarified it was minor paint degradation only",
     "Owner cited classification society confirmation of satisfactory condition"],
    ["The owner pushed back against inflated reports"],
    ["No response was made", "The owner confirmed structural concerns"],
    [n["memory_id"] for n in new_mem if "owner's response" in n.get("subject","").lower()][:1],
    [],
    "easy"
))

new_q.append(Q(
    "What is the actual insurance exposure from the MV Turkmenbashi cargo discrepancy?",
    "confidence_calibration",
    ["Minimal — the 3% discrepancy is within normal commercial tolerance",
     "Insurance covers the cargo at B/L weight of 4,850 tonnes at $2.3M"],
    ["No claim is expected from this discrepancy"],
    ["Significant insurance loss expected", "8 documents support a major claim",
     "The discrepancy indicates fraud"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and ("insurance" in m.get("subject","").lower() or "tolerance" in m.get("text",""))][:2],
    [m["memory_id"] for m in memories if m.get("story_id") == "C02" and "repeated" in m.get("tags",[])][:4],
    "medium"
))

new_q.append(Q(
    "How many insurance claims were filed for the December 2031 Astara storm?",
    "deduplication",
    ["4 insurance claims were filed — one per delayed vessel",
     "All claims reference the same single weather event"],
    ["Multiple claims for the same storm, not multiple storms"],
    ["4 separate storms triggered 4 claims",
     "Each claim is for a different weather event"],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C04" and "insurance" in m.get("subject","").lower()][:2] +
    [m["memory_id"] for m in memories if m.get("story_id") == "C04" and "primary_source" in m.get("tags",[])][:1],
    [],
    "medium"
))

new_q.append(Q(
    "What is the Port of Baku's actual safety record for 2033?",
    "confidence_calibration",
    ["2 minor OSHA-recordable incidents (forklift collision, chemical spill)",
     "Both were minor with no injuries"],
    ["A reasonably good safety record with only minor incidents"],
    ["8 safety incidents occurred", "11 safety events were documented",
     "The port has serious safety problems"],
    [m["memory_id"] for m in memories if m.get("story_id") == "C05" and "primary_source" in m.get("tags",[])][:2],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C05" and "repeated" in m.get("tags",[])][:5],
    "medium"
))

new_q.append(Q(
    "How many document copies of the MV Turkmenbashi cargo weight exist?",
    "provenance_tracking",
    ["8 documents list the cargo weight, but only 2 original measurements exist",
     "B/L says 4,850t and draft survey says 4,705t — all others copy the B/L figure"],
    ["6 of 8 documents derive from the B/L without independent measurement"],
    ["8 independent measurements confirm the weight",
     "All 8 documents are independent data sources"],
    [m["memory_id"] for m in memories + new_mem if m.get("story_id") == "C02"][:8],
    [],
    "hard",
    notes="Must recognize derivative documents vs. independent measurements"
))

memories.extend(new_mem)
queries.extend(new_q)

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
