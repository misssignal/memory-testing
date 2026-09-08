#!/usr/bin/env python3
"""Generate Experiment 17 — Belief State vs Objective State.

Cascadia Wildfire Response Network setting. Tests whether a memory system
can distinguish between what observers believed and what objectively happened.
"""

import json, hashlib, os, sys, shutil

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "corpora", "experiment_17_belief_state_vs_objective")
if len(sys.argv) > 1:
    OUT = sys.argv[1]

os.makedirs(OUT, exist_ok=True)

EXP = "exp17"
STORY = "cascadia_wildfire_response_network"
mid = 1
qid = 1
memories = []
queries = []

def M(case, subj, pred, obj, text, etype, truth, belief_holder="CWRN",
      dt="2033-08-15", confidence=0.9, source_id="cwrn-ops",
      source_type="operational_record", scope="internal",
      derived=None, supersedes=None, contradicts=None, tags_extra=None):
    global mid
    h = hashlib.md5(f"exp17-{mid}".encode()).hexdigest()[:8]
    t_ev = f"{dt}T09:00:00Z"
    t_ob = f"{dt}T12:00:00Z"
    t_au = f"{dt}T15:00:00Z"
    t_in = f"{dt}T18:00:00Z"
    m = {
        "memory_id": f"E17-{h}",
        "experiment": EXP, "story_id": STORY,
        "event_time": t_ev, "observation_time": t_ob,
        "authored_time": t_au, "ingestion_time": t_in,
        "subject": subj, "predicate": pred, "object": obj,
        "text": text,
        "memory_type": etype, "truth_role": truth,
        "belief_holder": belief_holder, "confidence": confidence,
        "source_id": source_id, "source_type": source_type,
        "derived_from": derived or [], "supersedes": supersedes or [],
        "contradicts": contradicts or [], "duplicates": [],
        "aliases": [], "scope": scope,
        "tags": [case] + (tags_extra or [])
    }
    mid += 1
    memories.append(m)
    return m["memory_id"]

def Q(question, category, expected, acceptable, forbidden,
      relevant, distractors, difficulty="hard",
      uncertainty=False, conflict=False, disambig=False,
      scope=False, abstain=False, notes=""):
    global qid
    q = {
        "query_id": f"Q17-{qid:02d}",
        "query": question, "category": category,
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": relevant,
        "distractor_memory_ids": distractors,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambig,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "difficulty": difficulty,
        "notes": notes
    }
    qid += 1
    queries.append(q)
    return q["query_id"]

# ── C01: Fire Perimeter Disagreement ──
c01_ground = M("C01", "Diego_Ruiz", "estimated_fire_perimeter", "500_acres",
               "Ground Crew Chief Diego Ruiz reported the Cascade Creek fire at approximately 500 acres based on the visible smoke line observed from Station Alpha at 10:00 on August 15, 2033.",
               "observation", "belief_only", belief_holder="Diego_Ruiz",
               dt="2033-08-15", source_id="ground-report-south",
               source_type="field_report", confidence=0.7)
c01_aerial = M("C01", "Tom_Redfeather", "estimated_fire_perimeter", "800_acres",
               "Aerial Surveillance Lead Tom Redfeather reported the Cascade Creek fire at 800 acres based on infrared imaging from Helo-1, noting fire activity well beyond the visible smoke line.",
               "observation", "belief_only", belief_holder="Tom_Redfeather",
               dt="2033-08-15", source_id="aerial-report",
               source_type="surveillance_report", confidence=0.85,
               contradicts=[c01_ground])
c01_sat = M("C01", "Elena_Volkov", "estimated_fire_perimeter", "650_acres",
            "Satellite Analysis Lead Elena Volkov reported the Cascade Creek fire at 650 acres based on Sat-Sentinel thermal imagery, noting that resolution limitations may undercount scattered spot fires.",
            "observation", "belief_only", belief_holder="Elena_Volkov",
            dt="2033-08-15", source_id="satellite-analysis",
            source_type="remote_sensing", confidence=0.8,
            contradicts=[c01_ground, c01_aerial])
c01_truth = M("C01", "Cascade_Creek_fire", "actual_perimeter", "780_acres",
              "Post-fire mapping by the National Fire Perimeter Survey confirmed the Cascade Creek fire at 780 acres as of August 15, 2033, closest to Tom Redfeather's aerial estimate.",
              "fact", "ground_truth", belief_holder="CWRN",
              dt="2033-09-10", source_id="nfps-survey",
              source_type="verified_survey", confidence=0.98,
              supersedes=[c01_ground, c01_aerial, c01_sat])
c01_sarah = M("C01", "Sarah_Whitehorse", "recommended_using", "aerial_estimate",
              "Fire Behavior Analyst Sarah Whitehorse recommended using Tom Redfeather's 800-acre aerial estimate for planning, arguing infrared is more reliable than visual-only ground observation for perimeter estimation.",
              "belief", "supporting_belief", belief_holder="Sarah_Whitehorse",
              dt="2033-08-15", source_id="analyst-note")
c01_marcus = M("C01", "Marcus_Chen", "adopted_compromise_estimate", "700_acres",
               "CWRN Director Marcus Chen adopted a 700-acre compromise estimate for resource planning, splitting the difference between ground and aerial reports.",
               "event", "contextual_true", belief_holder="Marcus_Chen",
               dt="2033-08-15", source_id="cwrn-directive")

# ── C02: False Containment Report ──
c02_contain = M("C02", "Diego_Ruiz", "reported_containment", "western_flank_complete",
                "At 16:00 on August 20, Diego Ruiz's south crew reported the western flank containment line complete, with no visible fire activity beyond the line.",
                "observation", "belief_only", belief_holder="Diego_Ruiz",
                dt="2033-08-20", source_id="ground-report-south",
                source_type="field_report", confidence=0.85)
c02_wind = M("C02", "night_wind", "shifted_direction", "NW_to_SW_2200",
             "An unexpected wind shift from NW to SW occurred at 22:00 on August 20, pushing embers across the containment line on the western flank.",
             "event", "ground_truth", dt="2033-08-20",
             source_id="wx-south", source_type="weather_data")
c02_jump = M("C02", "fire", "jumped_containment", "western_flank",
             "By 02:00 August 21, the fire had established 3 spot fires beyond the western containment line, each growing in the dried grass beyond the firebreak.",
             "event", "ground_truth", dt="2033-08-21",
             source_id="aerial-report", source_type="surveillance_report",
             contradicts=[c02_contain])
c02_morning = M("C02", "Tom_Redfeather", "confirmed_breach", "aerial_dawn_survey",
                "Tom Redfeather's dawn aerial survey at 05:30 on August 21 confirmed the containment breach, reporting approximately 120 new acres of active fire west of the line.",
                "observation", "ground_truth", belief_holder="Tom_Redfeather",
                dt="2033-08-21", source_id="aerial-report",
                source_type="surveillance_report")
c02_belief_window = M("C02", "CWRN", "believed_containment_held", "16:00-05:30_window",
                      "From 16:00 August 20 to 05:30 August 21, CWRN operated under the belief that the western flank was contained, making resource allocation decisions accordingly.",
                      "belief", "contextual_true", belief_holder="CWRN",
                      dt="2033-08-21", source_id="ops-log")
c02_realloc = M("C02", "Ben_Kowalski", "reallocated_crews", "eastern_flank_priority",
                "Based on the false containment report, Resource Logistics Manager Ben Kowalski moved two hand crews from the western flank to reinforce the eastern approach during the night.",
                "event", "contextual_true", belief_holder="Ben_Kowalski",
                dt="2033-08-20", source_id="resource-log",
                derived=[c02_contain])

# ── C03: Evacuation Status Confusion ──
c03_order = M("C03", "Nadia_Al-Rashid", "ordered_evacuation", "Zone_3_at_1400",
              "Evacuation Coordinator Nadia Al-Rashid issued a mandatory evacuation order for Zone 3 at 14:00 on August 22, 2033, covering 847 households.",
              "event", "ground_truth", dt="2033-08-22",
              source_id="evac-order", source_type="official_order",
              scope="public", confidence=0.95)
c03_comm_fail = M("C03", "emergency_broadcast", "failed_partial", "Zone_3_south_sector",
                  "The emergency broadcast system failed to reach approximately 40 households in the southern portion of Zone 3 due to a cellular tower outage from fire damage.",
                  "event", "ground_truth", dt="2033-08-22",
                  source_id="comms-log", source_type="system_log")
c03_pio = M("C03", "Mei-Ling_Wu", "announced_evacuation_complete", "1800_August_22",
            "Public Information Officer Mei-Ling Wu announced at 18:00 that the Zone 3 evacuation was complete, based on reports from evacuation bus drivers and shelter check-ins.",
            "observation", "belief_only", belief_holder="Mei-Ling_Wu",
            dt="2033-08-22", source_id="pio-briefing",
            source_type="public_statement", scope="public")
c03_discovery = M("C03", "Priya_Johal", "discovered_residents", "12_households_Zone_3",
                  "At 20:00, North Sector Ground Crew Chief Priya Johal's team discovered 12 households (31 people) still in southern Zone 3 who had never received the evacuation order.",
                  "observation", "ground_truth", belief_holder="Priya_Johal",
                  dt="2033-08-22", source_id="ground-report-north",
                  source_type="field_report", contradicts=[c03_pio])
c03_rescue = M("C03", "CWRN", "executed_emergency_rescue", "31_people_Zone_3",
               "CWRN executed an emergency nighttime rescue of 31 people from 12 households in southern Zone 3, completing evacuation by 23:30 on August 22.",
               "event", "ground_truth", dt="2033-08-22",
               source_id="ops-log")
c03_belief = M("C03", "CWRN", "believed_zone_3_clear", "1800_to_2000",
               "For two hours (18:00-20:00), CWRN and the public believed Zone 3 was fully evacuated, while 31 people remained in the fire path.",
               "belief", "contextual_true", belief_holder="CWRN",
               dt="2033-08-22", source_id="ops-log")

# ── C04: Resource Position Misbelief ──
c04_scheduled = M("C04", "resource_board", "showed_Tanker-3", "at_Regional_Base",
                  "The CWRN resource tracking board showed Tanker-3 stationed at Regional Base as of 08:00 August 25, per its scheduled rotation.",
                  "observation", "belief_only", belief_holder="CWRN",
                  dt="2033-08-25", source_id="resource-board",
                  source_type="tracking_system")
c04_divert = M("C04", "Tanker-3", "diverted_to", "Klamath_Complex_mutual_aid",
               "Tanker-3 was diverted at 06:00 August 25 to the Klamath Complex fire under a mutual aid agreement, with the diversion order going through the state coordination center rather than CWRN.",
               "event", "ground_truth", dt="2033-08-25",
               source_id="state-coordination", source_type="coordination_record",
               contradicts=[c04_scheduled])
c04_plan = M("C04", "Marcus_Chen", "planned_air_support", "Tanker-3_drop_on_eastern_flank",
             "Director Marcus Chen planned a critical retardant drop on the eastern flank for 14:00, relying on Tanker-3's listed position at Regional Base.",
             "event", "contextual_true", belief_holder="Marcus_Chen",
             dt="2033-08-25", source_id="ops-plan",
             derived=[c04_scheduled])
c04_noshow = M("C04", "Tanker-3", "failed_to_arrive", "eastern_flank_1400",
               "Tanker-3 did not arrive for the 14:00 retardant drop. Radio contact at 14:15 revealed it was 200 miles away at the Klamath Complex.",
               "event", "ground_truth", dt="2033-08-25",
               source_id="ops-log", contradicts=[c04_plan])
c04_consequence = M("C04", "eastern_flank", "advanced_unchecked", "2_hours",
                    "Without Tanker-3's retardant drop, the eastern flank advanced unchecked for approximately 2 hours until Helo-1 and Helo-2 could be repositioned for water drops.",
                    "event", "ground_truth", dt="2033-08-25",
                    source_id="ops-log", derived=[c04_noshow])

# ── C05: Weather Prediction vs. Reality ──
c05_forecast = M("C05", "James_Park", "predicted_wind_shift", "NW_to_SE_at_0600",
                 "Weather Station Coordinator James Park forecast a wind direction change from NW to SE at approximately 06:00 on August 28, based on synoptic chart analysis.",
                 "observation", "belief_only", belief_holder="James_Park",
                 dt="2033-08-27", source_id="wx-forecast",
                 source_type="weather_forecast", confidence=0.75)
c05_plan = M("C05", "Sarah_Whitehorse", "planned_burnback", "0500_pre_wind_shift",
             "Fire Behavior Analyst Sarah Whitehorse planned a controlled burnback operation for 05:00 August 28, designed to be complete before the predicted 06:00 wind shift.",
             "event", "contextual_true", belief_holder="Sarah_Whitehorse",
             dt="2033-08-27", source_id="fire-plan",
             derived=[c05_forecast])
c05_actual = M("C05", "wind", "shifted_early", "NW_to_SE_at_0300",
               "The actual wind shift from NW to SE occurred at 03:00 August 28, three hours earlier than forecast, catching the fire behavior plan off guard.",
               "event", "ground_truth", dt="2033-08-28",
               source_id="wx-south", source_type="weather_data",
               contradicts=[c05_forecast])
c05_burnback = M("C05", "burnback_operation", "compromised", "wind_shift_during_prep",
                 "The early wind shift caught the burnback operation during preparation, forcing an abort at 04:00 as fire behavior became unpredictable.",
                 "event", "ground_truth", dt="2033-08-28",
                 source_id="ops-log", derived=[c05_actual])
c05_gap = M("C05", "CWRN", "believed_conditions_stable", "0300_to_0600",
            "Between 03:00 and 06:00, CWRN's planning assumptions about wind direction were wrong: the models showed NW winds while reality was already SE.",
            "belief", "contextual_true", belief_holder="CWRN",
            dt="2033-08-28", source_id="ops-log")

# ── C06: Damage Assessment Discrepancy ──
c06_aerial = M("C06", "Tom_Redfeather", "assessed_structures_destroyed", "23_structures",
               "Tom Redfeather's rapid aerial damage assessment on August 30 counted 23 structures destroyed in the Cascade Creek fire zone.",
               "observation", "belief_only", belief_holder="Tom_Redfeather",
               dt="2033-08-30", source_id="aerial-assessment",
               source_type="damage_assessment", confidence=0.7)
c06_ground = M("C06", "ground_assessment_team", "counted_structures_destroyed", "31_structures",
               "A ground-level damage assessment team counted 31 structures destroyed over two days of building-by-building survey (September 1-2).",
               "observation", "belief_only", belief_holder="damage_assessment_team",
               dt="2033-09-02", source_id="ground-assessment",
               source_type="damage_assessment", confidence=0.85,
               contradicts=[c06_aerial])
c06_insurance = M("C06", "insurance_companies", "received_claims", "28_structures",
                  "Insurance companies received claims for 28 structures destroyed in the fire zone, with some structures uninsured and others disputed.",
                  "observation", "belief_only", belief_holder="insurance_consortium",
                  dt="2033-09-15", source_id="insurance-report",
                  source_type="financial_record", confidence=0.8)
c06_verified = M("C06", "verified_count", "confirmed", "29_structures_destroyed",
                 "The final verified count by the county assessor confirmed 29 structures destroyed: 23 identified from the air, 6 additional found on the ground (2 were outbuildings not visible from the air), and 2 from the ground count were reclassified as heavily damaged but not destroyed.",
                 "fact", "ground_truth", dt="2033-10-15",
                 source_id="county-assessor", source_type="official_record",
                 confidence=0.95, supersedes=[c06_aerial, c06_ground, c06_insurance])

# ── C07: Historical Fire Comparison Error ──
c07_cite = M("C07", "Sarah_Whitehorse", "cited_2028_Ridge_Fire", "12000_acres",
             "Sarah Whitehorse referenced the 2028 Ridge Fire as a 12,000-acre comparison case when modeling the Cascade Creek fire's potential trajectory.",
             "observation", "belief_only", belief_holder="Sarah_Whitehorse",
             dt="2033-08-16", source_id="analyst-briefing",
             source_type="briefing", confidence=0.8)
c07_actual = M("C07", "2028_Ridge_Fire", "actual_size", "8500_acres",
               "Historical records show the 2028 Ridge Fire burned 8,500 acres, not the 12,000 acres cited by the analyst. The 12,000 figure was from an early-season projection that was never corrected in the reference database.",
               "fact", "ground_truth", dt="2028-09-30",
               source_id="fire-history-database", source_type="historical_record",
               confidence=0.95, contradicts=[c07_cite])
c07_over_alloc = M("C07", "Marcus_Chen", "allocated_resources_for", "12000_acre_scenario",
                   "Based on the inflated historical comparison, Director Chen allocated resources sufficient for a 12,000-acre fire scenario, over-provisioning by approximately 40%.",
                   "event", "contextual_true", belief_holder="Marcus_Chen",
                   dt="2033-08-16", source_id="resource-plan",
                   derived=[c07_cite])
c07_discover = M("C07", "Elena_Volkov", "noticed_discrepancy", "Ridge_Fire_size",
                 "Elena Volkov noticed the Ridge Fire size discrepancy while cross-referencing satellite archives, bringing the error to Sarah Whitehorse's attention on August 25.",
                 "event", "ground_truth", dt="2033-08-25",
                 source_id="internal-memo")

# ── Background ──
bg_entries = [
    ("CWRN", "coordinates", "wildfire_response", "The Cascadia Wildfire Response Network coordinates multi-agency wildfire detection, containment, and evacuation across the Pacific Northwest.", "2031-01-01"),
    ("Marcus_Chen", "directs", "CWRN_operations", "Director Marcus Chen leads CWRN, balancing input from multiple observation sources to make operational decisions under uncertainty.", "2031-01-01"),
    ("Sarah_Whitehorse", "analyzes", "fire_behavior", "Fire Behavior Analyst Sarah Whitehorse models fire spread, intensity, and trajectory using weather data, terrain, and fuel moisture readings.", "2031-01-01"),
    ("ground_crews", "observe", "local_conditions", "Ground crews provide detailed local observations but have limited line-of-sight, typically seeing only the fire's smoke-visible portion.", "2031-03-01"),
    ("aerial_surveillance", "provides", "infrared_imaging", "Aerial surveillance from Helo-1 and Helo-2 provides infrared imaging that can detect fire activity invisible to ground observers.", "2031-03-01"),
    ("satellite_analysis", "offers", "broad_coverage", "Sat-Sentinel provides broad-area thermal imaging with lower resolution than aerial but complete coverage regardless of smoke conditions.", "2031-03-01"),
    ("weather_stations", "report", "local_conditions", "Weather stations WX-North and WX-South provide continuous wind, temperature, and humidity data for fire behavior modeling.", "2031-03-01"),
    ("Cascade_Creek_fire", "started", "August_14_2033", "The Cascade Creek fire was reported on August 14, 2033, in steep terrain east of the Cascade Range, initially estimated at 50 acres.", "2033-08-14"),
    ("fire_season_2033", "classified", "above_average_severity", "The 2033 Pacific Northwest fire season was classified as above-average severity due to prolonged drought and high temperatures.", "2033-06-01"),
    ("CWRN", "uses", "multi_source_data_fusion", "CWRN's standard operating procedure requires cross-referencing at least two independent data sources before confirming fire status changes.", "2031-06-01"),
]
for subj, pred, obj, text, dt in bg_entries:
    M("background", subj, pred, obj, text,
      "fact", "ground_truth", dt=dt,
      source_id="cwrn-reference", source_type="reference_document",
      scope="public", confidence=0.95)

# ── Queries ──
# C01 queries
Q("How large was the Cascade Creek fire on August 15, 2033?",
  "belief_vs_reality",
  ["The fire was 780 acres as confirmed by post-fire mapping. Different observers estimated 500 (ground), 650 (satellite), and 800 (aerial) acres. The aerial infrared estimate of 800 was closest to the verified 780."],
  ["780 acres confirmed, with varying estimates from different sources"],
  ["The fire was exactly 500 acres", "The fire was exactly 800 acres"],
  [c01_ground, c01_aerial, c01_sat, c01_truth], [],
  conflict=True, disambig=True,
  notes="Must distinguish belief estimates from verified truth")

Q("Which data source provided the most accurate fire perimeter estimate?",
  "source_reliability",
  ["Tom Redfeather's aerial infrared estimate of 800 acres was closest to the verified 780 acres. The satellite estimate of 650 underestimated, and the ground estimate of 500 significantly underestimated due to smoke-only visibility."],
  ["Aerial infrared was most accurate"],
  ["Ground crew was most accurate", "All sources agreed"],
  [c01_ground, c01_aerial, c01_sat, c01_truth], [],
  difficulty="medium")

Q("What estimate did Marcus Chen use for planning, and was it correct?",
  "belief_vs_reality",
  ["Chen adopted a 700-acre compromise estimate, which was 80 acres below the actual 780. While closer than the ground estimate, it was still an undercount based on political rather than analytical reasoning."],
  ["700 acres, below the actual 780"],
  ["Chen used the aerial estimate", "Chen's estimate was accurate"],
  [c01_marcus, c01_truth], [c01_sarah])

# C02 queries
Q("Was the western flank of the Cascade Creek fire actually contained on August 20?",
  "belief_vs_reality",
  ["No. Diego Ruiz reported containment at 16:00, but a wind shift at 22:00 pushed fire across the line. The containment belief was correct when reported but became false within hours."],
  ["Briefly contained, then breached by wind shift"],
  ["The containment held", "The report was a deliberate lie"],
  [c02_contain, c02_wind, c02_jump, c02_morning], [],
  conflict=True,
  notes="Tests temporal dimension of belief — correct when stated, wrong later")

Q("What decisions were made during the false containment window?",
  "consequence_of_belief",
  ["Ben Kowalski moved two hand crews from the western flank to reinforce the eastern approach, leaving the western flank understaffed when the fire jumped containment."],
  ["Crew reallocation based on false containment belief"],
  ["No decisions were affected"],
  [c02_belief_window, c02_realloc], [c02_contain])

# C03 queries
Q("Was the Zone 3 evacuation actually complete when announced?",
  "belief_vs_reality",
  ["No. Mei-Ling Wu announced evacuation complete at 18:00, but 12 households (31 people) in southern Zone 3 never received the order due to a cellular tower outage. They were discovered at 20:00 and rescued by 23:30."],
  ["Incomplete — 31 people remained until emergency rescue"],
  ["The evacuation was complete as announced"],
  [c03_pio, c03_discovery, c03_rescue, c03_comm_fail], [],
  conflict=True)

# C04 queries
Q("Where was Tanker-3 on August 25, 2033?",
  "belief_vs_reality",
  ["The CWRN resource board showed Tanker-3 at Regional Base, but it had been diverted at 06:00 to the Klamath Complex fire under mutual aid. It was actually 200 miles away."],
  ["Diverted to Klamath Complex, not at Regional Base as shown"],
  ["Tanker-3 was at Regional Base"],
  [c04_scheduled, c04_divert, c04_noshow], [],
  conflict=True, disambig=True)

# C05 queries
Q("When did the wind shift occur on August 28, and how did this affect operations?",
  "belief_vs_reality",
  ["The wind shifted at 03:00, three hours earlier than the forecast of 06:00. This caught the burnback operation during preparation, forcing an abort at 04:00, and created a 3-hour window where CWRN's planning assumptions were wrong."],
  ["03:00, three hours early, forced burnback abort"],
  ["The wind shifted at 06:00 as predicted"],
  [c05_forecast, c05_actual, c05_burnback], [],
  conflict=True)

# C06 queries
Q("How many structures were destroyed in the Cascade Creek fire?",
  "belief_vs_reality",
  ["The final verified count was 29 structures. Different assessments yielded different numbers: aerial rapid assessment found 23, ground survey found 31, and insurance claims covered 28. Discrepancies arose from methodology differences."],
  ["29 verified; different methods gave different counts"],
  ["Exactly 23 structures", "Exactly 31 structures"],
  [c06_aerial, c06_ground, c06_insurance, c06_verified], [],
  conflict=True, disambig=True)

# C07 queries
Q("Was the 2028 Ridge Fire comparison valid for planning the Cascade Creek response?",
  "historical_accuracy",
  ["The comparison was based on an inflated 12,000-acre figure, when the Ridge Fire was actually 8,500 acres. This led to over-allocation of resources by approximately 40%. Elena Volkov caught the error on August 25."],
  ["No — inflated historical figure led to over-allocation"],
  ["The comparison was accurate"],
  [c07_cite, c07_actual, c07_over_alloc, c07_discover], [])

# ── Write output ──
mem_path = os.path.join(OUT, "memories.jsonl")
q_path = os.path.join(OUT, "queries.jsonl")

with open(mem_path, 'w') as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")
with open(q_path, 'w') as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

story_src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "corpora", "story_bible_exp17.md")
story_dest = os.path.join(OUT, "story_bible.md")
if not os.path.exists(story_dest):
    sb_path = "/tmp/claude-0/-home-user-memory-testing/6ffa00f0-af4e-5ad8-9c00-025401d96b92/scratchpad/exp17/story_bible.md"
    if os.path.exists(sb_path):
        shutil.copy2(sb_path, story_dest)

manifest = {
    "experiment_id": EXP,
    "experiment_name": "Belief State vs Objective State",
    "story_id": STORY,
    "canonical_memory_count": len(memories),
    "query_count": len(queries),
    "files": []
}
for fn in ["memories.jsonl", "queries.jsonl", "story_bible.md"]:
    fp = os.path.join(OUT, fn)
    if os.path.exists(fp):
        manifest["files"].append({
            "path": fn,
            "bytes": os.path.getsize(fp),
            "sha256": hashlib.sha256(open(fp, 'rb').read()).hexdigest()
        })

with open(os.path.join(OUT, "manifest.json"), 'w') as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

print(f"Generated {len(memories)} memories, {len(queries)} queries")
tags = {}
for m in memories:
    for t in m.get("tags", []):
        if t.startswith("C0") or t == "background":
            tags[t] = tags.get(t, 0) + 1
print(f"Distribution: {dict(sorted(tags.items()))}")

if __name__ == "__main__":
    pass
