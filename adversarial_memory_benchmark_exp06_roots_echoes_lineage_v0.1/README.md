# Adversarial Memory Benchmark — Experiment 06 (v0.1)

Parser-ready synthetic benchmark bundle. Packaging mirrors the earlier `exp03_04_v0.1` bundle
convention so the same harness code can load it.

## Contents

- `experiment_06_roots_echoes_evidence_lineage/`
- `schema.json`
- `manifest.json`
- `EXPERIMENT_MAP.md`
- `checksums.sha256.json`

Each experiment directory mirrors the earlier benchmark packaging pattern:

- `README.md`
- `story_bible.md`
- `provenance_bible.md` *(new in exp06 — the explicit evidence-topology half of Stage 2, kept
  separate from the narrative `story_bible.md` since the spec asks for both a story bible and a
  provenance bible)*
- `self_review.md` *(new in exp06 — Stage 8 self-review and the spec's §12 self-critique answers)*
- `memories.jsonl`
- `truth_state.json`
- `provenance.json`
- `provenance_graph.json` *(new in exp06 — node-level lineage graph, spec section 6)*
- `claim_lineage.json` *(new in exp06 — claim-level provenance, spec section 6)*
- `queries.jsonl`
- `sources.md`
- `ingestion_chronological.jsonl`, `ingestion_shuffled.jsonl`, `ingestion_late_arrival.jsonl`
- `perturbations/perturbation_plan.json`

## Scale

This v0.1 bundle contains:

- Experiment 06: **413 memories**, **128 queries**, **88 fact instances**, **419 claim-level
  provenance records**, across all 12 required adversarial subfamilies (§06.1–§06.12) and all 8
  query categories (§9.1–§9.8).

This sits inside the spec's preferred 350–750-memory band. Repetition here is a deliberate
experimental variable, exactly as in exp03/04: the same *kind* of incident (a pressure trip, a
vibration excursion, a stuck relay valve, ...) recurs at different Thornfield Systems sites with
different Sentinel units, so that fan-out, cascade, convergence, and cycle motifs can each be
demonstrated cleanly and repeatedly without one shared graph tangling every test together. See
`experiment_06_roots_echoes_evidence_lineage/story_bible.md` for why 350–750 memories, reached this
way, is not filler.

## Central research question

Can the system explain where a claim came from, and distinguish genuinely independent
corroboration from many descendants of the same evidence root? A system can retrieve the right
documents and paraphrase-match perfectly while still failing this question — which is why it is
tested as its own axis rather than folded into retrieval-quality scoring. See
`experiment_06_roots_echoes_evidence_lineage/self_review.md`, "Benchmark verdict," for the full
statement of what capabilities are required to pass.

## Hidden fields

`memories.jsonl` contains an `_oracle` object for benchmark development. A production harness
should strip `_oracle` for blind runs — and should be especially careful to strip
`_oracle.archived_text_dev_only`, which holds the full original content of the five tombstoned
"source disappearance" evidence roots (§06.11) and would trivially solve those queries by
inspection if leaked. See `manifest.json`'s `blind_run_recommendation`.

## Important semantic distinction

`derived_from` and `contradicts` are *not* oracle metadata — they are ordinary required fields
from the base `memory_record` schema (unchanged from exp03/04) and are the actual graph edges this
experiment is testing. They must be preserved in any blind run; only the `_oracle` side-channel
that names ground truth (ultimate evidence roots, cycle membership, unsupported-clause spans, dev
flags) should be stripped.

## Status

**All 8 generation stages (candidate selection through self-review) were completed** for this
v0.1 bundle. See `experiment_06_roots_echoes_evidence_lineage/README.md`'s "Status (Stage
reached)" section for the itemized stage-by-stage account, and `self_review.md` for a defect found
and fixed during the Stage 8 audit (a testing-scaffold label had leaked into an exposed field and
was moved to oracle-only metadata before packaging — documented rather than silently corrected).
What remains open for a v0.2 pass is also itemized there rather than left implicit: primarily,
room to grow the corpus further toward the 750-memory ceiling, and a known semantic-shortcut
vulnerability (root nodes are always chronologically earliest within their cluster) that a future
revision should close with early-timestamped non-root distractors.

## How to regenerate and validate

See `experiment_06_roots_echoes_evidence_lineage/README.md`, "How to regenerate" / "How to
validate." In short: four deterministic, seeded, stdlib-only Python scripts at
`scripts/exp06_generation/` in the repository (outside this bundle) reproduce every generated file
byte-for-byte; a short validation script in that same README checks referential integrity
(`derived_from` edges, query `relevant_memory_ids`) across the whole bundle.
