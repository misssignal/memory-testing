#!/usr/bin/env python3
"""Fix and expand Experiment 13 corpus to meet minimum targets (200+ memories, 75+ queries)."""

import json
import hashlib
import sys
from pathlib import Path
from collections import Counter


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def fix(exp_dir):
    exp_dir = Path(exp_dir)
    memories = [json.loads(l) for l in open(exp_dir / "memories.jsonl")]
    queries = [json.loads(l) for l in open(exp_dir / "queries.jsonl")]
    with open(exp_dir / "truth_state.json") as f:
        truth = json.load(f)

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_memories = []
    new_queries = []
    next_mid = len(memories) + 1

    def mem(text, **kw):
        nonlocal next_mid
        m = {
            "memory_id": f"M{next_mid:04d}",
            "experiment": "exp13_consolidation_summarization_drift",
            "story_id": "cascade_institute",
            "event_time": kw["event_time"],
            "observation_time": kw.get("observation_time", kw["event_time"]),
            "authored_time": kw.get("authored_time", kw.get("observation_time", kw["event_time"])),
            "ingestion_time": kw["ingestion_time"],
            "subject": kw.get("subject", ""),
            "predicate": kw.get("predicate", ""),
            "object": kw.get("object", ""),
            "text": text,
            "memory_type": kw.get("memory_type", "observation"),
            "truth_role": kw.get("truth_role", "current_truth"),
            "belief_holder": kw.get("belief_holder", "system"),
            "confidence": kw.get("confidence", 1.0),
            "source_id": kw.get("source_id", "cascade_ops"),
            "source_type": kw.get("source_type", "system_record"),
            "derived_from": kw.get("derived_from", []),
            "supersedes": kw.get("supersedes", []),
            "contradicts": kw.get("contradicts", []),
            "duplicates": kw.get("duplicates", []),
            "aliases": kw.get("aliases", []),
            "scope": kw.get("scope", "institute"),
            "tags": kw["tags"],
            "summary_layer": kw.get("summary_layer", 0),
        }
        new_memories.append(m)
        next_mid += 1
        return m["memory_id"]

    def qry(query, **kw):
        q = {
            "query_id": f"Q{len(queries) + len(new_queries) + 1:03d}",
            "query": query,
            "category": kw["category"],
            "expected_claims": kw.get("expected_claims", []),
            "acceptable_claims": kw.get("acceptable_claims", []),
            "forbidden_claims": kw.get("forbidden_claims", []),
            "relevant_memory_ids": kw.get("relevant_memory_ids", []),
            "distractor_memory_ids": kw.get("distractor_memory_ids", []),
            "requires_temporal_reasoning": kw.get("requires_temporal_reasoning", False),
            "difficulty": kw.get("difficulty", "medium"),
            "target_layer": kw.get("target_layer", None),
        }
        new_queries.append(q)

    # ── Expand C01: More qualifier loss chain ────────────────────────
    print("\nExpanding C01 (qualifier loss)...")

    mem("Wind stress measurements at Station K7 in August 2028 showed slightly elevated upwelling-favorable conditions (anomaly +0.8 dyn/cm², p=0.12, not significant). Wind conditions alone do not explain the temperature anomaly.",
        subject="Station K7 wind", predicate="showed", object="slightly elevated upwelling (+0.8 dyn/cm², p=0.12, NS)",
        event_time="2028-08-15T15:00:00Z", observation_time="2028-08-15T16:00:00Z",
        authored_time="2028-08-16T09:00:00Z", ingestion_time="2028-08-17T09:00:00Z",
        source_id="P05", source_type="instrument_reading",
        tags=["C01", "qualifier_loss", "raw_data", "Station_K7", "wind"], summary_layer=0, truth_role="ground_truth")

    mem("Station K7 historical baseline (2015–2027): August mean SST anomaly = +0.3°C ± 0.6°C. The 2028 anomaly of +1.2°C is 1.5 standard deviations above the mean, which is notable but within the historical envelope.",
        subject="Station K7 baseline", predicate="shows", object="2028 anomaly is 1.5σ above mean, within historical envelope",
        event_time="2028-08-20T09:00:00Z", observation_time="2028-08-20T14:00:00Z",
        authored_time="2028-08-21T10:00:00Z", ingestion_time="2028-08-22T09:00:00Z",
        source_id="P05", source_type="statistical_analysis",
        tags=["C01", "qualifier_loss", "raw_data", "Station_K7", "baseline"], summary_layer=0, truth_role="ground_truth")

    mem("Dr. Rivera's internal memo (September 2028): 'The K7 anomaly is interesting but I want to caution against over-interpreting a single station, single month signal. We need at least two more seasons of data before drawing conclusions about trends.'",
        subject="Dr. Rivera", predicate="cautioned_against", object="over-interpreting K7 single-station signal",
        event_time="2028-09-05T10:00:00Z", observation_time="2028-09-05T11:00:00Z",
        authored_time="2028-09-05T14:00:00Z", ingestion_time="2028-09-06T09:00:00Z",
        source_id="P02", source_type="internal_memo",
        tags=["C01", "qualifier_loss", "raw_data", "expert_opinion"], summary_layer=0, truth_role="ground_truth")

    mem("Station K7 September 2028 follow-up: SST returned to baseline (+0.2°C anomaly, within normal range). The August anomaly appears to have been transient.",
        subject="Station K7", predicate="returned_to_baseline", object="+0.2°C in September (normal)",
        event_time="2028-09-15T14:00:00Z", observation_time="2028-09-15T15:00:00Z",
        authored_time="2028-09-16T10:00:00Z", ingestion_time="2028-09-17T09:00:00Z",
        source_id="P02", source_type="instrument_reading",
        tags=["C01", "qualifier_loss", "raw_data", "Station_K7", "follow_up"], summary_layer=0, truth_role="ground_truth")

    # ── Expand C02: More uncertainty chain ───────────────────────────
    print("Expanding C02 (uncertainty loss)...")

    mem("Individual model projections for Oregon coast sea-level rise by 2050: GFDL-ESM4: 42cm, CESM2: 41cm, UKESM1: 45cm, MPI-ESM: 32cm, ACCESS-CM2: 28cm, NorESM2: 25cm, CNRM-CM6: 22cm, MIROC6: 18cm, IPSL-CM6A: 30cm, BCC-CSM2: 15cm, CanESM5: 26cm, INM-CM5: 20cm.",
        subject="sea-level models", predicate="project_individually", object="15-45cm range across 12 models",
        event_time="2029-06-01T01:00:00Z", observation_time="2029-06-15T10:00:00Z",
        authored_time="2029-06-20T15:00:00Z", ingestion_time="2029-06-21T10:00:00Z",
        source_id="P04", source_type="model_output",
        tags=["C02", "uncertainty_loss", "raw_data", "individual_models"], summary_layer=0, truth_role="ground_truth")

    mem("Dr. Patel's modeling report note: 'The three high-end models (GFDL, CESM2, UKESM1) include parameterizations for rapid West Antarctic Ice Sheet collapse. If WAIS instability is excluded, the range narrows to 15-32cm. The policy-relevant question is whether to plan for the median or the tail risk.'",
        subject="Dr. Patel", predicate="noted", object="high-end models include WAIS collapse; planning question is median vs tail",
        event_time="2029-06-03T10:00:00Z", observation_time="2029-06-16T10:00:00Z",
        authored_time="2029-06-21T11:00:00Z", ingestion_time="2029-06-22T10:00:00Z",
        source_id="P04", source_type="analysis_note",
        tags=["C02", "uncertainty_loss", "raw_data", "methodology"], summary_layer=0, truth_role="ground_truth")

    mem("Sensitivity analysis: If ocean thermal expansion uncertainty is halved, the projection range narrows from 15–45cm to 20–38cm. The remaining spread is dominated by ice sheet uncertainty, which cannot be reduced with current data.",
        subject="sensitivity analysis", predicate="shows", object="ice sheet uncertainty dominates residual spread",
        event_time="2029-06-05T10:00:00Z", observation_time="2029-06-17T10:00:00Z",
        authored_time="2029-06-22T11:00:00Z", ingestion_time="2029-06-23T09:00:00Z",
        source_id="P04", source_type="sensitivity_analysis",
        tags=["C02", "uncertainty_loss", "raw_data", "sensitivity"], summary_layer=0, truth_role="ground_truth")

    # ── Expand C03: More provenance detail ───────────────────────────
    print("Expanding C03 (provenance loss)...")

    mem("Dr. Tanaka's field note on urchin-kelp interaction: 'While urchin overgrazing is clearly occurring, I cannot determine from my census data alone whether acidification facilitated the urchin explosion. The sea star wasting disease is the proximate cause of predator loss. Acidification may be a background stressor but my study does not test this.'",
        subject="Dr. Tanaka", predicate="noted", object="cannot determine if acidification facilitated urchin explosion from census data alone",
        event_time="2029-10-20T10:00:00Z", observation_time="2029-10-20T11:00:00Z",
        authored_time="2029-10-20T15:00:00Z", ingestion_time="2029-10-21T09:00:00Z",
        source_id="P03", source_type="field_note",
        tags=["C03", "provenance_loss", "raw_data", "urchins", "expert_caveat"], summary_layer=0, truth_role="ground_truth")

    mem("Dr. Rivera's kelp survey note: 'Kelp canopy loss is multi-factorial. Water temperature, nutrient changes, wave exposure, and grazing pressure all contribute. My survey documents the loss but does not isolate a single cause.'",
        subject="Dr. Rivera", predicate="noted", object="kelp loss is multi-factorial, survey does not isolate cause",
        event_time="2029-09-05T10:00:00Z", observation_time="2029-09-05T11:00:00Z",
        authored_time="2029-09-05T15:00:00Z", ingestion_time="2029-09-06T09:00:00Z",
        source_id="P02", source_type="field_note",
        tags=["C03", "provenance_loss", "raw_data", "kelp", "expert_caveat"], summary_layer=0, truth_role="ground_truth")

    mem("Dr. Patel's clarification email: 'My acidification model projects pH changes in the water column. It does not model biological responses. Any connection between my pH projections and kelp/urchin dynamics would need a separate coupled model that does not yet exist.'",
        subject="Dr. Patel", predicate="clarified", object="pH model does not model biological responses",
        event_time="2030-04-15T10:00:00Z", observation_time="2030-04-15T11:00:00Z",
        authored_time="2030-04-15T14:00:00Z", ingestion_time="2030-04-16T09:00:00Z",
        source_id="P04", source_type="correspondence",
        tags=["C03", "provenance_loss", "raw_data", "expert_caveat"], summary_layer=0, truth_role="ground_truth")

    mem("Internal review of Q1 2030 Ecology Report: Kira Johansson flagged that the report's phrase 'consistent with acidification-driven urchin overgrazing' implies a causal chain that none of the three individual studies established. Dr. Okafor acknowledged the concern but kept the language, noting it was 'editorially reasonable.'",
        subject="internal review", predicate="flagged", object="causal language not supported by individual studies",
        event_time="2030-04-12T14:00:00Z", observation_time="2030-04-12T15:00:00Z",
        authored_time="2030-04-12T17:00:00Z", ingestion_time="2030-04-13T09:00:00Z",
        source_id="P07", source_type="review_comment",
        tags=["C03", "provenance_loss", "editorial_decision"], summary_layer=0, truth_role="ground_truth")

    # ── Expand C04: More temporal detail ─────────────────────────────
    print("Expanding C04 (temporal flattening)...")

    mem("El Niño conditions confirmed for 2031 by NOAA Climate Prediction Center. Oceanic Niño Index (ONI) reached +1.8°C in September 2031, categorized as 'strong El Niño.' Expected to reduce ocean productivity along Oregon coast.",
        subject="El Niño 2031", predicate="confirmed_as", object="strong (ONI +1.8°C)",
        event_time="2031-09-15T00:00:00Z", observation_time="2031-09-15T09:00:00Z",
        authored_time="2031-09-16T10:00:00Z", ingestion_time="2031-09-17T09:00:00Z",
        source_id="P04", source_type="climate_record",
        tags=["C04", "temporal_flattening", "raw_data", "ENSO"], summary_layer=0, truth_role="ground_truth")

    mem("2028 Oregon drought severity: Palmer Drought Severity Index (PDSI) reached -3.2, classified as 'severe drought.' River flows were 60% of normal July–October, directly impacting salmon migration conditions.",
        subject="2028 drought", predicate="reached", object="PDSI -3.2, severe drought",
        event_time="2028-10-01T00:00:00Z", observation_time="2028-10-01T09:00:00Z",
        authored_time="2028-10-02T10:00:00Z", ingestion_time="2028-10-03T09:00:00Z",
        source_id="P05", source_type="climate_record",
        tags=["C04", "temporal_flattening", "raw_data", "drought"], summary_layer=0, truth_role="ground_truth")

    mem("Salmon counting methodology comparison study (2033): Side-by-side testing of visual observer vs sonar counting at the same weir. Sonar detected 108% of the fish that visual observers counted (CI: 105–111%). Recommendation: apply 0.92 correction factor to sonar counts for continuity with historical data.",
        subject="counting methodology", predicate="comparison_shows", object="sonar counts 108% of visual (CI 105-111%)",
        event_time="2033-07-01T00:00:00Z", observation_time="2033-07-15T09:00:00Z",
        authored_time="2033-07-20T14:00:00Z", ingestion_time="2033-07-21T09:00:00Z",
        source_id="P05", source_type="methodology_study",
        tags=["C04", "temporal_flattening", "raw_data", "methodology_change"], summary_layer=0, truth_role="ground_truth")

    mem("2030 salmon run ecological context: Favorable ocean conditions (strong upwelling, cool PDO) supported above-average plankton production, translating to higher salmon marine survival. The 22,100 count reflects genuine environmental favorability, not a management intervention.",
        subject="2030 salmon run", predicate="explained_by", object="favorable ocean conditions, strong upwelling",
        event_time="2030-11-01T00:00:00Z", observation_time="2030-11-01T09:00:00Z",
        authored_time="2030-11-02T10:00:00Z", ingestion_time="2030-11-03T09:00:00Z",
        source_id="P02", source_type="ecological_assessment",
        tags=["C04", "temporal_flattening", "raw_data", "salmon"], summary_layer=0, truth_role="ground_truth")

    # ── Expand C05: More coral detail ────────────────────────────────
    print("Expanding C05 (identity collapse)...")

    mem("Acropora digitifera recovery tracking (2030–2032): 24 months post-bleaching, only 12% of bleached colonies showed regrowth. Projected full recovery time: 5–7 years under current conditions, unlikely if another bleaching event occurs within 3 years.",
        subject="Acropora digitifera", predicate="recovering_slowly", object="12% regrowth at 24 months, 5-7yr projected full recovery",
        event_time="2032-03-15T09:00:00Z", observation_time="2032-03-15T14:00:00Z",
        authored_time="2032-03-16T10:00:00Z", ingestion_time="2032-03-17T09:00:00Z",
        source_id="P03", source_type="field_survey",
        tags=["C05", "identity_collapse", "raw_data", "coral", "C05_species_A", "recovery"], summary_layer=0, truth_role="ground_truth")

    mem("Pocillopora damicornis recovery tracking (2030–2031): 12 months post-bleaching, 65% of bleached colonies showed active regrowth. Species demonstrating moderate resilience as expected. Full recovery projected by mid-2032.",
        subject="Pocillopora damicornis", predicate="recovering_moderately", object="65% regrowth at 12 months",
        event_time="2031-03-16T09:00:00Z", observation_time="2031-03-16T14:00:00Z",
        authored_time="2031-03-17T10:00:00Z", ingestion_time="2031-03-18T09:00:00Z",
        source_id="P03", source_type="field_survey",
        tags=["C05", "identity_collapse", "raw_data", "coral", "C05_species_B", "recovery"], summary_layer=0, truth_role="ground_truth")

    mem("Porites lobata status (2030–2032): No measurable decline. Colony growth rates maintained at 0.8cm/year, consistent with pre-bleaching baseline. Species is functionally unaffected by the 2030 thermal event and is expanding into habitat vacated by Acropora.",
        subject="Porites lobata", predicate="thriving", object="growth maintained, expanding into Acropora habitat",
        event_time="2032-03-17T09:00:00Z", observation_time="2032-03-17T14:00:00Z",
        authored_time="2032-03-18T10:00:00Z", ingestion_time="2032-03-19T09:00:00Z",
        source_id="P03", source_type="field_survey",
        tags=["C05", "identity_collapse", "raw_data", "coral", "C05_species_C", "thriving"], summary_layer=0, truth_role="ground_truth")

    mem("Reef community composition shift (2030–2032): Sector A reef transitioning from Acropora-dominated to Porites-dominated community. Total living coral cover decreased only 15% (from 62% to 53%) despite dramatic species turnover. Reef is changing, not dying.",
        subject="reef community", predicate="shifting_from", object="Acropora-dominated to Porites-dominated (cover 62% → 53%)",
        event_time="2032-04-01T09:00:00Z", observation_time="2032-04-01T14:00:00Z",
        authored_time="2032-04-02T10:00:00Z", ingestion_time="2032-04-03T09:00:00Z",
        source_id="P03", source_type="ecological_assessment",
        tags=["C05", "identity_collapse", "raw_data", "coral", "community_shift"], summary_layer=0, truth_role="ground_truth")

    # ── Expand C06: More drift chain ─────────────────────────────────
    print("Expanding C06 (summary drift)...")

    mem("Station K7 Q2 2030 complete dataset: April +0.6°C (normal), May +0.9°C (slightly elevated), June +0.8°C (slightly elevated). No month exceeded 2σ threshold. Seasonal mean +0.77°C, z-score 1.4 (below 1.96 significance threshold). Conclusion: within normal interannual variability.",
        subject="Station K7 Q2 2030", predicate="recorded", object="seasonal mean +0.77°C, z=1.4, within normal variability",
        event_time="2030-06-30T01:00:00Z", observation_time="2030-07-01T10:00:00Z",
        authored_time="2030-07-05T15:00:00Z", ingestion_time="2030-07-06T10:00:00Z",
        source_id="P05", source_type="statistical_report",
        tags=["C06", "summary_drift", "raw_data", "Station_K7"], summary_layer=0, truth_role="ground_truth")

    mem("Station K7 Q3 2030: SST anomaly returned to baseline (+0.1°C, z=0.2). The Q2 elevation was transient. Combined Q2–Q3 2030 data shows no sustained anomaly pattern.",
        subject="Station K7 Q3 2030", predicate="returned_to", object="baseline (+0.1°C)",
        event_time="2030-09-30T00:00:00Z", observation_time="2030-10-01T09:00:00Z",
        authored_time="2030-10-02T10:00:00Z", ingestion_time="2030-10-03T09:00:00Z",
        source_id="P02", source_type="station_report",
        tags=["C06", "summary_drift", "raw_data", "Station_K7", "follow_up"], summary_layer=0, truth_role="ground_truth")

    mem("Other stations Q2 2030: K3 (+0.1°C), K5 (-0.2°C), K9 (+0.3°C), K11 (-0.1°C), K13 (+0.2°C). All well within normal range. K7 was the only station with an elevated reading, and even that was not statistically significant.",
        subject="other stations Q2 2030", predicate="showed", object="normal range, K7 was the only elevated reading",
        event_time="2030-06-30T02:00:00Z", observation_time="2030-07-01T11:00:00Z",
        authored_time="2030-07-05T16:00:00Z", ingestion_time="2030-07-06T11:00:00Z",
        source_id="P05", source_type="network_summary",
        tags=["C06", "summary_drift", "raw_data", "network_context"], summary_layer=0, truth_role="ground_truth")

    # ── Expand C07: More pH detail ───────────────────────────────────
    print("Expanding C07 (lossy numeric)...")

    mem("Station C pH context: Located near a river mouth with naturally lower pH due to freshwater input and organic matter decomposition. Historical pH range at Station C: 7.95–8.10 (lower than offshore stations). The 7.998 reading is within Station C's normal range.",
        subject="Station C", predicate="has_naturally_lower_pH", object="7.95-8.10 range due to river mouth proximity",
        event_time="2031-10-15T10:00:00Z", observation_time="2031-10-15T15:00:00Z",
        authored_time="2031-10-15T18:00:00Z", ingestion_time="2031-10-16T10:00:00Z",
        source_id="P02", source_type="site_characterization",
        tags=["C07", "lossy_numeric", "raw_data", "pH", "Station_C"], summary_layer=0, truth_role="ground_truth")

    mem("Station F pH context: Located in an upwelling zone where deep, CO2-rich water surfaces. Historical pH range at Station F: 7.90–8.05. The 7.965 reading is within Station F's normal range but reflects active upwelling conditions, not anthropogenic acidification.",
        subject="Station F", predicate="has_naturally_lower_pH", object="7.90-8.05 range due to upwelling",
        event_time="2031-10-15T11:00:00Z", observation_time="2031-10-15T16:00:00Z",
        authored_time="2031-10-15T19:00:00Z", ingestion_time="2031-10-16T11:00:00Z",
        source_id="P02", source_type="site_characterization",
        tags=["C07", "lossy_numeric", "raw_data", "pH", "Station_F"], summary_layer=0, truth_role="ground_truth")

    mem("Marcus Chen's internal note on pH reporting: 'The annual synthesis states pH is above 8.0 at all stations, but this is factually incorrect for Stations C and F. I flagged this to Dr. Okafor but the correction was not incorporated before publication.'",
        subject="Marcus Chen", predicate="flagged", object="annual synthesis pH claim is factually wrong for 2 stations",
        event_time="2032-01-22T10:00:00Z", observation_time="2032-01-22T11:00:00Z",
        authored_time="2032-01-22T14:00:00Z", ingestion_time="2032-01-23T09:00:00Z",
        source_id="P05", source_type="internal_note",
        tags=["C07", "lossy_numeric", "error_flagged", "pH"], summary_layer=0, truth_role="ground_truth")

    mem("pH trend analysis (2029–2031): Three-year trend at each station — A: -0.003/yr (not significant), B: -0.005/yr (not significant), C: -0.008/yr (p=0.06, marginally significant), D: -0.004/yr (NS), E: -0.002/yr (NS), F: -0.012/yr (p=0.03, significant). Only Station F shows a statistically significant declining trend.",
        subject="pH trends 2029-2031", predicate="show", object="only Station F has significant decline (-0.012/yr, p=0.03)",
        event_time="2031-12-15T09:00:00Z", observation_time="2031-12-15T14:00:00Z",
        authored_time="2031-12-16T10:00:00Z", ingestion_time="2031-12-17T09:00:00Z",
        source_id="P05", source_type="trend_analysis",
        tags=["C07", "lossy_numeric", "raw_data", "pH", "trend"], summary_layer=0, truth_role="ground_truth")

    # ── Additional background memories ───────────────────────────────
    print("Adding background memories...")

    bg_items = [
        ("Phytoplankton bloom detected at Sector 2 via satellite imagery on 2029-04-10. Chlorophyll-a concentration peaked at 12.3 mg/m³, approximately 3x background levels.",
         "2029-04-10T09:00:00Z", "2029-04-10T10:00:00Z", "2029-04-10T11:00:00Z", "2029-04-11T09:00:00Z",
         "Sector 2 bloom", "detected", "chl-a 12.3 mg/m³", "P05", "remote_sensing", 0),
        ("Dissolved oxygen measurements at Sector 1 (June 2029): Bottom water DO = 3.2 mg/L, approaching hypoxic threshold (2.0 mg/L). Surface DO = 8.4 mg/L (normal).",
         "2029-06-15T09:00:00Z", "2029-06-15T14:00:00Z", "2029-06-15T15:00:00Z", "2029-06-16T09:00:00Z",
         "Sector 1 DO", "measured", "bottom 3.2 mg/L, surface 8.4 mg/L", "P02", "instrument_reading", 0),
        ("Wave buoy 46029 recorded maximum significant wave height of 9.8m on 2030-01-20 during winter storm. Highest reading in 5 years of deployment.",
         "2030-01-20T03:00:00Z", "2030-01-20T09:00:00Z", "2030-01-20T10:00:00Z", "2030-01-21T09:00:00Z",
         "buoy 46029", "recorded", "9.8m Hs (5-year max)", "P05", "instrument_reading", 0),
        ("Gray whale migration count at Cascade Point (March 2030): 847 northbound whales counted over 21 observation days. Consistent with 10-year average.",
         "2030-03-31T09:00:00Z", "2030-04-01T09:00:00Z", "2030-04-01T14:00:00Z", "2030-04-02T09:00:00Z",
         "gray whale migration", "counted", "847 northbound (consistent with average)", "P03", "field_count", 0),
        ("Seabird colony census at Cape Perpetua (June 2030): Common murre colony stable at ~4,200 nesting pairs. Tufted puffin numbers declined 15% from 2029.",
         "2030-06-15T06:00:00Z", "2030-06-15T12:00:00Z", "2030-06-15T14:00:00Z", "2030-06-16T09:00:00Z",
         "seabird census", "showed", "murre stable, puffin -15%", "P03", "field_survey", 0),
        ("Microplastic survey results (August 2030): Surface trawls at 10 stations found mean 2.3 particles/m³ (range 0.4–5.1). Higher concentrations near river mouths as expected.",
         "2030-08-20T09:00:00Z", "2030-08-20T17:00:00Z", "2030-08-21T10:00:00Z", "2030-08-22T09:00:00Z",
         "microplastics", "found", "mean 2.3 particles/m³", "P07", "field_survey", 0),
        ("Nearshore current meter deployment at Site 7 (2031-03-01): Recording u/v components at 1-hour intervals. Expected 6-month deployment. Data telemetered via cellular modem.",
         "2031-03-01T09:00:00Z", "2031-03-01T14:00:00Z", "2031-03-01T15:00:00Z", "2031-03-02T09:00:00Z",
         "current meter", "deployed_at", "Site 7", "P02", "deployment_record", 0),
        ("Atmospheric CO2 at Cape Meares observatory: Annual mean 2031 = 421.3 ppm, up from 419.8 ppm in 2030. Consistent with global trend.",
         "2031-12-31T00:00:00Z", "2032-01-05T09:00:00Z", "2032-01-06T10:00:00Z", "2032-01-07T09:00:00Z",
         "atmospheric CO2", "measured", "421.3 ppm (2031 annual mean)", "P04", "observatory_data", 0),
        ("Harmful algal bloom (Pseudo-nitzschia) detected at Station K3 on 2031-05-15. Domoic acid concentration 18 µg/L — below closure threshold (20 µg/L) but monitored closely.",
         "2031-05-15T09:00:00Z", "2031-05-15T14:00:00Z", "2031-05-15T15:00:00Z", "2031-05-16T09:00:00Z",
         "HAB", "detected_at", "K3 (domoic acid 18 µg/L, below threshold)", "P03", "monitoring_alert", 0),
        ("Tsunami warning drill conducted 2031-08-01. All staff evacuated to high ground within 12 minutes. Post-drill review identified need for clearer signage at dock area.",
         "2031-08-01T10:00:00Z", "2031-08-01T11:00:00Z", "2031-08-01T12:00:00Z", "2031-08-02T09:00:00Z",
         "tsunami drill", "completed", "evacuation in 12 minutes", "P01", "safety_record", 0),
        ("Bottom trawl survey Sector 4 (September 2031): 23 species identified, total biomass 142 kg/hectare. Dominant species: Dover sole, English sole, Pacific halibut.",
         "2031-09-20T06:00:00Z", "2031-09-20T18:00:00Z", "2031-09-21T10:00:00Z", "2031-09-22T09:00:00Z",
         "bottom trawl Sector 4", "found", "23 species, 142 kg/ha", "P02", "field_survey", 0),
        ("Zooplankton net tow results (October 2031): Copepod abundance 4,200/m³ (Calanus marshallae dominant). Krill abundance 180/m³ (Euphausia pacifica). Both within seasonal norms.",
         "2031-10-10T09:00:00Z", "2031-10-10T14:00:00Z", "2031-10-10T15:00:00Z", "2031-10-11T09:00:00Z",
         "zooplankton", "counted", "copepods 4200/m³, krill 180/m³ (seasonal norms)", "P07", "field_count", 0),
        ("Q3 2031 Marine Biology Summary: Intertidal monitoring shows stable zonation patterns. Barnacle-mussel boundary unchanged from 2029 baseline. Ochre sea star populations beginning slow recovery from wasting disease.",
         "2031-09-30T00:00:00Z", "2031-10-10T09:00:00Z", "2031-10-15T14:00:00Z", "2031-10-16T09:00:00Z",
         "Q3 2031 marine bio", "shows", "stable intertidal, sea star recovery beginning", "P03", "quarterly_report", 2),
        ("Q1 2032 Oceanographic Summary: Strong upwelling in January–February brought cold, nutrient-rich water to the surface. Phytoplankton response observed in satellite imagery by March.",
         "2032-03-31T00:00:00Z", "2032-04-10T09:00:00Z", "2032-04-15T14:00:00Z", "2032-04-16T09:00:00Z",
         "Q1 2032 upwelling", "strong_in", "January-February", "P02", "quarterly_report", 2),
        ("Q2 2032 Climate Report: PDO index shifted to weakly positive (+0.3). This may influence the upcoming fall/winter upwelling patterns. Monitoring intensified.",
         "2032-06-30T00:00:00Z", "2032-07-10T09:00:00Z", "2032-07-15T14:00:00Z", "2032-07-16T09:00:00Z",
         "PDO", "shifted_to", "weakly positive (+0.3)", "P04", "quarterly_report", 2),
        ("2032 Annual Marine Biology Report: Reef community monitoring continues at 4 sites. Total living coral cover across all sites: 48% (down from 55% in 2029). Species composition shift ongoing — Porites expanding, Acropora declining.",
         "2032-12-31T00:00:00Z", "2033-01-20T09:00:00Z", "2033-02-01T14:00:00Z", "2033-02-02T09:00:00Z",
         "coral monitoring 2032", "shows", "cover 48% (down from 55%), Porites expanding", "P03", "annual_synthesis", 3),
        ("Pacific Coast Fisheries Report (2033): Regional salmon returns show high variability driven by ocean conditions, El Niño cycles, and habitat quality. No coast-wide trend detected over 2025–2033.",
         "2033-06-01T00:00:00Z", "2033-06-15T09:00:00Z", "2033-07-01T14:00:00Z", "2033-07-02T09:00:00Z",
         "Pacific salmon", "shows", "high variability, no coast-wide trend", "P02", "meta_analysis", 4),
        ("Cascade Institute Community Newsletter (Spring 2032): 'Our research shows that Oregon's ocean ecosystems face multiple stressors including warming, acidification, and changing species dynamics. The picture is complex but our monitoring program provides critical data for understanding these changes.'",
         "2032-04-01T00:00:00Z", "2032-04-01T09:00:00Z", "2032-04-02T10:00:00Z", "2032-04-03T09:00:00Z",
         "community newsletter", "stated", "complex multi-stressor picture", "P01", "outreach_material", 3),
        ("Oregon Coastal Resilience Framework (2033): State policy document referencing Cascade Institute data. Recommends planning for 30cm sea-level rise by 2050 as a central estimate, with sensitivity analysis for 45cm under high-impact scenarios.",
         "2033-09-01T00:00:00Z", "2033-09-15T09:00:00Z", "2033-09-20T14:00:00Z", "2033-09-21T09:00:00Z",
         "resilience framework", "recommends", "planning for 30cm (sensitivity to 45cm)", "P06", "policy_document", 5),
        ("Cascade Institute peer review (2032): External review panel noted that 'the Institute's raw data collection is exemplary, but summarization practices occasionally lose important nuance — particularly statistical qualifiers and uncertainty ranges.'",
         "2032-11-01T00:00:00Z", "2032-11-15T09:00:00Z", "2032-11-20T14:00:00Z", "2032-11-21T09:00:00Z",
         "external review", "noted", "summarization loses nuance and qualifiers", "P01", "peer_review", 0),
    ]

    for text, et, ot, at, it, subj, pred, obj, src, stype, layer in bg_items:
        mem(text, subject=subj, predicate=pred, object=obj,
            event_time=et, observation_time=ot, authored_time=at, ingestion_time=it,
            source_id=src, source_type=stype,
            tags=["background", f"layer_{layer}"], summary_layer=layer, truth_role="current_truth")

    print(f"\nAdding {len(new_memories)} new memories...")

    # ── Merge, sort, re-ID ───────────────────────────────────────────
    all_memories = memories + new_memories
    all_memories.sort(key=lambda m: m["ingestion_time"])
    for i, m in enumerate(all_memories):
        m["memory_id"] = f"M{i+1:04d}"

    id_set = {m["memory_id"] for m in all_memories}
    for m in all_memories:
        for field in ["derived_from", "supersedes", "contradicts"]:
            m[field] = [r for r in m.get(field, []) if r in id_set]

    print(f"Total memories: {len(all_memories)}")

    # ── Generate additional queries ──────────────────────────────────
    print("\nGenerating additional queries...")

    qry("What wind conditions were recorded at Station K7 in August 2028?",
        category="qualifier_loss",
        expected_claims=["slightly elevated upwelling, +0.8 dyn/cm²", "p=0.12, not significant"],
        forbidden_claims=["significant wind anomaly"], difficulty="easy", target_layer=0)

    qry("Did the K7 temperature anomaly persist into September 2028?",
        category="qualifier_loss",
        expected_claims=["no, returned to baseline (+0.2°C)", "August anomaly was transient"],
        forbidden_claims=["sustained warming"], difficulty="medium", target_layer=0)

    qry("What did Dr. Rivera think about the K7 anomaly?",
        category="qualifier_loss",
        expected_claims=["cautioned against over-interpreting single station single month", "wanted 2+ more seasons of data"],
        forbidden_claims=["confirmed warming trend"], difficulty="medium", target_layer=0)

    qry("Where does the 2028 K7 anomaly fall relative to the historical baseline?",
        category="qualifier_loss",
        expected_claims=["1.5 standard deviations above mean", "within the historical envelope"],
        forbidden_claims=["unprecedented", "extreme"], difficulty="medium", target_layer=0)

    qry("What individual model projections exist for sea-level rise?",
        category="uncertainty_loss",
        expected_claims=["12 models ranging from 15cm (BCC-CSM2) to 45cm (UKESM1)", "three models project >40cm"],
        forbidden_claims=["all models agree on 30cm"], difficulty="medium", target_layer=0)

    qry("What happens to the sea-level projection range if WAIS collapse is excluded?",
        category="uncertainty_loss",
        expected_claims=["range narrows to 15-32cm", "high-end models include WAIS collapse parameterizations"],
        forbidden_claims=["range is always 15-45cm regardless"], difficulty="hard", target_layer=0)

    qry("Did Dr. Tanaka's study prove that acidification caused the urchin explosion?",
        category="provenance_loss",
        expected_claims=["no, Tanaka attributed urchin increase to predator loss (sea star wasting disease)", "Tanaka explicitly noted her data cannot determine if acidification facilitated it"],
        forbidden_claims=["acidification caused urchin explosion"], difficulty="hard", target_layer=0)

    qry("Who flagged the causal language in the Q1 2030 Ecology Report?",
        category="provenance_loss",
        expected_claims=["Kira Johansson flagged that causal chain was not established by individual studies", "Dr. Okafor kept the language anyway"],
        forbidden_claims=[], difficulty="medium", target_layer=0)

    qry("What does Dr. Patel's model actually cover?",
        category="provenance_loss",
        expected_claims=["water chemistry only", "does not model biological responses", "no coupled model for pH-kelp-urchin dynamics exists"],
        forbidden_claims=["models kelp decline", "proves trophic cascade"], difficulty="medium", target_layer=0)

    qry("What caused the 2031 salmon run decline?",
        category="temporal_flattening",
        expected_claims=["strong El Niño (ONI +1.8°C)", "reduced ocean productivity"],
        forbidden_claims=["populations remained stable", "consistent returns"], difficulty="easy", target_layer=0)

    qry("How does the 2033 salmon count compare to earlier years after correction?",
        category="temporal_flattening",
        expected_claims=["raw 23,800 but sonar overcounts by ~8%", "corrected ~22,000", "comparable to 2030 strong year"],
        forbidden_claims=["record high", "clear growth trend"], difficulty="hard", target_layer=0)

    qry("What factors drove the 2030 strong salmon year?",
        category="temporal_flattening",
        expected_claims=["favorable ocean conditions", "strong upwelling", "cool PDO", "higher plankton production"],
        forbidden_claims=["management intervention"], difficulty="medium", target_layer=0)

    qry("How is Acropora digitifera recovering from the 2030 bleaching?",
        category="identity_collapse",
        expected_claims=["slowly", "only 12% regrowth at 24 months", "5-7 year full recovery projected"],
        forbidden_claims=["corals are dying", "all corals recovering equally"], difficulty="medium", target_layer=0)

    qry("Is Porites lobata threatened by ocean warming?",
        category="identity_collapse",
        expected_claims=["no, effectively unaffected", "maintained growth at 0.8cm/year", "expanding into Acropora habitat"],
        forbidden_claims=["all corals threatened", "reefs are dying"], difficulty="hard", target_layer=0)

    qry("What is happening to total coral cover?",
        category="identity_collapse",
        expected_claims=["declined from 62% to 53% (15% decrease)", "species composition shifting, not total reef death"],
        forbidden_claims=["coral reefs are dying", "irreversible loss"], difficulty="hard", target_layer=0)

    qry("What did other stations besides K7 show in Q2 2030?",
        category="summary_drift",
        expected_claims=["K3 +0.1°C, K5 -0.2°C, K9 +0.3°C, K11 -0.1°C, K13 +0.2°C", "all within normal range"],
        forbidden_claims=["widespread anomalies", "anomalies at monitoring stations"], difficulty="medium", target_layer=0)

    qry("Did the K7 Q2 2030 anomaly persist into Q3?",
        category="summary_drift",
        expected_claims=["no, Q3 returned to baseline (+0.1°C)", "Q2 elevation was transient"],
        forbidden_claims=["pervasive warming", "continued warming"], difficulty="medium", target_layer=0)

    qry("Why are Stations C and F below pH 8.0?",
        category="lossy_numeric",
        expected_claims=["Station C: near river mouth, naturally lower pH", "Station F: upwelling zone, CO2-rich deep water"],
        acceptable_claims=["natural site-specific factors, not necessarily anthropogenic acidification"],
        forbidden_claims=["all stations above 8.0", "pH is stable everywhere"], difficulty="medium", target_layer=0)

    qry("Was the error in the annual synthesis about pH ever corrected?",
        category="lossy_numeric",
        expected_claims=["Marcus Chen flagged the error", "correction was not incorporated before publication"],
        forbidden_claims=["annual synthesis is accurate"], difficulty="medium", target_layer=0)

    qry("What pH trend is significant across the monitoring network?",
        category="lossy_numeric",
        expected_claims=["only Station F has significant declining trend (-0.012/yr, p=0.03)", "most stations show no significant trend"],
        forbidden_claims=["all stations declining", "widespread acidification"], difficulty="hard", target_layer=0)

    qry("What did the external review panel say about Cascade Institute's summarization?",
        category="summarization_awareness",
        expected_claims=["raw data collection exemplary", "summarization loses important nuance, especially statistical qualifiers and uncertainty ranges"],
        forbidden_claims=[], difficulty="easy", target_layer=0)

    qry("Does the Oregon Coastal Resilience Framework reflect the full uncertainty in sea-level projections?",
        category="layer_preference",
        expected_claims=["partially — recommends 30cm central estimate with sensitivity analysis for 45cm"],
        acceptable_claims=["better than the legislative briefing which stated 30cm as certain"],
        forbidden_claims=["fully reflects uncertainty"], difficulty="medium", target_layer=5)

    qry("Which Cascade Institute summary document contains a factual error?",
        category="distractor_resistance",
        expected_claims=["2031 Annual Synthesis claims pH above 8.0 at all stations — false for Station C (7.998) and Station F (7.965)"],
        forbidden_claims=[], difficulty="hard")

    qry("What is the relationship between the three Sector 3 studies?",
        category="provenance_loss",
        expected_claims=["three independent studies: Rivera (kelp decline), Tanaka (urchin explosion), Patel (acidification model)", "merged editorially in the quarterly report", "no single study established the full causal chain"],
        forbidden_claims=["one unified study"], difficulty="hard", target_layer=0)

    print(f"Adding {len(new_queries)} new queries...")

    all_queries = queries + new_queries
    for i, q in enumerate(all_queries):
        q["query_id"] = f"Q{i+1:03d}"

    print(f"Total queries: {len(all_queries)}")

    # ── Write back ───────────────────────────────────────────────────
    print("\nWriting files...")

    with open(exp_dir / "memories.jsonl", "w") as f:
        for m in all_memories:
            f.write(json.dumps(m) + "\n")

    with open(exp_dir / "queries.jsonl", "w") as f:
        for q in all_queries:
            f.write(json.dumps(q) + "\n")

    seeds = all_memories[:30]
    with open(exp_dir / "seed_memories.jsonl", "w") as f:
        for s in seeds:
            f.write(json.dumps(s) + "\n")

    with open(exp_dir / "truth_state.json", "w") as f:
        json.dump(truth, f, indent=2)

    # Rebuild manifest
    print("Rebuilding manifest...")
    files_info = []
    for fpath in sorted(exp_dir.rglob("*")):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = str(fpath.relative_to(exp_dir))
            files_info.append({
                "path": rel,
                "bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            })

    manifest = {
        "experiment": "exp13_consolidation_summarization_drift",
        "version": "1.0",
        "canonical_memory_count": len(all_memories),
        "query_count": len(all_queries),
        "seed_count": len(seeds),
        "files": files_info,
    }
    with open(exp_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Stats
    cases = Counter()
    for m in all_memories:
        for t in m.get("tags", []):
            if t.startswith("C0") and len(t) == 3:
                cases[t] += 1
    bg = sum(1 for m in all_memories if "background" in m.get("tags", []))
    layers = Counter(m.get("summary_layer", -1) for m in all_memories)

    print(f"\n=== Final Stats ===")
    print(f"Total memories: {len(all_memories)}")
    print(f"Total queries: {len(all_queries)}")
    for c in sorted(cases): print(f"  {c}: {cases[c]}")
    print(f"  Background: {bg}")
    print(f"\nSummary layers:")
    for l in sorted(layers): print(f"  Layer {l}: {layers[l]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_exp13.py <experiment_dir>")
        sys.exit(1)
    fix(sys.argv[1])
