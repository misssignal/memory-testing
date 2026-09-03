# Story Bible — Experiment 05: Contested Reality

## Premise

Meridian Bay is a nine-turbine pilot tidal-energy array operated by **Meridian Tidal Energy**.
Beginning in March 2027, **Turbine Unit T-4** suffers a series of intermittent protective
shutdowns ("trips"). Over five months the investigation runs through misdiagnosis, an authority
inversion, a majority-wrong sensor theory, a confidence-laundering episode, a premature RCA
closure that reopens, several distinct flavors of instrument disagreement, and — deliberately —
two questions that the story's own evidence never allows anyone to close. The benchmark's research
target is whether a memory system preserves that structure rather than collapsing it into one
tidy answer.

## Core entities

### Organizations
- **Meridian Tidal Energy** (`org_meridian`) — site operator.
- **Kelvinbridge Marine Systems** (`org_kelvinbridge`) — turbine manufacturer.
- **Marine Energy Safety Board** (`org_mesb`) — independent regulator.
- **Solway Grid Connections** (`org_gridco`) — the utility T-4 exports power to.

### Site / hardware
- **Meridian Bay Array** (`facility_meridian_bay`), North Solway Firth pilot zone.
- **Turbine Unit T-4** (`system_t4`) — the turbine under investigation.
- Turbine Units T-2, T-6 (`system_t2`, `system_t6`) — comparison units, mostly uncontentious.
- **Power Conversion Module** (`subsystem_pcm`), **Main Gearbox** (`subsystem_gearbox`),
  **Main Shaft Bearing** (`subsystem_bearing`), **Mooring Line Array** (`subsystem_mooring`) — T-4
  subsystems.
- Sensors: `sensor_vib_4a`, `sensor_vib_4b` (vibration, two independent mounts), `sensor_temp_4a`,
  `sensor_temp_4b` (bearing temperature, two independent mounts), `sensor_scada_a`,
  `sensor_scada_b` (redundant SCADA telemetry nodes), `sensor_mooring_tension` (mooring load cell).

### People (with authority levels, used as evidence metadata only — Invariant 05-C)
- **Priya Nandy** (`person_nandy`) — junior site technician, Meridian. Low formal authority;
  correct about bearing wear.
- **Marcus Reyes** (`person_reyes`) — site operations manager, Meridian.
- **Dr. Adaeze Okafor** (`person_okafor`) — senior reliability engineer, Kelvinbridge. High formal
  authority; wrong about the firmware regression.
- **Grace Park** (`person_park`) — electrical engineer, Meridian.
- **Jordan Costa** (`person_costa`) — systems engineer, Meridian. Park and Costa's June statements
  are the 05.9 scope-disagreement pair — both correct, answering different questions.
- **Elin Lindqvist** (`person_lindqvist`) — lead investigator, Marine Energy Safety Board. High
  formal authority; correct about mooring tension (Control C).
- **Dr. Sam Hale** (`person_hale`) — independent marine engineering consultant, engaged June 2027.
- **Tom Voss** (`person_voss`) — Kelvinbridge spokesperson/PR.
- **Raj Singh** (`person_singh`), **Bo Ahn** (`person_ahn`) — night-shift and day-shift
  technicians; their independent gearbox-noise reports are Control B.
- **Dana Ferris** (`person_ferris`) — harbor pilot; source of an unsubstantiated dockside rumor.
- **Automated SCADA Monitoring System** (`automated_scada`) — treated as a source with its own
  authority level (`automated_detector`), neither inherently more nor less reliable than a human.

## Timeline (objective events, 2027)

| Date | Event |
|---|---|
| 2027-03-14 | First unexplained T-4 trip. |
| 2027-03-16 | Second T-4 trip. |
| 2027-03-15 | Site visitor reports "sparks and smoke" near the nacelle (later explained as sun glare on wet housing). |
| 2027-03-18 | Nandy's handwritten log notes a bearing-temperature drift pattern preceding both trips. |
| 2027-03-20 | A technician log entry is misread/paraphrased into a "biofouling on VIB-4A" theory; this becomes the root of a derivative citation chain (F05-003). |
| 2027-03-22 | First status report repeats the biofouling theory as the working explanation. |
| 2027-03-25 | Okafor (Kelvinbridge) issues a preliminary assessment blaming a firmware v3.2 trip-threshold regression. |
| 2027-04-01 | A whiteboard note speculates "maybe harmonic resonance, need to check" (F05-006 begins). |
| 2027-04-02 | Anomalous power spike on T-4 export line (Control E: initially unexplained). |
| 2027-04-05 | Meeting summary escalates harmonic resonance to "likely contributing factor." |
| 2027-04-10 | RCA report concludes "root cause: bearing wear, resolved" and schedules bearing replacement. |
| 2027-04-12 | Bearing replaced. |
| 2027-04-14 | Status report states harmonic resonance "identified as a contributing factor" — no new evidence introduced since 04-05. |
| 2027-04-20 | Executive summary states "root cause: harmonic resonance in mooring-rotor interaction" — confidence-laundering peak, still no new evidence. |
| 2027-05-01 | Scheduled dive inspection finds the VIB-4A sensor housing clean — first independent evidence against biofouling. |
| 2027-05-10 | An independently-mounted accelerometer at a different location shows trips uncorrelated with biofouling-theory predictions — second independent disconfirmation. |
| 2027-05-19 | Unexplained two-second voltage dip on T-4 (Control F: never resolved — decisive test never conducted). |
| 2027-06-02 | T-4 trips resume after the bearing replacement — the April RCA reopens. |
| 2027-06-05 | MESB investigator Lindqvist opens a formal inquiry. |
| 2027-06-10 | Independent consultant Hale is engaged. |
| 2027-06-15 | Park (electrical): "No electrical fault occurred in the PCM at the moment of the June 2 trip." |
| 2027-06-16 | Costa (systems): "The electrical protection system caused the June 2 shutdown." Both statements are correct; they answer different questions (05.9). |
| 2027-06-20 | Bearing teardown; TEMP-4A found to have a calibration drift undiscovered until teardown (05.10, unknown-until-hindsight case). |
| 2027-06-22 | Maintenance log cross-reference shows VIB-4A's calibration drift was already known and logged in April (05.10, known-calibration case). |
| 2027-06-25 | Kelvinbridge spokesperson Voss states publicly that the cause is "installation error by the site contractor," contradicting Kelvinbridge's own internal engineering notes. |
| 2027-07-01 | Combined finding published: both bearing wear (confirmed April/June) **and** an intermittent PCM ground fault (confirmed via June teardown) contributed; harmonic resonance is downgraded to unlikely; firmware and biofouling are formally disproven. The original March trips remain formally undetermined between the electrical and mechanical hypotheses for that specific episode — see below. |
| 2027-07-05 | Dockside rumor (Ferris): array to be "fully decommissioned by year end." No evidentiary basis; never substantiated within the story. |
| 2027-07-10 | Statistical review debunks an operator's tidal-phase correlation claim (Control D). |
| 2027-08-01 | Final investigation report: the July 1 combined finding explains the June recurrence, but investigators explicitly decline to retroactively assign the March 14/16 trips to either hypothesis, citing a data-recorder gap that makes the original episode's cause permanently underdetermined. No further testing is planned. |

## Truth / observation / belief / claim / hypothesis / rumor / official position / inference

The corpus explicitly distinguishes these epistemic categories via `memory_type` and the
`_oracle.confidence_label` / `_oracle.evidence_role` fields:

- **truth** — objective, story-authorial fact (lives in `truth_state.json` / `claim_ledger.json`
  `objective_status`, never itself a memory).
- **observation** — a direct, dated reading (sensor log, dive-inspection note, handwritten shift
  log).
- **belief** — a dated actor's internal confidence state (`claim_ledger.json` `belief_states`).
- **claim** — an assertion recorded in a memory, whether or not it is objectively true.
- **hypothesis** — an explicitly tentative explanatory claim (`memory_type: hypothesis_note`).
- **rumor** — an assertion with no evidentiary chain (`memory_type: rumor`; F05-022).
- **official position** — an institutional statement, which may or may not track internal belief
  (`memory_type: press_statement`, `official_position`; F05-021).
- **inference** — a derived conclusion from other memories (`derived_from` populated,
  `memory_type: status_summary`/`executive_summary`/`meeting_summary`).

## Evidence catalog (selected)

See `truth_state.json` → `evidence_catalog` for the full machine-readable list. Independence roots
are tracked explicitly: e.g., F05-003 (biofouling) has **one** independent evidence root (the
original misread technician log) despite ~10 derivative restatements, versus **two** independent
disconfirming roots (dive inspection; independently-mounted accelerometer) — this is the concrete
instance of Invariant 05-B (confidence is not vote count).

## Unresolved claims (by design, per Invariant 05-E)

- **F05-001 / F05-002** — March 14/16 trips: electrical-fault vs. mechanical/vibration hypothesis.
  Permanently underdetermined; the story never provides a decisive test (05.1, 05.6).
- **F05-018** — SCADA node A vs. B ~3% power-output discrepancy. Genuinely unexplained; no root
  cause is ever authored (05.10e).
- **F05-020** — May 19 two-second voltage dip: vessel-wake vs. sensor-noise. Decisive test never
  conducted (05.6, Control F, P05-E).
- **F05-021** — Whether Kelvinbridge's public "installation error" statement has any evidentiary
  support. Internally regarded as false by Meridian engineering, but never formally adjudicated
  within the story (authority/official-position divergence).

## Eventual resolutions (by design)

- **F05-003** (biofouling) — resolved false; two independent disconfirmations outweigh ~10
  derivative repetitions of one root claim (05.2).
- **F05-004** (firmware regression) — resolved false despite high-authority origin (05.3).
- **F05-005** (bearing wear) — resolved true despite low-authority origin (05.3); later folded into
  the July 1 combined finding.
- **F05-006** (harmonic resonance) — never disproven outright, but demoted from "official working
  theory" to "unlikely" once bearing wear and the electrical fault are confirmed; illustrates that
  confidence *evolution* need not end in binary confirm/disprove (05.4, 05.8).
- **F05-023** — the RCA-lifecycle umbrella claim: unresolved → provisionally resolved (April 10) →
  reopened (June 2) → resolved differently (July 1, combined cause, not the original single-cause
  RCA).

## Dramatic arcs

1. The technician who was right and the manufacturer's senior engineer who was confident and
   wrong (authority inversion, C04/C05).
2. The theory that "everyone knew" because it was repeated, not because it was independently
   observed (majority-wrong, C03).
3. The speculation that became a "known fact" in an executive summary with zero new evidence
   (confidence laundering, C06).
4. The RCA that closed, then reopened, then resolved differently (C23).
5. The two engineers who seemed to contradict each other but were both right about different
   things (C12/C13).
6. The question nobody could ever answer, because the one test that would have settled it was
   never run (C01/C02, C20).
