# Experiment 07 — The Shape of What Is Not Known

Story: **Meridian Station** (`meridian_station`) — a fictional 14-person
multinational Antarctic winter-over research station, 2031 season.

Records: 358
Queries: 80
Missingness-map claim entries: 51 (+2 direct controls, A/B, folded into
`queries.jsonl` but excluded from `missingness_map.json` since they are not
missingness propositions)

## Primary families

07.1 never recorded; 07.2 observation gap; 07.3 inaccessible source;
07.4 partial observation; 07.5 misleading premise; 07.6 multiple compatible
worlds; 07.7 evidence of absence (valid); 07.8 incomplete negative evidence
(invalid); 07.9 known-but-unspecified; 07.10 default-value trap; 07.11
continuity trap; 07.12 exhaustive-enumeration control; 07.13 lost evidence.

Plus direct Control A (explicit positive) and Control B (explicit negative)
anchors, and Control G (constraint-based deduction).

See `experimental_map.md` for the full per-claim table (proposition, objective
truth, observability, recording status, accessibility, inference status,
expected answer, manipulated variable, control).

## Important parser notes

- `_oracle` is development-only metadata (per `schema.json`); strip it for
  blind-system runs, along with `subject_entity_id` and `truth_role` if
  testing retrieval alone.
- A memory's absence from the corpus for a given window is not itself a
  memory — several claims (e.g. C34, the pre-Day-63 Tunnel Door) are
  correctly represented by there being **no matching record at all**, not by
  a record that says "no data." Do not treat sparse retrieval results near a
  claim's time window as a bug; for several claims it is the point.
- `queries.jsonl` extends the Experiment 03/04 query schema with six fields
  specific to this experiment's Stage 7 requirement: `answerability`,
  `missingness_type`, `compatible_world_count`, `negative_inference_valid`,
  `premise_valid`, `required_abstention_reason`. See the top-level
  `schema.json` for the full field list and the `answerability` enum.
- `missingness_map.json` is this experiment's required Stage 6 artifact (per
  the generation spec's §6): one entry per claim proposition, with `status`,
  `available_evidence` (memory IDs), `missing_evidence` (named missing
  channels/artifacts), `compatible_worlds`, `negative_inference_valid`, and
  `coverage`.
- Two claims (C31/C32) deliberately reproduce the generation spec's own
  worked example ("Did Rowan enter Lab B...") almost verbatim, as a direct
  fidelity check between the spec and the shipped corpus.

## Status

Stage 8 (self-review) is complete — see the top-level `SELF_REVIEW.md`. All
eight generation stages were completed for this v0.1 bundle. Scale (358
memories / 80 queries) sits comfortably inside the requested 300-650 /
75-150 ranges without padding: every filler memory is a distinct, non-
repeating routine-life record, and every trap claim has real, hand-authored
supporting evidence rather than templated boilerplate.

Possible future expansion (not done in this bundle, and not required to
reach a complete Stage-8 pass): additional partial-observation cases at
Field Camp Delta itself (its own two-person population is small enough that
most of its internal state is either fully known between the two of them or
fully unknown to the station — a further "co-located witness" sub-study),
and a second controlled-perturbation corpus fork materializing P07-D's
counterfactual variant B as a literal alternate file rather than a
documented description.
