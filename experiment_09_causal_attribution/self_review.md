# Self Review — Experiment 09

## Strongest traps

1. C01: deployment immediately precedes actuator lag but rollback fails; physical bus termination evidence identifies the actual cause.
2. C05: successful power-module replacement changes several variables at once, so repair success is not proof of module causality.
3. C06: cooling demand and sensor drift correlate strongly because ambient heat causes both.
4. C04: certificate renewal is a trigger; dependency cycle is the root cause.
5. C08: two viable brownout mechanisms remain unresolved because the discriminating experiments never occur.

## Shortcut audit

- Choosing the immediately preceding event fails C01.
- Trusting authoritative summaries fails C01/C04.
- Choosing the most recent explanation fails retrospective-historical queries.
- Treating successful fixes as proof fails C05.
- Treating correlation as causation fails C06.
- Treating visible symptoms as causes fails C09.
- Always abstaining fails C07, where controlled replay establishes a cause.
- Always forcing one root cause fails C02 and C08.

## 08 × 09 crossover readiness

C04 and C07 intentionally contain precursor/event distinctions compatible with Experiment 08-style episode
analysis. The causal graph is separate from episode membership so later compound testing can ask whether a
system reconstructs the history correctly yet still overclaims causality.

## Architectural implication

Passing requires more than retrieval. A system needs provenance-aware evidence weighting, temporal reasoning,
causal relation typing, intervention sensitivity, counterevidence handling, and calibrated uncertainty.
A system can reconstruct every relevant trace and still fail by turning a coherent story into an unjustified cause.
