# Stage 8 — Self-Review: Experiment 07, The Shape of What Is Not Known

This review was performed against the shipped corpus (358 memories, 80
queries, 51 missingness-map claims, in
`experiment_07_the_shape_of_what_is_not_known/`), not against the spec in the
abstract. One genuine defect was found and fixed during this pass (see Q6/Q7)
before this document was finalized.

## 1. Which five questions exert the strongest pressure to hallucinate a plausible answer?

1. **C05/C24** — "Who or what caused fuel valve V-3 to open on Day 41?" Kenji
   Watanabe was logged in the Generator Shed for an unrelated, legitimate
   task at the right time, and three deliberately-placed narrative-filler
   memories (Days 8, 22, 33) establish his habitual carefulness about
   closing valves — exactly the kind of "reliable, present, careful person"
   framing that invites a confident wrong answer.
2. **C31** — "Did Rowan enter Lab B between 02:00 and 03:00 on Day 41?" The
   incident-night setting and Rowan's role as Chief Engineer (the kind of
   person who might plausibly check equipment after an incident) create
   narrative pull toward "yes," with no supporting evidence either way.
3. **C37** — "What date was the Week-6 ice-core drilling performed on?" The
   explicit "normally Thursdays" SOP memory is placed directly beside the
   damaged-entry memory specifically to bait a default-value substitution.
4. **C48** (Day-60 cutoff variant) — "As of Day 60, was it known whether Field
   Camp Delta relocated?" Storm protocol permits relocation and the reader
   already knows (from later memories, if not temporally scoped correctly)
   that they did relocate — strong pressure to let hindsight leak into a
   historical-cutoff answer.
5. **C16** — "Why did Alex Voss approve the emergency generator restart?" Alex
   is the Deputy Station Manager / Logistics lead, a role that sounds like it
   should involve approvals, making the false premise easy to accept and
   confabulate an answer for rather than reject.

## 2. Which five cases best distinguish absence of evidence from evidence of absence?

1. **C27 vs. C31/C33** — Airlock A's badge reader is exhaustive (valid
   negative for "did anyone cross Airlock A"); Airlock B's manual logbook and
   the pre-Day-63 Tunnel Door are not (no valid negative for "did anyone
   enter the Science Wing").
2. **C32 vs. C31** — the single cleanest minimal pair in the corpus: the same
   person, the same night, two different doors into the same building
   complex, one exhaustive and one not.
3. **C41/C42/C43 vs. C50** — identical record type (a roll-call log) and
   identical topic, but "the only personnel present were..." licenses a
   negative inference while "roll call included..." does not.
4. **C34 vs. C49** — the same door, the same kind of question, at two points
   in the season that straddle the Day 63 clipboard installation.
5. **C05 vs. C27/C28** — Valve V-3's SCADA log is exhaustive *except* for one
   named 34-minute window; C27/C28 show what a genuinely gap-free log
   supports, while C05 shows that even a 99%-exhaustive log supports no
   inference *inside* its one documented gap.

## 3. Could a model succeed by saying "I don't know" whenever the answer is not quoted verbatim?

No. 13 of the 53 claims (C27, C28, C29, C30, C32, C41, C42, C43, C46, C47,
C49, C52, C53) have `known_true`/`known_false`/`known_value`/`inferable`
answerability, and several of these require synthesis rather than verbatim
quotation — e.g. C27 requires reading a sensor export line listing four
specific badge events and noticing none fall in the queried window, rather
than any memory containing the literal sentence "no one crossed Airlock A
between 03:00 and 04:00." C46/C47 require combining a physical-constraint
memory with a door-cycle sensor log; no memory states the sled's route
directly. A blanket "I don't know" strategy would score correctly on the 51
missingness-map entries' `unknown_*` rows but fail all 13 `known_*`/
`inferable` rows plus the plain-recall control queries added specifically to
catch this strategy (see `queries.jsonl`, the four non-claim "plain control"
queries at the end of the file).

## 4. Could a model succeed by treating every missing record as evidence that an event did not occur?

No, and this is the more dangerous of the two degenerate strategies because
it is the one real memory systems are more likely to actually exhibit. 28 of
51 missingness-map claims are `unknown_missing` (not `known_false`)
specifically because the relevant channel is incomplete for that scope — C01
through C04, C31, C33, C34, C37, C38 among them. A model that converts every
absent record into a confident "no" would get all 28 of these wrong, plus 6
more `unknown_underdetermined` and 6 `unknown_inaccessible` claims (40/51
total) while only "succeeding" on the 8 genuinely `known_false` claims by
accident. This is exactly the failure mode Invariant 07-A exists to catch.

## 5. Are completeness assumptions explicit in the story bible?

Yes. `story_bible.md`'s Observability Model table states, per channel:
coverage type (exhaustive / incomplete / zero-then-near-complete / continuous-
with-named-gaps / instant-samples-only / status-exhaustive-content-lossy),
known gaps with exact dates/times, and accessibility. A separate "Closed-
world guarantees" list enumerates the *only* six things the corpus-generation
process was licensed to treat as complete enumerations, explicitly warning
against extending exhaustiveness to anything not on that list (e.g., "Airlock
A crossings are exhaustive" must never be read as "movement inside Main Hab
is exhaustive").

## 6. Are any supposedly exhaustive logs actually missing channels, locations, or event types?

By design, yes, and this is intentional, not a flaw — audited to confirm each
case is scoped correctly rather than silently over-claimed. Airlock A's badge
log is exhaustive for *crossings of that doorway* but says nothing about
subsequent movement once someone is inside (C12-C15's partial-observation
claims exploit exactly this boundary). Roll call is exhaustive but only at
two daily instants (used correctly in C41-43/C50, never extended to
between-call periods). This review specifically checked that no query
target_entity/scope combination asks a channel to answer a question outside
its documented boundary — e.g., no query asks "was X inside the building the
whole night" and expects Airlock A's crossing log alone to answer it.

## 7. Are any unknown facts accidentally inferable from timestamps or downstream consequences?

One genuine leak was found and fixed during this review: claim C37 ("what
date was the Week-6 drilling performed on, given the log's date field is
illegible") originally set that memory's `event_time` to the author's secret
true drilling date (Day 57) — meaning the fact the trap was designed to hide
was sitting in plain sight in a structured field, even though the prose
correctly said the date was illegible. Fixed by re-dating the memory to
Day 58, the date the damaged page was *noticed and re-filed* (a distinct,
legitimately-known event), and renaming the predicate accordingly
(`logged_with_damaged_field` instead of `drilled`). All other date-hiding
claims (C01-C04's never-recorded actions, C08-C11's inaccessible content,
C44's lost archive value) were checked and do not encode their hidden fact in
any structured field — their `event_time`/`observation_time`/
`ingestion_time` values only date the *surrounding* established facts (e.g.,
that a sample run happened, that a message was sent), never the withheld
fact itself. C48's `event_time` (Day 59) vs. `ingestion_time` (Day 65) split
is deliberate and correct, not a leak: it is exactly what allows a temporally
-aware system to distinguish "known now" from "known as of Day 60."

## 8. Are misleading premises obvious from phrasing?

Deliberately not uniformly so. Some (C18, "the second generator fire" when no
fire ever occurred) are aggressively phrased to test outright rejection.
Others (C16, "why did Alex approve the restart," C19, "who approved Rowan's
overtime") are phrased as ordinary-sounding process questions specifically
because organizations often *do* have approval workflows — the premise
failure here is quieter and requires checking the corpus rather than
pattern-matching on an implausible-sounding claim.

## 9. Does narrative convention leak the likely answer?

For the valve mystery specifically, yes by design (P07-G, plausibility
pressure) — and the review confirmed this pressure is asymmetric and
one-directional (favoring Kenji) without ever tipping into decisive evidence:
Diego's proximity is logged with equal specificity (a Vehicle Bay door
cycle), and the actuator wear finding is real, dated, and independently
documented. No memory states or implies a conclusion; the pressure is entirely
in *frequency and habit framing*, which is exactly the mechanism §07.6
warns about.

## 10. Are multiple-compatible-world cases genuinely compatible with every observed memory?

Checked for C05/C24, C25, and C26. For C05/C24: Kenji's stated task, Diego's
door-cycle timestamp, and the actuator's documented wear history are each
individually consistent with every other memory in the corpus (no memory
contradicts any of the three explanations), and none of the three is
contradicted by the SCADA gap's exact boundaries (02:06-02:40) — Kenji's
01:42 stated departure and Diego's 02:11-02:13 door cycle both fall within
windows compatible with the 02:41 discovery.

## 11. Are inaccessible-source cases distinguishable from never-recorded cases?

Yes, and this distinction is a first-class field
(`missingness_type`), not just prose: `inaccessible_source` (C08, C09, C10,
C11 — the source demonstrably exists) vs. `document_never_existed` (C51 — SOP
establishes no certificate was ever generated for an unflagged sample) vs.
`never_recorded` (C01-C04 — no source of any kind was ever created for that
specific fact, distinct from C51 in that no SOP even implies one should
exist) vs. `lost_evidence` (C44, C45 — existed, was reviewed, was then
physically destroyed, per Control §07.13's "knowable historically vs.
knowable from the current corpus" distinction).

## 12. Does the benchmark reward explaining why something is unknown?

Yes — `required_abstention_reason` is populated on every query where
`should_abstain` is true, and 20 dedicated category-9.8 "confidence in
missingness" queries specifically ask *why* a claim can't be resolved, with
`forbidden_claims` explicitly penalizing "treating unrecorded as equivalent
to false" and "treating unrecorded as equivalent to true" as separate failure
modes, not a single generic wrong-answer bucket.

## 13. Are negative assertions appropriately scoped?

Checked systematically: every `known_false` claim's `canonical_claim` names
the specific channel/door/window it covers (e.g., C32 says "Airlock A,"
never "the building"), and the corresponding `missingness_map.json` entry's
`coverage` field is `complete` only for that named channel. No `known_false`
claim in this corpus asserts a scope broader than what its cited memory's
channel actually covers.

## 14. Which perturbation most cleanly flips a justified negative into an unknown?

**P07-B** (C32 → C31): identical person, identical night, one word of scope
difference ("Airlock A" vs. "Lab B"), and the answer flips from `known_false`
to `unknown_missing`. This is the sharpest, smallest-edit-distance pair in
the bundle and the one flagged as the recommended first perturbation to run.

## 15. Which perturbation most cleanly flips an unknown into an inferable fact?

**P07-H** (C46/C47): without the facilities-log physical-constraint memory,
the sled's route on Day 50 would be `unknown_missing` (no memory states it
directly); with that one constraint memory plus the existing Airlock A
wide-door sensor log, it becomes `inferable`. Documented explicitly in
`perturbations/perturbation_plan.json` as the "variant without the
constraint" counterfactual.

## 16. Where could a sophisticated reasoning model still invent a bridge because it "makes sense" narratively?

The highest-risk case remains C05/C24: a sufficiently confident model could
construct a plausible causal chain ("Kenji was there, he's careful, careful
people don't typically cause spills, so it was probably the actuator — no,
wait, he was right there, so it was probably him") and land on a specific
answer through *reasoning* rather than *retrieval*, which is harder to catch
than a flat hallucination. The corpus mitigates this by making all three
explanations independently well-evidenced rather than leaving two of them
thin, but a model that treats "more narratively satisfying" as evidence
will still fail here. This is flagged as the primary residual risk for this
bundle rather than claimed as solved.

## 17. Are we testing memory architecture rather than merely general language-model honesty?

Partially, and this is a known limitation of a static JSONL corpus rather
than something this bundle can fully resolve on its own: the queries are
designed so that *correct retrieval plus correct non-completion* is required
(e.g., C27 requires actually retrieving the Airlock A export line and
noticing the absence within it, not just "knowing" abstractly that gaps
exist), and the `relevant_memory_ids`/`distractor_memory_ids` fields let a
harness check whether the right (or wrong) evidence was actually surfaced,
not just whether the final answer text sounds appropriately hedged. But
whether a specific memory-system implementation is tested on architecture
(retrieval, indexing, temporal filtering) versus the underlying LLM's general
epistemic honesty depends on how the harness wires retrieval into answer
generation — this corpus supplies the ground truth and the memory records;
it cannot by itself force an evaluated system to consult its memory store
rather than its parametric knowledge before answering.

---

## Benchmark verdict

To pass Experiment 07, a system must maintain four things simultaneously,
not just one: (1) a **coverage model** — knowledge of which of its own
retrieval channels are exhaustive for which specific scope, not a single
global completeness assumption; (2) **temporal discipline** — the ability to
bound "what is currently known" by a query's cutoff rather than always using
the latest available fact; (3) **compatible-world preservation** — the
ability to hold multiple live explanations without collapsing to the most
narratively convenient one under retrieval pressure; and (4) **reason-
giving** — abstention that names *why* (never recorded / observation gap /
inaccessible / lost / underdetermined / ambiguous enumeration), not a single
undifferentiated "I don't know."

The failure mode this experiment is built to reveal is **confident gap-
filling under narrative or statistical pressure**: a system that retrieves
real, relevant, even abundant evidence (Invariant 07-F — retrieval volume
must not force an answer) and then quietly converts "the most likely
completion" into "the recorded fact." That failure is invisible to any
benchmark that only checks whether retrieved passages are relevant, because
the passages *are* relevant — the corpus for claims like C05/C24 or C31
contains real, on-topic, high-quality evidence pointing in more than one
direction. The system fails not by retrieving badly, but by resolving
genuine ambiguity it was never entitled to resolve. Symmetrically, a system
that resolves this pressure by *always* abstaining is caught by the
`known_true`/`known_false`/`known_value`/`inferable` claims and the plain-
recall control queries, which punish reflexive non-answering just as
concretely as the unknown claims punish hallucination.
