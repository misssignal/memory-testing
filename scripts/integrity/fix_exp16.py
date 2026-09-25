#!/usr/bin/env python3
"""First expansion for Experiment 16 — adds ~80 memories and ~30 queries."""

import json, hashlib, os, sys, uuid
from datetime import datetime, timedelta, timezone

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
        "memory_id": memory_id, "experiment": "exp16", "story_id": "hokulea_transit",
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

    # === C01 expansion: More detail on each link + parallel chain ===
    # Parts finally arrive
    ev = datetime(2032, 9, 12, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev, ev+timedelta(hours=4), ev+timedelta(hours=8), ev+timedelta(hours=12),
        "Bus-101", "returned_to_service", "brake overhaul completed September 12",
        "Bus-101 returned to service September 12, 2032 after brake parts finally arrived and were installed. Total downtime: 18 days. Anika Sharma filed report recommending maintenance budget ring-fencing to prevent recurrence.",
        src="maintenance_log", stype="operational_record", tags=["C01", "maintenance"]))

    # Route 14 restoration
    ev2 = datetime(2032, 9, 13, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev2, ev2+timedelta(hours=2), ev2+timedelta(hours=4), ev2+timedelta(hours=6),
        "Route 14", "restored", "service resumed 13 September 2032",
        "Route 14 service restored 13 September 2032 with Bus-102 returning to its original assignment. Total cancellation period: 18 days. Ridership took 6 weeks to recover to pre-cancellation levels.",
        src="operations_report", stype="operational_record", tags=["C01", "service"]))

    # Parallel chain: same budget cut → different effect
    ev3 = datetime(2032, 7, 25, tzinfo=timezone.utc)
    m1 = mid()
    new_mems.append(make_mem(m1, ev3, ev3+timedelta(hours=4), ev3+timedelta(hours=8), ev3+timedelta(hours=12),
        "Grace Okonkwo", "deferred", "West depot floor resurfacing",
        "Grace Okonkwo deferred West depot maintenance bay floor resurfacing due to Q3 budget cuts. Floor condition deteriorating — oil stains creating slip hazard. Safety inspection due November.",
        src="depot_log", stype="internal_record", tags=["C01", "budget", "safety"]))

    ev4 = datetime(2032, 11, 5, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev4, ev4+timedelta(hours=4), ev4+timedelta(hours=8), ev4+timedelta(hours=12),
        "WorkSafe", "issued", "improvement notice for West depot floor",
        "WorkSafe inspector issued improvement notice for West depot maintenance bay. Oil-stained floor surface failed slip resistance test. Grace Okonkwo given 30 days to remediate. Emergency budget allocation of $85,000 approved.",
        src="safety_notice", stype="regulatory_notice",
        derived=[m1], tags=["C01", "budget", "safety"]))

    # === C02 expansion: More cascade detail ===
    # Ferry-A repair progress
    ev5 = datetime(2033, 3, 12, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev5, ev5+timedelta(hours=4), ev5+timedelta(hours=8), ev5+timedelta(hours=12),
        "Anika Sharma", "reported", "Ferry-A engine repair status",
        "Anika Sharma reported Ferry-A engine repair status: port engine cylinder head cracked. Replacement ordered from Caterpillar Australia. ETA 15 March. Total repair time now estimated at 12 days, not 10.",
        src="maintenance_report", stype="operational_record", tags=["C02", "ferry"]))

    # Passenger impact stories
    ev6 = datetime(2033, 3, 9, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev6, ev6+timedelta(hours=2), ev6+timedelta(hours=4), ev6+timedelta(hours=6),
        "HTA customer services", "received", "46 complaints about ferry disruption Day 2",
        "46 complaints received on Day 2 of ferry disruption. Common themes: wait times doubled, bus alternatives too slow (40 min vs 25 min ferry), overcrowding on remaining services. Three passengers missed flights due to delayed cross-island journey.",
        src="complaints_register", stype="public_feedback", tags=["C02", "complaints"]))

    # Service restored
    ev7 = datetime(2033, 3, 20, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev7, ev7+timedelta(hours=2), ev7+timedelta(hours=4), ev7+timedelta(hours=6),
        "Ferry-A", "returned_to_service", "20 March 2033",
        "Ferry-A returned to service 20 March 2033 after 12-day repair. Normal two-ferry schedule restored. Post-disruption analysis: total of 340 complaints, estimated 4,500 passenger-hours of delay across the network.",
        src="operations_report", stype="operational_record", tags=["C02", "ferry"]))

    # === C03 expansion: More staff chain detail ===
    # Tane's workload
    ev8 = datetime(2033, 6, 5, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev8, ev8+timedelta(hours=2), ev8+timedelta(hours=4), ev8+timedelta(hours=6),
        "Tane Parata", "reported", "struggling with dual-division workload",
        "Tane Parata told Malia Reyes he was struggling to manage both bus and LR divisions simultaneously. LR track maintenance project consuming most of his attention. Bus operations running on autopilot with Kira handling scheduling.",
        src="management_meeting", stype="internal_record", tags=["C03", "staff"]))

    # Jiro returns
    ev9 = datetime(2033, 7, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev9, ev9+timedelta(hours=2), ev9+timedelta(hours=4), ev9+timedelta(hours=6),
        "Jiro Tanaka", "returned", "from leave 1 July 2033",
        "Jiro Tanaka returned from leave. Reviewed Kira's scheduling changes and reversed Bus-103 reassignment. Route 20 restored to two-bus operation. Blue Line overcrowding eased within a week.",
        src="management_memo", stype="internal_record", tags=["C03", "staff"]))

    # === C04 expansion ===
    # Ferry-B inspection finally done
    ev10 = datetime(2034, 11, 15, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev10, ev10+timedelta(days=3), ev10+timedelta(days=5), ev10+timedelta(days=7),
        "Ferry-B", "inspection_completed", "November 2034",
        "Ferry-B hull inspection completed 15 November 2034, six weeks after grounding. Found minor corrosion but vessel structurally sound. Maritime NZ reissued safety certificate. Total out-of-service time: 45 days.",
        src="inspection_report", stype="regulatory_record", tags=["C04", "ferry"]))

    # Tourism impact
    ev11 = datetime(2034, 10, 15, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev11, ev11+timedelta(hours=4), ev11+timedelta(hours=8), ev11+timedelta(hours=12),
        "Tourism Board", "complained", "ferry disruption harming peak season",
        "Island Tourism Board wrote to HTA complaining that single-ferry operation during October peak season was harming visitor experience. Tour operators reporting 20% cancellation rate for cross-island day trips.",
        src="correspondence", stype="external_feedback", tags=["C04", "complaints"]))

    # === C05 expansion ===
    # Survey methodology detail
    ev12 = datetime(2033, 9, 15, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev12, ev12+timedelta(hours=4), ev12+timedelta(hours=8), ev12+timedelta(hours=12),
        "HTA Planning", "distributed", "Route 24 survey via Marina District community page",
        "Route 24 ridership survey distributed primarily through Marina District community Facebook page and local newspaper. Response rate: 1,200 from Marina area vs 180 from rest of network. Self-selection bias not identified at survey stage.",
        src="survey_records", stype="methodology_detail", tags=["C05", "survey"]))

    # Route 20 ridership tracking
    ev13 = datetime(2034, 8, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev13, ev13+timedelta(hours=4), ev13+timedelta(hours=8), ev13+timedelta(hours=12),
        "Malia Reyes", "tracked", "Route 20 ridership recovery",
        "Malia Reyes's quarterly tracking: Route 20 ridership 6 months after restoration: 75% of original (up from 75% at restoration). Competitors (ride-share, cycling) have captured ~150 former daily riders permanently.",
        src="ridership_data", stype="data_analysis", tags=["C05", "ridership"]))

    # === C06 expansion ===
    # Anika investigates compatibility
    ev14 = datetime(2033, 8, 11, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev14, ev14+timedelta(hours=4), ev14+timedelta(hours=8), ev14+timedelta(hours=12),
        "Anika Sharma", "investigated", "brake actuator compatibility issue",
        "Anika Sharma's investigation: TransGlobal Components confirmed BKA-400 spec change was intentional cost reduction. They offered a mounting adapter plate for $800/unit but warned it would add 15mm to actuator depth, potentially fouling the bogie frame. Anika rejected adapter solution.",
        src="procurement_records", stype="internal_record", tags=["C06", "equipment"]))

    # Long-term solution
    ev15 = datetime(2033, 10, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev15, ev15+timedelta(days=3), ev15+timedelta(days=5), ev15+timedelta(days=7),
        "Anika Sharma", "contracted", "custom brake actuator manufacture",
        "Anika Sharma contracted local engineering firm KiwiRail Solutions to reverse-engineer and manufacture BKA-400 compatible actuators. Cost: $3,200/unit vs $1,800 original PRP price. Lead time: 8 weeks for first batch of 20 units. Ensures LR-03 future supply independence.",
        src="procurement_contract", stype="financial_record", tags=["C06", "procurement"]))

    # === C07 expansion ===
    # More detail on each year's decisions
    ev16 = datetime(2030, 9, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev16, ev16+timedelta(hours=4), ev16+timedelta(hours=8), ev16+timedelta(hours=12),
        "Ravi Mehta", "allocated", "Airport extension budget $12M",
        "Ravi Mehta's budget allocation for Airport extension: $12M over 3 years (2031-2033). Contingency: 10%. Major items: track and signaling $7.2M, station construction $3.1M, rolling stock modifications $1.7M.",
        mtype="procedural", src="budget_document", stype="financial_record", tags=["C07", "planning", "budget"]))

    ev17 = datetime(2032, 3, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev17, ev17+timedelta(days=3), ev17+timedelta(days=5), ev17+timedelta(days=7),
        "Jiro Tanaka", "reported", "construction delay on Airport extension",
        "Jiro Tanaka reported 6-month delay on Airport extension due to unexpected volcanic rock during excavation. Additional cost: $2.1M for specialized drilling. Opening date pushed from September 2032 to March 2033.",
        src="construction_report", stype="project_report", tags=["C07", "construction"]))

    # Airport shuttle competition detail
    ev18 = datetime(2033, 6, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev18, ev18+timedelta(hours=4), ev18+timedelta(hours=8), ev18+timedelta(hours=12),
        "Malia Reyes", "analyzed", "Airport shuttle competition",
        "Malia Reyes analyzed competition: three private shuttle operators captured 40% of Airport-Downtown market. Key advantages: door-to-door service, luggage handling. HTA Green Line advantage: lower cost ($4 vs $15-25 shuttle), frequent service, no traffic delays.",
        src="market_analysis", stype="data_analysis", tags=["C07", "competition"]))

    # === More background ===
    bg = [
        (datetime(2030, 3, 15, tzinfo=timezone.utc), "HTA", "conducted", "annual safety audit",
         "Annual safety audit completed across all divisions. 98.5% compliance. Two minor findings at East depot — fire extinguisher placement and first aid kit expiry."),
        (datetime(2030, 6, 20, tzinfo=timezone.utc), "Kira Nakamura", "designed", "summer timetable",
         "Kira Nakamura designed summer timetable with extended evening services on Routes 10 and 20 for the festival season. Additional 12% operating hours."),
        (datetime(2030, 9, 10, tzinfo=timezone.utc), "HTA", "participated", "regional transport planning workshop",
         "HTA participated in regional transport planning workshop. Presented 10-year growth projections: ridership expected to reach 18M trips by 2040."),
        (datetime(2031, 2, 5, tzinfo=timezone.utc), "Anika Sharma", "completed", "annual fleet inspection",
         "Anika Sharma completed annual fleet inspection. All buses and ferries certified roadworthy/seaworthy. LR units passed bi-annual rail safety audit."),
        (datetime(2031, 5, 20, tzinfo=timezone.utc), "HTA", "launched", "accessibility upgrade programme",
         "HTA launched 3-year accessibility upgrade programme. All bus stops to get tactile paving, audio announcements on all vehicles, wheelchair ramps on all ferries."),
        (datetime(2031, 8, 15, tzinfo=timezone.utc), "Sione Vunipola", "reported", "East depot capacity reaching limit",
         "Sione Vunipola reported East depot reaching capacity. Recommended expansion or satellite depot for Route 14 vehicles. Current capacity: 6 buses, current fleet: 4 assigned."),
        (datetime(2031, 11, 1, tzinfo=timezone.utc), "HTA Board", "approved", "fare increase for 2032",
         "Board approved 5% fare increase effective January 2032. First increase in 3 years. Expected to generate additional $1.1M revenue."),
        (datetime(2032, 1, 15, tzinfo=timezone.utc), "Malia Reyes", "reported", "December ridership records",
         "December 2031 set ridership record: 1.18 million trips in single month. Festival season and new contactless payment contributed to growth."),
        (datetime(2032, 3, 20, tzinfo=timezone.utc), "Leilani Kim", "ordered", "new life rafts",
         "Leilani Kim ordered replacement life rafts for both ferries. Maritime NZ requirement: annual inspection and 3-year replacement cycle. Cost: $28,000 per vessel."),
        (datetime(2032, 10, 5, tzinfo=timezone.utc), "Ravi Mehta", "prepared", "Q4 budget revision",
         "Ravi Mehta prepared Q4 2032 budget revision following Q3 cuts impact analysis. Recommended restoring maintenance procurement to pre-cut levels. Board approved partial restoration: 90% of original."),
        (datetime(2033, 1, 10, tzinfo=timezone.utc), "Tane Parata", "planned", "bus replacement programme",
         "Tane Parata submitted 3-year bus replacement programme. Four oldest buses (2024-2026 vintage) to be replaced with electric vehicles by 2036."),
        (datetime(2033, 4, 5, tzinfo=timezone.utc), "HTA", "signed", "power purchase agreement for EV charging",
         "HTA signed 10-year power purchase agreement with Pacific Solar for EV charging at both depots. Fixed rate: 12c/kWh. Saves 30% vs grid electricity."),
        (datetime(2033, 8, 20, tzinfo=timezone.utc), "Keanu Lani", "met_with", "mayor about transit funding",
         "Keanu Lani met with Mayor Chen to discuss long-term transit funding. Proposed dedicated transit levy. Mayor supportive but cautious about political timing."),
        (datetime(2034, 2, 15, tzinfo=timezone.utc), "Kira Nakamura", "implemented", "dynamic scheduling pilot",
         "Kira Nakamura piloted dynamic scheduling on Route 10. Real-time passenger counting adjusts dispatch frequency. 15% improvement in load factor evenness."),
        (datetime(2034, 5, 1, tzinfo=timezone.utc), "HTA", "hosted", "school transit education programme",
         "HTA hosted Transit Education Day for 500 primary school students. Tours of bus depot, ferry terminal, and light rail operations centre."),
        (datetime(2034, 8, 10, tzinfo=timezone.utc), "Grace Okonkwo", "completed", "West depot EV infrastructure",
         "Grace Okonkwo oversaw installation of 6 DC fast chargers at West depot. Capacity: charge 2 electric buses simultaneously. Cost: $340,000."),
        (datetime(2034, 11, 20, tzinfo=timezone.utc), "Jiro Tanaka", "completed", "Green Line track renewal",
         "Jiro Tanaka completed downtown section track renewal for Green Line. 800m of rail replaced over two weekends. Bus replacement service provided during closures."),
        (datetime(2035, 3, 15, tzinfo=timezone.utc), "HTA Board", "approved", "Blue Line extension study",
         "Board approved $1.2M feasibility study for Blue Line extension to Marina District. Funded from Ravi's federal infrastructure grant."),
        (datetime(2035, 6, 1, tzinfo=timezone.utc), "Malia Reyes", "launched", "customer feedback app",
         "Malia Reyes launched customer feedback feature in mobile app. Real-time issue reporting with photo upload. First month: 280 reports, average response time: 4.2 hours."),
        (datetime(2035, 9, 20, tzinfo=timezone.utc), "Sione Vunipola", "mentored", "Pacific Islands transit managers",
         "Sione Vunipola hosted a week-long mentoring programme for four transit managers from Pacific Island nations. Shared HTA operational practices and maintenance systems."),
        (datetime(2036, 1, 5, tzinfo=timezone.utc), "HTA", "celebrated", "15 million passenger milestone",
         "HTA celebrated reaching 15 million cumulative passenger trips since inception. Ceremony at Central Station with Keanu Lani, Mayor Chen, and transit staff."),
        (datetime(2036, 3, 15, tzinfo=timezone.utc), "Tane Parata", "received", "first fully electric bus fleet",
         "Tane Parata took delivery of final two electric buses, completing the transition. All eight buses now fully electric. Diesel fleet retired."),
        (datetime(2036, 6, 20, tzinfo=timezone.utc), "Leilani Kim", "commenced", "Ferry-C construction",
         "Construction began on Ferry-C, a new high-speed electric ferry. Capacity: 300 passengers. Expected delivery: 2038. Cost: $8.5M."),
    ]

    for dt, subj, pred, obj_, text in bg:
        new_mems.append(make_mem(mid(), dt, dt+timedelta(hours=2), dt+timedelta(hours=4), dt+timedelta(hours=6),
            subj, pred, obj_, text, src=pred, stype="internal_record", tags=["background"]))

    # === New queries ===
    new_qs.append(make_query("Q16-r1-01",
        "How long was Bus-101 out of service and what was the total impact?",
        "causal_chain", ["18 days downtime, Route 14 cancelled for same period, 142 complaints, media coverage"],
        ["Ridership took 6 weeks to recover after restoration"], ["Quick repair"],
        [], [], hop_count=3))

    new_qs.append(make_query("Q16-r1-02",
        "What other consequences came from the Q3 2032 budget cut besides Route 14 cancellation?",
        "causal_chain", ["West depot floor resurfacing deferred → WorkSafe improvement notice → $85,000 emergency spend"],
        ["Budget cut had multiple parallel consequences"], ["Budget cut only affected buses"],
        [], [], hop_count=3))

    new_qs.append(make_query("Q16-r1-03",
        "How long was Ferry-A actually out of service and what delayed the repair?",
        "transfer_cascade", ["12 days (not 10 initially estimated). Port engine cylinder head cracked, replacement from Caterpillar Australia."],
        [], ["10-day repair as estimated"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-04",
        "What was the total passenger impact of the March 2033 ferry disruption?",
        "transfer_cascade", ["340 complaints, estimated 4,500 passenger-hours delay across network, 3 missed flights"],
        ["Ferry-A returned March 20"], ["Minor impact"],
        [], [], hop_count=3))

    new_qs.append(make_query("Q16-r1-05",
        "What happened when Jiro returned from leave?",
        "staff_dependency", ["Reversed Kira's Bus-103 reassignment, restored Route 20 to two-bus operation, Blue Line overcrowding eased within a week"],
        [], ["Nothing changed"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-06",
        "Why was Tane Parata struggling during June 2033?",
        "staff_dependency", ["Managing both bus and LR divisions simultaneously while Jiro was on leave, with LR track project consuming most attention"],
        ["Delegated bus scheduling to Kira"], ["Normal workload"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-07",
        "How long was Ferry-B grounded and what was found during inspection?",
        "budget_chain", ["45 days (October 1 – November 15). Only minor corrosion found — vessel was structurally sound."],
        ["Grounding was unnecessary in hindsight — only delayed by budget constraint"], ["Major structural issues"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-08",
        "What was the tourism impact of Ferry-B grounding?",
        "budget_chain", ["Tourism Board complained, tour operators reported 20% cancellation rate for cross-island day trips"],
        ["October is peak tourism season"], ["No tourism impact"],
        [], [], hop_count=3))

    new_qs.append(make_query("Q16-r1-09",
        "What was wrong with the Route 24 ridership survey methodology?",
        "information_chain", ["Self-selection bias: distributed via Marina District community Facebook page, respondents disproportionately wanted the service"],
        ["1,200 responses from Marina vs 180 from rest of network"], ["Sound methodology"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-10",
        "What did Anika do about the long-term brake actuator supply for LR-03?",
        "equipment_provenance", ["Contracted KiwiRail Solutions to reverse-engineer and manufacture compatible actuators at $3,200/unit"],
        ["Ensures supply independence from TransGlobal"], ["Continued using TransGlobal parts"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-11",
        "Why did the Airport extension cost $14.1M instead of $12M?",
        "temporal_chain", ["$2.1M overrun from unexpected volcanic rock during excavation requiring specialized drilling"],
        ["Reported by Jiro Tanaka in March 2032"], ["Within budget"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-12",
        "Why did Airport shuttle buses capture 40% market share?",
        "temporal_chain", ["Door-to-door service and luggage handling advantages over Green Line"],
        ["Green Line advantages: lower cost ($4 vs $15-25) and no traffic delays"], ["No competition exists"],
        [], [], hop_count=2))

    new_qs.append(make_query("Q16-r1-13",
        "Trace the full chain from the federal funding cut to cross-island tourists being affected.",
        "cross_case", ["Federal 15% cut → Ravi reduced ferry maintenance 20% → hull inspection deferred → Maritime NZ grounded Ferry-B → single ferry → capacity halved → tour operators 20% cancellations"],
        [], ["No connection between federal funding and tourism"],
        [], [], hop_count=6))

    new_qs.append(make_query("Q16-r1-14",
        "What recurring pattern does HTA have with deferred maintenance?",
        "cross_case", ["Budget pressure → maintenance deferral → equipment failure or regulatory action → worse cost than original maintenance"],
        ["Happened with Bus-101 brakes (C01), Ferry-B hull (C04), West depot floor (C01)"], ["No pattern"],
        [], [], hop_count=3))

    new_qs.append(make_query("Q16-r1-15",
        "When did HTA complete its bus fleet electrification?",
        "control", ["March 2036, when Tane Parata received final two electric buses"], [], [],
        [], [], difficulty="easy", hop_count=1))

    new_qs.append(make_query("Q16-r1-16",
        "What fare increase did HTA approve for 2032?",
        "control", ["5% increase, first in 3 years, expected $1.1M additional revenue"], [], [],
        [], [], difficulty="easy", hop_count=1))

    new_qs.append(make_query("Q16-r1-17",
        "What was the December 2031 ridership record?",
        "control", ["1.18 million trips in a single month"], ["Festival season and contactless payment contributed"], [],
        [], [], difficulty="easy", hop_count=1))

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
