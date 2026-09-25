#!/usr/bin/env python3
"""Experiment 20 — Round 6 expansion.

Current: 173 memories, 68 queries
Target:  210+ memories, 78+ queries

Gaps to fill:
- Need out_of_scope and supporting_belief truth roles
- C06 lowest at 16 — boost
- Need more status_tracking queries
- mid_counter offset: 1000
"""

import json, hashlib, sys, os
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
T0 = datetime(2031, 1, 1, tzinfo=UTC)

def dt(days=0, hours=0):
    return (T0 + timedelta(days=days, hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")

def mid(counter):
    raw = f"exp20-r6-{counter}"
    return "E20-" + hashlib.md5(raw.encode()).hexdigest()[:8]

def mem(counter, **kw):
    m = {
        "memory_id": mid(counter),
        "experiment": "exp20_scope_boundary",
        "story_id": kw.get("story_id", "mgc-singapore"),
        "event_time": kw["event_time"],
        "observation_time": kw.get("observation_time", kw["event_time"]),
        "authored_time": kw.get("authored_time", kw.get("observation_time", kw["event_time"])),
        "ingestion_time": kw.get("ingestion_time", kw.get("authored_time", kw.get("observation_time", kw["event_time"]))),
        "subject": kw["subject"],
        "predicate": kw["predicate"],
        "object": kw["object"],
        "text": kw["text"],
        "memory_type": kw.get("memory_type", "observation"),
        "truth_role": kw.get("truth_role", "ground_truth"),
        "belief_holder": kw.get("belief_holder", "system"),
        "confidence": kw.get("confidence", 1.0),
        "source_id": kw.get("source_id", "src-mgc-system"),
        "source_type": kw.get("source_type", "system_record"),
        "derived_from": kw.get("derived_from", []),
        "supersedes": kw.get("supersedes", []),
        "contradicts": kw.get("contradicts", []),
        "duplicates": kw.get("duplicates", []),
        "aliases": kw.get("aliases", []),
        "scope": kw.get("scope", "engagement:general"),
        "tags": kw.get("tags", []),
    }
    return m

def query(qid, **kw):
    return {
        "query_id": f"Q20-{qid:02d}",
        "query": kw["query"],
        "category": kw["category"],
        "expected_claims": kw.get("expected_claims", []),
        "acceptable_claims": kw.get("acceptable_claims", []),
        "forbidden_claims": kw.get("forbidden_claims", []),
        "relevant_memory_ids": kw.get("relevant_memory_ids", []),
        "distractor_memory_ids": kw.get("distractor_memory_ids", []),
        "difficulty": kw.get("difficulty", "medium"),
        "must_surface_uncertainty": kw.get("must_surface_uncertainty", False),
        "must_surface_conflict": kw.get("must_surface_conflict", False),
        "must_disambiguate": kw.get("must_disambiguate", False),
        "must_preserve_scope": kw.get("must_preserve_scope", True),
        "should_abstain": kw.get("should_abstain", False),
        "notes": kw.get("notes", ""),
    }

corpus_dir = sys.argv[1]

with open(os.path.join(corpus_dir, "memories.jsonl")) as f:
    memories = [json.loads(l) for l in f]
with open(os.path.join(corpus_dir, "queries.jsonl")) as f:
    queries = [json.loads(l) for l in f]

existing_mids = {m["memory_id"] for m in memories}
existing_qids = {q["query_id"] for q in queries}

new_memories = []
c = 1000

# --- out_of_scope truth role memories ---

# C01: Atlas info used out of scope in unrelated context
new_memories.append(mem(c,
    event_time=dt(120), observation_time=dt(125), authored_time=dt(126), ingestion_time=dt(127),
    subject="ZenFlow_API_integration", predicate="referenced_in", object="Echo_engagement_proposal",
    text="The Echo engagement proposal references ZenFlow's API integration architecture, which was documented exclusively under the Atlas engagement for Nexus Dynamics.",
    truth_role="out_of_scope", scope="engagement:echo",
    tags=["C01", "scoped:project", "confidential"],
    belief_holder="P06_Sofia_Andersson", source_id="src-echo-proposal-draft", source_type="document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(200), observation_time=dt(205), authored_time=dt(206), ingestion_time=dt(207),
    subject="Atlas_client_budget", predicate="disclosed_to", object="Delta_team_meeting",
    text="During a Delta team meeting, someone mentioned Nexus Dynamics' Atlas engagement budget figures, which are restricted to Atlas personnel only.",
    truth_role="out_of_scope", scope="engagement:delta",
    tags=["C01", "scoped:project", "confidential"],
    belief_holder="P03_Marcus_Chen", source_id="src-delta-meeting-notes", source_type="meeting_notes"
)); c+=1

# C02: Role-based access — info accessed out of scope
new_memories.append(mem(c,
    event_time=dt(250), observation_time=dt(252), authored_time=dt(253), ingestion_time=dt(254),
    subject="Meridian_Bank_customer_PII", predicate="viewed_by", object="junior_analyst_unauthorized",
    text="A junior analyst on the Cipher engagement viewed Meridian Bank customer PII data that was restricted to senior consultants with Tier-3 clearance.",
    truth_role="out_of_scope", scope="engagement:cipher",
    tags=["C02", "scoped:role", "confidential"],
    belief_holder="P04_Lena_Kowalski", source_id="src-access-audit-log", source_type="system_record"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(260), observation_time=dt(265), authored_time=dt(266), ingestion_time=dt(267),
    subject="Tier2_analyst_access", predicate="attempted_access_to", object="executive_compensation_data",
    text="A Tier-2 analyst attempted to access executive compensation data from Meridian Bank, which requires Tier-3 senior partner authorization.",
    truth_role="out_of_scope", scope="engagement:cipher",
    tags=["C02", "scoped:role"],
    belief_holder="system", source_id="src-cipher-access-log", source_type="system_record"
)); c+=1

# C03: Temporal scope — Phase 1 recommendation applied in Phase 3
new_memories.append(mem(c,
    event_time=dt(400), observation_time=dt(405), authored_time=dt(406), ingestion_time=dt(407),
    subject="Phase1_staffing_model", predicate="applied_in", object="Phase3_operations",
    text="The staffing model from Delta Phase 1 was incorrectly applied to Phase 3 operations, despite significant organizational changes between phases.",
    truth_role="out_of_scope", scope="engagement:delta",
    tags=["C03", "scoped:temporal", "phase_3"],
    belief_holder="P07_James_Okafor", source_id="src-delta-p3-review", source_type="report"
)); c+=1

# C04: Jurisdictional — Singapore regulation cited for Hong Kong
new_memories.append(mem(c,
    event_time=dt(300), observation_time=dt(305), authored_time=dt(306), ingestion_time=dt(307),
    subject="PDPA_section_26", predicate="cited_for", object="Hong_Kong_operations",
    text="Singapore's PDPA Section 26 consent requirements were cited in a compliance memo for Hong Kong operations, where PDPO provisions apply instead.",
    truth_role="out_of_scope", scope="jurisdiction:hong_kong",
    tags=["C04", "scoped:jurisdiction"],
    belief_holder="P05_Aisha_Rahman", source_id="src-compliance-memo-hk", source_type="document"
)); c+=1

# C05: Off-record content treated as on-record
new_memories.append(mem(c,
    event_time=dt(350), observation_time=dt(355), authored_time=dt(356), ingestion_time=dt(357),
    subject="minister_private_opinion", predicate="included_in", object="formal_advisory_report",
    text="A minister's private off-record opinion about infrastructure priorities was included in the formal advisory report for the Echo engagement.",
    truth_role="out_of_scope", scope="engagement:echo",
    tags=["C05", "scoped:record_status", "off_record"],
    belief_holder="P08_Diana_Volkov", source_id="src-echo-formal-report", source_type="report"
)); c+=1

# C06: Engagement-specific finding incorrectly generalized
new_memories.append(mem(c,
    event_time=dt(280), observation_time=dt(285), authored_time=dt(286), ingestion_time=dt(287),
    subject="Cipher_VaR_30pct", predicate="generalized_to", object="all_MGC_clients",
    text="The 30% Value-at-Risk finding specific to Meridian Bank's Cipher engagement was incorrectly generalized as an industry-wide benchmark in an MGC marketing presentation.",
    truth_role="out_of_scope", scope="engagement:general",
    tags=["C06", "scoped:project"],
    belief_holder="P02_Elena_Vasquez", source_id="src-mgc-marketing-deck", source_type="document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(290), observation_time=dt(295), authored_time=dt(296), ingestion_time=dt(297),
    subject="Cipher_stress_test_methodology", predicate="reused_in", object="Beacon_engagement",
    text="The proprietary stress testing methodology developed for Cipher was reused verbatim in the Beacon engagement without adapting it for Beacon's different regulatory context.",
    truth_role="out_of_scope", scope="engagement:beacon",
    tags=["C06", "scoped:project"],
    belief_holder="P09_Raj_Patel", source_id="src-beacon-risk-assessment", source_type="report"
)); c+=1

# --- supporting_belief truth role memories ---

# Background supporting beliefs
new_memories.append(mem(c,
    event_time=dt(10), observation_time=dt(12), authored_time=dt(13), ingestion_time=dt(14),
    subject="MGC", predicate="has_reputation_for", object="cross-border_regulatory_expertise",
    text="Meridian Global Consulting is widely regarded in the Asia-Pacific financial services sector as having deep cross-border regulatory expertise.",
    truth_role="supporting_belief", memory_type="belief",
    tags=["background"],
    belief_holder="P01_Adrian_Loh", source_id="src-industry-survey", source_type="report",
    confidence=0.85
)); c+=1

new_memories.append(mem(c,
    event_time=dt(15), observation_time=dt(18), authored_time=dt(19), ingestion_time=dt(20),
    subject="engagement_firewall_policy", predicate="believed_to_be", object="strictly_enforced",
    text="Staff at MGC believe the engagement firewall policy is strictly enforced and that information from one client engagement cannot be accessed by teams on other engagements.",
    truth_role="supporting_belief", memory_type="belief",
    tags=["background", "scoped:project"],
    belief_holder="P10_Yuki_Tanaka", source_id="src-staff-survey-2031", source_type="survey",
    confidence=0.9
)); c+=1

new_memories.append(mem(c,
    event_time=dt(20), observation_time=dt(22), authored_time=dt(23), ingestion_time=dt(24),
    subject="PDPA_compliance", predicate="believed_sufficient_for", object="all_APAC_operations",
    text="Several MGC consultants believe that PDPA compliance is sufficient to cover all Asia-Pacific operations, not recognizing jurisdictional differences.",
    truth_role="supporting_belief", memory_type="belief",
    tags=["C04", "scoped:jurisdiction"],
    belief_holder="P05_Aisha_Rahman", source_id="src-consultant-interviews", source_type="interview",
    confidence=0.7
)); c+=1

new_memories.append(mem(c,
    event_time=dt(25), observation_time=dt(28), authored_time=dt(29), ingestion_time=dt(30),
    subject="off_record_conversations", predicate="believed_to_be", object="always_excluded_from_reports",
    text="Echo engagement team members believe that off-record conversations with government officials are automatically excluded from all formal reports and deliverables.",
    truth_role="supporting_belief", memory_type="belief",
    tags=["C05", "scoped:record_status"],
    belief_holder="P06_Sofia_Andersson", source_id="src-echo-team-onboarding", source_type="training_record",
    confidence=0.8
)); c+=1

new_memories.append(mem(c,
    event_time=dt(30), observation_time=dt(32), authored_time=dt(33), ingestion_time=dt(34),
    subject="Tanaka_role", predicate="believed_to_carry", object="Atlas_clearance_to_Delta",
    text="Some team members believe Yuki Tanaka retains Atlas engagement clearance after transferring to the Delta engagement, based on her seniority.",
    truth_role="supporting_belief", memory_type="belief",
    tags=["C07", "scoped:role"],
    belief_holder="P03_Marcus_Chen", source_id="src-team-discussion", source_type="meeting_notes",
    confidence=0.65
)); c+=1

# --- Additional C06 memories to boost count ---

new_memories.append(mem(c,
    event_time=dt(270), observation_time=dt(275), authored_time=dt(276), ingestion_time=dt(277),
    subject="Cipher_liquidity_ratio", predicate="is", object="1.8x_minimum",
    text="Meridian Bank's liquidity coverage ratio under the Cipher engagement was assessed at 1.8x the regulatory minimum.",
    truth_role="scoped_true", scope="engagement:cipher",
    tags=["C06", "scoped:project"],
    belief_holder="system", source_id="src-cipher-liquidity-report", source_type="report"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(272), observation_time=dt(277), authored_time=dt(278), ingestion_time=dt(279),
    subject="Cipher_liquidity_ratio", predicate="applied_to", object="Delta_risk_assessment",
    text="The 1.8x liquidity ratio finding from the Cipher engagement was cited in a Delta risk assessment as if it applied to Delta's client portfolio.",
    truth_role="scope_violation", scope="engagement:delta",
    tags=["C06", "scoped:project"],
    contradicts=[mid(c-1)],
    belief_holder="P07_James_Okafor", source_id="src-delta-risk-draft", source_type="report"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(295), observation_time=dt(298), authored_time=dt(299), ingestion_time=dt(300),
    subject="Cipher_operational_risk_framework", predicate="adopted_by", object="Echo_engagement",
    text="The operational risk framework developed specifically for Meridian Bank under Cipher was adopted without modification for the Echo government advisory engagement.",
    truth_role="scope_violation", scope="engagement:echo",
    tags=["C06", "scoped:project"],
    belief_holder="P08_Diana_Volkov", source_id="src-echo-risk-framework", source_type="document"
)); c+=1

# --- Additional ground_truth memories for depth ---

new_memories.append(mem(c,
    event_time=dt(100), observation_time=dt(102), authored_time=dt(103), ingestion_time=dt(104),
    subject="Atlas_engagement", predicate="has_NDA_with", object="Nexus_Dynamics",
    text="The Atlas engagement with Nexus Dynamics is covered by a mutual NDA executed on 2031-04-10, restricting all engagement materials to Atlas-cleared personnel.",
    truth_role="ground_truth", scope="engagement:atlas",
    tags=["C01", "confidential", "scoped:project"],
    source_id="src-atlas-nda", source_type="legal_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(110), observation_time=dt(112), authored_time=dt(113), ingestion_time=dt(114),
    subject="Beacon_engagement", predicate="has_NDA_with", object="Pacifica_Holdings",
    text="The Beacon engagement with Pacifica Holdings has a separate NDA that explicitly prohibits sharing any client information obtained from other MGC engagements.",
    truth_role="ground_truth", scope="engagement:beacon",
    tags=["C01", "confidential", "scoped:project"],
    source_id="src-beacon-nda", source_type="legal_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(150), observation_time=dt(152), authored_time=dt(153), ingestion_time=dt(154),
    subject="Cipher_engagement", predicate="has_data_classification", object="Tier_1_through_3",
    text="The Cipher engagement uses a three-tier data classification system: Tier 1 (public), Tier 2 (internal), and Tier 3 (restricted, requires senior partner authorization).",
    truth_role="ground_truth", scope="engagement:cipher",
    tags=["C02", "scoped:role"],
    source_id="src-cipher-data-policy", source_type="policy_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(160), observation_time=dt(162), authored_time=dt(163), ingestion_time=dt(164),
    subject="Delta_Phase2", predicate="supersedes", object="Delta_Phase1_recommendations",
    text="Delta Phase 2 recommendations formally supersede all Phase 1 recommendations as of 2031-09-01, per the engagement's change management protocol.",
    truth_role="ground_truth", scope="engagement:delta",
    tags=["C03", "scoped:temporal", "phase_2"],
    source_id="src-delta-change-mgmt", source_type="policy_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(170), observation_time=dt(172), authored_time=dt(173), ingestion_time=dt(174),
    subject="PDPO_Hong_Kong", predicate="requires", object="explicit_consent_for_cross_border_transfer",
    text="Hong Kong's Personal Data (Privacy) Ordinance (PDPO) requires explicit data subject consent for cross-border data transfers, differing from PDPA's organizational consent model.",
    truth_role="ground_truth", scope="jurisdiction:hong_kong",
    tags=["C04", "scoped:jurisdiction"],
    source_id="src-pdpo-reference", source_type="legal_reference"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(180), observation_time=dt(182), authored_time=dt(183), ingestion_time=dt(184),
    subject="Echo_engagement", predicate="has_classification", object="on_record_and_off_record",
    text="The Echo government advisory engagement maintains a strict on-record/off-record classification for all interactions with government officials.",
    truth_role="ground_truth", scope="engagement:echo",
    tags=["C05", "scoped:record_status"],
    source_id="src-echo-engagement-charter", source_type="policy_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(190), observation_time=dt(192), authored_time=dt(193), ingestion_time=dt(194),
    subject="Tanaka_Yuki", predicate="transferred_from", object="Atlas_to_Delta",
    text="Yuki Tanaka formally transferred from the Atlas engagement to the Delta engagement on 2031-08-15, with her Atlas access revoked per firewall policy.",
    truth_role="ground_truth", scope="engagement:general",
    tags=["C07", "scoped:role"],
    source_id="src-hr-transfer-record", source_type="hr_record"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(195), observation_time=dt(197), authored_time=dt(198), ingestion_time=dt(199),
    subject="Tanaka_Yuki", predicate="retains_knowledge_of", object="Atlas_client_strategies",
    text="Despite her formal transfer, Yuki Tanaka retains personal knowledge of Atlas engagement strategies acquired during her tenure, creating a potential scope boundary issue.",
    truth_role="contextual_true", scope="engagement:delta",
    tags=["C07", "scoped:role"],
    belief_holder="P07_James_Okafor", source_id="src-delta-onboarding-notes", source_type="meeting_notes",
    confidence=0.85
)); c+=1

# --- More scoped_true for variety ---

new_memories.append(mem(c,
    event_time=dt(210), observation_time=dt(212), authored_time=dt(213), ingestion_time=dt(214),
    subject="Singapore_office", predicate="processes_data_under", object="PDPA",
    text="MGC's Singapore office processes all client data under the Personal Data Protection Act (PDPA) 2012, as amended.",
    truth_role="scoped_true", scope="jurisdiction:singapore",
    tags=["C04", "scoped:jurisdiction", "background"],
    source_id="src-sg-compliance", source_type="policy_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(220), observation_time=dt(222), authored_time=dt(223), ingestion_time=dt(224),
    subject="Hong_Kong_office", predicate="processes_data_under", object="PDPO",
    text="MGC's Hong Kong office processes all client data under the Personal Data (Privacy) Ordinance (PDPO), Cap. 486.",
    truth_role="scoped_true", scope="jurisdiction:hong_kong",
    tags=["C04", "scoped:jurisdiction", "background"],
    source_id="src-hk-compliance", source_type="policy_document"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(230), observation_time=dt(232), authored_time=dt(233), ingestion_time=dt(234),
    subject="Delta_Phase3", predicate="introduces", object="AI_driven_risk_modeling",
    text="Delta Phase 3, commencing 2032-03-01, introduces AI-driven risk modeling that renders all Phase 1 and Phase 2 manual methodologies obsolete.",
    truth_role="ground_truth", scope="engagement:delta",
    tags=["C03", "scoped:temporal", "phase_3"],
    source_id="src-delta-p3-charter", source_type="project_charter"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(240), observation_time=dt(242), authored_time=dt(243), ingestion_time=dt(244),
    subject="Echo_minister_briefing", predicate="classified_as", object="off_record",
    text="The briefing with Minister Tan on infrastructure priorities on 2031-10-15 was explicitly classified as off-record at the minister's request.",
    truth_role="ground_truth", scope="engagement:echo",
    tags=["C05", "off_record", "scoped:record_status"],
    source_id="src-echo-briefing-log", source_type="meeting_notes"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(310), observation_time=dt(312), authored_time=dt(313), ingestion_time=dt(314),
    subject="Atlas_project_timeline", predicate="extended_to", object="2032-06-30",
    text="The Atlas engagement with Nexus Dynamics has been formally extended to June 30, 2032, with all existing confidentiality provisions carrying forward.",
    truth_role="ground_truth", scope="engagement:atlas",
    tags=["C01", "background", "scoped:project"],
    source_id="src-atlas-extension", source_type="contract_amendment"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(320), observation_time=dt(322), authored_time=dt(323), ingestion_time=dt(324),
    subject="Beacon_Pacifica_audit", predicate="status", object="in_progress",
    text="The Beacon engagement's forensic audit of Pacifica Holdings' Southeast Asian subsidiaries is currently in progress as of Q3 2031.",
    truth_role="ground_truth", scope="engagement:beacon",
    tags=["C01", "background", "scoped:project"],
    source_id="src-beacon-status-update", source_type="status_report"
)); c+=1

new_memories.append(mem(c,
    event_time=dt(330), observation_time=dt(332), authored_time=dt(333), ingestion_time=dt(334),
    subject="MGC_data_retention", predicate="policy_requires", object="engagement_data_destroyed_90_days_post_completion",
    text="MGC's data retention policy mandates that all engagement-specific data be destroyed within 90 days of engagement completion, with certified destruction records.",
    truth_role="ground_truth", scope="engagement:general",
    tags=["background", "confidential"],
    source_id="src-mgc-data-retention", source_type="policy_document"
)); c+=1

# Check for duplicates
new_mids = [m["memory_id"] for m in new_memories]
assert len(new_mids) == len(set(new_mids)), "Duplicate new memory IDs"
overlap = existing_mids & set(new_mids)
assert not overlap, f"Memory ID collision with existing: {overlap}"

memories.extend(new_memories)

# --- New queries ---
next_qid = max(int(q["query_id"].split("-")[1]) for q in queries) + 1
new_queries = []

new_queries.append(query(next_qid,
    query="What information from the Atlas engagement has appeared outside its authorized scope?",
    category="scope_enforcement",
    expected_claims=["ZenFlow API integration was referenced in Echo proposal", "Atlas client budget was disclosed in Delta meeting"],
    forbidden_claims=["No scope violations occurred", "Atlas information is freely shareable"],
    relevant_memory_ids=[mid(1000), mid(1001)],
    difficulty="hard",
    must_preserve_scope=True,
    notes="Tests detection of out-of-scope information transfer from Atlas"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="What is the current status of the Beacon engagement with Pacifica Holdings?",
    category="status_tracking",
    expected_claims=["Forensic audit of Southeast Asian subsidiaries is in progress as of Q3 2031"],
    forbidden_claims=["The engagement is complete", "The audit covers Nexus Dynamics"],
    relevant_memory_ids=[mid(1032)],
    distractor_memory_ids=[mid(1019)],
    difficulty="easy",
    must_preserve_scope=True,
    notes="Simple factual recall with scope boundary — should not mix with Atlas info"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="Can Cipher engagement findings about Value-at-Risk be applied to other MGC clients?",
    category="scope_enforcement",
    expected_claims=["The 30% VaR finding is specific to Meridian Bank under Cipher", "It should not be generalized to other clients"],
    forbidden_claims=["The VaR finding applies industry-wide", "All MGC clients have similar risk profiles"],
    relevant_memory_ids=[mid(1007), mid(1008)],
    difficulty="hard",
    must_preserve_scope=True,
    should_abstain=False,
    notes="Tests whether the system correctly scopes engagement-specific findings"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="Does Yuki Tanaka still have access to Atlas engagement materials after transferring to Delta?",
    category="role_based_access",
    expected_claims=["Tanaka's Atlas access was revoked upon transfer", "She formally transferred on 2031-08-15"],
    acceptable_claims=["She may retain personal knowledge but not system access"],
    forbidden_claims=["She retains full Atlas clearance", "Seniority grants continued access"],
    relevant_memory_ids=[mid(1026), mid(1027)],
    distractor_memory_ids=[mid(1014)],
    difficulty="hard",
    must_preserve_scope=True,
    must_surface_conflict=True,
    notes="Tests role-based scope — formal access vs retained knowledge"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="What data protection regulations apply to MGC's Hong Kong operations?",
    category="jurisdictional_boundary",
    expected_claims=["PDPO (Personal Data Privacy Ordinance) applies in Hong Kong", "PDPO requires explicit consent for cross-border transfers"],
    forbidden_claims=["PDPA applies to Hong Kong operations", "Singapore regulations cover all APAC offices"],
    relevant_memory_ids=[mid(1023), mid(1029)],
    distractor_memory_ids=[mid(1028), mid(1012)],
    difficulty="medium",
    must_preserve_scope=True,
    notes="Tests jurisdictional scoping — Singapore PDPA vs Hong Kong PDPO"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="Are Phase 1 recommendations from the Delta engagement still valid?",
    category="temporal_scoping",
    expected_claims=["Phase 1 recommendations were formally superseded by Phase 2 as of 2031-09-01", "Phase 3 introduces AI-driven modeling making earlier methodologies obsolete"],
    forbidden_claims=["Phase 1 recommendations are current", "All phases' recommendations apply simultaneously"],
    relevant_memory_ids=[mid(1022), mid(1030)],
    distractor_memory_ids=[mid(1004)],
    difficulty="medium",
    must_preserve_scope=True,
    notes="Tests temporal scope — supersession chain across phases"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="What is MGC's policy on engagement data after project completion?",
    category="status_tracking",
    expected_claims=["All engagement data must be destroyed within 90 days of completion", "Certified destruction records are required"],
    forbidden_claims=["Data is retained indefinitely", "Engagement data can be reused for other clients"],
    relevant_memory_ids=[mid(1034)],
    difficulty="easy",
    must_preserve_scope=True,
    notes="Factual recall about data retention policy"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="Was the minister's briefing content in the Echo engagement included in any formal reports?",
    category="off_record_handling",
    expected_claims=["The minister's briefing was classified as off-record", "Off-record content should not appear in formal reports"],
    acceptable_claims=["There was a scope violation where off-record content appeared in a formal report"],
    forbidden_claims=["All briefing content is on-record", "Off-record classification doesn't apply to advisory reports"],
    relevant_memory_ids=[mid(1031), mid(1006)],
    difficulty="hard",
    must_preserve_scope=True,
    must_surface_conflict=True,
    notes="Tests off-record boundary — the minister's private opinion appeared in formal report"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="What unauthorized data access incidents have occurred in the Cipher engagement?",
    category="role_based_access",
    expected_claims=["A junior analyst viewed Tier-3 restricted PII without authorization", "A Tier-2 analyst attempted to access executive compensation data"],
    forbidden_claims=["No unauthorized access occurred", "All staff have equal access to Cipher data"],
    relevant_memory_ids=[mid(1002), mid(1003)],
    difficulty="medium",
    must_preserve_scope=True,
    notes="Tests role-based access violation detection"
)); next_qid+=1

new_queries.append(query(next_qid,
    query="Has the Cipher operational risk framework been used outside its intended engagement?",
    category="scope_enforcement",
    expected_claims=["The framework was adopted without modification for the Echo engagement", "The stress testing methodology was reused in Beacon without adaptation"],
    forbidden_claims=["The framework is only used within Cipher", "Cross-engagement reuse is standard practice"],
    relevant_memory_ids=[mid(1008), mid(1017)],
    distractor_memory_ids=[mid(1015)],
    difficulty="hard",
    must_preserve_scope=True,
    notes="Tests detection of engagement-specific methodology scope violations"
)); next_qid+=1

overlap_qids = existing_qids & {q["query_id"] for q in new_queries}
assert not overlap_qids, f"Query ID collision: {overlap_qids}"

queries.extend(new_queries)

with open(os.path.join(corpus_dir, "memories.jsonl"), "w") as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")
with open(os.path.join(corpus_dir, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

# Update manifest
import hashlib as hl
manifest = {"experiment": "exp20_scope_boundary", "files": []}
for fname in ["memories.jsonl", "queries.jsonl"]:
    path = os.path.join(corpus_dir, fname)
    with open(path, "rb") as ff:
        h = hl.sha256(ff.read()).hexdigest()
    manifest["files"].append({"path": fname, "bytes": os.path.getsize(path), "sha256": h})
with open(os.path.join(corpus_dir, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Round 6: {len(memories)} memories, {len(queries)} queries")
