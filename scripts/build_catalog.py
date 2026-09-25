#!/usr/bin/env python3
"""Generate normalized/catalog.json — a machine-readable index of all 20 experiments."""

import json, os
from pathlib import Path
from collections import Counter

NORMALIZED = Path(__file__).resolve().parent.parent / "normalized"

EXPERIMENT_THEMES = {
    "experiment_01_temporal_traps": {
        "theme": "Temporal Traps",
        "story_world": "Northstar Array Observatory",
        "description": "Objective event chronology, contemporaneous belief, later reconstruction, and current operating state frequently differ.",
        "adversarial_patterns": ["stale references", "belief vs fact", "retroactive correction", "temporal ordering", "scoped exceptions"],
    },
    "experiment_02_false_consensus": {
        "theme": "False Consensus",
        "story_world": "Nightglass Festival",
        "description": "One obsolete number propagates through derivative documents to create the illusion of consensus; contrasted with genuine independent consensus.",
        "adversarial_patterns": ["citation cascade", "duplicate volume", "rumor propagation", "retrieval amplification", "source authority"],
    },
    "experiment_03_entity_identity_collision": {
        "theme": "Entity Identity Collision",
        "story_world": "Thornfield Biotech",
        "description": "Multiple entities share similar names, aliases, or surface forms, requiring disambiguation under ambiguity.",
        "adversarial_patterns": ["name collision", "alias confusion", "entity merging", "context-dependent identity"],
    },
    "experiment_04_scope_context_partial_truth": {
        "theme": "Scope, Context & Partial Truth",
        "story_world": "Thornfield Biotech",
        "description": "Claims that are true in one scope (time, department, role) are false in another; partial truths must be qualified.",
        "adversarial_patterns": ["scope-dependent truth", "partial truth", "overgeneralization", "context collapse"],
    },
    "experiment_05_contested_reality": {
        "theme": "Contested Reality",
        "story_world": "Thornfield Biotech",
        "description": "Multiple parties disagree about facts; the system must represent disagreement without collapsing to one view.",
        "adversarial_patterns": ["conflicting claims", "perspective-dependent truth", "disputed evidence", "confidence calibration"],
    },
    "experiment_06_evidence_lineage": {
        "theme": "Evidence Lineage",
        "story_world": "Thornfield Biotech",
        "description": "Claims derive from other claims through chains of inference; the system must track provenance and detect cycles.",
        "adversarial_patterns": ["derivation chains", "circular reasoning", "missing provenance", "independent root counting"],
    },
    "experiment_07_shape_of_not_known": {
        "theme": "Shape of Not-Known",
        "story_world": "Thornfield Biotech",
        "description": "Questions whose answers are genuinely unknown, unanswerable, or require abstention rather than a fabricated response.",
        "adversarial_patterns": ["missing data", "unanswerable queries", "negative inference", "premise invalidity", "abstention triggers"],
    },
    "experiment_08_episode_reconstruction": {
        "theme": "Episode Reconstruction",
        "story_world": "Kestrel Scheduler Migration",
        "description": "Reconstructing multi-step episodes from fragmented, out-of-order observations across different temporal windows.",
        "adversarial_patterns": ["temporal fragmentation", "out-of-order ingestion", "episode boundaries", "partial observation"],
    },
    "experiment_09_causal_attribution": {
        "theme": "Causal Attribution",
        "story_world": "Kestrel Scheduler Migration",
        "description": "Distinguishing correlation from causation, tracking causal chains, and avoiding post-hoc attribution errors.",
        "adversarial_patterns": ["spurious correlation", "confounded causes", "causal chain breaks", "post-hoc reasoning"],
    },
    "experiment_10_kestrel_full_corpus": {
        "theme": "Kestrel Full Corpus",
        "story_world": "Kestrel Scheduler Migration",
        "description": "Complete corpus combining episode reconstruction and causal reasoning at scale with delivery-run invariants.",
        "adversarial_patterns": ["scale", "cross-episode reasoning", "run invariants", "temporal span"],
    },
    "experiment_11_forgetting_retraction_deletion": {
        "theme": "Forgetting, Retraction & Deletion",
        "story_world": "Verdant Municipal Water District",
        "description": "Memories that should be forgotten, retracted, or deleted — testing whether the system respects removal signals.",
        "adversarial_patterns": ["soft deletion", "hard deletion", "retraction", "right to be forgotten", "tombstone reasoning"],
    },
    "experiment_12_privacy_namespace_isolation": {
        "theme": "Privacy & Namespace Isolation",
        "story_world": "Palomar Municipal Services",
        "description": "Multi-tenant data isolation where queries must respect access control boundaries and not leak across namespaces.",
        "adversarial_patterns": ["cross-tenant leakage", "access control", "namespace boundaries", "aggregation inference"],
    },
    "experiment_13_consolidation_summarization_drift": {
        "theme": "Consolidation & Summarization Drift",
        "story_world": "Halcyon Brewing Cooperative",
        "description": "Information distortion through progressive summarization — each layer loses nuance, flattens scope, or shifts meaning.",
        "adversarial_patterns": ["summarization loss", "layer drift", "detail flattening", "meaning shift"],
    },
    "experiment_14_semantic_near_miss": {
        "theme": "Semantic Near-Miss & Distractor Resistance",
        "story_world": "Ridgeline Alpine Rescue",
        "description": "Semantically similar but factually distinct memories that a retrieval system might conflate.",
        "adversarial_patterns": ["near-miss retrieval", "semantic similarity traps", "distractor confusion", "surface-form matching"],
    },
    "experiment_15_contradictory_metadata": {
        "theme": "Contradictory Metadata",
        "story_world": "Ashford County Historical Archive",
        "description": "Metadata (timestamps, source labels, confidence scores) contradicts the content of the memories themselves.",
        "adversarial_patterns": ["metadata-content conflict", "timestamp inconsistency", "confidence miscalibration", "label error"],
    },
    "experiment_16_multi_hop_dependencies": {
        "theme": "Multi-Hop Dependencies",
        "story_world": "Cascadia Transit Authority",
        "description": "Answering queries requires chaining information across multiple memories in sequence.",
        "adversarial_patterns": ["multi-hop reasoning", "chain breaks", "intermediate inference", "transitive dependencies"],
    },
    "experiment_17_belief_state_vs_objective": {
        "theme": "Belief State vs Objective Reality",
        "story_world": "Lakeshore Community Health Clinic",
        "description": "Agents hold beliefs that diverge from objective reality; the system must track both without conflation.",
        "adversarial_patterns": ["belief-reality divergence", "agent perspective", "belief update lag", "objective ground truth"],
    },
    "experiment_18_counterfactual_negative": {
        "theme": "Counterfactual & Negative Reasoning",
        "story_world": "Cedarpoint Unified School District",
        "description": "Reasoning about events that did not happen, conditions that do not hold, and counterfactual scenarios.",
        "adversarial_patterns": ["negative evidence", "absence of event", "counterfactual queries", "closed-world assumption"],
    },
    "experiment_19_repeated_exposure": {
        "theme": "Repeated Exposure & Confidence Inflation",
        "story_world": "Pinehurst Property Management",
        "description": "Repeated exposure to the same claim inflates confidence without adding new evidence.",
        "adversarial_patterns": ["repetition bias", "confidence inflation", "echo amplification", "evidence-free reinforcement"],
    },
    "experiment_20_scope_boundary": {
        "theme": "Cross-Context Transfer & Scope Boundary Violation",
        "story_world": "Mariner's Wharf Redevelopment Project",
        "description": "Information valid in one context (project, jurisdiction, role, time) is incorrectly applied to another.",
        "adversarial_patterns": ["scope violation", "cross-context transfer", "role-based boundaries", "jurisdictional limits"],
    },
}


def build_catalog():
    catalog = {
        "version": "1.0",
        "generated_by": "build_catalog.py",
        "schema": {
            "memory_keys": 24,
            "query_keys": 15,
            "min_memories": MIN_MEMORIES,
            "min_queries": MIN_QUERIES,
        },
        "experiments": [],
    }

    for exp_dir in sorted(NORMALIZED.glob("experiment_*")):
        name = exp_dir.name
        meta = EXPERIMENT_THEMES.get(name, {})

        mems = [json.loads(l) for l in open(exp_dir / "memories.jsonl")]
        qs = [json.loads(l) for l in open(exp_dir / "queries.jsonl")]

        roles = dict(Counter(m["truth_role"] for m in mems).most_common())
        cats = dict(Counter(q["category"] for q in qs).most_common())
        mtypes = dict(Counter(m["memory_type"] for m in mems).most_common())
        diffs = dict(Counter(q.get("difficulty", "medium") for q in qs).most_common())

        files = sorted(f.name for f in exp_dir.iterdir() if f.is_file())

        entry = {
            "directory": name,
            "experiment_number": int(name.split("_")[1]),
            "theme": meta.get("theme", ""),
            "story_world": meta.get("story_world", ""),
            "description": meta.get("description", ""),
            "adversarial_patterns": meta.get("adversarial_patterns", []),
            "counts": {
                "memories": len(mems),
                "queries": len(qs),
                "truth_roles": len(roles),
                "query_categories": len(cats),
                "memory_types": len(mtypes),
            },
            "truth_roles": roles,
            "query_categories": cats,
            "difficulty_distribution": diffs,
            "files": files,
            "has_extensions": (exp_dir / "extensions.jsonl").exists(),
            "has_query_extensions": (exp_dir / "query_extensions.jsonl").exists(),
            "has_ingestion_variants": (exp_dir / "ingestion_chronological.jsonl").exists(),
            "has_seed_memories": (exp_dir / "seed_memories.jsonl").exists(),
            "has_truth_state": (exp_dir / "truth_state.json").exists(),
            "has_provenance": (exp_dir / "provenance.json").exists(),
        }
        catalog["experiments"].append(entry)

    total_mems = sum(e["counts"]["memories"] for e in catalog["experiments"])
    total_qs = sum(e["counts"]["queries"] for e in catalog["experiments"])
    catalog["totals"] = {
        "experiments": len(catalog["experiments"]),
        "memories": total_mems,
        "queries": total_qs,
    }

    return catalog


MIN_MEMORIES = 200
MIN_QUERIES = 75

if __name__ == "__main__":
    catalog = build_catalog()
    out_path = NORMALIZED / "catalog.json"
    with open(out_path, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"Catalog written to {out_path}")
    print(f"  {catalog['totals']['experiments']} experiments, "
          f"{catalog['totals']['memories']} memories, "
          f"{catalog['totals']['queries']} queries")
