#!/usr/bin/env python3
"""Exp18 Round 5 expansion: 182 → 206+ memories, 63 → 76+ queries."""

import json, hashlib, os, sys
from datetime import datetime, timedelta, timezone

d = sys.argv[1] if len(sys.argv) > 1 else "experiment_18_counterfactual_negative"

with open(os.path.join(d, "memories.jsonl")) as f:
    memories = [json.loads(l) for l in f if l.strip()]
with open(os.path.join(d, "queries.jsonl")) as f:
    queries = [json.loads(l) for l in f if l.strip()]

UTC = timezone.utc
T0 = datetime(2029, 3, 1, tzinfo=UTC)

def ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

mid_counter = 800

def M(story, subj, pred, obj, text, etype, truth_role, holder, conf,
      src_id, src_type, ev_off, obs_off, auth_off, ing_off,
      tags, derived=None, supersedes=None, contradicts=None,
      duplicates=None, aliases=None, scope="internal"):
    global mid_counter
    _hash = hashlib.md5(f"exp18-r5-{mid_counter}".encode()).hexdigest()[:8]
    mid_counter += 1
    ev = T0 + timedelta(days=ev_off)
    ob = T0 + timedelta(days=ev_off + obs_off)
    au = T0 + timedelta(days=ev_off + obs_off + auth_off)
    ig = T0 + timedelta(days=ev_off + obs_off + auth_off + ing_off)
    return {
        "memory_id": f"E18-{_hash}",
        "experiment": "exp18",
        "story_id": story,
        "event_time": ts(ev),
        "observation_time": ts(ob),
        "authored_time": ts(au),
        "ingestion_time": ts(ig),
        "subject": subj,
        "predicate": pred,
        "object": obj,
        "text": text,
        "memory_type": etype,
        "truth_role": truth_role,
        "belief_holder": holder,
        "confidence": conf,
        "source_id": src_id,
        "source_type": src_type,
        "derived_from": derived or [],
        "supersedes": supersedes or [],
        "contradicts": contradicts or [],
        "duplicates": duplicates or [],
        "aliases": aliases or [],
        "scope": scope,
        "tags": tags
    }

qid_counter = len(queries)

def Q(query, cat, expected, acceptable, forbidden, rel, dist, difficulty,
      uncertainty=False, conflict=False, disambiguate=False,
      scope=False, abstain=False, notes=""):
    global qid_counter
    qid_counter += 1
    return {
        "query_id": f"Q18-{qid_counter:02d}",
        "query": query,
        "category": cat,
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "relevant_memory_ids": rel,
        "distractor_memory_ids": dist,
        "must_surface_uncertainty": uncertainty,
        "must_surface_conflict": conflict,
        "must_disambiguate": disambiguate,
        "must_preserve_scope": scope,
        "should_abstain": abstain,
        "difficulty": difficulty,
        "notes": notes
    }

new_mem = []
new_q = []

# === Fill remaining memories across all cases and background ===

# C01 extras
new_mem.append(M("C01", "MERIT-2 monitoring committee", "was_disbanded", "after cancellation",
    "The independent MERIT-2 monitoring committee was disbanded in April 2031 following trial cancellation.",
    "event", "ground_truth", "Dr. Amara Obi", 1.0, "SRC-C01-26", "committee_record",
    760, 1, 2, 1, ["C01"]))

new_mem.append(M("C01", "MERIT-2 investigator brochure", "was_completed", "but never distributed to sites",
    "The MERIT-2 investigator brochure was completed in May 2030 but never distributed to clinical sites due to the subsequent cancellation.",
    "event", "counterfactual", "Dr. Amara Obi", 0.9, "SRC-C01-27", "document_record",
    425, 1, 3, 1, ["C01", "counterfactual"]))

new_mem.append(M("C01", "Genexis Corp GNX-201", "entered", "Phase III before MGI's MGT-401",
    "Genexis Corp's competing DMD therapy GNX-201 entered Phase III in late 2030, making MERIT-2's original endpoint design less competitive.",
    "event", "ground_truth", "system", 0.9, "SRC-C01-28", "industry_news",
    640, 2, 5, 2, ["C01"], scope="public"))

# C02 extras
new_mem.append(M("C02", "VP-3 manufacturing cost", "is", "$45,000 per clinical dose",
    "VP-3 manufacturing cost is approximately $45,000 per clinical dose at MGI's GMP facility.",
    "fact", "ground_truth", "Morgan Hale", 0.9, "SRC-C02-19", "manufacturing_record",
    365, 0, 1, 1, ["C02", "background"]))

new_mem.append(M("C02", "VP-5 projected cost", "would_have_been", "$12,000 per dose if adopted",
    "VP-5 was projected to cost only $12,000 per dose if adopted, one-quarter of VP-3 manufacturing costs — a factor Dr. Chen cited in his dissent.",
    "observation", "counterfactual", "Dr. Marcus Chen", 0.8, "SRC-C02-20", "cost_analysis",
    205, 2, 3, 1, ["C02", "counterfactual"]))

# C03 extras
new_mem.append(M("C03", "post-MERIT-1 hepatotoxicity review", "concluded", "MGT-401 is safe at therapeutic doses",
    "A comprehensive post-MERIT-1 hepatotoxicity review concluded that MGT-401 at therapeutic doses (1e13 vg/kg) poses negligible liver toxicity risk.",
    "event", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C03-19", "safety_review",
    700, 2, 5, 2, ["C03", "negation"],
    supersedes=[m["memory_id"] for m in memories if "was_assessed_for_risk_of" in m.get("predicate","")][:1]))

new_mem.append(M("C03", "MGT-401 hepatotoxicity risk", "was_removed_from", "top 5 program risks in 2032",
    "Hepatotoxicity was removed from the MGT-401 top-5 program risk register in 2032 following consistently clean safety data.",
    "event", "ground_truth", "Dr. Felix Brennan", 0.95, "SRC-C03-20", "risk_register_update",
    1095, 1, 2, 1, ["C03", "negation"],
    supersedes=[m["memory_id"] for m in memories if "was_downgraded" in m.get("predicate","") and "hepatotoxicity" in m.get("subject","").lower()][:1]))

# C04 extras
new_mem.append(M("C04", "BLA withdrawal", "was_communicated_to", "investors in Q4 2031 earnings call",
    "The BLA withdrawal decision was communicated to investors during MGI's Q4 2031 earnings call, along with the revised Q2 2033 timeline.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.95, "SRC-C04-21", "earnings_transcript",
    1000, 1, 3, 1, ["C04"], scope="public"))

# C05 extras
new_mem.append(M("C05", "Dr. Chen", "redirected_CF_expertise_to", "MGT-502 lung delivery optimization",
    "After MGT-603 rejection, Dr. Chen redirected his CF-related lung delivery expertise to optimizing MGT-502's delivery to motor neurons.",
    "event", "ground_truth", "Dr. Marcus Chen", 0.9, "SRC-C05-19", "research_record",
    500, 1, 2, 1, ["C05"]))

new_mem.append(M("C05", "MGT-603 feasibility data", "informed", "MGT-502 vector design",
    "Some vector modification data from the MGT-603 feasibility study was later used to inform MGT-502's AAV capsid engineering.",
    "observation", "ground_truth", "Dr. Marcus Chen", 0.85, "SRC-C05-20", "research_record",
    550, 2, 4, 1, ["C05"],
    derived=[m["memory_id"] for m in memories if m.get("story_id") == "C05" and "feasibility" in m.get("predicate","")][:1]))

# C06 extras
new_mem.append(M("C06", "NOVA-1 adverse events", "were_not", "life-threatening",
    "None of the 3 NOVA-1 adverse events were classified as life-threatening (CTCAE grade 4 or 5). All were grade 2.",
    "observation", "ground_truth", "Dr. Felix Brennan", 1.0, "SRC-C06-24", "safety_classification",
    545, 1, 2, 1, ["C06"]))

new_mem.append(M("C06", "NOVA-1 data", "was_shared_with", "other CRISPR therapy developers",
    "MGI shared NOVA-1 safety data with two other CRISPR therapy developers under confidential data-sharing agreements to help the field learn from the adverse events.",
    "event", "ground_truth", "Dr. Elena Vasquez", 0.9, "SRC-C06-25", "data_sharing_record",
    700, 1, 3, 1, ["C06"]))

# C07 extras
new_mem.append(M("C07", "Dr. Patel", "published_simulation_methods", "as open-source code",
    "Dr. Patel published the simulation methodology and code on GitHub as an open-source contribution, though the specific TRX-88 binding data was kept proprietary.",
    "event", "ground_truth", "Dr. Ravi Patel", 0.9, "SRC-C07-18", "publication_record",
    870, 2, 5, 2, ["C07"], scope="public"))

new_mem.append(M("C07", "no patent application", "was_filed_for", "MGT-401 + TRX-88 combination",
    "No patent application was filed for the MGT-401 + TRX-88 combination concept. The idea remains unprotected IP.",
    "event", "negation", "Jordan Reeves", 1.0, "SRC-C07-19", "ip_record",
    900, 0, 1, 1, ["C07", "negation"]))

# Background extras
new_mem.append(M("bg", "MGI", "has_a_DSMB", "for each active trial",
    "MGI maintains an independent Data Safety Monitoring Board for each active clinical trial, as required by FDA.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG44", "governance_record",
    30, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI publication record", "includes", "23 peer-reviewed papers as of 2032",
    "MGI researchers have published 23 peer-reviewed papers as of 2032, covering gene therapy vector biology, preclinical results, and MERIT-1 outcomes.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG45", "publication_record",
    1100, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI", "has_no_approved_products", "as of 2032",
    "As of 2032, MGI has no approved products on the market. It remains a clinical-stage company.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG46", "corporate_status",
    1100, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI clinical operations team", "consists_of", "28 staff members",
    "MGI's clinical operations team consists of 28 staff members led by Dr. Amara Obi.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG47", "org_chart",
    365, 0, 1, 1, ["background"]))

new_mem.append(M("bg", "MGI regulatory team", "consists_of", "6 staff members",
    "MGI's regulatory affairs team consists of 6 staff members led by Jordan Reeves.",
    "fact", "ground_truth", "system", 1.0, "SRC-BG48", "org_chart",
    365, 0, 1, 1, ["background"]))

# === Additional queries ===
new_q.append(Q(
    "Was the MERIT-2 investigator brochure ever sent to clinical sites?",
    "negation_detection",
    ["The investigator brochure was completed but never distributed to sites",
     "The trial was cancelled before distribution"],
    ["Brochure was ready but never used"],
    ["Sites received the brochure", "Investigators reviewed the brochure",
     "The brochure was distributed"],
    [n["memory_id"] for n in new_mem if "investigator brochure" in n.get("subject","").lower()][:1],
    [],
    "easy"
))

new_q.append(Q(
    "How do VP-3 and VP-5 compare in terms of cost per dose?",
    "counterfactual_distinction",
    ["VP-3 costs $45,000 per dose", "VP-5 was projected at $12,000 per dose",
     "VP-5 was never adopted despite the cost advantage"],
    ["VP-5 would have been cheaper but was rejected for safety reasons"],
    ["VP-5 is used because it's cheaper", "Cost was the deciding factor"],
    [n["memory_id"] for n in new_mem if "manufacturing cost" in n.get("subject","").lower() or "projected cost" in n.get("subject","").lower()][:2],
    [m["memory_id"] for m in memories if "was_rejected_by" in m.get("predicate","")][:1],
    "medium",
    notes="Cost advantage existed but safety concerns overrode it"
))

new_q.append(Q(
    "Has the hepatotoxicity risk been fully resolved for MGT-401?",
    "evidence_absence",
    ["Hepatotoxicity was removed from the top-5 risk register in 2032",
     "Post-MERIT-1 review concluded MGT-401 is safe at therapeutic doses",
     "Monitoring is still recommended as a precaution in future trials"],
    ["Risk has been effectively retired based on clean clinical data"],
    ["Hepatotoxicity remains a major concern", "Liver damage was observed",
     "The risk was never evaluated"],
    [n["memory_id"] for n in new_mem if "removed_from" in n.get("predicate","") or "concluded" in n.get("predicate","")][:2],
    [m["memory_id"] for m in memories if m.get("story_id") == "C03" and "risk" in m.get("predicate","")][:1],
    "hard"
))

new_q.append(Q(
    "Did MGI share the NOVA-1 safety data with anyone?",
    "factual_recall",
    ["MGI shared NOVA-1 safety data with two other CRISPR therapy developers",
     "This was done under confidential data-sharing agreements"],
    ["Data was shared to benefit the broader CRISPR therapy field"],
    ["Data was kept secret", "No one outside MGI saw the data"],
    [n["memory_id"] for n in new_mem if "shared_with" in n.get("predicate","") and "NOVA-1" in n.get("subject","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Was any IP protection sought for the combination therapy concept?",
    "negation_detection",
    ["No patent application was filed for the MGT-401 + TRX-88 combination",
     "The idea remains unprotected IP"],
    ["No IP protection was pursued"],
    ["A patent was filed", "The combination is patented", "IP was secured"],
    [n["memory_id"] for n in new_mem if "no patent" in n.get("subject","").lower()][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Did any of the MGT-603 feasibility work get reused?",
    "factual_recall",
    ["Some vector modification data informed MGT-502's AAV capsid engineering",
     "Dr. Chen redirected CF lung delivery expertise to MGT-502"],
    ["The work found indirect application in another program"],
    ["All work was wasted", "Nothing from MGT-603 was ever used",
     "MGT-603 data was discarded"],
    [n["memory_id"] for n in new_mem if "redirected" in n.get("predicate","") or "informed" in n.get("predicate","")][:2],
    [],
    "medium"
))

new_q.append(Q(
    "Were the NOVA-1 adverse events life-threatening?",
    "evidence_absence",
    ["None were life-threatening — all were classified as CTCAE grade 2",
     "Patients recovered fully within 2 weeks with corticosteroid treatment"],
    ["Adverse events were moderate and resolved"],
    ["Events were life-threatening", "Patients died", "Grade 4-5 events occurred"],
    [n["memory_id"] for n in new_mem if "not" in n.get("predicate","") and "life-threatening" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if "recovered_fully" in m.get("predicate","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "How was the BLA withdrawal communicated to stakeholders?",
    "temporal_reasoning",
    ["Communicated to investors during Q4 2031 earnings call",
     "Included the revised Q2 2033 resubmission timeline"],
    ["Public disclosure was made through standard investor communications"],
    ["The withdrawal was kept secret", "Investors were not informed"],
    [n["memory_id"] for n in new_mem if "earnings call" in n.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "What is Genexis Corp's GNX-201 and how did it affect MGI?",
    "temporal_reasoning",
    ["GNX-201 is a competing DMD therapy that entered Phase III in late 2030",
     "Its data made MERIT-2's primary endpoint design outdated",
     "This contributed to MERIT-2's cancellation"],
    ["A competitor's progress helped make MERIT-2 obsolete"],
    ["MGI has no competitors", "GNX-201 failed",
     "MERIT-2 was cancelled for internal reasons only"],
    [n["memory_id"] for n in new_mem if "GNX-201" in n.get("text","") or "Genexis" in n.get("text","")][:1] +
    [m["memory_id"] for m in memories if "Genexis" in m.get("text","")][:1],
    [],
    "medium"
))

new_q.append(Q(
    "How many peer-reviewed publications has MGI produced?",
    "factual_recall",
    ["23 peer-reviewed papers as of 2032"],
    ["Covering vector biology, preclinical results, and trial outcomes"],
    ["MGI has no publications", "Over 100 papers"],
    [n["memory_id"] for n in new_mem if "23 peer-reviewed" in n.get("text","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "Did Dr. Patel make any of the TRX-88 simulation work publicly available?",
    "scope_preservation",
    ["Simulation methodology and code were published as open source on GitHub",
     "Specific TRX-88 binding data was kept proprietary"],
    ["Methods were shared but proprietary results were withheld"],
    ["Everything was published", "Nothing was shared",
     "Clinical results were published"],
    [n["memory_id"] for n in new_mem if "open-source" in n.get("text","")][:1],
    [],
    "medium",
    scope=True
))

new_q.append(Q(
    "Does MGI have any approved products on the market?",
    "negation_detection",
    ["MGI has no approved products as of 2032",
     "It remains a clinical-stage company"],
    ["No products have reached market"],
    ["MGT-401 is approved", "MGI sells gene therapy products",
     "Products are available"],
    [n["memory_id"] for n in new_mem if "no_approved_products" in n.get("predicate","")][:1],
    [],
    "easy"
))

new_q.append(Q(
    "How large is MGI's clinical operations team?",
    "factual_recall",
    ["28 staff members led by Dr. Amara Obi"],
    ["A dedicated clinical team of about 28 people"],
    ["Thousands of employees", "No dedicated clinical team exists"],
    [n["memory_id"] for n in new_mem if "28 staff" in n.get("text","")][:1],
    [],
    "easy"
))

memories.extend(new_mem)
queries.extend(new_q)

# Rewrite
with open(os.path.join(d, "memories.jsonl"), "w") as f:
    for m in memories:
        f.write(json.dumps(m) + "\n")
with open(os.path.join(d, "queries.jsonl"), "w") as f:
    for q in queries:
        f.write(json.dumps(q) + "\n")

files_info = []
for fname in ["memories.jsonl", "queries.jsonl"]:
    fp = os.path.join(d, fname)
    data = open(fp, 'rb').read()
    files_info.append({"path": fname, "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})

with open(os.path.join(d, "manifest.json")) as f:
    manifest = json.load(f)
manifest["files"] = files_info
with open(os.path.join(d, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Round 5: {len(memories)} memories, {len(queries)} queries")
