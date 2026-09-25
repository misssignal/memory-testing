#!/usr/bin/env python3
"""Third expansion for Experiment 15 — adds ~25 memories and ~30 queries to reach 200+/75+."""

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

    # === Additional memories to pad each case ===

    # C01: Method explanation memories
    ev = datetime(2030, 6, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev, ev+timedelta(hours=2), ev+timedelta(hours=4), ev+timedelta(hours=6),
        "Dr. Priya Nair", "explained", "Olsen P method",
        "Dr. Priya Nair explained that AgriLab NZ uses the Olsen P extraction method, which uses sodium bicarbonate at pH 8.5. Best suited for neutral to alkaline soils. Canterbury's silt loams are mildly acidic, which may cause underestimation of available phosphorus.",
        mtype="semantic", src="agrilab_nz", stype="professional_assessment", tags=["C01", "soil_test", "methodology"]))

    ev2 = datetime(2030, 6, 5, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev2, ev2+timedelta(hours=2), ev2+timedelta(hours=4), ev2+timedelta(hours=6),
        "Dr. James Whittle", "explained", "Bray P method",
        "Dr. James Whittle noted Canterbury Soil Services uses the Bray P extraction with dilute acid fluoride, better suited to acidic soils. Tends to extract more phosphorus than Olsen on Canterbury silt loams. Direct comparison between Bray and Olsen values is misleading without a conversion factor.",
        mtype="semantic", src="canterbury_soil", stype="professional_assessment", tags=["C01", "soil_test", "methodology"]))

    # C03: Wei Zhang data reconciliation
    ev3 = datetime(2033, 1, 20, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev3, ev3+timedelta(hours=2), ev3+timedelta(hours=4), ev3+timedelta(hours=6),
        "Wei Zhang", "analyzed", "yield prediction accuracy 2032",
        "Wei Zhang's analysis of 2032 yield prediction accuracy across cooperative: satellite estimates averaged 15% above actual, agronomist estimates 8% above, pre-harvest samples 4% above. Satellite consistently overestimates in dry years.",
        mtype="semantic", src="data_analysis", stype="data_analysis", tags=["C03", "yield", "analysis"]))

    # C04: Discussion of observer bias
    ev4 = datetime(2032, 1, 10, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev4, ev4+timedelta(hours=2), ev4+timedelta(hours=4), ev4+timedelta(hours=6),
        "Hana Tūhoe", "presented", "observer bias in pest counting",
        "Hana Tūhoe's presentation at cooperative January meeting on observer bias in pest monitoring. Key points: trained counters tend to be more accurate, visual estimates from non-specialists overestimate by 30-50%, drone algorithms underestimate in dense canopy. Recommends standardized protocol.",
        mtype="semantic", src="meeting_presentation", stype="professional_assessment", tags=["C04", "pest_count", "methodology"]))

    # C05: Margaret Holt frustration with weather data
    ev5 = datetime(2033, 4, 1, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev5, ev5+timedelta(hours=1), ev5+timedelta(hours=3), ev5+timedelta(hours=5),
        "Margaret Holt", "complained", "weather data inconsistency",
        "Margaret Holt raised at April 2033 committee meeting: 'We've got three different rainfall numbers for the March storm — our gauge, the council, and the insurer all disagree. How are we supposed to make irrigation decisions when we can't even agree on how much rain fell?'",
        src="meeting_minutes", stype="meeting_record", tags=["C05", "weather", "data_quality"]))

    # C06: Sarah Chen guidance on nitrogen
    ev6 = datetime(2033, 10, 15, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev6, ev6+timedelta(hours=2), ev6+timedelta(hours=4), ev6+timedelta(hours=6),
        "Sarah Chen", "recommended", "nitrogen application guidance",
        "Sarah Chen's recommendation to cooperative members following Margaret's request, October 2033: apply the most restrictive applicable limit. For most members, that's the new MPI limit of 150 kg N/ha. For export-oriented farms near waterways, consider the industry target of 140. Keep records to demonstrate compliance with all overlapping rules.",
        mtype="semantic", src="agronomist_notes", stype="professional_assessment", tags=["C06", "regulation", "nitrogen"]))

    # C07: Tom Brewer's explanation of T-04
    ev7 = datetime(2032, 3, 20, tzinfo=timezone.utc)
    new_mems.append(make_mem(mid(), ev7, ev7+timedelta(hours=1), ev7+timedelta(hours=3), ev7+timedelta(hours=5),
        "Tom Brewer", "explained", "T-04 service date confusion",
        "Tom Brewer explained at March 2032 debrief: T-04 service was originally booked for 15th, I rescheduled to 22nd by email, but Canterbury Farm Services had a cancellation and called David directly to bring it in on the 18th. David took it in without telling me. The email and schedule were both out of date.",
        src="meeting_minutes", stype="meeting_record", tags=["C07", "equipment", "T-04"]))

    # Background — more
    bg = [
        (datetime(2030, 3, 1, tzinfo=timezone.utc), "Thornfield Cooperative", "reviewed", "health and safety plan",
         "Annual health and safety plan review. Updated chainsaw training requirements, chemical handling procedures, and tractor rollover protection standards."),
        (datetime(2031, 9, 1, tzinfo=timezone.utc), "Margaret Holt", "wrote", "cooperative newsletter September 2031",
         "Margaret Holt's quarterly newsletter to members: harvest outlook positive, new weather station network coming online, reminder about upcoming pesticide certification renewals."),
        (datetime(2032, 12, 22, tzinfo=timezone.utc), "Thornfield Cooperative", "distributed", "end of year financial summary 2032",
         "End of year financial summary distributed to members. Total cooperative turnover $24.5 million. Net surplus after expenses: $380,000. Equipment fund balance: $290,000 after header depreciation."),
        (datetime(2033, 4, 20, tzinfo=timezone.utc), "David Kāhui", "coordinated", "autumn cultivation programme",
         "David Kāhui coordinated the autumn cultivation programme across 12 farms. Priority: minimum tillage on all canola stubble, direct drill wheat into oat cover crop on trial blocks."),
        (datetime(2034, 1, 15, tzinfo=timezone.utc), "Wei Zhang", "trained", "farm staff on FarmIQ",
         "Wei Zhang ran refresher training sessions on FarmIQ for 25 farm staff across the cooperative. Focus on accurate data entry for fertilizer applications and stock movements."),
        (datetime(2034, 8, 1, tzinfo=timezone.utc), "Sarah Chen", "published", "cooperative soil health summary",
         "Sarah Chen published a five-year soil health summary for the cooperative. Key finding: farms using cover crops showed 0.3% higher organic matter than continuous cropping farms."),
        (datetime(2035, 1, 10, tzinfo=timezone.utc), "Lachlan Murray", "renegotiated", "Ravensdown supply contract",
         "Lachlan Murray renegotiated the cooperative's bulk fertilizer supply contract with Ravensdown. Three-year deal with 8% volume discount. Estimated saving: $120,000/year."),
        (datetime(2035, 7, 1, tzinfo=timezone.utc), "Tom Brewer", "implemented", "equipment booking app",
         "Tom Brewer launched a mobile app for equipment booking within the cooperative. Members can view availability and book tractors, headers, and sprayers from their phones."),
        (datetime(2035, 11, 15, tzinfo=timezone.utc), "Thornfield Cooperative", "hosted", "soil health field day",
         "Cooperative hosted a soil health field day in November 2035. Demonstrations of spading, cover crops, and compost application. Guest speaker: Dr. Priya Nair on soil biology indicators."),
    ]
    for dt, subj, pred, obj_, text in bg:
        new_mems.append(make_mem(mid(), dt, dt+timedelta(hours=2), dt+timedelta(hours=4), dt+timedelta(hours=6),
            subj, pred, obj_, text, src=pred, stype="internal_record", tags=["background"]))

    # === 30 new queries to reach 75+ ===

    # C01 deep-dive queries
    new_qs.append(make_query("Q15-r3-01",
        "Why do AgriLab NZ and Canterbury Soil Services give different phosphorus readings?",
        "contradictory_sources",
        ["Different extraction methods: Olsen P (bicarbonate) vs Bray P (acid fluoride)"],
        ["Bray tends to extract more P on Canterbury silt loams", "Direct comparison is misleading without conversion"],
        ["Labs are inaccurate", "One lab is correct and the other wrong"],
        [], []))

    new_qs.append(make_query("Q15-r3-02",
        "Does Long Flat Block A need phosphorus fertilizer according to the 2032 tests?",
        "contradictory_sources",
        ["AgriLab says maintenance only (Olsen P 24); Canterbury says no P needed (Bray P 38)"],
        ["Labs agree fertility is adequate but differ on whether any P is needed"],
        ["Urgent P needed", "Both labs agree exactly"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r3-03",
        "How severe is the phosphorus deficiency on Brewer Downs paddock 3?",
        "contradictory_sources",
        ["AgriLab calls it urgent (Olsen P 10); Canterbury calls it moderate (Bray P 18)"],
        ["Both agree deficiency exists but disagree on severity and response"],
        ["No deficiency", "Both labs agree on severity"],
        [], [], conflict=True))

    # C02 more queries
    new_qs.append(make_query("Q15-r3-04",
        "Which price source gives the highest wheat price?",
        "source_dependent",
        ["Export buyer consistently gives highest price (FOB includes shipping margin)"],
        ["USDA index is consistently lowest"],
        ["All sources give the same price"],
        [], []))

    new_qs.append(make_query("Q15-r3-05",
        "What was the canola price trend from 2032 to 2034?",
        "source_dependent",
        ["Prices rose across all sources: cooperative $680 to $710, NZX $695 to $725, export $720 to $755"],
        ["Strong upward trend"],
        ["Prices fell"],
        [], []))

    new_qs.append(make_query("Q15-r3-06",
        "What lamb prices were available in September 2031?",
        "source_dependent",
        ["Cooperative schedule $6.20/kg, AgriHQ market $6.50/kg, meat works quote $5.90/kg"],
        ["Market data was highest, works quote lowest"],
        ["A single lamb price"],
        [], [], conflict=True))

    # C03 more queries
    new_qs.append(make_query("Q15-r3-07",
        "What was the actual canola yield at Pōhatu Farm in 2033?",
        "revised_estimates",
        ["2.6 tonnes/ha — below both satellite (2.8) and agronomist (3.1) estimates"],
        ["Late frost damage in October was the cause"],
        ["3.1 was the actual", "Predictions were accurate"],
        [], []))

    new_qs.append(make_query("Q15-r3-08",
        "How did the 2032 yield prediction accuracy compare across methods?",
        "revised_estimates",
        ["Satellite averaged 15% above actual, agronomist 8% above, pre-harvest 4% above"],
        ["Wei Zhang's analysis showed satellite consistently overestimates in dry years"],
        ["All methods were equally accurate"],
        [], []))

    new_qs.append(make_query("Q15-r3-09",
        "What happened to Pōhatu wheat yield in 2034?",
        "revised_estimates",
        ["Actual 5.7 t/ha — close to agronomist estimate of 5.9 but above satellite estimate of 5.5"],
        ["Good season overall"],
        ["5.5 was actual", "Estimates were all wrong"],
        [], []))

    # C04 more queries
    new_qs.append(make_query("Q15-r3-10",
        "What does Hana Tūhoe say about observer bias in pest counts?",
        "observer_disagreement",
        ["Trained counters more accurate; non-specialists overestimate 30-50%; drones underestimate in dense canopy"],
        ["Recommends standardized protocol"],
        ["All observers are equally accurate", "Drones are most accurate"],
        [], []))

    new_qs.append(make_query("Q15-r3-11",
        "Should Brewer Downs paddock 12 be treated for grass grub?",
        "observer_disagreement",
        ["Rob says yes (180/m², above 150 threshold); Hana says no (140/m², below threshold, natural predation expected)"],
        ["Different sample sizes: Rob 5, Hana 20"],
        ["Definitely treat or definitely don't without noting disagreement"],
        [], [], conflict=True))

    # C05 more queries
    new_qs.append(make_query("Q15-r3-12",
        "How cold was the frost at Riverside Farm on 3 October 2033?",
        "measurement_conflict",
        ["Farm station: -3.2°C, NIWA Lincoln (8km away): -2.8°C, MetService had predicted -1°C"],
        ["Forecast significantly underestimated"],
        ["-1°C", "Forecast was accurate"],
        [], [], conflict=True))

    new_qs.append(make_query("Q15-r3-13",
        "What did Margaret Holt say about weather data reliability?",
        "measurement_conflict",
        ["Complained that three sources gave different rainfall numbers for the same storm"],
        ["Questioned how to make irrigation decisions with inconsistent data"],
        ["Weather data is reliable"],
        [], []))

    # C06 more queries
    new_qs.append(make_query("Q15-r3-14",
        "What did Sarah Chen recommend for nitrogen application rates?",
        "regulatory_conflict",
        ["Apply the most restrictive applicable limit — usually 150 kg/ha (new MPI), consider 140 for export farms near waterways"],
        ["Keep records for all overlapping rules"],
        ["Apply 180 kg/ha", "One simple rule applies"],
        [], []))

    new_qs.append(make_query("Q15-r3-15",
        "Has the MPI nitrogen limit changed over time?",
        "regulatory_conflict",
        ["Yes — was 180 kg/ha in 2031, reduced to 150 kg/ha in August 2033"],
        ["2033 guidance supersedes 2031"],
        ["Always been 150", "Always been 180", "Limit hasn't changed"],
        [], []))

    new_qs.append(make_query("Q15-r3-16",
        "Which nitrogen limit is most restrictive?",
        "regulatory_conflict",
        ["Industry best practice at 140 kg/ha is lowest, then MPI 150, regional council 160, old MPI 180"],
        ["For organic, BioGro prohibits synthetic N entirely"],
        ["All limits are the same", "180 is still in effect"],
        [], []))

    # C07 more queries
    new_qs.append(make_query("Q15-r3-17",
        "What actually happened with the T-04 service scheduling?",
        "self_contradicting",
        ["Booked for 15th, rescheduled to 22nd via email, but Canterbury Farm Services called David to bring it 18th due to a cancellation"],
        ["Tom Brewer explained the mix-up at the March debrief"],
        ["Everything went according to plan"],
        [], []))

    new_qs.append(make_query("Q15-r3-18",
        "Why was there a 15-head difference in the Brewer Downs lamb count?",
        "self_contradicting",
        ["Possible explanations: lambs in wrong paddock not counted by Rob, or deaths/sales not yet recorded in FarmIQ"],
        ["Rob counted 847 on horseback; FarmIQ register shows 862"],
        ["Counts matched", "Exactly 847 lambs"],
        [], [], uncertainty=True))

    # Cross-case queries
    new_qs.append(make_query("Q15-r3-19",
        "Which types of contradictions in the cooperative's data are due to methodology vs genuine disagreement?",
        "cross_case",
        ["Methodology: soil test methods (C01), yield prediction models (C03). Genuine: pest counts (C04), weather measurements (C05), record-keeping errors (C07)"],
        ["Price differences (C02) reflect different markets, not error"],
        ["All contradictions are errors"],
        [], []))

    new_qs.append(make_query("Q15-r3-20",
        "How does the cooperative handle contradictory information from different sources?",
        "cross_case",
        ["Sarah Chen recommends applying the most restrictive rule for regulations; splitting the difference for soil test recommendations"],
        ["Wei Zhang tracks prediction accuracy; Hana recommends standardized protocols"],
        ["Contradictions are ignored", "One source is always used"],
        [], []))

    new_qs.append(make_query("Q15-r3-21",
        "What are the reliability tiers of the cooperative's data sources?",
        "cross_case",
        ["Certified measurements (weigh-bridge, instruments) most reliable; professional assessments moderate; visual estimates and forecasts least reliable"],
        ["Hana presented on this topic regarding pest counting"],
        ["All equally reliable"],
        [], []))

    # Control queries
    new_qs.append(make_query("Q15-r3-22",
        "How much did the cooperative's new sprayer cost?",
        "control",
        ["$385,000 for a Goldacres G6, 24m self-propelled, purchased July 2033"],
        ["Replaces aging Hardi unit, has GPS section control"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r3-23",
        "What was the cooperative's annual turnover in 2034?",
        "control",
        ["$28 million/year as of the 5th anniversary celebration in March 2034"],
        ["43 member families"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r3-24",
        "Who manages the cooperative's data systems?",
        "control",
        ["Wei Zhang, Data & Records Officer"],
        ["Implemented FarmIQ cloud system in 2031", "Upgraded to satellite imagery integration in 2035"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r3-25",
        "What export markets does the cooperative serve?",
        "control",
        ["Japan (primary, via Nissin Foods), Malaysia (flour mill, since 2034), South Korea (CJ CheilJedang, since 2034)"],
        ["Direct shipping via Maersk from Lyttelton to Yokohama"],
        [], [], [],
        difficulty="easy"))

    new_qs.append(make_query("Q15-r3-26",
        "What precision agriculture investment has the cooperative made?",
        "control",
        ["SFF-funded project (2032-2034): variable rate fertilizer, soil sensors, GPS guidance on header, drone capability"],
        ["Results: 6% yield improvement, 10% fertilizer cost reduction"],
        [], [], [],
        difficulty="medium"))

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

    q_cats = {}
    for q in queries:
        c = q.get("category", "?")
        q_cats[c] = q_cats.get(c, 0) + 1
    print(f"\nQuery distribution:")
    for c in sorted(q_cats):
        print(f"  {c}: {q_cats[c]}")

if __name__ == "__main__":
    main()
