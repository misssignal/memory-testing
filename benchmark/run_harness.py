"""Run the benchmark harness against bench-micro-001 with ID translation."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent))

from adapters.piyapi_rest import PiyAPIRestAdapter
from runner import load_cases, aggregate_scores, RunMetadata, RunResult, save_run
from evaluators.base import CaseResult
from evaluators.retrieval import evaluate_point_retrieval, evaluate_provenance
from evaluators.temporal import evaluate_temporal_latest, evaluate_temporal_history
from evaluators.contention import (
    evaluate_contradiction, evaluate_uncertainty, evaluate_alias,
    evaluate_exact_duplicate, evaluate_semantic_duplicate,
    evaluate_distractor, evaluate_abstention,
)
from reporter import generate_report

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

NAMESPACE = "bench-micro-001"
TOP_K = 10
QUERY_DELAY = 1.0


def load_id_map() -> dict[str, str]:
    with open(Path(__file__).parent / "cases" / "micro_id_map.json") as f:
        return json.load(f)


def translate_ids(obj, id_map: dict[str, str]):
    """Recursively translate corpus IDs to PiyAPI IDs in a case dict."""
    if isinstance(obj, str):
        return id_map.get(obj, obj)
    if isinstance(obj, list):
        return [translate_ids(x, id_map) for x in obj]
    if isinstance(obj, dict):
        return {k: translate_ids(v, id_map) for k, v in obj.items()}
    return obj


def is_runnable(case: dict, id_map: dict[str, str]) -> bool:
    """Check if critical IDs in the case exist in the id_map.

    Per-category logic: only require IDs that affect pass/fail, not metrics-only fields.
    """
    exp = case.get("expected", {})
    cat = case.get("category", "")
    ingested = set(id_map.keys())

    # Abstention: no IDs needed
    if cat == "abstention":
        return True

    # Alias: pass/fail checks content, not IDs. sample_relevant_ids are metrics-only.
    if cat == "alias":
        return True

    # Exact/semantic duplicate: always passes (informational), or checks para/orig presence
    if cat == "exact_duplicate":
        return True
    if cat == "semantic_duplicate":
        ids = set()
        if exp.get("paraphrase_id"):
            ids.add(exp["paraphrase_id"])
        ids.update(exp.get("original_ids", []))
        ids.discard("")
        return bool(ids & ingested)  # at least one of paraphrase or original present

    # Contradiction: need competing_claims.memory_id
    if cat == "contradiction":
        claim_ids = {c["memory_id"] for c in exp.get("competing_claims", []) if "memory_id" in c}
        claim_ids.discard("")
        return claim_ids.issubset(ingested) if claim_ids else True

    # For everything else: require critical IDs
    critical = set()
    critical.update(exp.get("relevant_memory_ids", []))

    if cat in ("supersession", "temporal_latest"):
        critical.update(exp.get("must_not_use_as_current", []))

    if cat == "temporal_history":
        for fact in exp.get("ordered_facts", []):
            if isinstance(fact, dict) and "memory_id" in fact:
                critical.add(fact["memory_id"])

    if cat == "distractor":
        if exp.get("correct_id"):
            critical.add(exp["correct_id"])
        critical.update(exp.get("distractor_ids", []))

    if cat == "provenance":
        critical.update(exp.get("supporting_memory_ids", []))

    critical.discard("")
    if not critical:
        return True
    return critical.issubset(ingested)


def main():
    id_map = load_id_map()
    print(f"ID map: {len(id_map)} entries")

    cases_dir = Path(__file__).parent / "cases"
    skip_stems = {"batch3_records", "batch3_remaining", "micro_batch", "micro_id_map"}
    all_cases = []
    for f in sorted(cases_dir.glob("*.jsonl")):
        if f.stem in skip_stems:
            continue
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_cases.append(json.loads(line))

    runnable = [c for c in all_cases if is_runnable(c, id_map)]
    skipped = len(all_cases) - len(runnable)
    print(f"Cases: {len(all_cases)} total, {len(runnable)} runnable, {skipped} skipped")

    # Translate IDs
    translated = []
    for case in runnable:
        tc = json.loads(json.dumps(case))
        tc["expected"] = translate_ids(tc["expected"], id_map)
        translated.append(tc)

    # Set up adapter
    adapter = PiyAPIRestAdapter()

    meta = RunMetadata(
        benchmark_version="0.1.0",
        adapter_name="PiyAPIRestAdapter",
        adapter_info={"namespace": NAMESPACE, "record_count": len(id_map)},
        config={"top_k": TOP_K, "namespace": NAMESPACE, "skip_ingest": True,
                "cases_total": len(all_cases), "cases_runnable": len(runnable),
                "query_delay_s": QUERY_DELAY},
        start_time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        total_cases=len(translated),
        platform="",
        python_version=sys.version,
    )

    print(f"\nRunning {len(translated)} cases against '{NAMESPACE}'...")
    results = []
    for i, case in enumerate(translated):
        category = case["category"]
        evaluator = EVALUATORS.get(category)
        if not evaluator:
            results.append(CaseResult(
                case_id=case["id"], category=category, passed=False,
                error=f"No evaluator for '{category}'",
            ))
            continue

        try:
            search_result = adapter.search(case["query"], NAMESPACE, top_k=TOP_K)
        except Exception as e:
            results.append(CaseResult(
                case_id=case["id"], category=category, passed=False,
                error=str(e),
            ))
            continue

        result = evaluator(case, search_result)
        results.append(result)

        status = "PASS" if result.passed else "FAIL"
        if (i + 1) % 5 == 0 or not result.passed:
            print(f"  [{i+1:3d}/{len(translated)}] {status} {result.case_id} ({category})")

        time.sleep(QUERY_DELAY)

    meta.total_passed = sum(1 for r in results if r.passed)
    meta.end_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    scores = aggregate_scores(results)

    run = RunResult(metadata=meta, results=results, scores=scores)

    # Save
    output_dir = Path(__file__).parent / "runs"
    run_dir = save_run(run, output_dir)

    # Generate report
    report = generate_report(run)
    report_file = run_dir / "report.md"
    with open(report_file, "w") as f:
        f.write(report)

    # Print summary
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS: {meta.total_passed}/{len(results)} passed "
          f"({meta.total_passed/len(results)*100:.0f}%)")
    print(f"{'='*60}")
    for s in scores:
        bar = "█" * int(s.pass_rate * 20) + "░" * (20 - int(s.pass_rate * 20))
        print(f"  {s.category:25s} {s.passed:2d}/{s.total_cases:2d} {bar} {s.pass_rate*100:5.1f}%")
    print(f"\nReport: {report_file}")
    print(f"Results: {run_dir}")


if __name__ == "__main__":
    main()
