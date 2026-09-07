#!/usr/bin/env python3
"""First expansion for Experiment 15 — adds ~80 memories and ~30 queries."""

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

    # === C01: More lab results for other farms ===
    # Pōhatu Farm soil tests — two labs disagree
    for year, agri_ph, agri_p, cant_ph, cant_p in [
        (2031, "5.6", "15 mg/kg", "5.8", "24 mg/kg"),
        (2033, "5.5", "14 mg/kg", "5.9", "26 mg/kg"),
    ]:
        ev1 = datetime(year, 3, 10, 10, 0, tzinfo=timezone.utc)
        m1 = mid(); m2 = mid()
        new_mems.append(make_mem(m1, ev1, ev1+timedelta(days=5), ev1+timedelta(days=7), ev1+timedelta(days=8),
            "Pōhatu Farm Block 2", "soil_test_result", f"AgriLab NZ, March {year}",
            f"AgriLab NZ soil test for Pōhatu Farm Block 2, March {year}. pH: {agri_ph}. Olsen P: {agri_p}. Moderate phosphorus deficiency indicated.",
            mtype="semantic", src="agrilab_nz", stype="lab_report", tags=["C01", "soil_test", "agrilab"]))
        ev2 = ev1 + timedelta(days=8)
        new_mems.append(make_mem(m2, ev2, ev2+timedelta(days=5), ev2+timedelta(days=7), ev2+timedelta(days=8),
            "Pōhatu Farm Block 2", "soil_test_result", f"Canterbury Soil, March {year}",
            f"Canterbury Soil Services test for Pōhatu Farm Block 2, March {year}. pH: {cant_ph}. Bray P: {cant_p}. Phosphorus adequate for cropping.",
            mtype="semantic", src="canterbury_soil", stype="lab_report",
            contradicts=[m1], tags=["C01", "soil_test", "canterbury"]))

    # Riverside Farm
    ev1 = datetime(2032, 4, 5, 10, 0, tzinfo=timezone.utc)
    m1 = mid(); m2 = mid()
    new_mems.append(make_mem(m1, ev1, ev1+timedelta(days=5), ev1+timedelta(days=7), ev1+timedelta(days=8),
        "Riverside Farm paddock 4", "soil_test_result", "AgriLab NZ, April 2032",
        "AgriLab NZ soil test for Riverside Farm paddock 4, April 2032. pH: 6.3. Olsen P: 28 mg/kg. Good fertility. Maintenance dressing only.",
        mtype="semantic", src="agrilab_nz", stype="lab_report", tags=["C01", "soil_test", "agrilab"]))
    ev2 = ev1 + timedelta(days=10)
    new_mems.append(make_mem(m2, ev2, ev2+timedelta(days=5), ev2+timedelta(days=7), ev2+timedelta(days=8),
        "Riverside Farm paddock 4", "soil_test_result", "Canterbury Soil, April 2032",
        "Canterbury Soil Services test for Riverside Farm paddock 4, April 2032. pH: 6.0. Bray P: 42 mg/kg. High phosphorus — reduce P inputs.",
        mtype="semantic", src="canterbury_soil", stype="lab_report",
        contradicts=[m1], tags=["C01", "soil_test", "canterbury"]))

    # === C02: More price data — barley and canola ===
    for commodity, yr, coop_p, nzx_p, export_p in [
        ("barley", 2031, "$310/tonne", "$305/tonne", "$335/tonne FOB"),
        ("barley", 2033, "$340/tonne", "$332/tonne", "$360/tonne FOB"),
        ("canola", 2032, "$680/tonne", "$695/tonne", "$720/tonne FOB"),
        ("canola", 2034, "$710/tonne", "$725/tonne", "$755/tonne FOB"),
    ]:
        base_dt = datetime(yr, 6, 15, 9, 0, tzinfo=timezone.utc)
        ids = []
        for label, price, src_name, stype, delay_h in [
            ("coop", coop_p, "cooperative_records", "internal_record", 0),
            ("nzx", nzx_p, "nzx_futures", "market_data", 2),
            ("export", export_p, "export_buyer", "commercial_offer", 4),
        ]:
            ev = base_dt + timedelta(hours=delay_h)
            m = mid()
            ids.append(m)
            new_mems.append(make_mem(m, ev, ev+timedelta(hours=1), ev+timedelta(hours=2), ev+timedelta(hours=3),
                commodity, "price", f"{price}, {src_name}, June {yr}",
                f"{commodity.capitalize()} price from {src_name}: {price} as of June {yr}.",
                mtype="semantic", src=src_name, stype=stype,
                contradicts=[x for x in ids[:-1]],
                tags=["C02", f"{commodity}_price", str(yr)]))

    # === C03: More revised estimates — Long Flat wheat 2033 ===
    estimates = [
        ("satellite", datetime(2033, 3, 25, tzinfo=timezone.utc), "6.8 t/ha",
         "Satellite estimate for Long Flat Farm wheat 2033: 6.8 tonnes/ha. Strong vegetation index.",
         0.6, "satellite_estimate", "remote_sensing"),
        ("agronomist", datetime(2033, 5, 20, tzinfo=timezone.utc), "6.5 t/ha",
         "Sarah Chen field walk estimate for Long Flat wheat 2033: 6.5 tonnes/ha. Good crop but slight drought stress.",
         0.75, "agronomist_walk", "professional_assessment"),
        ("pre_harvest", datetime(2033, 10, 15, tzinfo=timezone.utc), "7.0 t/ha",
         "Pre-harvest sample for Long Flat wheat 2033: 7.0 tonnes/ha. Surprising upward revision — late rains boosted grain fill.",
         0.9, "pre_harvest_sample", "field_measurement"),
        ("actual", datetime(2033, 12, 10, tzinfo=timezone.utc), "6.9 t/ha",
         "Actual harvest yield Long Flat wheat 2033: 6.9 tonnes/ha (2,415 tonnes from 350 ha). Weigh-bridge certified. Excellent season.",
         1.0, "harvest_records", "certified_measurement"),
    ]
    prev = None
    for label, ev, value, text, conf, src, stype in estimates:
        m = mid()
        sup = [prev] if prev else []
        new_mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=2), ev+timedelta(days=3),
            "Long Flat Farm wheat 2033", "yield_estimate", value,
            text, mtype="semantic", conf=conf, src=src, stype=stype,
            supersedes=sup, tags=["C03", "yield", "Long Flat"]))
        prev = m

    # Brewer Downs lamb weight estimates
    est_lamb = [
        ("visual", datetime(2032, 6, 1, tzinfo=timezone.utc), "32 kg average",
         "Rob Ellison's visual estimate for Brewer Downs autumn lambs, June 2032: approximately 32 kg liveweight average. Based on experienced eye across mob of 800.",
         0.5, "livestock_estimate", "informal_estimate"),
        ("weigh", datetime(2032, 6, 10, tzinfo=timezone.utc), "28.5 kg average",
         "Brewer Downs lamb weigh-day, June 2032: average liveweight 28.5 kg (n=200 head through scales). Rob's estimate was high.",
         0.95, "livestock_records", "direct_measurement"),
    ]
    prev = None
    for label, ev, value, text, conf, src, stype in est_lamb:
        m = mid()
        sup = [prev] if prev else []
        new_mems.append(make_mem(m, ev, ev+timedelta(hours=4), ev+timedelta(hours=8), ev+timedelta(hours=12),
            "Brewer Downs lambs 2032", "weight_estimate", value,
            text, mtype="semantic", conf=conf, src=src, stype=stype,
            supersedes=sup, tags=["C03", "livestock", "weight"]))
        prev = m

    # === C04: More observer disagreements ===
    # Weed assessment
    ev = datetime(2032, 10, 5, tzinfo=timezone.utc)
    weed_obs = [
        ("sarah", "Sarah Chen", "5% ground cover", 0.85,
         "Sarah Chen assessed wild oat infestation on Clearwater Block 5, October 2032: 5% ground cover. Spot-spray recommended, not blanket application.",
         "agronomist_assessment", "professional_assessment"),
        ("david", "David Kāhui", "15-20% ground cover", 0.5,
         "David Kāhui estimated wild oat at 15-20% ground cover on Clearwater Block 5 during October field check. Recommended full paddock spray.",
         "field_ops_estimate", "informal_estimate"),
        ("drone", "drone imaging", "8.2% ground cover", 0.7,
         "Drone multispectral analysis of Clearwater Block 5 wild oats, October 2032: 8.2% weed ground cover detected. Algorithm trained on Canterbury wild oat populations.",
         "drone_analysis", "automated_measurement"),
    ]
    weed_ids = []
    for label, observer, pct, conf, text, src, stype in weed_obs:
        m = mid()
        weed_ids.append(m)
        new_mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            "Clearwater Block 5 wild oats", "coverage", f"{pct} ({observer})",
            text, mtype="semantic", belief=observer, conf=conf, src=src, stype=stype,
            contradicts=[x for x in weed_ids[:-1]],
            tags=["C04", "weed_assessment"]))

    # Soil compaction disagreement
    ev2 = datetime(2033, 7, 20, tzinfo=timezone.utc)
    comp_obs = [
        ("sarah", "Sarah Chen", "moderate compaction",
         "Sarah Chen's penetrometer readings on Pōhatu Block 1, July 2033: moderate compaction at 15-20cm depth. Recommended subsoiling before spring sowing.",
         0.85, "agronomist_notes", "professional_assessment"),
        ("priya", "Dr. Priya Nair", "minimal compaction",
         "Dr. Priya Nair's bulk density analysis for Pōhatu Block 1, July 2033: bulk density 1.35 g/cm³ at 15-20cm. Within normal range for silt loam. No remediation needed.",
         0.9, "agrilab_nz", "lab_report"),
    ]
    for label, observer, assessment, text, conf, src, stype in comp_obs:
        m = mid()
        new_mems.append(make_mem(m, ev2, ev2+timedelta(hours=3), ev2+timedelta(hours=6), ev2+timedelta(hours=9),
            "Pōhatu Block 1 compaction", "assessment", f"{assessment} ({observer})",
            text, mtype="semantic", belief=observer, conf=conf, src=src, stype=stype,
            tags=["C04", "soil_compaction"]))

    # === C05: More weather conflicts ===
    # Wind speed disagreement
    ev3 = datetime(2034, 1, 18, 14, 0, tzinfo=timezone.utc)
    wind_obs = [
        ("station", "Clearwater station", "65 km/h gusts",
         "Clearwater Farm weather station recorded wind gusts to 65 km/h NW on 18 January 2034. Sustained at 40 km/h for 4 hours. One irrigation pivot damaged.",
         1.0, "farm_weather_station", "direct_measurement"),
        ("metservice", "MetService", "45-55 km/h predicted",
         "MetService severe weather outlook 17 January 2034: Canterbury Plains gust potential 45-55 km/h NW. Strong wind watch, below warning threshold.",
         0.5, "metservice", "weather_forecast"),
        ("insurance", "insurance report", "70-80 km/h estimated",
         "Insurance assessor report for Clearwater Farm pivot damage claim, 18 January 2034: estimated wind gusts 70-80 km/h based on damage pattern to irrigation pivot. Consistent with Category 1 wind damage.",
         0.6, "insurance_assessment", "indirect_estimate"),
    ]
    for label, source, speed, text, conf, src, stype in wind_obs:
        m = mid()
        new_mems.append(make_mem(m, ev3, ev3+timedelta(hours=6), ev3+timedelta(hours=12), ev3+timedelta(hours=24),
            "Clearwater Farm wind event", "measurement", f"{speed} ({source})",
            text, mtype="semantic", belief=source, conf=conf, src=src, stype=stype,
            tags=["C05", "weather", "wind"]))

    # Soil moisture conflict
    ev4 = datetime(2034, 11, 5, tzinfo=timezone.utc)
    for label, source, reading, text, conf in [
        ("sensor", "soil moisture sensor", "18% volumetric",
         "In-ground soil moisture sensor at Clearwater Block 7, 5 November 2034: 18% volumetric water content at 30cm depth. Below irrigation trigger of 22%.",
         0.9),
        ("hand", "David Kāhui hand feel", "adequate moisture",
         "David Kāhui assessed soil moisture on Clearwater Block 7 by hand, 5 November 2034. Soil at 30cm depth feels moist and holds shape when squeezed. Adequate for crop needs. No irrigation needed yet.",
         0.4),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev4, ev4+timedelta(hours=2), ev4+timedelta(hours=4), ev4+timedelta(hours=6),
            "Clearwater Block 7 soil moisture", "measurement", f"{reading} ({source})",
            text, mtype="semantic", belief=source, conf=conf,
            src=label, stype="direct_measurement" if label == "sensor" else "informal_estimate",
            tags=["C05", "irrigation", "soil_moisture"]))

    # === C06: More regulatory conflicts ===
    # Pesticide MRL disagreement
    ev5 = datetime(2033, 11, 1, tzinfo=timezone.utc)
    for label, source, limit, text in [
        ("nz_mrl", "NZ FSANZ", "0.1 mg/kg",
         "FSANZ Maximum Residue Limit for chlorpyrifos in wheat (NZ domestic): 0.1 mg/kg. Effective 2033.",
         ),
        ("japan_mrl", "Japan MAFF", "0.01 mg/kg",
         "Japan MAFF import MRL for chlorpyrifos in wheat: 0.01 mg/kg. Ten times stricter than NZ domestic standard. Critical for export shipments to Japan.",
         ),
        ("eu_mrl", "EU Commission", "0.01 mg/kg",
         "EU Commission MRL for chlorpyrifos in wheat: 0.01 mg/kg (effectively banned). Relevant for any future EU market access.",
         ),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev5, ev5+timedelta(days=1), ev5+timedelta(days=3), ev5+timedelta(days=5),
            "chlorpyrifos MRL wheat", "regulation", f"{limit} ({source})",
            text, mtype="regulatory", src=source, stype="government_regulation",
            tags=["C06", "regulation", "pesticide"]))

    # Water allocation contradictions
    ev6 = datetime(2034, 9, 1, tzinfo=timezone.utc)
    for label, source, allocation, text in [
        ("consent", "resource consent", "4,200 m³/ha/year",
         "Clearwater Farm resource consent CRC-042871: maximum water allocation 4,200 m³/ha/year for irrigation. Granted 2028, expires 2043.",
         ),
        ("plan_change", "ECan Plan Change 5", "3,800 m³/ha/year",
         "Canterbury Regional Council Plan Change 5 (operative 2034): maximum irrigation allocation reduced to 3,800 m³/ha/year for deep silt loams. Existing consents grandfathered until renewal.",
         ),
        ("industry", "Irrigation NZ guidelines", "3,500 m³/ha/year",
         "Irrigation NZ best practice guideline 2034: target maximum irrigation application 3,500 m³/ha/year for Canterbury wheat crops. Based on crop water demand modelling.",
         ),
    ]:
        m = mid()
        new_mems.append(make_mem(m, ev6, ev6+timedelta(days=1), ev6+timedelta(days=3), ev6+timedelta(days=5),
            "Clearwater Farm irrigation allocation", "regulation", f"{allocation} ({source})",
            text, mtype="regulatory", src=source, stype="government_regulation",
            tags=["C06", "regulation", "water"]))

    # === C07: More self-contradictions ===
    # Seed rate discrepancy
    ev7 = datetime(2032, 4, 1, tzinfo=timezone.utc)
    m1 = mid()
    new_mems.append(make_mem(m1, ev7, ev7+timedelta(hours=1), ev7+timedelta(hours=3), ev7+timedelta(hours=4),
        "Clearwater Block 3 sowing", "seed_rate", "150 kg/ha",
        "Sowing plan for Clearwater Block 3, autumn 2032: wheat variety Viceroy at 150 kg/ha. Target plant population: 250 plants/m².",
        mtype="procedural", src="sowing_plan", stype="farm_plan", tags=["C07", "sowing"]))
    ev8 = datetime(2032, 4, 10, 8, 0, tzinfo=timezone.utc)
    m2 = mid()
    new_mems.append(make_mem(m2, ev8, ev8+timedelta(hours=1), ev8+timedelta(hours=3), ev8+timedelta(hours=4),
        "David Kāhui", "reported", "actual seed rate Block 3",
        "David Kāhui's post-sowing report for Clearwater Block 3: actual seed rate was 165 kg/ha. Drill calibration was off — discovered after first two passes. Corrected to 150 for remaining area but average across block is 158 kg/ha.",
        src="field_report", stype="incident_report",
        contradicts=[m1], tags=["C07", "sowing"]))

    # Fertilizer application record vs tank dip
    ev9 = datetime(2033, 8, 5, 7, 0, tzinfo=timezone.utc)
    m3 = mid()
    new_mems.append(make_mem(m3, ev9, ev9+timedelta(hours=3), ev9+timedelta(hours=5), ev9+timedelta(hours=7),
        "Clearwater Block 7 nitrogen", "application_record", "120 kg N/ha",
        "FarmIQ application record: Clearwater Block 7 received 120 kg N/ha as urea on 5 August 2033. Applied by spreader truck, GPS-mapped. Total: 50.4 tonnes urea over 420 ha.",
        mtype="procedural", src="farmiq", stype="automated_record", tags=["C07", "fertilizer"]))
    ev10 = datetime(2033, 8, 6, 8, 0, tzinfo=timezone.utc)
    m4 = mid()
    new_mems.append(make_mem(m4, ev10, ev10+timedelta(hours=1), ev10+timedelta(hours=3), ev10+timedelta(hours=5),
        "Wei Zhang", "flagged", "fertilizer discrepancy Block 7",
        "Wei Zhang flagged discrepancy: FarmIQ records show 50.4 tonnes urea applied to Block 7, but the Ravensdown delivery total for August was only 45 tonnes. Either some came from existing stock (not recorded) or the application rate was lower than logged.",
        src="data_audit", stype="data_analysis",
        contradicts=[m3], tags=["C07", "fertilizer"]))

    # === More background ===
    bg_entries = [
        (datetime(2029, 11, 1, tzinfo=timezone.utc), "Tom Brewer", "serviced", "cooperative truck fleet",
         "Tom Brewer arranged WOF and COF inspections for the cooperative's three trucks. All passed. Fleet age: 5-8 years.",
         "procedural", "maintenance_records", "service_record"),
        (datetime(2030, 2, 10, tzinfo=timezone.utc), "Thornfield Cooperative", "hosted", "Lincoln University students",
         "Cooperative hosted 15 Lincoln University agriculture students for a week-long placement. Students assisted with soil sampling and crop assessments.",
         "episodic", "education_records", "event_report"),
        (datetime(2030, 5, 22, tzinfo=timezone.utc), "Margaret Holt", "attended", "Federated Farmers conference",
         "Margaret Holt attended the Federated Farmers annual conference in Wellington. Key topic: freshwater policy reform and implications for Canterbury farming.",
         "episodic", "admin_records", "event_report"),
        (datetime(2030, 8, 1, tzinfo=timezone.utc), "Hana Tūhoe", "ran", "integrated pest management workshop",
         "Hana Tūhoe ran a two-day IPM workshop for cooperative members. Topics: biological control agents, monitoring techniques, spray decision thresholds.",
         "episodic", "education_records", "event_report"),
        (datetime(2031, 2, 1, tzinfo=timezone.utc), "Thornfield Cooperative", "applied_for", "MPI SFF grant",
         "Cooperative submitted application to MPI Sustainable Farming Fund for a precision agriculture project. Requested: $180,000 over three years.",
         "episodic", "admin_records", "grant_application"),
        (datetime(2031, 5, 10, tzinfo=timezone.utc), "Rob Ellison", "organized", "sheep scanning day",
         "Rob Ellison organized pregnancy scanning day for cooperative sheep flocks. Average scanning percentage: 162%. Brewer Downs at 175% — above district average.",
         "episodic", "livestock_records", "event_report"),
        (datetime(2031, 10, 15, tzinfo=timezone.utc), "Lachlan Murray", "secured", "new shipping line",
         "Lachlan Murray secured a direct container shipping service from Lyttelton to Yokohama via Maersk. Previously relied on transhipment via Tauranga. Saves 5 days and $12/tonne.",
         "episodic", "logistics_records", "commercial_agreement"),
        (datetime(2032, 1, 10, tzinfo=timezone.utc), "Thornfield Cooperative", "received", "SFF grant approval",
         "MPI confirmed Sustainable Farming Fund grant of $165,000 (of $180,000 requested) for three-year precision agriculture programme. Co-funding required from cooperative.",
         "episodic", "admin_records", "government_correspondence"),
        (datetime(2032, 4, 20, tzinfo=timezone.utc), "Sarah Chen", "presented", "variable rate trial results",
         "Sarah Chen presented preliminary results of variable rate fertilizer trial at April cooperative meeting. Some blocks showed 8% yield improvement; others showed no difference. Two more seasons of data needed.",
         "episodic", "trial_records", "meeting_record"),
        (datetime(2032, 7, 5, tzinfo=timezone.utc), "Dr. James Whittle", "published", "Canterbury soil health report",
         "Dr. James Whittle published the Canterbury Soil Health Baseline Report 2032. Cooperative farms featured as case studies. Report highlights declining organic matter in continuously cropped paddocks.",
         "semantic", "research_publication", "academic_paper"),
        (datetime(2032, 10, 1, tzinfo=timezone.utc), "Thornfield Cooperative", "organized", "harvest planning meeting",
         "Harvest planning meeting held October 2032. Header booking schedule, grain storage allocation, and transport logistics confirmed for all 43 member farms.",
         "procedural", "meeting_minutes", "meeting_record"),
        (datetime(2033, 2, 15, tzinfo=timezone.utc), "David Kāhui", "trialled", "cover crop mix",
         "David Kāhui trialled a multi-species cover crop mix (oats, mustard, phacelia, crimson clover) on Clearwater Block 6 after wheat harvest. Aim: improve soil structure and nitrogen fixation.",
         "episodic", "trial_records", "field_measurement"),
        (datetime(2033, 5, 5, tzinfo=timezone.utc), "Margaret Holt", "negotiated", "electricity supply contract",
         "Margaret Holt negotiated a three-year electricity supply contract with Meridian Energy for cooperative facilities. Fixed rate: 18.5c/kWh. Saving of $22,000/year vs previous spot market arrangement.",
         "episodic", "admin_records", "commercial_agreement"),
        (datetime(2033, 8, 10, tzinfo=timezone.utc), "Rob Ellison", "introduced", "EID tags",
         "Rob Ellison introduced electronic identification (EID) tags across all cooperative sheep flocks. 12,000 tags deployed. Integrated with FarmIQ for individual animal tracking.",
         "episodic", "livestock_records", "project_report"),
        (datetime(2034, 3, 1, tzinfo=timezone.utc), "Thornfield Cooperative", "celebrated", "5th anniversary",
         "Thornfield Agricultural Cooperative celebrated its 5th anniversary at a dinner in Darfield. All 43 member families attended. Cooperative turnover now $28 million/year.",
         "episodic", "admin_records", "event_report"),
        (datetime(2034, 6, 15, tzinfo=timezone.utc), "Wei Zhang", "generated", "carbon footprint report",
         "Wei Zhang generated the cooperative's first carbon footprint report using Overseer model. Average emissions: 3.2 tonnes CO2e/ha for cropping, 8.5 tonnes CO2e/ha for sheep/beef. Identified key reduction opportunities.",
         "semantic", "environmental_records", "data_analysis"),
        (datetime(2034, 10, 20, tzinfo=timezone.utc), "Hana Tūhoe", "trained", "drone operators",
         "Hana Tūhoe trained three cooperative members as licensed drone operators for pest monitoring. CAANZ Part 102 certification obtained. Drones available for hire within cooperative.",
         "episodic", "education_records", "training_record"),
        (datetime(2035, 2, 1, tzinfo=timezone.utc), "Sarah Chen", "recommended", "new wheat variety",
         "Sarah Chen recommended cooperative members trial wheat variety 'Dorado' from PGG Wrightson Seeds. Showed 5% yield advantage over Viceroy in Lincoln University trials.",
         "semantic", "agronomist_notes", "professional_assessment"),
        (datetime(2035, 5, 10, tzinfo=timezone.utc), "Lachlan Murray", "reported", "export season summary",
         "Lachlan Murray's 2034/35 export summary: 8,200 tonnes wheat exported (Japan 60%, Malaysia 25%, domestic 15%). Average price: $442/tonne CIF. Record volume for the cooperative.",
         "episodic", "export_records", "financial_report"),
        (datetime(2035, 8, 15, tzinfo=timezone.utc), "Tom Brewer", "replaced", "cooperative header",
         "Cooperative replaced the 2029 John Deere S780 header with a new S790 model. Trade-in plus capital: $420,000 net cost. New header has yield mapping and grain quality sensing.",
         "episodic", "purchase_records", "financial_document"),
    ]

    for dt, subj, pred, obj_, text, mtype, src, stype in bg_entries:
        m = mid()
        ev = dt
        new_mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            subj, pred, obj_, text, mtype=mtype, src=src, stype=stype, tags=["background"]))

    # === New queries ===
    new_qs.append(make_query("Q15-r1-01",
        "Do AgriLab NZ and Canterbury Soil Services agree on phosphorus levels for Pōhatu Farm Block 2?",
        "contradictory_sources",
        ["No — AgriLab consistently reads lower P than Canterbury due to different methods (Olsen vs Bray)"],
        ["In 2031: AgriLab 15 vs Canterbury 24; in 2033: AgriLab 14 vs Canterbury 26"],
        ["Labs agree", "One result without mentioning the other"],
        [], [], conflict=True,
        notes="Same pattern as Clearwater but different farm"))

    new_qs.append(make_query("Q15-r1-02",
        "What was the barley price in June 2031?",
        "source_dependent",
        ["Multiple sources: cooperative $310, NZX $305, export $335 FOB"],
        ["Prices vary by source"],
        ["A single price without attribution"],
        [], [], conflict=True,
        notes="Tests same pattern as wheat but for barley"))

    new_qs.append(make_query("Q15-r1-03",
        "What was the canola price in June 2034?",
        "source_dependent",
        ["Cooperative $710, NZX $725, export $755 FOB"],
        ["NZX was higher than cooperative price"],
        ["A single price"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r1-04",
        "What was the actual wheat yield at Long Flat Farm in 2033?",
        "revised_estimates",
        ["6.9 tonnes/ha (2,415 tonnes from 350 ha), weigh-bridge certified"],
        ["Excellent season", "Pre-harvest estimate was 7.0 — very close"],
        ["6.8 tonnes/ha", "6.5 tonnes/ha", "Earlier estimates presented as final"],
        [], [],
        notes="Unlike Clearwater 2032, estimates went up as well as down"))

    new_qs.append(make_query("Q15-r1-05",
        "How accurate was Rob Ellison's visual estimate of lamb weights in June 2032?",
        "revised_estimates",
        ["Overestimated by about 3.5 kg — estimated 32 kg but actual was 28.5 kg"],
        ["Visual estimate was high by about 12%"],
        ["Estimate was accurate", "32 kg was correct"],
        [], [],
        notes="Visual vs measured comparison in livestock context"))

    new_qs.append(make_query("Q15-r1-06",
        "How much wild oat was on Clearwater Block 5 in October 2032?",
        "observer_disagreement",
        ["Estimates varied: Sarah Chen 5%, David Kāhui 15-20%, drone 8.2%"],
        ["Different observers gave very different assessments"],
        ["Any single number without noting disagreement"],
        [], [], conflict=True, uncertainty=True,
        notes="Same observer-disagreement pattern as aphid counts"))

    new_qs.append(make_query("Q15-r1-07",
        "Is Pōhatu Block 1 compacted?",
        "observer_disagreement",
        ["Sarah Chen says moderate compaction (penetrometer); Dr. Nair says minimal (bulk density analysis)"],
        ["Different methods give different conclusions"],
        ["Definitely compacted or definitely not without noting disagreement"],
        [], [], conflict=True,
        notes="Expert disagreement with different measurement methods"))

    new_qs.append(make_query("Q15-r1-08",
        "How fast were the wind gusts at Clearwater Farm on 18 January 2034?",
        "measurement_conflict",
        ["Farm station: 65 km/h. MetService predicted 45-55. Insurance estimated 70-80 based on damage."],
        ["Forecast underestimated the event"],
        ["45-55 km/h", "Exactly 70-80 km/h without noting uncertainty"],
        [], [], conflict=True,
        notes="Three different values from different source types"))

    new_qs.append(make_query("Q15-r1-09",
        "Does Clearwater Block 7 need irrigation as of 5 November 2034?",
        "measurement_conflict",
        ["Sensor says yes (18% below 22% trigger); David's hand assessment says no (adequate moisture)"],
        ["Conflicting signals from instrument vs human assessment"],
        ["Definitively yes or no without noting the conflict"],
        [], [], conflict=True,
        notes="Instrument vs human assessment disagreement"))

    new_qs.append(make_query("Q15-r1-10",
        "What chlorpyrifos residue limit applies to wheat exported to Japan?",
        "regulatory_conflict",
        ["Japan's limit is 0.01 mg/kg — ten times stricter than NZ domestic (0.1 mg/kg)"],
        ["EU has same 0.01 limit"],
        ["0.1 mg/kg applies to exports", "NZ domestic limit governs exports"],
        [], [], conflict=True,
        notes="Export market has stricter limit than domestic"))

    new_qs.append(make_query("Q15-r1-11",
        "How much water can Clearwater Farm use for irrigation?",
        "regulatory_conflict",
        ["Resource consent allows 4,200 m³/ha/year but new Plan Change 5 sets 3,800 (existing consents grandfathered)"],
        ["Industry guideline is even lower at 3,500"],
        ["4,200 without mentioning Plan Change", "3,500 as if it were law"],
        [], [], conflict=True,
        notes="Grandfathering adds complexity — consent still valid but new rule exists"))

    new_qs.append(make_query("Q15-r1-12",
        "Was the correct seed rate planted on Clearwater Block 3 in autumn 2032?",
        "self_contradicting",
        ["No — plan was 150 kg/ha but drill calibration was off; actual average was 158 kg/ha"],
        ["First two passes were at 165 kg/ha before correction"],
        ["150 kg/ha was achieved", "Plan was followed correctly"],
        [], [],
        notes="Plan vs actual discrepancy"))

    new_qs.append(make_query("Q15-r1-13",
        "Was 120 kg N/ha actually applied to Clearwater Block 7 in August 2033?",
        "self_contradicting",
        ["FarmIQ says 120 kg/ha (50.4t urea) but only 45t was delivered in August — discrepancy flagged by Wei Zhang"],
        ["Either existing stock was used or rate was lower than recorded"],
        ["Definitively yes, 120 kg applied", "Records are accurate"],
        [], [], conflict=True, uncertainty=True,
        notes="Digital record vs physical delivery discrepancy"))

    new_qs.append(make_query("Q15-r1-14",
        "What are the most common sources of contradictory information in the cooperative's records?",
        "cross_case",
        ["Labs disagree on soil tests, price sources diverge, yield estimates revise, observers count pests differently, weather records vary, regulations conflict"],
        ["Different measurement methods are a primary source"],
        ["Records are consistent", "Only one type of contradiction exists"],
        [], [],
        notes="Meta-question across all contradiction types"))

    new_qs.append(make_query("Q15-r1-15",
        "When did the cooperative first host a university student placement?",
        "control",
        ["February 2030, Lincoln University, 15 students for one week"],
        ["Students helped with soil sampling and crop assessments"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r1-16",
        "What was the cooperative's carbon footprint?",
        "control",
        ["3.2 tonnes CO2e/ha for cropping, 8.5 tonnes CO2e/ha for sheep/beef"],
        ["Generated by Wei Zhang using Overseer model", "First such report"],
        [], [], [],
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
