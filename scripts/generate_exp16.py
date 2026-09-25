#!/usr/bin/env python3
"""Generate Experiment 16 — Multi-hop Dependencies.

Hōkūleʻa Transit Authority setting with multi-hop causal chains:
maintenance→delay cascades, transfer cascades, staff dependency,
budget chains, information chains, equipment provenance, and
temporal dependency chains.
"""

import json, hashlib, os, sys, uuid
from datetime import datetime, timedelta, timezone

OUT = "experiment_16_multi_hop_dependencies"

def mid(prefix="E16"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def make_mem(memory_id, ev, obs, auth, ing, subj, pred, obj_, text,
             mtype="episodic", trole="ground_truth", belief="hta",
             conf=1.0, src="", stype="direct_observation",
             derived=None, supersedes=None, contradicts=None, duplicates=None,
             aliases=None, scope="Hōkūleʻa Transit Authority", tags=None):
    return {
        "memory_id": memory_id, "experiment": "exp16",
        "story_id": "hokulea_transit",
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
               scope=True, abstain=False, notes="", hop_count=1):
    return {
        "query_id": qid, "query": query, "category": cat,
        "expected_claims": expected, "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": relevant, "distractor_memory_ids": distractors,
        "difficulty": difficulty,
        "must_surface_uncertainty": uncertainty, "must_surface_conflict": conflict,
        "must_disambiguate": disambig, "must_preserve_scope": scope,
        "should_abstain": abstain, "notes": notes, "hop_count": hop_count
    }

BASE = datetime(2030, 1, 1, tzinfo=timezone.utc)

def gen_c01():
    """Chain: budget cut → parts delay → maintenance → vehicle swap → cancellation → complaints."""
    mems = []
    ids = {}
    chain = []

    # Link 1: Budget cut
    ev = datetime(2032, 7, 1, tzinfo=timezone.utc)
    m = mid(); ids["budget_cut"] = m; chain.append(m)
    mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=3), ev+timedelta(days=5),
        "HTA Board", "approved", "Q3 2032 budget reduction",
        "HTA Board approved 12% operating budget reduction for Q3 2032. Ravi Mehta directed to implement cuts across all divisions. Maintenance procurement budget reduced from $2.4M to $1.9M per quarter.",
        mtype="procedural", src="board_minutes", stype="official_record", tags=["C01", "budget"]))

    # Link 2: Parts procurement delayed
    ev2 = datetime(2032, 7, 20, tzinfo=timezone.utc)
    m = mid(); ids["parts_delay"] = m; chain.append(m)
    mems.append(make_mem(m, ev2, ev2+timedelta(days=1), ev2+timedelta(days=2), ev2+timedelta(days=3),
        "Anika Sharma", "deferred", "Bus-101 brake overhaul parts order",
        "Anika Sharma deferred order for Bus-101 brake overhaul parts due to Q3 budget constraints. Original delivery expected August 5; now pushed to September pending budget clearance. Bus-101 remains operational with existing brakes within tolerance.",
        src="maintenance_log", stype="internal_record",
        derived=[ids["budget_cut"]], tags=["C01", "maintenance"]))

    # Link 3: Bus-101 extended maintenance
    ev3 = datetime(2032, 8, 25, tzinfo=timezone.utc)
    m = mid(); ids["bus101_down"] = m; chain.append(m)
    mems.append(make_mem(m, ev3, ev3+timedelta(hours=4), ev3+timedelta(hours=8), ev3+timedelta(hours=12),
        "Bus-101", "entered_maintenance", "extended downtime due to deferred parts",
        "Bus-101 pulled from service for brake overhaul. Parts still not received (order deferred July 20). Estimated return to service: September 15 minimum. Sione Vunipola requested vehicle reassignment to cover Route 12.",
        src="depot_log", stype="operational_record",
        derived=[ids["parts_delay"]], tags=["C01", "maintenance"]))

    # Link 4: Bus-102 reassigned
    ev4 = datetime(2032, 8, 26, 6, 0, tzinfo=timezone.utc)
    m = mid(); ids["bus102_reassign"] = m; chain.append(m)
    mems.append(make_mem(m, ev4, ev4+timedelta(hours=2), ev4+timedelta(hours=4), ev4+timedelta(hours=6),
        "Kira Nakamura", "reassigned", "Bus-102 from Route 14 to Route 12",
        "Kira Nakamura reassigned Bus-102 from Route 14 to Route 12 to cover Bus-101 downtime. Route 14 left without assigned vehicle. Kira noted Route 14 has lower ridership and can absorb temporary cancellation.",
        src="scheduling_system", stype="operational_record",
        derived=[ids["bus101_down"]], tags=["C01", "scheduling"]))

    # Link 5: Route 14 cancellation
    ev5 = datetime(2032, 8, 26, 7, 0, tzinfo=timezone.utc)
    m = mid(); ids["route14_cancel"] = m; chain.append(m)
    mems.append(make_mem(m, ev5, ev5+timedelta(hours=1), ev5+timedelta(hours=3), ev5+timedelta(hours=5),
        "Route 14", "cancelled", "temporary cancellation effective 26 August 2032",
        "Route 14 service temporarily cancelled from 26 August 2032 due to vehicle shortage. Passengers directed to Route 10 with transfer at Downtown. Estimated 400 daily riders affected.",
        src="service_bulletin", stype="public_notice",
        derived=[ids["bus102_reassign"]], tags=["C01", "service"]))

    # Link 6: Complaints and media
    ev6 = datetime(2032, 9, 2, tzinfo=timezone.utc)
    m = mid(); ids["complaints"] = m; chain.append(m)
    mems.append(make_mem(m, ev6, ev6+timedelta(hours=4), ev6+timedelta(hours=8), ev6+timedelta(hours=12),
        "HTA", "received", "142 complaints about Route 14 cancellation",
        "HTA received 142 passenger complaints in first week of Route 14 cancellation. Local newspaper ran article 'Transit Cuts Leave East Side Stranded.' Board member questioned why a budget cut led to route cancellation. Keanu Lani asked for full chain-of-events briefing.",
        src="complaints_register", stype="public_feedback",
        derived=[ids["route14_cancel"]], tags=["C01", "complaints"]))

    return mems, ids

def gen_c02():
    """Transfer cascade: ferry failure → missed connections → network cascade."""
    mems = []
    ids = {}

    # Link 1: Ferry-A engine failure
    ev = datetime(2033, 3, 8, 6, 0, tzinfo=timezone.utc)
    m = mid(); ids["ferry_fail"] = m
    mems.append(make_mem(m, ev, ev+timedelta(hours=1), ev+timedelta(hours=3), ev+timedelta(hours=5),
        "Ferry-A", "engine_failure", "8 March 2033 morning service",
        "Ferry-A suffered port engine failure during 0600 crossing on 8 March 2033. Vessel towed to Harbor. Leilani Kim grounded Ferry-A pending inspection. Estimated repair: 10 days.",
        src="incident_report", stype="operational_record", tags=["C02", "ferry"]))

    # Link 2: Ferry-B schedule change
    ev2 = datetime(2033, 3, 8, 8, 0, tzinfo=timezone.utc)
    m = mid(); ids["ferry_schedule"] = m
    mems.append(make_mem(m, ev2, ev2+timedelta(hours=1), ev2+timedelta(hours=2), ev2+timedelta(hours=3),
        "Leilani Kim", "revised", "ferry schedule to single-vessel operation",
        "Leilani Kim implemented emergency single-vessel ferry schedule using Ferry-B only. Crossings reduced from every 30 minutes to every 75 minutes. Capacity reduced by 55%.",
        src="scheduling_system", stype="operational_record",
        derived=[ids["ferry_fail"]], tags=["C02", "ferry"]))

    # Link 3: Missed bus-ferry connections
    ev3 = datetime(2033, 3, 8, 9, 30, tzinfo=timezone.utc)
    m = mid(); ids["missed_connections"] = m
    mems.append(make_mem(m, ev3, ev3+timedelta(hours=1), ev3+timedelta(hours=3), ev3+timedelta(hours=5),
        "Routes 12 and 22", "connection_failure", "Harbor transfer point",
        "Route 12 and Route 22 bus arrivals at Harbor no longer aligned with ferry departures due to revised schedule. Estimated 60% of transferring passengers missing their ferry connection. Average wait extended from 8 minutes to 45 minutes.",
        src="operations_report", stype="operational_record",
        derived=[ids["ferry_schedule"]], tags=["C02", "connections"]))

    # Link 4: Emergency bus deployment
    ev4 = datetime(2033, 3, 8, 11, 0, tzinfo=timezone.utc)
    m = mid(); ids["emergency_bus"] = m
    mems.append(make_mem(m, ev4, ev4+timedelta(hours=1), ev4+timedelta(hours=2), ev4+timedelta(hours=3),
        "Sione Vunipola", "deployed", "Bus-102 as emergency Harbor shuttle",
        "Sione Vunipola deployed Bus-102 from East depot as emergency shuttle between Harbor and West side via the land bridge route. Added 40 minutes to cross-island journey but provided alternative to reduced ferry.",
        src="depot_log", stype="operational_record",
        derived=[ids["missed_connections"]], tags=["C02", "emergency"]))

    # Link 5: Route 10 reduced
    ev5 = datetime(2033, 3, 8, 12, 0, tzinfo=timezone.utc)
    m = mid(); ids["route10_reduced"] = m
    mems.append(make_mem(m, ev5, ev5+timedelta(hours=1), ev5+timedelta(hours=2), ev5+timedelta(hours=3),
        "Route 10", "frequency_reduced", "30-min headway due to Bus-102 redeployment",
        "Route 10 frequency reduced from 15-minute to 30-minute headway after Bus-102 redeployed to emergency Harbor shuttle. Downtown commuters affected during peak hours.",
        src="scheduling_system", stype="operational_record",
        derived=[ids["emergency_bus"]], tags=["C02", "service"]))

    # Link 6: Green Line overcrowding
    ev6 = datetime(2033, 3, 8, 17, 0, tzinfo=timezone.utc)
    m = mid(); ids["greenline_crowd"] = m
    mems.append(make_mem(m, ev6, ev6+timedelta(hours=2), ev6+timedelta(hours=4), ev6+timedelta(hours=6),
        "Green Line", "overcrowding", "March 8 evening peak",
        "Green Line reported severe overcrowding during March 8 evening peak. Load factor reached 185% on 1730 service. Route 10 passengers shifted to light rail due to reduced bus frequency. Jiro Tanaka requested additional rolling stock for next day.",
        src="operations_report", stype="operational_record",
        derived=[ids["route10_reduced"]], tags=["C02", "overcrowding"]))

    return mems, ids

def gen_c03():
    """Staff dependency chain."""
    mems = []
    ids = {}

    ev = datetime(2033, 6, 1, tzinfo=timezone.utc)
    m = mid(); ids["jiro_leave"] = m
    mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
        "Jiro Tanaka", "began", "four-week leave",
        "Jiro Tanaka (Light Rail Division Chief) began four-week annual leave effective 1 June 2033. Keanu Lani appointed Tane Parata as acting LR chief in addition to bus division responsibilities.",
        src="hr_records", stype="personnel_record", tags=["C03", "staff"]))

    ev2 = datetime(2033, 6, 3, tzinfo=timezone.utc)
    m = mid(); ids["tane_covers"] = m
    mems.append(make_mem(m, ev2, ev2+timedelta(hours=2), ev2+timedelta(hours=4), ev2+timedelta(hours=6),
        "Tane Parata", "delegated", "bus scheduling to Kira Nakamura",
        "Tane Parata, managing both bus and LR divisions, delegated day-to-day bus scheduling decisions to Kira Nakamura. Tane focused on LR track maintenance project due in July.",
        src="management_memo", stype="internal_record",
        derived=[ids["jiro_leave"]], tags=["C03", "staff"]))

    ev3 = datetime(2033, 6, 10, tzinfo=timezone.utc)
    m = mid(); ids["kira_reassign"] = m
    mems.append(make_mem(m, ev3, ev3+timedelta(hours=2), ev3+timedelta(hours=4), ev3+timedelta(hours=6),
        "Kira Nakamura", "reassigned", "Bus-103 from Route 20 to Route 22",
        "Kira Nakamura reassigned Bus-103 from Route 20 to Route 22 to improve Harbor connection timing. Kira's previous role was Route 22 coordinator and she judged it needed better service. Route 20 reduced to single-bus operation with Bus-104.",
        src="scheduling_system", stype="operational_record",
        derived=[ids["tane_covers"]], tags=["C03", "scheduling"]))

    ev4 = datetime(2033, 6, 15, tzinfo=timezone.utc)
    m = mid(); ids["route20_gaps"] = m
    mems.append(make_mem(m, ev4, ev4+timedelta(hours=4), ev4+timedelta(hours=8), ev4+timedelta(hours=12),
        "Route 20", "service_gaps", "45-min headways during peak",
        "Route 20 service gaps reaching 45 minutes during peak hours with single-bus operation. University students reporting difficulty reaching campus. 38 complaints in first week.",
        src="operations_report", stype="operational_record",
        derived=[ids["kira_reassign"]], tags=["C03", "service"]))

    ev5 = datetime(2033, 6, 20, tzinfo=timezone.utc)
    m = mid(); ids["blueline_shift"] = m
    mems.append(make_mem(m, ev5, ev5+timedelta(hours=4), ev5+timedelta(hours=8), ev5+timedelta(hours=12),
        "Blue Line", "ridership_spike", "20% increase from Route 20 passengers",
        "Blue Line ridership spiked 20% as Route 20 passengers shifted to light rail via University transfer. Load factor on morning Blue Line services reaching 150%. Overcrowding complaints filed.",
        src="ridership_data", stype="automated_measurement",
        derived=[ids["route20_gaps"]], tags=["C03", "overcrowding"]))

    return mems, ids

def gen_c04():
    """Budget chain: funding cut → ferry maintenance deferred → grounding."""
    mems = []
    ids = {}

    ev = datetime(2034, 1, 15, tzinfo=timezone.utc)
    m = mid(); ids["federal_cut"] = m
    mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=3), ev+timedelta(days=5),
        "Federal Transit Authority", "announced", "15% funding reduction for 2034",
        "Federal Transit Authority announced 15% reduction in transit operating grants for fiscal year 2034. HTA allocation reduced from $18M to $15.3M. Keanu Lani convened emergency budget meeting.",
        mtype="semantic", src="government_bulletin", stype="government_data", tags=["C04", "budget"]))

    ev2 = datetime(2034, 2, 1, tzinfo=timezone.utc)
    m = mid(); ids["hta_budget"] = m
    mems.append(make_mem(m, ev2, ev2+timedelta(days=1), ev2+timedelta(days=2), ev2+timedelta(days=3),
        "Ravi Mehta", "restructured", "HTA operating budget 2034",
        "Ravi Mehta presented restructured budget: ferry division maintenance budget reduced 20% ($800K → $640K), bus maintenance reduced 10%, light rail held steady. Rationale: ferries have most recent major overhaul, can defer some inspections.",
        src="budget_document", stype="financial_record",
        derived=[ids["federal_cut"]], tags=["C04", "budget"]))

    ev3 = datetime(2034, 3, 15, tzinfo=timezone.utc)
    m = mid(); ids["hull_deferred"] = m
    mems.append(make_mem(m, ev3, ev3+timedelta(days=1), ev3+timedelta(days=3), ev3+timedelta(days=5),
        "Anika Sharma", "deferred", "Ferry-B hull inspection to Q4 2034",
        "Anika Sharma deferred Ferry-B scheduled hull inspection from Q1 to Q4 2034 due to budget constraints. Maritime safety certificate expires October 2034. Anika noted the deferral was within regulatory grace period.",
        src="maintenance_plan", stype="internal_record",
        derived=[ids["hta_budget"]], tags=["C04", "maintenance"]))

    ev4 = datetime(2034, 10, 1, tzinfo=timezone.utc)
    m = mid(); ids["ferry_grounded"] = m
    mems.append(make_mem(m, ev4, ev4+timedelta(hours=4), ev4+timedelta(hours=8), ev4+timedelta(hours=12),
        "Maritime NZ", "grounded", "Ferry-B pending overdue hull inspection",
        "Maritime NZ grounded Ferry-B effective 1 October 2034. Safety certificate expired. Hull inspection not completed within grace period. HTA must complete inspection before resumption of service.",
        src="regulatory_notice", stype="government_data",
        derived=[ids["hull_deferred"]], tags=["C04", "regulatory"]))

    ev5 = datetime(2034, 10, 2, tzinfo=timezone.utc)
    m = mid(); ids["single_ferry"] = m
    mems.append(make_mem(m, ev5, ev5+timedelta(hours=2), ev5+timedelta(hours=4), ev5+timedelta(hours=6),
        "Leilani Kim", "implemented", "single-ferry emergency schedule",
        "Leilani Kim implemented single-ferry operation using Ferry-A only (repaired after March 2033 failure). Cross-island capacity halved. Estimated 2,000 daily passengers affected. Similar to March 2033 disruption but worse timing — October is peak tourism season.",
        src="operations_report", stype="operational_record",
        derived=[ids["ferry_grounded"]], tags=["C04", "service"]))

    return mems, ids

def gen_c05():
    """Information chain: bad survey → bad decision → reversal."""
    mems = []
    ids = {}

    ev = datetime(2033, 9, 1, tzinfo=timezone.utc)
    m = mid(); ids["survey"] = m
    mems.append(make_mem(m, ev, ev+timedelta(days=5), ev+timedelta(days=10), ev+timedelta(days=12),
        "HTA Planning", "conducted", "Route 24 ridership survey",
        "HTA Planning department conducted ridership survey for proposed Route 24 extension, September 2033. Methodology: online survey with self-reported travel patterns. Result: projected 800 daily riders for Route 24 extension to Marina District.",
        src="planning_report", stype="survey_data", tags=["C05", "survey"]))

    ev2 = datetime(2033, 11, 1, tzinfo=timezone.utc)
    m = mid(); ids["board_approve"] = m
    mems.append(make_mem(m, ev2, ev2+timedelta(days=1), ev2+timedelta(days=3), ev2+timedelta(days=5),
        "HTA Board", "approved", "Route 24 Marina extension",
        "Board approved Route 24 Marina extension based on projected 800 daily riders. Two additional buses allocated: Bus-103 from Route 20, Bus-104 retained on Route 20 with reduced frequency. Service begins January 2034.",
        src="board_minutes", stype="official_record",
        derived=[ids["survey"]], tags=["C05", "planning"]))

    ev3 = datetime(2034, 1, 15, tzinfo=timezone.utc)
    m = mid(); ids["route20_cut"] = m
    mems.append(make_mem(m, ev3, ev3+timedelta(hours=4), ev3+timedelta(hours=8), ev3+timedelta(hours=12),
        "Route 20", "frequency_reduced", "40-min headway after bus reallocation",
        "Route 20 frequency reduced to 40-minute headway after Bus-103 reallocated to Route 24 extension. Ridership dropped 25% in first month as passengers found alternative transport.",
        src="operations_report", stype="operational_record",
        derived=[ids["board_approve"]], tags=["C05", "service"]))

    ev4 = datetime(2034, 4, 1, tzinfo=timezone.utc)
    m = mid(); ids["survey_error"] = m
    mems.append(make_mem(m, ev4, ev4+timedelta(days=3), ev4+timedelta(days=5), ev4+timedelta(days=7),
        "Malia Reyes", "discovered", "ridership survey methodology error",
        "Malia Reyes identified that the Route 24 ridership survey used self-selection bias: online respondents were disproportionately Marina District residents who wanted the service. Actual ridership after 3 months: 280 daily, not 800 projected. Survey overestimated demand by 65%.",
        src="operations_review", stype="internal_audit",
        derived=[ids["survey"]], tags=["C05", "audit"]))

    ev5 = datetime(2034, 5, 15, tzinfo=timezone.utc)
    m = mid(); ids["reversal"] = m
    mems.append(make_mem(m, ev5, ev5+timedelta(days=1), ev5+timedelta(days=3), ev5+timedelta(days=5),
        "HTA Board", "reversed", "Route 24 extension",
        "Board voted to reverse Route 24 Marina extension effective June 2034. Bus-103 returned to Route 20. However, Route 20 ridership had dropped 25% and recovered only 60% of lost riders by end of 2034. Net ridership loss estimated at 150 daily riders across the network.",
        src="board_minutes", stype="official_record",
        derived=[ids["survey_error"]], tags=["C05", "planning"]))

    return mems, ids

def gen_c06():
    """Equipment provenance chain."""
    mems = []
    ids = {}

    ev = datetime(2031, 6, 1, tzinfo=timezone.utc)
    m = mid(); ids["original_part"] = m
    mems.append(make_mem(m, ev, ev+timedelta(days=1), ev+timedelta(days=2), ev+timedelta(days=3),
        "LR-03", "fitted_with", "brake actuator from Pacific Rail Parts (PRP)",
        "LR-03 fitted with type BKA-400 brake actuators from Pacific Rail Parts (PRP) during initial commissioning, June 2031. Part number: PRP-BKA-400-Rev3. Four units installed per car.",
        mtype="procedural", src="commissioning_records", stype="technical_record", tags=["C06", "equipment"]))

    ev2 = datetime(2032, 3, 1, tzinfo=timezone.utc)
    m = mid(); ids["acquisition"] = m
    mems.append(make_mem(m, ev2, ev2+timedelta(days=5), ev2+timedelta(days=10), ev2+timedelta(days=12),
        "Pacific Rail Parts", "acquired_by", "TransGlobal Components",
        "Pacific Rail Parts (PRP) acquired by TransGlobal Components effective March 2032. PRP product lines to be integrated into TransGlobal catalog. Existing part numbers to be migrated to TGC system.",
        mtype="semantic", src="industry_news", stype="press_release", tags=["C06", "supply_chain"]))

    ev3 = datetime(2033, 1, 15, tzinfo=timezone.utc)
    m = mid(); ids["spec_change"] = m
    mems.append(make_mem(m, ev3, ev3+timedelta(days=3), ev3+timedelta(days=5), ev3+timedelta(days=7),
        "TransGlobal Components", "changed", "BKA-400 specification",
        "TransGlobal Components issued revised specification for BKA-400 brake actuator (now TGC-BKA-400-Rev1). Mounting bolt pattern changed from 4x M12 to 4x M10. Actuator stroke reduced from 65mm to 60mm. 'Improved' model per TGC engineering.",
        mtype="semantic", src="supplier_bulletin", stype="technical_document",
        derived=[ids["acquisition"]], tags=["C06", "equipment"]))

    ev4 = datetime(2033, 8, 10, tzinfo=timezone.utc)
    m = mid(); ids["part_mismatch"] = m
    mems.append(make_mem(m, ev4, ev4+timedelta(hours=4), ev4+timedelta(hours=8), ev4+timedelta(hours=12),
        "Anika Sharma", "discovered", "replacement brake actuator doesn't fit LR-03",
        "During scheduled brake replacement on LR-03, Anika Sharma discovered that the TGC-BKA-400-Rev1 replacement actuator does not fit. Mounting holes misaligned (M10 vs M12) and stroke too short (60mm vs 65mm needed). Original PRP-BKA-400-Rev3 no longer manufactured.",
        src="maintenance_report", stype="incident_report",
        derived=[ids["spec_change"]], tags=["C06", "maintenance"]))

    ev5 = datetime(2033, 8, 15, tzinfo=timezone.utc)
    m = mid(); ids["emergency_source"] = m
    mems.append(make_mem(m, ev5, ev5+timedelta(days=3), ev5+timedelta(days=5), ev5+timedelta(days=7),
        "Anika Sharma", "sourced", "original-spec actuators from secondary market",
        "Anika Sharma located four PRP-BKA-400-Rev3 actuators from a decommissioned light rail system in Osaka. Cost: 3x normal price. Lead time: 3 weeks for international shipping. LR-03 out of service until parts arrive.",
        src="procurement_records", stype="financial_record",
        derived=[ids["part_mismatch"]], tags=["C06", "procurement"]))

    ev6 = datetime(2033, 9, 5, tzinfo=timezone.utc)
    m = mid(); ids["lr03_impact"] = m
    mems.append(make_mem(m, ev6, ev6+timedelta(hours=4), ev6+timedelta(hours=8), ev6+timedelta(hours=12),
        "Blue Line", "single_car_operation", "LR-03 out of service 3 weeks",
        "Blue Line operated single-car service for three weeks (August 15 – September 5) while LR-03 awaited brake actuators. Peak capacity reduced by 50%. Jiro Tanaka arranged shuttle bus connection at University station.",
        src="operations_report", stype="operational_record",
        derived=[ids["emergency_source"]], tags=["C06", "service"]))

    return mems, ids

def gen_c07():
    """Temporal dependency chain — year-over-year decisions."""
    mems = []
    ids = {}

    years = [
        (2030, "HTA approved 5-year network plan. Key decision: extend Green Line to Airport by 2035. Route 10 identified as main feeder service.",
         "HTA Board", "approved", "5-year network plan 2030-2035"),
        (2031, "HTA invested $12M in Green Line track extension to Airport precinct. Construction began on 3.2km new track. Disruption to Route 10 terminus anticipated during 2032 construction.",
         "HTA", "invested", "Green Line Airport extension construction"),
        (2032, "Green Line Airport extension construction disrupted Route 10 terminus for 6 months. Temporary bus bridge installed. Ridership on Route 10 dropped 18% during construction. Cost overrun of $2.1M.",
         "Route 10", "disrupted_by", "Green Line construction 2032"),
        (2033, "Green Line Airport station opened March 2033. Initial ridership 3,200 daily — below 4,500 target. Airport shuttle bus competitors captured expected demand.",
         "HTA", "opened", "Green Line Airport station"),
        (2034, "Ridership patterns shifted: Route 10 recovered to only 90% of pre-construction levels. Airport station ridership grew to 3,800 but shuttle buses retained 40% market share. Revenue shortfall of $1.2M against plan.",
         "HTA", "observed", "ridership pattern shift 2034"),
        (2035, "Kira Nakamura's revised schedule integrated Route 10 and Green Line timetables. Timed transfers reduced journey time by 8 minutes. Airport station ridership grew to 4,100. Shuttle bus market share declined to 25%.",
         "Kira Nakamura", "revised", "integrated schedule Route 10 / Green Line 2035"),
        (2036, "Performance review of 5-year plan. Airport extension delivered 18 months late (opened 2033 vs 2031 target). Current ridership 4,400 vs 4,500 target — nearly achieved. Total cost: $14.1M vs $12M budget. Route 10 still 10% below pre-construction ridership. Lesson: construction disruption lasting effects underestimated.",
         "HTA Board", "reviewed", "5-year plan performance"),
    ]

    prev = None
    for year, text, subj, pred, obj_ in years:
        ev = datetime(year, 6, 1, tzinfo=timezone.utc)
        m = mid(); ids[f"y{year}"] = m
        der = [prev] if prev else []
        mems.append(make_mem(m, ev, ev+timedelta(days=5), ev+timedelta(days=10), ev+timedelta(days=15),
            subj, pred, obj_, text,
            mtype="semantic", src="planning_records", stype="official_record",
            derived=der, tags=["C07", "planning", str(year)]))
        prev = m

    return mems, ids

def gen_background():
    """Background memories."""
    mems = []
    entries = [
        (datetime(2030, 2, 1, tzinfo=timezone.utc), "HTA", "launched", "new website",
         "HTA launched redesigned public website with real-time service information and journey planner."),
        (datetime(2030, 5, 15, tzinfo=timezone.utc), "Keanu Lani", "presented", "annual report 2029",
         "Keanu Lani presented 2029 annual report: 12.4 million passenger trips, 98.1% on-time performance, customer satisfaction 72%."),
        (datetime(2030, 8, 10, tzinfo=timezone.utc), "HTA", "hired", "12 new bus drivers",
         "HTA completed recruitment of 12 new bus drivers. Training programme: 6 weeks classroom, 2 weeks supervised driving."),
        (datetime(2030, 11, 20, tzinfo=timezone.utc), "Malia Reyes", "implemented", "contactless payment",
         "Malia Reyes oversaw rollout of contactless payment across all bus routes. Tap-on/tap-off system using existing fare cards plus bank cards."),
        (datetime(2031, 1, 10, tzinfo=timezone.utc), "Tane Parata", "reported", "bus fleet condition",
         "Tane Parata's annual fleet report: 8 buses in active service, average age 4.2 years, 2 buses due for replacement by 2033."),
        (datetime(2031, 3, 15, tzinfo=timezone.utc), "HTA", "held", "public consultation on fares",
         "HTA held three public consultation sessions on proposed fare structure changes. 340 submissions received. Majority supported distance-based pricing."),
        (datetime(2031, 7, 1, tzinfo=timezone.utc), "Leilani Kim", "completed", "ferry safety drill",
         "Leilani Kim completed quarterly safety drill on both ferries. All crew passed emergency procedures assessment. Evacuation time: Ferry-A 4:12, Ferry-B 3:58."),
        (datetime(2031, 9, 20, tzinfo=timezone.utc), "Jiro Tanaka", "reported", "Green Line track condition",
         "Jiro Tanaka's track condition report: Green Line rail wear within tolerance. One section near Downtown station showing accelerated wear — scheduled for rail grinding."),
        (datetime(2031, 12, 5, tzinfo=timezone.utc), "Ravi Mehta", "presented", "budget forecast 2032",
         "Ravi Mehta presented 2032 budget forecast: total revenue $22M, operating costs $20.5M, capital budget $3.5M. Surplus of $1.5M projected."),
        (datetime(2032, 2, 15, tzinfo=timezone.utc), "Grace Okonkwo", "reorganized", "West depot layout",
         "Grace Okonkwo reorganized West depot bus parking and maintenance bay layout. New flow improves morning dispatch time by 8 minutes."),
        (datetime(2032, 4, 10, tzinfo=timezone.utc), "HTA", "won", "Clean Transit Award 2032",
         "HTA won regional Clean Transit Award for electric bus pilot programme. Two electric buses trialled on Route 22 since 2031."),
        (datetime(2032, 6, 1, tzinfo=timezone.utc), "Sione Vunipola", "trained", "apprentice mechanics",
         "Sione Vunipola began training two apprentice mechanics at East depot. Focus: bus hydraulic systems and electrical diagnostics."),
        (datetime(2032, 11, 10, tzinfo=timezone.utc), "Kira Nakamura", "optimized", "weekday timetable",
         "Kira Nakamura optimized weekday timetable across all bus routes. Reduced dead-running by 12%. Estimated fuel savings: $45,000/year."),
        (datetime(2033, 2, 1, tzinfo=timezone.utc), "HTA", "installed", "CCTV on all ferries",
         "HTA installed CCTV camera systems on both ferries. Maritime NZ requirement for passenger vessels. 8 cameras per vessel."),
        (datetime(2033, 5, 15, tzinfo=timezone.utc), "Malia Reyes", "conducted", "passenger satisfaction survey",
         "Malia Reyes conducted annual passenger satisfaction survey. Overall satisfaction: 68% (down from 72%). Main complaints: frequency and reliability."),
        (datetime(2033, 10, 1, tzinfo=timezone.utc), "Anika Sharma", "established", "preventive maintenance programme",
         "Anika Sharma established new preventive maintenance programme for bus fleet. Scheduled intervals: 10,000 km minor, 50,000 km major. Expected to reduce breakdowns by 25%."),
        (datetime(2034, 3, 1, tzinfo=timezone.utc), "HTA", "introduced", "real-time passenger information displays",
         "HTA installed real-time passenger information displays at 12 major stops. Shows next service, estimated arrival, and disruption alerts."),
        (datetime(2034, 6, 15, tzinfo=timezone.utc), "Keanu Lani", "presented", "mid-year review 2034",
         "Keanu Lani's mid-year review: ridership down 5% due to ferry disruptions and Route 20 issues. On-time performance: 91.2% (target 95%)."),
        (datetime(2034, 9, 1, tzinfo=timezone.utc), "Tane Parata", "received", "two new buses",
         "Tane Parata took delivery of two new Yutong E12 electric buses for Routes 10 and 12. Replaces Bus-101 and Bus-102."),
        (datetime(2035, 1, 10, tzinfo=timezone.utc), "HTA", "launched", "mobile ticketing app",
         "HTA launched mobile ticketing app. Passengers can buy and display tickets on smartphone. 15,000 downloads in first month."),
        (datetime(2035, 4, 20, tzinfo=timezone.utc), "Leilani Kim", "completed", "Ferry-A engine overhaul",
         "Leilani Kim oversaw complete engine overhaul of Ferry-A. New engines: Caterpillar C18 marine diesels. Cost: $450,000. Expected service life: 15 years."),
        (datetime(2035, 8, 1, tzinfo=timezone.utc), "Ravi Mehta", "secured", "federal infrastructure grant",
         "Ravi Mehta secured $5.2M federal infrastructure grant for Blue Line extension feasibility study and preliminary design."),
        (datetime(2035, 11, 15, tzinfo=timezone.utc), "Grace Okonkwo", "hired", "new West depot team",
         "Grace Okonkwo hired three additional maintenance technicians for West depot. Expanding capacity for electric bus servicing."),
        (datetime(2036, 2, 1, tzinfo=timezone.utc), "Jiro Tanaka", "completed", "Green Line platform extensions",
         "Jiro Tanaka completed platform extensions at three Green Line stations to accommodate longer trains. Cost: $1.8M. Capacity increase: 40%."),
        (datetime(2036, 5, 10, tzinfo=timezone.utc), "HTA", "published", "2035 annual report",
         "HTA 2035 annual report: 13.1 million trips (up 5.6% from 2029). Customer satisfaction: 75%. On-time: 94.8%."),
    ]

    for dt, subj, pred, obj_, text in entries:
        m = mid()
        ev = dt
        mems.append(make_mem(m, ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
            subj, pred, obj_, text, src=pred, stype="internal_record", tags=["background"]))

    return mems

def gen_queries(all_ids):
    """Generate queries spanning 1-6 hops."""
    qs = []

    # C01: 5-hop chain
    qs.append(make_query("Q16-01",
        "Why was Route 14 cancelled in August 2032?",
        "causal_chain",
        ["Budget cut → parts delayed → Bus-101 extended maintenance → Bus-102 reassigned to Route 12 → Route 14 left without vehicle"],
        ["Chain started with Q3 2032 12% budget reduction"],
        ["Cancelled due to low ridership", "Bus breakdown", "No connection to budget"],
        list(all_ids["c01"].values()), [],
        hop_count=5, notes="Full 5-hop causal chain"))

    qs.append(make_query("Q16-02",
        "What was the connection between the Q3 2032 budget cut and media coverage?",
        "causal_chain",
        ["Budget cut → deferred parts → Bus-101 down → Bus-102 reassigned → Route 14 cancelled → 142 complaints → newspaper article"],
        [],
        ["No connection", "Direct link from budget to media"],
        list(all_ids["c01"].values()), [],
        hop_count=5, notes="End-to-end chain requires all intermediate links"))

    qs.append(make_query("Q16-03",
        "Why was Bus-102 moved from Route 14?",
        "causal_chain",
        ["Bus-101 was in extended maintenance due to deferred brake parts, so Bus-102 was reassigned to cover Route 12"],
        [],
        ["Bus-102 broke down", "Route 14 was cancelled first"],
        [all_ids["c01"]["bus101_down"], all_ids["c01"]["bus102_reassign"]], [],
        hop_count=2, notes="2-hop subset of the chain"))

    # C02: Transfer cascade
    qs.append(make_query("Q16-04",
        "How did Ferry-A's engine failure on March 8 affect the Green Line?",
        "transfer_cascade",
        ["Ferry-A failure → single-ferry schedule → missed bus-ferry connections → emergency bus from East → Route 10 frequency reduced → passengers shifted to Green Line → overcrowding"],
        [],
        ["No connection", "Direct ferry-to-rail impact"],
        list(all_ids["c02"].values()), [],
        hop_count=6, notes="Full 6-hop cascade across modes"))

    qs.append(make_query("Q16-05",
        "Why was Route 10 frequency reduced on March 8, 2033?",
        "transfer_cascade",
        ["Bus-102 was redeployed as emergency Harbor shuttle due to ferry disruption"],
        [],
        ["Planned schedule change", "Bus breakdown"],
        [all_ids["c02"]["emergency_bus"], all_ids["c02"]["route10_reduced"]], [],
        hop_count=2))

    # C03: Staff chain
    qs.append(make_query("Q16-06",
        "How did Jiro Tanaka's leave lead to Blue Line overcrowding?",
        "staff_dependency",
        ["Jiro on leave → Tane covers both divisions → delegates bus scheduling to Kira → Kira reassigns Bus-103 to Route 22 → Route 20 gaps → passengers shift to Blue Line → overcrowding"],
        [],
        ["Jiro caused overcrowding directly", "No connection"],
        list(all_ids["c03"].values()), [],
        hop_count=5))

    qs.append(make_query("Q16-07",
        "Why did Kira reassign Bus-103 to Route 22?",
        "staff_dependency",
        ["Tane delegated scheduling to Kira; Kira's previous role was Route 22 coordinator and she judged it needed better service"],
        ["Tane was stretched across two divisions during Jiro's leave"],
        ["Standard schedule optimization", "Bus-103 broke down"],
        [all_ids["c03"]["tane_covers"], all_ids["c03"]["kira_reassign"]], [],
        hop_count=2))

    # C04: Budget chain
    qs.append(make_query("Q16-08",
        "Why was Ferry-B grounded in October 2034?",
        "budget_chain",
        ["Federal funding cut → HTA budget reduction → ferry maintenance deferred → hull inspection missed → Maritime NZ grounded Ferry-B"],
        [],
        ["Engine failure", "Safety violation unrelated to budget"],
        list(all_ids["c04"].values()), [],
        hop_count=4))

    qs.append(make_query("Q16-09",
        "What was the connection between the federal funding cut and cross-island ferry service?",
        "budget_chain",
        ["15% federal cut → Ravi reduced ferry maintenance 20% → Anika deferred hull inspection → Maritime NZ grounded Ferry-B → single-ferry operation, capacity halved"],
        [],
        ["No connection", "Direct cut to service"],
        list(all_ids["c04"].values()), [],
        hop_count=5))

    # C05: Information chain
    qs.append(make_query("Q16-10",
        "What happened with the Route 24 Marina extension?",
        "information_chain",
        ["Flawed survey (self-selection bias) → inflated demand estimate (800 vs actual 280) → board approved extension → buses taken from Route 20 → Route 20 ridership dropped → survey error discovered → extension reversed but Route 20 didn't fully recover"],
        [],
        ["Extension was successful", "Survey was accurate"],
        list(all_ids["c05"].values()), [],
        hop_count=5))

    qs.append(make_query("Q16-11",
        "Why didn't Route 20 ridership recover after the Route 24 reversal?",
        "information_chain",
        ["Passengers who left during the service cuts found alternatives and didn't return — recovered only 60% of lost riders"],
        ["Net loss of 150 daily riders across network"],
        ["Full recovery", "Ridership wasn't affected"],
        [all_ids["c05"]["route20_cut"], all_ids["c05"]["reversal"]], [],
        hop_count=2))

    # C06: Equipment provenance
    qs.append(make_query("Q16-12",
        "Why was LR-03 out of service for three weeks in 2033?",
        "equipment_provenance",
        ["Original supplier PRP acquired by TransGlobal → new owner changed brake actuator specs → replacement parts didn't fit → emergency sourcing from Japan → 3-week wait"],
        [],
        ["Regular maintenance", "Brake failure"],
        list(all_ids["c06"].values()), [],
        hop_count=5))

    qs.append(make_query("Q16-13",
        "Why didn't the replacement brake actuator fit LR-03?",
        "equipment_provenance",
        ["TransGlobal changed mounting bolt pattern (M12→M10) and stroke (65→60mm) from original PRP specification"],
        ["PRP was acquired by TransGlobal in 2032"],
        ["Manufacturing defect", "Wrong part ordered"],
        [all_ids["c06"]["spec_change"], all_ids["c06"]["part_mismatch"]], [],
        hop_count=2))

    # C07: Temporal chain
    qs.append(make_query("Q16-14",
        "How did the 2030 network plan ultimately perform?",
        "temporal_chain",
        ["Airport extension 18 months late, cost $14.1M vs $12M budget. Ridership 4,400 vs 4,500 target — nearly achieved. Route 10 still 10% below pre-construction levels."],
        ["Construction disruption lasting effects were underestimated"],
        ["Plan was fully achieved", "Extension was cancelled"],
        list(all_ids["c07"].values()), [],
        hop_count=7, notes="7-year chain"))

    qs.append(make_query("Q16-15",
        "What was the impact of 2032 construction on Route 10?",
        "temporal_chain",
        ["Ridership dropped 18% during construction; by 2036 it had recovered to only 90% of pre-construction levels"],
        ["Temporary bus bridge was installed during construction"],
        ["No impact", "Full recovery"],
        [all_ids["c07"]["y2032"], all_ids["c07"]["y2034"], all_ids["c07"]["y2036"]], [],
        hop_count=3))

    # Cross-case
    qs.append(make_query("Q16-16",
        "What are the recurring patterns when HTA makes budget cuts?",
        "cross_case",
        ["Deferred maintenance leads to equipment failures (C01, C04); vehicle shortages cascade to route cancellations and complaints"],
        [],
        ["Budget cuts have no service impact"],
        [], [],
        notes="Cross-case pattern recognition"))

    # Control
    qs.append(make_query("Q16-17",
        "When did HTA launch its mobile ticketing app?",
        "control",
        ["January 2035, 15,000 downloads in first month"],
        [],
        [], [], [],
        difficulty="easy", hop_count=1))

    return qs

def main():
    out_dir = os.path.join(os.getcwd(), OUT) if len(sys.argv) < 2 else sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    all_mems = []
    all_ids = {}

    for name, gen_fn in [("c01", gen_c01), ("c02", gen_c02), ("c03", gen_c03),
                          ("c04", gen_c04), ("c05", gen_c05), ("c06", gen_c06), ("c07", gen_c07)]:
        mems, ids = gen_fn()
        all_mems.extend(mems)
        all_ids[name] = ids

    bg = gen_background()
    all_mems.extend(bg)

    queries = gen_queries(all_ids)

    # Write
    mem_path = os.path.join(out_dir, "memories.jsonl")
    with open(mem_path, 'w') as f:
        for m in all_mems:
            f.write(json.dumps(m) + "\n")

    q_path = os.path.join(out_dir, "queries.jsonl")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    files_info = []
    for fname in ["memories.jsonl", "queries.jsonl"]:
        fp = os.path.join(out_dir, fname)
        h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
        files_info.append({"path": fname, "sha256": h, "bytes": os.path.getsize(fp)})

    manifest = {
        "experiment": "exp16", "title": "Multi-hop Dependencies",
        "story_id": "hokulea_transit",
        "canonical_memory_count": len(all_mems), "query_count": len(queries),
        "files": files_info
    }
    with open(os.path.join(out_dir, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)

    sb_src = "/tmp/claude-0/-home-user-memory-testing/6ffa00f0-af4e-5ad8-9c00-025401d96b92/scratchpad/exp16/story_bible.md"
    if os.path.exists(sb_src):
        import shutil
        shutil.copy(sb_src, os.path.join(out_dir, "story_bible.md"))

    print(f"Generated {len(all_mems)} memories, {len(queries)} queries")
    print(f"Output: {out_dir}")

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
        c = q.get("category","?")
        q_cats[c] = q_cats.get(c,0)+1
    print(f"\nQuery categories:")
    for c in sorted(q_cats):
        print(f"  {c}: {q_cats[c]}")

if __name__ == "__main__":
    main()
