#!/usr/bin/env python3
"""Exp 17 round-4 expansion — target ≥ 200 memories, ≥ 75 queries."""

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

    mid_counter = len(memories) + 600
    qid_counter = len(queries) + 1

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_mems = []
    new_qs = []

    def M(case, subj, pred, obj, text, etype, truth, belief_holder="CWRN",
          dt="2033-08-15", confidence=0.9, source_id="cwrn-ops",
          source_type="operational_record", scope="internal",
          derived=None, supersedes=None, contradicts=None, tags_extra=None):
        nonlocal mid_counter
        h = hashlib.md5(f"exp17-r4-{mid_counter}".encode()).hexdigest()[:8]
        t_ev = f"{dt}T09:00:00Z"; t_ob = f"{dt}T12:00:00Z"
        t_au = f"{dt}T15:00:00Z"; t_in = f"{dt}T18:00:00Z"
        m = {
            "memory_id": f"E17-{h}",
            "experiment": "exp17", "story_id": "cascadia_wildfire_response_network",
            "event_time": t_ev, "observation_time": t_ob,
            "authored_time": t_au, "ingestion_time": t_in,
            "subject": subj, "predicate": pred, "object": obj, "text": text,
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
            "expected_claims": expected, "acceptable_claims": acceptable,
            "forbidden_claims": forbidden,
            "relevant_memory_ids": relevant, "distractor_memory_ids": distractors,
            "must_surface_uncertainty": uncertainty, "must_surface_conflict": conflict,
            "must_disambiguate": disambig, "must_preserve_scope": scope,
            "should_abstain": abstain, "difficulty": difficulty, "notes": notes
        }
        qid_counter += 1
        new_qs.append(q)
        return q["query_id"]

    # ── C01-C07 additional memories to reach 200+ ──
    M("C01", "Priya_Johal", "estimated_fire", "northeast_sector_200_acres",
      "North Sector Chief Priya Johal independently estimated the fire's northeast sector at 200 acres from Station Bravo, but this sector estimate was never integrated into the composite picture.",
      "observation", "belief_only", belief_holder="Priya_Johal",
      dt="2033-08-15", source_id="ground-report-north", source_type="field_report", confidence=0.7)
    M("C01", "fire_mapping_team", "deployed", "August_16",
      "A dedicated fire mapping team was deployed on August 16 to resolve the conflicting estimates, using a combination of ground GPS traverses and aerial photo mosaics.",
      "event", "ground_truth", dt="2033-08-16", source_id="ops-log")
    M("C01", "Sarah_Whitehorse", "used_500_acre_estimate", "initial_resource_request",
      "Sarah Whitehorse's initial resource request on the morning of August 15 was based on Diego's 500-acre ground estimate (received first), before aerial and satellite data arrived.",
      "event", "contextual_true", belief_holder="Sarah_Whitehorse",
      dt="2033-08-15", source_id="resource-request", source_type="operational_record")

    M("C02", "Diego_Ruiz", "defended_report", "conditions_changed_after",
      "In the after-action review, Diego Ruiz defended his containment report, stating the line was sound when inspected and that no one could have predicted the wind-driven ember transport distance.",
      "observation", "contextual_true", belief_holder="Diego_Ruiz",
      dt="2033-09-20", source_id="after-action-review", source_type="investigation_report")
    M("C02", "Priya_Johal", "noticed_glow", "0100_from_Station_Bravo",
      "Priya Johal reported seeing an orange glow west of the containment line from Station Bravo at 01:00, but communication was patchy and the report didn't reach the ops center until 04:00.",
      "observation", "ground_truth", belief_holder="Priya_Johal",
      dt="2033-08-21", source_id="ground-report-north", source_type="field_report")

    M("C03", "county_emergency_manager", "confirmed", "communication_gap",
      "The county emergency manager confirmed that no backup notification method (door-to-door, siren) was triggered for Zone 3 because the WEA system reported successful transmission on all active towers — it couldn't report the dead tower's coverage gap.",
      "event", "ground_truth", dt="2033-08-23", source_id="county-ema-report",
      source_type="government_record")
    M("C03", "post_incident_review", "recommended", "tower_status_integration",
      "The post-incident review recommended integrating cell tower status monitoring into evacuation planning, so damaged towers automatically trigger backup notification methods.",
      "event", "ground_truth", dt="2033-10-15", source_id="after-action-report",
      source_type="investigation_report")

    M("C04", "Ben_Kowalski", "had_no_reason", "to_doubt_resource_board",
      "Ben Kowalski noted that the resource board had been reliable for 3 years of operations, making the Tanker-3 discrepancy the first known instance of a stale position causing operational failure.",
      "observation", "contextual_true", belief_holder="Ben_Kowalski",
      dt="2033-08-25", source_id="after-action-interview", source_type="interview")

    M("C05", "WX-North", "showed_delayed_shift", "0345_vs_0300",
      "Weather station WX-North on the ridge recorded the wind shift at 03:45, 45 minutes later than WX-South in the valley, illustrating how terrain affects wind shift timing across the fire zone.",
      "observation", "ground_truth", dt="2033-08-28", source_id="wx-north",
      source_type="weather_data")
    M("C05", "Sarah_Whitehorse", "realized_error", "0415_checking_wx_data",
      "Sarah Whitehorse checked the real-time weather data feeds at 04:15 after receiving the crew chief's report of unexpected fire behavior, discovering the wind had shifted 75 minutes earlier.",
      "observation", "ground_truth", belief_holder="Sarah_Whitehorse",
      dt="2033-08-28", source_id="ops-log")

    M("C06", "Tom_Redfeather", "acknowledged_limitations", "aerial_method",
      "Tom Redfeather acknowledged in his report that the single-pass aerial assessment was intended as a rapid estimate, not a definitive count, and recommended ground follow-up.",
      "observation", "contextual_true", belief_holder="Tom_Redfeather",
      dt="2033-08-30", source_id="aerial-assessment-notes", source_type="field_report")
    M("C06", "county_assessor", "used_engineering_criteria", "structural_assessment",
      "The county assessor used licensed structural engineering criteria for the final assessment, with each structure evaluated for load-bearing integrity, not just visual damage.",
      "fact", "ground_truth", dt="2033-10-15", source_id="assessment-methodology",
      source_type="official_record")

    M("C07", "fire_history_database", "lacked", "verification_flags",
      "The CWRN fire history database had no verification flags or data provenance tracking, making it impossible to distinguish preliminary estimates from verified final figures without checking external sources.",
      "fact", "ground_truth", dt="2033-08-25", source_id="database-audit",
      source_type="audit_report")
    M("C07", "14_additional_errors", "ranged_from", "10_to_40_percent_overestimates",
      "The 14 additional database errors found in the audit ranged from 10% to 40% overestimates, all cases where pre-containment projections were stored instead of final verified acreages.",
      "fact", "ground_truth", dt="2033-10-01", source_id="database-audit",
      source_type="audit_report")

    # Additional background
    bg = [
        ("fire_containment_verification", "best_practice", "aerial_plus_ground", "Best practice for containment verification is a combined ground inspection and aerial survey, as ground crews can confirm line integrity while aerial identifies hotspots beyond the line.", "2031-06-01"),
        ("emergency_communication_redundancy", "principle", "no_single_point_of_failure", "Emergency communication systems should have no single point of failure — redundant channels ensure messages reach all intended recipients even if one system fails.", "2031-09-01"),
        ("real_time_tracking", "advantage", "eliminates_schedule_lag", "Real-time GPS tracking eliminates the position lag inherent in schedule-based systems, showing actual asset locations regardless of diversions or delays.", "2031-03-01"),
        ("forecast_uncertainty_communication", "should_include", "timing_confidence_bands", "Best practice weather forecasting for fire operations should include timing confidence bands, not just point estimates, so planners can build appropriate safety margins.", "2031-06-01"),
        ("multi_tier_assessment", "purpose", "progressive_refinement", "Multi-tier damage assessment serves progressive refinement: rapid estimates support immediate decisions, while detailed surveys provide the legal record for recovery and insurance.", "2031-09-01"),
        ("data_provenance", "critical_for", "historical_databases", "Data provenance (tracking source, version, and verification status of each entry) is critical for historical databases used in operational planning.", "2031-01-01"),
        ("Cascade_Creek_fire", "total_size", "2100_acres_final", "The Cascade Creek fire burned a total of 2,100 acres before full containment on September 5, 2033.", "2033-09-05"),
        ("Cascade_Creek_fire", "cost", "$14.2M_total_suppression", "Total suppression costs for the Cascade Creek fire were $14.2 million, including $450K in over-allocated mutual aid and $180K in emergency water taxis.", "2033-12-01"),
        ("after_action_report", "completed", "October_2033", "CWRN's comprehensive after-action report for the Cascade Creek fire was completed in October 2033, documenting all seven major belief-reality divergences.", "2033-10-30"),
        ("CWRN_reforms", "implemented", "2034_fire_season", "All CWRN protocol reforms from the Cascade Creek after-action report were implemented before the 2034 fire season.", "2034-05-01"),
        ("belief_reality_gap", "is", "inherent_in_emergency_ops", "The after-action report concluded that some degree of belief-reality gap is inherent in emergency operations and cannot be eliminated, only managed through systematic verification and redundancy.", "2033-10-30"),
    ]
    for subj, pred, obj, text, dt in bg:
        M("background", subj, pred, obj, text,
          "fact", "ground_truth", dt=dt,
          source_id="cwrn-reference", source_type="reference_document",
          scope="public", confidence=0.95)

    # ── Additional queries ──
    Q("Did Priya Johal contribute any fire size observations from the north sector?",
      "belief_attribution",
      ["Yes — Priya independently estimated the northeast sector at 200 acres from Station Bravo, but this estimate was never integrated into the composite picture that used only Diego's, Tom's, and Elena's estimates."],
      ["200-acre northeast sector estimate, not integrated"],
      ["Priya made no observations about fire size"],
      [], [], difficulty="medium")

    Q("What happened first on August 15 — the resource request or the aerial estimate?",
      "temporal_ordering",
      ["Sarah Whitehorse's initial resource request was based on Diego's 500-acre ground estimate, which arrived first. The aerial and satellite data came later, creating a resource deployment sized for a smaller fire."],
      ["Resource request based on first (ground) estimate, before aerial data"],
      ["Resources were allocated after all estimates were received"],
      [], [], difficulty="medium",
      notes="Tests temporal ordering of belief formation and decision-making")

    Q("Did anyone observe the containment breach in real time on August 20-21?",
      "temporal_belief_gap",
      ["Priya Johal saw an orange glow west of the containment line from Station Bravo at 01:00, but patchy communications meant her report didn't reach the ops center until 04:00. The breach was formally confirmed by Tom Redfeather's dawn aerial survey at 05:30."],
      ["Priya saw it at 01:00 but report was delayed; confirmed by aerial at 05:30"],
      ["The breach was detected immediately"],
      [], [],
      notes="Tests whether delayed observation counts as real-time detection")

    Q("Why did the WEA system not alert CWRN to the Zone 3 coverage gap?",
      "root_cause_analysis",
      ["The WEA system reported successful transmission on all active towers — it couldn't report on the dead tower's coverage gap because it only tracked active infrastructure, not missing coverage areas."],
      ["System reported success on active towers but couldn't detect dead tower's gap"],
      ["The WEA system alerted CWRN but the alert was ignored"],
      [], [])

    Q("Was Ben Kowalski negligent in relying on the resource board for Tanker-3's position?",
      "decision_evaluation",
      ["No — the resource board had been reliable for 3 years of operations, and the Tanker-3 incident was the first known case of a stale position causing operational failure. The systemic flaw was in the schedule-based tracking system, not in Ben's reliance on it."],
      ["Not negligent — systemic failure, not individual error"],
      ["Ben was negligent for not verifying"],
      [], [],
      disambig=True)

    Q("Did the two weather stations show the same wind shift timing?",
      "factual_comparison",
      ["No — WX-South (valley floor) recorded the shift at 02:58 while WX-North (ridge at 2,400 feet) recorded it at 03:45, a 47-minute difference illustrating terrain effects on wind pattern propagation."],
      ["47-minute difference due to terrain — valley first, ridge later"],
      ["Both stations recorded the same time"],
      [], [], difficulty="medium")

    Q("What was the total financial cost of the Cascade Creek fire, including belief-related expenses?",
      "quantitative_comparison",
      ["Total suppression cost was $14.2M, including at least $450K in over-allocated mutual aid (C07), $180K in emergency water taxis (C02), and additional costs from the containment breach ($2.3M additional suppression). Belief-reality gaps contributed measurably to the total."],
      ["$14.2M total, with identified belief-related costs of $3M+"],
      ["Belief-reality gaps had no financial impact"],
      [], [], difficulty="medium")

    Q("What was the most consequential belief-reality divergence in the Cascade Creek fire?",
      "meta_analysis",
      ["Arguably the Zone 3 evacuation (C03), as it directly endangered 31 lives. The containment breach (C02) was costliest in acres and dollars ($2.3M, 400 acres). The answer depends on whether you measure consequence by human safety, financial cost, or operational impact."],
      ["C03 for human safety; C02 for cost/acreage — depends on measurement"],
      ["There was no significant divergence"],
      [], [],
      uncertainty=True,
      notes="Tests ability to evaluate severity with multiple valid frameworks")

    Q("Did the CWRN reforms from the Cascade Creek fire address all seven types of belief-reality divergence?",
      "cross_case_synthesis",
      ["The reforms addressed most types: aerial containment verification (C02), multi-channel evacuation confirmation (C03), real-time GPS tracking (C04), 24-hour weather monitoring (C05), database verification flags (C07). The observation methodology gap (C01) and damage assessment timing (C06) were acknowledged but less directly reformed."],
      ["Most but not all types addressed; C01 and C06 less directly reformed"],
      ["All types were fully resolved"],
      [], [],
      notes="Tests nuanced assessment of institutional response")

    Q("What did the after-action report conclude about the possibility of eliminating belief-reality gaps?",
      "factual_retrieval",
      ["The report concluded that some degree of belief-reality gap is inherent in emergency operations and cannot be eliminated, only managed through systematic verification and redundancy."],
      ["Gaps are inherent and can only be managed, not eliminated"],
      ["The report concluded all gaps are preventable"],
      [], [], difficulty="easy")

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
