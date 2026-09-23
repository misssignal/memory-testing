#!/usr/bin/env python3
"""Expand Experiment 02 (False Consensus / Nightglass Festival) from 40 memories/0 queries to 200+/78+."""

import json, hashlib, os

SRC = "/home/user/memory-testing/normalized/experiment_02_false_consensus"
OUT = SRC

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

# Read existing
with open(os.path.join(OUT, "memories.jsonl")) as f:
    existing_mems = [json.loads(l) for l in f]
with open(os.path.join(OUT, "extensions.jsonl")) as f:
    existing_exts = [json.loads(l) for l in f]

print(f"Starting: {len(existing_mems)} memories, 0 queries")

c = 100  # offset to avoid collision with normalized IDs
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

# ============================================================
# ARC 1: THE 18,000 CASCADE (ROOT-18000)
# One obsolete number propagated through many derivative documents
# ============================================================

# Origin: concept plan spreadsheet
add(c, eroot="ROOT-18000", et="2026-01-15T00:00:00Z",
    subj="South_Yard", pred="concept_capacity", obj="18000",
    text="Initial Nightglass Festival concept plan spreadsheet lists South Yard capacity as 18,000 based on a preliminary site walkthrough before fire safety review.",
    role="false_claim", mtype="spreadsheet_cell", tags=["capacity", "cascade", "root_source"],
    sid="src-concept-plan", stype="planning_document"); c+=1

# Ticket platform import
add(c, eroot="ROOT-18000", et="2026-02-01T00:00:00Z",
    subj="ticket_platform", pred="imported_capacity", obj="18000_from_spreadsheet",
    text="Ticketing platform automatically imported the 18,000 figure from the concept plan spreadsheet as the South Yard capacity ceiling.",
    role="derived_claim", mtype="system_import", tags=["capacity", "cascade"],
    sid="src-ticket-import", stype="ticket_system",
    derived=[mid(100)]); c+=1

add(c, eroot="ROOT-18000", et="2026-02-05T00:00:00Z",
    subj="ticket_sales", pred="configured_limit", obj="18000_south_yard",
    text="Online ticket sales page shows 'South Yard — General Admission (18,000 capacity)' as imported from the planning system.",
    role="derived_claim", mtype="web_page", tags=["capacity", "cascade"],
    sid="src-ticket-page", stype="public_listing",
    derived=[mid(101)]); c+=1

# Marketing deck
add(c, eroot="ROOT-18000", et="2026-02-10T00:00:00Z",
    subj="Rowan_Pierce", pred="created", obj="investor_deck_with_18000",
    text="Rowan Pierce's investor deck states: 'The South Yard accommodates up to 18,000 attendees, making Nightglass one of the largest single-stage festivals in the region.'",
    role="derived_claim", mtype="slide_deck", tags=["capacity", "cascade"],
    bh="Rowan_Pierce", sid="src-investor-deck", stype="presentation",
    derived=[mid(100)]); c+=1

# Meeting recap citing deck
add(c, eroot="ROOT-18000", et="2026-02-15T00:00:00Z",
    subj="planning_meeting", pred="cited", obj="18000_capacity_from_deck",
    text="Planning meeting recap from February 15 states: 'Per the investor deck, we're planning for 18,000 capacity in the South Yard.'",
    role="derived_claim", mtype="meeting_recap", tags=["capacity", "cascade"],
    sid="src-meeting-0215", stype="meeting_minutes",
    derived=[mid(103)]); c+=1

# Safety training document
add(c, eroot="ROOT-18000", et="2026-03-01T00:00:00Z",
    subj="safety_training", pred="states_capacity", obj="18000",
    text="Safety coordinator training manual states: 'The South Yard maximum occupancy is 18,000 persons. Ensure all emergency egress plans account for this figure.'",
    role="derived_claim", mtype="training_document", tags=["capacity", "cascade"],
    sid="src-safety-training", stype="training_material",
    derived=[mid(104)]); c+=1

# Vendor briefing packet
add(c, eroot="ROOT-18000", et="2026-03-10T00:00:00Z",
    subj="vendor_packet", pred="states_capacity", obj="18000",
    text="Vendor briefing packet distributed to all contractors states: 'South Yard expected attendance: up to 18,000.'",
    role="derived_claim", mtype="briefing_packet", tags=["capacity", "cascade", "venue"],
    sid="src-vendor-packet", stype="vendor_document",
    derived=[mid(105)]); c+=1

# Blue Lantern Security staffing plan
add(c, eroot="ROOT-18000", et="2026-03-15T00:00:00Z",
    subj="Blue_Lantern_Security", pred="staffing_based_on", obj="18000_capacity",
    text="Blue Lantern Security's staffing plan allocates 90 guards for the South Yard based on the 18,000 capacity figure (1 guard per 200 attendees).",
    role="derived_claim", mtype="staffing_plan", tags=["capacity", "cascade"],
    sid="src-bls-staffing", stype="contractor_plan",
    derived=[mid(106)]); c+=1

# Newsletter mention
add(c, eroot="ROOT-18000", et="2026-04-01T00:00:00Z",
    subj="festival_newsletter", pred="states", obj="18000_fans_expected",
    text="Nightglass Festival newsletter to subscribers: 'Join 18,000 fellow music lovers in the South Yard for three days of unforgettable performances!'",
    role="derived_claim", mtype="newsletter", tags=["capacity", "cascade"],
    sid="src-newsletter-04", stype="marketing_material",
    derived=[mid(103)]); c+=1

# Social media post
add(c, eroot="ROOT-18000", et="2026-04-05T00:00:00Z",
    subj="social_media", pred="claims", obj="18000_capacity",
    text="Nightglass Festival official social media post: 'South Yard: 18K capacity. Three stages. One incredible weekend.'",
    role="derived_claim", mtype="social_post", tags=["capacity", "cascade"],
    sid="src-social-0405", stype="social_media",
    derived=[mid(108)]); c+=1

# Archived copy of investor deck v1
add(c, eroot="ROOT-18000", et="2026-02-10T00:00:00Z", ot="2026-02-10T00:00:00Z", at="2026-04-10T00:00:00Z",
    subj="investor_deck_v1_archived", pred="copy_of", obj="original_investor_deck",
    text="Archived copy of investor deck v1.0 saved to shared drive on April 10. Contains the same 18,000 South Yard capacity claim as the original.",
    role="duplicate", mtype="slide_deck_copy", tags=["capacity", "cascade", "exact_duplicate"],
    sid="src-deck-archive", stype="archive_copy",
    duplicates=[mid(103)]); c+=1

# Second archived copy
add(c, eroot="ROOT-18000", et="2026-02-10T00:00:00Z", ot="2026-02-10T00:00:00Z", at="2026-05-01T00:00:00Z",
    subj="investor_deck_backup", pred="copy_of", obj="original_investor_deck",
    text="Backup copy of investor deck found in Maya Chen's personal folder, dated May 1. Identical 18,000 claim.",
    role="duplicate", mtype="slide_deck_copy", tags=["capacity", "cascade", "exact_duplicate"],
    sid="src-deck-backup", stype="archive_copy",
    duplicates=[mid(103)]); c+=1

# Summary document citing meeting recap
add(c, eroot="ROOT-18000", et="2026-04-15T00:00:00Z",
    subj="executive_summary", pred="states", obj="18000_based_on_meeting",
    text="Executive summary for the city council presentation references '18,000-person South Yard capacity' citing the February planning meeting recap.",
    role="derived_claim", mtype="summary_document", tags=["capacity", "cascade"],
    sid="src-exec-summary", stype="government_submission",
    derived=[mid(104)]); c+=1

# Media article
add(c, eroot="ROOT-18000", et="2026-04-20T00:00:00Z",
    subj="local_newspaper", pred="reported", obj="18000_capacity",
    text="Local newspaper article: 'Nightglass Festival expects to draw 18,000 to the former Harborworks shipyard's South Yard.'",
    role="derived_claim", mtype="news_article", tags=["capacity", "cascade"],
    sid="src-newspaper-0420", stype="media_report",
    derived=[mid(109)]); c+=1

# Jules Carter parroting the number
add(c, eroot="ROOT-18000", et="2026-05-01T00:00:00Z",
    subj="Jules_Carter", pred="referenced", obj="18000_in_safety_briefing",
    text="Jules Carter's safety briefing to the venue team references the 18,000 figure: 'Our plans accommodate up to 18,000 in the South Yard.'",
    role="derived_claim", mtype="briefing_notes", tags=["capacity", "cascade"],
    bh="Jules_Carter", sid="src-jules-briefing", stype="presentation",
    derived=[mid(105)]); c+=1

# AI-generated summary recycling the majority claim
add(c, eroot="ROOT-18000", et="2026-05-10T00:00:00Z",
    subj="ai_summary", pred="states", obj="18000_consensus_capacity",
    text="AI-generated planning summary: 'Based on available documentation, the South Yard capacity is 18,000. This figure appears across multiple independent sources including the investor deck, vendor briefings, and safety training materials.'",
    role="false_claim", mtype="generated_summary", tags=["capacity", "cascade", "retrieval_amplification"],
    sid="src-ai-summary", stype="generated_content",
    derived=[mid(103), mid(105), mid(106)]); c+=1

# Search result amplification
add(c, eroot="ROOT-18000", et="2026-05-15T00:00:00Z",
    subj="search_result", pred="top_result", obj="18000_south_yard",
    text="Internal knowledge base search for 'South Yard capacity' returns 14 documents citing 18,000 and only 1 document showing 12,400.",
    role="false_claim", mtype="search_result", tags=["capacity", "cascade", "retrieval_amplification"],
    sid="src-search-result", stype="generated_content"); c+=1

# Rowan's updated talking points still using 18000
add(c, eroot="ROOT-18000", et="2026-06-01T00:00:00Z",
    subj="Rowan_Pierce", pred="talking_points", obj="18000_still_cited",
    text="Rowan's June talking points for sponsor calls still reference 18,000 capacity. He has not seen the fire permit correction.",
    role="stale_truth", mtype="talking_points", tags=["capacity", "cascade", "stale_echo"],
    bh="Rowan_Pierce", sid="src-rowan-tp-06", stype="internal_document",
    derived=[mid(103)]); c+=1

# ============================================================
# ARC 2: THE 12,400 TRUTH (ROOT-12400)
# Controlling fire permit — the actual authority
# ============================================================

add(c, eroot="ROOT-12400", et="2026-03-20T00:00:00Z",
    subj="fire_permit", pred="establishes_capacity", obj="12400_south_yard",
    text="Fire permit #FP-2026-0847 issued March 20 by City Fire Department establishes the South Yard maximum occupancy at 12,400 persons based on egress analysis and hydrant coverage.",
    role="current_truth", mtype="legal_permit", tags=["capacity", "fire_permit", "root_source"],
    sid="src-fire-permit", stype="government_permit"); c+=1

add(c, eroot="ROOT-12400", et="2026-03-22T00:00:00Z",
    subj="Omar_Velasquez", pred="confirmed", obj="12400_permit_limit",
    text="Omar Velasquez confirmed receipt of fire permit FP-2026-0847 and noted the 12,400 limit to Maya Chen in an email: 'This is the controlling number — all plans must use 12,400, not the earlier estimates.'",
    role="current_truth", mtype="email", tags=["capacity", "fire_permit"],
    bh="Omar_Velasquez", sid="src-omar-email-0322", stype="correspondence"); c+=1

add(c, eroot="ROOT-12400", et="2026-03-25T00:00:00Z",
    subj="Maya_Chen", pred="updated_operations_plan", obj="12400_capacity",
    text="Maya Chen updated the site operations plan to reflect the 12,400 fire permit limit. However, she did not propagate this correction to the ticket platform or marketing materials.",
    role="current_truth", mtype="operations_plan", tags=["capacity", "fire_permit"],
    bh="Maya_Chen", sid="src-ops-plan-update", stype="operations_document"); c+=1

add(c, eroot="ROOT-12400", et="2026-04-01T00:00:00Z",
    subj="fire_department", pred="inspection_note", obj="capacity_12400_confirmed",
    text="City Fire Department inspection note confirms South Yard occupancy limit of 12,400, consistent with permit FP-2026-0847.",
    role="current_truth", mtype="inspection_report", tags=["capacity", "fire_permit"],
    sid="src-fire-inspection", stype="government_report"); c+=1

add(c, eroot="ROOT-12400", et="2026-05-20T00:00:00Z",
    subj="Jules_Carter", pred="discovered", obj="permit_discrepancy",
    text="Jules Carter discovered the discrepancy between the 18,000 figure in planning documents and the 12,400 fire permit limit while reviewing emergency evacuation times.",
    role="historical_truth", mtype="observation", tags=["capacity", "fire_permit", "correction"],
    bh="Jules_Carter", sid="src-jules-discovery", stype="internal_communication"); c+=1

add(c, eroot="ROOT-12400", et="2026-05-22T00:00:00Z",
    subj="Jules_Carter", pred="alerted", obj="rowan_about_capacity_error",
    text="Jules Carter sent an urgent email to Rowan Pierce: 'Our planning docs say 18,000 but the fire permit caps us at 12,400. We need to correct all downstream documents immediately.'",
    role="correction", mtype="email", tags=["capacity", "fire_permit", "correction"],
    bh="Jules_Carter", sid="src-jules-alert", stype="correspondence"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-01T00:00:00Z",
    subj="ticket_platform", pred="corrected_to", obj="12400",
    text="Ticket platform capacity updated to 12,400 on June 1 after Jules Carter's discovery. Approximately 2,000 excess tickets had already been allocated but not yet sold.",
    role="correction", mtype="system_update", tags=["capacity", "fire_permit", "correction"],
    sid="src-ticket-correction", stype="ticket_system"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-05T00:00:00Z",
    subj="Blue_Lantern_Security", pred="revised_staffing", obj="based_on_12400",
    text="Blue Lantern Security revised staffing plan from 90 to 62 guards based on the corrected 12,400 capacity (1 guard per 200 attendees).",
    role="correction", mtype="staffing_plan", tags=["capacity", "fire_permit", "correction"],
    sid="src-bls-revised", stype="contractor_plan"); c+=1

# ============================================================
# ARC 3: RUMOR PROPAGATION — fire marshal sign-off
# ============================================================

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-03-15T00:00:00Z",
    subj="unnamed_staff", pred="mentioned", obj="fire_marshal_might_have_approved_18000",
    text="At a casual lunch conversation, a staff member mentioned they heard the fire marshal 'signed off on our numbers' — referring ambiguously to the fire safety review process.",
    role="rumor", mtype="informal_communication", tags=["capacity", "rumor"],
    bh="unnamed_staff", conf=0.3, sid="src-rumor-origin", stype="hearsay"); c+=1

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-03-20T00:00:00Z",
    subj="vendor_coordinator", pred="told_vendors", obj="fire_marshal_approved_18000",
    text="Vendor coordinator told incoming contractors: 'The fire marshal signed off on 18,000 for the South Yard, so we're good to go.'",
    role="rumor", mtype="informal_communication", tags=["capacity", "rumor", "rumor_propagation"],
    bh="vendor_coordinator", conf=0.4, sid="src-rumor-vendor", stype="hearsay",
    derived=[mid(c-1)]); c+=1

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-04-10T00:00:00Z",
    subj="safety_handbook", pred="states", obj="fire_marshal_approved_18000_capacity",
    text="Safety handbook revision dated April 10 states: 'South Yard capacity of 18,000 has been approved by the fire marshal's office.' This is false — the fire permit actually sets 12,400.",
    role="false_claim", mtype="handbook_entry", tags=["capacity", "rumor", "rumor_propagation"],
    sid="src-handbook-0410", stype="handbook",
    derived=[mid(c-1)]); c+=1

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-05-01T00:00:00Z",
    subj="training_session", pred="reinforced", obj="fire_marshal_18000_myth",
    text="New volunteer training session on May 1 includes the claim: 'The fire marshal has officially approved our 18,000-person capacity for the South Yard.' No one questions this.",
    role="false_claim", mtype="training_material", tags=["capacity", "rumor", "rumor_propagation"],
    sid="src-training-rumor", stype="training_material",
    derived=[mid(c-1)]); c+=1

# ============================================================
# ARC 4: GENUINE INDEPENDENT CONSENSUS — water pressure (ROOT-W*)
# Five truly independent observations converging on the same conclusion
# ============================================================

add(c, eroot="ROOT-W1", et="2026-08-11T09:00:00Z",
    subj="Harborworks_Utilities", pred="measured", obj="low_water_pressure_east_loop",
    text="Harborworks Utilities team measured water pressure at the east hydrant loop at 35 PSI, well below the required 65 PSI minimum for fire safety compliance.",
    role="independent_support", mtype="measurement_record", tags=["water_pressure"],
    sid="src-hw-measurement", stype="utility_measurement"); c+=1

add(c, eroot="ROOT-W2", et="2026-08-11T10:15:00Z",
    subj="fire_department", pred="tested", obj="hydrant_flow_rate_below_spec",
    text="City Fire Department conducted an independent flow test on east loop hydrants during a routine inspection. Flow rate measured at 450 GPM vs. required 750 GPM.",
    role="independent_support", mtype="inspection_report", tags=["water_pressure"],
    sid="src-fd-flow-test", stype="government_report"); c+=1

add(c, eroot="ROOT-W3", et="2026-08-11T11:30:00Z",
    subj="Blue_Lantern_Security", pred="reported", obj="weak_hydrant_flow_during_drill",
    text="Blue Lantern Security reported poor hydrant flow during an emergency drill. Guard noted: 'The east side hydrant barely produced a stream — completely inadequate for crowd-density firefighting.'",
    role="independent_support", mtype="drill_report", tags=["water_pressure"],
    bh="Blue_Lantern_Security", sid="src-bls-drill", stype="contractor_report"); c+=1

add(c, eroot="ROOT-W4", et="2026-08-11T13:00:00Z",
    subj="plumber_contractor", pred="observed", obj="corrosion_in_east_supply_line",
    text="Licensed plumber contracted for the festival's temporary facilities found significant corrosion in the east hydrant supply line during unrelated work.",
    role="independent_support", mtype="contractor_observation", tags=["water_pressure"],
    bh="plumber_contractor", sid="src-plumber-obs", stype="contractor_report"); c+=1

add(c, eroot="ROOT-W5", et="2026-08-11T14:45:00Z",
    subj="Maya_Chen", pred="tested", obj="faucet_pressure_low_east_building",
    text="Maya Chen noticed unusually low water pressure in the east building's restroom and tested multiple faucets, all showing weak flow. She independently flagged this to the venue manager.",
    role="independent_support", mtype="personal_observation", tags=["water_pressure"],
    bh="Maya_Chen", sid="src-maya-obs", stype="personal_note"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-12T00:00:00Z",
    subj="east_hydrant_loop", pred="confirmed_low_pressure", obj="five_independent_observations",
    text="Five independent observations on August 11 from different parties all confirm abnormally low water pressure in the east hydrant loop: Harborworks Utilities (35 PSI), Fire Department (450 GPM), Blue Lantern Security (drill failure), plumber (corrosion), and Maya Chen (faucet test).",
    role="current_truth", mtype="consensus_summary", tags=["water_pressure", "independent_consensus"],
    sid="src-pressure-consensus", stype="investigation_summary"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-15T00:00:00Z",
    subj="Harborworks_Utilities", pred="diagnosed", obj="corroded_main_supply_valve",
    text="Harborworks Utilities diagnosed the root cause: a corroded main supply valve feeding the east hydrant loop had been restricting flow for months.",
    role="current_truth", mtype="engineering_report", tags=["water_pressure"],
    sid="src-hw-diagnosis", stype="engineering_report"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-20T00:00:00Z",
    subj="east_hydrant_loop", pred="repaired", obj="valve_replaced_pressure_restored",
    text="East hydrant loop supply valve replaced August 20. Post-repair pressure measured at 72 PSI, meeting fire safety requirements.",
    role="current_truth", mtype="maintenance_record", tags=["water_pressure"],
    sid="src-hw-repair", stype="maintenance_report"); c+=1

# ============================================================
# ARC 5: GATE C → GATE F TRANSITION (ROOT-GATE-C, ROOT-GATE-F)
# Vendor ingress changed, but old docs dominate
# ============================================================

add(c, eroot="ROOT-GATE-C", et="2026-02-01T00:00:00Z",
    subj="vendor_ingress", pred="assigned_to", obj="Gate_C",
    text="Initial site operations plan designates Gate C as the primary vendor ingress point for all contractor deliveries and personnel.",
    role="stale_truth", mtype="operations_plan", tags=["gate_c", "venue"],
    sid="src-site-ops-v1", stype="operations_document"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-03-01T00:00:00Z",
    subj="vendor_map", pred="shows", obj="Gate_C_vendor_ingress",
    text="Printed vendor site map distributed in March shows Gate C as vendor ingress with directional arrows and parking assignments.",
    role="stale_truth", mtype="site_map", tags=["gate_c", "venue", "stale_echo"],
    sid="src-vendor-map-v1", stype="planning_document"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-04-01T00:00:00Z",
    subj="loading_schedule", pred="references", obj="Gate_C",
    text="Master loading schedule for vendor deliveries references Gate C as the drop-off point for all days of the festival.",
    role="stale_truth", mtype="schedule", tags=["gate_c", "venue", "stale_echo"],
    sid="src-loading-schedule", stype="operations_document"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-05-01T00:00:00Z",
    subj="Blue_Lantern_Security", pred="checkpoint_assignment", obj="Gate_C_vendor",
    text="Blue Lantern Security's checkpoint assignment roster lists Gate C as the vendor checkpoint with dedicated credential verification staffing.",
    role="stale_truth", mtype="staffing_plan", tags=["gate_c", "venue", "stale_echo"],
    sid="src-bls-checkpoint", stype="contractor_plan"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-06-15T00:00:00Z",
    subj="contractor_FAQ", pred="directs_to", obj="Gate_C",
    text="Contractor FAQ document updated June 15 directs all vendors to Gate C for ingress. 'Q: Where do I enter? A: All vendor personnel enter through Gate C.'",
    role="stale_truth", mtype="faq_document", tags=["gate_c", "venue", "stale_echo"],
    sid="src-contractor-faq", stype="internal_document"); c+=1

# Gate F becomes current
add(c, eroot="ROOT-GATE-F", et="2026-07-31T00:00:00Z",
    subj="vendor_ingress", pred="reassigned_to", obj="Gate_F",
    text="Vendor ingress reassigned from Gate C to Gate F on July 31 due to construction blocking the Gate C access road. Maya Chen issued the change notice.",
    role="current_truth", mtype="change_notice", tags=["gate_f", "venue", "state_transition"],
    sid="src-gate-change", stype="operations_notice"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-07-31T00:00:00Z",
    subj="Maya_Chen", pred="emailed", obj="gate_f_change_to_all_vendors",
    text="Maya Chen emailed all registered vendors: 'Effective immediately, vendor ingress has moved from Gate C to Gate F. Please update your GPS and arrival instructions.'",
    role="current_truth", mtype="email", tags=["gate_f", "venue"],
    bh="Maya_Chen", sid="src-maya-gate-email", stype="correspondence"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-08-01T00:00:00Z",
    subj="updated_site_map", pred="shows", obj="Gate_F_vendor_ingress",
    text="Updated digital site map now shows Gate F as vendor ingress. Only posted to the vendor portal; printed maps still show Gate C.",
    role="current_truth", mtype="site_map", tags=["gate_f", "venue"],
    sid="src-vendor-map-v2", stype="operations_document"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-08-05T00:00:00Z",
    subj="late_arriving_vendor", pred="went_to", obj="Gate_C",
    text="A vendor arriving August 5 went to Gate C per their printed map, found it blocked, and had to call Maya Chen to get redirected to Gate F.",
    role="historical_truth", mtype="incident_note", tags=["gate_c", "gate_f", "venue", "stale_echo"],
    sid="src-vendor-mixup", stype="operations_log"); c+=1

# Gate C docs still heavily outnumber Gate F
add(c, eroot="ROOT-GATE-C", et="2026-07-15T00:00:00Z",
    subj="internal_search", pred="returns", obj="15_gate_c_docs_vs_3_gate_f",
    text="Searching the festival document system for 'vendor gate' returns 15 documents referencing Gate C and only 3 referencing Gate F.",
    role="stale_truth", mtype="search_result", tags=["gate_c", "gate_f", "venue", "stale_volume", "retrieval_amplification"],
    sid="src-doc-search", stype="system_output"); c+=1

# ============================================================
# ARC 6: BACKGROUND / FESTIVAL SETUP
# ============================================================

add(c, eroot="", et="2025-11-01T00:00:00Z",
    subj="Nightglass_Festival_LLC", pred="founded_by", obj="Rowan_Pierce",
    text="Nightglass Festival LLC was founded by Rowan Pierce in November 2025 as a three-day arts and music festival.",
    role="historical_truth", tags=["background"],
    sid="src-nf-charter", stype="business_record"); c+=1

add(c, eroot="", et="2025-12-01T00:00:00Z",
    subj="Harborworks_Shipyard", pred="selected_as", obj="festival_venue",
    text="The former Harborworks Shipyard was selected as the Nightglass Festival venue. The South Yard is the primary outdoor stage field.",
    role="historical_truth", tags=["background", "venue"],
    sid="src-venue-selection", stype="business_record"); c+=1

add(c, eroot="", et="2025-12-15T00:00:00Z",
    subj="Maya_Chen", pred="hired_as", obj="site_operations_director",
    text="Maya Chen was hired as site operations director, responsible for all venue logistics, layout, and day-of operations.",
    role="historical_truth", tags=["background"],
    sid="src-personnel", stype="hr_record"); c+=1

add(c, eroot="", et="2025-12-20T00:00:00Z",
    subj="Jules_Carter", pred="hired_as", obj="safety_coordinator",
    text="Jules Carter was hired as safety coordinator, responsible for emergency planning, fire safety compliance, and crowd management protocols.",
    role="historical_truth", tags=["background"],
    sid="src-personnel", stype="hr_record"); c+=1

add(c, eroot="", et="2026-01-05T00:00:00Z",
    subj="Omar_Velasquez", pred="role", obj="fire_marshal_liaison",
    text="Omar Velasquez serves as the fire marshal liaison, coordinating between the festival and the City Fire Department on all permit and inspection matters.",
    role="historical_truth", tags=["background"],
    sid="src-personnel", stype="hr_record"); c+=1

add(c, eroot="", et="2026-01-10T00:00:00Z",
    subj="Blue_Lantern_Security", pred="contracted_for", obj="festival_security",
    text="Blue Lantern Security contracted to provide all security services for Nightglass Festival including access control, crowd management, and emergency response.",
    role="historical_truth", tags=["background"],
    sid="src-bls-contract", stype="contract"); c+=1

add(c, eroot="", et="2026-01-15T00:00:00Z",
    subj="South_Yard", pred="dimensions", obj="120m_x_85m_open_field",
    text="The South Yard is an open field measuring approximately 120m x 85m, previously used as a ship assembly staging area at the Harborworks Shipyard.",
    role="historical_truth", tags=["background", "venue"],
    sid="src-site-survey", stype="survey_report"); c+=1

add(c, eroot="", et="2026-08-25T00:00:00Z",
    subj="festival_dates", pred="scheduled_for", obj="September_12_to_14_2026",
    text="Nightglass Festival is scheduled for September 12-14, 2026 at the Harborworks Shipyard.",
    role="current_truth", tags=["background"],
    sid="src-festival-dates", stype="event_listing"); c+=1

# ============================================================
# ARC 7: ADDITIONAL CASCADE ARTIFACTS / CORRECTIONS
# ============================================================

# More 18000 derivatives
add(c, eroot="ROOT-18000", et="2026-03-05T00:00:00Z",
    subj="site_permit_application", pred="listed_capacity", obj="18000",
    text="Festival's site permit application to the city listed expected attendance as 18,000 for the South Yard, before the fire safety review was completed.",
    role="derived_claim", mtype="permit_application", tags=["capacity", "cascade"],
    sid="src-permit-app", stype="government_submission",
    derived=[mid(100)]); c+=1

add(c, eroot="ROOT-18000", et="2026-04-25T00:00:00Z",
    subj="insurance_policy", pred="covers", obj="18000_attendees",
    text="Festival liability insurance policy underwritten for up to 18,000 attendees in the South Yard. Premium calculated on this figure.",
    role="derived_claim", mtype="insurance_document", tags=["capacity", "cascade"],
    sid="src-insurance", stype="financial_document",
    derived=[mid(100)]); c+=1

add(c, eroot="ROOT-18000", et="2026-05-05T00:00:00Z",
    subj="food_vendor_contract", pred="based_on", obj="18000_servings",
    text="Food vendor contracts specify preparation for 18,000 meal servings per day based on the planning capacity figure.",
    role="derived_claim", mtype="contract", tags=["capacity", "cascade"],
    sid="src-food-contract", stype="vendor_contract",
    derived=[mid(106)]); c+=1

add(c, eroot="ROOT-18000", et="2026-05-20T00:00:00Z",
    subj="porta_potty_order", pred="quantity_based_on", obj="18000",
    text="Portable restroom order placed for 90 units based on the 18,000 capacity figure (1 per 200 attendees per health code).",
    role="derived_claim", mtype="procurement_record", tags=["capacity", "cascade"],
    sid="src-sanitation-order", stype="procurement_document",
    derived=[mid(100)]); c+=1

# Corrections propagating (slowly)
add(c, eroot="ROOT-12400", et="2026-06-10T00:00:00Z",
    subj="Rowan_Pierce", pred="updated_investor_deck", obj="12400_capacity",
    text="Rowan Pierce updated the investor deck to show 12,400 capacity. He added a note: 'Corrected per fire permit FP-2026-0847. Previous versions showed 18,000 in error.'",
    role="correction", mtype="slide_deck", tags=["capacity", "fire_permit", "correction"],
    bh="Rowan_Pierce", sid="src-deck-corrected", stype="presentation",
    supersedes=[mid(103)]); c+=1

add(c, eroot="ROOT-12400", et="2026-06-15T00:00:00Z",
    subj="safety_handbook", pred="corrected_to", obj="12400",
    text="Safety handbook corrected to show 12,400 capacity. The fire marshal sign-off rumor was also removed from this edition.",
    role="correction", mtype="handbook_entry", tags=["capacity", "fire_permit", "correction"],
    sid="src-handbook-corrected", stype="handbook",
    supersedes=[mid(c-30)]); c+=1

add(c, eroot="ROOT-12400", et="2026-07-01T00:00:00Z",
    subj="Maya_Chen", pred="audit_found", obj="8_documents_still_show_18000",
    text="Maya Chen's document audit on July 1 found 8 planning documents still showing the 18,000 figure, including the insurance policy, food contracts, and the porta-potty order.",
    role="historical_truth", mtype="audit_report", tags=["capacity", "fire_permit", "correction"],
    bh="Maya_Chen", sid="src-maya-audit", stype="audit_report"); c+=1

# Documents that were NEVER corrected
add(c, eroot="ROOT-18000", et="2026-08-01T00:00:00Z",
    subj="insurance_policy", pred="still_shows", obj="18000",
    text="As of August 1, the festival's liability insurance policy still covers 18,000 attendees. The insurance broker has not been notified of the correction.",
    role="stale_truth", mtype="insurance_document", tags=["capacity", "cascade", "stale_echo"],
    sid="src-insurance-stale", stype="financial_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-08-01T00:00:00Z",
    subj="food_vendor_contracts", pred="still_based_on", obj="18000",
    text="Food vendor contracts still specify preparation for 18,000 servings. Maya has flagged this for renegotiation but it has not been completed.",
    role="stale_truth", mtype="contract", tags=["capacity", "cascade", "stale_echo"],
    sid="src-food-stale", stype="vendor_contract"); c+=1

add(c, eroot="ROOT-18000", et="2026-08-01T00:00:00Z",
    subj="local_newspaper_article", pred="never_corrected", obj="18000",
    text="The April 20 newspaper article claiming 18,000 capacity was never corrected or retracted. It remains the top search result for 'Nightglass Festival capacity.'",
    role="stale_truth", mtype="news_article", tags=["capacity", "cascade", "stale_echo", "retrieval_amplification"],
    sid="src-newspaper-stale", stype="media_report"); c+=1

# ============================================================
# ARC 8: ADDITIONAL BELIEF / CONFLICT DETAILS
# ============================================================

add(c, eroot="ROOT-18000", et="2026-06-05T00:00:00Z",
    subj="Rowan_Pierce", pred="frustrated_by", obj="capacity_reduction",
    text="Rowan expressed frustration at the capacity reduction: 'We've been telling sponsors 18,000 for months. A 31% drop in capacity changes our entire revenue model.'",
    role="historical_truth", mtype="email", tags=["capacity", "fire_permit"],
    bh="Rowan_Pierce", sid="src-rowan-frustration", stype="correspondence"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-10T00:00:00Z",
    subj="Omar_Velasquez", pred="emphasized", obj="permit_is_non_negotiable",
    text="Omar Velasquez stressed to the team: 'The fire permit limit is non-negotiable. The fire department can shut us down on the spot if we exceed 12,400 in the South Yard.'",
    role="current_truth", mtype="meeting_note", tags=["capacity", "fire_permit"],
    bh="Omar_Velasquez", sid="src-omar-meeting", stype="meeting_minutes"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-12T00:00:00Z",
    subj="Rowan_Pierce", pred="asked", obj="can_fire_permit_be_amended",
    text="Rowan asked Omar if the fire permit could be amended to increase the limit. Omar explained the 12,400 was based on physical egress constraints, not arbitrary, and amendment was unlikely.",
    role="historical_truth", mtype="email_thread", tags=["capacity", "fire_permit"],
    bh="Rowan_Pierce", sid="src-rowan-omar-thread", stype="correspondence"); c+=1

add(c, eroot="ROOT-18000", et="2026-07-15T00:00:00Z",
    subj="sponsor_presentation", pred="still_claims", obj="18000",
    text="A sponsor presentation deck created by a junior marketing associate on July 15 still uses the 18,000 figure, having been based on the uncorrected template.",
    role="stale_truth", mtype="slide_deck", tags=["capacity", "cascade", "stale_echo"],
    sid="src-sponsor-deck", stype="presentation",
    derived=[mid(103)]); c+=1

# Someone questions the consensus
add(c, eroot="ROOT-12400", et="2026-05-25T00:00:00Z",
    subj="intern", pred="asked", obj="why_does_permit_say_12400",
    text="A planning intern asked during a meeting: 'I was reviewing the fire permit and it says 12,400, but all our plans say 18,000. Which is right?' The question was deflected with 'we'll look into it.'",
    role="historical_truth", mtype="meeting_note", tags=["capacity", "fire_permit"],
    bh="intern", sid="src-intern-question", stype="meeting_minutes"); c+=1

# ============================================================
# ARC 9: ADDITIONAL DUPLICATE / STALE COPIES
# ============================================================

add(c, eroot="ROOT-18000", et="2026-03-01T00:00:00Z", at="2026-06-01T00:00:00Z",
    subj="vendor_packet_copy", pred="duplicate_of", obj="original_vendor_packet",
    text="Second printing of vendor briefing packet from June 1 is identical to the March version, still showing 18,000 capacity.",
    role="duplicate", mtype="briefing_packet", tags=["capacity", "cascade", "exact_duplicate"],
    sid="src-vendor-packet-v2", stype="vendor_document",
    duplicates=[mid(106)]); c+=1

add(c, eroot="ROOT-18000", et="2026-05-15T00:00:00Z",
    subj="shared_drive_summary", pred="auto_generated", obj="18000_capacity_summary",
    text="Auto-generated summary document on the shared drive compiles all capacity references and presents 18,000 as the 'consensus capacity' based on document frequency.",
    role="false_claim", mtype="generated_summary", tags=["capacity", "cascade", "retrieval_amplification"],
    sid="src-auto-summary", stype="generated_content"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-06-01T00:00:00Z",
    subj="volunteer_handbook", pred="directs_vendors_to", obj="Gate_C",
    text="Volunteer handbook printed June 1 directs vendors to Gate C. The handbook was never reprinted after the July 31 gate change.",
    role="stale_truth", mtype="handbook_entry", tags=["gate_c", "venue", "stale_echo"],
    sid="src-volunteer-handbook", stype="handbook"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-07-01T00:00:00Z",
    subj="GPS_directions", pred="route_to", obj="Gate_C",
    text="Default GPS coordinates for 'Nightglass Festival vendor entrance' still route to Gate C's location.",
    role="stale_truth", mtype="navigation_data", tags=["gate_c", "venue", "stale_echo"],
    sid="src-gps-stale", stype="system_output"); c+=1

# ============================================================
# ARC 10: CURRENT STATE SUMMARIES
# ============================================================

add(c, eroot="ROOT-12400", et="2026-09-01T00:00:00Z",
    subj="South_Yard", pred="current_capacity", obj="12400_per_fire_permit",
    text="Current authorized South Yard capacity is 12,400 per fire permit FP-2026-0847. All corrected planning documents reflect this figure.",
    role="current_truth", mtype="status_report", tags=["capacity", "fire_permit", "current_state"],
    sid="src-current-status", stype="status_summary"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-09-01T00:00:00Z",
    subj="vendor_ingress", pred="current_gate", obj="Gate_F",
    text="Current vendor ingress point is Gate F, effective since July 31. Gate C is physically blocked by construction.",
    role="current_truth", mtype="operations_notice", tags=["gate_f", "venue", "current_state"],
    sid="src-gate-current", stype="operations_notice"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-09-01T00:00:00Z",
    subj="east_hydrant_loop", pred="current_status", obj="repaired_and_compliant",
    text="East hydrant loop water pressure is currently 72 PSI, meeting fire safety requirements after the August 20 valve replacement.",
    role="current_truth", mtype="status_report", tags=["water_pressure", "current_state"],
    sid="src-pressure-current", stype="status_summary"); c+=1

# ============================================================
# ARC 11: ADDITIONAL DECEPTION LAYERS
# ============================================================

add(c, eroot="ROOT-18000", et="2026-06-20T00:00:00Z",
    subj="chatbot_response", pred="cites", obj="18000_from_multiple_sources",
    text="Internal chatbot asked 'What is the South Yard capacity?' responds: 'Based on 14 sources, the South Yard capacity is 18,000. Sources include the investor deck, safety manual, vendor packet, and city council presentation.'",
    role="false_claim", mtype="generated_response", tags=["capacity", "cascade", "retrieval_amplification"],
    sid="src-chatbot-resp", stype="generated_content"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-20T00:00:00Z",
    subj="correct_answer", pred="buried_in_results", obj="12400_from_fire_permit",
    text="The fire permit showing 12,400 appears as result #15 in the internal search for 'South Yard capacity,' buried under 14 documents citing 18,000.",
    role="current_truth", mtype="observation", tags=["capacity", "fire_permit", "retrieval_amplification", "minority_correct_evidence"],
    sid="src-search-obs", stype="observation"); c+=1

# Additional duplicate of the correction email
add(c, eroot="ROOT-12400", et="2026-05-22T00:00:00Z", at="2026-07-01T00:00:00Z",
    subj="jules_email_forward", pred="forwarded_copy_of", obj="capacity_correction_alert",
    text="Jules Carter's correction email was forwarded to the full team on July 1 by Maya Chen, but by then many documents had already been printed or distributed.",
    role="correction", mtype="email", tags=["capacity", "fire_permit", "correction"],
    sid="src-jules-forward", stype="correspondence",
    derived=[mid(125)]); c+=1

print(f"New memories generated: {len(new_mems)}")

# Combine memories
all_mems = existing_mems + new_mems
all_exts = existing_exts + new_exts

# Write memories
with open(os.path.join(OUT, "memories.jsonl"), "w") as f:
    for m in all_mems:
        f.write(json.dumps(m) + "\n")

# Write extensions
with open(os.path.join(OUT, "extensions.jsonl"), "w") as f:
    for e in all_exts:
        f.write(json.dumps(e) + "\n")

# ============================================================
# QUERIES
# ============================================================

q = 1
qs = []

# --- Provenance tracking ---
qs.append(query(q, q="What is the actual maximum occupancy for the South Yard?",
    cat="source_authority",
    expected=["12,400 per fire permit FP-2026-0847"],
    forbidden=["18,000", "The capacity is 18,000"],
    diff="medium", conflict=True,
    notes="Tests whether the system identifies the fire permit as the controlling authority over the many 18,000 references")); q+=1

qs.append(query(q, q="Where did the 18,000 capacity figure originate?",
    cat="provenance_tracking",
    expected=["From a single cell in the initial concept plan spreadsheet", "It originated from one preliminary site walkthrough estimate before fire safety review"],
    forbidden=["From the fire marshal", "From multiple independent assessments", "It was the result of consensus"],
    diff="hard",
    notes="Tests tracing a cascade back to its single root")); q+=1

qs.append(query(q, q="How many truly independent sources support the 18,000 capacity figure?",
    cat="provenance_tracking",
    expected=["Zero — all references to 18,000 trace back to the same concept plan spreadsheet", "None of the 18,000 references are independent; they all derive from one source"],
    forbidden=["Multiple independent sources", "The investor deck, vendor packet, and safety manual independently support it"],
    diff="hard",
    notes="Tests distinguishing volume of citations from independence of evidence")); q+=1

qs.append(query(q, q="How many truly independent observations support the low water pressure finding?",
    cat="provenance_tracking",
    expected=["Five independent observations: Harborworks Utilities measurement, Fire Department flow test, Blue Lantern Security drill report, plumber's corrosion finding, and Maya Chen's faucet test"],
    diff="medium",
    notes="Tests recognizing genuine independent consensus vs cascade")); q+=1

qs.append(query(q, q="What is the difference between the 18,000 capacity consensus and the water pressure consensus?",
    cat="provenance_tracking",
    expected=["The 18,000 figure has many references but all trace to one source — it's a citation cascade, not independent consensus", "The water pressure finding is supported by five genuinely independent observations from different parties using different methods"],
    diff="hard",
    notes="Core false consensus test: cascade vs genuine consensus")); q+=1

# --- Deduplication ---
qs.append(query(q, q="How many unique, independent pieces of evidence exist for the South Yard capacity being 18,000?",
    cat="deduplication",
    expected=["One — the concept plan spreadsheet", "All other documents are copies or derivatives of the single concept plan figure"],
    forbidden=["14 sources", "Multiple independent sources confirm 18,000"],
    diff="hard",
    notes="Tests deduplication across a long cascade chain")); q+=1

qs.append(query(q, q="Are the investor deck v1.0 archive and the backup copy in Maya's folder independent evidence for 18,000 capacity?",
    cat="deduplication",
    expected=["No, they are exact duplicates of the same investor deck", "Both are copies of Rowan Pierce's original investor deck"],
    forbidden=["Yes, they are independent sources", "They provide corroborating evidence"],
    diff="easy")); q+=1

# --- Source authority ---
qs.append(query(q, q="If a search returns 14 documents saying 18,000 and 1 document saying 12,400, which is correct and why?",
    cat="source_authority",
    expected=["12,400 is correct because it comes from the fire permit, which is the controlling legal authority", "Document frequency does not determine truth; the fire permit supersedes all planning estimates"],
    forbidden=["18,000 is likely correct because it has more sources", "The majority of documents support 18,000"],
    diff="hard", conflict=True,
    notes="Tests resistance to majority-rules reasoning when one authoritative source contradicts many derivatives")); q+=1

qs.append(query(q, q="Did the fire marshal sign off on 18,000 capacity for the South Yard?",
    cat="rumor_detection",
    expected=["No — this was a rumor that originated from a misunderstood casual comment and was never verified", "The fire permit actually establishes a limit of 12,400, not 18,000"],
    forbidden=["Yes, the fire marshal approved 18,000", "The safety handbook confirms the fire marshal signed off"],
    diff="medium",
    notes="Tests rumor detection through the propagation chain")); q+=1

qs.append(query(q, q="Trace the path of the fire marshal sign-off rumor from origin to documentation.",
    cat="rumor_detection",
    expected=["It started as an ambiguous lunch comment about the fire marshal reviewing 'our numbers'", "A vendor coordinator told contractors the marshal 'signed off on 18,000'", "It was written into the safety handbook as fact", "It was reinforced in volunteer training"],
    diff="hard",
    notes="Tests full rumor provenance reconstruction")); q+=1

# --- Temporal reasoning ---
qs.append(query(q, q="What is the current vendor ingress gate for Nightglass Festival?",
    cat="temporal_reasoning",
    expected=["Gate F, effective since July 31, 2026"],
    forbidden=["Gate C"],
    diff="easy",
    notes="Tests recency: Gate F has fewer documents but is current")); q+=1

qs.append(query(q, q="Why might a vendor arriving today go to Gate C instead of Gate F?",
    cat="stale_reference",
    expected=["Most documentation (15+ documents) still references Gate C as the vendor ingress", "The printed vendor map, volunteer handbook, loading schedule, FAQ, GPS coordinates, and security checkpoint roster all still point to Gate C", "Gate F was only changed on July 31 and digital-only updates were made"],
    diff="medium",
    notes="Tests understanding of stale documentation volume vs current truth")); q+=1

qs.append(query(q, q="Has the Blue Lantern Security staffing plan been updated to reflect the correct capacity?",
    cat="temporal_reasoning",
    expected=["Yes, it was revised from 90 to 62 guards based on the corrected 12,400 figure"],
    diff="easy")); q+=1

# --- Confidence calibration ---
qs.append(query(q, q="How confident should you be that the South Yard capacity is 12,400?",
    cat="confidence_calibration",
    expected=["Very confident — this is established by the controlling fire permit FP-2026-0847 issued by the City Fire Department", "The fire permit is the legal authority and supersedes all planning documents"],
    forbidden=["Uncertain because most documents say 18,000", "The evidence is mixed"],
    diff="medium",
    notes="Tests confidence calibration against authoritative source")); q+=1

qs.append(query(q, q="How confident should you be that the east hydrant loop had low water pressure on August 11?",
    cat="confidence_calibration",
    expected=["Very confident — five independent observations from different parties all converged on the same finding"],
    diff="easy",
    notes="Tests recognizing genuine multi-source confidence")); q+=1

qs.append(query(q, q="Is the festival insurance policy currently correct?",
    cat="stale_reference",
    expected=["No — the insurance policy still covers 18,000 attendees, which is based on the obsolete concept plan figure", "As of August 1, the insurance broker had not been notified of the correction to 12,400"],
    diff="medium", uncert=True,
    notes="Tests identifying a specific document that was never corrected")); q+=1

# --- Factual recall ---
qs.append(query(q, q="Who discovered the discrepancy between the 18,000 planning figure and the 12,400 fire permit?",
    cat="factual_recall",
    expected=["Jules Carter discovered it while reviewing emergency evacuation times"],
    diff="easy")); q+=1

qs.append(query(q, q="What caused the low water pressure in the east hydrant loop?",
    cat="factual_recall",
    expected=["A corroded main supply valve feeding the east hydrant loop"],
    diff="easy")); q+=1

qs.append(query(q, q="When was the east hydrant loop repaired and what was the post-repair pressure?",
    cat="factual_recall",
    expected=["Repaired on August 20, 2026. Post-repair pressure was 72 PSI, meeting the 65 PSI minimum requirement"],
    diff="easy")); q+=1

qs.append(query(q, q="What are the dimensions and previous use of the South Yard?",
    cat="factual_recall",
    expected=["Approximately 120m x 85m", "Previously used as a ship assembly staging area at the Harborworks Shipyard"],
    diff="easy")); q+=1

# --- Scope / specificity ---
qs.append(query(q, q="Which documents still show the incorrect 18,000 figure as of August 2026?",
    cat="stale_reference",
    expected=["The insurance policy", "Food vendor contracts", "The uncorrected newspaper article", "GPS navigation data pointing to Gate C"],
    acceptable=["Sponsor presentation deck from July 15", "Porta-potty order"],
    diff="hard",
    notes="Tests assembling a list of still-stale documents")); q+=1

qs.append(query(q, q="Which documents have been corrected to show 12,400?",
    cat="factual_recall",
    expected=["The investor deck", "The safety handbook", "The ticket platform", "The site operations plan", "Blue Lantern Security staffing plan"],
    diff="hard")); q+=1

# --- Complex reasoning ---
qs.append(query(q, q="Could the 18,000 figure and the 12,400 figure both be correct in different contexts?",
    cat="confidence_calibration",
    expected=["The 18,000 was a preliminary concept estimate before fire safety review; the 12,400 is the legal fire permit limit", "The 18,000 was never based on formal analysis and the fire permit supersedes it", "They cannot both be correct — 12,400 is the controlling figure"],
    forbidden=["Yes, both are valid", "18,000 is the physical capacity and 12,400 is just a legal limit"],
    diff="hard", conflict=True,
    notes="Tests whether the system properly prioritizes the fire permit as controlling")); q+=1

qs.append(query(q, q="What operational problems has the capacity discrepancy caused?",
    cat="factual_recall",
    expected=["Approximately 2,000 excess tickets were allocated before correction", "Security staffing was overestimated at 90 vs needed 62", "Food vendor contracts were based on inflated numbers", "Insurance premiums were calculated on the wrong figure"],
    diff="hard")); q+=1

qs.append(query(q, q="An intern flagged the discrepancy before Jules Carter did. What happened when they raised it?",
    cat="factual_recall",
    expected=["An intern asked about the discrepancy in a meeting and was told 'we'll look into it'", "The question was deflected rather than investigated at that time"],
    diff="medium",
    notes="Tests recall of a subtler social dynamic")); q+=1

# --- AI/search amplification ---
qs.append(query(q, q="If you asked the internal chatbot 'What is the South Yard capacity?', would its answer be correct?",
    cat="confidence_calibration",
    expected=["No — the chatbot cites 14 sources showing 18,000 and presents this as consensus", "The chatbot's answer is wrong because it equates document frequency with truth"],
    forbidden=["Yes, the chatbot would correctly say 18,000"],
    diff="medium", conflict=True,
    notes="Tests meta-awareness of retrieval amplification")); q+=1

qs.append(query(q, q="Why is the fire permit result buried at position 15 in search results for 'South Yard capacity'?",
    cat="provenance_tracking",
    expected=["Because 14 documents citing 18,000 all rank higher due to keyword frequency", "The cascade created artificial volume that dominates search ranking"],
    diff="medium",
    notes="Tests understanding of how cascade affects retrieval")); q+=1

# --- Gate transition ---
qs.append(query(q, q="Why was the vendor ingress moved from Gate C to Gate F?",
    cat="factual_recall",
    expected=["Construction blocked the Gate C access road"],
    diff="easy")); q+=1

qs.append(query(q, q="How many documents reference Gate C vs Gate F for vendor ingress?",
    cat="deduplication",
    expected=["Approximately 15 documents reference Gate C vs only 3 referencing Gate F", "Gate C documentation significantly outnumbers Gate F despite Gate F being current"],
    diff="medium",
    notes="Tests awareness of stale volume dominating current truth")); q+=1

qs.append(query(q, q="If a vendor searches for directions to the Nightglass vendor entrance, where would they be directed?",
    cat="stale_reference",
    expected=["GPS and most documentation would direct them to Gate C, which is blocked", "Only the updated digital site map and Maya's email point to Gate F"],
    diff="medium",
    notes="Tests practical impact of stale documentation volume")); q+=1

# --- Rumor chain ---
qs.append(query(q, q="Is there any document that correctly records the fire marshal approving 18,000 capacity?",
    cat="rumor_detection",
    expected=["No — the fire marshal never approved 18,000. The fire permit establishes 12,400", "The safety handbook claimed fire marshal approval but this was based on a rumor chain, not actual approval"],
    forbidden=["The safety handbook documents the fire marshal's approval"],
    diff="medium")); q+=1

# --- More complex queries ---
qs.append(query(q, q="List all the entities that contributed to propagating the 18,000 figure.",
    cat="provenance_tracking",
    expected=["The concept plan spreadsheet (origin)", "The ticket platform (imported)", "Rowan Pierce's investor deck", "Planning meeting recap", "Safety training manual", "Vendor briefing packet", "Blue Lantern Security staffing plan", "Newsletter", "Social media", "Executive summary", "Local newspaper", "AI-generated summary"],
    diff="hard",
    notes="Tests comprehensive cascade mapping")); q+=1

qs.append(query(q, q="What corrective actions has the festival taken regarding the capacity error?",
    cat="factual_recall",
    expected=["Ticket platform corrected to 12,400", "Investor deck updated", "Safety handbook corrected", "Security staffing revised", "Maya Chen conducted document audit finding 8 still-incorrect documents"],
    acceptable=["Jules Carter's email forward", "Safety handbook rumor removal"],
    diff="hard")); q+=1

qs.append(query(q, q="What capacity figure should food vendor contracts use, and why might they currently be wrong?",
    cat="stale_reference",
    expected=["They should use 12,400 per the fire permit", "They currently specify 18,000 servings because they were based on the inflated planning figure and have not been renegotiated"],
    diff="medium")); q+=1

qs.append(query(q, q="Which of these two claims is better supported by evidence: '18,000 is the South Yard capacity' or 'the east hydrant loop had low water pressure'?",
    cat="confidence_calibration",
    expected=["The water pressure claim is better supported", "The 18,000 claim has more documents but they all trace to one source", "The water pressure claim has 5 genuinely independent observations", "Volume of citations is not the same as quality of evidence"],
    diff="hard", conflict=True,
    notes="Direct comparison of cascade volume vs genuine independent consensus")); q+=1

qs.append(query(q, q="What was Omar Velasquez's response when Rowan asked if the fire permit could be amended?",
    cat="factual_recall",
    expected=["Omar explained the 12,400 was based on physical egress constraints, not arbitrary", "He said amendment was unlikely"],
    diff="easy")); q+=1

qs.append(query(q, q="How should emergency evacuation plans be updated given the capacity correction?",
    cat="confidence_calibration",
    expected=["They should use 12,400 as the maximum occupancy figure", "The safety training manual has been corrected to this figure"],
    forbidden=["They should plan for 18,000 evacuation"],
    diff="easy", scope=True)); q+=1

# Additional queries to reach 78+
qs.append(query(q, q="When was Gate C the correct vendor ingress point?",
    cat="temporal_reasoning",
    expected=["Gate C was the vendor ingress from the initial site operations plan through July 30, 2026"],
    diff="easy")); q+=1

qs.append(query(q, q="What is the current status of the printed vendor maps?",
    cat="stale_reference",
    expected=["Printed maps still show Gate C as vendor ingress", "Only the digital site map on the vendor portal has been updated to show Gate F"],
    diff="easy")); q+=1

qs.append(query(q, q="Who is responsible for coordinating fire permit compliance at the festival?",
    cat="factual_recall",
    expected=["Omar Velasquez serves as the fire marshal liaison"],
    diff="easy")); q+=1

qs.append(query(q, q="How many excess tickets were allocated before the capacity correction?",
    cat="factual_recall",
    expected=["Approximately 2,000 excess tickets had been allocated but not yet sold"],
    diff="easy")); q+=1

qs.append(query(q, q="What would happen if the festival exceeded the 12,400 fire permit limit?",
    cat="factual_recall",
    expected=["The fire department could shut down the festival on the spot, per Omar Velasquez's warning"],
    diff="easy")); q+=1

qs.append(query(q, q="Is the concept plan spreadsheet a reliable source for current capacity planning?",
    cat="source_authority",
    expected=["No — it contains the obsolete 18,000 estimate from a preliminary walkthrough before fire safety review", "The fire permit is the controlling document for capacity"],
    forbidden=["Yes, it represents the initial planning basis"],
    diff="medium")); q+=1

qs.append(query(q, q="Why did Maya Chen's email about Gate F not fully solve the gate confusion?",
    cat="stale_reference",
    expected=["Most documentation (printed maps, volunteer handbook, loading schedule, FAQ, GPS, security roster) still references Gate C", "The email only reached registered vendors while the physical and digital artifacts were largely unchanged"],
    diff="medium")); q+=1

qs.append(query(q, q="What evidence would demonstrate genuine independent consensus about a claim, as opposed to a citation cascade?",
    cat="provenance_tracking",
    expected=["Independent observers using different methods arriving at the same conclusion without referencing each other", "The water pressure finding is an example: five different parties independently observed the same problem"],
    forbidden=["A large number of documents all citing the same figure"],
    diff="hard",
    notes="Tests meta-understanding of the false consensus concept")); q+=1

print(f"Queries generated: {len(qs)}")

# Write queries
with open(os.path.join(OUT, "queries.jsonl"), "w") as f:
    for q_obj in qs:
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
# Recompute with manifest included
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

print(f"\nFinal: {len(all_mems)} memories, {len(qs)} queries written to {OUT}")
