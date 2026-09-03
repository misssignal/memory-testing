"""PiyAPI REST adapter — talks directly to api.piyapi.cloud via urllib.

Reads PIYAPI_API_KEY from the environment. Never logs or prints the key.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from typing import Any

from .base import (
    MemorySystemAdapter,
    MemoryRecord,
    RetrievalResult,
    TraceEntry,
)


class PiyAPIRestAdapter(MemorySystemAdapter):
    def __init__(self, base_url: str = "https://api.piyapi.cloud/api/v1"):
        self._base = base_url.rstrip("/")
        self._key = os.environ["PIYAPI_API_KEY"]
        self._headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }
        self._trace: list[TraceEntry] = []

    def _request(
        self, method: str, endpoint: str, body: dict | None = None, timeout: int = 30
    ) -> tuple[int, dict]:
        url = f"{self._base}/{endpoint.lstrip('/')}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self._headers, method=method)

        entry = TraceEntry(operation=method, endpoint=endpoint, request=body or {})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read())
                entry.response = resp
                entry.latency_ms = (time.monotonic() - t0) * 1000
                self._trace.append(entry)
                return r.status, resp
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            try:
                resp = json.loads(body_text)
            except json.JSONDecodeError:
                resp = {"raw": body_text}
            entry.response = resp
            entry.error = f"HTTP {e.code}"
            entry.latency_ms = (time.monotonic() - t0) * 1000
            self._trace.append(entry)
            return e.code, resp

    def _to_record(self, raw: dict) -> MemoryRecord:
        return MemoryRecord(
            id=raw.get("id", ""),
            content=raw.get("content", ""),
            timestamp=raw.get("created_at") or raw.get("event_time"),
            namespace=raw.get("namespace"),
            tags=raw.get("tags", []),
            metadata={
                k: raw[k]
                for k in (
                    "importance_score",
                    "confidence_score",
                    "memory_type",
                    "is_pinned",
                    "version",
                    "is_deprecated",
                    "data_classification",
                    "contains_phi",
                )
                if k in raw
            },
            raw=raw,
        )

    # --- interface ---

    def reset(self, namespace: str) -> None:
        mems = self.list_all(namespace, limit=5000)
        for m in mems:
            self.delete(m.id)

    def ingest(self, memories: list[dict[str, Any]], namespace: str) -> list[str]:
        ids = []
        for m in memories:
            ids.append(self.ingest_one(m, namespace))
        return ids

    def ingest_one(self, memory: dict[str, Any], namespace: str) -> str:
        payload: dict[str, Any] = {
            "content": memory.get("text", memory.get("content", "")),
            "namespace": namespace,
        }
        tags = memory.get("tags", [])
        if tags:
            payload["tags"] = tags
        meta = {}
        for k in ("subject", "predicate", "object", "status", "confidence",
                   "source_type", "source_id", "supersedes", "aliases",
                   "expected_behavior", "memory_type", "timestamp"):
            if k in memory and memory[k] is not None:
                meta[k] = memory[k]
        if meta:
            payload["metadata"] = meta
        status, resp = self._request("POST", "memories", payload)
        return resp.get("memory", resp).get("id", "")

    def search(self, query: str, namespace: str, top_k: int = 10) -> RetrievalResult:
        t0 = time.monotonic()
        status, resp = self._request("POST", "search/hybrid", {
            "query": query,
            "namespace": namespace,
            "limit": top_k,
        })
        latency = (time.monotonic() - t0) * 1000
        if status != 200:
            return RetrievalResult(
                query=query, memories=[], scores=[],
                raw_response=resp, latency_ms=latency,
                error=f"HTTP {status}",
            )
        results = resp.get("results", [])
        memories = [self._to_record(r.get("memory", r)) for r in results]
        scores = [
            r.get("hybridScore", r.get("similarity", r.get("combined_score", 0.0)))
            for r in results
        ]
        return RetrievalResult(
            query=query, memories=memories, scores=scores,
            raw_response=resp, latency_ms=latency,
        )

    def get_by_id(self, memory_id: str) -> MemoryRecord | None:
        status, resp = self._request("GET", f"memories/{memory_id}")
        if status != 200:
            return None
        data = resp.get("memory", resp)
        return self._to_record(data)

    def list_all(self, namespace: str, limit: int = 1000) -> list[MemoryRecord]:
        status, resp = self._request(
            "GET", f"memories?namespace={namespace}&limit={limit}"
        )
        if status != 200:
            return []
        return [self._to_record(m) for m in resp.get("memories", [])]

    def delete(self, memory_id: str) -> bool:
        status, _ = self._request("DELETE", f"memories/{memory_id}")
        return status == 200

    def get_context(self, query: str, namespace: str, max_tokens: int = 4000) -> RetrievalResult:
        t0 = time.monotonic()
        status, resp = self._request("POST", "context/retrieve", {
            "query": query,
            "namespace": namespace,
            "max_tokens": max_tokens,
        })
        latency = (time.monotonic() - t0) * 1000
        if status != 200:
            return RetrievalResult(
                query=query, memories=[], scores=[],
                raw_response=resp, latency_ms=latency,
                error=f"HTTP {status}",
            )
        memories = [self._to_record(m) for m in resp.get("memories", [])]
        return RetrievalResult(
            query=query, memories=memories, scores=[],
            raw_response=resp, latency_ms=latency,
        )

    def get_trace(self) -> list[TraceEntry]:
        return list(self._trace)

    def clear_trace(self) -> None:
        self._trace.clear()

    def info(self) -> dict[str, Any]:
        _, resp = self._request("GET", "/")
        return {
            "name": "PiyAPI REST",
            "base_url": self._base,
            "api_info": resp,
        }
