"""Ingest fake_becca corpus into bench-micro-001 with degradation probes at checkpoints."""
from __future__ import annotations

import json
import os
import random
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

NAMESPACE = "bench-micro-001"
CORPUS_PATH = Path(__file__).parent / "corpus" / "fake_becca" / "memories.jsonl"
ID_MAP_PATH = Path(__file__).parent / "cases" / "micro_id_map.json"
PROBE_LOG_PATH = Path(__file__).parent / "degradation_probes.jsonl"
PROGRESS_PATH = Path(__file__).parent / "ingest_progress.json"

DELAY = 0.5
SEED = 42

# Asymmetric checkpoints — tighter early where degradation is steepest
CHECKPOINTS = {250, 500, 1000, 1750, 2500, 3500, 5000}

PROBE_QUERIES = [
    {
        "label": "db_preference",
        "query": "What is Morgan Vale's current preferred database?",
        "expected_subject": "Morgan Vale",
        "expected_predicate": "preferred_database",
        "notes": "Baseline at 18 records: MongoDB rank 1. At 118: not in top 5.",
    },
    {
        "label": "meeting_preference",
        "query": "What does Jamie Hart prefer for meetings?",
        "expected_subject": "Jamie Hart",
        "expected_predicate": "meeting_preference",
        "notes": "Baseline at 118: all 3 records in top 3.",
    },
    {
        "label": "atlas_alias",
        "query": "Tell me about atlas-svc",
        "expected_subject": "Atlas",
        "expected_tag": "atlas",
        "notes": "Alias metadata not indexed. At 118: only 1 Atlas record in top 5.",
    },
    {
        "label": "abstention_shoe",
        "query": "What is Riley Chen's shoe size?",
        "expected_answer": None,
        "notes": "Unanswerable. At 118: top_similarity=0.640, did not abstain.",
    },
    {
        "label": "cross_entity",
        "query": "What bugs has Harbor had?",
        "expected_tag": "harbor",
        "expected_predicate": "bug",
        "notes": "Cross-entity retrieval. Should find harbor+bug records.",
    },
    {
        "label": "kepler_decisions",
        "query": "What decisions were made about Kepler?",
        "expected_tag": "kepler",
        "expected_type": "decision",
        "notes": "Project-scoped retrieval for a specific memory type.",
    },
]


def api_request(method: str, endpoint: str, body: dict | None = None,
                timeout: int = 30) -> tuple[int, dict]:
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body_text)
        except json.JSONDecodeError:
            return e.code, {"raw": body_text}


def ingest_one(record: dict) -> str:
    payload: dict = {
        "content": record.get("text", record.get("content", "")),
        "namespace": NAMESPACE,
    }
    tags = record.get("tags", [])
    if tags:
        payload["tags"] = tags
    meta: dict = {}
    for k in ("subject", "predicate", "object", "status", "confidence",
               "source_type", "source_id", "supersedes", "aliases",
               "expected_behavior", "memory_type", "timestamp"):
        if k in record and record[k] is not None:
            meta[k] = record[k]
    meta["corpus_id"] = record["id"]
    if meta:
        payload["metadata"] = meta
    status, resp = api_request("POST", "memories", payload)
    return resp.get("memory", resp).get("id", "")


def run_probes(total_ingested: int) -> list[dict]:
    results = []
    for probe in PROBE_QUERIES:
        try:
            status, resp = api_request("POST", "search/hybrid", {
                "query": probe["query"],
                "namespace": NAMESPACE,
                "limit": 10,
            })
        except Exception as e:
            results.append({
                "label": probe["label"],
                "total_ingested": total_ingested,
                "error": str(e),
            })
            continue

        search_results = resp.get("results", [])
        memories = []
        for r in search_results:
            m = r.get("memory", r)
            memories.append({
                "id": m.get("id", ""),
                "content": m.get("content", "")[:120],
                "score": r.get("hybridScore", r.get("similarity", 0.0)),
                "subject": m.get("metadata", {}).get("subject", ""),
                "predicate": m.get("metadata", {}).get("predicate", ""),
                "memory_type": m.get("metadata", {}).get("memory_type", ""),
                "status": m.get("metadata", {}).get("status", ""),
                "tags": m.get("tags", []),
            })

        # Compute metrics
        top_score = memories[0]["score"] if memories else 0.0

        # Subject match in top-k
        exp_subj = probe.get("expected_subject", "")
        exp_pred = probe.get("expected_predicate", "")
        exp_tag = probe.get("expected_tag", "")
        exp_type = probe.get("expected_type", "")

        subject_hits = []
        predicate_hits = []
        tag_hits = []
        type_hits = []
        for i, m in enumerate(memories):
            if exp_subj and exp_subj.lower() in m["subject"].lower():
                subject_hits.append(i + 1)
            if exp_pred and m["predicate"] == exp_pred:
                predicate_hits.append(i + 1)
            if exp_tag and exp_tag in m.get("tags", []):
                tag_hits.append(i + 1)
            if exp_type and m["memory_type"] == exp_type:
                type_hits.append(i + 1)

        # Combined relevance: match on the primary expected field(s)
        relevant_ranks = []
        if exp_subj and exp_pred:
            for i, m in enumerate(memories):
                if (exp_subj.lower() in m["subject"].lower() and
                    m["predicate"] == exp_pred):
                    relevant_ranks.append(i + 1)
        elif exp_tag and exp_pred:
            for i, m in enumerate(memories):
                if exp_tag in m.get("tags", []) and m["predicate"] == exp_pred:
                    relevant_ranks.append(i + 1)
        elif exp_tag and exp_type:
            for i, m in enumerate(memories):
                if exp_tag in m.get("tags", []) and m["memory_type"] == exp_type:
                    relevant_ranks.append(i + 1)
        elif exp_tag:
            relevant_ranks = tag_hits
        elif exp_subj:
            relevant_ranks = subject_hits

        result = {
            "label": probe["label"],
            "total_ingested": total_ingested,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "result_count": len(memories),
            "top_score": round(top_score, 4),
            "top1_content": memories[0]["content"][:80] if memories else "",
            "top1_subject": memories[0]["subject"] if memories else "",
            "top1_predicate": memories[0]["predicate"] if memories else "",
            "subject_hits_at": subject_hits[:5],
            "predicate_hits_at": predicate_hits[:5],
            "tag_hits_at": tag_hits[:5],
            "relevant_ranks": relevant_ranks[:5],
            "first_relevant": relevant_ranks[0] if relevant_ranks else None,
            "relevant_in_top3": sum(1 for r in relevant_ranks if r <= 3),
            "relevant_in_top5": sum(1 for r in relevant_ranks if r <= 5),
            "relevant_in_top10": len(relevant_ranks),
        }
        results.append(result)
        time.sleep(0.8)

    return results


def save_probes(probes: list[dict]):
    with open(PROBE_LOG_PATH, "a") as f:
        for p in probes:
            f.write(json.dumps(p) + "\n")


def load_progress() -> dict:
    if PROGRESS_PATH.exists():
        with open(PROGRESS_PATH) as f:
            return json.load(f)
    return {"ingested_count": 0, "order": []}


def save_progress(progress: dict):
    with open(PROGRESS_PATH, "w") as f:
        json.dump(progress, f)


def main():
    # Load corpus
    all_records = []
    with open(CORPUS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                all_records.append(json.loads(line))
    print(f"Corpus: {len(all_records)} total records")

    # Load existing id_map
    id_map: dict[str, str] = {}
    if ID_MAP_PATH.exists():
        with open(ID_MAP_PATH) as f:
            id_map = json.load(f)
    already_ingested = set(id_map.keys())
    print(f"Already ingested: {len(already_ingested)}")

    # Filter out already-ingested, shuffle the rest
    remaining = [r for r in all_records if r["id"] not in already_ingested]
    rng = random.Random(SEED)
    rng.shuffle(remaining)
    print(f"Remaining to ingest: {len(remaining)}")

    # Load or init progress
    progress = load_progress()
    start_idx = progress["ingested_count"]
    if start_idx > 0:
        print(f"Resuming from record {start_idx}")

    total_in_ns = len(already_ingested) + start_idx

    # Optional: limit how many to do this run
    batch_limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(remaining)
    end_idx = min(start_idx + batch_limit, len(remaining))
    print(f"This run: records {start_idx} to {end_idx - 1} ({end_idx - start_idx} records)")
    print(f"Checkpoints: {sorted(CHECKPOINTS)}")
    print()

    # Run initial probe if at first run
    if total_in_ns > 0 and start_idx == 0:
        print(f"=== BASELINE PROBE at {total_in_ns} records ===")
        probes = run_probes(total_in_ns)
        save_probes(probes)
        for p in probes:
            fr = p.get("first_relevant")
            print(f"  {p['label']:25s} first_relevant={fr} in_top5={p['relevant_in_top5']} top_score={p['top_score']}")
        print()

    errors = 0
    for i in range(start_idx, end_idx):
        rec = remaining[i]
        cid = rec["id"]

        try:
            piy_id = ingest_one(rec)
        except Exception as e:
            print(f"  [{i:5d}] ERR {cid[:12]}... {e}")
            errors += 1
            if errors > 10:
                print("Too many errors, stopping.")
                break
            time.sleep(2)
            continue

        if piy_id and piy_id != "???":
            id_map[cid] = piy_id
            total_in_ns += 1
        else:
            print(f"  [{i:5d}] NO_ID {cid[:12]}...")

        # Progress update every 50
        if (i + 1) % 50 == 0:
            progress["ingested_count"] = i + 1
            save_progress(progress)
            with open(ID_MAP_PATH, "w") as f:
                json.dump(id_map, f)
            print(f"  ... {i + 1}/{end_idx} ingested (total in ns: {total_in_ns})")

        # Checkpoint probe
        if total_in_ns in CHECKPOINTS:
            print(f"\n=== CHECKPOINT PROBE at {total_in_ns} records ===")
            # Save state first
            progress["ingested_count"] = i + 1
            save_progress(progress)
            with open(ID_MAP_PATH, "w") as f:
                json.dump(id_map, f)

            probes = run_probes(total_in_ns)
            save_probes(probes)
            for p in probes:
                fr = p.get("first_relevant")
                print(f"  {p['label']:25s} first_relevant={fr} in_top5={p['relevant_in_top5']} top_score={p['top_score']}")
            print()

        time.sleep(DELAY)

    # Final save
    progress["ingested_count"] = min(end_idx, i + 1) if 'i' in dir() else end_idx
    save_progress(progress)
    with open(ID_MAP_PATH, "w") as f:
        json.dump(id_map, f)

    # Final probe
    print(f"\n=== FINAL PROBE at {total_in_ns} records ===")
    probes = run_probes(total_in_ns)
    save_probes(probes)
    for p in probes:
        fr = p.get("first_relevant")
        print(f"  {p['label']:25s} first_relevant={fr} in_top5={p['relevant_in_top5']} top_score={p['top_score']}")

    print(f"\nDone. Total in namespace: {total_in_ns}. ID map: {len(id_map)} entries.")
    print(f"Errors: {errors}")
    print(f"Probe log: {PROBE_LOG_PATH}")


if __name__ == "__main__":
    main()
