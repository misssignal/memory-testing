#!/usr/bin/env python3
"""Stage 2/7 companion: claim_ledger.json, truth_state.json, provenance.json,
ingestion_*.jsonl, sources.md -- built from memories.jsonl + _gen_chains.json.
"""
import json, os, random

OUTDIR = "/home/user/memory-testing/adversarial_memory_benchmark_exp05_contested_reality_v0.1/experiment_05_contested_reality"
random.seed(20270802)

memories = [json.loads(l) for l in open(os.path.join(OUTDIR, "memories.jsonl"))]
gen = json.load(open(os.path.join(OUTDIR, "_gen_chains.json")))
CLAIM_META = gen["claim_meta"]

by_claim = {}
for m in memories:
    cid = m["_oracle"]["claim_id"]
    if cid:
        by_claim.setdefault(cid, []).append(m)

OBJECTIVE_STATUS = {
 "C01": "underdetermined", "C02": "underdetermined", "C03": "false", "C04": "false",
 "C05": "true", "C06": "unsupported", "C07": "false", "C08": "false", "C09": "true",
 "C10": "true", "C11": "true", "C12": "true", "C13": "true", "C14": "true_with_known_bias",
 "C15": "true_with_undiscovered_bias_until_teardown", "C16": "true_apparent_conflict_resolved",
 "C17": "true_apparent_conflict_resolved", "C18": "underdetermined", "C19": "true",
 "C20": "underdetermined", "C21": "unsupported", "C22": "false", "C23": "corrected",
 "C24": "false", "C25": "false",
}
RESOLUTION_STATUS = {
 "C01": "unresolved", "C02": "unresolved", "C03": "resolved", "C04": "resolved",
 "C05": "resolved", "C06": "disputed_downgraded", "C07": "resolved", "C08": "resolved",
 "C09": "resolved", "C10": "resolved", "C11": "resolved", "C12": "resolved", "C13": "resolved",
 "C14": "resolved", "C15": "resolved", "C16": "resolved", "C17": "resolved", "C18": "unresolved",
 "C19": "resolved", "C20": "unresolved", "C21": "unresolved_officially_disputed_internally",
 "C22": "resolved", "C23": "resolved_differently", "C24": "resolved", "C25": "resolved",
}

BELIEF_STATES = {
 "C01": {"2027-03-22": {"investigation_team": "uncertain"}, "2027-04-05": {"investigation_team": "probable"}, "2027-08-01": {"investigation_team": "unresolved"}},
 "C02": {"2027-03-22": {"investigation_team": "unconsidered"}, "2027-04-05": {"investigation_team": "possible"}, "2027-08-01": {"investigation_team": "unresolved"}},
 "C03": {"2027-03-22": {"investigation_team": "probable"}, "2027-04-14": {"investigation_team": "probable"}, "2027-05-15": {"investigation_team": "disproven"}},
 "C04": {"2027-03-26": {"investigation_team": "probable", "kelvinbridge_team": "probable"}, "2027-06-03": {"investigation_team": "unlikely", "kelvinbridge_team": "unlikely"}, "2027-07-01": {"investigation_team": "disproven", "kelvinbridge_team": "disproven"}},
 "C05": {"2027-03-18": {"investigation_team": "uncertain"}, "2027-04-10": {"investigation_team": "confirmed"}, "2027-06-20": {"investigation_team": "confirmed_but_incomplete"}},
 "C06": {"2027-04-01": {"investigation_team": "possible"}, "2027-04-14": {"investigation_team": "official_working_theory"}, "2027-06-10": {"investigation_team": "disputed"}, "2027-07-01": {"investigation_team": "unlikely"}},
 "C07": {"2027-03-15": {"investigation_team": "uncertain"}, "2027-03-18": {"investigation_team": "unlikely"}, "2027-06-20": {"investigation_team": "reframed_as_early_pcm_signal"}},
 "C08": {"2027-04-15": {"investigation_team": "possible"}, "2027-07-10": {"investigation_team": "disproven"}},
 "C09": {"2026-11-01": {"investigation_team": "confirmed", "kelvinbridge_team": "confirmed", "mesb_team": "confirmed"}},
 "C10": {"2027-05-25": {"investigation_team": "possible"}, "2027-05-28": {"investigation_team": "confirmed"}},
 "C11": {"2027-06-08": {"investigation_team": "unresolved"}, "2027-06-12": {"investigation_team": "confirmed", "mesb_team": "confirmed"}},
 "C12": {"2027-06-15": {"investigation_team": "confirmed"}},
 "C13": {"2027-06-16": {"investigation_team": "confirmed"}, "2027-06-17": {"investigation_team": "confirmed_scope_reconciled"}},
 "C14": {"2027-06-05": {"investigation_team": "uncertain"}, "2027-06-22": {"investigation_team": "confirmed_known_calibration_issue"}},
 "C15": {"2027-05-30": {"investigation_team": "uncertain"}, "2027-06-08": {"investigation_team": "uncertain"}, "2027-06-20": {"investigation_team": "confirmed_after_teardown"}},
 "C16": {"2027-04-08": {"investigation_team": "uncertain"}, "2027-04-09": {"investigation_team": "confirmed_sampling_artifact"}},
 "C17": {"2027-06-08": {"investigation_team": "uncertain"}, "2027-06-09": {"investigation_team": "confirmed_tidal_state_artifact"}},
 "C18": {"2027-06-01": {"investigation_team": "uncertain"}, "2027-06-15": {"investigation_team": "unresolved"}, "2027-08-01": {"investigation_team": "unresolved"}},
 "C19": {"2027-04-02": {"investigation_team": "uncertain"}, "2027-05-20": {"investigation_team": "confirmed"}},
 "C20": {"2027-05-19": {"investigation_team": "uncertain"}, "2027-08-01": {"investigation_team": "unresolved"}},
 "C21": {"2027-06-20": {"kelvinbridge_team": "unlikely"}, "2027-06-25": {"kelvinbridge_spokesperson": "official_working_theory"}, "2027-07-02": {"investigation_team": "unlikely"}},
 "C22": {"2027-07-05": {"public_rumor": "rumor"}, "2027-07-15": {"investigation_team": "false"}},
 "C23": {"2027-03-14": {"investigation_team": "unresolved"}, "2027-04-10": {"investigation_team": "provisionally_resolved"}, "2027-06-02": {"investigation_team": "reopened"}, "2027-07-01": {"investigation_team": "resolved_differently"}},
 "C24": {"2027-04-18": {"investigation_team": "possible"}, "2027-05-11": {"investigation_team": "probable"}, "2027-06-16": {"investigation_team": "disproven"}},
 "C25": {"2027-04-04": {"kelvinbridge_team": "probable", "investigation_team": "uncertain"}, "2027-05-21": {"investigation_team": "disproven"}},
}

ledger = []
for cid, meta in CLAIM_META.items():
    ms = by_claim.get(cid, [])
    supporting = [m["_oracle"]["evidence_id"] for m in ms if m["_oracle"]["stance"] == "supports" and m["_oracle"]["evidence_id"]]
    contradicting = [m["_oracle"]["evidence_id"] for m in ms if m["_oracle"]["stance"] == "contradicts" and m["_oracle"]["evidence_id"]]
    roots = sorted({
        (m["_oracle"]["evidence_root"] or m["memory_id"])
        for m in ms if m["_oracle"]["evidence_role"] == "independent_primary"
    })
    entry = {
        "claim_id": cid,
        "fact_id": meta["fact"],
        "claim": meta["canonical"],
        "adversarial_subfamily": meta["subfamily"],
        "objective_status": OBJECTIVE_STATUS.get(cid, "underdetermined"),
        "resolution_status": RESOLUTION_STATUS.get(cid, "unresolved"),
        "supporting_evidence": supporting,
        "contradicting_evidence": contradicting,
        "independent_evidence_roots": len(roots),
        "independent_evidence_root_labels": roots,
        "memory_ids": [m["memory_id"] for m in ms],
        "belief_states": BELIEF_STATES.get(cid, {}),
    }
    ledger.append(entry)

with open(os.path.join(OUTDIR, "claim_ledger.json"), "w") as fh:
    json.dump({"story_id": "meridian_bay", "claims": ledger}, fh, indent=2)
print("Wrote claim_ledger.json with", len(ledger), "claims")

# --- truth_state.json -------------------------------------------------------
entities = [
    {"canonical_id": "org_meridian", "canonical_name": "Meridian Tidal Energy", "entity_type": "organization"},
    {"canonical_id": "org_kelvinbridge", "canonical_name": "Kelvinbridge Marine Systems", "entity_type": "organization"},
    {"canonical_id": "org_mesb", "canonical_name": "Marine Energy Safety Board", "entity_type": "organization"},
    {"canonical_id": "org_gridco", "canonical_name": "Solway Grid Connections", "entity_type": "organization"},
    {"canonical_id": "facility_meridian_bay", "canonical_name": "Meridian Bay Array", "entity_type": "facility"},
    {"canonical_id": "system_t4", "canonical_name": "Turbine Unit T-4", "entity_type": "system"},
    {"canonical_id": "system_t2", "canonical_name": "Turbine Unit T-2", "entity_type": "system"},
    {"canonical_id": "system_t6", "canonical_name": "Turbine Unit T-6", "entity_type": "system"},
    {"canonical_id": "subsystem_pcm", "canonical_name": "Power Conversion Module", "entity_type": "subsystem"},
    {"canonical_id": "subsystem_gearbox", "canonical_name": "Main Gearbox", "entity_type": "subsystem"},
    {"canonical_id": "subsystem_bearing", "canonical_name": "Main Shaft Bearing", "entity_type": "subsystem"},
    {"canonical_id": "subsystem_mooring", "canonical_name": "Mooring Line Array", "entity_type": "subsystem"},
    {"canonical_id": "sensor_vib_4a", "canonical_name": "Vibration Sensor VIB-4A", "entity_type": "sensor"},
    {"canonical_id": "sensor_temp_4a", "canonical_name": "Bearing Temperature Sensor TEMP-4A", "entity_type": "sensor"},
    {"canonical_id": "person_nandy", "canonical_name": "Priya Nandy", "entity_type": "person", "role": "junior_technician", "org": "org_meridian"},
    {"canonical_id": "person_reyes", "canonical_name": "Marcus Reyes", "entity_type": "person", "role": "site_manager", "org": "org_meridian"},
    {"canonical_id": "person_okafor", "canonical_name": "Dr. Adaeze Okafor", "entity_type": "person", "role": "senior_engineer_manufacturer", "org": "org_kelvinbridge"},
    {"canonical_id": "person_park", "canonical_name": "Grace Park", "entity_type": "person", "role": "electrical_engineer", "org": "org_meridian"},
    {"canonical_id": "person_costa", "canonical_name": "Jordan Costa", "entity_type": "person", "role": "systems_engineer", "org": "org_meridian"},
    {"canonical_id": "person_lindqvist", "canonical_name": "Elin Lindqvist", "entity_type": "person", "role": "external_regulator_investigator", "org": "org_mesb"},
    {"canonical_id": "person_hale", "canonical_name": "Dr. Sam Hale", "entity_type": "person", "role": "independent_consultant", "org": "independent"},
    {"canonical_id": "person_voss", "canonical_name": "Tom Voss", "entity_type": "person", "role": "spokesperson", "org": "org_kelvinbridge"},
    {"canonical_id": "person_singh", "canonical_name": "Raj Singh", "entity_type": "person", "role": "technician", "org": "org_meridian"},
    {"canonical_id": "person_ahn", "canonical_name": "Bo Ahn", "entity_type": "person", "role": "technician", "org": "org_meridian"},
    {"canonical_id": "person_ferris", "canonical_name": "Dana Ferris", "entity_type": "person", "role": "harbor_pilot_bystander", "org": "external"},
    {"canonical_id": "automated_scada", "canonical_name": "SCADA Automated Monitoring System", "entity_type": "automated_system", "role": "automated_detector", "org": "org_meridian"},
]

evidence_catalog = []
for m in memories:
    o = m["_oracle"]
    if o.get("evidence_id"):
        evidence_catalog.append({
            "evidence_id": o["evidence_id"], "memory_id": m["memory_id"], "fact_id": o["fact_id"],
            "claim_id": o["claim_id"], "evidence_role": o["evidence_role"], "evidence_root": o.get("evidence_root"),
            "stance": o["stance"], "source_authority": o["source_authority"], "confidence_label": o["confidence_label"],
            "observation_time": m["observation_time"],
        })

truth_state = {
    "story_id": "meridian_bay",
    "timeline_span": {"start": "2026-10-01", "end": "2027-08-14"},
    "entities": entities,
    "confidence_label_scale": ["rumor", "possible", "uncertain", "disputed", "probable",
        "official_working_theory", "confirmed", "unlikely", "disproven",
        "provisionally_resolved", "reopened", "resolved_differently"],
    "evidence_role_scale": ["independent_primary", "derivative_copy", "synthesis", "context"],
    "stance_scale": ["supports", "contradicts", "neutral_observation"],
    "adversarial_subfamilies": {
        "05.1": "balanced_unresolved_contention", "05.2": "majority_wrong_minority_right",
        "05.3": "authority_inversion", "05.4": "confidence_evolution",
        "05.5": "evidence_quality_inversion", "05.6": "genuine_persistent_ambiguity",
        "05.7": "apparent_resolution_then_reopening", "05.8": "confidence_laundering",
        "05.9": "expert_disagreement_different_scopes", "05.10a": "measurement_disagreement_known_calibration",
        "05.10b": "measurement_disagreement_unknown_calibration", "05.10c": "measurement_disagreement_sampling_window",
        "05.10d": "measurement_disagreement_different_time", "05.10e": "measurement_disagreement_unexplained",
        "control_A": "clear_consensus", "control_B": "repetition_with_independence",
        "control_C": "authoritative_and_correct", "control_D": "minority_and_wrong",
        "control_E": "uncertainty_that_later_resolves", "control_F": "uncertainty_that_never_resolves",
        "rumor": "unsubstantiated_rumor", "context": "narrative_continuity",
    },
    "evidence_catalog": evidence_catalog,
    "permanently_unresolved_fact_ids": ["F05-001", "F05-002", "F05-018", "F05-020", "F05-021"],
    "notes": {
        "_oracle": "Development-only ground-truth metadata; strip for blind-system runs.",
        "underdetermined": "objective_status may be 'underdetermined' where the story itself never supplies a decisive test; this is intentional per Invariant 05-E and must not be inferred to secretly favor one hypothesis.",
    },
}
with open(os.path.join(OUTDIR, "truth_state.json"), "w") as fh:
    json.dump(truth_state, fh, indent=2)
print("Wrote truth_state.json")

# --- provenance.json ---------------------------------------------------------
nodes = []
for m in memories:
    o = m["_oracle"]
    nodes.append({
        "memory_id": m["memory_id"], "fact_id": o["fact_id"], "source_id": m["source_id"],
        "derived_from": m["derived_from"], "supersedes": m["supersedes"], "contradicts": m["contradicts"],
        "evidence_root": o.get("evidence_root"),
    })
with open(os.path.join(OUTDIR, "provenance.json"), "w") as fh:
    json.dump({"nodes": nodes}, fh, indent=2)
print("Wrote provenance.json")

# --- ingestion variants -------------------------------------------------------
chrono = sorted(memories, key=lambda m: (m["event_time"], m["memory_id"]))
late = sorted(memories, key=lambda m: (m["ingestion_time"], m["memory_id"]))
shuffled = memories[:]
random.shuffle(shuffled)

for name, data in [("ingestion_chronological.jsonl", chrono),
                    ("ingestion_late_arrival.jsonl", late),
                    ("ingestion_shuffled.jsonl", shuffled)]:
    with open(os.path.join(OUTDIR, name), "w") as fh:
        for m in data:
            fh.write(json.dumps(m) + "\n")
print("Wrote ingestion variants")

# --- sources.md ---------------------------------------------------------------
sources_md = """# Sources

This story is fully synthetic. No real company, product, regulator, or incident is being asserted
as factual. Meridian Tidal Energy, Kelvinbridge Marine Systems, the Marine Energy Safety Board,
Solway Grid Connections, and all named individuals are fictional benchmark artifacts.

## Source types in this corpus

- `sensor_log` -- automated SCADA/instrumentation readings (`automated_scada`).
- `handwritten_log` / `technical_note` -- direct technician or engineer observations.
- `status_summary` / `executive_summary` / `meeting_summary` -- institutional documents, often
  derivative of an earlier technical note (see `derived_from`).
- `investigation_report` / `rca_report` / `teardown_report` / `inspection_report` -- formal
  findings, some provisional (see `truth_role` and `_oracle.confidence_label`).
- `press_statement` -- an official public position, which may diverge from the internal
  evidentiary record (Invariant 05-C). Never treat as automatically authoritative.
- `rumor` / `dockside_rumor` -- explicitly unattributed, no evidentiary chain.
- `authoritative_record` -- nameplate data, regulatory records, utility logs, commissioning
  reports; still subject to Invariant 05-C (authoritative does not mean automatically correct
  for interpretive claims, though several Control-A/C records here are both authoritative and
  correct by design).

## Reading `_oracle`

Each memory's `_oracle` block records development-only ground truth: `fact_id`, `claim_id`
(cross-referencing `claim_ledger.json`), `adversarial_subfamily`, `is_distractor`,
`confidence_label` (the *stated* confidence at the time, not necessarily justified confidence),
`evidence_role` (`independent_primary` / `derivative_copy` / `synthesis` / `context`), `stance`
(`supports` / `contradicts` / `neutral_observation` relative to the claim), `source_authority`,
and `evidence_root` (a label shared by all derivative copies of one underlying observation --
used to compute `independent_evidence_roots` in `claim_ledger.json`). Strip `_oracle` for blind
runs, per `manifest.json`.
"""
with open(os.path.join(OUTDIR, "sources.md"), "w") as fh:
    fh.write(sources_md)
print("Wrote sources.md")
