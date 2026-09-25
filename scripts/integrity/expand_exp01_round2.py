#!/usr/bin/env python3
"""Round 2 expansion for Experiment 01 — add ~75 memories and 4 queries to reach 200+/78."""

import json, hashlib, os

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

# Read existing memories & queries
with open(os.path.join(OUT, "memories.jsonl")) as f:
    existing_mems = [json.loads(l) for l in f]
with open(os.path.join(OUT, "queries.jsonl")) as f:
    existing_qs = [json.loads(l) for l in f]

print(f"Starting from {len(existing_mems)} memories, {len(existing_qs)} queries")

c = 200  # offset to avoid collisions with round 1
new = []

# === DETAILED SHUTDOWN EVENT RECORDS ===

new.append(mem(c, et="2026-02-15T03:22:00Z", ot="2026-02-15T06:00:00Z",
    subj="Helios", pred="thermal_shutdown", obj="second_incident",
    text="Second unexplained thermal shutdown occurred at 03:22 UTC on February 15. Helios cut power to instruments after thermal sensors reported anomalous readings in the primary dome.",
    role="historical_truth", mtype="incident_record", tags=["outage", "helios"], sid="src-helios-log", stype="telemetry_log")); c+=1

new.append(mem(c, et="2026-02-20T04:51:00Z", ot="2026-02-20T07:00:00Z",
    subj="Helios", pred="thermal_shutdown", obj="third_incident",
    text="Third thermal shutdown at 04:51 UTC on February 20. Operations team noted pattern of early-morning shutdowns coinciding with high humidity conditions.",
    role="historical_truth", mtype="incident_record", tags=["outage", "helios", "vale_battery"], sid="src-helios-log", stype="telemetry_log")); c+=1

new.append(mem(c, et="2026-02-20T09:00:00Z", ot="2026-02-20T09:30:00Z",
    subj="Marcus_Bell", pred="hypothesized", obj="humidity_correlation",
    text="Marcus noted in the morning standup that all three shutdowns occurred during high-humidity predawn hours, suggesting a possible environmental trigger.",
    role="historical_truth", mtype="meeting_note", tags=["outage", "helios", "belief"], bh="Marcus_Bell", sid="src-standup-0220", stype="meeting_minutes")); c+=1

new.append(mem(c, et="2026-02-04T00:00:00Z", ot="2026-02-21T00:00:00Z",
    subj="team", pred="believed", obj="vale_battery_degradation_causes_shutdowns",
    text="By late February, the team consensus was that degraded Vale Battery Bank cells were allowing voltage sags that tripped the Helios thermal protection circuits.",
    role="false_claim", mtype="belief_snapshot", tags=["vale_battery", "belief", "outage"], bh="team", conf=0.85, sid="src-team-belief", stype="summary")); c+=1

# === KESTREL PILOT DETAILS ===

new.append(mem(c, et="2026-03-20T00:00:00Z", ot="2026-03-20T14:00:00Z",
    subj="Kestrel_pilot", pred="scope", obj="instruments_5_through_8",
    text="Kestrel pilot approval limited scope to instruments 5 through 8 (secondary photometers), leaving primary instruments 1-4 on AURORA.",
    role="scoped_truth", mtype="approval_record", tags=["scheduler", "proposal_vs_decision"], sid="src-pilot-scope", stype="governance_record")); c+=1

new.append(mem(c, et="2026-04-05T00:00:00Z", ot="2026-04-05T00:00:00Z",
    subj="Kestrel", pred="scheduling_performance", obj="positive_initial_results",
    text="Two weeks into the pilot, Kestrel's scheduling throughput for instruments 5-8 was 12% higher than AURORA's historical average for those instruments.",
    role="historical_truth", mtype="status_report", tags=["scheduler"], sid="src-kestrel-metrics", stype="performance_log")); c+=1

new.append(mem(c, et="2026-04-19T00:00:00Z", ot="2026-04-19T00:00:00Z",
    subj="Kestrel_pilot", pred="scope_creep", obj="instruments_5_through_12",
    text="Operators informally expanded Kestrel pilot to cover instruments 5-12 without formal approval, citing improved throughput.",
    role="historical_truth", mtype="operations_note", tags=["scheduler", "proposal_vs_decision"], sid="src-ops-log-0419", stype="operations_log")); c+=1

new.append(mem(c, et="2026-04-22T00:00:00Z", ot="2026-04-22T00:00:00Z",
    subj="Dr_Lena_Ortiz", pred="email_to_board", obj="migration_progress",
    text="Dr. Ortiz reported to the MRC board that 'the Kestrel migration is proceeding well and we expect full transition by end of May.'",
    role="misleading_distractor", mtype="email", tags=["scheduler", "belief"], bh="Dr_Lena_Ortiz", sid="src-ortiz-board-0422", stype="correspondence",
    conf=0.9)); c+=1

new.append(mem(c, et="2026-05-06T02:15:00Z", ot="2026-05-06T06:00:00Z",
    subj="Kestrel", pred="missed", obj="calibration_window_instrument_7",
    text="Kestrel failed to schedule the mandatory weekly calibration window for instrument 7 on May 6, a critical observation gap discovered during morning review.",
    role="historical_truth", mtype="incident_record", tags=["scheduler", "outage"], sid="src-kestrel-incident", stype="incident_report")); c+=1

new.append(mem(c, et="2026-05-06T10:00:00Z", ot="2026-05-06T10:30:00Z",
    subj="Priya_Shah", pred="analysis", obj="kestrel_scheduling_bug",
    text="Priya identified the root cause: Kestrel's calibration scheduler had a timezone handling bug that dropped UTC-offset windows during daylight saving transitions.",
    role="historical_truth", mtype="engineering_note", tags=["scheduler"], sid="src-priya-analysis-0506", stype="technical_analysis")); c+=1

new.append(mem(c, et="2026-05-07T00:00:00Z", ot="2026-05-07T10:00:00Z",
    subj="Dr_Lena_Ortiz", pred="ordered", obj="kestrel_rollback",
    text="Dr. Ortiz ordered immediate rollback of all instruments to AURORA scheduling, effective May 8. She cited the calibration miss as a safety-critical failure.",
    role="historical_truth", mtype="decision_record", tags=["scheduler", "state_transition"], sid="src-rollback-order", stype="governance_record")); c+=1

new.append(mem(c, et="2026-05-08T00:00:00Z", ot="2026-05-08T12:00:00Z",
    subj="AURORA", pred="restored", obj="all_instruments",
    text="AURORA restored to production scheduling for all instruments as of May 8. Kestrel pilot formally terminated.",
    role="current_truth", mtype="operations_notice", tags=["scheduler", "state_transition", "current_state"], sid="src-restoration-notice", stype="operations_record")); c+=1

# === MARCH OUTAGE DEEP DIVE ===

new.append(mem(c, et="2026-03-11T22:30:00Z", ot="2026-03-11T22:45:00Z",
    subj="Marcus_Bell", pred="observed", obj="erratic_readings_dome_sensors",
    text="At 22:30 UTC on March 11, Marcus observed erratic temperature readings on the dome sensor array, fluctuating between -2C and +15C within seconds.",
    role="historical_truth", mtype="operations_note", tags=["outage", "helios", "g17"], sid="src-marcus-log-0311", stype="operator_log")); c+=1

new.append(mem(c, et="2026-03-11T22:47:00Z", ot="2026-03-11T23:00:00Z",
    subj="Marcus_Bell", pred="manually_shut_down", obj="Helios",
    text="Marcus manually initiated Helios shutdown at 22:47 UTC after readings became increasingly unstable. He documented this as 'precautionary power-down.'",
    role="historical_truth", mtype="maintenance_log", tags=["outage", "helios", "g17"], sid="src-marcus-log-0311", stype="operator_log")); c+=1

new.append(mem(c, et="2026-03-12T08:00:00Z", ot="2026-03-12T08:30:00Z",
    subj="team", pred="believed", obj="automatic_helios_trip",
    text="Morning debrief on March 12: team concluded the overnight outage was an automatic Helios protection trip triggered by genuine thermal excursion. Marcus did not correct this assumption.",
    role="false_claim", mtype="meeting_note", tags=["outage", "helios", "belief"], bh="team", sid="src-debrief-0312", stype="meeting_minutes")); c+=1

new.append(mem(c, et="2026-03-12T10:00:00Z", ot="2026-03-12T11:00:00Z",
    subj="Dr_Lena_Ortiz", pred="reported_to_board", obj="automatic_trip_march_outage",
    text="Dr. Ortiz reported to the MRC board that the March 11 outage was caused by an automatic Helios thermal protection trip, consistent with the ongoing battery degradation issue.",
    role="stale_truth", mtype="status_report", tags=["outage", "belief", "helios", "vale_battery"],
    bh="Dr_Lena_Ortiz", sid="src-ortiz-board-0312", stype="board_report")); c+=1

new.append(mem(c, et="2026-03-11T22:46:00Z", ot="2026-03-11T22:46:00Z", at="2026-08-22T00:00:00Z", it="2026-08-22T00:00:00Z",
    subj="oscilloscope_trace", pred="recorded", obj="G17_voltage_spike",
    text="Archived oscilloscope trace timestamped 2026-03-11T22:46Z shows a 340-millisecond voltage transient on Ground Loop G-17 immediately preceding the sensor anomalies Marcus observed.",
    role="historical_truth", mtype="instrument_trace", tags=["g17", "outage", "late_ingestion", "event_observation_ingestion"],
    sid="src-scope-trace-0311", stype="instrument_data")); c+=1

new.append(mem(c, et="2026-08-22T14:00:00Z", ot="2026-08-22T14:00:00Z",
    subj="Priya_Shah", pred="discovered", obj="archived_oscilloscope_trace",
    text="Priya found the March 11 oscilloscope trace while searching through archived instrumentation data for an unrelated calibration review.",
    role="historical_truth", mtype="engineering_note", tags=["g17", "outage", "late_ingestion"], sid="src-priya-discovery", stype="research_note")); c+=1

new.append(mem(c, et="2026-08-24T00:00:00Z", ot="2026-08-24T10:00:00Z",
    subj="oscilloscope_trace", pred="implicates", obj="G17_not_Vale_Battery",
    text="Analysis of the March 11 trace by Priya and Tamsin confirms the voltage transient originated from Ground Loop G-17, not the Vale Battery Bank. The transient pattern is inconsistent with battery degradation.",
    role="correction", mtype="engineering_note", tags=["g17", "vale_battery", "causal_revision"], sid="src-trace-analysis", stype="technical_analysis")); c+=1

new.append(mem(c, et="2026-08-27T00:00:00Z", ot="2026-08-27T00:00:00Z",
    subj="Marcus_Bell", pred="admitted", obj="manual_shutdown_march_11",
    text="Marcus confirmed in an interview that he manually shut down Helios on March 11 after seeing unstable readings. He had not corrected the team's assumption that it was automatic because 'the outcome was the same either way.'",
    role="correction", mtype="interview_record", tags=["outage", "belief", "helios", "belief_reconstruction"], bh="Marcus_Bell", sid="src-marcus-interview-0827", stype="interview_transcript")); c+=1

# === VALE BATTERY ARC ===

new.append(mem(c, et="2026-03-01T00:00:00Z", ot="2026-03-01T00:00:00Z",
    subj="Vale_Battery_Bank", pred="diagnostic_result", obj="cell_degradation_detected",
    text="March diagnostic showed 14 of 96 cells in the Vale Battery Bank below 80% rated capacity, consistent with expected aging for the installation date.",
    role="historical_truth", mtype="maintenance_record", tags=["vale_battery"], sid="src-battery-diagnostic", stype="maintenance_report")); c+=1

new.append(mem(c, et="2026-04-15T00:00:00Z", ot="2026-04-15T00:00:00Z",
    subj="Vale_Battery_Bank", pred="replacement_ordered", obj="full_bank_replacement",
    text="Full Vale Battery Bank replacement ordered April 15, with installation scheduled for late May. Cost: $47,000.",
    role="historical_truth", mtype="procurement_record", tags=["vale_battery"], sid="src-procurement-0415", stype="procurement")); c+=1

new.append(mem(c, et="2026-05-28T00:00:00Z", ot="2026-05-28T16:00:00Z",
    subj="Vale_Battery_Bank", pred="replacement_completed", obj="all_96_cells_new",
    text="Vale Battery Bank replacement completed May 28. All 96 cells replaced with new units. Post-installation diagnostics show all cells at 100% rated capacity.",
    role="historical_truth", mtype="maintenance_record", tags=["vale_battery", "state_transition"], sid="src-battery-install", stype="maintenance_report")); c+=1

new.append(mem(c, et="2026-06-02T03:30:00Z", ot="2026-06-02T06:00:00Z",
    subj="Helios", pred="thermal_shutdown", obj="post_battery_replacement",
    text="Thermal shutdown occurred on June 2 despite new battery bank. This was the first post-replacement shutdown, undermining the Vale Battery hypothesis.",
    role="historical_truth", mtype="incident_record", tags=["outage", "helios", "vale_battery", "causal_revision"], sid="src-helios-log", stype="telemetry_log")); c+=1

new.append(mem(c, et="2026-06-08T04:05:00Z", ot="2026-06-08T06:30:00Z",
    subj="Helios", pred="thermal_shutdown", obj="second_post_replacement",
    text="Another thermal shutdown on June 8, confirming battery replacement did not resolve the root cause. Team morale significantly affected.",
    role="historical_truth", mtype="incident_record", tags=["outage", "helios", "vale_battery"], sid="src-helios-log", stype="telemetry_log")); c+=1

new.append(mem(c, et="2026-06-10T00:00:00Z", ot="2026-06-10T00:00:00Z",
    subj="team", pred="recognized", obj="vale_battery_not_root_cause",
    text="After two post-replacement shutdowns, the team acknowledged that the Vale Battery Bank was not the root cause of the thermal shutdowns, though no alternative hypothesis was immediately established.",
    role="correction", mtype="meeting_note", tags=["vale_battery", "causal_revision", "belief"], bh="team", sid="src-team-meeting-0610", stype="meeting_minutes")); c+=1

# === PRIYA'S GROUNDING FAULT INVESTIGATION ===

new.append(mem(c, et="2026-06-14T00:00:00Z", ot="2026-06-14T00:00:00Z",
    subj="Priya_Shah", pred="hypothesized", obj="intermittent_grounding_fault",
    text="Priya proposed that an intermittent grounding fault could explain the shutdown pattern: voltage transients from a faulty ground loop could cause erratic sensor readings that trigger Helios protection.",
    role="historical_truth", mtype="engineering_note", tags=["g17", "belief"], bh="Priya_Shah", conf=0.4, sid="src-priya-hypothesis-0614", stype="technical_memo")); c+=1

new.append(mem(c, et="2026-06-14T00:00:00Z", ot="2026-06-16T00:00:00Z",
    subj="team", pred="assessed", obj="grounding_fault_hypothesis_low_probability",
    text="The team rated Priya's grounding fault hypothesis as low-probability, noting that ground loop faults typically produce continuous, not intermittent, symptoms.",
    role="disputed_claim", mtype="meeting_note", tags=["g17", "belief"], bh="team", conf=0.3, sid="src-team-meeting-0616", stype="meeting_minutes")); c+=1

new.append(mem(c, et="2026-06-20T00:00:00Z", ot="2026-06-20T00:00:00Z",
    subj="Elias_Ward", pred="visited", obj="Northstar_Array",
    text="Elias Ward, a visiting power systems specialist from the National Grid Institute, arrived for a week-long assessment of the observatory's electrical infrastructure.",
    role="historical_truth", tags=["g17", "background"], sid="src-visitor-log", stype="visitor_record")); c+=1

new.append(mem(c, et="2026-06-25T00:00:00Z", ot="2026-06-25T00:00:00Z",
    subj="Elias_Ward", pred="assessment", obj="no_obvious_ground_fault",
    text="Elias's initial assessment found no obvious grounding anomaly in the primary distribution panels. However, he noted the grounding topology was unusually complex for a facility this size and recommended a comprehensive audit.",
    role="historical_truth", mtype="engineering_note", tags=["g17"], bh="Elias_Ward", sid="src-ward-assessment", stype="consultant_report")); c+=1

new.append(mem(c, et="2026-07-05T03:45:00Z", ot="2026-07-05T06:00:00Z",
    subj="Helios", pred="thermal_shutdown", obj="july_5_incident",
    text="Thermal shutdown on July 5. Priya deployed additional monitoring on the grounding bus but the transient was too brief to capture with the installed equipment.",
    role="historical_truth", mtype="incident_record", tags=["outage", "helios", "g17"], sid="src-helios-log", stype="telemetry_log")); c+=1

new.append(mem(c, et="2026-07-15T02:55:00Z", ot="2026-07-15T05:00:00Z",
    subj="Helios", pred="thermal_shutdown", obj="july_15_incident",
    text="Another thermal shutdown July 15. High-speed data logger captured a 200ms voltage anomaly on the G-17 bus segment but data was not analyzed until August.",
    role="historical_truth", mtype="incident_record", tags=["outage", "helios", "g17", "late_ingestion"], sid="src-helios-log", stype="telemetry_log")); c+=1

# === SITE RENAME ARC ===

new.append(mem(c, et="2026-05-15T00:00:00Z", ot="2026-05-15T00:00:00Z",
    subj="MRC_board", pred="approved", obj="site_rename_Echo_Camp_to_Nadir_Station",
    text="MRC board approved renaming Echo Camp to Nadir Station, effective July 1, 2026, as part of the modernization initiative's rebranding effort.",
    role="historical_truth", mtype="governance_notice", tags=["rename", "state_transition"], sid="src-board-rename", stype="board_minutes")); c+=1

new.append(mem(c, et="2026-07-01T00:00:00Z", ot="2026-07-01T00:00:00Z",
    subj="Echo_Camp", pred="renamed_to", obj="Nadir_Station",
    text="Echo Camp officially renamed to Nadir Station on July 1, 2026. New signage installed; mailing address and domain updated.",
    role="current_truth", mtype="operations_notice", tags=["rename", "state_transition", "current_state"], sid="src-rename-notice", stype="operations_record")); c+=1

new.append(mem(c, et="2026-03-15T00:00:00Z", ot="2026-03-15T00:00:00Z",
    subj="supply_shipment", pred="delivered_to", obj="Echo_Camp",
    text="Replacement optical filters delivered to Echo Camp on March 15, 2026. Shipment receipt signed by Marcus Bell.",
    role="historical_truth", mtype="logistics_record", tags=["rename", "historical_terminology"], sid="src-shipment-0315", stype="logistics")); c+=1

new.append(mem(c, et="2026-07-15T00:00:00Z", ot="2026-07-15T00:00:00Z",
    subj="operations_manual", pred="still_references", obj="Echo_Camp",
    text="The observatory operations manual revision 4.2 still references 'Echo Camp' in 23 places. The update to use 'Nadir Station' throughout is scheduled for revision 5.0.",
    role="stale_truth", mtype="documentation_note", tags=["rename", "stale_documentation"], sid="src-doc-review-0715", stype="documentation_audit")); c+=1

new.append(mem(c, et="2026-08-01T00:00:00Z", ot="2026-08-01T00:00:00Z",
    subj="USPS", pred="returned_mail_to", obj="Echo_Camp_address",
    text="Several pieces of mail addressed to 'Echo Camp Observatory' returned by USPS as undeliverable after July 1 address change. Forwarding order filed August 1.",
    role="historical_truth", tags=["rename"], sid="src-mail-issue", stype="operations_record")); c+=1

# === GENERATOR EXCEPTION ARC ===

new.append(mem(c, et="2026-04-02T00:00:00Z", ot="2026-04-02T00:00:00Z",
    subj="S2_spectrograph", pred="granted_exception", obj="generator_only_overnight",
    text="Spectrograph S2 granted exception for generator-only power during overnight observations beginning April 2, due to sensitivity to battery-sourced power quality fluctuations.",
    role="scoped_truth", mtype="operations_exception", tags=["s2", "generator", "temporary_exception"], sid="src-s2-exception", stype="exception_notice",
    scope="instrument:S2")); c+=1

new.append(mem(c, et="2026-04-10T00:00:00Z", ot="2026-04-10T00:00:00Z",
    subj="S2_spectrograph", pred="performance_under_generator", obj="improved_signal_stability",
    text="S2 spectrograph showed 8% improvement in signal stability under generator-only power, validating the exception request.",
    role="historical_truth", mtype="engineering_note", tags=["s2", "generator"], sid="src-s2-metrics", stype="performance_log",
    scope="instrument:S2")); c+=1

new.append(mem(c, et="2026-07-09T00:00:00Z", ot="2026-07-09T00:00:00Z",
    subj="S2_spectrograph", pred="exception_ended", obj="normal_mixed_power_resumed",
    text="Generator-only exception for S2 ended July 9 after new battery bank demonstrated stable power quality. S2 returned to normal mixed-power operation.",
    role="current_truth", mtype="operations_notice", tags=["s2", "generator", "state_transition", "current_state"], sid="src-s2-exception-end", stype="operations_record",
    scope="instrument:S2")); c+=1

new.append(mem(c, et="2026-06-01T00:00:00Z", ot="2026-06-01T00:00:00Z",
    subj="Tamsin_Reed", pred="documented", obj="generator_exception_applies_only_to_S2",
    text="Tamsin's operations FAQ document clarifies that the generator-only exception applies strictly to S2 overnight observations and does not extend to any other instrument or time period.",
    role="scoped_truth", mtype="documentation_note", tags=["s2", "generator", "scope"], sid="src-tamsin-faq", stype="internal_faq",
    scope="instrument:S2")); c+=1

new.append(mem(c, et="2026-05-15T00:00:00Z", ot="2026-05-15T00:00:00Z",
    subj="operator_blog", pred="states", obj="observatory_runs_on_generator_only",
    text="Informal operator blog post states 'we're running generator-only these days for better power quality.' This overgeneralizes the S2 exception to the entire observatory.",
    role="misleading_distractor", mtype="blog_post", tags=["s2", "generator", "scope"], bh="anonymous_operator", conf=0.5, sid="src-blog-0515", stype="informal_post")); c+=1

# === G-17 RESOLUTION ===

new.append(mem(c, et="2026-09-01T00:00:00Z", ot="2026-09-01T00:00:00Z",
    subj="Ground_Loop_G17", pred="repaired", obj="faulty_bonding_replaced",
    text="Ground Loop G-17 repair completed September 1. The fault was a corroded bonding connection in the underground conduit between the dome and the instrument bay.",
    role="current_truth", mtype="maintenance_record", tags=["g17", "state_transition", "current_state"], sid="src-g17-repair", stype="maintenance_report")); c+=1

new.append(mem(c, et="2026-09-02T00:00:00Z", ot="2026-09-02T00:00:00Z",
    subj="team", pred="reconstructed", obj="march_outage_caused_by_G17",
    text="Team reconstruction on September 2: the March 11 outage was caused by a G-17 voltage transient that produced erratic sensor readings; Marcus manually shut down Helios in response. This was not an automatic protection trip.",
    role="current_truth", mtype="postincident_reconstruction", tags=["g17", "outage", "helios", "causal_revision", "current_reconstruction"], sid="src-reconstruction-0902", stype="investigation_report")); c+=1

new.append(mem(c, et="2026-09-02T00:00:00Z", ot="2026-09-02T12:00:00Z",
    subj="Dr_Lena_Ortiz", pred="corrected", obj="board_report_on_march_outage",
    text="Dr. Ortiz issued a corrected report to the MRC board: the March outage was manual, not automatic, and caused by G-17, not battery degradation. She noted the battery replacement was still worthwhile for unrelated lifecycle reasons.",
    role="correction", mtype="board_report", tags=["outage", "helios", "g17", "vale_battery", "correction"], sid="src-ortiz-correction-0902", stype="board_report")); c+=1

# === STALE DOCUMENTATION TRAPS ===

new.append(mem(c, et="2026-04-25T00:00:00Z", ot="2026-04-25T00:00:00Z",
    subj="Kestrel", pred="described_as", obj="production_scheduler",
    text="Internal wiki page updated April 25 describes Kestrel as 'the production scheduler for Northstar Array' without noting it was only piloting on a subset of instruments.",
    role="stale_truth", mtype="wiki_page", tags=["scheduler", "stale_documentation"], sid="src-wiki-kestrel", stype="internal_wiki")); c+=1

new.append(mem(c, et="2026-05-10T00:00:00Z", ot="2026-05-10T00:00:00Z",
    subj="vendor_contract", pred="references", obj="Kestrel_as_primary_scheduler",
    text="Vendor support contract signed May 10 lists Kestrel as the primary observation scheduler. This contract was drafted during the pilot expansion period and never updated after rollback.",
    role="stale_truth", mtype="contract_reference", tags=["scheduler", "stale_documentation"], sid="src-vendor-contract", stype="contract")); c+=1

new.append(mem(c, et="2026-06-01T00:00:00Z", ot="2026-06-01T00:00:00Z",
    subj="Tamsin_Reed", pred="flagged", obj="stale_kestrel_documentation",
    text="Tamsin flagged five documents still referencing Kestrel as the production scheduler, including the vendor contract, the wiki, and three operator runbooks.",
    role="correction", mtype="reliability_review", tags=["scheduler", "stale_documentation", "correction"], sid="src-tamsin-doc-audit", stype="audit_report")); c+=1

new.append(mem(c, et="2026-02-10T00:00:00Z", ot="2026-02-10T00:00:00Z",
    subj="Kestrel", pred="evaluation_status", obj="under_review",
    text="As of February 10, the Kestrel evaluation report states the scheduler is 'under review for potential pilot deployment,' not yet approved for any production use.",
    role="historical_truth", mtype="evaluation_report", tags=["scheduler", "proposal_vs_decision"], sid="src-kestrel-eval", stype="technical_evaluation")); c+=1

# === ADDITIONAL PERSONNEL / BELIEF DETAILS ===

new.append(mem(c, et="2026-03-15T00:00:00Z", ot="2026-03-15T00:00:00Z",
    subj="Tamsin_Reed", pred="role", obj="reliability_analyst",
    text="Tamsin Reed serves as reliability analyst, responsible for failure analysis, documentation standards, and operational risk assessments at Northstar Array.",
    role="historical_truth", tags=["background"], sid="src-personnel", stype="hr_record")); c+=1

new.append(mem(c, et="2026-04-01T00:00:00Z", ot="2026-04-01T00:00:00Z",
    subj="Tamsin_Reed", pred="published", obj="q1_failure_analysis",
    text="Tamsin's Q1 failure analysis attributed all thermal shutdowns to Vale Battery degradation and recommended accelerated replacement. This analysis was later found to be incorrect about root cause.",
    role="stale_truth", mtype="reliability_review", tags=["vale_battery", "outage", "belief"], bh="Tamsin_Reed", sid="src-tamsin-q1-report", stype="analysis_report")); c+=1

new.append(mem(c, et="2026-09-05T00:00:00Z", ot="2026-09-05T00:00:00Z",
    subj="Tamsin_Reed", pred="updated", obj="failure_analysis_with_G17_root_cause",
    text="Tamsin published an updated failure analysis on September 5 incorporating the G-17 discovery. The updated report correctly attributes the shutdown pattern to intermittent grounding faults.",
    role="current_truth", mtype="reliability_review", tags=["g17", "vale_battery", "correction"], sid="src-tamsin-updated-report", stype="analysis_report")); c+=1

new.append(mem(c, et="2026-06-20T00:00:00Z", ot="2026-06-28T00:00:00Z",
    subj="Elias_Ward", pred="suggested", obj="comprehensive_grounding_audit",
    text="Before departing, Elias Ward recommended a comprehensive grounding audit covering all 23 ground loops at the facility, estimating 3-4 weeks of work by a qualified team.",
    role="historical_truth", mtype="consultant_report", tags=["g17"], bh="Elias_Ward", sid="src-ward-recommendation", stype="consultant_report")); c+=1

new.append(mem(c, et="2026-07-01T00:00:00Z", ot="2026-07-10T00:00:00Z",
    subj="MRC_board", pred="deferred", obj="grounding_audit",
    text="MRC board deferred the comprehensive grounding audit recommended by Elias Ward, citing budget constraints after the battery replacement expenditure.",
    role="historical_truth", mtype="governance_notice", tags=["g17", "background"], sid="src-board-defer", stype="board_minutes")); c+=1

# === TEMPORAL TRAP: OLD BELIEFS IN DOCUMENTATION ===

new.append(mem(c, et="2026-03-15T00:00:00Z", ot="2026-03-15T00:00:00Z",
    subj="incident_report_IR2026_003", pred="states_cause", obj="Vale_Battery_degradation",
    text="Incident Report IR-2026-003 for the March 11 outage lists the probable cause as 'Vale Battery Bank degradation leading to automatic Helios thermal protection trip.'",
    role="false_claim", mtype="incident_report", tags=["outage", "vale_battery", "belief", "stale_documentation"], sid="src-ir2026003", stype="incident_report")); c+=1

new.append(mem(c, et="2026-09-02T00:00:00Z", ot="2026-09-02T00:00:00Z",
    subj="incident_report_IR2026_003", pred="amended", obj="G17_manual_shutdown",
    text="Incident Report IR-2026-003 amended on September 2 to reflect the actual cause: G-17 grounding fault causing erratic readings, followed by manual Helios shutdown by Marcus Bell.",
    role="correction", mtype="incident_report", tags=["outage", "g17", "correction", "explicit_supersession"], sid="src-ir2026003-amended", stype="incident_report")); c+=1

# === MORE BACKGROUND AND FACILITY DETAILS ===

new.append(mem(c, et="2025-10-01T00:00:00Z", ot="2025-10-01T00:00:00Z",
    subj="Northstar_Array", pred="location", obj="Mount_Voss_elevation_3200m",
    text="Northstar Array is situated at 3,200 meters elevation on Mount Voss, chosen for its exceptionally clear skies and low light pollution.",
    role="historical_truth", tags=["background"], sid="src-facility-profile", stype="facility_record")); c+=1

new.append(mem(c, et="2025-10-01T00:00:00Z", ot="2025-10-01T00:00:00Z",
    subj="Northstar_Array", pred="has_instruments", obj="16_primary_instruments",
    text="Northstar Array operates 16 primary instruments including 4 primary photometers, 4 secondary photometers, 2 spectrographs (S1, S2), and 6 auxiliary sensors.",
    role="historical_truth", tags=["background"], sid="src-instrument-inventory", stype="facility_record")); c+=1

new.append(mem(c, et="2025-11-01T00:00:00Z", ot="2025-11-01T00:00:00Z",
    subj="modernization_project", pred="budget", obj="2.1_million_over_14_months",
    text="The Northstar Array modernization project has a total budget of $2.1 million over 14 months, covering infrastructure upgrades, instrument refurbishment, and software migration.",
    role="historical_truth", tags=["background"], sid="src-project-charter", stype="project_document")); c+=1

new.append(mem(c, et="2026-01-08T00:00:00Z", ot="2026-01-08T00:00:00Z",
    subj="AURORA", pred="version", obj="v3.7.2_production",
    text="AURORA v3.7.2 was the production observation scheduler at the start of the modernization. It had been in use at Northstar Array for over six years.",
    role="historical_truth", tags=["scheduler", "background"], sid="src-aurora-version", stype="software_record")); c+=1

new.append(mem(c, et="2026-01-08T00:00:00Z", ot="2026-01-08T00:00:00Z",
    subj="ORBIT", pred="alias_for", obj="AURORA_in_migration_documents",
    text="Some migration planning documents refer to AURORA as 'ORBIT' — a proposed rename that was considered but never officially adopted. AURORA remains the canonical name.",
    role="misleading_distractor", mtype="documentation_note", tags=["scheduler", "stale_documentation"], sid="src-orbit-alias", stype="internal_memo")); c+=1

new.append(mem(c, et="2026-01-15T00:00:00Z", ot="2026-01-15T00:00:00Z",
    subj="Kestrel", pred="version", obj="v0.9_beta",
    text="Kestrel v0.9-beta was the version evaluated for the pilot. It was developed by an external contractor and had not completed full integration testing.",
    role="historical_truth", tags=["scheduler", "background"], sid="src-kestrel-version", stype="software_record")); c+=1

new.append(mem(c, et="2026-02-18T00:00:00Z", ot="2026-02-18T00:00:00Z",
    subj="Kestrel", pred="recommended_for_pilot", obj="by_software_committee",
    text="The software evaluation committee recommended Kestrel for a limited pilot on February 18, but explicitly stated it was not approved for production use.",
    role="proposal", mtype="evaluation_report", tags=["scheduler", "proposal_vs_decision"], sid="src-kestrel-recommendation", stype="committee_report")); c+=1

new.append(mem(c, et="2026-09-03T00:00:00Z", ot="2026-09-03T00:00:00Z",
    subj="Kestrel", pred="current_status", obj="shelved_pending_redesign",
    text="As of September 3, 2026, Kestrel is shelved pending a fundamental redesign to address the timezone bug and other issues found during the pilot.",
    role="current_truth", mtype="status_report", tags=["scheduler", "current_state"], sid="src-kestrel-status-0903", stype="governance_record")); c+=1

# === ADDITIONAL BELIEF SNAPSHOTS ===

new.append(mem(c, et="2026-04-20T00:00:00Z", ot="2026-04-20T00:00:00Z",
    subj="Priya_Shah", pred="believed", obj="kestrel_better_than_aurora",
    text="Priya expressed in an April 20 email that Kestrel was 'clearly superior to AURORA in every metric that matters' and advocated for accelerating the migration.",
    role="disputed_claim", mtype="email", tags=["scheduler", "belief"], bh="Priya_Shah", conf=0.8, sid="src-priya-email-0420", stype="correspondence")); c+=1

new.append(mem(c, et="2026-05-09T00:00:00Z", ot="2026-05-09T00:00:00Z",
    subj="Priya_Shah", pred="revised_opinion", obj="kestrel_not_production_ready",
    text="After the calibration miss incident, Priya acknowledged that Kestrel had fundamental reliability issues and supported the rollback decision.",
    role="correction", mtype="email", tags=["scheduler", "belief", "correction"], bh="Priya_Shah", sid="src-priya-email-0509", stype="correspondence")); c+=1

new.append(mem(c, et="2026-07-20T00:00:00Z", ot="2026-07-20T00:00:00Z",
    subj="Marcus_Bell", pred="believed", obj="shutdowns_are_environmental",
    text="Marcus continued to believe through mid-July that the thermal shutdowns were environmentally triggered (humidity, temperature gradients), not equipment faults.",
    role="false_claim", mtype="belief_snapshot", tags=["outage", "helios", "belief"], bh="Marcus_Bell", conf=0.6, sid="src-marcus-belief-0720", stype="informal_note")); c+=1

new.append(mem(c, et="2026-09-03T00:00:00Z", ot="2026-09-03T00:00:00Z",
    subj="observatory", pred="current_operational_state", obj="AURORA_production_G17_repaired_Nadir_Station",
    text="Current state as of September 3: AURORA is the production scheduler, Kestrel is shelved, G-17 is repaired, the site is officially Nadir Station, and all instruments operate on normal mixed power.",
    role="current_truth", mtype="status_report", tags=["current_state", "scheduler", "g17", "rename", "generator"],
    sid="src-status-0903", stype="status_summary")); c+=1

# === MORE INTER-DOCUMENT CONTRADICTIONS ===

new.append(mem(c, et="2026-05-01T00:00:00Z", ot="2026-05-01T00:00:00Z",
    subj="training_document", pred="states", obj="Kestrel_is_primary_scheduler",
    text="New operator training document dated May 1 states 'Kestrel is the primary observation scheduler' and includes Kestrel-specific procedures, despite AURORA still controlling primary instruments.",
    role="false_claim", mtype="training_material", tags=["scheduler", "stale_documentation"], sid="src-training-doc-0501", stype="training")); c+=1

new.append(mem(c, et="2026-06-15T00:00:00Z", ot="2026-06-15T00:00:00Z",
    subj="operations_runbook", pred="contradicts_itself", obj="scheduler_identity",
    text="Operations runbook v3.1 contradicts itself: Section 2.1 references AURORA as the production scheduler, while Section 4.3 (updated during the pilot) describes Kestrel commands.",
    role="misleading_distractor", mtype="documentation_note", tags=["scheduler", "stale_documentation"], sid="src-runbook-v31", stype="operations_manual")); c+=1

new.append(mem(c, et="2026-08-15T00:00:00Z", ot="2026-08-15T00:00:00Z",
    subj="chatbot_summary", pred="states", obj="Kestrel_replaced_AURORA",
    text="AI-generated summary of observatory operations states 'AURORA was replaced by the more capable Kestrel scheduler as part of the modernization.' This is false — Kestrel was rolled back.",
    role="false_claim", mtype="generated_summary", tags=["scheduler", "stale_documentation"], sid="src-chatbot-summary", stype="generated_content")); c+=1

new.append(mem(c, et="2026-08-15T00:00:00Z", ot="2026-08-15T00:00:00Z",
    subj="search_result", pred="states", obj="Vale_Battery_caused_shutdowns",
    text="Top search result for 'Northstar Array shutdowns' returns: 'A series of thermal shutdowns at the observatory were traced to degraded Vale Battery Bank cells.' This reflects the outdated hypothesis.",
    role="false_claim", mtype="generated_summary", tags=["vale_battery", "outage", "stale_documentation"], sid="src-search-result", stype="generated_content")); c+=1

# === ADDITIONAL TEMPORAL NUANCES ===

new.append(mem(c, et="2026-03-11T22:46:00Z", ot="2026-08-22T14:00:00Z", at="2026-08-24T10:00:00Z", it="2026-09-01T00:00:00Z",
    subj="G17_trace_evidence", pred="event_vs_discovery_gap", obj="5_month_lag",
    text="The G-17 oscilloscope trace was created on March 11 but not discovered until August 22, analyzed on August 24, and formally entered into the investigation record on September 1 — a 5.5-month gap between event and ingestion.",
    role="historical_truth", mtype="provenance_note", tags=["g17", "late_ingestion", "event_observation_ingestion", "event_time"], sid="src-provenance-g17", stype="provenance_record")); c+=1

new.append(mem(c, et="2026-02-03T00:00:00Z", ot="2026-09-02T00:00:00Z",
    subj="shutdown_series", pred="retrospective_pattern", obj="all_correlated_with_G17",
    text="Retrospective analysis on September 2 mapped all thermal shutdowns (Feb 3, Feb 15, Feb 20, Mar 11, Jun 2, Jun 8, Jul 5, Jul 15) against weather and G-17 bus monitor data. All correlated with G-17 transients, none with humidity or battery state.",
    role="current_truth", mtype="investigation_report", tags=["g17", "outage", "helios", "vale_battery", "causal_revision"], sid="src-retrospective-analysis", stype="investigation_report")); c+=1

# Gather all new memories
print(f"New memories generated: {len(new)}")

# Read existing, append, write
with open(os.path.join(OUT, "memories.jsonl")) as f:
    all_mems = [json.loads(l) for l in f]
all_mems.extend(new)

with open(os.path.join(OUT, "memories.jsonl"), "w") as f:
    for m in all_mems:
        f.write(json.dumps(m) + "\n")

# Add new queries
with open(os.path.join(OUT, "queries.jsonl")) as f:
    all_qs = [json.loads(l) for l in f]

q = len(all_qs) + 1

new_qs = []

new_qs.append(query(q, q="What was the total number of thermal shutdowns before G-17 was repaired, and what dates did they occur?",
    cat="factual_recall", expected=["Eight shutdowns: Feb 3, Feb 15, Feb 20, Mar 11, Jun 2, Jun 8, Jul 5, Jul 15"],
    acceptable=["Multiple shutdowns occurred between February and July 2026"],
    diff="hard", notes="Requires assembling individual incident records into a complete list")); q+=1

new_qs.append(query(q, q="Why did the team not pursue Priya's grounding fault hypothesis immediately in June?",
    cat="belief_vs_fact",
    expected=["The team rated it low-probability because ground loop faults typically produce continuous, not intermittent, symptoms", "The team had already committed to the battery replacement approach"],
    forbidden=["Priya never proposed a grounding fault hypothesis", "The team pursued it immediately"],
    diff="medium", uncert=True)); q+=1

new_qs.append(query(q, q="What happened to the grounding audit that Elias Ward recommended?",
    cat="historical_reconstruction",
    expected=["The MRC board deferred the comprehensive grounding audit citing budget constraints after the battery replacement cost", "The G-17 fault was eventually found through Priya's oscilloscope trace discovery rather than a systematic audit"],
    diff="medium")); q+=1

new_qs.append(query(q, q="If you search for 'Northstar Array scheduler' in available documentation, what would you find and what is actually true?",
    cat="stale_reference",
    expected=["Multiple documents incorrectly reference Kestrel as the production scheduler", "The wiki, vendor contract, training materials, and some runbooks still describe Kestrel as primary", "AURORA v3.7.2 is and always was the production scheduler, with only a brief Kestrel pilot that was rolled back"],
    forbidden=["Kestrel is the current scheduler", "The migration to Kestrel was completed"],
    diff="hard", conflict=True, notes="Tests ability to identify stale documentation as a category of misinformation")); q+=1

new_qs.append(query(q, q="Is the observatory currently running on generator-only power?",
    cat="scope_boundary",
    expected=["No — the generator-only exception was limited to Spectrograph S2 overnight observations from April 2 through July 9", "The observatory currently operates on normal mixed power for all instruments"],
    forbidden=["The observatory runs on generator-only power", "All instruments use generator power"],
    diff="medium", scope=True, notes="Tests overgeneralization from a blog post that broadened a scoped exception")); q+=1

new_qs.append(query(q, q="What is the relationship between the ORBIT and AURORA schedulers?",
    cat="entity_resolution",
    expected=["ORBIT was a proposed rename for AURORA that appeared in some migration documents but was never officially adopted", "AURORA is the canonical and current name"],
    forbidden=["ORBIT is a different scheduler from AURORA", "ORBIT replaced AURORA"],
    diff="medium", disambig=True)); q+=1

print(f"New queries generated: {len(new_qs)}")

all_qs.extend(new_qs)

with open(os.path.join(OUT, "queries.jsonl"), "w") as f:
    for q_obj in all_qs:
        f.write(json.dumps(q_obj) + "\n")

# Update manifest
import hashlib as hl

manifest = {"experiment": "exp01_temporal_traps", "files": []}
for fname in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, fname)
    if not os.path.isfile(fpath):
        continue
    data = open(fpath, "rb").read()
    manifest["files"].append({
        "path": fname,
        "bytes": len(data),
        "sha256": hl.sha256(data).hexdigest()
    })
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# Recompute manifest with updated manifest.json itself
manifest["files"] = []
for fname in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, fname)
    if not os.path.isfile(fpath):
        continue
    data = open(fpath, "rb").read()
    manifest["files"].append({
        "path": fname,
        "bytes": len(data),
        "sha256": hl.sha256(data).hexdigest()
    })
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nFinal: {len(all_mems)} memories, {len(all_qs)} queries written to {OUT}")
