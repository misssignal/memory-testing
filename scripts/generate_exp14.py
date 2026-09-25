#!/usr/bin/env python3
"""Generate Experiment 14: Semantic Near-Miss / Distractor Resistance.

Story: Twin Bridges Racing — competitive sailing team with two nearly identical
yachts (Albatross and Petrel) competing in 2032 and 2036 Pacific Cup campaigns.

Tests whether semantic/embedding similarity dominates over factual relevance.
Seven cases: wrong entity, wrong time, near-identical events, template reuse,
different terminology, name collision, and misleading embedding proximity.

Produces: ~250 memories, ~100 queries, truth_state.json, and supporting files.
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── Globals ──────────────────────────────────────────────────────────────

EXP = "exp14_semantic_near_miss_distractor_resistance"
STORY = "twin_bridges_racing"
NEXT_ID = [1]
NEXT_QID = [1]


def mid():
    r = f"M{NEXT_ID[0]:04d}"
    NEXT_ID[0] += 1
    return r


def qid():
    r = f"Q{NEXT_QID[0]:03d}"
    NEXT_QID[0] += 1
    return r


def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def mem(event_time, obs_delay_h, auth_delay_h, ing_delay_h,
        subject, predicate, obj, text, memory_type, truth_role,
        source_id, source_type, tags, belief_holder="system",
        confidence=1.0, derived_from=None, supersedes=None,
        contradicts=None, duplicates=None, scope="team"):
    et = event_time
    ot = et + timedelta(hours=obs_delay_h)
    at = ot + timedelta(hours=auth_delay_h)
    it = at + timedelta(hours=ing_delay_h)
    return {
        "memory_id": mid(),
        "experiment": EXP,
        "story_id": STORY,
        "event_time": ts(et),
        "observation_time": ts(ot),
        "authored_time": ts(at),
        "ingestion_time": ts(it),
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "text": text,
        "memory_type": memory_type,
        "truth_role": truth_role,
        "belief_holder": belief_holder,
        "confidence": confidence,
        "source_id": source_id,
        "source_type": source_type,
        "derived_from": derived_from or [],
        "supersedes": supersedes or [],
        "contradicts": contradicts or [],
        "duplicates": duplicates or [],
        "aliases": [],
        "scope": scope,
        "tags": tags,
    }


# ── Case generators ─────────────────────────────────────────────────────

def gen_c01_wrong_entity():
    """Wrong entity, right description — Albatross vs Petrel confusion."""
    ms = []

    # Albatross 2032 Pacific Cup performance
    ms.append(mem(
        datetime(2032, 7, 10, 8, 0), 1, 2, 12,
        "Albatross", "started", "2032 Pacific Cup, San Francisco",
        "Albatross (TB-001) crossed the start line at 08:14 PDT in the 2032 Pacific Cup, San Francisco to Kauai. Starting conditions: 12 knots WNW, moderate swell. Good start, positioned to windward of fleet.",
        "race_log", "ground_truth", "P02", "race_record",
        ["C01", "wrong_entity", "Albatross", "2032_Pacific_Cup"]
    ))
    ms.append(mem(
        datetime(2032, 7, 12, 14, 0), 0.5, 1, 12,
        "Albatross", "reached", "Mile 400 in 2032 Pacific Cup",
        "Albatross passed Mile 400 at 14:12 PDT, Day 3. Speed averaging 9.2 knots. Leading Class B by 45 minutes corrected time. Weather: steady NE trades 18-22 knots.",
        "race_log", "ground_truth", "P09", "navigation_log",
        ["C01", "wrong_entity", "Albatross", "2032_Pacific_Cup"]
    ))
    ms.append(mem(
        datetime(2032, 7, 16, 6, 0), 0.5, 1, 12,
        "Albatross", "finished", "3rd overall, 1st in class, 2032 Pacific Cup",
        "Albatross finished the 2032 Pacific Cup in 6 days, 4 hours, 22 minutes. 3rd overall, 1st in Class B. Elapsed time corrected: 5d 18h 41m. Strong upwind performance compensated for lighter air reaching legs.",
        "race_log", "ground_truth", "P02", "race_record",
        ["C01", "wrong_entity", "Albatross", "2032_Pacific_Cup"]
    ))

    # Petrel 2032 Pacific Cup — retirement
    ms.append(mem(
        datetime(2032, 7, 10, 8, 0), 1, 2, 12,
        "Petrel", "started", "2032 Pacific Cup, San Francisco",
        "Petrel (TB-002) crossed the start line at 08:16 PDT in the 2032 Pacific Cup, San Francisco to Kauai. Starting conditions: 12 knots WNW, moderate swell. Clean start but slightly to leeward of Albatross.",
        "race_log", "ground_truth", "P04", "race_record",
        ["C01", "wrong_entity", "Petrel", "2032_Pacific_Cup"]
    ))
    ms.append(mem(
        datetime(2032, 7, 13, 22, 30), 0.5, 1, 12,
        "Petrel", "reported", "keel hydraulic warning at Mile 847",
        "Petrel reported keel hydraulic system warning alarm at Mile 847 during the 2032 Pacific Cup. Hydraulic pressure dropping intermittently. Skipper Hartley reduced sail area as precaution. Conditions: 25 knots, 3m seas.",
        "race_log", "ground_truth", "P04", "race_record",
        ["C01", "wrong_entity", "Petrel", "2032_Pacific_Cup", "keel_failure"]
    ))
    ms.append(mem(
        datetime(2032, 7, 14, 3, 0), 0.5, 2, 12,
        "Petrel", "retired", "from 2032 Pacific Cup at Mile 891",
        "Petrel retired from the 2032 Pacific Cup at Mile 891 after keel hydraulic failure. Keel locked at 8° cant angle. Unable to maintain course control in heavy conditions. Hartley diverted to Hilo under reduced sail. All crew safe.",
        "race_log", "ground_truth", "P04", "race_record",
        ["C01", "wrong_entity", "Petrel", "2032_Pacific_Cup", "keel_failure", "retirement"]
    ))

    # 2036 Pacific Cup — both boats finish
    ms.append(mem(
        datetime(2036, 7, 12, 8, 0), 1, 2, 12,
        "Albatross", "finished", "2nd overall, 1st in class, 2036 Pacific Cup",
        "Albatross finished the 2036 Pacific Cup in 5 days, 22 hours, 15 minutes. 2nd overall, 1st in Class B. New class record. Nikora's aggressive routing through the Pacific High paid off.",
        "race_log", "ground_truth", "P02", "race_record",
        ["C01", "wrong_entity", "Albatross", "2036_Pacific_Cup"]
    ))
    ms.append(mem(
        datetime(2036, 7, 13, 14, 0), 1, 2, 12,
        "Petrel", "finished", "5th overall, 2nd in class, 2036 Pacific Cup",
        "Petrel finished the 2036 Pacific Cup in 6 days, 8 hours, 44 minutes. 5th overall, 2nd in Class B. Solid performance after keel system overhaul. O'Brien-Sato's trimming in light air was exceptional.",
        "race_log", "ground_truth", "P04", "race_record",
        ["C01", "wrong_entity", "Petrel", "2036_Pacific_Cup"]
    ))

    return ms


def gen_c02_wrong_time():
    """Wrong time, right entity — 2032 vs 2036 campaign confusion."""
    ms = []

    # Auckland-Fiji 2032
    ms.append(mem(
        datetime(2032, 3, 5, 6, 0), 1, 2, 12,
        "Auckland-Fiji race 2032", "conditions", "25-knot NE trade winds",
        "Auckland-Fiji qualifying race 2032: NE trade winds averaging 25 knots with gusts to 32. Sea state: 2.5-3m swell from the NE. Fleet of 34 boats started. Albatross finished 4th, Petrel 7th.",
        "race_log", "ground_truth", "P09", "weather_log",
        ["C02", "wrong_time", "Auckland_Fiji", "2032"]
    ))
    ms.append(mem(
        datetime(2032, 3, 5, 8, 0), 0.5, 1, 12,
        "Albatross", "performance_in", "Auckland-Fiji 2032",
        "Albatross performance in Auckland-Fiji 2032: excellent upwind through the Colville Channel, lost ground reaching in the trades. Avg speed 8.7 knots. Finished 4th overall in 3 days 14 hours.",
        "race_log", "ground_truth", "P02", "performance_report",
        ["C02", "wrong_time", "Auckland_Fiji", "2032", "Albatross"]
    ))
    ms.append(mem(
        datetime(2032, 3, 8, 16, 0), 1, 4, 12,
        "Albatross", "post_race_note", "Auckland-Fiji 2032",
        "Post-race debrief Auckland-Fiji 2032: Need to improve reaching performance in 20+ knot trade winds. Code Zero sail (SL-4410-A) was too light for conditions; consider heavier cloth for replacement.",
        "debrief", "ground_truth", "P02", "debrief_notes",
        ["C02", "wrong_time", "Auckland_Fiji", "2032", "Albatross"]
    ))

    # Auckland-Fiji 2036 — similar but distinct
    ms.append(mem(
        datetime(2036, 3, 7, 6, 0), 1, 2, 12,
        "Auckland-Fiji race 2036", "conditions", "22-knot NE trade winds",
        "Auckland-Fiji qualifying race 2036: NE trade winds averaging 22 knots with gusts to 28. Sea state: 2-2.5m swell from the NE. Fleet of 31 boats started. Albatross finished 2nd, Petrel 5th.",
        "race_log", "ground_truth", "P09", "weather_log",
        ["C02", "wrong_time", "Auckland_Fiji", "2036"]
    ))
    ms.append(mem(
        datetime(2036, 3, 7, 8, 0), 0.5, 1, 12,
        "Albatross", "performance_in", "Auckland-Fiji 2036",
        "Albatross performance in Auckland-Fiji 2036: dominant throughout. New heavier Code Zero sail (SL-4410-A v2) performed well in trade winds. Avg speed 9.1 knots. Finished 2nd overall in 3 days 8 hours.",
        "race_log", "ground_truth", "P02", "performance_report",
        ["C02", "wrong_time", "Auckland_Fiji", "2036", "Albatross"]
    ))
    ms.append(mem(
        datetime(2036, 3, 10, 16, 0), 1, 4, 12,
        "Albatross", "post_race_note", "Auckland-Fiji 2036",
        "Post-race debrief Auckland-Fiji 2036: Reaching performance much improved with new sail. Upwind edge slightly reduced — possible keel foil wear after 6 years. Schedule inspection before Pacific Cup.",
        "debrief", "ground_truth", "P02", "debrief_notes",
        ["C02", "wrong_time", "Auckland_Fiji", "2036", "Albatross"]
    ))

    # Sydney-Hobart feeder 2032
    ms.append(mem(
        datetime(2032, 6, 15, 10, 0), 1, 2, 12,
        "Sydney-Hobart feeder 2032", "conditions", "light and variable, 8-12 knots",
        "Sydney-Hobart feeder race 2032: light and variable conditions, 8-12 knots from the S-SE. Glassy patches in Bass Strait. Petrel excelled in light air, finishing 3rd. Albatross 9th — struggled in sub-10 knot conditions.",
        "race_log", "ground_truth", "P09", "weather_log",
        ["C02", "wrong_time", "Sydney_Hobart", "2032"]
    ))

    # Sydney-Hobart feeder 2036
    ms.append(mem(
        datetime(2036, 6, 18, 10, 0), 1, 2, 12,
        "Sydney-Hobart feeder 2036", "conditions", "moderate SW 15-20 knots",
        "Sydney-Hobart feeder race 2036: moderate SW winds 15-20 knots, building to 25 in Bass Strait. Both boats performed well. Albatross 4th, Petrel 6th. Petrel's new keel system performed flawlessly in the building seas.",
        "race_log", "ground_truth", "P09", "weather_log",
        ["C02", "wrong_time", "Sydney_Hobart", "2036"]
    ))

    return ms


def gen_c03_near_identical_events():
    """Near-identical events — two keel inspections with opposite outcomes."""
    ms = []

    # 2031 routine inspection — Petrel cleared
    ms.append(mem(
        datetime(2031, 9, 15, 8, 0), 2, 4, 12,
        "Petrel keel inspection", "routine_annual", "2031-09",
        "Annual keel inspection for Petrel (TB-002), September 2031. Keel structure: sound. Hydraulic ram actuator assembly (HR-2202): operating within spec. Hydraulic pressure test: 280 bar, holding. Minor surface corrosion on keel bulb fairing — cosmetic only. CLEARED FOR RACING.",
        "inspection_report", "ground_truth", "P05", "marine_survey",
        ["C03", "near_identical", "Petrel", "keel_inspection", "2031", "cleared"]
    ))
    ms.append(mem(
        datetime(2031, 9, 15, 14, 0), 1, 2, 12,
        "Petrel keel corrosion", "noted", "minor surface corrosion on bulb fairing",
        "Surveyor noted minor surface corrosion on Petrel's keel bulb fairing during annual inspection. Corrosion depth <0.2mm, well within tolerance. Recommended re-fairing before next season. Does not affect structural integrity or hydrodynamic performance.",
        "inspection_report", "ground_truth", "P05", "marine_survey",
        ["C03", "near_identical", "Petrel", "keel_inspection", "2031", "corrosion"]
    ))

    # 2031 routine inspection — Albatross
    ms.append(mem(
        datetime(2031, 9, 17, 8, 0), 2, 4, 12,
        "Albatross keel inspection", "routine_annual", "2031-09",
        "Annual keel inspection for Albatross (TB-001), September 2031. Keel structure: sound. Hydraulic ram actuator assembly (HR-2201): operating within spec. Hydraulic pressure test: 285 bar, holding. No corrosion noted. CLEARED FOR RACING.",
        "inspection_report", "ground_truth", "P05", "marine_survey",
        ["C03", "near_identical", "Albatross", "keel_inspection", "2031", "cleared"]
    ))

    # 2033 post-incident inspection — Petrel found FATIGUE CRACK
    ms.append(mem(
        datetime(2033, 11, 5, 8, 0), 4, 8, 24,
        "Petrel keel inspection", "post_incident", "2033-11",
        "Post-incident keel inspection for Petrel (TB-002), November 2033 — following 2032 Pacific Cup retirement. Keel structure: DEFECT FOUND. Hydraulic ram actuator assembly (HR-2202): fatigue crack discovered in mounting bracket at 47,000 load cycles. Crack length: 12mm. Hydraulic pressure test: failed at 195 bar (spec: 280 bar minimum). NOT CLEARED — REQUIRES REPAIR.",
        "inspection_report", "ground_truth", "P05", "marine_survey",
        ["C03", "near_identical", "Petrel", "keel_inspection", "2033", "fatigue_crack", "failed"]
    ))
    ms.append(mem(
        datetime(2033, 11, 5, 16, 0), 2, 4, 24,
        "Petrel keel fatigue crack", "analysis", "mounting bracket failure mode",
        "Engineering analysis of Petrel's keel hydraulic mount fatigue crack: initiated at stress riser on mounting bracket inner radius. Propagated over approximately 15,000 cycles. Root cause: insufficient fillet radius in original fabrication (0.5mm vs 2mm design spec). Albatross (HR-2201) has the same bracket design — recommend immediate inspection.",
        "engineering_report", "ground_truth", "P05", "engineering_analysis",
        ["C03", "near_identical", "Petrel", "keel_inspection", "2033", "fatigue_crack", "root_cause"]
    ))
    ms.append(mem(
        datetime(2033, 11, 8, 8, 0), 2, 4, 24,
        "Albatross keel inspection", "emergency", "2033-11",
        "Emergency keel inspection for Albatross (TB-001), November 2033 — triggered by Petrel fatigue crack finding. Hydraulic ram actuator assembly (HR-2201): NO CRACK FOUND. Bracket fillet radius measured at 1.8mm (vs Petrel's 0.5mm). Hydraulic pressure test: 282 bar, holding. CLEARED — but recommend bracket replacement at next haul-out as preventive measure.",
        "inspection_report", "ground_truth", "P05", "marine_survey",
        ["C03", "near_identical", "Albatross", "keel_inspection", "2033", "cleared"]
    ))

    return ms


def gen_c04_template_language():
    """Reused template phrases — sail inventory logs."""
    ms = []

    inventories = [
        (datetime(2031, 11, 1, 9, 0), "2031 pre-season", 14, 2, 1,
         "Pre-season sail inventory for 2032 campaign. All racing sails inspected and catalogued. UV damage on #1 jib (SL-4402-A) — recommend replacement before Auckland-Fiji."),
        (datetime(2032, 6, 25, 9, 0), "2032 pre-Pacific Cup", 16, 4, 2,
         "Pre-Pacific Cup sail inventory. Four sails requiring repair: 2 spinnakers with batten pocket wear, 1 jib with leech cord failure, 1 mainsail with minor delamination near head. Two sails recommended for replacement: Code Zero (SL-4410-A) too light for expected conditions, storm jib past fatigue life."),
        (datetime(2033, 10, 15, 9, 0), "2033 post-season", 18, 3, 0,
         "Post-season sail inventory. Three sails requiring repair: UV damage, chafe, and one torn spinnaker from training incident. No replacements needed — all sails within acceptable fatigue life."),
        (datetime(2035, 11, 1, 9, 0), "2035 pre-season", 20, 5, 3,
         "Pre-season sail inventory for 2036 campaign. Five sails requiring repair, three recommended for replacement including both primary jibs (showing adhesive failure at tack) and the heavy-air spinnaker (delaminated panels)."),
        (datetime(2036, 6, 28, 9, 0), "2036 pre-Pacific Cup", 22, 2, 1,
         "Pre-Pacific Cup sail inventory. Fleet in excellent condition after winter repairs. Two sails needing minor repair (chafe patches). One recommendation: replace backup Code Zero as precaution — showing early signs of adhesive degradation."),
    ]

    for dt, label, total, repair, replace, detail in inventories:
        ms.append(mem(
            dt, 2, 4, 12,
            f"Sail inventory {label}", "completed",
            f"{total} inspected, {repair} repair, {replace} replace",
            f"Sail inventory check completed. {total} sails inspected, {repair} requiring repair, {replace} recommended for replacement. {detail}",
            "maintenance_log", "ground_truth", "P06", "sail_inventory",
            ["C04", "template_language", "sail_inventory", label.replace(" ", "_")]
        ))

    # Also add near-identical maintenance log entries for rigging
    rigging_checks = [
        (datetime(2031, 11, 5, 9, 0), "2031", "Albatross",
         "All standing rigging within spec. Forestay tension: 4,200 kg. Running backstay blocks: smooth operation. Vang hydraulic: operating at 190 bar."),
        (datetime(2031, 11, 7, 9, 0), "2031", "Petrel",
         "All standing rigging within spec. Forestay tension: 4,150 kg. Running backstay blocks: smooth operation. Vang hydraulic: operating at 185 bar."),
        (datetime(2035, 11, 10, 9, 0), "2035", "Albatross",
         "All standing rigging within spec. Forestay tension: 4,100 kg (slight decrease — recommend re-tension). Running backstay blocks: minor wear on port block. Vang hydraulic: operating at 188 bar."),
        (datetime(2035, 11, 12, 9, 0), "2035", "Petrel",
         "All standing rigging within spec. Forestay tension: 4,180 kg. Running backstay blocks: smooth operation. Vang hydraulic: operating at 192 bar. New hydraulic ram performing well."),
    ]

    for dt, year, boat, detail in rigging_checks:
        ms.append(mem(
            dt, 2, 4, 12,
            f"{boat} rigging check {year}", "completed",
            f"rigging within spec",
            f"Standing rigging inspection completed for {boat} ({year}). {detail}",
            "maintenance_log", "ground_truth", "P05", "rigging_inspection",
            ["C04", "template_language", "rigging_check", boat, year]
        ))

    return ms


def gen_c05_terminology():
    """Correct answer uses different terminology — hydraulic ram system."""
    ms = []

    # Engineering documentation uses formal name
    ms.append(mem(
        datetime(2030, 8, 15, 9, 0), 4, 8, 24,
        "HRAA design spec", "specifies", "hydraulic ram actuator assembly for canting keel",
        "Design specification for hydraulic ram actuator assembly (HRAA), Twin Bridges Mark IV/IV-B canting keel system. Operating pressure: 280 bar. Stroke: 450mm. Cant range: ±40°. Assembly includes: hydraulic cylinder, mounting bracket, pivot pin, pressure accumulator, and control valve. Part numbers: HR-2201 (Albatross), HR-2202 (Petrel).",
        "engineering_spec", "ground_truth", "P05", "design_document",
        ["C05", "terminology", "HRAA", "formal"]
    ))
    ms.append(mem(
        datetime(2031, 3, 10, 9, 0), 2, 4, 12,
        "HRAA maintenance manual", "prescribes", "monthly hydraulic fluid analysis",
        "HRAA Maintenance Manual Rev 3.2: Monthly hydraulic fluid analysis required. Check for metal particles indicating wear. Replace fluid every 500 operating hours. Hydraulic ram actuator assembly must be fully depressurized before any bracket inspection.",
        "engineering_spec", "ground_truth", "P05", "maintenance_manual",
        ["C05", "terminology", "HRAA", "formal"]
    ))

    # Race reports use informal names
    ms.append(mem(
        datetime(2032, 7, 13, 23, 0), 0.5, 1, 12,
        "Petrel keel mechanism", "alarming", "pressure dropping",
        "Hartley to shore team: 'The keel mechanism is playing up. Pressure gauge dropping. The keel jack won't hold angle in these seas. Going to try manual override.'",
        "radio_log", "ground_truth", "P04", "race_communication",
        ["C05", "terminology", "keel_mechanism", "informal", "Petrel"]
    ))
    ms.append(mem(
        datetime(2032, 7, 14, 1, 0), 0.5, 1, 12,
        "Petrel", "reported", "the ram is gone, keel locked at 8 degrees",
        "Hartley radio transmission 01:12 UTC: 'The ram is gone. Keel locked at 8 degrees. We've lost the ability to control cant angle. Keel pivot system is seized. Making for Hilo.'",
        "radio_log", "ground_truth", "P04", "race_communication",
        ["C05", "terminology", "keel_ram", "informal", "Petrel", "failure"]
    ))

    # Crew logs use colloquial terms
    ms.append(mem(
        datetime(2032, 7, 14, 10, 0), 2, 8, 24,
        "O'Brien-Sato", "logged", "keel jack failure during Pacific Cup",
        "Personal log, Liam O'Brien-Sato: 'The keel jack started making grinding noises around mile 800. Hartley noticed the pressure dropping first. By mile 847 it was clear the keel pivot system was failing. We tried everything — manual override, bleeding the lines, even hitting the ram housing with a wrench. Nothing worked. Had to retire.'",
        "crew_log", "ground_truth", "P08", "personal_log",
        ["C05", "terminology", "keel_jack", "informal", "Petrel", "failure"]
    ))

    # Post-incident report uses both
    ms.append(mem(
        datetime(2032, 8, 5, 9, 0), 4, 12, 24,
        "Petrel incident report", "concluded", "HRAA failure due to fatigue",
        "Incident Report IR-2032-003: Petrel hydraulic ram actuator assembly (HRAA, part HR-2202) failure during 2032 Pacific Cup. Crew reported 'keel mechanism' and 'ram' failure. Post-race inspection confirmed hydraulic cylinder seal failure leading to pressure loss. Root cause: deferred to detailed inspection (see 2033-11 survey).",
        "incident_report", "ground_truth", "P01", "incident_report",
        ["C05", "terminology", "HRAA", "keel_mechanism", "formal_and_informal"]
    ))

    return ms


def gen_c06_name_collision():
    """Name collision — Liam O'Brien vs Liam O'Brien-Sato."""
    ms = []

    # Liam O'Brien (P07) — Albatross sail trimmer
    ms.append(mem(
        datetime(2031, 2, 1, 9, 0), 1, 2, 12,
        "Liam O'Brien", "joined", "Twin Bridges Racing as sail trimmer, Albatross",
        "Liam O'Brien (P07) joined Twin Bridges Racing as sail trimmer for Albatross. Previous experience: 3x Auckland-Tauranga winner. Specialty: heavy-air trimming. Assigned to Albatross (TB-001).",
        "personnel", "ground_truth", "P01", "personnel_record",
        ["C06", "name_collision", "OBrien", "Albatross", "P07"]
    ))
    ms.append(mem(
        datetime(2032, 3, 6, 14, 0), 1, 2, 12,
        "Liam", "trimmed", "spinnaker for record run in Auckland-Fiji 2032",
        "Liam trimmed the A2 spinnaker to perfection during the final night of Auckland-Fiji 2032. Albatross recorded a 12-hour run of 228 nm — a new personal best for the boat. Nikora credited 'Liam's feel for the sail' in the post-race debrief.",
        "race_log", "ground_truth", "P02", "crew_report",
        ["C06", "name_collision", "Liam", "Albatross", "ambiguous"]
    ))

    # Liam O'Brien-Sato (P08) — Petrel sail trimmer
    ms.append(mem(
        datetime(2031, 3, 1, 9, 0), 1, 2, 12,
        "Liam O'Brien-Sato", "joined", "Twin Bridges Racing as sail trimmer, Petrel",
        "Liam O'Brien-Sato (P08) joined Twin Bridges Racing as sail trimmer for Petrel. Previous experience: Olympic 49er campaign (2028). Specialty: light-air trimming. Assigned to Petrel (TB-002). No relation to Liam O'Brien on Albatross.",
        "personnel", "ground_truth", "P01", "personnel_record",
        ["C06", "name_collision", "OBrien-Sato", "Petrel", "P08"]
    ))
    ms.append(mem(
        datetime(2032, 6, 16, 18, 0), 1, 2, 12,
        "Liam", "excelled", "in light-air trimming during Sydney-Hobart feeder 2032",
        "Liam's light-air trimming was the difference in the Sydney-Hobart feeder. Petrel gained 2 miles on the fleet during the Bass Strait calm. 'Liam kept the boat moving when nobody else could' — Hartley in post-race interview.",
        "race_log", "ground_truth", "P04", "crew_report",
        ["C06", "name_collision", "Liam", "Petrel", "ambiguous"]
    ))

    # 2035 transfer
    ms.append(mem(
        datetime(2035, 1, 15, 9, 0), 1, 4, 12,
        "Liam O'Brien", "transferred_to", "shore team coordinator role",
        "Liam O'Brien (P07) transferred from Albatross sailing crew to shore team coordinator effective January 2035. Shoulder injury from 2034 training prevented continued on-water racing. Replaced on Albatross by Marcus Yip.",
        "personnel", "ground_truth", "P01", "personnel_record",
        ["C06", "name_collision", "OBrien", "transfer", "2035"]
    ))
    ms.append(mem(
        datetime(2036, 7, 13, 14, 0), 1, 2, 12,
        "O'Brien-Sato", "praised", "for exceptional light-air trimming in 2036 Pacific Cup",
        "Liam O'Brien-Sato's trimming in the light-air zone north of the Pacific High was exceptional. Petrel gained 15 miles on corrected time during the 18-hour drifting match. Post-race consensus: O'Brien-Sato's Olympic dinghy experience was the deciding factor.",
        "race_log", "ground_truth", "P04", "crew_report",
        ["C06", "name_collision", "OBrien-Sato", "Petrel", "2036_Pacific_Cup"]
    ))

    # Ambiguous "O'Brien" references
    ms.append(mem(
        datetime(2032, 4, 10, 14, 0), 1, 2, 12,
        "O'Brien", "involved_in", "sail development meeting",
        "O'Brien attended the sail development meeting with Sørensen. Discussion focused on Code Zero design for Pacific Cup. O'Brien advocated for a fuller entry angle based on experience in strong trades.",
        "meeting_notes", "ground_truth", "P06", "meeting_record",
        ["C06", "name_collision", "OBrien", "ambiguous", "sail_development"],
        belief_holder="P06"
    ))

    return ms


def gen_c07_misleading_embedding():
    """Misleading embedding proximity — depression/strengthen polysemy."""
    ms = []

    # Weather: tropical depression
    ms.append(mem(
        datetime(2032, 7, 11, 6, 0), 0.5, 1, 12,
        "Tropical depression TD-07", "approaching", "from southwest during 2032 Pacific Cup",
        "Weather briefing Day 2: Tropical depression TD-07 approaching from the southwest, currently at 18°N 148°W. Expected to strengthen to tropical storm within 48 hours. Course track suggests it will pass 200nm south of the fleet. Recommend maintaining northerly course to avoid outer bands.",
        "weather_briefing", "ground_truth", "P09", "weather_report",
        ["C07", "misleading_embedding", "weather", "tropical_depression"]
    ))
    ms.append(mem(
        datetime(2032, 7, 12, 6, 0), 0.5, 1, 12,
        "Tropical depression TD-07", "strengthened_to", "Tropical Storm Kilo",
        "Weather update Day 3: TD-07 has strengthened to Tropical Storm Kilo, sustained winds 45 knots. Track shifting slightly north — now expected to pass 150nm south of fleet center. Outer rain bands may affect southern boats. Albatross and Petrel both north of likely impact zone.",
        "weather_briefing", "ground_truth", "P09", "weather_report",
        ["C07", "misleading_embedding", "weather", "tropical_storm"]
    ))

    # Morale: team depression after retirement
    ms.append(mem(
        datetime(2032, 8, 1, 14, 0), 2, 4, 12,
        "Team morale", "experienced", "depression after Petrel's retirement from Pacific Cup",
        "Team debrief following 2032 Pacific Cup: significant morale depression across both crews after Petrel's retirement. Hartley particularly affected. However, the setback strengthened the team's resolve for the 2036 campaign. Maitland initiated a formal review process that ultimately led to important keel system improvements.",
        "team_report", "ground_truth", "P10", "performance_report",
        ["C07", "misleading_embedding", "morale", "team_depression"]
    ))
    ms.append(mem(
        datetime(2032, 8, 15, 10, 0), 2, 4, 12,
        "Maitland", "addressed", "team depression in all-hands meeting",
        "Maitland held all-hands meeting to address post-race depression and chart path forward. Key message: 'Petrel's retirement was a setback but it has strengthened our engineering processes. The 2036 campaign will be stronger because of what we learned.' New engineering review protocols announced.",
        "meeting_notes", "ground_truth", "P01", "meeting_record",
        ["C07", "misleading_embedding", "morale", "depression_addressed"]
    ))

    # Weather: atmospheric pressure system (another "depression" context)
    ms.append(mem(
        datetime(2036, 7, 9, 6, 0), 0.5, 1, 12,
        "Low pressure system", "affecting", "start area for 2036 Pacific Cup",
        "Pre-race weather: atmospheric depression centered at 38°N 125°W producing overcast skies and 15-knot SW winds in San Francisco Bay. Expected to move NE and clear by race start. High pressure ridge building from the west will strengthen over the next 72 hours, providing NW gradient winds for the fleet.",
        "weather_briefing", "ground_truth", "P09", "weather_report",
        ["C07", "misleading_embedding", "weather", "atmospheric_depression", "2036"]
    ))

    return ms


def gen_background():
    """Background memories providing realistic noise."""
    ms = []

    bg_events = [
        (datetime(2030, 6, 1, 9, 0), "Twin Bridges Racing", "founded", "by James Maitland in Auckland",
         "Twin Bridges Racing established by James Maitland. Goal: competitive offshore racing in the Pacific Cup circuit. Initial funding from NZ Marine Foundation grant and private sponsors.",
         "administrative", "P01", "company_record", ["background", "founding"]),

        (datetime(2030, 9, 15, 9, 0), "Albatross", "launched", "at McMullen & Wing yard",
         "Albatross (TB-001) launched at McMullen & Wing boatyard, Auckland. Mark IV design by Mei-Lin Chen. Hull length 12.8m, beam 3.9m, draft 2.8m. Canting keel with 4,050 kg bulb.",
         "event", "P05", "boat_record", ["background", "Albatross", "launch"]),

        (datetime(2031, 1, 10, 9, 0), "Petrel", "launched", "at McMullen & Wing yard",
         "Petrel (TB-002) launched at McMullen & Wing boatyard. Mark IV-B design — 0.3m longer waterline than Albatross, heavier keel bulb (4,200 kg), modified sail plan with taller mast (+0.4m).",
         "event", "P05", "boat_record", ["background", "Petrel", "launch"]),

        (datetime(2031, 4, 15, 9, 0), "Crew training", "completed", "pre-season camp at Bay of Islands",
         "Two-week crew training camp at Bay of Islands. Both crews practiced maneuvers, heavy-weather sailing, and man-overboard recovery. Fitness testing by Dr. Vasquez showed all crew members meeting minimum VO2 max requirements.",
         "training", "P10", "training_record", ["background", "training"]),

        (datetime(2031, 6, 10, 9, 0), "Sponsor event", "held", "AkzoNobel Auckland reception",
         "AkzoNobel Auckland reception. Title sponsor renewed for 2032-2036 campaign. Maitland presented campaign plan. Media coverage: NZ Herald, Sailing Anarchy, Stuff.co.nz.",
         "event", "P01", "media_record", ["background", "sponsor"]),

        (datetime(2031, 8, 1, 9, 0), "Sail development", "progressed", "new asymmetric spinnaker design",
         "Sørensen completed design of new asymmetric spinnaker for downwind Pacific Cup legs. CFD analysis shows 3% improvement in VMG at TWA 140°. Prototype ordered from North Sails NZ.",
         "design", "P06", "design_record", ["background", "sail_development"]),

        (datetime(2031, 12, 15, 9, 0), "Haul-out", "completed", "both boats at Westhaven Marina",
         "Annual haul-out completed at Westhaven Marina. Antifouling applied, through-hulls serviced, rudder bearings checked. Both boats in excellent condition for 2032 season.",
         "maintenance", "P05", "maintenance_log", ["background", "haul_out"]),

        (datetime(2032, 2, 1, 9, 0), "Pacific Cup entry", "confirmed", "for both Albatross and Petrel",
         "Pacific Cup Committee confirmed entries for both Albatross (TB-001) and Petrel (TB-002) in Class B. Entry fees paid. Measurement certificates submitted and approved.",
         "administrative", "P01", "race_entry", ["background", "Pacific_Cup", "2032"]),

        (datetime(2032, 5, 1, 9, 0), "Container shipment", "arranged", "boats to San Francisco",
         "Logistics: both boats containerized and shipped from Auckland to San Francisco via Matson Navigation. Expected arrival May 28. Cradle design by Chen ensures keel protection during transit.",
         "logistics", "P01", "shipping_record", ["background", "logistics"]),

        (datetime(2032, 6, 1, 9, 0), "Boats arrived", "in", "San Francisco Bay",
         "Albatross and Petrel arrived at San Francisco Yacht Club after container transit from Auckland. Boats launched successfully, systems checks completed. Both boats ready for familiarization sailing.",
         "logistics", "P01", "shipping_record", ["background", "logistics", "arrival"]),

        (datetime(2032, 7, 8, 9, 0), "Pre-race briefing", "held", "at St. Francis Yacht Club",
         "Pre-race skipper's briefing at St. Francis Yacht Club. 94 boats entered. Weather outlook: moderate NW gradient winds at start, transitioning to NE trades south of Point Conception. ITCZ position uncertain.",
         "event", "P01", "race_record", ["background", "Pacific_Cup", "2032", "briefing"]),

        (datetime(2032, 8, 20, 9, 0), "Post-season review", "conducted", "2032 campaign debrief",
         "Comprehensive post-season review of 2032 campaign. Albatross: strong season, 3rd overall in Pacific Cup. Petrel: disappointing — keel failure in Pacific Cup overshadowed earlier results. Key action: independent keel system review.",
         "meeting_notes", "P01", "debrief_record", ["background", "review", "2032"]),

        (datetime(2033, 3, 1, 9, 0), "Design review", "initiated", "Mark IV-C concept study",
         "Mei-Lin Chen initiated concept study for Mark IV-C hull design. Focus: improved reaching performance while maintaining upwind edge. Timeline: 18-month design cycle for possible 2036 build.",
         "design", "P05", "design_record", ["background", "design", "Mark_IV-C"]),

        (datetime(2033, 6, 15, 9, 0), "Petrel refit", "began", "keel system complete overhaul",
         "Petrel keel system overhaul commenced at McMullen & Wing. Scope: replace hydraulic ram actuator assembly (HR-2202), new mounting brackets with improved fillet radius (2mm spec), new hydraulic lines and control valve. Budget: NZD 180,000.",
         "maintenance", "P05", "refit_record", ["background", "Petrel", "refit"]),

        (datetime(2034, 1, 15, 9, 0), "Petrel refit", "completed", "keel system fully rebuilt",
         "Petrel keel system refit completed. New HR-2202-R2 hydraulic ram installed with redesigned mounting brackets. Sea trials: pressure test 295 bar (spec 280), cant range full ±40°. System performing above specification.",
         "maintenance", "P05", "refit_record", ["background", "Petrel", "refit_complete"]),

        (datetime(2034, 6, 1, 9, 0), "Fitness camp", "held", "pre-season at Whangarei",
         "Pre-season fitness camp at Whangarei. Dr. Vasquez introduced new fatigue monitoring protocol using heart rate variability. Key finding: O'Brien showing signs of overtraining — recommended reduced on-water time.",
         "training", "P10", "fitness_record", ["background", "fitness", "2034"]),

        (datetime(2034, 9, 1, 9, 0), "O'Brien shoulder injury", "diagnosed", "rotator cuff tear",
         "Liam O'Brien (P07) diagnosed with partial rotator cuff tear in right shoulder. Occurred during heavy-air training sail. Dr. Vasquez: 'Not surgery-worthy but will limit grinding and trimming capacity.' O'Brien elected conservative treatment.",
         "medical", "P10", "medical_record", ["background", "OBrien", "injury"]),

        (datetime(2035, 2, 1, 9, 0), "Nikora", "moved_to", "Petrel as skipper for 2036 campaign",
         "Aroha Nikora moved from Albatross to Petrel as skipper for the 2036 Pacific Cup campaign, replacing Ben Hartley who stepped back to advisory role. Nikora will skip both boats in training — final assignment before Pacific Cup to be determined based on performance.",
         "personnel", "P01", "personnel_record", ["background", "Nikora", "Petrel"]),

        (datetime(2035, 6, 15, 9, 0), "Mark IV-C decision", "cancelled", "too risky for 2036",
         "Decision: Mark IV-C new-build cancelled for 2036 campaign. Timeline too tight, risk too high. Instead: focus on optimizing existing Albatross and Petrel. Chen to develop keel foil upgrade package for both boats.",
         "administrative", "P01", "design_record", ["background", "design", "cancelled"]),

        (datetime(2035, 10, 1, 9, 0), "Keel foil upgrade", "installed", "on both boats",
         "New keel foil profiles installed on both Albatross and Petrel. Computational analysis predicts 1.5% reduction in upwind drag. Sea trials confirmed improvement in pointing ability — 0.8° higher VMG angle in 15-knot conditions.",
         "maintenance", "P05", "upgrade_record", ["background", "keel_foil", "upgrade"]),

        (datetime(2036, 2, 1, 9, 0), "Pacific Cup 2036 entry", "confirmed", "for both boats",
         "2036 Pacific Cup entries confirmed for Albatross and Petrel. Both boats assigned to Class B. Campaign budget: NZD 2.4M. Primary sponsor AkzoNobel renewed through 2040.",
         "administrative", "P01", "race_entry", ["background", "Pacific_Cup", "2036"]),

        (datetime(2036, 5, 10, 9, 0), "Container shipment", "arranged", "boats to San Francisco 2036",
         "Logistics: both boats containerized and shipped to San Francisco via Matson Navigation. Same routing as 2032. Expected arrival June 1. Chen supervised loading with improved cradle design.",
         "logistics", "P01", "shipping_record", ["background", "logistics", "2036"]),

        (datetime(2036, 6, 5, 9, 0), "Boats arrived", "in", "San Francisco 2036",
         "Albatross and Petrel arrived at San Francisco Yacht Club. Boats launched and systems checked. Petrel's rebuilt keel system performing perfectly. Both crews began familiarization sailing in Bay conditions.",
         "logistics", "P01", "shipping_record", ["background", "logistics", "arrival_2036"]),

        (datetime(2036, 7, 7, 9, 0), "Pre-race briefing 2036", "held", "at St. Francis Yacht Club",
         "Pre-race skipper's briefing at St. Francis Yacht Club. 89 boats entered (fewer than 2032's 94). Weather outlook: SW winds at start clearing to NW, early transition to trades. ITCZ further north than 2032 — shorter course effectively.",
         "event", "P01", "race_record", ["background", "Pacific_Cup", "2036", "briefing"]),

        (datetime(2036, 8, 1, 9, 0), "Post-race celebration", "held", "in Kauai",
         "Post-race celebration at Kauai Yacht Club. Albatross crew received Class B trophy. Both boats completed the race — redemption for Petrel after 2032 retirement. Maitland: 'Four years of work paid off today.'",
         "event", "P01", "social_record", ["background", "celebration", "2036"]),

        (datetime(2031, 7, 5, 9, 0), "Wallace navigation", "system_upgraded", "new B&G Zeus chartplotter",
         "Ngaire Wallace oversaw installation of B&G Zeus³ Glass Helm chartplotters on both boats. Identical hardware and software versions to ensure consistency between Albatross and Petrel navigation systems.",
         "maintenance", "P09", "equipment_record", ["background", "navigation", "upgrade"]),

        (datetime(2032, 4, 1, 9, 0), "Sørensen sail plan", "finalized", "for 2032 Pacific Cup",
         "Riku Sørensen finalized sail plan for 2032 Pacific Cup. Albatross carrying 16 sails, Petrel carrying 16 sails. Key difference: Petrel's A2 spinnaker cut 5% fuller to exploit its longer waterline.",
         "design", "P06", "sail_plan", ["background", "sail_plan", "2032"]),

        (datetime(2033, 5, 1, 9, 0), "Vasquez performance", "analysis", "2032 campaign biometric data",
         "Dr. Vasquez published internal analysis of 2032 campaign biometric data. Key findings: crew fatigue peaked at Day 4 of Pacific Cup. Night watches showed 23% slower reaction times. Recommended: 4-hour watch rotation instead of 6-hour for 2036.",
         "research", "P10", "performance_analysis", ["background", "biometrics", "2032"]),

        (datetime(2034, 3, 15, 9, 0), "Hartley advisory", "role", "shifted to performance coaching",
         "Ben Hartley's role formalized as Performance Coach and Campaign Advisor. No longer sailing regularly due to back problems. Focuses on tactical planning, weather routing analysis, and mentoring younger sailors.",
         "personnel", "P01", "personnel_record", ["background", "Hartley", "advisory"]),

        (datetime(2035, 4, 1, 9, 0), "Marcus Yip", "joined", "as Albatross sail trimmer",
         "Marcus Yip joined Twin Bridges Racing as replacement sail trimmer for Albatross, taking over from Liam O'Brien. Background: Hong Kong Sailing Federation development squad. Strong heavy-air skills.",
         "personnel", "P01", "personnel_record", ["background", "Yip", "new_trimmer"]),

        (datetime(2036, 3, 15, 9, 0), "Campaign strategy", "meeting", "2036 Pacific Cup routing options",
         "Campaign strategy meeting: Nikora and Wallace presented three routing options for 2036 Pacific Cup. Option A: northern arc (longer but more wind). Option B: direct rhumbline. Option C: southern dive below ITCZ. Team selected Option A with contingency fallback to B.",
         "meeting_notes", "P01", "strategy_record", ["background", "strategy", "2036"]),
    ]

    for dt, subj, pred, obj, text, mtype, src, stype, tags in bg_events:
        ms.append(mem(dt, 1, 2, 12, subj, pred, obj, text, mtype,
                      "background", src, stype, tags))

    return ms


def gen_queries():
    """Generate queries for Exp14."""
    qs = []

    # C01 — Wrong entity
    qs.extend([
        {"query_id": qid(), "query": "Which boat retired from the 2032 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["Petrel retired", "Keel hydraulic failure at Mile 891", "Diverted to Hilo"],
         "acceptable_claims": ["Petrel retired due to keel problems"],
         "forbidden_claims": ["Albatross retired", "Both boats retired"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Albatross data from same race is a strong distractor"},
        {"query_id": qid(), "query": "How did Albatross perform in the 2032 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["3rd overall", "1st in Class B", "6 days 4 hours 22 minutes"],
         "acceptable_claims": ["Strong upwind performance"],
         "forbidden_claims": ["Retired", "Keel failure", "Diverted to Hilo"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Must not confuse Albatross with Petrel's retirement"},
        {"query_id": qid(), "query": "What was Petrel's best Pacific Cup result?",
         "category": "wrong_entity",
         "expected_claims": ["5th overall, 2nd in class in 2036 Pacific Cup"],
         "acceptable_claims": ["2036 was Petrel's only Pacific Cup finish"],
         "forbidden_claims": ["3rd overall (that was Albatross)", "1st in class (that was Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Petrel's only finish vs Albatross's multiple strong results"},
        {"query_id": qid(), "query": "What is the difference between Albatross and Petrel's keel bulb weight?",
         "category": "wrong_entity",
         "expected_claims": ["Albatross: 4,050 kg", "Petrel: 4,200 kg", "150 kg difference"],
         "acceptable_claims": ["Petrel is heavier by 150 kg"],
         "forbidden_claims": ["Same weight", "Identical boats"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Tests precise entity differentiation"},

        # C02 — Wrong time
        {"query_id": qid(), "query": "What were the wind conditions in the Auckland-Fiji race in 2036?",
         "category": "wrong_time",
         "expected_claims": ["NE trade winds averaging 22 knots", "Gusts to 28"],
         "acceptable_claims": ["Moderate NE trades"],
         "forbidden_claims": ["25 knots (that was 2032)", "Gusts to 32 (that was 2032)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "2032 Auckland-Fiji data is a near-identical distractor"},
        {"query_id": qid(), "query": "How did Albatross perform in the 2036 Auckland-Fiji race compared to 2032?",
         "category": "wrong_time",
         "expected_claims": ["2032: 4th overall, avg 8.7 knots, 3d 14h", "2036: 2nd overall, avg 9.1 knots, 3d 8h", "Improvement between campaigns"],
         "acceptable_claims": ["Better in 2036 than 2032"],
         "forbidden_claims": ["Same result both years", "Performance declined"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Must correctly separate two temporally similar events"},
        {"query_id": qid(), "query": "In which qualifying race did Petrel outperform Albatross?",
         "category": "wrong_time",
         "expected_claims": ["Sydney-Hobart feeder 2032: Petrel 3rd, Albatross 9th"],
         "acceptable_claims": ["The light-air Sydney-Hobart feeder in 2032"],
         "forbidden_claims": ["Auckland-Fiji (Albatross outperformed)", "2036 Sydney-Hobart (Albatross also ahead)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Only one race where Petrel beat Albatross"},

        # C03 — Near-identical events
        {"query_id": qid(), "query": "What was found during Petrel's 2033 keel inspection?",
         "category": "near_identical_events",
         "expected_claims": ["Fatigue crack in mounting bracket", "12mm crack length", "47,000 load cycles", "Failed pressure test at 195 bar", "NOT CLEARED"],
         "acceptable_claims": ["Defect found requiring repair"],
         "forbidden_claims": ["Cleared for racing (that was 2031)", "Minor surface corrosion (that was 2031)", "Operating within spec"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "2031 routine inspection is a strong distractor with overlapping terms"},
        {"query_id": qid(), "query": "Was Petrel's keel ever cleared for racing after an inspection?",
         "category": "near_identical_events",
         "expected_claims": ["Yes, in September 2031 routine inspection", "Cleared with minor cosmetic corrosion noted"],
         "acceptable_claims": ["Also cleared after 2034 refit completion"],
         "forbidden_claims": ["Cleared in 2033 (it was NOT cleared then)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Must distinguish between inspections with opposite outcomes"},
        {"query_id": qid(), "query": "What caused the fatigue crack in Petrel's keel mounting bracket?",
         "category": "near_identical_events",
         "expected_claims": ["Insufficient fillet radius in original fabrication", "0.5mm vs 2mm design spec", "Propagated over ~15,000 cycles"],
         "acceptable_claims": ["Manufacturing defect — fillet radius too small"],
         "forbidden_claims": ["Corrosion (that was cosmetic only)", "Impact damage"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Root cause from engineering analysis"},

        # C04 — Template language
        {"query_id": qid(), "query": "How many sails were recommended for replacement in the 2035 pre-season inventory?",
         "category": "template_reuse",
         "expected_claims": ["3 sails recommended for replacement", "Both primary jibs (adhesive failure)", "Heavy-air spinnaker (delaminated panels)"],
         "acceptable_claims": ["Three replacements needed"],
         "forbidden_claims": ["2 replacements (that was 2032)", "1 replacement (2031 or 2036)", "0 replacements (2033)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Five near-identical template entries — must pick the right year"},
        {"query_id": qid(), "query": "In which sail inventory was no replacement recommended?",
         "category": "template_reuse",
         "expected_claims": ["2033 post-season inventory", "All sails within acceptable fatigue life"],
         "acceptable_claims": ["The post-season inventory in 2033"],
         "forbidden_claims": ["2031 (1 replacement)", "2032 (2 replacements)", "2035 (3 replacements)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Must find the one inventory with zero replacements among five similar entries"},
        {"query_id": qid(), "query": "What was the forestay tension on Albatross in 2035?",
         "category": "template_reuse",
         "expected_claims": ["4,100 kg", "Slight decrease — re-tension recommended"],
         "acceptable_claims": [],
         "forbidden_claims": ["4,200 kg (that was 2031)", "4,150 kg (that was Petrel 2031)", "4,180 kg (that was Petrel 2035)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "very_hard", "notes": "Four near-identical rigging entries with slightly different numbers"},

        # C05 — Terminology
        {"query_id": qid(), "query": "What is the HRAA and what happened to it on Petrel?",
         "category": "terminology",
         "expected_claims": ["HRAA = hydraulic ram actuator assembly", "Part HR-2202 on Petrel", "Failed during 2032 Pacific Cup", "Crew called it 'the ram' and 'keel jack'"],
         "acceptable_claims": ["Hydraulic keel system that failed"],
         "forbidden_claims": ["Unknown system", "No failure occurred"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Tests whether formal terminology maps to informal crew descriptions"},
        {"query_id": qid(), "query": "What did Hartley call the failing keel system during the 2032 race?",
         "category": "terminology",
         "expected_claims": ["'keel mechanism'", "'keel pivot system'", "'the ram'"],
         "acceptable_claims": ["Informal terms for the HRAA"],
         "forbidden_claims": ["HRAA (that's the formal term Hartley didn't use in radio comms)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Tests retrieval of informal terminology"},
        {"query_id": qid(), "query": "What do crew logs say about the keel jack failure?",
         "category": "terminology",
         "expected_claims": ["O'Brien-Sato described grinding noises around mile 800", "Pressure dropping by mile 847", "Tried manual override, bleeding lines", "Had to retire"],
         "acceptable_claims": ["Keel jack = HRAA = hydraulic ram actuator assembly"],
         "forbidden_claims": ["No crew logs mentioning this"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Query uses colloquial term — system must map to formal HRAA context"},

        # C06 — Name collision
        {"query_id": qid(), "query": "Which Liam is the light-air specialist?",
         "category": "name_collision",
         "expected_claims": ["Liam O'Brien-Sato (P08)", "Olympic 49er background", "Sails on Petrel"],
         "acceptable_claims": ["O'Brien-Sato on Petrel"],
         "forbidden_claims": ["Liam O'Brien (he is the heavy-air specialist on Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Two Liams with complementary specialties"},
        {"query_id": qid(), "query": "What happened to Liam O'Brien in 2035?",
         "category": "name_collision",
         "expected_claims": ["Transferred to shore team coordinator", "Shoulder injury prevented continued on-water racing", "Replaced by Marcus Yip on Albatross"],
         "acceptable_claims": ["Left active sailing due to injury"],
         "forbidden_claims": ["Still sailing on Petrel (that's O'Brien-Sato)", "Left the team entirely"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Must not confuse O'Brien's shore transfer with O'Brien-Sato"},
        {"query_id": qid(), "query": "Who trimmed sails on Petrel in the 2036 Pacific Cup?",
         "category": "name_collision",
         "expected_claims": ["Liam O'Brien-Sato (P08)"],
         "acceptable_claims": [],
         "forbidden_claims": ["Liam O'Brien (he was on shore team by 2036)", "Marcus Yip (he's on Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Must correctly resolve which Liam was on which boat by 2036"},
        {"query_id": qid(), "query": "Which O'Brien attended the sail development meeting?",
         "category": "name_collision",
         "expected_claims": ["Ambiguous — the meeting notes just say 'O'Brien'", "Advocated for fuller entry angle based on strong-trades experience, which matches O'Brien (P07, heavy-air specialist) more than O'Brien-Sato"],
         "acceptable_claims": ["Likely Liam O'Brien (P07) based on the heavy-air context"],
         "forbidden_claims": ["Definitively O'Brien-Sato"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": True, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "very_hard", "notes": "Genuinely ambiguous — system should surface the ambiguity"},

        # C07 — Misleading embedding
        {"query_id": qid(), "query": "What weather systems affected the 2032 Pacific Cup fleet?",
         "category": "misleading_embedding",
         "expected_claims": ["Tropical depression TD-07", "Strengthened to Tropical Storm Kilo", "Passed ~150nm south of fleet"],
         "acceptable_claims": ["Tropical storm threatened but didn't directly impact"],
         "forbidden_claims": ["Team depression (that's morale, not weather)", "Low morale affected fleet"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Morale 'depression' memory shares many keywords with weather depression"},
        {"query_id": qid(), "query": "What strengthened after the 2032 Pacific Cup?",
         "category": "misleading_embedding",
         "expected_claims": ["Team's resolve for 2036 campaign", "Engineering review processes"],
         "acceptable_claims": ["The team came back stronger after the setback"],
         "forbidden_claims": ["Tropical Storm Kilo (that strengthened DURING the race, not after)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Tests whether 'strengthened' retrieves weather or morale context correctly"},

        # Easy controls
        {"query_id": qid(), "query": "Who founded Twin Bridges Racing?",
         "category": "control",
         "expected_claims": ["James Maitland"],
         "acceptable_claims": [], "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
        {"query_id": qid(), "query": "Where are Albatross and Petrel built?",
         "category": "control",
         "expected_claims": ["McMullen & Wing boatyard, Auckland"],
         "acceptable_claims": [], "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
        {"query_id": qid(), "query": "Who is the head of design at Twin Bridges Racing?",
         "category": "control",
         "expected_claims": ["Mei-Lin Chen"],
         "acceptable_claims": [], "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
    ])

    return qs


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        out_dir = Path(sys.argv[1])
    else:
        out_dir = Path("experiment_14_semantic_near_miss_distractor_resistance")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "perturbations").mkdir(exist_ok=True)

    print("Generating Experiment 14: Semantic Near-Miss / Distractor Resistance")

    all_memories = []
    generators = [
        ("C01: Wrong entity", gen_c01_wrong_entity),
        ("C02: Wrong time", gen_c02_wrong_time),
        ("C03: Near-identical events", gen_c03_near_identical_events),
        ("C04: Template language", gen_c04_template_language),
        ("C05: Terminology", gen_c05_terminology),
        ("C06: Name collision", gen_c06_name_collision),
        ("C07: Misleading embedding", gen_c07_misleading_embedding),
        ("Background", gen_background),
    ]

    for name, gen_fn in generators:
        ms = gen_fn()
        print(f"  {name}: {len(ms)} memories")
        all_memories.extend(ms)

    queries = gen_queries()
    print(f"\nTotal memories: {len(all_memories)}")
    print(f"Total queries: {len(queries)}")

    # Write memories
    mem_path = out_dir / "memories.jsonl"
    with open(mem_path, "w") as f:
        for m in all_memories:
            f.write(json.dumps(m) + "\n")

    # Write queries
    q_path = out_dir / "queries.jsonl"
    with open(q_path, "w") as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    # Write seed memories (first 30)
    seed_path = out_dir / "seed_memories.jsonl"
    with open(seed_path, "w") as f:
        for m in all_memories[:30]:
            f.write(json.dumps(m) + "\n")

    # Write truth state
    truth = {
        "experiment": EXP,
        "ground_truth_invariants": {
            "albatross_ne_petrel": "Albatross and Petrel are distinct boats with distinct performance profiles",
            "campaign_2032_ne_2036": "2032 and 2036 campaigns are distinct events despite similar structure",
            "obrien_ne_obrien_sato": "Liam O'Brien (P07) and Liam O'Brien-Sato (P08) are different people",
            "routine_ne_post_incident": "2031 routine inspection cleared; 2033 post-incident found fatigue crack",
            "each_inventory_distinct": "Five sail inventories are distinct events with different numbers",
            "terminology_resolves": "HRAA = hydraulic ram actuator assembly = keel mechanism = keel jack = the ram",
            "embedding_similarity_ne_relevance": "Semantic similarity does not equal factual relevance",
            "part_suffix_determines_boat": "Part suffix -A = Albatross, -P = Petrel",
        },
        "cases": {
            "C01": {"name": "Wrong Entity, Right Description", "boat_distinction": True},
            "C02": {"name": "Wrong Time, Right Entity", "temporal_distinction": True},
            "C03": {"name": "Near-Identical Events", "outcome_distinction": True},
            "C04": {"name": "Reused Phrases / Template Language", "numeric_distinction": True},
            "C05": {"name": "Correct Answer Uses Different Terminology", "synonym_resolution": True},
            "C06": {"name": "Name Collision", "entity_disambiguation": True},
            "C07": {"name": "Misleading Embedding Proximity", "polysemy_resolution": True},
        }
    }
    with open(out_dir / "truth_state.json", "w") as f:
        json.dump(truth, f, indent=2)

    # Write story bible
    sb_src = Path("/tmp/claude-0/-home-user-memory-testing/6ffa00f0-af4e-5ad8-9c00-025401d96b92/scratchpad/exp14/story_bible.md")
    if sb_src.exists():
        import shutil
        shutil.copy(sb_src, out_dir / "story_bible.md")
    else:
        with open(out_dir / "story_bible.md", "w") as f:
            f.write("# Story Bible — Experiment 14\nSee scratchpad for full version.\n")

    # Write experimental map
    exp_map = {
        "experiment": EXP,
        "cases": {
            "C01": {"manipulated": "entity identity (Albatross vs Petrel)", "controlled": "same race, same team", "failure_mode": "wrong boat selected"},
            "C02": {"manipulated": "temporal context (2032 vs 2036)", "controlled": "same entity, same race format", "failure_mode": "wrong year's data retrieved"},
            "C03": {"manipulated": "inspection outcome", "controlled": "same boat, same system, same terminology", "failure_mode": "opposite outcome reported"},
            "C04": {"manipulated": "numeric values within template", "controlled": "identical template language", "failure_mode": "wrong year's numbers retrieved"},
            "C05": {"manipulated": "terminology", "controlled": "same physical system", "failure_mode": "fails to connect formal and informal terms"},
            "C06": {"manipulated": "person identity (two Liams)", "controlled": "same team, similar roles", "failure_mode": "wrong person attributed"},
            "C07": {"manipulated": "semantic domain (weather vs morale)", "controlled": "shared keywords (depression, strengthen)", "failure_mode": "wrong domain retrieved"},
        }
    }
    with open(out_dir / "experimental_map.json", "w") as f:
        json.dump(exp_map, f, indent=2)

    # Write README
    readme = f"""# Experiment 14: Semantic Near-Miss / Distractor Resistance

## Research Question
Does semantic/embedding similarity dominate over factual relevance in memory retrieval?

## Setting
Twin Bridges Racing — competitive sailing team based in Auckland, NZ.
Two nearly identical yachts (Albatross and Petrel), two campaign cycles (2032, 2036).

## Cases
- C01: Wrong Entity, Right Description (Albatross vs Petrel)
- C02: Wrong Time, Right Entity (2032 vs 2036)
- C03: Near-Identical Events (two keel inspections, opposite outcomes)
- C04: Reused Phrases / Template Language (sail inventories)
- C05: Correct Answer Uses Different Terminology (HRAA aliases)
- C06: Name Collision (O'Brien vs O'Brien-Sato)
- C07: Misleading Embedding Proximity (depression polysemy)

## Corpus Size
- Memories: {len(all_memories)}
- Queries: {len(queries)}
"""
    with open(out_dir / "README.md", "w") as f:
        f.write(readme)

    # Write sources
    sources = """# Sources — Experiment 14

## Source Type
Fully synthetic. All events, people, boats, and races are fictional.

## Narrative Basis
Competitive offshore sailing (Pacific Cup format). Setting chosen because:
- Two boats on one team creates natural entity confusion
- Multi-year campaigns create temporal near-misses
- Equipment with part numbers creates template similarity
- Crew rotations create name collision opportunities
- Weather terminology has polysemy (depression = weather system vs morale)

## Ground Truth
All facts are author-defined with no ambiguity in the story bible.
"""
    with open(out_dir / "sources.md", "w") as f:
        f.write(sources)

    # Write manifest
    manifest = {
        "experiment": EXP,
        "version": "1.0",
        "canonical_memory_count": len(all_memories),
        "query_count": len(queries),
        "seed_count": min(30, len(all_memories)),
        "files": []
    }
    for fn in ["README.md", "experimental_map.json", "memories.jsonl", "queries.jsonl",
               "seed_memories.jsonl", "sources.md", "story_bible.md", "truth_state.json"]:
        fp = out_dir / fn
        if fp.exists():
            h = hashlib.sha256(fp.read_bytes()).hexdigest()
            manifest["files"].append({
                "path": fn,
                "bytes": fp.stat().st_size,
                "sha256": h
            })
    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Write perturbation manifest
    pert_manifest = {
        "experiment": EXP,
        "perturbations": [
            {"id": "P1", "description": "Remove boat names from all memories (replace with 'the team boat')"},
            {"id": "P2", "description": "Shuffle event_time within ±6 months"},
            {"id": "P3", "description": "Replace all 'O'Brien-Sato' with 'O'Brien' (collapse name distinction)"},
            {"id": "P4", "description": "Standardize all terminology to formal HRAA only"},
            {"id": "P5", "description": "Remove all date/year information from text fields"},
        ]
    }
    with open(out_dir / "perturbations" / "manifest.json", "w") as f:
        json.dump(pert_manifest, f, indent=2)

    print(f"\nOutput written to: {out_dir}")

    # Stats
    tags = {}
    for m in all_memories:
        for t in m.get("tags", []):
            if t.startswith("C0"):
                tags[t] = tags.get(t, 0) + 1
                break
        else:
            tags["background"] = tags.get("background", 0) + 1

    print("\nMemory distribution:")
    for k in sorted(tags.keys()):
        print(f"  {k}: {tags[k]}")

    qcats = {}
    for q in queries:
        c = q.get("category", "unknown")
        qcats[c] = qcats.get(c, 0) + 1
    print("\nQuery distribution:")
    for k in sorted(qcats.keys()):
        print(f"  {k}: {qcats[k]}")


if __name__ == "__main__":
    main()
