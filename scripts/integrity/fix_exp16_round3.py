#!/usr/bin/env python3
"""Exp 16 round-3 expansion — target ≥ 200 memories, ≥ 75 queries."""

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

    mid_counter = len(memories) + 100
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
        _hash = hashlib.md5(f"exp16-r3-{mid_counter}".encode()).hexdigest()[:8]
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

    # Build ID lookup for existing memories
    mem_by_id = {m["memory_id"]: m for m in memories}

    # --- C01 additional chain nodes ---
    c01_comm = M("C01", "commuters", "filed_complaints", "Route_14_cancellations",
                 "Over 200 commuter complaints were filed with HTA customer service about Route 14 cancellations in August 2032, with many citing missed medical appointments.",
                 "event", "ground_truth", dt="2032-08-25", source_id="complaint-log")
    c01_council = M("C01", "city_council", "demanded_explanation", "HTA_service_failures",
                    "Three city council members sent a formal letter to HTA demanding an explanation for Route 14 service failures and threatening budget hearings.",
                    "event", "ground_truth", dt="2032-09-01", source_id="council-letter",
                    source_type="government_record", scope="public")
    c01_brake = M("C01", "brake_pads", "arrived", "Bus-101_October_2032",
                  "The deferred brake pad order for Bus-101 finally arrived on October 8, 2032, four months after the original scheduled delivery.",
                  "event", "ground_truth", dt="2032-10-08", source_id="procurement-log")

    # --- C02 additional ---
    c02_maint = M("C02", "Ferry-B", "required_emergency_maintenance", "engine_stress_March_2033",
                  "Ferry-B's engines required emergency maintenance on March 12 after 9 days of doubled service, with mechanics identifying bearing wear from overuse.",
                  "event", "ground_truth", dt="2033-03-12", source_id="maintenance-log")
    c02_taxi = M("C02", "HTA", "contracted_water_taxis", "March_2033_emergency",
                 "HTA contracted three private water taxis at premium rates to maintain minimum cross-island service while both ferries were down in mid-March 2033.",
                 "event", "ground_truth", dt="2033-03-13", source_id="procurement-log")
    c02_cost = M("C02", "water_taxi_operation", "cost_HTA", "$180K_over_budget",
                 "The emergency water taxi contracts cost HTA $180,000 over two weeks, exceeding the entire quarterly ferry maintenance budget.",
                 "event", "ground_truth", dt="2033-03-27", source_id="finance-report",
                 source_type="financial_record")

    # --- C03 additional ---
    c03_tane_err = M("C03", "Tane_Parata", "missed_LR_inspection_deadline", "February_2034",
                     "While managing both divisions, Tane Parata missed the February 2034 light rail safety inspection deadline, requiring an expedited weekend inspection.",
                     "event", "ground_truth", dt="2034-02-15", source_id="safety-log")
    c03_jiro_ret = M("C03", "Jiro_Tanaka", "returned_from_leave", "February_8_2034",
                     "Jiro Tanaka returned from medical leave on February 8, 2034, inheriting several operational issues created during his absence including the Bus-103 reassignment.",
                     "event", "ground_truth", dt="2034-02-08", source_id="hr-record",
                     source_type="hr_record")
    c03_review = M("C03", "Keanu_Lani", "ordered_coverage_review", "delegation_policy",
                   "After the cascading issues from Jiro's leave, GM Keanu Lani ordered a review of the division cross-coverage policy to prevent similar delegation chains.",
                   "event", "ground_truth", dt="2034-03-01", source_id="gm-directive")

    # --- C04 additional ---
    c04_drydock = M("C04", "Ferry-B", "entered_emergency_drydock", "October_2034",
                    "Ferry-B entered emergency drydock on October 1, 2034 for the overdue hull inspection, with the Maritime Authority requiring a full structural survey.",
                    "event", "ground_truth", dt="2034-10-01", source_id="maritime-log",
                    source_type="regulatory_record")
    c04_petition = M("C04", "west_island_residents", "petitioned", "restore_ferry_service",
                     "West island residents gathered 3,400 signatures on a petition demanding restoration of full cross-island ferry service within 30 days.",
                     "event", "ground_truth", dt="2034-11-01", source_id="petition-record",
                     scope="public")
    c04_restore = M("C04", "Ferry-B", "returned_to_service", "December_15_2034",
                    "Ferry-B passed its structural survey and returned to service on December 15, 2034, ending three months of single-ferry operation.",
                    "event", "ground_truth", dt="2034-12-15", source_id="maritime-log",
                    source_type="regulatory_record")

    # --- C05 additional ---
    c05_consult = M("C05", "consultancy_firm", "defended_methodology", "disputed_findings",
                    "The external consultancy firm initially disputed the audit findings, arguing that transfer double-counting was an accepted industry practice.",
                    "event", "ground_truth", dt="2034-02-01", source_id="correspondence",
                    source_type="correspondence", confidence=0.8)
    c05_perm_dmg = M("C05", "Route_20", "ridership_remained_depressed", "25%_below_baseline_mid_2035",
                     "Despite buses returning, Route 20 ridership remained 25% below its pre-cut baseline through mid-2035 as former riders had established alternative commute patterns.",
                     "event", "ground_truth", dt="2035-06-01", source_id="ridership-data")

    # --- C06 additional ---
    c06_adapter = M("C06", "maintenance_team", "considered_adapter_plate", "BA-450_to_BA-400",
                    "The maintenance team considered fabricating an adapter plate to make the BA-450 actuator fit the BA-400 mounting points, but Anika Sharma rejected this as unsafe.",
                    "event", "ground_truth", dt="2033-02-18", source_id="maintenance-log")
    c06_policy = M("C06", "Anika_Sharma", "established_sole_source_policy", "critical_rail_parts",
                   "After the LR-03 incident, Anika Sharma established a sole-source policy for critical rail parts, maintaining backup relationships with original-spec suppliers.",
                   "event", "ground_truth", dt="2033-04-01", source_id="policy-doc",
                   source_type="policy_document")

    # --- C07 additional ---
    c07_delay = M("C07", "airport_extension", "delayed_by_2_years", "budget_constraints",
                  "The Green Line airport extension, originally planned for 2035 completion, was delayed to 2037 due to accumulated budget pressures from operational crises.",
                  "event", "ground_truth", dt="2035-01-15", source_id="planning-doc",
                  source_type="planning_document")
    c07_compete = M("C07", "private_shuttle_service", "launched", "airport_corridor_2035",
                    "A private shuttle service launched in the airport corridor in 2035, capturing demand that the delayed Green Line extension was supposed to serve.",
                    "event", "ground_truth", dt="2035-06-01", source_id="media-report",
                    source_type="media_report", scope="public")

    # --- Additional background ---
    bg_extra = [
        ("HTA_annual_budget", "totals", "$85M_FY2032", "HTA's total annual operating budget for FY2032 was $85 million, with maintenance representing 22% of expenditures.", "2032-07-01"),
        ("passenger_safety_record", "maintained", "zero_serious_injuries_2030-2033", "HTA maintained a zero serious-injury record from 2030 through 2033 despite operational challenges.", "2033-12-31"),
        ("Anika_Sharma", "manages", "12_person_maintenance_team", "Maintenance Director Anika Sharma oversees a 12-person team split between the bus/ferry workshop and the light rail maintenance bay.", "2030-06-01"),
        ("Route_14", "serves", "hospital_corridor", "Route 14 serves the hospital corridor on the east side, making its reliability critical for medical appointment access.", "2030-03-15"),
        ("Route_24", "proposed_for", "southern_suburbs", "Route 24 was proposed to serve the growing southern suburbs, which had no direct transit connection to Downtown.", "2033-05-01"),
        ("tourism_season", "peaks", "June-August", "Island tourism peaks June through August, increasing ferry demand by 60% and straining the two-vessel fleet.", "2031-06-15"),
        ("Ravi_Mehta", "reports_to", "HTA_Board", "Budget Director Ravi Mehta reports directly to the HTA Board on financial matters and prepares quarterly budget forecasts.", "2030-01-15"),
        ("Grace_Okonkwo", "coordinates_with", "Sione_Vunipola", "West Depot Manager Grace Okonkwo and East Depot Manager Sione Vunipola coordinate vehicle sharing during maintenance windows.", "2030-02-15"),
        ("Central_Station", "handles", "45000_daily_transfers", "Central Station handles approximately 45,000 daily passenger transfers between bus and light rail services.", "2032-01-01"),
        ("HTA_customer_service", "receives", "200_calls_daily", "HTA customer service receives approximately 200 calls daily, with complaints spiking during service disruptions.", "2031-03-01"),
        ("bus_fleet_age", "averages", "4_years_in_2032", "The HTA bus fleet averaged 4 years of age in 2032, within manufacturer-recommended service life but approaching major maintenance milestones.", "2032-01-01"),
        ("light_rail_maintenance", "scheduled", "quarterly_inspections", "Light rail cars undergo mandatory quarterly safety inspections, with full overhauls every 18 months.", "2030-04-01"),
        ("ferry_turnaround", "requires", "30_minute_minimum", "Each ferry crossing takes 45 minutes with a minimum 30-minute turnaround for refueling and passenger boarding.", "2030-05-01"),
        ("Kira_Nakamura", "previously_managed", "Route_22_scheduling", "Before becoming the system-wide Scheduling Coordinator, Kira Nakamura managed Route 22 scheduling for three years.", "2030-02-01"),
        ("night_service", "operates", "limited_routes_10pm-6am", "HTA operates limited night service from 10 PM to 6 AM, with only Routes 10 and 20 running hourly.", "2030-03-01"),
    ]
    for subj, pred, obj, text, dt in bg_extra:
        M("background", subj, pred, obj, text,
          "fact", "ground_truth", dt=dt,
          source_id="hta-reference", source_type="reference_document",
          scope="public", confidence=0.95)

    # --- Additional queries to reach 75+ ---

    # Existing memory IDs from round 2 that we need - gather from the corpus
    all_mids = {m["memory_id"] for m in memories}

    # C01 queries
    Q("What role did commuter complaints play in the chain from Bus-101 maintenance to the Board's response?",
      "causal_chain", ["Over 200 complaints about Route 14 cancellations, combined with the Island Herald investigation, created the political pressure that led to the Board's emergency funding allocation"],
      ["Complaints added to media pressure"], ["Complaints were the primary cause of the reversal"],
      [c01_comm, c01_council], [], hop_count=2, difficulty="medium")

    Q("When did the deferred brake pads for Bus-101 finally arrive, and how long was the delay?",
      "factual_retrieval", ["The brake pads arrived October 8, 2032, four months after the originally scheduled June delivery"],
      ["October 2032, delayed by budget cut"], ["Brake pads never arrived"],
      [c01_brake], [], hop_count=1, difficulty="easy")

    # C02 queries
    Q("What were the financial consequences of the Ferry-A engine failure cascade?",
      "cascade_analysis", ["Emergency water taxi contracts cost $180,000 over two weeks, exceeding the quarterly ferry maintenance budget, on top of Ferry-B emergency maintenance costs from engine stress due to doubled service"],
      ["Water taxis cost $180K, Ferry-B needed emergency maintenance"], ["No significant financial impact"],
      [c02_maint, c02_taxi, c02_cost], [], hop_count=3, difficulty="medium")

    Q("What happened to Ferry-B during the period it was running doubled service?",
      "factual_retrieval", ["Ferry-B's engines suffered bearing wear from overuse and required emergency maintenance on March 12, after 9 days of doubled service replacing grounded Ferry-A"],
      ["Engine stress from doubled schedule"], ["Ferry-B operated normally"],
      [c02_maint], [], hop_count=1, difficulty="easy")

    # C03 queries
    Q("What additional problem did Tane Parata's dual-division role cause beyond the bus scheduling issues?",
      "intermediate_node", ["Tane missed the February 2034 light rail safety inspection deadline while managing both bus and light rail divisions, requiring an expedited weekend inspection"],
      ["Missed LR safety inspection"], ["No additional problems"],
      [c03_tane_err], [], hop_count=1, difficulty="medium")

    Q("What policy change resulted from the cascading issues during Jiro Tanaka's leave?",
      "causal_chain", ["GM Keanu Lani ordered a review of the division cross-coverage policy to prevent similar delegation chains from causing operational disruptions"],
      ["Cross-coverage policy review ordered"], ["No policy changes were made"],
      [c03_review], [c03_jiro_ret], hop_count=1, difficulty="medium")

    # C04 queries
    Q("How did west island residents respond to the single-ferry operation?",
      "factual_retrieval", ["3,400 residents signed a petition demanding restoration of full cross-island ferry service within 30 days"],
      ["Petition with 3,400 signatures"], ["Residents accepted the reduced service"],
      [c04_petition], [], hop_count=1, difficulty="easy")

    Q("How long was Ferry-B out of service due to the grounding, and when did it return?",
      "factual_retrieval", ["Ferry-B was grounded September 15 and returned to service December 15, 2034 — three months of single-ferry operation"],
      ["Three months, returned December 15, 2034"], ["Ferry-B never returned to service"],
      [c04_drydock, c04_restore], [], hop_count=1, difficulty="easy")

    # C05 queries
    Q("How did the consultancy respond when the survey error was discovered?",
      "factual_retrieval", ["The consultancy initially disputed the audit findings, arguing that transfer double-counting was an accepted industry practice"],
      ["Disputed the findings, claimed methodology was standard"], ["Immediately acknowledged the error"],
      [c05_consult], [], hop_count=1, difficulty="easy")

    Q("Why didn't Route 20 ridership recover after the Route 24 expansion was reversed?",
      "causal_chain", ["Former Route 20 riders had established alternative commute patterns (private transport, remote work) during the service cuts, and these habits persisted even after buses returned, leaving ridership 25% below baseline through mid-2035"],
      ["Riders found alternatives and didn't return"], ["Route 20 fully recovered immediately"],
      [c05_perm_dmg], [], hop_count=1, difficulty="medium")

    # C06 queries
    Q("Why didn't the maintenance team simply use an adapter plate for the BA-450 actuator?",
      "intermediate_node", ["The team considered fabricating an adapter plate but Maintenance Director Anika Sharma rejected it as unsafe, insisting on an original-spec replacement"],
      ["Rejected as unsafe by Anika Sharma"], ["An adapter plate was successfully used"],
      [c06_adapter], [], hop_count=1, difficulty="medium")

    Q("What long-term policy change resulted from the LR-03 brake actuator incident?",
      "causal_chain", ["Anika Sharma established a sole-source policy for critical rail parts, maintaining backup relationships with original-spec suppliers to prevent future supply chain disruptions"],
      ["Sole-source policy for critical parts"], ["No policy changes were made"],
      [c06_policy], [c06_adapter], hop_count=1, difficulty="medium")

    # C07 queries
    Q("What unintended consequence did the accumulated operational crises have on HTA's long-term plans?",
      "temporal_chain", ["The Green Line airport extension was delayed by 2 years (from 2035 to 2037) due to budget pressures from operational crises, and a private shuttle service launched to capture the unserved demand"],
      ["Airport extension delayed, private competition emerged"], ["Plans proceeded on schedule"],
      [c07_delay, c07_compete], [], hop_count=2, difficulty="medium")

    # Cross-case synthesis queries
    Q("Which HTA vehicles experienced extended out-of-service periods between 2032 and 2034, and what caused each?",
      "cross_case", ["Bus-101: extended maintenance due to deferred brake pads (budget cut). LR-03: 3 weeks for brake actuator sourcing (supplier acquisition changed specs). Ferry-A: engine failure. Ferry-B: grounded by maritime authority (overdue hull inspection from deferred maintenance)"],
      ["Multiple vehicles across different root causes"], ["Only Ferry-A was out of service"],
      [c01_brake, c04_drydock], [], hop_count=3, difficulty="hard",
      notes="Cross-case synthesis requiring C01, C02, C04, C06 knowledge")

    Q("How did Anika Sharma's maintenance decisions feature across multiple crisis chains?",
      "cross_case", ["Anika extended Bus-101 shop time due to deferred parts (C01), sourced emergency brake actuator for LR-03 from Japan (C06), and later established sole-source policy for critical parts. Her decisions were both constrained by budget cuts and proactive in preventing future issues"],
      ["Key actor across C01 and C06 chains"], ["Anika only dealt with bus maintenance"],
      [], [], hop_count=3, difficulty="hard",
      notes="Person-centric cross-case query")

    Q("Identify all instances where an HTA Board decision had unintended negative consequences.",
      "cross_case", ["Q3 2032 budget cut → Route 14 cancellations and media crisis (C01). Route 24 expansion approval → Route 20 service cuts and lasting ridership damage (C05). Both were later reversed but the damage was done"],
      ["Two board decisions with cascading negative outcomes"], ["Board decisions had no negative consequences"],
      [], [], hop_count=4, difficulty="hard")

    Q("What role did Kira Nakamura play in both the C03 staff chain and the C07 temporal chain?",
      "cross_case", ["In C03, Kira was delegated bus scheduling during Jiro's leave and reassigned Bus-103 to Route 22 (her former route), causing Route 20 gaps. In C07, she led the 2035 schedule revision that shifted Green Line to Midtown-focused shuttles based on evolved ridership patterns"],
      ["Kira appeared in both chains with different roles"], ["Kira only worked on bus scheduling"],
      [], [], hop_count=3, difficulty="hard")

    Q("How many separate incidents involved the Harbor terminal as a failure point or crisis location?",
      "cross_case", ["At least two major incidents: the March 2033 ferry cascade (C02) where passengers were stranded at Harbor after missed connections, and the broader ferry service reductions (C04) that affected Harbor as the ferry terminal"],
      ["Multiple Harbor-connected incidents"], ["Harbor was never a problem location"],
      [], [], hop_count=2, difficulty="medium")

    Q("What was the total cost to HTA of the Ferry-A engine failure cascade, considering both direct and indirect expenses?",
      "cascade_analysis", ["Direct: Ferry-A engine repair, Ferry-B emergency maintenance from overuse, $180K water taxi contracts. Indirect: Bus-102 emergency dispatch costs, Route 10 reduced service, Green Line overcrowding management"],
      ["Multiple direct and indirect costs across modes"], ["Only the engine repair cost"],
      [c02_cost, c02_maint, c02_taxi], [], hop_count=4, difficulty="hard")

    Q("Across all seven cases, which crisis had the longest chain of causation?",
      "meta_analysis", ["C02 (Transfer Cascade) at 6 hops: Ferry-A failure → doubled Ferry-B → delays → stranded passengers → emergency bus → reduced Route 10 → Green Line overcrowding. C07 (Temporal) spans 7 hops across years but is sequential rather than cascading"],
      ["C02 has 6 cascade hops, C07 spans 7 temporal hops"], ["C01 had the longest chain"],
      [], [], hop_count=1, difficulty="hard",
      notes="Meta-analysis requiring understanding of all chains")

    Q("Did any of the operational crises in 2032-2034 have overlapping time periods, and if so, how did they interact?",
      "temporal_overlap", ["The C01 budget crisis (summer 2032) predated but influenced subsequent events. The C02 ferry cascade (March 2033) and C06 LR-03 actuator issue (Feb-Mar 2033) overlapped, both reducing capacity on different modes simultaneously. C03 staff chain (Jan-Feb 2034) and C04 budget chain (leading to Sept 2034 grounding) overlapped in early 2034"],
      ["Multiple overlapping crises, some with compounding effects"], ["All crises were isolated in time"],
      [], [], hop_count=3, difficulty="hard")

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
