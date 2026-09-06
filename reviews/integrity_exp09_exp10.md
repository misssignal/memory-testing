# Integrity Review — Experiment 09 (Causal Attribution) and Experiment 10 (Kestrel Full Corpus)

Reviewed: `experiment_09_causal_attribution.zip`, `experiment_10_kestrel_full_corpus.zip` (repo root, commit d55d31e).
Method: extract each zip, then run `scripts/integrity/check_exp09.py` / `check_exp10.py` against the
extracted directory. Every claim below was produced by those scripts or by direct inspection of the files.

## Verdict

| Bundle | Structural integrity | Content integrity | Usable as-is? |
|---|---|---|---|
| Exp 10 | PASS (checksums, counts, refs, clocks, delivery runs all verified) | Caveats: duplicated queries, unlinked queries, answer-key language in memory text | Yes, after a small cleanup |
| Exp 09 | PASS on counts/ids/refs; no checksums to verify | FAIL: evidence file broken for headline claims, corpus is heavily templated, gold answers mostly non-specific | Not yet |

---

## Experiment 10 — Kestrel Full Corpus

### Verified clean
- `manifest.json` lists 25 files; all 25 byte sizes and SHA-256 digests match. No unlisted or missing files.
- 500 memories, ids `K10-M001`..`K10-M500`, no gaps, no duplicates, one key set. 120 queries, one key set.
- All 137 `derived_from`, 16 `supersedes`, 27 `contradicts` references resolve. All `provenance.json` refs resolve.
  The correction edge M020 -> M021 matches M021's `supersedes` field.
- Four-clock ordering `event <= observation <= authored <= ingestion` holds for all 500 records.
- `analysis/corpus_stats.json` reproduces exactly for memory_types, source_types, top_tags, derived (116),
  superseding (16), late_arrival (50). `control_or_distractor_count` = 222 only if `non_decisive` is counted
  alongside `control`/`distractor` (192 without it); the definition is undocumented.
- `R00_canonical_ingestion` is exactly the corpus sorted by `ingestion_time`. All five checkpoints are exact prefixes of R00.
- Every delivery run does what its description says:
  - R01–R03: `random.Random(seed).shuffle(sorted(ids))` reproduces each sequence.
  - R04: the five R7/DT-3 primaries (M008, M009, M010, M017, M018) occupy positions 495–499; all other relative order preserved.
  - R05: all 16 corrections precede their originals (0/16 in R00).
  - R06: M017, M045, M046 each delivered 8 times.
  - R07: `R00[:260] + R00[220:300] + R00[260:]` (80 records replayed once), matching `restart_boundaries=[260]`, `replay_window=220..299`.
  - R08: `batch_order` applied to ten 50-record batches reproduces the sequence.
  - R09: all 116 derived records precede all non-derived records.
  - R10: `R00[:320] + R00[250:] + R00[320:]` — see caveat below.
  - R11: exact reverse of R00.
  - R12: tail is the `non_impacting_late_evidence` block. R13: last record is M213 (confidence-reducing note).
- The 10 `ambiguous_order` pairs genuinely share `event_time` and `ingestion_time`.
- Locked truths in `truth_state.json` are stated verbatim by the referenced primaries (M017/M018 R7, M008–M010 DT-3, M020/M021 Jonah, M040/M041 FC-4.8.3).

### Issues (in priority order)

1. **40 of 120 queries are byte-identical duplicates.** Four blocks of ten (Q061–070, Q071–080, Q091–100, Q101–110)
   repeat the same query text, expected claims, and relevant ids. Distinct queries = 84. The manifest's `query_count: 120`
   and README's "120 benchmark queries" overstate coverage, and any aggregate score is weighted 10x toward four questions.
2. **30 queries have empty `relevant_memory_ids` although their target memories exist.** Q041–Q060 (`event_vs_discovery`)
   should link to K10-M459..M478 (subsystems X1–X10 / Y1–Y10); Q111–Q120 (`authored_vs_event`) should link to K10-M479..M488
   (field logs 1–10). Retrieval-based scoring cannot run on a quarter of the (deduplicated) query set.
3. **Answer-key language inside memory text.** 148/500 memories state the conclusion the benchmark wants, e.g.
   "replay of older Flight 17 evidence must not revert this later current state" (20 records), "replay should not affect
   Flight 17 evidence ranking" (10), "is not independent" / "adds no independent primary evidence" (40),
   "this is late occurrence, not late discovery" (10), "the evidence cannot determine which marker occurred first" (10).
   A system that surfaces the retrieved text will pass those queries without doing the reasoning the invariant is meant
   to test. Either strip the evaluative clauses or document that those query families test retrieval rather than inference.
4. **Templating.** All 500 texts are unique strings, but only 91 digit-stripped templates exist; 29 families of 10+
   cover 392 records (about 51 records look hand-written). Adequate for an ordering/replay benchmark, but weaker realism
   than exp05 (198 templates / 202 records) or exp07.
5. **R10 undocumented third pass.** After the stale resume from 250, records 320–499 are delivered a third time.
   `restart_boundaries=[320]`, `stale_resume_from=250` explain only the second pass. Either document the extra pass or drop it.
6. **Q006 has empty `expected_claims`** (the only such query). Q006 and Q018 are correctly marked `run_invariant: false`.
7. Minor: the `late_arrival` tag is semantic, not mechanical; 28 untagged records have an ingestion delay over one day
   (M033, M037, M042, M043, M045, M046, M459…). Fine, but worth a sentence in the README.

---

## Experiment 09 — Causal Attribution

### Verified clean
- Counts match `manifest.json`: 525 memories, 133 queries, 10 cases, 23 claims, 180 background, 11 perturbations,
  2 unresolved cases (C05, C08).
- ids `M0001`..`M0525`, no gaps, no duplicates, one key set (identical to exp08's schema). `seed_memories.jsonl` (60)
  is an exact subset of `memories.jsonl`.
- `event <= observation <= ingestion` holds for all 525 records.
- All query `relevant_memory_ids` resolve. `causal_graph.json` edge set equals `causal_claims.json` exactly.
  `causal_evidence.json` covers exactly the 23 claim ids.
- Case memories fall inside their story-bible windows except three intentional records (M0341/M0342 precursors, M0345 retrospective).
- No manifest checksums exist (unlike exp10 and the exp05–07 bundles), so nothing beyond archive extraction could be verified.

### Issues (in priority order)

1. **`causal_evidence.json` is empty for 5 of 23 claims, including headline claims.** CC001 (bus-termination-resistance
   CAUSES retries — the true cause of C01), CC004 (thermal CONTRIBUTES_TO reset), CC006 (thermal+race jointly CAUSE reset,
   the C02 answer), CC008 (retry volume CONTRIBUTES_TO degradation), CC021 (control-loop misses CAUSE log storm, the C09
   answer) have zero supporting and zero contradicting evidence. The pattern (claims whose effect is an intermediate node)
   points to a generator keyed on each case's terminal outcome.
2. **Evidence lists are stride-sampled, not content-selected.** Seven claims list the same memory as both supporting and
   contradicting (CC003 M0008; CC012/CC013 M0149; CC016 M0178, M0184, M0187; CC019 M0250, M0255; CC020 M0255, M0260).
   CC002 and CC003 (a CAUSES claim and a PRECEDES/noncausal claim) share an identical support list; CC014/CC015 are identical.
   The file cannot be used to score evidence-grounding.
3. **Corpus is a small template set replicated.** The 345 case memories consist of 68 base sentences, each repeated 4–8
   times with one of four boilerplate suffixes ("The note distinguishes observation from explanation.", etc.). The 180
   background memories are 10 sentences repeated 18x each. 42 texts are exact duplicates (max 24 copies) while
   `duplicates[]` is empty on every record. Consequences:
   - `memory_type` is assigned round-robin and decoupled from content: 63/68 base sentences appear under 4+ types
     ("Bus analyzer shows repeated command retries" is variously a chat_message, lab_notebook, release_note, telemetry_summary).
   - `belief_holder` is round-robin: the same official-position sentence is attributed to six different people (P01–P07).
   - Timestamps are linearly spaced with one constant gap per case (C01: 12097 s) and carry microsecond fractions.
   - The self-review's shortcut audit is undermined: majority-vote over near-duplicate records recovers most answers,
     and type/holder fields carry no signal a provenance-aware system could use.
   Exp08 has the same unique-text ratio (0.58 vs 0.62), so this is the 08/09 generator's style, but exp09's causal task
   depends far more on per-record semantics than episode membership does.
4. **Gold answers are mostly generic instructions.** Only 30 distinct `expected_claims` strings across 133 queries.
   The 55 `single_memory_overclaim` queries share one answer ("Usually no; interpret it according to its role…"); the 10
   `causal_evidence` queries share "Use contemporaneous evidence…"; the 10 `historical_causal_belief` queries share
   "Report the early working explanation separately…" without saying what the early belief in each case was. The 25
   `distractor_resistance` queries contain the word "background" in the question itself. `must_preserve_scope` is true on
   all 133 queries; only 3 have `forbidden_claims`. Roughly 40 queries (Q001–Q053 minus the generic ones) carry case-specific gold.
5. **No relations at all.** `derived_from`, `supersedes`, `contradicts`, `duplicates` are empty on all 525 records, even
   though M0343/M0344 (official positions) and M0345 (retrospective) directly contradict objective traces. The
   provenance-aware weighting the self-review calls a requirement has nothing to key on.
6. Perturbations are a plan only; no variant corpora are materialized (same as exp08).
7. Manifest lacks file checksums; recommend adopting exp10's `files[]` sha256 format.

---

## Harness note
Neither corpus loads through `benchmark/corpus_loader.py` (expects `id`/`status`/`timestamp`; fails with `KeyError('id')`),
and `benchmark/run_exp05.py` expects `subject_text`. There is no runner for exp09/exp10 yet; the exp05 runner would need
a small adapter (memory_id -> corpus_id, drop subject_text) plus, for exp10, delivery-sequence support.

## Recommended fixes
- Exp10: dedupe the four query blocks (or make each of the ten a distinct question), link Q041–060 and Q111–120 to their
  memories, decide on the evaluative-clause leakage, document R10's third pass and the control/distractor definition.
- Exp09: regenerate `causal_evidence.json` from content (every claim non-empty, no support/contradict overlap), rewrite
  the corpus so each record is a distinct artifact with a memory_type and belief_holder that match its content, add
  `contradicts`/`derived_from` edges for official/retrospective records, write per-case gold for the belief and evidence
  queries, and add manifest checksums.
