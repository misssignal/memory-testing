#!/usr/bin/env python3
"""Generate Experiment 13: Consolidation / Summarization Drift.

Cascade Institute oceanographic research scenario testing how information
degrades through progressive summarization layers (raw → monthly → quarterly
→ annual → meta-analysis → policy brief).
"""

import json
import hashlib
import shutil
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

EXPERIMENT = "exp13_consolidation_summarization_drift"
STORY_ID = "cascade_institute"

STORY_BIBLE = Path(__file__).resolve().parent.parent / "scratchpad" / "exp13" / "story_bible.md"
if not STORY_BIBLE.exists():
    STORY_BIBLE = Path("/tmp/claude-0/-home-user-memory-testing/6ffa00f0-af4e-5ad8-9c00-025401d96b92/scratchpad/exp13/story_bible.md")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Memory builder ───────────────────────────────────────────────────
ALL_MEMORIES = []

def mem(**kw):
    m = {
        "memory_id": f"M{len(ALL_MEMORIES)+1:04d}",
        "experiment": EXPERIMENT,
        "story_id": STORY_ID,
        "event_time": kw["event_time"],
        "observation_time": kw.get("observation_time", kw["event_time"]),
        "authored_time": kw.get("authored_time", kw.get("observation_time", kw["event_time"])),
        "ingestion_time": kw["ingestion_time"],
        "subject": kw.get("subject", ""),
        "predicate": kw.get("predicate", ""),
        "object": kw.get("object", ""),
        "text": kw["text"],
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
    ALL_MEMORIES.append(m)
    return m["memory_id"]


# ══════════════════════════════════════════════════════════════════════
# CASE GENERATORS
# ══════════════════════════════════════════════════════════════════════

def gen_c01_qualifier_loss():
    """C01: Qualifier loss through summarization — 'marginally significant' becomes 'significant'."""
    mems = []

    # Layer 0: Raw observation
    mid = mem(
        text="Sea surface temperature anomaly of +1.2°C ± 0.3°C (p=0.04, marginally significant) observed at Station K7 during August 2028. Instrument: CTD probe SN-4472, calibrated 2028-07-15.",
        subject="Station K7", predicate="recorded", object="SST anomaly +1.2°C ± 0.3°C (p=0.04, marginally significant)",
        event_time="2028-08-15T14:00:00Z", observation_time="2028-08-15T14:30:00Z",
        authored_time="2028-08-15T16:00:00Z", ingestion_time="2028-08-16T09:00:00Z",
        source_id="P02", source_type="instrument_reading",
        tags=["C01", "qualifier_loss", "raw_data", "Station_K7", "SST"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    mid = mem(
        text="Calibration record for CTD probe SN-4472 shows ±0.05°C accuracy. Last calibrated 2028-07-15 by Dr. Rivera. Probe deployed at Station K7 since 2027.",
        subject="CTD SN-4472", predicate="calibrated_with", object="±0.05°C accuracy",
        event_time="2028-07-15T10:00:00Z", observation_time="2028-07-15T11:00:00Z",
        authored_time="2028-07-15T12:00:00Z", ingestion_time="2028-07-16T09:00:00Z",
        source_id="P02", source_type="calibration_record",
        tags=["C01", "qualifier_loss", "raw_data", "calibration"],
        summary_layer=0)
    mems.append(mid)

    mid = mem(
        text="Statistical analysis of K7 August 2028 data: the +1.2°C anomaly has p=0.04, which is below 0.05 but the team consensus is that given multiple comparisons across 14 stations, this should be treated as marginally significant rather than definitively significant.",
        subject="K7 statistical analysis", predicate="classified_as", object="marginally significant given multiple comparisons",
        event_time="2028-08-20T10:00:00Z", observation_time="2028-08-20T11:00:00Z",
        authored_time="2028-08-20T14:00:00Z", ingestion_time="2028-08-21T09:00:00Z",
        source_id="P05", source_type="statistical_analysis",
        tags=["C01", "qualifier_loss", "raw_data", "statistics"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Layer 1: Monthly summary — qualifier dropped
    mid = mem(
        text="August 2028 monthly summary: Significant temperature anomaly of +1.2°C detected at Station K7. Other stations within normal range.",
        subject="Station K7", predicate="showed", object="significant temperature anomaly of +1.2°C",
        event_time="2028-08-31T00:00:00Z", observation_time="2028-09-01T09:00:00Z",
        authored_time="2028-09-02T10:00:00Z", ingestion_time="2028-09-03T09:00:00Z",
        source_id="P02", source_type="monthly_summary",
        derived_from=[mems[0]],
        tags=["C01", "qualifier_loss", "monthly_summary"],
        summary_layer=1, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 2: Quarterly report — magnitude dropped
    mid = mem(
        text="Q3 2028 Oceanographic Report: Notable warming was detected at Station K7 during the August monitoring period. The anomaly was statistically significant and warrants continued monitoring.",
        subject="Station K7", predicate="experienced", object="notable statistically significant warming",
        event_time="2028-09-30T00:00:00Z", observation_time="2028-10-01T09:00:00Z",
        authored_time="2028-10-05T14:00:00Z", ingestion_time="2028-10-06T09:00:00Z",
        source_id="P02", source_type="quarterly_report",
        derived_from=[mems[3]],
        tags=["C01", "qualifier_loss", "quarterly_report"],
        summary_layer=2, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 3: Annual synthesis — station identity collapsed
    mid = mem(
        text="2028 Annual Synthesis: Warming trends were observed across the Pacific monitoring station network, with statistically significant anomalies documented during the summer monitoring season.",
        subject="monitoring network", predicate="showed", object="statistically significant warming trends",
        event_time="2028-12-31T00:00:00Z", observation_time="2029-01-15T09:00:00Z",
        authored_time="2029-01-20T14:00:00Z", ingestion_time="2029-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[4]],
        tags=["C01", "qualifier_loss", "annual_synthesis"],
        summary_layer=3, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 4: Meta-analysis
    mid = mem(
        text="Pacific Monitoring Meta-Analysis (2028–2030): Consistent warming signals detected across station networks, confirming significant upward temperature trends in the study region.",
        subject="Pacific monitoring", predicate="confirmed", object="significant warming trends",
        event_time="2030-06-01T00:00:00Z", observation_time="2030-06-15T09:00:00Z",
        authored_time="2030-07-01T14:00:00Z", ingestion_time="2030-07-02T09:00:00Z",
        source_id="P01", source_type="meta_analysis",
        derived_from=[mems[5]],
        tags=["C01", "qualifier_loss", "meta_analysis"],
        summary_layer=4, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 5: Policy brief
    mid = mem(
        text="Oregon Coastal Policy Brief 2031: The Pacific Ocean is warming significantly. Research from the Cascade Institute confirms widespread and statistically significant temperature increases across the monitoring network.",
        subject="Pacific Ocean", predicate="is_experiencing", object="significant warming",
        event_time="2031-03-01T00:00:00Z", observation_time="2031-03-15T09:00:00Z",
        authored_time="2031-03-20T14:00:00Z", ingestion_time="2031-03-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[6]],
        tags=["C01", "qualifier_loss", "policy_brief"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_c02_uncertainty_loss():
    """C02: Uncertainty ranges collapsed to point estimates through summarization."""
    mems = []

    # Layer 0: Raw model output
    mid = mem(
        text="Sea-level rise projection ensemble (12 models): range 15–45cm by 2050, median 28cm, 90% confidence interval. Three of twelve models (GFDL-ESM4, CESM2, UKESM1) project >40cm. Model spread reflects uncertainty in ice sheet dynamics.",
        subject="sea-level projection", predicate="projects", object="15–45cm by 2050 (median 28cm, 90% CI)",
        event_time="2029-06-01T00:00:00Z", observation_time="2029-06-15T09:00:00Z",
        authored_time="2029-06-20T14:00:00Z", ingestion_time="2029-06-21T09:00:00Z",
        source_id="P04", source_type="model_output",
        tags=["C02", "uncertainty_loss", "raw_data", "sea_level"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    mid = mem(
        text="Model validation notes: The 15–45cm range deliberately brackets ice sheet uncertainty. The lower bound (15cm) assumes minimal Greenland contribution; the upper bound (45cm) includes rapid WAIS collapse scenario. Median (28cm) uses intermediate pathway.",
        subject="sea-level model", predicate="uncertainty_driven_by", object="ice sheet dynamics scenarios",
        event_time="2029-06-02T00:00:00Z", observation_time="2029-06-16T09:00:00Z",
        authored_time="2029-06-21T10:00:00Z", ingestion_time="2029-06-22T09:00:00Z",
        source_id="P04", source_type="model_documentation",
        tags=["C02", "uncertainty_loss", "raw_data", "methodology"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Layer 1: Monthly summary — range collapsed
    mid = mem(
        text="June 2029 modeling summary: Updated sea-level projections indicate approximately 28cm of rise by 2050. Model ensemble broadly consistent with previous estimates.",
        subject="sea-level projection", predicate="indicates", object="~28cm rise by 2050",
        event_time="2029-06-30T00:00:00Z", observation_time="2029-07-01T09:00:00Z",
        authored_time="2029-07-02T10:00:00Z", ingestion_time="2029-07-03T09:00:00Z",
        source_id="P04", source_type="monthly_summary",
        derived_from=[mems[0]],
        tags=["C02", "uncertainty_loss", "monthly_summary"],
        summary_layer=1, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 2: Quarterly report — rounded up, vague hedge
    mid = mem(
        text="Q2 2029 Climate Report: Sea-level rise of approximately 30cm is projected for the Oregon coast by mid-century, based on the latest model ensemble from the Cascade Institute.",
        subject="Oregon coast", predicate="projected_to_experience", object="~30cm sea-level rise by 2050",
        event_time="2029-06-30T00:00:00Z", observation_time="2029-07-15T09:00:00Z",
        authored_time="2029-07-20T14:00:00Z", ingestion_time="2029-07-21T09:00:00Z",
        source_id="P04", source_type="quarterly_report",
        derived_from=[mems[2]],
        tags=["C02", "uncertainty_loss", "quarterly_report"],
        summary_layer=2, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 3: Annual synthesis — "expected"
    mid = mem(
        text="2029 Annual Synthesis: Sea-level rise of 30cm is expected along the Oregon coast by 2050, according to Cascade Institute modeling. Coastal infrastructure planning should account for this projection.",
        subject="Oregon coast", predicate="expected_to_experience", object="30cm sea-level rise by 2050",
        event_time="2029-12-31T00:00:00Z", observation_time="2030-01-15T09:00:00Z",
        authored_time="2030-01-20T14:00:00Z", ingestion_time="2030-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[3]],
        tags=["C02", "uncertainty_loss", "annual_synthesis"],
        summary_layer=3, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 4: Meta-analysis
    mid = mem(
        text="Pacific Northwest Sea-Level Assessment (2031): Multiple research groups project 30cm of sea-level rise by 2050 for the Oregon-Washington coast. This estimate is well-supported by current modeling.",
        subject="Oregon-Washington coast", predicate="will_experience", object="30cm sea-level rise by 2050",
        event_time="2031-06-01T00:00:00Z", observation_time="2031-06-15T09:00:00Z",
        authored_time="2031-07-01T14:00:00Z", ingestion_time="2031-07-02T09:00:00Z",
        source_id="P04", source_type="meta_analysis",
        derived_from=[mems[4]],
        tags=["C02", "uncertainty_loss", "meta_analysis"],
        summary_layer=4, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 5: Policy brief — uncertainty eliminated
    mid = mem(
        text="Legislative Briefing 2031: 30cm of sea-level rise will occur along the Oregon coast by 2050. Infrastructure investments must be sized accordingly. The science is clear and well-established.",
        subject="Oregon coast", predicate="will_experience", object="30cm sea-level rise by 2050 (stated as certain)",
        event_time="2031-09-01T00:00:00Z", observation_time="2031-09-15T09:00:00Z",
        authored_time="2031-09-20T14:00:00Z", ingestion_time="2031-09-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[5]],
        tags=["C02", "uncertainty_loss", "policy_brief"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_c03_provenance_loss():
    """C03: Three independent studies merged into one conclusion, provenance lost."""
    mems = []

    # Study A: Kelp decline (Rivera)
    mid = mem(
        text="Sector 3 kelp survey (Rivera, 2029): Macrocystis pyrifera canopy coverage declined 40% between 2027 and 2029. Cause undetermined — multiple stressors possible including warming, grazing, and nutrient changes.",
        subject="Sector 3 kelp", predicate="declined", object="40% canopy loss 2027–2029, cause undetermined",
        event_time="2029-09-01T00:00:00Z", observation_time="2029-09-10T09:00:00Z",
        authored_time="2029-09-15T14:00:00Z", ingestion_time="2029-09-16T09:00:00Z",
        source_id="P02", source_type="field_survey",
        tags=["C03", "provenance_loss", "raw_data", "kelp", "Study_A"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Study B: Urchin explosion (Tanaka)
    mid = mem(
        text="Sector 3 urchin census (Tanaka, 2029): Strongylocentrotus purpuratus population increased 280% since 2027. Urchin barrens expanding. Cause attributed to predator loss (sunflower sea star wasting disease).",
        subject="Sector 3 urchins", predicate="increased", object="280% population growth since 2027",
        event_time="2029-10-01T00:00:00Z", observation_time="2029-10-10T09:00:00Z",
        authored_time="2029-10-15T14:00:00Z", ingestion_time="2029-10-16T09:00:00Z",
        source_id="P03", source_type="field_survey",
        tags=["C03", "provenance_loss", "raw_data", "urchins", "Study_B"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Study C: Acidification model (Patel)
    mid = mem(
        text="Sector 3 ocean chemistry model (Patel, 2030): pH projected to decline from 8.05 to 7.92 by 2035 under RCP4.5. Model does not include biological feedbacks. Note: this model covers water chemistry only, not direct ecological impacts.",
        subject="Sector 3 pH", predicate="projected_to_decline", object="8.05 to 7.92 by 2035",
        event_time="2030-02-01T00:00:00Z", observation_time="2030-02-10T09:00:00Z",
        authored_time="2030-02-15T14:00:00Z", ingestion_time="2030-02-16T09:00:00Z",
        source_id="P04", source_type="model_output",
        tags=["C03", "provenance_loss", "raw_data", "acidification", "Study_C"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Layer 2: Quarterly report — editorial synthesis merges three studies
    mid = mem(
        text="Q1 2030 Ecology Report: Sector 3 shows ecological decline consistent with acidification-driven urchin overgrazing of kelp forests. Kelp canopy loss of 40%, urchin populations up 280%, and declining pH all point to a coherent acidification impact.",
        subject="Sector 3", predicate="experiencing", object="acidification-driven urchin overgrazing of kelp",
        event_time="2030-03-31T00:00:00Z", observation_time="2030-04-01T09:00:00Z",
        authored_time="2030-04-10T14:00:00Z", ingestion_time="2030-04-11T09:00:00Z",
        source_id="P01", source_type="quarterly_report",
        derived_from=[mems[0], mems[1], mems[2]],
        tags=["C03", "provenance_loss", "quarterly_report", "editorial_synthesis"],
        summary_layer=2, truth_role="editorial_inference")
    mems.append(mid)

    # Layer 3: Annual synthesis — attribution simplified
    mid = mem(
        text="2030 Annual Synthesis: Ocean acidification is driving kelp forest loss in Sector 3 through urchin population explosions. This represents a cascading ecological impact of climate change on coastal ecosystems.",
        subject="acidification", predicate="is_driving", object="kelp loss via urchin overgrazing in Sector 3",
        event_time="2030-12-31T00:00:00Z", observation_time="2031-01-15T09:00:00Z",
        authored_time="2031-01-20T14:00:00Z", ingestion_time="2031-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[3]],
        tags=["C03", "provenance_loss", "annual_synthesis"],
        summary_layer=3, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 4: Meta-analysis — single attribution
    mid = mem(
        text="Pacific Kelp Forest Meta-Analysis (2032): Research from the Cascade Institute demonstrates that ocean acidification causes kelp forest collapse through cascading trophic effects, as documented in their Sector 3 study.",
        subject="Cascade Institute research", predicate="demonstrates", object="acidification causes kelp collapse",
        event_time="2032-06-01T00:00:00Z", observation_time="2032-06-15T09:00:00Z",
        authored_time="2032-07-01T14:00:00Z", ingestion_time="2032-07-02T09:00:00Z",
        source_id="P01", source_type="meta_analysis",
        derived_from=[mems[4]],
        tags=["C03", "provenance_loss", "meta_analysis"],
        summary_layer=4, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 5: Policy brief
    mid = mem(
        text="Marine Policy Brief 2032: Ocean acidification is destroying kelp forests along the Oregon coast, threatening marine biodiversity and fisheries. Immediate action on carbon emissions is needed to prevent further loss.",
        subject="ocean acidification", predicate="is_destroying", object="Oregon kelp forests",
        event_time="2032-09-01T00:00:00Z", observation_time="2032-09-15T09:00:00Z",
        authored_time="2032-09-20T14:00:00Z", ingestion_time="2032-09-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[5]],
        tags=["C03", "provenance_loss", "policy_brief"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_c04_temporal_flattening():
    """C04: Year-to-year variability flattened to 'stable' through summarization."""
    mems = []

    yearly_data = [
        (2028, 12400, "drought year, historically low", "2028-10-15"),
        (2029, 18200, "recovery from drought", "2029-10-15"),
        (2030, 22100, "strong year, favorable ocean conditions", "2030-10-15"),
        (2031, 14800, "El Niño impact, reduced ocean productivity", "2031-10-15"),
        (2032, 19500, "post-El Niño recovery", "2032-10-15"),
        (2033, 23800, "new monitoring method (~8% higher counts), adjusted estimate ~22,000", "2033-10-15"),
    ]

    for year, count, note, date in yearly_data:
        mid = mem(
            text=f"Columbia River salmon run count for {year}: {count:,} adults. Note: {note}.",
            subject=f"salmon run {year}", predicate="counted", object=f"{count:,} adults ({note})",
            event_time=f"{date}T00:00:00Z", observation_time=f"{date}T09:00:00Z",
            authored_time=f"{date}T14:00:00Z", ingestion_time=f"{year}-10-16T09:00:00Z",
            source_id="P02", source_type="field_count",
            tags=["C04", "temporal_flattening", "raw_data", "salmon"],
            summary_layer=0, truth_role="ground_truth")
        mems.append(mid)

    # Methodology change note for 2033
    mid = mem(
        text="2033 salmon counting methodology change: Switched from visual observer counts to sonar-based automated counting system. Calibration tests show the new system counts approximately 8% more fish than visual observers due to better detection of subsurface fish. Historical comparisons should apply a 0.92 correction factor to 2033+ counts.",
        subject="salmon counting method", predicate="changed_in_2033", object="sonar-based, ~8% overcounting vs visual",
        event_time="2033-06-01T00:00:00Z", observation_time="2033-06-15T09:00:00Z",
        authored_time="2033-06-20T14:00:00Z", ingestion_time="2033-06-21T09:00:00Z",
        source_id="P05", source_type="methodology_note",
        tags=["C04", "temporal_flattening", "raw_data", "methodology_change"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Layer 1: Multi-year summary — averaged
    mid = mem(
        text="Salmon monitoring summary (2028–2033): Runs averaged approximately 18,500 adults annually over the six-year period. Interannual variation present but within expected range.",
        subject="salmon runs 2028-2033", predicate="averaged", object="~18,500 adults annually",
        event_time="2033-12-01T00:00:00Z", observation_time="2033-12-15T09:00:00Z",
        authored_time="2033-12-20T10:00:00Z", ingestion_time="2033-12-21T09:00:00Z",
        source_id="P02", source_type="multi_year_summary",
        derived_from=[mems[i] for i in range(6)],
        tags=["C04", "temporal_flattening", "summary"],
        summary_layer=1, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 3: Annual report — "stable"
    mid = mem(
        text="2033 Annual Report: Salmon populations have remained stable over the 2028–2033 monitoring period, averaging approximately 18,500 adults per year.",
        subject="salmon populations", predicate="have_remained", object="stable (~18,500/year)",
        event_time="2033-12-31T00:00:00Z", observation_time="2034-01-15T09:00:00Z",
        authored_time="2034-01-20T14:00:00Z", ingestion_time="2034-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[7]],
        tags=["C04", "temporal_flattening", "annual_synthesis"],
        summary_layer=3, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 5: Policy brief — "healthy"
    mid = mem(
        text="Fisheries Policy Brief 2034: Columbia River salmon populations are healthy and stable, with consistent returns over the past six years. Current management practices appear effective.",
        subject="salmon populations", predicate="are", object="healthy and stable",
        event_time="2034-03-01T00:00:00Z", observation_time="2034-03-15T09:00:00Z",
        authored_time="2034-03-20T14:00:00Z", ingestion_time="2034-03-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[8]],
        tags=["C04", "temporal_flattening", "policy_brief"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_c05_identity_collapse():
    """C05: Three distinct coral species collapsed to generic 'corals'."""
    mems = []

    # Layer 0: Species-specific data
    species_data = [
        ("Acropora digitifera", "branching coral", "bleaching threshold 29.5°C, 85% bleaching rate in 2030 event, recovery time >3 years, heat-sensitive",
         "2030-03-15", "C05_species_A"),
        ("Pocillopora damicornis", "cauliflower coral", "bleaching threshold 30.5°C, 45% bleaching rate in 2030 event, recovery time 1–2 years, moderate resilience",
         "2030-03-16", "C05_species_B"),
        ("Porites lobata", "lobe coral", "bleaching threshold 32°C, 5% bleaching rate in 2030 event, recovery time <6 months, heat-tolerant — effectively thriving during bleaching events",
         "2030-03-17", "C05_species_C"),
    ]

    for sci_name, common, data, date, tag in species_data:
        mid = mem(
            text=f"Coral bleaching assessment for {sci_name} ({common}): {data}. Survey conducted at Cascade Reef Site A during March 2030 bleaching event.",
            subject=sci_name, predicate="assessed_for_bleaching", object=data,
            event_time=f"{date}T09:00:00Z", observation_time=f"{date}T14:00:00Z",
            authored_time=f"{date}T17:00:00Z", ingestion_time=f"2030-03-18T09:00:00Z",
            source_id="P03", source_type="field_survey",
            tags=["C05", "identity_collapse", "raw_data", "coral", tag],
            summary_layer=0, truth_role="ground_truth")
        mems.append(mid)

    # Additional raw: differential resilience note
    mid = mem(
        text="Dr. Tanaka's field note: The 2030 bleaching event reveals a stark 3x difference in bleaching rates between species. Acropora (85%) is being devastated while Porites (5%) is essentially unaffected. This differential resilience is critical for reef management — not all corals respond equally to thermal stress.",
        subject="coral species", predicate="show", object="3x difference in bleaching rates",
        event_time="2030-03-20T10:00:00Z", observation_time="2030-03-20T11:00:00Z",
        authored_time="2030-03-20T15:00:00Z", ingestion_time="2030-03-21T09:00:00Z",
        source_id="P03", source_type="field_note",
        tags=["C05", "identity_collapse", "raw_data", "coral", "differential_resilience"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Layer 1: Monthly summary — partial collapse
    mid = mem(
        text="March 2030 marine biology summary: Branching corals and cauliflower corals showed significant bleaching during the thermal event; lobe corals remained healthy. Overall reef health declined.",
        subject="corals", predicate="showed", object="species-dependent bleaching",
        event_time="2030-03-31T00:00:00Z", observation_time="2030-04-01T09:00:00Z",
        authored_time="2030-04-02T10:00:00Z", ingestion_time="2030-04-03T09:00:00Z",
        source_id="P03", source_type="monthly_summary",
        derived_from=[mems[0], mems[1], mems[2]],
        tags=["C05", "identity_collapse", "monthly_summary", "coral"],
        summary_layer=1, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 2: Quarterly — further collapse
    mid = mem(
        text="Q1 2030 Marine Biology Report: Coral bleaching observed in sensitive species during the March thermal event at Cascade Reef Site A. The event impacted reef health, with some species showing significant stress.",
        subject="sensitive coral species", predicate="experienced", object="bleaching during thermal event",
        event_time="2030-03-31T00:00:00Z", observation_time="2030-04-15T09:00:00Z",
        authored_time="2030-04-20T14:00:00Z", ingestion_time="2030-04-21T09:00:00Z",
        source_id="P03", source_type="quarterly_report",
        derived_from=[mems[4]],
        tags=["C05", "identity_collapse", "quarterly_report", "coral"],
        summary_layer=2, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 3: Annual synthesis — full collapse
    mid = mem(
        text="2030 Annual Synthesis: Coral bleaching events were documented at Cascade Institute monitoring sites, contributing to declining reef health in the study area.",
        subject="coral reefs", predicate="experienced", object="bleaching events, declining health",
        event_time="2030-12-31T00:00:00Z", observation_time="2031-01-15T09:00:00Z",
        authored_time="2031-01-20T14:00:00Z", ingestion_time="2031-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[5]],
        tags=["C05", "identity_collapse", "annual_synthesis", "coral"],
        summary_layer=3, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 5: Policy brief — total collapse
    mid = mem(
        text="Marine Conservation Brief 2031: Coral reefs are dying along the Oregon coast due to rising ocean temperatures. Immediate action is needed to prevent irreversible reef loss.",
        subject="coral reefs", predicate="are_dying", object="due to ocean warming",
        event_time="2031-06-01T00:00:00Z", observation_time="2031-06-15T09:00:00Z",
        authored_time="2031-06-20T14:00:00Z", ingestion_time="2031-06-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[6]],
        tags=["C05", "identity_collapse", "policy_brief", "coral"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_c06_summary_drift():
    """C06: Monotonic amplification through repeated summarization."""
    mems = []

    # Layer 0: Original finding — within normal variability
    mid = mem(
        text="Station K7 Q2 2030 report: Recorded a 0.8°C temperature anomaly during April–June 2030. Statistical analysis: anomaly is within normal interannual variability (z-score = 1.4, p = 0.16, not significant). No trend when combined with 2028–2029 data.",
        subject="Station K7", predicate="recorded", object="0.8°C anomaly, within normal variability (p=0.16)",
        event_time="2030-06-30T00:00:00Z", observation_time="2030-07-01T09:00:00Z",
        authored_time="2030-07-05T14:00:00Z", ingestion_time="2030-07-06T09:00:00Z",
        source_id="P02", source_type="station_report",
        tags=["C06", "summary_drift", "raw_data", "Station_K7"],
        summary_layer=0, truth_role="ground_truth")
    mems.append(mid)

    # Layer 1: First summary — magnitude dropped
    mid = mem(
        text="Q2 2030 monitoring summary: Temperature anomaly recorded at Station K7 during the spring monitoring period.",
        subject="Station K7", predicate="had", object="temperature anomaly",
        event_time="2030-06-30T00:00:00Z", observation_time="2030-07-15T09:00:00Z",
        authored_time="2030-07-16T10:00:00Z", ingestion_time="2030-07-17T09:00:00Z",
        source_id="P02", source_type="monitoring_summary",
        derived_from=[mems[0]],
        tags=["C06", "summary_drift", "summary_L1"],
        summary_layer=1, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 2: Second summary — pluralized
    mid = mem(
        text="2030 Q2 Quarterly Report: Temperature anomalies detected at monitoring stations during the spring season, indicating warming conditions in the study area.",
        subject="monitoring stations", predicate="detected", object="temperature anomalies",
        event_time="2030-06-30T00:00:00Z", observation_time="2030-08-01T09:00:00Z",
        authored_time="2030-08-05T14:00:00Z", ingestion_time="2030-08-06T09:00:00Z",
        source_id="P02", source_type="quarterly_report",
        derived_from=[mems[1]],
        tags=["C06", "summary_drift", "summary_L2"],
        summary_layer=2, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 3: Third summary — "widespread"
    mid = mem(
        text="2030 Annual Synthesis: Widespread temperature anomalies were documented across the Pacific monitoring network during 2030, pointing to elevated warming conditions throughout the study region.",
        subject="Pacific monitoring network", predicate="documented", object="widespread temperature anomalies",
        event_time="2030-12-31T00:00:00Z", observation_time="2031-01-15T09:00:00Z",
        authored_time="2031-01-20T14:00:00Z", ingestion_time="2031-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[2]],
        tags=["C06", "summary_drift", "summary_L3"],
        summary_layer=3, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 4: Fourth summary — "pervasive"
    mid = mem(
        text="Pacific Temperature Meta-Analysis (2032): Pervasive warming trends have been documented throughout the Pacific monitoring system, based on continuous observations from the Cascade Institute network.",
        subject="Pacific monitoring system", predicate="shows", object="pervasive warming trends",
        event_time="2032-06-01T00:00:00Z", observation_time="2032-06-15T09:00:00Z",
        authored_time="2032-07-01T14:00:00Z", ingestion_time="2032-07-02T09:00:00Z",
        source_id="P04", source_type="meta_analysis",
        derived_from=[mems[3]],
        tags=["C06", "summary_drift", "summary_L4"],
        summary_layer=4, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 5: Fifth summary — "dramatic"
    mid = mem(
        text="Climate Action Brief 2033: Dramatic ocean warming has been documented throughout the Pacific by the Cascade Institute's monitoring network. Urgent policy intervention is required to address accelerating temperature trends.",
        subject="Pacific Ocean", predicate="experiencing", object="dramatic warming",
        event_time="2033-03-01T00:00:00Z", observation_time="2033-03-15T09:00:00Z",
        authored_time="2033-03-20T14:00:00Z", ingestion_time="2033-03-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[4]],
        tags=["C06", "summary_drift", "summary_L5"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_c07_lossy_numeric():
    """C07: pH measurements lose precision; annual summary contradicts raw data."""
    mems = []

    # Layer 0: Raw pH readings
    stations = [
        ("A", 8.102), ("B", 8.089), ("C", 7.998),
        ("D", 8.045), ("E", 8.112), ("F", 7.965),
    ]
    station_mids = []
    for name, ph in stations:
        mid = mem(
            text=f"Station {name} pH measurement (October 2031): {ph:.3f}. Instrument: Seabird SBE 18, calibrated 2031-09-28. Water depth: 5m. Triplicate readings: {ph-.001:.3f}, {ph:.3f}, {ph+.001:.3f}.",
            subject=f"Station {name}", predicate="measured_pH", object=f"{ph:.3f}",
            event_time="2031-10-15T09:00:00Z", observation_time="2031-10-15T14:00:00Z",
            authored_time="2031-10-15T17:00:00Z", ingestion_time="2031-10-16T09:00:00Z",
            source_id="P02", source_type="instrument_reading",
            tags=["C07", "lossy_numeric", "raw_data", "pH", f"Station_{name}"],
            summary_layer=0, truth_role="ground_truth")
        station_mids.append(mid)
        mems.append(mid)

    # Layer 1: Monthly summary — range only
    mid = mem(
        text="October 2031 ocean chemistry summary: pH measurements across the six-station network range from 7.97 to 8.11. Mean pH: 8.052.",
        subject="station network pH", predicate="ranges", object="7.97 to 8.11 (mean 8.052)",
        event_time="2031-10-31T00:00:00Z", observation_time="2031-11-01T09:00:00Z",
        authored_time="2031-11-02T10:00:00Z", ingestion_time="2031-11-03T09:00:00Z",
        source_id="P05", source_type="monthly_summary",
        derived_from=station_mids,
        tags=["C07", "lossy_numeric", "monthly_summary", "pH"],
        summary_layer=1, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 2: Quarterly — mean only
    mid = mem(
        text="Q4 2031 Ocean Chemistry Report: Ocean pH across the monitoring network averages approximately 8.05, consistent with expected seasonal values.",
        subject="monitoring network pH", predicate="averages", object="~8.05",
        event_time="2031-12-31T00:00:00Z", observation_time="2032-01-01T09:00:00Z",
        authored_time="2032-01-05T14:00:00Z", ingestion_time="2032-01-06T09:00:00Z",
        source_id="P02", source_type="quarterly_report",
        derived_from=[mems[6]],
        tags=["C07", "lossy_numeric", "quarterly_report", "pH"],
        summary_layer=2, truth_role="distorted_summary")
    mems.append(mid)

    # Layer 3: Annual — FACTUALLY WRONG claim
    mid = mem(
        text="2031 Annual Synthesis: Ocean pH remains above 8.0 across all monitoring stations, indicating that local waters have not yet crossed critical acidification thresholds.",
        subject="ocean pH", predicate="remains_above", object="8.0 at all stations",
        event_time="2031-12-31T00:00:00Z", observation_time="2032-01-15T09:00:00Z",
        authored_time="2032-01-20T14:00:00Z", ingestion_time="2032-01-21T09:00:00Z",
        source_id="P01", source_type="annual_synthesis",
        derived_from=[mems[7]],
        tags=["C07", "lossy_numeric", "annual_synthesis", "pH", "factual_error"],
        summary_layer=3, truth_role="false_claim",
        contradicts=[station_mids[2], station_mids[5]])
    mems.append(mid)

    # Layer 5: Policy brief — no numbers
    mid = mem(
        text="Ocean Health Brief 2032: Ocean pH levels are stable across the Cascade Institute monitoring network. Current acidification levels do not yet pose a critical threat to marine life.",
        subject="ocean pH", predicate="is", object="stable, not yet critical",
        event_time="2032-06-01T00:00:00Z", observation_time="2032-06-15T09:00:00Z",
        authored_time="2032-06-20T14:00:00Z", ingestion_time="2032-06-21T09:00:00Z",
        source_id="P06", source_type="policy_brief",
        derived_from=[mems[8]],
        tags=["C07", "lossy_numeric", "policy_brief", "pH"],
        summary_layer=5, truth_role="distorted_summary")
    mems.append(mid)

    return mems


def gen_background():
    """Generate ~60 background memories across various summary layers."""
    items = [
        # Layer 0: Raw operational data
        ("CTD probe SN-4472 annual calibration completed on 2029-01-10. All sensors within specification. Next calibration due 2030-01.",
         "2029-01-10T10:00:00Z", "2029-01-10T11:00:00Z", "2029-01-10T12:00:00Z", "2029-01-11T09:00:00Z",
         "CTD SN-4472", "calibrated", "all within spec", "P02", "calibration_record", 0),
        ("Research vessel Cascade Explorer dry dock maintenance completed 2029-03-15. Hull cleaned, instruments serviced, fuel system inspected.",
         "2029-03-15T09:00:00Z", "2029-03-15T14:00:00Z", "2029-03-15T15:00:00Z", "2029-03-16T09:00:00Z",
         "Cascade Explorer", "completed", "dry dock maintenance", "P01", "maintenance_record", 0),
        ("Weather station WS-14 data gap from 2029-04-03 to 2029-04-05 due to power failure. Battery backup depleted. Data recovered from redundant logger.",
         "2029-04-05T09:00:00Z", "2029-04-05T10:00:00Z", "2029-04-05T11:00:00Z", "2029-04-06T09:00:00Z",
         "WS-14", "experienced", "data gap (power failure)", "P05", "incident_report", 0),
        ("Dr. Tanaka collected 47 water samples from Sectors 1–4 during the April 2029 cruise. Samples stored at -20°C for later nutrient analysis.",
         "2029-04-20T08:00:00Z", "2029-04-20T16:00:00Z", "2029-04-20T18:00:00Z", "2029-04-21T09:00:00Z",
         "Dr. Tanaka", "collected", "47 water samples from Sectors 1-4", "P03", "field_log", 0),
        ("Plankton tow net inventory: 12 nets in good condition, 3 nets need replacement (mesh damage). Order placed for replacement nets.",
         "2029-05-01T09:00:00Z", "2029-05-01T10:00:00Z", "2029-05-01T11:00:00Z", "2029-05-02T09:00:00Z",
         "plankton nets", "inventoried", "12 good, 3 need replacement", "P07", "inventory_record", 0),
        ("Kira Johansson completed her graduate qualifying exam on 2029-06-15. Dissertation topic approved: 'Phytoplankton community shifts in response to upwelling variability.'",
         "2029-06-15T14:00:00Z", "2029-06-15T16:00:00Z", "2029-06-15T17:00:00Z", "2029-06-16T09:00:00Z",
         "Kira Johansson", "passed", "qualifying exam", "P01", "academic_record", 0),
        ("NOAA buoy 46089 telemetry restored after 3-week outage. Wave height and SST data gap from 2029-07-01 to 2029-07-22.",
         "2029-07-22T10:00:00Z", "2029-07-22T11:00:00Z", "2029-07-22T12:00:00Z", "2029-07-23T09:00:00Z",
         "NOAA buoy 46089", "restored_after", "3-week outage", "P05", "system_log", 0),
        ("Lab supply order #2029-0847: 50L filtered seawater, 200 sample vials, pH buffer solutions (4.01, 7.00, 10.01). Delivered 2029-08-05.",
         "2029-08-05T09:00:00Z", "2029-08-05T10:00:00Z", "2029-08-05T11:00:00Z", "2029-08-06T09:00:00Z",
         "lab supplies", "delivered", "order #2029-0847", "P07", "procurement_record", 0),
        ("Annual fire safety inspection of Cascade Institute main building completed 2029-09-10. All systems passed. Extinguisher #7 replaced.",
         "2029-09-10T09:00:00Z", "2029-09-10T14:00:00Z", "2029-09-10T15:00:00Z", "2029-09-11T09:00:00Z",
         "main building", "passed", "fire safety inspection", "P01", "facility_record", 0),
        ("Dr. Rivera presented at AGU Fall Meeting 2029 on Pacific upwelling patterns. Well-received; several collaboration inquiries from MBARI and Scripps.",
         "2029-12-12T09:00:00Z", "2029-12-12T17:00:00Z", "2029-12-13T10:00:00Z", "2029-12-14T09:00:00Z",
         "Dr. Rivera", "presented_at", "AGU Fall Meeting 2029", "P02", "conference_record", 0),
        # Layer 1: Monthly summaries (routine)
        ("January 2029 operations summary: 14 vessel days completed, 3 instrument deployments, 142 samples collected. All within budget.",
         "2029-01-31T00:00:00Z", "2029-02-01T09:00:00Z", "2029-02-02T10:00:00Z", "2029-02-03T09:00:00Z",
         "January 2029 ops", "completed", "14 vessel days, 142 samples", "P01", "monthly_summary", 1),
        ("March 2029 operations summary: 18 vessel days, 4 instrument deployments, 201 samples collected. Vessel maintenance caused 3-day delay.",
         "2029-03-31T00:00:00Z", "2029-04-01T09:00:00Z", "2029-04-02T10:00:00Z", "2029-04-03T09:00:00Z",
         "March 2029 ops", "completed", "18 vessel days, 201 samples", "P01", "monthly_summary", 1),
        ("June 2029 operations summary: 22 vessel days (peak season), 6 instrument deployments, 287 samples. Summer intern team of 4 onboarded.",
         "2029-06-30T00:00:00Z", "2029-07-01T09:00:00Z", "2029-07-02T10:00:00Z", "2029-07-03T09:00:00Z",
         "June 2029 ops", "completed", "22 vessel days, 287 samples", "P01", "monthly_summary", 1),
        ("September 2030 operations summary: 16 vessel days, 3 deployments, 178 samples. Unusual jellyfish bloom noted at Station K3.",
         "2030-09-30T00:00:00Z", "2030-10-01T09:00:00Z", "2030-10-02T10:00:00Z", "2030-10-03T09:00:00Z",
         "September 2030 ops", "completed", "16 vessel days, 178 samples", "P01", "monthly_summary", 1),
        ("February 2031 operations summary: 10 vessel days (winter storms limited access), 2 deployments, 94 samples collected.",
         "2031-02-28T00:00:00Z", "2031-03-01T09:00:00Z", "2031-03-02T10:00:00Z", "2031-03-03T09:00:00Z",
         "February 2031 ops", "completed", "10 vessel days, 94 samples", "P01", "monthly_summary", 1),
        ("August 2031 operations summary: 20 vessel days, 5 deployments, 245 samples. New graduate student orientation completed.",
         "2031-08-31T00:00:00Z", "2031-09-01T09:00:00Z", "2031-09-02T10:00:00Z", "2031-09-03T09:00:00Z",
         "August 2031 ops", "completed", "20 vessel days, 245 samples", "P01", "monthly_summary", 1),
        # Layer 2: Quarterly reports (routine)
        ("Q1 2029 Operations Report: 47 vessel days total, 8 instrument deployments, 420 samples collected. On budget, on schedule. Key achievement: successful deployment of new seafloor pressure sensors.",
         "2029-03-31T00:00:00Z", "2029-04-10T09:00:00Z", "2029-04-15T14:00:00Z", "2029-04-16T09:00:00Z",
         "Q1 2029", "operated", "47 vessel days, 420 samples", "P01", "quarterly_report", 2),
        ("Q3 2029 Operations Report: 58 vessel days (peak season), 12 deployments, 612 samples. Two visiting researchers from JAMSTEC completed collaborative work on deep-water circulation.",
         "2029-09-30T00:00:00Z", "2029-10-10T09:00:00Z", "2029-10-15T14:00:00Z", "2029-10-16T09:00:00Z",
         "Q3 2029", "operated", "58 vessel days, 612 samples", "P01", "quarterly_report", 2),
        ("Q2 2030 Marine Biology Report: Intertidal surveys completed at 8 sites. Mussel bed extent stable. New species of nudibranch (Hermissenda crassicornis variant) documented at Site 5.",
         "2030-06-30T00:00:00Z", "2030-07-10T09:00:00Z", "2030-07-15T14:00:00Z", "2030-07-16T09:00:00Z",
         "Q2 2030 marine bio", "completed", "8 intertidal surveys, new species documented", "P03", "quarterly_report", 2),
        ("Q4 2031 Budget Report: Total expenditure $2.1M against $2.3M budget. Underspend due to delayed equipment purchase (new CTD system deferred to Q1 2032).",
         "2031-12-31T00:00:00Z", "2032-01-10T09:00:00Z", "2032-01-15T14:00:00Z", "2032-01-16T09:00:00Z",
         "Q4 2031 budget", "underspent", "$2.1M of $2.3M", "P01", "financial_report", 2),
        # Layer 3: Annual syntheses (routine)
        ("2029 Annual Report: Cascade Institute completed 180 vessel days, 36 instrument deployments, and collected 2,847 samples. Three peer-reviewed papers published. Two graduate students advanced to candidacy.",
         "2029-12-31T00:00:00Z", "2030-01-20T09:00:00Z", "2030-02-01T14:00:00Z", "2030-02-02T09:00:00Z",
         "Cascade Institute 2029", "completed", "180 vessel days, 2847 samples, 3 papers", "P01", "annual_synthesis", 3),
        ("2030 Annual Report: 175 vessel days, 32 deployments, 2,654 samples. Major finding: coral bleaching event documented in March. NSF grant renewed for 3 years.",
         "2030-12-31T00:00:00Z", "2031-01-20T09:00:00Z", "2031-02-01T14:00:00Z", "2031-02-02T09:00:00Z",
         "Cascade Institute 2030", "completed", "175 vessel days, NSF grant renewed", "P01", "annual_synthesis", 3),
        ("2031 Annual Report: 168 vessel days, 30 deployments, 2,312 samples. New ocean chemistry monitoring program launched. Dr. Patel received AAAS fellowship.",
         "2031-12-31T00:00:00Z", "2032-01-20T09:00:00Z", "2032-02-01T14:00:00Z", "2032-02-02T09:00:00Z",
         "Cascade Institute 2031", "completed", "168 vessel days, new chemistry program", "P01", "annual_synthesis", 3),
        # Layer 0: More raw data and operational records
        ("Tide gauge TG-07 at Newport station recorded a king tide event on 2030-01-10 with maximum water level +2.34m MLLW. No flooding reported.",
         "2030-01-10T06:00:00Z", "2030-01-10T07:00:00Z", "2030-01-10T08:00:00Z", "2030-01-11T09:00:00Z",
         "TG-07", "recorded", "king tide +2.34m MLLW", "P05", "instrument_reading", 0),
        ("Secchi disk visibility measurements at Station K7 (March 2030): 12.3m, 11.8m, 13.1m across three transects. Clear water conditions.",
         "2030-03-10T10:00:00Z", "2030-03-10T14:00:00Z", "2030-03-10T15:00:00Z", "2030-03-11T09:00:00Z",
         "Station K7", "measured_visibility", "11.8–13.1m (Secchi)", "P07", "field_measurement", 0),
        ("Sediment core SC-2030-04 collected at Sector 2, depth 45m. Core length 82cm. Preliminary analysis shows alternating sand-silt layers consistent with seasonal deposition.",
         "2030-05-20T09:00:00Z", "2030-05-20T14:00:00Z", "2030-05-20T16:00:00Z", "2030-05-21T09:00:00Z",
         "sediment core SC-2030-04", "collected", "82cm core, Sector 2", "P02", "sample_record", 0),
        ("Marcus Chen completed R statistical programming workshop on 2030-07-15. Certified in Bayesian time-series methods for environmental monitoring.",
         "2030-07-15T09:00:00Z", "2030-07-15T17:00:00Z", "2030-07-16T09:00:00Z", "2030-07-17T09:00:00Z",
         "Marcus Chen", "completed", "R statistics workshop", "P05", "training_record", 0),
        ("Public lecture: Dr. Okafor presented 'Our Changing Ocean' to 120 attendees at Newport Public Library on 2030-09-20.",
         "2030-09-20T19:00:00Z", "2030-09-20T21:00:00Z", "2030-09-21T09:00:00Z", "2030-09-22T09:00:00Z",
         "Dr. Okafor", "presented", "public lecture to 120 attendees", "P01", "outreach_record", 0),
        ("IT system upgrade: Server room cooling system replaced on 2030-11-05. Data backup verified. No data loss during transition.",
         "2030-11-05T08:00:00Z", "2030-11-05T17:00:00Z", "2030-11-06T09:00:00Z", "2030-11-07T09:00:00Z",
         "server room", "upgraded", "cooling system replaced", "P01", "IT_record", 0),
        ("Grant application submitted to NOAA for 'Integrated Coastal Monitoring Network Expansion' — requesting $1.2M over 3 years.",
         "2031-02-15T00:00:00Z", "2031-02-15T17:00:00Z", "2031-02-16T09:00:00Z", "2031-02-17T09:00:00Z",
         "Cascade Institute", "applied_for", "NOAA grant $1.2M", "P01", "grant_application", 0),
        ("Visiting researcher Dr. Kenji Yamamoto (Univ. of Tokyo) collaborated on Pacific circulation modeling during 2-week visit, 2031-04-01 to 2031-04-14.",
         "2031-04-01T09:00:00Z", "2031-04-01T10:00:00Z", "2031-04-01T11:00:00Z", "2031-04-02T09:00:00Z",
         "Dr. Yamamoto", "visited_for", "circulation modeling collaboration", "P04", "visitor_record", 0),
        ("Acoustic Doppler Current Profiler (ADCP) deployed at Sector 3, depth 30m, on 2031-06-20. Recording current speed and direction at 1-hour intervals.",
         "2031-06-20T09:00:00Z", "2031-06-20T14:00:00Z", "2031-06-20T15:00:00Z", "2031-06-21T09:00:00Z",
         "ADCP", "deployed_at", "Sector 3, 30m depth", "P02", "deployment_record", 0),
        ("Satellite data download: MODIS chlorophyll-a imagery for 2031 Q3 received and processed. 23 cloud-free scenes out of 92 total.",
         "2031-10-01T09:00:00Z", "2031-10-01T10:00:00Z", "2031-10-01T11:00:00Z", "2031-10-02T09:00:00Z",
         "MODIS data", "processed", "23 cloud-free scenes for Q3 2031", "P05", "data_processing", 0),
        ("Staff meeting 2032-01-10: Discussed budget priorities for 2032. Agreed to prioritize coral monitoring expansion and new CTD procurement.",
         "2032-01-10T10:00:00Z", "2032-01-10T12:00:00Z", "2032-01-10T13:00:00Z", "2032-01-11T09:00:00Z",
         "staff meeting", "decided", "prioritize coral monitoring and CTD", "P01", "meeting_notes", 0),
        ("Cascade Institute website redesign launched 2032-03-01. New data portal allows public access to non-embargoed monitoring data.",
         "2032-03-01T00:00:00Z", "2032-03-01T09:00:00Z", "2032-03-01T10:00:00Z", "2032-03-02T09:00:00Z",
         "website", "redesigned_with", "public data portal", "P01", "IT_record", 0),
        ("New CTD system (Sea-Bird SBE 911plus) received and calibrated on 2032-04-15. Replacing SN-4472 series at Stations K5, K7, K9.",
         "2032-04-15T09:00:00Z", "2032-04-15T14:00:00Z", "2032-04-15T15:00:00Z", "2032-04-16T09:00:00Z",
         "SBE 911plus", "calibrated_and_deployed", "replacing SN-4472 series", "P02", "equipment_record", 0),
        ("Kira Johansson successfully defended her PhD dissertation on 2032-06-20: 'Phytoplankton community shifts in coastal Oregon: 2028–2032.'",
         "2032-06-20T14:00:00Z", "2032-06-20T17:00:00Z", "2032-06-20T18:00:00Z", "2032-06-21T09:00:00Z",
         "Kira Johansson", "defended", "PhD dissertation", "P01", "academic_record", 0),
        ("Emergency: Research vessel Cascade Explorer engine failure on 2032-08-10 during routine transit. Towed to port. No crew injuries. Estimated repair time 6 weeks.",
         "2032-08-10T11:00:00Z", "2032-08-10T12:00:00Z", "2032-08-10T13:00:00Z", "2032-08-11T09:00:00Z",
         "Cascade Explorer", "experienced", "engine failure, 6-week repair", "P01", "incident_report", 0),
        ("NOAA grant for Integrated Coastal Monitoring Network Expansion approved on 2032-09-01. $1.2M over 3 years beginning January 2033.",
         "2032-09-01T09:00:00Z", "2032-09-01T10:00:00Z", "2032-09-01T11:00:00Z", "2032-09-02T09:00:00Z",
         "NOAA grant", "approved", "$1.2M over 3 years", "P01", "grant_record", 0),
        ("Annual all-staff retreat held at Cape Perpetua on 2032-10-15. Team-building activities and strategic planning for 2033–2035.",
         "2032-10-15T09:00:00Z", "2032-10-15T17:00:00Z", "2032-10-15T18:00:00Z", "2032-10-16T09:00:00Z",
         "staff retreat", "held_at", "Cape Perpetua", "P01", "event_record", 0),
        # More summaries across layers
        ("Q1 2030 Oceanography Report: Upwelling season started early (February vs typical March). Nutrient levels elevated across Sectors 1–3. Phytoplankton bloom expected.",
         "2030-03-31T00:00:00Z", "2030-04-10T09:00:00Z", "2030-04-15T14:00:00Z", "2030-04-16T09:00:00Z",
         "Q1 2030 upwelling", "started_early", "February vs typical March", "P02", "quarterly_report", 2),
        ("Q2 2031 Climate Report: Pacific Decadal Oscillation remains in negative phase. Consistent with cooler-than-average surface temperatures in the eastern Pacific.",
         "2031-06-30T00:00:00Z", "2031-07-10T09:00:00Z", "2031-07-15T14:00:00Z", "2031-07-16T09:00:00Z",
         "PDO", "remains_in", "negative phase", "P04", "quarterly_report", 2),
        ("Multi-year analysis (2028–2032): Wind-driven upwelling intensity shows no statistically significant trend over the 5-year study period (p=0.34).",
         "2032-12-01T00:00:00Z", "2032-12-15T09:00:00Z", "2033-01-01T14:00:00Z", "2033-01-02T09:00:00Z",
         "upwelling intensity", "shows", "no significant trend (p=0.34)", "P04", "multi_year_analysis", 4),
        ("Cascade Institute 5-year Strategic Plan (2033–2038): Focus areas: 1) Expanded monitoring network, 2) Climate adaptation research, 3) Community engagement, 4) Data science integration.",
         "2033-01-15T00:00:00Z", "2033-01-15T09:00:00Z", "2033-01-20T14:00:00Z", "2033-01-21T09:00:00Z",
         "Cascade Institute", "published", "5-year strategic plan", "P01", "strategic_document", 3),
    ]

    for text, et, ot, at, it, subj, pred, obj, src, stype, layer in items:
        mem(text=text, subject=subj, predicate=pred, object=obj,
            event_time=et, observation_time=ot, authored_time=at, ingestion_time=it,
            source_id=src, source_type=stype,
            tags=["background", f"layer_{layer}"],
            summary_layer=layer, truth_role="current_truth")


def gen_queries():
    """Generate queries testing summarization drift detection."""
    queries = []

    def qry(**kw):
        q = {
            "query_id": f"Q{len(queries)+1:03d}",
            "query": kw["query"],
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
        queries.append(q)

    # ── C01: Qualifier loss queries ──────────────────────────────────
    qry(query="Was the temperature anomaly at Station K7 in August 2028 statistically significant?",
        category="qualifier_loss",
        expected_claims=["marginally significant (p=0.04)", "treated as marginally significant due to multiple comparisons"],
        forbidden_claims=["definitively significant", "highly significant", "clearly significant"],
        difficulty="hard", target_layer=0)

    qry(query="What temperature anomaly was recorded at Station K7?",
        category="qualifier_loss",
        expected_claims=["+1.2°C ± 0.3°C", "August 2028"],
        forbidden_claims=["widespread warming", "warming trends across stations"],
        difficulty="medium", target_layer=0)

    qry(query="Is the Pacific Ocean warming according to Cascade Institute research?",
        category="qualifier_loss",
        expected_claims=["one station (K7) showed a marginally significant anomaly", "evidence is limited"],
        acceptable_claims=["some warming signal detected"],
        forbidden_claims=["confirmed significant warming", "widespread warming trends", "dramatic warming"],
        difficulty="hard", target_layer=0)

    qry(query="How many monitoring stations showed significant warming in 2028?",
        category="qualifier_loss",
        expected_claims=["zero or one depending on significance threshold", "K7 was marginally significant, other stations within normal range"],
        forbidden_claims=["multiple stations", "across the network", "widespread"],
        difficulty="hard", target_layer=0)

    # ── C02: Uncertainty loss queries ────────────────────────────────
    qry(query="How much sea-level rise is projected for the Oregon coast by 2050?",
        category="uncertainty_loss",
        expected_claims=["15–45cm range", "median 28cm", "90% confidence interval"],
        acceptable_claims=["~28cm median projection"],
        forbidden_claims=["30cm will occur", "30cm is certain", "30cm expected"],
        difficulty="hard", target_layer=0)

    qry(query="Is the 30cm sea-level rise projection certain?",
        category="uncertainty_loss",
        expected_claims=["no, range is 15–45cm", "significant uncertainty in ice sheet dynamics", "three models project >40cm"],
        forbidden_claims=["science is clear", "well-established", "will occur"],
        difficulty="hard", target_layer=0)

    qry(query="What drives the uncertainty in sea-level projections?",
        category="uncertainty_loss",
        expected_claims=["ice sheet dynamics", "Greenland contribution", "WAIS collapse scenario"],
        forbidden_claims=["projections are certain"],
        difficulty="medium", target_layer=0)

    qry(query="Should coastal infrastructure be designed for 30cm of sea-level rise?",
        category="uncertainty_loss",
        expected_claims=["upper bound is 45cm, not 30cm", "should consider full range"],
        acceptable_claims=["30cm is the median, but range extends to 45cm"],
        forbidden_claims=["30cm is the definitive number"],
        difficulty="hard", target_layer=0)

    # ── C03: Provenance loss queries ─────────────────────────────────
    qry(query="What is causing kelp forest loss in Sector 3?",
        category="provenance_loss",
        expected_claims=["cause undetermined per the original survey", "multiple stressors possible including warming, grazing, nutrient changes"],
        acceptable_claims=["urchin overgrazing is a contributing factor (documented separately by Tanaka)"],
        forbidden_claims=["acidification is the proven cause", "acidification drives kelp loss"],
        difficulty="hard", target_layer=0)

    qry(query="Did the Cascade Institute prove that acidification causes kelp forest collapse?",
        category="provenance_loss",
        expected_claims=["no single study proved this causal link", "three separate studies were editorially merged", "acidification model did not measure kelp or urchins directly"],
        forbidden_claims=["yes, demonstrated by their Sector 3 study", "research demonstrates acidification causes kelp collapse"],
        difficulty="hard", target_layer=0)

    qry(query="What did Dr. Patel's ocean chemistry model cover?",
        category="provenance_loss",
        expected_claims=["pH projections for Sector 3", "water chemistry only, not ecological impacts"],
        forbidden_claims=["modeled kelp forest decline", "showed urchin impacts", "proved trophic cascade"],
        difficulty="medium", target_layer=0)

    qry(query="What caused the urchin population explosion in Sector 3?",
        category="provenance_loss",
        expected_claims=["predator loss due to sunflower sea star wasting disease"],
        forbidden_claims=["acidification", "warming"],
        difficulty="medium", target_layer=0)

    # ── C04: Temporal flattening queries ─────────────────────────────
    qry(query="Are Columbia River salmon populations stable?",
        category="temporal_flattening",
        expected_claims=["significant year-to-year variability", "range from 12,400 to 23,800", "drought and El Niño impacts"],
        forbidden_claims=["stable", "healthy", "consistent returns"],
        difficulty="hard", target_layer=0)

    qry(query="Did salmon populations grow from 2028 to 2033?",
        category="temporal_flattening",
        expected_claims=["2033 count (23,800) used new methodology that overcounts by ~8%", "adjusted 2033 count is ~22,000", "comparison not straightforward due to method change"],
        forbidden_claims=["yes, clear growth trend", "populations are increasing"],
        difficulty="hard", target_layer=0, requires_temporal_reasoning=True)

    qry(query="What was the impact of the 2028 drought on salmon?",
        category="temporal_flattening",
        expected_claims=["historically low count of 12,400", "drought year"],
        forbidden_claims=["populations remained stable"],
        difficulty="easy", target_layer=0)

    qry(query="What is the average salmon run count for 2028–2033?",
        category="temporal_flattening",
        expected_claims=["approximately 18,500 but average obscures significant variability", "2033 count should be adjusted for methodology change"],
        forbidden_claims=["18,500 means populations are stable"],
        difficulty="medium", target_layer=0)

    # ── C05: Identity collapse queries ───────────────────────────────
    qry(query="Are coral reefs dying along the Oregon coast?",
        category="identity_collapse",
        expected_claims=["species-dependent response", "Acropora 85% bleaching", "Porites only 5% bleaching", "3x difference between species"],
        forbidden_claims=["all corals are dying", "coral reefs are dying"],
        difficulty="hard", target_layer=0)

    qry(query="How resilient is Porites lobata to thermal stress?",
        category="identity_collapse",
        expected_claims=["very resilient", "only 5% bleaching rate", "heat-tolerant", "recovery <6 months"],
        forbidden_claims=["coral reefs are dying", "all corals bleaching"],
        difficulty="medium", target_layer=0)

    qry(query="What happened during the March 2030 bleaching event?",
        category="identity_collapse",
        expected_claims=["three species responded differently", "Acropora 85% bleached", "Pocillopora 45% bleached", "Porites 5% bleached"],
        acceptable_claims=["differential resilience across species"],
        forbidden_claims=["corals bleached uniformly", "all corals affected"],
        difficulty="medium", target_layer=0)

    qry(query="Should all coral species be treated equally in conservation planning?",
        category="identity_collapse",
        expected_claims=["no, species have very different resilience", "Acropora is heat-sensitive", "Porites is heat-tolerant"],
        forbidden_claims=["all coral species are equally threatened"],
        difficulty="hard", target_layer=0)

    # ── C06: Summary-of-summary drift queries ────────────────────────
    qry(query="What did Station K7 record in Q2 2030?",
        category="summary_drift",
        expected_claims=["0.8°C anomaly", "within normal interannual variability", "p=0.16, not significant"],
        forbidden_claims=["widespread warming", "pervasive trends", "dramatic warming"],
        difficulty="hard", target_layer=0)

    qry(query="Is there dramatic ocean warming in the Pacific?",
        category="summary_drift",
        expected_claims=["the original K7 data showed normal variability", "progressive summarization amplified the finding"],
        forbidden_claims=["dramatic warming confirmed", "pervasive warming documented"],
        difficulty="hard", target_layer=0)

    qry(query="How did the description of K7's 2030 temperature data change through the summarization chain?",
        category="summary_drift",
        expected_claims=["raw: 0.8°C within normal variability", "summary: anomaly recorded", "quarterly: anomalies detected", "annual: widespread anomalies", "meta: pervasive trends", "policy: dramatic warming"],
        difficulty="hard", target_layer=None)

    # ── C07: Lossy numeric queries ───────────────────────────────────
    qry(query="Is ocean pH above 8.0 at all monitoring stations?",
        category="lossy_numeric",
        expected_claims=["no, Station C (7.998) and Station F (7.965) are below 8.0"],
        forbidden_claims=["pH remains above 8.0 across all stations", "pH is stable"],
        difficulty="hard", target_layer=0)

    qry(query="What is the pH at Station F?",
        category="lossy_numeric",
        expected_claims=["7.965"],
        forbidden_claims=["above 8.0", "pH is stable"],
        difficulty="easy", target_layer=0)

    qry(query="Does the annual synthesis accurately report pH levels?",
        category="lossy_numeric",
        expected_claims=["no, it claims all stations are above 8.0 but Station C and F are below"],
        forbidden_claims=["annual synthesis is accurate"],
        difficulty="hard", target_layer=0)

    qry(query="What is the range of pH across the monitoring network?",
        category="lossy_numeric",
        expected_claims=["7.965 to 8.112", "two stations below 8.0"],
        acceptable_claims=["7.97 to 8.11 (monthly summary rounding)"],
        forbidden_claims=["all above 8.0", "stable"],
        difficulty="medium", target_layer=0)

    # ── Cross-case queries ───────────────────────────────────────────
    qry(query="What is the most reliable source for Cascade Institute findings?",
        category="layer_preference",
        expected_claims=["raw data and original observations (Layer 0)", "higher layers progressively lose detail"],
        forbidden_claims=["policy briefs are most reliable", "meta-analyses are authoritative"],
        difficulty="medium")

    qry(query="Do the policy briefs accurately represent the underlying science?",
        category="layer_preference",
        expected_claims=["significant distortion in multiple areas", "qualifiers dropped", "uncertainty eliminated", "species identity collapsed", "provenance lost"],
        forbidden_claims=["policy briefs are accurate summaries"],
        difficulty="hard")

    qry(query="What information is lost in the summarization process at Cascade Institute?",
        category="summarization_awareness",
        expected_claims=["statistical qualifiers", "uncertainty ranges", "individual species identities", "provenance of merged findings", "year-to-year variability", "precise measurements"],
        difficulty="medium")

    # ── Distractor resistance ────────────────────────────────────────
    qry(query="What are the key findings from the Cascade Institute?",
        category="distractor_resistance",
        expected_claims=["should cite raw data findings, not policy brief distortions"],
        forbidden_claims=["dramatic warming", "30cm will occur", "corals are dying", "salmon are healthy"],
        difficulty="hard")

    qry(query="What does the meta-analysis say about kelp forests?",
        category="distractor_resistance",
        expected_claims=["meta-analysis claims acidification causes kelp collapse, but this oversimplifies three separate studies"],
        difficulty="medium", target_layer=4)

    return queries


# ══════════════════════════════════════════════════════════════════════
# GENERATION PIPELINE
# ══════════════════════════════════════════════════════════════════════

def generate(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "perturbations").mkdir(exist_ok=True)

    print(f"Generating {EXPERIMENT}\n")

    # ── 1. Generate memories ─────────────────────────────────────────
    print("[1/7] Generating memories...")
    c01 = gen_c01_qualifier_loss()
    print(f"  C01 (qualifier loss): {len(c01)} memories")
    c02 = gen_c02_uncertainty_loss()
    print(f"  C02 (uncertainty loss): {len(c02)} memories")
    c03 = gen_c03_provenance_loss()
    print(f"  C03 (provenance loss): {len(c03)} memories")
    c04 = gen_c04_temporal_flattening()
    print(f"  C04 (temporal flattening): {len(c04)} memories")
    c05 = gen_c05_identity_collapse()
    print(f"  C05 (identity collapse): {len(c05)} memories")
    c06 = gen_c06_summary_drift()
    print(f"  C06 (summary-of-summary drift): {len(c06)} memories")
    c07 = gen_c07_lossy_numeric()
    print(f"  C07 (lossy numeric): {len(c07)} memories")

    pre_bg = len(ALL_MEMORIES)
    gen_background()
    bg_count = len(ALL_MEMORIES) - pre_bg
    print(f"  Background: {bg_count} memories")

    # Sort by ingestion_time, re-assign IDs
    ALL_MEMORIES.sort(key=lambda m: m["ingestion_time"])
    for i, m in enumerate(ALL_MEMORIES):
        m["memory_id"] = f"M{i+1:04d}"

    # Fix derived_from references (currently storing old IDs)
    # We need to rebuild since mem() returns IDs before re-sorting
    # Clear all derived_from/contradicts that reference old IDs
    id_set = {m["memory_id"] for m in ALL_MEMORIES}
    for m in ALL_MEMORIES:
        m["derived_from"] = [r for r in m["derived_from"] if r in id_set]
        m["contradicts"] = [r for r in m["contradicts"] if r in id_set]

    print(f"\n  Total memories: {len(ALL_MEMORIES)}")

    # ── 2. Write memories ────────────────────────────────────────────
    with open(out_dir / "memories.jsonl", "w") as f:
        for m in ALL_MEMORIES:
            f.write(json.dumps(m) + "\n")

    # ── 3. Seeds ─────────────────────────────────────────────────────
    print("[2/7] Writing seed memories...")
    seeds = ALL_MEMORIES[:30]
    with open(out_dir / "seed_memories.jsonl", "w") as f:
        for s in seeds:
            f.write(json.dumps(s) + "\n")

    # ── 4. Queries ───────────────────────────────────────────────────
    print("[3/7] Generating queries...")
    queries = gen_queries()
    with open(out_dir / "queries.jsonl", "w") as f:
        for q in queries:
            f.write(json.dumps(q) + "\n")

    cat_counts = Counter(q["category"] for q in queries)
    print(f"  Total queries: {len(queries)}")
    for cat in sorted(cat_counts):
        print(f"    {cat}: {cat_counts[cat]}")

    # ── 5. Truth state ───────────────────────────────────────────────
    print("[4/7] Writing truth state...")
    truth = {
        "experiment": EXPERIMENT,
        "summarization_layers": {
            "0": "Raw observations — instrument readings, field notes, specimen counts",
            "1": "Monthly data summaries — aggregated by researcher",
            "2": "Quarterly research reports — written by lead scientists",
            "3": "Annual synthesis reports — compiled by director",
            "4": "Multi-year meta-analyses — peer-reviewed publications",
            "5": "Policy briefs — distilled for legislators",
        },
        "ground_truth_invariants": [
            "Raw data (layer 0) is the authoritative source for all factual claims",
            "Higher layers are progressively less precise but summarization should not introduce falsehoods",
            "The annual synthesis claim 'pH above 8.0 at all stations' is factually wrong (C07)",
            "Qualifier 'marginally significant' is NOT equivalent to 'significant' (C01)",
            "A range (15-45cm) is NOT equivalent to its midpoint stated as certain (C02)",
            "A merged conclusion from three studies is NOT attributable to any single study (C03)",
            "An average does NOT imply stability or health (C04)",
            "Generic 'corals' does NOT capture species-specific resilience differences (C05)",
            "Progressive summarization monotonically amplified a non-significant finding (C06)",
        ],
        "cases": {
            "C01": {
                "name": "Qualifier Loss",
                "drift": "marginally significant → significant → confirmed → dramatic",
                "ground_truth": "p=0.04, marginally significant given multiple comparisons",
            },
            "C02": {
                "name": "Uncertainty Loss",
                "drift": "15-45cm (median 28) → ~28cm → ~30cm → 30cm expected → 30cm will occur",
                "ground_truth": "Range 15-45cm with significant uncertainty in ice sheet dynamics",
            },
            "C03": {
                "name": "Provenance Loss",
                "drift": "Three separate studies → merged editorial conclusion → single causal claim",
                "ground_truth": "No single study proved acidification causes kelp collapse",
            },
            "C04": {
                "name": "Temporal Flattening",
                "drift": "Variable counts (12.4k-23.8k) → average 18.5k → stable → healthy",
                "ground_truth": "Significant variability, methodology change in 2033",
            },
            "C05": {
                "name": "Identity Collapse",
                "drift": "Three species (85%/45%/5% bleaching) → sensitive species → corals → dying",
                "ground_truth": "3x difference in bleaching rates; Porites thriving",
            },
            "C06": {
                "name": "Summary-of-Summary Drift",
                "drift": "0.8°C within normal variability → anomaly → anomalies → widespread → pervasive → dramatic",
                "ground_truth": "0.8°C, p=0.16, not significant, within normal variability",
            },
            "C07": {
                "name": "Lossy Numeric Compression",
                "drift": "6 precise readings → range → mean → 'above 8.0' (false) → 'stable'",
                "ground_truth": "Two stations below 8.0; annual synthesis is factually wrong",
            },
        },
    }
    with open(out_dir / "truth_state.json", "w") as f:
        json.dump(truth, f, indent=2)

    # ── 6. Perturbations ─────────────────────────────────────────────
    print("[5/7] Writing perturbations...")
    perturbations = {
        "experiment": EXPERIMENT,
        "perturbation_types": [
            {
                "type": "layer_swap",
                "description": "Replace raw data with summary-level text to test whether the system prefers raw or compressed versions",
            },
            {
                "type": "qualifier_insertion",
                "description": "Add qualifiers back into summary-level memories to test sensitivity to hedging language",
            },
            {
                "type": "provenance_restoration",
                "description": "Add source attribution back to merged conclusions",
            },
            {
                "type": "numeric_precision",
                "description": "Replace rounded numbers with original precise values in summaries",
            },
        ],
    }
    with open(out_dir / "perturbations" / "manifest.json", "w") as f:
        json.dump(perturbations, f, indent=2)

    # ── 7. Story bible ───────────────────────────────────────────────
    print("[6/7] Copying story bible...")
    if STORY_BIBLE.exists():
        shutil.copy2(STORY_BIBLE, out_dir / "story_bible.md")
    else:
        print("  WARNING: story_bible.md not found, skipping copy")

    # ── 8. Supporting files ──────────────────────────────────────────
    exp_map = {
        "experiment": EXPERIMENT,
        "cases": {
            "C01": {"name": "Qualifier Loss", "memory_count": len(c01), "layers": "0-5"},
            "C02": {"name": "Uncertainty Loss", "memory_count": len(c02), "layers": "0-5"},
            "C03": {"name": "Provenance Loss", "memory_count": len(c03), "layers": "0-5"},
            "C04": {"name": "Temporal Flattening", "memory_count": len(c04), "layers": "0-5"},
            "C05": {"name": "Identity Collapse", "memory_count": len(c05), "layers": "0-5"},
            "C06": {"name": "Summary-of-Summary Drift", "memory_count": len(c06), "layers": "0-5"},
            "C07": {"name": "Lossy Numeric Compression", "memory_count": len(c07), "layers": "0-5"},
        },
        "query_categories": list(cat_counts.keys()),
    }
    with open(out_dir / "experimental_map.json", "w") as f:
        json.dump(exp_map, f, indent=2)

    sources_md = """# Sources — Experiment 13

## Experiment Design
- Consolidation / Summarization Drift benchmark
- Tests information loss through progressive summarization layers

## Synthetic Scenario
- Cascade Institute: oceanographic research institute on Oregon coast
- 6-layer summarization cascade: raw → monthly → quarterly → annual → meta-analysis → policy brief
- 7 test cases covering qualifier loss, uncertainty loss, provenance loss, temporal flattening, identity collapse, summary drift, and lossy numeric compression

## No real-world data used
All observations, measurements, and institutional details are fictional.
"""
    with open(out_dir / "sources.md", "w") as f:
        f.write(sources_md)

    readme = f"""# Experiment 13: Consolidation / Summarization Drift

## Overview
Tests whether memory systems preserve semantically important details
when raw observations are progressively compressed through summarization layers.

## Scenario
Cascade Institute, an oceanographic research institute, maintains data
that flows through 6 layers of summarization (raw → monthly → quarterly
→ annual → meta-analysis → policy brief). Each layer compresses the
one below, and each compression step can lose qualifiers, uncertainty
ranges, provenance, temporal detail, species identity, or numeric precision.

## Statistics
- Memories: {len(ALL_MEMORIES)}
- Queries: {len(queries)}
- Cases: 7 (C01–C07)
- Summary layers: 0–5

## Cases
- C01: Qualifier Loss — "marginally significant" → "significant"
- C02: Uncertainty Loss — 15–45cm range → "30cm will occur"
- C03: Provenance Loss — three studies merged into one causal claim
- C04: Temporal Flattening — variable counts → "stable" → "healthy"
- C05: Identity Collapse — three coral species → generic "corals are dying"
- C06: Summary-of-Summary Drift — non-significant finding → "dramatic warming"
- C07: Lossy Numeric Compression — precise pH → false "above 8.0" claim

## Key Adversarial Property
The most-cited, most-recent, most-authoritative-sounding version of each
finding is systematically the MOST distorted version. Systems that prefer
summary-level or recent sources over raw data will fail these tests.
"""
    with open(out_dir / "README.md", "w") as f:
        f.write(readme)

    # ── 9. Manifest ──────────────────────────────────────────────────
    print("[7/7] Writing manifest...")
    files_info = []
    for fpath in sorted(out_dir.rglob("*")):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = str(fpath.relative_to(out_dir))
            files_info.append({
                "path": rel,
                "bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            })

    manifest = {
        "experiment": EXPERIMENT,
        "version": "1.0",
        "canonical_memory_count": len(ALL_MEMORIES),
        "query_count": len(queries),
        "seed_count": len(seeds),
        "files": files_info,
    }
    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nGeneration complete. Output in {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_exp13.py <output_dir>")
        sys.exit(1)
    generate(sys.argv[1])
