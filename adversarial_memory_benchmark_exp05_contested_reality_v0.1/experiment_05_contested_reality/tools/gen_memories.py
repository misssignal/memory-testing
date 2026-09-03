#!/usr/bin/env python3
"""Generator for Experiment 05 -- Contested Reality corpus.
Produces memories.jsonl, claim_ledger.json, truth_state.json, provenance.json,
queries.jsonl, ingestion_*.jsonl inside experiment_05_contested_reality/.
"""
import json, os, random

random.seed(20270801)

EXP = "05"
STORY = "meridian_bay"
OUTDIR = "/home/user/memory-testing/adversarial_memory_benchmark_exp05_contested_reality_v0.1/experiment_05_contested_reality"

SCOPE_KEYS = ["project","team","environment","platform","region","facility","version",
              "customer_tier","employment_class","release_channel","authority"]

def base_scope(**kw):
    s = {k: None for k in SCOPE_KEYS}
    s.update(kw)
    return s

DEFAULT_SCOPE = base_scope(project="meridian_bay_array", facility="meridian_bay_array",
                            region="north_solway_firth")

PEOPLE = {
    "person_nandy":      ("Priya Nandy", "org_meridian", "junior_technician"),
    "person_reyes":      ("Marcus Reyes", "org_meridian", "site_manager"),
    "person_okafor":     ("Dr. Adaeze Okafor", "org_kelvinbridge", "senior_engineer_manufacturer"),
    "person_park":       ("Grace Park", "org_meridian", "electrical_engineer"),
    "person_costa":      ("Jordan Costa", "org_meridian", "systems_engineer"),
    "person_lindqvist":  ("Elin Lindqvist", "org_mesb", "external_regulator_investigator"),
    "person_hale":       ("Dr. Sam Hale", "independent", "independent_consultant"),
    "person_voss":       ("Tom Voss", "org_kelvinbridge", "spokesperson"),
    "person_singh":      ("Raj Singh", "org_meridian", "technician"),
    "person_ahn":        ("Bo Ahn", "org_meridian", "technician"),
    "person_ferris":     ("Dana Ferris", "external", "harbor_pilot_bystander"),
    "automated_scada":   ("SCADA Automated Monitoring System", "org_meridian", "automated_detector"),
    "system_doc":        ("Status Reporting Pipeline", "org_meridian", "document_pipeline"),
}

CLAIM_META = {
"C01": dict(fact="F05-001", subfamily=["05.1","05.6"], subject_text="Turbine Unit T-4 March 14/16 trips", subject_entity_id="system_t4", predicate="caused_by", object="PCM ground fault (Hypothesis E)", canonical="The March 14/16 T-4 trips were caused by a ground fault in the Power Conversion Module."),
"C02": dict(fact="F05-002", subfamily=["05.1","05.6"], subject_text="Turbine Unit T-4 March 14/16 trips", subject_entity_id="system_t4", predicate="caused_by", object="bearing/vibration protective trip (Hypothesis M)", canonical="The March 14/16 T-4 trips were caused by mechanical bearing degradation triggering a vibration protective trip."),
"C03": dict(fact="F05-003", subfamily=["05.2"], subject_text="Vibration sensor VIB-4A", subject_entity_id="sensor_vib_4a", predicate="affected_by", object="biofouling", canonical="Biofouling on the VIB-4A sensor housing is causing spurious T-4 trips."),
"C04": dict(fact="F05-004", subfamily=["05.3"], subject_text="Turbine Unit T-4 trips", subject_entity_id="system_t4", predicate="caused_by", object="firmware v3.2 trip-threshold regression", canonical="A firmware v3.2 trip-threshold regression is causing the T-4 trips."),
"C05": dict(fact="F05-005", subfamily=["05.3"], subject_text="Main Shaft Bearing", subject_entity_id="subsystem_bearing", predicate="condition", object="worn/degraded", canonical="T-4's main shaft bearing is worn and degrading, causing the trips."),
"C06": dict(fact="F05-006", subfamily=["05.4","05.8"], subject_text="Turbine Unit T-4 trips", subject_entity_id="system_t4", predicate="caused_by", object="harmonic resonance between rotor and mooring line", canonical="Harmonic resonance between the rotor and mooring line is the root cause of the T-4 trips."),
"C07": dict(fact="F05-007", subfamily=["05.5"], subject_text="T-4 nacelle", subject_entity_id="system_t4", predicate="observed_as", object="sparks and smoke", canonical="Visible sparks and smoke near the T-4 nacelle on 2027-03-15 indicated an electrical fire."),
"C08": dict(fact="F05-008", subfamily=["control_D"], subject_text="Turbine Unit T-4 trips", subject_entity_id="system_t4", predicate="correlated_with", object="tidal phase", canonical="T-4 trips correlate with tidal phase."),
"C09": dict(fact="F05-009", subfamily=["control_A"], subject_text="Turbine Unit T-4", subject_entity_id="system_t4", predicate="rated_capacity", object="2.4 MW", canonical="Turbine Unit T-4's rated generator capacity is 2.4 MW."),
"C10": dict(fact="F05-010", subfamily=["control_B"], subject_text="T-4 main gearbox", subject_entity_id="subsystem_gearbox", predicate="observed_as", object="abnormal noise", canonical="T-4's main gearbox is producing abnormal noise."),
"C11": dict(fact="F05-011", subfamily=["control_C"], subject_text="Mooring Line Array", subject_entity_id="subsystem_mooring", predicate="tension_status", object="within specification", canonical="T-4's mooring line tension is within specification."),
"C12": dict(fact="F05-012", subfamily=["05.9"], subject_text="Power Conversion Module", subject_entity_id="subsystem_pcm", predicate="fault_status", object="no electrical fault at time of June 2 trip", canonical="No electrical fault occurred in the PCM at the moment of the June 2 trip."),
"C13": dict(fact="F05-013", subfamily=["05.9"], subject_text="Electrical protection system", subject_entity_id="subsystem_pcm", predicate="caused", object="June 2 shutdown", canonical="The electrical protection system caused the June 2 shutdown."),
"C14": dict(fact="F05-014", subfamily=["05.10a"], subject_text="Vibration sensors VIB-4A/VIB-4B", subject_entity_id="sensor_vib_4a", predicate="disagree_on", object="vibration amplitude", canonical="VIB-4A and VIB-4B disagree on vibration amplitude; VIB-4A has a known calibration drift."),
"C15": dict(fact="F05-015", subfamily=["05.10b"], subject_text="Temperature sensors TEMP-4A/TEMP-4B", subject_entity_id="sensor_temp_4a", predicate="disagree_on", object="bearing temperature", canonical="TEMP-4A and TEMP-4B disagree on bearing temperature; TEMP-4A had an undiscovered calibration drift."),
"C16": dict(fact="F05-016", subfamily=["05.10c"], subject_text="SCADA power reading vs manual reading", subject_entity_id="system_t4", predicate="disagree_on", object="power output at 2027-04-08 14:00", canonical="SCADA's hourly-average power reading and the technician's manual instantaneous reading appear to disagree on T-4's power output."),
"C17": dict(fact="F05-017", subfamily=["05.10d"], subject_text="Mooring tension readings", subject_entity_id="subsystem_mooring", predicate="disagree_on", object="tension value", canonical="Two mooring tension readings appear to disagree because they were taken at different tidal states."),
"C18": dict(fact="F05-018", subfamily=["05.10e"], subject_text="SCADA nodes A/B", subject_entity_id="system_t4", predicate="disagree_on", object="power output (~3%)", canonical="Redundant SCADA nodes A and B disagree on T-4 power output by about 3%, with no identified cause."),
"C19": dict(fact="F05-019", subfamily=["control_E"], subject_text="T-4 export line", subject_entity_id="system_t4", predicate="caused_by", object="grid switching transient", canonical="The 2027-04-02 anomalous power spike was caused by a Solway Grid switching transient."),
"C20": dict(fact="F05-020", subfamily=["05.6","control_F"], subject_text="T-4 export line", subject_entity_id="system_t4", predicate="caused_by", object="vessel wake or sensor noise (undetermined)", canonical="The cause of the 2027-05-19 two-second voltage dip is undetermined between a passing vessel's wake and sensor noise."),
"C21": dict(fact="F05-021", subfamily=["05.3","05.8"], subject_text="Kelvinbridge public statement", subject_entity_id="org_kelvinbridge", predicate="attributed_cause_to", object="site contractor installation error", canonical="Kelvinbridge's public statement attributes the T-4 trips to installation error by the site contractor."),
"C22": dict(fact="F05-022", subfamily=["rumor"], subject_text="Meridian Bay Array", subject_entity_id="facility_meridian_bay", predicate="rumored_status", object="full decommissioning by year end", canonical="Meridian Bay Array will be fully decommissioned by year end."),
"C23": dict(fact="F05-023", subfamily=["05.7"], subject_text="T-4 root cause investigation (RCA)", subject_entity_id="system_t4", predicate="resolution_status", object="bearing wear + intermittent PCM ground fault (combined)", canonical="T-4 root cause investigation: resolved (bearing wear) then reopened then resolved differently (combined bearing wear + intermittent PCM ground fault)."),
}

memories = []
mem_counter = 0
src_counters = {}

def next_mem_id():
    global mem_counter
    mem_counter += 1
    return f"e05m_{mem_counter:04d}"

def next_src_id(fact):
    src_counters[fact] = src_counters.get(fact, 0) + 1
    return f"src_{fact.lower()}_{src_counters[fact]}"

# beat = dict(event, obs, ing, mtype, stype, source_key, text, conf, evrole, stance,
#             distractor=False, evidence_root=None, deriv=None, contra=None, super_=None,
#             extra_tags=None, scope=None, truth_role=None)
def emit(claim_id, beat, chain):
    meta = CLAIM_META[claim_id]
    fact = meta["fact"]
    sid = next_src_id(fact)
    source_key = beat["source_key"]
    if source_key in PEOPLE:
        name, org, authority = PEOPLE[source_key]
    else:
        name, org, authority = source_key, "unknown", "unspecified"
    deriv_ids = beat.get("deriv_abs") or [chain[i] for i in beat.get("deriv", [])]
    contra_ids = beat.get("contra_abs") or [chain[i] for i in beat.get("contra", [])]
    super_ids = beat.get("super_abs") or [chain[i] for i in beat.get("super_", [])]
    tags = ["exp05"] + [f"family_{f}" for f in meta["subfamily"]] + [fact] + (beat.get("extra_tags") or [])
    mid = next_mem_id()
    rec = {
        "memory_id": mid,
        "experiment": EXP,
        "story_id": STORY,
        "event_time": beat["event"],
        "observation_time": beat["obs"],
        "ingestion_time": beat["ing"],
        "subject_text": meta["subject_text"],
        "subject_entity_id": meta["subject_entity_id"],
        "predicate": meta["predicate"],
        "object": meta["object"],
        "text": beat["text"],
        "memory_type": beat["mtype"],
        "truth_role": beat.get("truth_role") or "unresolved",
        "scope": beat.get("scope") or DEFAULT_SCOPE,
        "source_id": sid,
        "source_type": beat["stype"],
        "derived_from": deriv_ids,
        "supersedes": super_ids,
        "contradicts": contra_ids,
        "aliases_used": beat.get("aliases_used") or [],
        "tags": tags,
        "_oracle": {
            "fact_id": fact,
            "claim_id": claim_id,
            "adversarial_subfamily": meta["subfamily"],
            "canonical_claim": meta["canonical"],
            "is_distractor": beat.get("distractor", False),
            "confidence_label": beat["conf"],
            "evidence_role": beat["evrole"],
            "stance": beat["stance"],
            "source_name": name,
            "source_org": org,
            "source_authority": authority,
            "evidence_root": beat.get("evidence_root"),
            "evidence_id": f"E{fact.split('-')[1]}_{len(chain)+1}",
        },
    }
    memories.append(rec)
    chain.append(mid)
    return mid

def run_claim(claim_id, beats):
    chain = []
    for b in beats:
        emit(claim_id, b, chain)
    return chain

# ---------------------------------------------------------------------------
# Beat definitions per claim
# ---------------------------------------------------------------------------
ALL_CHAINS = {}

# C01 / C02 -- balanced unresolved contention (05.1 / 05.6)
ALL_CHAINS["C01"] = run_claim("C01", [
    dict(event="2027-03-14", obs="2027-03-14", ing="2027-03-15", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_pcm_leakage_current_0314",
         text="SCADA fault log, 2027-03-14 trip: PCM ground-fault-current channel briefly exceeded its warning band (not the trip band) 40ms before the protective trip fired.",
         truth_role="unresolved"),
    dict(event="2027-03-16", obs="2027-03-16", ing="2027-03-17", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_pcm_leakage_current_0316",
         text="SCADA fault log, 2027-03-16 trip: same PCM ground-fault-current warning-band excursion pattern recorded 55ms before trip.",
         truth_role="unresolved"),
    dict(event="2027-03-19", obs="2027-03-19", ing="2027-03-19", mtype="technical_note", stype="technical_note",
         source_key="person_park", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_park_pcm_review_0319",
         text="Grace Park, electrical review note: the ground-fault-current excursions preceding both March trips are consistent with an intermittent insulation fault inside the PCM; recommend megger test.",
         truth_role="unresolved"),
    dict(event="2027-03-21", obs="2027-03-21", ing="2027-03-22", mtype="technical_note", stype="technical_note",
         source_key="person_park", conf="disputed", evrole="independent_primary", stance="neutral_observation",
         evidence_root="root_megger_test_0321",
         text="Megger insulation-resistance test on the PCM, 2027-03-21: results within normal range, no insulation breakdown detected at time of test. Does not rule out an intermittent fault that clears before testing.",
         truth_role="unresolved"),
    dict(event="2027-04-05", obs="2027-04-05", ing="2027-04-06", mtype="meeting_summary", stype="meeting_summary",
         source_key="person_reyes", conf="probable", evrole="derivative_copy", stance="supports", deriv=[2],
         text="Meeting summary, 2027-04-05: team leans toward the electrical explanation for the March trips being 'probably correct,' pending further data.",
         truth_role="unresolved"),
    dict(event="2027-08-01", obs="2027-08-01", ing="2027-08-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_lindqvist", conf="unresolved", evrole="synthesis", stance="neutral_observation",
         text="MESB final report, 2027-08-01: the March 14/16 trips cannot be retroactively attributed to either the electrical or mechanical hypothesis. The onboard event recorder for that period has a data gap that was never filled; no further testing is planned. Status: permanently underdetermined for this specific episode.",
         truth_role="unresolved", extra_tags=["final_disposition"]),
])

ALL_CHAINS["C02"] = run_claim("C02", [
    dict(event="2027-03-18", obs="2027-03-18", ing="2027-03-18", mtype="technical_note", stype="handwritten_log",
         source_key="person_nandy", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_nandy_temp_drift_0318",
         text="Priya Nandy, shift log: bearing temperature on both TEMP-4A and TEMP-4B crept up steadily for about six hours before each trip, then reset after the trip. Could be a bearing issue rather than electrical.",
         truth_role="unresolved"),
    dict(event="2027-03-14", obs="2027-03-14", ing="2027-03-15", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_vib_amplitude_climb_0314",
         text="SCADA vibration log, 2027-03-14: VIB-4B amplitude (the sensor without a known calibration issue) climbed gradually in the hours before the trip, consistent with escalating mechanical imbalance.",
         truth_role="unresolved"),
    dict(event="2027-04-05", obs="2027-04-05", ing="2027-04-06", mtype="meeting_summary", stype="meeting_summary",
         source_key="person_reyes", conf="uncertain", evrole="derivative_copy", stance="neutral_observation", deriv=[0,1],
         text="Meeting summary, 2027-04-05: Nandy's bearing-drift observation is noted but deprioritized relative to the electrical hypothesis; not yet formally investigated.",
         truth_role="unresolved"),
    dict(event="2027-08-01", obs="2027-08-01", ing="2027-08-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_lindqvist", conf="unresolved", evrole="synthesis", stance="neutral_observation",
         text="MESB final report, 2027-08-01: although bearing wear was later confirmed as a real, independent problem (see F05-005), the report explicitly declines to say the March 14/16 trips specifically were caused by it, given the same unresolved data-recorder gap noted for the electrical hypothesis.",
         truth_role="unresolved", extra_tags=["final_disposition"]),
])

# C03 -- majority-wrong / minority-right (05.2)
c03_beats = [
    dict(event="2027-03-20", obs="2027-03-20", ing="2027-03-20", mtype="technical_note", stype="technical_note",
         source_key="person_singh", conf="possible", evrole="derivative_copy", stance="supports",
         evidence_root="root_misread_log_0320",
         text="Raj Singh, technician log: noted 'VIB-4A housing looks like it might have some marine growth, worth a look.' Not independently verified at time of writing.",
         truth_role="unresolved"),
]
paraphrases = [
    ("2027-03-22","status_summary","person_reyes","Status summary, 2027-03-22: working theory is biofouling on VIB-4A causing spurious trip signals."),
    ("2027-03-24","chat_message","person_reyes","Chat: 'heads up, looks like it's the usual biofouling thing on 4A again.'"),
    ("2027-03-27","status_summary","person_reyes","Status summary, 2027-03-27: biofouling on VIB-4A remains the leading explanation for T-4 trips."),
    ("2027-03-30","technical_note","system_doc","Weekly technical digest: VIB-4A biofouling flagged as probable trip cause (carried over from prior week)."),
    ("2027-04-03","chat_message","person_reyes","Chat: reminder to dive team — 4A biofouling still suspected, please prioritize cleaning next visit."),
    ("2027-04-08","status_summary","person_reyes","Status summary, 2027-04-08: no change; biofouling on VIB-4A still cited as probable cause."),
    ("2027-04-14","executive_summary","system_doc","Executive summary, week of 04-14: sensor biofouling (VIB-4A) identified as probable contributor to T-4 anomalies."),
    ("2027-04-21","status_summary","person_reyes","Status summary, 2027-04-21: biofouling theory unchanged; dive inspection still pending scheduling."),
    ("2027-04-28","chat_message","person_reyes","Chat: 'still waiting on the dive team for the 4A biofouling check.'"),
    ("2027-04-30","technical_note","system_doc","Weekly technical digest: biofouling (VIB-4A) still listed as probable cause, tenth consecutive week."),
]
for dt, mtype, key, text in paraphrases:
    c03_beats.append(dict(event="2027-03-20", obs=dt, ing=dt, mtype=mtype, stype=mtype,
        source_key=key, conf="probable", evrole="derivative_copy", stance="supports", deriv=[0], text=text,
        truth_role="unresolved"))
c03_beats += [
    dict(event="2027-05-01", obs="2027-05-01", ing="2027-05-02", mtype="inspection_report", stype="dive_inspection_report",
         source_key="person_ahn", conf="unlikely", evrole="independent_primary", stance="contradicts",
         evidence_root="root_dive_inspection_0501",
         text="Scheduled dive inspection, 2027-05-01: VIB-4A sensor housing found clean, no marine growth present. Contradicts the biofouling theory.",
         truth_role="unresolved", contra=[1]),
    dict(event="2027-05-10", obs="2027-05-10", ing="2027-05-11", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="disproven", evrole="independent_primary", stance="contradicts",
         evidence_root="root_independent_accelerometer_0510",
         text="Independently-mounted accelerometer (temporary rig, different location from VIB-4A) shows T-4 trip events uncorrelated with any biofouling-consistent signal pattern.",
         truth_role="unresolved", contra=[1]),
    dict(event="2027-05-15", obs="2027-05-15", ing="2027-05-16", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="disproven", evrole="synthesis", stance="contradicts",
         text="Status summary, 2027-05-15: biofouling theory formally retired. Two independent observations (clean dive inspection; independent accelerometer) outweigh the ten-week chain of repeated status-summary language, which all traced back to one unverified 2027-03-20 note.",
         truth_role="corrected", super_=list(range(1,11))),
]
ALL_CHAINS["C03"] = run_claim("C03", c03_beats)

# C04 / C05 -- authority inversion (05.3)
ALL_CHAINS["C04"] = run_claim("C04", [
    dict(event="2027-03-25", obs="2027-03-25", ing="2027-03-25", mtype="authoritative_record", stype="manufacturer_assessment",
         source_key="person_okafor", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_okafor_firmware_0325",
         text="Dr. Adaeze Okafor (Kelvinbridge, senior reliability engineer), preliminary assessment: telemetry pattern is consistent with a known firmware v3.2 trip-threshold regression affecting several fielded units. Recommend rollback to v3.1.",
         truth_role="unresolved"),
    dict(event="2027-03-26", obs="2027-03-26", ing="2027-03-27", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="probable", evrole="derivative_copy", stance="supports", deriv=[0],
         text="Status summary, 2027-03-26: per Kelvinbridge's senior reliability engineer, firmware v3.2 is the probable cause. Rollback scheduled.",
         truth_role="unresolved"),
    dict(event="2027-04-01", obs="2027-04-01", ing="2027-04-02", mtype="technical_note", stype="technical_note",
         source_key="person_costa", conf="probable", evrole="derivative_copy", stance="supports", deriv=[0],
         text="Firmware rolled back to v3.1 on all T-series units, 2027-04-01, per Kelvinbridge recommendation.",
         truth_role="unresolved"),
    dict(event="2027-06-02", obs="2027-06-02", ing="2027-06-02", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unlikely", evrole="independent_primary", stance="contradicts",
         evidence_root="root_recurrence_on_v31_0602",
         text="T-4 trip recurs 2027-06-02, over two months after the firmware rollback to v3.1. Firmware regression cannot explain a trip on a version that never had the flagged regression.",
         truth_role="unresolved", contra=[0]),
    dict(event="2027-07-01", obs="2027-07-01", ing="2027-07-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_hale", conf="disproven", evrole="synthesis", stance="contradicts",
         text="Independent consultant finding, 2027-07-01: firmware v3.2 formally ruled out. The June 2 recurrence on v3.1 is inconsistent with the firmware hypothesis regardless of its plausibility at the time it was proposed by Kelvinbridge's senior engineer.",
         truth_role="corrected", super_=[0,1]),
])

ALL_CHAINS["C05"] = run_claim("C05", [
    dict(event="2027-03-18", obs="2027-03-18", ing="2027-03-18", mtype="technical_note", stype="handwritten_log",
         source_key="person_nandy", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_nandy_temp_drift_0318b",
         text="Priya Nandy, shift log: repeating the bearing-temperature-drift observation from the T-4 trip log; requesting this be checked against bearing spec before ruling anything out.",
         truth_role="unresolved"),
    dict(event="2027-04-09", obs="2027-04-09", ing="2027-04-09", mtype="technical_note", stype="technical_note",
         source_key="person_nandy", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_nandy_vibration_signature_0409",
         text="Priya Nandy, follow-up note: cross-checked TEMP-4B trend against VIB-4B trend across all three trips so far; both show the same slow-climb-then-reset pattern. Requesting a bearing inspection be added to the RCA scope.",
         truth_role="unresolved"),
    dict(event="2027-04-10", obs="2027-04-10", ing="2027-04-10", mtype="investigation_report", stype="rca_report",
         source_key="person_reyes", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_bearing_inspection_0410",
         text="RCA report, 2027-04-10: bearing inspection (prompted by Nandy's 04-09 note) finds measurable wear on the main shaft bearing consistent with the temperature/vibration drift pattern. Root cause: bearing wear. Replacement scheduled.",
         truth_role="globally_true", deriv=[0,1]),
    dict(event="2027-04-12", obs="2027-04-12", ing="2027-04-12", mtype="technical_note", stype="maintenance_log",
         source_key="person_ahn", conf="confirmed", evrole="derivative_copy", stance="supports", deriv=[2],
         text="Maintenance log, 2027-04-12: main shaft bearing replaced on T-4, per 2027-04-10 RCA finding.",
         truth_role="globally_true"),
    dict(event="2027-06-20", obs="2027-06-20", ing="2027-06-21", mtype="inspection_report", stype="teardown_report",
         source_key="person_hale", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_teardown_0620",
         text="Teardown report, 2027-06-20 (post-recurrence): confirms the April bearing-wear finding was correct as far as it went; the original bearing showed genuine wear consistent with Nandy's temperature/vibration observations. It was simply not the whole story (see F05-023).",
         truth_role="globally_true", deriv=[2]),
])

# C06 -- confidence evolution + laundering (05.4 / 05.8)
ALL_CHAINS["C06"] = run_claim("C06", [
    dict(event="2027-04-01", obs="2027-04-01", ing="2027-04-01", mtype="informal_note", stype="whiteboard_note",
         source_key="person_costa", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_whiteboard_0401",
         text="Whiteboard note (photographed for the record), 2027-04-01: 'maybe harmonic resonance btwn rotor + mooring line? need to check w/ Hale or someone.' No calculation or test attached.",
         truth_role="unresolved"),
    dict(event="2027-04-01", obs="2027-04-05", ing="2027-04-06", mtype="meeting_summary", stype="meeting_summary",
         source_key="person_reyes", conf="probable", evrole="derivative_copy", stance="supports", deriv=[0],
         text="Meeting summary, 2027-04-05: harmonic resonance between rotor and mooring line raised as a likely contributing factor to the trips. (No new data since the 04-01 whiteboard note.)",
         truth_role="unresolved"),
    dict(event="2027-04-01", obs="2027-04-14", ing="2027-04-14", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="official_working_theory", evrole="derivative_copy", stance="supports", deriv=[1],
         text="Status summary, 2027-04-14: harmonic resonance identified as a contributing factor to T-4 trips. (Carried forward from the 04-05 meeting summary; no additional evidence gathered.)",
         truth_role="unresolved"),
    dict(event="2027-04-01", obs="2027-04-20", ing="2027-04-20", mtype="executive_summary", stype="executive_summary",
         source_key="system_doc", conf="official_working_theory", evrole="derivative_copy", stance="supports", deriv=[2],
         text="Executive summary, 2027-04-20: root cause of T-4 anomalies is harmonic resonance in the mooring-rotor interaction. (No new evidence between this and the 04-01 whiteboard speculation; confidence language escalated purely through document genre.)",
         truth_role="overgeneralized", extra_tags=["laundering_peak"]),
    dict(event="2027-06-10", obs="2027-06-10", ing="2027-06-11", mtype="technical_note", stype="engineering_analysis",
         source_key="person_hale", conf="disputed", evrole="independent_primary", stance="contradicts",
         evidence_root="root_hale_modal_analysis_0610",
         text="Dr. Sam Hale, modal analysis, 2027-06-10: rotor and mooring natural frequencies are separated by a wide enough margin that sustained harmonic resonance is unlikely to explain the trip pattern, though a transient coupling under specific sea states cannot be fully excluded with current data.",
         truth_role="unresolved"),
    dict(event="2027-07-01", obs="2027-07-01", ing="2027-07-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_lindqvist", conf="unlikely", evrole="synthesis", stance="contradicts",
         text="MESB combined finding, 2027-07-01: harmonic resonance downgraded from 'official working theory' to 'unlikely, not excluded.' It is not formally disproven the way firmware or biofouling were -- it simply never had supporting evidence beyond the original unverified whiteboard speculation, and Hale's analysis makes it an unlikely primary contributor.",
         truth_role="unresolved", super_=[3]),
])

# C07 -- evidence-quality inversion (05.5)
ALL_CHAINS["C07"] = run_claim("C07", [
    dict(event="2027-03-15", obs="2027-03-15", ing="2027-03-15", mtype="eyewitness_account", stype="visitor_report",
         source_key="person_ferris", conf="unlikely", evrole="independent_primary", stance="contradicts",
         evidence_root="root_ferris_sighting_0315",
         text="Dana Ferris (harbor pilot, passing by boat), account taken 2027-03-15: 'I saw sparks and what looked like smoke coming off the turbine housing near the top, really vivid, lasted a few seconds.' Vivid and detailed, but Ferris was roughly 400m away and had no direct line of sight to the nacelle interior.",
         truth_role="unresolved"),
    dict(event="2027-03-15", obs="2027-03-15", ing="2027-03-16", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_temp_anomaly_0315",
         text="SCADA log, 2027-03-15, 14:32: single bearing-temperature sensor reading 2.1C above trend for one polling interval, then back to normal. Brief, unremarkable-looking entry easy to overlook in the log.",
         truth_role="unresolved"),
    dict(event="2027-03-17", obs="2027-03-17", ing="2027-03-18", mtype="technical_note", stype="technical_note",
         source_key="person_park", conf="unlikely", evrole="independent_primary", stance="contradicts",
         evidence_root="root_glare_reconstruction_0317",
         text="Grace Park, follow-up on the 03-15 sighting: weather log shows bright low-angle sun and light rain at the reported time; wet nacelle housing at that sun angle is a known glare source from the harbor approach. No corresponding electrical event in the SCADA log at 03-15's reported sighting time. Most likely explanation: sun glare on wet housing, not sparks.",
         truth_role="unresolved", contra=[0]),
    dict(event="2027-06-20", obs="2027-06-20", ing="2027-06-21", mtype="inspection_report", stype="teardown_report",
         source_key="person_hale", conf="probable", evrole="independent_primary", stance="supports",
         text="Teardown report, 2027-06-20: the brief 03-15 temperature anomaly is consistent with an early, transient instance of the intermittent PCM ground fault later confirmed in July -- the boring one-line sensor entry turned out to be more diagnostically useful than the vivid eyewitness account.",
         truth_role="globally_true", deriv=[1]),
])

# C08 -- Control D: minority and wrong
c08_beats = [
    dict(event="2027-04-01", obs="2027-04-15", ing="2027-04-16", mtype="informal_note", stype="chat_message",
         source_key="person_singh", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_singh_tidal_hunch_0415",
         text="Raj Singh, chat message: 'not sure if it means anything but it feels like the trips happen more around spring tides?'",
         truth_role="unresolved"),
]
for i,(dt) in enumerate(["2027-03-14","2027-03-16","2027-04-02","2027-05-19","2027-06-02"]):
    c08_beats.append(dict(event=dt, obs=dt, ing=dt, mtype="sensor_log", stype="sensor_log",
        source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
        evidence_root=f"root_trip_timestamp_{i}",
        text=f"SCADA trip-event timestamp, {dt}, logged alongside contemporaneous tidal-phase reading for later statistical review.",
        truth_role="unresolved"))
c08_beats.append(
    dict(event="2027-07-10", obs="2027-07-10", ing="2027-07-10", mtype="statistical_analysis", stype="statistical_analysis",
         source_key="person_hale", conf="disproven", evrole="synthesis", stance="contradicts",
         text="Statistical review, 2027-07-10: all six T-4 trip timestamps plotted against tidal phase over the full investigation period show no significant correlation (p=0.71, n=6). Singh's hunch does not hold up; T-4 trips do not correlate with tidal phase.",
         truth_role="false", contra=[0]))
ALL_CHAINS["C08"] = run_claim("C08", c08_beats)

# C09 -- Control A: clear consensus
ALL_CHAINS["C09"] = run_claim("C09", [
    dict(event="2026-11-01", obs="2026-11-01", ing="2026-11-02", mtype="authoritative_record", stype="nameplate_spec",
         source_key="system_doc", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_nameplate", text="T-4 nameplate data sheet: rated generator capacity 2.4 MW.",
         truth_role="globally_true"),
    dict(event="2026-11-01", obs="2026-11-05", ing="2026-11-06", mtype="authoritative_record", stype="manufacturer_spec",
         source_key="person_okafor", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_kelvinbridge_spec", text="Kelvinbridge factory acceptance test report: T-series unit T-4 rated at 2.4 MW, verified at commissioning.",
         truth_role="globally_true"),
    dict(event="2026-11-01", obs="2026-12-01", ing="2026-12-02", mtype="authoritative_record", stype="commissioning_report",
         source_key="person_lindqvist", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_mesb_commissioning", text="MESB commissioning sign-off: confirms T-4 rated capacity of 2.4 MW independently verified against grid interconnection filings.",
         truth_role="globally_true"),
])

# C10 -- Control B: repetition with independence
ALL_CHAINS["C10"] = run_claim("C10", [
    dict(event="2027-05-25", obs="2027-05-25", ing="2027-05-25", mtype="technical_note", stype="handwritten_log",
         source_key="person_singh", conf="possible", evrole="independent_primary", stance="supports",
         evidence_root="root_singh_gearbox_noise", text="Raj Singh, night-shift log, 2027-05-25: unusual grinding noise from T-4 gearbox during routine walk-around, roughly 23:10.",
         truth_role="unresolved"),
    dict(event="2027-05-26", obs="2027-05-26", ing="2027-05-26", mtype="technical_note", stype="handwritten_log",
         source_key="person_ahn", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_ahn_gearbox_noise", text="Bo Ahn, day-shift log, 2027-05-26: independently noticed the same grinding noise from T-4 gearbox before reading Singh's note; timed it to roughly 09:40.",
         truth_role="unresolved"),
    dict(event="2027-05-27", obs="2027-05-27", ing="2027-05-27", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_gearbox_acoustic_sensor", text="Acoustic monitoring sensor on the gearbox housing (independent of both technicians' direct hearing) flags an above-baseline high-frequency component starting 2027-05-25.",
         truth_role="unresolved"),
    dict(event="2027-05-28", obs="2027-05-28", ing="2027-05-29", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="confirmed", evrole="synthesis", stance="supports",
         text="Status summary, 2027-05-28: gearbox inspection scheduled with elevated priority. Confidence raised appropriately here -- two technicians on different shifts and an independent acoustic sensor all corroborate the same finding without having copied from each other.",
         truth_role="globally_true", deriv=[0,1,2]),
])

# C11 -- Control C: authoritative and correct
ALL_CHAINS["C11"] = run_claim("C11", [
    dict(event="2027-06-08", obs="2027-06-08", ing="2027-06-08", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="probable", evrole="independent_primary", stance="supports",
         evidence_root="root_mooring_load_cell", text="Mooring load-cell telemetry, 2027-06-08: tension readings across all four T-4 mooring lines within the specified 850-1150 kN operating band.",
         truth_role="unresolved"),
    dict(event="2027-06-12", obs="2027-06-12", ing="2027-06-13", mtype="authoritative_record", stype="investigator_finding",
         source_key="person_lindqvist", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_lindqvist_mooring_review", text="Elin Lindqvist (MESB lead investigator), formal finding, 2027-06-12: independently reviewed mooring tension telemetry and physical line inspection; confirms tension within specification. Mooring integrity is not a contributing factor to the T-4 trips.",
         truth_role="globally_true", deriv=[0]),
])

# C12 / C13 -- expert disagreement, different scopes (05.9)
ALL_CHAINS["C12"] = run_claim("C12", [
    dict(event="2027-06-15", obs="2027-06-15", ing="2027-06-15", mtype="technical_note", stype="engineering_statement",
         source_key="person_park", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_park_no_fault_0615",
         text="Grace Park, electrical engineer: 'No electrical fault occurred in the PCM at the moment of the June 2 trip.' Statement scoped narrowly to the PCM's internal electrical state at the instant of the trip, based on component-level diagnostic readout.",
         truth_role="globally_true"),
])
ALL_CHAINS["C13"] = run_claim("C13", [
    dict(event="2027-06-16", obs="2027-06-16", ing="2027-06-16", mtype="technical_note", stype="engineering_statement",
         source_key="person_costa", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_costa_protection_caused_0616",
         text="Jordan Costa, systems engineer: 'The electrical protection system caused the June 2 shutdown.' Statement scoped to the systems-level trigger chain: the protection relay tripped the breaker, which is what actually stopped the turbine, regardless of whether the underlying PCM component itself was faulted at that instant.",
         truth_role="globally_true"),
    dict(event="2027-06-17", obs="2027-06-17", ing="2027-06-18", mtype="meeting_summary", stype="meeting_summary",
         source_key="person_reyes", conf="confirmed", evrole="synthesis", stance="neutral_observation",
         text="Meeting summary, 2027-06-17: reconciled Park's and Costa's 06-15/06-16 statements. Both are correct and are not in tension: Park is describing the PCM component's electrical state at the trip instant (no internal fault detected then); Costa is describing the protection system's trigger action (which is what physically caused the shutdown, prompted by threshold logic upstream of the momentary component state Park examined). Do not collapse these into a single contradictory claim.",
         truth_role="globally_true"),
])

# C14 -- 05.10a known calibration problem
ALL_CHAINS["C14"] = run_claim("C14", [
    dict(event="2027-04-20", obs="2027-04-20", ing="2027-04-21", mtype="maintenance_log", stype="maintenance_log",
         source_key="person_ahn", conf="confirmed", evrole="independent_primary", stance="neutral_observation",
         evidence_root="root_vib4a_calibration_log_0420",
         text="Maintenance log, 2027-04-20: VIB-4A calibration check shows a documented +18% gain drift versus reference; flagged for recalibration at next scheduled maintenance window.",
         truth_role="globally_true"),
    dict(event="2027-06-05", obs="2027-06-05", ing="2027-06-05", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA log, 2027-06-05: VIB-4A reads 22.4 mm/s RMS while VIB-4B (same shaft, different mount) reads 18.6 mm/s RMS for the same event window.",
         truth_role="unresolved"),
    dict(event="2027-06-22", obs="2027-06-22", ing="2027-06-22", mtype="technical_note", stype="technical_note",
         source_key="person_park", conf="confirmed", evrole="synthesis", stance="supports",
         text="Grace Park, 2027-06-22: cross-referenced the 06-05 VIB-4A/4B discrepancy against the 04-20 maintenance log. VIB-4A's known +18% gain drift fully accounts for the gap; VIB-4B is the reliable reading. This is a known, already-documented calibration problem, not a genuine sensor mystery.",
         truth_role="corrected", deriv=[0,1]),
])

# C15 -- 05.10b unknown-until-teardown calibration problem
ALL_CHAINS["C15"] = run_claim("C15", [
    dict(event="2027-05-30", obs="2027-05-30", ing="2027-05-30", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA log, 2027-05-30: TEMP-4A reads 61.2C while TEMP-4B reads 57.8C for the same bearing at the same instant. No known calibration issue on record for either sensor at this time.",
         truth_role="unresolved"),
    dict(event="2027-06-08", obs="2027-06-08", ing="2027-06-08", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="uncertain", evrole="derivative_copy", stance="neutral_observation", deriv=[0],
         text="Status summary, 2027-06-08: TEMP-4A/4B discrepancy still open; unclear at this time which reading (if either) is more trustworthy. Treating both as provisionally uncertain pending inspection.",
         truth_role="unresolved"),
    dict(event="2027-06-20", obs="2027-06-20", ing="2027-06-21", mtype="inspection_report", stype="teardown_report",
         source_key="person_hale", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_teardown_temp4a_drift_0620",
         text="Teardown report, 2027-06-20: TEMP-4A found to have a corroded lead connection causing a resistance-based calibration drift, undiscoverable without physical inspection. TEMP-4B was accurate throughout. This calibration problem was genuinely unknown before teardown -- the 05-30 through 06-08 uncertainty was appropriate given the information available at the time, not a failure to notice something knowable.",
         truth_role="corrected", deriv=[0]),
])

# C16 -- 05.10c different sampling windows
ALL_CHAINS["C16"] = run_claim("C16", [
    dict(event="2027-04-08", obs="2027-04-08", ing="2027-04-08", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA hourly-average log, 2027-04-08 14:00 window: T-4 average power output 2.05 MW for the hour ending 14:00.",
         truth_role="unresolved"),
    dict(event="2027-04-08", obs="2027-04-08", ing="2027-04-08", mtype="technical_note", stype="handwritten_log",
         source_key="person_singh", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="Raj Singh, manual reading, 2027-04-08 14:00 exactly: T-4 power output 2.38 MW on the local gauge, a single instantaneous reading.",
         truth_role="unresolved"),
    dict(event="2027-04-09", obs="2027-04-09", ing="2027-04-09", mtype="technical_note", stype="technical_note",
         source_key="person_costa", conf="confirmed", evrole="synthesis", stance="supports",
         text="Jordan Costa, 2027-04-09: the apparent SCADA-vs-manual discrepancy (2.05 MW vs 2.38 MW) is explained by sampling window, not sensor error. SCADA reports the hourly average across a tidal current ramp-up; Singh's manual reading was a single instant near the hour's peak. Both readings are individually correct for what they measure.",
         truth_role="corrected", deriv=[0,1]),
])

# C17 -- 05.10d different times (tidal state)
ALL_CHAINS["C17"] = run_claim("C17", [
    dict(event="2027-06-08", obs="2027-06-08", ing="2027-06-08", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="Mooring load-cell reading, 2027-06-08, 03:00 (near slack tide): 890 kN average across all four lines.",
         truth_role="unresolved"),
    dict(event="2027-06-08", obs="2027-06-08", ing="2027-06-08", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="Mooring load-cell reading, 2027-06-08, 09:00 (near peak flood current): 1120 kN average across all four lines.",
         truth_role="unresolved"),
    dict(event="2027-06-09", obs="2027-06-09", ing="2027-06-09", mtype="technical_note", stype="technical_note",
         source_key="person_park", conf="confirmed", evrole="synthesis", stance="supports",
         text="Grace Park, 2027-06-09: the 890 kN vs 1120 kN readings are not in tension -- mooring tension is known to vary with current speed across the tidal cycle, and both readings fall within the 850-1150 kN spec band for their respective tidal states. This is a different-time artifact, not a sensor disagreement.",
         truth_role="corrected", deriv=[0,1]),
])

# C18 -- 05.10e genuinely unexplained
ALL_CHAINS["C18"] = run_claim("C18", [
    dict(event="2027-06-01", obs="2027-06-01", ing="2027-06-01", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA node A power-output telemetry, 2027-06-01: T-4 output 1.92 MW at 12:00.",
         truth_role="unresolved"),
    dict(event="2027-06-01", obs="2027-06-01", ing="2027-06-01", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA node B power-output telemetry (redundant node, same measurement point), 2027-06-01: T-4 output 1.98 MW at 12:00 -- roughly 3% higher than node A for the same instant.",
         truth_role="unresolved"),
    dict(event="2027-06-15", obs="2027-06-15", ing="2027-06-16", mtype="technical_note", stype="technical_note",
         source_key="person_costa", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="Jordan Costa, 2027-06-15: investigated the node A/B ~3% discrepancy. Ruled out sampling-window and calibration-log explanations (both nodes poll synchronously and neither has a logged calibration issue). Discrepancy persists across multiple dates and remains unexplained. Recommend continued monitoring rather than guessing at a cause.",
         truth_role="unresolved", contra=[0,1]),
    dict(event="2027-08-01", obs="2027-08-01", ing="2027-08-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_lindqvist", conf="unresolved", evrole="synthesis", stance="neutral_observation",
         text="MESB final report, 2027-08-01: the SCADA node A/B power-output discrepancy remains genuinely unexplained. Unlike the VIB-4A and TEMP-4A cases, no calibration record, sampling-window artifact, or physical inspection finding accounts for it. Recorded here as an open, unresolved measurement disagreement, not to be conflated with the resolved sensor cases.",
         truth_role="unresolved", extra_tags=["final_disposition"]),
])

# C19 -- Control E: uncertainty that later resolves
ALL_CHAINS["C19"] = run_claim("C19", [
    dict(event="2027-04-02", obs="2027-04-02", ing="2027-04-02", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA log, 2027-04-02, 16:47: brief anomalous power spike on T-4 export line, +40% for approximately 300ms, cause not identified at time of logging.",
         truth_role="unresolved"),
    dict(event="2027-04-03", obs="2027-04-03", ing="2027-04-03", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="uncertain", evrole="derivative_copy", stance="neutral_observation", deriv=[0],
         text="Status summary, 2027-04-03: cause of the 04-02 power spike is uncertain; several possibilities under consideration including grid-side and turbine-side origins.",
         truth_role="unresolved"),
    dict(event="2027-05-20", obs="2027-05-20", ing="2027-05-21", mtype="authoritative_record", stype="utility_log",
         source_key="system_doc", conf="confirmed", evrole="independent_primary", stance="supports",
         evidence_root="root_gridco_switching_log_0520",
         text="Solway Grid Connections switching log (obtained 2027-05-20): confirms a substation capacitor-bank switching event at 2027-04-02 16:47:03, matching the T-4 spike timing to within one second. Root cause: grid switching transient, not a turbine-side event.",
         truth_role="globally_true", deriv=[0]),
])

# C20 -- Control F: never resolves
ALL_CHAINS["C20"] = run_claim("C20", [
    dict(event="2027-05-19", obs="2027-05-19", ing="2027-05-19", mtype="sensor_log", stype="sensor_log",
         source_key="automated_scada", conf="unresolved", evrole="independent_primary", stance="neutral_observation",
         text="SCADA log, 2027-05-19, 21:03: two-second voltage dip on T-4's subsea export cable connector, -12% nominal, self-cleared. No corresponding turbine-side or grid-side event logged at that time.",
         truth_role="unresolved"),
    dict(event="2027-05-20", obs="2027-05-20", ing="2027-05-20", mtype="technical_note", stype="technical_note",
         source_key="person_park", conf="possible", evrole="independent_primary", stance="neutral_observation",
         text="Grace Park, 2027-05-20: harbor traffic log shows a supply vessel passing near the subsea cable route around 21:02-21:04. A vessel wake affecting the connector is plausible but not confirmed -- the connector has no strain gauge to test this directly.",
         truth_role="unresolved"),
    dict(event="2027-05-22", obs="2027-05-22", ing="2027-05-22", mtype="technical_note", stype="technical_note",
         source_key="person_costa", conf="possible", evrole="independent_primary", stance="neutral_observation",
         text="Jordan Costa, 2027-05-22: alternative explanation -- the dip's signature is also consistent with a transient sensor-noise event on the voltage monitoring channel itself, which has an unrelated, lower-severity noise history. No way to distinguish from the vessel-wake hypothesis with data currently collected.",
         truth_role="unresolved"),
    dict(event="2027-08-01", obs="2027-08-01", ing="2027-08-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_lindqvist", conf="unresolved", evrole="synthesis", stance="neutral_observation",
         text="MESB final report, 2027-08-01: the 05-19 voltage dip's cause remains undetermined between vessel-wake and sensor-noise explanations. Installing a strain gauge that could have distinguished the two was proposed in June but not funded within the investigation's scope; no decisive test was ever conducted. This is recorded as permanently unresolved, not merely unresolved-for-now.",
         truth_role="unresolved", extra_tags=["final_disposition"]),
])

# C21 -- authority/PR divergence (05.3 / 05.8)
ALL_CHAINS["C21"] = run_claim("C21", [
    dict(event="2027-06-20", obs="2027-06-20", ing="2027-06-20", mtype="technical_note", stype="internal_engineering_note",
         source_key="person_okafor", conf="unlikely", evrole="independent_primary", stance="contradicts",
         evidence_root="root_kelvinbridge_internal_0620",
         text="Dr. Adaeze Okafor, internal Kelvinbridge engineering note, 2027-06-20: teardown findings do not support an installation-error explanation; mounting torque and alignment records from commissioning are within spec. Internal assessment: bearing wear and PCM intermittent fault, not installation error.",
         truth_role="unresolved"),
    dict(event="2027-06-25", obs="2027-06-25", ing="2027-06-25", mtype="press_statement", stype="press_statement",
         source_key="person_voss", conf="official_working_theory", evrole="independent_primary", stance="supports",
         evidence_root="root_voss_public_statement_0625",
         text="Tom Voss (Kelvinbridge spokesperson), public statement, 2027-06-25: 'Our engineering review indicates the issues at Meridian Bay are most likely attributable to installation conditions at the site, which fall outside Kelvinbridge's scope of responsibility.'",
         truth_role="underspecified", contra=[0], extra_tags=["official_position"]),
    dict(event="2027-07-02", obs="2027-07-02", ing="2027-07-02", mtype="technical_note", stype="technical_note",
         source_key="person_reyes", conf="unlikely", evrole="synthesis", stance="contradicts",
         text="Meridian internal note, 2027-07-02: Kelvinbridge's 06-25 public statement is not consistent with Kelvinbridge's own 06-20 internal engineering note (which we received under the investigation-sharing agreement) or with the 07-01 MESB combined finding, neither of which identifies installation error as a contributor. The public statement is recorded here as an official position that diverges from the evidentiary record, not adopted as fact.",
         truth_role="unresolved", contra=[1]),
])

# C22 -- pure rumor, distractor
ALL_CHAINS["C22"] = run_claim("C22", [
    dict(event="2027-07-05", obs="2027-07-05", ing="2027-07-05", mtype="rumor", stype="dockside_rumor",
         source_key="person_ferris", conf="rumor", evrole="independent_primary", stance="neutral_observation",
         evidence_root="root_ferris_rumor_0705",
         text="Dana Ferris, dockside conversation relayed secondhand, 2027-07-05: 'heard the whole array's getting decommissioned by the end of the year because of all these problems.' No source given; not attributed to any Meridian, Kelvinbridge, or MESB record.",
         truth_role="unresolved", distractor=True),
    dict(event="2027-07-08", obs="2027-07-08", ing="2027-07-08", mtype="chat_message", stype="chat_message",
         source_key="person_singh", conf="rumor", evrole="derivative_copy", stance="neutral_observation", deriv=[0],
         text="Chat message, 2027-07-08: 'anyone else hearing the decommissioning rumor? no idea if it's real.'",
         truth_role="unresolved", distractor=True),
    dict(event="2027-07-15", obs="2027-07-15", ing="2027-07-15", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="unresolved", evrole="synthesis", stance="neutral_observation",
         text="Status summary, 2027-07-15: for the record, no decommissioning decision has been made or proposed at any level of Meridian Tidal Energy as of this date. The circulating rumor has no identified originating source within the investigation or company records.",
         truth_role="false", distractor=True, contra=[0,1]),
])

# C23 -- apparent resolution, reopening, resolved differently (05.7)
ALL_CHAINS["C23"] = run_claim("C23", [
    dict(event="2027-03-14", obs="2027-03-14", ing="2027-03-15", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="unresolved", evrole="synthesis", stance="neutral_observation",
         text="Status summary, 2027-03-14: T-4 trip cause under investigation. Status: open.",
         truth_role="unresolved"),
    dict(event="2027-04-10", obs="2027-04-10", ing="2027-04-10", mtype="investigation_report", stype="rca_report",
         source_key="person_reyes", conf="provisionally_resolved", evrole="synthesis", stance="supports",
         text="RCA report, 2027-04-10: root cause identified as bearing wear (see F05-005). Status: resolved. Bearing replacement scheduled.",
         truth_role="partially_true", deriv=[0]),
    dict(event="2027-06-02", obs="2027-06-02", ing="2027-06-02", mtype="status_summary", stype="status_summary",
         source_key="person_reyes", conf="reopened", evrole="synthesis", stance="neutral_observation",
         text="Status summary, 2027-06-02: T-4 trip recurs after bearing replacement. The April RCA's single-cause closure is reopened; investigation resumes with MESB involvement.",
         truth_role="unresolved", contra=[1]),
    dict(event="2027-07-01", obs="2027-07-01", ing="2027-07-01", mtype="investigation_report", stype="investigation_report",
         source_key="person_lindqvist", conf="resolved_differently", evrole="synthesis", stance="supports",
         text="MESB combined finding, 2027-07-01: root cause was not a single factor. Bearing wear (confirmed April, real and correctly identified) was a genuine contributor but incomplete as a full explanation; an intermittent PCM ground fault (confirmed via June teardown) was a second, independent contributor. Status: resolved, with a different and more complete finding than the April RCA. The April finding is not 'wrong' -- it correctly identified one real cause; it was incomplete, not false.",
         truth_role="corrected", super_=[1], deriv=[2]),
])

# ---------------------------------------------------------------------------
# Padding: additional independent/derivative beats on existing chains, to
# raise statistical weight on repetition-vs-independence and corroboration
# patterns (05.1-05.4, 05.10, Control B). Each beat still carries real
# adversarial content (varying source, date, independence root) rather than
# inert filler.
# ---------------------------------------------------------------------------
def emit_pad(claim_id, beats):
    chain = ALL_CHAINS[claim_id]
    for b in beats:
        emit(claim_id, b, chain)

def mk(dt, mtype, key, text, conf, evrole, stance, deriv_abs=None, contra_abs=None,
       evidence_root=None, distractor=False, truth_role="unresolved"):
    return dict(event=dt, obs=dt, ing=dt, mtype=mtype, stype=mtype, source_key=key, text=text,
                conf=conf, evrole=evrole, stance=stance, deriv_abs=deriv_abs, contra_abs=contra_abs,
                evidence_root=evidence_root, distractor=distractor, truth_role=truth_role)

c01_root = ALL_CHAINS["C01"][0]
emit_pad("C01", [
    mk("2027-03-24","technical_note","person_costa","Jordan Costa, independent review of the March PCM leakage-current traces: pattern is plausible for an intermittent insulation fault but the magnitude is close to the sensor's own noise floor, so this should be treated as weak-to-moderate evidence, not conclusive.","disputed","independent_primary","neutral_observation",evidence_root="root_costa_review_0324"),
    mk("2027-04-06","meeting_summary","person_reyes","Meeting summary, 2027-04-06: electrical hypothesis for March trips remains the working lean, but no decisive test has been run and the team explicitly notes the bearing hypothesis has not been ruled out.","probable","derivative_copy","supports",deriv_abs=[c01_root]),
])
c02_root = ALL_CHAINS["C02"][0]
emit_pad("C02", [
    mk("2027-03-23","technical_note","person_nandy","Priya Nandy, follow-up shift note: temperature drift pattern held on a third occasion (a near-trip event on 2027-03-23 that self-cleared before threshold). Requesting this be logged alongside the two confirmed trips.","probable","independent_primary","supports",evidence_root="root_nandy_near_trip_0323"),
    mk("2027-04-06","meeting_summary","person_reyes","Meeting summary, 2027-04-06: mechanical/bearing hypothesis for March trips remains plausible per Nandy's repeated observations, but has not been formally tested against the electrical hypothesis.","possible","derivative_copy","supports",deriv_abs=[c02_root]),
])

c04_root = ALL_CHAINS["C04"][0]
emit_pad("C04", [
    mk("2027-03-28","chat_message","person_reyes","Chat: 'Kelvinbridge's senior engineer is pretty confident it's the v3.2 firmware thing, rolling back this week.'","probable","derivative_copy","supports",deriv_abs=[c04_root]),
    mk("2027-04-02","status_summary","person_reyes","Status summary, 2027-04-02: firmware rollback complete across all T-series units per Kelvinbridge's recommendation; monitoring for recurrence.","probable","derivative_copy","supports",deriv_abs=[c04_root]),
    mk("2027-04-20","executive_summary","system_doc","Executive summary, 2027-04-20: T-4 trip issue considered addressed via firmware rollback per manufacturer guidance.","official_working_theory","derivative_copy","supports",deriv_abs=[c04_root]),
])
c05_root = ALL_CHAINS["C05"][2]  # RCA report beat
emit_pad("C05", [
    mk("2027-04-11","technical_note","person_park","Grace Park, cross-check note, 2027-04-11: bearing wear finding is consistent with the electrical team's own vibration data; no objection to closing on this cause for now.","confirmed","independent_primary","supports",evidence_root="root_park_crosscheck_0411"),
    mk("2027-06-21","technical_note","person_nandy","Priya Nandy, note after teardown, 2027-06-21: glad the April finding held up under teardown; still think the electrical side needs its own separate look given the June recurrence.","confirmed","independent_primary","supports",deriv_abs=[c05_root]),
])

c06_root = ALL_CHAINS["C06"][0]
emit_pad("C06", [
    mk("2027-04-16","chat_message","person_costa","Chat, 2027-04-16: 'has anyone actually run the resonance numbers or are we just repeating the whiteboard thing at this point?' (no reply on record)","possible","derivative_copy","neutral_observation",deriv_abs=[c06_root]),
    mk("2027-04-22","status_summary","person_reyes","Status summary, 2027-04-22: harmonic resonance theory reiterated per the 04-20 executive summary; treated as current understanding.","official_working_theory","derivative_copy","supports",deriv_abs=[c06_root]),
    mk("2027-05-01","status_summary","person_reyes","Status summary, 2027-05-01: harmonic resonance remains the recorded root cause pending the consultant's review (Hale engaged 06-10).","official_working_theory","derivative_copy","supports",deriv_abs=[c06_root]),
])

c07_root = ALL_CHAINS["C07"][0]
emit_pad("C07", [
    mk("2027-03-16","chat_message","person_reyes","Chat, 2027-03-16: 'got a report of sparks/smoke from a boater yesterday, anyone else see anything unusual near T-4?' No corroborating reports came in.","unlikely","derivative_copy","neutral_observation",deriv_abs=[c07_root]),
    mk("2027-03-18","status_summary","person_reyes","Status summary, 2027-03-18: unconfirmed spark/smoke sighting noted for completeness; no supporting instrumentation event found at the reported time.","unlikely","derivative_copy","neutral_observation",deriv_abs=[c07_root]),
])

c10_i, c10_j = ALL_CHAINS["C10"][0], ALL_CHAINS["C10"][1]
emit_pad("C10", [
    mk("2027-05-27","technical_note","person_reyes","Marcus Reyes, third independent confirmation, 2027-05-27: personally walked the site after reading both shift logs and confirms the grinding noise is audible and consistent with Singh's and Ahn's descriptions.","confirmed","independent_primary","supports",evidence_root="root_reyes_gearbox_confirm_0527"),
])

c11_root = ALL_CHAINS["C11"][1]
emit_pad("C11", [
    mk("2027-06-14","technical_note","person_hale","Dr. Sam Hale, independent mooring assessment, 2027-06-14: reviewed the same telemetry Lindqvist used plus an independent physical line inspection; concurs mooring tension is within spec and not a contributing factor.","confirmed","independent_primary","supports",deriv_abs=[c11_root]),
])

c12_root = ALL_CHAINS["C12"][0]
c13_root = ALL_CHAINS["C13"][0]
emit_pad("C12", [
    mk("2027-06-18","technical_note","person_hale","Dr. Sam Hale, independent review, 2027-06-18: confirms Park's PCM component-level diagnostic readout at the trip instant shows no internal electrical fault.","confirmed","independent_primary","supports",deriv_abs=[c12_root]),
])
emit_pad("C13", [
    mk("2027-06-19","technical_note","person_hale","Dr. Sam Hale, independent review, 2027-06-19: confirms the protection relay log shows the protection system's threshold logic triggered the June 2 breaker trip, consistent with Costa's systems-level statement.","confirmed","independent_primary","supports",deriv_abs=[c13_root]),
])

c14_a, c14_b = ALL_CHAINS["C14"][0], ALL_CHAINS["C14"][1]
emit_pad("C14", [
    mk("2027-06-10","sensor_log","automated_scada","SCADA log, 2027-06-10: VIB-4A reads 19.8 mm/s RMS, VIB-4B reads 16.4 mm/s RMS, same ~18-20% gap pattern as 06-05, consistent with the known VIB-4A drift.","unresolved","independent_primary","neutral_observation"),
    mk("2027-07-05","maintenance_log","person_ahn","Maintenance log, 2027-07-05: VIB-4A recalibrated per the 04-20 flag; post-recalibration readings now track VIB-4B within 2%.","confirmed","independent_primary","supports",deriv_abs=[c14_a]),
])
c15_a = ALL_CHAINS["C15"][0]
emit_pad("C15", [
    mk("2027-06-14","sensor_log","automated_scada","SCADA log, 2027-06-14: TEMP-4A/4B gap persists (60.9C vs 57.5C), still unexplained at this point in the timeline.","unresolved","independent_primary","neutral_observation",deriv_abs=[c15_a]),
])
c16_a = ALL_CHAINS["C16"][0]
emit_pad("C16", [
    mk("2027-04-15","sensor_log","automated_scada","SCADA hourly-average log, 2027-04-15 15:00 window: T-4 average power output 1.88 MW -- a second instance of the same sampling-window gap noted against a manual spot reading of 2.20 MW logged by Ahn at 15:00 exactly.","unresolved","independent_primary","neutral_observation",deriv_abs=[c16_a]),
])
c17_a = ALL_CHAINS["C17"][0]
emit_pad("C17", [
    mk("2027-06-22","sensor_log","automated_scada","Mooring load-cell reading, 2027-06-22, 04:00 (near slack tide): 905 kN -- second instance consistent with the 06-08 slack-tide reading, supporting the tidal-state explanation over a sensor-fault explanation.","confirmed","independent_primary","supports",deriv_abs=[c17_a]),
])
c18_a, c18_b = ALL_CHAINS["C18"][0], ALL_CHAINS["C18"][1]
emit_pad("C18", [
    mk("2027-06-08","sensor_log","automated_scada","SCADA node A telemetry, 2027-06-08: T-4 output 2.10 MW at 12:00.","unresolved","independent_primary","neutral_observation"),
    mk("2027-06-08","sensor_log","automated_scada","SCADA node B telemetry, 2027-06-08: T-4 output 2.16 MW at 12:00 -- same ~3% gap recurs, still unexplained.","unresolved","independent_primary","neutral_observation"),
])

c19_root = ALL_CHAINS["C19"][0]
emit_pad("C19", [
    mk("2027-04-10","technical_note","person_costa","Jordan Costa, 2027-04-10: checked T-4's own protection logic for the 04-02 spike; no turbine-side trigger recorded, consistent with (but not yet confirming) a grid-side origin.","uncertain","independent_primary","neutral_observation",deriv_abs=[c19_root]),
])
c20_root = ALL_CHAINS["C20"][0]
emit_pad("C20", [
    mk("2027-06-05","technical_note","person_costa","Jordan Costa, follow-up, 2027-06-05: proposed a strain gauge to distinguish vessel-wake from sensor-noise for the 05-19 dip; flagged as unfunded pending investigation prioritization.","possible","independent_primary","neutral_observation",deriv_abs=[c20_root]),
])

c21_a = ALL_CHAINS["C21"][0]
emit_pad("C21", [
    mk("2027-06-26","chat_message","person_park","Chat, 2027-06-26: 'Kelvinbridge's public statement doesn't match what Okafor told us internally. Flagging so we don't accidentally repeat it as fact.'","unlikely","derivative_copy","contradicts",deriv_abs=[a := ALL_CHAINS["C21"][1]], contra_abs=[a]),
])
c22_a = ALL_CHAINS["C22"][0]
emit_pad("C22", [
    mk("2027-07-10","chat_message","person_ahn","Chat, 2027-07-10: 'talked to Reyes, decommissioning rumor is not real, nothing planned.'","false","derivative_copy","contradicts",deriv_abs=[c22_a], contra_abs=[c22_a], distractor=True),
])
c23_root = ALL_CHAINS["C23"][1]
emit_pad("C23", [
    mk("2027-05-01","status_summary","person_reyes","Status summary, 2027-05-01: T-4 running normally since the April 12 bearing replacement; RCA remains closed at this point.","provisionally_resolved","derivative_copy","supports",deriv_abs=[c23_root]),
    mk("2027-06-25","meeting_summary","person_lindqvist","MESB meeting summary, 2027-06-25: combined-cause hypothesis (bearing wear + intermittent PCM fault) discussed as the likely direction for the final finding, pending teardown confirmation already in hand from 06-20.","disputed","synthesis","neutral_observation"),
])

# --- Secondary arc: second majority-wrong case (05.2) -----------------------
CLAIM_META["C24"] = dict(fact="F05-024", subfamily=["05.2"], subject_text="T-4 grid-tie transformer", subject_entity_id="subsystem_pcm", predicate="condition", object="overheating", canonical="T-4's grid-tie transformer is overheating and contributing to the trips.")
c24_beats = [
    mk("2027-04-18","technical_note","person_singh","Raj Singh, note, 2027-04-18: transformer housing felt warm to the touch during a walk-around; noted as a possible overheating issue.","possible","independent_primary","supports",evidence_root="root_singh_transformer_touch_0418"),
]
for i,(dt,key,text) in enumerate([
    ("2027-04-20","person_reyes","Status summary, 2027-04-20: possible transformer overheating flagged as a contributing factor to monitor."),
    ("2027-04-27","person_reyes","Status summary, 2027-04-27: transformer overheating theory unchanged, still listed as a watch item."),
    ("2027-05-04","system_doc","Weekly technical digest: transformer overheating carried forward as a monitored risk factor."),
    ("2027-05-11","person_reyes","Status summary, 2027-05-11: no change on the transformer overheating watch item."),
    ("2027-05-18","system_doc","Weekly technical digest: transformer overheating watch item, fourth consecutive week, unchanged."),
]):
    c24_beats.append(mk(dt, "status_summary" if key!="system_doc" else "technical_note", key, text, "probable", "derivative_copy", "supports", deriv_abs=[]))
emit_pad_placeholder = None
ALL_CHAINS["C24"] = []
for b in c24_beats:
    if not b.get("deriv_abs") and len(ALL_CHAINS["C24"]) > 0:
        b["deriv_abs"] = [ALL_CHAINS["C24"][0]]
    emit("C24", b, ALL_CHAINS["C24"])
c24_root = ALL_CHAINS["C24"][0]
emit_pad("C24", [
    mk("2027-05-25","inspection_report","person_ahn","Thermal-camera survey, 2027-05-25: transformer housing temperature within normal operating range across a full tidal cycle; no overheating detected.","unlikely","independent_primary","contradicts",contra_abs=[c24_root],evidence_root="root_thermal_survey_0525"),
    mk("2027-06-15","inspection_report","person_hale","Second independent thermal-camera survey, 2027-06-15 (different equipment, different operator): confirms transformer housing temperature normal; no correlation with trip events.","disproven","independent_primary","contradicts",contra_abs=[c24_root],evidence_root="root_thermal_survey_0615"),
    mk("2027-06-16","status_summary","person_reyes","Status summary, 2027-06-16: transformer overheating theory retired. Two independent thermal surveys outweigh the five-week chain of repeated status-summary language tracing to one informal touch-test observation.","disproven","synthesis","contradicts",contra_abs=[c24_root]),
]);

# --- Secondary arc: second authority-inversion case (05.3) -------------------
CLAIM_META["C25"] = dict(fact="F05-025", subfamily=["05.3"], subject_text="T-4 April 2 power spike", subject_entity_id="system_t4", predicate="proves", object="turbine-side fault (external consultant claim)", canonical="An external grid consultant's claim that the April 2 spike proves a turbine-side fault, versus a systems engineer's contemporaneous note that its timing matched known grid-switching patterns.")
c25_beats = [
    mk("2027-04-04","authoritative_record","person_hale","External grid-interconnection consultant (engaged briefly by Kelvinbridge, not Hale -- credentialed senior grid consultant), assessment, 2027-04-04: 'the magnitude and shape of the April 2 spike is consistent with a turbine-side fault condition; recommend treating it as evidence for an internal PCM problem.'","probable","independent_primary","supports",evidence_root="root_external_consultant_0404"),
    mk("2027-04-04","technical_note","person_costa","Jordan Costa, same-day note, 2027-04-04: spike timing (16:47:03) matches a pattern Costa has seen before in Solway Grid's public switching schedule notices; flags this as worth checking against grid logs before accepting the turbine-side explanation.","possible","independent_primary","contradicts",evidence_root="root_costa_grid_pattern_0404"),
    mk("2027-04-06","status_summary","person_reyes","Status summary, 2027-04-06: per the external consultant's assessment, the April 2 spike is treated as probable evidence of a turbine-side fault; Costa's grid-pattern note is recorded but not treated as decisive at this time.","probable","derivative_copy","supports",deriv_abs=[]),
    mk("2027-05-20","authoritative_record","system_doc","Solway Grid Connections switching log (obtained 2027-05-20): confirms the substation switching event at 16:47:03 on 2027-04-02, matching Costa's flagged pattern and directly contradicting the external consultant's turbine-side-fault assessment.","disproven","independent_primary","contradicts",contra_abs=[]),
]
ALL_CHAINS["C25"] = []
for i,b in enumerate(c25_beats):
    if i==2:
        b["deriv_abs"] = [ALL_CHAINS["C25"][0]]
    if i==3:
        b["contra_abs"] = [ALL_CHAINS["C25"][0]]
        b["deriv_abs"] = [ALL_CHAINS["C25"][1]]
    emit("C25", b, ALL_CHAINS["C25"])

# ---------------------------------------------------------------------------
# Round 2 padding -- push corpus toward the 300-memory scale with further
# genuine adversarial content (more independent corroboration, more
# derivative repetition, more paired sensor readings across dates).
# ---------------------------------------------------------------------------
r = lambda cid, k=0: ALL_CHAINS[cid][k]

emit_pad("C01", [
    mk("2027-03-30","technical_note","person_hale","Dr. Sam Hale (informal early consult, before formal June engagement), 2027-03-30: reviewed the leakage-current traces on request; agrees the pattern is suggestive but well within the range where an intermittent bearing-triggered electrical transient could produce a similar signature, so it does not cleanly discriminate between hypotheses.","disputed","independent_primary","neutral_observation",evidence_root="root_hale_early_consult_0330"),
])
emit_pad("C02", [
    mk("2027-04-08","technical_note","person_ahn","Bo Ahn, independent note, 2027-04-08: reviewed VIB-4B trend independently of Nandy's log and agrees the gradual-climb pattern before each March trip looks mechanical rather than electrical, for whatever that's worth without a decisive test.","possible","independent_primary","supports",evidence_root="root_ahn_vib_review_0408"),
])
emit_pad("C03", [
    mk("2027-05-03","technical_note","person_park","Grace Park, note, 2027-05-03: independently re-examined the original 03-20 log Singh wrote; the phrase 'might have some marine growth' was speculative and hedged, not a confirmed finding -- the certainty in later status summaries was never supported by the source text itself.","unlikely","independent_primary","contradicts",contra_abs=[ALL_CHAINS["C03"][1]]),
])
emit_pad("C04", [
    mk("2027-06-03","status_summary","person_reyes","Status summary, 2027-06-03: noting for the record that the June 2 recurrence occurred on firmware v3.1, which never carried the flagged v3.2 regression -- reopening scrutiny of the firmware explanation.","unlikely","synthesis","contradicts",contra_abs=[r("C04")]),
])
emit_pad("C05", [
    mk("2027-04-13","technical_note","person_okafor","Dr. Adaeze Okafor, note after being informed of the bearing-wear finding, 2027-04-13: 'plausible independent finding; does not by itself confirm or rule out the firmware regression we flagged separately.'","confirmed","independent_primary","neutral_observation",deriv_abs=[r("C05",2)]),
])
emit_pad("C06", [
    mk("2027-05-20","chat_message","person_reyes","Chat, 2027-05-20: 'putting harmonic resonance in the monthly board summary since it's in the exec summary already' -- another downstream document about to inherit the unverified claim.","official_working_theory","derivative_copy","supports",deriv_abs=[r("C06")]),
])
emit_pad("C08", [
    mk("2027-07-08","technical_note","person_costa","Jordan Costa, note, 2027-07-08: re-ran the tidal-phase check with a looser correlation window per Singh's original hunch; still no significant relationship found.","disproven","independent_primary","contradicts",contra_abs=[r("C08")]),
])
emit_pad("C10", [
    mk("2027-06-01","maintenance_log","person_ahn","Maintenance log, 2027-06-01: gearbox repair follow-up; noise level back to baseline per acoustic sensor, confirming the original three independent observations were tracking a real, now-resolved condition.","confirmed","synthesis","supports",deriv_abs=[r("C10")]),
])
emit_pad("C14", [
    mk("2027-07-06","sensor_log","automated_scada","SCADA log, 2027-07-06 (post-recalibration): VIB-4A and VIB-4B track within 1.5% across a full trip cycle, confirming the calibration fix resolved the discrepancy.","confirmed","independent_primary","supports",deriv_abs=[r("C14",3)]),
])
emit_pad("C15", [
    mk("2027-07-06","sensor_log","automated_scada","SCADA log, 2027-07-06 (post-teardown, TEMP-4A replaced): TEMP-4A and TEMP-4B now track within 0.5C, consistent with the corroded-lead explanation.","confirmed","independent_primary","supports",deriv_abs=[r("C15",2)]),
])
emit_pad("C18", [
    mk("2027-07-01","sensor_log","automated_scada","SCADA node A/B telemetry, 2027-07-01: ~3% gap still present after the June combined-cause repair, confirming it is unrelated to either the bearing or PCM fault.","unresolved","independent_primary","neutral_observation",deriv_abs=[r("C18",2)]),
])
emit_pad("C20", [
    mk("2027-07-30","technical_note","person_park","Grace Park, note, 2027-07-30: reviewed vessel-traffic and sensor-noise-history data once more ahead of the final report; still no way to distinguish the two hypotheses without the proposed strain gauge.","possible","independent_primary","neutral_observation",deriv_abs=[r("C20")]),
])
emit_pad("C21", [
    mk("2027-07-01","technical_note","person_hale","Dr. Sam Hale, independent note, 2027-07-01: the MESB combined finding (bearing wear + intermittent PCM fault) does not identify installation error as a contributor, which is independent confirmation that Kelvinbridge's 06-25 public statement is not supported by the evidentiary record.","unlikely","independent_primary","contradicts",contra_abs=[ALL_CHAINS["C21"][1]]),
])
emit_pad("C23", [
    mk("2027-07-02","status_summary","person_reyes","Status summary, 2027-07-02: documentation updated site-wide to reflect the combined-cause finding; explicitly notes the April RCA is superseded in scope (not in accuracy) by the July finding.","resolved_differently","derivative_copy","supports",deriv_abs=[r("C23",3)]),
])
emit_pad("C24", [
    mk("2027-06-17","chat_message","person_singh","Chat, 2027-06-17: 'ok yeah my touch-test was not exactly rigorous, my bad' -- Singh's own retrospective note on the original observation that started the chain.","disproven","derivative_copy","contradicts",deriv_abs=[r("C24")]),
])
emit_pad("C25", [
    mk("2027-05-21","status_summary","person_reyes","Status summary, 2027-05-21: updated to reflect the grid-log confirmation; the external consultant's turbine-side-fault assessment is noted as superseded by the 05-20 grid switching log.","disproven","synthesis","contradicts",contra_abs=[r("C25")]),
])

# ---------------------------------------------------------------------------
# Filler / narrative-continuity memories (uncontentious world-building, small
# set of realistic distractors not tied to a specific claim id)
# ---------------------------------------------------------------------------
FILLER = [
    dict(event="2026-10-01", obs="2026-10-01", ing="2026-10-02", subj="Meridian Bay Array", ent="facility_meridian_bay",
         pred="commissioned_on", obj="2026-10-01", mtype="authoritative_record", stype="commissioning_record",
         key="system_doc", text="Meridian Bay Array (nine turbine units, T-1 through T-9) formally commissioned 2026-10-01.", conf="confirmed"),
    dict(event="2027-01-15", obs="2027-01-15", ing="2027-01-16", subj="Turbine Unit T-2", ent="system_t2",
         pred="status", obj="normal operation", mtype="status_summary", stype="status_summary",
         key="person_reyes", text="Status summary, 2027-01-15: T-2 and T-6 continue normal operation with no anomalies to report this quarter.", conf="confirmed"),
    dict(event="2027-02-01", obs="2027-02-01", ing="2027-02-02", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="staffing_change", obj="Priya Nandy joins as junior technician", mtype="hr_record", stype="hr_record",
         key="system_doc", text="Priya Nandy joins Meridian Tidal Energy as junior site technician, 2027-02-01.", conf="confirmed"),
    dict(event="2027-03-01", obs="2027-03-01", ing="2027-03-02", subj="Turbine Unit T-4", ent="system_t4",
         pred="maintenance_event", obj="scheduled quarterly service", mtype="maintenance_log", stype="maintenance_log",
         key="person_ahn", text="Maintenance log, 2027-03-01: T-4 quarterly scheduled service completed, no issues flagged.", conf="confirmed"),
    dict(event="2027-03-30", obs="2027-03-30", ing="2027-03-31", subj="Marine Energy Safety Board", ent="org_mesb",
         pred="routine_review", obj="Q1 site inspection", mtype="authoritative_record", stype="regulatory_record",
         key="person_lindqvist", text="MESB routine Q1 site inspection at Meridian Bay Array, 2027-03-30: general compliance satisfactory; T-4 trip investigation noted as ongoing and flagged for follow-up.", conf="confirmed"),
    dict(event="2027-04-25", obs="2027-04-25", ing="2027-04-26", subj="Turbine Unit T-6", ent="system_t6",
         pred="maintenance_event", obj="routine gearbox oil change", mtype="maintenance_log", stype="maintenance_log",
         key="person_singh", text="Maintenance log, 2027-04-25: T-6 routine gearbox oil change, unrelated to T-4 investigation.", conf="confirmed"),
    dict(event="2027-05-05", obs="2027-05-05", ing="2027-05-06", subj="Solway Grid Connections", ent="org_gridco",
         pred="scheduled_maintenance", obj="substation upgrade notice", mtype="authoritative_record", stype="utility_notice",
         key="system_doc", text="Solway Grid Connections notice, 2027-05-05: scheduled substation upgrade work planned for Q3 2027, unrelated to the April switching-transient finding.", conf="confirmed"),
    dict(event="2027-05-12", obs="2027-05-12", ing="2027-05-13", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="staffing_change", obj="Dr. Sam Hale engaged as consultant (initial contact)", mtype="hr_record", stype="contract_record",
         key="system_doc", text="Initial contact and scoping call with independent marine engineering consultant Dr. Sam Hale, 2027-05-12, ahead of formal engagement in June.", conf="confirmed"),
    dict(event="2027-06-01", obs="2027-06-01", ing="2027-06-02", subj="Turbine Unit T-2", ent="system_t2",
         pred="status", obj="normal operation", mtype="status_summary", stype="status_summary",
         key="person_reyes", text="Status summary, 2027-06-01: T-2 continues normal operation; no cross-contamination of the T-4 investigation into other units observed.", conf="confirmed"),
    dict(event="2027-06-30", obs="2027-06-30", ing="2027-07-01", subj="Meridian Bay Array", ent="facility_meridian_bay",
         pred="production_report", obj="Q2 2027 output summary", mtype="status_summary", stype="quarterly_report",
         key="system_doc", text="Q2 2027 production report: array-wide output within 4% of forecast despite the T-4 investigation; T-4's downtime during trips was a minor contributor to the variance.", conf="confirmed"),
    dict(event="2027-07-20", obs="2027-07-20", ing="2027-07-21", subj="Marine Energy Safety Board", ent="org_mesb",
         pred="routine_review", obj="Q3 preliminary site visit", mtype="authoritative_record", stype="regulatory_record",
         key="person_lindqvist", text="MESB preliminary Q3 site visit, 2027-07-20: notes the pending 08-01 final investigation report as the outstanding item for this site.", conf="confirmed"),
    dict(event="2027-08-05", obs="2027-08-05", ing="2027-08-06", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="follow_up_action", obj="strain gauge installation proposed for subsea connector", mtype="technical_note", stype="technical_note",
         key="person_costa", text="Technical note, 2027-08-05: proposal to install a strain gauge on the subsea cable connector to allow future testing of the vessel-wake hypothesis (F05-020) if a similar event recurs; not yet funded.", conf="unresolved"),
    dict(event="2027-03-05", obs="2027-03-05", ing="2027-03-06", subj="Turbine Unit T-4", ent="system_t4",
         pred="maintenance_event", obj="pre-season dive inspection", mtype="inspection_report", stype="dive_inspection_report",
         key="person_ahn", text="Pre-season dive inspection, 2027-03-05: T-4 substructure and mooring hardware in good condition; routine finding, no anomalies.", conf="confirmed"),
    dict(event="2027-03-10", obs="2027-03-10", ing="2027-03-11", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="policy_update", obj="updated shift-log escalation procedure", mtype="policy_document", stype="policy_document",
         key="person_reyes", text="Updated shift-log escalation procedure issued 2027-03-10, intended to route technician observations to engineering review faster (informed in part by the delay in escalating Nandy's later bearing-temperature notes).", conf="confirmed"),
    dict(event="2027-04-01", obs="2027-04-01", ing="2027-04-02", subj="Turbine Unit T-9", ent="system_t2",
         pred="status", obj="normal operation", mtype="status_summary", stype="status_summary",
         key="person_reyes", text="Status summary, 2027-04-01: T-9 continues normal operation, unaffected by the T-4 investigation.", conf="confirmed"),
    dict(event="2027-04-18", obs="2027-04-18", ing="2027-04-19", subj="Kelvinbridge Marine Systems", ent="org_kelvinbridge",
         pred="product_notice", obj="firmware v3.3 general release", mtype="authoritative_record", stype="manufacturer_notice",
         key="person_okafor", text="Kelvinbridge releases firmware v3.3 fleet-wide, 2027-04-18, an unrelated scheduled feature update with no changes to trip-threshold logic.", conf="confirmed"),
    dict(event="2027-05-08", obs="2027-05-08", ing="2027-05-09", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="budget_event", obj="Q2 investigation budget approved", mtype="administrative_record", stype="administrative_record",
         key="person_reyes", text="Q2 investigation budget approved 2027-05-08, covering the dive inspections, independent accelerometer rig, and upcoming consultant engagement.", conf="confirmed"),
    dict(event="2027-05-14", obs="2027-05-14", ing="2027-05-15", subj="Dr. Sam Hale", ent="person_hale",
         pred="engagement_status", obj="formally engaged as independent consultant", mtype="administrative_record", stype="contract_record",
         key="system_doc", text="Dr. Sam Hale formally engaged as independent marine engineering consultant effective 2027-06-01, following the May scoping call.", conf="confirmed"),
    dict(event="2027-05-29", obs="2027-05-29", ing="2027-05-30", subj="Turbine Unit T-4", ent="system_t4",
         pred="maintenance_event", obj="gearbox inspection completed", mtype="maintenance_log", stype="maintenance_log",
         key="person_ahn", text="Maintenance log, 2027-05-29: gearbox inspection (prompted by the 05-25/05-26 noise reports) completed; minor gear-tooth wear found and logged separately from the T-4 trip investigation as routine wear-and-tear.", conf="confirmed"),
    dict(event="2027-06-01", obs="2027-06-01", ing="2027-06-02", subj="Marine Energy Safety Board", ent="org_mesb",
         pred="administrative_action", obj="formal inquiry docket opened", mtype="authoritative_record", stype="regulatory_record",
         key="person_lindqvist", text="MESB opens formal inquiry docket MESB-2027-0119 for the T-4 trip pattern, 2027-06-05, following the June 2 recurrence.", conf="confirmed"),
    dict(event="2027-06-11", obs="2027-06-11", ing="2027-06-12", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="communication", obj="internal notice of MESB inquiry and consultant engagement", mtype="internal_notice", stype="internal_notice",
         key="person_reyes", text="Internal notice, 2027-06-11: staff informed of the MESB formal inquiry and Dr. Hale's engagement; reminder to route all T-4 findings through the shared investigation log.", conf="confirmed"),
    dict(event="2027-07-03", obs="2027-07-03", ing="2027-07-04", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="communication", obj="internal circulation of July 1 combined finding", mtype="internal_notice", stype="internal_notice",
         key="person_reyes", text="Internal notice, 2027-07-03: July 1 MESB combined finding circulated to all site staff, with a note to update any local documentation still citing firmware, biofouling, or transformer-overheating as the cause.", conf="confirmed"),
    dict(event="2027-07-25", obs="2027-07-25", ing="2027-07-26", subj="Meridian Bay Array", ent="facility_meridian_bay",
         pred="production_report", obj="July 2027 output summary", mtype="status_summary", stype="monthly_report",
         key="system_doc", text="July 2027 production report: array output nominal; T-4 back in continuous service since the June 20 teardown and repair.", conf="confirmed"),
    dict(event="2027-08-10", obs="2027-08-10", ing="2027-08-11", subj="Marine Energy Safety Board", ent="org_mesb",
         pred="administrative_action", obj="inquiry docket closed with open items noted", mtype="authoritative_record", stype="regulatory_record",
         key="person_lindqvist", text="MESB closes inquiry docket MESB-2027-0119, 2027-08-10, referencing the 08-01 final report; explicitly notes two items (F05-018, F05-020) remain open/unresolved rather than closed.", conf="confirmed"),
    dict(event="2027-08-12", obs="2027-08-12", ing="2027-08-13", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="follow_up_action", obj="documentation cleanup tasked", mtype="internal_notice", stype="internal_notice",
         key="person_reyes", text="Internal notice, 2027-08-12: tasking a documentation cleanup to ensure retired theories (firmware, biofouling, transformer overheating, tidal-phase correlation) are marked resolved-false rather than silently deleted, so the investigation history remains auditable.", conf="confirmed"),
    dict(event="2027-08-14", obs="2027-08-14", ing="2027-08-15", subj="Turbine Unit T-4", ent="system_t4",
         pred="status", obj="in service, monitored", mtype="status_summary", stype="status_summary",
         key="person_reyes", text="Status summary, 2027-08-14: T-4 in continuous service since repair; SCADA node A/B discrepancy (F05-018) and the May 19 voltage-dip cause (F05-020) remain flagged open in the monitoring dashboard, not resolved.", conf="unresolved"),
]

FILLER += [
    dict(event="2027-01-05", obs="2027-01-05", ing="2027-01-06", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="staffing_change", obj="Grace Park joins as electrical engineer", mtype="hr_record", stype="hr_record",
         key="system_doc", text="Grace Park joins Meridian Tidal Energy as electrical engineer, 2027-01-05.", conf="confirmed"),
    dict(event="2027-01-20", obs="2027-01-20", ing="2027-01-21", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="staffing_change", obj="Jordan Costa joins as systems engineer", mtype="hr_record", stype="hr_record",
         key="system_doc", text="Jordan Costa joins Meridian Tidal Energy as systems engineer, 2027-01-20.", conf="confirmed"),
    dict(event="2027-02-10", obs="2027-02-10", ing="2027-02-11", subj="Turbine Unit T-4", ent="system_t4",
         pred="maintenance_event", obj="annual mooring line inspection", mtype="inspection_report", stype="inspection_report",
         key="person_ahn", text="Annual mooring line inspection, 2027-02-10: all four T-4 mooring lines within spec, no wear flagged.", conf="confirmed"),
    dict(event="2027-02-20", obs="2027-02-20", ing="2027-02-21", subj="Kelvinbridge Marine Systems", ent="org_kelvinbridge",
         pred="contract_status", obj="warranty and service agreement renewed", mtype="administrative_record", stype="contract_record",
         key="system_doc", text="Kelvinbridge Marine Systems service and warranty agreement renewed for the T-series fleet, 2027-02-20.", conf="confirmed"),
    dict(event="2027-03-08", obs="2027-03-08", ing="2027-03-09", subj="Turbine Unit T-6", ent="system_t6",
         pred="status", obj="normal operation", mtype="status_summary", stype="status_summary",
         key="person_reyes", text="Status summary, 2027-03-08: T-6 normal operation, pre-dating the T-4 trip investigation.", conf="confirmed"),
    dict(event="2027-03-29", obs="2027-03-29", ing="2027-03-30", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="communication", obj="internal weekly all-hands notes", mtype="meeting_summary", stype="meeting_summary",
         key="person_reyes", text="Weekly all-hands notes, 2027-03-29: T-4 investigation flagged as top operational priority for the coming month.", conf="confirmed"),
    dict(event="2027-04-11", obs="2027-04-11", ing="2027-04-12", subj="Turbine Unit T-4", ent="system_t4",
         pred="production_report", obj="downtime accounting for March trips", mtype="status_summary", stype="financial_note",
         key="system_doc", text="Downtime accounting note, 2027-04-11: March T-4 trips accounted for approximately 6 hours of lost generation, factored into Q1 financial reporting.", conf="confirmed"),
    dict(event="2027-04-24", obs="2027-04-24", ing="2027-04-25", subj="Meridian Bay Array", ent="facility_meridian_bay",
         pred="visitor_log", obj="regulatory site visit, unrelated permitting matter", mtype="administrative_record", stype="visitor_log",
         key="system_doc", text="Visitor log, 2027-04-24: unrelated coastal-permitting site visit by a separate agency, not connected to the T-4 investigation.", conf="confirmed"),
    dict(event="2027-05-02", obs="2027-05-02", ing="2027-05-03", subj="Turbine Unit T-4", ent="system_t4",
         pred="maintenance_event", obj="dive-team follow-up cleaning (routine, unrelated to biofouling theory)", mtype="maintenance_log", stype="maintenance_log",
         key="person_ahn", text="Maintenance log, 2027-05-02: routine hull and substructure cleaning performed during the same dive as the 05-01 VIB-4A inspection; standard biannual task, not specific to the biofouling theory.", conf="confirmed"),
    dict(event="2027-05-16", obs="2027-05-16", ing="2027-05-17", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="communication", obj="internal weekly all-hands notes", mtype="meeting_summary", stype="meeting_summary",
         key="person_reyes", text="Weekly all-hands notes, 2027-05-16: independent dive and accelerometer findings against biofouling discussed; documentation cleanup for that theory tasked for the following week.", conf="confirmed"),
    dict(event="2027-06-04", obs="2027-06-04", ing="2027-06-05", subj="Turbine Unit T-2", ent="system_t2",
         pred="maintenance_event", obj="routine annual inspection", mtype="inspection_report", stype="inspection_report",
         key="person_singh", text="Routine annual inspection, 2027-06-04: T-2 in good condition, unrelated to the T-4 investigation.", conf="confirmed"),
    dict(event="2027-06-28", obs="2027-06-28", ing="2027-06-29", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="communication", obj="internal weekly all-hands notes", mtype="meeting_summary", stype="meeting_summary",
         key="person_reyes", text="Weekly all-hands notes, 2027-06-28: teardown findings and Kelvinbridge's public statement discussed; staff reminded not to repeat the installation-error claim internally without attribution.", conf="confirmed"),
    dict(event="2027-07-12", obs="2027-07-12", ing="2027-07-13", subj="Turbine Unit T-4", ent="system_t4",
         pred="production_report", obj="downtime accounting for June trip and repair", mtype="status_summary", stype="financial_note",
         key="system_doc", text="Downtime accounting note, 2027-07-12: June T-4 trip and subsequent repair window accounted for approximately 30 hours of lost generation.", conf="confirmed"),
    dict(event="2027-08-02", obs="2027-08-02", ing="2027-08-03", subj="Meridian Tidal Energy", ent="org_meridian",
         pred="communication", obj="board briefing on final investigation report", mtype="meeting_summary", stype="meeting_summary",
         key="person_reyes", text="Board briefing, 2027-08-02: 08-01 MESB final report presented; board specifically briefed that two items (SCADA node discrepancy, May voltage dip) remain formally unresolved rather than closed.", conf="confirmed"),
]

filler_chain = []
for i, f in enumerate(FILLER):
    sid = f"src_filler_{i+1:03d}"
    key = f["key"]
    name, org, authority = PEOPLE.get(key, (key, "unknown", "unspecified"))
    mid = next_mem_id()
    rec = {
        "memory_id": mid, "experiment": EXP, "story_id": STORY,
        "event_time": f["event"], "observation_time": f["obs"], "ingestion_time": f["ing"],
        "subject_text": f["subj"], "subject_entity_id": f["ent"], "predicate": f["pred"], "object": f["obj"],
        "text": f["text"], "memory_type": f["mtype"], "truth_role": "globally_true",
        "scope": DEFAULT_SCOPE, "source_id": sid, "source_type": f["stype"],
        "derived_from": [], "supersedes": [], "contradicts": [], "aliases_used": [],
        "tags": ["exp05", "narrative_continuity"],
        "_oracle": {"fact_id": "F05-CONTEXT", "claim_id": None, "adversarial_subfamily": ["context"],
                    "canonical_claim": f["text"], "is_distractor": False, "confidence_label": f["conf"],
                    "evidence_role": "context", "stance": "neutral_observation",
                    "source_name": name, "source_org": org, "source_authority": authority,
                    "evidence_root": None, "evidence_id": None},
    }
    memories.append(rec)
    filler_chain.append(mid)

emit_pad("C03", [
    mk("2027-05-16","technical_note","system_doc","Weekly technical digest, 2027-05-16: biofouling theory marked retired in this issue per the 05-15 status summary; prior nine weeks of digest entries remain in the record unedited for audit purposes.","disproven","synthesis","contradicts",contra_abs=[ALL_CHAINS["C03"][1]]),
])
emit_pad("C06", [
    mk("2027-06-30","status_summary","person_reyes","Status summary, 2027-06-30: harmonic resonance status updated to 'unlikely, not excluded' per Hale's modal analysis and the pending combined finding.","unlikely","synthesis","contradicts",contra_abs=[r("C06")]),
])
emit_pad("C09", [
    mk("2027-01-10","technical_note","person_park","Grace Park, cross-check, 2027-01-10: rated capacity of 2.4 MW confirmed against the interconnection agreement filed with Solway Grid Connections; fourth independent confirmation.","confirmed","independent_primary","supports",deriv_abs=[r("C09")]),
])
emit_pad("C12", [
    mk("2027-06-21","technical_note","person_costa","Jordan Costa, cross-check, 2027-06-21: agrees with Park's component-level reading; no internal PCM electrical fault detected at the exact trip instant per the diagnostic readout.","confirmed","independent_primary","supports",deriv_abs=[r("C12")]),
])
emit_pad("C16", [
    mk("2027-04-16","technical_note","person_park","Grace Park, note, 2027-04-16: confirms the sampling-window explanation for the 04-08 and 04-15 SCADA-vs-manual gaps generalizes; recommend documenting this as standard practice rather than re-litigating it each time it recurs.","confirmed","synthesis","supports",deriv_abs=[r("C16")]),
])
emit_pad("C19", [
    mk("2027-05-21","status_summary","person_reyes","Status summary, 2027-05-21: 04-02 power spike formally closed as resolved -- confirmed grid switching transient, no turbine-side action needed.","confirmed","synthesis","supports",deriv_abs=[r("C19")]),
])

print(f"Total memories generated: {len(memories)}")
for cid, chain in ALL_CHAINS.items():
    print(cid, len(chain))

os.makedirs(OUTDIR, exist_ok=True)
with open(os.path.join(OUTDIR, "memories.jsonl"), "w") as fh:
    for m in memories:
        fh.write(json.dumps(m) + "\n")

# Save chains + claim meta for downstream scripts
with open(os.path.join(OUTDIR, "_gen_chains.json"), "w") as fh:
    json.dump({"chains": ALL_CHAINS, "claim_meta": CLAIM_META}, fh)

print("Wrote memories.jsonl")
