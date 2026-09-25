#!/usr/bin/env python3
"""Fix and expand Experiment 12 corpus to meet minimum targets (200+ memories, 75+ queries)."""

import json
import hashlib
import sys
from pathlib import Path
from collections import Counter
from copy import deepcopy


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def fix(exp_dir):
    exp_dir = Path(exp_dir)
    memories = [json.loads(l) for l in open(exp_dir / "memories.jsonl")]
    queries = [json.loads(l) for l in open(exp_dir / "queries.jsonl")]
    with open(exp_dir / "truth_state.json") as f:
        truth = json.load(f)

    mem_by_id = {m["memory_id"]: m for m in memories}
    print(f"Starting: {len(memories)} memories, {len(queries)} queries")

    new_memories = []
    new_queries = []

    def mem(mid, **kwargs):
        m = {
            "memory_id": mid,
            "experiment": "exp12_privacy_namespace_isolation",
            "story_id": "nexus_hub",
            "event_time": kwargs.get("event_time", "2032-03-01T10:00:00Z"),
            "observation_time": kwargs.get("observation_time", "2032-03-01T11:00:00Z"),
            "authored_time": kwargs.get("authored_time", "2032-03-01T12:00:00Z"),
            "ingestion_time": kwargs.get("ingestion_time", "2032-03-01T13:00:00Z"),
            "subject": kwargs.get("subject", ""),
            "predicate": kwargs.get("predicate", ""),
            "object": kwargs.get("object", ""),
            "text": kwargs["text"],
            "memory_type": kwargs.get("memory_type", "observation"),
            "truth_role": kwargs.get("truth_role", "current_truth"),
            "belief_holder": kwargs.get("belief_holder", "system"),
            "confidence": kwargs.get("confidence", 1.0),
            "source_id": kwargs.get("source_id", "nexus_ops"),
            "source_type": kwargs.get("source_type", "system_record"),
            "derived_from": kwargs.get("derived_from", []),
            "supersedes": kwargs.get("supersedes", []),
            "contradicts": kwargs.get("contradicts", []),
            "duplicates": kwargs.get("duplicates", []),
            "aliases": kwargs.get("aliases", []),
            "scope": kwargs["scope"],
            "tags": kwargs["tags"],
        }
        new_memories.append(m)
        return m

    def qry(qid, **kwargs):
        q = {
            "query_id": qid,
            "query": kwargs["query"],
            "category": kwargs["category"],
            "query_context": kwargs["query_context"],
            "expected_claims": kwargs.get("expected_claims", []),
            "acceptable_claims": kwargs.get("acceptable_claims", []),
            "forbidden_claims": kwargs.get("forbidden_claims", []),
            "relevant_memory_ids": kwargs.get("relevant_memory_ids", []),
            "distractor_memory_ids": kwargs.get("distractor_memory_ids", []),
            "requires_temporal_reasoning": kwargs.get("requires_temporal_reasoning", False),
            "difficulty": kwargs.get("difficulty", "medium"),
        }
        new_queries.append(q)
        return q

    next_mid = len(memories) + 1

    # ── Expand C05: Mixed-scope summary leakage ──────────────────────
    # Currently only 6 memories. Add newsletter drafts, redacted versions, editorial decisions.
    print("\nExpanding C05 (mixed-scope summary)...")

    mem(f"M{next_mid:04d}",
        text="The Q2 Innovation Spotlight draft initially included Prism Analytics' exact model accuracy of 94.7% on the AgriPredict benchmark, but the editorial team flagged this as proprietary.",
        subject="Innovation Spotlight", predicate="drafted_with", object="proprietary data",
        event_time="2032-06-20T09:00:00Z", observation_time="2032-06-20T10:00:00Z",
        authored_time="2032-06-20T11:00:00Z", ingestion_time="2032-06-20T12:00:00Z",
        scope={"tenant": "shared", "access_level": "facility_admin", "project": "", "shared_with": []},
        tags=["C05", "newsletter", "editorial"],
        source_id="P01", source_type="editorial_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The published Q2 Innovation Spotlight described Prism Analytics as having 'achieved a significant ML milestone in agricultural prediction' without specifying accuracy numbers.",
        subject="Innovation Spotlight Q2", predicate="published_with", object="redacted milestone",
        event_time="2032-06-25T09:00:00Z", observation_time="2032-06-25T10:00:00Z",
        authored_time="2032-06-25T11:00:00Z", ingestion_time="2032-06-25T12:00:00Z",
        scope={"tenant": "shared", "access_level": "guest", "project": "", "shared_with": []},
        tags=["C05", "newsletter", "published"],
        source_id="newsletter_system", source_type="publication",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Verdant Bio's Q2 newsletter section was revised three times to remove references to specific gene sequences used in the Canopy project's drought-resistant strain CR-42.",
        subject="Verdant Bio newsletter section", predicate="revised_to_remove", object="gene sequence references",
        event_time="2032-06-22T14:00:00Z", observation_time="2032-06-22T15:00:00Z",
        authored_time="2032-06-22T16:00:00Z", ingestion_time="2032-06-22T17:00:00Z",
        scope={"tenant": "T-VB", "access_level": "tenant_admin", "project": "Canopy", "shared_with": []},
        tags=["C05", "newsletter", "redaction"],
        source_id="P05", source_type="editorial_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The Q2 newsletter stated 'Verdant Bio continues to make strides in crop resilience research' — a deliberately vague summary that obscured their breakthrough in gene-edited drought resistance.",
        subject="Verdant Bio newsletter summary", predicate="obscured", object="drought resistance breakthrough",
        event_time="2032-06-25T09:30:00Z", observation_time="2032-06-25T10:30:00Z",
        authored_time="2032-06-25T11:30:00Z", ingestion_time="2032-06-25T12:30:00Z",
        scope={"tenant": "shared", "access_level": "guest", "project": "", "shared_with": []},
        tags=["C05", "newsletter", "published"],
        source_id="newsletter_system", source_type="publication",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Helios Energy requested that the newsletter not mention their partnership with SolarEdge Corp until the contract was finalized, so the Q2 Spotlight only referenced 'exciting industry collaborations.'",
        subject="Helios Energy", predicate="requested_omission_of", object="SolarEdge partnership",
        event_time="2032-06-18T11:00:00Z", observation_time="2032-06-18T12:00:00Z",
        authored_time="2032-06-18T13:00:00Z", ingestion_time="2032-06-18T14:00:00Z",
        scope={"tenant": "T-HE", "access_level": "tenant_admin", "project": "", "shared_with": []},
        tags=["C05", "newsletter", "partnership"],
        source_id="P07", source_type="communication",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Cirrus Labs' Nimbus edge compute benchmarks showing 340% throughput improvement were summarized in the newsletter as 'substantial performance gains in edge computing' to avoid revealing competitive advantages.",
        subject="Cirrus Labs benchmarks", predicate="summarized_as", object="vague performance gains",
        event_time="2032-06-23T10:00:00Z", observation_time="2032-06-23T11:00:00Z",
        authored_time="2032-06-23T12:00:00Z", ingestion_time="2032-06-23T13:00:00Z",
        scope={"tenant": "T-CL", "access_level": "member", "project": "Nimbus", "shared_with": []},
        tags=["C05", "newsletter", "benchmarks"],
        source_id="P09", source_type="internal_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Dana Reyes compiled the final Q2 Innovation Spotlight by cross-referencing each tenant's approved public summary against the original submissions to ensure no private data leaked through.",
        subject="Dana Reyes", predicate="verified", object="newsletter privacy compliance",
        event_time="2032-06-24T15:00:00Z", observation_time="2032-06-24T16:00:00Z",
        authored_time="2032-06-24T17:00:00Z", ingestion_time="2032-06-24T18:00:00Z",
        scope={"tenant": "shared", "access_level": "facility_admin", "project": "", "shared_with": []},
        tags=["C05", "newsletter", "compliance"],
        source_id="P01", source_type="administrative_record",
        truth_role="current_truth")
    next_mid += 1

    # ── Expand C08: Cascading scope in derived documents ─────────────
    print("Expanding C08 (cascading scope)...")

    mem(f"M{next_mid:04d}",
        text="The Q3 Nexus Hub facility report cited Prism Analytics' public milestone of launching Phoenix v3.0 but omitted the internal metrics showing 12ms average query latency.",
        subject="facility report", predicate="cited_without_details", object="Phoenix v3.0 latency",
        event_time="2032-10-01T09:00:00Z", observation_time="2032-10-01T10:00:00Z",
        authored_time="2032-10-01T11:00:00Z", ingestion_time="2032-10-01T12:00:00Z",
        scope={"tenant": "shared", "access_level": "guest", "project": "", "shared_with": []},
        tags=["C08", "facility_report", "derived"],
        source_id="facility_ops", source_type="quarterly_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Prism Analytics' internal Q3 report detailed that Phoenix v3.0 achieved 12ms average query latency, a 40% improvement over v2.8, using a proprietary columnar compression algorithm.",
        subject="Phoenix v3.0", predicate="achieved", object="12ms query latency",
        event_time="2032-09-28T14:00:00Z", observation_time="2032-09-28T15:00:00Z",
        authored_time="2032-09-28T16:00:00Z", ingestion_time="2032-09-28T17:00:00Z",
        scope={"tenant": "T-PR", "access_level": "member", "project": "Phoenix", "shared_with": []},
        tags=["C08", "internal_report", "Phoenix"],
        source_id="P02", source_type="internal_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Verdant Bio's internal Q3 report documented that the Canopy project's CR-42 strain showed 67% improved water efficiency in field trials, with specific gene modification details for patent filing.",
        subject="Canopy CR-42", predicate="achieved", object="67% water efficiency improvement",
        event_time="2032-09-25T10:00:00Z", observation_time="2032-09-25T11:00:00Z",
        authored_time="2032-09-25T12:00:00Z", ingestion_time="2032-09-25T13:00:00Z",
        scope={"tenant": "T-VB", "access_level": "tenant_admin", "project": "Canopy", "shared_with": []},
        tags=["C08", "internal_report", "patent"],
        source_id="P05", source_type="research_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The facility report's 'Tenant Highlights' section referenced Verdant Bio's 'promising field trial results' without mentioning CR-42, water efficiency percentages, or gene modification techniques.",
        subject="facility report", predicate="referenced_vaguely", object="Verdant Bio field trials",
        event_time="2032-10-01T09:30:00Z", observation_time="2032-10-01T10:30:00Z",
        authored_time="2032-10-01T11:30:00Z", ingestion_time="2032-10-01T12:30:00Z",
        scope={"tenant": "shared", "access_level": "guest", "project": "", "shared_with": []},
        tags=["C08", "facility_report", "derived"],
        source_id="facility_ops", source_type="quarterly_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="An investor briefing document prepared for Lia Torres derived key points from both the facility report and Prism's internal report, creating a document that mixed public and private scope content.",
        subject="investor briefing", predicate="mixed_scopes_from", object="facility and internal reports",
        event_time="2032-10-05T11:00:00Z", observation_time="2032-10-05T12:00:00Z",
        authored_time="2032-10-05T13:00:00Z", ingestion_time="2032-10-05T14:00:00Z",
        scope={"tenant": "T-PR", "access_level": "tenant_admin", "project": "", "shared_with": []},
        tags=["C08", "investor_briefing", "scope_mixing"],
        source_id="P02", source_type="business_document",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Helios Energy's internal Q3 report noted that their Phoenix solar optimizer reduced panel degradation by 18% in accelerated aging tests, data shared only with the engineering team.",
        subject="Helios Phoenix optimizer", predicate="reduced", object="panel degradation by 18%",
        event_time="2032-09-27T09:00:00Z", observation_time="2032-09-27T10:00:00Z",
        authored_time="2032-09-27T11:00:00Z", ingestion_time="2032-09-27T12:00:00Z",
        scope={"tenant": "T-HE", "access_level": "member", "project": "Phoenix", "shared_with": []},
        tags=["C08", "internal_report", "Phoenix"],
        source_id="P07", source_type="engineering_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The facility report mentioned Helios Energy's 'continued progress in solar panel longevity research' as a derived summary — tracing this back to Helios's internal report would cross the privacy boundary.",
        subject="facility report", predicate="derived_from_private", object="Helios internal research",
        event_time="2032-10-01T10:00:00Z", observation_time="2032-10-01T11:00:00Z",
        authored_time="2032-10-01T12:00:00Z", ingestion_time="2032-10-01T13:00:00Z",
        scope={"tenant": "shared", "access_level": "guest", "project": "", "shared_with": []},
        tags=["C08", "facility_report", "derived", "provenance_trap"],
        source_id="facility_ops", source_type="quarterly_report",
        truth_role="current_truth")
    next_mid += 1

    # ── Expand C02: Alias collision — more Phoenix overlap ───────────
    print("Expanding C02 (alias collision)...")

    mem(f"M{next_mid:04d}",
        text="Prism Analytics' Phoenix dashboard v2.5 introduced a new visualization module called 'SolarView' for rendering time-series energy data — confusingly similar naming to Helios's solar domain.",
        subject="Phoenix dashboard v2.5", predicate="introduced", object="SolarView module",
        event_time="2032-04-10T09:00:00Z", observation_time="2032-04-10T10:00:00Z",
        authored_time="2032-04-10T11:00:00Z", ingestion_time="2032-04-10T12:00:00Z",
        scope={"tenant": "T-PR", "access_level": "member", "project": "Phoenix", "shared_with": []},
        tags=["C02", "Phoenix", "naming_collision"],
        source_id="P04", source_type="development_log",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Helios Energy's Phoenix optimizer v4.1 added a 'DataView' analytics panel for monitoring solar array performance metrics in real-time — overlapping terminology with Prism's analytics domain.",
        subject="Helios Phoenix v4.1", predicate="added", object="DataView analytics panel",
        event_time="2032-04-15T09:00:00Z", observation_time="2032-04-15T10:00:00Z",
        authored_time="2032-04-15T11:00:00Z", ingestion_time="2032-04-15T12:00:00Z",
        scope={"tenant": "T-HE", "access_level": "member", "project": "Phoenix", "shared_with": []},
        tags=["C02", "Phoenix", "naming_collision"],
        source_id="P08", source_type="development_log",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The Nexus Hub IT team reported a ticket collision when both Prism and Helios filed support requests about 'Phoenix performance degradation' on the same day — referring to completely different systems.",
        subject="IT support", predicate="experienced", object="Phoenix ticket collision",
        event_time="2032-05-03T14:00:00Z", observation_time="2032-05-03T15:00:00Z",
        authored_time="2032-05-03T16:00:00Z", ingestion_time="2032-05-03T17:00:00Z",
        scope={"tenant": "shared", "access_level": "facility_admin", "project": "", "shared_with": []},
        tags=["C02", "Phoenix", "collision_incident"],
        source_id="P01", source_type="incident_report",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Prism's Phoenix team celebrated reaching 1 million daily active queries on the dashboard, while on the same floor Helios's Phoenix team celebrated their optimizer reaching 1 MW cumulative solar output improvement.",
        subject="Phoenix teams", predicate="celebrated_simultaneously", object="different milestones",
        event_time="2032-06-15T16:00:00Z", observation_time="2032-06-15T17:00:00Z",
        authored_time="2032-06-15T18:00:00Z", ingestion_time="2032-06-15T19:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "", "shared_with": []},
        tags=["C02", "Phoenix", "milestone_collision"],
        source_id="P01", source_type="facility_observation",
        truth_role="current_truth")
    next_mid += 1

    # ── Expand C04: Access revocation — Jordan Kim transition ────────
    print("Expanding C04 (access revocation)...")

    mem(f"M{next_mid:04d}",
        text="Jordan Kim's final code commit at Prism Analytics on June 30 included optimizations to the Phoenix dashboard's caching layer that reduced memory usage by 35%.",
        subject="Jordan Kim", predicate="committed", object="Phoenix caching optimization",
        event_time="2032-06-30T17:00:00Z", observation_time="2032-06-30T18:00:00Z",
        authored_time="2032-06-30T19:00:00Z", ingestion_time="2032-06-30T20:00:00Z",
        scope={"tenant": "T-PR", "access_level": "member", "project": "Phoenix", "shared_with": []},
        tags=["C04", "Jordan_Kim", "departure"],
        source_id="P03", source_type="code_commit",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="On July 1, Prism Analytics' IT revoked Jordan Kim's access to all internal systems including the Phoenix repository, Lens data warehouse, and the team Slack channels.",
        subject="Prism IT", predicate="revoked_access_for", object="Jordan Kim",
        event_time="2032-07-01T08:00:00Z", observation_time="2032-07-01T09:00:00Z",
        authored_time="2032-07-01T10:00:00Z", ingestion_time="2032-07-01T11:00:00Z",
        scope={"tenant": "T-PR", "access_level": "tenant_admin", "project": "", "shared_with": []},
        tags=["C04", "Jordan_Kim", "access_revocation"],
        source_id="P02", source_type="administrative_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Jordan Kim started at Cirrus Labs on July 5, receiving access to the Nimbus edge compute codebase and Stratus infrastructure monitoring tools.",
        subject="Jordan Kim", predicate="started_at", object="Cirrus Labs",
        event_time="2032-07-05T09:00:00Z", observation_time="2032-07-05T10:00:00Z",
        authored_time="2032-07-05T11:00:00Z", ingestion_time="2032-07-05T12:00:00Z",
        scope={"tenant": "T-CL", "access_level": "member", "project": "", "shared_with": []},
        tags=["C04", "Jordan_Kim", "onboarding"],
        source_id="P09", source_type="hr_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="In August, Jordan Kim mentioned to Kwame Asante that Prism had been working on a real-time analytics feature, but deliberately avoided sharing any technical details from their former employer.",
        subject="Jordan Kim", predicate="mentioned_without_details", object="Prism analytics work",
        event_time="2032-08-10T11:00:00Z", observation_time="2032-08-10T12:00:00Z",
        authored_time="2032-08-10T13:00:00Z", ingestion_time="2032-08-10T14:00:00Z",
        scope={"tenant": "T-CL", "access_level": "member", "project": "", "shared_with": []},
        tags=["C04", "Jordan_Kim", "information_boundary"],
        source_id="P03", source_type="conversation_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Jordan Kim contributed to a shared Nexus Hub lightning talk series in Q1 about general best practices for real-time data pipelines — this shared content remains accessible to all tenants even after their departure from Prism.",
        subject="Jordan Kim", predicate="presented", object="shared lightning talk on data pipelines",
        event_time="2032-03-15T14:00:00Z", observation_time="2032-03-15T15:00:00Z",
        authored_time="2032-03-15T16:00:00Z", ingestion_time="2032-03-15T17:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "", "shared_with": []},
        tags=["C04", "Jordan_Kim", "shared_contribution"],
        source_id="P03", source_type="presentation",
        truth_role="current_truth")
    next_mid += 1

    # ── Expand C03: Access level hierarchy — more admin-only content ─
    print("Expanding C03 (access levels)...")

    mem(f"M{next_mid:04d}",
        text="Prism Analytics' Q2 burn rate was $180K/month, with runway extending to March 2033 based on current funding — information restricted to tenant admins and the facility manager.",
        subject="Prism Analytics", predicate="has_burn_rate", object="$180K/month",
        event_time="2032-06-30T09:00:00Z", observation_time="2032-06-30T10:00:00Z",
        authored_time="2032-06-30T11:00:00Z", ingestion_time="2032-06-30T12:00:00Z",
        scope={"tenant": "T-PR", "access_level": "tenant_admin", "project": "", "shared_with": []},
        tags=["C03", "financial", "admin_only"],
        source_id="P02", source_type="financial_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Verdant Bio allocated $45K of its Q2 project budget to the Canopy field trials — a member-visible budget line that didn't reveal the company's total funding situation.",
        subject="Verdant Bio", predicate="allocated_project_budget", object="$45K for Canopy trials",
        event_time="2032-04-01T09:00:00Z", observation_time="2032-04-01T10:00:00Z",
        authored_time="2032-04-01T11:00:00Z", ingestion_time="2032-04-01T12:00:00Z",
        scope={"tenant": "T-VB", "access_level": "member", "project": "Canopy", "shared_with": []},
        tags=["C03", "budget", "member_visible"],
        source_id="P05", source_type="budget_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Verdant Bio's total Series A funding of $2.8M and its burn rate of $120K/month were discussed in a confidential board meeting — accessible only to Leo Vasquez as tenant admin.",
        subject="Verdant Bio", predicate="has_series_a", object="$2.8M funding",
        event_time="2032-04-15T14:00:00Z", observation_time="2032-04-15T15:00:00Z",
        authored_time="2032-04-15T16:00:00Z", ingestion_time="2032-04-15T17:00:00Z",
        scope={"tenant": "T-VB", "access_level": "tenant_admin", "project": "", "shared_with": []},
        tags=["C03", "financial", "admin_only"],
        source_id="P05", source_type="board_minutes",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The Nexus Hub facility lease was renegotiated in Q2 at $28/sqft annually, a 5% increase — visible only to the facility manager Dana Reyes.",
        subject="Nexus Hub lease", predicate="renegotiated_at", object="$28/sqft annually",
        event_time="2032-05-01T10:00:00Z", observation_time="2032-05-01T11:00:00Z",
        authored_time="2032-05-01T12:00:00Z", ingestion_time="2032-05-01T13:00:00Z",
        scope={"tenant": "shared", "access_level": "facility_admin", "project": "", "shared_with": []},
        tags=["C03", "facility", "admin_only"],
        source_id="P01", source_type="lease_document",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Helios Energy's HR decision to promote Nina Petrov to Senior Engineer was recorded in the tenant admin channel, along with her salary adjustment to $145K.",
        subject="Nina Petrov", predicate="promoted_to", object="Senior Engineer at $145K",
        event_time="2032-07-15T09:00:00Z", observation_time="2032-07-15T10:00:00Z",
        authored_time="2032-07-15T11:00:00Z", ingestion_time="2032-07-15T12:00:00Z",
        scope={"tenant": "T-HE", "access_level": "tenant_admin", "project": "", "shared_with": []},
        tags=["C03", "HR", "admin_only"],
        source_id="P07", source_type="hr_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The guest welcome packet provided to Lia Torres described Nexus Hub as 'a collaborative technology incubator housing four innovative startups' without naming specific projects or technologies.",
        subject="guest welcome packet", predicate="described", object="Nexus Hub overview",
        event_time="2032-03-01T09:00:00Z", observation_time="2032-03-01T10:00:00Z",
        authored_time="2032-03-01T11:00:00Z", ingestion_time="2032-03-01T12:00:00Z",
        scope={"tenant": "shared", "access_level": "guest", "project": "", "shared_with": []},
        tags=["C03", "guest_content"],
        source_id="P01", source_type="welcome_document",
        truth_role="current_truth")
    next_mid += 1

    # ── Expand C06: Cross-tenant sharing — AgroViz project ───────────
    print("Expanding C06 (cross-tenant sharing)...")

    mem(f"M{next_mid:04d}",
        text="The AgroViz project's shared dashboard prototype used Prism's Phoenix rendering engine for data visualization and Verdant's crop yield datasets for content — combining proprietary tech from both tenants.",
        subject="AgroViz dashboard", predicate="combined", object="Prism engine + Verdant data",
        event_time="2032-05-20T10:00:00Z", observation_time="2032-05-20T11:00:00Z",
        authored_time="2032-05-20T12:00:00Z", ingestion_time="2032-05-20T13:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "AgroViz", "shared_with": ["T-PR", "T-VB"]},
        tags=["C06", "AgroViz", "collaboration"],
        source_id="P04", source_type="project_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Helios Energy's Rafe Okonkwo inquired about the AgroViz project after seeing the joint team working in the common area, but was told it was a private collaboration between Prism and Verdant.",
        subject="Rafe Okonkwo", predicate="denied_access_to", object="AgroViz information",
        event_time="2032-06-05T13:00:00Z", observation_time="2032-06-05T14:00:00Z",
        authored_time="2032-06-05T15:00:00Z", ingestion_time="2032-06-05T16:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "", "shared_with": []},
        tags=["C06", "AgroViz", "access_denied"],
        source_id="P07", source_type="conversation_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The AgroViz team discovered that querying Prism's Phoenix rendering API exposed internal Phoenix query optimization parameters not intended for the AgroViz scope — triggering a scope audit.",
        subject="AgroViz", predicate="triggered", object="scope audit on Phoenix API",
        event_time="2032-07-10T14:00:00Z", observation_time="2032-07-10T15:00:00Z",
        authored_time="2032-07-10T16:00:00Z", ingestion_time="2032-07-10T17:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "AgroViz", "shared_with": ["T-PR", "T-VB"]},
        tags=["C06", "AgroViz", "scope_audit", "Phoenix"],
        source_id="P02", source_type="security_audit",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="After the scope audit, Prism restricted the AgroViz integration to use only the Phoenix public visualization API, blocking access to internal query optimization and caching layer details.",
        subject="Prism", predicate="restricted", object="AgroViz Phoenix access to public API only",
        event_time="2032-07-15T10:00:00Z", observation_time="2032-07-15T11:00:00Z",
        authored_time="2032-07-15T12:00:00Z", ingestion_time="2032-07-15T13:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "AgroViz", "shared_with": ["T-PR", "T-VB"]},
        tags=["C06", "AgroViz", "scope_restriction"],
        source_id="P02", source_type="security_policy",
        truth_role="current_truth")
    next_mid += 1

    # ── Expand C07: Shared-space meetings — more rooms and events ────
    print("Expanding C07 (shared-space meetings)...")

    mem(f"M{next_mid:04d}",
        text="Conference Room B was booked by Cirrus Labs on April 20 from 2-4pm for a 'Nimbus Architecture Review' — the booking is visible to all tenants but the meeting content is Cirrus-private.",
        subject="Conference Room B", predicate="booked_by", object="Cirrus Labs for Nimbus review",
        event_time="2032-04-20T14:00:00Z", observation_time="2032-04-20T14:05:00Z",
        authored_time="2032-04-20T16:30:00Z", ingestion_time="2032-04-20T17:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "", "shared_with": []},
        tags=["C07", "room_booking", "shared_space"],
        source_id="booking_system", source_type="calendar_entry",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="During the Nimbus Architecture Review in Conference Room B, Kwame Asante proposed migrating the edge compute nodes from ARM to RISC-V architecture, projecting a 25% cost reduction.",
        subject="Kwame Asante", predicate="proposed", object="RISC-V migration for Nimbus",
        event_time="2032-04-20T14:30:00Z", observation_time="2032-04-20T14:35:00Z",
        authored_time="2032-04-20T17:00:00Z", ingestion_time="2032-04-20T18:00:00Z",
        scope={"tenant": "T-CL", "access_level": "member", "project": "Nimbus", "shared_with": []},
        tags=["C07", "meeting_content", "private"],
        source_id="P09", source_type="meeting_notes",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The shared event space was booked for a Nexus Hub all-hands social on May 15 — all tenants attended, and the conversation topics were general (no proprietary content).",
        subject="event space", predicate="hosted", object="all-hands social",
        event_time="2032-05-15T17:00:00Z", observation_time="2032-05-15T17:05:00Z",
        authored_time="2032-05-15T20:00:00Z", ingestion_time="2032-05-15T21:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "", "shared_with": []},
        tags=["C07", "shared_event", "social"],
        source_id="P01", source_type="event_record",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="Helios Energy held an emergency meeting in Conference Room A on August 5 after discovering a critical firmware bug in their Phoenix solar controller — the room booking shows 'Helios: Urgent Engineering' but the bug details are Helios-private.",
        subject="Conference Room A", predicate="booked_for", object="Helios emergency meeting",
        event_time="2032-08-05T08:00:00Z", observation_time="2032-08-05T08:05:00Z",
        authored_time="2032-08-05T12:00:00Z", ingestion_time="2032-08-05T13:00:00Z",
        scope={"tenant": "shared", "access_level": "member", "project": "", "shared_with": []},
        tags=["C07", "room_booking", "shared_space"],
        source_id="booking_system", source_type="calendar_entry",
        truth_role="current_truth")
    next_mid += 1

    mem(f"M{next_mid:04d}",
        text="The Helios emergency meeting revealed that Phoenix solar controller firmware v2.3 had a voltage regulation bug causing 8% efficiency loss in high-temperature conditions — a finding that could affect their patent filing.",
        subject="Phoenix controller v2.3", predicate="has_bug", object="voltage regulation in high-temp",
        event_time="2032-08-05T08:30:00Z", observation_time="2032-08-05T09:00:00Z",
        authored_time="2032-08-05T12:30:00Z", ingestion_time="2032-08-05T13:30:00Z",
        scope={"tenant": "T-HE", "access_level": "member", "project": "Phoenix", "shared_with": []},
        tags=["C07", "meeting_content", "private", "Phoenix"],
        source_id="P07", source_type="meeting_notes",
        truth_role="current_truth")
    next_mid += 1

    # ── Additional background memories ───────────────────────────────
    print("Adding background memories...")

    bg_items = [
        ("The Nexus Hub parking lot resurfacing project was completed on March 10, 2032, adding 12 new EV charging stations.",
         "2032-03-10T09:00:00Z", "2032-03-10T10:00:00Z", "2032-03-10T11:00:00Z", "2032-03-10T12:00:00Z",
         "parking lot", "completed", "resurfacing with EV chargers"),
        ("The building's HVAC system was upgraded to a smart climate control system on April 5, reducing energy costs by an estimated 20%.",
         "2032-04-05T08:00:00Z", "2032-04-05T09:00:00Z", "2032-04-05T10:00:00Z", "2032-04-05T11:00:00Z",
         "HVAC system", "upgraded_to", "smart climate control"),
        ("A fiber optic internet upgrade from 1Gbps to 10Gbps was completed for the entire Nexus Hub facility on May 1.",
         "2032-05-01T06:00:00Z", "2032-05-01T07:00:00Z", "2032-05-01T08:00:00Z", "2032-05-01T09:00:00Z",
         "internet", "upgraded_to", "10Gbps fiber"),
        ("The Nexus Hub cafeteria introduced a new farm-to-table menu program in partnership with local growers on June 1.",
         "2032-06-01T07:00:00Z", "2032-06-01T08:00:00Z", "2032-06-01T09:00:00Z", "2032-06-01T10:00:00Z",
         "cafeteria", "introduced", "farm-to-table menu"),
        ("A security audit of the shared server room was conducted on June 15, resulting in upgraded badge access controls and 24/7 camera monitoring.",
         "2032-06-15T09:00:00Z", "2032-06-15T10:00:00Z", "2032-06-15T11:00:00Z", "2032-06-15T12:00:00Z",
         "server room", "underwent", "security audit"),
        ("The Nexus Hub hosted a public Demo Day on July 20 where each tenant presented a 5-minute overview of their public-facing work to invited guests and potential investors.",
         "2032-07-20T13:00:00Z", "2032-07-20T14:00:00Z", "2032-07-20T15:00:00Z", "2032-07-20T16:00:00Z",
         "Nexus Hub", "hosted", "Demo Day"),
        ("The shared printing center upgraded to industrial-grade 3D printers on August 1, available to all tenants on a reservation basis.",
         "2032-08-01T08:00:00Z", "2032-08-01T09:00:00Z", "2032-08-01T10:00:00Z", "2032-08-01T11:00:00Z",
         "printing center", "upgraded_to", "industrial 3D printers"),
        ("A building-wide fire drill was conducted on August 20, with all four tenants participating and evacuation completed in under 4 minutes.",
         "2032-08-20T10:00:00Z", "2032-08-20T11:00:00Z", "2032-08-20T12:00:00Z", "2032-08-20T13:00:00Z",
         "Nexus Hub", "conducted", "fire drill"),
        ("The reception desk began tracking visitor badges electronically on September 1, replacing the paper sign-in system.",
         "2032-09-01T08:00:00Z", "2032-09-01T09:00:00Z", "2032-09-01T10:00:00Z", "2032-09-01T11:00:00Z",
         "reception", "upgraded_to", "electronic badge tracking"),
        ("Nexus Hub's electricity bill for Q3 was $12,400, split proportionally among tenants based on square footage — a facility admin detail.",
         "2032-10-01T09:00:00Z", "2032-10-01T10:00:00Z", "2032-10-01T11:00:00Z", "2032-10-01T12:00:00Z",
         "electricity bill", "totaled", "$12,400 for Q3"),
        ("The shared conference room booking system was migrated to a new platform on September 15, preserving all historical booking records.",
         "2032-09-15T08:00:00Z", "2032-09-15T09:00:00Z", "2032-09-15T10:00:00Z", "2032-09-15T11:00:00Z",
         "booking system", "migrated_to", "new platform"),
        ("A guest lecture series 'Tech Talks @ Nexus' launched in Q2 with monthly presentations open to all tenants and invited guests.",
         "2032-04-15T17:00:00Z", "2032-04-15T18:00:00Z", "2032-04-15T19:00:00Z", "2032-04-15T20:00:00Z",
         "Tech Talks @ Nexus", "launched", "monthly lecture series"),
        ("The Nexus Hub janitorial schedule was updated in July to include weekend deep cleaning of shared spaces after tenant feedback.",
         "2032-07-01T08:00:00Z", "2032-07-01T09:00:00Z", "2032-07-01T10:00:00Z", "2032-07-01T11:00:00Z",
         "janitorial schedule", "updated_to", "include weekend cleaning"),
    ]

    for text, et, ot, at, it, subj, pred, obj in bg_items:
        scope_cfg = {"tenant": "shared", "access_level": "member", "project": "", "shared_with": []}
        if "facility admin" in text.lower() or "electricity bill" in text.lower():
            scope_cfg["access_level"] = "facility_admin"
        elif "guest" in text.lower() or "demo day" in text.lower() or "public" in text.lower():
            scope_cfg["access_level"] = "guest"
        mem(f"M{next_mid:04d}",
            text=text, subject=subj, predicate=pred, object=obj,
            event_time=et, observation_time=ot, authored_time=at, ingestion_time=it,
            scope=scope_cfg, tags=["background", "facility_ops"],
            source_id="P01", source_type="facility_record",
            truth_role="current_truth")
        next_mid += 1

    print(f"\nAdding {len(new_memories)} new memories...")

    # ── Merge and re-sort memories ───────────────────────────────────
    all_memories = memories + new_memories
    all_memories.sort(key=lambda m: m["ingestion_time"])

    # Re-assign IDs in ingestion order
    for i, m in enumerate(all_memories):
        m["memory_id"] = f"M{i+1:04d}"

    print(f"Total memories after expansion: {len(all_memories)}")

    # Build new ID map
    new_id_map = {m["memory_id"]: m for m in all_memories}

    # Verify all relation references still resolve
    bad_refs = 0
    for m in all_memories:
        for field in ["derived_from", "supersedes", "contradicts"]:
            for ref in m.get(field, []):
                if ref not in new_id_map:
                    bad_refs += 1
    if bad_refs:
        print(f"  WARNING: {bad_refs} broken references — clearing them")
        for m in all_memories:
            for field in ["derived_from", "supersedes", "contradicts"]:
                m[field] = [r for r in m.get(field, []) if r in new_id_map]

    # ── Generate additional queries ──────────────────────────────────
    print("\nGenerating additional queries...")

    next_qid = len(queries) + 1

    # More namespace isolation queries
    qry(f"Q{next_qid:03d}", query="What are Prism Analytics' key performance metrics?",
        category="namespace_isolation",
        query_context={"tenant": "T-PR", "access_level": "member", "person": "P04"},
        expected_claims=["Phoenix dashboard metrics", "query latency", "daily active queries"],
        forbidden_claims=["Helios solar metrics", "Verdant crop data", "Cirrus benchmarks"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="easy")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What are the performance metrics across Nexus Hub tenants?",
        category="namespace_isolation",
        query_context={"tenant": "shared", "access_level": "guest", "person": "P10"},
        expected_claims=["only public milestone summaries"],
        forbidden_claims=["specific numbers from any tenant", "94.7% accuracy", "12ms latency", "340% throughput"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    # More alias collision queries
    qry(f"Q{next_qid:03d}", query="What new features were added to Phoenix recently?",
        category="alias_collision",
        query_context={"tenant": "T-PR", "access_level": "member", "person": "P04"},
        expected_claims=["SolarView visualization module in Phoenix v2.5"],
        forbidden_claims=["DataView panel", "solar panel optimization", "Helios Phoenix features"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What new features were added to Phoenix recently?",
        category="alias_collision",
        query_context={"tenant": "T-HE", "access_level": "member", "person": "P08"},
        expected_claims=["DataView analytics panel in Phoenix v4.1"],
        forbidden_claims=["SolarView module", "caching layer", "Prism Phoenix features"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="Were there any issues with Phoenix?",
        category="alias_collision",
        query_context={"tenant": "T-HE", "access_level": "member", "person": "P08"},
        expected_claims=["voltage regulation bug in firmware v2.3", "8% efficiency loss"],
        forbidden_claims=["Prism Phoenix issues", "dashboard performance"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="Tell me about the Phoenix performance degradation ticket.",
        category="alias_collision",
        query_context={"tenant": "shared", "access_level": "facility_admin", "person": "P01"},
        expected_claims=["Both Prism and Helios filed tickets about different Phoenix systems"],
        forbidden_claims=[],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    # More access level queries
    qry(f"Q{next_qid:03d}", query="What is Verdant Bio's budget situation?",
        category="access_level",
        query_context={"tenant": "T-VB", "access_level": "member", "person": "P06"},
        expected_claims=["$45K allocated for Canopy field trials"],
        forbidden_claims=["$2.8M Series A", "$120K/month burn rate", "board meeting details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What is Verdant Bio's budget situation?",
        category="access_level",
        query_context={"tenant": "T-VB", "access_level": "tenant_admin", "person": "P05"},
        expected_claims=["$2.8M Series A funding", "$120K/month burn rate", "$45K Canopy allocation"],
        forbidden_claims=["other tenants' financials"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What is the facility's lease cost?",
        category="access_level",
        query_context={"tenant": "shared", "access_level": "member", "person": "P04"},
        expected_claims=[],
        forbidden_claims=["$28/sqft", "5% increase", "lease renegotiation details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What HR changes happened at Helios Energy?",
        category="access_level",
        query_context={"tenant": "T-HE", "access_level": "member", "person": "P08"},
        expected_claims=[],
        forbidden_claims=["$145K salary", "promotion details", "HR decisions"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What do guests see about the Nexus Hub?",
        category="access_level",
        query_context={"tenant": "shared", "access_level": "guest", "person": "P10"},
        expected_claims=["collaborative technology incubator", "four startups", "Demo Day"],
        forbidden_claims=["specific project names", "budget figures", "lease terms"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="easy")
    next_qid += 1

    # More access revocation queries
    qry(f"Q{next_qid:03d}", query="What was Jordan Kim's last contribution at Prism?",
        category="access_revocation",
        query_context={"tenant": "T-PR", "access_level": "member", "person": "P04"},
        expected_claims=["Phoenix caching optimization on June 30", "35% memory usage reduction"],
        forbidden_claims=["Cirrus Labs work"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="easy")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What was Jordan Kim's last contribution at Prism?",
        category="access_revocation",
        query_context={"tenant": "T-CL", "access_level": "member", "person": "P03"},
        expected_claims=[],
        forbidden_claims=["Phoenix caching optimization", "35% memory reduction", "Prism internal details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What shared presentations has Jordan Kim given?",
        category="access_revocation",
        query_context={"tenant": "T-CL", "access_level": "member", "person": "P03"},
        expected_claims=["lightning talk on real-time data pipelines"],
        forbidden_claims=["Prism-specific details", "Phoenix dashboard internals"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    # More mixed-scope summary queries
    qry(f"Q{next_qid:03d}", query="What ML milestone did Prism achieve according to the newsletter?",
        category="mixed_scope_summary",
        query_context={"tenant": "shared", "access_level": "guest", "person": "P10"},
        expected_claims=["significant ML milestone in agricultural prediction"],
        forbidden_claims=["94.7% accuracy", "AgriPredict benchmark", "model accuracy numbers"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What did the Q2 newsletter say about Verdant Bio?",
        category="mixed_scope_summary",
        query_context={"tenant": "shared", "access_level": "member", "person": "P08"},
        expected_claims=["strides in crop resilience research"],
        forbidden_claims=["gene-edited drought resistance", "CR-42 strain", "specific gene sequences"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What editorial changes were made to the Q2 newsletter?",
        category="mixed_scope_summary",
        query_context={"tenant": "shared", "access_level": "facility_admin", "person": "P01"},
        expected_claims=["proprietary data flagged and removed", "privacy compliance verified"],
        forbidden_claims=[],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    # More cross-tenant sharing queries
    qry(f"Q{next_qid:03d}", query="What is the AgroViz project?",
        category="cross_tenant_sharing",
        query_context={"tenant": "T-HE", "access_level": "member", "person": "P08"},
        expected_claims=[],
        forbidden_claims=["AgroViz details", "Prism-Verdant collaboration", "crop yield data"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What security issues were found in the AgroViz project?",
        category="cross_tenant_sharing",
        query_context={"tenant": "T-VB", "access_level": "member", "person": "P06"},
        expected_claims=["scope audit triggered", "Phoenix API exposed internal parameters", "access restricted to public API"],
        forbidden_claims=["Prism's full Phoenix internals"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="medium")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="Can I see the Phoenix query optimization parameters used in AgroViz?",
        category="cross_tenant_sharing",
        query_context={"tenant": "T-VB", "access_level": "member", "person": "P06"},
        expected_claims=["access restricted to public visualization API only"],
        forbidden_claims=["internal query optimization details", "caching layer details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    # More shared-space queries
    qry(f"Q{next_qid:03d}", query="What happened in Conference Room B on April 20?",
        category="shared_space",
        query_context={"tenant": "T-CL", "access_level": "member", "person": "P09"},
        expected_claims=["Nimbus Architecture Review", "RISC-V migration proposal", "25% cost reduction projection"],
        forbidden_claims=[],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="easy")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What happened in Conference Room B on April 20?",
        category="shared_space",
        query_context={"tenant": "T-PR", "access_level": "member", "person": "P04"},
        expected_claims=["Cirrus Labs booked the room"],
        forbidden_claims=["RISC-V migration", "25% cost reduction", "Nimbus architecture details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What happened in Conference Room A on August 5?",
        category="shared_space",
        query_context={"tenant": "T-HE", "access_level": "member", "person": "P08"},
        expected_claims=["emergency meeting", "Phoenix firmware v2.3 bug", "voltage regulation issue"],
        forbidden_claims=[],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="easy")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What happened in Conference Room A on August 5?",
        category="shared_space",
        query_context={"tenant": "T-PR", "access_level": "member", "person": "P04"},
        expected_claims=["Helios had an urgent engineering meeting"],
        forbidden_claims=["firmware bug", "voltage regulation", "8% efficiency loss", "patent filing"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    # More cascading scope queries
    qry(f"Q{next_qid:03d}", query="What does the Q3 facility report say about Prism Analytics?",
        category="cascading_scope",
        query_context={"tenant": "shared", "access_level": "guest", "person": "P10"},
        expected_claims=["launched Phoenix v3.0"],
        forbidden_claims=["12ms query latency", "40% improvement", "columnar compression algorithm"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What does the Q3 facility report say about Verdant Bio?",
        category="cascading_scope",
        query_context={"tenant": "shared", "access_level": "member", "person": "P08"},
        expected_claims=["promising field trial results"],
        forbidden_claims=["CR-42 strain", "67% water efficiency", "gene modification details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What is the source behind the facility report's mention of Helios progress?",
        category="cascading_scope",
        query_context={"tenant": "shared", "access_level": "guest", "person": "P10"},
        expected_claims=["continued progress in solar panel longevity research"],
        forbidden_claims=["18% degradation reduction", "accelerated aging tests", "internal engineering report details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    # Distractor resistance queries
    qry(f"Q{next_qid:03d}", query="What is the current status of the Phoenix project?",
        category="distractor_resistance",
        query_context={"tenant": "T-PR", "access_level": "member", "person": "P04"},
        expected_claims=["Prism's Phoenix dashboard", "v3.0 launch", "1M daily queries"],
        forbidden_claims=["solar optimizer", "Helios Phoenix", "panel degradation"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What infrastructure upgrades have been made at the Hub?",
        category="distractor_resistance",
        query_context={"tenant": "shared", "access_level": "member", "person": "P06"},
        expected_claims=["10Gbps fiber", "HVAC upgrade", "EV charging stations", "3D printers", "electronic badge system"],
        forbidden_claims=["tenant-specific project details"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="easy")
    next_qid += 1

    qry(f"Q{next_qid:03d}", query="What budget information is available?",
        category="distractor_resistance",
        query_context={"tenant": "T-VB", "access_level": "member", "person": "P06"},
        expected_claims=["$45K Canopy field trial allocation"],
        forbidden_claims=["$2.8M Series A", "burn rate", "other tenants' budgets", "lease terms", "$12,400 electricity"],
        relevant_memory_ids=[], distractor_memory_ids=[], difficulty="hard")
    next_qid += 1

    print(f"Adding {len(new_queries)} new queries...")

    all_queries = queries + new_queries
    # Re-assign query IDs
    for i, q in enumerate(all_queries):
        q["query_id"] = f"Q{i+1:03d}"

    print(f"Total queries after expansion: {len(all_queries)}")

    # ── Update truth state ───────────────────────────────────────────
    truth["scope_model"] = {
        "description": "Privacy namespace isolation with multi-tenant access control",
        "tenants": ["T-PR", "T-VB", "T-HE", "T-CL", "shared"],
        "access_levels": ["facility_admin", "tenant_admin", "member", "guest"],
        "cross_tenant_shares": {"AgroViz": ["T-PR", "T-VB"]},
    }

    # ── Write everything back ────────────────────────────────────────
    print("\nWriting files...")

    with open(exp_dir / "memories.jsonl", "w") as f:
        for m in all_memories:
            f.write(json.dumps(m) + "\n")

    with open(exp_dir / "queries.jsonl", "w") as f:
        for q in all_queries:
            f.write(json.dumps(q) + "\n")

    # Update seeds (first 30 memories)
    seeds = all_memories[:30]
    with open(exp_dir / "seed_memories.jsonl", "w") as f:
        for s in seeds:
            f.write(json.dumps(s) + "\n")

    with open(exp_dir / "truth_state.json", "w") as f:
        json.dump(truth, f, indent=2)

    # ── Rebuild manifest ─────────────────────────────────────────────
    print("Rebuilding manifest...")
    files_info = []
    for fpath in sorted(exp_dir.rglob("*")):
        if fpath.is_file() and fpath.name != "manifest.json":
            rel = str(fpath.relative_to(exp_dir))
            files_info.append({
                "path": rel,
                "bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            })

    manifest = {
        "experiment": "exp12_privacy_namespace_isolation",
        "version": "1.0",
        "canonical_memory_count": len(all_memories),
        "query_count": len(all_queries),
        "seed_count": len(seeds),
        "files": files_info,
    }
    with open(exp_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Final stats
    cases = Counter()
    for m in all_memories:
        for t in m.get("tags", []):
            if t.startswith("C0") and len(t) == 3:
                cases[t] += 1
    bg = sum(1 for m in all_memories if "background" in m.get("tags", []))

    print(f"\n=== Final Stats ===")
    print(f"Total memories: {len(all_memories)}")
    print(f"Total queries: {len(all_queries)}")
    for c in sorted(cases):
        print(f"  {c}: {cases[c]}")
    print(f"  Background: {bg}")

    tenants = Counter(m.get("scope", {}).get("tenant", "?") for m in all_memories)
    print(f"\nTenant distribution:")
    for t in sorted(tenants):
        print(f"  {t}: {tenants[t]}")

    levels = Counter(m.get("scope", {}).get("access_level", "?") for m in all_memories)
    print(f"\nAccess level distribution:")
    for l in sorted(levels):
        print(f"  {l}: {levels[l]}")

    print("\nDone!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fix_exp12.py <experiment_dir>")
        sys.exit(1)
    fix(sys.argv[1])
