#!/usr/bin/env python3
"""Generate Experiment 15 — Contradictory Metadata.

Thornfield Agricultural Cooperative setting with contradictory sources:
conflicting lab results, divergent price data, revised estimates,
observer disagreement, weather discrepancies, regulatory conflicts,
and self-contradicting records.
"""

import json, hashlib, os, sys, uuid, random
from datetime import datetime, timedelta, timezone

OUT = "experiment_15_contradictory_metadata"

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
        "memory_id": memory_id,
        "experiment": "exp15",
        "story_id": "thornfield_coop",
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

BASE = datetime(2029, 1, 1, tzinfo=timezone.utc)

def gen_c01():
    """Contradictory lab results."""
    mems = []
    ids = {}

    # AgriLab NZ results for Clearwater Block 7
    for year, ph, olsen_p, nitrogen, rec in [
        (2030, "5.8", "18 mg/kg", "42 kg/ha mineral N", "Apply 200 kg/ha superphosphate, 150 kg/ha urea"),
        (2031, "5.9", "22 mg/kg", "38 kg/ha mineral N", "Apply 150 kg/ha superphosphate, 180 kg/ha urea"),
        (2032, "6.1", "20 mg/kg", "45 kg/ha mineral N", "Apply 175 kg/ha superphosphate, 140 kg/ha urea"),
    ]:
        ev = datetime(year, 3, 15, 10, 0, tzinfo=timezone.utc)
        m = mid()
        ids[f"agrilab_{year}"] = m
        mems.append(make_mem(m, ev, ev+timedelta(days=5), ev+timedelta(days=7), ev+timedelta(days=8),
            "Clearwater Block 7", "soil_test_result", f"AgriLab NZ, March {year}",
            f"AgriLab NZ soil test results for Clearwater Block 7, March {year}. Method: Olsen P extraction. pH: {ph}. Phosphorus (Olsen P): {olsen_p}. Mineral nitrogen: {nitrogen}. Recommendation: {rec}.",
            mtype="semantic", src="agrilab_nz", stype="lab_report",
            tags=["C01", "soil_test", "agrilab"]))

    # Canterbury Soil Services — same fields, different results
    for year, ph, bray_p, nitrogen, rec in [
        (2030, "6.0", "32 mg/kg", "35 kg/ha mineral N", "Apply 120 kg/ha superphosphate, 180 kg/ha urea"),
        (2031, "5.7", "28 mg/kg", "44 kg/ha mineral N", "Apply 180 kg/ha superphosphate, 130 kg/ha urea"),
        (2032, "5.9", "35 mg/kg", "40 kg/ha mineral N", "Apply 100 kg/ha superphosphate, 160 kg/ha urea"),
    ]:
        ev = datetime(year, 3, 20, 10, 0, tzinfo=timezone.utc)
        m = mid()
        contra = [ids.get(f"agrilab_{year}", "")]
        ids[f"canterbury_{year}"] = m
        mems.append(make_mem(m, ev, ev+timedelta(days=5), ev+timedelta(days=7), ev+timedelta(days=8),
            "Clearwater Block 7", "soil_test_result", f"Canterbury Soil, March {year}",
            f"Canterbury Soil Services test for Clearwater Block 7, March {year}. Method: Bray P extraction. pH: {ph}. Phosphorus (Bray P): {bray_p}. Mineral nitrogen: {nitrogen}. Recommendation: {rec}.",
            mtype="semantic", src="canterbury_soil", stype="lab_report",
            contradicts=contra,
            tags=["C01", "soil_test", "canterbury"]))

    # Agronomist notes on the discrepancy
    ev = datetime(2032, 4, 5, 14, 0, tzinfo=timezone.utc)
    m = mid()
    ids["sarah_note"] = m
    mems.append(make_mem(m, ev, ev+timedelta(hours=1), ev+timedelta(hours=3), ev+timedelta(hours=4),
        "Sarah Chen", "noted", "lab discrepancy Clearwater Block 7",
        "Sarah Chen noted significant discrepancy between AgriLab NZ and Canterbury Soil results for Clearwater Block 7 in 2032. Olsen P (AgriLab) reads 20 mg/kg while Bray P (Canterbury) reads 35 mg/kg. Different extraction methods explain part of the gap but pH readings also differ by 0.2 units. Recommended splitting the difference for fertilizer application.",
        mtype="semantic", src="agronomist_notes", stype="professional_assessment",
        tags=["C01", "soil_test", "reconciliation"]))

    return mems, ids

def gen_c02():
    """Source-dependent price data."""
    mems = []
    ids = {}

    # Multiple price sources for wheat on same dates
    for year, month, coop_price, nzx_price, export_price, usda_index in [
        (2031, 6, "$385/tonne", "$392/tonne", "$410/tonne FOB", "$378/tonne"),
        (2032, 6, "$420/tonne", "$415/tonne", "$445/tonne FOB", "$402/tonne"),
        (2033, 6, "$395/tonne", "$388/tonne", "$425/tonne FOB", "$370/tonne"),
        (2034, 6, "$440/tonne", "$448/tonne", "$465/tonne FOB", "$425/tonne"),
    ]:
        base_dt = datetime(year, month, 15, 9, 0, tzinfo=timezone.utc)

        for label, price, src_name, stype, delay_h in [
            ("coop", coop_price, "cooperative_records", "internal_record", 0),
            ("nzx", nzx_price, "nzx_futures", "market_data", 2),
            ("export", export_price, "export_buyer", "commercial_offer", 4),
            ("usda", usda_index, "usda_index", "government_data", 8),
        ]:
            ev = base_dt + timedelta(hours=delay_h)
            m = mid()
            ids[f"{label}_{year}"] = m
            contras = [ids[f"{other}_{year}"] for other in ["coop","nzx","export","usda"]
                       if f"{other}_{year}" in ids and other != label]
            mems.append(make_mem(m, ev, ev+timedelta(hours=1), ev+timedelta(hours=2), ev+timedelta(hours=3),
                "wheat", "price", f"{price}, {src_name}, June {year}",
                f"Wheat price from {src_name}: {price} as of June {year}. Source: {src_name}.",
                mtype="semantic", src=src_name, stype=stype,
                contradicts=contras,
                tags=["C02", "wheat_price", str(year)]))

    return mems, ids

def gen_c03():
    """Revised estimates (temporal contradiction)."""
    mems = []
    ids = {}

    # Clearwater Block 7 wheat yield 2032 — four progressive estimates
    estimates = [
        ("satellite", datetime(2032, 3, 20, tzinfo=timezone.utc), "6.2 tonnes/ha",
         "Satellite NDVI analysis estimates Clearwater Block 7 wheat yield at 6.2 tonnes/ha for the 2032 season. Based on March vegetation index and historical correlation model. Confidence: moderate.",
         0.6, "satellite_estimate", "remote_sensing"),
        ("agronomist_walk", datetime(2032, 5, 15, tzinfo=timezone.utc), "5.8 tonnes/ha",
         "Sarah Chen's field walk estimate for Clearwater Block 7 wheat: 5.8 tonnes/ha. Tiller count below average, some moisture stress evident. Downward revision from satellite estimate.",
         0.75, "agronomist_walk", "professional_assessment"),
        ("pre_harvest", datetime(2032, 10, 10, tzinfo=timezone.utc), "5.4 tonnes/ha",
         "Pre-harvest sampling of Clearwater Block 7 wheat: 5.4 tonnes/ha estimated. Twenty quadrat samples averaged. Grain fill below expectations due to late-season dry spell. Further downward revision.",
         0.9, "pre_harvest_sample", "field_measurement"),
        ("actual_harvest", datetime(2032, 12, 18, tzinfo=timezone.utc), "5.1 tonnes/ha",
         "Actual harvest yield for Clearwater Block 7 wheat 2032: 5.1 tonnes/ha (2,142 tonnes from 420 ha). Weigh-bridge certified. Below all prior estimates.",
         1.0, "harvest_records", "certified_measurement"),
    ]

    prev_id = None
    for label, ev, value, text, conf, src, stype in estimates:
        m = mid()
        ids[f"yield_{label}"] = m
        sup = [prev_id] if prev_id else []
        contra = [ids[f"yield_{k}"] for k in ["satellite","agronomist_walk","pre_harvest","actual_harvest"]
                  if f"yield_{k}" in ids and f"yield_{k}" != f"yield_{label}"]
        mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=2), ev+timedelta(days=3),
            "Clearwater Block 7 wheat 2032", "yield_estimate", value,
            text, mtype="semantic", conf=conf, src=src, stype=stype,
            supersedes=sup, contradicts=contra,
            tags=["C03", "yield", "Clearwater"]))
        prev_id = m

    # Second field — Pōhatu canola 2033
    estimates2 = [
        ("satellite", datetime(2033, 4, 1, tzinfo=timezone.utc), "2.8 tonnes/ha",
         "Satellite estimate for Pōhatu Farm canola 2033: 2.8 tonnes/ha based on April NDVI.",
         0.6, "satellite_estimate", "remote_sensing"),
        ("agronomist", datetime(2033, 6, 10, tzinfo=timezone.utc), "3.1 tonnes/ha",
         "Sarah Chen estimates Pōhatu canola at 3.1 tonnes/ha — upward revision from satellite. Crop looks better than expected after good spring rains.",
         0.75, "agronomist_walk", "professional_assessment"),
        ("actual", datetime(2033, 12, 5, tzinfo=timezone.utc), "2.6 tonnes/ha",
         "Actual harvest yield for Pōhatu Farm canola 2033: 2.6 tonnes/ha (806 tonnes from 310 ha). Below both estimates — late frost damage in October.",
         1.0, "harvest_records", "certified_measurement"),
    ]
    prev_id = None
    for label, ev, value, text, conf, src, stype in estimates2:
        m = mid()
        ids[f"pohatu_{label}"] = m
        sup = [prev_id] if prev_id else []
        mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=2), ev+timedelta(days=3),
            "Pōhatu Farm canola 2033", "yield_estimate", value,
            text, mtype="semantic", conf=conf, src=src, stype=stype,
            supersedes=sup,
            tags=["C03", "yield", "Pōhatu"]))
        prev_id = m

    return mems, ids

def gen_c04():
    """Observer disagreement — pest counts."""
    mems = []
    ids = {}

    # Aphid counts — four observers, same field, same week
    ev_base = datetime(2031, 11, 8, tzinfo=timezone.utc)

    observers = [
        ("hana", "Hana Tūhoe", "12 per tiller", 0.9,
         "Hana Tūhoe's aphid count for Clearwater Block 3, November 2031: 12 aphids per tiller average (n=50 tillers, systematic transect). Below economic threshold of 15/tiller. No spray recommended at this time.",
         "entomologist_count", "professional_assessment"),
        ("david", "David Kāhui", "20-25 per tiller", 0.5,
         "David Kāhui estimated aphid numbers at 20-25 per tiller on Clearwater Block 3 during his November 2031 field round. Noted heavy infestation in headland rows. Recommended spray application.",
         "field_ops_estimate", "informal_estimate"),
        ("drone", "drone imaging system", "8.3 per tiller", 0.7,
         "Automated drone imaging analysis for Clearwater Block 3, November 2031: average aphid density 8.3 per tiller across 200 sample points. Algorithm v3.2 calibrated against manual counts. Note: algorithm tends to undercount in dense canopy.",
         "drone_analysis", "automated_measurement"),
        ("regional", "regional council", "15 per tiller (district average)", 0.4,
         "Canterbury Regional Council seasonal pest report, November 2031: district average aphid density 15 per tiller for wheat crops. Based on 30 sentinel sites across the region. Clearwater not individually sampled.",
         "regional_council", "government_data"),
    ]

    for label, observer, count, conf, text, src, stype in observers:
        m = mid()
        ids[f"aphid_{label}"] = m
        contras = [ids[f"aphid_{k}"] for k in ["hana","david","drone","regional"]
                   if f"aphid_{k}" in ids and k != label]
        mems.append(make_mem(m, ev_base+timedelta(days=["hana","david","drone","regional"].index(label)),
            ev_base+timedelta(days=["hana","david","drone","regional"].index(label), hours=2),
            ev_base+timedelta(days=["hana","david","drone","regional"].index(label), hours=4),
            ev_base+timedelta(days=["hana","david","drone","regional"].index(label), hours=6),
            "Clearwater Block 3 aphids", "count", f"{count} ({observer})",
            text, mtype="semantic", belief=observer, conf=conf, src=src, stype=stype,
            contradicts=contras,
            tags=["C04", "pest_count", "aphids"]))

    # Second pest disagreement: grass grub in pasture
    ev_base2 = datetime(2032, 8, 15, tzinfo=timezone.utc)
    grub_obs = [
        ("rob", "Rob Ellison", "180 per m²", 0.6,
         "Rob Ellison's grass grub count on Brewer Downs paddock 12, August 2032: 180 per m² from spade sampling (5 samples). Above damage threshold of 150/m². Recommended treatment.",
         "livestock_manager", "informal_estimate"),
        ("hana2", "Hana Tūhoe", "140 per m²", 0.85,
         "Hana Tūhoe's systematic grass grub survey on Brewer Downs paddock 12, August 2032: 140 per m² (n=20 samples, stratified grid). Below treatment threshold. Natural predation expected to reduce numbers by spring.",
         "entomologist_count", "professional_assessment"),
    ]
    for label, observer, count, conf, text, src, stype in grub_obs:
        m = mid()
        ids[f"grub_{label}"] = m
        mems.append(make_mem(m, ev_base2, ev_base2+timedelta(hours=3), ev_base2+timedelta(hours=5), ev_base2+timedelta(hours=7),
            "Brewer Downs paddock 12 grass grub", "count", f"{count} ({observer})",
            text, mtype="semantic", belief=observer, conf=conf, src=src, stype=stype,
            tags=["C04", "pest_count", "grass_grub"]))

    return mems, ids

def gen_c05():
    """Weather station vs forecast conflict."""
    mems = []
    ids = {}

    # Rainfall event — four sources
    ev = datetime(2033, 3, 14, 6, 0, tzinfo=timezone.utc)

    sources = [
        ("farm_station", "Pōhatu Farm weather station", "42mm",
         "Pōhatu Farm weather station recorded 42mm of rainfall on 14 March 2033 between 0600 and 1800 NZDT. Peak intensity: 18mm/hour at 1100. Wind: NW 35 km/h gusting 55.",
         1.0, "farm_weather_station", "direct_measurement"),
        ("metservice", "MetService forecast", "15-20mm predicted",
         "MetService forecast issued 13 March 2033 for Canterbury Plains: 15-20mm rainfall expected 14 March. Moderate confidence. Northwest flow with embedded frontal band.",
         0.5, "metservice", "weather_forecast"),
        ("council_gauge", "regional council gauge", "38mm",
         "Canterbury Regional Council rain gauge at Tai Tapu (3km from Pōhatu Farm) recorded 38mm on 14 March 2033. Gauge site is in slightly sheltered position relative to Pōhatu.",
         0.95, "regional_council_gauge", "direct_measurement"),
        ("insurance", "insurance assessor", "approximately 50mm",
         "Insurance assessor's report for Pōhatu Farm flood claim, 14 March 2033: estimated rainfall approximately 50mm based on ponding measurements and soil saturation analysis. Note: assessor visited site on 16 March.",
         0.6, "insurance_assessment", "indirect_estimate"),
    ]

    for label, source, amount, text, conf, src, stype in sources:
        m = mid()
        ids[f"rain_{label}"] = m
        contras = [ids[f"rain_{k}"] for k in ["farm_station","metservice","council_gauge","insurance"]
                   if f"rain_{k}" in ids and k != label]
        mems.append(make_mem(m, ev, ev+timedelta(hours=12), ev+timedelta(days=1), ev+timedelta(days=2),
            "Pōhatu Farm rainfall", "measurement", f"{amount} ({source})",
            text, mtype="semantic", belief=source, conf=conf, src=src, stype=stype,
            contradicts=contras,
            tags=["C05", "weather", "rainfall"]))

    # Second weather event — frost
    ev2 = datetime(2033, 10, 3, 4, 0, tzinfo=timezone.utc)
    frost_sources = [
        ("station", "Riverside Farm station", "-3.2°C",
         "Riverside Farm weather station recorded minimum temperature -3.2°C at 0415 on 3 October 2033. Duration below 0°C: 4.5 hours. Ground frost confirmed visually at dawn.",
         1.0, "farm_weather_station", "direct_measurement"),
        ("forecast", "MetService", "-1°C predicted",
         "MetService frost warning for Canterbury 3 October 2033: minimum -1°C expected in sheltered valleys. Light frost possible on exposed sites.",
         0.5, "metservice", "weather_forecast"),
        ("niwa", "NIWA climate station", "-2.8°C",
         "NIWA Lincoln climate station (8km from Riverside) recorded -2.8°C minimum on 3 October 2033. Station in open paddock, standard Stevenson screen.",
         0.95, "niwa_station", "direct_measurement"),
    ]
    for label, source, temp, text, conf, src, stype in frost_sources:
        m = mid()
        ids[f"frost_{label}"] = m
        mems.append(make_mem(m, ev2, ev2+timedelta(hours=4), ev2+timedelta(hours=8), ev2+timedelta(hours=12),
            "Riverside Farm frost", "temperature", f"{temp} ({source})",
            text, mtype="semantic", belief=source, conf=conf, src=src, stype=stype,
            tags=["C05", "weather", "frost"]))

    return mems, ids

def gen_c06():
    """Contradictory regulatory guidance."""
    mems = []
    ids = {}

    regs = [
        ("mpi_2031", datetime(2031, 2, 1, tzinfo=timezone.utc), "MPI", "180 kg/ha/year",
         "MPI Bulletin 2031/04: Maximum nitrogen application rate for Canterbury irrigated cropland: 180 kg N/ha/year. Effective 1 March 2031. Compliance monitoring via farm environment plans.",
         "regulatory", "government_bulletin"),
        ("industry_2032", datetime(2032, 5, 15, tzinfo=timezone.utc), "NZ Cropping Industry", "140 kg/ha/year recommended",
         "NZ Cropping Industry best practice guide, May 2032: Recommended maximum nitrogen application 140 kg N/ha/year for Canterbury wheat crops. Based on latest leaching research. Voluntary target.",
         "semantic", "industry_guideline"),
        ("regional_council", datetime(2030, 7, 1, tzinfo=timezone.utc), "Canterbury Regional Council", "160 kg/ha/year",
         "Canterbury Regional Council Plan Change 7 (operative 2030): Maximum nitrogen discharge allowance 160 kg N/ha/year for irrigated cropland on deep silt loam. Varies by soil type.",
         "regulatory", "regional_rule"),
        ("mpi_2033", datetime(2033, 8, 1, tzinfo=timezone.utc), "MPI", "150 kg/ha/year",
         "MPI Updated Guidance 2033/12: Revised maximum nitrogen application rate for Canterbury irrigated cropland: 150 kg N/ha/year. Effective 1 October 2033. Supersedes Bulletin 2031/04. Aligned with NPS-FM 2020 targets.",
         "regulatory", "government_bulletin"),
    ]

    for label, ev, source, limit, text, mtype, stype in regs:
        m = mid()
        ids[label] = m
        sup = []
        if label == "mpi_2033":
            sup = [ids["mpi_2031"]]
        mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=3), ev+timedelta(days=5),
            "nitrogen application limit", "regulation", f"{limit} ({source})",
            text, mtype=mtype, src=source, stype=stype,
            supersedes=sup,
            tags=["C06", "regulation", "nitrogen"]))

    # Farmer confusion
    ev = datetime(2033, 9, 10, 10, 0, tzinfo=timezone.utc)
    m = mid()
    ids["confusion"] = m
    mems.append(make_mem(m, ev, ev+timedelta(hours=1), ev+timedelta(hours=3), ev+timedelta(hours=4),
        "Margaret Holt", "raised_concern", "nitrogen limit confusion",
        "Margaret Holt raised concern at September 2033 cooperative meeting: four different nitrogen limits in play — MPI old (180), MPI new (150), regional council (160), and industry recommendation (140). Asked Sarah Chen to prepare guidance for members on which limit applies.",
        src="meeting_minutes", stype="meeting_record",
        tags=["C06", "regulation", "nitrogen"]))

    return mems, ids

def gen_c07():
    """Self-contradicting records."""
    mems = []
    ids = {}

    # Tractor T-04 service date contradictions
    ev1 = datetime(2032, 3, 1, 9, 0, tzinfo=timezone.utc)
    m = mid()
    ids["t04_log"] = m
    mems.append(make_mem(m, ev1, ev1+timedelta(hours=1), ev1+timedelta(hours=2), ev1+timedelta(hours=3),
        "Tractor T-04", "scheduled_service", "15 March 2032",
        "Equipment maintenance schedule: Tractor T-04 (John Deere 6155R) due for 500-hour service on 15 March 2032. Service items: engine oil, hydraulic filters, air filter, grease points. Booked with Canterbury Farm Services.",
        mtype="procedural", src="maintenance_log", stype="schedule",
        tags=["C07", "equipment", "T-04"]))

    ev2 = datetime(2032, 3, 12, 14, 0, tzinfo=timezone.utc)
    m = mid()
    ids["t04_email"] = m
    mems.append(make_mem(m, ev2, ev2+timedelta(hours=1), ev2+timedelta(hours=2), ev2+timedelta(hours=3),
        "Tom Brewer", "emailed", "T-04 service rescheduled to 22 March",
        "Email from Tom Brewer to Margaret Holt, 12 March 2032: 'Need to reschedule T-04 service from 15 March to 22 March. David needs the tractor for sowing on Block 4 next week. Canterbury Farm Services confirmed the new date.'",
        src="email", stype="correspondence",
        contradicts=[ids["t04_log"]],
        tags=["C07", "equipment", "T-04"]))

    ev3 = datetime(2032, 3, 18, 8, 0, tzinfo=timezone.utc)
    m = mid()
    ids["t04_invoice"] = m
    mems.append(make_mem(m, ev3, ev3+timedelta(hours=6), ev3+timedelta(hours=8), ev3+timedelta(hours=10),
        "Canterbury Farm Services", "invoiced", "T-04 service completed 18 March 2032",
        "Invoice #CFS-2032-0847 from Canterbury Farm Services, dated 18 March 2032. Tractor T-04 (JD 6155R, 2,847 hours): 500-hour service completed. Parts: oil filter, hydraulic filter set, air filter. Labour: 3.5 hours. Total: $1,240+GST.",
        src="invoice", stype="financial_document",
        contradicts=[ids["t04_log"], ids["t04_email"]],
        tags=["C07", "equipment", "T-04"]))

    ev4_start = datetime(2032, 3, 15, 7, 0, tzinfo=timezone.utc)
    m = mid()
    ids["t04_gps"] = m
    mems.append(make_mem(m, ev4_start, ev4_start+timedelta(hours=10), ev4_start+timedelta(hours=12), ev4_start+timedelta(hours=14),
        "Tractor T-04 GPS", "location_log", "in field 15 March 2032",
        "GPS log for Tractor T-04, 15 March 2032: unit operated on Clearwater Block 4 from 0700 to 1730 NZDT. Total distance: 47km. Engine hours logged: 10.2. Operator: David Kāhui. Confirms tractor was not at workshop on scheduled service date.",
        conf=1.0, src="gps_log", stype="automated_measurement",
        contradicts=[ids["t04_log"]],
        tags=["C07", "equipment", "T-04"]))

    # Second contradiction set — fertilizer delivery
    ev5 = datetime(2031, 8, 10, tzinfo=timezone.utc)
    m = mid()
    ids["fert_order"] = m
    mems.append(make_mem(m, ev5, ev5+timedelta(hours=2), ev5+timedelta(hours=4), ev5+timedelta(hours=6),
        "Thornfield Cooperative", "ordered", "25 tonnes urea from Ravensdown",
        "Purchase order PO-2031-142: 25 tonnes granular urea ordered from Ravensdown for autumn application. Delivery requested week of 20 August 2031 to Clearwater Farm store.",
        mtype="procedural", src="purchase_order", stype="financial_document",
        tags=["C07", "fertilizer"]))

    ev6 = datetime(2031, 8, 22, 10, 0, tzinfo=timezone.utc)
    m = mid()
    ids["fert_delivery"] = m
    mems.append(make_mem(m, ev6, ev6+timedelta(hours=2), ev6+timedelta(hours=4), ev6+timedelta(hours=6),
        "Ravensdown", "delivered", "22 tonnes urea",
        "Ravensdown delivery docket DD-48291, 22 August 2031: 22 tonnes granular urea delivered to Clearwater Farm store. Driver noted: 'Short shipment due to supply constraints. Remaining 3 tonnes scheduled next week.'",
        src="delivery_docket", stype="logistics_document",
        contradicts=[ids["fert_order"]],
        tags=["C07", "fertilizer"]))

    return mems, ids

def gen_background():
    """Background noise memories."""
    mems = []
    entries = [
        (datetime(2029, 3, 1, tzinfo=timezone.utc), "Thornfield Cooperative", "held", "annual general meeting",
         "Thornfield Agricultural Cooperative AGM held March 2029. Margaret Holt elected as cooperative manager. 38 of 42 member farms represented.",
         "episodic", "meeting_minutes", "meeting_record"),
        (datetime(2029, 6, 15, tzinfo=timezone.utc), "Thornfield Cooperative", "purchased", "shared header",
         "Cooperative purchased a John Deere S780 combine header for shared use among members. Cost: $620,000. Funded from capital reserves and member levies.",
         "episodic", "purchase_records", "financial_document"),
        (datetime(2029, 9, 10, tzinfo=timezone.utc), "David Kāhui", "organized", "spring field day",
         "David Kāhui organized a spring field day at Pōhatu Farm, September 2029. Demonstrations of direct drilling and cover cropping. 60 attendees from the district.",
         "episodic", "event_records", "event_report"),
        (datetime(2030, 1, 20, tzinfo=timezone.utc), "Thornfield Cooperative", "renewed", "insurance policies",
         "Annual insurance renewal for all cooperative properties and equipment. Premiums increased 8% due to increased flood risk assessment for Canterbury.",
         "procedural", "insurance_records", "financial_document"),
        (datetime(2030, 4, 5, tzinfo=timezone.utc), "Lachlan Murray", "arranged", "export shipment to Japan",
         "Lachlan Murray arranged first export shipment of 2030 season wheat to Nissin Foods Japan. 2,400 tonnes at $395/tonne CIF Yokohama. Shipping via Port of Lyttelton.",
         "episodic", "export_records", "logistics_document"),
        (datetime(2030, 7, 12, tzinfo=timezone.utc), "Sarah Chen", "conducted", "canola trial assessment",
         "Sarah Chen assessed the cooperative's canola variety trial at Long Flat Farm. Six varieties compared. Pioneer 44Y94 showed highest oil content at 44.2%.",
         "semantic", "trial_records", "professional_assessment"),
        (datetime(2030, 10, 1, tzinfo=timezone.utc), "Hana Tūhoe", "completed", "autumn pest survey",
         "Hana Tūhoe completed the autumn pest survey across 15 cooperative farms. Key findings: slug pressure moderate, no significant insect pest issues ahead of winter.",
         "episodic", "pest_records", "professional_assessment"),
        (datetime(2030, 12, 15, tzinfo=timezone.utc), "Tom Brewer", "scheduled", "winter equipment maintenance",
         "Tom Brewer scheduled winter maintenance programme for cooperative machinery pool. 12 tractors, 3 headers, and assorted implements to be serviced before August.",
         "procedural", "maintenance_records", "schedule"),
        (datetime(2031, 1, 8, tzinfo=timezone.utc), "Wei Zhang", "implemented", "new record-keeping system",
         "Wei Zhang implemented a new cloud-based record-keeping system (FarmIQ) across the cooperative. Training sessions held in January 2031. Replaces paper-based system.",
         "episodic", "admin_records", "team_announcement"),
        (datetime(2031, 4, 20, tzinfo=timezone.utc), "Thornfield Cooperative", "hosted", "MPI biosecurity briefing",
         "MPI biosecurity team visited Thornfield Cooperative in April 2031. Briefing on fall armyworm preparedness and the cooperative's role in the regional surveillance network.",
         "episodic", "biosecurity_records", "meeting_record"),
        (datetime(2031, 7, 1, tzinfo=timezone.utc), "Margaret Holt", "presented", "mid-year financial report",
         "Margaret Holt presented mid-year financials at July 2031 committee meeting. Operating surplus of $182,000, ahead of budget. Equipment fund balance: $340,000.",
         "episodic", "financial_records", "meeting_record"),
        (datetime(2031, 8, 25, tzinfo=timezone.utc), "Rob Ellison", "completed", "annual stock count",
         "Rob Ellison completed annual livestock count across cooperative farms: 12,400 sheep, 2,800 cattle. Brewer Downs carrying 3,200 sheep and 800 cattle.",
         "episodic", "livestock_records", "field_measurement"),
        (datetime(2032, 2, 5, tzinfo=timezone.utc), "David Kāhui", "tested", "new seed drill settings",
         "David Kāhui tested modified seed drill settings on Clearwater Block 2. Increased row spacing from 15cm to 17.5cm. Aim: reduce fungal pressure while maintaining yield.",
         "episodic", "trial_records", "field_measurement"),
        (datetime(2032, 5, 10, tzinfo=timezone.utc), "Lachlan Murray", "negotiated", "freight rate reduction",
         "Lachlan Murray negotiated a 5% freight rate reduction with Mainfreight for the 2032/33 export season. Annual saving estimated at $28,000 for cooperative members.",
         "episodic", "logistics_records", "commercial_agreement"),
        (datetime(2032, 8, 15, tzinfo=timezone.utc), "Thornfield Cooperative", "received", "Sustainable Farming Award",
         "Thornfield Agricultural Cooperative received the Canterbury Sustainable Farming Award 2032 for integrated pest management programme led by Hana Tūhoe.",
         "episodic", "awards_records", "press_release"),
        (datetime(2032, 11, 20, tzinfo=timezone.utc), "Sarah Chen", "recommended", "lime application",
         "Sarah Chen recommended lime application of 2.5 tonnes/ha on Clearwater Blocks 5 and 6 based on declining pH trend. Estimated cost: $45/ha applied.",
         "semantic", "agronomist_notes", "professional_assessment"),
        (datetime(2033, 1, 15, tzinfo=timezone.utc), "Wei Zhang", "produced", "annual data summary 2032",
         "Wei Zhang produced the 2032 annual data summary for the cooperative. Average wheat yield across members: 5.6 tonnes/ha. Average canola: 2.4 tonnes/ha.",
         "semantic", "data_records", "data_analysis"),
        (datetime(2033, 4, 10, tzinfo=timezone.utc), "Tom Brewer", "reported", "header breakdown",
         "Tom Brewer reported the shared S780 header broke down during autumn harvest at Long Flat Farm. Front feeder chain failure. Repaired on-farm in 6 hours. Delayed harvest by one day.",
         "episodic", "maintenance_records", "incident_report"),
        (datetime(2033, 6, 20, tzinfo=timezone.utc), "Thornfield Cooperative", "held", "strategic planning day",
         "Cooperative strategic planning day held June 2033. Key priorities: invest in precision agriculture, expand export markets to Southeast Asia, improve water use efficiency.",
         "episodic", "meeting_minutes", "meeting_record"),
        (datetime(2033, 9, 5, tzinfo=timezone.utc), "Dr. Priya Nair", "published", "soil carbon study",
         "Dr. Priya Nair (AgriLab NZ) published soil carbon findings from cooperative farms in the NZ Journal of Agricultural Science. Direct-drilled paddocks showed 12% higher soil organic carbon than conventionally tilled.",
         "semantic", "research_publication", "academic_paper"),
        (datetime(2033, 12, 1, tzinfo=timezone.utc), "Margaret Holt", "announced", "new member farm",
         "Margaret Holt announced that Kaiapoi Downs (240 ha, dairy support/cropping) has joined the cooperative as the 43rd member farm. Effective January 2034.",
         "episodic", "admin_records", "team_announcement"),
        (datetime(2034, 2, 14, tzinfo=timezone.utc), "Hana Tūhoe", "detected", "fall armyworm",
         "Hana Tūhoe confirmed first detection of fall armyworm (Spodoptera frugiperda) on cooperative land — two moths caught in pheromone trap at Riverside Farm. Reported to MPI within 24 hours.",
         "episodic", "biosecurity_records", "incident_report"),
        (datetime(2034, 5, 1, tzinfo=timezone.utc), "Lachlan Murray", "opened", "new market in Malaysia",
         "Lachlan Murray secured first wheat export contract to a Malaysian flour mill. 800 tonnes at $435/tonne CIF Port Klang. Trial shipment to establish quality credentials.",
         "episodic", "export_records", "commercial_agreement"),
        (datetime(2034, 8, 20, tzinfo=timezone.utc), "Rob Ellison", "reported", "lamb growth rates",
         "Rob Ellison reported above-average lamb growth rates across cooperative farms for winter 2034. Average daily gain: 280g/day. Attributed to mild winter and good pasture covers.",
         "episodic", "livestock_records", "field_measurement"),
        (datetime(2034, 11, 10, tzinfo=timezone.utc), "David Kāhui", "oversaw", "irrigation upgrade",
         "David Kāhui oversaw installation of soil moisture sensors on Clearwater and Pōhatu farms. Twelve sensors installed at three depths. Connected to FarmIQ for automated irrigation scheduling.",
         "episodic", "infrastructure_records", "project_report"),
        (datetime(2035, 1, 5, tzinfo=timezone.utc), "Thornfield Cooperative", "submitted", "environment plan",
         "Thornfield Cooperative submitted updated Farm Environment Plan to Canterbury Regional Council. Covers nutrient management, waterway fencing, winter grazing management for all 43 member farms.",
         "procedural", "environmental_records", "regulatory_submission"),
        (datetime(2035, 4, 15, tzinfo=timezone.utc), "Sarah Chen", "trialled", "variable rate fertilizer",
         "Sarah Chen trialled variable rate fertilizer application on Clearwater Block 7 using GPS-guided spreader. Nitrogen rates varied from 80 to 160 kg/ha based on soil sensor data and yield maps.",
         "episodic", "trial_records", "field_measurement"),
        (datetime(2035, 7, 1, tzinfo=timezone.utc), "Wei Zhang", "upgraded", "data platform",
         "Wei Zhang upgraded the cooperative's data platform to include satellite imagery integration. NDVI maps now available weekly for all member farms during growing season.",
         "episodic", "admin_records", "project_report"),
    ]

    for dt, subj, pred, obj_, text, mtype, src, stype in entries:
        m = mid()
        ev = dt
        mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            subj, pred, obj_, text, mtype=mtype, trole="ground_truth",
            src=src, stype=stype, tags=["background"]))

    return mems

def gen_queries(all_ids):
    """Generate queries."""
    qs = []

    # C01 queries
    qs.append(make_query("Q15-01",
        "What were the soil test results for Clearwater Block 7 in 2032?",
        "contradictory_sources",
        ["Two labs gave different results: AgriLab NZ (Olsen P: 20 mg/kg, pH 6.1) and Canterbury Soil (Bray P: 35 mg/kg, pH 5.9)"],
        ["Results differ due to different extraction methods", "Sarah Chen noted the discrepancy"],
        ["Only one set of results presented as definitive", "Results are the same"],
        list(all_ids.get("c01", {}).values()),
        [],
        conflict=True,
        notes="Must surface that two labs disagree, not pick one"))

    qs.append(make_query("Q15-02",
        "What fertilizer should be applied to Clearwater Block 7 based on 2032 soil tests?",
        "contradictory_sources",
        ["Recommendations conflict: AgriLab says 175 kg/ha super + 140 kg/ha urea; Canterbury says 100 kg/ha super + 160 kg/ha urea"],
        ["Sarah Chen recommended splitting the difference"],
        ["A single definitive recommendation without mentioning conflict"],
        list(all_ids.get("c01", {}).values()),
        [],
        conflict=True,
        notes="Must acknowledge conflicting recommendations"))

    # C02 queries
    qs.append(make_query("Q15-03",
        "What was the wheat price in June 2032?",
        "source_dependent",
        ["Multiple prices: cooperative $420, NZX $415, export $445 FOB, USDA $402"],
        ["Prices vary by source and market type"],
        ["A single price without source attribution"],
        [all_ids["c02"].get(f"{s}_2032","") for s in ["coop","nzx","export","usda"] if f"{s}_2032" in all_ids["c02"]],
        [all_ids["c02"].get(f"{s}_2031","") for s in ["coop","nzx","export","usda"] if f"{s}_2031" in all_ids["c02"]],
        conflict=True,
        notes="Must distinguish between price sources"))

    qs.append(make_query("Q15-04",
        "How did wheat prices change from 2031 to 2034?",
        "source_dependent",
        ["Prices generally increased across all sources", "Cooperative: $385 to $440, NZX: $392 to $448"],
        ["Export prices rose from $410 to $465 FOB"],
        ["Prices decreased", "Only one source cited without noting others"],
        [v for k,v in all_ids["c02"].items()],
        [],
        notes="Trend question spanning multiple years and sources"))

    # C03 queries
    qs.append(make_query("Q15-05",
        "What was the actual wheat yield for Clearwater Block 7 in 2032?",
        "revised_estimates",
        ["5.1 tonnes/ha (2,142 tonnes from 420 ha), weigh-bridge certified"],
        ["Below all prior estimates"],
        ["6.2 tonnes/ha", "5.8 tonnes/ha", "5.4 tonnes/ha", "Earlier estimates presented as final"],
        [all_ids["c03"]["yield_actual_harvest"]],
        [all_ids["c03"].get(f"yield_{k}","") for k in ["satellite","agronomist_walk","pre_harvest"]],
        notes="Must return the final certified value, not earlier estimates"))

    qs.append(make_query("Q15-06",
        "How accurate were the yield predictions for Clearwater Block 7 in 2032?",
        "revised_estimates",
        ["All overestimated: satellite by 1.1t/ha, agronomist by 0.7, pre-harvest by 0.3", "Actual was 5.1 tonnes/ha"],
        ["Progressive downward revision from 6.2 to 5.1"],
        ["Predictions were accurate", "Satellite estimate was correct"],
        list(all_ids["c03"].values()),
        [],
        notes="Requires comparing all estimates against actual"))

    # C04 queries
    qs.append(make_query("Q15-07",
        "How many aphids per tiller were on Clearwater Block 3 in November 2031?",
        "observer_disagreement",
        ["Counts varied by observer: Hana 12/tiller, David 20-25, drone 8.3, regional avg 15"],
        ["Professional count (Hana) is most methodologically rigorous"],
        ["Any single number without noting disagreement", "Exact count is known"],
        [all_ids["c04"].get(f"aphid_{k}","") for k in ["hana","david","drone","regional"]],
        [],
        conflict=True, uncertainty=True,
        notes="Must surface observer disagreement, not pick one number"))

    qs.append(make_query("Q15-08",
        "Was spray recommended for aphids on Clearwater Block 3 in November 2031?",
        "observer_disagreement",
        ["Conflicting: Hana said no (below threshold at 12), David said yes (estimated 20-25)"],
        ["Different counts led to different recommendations"],
        ["Definitively yes or no without noting disagreement"],
        [all_ids["c04"].get(f"aphid_{k}","") for k in ["hana","david"]],
        [],
        conflict=True,
        notes="Recommendation depends on which observer's count is used"))

    # C05 queries
    qs.append(make_query("Q15-09",
        "How much rain fell at Pōhatu Farm on 14 March 2033?",
        "measurement_conflict",
        ["Farm station: 42mm, council gauge 3km away: 38mm; forecast had predicted only 15-20mm"],
        ["Insurance assessor estimated ~50mm but visited 2 days later"],
        ["Exactly 15-20mm", "Exactly 50mm", "Single number without noting variation"],
        [all_ids["c05"].get(f"rain_{k}","") for k in ["farm_station","metservice","council_gauge","insurance"]],
        [],
        conflict=True,
        notes="Must distinguish measured vs predicted vs estimated"))

    qs.append(make_query("Q15-10",
        "Did MetService accurately forecast the March 2033 rainfall for Canterbury?",
        "measurement_conflict",
        ["No — forecast 15-20mm but actual was 42mm at Pōhatu (38mm at nearby council gauge)"],
        ["Significantly underestimated"],
        ["Forecast was accurate", "20mm fell"],
        [all_ids["c05"].get(f"rain_{k}","") for k in ["farm_station","metservice","council_gauge"]],
        [],
        notes="Comparing forecast against multiple measured values"))

    # C06 queries
    qs.append(make_query("Q15-11",
        "What is the current nitrogen application limit for Clearwater Farm?",
        "regulatory_conflict",
        ["MPI limit is 150 kg/ha (from August 2033, supersedes earlier 180)", "Regional council limit is 160 kg/ha"],
        ["The stricter MPI limit of 150 effectively governs", "Industry recommends even lower at 140"],
        ["180 kg/ha", "The limit is 180 kg/ha (this was superseded)"],
        [all_ids["c06"]["mpi_2033"], all_ids["c06"]["regional_council"]],
        [all_ids["c06"]["mpi_2031"]],
        conflict=True,
        notes="Must use the most recent MPI guidance (150), not the superseded 180"))

    qs.append(make_query("Q15-12",
        "Why are farmers confused about nitrogen limits?",
        "regulatory_conflict",
        ["Four different limits exist: MPI old 180, MPI new 150, regional 160, industry 140"],
        ["Margaret Holt raised this at September 2033 meeting"],
        ["There is only one clear limit", "No confusion exists"],
        list(all_ids.get("c06", {}).values()),
        [],
        notes="Requires synthesizing multiple contradictory regulatory sources"))

    # C07 queries
    qs.append(make_query("Q15-13",
        "When was Tractor T-04 actually serviced in March 2032?",
        "self_contradicting",
        ["18 March 2032 (per invoice)", "GPS confirms it was in the field on 15 March (scheduled date)"],
        ["Originally scheduled 15 March, rescheduled to 22 March per email, but actually done 18 March"],
        ["15 March", "22 March", "Service happened on the scheduled date"],
        [all_ids["c07"]["t04_invoice"], all_ids["c07"]["t04_gps"]],
        [all_ids["c07"]["t04_log"], all_ids["c07"]["t04_email"]],
        notes="Invoice + GPS are strongest evidence; schedule and email are weaker"))

    qs.append(make_query("Q15-14",
        "Was the full 25-tonne urea order delivered in August 2031?",
        "self_contradicting",
        ["No — only 22 tonnes delivered. 3 tonnes short due to supply constraints."],
        ["Remaining 3 tonnes scheduled for next week"],
        ["Yes, full delivery", "25 tonnes delivered"],
        [all_ids["c07"]["fert_order"], all_ids["c07"]["fert_delivery"]],
        [],
        conflict=True,
        notes="Delivery docket contradicts purchase order quantity"))

    # Cross-case queries
    qs.append(make_query("Q15-15",
        "What sources of information does the cooperative use for decision-making, and how reliable are they?",
        "cross_case",
        ["Multiple sources often disagree: labs, weather stations, market prices, pest counts, regulations"],
        ["Measured data is more reliable than forecasts or estimates"],
        ["All sources agree", "One authoritative source for everything"],
        [],
        [],
        notes="Meta-question about the reliability landscape across all cases"))

    # Control queries
    qs.append(make_query("Q15-16",
        "When was the shared combine header purchased and how much did it cost?",
        "control",
        ["June 2029, John Deere S780, $620,000"],
        ["Funded from capital reserves and member levies"],
        [],
        [], [],
        difficulty="easy",
        notes="Simple factual retrieval from background — no contradiction"))

    qs.append(make_query("Q15-17",
        "Who detected fall armyworm on cooperative land?",
        "control",
        ["Hana Tūhoe, February 2034, at Riverside Farm"],
        ["Two moths caught in pheromone trap", "Reported to MPI within 24 hours"],
        [],
        [], [],
        difficulty="easy",
        notes="Simple factual retrieval from background"))

    return qs

def main():
    out = os.path.join(os.getcwd(), OUT) if len(sys.argv) < 2 else sys.argv[1]
    os.makedirs(out, exist_ok=True)

    all_mems = []
    all_ids = {}

    # Generate case memories
    for name, gen_fn in [("c01", gen_c01), ("c02", gen_c02), ("c03", gen_c03),
                          ("c04", gen_c04), ("c05", gen_c05), ("c06", gen_c06), ("c07", gen_c07)]:
        mems, ids = gen_fn()
        all_mems.extend(mems)
        all_ids[name] = ids

    # Background
    bg_mems = gen_background()
    all_mems.extend(bg_mems)

    # Queries
    queries = gen_queries(all_ids)

    # Write memories
    mem_path = os.path.join(out, "memories.jsonl")
    with open(mem_path, 'w') as f:
        for m in all_mems:
            f.write(json.dumps(m) + "\n")

    # Write queries
    q_path = os.path.join(out, "queries.jsonl")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    # Manifest
    files_info = []
    for fname in ["memories.jsonl", "queries.jsonl"]:
        fp = os.path.join(out, fname)
        h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
        files_info.append({"path": fname, "sha256": h, "bytes": os.path.getsize(fp)})

    manifest = {
        "experiment": "exp15",
        "title": "Contradictory Metadata",
        "story_id": "thornfield_coop",
        "canonical_memory_count": len(all_mems),
        "query_count": len(queries),
        "files": files_info
    }
    with open(os.path.join(out, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)

    # Story bible
    sb_src = "/tmp/claude-0/-home-user-memory-testing/6ffa00f0-af4e-5ad8-9c00-025401d96b92/scratchpad/exp15/story_bible.md"
    if os.path.exists(sb_src):
        import shutil
        shutil.copy(sb_src, os.path.join(out, "story_bible.md"))

    print(f"Generated {len(all_mems)} memories, {len(queries)} queries")
    print(f"Output: {out}")

    # Distribution
    tag_counts = {}
    for m in all_mems:
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
