#!/usr/bin/env python3
"""Second expansion for Experiment 15 — adds ~60 memories and ~25 queries to approach 200+/75+."""

import json, hashlib, os, sys, uuid
from datetime import datetime, timedelta, timezone

def mid(prefix="E15"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def make_mem(memory_id, ev, obs, auth, ing, subj, pred, obj_, text,
             mtype="episodic", trole="ground_truth", belief="cooperative",
             conf=1.0, src="", stype="direct_observation",
             derived=None, supersedes=None, contradicts=None, duplicates=None,
             aliases=None, scope="Thornfield Agricultural Cooperative", tags=None):
    return {
        "memory_id": memory_id, "experiment": "exp15", "story_id": "thornfield_coop",
        "event_time": ts(ev), "observation_time": ts(obs),
        "authored_time": ts(auth), "ingestion_time": ts(ing),
        "subject": subj, "predicate": pred, "object": obj_, "text": text,
        "memory_type": mtype, "truth_role": trole, "belief_holder": belief,
        "confidence": conf, "source_id": src or memory_id, "source_type": stype,
        "derived_from": derived or [], "supersedes": supersedes or [],
        "contradicts": contradicts or [], "duplicates": duplicates or [],
        "aliases": aliases or [], "scope": scope, "tags": tags or []
    }

def make_query(qid, query, cat, expected, acceptable, forbidden,
               relevant, distractors, difficulty="hard",
               uncertainty=False, conflict=False, disambig=False,
               scope=True, abstain=False, notes=""):
    return {
        "query_id": qid, "query": query, "category": cat,
        "expected_claims": expected, "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": relevant, "distractor_memory_ids": distractors,
        "difficulty": difficulty,
        "must_surface_uncertainty": uncertainty, "must_surface_conflict": conflict,
        "must_disambiguate": disambig, "must_preserve_scope": scope,
        "should_abstain": abstain, "notes": notes
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

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_mems = []
    new_qs = []

    # === C01: Additional lab tests for Brewer Downs and Long Flat ===
    for farm, block, year, agri_vals, cant_vals in [
        ("Brewer Downs paddock 8", "BD-P8", 2031,
         ("5.4", "12 mg/kg", "30 kg/ha", "Apply 250 kg/ha super, 200 kg/ha urea"),
         ("5.7", "20 mg/kg", "25 kg/ha", "Apply 150 kg/ha super, 220 kg/ha urea")),
        ("Long Flat Block A", "LF-A", 2032,
         ("6.2", "24 mg/kg", "50 kg/ha", "Maintenance only: 100 kg/ha super"),
         ("6.4", "38 mg/kg", "42 kg/ha", "No phosphorus needed this season")),
        ("Brewer Downs paddock 3", "BD-P3", 2034,
         ("5.3", "10 mg/kg", "28 kg/ha", "Urgent P remediation: 300 kg/ha super + 200 urea"),
         ("5.6", "18 mg/kg", "32 kg/ha", "Moderate P deficiency: 200 kg/ha super + 180 urea")),
    ]:
        ev1 = datetime(year, 3, 12, 10, 0, tzinfo=timezone.utc)
        m1 = mid()
        new_mems.append(make_mem(m1, ev1, ev1+timedelta(days=5), ev1+timedelta(days=7), ev1+timedelta(days=8),
            farm, "soil_test_result", f"AgriLab NZ, March {year}",
            f"AgriLab NZ soil test for {farm}, March {year}. pH: {agri_vals[0]}. Olsen P: {agri_vals[1]}. Mineral N: {agri_vals[2]}. Recommendation: {agri_vals[3]}.",
            mtype="semantic", src="agrilab_nz", stype="lab_report", tags=["C01", "soil_test", "agrilab"]))
        ev2 = ev1 + timedelta(days=10)
        m2 = mid()
        new_mems.append(make_mem(m2, ev2, ev2+timedelta(days=5), ev2+timedelta(days=7), ev2+timedelta(days=8),
            farm, "soil_test_result", f"Canterbury Soil, March {year}",
            f"Canterbury Soil Services test for {farm}, March {year}. pH: {cant_vals[0]}. Bray P: {cant_vals[1]}. Mineral N: {cant_vals[2]}. Recommendation: {cant_vals[3]}.",
            mtype="semantic", src="canterbury_soil", stype="lab_report",
            contradicts=[m1], tags=["C01", "soil_test", "canterbury"]))

    # === C02: Lamb price data from different sources ===
    for yr, coop_p, market_p, works_p in [
        (2031, "$6.20/kg CW", "$6.50/kg CW", "$5.90/kg CW"),
        (2033, "$6.80/kg CW", "$7.10/kg CW", "$6.45/kg CW"),
    ]:
        base_dt = datetime(yr, 9, 15, 9, 0, tzinfo=timezone.utc)
        for label, price, src_name, stype in [
            ("coop", coop_p, "cooperative_schedule", "internal_record"),
            ("market", market_p, "AgriHQ", "market_data"),
            ("works", works_p, "meat_works_quote", "commercial_offer"),
        ]:
            ev = base_dt + timedelta(hours=[0,2,4][["coop","market","works"].index(label)])
            m = mid()
            new_mems.append(make_mem(m, ev, ev+timedelta(hours=1), ev+timedelta(hours=2), ev+timedelta(hours=3),
                "lamb", "price", f"{price}, {src_name}, Sept {yr}",
                f"Lamb price ({label}): {price} as of September {yr}. Source: {src_name}.",
                mtype="semantic", src=src_name, stype=stype,
                tags=["C02", "lamb_price", str(yr)]))

    # === C03: More yield revisions ===
    # Riverside canola 2034
    for label, ev, value, text, conf in [
        ("satellite", datetime(2034, 4, 5, tzinfo=timezone.utc), "3.0 t/ha",
         "Satellite estimate for Riverside Farm canola 2034: 3.0 tonnes/ha. Good canopy establishment.", 0.6),
        ("actual", datetime(2034, 12, 8, tzinfo=timezone.utc), "2.2 t/ha",
         "Actual harvest yield Riverside Farm canola 2034: 2.2 tonnes/ha (638 tonnes from 290 ha). Sclerotinia rot reduced yield significantly. Well below satellite estimate.", 1.0),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=2), ev+timedelta(days=3),
            "Riverside Farm canola 2034", "yield_estimate", value,
            text, mtype="semantic", conf=conf, src=label, stype="certified_measurement" if label=="actual" else "remote_sensing",
            tags=["C03", "yield", "Riverside"]))

    # Pōhatu wheat 2034
    for label, ev, value, text, conf in [
        ("satellite", datetime(2034, 3, 20, tzinfo=timezone.utc), "5.5 t/ha",
         "Satellite estimate for Pōhatu Farm wheat 2034: 5.5 tonnes/ha.", 0.6),
        ("agronomist", datetime(2034, 5, 25, tzinfo=timezone.utc), "5.9 t/ha",
         "Sarah Chen field estimate for Pōhatu wheat 2034: 5.9 t/ha. Crop looking strong after good rain.", 0.75),
        ("actual", datetime(2034, 12, 15, tzinfo=timezone.utc), "5.7 t/ha",
         "Actual harvest Pōhatu wheat 2034: 5.7 t/ha (1,767 tonnes from 310 ha). Weigh-bridge certified. Good season.", 1.0),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=2), ev+timedelta(days=3),
            "Pōhatu Farm wheat 2034", "yield_estimate", value,
            text, mtype="semantic", conf=conf, src=label, stype="certified_measurement" if label=="actual" else "remote_sensing",
            tags=["C03", "yield", "Pōhatu"]))

    # === C04: More observer disagreements ===
    # Pasture cover disagreement
    ev = datetime(2033, 5, 1, tzinfo=timezone.utc)
    for label, observer, reading, text, conf in [
        ("rob", "Rob Ellison", "2,200 kg DM/ha",
         "Rob Ellison's visual pasture assessment for Brewer Downs paddock 5, May 2033: approximately 2,200 kg DM/ha. Good autumn cover. Ready for set-stocking ewes.",
         0.5),
        ("plate", "rising plate meter", "1,750 kg DM/ha",
         "Rising plate meter reading for Brewer Downs paddock 5, May 2033: average 1,750 kg DM/ha from 50 readings on walking transect. Below target cover of 2,000 kg DM/ha.",
         0.85),
        ("satellite2", "satellite pasture analysis", "1,900 kg DM/ha",
         "LIC SPACE pasture analysis for Brewer Downs paddock 5, May 2033: estimated 1,900 kg DM/ha based on satellite imagery. Moderate confidence — cloud cover affected recent image quality.",
         0.7),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            "Brewer Downs paddock 5 pasture", "cover_assessment", f"{reading} ({observer})",
            text, mtype="semantic", belief=observer, conf=conf, src=label, stype="field_measurement",
            tags=["C04", "pasture_cover"]))

    # Disease severity disagreement
    ev2 = datetime(2034, 9, 20, tzinfo=timezone.utc)
    for label, observer, severity, text, conf in [
        ("hana", "Hana Tūhoe", "moderate (2-5% leaf area)",
         "Hana Tūhoe assessed Septoria leaf blotch on Clearwater Block 7 wheat, September 2034: moderate severity, 2-5% leaf area affected on flag leaf. Below spray threshold.",
         0.85),
        ("david2", "David Kāhui", "severe (10-15% leaf area)",
         "David Kāhui's assessment of Clearwater Block 7 wheat disease, September 2034: Septoria looks severe to me, maybe 10-15% of the flag leaf. I'd spray.",
         0.4),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev2, ev2+timedelta(hours=2), ev2+timedelta(hours=4), ev2+timedelta(hours=6),
            "Clearwater Block 7 Septoria", "severity", f"{severity} ({observer})",
            text, mtype="semantic", belief=observer, conf=conf, src=label, stype="professional_assessment" if label=="hana" else "informal_estimate",
            tags=["C04", "disease", "Septoria"]))

    # === C05: More weather conflicts ===
    # Hail event discrepancy
    ev3 = datetime(2034, 12, 22, 15, 0, tzinfo=timezone.utc)
    for label, source, report, text, conf in [
        ("station", "Clearwater station", "10mm hailstones, 8 minutes",
         "Clearwater Farm weather station recorded hail event 22 December 2034: stones to 10mm diameter, duration 8 minutes, 15mm precipitation. Minor crop damage expected.",
         0.95),
        ("metservice2", "MetService", "no hail warning issued",
         "MetService 22 December 2034: thunderstorm watch for Canterbury but no specific hail warning for the Clearwater area. Post-event verification confirmed localized cell not captured by radar.",
         0.3),
        ("sarah_obs", "Sarah Chen field inspection", "20-25mm hailstones, significant damage",
         "Sarah Chen's post-hail inspection of Clearwater Block 2, 23 December 2034: hailstone impact craters suggest stones up to 20-25mm. Wheat heads damaged — estimated 15% yield loss in worst-affected strip.",
         0.8),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev3, ev3+timedelta(hours=3), ev3+timedelta(hours=8), ev3+timedelta(hours=12),
            "Clearwater Farm hail event", "observation", f"{report} ({source})",
            text, mtype="semantic", belief=source, conf=conf, src=label, stype="direct_measurement",
            tags=["C05", "weather", "hail"]))

    # === C06: Organic certification vs conventional rules ===
    ev4 = datetime(2035, 3, 1, tzinfo=timezone.utc)
    for label, source, rule, text in [
        ("biogro", "BioGro NZ", "no synthetic nitrogen",
         "BioGro NZ organic certification standard: no synthetic nitrogen fertilizers permitted. Nitrogen inputs from legume crops, compost, and approved organic sources only.",),
        ("mpi_organic", "MPI organic standard", "max 170 kg N/ha from all sources",
         "MPI organic production standard: maximum 170 kg N/ha/year from all sources including manure and compost. Stricter than conventional limits in some aspects.",),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev4, ev4+timedelta(days=1), ev4+timedelta(days=3), ev4+timedelta(days=5),
            "organic nitrogen rules", "regulation", f"{rule} ({source})",
            text, mtype="regulatory", src=source, stype="certification_standard",
            tags=["C06", "regulation", "organic"]))

    # === C07: More self-contradictions ===
    # Harvest date discrepancy
    ev5 = datetime(2032, 12, 1, tzinfo=timezone.utc)
    m1 = mid()
    new_mems.append(make_mem(m1, ev5, ev5+timedelta(hours=2), ev5+timedelta(hours=4), ev5+timedelta(hours=6),
        "Clearwater Block 7", "harvest_date", "planned 15 December 2032",
        "Harvest schedule: Clearwater Block 7 wheat planned for 15 December 2032. Header booked from cooperative pool.",
        mtype="procedural", src="harvest_schedule", stype="schedule", tags=["C07", "harvest"]))
    ev6 = datetime(2032, 12, 18, 18, 0, tzinfo=timezone.utc)
    m2 = mid()
    new_mems.append(make_mem(m2, ev6, ev6+timedelta(hours=2), ev6+timedelta(hours=4), ev6+timedelta(hours=6),
        "Clearwater Block 7", "harvest_completed", "18 December 2032",
        "Clearwater Block 7 wheat harvest completed 18 December 2032. Three-day delay from plan due to rain on 14-16 December. Grain moisture at harvest: 13.8%.",
        src="harvest_records", stype="field_measurement",
        contradicts=[m1], tags=["C07", "harvest"]))

    # Stock count discrepancy
    ev7 = datetime(2033, 9, 1, tzinfo=timezone.utc)
    m3 = mid()
    new_mems.append(make_mem(m3, ev7, ev7+timedelta(hours=2), ev7+timedelta(hours=4), ev7+timedelta(hours=6),
        "Rob Ellison", "counted", "Brewer Downs lambs — 847 head",
        "Rob Ellison's physical count of Brewer Downs lamb flock, 1 September 2033: 847 head in paddocks 3, 4, and 5. Count done on horseback.",
        src="livestock_count", stype="field_measurement", tags=["C07", "livestock"]))
    ev8 = datetime(2033, 9, 5, tzinfo=timezone.utc)
    m4 = mid()
    new_mems.append(make_mem(m4, ev8, ev8+timedelta(hours=2), ev8+timedelta(hours=4), ev8+timedelta(hours=6),
        "FarmIQ", "recorded", "Brewer Downs lambs — 862 head",
        "FarmIQ livestock register for Brewer Downs, September 2033: 862 lambs on hand. Discrepancy with Rob's count of 847. Possible: 15 lambs in wrong paddock not counted, or deaths/sales not yet recorded in system.",
        src="farmiq", stype="automated_record",
        contradicts=[m3], tags=["C07", "livestock"]))

    # === More background ===
    bg_entries = [
        (datetime(2031, 3, 15, tzinfo=timezone.utc), "Thornfield Cooperative", "held", "autumn sowing planning meeting",
         "Autumn sowing planning meeting March 2031. Wheat area slightly increased across cooperative. Total planned: 2,800 ha wheat, 600 ha barley, 450 ha canola."),
        (datetime(2031, 6, 1, tzinfo=timezone.utc), "David Kāhui", "installed", "GPS guidance on header",
         "David Kāhui oversaw installation of RTK GPS guidance on the cooperative's John Deere S780 header. Allows 2.5cm pass-to-pass accuracy for controlled traffic farming."),
        (datetime(2031, 12, 20, tzinfo=timezone.utc), "Thornfield Cooperative", "held", "Christmas function",
         "Annual cooperative Christmas function at Darfield Community Centre. 120 attendees. BBQ and awards. Clearwater Farm won 'Best Wheat Crop 2031' award."),
        (datetime(2032, 3, 1, tzinfo=timezone.utc), "Hana Tūhoe", "installed", "moth traps",
         "Hana Tūhoe installed 20 new pheromone moth traps across cooperative farms for the 2032 season. Targeting diamondback moth in canola and wheat bug in wheat."),
        (datetime(2032, 6, 8, tzinfo=timezone.utc), "Sarah Chen", "attended", "FAR conference",
         "Sarah Chen attended the Foundation for Arable Research annual conference in Lincoln. Presented cooperative's precision fertilizer trial preliminary results."),
        (datetime(2032, 9, 1, tzinfo=timezone.utc), "Lachlan Murray", "arranged", "grain storage",
         "Lachlan Murray arranged additional grain storage capacity at Lyttelton for the 2032/33 export season. Secured 5,000 tonnes of silo space at port."),
        (datetime(2033, 3, 10, tzinfo=timezone.utc), "Wei Zhang", "completed", "farm mapping update",
         "Wei Zhang completed GIS mapping update for all cooperative farms. All paddock boundaries, soil types, and drainage features now in digital format."),
        (datetime(2033, 7, 15, tzinfo=timezone.utc), "Tom Brewer", "purchased", "new spray rig",
         "Cooperative purchased a 24m self-propelled sprayer (Goldacres G6). Cost: $385,000. Replaces aging Hardi unit. GPS section control for reduced chemical overlap."),
        (datetime(2033, 11, 1, tzinfo=timezone.utc), "Margaret Holt", "reported", "mid-year surplus",
         "Margaret Holt reported a mid-year operating surplus of $210,000 at the November committee meeting. Ahead of budget by $35,000."),
        (datetime(2034, 4, 1, tzinfo=timezone.utc), "Rob Ellison", "implemented", "rotational grazing plan",
         "Rob Ellison implemented a new rotational grazing plan across Brewer Downs. Six-week rotation, 12 paddock subdivisions. Aim: improve pasture utilization from 60% to 80%."),
        (datetime(2034, 7, 20, tzinfo=timezone.utc), "Thornfield Cooperative", "submitted", "MPI SFF final report",
         "Cooperative submitted final report for the MPI Sustainable Farming Fund precision agriculture project. Three years of data analysed. Average 6% yield improvement and 10% fertilizer cost reduction on trial blocks."),
        (datetime(2034, 12, 1, tzinfo=timezone.utc), "Lachlan Murray", "diversified", "export markets",
         "Lachlan Murray expanded export portfolio to include South Korea as a destination. First shipment: 400 tonnes wheat to CJ CheilJedang."),
        (datetime(2035, 3, 20, tzinfo=timezone.utc), "David Kāhui", "oversaw", "drainage installation",
         "David Kāhui oversaw installation of tile drainage on Pōhatu Farm's waterlogged Block 3. 2km of perforated pipe at 80cm depth. Cost: $4,200/ha."),
        (datetime(2035, 6, 1, tzinfo=timezone.utc), "Dr. Priya Nair", "began", "soil biology study",
         "Dr. Priya Nair began a two-year soil biology study on cooperative farms. Comparing microbial diversity under continuous cropping vs crop-pasture rotation."),
        (datetime(2035, 9, 10, tzinfo=timezone.utc), "Thornfield Cooperative", "participated_in", "regional water group",
         "Cooperative joined the Selwyn-Waihora Zone Committee water management group. Margaret Holt represents farming interests in freshwater quality discussions."),
    ]

    for dt, subj, pred, obj_, text in bg_entries:
        m = mid()
        ev = dt
        new_mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            subj, pred, obj_, text, src=pred, stype="internal_record", tags=["background"]))

    # === New queries ===
    new_qs.append(make_query("Q15-r2-01",
        "What do the two labs say about phosphorus levels on Brewer Downs paddock 3 in 2034?",
        "contradictory_sources",
        ["AgriLab: Olsen P 10 mg/kg (urgent P remediation needed), Canterbury: Bray P 18 mg/kg (moderate deficiency)"],
        ["Both agree on deficiency but disagree on severity"],
        ["Labs agree", "One result only"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r2-02",
        "What was the lamb price in September 2033?",
        "source_dependent",
        ["Cooperative schedule $6.80/kg, AgriHQ market $7.10/kg, meat works quote $6.45/kg"],
        ["Prices vary by source"],
        ["A single price without attribution"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r2-03",
        "Did the satellite estimate accurately predict Riverside canola yield in 2034?",
        "revised_estimates",
        ["No — satellite estimated 3.0 t/ha but actual was only 2.2 t/ha due to Sclerotinia rot"],
        ["Overestimated by about 36%"],
        ["Estimate was accurate", "3.0 was the actual yield"],
        [], []))

    new_qs.append(make_query("Q15-r2-04",
        "How much pasture cover is on Brewer Downs paddock 5 in May 2033?",
        "observer_disagreement",
        ["Three estimates disagree: Rob visual 2,200, plate meter 1,750, satellite 1,900 kg DM/ha"],
        ["Plate meter is most methodical measurement"],
        ["Any single number without disagreement noted"],
        [], [], conflict=True, uncertainty=True))

    new_qs.append(make_query("Q15-r2-05",
        "How severe is the Septoria leaf blotch on Clearwater Block 7 in September 2034?",
        "observer_disagreement",
        ["Hana Tūhoe: moderate 2-5% (below threshold), David Kāhui: severe 10-15% (would spray)"],
        ["Professional assessment differs from field operations estimate"],
        ["Definitively moderate or severe without noting disagreement"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r2-06",
        "What size were the hailstones at Clearwater Farm on 22 December 2034?",
        "measurement_conflict",
        ["Station recorded 10mm; Sarah Chen's field inspection found evidence of 20-25mm stones"],
        ["MetService had not issued a hail warning"],
        ["No hail occurred", "Exactly 10mm or exactly 25mm without noting discrepancy"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r2-07",
        "Can a cooperative member apply synthetic nitrogen if they have BioGro organic certification?",
        "regulatory_conflict",
        ["No — BioGro prohibits all synthetic nitrogen"],
        ["MPI organic standard caps total N at 170 kg/ha from all sources"],
        ["Synthetic N is permitted under organic certification"],
        [], []))

    new_qs.append(make_query("Q15-r2-08",
        "When was Clearwater Block 7 wheat actually harvested in 2032?",
        "self_contradicting",
        ["18 December 2032 — three days late due to rain on 14-16 December"],
        ["Originally planned for 15 December"],
        ["15 December", "Harvested on schedule"],
        [], []))

    new_qs.append(make_query("Q15-r2-09",
        "How many lambs does Brewer Downs have in September 2033?",
        "self_contradicting",
        ["Discrepancy: Rob's physical count is 847, FarmIQ register says 862"],
        ["15-head difference possibly due to miscounting or unrecorded transactions"],
        ["Exactly 847 or exactly 862 without noting discrepancy"],
        [], [], conflict=True, uncertainty=True))

    new_qs.append(make_query("Q15-r2-10",
        "Which yield estimates were most accurate across the cooperative?",
        "cross_case",
        ["Pre-harvest samples were closest to actual yields", "Satellite estimates were consistently off"],
        ["Long Flat 2033 was unusual: pre-harvest actually overestimated slightly"],
        ["All estimates were accurate", "Satellite is the best predictor"],
        [], [],
        notes="Cross-case comparison of prediction accuracy"))

    new_qs.append(make_query("Q15-r2-11",
        "What did the MPI Sustainable Farming Fund project achieve?",
        "control",
        ["6% average yield improvement and 10% fertilizer cost reduction over three years"],
        ["Received $165,000 grant"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r2-12",
        "What new markets did Lachlan Murray open for the cooperative?",
        "control",
        ["Malaysia (2034, 800 tonnes wheat) and South Korea (2034, 400 tonnes to CJ CheilJedang)"],
        ["Also secured direct Maersk shipping to Yokohama in 2031"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r2-13",
        "When did Hana Tūhoe detect fall armyworm and what happened?",
        "control",
        ["February 2034 at Riverside Farm, two moths in pheromone trap, reported to MPI within 24 hours"],
        [], [], [], [],
        difficulty="easy"))

    # Merge
    memories.extend(new_mems)
    queries.extend(new_qs)

    with open(mem_path, 'w') as f:
        for m in memories:
            f.write(json.dumps(m) + "\n")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

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

    print(f"\nAdded {len(new_mems)} memories, {len(new_qs)} queries")
    print(f"Total: {len(memories)} memories, {len(queries)} queries")

    tag_counts = {}
    for m in memories:
        for t in m.get("tags", []):
            if t.startswith("C0") or t == "background":
                tag_counts[t] = tag_counts.get(t, 0) + 1
    print(f"\nMemory distribution:")
    for t in sorted(tag_counts):
        print(f"  {t}: {tag_counts[t]}")

if __name__ == "__main__":
    main()
