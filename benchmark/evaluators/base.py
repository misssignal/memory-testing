"""Base evaluator and common scoring utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseResult:
    """Result of evaluating one test case."""
    case_id: str
    category: str
    passed: bool
    metrics: dict[str, float] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    retrieved_ids: list[str] = field(default_factory=list)
    raw_response: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class CategoryScore:
    """Aggregate score for one benchmark category."""
    category: str
    total_cases: int
    passed: int
    failed: int
    metrics: dict[str, float] = field(default_factory=dict)
    failures: list[CaseResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total_cases if self.total_cases else 0.0


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    if not relevant_ids:
        return 1.0
    top_k = set(retrieved_ids[:k])
    hits = len(top_k & set(relevant_ids))
    return hits / len(relevant_ids)


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = len(set(top_k) & set(relevant_ids))
    return hits / len(top_k)


def mean_reciprocal_rank(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    relevant_set = set(relevant_ids)
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def ids_from_retrieval(result) -> list[str]:
    """Extract memory IDs from a RetrievalResult."""
    return [m.id for m in result.memories]
