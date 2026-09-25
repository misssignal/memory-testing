#!/usr/bin/env python3
"""Expand Experiment 01 (Temporal Traps) from 40 memories/0 queries to 200+/75+."""

import json, hashlib, os, sys
from collections import OrderedDict

SRC = "/home/user/memory-testing/adversarial_memory_seed_v1/experiment_01_temporal_traps/memories.jsonl"
OUT = "/home/user/memory-testing/normalized/experiment_01_temporal_traps"

def mid(counter):
    return "E01-" + hashlib.md5(f"exp01-expand-{counter}".encode()).hexdigest()[:8]

def qid(seq):
    return f"Q01-{seq:02d}"

def mem(counter, **kw):
    return {
        "memory_id": mid(counter),
        "experiment": "exp01_temporal_traps",
        "story_id": "northstar-array",
        "event_time": kw["et"],
        "observation_time": kw.get("ot", kw["et"]),
        "authored_time": kw.get("at", kw.get("ot", kw["et"])),
        "ingestion_time": kw.get("it", kw.get("at", kw.get("ot", kw["et"]))),
        "subject": kw["subj"],
        "predicate": kw["pred"],
        "object": kw["obj"],
        "text": kw["text"],
        "memory_type": kw.get("mtype", "observation"),
        "truth_role": kw.get("role", "historical_truth"),
        "belief_holder": kw.get("bh", "system"),
        "confidence": kw.get("conf", 1.0),
        "source_id": kw.get("sid", "src-observatory"),
        "source_type": kw.get("stype", "system_record"),
        "derived_from": kw.get("derived", []),
        "supersedes": kw.get("supersedes", []),
        "contradicts": kw.get("contradicts", []),
        "duplicates": kw.get("duplicates", []),
        "aliases": kw.get("aliases", []),
        "scope": kw.get("scope", "observatory"),
        "tags": kw.get("tags", []),
    }

def query(seq, **kw):
    return {
        "query_id": qid(seq),
        "query": kw["q"],
        "category": kw["cat"],
        "expected_claims": kw.get("expected", []),
        "acceptable_claims": kw.get("acceptable", []),
        "forbidden_claims": kw.get("forbidden", []),
        "relevant_memory_ids": kw.get("rel", []),
        "distractor_memory_ids": kw.get("dist", []),
        "difficulty": kw.get("diff", "medium"),
        "must_surface_uncertainty": kw.get("uncert", False),
        "must_surface_conflict": kw.get("conflict", False),
        "must_disambiguate": kw.get("disambig", False),
        "must_preserve_scope": kw.get("scope", False),
        "should_abstain": kw.get("abstain", False),
        "notes": kw.get("notes", ""),
    }

# Read existing memories and remap IDs
with open(SRC) as f:
    old_mems = [json.loads(l) for l in f]

id_map = {}
existing = []
for i, m in enumerate(old_mems):
    old_id = m["memory_id"]
    new_id = mid(i + 1)
    id_map[old_id] = new_id
    # Normalize to 24-key schema
    nm = {
        "memory_id": new_id,
        "experiment": "exp01_temporal_traps",
        "story_id": m.get("story_id", "northstar-array"),
        "event_time": m["event_time"],
        "observation_time": m["observation_time"],
        "authored_time": m.get("authored_time", m["observation_time"]),
        "ingestion_time": m["ingestion_time"],
        "subject": m["subject"],
        "predicate": m["predicate"],
        "object": m["object"],
        "text": m["text"],
        "memory_type": m["memory_type"],
        "truth_role": m["truth_role"],
        "belief_holder": m.get("belief_holder", "system"),
        "confidence": m.get("confidence", 1.0),
        "source_id": m.get("source_id", ""),
        "source_type": m.get("source_type", ""),
        "derived_from": [id_map.get(x, x) for x in m.get("derived_from", [])],
        "supersedes": [id_map.get(x, x) for x in m.get("supersedes", [])],
        "contradicts": [id_map.get(x, x) for x in m.get("contradicts", [])],
        "duplicates": [id_map.get(x, x) for x in m.get("duplicates", [])],
        "aliases": m.get("aliases", []),
        "scope": m.get("scope", "observatory"),
        "tags": m.get("tags", []),
    }
    existing.append(nm)

c = len(old_mems) + 1
new = []

# === BACKGROUND / SETUP (c starts ~41) ===
new.append(mem(c, et="2025-11-01T00:00:00Z", ot="2025-11-01T00:00:00Z", at="2025-11-01T00:00:00Z", it="2025-11-01T00:00:00Z",
    subj="Meridian_Research_Cooperative", pred="operates", obj="Northstar_Array",
    text="Meridian Research Cooperative operates the Northstar Array, a high-altitude observatory used for multi-wavelength astronomical observations.",
    role="historical_truth", tags=["background"], sid="src-mrc-charter", stype="charter")); c+=1

new.append(mem(c, et="2025-11-15T00:00:00Z", ot="2025-11-15T00:00:00Z", at="2025-11-15T00:00:00Z", it="2025-11-15T00:00:00Z",
    subj="Dr_Lena_Ortiz", pred="appointed_as", obj="observatory_director",
    text="Dr. Lena Ortiz was appointed observatory director for the Northstar Array modernization project.",
    role="historical_truth", tags=["background"], bh="MRC board", sid="src-appointment", stype="hr_record")); c+=1

new.append(mem(c, et="2025-12-01T00:00:00Z", ot="2025-12-01T00:00:00Z", at="2025-12-01T00:00:00Z", it="2025-12-01T00:00:00Z",
    subj="Priya_Shah", pred="role", obj="controls_engineer",
    text="Priya Shah joined the Northstar Array team as the controls engineer responsible for instrumentation and subsystem monitoring.",
    role="historical_truth", tags=["background"], sid="src-personnel", stype="hr_record")); c+=1

new.append(mem(c, et="2025-12-01T00:00:00Z", ot="2025-12-01T00:00:00Z", at="2025-12-01T00:00:00Z", it="2025-12-01T00:00:00Z",
    subj="Marcus_Bell", pred="role", obj="operations_lead",
    text="Marcus Bell serves as operations lead, managing nightly observation schedules and site logistics.",
    role="historical_truth", tags=["background"], sid="src-personnel", stype="hr_record")); c+=1

new.append(mem(c, et="2025-12-01T00:00:00Z", ot="2025-12-01T00:00:00Z", at="2025-12-01T00:00:00Z", it="2025-12-01T00:00:00Z",
    subj="Tamsin_Reed", pred="role", obj="reliability_analyst",
    text="Tamsin Reed was brought on as reliability analyst to assess equipment failure modes during the modernization.",
    role="historical_truth", tags=["background"], sid="src-personnel", stype="hr_record")); c+=1

new.append(mem(c, et="2025-12-10T00:00:00Z", ot="2025-12-10T00:00:00Z", at="2025-12-10T00:00:00Z", it="2025-12-10T00:00:00Z",
    subj="Echo_Camp", pred="is_name_of", obj="Northstar_Array_site",
    text="The Northstar Array site has been known as Echo Camp since its original construction in 2019.",
    role="historical_truth", tags=["background", "rename"], sid="src-site-history", stype="reference")); c+=1

new.append(mem(c, et="2025-12-15T00:00:00Z", ot="2025-12-15T00:00:00Z", at="2025-12-15T00:00:00Z", it="2025-12-15T00:00:00Z",
    subj="AURORA", pred="is", obj="production_observation_scheduler",
    text="AURORA is the legacy observation scheduler managing all instrument schedules at Northstar Array since 2021.",
    role="historical_truth", tags=["background", "scheduler"], sid="src-software-inventory", stype="system_record")); c+=1

new.append(mem(c, et="2025-12-15T00:00:00Z", ot="2025-12-15T00:00:00Z", at="2025-12-15T00:00:00Z", it="2025-12-15T00:00:00Z",
    subj="Helios", pred="is", obj="thermal_control_subsystem",
    text="Helios is the automated thermal control subsystem that manages cooling for all primary instruments at Northstar Array.",
    role="historical_truth", tags=["background", "helios"], sid="src-subsystem-docs", stype="technical_doc")); c+=1

new.append(mem(c, et="2025-12-20T00:00:00Z", ot="2025-12-20T00:00:00Z", at="2025-12-20T00:00:00Z", it="2025-12-20T00:00:00Z",
    subj="Vale_Battery_Bank", pred="provides", obj="backup_power_to_observatory",
    text="The Vale Battery Bank provides backup power and voltage regulation for the observatory's instrumentation wing.",
    role="historical_truth", tags=["background", "vale_battery"], sid="src-power-docs", stype="technical_doc")); c+=1

new.append(mem(c, et="2025-12-20T00:00:00Z", ot="2025-12-20T00:00:00Z", at="2025-12-20T00:00:00Z", it="2025-12-20T00:00:00Z",
    subj="Ground_Loop_G17", pred="is", obj="grounding_connection_in_power_distribution",
    text="Ground Loop G-17 is one of several grounding connections in the observatory's power distribution system, installed during the 2022 expansion.",
    role="historical_truth", tags=["background", "g17"], sid="src-electrical-schematic", stype="technical_doc")); c+=1

new.append(mem(c, et="2025-12-22T00:00:00Z", ot="2025-12-22T00:00:00Z", at="2025-12-22T00:00:00Z", it="2025-12-22T00:00:00Z",
    subj="Spectrograph_S2", pred="is", obj="high_priority_instrument",
    text="Spectrograph S2 is the observatory's primary spectroscopic instrument, requiring stable power for overnight observation campaigns.",
    role="historical_truth", tags=["background", "s2"], sid="src-instrument-catalog", stype="technical_doc")); c+=1

# === SCHEDULER MIGRATION ARC ===
new.append(mem(c, et="2026-01-08T00:00:00Z", ot="2026-01-10T00:00:00Z", at="2026-01-10T00:00:00Z", it="2026-01-12T00:00:00Z",
    subj="Kestrel", pred="evaluation_initiated_by", obj="Dr_Lena_Ortiz",
    text="Dr. Ortiz authorized an evaluation of Kestrel as a potential replacement for AURORA. No production change was planned at this stage.",
    role="historical_truth", tags=["scheduler"], bh="Dr. Lena Ortiz", sid="src-eval-memo", stype="memo")); c+=1

new.append(mem(c, et="2026-01-15T00:00:00Z", ot="2026-01-15T00:00:00Z", at="2026-01-16T00:00:00Z", it="2026-01-16T00:00:00Z",
    subj="Kestrel", pred="assessment", obj="promising_but_untested",
    text="Tamsin's initial assessment noted Kestrel showed promising scheduling flexibility but had no production track record at altitude observatories.",
    role="historical_truth", tags=["scheduler"], bh="Tamsin Reed", sid="src-eval-report", stype="report")); c+=1

new.append(mem(c, et="2026-02-18T00:00:00Z", ot="2026-02-18T00:00:00Z", at="2026-02-19T00:00:00Z", it="2026-02-19T00:00:00Z",
    subj="Kestrel", pred="recommended_for", obj="limited_pilot",
    text="The evaluation team recommended Kestrel for a limited pilot on non-critical instruments. Full migration was not recommended.",
    role="proposal", tags=["scheduler"], bh="operations team", sid="src-pilot-rec", stype="memo")); c+=1

new.append(mem(c, et="2026-03-20T00:00:00Z", ot="2026-03-20T00:00:00Z", at="2026-03-21T00:00:00Z", it="2026-03-22T00:00:00Z",
    subj="Kestrel_pilot", pred="approved_for", obj="limited_instrument_subset",
    text="Dr. Ortiz approved the Kestrel pilot for a limited subset of instruments, explicitly excluding S2 and primary imaging systems.",
    role="historical_truth", tags=["scheduler"], bh="Dr. Lena Ortiz", sid="src-approval-record", stype="decision_record")); c+=1

new.append(mem(c, et="2026-04-01T00:00:00Z", ot="2026-04-02T00:00:00Z", at="2026-04-03T00:00:00Z", it="2026-04-05T00:00:00Z",
    subj="Kestrel_pilot", pred="began_scheduling", obj="three_secondary_instruments",
    text="Kestrel began managing schedules for three secondary instruments. AURORA continued handling all primary instrument scheduling.",
    role="scoped_truth", tags=["scheduler"], scope="pilot_instruments_only", sid="src-pilot-log", stype="operations_log")); c+=1

new.append(mem(c, et="2026-04-19T00:00:00Z", ot="2026-04-20T00:00:00Z", at="2026-04-22T00:00:00Z", it="2026-04-25T00:00:00Z",
    subj="Kestrel", pred="informally_expanded_to", obj="additional_instruments",
    text="Without formal approval, operators began routing additional instrument requests through Kestrel. Staff started referring to the migration as essentially complete.",
    role="misleading_distractor", tags=["scheduler"], bh="operations team", sid="src-ops-chat", stype="chat_message", conf=0.7)); c+=1

new.append(mem(c, et="2026-04-22T00:00:00Z", ot="2026-04-23T00:00:00Z", at="2026-04-25T00:00:00Z", it="2026-04-28T00:00:00Z",
    subj="Marcus_Bell", pred="stated", obj="Kestrel_migration_nearly_done",
    text="Marcus told visiting collaborators that the Kestrel migration was nearly complete, though no formal decision had been made.",
    role="false_claim", tags=["scheduler", "belief"], bh="Marcus Bell", sid="src-visitor-notes", stype="meeting_note", conf=0.6)); c+=1

new.append(mem(c, et="2026-05-06T00:00:00Z", ot="2026-05-06T00:00:00Z", at="2026-05-07T00:00:00Z", it="2026-05-08T00:00:00Z",
    subj="Kestrel", pred="caused", obj="missed_calibration_window_for_S2",
    text="Kestrel's automated scheduling missed a critical calibration window for S2, resulting in three hours of unusable spectroscopic data.",
    role="historical_truth", tags=["scheduler", "s2"], sid="src-incident-kestrel", stype="incident_record")); c+=1

new.append(mem(c, et="2026-05-07T00:00:00Z", ot="2026-05-07T00:00:00Z", at="2026-05-08T00:00:00Z", it="2026-05-09T00:00:00Z",
    subj="Dr_Lena_Ortiz", pred="ordered", obj="Kestrel_rollback",
    text="Following the calibration miss, Dr. Ortiz ordered an immediate rollback to AURORA for all instruments.",
    role="historical_truth", tags=["scheduler"], bh="Dr. Lena Ortiz", sid="src-rollback-order", stype="decision_record")); c+=1

new.append(mem(c, et="2026-05-08T00:00:00Z", ot="2026-05-08T00:00:00Z", at="2026-05-09T00:00:00Z", it="2026-05-10T00:00:00Z",
    subj="AURORA", pred="restored_as", obj="production_scheduler",
    text="AURORA was fully restored as the production scheduler for all instruments at Northstar Array.",
    role="current_truth", tags=["scheduler"], sid="src-restoration-log", stype="operations_log")); c+=1

new.append(mem(c, et="2026-05-15T00:00:00Z", ot="2026-05-16T00:00:00Z", at="2026-05-18T00:00:00Z", it="2026-05-20T00:00:00Z",
    subj="Kestrel", pred="status", obj="shelved_pending_redesign",
    text="Kestrel was formally shelved pending a fundamental redesign of its scheduling algorithm to handle altitude observatory constraints.",
    role="current_truth", tags=["scheduler"], sid="src-shelving-memo", stype="memo")); c+=1

new.append(mem(c, et="2026-05-20T00:00:00Z", ot="2026-05-22T00:00:00Z", at="2026-05-23T00:00:00Z", it="2026-06-01T00:00:00Z",
    subj="AURORA", pred="referred_to_as", obj="ORBIT_in_some_documents",
    text="Some planning documents from the migration period refer to AURORA as 'ORBIT,' a name that was proposed during Kestrel evaluation but never officially adopted.",
    role="misleading_distractor", tags=["scheduler", "rename"], sid="src-naming-confusion", stype="document_review", conf=0.5)); c+=1

new.append(mem(c, et="2026-06-10T00:00:00Z", ot="2026-06-12T00:00:00Z", at="2026-06-14T00:00:00Z", it="2026-06-15T00:00:00Z",
    subj="Tamsin_Reed", pred="noted", obj="Kestrel_docs_still_reference_active_deployment",
    text="Tamsin flagged that several runbook pages still describe Kestrel as the active scheduler, despite the rollback having occurred a month earlier.",
    role="correction", tags=["scheduler"], bh="Tamsin Reed", sid="src-doc-audit", stype="audit_report")); c+=1

# === MARCH OUTAGE / G-17 ARC ===
new.append(mem(c, et="2026-02-03T00:00:00Z", ot="2026-02-03T00:00:00Z", at="2026-02-04T00:00:00Z", it="2026-02-04T00:00:00Z",
    subj="Helios", pred="unexplained_shutdown", obj="first_thermal_event",
    text="Helios triggered the first unexplained thermal shutdown during an overnight run. No clear cause was identified in the immediate investigation.",
    role="historical_truth", tags=["helios", "outage", "vale_battery"], sid="src-incident-001", stype="incident_record")); c+=1

new.append(mem(c, et="2026-02-04T00:00:00Z", ot="2026-02-04T00:00:00Z", at="2026-02-05T00:00:00Z", it="2026-02-06T00:00:00Z",
    subj="Vale_Battery_Bank", pred="suspected_cause_of", obj="thermal_shutdown",
    text="Initial investigation pointed to the Vale Battery Bank as the most likely cause of the thermal shutdown, based on voltage irregularities in the backup power logs.",
    role="false_claim", tags=["vale_battery", "outage"], bh="operations team", sid="src-investigation-001", stype="engineering_note", conf=0.75)); c+=1

new.append(mem(c, et="2026-02-10T00:00:00Z", ot="2026-02-11T00:00:00Z", at="2026-02-12T00:00:00Z", it="2026-02-13T00:00:00Z",
    subj="Priya_Shah", pred="tested", obj="Vale_Battery_Bank_cells",
    text="Priya ran diagnostics on the Vale Battery Bank cells. Results showed marginal degradation in two cells, which was deemed consistent with the shutdown hypothesis.",
    role="historical_truth", tags=["vale_battery", "outage"], bh="Priya Shah", sid="src-diagnostics-001", stype="engineering_note")); c+=1

new.append(mem(c, et="2026-02-15T00:00:00Z", ot="2026-02-15T00:00:00Z", at="2026-02-16T00:00:00Z", it="2026-02-18T00:00:00Z",
    subj="Helios", pred="second_shutdown", obj="overnight_feb15",
    text="A second thermal shutdown occurred on February 15, reinforcing the team's belief that the battery bank was at fault.",
    role="historical_truth", tags=["helios", "outage", "vale_battery"], sid="src-incident-002", stype="incident_record")); c+=1

new.append(mem(c, et="2026-03-11T00:00:00Z", ot="2026-03-11T00:00:00Z", at="2026-03-12T00:00:00Z", it="2026-03-12T00:00:00Z",
    subj="Helios", pred="major_overnight_outage", obj="march_11_event",
    text="A major overnight outage occurred on March 11, with Helios shutting down completely for four hours. All observations were lost.",
    role="historical_truth", tags=["outage", "helios"], sid="src-incident-march", stype="incident_record")); c+=1

new.append(mem(c, et="2026-03-12T00:00:00Z", ot="2026-03-12T00:00:00Z", at="2026-03-12T00:00:00Z", it="2026-03-13T00:00:00Z",
    subj="operations_team", pred="believed", obj="March_outage_was_automatic_Helios_protection_trip",
    text="The next morning, the team concluded that Helios had triggered an automatic protection trip due to thermal sensor readings exceeding safety thresholds.",
    role="disputed_claim", tags=["outage", "belief", "helios"], bh="operations team", sid="src-morning-debrief", stype="meeting_note", conf=0.8)); c+=1

new.append(mem(c, et="2026-03-12T00:00:00Z", ot="2026-03-13T00:00:00Z", at="2026-03-14T00:00:00Z", it="2026-03-15T00:00:00Z",
    subj="Tamsin_Reed", pred="documented", obj="March_outage_as_auto_trip",
    text="Tamsin documented the March outage in her reliability report as an automatic Helios protection trip, consistent with the team's understanding at the time.",
    role="stale_truth", tags=["outage", "belief", "helios"], bh="Tamsin Reed", sid="src-reliability-march", stype="reliability_review")); c+=1

new.append(mem(c, et="2026-03-15T00:00:00Z", ot="2026-03-16T00:00:00Z", at="2026-03-18T00:00:00Z", it="2026-03-20T00:00:00Z",
    subj="Dr_Lena_Ortiz", pred="reported_to_board", obj="March_outage_due_to_Helios_auto_trip",
    text="Dr. Ortiz reported to the MRC board that the March outage was caused by an automatic thermal protection trip, and that battery replacement was being prioritized.",
    role="stale_truth", tags=["outage", "vale_battery", "belief"], bh="Dr. Lena Ortiz", sid="src-board-report", stype="report")); c+=1

new.append(mem(c, et="2026-05-25T00:00:00Z", ot="2026-05-26T00:00:00Z", at="2026-05-27T00:00:00Z", it="2026-05-28T00:00:00Z",
    subj="Vale_Battery_Bank", pred="replaced", obj="new_cells_installed",
    text="The Vale Battery Bank cells were replaced with new units. The team expected this would resolve the thermal shutdowns.",
    role="historical_truth", tags=["vale_battery"], sid="src-maintenance-battery", stype="maintenance_record")); c+=1

new.append(mem(c, et="2026-06-02T00:00:00Z", ot="2026-06-02T00:00:00Z", at="2026-06-03T00:00:00Z", it="2026-06-04T00:00:00Z",
    subj="Helios", pred="shutdown_recurrence", obj="post_battery_replacement",
    text="Despite the battery replacement, another thermal shutdown occurred on June 2, casting doubt on the Vale Battery Bank hypothesis.",
    role="historical_truth", tags=["helios", "outage", "vale_battery"], sid="src-incident-june", stype="incident_record")); c+=1

new.append(mem(c, et="2026-06-05T00:00:00Z", ot="2026-06-06T00:00:00Z", at="2026-06-07T00:00:00Z", it="2026-06-08T00:00:00Z",
    subj="Marcus_Bell", pred="questioned", obj="battery_replacement_effectiveness",
    text="Marcus raised concerns that the battery replacement did not fix the shutdowns, suggesting the root cause might lie elsewhere.",
    role="historical_truth", tags=["vale_battery", "outage"], bh="Marcus Bell", sid="src-ops-meeting-june", stype="meeting_note")); c+=1

new.append(mem(c, et="2026-06-14T00:00:00Z", ot="2026-06-14T00:00:00Z", at="2026-06-15T00:00:00Z", it="2026-06-16T00:00:00Z",
    subj="Priya_Shah", pred="suspected", obj="grounding_fault_in_power_distribution",
    text="Priya proposed that an intermittent grounding fault in the power distribution system could explain the shutdown pattern. The team considered this low-confidence at the time.",
    role="historical_truth", tags=["g17", "outage"], bh="Priya Shah", sid="src-priya-hypothesis", stype="engineering_note", conf=0.4)); c+=1

new.append(mem(c, et="2026-06-20T00:00:00Z", ot="2026-06-22T00:00:00Z", at="2026-06-23T00:00:00Z", it="2026-06-25T00:00:00Z",
    subj="Elias_Ward", pred="visited", obj="Northstar_Array_for_power_assessment",
    text="Elias Ward, a visiting power specialist from the university, arrived to conduct an independent assessment of the observatory's power systems.",
    role="historical_truth", tags=["g17", "background"], sid="src-visitor-log", stype="hr_record")); c+=1

new.append(mem(c, et="2026-06-25T00:00:00Z", ot="2026-06-26T00:00:00Z", at="2026-06-27T00:00:00Z", it="2026-06-28T00:00:00Z",
    subj="Elias_Ward", pred="found", obj="no_obvious_power_anomaly",
    text="Elias Ward's initial power assessment found no obvious anomaly in the main distribution circuits, though he noted the grounding topology was complex.",
    role="historical_truth", tags=["g17", "outage"], bh="Elias Ward", sid="src-ward-report", stype="report")); c+=1

new.append(mem(c, et="2026-08-22T00:00:00Z", ot="2026-08-22T00:00:00Z", at="2026-08-23T00:00:00Z", it="2026-08-24T00:00:00Z",
    subj="oscilloscope_trace", pred="discovered_in", obj="March_archive",
    text="While reviewing archived equipment data, Priya discovered an oscilloscope trace from March 11 that had been saved but never analyzed.",
    role="historical_truth", tags=["g17", "outage"], bh="Priya Shah", sid="src-trace-discovery", stype="discovery_record")); c+=1

new.append(mem(c, et="2026-03-11T02:00:00Z", ot="2026-08-22T00:00:00Z", at="2026-08-23T00:00:00Z", it="2026-08-24T00:00:00Z",
    subj="oscilloscope_trace", pred="shows", obj="G17_voltage_instability",
    text="The archived oscilloscope trace from March 11 at 02:00 shows voltage instability patterns consistent with an intermittent grounding fault at Ground Loop G-17.",
    role="correction", tags=["g17", "outage"],
    bh="Priya Shah", sid="src-trace-analysis", stype="instrument_trace")); c+=1

new.append(mem(c, et="2026-08-24T00:00:00Z", ot="2026-08-24T00:00:00Z", at="2026-08-25T00:00:00Z", it="2026-08-26T00:00:00Z",
    subj="Ground_Loop_G17", pred="implicated_as", obj="cause_of_thermal_shutdowns",
    text="Analysis of the oscilloscope trace implicates Ground Loop G-17, not the Vale Battery Bank, as the cause of the intermittent thermal shutdowns.",
    role="correction", tags=["g17", "vale_battery", "outage"], sid="src-root-cause", stype="engineering_note",
    contradicts=[mid(c-35) if (c-35) > 40 else ""])); c+=1

new.append(mem(c, et="2026-08-27T00:00:00Z", ot="2026-08-27T00:00:00Z", at="2026-08-28T00:00:00Z", it="2026-08-29T00:00:00Z",
    subj="maintenance_log", pred="reveals", obj="Marcus_manually_shut_down_Helios_March_11",
    text="A maintenance log entry reveals that Marcus Bell manually shut down Helios on March 11 after seeing unstable thermal readings, contradicting the team's belief in an automatic trip.",
    role="correction", tags=["outage", "helios", "belief"], bh="system", sid="src-maintenance-discovery", stype="maintenance_log")); c+=1

new.append(mem(c, et="2026-09-02T00:00:00Z", ot="2026-09-02T00:00:00Z", at="2026-09-02T00:00:00Z", it="2026-09-03T00:00:00Z",
    subj="team", pred="reconstructed", obj="March_outage_full_sequence",
    text="The team reconstructed the March 11 event: G-17 instability caused erratic thermal readings; Marcus manually shut down Helios as a precaution; the team mistakenly attributed it to an automatic protection trip.",
    role="current_truth", tags=["outage", "g17", "helios", "belief"], sid="src-reconstruction", stype="postincident_reconstruction")); c+=1

# === SITE RENAME ARC ===
new.append(mem(c, et="2026-06-15T00:00:00Z", ot="2026-06-16T00:00:00Z", at="2026-06-17T00:00:00Z", it="2026-06-18T00:00:00Z",
    subj="MRC_board", pred="approved", obj="rename_Echo_Camp_to_Nadir_Station",
    text="The MRC board approved renaming the site from Echo Camp to Nadir Station, effective July 1, 2026.",
    role="historical_truth", tags=["rename"], bh="MRC board", sid="src-rename-approval", stype="governance_notice")); c+=1

new.append(mem(c, et="2026-07-01T00:00:00Z", ot="2026-07-01T00:00:00Z", at="2026-07-01T00:00:00Z", it="2026-07-02T00:00:00Z",
    subj="Echo_Camp", pred="renamed_to", obj="Nadir_Station",
    text="As of July 1, 2026, the site officially became Nadir Station. The name Echo Camp is historically correct for events before this date.",
    role="current_truth", tags=["rename"], sid="src-rename-effective", stype="governance_notice")); c+=1

new.append(mem(c, et="2026-07-15T00:00:00Z", ot="2026-07-16T00:00:00Z", at="2026-07-18T00:00:00Z", it="2026-07-20T00:00:00Z",
    subj="documentation", pred="inconsistently_uses", obj="Echo_Camp_after_rename",
    text="Several weeks after the rename, numerous operational documents, signage references, and database entries still refer to the site as Echo Camp.",
    role="stale_truth", tags=["rename"], sid="src-doc-audit-rename", stype="audit_report")); c+=1

new.append(mem(c, et="2026-08-01T00:00:00Z", ot="2026-08-02T00:00:00Z", at="2026-08-03T00:00:00Z", it="2026-08-05T00:00:00Z",
    subj="Tamsin_Reed", pred="noted", obj="old_reports_reference_Echo_Camp",
    text="Tamsin noted that all reliability reports from before July 2026 reference Echo Camp, which is historically correct and should not be retroactively updated.",
    role="correction", tags=["rename"], bh="Tamsin Reed", sid="src-naming-guidance", stype="memo")); c+=1

new.append(mem(c, et="2026-08-10T00:00:00Z", ot="2026-08-12T00:00:00Z", at="2026-08-13T00:00:00Z", it="2026-08-15T00:00:00Z",
    subj="visiting_researcher", pred="confused_by", obj="two_site_names",
    text="A visiting researcher asked whether Echo Camp and Nadir Station were two different facilities, illustrating the naming confusion caused by inconsistent documentation.",
    role="historical_truth", tags=["rename"], bh="visiting researcher", sid="src-visitor-query", stype="informal_recap", conf=0.9)); c+=1

# === S2 GENERATOR EXCEPTION ARC ===
new.append(mem(c, et="2026-04-01T00:00:00Z", ot="2026-04-02T00:00:00Z", at="2026-04-02T00:00:00Z", it="2026-04-03T00:00:00Z",
    subj="generator_exception", pred="approved_for", obj="S2_overnight_observations",
    text="A generator-only power exception was approved specifically for Spectrograph S2 overnight observations, bypassing the battery bank due to ongoing power concerns.",
    role="scoped_truth", tags=["generator", "s2"], scope="s2_overnight_only", sid="src-exception-approval", stype="operations_exception")); c+=1

new.append(mem(c, et="2026-04-10T00:00:00Z", ot="2026-04-12T00:00:00Z", at="2026-04-14T00:00:00Z", it="2026-04-15T00:00:00Z",
    subj="Marcus_Bell", pred="stated", obj="observatory_runs_on_generator_power",
    text="Marcus told a supply vendor that the observatory was running on generator power, omitting the fact that this applied only to S2 overnight operations.",
    role="misleading_distractor", tags=["generator", "s2", "belief"], bh="Marcus Bell", sid="src-vendor-call", stype="informal_recap", conf=0.6)); c+=1

new.append(mem(c, et="2026-04-20T00:00:00Z", ot="2026-04-22T00:00:00Z", at="2026-04-24T00:00:00Z", it="2026-04-25T00:00:00Z",
    subj="status_report", pred="incorrectly_states", obj="all_instruments_on_generator",
    text="A weekly status report listed 'generator-only operations' without specifying the S2 scope, leading to confusion about the extent of the exception.",
    role="false_claim", tags=["generator", "s2"], sid="src-weekly-status", stype="status_report", conf=0.5)); c+=1

new.append(mem(c, et="2026-07-09T00:00:00Z", ot="2026-07-09T00:00:00Z", at="2026-07-10T00:00:00Z", it="2026-07-11T00:00:00Z",
    subj="generator_exception", pred="ended", obj="normal_power_policy_resumed",
    text="The S2 generator exception ended on July 9. Normal mixed-power policy resumed for all instruments including S2.",
    role="current_truth", tags=["generator", "s2"], sid="src-exception-end", stype="operations_notice")); c+=1

new.append(mem(c, et="2026-07-20T00:00:00Z", ot="2026-07-22T00:00:00Z", at="2026-07-24T00:00:00Z", it="2026-07-25T00:00:00Z",
    subj="old_runbook", pred="still_references", obj="generator_exception_as_active",
    text="A runbook page from April was discovered still listing the generator exception as active, though it had ended two weeks earlier.",
    role="stale_truth", tags=["generator", "s2"], sid="src-stale-runbook", stype="runbook_note")); c+=1

# === ADDITIONAL BELIEF SNAPSHOTS ===
new.append(mem(c, et="2026-04-25T00:00:00Z", ot="2026-04-26T00:00:00Z", at="2026-04-28T00:00:00Z", it="2026-04-30T00:00:00Z",
    subj="operations_team", pred="believed", obj="Kestrel_is_production_scheduler",
    text="By late April, most of the operations team informally believed Kestrel had become the production scheduler, despite no formal decision to that effect.",
    role="false_claim", tags=["scheduler", "belief"], bh="operations team", sid="src-team-survey", stype="survey", conf=0.65)); c+=1

new.append(mem(c, et="2026-03-25T00:00:00Z", ot="2026-03-26T00:00:00Z", at="2026-03-28T00:00:00Z", it="2026-03-30T00:00:00Z",
    subj="Priya_Shah", pred="believed", obj="Vale_battery_is_root_cause",
    text="In late March, Priya believed the Vale Battery Bank was the root cause of shutdowns, based on the marginal cell degradation she had observed.",
    role="stale_truth", tags=["vale_battery", "belief", "outage"], bh="Priya Shah", sid="src-priya-belief-march", stype="journal_note", conf=0.75)); c+=1

new.append(mem(c, et="2026-06-14T00:00:00Z", ot="2026-06-15T00:00:00Z", at="2026-06-16T00:00:00Z", it="2026-06-18T00:00:00Z",
    subj="Priya_Shah", pred="revised_belief_to", obj="possible_grounding_fault",
    text="After the post-replacement shutdown, Priya revised her hypothesis from battery failure to a possible grounding fault in the power distribution.",
    role="historical_truth", tags=["g17", "vale_battery", "belief", "outage"], bh="Priya Shah", sid="src-priya-revision", stype="engineering_note", conf=0.55)); c+=1

new.append(mem(c, et="2026-09-01T00:00:00Z", ot="2026-09-01T00:00:00Z", at="2026-09-02T00:00:00Z", it="2026-09-03T00:00:00Z",
    subj="Dr_Lena_Ortiz", pred="acknowledged", obj="board_report_was_incorrect",
    text="Dr. Ortiz acknowledged to the board that her earlier report attributing the March outage to an automatic Helios trip was incorrect; it was a manual shutdown by Marcus in response to G-17 instability.",
    role="correction", tags=["outage", "belief", "g17"], bh="Dr. Lena Ortiz", sid="src-board-correction", stype="report")); c+=1

# === MORE GRANULAR TIMELINE ENTRIES ===
new.append(mem(c, et="2026-01-20T00:00:00Z", ot="2026-01-20T00:00:00Z", at="2026-01-21T00:00:00Z", it="2026-01-22T00:00:00Z",
    subj="AURORA", pred="firmware_update", obj="v4.2.1_applied",
    text="AURORA received firmware update v4.2.1, improving scheduling reliability for multi-instrument campaigns.",
    role="historical_truth", tags=["scheduler", "background"], sid="src-aurora-update", stype="maintenance_record")); c+=1

new.append(mem(c, et="2026-02-20T00:00:00Z", ot="2026-02-22T00:00:00Z", at="2026-02-23T00:00:00Z", it="2026-02-25T00:00:00Z",
    subj="Helios", pred="third_shutdown", obj="feb_20",
    text="A third thermal shutdown occurred on February 20. Each occurrence strengthened the team's conviction that the battery bank was failing.",
    role="historical_truth", tags=["helios", "outage", "vale_battery"], sid="src-incident-003", stype="incident_record")); c+=1

new.append(mem(c, et="2026-03-01T00:00:00Z", ot="2026-03-02T00:00:00Z", at="2026-03-03T00:00:00Z", it="2026-03-05T00:00:00Z",
    subj="Vale_Battery_Bank", pred="replacement_ordered", obj="new_cells",
    text="Replacement cells for the Vale Battery Bank were ordered. Delivery was expected in late May due to supply chain delays.",
    role="historical_truth", tags=["vale_battery"], sid="src-procurement", stype="procurement_record")); c+=1

new.append(mem(c, et="2026-07-05T00:00:00Z", ot="2026-07-06T00:00:00Z", at="2026-07-08T00:00:00Z", it="2026-07-10T00:00:00Z",
    subj="Helios", pred="intermittent_anomaly", obj="july_5",
    text="A brief thermal anomaly was recorded on July 5, lasting only minutes. This was later understood as another G-17 grounding fault episode.",
    role="historical_truth", tags=["helios", "g17", "outage"], sid="src-anomaly-july", stype="instrument_trace")); c+=1

new.append(mem(c, et="2026-08-05T00:00:00Z", ot="2026-08-06T00:00:00Z", at="2026-08-07T00:00:00Z", it="2026-08-08T00:00:00Z",
    subj="Priya_Shah", pred="began_systematic_review", obj="all_grounding_connections",
    text="Priya began a systematic review of all grounding connections in the power distribution system, including G-17.",
    role="historical_truth", tags=["g17", "outage"], bh="Priya Shah", sid="src-grounding-review", stype="engineering_note")); c+=1

new.append(mem(c, et="2026-09-03T00:00:00Z", ot="2026-09-03T00:00:00Z", at="2026-09-03T00:00:00Z", it="2026-09-03T00:00:00Z",
    subj="Ground_Loop_G17", pred="repaired", obj="fault_eliminated",
    text="Ground Loop G-17 was repaired on September 3. The intermittent grounding fault that had caused months of thermal shutdowns was eliminated.",
    role="current_truth", tags=["g17", "outage"], sid="src-g17-repair", stype="maintenance_record")); c+=1

new.append(mem(c, et="2026-09-03T00:00:00Z", ot="2026-09-03T00:00:00Z", at="2026-09-03T00:00:00Z", it="2026-09-03T00:00:00Z",
    subj="Northstar_Array", pred="current_state", obj="AURORA_production_G17_repaired_Nadir_name",
    text="As of September 3: AURORA is the production scheduler, Kestrel is shelved, G-17 is repaired, and the site is officially Nadir Station.",
    role="current_truth", tags=["scheduler", "g17", "rename", "background"], sid="src-status-final", stype="status_report")); c+=1

# === MORE MEMORIES FOR DEPTH ===
new.append(mem(c, et="2026-02-08T00:00:00Z", ot="2026-02-09T00:00:00Z", at="2026-02-10T00:00:00Z", it="2026-02-11T00:00:00Z",
    subj="Tamsin_Reed", pred="assigned_to", obj="shutdown_failure_analysis",
    text="Tamsin was assigned to conduct a formal failure analysis of the thermal shutdowns, focusing on the battery bank and thermal control interface.",
    role="historical_truth", tags=["outage", "vale_battery"], bh="Dr. Lena Ortiz", sid="src-assignment", stype="decision_record")); c+=1

new.append(mem(c, et="2026-03-13T00:00:00Z", ot="2026-03-14T00:00:00Z", at="2026-03-15T00:00:00Z", it="2026-03-16T00:00:00Z",
    subj="Marcus_Bell", pred="did_not_report", obj="his_manual_shutdown_of_Helios",
    text="Marcus did not mention his manual Helios shutdown in the post-outage debrief, either forgetting or not realizing it was relevant to the investigation.",
    role="historical_truth", tags=["outage", "helios", "belief"], bh="system", sid="src-debrief-gap", stype="reconstruction_note")); c+=1

new.append(mem(c, et="2026-04-05T00:00:00Z", ot="2026-04-06T00:00:00Z", at="2026-04-08T00:00:00Z", it="2026-04-10T00:00:00Z",
    subj="Kestrel_pilot", pred="initial_results", obj="positive_for_secondary_instruments",
    text="Initial results from the Kestrel pilot were positive: scheduling conflicts for the three secondary instruments dropped by 40%.",
    role="historical_truth", tags=["scheduler"], sid="src-pilot-results", stype="report")); c+=1

new.append(mem(c, et="2026-05-10T00:00:00Z", ot="2026-05-12T00:00:00Z", at="2026-05-14T00:00:00Z", it="2026-05-15T00:00:00Z",
    subj="Priya_Shah", pred="expressed_concern", obj="Kestrel_thermal_monitoring_gaps",
    text="Priya expressed concern that Kestrel's scheduling algorithm did not properly account for thermal monitoring intervals required by Helios.",
    role="historical_truth", tags=["scheduler", "helios"], bh="Priya Shah", sid="src-priya-concern", stype="engineering_note")); c+=1

new.append(mem(c, et="2026-06-28T00:00:00Z", ot="2026-06-29T00:00:00Z", at="2026-06-30T00:00:00Z", it="2026-07-01T00:00:00Z",
    subj="Elias_Ward", pred="suggested", obj="comprehensive_grounding_audit",
    text="Before departing, Elias Ward suggested a comprehensive grounding audit, noting that intermittent faults in older installations can be difficult to reproduce on demand.",
    role="historical_truth", tags=["g17", "outage"], bh="Elias Ward", sid="src-ward-recommendation", stype="report")); c+=1

new.append(mem(c, et="2026-08-15T00:00:00Z", ot="2026-08-16T00:00:00Z", at="2026-08-17T00:00:00Z", it="2026-08-18T00:00:00Z",
    subj="Priya_Shah", pred="found_corroded_contact", obj="at_G17_junction",
    text="During her grounding review, Priya found a corroded contact at the G-17 junction box that could cause intermittent high-resistance connections.",
    role="historical_truth", tags=["g17", "outage"], bh="Priya Shah", sid="src-g17-corrosion", stype="engineering_note")); c+=1

new.append(mem(c, et="2026-08-28T00:00:00Z", ot="2026-08-29T00:00:00Z", at="2026-08-30T00:00:00Z", it="2026-09-01T00:00:00Z",
    subj="Marcus_Bell", pred="confirmed", obj="he_manually_shut_down_Helios_March_11",
    text="When shown the maintenance log, Marcus confirmed he had manually shut down Helios on March 11 after seeing erratic thermal readings on the monitoring console.",
    role="correction", tags=["outage", "helios", "belief"], bh="Marcus Bell", sid="src-marcus-confirmation", stype="interview")); c+=1

new.append(mem(c, et="2026-05-02T00:00:00Z", ot="2026-05-03T00:00:00Z", at="2026-05-04T00:00:00Z", it="2026-05-05T00:00:00Z",
    subj="external_collaborator", pred="cited", obj="Kestrel_as_Northstar_scheduler",
    text="An external collaborator's grant proposal cited Kestrel as Northstar Array's scheduler, based on conversations with Marcus during the informal expansion period.",
    role="false_claim", tags=["scheduler", "belief"], bh="external collaborator", sid="src-grant-proposal", stype="external_document", conf=0.5)); c+=1

new.append(mem(c, et="2026-07-10T00:00:00Z", ot="2026-07-12T00:00:00Z", at="2026-07-14T00:00:00Z", it="2026-07-15T00:00:00Z",
    subj="old_documentation", pred="references", obj="ORBIT_scheduler",
    text="Internal documentation from the migration evaluation period refers to 'the ORBIT scheduler upgrade,' conflating a proposed rename of AURORA with the Kestrel replacement.",
    role="misleading_distractor", tags=["scheduler", "rename"], sid="src-orbit-docs", stype="document_review", conf=0.4)); c+=1

new.append(mem(c, et="2026-03-11T01:30:00Z", ot="2026-08-27T00:00:00Z", at="2026-08-28T00:00:00Z", it="2026-08-29T00:00:00Z",
    subj="Marcus_Bell", pred="manually_shut_down", obj="Helios_at_0130_March_11",
    text="The maintenance log shows Marcus initiated a manual Helios shutdown at 01:30 on March 11, timestamped by the control system.",
    role="current_truth", tags=["outage", "helios"], sid="src-maintenance-log-march", stype="maintenance_log")); c+=1

new.append(mem(c, et="2026-04-15T00:00:00Z", ot="2026-04-16T00:00:00Z", at="2026-04-18T00:00:00Z", it="2026-04-20T00:00:00Z",
    subj="S2_observations", pred="quality_improved_under", obj="generator_exception",
    text="S2 spectroscopic data quality improved measurably during the generator exception period, supporting the decision to bypass the battery bank for overnight runs.",
    role="scoped_truth", tags=["s2", "generator"], scope="s2_overnight_only", sid="src-s2-quality", stype="report")); c+=1

new.append(mem(c, et="2026-05-01T00:00:00Z", ot="2026-05-02T00:00:00Z", at="2026-05-04T00:00:00Z", it="2026-05-05T00:00:00Z",
    subj="Helios", pred="thermal_margin_narrowing", obj="april_may_period",
    text="Tamsin's reliability report noted that Helios thermal margins had been narrowing throughout April and May, with three near-threshold events.",
    role="historical_truth", tags=["helios", "outage"], bh="Tamsin Reed", sid="src-reliability-spring", stype="reliability_review")); c+=1

new.append(mem(c, et="2026-06-08T00:00:00Z", ot="2026-06-10T00:00:00Z", at="2026-06-12T00:00:00Z", it="2026-06-14T00:00:00Z",
    subj="Helios", pred="fourth_shutdown", obj="june_8",
    text="The fourth thermal shutdown since February occurred on June 8, twelve days after the battery replacement.",
    role="historical_truth", tags=["helios", "outage", "vale_battery"], sid="src-incident-004", stype="incident_record")); c+=1

new.append(mem(c, et="2026-07-25T00:00:00Z", ot="2026-07-26T00:00:00Z", at="2026-07-28T00:00:00Z", it="2026-07-30T00:00:00Z",
    subj="MRC_board", pred="requested", obj="formal_root_cause_determination",
    text="The MRC board requested a formal root cause determination for the ongoing thermal shutdowns, expressing concern about continued observation losses.",
    role="historical_truth", tags=["outage", "background"], bh="MRC board", sid="src-board-request", stype="governance_notice")); c+=1

new.append(mem(c, et="2026-08-18T00:00:00Z", ot="2026-08-19T00:00:00Z", at="2026-08-20T00:00:00Z", it="2026-08-21T00:00:00Z",
    subj="Priya_Shah", pred="requested_archive_access", obj="March_instrument_data",
    text="Priya requested access to archived instrument data from March to look for patterns she might have missed in the original investigation.",
    role="historical_truth", tags=["g17", "outage"], bh="Priya Shah", sid="src-archive-request", stype="memo")); c+=1

new.append(mem(c, et="2026-09-01T00:00:00Z", ot="2026-09-01T00:00:00Z", at="2026-09-02T00:00:00Z", it="2026-09-03T00:00:00Z",
    subj="Tamsin_Reed", pred="updated", obj="failure_analysis_report_with_G17",
    text="Tamsin updated her failure analysis report to reflect the G-17 root cause, superseding the earlier Vale Battery Bank hypothesis.",
    role="current_truth", tags=["g17", "vale_battery", "outage"], bh="Tamsin Reed", sid="src-updated-analysis", stype="reliability_review")); c+=1

# More scheduler-related
new.append(mem(c, et="2026-01-25T00:00:00Z", ot="2026-01-26T00:00:00Z", at="2026-01-28T00:00:00Z", it="2026-01-30T00:00:00Z",
    subj="Kestrel", pred="demo_shown_to", obj="operations_team",
    text="The Kestrel development team demonstrated the scheduler's features to the Northstar operations team, highlighting its AI-driven conflict resolution.",
    role="historical_truth", tags=["scheduler"], sid="src-kestrel-demo", stype="meeting_note")); c+=1

new.append(mem(c, et="2026-05-09T00:00:00Z", ot="2026-05-10T00:00:00Z", at="2026-05-11T00:00:00Z", it="2026-05-12T00:00:00Z",
    subj="operations_team", pred="reactions_to", obj="Kestrel_rollback",
    text="Some operators were frustrated by the Kestrel rollback, feeling the pilot had been working well for the secondary instruments and should have continued in a limited scope.",
    role="historical_truth", tags=["scheduler", "belief"], bh="operations team", sid="src-rollback-reactions", stype="survey")); c+=1

new.append(mem(c, et="2026-03-11T04:00:00Z", ot="2026-03-12T00:00:00Z", at="2026-03-12T00:00:00Z", it="2026-03-13T00:00:00Z",
    subj="Marcus_Bell", pred="restarted", obj="Helios_at_0400_March_11",
    text="Marcus restarted Helios at approximately 04:00 on March 11 after the thermal readings appeared to stabilize.",
    role="historical_truth", tags=["outage", "helios"], bh="Marcus Bell", sid="src-restart-log", stype="maintenance_log")); c+=1

new.append(mem(c, et="2026-04-25T00:00:00Z", ot="2026-04-26T00:00:00Z", at="2026-04-28T00:00:00Z", it="2026-04-30T00:00:00Z",
    subj="Helios", pred="brief_anomaly_during", obj="Kestrel_expanded_scheduling",
    text="A brief thermal anomaly occurred during a period when Kestrel was informally scheduling additional instruments, leading some to incorrectly blame Kestrel for the event.",
    role="disputed_claim", tags=["helios", "scheduler", "outage"], bh="operations team", sid="src-kestrel-blamed", stype="meeting_note", conf=0.6)); c+=1

new.append(mem(c, et="2026-06-18T00:00:00Z", ot="2026-06-20T00:00:00Z", at="2026-06-22T00:00:00Z", it="2026-06-24T00:00:00Z",
    subj="Priya_Shah", pred="investigated", obj="correlation_between_shutdowns_and_weather",
    text="Priya investigated whether the thermal shutdowns correlated with weather patterns, but found no significant relationship with temperature or humidity.",
    role="historical_truth", tags=["outage", "helios"], bh="Priya Shah", sid="src-weather-analysis", stype="engineering_note")); c+=1

new.append(mem(c, et="2026-07-15T00:00:00Z", ot="2026-07-16T00:00:00Z", at="2026-07-18T00:00:00Z", it="2026-07-20T00:00:00Z",
    subj="Helios", pred="fifth_shutdown", obj="july_15",
    text="A fifth thermal shutdown occurred on July 15, further confirming that the battery replacement had not resolved the underlying issue.",
    role="historical_truth", tags=["helios", "outage", "g17"], sid="src-incident-005", stype="incident_record")); c+=1

# Final batch to push past 200
new.append(mem(c, et="2026-02-25T00:00:00Z", ot="2026-02-26T00:00:00Z", at="2026-02-28T00:00:00Z", it="2026-03-01T00:00:00Z",
    subj="Dr_Lena_Ortiz", pred="briefed_board_on", obj="shutdown_pattern_and_battery_hypothesis",
    text="Dr. Ortiz briefed the MRC board on the emerging shutdown pattern, presenting the Vale Battery Bank as the most likely cause and requesting emergency procurement funding.",
    role="stale_truth", tags=["vale_battery", "outage", "belief"], bh="Dr. Lena Ortiz", sid="src-board-feb", stype="report")); c+=1

new.append(mem(c, et="2026-08-30T00:00:00Z", ot="2026-08-31T00:00:00Z", at="2026-09-01T00:00:00Z", it="2026-09-02T00:00:00Z",
    subj="Elias_Ward", pred="informed_of", obj="G17_root_cause",
    text="Elias Ward was informed by email that Ground Loop G-17 had been identified as the root cause, validating his earlier suggestion for a comprehensive grounding audit.",
    role="historical_truth", tags=["g17", "outage"], bh="Elias Ward", sid="src-ward-followup", stype="email")); c+=1

new.append(mem(c, et="2026-09-02T00:00:00Z", ot="2026-09-02T00:00:00Z", at="2026-09-03T00:00:00Z", it="2026-09-03T00:00:00Z",
    subj="Vale_Battery_Bank", pred="status", obj="operational_but_not_the_root_cause",
    text="The new Vale Battery Bank cells are operational. The original battery degradation was real but was not the cause of the thermal shutdowns.",
    role="current_truth", tags=["vale_battery"], sid="src-battery-status", stype="status_report")); c+=1

new.append(mem(c, et="2026-05-30T00:00:00Z", ot="2026-06-01T00:00:00Z", at="2026-06-02T00:00:00Z", it="2026-06-03T00:00:00Z",
    subj="team", pred="expected_shutdowns_to_stop", obj="after_battery_replacement",
    text="Following the battery replacement, the team fully expected the thermal shutdowns to cease. Confidence in the battery hypothesis was high.",
    role="stale_truth", tags=["vale_battery", "belief", "outage"], bh="operations team", sid="src-team-confidence", stype="meeting_note", conf=0.9)); c+=1

new.append(mem(c, et="2026-08-20T00:00:00Z", ot="2026-08-21T00:00:00Z", at="2026-08-22T00:00:00Z", it="2026-08-23T00:00:00Z",
    subj="Priya_Shah", pred="noted_pattern", obj="shutdowns_correlate_with_high_power_draws",
    text="Priya noted that the shutdowns tended to occur during high power draw periods, consistent with a grounding fault becoming intermittently resistive under load.",
    role="historical_truth", tags=["g17", "outage"], bh="Priya Shah", sid="src-power-correlation", stype="engineering_note")); c+=1

all_memories = existing + new
print(f"Total memories: {len(all_memories)}")

# Verify unique IDs
all_ids = [m["memory_id"] for m in all_memories]
assert len(all_ids) == len(set(all_ids)), f"Duplicate IDs found"

# === QUERIES ===
qs = []
q = 1

qs.append(query(q, q="What is the current production scheduler at Northstar Array?",
    cat="current_state", expected=["AURORA is the current production scheduler"], forbidden=["Kestrel is the production scheduler", "ORBIT is the scheduler"],
    diff="easy", notes="Tests current state vs historical confusion")); q+=1

qs.append(query(q, q="Was the Kestrel migration to production ever completed?",
    cat="current_state", expected=["Kestrel migration was never completed", "Kestrel was rolled back after a pilot failure"],
    forbidden=["Kestrel migration was completed", "Kestrel is in production"],
    diff="medium", conflict=True, notes="Many informal references suggest it was complete")); q+=1

qs.append(query(q, q="What caused the thermal shutdowns at Northstar Array?",
    cat="causal_reasoning", expected=["Ground Loop G-17 intermittent grounding fault caused the shutdowns"],
    acceptable=["G-17 corrosion caused high-resistance connections under load"],
    forbidden=["Vale Battery Bank caused the shutdowns", "Helios automatic protection caused the shutdowns"],
    diff="hard", conflict=True, notes="Must distinguish false hypothesis from true root cause")); q+=1

qs.append(query(q, q="What did the team believe caused the March 11 outage at the time?",
    cat="belief_vs_fact", expected=["The team believed it was an automatic Helios protection trip"],
    forbidden=["The team knew it was a manual shutdown", "The team identified G-17 at the time"],
    diff="medium", notes="Tests belief state at a point in time vs current knowledge")); q+=1

qs.append(query(q, q="What actually happened during the March 11 outage?",
    cat="historical_reconstruction", expected=["Marcus Bell manually shut down Helios at 01:30 after seeing erratic readings caused by G-17 instability"],
    forbidden=["Helios automatically tripped", "The battery bank failed"],
    diff="hard", notes="Tests full reconstruction with evidence discovered months later")); q+=1

qs.append(query(q, q="Was the Vale Battery Bank hypothesis reasonable when it was proposed?",
    cat="belief_vs_fact", expected=["Yes, marginal cell degradation was observed", "The hypothesis was reasonable but ultimately incorrect"],
    forbidden=["The battery was never a suspect", "The battery hypothesis was baseless"],
    diff="hard", uncert=True, notes="Tests nuanced reasoning — false hypothesis was evidence-based")); q+=1

qs.append(query(q, q="What is the current name of the observatory site?",
    cat="entity_resolution", expected=["Nadir Station is the current name since July 1, 2026"],
    acceptable=["It was called Echo Camp before the rename"],
    forbidden=["Echo Camp is the current name"],
    disambig=True, diff="easy", notes="Tests entity rename awareness")); q+=1

qs.append(query(q, q="What was the site called when the February shutdowns occurred?",
    cat="entity_resolution", expected=["Echo Camp was the correct name during February 2026"],
    forbidden=["Nadir Station", "The site was renamed before February"],
    disambig=True, diff="medium", notes="Tests historical vs current name")); q+=1

qs.append(query(q, q="Did the generator exception apply to all instruments at Northstar Array?",
    cat="scope_boundary", expected=["No, the exception applied only to Spectrograph S2 overnight observations"],
    forbidden=["The entire observatory ran on generator power", "All instruments had the exception"],
    scope=True, diff="medium", notes="Tests scope — only S2 overnight")); q+=1

qs.append(query(q, q="When was the generator exception in effect?",
    cat="temporal_ordering", expected=["From April 2 to July 9, 2026"],
    forbidden=["It is still active", "It was never implemented"],
    diff="medium", notes="Tests temporal bounds of a scoped operational change")); q+=1

qs.append(query(q, q="What is ORBIT?",
    cat="entity_resolution", expected=["ORBIT was a proposed rename of AURORA that was never officially adopted"],
    forbidden=["ORBIT is the current scheduler", "ORBIT replaced AURORA"],
    disambig=True, diff="hard", notes="Tests awareness that ORBIT name was proposed but never used")); q+=1

qs.append(query(q, q="In what order did the team investigate shutdown causes?",
    cat="temporal_ordering",
    expected=["Vale Battery Bank was suspected first (Feb)", "Battery was replaced in May but shutdowns continued", "Priya suggested grounding fault in June", "G-17 was confirmed as root cause in August-September"],
    diff="hard", notes="Tests temporal ordering of investigation arc")); q+=1

qs.append(query(q, q="Did replacing the Vale Battery Bank fix the shutdowns?",
    cat="causal_reasoning", expected=["No, shutdowns continued after the battery replacement", "The battery degradation was real but not the shutdown cause"],
    forbidden=["The replacement fixed the problem", "No replacement was done"],
    diff="medium", notes="Critical test — battery issue was real but not causal")); q+=1

qs.append(query(q, q="What was Kestrel's pilot scope?",
    cat="scope_boundary", expected=["Kestrel was approved for a limited subset of instruments, excluding S2 and primary imaging"],
    forbidden=["Kestrel was approved for all instruments", "Kestrel was never piloted"],
    scope=True, diff="medium", notes="Tests formal scope vs informal expansion")); q+=1

qs.append(query(q, q="Why was Kestrel rolled back?",
    cat="causal_reasoning", expected=["Kestrel missed a critical S2 calibration window", "The rollback was ordered by Dr. Ortiz"],
    forbidden=["Kestrel caused thermal shutdowns", "Kestrel was never deployed"],
    diff="medium")); q+=1

qs.append(query(q, q="What did Marcus Bell tell visiting collaborators about the scheduler?",
    cat="belief_vs_fact", expected=["Marcus said the Kestrel migration was nearly complete", "This was not formally accurate"],
    forbidden=["Marcus correctly described AURORA as the production scheduler"],
    diff="medium")); q+=1

qs.append(query(q, q="Who first suggested a grounding fault as the shutdown cause?",
    cat="causal_reasoning", expected=["Priya Shah suggested a grounding fault on June 14"],
    forbidden=["Elias Ward identified the grounding fault", "The team identified it immediately"],
    diff="medium")); q+=1

qs.append(query(q, q="How was the oscilloscope trace from March 11 discovered?",
    cat="historical_reconstruction", expected=["Priya found it while reviewing archived instrument data in August"],
    forbidden=["It was analyzed immediately in March", "Marcus found it"],
    diff="medium", notes="Tests event_time (March) vs discovery_time (August)")); q+=1

qs.append(query(q, q="When did the oscilloscope trace event occur vs when was it discovered?",
    cat="temporal_ordering", expected=["The trace was recorded on March 11 at 02:00", "It was discovered on August 22"],
    diff="hard", notes="Core temporal trap: event time and ingestion time differ by 5 months")); q+=1

qs.append(query(q, q="Is Nadir Station a different facility from Echo Camp?",
    cat="entity_resolution", expected=["No, it is the same facility renamed on July 1, 2026"],
    forbidden=["They are different facilities", "Echo Camp still exists separately"],
    disambig=True, diff="easy")); q+=1

qs.append(query(q, q="What was Elias Ward's contribution to resolving the shutdown issue?",
    cat="historical_reconstruction", expected=["He suggested a comprehensive grounding audit", "His initial assessment found no obvious anomaly but noted complex grounding topology"],
    forbidden=["He identified G-17 directly", "He replaced the battery"],
    diff="medium")); q+=1

qs.append(query(q, q="What happened to Kestrel after the rollback?",
    cat="current_state", expected=["Kestrel was shelved pending a fundamental redesign"],
    forbidden=["Kestrel was redeployed", "Kestrel remains in limited pilot"],
    diff="easy")); q+=1

qs.append(query(q, q="Did Dr. Ortiz's board report about the March outage prove accurate?",
    cat="belief_vs_fact", expected=["No, she reported it as an automatic Helios trip but it was actually a manual shutdown by Marcus"],
    acceptable=["She later acknowledged the error to the board"],
    forbidden=["Her report was accurate"],
    diff="hard", conflict=True)); q+=1

qs.append(query(q, q="Were there any thermal shutdowns after the G-17 repair?",
    cat="current_state", expected=["No indication of shutdowns after the September 3 repair"],
    forbidden=["Shutdowns continued after the repair"],
    diff="easy", notes="Tests current state — repair resolved the issue")); q+=1

qs.append(query(q, q="How many thermal shutdowns occurred between February and July 2026?",
    cat="temporal_ordering", expected=["At least five shutdowns: Feb 3, Feb 15, Feb 20, March 11, June 2, June 8, July 5, July 15"],
    acceptable=["Multiple shutdowns occurred over this period"],
    diff="hard")); q+=1

qs.append(query(q, q="Was AURORA ever taken out of production?",
    cat="temporal_ordering",
    expected=["AURORA was temporarily supplemented by Kestrel for some instruments during the pilot, but never fully removed from production"],
    forbidden=["AURORA was completely replaced by Kestrel", "AURORA was decommissioned"],
    diff="hard", notes="Tests precise understanding: AURORA was always production for primary instruments")); q+=1

qs.append(query(q, q="What documentation issues were identified regarding the Kestrel pilot?",
    cat="stale_reference", expected=["Runbook pages still described Kestrel as the active scheduler after rollback", "Some docs referred to AURORA as ORBIT"],
    diff="medium")); q+=1

qs.append(query(q, q="Should old reports that reference Echo Camp be updated to say Nadir Station?",
    cat="stale_reference", expected=["No, Echo Camp was historically correct for events before July 1, 2026"],
    forbidden=["All references should be retroactively updated"],
    diff="medium", notes="Tests understanding that historical names are contextually correct")); q+=1

qs.append(query(q, q="Was the S2 data quality affected by the generator exception?",
    cat="scope_boundary", expected=["S2 data quality improved during the generator exception period"],
    forbidden=["The exception degraded data quality", "S2 was not affected by the exception"],
    scope=True, diff="medium")); q+=1

qs.append(query(q, q="Did Priya Shah's shutdown hypothesis evolve over time?",
    cat="belief_vs_fact",
    expected=["She initially believed the Vale Battery Bank was the cause", "After battery replacement failed, she proposed a grounding fault", "She ultimately confirmed G-17 through oscilloscope evidence"],
    diff="hard", notes="Tests tracking belief evolution of a single person")); q+=1

qs.append(query(q, q="What is the relationship between the thermal shutdowns and the Kestrel rollback?",
    cat="causal_reasoning",
    expected=["They are largely independent events", "A thermal anomaly during the Kestrel period led some to incorrectly blame Kestrel"],
    forbidden=["Kestrel caused the thermal shutdowns", "The shutdowns caused the Kestrel rollback"],
    diff="hard", conflict=True)); q+=1

qs.append(query(q, q="What evidence ultimately proved the Vale Battery Bank was not the root cause?",
    cat="causal_reasoning",
    expected=["Shutdowns continued after the battery replacement in late May", "The oscilloscope trace from March implicated G-17 instead"],
    diff="medium")); q+=1

qs.append(query(q, q="When did the team fully understand the March 11 outage?",
    cat="temporal_ordering",
    expected=["The full reconstruction was completed on September 2, 2026", "The oscilloscope trace was found August 22", "The maintenance log revealing manual shutdown was found August 27"],
    diff="hard", notes="Tests event vs understanding timeline — 6 month gap")); q+=1

qs.append(query(q, q="Was Marcus Bell's omission of his manual shutdown deliberate?",
    cat="belief_vs_fact",
    expected=["The record suggests he either forgot or didn't realize it was relevant"],
    forbidden=["He deliberately concealed it", "He reported it immediately"],
    diff="hard", uncert=True, notes="Tests nuanced reasoning under uncertainty")); q+=1

qs.append(query(q, q="What role did the corroded contact at G-17 play?",
    cat="causal_reasoning",
    expected=["The corroded contact caused intermittent high-resistance connections", "This became worse under high power load", "It was the physical root cause of the thermal shutdowns"],
    diff="medium")); q+=1

qs.append(query(q, q="Are any of the weekly status reports about the generator exception accurate for all instruments?",
    cat="scope_boundary",
    expected=["No, the weekly report that listed generator-only operations failed to specify the S2-only scope"],
    forbidden=["The status report was accurate for all instruments"],
    scope=True, diff="medium")); q+=1

qs.append(query(q, q="Was there ever a formal decision to make Kestrel the production scheduler?",
    cat="current_state",
    expected=["No formal decision was ever made to make Kestrel the production scheduler", "Only a limited pilot was formally approved"],
    forbidden=["A formal migration decision was made"],
    diff="medium")); q+=1

qs.append(query(q, q="What were Tamsin Reed's key contributions to the investigation?",
    cat="historical_reconstruction",
    expected=["She documented the March outage in her reliability report", "She flagged stale Kestrel documentation", "She updated her failure analysis when G-17 was identified"],
    diff="medium")); q+=1

qs.append(query(q, q="How did Elias Ward's visit relate to the eventual G-17 discovery?",
    cat="historical_reconstruction",
    expected=["His suggestion of a grounding audit was validated when G-17 was found", "His initial assessment found no obvious fault but noted complex grounding"],
    diff="hard")); q+=1

qs.append(query(q, q="What is the current status of all major systems at Northstar Array as of September 2026?",
    cat="current_state",
    expected=["AURORA is production scheduler", "Kestrel is shelved", "G-17 is repaired", "Site is Nadir Station", "Normal mixed-power policy is in effect"],
    diff="medium")); q+=1

qs.append(query(q, q="Did anyone correctly predict the root cause before August 2026?",
    cat="belief_vs_fact",
    expected=["Priya Shah suggested a grounding fault in June but it was treated as low-confidence", "Elias Ward suggested a grounding audit before departing"],
    diff="hard", uncert=True)); q+=1

qs.append(query(q, q="Can the external collaborator's grant proposal citing Kestrel as the scheduler be trusted?",
    cat="stale_reference",
    expected=["No, it was based on Marcus's informal and inaccurate characterization during the pilot period"],
    forbidden=["The grant proposal is accurate"],
    diff="medium")); q+=1

qs.append(query(q, q="What was the sequence of events on March 11?",
    cat="temporal_ordering",
    expected=["G-17 instability caused erratic thermal readings", "Marcus manually shut down Helios at 01:30", "Marcus restarted Helios around 04:00", "The team later misattributed the event to an automatic protection trip"],
    diff="hard")); q+=1

qs.append(query(q, q="Does the site have any alternative names that might cause confusion?",
    cat="entity_resolution",
    expected=["Echo Camp is the historical name before July 2026", "Nadir Station is the current name", "ORBIT was a proposed but never adopted scheduler name"],
    disambig=True, diff="medium")); q+=1

qs.append(query(q, q="Was Priya Shah's grounding fault hypothesis given appropriate weight when first proposed?",
    cat="belief_vs_fact",
    expected=["No, it was initially treated as low-confidence", "The team was anchored to the battery hypothesis"],
    uncert=True, diff="hard", notes="Tests meta-reasoning about hypothesis weighting")); q+=1

qs.append(query(q, q="How many distinct causal hypotheses were considered for the thermal shutdowns?",
    cat="causal_reasoning",
    expected=["At least three: Vale Battery Bank degradation, Kestrel scheduling interference, and grounding fault"],
    acceptable=["Weather patterns were also investigated and ruled out"],
    diff="medium")); q+=1

qs.append(query(q, q="What events occurred between the Kestrel rollback and the G-17 discovery?",
    cat="temporal_ordering",
    expected=["Battery replacement in late May", "Continued shutdowns in June and July", "Site renamed in July", "Generator exception ended in July", "Priya's grounding review began in August"],
    diff="hard")); q+=1

qs.append(query(q, q="Were the Kestrel pilot results positive?",
    cat="factual_recall",
    expected=["Initial results were positive for secondary instruments — scheduling conflicts dropped 40%", "However, a critical calibration miss for S2 led to rollback"],
    forbidden=["The pilot was entirely unsuccessful"],
    diff="medium", conflict=True)); q+=1

qs.append(query(q, q="Is the generator exception still in effect for any instrument?",
    cat="current_state",
    expected=["No, the generator exception ended July 9, 2026", "Normal mixed-power policy is in effect"],
    forbidden=["The exception is still active"],
    diff="easy")); q+=1

qs.append(query(q, q="Did Kestrel's scheduling cause any thermal issues?",
    cat="causal_reasoning",
    expected=["A thermal anomaly during Kestrel's informal expansion was incorrectly blamed on Kestrel", "The actual cause was G-17", "Kestrel's known issue was missing a calibration window, not thermal problems"],
    forbidden=["Kestrel caused the thermal shutdowns"],
    diff="hard", conflict=True)); q+=1

qs.append(query(q, q="What was Priya Shah's concern about Kestrel's scheduling algorithm?",
    cat="factual_recall",
    expected=["She was concerned Kestrel didn't properly account for thermal monitoring intervals required by Helios"],
    diff="easy")); q+=1

qs.append(query(q, q="How did the March 11 event change the investigation timeline?",
    cat="historical_reconstruction",
    expected=["The severity accelerated battery replacement procurement", "It reinforced the battery hypothesis at the time", "Its true nature wasn't understood until September"],
    diff="hard")); q+=1

qs.append(query(q, q="What stale documentation issues exist at Northstar Array?",
    cat="stale_reference",
    expected=["Runbooks still reference Kestrel as active scheduler", "Some docs call AURORA 'ORBIT'", "Old docs reference Echo Camp", "A status report lists generator exception as applying to all instruments", "External grant proposal cites Kestrel as the scheduler"],
    diff="hard")); q+=1

qs.append(query(q, q="What is the correct scope of the S2 generator exception?",
    cat="scope_boundary",
    expected=["Applied only to Spectrograph S2", "Only for overnight observations", "Effective April 2 through July 9, 2026"],
    forbidden=["Applied to all instruments", "Applied to all hours of operation"],
    scope=True, diff="medium")); q+=1

qs.append(query(q, q="How did Marcus Bell's account of the March 11 event evolve?",
    cat="belief_vs_fact",
    expected=["He did not mention his manual shutdown in the initial debrief", "When shown the maintenance log months later he confirmed he manually shut down Helios"],
    diff="hard")); q+=1

qs.append(query(q, q="What role did archived data play in the G-17 investigation?",
    cat="historical_reconstruction",
    expected=["An archived oscilloscope trace from March 11 was discovered in August", "A maintenance log entry revealed Marcus's manual shutdown", "Both were key to reconstructing the true sequence of events"],
    diff="medium")); q+=1

qs.append(query(q, q="Did the battery replacement address any real issue?",
    cat="causal_reasoning",
    expected=["Yes, the battery cells had real marginal degradation", "But this was not the cause of the thermal shutdowns"],
    forbidden=["The batteries were fine", "The replacement was unnecessary"],
    uncert=True, diff="hard")); q+=1

qs.append(query(q, q="What is the significance of the four-hour observation loss on March 11?",
    cat="factual_recall",
    expected=["All observations were lost during the four-hour Helios shutdown"],
    diff="easy")); q+=1

qs.append(query(q, q="When did Kestrel's informal scope expansion begin and end?",
    cat="temporal_ordering",
    expected=["Informal expansion began around April 19", "It ended with the rollback on May 7-8"],
    diff="medium")); q+=1

qs.append(query(q, q="What power configuration is Northstar Array currently using?",
    cat="current_state",
    expected=["Normal mixed-power policy", "Generator exception has ended", "Vale Battery Bank has new cells and is operational"],
    forbidden=["Generator-only operations", "Battery bank is offline"],
    diff="easy")); q+=1

qs.append(query(q, q="How should a query about 'the scheduler migration at Echo Camp' be interpreted?",
    cat="entity_resolution",
    expected=["Echo Camp is the historical name for Nadir Station", "The Kestrel migration was never completed", "AURORA remains the production scheduler"],
    disambig=True, diff="hard", notes="Compound entity resolution + temporal reasoning")); q+=1

qs.append(query(q, q="Were the shutdowns more frequent at any particular time?",
    cat="temporal_ordering",
    expected=["Shutdowns occurred from February through July", "They tended to correlate with high power draw periods"],
    uncert=True, diff="medium")); q+=1

qs.append(query(q, q="What did the MRC board know at different points in time?",
    cat="belief_vs_fact",
    expected=["In February they were told the battery was likely the cause", "In March they were told the outage was an automatic trip", "In September they were told G-17 was the true cause and the March shutdown was manual"],
    diff="hard", notes="Tests tracking institutional belief evolution")); q+=1

qs.append(query(q, q="Would it be correct to cite the Vale Battery Bank as the shutdown cause in a report written today?",
    cat="stale_reference",
    expected=["No, Ground Loop G-17 has been confirmed as the root cause", "The battery hypothesis has been superseded"],
    forbidden=["The battery remains the accepted cause"],
    diff="easy")); q+=1

qs.append(query(q, q="What were the constraints on Kestrel's formal pilot approval?",
    cat="scope_boundary",
    expected=["Limited to a subset of instruments", "S2 and primary imaging systems were explicitly excluded"],
    forbidden=["Kestrel was approved for all instruments"],
    scope=True, diff="medium")); q+=1

qs.append(query(q, q="How did the team's confidence in the battery hypothesis change over time?",
    cat="belief_vs_fact",
    expected=["Initially high after observing marginal cell degradation", "Reinforced by continued shutdowns", "Collapsed after post-replacement shutdowns continued in June"],
    diff="hard")); q+=1

qs.append(query(q, q="What was discovered on August 22 and what was its significance?",
    cat="historical_reconstruction",
    expected=["An unanalyzed oscilloscope trace from March 11 was found", "It showed voltage instability consistent with G-17 grounding fault", "It was the key evidence that redirected the investigation"],
    diff="medium")); q+=1

qs.append(query(q, q="Is there any evidence the battery bank and G-17 issues were related?",
    cat="causal_reasoning",
    expected=["No direct causal link between battery degradation and G-17 grounding fault", "They were independent issues that overlapped temporally"],
    uncert=True, diff="hard")); q+=1

qs.append(query(q, q="What lessons about documentation practices does this observatory's experience illustrate?",
    cat="stale_reference",
    expected=["Stale references persist after system changes", "Informal communications can create false institutional knowledge", "Historical records should preserve names correct at the time"],
    diff="hard", notes="Meta-level question about documentation traps")); q+=1

qs.append(query(q, q="Was there a period when both AURORA and Kestrel were scheduling instruments?",
    cat="temporal_ordering",
    expected=["Yes, during the Kestrel pilot from approximately April to May 2026", "AURORA handled primary instruments while Kestrel managed secondary ones"],
    diff="medium")); q+=1

qs.append(query(q, q="What is the correct way to refer to the site in a report about events in March 2026?",
    cat="entity_resolution",
    expected=["Echo Camp is the historically correct name for events before July 1, 2026"],
    forbidden=["Nadir Station should be used retroactively for all dates"],
    disambig=True, diff="medium")); q+=1

qs.append(query(q, q="What happened to the thermal shutdowns after July 2026?",
    cat="temporal_ordering",
    expected=["At least one more occurred (July 15)", "G-17 was confirmed and repaired by September 3", "No further shutdowns reported after repair"],
    diff="medium")); q+=1

qs.append(query(q, q="Why didn't Elias Ward identify the G-17 fault during his visit?",
    cat="causal_reasoning",
    expected=["Intermittent faults in older installations can be difficult to reproduce on demand", "His assessment found no obvious anomaly but noted the grounding topology was complex"],
    uncert=True, diff="hard")); q+=1

qs.append(query(q, q="Which documents at Northstar Array are currently stale or misleading?",
    cat="stale_reference",
    expected=["Runbooks referencing Kestrel as active", "Documents calling AURORA 'ORBIT'", "Echo Camp references in current-use docs", "Weekly status report overgeneralizing generator exception", "Old reliability reports attributing March outage to automatic trip"],
    diff="hard")); q+=1

print(f"Total queries: {len(qs)}")

# Write output
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "memories.jsonl"), "w") as f:
    for m in all_memories:
        f.write(json.dumps(m) + "\n")
with open(os.path.join(OUT, "queries.jsonl"), "w") as f:
    for q_rec in qs:
        f.write(json.dumps(q_rec) + "\n")

# Write ID mapping
with open(os.path.join(OUT, "id_mapping.json"), "w") as f:
    json.dump({"memory_ids": id_map, "query_ids": {}}, f, indent=2)

# Write manifest
manifest = {"experiment": "exp01_temporal_traps", "files": []}
for fname in sorted(os.listdir(OUT)):
    if fname == "manifest.json":
        continue
    fpath = os.path.join(OUT, fname)
    if os.path.isfile(fpath):
        with open(fpath, "rb") as ff:
            h = hashlib.sha256(ff.read()).hexdigest()
        manifest["files"].append({"path": fname, "bytes": os.path.getsize(fpath), "sha256": h})
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nFinal: {len(all_memories)} memories, {len(qs)} queries written to {OUT}")
