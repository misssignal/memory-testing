"""Evaluator for point retrieval and provenance cases."""

from .base import CaseResult, recall_at_k, precision_at_k, mean_reciprocal_rank, ids_from_retrieval
from adapters.base import RetrievalResult


def evaluate_point_retrieval(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    relevant_ids = expected.get("relevant_memory_ids", [])
    retrieved_ids = ids_from_retrieval(result)

    r5 = recall_at_k(retrieved_ids, relevant_ids, 5)
    r10 = recall_at_k(retrieved_ids, relevant_ids, 10)
    p5 = precision_at_k(retrieved_ids, relevant_ids, 5)
    mrr = mean_reciprocal_rank(retrieved_ids, relevant_ids)

    passed = r10 > 0

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={"recall@5": r5, "recall@10": r10, "precision@5": p5, "mrr": mrr},
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "relevant_ids": relevant_ids,
            "hits_in_top10": list(set(retrieved_ids[:10]) & set(relevant_ids)),
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_provenance(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    supporting_ids = expected.get("supporting_memory_ids", [])
    retrieved_ids = ids_from_retrieval(result)

    has_source = bool(set(retrieved_ids[:10]) & set(supporting_ids))

    source_metadata_present = False
    for m in result.memories:
        if m.id in supporting_ids:
            raw = m.raw
            if raw.get("metadata", {}).get("source_id") or raw.get("source_type"):
                source_metadata_present = True
                break

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=has_source,
        metrics={
            "provenance_present": 1.0 if has_source else 0.0,
            "source_metadata_present": 1.0 if source_metadata_present else 0.0,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "expected_source_ids": supporting_ids,
            "expected_claim": expected.get("claim", ""),
            "latency_ms": result.latency_ms,
        },
    )
