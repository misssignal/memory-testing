#!/usr/bin/env python3
"""Scoring harness for adversarial memory benchmark experiments.

Usage:
    python evaluate.py <answers.jsonl> [--experiment EXP_DIR] [--output results.json]

answers.jsonl format (one per line):
    {"query_id": "Q01-01", "response": "AURORA is the production scheduler..."}

Scoring:
    For each query, the response is checked against expected_claims (must appear),
    acceptable_claims (may appear), and forbidden_claims (must not appear).
    Each claim is matched by substring (case-insensitive) by default.

    Scores:
    - expected_hit_rate: fraction of expected_claims found in response
    - forbidden_violation_rate: fraction of forbidden_claims found in response
    - composite: expected_hit_rate * (1 - forbidden_violation_rate)

    Flag compliance:
    - must_surface_uncertainty, must_surface_conflict, must_disambiguate,
      must_preserve_scope, should_abstain are checked via heuristic keywords.
"""

import json, sys, re, os
from pathlib import Path
from collections import defaultdict

NORMALIZED = Path(__file__).resolve().parent.parent / "normalized"

UNCERTAINTY_SIGNALS = [
    "uncertain", "unclear", "not sure", "unknown", "ambiguous",
    "insufficient", "cannot determine", "may or may not", "it's unclear",
    "conflicting", "no definitive", "cannot confirm",
]
CONFLICT_SIGNALS = [
    "conflict", "contradict", "disagree", "inconsistent", "dispute",
    "competing", "opposing", "at odds", "tension between",
]
DISAMBIG_SIGNALS = [
    "distinguish", "disambiguate", "should not be confused", "different from",
    "not the same as", "two separate", "multiple entities", "which one",
]
SCOPE_SIGNALS = [
    "only applies to", "limited to", "within the scope", "does not extend",
    "specifically for", "not all", "in this context", "scoped to",
]
ABSTAIN_SIGNALS = [
    "cannot answer", "not enough information", "unable to determine",
    "no data", "would be speculative", "cannot reliably", "abstain",
    "insufficient evidence", "not possible to determine",
]


def claim_in_response(claim, response):
    return claim.lower() in response.lower()


def check_flag(response, signals):
    resp_lower = response.lower()
    return any(s in resp_lower for s in signals)


def score_query(query, response):
    result = {
        "query_id": query["query_id"],
        "category": query["category"],
        "difficulty": query.get("difficulty", "medium"),
    }

    expected = query.get("expected_claims", [])
    acceptable = query.get("acceptable_claims", [])
    forbidden = query.get("forbidden_claims", [])

    expected_hits = [c for c in expected if claim_in_response(c, response)]
    forbidden_hits = [c for c in forbidden if claim_in_response(c, response)]

    result["expected_total"] = len(expected)
    result["expected_hits"] = len(expected_hits)
    result["expected_hit_rate"] = len(expected_hits) / len(expected) if expected else 1.0
    result["expected_matched"] = expected_hits
    result["expected_missed"] = [c for c in expected if c not in expected_hits]

    result["forbidden_total"] = len(forbidden)
    result["forbidden_violations"] = len(forbidden_hits)
    result["forbidden_violation_rate"] = len(forbidden_hits) / len(forbidden) if forbidden else 0.0
    result["forbidden_matched"] = forbidden_hits

    result["composite"] = result["expected_hit_rate"] * (1.0 - result["forbidden_violation_rate"])

    # Flag compliance
    flags = {}
    if query.get("must_surface_uncertainty"):
        flags["uncertainty"] = check_flag(response, UNCERTAINTY_SIGNALS)
    if query.get("must_surface_conflict"):
        flags["conflict"] = check_flag(response, CONFLICT_SIGNALS)
    if query.get("must_disambiguate"):
        flags["disambiguation"] = check_flag(response, DISAMBIG_SIGNALS)
    if query.get("must_preserve_scope"):
        flags["scope"] = check_flag(response, SCOPE_SIGNALS)
    if query.get("should_abstain"):
        flags["abstention"] = check_flag(response, ABSTAIN_SIGNALS)

    result["flag_compliance"] = flags
    result["flags_required"] = len(flags)
    result["flags_met"] = sum(1 for v in flags.values() if v)

    return result


def evaluate(answers_path, experiment_dir=None, output_path=None):
    # Load answers
    answers = {}
    with open(answers_path) as f:
        for line in f:
            obj = json.loads(line)
            answers[obj["query_id"]] = obj.get("response", "")

    # Determine experiment(s) to score against
    if experiment_dir:
        exp_dirs = [Path(experiment_dir)]
    else:
        # Auto-detect from query ID prefixes
        prefixes = {qid.split("-")[0] for qid in answers}
        exp_dirs = []
        for prefix in prefixes:
            num = prefix.replace("Q", "")
            matches = list(NORMALIZED.glob(f"experiment_{num}_*"))
            exp_dirs.extend(matches)

    if not exp_dirs:
        print("No matching experiments found for the given answers.")
        sys.exit(1)

    # Load all queries
    all_queries = {}
    for exp_dir in exp_dirs:
        qpath = exp_dir / "queries.jsonl"
        if qpath.exists():
            for line in open(qpath):
                q = json.loads(line)
                all_queries[q["query_id"]] = q

    # Score
    results = []
    for qid, response in sorted(answers.items()):
        if qid not in all_queries:
            results.append({"query_id": qid, "error": "query not found in corpus"})
            continue
        results.append(score_query(all_queries[qid], response))

    # Aggregate
    scored = [r for r in results if "error" not in r]
    agg = {
        "total_queries": len(answers),
        "scored": len(scored),
        "not_found": len(results) - len(scored),
    }

    if scored:
        agg["mean_expected_hit_rate"] = sum(r["expected_hit_rate"] for r in scored) / len(scored)
        agg["mean_forbidden_violation_rate"] = sum(r["forbidden_violation_rate"] for r in scored) / len(scored)
        agg["mean_composite"] = sum(r["composite"] for r in scored) / len(scored)

        # By category
        by_cat = defaultdict(list)
        for r in scored:
            by_cat[r["category"]].append(r)
        agg["by_category"] = {
            cat: {
                "count": len(rs),
                "mean_composite": sum(r["composite"] for r in rs) / len(rs),
                "mean_expected_hit_rate": sum(r["expected_hit_rate"] for r in rs) / len(rs),
            }
            for cat, rs in sorted(by_cat.items())
        }

        # By difficulty
        by_diff = defaultdict(list)
        for r in scored:
            by_diff[r["difficulty"]].append(r)
        agg["by_difficulty"] = {
            diff: {
                "count": len(rs),
                "mean_composite": sum(r["composite"] for r in rs) / len(rs),
            }
            for diff, rs in sorted(by_diff.items())
        }

        # Flag compliance
        flag_total = sum(r["flags_required"] for r in scored)
        flag_met = sum(r["flags_met"] for r in scored)
        agg["flag_compliance_rate"] = flag_met / flag_total if flag_total else None

    output = {
        "summary": agg,
        "per_query": results,
    }

    if output_path:
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Results written to {output_path}")
    else:
        print(json.dumps(output, indent=2))

    # Print summary table
    print(f"\n{'='*60}")
    print(f"Scored {agg['scored']} / {agg['total_queries']} queries")
    if scored:
        print(f"  Expected claim hit rate:      {agg['mean_expected_hit_rate']:.1%}")
        print(f"  Forbidden violation rate:      {agg['mean_forbidden_violation_rate']:.1%}")
        print(f"  Composite score:              {agg['mean_composite']:.1%}")
        if agg.get("flag_compliance_rate") is not None:
            print(f"  Flag compliance:              {agg['flag_compliance_rate']:.1%}")
        print(f"\n  By difficulty:")
        for diff, stats in agg["by_difficulty"].items():
            print(f"    {diff:8s}: {stats['mean_composite']:.1%} ({stats['count']} queries)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Score memory system answers against benchmark queries")
    parser.add_argument("answers", help="Path to answers.jsonl")
    parser.add_argument("--experiment", "-e", help="Path to experiment directory (auto-detected if omitted)")
    parser.add_argument("--output", "-o", help="Path to write detailed results JSON")
    args = parser.parse_args()

    evaluate(args.answers, args.experiment, args.output)


if __name__ == "__main__":
    main()
