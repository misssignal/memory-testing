"""Abstract base class for memory system adapters.

Every MCP / memory system under test implements this interface.
The benchmark never calls vendor-specific APIs directly.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryRecord:
    """Normalized memory record used throughout the benchmark."""
    id: str
    content: str
    timestamp: str | None = None
    namespace: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """What the system returned for a single query."""
    query: str
    memories: list[MemoryRecord]
    scores: list[float]
    raw_response: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    error: str | None = None


@dataclass
class TraceEntry:
    """One step in the adapter's interaction log."""
    operation: str
    endpoint: str
    request: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    error: str | None = None


class MemorySystemAdapter(ABC):
    """Interface for any memory system under test."""

    @abstractmethod
    def reset(self, namespace: str) -> None:
        """Delete all memories in a namespace. Use only for test isolation."""

    @abstractmethod
    def ingest(self, memories: list[dict[str, Any]], namespace: str) -> list[str]:
        """Bulk-load memory records. Returns list of assigned IDs."""

    @abstractmethod
    def ingest_one(self, memory: dict[str, Any], namespace: str) -> str:
        """Ingest a single memory. Returns its assigned ID."""

    @abstractmethod
    def search(self, query: str, namespace: str, top_k: int = 10) -> RetrievalResult:
        """Semantic/hybrid search. Returns ranked results."""

    @abstractmethod
    def get_by_id(self, memory_id: str) -> MemoryRecord | None:
        """Retrieve a specific memory by its ID."""

    @abstractmethod
    def list_all(self, namespace: str, limit: int = 1000) -> list[MemoryRecord]:
        """List memories in a namespace (for verification)."""

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a single memory."""

    def get_context(self, query: str, namespace: str, max_tokens: int = 4000) -> RetrievalResult:
        """Token-budgeted context retrieval. Falls back to search if not supported."""
        return self.search(query, namespace, top_k=20)

    def get_trace(self) -> list[TraceEntry]:
        """Return interaction trace for the current session. Optional."""
        return []

    def clear_trace(self) -> None:
        """Clear the interaction trace. Optional."""

    def info(self) -> dict[str, Any]:
        """Return system metadata (name, version, config). Optional."""
        return {}
