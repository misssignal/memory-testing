# Experiment 06 — Roots, Echoes, and Evidence Lineage

Story: **Thornfield Sentinel** (`thornfield_sentinel`) — an industrial-IoT incident-lineage arc.
See `story_bible.md` for the world/cast and `provenance_bible.md` for the explicit evidence
topology that was authored before any memory text.

Central research question: *can the system explain where a claim came from, and distinguish
genuinely independent corroboration from many descendants of the same evidence root?*

## Scale

- **413 memories**, **419 claim-level provenance records**, **128 ground-truth queries**
- **88 fact instances** across the 12 required adversarial subfamilies (§06.1–§06.12)
- This sits inside the spec's preferred 350–750 range (target was "200–1,000, preferably
  350–750"), reached through genuine narrative repetition (the same *kind* of incident recurring
  at different sites/units — not mechanical duplication; see `story_bible.md`, "narrative thread").
- Query categories: all 8 of §9.1–§9.8 are represented (root tracing 26, independence 34, path
  reconstruction 13, unsupported-claim detection 14, circular citation 10, provenance completeness
  11, source-loss 15, comparison 5).

## Experimental map (Stage 3)

| Family | Spec § | Graph motif | Manipulated variable | Control | Expected result | Naive failure mode | Metric(s) |
|---|---|---|---|---|---|---|---|
| `cascade` | 06.1 | linear 6-hop chain, single root | — (fixed depth 5) | — | root recovers to `[E1]` at every hop | citing the nearest upstream hop as "the source" instead of walking to the root | Root Recovery Accuracy, Provenance Path Accuracy |
| `fanout` | 06.2, P06-A | 1 root → n descendants, n ∈ {1,4,5,25} | descendant count | Control A (many descendants, one root) | independent-root count stays 1 for all n | scoring confidence/independent-evidence-count proportional to n | Derivative Inflation Rate, Fan-out Robustness |
| `convergent` | 06.3 | 3 independent roots → 1 conclusion | — | **Control B** (positive control) | independent-root count = 3 | under-counting to 1 out of habit from seeing many fanout cases elsewhere in the corpus | Independent Evidence Count Error |
| `hidden_root` | 06.4 | 1 root → 2 divergent, non-cross-citing paths → 2 "independent-looking" reports | — | — | independent-root count = 1, not 2 | trusting apparent independence (different authors/sites/no cross-citation) as proof of independence | Independent Evidence Count Error |
| `depth_chain` | 06.5, P06-C | linear chain, depth ∈ {1,2,4,8} | derivation depth | **Control D** (deep, complete) | root recovery does not degrade with depth | truncating lineage walk at a fixed hop budget | Depth Robustness, Root Recovery Accuracy |
| `partial_loss` | 06.6 | 2 roots → sibling "mid" (both cited) / "late" (one cited) | citation completeness of the *specific memory* vs. the *corpus* | **Control E** (shallow, incomplete) | "what does this memory cite" ≠ "what does the corpus retain" | conflating a sibling's fuller citation with this memory's own, and vice versa | Provenance Path Accuracy |
| `unsupported` | 06.7, P06-F | 2 roots → 1 summary with 2 supported + 1 unsupported claim | presence of the unsupported clause | **Control F** (fully supported) vs. **Control G** (partially unsupported) | supported clauses stay supported, unsupported clause stays unsupported, independently | document-level scoring that lets sourced neighbors "launder" the unsupported clause | Unsupported Claim Detection, Claim-Level Provenance Accuracy |
| `circular` | 06.8, P06-E | 3-node cycle vs. acyclic 3-hop chain to a real root | presence of a cycle | — | cyclic: independent-root count 0, `must_detect_cycle=true`; acyclic: count 1 | treating mutual citation as multiplying evidence strength | Circularity Detection Rate |
| `contradiction` | 06.9 | root → 1 node whose text contradicts the root it cites | — | — | citing D's own text should not be trusted over E7's, given the mismatch | inheriting the root's credibility for D's contradicting claim just because `derived_from` points at it | Provenance Hallucination Rate |
| `root_sub` | 06.10, P06-B | World A (1 root, 5 copies) vs. World B (5 roots, 1 summary) | root count, holding document count constant | **Control C** (mixed, here realized as the A/B pair itself) | World B strictly stronger despite equal document counts | scoring both worlds identically because both surface 5 documents | Independent Evidence Count Error |
| `disappearance` | 06.11, P06-H | root tombstoned, descendants intact | root retrievability | — | 3 distinct answers: origin known, not currently inspectable, reduced-but-nonzero surviving support | collapsing the 3 questions into one (either full trust or total rejection) | Provenance Hallucination Rate, Root Recovery Accuracy |
| `reentry` | 06.12, P06-G | root → summary → AI output → reingested copy → report | reingestion depth | — | independent-root count stays 1 across all 4 downstream hops | treating the reingested memory's own `memory_id` as a new observation | Provenance Hallucination Rate, Independent Evidence Count Error |

## Files

```
README.md                      this file
story_bible.md                 Stage 1 arc selection + narrative world (Stage 2, narrative half)
provenance_bible.md            Stage 2, explicit evidence-topology half (per-family graph definitions)
self_review.md                 Stage 8 self-review + §12 self-critique + benchmark verdict
memories.jsonl                 413 memory records (schema: ../schema.json, memory_record)
truth_state.json               story/world facts, family legend, invariant summary, oracle ID lists
provenance.json                flat memory_id -> fact_id -> source_id mapping (exp03/04-compatible shape)
provenance_graph.json           full per-node graph: node_type, derived_from, ultimate_evidence_roots,
                                adds_new_evidence, retrievable, cycle flags (spec §6)
claim_lineage.json             claim-level provenance: one record per claim, with root + path support (spec §6)
queries.jsonl                  128 ground-truth queries (schema: ../schema.json, query_record, extended)
sources.md                     one row per memory's originating artifact
ingestion_chronological.jsonl  memory_ids ordered by event_time
ingestion_shuffled.jsonl       memory_ids in a fixed random order (seed 7)
ingestion_late_arrival.jsonl   13 fact instances' evidence roots deliberately ingested after most of
                                their own descendants (tests retroactive provenance correction)
perturbations/perturbation_plan.json   P06-A..H, each grounded in real fact_id/memory_id references
```

## Status (Stage reached)

**All 8 generation stages were completed** for this v0.1 bundle:

1. Candidate selection — done (`story_bible.md`, "Stage 1").
2. Story bible + provenance bible — done, and written *before* corpus expansion (see
   provenance_bible.md's "never-retroactive-invention discipline" section for the two narrow
   label-level exceptions made during validation, both applied uniformly across every instance of
   their family).
3. Experimental map — done (table above).
4. Seed corpus — superseded by full expansion below; the same generator produced both.
5. Full expansion — done: 413 memories, within the preferred 350–750 band.
6. Controlled perturbations — done: `perturbations/perturbation_plan.json` covers P06-A through
   P06-H, each pointing at real instances in this bundle rather than describing dimensions in the
   abstract.
7. Ground truth and queries — done: 128 queries covering all 9 query-category groups (§9.1–9.8),
   with `required_source_roots`, `expected_independent_root_count`, `expected_lineage_paths`,
   `must_detect_cycle`, and `must_report_missing_provenance` populated per spec §7's worked example.
8. Self-review — done: see `self_review.md`.

**What is intentionally left for a v0.2 pass**, honestly flagged rather than silently omitted:

- The corpus sits at 413 memories / 128 queries — comfortably inside spec's preferred range, but
  a future pass could push toward the 750-memory ceiling by adding more `depth_chain` topic sets
  and a wider `hidden_root` variety (e.g. a 3-way hidden shared root, not just 2-way).
- `quoted_claim` is not materialized as its own distinct `node_type` (see provenance_bible.md's
  note) — a stricter revision could split quotation-fidelity out from paraphrase-fidelity as an
  independently-testable axis.
- Perturbation pairs are *embedded* in the main corpus (e.g. World A/B live side by side as real
  fact instances) rather than shipped as a separate before/after diff format; `perturbation_plan.json`
  documents which real IDs form each pair. A harness wanting isolated single-variable ablation runs
  would filter `memories.jsonl` by `_oracle.fact_id` using the IDs listed there.
- No `checksums.sha256.json`-verified regeneration test has been run through the shared
  `benchmark/` harness itself (that harness currently targets its own `fake_becca` corpus format;
  wiring exp06 into it is out of scope for this additive, isolated bundle).

## Hidden fields

`memories.jsonl` contains an `_oracle` object for benchmark development, matching the exp03/04
convention. Strip `_oracle` for blind runs. `_oracle.archived_text_dev_only` is especially
sensitive for the `disappearance` family — it holds the tombstoned root's real content, and its
presence in a blind run would trivially solve the source-disappearance queries by inspection.

## How to regenerate

The full bundle is produced by four deterministic Python scripts (seeded, no external
dependencies beyond the standard library), checked into the repository at
`scripts/exp06_generation/` (one level above this bundle, not inside the zip — the bundle itself
ships only the generated data, matching the exp03/04 packaging convention). Run in this order from
that directory:

```bash
EXP06_OUT=/tmp/exp06_build python3 generate_corpus.py        # memories, provenance_graph, claim_lineage
python3 generate_supporting.py                               # ingestion_*.jsonl, sources.md, truth_state.json, provenance.json
python3 generate_queries.py                                   # queries.jsonl
python3 generate_perturbations.py                             # perturbations/perturbation_plan.json
```

`generate_supporting.py`, `generate_queries.py`, and `generate_perturbations.py` read from
`/tmp/claude-0/exp06_build` by default (matching `generate_corpus.py`'s default `EXP06_OUT`); set
`EXP06_OUT` consistently, or edit `BUILD_DIR` at the top of each script, if regenerating elsewhere.
Re-running all four with the same `SEED = 20260614` reproduces this corpus byte-for-byte.

## How to validate

```bash
python3 - <<'EOF'
import json
mems = [json.loads(l) for l in open("memories.jsonl")]
qs = [json.loads(l) for l in open("queries.jsonl")]
prov = json.load(open("provenance_graph.json"))["nodes"]
claims = json.load(open("claim_lineage.json"))["claims"]
assert len(mems) == len({m["memory_id"] for m in mems}), "duplicate memory_id"
ids = {m["memory_id"] for m in mems}
for m in mems:
    for d in m["derived_from"]:
        assert d in ids, f"{m['memory_id']} derives from missing {d}"
for q in qs:
    for mid in q["relevant_memory_ids"]:
        assert mid in ids, f"{q['query_id']} references missing {mid}"
print(f"OK: {len(mems)} memories, {len(qs)} queries, {len(prov)} provenance nodes, {len(claims)} claims")
EOF
```
