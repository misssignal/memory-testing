#!/usr/bin/env python3
"""Exp 17 round-1 expansion — target ~120 memories, ~35 queries."""

import json, hashlib, os, sys

def main():
    d = sys.argv[1]
    mem_path = os.path.join(d, "memories.jsonl")
    q_path = os.path.join(d, "queries.jsonl")
    manifest_path = os.path.join(d, "manifest.json")

    with open(mem_path) as f:
        memories = [json.loads(l) for l in f if l.strip()]
    with open(q_path) as f:
        queries = [json.loads(l) for l in f if l.strip()]
    with open(manifest_path) as f:
        manifest = json.load(f)

    mid_counter = len(memories) + 1
    qid_counter = len(queries) + 1
    EXP = "exp17"
    STORY = "cascadia_wildfire_response_network"

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_mems = []
    new_qs = []
    mem_by_id = {m["memory_id"]: m for m in memories}

    def M(case, subj, pred, obj, text, etype, truth, belief_holder="CWRN",
          dt="2033-08-15", confidence=0.9, source_id="cwrn-ops",
          source_type="operational_record", scope="internal",
          derived=None, supersedes=None, contradicts=None, tags_extra=None):
        nonlocal mid_counter
        h = hashlib.md5(f"exp17-r1-{mid_counter}".encode()).hexdigest()[:8]
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
        mid_counter += 1
        new_mems.append(m)
        return m["memory_id"]

    def Q(question, category, expected, acceptable, forbidden,
          relevant, distractors, difficulty="hard",
          uncertainty=False, conflict=False, disambig=False,
          scope=False, abstain=False, notes=""):
        nonlocal qid_counter
        q = {
            "query_id": f"Q17-{qid_counter:02d}",
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
        qid_counter += 1
        new_qs.append(q)
        return q["query_id"]

    # ── C01 expansion: fire perimeter ──
    c01_diego_method = M("C01", "Diego_Ruiz", "used_method", "visual_smoke_line_estimation",
        "Diego Ruiz's 500-acre estimate was based on walking the visible smoke perimeter and using GPS waypoints, a method limited to smoke-visible fire only.",
        "observation", "contextual_true", belief_holder="Diego_Ruiz",
        dt="2033-08-15", source_id="ground-report-south", source_type="field_report")
    c01_ir_detail = M("C01", "Helo-1_FLIR", "detected", "subsurface_fire_beyond_smoke",
        "Helo-1's forward-looking infrared camera detected active combustion in 280 acres of forest floor not producing visible smoke, explaining the gap between ground and aerial estimates.",
        "observation", "ground_truth", belief_holder="Tom_Redfeather",
        dt="2033-08-15", source_id="flir-imagery", source_type="surveillance_report")
    c01_sat_res = M("C01", "Sat-Sentinel", "had_resolution_limit", "30m_pixel_size",
        "Sat-Sentinel's 30-meter pixel resolution caused it to miss narrow fire fingers less than 30 meters wide, explaining the satellite undercount relative to aerial.",
        "fact", "ground_truth", dt="2033-08-15", source_id="satellite-tech-spec",
        source_type="technical_document")
    c01_sarah_memo = M("C01", "Sarah_Whitehorse", "wrote_analysis", "observation_source_reliability",
        "Sarah Whitehorse authored a post-incident memo ranking observation reliability: FLIR aerial (±5%) > satellite thermal (±15%) > ground visual (±30%) for perimeter estimation.",
        "belief", "supporting_belief", belief_holder="Sarah_Whitehorse",
        dt="2033-09-15", source_id="analyst-memo", source_type="internal_memo")
    c01_next_day = M("C01", "Cascade_Creek_fire", "grew_to", "1200_acres_August_16",
        "By August 16, the Cascade Creek fire had grown to approximately 1,200 acres, with all three observation sources showing growth consistent with the verified 780-acre baseline.",
        "observation", "ground_truth", dt="2033-08-16", source_id="ops-log")

    # ── C02 expansion: false containment ──
    c02_line_specs = M("C02", "containment_line", "specifications", "8_foot_wide_mineral_soil",
        "The western flank containment line was 8 feet wide cut to mineral soil, meeting standard specifications for the fuel type but inadequate for ember transport in 25+ mph winds.",
        "fact", "ground_truth", dt="2033-08-20", source_id="fire-line-report", source_type="field_report")
    c02_diego_check = M("C02", "Diego_Ruiz", "walked_full_line", "1500_August_20",
        "Diego Ruiz personally walked the full 2.3-mile western containment line at 15:00 before reporting it complete, finding no active fire within 100 feet of the line.",
        "observation", "contextual_true", belief_holder="Diego_Ruiz",
        dt="2033-08-20", source_id="ground-report-south", source_type="field_report")
    c02_ember = M("C02", "embers", "transported", "300_feet_across_line",
        "Wind-driven embers were transported up to 300 feet across the containment line during the 22:00 wind shift, far exceeding the 8-foot line width.",
        "event", "ground_truth", dt="2033-08-20", source_id="fire-investigation",
        source_type="investigation_report")
    c02_night_crew = M("C02", "night_patrol", "missed_spot_fires", "reduced_visibility",
        "The skeleton night patrol crew on the western flank missed the initial spot fires due to dense smoke reducing visibility to under 50 feet.",
        "observation", "ground_truth", dt="2033-08-21", source_id="after-action-report",
        source_type="investigation_report")
    c02_cost = M("C02", "containment_breach", "cost", "additional_400_acres",
        "The containment breach ultimately cost an additional 400 acres of burned forest and $2.3M in additional suppression costs before the western flank was re-contained.",
        "fact", "ground_truth", dt="2033-08-25", source_id="fire-cost-report",
        source_type="financial_record")
    c02_review = M("C02", "after_action_review", "found", "containment_report_premature",
        "The after-action review concluded that the containment report was premature — the line was physically complete but should not have been reported as 'contained' without aerial confirmation and weather forecast review.",
        "event", "ground_truth", dt="2033-09-20", source_id="after-action-report",
        source_type="investigation_report")

    # ── C03 expansion: evacuation ──
    c03_bus_drivers = M("C03", "evacuation_bus_drivers", "reported", "all_stops_completed",
        "Evacuation bus drivers reported completing all scheduled stops in Zone 3 by 17:00, unaware that some households in the southern sector never received notification to be at the stops.",
        "observation", "belief_only", belief_holder="bus_drivers",
        dt="2033-08-22", source_id="transport-log", source_type="operational_record")
    c03_shelter = M("C03", "Red_Cross_shelter", "counted", "816_evacuees_from_Zone_3",
        "The Red Cross shelter logged 816 evacuees from Zone 3 by 17:30, which Mei-Ling Wu compared against the 847-household count, noting it was close enough to confirm completion.",
        "observation", "belief_only", belief_holder="Mei-Ling_Wu",
        dt="2033-08-22", source_id="shelter-log", source_type="humanitarian_record",
        confidence=0.7)
    c03_tower = M("C03", "cell_tower_south", "damaged", "fire_proximity",
        "The southern Zone 3 cell tower was damaged by fire proximity at approximately 12:30, two hours before the evacuation order, cutting wireless emergency alert delivery to 40 households.",
        "event", "ground_truth", dt="2033-08-22", source_id="telecom-report",
        source_type="infrastructure_report")
    c03_door = M("C03", "Priya_Johal", "conducted_door_to_door", "southern_Zone_3",
        "Priya Johal's crew conducted door-to-door checks in southern Zone 3 as part of a fire perimeter survey, not specifically looking for un-evacuated residents but finding them.",
        "observation", "ground_truth", belief_holder="Priya_Johal",
        dt="2033-08-22", source_id="ground-report-north", source_type="field_report")
    c03_review = M("C03", "CWRN", "revised_evacuation_protocol", "multi_channel_confirmation",
        "Following the Zone 3 incident, CWRN revised its evacuation protocol to require confirmation via at least two independent communication channels before declaring an area cleared.",
        "event", "ground_truth", dt="2033-10-01", source_id="protocol-update",
        source_type="policy_document")
    c03_mei_apology = M("C03", "Mei-Ling_Wu", "issued_correction", "evacuation_announcement",
        "Mei-Ling Wu issued a public correction on August 23 acknowledging that the evacuation completion announcement was premature and that 31 people required emergency rescue.",
        "event", "ground_truth", belief_holder="Mei-Ling_Wu",
        dt="2033-08-23", source_id="pio-correction", source_type="public_statement",
        scope="public")

    # ── C04 expansion: resource position ──
    c04_state_center = M("C04", "state_coordination_center", "notified", "CWRN_email_0615",
        "The state coordination center sent an email notification of Tanker-3's diversion to CWRN at 06:15, but it went to a generic inbox that wasn't monitored during the overnight shift.",
        "event", "ground_truth", dt="2033-08-25", source_id="email-log",
        source_type="communication_record")
    c04_ben_check = M("C04", "Ben_Kowalski", "checked_resource_board", "0800_no_update",
        "Ben Kowalski checked the resource tracking board at 08:00 and saw Tanker-3 listed at Regional Base, not knowing the board hadn't been updated with the mutual aid diversion.",
        "observation", "belief_only", belief_holder="Ben_Kowalski",
        dt="2033-08-25", source_id="resource-log", source_type="operational_record")
    c04_helo_sub = M("C04", "Helo-1_and_Helo-2", "substituted_for", "Tanker-3",
        "Helo-1 and Helo-2 were repositioned from reconnaissance to water-drop duty to partially substitute for the absent Tanker-3, but their smaller capacity (700 gallons vs 3,000) was insufficient.",
        "event", "ground_truth", dt="2033-08-25", source_id="ops-log")
    c04_protocol = M("C04", "CWRN", "revised_tracking", "real_time_GPS_required",
        "After the Tanker-3 incident, CWRN mandated real-time GPS tracking for all air assets, replacing the schedule-based position tracking that had caused the misbelief.",
        "event", "ground_truth", dt="2033-10-15", source_id="protocol-update",
        source_type="policy_document")

    # ── C05 expansion: weather ──
    c05_wx_data = M("C05", "WX-South", "recorded", "wind_shift_0258",
        "Weather station WX-South recorded the wind direction change from 315° (NW) to 145° (SE) beginning at 02:58 on August 28, with the shift completing by 03:12.",
        "observation", "ground_truth", belief_holder="WX-South",
        dt="2033-08-28", source_id="wx-south", source_type="weather_data",
        confidence=0.98)
    c05_james_sleep = M("C05", "James_Park", "was_off_duty", "0100_to_0600",
        "Weather Coordinator James Park was off-duty from 01:00 to 06:00, with the overnight weather watch handled by an automated alert system that had a 4-hour latency for non-critical updates.",
        "event", "ground_truth", dt="2033-08-28", source_id="duty-roster",
        source_type="operational_record")
    c05_auto_alert = M("C05", "automated_system", "classified_wind_shift", "non_critical",
        "The automated weather alert system classified the 03:00 wind shift as non-critical because the wind speed didn't exceed threshold values, even though the direction change was operationally significant.",
        "event", "ground_truth", dt="2033-08-28", source_id="alert-system-log",
        source_type="system_log")
    c05_burnback_prep = M("C05", "burnback_crew", "staged_equipment", "0400_August_28",
        "The burnback crew staged equipment at the planned ignition point at 04:00, unaware that the wind had already shifted from NW to SE an hour earlier.",
        "observation", "belief_only", belief_holder="burnback_crew",
        dt="2033-08-28", source_id="ground-report-south", source_type="field_report")
    c05_abort_detail = M("C05", "Sarah_Whitehorse", "ordered_abort", "0415_burnback",
        "Sarah Whitehorse ordered the burnback abort at 04:15 after the crew chief reported unexpected fire behavior inconsistent with NW winds, leading her to check real-time weather data.",
        "event", "ground_truth", belief_holder="Sarah_Whitehorse",
        dt="2033-08-28", source_id="ops-log")
    c05_consequence = M("C05", "early_wind_shift", "caused", "250_additional_acres",
        "The 3-hour planning gap caused by the early wind shift resulted in approximately 250 additional acres burned in a direction CWRN hadn't anticipated or resourced for.",
        "fact", "ground_truth", dt="2033-08-28", source_id="fire-report",
        source_type="investigation_report")

    # ── C06 expansion: damage ──
    c06_method_diff = M("C06", "aerial_assessment", "methodology", "fly_over_count",
        "Tom Redfeather's aerial assessment used a single fly-over count at 500 feet altitude, identifying structures by visible roof destruction, which missed structures obscured by canopy or debris.",
        "fact", "contextual_true", belief_holder="Tom_Redfeather",
        dt="2033-08-30", source_id="assessment-methodology", source_type="technical_document")
    c06_ground_method = M("C06", "ground_assessment", "methodology", "building_by_building",
        "The ground assessment team walked each property, counting any structure with more than 50% wall/roof destruction, which caught outbuildings invisible from the air but may have over-counted damaged structures.",
        "fact", "contextual_true", belief_holder="damage_assessment_team",
        dt="2033-09-02", source_id="assessment-methodology", source_type="technical_document")
    c06_reclass = M("C06", "county_assessor", "reclassified", "2_structures_as_damaged",
        "The county assessor reclassified 2 structures from the ground team's 'destroyed' list as 'heavily damaged but repairable' based on structural engineering evaluation.",
        "event", "ground_truth", dt="2033-10-10", source_id="county-assessor",
        source_type="official_record")
    c06_uninsured = M("C06", "insurance_gap", "identified", "3_uninsured_structures",
        "Three destroyed structures had no insurance, explaining the gap between the 29 verified destroyed and 28 insurance claims.",
        "fact", "ground_truth", dt="2033-10-20", source_id="county-records",
        source_type="official_record")
    c06_disputed = M("C06", "insurance_claim", "disputed", "2_structures_questionable",
        "Insurance companies disputed claims on 2 structures, arguing damage was from pre-existing conditions rather than fire, but the county assessor attributed both to the fire.",
        "event", "ground_truth", dt="2033-11-01", source_id="insurance-dispute",
        source_type="legal_record")

    # ── C07 expansion: historical comparison ──
    c07_db_error = M("C07", "fire_history_database", "contained_error", "Ridge_Fire_projection_vs_final",
        "The CWRN fire history database listed the 2028 Ridge Fire at 12,000 acres — the pre-containment projection from August 2028 — rather than the final verified 8,500 acres.",
        "fact", "ground_truth", dt="2033-08-16", source_id="database-audit",
        source_type="audit_report")
    c07_sarah_relied = M("C07", "Sarah_Whitehorse", "relied_on", "database_without_verification",
        "Sarah Whitehorse pulled the Ridge Fire figure directly from the database without cross-checking against the post-fire survey records, which were stored in a different system.",
        "observation", "contextual_true", belief_holder="Sarah_Whitehorse",
        dt="2033-08-16", source_id="investigation-notes", source_type="internal_memo")
    c07_overalloc_detail = M("C07", "resource_over_allocation", "included", "extra_engine_companies",
        "The over-allocation based on the inflated comparison included 3 extra engine companies and 2 additional hand crews requested from mutual aid, costing an estimated $450K in unnecessary deployment.",
        "event", "ground_truth", dt="2033-08-17", source_id="resource-audit",
        source_type="financial_record")
    c07_correction = M("C07", "CWRN", "corrected_database", "Ridge_Fire_actual_8500",
        "Following Elena Volkov's discovery, CWRN corrected the fire history database to show the Ridge Fire's verified 8,500 acres and added a verification flag requirement for all entries.",
        "event", "ground_truth", dt="2033-09-01", source_id="database-update",
        source_type="system_log")

    # ── Additional background ──
    bg_extra = [
        ("CWRN_SOPs", "require", "multi_source_confirmation", "CWRN standard operating procedures require fire status changes to be confirmed by at least two independent observation sources before updating the operational picture.", "2031-06-01"),
        ("infrared_detection", "advantage", "sees_through_smoke", "Forward-looking infrared (FLIR) cameras detect heat signatures through smoke, giving aerial observers visibility that ground crews lack in heavy smoke conditions.", "2031-03-01"),
        ("fire_perimeter_mapping", "standard", "GPS_polygon_method", "Standard fire perimeter mapping uses GPS waypoint polygons connected by the observer, with accuracy depending on waypoint density and terrain access.", "2031-03-01"),
        ("evacuation_protocol", "requires", "positive_confirmation", "CWRN evacuation protocol requires positive confirmation of clearance from each zone, defined as all known residents accounted for at shelters or confirmed departed.", "2031-09-01"),
        ("mutual_aid_agreements", "allow", "resource_sharing", "Pacific Northwest mutual aid agreements allow fire agencies to share resources during multi-fire events, with the state coordination center managing deployments.", "2031-01-01"),
        ("wind_shift_impact", "affects", "fire_spread_direction", "Wind direction shifts are among the most critical weather events for active fires, as they can push fire into unburned fuel and outflank containment lines.", "2031-06-01"),
        ("damage_assessment_levels", "include", "three_tiers", "Fire damage assessment follows three tiers: rapid aerial (hours), detailed ground (days), and verified official (weeks), with accuracy increasing at each tier.", "2031-09-01"),
        ("fire_history_database", "serves_as", "planning_reference", "CWRN maintains a fire history database for comparison-based planning, enabling analysts to model current fires against historical precedents.", "2031-01-01"),
        ("Station_Alpha", "located", "south_sector_base_camp", "Station Alpha serves as the south sector base camp, housing ground crews, equipment, and a communications relay for the southern fire operations.", "2031-02-01"),
        ("Station_Bravo", "located", "north_sector_base_camp", "Station Bravo serves as the north sector base camp, positioned closer to residential areas and the primary evacuation staging point.", "2031-02-01"),
        ("Cascade_Creek_terrain", "characterized_by", "steep_mixed_forest", "The Cascade Creek fire area features steep terrain with mixed conifer forest, creating challenging access for ground crews and variable fire behavior.", "2033-08-14"),
        ("fire_behavior_modeling", "uses", "weather_terrain_fuel_inputs", "Fire behavior modeling combines real-time weather data, terrain slope and aspect, and fuel moisture content to predict fire spread rate and direction.", "2031-06-01"),
        ("Nadia_Al-Rashid", "coordinates_with", "county_emergency_management", "Evacuation Coordinator Nadia Al-Rashid works directly with county emergency management to issue orders, coordinate transportation, and manage shelters.", "2031-01-01"),
        ("Ben_Kowalski", "tracks", "all_CWRN_resources", "Resource Logistics Manager Ben Kowalski maintains the resource tracking board showing the position and status of all CWRN assets including aircraft, engines, and hand crews.", "2031-01-01"),
        ("Mei-Ling_Wu", "interfaces_with", "media_and_public", "Public Information Officer Mei-Ling Wu manages all media communications and public alerts, serving as the single authorized source for public-facing fire information.", "2031-01-01"),
    ]
    for subj, pred, obj, text, dt in bg_extra:
        M("background", subj, pred, obj, text,
          "fact", "ground_truth", dt=dt,
          source_id="cwrn-reference", source_type="reference_document",
          scope="public", confidence=0.95)

    # ── Queries ──
    Q("Why was Diego Ruiz's fire perimeter estimate so much lower than the actual size?",
      "methodology_analysis",
      ["Diego's estimate was based on walking the visible smoke line with GPS waypoints, a method that only captures smoke-visible fire. FLIR aerial imaging showed 280 additional acres of subsurface combustion invisible from the ground."],
      ["Ground visual methods miss fire hidden by canopy and smoke"],
      ["Diego deliberately underreported", "Ground estimates are always accurate"],
      [c01_diego_method, c01_ir_detail], [],
      notes="Tests understanding of observation methodology limitations")

    Q("What explains the gap between the satellite and aerial fire perimeter estimates?",
      "methodology_analysis",
      ["Sat-Sentinel's 30-meter pixel resolution caused it to miss narrow fire fingers less than 30m wide, while the aerial FLIR at lower altitude could detect finer details, explaining the 650 vs 800 acre difference."],
      ["Resolution limitations of satellite vs detail of aerial"],
      ["Satellite is always more accurate than aerial"],
      [c01_sat_res, c01_ir_detail], [])

    Q("According to Sarah Whitehorse, what is the reliability ranking of observation sources for fire perimeter estimation?",
      "belief_attribution",
      ["Sarah's post-incident memo ranked: FLIR aerial (±5% accuracy) > satellite thermal (±15%) > ground visual (±30%)"],
      ["Aerial > satellite > ground for perimeter estimation"],
      ["All sources are equally reliable"],
      [c01_sarah_memo], [],
      difficulty="medium", notes="Tests attribution of belief to specific holder")

    Q("Was Diego Ruiz's containment report on August 20 dishonest or simply wrong?",
      "belief_vs_reality",
      ["The report was honest but ultimately wrong. Diego personally walked the full 2.3-mile line and found no active fire within 100 feet. The containment was real at the time of reporting; it failed hours later when wind-driven embers were transported 300 feet across the line, far exceeding its 8-foot width."],
      ["Honest report that became wrong due to conditions changing"],
      ["Diego lied about containment", "Diego was negligent"],
      [c02_diego_check, c02_ember, c02_line_specs], [],
      disambig=True, notes="Tests distinguishing honest-but-wrong from dishonest")

    Q("What was the financial cost of the western flank containment breach?",
      "consequence_of_belief",
      ["The breach cost approximately $2.3M in additional suppression costs and resulted in 400 additional acres burned, plus the indirect costs of crew reallocation."],
      ["$2.3M and 400 additional acres"],
      ["No significant cost"],
      [c02_cost], [], difficulty="medium")

    Q("What systemic failure led to the Zone 3 evacuation being declared complete prematurely?",
      "root_cause_analysis",
      ["Multiple failures compounded: the southern cell tower was damaged before the evacuation order, cutting wireless alerts to 40 households; bus drivers completed scheduled stops but unnotified residents weren't at them; the shelter count of 816 vs 847 households seemed close enough; and no door-to-door verification was conducted before declaring clearance."],
      ["Communication failure + incomplete verification methodology"],
      ["Mei-Ling Wu deliberately lied"],
      [c03_tower, c03_bus_drivers, c03_shelter], [],
      notes="Tests distinguishing systemic failure from individual blame")

    Q("What policy change resulted from the Zone 3 evacuation incident?",
      "consequence_of_belief",
      ["CWRN revised its evacuation protocol to require confirmation via at least two independent communication channels before declaring an area cleared."],
      ["Multi-channel confirmation requirement"],
      ["No changes were made"],
      [c03_review], [], difficulty="medium")

    Q("Why didn't CWRN know Tanker-3 had been diverted before planning the retardant drop?",
      "root_cause_analysis",
      ["The state coordination center notified CWRN by email at 06:15, but the message went to a generic inbox not monitored during the overnight shift. Ben Kowalski checked the schedule-based resource board at 08:00, which still showed Tanker-3 at Regional Base."],
      ["Email went to unmonitored inbox; resource board was schedule-based not real-time"],
      ["CWRN was never notified", "Ben Kowalski ignored the notification"],
      [c04_state_center, c04_ben_check], [],
      notes="Tests understanding of communication failure vs. information availability")

    Q("How effective was the helicopter substitution for the absent Tanker-3?",
      "consequence_of_belief",
      ["Helo-1 and Helo-2 were repositioned from reconnaissance to water drops, but their combined 1,400-gallon capacity (700 each) was less than half of Tanker-3's 3,000-gallon capacity, making them insufficient as substitutes."],
      ["Insufficient — less than half the capacity"],
      ["Helicopters fully compensated for the tanker"],
      [c04_helo_sub], [], difficulty="medium")

    Q("Why wasn't the 03:00 wind shift detected and communicated before the burnback operation?",
      "root_cause_analysis",
      ["Three factors: James Park was off-duty, the automated weather alert system classified the direction change as non-critical because wind speed didn't exceed thresholds, and the system had 4-hour latency for non-critical updates. The actual detection came from ground crew noticing unexpected fire behavior at 04:15."],
      ["Off-duty coordinator + automated system classified it as non-critical"],
      ["The wind shift wasn't detected at all"],
      [c05_james_sleep, c05_auto_alert, c05_wx_data, c05_abort_detail], [])

    Q("How many acres were lost due to the early wind shift planning gap?",
      "consequence_of_belief",
      ["Approximately 250 additional acres burned in an unanticipated direction during the 3-hour gap between the actual wind shift (03:00) and when CWRN's planning assumptions caught up."],
      ["250 additional acres"],
      ["No additional acres were lost"],
      [c05_consequence], [], difficulty="medium")

    Q("Why did the aerial and ground damage assessments yield different structure counts?",
      "methodology_analysis",
      ["The aerial count (23) missed structures obscured by canopy or debris at 500-foot altitude. The ground count (31) caught outbuildings invisible from the air but over-counted by including 2 structures later reclassified as heavily damaged rather than destroyed."],
      ["Different methodologies: aerial missed hidden structures, ground over-counted damaged ones"],
      ["Both counts were equally wrong"],
      [c06_method_diff, c06_ground_method, c06_reclass], [],
      disambig=True)

    Q("Why was the insurance claim count (28) different from the verified count (29)?",
      "factual_discrepancy",
      ["Three destroyed structures had no insurance (reducing the claim count) while 2 insured structures had disputed claims (eventually attributed to fire by the county assessor), netting to 28 claims vs 29 verified."],
      ["3 uninsured + 2 disputed claims explains the gap"],
      ["All destroyed structures were insured"],
      [c06_uninsured, c06_disputed], [], difficulty="medium")

    Q("What was the specific error in the fire history database regarding the 2028 Ridge Fire?",
      "factual_discrepancy",
      ["The database listed the Ridge Fire at 12,000 acres — the pre-containment projection from August 2028 — rather than the final verified 8,500 acres. The projection was never updated with the actual figure."],
      ["Projection (12,000) stored instead of verified final (8,500)"],
      ["The database was intentionally falsified"],
      [c07_db_error], [], difficulty="medium")

    Q("What was the financial cost of the historical comparison error?",
      "consequence_of_belief",
      ["The over-allocation based on the inflated Ridge Fire comparison included 3 extra engine companies and 2 additional hand crews from mutual aid, costing an estimated $450K in unnecessary deployment."],
      ["$450K in unnecessary mutual aid deployment"],
      ["No financial impact"],
      [c07_overalloc_detail], [], difficulty="medium")

    # Append
    memories.extend(new_mems)
    queries.extend(new_qs)

    with open(mem_path, 'w') as f:
        for m in memories:
            f.write(json.dumps(m) + "\n")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

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
        f.write("\n")

    print(f"\nAdded {len(new_mems)} memories, {len(new_qs)} queries")
    print(f"Total: {len(memories)} memories, {len(queries)} queries")
    tags = {}
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0") or t == "background":
                tags[t] = tags.get(t, 0) + 1
    print(f"\nDistribution:")
    for k in sorted(tags):
        print(f"  {k}: {tags[k]}")

if __name__ == "__main__":
    main()
