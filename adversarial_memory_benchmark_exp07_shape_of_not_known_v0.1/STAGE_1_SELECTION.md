# Stage 1 — Candidate Story Selection

## Experiment 07: The Shape of What Is Not Known

Research target: can a memory system distinguish absence of evidence, evidence of
absence, incomplete observation, inaccessible evidence, lost evidence, contradictory
evidence, unresolved ambiguity, misleading question premises, never-recorded facts,
facts inferable from constraints, and facts merely plausible from narrative context?

### Candidates considered

**1. Meridian Station — Antarctic winter-over research station (closed-world facility + expedition hybrid).**
A 14-person multinational station, isolated for the winter (no flights in or out).
Two heated entrances (one badge-logged and exhaustive, one manual-logbook and
routinely skipped), an unmonitored tunnel connecting two wings, a satellite field
camp reachable only by twice-daily scheduled radio windows, a fuel-valve incident
with a real telemetry gap, weather instruments with documented outage windows, and
a small enough population that "the only crew present were X, Y, Z" is a coherent,
literally true sentence. Strengths: the station's size and instrumentation can be
*authored exhaustively*, so completeness and incompleteness of any given log is a
fact the corpus can state outright and enforce consistently across hundreds of
records. Isolation creates natural, dramatically coherent reasons for gaps (storms,
radio blackouts, telemetry outages, a damaged data drive on the outbound flight)
without needing contrived plot devices. Routine daily rhythms (roll calls, generator
checks, meal duty, weather rounds) supply exactly the "narrative pressure toward a
plausible-but-unsupported answer" the spec requires, and a small fixed cast makes
multi-observer partial-observation cases easy to construct precisely.

**2. Nordfjall Systems — software incident postmortem (SaaS outage investigation).**
A mid-size company investigating a service outage: log rotation destroyed part of
the trace history, a manual hotfix was pushed without a ticket, a vendor's status
page is the only record of a dependency's downtime and the vendor won't share raw
logs, and chat history for the incident channel has a gap during a platform
migration. Strengths: very natural fit for 07.2 (observation gap), 07.3
(inaccessible vendor logs), 07.8 (partial instrumentation — only some services emit
telemetry). Weaknesses: this genre overlaps heavily with the technical, infra-heavy
texture already used by Experiment 04 (Aurora Global / Relay), risking a corpus that
reads as a re-skin rather than a distinct adversarial surface; and "exhaustive vs.
incomplete" is harder to make air-tight, since almost any software system has some
plausible unlogged code path a skeptical evaluator could point to as inherently
incomplete, which weakens the clean Control C (valid evidence-of-absence) cases the
spec needs.

**3. Harrow County fire investigation — warehouse fire, insurance/legal dispute.**
An investigator reconstructs a warehouse fire: sealed evidence exhibits, a badge
system covering the front office but not the loading dock, witness statements that
each cover only part of the night, and a disputed insurance claim built on
unsupported premises ("why did the security guard disable the alarm?"). Strengths:
excellent for 07.5 (misleading premises) and 07.3 (sealed exhibits) because a legal
frame makes "the record does not establish that" a natural, expected register.
Weaknesses: a single dramatic fire-and-dispute event gives less room for the
*sustained, dense, routine* narrative texture (07.5, section 5 wants recurring
habits and expectations across hundreds of memories) that the spec asks for, and
sustaining 300+ non-repetitive memories around one investigation risks padding;
also the subject matter (fire, injury liability) requires more care to keep
appropriately low-stakes and non-graphic throughout a large corpus.

### Evaluation against the required criteria

| Criterion | Meridian Station | Nordfjall Systems | Harrow County |
|---|---|---|---|
| Realistic information gaps | Strong (isolation, weather, radio) | Strong | Moderate |
| Exhaustive vs. incomplete records definable | Very strong (small closed population, authored logs) | Moderate (software completeness is fuzzy) | Moderate (single building, two systems) |
| Narrative pressure toward plausible-but-unsupported answers | Very strong (daily routines/habits) | Strong | Moderate |
| Deterministic missingness ground truth | Very strong (author controls every sensor/log) | Strong | Strong |
| Misleading-premise opportunities | Strong | Strong | Very strong |
| Later-resolution opportunities | Strong (blackout ends, supply flight, repaired part) | Moderate | Moderate |
| Dramatic coherence at 300–650 memories | Strong (many parallel routines, sub-plots) | Moderate (risks re-skinning Exp 04) | Weaker (single incident, padding risk) |

### Selected: **Meridian Station** (Antarctic winter-over research station)

It is the strongest fit for the spec's own recommendation that a "fully synthetic
closed-world facility... is useful because the benchmark can carefully define when
logs are exhaustive and when they are not" (§5.E), while still carrying the
expedition/isolation texture of §5.A. Its small, fixed population and dual-entrance
layout make Invariants 07-C/07-D (evidence of absence vs. scoped negatives) exact
and checkable, and its instrument/radio infrastructure gives natural, low-drama
sources for observation gaps, inaccessible sources, and later resolution — the
three hardest properties to fake convincingly at scale.
