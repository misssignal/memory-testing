#!/usr/bin/env python3
"""Exp 17 round-2 expansion — target ~170 memories, ~55 queries."""

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

    mid_counter = len(memories) + 200
    qid_counter = len(queries) + 1
    EXP = "exp17"
    STORY = "cascadia_wildfire_response_network"

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_mems = []
    new_qs = []

    def M(case, subj, pred, obj, text, etype, truth, belief_holder="CWRN",
          dt="2033-08-15", confidence=0.9, source_id="cwrn-ops",
          source_type="operational_record", scope="internal",
          derived=None, supersedes=None, contradicts=None, tags_extra=None):
        nonlocal mid_counter
        h = hashlib.md5(f"exp17-r2-{mid_counter}".encode()).hexdigest()[:8]
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

    # ── C01 continued expansion ──
    c01_pub = M("C01", "Mei-Ling_Wu", "announced_fire_size", "700_acres_public_briefing",
        "Mei-Ling Wu announced the fire at 'approximately 700 acres' in the 17:00 public briefing, using Marcus Chen's compromise figure rather than the aerial or ground estimates.",
        "observation", "belief_only", belief_holder="Mei-Ling_Wu",
        dt="2033-08-15", source_id="pio-briefing", source_type="public_statement",
        scope="public", confidence=0.7)
    c01_media = M("C01", "local_news", "reported", "500_to_800_acre_range",
        "Local news outlets reported the fire size as 'between 500 and 800 acres depending on the source,' highlighting the conflicting official estimates.",
        "observation", "contextual_true", belief_holder="media",
        dt="2033-08-15", source_id="media-coverage", source_type="media_report",
        scope="public")
    c01_nfps_method = M("C01", "NFPS", "used_method", "high_res_aerial_photo_mapping",
        "The National Fire Perimeter Survey used high-resolution aerial photography and ground truth points to produce the definitive 780-acre perimeter map with ±2% accuracy.",
        "fact", "ground_truth", dt="2033-09-10", source_id="nfps-methodology",
        source_type="technical_document")

    # ── C02 continued expansion ──
    c02_sarah_reaction = M("C02", "Sarah_Whitehorse", "predicted_breach_risk", "before_wind_shift",
        "Sarah Whitehorse had flagged the western flank as vulnerable to wind-driven ember transport in her evening briefing at 19:00, but the crew had already reported containment and resources were being moved.",
        "observation", "contextual_true", belief_holder="Sarah_Whitehorse",
        dt="2033-08-20", source_id="evening-briefing", source_type="briefing")
    c02_marcus_decision = M("C02", "Marcus_Chen", "accepted_containment_report", "standard_procedure",
        "Marcus Chen accepted Diego's containment report as per standard procedure — a ground crew chief's physical inspection of the line is the primary confirmation method.",
        "event", "contextual_true", belief_holder="Marcus_Chen",
        dt="2033-08-20", source_id="ops-log")
    c02_recontain = M("C02", "western_flank", "re_contained", "August_25",
        "The western flank was re-contained on August 25 after 5 days of additional suppression effort, with the new containment line set 400 feet further west.",
        "event", "ground_truth", dt="2033-08-25", source_id="ops-log")

    # ── C03 continued expansion ──
    c03_nadia_method = M("C03", "Nadia_Al-Rashid", "relied_on", "single_channel_WEA",
        "Nadia relied primarily on Wireless Emergency Alerts (WEA) for the Zone 3 evacuation notification, a cell-based system that depends on functioning towers in the target area.",
        "observation", "contextual_true", belief_holder="Nadia_Al-Rashid",
        dt="2033-08-22", source_id="evac-plan", source_type="operational_record")
    c03_siren = M("C03", "outdoor_warning_sirens", "not_activated", "Zone_3",
        "Zone 3 outdoor warning sirens were not activated because the fire threat was not classified as 'imminent life safety' at the time of the evacuation order — it was a mandatory but not emergency-level order.",
        "event", "ground_truth", dt="2033-08-22", source_id="evac-protocol",
        source_type="policy_document")
    c03_family = M("C03", "rescued_family", "reported", "no_warning_received",
        "A rescued family of five reported they had no landline, no cell service after the tower went down, and heard no sirens or door-to-door notification before the fire crew arrived.",
        "observation", "ground_truth", belief_holder="evacuee_family",
        dt="2033-08-23", source_id="evacuee-interview", source_type="interview")

    # ── C04 continued expansion ──
    c04_shift_brief = M("C04", "overnight_shift", "did_not_check", "generic_email_inbox",
        "The overnight shift team did not check the generic CWRN operations inbox between 22:00 and 07:00, as the inbox was not designated as critical communications in the overnight checklist.",
        "event", "ground_truth", dt="2033-08-25", source_id="shift-log",
        source_type="operational_record")
    c04_tanker_return = M("C04", "Tanker-3", "returned_to_CWRN", "August_27",
        "Tanker-3 returned from the Klamath Complex mutual aid deployment on August 27, two days after the missed retardant drop.",
        "event", "ground_truth", dt="2033-08-27", source_id="resource-log")
    c04_flank_cost = M("C04", "eastern_flank_advance", "burned", "additional_85_acres",
        "The 2-hour unchecked advance on the eastern flank due to Tanker-3's absence resulted in approximately 85 additional acres burned before helicopter water drops slowed the progression.",
        "fact", "ground_truth", dt="2033-08-25", source_id="fire-report",
        source_type="investigation_report")

    # ── C05 continued expansion ──
    c05_model_output = M("C05", "fire_spread_model", "predicted", "NW_progression_until_0600",
        "Sarah Whitehorse's fire spread model predicted continued northwestward progression until 06:00, with a southeast spread beginning after the forecast wind shift.",
        "belief", "belief_only", belief_holder="Sarah_Whitehorse",
        dt="2033-08-27", source_id="fire-model", source_type="model_output",
        confidence=0.75)
    c05_actual_spread = M("C05", "fire", "spread_southeast", "from_0300_August_28",
        "The fire began spreading southeast at 03:00 on August 28, three hours before the model predicted, moving into an area with no pre-positioned suppression resources.",
        "event", "ground_truth", dt="2033-08-28", source_id="fire-report")
    c05_wx_review = M("C05", "weather_service_review", "found", "forecast_model_limitation",
        "A post-incident weather service review found that the synoptic model used for the wind shift forecast had a known 2-4 hour timing uncertainty for ridge-top wind events in complex terrain.",
        "fact", "ground_truth", dt="2033-09-15", source_id="weather-review",
        source_type="investigation_report")

    # ── C06 continued expansion ──
    c06_canopy = M("C06", "canopy_cover", "obscured", "6_structures_from_air",
        "Dense canopy cover in the east portion of the fire zone obscured 6 structures from aerial view, accounting for the primary gap between Tom Redfeather's 23 and the actual 29.",
        "fact", "ground_truth", dt="2033-09-05", source_id="assessment-review",
        source_type="investigation_report")
    c06_outbuilding = M("C06", "outbuildings", "included_in", "ground_but_not_aerial_count",
        "Two destroyed outbuildings (a barn and a workshop) were counted in the ground assessment's 31 but not in the aerial count, as they were indistinguishable from debris piles from the air.",
        "fact", "ground_truth", dt="2033-09-05", source_id="assessment-review")
    c06_timeline = M("C06", "damage_assessment_timeline", "spanned", "August_30_to_October_15",
        "The full damage assessment process took 47 days from rapid aerial (Aug 30) through ground survey (Sep 1-2) to final verified count (Oct 15), with each tier refining the previous.",
        "fact", "ground_truth", dt="2033-10-15", source_id="assessment-summary",
        source_type="official_record")

    # ── C07 continued expansion ──
    c07_mutual_aid_cost = M("C07", "mutual_aid_deployment", "returned", "3_companies_recalled",
        "The 3 extra engine companies and 2 hand crews were recalled on August 26 after Elena Volkov's correction, but the deployment costs for the 10-day period were not recoverable.",
        "event", "ground_truth", dt="2033-08-26", source_id="resource-log")
    c07_other_fires = M("C07", "mutual_aid_units", "needed_elsewhere", "during_over_deployment",
        "The over-deployed mutual aid units were needed at two other active fires during the 10-day period, creating resource gaps at those incidents.",
        "event", "ground_truth", dt="2033-08-20", source_id="state-coordination",
        source_type="coordination_record")
    c07_database_audit = M("C07", "CWRN", "audited_database", "found_14_more_errors",
        "A subsequent audit of the CWRN fire history database triggered by the Ridge Fire error found 14 additional entries with uncorrected projection figures rather than final verified acreage.",
        "event", "ground_truth", dt="2033-10-01", source_id="database-audit",
        source_type="audit_report")

    # ── Cross-case belief-reality memories ──
    xc1 = M("C01", "CWRN_operations", "used_wrong_figure", "planning_based_on_700_acres",
        "CWRN's resource deployment on August 15 was based on the 700-acre compromise, underestimating the actual 780 acres and leaving the southeast perimeter under-resourced.",
        "event", "contextual_true", belief_holder="CWRN",
        dt="2033-08-15", source_id="ops-log")
    xc2 = M("C02", "CWRN", "learned_containment_unreliable", "post_incident_analysis",
        "The post-incident analysis concluded that containment reports based on ground inspection alone are insufficient — aerial confirmation and weather forecast review should be mandatory.",
        "event", "ground_truth", dt="2033-09-20", source_id="after-action-report",
        source_type="investigation_report")
    xc3 = M("C05", "CWRN", "revised_weather_monitoring", "24_hour_human_watch",
        "After the August 28 wind shift incident, CWRN established 24-hour human weather monitoring during active fires, replacing the automated overnight system.",
        "event", "ground_truth", dt="2033-10-15", source_id="protocol-update",
        source_type="policy_document")

    # ── Additional background ──
    bg_extra = [
        ("wildfire_observation", "inherently_uncertain", "multiple_methods", "No single observation method provides complete fire status — each has blind spots, latency, and resolution limits that create opportunities for belief-reality divergence.", "2031-06-01"),
        ("belief_state_lag", "common_in", "fire_operations", "Operational belief states typically lag reality by 30 minutes to several hours depending on the observation method, communication chain, and update frequency.", "2031-06-01"),
        ("resource_tracking", "historically_used", "schedule_based_positions", "Prior to GPS tracking mandates, CWRN tracked aircraft by their scheduled positions, which could diverge from actual positions during mutual aid diversions.", "2031-01-01"),
        ("evacuation_completeness", "hard_to_verify", "in_real_time", "Verifying evacuation completeness in real-time is challenging because there is no pre-existing census of who is present in a fire zone at any given time.", "2031-09-01"),
        ("damage_assessment_accuracy", "improves_with", "time_and_detail", "Damage assessment accuracy improves with time and methodological detail, but operational decisions must be made with early, less accurate estimates.", "2031-09-01"),
        ("historical_fire_data", "subject_to", "entry_quality", "Historical fire databases are only as reliable as their data entry process — projection figures, preliminary estimates, and verified finals may all exist for the same event.", "2031-01-01"),
        ("Helo-1", "equipped_with", "FLIR_and_video", "Helo-1 carries a forward-looking infrared camera and video downlink, enabling real-time thermal imaging transmission to CWRN operations.", "2031-03-01"),
        ("Helo-2", "serves_as", "backup_and_transport", "Helo-2 primarily serves as personnel transport and backup surveillance, with water-drop capability via an external bucket.", "2031-03-01"),
        ("Tanker-3", "carries", "3000_gallons_retardant", "Air tanker Tanker-3 carries 3,000 gallons of fire retardant, making it the most impactful single-asset deployment in CWRN's inventory.", "2031-03-01"),
        ("WX-North", "located_at", "2400_feet_ridge", "Weather station WX-North is located at 2,400 feet on the north ridge, reporting wind, temperature, and humidity every 10 minutes.", "2031-03-01"),
        ("WX-South", "located_at", "valley_floor", "Weather station WX-South is located on the valley floor at 800 feet, with wind readings often diverging from ridge-top conditions.", "2031-03-01"),
        ("CWRN_shift_structure", "operates", "three_8_hour_shifts", "CWRN operates on three 8-hour shifts during active fires: day (06:00-14:00), swing (14:00-22:00), and overnight (22:00-06:00).", "2031-01-01"),
        ("overnight_shift", "has", "reduced_staffing", "The overnight shift operates with reduced staffing — typically one operations officer, one weather monitor, and one communications operator.", "2031-01-01"),
        ("fire_season_length", "increasing", "Pacific_Northwest", "Pacific Northwest fire seasons have been increasing in length and severity, with the 2033 season starting 3 weeks earlier than the 10-year average.", "2033-05-01"),
        ("community_alert_systems", "include", "WEA_sirens_radio_doorknock", "Community alert systems include Wireless Emergency Alerts (WEA), outdoor sirens, Emergency Alert System (EAS) radio broadcasts, and door-to-door notifications as a last resort.", "2031-09-01"),
        ("post_fire_survey", "is", "definitive_record", "The National Fire Perimeter Survey conducted after containment provides the definitive acreage record, superseding all operational estimates.", "2031-01-01"),
    ]
    for subj, pred, obj, text, dt in bg_extra:
        M("background", subj, pred, obj, text,
          "fact", "ground_truth", dt=dt,
          source_id="cwrn-reference", source_type="reference_document",
          scope="public", confidence=0.95)

    # ── Queries ──
    Q("What figure did the public receive for the Cascade Creek fire size on August 15?",
      "belief_attribution",
      ["The public received 'approximately 700 acres' from Mei-Ling Wu's 17:00 briefing, based on Marcus Chen's compromise figure. Local news reported the range as '500 to 800 acres depending on the source.'"],
      ["700 acres publicly, with media noting conflicting estimates"],
      ["The public was told the accurate 780-acre figure"],
      [c01_pub, c01_media], [], difficulty="medium")

    Q("How accurate was the National Fire Perimeter Survey compared to the operational estimates?",
      "methodology_analysis",
      ["The NFPS used high-resolution aerial photography with ground truth points for ±2% accuracy, producing the definitive 780-acre figure. Operational estimates ranged from 500 (ground) to 800 (aerial), bracketing the truth but with much wider error margins."],
      ["NFPS most accurate at ±2%; operational estimates had ±5-30% error"],
      ["Operational estimates were equally accurate"],
      [c01_nfps_method], [])

    Q("Did Sarah Whitehorse's warning about the western flank prevent the containment breach?",
      "belief_vs_reality",
      ["No. Sarah flagged the vulnerability at 19:00, but the containment had already been reported complete and resources were being moved. The breach occurred at 22:00 when wind-driven embers jumped the line."],
      ["Warning came too late — resources already reallocated"],
      ["Sarah's warning prevented the breach"],
      [c02_sarah_reaction, c02_marcus_decision], [],
      notes="Tests whether a warning that came too late changes the narrative")

    Q("How long did it take to re-contain the western flank after the breach?",
      "factual_retrieval",
      ["Five days — the western flank was re-contained on August 25, with the new containment line set 400 feet further west than the original."],
      ["5 days, with line repositioned 400 feet further west"],
      ["Containment was restored within hours"],
      [c02_recontain], [], difficulty="easy")

    Q("Why weren't Zone 3 outdoor warning sirens used during the evacuation?",
      "root_cause_analysis",
      ["The fire threat was not classified as 'imminent life safety' at the time — it was a mandatory but not emergency-level evacuation order. Sirens require the higher classification to activate."],
      ["Threat classification was below siren activation threshold"],
      ["Sirens were activated"],
      [c03_siren], [], difficulty="medium")

    Q("What did the rescued Zone 3 families experience during the failed evacuation notification?",
      "witness_account",
      ["A family of five reported having no landline, no cell service after the tower went down, and hearing no sirens or door-to-door notification. They only learned of the fire when the crew arrived."],
      ["No warning through any channel due to cascading communication failures"],
      ["All families received timely warning"],
      [c03_family], [], difficulty="medium")

    Q("Why wasn't the state coordination center's email about Tanker-3 seen before the planned drop?",
      "root_cause_analysis",
      ["The email arrived at 06:15 to a generic inbox not included in the overnight shift checklist. The overnight team didn't check it, and Ben Kowalski checked the schedule-based resource board at 08:00, which showed the outdated position."],
      ["Unmonitored inbox + outdated tracking system"],
      ["The email was never sent"],
      [c04_shift_brief], [])

    Q("What were the consequences of Tanker-3's absence on August 25?",
      "consequence_of_belief",
      ["The eastern flank advanced unchecked for approximately 2 hours, burning an additional 85 acres before Helo-1 and Helo-2 (with much smaller capacity) could be repositioned for water drops."],
      ["85 additional acres burned, 2-hour delay"],
      ["No significant consequences"],
      [c04_flank_cost], [], difficulty="medium")

    Q("What known limitation of the weather forecast model contributed to the wind shift timing error?",
      "methodology_analysis",
      ["The synoptic model used for the forecast had a known 2-4 hour timing uncertainty for ridge-top wind events in complex terrain, meaning the actual 03:00 shift was within the model's error bounds of the 06:00 prediction."],
      ["2-4 hour timing uncertainty for ridge-top wind events"],
      ["The model had no known limitations"],
      [c05_wx_review], [])

    Q("Where did the fire spread during the 3-hour planning gap on August 28?",
      "belief_vs_reality",
      ["The fire spread southeast starting at 03:00, moving into an area with no pre-positioned suppression resources because the model predicted northwestward progression until 06:00."],
      ["Southeast, into an un-resourced area"],
      ["The fire continued northwest as predicted"],
      [c05_actual_spread, c05_model_output], [],
      conflict=True)

    Q("What specifically caused the 8-structure gap between aerial and verified damage counts?",
      "methodology_analysis",
      ["The aerial assessment missed 6 structures obscured by dense canopy cover and 2 outbuildings (barn and workshop) that were indistinguishable from debris from the air. The ground team then over-counted 2 structures later reclassified as damaged but repairable, netting to a 6-structure gap between aerial (23) and final (29)."],
      ["6 canopy-obscured + 2 outbuildings missed from air, minus 2 over-counted on ground"],
      ["The aerial team was careless"],
      [c06_canopy, c06_outbuilding], [],
      disambig=True)

    Q("How long did the full damage assessment process take from start to final count?",
      "factual_retrieval",
      ["47 days — from the rapid aerial assessment on August 30 through ground survey (Sep 1-2) to final verified count on October 15."],
      ["47 days, three assessment tiers"],
      ["Assessment was complete within a week"],
      [c06_timeline], [], difficulty="easy")

    Q("What broader impact did the Ridge Fire database error have beyond the Cascade Creek response?",
      "consequence_of_belief",
      ["The over-deployed mutual aid units (3 engine companies, 2 hand crews) were needed at two other active fires during their 10-day deployment, creating resource gaps at those incidents. Additionally, a database audit found 14 more entries with uncorrected projection figures."],
      ["Resource gaps at other fires + 14 additional database errors found"],
      ["No broader impact"],
      [c07_other_fires, c07_database_audit], [])

    Q("In how many of the seven cases did CWRN's belief state diverge from objective reality?",
      "cross_case_synthesis",
      ["All seven cases involve belief-reality divergence: C01 (fire size), C02 (containment status), C03 (evacuation completeness), C04 (resource position), C05 (weather conditions), C06 (damage count), C07 (historical comparison). This was by design — the entire fire response was characterized by persistent information gaps."],
      ["All seven cases involved belief-reality divergence"],
      ["Only one or two cases had divergence"],
      [], [],
      notes="Meta-analysis of belief-reality theme across all cases")

    Q("What policy changes did CWRN implement after the Cascade Creek fire to reduce belief-reality gaps?",
      "cross_case_synthesis",
      ["Multiple policies: aerial confirmation required before declaring containment (C02); multi-channel evacuation confirmation (C03); real-time GPS for air assets (C04); 24-hour human weather monitoring (C05); database verification flags (C07). The fire led to a systematic overhaul of information verification procedures."],
      ["Policy changes addressing each type of belief-reality gap"],
      ["No policy changes were made"],
      [xc2, xc3], [],
      notes="Cross-case synthesis of institutional learning")

    Q("Across all the Cascade Creek incidents, did any observer deliberately misrepresent information?",
      "belief_attribution",
      ["No — in every case, observers reported honestly based on their available information and methodology. Diego's containment report was based on physical inspection; Mei-Ling's evacuation announcement was based on shelter counts; the database error was an uncorrected historical entry. All were honest beliefs that happened to be wrong."],
      ["No deliberate misrepresentation in any case"],
      ["Multiple observers lied", "Diego fabricated the containment report"],
      [], [],
      disambig=True,
      notes="Critical test: system must distinguish honest error from deception")

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
