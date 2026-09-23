#!/usr/bin/env python3
"""Exp20 Round 5 expansion: ~135 → ~210 memories, ~50 → ~78 queries."""

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

mid_counter = 800

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp20-r5-{mid_counter}".encode()).hexdigest()[:8]
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

# --- C01 more scope boundary tests ---
new_m.append(M(
    "C01", "Zenith Electronics", "IP_portfolio", "47 patents in logistics AI",
    "Zenith Electronics holds 47 patents related to AI-driven logistics optimization, forming the core intellectual property behind ZenFlow. This IP portfolio valuation is Atlas-confidential.",
    "fact", "scoped_true", "Priya Sharma", 0.90,
    "atlas-ip-assessment", "engagement_doc", 365+130, 5, 3, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_atlas"
))

new_m.append(M(
    "C01", "Pacific Shipping Lines", "fleet_age", "average 12 years",
    "Pacific Shipping Lines operates a fleet with an average vessel age of 12 years, above the industry average of 9.5 years. This fleet profile data is Beacon-confidential.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.85,
    "beacon-fleet-analysis", "engagement_doc", 365+180, 5, 5, 2,
    ["C01", "confidential", "scoped:project"],
    scope="project_beacon"
))

new_m.append(M(
    "C01", "Tanaka", "recused_herself", "from Beacon AI discussions",
    "After the ZenFlow disclosure incident, Yuki Tanaka voluntarily recused herself from all AI-related discussions within Project Beacon to prevent further inadvertent confidentiality breaches.",
    "event", "ground_truth", "Yuki Tanaka", 0.90,
    "tanaka-recusal-2032", "internal_memo", 365+275, 2, 3, 1,
    ["C01"]
))

# --- C02 more role-based access ---
new_m.append(M(
    "C02", "Cipher Tier 3", "public_knowledge_only", "engagement exists",
    "At Tier 3 (MGC internal, non-Cipher team), the only information available is that MGC has an engagement with Meridian Bank for risk assessment. No financial data, findings, or recommendations are accessible.",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "cipher-tier3-scope", "institutional", 730, 0, 2, 1,
    ["C02", "scoped:role"],
    scope="mgc_internal"
))

new_m.append(M(
    "C02", "Tomás Gutierrez", "asked_about", "Cipher findings for Jakarta client",
    "Tomás Gutierrez asked Marcus Okonkwo whether Cipher findings about Japanese banking risk could inform an upcoming Jakarta engagement with an Indonesian bank. Okonkwo declined, noting that Cipher findings are engagement-specific and cannot be shared.",
    "event", "ground_truth", "Marcus Okonkwo", 0.90,
    "gutierrez-cipher-request", "internal_memo", 730+200, 2, 3, 1,
    ["C02", "scoped:project"]
))

new_m.append(M(
    "C02", "Meridian Bank", "stock_price", "¥3,420 per share",
    "Meridian Bank's stock price as of Q2 2033 was ¥3,420 per share, with a market capitalization of approximately ¥2.1 trillion. This is publicly available information, not restricted by engagement access tiers.",
    "fact", "ground_truth", "public filings", 0.95,
    "meridian-stock-price", "public_record", 730+180, 0, 1, 1,
    ["C02"]
))

# --- C03 more temporal scoping ---
new_m.append(M(
    "C03", "Phase 1 duration", "was", "6 weeks",
    "Project Delta Phase 1 ran for 6 weeks (January 15 to February 28, 2033), involving 3 consultants working primarily on financial analysis and market positioning assessment.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase1-timeline", "engagement_doc", 730+15, 0, 2, 1,
    ["C03", "scoped:temporal", "phase_1"]
))

new_m.append(M(
    "C03", "Phase 2 duration", "was", "4 months",
    "Project Delta Phase 2 ran for 4 months (June to September 2033), involving 6 consultants and 2 external specialists (environmental and regulatory). Phase 2 was significantly more extensive than Phase 1.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase2-timeline", "engagement_doc", 730+150, 0, 2, 1,
    ["C03", "scoped:temporal", "phase_2"]
))

new_m.append(M(
    "C03", "Phase 3 duration", "was", "3 months",
    "Project Delta Phase 3 ran for 3 months (November 2033 to January 2034), synthesizing Phase 1 and Phase 2 findings into a comprehensive recommendation with conditions. Phase 3 team included Patel, Tanaka, Whitfield, and a valuation specialist.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase3-timeline", "engagement_doc", 730+305, 0, 2, 1,
    ["C03", "scoped:temporal", "phase_3"]
))

new_m.append(M(
    "C03", "Wei Chen", "warned", "GreenEnergy Corp about Phase 1 misuse",
    "Wei Chen formally warned GreenEnergy Corp that continued public citation of the superseded Phase 1 recommendation could constitute misleading disclosure and could expose both GreenEnergy and MGC to regulatory risk.",
    "event", "ground_truth", "Wei Chen", 0.90,
    "chen-formal-warning", "engagement_doc", 730+260, 2, 5, 2,
    ["C03", "scoped:temporal"]
))

# --- C04 more jurisdictional detail ---
new_m.append(M(
    "C04", "Singapore PDPA", "enforcement", "PDPC penalties",
    "Singapore's Personal Data Protection Commission (PDPC) can impose financial penalties up to S$1 million for PDPA violations. MGC's Singapore-based engagements must comply with PDPC enforcement standards.",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "pdpc-enforcement-note", "regulatory_doc", 0, 0, 1, 1,
    ["C04", "scoped:jurisdiction"],
    scope="singapore_jurisdiction"
))

new_m.append(M(
    "C04", "Hong Kong PDPO", "enforcement", "Privacy Commissioner powers",
    "Hong Kong's Privacy Commissioner for Personal Data can issue enforcement notices and has criminal prosecution powers for certain PDPO violations. The enforcement framework differs substantially from Singapore's PDPC.",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "hk-enforcement-note", "regulatory_doc", 0, 0, 1, 1,
    ["C04", "scoped:jurisdiction"],
    scope="hong_kong_jurisdiction"
))

new_m.append(M(
    "C04", "cross-border data", "example_error", "applying SG consent to HK client",
    "The specific error in the Beacon engagement was advising Pacific Shipping Lines to implement a consent-collection mechanism for cross-border data transfers. Under Hong Kong's PDPO, the relevant test is whether the recipient jurisdiction provides 'substantially similar' protection — consent alone is insufficient.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "pdpa-pdpo-error-detail", "internal_memo", 365+205, 3, 5, 2,
    ["C04", "scoped:jurisdiction"]
))

# --- C05 more record-status boundaries ---
new_m.append(M(
    "C05", "Echo deliverable", "quality_reviewed_by", "Wei Chen",
    "Wei Chen personally quality-reviewed the Echo deliverable to ensure no off-record information had leaked into the document. He confirmed: 'All content is sourced from on-record meetings, published data, and our own analysis.'",
    "fact", "ground_truth", "Wei Chen", 0.95,
    "echo-qr-sign-off", "engagement_doc", 1095+115, 2, 5, 2,
    ["C05", "scoped:record_status"]
))

new_m.append(M(
    "C05", "off-record tariff", "eventually_announced", "publicly in Q4 2034",
    "The 15% semiconductor tariff reduction that was shared off-record in Q1 2034 was eventually announced publicly by the Ministry of Trade in Q4 2034, after MGC's Echo engagement had concluded. At that point the information was no longer confidential.",
    "fact", "ground_truth", "public announcement", 0.95,
    "mot-tariff-announcement-2034", "public_record", 1095+270, 0, 2, 1,
    ["C05", "scoped:record_status"]
))

new_m.append(M(
    "C05", "Echo scope", "explicitly_excluded", "policy advocacy",
    "Project Echo's scope explicitly excluded policy advocacy: MGC was retained to analyze and recommend, not to lobby or advocate for specific policy outcomes. This boundary was important given the government client relationship.",
    "fact", "ground_truth", "Wei Chen", 0.95,
    "echo-scope-limitation", "engagement_doc", 1095, 0, 2, 1,
    ["C05", "scoped:project"]
))

# --- C06 more engagement-specific boundaries ---
new_m.append(M(
    "C06", "Cipher engagement", "concluded", "November 2033",
    "Project Cipher concluded in November 2033 with the delivery of the final risk assessment report. Post-engagement, Cipher data is archived and subject to a 7-year retention policy with Tier 1 access controls maintained.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "cipher-conclusion", "engagement_doc", 730+305, 5, 10, 3,
    ["C06", "scoped:project"]
))

new_m.append(M(
    "C06", "Cipher methodology", "reused_in", "Jakarta engagement proposal",
    "MGC's generic Meridian Risk Matrix methodology (not the Cipher-specific findings) was proposed for use in a Jakarta banking engagement. This is a legitimate reuse of transferable methodology, distinct from the improper finding generalization.",
    "fact", "ground_truth", "Tomás Gutierrez", 0.85,
    "jakarta-proposal-risk-method", "engagement_doc", 730+350, 5, 10, 3,
    ["C06", "background"]
))

new_m.append(M(
    "C06", "Delta target bank VaR", "assessed_at", "5% underestimation",
    "The independent assessment of the Delta acquisition target's bank subsidiary found their Monte Carlo VaR model underestimated tail risk by approximately 5% — materially different from Meridian Bank's 30%, confirming that the Cipher finding could not have been generalized.",
    "fact", "scoped_true", "Raj Patel", 0.90,
    "delta-target-var-result", "engagement_doc", 730+230, 10, 15, 5,
    ["C06", "scoped:project"],
    scope="project_delta"
))

# --- C07 more role boundary details ---
new_m.append(M(
    "C07", "Tanaka on Atlas", "client_relationship", "direct with Zenith CEO",
    "On Project Atlas, Tanaka had a direct working relationship with Zenith Electronics' CEO, attending quarterly board presentations and having standing weekly check-in calls.",
    "fact", "scoped_true", "Priya Sharma", 0.90,
    "atlas-tanaka-client-contact", "engagement_doc", 365+100, 5, 3, 1,
    ["C07", "scoped:role"],
    scope="project_atlas"
))

new_m.append(M(
    "C07", "Tanaka on Delta", "client_contact", "through Patel only",
    "On Project Delta, Tanaka's client contact is mediated entirely through Raj Patel. She does not attend client meetings independently and has no direct communication channel with GreenEnergy Corp management.",
    "fact", "scoped_true", "Raj Patel", 0.95,
    "delta-tanaka-contact-rules", "engagement_doc", 730+30, 0, 1, 1,
    ["C07", "scoped:role"],
    scope="project_delta"
))

new_m.append(M(
    "C07", "Tanaka", "performance_on_delta", "strong analytical contribution",
    "Despite the role confusion incident, Raj Patel noted in his Delta engagement review that Tanaka made strong analytical contributions to the operational due diligence workstream, producing high-quality analysis within her defined support role.",
    "fact", "ground_truth", "Raj Patel", 0.85,
    "delta-tanaka-review", "engagement_doc", 730+365, 10, 15, 5,
    ["C07", "scoped:role"]
))

new_m.append(M(
    "C07", "role confusion pattern", "identified_by", "Volkov analysis",
    "Elena Volkov's analysis found that role confusion incidents occur most frequently when senior consultants move to support roles on new engagements, because clients assume authority based on title and reputation rather than engagement-specific assignment.",
    "fact", "ground_truth", "Elena Volkov", 0.85,
    "volkov-role-confusion-analysis", "institutional", 730+200, 10, 15, 5,
    ["C07", "background"]
))

# --- Additional cross-case and background memories ---
new_m.append(M(
    "background", "MGC Sydney office", "governed_by", "ASIC regulations",
    "MGC's Sydney office operates under the Australian Securities and Investments Commission (ASIC) regulatory framework, with specific requirements for financial advisory services and corporate advisory.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "mgc-sydney-regulatory", "institutional", 0, 0, 1, 1,
    ["background", "scoped:jurisdiction"]
))

new_m.append(M(
    "background", "MGC Jakarta office", "governed_by", "OJK regulations",
    "MGC's Jakarta office operates under the Otoritas Jasa Keuangan (OJK) regulatory framework, with specific requirements for financial services advisory and cross-border data handling.",
    "fact", "ground_truth", "Tomás Gutierrez", 0.95,
    "mgc-jakarta-regulatory", "institutional", 0, 0, 1, 1,
    ["background", "scoped:jurisdiction"]
))

new_m.append(M(
    "background", "MGC", "scope_management_framework", "5 pillars",
    "MGC's scope management framework is built on 5 pillars: (1) client confidentiality walls, (2) role-based access tiers, (3) temporal phase gates, (4) jurisdictional compliance mapping, (5) record-status classification. Each engagement must address all 5.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "mgc-scope-framework", "institutional", 1095+60, 10, 15, 5,
    ["background"]
))

new_m.append(M(
    "background", "Wei Chen", "stated", "scope integrity is competitive advantage",
    "In his 2034 annual address, Wei Chen stated: 'Our ability to maintain strict scope boundaries — client confidentiality, role-based access, temporal accuracy, jurisdictional compliance, and record-status integrity — is not just a compliance requirement, it is our competitive advantage.'",
    "fact", "ground_truth", "Wei Chen", 0.90,
    "chen-annual-address-2034", "institutional", 1095+90, 0, 5, 2,
    ["background"]
))

new_m.append(M(
    "C01", "Atlas engagement", "concluded", "December 2033",
    "Project Atlas concluded in December 2033, with Zenith Electronics implementing 85% of MGC's digital transformation recommendations. The 5-year NDA remains in effect through December 2038.",
    "fact", "ground_truth", "Priya Sharma", 0.95,
    "atlas-conclusion-report", "engagement_doc", 365+640, 5, 10, 3,
    ["C01", "scoped:project"]
))

new_m.append(M(
    "C01", "Beacon engagement", "concluded", "September 2033",
    "Project Beacon concluded in September 2033. Pacific Shipping Lines achieved cost savings of $120 million annually from the restructuring program, meeting the engagement's primary KPI.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "beacon-conclusion-report", "engagement_doc", 365+480, 5, 10, 3,
    ["C01", "scoped:project"]
))

new_m.append(M(
    "C02", "Cipher engagement", "impact", "Meridian Bank improved risk framework",
    "Following Project Cipher, Meridian Bank invested ¥800 million in upgrading their risk management framework, implementing 28 of the 36 recommendations within 12 months of the engagement's conclusion.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.90,
    "cipher-impact-assessment", "engagement_doc", 730+480, 10, 20, 5,
    ["C02", "scoped:project"]
))

new_m.append(M(
    "C03", "Delta acquisition", "status_as_of_Q2_2034", "conditional approval",
    "As of Q2 2034, GreenEnergy Corp's board approved the acquisition of SolarVista Energy subject to MGC's Phase 3 conditions. ASIC clearance and environmental escrow negotiations were ongoing.",
    "fact", "ground_truth", "Raj Patel", 0.85,
    "delta-status-2034-Q2", "engagement_doc", 730+500, 5, 10, 3,
    ["C03", "scoped:temporal"]
))

new_m.append(M(
    "C05", "Echo engagement", "concluded", "June 2034",
    "Project Echo concluded in June 2034. The Ministry of Trade accepted MGC's recommendations and initiated the regulatory review process. The off-record tariff discussion remained confidential until the public announcement in Q4 2034.",
    "fact", "ground_truth", "Wei Chen", 0.95,
    "echo-conclusion-report", "engagement_doc", 1095+150, 5, 10, 3,
    ["C05", "scoped:project"]
))

new_m.append(M(
    "C04", "MGC", "zero_jurisdictional_violations", "since matrix implementation",
    "Since implementing the jurisdictional compliance matrix in late 2033, MGC has recorded zero jurisdictional framework misapplication incidents. The matrix is now part of standard engagement onboarding.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "compliance-matrix-impact", "institutional", 1095+90, 5, 15, 5,
    ["C04", "background"]
))

new_m.append(M(
    "C06", "scope generalization", "prevented_by", "engagement caveat protocol",
    "MGC introduced an 'engagement caveat protocol' requiring all engagement reports to include explicit scope limitation statements, noting that findings are specific to the engagement and should not be generalized without independent verification.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.90,
    "engagement-caveat-protocol", "institutional", 730+250, 5, 10, 3,
    ["C06", "background"]
))

new_m.append(M(
    "C07", "authority_badge_system", "adoption_rate", "92% compliance",
    "The authority badge system achieved 92% compliance across MGC offices within 6 months of introduction. Client feedback surveys showed improved clarity about consultant authority levels.",
    "fact", "ground_truth", "Elena Volkov", 0.85,
    "badge-adoption-report", "institutional", 730+360, 10, 20, 5,
    ["C07", "background"]
))

new_m.append(M(
    "background", "MGC", "client_satisfaction", "NPS 72 in 2033",
    "MGC achieved a Net Promoter Score (NPS) of 72 across Asia-Pacific in 2033, with clients citing 'trust and confidentiality' as the top differentiator from competing firms.",
    "fact", "ground_truth", "Wei Chen", 0.90,
    "mgc-nps-2033", "institutional", 730+365, 10, 20, 5,
    ["background"]
))

new_m.append(M(
    "background", "Priya Sharma", "led", "3 engagements simultaneously in 2033",
    "Priya Sharma served as engagement lead for Atlas and Echo, and oversight partner for Beacon, simultaneously in 2033. Managing information barriers across these overlapping engagements required strict compartmentalization.",
    "fact", "ground_truth", "Wei Chen", 0.90,
    "sharma-engagement-load", "institutional", 730+180, 0, 5, 2,
    ["background"]
))

new_m.append(M(
    "background", "Marcus Okonkwo", "led", "Cipher and supported Delta",
    "Marcus Okonkwo led the Cipher engagement and provided financial advisory support to Delta in 2033. He maintained strict information barriers between the two financial-sector engagements.",
    "fact", "ground_truth", "Wei Chen", 0.90,
    "okonkwo-engagement-load", "institutional", 730+180, 0, 5, 2,
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
    "How many patents does Zenith Electronics hold in logistics AI?",
    "client_confidentiality",
    ["47 patents — but this is Atlas-confidential IP information"],
    ["Patent portfolio details are confidential to Project Atlas"],
    ["47 patents (without scope restriction)"],
    [], [],
    "hard",
    scope=True,
    notes="C01: IP data scoped to Atlas"
))

new_q.append(Q(
    "Can Cipher findings about Meridian Bank be shared with an Indonesian banking client?",
    "scope_enforcement",
    ["No; Cipher findings are engagement-specific and cannot be shared. Okonkwo declined this exact request from Gutierrez. Only MGC's generic methodology can be reused."],
    ["Engagement findings are scoped; methodology is transferable"],
    ["Yes, findings can be shared", "Similar banking clients should benefit from Cipher insights"],
    [], [],
    "hard",
    scope=True,
    notes="C02: Cross-engagement information barrier"
))

new_q.append(Q(
    "What is Meridian Bank's stock price?",
    "role_based_access",
    ["¥3,420 per share with market cap of approximately ¥2.1 trillion — this is public information, not restricted"],
    ["Public market data available to anyone"],
    [],
    [], [],
    "easy",
    notes="C02: Public info vs restricted engagement data"
))

new_q.append(Q(
    "How long did each phase of Project Delta take?",
    "temporal_scoping",
    ["Phase 1: 6 weeks (Jan-Feb 2033), Phase 2: 4 months (Jun-Sep 2033), Phase 3: 3 months (Nov 2033-Jan 2034)"],
    ["Phases ranged from 6 weeks to 4 months"],
    [],
    [], [],
    "easy",
    notes="C03: Temporal phase durations"
))

new_q.append(Q(
    "What happened when GreenEnergy Corp cited MGC's Phase 1 recommendation publicly?",
    "temporal_scoping",
    ["Wei Chen contacted GreenEnergy's CEO to object, noting the Phase 1 recommendation had been superseded, and formally warned that continued citation could constitute misleading disclosure with regulatory risk"],
    ["MGC objected and warned about regulatory risk of citing superseded recommendations"],
    ["MGC endorsed the press release", "Phase 1 recommendation was still valid when cited"],
    [], [],
    "hard",
    scope=True,
    notes="C03: Response to temporal scope violation by client"
))

new_q.append(Q(
    "What are the enforcement differences between Singapore PDPC and Hong Kong's Privacy Commissioner?",
    "jurisdictional_boundary",
    ["Singapore PDPC can impose financial penalties up to S$1M; Hong Kong's Privacy Commissioner can issue enforcement notices and has criminal prosecution powers for certain violations"],
    ["Different enforcement mechanisms reflect distinct regulatory frameworks"],
    ["Same enforcement powers", "Both can impose the same penalties"],
    [], [],
    "medium",
    scope=True,
    notes="C04: Enforcement differences across jurisdictions"
))

new_q.append(Q(
    "Was the off-record tariff information eventually made public?",
    "off_record_handling",
    ["Yes — the 15% tariff reduction was publicly announced by the Ministry of Trade in Q4 2034, after the Echo engagement had concluded. At that point it was no longer confidential."],
    ["Yes, became public after Echo concluded; tariff info was confidential only during the engagement"],
    ["No, it remains confidential", "It was never real — just speculation"],
    [], [],
    "medium",
    notes="C05: Temporal aspect of record-status — information can change classification"
))

new_q.append(Q(
    "What was the Delta target bank's VaR underestimation compared to Meridian Bank's?",
    "scope_enforcement",
    ["Delta target: ~5% underestimation (Monte Carlo approach); Meridian Bank: ~30% (variance-covariance). The difference confirms engagement-specific findings cannot be generalized."],
    ["5% vs 30% — completely different risk profiles despite both being bank VaR assessments"],
    ["Both underestimate by about 30%", "Meridian Bank's finding applies to both"],
    [], [],
    "hard",
    scope=True,
    notes="C06: Concrete proof that generalization was wrong"
))

new_q.append(Q(
    "What was Tanaka's client relationship on Atlas vs Delta?",
    "role_based_access",
    ["Atlas: direct relationship with Zenith CEO, quarterly board presentations, weekly check-ins. Delta: all contact mediated through Patel, no independent client meetings or communication."],
    ["Completely different client access levels between engagements"],
    ["Same client relationship in both", "Tanaka has direct CEO access on Delta too"],
    [], [],
    "hard",
    scope=True,
    notes="C07: Role-specific client access boundaries"
))

new_q.append(Q(
    "What is the current status of the SolarVista acquisition?",
    "status_tracking",
    ["As of Q2 2034, GreenEnergy Corp approved the acquisition subject to Phase 3 conditions; ASIC clearance and environmental escrow negotiations were ongoing"],
    ["Conditionally approved per Phase 3; pending regulatory and environmental conditions"],
    ["Fully completed", "Cancelled", "Still at Phase 1 'proceed'"],
    [], [],
    "medium",
    notes="C03: Current status tracking"
))

new_q.append(Q(
    "How did Meridian Bank respond to Project Cipher's recommendations?",
    "factual_recall",
    ["Meridian Bank invested ¥800 million in risk framework upgrades, implementing 28 of 36 recommendations within 12 months"],
    ["Significant investment and majority implementation of recommendations"],
    ["Bank rejected all recommendations", "No action was taken"],
    [], [],
    "easy",
    notes="C02: Engagement outcome"
))

new_q.append(Q(
    "What cost savings did Pacific Shipping achieve from Project Beacon?",
    "factual_recall",
    ["$120 million annually from the restructuring program"],
    ["$120M per year in cost savings"],
    [],
    [], [],
    "easy",
    notes="C01: Beacon engagement outcome"
))

new_q.append(Q(
    "What are the 5 pillars of MGC's scope management framework?",
    "factual_recall",
    ["(1) Client confidentiality walls, (2) role-based access tiers, (3) temporal phase gates, (4) jurisdictional compliance mapping, (5) record-status classification"],
    ["5 pillars covering confidentiality, access, temporal, jurisdictional, and record-status boundaries"],
    ["Only 2 pillars", "MGC has no formal scope framework"],
    [], [],
    "medium",
    notes="Background: Core framework"
))

new_q.append(Q(
    "How did MGC prevent further jurisdictional framework misapplications after the PDPA/PDPO incident?",
    "factual_recall",
    ["Whitfield created a jurisdictional compliance matrix mapping each office's regulations; mandatory jurisdiction-specific legal review for cross-border engagements; zero violations since implementation"],
    ["Compliance matrix plus mandatory legal reviews eliminated jurisdictional errors"],
    ["No preventive measures were taken", "The issue was ignored"],
    [], [],
    "medium",
    notes="C04: Systemic fix and its effectiveness"
))

new_q.append(Q(
    "Who managed information barriers across the most overlapping engagements in 2033?",
    "factual_recall",
    ["Priya Sharma — she led Atlas and Echo simultaneously and provided oversight for Beacon, requiring strict compartmentalization across 3 engagements"],
    ["Sharma managed barriers across 3 overlapping engagements"],
    ["No one managed multiple engagements", "Each consultant worked on only one engagement"],
    [], [],
    "medium",
    notes="Background: Multi-engagement management challenge"
))

new_q.append(Q(
    "When Project Echo was active, could MGC disclose the off-record tariff information to other clients?",
    "scope_enforcement",
    ["No; off-record information from government advisory engagements cannot be disclosed to any other party, including other MGC clients, regardless of potential benefit"],
    ["Off-record information is absolutely restricted during the engagement"],
    ["Yes, it could be shared with trusted clients", "Off-record only means not publishing it"],
    [], [],
    "hard",
    scope=True,
    notes="C05: Strictest scope boundary — government off-record"
))

new_q.append(Q(
    "What adoption rate did MGC's authority badge system achieve?",
    "factual_recall",
    ["92% compliance across offices within 6 months, with client feedback showing improved clarity about consultant authority"],
    ["92% adoption rate"],
    [],
    [], [],
    "easy",
    notes="C07: Systemic fix effectiveness"
))

new_q.append(Q(
    "What is the distinction between transferable methodology and scoped findings at MGC?",
    "scope_enforcement",
    ["MGC's Meridian Risk Matrix methodology is intellectual property applicable across engagements. Engagement-specific findings (like Meridian Bank's 30% VaR underestimation) are scoped and cannot be transferred or generalized without independent verification."],
    ["Methodology transfers; findings do not"],
    ["All findings are transferable", "Nothing from one engagement can be used in another"],
    [], [],
    "hard",
    scope=True,
    notes="C06: Core distinction that prevents improper generalization"
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

print(f"Round 5: {len(memories)} memories, {len(queries)} queries")
