# Story Bible

A synthetic aerospace controls team develops Helix, a flight-control computer for an unmanned research aircraft. Across one test year the program experiences several anomalies: actuator lag, sensor resets, startup stalls, telemetry spikes, and rollback incidents. Some have clear mechanisms, some have multiple contributors, and some remain unresolved.

## C01 — January actuator lag after software deployment
- Start: 2031-01-12T09:20:00
- End: 2031-01-16T17:30:00
- Objective causal truth: Deployment was temporally adjacent but not causal; actuator lag came from intermittent bus termination resistance.
- Motifs: post_hoc, symptom_vs_cause

## C02 — February sensor reset under thermal stress
- Start: 2031-02-03T08:45:00
- End: 2031-02-10T15:10:00
- Objective causal truth: High thermal load and a firmware race jointly caused resets; neither alone was sufficient in tested conditions.
- Motifs: multiple_causes, necessary_insufficient, clean_intervention

## C03 — March retry storm and network degradation
- Start: 2031-03-14T10:05:00
- End: 2031-03-18T19:00:00
- Objective causal truth: Network degradation triggered retries; retry volume then amplified the degradation. Initial belief reversed direction.
- Motifs: reverse_causality, feedback_loop

## C04 — April startup stall after certificate renewal
- Start: 2031-04-21T07:40:00
- End: 2031-04-25T18:20:00
- Objective causal truth: Certificate renewal triggered restart; root cause was a startup dependency cycle exposed by restart timing.
- Motifs: trigger_vs_root, long_range_precursor

## C05 — May power reset fixed after module replacement
- Start: 2031-05-08T11:00:00
- End: 2031-05-12T16:45:00
- Objective causal truth: Replacement coincided with reseating harness, controller reset, and power-cycle; causal attribution to module alone remained unresolved.
- Motifs: confounded_intervention, repair_success_overreach, unresolved

## C06 — June telemetry spike during cooling demand
- Start: 2031-06-17T13:20:00
- End: 2031-06-20T14:00:00
- Objective causal truth: Ambient heat caused both cooling demand and sensor drift; cooling demand did not cause the drift.
- Motifs: common_cause, correlation

## C07 — August rollback loop after configuration migration
- Start: 2031-08-04T14:10:00
- End: 2031-08-07T20:30:00
- Objective causal truth: A configuration schema mismatch directly caused rollback evaluation failure; controlled replay reproduced and isolated it.
- Motifs: clean_causal_control, reproduction

## C08 — September intermittent sensor-hub brownout
- Start: 2031-09-09T09:30:00
- End: 2031-09-16T17:00:00
- Objective causal truth: Two mechanisms remained viable: transient connector resistance or regulator instability. No discriminating test was completed.
- Motifs: unresolved_competing_mechanisms

## C09 — October CPU spike during control-loop misses
- Start: 2031-10-02T08:00:00
- End: 2031-10-05T18:10:00
- Objective causal truth: CPU spike was a symptom of runaway diagnostic logging caused by control-loop misses, not the primary cause of misses.
- Motifs: symptom_mistaken_for_cause, reverse_direction

## C10 — November no-failure protection event
- Start: 2031-11-13T12:00:00
- End: 2031-11-13T13:15:00
- Objective causal truth: Overcurrent protection prevented actuator damage; damage did not occur.
- Motifs: prevented_outcome, negative_event

## Causal ontology

The benchmark distinguishes PRECEDES, CORRELATES_WITH, TRIGGERS, CAUSES, CONTRIBUTES_TO,
ENABLES, NECESSARY_FOR, SUFFICIENT_FOR, PROXIMATE_CAUSE_OF, ROOT_CAUSE_OF, SYMPTOM_OF,
MITIGATES, PREVENTS, MASKS, RULED_OUT_AS_CAUSE, and HYPOTHESIZED_CAUSE_OF.

Official statements and investigator beliefs are represented separately from objective causal truth.
