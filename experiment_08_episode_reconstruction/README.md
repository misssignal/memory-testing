# Experiment 08 — Bursts, Boundaries, and Resumption

Synthetic adversarial benchmark for episode reconstruction in long-term memory systems.

## Research question

Can a system infer meaningful episode boundaries and membership from distributed traces without
joining unrelated work, splitting resumed work, or confusing precursors and consequences with members?

## Corpus summary

- Story: Northstar Control Plane: A Year of Distributed Reliability Work
- Memories: 525
- Canonical episodes: 12
- Query set: 129
- Controlled perturbations: 10
- Background distractor memories: 170
- Ground truth includes explicit `MEMBER_OF`, precursor, consequence, ambiguous-boundary, overlap,
  similarity, resumption, and follow-up relationships.

## Core benchmark invariants

1. Temporal proximity does not imply same episode.
2. Temporal separation does not imply different episode.
3. Project/work-item identity does not imply episode identity.
4. Similarity does not imply membership.
5. Consequences and precursors are not automatically members.
6. Ambiguous membership may remain ambiguous.

## Important design structures

- EP01 overlaps an unrelated docs cleanup and includes a wait/resumption.
- Issue #73 contains EP04 and EP05 as two distinct bursts.
- EP05 and EP06 overlap in June but are separate.
- EP06 contains a multi-day interruption and terminology drift.
- EP03 and EP07 are semantically similar but distinct token incidents.
- EP06 and EP10 are symptomatically similar but distinct startup incidents.
- EP11 is a follow-up architecture initiative, not part of EP06 or EP10.
- Background activity is deliberately interleaved across the year.

## Files

- `story_bible.md`
- `memories.jsonl`
- `truth_state.json`
- `episode_ledger.json`
- `episode_membership.json`
- `episode_relationships.json`
- `experimental_map.json`
- `queries.jsonl`
- `perturbations/manifest.json`
- `sources.md`
- `self_review.md`
