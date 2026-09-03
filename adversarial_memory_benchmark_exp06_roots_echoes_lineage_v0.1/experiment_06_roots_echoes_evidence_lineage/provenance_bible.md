# Provenance Bible — Experiment 06

This is the explicit evidence-topology definition required by Stage 2. It was authored as data
(`generate_corpus.py`, function `build_*` per family) **before** any memory text was rendered —
every `Node(...)` call below declares its type, its `derived_from` edges, its evidence-root status,
its retrievability, and (where relevant) its unsupported clause, and the prose text is a template
filled in from that already-fixed topology, never the other way around. This file is the
human-readable restatement of that same topology, cross-checked against the generated
`provenance_graph.json` counts.

Corpus-wide totals (from `truth_state.json`): 413 memories, 419 claims, 88 fact instances,
125 evidence-root memories, 15 cycle-member memories, 21 claims with no supporting root (6 are
injected-unsupported clauses in the `unsupported` family; the remaining 15 are the three cyclic
`circular` instances' A/B/C nodes, which correctly have no external root — see Invariant 06-C),
5 tombstoned/inaccessible roots, 25 reentry-chain nodes, 5 provenance-contradiction nodes.

## Evidence roots

An **evidence root** is any memory with `_oracle.is_evidence_root = true` in `memories.jsonl`
(equivalently, `provenance_graph.json` nodes whose own `ultimate_evidence_roots` is `[self]`).
Every evidence root is a primary observation: a machine-generated sensor/SCADA/weather log, or a
human's own on-site physical inspection recorded in their own words, never a restatement of someone
else's claim. There are 125 such memories across the corpus. No evidence root has a non-empty
`derived_from`.

## Node types (`_oracle.node_type`, mirrors §2's required distinction)

| node_type | Meaning | Used by |
|---|---|---|
| `evidence_root` | primary observation, no upstream derivation | all families |
| `primary_observation` | a human's direct, first-hand inspection anchored to a root event (not itself a root, but not a restatement either) | `cascade`, `hidden_root` (path notes) |
| `interpretation` | a reader's judgment about what an observation means | `cascade`, `hidden_root`, `circular`, `partial_loss` |
| `derived_summary` | a document that consolidates one or more upstream claims | `cascade`, `convergent`, `partial_loss`, `unsupported`, `root_sub` (World B), `reentry` |
| `transformed_claim` | a claim that has been paraphrased/reworded while being passed along | `cascade`, `fanout`, `hidden_root`, `depth_chain`, `circular` (acyclic), `contradiction`, `root_sub` (World A) |
| `copied_claim` | near-verbatim restatement one hop downstream | `cascade` (S3), `reentry` (R1) |
| `quoted_claim` | (reserved; represented in this bundle via `copied_claim`/`transformed_claim` with explicit "per X" wording — see note below) |
| `model_generated` | output of the internal AI summarizer, `adds_new_evidence=false` by construction | `reentry` |
| `reingested` | a `model_generated` output pasted back in as if it were an independent new source | `reentry` |

Note on `quoted_claim`: rather than introduce a fourteenth memory-type/node-type pairing purely for
label completeness, direct quotation is represented through wording ("per Priya's field note...",
"consistent with the wiki writeup (B)...") on `transformed_claim`/`copied_claim`/`interpretation`
nodes, since in this corpus a quoted claim and a lightly-reworded claim carry the same provenance
consequences (Invariant 06-A applies identically to both). A stricter future revision could split
`quoted_claim` out as its own `node_type` if a harness needs to test quotation-fidelity separately
from paraphrase-fidelity.

## Per-family topology (as authored, before text generation)

### `cascade` (§06.1) — 8 instances, 6 memories each
```
E1(evidence_root) -> N1(primary_observation) -> C1(interpretation)
   -> S1(derived_summary) -> S2(transformed_claim) -> S3(copied_claim)
```
Single root, strictly linear, depth 5. `ultimate_evidence_roots` for every node = `[E1]`.

### `fanout` (§06.2, P06-A) — 6 instances at fanout=4, plus 3 instances at fanout=1/5/25
```
E1(evidence_root) -> note(primary_observation) -> desc0..desc_{n-1}(transformed_claim, n in {1,4,5,25})
```
All descendants derive directly from `note`, which derives from `E1`. `ultimate_evidence_roots` for
every descendant = `[E1]` regardless of `n` — the trap is that descendant *count* varies by 25x
while independent evidence stays at 1.

### `convergent` (§06.3, Control B) — 6 instances, 4 memories each
```
E1(evidence_root, Thornfield telemetry), E2(evidence_root, customer SCADA),
E3(evidence_root, unprompted technician touch) -> C(derived_summary)
```
Three roots are constructed to be genuinely instrument/observer-independent: different data path
(Thornfield backend vs. customer's own historian), different observer (automated vs. human), and
the human observation is explicitly unprompted ("unaware of any alert"), which rules out the
technician's note being downstream of the same alert that generated E1/E2.

### `hidden_root` (§06.4) — 6 instances, 5 memories each
```
E1(evidence_root, unattributed ops-channel message)
   -> path1_note(interpretation, site X) -> reportA(transformed_claim, site X)
   -> path2_note(interpretation, site Y) -> reportB(transformed_claim, site Y)
```
`reportA` and `reportB` are authored by different people at different sites and never cite each
other — lexically they look independent. Both trace to the same `E1`. The shared root is
deliberately *not* named identically in both branches (site X's note says "heard from the ops
channel"; site Y's note says "saw the same ops-channel mention") to avoid trivial lexical detection
(self-critique question 5, §12).

### `depth_chain` (§06.5, P06-C) — 3 topic sets × depths {1,2,4,8} = 12 instances
```
D0(evidence_root) -> D1 -> D2 -> ... -> D_depth   (all transformed_claim, strictly linear)
```
Every edge is intentionally preserved (Control D, "deep but complete lineage") — this family
isolates the *depth* variable from provenance loss, which is tested separately in `partial_loss`.

### `partial_loss` (§06.6, Control E) — 6 instances, 4 memories each
```
E1(evidence_root, current-draw telemetry), E2(evidence_root, field-note inspection)
   -> mid(derived_summary, cites both E1 and E2)
E1 -> late(derived_summary, written later, cites only E1)
```
`mid` and `late` are siblings, not a chain — `late` does not derive from `mid`. This isolates
"what does *this specific memory* cite" from "what does the corpus as a whole retain," which is
exactly the 9.6 distinction the spec requires (`required_source_roots` differs between the two
per-node queries even though they describe the same real-world event).

### `unsupported` (§06.7, Control F/G) — 6 unsupported instances + 2 fully-grounded siblings
```
A(evidence_root, "pump stopped at 14:02:00Z"), B(evidence_root, "coolant temp rose from 14:03Z")
   -> S(derived_summary): two supported clauses (from A, from B)
                            + one unsupported clause ("because of a known firmware bug...")
```
This is a direct instantiation of the spec's own §06.7 worked example. The unsupported clause has
its own `claim_id` with `support: []`, sitting inside the same memory as two fully-supported claims
— Invariant 06-E requires a system to keep these three claims separately scored. The two
Control-F sibling instances use the same A/B roots but omit the firmware sentence entirely.

### `circular` (§06.8, P06-E) — 5 cyclic instances + 5 acyclic siblings
```
Cyclic:   A(interpretation) -> derived_from C
          B(interpretation) -> derived_from A
          C(transformed_claim) -> derived_from B
          (A -> C -> B -> A: a 3-cycle, no node outside the cycle)
Acyclic:  root(evidence_root, field-note teardown) -> A -> B -> C   (strictly linear)
```
The acyclic sibling is P06-E's "before" state; the cyclic instance is the "after" state with one
backward citation added (C now points back into the loop instead of terminating at an external
root) and the external `root` node removed. Wording of A/B/C is held nearly identical between the
two variants. `ultimate_evidence_roots` for cyclic A/B/C is computed as `[]` with an explicit
`ultimate_evidence_roots_note` flagging cycle membership (Invariant 06-C: longer cycles must not
look stronger; here the cycle length is fixed at 3 throughout).

### `contradiction` (§06.9) — 5 instances, 2 memories each
```
E7(evidence_root, "unit ONLINE throughout, no fault codes") -> D(transformed_claim, contradicts_root=true)
```
`D.derived_from = [E7]` and `D.contradicts = [E7]` simultaneously — the metadata says D is sourced
from E7, but D's text ("unit went OFFLINE for six hours") materially conflicts with E7's content.
This is a deliberately small set (5 instances, per the spec's "include a few controlled cases"
instruction, since full contradiction-auditing is Experiment 15's primary topic).

### `root_sub` (§06.10, Control C, P06-B) — 4 paired World A / World B instances
```
World A: root(evidence_root) -> r0..r4 (5x transformed_claim, transformed_claim, all citing root)
World B: root0..root4 (5x evidence_root, independently instrumented)
             -> conv(derived_summary, cites all 5)
```
Held constant between A and B: claim wording pattern, document count (5), subject unit/site, base
date. Varied: whether the 5 documents share one root or are themselves 5 roots. This is the
cleanest isolated test of the experiment's central research question.

### `disappearance` (§06.11, P06-H) — 5 instances, 3 memories each
```
root(evidence_root, vendor test-bench report, retrievable=false, event 60 days before the rest)
   -> note(interpretation) -> report(transformed_claim)
```
`root`'s exposed `text` field is replaced with a tombstone stub at generation time; its real content
is preserved only under `_oracle.archived_text_dev_only` (development-only ground truth — a blind
run must not expose this). `note` and `report` remain fully retrievable and still name `root` by
`source_id`, so the lineage edge itself is never severed — only the root's content is withheld.

### `reentry` (§06.12, P06-G) — 5 instances, 5 memories each
```
E1(evidence_root) -> S1(derived_summary, postmortem)
   -> M1(model_generated, "Thornfield Assist summary", adds_new_evidence=false)
   -> M2(reingested, wiki page pasted from M1, adds_new_evidence=false)
   -> R1(copied_claim, status email citing the wiki page)
```
Every node from S1 onward is flagged `adds_new_evidence=false` in `provenance_graph.json`. The
whole 4-hop chain still resolves to the single `E1` root — a system that treats `M1`'s or `M2`'s own
`memory_id`/`source_id` as evidence of a new observation fails Invariant 06-A in its sharpest form.

## Never-retroactive-invention discipline

No family above was adjusted after `memories.jsonl` was first generated except two narrow,
topology-preserving fixes made during validation (both changed *labels*, not graph structure, and
both are visible in the generator's git history within this branch):

1. `partial_loss`'s second evidence root was originally marked `retrievable=false`, which
   conflated "this derivative dropped a citation" (§06.6) with "this source is inaccessible"
   (§06.11). It was corrected to `retrievable=true` with a `provenance_dropped_in_later_derivative`
   tag instead, so the two subfamilies test genuinely different failure modes.
2. `disappearance`'s tombstoned root originally kept its full observational text in the exposed
   `text` field with only an oracle flag marking it inaccessible. It was corrected to a real
   tombstone (`text` replaced with a stub; original content moved to `_oracle.archived_text_dev_only`)
   so that P06-H is testable against systems that only see exposed fields, not just against systems
   given the development oracle.

Both fixes were made before Stage 5 expansion and are reflected identically across all 88
instances of their respective families — no instance-specific provenance was hand-patched.
