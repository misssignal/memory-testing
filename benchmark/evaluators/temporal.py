"""Evaluator for temporal latest-state and history reconstruction cases."""

from .base import CaseResult, recall_at_k, ids_from_retrieval
from adapters.base import RetrievalResult


def evaluate_temporal_latest(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    facts = expected.get("facts", [])
    relevant_ids = expected.get("relevant_memory_ids", [])
    must_not_use = set(expected.get("must_not_use_as_current", []))
    retrieved_ids = ids_from_retrieval(result)

    # did it find the correct current record?
    correct_found = bool(set(retrieved_ids[:10]) & set(relevant_ids))

    # did it rank a superseded record above the current one?
    stale_above_current = False
    current_rank = None
    for i, rid in enumerate(retrieved_ids):
        if rid in set(relevant_ids):
            current_rank = i
            break
    if current_rank is not None:
        stale_ids_above = [rid for rid in retrieved_ids[:current_rank] if rid in must_not_use]
        stale_above_current = len(stale_ids_above) > 0
    elif must_not_use & set(retrieved_ids[:10]):
        stale_above_current = True

    # did any stale record appear in top results?
    stale_in_results = len(must_not_use & set(retrieved_ids[:10]))

    # check if top-1 result has the correct object value
    correct_object = facts[0]["object"] if facts else None
    top1_correct = False
    if result.memories:
        top_content = result.memories[0].content
        if correct_object and correct_object.lower() in top_content.lower():
            top1_correct = True

    passed = correct_found and not stale_above_current

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "correct_current_fact": 1.0 if correct_found else 0.0,
            "stale_fact_error": 1.0 if stale_above_current else 0.0,
            "stale_in_top10": float(stale_in_results),
            "top1_correct_object": 1.0 if top1_correct else 0.0,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "expected_object": correct_object,
            "current_rank": current_rank,
            "stale_ids_found": list(must_not_use & set(retrieved_ids[:10])),
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_temporal_history(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    ordered_facts = expected.get("ordered_facts", [])
    expected_ids = [f["memory_id"] for f in ordered_facts]
    expected_count = expected.get("expected_count", len(ordered_facts))
    retrieved_ids = ids_from_retrieval(result)

    # event recall: how many of the expected events appeared?
    hits = set(retrieved_ids) & set(expected_ids)
    event_recall = len(hits) / len(expected_ids) if expected_ids else 1.0

    # event ordering: among retrieved events that match, is their relative order correct?
    retrieved_expected = [rid for rid in retrieved_ids if rid in set(expected_ids)]
    expected_order = {eid: i for i, eid in enumerate(expected_ids)}
    ordering_correct = True
    inversions = 0
    for i in range(len(retrieved_expected)):
        for j in range(i + 1, len(retrieved_expected)):
            if expected_order.get(retrieved_expected[i], 0) > expected_order.get(retrieved_expected[j], 0):
                inversions += 1
                ordering_correct = False

    # missing transitions: events in ground truth not in results
    missing = [eid for eid in expected_ids if eid not in set(retrieved_ids)]
    missing_rate = len(missing) / len(expected_ids) if expected_ids else 0.0

    # invented transitions: results that aren't in the ground truth
    # (not strictly "invented" since they may be real memories, just not part of the chain)
    extra = [rid for rid in retrieved_ids if rid not in set(expected_ids)]

    passed = event_recall >= 0.5 and ordering_correct

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "event_recall": event_recall,
            "ordering_correct": 1.0 if ordering_correct else 0.0,
            "inversions": float(inversions),
            "missing_transition_rate": missing_rate,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "expected_ids": expected_ids,
            "missing_ids": missing,
            "extra_ids_in_results": extra[:10],
            "expected_count": expected_count,
            "latency_ms": result.latency_ms,
        },
    )
