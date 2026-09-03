#!/usr/bin/env python3
"""CLI entry point for the memory benchmark.

Usage:
    python cli.py generate-cases [--corpus PATH]
    python cli.py ingest --adapter piyapi [--namespace NAME] [--corpus PATH]
    python cli.py run --adapter piyapi [--namespace NAME] [--top-k N] [--categories CAT,CAT]
    python cli.py evaluate --run-dir runs/run_XXXXX
    python cli.py report --run-dir runs/run_XXXXX
    python cli.py full --adapter piyapi [--namespace NAME]
"""

import argparse
import json
import sys
import time
from pathlib import Path


def get_adapter(name: str):
    if name == "piyapi":
        from adapters.piyapi_rest import PiyAPIRestAdapter
        return PiyAPIRestAdapter()
    raise ValueError(f"Unknown adapter: {name}. Available: piyapi")


def cmd_generate_cases(args):
    from ground_truth import write_cases
    print("Generating test cases from corpus...")
    write_cases(args.corpus, args.output)


def cmd_ingest(args):
    from runner import ingest_corpus
    adapter = get_adapter(args.adapter)
    print(f"Ingesting corpus into {args.adapter} namespace '{args.namespace}'...")
    count = ingest_corpus(adapter, args.corpus, args.namespace)
    print(f"Done. {count} records ingested.")


def cmd_run(args):
    from runner import run_benchmark, save_run, RunConfig
    adapter = get_adapter(args.adapter)
    categories = args.categories.split(",") if args.categories else None
    config = RunConfig(
        corpus_path=args.corpus,
        cases_dir=args.cases_dir,
        namespace=args.namespace,
        top_k=args.top_k,
        categories=categories,
        skip_ingest=args.skip_ingest,
        seed=args.seed,
    )
    print(f"Running benchmark against {args.adapter}...")
    result = run_benchmark(adapter, config)
    run_dir = save_run(result, "runs")

    from reporter import write_report
    report_path = run_dir / "report.md"
    write_report(result, report_path)

    print(f"\nResults: {run_dir}")
    print(f"Pass rate: {result.metadata.total_passed}/{result.metadata.total_cases}")

    for s in result.scores:
        print(f"  {s.category}: {s.passed}/{s.total_cases} ({s.pass_rate:.0%})")


def cmd_report(args):
    from runner import RunResult, RunMetadata
    from evaluators.base import CaseResult, CategoryScore
    from reporter import write_report

    run_dir = Path(args.run_dir)
    results_file = run_dir / "results.json"
    scores_file = run_dir / "scores.json"

    with open(results_file) as f:
        data = json.load(f)

    meta = RunMetadata(**data["metadata"])
    results = [CaseResult(**r) for r in data["results"]]

    from runner import aggregate_scores
    scores = aggregate_scores(results)

    run = RunResult(metadata=meta, results=results, scores=scores)
    report_path = run_dir / "report.md"
    write_report(run, report_path)


def cmd_full(args):
    """Generate cases, ingest, run, and report in one command."""
    from ground_truth import write_cases
    from runner import run_benchmark, save_run, RunConfig
    from reporter import write_report

    print("=== Step 1: Generate test cases ===")
    write_cases(args.corpus, args.cases_dir)

    print("\n=== Step 2: Run benchmark ===")
    adapter = get_adapter(args.adapter)
    categories = args.categories.split(",") if args.categories else None
    config = RunConfig(
        corpus_path=args.corpus,
        cases_dir=args.cases_dir,
        namespace=args.namespace,
        top_k=args.top_k,
        categories=categories,
        skip_ingest=False,
        seed=args.seed,
    )
    result = run_benchmark(adapter, config)

    print("\n=== Step 3: Save results ===")
    run_dir = save_run(result, "runs")

    print("\n=== Step 4: Generate report ===")
    report_path = run_dir / "report.md"
    write_report(result, report_path)

    print(f"\n{'='*60}")
    print(f"Benchmark complete.")
    print(f"Results: {run_dir}")
    print(f"Report:  {report_path}")
    print(f"Pass rate: {result.metadata.total_passed}/{result.metadata.total_cases}")
    for s in result.scores:
        print(f"  {s.category}: {s.passed}/{s.total_cases} ({s.pass_rate:.0%})")


def main():
    parser = argparse.ArgumentParser(description="Memory MCP Benchmark Harness")
    sub = parser.add_subparsers(dest="command")

    # generate-cases
    p = sub.add_parser("generate-cases", help="Generate test cases from corpus")
    p.add_argument("--corpus", default="corpus/fake_becca")
    p.add_argument("--output", default="cases")

    # ingest
    p = sub.add_parser("ingest", help="Ingest corpus into a memory system")
    p.add_argument("--adapter", required=True)
    p.add_argument("--namespace", default="bench-test")
    p.add_argument("--corpus", default="corpus/fake_becca")

    # run
    p = sub.add_parser("run", help="Run benchmark test cases")
    p.add_argument("--adapter", required=True)
    p.add_argument("--namespace", default="bench-test")
    p.add_argument("--corpus", default="corpus/fake_becca")
    p.add_argument("--cases-dir", default="cases")
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--categories", default=None, help="Comma-separated categories to run")
    p.add_argument("--skip-ingest", action="store_true")
    p.add_argument("--seed", type=int, default=42)

    # report
    p = sub.add_parser("report", help="Generate report from a run")
    p.add_argument("--run-dir", required=True)

    # full
    p = sub.add_parser("full", help="Generate cases, ingest, run, and report")
    p.add_argument("--adapter", required=True)
    p.add_argument("--namespace", default="bench-test")
    p.add_argument("--corpus", default="corpus/fake_becca")
    p.add_argument("--cases-dir", default="cases")
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--categories", default=None)
    p.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.command == "generate-cases":
        cmd_generate_cases(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "full":
        cmd_full(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
