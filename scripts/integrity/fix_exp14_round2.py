#!/usr/bin/env python3
"""Second expansion for Experiment 14 — Semantic Near-Miss / Distractor Resistance.
Adds ~80 memories and ~40 queries to reach 200+ / 75+ targets."""

import json, hashlib, sys, os
from datetime import datetime, timedelta

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_exp14_round2.py <corpus_dir>")
        sys.exit(1)

    d = sys.argv[1]
    mem_path = os.path.join(d, "memories.jsonl")
    q_path = os.path.join(d, "queries.jsonl")

    with open(mem_path) as f:
        memories = [json.loads(l) for l in f]
    with open(q_path) as f:
        queries = [json.loads(l) for l in f]

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    next_mid = max(int(m["memory_id"][1:]) for m in memories) + 1
    next_qid = max(int(q["query_id"][1:]) for q in queries) + 1

    EXP = "exp14_semantic_near_miss_distractor_resistance"
    STORY = "twin_bridges_racing"

    def mid():
        nonlocal next_mid
        r = f"M{next_mid:04d}"
        next_mid += 1
        return r

    def qid():
        nonlocal next_qid
        r = f"Q{next_qid:03d}"
        next_qid += 1
        return r

    def ts(dt):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def mem(et, obs_h, auth_h, ing_h, subj, pred, obj, text, mtype, trole, src, stype, tags,
            bh="system", conf=1.0):
        ot = et + timedelta(hours=obs_h)
        at = ot + timedelta(hours=auth_h)
        it = at + timedelta(hours=ing_h)
        return {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": ts(et), "observation_time": ts(ot),
            "authored_time": ts(at), "ingestion_time": ts(it),
            "subject": subj, "predicate": pred, "object": obj, "text": text,
            "memory_type": mtype, "truth_role": trole, "belief_holder": bh,
            "confidence": conf, "source_id": src, "source_type": stype,
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "team", "tags": tags,
        }

    new_mems = []
    new_qs = []

    # === More C01: entity-level detail ===
    new_mems.extend([
        mem(datetime(2032,7,13,8,0), 0.5,1,12, "Albatross", "speed_log", "Day 4: avg 9.5 knots in trades",
            "Albatross speed log Day 4, 2032 Pacific Cup: averaging 9.5 knots in established NE trades. Boat well-balanced. Keel canted to starboard 18°. VMG excellent — best day of the race. Leading Class B by estimated 2 hours.",
            "race_log", "ground_truth", "P02", "speed_log",
            ["C01", "wrong_entity", "Albatross", "2032_Pacific_Cup"]),
        mem(datetime(2032,7,13,8,0), 0.5,1,12, "Petrel", "speed_log", "Day 4: avg 8.1 knots, keel concern",
            "Petrel speed log Day 4, 2032 Pacific Cup: averaging 8.1 knots. Keel hydraulic making intermittent clicking noise since dawn. Hartley monitoring closely. Reduced from full 25° cant to 15° as precaution. Speed loss estimated 0.5 knots.",
            "race_log", "ground_truth", "P04", "speed_log",
            ["C01", "wrong_entity", "Petrel", "2032_Pacific_Cup", "pre_failure"]),
        mem(datetime(2036,7,11,12,0), 0.5,1,12, "Albatross", "day2_log", "9.3 knots in NW transition",
            "Albatross Day 2 log, 2036 Pacific Cup: winds transitioning from NW to N. Averaging 9.3 knots. Wallace's routing through the high-pressure ridge working well. Keel system nominal.",
            "race_log", "ground_truth", "P02", "speed_log",
            ["C01", "wrong_entity", "Albatross", "2036_Pacific_Cup"]),
        mem(datetime(2036,7,11,12,0), 0.5,1,12, "Petrel", "day2_log", "8.7 knots in NW transition",
            "Petrel Day 2 log, 2036 Pacific Cup: averaging 8.7 knots. New HR-2202-R2 keel system running beautifully. O'Brien-Sato trimming the reaching sails aggressively. Falling behind Albatross but well within class contention.",
            "race_log", "ground_truth", "P04", "speed_log",
            ["C01", "wrong_entity", "Petrel", "2036_Pacific_Cup"]),
    ])

    # === More C02: paired temporal events ===
    new_mems.extend([
        mem(datetime(2032,7,16,18,0), 2,4,12, "Post-race debrief 2032", "held", "at Kauai Yacht Club",
            "2032 Pacific Cup post-race debrief at Kauai Yacht Club. Albatross crew celebrated 3rd overall finish. Analysis: Nikora's northern routing gained 4 hours over rhumbline boats. Key weakness: light-air reaching on Day 5.",
            "meeting_notes", "ground_truth", "P01", "debrief_record",
            ["C02", "wrong_time", "Pacific_Cup", "2032", "debrief"]),
        mem(datetime(2036,7,15,18,0), 2,4,12, "Post-race debrief 2036", "held", "at Kauai Yacht Club",
            "2036 Pacific Cup post-race debrief at Kauai Yacht Club. Albatross crew celebrated 2nd overall — new class record. Analysis: routing through Pacific High was bold but paid off. Both boats finished — team's first clean Pacific Cup.",
            "meeting_notes", "ground_truth", "P01", "debrief_record",
            ["C02", "wrong_time", "Pacific_Cup", "2036", "debrief"]),
        mem(datetime(2032,6,28,9,0), 1,2,12, "Weather outlook", "for_2032_Pacific_Cup", "NW gradient, trades expected Day 3",
            "Weather routing briefing for 2032 Pacific Cup: NW gradient winds at start 12-15 knots. Transition to NE trades expected by Day 3 south of 30°N. ITCZ at approximately 8°N — may impact southern routing strategies. Sea state: 1.5-2m WNW swell.",
            "weather_briefing", "ground_truth", "P09", "weather_analysis",
            ["C02", "wrong_time", "Pacific_Cup", "2032", "weather_outlook"]),
        mem(datetime(2036,7,5,9,0), 1,2,12, "Weather outlook", "for_2036_Pacific_Cup", "SW clearing to NW, trades Day 2",
            "Weather routing briefing for 2036 Pacific Cup: SW winds at start clearing to NW by evening. Earlier transition to trades expected — Day 2 south of 32°N (ITCZ further north than 2032). Sea state: 1-1.5m SW swell diminishing.",
            "weather_briefing", "ground_truth", "P09", "weather_analysis",
            ["C02", "wrong_time", "Pacific_Cup", "2036", "weather_outlook"]),
    ])

    # === More C03: additional inspection details ===
    new_mems.extend([
        mem(datetime(2031,9,16,9,0), 1,2,12, "Petrel keel survey", "recommendation", "re-fair keel bulb before next season",
            "Surveyor's recommendation following 2031 annual inspection: re-fair keel bulb to address cosmetic corrosion. Estimated cost: NZD 4,500. No structural concern. Keel system cleared for current season without action required.",
            "inspection_report", "ground_truth", "P05", "survey_recommendation",
            ["C03", "near_identical", "Petrel", "2031", "recommendation"]),
        mem(datetime(2033,11,6,9,0), 4,8,24, "Petrel keel survey", "recommendation", "full hydraulic system replacement required",
            "Surveyor's recommendation following 2033 post-incident inspection: FULL hydraulic ram actuator assembly replacement required. Mounting bracket replacement mandatory. All hydraulic lines to be replaced. Estimated cost: NZD 180,000. Boat NOT CLEARED for any sailing until repairs completed.",
            "inspection_report", "ground_truth", "P05", "survey_recommendation",
            ["C03", "near_identical", "Petrel", "2033", "recommendation"]),
    ])

    # === More C04: more template entries ===
    new_mems.extend([
        mem(datetime(2032,2,15,9,0), 2,4,12, "Electronics check 2032", "completed", "both boats pre-season",
            "Pre-season electronics check completed for both boats. Autopilot calibration: Albatross heading error +0.3°, corrected. Petrel heading error -0.1°, within spec. AIS: both operational. VHF: both operational. Satphone: both charged and tested. All systems GO.",
            "maintenance_log", "ground_truth", "P09", "electronics_check",
            ["C04", "template_language", "electronics", "2032"]),
        mem(datetime(2036,2,15,9,0), 2,4,12, "Electronics check 2036", "completed", "both boats pre-season",
            "Pre-season electronics check completed for both boats. Autopilot calibration: Albatross heading error +0.5° (increased since 2032, recalibrated). Petrel heading error +0.2°, within spec. AIS: both operational. VHF: both operational. New Iridium Certus: both operational. All systems GO.",
            "maintenance_log", "ground_truth", "P09", "electronics_check",
            ["C04", "template_language", "electronics", "2036"]),
        mem(datetime(2032,7,7,9,0), 1,2,12, "Provision check 2032", "completed", "Pacific Cup supplies verified",
            "Final provision check for 2032 Pacific Cup: Albatross — 14 days food, 200L water, 48 energy bars, complete medical kit. Petrel — 14 days food, 200L water, 48 energy bars, complete medical kit. Both boats' emergency rations sealed and dated.",
            "logistics", "ground_truth", "P01", "provisions_check",
            ["C04", "template_language", "provisions", "2032"]),
        mem(datetime(2036,7,6,9,0), 1,2,12, "Provision check 2036", "completed", "Pacific Cup supplies verified",
            "Final provision check for 2036 Pacific Cup: Albatross — 12 days food (shorter expected passage), 180L water, 60 energy bars (increased per Vasquez), complete medical kit. Petrel — 14 days food (conservative estimate), 200L water, 60 energy bars, complete medical kit.",
            "logistics", "ground_truth", "P01", "provisions_check",
            ["C04", "template_language", "provisions", "2036"]),
    ])

    # === More C05: terminology bridges ===
    new_mems.extend([
        mem(datetime(2032,7,14,4,0), 0.5,1,12, "Shore team", "received", "distress report about keel pivot system",
            "Shore team received satellite phone call from Petrel at 04:15: 'Keel pivot system has failed completely. The hydraulic is dead. Keel locked. We're heading for Hilo.' Maitland immediately contacted US Coast Guard as precaution.",
            "radio_log", "ground_truth", "P01", "emergency_communication",
            ["C05", "terminology", "keel_pivot", "informal"]),
        mem(datetime(2034,1,10,9,0), 2,4,12, "Chen design review", "specified", "HRAA Rev 2 bracket improvements",
            "Mei-Lin Chen's design review for HRAA Rev 2 mounting bracket: increased fillet radius from 0.5mm to 2.5mm (5× increase). Added FEA analysis showing stress concentration reduction of 68%. New bracket milled from solid billet instead of cast — eliminates porosity risk.",
            "engineering_spec", "ground_truth", "P05", "design_review",
            ["C05", "terminology", "HRAA", "formal", "design_improvement"]),
    ])

    # === More C06: name collision scenarios ===
    new_mems.extend([
        mem(datetime(2031,6,15,14,0), 1,2,12, "Liam", "training_report", "heavy-air session in Hauraki Gulf",
            "Liam logged an intense heavy-air training session in the Hauraki Gulf. 28 knots gusting 35. Albatross flew the heavy A3 spinnaker for 4 hours. 'Best conditions we've had all season for practicing heavy-air drops' — Liam to Nikora.",
            "training", "ground_truth", "P07", "training_log",
            ["C06", "name_collision", "Liam", "Albatross", "ambiguous_P07"]),
        mem(datetime(2031,6,16,14,0), 1,2,12, "Liam", "training_report", "light-air session off Waiheke Island",
            "Liam reported a productive light-air training session off Waiheke Island. 6-8 knots, glassy conditions. Petrel practiced slow-speed tacking and spinnaker peeling. 'Got the peel down to 12 seconds' — Liam to Hartley.",
            "training", "ground_truth", "P08", "training_log",
            ["C06", "name_collision", "Liam", "Petrel", "ambiguous_P08"]),
        mem(datetime(2035,5,1,9,0), 1,2,12, "Yip and O'Brien-Sato", "joint_training", "inter-boat crew exchange",
            "Marcus Yip and Liam O'Brien-Sato swapped boats for a week of cross-training. Yip sailed on Petrel to learn O'Brien-Sato's light-air techniques. O'Brien-Sato sailed on Albatross to refine heavy-air skills. Both reported valuable experience.",
            "training", "ground_truth", "P10", "training_record",
            ["C06", "name_collision", "cross_training", "Yip", "OBrien-Sato"]),
    ])

    # === More C07: additional polysemy ===
    new_mems.extend([
        # "Pitch" — boat motion vs design pitch angle
        mem(datetime(2032,7,12,2,0), 0.5,1,12, "Albatross", "experienced", "heavy pitching in short seas",
            "Albatross experienced heavy pitching in short, steep seas during the night watch. Pitch angle reaching ±12°. Crew wearing harnesses at all times. Speed reduced to 7.5 knots for comfort. Wallace: 'The pitch is slowing us down but safety comes first.'",
            "race_log", "ground_truth", "P09", "navigation_log",
            ["C07", "misleading_embedding", "pitch_motion", "Albatross"]),
        mem(datetime(2031,2,15,9,0), 4,8,24, "Sørensen sail design", "specified", "jib luff pitch angle of 12°",
            "Sørensen's jib design specification: luff pitch angle of 12° from mast centerline. This pitch optimizes the slot between jib and mainsail at 12-knot apparent wind. Manufacturing tolerance: ±0.5°.",
            "engineering_spec", "ground_truth", "P06", "sail_design",
            ["C07", "misleading_embedding", "pitch_angle", "sail_design"]),
        # "Draft" — boat draft vs sail draft
        mem(datetime(2030,9,15,10,0), 2,4,24, "Albatross", "measured", "draft of 2.8m with keel down",
            "Albatross hull measurements at launch: draft 2.8m with keel fully down (0° cant). Draft reduces to 2.1m with keel canted to maximum 40°. Minimum water depth for safe maneuvering: 3.5m.",
            "engineering_spec", "ground_truth", "P05", "hull_measurement",
            ["C07", "misleading_embedding", "hull_draft", "Albatross"]),
        mem(datetime(2032,6,26,9,0), 1,2,12, "Sørensen", "adjusted", "mainsail draft position to 42%",
            "Sørensen adjusted the mainsail draft position to 42% from the luff (previously 38%). Purpose: deeper draft further aft provides more power in the reaching conditions expected for the Pacific Cup. Achieved by adjusting cunningham and outhaul settings.",
            "maintenance", "ground_truth", "P06", "sail_tuning",
            ["C07", "misleading_embedding", "sail_draft", "mainsail"]),
    ])

    # === More Background ===
    bg = [
        mem(datetime(2031,3,15,9,0), 1,2,12, "Albatross", "measured", "VPP performance prediction validated",
            "Velocity Prediction Program (VPP) validated against Albatross sea trial data. Model accuracy: ±3% across tested wind range (8-25 knots). VPP predicts Albatross slightly faster upwind, Petrel slightly faster downwind — consistent with hull form differences.",
            "research", "ground_truth", "P05", "performance_model", ["background", "VPP", "performance"]),
        mem(datetime(2031,8,15,9,0), 1,2,12, "Dive inspection", "completed", "underwater hull check both boats",
            "Commercial dive inspection of both hulls at Westhaven Marina. Albatross: hull clean, no growth, all appendages intact. Petrel: minor algae on starboard waterline, cleaned. Through-hull fittings: both boats clear.",
            "maintenance", "background", "P05", "dive_report", ["background", "dive_inspection"]),
        mem(datetime(2032,3,10,9,0), 1,2,12, "NZ team sendoff", "event", "media and supporters at Viaduct",
            "Team sendoff event at Auckland Viaduct. 200 supporters attended. Mayor spoke. Team flag raised. Both boats displayed in full racing livery. Media coverage on TV3 and in NZ Herald sports section.",
            "event", "background", "P01", "media_record", ["background", "sendoff"]),
        mem(datetime(2032,7,17,14,0), 1,2,12, "Post-race interview", "given", "Nikora to Sailing Magazine",
            "Nikora's post-2032 Pacific Cup interview with Sailing Magazine: 'Albatross is a wonderful boat. 3rd overall against these big-budget American teams is something to be proud of. We learned a lot about the Pacific High transition that will help in 2036.'",
            "media", "background", "P02", "media_interview", ["background", "media", "2032"]),
        mem(datetime(2033,1,15,9,0), 1,2,12, "Budget review", "completed", "2033 financial planning",
            "Annual budget review for 2033. Total campaign spend 2032: NZD 1.8M (under budget by NZD 200K). Petrel keel repair will consume most of the 2033 budget. Maitland: 'We need to find additional funding for the repair.'",
            "administrative", "background", "P01", "financial_record", ["background", "budget"]),
        mem(datetime(2034,4,15,9,0), 1,2,12, "Chen", "presented", "keel foil optimization study",
            "Mei-Lin Chen presented keel foil optimization study at NZ Yacht Research Conference. CFD results showed potential for 1.5% drag reduction with modified NACA profile. Paper well-received; three international teams expressed interest in the method.",
            "event", "background", "P05", "conference_record", ["background", "conference", "keel_foil"]),
        mem(datetime(2034,11,1,9,0), 1,2,12, "Team photo", "shoot", "for 2035 sponsor materials",
            "Professional team photo shoot at McMullen & Wing boatyard. Both boats hauled out, crews in full kit. O'Brien still in team photo despite transition to shore role. New crew member Marcus Yip photographed with Albatross crew.",
            "event", "background", "P01", "media_record", ["background", "media", "photo"]),
        mem(datetime(2035,9,1,9,0), 1,2,12, "Hartley", "published", "tactical guide for Pacific Cup",
            "Ben Hartley published 'Pacific Cup Tactical Playbook' based on his racing and coaching experience. Distributed to both crews. 47-page guide covering start strategy, rhumbline vs great circle, Pacific High tactics, and ITCZ crossing.",
            "publication", "background", "P04", "publication_record", ["background", "publication", "tactics"]),
        mem(datetime(2036,1,5,9,0), 1,2,12, "New Year planning", "session", "2036 season goals",
            "New Year planning session: Maitland set three goals for 2036 — (1) Both boats finish Pacific Cup. (2) At least one boat in top 3 overall. (3) Class B record attempt. Team unanimous in prioritizing Goal 1 after 2032 Petrel retirement.",
            "meeting_notes", "background", "P01", "planning_record", ["background", "planning", "2036"]),
        mem(datetime(2036,6,20,9,0), 1,2,12, "Crew briefing", "held", "weather contingency planning",
            "Crew briefing on weather contingency plans: if tropical cyclone threatens, diversion ports listed (Hilo, Honolulu, Monterey). Emergency procedures reviewed. Satellite phone protocols confirmed. All crew acknowledge.",
            "training", "background", "P09", "safety_briefing", ["background", "safety", "contingency"]),
        mem(datetime(2036,7,14,6,0), 0.5,1,12, "Final morning", "of_2036_race", "both boats approaching Kauai",
            "Final morning of 2036 Pacific Cup: both Twin Bridges boats approaching Kauai from the NW. Albatross 40nm from finish, Petrel 85nm. Beautiful conditions — 12 knots NE, clear skies, flat seas. Shore team and supporters assembling at Kauai Yacht Club.",
            "race_log", "ground_truth", "P09", "navigation_log", ["background", "2036_Pacific_Cup", "final_approach"]),
        mem(datetime(2031,11,20,9,0), 1,2,12, "Weather station", "installed", "at team base for training reference",
            "Professional weather station installed at team base (Westhaven Marina) for training data reference. Measures wind speed/direction, barometric pressure, temperature, humidity. Data logged at 10-minute intervals. Helps crew calibrate their wind sense.",
            "maintenance", "background", "P09", "equipment_record", ["background", "weather_station"]),
    ]
    new_mems.extend(bg)

    # === More Queries ===
    new_qs.extend([
        # C01
        {"query_id": qid(), "query": "What speed was Albatross averaging on Day 4 of the 2032 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["9.5 knots"],
         "acceptable_claims": [],
         "forbidden_claims": ["8.1 knots (that was Petrel Day 4)", "8.5 knots (that was Petrel Day 2)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Must match both correct entity and correct day"},
        {"query_id": qid(), "query": "Did both boats finish the 2036 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["Yes — both finished", "Albatross 2nd overall", "Petrel 5th overall"],
         "acceptable_claims": ["Both completed the race"],
         "forbidden_claims": ["One retired (2032, not 2036)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "medium", "notes": "Contrasts with 2032 where Petrel retired"},
        {"query_id": qid(), "query": "What was Petrel's speed at Mile 400 in the 2032 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["No specific Mile 400 data for Petrel in 2032 is recorded"],
         "acceptable_claims": ["Petrel was averaging 8.5 knots on Day 2 and 8.1 knots on Day 4"],
         "forbidden_claims": ["9.2 knots (that's Albatross at Mile 400)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": True, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": True,
         "difficulty": "very_hard", "notes": "Albatross Mile 400 data is a strong distractor"},

        # C02
        {"query_id": qid(), "query": "How many boats entered the 2036 Pacific Cup?",
         "category": "wrong_time",
         "expected_claims": ["89 boats"],
         "acceptable_claims": [],
         "forbidden_claims": ["94 boats (that was 2032)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Near-identical briefing entries from two years"},
        {"query_id": qid(), "query": "What ENSO conditions prevailed during the 2032 vs 2036 Pacific Cup?",
         "category": "wrong_time",
         "expected_claims": ["2032: weak La Niña", "2036: ENSO neutral"],
         "acceptable_claims": ["Different ENSO states"],
         "forbidden_claims": ["Same conditions both years"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Climate context differs between campaigns"},

        # C03
        {"query_id": qid(), "query": "What did the surveyor recommend after each of Petrel's two keel inspections?",
         "category": "near_identical_events",
         "expected_claims": ["2031: re-fair keel bulb (NZD 4,500 cosmetic)", "2033: full hydraulic system replacement (NZD 180,000 mandatory)"],
         "acceptable_claims": ["Cosmetic repair in 2031 vs major structural repair in 2033"],
         "forbidden_claims": ["Same recommendation both times"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Opposite recommendations from near-identical inspection reports"},

        # C04
        {"query_id": qid(), "query": "What was Albatross's autopilot heading error in 2036?",
         "category": "template_reuse",
         "expected_claims": ["+0.5° (increased since 2032, recalibrated)"],
         "acceptable_claims": [],
         "forbidden_claims": ["+0.3° (that was 2032)", "-0.1° (that was Petrel 2032)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "very_hard", "notes": "Small number difference in template-identical electronics checks"},
        {"query_id": qid(), "query": "How did food provisions differ between 2032 and 2036 Pacific Cups?",
         "category": "template_reuse",
         "expected_claims": ["2032: 14 days food both boats, 200L water", "2036: Albatross 12 days (shorter expected), Petrel 14 days (conservative), energy bars increased to 60"],
         "acceptable_claims": ["Provisions adapted for expected passage time"],
         "forbidden_claims": ["Identical provisions both years"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Template-language entries with meaningful differences in detail"},

        # C05
        {"query_id": qid(), "query": "What design improvements did Chen make to the HRAA mounting bracket?",
         "category": "terminology",
         "expected_claims": ["Fillet radius increased from 0.5mm to 2.5mm (5× increase)", "FEA showed 68% stress concentration reduction", "Milled from solid billet instead of cast"],
         "acceptable_claims": ["Comprehensive bracket redesign"],
         "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Uses formal HRAA term — must retrieve engineering details"},

        # C06
        {"query_id": qid(), "query": "Did the two Liams ever sail together on the same boat?",
         "category": "name_collision",
         "expected_claims": ["No — O'Brien was always on Albatross and O'Brien-Sato was always on Petrel during racing", "O'Brien-Sato briefly sailed on Albatross during a cross-training week in 2035"],
         "acceptable_claims": ["Only during cross-training, not competitive racing"],
         "forbidden_claims": ["They always sailed together", "They're the same person"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Must distinguish racing assignment from training cross-over"},

        # C07
        {"query_id": qid(), "query": "What was the pitch angle issue with Albatross?",
         "category": "misleading_embedding",
         "expected_claims": ["Albatross experienced heavy pitching (±12° boat motion) in short seas during 2032 Pacific Cup night watch"],
         "acceptable_claims": ["Boat motion issue in rough seas"],
         "forbidden_claims": ["12° jib luff pitch angle (that's a sail design specification, not a boat motion problem)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "'Pitch' polysemy — boat motion (±12°) vs sail design (12° luff pitch)"},
        {"query_id": qid(), "query": "What is Albatross's draft?",
         "category": "misleading_embedding",
         "expected_claims": ["2.8m with keel fully down", "Reduces to 2.1m at maximum cant"],
         "acceptable_claims": ["Hull draft depends on keel angle"],
         "forbidden_claims": ["42% (that's the mainsail draft position, not the hull draft)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "'Draft' polysemy — hull depth (2.8m) vs sail shape (42%)"},

        # Cross-case
        {"query_id": qid(), "query": "What was Nikora's key tactical decision in each Pacific Cup?",
         "category": "cross_case",
         "expected_claims": ["2032: stayed north of rhumbline, gained 4 hours over direct-route boats", "2036: aggressive routing through Pacific High, achieved class record"],
         "acceptable_claims": ["Bold routing decisions both years"],
         "forbidden_claims": ["Same strategy both years"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Must correctly attribute tactical decisions to correct year"},
        {"query_id": qid(), "query": "How did Petrel's keel system perform across its entire history?",
         "category": "cross_case",
         "expected_claims": ["2031: cleared for racing", "2032: failed during Pacific Cup", "2033: fatigue crack found", "2034: rebuilt with HR-2202-R2", "2034-2036: performed flawlessly"],
         "acceptable_claims": ["Failed once, then rebuilt and performed well"],
         "forbidden_claims": ["Always performed well", "Failed multiple times"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Requires assembling a timeline from multiple near-identical inspection/test entries"},

        # Easy controls
        {"query_id": qid(), "query": "What year was Petrel launched?",
         "category": "control",
         "expected_claims": ["January 2031"],
         "acceptable_claims": [],
         "forbidden_claims": ["2030 (that was Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
        {"query_id": qid(), "query": "Who replaced Liam O'Brien on Albatross?",
         "category": "control",
         "expected_claims": ["Marcus Yip"],
         "acceptable_claims": [],
         "forbidden_claims": ["O'Brien-Sato (wrong boat)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval with name collision potential"},
        {"query_id": qid(), "query": "What is the team's primary sponsor?",
         "category": "control",
         "expected_claims": ["AkzoNobel"],
         "acceptable_claims": [],
         "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
    ])

    print(f"\nAdding {len(new_mems)} memories, {len(new_qs)} queries...")
    memories.extend(new_mems)
    queries.extend(new_qs)
    print(f"Total memories: {len(memories)}, queries: {len(queries)}")

    # Write
    with open(mem_path, 'w') as f:
        for m in memories:
            f.write(json.dumps(m) + "\n")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    # Update manifest
    manifest_path = os.path.join(d, "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    for entry in manifest["files"]:
        fn = entry["path"]
        if fn in ("memories.jsonl", "queries.jsonl"):
            fp = os.path.join(d, fn)
            entry["sha256"] = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            entry["bytes"] = os.path.getsize(fp)
    manifest["canonical_memory_count"] = len(memories)
    manifest["query_count"] = len(queries)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Stats
    tags = {}
    for m in memories:
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
