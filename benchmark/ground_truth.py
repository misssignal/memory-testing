"""Generate benchmark test cases from the corpus index.

Each function returns a list of test-case dicts matching the schema in cases/.
All ground truth is derived deterministically from the corpus — no LLM involved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from corpus_loader import CorpusIndex, load_corpus


def _case(id: str, category: str, query: str, expected: dict, **extra) -> dict:
    c = {"id": id, "category": category, "query": query, "expected": expected}
    c.update(extra)
    return c


def point_retrieval_cases(idx: CorpusIndex) -> list[dict]:
    """Cases where a directly relevant memory should be retrieved."""
    cases = []
    n = 0
    for r in idx.by_expected_behavior.get("retrieve_relevant", [])[:40]:
        n += 1
        cases.append(_case(
            id=f"retrieval_{n:03d}",
            category="point_retrieval",
            query=r["text"],
            expected={
                "relevant_memory_ids": [r["id"]],
                "facts": [{"subject": r["subject"], "predicate": r["predicate"], "object": r["object"]}],
                "allow_unknown": False,
            },
        ))
    return cases


def temporal_latest_cases(idx: CorpusIndex) -> list[dict]:
    """Queries that require returning the latest active fact, not a superseded one."""
    cases = []
    for (subj, pred), chain in idx.supersession_chains.items():
        active = [r for r in chain if r["status"] == "active"]
        superseded = [r for r in chain if r["status"] == "superseded"]
        if not active:
            continue
        latest = active[-1]
        cases.append(_case(
            id=f"temporal_latest_{subj.lower().replace(' ', '_')}_{pred}",
            category="temporal_latest",
            query=f"What is {subj}'s current {pred.replace('_', ' ')}?",
            expected={
                "facts": [{"subject": subj, "predicate": pred, "object": latest["object"]}],
                "relevant_memory_ids": [latest["id"]],
                "must_not_use_as_current": [r["id"] for r in superseded],
                "allow_unknown": False,
                "must_surface_conflict": False,
            },
        ))
    return cases


def temporal_history_cases(idx: CorpusIndex) -> list[dict]:
    """Queries that require reconstructing a timeline of changes."""
    cases = []
    for (subj, pred), chain in idx.supersession_chains.items():
        if len(chain) < 2:
            continue
        ordered = sorted(chain, key=lambda r: r["timestamp"])
        cases.append(_case(
            id=f"temporal_history_{subj.lower().replace(' ', '_')}_{pred}",
            category="temporal_history",
            query=f"How has {subj}'s {pred.replace('_', ' ')} changed over time?",
            expected={
                "ordered_facts": [
                    {"timestamp": r["timestamp"], "object": r["object"], "memory_id": r["id"]}
                    for r in ordered
                ],
                "expected_count": len(ordered),
                "allow_unknown": False,
            },
        ))

    for subj in idx.projects:
        events = [r for r in idx.by_subject.get(subj, []) if r["memory_type"] == "project_event"]
        if len(events) < 3:
            continue
        ordered = sorted(events, key=lambda r: r["timestamp"])
        cases.append(_case(
            id=f"temporal_history_{subj.lower()}_lifecycle",
            category="temporal_history",
            query=f"What is the history of project {subj}?",
            expected={
                "ordered_facts": [
                    {"timestamp": r["timestamp"], "object": r["object"], "memory_id": r["id"]}
                    for r in ordered
                ],
                "expected_count": len(ordered),
                "allow_unknown": False,
            },
        ))
    return cases


def supersession_cases(idx: CorpusIndex) -> list[dict]:
    """Test that superseded records are not treated as current, but remain recoverable."""
    cases = []
    for (subj, pred), chain in idx.supersession_chains.items():
        active = [r for r in chain if r["status"] == "active"]
        superseded = [r for r in chain if r["status"] == "superseded"]
        if not active or not superseded:
            continue
        latest = active[-1]
        earliest_superseded = superseded[0]
        cases.append(_case(
            id=f"supersession_{subj.lower().replace(' ', '_')}_{pred}",
            category="supersession",
            query=f"What is {subj}'s {pred.replace('_', ' ')}?",
            expected={
                "current_fact": {"subject": subj, "predicate": pred, "object": latest["object"]},
                "current_id": latest["id"],
                "superseded_ids": [r["id"] for r in superseded],
                "superseded_objects": [r["object"] for r in superseded],
                "historical_query": f"What was {subj}'s previous {pred.replace('_', ' ')}?",
                "historical_answer": earliest_superseded["object"],
            },
        ))
    return cases


def contradiction_cases(idx: CorpusIndex) -> list[dict]:
    """Test that unresolved contradictions are surfaced, not silently resolved."""
    cases = []
    for (subj, pred), group in idx.conflict_groups.items():
        if len(group) < 2:
            continue
        cases.append(_case(
            id=f"contradiction_{subj.lower().replace(' ', '_')}_{pred}_{len(cases):02d}",
            category="contradiction",
            query=f"What is {subj}'s {pred.replace('_', ' ')}?",
            expected={
                "competing_claims": [
                    {"object": r["object"], "confidence": r["confidence"], "memory_id": r["id"]}
                    for r in group
                ],
                "must_surface_conflict": True,
                "allow_unknown": True,
                "relevant_memory_ids": [r["id"] for r in group],
            },
        ))
        if len(cases) >= 20:
            break
    return cases


def uncertainty_cases(idx: CorpusIndex) -> list[dict]:
    """Test that uncertain claims are not presented as definitive."""
    cases = []
    uncertain = [r for r in idx.by_status.get("uncertain", []) if r["confidence"] < 0.6]
    for r in uncertain[:15]:
        cases.append(_case(
            id=f"uncertainty_{len(cases):03d}",
            category="uncertainty",
            query=r["text"].rstrip(".") + "?",
            expected={
                "facts": [{"subject": r["subject"], "predicate": r["predicate"], "object": r["object"]}],
                "relevant_memory_ids": [r["id"]],
                "confidence": r["confidence"],
                "status": r["status"],
                "must_preserve_uncertainty": True,
                "allow_unknown": True,
            },
        ))
    return cases


def alias_cases(idx: CorpusIndex) -> list[dict]:
    """Test entity resolution across aliases."""
    cases = []
    for entity, aliases in idx.alias_map.items():
        if not aliases:
            continue
        entity_recs = idx.by_subject.get(entity, [])
        if len(entity_recs) < 5:
            continue
        sample_ids = [r["id"] for r in entity_recs[:10]]
        cases.append(_case(
            id=f"alias_{entity.lower().replace(' ', '_')}",
            category="alias",
            query=f"What do you know about {aliases[0]}?",
            expected={
                "canonical_entity": entity,
                "aliases": aliases,
                "should_resolve_to": entity,
                "sample_relevant_ids": sample_ids,
                "allow_unknown": False,
            },
        ))

    alias_in_text = [r for r in idx.records if "alias" in r["text"].lower() and "referred to" in r["text"].lower()]
    for r in alias_in_text[:5]:
        m = re.search(r"referred to (\w+) by the alias '([^']+)'", r["text"])
        if not m:
            continue
        entity_name, alias_val = m.group(1), m.group(2)
        cases.append(_case(
            id=f"alias_text_{alias_val.lower().replace('-', '_').replace(' ', '_')}",
            category="alias",
            query=f"What is {alias_val}?",
            expected={
                "canonical_entity": entity_name,
                "aliases": [alias_val],
                "should_resolve_to": entity_name,
                "relevant_memory_ids": [r["id"]],
                "allow_unknown": False,
            },
        ))
    return cases


def exact_duplicate_cases(idx: CorpusIndex) -> list[dict]:
    """Test that exact duplicates don't inflate ranking or confidence."""
    cases = []
    sorted_clusters = sorted(idx.duplicate_clusters.items(), key=lambda x: -len(x[1]))
    for text, ids in sorted_clusters[:10]:
        rec = idx.by_id[ids[0]]
        cases.append(_case(
            id=f"exact_dup_{len(cases):03d}",
            category="exact_duplicate",
            query=text,
            expected={
                "duplicate_ids": ids,
                "cluster_size": len(ids),
                "canonical_text": text,
                "subject": rec["subject"],
                "should_not_inflate_confidence": True,
            },
        ))
    return cases


def semantic_duplicate_cases(idx: CorpusIndex) -> list[dict]:
    """Test that paraphrases are recognized as describing the same fact."""
    cases = []
    para_recs = [r for r in idx.records if r["source_id"].startswith("para-src-")]
    for r in para_recs[:10]:
        m = re.match(r"para-src-(\d+)-", r["source_id"])
        if not m:
            continue
        orig_src = f"src-{m.group(1)}"
        originals = idx.by_source_id.get(orig_src, [])
        matching = [o for o in originals if o["text"].lower().rstrip(".") in r["text"].lower()
                     or r["text"].replace("Paraphrased recollection: ", "").rstrip(".").lower()
                     == o["text"].rstrip(".").lower()]
        if not matching:
            matching = originals[:1]
        if not matching:
            continue
        cases.append(_case(
            id=f"semantic_dup_{len(cases):03d}",
            category="semantic_duplicate",
            query=r["text"],
            expected={
                "paraphrase_id": r["id"],
                "original_ids": [o["id"] for o in matching],
                "original_text": matching[0]["text"],
                "paraphrase_text": r["text"],
            },
        ))
    return cases


def provenance_cases(idx: CorpusIndex) -> list[dict]:
    """Test whether the system can trace claims back to source memories."""
    cases = []
    for r in idx.by_expected_behavior.get("retrieve_relevant", [])[:15]:
        cases.append(_case(
            id=f"provenance_{len(cases):03d}",
            category="provenance",
            query=f"What do you know about {r['subject']} and {r['predicate'].replace('_', ' ')}?",
            expected={
                "supporting_memory_ids": [r["id"]],
                "source_type": r["source_type"],
                "source_id": r["source_id"],
                "claim": r["text"],
            },
        ))
    return cases


def distractor_cases(idx: CorpusIndex) -> list[dict]:
    """Test resistance to retrieving semantically similar but wrong records."""
    cases = []
    for (subj, pred), chain in idx.supersession_chains.items():
        active = [r for r in chain if r["status"] == "active"]
        superseded = [r for r in chain if r["status"] == "superseded"]
        if not active or not superseded:
            continue
        latest = active[-1]
        # the superseded records are distractors for a current-state query
        cases.append(_case(
            id=f"distractor_{subj.lower().replace(' ', '_')}_{pred}",
            category="distractor",
            query=f"What is {subj}'s current {pred.replace('_', ' ')}?",
            expected={
                "correct_id": latest["id"],
                "correct_object": latest["object"],
                "distractor_ids": [r["id"] for r in superseded],
                "distractor_objects": [r["object"] for r in superseded],
            },
        ))

    # duplicate-heavy distractors: query a fact that appears N times as stale
    sorted_clusters = sorted(idx.duplicate_clusters.items(), key=lambda x: -len(x[1]))
    for text, ids in sorted_clusters[:3]:
        rec = idx.by_id[ids[0]]
        if rec["status"] in ("superseded", "archived"):
            cases.append(_case(
                id=f"distractor_dup_heavy_{len(cases):03d}",
                category="distractor",
                query=text,
                expected={
                    "distractor_ids": ids,
                    "distractor_count": len(ids),
                    "note": "High duplicate count should not make stale fact appear more current",
                },
            ))
    return cases


def abstention_cases(idx: CorpusIndex) -> list[dict]:
    """Queries the corpus cannot answer — correct behavior is 'unknown'."""
    return [
        _case(
            id="abstention_001",
            category="abstention",
            query="What is Morgan Vale's favorite color?",
            expected={"allow_unknown": True, "must_abstain": True,
                      "note": "No memory records about favorite color exist"},
        ),
        _case(
            id="abstention_002",
            category="abstention",
            query="When did Project Phoenix launch?",
            expected={"allow_unknown": True, "must_abstain": True,
                      "note": "Project Phoenix does not exist in the corpus"},
        ),
        _case(
            id="abstention_003",
            category="abstention",
            query="What is Riley Chen's salary?",
            expected={"allow_unknown": True, "must_abstain": True,
                      "note": "No salary information exists in the corpus"},
        ),
        _case(
            id="abstention_004",
            category="abstention",
            query="Who founded Acme Robotics?",
            expected={"allow_unknown": True, "must_abstain": True,
                      "note": "Acme Robotics appears as a project host but no founding info exists"},
        ),
        _case(
            id="abstention_false_premise_001",
            category="abstention",
            query="Why did Morgan Vale switch from Rust to Go?",
            expected={"allow_unknown": True, "must_abstain": True,
                      "note": "Morgan's latest language is Rust — the premise (switched away) is false"},
        ),
    ]


def generate_all_cases(corpus_path: str | Path) -> dict[str, list[dict]]:
    idx = load_corpus(corpus_path)
    return {
        "retrieval": point_retrieval_cases(idx),
        "temporal": temporal_latest_cases(idx) + temporal_history_cases(idx),
        "supersession": supersession_cases(idx),
        "contradiction": contradiction_cases(idx),
        "uncertainty": uncertainty_cases(idx),
        "aliases": alias_cases(idx),
        "exact_duplicate": exact_duplicate_cases(idx),
        "semantic_duplicate": semantic_duplicate_cases(idx),
        "provenance": provenance_cases(idx),
        "distractor": distractor_cases(idx),
        "abstention": abstention_cases(idx),
    }


def write_cases(corpus_path: str | Path, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_cases = generate_all_cases(corpus_path)
    total = 0
    for category, cases in all_cases.items():
        outfile = output_dir / f"{category}.jsonl"
        with open(outfile, "w") as f:
            for c in cases:
                f.write(json.dumps(c) + "\n")
        total += len(cases)
        print(f"  {category}: {len(cases)} cases -> {outfile}")
    print(f"  total: {total} cases")


if __name__ == "__main__":
    import sys
    corpus = sys.argv[1] if len(sys.argv) > 1 else "corpus/fake_becca"
    write_cases(corpus, "cases")
