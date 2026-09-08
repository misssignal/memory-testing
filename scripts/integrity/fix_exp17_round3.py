#!/usr/bin/env python3
"""Exp 17 round-3 expansion — target ≥ 200 memories, ≥ 75 queries."""

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

    mid_counter = len(memories) + 400
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
        h = hashlib.md5(f"exp17-r3-{mid_counter}".encode()).hexdigest()[:8]
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

    # ── C01 more memories ──
    M("C01", "ground_crew", "acknowledged_limitation", "smoke_only_visibility",
      "Diego Ruiz's crew acknowledged in their report that thick smoke limited visibility to the fire's edge, noting 'we can only map what we can see.'",
      "observation", "contextual_true", belief_holder="Diego_Ruiz",
      dt="2033-08-15", source_id="ground-report-south", source_type="field_report")
    M("C01", "CWRN_ops", "logged_three_estimates", "500_650_800_acres",
      "The CWRN operations log at 12:00 on August 15 recorded three simultaneous fire size estimates: ground 500, satellite 650, aerial 800 acres, with a note requesting resolution.",
      "event", "ground_truth", dt="2033-08-15", source_id="ops-log")
    M("C01", "Tom_Redfeather", "noted_fire_behavior", "crown_fire_in_NW_sector",
      "Tom Redfeather observed active crown fire in the northwest sector visible on FLIR but producing minimal smoke, making it invisible to ground observers 2 miles away.",
      "observation", "ground_truth", belief_holder="Tom_Redfeather",
      dt="2033-08-15", source_id="aerial-report", source_type="surveillance_report")

    # ── C02 more memories ──
    M("C02", "wind_speed", "increased_to", "28_mph_gusts_2200",
      "Wind speed increased to sustained 22 mph with gusts to 28 mph during the 22:00 shift, exceeding the 20 mph threshold for ember transport across 8-foot firebreaks.",
      "event", "ground_truth", dt="2033-08-20", source_id="wx-south", source_type="weather_data")
    M("C02", "spot_fires", "grew_to", "15_acres_each_by_dawn",
      "Each of the three spot fires that established beyond the containment line had grown to approximately 15 acres by dawn, totaling 45 acres of new fire west of the original line.",
      "observation", "ground_truth", belief_holder="Tom_Redfeather",
      dt="2033-08-21", source_id="aerial-report", source_type="surveillance_report")
    M("C02", "Ben_Kowalski", "scrambled_resources", "back_to_western_flank",
      "Ben Kowalski scrambled two hand crews and an engine company back to the western flank at 06:00 August 21 after the breach was confirmed, reversing the previous night's reallocation.",
      "event", "ground_truth", dt="2033-08-21", source_id="resource-log")

    # ── C03 more memories ──
    M("C03", "shelter_registration", "showed_discrepancy", "816_vs_847",
      "The shelter registration showed 816 people from Zone 3, compared to the 847 household count. Mei-Ling Wu interpreted the gap as families who self-evacuated to hotels or relatives.",
      "observation", "belief_only", belief_holder="Mei-Ling_Wu",
      dt="2033-08-22", source_id="shelter-log", source_type="humanitarian_record")
    M("C03", "Nadia_Al-Rashid", "assumed_self_evacuation", "gap_in_numbers",
      "Nadia Al-Rashid assumed the 31-person gap between shelter registrations and expected evacuees was due to self-evacuation, a common pattern in previous Zone evacuations.",
      "belief", "belief_only", belief_holder="Nadia_Al-Rashid",
      dt="2033-08-22", source_id="evac-log")
    M("C03", "fire_proximity", "was", "2_miles_from_southern_Zone_3",
      "At the time of discovery, the fire front was approximately 2 miles from the southern Zone 3 households, with an estimated 4-hour window before potential direct threat.",
      "observation", "ground_truth", dt="2033-08-22", source_id="fire-report")

    # ── C04 more memories ──
    M("C04", "Klamath_Complex_fire", "requested_Tanker-3", "urgent_need",
      "The Klamath Complex fire's incident commander requested Tanker-3 via the state coordination center, citing critical structure protection needs that outranked CWRN's planned deployment.",
      "event", "ground_truth", dt="2033-08-25", source_id="state-coordination",
      source_type="coordination_record")
    M("C04", "Marcus_Chen", "expressed_frustration", "communication_gap",
      "Director Chen expressed frustration that the state coordination center could divert a CWRN asset without direct notification to the CWRN operations floor, calling it 'a system designed to fail.'",
      "observation", "contextual_true", belief_holder="Marcus_Chen",
      dt="2033-08-25", source_id="after-action-notes")

    # ── C05 more memories ──
    M("C05", "burnback_crew", "observed", "fire_moving_wrong_direction",
      "The burnback crew chief observed fire moving southeast instead of the expected northwest at 04:10, reporting 'the fire isn't doing what it's supposed to' before Sarah ordered the abort.",
      "observation", "ground_truth", belief_holder="burnback_crew",
      dt="2033-08-28", source_id="ground-report-south", source_type="field_report")
    M("C05", "James_Park", "acknowledged", "forecast_limitation",
      "James Park acknowledged post-incident that he should have flagged the known 2-4 hour timing uncertainty in the forecast and recommended a wider safety window for the burnback.",
      "observation", "contextual_true", belief_holder="James_Park",
      dt="2033-09-15", source_id="after-action-interview", source_type="interview")
    M("C05", "CWRN", "revised_burnback_protocol", "2_hour_buffer",
      "CWRN's revised burnback protocol requires a minimum 2-hour buffer between planned ignition and any forecast weather event, accounting for forecast timing uncertainty.",
      "event", "ground_truth", dt="2033-10-15", source_id="protocol-update",
      source_type="policy_document")

    # ── C06 more memories ──
    M("C06", "homeowner_disputes", "challenged", "2_assessments",
      "Two homeowners challenged the county assessor's 'destroyed' classification, arguing their structures were repairable, but engineering surveys confirmed total loss.",
      "event", "ground_truth", dt="2033-11-15", source_id="appeals-record",
      source_type="legal_record")
    M("C06", "media", "reported", "conflicting_damage_numbers",
      "Local media reported the conflicting damage numbers (23, 28, 31) over successive weeks, creating public confusion about the fire's actual impact.",
      "observation", "contextual_true", belief_holder="media",
      dt="2033-09-20", source_id="media-coverage", source_type="media_report",
      scope="public")

    # ── C07 more memories ──
    M("C07", "Elena_Volkov", "cross_referenced", "satellite_archive_vs_database",
      "Elena Volkov discovered the Ridge Fire discrepancy while cross-referencing CWRN's database against Sat-Sentinel's historical archive, which showed the 2028 fire's thermal footprint consistent with 8,500 acres.",
      "observation", "ground_truth", belief_holder="Elena_Volkov",
      dt="2033-08-25", source_id="satellite-analysis", source_type="remote_sensing")
    M("C07", "Sarah_Whitehorse", "revised_fire_models", "using_correct_8500",
      "Sarah Whitehorse re-ran her fire behavior models with the corrected 8,500-acre Ridge Fire comparison, finding the Cascade Creek fire's trajectory was actually closer to a 2031 Valley Creek fire pattern.",
      "event", "ground_truth", belief_holder="Sarah_Whitehorse",
      dt="2033-08-26", source_id="analyst-revision", source_type="internal_memo")

    # ── Additional background ──
    bg_round3 = [
        ("fire_perimeter_estimation", "standard_error", "varies_by_method", "Standard error ranges for fire perimeter estimation: ground visual ±25-35%, satellite thermal ±10-20%, aerial FLIR ±3-8%, post-fire survey ±1-3%.", "2031-06-01"),
        ("containment_definition", "means", "no_fire_spread_beyond_line", "In fire terminology, 'containment' means a continuous fire line exists around the perimeter with no active fire spreading beyond it; it does not guarantee the line will hold under all conditions.", "2031-06-01"),
        ("WEA_system", "depends_on", "functioning_cell_towers", "Wireless Emergency Alerts depend on functioning cellular infrastructure in the target area; if towers are damaged or overloaded, alerts may not reach all devices.", "2031-09-01"),
        ("resource_tracking_systems", "historically", "update_delayed", "Resource tracking systems in multi-agency fire responses have historically suffered from update delays when assets cross jurisdictional boundaries.", "2031-01-01"),
        ("fire_weather_forecasting", "inherent_uncertainty", "2_to_6_hours", "Fire weather forecasting in complex terrain has inherent timing uncertainty of 2-6 hours for wind shift events due to interactions between synoptic and local wind patterns.", "2031-06-01"),
        ("structure_triage_categories", "include", "destroyed_damaged_threatened", "Post-fire structure triage uses three categories: destroyed (>50% wall/roof loss), damaged (repairable structural damage), and threatened (exposure only, no structural damage).", "2031-09-01"),
        ("fire_history_databases", "maintained_by", "multiple_agencies", "Fire history databases are maintained by multiple agencies (CWRN, state forestry, USFS) with varying data quality standards and update frequencies.", "2031-01-01"),
        ("Pacific_Northwest_fire_ecology", "shaped_by", "dry_east_wet_west", "Pacific Northwest fire ecology is shaped by the Cascade divide: dry east-side forests have frequent fire regimes; wet west-side forests have infrequent but severe fire events.", "2031-01-01"),
        ("CWRN_communications", "use", "radio_satellite_phone_email", "CWRN communications infrastructure includes VHF radio (primary), satellite phone (backup), cellular (supplementary), and email (administrative).", "2031-03-01"),
        ("interagency_coordination", "challenges", "different_systems", "Interagency fire coordination is challenged by different tracking systems, communication protocols, and command structures across cooperating agencies.", "2031-01-01"),
        ("fire_retardant", "effectiveness", "depends_on_timing", "Fire retardant effectiveness depends critically on delivery timing — a drop on an advancing fire head is far more effective than the same drop an hour later on an established front.", "2031-06-01"),
        ("smoke_column", "can_obscure", "ground_observations", "Dense smoke columns from active fires can severely limit ground-level visibility, making it impossible for ground crews to assess fire perimeters more than a few hundred meters away.", "2031-06-01"),
        ("GPS_tracking", "accuracy", "3_to_10_meters", "GPS handheld accuracy ranges from 3-10 meters in open terrain but degrades to 15-30 meters under heavy canopy, affecting perimeter mapping precision.", "2031-03-01"),
        ("evacuation_verification", "best_practice", "door_to_door", "Best practice for evacuation verification is door-to-door canvassing, but this is resource-intensive and typically reserved for imminent-threat situations.", "2031-09-01"),
        ("mutual_aid_protocol", "requires", "notification_chain", "Mutual aid protocol requires the state coordination center to notify both the providing and receiving agencies when diverting shared resources between incidents.", "2031-01-01"),
    ]
    for subj, pred, obj, text, dt in bg_round3:
        M("background", subj, pred, obj, text,
          "fact", "ground_truth", dt=dt,
          source_id="cwrn-reference", source_type="reference_document",
          scope="public", confidence=0.95)

    # ── Queries round 3 ──
    Q("What was the largest single gap between an observer's fire size estimate and the verified figure?",
      "quantitative_comparison",
      ["Diego Ruiz's ground estimate of 500 acres was 280 acres (36%) below the verified 780 acres — the largest gap. The satellite was off by 130 acres (17%), and the aerial by only 20 acres (2.6%)."],
      ["Ground estimate had the largest gap at 280 acres"],
      ["All estimates were equally close"],
      [], [], difficulty="medium",
      notes="Requires comparing multiple belief states against verified truth")

    Q("What was the precise time window during which CWRN believed the western flank was contained when it actually wasn't?",
      "temporal_belief_gap",
      ["From 16:00 August 20 (Diego's report) to 05:30 August 21 (Tom's aerial confirmation of breach) — a 13.5-hour window. The actual breach began around 22:00 with ember transport, so the belief was false for about 7.5 hours."],
      ["Belief false from ~22:00 Aug 20 to ~05:30 Aug 21, about 7.5 hours"],
      ["The belief was never wrong"],
      [], [], disambig=True,
      notes="Tests distinguishing when belief became wrong vs when it was corrected")

    Q("How many people were at risk during the Zone 3 evacuation belief gap?",
      "consequence_of_belief",
      ["31 people in 12 households were in the fire path during the 2-hour window (18:00-20:00) when CWRN believed the zone was clear. The fire front was approximately 2 miles away with an estimated 4-hour window."],
      ["31 people, 2 miles from fire front"],
      ["Everyone was safely evacuated"],
      [], [])

    Q("What was Nadia Al-Rashid's explanation for the shelter registration gap?",
      "belief_attribution",
      ["Nadia assumed the 31-person gap between shelter registrations and expected evacuees was due to self-evacuation, a common pattern in previous zone evacuations. This assumption was incorrect."],
      ["Assumed self-evacuation based on past patterns"],
      ["Nadia knew people were still in the zone"],
      [], [], difficulty="medium")

    Q("How did the Klamath Complex fire's priority compare to CWRN's planned use of Tanker-3?",
      "belief_vs_reality",
      ["The Klamath Complex's incident commander cited critical structure protection needs that outranked CWRN's planned retardant drop through the state coordination priority system. CWRN was unaware of this prioritization."],
      ["Klamath had higher priority but CWRN didn't know"],
      ["CWRN had the highest priority"],
      [], [])

    Q("What was the crew chief's first indication that the wind shift had already occurred on August 28?",
      "witness_account",
      ["The burnback crew chief observed fire moving southeast instead of the expected northwest at 04:10, reporting 'the fire isn't doing what it's supposed to' — the first human observation of the already-shifted conditions."],
      ["Fire behavior inconsistent with expected wind direction at 04:10"],
      ["Weather instruments detected it first"],
      [], [], difficulty="medium")

    Q("How did James Park react to the wind shift forecasting failure?",
      "belief_attribution",
      ["James acknowledged post-incident that he should have flagged the known 2-4 hour timing uncertainty in the forecast and recommended a wider safety window for the burnback operation."],
      ["Acknowledged he should have communicated forecast uncertainty"],
      ["James denied any forecasting error"],
      [], [], difficulty="medium")

    Q("Why did local media report multiple conflicting damage numbers for the Cascade Creek fire?",
      "information_chain",
      ["Media reported the numbers as they were released over weeks: aerial rapid assessment (23), ground survey (31), insurance claims (28), without context about why each tier produces different counts. The final verified count (29) came weeks later."],
      ["Sequential release of different-methodology counts without context"],
      ["Media fabricated numbers"],
      [], [], difficulty="medium")

    Q("How did Elena Volkov discover the Ridge Fire database error?",
      "factual_retrieval",
      ["Elena cross-referenced CWRN's fire history database against Sat-Sentinel's historical satellite archive, which showed the 2028 Ridge Fire's thermal footprint consistent with 8,500 acres — not the 12,000 listed in the database."],
      ["Cross-referenced database against satellite archive"],
      ["Another analyst pointed out the error"],
      [], [], difficulty="easy")

    Q("What did Sarah Whitehorse find when she re-ran models with the corrected Ridge Fire figure?",
      "consequence_of_belief",
      ["Sarah found that the Cascade Creek fire's trajectory was actually closer to a 2031 Valley Creek fire pattern than the Ridge Fire, suggesting the original comparison was not only inflated but also a poor match."],
      ["Better match with Valley Creek fire, not Ridge Fire"],
      ["The corrected figure didn't change the models"],
      [], [])

    Q("If you could only trust one observation source during the Cascade Creek fire, which should it be and why?",
      "source_reliability",
      ["Based on verified results, aerial FLIR was the most consistently accurate: it was closest on fire perimeter (800 vs 780 actual), provided the first confirmation of the containment breach, and identified the initial damage count baseline. However, it couldn't detect the communication failure that affected evacuation."],
      ["Aerial FLIR, based on accuracy track record in this fire"],
      ["Ground crews were most reliable for all purposes"],
      [], [],
      notes="Tests nuanced source reliability assessment")

    Q("At what point during the Cascade Creek fire did CWRN's collective belief state most closely match objective reality?",
      "temporal_belief_gap",
      ["Post-fire mapping on September 10 and the county assessor's verified count on October 15 brought CWRN's records closest to reality. During active operations, the belief-reality gap was persistent and significant across all seven incident types."],
      ["Only after active operations ended, during formal post-incident reviews"],
      ["During active operations, beliefs were generally accurate"],
      [], [],
      notes="Tests understanding that real-time operations inherently involve belief-reality gaps")

    Q("What common thread connects the Zone 3 evacuation failure and the Tanker-3 position error?",
      "cross_case_synthesis",
      ["Both involved communication system failures: the cell tower outage prevented evacuation alerts reaching Zone 3's southern sector, while the email to a generic unmonitored inbox prevented CWRN from learning about Tanker-3's diversion. Both highlight single-channel communication vulnerabilities."],
      ["Communication system failures creating information gaps"],
      ["Both were caused by deliberate deception"],
      [], [],
      notes="Cross-case synthesis linking C03 and C04 through communication failure theme")

    Q("How did CWRN's resource decisions differ when based on belief states vs objective states?",
      "meta_analysis",
      ["Every belief-based decision was suboptimal: resource allocation based on 700 acres (not 780), crew reallocation based on false containment, air support planned around absent Tanker-3, burnback timed to wrong forecast. In each case, the objective state would have produced a different, better decision."],
      ["All belief-based decisions were suboptimal relative to what objective truth would have produced"],
      ["Belief-based decisions were generally adequate"],
      [], [],
      notes="Meta-analysis of belief-vs-reality impact on decision quality")

    Q("Was Marcus Chen's 700-acre compromise a reasonable decision given the information available?",
      "decision_evaluation",
      ["The compromise was politically understandable but analytically wrong — Sarah Whitehorse recommended the aerial estimate, which proved nearest to truth. However, no observer had the verified figure at the time, and averaging conflicting sources is a common real-time heuristic."],
      ["Understandable heuristic but suboptimal; the expert recommendation was better"],
      ["Chen made the perfect decision"],
      [], [],
      uncertainty=True, disambig=True,
      notes="Tests nuanced evaluation of decisions under uncertainty")

    Q("What standard operating procedures were violated during the Cascade Creek fire?",
      "procedure_compliance",
      ["The SOP requiring multi-source confirmation before status changes was arguably violated in C02 (containment declared on ground-only report without aerial confirmation) and C03 (evacuation declared complete without multi-channel verification). C04 involved a state-level protocol failure rather than CWRN SOP violation."],
      ["C02 and C03 involved SOP violations; C04 was external protocol failure"],
      ["No SOPs were violated"],
      [], [],
      disambig=True)

    Q("Could the Zone 3 evacuation failure have been prevented if the fire had not damaged the cell tower?",
      "counterfactual",
      ["Likely yes — if the cell tower remained operational, Wireless Emergency Alerts would have reached the 40 households in southern Zone 3, and most or all would have self-evacuated or been at the bus stops. However, the incident also exposed the single-channel notification dependency."],
      ["Probably prevented, but the underlying single-channel vulnerability would remain"],
      ["The cell tower was irrelevant to the failure"],
      [], [],
      uncertainty=True,
      notes="Counterfactual requiring belief vs reality distinction")

    Q("What is the relationship between observation methodology and belief accuracy in the Cascade Creek fire?",
      "meta_analysis",
      ["Higher-technology observation methods (FLIR aerial, satellite thermal) produced beliefs closer to objective reality than lower-technology methods (visual ground observation, schedule-based tracking, single-channel alerts). But no method eliminated the gap entirely — each had specific blind spots."],
      ["Technology correlates with accuracy but doesn't eliminate belief-reality gaps"],
      ["All methods are equally accurate"],
      [], [],
      notes="Meta-analysis of methodology-accuracy relationship")

    Q("How many distinct types of belief-reality divergence are represented in the Cascade Creek incidents?",
      "taxonomy",
      ["At least five types: (1) observation limitation (C01 — methods can't see full picture), (2) temporal obsolescence (C02 — correct belief becomes wrong), (3) verification gap (C03 — assumed completeness without verification), (4) stale data (C04 — tracking system not updated), (5) forecast error (C05 — prediction differs from outcome), (6) methodology difference (C06 — methods produce different counts), (7) data entry error (C07 — wrong value in database)"],
      ["Seven distinct types of belief-reality divergence"],
      ["Only one type of divergence exists"],
      [], [],
      notes="Taxonomy query requiring classification of divergence types")

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
