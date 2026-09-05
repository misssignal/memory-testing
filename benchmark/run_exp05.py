"""Blind retrieval benchmark for Experiment 05 against the PiyAPI REST API.

The importer is idempotent by corpus ID and never uploads development-only oracle
fields such as ``_oracle`` or ``truth_role``. Ground truth remains local.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[1]
    / "adversarial_memory_benchmark_exp05_contested_reality_v0.1"
    / "experiment_05_contested_reality"
)
BASE_URL = "https://api.piyapi.cloud/api/v1"
ORDER_FILES = {
    "chronological": "ingestion_chronological.jsonl",
    "shuffled": "ingestion_shuffled.jsonl",
    "late-arrival": "ingestion_late_arrival.jsonl",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def ordered_memories(order: str) -> list[dict]:
    memories = read_jsonl(ROOT / "memories.jsonl")
    by_id = {m["memory_id"]: m for m in memories}
    rows = read_jsonl(ROOT / ORDER_FILES[order])
    ids = [row["memory_id"] if isinstance(row, dict) else row for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(by_id):
        raise ValueError(f"{order} ordering is not a permutation of memories.jsonl")
    return [by_id[mid] for mid in ids]


def public_payload(memory: dict, namespace: str) -> dict:
    """Create the blind-system payload; omit every ground-truth/oracle label."""
    metadata = {
        "corpus_id": memory["memory_id"],
        "event_time": memory["event_time"],
        "observation_time": memory["observation_time"],
        "ingestion_time": memory["ingestion_time"],
        "memory_type": memory["memory_type"],
        "source_id": memory["source_id"],
        "source_type": memory["source_type"],
        "subject_text": memory["subject_text"],
        "predicate": memory["predicate"],
        "object": memory["object"],
        "scope": json.dumps(memory["scope"], sort_keys=True),
    }
    for field in ("derived_from", "supersedes", "contradicts", "aliases_used"):
        if memory.get(field):
            metadata[field] = memory[field]
    return {
        "content": memory["text"],
        "namespace": namespace,
        "tags": memory.get("tags", []),
        "metadata": metadata,
    }


class Client:
    def __init__(self) -> None:
        key = os.environ.get("PIYAPI_API_KEY")
        if not key:
            raise RuntimeError("PIYAPI_API_KEY is not set")
        self.headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def request(self, method: str, endpoint: str, body: dict | None = None) -> tuple[int, dict]:
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            f"{BASE_URL}/{endpoint.lstrip('/')}",
            data=data,
            headers=self.headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            raw = error.read().decode(errors="replace")
            try:
                return error.code, json.loads(raw)
            except json.JSONDecodeError:
                return error.code, {"raw": raw}
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as error:
            return 0, {"transport_error": str(error)}


def validate() -> None:
    memories = read_jsonl(ROOT / "memories.jsonl")
    queries = read_jsonl(ROOT / "queries.jsonl")
    ids = {m["memory_id"] for m in memories}
    if len(ids) != len(memories):
        raise ValueError("duplicate memory_id")
    for order in ORDER_FILES:
        ordered_memories(order)
    missing = {
        mid
        for query in queries
        for mid in query["relevant_memory_ids"] + query["distractor_memory_ids"]
        if mid not in ids
    }
    if missing:
        raise ValueError(f"query references missing IDs: {sorted(missing)}")
    print(f"OK: {len(memories)} memories, {len(queries)} queries, all references valid")


def ingest(
    order: str, namespace: str, map_path: Path, delay: float, count: int | None
) -> None:
    client = Client()
    memories = ordered_memories(order)
    id_map = json.loads(map_path.read_text()) if map_path.exists() else {}
    failures = 0
    pending = [memory for memory in memories if memory["memory_id"] not in id_map]
    if count is not None:
        pending = pending[:count]
    for index, memory in enumerate(pending, 1):
        corpus_id = memory["memory_id"]
        status, response, remote_id = 0, {}, ""
        for attempt in range(1, 4):
            status, response = client.request("POST", "memories", public_payload(memory, namespace))
            remote_id = response.get("memory", response).get("id", "")
            if status in (200, 201) and remote_id:
                break
            if status == 0 or status >= 500:
                print(f"[{index:03d}/{len(pending):03d}] RETRY {attempt}/3 HTTP {status}")
                time.sleep(attempt * 2)
                continue
            break
        if status not in (200, 201) or not remote_id:
            failures += 1
            print(f"[{index:03d}/{len(pending):03d}] ERROR {corpus_id} HTTP {status}")
            if failures >= 5:
                raise RuntimeError("stopping after five ingestion failures")
            continue
        id_map[corpus_id] = remote_id
        map_path.parent.mkdir(parents=True, exist_ok=True)
        map_path.write_text(json.dumps(id_map, indent=2, sort_keys=True) + "\n")
        if index % 20 == 0 or index == len(pending):
            print(f"[{index:03d}/{len(pending):03d}] mapped={len(id_map)}")
        time.sleep(delay)
    print(f"Done: mapped={len(id_map)}, failures={failures}, namespace={namespace}")


def extract_remote_id(result: dict) -> str:
    memory = result.get("memory", result)
    return memory.get("id", "")


def analyze(
    namespace: str,
    map_path: Path,
    limit: int,
    endpoint: str,
    category: str | None,
    query_ids: list[str],
    fully_mapped_only: bool,
    delay: float,
) -> None:
    client = Client()
    id_map = json.loads(map_path.read_text())
    reverse = {remote: corpus for corpus, remote in id_map.items()}
    queries = read_jsonl(ROOT / "queries.jsonl")
    if category:
        queries = [q for q in queries if q["category"] == category]
    if query_ids:
        wanted = set(query_ids)
        queries = [q for q in queries if q["query_id"] in wanted]
    if fully_mapped_only:
        mapped = set(id_map)
        queries = [q for q in queries if set(q["relevant_memory_ids"]) <= mapped]

    endpoint_label = endpoint.replace("/", "_")
    output = Path(__file__).parent / "runs" / f"exp05_{endpoint_label}_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    output.mkdir(parents=True)
    rows = []
    by_category = defaultdict(list)
    for index, query in enumerate(queries, 1):
        started = time.monotonic()
        status, response = client.request(
            "POST",
            endpoint,
            {"query": query["query"], "namespace": namespace, "limit": limit},
        )
        latency_ms = round((time.monotonic() - started) * 1000)
        results = response.get("results", []) if status == 200 else []
        returned = [reverse.get(extract_remote_id(item), "") for item in results]
        relevant = set(query["relevant_memory_ids"])
        distractors = set(query["distractor_memory_ids"])
        hits = [rank for rank, mid in enumerate(returned, 1) if mid in relevant]
        row = {
            "query_id": query["query_id"],
            "category": query["category"],
            "endpoint": endpoint,
            "http_status": status,
            "latency_ms": latency_ms,
            "recall_at_k": len(set(returned) & relevant) / len(relevant) if relevant else 1.0,
            "first_relevant_rank": hits[0] if hits else None,
            "distractors_at_k": len(set(returned) & distractors),
            "should_abstain": query["should_abstain"],
            "api_abstain": response.get("abstain", response.get("metadata", {}).get("abstain")),
            "returned_corpus_ids": returned,
        }
        rows.append(row)
        by_category[row["category"]].append(row)
        (output / "results.json").write_text(json.dumps(rows, indent=2) + "\n")
        print(
            f"[{index:03d}/{len(queries)}] {query['query_id']} "
            f"recall={row['recall_at_k']:.2f} first={row['first_relevant_rank']} "
            f"distractors={row['distractors_at_k']} {latency_ms}ms"
        )
        time.sleep(delay)

    summary = {}
    for name, group in sorted(by_category.items()):
        summary[name] = {
            "queries": len(group),
            "mean_recall_at_k": sum(r["recall_at_k"] for r in group) / len(group),
            "queries_with_any_relevant": sum(r["first_relevant_rank"] is not None for r in group),
            "distractors_returned": sum(r["distractors_at_k"] for r in group),
            "http_statuses": dict(Counter(r["http_status"] for r in group)),
        }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Results: {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    ingest_parser = sub.add_parser("ingest")
    ingest_parser.add_argument("--order", choices=ORDER_FILES, default="chronological")
    ingest_parser.add_argument("--namespace", default="exp05-chronological-v1")
    ingest_parser.add_argument("--id-map", type=Path, default=Path(__file__).parent / "cases" / "exp05_chronological_id_map.json")
    ingest_parser.add_argument("--delay", type=float, default=0.6)
    ingest_parser.add_argument("--count", type=int)
    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("--namespace", default="exp05-chronological-v1")
    analyze_parser.add_argument("--id-map", type=Path, default=Path(__file__).parent / "cases" / "exp05_chronological_id_map.json")
    analyze_parser.add_argument("--limit", type=int, default=10)
    analyze_parser.add_argument("--endpoint", choices=("search/hybrid", "search"), default="search/hybrid")
    analyze_parser.add_argument("--category")
    analyze_parser.add_argument("--query-id", action="append", default=[])
    analyze_parser.add_argument("--fully-mapped-only", action="store_true")
    analyze_parser.add_argument("--delay", type=float, default=0.8)
    args = parser.parse_args()
    if args.command == "validate":
        validate()
    elif args.command == "ingest":
        ingest(args.order, args.namespace, args.id_map, args.delay, args.count)
    else:
        analyze(
            args.namespace,
            args.id_map,
            args.limit,
            args.endpoint,
            args.category,
            args.query_id,
            args.fully_mapped_only,
            args.delay,
        )


if __name__ == "__main__":
    main()
