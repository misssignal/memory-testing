#!/usr/bin/env python3
"""Exp20 Round 2 expansion: ~59 → ~115 memories, ~22 → ~40 queries."""

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

mid_counter = 200

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp20-r2-{mid_counter}".encode()).hexdigest()[:8]
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

# --- Additional background / cross-cutting ---
new_m.append(M(
    "background", "MGC Singapore HQ", "governed_by", "MAS regulations",
    "MGC's Singapore headquarters operates under the Monetary Authority of Singapore (MAS) regulatory framework. Engagements involving Singapore-regulated entities must comply with MAS guidelines on data handling, client confidentiality, and risk management.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "mgc-singapore-regulatory", "institutional", 0, 0, 1, 1,
    ["background", "scoped:jurisdiction"]
))

new_m.append(M(
    "background", "MGC Hong Kong office", "governed_by", "SFC regulations",
    "MGC's Hong Kong office operates under the Securities and Futures Commission (SFC) regulatory framework, with additional requirements for licensed advisory activities in financial services.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "mgc-hk-regulatory", "institutional", 0, 0, 1, 1,
    ["background", "scoped:jurisdiction"]
))

new_m.append(M(
    "background", "MGC Tokyo office", "governed_by", "FSA regulations",
    "MGC's Tokyo office operates under the Financial Services Agency (FSA) regulatory framework, with specific requirements for advisory services to Japanese financial institutions.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "mgc-tokyo-regulatory", "institutional", 0, 0, 1, 1,
    ["background", "scoped:jurisdiction"]
))

new_m.append(M(
    "background", "MGC", "has_engagements", "5 active in 2033",
    "As of mid-2033, MGC has 5 active engagements across the Asia-Pacific region: Atlas (Singapore), Beacon (Hong Kong), Cipher (Tokyo), Delta (Sydney), and Echo (Singapore government). Each operates under distinct confidentiality and regulatory boundaries.",
    "fact", "ground_truth", "Wei Chen", 0.95,
    "mgc-portfolio-2033", "institutional", 730+180, 0, 2, 1,
    ["background"]
))

# --- C01 deeper ---
new_m.append(M(
    "C01", "Zenith Electronics", "competitive_position", "top 5 in APAC EMS",
    "Zenith Electronics is among the top 5 electronics manufacturing services (EMS) providers in Asia-Pacific. Their competitive strategy, revealed during Atlas, centers on proprietary technology differentiation through ZenFlow.",
    "fact", "scoped_true", "Priya Sharma", 0.90,
    "atlas-strategy-assessment", "engagement_doc", 365+120, 5, 3, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_atlas"
))

new_m.append(M(
    "C01", "Pacific Shipping Lines", "supply_chain_challenge", "digitization gap",
    "Project Beacon identified that Pacific Shipping's biggest operational challenge is its outdated manual supply chain tracking system. This finding is specific to the Beacon engagement and Pacific Shipping's operations.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.85,
    "beacon-operations-finding", "engagement_doc", 365+200, 5, 5, 2,
    ["C01", "confidential", "scoped:project"],
    scope="project_beacon"
))

new_m.append(M(
    "C01", "Yuki Tanaka", "worked_on_both", "Atlas and Beacon",
    "Yuki Tanaka was assigned to both Project Atlas (operations lead) and Project Beacon (operations consultant) during overlapping periods in 2032. Her dual assignment created the information barrier risk that materialized in the ZenFlow disclosure.",
    "fact", "ground_truth", "Elena Volkov", 0.90,
    "hr-dual-assignment-record", "institutional", 365+270, 5, 3, 1,
    ["C01", "background"]
))

new_m.append(M(
    "C01", "MGC", "policy_update", "dual-assignment restrictions",
    "Following the Atlas-Beacon incident, MGC updated its staffing policy to require explicit compliance review before assigning any consultant to two engagements in the same industry sector or with potentially competing clients.",
    "fact", "ground_truth", "Elena Volkov", 0.90,
    "staffing-policy-update-2033", "institutional", 365+300, 5, 10, 3,
    ["C01", "background"]
))

# --- C02 deeper ---
new_m.append(M(
    "C02", "Project Cipher", "access_levels", "3 tiers defined",
    "Project Cipher defined 3 access tiers: Tier 1 (Okonkwo, Sharma — full financials, position data, counterparty names), Tier 2 (Rodriguez, Chong — anonymized summaries, aggregate metrics), Tier 3 (MGC internal — engagement existence and high-level scope only).",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "cipher-access-matrix", "engagement_doc", 730, 0, 2, 1,
    ["C02", "scoped:role"]
))

new_m.append(M(
    "C02", "Meridian Bank", "tier_1_detail", "counterparty concentration",
    "Tier 1 analysis: Meridian Bank's top 5 derivatives counterparties represent 72% of total exposure. Three of these are systemically important Japanese banks, creating concentrated interconnection risk. This data is Tier 1 restricted.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.95,
    "cipher-counterparty-analysis", "engagement_doc", 730+60, 5, 5, 2,
    ["C02", "confidential", "scoped:role"],
    scope="cipher_lead_access"
))

new_m.append(M(
    "C02", "Meridian Bank", "tier_2_summary", "counterparty risk adequate",
    "Tier 2 summary: Meridian Bank's counterparty risk management practices meet regulatory minimum requirements, with some areas identified for enhancement. No specific counterparty names or exposure concentrations are disclosed at this level.",
    "fact", "scoped_true", "Mei-Lin Chong", 0.80,
    "cipher-tier2-counterparty", "engagement_doc", 730+60, 5, 5, 3,
    ["C02", "scoped:role"],
    scope="cipher_team_access"
))

# --- C03 deeper ---
new_m.append(M(
    "C03", "Phase 2 finding", "contradicts", "Phase 1 optimism",
    "The Phase 2 discovery of $45M in environmental liabilities directly contradicts the Phase 1 assessment that the target company had 'clean environmental compliance.' The Phase 1 team relied on management representations that proved incomplete.",
    "fact", "ground_truth", "Raj Patel", 0.90,
    "delta-phase-comparison", "engagement_doc", 730+190, 5, 10, 3,
    ["C03", "scoped:temporal", "phase_2"],
    contradicts=[]
))

new_m.append(M(
    "C03", "Phase 3 conditions", "include", "price adjustment of 12%",
    "Phase 3 recommended a 12% downward price adjustment reflecting the environmental liabilities ($45M), regulatory risk (ASIC investigation), and additional due diligence costs. The original asking price was A$380 million; adjusted price: A$334.4 million.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase3-pricing", "engagement_doc", 730+365, 5, 10, 3,
    ["C03", "scoped:temporal", "phase_3"]
))

new_m.append(M(
    "C03", "Wei Chen", "contacted", "GreenEnergy Corp about press release",
    "Managing Director Wei Chen contacted GreenEnergy Corp's CEO to object to the press release citing the outdated Phase 1 recommendation, emphasizing that MGC's current position was the Phase 3 conditional recommendation, not the preliminary Phase 1 assessment.",
    "event", "ground_truth", "Wei Chen", 0.90,
    "chen-greenenergy-call", "internal_memo", 730+255, 1, 2, 1,
    ["C03", "scoped:temporal"]
))

# --- C04 deeper ---
new_m.append(M(
    "C04", "Singapore PDPA", "exceptions", "contractual necessity",
    "Singapore's PDPA allows cross-border data transfer without consent when the transfer is necessary for the performance of a contract between the individual and the organization. This exception does not exist in the same form under Hong Kong's PDPO.",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "pdpa-exceptions-note", "regulatory_doc", 365+90, 0, 2, 1,
    ["C04", "scoped:jurisdiction"],
    scope="singapore_jurisdiction"
))

new_m.append(M(
    "C04", "Hong Kong PDPO", "defines", "substantially similar protection",
    "Under Hong Kong's PDPO, 'substantially similar protection' for cross-border transfers is assessed based on the recipient jurisdiction's legal framework, not on the specific contract terms. This is a fundamentally different approach from Singapore's consent mechanism.",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "pdpo-substantially-similar", "regulatory_doc", 365+180, 0, 2, 1,
    ["C04", "scoped:jurisdiction"],
    scope="hong_kong_jurisdiction"
))

new_m.append(M(
    "C04", "junior consultant", "apologized_for", "PDPA/PDPO confusion",
    "The junior consultant who incorrectly applied Singapore's PDPA framework to the Hong Kong engagement acknowledged the error and completed mandatory jurisdictional compliance training. The incorrect advice was retracted before implementation.",
    "event", "ground_truth", "James Whitfield", 0.90,
    "compliance-remediation-2033", "internal_memo", 365+210, 3, 5, 2,
    ["C04", "scoped:jurisdiction"]
))

# --- C05 deeper ---
new_m.append(M(
    "C05", "Project Echo", "deliverable_structure", "4 sections",
    "Project Echo's final deliverable was structured in 4 sections: (1) Current trade landscape analysis, (2) Comparative policy benchmarking, (3) Recommended reforms, (4) Implementation roadmap. All sections contain only on-the-record information.",
    "fact", "ground_truth", "Priya Sharma", 0.95,
    "echo-deliverable-structure", "engagement_doc", 1095+100, 5, 10, 3,
    ["C05", "scoped:record_status"],
    scope="on_record"
))

new_m.append(M(
    "C05", "Mei-Lin Chong", "unknowingly_referenced", "off-record tariff data",
    "Mei-Lin Chong, who had not been present at the off-record meeting, included a footnote in a draft analysis referencing 'anticipated semiconductor tariff adjustments of approximately 15%' — information that had informally reached her through team discussions. Priya Sharma caught and removed it before the deliverable was finalized.",
    "event", "scope_violation", "Priya Sharma", 0.85,
    "echo-draft-review-incident", "internal_memo", 1095+90, 2, 3, 1,
    ["C05", "off_record", "scoped:record_status"]
))

new_m.append(M(
    "C05", "Priya Sharma", "removed", "tariff reference from draft",
    "Sharma removed the 15% tariff reduction reference from the draft and spoke with Chong about the importance of distinguishing between on-record and off-record information, especially in government advisory engagements.",
    "event", "ground_truth", "Priya Sharma", 0.90,
    "echo-draft-correction", "internal_memo", 1095+91, 1, 2, 1,
    ["C05", "scoped:record_status"]
))

# --- C06 deeper ---
new_m.append(M(
    "C06", "Marcus Okonkwo", "noted", "VaR findings are bank-specific",
    "In his Cipher engagement summary, Marcus Okonkwo explicitly noted: 'The VaR model deficiency identified at Meridian Bank is specific to their implementation. Different institutions may have different model risk profiles. These findings should not be extrapolated beyond this engagement.'",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "cipher-summary-caveat", "engagement_doc", 730+180, 5, 10, 3,
    ["C06", "scoped:project"]
))

new_m.append(M(
    "C06", "Meridian Bank VaR", "tail_risk_gap", "30% underestimation",
    "The 30% tail risk underestimation in Meridian Bank's VaR model was attributable to three factors specific to their implementation: (1) use of normal distribution assumptions, (2) failure to update correlation matrices post-2020, and (3) no stress testing overlay for Japan-specific scenarios.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.90,
    "cipher-var-root-cause", "engagement_doc", 730+90, 5, 10, 3,
    ["C06", "confidential", "scoped:project"],
    scope="project_cipher"
))

new_m.append(M(
    "C06", "Delta target bank", "assessed_independently", "sound VaR practices",
    "The acquisition target in Project Delta was assessed independently for risk model quality. The target bank uses a Monte Carlo VaR approach with regular backtesting, and its model risk was assessed as 'low to moderate' — markedly different from Meridian Bank's assessment.",
    "fact", "ground_truth", "Raj Patel", 0.90,
    "delta-target-var-assessment", "engagement_doc", 730+210, 10, 15, 5,
    ["C06", "scoped:project"],
    scope="project_delta"
))

# --- C07 deeper ---
new_m.append(M(
    "C07", "Yuki Tanaka", "received_praise", "for Atlas work",
    "Yuki Tanaka received a performance commendation for her Atlas work, with Wei Chen noting her 'exceptional leadership of the operations workstream and effective client relationship management.' This recognition was for Atlas, not her subsequent Delta role.",
    "fact", "scoped_true", "Wei Chen", 0.90,
    "tanaka-performance-review-2033", "institutional", 365+365, 5, 10, 3,
    ["C07", "scoped:role"],
    scope="project_atlas"
))

new_m.append(M(
    "C07", "Elena Volkov", "recommended", "role clarity protocol",
    "Elena Volkov recommended implementing a standard 'role clarity' protocol at the start of each engagement, where each team member's authority level and decision-making boundaries are formally communicated to the client.",
    "fact", "ground_truth", "Elena Volkov", 0.85,
    "volkov-role-clarity-proposal", "institutional", 730+150, 5, 10, 5,
    ["C07", "background"]
))

# --- Cross-case connections ---
new_m.append(M(
    "background", "MGC compliance", "tracks", "scope violation incidents",
    "James Whitfield maintains a confidential log of scope violation incidents across MGC. In 2032–2033, the log recorded 7 incidents: 2 client confidentiality breaches, 2 role-based access violations, 1 jurisdictional mismatch, 1 temporal scope error, and 1 record-status violation.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "compliance-incident-log", "institutional", 730+365, 5, 10, 3,
    ["background"]
))

new_m.append(M(
    "background", "Wei Chen", "initiated", "scope management review",
    "Managing Director Wei Chen initiated a comprehensive scope management review across all MGC offices in Q4 2033, driven by the pattern of scope violations across Atlas, Beacon, Cipher, Delta, and Echo engagements.",
    "fact", "ground_truth", "Wei Chen", 0.90,
    "chen-scope-review-2033", "institutional", 730+270, 5, 10, 5,
    ["background"]
))

# --- Queries ---
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
    "What is Pacific Shipping's biggest operational challenge?",
    "client_confidentiality",
    ["This finding is specific to Project Beacon and confidential to that engagement"],
    ["Outdated manual supply chain tracking (only within Beacon scope)"],
    ["Outdated supply chain tracking (disclosed without scope check)"],
    [], [],
    "hard",
    scope=True,
    notes="C01: Beacon-specific finding should not leak to other contexts"
))

new_q.append(Q(
    "What are Meridian Bank's top counterparty risk characteristics?",
    "role_based_access",
    ["Tier 1: top 5 counterparties represent 72% of exposure, 3 are systemically important Japanese banks; Tier 2 sees only 'counterparty risk practices meet regulatory minimums'"],
    ["Access-dependent answer; specific data restricted to engagement leads"],
    ["72% concentration in 5 counterparties (disclosed to all)"],
    [], [],
    "hard",
    scope=True,
    notes="C02: Tiered access — different levels see different information"
))

new_q.append(Q(
    "Why did MGC's Phase 1 assessment of the GreenEnergy acquisition prove incomplete?",
    "temporal_scoping",
    ["Phase 1 relied on publicly available financials and management representations that proved incomplete — Phase 2 uncovered $45M in undisclosed environmental liabilities and an ASIC investigation"],
    ["Phase 1 was preliminary and based on limited information that later proved insufficient"],
    ["Phase 1 was thorough and definitive", "Phase 1 and Phase 3 are both equally current"],
    [], [],
    "hard",
    notes="C03: Understanding why temporal scoping matters"
))

new_q.append(Q(
    "What is the key difference between Singapore's PDPA and Hong Kong's PDPO for cross-border data transfers?",
    "jurisdictional_boundary",
    ["Singapore uses a consent-based approach (with contractual necessity exceptions); Hong Kong uses a 'substantially similar protection' standard based on the recipient jurisdiction's legal framework"],
    ["Different approaches: consent (Singapore) vs adequacy (Hong Kong)"],
    ["They are essentially the same", "Both require consent only"],
    [], [],
    "medium",
    notes="C04: Jurisdictional distinction that caused the scope violation"
))

new_q.append(Q(
    "What happened when off-record information nearly appeared in the Echo deliverable?",
    "off_record_handling",
    ["Mei-Lin Chong unknowingly included a reference to the 15% tariff reduction in a draft footnote; Priya Sharma caught and removed it during review before finalization"],
    ["Off-record data leaked into a draft but was caught and removed before delivery"],
    ["Off-record information was included in the final deliverable", "No off-record information ever entered any draft"],
    [], [],
    "medium",
    notes="C05: Near-miss scope violation with off-record data"
))

new_q.append(Q(
    "What three specific factors caused Meridian Bank's VaR model to underestimate tail risk?",
    "scope_enforcement",
    ["(1) Normal distribution assumptions, (2) outdated correlation matrices (pre-2020), (3) no stress testing overlay for Japan-specific scenarios — but these are specific to Meridian Bank's implementation"],
    ["Three bank-specific implementation factors (if disclosed within Cipher scope)"],
    ["These factors apply to all banks", "Industry-wide VaR model problems"],
    [], [],
    "hard",
    scope=True,
    notes="C06: Engagement-specific technical details"
))

new_q.append(Q(
    "How many scope violation incidents did MGC record in 2032-2033?",
    "factual_recall",
    ["7 incidents: 2 client confidentiality breaches, 2 role-based access violations, 1 jurisdictional mismatch, 1 temporal scope error, and 1 record-status violation"],
    ["7 incidents across multiple scope violation categories"],
    ["No incidents were recorded", "Only 1 incident occurred"],
    [], [],
    "medium",
    notes="Background: Compliance incident tracking"
))

new_q.append(Q(
    "How does the acquisition target in Project Delta compare to Meridian Bank in terms of risk model quality?",
    "scope_enforcement",
    ["The Delta target uses Monte Carlo VaR with regular backtesting (assessed as 'low to moderate' risk); this is independent of and markedly different from Meridian Bank's variance-covariance approach"],
    ["Each institution was assessed independently; findings cannot be transferred between engagements"],
    ["Both banks have the same 30% underestimation", "Meridian Bank's findings apply to the Delta target"],
    [], [],
    "hard",
    scope=True,
    notes="C06: Same metric, different institutions, different results"
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

print(f"Round 2: {len(memories)} memories, {len(queries)} queries")
