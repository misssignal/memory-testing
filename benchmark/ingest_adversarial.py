"""Ingest adversarial experiment records into PiyAPI namespaces."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://api.piyapi.cloud/api/v1"
KEY = os.environ["PIYAPI_API_KEY"]
HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
}
DELAY = 0.6


def post_memory(payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/memories", data=data, headers=HEADERS, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body}


def ingest_file(jsonl_path: str, namespace: str, id_map_path: str,
                start: int = 0, count: int | None = None):
    records = []
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    # Load existing id_map if present
    id_map: dict[str, str] = {}
    if os.path.exists(id_map_path):
        with open(id_map_path) as f:
            id_map = json.load(f)

    end = len(records) if count is None else min(start + count, len(records))
    batch = records[start:end]
    print(f"Ingesting records {start}-{end-1} ({len(batch)} records) into '{namespace}'")
    print(f"Existing id_map: {len(id_map)} entries")

    for i, rec in enumerate(batch):
        mid = rec["memory_id"]
        if mid in id_map:
            print(f"  [{start+i:3d}] SKIP {mid} (already ingested)")
            continue

        payload: dict = {
            "content": rec["text"],
            "namespace": namespace,
        }
        tags = rec.get("tags", [])
        if tags:
            payload["tags"] = tags

        meta: dict = {}
        for k in ("subject", "predicate", "object", "memory_type", "truth_role",
                   "belief_holder", "confidence", "source_id", "source_type",
                   "event_time", "observation_time", "ingestion_time",
                   "experiment", "story_id", "evidence_root"):
            if k in rec and rec[k] is not None:
                meta[k] = rec[k]

        # Store relational fields
        for k in ("derived_from", "supersedes", "contradicts", "duplicates", "aliases"):
            if rec.get(k):
                meta[k] = rec[k]

        if rec.get("scope"):
            meta["scope"] = json.dumps(rec["scope"])

        meta["corpus_id"] = mid
        payload["metadata"] = meta

        status, resp = post_memory(payload)
        piy_id = resp.get("memory", resp).get("id", "???")

        if status in (200, 201):
            id_map[mid] = piy_id
            print(f"  [{start+i:3d}] OK   {mid} -> {piy_id}")
        else:
            print(f"  [{start+i:3d}] ERR  {mid} HTTP {status}: {resp}")

        time.sleep(DELAY)

    # Save updated id_map
    with open(id_map_path, "w") as f:
        json.dump(id_map, f, indent=2)
    print(f"\nDone. id_map: {len(id_map)} entries -> {id_map_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python ingest_adversarial.py <jsonl_path> <namespace> <id_map_path> [start] [count]")
        sys.exit(1)

    jsonl_path = sys.argv[1]
    namespace = sys.argv[2]
    id_map_path = sys.argv[3]
    start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    count = int(sys.argv[5]) if len(sys.argv) > 5 else None

    ingest_file(jsonl_path, namespace, id_map_path, start, count)
