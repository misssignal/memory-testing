# Self-Review — Experiment 05: Contested Reality

## Standard benchmark self-review

**Schema conformance.** All 202 memory records carry every field required by `schema.json`'s
`memory_record` (verified by script: 0 missing fields, 0 unique-id collisions, 0 dangling
`derived_from`/`supersedes`/`contradicts` references). All 153 query records carry every field
required by `query_record`. `_oracle` extends the schema with `claim_id`, `adversarial_subfamily`,
`confidence_label`, `evidence_role`, `stance`, `source_name`/`source_org`/`source_authority`, and
`evidence_root`/`evidence_id` — additive fields only; no required exp03/04 field was removed or
repurposed incompatibly. Two new query-level fields (`must_surface_uncertainty`,
`must_surface_conflict`) are additive per spec section 9.6/9.7 and section 7.

**Synthetic-only.** All organizations, people, and the Meridian Bay Array itself are fictional
(see `sources.md`). No real company, regulator, or incident is asserted as factual.

**Balance.** 25 claims span all ten adversarial subfamilies (with two subfamilies — 05.2 and
05.3 — instantiated twice, per spec section 3's request for "several related arcs" where
practical) and all six control conditions (A–F). Query categories 9.1–9.5 and 9.7 each have 25
instances; 9.6 (forced-choice traps) has 3, deliberately kept small since a forced-choice trap is
only valid where the story genuinely never resolves the dichotomy (C01/C02, C20, and C23's
single-factor framing) — inflating this category would have required inventing more permanently
unresolved claims than the narrative naturally supports, which would have felt authorially
arbitrary rather than earned.

**Distractor discipline.** `is_distractor` is set narrowly (the rumor arc C22 and its two
supporting memories, plus the retracted C21 public statement) rather than applied broadly, so it
functions as a real signal rather than a diluted label.

**Blind-run guidance.** `_oracle` should be stripped for blind runs; `claim_id`, `truth_role`, and
`scope` are optionally strippable depending on which condition is under test, matching the
exp03/04 convention (`manifest.json`).

## Experiment-specific self-critique (spec section 12)

**1. Which five cases most strongly distinguish evidence weighting from simple majority voting?**
C03 (biofouling: 11 supporting memories from 1 root vs. 2 independent disconfirming roots), C24
(transformer overheating: same shape, second instance), C06 (harmonic resonance: confidence
climbs through 4 document genres with 0 new evidence roots), P05-A's repetition-count perturbation
built directly on C03, and the C03-vs-C10 pairing (identical repetition *shape*, opposite
independence property) inside the shipped corpus.

**2. Can a system succeed by always choosing the minority claim?** No — C08 (control_D) and
C24-adjacent dynamics punish this: C08's minority tidal-phase hunch is genuinely wrong and
statistically debunked. A system that always favors the minority position fails C08 while
correctly handling C05/C25 (where minority happens to be right), so the two must be
distinguished on evidence, not position.

**3. Can a system succeed by always choosing the highest-authority source?** No — C04 (senior
Kelvinbridge engineer, wrong) and C21 (spokesperson, unsupported) punish this directly, while C11
and C09 (authority correct) reward correctly trusting authority when it is in fact right. A
uniform "trust authority" or "distrust authority" heuristic fails roughly half of the
authority-bearing claims by design.

**4. Can a system succeed by always saying "uncertain"?** No — most claims (C03, C04, C05, C08,
C09, C10, C11, C12, C13, C14–C17, C19, C22, C24, C25) have a determinate, well-evidenced
objective_status. A blanket-abstain strategy would fail Contention Preservation Rate's positive
cases and would score badly on Confidence Calibration Accuracy for the many Control-A/B/C/E cases
that specifically reward confident, correct answers. Only 4 of 25 claims (C01, C02, C18, C20) plus
C06's specific demoted-not-disproven state are genuinely open.

**5. Which genuinely unresolved cases are accidentally resolvable through wording?** Reviewed
C01/C02, C18, C20, and C06. Risk case: C06's canonical claim text ("harmonic resonance ... is the
root cause") could read as falsifiable-and-false rather than "downgraded to unlikely, not
disproven" if a system over-indexes on the word "unlikely" in later memories as equivalent to
"disproven." Mitigated by explicitly recording `objective_status: "unsupported"` (not `"false"`)
in `claim_ledger.json` and by the T05-05/T05-09 trap notes calling this out.

**6. Do confidence adjectives leak ground truth?** Deliberately, in some places (Control A/C use
"confirmed" honestly) and deliberately not in others: C03 and C06 use *high*-sounding confidence
language ("probable," "official working theory," "root cause") for claims that are objectively
false/unsupported, which is the entire point of 05.2/05.4/05.8. A system that reads confidence
adjectives as ground truth will fail exactly these cases.

**7. Does source role leak truth?** No single role is a reliable predictor: `automated_scada`
appears in both correct (C10, C19) and merely-neutral-observation (C18, C20) contexts;
`senior_engineer_manufacturer` appears wrong (C04) and is never shown correct in this corpus (a
residual limitation — see item 15); `junior_technician` appears both correct (C05) and originating
a false theory (C03's root note was Singh, a plain technician, not junior-labeled specifically).
`spokesperson` (C21) and `harbor_pilot_bystander` (C07, C22) are consistently unreliable by
design, which is intentional (PR statements and unsourced dockside rumor are not meant to be
genuine 50/50 traps) but is worth flagging as a place where role does correlate with outcome.

**8. Does recency correlate accidentally with correctness?** Largely no, by design: the *final*
memory in several chains is a synthesis/resolution record that is authoritatively correct (this is
structurally necessary — a corpus has to end somewhere), but intermediate-recency records are
frequently wrong-but-confident (C06's 04-20 executive summary is more recent than the 04-01
whiteboard note and *less* correct). The one place recency and correctness align cleanly by
construction is every claim's final synthesis memory, which is unavoidable in a finite,
chronologically-authored corpus rather than a designed trap.

**9. Are independent and derivative sources clearly distinguished in hidden ground truth?** Yes —
`_oracle.evidence_role` (`independent_primary` / `derivative_copy` / `synthesis` / `context`) and
`_oracle.evidence_root` (shared string for beats tracing to one underlying observation) are set on
every claim-linked memory and are the direct input to `claim_ledger.json`'s
`independent_evidence_roots` computation.

**10. Are any "independent" observations actually causally dependent?** Reviewed. One
soft case: C10's three "independent" corroborations (Singh, Ahn, acoustic sensor) all observe the
*same* physical gearbox in the *same* week, so they are independent in sourcing but not in the
sense of measuring unrelated phenomena — this is intentional (that is what genuine independent
corroboration of one real phenomenon looks like) but is worth distinguishing from
"independent evidence for different aspects of a claim." No case was found where a labeled
`independent_primary` memory secretly reads from another memory's text.

**11. Are historical belief queries separable from present truth queries?** Yes structurally —
`claim_ledger.json`'s `belief_states` are keyed by date and actor and are distinct from
`objective_status`; the query set's `9.2_historical_epistemic_state` category is built directly
from `belief_states` snapshots and never from the claim's final resolution. Spot-checked C03, C15,
C19, C23.

**12. Does any supposedly unresolved question actually have sufficient evidence for
resolution?** Reviewed C01/C02, C18, C20 line by line. C01/C02: the megger test (C01 beat 4) is
inconclusive by construction and no later memory supplies a discriminating test for the *specific*
March episode — the June/July combined finding concerns a different recurrence and is explicitly
not backdated in the 08-01 report. C18: ruled out sampling-window and calibration explanations
on-page; no memory supplies an alternative explanation. C20: the vessel-traffic correlation is
"plausible but not confirmed" and the sensor-noise explanation is symmetric; the proposed
strain-gauge test is explicitly unfunded. No leakage found.

**13. Which perturbation produces the clearest authority-bias measurement?** P05-B (authority
label swapped on the identical firmware claim, C04) — because the underlying evidence and text are
held completely fixed and only the source-role label changes, isolating authority as the sole
variable.

**14. Which perturbation best distinguishes duplicate evidence from independent corroboration?**
P05-G (minority evidence removed from C03) combined with the naturalistic C03-vs-C10 pairing —
P05-G isolates the *marginal* value of one additional independent root, while C03-vs-C10 shows the
categorical difference between all-derivative and genuinely-independent repetition at comparable
volume.

**15. Where could a sophisticated graph-memory architecture still collapse contention
incorrectly?** Two likely failure points: (a) a system that deduplicates by semantic similarity
could merge C12 and C13's "contradictory-sounding" statements into one node and then have to pick
a winner, destroying the 05.9 scope distinction — this is the single hardest case in the corpus
for embedding-based dedup; (b) a system that resolves claims via most-recent-write-wins on a
per-entity graph node could silently overwrite C23's April "provisionally_resolved" state with the
July "resolved_differently" state on the *same* node, losing the ability to answer the 04-11
historical-belief query correctly even though the raw memory is still stored, if its retrieval
layer only surfaces the latest node value by default.

## Residual limitations (honest accounting)

- No claim in the shipped corpus shows a `senior_engineer_manufacturer`-authority source being
  *both* authoritative *and* correct on a contested (non-Control-C) claim — Control C (C11) uses an
  `external_regulator_investigator` role instead. A future revision should add at least one
  senior-engineer-correct instance so Authority Bias Score cannot be gamed by a
  role-specific rather than general heuristic.
- Perturbation *variant files* (materialized World-B memory/query sets) are not generated for
  P05-A, P05-B, P05-D, P05-F, or the full P05-G; only the plan and, where the base corpus already
  contains a naturalistic instance, the matched pair is provided. See README.md Status.
- 153 queries is slightly above the spec's "preferably 75–150" band; left as-is rather than cut,
  since every query maps to a claim/category cell needed for the coverage claims made above.

## Benchmark verdict

To perform well on Experiment 05, a memory architecture must do four things that are each
individually hard and jointly rare: (1) represent **evidence independence as a first-class,
queryable property distinct from mention count** — not just store many similar memories and let a
retriever's frequency or similarity ranking stand in for confidence; (2) keep **confidence state
and claim identity separable from document recency and genre** — a later, more formal-sounding
summary must not automatically outrank an earlier, more tentative primary observation; (3)
**index belief state by (claim, actor, time) as its own queryable dimension**, separate from the
claim's current objective status, so historical "what did we believe then" questions do not
silently read off the present; and (4) **preserve scope/question-boundary metadata** so that two
true statements about different aspects of the same event are not forced into a single
merged-and-then-contradictory node.

A system that fails this experiment will typically do so in one of two visible ways: either it
manufactures false confidence (collapsing C01/C02/C06/C18/C20 to a single answer, or promoting
C03/C06/C21/C24/C25 because of volume, genre, or authority rather than evidence), or it
under-confidently hedges everything (failing to give the clean, confident answers that C09, C10,
C11, C12, C13, C19 specifically require). Passing requires calibration in both directions at once
— which is the whole point of shipping matched controls (A–F) alongside the ten adversarial
subfamilies: a system cannot pass by learning a single global disposition toward certainty or
doubt. It has to actually track the evidence.
