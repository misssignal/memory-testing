#!/usr/bin/env python3
"""Exp 16 round-2 expansion — target ≥ 170 memories, ≥ 55 queries."""

import json, hashlib, os, sys
from datetime import datetime

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
    EXP = "exp16"
    STORY = "hokuleʻa_transit_authority"

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_mems = []
    new_qs = []

    def M(case, subj, pred, obj, text, etype, truth, tags_extra=None,
          dt="2032-06-01", derived=None, supersedes=None, contradicts=None,
          confidence=0.9, source_id="hta-ops", source_type="operational_record",
          belief_holder="HTA", scope="internal"):
        nonlocal mid_counter
        t_ev = f"{dt}T09:00:00Z"
        t_ob = f"{dt}T12:00:00Z"
        t_au = f"{dt}T15:00:00Z"
        t_in = f"{dt}T18:00:00Z"
        import hashlib as _hl
        _hash = _hl.md5(f"exp16-r2-{mid_counter}".encode()).hexdigest()[:8]
        m = {
            "memory_id": f"E16-{_hash}",
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
          relevant, distractors, hop_count, difficulty="hard",
          uncertainty=False, conflict=False, disambig=False,
          scope=False, abstain=False, notes=""):
        nonlocal qid_counter
        q = {
            "query_id": f"Q16-{qid_counter:02d}",
            "query": question, "category": category,
            "expected_claims": expected,
            "acceptable_claims": acceptable,
            "forbidden_claims": forbidden,
            "relevant_memory_ids": relevant,
            "distractor_memory_ids": distractors,
            "hop_count": hop_count, "difficulty": difficulty,
            "must_surface_uncertainty": uncertainty,
            "must_surface_conflict": conflict,
            "must_disambiguate": disambig,
            "must_preserve_scope": scope,
            "should_abstain": abstain,
            "notes": notes
        }
        qid_counter += 1
        new_qs.append(q)
        return q["query_id"]

    # --- C01 deeper chain details ---
    c01a = M("C01", "HTA_Board", "approved_budget_cut", "Q3_2032_operations",
             "The HTA Board voted 5-2 to cut the Q3 2032 operations budget by 12%, specifically targeting discretionary maintenance spending.",
             "event", "ground_truth", dt="2032-05-15", source_id="board-minutes",
             source_type="meeting_minutes", confidence=0.95)
    c01b = M("C01", "procurement_office", "delayed_order", "Bus-101_brake_pads",
             "Due to the Q3 budget cut, the procurement office deferred the brake pad order for Bus-101 from June to September 2032.",
             "event", "ground_truth", dt="2032-06-20", derived=[c01a],
             source_id="procurement-log")
    c01c = M("C01", "Anika_Sharma", "extended_maintenance_window", "Bus-101",
             "Maintenance Director Anika Sharma extended Bus-101's shop time by 6 weeks due to the deferred brake pad delivery, keeping it out of service until late October.",
             "event", "ground_truth", dt="2032-07-10", derived=[c01b],
             source_id="maintenance-log")
    c01d = M("C01", "Sione_Vunipola", "reallocated_vehicle", "Bus-102_to_Route_12",
             "East Depot Manager Sione Vunipola moved Bus-102 from Route 14 to Route 12 to cover Bus-101's absence, leaving Route 14 without dedicated rolling stock.",
             "event", "ground_truth", dt="2032-07-15", derived=[c01c])
    c01e = M("C01", "Route_14", "experienced_cancellations", "3_weeks_August_2032",
             "Route 14 suffered 47 service cancellations over three weeks in August 2032 due to having no dedicated bus after Bus-102's reallocation.",
             "event", "ground_truth", dt="2032-08-20", derived=[c01d],
             source_id="service-report")
    c01f = M("C01", "Island_Herald", "published_investigation", "Route_14_failures",
             "The Island Herald published a front-page investigation titled 'Stranded Commuters' documenting the Route 14 cancellations and tracing them to the budget cut.",
             "event", "ground_truth", dt="2032-09-05", derived=[c01e],
             source_id="island-herald", source_type="media_report")
    c01g = M("C01", "HTA_Board", "reversed_budget_cut", "Q4_2032_emergency_allocation",
             "Under media pressure, the HTA Board approved an emergency Q4 allocation restoring maintenance funding and expediting the Bus-101 parts order.",
             "event", "ground_truth", dt="2032-09-20", derived=[c01f],
             source_id="board-minutes", source_type="meeting_minutes")

    # --- C02 deeper chain details ---
    c02a = M("C02", "Ferry-A", "suffered_engine_failure", "March_3_2033",
             "Ferry-A's port engine seized during the 7:15 AM crossing on March 3, 2033, forcing an emergency return to Harbor terminal.",
             "event", "ground_truth", dt="2033-03-03", source_id="incident-report",
             confidence=0.95)
    c02b = M("C02", "Harbor_operations", "doubled_Ferry-B_schedule", "March_2033",
             "With Ferry-A grounded, Harbor operations doubled Ferry-B's daily crossings from 8 to 16, cutting turnaround time in half.",
             "event", "ground_truth", dt="2033-03-04", derived=[c02a])
    c02c = M("C02", "Ferry-B", "ran_45_minutes_late", "March_8_2033",
             "By March 8, accumulated fatigue on Ferry-B's engines caused a 45-minute delay on the afternoon crossing, cascading into missed bus connections at Harbor.",
             "event", "ground_truth", dt="2033-03-08", derived=[c02b])
    c02d = M("C02", "Route_12_passengers", "stranded_at_Harbor", "42_passengers_March_8",
             "42 Route 12 passengers missed their connecting bus at Harbor terminal on March 8 because the ferry arrived 45 minutes late.",
             "event", "ground_truth", dt="2033-03-08", derived=[c02c])
    c02e = M("C02", "Sione_Vunipola", "dispatched_emergency_bus", "Bus-102_to_Harbor",
             "Sione Vunipola dispatched Bus-102 as an emergency shuttle from East Depot to Harbor, pulling it off Route 10's evening service.",
             "event", "ground_truth", dt="2033-03-08", derived=[c02d])
    c02f = M("C02", "Route_10", "reduced_frequency", "evening_March_8_2033",
             "Route 10 evening frequency dropped from 15-minute to 30-minute headways after Bus-102 was diverted to Harbor emergency duty.",
             "event", "ground_truth", dt="2033-03-08", derived=[c02e])
    c02g = M("C02", "Green_Line", "experienced_overcrowding", "March_8-15_2033",
             "Green Line ridership spiked 40% as Route 10 passengers switched to light rail, causing standing-room-only conditions for a week.",
             "event", "ground_truth", dt="2033-03-10", derived=[c02f],
             source_id="ridership-data")

    # --- C03 deeper chain ---
    c03a = M("C03", "Jiro_Tanaka", "took_medical_leave", "4_weeks_Jan_2034",
             "Light Rail Division Chief Jiro Tanaka began a four-week medical leave on January 8, 2034.",
             "event", "ground_truth", dt="2034-01-08", source_id="hr-record",
             source_type="hr_record")
    c03b = M("C03", "Keanu_Lani", "assigned_dual_role", "Tane_Parata_covers_LR",
             "GM Keanu Lani assigned Bus Division Chief Tane Parata to also oversee Light Rail operations during Jiro's absence.",
             "event", "ground_truth", dt="2034-01-09", derived=[c03a])
    c03c = M("C03", "Tane_Parata", "delegated_bus_scheduling", "Kira_Nakamura",
             "Overwhelmed by dual responsibilities, Tane delegated day-to-day bus scheduling decisions to Scheduling Coordinator Kira Nakamura.",
             "event", "ground_truth", dt="2034-01-15", derived=[c03b])
    c03d = M("C03", "Kira_Nakamura", "reassigned_Bus-103", "Route_22_from_Route_20",
             "Kira moved Bus-103 from Route 20 to Route 22 to improve frequency on the West-Harbor corridor she was most familiar with.",
             "event", "ground_truth", dt="2034-01-20", derived=[c03c])
    c03e = M("C03", "Route_20", "suffered_service_gaps", "Jan-Feb_2034",
             "Route 20 experienced 30-minute gaps during peak hours in late January and February after losing Bus-103, with Bus-104 alone insufficient.",
             "event", "ground_truth", dt="2034-01-25", derived=[c03d])
    c03f = M("C03", "Blue_Line", "received_overflow_passengers", "Feb_2034",
             "Blue Line ridership increased 25% in February 2034 as Route 20 commuters shifted to light rail at Central Station.",
             "event", "ground_truth", dt="2034-02-05", derived=[c03e],
             source_id="ridership-data")

    # --- C04 deeper chain ---
    c04a = M("C04", "federal_government", "cut_transit_funding", "15%_reduction_FY2034",
             "The federal government announced a 15% reduction in transit operating grants for FY2034, effective July 1.",
             "event", "ground_truth", dt="2033-12-15", source_id="federal-gazette",
             source_type="government_record", scope="public")
    c04b = M("C04", "Ravi_Mehta", "restructured_allocations", "ferry_maintenance_deferred",
             "Budget Director Ravi Mehta deferred Ferry-B's scheduled hull inspection from Q2 to Q4 2034 to balance the reduced budget.",
             "event", "ground_truth", dt="2034-01-20", derived=[c04a])
    c04c = M("C04", "maritime_authority", "grounded_Ferry-B", "overdue_hull_inspection",
             "The Maritime Safety Authority grounded Ferry-B on September 15, 2034 after its hull inspection certificate expired without renewal.",
             "event", "ground_truth", dt="2034-09-15", derived=[c04b],
             source_id="maritime-notice", source_type="regulatory_record")
    c04d = M("C04", "HTA", "operated_single_ferry", "Oct-Dec_2034",
             "With both ferries now out of service at different times (Ferry-A repaired but Ferry-B grounded), cross-island capacity dropped to single-ferry operation.",
             "event", "ground_truth", dt="2034-10-01", derived=[c04c])
    c04e = M("C04", "cross_island_service", "halved_frequency", "Q4_2034",
             "Cross-island ferry frequency dropped from 16 to 8 daily crossings during Q4 2034, stranding West island commuters during peak hours.",
             "event", "ground_truth", dt="2034-10-15", derived=[c04d],
             source_id="service-report")

    # --- C05 deeper chain ---
    c05a = M("C05", "consultancy_firm", "used_flawed_methodology", "ridership_survey_2033",
             "The external consultancy counted boarding taps but not alighting, double-counting transfer passengers in their 2033 ridership survey.",
             "event", "ground_truth", dt="2033-06-01", source_id="audit-report",
             source_type="audit_report", confidence=0.95)
    c05b = M("C05", "ridership_survey", "inflated_Route_24_patronage", "35%_overestimate",
             "The flawed survey inflated Route 24's apparent patronage by 35%, making it appear to be the highest-demand unserved corridor.",
             "event", "ground_truth", dt="2033-07-15", derived=[c05a])
    c05c = M("C05", "HTA_Board", "approved_Route_24_expansion", "3_buses_allocated",
             "Based on the inflated ridership data, the board approved a Route 24 expansion, allocating Bus-103 and Bus-104 plus a leased bus.",
             "event", "ground_truth", dt="2033-09-01", derived=[c05b],
             source_id="board-minutes", source_type="meeting_minutes")
    c05d = M("C05", "Route_20", "lost_both_buses", "Oct_2033",
             "Route 20 lost both Bus-103 and Bus-104 to the Route 24 expansion, reducing service to a single leased backup vehicle.",
             "event", "ground_truth", dt="2033-10-01", derived=[c05c])
    c05e = M("C05", "Route_20_ridership", "dropped_40%", "Q4_2033",
             "Route 20 ridership fell 40% in Q4 2033 as commuters abandoned the unreliable service for private transport or remote work.",
             "event", "ground_truth", dt="2033-12-15", derived=[c05d],
             source_id="ridership-data")
    c05f = M("C05", "internal_audit", "discovered_survey_error", "January_2034",
             "An internal audit in January 2034 discovered the double-counting error in the 2033 ridership survey methodology.",
             "event", "ground_truth", dt="2034-01-15", derived=[c05e, c05a],
             source_id="audit-report", source_type="audit_report")
    c05g = M("C05", "HTA_Board", "reversed_Route_24_expansion", "March_2034",
             "The board reversed the Route 24 expansion in March 2034, but Route 20's ridership remained 25% below its pre-cut baseline through mid-2035.",
             "event", "ground_truth", dt="2034-03-01", derived=[c05f],
             source_id="board-minutes", source_type="meeting_minutes")

    # --- C06 deeper chain ---
    c06a = M("C06", "supplier_X", "manufactured_LR-03_brake_actuator", "original_spec_BA-400",
             "Supplier X manufactured LR-03's brake actuator to specification BA-400, installed during the 2031 light rail procurement.",
             "event", "ground_truth", dt="2031-03-01", source_id="procurement-log")
    c06b = M("C06", "company_Y", "acquired_supplier_X", "July_2032",
             "Company Y acquired Supplier X in July 2032 and began consolidating product lines under new specifications.",
             "event", "ground_truth", dt="2032-07-01", derived=[c06a],
             source_id="trade-publication", source_type="media_report")
    c06c = M("C06", "company_Y", "changed_brake_actuator_spec", "BA-400_to_BA-450",
             "Company Y discontinued the BA-400 specification and replaced it with BA-450, which has different mounting dimensions.",
             "event", "ground_truth", dt="2032-11-01", derived=[c06b])
    c06d = M("C06", "maintenance_team", "received_wrong_part", "BA-450_for_LR-03",
             "When LR-03 needed a brake actuator replacement in February 2033, the maintenance team received a BA-450 that wouldn't fit the BA-400 mounting points.",
             "event", "ground_truth", dt="2033-02-15", derived=[c06c])
    c06e = M("C06", "Anika_Sharma", "initiated_emergency_sourcing", "BA-400_from_secondary_supplier",
             "Maintenance Director Anika Sharma sourced a BA-400-compatible actuator from a secondary supplier in Japan, with 3-week lead time.",
             "event", "ground_truth", dt="2033-02-20", derived=[c06d])
    c06f = M("C06", "LR-03", "out_of_service", "3_weeks_Feb-Mar_2033",
             "LR-03 remained out of service for 3 weeks while awaiting the emergency-sourced brake actuator, leaving the Blue Line on single-car operation.",
             "event", "ground_truth", dt="2033-03-10", derived=[c06e])

    # --- C07 deeper chain ---
    c07a = M("C07", "HTA", "published_2030_route_plan", "5_year_network_expansion",
             "HTA published its 2030 Five-Year Network Expansion Plan, proposing the Green Line extension to the airport by 2035.",
             "event", "ground_truth", dt="2030-03-01", source_id="planning-doc",
             source_type="planning_document", scope="public")
    c07b = M("C07", "HTA", "invested_in_Central_Station", "2031_infrastructure_upgrade",
             "Based on the 2030 plan, HTA invested $45M in upgrading Central Station as the hub for the expanded network.",
             "event", "ground_truth", dt="2031-06-01", derived=[c07a],
             source_id="capital-budget")
    c07c = M("C07", "Central_Station_construction", "disrupted_Green_Line", "2032_6_month_partial_closure",
             "The Central Station upgrade required a 6-month partial closure of the Green Line in 2032, reducing capacity by 40%.",
             "event", "ground_truth", dt="2032-01-15", derived=[c07b])
    c07d = M("C07", "new_Midtown_station", "opened", "January_2033",
             "The new Midtown interchange station opened in January 2033, connecting the Green and Blue Lines with a 2-minute transfer.",
             "event", "ground_truth", dt="2033-01-15", derived=[c07c])
    c07e = M("C07", "ridership_patterns", "shifted", "2034_Midtown_hub_effect",
             "By 2034, Midtown station had become the busiest interchange, with 60% of Green Line passengers transferring rather than riding end-to-end.",
             "event", "ground_truth", dt="2034-06-01", derived=[c07d],
             source_id="ridership-data")
    c07f = M("C07", "Kira_Nakamura", "revised_schedule", "2035_frequency_rebalancing",
             "Kira Nakamura led the 2035 schedule revision, shifting Green Line frequency from end-to-end runs to Midtown-focused shuttles based on the new ridership patterns.",
             "event", "ground_truth", dt="2035-03-01", derived=[c07e])
    c07g = M("C07", "performance_review", "traced_all_decisions", "2036_network_audit",
             "The 2036 network performance review traced the evolution from the 2030 plan through each year's cascading decisions, noting the Midtown hub was an emergent outcome not in the original design.",
             "event", "ground_truth", dt="2036-06-01", derived=[c07f, c07a],
             source_id="audit-report", source_type="audit_report")

    # --- Background memories ---
    bg = [
        ("HTA", "operates", "9_vehicle_fleet", "The Hōkūleʻa Transit Authority operates a fleet of 4 buses, 2 ferries, and 3 light rail cars serving the island chain.", "2030-01-15"),
        ("East_Depot", "houses", "Bus-101_Bus-102", "East Depot, managed by Sione Vunipola, houses Bus-101 and Bus-102 serving the eastern routes.", "2030-02-01"),
        ("West_Depot", "houses", "Bus-103_Bus-104", "West Depot, managed by Grace Okonkwo, houses Bus-103 and Bus-104 serving the western routes.", "2030-02-01"),
        ("Harbor_terminal", "serves_as", "ferry_bus_interchange", "Harbor terminal is the critical interchange point where ferry passengers connect to Route 12 and Route 22 bus services.", "2030-03-01"),
        ("Green_Line", "runs", "Central_to_Airport_corridor", "The Green Line light rail runs from Central Station through Midtown to the planned airport extension corridor.", "2030-04-01"),
        ("Blue_Line", "runs", "Central_to_University_corridor", "The Blue Line light rail runs from Central Station to University, with a transfer connection to Route 20.", "2030-04-01"),
        ("Malia_Reyes", "oversees", "daily_operations", "Operations Director Malia Reyes coordinates between the bus, ferry, and light rail divisions for daily service delivery.", "2030-05-01"),
        ("HTA", "carries", "85000_daily_riders", "HTA's combined network carries approximately 85,000 daily riders across all modes during peak season.", "2031-09-01"),
        ("Route_10", "connects", "East_Downtown_Central", "Route 10 is the primary east-side bus route connecting East residential areas to Downtown and Central Station.", "2030-03-15"),
        ("Route_12", "connects", "East_Harbor", "Route 12 connects East residential areas to Harbor terminal, serving as the primary bus-ferry connection for eastern commuters.", "2030-03-15"),
        ("Route_20", "connects", "West_Downtown_Central", "Route 20 is the primary west-side bus route connecting West residential areas to Downtown and Central Station.", "2030-03-15"),
        ("Route_22", "connects", "West_Harbor", "Route 22 connects West residential areas to Harbor terminal, serving the western bus-ferry interchange.", "2030-03-15"),
        ("transfer_at_Central", "enables", "bus_rail_connection", "Central Station is the primary bus-to-rail transfer point, where Routes 10 and 20 connect to the Green and Blue Lines respectively.", "2030-06-01"),
        ("HTA_Board", "meets", "monthly", "The HTA Board meets monthly to review operations, approve budgets, and make strategic decisions about network expansion.", "2030-01-01"),
        ("LR-01_LR-02", "serve", "Green_Line", "Light rail cars LR-01 and LR-02 are dedicated to Green Line service, running 18-hour daily schedules.", "2030-04-15"),
        ("LR-03", "serves", "Blue_Line", "Light rail car LR-03 is the sole vehicle on the Blue Line, making it a single point of failure for University corridor service.", "2030-04-15"),
        ("Ferry-A_Ferry-B", "provide", "cross_island_service", "Ferries A and B alternate on the cross-island route, each making 8 daily crossings with 30-minute turnarounds.", "2030-05-15"),
        ("Keanu_Lani", "leads", "HTA_as_GM", "General Manager Keanu Lani has led HTA since its founding, balancing political pressure with operational realities.", "2030-01-01"),
    ]
    for subj, pred, obj, text, dt in bg:
        M("background", subj, pred, obj, text,
          "fact", "ground_truth", dt=dt,
          source_id="hta-reference", source_type="reference_document",
          scope="public", confidence=0.95)

    # --- Queries ---
    # C01 chain queries
    Q("What was the root cause of Route 14's service cancellations in August 2032?",
      "causal_chain", ["The HTA Board's Q3 2032 budget cut led to deferred brake pad procurement for Bus-101, extending its maintenance, which caused Bus-102 to be reallocated from Route 14 to Route 12, leaving Route 14 without a dedicated bus"],
      ["Budget cuts delayed parts for Bus-101"], ["Ferry-A failure caused Route 14 issues"],
      [c01a, c01b, c01c, c01d, c01e], [c02a], hop_count=4,
      notes="Must trace budget cut → parts delay → extended maintenance → vehicle reallocation → cancellations")

    Q("How did the Island Herald investigation connect to the HTA Board's emergency allocation?",
      "causal_chain", ["The Herald's front-page investigation of Route 14 cancellations created media pressure that led the Board to approve an emergency Q4 allocation restoring maintenance funding"],
      ["Media coverage pressured the board"], ["The Herald caused the budget cut"],
      [c01e, c01f, c01g], [], hop_count=2)

    Q("Trace the complete chain from the Q3 2032 budget cut to the Board's reversal.",
      "full_chain_traversal", ["Budget cut → deferred brake pads → extended Bus-101 maintenance → Bus-102 reallocation → Route 14 cancellations → Herald investigation → Board emergency allocation"],
      ["5-hop chain from budget to media to reversal"], ["The budget cut was reversed immediately"],
      [c01a, c01b, c01c, c01d, c01e, c01f, c01g], [], hop_count=6)

    # C02 chain queries
    Q("How did Ferry-A's engine failure on March 3 lead to Green Line overcrowding?",
      "cascade_analysis", ["Ferry-A failure → doubled Ferry-B schedule → Ferry-B delays → missed connections at Harbor → emergency bus dispatched → Route 10 frequency reduced → Green Line overcrowding"],
      ["Ferry failure cascaded through bus and rail networks"], ["Green Line had its own mechanical issues"],
      [c02a, c02b, c02c, c02d, c02e, c02f, c02g], [c06f], hop_count=6,
      notes="Full 6-hop cascade through ferry, bus, and rail")

    Q("Why were 42 Route 12 passengers stranded at Harbor on March 8, 2033?",
      "causal_chain", ["Ferry-B ran 45 minutes late due to accumulated fatigue from doubled schedule after Ferry-A's grounding, causing passengers to miss their connecting bus"],
      ["Ferry delay caused missed connections"], ["Route 12 buses were cancelled"],
      [c02b, c02c, c02d], [c01e], hop_count=2)

    # C03 chain queries
    Q("What chain of events led to Blue Line overcrowding in February 2034?",
      "cascade_analysis", ["Jiro's medical leave → Tane assigned dual role → delegated to Kira → Kira moved Bus-103 to Route 22 → Route 20 gaps → passengers shifted to Blue Line"],
      ["Staff changes cascaded to service changes"], ["Blue Line had mechanical problems"],
      [c03a, c03b, c03c, c03d, c03e, c03f], [], hop_count=5)

    Q("Why did Kira Nakamura reassign Bus-103 from Route 20 to Route 22?",
      "intermediate_node", ["Kira was delegated bus scheduling by Tane Parata, who was overwhelmed covering both bus and light rail divisions during Jiro Tanaka's medical leave; she moved Bus-103 to Route 22, the corridor she was most familiar with"],
      ["Delegation chain from Jiro's leave through Tane to Kira"], ["Kira was ordered to make the change"],
      [c03b, c03c, c03d], [c03a], hop_count=2,
      notes="Tests retrieval of intermediate authority nodes")

    # C04 chain queries
    Q("How did the federal funding cut lead to Ferry-B being grounded?",
      "causal_chain", ["Federal 15% funding cut → Ravi Mehta deferred Ferry-B hull inspection → inspection certificate expired → Maritime Authority grounded Ferry-B"],
      ["Budget cut led to deferred maintenance led to regulatory grounding"], ["Ferry-B had engine failure"],
      [c04a, c04b, c04c], [c02a], hop_count=2)

    Q("What was the full impact chain from the FY2034 federal funding cut to cross-island service?",
      "full_chain_traversal", ["Federal cut → budget restructure → deferred hull inspection → grounding → single-ferry operation → halved crossing frequency"],
      ["4-hop chain from funding to service reduction"], ["The funding cut was restored"],
      [c04a, c04b, c04c, c04d, c04e], [], hop_count=4)

    # C05 chain queries
    Q("How did a flawed ridership survey lead to Route 20's long-term ridership decline?",
      "full_chain_traversal", ["Flawed methodology double-counted transfers → inflated Route 24 patronage → board approved expansion → Route 20 lost buses → ridership dropped 40% → error discovered → expansion reversed but ridership hadn't recovered"],
      ["Survey error caused misallocation that permanently damaged Route 20"], ["Route 20 declined due to competition"],
      [c05a, c05b, c05c, c05d, c05e, c05f, c05g], [], hop_count=6,
      notes="Information chain with feedback loop and lasting damage")

    Q("Why was Route 24 expanded in September 2033?",
      "intermediate_node", ["The HTA Board approved the expansion based on a ridership survey that inflated Route 24 patronage by 35% due to a double-counting methodology error"],
      ["Based on flawed ridership data"], ["Route 24 had genuinely high demand"],
      [c05a, c05b, c05c], [], hop_count=2)

    # C06 chain queries
    Q("Why was LR-03 out of service for three weeks in early 2033?",
      "causal_chain", ["Supplier X was acquired by Company Y → specification changed from BA-400 to BA-450 → replacement part didn't fit → emergency sourcing needed → 3-week wait"],
      ["Supply chain change caused part incompatibility"], ["LR-03 had a derailment"],
      [c06a, c06b, c06c, c06d, c06e, c06f], [], hop_count=5)

    # C07 chain queries
    Q("How did the 2030 route plan influence the 2035 schedule revision?",
      "temporal_chain", ["2030 plan → 2031 Central Station investment → 2032 construction disruption → 2033 Midtown station opened → 2034 ridership shifted to Midtown hub → 2035 schedule revised to Midtown-focused shuttles"],
      ["Each year's decision built on the prior year's outcome"], ["The 2035 revision was independent of earlier plans"],
      [c07a, c07b, c07c, c07d, c07e, c07f], [], hop_count=5)

    Q("What did the 2036 performance review conclude about Midtown station's role?",
      "temporal_chain", ["The review traced the full evolution from the 2030 plan through each cascading decision and concluded that Midtown becoming the network hub was an emergent outcome not anticipated in the original design"],
      ["Emergent outcome traced across 7 years of decisions"], ["Midtown was always planned as the hub"],
      [c07a, c07f, c07g], [c07d], hop_count=6)

    # Cross-case queries
    Q("In how many separate incidents did East Depot Manager Sione Vunipola dispatch emergency bus reassignments?",
      "cross_case", ["At least two: Bus-102 to Route 12 during the 2032 Bus-101 maintenance crisis (C01) and Bus-102 to Harbor during the 2033 ferry failure cascade (C02)"],
      ["Multiple emergency dispatches across different crises"], ["Only one incident"],
      [c01d, c02e], [], hop_count=2, difficulty="medium",
      notes="Cross-case query linking C01 and C02 through a common actor")

    Q("Which HTA Board decisions were later reversed, and what triggered each reversal?",
      "cross_case", ["The Q3 2032 budget cut was reversed after the Island Herald investigation (C01), and the Route 24 expansion was reversed after the survey methodology error was discovered (C05)"],
      ["Two reversals: budget cut (media pressure) and Route 24 (audit discovery)"], ["No board decisions were reversed"],
      [c01a, c01g, c05c, c05f, c05g], [], hop_count=3,
      notes="Cross-case requiring synthesis of C01 and C05 chains")

    Q("How many separate events caused single-vehicle operation on a line during the 2032-2034 period?",
      "cross_case", ["At least two: LR-03's brake actuator issue left the Blue Line on single-car operation (C06), and Ferry-B's grounding left cross-island service on single-ferry operation (C04)"],
      ["Multiple single-vehicle incidents across different modes"], ["Only the ferry was affected"],
      [c06f, c04d], [c02a], hop_count=2, difficulty="medium")

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
    print(f"\nMemory distribution:")
    for k in sorted(tags):
        print(f"  {k}: {tags[k]}")

if __name__ == "__main__":
    main()
