# Adversarial Memory Benchmark Suite

A suite of 20 adversarial benchmark experiments for evaluating MCP-based and long-term memory systems. Each experiment targets a specific failure mode — from temporal confusion and false consensus to privacy leakage and multi-hop reasoning — using synthetic corpora grounded in detailed fictional story worlds.

**5,424 memories | 1,842 queries | 20 experiments**

## What This Tests

Memory systems that store, retrieve, and reason over accumulated knowledge face adversarial conditions that simple retrieval benchmarks miss. This suite creates controlled scenarios where:

- Outdated information vastly outnumbers current truth
- Multiple documents cite the same incorrect source, creating false consensus
- Entities share names or aliases, requiring disambiguation
- Claims are true in one scope but false in another
- Evidence chains have gaps, cycles, or missing provenance
- Repeated exposure inflates confidence without adding evidence
- Privacy boundaries must be enforced across namespaces

Each experiment provides a self-contained corpus of memories, queries with expected/forbidden claims, and ground truth metadata.

## Repository Structure

```
normalized/                         # Standardized corpora (use this)
  catalog.json                      # Machine-readable index of all experiments
  experiment_01_temporal_traps/
    memories.jsonl                  # Core memory corpus (24-key schema)
    queries.jsonl                   # Evaluation queries (15-key schema)
    extensions.jsonl                # Experiment-specific fields (optional)
    query_extensions.jsonl          # Query-specific extensions (optional)
    manifest.json                   # SHA-256 checksums
    id_mapping.json                 # Original → normalized ID mapping
    truth_state.json                # Ground truth state (optional)
    provenance.json                 # Derivation metadata (optional)
    ingestion_*.jsonl               # Alternate ingestion orderings (optional)
  experiment_02_false_consensus/
    ...
  ...

scripts/
  check_suite.py                    # Suite-wide integrity checker
  build_catalog.py                  # Regenerate catalog.json
  evaluate.py                       # Scoring harness

adversarial_memory_seed_v1/         # Original story bibles & experimental maps
```

## Memory Schema (24 keys)

Every memory in `memories.jsonl` has exactly these fields:

| Key | Type | Description |
|-----|------|-------------|
| `memory_id` | string | Unique ID, format `E{NN}-{8hex}` |
| `experiment` | string | Experiment identifier |
| `story_id` | string | Story world identifier |
| `event_time` | ISO 8601 | When the event actually occurred |
| `observation_time` | ISO 8601 | When it was observed or recorded |
| `authored_time` | ISO 8601 | When the document was authored |
| `ingestion_time` | ISO 8601 | When it entered the memory system |
| `subject` | string | Subject entity |
| `predicate` | string | Relationship or action |
| `object` | string | Object entity or value |
| `text` | string | Full natural-language description |
| `memory_type` | string | Document type (observation, email, report, etc.) |
| `truth_role` | string | Role in the truth landscape (see below) |
| `belief_holder` | string | Who holds this belief ("system" = objective) |
| `confidence` | float | Confidence score [0, 1] |
| `source_id` | string | Source identifier |
| `source_type` | string | Source category |
| `derived_from` | list | Memory IDs this was derived from |
| `supersedes` | list | Memory IDs this supersedes |
| `contradicts` | list | Memory IDs this contradicts |
| `duplicates` | list | Memory IDs this duplicates |
| `aliases` | list | Alternative names for the subject |
| `scope` | string | Applicability scope |
| `tags` | list | Categorical tags |

### Four-Clock Temporal Model

Each memory carries four timestamps: `event_time <= observation_time <= authored_time <= ingestion_time`. This captures the common real-world pattern where events happen, are observed later, documented later still, and ingested into a system even later. The gap between these timestamps is itself an adversarial signal.

### Truth Roles

Common values across experiments:

- `current_truth` — what is objectively true now
- `historical_truth` — what was true at the stated time
- `stale_truth` — was true, no longer is
- `false_claim` — never true
- `correction` — explicitly corrects an earlier claim
- `derived_claim` — derived from another source
- `disputed_claim` — contested by credible sources
- `rumor` — unverified hearsay
- `independent_support` — independently corroborates a claim
- `misleading_distractor` — technically related but misleading
- `scoped_truth` — true only within a specific scope
- `proposal` — proposed but not enacted

## Query Schema (15 keys)

| Key | Type | Description |
|-----|------|-------------|
| `query_id` | string | Unique ID, format `Q{NN}-{seq}` |
| `query` | string | Natural-language question |
| `category` | string | Query category |
| `expected_claims` | list | Claims that should appear in a correct answer |
| `acceptable_claims` | list | Claims that may appear (not penalized) |
| `forbidden_claims` | list | Claims that must NOT appear |
| `relevant_memory_ids` | list | Memories needed to answer correctly |
| `distractor_memory_ids` | list | Memories that might mislead |
| `difficulty` | string | easy, medium, or hard |
| `must_surface_uncertainty` | bool | Response should express uncertainty |
| `must_surface_conflict` | bool | Response should note conflicting evidence |
| `must_disambiguate` | bool | Response should distinguish similar entities |
| `must_preserve_scope` | bool | Response should respect scope boundaries |
| `should_abstain` | bool | Correct response is to decline to answer |
| `notes` | string | Evaluator notes |

## Experiments

| # | Theme | Story World | Memories | Queries |
|---|-------|-------------|----------|---------|
| 01 | Temporal Traps | Northstar Array Observatory | 205 | 80 |
| 02 | False Consensus | Nightglass Festival | 202 | 81 |
| 03 | Entity Identity Collision | Thornfield Biotech | 200 | 75 |
| 04 | Scope, Context & Partial Truth | Thornfield Biotech | 200 | 75 |
| 05 | Contested Reality | Thornfield Biotech | 202 | 153 |
| 06 | Evidence Lineage | Thornfield Biotech | 413 | 128 |
| 07 | Shape of Not-Known | Thornfield Biotech | 358 | 80 |
| 08 | Episode Reconstruction | Kestrel Migration | 525 | 129 |
| 09 | Causal Attribution | Kestrel Migration | 525 | 133 |
| 10 | Kestrel Full Corpus | Kestrel Migration | 500 | 120 |
| 11 | Forgetting & Retraction | Verdant Water District | 207 | 77 |
| 12 | Privacy & Namespace Isolation | Palomar Municipal | 212 | 80 |
| 13 | Consolidation & Summarization Drift | Halcyon Brewing | 232 | 98 |
| 14 | Semantic Near-Miss | Ridgeline Alpine Rescue | 214 | 75 |
| 15 | Contradictory Metadata | Ashford County Archive | 208 | 75 |
| 16 | Multi-Hop Dependencies | Cascadia Transit | 202 | 76 |
| 17 | Belief State vs Objective | Lakeshore Clinic | 206 | 75 |
| 18 | Counterfactual & Negative | Cedarpoint Schools | 207 | 76 |
| 19 | Repeated Exposure | Pinehurst Property | 201 | 78 |
| 20 | Scope Boundary Violation | Mariner's Wharf | 205 | 78 |

## Quick Start

### Load an experiment

```python
import json

experiment = "experiment_01_temporal_traps"
memories = [json.loads(l) for l in open(f"normalized/{experiment}/memories.jsonl")]
queries = [json.loads(l) for l in open(f"normalized/{experiment}/queries.jsonl")]
```

### Run the integrity checker

```bash
python scripts/check_suite.py          # summary
python scripts/check_suite.py -v       # with warnings
python scripts/check_suite.py --json   # machine-readable output
```

### Score answers

Create an `answers.jsonl` with one response per query:

```jsonl
{"query_id": "Q01-01", "response": "AURORA is the current production scheduler..."}
{"query_id": "Q01-02", "response": "The March outage was caused by G-17..."}
```

Then score:

```bash
python scripts/evaluate.py answers.jsonl
python scripts/evaluate.py answers.jsonl -o results.json   # detailed output
```

### Explore the catalog

```python
import json
catalog = json.load(open("normalized/catalog.json"))
for exp in catalog["experiments"]:
    print(f"{exp['experiment_number']:2d}. {exp['theme']}: {exp['counts']['memories']} memories")
```

## Extensions

Some experiments have additional fields in `extensions.jsonl` (keyed by `memory_id`) or `query_extensions.jsonl` (keyed by `query_id`). These carry experiment-specific metadata that doesn't fit the core schema:

- **Exp 02**: `evidence_root` — cluster ID tracing each memory to its original factual claim
- **Exp 03-07**: `_oracle`, `subject_entity_id`, `aliases_used` — entity resolution answer keys
- **Exp 06**: `expected_lineage_paths`, `must_detect_cycle` — lineage-specific query fields
- **Exp 07**: `answerability`, `missingness_type` — abstention-specific query fields
- **Exp 11**: `deletion_reason`, `deletion_status` — forgetting/retraction metadata
- **Exp 12**: `query_context` (tenant, access_level) — privacy namespace query context

## Ingestion Variants

Experiments 01-07 include alternate ingestion orderings:

- `ingestion_chronological.jsonl` — memories ordered by ingestion time
- `ingestion_shuffled.jsonl` — randomized order
- `ingestion_late_arrival.jsonl` — critical evidence arrives last

These test whether a memory system's behavior depends on the order information is encountered.
