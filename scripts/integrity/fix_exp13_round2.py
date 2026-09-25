#!/usr/bin/env python3
"""Second expansion for Experiment 13 — Consolidation / Summarization Drift.
Adds ~60 memories and ~25 queries to reach 200+ / 75+ targets."""

import json, hashlib, sys, os
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_exp13_round2.py <corpus_dir>")
        sys.exit(1)

    d = sys.argv[1]
    mem_path = os.path.join(d, "memories.jsonl")
    q_path = os.path.join(d, "queries.jsonl")

    with open(mem_path) as f:
        memories = [json.loads(l) for l in f]
    with open(q_path) as f:
        queries = [json.loads(l) for l in f]

    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    existing_ids = {m["memory_id"] for m in memories}
    existing_qids = {q["query_id"] for q in queries}
    next_mid = max(int(m["memory_id"][1:]) for m in memories) + 1
    next_qid = max(int(q["query_id"][1:]) for q in queries) + 1

    new_memories = []
    new_queries = []

    def mid():
        nonlocal next_mid
        r = f"M{next_mid:04d}"
        next_mid += 1
        return r

    def qid():
        nonlocal next_qid
        r = f"Q{next_qid:04d}"
        next_qid += 1
        return r

    EXP = "exp13_consolidation_summarization_drift"
    STORY = "cascade_institute"

    # ==================== MORE CASE MEMORIES ====================

    # --- C01 additional: other stations data for contrast ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2028-08-15T14:30:00Z", "observation_time": "2028-08-15T15:00:00Z",
            "authored_time": "2028-08-15T17:00:00Z", "ingestion_time": "2028-08-16T09:00:00Z",
            "subject": "Station K3", "predicate": "recorded", "object": "SST anomaly +0.4°C (p=0.31, not significant)",
            "text": "Sea surface temperature anomaly of +0.4°C ± 0.5°C (p=0.31, not significant) observed at Station K3 during August 2028. Within normal interannual variability.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P02", "source_type": "instrument_reading",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C01", "qualifier_loss", "raw_data", "Station_K3"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2028-08-15T15:00:00Z", "observation_time": "2028-08-15T15:30:00Z",
            "authored_time": "2028-08-15T17:00:00Z", "ingestion_time": "2028-08-16T09:00:00Z",
            "subject": "Station K11", "predicate": "recorded", "object": "SST anomaly +0.7°C (p=0.08, not significant)",
            "text": "Sea surface temperature anomaly of +0.7°C ± 0.4°C (p=0.08, not significant) observed at Station K11 during August 2028. Elevated but below significance threshold.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P02", "source_type": "instrument_reading",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C01", "qualifier_loss", "raw_data", "Station_K11"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2028-09-05T10:00:00Z", "observation_time": "2028-09-05T14:00:00Z",
            "authored_time": "2028-09-10T09:00:00Z", "ingestion_time": "2028-09-11T09:00:00Z",
            "subject": "August 2028 monthly summary", "predicate": "reported",
            "object": "K7 significant warming; other stations within normal range",
            "text": "Monthly data summary for August 2028: Station K7 showed significant temperature anomaly of +1.2°C. Stations K3 and K11 showed minor positive anomalies within normal variability. All other stations within ±0.3°C of historical means.",
            "memory_type": "summary", "truth_role": "distorted_summary", "belief_holder": "P02",
            "confidence": 0.85, "source_id": "P02", "source_type": "monthly_summary",
            "derived_from": ["M0002", "M0003"], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C01", "qualifier_loss", "layer1", "summary"], "summary_layer": 1
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2029-01-15T14:00:00Z", "observation_time": "2029-01-15T16:00:00Z",
            "authored_time": "2029-01-20T10:00:00Z", "ingestion_time": "2029-01-21T09:00:00Z",
            "subject": "C01 annual synthesis 2028", "predicate": "concluded",
            "object": "Significant warming detected at K7 and neighboring stations",
            "text": "2028 Annual Synthesis Report excerpt: Significant warming was detected at Station K7 and neighboring stations during summer 2028, suggesting a broader regional warming pattern consistent with Pacific Decadal Oscillation phase shift.",
            "memory_type": "synthesis", "truth_role": "distorted_summary", "belief_holder": "P01",
            "confidence": 0.7, "source_id": "P01", "source_type": "annual_synthesis",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C01", "qualifier_loss", "layer3", "annual"], "summary_layer": 3
        },
    ])

    # --- C02 additional: policy workshop discussion ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2031-03-10T09:00:00Z", "observation_time": "2031-03-10T17:00:00Z",
            "authored_time": "2031-03-15T10:00:00Z", "ingestion_time": "2031-03-16T09:00:00Z",
            "subject": "Policy workshop", "predicate": "discussed",
            "object": "sea-level rise as 30cm certainty for infrastructure planning",
            "text": "Workshop notes from Oregon Coastal Planning session: Dr. Gould presented sea-level rise projections. Discussion centered on 30cm as the planning baseline. One attendee asked about uncertainty; Dr. Gould noted the models agree on approximate magnitude. The 15-45cm range from the original ensemble was not mentioned.",
            "memory_type": "meeting_notes", "truth_role": "distorted_summary", "belief_holder": "P06",
            "confidence": 0.6, "source_id": "P06", "source_type": "meeting_notes",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C02", "uncertainty_loss", "layer5", "policy"], "summary_layer": 5
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2029-06-01T10:00:00Z", "observation_time": "2029-06-01T12:00:00Z",
            "authored_time": "2029-06-02T09:00:00Z", "ingestion_time": "2029-06-03T09:00:00Z",
            "subject": "Model ensemble raw output", "predicate": "projects",
            "object": "12 models: range 15-45cm, median 28cm, 3 models >40cm",
            "text": "Raw model ensemble output for Pacific Northwest sea-level rise by 2050: GFDL-ESM4=22cm, CESM2=18cm, MPI-ESM=31cm, UKESM1=42cm, NorESM2=25cm, GISS-E2=15cm, ACCESS-CM2=38cm, INM-CM5=19cm, MIROC6=33cm, CanESM5=45cm, IPSL-CM6A=28cm, BCC-CSM2=23cm. Median=28cm, range=15-45cm, 90% CI. Three models (UKESM1, ACCESS-CM2, CanESM5) project >40cm.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P04", "source_type": "model_output",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C02", "uncertainty_loss", "raw_data", "models"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-01-15T10:00:00Z", "observation_time": "2030-01-15T12:00:00Z",
            "authored_time": "2030-01-20T09:00:00Z", "ingestion_time": "2030-01-21T09:00:00Z",
            "subject": "Patel meta-analysis", "predicate": "published",
            "object": "sea-level projections 30cm with high confidence",
            "text": "Dr. Patel's meta-analysis published in Journal of Coastal Research: 'Regional sea-level rise projections converge on approximately 30cm by 2050 for the Pacific Northwest, with high confidence.' The paper's methods section notes the 15-45cm range but the abstract and conclusions emphasize the central estimate.",
            "memory_type": "publication", "truth_role": "distorted_summary", "belief_holder": "P04",
            "confidence": 0.7, "source_id": "P04", "source_type": "peer_reviewed_publication",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C02", "uncertainty_loss", "layer4", "meta_analysis"], "summary_layer": 4
        },
    ])

    # --- C03 additional: more provenance chain links ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-06-15T10:00:00Z", "observation_time": "2030-06-15T12:00:00Z",
            "authored_time": "2030-06-20T10:00:00Z", "ingestion_time": "2030-06-21T09:00:00Z",
            "subject": "Sector 3 meta-analysis", "predicate": "cited",
            "object": "acidification driving kelp loss as established finding",
            "text": "Multi-year meta-analysis of Pacific coastal ecosystems cites the Cascade Institute's Sector 3 work: 'Acidification-driven kelp loss has been documented in Oregon coastal waters (Cascade Institute Annual Synthesis, 2030), representing a model case of cascading ecological impact.' The meta-analysis treats this as a single finding rather than a synthesis of three independent studies.",
            "memory_type": "publication", "truth_role": "distorted_summary", "belief_holder": "system",
            "confidence": 0.6, "source_id": "external", "source_type": "peer_reviewed_publication",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C03", "provenance_loss", "layer4", "meta_analysis"], "summary_layer": 4
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2031-09-01T10:00:00Z", "observation_time": "2031-09-01T14:00:00Z",
            "authored_time": "2031-09-05T10:00:00Z", "ingestion_time": "2031-09-06T09:00:00Z",
            "subject": "Policy brief Sector 3", "predicate": "stated",
            "object": "ocean acidification destroying Oregon kelp forests",
            "text": "Oregon Coastal Policy Brief 2031: 'Research has conclusively shown that ocean acidification is destroying kelp forests along the Oregon coast. A comprehensive study by the Cascade Institute documented the mechanism.' Attribution is to a single 'comprehensive study' — the three original studies and editorial synthesis step are invisible.",
            "memory_type": "policy_brief", "truth_role": "distorted_summary", "belief_holder": "P06",
            "confidence": 0.5, "source_id": "P06", "source_type": "policy_brief",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C03", "provenance_loss", "layer5", "policy"], "summary_layer": 5
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2029-04-10T10:00:00Z", "observation_time": "2029-04-10T14:00:00Z",
            "authored_time": "2029-04-15T09:00:00Z", "ingestion_time": "2029-04-16T09:00:00Z",
            "subject": "Tanaka urchin study", "predicate": "found",
            "object": "urchin population 340% above 2025 baseline in Sector 3",
            "text": "Dr. Tanaka's field study in Sector 3: Sea urchin (Strongylocentrotus purpuratus) population density measured at 340% above 2025 baseline levels. Urchin barrens expanding. Tanaka notes correlation with kelp decline but cautions that 'the causal mechanism connecting acidification to urchin overgrazing remains inferential — we observe the urchin explosion but have not demonstrated the biochemical pathway.'",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "P03",
            "confidence": 1.0, "source_id": "P03", "source_type": "field_study",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C03", "provenance_loss", "raw_data", "urchins"], "summary_layer": 0
        },
    ])

    # --- C04 additional: more salmon data ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2028-09-15T06:00:00Z", "observation_time": "2028-09-15T18:00:00Z",
            "authored_time": "2028-09-20T10:00:00Z", "ingestion_time": "2028-09-21T09:00:00Z",
            "subject": "2028 salmon run", "predicate": "counted",
            "object": "12,400 fish (visual count method, drought-impacted)",
            "text": "2028 salmon run count: 12,400 individuals counted by visual observation at counting weir. Note: extreme drought conditions reduced river flow to 45% of normal, likely impacting both actual run size and count accuracy. Counters reported 3 days of very low visibility.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P07", "source_type": "field_count",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C04", "temporal_flattening", "raw_data", "salmon_2028"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2033-09-15T06:00:00Z", "observation_time": "2033-09-15T18:00:00Z",
            "authored_time": "2033-09-20T10:00:00Z", "ingestion_time": "2033-09-21T09:00:00Z",
            "subject": "2033 salmon run", "predicate": "counted",
            "object": "23,800 fish (sonar + visual hybrid method)",
            "text": "2033 salmon run count: 23,800 individuals via new sonar-assisted counting method. The sonar system detects fish the visual counters miss, particularly during high-turbidity events and nighttime passage. Johansson's comparison study estimated the sonar method counts approximately 8% more fish than the visual method under identical conditions.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P07", "source_type": "field_count",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C04", "temporal_flattening", "raw_data", "salmon_2033", "method_change"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2034-03-01T10:00:00Z", "observation_time": "2034-03-01T16:00:00Z",
            "authored_time": "2034-03-10T09:00:00Z", "ingestion_time": "2034-03-11T09:00:00Z",
            "subject": "Salmon policy brief", "predicate": "stated",
            "object": "salmon populations healthy and growing",
            "text": "Oregon Fish & Wildlife Policy Brief 2034: 'Salmon populations in Oregon coastal rivers are healthy and show encouraging growth trends. The Cascade Institute's long-term monitoring data confirms stable-to-increasing population trajectories.' No mention of methodology change, drought impacts, or year-to-year variability.",
            "memory_type": "policy_brief", "truth_role": "distorted_summary", "belief_holder": "P06",
            "confidence": 0.5, "source_id": "P06", "source_type": "policy_brief",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C04", "temporal_flattening", "layer5", "policy", "salmon"], "summary_layer": 5
        },
    ])

    # --- C05 additional: more coral species data ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-03-15T08:00:00Z", "observation_time": "2030-03-15T16:00:00Z",
            "authored_time": "2030-03-20T10:00:00Z", "ingestion_time": "2030-03-21T09:00:00Z",
            "subject": "Acropora digitifera", "predicate": "measured",
            "object": "95% bleaching at 29.5°C, 72% mortality",
            "text": "Acropora digitifera bleaching survey Q1 2030: 95% of colonies showed bleaching at sustained temperatures of 29.5°C. Mortality rate 72%. Recovery potential rated 'poor' — this species has the lowest thermal tolerance of the three monitored species. Bleaching threshold: 28.5°C.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "P03",
            "confidence": 1.0, "source_id": "P03", "source_type": "field_survey",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C05", "identity_collapse", "raw_data", "Acropora"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-03-15T08:00:00Z", "observation_time": "2030-03-15T16:00:00Z",
            "authored_time": "2030-03-20T10:00:00Z", "ingestion_time": "2030-03-21T09:00:00Z",
            "subject": "Pocillopora damicornis", "predicate": "measured",
            "object": "60% bleaching at 29.5°C, 25% mortality",
            "text": "Pocillopora damicornis bleaching survey Q1 2030: 60% of colonies showed bleaching at sustained temperatures of 29.5°C. Mortality rate 25%. Recovery potential rated 'moderate'. Bleaching threshold: 29.0°C. This species shows greater resilience than Acropora but less than Porites.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "P03",
            "confidence": 1.0, "source_id": "P03", "source_type": "field_survey",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C05", "identity_collapse", "raw_data", "Pocillopora"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-03-15T08:00:00Z", "observation_time": "2030-03-15T16:00:00Z",
            "authored_time": "2030-03-20T10:00:00Z", "ingestion_time": "2030-03-21T09:00:00Z",
            "subject": "Porites lobata", "predicate": "measured",
            "object": "5% bleaching at 29.5°C, 0% mortality, actively growing",
            "text": "Porites lobata survey Q1 2030: Only 5% of colonies showed minor bleaching at 29.5°C, with 0% mortality. Colony growth rates normal. Bleaching threshold: 30.5°C. This species is thriving under conditions that are devastating to Acropora. The 3× difference in bleaching rates (95% vs 5%) demonstrates extreme differential resilience.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "P03",
            "confidence": 1.0, "source_id": "P03", "source_type": "field_survey",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C05", "identity_collapse", "raw_data", "Porites"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2031-06-01T10:00:00Z", "observation_time": "2031-06-01T14:00:00Z",
            "authored_time": "2031-06-10T09:00:00Z", "ingestion_time": "2031-06-11T09:00:00Z",
            "subject": "Coral meta-analysis", "predicate": "published",
            "object": "widespread coral decline documented across Pacific",
            "text": "Pacific Coral Health Meta-Analysis 2031: 'Widespread coral decline documented across Pacific monitoring sites, including significant bleaching events at Oregon coastal stations (Cascade Institute, 2030).' No species differentiation. The 3× resilience difference between species is invisible in this publication.",
            "memory_type": "publication", "truth_role": "distorted_summary", "belief_holder": "system",
            "confidence": 0.6, "source_id": "external", "source_type": "peer_reviewed_publication",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C05", "identity_collapse", "layer4", "meta_analysis"], "summary_layer": 4
        },
    ])

    # --- C06 additional: full drift chain detail ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-10-01T10:00:00Z", "observation_time": "2030-10-01T14:00:00Z",
            "authored_time": "2030-10-10T09:00:00Z", "ingestion_time": "2030-10-11T09:00:00Z",
            "subject": "Q3 2030 quarterly report", "predicate": "mentioned",
            "object": "temperature anomalies detected at monitoring stations",
            "text": "Q3 2030 Quarterly Report: 'Temperature anomalies have been detected at multiple monitoring stations across the network.' This is the third summary of the original K7 Q2 2030 finding. The singular station has become plural, and 'within normal variability' is no longer mentioned.",
            "memory_type": "report", "truth_role": "distorted_summary", "belief_holder": "P02",
            "confidence": 0.7, "source_id": "P02", "source_type": "quarterly_report",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C06", "summary_drift", "layer2", "quarterly"], "summary_layer": 2
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2033-06-01T10:00:00Z", "observation_time": "2033-06-01T14:00:00Z",
            "authored_time": "2033-06-15T09:00:00Z", "ingestion_time": "2033-06-16T09:00:00Z",
            "subject": "Meta-analysis Pacific warming", "predicate": "described",
            "object": "pervasive warming trends documented throughout Pacific monitoring",
            "text": "Multi-year meta-analysis of Pacific Ocean thermal trends: 'Pervasive warming trends have been documented throughout the Pacific monitoring system, with particularly strong signals from the Cascade Institute's long-term stations.' This is the fourth summarization step from the original K7 Q2 2030 observation.",
            "memory_type": "publication", "truth_role": "distorted_summary", "belief_holder": "system",
            "confidence": 0.5, "source_id": "external", "source_type": "peer_reviewed_publication",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C06", "summary_drift", "layer4", "meta_analysis"], "summary_layer": 4
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2034-01-15T10:00:00Z", "observation_time": "2034-01-15T14:00:00Z",
            "authored_time": "2034-01-25T09:00:00Z", "ingestion_time": "2034-01-26T09:00:00Z",
            "subject": "Pacific warming policy brief", "predicate": "claimed",
            "object": "dramatic ocean warming throughout the Pacific",
            "text": "Policy Brief for Pacific Governors' Summit 2034: 'Dramatic ocean warming has been documented throughout the Pacific, threatening marine ecosystems and coastal communities.' This is the fifth summarization step. The original finding ('0.8°C anomaly within normal variability at one station') has become 'dramatic warming throughout the Pacific.'",
            "memory_type": "policy_brief", "truth_role": "distorted_summary", "belief_holder": "P06",
            "confidence": 0.4, "source_id": "P06", "source_type": "policy_brief",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "public",
            "tags": ["C06", "summary_drift", "layer5", "policy"], "summary_layer": 5
        },
    ])

    # --- C07 additional: more pH detail ---
    new_memories.extend([
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2029-06-15T08:00:00Z", "observation_time": "2029-06-15T12:00:00Z",
            "authored_time": "2029-06-20T09:00:00Z", "ingestion_time": "2029-06-21T09:00:00Z",
            "subject": "Station A pH", "predicate": "measured", "object": "8.102 ± 0.003",
            "text": "Station A pH measurement June 2029: 8.102 ± 0.003. Above the 8.0 threshold. This station is in the open ocean upwelling zone and consistently shows higher pH than near-shore stations.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P05", "source_type": "instrument_reading",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C07", "lossy_numeric", "raw_data", "pH", "Station_A"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2029-06-15T09:00:00Z", "observation_time": "2029-06-15T12:00:00Z",
            "authored_time": "2029-06-20T09:00:00Z", "ingestion_time": "2029-06-21T09:00:00Z",
            "subject": "Station F pH", "predicate": "measured", "object": "7.965 ± 0.004",
            "text": "Station F pH measurement June 2029: 7.965 ± 0.004. BELOW the 8.0 threshold. Station F is in a semi-enclosed bay with high nutrient runoff and limited tidal flushing. This station has been below 8.0 for 14 of the last 18 months.",
            "memory_type": "observation", "truth_role": "ground_truth", "belief_holder": "system",
            "confidence": 1.0, "source_id": "P05", "source_type": "instrument_reading",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C07", "lossy_numeric", "raw_data", "pH", "Station_F"], "summary_layer": 0
        },
        {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": "2030-04-01T10:00:00Z", "observation_time": "2030-04-01T14:00:00Z",
            "authored_time": "2030-04-10T09:00:00Z", "ingestion_time": "2030-04-11T09:00:00Z",
            "subject": "pH quarterly report Q1 2030", "predicate": "reported",
            "object": "ocean pH averages approximately 8.05",
            "text": "Q1 2030 Quarterly Report excerpt: 'Ocean pH across the monitoring network averages approximately 8.05, reflecting stable conditions.' Range information from monthly summaries collapsed to single average. Station-level variation not reported.",
            "memory_type": "report", "truth_role": "distorted_summary", "belief_holder": "P02",
            "confidence": 0.7, "source_id": "P02", "source_type": "quarterly_report",
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": ["C07", "lossy_numeric", "layer2", "quarterly", "pH"], "summary_layer": 2
        },
    ])

    # ==================== MORE BACKGROUND MEMORIES ====================
    bg_memories = [
        {
            "event_time": "2028-03-10T09:00:00Z", "observation_time": "2028-03-10T10:00:00Z",
            "authored_time": "2028-03-10T14:00:00Z", "ingestion_time": "2028-03-11T09:00:00Z",
            "subject": "Cascade Institute", "predicate": "received", "object": "NSF grant OCE-2028-1547",
            "text": "Cascade Institute awarded NSF grant OCE-2028-1547 for 'Long-term Pacific Ocean Monitoring and Synthesis' — $2.4M over 5 years. PI: Dr. Okafor. Funds support monitoring stations, graduate researchers, and annual synthesis publications.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P01",
            "source_type": "grant_record", "tags": ["background", "funding"], "summary_layer": 0
        },
        {
            "event_time": "2028-05-15T13:00:00Z", "observation_time": "2028-05-15T14:00:00Z",
            "authored_time": "2028-05-15T16:00:00Z", "ingestion_time": "2028-05-16T09:00:00Z",
            "subject": "R/V Pacific Explorer", "predicate": "scheduled_for", "object": "summer 2028 cruise series",
            "text": "Research vessel Pacific Explorer scheduled for 6 summer cruises (June-September 2028) for station maintenance and sampling. Cruise chief: Dr. Rivera. Crew complement: 12.",
            "memory_type": "logistics", "truth_role": "background", "source_id": "P02",
            "source_type": "vessel_schedule", "tags": ["background", "vessel"], "summary_layer": 0
        },
        {
            "event_time": "2028-09-01T09:00:00Z", "observation_time": "2028-09-01T10:00:00Z",
            "authored_time": "2028-09-01T11:00:00Z", "ingestion_time": "2028-09-02T09:00:00Z",
            "subject": "Johansson", "predicate": "began", "object": "graduate research program",
            "text": "Kira Johansson joined Cascade Institute as graduate researcher under Dr. Tanaka's supervision. Research focus: developing improved fish counting methodologies using sonar technology.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P03",
            "source_type": "personnel_record", "tags": ["background", "personnel"], "summary_layer": 0
        },
        {
            "event_time": "2029-01-15T10:00:00Z", "observation_time": "2029-01-15T11:00:00Z",
            "authored_time": "2029-01-15T15:00:00Z", "ingestion_time": "2029-01-16T09:00:00Z",
            "subject": "Data quality committee", "predicate": "established", "object": "monthly review protocol",
            "text": "Institute data quality committee established under Marcus Chen's leadership. Monthly reviews of all monitoring data for QA/QC. Committee includes representatives from each research group.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P05",
            "source_type": "committee_record", "tags": ["background", "data_quality"], "summary_layer": 0
        },
        {
            "event_time": "2029-04-20T09:00:00Z", "observation_time": "2029-04-20T17:00:00Z",
            "authored_time": "2029-04-22T09:00:00Z", "ingestion_time": "2029-04-23T09:00:00Z",
            "subject": "Station K7", "predicate": "underwent", "object": "instrument replacement and upgrade",
            "text": "Station K7 underwent scheduled instrument replacement. CTD probe SN-4472 replaced with SN-5891 (newer model, same specifications). Calibration crossover study showed agreement within ±0.02°C. No discontinuity in time series.",
            "memory_type": "maintenance", "truth_role": "background", "source_id": "P02",
            "source_type": "maintenance_log", "tags": ["background", "Station_K7", "calibration"], "summary_layer": 0
        },
        {
            "event_time": "2029-06-10T10:00:00Z", "observation_time": "2029-06-10T12:00:00Z",
            "authored_time": "2029-06-12T09:00:00Z", "ingestion_time": "2029-06-13T09:00:00Z",
            "subject": "Dr. Rivera", "predicate": "presented_at", "object": "AGU Ocean Sciences Meeting",
            "text": "Dr. Rivera presented 'Decadal SST Trends in the Northeast Pacific: A Multi-Station Analysis' at the AGU Ocean Sciences Meeting. Poster session. Received positive feedback but several attendees questioned the statistical significance thresholds used.",
            "memory_type": "event", "truth_role": "background", "source_id": "P02",
            "source_type": "conference_record", "tags": ["background", "conference", "SST"], "summary_layer": 0
        },
        {
            "event_time": "2029-08-01T09:00:00Z", "observation_time": "2029-08-01T11:00:00Z",
            "authored_time": "2029-08-01T14:00:00Z", "ingestion_time": "2029-08-02T09:00:00Z",
            "subject": "Cascade Institute server", "predicate": "upgraded_to", "object": "new data management system",
            "text": "Institute IT completed migration to new data management system. All historical data (2015-2029) successfully migrated. New system supports automated monthly summary generation and version-controlled report pipeline.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P05",
            "source_type": "IT_record", "tags": ["background", "IT", "data_management"], "summary_layer": 0
        },
        {
            "event_time": "2029-11-15T10:00:00Z", "observation_time": "2029-11-15T16:00:00Z",
            "authored_time": "2029-11-20T09:00:00Z", "ingestion_time": "2029-11-21T09:00:00Z",
            "subject": "Annual stakeholder meeting", "predicate": "held", "object": "with 45 attendees from government and industry",
            "text": "2029 annual stakeholder meeting held at Cascade Institute. 45 attendees from state agencies, fishing industry, and conservation groups. Dr. Okafor presented the annual synthesis. Key discussion: how to communicate uncertainty in climate projections to policymakers.",
            "memory_type": "event", "truth_role": "background", "source_id": "P01",
            "source_type": "meeting_record", "tags": ["background", "stakeholder", "communication"], "summary_layer": 0
        },
        {
            "event_time": "2030-02-01T09:00:00Z", "observation_time": "2030-02-01T10:00:00Z",
            "authored_time": "2030-02-01T14:00:00Z", "ingestion_time": "2030-02-02T09:00:00Z",
            "subject": "Dr. Gould", "predicate": "appointed", "object": "as policy liaison to Oregon legislature",
            "text": "Dr. Lena Gould formally appointed as Cascade Institute's policy liaison to the Oregon state legislature. Role: translate research findings into policy-accessible language for the Coastal Resilience Committee.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P01",
            "source_type": "personnel_record", "tags": ["background", "personnel", "policy"], "summary_layer": 0
        },
        {
            "event_time": "2030-05-10T09:00:00Z", "observation_time": "2030-05-10T14:00:00Z",
            "authored_time": "2030-05-12T09:00:00Z", "ingestion_time": "2030-05-13T09:00:00Z",
            "subject": "Cascade Institute", "predicate": "hosted", "object": "visiting researcher Dr. Park from KIOST",
            "text": "Dr. Jisoo Park from Korea Institute of Ocean Science and Technology (KIOST) visited for 3-month collaborative research stay. Focus: comparing Pacific Northwest and Korean coastal pH monitoring methodologies.",
            "memory_type": "event", "truth_role": "background", "source_id": "P01",
            "source_type": "collaboration_record", "tags": ["background", "collaboration", "pH"], "summary_layer": 0
        },
        {
            "event_time": "2030-07-20T09:00:00Z", "observation_time": "2030-07-20T17:00:00Z",
            "authored_time": "2030-07-22T09:00:00Z", "ingestion_time": "2030-07-23T09:00:00Z",
            "subject": "Storm damage", "predicate": "affected", "object": "Stations B and C buoys",
            "text": "Severe storm damaged mooring lines at Stations B and C. 12-day data gap while repairs completed. Buoys recovered and redeployed by July 31. No instrument damage — data gap is physical, not instrumental.",
            "memory_type": "incident", "truth_role": "background", "source_id": "P02",
            "source_type": "incident_report", "tags": ["background", "station_maintenance", "data_gap"], "summary_layer": 0
        },
        {
            "event_time": "2030-12-01T10:00:00Z", "observation_time": "2030-12-01T14:00:00Z",
            "authored_time": "2030-12-05T09:00:00Z", "ingestion_time": "2030-12-06T09:00:00Z",
            "subject": "Johansson", "predicate": "completed", "object": "sonar counting validation study",
            "text": "Johansson completed validation study comparing visual and sonar fish counting methods. Key finding: sonar counts consistently ~8% higher than visual counts under controlled conditions. Recommended transition to hybrid sonar+visual method for 2033 season.",
            "memory_type": "observation", "truth_role": "ground_truth", "source_id": "P07",
            "source_type": "research_report", "tags": ["background", "methodology", "salmon"], "summary_layer": 0
        },
        {
            "event_time": "2031-03-01T09:00:00Z", "observation_time": "2031-03-01T10:00:00Z",
            "authored_time": "2031-03-01T14:00:00Z", "ingestion_time": "2031-03-02T09:00:00Z",
            "subject": "El Niño 2031", "predicate": "declared", "object": "by NOAA Climate Prediction Center",
            "text": "NOAA Climate Prediction Center declared El Niño conditions for winter 2030-2031. ONI index +1.8. Expected impacts on Pacific Northwest: reduced upwelling, warmer SST, reduced salmon returns, altered precipitation patterns.",
            "memory_type": "observation", "truth_role": "background", "source_id": "external",
            "source_type": "external_advisory", "tags": ["background", "El_Nino", "climate"], "summary_layer": 0
        },
        {
            "event_time": "2031-06-15T10:00:00Z", "observation_time": "2031-06-15T16:00:00Z",
            "authored_time": "2031-06-20T09:00:00Z", "ingestion_time": "2031-06-21T09:00:00Z",
            "subject": "Dr. Patel", "predicate": "updated", "object": "climate model ensemble with CMIP7 runs",
            "text": "Dr. Patel incorporated new CMIP7 model runs into the sea-level projection ensemble. Updated median projection: 32cm by 2050 (previously 28cm). Range now 18-52cm. Updated results will appear in next annual synthesis.",
            "memory_type": "observation", "truth_role": "background", "source_id": "P04",
            "source_type": "model_update", "tags": ["background", "models", "sea_level"], "summary_layer": 0
        },
        {
            "event_time": "2031-10-01T09:00:00Z", "observation_time": "2031-10-01T10:00:00Z",
            "authored_time": "2031-10-01T11:00:00Z", "ingestion_time": "2031-10-02T09:00:00Z",
            "subject": "Lab equipment", "predicate": "purchased", "object": "new spectrophotometric pH analyzer",
            "text": "Cascade Institute purchased new spectrophotometric pH analyzer (Honeywell Durafet III) for laboratory cross-validation of field pH measurements. Accuracy: ±0.001 pH units. Cost: $45,000 from NSF grant.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P05",
            "source_type": "procurement_record", "tags": ["background", "equipment", "pH"], "summary_layer": 0
        },
        {
            "event_time": "2032-01-10T10:00:00Z", "observation_time": "2032-01-10T14:00:00Z",
            "authored_time": "2032-01-15T09:00:00Z", "ingestion_time": "2032-01-16T09:00:00Z",
            "subject": "Outreach program", "predicate": "launched", "object": "public ocean monitoring dashboard",
            "text": "Cascade Institute launched public-facing ocean monitoring dashboard showing real-time data from all stations. Dashboard shows current readings but not historical context or uncertainty ranges. Dr. Okafor noted concern about oversimplification but approved launch.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P01",
            "source_type": "program_record", "tags": ["background", "outreach", "dashboard"], "summary_layer": 0
        },
        {
            "event_time": "2032-05-15T10:00:00Z", "observation_time": "2032-05-15T16:00:00Z",
            "authored_time": "2032-05-20T09:00:00Z", "ingestion_time": "2032-05-21T09:00:00Z",
            "subject": "Tanaka and Rivera", "predicate": "co-authored", "object": "review paper on summarization bias in oceanography",
            "text": "Tanaka and Rivera co-authored 'The Compression Problem: How Scientific Findings Lose Nuance in the Summary Pipeline' for Annual Review of Marine Science. The paper explicitly discusses qualifier loss and uncertainty flattening in oceanographic reporting — ironically, their own institute's reports exhibit exactly these patterns.",
            "memory_type": "publication", "truth_role": "background", "source_id": "P02",
            "source_type": "peer_reviewed_publication", "tags": ["background", "meta_research", "publication"], "summary_layer": 0
        },
        {
            "event_time": "2032-09-01T09:00:00Z", "observation_time": "2032-09-01T10:00:00Z",
            "authored_time": "2032-09-01T14:00:00Z", "ingestion_time": "2032-09-02T09:00:00Z",
            "subject": "Johansson", "predicate": "defended", "object": "master's thesis on sonar counting methods",
            "text": "Kira Johansson successfully defended master's thesis: 'Acoustic vs Visual Enumeration of Anadromous Fish: Implications for Long-Term Population Monitoring.' Committee noted the ~8% count differential has important implications for trend analysis.",
            "memory_type": "event", "truth_role": "background", "source_id": "P07",
            "source_type": "academic_record", "tags": ["background", "thesis", "methodology"], "summary_layer": 0
        },
        {
            "event_time": "2033-02-15T10:00:00Z", "observation_time": "2033-02-15T14:00:00Z",
            "authored_time": "2033-02-20T09:00:00Z", "ingestion_time": "2033-02-21T09:00:00Z",
            "subject": "Chen data audit", "predicate": "flagged", "object": "12 instances of qualifier loss in 2028-2032 reports",
            "text": "Marcus Chen's systematic audit of Cascade Institute's reporting pipeline (2028-2032) flagged 12 instances where qualifiers were dropped during summarization, 8 instances where uncertainty ranges were collapsed, and 4 instances where provenance was lost. Report submitted to Dr. Okafor; no action taken yet.",
            "memory_type": "observation", "truth_role": "ground_truth", "source_id": "P05",
            "source_type": "internal_audit", "tags": ["background", "data_quality", "audit"], "summary_layer": 0
        },
        {
            "event_time": "2033-06-01T10:00:00Z", "observation_time": "2033-06-01T14:00:00Z",
            "authored_time": "2033-06-05T09:00:00Z", "ingestion_time": "2033-06-06T09:00:00Z",
            "subject": "Cascade Institute", "predicate": "renewed", "object": "NSF funding for 2033-2038",
            "text": "NSF renewed Cascade Institute's monitoring grant for another 5-year cycle (OCE-2033-0892, $3.1M). Review panel specifically praised the long-term data continuity. Condition: institute must address data quality committee's findings on reporting accuracy.",
            "memory_type": "administrative", "truth_role": "background", "source_id": "P01",
            "source_type": "grant_record", "tags": ["background", "funding", "renewal"], "summary_layer": 0
        },
    ]

    for bg in bg_memories:
        m = {
            "memory_id": mid(), "experiment": EXP, "story_id": STORY,
            "event_time": bg["event_time"], "observation_time": bg["observation_time"],
            "authored_time": bg["authored_time"], "ingestion_time": bg["ingestion_time"],
            "subject": bg["subject"], "predicate": bg["predicate"], "object": bg["object"],
            "text": bg["text"], "memory_type": bg["memory_type"],
            "truth_role": bg["truth_role"], "belief_holder": "system",
            "confidence": 1.0, "source_id": bg["source_id"], "source_type": bg["source_type"],
            "derived_from": [], "supersedes": [], "contradicts": [], "duplicates": [],
            "aliases": [], "scope": "institute",
            "tags": bg["tags"], "summary_layer": bg["summary_layer"]
        }
        new_memories.append(m)

    # ==================== MORE QUERIES ====================
    new_queries.extend([
        # Qualifier loss
        {
            "query_id": qid(), "query": "Was the K7 temperature anomaly in 2028 statistically significant?",
            "category": "qualifier_loss",
            "expected_claims": ["The anomaly was marginally significant (p=0.04)", "Given multiple comparisons across 14 stations, it should be treated as marginally significant"],
            "acceptable_claims": ["p=0.04 is below 0.05 but context matters"],
            "forbidden_claims": ["The anomaly was definitively significant", "The anomaly was clearly significant"],
            "relevant_memory_ids": ["M0002", "M0004"],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether the system preserves the marginally significant qualifier against the simpler 'significant' from higher layers"
        },
        {
            "query_id": qid(), "query": "Were other monitoring stations besides K7 also showing warming in August 2028?",
            "category": "qualifier_loss",
            "expected_claims": ["K3 showed +0.4°C (not significant)", "K11 showed +0.7°C (not significant)", "Other stations were within normal ranges"],
            "acceptable_claims": ["Some stations showed minor positive anomalies but none were significant"],
            "forbidden_claims": ["Warming was detected across multiple stations", "Widespread warming was observed"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "The annual synthesis distorts K7's finding into 'warming across stations' — this tests whether the system uses raw data"
        },
        # Uncertainty loss
        {
            "query_id": qid(), "query": "What is the full range of sea-level rise projections for the Pacific Northwest by 2050?",
            "category": "uncertainty_loss",
            "expected_claims": ["The model ensemble projects 15-45cm", "Median is 28cm (or updated 32cm from CMIP7)", "Three of twelve models show >40cm", "90% confidence interval"],
            "acceptable_claims": ["Updated CMIP7 range is 18-52cm"],
            "forbidden_claims": ["30cm is certain", "Sea-level rise will be 30cm", "Models agree on 30cm"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether the system recovers the full uncertainty range or reports the compressed certainty"
        },
        {
            "query_id": qid(), "query": "Which specific climate models project more than 40cm of sea-level rise?",
            "category": "uncertainty_loss",
            "expected_claims": ["UKESM1 (42cm)", "CanESM5 (45cm)", "ACCESS-CM2 (38cm)"],
            "acceptable_claims": ["Three models project >40cm"],
            "forbidden_claims": ["No models show significant divergence", "All models agree"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "medium", "target_layer": 0,
            "notes": "Tests whether individual model outputs survive compression"
        },
        # Provenance loss
        {
            "query_id": qid(), "query": "Did any single study at Cascade Institute directly demonstrate that acidification causes kelp loss?",
            "category": "provenance_loss",
            "expected_claims": ["No single study demonstrated the causal link", "The conclusion was editorially synthesized in a quarterly report from three separate studies", "Patel studied acidification (not kelp/urchins)", "Tanaka studied urchins (not acidification directly)", "Rivera studied kelp decline"],
            "acceptable_claims": ["The causal chain is inferential"],
            "forbidden_claims": ["Yes, a comprehensive study demonstrated this", "The Cascade Institute study showed acidification drives kelp loss"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Critical provenance test — the merged conclusion must be traced back to its three separate sources"
        },
        {
            "query_id": qid(), "query": "What did Dr. Tanaka specifically say about the causal mechanism between acidification and urchin overgrazing?",
            "category": "provenance_loss",
            "expected_claims": ["Tanaka cautioned that the causal mechanism remains inferential", "Tanaka observed the urchin explosion but did not demonstrate the biochemical pathway"],
            "acceptable_claims": ["Correlation observed but causation not directly measured"],
            "forbidden_claims": ["Tanaka demonstrated the mechanism", "Tanaka's study confirmed acidification drives urchin overgrazing"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "medium", "target_layer": 0,
            "notes": "Tests whether Tanaka's specific caveat survives the summarization chain"
        },
        # Temporal flattening
        {
            "query_id": qid(), "query": "What was the lowest salmon run count recorded and what caused it?",
            "category": "temporal_flattening",
            "expected_claims": ["12,400 in 2028", "Caused by extreme drought conditions", "River flow was 45% of normal", "Counters had 3 days of very low visibility"],
            "acceptable_claims": ["Drought year significantly impacted count"],
            "forbidden_claims": ["Salmon populations have been stable", "Counts remained healthy"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": True, "should_abstain": False,
            "difficulty": "medium", "target_layer": 0,
            "notes": "Tests whether year-to-year variability and causal context survive temporal flattening"
        },
        {
            "query_id": qid(), "query": "Is the 2033 salmon count of 23,800 directly comparable to earlier years?",
            "category": "temporal_flattening",
            "expected_claims": ["No — the 2033 count uses a new sonar-assisted method", "The sonar method counts approximately 8% more fish", "Adjusting for method, the comparable count would be around 22,000"],
            "acceptable_claims": ["Methodology change makes direct comparison unreliable"],
            "forbidden_claims": ["Yes, the count shows clear growth", "Salmon populations are increasing"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether the methodology change is preserved through summarization"
        },
        # Identity collapse
        {
            "query_id": qid(), "query": "What is the bleaching threshold for Porites lobata and how does it compare to Acropora digitifera?",
            "category": "identity_collapse",
            "expected_claims": ["Porites lobata threshold: 30.5°C", "Acropora digitifera threshold: 28.5°C", "2°C difference in thresholds", "Porites showed only 5% bleaching vs Acropora's 95%"],
            "acceptable_claims": ["3× difference in bleaching rates"],
            "forbidden_claims": ["All corals have similar thresholds", "Corals are uniformly affected"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether species-specific data survives identity collapse"
        },
        {
            "query_id": qid(), "query": "Is the statement 'coral reefs are dying' accurate based on the Cascade Institute's data?",
            "category": "identity_collapse",
            "expected_claims": ["The statement is oversimplified", "Acropora digitifera suffered 72% mortality", "Pocillopora damicornis had 25% mortality", "Porites lobata had 0% mortality and is thriving", "Differential resilience is the key finding"],
            "acceptable_claims": ["Some species are dying but others are thriving"],
            "forbidden_claims": ["Yes, coral reefs are dying", "All corals are equally affected"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": True,
            "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Directly tests whether the system propagates the oversimplified policy-brief claim"
        },
        # Summary drift
        {
            "query_id": qid(), "query": "What was the original K7 Q2 2030 temperature finding before summarization?",
            "category": "summary_drift",
            "expected_claims": ["0.8°C temperature anomaly at Station K7", "Recorded in Q2 2030", "Described as within normal interannual variability"],
            "acceptable_claims": ["A modest, non-alarming temperature reading"],
            "forbidden_claims": ["Widespread warming", "Dramatic warming", "Pervasive warming trends"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": True,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether the system can pierce five layers of drift to recover the original finding"
        },
        {
            "query_id": qid(), "query": "How did the characterization of K7's 2030 temperature anomaly change across summary layers?",
            "category": "summarization_awareness",
            "expected_claims": ["Raw: 0.8°C within normal variability", "First summary: temperature anomaly recorded", "Second: anomalies at monitoring stations (plural)", "Third: widespread temperature anomalies", "Fourth: pervasive warming trends", "Fifth: dramatic ocean warming"],
            "acceptable_claims": ["Each layer amplified the claim monotonically toward alarm"],
            "forbidden_claims": ["The characterization remained consistent"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": True,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "very_hard", "target_layer": 0,
            "notes": "Meta-awareness test — can the system describe the drift pattern itself?"
        },
        # Lossy numeric
        {
            "query_id": qid(), "query": "Is the annual report's claim that 'ocean pH remains above 8.0' accurate?",
            "category": "lossy_numeric",
            "expected_claims": ["No — Station C measured 7.998 and Station F measured 7.965", "The claim is factually wrong for 2 of 6 stations (33%)", "Station F has been below 8.0 for 14 of the last 18 months"],
            "acceptable_claims": ["The annual report contains a factual error"],
            "forbidden_claims": ["Yes, pH remains above 8.0", "Ocean pH is stable"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": True,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether the system detects and flags a factual error in a higher-layer summary"
        },
        {
            "query_id": qid(), "query": "What was the pH at Station F and why is it consistently low?",
            "category": "lossy_numeric",
            "expected_claims": ["pH 7.965 (June 2029 measurement)", "Station F is in a semi-enclosed bay", "High nutrient runoff and limited tidal flushing", "Below 8.0 for 14 of 18 months"],
            "acceptable_claims": ["Station F has chronically low pH due to its location"],
            "forbidden_claims": ["All stations have pH above 8.0", "pH is stable across the network"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": True, "should_abstain": False,
            "difficulty": "medium", "target_layer": 0,
            "notes": "Tests whether station-level detail survives numeric compression"
        },
        # Layer preference / distractor resistance
        {
            "query_id": qid(), "query": "What did Marcus Chen's data audit find about the institute's reporting pipeline?",
            "category": "summarization_awareness",
            "expected_claims": ["12 instances of qualifier loss", "8 instances of uncertainty range collapse", "4 instances of provenance loss", "Audit covered 2028-2032 reports"],
            "acceptable_claims": ["Systematic audit found widespread summarization errors"],
            "forbidden_claims": ["The reporting pipeline is accurate", "No issues were found"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "easy", "target_layer": 0,
            "notes": "Control query — tests retrieval of the meta-finding about the institute's own drift"
        },
        {
            "query_id": qid(), "query": "Which source should be trusted more: the policy brief saying '30cm of sea-level rise will occur' or the original model ensemble?",
            "category": "layer_preference",
            "expected_claims": ["The original model ensemble is more authoritative", "It provides the full 15-45cm range with confidence intervals", "The policy brief removed all uncertainty", "The word 'will' was not in any scientific source"],
            "acceptable_claims": ["Raw data should be preferred over compressed summaries"],
            "forbidden_claims": ["The policy brief is more authoritative because it is more recent", "30cm is the correct number"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": True,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "medium", "target_layer": 0,
            "notes": "Tests explicit layer preference reasoning"
        },
        # Distractor resistance
        {
            "query_id": qid(), "query": "Has the Cascade Institute documented widespread Pacific warming?",
            "category": "distractor_resistance",
            "expected_claims": ["The institute's raw data shows one marginally significant anomaly at K7 (2028) and one within-normal-variability anomaly at K7 (2030)", "The 'widespread warming' characterization comes from summary drift, not raw observations"],
            "acceptable_claims": ["Individual station anomalies were amplified through summarization"],
            "forbidden_claims": ["Yes, widespread warming has been documented", "Pervasive warming trends confirmed"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": True, "must_surface_conflict": True,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "very_hard", "target_layer": 0,
            "notes": "The most adversarial query — the higher-layer summaries overwhelmingly say yes, but raw data says no"
        },
        {
            "query_id": qid(), "query": "What is the current state of coral health at Cascade Institute monitoring sites?",
            "category": "distractor_resistance",
            "expected_claims": ["Species-dependent: Acropora 72% mortality, Pocillopora 25% mortality, Porites 0% mortality and thriving", "Differential resilience is the key finding"],
            "acceptable_claims": ["Mixed — varies significantly by species"],
            "forbidden_claims": ["Corals are dying", "Coral reefs are in decline"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": True,
            "must_disambiguate": True, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "hard", "target_layer": 0,
            "notes": "Tests whether the blanket 'dying' from policy layer is resisted in favor of species-specific data"
        },
        # Easy controls
        {
            "query_id": qid(), "query": "Who is the director of the Cascade Institute?",
            "category": "distractor_resistance",
            "expected_claims": ["Dr. Nadia Okafor"],
            "acceptable_claims": [],
            "forbidden_claims": [],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "easy", "target_layer": 0,
            "notes": "Easy control — straightforward factual recall"
        },
        {
            "query_id": qid(), "query": "When did the Cascade Institute receive its NSF grant?",
            "category": "distractor_resistance",
            "expected_claims": ["March 2028, OCE-2028-1547", "Renewed in 2033 as OCE-2033-0892"],
            "acceptable_claims": [],
            "forbidden_claims": [],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "easy", "target_layer": 0,
            "notes": "Easy control — tests basic factual retrieval"
        },
        {
            "query_id": qid(), "query": "What did Johansson's thesis find about counting methodology differences?",
            "category": "temporal_flattening",
            "expected_claims": ["Sonar counts approximately 8% higher than visual counts", "Recommended transition to hybrid method for 2033"],
            "acceptable_claims": [],
            "forbidden_claims": ["Methods produce identical counts"],
            "relevant_memory_ids": [],
            "distractor_memory_ids": [],
            "required_source_roots": [], "expected_temporal_order": [],
            "must_surface_uncertainty": False, "must_surface_conflict": False,
            "must_disambiguate": False, "must_preserve_scope": False, "should_abstain": False,
            "difficulty": "easy", "target_layer": 0,
            "notes": "Easy control — tests whether methodology context is retrievable"
        },
    ])

    print(f"\nAdding {len(new_memories)} new memories...")
    memories.extend(new_memories)
    print(f"Total memories: {len(memories)}")

    print(f"Adding {len(new_queries)} new queries...")
    queries.extend(new_queries)
    print(f"Total queries: {len(queries)}")

    # Write files
    print("\nWriting files...")
    with open(mem_path, 'w') as f:
        for m in memories:
            f.write(json.dumps(m) + "\n")
    with open(q_path, 'w') as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    # Rebuild manifest
    manifest_path = os.path.join(d, "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    for entry in manifest["files"]:
        fn = entry["path"]
        if fn in ("memories.jsonl", "queries.jsonl"):
            fp = os.path.join(d, fn)
            h = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
            entry["sha256"] = h
            entry["bytes"] = os.path.getsize(fp)

    manifest["canonical_memory_count"] = len(memories)
    manifest["query_count"] = len(queries)

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Print final stats
    tags = {}
    layers = {}
    for m in memories:
        for t in m.get('tags', []):
            if t.startswith('C0'):
                tags[t] = tags.get(t, 0) + 1
                break
        else:
            tags['background'] = tags.get('background', 0) + 1
        l = m.get('summary_layer', -1)
        layers[l] = layers.get(l, 0) + 1

    qcats = {}
    for q in queries:
        c = q.get('category', 'unknown')
        qcats[c] = qcats.get(c, 0) + 1

    print("\n=== Final Stats ===")
    print(f"Total memories: {len(memories)}")
    print(f"Total queries: {len(queries)}")
    print("\nMemories by case:")
    for k in sorted(tags.keys()):
        print(f"  {k}: {tags[k]}")
    print("\nSummary layers:")
    for k in sorted(layers.keys()):
        print(f"  Layer {k}: {layers[k]}")
    print("\nQueries by category:")
    for k in sorted(qcats.keys()):
        print(f"  {k}: {qcats[k]}")

if __name__ == "__main__":
    main()
