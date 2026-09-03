# Fake Becca MCP Memory Corpus

This dataset is fully synthetic and contains no real user, employer, project, credential, or personal data.

## Files

- `fake_becca_memories.jsonl` — primary bulk-load format
- `fake_becca_memories.csv` — convenient inspection format
- `gold_queries.json` — starter retrieval/evaluation prompts
- `schema.json` — field definitions and stressors

## Size

5,360 memory records.

## What it intentionally contains

- Longitudinal facts that change over time
- Superseded facts
- Conflicting claims
- Low-confidence / uncertain memories
- Exact duplicate memories
- Semantic paraphrases
- Entity aliases
- Cross-project and cross-person references
- Mixed synthetic provenance
- Archived/stale records

## Suggested evaluation dimensions

1. Retrieval precision / recall
2. Recency handling
3. Temporal reconstruction
4. Conflict surfacing
5. Alias/entity resolution
6. Duplicate clustering
7. Uncertainty preservation
8. Provenance retention
9. Resistance to stale-memory overwrite
10. Ability to explain why a memory was selected

## Safety

Every record uses `"sensitivity": "synthetic"`. Do not merge this dataset into a real personal memory store unless the namespace is isolated.
