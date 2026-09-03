# Story Bible — Experiment 01: Northstar Array

## Premise
Northstar Array is a remote high-altitude observatory operated by the nonprofit Meridian Research Cooperative.
During a 14-month modernization, the observatory experiences intermittent thermal shutdowns, a scheduler migration,
a temporary generator exception, a site rename, and a disputed March outage whose cause is only reconstructed months later.

The benchmark is designed so that objective event chronology, contemporaneous belief, later reconstruction,
and current operating state frequently differ.

## Core entities
- Meridian Research Cooperative (MRC), operator.
- Northstar Array, the observatory.
- Echo Camp, historical site name; renamed Nadir Station on 2026-07-01.
- AURORA, legacy observation scheduler; renamed in documentation to ORBIT after migration planning began.
- Kestrel, proposed replacement scheduler; pilot ran temporarily, then was rolled back.
- Helios, thermal-control subsystem.
- Vale Battery Bank, initially suspected in shutdowns.
- Ground Loop G-17, actual intermittent grounding fault later found to have caused several shutdowns.
- Dr. Lena Ortiz, observatory director.
- Priya Shah, controls engineer.
- Marcus Bell, operations lead.
- Tamsin Reed, reliability analyst.
- Elias Ward, visiting power specialist.

## Major timeline
1. 2026-01-08 — AURORA remains production scheduler; Kestrel evaluation begins.
2. 2026-02-03 — First unexplained thermal shutdown.
3. 2026-02-04 — Vale Battery Bank becomes leading hypothesis.
4. 2026-02-18 — Kestrel recommended for pilot, not yet approved for production.
5. 2026-03-11 — Major overnight outage occurs.
6. 2026-03-12 — Team believes March outage was automatic Helios protection trip.
7. 2026-03-20 — Kestrel pilot approved for a limited instrument subset.
8. 2026-04-02 — Generator-only exception begins for Spectrograph S2 overnight observations.
9. 2026-04-19 — Kestrel pilot expands informally; staff begin speaking as if migration is complete.
10. 2026-05-06 — Kestrel pilot causes missed calibration window; rollback ordered.
11. 2026-05-08 — AURORA restored as production scheduler.
12. 2026-05-28 — Battery replacement completed, but shutdowns continue.
13. 2026-06-14 — Priya suspects grounding fault; initially treated as low-confidence.
14. 2026-07-01 — Echo Camp officially renamed Nadir Station.
15. 2026-07-09 — Generator exception ends; normal mixed-power policy resumes.
16. 2026-08-22 — Archived oscilloscope trace from March is discovered.
17. 2026-08-24 — Trace implicates Ground Loop G-17, not Vale Battery Bank.
18. 2026-08-27 — Maintenance log reveals Marcus manually shut down Helios on March 11 after seeing unstable readings.
19. 2026-09-02 — Team reconstructs March event: manual shutdown was a response to G-17 instability.
20. 2026-09-03 — Current state: AURORA is production scheduler; Kestrel is shelved pending redesign; G-17 repaired; Nadir name current.

## Truth-state anchors
- AURORA was production at start, Kestrel briefly served a scoped pilot, AURORA is current production.
- “Kestrel migration completed” was never globally true.
- Vale Battery Bank was a reasonable but false causal hypothesis.
- Ground Loop G-17 caused the instability behind multiple shutdowns.
- The March 11 shutdown action itself was manual, though contemporaries believed it was automatic.
- Echo Camp was the correct historical name before 2026-07-01; Nadir Station is correct after.
- Generator-only operation was true only for Spectrograph S2 overnight work from 2026-04-02 through 2026-07-09.
