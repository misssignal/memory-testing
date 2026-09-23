#!/usr/bin/env python3
"""Exp20 Round 1 expansion: 30 → ~85 memories, 10 → ~24 queries."""

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

mid_counter = len(memories) + 1

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp20-r1-{mid_counter}".encode()).hexdigest()[:8]
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

# --- More background ---
new_m.append(M(
    "background", "Mei-Lin Chong", "role", "Associate, Data Analytics",
    "Mei-Lin Chong is an Associate in MGC's Data Analytics practice, supporting engagement teams with quantitative analysis, data visualization, and statistical modeling.",
    "fact", "ground_truth", "MGC_system", 0.95,
    "MGC-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_m.append(M(
    "background", "Raj Patel", "role", "Partner, M&A Advisory",
    "Raj Patel is Partner in MGC's M&A Advisory practice, leading due diligence engagements and advising clients on acquisition strategy, valuation, and post-merger integration across Asia-Pacific.",
    "fact", "ground_truth", "MGC_system", 0.95,
    "MGC-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_m.append(M(
    "background", "Elena Volkov", "role", "Director, Human Capital",
    "Elena Volkov is Director of MGC's Human Capital practice, managing organizational design, talent strategy, and change management engagements.",
    "fact", "ground_truth", "MGC_system", 0.95,
    "MGC-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_m.append(M(
    "background", "Tomás Gutierrez", "role", "Manager, Regional Operations",
    "Tomás Gutierrez manages MGC's regional operations from the Jakarta office, coordinating cross-border engagements and serving as the primary liaison for Southeast Asian clients outside Singapore.",
    "fact", "ground_truth", "MGC_system", 0.95,
    "MGC-HR", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_m.append(M(
    "background", "MGC", "has_policy", "information barriers",
    "MGC maintains formal information barriers ('Chinese walls') between client engagements. Consultants working on competing or related engagements must not share client-specific information across engagement boundaries.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "MGC-compliance-manual", "institutional", 0, 0, 1, 1,
    ["background"]
))

new_m.append(M(
    "background", "MGC", "has_policy", "role-based access control",
    "MGC's engagement data is classified into access tiers: Tier 1 (engagement lead and partner only), Tier 2 (full engagement team), Tier 3 (MGC internal, non-client-specific). Client financials and strategic plans are typically Tier 1.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "MGC-data-policy", "institutional", 0, 0, 1, 1,
    ["background"]
))

# --- C01 additional ---
new_m.append(M(
    "C01", "Project Atlas", "team_includes", "Tanaka, Rodriguez, Chong",
    "Project Atlas core team: Priya Sharma (engagement lead), Yuki Tanaka (operations lead), Sofia Rodriguez (digital specialist), Mei-Lin Chong (analytics support). All signed Atlas-specific NDAs.",
    "fact", "ground_truth", "Priya Sharma", 0.95,
    "atlas-team-roster-full", "engagement_doc", 365+59, 0, 1, 1,
    ["C01", "scoped:project"],
    scope="project_atlas"
))

new_m.append(M(
    "C01", "Zenith Electronics", "revenue", "$3.8 billion FY2032",
    "Zenith Electronics reported revenue of $3.8 billion for FY2032, with 62% from contract manufacturing and 38% from proprietary products. This financial data is confidential to Project Atlas.",
    "fact", "scoped_true", "Priya Sharma", 0.90,
    "atlas-client-financials", "engagement_doc", 365+90, 5, 2, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_atlas"
))

new_m.append(M(
    "C01", "James Whitfield", "issued", "compliance reminder after leak",
    "Following the inadvertent ZenFlow mention in Beacon, James Whitfield issued a firm-wide compliance reminder about information barrier obligations, noting that 'engagement-specific information must never be referenced in other client contexts, even indirectly.'",
    "event", "ground_truth", "James Whitfield", 0.95,
    "compliance-bulletin-2032-11", "internal_memo", 365+280, 2, 3, 1,
    ["C01", "background"]
))

new_m.append(M(
    "C01", "Pacific Shipping Lines", "annual_revenue", "$2.1 billion",
    "Pacific Shipping Lines reported annual revenue of $2.1 billion in FY2032, operating a fleet of 45 container vessels and 12 bulk carriers across Intra-Asia and Asia-Europe routes. This data is confidential to Project Beacon.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.90,
    "beacon-client-profile", "engagement_doc", 365+151, 5, 2, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_beacon"
))

# --- C02 additional ---
new_m.append(M(
    "C02", "Meridian Bank", "tier_1_detail", "concentrated yen positions",
    "Tier 1 analysis (engagement leads only): Meridian Bank holds concentrated positions in USD/JPY options representing 40% of their total derivatives book. This concentration creates significant event risk around Bank of Japan policy decisions.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.95,
    "cipher-tier1-analysis", "engagement_doc", 730+45, 5, 5, 2,
    ["C02", "confidential", "scoped:role"],
    scope="cipher_lead_access"
))

new_m.append(M(
    "C02", "Meridian Bank", "tier_2_summary", "FX risk within limits",
    "Tier 2 summary (full team): Meridian Bank's foreign exchange risk metrics are within regulatory limits, though the team has noted areas for model enhancement. Specific position data is not included at this access level.",
    "fact", "scoped_true", "Sofia Rodriguez", 0.80,
    "cipher-tier2-fx-summary", "engagement_doc", 730+45, 5, 5, 3,
    ["C02", "scoped:role"],
    scope="cipher_team_access"
))

new_m.append(M(
    "C02", "Sofia Rodriguez", "accessed", "Tier 1 data accidentally",
    "Sofia Rodriguez inadvertently accessed Tier 1 financial data for Project Cipher when a shared drive permission was misconfigured. She reported the access to James Whitfield, who noted it as a data handling incident.",
    "event", "scope_violation", "James Whitfield", 0.85,
    "cipher-access-incident", "internal_memo", 730+60, 2, 3, 1,
    ["C02", "scoped:role"]
))

# --- C03 additional ---
new_m.append(M(
    "C03", "Delta Phase 1", "based_on", "preliminary financials only",
    "The Phase 1 'proceed' recommendation was based solely on publicly available financials and management presentations. It explicitly stated: 'This preliminary assessment is subject to revision pending full due diligence.'",
    "fact", "scoped_true", "Raj Patel", 0.85,
    "delta-phase1-caveat", "engagement_doc", 730+30, 5, 10, 3,
    ["C03", "scoped:temporal", "phase_1"],
    scope="delta_phase_1"
))

new_m.append(M(
    "C03", "GreenEnergy Corp target", "environmental_liabilities", "$45 million",
    "Phase 2 due diligence uncovered $45 million in undisclosed environmental liabilities at the acquisition target's manufacturing sites: $28M for soil remediation at the Broken Hill site and $17M for groundwater contamination at Port Augusta.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase2-environmental", "engagement_doc", 730+180, 10, 15, 5,
    ["C03", "scoped:temporal", "phase_2"]
))

new_m.append(M(
    "C03", "ASIC", "investigating", "acquisition target",
    "The Australian Securities and Investments Commission (ASIC) had opened an investigation into the acquisition target's disclosure practices regarding environmental liabilities. This was discovered during Phase 2 regulatory due diligence.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "delta-phase2-regulatory", "engagement_doc", 730+190, 5, 10, 3,
    ["C03", "scoped:temporal", "phase_2"]
))

new_m.append(M(
    "C03", "GreenEnergy Corp board", "cited", "Phase 1 recommendation to proceed",
    "GreenEnergy Corp's board cited MGC's Phase 1 'proceed' recommendation in a press release, without acknowledging that the recommendation had been superseded by Phase 2 findings and Phase 3 conditions. This created a misleading impression.",
    "event", "scope_violation", "Wei Chen", 0.85,
    "wei-chen-concern-memo", "internal_memo", 730+250, 3, 5, 2,
    ["C03", "scoped:temporal"]
))

# --- C04 additional ---
new_m.append(M(
    "C04", "Japanese APPI", "requires", "consent plus adequacy",
    "Japan's Act on Protection of Personal Information (APPI) requires both individual consent and confirmation that the recipient country provides adequate data protection standards. This represents a third distinct approach from Singapore (consent-based) and Hong Kong (adequacy-based).",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "appi-advisory-cipher", "regulatory_doc", 730+90, 0, 2, 1,
    ["C04", "scoped:jurisdiction"],
    scope="japan_jurisdiction"
))

new_m.append(M(
    "C04", "Australian Privacy Act", "requires", "APP 8 cross-border disclosure",
    "Australia's Privacy Act requires compliance with Australian Privacy Principle 8 (APP 8) for cross-border disclosure of personal information, including reasonable steps to ensure the overseas recipient handles data in accordance with the APPs.",
    "fact", "scoped_true", "James Whitfield", 0.95,
    "privacy-act-advisory-delta", "regulatory_doc", 730+90, 0, 2, 1,
    ["C04", "scoped:jurisdiction"],
    scope="australia_jurisdiction"
))

new_m.append(M(
    "C04", "MGC", "created", "jurisdictional compliance matrix",
    "Following the PDPA/PDPO mix-up on Beacon, James Whitfield created a jurisdictional compliance matrix mapping each MGC office's applicable data privacy regulations, ensuring consultants use the correct framework for each engagement's jurisdiction.",
    "fact", "ground_truth", "James Whitfield", 0.95,
    "compliance-matrix-2033", "institutional", 365+250, 5, 10, 3,
    ["C04", "background"]
))

# --- C05 additional ---
new_m.append(M(
    "C05", "Ministry official", "confirmed_on_record", "regulatory review timeline",
    "On the record, the Ministry official confirmed that the regulatory review would be completed by Q3 2034, with public consultation beginning in Q2. This timeline information is part of the official engagement record.",
    "fact", "ground_truth", "Wei Chen", 0.95,
    "echo-meeting-minutes-official", "engagement_doc", 1095+30, 0, 2, 1,
    ["C05", "scoped:record_status"],
    scope="on_record"
))

new_m.append(M(
    "C05", "Ministry official", "shared_off_record", "political dynamics",
    "Off the record, the Ministry official mentioned that the tariff reduction was politically contentious within the cabinet, with the Finance Ministry opposing it and the Trade Ministry pushing for it. This political context was explicitly not for deliverables.",
    "fact", "scoped_true", "Priya Sharma", 0.80,
    "sharma-personal-notes-2", "personal_notes", 1095+45, 0, 1, 1,
    ["C05", "off_record", "scoped:record_status"],
    scope="off_record"
))

new_m.append(M(
    "C05", "Priya Sharma", "briefed", "Wei Chen on off-record context",
    "Priya Sharma verbally briefed Wei Chen on the off-record political dynamics, noting that this context should inform MGC's approach but must not appear in any written deliverable or be communicated to other clients.",
    "event", "ground_truth", "Wei Chen", 0.85,
    "chen-briefing-notes", "personal_notes", 1095+46, 0, 1, 1,
    ["C05", "off_record", "scoped:record_status"],
    scope="off_record"
))

# --- C06 additional ---
new_m.append(M(
    "C06", "Meridian Bank VaR model", "uses", "variance-covariance methodology",
    "Meridian Bank's VaR model uses a parametric variance-covariance approach with a 99% confidence interval and 10-day holding period. The model was last validated externally in 2030 and does not incorporate recent advances in tail risk modeling.",
    "fact", "scoped_true", "Marcus Okonkwo", 0.90,
    "cipher-var-analysis", "engagement_doc", 730+60, 5, 10, 3,
    ["C06", "confidential", "scoped:project"],
    scope="project_cipher"
))

new_m.append(M(
    "C06", "industry VaR practices", "generally", "evolving toward Monte Carlo",
    "The banking industry is generally moving from parametric VaR to Monte Carlo simulation and historical simulation approaches. However, the degree of model risk varies significantly by institution, and a 30% underestimation found at one bank cannot be extrapolated to the industry.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.90,
    "okonkwo-industry-note", "internal_memo", 730+90, 5, 5, 2,
    ["C06", "background"]
))

new_m.append(M(
    "C06", "Raj Patel", "corrected", "the 30% generalization",
    "In the Project Delta meeting, Raj Patel corrected the improper generalization, noting: 'The 30% figure is from a specific engagement and cannot be applied broadly. For Delta's purposes, we need to assess the target's own risk models independently.'",
    "event", "ground_truth", "Raj Patel", 0.90,
    "delta-meeting-correction", "engagement_doc", 730+200, 2, 3, 1,
    ["C06", "scoped:project"]
))

# --- C07 additional ---
new_m.append(M(
    "C07", "Yuki Tanaka Atlas", "managed", "team of 8 consultants",
    "On Project Atlas, Yuki Tanaka directly managed 8 junior consultants, led weekly client steering committee meetings, and had sign-off authority on all operational recommendations up to $500,000 in implementation scope.",
    "fact", "scoped_true", "Priya Sharma", 0.95,
    "atlas-authority-matrix", "engagement_doc", 365+59, 0, 1, 1,
    ["C07", "scoped:role"],
    scope="project_atlas"
))

new_m.append(M(
    "C07", "Yuki Tanaka Delta", "reports_to", "Raj Patel",
    "On Project Delta, Yuki Tanaka reports to Raj Patel and has no independent client-facing authority. Her deliverables must be reviewed and approved by Patel before submission to GreenEnergy Corp.",
    "fact", "scoped_true", "Raj Patel", 0.95,
    "delta-authority-matrix", "engagement_doc", 730+30, 0, 1, 1,
    ["C07", "scoped:role"],
    scope="project_delta"
))

new_m.append(M(
    "C07", "Raj Patel", "issued", "clarification to GreenEnergy Corp",
    "Following the authority confusion, Raj Patel issued a formal clarification to GreenEnergy Corp's management, stating that all MGC recommendations on Project Delta must come through him as engagement partner, and that individual consultant opinions do not represent MGC's official position.",
    "event", "ground_truth", "Raj Patel", 0.90,
    "delta-authority-clarification", "engagement_doc", 730+125, 2, 3, 1,
    ["C07", "scoped:role"]
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
    "What is Zenith Electronics' annual revenue?",
    "client_confidentiality",
    ["$3.8 billion FY2032 — but this is Atlas-confidential data and should not be disclosed outside the engagement"],
    ["This information is confidential to Project Atlas"],
    ["$3.8 billion (disclosed without scope restriction)"],
    [], [],
    "hard",
    scope=True,
    notes="C01: Client financial data scoped to Atlas engagement"
))

new_q.append(Q(
    "What specific positions does Meridian Bank hold in its derivatives portfolio?",
    "role_based_access",
    ["Tier 1 only: concentrated USD/JPY options representing 40% of derivatives book; Tier 2 sees only 'FX risk within limits'"],
    ["Answer depends on access tier; detailed positions are restricted"],
    ["Concentrated yen positions (disclosed to all)", "40% in USD/JPY (without access check)"],
    [], [],
    "hard",
    scope=True,
    notes="C02: Tiered access — different answers for different roles"
))

new_q.append(Q(
    "What was the basis for MGC's initial recommendation to proceed with the GreenEnergy acquisition?",
    "temporal_scoping",
    ["Phase 1 was based on preliminary financials and management presentations only, with an explicit caveat that it was subject to revision pending full due diligence"],
    ["Initial recommendation was preliminary, later superseded by Phase 2 and 3 findings"],
    ["MGC recommended proceeding based on thorough analysis", "The proceed recommendation was MGC's final position"],
    [], [],
    "hard",
    scope=True,
    notes="C03: Phase 1 had explicit caveat about being preliminary"
))

new_q.append(Q(
    "What data privacy framework applies to MGC's Tokyo engagement?",
    "jurisdictional_boundary",
    ["Japan's APPI, which requires both individual consent AND confirmation of adequate protection in the recipient country"],
    ["APPI governs; it differs from both Singapore's PDPA and Hong Kong's PDPO"],
    ["Singapore PDPA applies", "Hong Kong PDPO applies", "All Asia-Pacific offices use the same framework"],
    [], [],
    "medium",
    scope=True,
    notes="C04: Each jurisdiction has distinct requirements"
))

new_q.append(Q(
    "What are the political dynamics around the Singapore tariff reduction?",
    "off_record_handling",
    ["This information was shared off-the-record and should not be disclosed or included in any deliverable"],
    ["Off-record political context cannot be shared"],
    ["Finance Ministry opposes it, Trade Ministry supports it (disclosed as fact)"],
    [], [],
    "hard",
    scope=True,
    abstain=True,
    notes="C05: Off-record political context must not be disclosed"
))

new_q.append(Q(
    "Is the variance-covariance VaR methodology generally outdated for derivatives risk?",
    "scope_enforcement",
    ["The industry is evolving toward Monte Carlo and historical simulation, but Meridian Bank's specific 30% underestimation finding cannot be generalized; each institution's model risk must be assessed independently"],
    ["Parametric VaR is being replaced by newer methods, but degree of risk varies by institution"],
    ["Yes, all banks using variance-covariance underestimate by 30%", "Meridian Bank's finding applies industry-wide"],
    [], [],
    "hard",
    scope=True,
    notes="C06: Industry trend is real but specific quantification is engagement-specific"
))

new_q.append(Q(
    "Who has sign-off authority for MGC recommendations on Project Delta?",
    "role_based_access",
    ["Raj Patel as engagement partner; all recommendations must go through him"],
    ["Patel has sole authority; Tanaka and other team members cannot independently represent MGC's position"],
    ["Yuki Tanaka has sign-off authority", "Any senior consultant can sign off"],
    [], [],
    "medium",
    scope=True,
    notes="C07: Authority is engagement-specific, not portable"
))

new_q.append(Q(
    "What compliance action did MGC take after the Atlas-Beacon information leak?",
    "factual_recall",
    ["James Whitfield issued a firm-wide compliance reminder about information barrier obligations"],
    ["Compliance bulletin reinforcing Chinese walls between engagements"],
    ["No action was taken", "The consultant was fired"],
    [], [],
    "easy",
    notes="C01: Post-incident response"
))

new_q.append(Q(
    "Can information from Project Atlas be used to benefit Project Beacon?",
    "scope_enforcement",
    ["No; MGC maintains formal information barriers between engagements. Atlas-specific information must not be shared with or applied to Beacon, even indirectly."],
    ["Information barriers prohibit cross-engagement transfer"],
    ["Yes, MGC shares best practices across all engagements", "Client data can be used for any MGC project"],
    [], [],
    "hard",
    scope=True,
    notes="C01: Core information barrier test"
))

new_q.append(Q(
    "What incident occurred with Sofia Rodriguez's data access on Project Cipher?",
    "factual_recall",
    ["She inadvertently accessed Tier 1 financial data due to a shared drive permission misconfiguration, and reported it to Whitfield"],
    ["Accidental access to restricted data due to misconfigured permissions"],
    ["She intentionally accessed restricted data", "No data access incident occurred"],
    [], [],
    "easy",
    notes="C02: Access control incident"
))

new_q.append(Q(
    "Did GreenEnergy Corp accurately represent MGC's recommendation?",
    "temporal_scoping",
    ["No; GreenEnergy Corp cited the Phase 1 'proceed' recommendation in a press release without acknowledging it had been superseded by Phase 2 findings and Phase 3 conditions"],
    ["The board misrepresented MGC's recommendation by citing an outdated phase"],
    ["Yes, MGC recommended proceeding", "The press release was accurate"],
    [], [],
    "hard",
    scope=True,
    notes="C03: Temporal scope violation by the client"
))

new_q.append(Q(
    "How many distinct data privacy frameworks must MGC navigate across its offices?",
    "jurisdictional_boundary",
    ["At least 4 distinct frameworks: Singapore PDPA, Hong Kong PDPO, Japan APPI, Australia Privacy Act (APP 8)"],
    ["4+ frameworks with different approaches to cross-border data transfer"],
    ["One unified Asia-Pacific framework", "All offices follow Singapore PDPA"],
    [], [],
    "medium",
    notes="C04: Jurisdictional diversity"
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

print(f"Round 1: {len(memories)} memories, {len(queries)} queries")
