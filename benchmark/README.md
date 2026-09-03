# Memory MCP Benchmark Harness

A reusable testing infrastructure for evaluating MCP-based memory systems. Tests whether the underlying memory system retrieves, preserves, and reconstructs information correctly — not whether an LLM produces a pleasant answer.

## Quick start

```bash
cd benchmark

# 1. Generate test cases from the synthetic corpus
python3 cli.py generate-cases

# 2. Run the full benchmark (generates cases, ingests corpus, runs tests, produces report)
export PIYAPI_API_KEY="sk_live_..."
python3 cli.py full --adapter piyapi --namespace bench-test

# Or step by step:
python3 cli.py ingest --adapter piyapi --namespace bench-test
python3 cli.py run --adapter piyapi --namespace bench-test --skip-ingest
python3 cli.py report --run-dir runs/run_XXXXX
```

## Architecture

```
benchmark/
  corpus/fake_becca/     Synthetic memory records (5,360 records, 18 entities)
  adapters/              Memory system adapters (one per vendor)
    base.py              Abstract interface
    piyapi_rest.py       PiyAPI REST adapter
  cases/                 Generated test cases (.jsonl per category)
  evaluators/            Deterministic scoring logic
    retrieval.py         recall@k, precision@k, MRR
    temporal.py          Latest-state and history reconstruction
    contention.py        Contradiction, uncertainty, alias, duplicate, distractor, abstention
    semantic_judge.py    Optional LLM judge (never in the retrieval path)
  runs/                  Raw results per run
  reports/               Generated Markdown reports
  config/                Benchmark configuration
  corpus_loader.py       Loads corpus, builds indexes
  ground_truth.py        Generates test cases from corpus analysis
  runner.py              Orchestrates ingestion + execution + evaluation
  reporter.py            Markdown/JSON/CSV report generation
  cli.py                 CLI entry point
```

## Benchmark categories (161 cases)

| Category | Cases | What it tests |
|---|---|---|
| point_retrieval | 40 | Can the system find a directly relevant memory? |
| temporal_latest | 6 | Does it return the latest active fact, not a superseded one? |
| temporal_history | 14 | Can it reconstruct an ordered timeline of changes? |
| supersession | 6 | Does it handle superseded-but-not-deleted records correctly? |
| contradiction | 20 | Does it surface unresolved conflicts instead of picking one? |
| uncertainty | 15 | Does it preserve low-confidence / uncertain status? |
| alias | 14 | Can it resolve entity aliases (e.g. "Project Atlas" = "atlas-svc")? |
| exact_duplicate | 10 | Do exact duplicates distort ranking or confidence? |
| semantic_duplicate | 10 | Are paraphrased memories recognized as the same fact? |
| provenance | 15 | Can it trace claims back to supporting source memories? |
| distractor | 6 | Does it resist semantically similar but wrong records? |
| abstention | 5 | Does it say "unknown" when the corpus can't answer? |

## Adding a new MCP implementation

1. Create `adapters/my_system.py`
2. Implement `MemorySystemAdapter` (see `adapters/base.py`):

```python
from adapters.base import MemorySystemAdapter, MemoryRecord, RetrievalResult

class MySystemAdapter(MemorySystemAdapter):
    def reset(self, namespace):          ...
    def ingest(self, memories, ns):      ...
    def ingest_one(self, memory, ns):    ...
    def search(self, query, ns, top_k):  ...
    def get_by_id(self, memory_id):      ...
    def list_all(self, ns, limit):       ...
    def delete(self, memory_id):         ...
```

3. Register it in `cli.py`:

```python
def get_adapter(name):
    if name == "my_system":
        from adapters.my_system import MySystemAdapter
        return MySystemAdapter()
```

4. Run: `python3 cli.py full --adapter my_system`

The adapter normalizes vendor-specific APIs behind a common interface. The benchmark never calls vendor endpoints directly.

## Scoring philosophy

- **Deterministic scoring first.** LLM judges are optional and never in the retrieval path.
- **Scorecard by dimension.** No single aggregate score by default.
- **Explicit weights.** If you enable aggregate scoring, weights are in `config/default.yaml`.
- **Never hide catastrophic failures.** Excellent recall cannot compensate for broken temporal reasoning.

## Metrics per category

| Metric | Categories |
|---|---|
| recall@5, recall@10 | point_retrieval, provenance |
| precision@5 | point_retrieval |
| mean reciprocal rank | point_retrieval |
| correct_current_fact | temporal_latest, supersession, distractor |
| stale_fact_error | temporal_latest, supersession |
| event_recall | temporal_history |
| ordering_correct | temporal_history |
| competing_claim_recall | contradiction |
| arbitrary_resolution | contradiction |
| uncertainty_preserved | uncertainty |
| alias_resolved | alias |
| duplicate_ratio | exact_duplicate |
| provenance_present | provenance |
| distractor_above_correct | distractor |
| abstained | abstention |

## Run outputs

Each run produces:
- `results.json` — raw per-case results with retrieved IDs and scores
- `scores.json` — aggregated metrics per category
- `summary.csv` — one-line-per-category for quick comparison
- `report.md` — human-readable Markdown with failure details and latency

## Corpus

The synthetic corpus (`fake_becca_memories.jsonl`) contains:
- 5,360 records across 18 entities (10 people, 8 projects)
- Explicit supersession chains (Morgan Vale's preferences, project architecture changes)
- Disputed/conflicting claims with varying confidence
- Exact duplicates (clusters up to 33 copies)
- Semantic paraphrases (78 records with `para-src-` provenance)
- Entity aliases (both in metadata and in-text references)
- 6-step temporal project lifecycles
- Status values: active, superseded, disputed, uncertain, archived

All records use `"sensitivity": "synthetic"`. No real user data.
