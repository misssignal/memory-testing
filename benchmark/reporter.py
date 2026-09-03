"""Generate human-readable Markdown reports from benchmark runs."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from runner import RunResult
from evaluators.base import CaseResult, CategoryScore


def generate_report(run: RunResult) -> str:
    meta = run.metadata
    lines = [
        "# Memory Benchmark Report",
        "",
        "## Configuration",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| Benchmark version | {meta.benchmark_version} |",
        f"| Adapter | {meta.adapter_name} |",
        f"| Corpus hash | `{meta.corpus_hash}` |",
        f"| Namespace | {meta.config.get('namespace', 'n/a')} |",
        f"| top_k | {meta.config.get('top_k', 'n/a')} |",
        f"| Seed | {meta.config.get('seed', 'n/a')} |",
        f"| Start | {meta.start_time} |",
        f"| End | {meta.end_time} |",
        f"| Platform | {meta.platform} |",
        "",
        "## Summary",
        "",
        f"**Total cases:** {meta.total_cases}  ",
        f"**Passed:** {meta.total_passed}  ",
        f"**Failed:** {meta.total_cases - meta.total_passed}  ",
        f"**Overall pass rate:** {meta.total_passed / meta.total_cases:.1%}" if meta.total_cases else "",
        "",
    ]

    # scorecard table
    lines.extend([
        "## Scorecard by Category",
        "",
        "| Category | Total | Passed | Failed | Pass Rate |",
        "|---|---|---|---|---|",
    ])
    for s in run.scores:
        lines.append(f"| {s.category} | {s.total_cases} | {s.passed} | {s.failed} | {s.pass_rate:.1%} |")
    lines.append("")

    # per-category metrics
    lines.extend(["## Component Metrics", ""])
    for s in run.scores:
        lines.append(f"### {s.category}")
        lines.append("")
        if s.metrics:
            lines.append("| Metric | Value |")
            lines.append("|---|---|")
            for k, v in sorted(s.metrics.items()):
                lines.append(f"| {k} | {v:.3f} |")
            lines.append("")

    # worst failures
    all_failures = [r for r in run.results if not r.passed]
    if all_failures:
        lines.extend(["## Worst Failures (up to 20)", ""])
        for r in all_failures[:20]:
            lines.append(f"### `{r.case_id}` ({r.category})")
            lines.append("")
            if r.error:
                lines.append(f"**Error:** {r.error}")
                lines.append("")
            lines.append(f"**Retrieved IDs (top 5):** {r.retrieved_ids[:5]}")
            lines.append("")
            if r.details:
                for k, v in r.details.items():
                    if k == "latency_ms":
                        lines.append(f"**Latency:** {v:.0f}ms")
                    elif isinstance(v, list) and len(v) > 5:
                        lines.append(f"**{k}:** {v[:5]} ... ({len(v)} total)")
                    else:
                        lines.append(f"**{k}:** {v}")
            lines.append("")
            if r.metrics:
                lines.append("| Metric | Value |")
                lines.append("|---|---|")
                for k, v in sorted(r.metrics.items()):
                    lines.append(f"| {k} | {v:.3f} |")
                lines.append("")

    # latency summary
    latencies = [r.details.get("latency_ms", 0) for r in run.results if r.details.get("latency_ms")]
    if latencies:
        latencies.sort()
        lines.extend([
            "## Latency Summary",
            "",
            f"| Stat | ms |",
            f"|---|---|",
            f"| min | {latencies[0]:.0f} |",
            f"| median | {latencies[len(latencies)//2]:.0f} |",
            f"| p95 | {latencies[int(len(latencies)*0.95)]:.0f} |",
            f"| max | {latencies[-1]:.0f} |",
            f"| mean | {sum(latencies)/len(latencies):.0f} |",
            "",
        ])

    return "\n".join(lines)


def write_report(run: RunResult, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = generate_report(run)
    output_path.write_text(report)
    print(f"  Report written to {output_path}")
