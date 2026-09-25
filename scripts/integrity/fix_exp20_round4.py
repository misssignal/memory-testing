#!/usr/bin/env python3
"""Exp20 Round 4 expansion: ~112 → ~170 memories, ~41 → ~58 queries."""

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

mid_counter = 600

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp20-r4-{mid_counter}".encode()).hexdigest()[:8]
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

# --- C01 final expansion ---
new_m.append(M(
    "C01", "Zenith Electronics", "market_share", "14% of APAC EMS",
    "Zenith Electronics holds approximately 14% market share in the Asia-Pacific EMS market. This competitive positioning data was part of Atlas's strategic analysis and is confidential.",
    "fact", "scoped_true", "Priya Sharma", 0.90,
    "atlas-market-analysis", "engagement_doc", 365+120, 5, 3, 1,
    ["C01", "confidential", "scoped:project"],
    scope="project_atlas"
))

new_m.append(M(
    "C01", "Beacon recommendation", "included", "technology vendor evaluation",
    "Project Beacon's deliverable included a recommendation for Pacific Shipping to evaluate AI logistics vendors. The recommendation was carefully worded to avoid any reference to specific platforms, including ZenFlow, which MGC knew about from Atlas.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.90,
    "beacon-tech-recommendation", "engagement_doc", 365+280, 10, 15, 5,
    ["C01", "scoped:project"]
))

new_m.append(M(
    "C01", "information barrier", "verified_by", "compliance audit",
    "MGC's quarterly compliance audit confirmed that no Atlas-specific information appeared in any Beacon deliverable or working paper. The ZenFlow mention in the meeting was verbal and was not documented in Beacon records.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "compliance-audit-2033-Q1", "institutional", 365+300, 10, 15, 5,
    ["C01"]
))

# --- C02 final expansion ---
new_m.append(M(
    "C02", "Cipher engagement", "final_report", "36 recommendations",
    "Project Cipher's final report contained 36 recommendations for Meridian Bank, organized by risk category. The full report (Tier 1) includes specific position recommendations; the executive summary (Tier 2) presents aggregate improvement priorities.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "cipher-final-report", "engagement_doc", 730+300, 10, 15, 5,
    ["C02", "scoped:role"]
))

new_m.append(M(
    "C02", "Meridian Bank CEO", "received", "Tier 1 report only",
    "Meridian Bank's CEO received the full Tier 1 report. MGC ensured that no copies of the Tier 1 report were retained in systems accessible to Tier 2 team members after the engagement concluded.",
    "fact", "ground_truth", "Marcus Okonkwo", 0.95,
    "cipher-report-distribution", "engagement_doc", 730+310, 5, 10, 3,
    ["C02", "scoped:role"]
))

new_m.append(M(
    "C02", "shared drive", "permissions_fixed", "after Rodriguez incident",
    "Following Sofia Rodriguez's accidental Tier 1 data access, MGC IT implemented mandatory quarterly access permission audits for all engagement shared drives and introduced automated access-level tagging for all uploaded documents.",
    "fact", "ground_truth", "James Whitfield", 0.90,
    "it-access-remediation", "institutional", 730+65, 5, 10, 3,
    ["C02", "background"]
))

# --- C03 final expansion ---
new_m.append(M(
    "C03", "Delta acquisition target", "name", "SolarVista Energy",
    "The acquisition target in Project Delta is SolarVista Energy Pty Ltd, an Australian renewable energy company with solar and wind assets across New South Wales and South Australia. Revenue: A$95 million (FY2032).",
    "fact", "scoped_true", "Raj Patel", 0.90,
    "delta-target-profile", "engagement_doc", 730+30, 5, 10, 3,
    ["C03", "confidential", "scoped:project"],
    scope="project_delta"
))

new_m.append(M(
    "C03", "Phase 2 team", "included", "environmental specialist",
    "Phase 2 of Project Delta brought in an environmental due diligence specialist who discovered the $45M liabilities through site inspections and regulatory record reviews — work that was explicitly excluded from Phase 1 scope.",
    "fact", "ground_truth", "Raj Patel", 0.95,
    "delta-phase2-specialist", "engagement_doc", 730+180, 5, 10, 3,
    ["C03", "scoped:temporal", "phase_2"]
))

new_m.append(M(
    "C03", "SolarVista", "Broken Hill site", "$28M remediation needed",
    "SolarVista's Broken Hill manufacturing site requires $28 million in soil remediation due to historical use of cadmium telluride in solar panel production. This liability was not disclosed in SolarVista's financial statements.",
    "fact", "ground_truth", "environmental specialist", 0.95,
    "delta-broken-hill-assessment", "engagement_doc", 730+190, 10, 15, 5,
    ["C03", "scoped:temporal", "phase_2"]
))

new_m.append(M(
    "C03", "SolarVista", "Port Augusta site", "$17M groundwater contamination",
    "SolarVista's Port Augusta wind farm site has $17 million in groundwater contamination remediation costs from improper disposal of transformer oils during the site's development in 2025-2027.",
    "fact", "ground_truth", "environmental specialist", 0.95,
    "delta-port-augusta-assessment", "engagement_doc", 730+195, 10, 15, 5,
    ["C03", "scoped:temporal", "phase_2"]
))

# --- C04 final expansion ---
new_m.append(M(
    "C04", "Atlas data privacy", "compliant_with", "Singapore PDPA",
    "Project Atlas's data handling procedures for Zenith Electronics were designed to comply with Singapore's PDPA, including consent management for employee data and contractual protections for cross-border vendor data sharing.",
    "fact", "scoped_true", "James Whitfield", 0.90,
    "atlas-pdpa-compliance", "engagement_doc", 365+120, 5, 10, 3,
    ["C04", "scoped:jurisdiction"],
    scope="singapore_jurisdiction"
))

new_m.append(M(
    "C04", "Cipher data privacy", "compliant_with", "Japan APPI",
    "Project Cipher's data handling procedures for Meridian Bank were designed to comply with Japan's APPI, including dual requirements of individual consent and adequacy assessment for any cross-border data flows.",
    "fact", "scoped_true", "James Whitfield", 0.90,
    "cipher-appi-compliance", "engagement_doc", 730+30, 5, 10, 3,
    ["C04", "scoped:jurisdiction"],
    scope="japan_jurisdiction"
))

new_m.append(M(
    "C04", "Delta data privacy", "compliant_with", "Australian Privacy Act",
    "Project Delta's due diligence data handling complied with Australia's Privacy Act APP 8, including documented 'reasonable steps' to ensure overseas recipients (MGC Singapore) handled personal data consistently with Australian Privacy Principles.",
    "fact", "scoped_true", "James Whitfield", 0.90,
    "delta-app8-compliance", "engagement_doc", 730+60, 5, 10, 3,
    ["C04", "scoped:jurisdiction"],
    scope="australia_jurisdiction"
))

# --- C05 final expansion ---
new_m.append(M(
    "C05", "Echo engagement", "staff", "3 consultants",
    "Project Echo was staffed with 3 consultants: Priya Sharma (engagement lead), Wei Chen (partner oversight, given government client sensitivity), and Sofia Rodriguez (policy analysis). Only Sharma and Chen attended off-record meetings.",
    "fact", "ground_truth", "Wei Chen", 0.95,
    "echo-staffing", "engagement_doc", 1095, 0, 2, 1,
    ["C05", "scoped:project"]
))

new_m.append(M(
    "C05", "Echo off-record meetings", "protocol", "no notes distributed",
    "For off-record meetings with Ministry officials, MGC protocol required: no written notes distributed, no audio recording, no email follow-up referencing off-record content. Sharma maintained personal handwritten notes in a locked file for her own reference only.",
    "fact", "ground_truth", "Priya Sharma", 0.95,
    "echo-off-record-protocol", "institutional", 1095+10, 0, 2, 1,
    ["C05", "off_record", "scoped:record_status"]
))

new_m.append(M(
    "C05", "Ministry official", "shared_on_record", "Singapore trade data",
    "On the record, the Ministry shared trade flow data showing Singapore's semiconductor imports grew 22% in 2033, with 60% sourced from Taiwan and South Korea. This data appeared in MGC's deliverable analysis.",
    "fact", "ground_truth", "Ministry of Trade", 0.95,
    "echo-trade-data-official", "engagement_doc", 1095+40, 0, 5, 2,
    ["C05", "scoped:record_status"],
    scope="on_record"
))

# --- C06 final expansion ---
new_m.append(M(
    "C06", "consultant who generalized", "was", "junior from Cipher team",
    "The consultant who generalized the Meridian Bank VaR finding in the Delta meeting was a junior analyst who had worked on both Cipher and Delta. The analyst did not intend to breach confidentiality but failed to distinguish between engagement-specific findings and general industry knowledge.",
    "event", "ground_truth", "Marcus Okonkwo", 0.85,
    "okonkwo-incident-review", "internal_memo", 730+205, 3, 5, 2,
    ["C06"]
))

new_m.append(M(
    "C06", "Marcus Okonkwo", "conducted", "remedial training session",
    "Okonkwo conducted a remedial training session for the analyst, emphasizing the distinction between transferable methodology and scoped findings, and the potential legal and reputational consequences of improper generalization.",
    "event", "ground_truth", "Marcus Okonkwo", 0.90,
    "okonkwo-remedial-training", "institutional", 730+210, 2, 3, 1,
    ["C06"]
))

# --- C07 final expansion ---
new_m.append(M(
    "C07", "GreenEnergy Corp CEO", "apologized_for", "assumption about Tanaka",
    "GreenEnergy Corp's CEO acknowledged that their team should have verified Tanaka's authority level rather than assuming it based on her title and Atlas reputation. The A$200,000 in implementation costs were ultimately absorbed by GreenEnergy as their own decision.",
    "event", "ground_truth", "Wei Chen", 0.85,
    "greenenergy-acknowledgment", "internal_memo", 730+140, 5, 10, 3,
    ["C07", "scoped:role"]
))

new_m.append(M(
    "C07", "MGC", "implemented", "authority badges for client meetings",
    "MGC implemented a visual authority-level indicator system: consultants with decision-making authority wear gold engagement badges at client meetings; support staff wear silver. This was Elena Volkov's role clarity protocol in action.",
    "fact", "ground_truth", "Elena Volkov", 0.85,
    "authority-badge-system", "institutional", 730+180, 5, 15, 5,
    ["C07", "background"]
))

# --- Additional cross-case memories ---
new_m.append(M(
    "background", "MGC", "2033_revenue", "$245 million",
    "MGC's Asia-Pacific operations generated revenue of $245 million in FY2033, with the strategy practice contributing 35% and financial advisory 28%.",
    "fact", "ground_truth", "Wei Chen", 0.90,
    "mgc-financials-2033", "institutional", 730+365, 5, 15, 5,
    ["background"]
))

new_m.append(M(
    "background", "MGC", "employs", "340 consultants across APAC",
    "MGC employs 340 consultants across its 5 Asia-Pacific offices: Singapore (120), Hong Kong (75), Tokyo (60), Sydney (55), Jakarta (30).",
    "fact", "ground_truth", "Elena Volkov", 0.95,
    "mgc-headcount-2033", "institutional", 730+180, 0, 5, 2,
    ["background"]
))

new_m.append(M(
    "background", "MGC client", "engagement_types", "4 practice areas",
    "MGC organizes engagements across 4 practice areas: Strategy (led by Sharma), Financial Advisory (led by Okonkwo), Risk & Compliance (led by Whitfield), and Human Capital (led by Volkov). Digital Transformation and Operations are sub-practices.",
    "fact", "ground_truth", "MGC_system", 0.95,
    "mgc-practice-structure", "institutional", 0, 0, 1, 1,
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
    "What did MGC's compliance audit find regarding the Atlas-Beacon information barrier?",
    "client_confidentiality",
    ["The audit confirmed no Atlas-specific information appeared in any Beacon deliverable. The ZenFlow mention was verbal and was not documented in Beacon records."],
    ["Compliance audit verified the barrier was maintained in written records"],
    ["Atlas information leaked into Beacon deliverables", "The barrier was breached in writing"],
    [], [],
    "medium",
    notes="C01: Compliance verification"
))

new_q.append(Q(
    "How many recommendations did Project Cipher produce for Meridian Bank?",
    "factual_recall",
    ["36 recommendations organized by risk category"],
    ["36 recommendations in the final report"],
    [],
    [], [],
    "easy",
    notes="C02: Basic fact retrieval"
))

new_q.append(Q(
    "What is the name of the acquisition target in Project Delta?",
    "client_confidentiality",
    ["SolarVista Energy Pty Ltd — but this is Delta-confidential information"],
    ["SolarVista Energy (within Delta scope only)"],
    ["SolarVista Energy (disclosed without scope restriction)"],
    [], [],
    "hard",
    scope=True,
    notes="C03: Client name is scoped to engagement"
))

new_q.append(Q(
    "What specific environmental issues exist at SolarVista's two sites?",
    "temporal_scoping",
    ["Broken Hill: $28M soil remediation (cadmium telluride from solar panel production); Port Augusta: $17M groundwater contamination (transformer oil disposal in 2025-2027)"],
    ["Two environmental liabilities totaling $45M discovered in Phase 2"],
    [],
    [], [],
    "medium",
    notes="C03: Phase 2 specific findings"
))

new_q.append(Q(
    "What semiconductor import data did the Ministry share on the record?",
    "off_record_handling",
    ["Singapore's semiconductor imports grew 22% in 2033, with 60% sourced from Taiwan and South Korea — this was on-record data included in MGC's deliverable"],
    ["22% growth, Taiwan and South Korea as primary sources (public data)"],
    ["15% tariff reduction plans", "Cabinet dynamics about tariff policy"],
    [], [],
    "medium",
    scope=True,
    notes="C05: On-record vs off-record distinction"
))

new_q.append(Q(
    "What remedial action was taken after the VaR finding was improperly generalized?",
    "factual_recall",
    ["Okonkwo conducted a remedial training session for the junior analyst, and Patel corrected the generalization in the Delta meeting"],
    ["Training on methodology vs findings distinction, and in-meeting correction"],
    ["No action was taken", "The analyst was fired"],
    [], [],
    "easy",
    notes="C06: Post-incident remediation"
))

new_q.append(Q(
    "What protocol did MGC implement to prevent role confusion at client meetings?",
    "factual_recall",
    ["A visual authority-level badge system: gold badges for decision-making authority, silver for support staff"],
    ["Authority badges per Elena Volkov's role clarity protocol"],
    ["No protocol was implemented", "MGC banned consultants from attending multiple engagements"],
    [], [],
    "easy",
    notes="C07: Systemic fix for role confusion"
))

new_q.append(Q(
    "Who absorbed the A$200,000 implementation cost from Tanaka's informal Delta recommendations?",
    "status_tracking",
    ["GreenEnergy Corp absorbed the costs as their own decision, after acknowledging they should have verified Tanaka's authority"],
    ["GreenEnergy accepted the costs; acknowledged assumption error"],
    ["MGC paid the costs", "The costs were shared equally"],
    [], [],
    "medium",
    notes="C07: Resolution of the scope violation consequence"
))

new_q.append(Q(
    "How many consultants does MGC employ across Asia-Pacific?",
    "factual_recall",
    ["340 consultants: Singapore (120), Hong Kong (75), Tokyo (60), Sydney (55), Jakarta (30)"],
    ["340 across 5 offices"],
    [],
    [], [],
    "easy",
    notes="Background: basic org fact"
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

print(f"Round 4: {len(memories)} memories, {len(queries)} queries")
