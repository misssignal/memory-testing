#!/usr/bin/env python3
"""Round 3 expansion for Experiment 02 — final push to 200+/78+."""

import json, hashlib, os

OUT = "/home/user/memory-testing/normalized/experiment_02_false_consensus"

def mid(counter):
    return "E02-" + hashlib.md5(f"exp02-expand-{counter}".encode()).hexdigest()[:8]

def qid(seq):
    return f"Q02-{seq:02d}"

def mem(counter, **kw):
    return {
        "memory_id": mid(counter),
        "experiment": "exp02_false_consensus",
        "story_id": "nightglass-festival",
        "event_time": kw["et"],
        "observation_time": kw.get("ot", kw["et"]),
        "authored_time": kw.get("at", kw.get("ot", kw["et"])),
        "ingestion_time": kw.get("it", kw.get("at", kw.get("ot", kw["et"]))),
        "subject": kw["subj"],
        "predicate": kw["pred"],
        "object": kw["obj"],
        "text": kw["text"],
        "memory_type": kw.get("mtype", "observation"),
        "truth_role": kw.get("role", "historical_truth"),
        "belief_holder": kw.get("bh", "system"),
        "confidence": kw.get("conf", 1.0),
        "source_id": kw.get("sid", "src-nightglass"),
        "source_type": kw.get("stype", "system_record"),
        "derived_from": kw.get("derived", []),
        "supersedes": kw.get("supersedes", []),
        "contradicts": kw.get("contradicts", []),
        "duplicates": kw.get("duplicates", []),
        "aliases": kw.get("aliases", []),
        "scope": kw.get("scope", "festival"),
        "tags": kw.get("tags", []),
    }, kw.get("eroot", "")

def query(seq, **kw):
    return {
        "query_id": qid(seq),
        "query": kw["q"],
        "category": kw["cat"],
        "expected_claims": kw.get("expected", []),
        "acceptable_claims": kw.get("acceptable", []),
        "forbidden_claims": kw.get("forbidden", []),
        "relevant_memory_ids": kw.get("rel", []),
        "distractor_memory_ids": kw.get("dist", []),
        "difficulty": kw.get("diff", "medium"),
        "must_surface_uncertainty": kw.get("uncert", False),
        "must_surface_conflict": kw.get("conflict", False),
        "must_disambiguate": kw.get("disambig", False),
        "must_preserve_scope": kw.get("scope", False),
        "should_abstain": kw.get("abstain", False),
        "notes": kw.get("notes", ""),
    }

with open(os.path.join(OUT, "memories.jsonl")) as f:
    existing_mems = [json.loads(l) for l in f]
with open(os.path.join(OUT, "extensions.jsonl")) as f:
    existing_exts = [json.loads(l) for l in f]
with open(os.path.join(OUT, "queries.jsonl")) as f:
    existing_qs = [json.loads(l) for l in f]

print(f"Starting: {len(existing_mems)} memories, {len(existing_qs)} queries")

c = 500
new_mems = []
new_exts = []

def add(counter, eroot="", **kw):
    m, er = mem(counter, eroot=eroot, **kw)
    new_mems.append(m)
    ext = {"memory_id": m["memory_id"]}
    if er:
        ext["evidence_root"] = er
    new_exts.append(ext)
    return m["memory_id"]

# === ADDITIONAL DERIVED CLAIMS FROM 18000 ===

add(c, eroot="ROOT-18000", et="2026-03-20T00:00:00Z",
    subj="shuttle_service", pred="planned_for", obj="18000_attendees",
    text="Festival shuttle service contract specifies capacity for 18,000 daily round trips between parking overflow and the venue.",
    role="derived_claim", mtype="contract", tags=["capacity", "cascade"],
    sid="src-shuttle-contract", stype="vendor_contract"); c+=1

add(c, eroot="ROOT-18000", et="2026-04-02T00:00:00Z",
    subj="crowd_control_barriers", pred="ordered_for", obj="18000_crowd",
    text="Crowd control barrier order: 240 steel barriers configured for crowd channeling based on 18,000-person flow modeling.",
    role="derived_claim", mtype="procurement_record", tags=["capacity", "cascade"],
    sid="src-barrier-order", stype="procurement_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-04-18T00:00:00Z",
    subj="porta_potty_placement_map", pred="shows", obj="90_units_for_18000",
    text="Placement map for 90 portable restrooms positions them based on 18,000-person crowd density patterns.",
    role="derived_claim", mtype="site_plan", tags=["capacity", "cascade"],
    sid="src-porto-placement", stype="operations_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-05-03T00:00:00Z",
    subj="press_release", pred="announces", obj="18000_capacity_festival",
    text="Official press release: 'Nightglass Festival announces 18,000-capacity main stage event at historic Harborworks Shipyard, September 12-14.'",
    role="derived_claim", mtype="press_release", tags=["capacity", "cascade"],
    sid="src-press-release", stype="marketing_material"); c+=1

# === GATE TRANSITION DETAILS ===

add(c, eroot="ROOT-GATE-C", et="2026-07-25T00:00:00Z",
    subj="construction_notice", pred="announced", obj="gate_c_closure",
    text="Construction company posted notice July 25 that heavy equipment staging would block the Gate C access road starting July 30. Maya began planning the transition to Gate F.",
    role="historical_truth", mtype="construction_notice", tags=["gate_c", "gate_f", "venue"],
    sid="src-construction-notice", stype="contractor_communication"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-08-01T00:00:00Z",
    subj="signage", pred="installed_at", obj="Gate_F",
    text="New directional signage installed at Gate F and along the approach road. Signs read 'VENDORS → GATE F' with Nightglass Festival branding.",
    role="current_truth", mtype="operations_record", tags=["gate_f", "venue"],
    sid="src-signage-gatef", stype="operations_record"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-08-07T00:00:00Z",
    subj="second_vendor", pred="arrived_at", obj="Gate_C",
    text="Second vendor in a week arrived at the now-blocked Gate C. Called the festival hotline confused: 'All my paperwork says Gate C but there's a construction fence.'",
    role="historical_truth", mtype="incident_note", tags=["gate_c", "gate_f", "venue", "stale_echo"],
    sid="src-vendor-mixup-2", stype="operations_log"); c+=1

# === ADDITIONAL WATER PRESSURE CONTEXT ===

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-16T00:00:00Z",
    subj="Harborworks_Utilities", pred="estimated", obj="corrosion_from_salt_water",
    text="Harborworks Utilities estimated the valve corrosion developed over 3-5 years from salt water exposure common in shipyard infrastructure.",
    role="historical_truth", mtype="engineering_note", tags=["water_pressure"],
    sid="src-hw-corrosion-analysis", stype="engineering_report"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-21T00:00:00Z",
    subj="fire_department", pred="verified_repair", obj="pressure_restored",
    text="Fire Department independently verified the pressure restoration: 72 PSI at H-1, 70 PSI at H-2, 74 PSI at H-3, 71 PSI at H-4. All above 65 PSI minimum.",
    role="current_truth", mtype="inspection_report", tags=["water_pressure"],
    sid="src-fd-verification", stype="government_report"); c+=1

# === PATTERN: CORRECTIONS NOT PROPAGATING ===

add(c, eroot="ROOT-12400", et="2026-07-01T00:00:00Z",
    subj="Maya_Chen", pred="audit_detail", obj="18000_in_8_critical_docs",
    text="Maya's July 1 audit breakdown: insurance policy (18K), food contracts (18K), porta-potty order (18K), waste contract (18K), water plan (18K), parking plan (18K), sound spec (18K), medical plan (18K). All still uncorrected.",
    role="historical_truth", mtype="audit_report", tags=["capacity", "correction"],
    bh="Maya_Chen", sid="src-maya-audit-detail", stype="audit_report"); c+=1

add(c, eroot="ROOT-12400", et="2026-08-15T00:00:00Z",
    subj="Maya_Chen", pred="follow_up_audit", obj="5_still_uncorrected",
    text="Maya's August 15 follow-up audit: insurance policy, medical plan, parking plan, waste contract, and water distribution plan still show 18,000. Food contracts and porta-potty order were renegotiated.",
    role="historical_truth", mtype="audit_report", tags=["capacity", "correction"],
    bh="Maya_Chen", sid="src-maya-audit-aug", stype="audit_report"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-03T00:00:00Z",
    subj="food_vendor_contracts", pred="renegotiated", obj="12400_servings",
    text="Food vendor contracts renegotiated to 12,400 servings per day. Two vendors objected but eventually agreed to revised terms.",
    role="correction", mtype="contract", tags=["capacity", "fire_permit", "correction"],
    sid="src-food-renegotiated", stype="vendor_contract"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-08T00:00:00Z",
    subj="porta_potty_order", pred="reduced_to", obj="62_units",
    text="Portable restroom order reduced from 90 to 62 units based on corrected 12,400 capacity.",
    role="correction", mtype="procurement_record", tags=["capacity", "fire_permit", "correction"],
    sid="src-porto-corrected", stype="procurement_document"); c+=1

# === INSTITUTIONAL MEMORY TRAPS ===

add(c, eroot="ROOT-18000", et="2026-08-20T00:00:00Z",
    subj="new_hire_onboarding", pred="presents", obj="18000_in_deck",
    text="A new operations hire's onboarding deck includes a slide stating 'South Yard capacity: 18,000' — sourced from the shared drive where the archived deck copies still reside.",
    role="stale_truth", mtype="training_material", tags=["capacity", "cascade", "stale_echo", "institutional_echo"],
    sid="src-onboarding-stale", stype="training_material"); c+=1

add(c, eroot="ROOT-18000", et="2026-08-25T00:00:00Z",
    subj="city_council_minutes", pred="record", obj="18000_from_presentation",
    text="City council meeting minutes from April record the 18,000 figure as presented. Official government minutes are not typically corrected after the fact.",
    role="stale_truth", mtype="government_record", tags=["capacity", "cascade", "stale_echo"],
    sid="src-council-minutes", stype="government_record"); c+=1

add(c, eroot="ROOT-18000", et="2026-09-05T00:00:00Z",
    subj="google_knowledge_panel", pred="shows", obj="18000_capacity",
    text="Google's knowledge panel for 'Nightglass Festival' shows '18,000 capacity' sourced from the newspaper article and tourism board website.",
    role="stale_truth", mtype="search_result", tags=["capacity", "cascade", "stale_echo", "retrieval_amplification"],
    sid="src-google-panel", stype="external_reference"); c+=1

# === BELIEF EVOLUTION ===

add(c, eroot="ROOT-18000", et="2026-02-15T00:00:00Z",
    subj="Rowan_Pierce", pred="confident_in", obj="18000_capacity",
    text="In February, Rowan was fully confident in the 18,000 figure: 'This is a world-class venue and 18,000 is exactly the scale we need to be competitive.'",
    role="historical_truth", mtype="belief_snapshot", tags=["capacity", "belief"],
    bh="Rowan_Pierce", conf=0.95, sid="src-rowan-conf-feb", stype="correspondence"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-15T00:00:00Z",
    subj="Rowan_Pierce", pred="accepted", obj="12400_reality",
    text="By mid-June, Rowan had accepted the 12,400 limit: 'It changes our business model, but we can't argue with the fire department. Let's make 12,400 work.'",
    role="historical_truth", mtype="belief_snapshot", tags=["capacity", "fire_permit", "belief"],
    bh="Rowan_Pierce", sid="src-rowan-accept", stype="correspondence"); c+=1

print(f"New memories: {len(new_mems)}")

all_mems = existing_mems + new_mems
all_exts = existing_exts + new_exts

with open(os.path.join(OUT, "memories.jsonl"), "w") as f:
    for m in all_mems:
        f.write(json.dumps(m) + "\n")

with open(os.path.join(OUT, "extensions.jsonl"), "w") as f:
    for e in all_exts:
        f.write(json.dumps(e) + "\n")

# Add remaining queries
q = len(existing_qs) + 1
new_qs = []

new_qs.append(query(q, q="How many portable restrooms were originally ordered vs the corrected number?",
    cat="factual_recall",
    expected=["Originally 90 based on 18,000; reduced to 62 based on 12,400"],
    diff="easy")); q+=1

new_qs.append(query(q, q="How did the capacity cascade affect vendor contracts?",
    cat="factual_recall",
    expected=["Food vendor contracts were renegotiated to 12,400 servings", "Porta-potty order was reduced from 90 to 62 units", "Some vendor contracts (shuttle, waste management) were not yet renegotiated"],
    diff="medium")); q+=1

new_qs.append(query(q, q="Can the city council minutes about the 18,000 capacity be corrected?",
    cat="stale_reference",
    expected=["Official government minutes typically are not corrected after the fact", "The 18,000 figure in the minutes reflects what was presented at the time"],
    diff="medium", uncert=True)); q+=1

new_qs.append(query(q, q="How many vendors were misdirected to Gate C after the change to Gate F?",
    cat="factual_recall",
    expected=["At least two vendors arrived at Gate C and had to be redirected"],
    diff="easy")); q+=1

new_qs.append(query(q, q="What was the original concept plan author's intent for the 18,000 figure?",
    cat="provenance_tracking",
    expected=["It was a rough estimate based on square footage and a rule of thumb", "The author did not intend it as an official capacity figure", "They did not validate it against fire safety standards"],
    diff="medium")); q+=1

new_qs.append(query(q, q="How does Google's knowledge panel for Nightglass Festival contribute to the false consensus?",
    cat="confidence_calibration",
    expected=["It shows 18,000 capacity sourced from the newspaper and tourism board", "This creates a public-facing authoritative-looking source that reinforces the incorrect figure"],
    diff="medium",
    notes="Tests understanding of external amplification of cascade")); q+=1

new_qs.append(query(q, q="What was the sequence of Rowan Pierce's beliefs about the South Yard capacity?",
    cat="belief_vs_fact",
    expected=["February: fully confident in 18,000", "June 5: frustrated by the reduction", "June 12: asked if permit could be amended", "Mid-June: accepted the 12,400 reality"],
    diff="hard")); q+=1

new_qs.append(query(q, q="How long was the east hydrant loop compromised before being detected?",
    cat="temporal_reasoning",
    expected=["Harborworks Utilities estimated the corrosion developed over 3-5 years", "It was not detected until the independent observations on August 11, 2026"],
    diff="medium")); q+=1

print(f"New queries: {len(new_qs)}")

all_qs = existing_qs + new_qs

with open(os.path.join(OUT, "queries.jsonl"), "w") as f:
    for q_obj in all_qs:
        f.write(json.dumps(q_obj) + "\n")

# Write manifest
import hashlib as hl
manifest = {"experiment": "exp02_false_consensus", "files": []}
for fname in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, fname)
    if not os.path.isfile(fpath):
        continue
    data = open(fpath, "rb").read()
    manifest["files"].append({
        "path": fname,
        "bytes": len(data),
        "sha256": hl.sha256(data).hexdigest()
    })
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
manifest["files"] = []
for fname in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, fname)
    if not os.path.isfile(fpath):
        continue
    data = open(fpath, "rb").read()
    manifest["files"].append({
        "path": fname,
        "bytes": len(data),
        "sha256": hl.sha256(data).hexdigest()
    })
with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nFinal: {len(all_mems)} memories, {len(all_qs)} queries written to {OUT}")
