# Self-Review — Experiment 06 (Stage 8)

## Audit method

Two passes were run against the generated bundle before packaging:

1. **Graph correctness** — a validation script (embedded in `README.md`, "How to validate")
   confirms every `derived_from` edge resolves to a real `memory_id`, every query's
   `relevant_memory_ids` resolve to real memories, and no `memory_id`/`claim_id` collides.
   Separately, `ultimate_evidence_roots` was checked against hand-computed expectations for one
   instance per family (see the worked traversal outputs used while writing `provenance_bible.md`):
   cascade → single root at every hop; fan-out at n=25 → still one root; convergent → three roots;
   circular (cyclic) → zero roots with `ultimate_evidence_roots_note` set; root-substitution World A
   → one root repeated across all 5 citers, World B → five distinct roots. All matched expectation.
   Corpus-wide counts were cross-derived two independent ways (once from `truth_state.json`'s
   summary counters, once by hand-summing per-family construction) and reconciled exactly
   (125 evidence roots, 15 cycle members, 21 no-root claims split 6 injected-unsupported + 15
   cycle-member, 5 tombstoned roots, 25 reentry nodes, 5 contradictions — see `provenance_bible.md`).

2. **Narrative/adversarial-soundness audit** — a manual read of a sample from each family's
   generated text, checking specifically for exactly the kind of accidental leak the self-critique
   questions below ask about. **This pass found a real defect**: the initial generator wrote
   testing-scaffold labels (`cycle_member`, `historically_sourced`, `root_inaccessible`,
   `reingested_model_output`, `provenance_dropped_in_later_derivative`, `partial_provenance`)
   directly into the exposed `memories.jsonl` `tags` array — a field the blind-run convention does
   *not* strip (only `_oracle` is stripped, per the exp03/04 `manifest.json` convention this bundle
   follows). A system could have "detected" every citation cycle in the corpus by string-matching
   the tag `cycle_member` instead of walking the `derived_from` graph, which would have made the
   `circular` family's central test trivial and uninformative. **This was fixed** before packaging:
   these labels now live under `_oracle.dev_flags` only (see `scripts/exp06_generation/generate_corpus.py`,
   and the regenerated `memories.jsonl` — zero occurrences of any of the six labels remain in any
   memory's exposed `tags` field, verified programmatically). This is exactly the failure mode
   self-critique question 12 warns about, and it is reported here rather than silently corrected
   without mention, per the task's instruction not to silently truncate/hide gaps.

## Experiment-specific self-critique (spec §12)

**1. Which five cases most clearly distinguish citation count from evidence independence?**
The P06-A fan-out triple (`fanout_n` ∈ {1, 5, 25} on one root — independent count stays 1 while
document count spans a 25x range); the `root_sub` World A/B pair (5 documents in both worlds, 1
root vs. 5 roots); the `hidden_root` family (2 authored, non-cross-citing, differently-worded
reports that read as independent but share one unattributed ops-channel root); the `convergent`
family as the positive control (3 documents, genuinely 3 roots — proves the benchmark doesn't just
reward "always answer 1"); and the cyclic `circular` instances (3 mutually-citing documents, 0
independent roots — proves citation count and evidence count can diverge in *either* direction,
not just the "many copies, one root" direction).

**2. Could a system succeed by simply preferring the oldest source?**
Partially, and this is a real limitation worth flagging rather than hiding. Every evidence root in
this corpus has `day_offset = 0` relative to its instance's base date, and non-root nodes always
have a strictly later `day_offset` (the one exception, `disappearance`'s tombstoned root, is offset
*earlier* still, at -60 days, which an oldest-source heuristic would also get right). So a naive
"trust whichever cited memory has the earliest `event_time`" heuristic would correctly answer most
**9.1 root-tracing** queries in this bundle. It would *not* help with independence counting (9.2):
oldest-timestamp alone can't distinguish `fanout` (1 root) from `convergent` (3 roots) since both
have roots at the earliest timestamp in their cluster; it fails `circular`'s cyclic instances
outright (there is no valid root to be "oldest" toward — all three nodes are comparably early and
none is correct); and it is irrelevant to unsupported-claim detection (9.4) and reentry (9.12/P06-G)
provenance questions, which turn on graph structure and node semantics, not recency. **v0.2 should
add non-root distractor memories with artificially early timestamps** to close this gap for 9.1
specifically; documented here rather than fixed silently, per the task's scale-vs-completeness
guidance to prioritize finishing all stages over open-ended polishing.

**3. Could a system succeed by treating every source type as one evidence root?**
No — this shortcut is actively falsified by the `fanout` family. A "count distinct `memory_type`
values among citing documents" heuristic would report up to 9 distinct types across a 25-descendant
fan-out cluster (this bundle cycles through 20 type/author combinations), wildly overcounting a
true independent-root count of 1. It would coincidentally get `convergent` and `root_sub` World B
right (their independent roots do happen to use distinct source types: sensor_log, scada_log,
technician_note, test_bench_report, weather_station_log), but "coincidentally right on the positive
controls, badly wrong on the central adversarial case" is exactly the failure profile this
subfamily is designed to catch.

**4. Are supposedly independent roots genuinely independent?**
Structurally yes — in `convergent` and `root_sub` World B, the root nodes have no `derived_from`
edges among themselves or to a common ancestor (each `is_evidence_root=true` with `derived_from: []`
independently). Narratively, independence is constructed via different data paths (Thornfield's own
telemetry vs. the customer's own SCADA historian, which the text states explicitly has "no data
path shared with Thornfield telemetry"), different observer types (automated system vs. unprompted
human), and in `root_sub` World B, five distinct source types/instruments. This is asserted in the
prose, which is honest for a benchmark (the ground truth needs to be legible somewhere) but see
question 7 below for the tradeoff that creates.

**5. Are any hidden shared roots accidentally revealed by identical wording?**
No for `hidden_root`'s two branches — `path1_note` reads "heard from the ops channel that some fleet
units are seeing dropouts," `path2_note` reads "saw the same ops-channel mention of relay dropouts,"
and the two postmortems (`reportA`/`reportB`) are independently worded per-site. Neither ever
quotes `E1` verbatim. Yes for `root_sub` World A, but by design, not accident: its five descendant
copies are explicitly labeled "copy 1" … "copy 5" in-text, because World A's whole purpose is to be
the unambiguous "many-copies-of-one-root" baseline the P06-B comparison measures against — making it
*too* easy to spot as duplicative is the correct adversarial shape for a baseline, not a flaw.

**6. Are citation cycles detectable only because of metadata labels?**
This was true of the initial build and is the defect described in "Audit method" above. After the
fix, cycle detection requires actually walking `derived_from` (A→C, B→A, C→B) — the `dev_flags`
oracle field still names cycle members for grading, but nothing in the exposed record does.

**7. Do summaries accidentally name their root sources too explicitly?**
Mostly no. `cascade`/`depth_chain` summaries describe the underlying event, not "per E1" — they say
things like "consistent with field inspection and the originating sensor log" without quoting the
sensor log's `memory_id`. The one deliberate exception is `contradiction`'s "D" node, which says
"per the {date} telemetry (E7)" — but that's intentional: the point of that family is that the
*citation* is explicit and correct while the *content* still contradicts what's cited, so the
citation needs to be legible for the contradiction to be checkable at all.

**8. Does graph depth correlate with truth or falsehood?**
No. `depth_chain` (the only family where depth is a manipulated variable) holds every edge intact
at every depth (1/2/4/8) — the claim is equally true and equally traceable regardless of depth
(Control D). Falseness/unsupportedness is controlled by a completely separate variable
(`unsupported` family's injected clause), decoupled from depth on purpose so a system can't learn
"deep chains are where the false claims hide" as a shortcut.

**9. Can provenance be recovered from content alone where it is supposed to be hidden?**
For `disappearance`'s tombstoned roots, no — the exposed `text` is a fixed tombstone stub with no
content-derived hints about what the original measurement said; only `_oracle.archived_text_dev_only`
(stripped in blind runs) has it. Descendants (`note`, `report`) preserve a paraphrase of the
original finding, so the *claim* survives even though the *root's own text* doesn't — which is the
intended, realistic shape of source disappearance (per Invariant 06-F, the correct behavior is
representing this as reduced-confidence knowledge, not fabricating or refusing to answer).

**10. Do any missing-lineage cases secretly contain enough context to reconstruct the missing edge
deterministically?**
Yes, deliberately, in `partial_loss`: `late` alone only cites `E1`, but `mid` (a sibling instance in
the same fact cluster) cites both `E1` and `E2`, so a system that reads the whole fact cluster
*can* reconstruct that `E2` also bears on the claim. This is intentional — the two `partial_loss`
queries are written to test exactly this distinction (`required_source_roots=[E1]` for the
direct-citation reading of `late` alone, vs. `required_source_roots=[E1,E2]` for the
corpus-wide completeness reading) rather than testing genuinely unrecoverable information, which is
`disappearance`'s job instead.

**11. Does the benchmark distinguish "unknown lineage" from "no supporting evidence"?**
Yes, and they are kept in different families on purpose: `disappearance` (P06-H) is "lineage is
known, but the root can no longer be inspected" (`required_source_roots` is non-empty,
`should_abstain=true` only on the inspectability sub-question, not on origin); `unsupported`
(P06-F/G) is "no lineage exists for this specific clause at all" (`required_source_roots=[]`,
`expected_independent_root_count=0`). The `circular` family adds a third, related-but-distinct
state: "lineage exists but is self-referential and therefore contributes zero net evidence."

**12. Are unsupported additions marked only in hidden ground truth rather than by suspicious
wording?**
Largely yes, by design — "because of a known firmware bug in the pump controller" is a plausible,
confidently-worded clause, not hedged or flagged in prose (the hidden ground truth is
`claim_lineage.json`'s `support: []` entry, not a tell in the text). The broader tag-leak defect
found in this review (see "Audit method") was the same category of mistake applied to a different
family (`circular`) and has been corrected.

**13. Can a vector-search system retrieve the correct documents but still fail the actual
provenance task?**
Yes, and this is close to the central point of the whole experiment. In `fanout`, a retrieval
system will find all n descendants (they are lexically and semantically near-duplicates of each
other) with no difficulty, and can still get the independence count (9.2) completely wrong by
reporting confidence proportional to n. In `hidden_root`, retrieval of both `reportA` and `reportB`
is easy (they're both clearly about the same relay-dropout event); recognizing they share a root
requires walking `derived_from`, which retrieval alone doesn't do.

**14. Which test best demonstrates provenance destruction during consolidation?**
`partial_loss`'s `late` node: a wiki summary written well after the original technical note, which
silently drops one of the two roots the earlier note carried, during ordinary editorial
consolidation (not malice, not an injected clause — just what tends to happen when someone
summarizes a summary later without re-checking the original citations).

**15. Which case would most likely fool a sophisticated graph-based memory architecture?**
`hidden_root`, specifically. A graph-based system that correctly walks `derived_from` edges within
each report's own branch will still get this right eventually — but a system that deduplicates or
merges near-identical citation subgraphs *by node similarity* rather than by literal shared-node
identity could plausibly treat `path1_note` and `path2_note` as two separate, coincidentally-similar
observations (since they're worded differently and sit at different sites) rather than recognizing
they both terminate at the literal same `E1` node — the failure mode is architectural
over-generalization at exactly the step where exact-identity matching matters most.

## Benchmark verdict

To pass Experiment 06, a memory architecture needs, at minimum:

- **An explicit, walkable derivation graph**, not just semantic similarity between records — the
  `derived_from` field (or an architectural equivalent) must be preserved through every
  transformation, consolidation, and paraphrase, and must remain queryable independently of
  retrieval ranking.
- **A traversal operation that resolves to evidence roots**, distinct from "the most recent thing
  that cites this" or "the most similar-looking document" — including correct behavior at depth
  (no silent truncation), across fan-out (no confidence inflation by count), and through cycles (no
  infinite loop, and a return value of zero net new evidence, not a crash or a fabricated root).
- **Claim-level, not only document-level, provenance** — a single memory can contain both
  fully-sourced and entirely unsourced assertions, and a system that scores support at the document
  granularity will systematically over-trust the unsourced portions of otherwise well-cited
  documents.
- **A distinction between "new memory object" and "new evidence"** — reingested or model-generated
  content must not silently increment an independent-evidence counter just because it was written
  down again with a new ID.
- **Three-way handling of source accessibility** — origin known vs. currently inspectable vs.
  strength of surviving support are different questions with different correct answers, and
  collapsing them (either into blind trust or into total rejection) is a failure on this benchmark
  even when the system's retrieval and paraphrase-matching are otherwise excellent.

A system can pass point-retrieval and paraphrase-recognition benchmarks entirely while failing
every one of these — which is the reason this experiment exists as its own axis rather than being
folded into retrieval-quality scoring.
