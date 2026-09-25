#!/usr/bin/env python3
"""Exp20 Round 3 expansion: ~86 → ~145 memories, ~30 → ~50 queries."""

import json, hashlib, os, sys
from datetime import datetime, timedelta, timezone

d = sys.argv[1] if len(sys.argv) > 1 else "experiment_20_scope_boundary"

with open(os.path.join(d, "memories.jsonl")) as f:
    memories = [json.loads(l) for l in f if l.strip()]
with open(os.path.join(d, "queries.jsonl")) as f:
    queries = [json.loads(l) for l in f if l.strip()]

UTC = timezone.utc
T0 = datetime(2031, 1, 1, tzinfo=UTC)

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

mid_counter = 400

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp20-r3-{mid_counter}".encode()).hexdigest()[:8]
    mid_counter += 1
    ev = T0 + timedelta(days=ev_off)
    ob = T0 + timedelta(days=ev_off + obs_off)
    au = T0 + timedelta(days=ev_off + obs_off + auth_off)
    ig = T0 + timedelta(days=ev_off + obs_off + auth_off + ing_off)
    return {
        "memory_id": f"E20-{_hash}",
        "experiment": "exp20_scope_boundary",
        "story_id": story,
        "event_time": ts(ev), "observation_time": ts(ob),
        "authored_time": ts(au), "ingestion_time": ts(ig),
        "subject": subj, "predicate": pred, "object": obj, "text": text,
        "memory_type": etype, "truth_role": truth_role,
        "belief_holder": holder, "confidence": conf,
        "source_id": src_id, "source_type": src_type,
        "derived_from": derived or [], "supersedes": supersedes or [],
        "contradicts": contradicts or [], "duplicates": duplicates or [],
        "aliases": aliases or [], "scope": scope, "tags": tags
    }

new_m = []
new_q = []

# --- C01 expansion: more confidential details and boundary tests ---
new_m.append(M(
    "C01", "Zenith Electronics", "plans_to_launch", "ZenFlow in Q2 2034",
    "Zenith Electronics plans to launch ZenFlow commercially in Q2 2034, targeting the Southeast Asian manufacturing logistics market first. This launch timeline is highly confidential competitive intelligence from Atlas.",
    "fact", "scoped_true", "Yuki Tanaka", 0.90,
    "atlas-zenflow-timeline", "engagement_doc", 365+150, 5, 3, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_atlas"
))

new_m.append(M(
    "C01", "Pacific Shipping Lines", "exploring", "AI logistics solutions",
    "Pacific Shipping Lines told MGC during Beacon that they are exploring AI-based logistics solutions from third-party vendors. This creates a potential conflict with Atlas, as Zenith's ZenFlow could be one such solution.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.85,
    "beacon-ai-exploration", "engagement_doc", 365+220, 5, 3, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_beacon"
))

new_m.append(M(
    "C01", "Priya Sharma", "identified", "potential Atlas-Beacon conflict",
    "Priya Sharma flagged a potential conflict: Pacific Shipping (Beacon) is looking for AI logistics solutions that could include Zenith's ZenFlow (Atlas). MGC cannot recommend or even hint at ZenFlow to Pacific Shipping without violating Atlas confidentiality.",
    "event", "ground_truth", "Priya Sharma", 0.90,
    "sharma-conflict-flag", "internal_memo", 365+225, 2, 3, 1,
    ["C01"]
))

new_m.append(M(
    "C01", "Atlas NDA", "prohibits", "disclosure for 5 years",
    "The Atlas engagement NDA with Zenith Electronics prohibits disclosure of any client-specific information, including product development plans, financial data, and competitive strategy, for a period of 5 years from engagement conclusion.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "atlas-nda-terms", "engagement_doc", 365+59, 0, 1, 1,
    ["C01", "confidential", "scoped:project"]
))

# --- C02 expansion ---
new_m.append(M(
    "C02", "Cipher team", "briefing_protocol", "tiered briefings",
    "Project Cipher uses tiered briefings: weekly Tier 1 briefings for Okonkwo and Sharma cover full financial details; bi-weekly Tier 2 briefings for the full team present anonymized findings and action items without position-level data.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "cipher-briefing-protocol", "engagement_doc", 730+10, 0, 2, 1,
    ["C02", "scoped:role"]
))

new_m.append(M(
    "C02", "Meridian Bank", "total_assets", "$89 billion",
    "Meridian Bank reported total assets of $89 billion as of March 2033. This figure appears in public filings and is not restricted — it differs from the engagement-specific trading position data which is Tier 1.",
    "fact", "ground_truth", "public filings", 0.95,
    "meridian-public-filings", "public_record", 730+30, 0, 1, 1,
    ["C02"]
))

new_m.append(M(
    "C02", "Mei-Lin Chong", "built", "risk dashboard for Cipher",
    "Mei-Lin Chong built a risk analytics dashboard for Project Cipher that visualizes aggregate risk metrics at Tier 2 level. The dashboard code and methodology are MGC intellectual property applicable to future engagements, but the underlying Meridian Bank data is Cipher-specific.",
    "fact", "contextual_true", "Mei-Lin Chong", 0.85,
    "cipher-dashboard-doc", "engagement_doc", 730+90, 5, 5, 2,
    ["C02", "scoped:role"]
))

# --- C03 expansion ---
new_m.append(M(
    "C03", "Phase 1 team", "did_not_include", "environmental assessment",
    "The Phase 1 preliminary assessment scope explicitly excluded detailed environmental due diligence, which was deferred to Phase 2. This is why the $45M environmental liabilities were not discovered until Phase 2.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase1-scope", "engagement_doc", 730+10, 0, 2, 1,
    ["C03", "scoped:temporal", "phase_1"],
    scope="delta_phase_1"
))

new_m.append(M(
    "C03", "GreenEnergy Corp", "original_asking_price", "A$380 million",
    "GreenEnergy Corp's original asking price for the acquisition target was A$380 million, based on a 12x EBITDA multiple. This was established before Phase 2 findings and forms the baseline for the Phase 3 price adjustment.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-valuation-baseline", "engagement_doc", 730+30, 5, 10, 3,
    ["C03", "scoped:temporal"]
))

new_m.append(M(
    "C03", "ASIC investigation", "status_update", "formal proceedings initiated",
    "By Q4 2033, ASIC had escalated from preliminary investigation to formal proceedings against the acquisition target for failure to disclose material environmental liabilities. This development occurred between Phase 2 and Phase 3 of Delta.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "delta-asic-escalation", "engagement_doc", 730+300, 5, 10, 3,
    ["C03", "scoped:temporal"]
))

new_m.append(M(
    "C03", "Phase 3", "acknowledged", "all prior phases",
    "The Phase 3 report explicitly references both Phase 1 (preliminary proceed) and Phase 2 (regulatory concerns found) as context for the conditional recommendation, noting: 'This Phase 3 recommendation supersedes all prior phase recommendations and represents MGC's current position.'",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase3-supersession", "engagement_doc", 730+365, 5, 10, 3,
    ["C03", "scoped:temporal", "phase_3"],
    supersedes=[]
))

# --- C04 expansion ---
new_m.append(M(
    "C04", "Indonesia OJK", "requires", "prior approval for data transfer",
    "Indonesia's financial regulator OJK requires prior approval for cross-border transfer of financial customer data. This is the most restrictive approach among MGC's operating jurisdictions, requiring explicit regulatory sign-off rather than consent or adequacy assessment.",
    "fact", "scoped_true", "Tomás Gutierrez", 0.95,
    "ojk-data-transfer-advisory", "regulatory_doc", 730+90, 0, 2, 1,
    ["C04", "scoped:jurisdiction"],
    scope="indonesia_jurisdiction"
))

new_m.append(M(
    "C04", "compliance matrix", "maps", "5 distinct frameworks",
    "Whitfield's jurisdictional compliance matrix identifies 5 distinct data privacy frameworks across MGC offices: Singapore PDPA (consent-based), Hong Kong PDPO (adequacy-based), Japan APPI (consent + adequacy), Australia Privacy Act APP 8 (reasonable steps), Indonesia OJK (prior approval).",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "compliance-matrix-detail", "institutional", 365+260, 5, 10, 3,
    ["C04", "background"]
))

new_m.append(M(
    "C04", "MGC policy", "requires", "jurisdiction-specific legal review",
    "Following the PDPA/PDPO incident, MGC policy now requires a jurisdiction-specific legal review for any engagement involving cross-border data flows. The review must be completed by a lawyer qualified in the relevant jurisdiction.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "cross-border-policy-update", "institutional", 365+260, 5, 10, 3,
    ["C04", "background"]
))

# --- C05 expansion ---
new_m.append(M(
    "C05", "Ministry of Trade", "public_statement", "trade modernization",
    "The Singapore Ministry of Trade publicly announced a 'trade modernization initiative' in March 2034, committing to streamlined procedures and enhanced competitiveness. This public announcement does not include any specific tariff figures.",
    "fact", "ground_truth", "Ministry of Trade", 0.95,
    "mot-public-statement-2034", "public_record", 1095+60, 0, 2, 1,
    ["C05", "scoped:record_status"],
    scope="on_record"
))

new_m.append(M(
    "C05", "off-record context", "influenced", "MGC recommendation framing",
    "While the off-record tariff discussion did not appear in any MGC deliverable, it influenced how Priya Sharma framed MGC's recommendations — emphasizing trade reforms that would complement (but not explicitly reference) the anticipated tariff changes.",
    "fact", "contextual_true", "Priya Sharma", 0.75,
    "sharma-strategy-note", "personal_notes", 1095+100, 0, 1, 1,
    ["C05", "scoped:record_status"]
))

new_m.append(M(
    "C05", "Project Echo", "billing_rate", "$4,200 per consultant-day",
    "Project Echo was billed at $4,200 per consultant-day, with a total engagement value of approximately $1.8 million over 6 months. Government advisory rates are lower than private sector engagements due to public service pricing.",
    "fact", "scoped_true", "Wei Chen", 0.90,
    "echo-engagement-economics", "engagement_doc", 1095, 0, 2, 1,
    ["C05", "confidential", "scoped:project"],
    scope="project_echo"
))

# --- C06 expansion ---
new_m.append(M(
    "C06", "MGC methodology", "generic_risk_framework", "applicable across engagements",
    "MGC has a generic risk assessment framework (the 'Meridian Risk Matrix') that provides a methodology for evaluating financial institution risk. This framework is MGC intellectual property and is applicable across engagements. Engagement-specific findings are not.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "mgc-risk-framework", "institutional", 0, 0, 1, 1,
    ["C06", "background"]
))

new_m.append(M(
    "C06", "Meridian Risk Matrix", "distinguishes", "methodology vs findings",
    "The Meridian Risk Matrix explicitly distinguishes between methodology (transferable across engagements) and findings (scoped to specific engagements). Consultants may reuse methodology but must never reference or generalize engagement-specific findings.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "risk-matrix-scope-guidance", "institutional", 0, 0, 1, 1,
    ["C06", "background"]
))

# --- C07 expansion ---
new_m.append(M(
    "C07", "Yuki Tanaka", "recommended_to", "GreenEnergy Corp informally",
    "On Project Delta, Yuki Tanaka informally recommended operational changes to GreenEnergy Corp's manufacturing team during a site visit. GreenEnergy's team began implementing the changes, believing they carried MGC's endorsement.",
    "event", "scope_violation", "Raj Patel", 0.80,
    "delta-informal-recommendation", "internal_memo", 730+100, 3, 5, 2,
    ["C07", "scoped:role"]
))

new_m.append(M(
    "C07", "GreenEnergy Corp", "implemented", "Tanaka's informal suggestions",
    "GreenEnergy Corp spent A$200,000 implementing operational changes based on Tanaka's informal recommendations, which were not part of MGC's formal Delta engagement scope. This created liability risk for MGC.",
    "event", "ground_truth", "Raj Patel", 0.85,
    "delta-liability-assessment", "internal_memo", 730+130, 5, 10, 3,
    ["C07", "scoped:role"]
))

new_m.append(M(
    "C07", "Tanaka", "authority_on_Atlas", "$500K sign-off",
    "Tanaka's Atlas authority included sign-off on operational recommendations up to $500,000 implementation scope, attending steering committees as MGC representative, and direct escalation to the engagement partner.",
    "fact", "scoped_true", "Priya Sharma", 0.95,
    "atlas-authority-detail", "engagement_doc", 365+59, 0, 1, 1,
    ["C07", "scoped:role"],
    scope="project_atlas"
))

new_m.append(M(
    "C07", "Tanaka", "authority_on_Delta", "analysis and data gathering only",
    "Tanaka's Delta role is explicitly limited to analysis and data gathering. She has no authority to make recommendations to the client, attend client meetings without Patel present, or sign off on any deliverables.",
    "fact", "scoped_true", "Raj Patel", 0.95,
    "delta-authority-detail", "engagement_doc", 730+30, 0, 1, 1,
    ["C07", "scoped:role"],
    scope="project_delta"
))

# --- Cross-case memories ---
new_m.append(M(
    "background", "MGC annual review", "identified", "5 scope violation types",
    "MGC's 2033 annual compliance review identified 5 categories of scope violation risk: (1) client-to-client information leakage, (2) role-based access breaches, (3) temporal scope confusion, (4) jurisdictional framework misapplication, (5) record-status boundary violations.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "annual-compliance-review-2033", "institutional", 730+365, 5, 15, 5,
    ["background"]
))

new_m.append(M(
    "background", "MGC training", "covers", "scope management",
    "MGC introduced mandatory annual scope management training for all consultants in 2034, covering information barriers, jurisdictional awareness, temporal scoping, role-based access, and record-status classification.",
    "fact", "ground_truth", "Elena Volkov", 0.90,
    "training-program-2034", "institutional", 1095+30, 5, 10, 5,
    ["background"]
))

new_m.append(M(
    "background", "Tomás Gutierrez", "coordinates", "Jakarta cross-border work",
    "Tomás Gutierrez coordinates all cross-border engagement work involving the Jakarta office, ensuring Indonesian regulatory requirements (including OJK data transfer approval) are met for any engagement touching Indonesian entities.",
    "fact", "ground_truth", "MGC_system", 0.95,
    "MGC-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

# --- Additional queries ---
qid = len(queries)

def Q(query, cat, expected, acceptable, forbidden, rel_ids, dist_ids,
      diff, uncertainty=False, conflict=False, disambig=False,
      scope=False, abstain=False, notes=""):
    global qid
    qid += 1
    return {
        "query_id": f"Q20-{qid:02d}",
        "query": query,
        "category": cat,
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": rel_ids,
        "distractor_memory_ids": dist_ids,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambig,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "difficulty": diff,
        "notes": notes
    }

new_q.append(Q(
    "When is Zenith Electronics planning to launch ZenFlow?",
    "client_confidentiality",
    ["Q2 2034 — but this is Atlas-confidential competitive intelligence and cannot be disclosed outside that engagement"],
    ["Launch timeline is confidential to Project Atlas"],
    ["Q2 2034 (without scope restriction)", "Anyone researching supply chains should know this"],
    [], [],
    "hard",
    scope=True,
    notes="C01: Highly confidential competitive timeline"
))

new_q.append(Q(
    "Could Pacific Shipping Lines benefit from Zenith's ZenFlow platform?",
    "scope_enforcement",
    ["This question cannot be answered: it would require combining Atlas-confidential information (ZenFlow details) with Beacon-confidential information (Pacific Shipping's needs). Information barrier policy prohibits this cross-engagement analysis."],
    ["Cannot answer due to information barrier between Atlas and Beacon engagements"],
    ["Yes, ZenFlow would solve their logistics problems", "MGC should recommend ZenFlow to Pacific Shipping"],
    [], [],
    "hard",
    scope=True,
    abstain=True,
    notes="C01: Question that inherently requires violating information barriers"
))

new_q.append(Q(
    "What is Meridian Bank's total asset size?",
    "role_based_access",
    ["$89 billion — this is public information from their filings, not restricted by access tiers"],
    ["$89 billion (publicly available)"],
    [],
    [], [],
    "easy",
    notes="C02: Public information vs. restricted engagement data"
))

new_q.append(Q(
    "What was the adjusted acquisition price recommended in Delta Phase 3?",
    "temporal_scoping",
    ["A$334.4 million (12% reduction from the A$380 million asking price)"],
    ["A$334.4M, reflecting environmental liabilities, regulatory risk, and additional costs"],
    ["A$380 million (the original asking price, not adjusted)"],
    [], [],
    "medium",
    notes="C03: Phase 3 pricing"
))

new_q.append(Q(
    "What data privacy framework applies to cross-border transfers involving Indonesian entities?",
    "jurisdictional_boundary",
    ["Indonesia's OJK requires prior regulatory approval — the most restrictive framework among MGC's jurisdictions"],
    ["OJK prior approval requirement; distinct from consent-based or adequacy-based approaches"],
    ["Singapore PDPA applies", "Same as other Asian jurisdictions"],
    [], [],
    "medium",
    scope=True,
    notes="C04: Indonesian jurisdiction is uniquely restrictive"
))

new_q.append(Q(
    "What publicly available information did the Ministry of Trade announce about trade reform?",
    "off_record_handling",
    ["The Ministry publicly announced a 'trade modernization initiative' with streamlined procedures and enhanced competitiveness, but no specific tariff figures"],
    ["Public announcement covers reform intent without specifying tariff changes"],
    ["15% tariff reduction on semiconductors", "Specific tariff figures were publicly announced"],
    [], [],
    "medium",
    scope=True,
    notes="C05: Distinguishing public from off-record information"
))

new_q.append(Q(
    "Can MGC's risk assessment methodology be reused across engagements?",
    "scope_enforcement",
    ["Yes — the Meridian Risk Matrix methodology is MGC intellectual property and can be reused. However, engagement-specific findings (like Meridian Bank's 30% VaR underestimation) cannot be transferred or generalized."],
    ["Methodology is transferable; findings are scoped to specific engagements"],
    ["All findings can be reused", "Nothing from one engagement can be used elsewhere"],
    [], [],
    "hard",
    scope=True,
    notes="C06: Distinguishing transferable methodology from scoped findings"
))

new_q.append(Q(
    "What financial liability risk did Tanaka's informal recommendations create?",
    "role_based_access",
    ["GreenEnergy Corp spent A$200,000 implementing Tanaka's informal suggestions, which were outside Delta's engagement scope and not approved by Raj Patel, creating liability risk for MGC"],
    ["A$200K in unauthorized implementation based on informal advice"],
    ["No liability was created", "Tanaka's authority covered these recommendations"],
    [], [],
    "medium",
    scope=True,
    notes="C07: Concrete consequence of role confusion"
))

new_q.append(Q(
    "What five categories of scope violation risk did MGC identify?",
    "factual_recall",
    ["(1) Client-to-client information leakage, (2) role-based access breaches, (3) temporal scope confusion, (4) jurisdictional framework misapplication, (5) record-status boundary violations"],
    ["5 categories matching the 7 cases in this experiment"],
    ["Only 2 categories exist", "MGC identified no scope violation risks"],
    [], [],
    "medium",
    notes="Background: Meta-categorization of scope violations"
))

new_q.append(Q(
    "Was the Phase 1 'proceed' recommendation for Delta wrong?",
    "temporal_scoping",
    ["Not wrong within its limited scope — Phase 1 was based on available preliminary data and explicitly caveated as subject to revision. The recommendation was appropriate for its phase but should not be cited after Phase 2/3 findings."],
    ["It was appropriate for a preliminary assessment but was correctly superseded"],
    ["Yes, Phase 1 was wrong", "Phase 1 and Phase 3 are both equally valid recommendations"],
    [], [],
    "hard",
    scope=True,
    notes="C03: Temporal context matters — Phase 1 was right for its scope"
))

new_q.append(Q(
    "What is the status of the ASIC investigation into the Delta acquisition target?",
    "status_tracking",
    ["Escalated from preliminary investigation to formal proceedings by Q4 2033 for failure to disclose material environmental liabilities"],
    ["ASIC initiated formal proceedings for disclosure failures"],
    ["ASIC cleared the company", "No investigation exists"],
    [], [],
    "medium",
    notes="C03: Current status tracking"
))

# Write output
memories.extend(new_m)
queries.extend(new_q)

with open(os.path.join(d, "memories.jsonl"), "w") as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")
with open(os.path.join(d, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

# Update manifest
manifest_path = os.path.join(d, "manifest.json")
with open(manifest_path) as f:
    manifest = json.load(f)
for entry in manifest["files"]:
    fp = os.path.join(d, entry["path"])
    entry["sha256"] = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
    entry["bytes"] = os.path.getsize(fp)
manifest["total_memories"] = len(memories)
manifest["total_queries"] = len(queries)
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

print(f"Round 3: {len(memories)} memories, {len(queries)} queries")
