#!/usr/bin/env python3
"""Generate Experiment 19 — Repeated Exposure / Confidence Inflation.

Setting: Caspian Maritime Exchange (CME), Baku, Azerbaijan (2030-2035).
Tests whether memory systems inflate confidence from repeated exposure
when multiple sources trace back to a single origin.

Cases:
  C01: Hull Inspection Rumor (paint degradation → "structural concerns")
  C02: Cargo Weight Discrepancy (same 2 measurements in 8 documents)
  C03: Fuel Quality Allegation (5 say out-of-spec, 2 say retest passed)
  C04: Weather Delay Attribution (1 storm, 15+ reports)
  C05: Safety Record Inflation (2 incidents in 11 documents)
  C06: Sanctions Compliance Echo (7 flagged, only 4 cleared)
  C07: Salvage Value Estimate ($195K real vs $2.1M typo in 7 sources)
"""

import json, hashlib, os, sys
from datetime import datetime, timedelta, timezone

OUT = sys.argv[1] if len(sys.argv) > 1 else "experiment_19_repeated_exposure"
os.makedirs(OUT, exist_ok=True)

UTC = timezone.utc
T0 = datetime(2030, 6, 1, tzinfo=UTC)

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

mid_counter = 0
def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    mid_counter += 1
    _hash = hashlib.md5(f"exp19-r0-{mid_counter}".encode()).hexdigest()[:8]
    ev = T0 + timedelta(days=ev_off)
    ob = T0 + timedelta(days=ev_off + obs_off)
    au = T0 + timedelta(days=ev_off + obs_off + auth_off)
    ig = T0 + timedelta(days=ev_off + obs_off + auth_off + ing_off)
    return {
        "memory_id": f"E19-{_hash}",
        "experiment": "exp19",
        "story_id": story,
        "event_time": ts(ev),
        "observation_time": ts(ob),
        "authored_time": ts(au),
        "ingestion_time": ts(ig),
        "subject": subj, "predicate": pred, "object": obj, "text": text,
        "memory_type": etype, "truth_role": truth_role,
        "belief_holder": holder, "confidence": conf,
        "source_id": src_id, "source_type": src_type,
        "derived_from": derived or [], "supersedes": supersedes or [],
        "contradicts": contradicts or [], "duplicates": duplicates or [],
        "aliases": aliases or [], "scope": scope, "tags": tags
    }

qid_counter = 0
def Q(query, cat, expected, acceptable, forbidden, rel, dist, difficulty,
      uncertainty=False, conflict=False, disambiguate=False,
      scope=False, abstain=False, notes=""):
    global qid_counter
    qid_counter += 1
    return {
        "query_id": f"Q19-{qid_counter:02d}",
        "query": query, "category": cat,
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

memories = []
queries = []

# === BACKGROUND ===
memories.append(M("bg", "Caspian Maritime Exchange", "is_located_in", "Baku, Azerbaijan",
    "The Caspian Maritime Exchange (CME) is a shipping and maritime trade hub headquartered in Baku, Azerbaijan, coordinating vessel traffic across the Caspian Sea.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG1", "institutional_record",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "Captain Yusif Aliyev", "holds_role", "Senior Harbor Pilot",
    "Captain Yusif Aliyev is the Senior Harbor Pilot at CME, with 25 years of Caspian Sea navigation experience.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG2", "hr_record",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "Nargiz Mammadova", "holds_role", "Chief Operations Officer",
    "Nargiz Mammadova serves as Chief Operations Officer at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG3", "hr_record",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "Dmitri Volkov", "holds_role", "Insurance Underwriter",
    "Dmitri Volkov is the Lloyd's of London liaison insurance underwriter at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG4", "hr_record",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "Leyla Hasanova", "holds_role", "Cargo Logistics Director",
    "Leyla Hasanova directs cargo logistics operations at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG5", "hr_record",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "MV Atropatene", "is_a", "bulk carrier, 45,000 DWT, Azerbaijani flag",
    "MV Atropatene is a 45,000 DWT bulk carrier registered under the Azerbaijani flag, regularly transiting the Caspian Sea.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG6", "vessel_registry",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "MV Khazar Star", "is_a", "oil tanker, 28,000 DWT, Kazakh flag",
    "MV Khazar Star is a 28,000 DWT oil tanker registered under the Kazakh flag.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG7", "vessel_registry",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "MV Turkmenbashi", "is_a", "container vessel, 12,000 DWT, Turkmen flag",
    "MV Turkmenbashi is a 12,000 DWT container vessel operating under the Turkmen flag.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG8", "vessel_registry",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "MV Caspian Dawn", "is_a", "general cargo, 8,000 DWT, Russian flag",
    "MV Caspian Dawn is an 8,000 DWT general cargo vessel registered under the Russian flag.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG9", "vessel_registry",
    0, 0, 1, 1, ["background"]))

memories.append(M("bg", "Sergei Petrov", "holds_role", "Coast Guard Liaison Officer",
    "Sergei Petrov serves as Coast Guard Liaison Officer at CME.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG10", "hr_record",
    0, 0, 1, 1, ["background"]))

# === C01: Hull Inspection Rumor ===
c01_orig = M("C01", "MV Atropatene hull inspection", "found", "minor paint degradation",
    "MV Atropatene underwent routine hull inspection on March 15, 2031. Inspector found minor paint degradation on starboard hull plates. Classification society rated the vessel 'satisfactory with observations.'",
    "observation", "ground_truth", "Captain Yusif Aliyev", 1.0, "SRC-C01-1", "inspection_report",
    287, 0, 1, 1, ["C01", "primary_source"])
memories.append(c01_orig)

c01_port = M("C01", "port state inspector", "noted", "paint degradation on MV Atropatene",
    "Port state control inspector noted paint degradation on MV Atropatene hull during routine inspection. Vessel cleared for continued operation.",
    "observation", "repeated_claim", "Sergei Petrov", 0.9, "SRC-C01-2", "port_state_report",
    287, 1, 2, 1, ["C01", "repeated"],
    derived=[c01_orig["memory_id"]])
memories.append(c01_port)

c01_insure = M("C01", "insurance surveyor", "reported", "hull coating issues on MV Atropatene",
    "Insurance surveyor reported hull coating issues on MV Atropatene requiring monitoring. Recommended re-inspection in 6 months.",
    "observation", "repeated_claim", "Dmitri Volkov", 0.85, "SRC-C01-3", "insurance_survey",
    287, 2, 3, 1, ["C01", "repeated"],
    derived=[c01_orig["memory_id"]])
memories.append(c01_insure)

c01_broker = M("C01", "broker newsletter", "reported", "hull condition concerns for MV Atropatene",
    "Maritime broker newsletter reported hull condition concerns for MV Atropatene, citing coating deterioration and recommending caution for charterers.",
    "observation", "inflated_claim", "system", 0.7, "SRC-C01-4", "broker_newsletter",
    287, 5, 7, 2, ["C01", "repeated"],
    derived=[c01_orig["memory_id"]])
memories.append(c01_broker)

c01_trade = M("C01", "trade magazine", "reported", "structural concerns for MV Atropatene",
    "Caspian Shipping Weekly reported structural concerns for MV Atropatene, citing multiple sources noting hull deterioration.",
    "observation", "inflated_claim", "system", 0.6, "SRC-C01-5", "trade_publication",
    287, 10, 14, 3, ["C01", "repeated"],
    derived=[c01_orig["memory_id"]],
    contradicts=[c01_orig["memory_id"]])
memories.append(c01_trade)

# === C02: Cargo Weight Discrepancy ===
c02_bl = M("C02", "MV Turkmenbashi B/L", "states_cargo_weight", "4,850 tonnes",
    "Bill of lading for MV Turkmenbashi voyage TK-2031-08 states cargo weight of 4,850 tonnes of cotton fiber.",
    "fact", "ground_truth", "Leyla Hasanova", 0.95, "SRC-C02-1", "bill_of_lading",
    400, 0, 1, 1, ["C02", "primary_source"])
memories.append(c02_bl)

c02_draft = M("C02", "MV Turkmenbashi draft survey", "measured_cargo_weight", "4,705 tonnes",
    "Draft survey at loading port measured MV Turkmenbashi cargo at 4,705 tonnes, a 3% discrepancy from the bill of lading figure.",
    "observation", "ground_truth", "Captain Yusif Aliyev", 0.95, "SRC-C02-2", "draft_survey",
    400, 0, 1, 1, ["C02", "primary_source"])
memories.append(c02_draft)

c02_customs = M("C02", "customs declaration", "lists_cargo", "4,850 tonnes per B/L",
    "Customs declaration for MV Turkmenbashi lists cargo weight as 4,850 tonnes, copying the B/L figure.",
    "fact", "repeated_claim", "Fatima Guliyeva", 0.9, "SRC-C02-3", "customs_form",
    400, 0, 2, 1, ["C02", "repeated"],
    derived=[c02_bl["memory_id"]])
memories.append(c02_customs)

c02_insurance = M("C02", "insurance certificate", "covers_cargo", "4,850 tonnes at $2.3M",
    "Marine insurance certificate covers MV Turkmenbashi cargo of 4,850 tonnes valued at $2.3 million.",
    "fact", "repeated_claim", "Dmitri Volkov", 0.9, "SRC-C02-4", "insurance_certificate",
    400, 1, 2, 1, ["C02", "repeated"],
    derived=[c02_bl["memory_id"]])
memories.append(c02_insurance)

c02_port = M("C02", "port authority record", "logs_cargo", "4,850 tonnes for MV Turkmenbashi",
    "Port of Baku cargo log records MV Turkmenbashi discharge of 4,850 tonnes of cotton fiber.",
    "fact", "repeated_claim", "Nargiz Mammadova", 0.9, "SRC-C02-5", "port_record",
    403, 0, 1, 1, ["C02", "repeated"],
    derived=[c02_bl["memory_id"]])
memories.append(c02_port)

c02_broker = M("C02", "broker report", "notes", "3% weight discrepancy on MV Turkmenbashi",
    "Broker's fixture recap notes 3% weight discrepancy between B/L (4,850t) and draft survey (4,705t) for MV Turkmenbashi.",
    "observation", "ground_truth", "system", 0.85, "SRC-C02-6", "broker_report",
    405, 2, 4, 1, ["C02"])
memories.append(c02_broker)

# === C03: Fuel Quality Allegation ===
c03_test1 = M("C03", "fuel sample from Kuryk Terminal", "showed", "sulfur at 0.52% (above 0.50% limit)",
    "Fuel sample from MV Khazar Star bunkering at Kuryk Terminal showed sulfur content of 0.52%, marginally exceeding the 0.50% regulatory limit.",
    "observation", "ground_truth", "system", 0.9, "SRC-C03-1", "lab_report",
    180, 0, 2, 1, ["C03", "primary_source"])
memories.append(c03_test1)

c03_retest = M("C03", "fuel retest", "showed", "sulfur at 0.49% (within spec)",
    "Retest of the same fuel sample from MV Khazar Star showed sulfur content of 0.49%, within the 0.50% regulatory limit. The initial 0.52% result was likely a testing error.",
    "observation", "corrected", "system", 0.95, "SRC-C03-2", "lab_report",
    180, 3, 4, 1, ["C03", "primary_source", "correction"],
    supersedes=[c03_test1["memory_id"]])
memories.append(c03_retest)

c03_eng = M("C03", "chief engineer MV Khazar Star", "reported", "out-of-spec fuel sample",
    "Chief engineer of MV Khazar Star reported the out-of-spec fuel sample (0.52% sulfur) to the vessel's owner.",
    "event", "repeated_claim", "system", 0.85, "SRC-C03-3", "vessel_report",
    180, 0, 1, 1, ["C03", "repeated"],
    derived=[c03_test1["memory_id"]])
memories.append(c03_eng)

c03_flag = M("C03", "flag state notification", "recorded", "MV Khazar Star fuel non-compliance",
    "Kazakhstan flag state was notified of MV Khazar Star fuel non-compliance: sulfur at 0.52% vs 0.50% limit.",
    "event", "repeated_claim", "Fatima Guliyeva", 0.85, "SRC-C03-4", "flag_state_record",
    180, 1, 3, 1, ["C03", "repeated"],
    derived=[c03_test1["memory_id"]])
memories.append(c03_flag)

c03_port_state = M("C03", "port state control", "recorded", "MV Khazar Star fuel violation",
    "Port state control recorded fuel sulfur violation for MV Khazar Star at Kuryk Terminal.",
    "event", "repeated_claim", "Sergei Petrov", 0.85, "SRC-C03-5", "port_state_record",
    180, 1, 3, 1, ["C03", "repeated"],
    derived=[c03_test1["memory_id"]])
memories.append(c03_port_state)

c03_insure = M("C03", "insurance notification", "flagged", "MV Khazar Star fuel quality issue",
    "Insurance underwriter was notified of MV Khazar Star fuel quality issue (sulfur at 0.52%).",
    "event", "repeated_claim", "Dmitri Volkov", 0.8, "SRC-C03-6", "insurance_notification",
    180, 2, 3, 1, ["C03", "repeated"],
    derived=[c03_test1["memory_id"]])
memories.append(c03_insure)

c03_eng_cleared = M("C03", "chief engineer", "received_retest_result", "fuel within spec",
    "Chief engineer of MV Khazar Star was informed that the retest showed fuel sulfur at 0.49%, within spec.",
    "event", "corrected", "system", 0.95, "SRC-C03-7", "vessel_communication",
    183, 0, 1, 1, ["C03", "correction"],
    derived=[c03_retest["memory_id"]])
memories.append(c03_eng_cleared)

# === C04: Weather Delay ===
c04_storm = M("C04", "severe storm", "occurred_at", "Astara Anchorage, December 2031",
    "A severe storm with sustained winds of 65 knots hit Astara Anchorage on December 8-10, 2031, causing a 72-hour delay for all vessels.",
    "event", "ground_truth", "Timur Nazarov", 1.0, "SRC-C04-1", "weather_service",
    555, 0, 1, 1, ["C04", "primary_source"])
memories.append(c04_storm)

c04_v1 = M("C04", "MV Atropatene", "filed_delay_report", "72 hours weather delay at Astara",
    "MV Atropatene filed delay report: 72-hour weather delay at Astara Anchorage, December 8-10, 2031.",
    "event", "repeated_claim", "Captain Yusif Aliyev", 1.0, "SRC-C04-2", "delay_report",
    555, 0, 1, 1, ["C04", "repeated"],
    derived=[c04_storm["memory_id"]])
memories.append(c04_v1)

c04_v2 = M("C04", "MV Khazar Star", "filed_delay_report", "72 hours weather delay at Astara",
    "MV Khazar Star filed delay report: 72-hour weather delay at Astara Anchorage, December 8-10, 2031.",
    "event", "repeated_claim", "system", 1.0, "SRC-C04-3", "delay_report",
    555, 0, 1, 1, ["C04", "repeated"],
    derived=[c04_storm["memory_id"]])
memories.append(c04_v2)

c04_cg = M("C04", "coast guard", "issued_advisory", "all vessels shelter at Astara",
    "Coast guard issued storm advisory: all vessels to shelter at Astara Anchorage, December 8-10, 2031.",
    "event", "repeated_claim", "Sergei Petrov", 1.0, "SRC-C04-4", "coast_guard_advisory",
    555, 0, 1, 1, ["C04", "repeated"],
    derived=[c04_storm["memory_id"]])
memories.append(c04_cg)

c04_cme = M("C04", "CME", "issued_notice", "operational delay advisory for Astara",
    "CME issued operational delay advisory for Astara Anchorage area, December 8-10, 2031.",
    "event", "repeated_claim", "Nargiz Mammadova", 1.0, "SRC-C04-5", "cme_advisory",
    555, 0, 1, 1, ["C04", "repeated"],
    derived=[c04_storm["memory_id"]])
memories.append(c04_cme)

# === C05: Safety Record Inflation ===
c05_inc1 = M("C05", "Port of Baku", "had_incident", "forklift collision in warehouse 3",
    "Minor forklift collision in Port of Baku warehouse 3 on April 12, 2033. No injuries. OSHA-recordable property damage only.",
    "event", "ground_truth", "Nargiz Mammadova", 1.0, "SRC-C05-1", "incident_report",
    1045, 0, 1, 1, ["C05", "primary_source"])
memories.append(c05_inc1)

c05_inc2 = M("C05", "Port of Baku", "had_incident", "chemical spill at berth 7",
    "Small chemical spill at Port of Baku berth 7 on June 3, 2033. 20 liters of cleaning solvent. Contained within 30 minutes. OSHA-recordable.",
    "event", "ground_truth", "Nargiz Mammadova", 1.0, "SRC-C05-2", "incident_report",
    1098, 0, 1, 1, ["C05", "primary_source"])
memories.append(c05_inc2)

c05_osha1 = M("C05", "OSHA report", "recorded", "forklift incident at Port of Baku",
    "OSHA report #2033-BK-0412 recorded the forklift collision at Port of Baku warehouse 3.",
    "fact", "repeated_claim", "Fatima Guliyeva", 1.0, "SRC-C05-3", "osha_report",
    1045, 1, 3, 1, ["C05", "repeated"],
    derived=[c05_inc1["memory_id"]])
memories.append(c05_osha1)

c05_pr = M("C05", "Port of Baku PR", "announced", "safety improvement program",
    "Port of Baku PR team announced a comprehensive safety improvement program, citing recent incidents as motivation for enhanced protocols.",
    "event", "inflated_claim", "Nargiz Mammadova", 0.8, "SRC-C05-4", "press_release",
    1100, 2, 5, 2, ["C05", "repeated"],
    derived=[c05_inc1["memory_id"], c05_inc2["memory_id"]])
memories.append(c05_pr)

# === C06: Sanctions Compliance Echo ===
c06_flag_orig = M("C06", "MV Caspian Dawn", "was_flagged_in", "sanctions screening",
    "MV Caspian Dawn was flagged in routine sanctions screening due to false-positive name match with sanctioned entity 'Caspian Dawn Trading LLC.'",
    "event", "ground_truth", "Fatima Guliyeva", 0.9, "SRC-C06-1", "compliance_screening",
    700, 0, 1, 1, ["C06", "primary_source"])
memories.append(c06_flag_orig)

c06_cleared = M("C06", "MV Caspian Dawn", "was_cleared", "sanctions screening false positive",
    "MV Caspian Dawn sanctions flag was cleared within 24 hours. Compliance review confirmed the vessel has no connection to 'Caspian Dawn Trading LLC.'",
    "event", "corrected", "Fatima Guliyeva", 1.0, "SRC-C06-2", "clearance_report",
    701, 0, 1, 1, ["C06", "primary_source", "correction"],
    supersedes=[c06_flag_orig["memory_id"]])
memories.append(c06_cleared)

c06_ins = M("C06", "insurance compliance database", "flagged", "MV Caspian Dawn sanctions concern",
    "Insurance compliance database flagged MV Caspian Dawn for potential sanctions concern.",
    "event", "repeated_claim", "Dmitri Volkov", 0.8, "SRC-C06-3", "compliance_database",
    700, 0, 2, 1, ["C06", "repeated"],
    derived=[c06_flag_orig["memory_id"]])
memories.append(c06_ins)

c06_bank1 = M("C06", "First Caspian Bank", "flagged", "MV Caspian Dawn in sanctions screening",
    "First Caspian Bank flagged MV Caspian Dawn in its trade finance sanctions screening system.",
    "event", "repeated_claim", "system", 0.75, "SRC-C06-4", "bank_compliance",
    700, 0, 2, 1, ["C06", "repeated"],
    derived=[c06_flag_orig["memory_id"]])
memories.append(c06_bank1)

c06_trade = M("C06", "trade compliance service", "listed", "MV Caspian Dawn as sanctions concern",
    "International trade compliance service listed MV Caspian Dawn as having a sanctions concern flag.",
    "event", "repeated_claim", "system", 0.7, "SRC-C06-5", "compliance_service",
    700, 1, 3, 2, ["C06", "repeated"],
    derived=[c06_flag_orig["memory_id"]])
memories.append(c06_trade)

# === C07: Salvage Value Estimate ===
c07_surv1 = M("C07", "surveyor 1", "assessed_damage_at", "$180,000",
    "Marine surveyor #1 assessed MV Atropatene grounding damage at $180,000, covering hull plate replacement and drydock costs.",
    "observation", "ground_truth", "Viktor Kovalenko", 0.95, "SRC-C07-1", "survey_report",
    800, 1, 3, 1, ["C07", "primary_source"])
memories.append(c07_surv1)

c07_surv2 = M("C07", "surveyor 2", "assessed_damage_at", "$195,000",
    "Marine surveyor #2 assessed MV Atropatene grounding damage at $195,000.",
    "observation", "ground_truth", "Viktor Kovalenko", 0.95, "SRC-C07-2", "survey_report",
    800, 1, 3, 1, ["C07", "primary_source"])
memories.append(c07_surv2)

c07_surv3 = M("C07", "surveyor 3", "assessed_damage_at", "$210,000",
    "Marine surveyor #3 assessed MV Atropatene grounding damage at $210,000.",
    "observation", "ground_truth", "Viktor Kovalenko", 0.95, "SRC-C07-3", "survey_report",
    800, 1, 3, 1, ["C07", "primary_source"])
memories.append(c07_surv3)

c07_typo = M("C07", "broker newsletter", "reported_damage_at", "$2.1 million (decimal point error)",
    "Maritime broker newsletter reported MV Atropatene grounding damage at $2.1 million. This was a decimal point error — the actual highest estimate was $210,000.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-4", "broker_newsletter",
    800, 5, 8, 2, ["C07", "repeated"],
    contradicts=[c07_surv3["memory_id"]])
memories.append(c07_typo)

c07_trade1 = M("C07", "trade publication 1", "cited", "$2.1M damage for MV Atropatene",
    "Caspian Shipping Weekly cited $2.1 million in grounding damage for MV Atropatene, referencing the broker newsletter.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-5", "trade_publication",
    800, 8, 12, 3, ["C07", "repeated"],
    derived=[c07_typo["memory_id"]],
    contradicts=[c07_surv3["memory_id"]])
memories.append(c07_trade1)

c07_trade2 = M("C07", "trade publication 2", "reported", "$2.1M damage estimate for MV Atropatene grounding",
    "Marine Insurance Digest reported a $2.1 million damage estimate for the MV Atropatene grounding incident.",
    "observation", "inflated_claim", "system", 0.5, "SRC-C07-6", "trade_publication",
    800, 10, 15, 3, ["C07", "repeated"],
    derived=[c07_typo["memory_id"]],
    contradicts=[c07_surv1["memory_id"]])
memories.append(c07_trade2)

# === QUERIES ===
queries.append(Q(
    "What is the actual condition of MV Atropatene's hull?",
    "source_quality",
    ["Minor paint degradation found in routine inspection",
     "Classification society rated it 'satisfactory with observations'"],
    ["The hull has cosmetic issues only, no structural problems"],
    ["Structural concerns exist", "The hull is failing",
     "Multiple sources confirm structural problems"],
    [c01_orig["memory_id"]],
    [c01_broker["memory_id"], c01_trade["memory_id"]],
    "hard",
    notes="Must distinguish primary inspection report from derivative/inflated reports"
))

queries.append(Q(
    "How much cargo was on MV Turkmenbashi voyage TK-2031-08?",
    "deduplication",
    ["B/L states 4,850 tonnes; draft survey measured 4,705 tonnes",
     "There is a 3% discrepancy between the two measurements"],
    ["The actual weight is likely closer to the draft survey measurement"],
    ["8 independent sources confirm 4,850 tonnes",
     "Multiple measurements agree on the weight"],
    [c02_bl["memory_id"], c02_draft["memory_id"]],
    [c02_customs["memory_id"], c02_insurance["memory_id"], c02_port["memory_id"]],
    "hard",
    conflict=True,
    notes="Must recognize 8 documents derive from 2 original measurements"
))

queries.append(Q(
    "Does MV Khazar Star's fuel meet sulfur specifications?",
    "correction_handling",
    ["The retest showed sulfur at 0.49%, within the 0.50% limit",
     "The initial 0.52% result was likely a testing error"],
    ["Current evidence indicates the fuel is within spec"],
    ["The fuel is definitively out of spec",
     "5 sources confirm non-compliance", "The vessel violated fuel standards"],
    [c03_retest["memory_id"]],
    [c03_test1["memory_id"], c03_eng["memory_id"], c03_flag["memory_id"],
     c03_port_state["memory_id"], c03_insure["memory_id"]],
    "hard",
    notes="5 sources repeat the initial fail vs 2 with the corrected pass — must weight retest over repetition"
))

queries.append(Q(
    "How many weather delay incidents occurred at Astara in December 2031?",
    "deduplication",
    ["One storm caused a single 72-hour delay event",
     "Multiple vessels and authorities reported the same event"],
    ["15+ reports all describe one weather incident"],
    ["15 separate weather incidents occurred",
     "Multiple storms hit Astara", "4 different delay events"],
    [c04_storm["memory_id"]],
    [c04_v1["memory_id"], c04_v2["memory_id"], c04_cg["memory_id"], c04_cme["memory_id"]],
    "medium",
    notes="Must recognize all reports derive from one storm"
))

queries.append(Q(
    "How many safety incidents occurred at Port of Baku in 2033?",
    "confidence_calibration",
    ["Two incidents: a forklift collision and a chemical spill",
     "Both were minor, OSHA-recordable events"],
    ["Only 2 actual incidents despite multiple records and PR mentions"],
    ["8 incidents occurred", "11 safety events were recorded",
     "Numerous safety problems plagued the port"],
    [c05_inc1["memory_id"], c05_inc2["memory_id"]],
    [c05_osha1["memory_id"], c05_pr["memory_id"]],
    "medium",
    notes="Must count actual incidents, not document copies"
))

queries.append(Q(
    "Is MV Caspian Dawn currently under sanctions?",
    "status_tracking",
    ["No — the sanctions flag was a false positive, cleared within 24 hours",
     "The vessel has no connection to sanctioned entities"],
    ["The flag was resolved; MV Caspian Dawn is not sanctioned"],
    ["The vessel is under sanctions", "Multiple databases confirm sanctions concern",
     "The sanctions status is unresolved"],
    [c06_cleared["memory_id"]],
    [c06_flag_orig["memory_id"], c06_ins["memory_id"], c06_bank1["memory_id"], c06_trade["memory_id"]],
    "hard",
    notes="Must recognize clearance supersedes flags, regardless of 7-to-4 source ratio"
))

queries.append(Q(
    "What was the damage estimate for the MV Atropatene grounding?",
    "source_quality",
    ["Three independent surveyors assessed damage at $180K, $195K, and $210K",
     "Average estimate is approximately $195,000"],
    ["Damage was in the $180K-$210K range based on professional surveys"],
    ["Damage was $2.1 million", "Multiple sources confirm $2.1M",
     "The damage exceeded $1 million"],
    [c07_surv1["memory_id"], c07_surv2["memory_id"], c07_surv3["memory_id"]],
    [c07_typo["memory_id"], c07_trade1["memory_id"], c07_trade2["memory_id"]],
    "hard",
    notes="Must weight 3 surveyor reports over 7 copies of a typo"
))

queries.append(Q(
    "What sources report on MV Atropatene's hull condition?",
    "provenance_tracking",
    ["The primary source is the classification society inspection",
     "Derivative reports include port state, insurance, broker, and trade publications",
     "The trade publication inflated 'paint degradation' to 'structural concerns'"],
    ["All derivative reports trace back to one inspection"],
    ["Multiple independent inspections found structural problems",
     "6 independent sources confirm hull issues"],
    [c01_orig["memory_id"], c01_port["memory_id"], c01_insure["memory_id"],
     c01_broker["memory_id"], c01_trade["memory_id"]],
    [],
    "hard",
    notes="Must trace provenance chain from original to derivatives"
))

queries.append(Q(
    "Was the MV Khazar Star fuel issue resolved?",
    "correction_handling",
    ["Yes — retest showed 0.49% sulfur, within the 0.50% limit",
     "The initial 0.52% result was likely a testing error"],
    ["The fuel issue was resolved by retest"],
    ["The issue remains unresolved", "The vessel is still non-compliant",
     "5 agencies confirm the violation"],
    [c03_retest["memory_id"], c03_eng_cleared["memory_id"]],
    [c03_flag["memory_id"], c03_port_state["memory_id"], c03_insure["memory_id"]],
    "medium"
))

queries.append(Q(
    "How many sources report the $2.1M damage figure for MV Atropatene?",
    "provenance_tracking",
    ["7 sources cite $2.1M but all derive from one broker newsletter typo",
     "The original surveyor reports show $180K-$210K"],
    ["The $2.1M figure is a decimal point error propagated through derivative sources"],
    ["7 independent estimates confirm $2.1M",
     "The $2.1M figure is well-established"],
    [c07_typo["memory_id"], c07_trade1["memory_id"], c07_trade2["memory_id"],
     c07_surv1["memory_id"], c07_surv2["memory_id"], c07_surv3["memory_id"]],
    [],
    "hard",
    notes="Key test: source count vs source quality"
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
        "path": fname, "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest()
    })

manifest = {
    "experiment": "exp19",
    "title": "Repeated Exposure / Confidence Inflation",
    "description": "Tests whether memory systems inflate confidence from repeated exposure when multiple sources trace to a single origin.",
    "files": files_info,
    "generated": datetime.now(UTC).isoformat()
}
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Generated {len(memories)} memories, {len(queries)} queries")
print(f"Output: {OUT}/")
