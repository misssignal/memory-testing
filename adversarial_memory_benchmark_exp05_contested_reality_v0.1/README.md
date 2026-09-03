# Adversarial Memory Benchmark — Experiment 05 (v0.1)

Parser-ready synthetic benchmark bundle.

## Contents

- `experiment_05_contested_reality/`
- `schema.json`
- `manifest.json`
- `EXPERIMENT_MAP.md`
- `checksums.sha256.json`

The experiment directory mirrors the earlier benchmark packaging pattern (exp01–04), plus the
experiment-specific epistemic files this spec introduces:

- `README.md`
- `STAGE_1_SELECTION.md`
- `story_bible.md`
- `epistemic_state.md` *(new for Experiment 05)*
- `claim_ledger.json` *(new for Experiment 05)*
- `experimental_map.json`
- `memories.jsonl`
- `truth_state.json`
- `provenance.json`
- `queries.jsonl`
- `sources.md`
- `ingestion_chronological.jsonl`
- `ingestion_shuffled.jsonl`
- `ingestion_late_arrival.jsonl`
- `perturbations/perturbation_plan.json`
- `SELF_REVIEW.md`
- `tools/` (generator scripts)

## Scale

This v0.1 bundle contains:

- Experiment 05: 202 memories, 153 queries, 25 tracked claims

This lands at the low end of the spec's preferred 350–700-memory band (above its 200-memory
floor) and slightly above its 75–150-query band. Every record maps to a specific claim,
adversarial subfamily, or control condition (see `experiment_05_contested_reality/claim_ledger.json`
and `experimental_map.json`) — repetition is used deliberately as an experimental variable (see
Invariant 05-B), not as filler.

## Hidden fields

`memories.jsonl` contains an `_oracle` object for benchmark development, extended for
Experiment 05 with `claim_id`, `adversarial_subfamily`, `confidence_label`, `evidence_role`,
`stance`, `source_authority`, and `evidence_root`/`evidence_id`. A production harness should be
able to strip `_oracle`, `subject_entity_id`, `truth_role`, and/or normalized `scope` fields
depending on the condition being tested (see `manifest.json`).

## Important semantic distinction

`objective_status: "underdetermined"` (in `claim_ledger.json`) is not a data-quality issue to be
resolved in a later revision. Four claims (the original March turbine-trip episode, split into two
competing hypotheses; a redundant-telemetry discrepancy; a voltage-dip cause) are authorially,
permanently unresolved — the story itself never supplies the decisive test that would settle them.
Per Invariant 05-E, the benchmark's correct ground truth for these is "insufficient evidence,"
not a synthetic tie-breaker chosen for scoring convenience.

## Status

This is a Stage-7/8-complete corpus: story bible, epistemic state, claim ledger, experimental map,
full memory expansion (202 records), ground-truth queries (153), and a self-review with a
benchmark verdict are all present. Stage 6 (controlled perturbations) ships a complete plan for
all seven required perturbation types, with materialized World-B variant files generated for none
yet (three of the seven perturbation predictions are additionally testable today via naturalistic
matched claim pairs already present in the base corpus — see
`experiment_05_contested_reality/README.md` for specifics). A future revision could expand the
corpus toward the 350–700-memory band (adding more independent arcs per subfamily, per the spec's
"several related arcs" guidance) and materialize the remaining perturbation variant files.
