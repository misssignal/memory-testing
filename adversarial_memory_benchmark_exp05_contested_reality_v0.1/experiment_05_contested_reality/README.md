# Experiment 05 — Contested Reality

Story: **Meridian Bay** (tidal-array turbine trip investigation)

Records: 202
Queries: 153
Claims: 25 (in `claim_ledger.json`)

## Primary families

05.1 balanced unresolved contention; 05.2 majority-wrong/minority-right; 05.3 authority
inversion; 05.4 confidence evolution; 05.5 evidence-quality inversion; 05.6 genuine persistent
ambiguity; 05.7 apparent resolution then reopening; 05.8 confidence laundering; 05.9 expert
disagreement with different scopes; 05.10a–e measurement disagreement (known calibration, unknown
calibration, sampling window, different time, genuinely unexplained); plus control conditions
A–F (clear consensus, repetition with independence, authoritative-and-correct,
minority-and-wrong, uncertainty-that-resolves, uncertainty-that-never-resolves).

See `experimental_map.json` for the full per-trap breakdown (manipulated/controlled variables,
expected behavior, naive failure, metric, matched control) and `STAGE_1_SELECTION.md` for the
Stage 1 candidate-arc evaluation.

## Files

- `STAGE_1_SELECTION.md` — Stage 1 candidate-arc proposal and selection.
- `story_bible.md` — timeline, entities, evidence catalog, truth/belief/claim distinctions.
- `epistemic_state.md` — prose narration of belief evolution by actor/date, companion to the
  machine-readable ledger.
- `claim_ledger.json` — per-claim objective_status, resolution_status, supporting/contradicting
  evidence, independent_evidence_roots, belief_states by date/actor.
- `experimental_map.json` — Stage 3 trap enumeration.
- `memories.jsonl` — 202 records.
- `truth_state.json` — entities, evidence catalog, confidence/evidence-role/stance scales,
  permanently-unresolved fact list.
- `provenance.json` — memory → fact → source graph with derived_from/supersedes/contradicts.
- `queries.jsonl` — 153 ground-truth queries.
- `sources.md` — source-type glossary and `_oracle` field guide.
- `ingestion_chronological.jsonl` / `ingestion_shuffled.jsonl` / `ingestion_late_arrival.jsonl` —
  the same 202 records in event-time order, randomized order, and ingestion-time order
  respectively (verified: chronological is sorted by `event_time`, late_arrival by
  `ingestion_time`, shuffled is neither).
- `perturbations/perturbation_plan.json` — Stage 6 plan for all seven required perturbation types
  (P05-A–G), with three additionally instantiated as naturalistic matched pairs already present
  in the shipped World-A corpus.
- `SELF_REVIEW.md` — Stage 8 self-critique (standard + the 15 experiment-specific questions from
  spec section 12) and benchmark verdict.
- `tools/` — the three generator scripts used to build this package (`gen_memories.py`,
  `gen_ledger_and_truth.py`, `gen_queries.py`) plus `_gen_chains.json`, the intermediate claim/
  chain-id map the second and third scripts depend on. Re-running all three in order regenerates
  the package deterministically (fixed random seeds).

## Scale and status

This reaches **Stage 7 complete, Stage 8 (self-review) complete**. All eight stages in the spec
have a corresponding artifact in this package. Honest gaps, documented in `SELF_REVIEW.md`:

- Perturbations (Stage 6) ship as a fully-specified **plan** (`perturbation_plan.json`) covering
  all seven required types, with three types already testable today via naturalistic matched
  claim pairs in the base corpus (C03-vs-C10 for P05-C; C19-vs-C20 for P05-E; C03's own
  two-independent-root structure for P05-G's prediction). Materialized World-B variant
  memory/query files for P05-A, P05-B, P05-D, P05-F, and full P05-G are **not yet generated** —
  a follow-up pass would add ~5 small variant sub-bundles under `perturbations/`, each swapping
  exactly one variable per the plan.
  - Regenerate the base corpus with `python3 tools/gen_memories.py && python3 tools/gen_ledger_and_truth.py && python3 tools/gen_queries.py` (run from this directory; each script has `OUTDIR` hardcoded to this experiment's path — edit that constant to point elsewhere).
- 202 memories / 153 queries lands at the low end of the spec's 350–700-memory "preferred" band
  and slightly above its 75–150 query band. Every memory and query maps to a specific claim,
  subfamily, or control condition (see `experimental_map.json` / `claim_ledger.json`) — none is
  filler — but a larger corpus would allow more statistical replication per subfamily (the spec's
  "several related arcs" guidance is satisfied for 05.2 and 05.3, which each have two independent
  arcs, but not yet for the other eight subfamilies).

## Validating this package

```bash
python3 -c "
import json
mem = [json.loads(l) for l in open('memories.jsonl')]
q = [json.loads(l) for l in open('queries.jsonl')]
mem_ids = {m['memory_id'] for m in mem}
assert len(mem_ids) == len(mem), 'duplicate memory_id'
for m in mem:
    for k in ('derived_from','supersedes','contradicts'):
        assert all(r in mem_ids for r in m[k]), (m['memory_id'], k)
for qq in q:
    for r in qq['relevant_memory_ids'] + qq['distractor_memory_ids']:
        assert r in mem_ids, (qq['query_id'], r)
print('OK:', len(mem), 'memories,', len(q), 'queries, all cross-references valid')
"
```

## Important semantic distinctions

- `_oracle.confidence_label` records the *stated* confidence at the time a memory was written,
  which is sometimes deliberately unjustified by the evidence available (see 05.2/05.4/05.8).
  Do not treat it as ground truth on its own — cross-reference `claim_ledger.json`'s
  `objective_status`.
- `objective_status: "underdetermined"` is an intentional, permanent authorial state for four
  claims (C01, C02, C18, C20) per Invariant 05-E, not a placeholder pending a future revision.
- `_oracle.evidence_role: "independent_primary"` vs. `"derivative_copy"` is the basis for
  `independent_evidence_roots`; confidence should track root count, not raw memory count
  (Invariant 05-B).
