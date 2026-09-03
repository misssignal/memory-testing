"""Evaluator for contradiction, uncertainty, duplicate, alias, distractor, and abstention cases."""

from .base import CaseResult, recall_at_k, ids_from_retrieval
from adapters.base import RetrievalResult


def evaluate_contradiction(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    competing = expected.get("competing_claims", [])
    relevant_ids = set(expected.get("relevant_memory_ids", []))
    retrieved_ids = ids_from_retrieval(result)
    retrieved_set = set(retrieved_ids[:20])

    # how many competing claims appeared in results?
    claims_found = [c for c in competing if c["memory_id"] in retrieved_set]
    claim_recall = len(claims_found) / len(competing) if competing else 0.0

    # did the system only return one side of the dispute?
    unique_objects = set(c["object"] for c in claims_found)
    arbitrary_resolution = len(claims_found) >= 1 and len(unique_objects) == 1 and len(competing) > 1

    passed = claim_recall >= 0.5 and not arbitrary_resolution

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "competing_claim_recall": claim_recall,
            "arbitrary_resolution": 1.0 if arbitrary_resolution else 0.0,
            "unique_claims_surfaced": float(len(unique_objects)),
            "total_competing_claims": float(len(competing)),
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "claims_found": [c["object"] for c in claims_found],
            "claims_missing": [c["object"] for c in competing if c["memory_id"] not in retrieved_set],
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_uncertainty(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    relevant_ids = expected.get("relevant_memory_ids", [])
    retrieved_ids = ids_from_retrieval(result)

    found = bool(set(retrieved_ids[:10]) & set(relevant_ids))

    # check if the uncertain record's metadata is preserved
    uncertainty_preserved = False
    for m in result.memories:
        if m.id in relevant_ids:
            meta = m.raw.get("metadata", {})
            if meta.get("status") in ("uncertain", "disputed") or meta.get("confidence", 1.0) < 0.7:
                uncertainty_preserved = True
            break

    passed = found

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "relevant_found": 1.0 if found else 0.0,
            "uncertainty_preserved": 1.0 if uncertainty_preserved else 0.0,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "expected_confidence": expected.get("confidence"),
            "expected_status": expected.get("status"),
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_alias(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    canonical = expected["canonical_entity"]
    sample_ids = expected.get("sample_relevant_ids", [])
    retrieved_ids = ids_from_retrieval(result)

    # did results contain records about the canonical entity?
    alias_resolved = False
    for m in result.memories[:10]:
        content = m.content.lower()
        meta = m.raw.get("metadata", {})
        subject = meta.get("subject", "")
        if canonical.lower() in content or subject == canonical:
            alias_resolved = True
            break

    recall = recall_at_k(retrieved_ids, sample_ids, 10) if sample_ids else (1.0 if alias_resolved else 0.0)

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=alias_resolved,
        metrics={
            "alias_resolved": 1.0 if alias_resolved else 0.0,
            "recall@10": recall,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "canonical_entity": canonical,
            "query_used_alias": expected.get("aliases", []),
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_exact_duplicate(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    dup_ids = set(expected.get("duplicate_ids", []))
    cluster_size = expected.get("cluster_size", 0)
    retrieved_ids = ids_from_retrieval(result)

    # how many duplicates appeared in results?
    dups_found = len(set(retrieved_ids[:20]) & dup_ids)

    # did duplicates dominate the result set?
    top10_dup_ratio = len(set(retrieved_ids[:10]) & dup_ids) / min(10, len(retrieved_ids)) if retrieved_ids else 0.0

    # score inflation: if scores are available, check if duplicates get higher scores
    passed = True  # duplicate detection is informational, not pass/fail in basic mode

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "duplicates_in_results": float(dups_found),
            "cluster_size": float(cluster_size),
            "top10_duplicate_ratio": top10_dup_ratio,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={"duplicate_ids": list(dup_ids), "latency_ms": result.latency_ms},
    )


def evaluate_semantic_duplicate(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    para_id = expected.get("paraphrase_id", "")
    original_ids = expected.get("original_ids", [])
    retrieved_ids = ids_from_retrieval(result)

    # did both the paraphrase and an original appear?
    para_found = para_id in set(retrieved_ids[:20])
    orig_found = bool(set(retrieved_ids[:20]) & set(original_ids))

    passed = para_found or orig_found

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "paraphrase_found": 1.0 if para_found else 0.0,
            "original_found": 1.0 if orig_found else 0.0,
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "paraphrase_text": expected.get("paraphrase_text", ""),
            "original_text": expected.get("original_text", ""),
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_distractor(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    correct_id = expected.get("correct_id")
    distractor_ids = set(expected.get("distractor_ids", []))
    retrieved_ids = ids_from_retrieval(result)

    correct_found = correct_id in set(retrieved_ids[:10]) if correct_id else True

    # did distractors rank above the correct answer?
    distractor_above = False
    if correct_id:
        correct_rank = None
        for i, rid in enumerate(retrieved_ids):
            if rid == correct_id:
                correct_rank = i
                break
        if correct_rank is not None:
            distractor_above = any(rid in distractor_ids for rid in retrieved_ids[:correct_rank])
        elif distractor_ids & set(retrieved_ids[:10]):
            distractor_above = True

    distractor_selected = len(distractor_ids & set(retrieved_ids[:10]))

    passed = correct_found and not distractor_above

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=passed,
        metrics={
            "correct_found": 1.0 if correct_found else 0.0,
            "distractor_above_correct": 1.0 if distractor_above else 0.0,
            "distractors_in_top10": float(distractor_selected),
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "correct_id": correct_id,
            "correct_object": expected.get("correct_object"),
            "latency_ms": result.latency_ms,
        },
    )


def evaluate_abstention(case: dict, result: RetrievalResult) -> CaseResult:
    expected = case["expected"]
    retrieved_ids = ids_from_retrieval(result)

    # for abstention: fewer results (or low-confidence results) is better
    result_count = len(result.memories)

    # basic heuristic: if no results, that's correct abstention
    # if results exist, check if any of them actually answer the question
    # (this is where an LLM judge would help, but we keep it structural)
    abstained = result_count == 0 or (result.error is not None)

    return CaseResult(
        case_id=case["id"],
        category=case["category"],
        passed=abstained,
        metrics={
            "abstained": 1.0 if abstained else 0.0,
            "result_count": float(result_count),
        },
        retrieved_ids=retrieved_ids,
        raw_response=result.raw_response,
        details={
            "note": expected.get("note", ""),
            "latency_ms": result.latency_ms,
        },
    )
