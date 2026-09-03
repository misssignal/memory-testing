# Epistemic State — Experiment 05: Contested Reality

This document narrates *who believed what, when, and why*, as a prose companion to the
machine-readable `claim_ledger.json`. It exists to make Invariant 05-D concrete: Tuesday's belief
state must remain "A was believed on Tuesday" even after Friday's evidence changes the picture.
Every belief snapshot below has a corresponding `belief_states` entry in `claim_ledger.json` keyed
by the same date.

## Phase 1 — Initial confusion (2027-03-14 to 2027-03-22)

After the first two trips, **operations** (Reyes, Meridian ops team) has no working theory:
confidence in any specific cause is "uncertain" across the board. Nandy's 03-18 handwritten log
(bearing-temperature drift) exists but has not yet been read by anyone with authority to act on it
— it sits in the shift-log queue. On 03-20 a technician log entry about VIB-4A's sensor housing is
paraphrased into a biofouling theory (F05-003); by 03-22 operations regards biofouling as
"probable" — not because anyone independently observed biofouling, but because the paraphrase
reads confidently. **At this point, operations' belief in biofouling (probable) is objectively
unjustified relative to the evidence that exists** — this is deliberate: a query about "what was
believed on 2027-03-22" must return "probable" (the belief), while a query about "was that belief
justified" must surface that it rests on a single unread log, not independent confirmation.

## Phase 2 — Authority arrives, confidently wrong (2027-03-25 to 2027-04-05)

Kelvinbridge's Dr. Okafor reviews remote telemetry and, on 03-25, issues a preliminary assessment
blaming firmware v3.2 (F05-004). Because Okafor is the manufacturer's senior reliability engineer,
Meridian operations' confidence in the firmware explanation jumps to "probable" by early April —
again, on authority, not on new independent evidence. Nandy's bearing-temperature log (F05-005) is
still in circulation but is informally regarded as "worth checking eventually," not a competing
hypothesis — this is the authority-inversion trap in its belief-state form: the investigation
team's *stated* confidence ranks the wrong hypothesis above the right one throughout this phase.

## Phase 3 — Speculation becomes "fact" (2027-04-01 to 2027-04-20)

A whiteboard note on 04-01 speculates about harmonic resonance (F05-006), explicitly hedged as
"maybe... need to check." No one ever checks. By 04-05 a meeting summary calls it "a likely
contributing factor." By 04-14 a status report calls it "identified as a contributing factor." By
04-20 an executive summary calls it "the root cause." At no point between 04-01 and 04-20 does a
new observation, test, or independent source enter the record — the confidence trajectory is
generated entirely by document-genre laundering (05.8), and `claim_ledger.json` for F05-006 records
`independent_evidence_roots: 0` for this entire span despite the confidence label climbing from
"possible" to "official working theory."

## Phase 4 — Provisional resolution (2027-04-10 to 2027-04-12)

Independently of the harmonic-resonance thread, the 04-10 RCA correctly identifies bearing wear
(F05-005) — Nandy's low-status log is finally read and acted on. Operations' belief in F05-005
moves to "confirmed" and the bearing is replaced 04-12. As of 04-12, the *organizationally correct*
belief snapshot is: bearing wear = resolved cause; firmware = never formally retracted but
deprioritized; biofouling = still "probable" in some derivative documents that haven't caught up;
harmonic resonance = still climbing toward "official" in the report-writing pipeline that started
in Phase 3 and has its own lag.

## Phase 5 — Independent disconfirmation of biofouling (2027-05-01 to 2027-05-10)

The first real independent evidence against F05-003 arrives: a clean dive inspection (05-01) and
an independently-mounted accelerometer showing no biofouling correlation (05-10). These are two
independent roots against a claim that, by this point, has been restated in roughly ten derivative
documents. Belief should now shift toward "unlikely"/"disproven" for biofouling — and the ledger
requires that this shift be attributable to the two independent observations, not to the passage
of time or to repetition count.

## Phase 6 — Reopening (2027-06-02 onward)

Trips resume after the bearing replacement. This does not erase the fact that bearing wear was a
real, confirmed contributor — it means the April RCA's *single-cause* framing was incomplete. The
investigation team's 06-02 belief state for F05-023 (the RCA-lifecycle claim) moves to
"reopened," not "the April finding was wrong." Historical queries about "was bearing wear
established as of April 11" must still return yes; queries about "is the case closed" from
06-02 onward must return no.

## Phase 7 — Scope clarity and calibration forensics (2027-06-15 to 2027-06-22)

Park and Costa's 06-15/06-16 statements are both true; they are not a contradiction to preserve as
"unresolved" but a scope distinction to preserve as "both correct, different questions" (05.9).
The 06-20 teardown reveals TEMP-4A's calibration drift — this was *unknown* before teardown, so any
belief-state query dated before 06-20 must reflect genuine uncertainty about which temperature
sensor to trust, even though the ledger's current objective record (post-06-20) resolves it. The
06-22 cross-reference to VIB-4A's calibration issue is different in kind: that drift was already
logged in April, so the "unknown calibration problem" framing applies only to TEMP-4A, not VIB-4A.

## Phase 8 — Institutional divergence and closure-with-remainder (2027-06-25 to 2027-08-01)

Voss's 06-25 public statement (installation error) diverges from Meridian's internal engineering
position and is never adopted internally — this is Invariant 05-C in its clearest form: an
authoritative public statement that is evidence of what was *said*, not of what was *true*. The
07-01 combined finding resolves F05-004/F05-003/F05-006 (false/false/unlikely) and confirms
F05-005 plus a newly-identified intermittent PCM ground fault as joint contributors to the June
recurrence. Critically, the 08-01 final report explicitly declines to retroactively resolve the
original March 14/16 trips (F05-001/F05-002) — the data-recorder gap that would have distinguished
electrical from mechanical causation for that specific episode was never filled. This is
authorial, permanent underdetermination, not an omission to be "fixed" by inference from the later,
different-episode finding.

## Belief-state cross-check table

| Date | Ops belief: biofouling (F05-003) | Ops belief: firmware (F05-004) | Ops belief: bearing wear (F05-005) | Ops belief: harmonic resonance (F05-006) | RCA state (F05-023) |
|---|---|---|---|---|---|
| 2027-03-22 | probable | uncertain | unconsidered | n/a | unresolved |
| 2027-04-05 | probable | probable | uncertain | possible | unresolved |
| 2027-04-14 | probable | probable | confirmed (resolved 04-10) | probable | provisionally_resolved |
| 2027-05-15 | unlikely | disputed | confirmed | official_working_theory | provisionally_resolved |
| 2027-06-10 | disproven | unlikely | confirmed, incomplete | disputed | reopened |
| 2027-08-01 | disproven | disproven | confirmed (joint cause) | unlikely | resolved_differently |

This table is illustrative; the authoritative machine-readable belief states (including the
investigation-team and Kelvinbridge-team tracks, which diverge at several points) live in
`claim_ledger.json`.
