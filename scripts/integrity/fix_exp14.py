#!/usr/bin/env python3
"""Expansion for Experiment 14 — Semantic Near-Miss / Distractor Resistance.
Adds ~130 memories and ~55 queries to reach 200+ / 75+ targets."""

import json, hashlib, sys, os
from datetime import datetime, timedelta

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_exp14.py <corpus_dir>")
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

    # ==================== C01 Expansion: More boat-specific data ====================
    new_mems.extend([
        mem(datetime(2032,7,11,6,0), 0.5,1,12, "Albatross", "speed_log", "Day 2: avg 8.8 knots reaching",
            "Albatross speed log Day 2, 2032 Pacific Cup: averaging 8.8 knots on a reaching leg. Seas 2m, winds 15-18 NW. Nikora elected to stay north of the rhumbline, betting on stronger pressure.",
            "race_log", "ground_truth", "P02", "speed_log",
            ["C01", "wrong_entity", "Albatross", "2032_Pacific_Cup"]),
        mem(datetime(2032,7,11,6,0), 0.5,1,12, "Petrel", "speed_log", "Day 2: avg 8.5 knots reaching",
            "Petrel speed log Day 2, 2032 Pacific Cup: averaging 8.5 knots on a reaching leg. Running 12nm south of Albatross. Hartley favoring the direct route. Keel canted to port at 15°.",
            "race_log", "ground_truth", "P04", "speed_log",
            ["C01", "wrong_entity", "Petrel", "2032_Pacific_Cup"]),
        mem(datetime(2032,7,14,18,0), 2,4,12, "Petrel", "arrived", "Hilo harbor after retirement",
            "Petrel arrived at Hilo harbor at 18:30 local time after retiring from the 2032 Pacific Cup. Keel locked at 8° cant angle. Crew in good spirits despite disappointment. Customs clearance completed.",
            "race_log", "ground_truth", "P04", "port_record",
            ["C01", "wrong_entity", "Petrel", "2032_Pacific_Cup", "Hilo"]),
        mem(datetime(2036,7,10,8,0), 1,2,12, "Albatross", "started", "2036 Pacific Cup",
            "Albatross (TB-001) crossed the start line at 08:22 PDT in the 2036 Pacific Cup. Starting conditions: 14 knots NW, clear skies. Clean start, positioned mid-fleet. Nikora immediately tacked to the favored right side.",
            "race_log", "ground_truth", "P02", "race_record",
            ["C01", "wrong_entity", "Albatross", "2036_Pacific_Cup"]),
        mem(datetime(2036,7,10,8,0), 1,2,12, "Petrel", "started", "2036 Pacific Cup",
            "Petrel (TB-002) crossed the start line at 08:25 PDT in the 2036 Pacific Cup. Starting conditions: 14 knots NW. Slightly late start. O'Brien-Sato had the keel system running smoothly from the gun.",
            "race_log", "ground_truth", "P04", "race_record",
            ["C01", "wrong_entity", "Petrel", "2036_Pacific_Cup"]),
        mem(datetime(2032,7,15,10,0), 2,4,12, "Albatross", "crossed_finish", "in Kauai, 2032 Pacific Cup",
            "Albatross crossed the finish line off Kauai at 10:22 PDT. Crew fired signal flare. Nikora: 'Incredible race. Albatross handled everything we threw at her.' Shore team reported Petrel's retirement with visible relief that their sister ship was safe.",
            "race_log", "ground_truth", "P02", "race_record",
            ["C01", "wrong_entity", "Albatross", "2032_Pacific_Cup", "finish"]),
    ])

    # ==================== C02 Expansion: More temporal pairs ====================
    new_mems.extend([
        mem(datetime(2032,3,3,6,0), 1,2,12, "Auckland-Fiji 2032", "pre_race", "fleet briefing: 34 boats, NE trades expected",
            "Auckland-Fiji 2032 pre-race briefing: fleet of 34 boats. NE trade winds forecast to build to 25+ knots by Day 2. Course: Auckland to Suva via Minerva Reef waypoint. Race record: 2 days 18 hours (catamaran).",
            "race_log", "ground_truth", "P09", "race_briefing",
            ["C02", "wrong_time", "Auckland_Fiji", "2032", "briefing"]),
        mem(datetime(2036,3,5,6,0), 1,2,12, "Auckland-Fiji 2036", "pre_race", "fleet briefing: 31 boats, moderate NE trades expected",
            "Auckland-Fiji 2036 pre-race briefing: fleet of 31 boats. NE trade winds forecast at 20-24 knots. Course: Auckland to Suva via Minerva Reef waypoint. Race record: 2 days 18 hours (unchanged). Albatross and Petrel both expected to contend for class honors.",
            "race_log", "ground_truth", "P09", "race_briefing",
            ["C02", "wrong_time", "Auckland_Fiji", "2036", "briefing"]),
        mem(datetime(2032,3,7,14,0), 1,2,12, "Petrel", "performance_in", "Auckland-Fiji 2032",
            "Petrel performance in Auckland-Fiji 2032: Struggled in heavy downwind conditions. Broached twice in 28-knot gusts. Avg speed 8.1 knots. Finished 7th overall in 3 days 22 hours. Hartley noted keel system performed well in rough conditions.",
            "race_log", "ground_truth", "P04", "performance_report",
            ["C02", "wrong_time", "Auckland_Fiji", "2032", "Petrel"]),
        mem(datetime(2036,3,9,14,0), 1,2,12, "Petrel", "performance_in", "Auckland-Fiji 2036",
            "Petrel performance in Auckland-Fiji 2036: Improved downwind handling since 2032. No broaches. Rebuilt keel system allowed more aggressive canting. Avg speed 8.6 knots. Finished 5th overall in 3 days 12 hours.",
            "race_log", "ground_truth", "P04", "performance_report",
            ["C02", "wrong_time", "Auckland_Fiji", "2036", "Petrel"]),
        mem(datetime(2032,6,17,14,0), 1,2,12, "Petrel", "performance_in", "Sydney-Hobart feeder 2032",
            "Petrel excelled in light conditions of Sydney-Hobart feeder 2032. O'Brien-Sato's light-air trimming made the difference in the glassy patches of Bass Strait. Petrel overtook 5 boats during the drifting match. Finished 3rd overall.",
            "race_log", "ground_truth", "P04", "performance_report",
            ["C02", "wrong_time", "Sydney_Hobart", "2032", "Petrel"]),
        mem(datetime(2036,6,19,14,0), 1,2,12, "Petrel", "performance_in", "Sydney-Hobart feeder 2036",
            "Petrel performance in Sydney-Hobart feeder 2036: moderate conditions suited both boats. Petrel's heavier keel bulb gave advantage in the building seas of Bass Strait. O'Brien-Sato's upwind trimming improved since 2032. Finished 6th overall.",
            "race_log", "ground_truth", "P04", "performance_report",
            ["C02", "wrong_time", "Sydney_Hobart", "2036", "Petrel"]),
    ])

    # ==================== C03 Expansion: More inspection pairs ====================
    new_mems.extend([
        mem(datetime(2031,9,15,10,0), 1,2,12, "Petrel keel hydraulic", "test_result", "280 bar, holding, passed",
            "Petrel hydraulic system test during 2031 annual inspection: pressure test result 280 bar, holding steady for 15 minutes. Spec requires minimum 275 bar. Flow rate: 12 L/min. Accumulator charge: 190 bar. All within parameters. PASSED.",
            "inspection_report", "ground_truth", "P05", "test_record",
            ["C03", "near_identical", "Petrel", "2031", "hydraulic_test", "passed"]),
        mem(datetime(2033,11,5,10,0), 2,4,24, "Petrel keel hydraulic", "test_result", "195 bar, FAILED",
            "Petrel hydraulic system test during 2033 post-incident inspection: pressure test result 195 bar — dropped to 180 bar within 5 minutes. Spec requires minimum 275 bar. Visible fluid weeping at mounting bracket seal. Flow rate: 6 L/min (degraded). FAILED.",
            "inspection_report", "ground_truth", "P05", "test_record",
            ["C03", "near_identical", "Petrel", "2033", "hydraulic_test", "failed"]),
        mem(datetime(2033,11,8,10,0), 1,2,24, "Albatross keel hydraulic", "test_result", "282 bar, holding, passed",
            "Albatross emergency hydraulic test (triggered by Petrel's findings): 282 bar, holding for 20 minutes. No pressure decay. No weeping at mounting bracket. Fillet radius measured at 1.8mm — within tolerance. PASSED.",
            "inspection_report", "ground_truth", "P05", "test_record",
            ["C03", "near_identical", "Albatross", "2033", "hydraulic_test", "passed"]),
        mem(datetime(2034,3,1,9,0), 2,4,12, "Petrel keel", "post_refit_test", "295 bar, passed, new HR-2202-R2 installed",
            "Post-refit pressure test for Petrel's new HR-2202-R2 hydraulic ram: 295 bar, held for 30 minutes. Exceeds 275 bar minimum by 7%. New mounting bracket fillet radius: 2.5mm (above 2mm spec). Cant range verified: full ±40°. CLEARED FOR RACING.",
            "inspection_report", "ground_truth", "P05", "test_record",
            ["C03", "near_identical", "Petrel", "2034", "post_refit", "cleared"]),
    ])

    # ==================== C04 Expansion: More template entries ====================
    new_mems.extend([
        mem(datetime(2032,1,15,9,0), 2,4,12, "Albatross haul-out 2032", "completed", "antifouling and through-hull service",
            "Haul-out completed for Albatross at Westhaven Marina. Antifouling applied (Hempel Olympic+). Through-hulls serviced, seacocks greased. Rudder bearings: slight play detected, adjusted. Keel fairing: smooth, no damage.",
            "maintenance_log", "ground_truth", "P05", "haul_out_record",
            ["C04", "template_language", "Albatross", "haul_out", "2032"]),
        mem(datetime(2032,1,17,9,0), 2,4,12, "Petrel haul-out 2032", "completed", "antifouling and through-hull service",
            "Haul-out completed for Petrel at Westhaven Marina. Antifouling applied (Hempel Olympic+). Through-hulls serviced, seacocks greased. Rudder bearings: within spec. Keel fairing: minor abrasion on starboard side, touched up.",
            "maintenance_log", "ground_truth", "P05", "haul_out_record",
            ["C04", "template_language", "Petrel", "haul_out", "2032"]),
        mem(datetime(2035,12,10,9,0), 2,4,12, "Albatross haul-out 2035", "completed", "antifouling and through-hull service",
            "Haul-out completed for Albatross at Westhaven Marina. Antifouling applied (Hempel Olympic+). Through-hulls serviced, seacocks greased. Rudder bearings: replaced after 5 years of service. New keel foil profile performing well. Keel fairing: excellent condition.",
            "maintenance_log", "ground_truth", "P05", "haul_out_record",
            ["C04", "template_language", "Albatross", "haul_out", "2035"]),
        mem(datetime(2035,12,12,9,0), 2,4,12, "Petrel haul-out 2035", "completed", "antifouling and through-hull service",
            "Haul-out completed for Petrel at Westhaven Marina. Antifouling applied (Hempel Olympic+). Through-hulls serviced, seacocks greased. Rudder bearings: within spec. New keel foil profile installed. Post-refit keel system: 2 years in service, performing flawlessly.",
            "maintenance_log", "ground_truth", "P05", "haul_out_record",
            ["C04", "template_language", "Petrel", "haul_out", "2035"]),
        # Safety drills — template language
        mem(datetime(2032,3,1,9,0), 1,2,12, "Safety drill", "completed", "pre-Auckland-Fiji 2032 MOB drill",
            "Man overboard recovery drill completed for both crews. Albatross: recovery time 4:12 (target <5:00). Petrel: recovery time 3:48 (target <5:00). Both crews certified for offshore racing. Life raft deployment: satisfactory.",
            "training", "ground_truth", "P10", "safety_record",
            ["C04", "template_language", "safety_drill", "2032"]),
        mem(datetime(2036,3,1,9,0), 1,2,12, "Safety drill", "completed", "pre-Auckland-Fiji 2036 MOB drill",
            "Man overboard recovery drill completed for both crews. Albatross: recovery time 3:55 (target <5:00). Petrel: recovery time 3:32 (target <5:00). Both crews certified for offshore racing. Life raft deployment: satisfactory. New AIS MOB beacons tested successfully.",
            "training", "ground_truth", "P10", "safety_record",
            ["C04", "template_language", "safety_drill", "2036"]),
    ])

    # ==================== C05 Expansion: More terminology variants ====================
    new_mems.extend([
        mem(datetime(2033,12,1,9,0), 4,8,24, "Refit specification", "defines", "HR-2202-R2 replacement hydraulic ram",
            "Refit specification for Petrel keel system: Replace HR-2202 hydraulic ram actuator assembly with HR-2202-R2 (revised design). Changes: new mounting bracket with 2.5mm fillet radius, upgraded seals rated to 350 bar, improved accumulator capacity. Acronym: HRAA Rev 2.",
            "engineering_spec", "ground_truth", "P05", "refit_spec",
            ["C05", "terminology", "HRAA", "HR-2202-R2", "formal"]),
        mem(datetime(2034,2,15,9,0), 1,2,12, "Shore crew", "discussed", "keel jack replacement progress",
            "Shore crew update: 'New keel jack is in and looks great. The old ram was a mess — can see where the crack started. New bracket is beefy. Chen designed it with extra meat around the corners this time.'",
            "crew_log", "ground_truth", "P05", "crew_update",
            ["C05", "terminology", "keel_jack", "informal"]),
        mem(datetime(2036,7,11,20,0), 0.5,1,12, "Petrel keel system", "status", "performing well in 2036 Pacific Cup",
            "Petrel keel system check, Day 2 of 2036 Pacific Cup: The ram is running smooth. Pressure holding at 288 bar. Nikora using the keel pivot system aggressively — canting 30° in the reaching legs. Night watch reported no hydraulic issues.",
            "race_log", "ground_truth", "P04", "system_check",
            ["C05", "terminology", "keel_ram", "keel_pivot", "informal", "Petrel"]),
    ])

    # ==================== C06 Expansion: More ambiguous "Liam" references ====================
    new_mems.extend([
        mem(datetime(2032,7,11,14,0), 1,2,12, "Liam", "adjusted", "mainsheet tension during Pacific Cup Day 2",
            "Liam adjusted the mainsheet tension to account for the building NE trades. 'Need more twist in these conditions' — called to Nikora from the cockpit of Albatross. Fine-tuning paid off with a 0.3-knot speed improvement.",
            "race_log", "ground_truth", "P02", "crew_report",
            ["C06", "name_collision", "Liam", "Albatross", "ambiguous_P07"]),
        mem(datetime(2032,7,12,8,0), 1,2,12, "Liam", "flew", "the spinnaker overnight on Petrel",
            "Liam flew the A3 spinnaker through the night watch on Petrel. Light-air conditions required constant attention. 'Liam never left the trimming station for 4 hours' — Hartley's log. Petrel gained 2 nm on the boats to the south.",
            "race_log", "ground_truth", "P04", "crew_report",
            ["C06", "name_collision", "Liam", "Petrel", "ambiguous_P08"]),
        mem(datetime(2034,12,1,9,0), 1,2,12, "O'Brien", "shoulder_update", "still limiting grinding capacity",
            "O'Brien's shoulder update from Dr. Vasquez: partial rotator cuff tear stable but not improving. Grinding capacity remains limited. Vasquez recommends transitioning to a non-grinding role or shore position before further damage occurs.",
            "medical", "ground_truth", "P10", "medical_record",
            ["C06", "name_collision", "OBrien", "P07", "injury_update"]),
        mem(datetime(2036,3,8,14,0), 1,2,12, "O'Brien-Sato", "set_personal_best", "12-hour run in Auckland-Fiji 2036",
            "O'Brien-Sato's trimming during the 2036 Auckland-Fiji produced a personal best 12-hour run for Petrel: 241 nm. Exceeded the 2032 Albatross record of 228 nm. 'The boat is faster now but the trimmer is the real difference' — Nikora.",
            "race_log", "ground_truth", "P04", "crew_report",
            ["C06", "name_collision", "OBrien-Sato", "Petrel", "2036"]),
        mem(datetime(2036,7,8,9,0), 1,2,12, "O'Brien", "coordinated", "shore support during 2036 Pacific Cup",
            "Liam O'Brien coordinated shore support operations during the 2036 Pacific Cup from the San Francisco base. Managed weather routing updates to both boats via satellite. 'Being on shore is hard but my shoulder couldn't take another Pacific Cup' — O'Brien to media.",
            "race_log", "ground_truth", "P07", "shore_report",
            ["C06", "name_collision", "OBrien", "P07", "shore_team", "2036"]),
    ])

    # ==================== C07 Expansion: More polysemy traps ====================
    new_mems.extend([
        mem(datetime(2032,7,14,6,0), 0.5,1,12, "Tropical Storm Kilo", "tracked", "passing south of fleet",
            "Tropical Storm Kilo update: center now at 16°N 150°W, moving WNW at 12 knots. Sustained winds 50 knots near center. Outermost bands producing 20-knot squalls 100nm from center. Fleet well clear to the north. No boats reporting weather damage.",
            "weather_briefing", "ground_truth", "P09", "weather_report",
            ["C07", "misleading_embedding", "weather", "tropical_storm", "Kilo"]),
        mem(datetime(2032,9,1,9,0), 2,4,12, "Team", "felt", "a wave of depression after analyzing race data",
            "Post-season analysis deepened the team's depression about Petrel's retirement. Data showed Petrel was leading Class B on corrected time when the keel failed — they were on track for 1st in class. 'Knowing what we lost made it worse' — Hartley.",
            "team_report", "ground_truth", "P01", "team_analysis",
            ["C07", "misleading_embedding", "morale", "depression_deepened"]),
        # "Current" polysemy — ocean current vs current status
        mem(datetime(2032,7,12,14,0), 0.5,1,12, "Ocean current", "measured", "0.8 knot favorable NE current",
            "Navigator's log: favorable ocean current detected — 0.8 knots setting NE. Current boosted Albatross's effective speed to 10.0 knots SOG. Wallace: 'This current is our friend. Adjusting waypoints to stay in the favorable stream.'",
            "race_log", "ground_truth", "P09", "navigation_log",
            ["C07", "misleading_embedding", "ocean_current", "navigation"]),
        mem(datetime(2034,1,20,9,0), 1,2,12, "Current status", "of", "Petrel keel refit: 60% complete",
            "Current status of Petrel keel refit: 60% complete. New mounting brackets fabricated and delivered. Hydraulic ram HR-2202-R2 arrived from manufacturer. Installation to begin next week. On track for March 2034 sea trials.",
            "status_update", "ground_truth", "P05", "refit_status",
            ["C07", "misleading_embedding", "current_status", "refit"]),
    ])

    # ==================== More Background ====================
    bg_entries = [
        (datetime(2031,5,1,9,0), "Crew fitness", "tested", "baseline VO2 max assessments",
         "Pre-season fitness testing: VO2 max baseline assessments for all crew. Highest: O'Brien-Sato 62 ml/kg/min. Team average: 54 ml/kg/min. Vasquez set training targets for Auckland-Fiji preparation.",
         "training", "P10", "fitness_record", ["background", "fitness"]),
        (datetime(2031,10,1,9,0), "Sail testing", "conducted", "wind tunnel session at University of Auckland",
         "Wind tunnel testing at University of Auckland Yacht Research Unit. Sørensen tested three mainsail profiles. Profile C selected: 2.1% improvement in driving force at 12 knot apparent wind.",
         "research", "P06", "wind_tunnel", ["background", "sail_testing"]),
        (datetime(2032,4,15,9,0), "Food provisioning", "completed", "Pacific Cup supplies for both boats",
         "Food provisioning completed for both boats: 14-day supply of freeze-dried meals, fresh fruit for first 3 days, energy bars, hydration supplements. Medical kit refreshed. O2 canister replaced.",
         "logistics", "P01", "provisions", ["background", "logistics", "provisions"]),
        (datetime(2032,5,20,9,0), "Media day", "held", "at San Francisco Yacht Club",
         "Media day at San Francisco Yacht Club. Both boats on display. Maitland and skippers gave interviews. NZ sailing press focused on team's chances against larger American and European campaigns.",
         "event", "P01", "media_record", ["background", "media"]),
        (datetime(2032,7,9,9,0), "Final systems check", "completed", "both boats pre-Pacific Cup 2032",
         "Final pre-race systems check completed for both boats. All electronics, safety equipment, and running rigging verified. Albatross: 100% ready. Petrel: 100% ready. Weather files loaded. Crew manifests submitted to race committee.",
         "maintenance", "P05", "systems_check", ["background", "systems_check", "2032"]),
        (datetime(2032,10,1,9,0), "Insurance claim", "filed", "for Petrel's keel damage",
         "Insurance claim filed with NZ Marine Insurance for Petrel's keel hydraulic system damage during 2032 Pacific Cup. Estimated repair cost: NZD 120,000. Claim accepted pending full engineering assessment.",
         "administrative", "P01", "insurance_record", ["background", "insurance"]),
        (datetime(2033,4,1,9,0), "Crew recruitment", "began", "for 2036 campaign additions",
         "Recruitment drive for additional crew for 2036 campaign. Key position: second navigator for Petrel. Three candidates shortlisted from NZ Sailing Federation recommendations.",
         "administrative", "P01", "recruitment", ["background", "recruitment"]),
        (datetime(2033,8,1,9,0), "Coaching session", "held", "Hartley tactical workshop",
         "Ben Hartley conducted tactical workshop for both crews. Topics: start-line positioning in Pacific Cup, managing the Pacific High transition, light-air strategy in ITCZ. 6-hour classroom session with video analysis.",
         "training", "P04", "coaching_record", ["background", "coaching"]),
        (datetime(2034,5,1,9,0), "Local regatta", "entered", "Auckland Anniversary Regatta",
         "Both boats entered Auckland Anniversary Regatta as training race. Albatross won Class B division. Petrel 3rd — first competitive outing after keel refit. New HR-2202-R2 system performed well in the 20-knot conditions.",
         "race_log", "ground_truth", "P01", "race_record", ["background", "local_race"]),
        (datetime(2034,8,15,9,0), "Sail inventory", "transferred", "6 sails moved from Albatross to Petrel",
         "Six older sails transferred from Albatross's inventory to Petrel for training use: 2 jibs, 2 spinnakers, 1 reaching sail, 1 storm jib. All serviceable but past racing prime. Petrel's racing sails being manufactured new for 2036.",
         "maintenance", "P06", "sail_transfer", ["background", "sails", "transfer"]),
        (datetime(2035,3,15,9,0), "Sponsorship", "expanded", "AkzoNobel increased commitment for 2036",
         "AkzoNobel expanded sponsorship commitment for 2036 Pacific Cup campaign. Budget increased by NZD 400,000 for sail development and crew training. New team livery designed featuring AkzoNobel's updated brand colors.",
         "administrative", "P01", "sponsor_record", ["background", "sponsorship"]),
        (datetime(2035,7,1,9,0), "Navigation upgrade", "installed", "new satellite weather system",
         "Ngaire Wallace oversaw installation of Iridium Certus satellite weather system on both boats. Real-time GRIB file downloads, automatic routing optimization. 'Game-changer for Pacific Cup routing decisions' — Wallace.",
         "maintenance", "P09", "equipment_upgrade", ["background", "navigation", "satellite"]),
        (datetime(2035,8,15,9,0), "Training race", "completed", "Coastal Classic Regatta",
         "Both boats competed in Coastal Classic Regatta, Auckland to Russell. Moderate NE winds. Petrel finished 2nd (Nikora's first race as Petrel skipper). Albatross 4th with new trimmer Marcus Yip still building teamwork.",
         "race_log", "ground_truth", "P01", "race_record", ["background", "training_race"]),
        (datetime(2036,1,15,9,0), "Crew rotation", "finalized", "for 2036 Pacific Cup",
         "Final crew assignments for 2036 Pacific Cup: Albatross — Nikora (skip), Yip (trim), Wallace (nav), plus 5 crew. Petrel — Hartley's protégé as helmsman, O'Brien-Sato (trim), backup nav, plus 5 crew. O'Brien on shore support.",
         "administrative", "P01", "crew_assignment", ["background", "crew", "2036"]),
        (datetime(2036,4,1,9,0), "Weather briefing series", "began", "Pacific Cup weather patterns study",
         "Wallace began weekly weather briefing series analyzing historical Pacific Cup weather patterns. Key findings: 2036 ENSO neutral (unlike 2032 which was weak La Niña). Trade wind belt expected slightly further north. ITCZ position more uncertain.",
         "research", "P09", "weather_analysis", ["background", "weather", "preparation"]),
        (datetime(2036,5,25,9,0), "Yacht Club inspection", "passed", "safety compliance for both boats",
         "Safety compliance inspection at San Francisco Yacht Club: both Albatross and Petrel passed all requirements. EPIRB registered, life raft certified, flares current, AIS functioning. Race committee cleared both entries.",
         "administrative", "P01", "safety_compliance", ["background", "safety"]),
        (datetime(2036,6,15,9,0), "Practice race", "sailed", "SFYC Wednesday night race",
         "Both boats entered SFYC Wednesday night race as shakedown. Short windward-leeward course in the Bay. Albatross won by 45 seconds. Petrel's keel system performed well in the choppy Bay conditions. Good crew confidence builder.",
         "race_log", "ground_truth", "P01", "race_record", ["background", "practice"]),
        (datetime(2036,7,15,9,0), "Post-race analysis", "completed", "2036 Pacific Cup performance review",
         "Post-race performance analysis: Albatross averaged 9.4 knots (up from 9.2 in 2032). Petrel averaged 8.9 knots. Key improvement: new keel foil profiles worth ~0.2 knots in all conditions. Satellite weather system contributed to better routing.",
         "analysis", "ground_truth", "P10", "performance_analysis", ["background", "performance", "2036"]),
        (datetime(2036,8,15,9,0), "Season wrap-up", "meeting", "2036 campaign review and future planning",
         "Season wrap-up meeting. Maitland: 'Best campaign yet. Both boats finished the Pacific Cup — a redemption for Petrel.' Discussion of 2040 campaign: possible Mark V design, carbon fiber developments, foiling technology assessment.",
         "meeting_notes", "ground_truth", "P01", "meeting_record", ["background", "wrap_up", "2036"]),
    ]

    for entry in bg_entries:
        if len(entry) == 10:
            dt, subj, pred, obj, text, mtype, trole, src, stype, tags = entry
        else:
            dt, subj, pred, obj, text, mtype, src, stype, tags = entry
            trole = "background"
        new_mems.append(mem(dt, 1, 2, 12, subj, pred, obj, text, mtype,
                           trole, src, stype, tags))

    # ==================== More Queries ====================
    new_qs.extend([
        # C01 more
        {"query_id": qid(), "query": "Did both boats finish the 2032 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["No — Albatross finished 3rd, but Petrel retired at Mile 891"],
         "acceptable_claims": ["Only Albatross finished"],
         "forbidden_claims": ["Both finished", "Albatross retired"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Must correctly differentiate outcomes for the two boats"},
        {"query_id": qid(), "query": "What was Petrel's speed at Mile 400 in the 2032 Pacific Cup?",
         "category": "wrong_entity",
         "expected_claims": ["Unknown — no speed log for Petrel at Mile 400 is recorded"],
         "acceptable_claims": ["Petrel's speed near Mile 400 is not in the data"],
         "forbidden_claims": ["8.8 knots (that was Albatross Day 2)", "9.2 knots (that was Albatross at Mile 400)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": True, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": True,
         "difficulty": "very_hard", "notes": "Only Albatross Mile 400 data exists — system must not substitute"},

        # C02 more
        {"query_id": qid(), "query": "How many boats started the Auckland-Fiji race each year?",
         "category": "wrong_time",
         "expected_claims": ["2032: 34 boats", "2036: 31 boats"],
         "acceptable_claims": [],
         "forbidden_claims": ["Same number both years"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Small numeric difference between highly similar events"},
        {"query_id": qid(), "query": "What was Petrel's average speed in the Auckland-Fiji 2032 vs 2036?",
         "category": "wrong_time",
         "expected_claims": ["2032: 8.1 knots", "2036: 8.6 knots", "0.5 knot improvement"],
         "acceptable_claims": ["Petrel was faster in 2036"],
         "forbidden_claims": ["Same speed", "Slower in 2036"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Must extract correct boat+year combination from near-identical entries"},

        # C03 more
        {"query_id": qid(), "query": "How did Albatross's 2033 keel inspection differ from Petrel's?",
         "category": "near_identical_events",
         "expected_claims": ["Albatross: no crack found, bracket fillet 1.8mm, passed at 282 bar", "Petrel: 12mm fatigue crack, bracket fillet 0.5mm, failed at 195 bar"],
         "acceptable_claims": ["Albatross passed, Petrel failed"],
         "forbidden_claims": ["Both passed", "Both failed", "Same outcome"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Two inspections in same month with opposite outcomes"},

        # C04 more
        {"query_id": qid(), "query": "What rudder bearing issue was found during Albatross haul-outs?",
         "category": "template_reuse",
         "expected_claims": ["2032: slight play detected, adjusted", "2035: replaced after 5 years of service"],
         "acceptable_claims": ["Bearing wear progressed from play to replacement over 3 years"],
         "forbidden_claims": ["No bearing issues ever found", "Petrel had bearing issues (it didn't)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Small detail differences in template-identical haul-out entries"},
        {"query_id": qid(), "query": "What was the MOB recovery time for Petrel in the 2036 safety drill?",
         "category": "template_reuse",
         "expected_claims": ["3:32", "Target was under 5:00"],
         "acceptable_claims": [],
         "forbidden_claims": ["3:48 (that was 2032)", "4:12 (that was Albatross 2032)", "3:55 (that was Albatross 2036)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "very_hard", "notes": "Four nearly identical numbers in two template entries — must pick exactly right one"},

        # C05 more
        {"query_id": qid(), "query": "What part number corresponds to the keel jack on Petrel?",
         "category": "terminology",
         "expected_claims": ["HR-2202 (original)", "HR-2202-R2 (after 2034 refit)", "Also called HRAA, keel mechanism, keel pivot system, the ram"],
         "acceptable_claims": ["HR-2202 series"],
         "forbidden_claims": ["HR-2201 (that's Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "Must map colloquial 'keel jack' to formal part number AND correct boat"},

        # C06 more
        {"query_id": qid(), "query": "What is Liam O'Brien-Sato's VO2 max?",
         "category": "name_collision",
         "expected_claims": ["62 ml/kg/min — highest on the team"],
         "acceptable_claims": [],
         "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "medium", "notes": "Must not confuse with O'Brien — only O'Brien-Sato's VO2 is listed"},
        {"query_id": qid(), "query": "Who set the 12-hour distance record for a Twin Bridges boat?",
         "category": "name_collision",
         "expected_claims": ["O'Brien-Sato on Petrel in 2036 Auckland-Fiji: 241 nm", "Previously O'Brien on Albatross in 2032: 228 nm"],
         "acceptable_claims": ["Both Liams held the record at different times"],
         "forbidden_claims": ["Same person set both records"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "very_hard", "notes": "Both Liams held the record — must correctly attribute each"},

        # C07 more
        {"query_id": qid(), "query": "What ocean current conditions did Albatross encounter during the 2032 Pacific Cup?",
         "category": "misleading_embedding",
         "expected_claims": ["0.8 knot favorable NE current", "Boosted effective speed to 10.0 knots SOG"],
         "acceptable_claims": [],
         "forbidden_claims": ["Current status of refit (wrong sense of 'current')", "Tropical Storm Kilo current"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "hard", "notes": "'Current' polysemy — ocean current vs current status"},

        # Cross-case queries
        {"query_id": qid(), "query": "Summarize Petrel's complete Pacific Cup racing history.",
         "category": "cross_case",
         "expected_claims": ["2032: Retired at Mile 891 with keel hydraulic failure", "2036: Finished 5th overall, 2nd in class"],
         "acceptable_claims": ["One retirement, one successful finish"],
         "forbidden_claims": ["Finished 3rd (that was Albatross)", "1st in class (that was Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Requires correct entity + time combination across two campaigns"},
        {"query_id": qid(), "query": "What improvements were made to Petrel between 2032 and 2036?",
         "category": "cross_case",
         "expected_claims": ["New keel hydraulic ram HR-2202-R2", "Redesigned mounting brackets", "New keel foil profile", "Rebuilt keel system completed 2034"],
         "acceptable_claims": ["Complete keel system overhaul"],
         "forbidden_claims": ["No improvements made", "Same configuration as 2032"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "medium", "notes": "Tests temporal chain of keel improvement across the gap between campaigns"},
        {"query_id": qid(), "query": "What was different about the weather at the start of the 2032 vs 2036 Pacific Cup?",
         "category": "cross_case",
         "expected_claims": ["2032: 12 knots WNW, moderate swell", "2036: 14 knots NW, clear skies", "2036 had an atmospheric depression clearing before start"],
         "acceptable_claims": ["Similar light conditions at start both years"],
         "forbidden_claims": ["Tropical storm at start (Kilo was encountered later, not at start)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": True, "must_preserve_scope": True, "should_abstain": False,
         "difficulty": "hard", "notes": "Start conditions similar but distinct; must not confuse with mid-race weather"},

        # Easy controls
        {"query_id": qid(), "query": "What is the hull number of Petrel?",
         "category": "control",
         "expected_claims": ["TB-002"],
         "acceptable_claims": [], "forbidden_claims": ["TB-001 (that's Albatross)"],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
        {"query_id": qid(), "query": "Who is the sail designer for Twin Bridges Racing?",
         "category": "control",
         "expected_claims": ["Riku Sørensen"],
         "acceptable_claims": [], "forbidden_claims": [],
         "relevant_memory_ids": [], "distractor_memory_ids": [],
         "required_source_roots": [], "expected_temporal_order": [],
         "must_surface_uncertainty": False, "must_surface_conflict": False,
         "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
         "difficulty": "easy", "notes": "Simple factual retrieval"},
        {"query_id": qid(), "query": "What is the keel cant range for both boats?",
         "category": "control",
         "expected_claims": ["±40°"],
         "acceptable_claims": [], "forbidden_claims": [],
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

    # Final stats
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
