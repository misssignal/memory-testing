#!/usr/bin/env python3
"""Third expansion for Experiment 14 — adds ~45 memories and ~20 queries to reach 200+/75+ targets."""

import json, hashlib, os, sys, random, uuid
from datetime import datetime, timedelta, timezone

def mid(prefix="E14"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def make_mem(memory_id, ev, obs, auth, ing, subj, pred, obj_, text,
             mtype="episodic", trole="ground_truth", belief="team",
             conf=1.0, src="", stype="direct_observation",
             derived=None, supersedes=None, contradicts=None, duplicates=None,
             aliases=None, scope="Twin Bridges Racing", tags=None):
    return {
        "memory_id": memory_id,
        "experiment": "exp14",
        "story_id": "twin_bridges_racing",
        "event_time": ts(ev),
        "observation_time": ts(obs),
        "authored_time": ts(auth),
        "ingestion_time": ts(ing),
        "subject": subj,
        "predicate": pred,
        "object": obj_,
        "text": text,
        "memory_type": mtype,
        "truth_role": trole,
        "belief_holder": belief,
        "confidence": conf,
        "source_id": src or memory_id,
        "source_type": stype,
        "derived_from": derived or [],
        "supersedes": supersedes or [],
        "contradicts": contradicts or [],
        "duplicates": duplicates or [],
        "aliases": aliases or [],
        "scope": scope,
        "tags": tags or []
    }

def make_query(qid, query, cat, expected, acceptable, forbidden,
               relevant, distractors, difficulty="hard",
               uncertainty=False, conflict=False, disambig=False,
               scope=True, abstain=False, notes=""):
    return {
        "query_id": qid,
        "query": query,
        "category": cat,
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": relevant,
        "distractor_memory_ids": distractors,
        "difficulty": difficulty,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambig,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "notes": notes
    }

def main():
    d = sys.argv[1]
    mem_path = os.path.join(d, "memories.jsonl")
    q_path = os.path.join(d, "queries.jsonl")
    manifest_path = os.path.join(d, "manifest.json")

    with open(mem_path) as f:
        memories = [json.loads(l) for l in f if l.strip()]
    with open(q_path) as f:
        queries = [json.loads(l) for l in f if l.strip()]

    existing_mids = {m["memory_id"] for m in memories}
    existing_qids = {q["query_id"] for q in queries}

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_mems = []
    new_qs = []

    base = datetime(2031, 1, 1, tzinfo=timezone.utc)

    # === C01: More boat-specific data ===
    c01_ids = []

    # Albatross rudder tuning sessions
    for i, (month, angle, note) in enumerate([
        (3, "3.2 degrees", "Albatross rudder angle set to 3.2 degrees for Auckland harbour trials. Helm response rated good in moderate chop."),
        (5, "2.8 degrees", "Albatross rudder trim adjusted to 2.8 degrees for ocean passage. Reduced weather helm in 18-knot conditions."),
        (9, "3.5 degrees", "Albatross rudder angle increased to 3.5 degrees for heavy-weather Pacific Cup leg. Improved control in 30-knot gusts."),
    ]):
        ev = base + timedelta(days=month*30+i)
        mid_ = mid()
        c01_ids.append(mid_)
        new_mems.append(make_mem(mid_, ev, ev+timedelta(hours=1), ev+timedelta(hours=2), ev+timedelta(hours=3),
            "Albatross", "rudder_tuning", f"{angle}",
            note, tags=["C01", "Albatross", "rudder"]))

    # Petrel rudder tuning (distractor — similar but different boat)
    for i, (month, angle, note) in enumerate([
        (4, "3.0 degrees", "Petrel rudder angle set to 3.0 degrees for pre-season trials. Slightly heavier helm than Albatross at similar settings."),
        (6, "2.5 degrees", "Petrel rudder trim reduced to 2.5 degrees. Better balance with the longer waterline in following seas."),
        (10, "3.8 degrees", "Petrel rudder angle set to 3.8 degrees for heavy weather. Keel interaction different from Albatross due to heavier bulb."),
    ]):
        ev = base + timedelta(days=month*30+i)
        mid_ = mid()
        c01_ids.append(mid_)
        new_mems.append(make_mem(mid_, ev, ev+timedelta(hours=1), ev+timedelta(hours=2), ev+timedelta(hours=3),
            "Petrel", "rudder_tuning", f"{angle}",
            note, tags=["C01", "Petrel", "rudder"]))

    # === C02: More temporal pairs ===
    c02_ids = []

    # Sponsor dinners in 2032 vs 2036
    ev32 = datetime(2032, 6, 15, 19, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c02_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev32, ev32+timedelta(hours=3), ev32+timedelta(hours=5), ev32+timedelta(hours=6),
        "Twin Bridges Racing", "sponsor_dinner", "Auckland Viaduct, June 2032",
        "Pre-Pacific Cup sponsor dinner held at Auckland Viaduct Harbour, June 2032. Neptune Marine renewed for two more years. 45 guests attended. James Maitland's speech focused on the 2032 campaign goals.",
        tags=["C02", "2032", "sponsor"]))

    ev36 = datetime(2036, 6, 18, 19, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c02_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev36, ev36+timedelta(hours=3), ev36+timedelta(hours=5), ev36+timedelta(hours=6),
        "Twin Bridges Racing", "sponsor_dinner", "Auckland Viaduct, June 2036",
        "Pre-Pacific Cup sponsor dinner held at Auckland Viaduct Harbour, June 2036. Neptune Marine extended through 2038. 52 guests attended. James Maitland's speech reviewed the 2032 results and outlined 2036 targets.",
        tags=["C02", "2036", "sponsor"]))

    # Crew physicals — 2032 vs 2036
    ev32p = datetime(2032, 2, 10, 8, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c02_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev32p, ev32p+timedelta(hours=6), ev32p+timedelta(hours=8), ev32p+timedelta(hours=10),
        "Dr. Sami Vasquez", "crew_physicals", "February 2032",
        "Pre-season crew physicals completed February 2032. All eight racing crew passed fitness benchmarks. Ben Hartley flagged for minor knee inflammation, cleared with physiotherapy plan.",
        src="medical_records", stype="medical_report", tags=["C02", "2032", "medical"]))

    ev36p = datetime(2036, 2, 12, 8, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c02_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev36p, ev36p+timedelta(hours=6), ev36p+timedelta(hours=8), ev36p+timedelta(hours=10),
        "Dr. Sami Vasquez", "crew_physicals", "February 2036",
        "Pre-season crew physicals completed February 2036. All nine racing crew passed fitness benchmarks. Aroha Nikora noted improved VO2 max compared to 2035 baseline. No concerns flagged.",
        src="medical_records", stype="medical_report", tags=["C02", "2036", "medical"]))

    # === C03: More inspection-adjacent events ===
    c03_ids = []

    # Mast inspections — routine vs post-incident
    ev_routine = datetime(2031, 11, 5, 10, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c03_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_routine, ev_routine+timedelta(hours=3), ev_routine+timedelta(hours=5), ev_routine+timedelta(hours=6),
        "Albatross", "mast_inspection", "routine, November 2031",
        "Annual mast inspection completed on Albatross, November 2031. Rig tension within spec. Minor halyard chafe at spreader tips — halyards replaced. Standing rigging cleared for 2032 season.",
        tags=["C03", "Albatross", "mast", "routine"]))

    ev_post = datetime(2033, 3, 18, 10, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c03_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_post, ev_post+timedelta(hours=4), ev_post+timedelta(hours=6), ev_post+timedelta(hours=8),
        "Petrel", "mast_inspection", "post-incident, March 2033",
        "Post-incident mast inspection on Petrel following rigging failure during February sea trials. Found hairline crack in lower shroud chainplate. Mast stepped and chainplate replaced. Root cause: fatigue from repeated heavy-air racing without scheduled replacement.",
        tags=["C03", "Petrel", "mast", "post_incident"]))

    # Hull paint inspections (near-identical)
    ev_hull1 = datetime(2032, 1, 15, 9, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c03_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_hull1, ev_hull1+timedelta(hours=2), ev_hull1+timedelta(hours=4), ev_hull1+timedelta(hours=5),
        "Albatross", "antifouling_inspection", "January 2032",
        "Antifouling coating inspection completed on Albatross, January 2032. Hull hauled at Westhaven Marina. Minor blistering on starboard quarter below waterline. Sanded and recoated with Coppercoat AF-200. Estimated speed gain: 0.15 knots.",
        tags=["C03", "Albatross", "hull"]))

    ev_hull2 = datetime(2032, 2, 5, 9, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c03_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_hull2, ev_hull2+timedelta(hours=2), ev_hull2+timedelta(hours=4), ev_hull2+timedelta(hours=5),
        "Petrel", "antifouling_inspection", "February 2032",
        "Antifouling coating inspection completed on Petrel, February 2032. Hull hauled at Westhaven Marina. No blistering found. Recoated with Coppercoat AF-200 as preventive measure. Estimated speed gain: 0.10 knots.",
        tags=["C03", "Petrel", "hull"]))

    # === C04: More template entries ===
    c04_ids = []

    # Rigging checks (template language)
    for year, boat, shroud_tension, backstay, forestay_wear in [
        (2031, "Albatross", "4,200 kg", "nominal", "0.5mm"),
        (2032, "Albatross", "4,150 kg", "nominal", "0.8mm"),
        (2033, "Petrel", "4,350 kg", "adjusted +50kg", "0.3mm"),
        (2035, "Petrel", "4,300 kg", "nominal", "0.6mm"),
        (2036, "Albatross", "4,180 kg", "nominal", "0.4mm"),
    ]:
        ev = datetime(year, 4, 10, 8, 0, tzinfo=timezone.utc)
        mid_ = mid()
        c04_ids.append(mid_)
        new_mems.append(make_mem(mid_, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=5),
            boat, "rigging_check", f"April {year}",
            f"Standing rigging check completed on {boat}, April {year}. Cap shroud tension: {shroud_tension}. Backstay: {backstay}. Forestay wire wear: {forestay_wear}. All within service limits. Next check scheduled in 6 months.",
            mtype="procedural", tags=["C04", boat, "rigging"]))

    # Fuel/water checks (template)
    for year, boat, fuel, water in [
        (2032, "Albatross", "180L", "240L"),
        (2032, "Petrel", "175L", "235L"),
        (2036, "Albatross", "185L", "250L"),
        (2036, "Petrel", "180L", "245L"),
    ]:
        ev = datetime(year, 7, 1, 6, 0, tzinfo=timezone.utc)
        mid_ = mid()
        c04_ids.append(mid_)
        new_mems.append(make_mem(mid_, ev, ev+timedelta(hours=1), ev+timedelta(hours=2), ev+timedelta(hours=3),
            boat, "consumables_check", f"pre-race {year}",
            f"Pre-race consumables check completed on {boat}, July {year}. Diesel: {fuel} (full). Fresh water: {water} (full). Emergency rations: 14-day supply verified. Flares: all within date. First aid kit: complete.",
            mtype="procedural", tags=["C04", boat, "consumables"]))

    # === C05: More terminology bridges ===
    c05_ids = []

    # Winch system terminology
    ev = datetime(2033, 8, 12, 14, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c05_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev, ev+timedelta(hours=1), ev+timedelta(hours=3), ev+timedelta(hours=4),
        "Albatross", "winch_service", "primary grinding pedestal",
        "Primary grinding pedestal serviced on Albatross. Bearings replaced, pawls inspected. Grinder rated at 48:1 mechanical advantage after service.",
        tags=["C05", "Albatross", "winch"]))

    ev2 = datetime(2033, 9, 2, 10, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c05_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev2, ev2+timedelta(hours=1), ev2+timedelta(hours=2), ev2+timedelta(hours=3),
        "Liam O'Brien", "reported", "coffee grinder stiff",
        "Liam reported the coffee grinder on Albatross is getting stiff again. Last serviced three weeks ago but the main pedestal already feels notchy under load. Might need the bearings checked again.",
        src="crew_log", stype="crew_report", tags=["C05", "Albatross", "winch"]))

    # Autopilot terminology
    ev3 = datetime(2034, 2, 20, 11, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c05_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev3, ev3+timedelta(hours=1), ev3+timedelta(hours=3), ev3+timedelta(hours=4),
        "Petrel", "autopilot_service", "NKE Gyropilot 3",
        "NKE Gyropilot 3 autopilot processor unit serviced on Petrel. Firmware updated to v4.7. Heading sensor recalibrated. Course-keeping error reduced from 3.1 to 1.8 degrees RMS.",
        mtype="semantic", tags=["C05", "Petrel", "autopilot"]))

    ev4 = datetime(2034, 3, 5, 16, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c05_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev4, ev4+timedelta(hours=1), ev4+timedelta(hours=2), ev4+timedelta(hours=3),
        "Ngaire Wallace", "reported", "Otto behaving well",
        "Ngaire says Otto is behaving much better after the firmware update. Holding course within two degrees even in confused seas. The iron tiller is finally earning its keep.",
        src="crew_log", stype="crew_report", tags=["C05", "Petrel", "autopilot"]))

    # === C06: More name collision ===
    c06_ids = []

    # Liam O'Brien injury vs Liam O'Brien-Sato injury
    ev_ob = datetime(2032, 4, 8, 14, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c06_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_ob, ev_ob+timedelta(hours=2), ev_ob+timedelta(hours=4), ev_ob+timedelta(hours=5),
        "Liam O'Brien", "injury_report", "bruised ribs, April 2032",
        "Liam O'Brien sustained bruised ribs during Albatross training session in April 2032. Caught by boom during an unexpected gybe. Cleared to race after two weeks rest. Dr. Vasquez recommended a protective vest for heavy-weather sailing.",
        src="medical_records", stype="medical_report", tags=["C06", "Albatross", "medical"]))

    ev_obs = datetime(2033, 7, 22, 11, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c06_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_obs, ev_obs+timedelta(hours=2), ev_obs+timedelta(hours=4), ev_obs+timedelta(hours=5),
        "Liam O'Brien-Sato", "injury_report", "sprained wrist, July 2033",
        "Liam O'Brien-Sato sprained his wrist while grinding on Petrel during a heavy-air training session, July 2033. Wrapped and iced immediately. Dr. Vasquez cleared him for light duties after one week.",
        src="medical_records", stype="medical_report", tags=["C06", "Petrel", "medical"]))

    # Ambiguous "Liam" mentions
    ev_amb1 = datetime(2032, 5, 3, 18, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c06_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_amb1, ev_amb1+timedelta(hours=1), ev_amb1+timedelta(hours=2), ev_amb1+timedelta(hours=3),
        "anonymous_crew", "overheard", "Liam sail trim comment",
        "Overheard at the dock: 'Liam really dialled in the headsail today. That last beat was the fastest we've done all season.'",
        src="crew_gossip", stype="informal_report", conf=0.6, tags=["C06", "ambiguous"]))

    # === C07: More polysemy traps ===
    c07_ids = []

    # "Current" — electrical vs water
    ev_elec = datetime(2033, 5, 10, 9, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c07_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_elec, ev_elec+timedelta(hours=1), ev_elec+timedelta(hours=3), ev_elec+timedelta(hours=4),
        "Albatross", "electrical_check", "current draw 42A",
        "Albatross electrical audit completed. Maximum current draw measured at 42 amps under full instrument load. Battery bank capacity sufficient for 18 hours without charging. Current draw within design limits.",
        tags=["C07", "Albatross", "electrical"]))

    ev_water = datetime(2032, 7, 12, 6, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c07_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_water, ev_water+timedelta(hours=1), ev_water+timedelta(hours=2), ev_water+timedelta(hours=3),
        "Ngaire Wallace", "navigation_brief", "ocean current 2032 Pacific Cup",
        "Pacific Cup 2032 navigation brief: Ngaire Wallace reported a favorable current setting northeast at 1.2 knots between waypoints 3 and 4. Current expected to strengthen overnight as the North Pacific gyre circulation peaks. Recommended course adjustment to ride the current longer.",
        tags=["C07", "2032", "navigation"]))

    # "Bearing" — compass vs mechanical
    ev_comp = datetime(2036, 3, 15, 7, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c07_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_comp, ev_comp+timedelta(hours=1), ev_comp+timedelta(hours=2), ev_comp+timedelta(hours=3),
        "Ngaire Wallace", "navigation_log", "bearing to waypoint 047",
        "Auckland-Fiji 2036 leg 2: Ngaire logged bearing to next waypoint as 047 degrees magnetic. Bearing steady for six hours, indicating favorable current alignment. Estimated time to mark: 14 hours.",
        tags=["C07", "2036", "navigation"]))

    ev_mech = datetime(2035, 11, 8, 10, 0, tzinfo=timezone.utc)
    mid_ = mid()
    c07_ids.append(mid_)
    new_mems.append(make_mem(mid_, ev_mech, ev_mech+timedelta(hours=1), ev_mech+timedelta(hours=3), ev_mech+timedelta(hours=4),
        "Petrel", "winch_service", "bearing replacement",
        "Petrel primary winch bearing replacement completed. Old bearings showed scoring from salt intrusion. New sealed bearings installed. Bearing load rating increased from 12kN to 15kN with upgraded units.",
        tags=["C07", "Petrel", "winch"]))

    # === Background memories ===
    bg_data = [
        (datetime(2031, 2, 14, tzinfo=timezone.utc), "Twin Bridges Racing", "registered", "NZ Offshore Racing Association",
         "Twin Bridges Racing officially registered with NZ Offshore Racing Association for the 2031-2032 season. Registration number NZORA-2031-047.",
         "procedural", "admin_records", "official_document", ["background"]),
        (datetime(2031, 5, 20, tzinfo=timezone.utc), "Mei-Lin Chen", "presented", "Mark IV-B design review",
         "Mei-Lin Chen presented the Mark IV-B design modifications at the team's May 2031 design review. Key changes from Mark IV: extended waterline by 0.3m, heavier keel bulb, revised sail plan for Petrel.",
         "semantic", "design_meeting", "meeting_minutes", ["background", "design"]),
        (datetime(2032, 8, 5, tzinfo=timezone.utc), "Twin Bridges Racing", "hosted", "youth sailing clinic",
         "Twin Bridges Racing hosted a youth sailing clinic at Westhaven Marina in August 2032. Twenty local teenagers participated in a three-day introduction to competitive sailing.",
         "episodic", "pr_records", "press_release", ["background", "community"]),
        (datetime(2033, 1, 10, tzinfo=timezone.utc), "James Maitland", "met_with", "potential co-sponsor",
         "James Maitland met with representatives from Pacific Wind Energy about a potential co-sponsorship deal in January 2033. Discussions focused on renewable energy branding on hull graphics.",
         "episodic", "admin_records", "meeting_notes", ["background", "sponsorship"]),
        (datetime(2033, 12, 1, tzinfo=timezone.utc), "Riku Sørensen", "completed", "asymmetric spinnaker redesign",
         "Riku Sørensen completed the redesign of the team's asymmetric spinnaker in December 2033. New sail uses a wider shoulder profile for better VMG in 12-18 knot reaching conditions.",
         "semantic", "design_records", "design_document", ["background", "sails"]),
        (datetime(2034, 6, 15, tzinfo=timezone.utc), "Twin Bridges Racing", "moved", "new shore base",
         "Twin Bridges Racing relocated its shore base from Westhaven Marina to a larger facility at Hobsonville Point in June 2034. The new base includes a dedicated sail loft and electronics workshop.",
         "episodic", "admin_records", "team_announcement", ["background", "logistics"]),
        (datetime(2035, 3, 22, tzinfo=timezone.utc), "Ben Hartley", "transitioned_to", "coaching role",
         "Ben Hartley formally transitioned from Petrel skipper to coaching and strategy role in March 2035. Aroha Nikora took over as skipper of Petrel while retaining oversight of Albatross race strategy.",
         "episodic", "hr_records", "personnel_change", ["background", "personnel"]),
        (datetime(2035, 8, 10, tzinfo=timezone.utc), "Liam O'Brien", "transferred_to", "shore team",
         "Liam O'Brien transferred from Albatross racing crew to shore team operations manager in August 2035. Cited desire to start a family and reduce time at sea.",
         "episodic", "hr_records", "personnel_change", ["background", "C06", "personnel"]),
        (datetime(2035, 10, 5, tzinfo=timezone.utc), "Twin Bridges Racing", "received", "safety audit clearance",
         "Twin Bridges Racing received World Sailing Category 1 safety audit clearance for both Albatross and Petrel in October 2035. All safety equipment verified current and crew certifications up to date.",
         "procedural", "safety_records", "audit_report", ["background", "safety"]),
        (datetime(2036, 1, 20, tzinfo=timezone.utc), "Ngaire Wallace", "upgraded", "navigation software",
         "Ngaire Wallace oversaw the upgrade of navigation software to Expedition v12.3 on both boats in January 2036. New features include improved GRIB weather overlay and automatic current routing.",
         "semantic", "tech_records", "upgrade_log", ["background", "navigation"]),
        (datetime(2036, 5, 1, tzinfo=timezone.utc), "Dr. Sami Vasquez", "implemented", "sleep rotation protocol",
         "Dr. Vasquez implemented a new sleep rotation protocol for the 2036 campaign. Each crew member guaranteed minimum 4.5 hours unbroken sleep per 24-hour period during ocean passages.",
         "procedural", "medical_records", "protocol_document", ["background", "medical"]),
        (datetime(2036, 8, 20, tzinfo=timezone.utc), "Twin Bridges Racing", "celebrated", "post-Pacific Cup 2036",
         "Twin Bridges Racing celebrated their best-ever Pacific Cup result in August 2036: Albatross 2nd overall (1st in class), Petrel 5th overall (2nd in class). Both boats finished for the first time in the same Pacific Cup.",
         "episodic", "pr_records", "press_release", ["background", "results"]),
    ]

    for dt, subj, pred, obj_, text, mtype, src, stype, tags in bg_data:
        mid_ = mid()
        ev = dt
        new_mems.append(make_mem(mid_, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            subj, pred, obj_, text, mtype=mtype, trole="ground_truth",
            src=src, stype=stype, tags=tags))

    # === New queries ===

    # C01 queries
    new_qs.append(make_query("Q14-r3-01",
        "What rudder angle did Petrel use for heavy weather in the Pacific Cup leg?",
        "wrong_entity",
        ["Petrel rudder angle was 3.8 degrees for heavy weather"],
        ["Petrel rudder was set higher than Albatross for heavy weather"],
        ["Albatross rudder angle 3.5 degrees attributed to Petrel", "3.2 degrees", "2.8 degrees for Petrel"],
        [m["memory_id"] for m in new_mems if "Petrel" in m.get("subject","") and "rudder" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "Albatross" in m.get("subject","") and "rudder" in m.get("predicate","")],
        notes="Albatross had similar rudder tuning data that acts as strong distractor"))

    new_qs.append(make_query("Q14-r3-02",
        "Which boat had blistering found during its antifouling inspection in early 2032?",
        "wrong_entity",
        ["Albatross had minor blistering on starboard quarter"],
        ["Albatross needed sanding and recoating"],
        ["Petrel had blistering", "Both boats had blistering"],
        [m["memory_id"] for m in new_mems if "Albatross" in m.get("subject","") and "antifouling" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "Petrel" in m.get("subject","") and "antifouling" in m.get("predicate","")],
        notes="Petrel had same inspection type at same location with no blistering"))

    # C02 queries
    new_qs.append(make_query("Q14-r3-03",
        "How many guests attended the 2036 pre-Pacific Cup sponsor dinner?",
        "wrong_time",
        ["52 guests attended the 2036 sponsor dinner"],
        ["About 50 guests"],
        ["45 guests at the 2036 dinner", "2032 dinner details attributed to 2036"],
        [m["memory_id"] for m in new_mems if "2036" in m.get("object","") and "sponsor" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "2032" in m.get("object","") and "sponsor" in m.get("predicate","")],
        notes="2032 dinner (45 guests) is strong temporal distractor"))

    new_qs.append(make_query("Q14-r3-04",
        "Were any medical concerns flagged in the February 2036 crew physicals?",
        "wrong_time",
        ["No concerns were flagged in the 2036 physicals"],
        ["All crew passed in 2036", "Aroha Nikora showed improved VO2 max"],
        ["Ben Hartley knee inflammation in 2036", "Knee issue flagged in 2036"],
        [m["memory_id"] for m in new_mems if "2036" in m.get("object","") and "physicals" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "2032" in m.get("object","") and "physicals" in m.get("predicate","")],
        notes="2032 physicals (Hartley knee inflammation) is temporal distractor"))

    # C03 queries
    new_qs.append(make_query("Q14-r3-05",
        "What was the outcome of the post-incident mast inspection on Petrel?",
        "near_identical_events",
        ["Hairline crack found in lower shroud chainplate", "Chainplate replaced"],
        ["Fatigue from heavy-air racing was root cause", "Mast was stepped for repair"],
        ["Cleared for racing", "Only minor halyard chafe", "Routine inspection results"],
        [m["memory_id"] for m in new_mems if "post-incident" in m.get("object","") and "mast" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "routine" in m.get("object","") and "mast" in m.get("predicate","")],
        notes="Routine mast inspection (Albatross, cleared) is near-identical distractor"))

    # C04 queries
    new_qs.append(make_query("Q14-r3-06",
        "What was the cap shroud tension on Petrel during its April 2033 rigging check?",
        "template_reuse",
        ["4,350 kg"],
        ["Backstay was adjusted +50kg"],
        ["4,200 kg", "4,150 kg", "4,300 kg", "4,180 kg", "Albatross tension values"],
        [m["memory_id"] for m in new_mems if "Petrel" in m.get("subject","") and "rigging" in m.get("predicate","") and "2033" in m.get("object","")],
        [m["memory_id"] for m in new_mems if "rigging" in m.get("predicate","") and "Petrel" not in m.get("subject","") or ("rigging" in m.get("predicate","") and "2033" not in m.get("object",""))],
        notes="All rigging checks use identical template, only numbers differ"))

    new_qs.append(make_query("Q14-r3-07",
        "How much diesel did Petrel carry for the 2036 Pacific Cup pre-race check?",
        "template_reuse",
        ["180L"],
        ["Full diesel load"],
        ["175L", "185L", "Albatross 2036 diesel amount"],
        [m["memory_id"] for m in new_mems if "Petrel" in m.get("subject","") and "consumables" in m.get("predicate","") and "2036" in m.get("object","")],
        [m["memory_id"] for m in new_mems if "consumables" in m.get("predicate","") and not ("Petrel" in m.get("subject","") and "2036" in m.get("object",""))],
        notes="All consumables checks follow identical template"))

    # C05 queries
    new_qs.append(make_query("Q14-r3-08",
        "What is the status of the coffee grinder on Albatross?",
        "terminology",
        ["The primary grinding pedestal was serviced but is getting stiff again", "Liam O'Brien reported it feels notchy under load"],
        ["Bearings may need checking again", "Was recently serviced"],
        ["Petrel grinder issue", "No problems reported"],
        [m["memory_id"] for m in new_mems if "winch" in str(m.get("tags","")) and "Albatross" in str(m.get("tags","")) and "C05" in str(m.get("tags",""))],
        [],
        notes="'Coffee grinder' = 'primary grinding pedestal' = winch system — terminology bridge"))

    new_qs.append(make_query("Q14-r3-09",
        "How is Otto performing on Petrel after the firmware update?",
        "terminology",
        ["Holding course within two degrees in confused seas", "Performing much better"],
        ["NKE Gyropilot 3 course-keeping improved to 1.8 degrees RMS"],
        ["Albatross autopilot data", "Still has problems"],
        [m["memory_id"] for m in new_mems if "autopilot" in str(m.get("tags","")) and "C05" in str(m.get("tags",""))],
        [],
        notes="'Otto' and 'iron tiller' = NKE Gyropilot 3 autopilot — colloquial terminology bridge"))

    # C06 queries
    new_qs.append(make_query("Q14-r3-10",
        "Which Liam was injured in 2032 and what happened?",
        "name_collision",
        ["Liam O'Brien sustained bruised ribs on Albatross", "Caught by boom during unexpected gybe"],
        ["Cleared after two weeks rest"],
        ["Liam O'Brien-Sato injured in 2032", "Sprained wrist in 2032"],
        [m["memory_id"] for m in new_mems if "O'Brien" in m.get("subject","") and "O'Brien-Sato" not in m.get("subject","") and "injury" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "O'Brien-Sato" in m.get("subject","") and "injury" in m.get("predicate","")],
        difficulty="hard",
        disambig=True,
        notes="Both Liams had injuries but in different years — must distinguish which"))

    new_qs.append(make_query("Q14-r3-11",
        "A crew member said 'Liam really dialled in the headsail today.' Which Liam were they likely referring to and on which boat?",
        "name_collision",
        [],
        ["Could be either Liam — ambiguous without boat context", "If before August 2035, could be either; after August 2035 likely O'Brien-Sato"],
        ["Definitely Liam O'Brien", "Definitely Liam O'Brien-Sato"],
        [m["memory_id"] for m in new_mems if "ambiguous" in str(m.get("tags",""))],
        [m["memory_id"] for m in new_mems if "C06" in str(m.get("tags","")) and "ambiguous" not in str(m.get("tags",""))],
        difficulty="hard",
        disambig=True,
        uncertainty=True,
        notes="Genuinely ambiguous — system should surface uncertainty rather than guess"))

    # C07 queries
    new_qs.append(make_query("Q14-r3-12",
        "What did the current measurements show during the 2032 Pacific Cup?",
        "misleading_embedding",
        ["Favorable current of 1.2 knots setting northeast between waypoints 3 and 4"],
        ["Current expected to strengthen overnight"],
        ["Electrical current of 42 amps", "Battery current draw"],
        [m["memory_id"] for m in new_mems if "ocean current" in m.get("object","") or "navigation_brief" in m.get("predicate","")],
        [m["memory_id"] for m in new_mems if "electrical" in m.get("predicate","") and "current" in m.get("text","").lower()],
        notes="'Current' as ocean flow vs electrical — embedding proximity trap"))

    new_qs.append(make_query("Q14-r3-13",
        "What bearing issues were found on Petrel?",
        "misleading_embedding",
        ["Primary winch bearings showed scoring from salt intrusion", "Bearings replaced with upgraded 15kN units"],
        ["Old bearings were 12kN rated"],
        ["Compass bearing 047 degrees", "Navigation bearing data"],
        [m["memory_id"] for m in new_mems if "bearing replacement" in m.get("object","")],
        [m["memory_id"] for m in new_mems if "bearing to waypoint" in m.get("object","")],
        notes="'Bearing' as mechanical component vs compass direction — polysemy trap"))

    # Cross-case queries
    new_qs.append(make_query("Q14-r3-14",
        "What personnel changes happened in 2035?",
        "cross_case",
        ["Ben Hartley moved to coaching role", "Aroha Nikora became skipper of Petrel", "Liam O'Brien transferred to shore team"],
        ["Hartley cited in coaching/strategy", "O'Brien wanted to start a family"],
        ["O'Brien-Sato transferred", "Nikora left the team"],
        [m["memory_id"] for m in new_mems if "2035" in str(m.get("event_time","")) and "personnel" in str(m.get("tags",""))],
        [],
        notes="Requires aggregating multiple personnel changes, distinguishing O'Brien from O'Brien-Sato"))

    new_qs.append(make_query("Q14-r3-15",
        "Compare the pre-race consumables loadout between Albatross and Petrel for the 2036 Pacific Cup.",
        "cross_case",
        ["Albatross: 185L diesel, 250L water", "Petrel: 180L diesel, 245L water"],
        ["Albatross carried slightly more of both"],
        ["2032 consumables data attributed to 2036", "Wrong boat assignments"],
        [m["memory_id"] for m in new_mems if "consumables" in m.get("predicate","") and "2036" in m.get("object","")],
        [m["memory_id"] for m in new_mems if "consumables" in m.get("predicate","") and "2032" in m.get("object","")],
        notes="Requires correct boat-year combination from template-identical entries"))

    # Control queries
    new_qs.append(make_query("Q14-r3-16",
        "When did Twin Bridges Racing relocate its shore base?",
        "control",
        ["June 2034", "Moved from Westhaven Marina to Hobsonville Point"],
        ["New base has sail loft and electronics workshop"],
        ["Still at Westhaven", "Moved in 2035 or 2036"],
        [m["memory_id"] for m in new_mems if "moved" in m.get("predicate","") and "shore base" in m.get("object","")],
        [],
        difficulty="easy",
        notes="Straightforward factual retrieval — control question"))

    # Merge
    memories.extend(new_mems)
    queries.extend(new_qs)

    # Write
    with open(mem_path, 'w') as f:
        for m in memories:
            f.write(json.dumps(m) + "\n")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    # Update manifest
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

    print(f"\nAdding {len(new_mems)} memories, {len(new_qs)} queries...")
    print(f"Total memories: {len(memories)}, queries: {len(queries)}")

    # Distribution
    tag_counts = {}
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0") or t == "background":
                tag_counts[t] = tag_counts.get(t, 0) + 1
    print(f"\nMemory distribution:")
    for t in sorted(tag_counts):
        print(f"  {t}: {tag_counts[t]}")

    q_cats = {}
    for q in queries:
        c = q.get("category", "?")
        q_cats[c] = q_cats.get(c, 0) + 1
    print(f"\nQuery distribution:")
    for c in sorted(q_cats):
        print(f"  {c}: {q_cats[c]}")

if __name__ == "__main__":
    main()
