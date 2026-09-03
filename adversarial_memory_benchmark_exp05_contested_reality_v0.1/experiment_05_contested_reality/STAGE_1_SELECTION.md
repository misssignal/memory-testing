# Stage 1 — Candidate Story Selection: Experiment 05, Contested Reality

Per spec section 11 (Stage 1), three candidate arcs are proposed and evaluated before any corpus
generation begins.

## Candidate 1 — Tidal-array turbine trip investigation (technical incident)

A pilot tidal-energy array's Turbine Unit T-4 suffers repeated intermittent shutdowns. Root cause
is contested between an electrical-fault hypothesis and a mechanical/vibration hypothesis; an
authoritative manufacturer engineer blames a firmware regression (wrong) while a junior site
technician's handwritten log points to bearing wear (right); redundant sensors disagree for
several distinct reasons (known calibration drift, unknown-until-teardown calibration drift,
different sampling windows, different tidal-state timing, genuinely unexplained residual
disagreement); a speculative whiteboard note about "harmonic resonance" is laundered through a
meeting summary, a status report, and an executive summary into an unsupported "known fact"; an
apparently resolved RCA reopens months later; a manufacturer spokesperson issues a PR statement
blaming the site contractor.

- Narrative strength: High. Marine engineering gives a natural cast of differently-authoritative
  actors (technician, site engineer, manufacturer reliability engineer, independent consultant,
  safety-board investigator, spokesperson) and a rich instrument set (vibration, temperature,
  SCADA telemetry, mooring tension) that produces measurement disagreement organically.
- Adversarial strength: Very high. Every one of the ten required subfamilies (05.1–05.10) maps
  onto a distinct, story-native sub-arc without forcing the narrative.
- Epistemic complexity: High. Confidence states evolve over a 5-month timeline with genuine
  reopening and at least two claims (original March root cause; the May voltage dip) that the
  story itself does not support resolving.
- Deterministic ground-truth potential: High. Objective status can be fixed authorially
  (electrical/mechanical split stays "underdetermined" by design; bearing wear is authorially
  true; biofouling is authorially false) without contradiction.
- Independent vs. derivative evidence: Very high. Instrumentation plus multiple human observers on
  different shifts naturally separates independent primary observation from copied/derivative
  reporting (status reports, exec summaries citing the same root memo).
- Evolving confidence: Very high — RCA lifecycle (open → provisional → reopened → resolved
  differently) is a standard engineering-investigation shape.
- Likely benchmark difficulty: High — many near-miss traps (authority language, repetition volume,
  vivid-but-wrong eyewitness testimony) that a naive system will resolve incorrectly.

## Candidate 2 — Disputed exoplanet transit-timing anomaly (scientific investigation)

A university team detects a transit-timing anomaly suggesting an unseen companion planet. A rival
group's reanalysis disputes it. A junior postdoc's independent photometry (uncorrelated
instrument) turns out to matter more than a senior PI's confident public statement, which
downstream press coverage launders into "confirmed exoplanet."

- Narrative strength: Good, but the cast of plausible authority levels is narrower (mostly
  academic hierarchy) and instrumentation diversity is lower than Candidate 1 unless invented
  facilities are added, which reduces plausibility.
- Adversarial strength: Good for 05.3, 05.4, 05.8, 05.9 (systematic vs. instrumental scope
  disagreement), but 05.10 (measurement disagreement) is harder to make non-technical-reader
  legible without heavy astrophysics exposition, and 05.2 (majority-wrong) is less natural since
  academic citation cascades are a better fit for Experiment 06 (provenance topology) than for
  Experiment 05's confidence focus.
- Epistemic complexity: High, but risks overlapping substantially with the provenance-cascade
  territory reserved for a future experiment 06, per spec section 05.8's explicit warning to keep
  overlap minimal.
- Deterministic ground-truth: Medium — real exoplanet detection controversies are genuinely
  contested in ways that are hard to author a clean, defensible objective_status for without either
  trivializing the science or requiring extensive invented physics.
- Likely benchmark difficulty: Medium-high, but at higher authoring risk of accidental leakage
  through science-communication tropes ("peer review" as an authority shortcut).

## Candidate 3 — Consumer product safety recall dispute (organizational crisis)

An e-bike battery manufacturer investigates a pattern of thermal incidents. Official press
statements diverge from internal QA findings; a low-status QA technician's finding is correct
against a VP's confident public reassurance; a regulator's inquiry runs in parallel.

- Narrative strength: Good — organizational/PR divergence is a strong fit for Invariant 05-C
  (authority ≠ truth) and 05.8 (confidence laundering from spin).
- Adversarial strength: Good for 05.3, 05.8, and the Control conditions, but weaker for 05.10
  (measurement disagreement) since consumer-product QA lacks the natural redundant-instrumentation
  setting Candidate 1 has, and weaker for 05.9 (expert disagreement across scopes) without
  contrivance.
- Epistemic complexity: Medium — the corporate/regulatory frame tends to collapse into a single
  "who is lying" axis rather than genuine multi-hypothesis contention, which risks under-serving
  05.1 and 05.6 (genuinely unresolved cases).
- Deterministic ground-truth: High, but the natural shape of the story pushes toward eventual full
  resolution (a recall is issued once cause is found), making genuine, permanent unresolved
  ambiguity (05.6, Control F) feel like an authorial contrivance rather than a natural outcome.
- Likely benchmark difficulty: Medium — the authority-inversion trap is strong, but the story
  offers fewer independent, differently-calibrated instruments to build 05.10's five sub-cases on.

## Selection

**Selected: Candidate 1 — Meridian Bay tidal-array turbine trip investigation.**

It is the only candidate that lets all ten required adversarial subfamilies (05.1–05.10) and all
six control conditions (A–F) arise as natural, undistorted consequences of the setting, rather
than requiring contrivance for at least one subfamily (as Candidates 2 and 3 do for 05.10 and,
in Candidate 2's case, risking overlap with Experiment 06's provenance-topology focus). It also
gives the richest, least leakage-prone authority ladder (automated SCADA → technician → site
engineer → manufacturer reliability engineer → independent consultant → regulator → spokesperson)
without relying on mocking or obviously-incompetent characterization to signal who is right.
