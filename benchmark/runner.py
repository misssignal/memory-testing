"""Benchmark runner — orchestrates ingestion, query execution, and evaluation."""
from __future__ import annotations

import json
import time
import hashlib
import platform
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from adapters.base import MemorySystemAdapter
from corpus_loader import load_corpus
from evaluators.base import CaseResult, CategoryScore
from evaluators.retrieval import evaluate_point_retrieval, evaluate_provenance
from evaluators.temporal import evaluate_temporal_latest, evaluate_temporal_history
from evaluators.contention import (
    evaluate_contradiction,
    evaluate_uncertainty,
    evaluate_alias,
    evaluate_exact_duplicate,
    evaluate_semantic_duplicate,
    evaluate_distractor,
    evaluate_abstention,
)

EVALUATORS = {
    "point_retrieval": evaluate_point_retrieval,
    "temporal_latest": evaluate_temporal_latest,
    "temporal_history": evaluate_temporal_history,
    "supersession": evaluate_temporal_latest,
    "contradiction": evaluate_contradiction,
    "uncertainty": evaluate_uncertainty,
    "alias": evaluate_alias,
    "exact_duplicate": evaluate_exact_duplicate,
    "semantic_duplicate": evaluate_semantic_duplicate,
    "provenance": evaluate_provenance,
    "distractor": evaluate_distractor,
    "abstention": evaluate_abstention,
}


@dataclass
class RunConfig:
    corpus_path: str = "corpus/fake_becca"
    cases_dir: str = "cases"
    namespace: str = "bench-test"
    top_k: int = 10
    categories: list[str] | None = None
    skip_ingest: bool = False
    seed: int = 42


@dataclass
class RunMetadata:
    benchmark_version: str = "0.1.0"
    corpus_hash: str = ""
    adapter_name: str = ""
    adapter_info: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    start_time: str = ""
    end_time: str = ""
    total_cases: int = 0
    total_passed: int = 0
    platform: str = ""
    python_version: str = ""


@dataclass
class RunResult:
    metadata: RunMetadata
    results: list[CaseResult]
    scores: list[CategoryScore]


def load_cases(cases_dir: str | Path, categories: list[str] | None = None) -> list[dict]:
    cases_dir = Path(cases_dir)
    all_cases = []
    for f in sorted(cases_dir.glob("*.jsonl")):
        cat_name = f.stem
        if categories and cat_name not in categories:
            continue
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_cases.append(json.loads(line))
    return all_cases


def ingest_corpus(adapter: MemorySystemAdapter, corpus_path: str | Path, namespace: str) -> int:
    idx = load_corpus(corpus_path)
    print(f"  Ingesting {len(idx.records)} records into namespace '{namespace}'...")
    t0 = time.monotonic()
    ids = adapter.ingest(idx.records, namespace)
    elapsed = time.monotonic() - t0
    print(f"  Ingested {len(ids)} records in {elapsed:.1f}s")
    return len(ids)


def run_case(adapter: MemorySystemAdapter, case: dict, namespace: str, top_k: int) -> CaseResult:
    category = case["category"]
    evaluator = EVALUATORS.get(category)
    if not evaluator:
        return CaseResult(
            case_id=case["id"],
            category=category,
            passed=False,
            error=f"No evaluator for category '{category}'",
        )

    try:
        result = adapter.search(case["query"], namespace, top_k=top_k)
    except Exception as e:
        return CaseResult(
            case_id=case["id"],
            category=category,
            passed=False,
            error=str(e),
        )

    return evaluator(case, result)


def aggregate_scores(results: list[CaseResult]) -> list[CategoryScore]:
    by_cat: dict[str, list[CaseResult]] = {}
    for r in results:
        by_cat.setdefault(r.category, []).append(r)

    scores = []
    for cat, cat_results in sorted(by_cat.items()):
        passed = sum(1 for r in cat_results if r.passed)
        failed = sum(1 for r in cat_results if not r.passed)

        # aggregate metrics by averaging
        all_metrics: dict[str, list[float]] = {}
        for r in cat_results:
            for k, v in r.metrics.items():
                all_metrics.setdefault(k, []).append(v)
        avg_metrics = {k: sum(v) / len(v) for k, v in all_metrics.items()}

        failures = [r for r in cat_results if not r.passed]

        scores.append(CategoryScore(
            category=cat,
            total_cases=len(cat_results),
            passed=passed,
            failed=failed,
            metrics=avg_metrics,
            failures=failures[:5],
        ))
    return scores


def run_benchmark(adapter: MemorySystemAdapter, config: RunConfig) -> RunResult:
    import sys

    idx = load_corpus(config.corpus_path)

    meta = RunMetadata(
        corpus_hash=idx.corpus_hash,
        adapter_name=type(adapter).__name__,
        adapter_info=adapter.info(),
        config={"top_k": config.top_k, "namespace": config.namespace, "seed": config.seed},
        start_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        platform=platform.platform(),
        python_version=sys.version,
    )

    if not config.skip_ingest:
        ingest_corpus(adapter, config.corpus_path, config.namespace)
        time.sleep(2)  # allow indexing

    cases = load_cases(config.cases_dir, config.categories)
    meta.total_cases = len(cases)
    print(f"  Running {len(cases)} test cases...")

    results = []
    for i, case in enumerate(cases):
        r = run_case(adapter, case, config.namespace, config.top_k)
        results.append(r)
        status = "PASS" if r.passed else "FAIL"
        if (i + 1) % 10 == 0 or not r.passed:
            print(f"  [{i+1}/{len(cases)}] {status} {r.case_id}")

    meta.total_passed = sum(1 for r in results if r.passed)
    meta.end_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    scores = aggregate_scores(results)

    return RunResult(metadata=meta, results=results, scores=scores)


def save_run(run: RunResult, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = run.metadata.start_time.replace(":", "").replace("-", "")
    run_dir = output_dir / f"run_{timestamp}"
    run_dir.mkdir(exist_ok=True)

    # raw results
    results_file = run_dir / "results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "metadata": asdict(run.metadata),
                "results": [asdict(r) for r in run.results],
            },
            f,
            indent=2,
            default=str,
        )

    # scores
    scores_file = run_dir / "scores.json"
    with open(scores_file, "w") as f:
        json.dump(
            [
                {
                    "category": s.category,
                    "total": s.total_cases,
                    "passed": s.passed,
                    "failed": s.failed,
                    "pass_rate": s.pass_rate,
                    "metrics": s.metrics,
                }
                for s in run.scores
            ],
            f,
            indent=2,
        )

    # CSV summary
    csv_file = run_dir / "summary.csv"
    with open(csv_file, "w") as f:
        f.write("category,total,passed,failed,pass_rate\n")
        for s in run.scores:
            f.write(f"{s.category},{s.total_cases},{s.passed},{s.failed},{s.pass_rate:.3f}\n")

    print(f"  Run saved to {run_dir}")
    return run_dir
