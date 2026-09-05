# Self Review — Experiment 08

## Strongest traps

1. Long-lived Issue #73 contains two distinct episodes (EP04, EP05).
2. EP06 survives a multi-day hardware wait and terminology drift.
3. EP03 and EP07 share token-expiry vocabulary but are distinct.
4. EP05 and EP06 overlap heavily in June but remain separate.
5. EP11 is topically continuous with startup incidents yet is a follow-up episode, not incident membership.

## Shortcut audit

- A fixed inactivity timeout will fail the EP06 gap sweep.
- Issue IDs cannot solve the benchmark because one issue contains multiple episodes and one episode spans many artifacts.
- Repository boundaries cannot solve it because EP08 crosses repositories.
- Author identity cannot solve it because the same people participate in unrelated efforts.
- Weekends do not consistently define boundaries.
- Episode starts/ends are not uniformly tied to issue-open or merge events.
- Similarity alone fails on EP03/EP07 and EP06/EP10.
- Temporal windows alone fail on EP01/EP02 and EP05/EP06.
- Connected-components alone risks swallowing consequences and follow-up work.

## Remaining ambiguity

A few boundary traces are intentionally marked `ambiguous`. These should not be forced into binary
membership. The benchmark rewards calibrated uncertainty.

## Architectural implication

A strong system needs temporal structure, semantic continuity, entity resolution, explicit artifact
relationships, and goal/intent continuity. No single signal is sufficient. A system that retrieves
all relevant records but still overmerges or oversplits is failing reconstruction rather than retrieval.
