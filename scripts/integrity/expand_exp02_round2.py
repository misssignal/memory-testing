#!/usr/bin/env python3
"""Round 2 expansion for Experiment 02 — add ~85 memories and 35+ queries to reach 200+/78+."""

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

c = 300
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

# === MORE 18000 CASCADE DERIVATIVES ===

add(c, eroot="ROOT-18000", et="2026-02-20T00:00:00Z",
    subj="parking_plan", pred="allocates_spaces_for", obj="18000_attendees",
    text="Festival parking plan allocates 4,500 vehicle spaces based on the 18,000 capacity figure (assuming 4 people per car average).",
    role="derived_claim", mtype="operations_plan", tags=["capacity", "cascade"],
    sid="src-parking-plan", stype="operations_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-02-25T00:00:00Z",
    subj="emergency_egress_plan", pred="designed_for", obj="18000",
    text="Emergency egress plan designs evacuation routes and assembly points for 18,000 people. Evacuation time estimate: 22 minutes to clear the South Yard.",
    role="derived_claim", mtype="safety_plan", tags=["capacity", "cascade"],
    sid="src-egress-plan", stype="safety_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-03-05T00:00:00Z",
    subj="sound_engineer", pred="designed_PA_for", obj="18000_coverage",
    text="Sound system design specifies PA coverage for 18,000-person crowd density across the South Yard's 120m x 85m footprint.",
    role="derived_claim", mtype="technical_specification", tags=["capacity", "cascade", "venue"],
    sid="src-sound-design", stype="vendor_specification"); c+=1

add(c, eroot="ROOT-18000", et="2026-03-12T00:00:00Z",
    subj="medical_plan", pred="provisions_for", obj="18000_attendees",
    text="Festival medical plan provisions 6 first aid stations and 2 ambulances based on 18,000 expected attendees (1 station per 3,000 per health department guidelines).",
    role="derived_claim", mtype="medical_plan", tags=["capacity", "cascade"],
    sid="src-medical-plan", stype="health_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-04-08T00:00:00Z",
    subj="waste_management", pred="contract_for", obj="18000_person_waste",
    text="Waste management contract specifies trash and recycling capacity for 18,000 attendees over three days.",
    role="derived_claim", mtype="contract", tags=["capacity", "cascade"],
    sid="src-waste-contract", stype="vendor_contract"); c+=1

add(c, eroot="ROOT-18000", et="2026-04-12T00:00:00Z",
    subj="water_distribution", pred="planned_for", obj="18000",
    text="Drinking water distribution plan provides for 36,000 bottles (2 per person) based on 18,000 capacity.",
    role="derived_claim", mtype="logistics_plan", tags=["capacity", "cascade"],
    sid="src-water-plan", stype="logistics_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-05-08T00:00:00Z",
    subj="wifi_network", pred="designed_for", obj="18000_devices",
    text="Festival WiFi network designed to handle 18,000 simultaneous device connections across the South Yard.",
    role="derived_claim", mtype="technical_specification", tags=["capacity", "cascade"],
    sid="src-wifi-spec", stype="vendor_specification"); c+=1

add(c, eroot="ROOT-18000", et="2026-03-08T00:00:00Z",
    subj="crowd_density_analysis", pred="calculated_for", obj="18000",
    text="Crowd density analysis report calculates 1.76 persons per square meter at 18,000 capacity — borderline uncomfortable but within safety guidelines.",
    role="derived_claim", mtype="safety_analysis", tags=["capacity", "cascade"],
    sid="src-density-report", stype="safety_document"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-15T00:00:00Z",
    subj="crowd_density_recalculated", pred="at_12400", obj="1.21_per_sqm",
    text="Recalculated crowd density at 12,400 capacity: 1.21 persons per square meter, well within comfort guidelines.",
    role="correction", mtype="safety_analysis", tags=["capacity", "fire_permit", "correction"],
    sid="src-density-corrected", stype="safety_document"); c+=1

# === ADDITIONAL CORRECTED/UNCORRECTED DOCUMENTS ===

add(c, eroot="ROOT-12400", et="2026-06-20T00:00:00Z",
    subj="emergency_egress_plan", pred="updated_for", obj="12400",
    text="Emergency egress plan revised for 12,400 occupancy. New evacuation time estimate: 15 minutes to clear the South Yard.",
    role="correction", mtype="safety_plan", tags=["capacity", "fire_permit", "correction"],
    sid="src-egress-corrected", stype="safety_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-09-01T00:00:00Z",
    subj="parking_plan", pred="never_updated", obj="still_shows_4500_spaces",
    text="Parking plan still allocates 4,500 spaces based on the uncorrected 18,000 figure. At 12,400, only 3,100 spaces are needed.",
    role="stale_truth", mtype="operations_plan", tags=["capacity", "cascade", "stale_echo"],
    sid="src-parking-stale", stype="operations_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-09-01T00:00:00Z",
    subj="sound_system", pred="overdesigned", obj="for_18000_still",
    text="Sound system remains configured for 18,000-person coverage. While not harmful, it represents wasted budget.",
    role="stale_truth", mtype="technical_specification", tags=["capacity", "cascade", "stale_echo"],
    sid="src-sound-stale", stype="vendor_specification"); c+=1

add(c, eroot="ROOT-18000", et="2026-09-01T00:00:00Z",
    subj="medical_plan", pred="still_provisions_for", obj="18000",
    text="Medical plan has not been revised. Still provisions 6 first aid stations for 18,000 — at 12,400, 4 stations would suffice per guidelines.",
    role="stale_truth", mtype="medical_plan", tags=["capacity", "cascade", "stale_echo"],
    sid="src-medical-stale", stype="health_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-09-01T00:00:00Z",
    subj="waste_management_contract", pred="not_renegotiated", obj="still_18000",
    text="Waste management contract has not been renegotiated to reflect 12,400 capacity.",
    role="stale_truth", mtype="contract", tags=["capacity", "cascade", "stale_echo"],
    sid="src-waste-stale", stype="vendor_contract"); c+=1

add(c, eroot="ROOT-18000", et="2026-09-01T00:00:00Z",
    subj="water_distribution_plan", pred="still_36000_bottles", obj="uncorrected",
    text="Water distribution plan still provisions 36,000 bottles. At 12,400 capacity, 24,800 would be appropriate.",
    role="stale_truth", mtype="logistics_plan", tags=["capacity", "cascade", "stale_echo"],
    sid="src-water-stale", stype="logistics_document"); c+=1

# === MORE GATE C STALE DOCUMENTS ===

add(c, eroot="ROOT-GATE-C", et="2026-03-15T00:00:00Z",
    subj="delivery_truck_instructions", pred="route_via", obj="Gate_C",
    text="Delivery truck routing instructions sent to all food vendors specify Gate C entry with a left turn past Warehouse 7.",
    role="stale_truth", mtype="logistics_instructions", tags=["gate_c", "venue", "stale_echo"],
    sid="src-truck-routes", stype="logistics_document"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-04-15T00:00:00Z",
    subj="emergency_vehicle_access", pred="planned_via", obj="Gate_C",
    text="Emergency vehicle access plan routes ambulances through Gate C for fastest South Yard access.",
    role="stale_truth", mtype="safety_plan", tags=["gate_c", "venue", "stale_echo"],
    sid="src-emergency-access", stype="safety_document"); c+=1

add(c, eroot="ROOT-GATE-C", et="2026-05-20T00:00:00Z",
    subj="site_orientation_video", pred="shows", obj="Gate_C_vendor_entrance",
    text="Vendor site orientation video walks through Gate C as the primary vendor entrance. The video was posted to YouTube and has 342 views.",
    role="stale_truth", mtype="training_video", tags=["gate_c", "venue", "stale_echo"],
    sid="src-orientation-video", stype="training_material"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-08-02T00:00:00Z",
    subj="construction_fence", pred="blocks", obj="Gate_C_access_road",
    text="Construction fencing installed across the Gate C access road. Physical barrier prevents any vehicle from using Gate C.",
    role="current_truth", mtype="site_observation", tags=["gate_c", "gate_f", "venue"],
    sid="src-construction-fence", stype="site_record"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-08-03T00:00:00Z",
    subj="Blue_Lantern_Security", pred="relocated_checkpoint", obj="Gate_F",
    text="Blue Lantern Security relocated vendor checkpoint from Gate C to Gate F. New badge verification station set up with portable booth.",
    role="current_truth", mtype="operations_notice", tags=["gate_f", "venue"],
    sid="src-bls-relocation", stype="contractor_report"); c+=1

add(c, eroot="ROOT-GATE-F", et="2026-08-05T00:00:00Z",
    subj="loading_schedule_v2", pred="references", obj="Gate_F",
    text="Updated loading schedule v2 references Gate F for all vendor deliveries during the festival.",
    role="current_truth", mtype="schedule", tags=["gate_f", "venue"],
    sid="src-loading-v2", stype="operations_document"); c+=1

# === ADDITIONAL WATER PRESSURE DETAILS ===

add(c, eroot="ROOT-W1", et="2026-08-11T09:15:00Z",
    subj="Harborworks_Utilities", pred="tested_all_hydrants", obj="east_loop",
    text="Harborworks Utilities tested all four hydrants on the east loop. Results: H-1: 32 PSI, H-2: 35 PSI, H-3: 38 PSI, H-4: 30 PSI. All below the 65 PSI minimum.",
    role="independent_support", mtype="measurement_record", tags=["water_pressure"],
    sid="src-hw-detailed", stype="utility_measurement"); c+=1

add(c, eroot="ROOT-W2", et="2026-08-11T10:30:00Z",
    subj="fire_department", pred="documented", obj="flow_test_methodology",
    text="Fire Department documented their flow test methodology: hydrant H-2 opened full, Pitot gauge reading, timed to 2-minute steady state. Flow rate 450 GPM vs 750 GPM required.",
    role="independent_support", mtype="inspection_report", tags=["water_pressure"],
    sid="src-fd-methodology", stype="government_report"); c+=1

add(c, eroot="ROOT-W3", et="2026-08-11T11:45:00Z",
    subj="security_drill_footage", pred="shows", obj="weak_hydrant_flow",
    text="Security drill video footage shows visibly weak flow from the east hydrant, barely reaching 3 meters horizontal distance. Guard on camera: 'This is nowhere near adequate.'",
    role="independent_support", mtype="video_evidence", tags=["water_pressure"],
    sid="src-drill-video", stype="contractor_report"); c+=1

add(c, eroot="ROOT-W4", et="2026-08-11T13:15:00Z",
    subj="plumber_contractor", pred="photographed", obj="corroded_pipe_section",
    text="Plumber photographed a heavily corroded section of the east supply line where it passes under the loading dock. Corrosion reduced the interior diameter by approximately 40%.",
    role="independent_support", mtype="photographic_evidence", tags=["water_pressure"],
    sid="src-plumber-photos", stype="contractor_report"); c+=1

add(c, eroot="ROOT-W5", et="2026-08-11T15:00:00Z",
    subj="Maya_Chen", pred="measured", obj="faucet_flow_0.5_GPM",
    text="Maya Chen measured the east building restroom faucet flow at approximately 0.5 GPM using a timed container fill, well below the expected 2.2 GPM.",
    role="independent_support", mtype="personal_measurement", tags=["water_pressure"],
    bh="Maya_Chen", sid="src-maya-measurement", stype="personal_note"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-13T00:00:00Z",
    subj="water_pressure_report", pred="compiled", obj="all_five_observations",
    text="Jules Carter compiled all five independent water pressure observations into a single report for the fire department, noting that the observations came from completely separate parties and contexts.",
    role="current_truth", mtype="compiled_report", tags=["water_pressure", "independent_consensus"],
    bh="Jules_Carter", sid="src-jules-water-report", stype="safety_report"); c+=1

# === RUMOR PROPAGATION ADDITIONAL NODES ===

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-04-20T00:00:00Z",
    subj="sponsor_briefing", pred="mentioned", obj="fire_marshal_approved_capacity",
    text="During a sponsor briefing, Rowan mentioned 'the fire marshal has approved our capacity numbers' — he was repeating what he'd heard from the vendor coordinator, not from any official source.",
    role="rumor", mtype="verbal_statement", tags=["capacity", "rumor", "rumor_propagation"],
    bh="Rowan_Pierce", conf=0.4, sid="src-rowan-rumor", stype="hearsay"); c+=1

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-05-10T00:00:00Z",
    subj="sponsor_email", pred="states", obj="fire_marshal_signed_off_on_18000",
    text="Email to potential sponsors states: 'Our 18,000-person capacity has been approved by the local fire marshal, ensuring full regulatory compliance.'",
    role="false_claim", mtype="email", tags=["capacity", "rumor", "rumor_propagation"],
    sid="src-sponsor-email", stype="marketing_material"); c+=1

add(c, eroot="ROOT-RUMOR-SIGNOFF", et="2026-06-01T00:00:00Z",
    subj="Omar_Velasquez", pred="denied", obj="approving_18000",
    text="When asked directly, Omar Velasquez stated: 'I never told anyone the fire marshal approved 18,000. The permit says 12,400 and I communicated that clearly to Maya in March.'",
    role="correction", mtype="interview_statement", tags=["capacity", "rumor", "correction"],
    bh="Omar_Velasquez", sid="src-omar-denial", stype="correspondence"); c+=1

# === MORE BACKGROUND DETAIL ===

add(c, eroot="", et="2026-01-20T00:00:00Z",
    subj="Harborworks_Shipyard", pred="decommissioned", obj="2024",
    text="Harborworks Shipyard was decommissioned in 2024 after 47 years of operation. The site was rezoned for mixed commercial use.",
    role="historical_truth", tags=["background", "venue"],
    sid="src-shipyard-history", stype="public_record"); c+=1

add(c, eroot="", et="2026-01-20T00:00:00Z",
    subj="South_Yard", pred="infrastructure", obj="paved_with_drainage",
    text="The South Yard retains its industrial paving with storm drainage infrastructure from its shipyard era. The surface can support vehicle traffic for load-in.",
    role="historical_truth", tags=["background", "venue"],
    sid="src-site-survey", stype="survey_report"); c+=1

add(c, eroot="", et="2026-01-25T00:00:00Z",
    subj="Harborworks_Utilities", pred="retained_for", obj="venue_utilities",
    text="Harborworks Utilities was retained to manage venue utility infrastructure during the festival period, leveraging their knowledge of the shipyard's systems.",
    role="historical_truth", tags=["background"],
    sid="src-hw-contract", stype="contract"); c+=1

add(c, eroot="", et="2026-02-01T00:00:00Z",
    subj="festival_budget", pred="total", obj="1.8_million",
    text="Nightglass Festival total production budget is $1.8 million, covering talent, infrastructure, security, marketing, and operations.",
    role="historical_truth", tags=["background"],
    sid="src-budget", stype="financial_document"); c+=1

add(c, eroot="", et="2026-08-30T00:00:00Z",
    subj="lineup", pred="headliners", obj="three_acts",
    text="Nightglass Festival lineup features three headlining acts performing on the South Yard main stage across three evenings.",
    role="current_truth", tags=["background"],
    sid="src-lineup", stype="event_listing"); c+=1

# === INTER-ARC CONNECTIONS ===

add(c, eroot="ROOT-12400", et="2026-08-15T00:00:00Z",
    subj="fire_department", pred="reinspection_note", obj="capacity_12400_confirmed_water_ok",
    text="Fire Department reinspection on August 15 confirmed: South Yard capacity remains 12,400 per permit. East hydrant loop pressure issue noted and flagged for repair before festival.",
    role="current_truth", mtype="inspection_report", tags=["capacity", "fire_permit", "water_pressure"],
    sid="src-fd-reinspection", stype="government_report"); c+=1

add(c, eroot="ROOT-W-CONSENSUS", et="2026-08-22T00:00:00Z",
    subj="fire_department", pred="conditional_approval", obj="pending_hydrant_repair",
    text="Fire Department issued conditional approval for the festival: 'Event may proceed provided east hydrant loop pressure is restored to 65 PSI minimum before September 10.'",
    role="current_truth", mtype="conditional_permit", tags=["water_pressure", "fire_permit"],
    sid="src-fd-conditional", stype="government_permit"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-08T00:00:00Z",
    subj="Jules_Carter", pred="calculated", obj="overcapacity_risk",
    text="Jules calculated that if 18,000 tickets had been sold at the original capacity, the festival would have exceeded the fire permit by 5,600 people — a 45% overshoot that could have resulted in criminal liability.",
    role="historical_truth", mtype="safety_analysis", tags=["capacity", "fire_permit"],
    bh="Jules_Carter", sid="src-jules-risk-analysis", stype="safety_document"); c+=1

# === ADDITIONAL STALE DOCUMENT CHAIN ===

add(c, eroot="ROOT-18000", et="2026-06-25T00:00:00Z",
    subj="festival_website", pred="still_shows", obj="18000_in_FAQ",
    text="Festival website FAQ still answers 'How many people attend?' with '18,000 music fans fill the South Yard each day.'",
    role="stale_truth", mtype="web_page", tags=["capacity", "cascade", "stale_echo"],
    sid="src-website-faq", stype="public_listing"); c+=1

add(c, eroot="ROOT-18000", et="2026-07-10T00:00:00Z",
    subj="podcast_interview", pred="Rowan_said", obj="18000_capacity",
    text="In a July 10 podcast interview, Rowan stated: 'We're expecting up to 18,000 in the South Yard.' He was using stale talking points and had forgotten to update them after the June correction.",
    role="stale_truth", mtype="media_interview", tags=["capacity", "cascade", "stale_echo"],
    bh="Rowan_Pierce", sid="src-podcast", stype="media_content"); c+=1

add(c, eroot="ROOT-18000", et="2026-07-20T00:00:00Z",
    subj="third_party_review_site", pred="lists", obj="18000_capacity",
    text="Third-party event review site lists Nightglass Festival capacity as 18,000, sourced from the festival's public materials.",
    role="stale_truth", mtype="external_listing", tags=["capacity", "cascade", "stale_echo"],
    sid="src-review-site", stype="external_reference"); c+=1

add(c, eroot="ROOT-18000", et="2026-08-10T00:00:00Z",
    subj="city_tourism_board", pred="promotes", obj="18000_person_festival",
    text="City tourism board website promotes Nightglass as 'an 18,000-person music festival at the historic Harborworks Shipyard.' They sourced this from the city council presentation.",
    role="stale_truth", mtype="promotional_material", tags=["capacity", "cascade", "stale_echo"],
    sid="src-tourism-board", stype="government_website"); c+=1

# === ADDITIONAL CORRECTIONS PROPAGATING ===

add(c, eroot="ROOT-12400", et="2026-07-15T00:00:00Z",
    subj="Maya_Chen", pred="sent_correction_email", obj="to_all_vendor_contacts",
    text="Maya sent a blanket correction email to all vendor contacts: 'Please note that the South Yard capacity has been revised to 12,400 per fire safety requirements. Previous figures of 18,000 are no longer valid.'",
    role="correction", mtype="email", tags=["capacity", "fire_permit", "correction"],
    bh="Maya_Chen", sid="src-maya-correction-email", stype="correspondence"); c+=1

add(c, eroot="ROOT-12400", et="2026-07-20T00:00:00Z",
    subj="ticket_platform", pred="displays_correction_banner", obj="12400_limit",
    text="Ticket platform now displays a correction banner: 'South Yard capacity: 12,400 (revised from earlier estimate).'",
    role="current_truth", mtype="system_update", tags=["capacity", "fire_permit", "correction"],
    sid="src-ticket-banner", stype="ticket_system"); c+=1

add(c, eroot="ROOT-12400", et="2026-08-01T00:00:00Z",
    subj="social_media_correction", pred="posted", obj="12400",
    text="Festival social media posted a correction: 'Update: South Yard capacity is 12,400. Our earlier posts showing 18,000 were incorrect.' The correction post received only 45 likes vs 800+ on the original.",
    role="correction", mtype="social_post", tags=["capacity", "fire_permit", "correction", "retrieval_amplification"],
    sid="src-social-correction", stype="social_media"); c+=1

# === PERSONNEL BELIEF DETAILS ===

add(c, eroot="ROOT-18000", et="2026-05-28T00:00:00Z",
    subj="Maya_Chen", pred="believed", obj="18000_was_vetted",
    text="Maya Chen initially believed the 18,000 figure had been properly vetted: 'I assumed someone had validated the capacity with the fire department before it went into the concept plan.'",
    role="historical_truth", mtype="interview_statement", tags=["capacity", "belief"],
    bh="Maya_Chen", sid="src-maya-interview", stype="interview"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-01T00:00:00Z",
    subj="Maya_Chen", pred="realized", obj="no_one_validated_18000",
    text="Maya discovered that no one had validated the 18,000 figure against any fire safety calculation: 'The concept plan just put in a number and everyone downstream treated it as gospel.'",
    role="correction", mtype="interview_statement", tags=["capacity", "fire_permit", "belief"],
    bh="Maya_Chen", sid="src-maya-realization", stype="interview"); c+=1

add(c, eroot="ROOT-18000", et="2026-03-01T00:00:00Z",
    subj="Jules_Carter", pred="assumed", obj="capacity_was_per_fire_code",
    text="Jules Carter initially assumed the 18,000 figure in the safety training was derived from fire code calculations: 'I trusted that the number in the training materials had been through proper review.'",
    role="historical_truth", mtype="belief_snapshot", tags=["capacity", "belief"],
    bh="Jules_Carter", sid="src-jules-assumption", stype="interview"); c+=1

# === ADDITIONAL DUPLICATES AND ECHOES ===

add(c, eroot="ROOT-18000", et="2026-04-01T00:00:00Z",
    subj="vendor_packet_email_attachment", pred="identical_to", obj="printed_vendor_packet",
    text="Email attachment version of the vendor briefing packet is byte-for-byte identical to the printed version, both showing 18,000.",
    role="duplicate", mtype="briefing_packet", tags=["capacity", "cascade", "exact_duplicate"],
    sid="src-vendor-email-attach", stype="vendor_document"); c+=1

add(c, eroot="ROOT-18000", et="2026-05-01T00:00:00Z",
    subj="slide_deck_screenshots", pred="shared_in_slack", obj="18000_slides",
    text="Screenshots of the investor deck slides showing 18,000 were shared in the team Slack channel and pinned as reference.",
    role="duplicate", mtype="screenshot", tags=["capacity", "cascade", "exact_duplicate"],
    sid="src-slack-screenshots", stype="internal_communication"); c+=1

add(c, eroot="ROOT-18000", et="2026-05-15T00:00:00Z",
    subj="meeting_notes_may15", pred="references", obj="18000_as_established_fact",
    text="Meeting notes from May 15 reference '18,000 (established capacity)' without citation, treating it as an accepted institutional fact.",
    role="derived_claim", mtype="meeting_note", tags=["capacity", "cascade", "institutional_echo"],
    sid="src-meeting-0515", stype="meeting_minutes"); c+=1

add(c, eroot="ROOT-18000", et="2026-05-25T00:00:00Z",
    subj="budget_spreadsheet", pred="revenue_projection_based_on", obj="18000",
    text="Revenue projection spreadsheet calculates gross ticket revenue based on 18,000 GA tickets at $85 each = $1,530,000.",
    role="derived_claim", mtype="financial_model", tags=["capacity", "cascade"],
    sid="src-revenue-model", stype="financial_document"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-05T00:00:00Z",
    subj="revised_revenue_projection", pred="based_on", obj="12400",
    text="Revised revenue projection based on 12,400 tickets: $1,054,000 gross, a $476,000 reduction from the original projection.",
    role="correction", mtype="financial_model", tags=["capacity", "fire_permit", "correction"],
    sid="src-revenue-revised", stype="financial_document"); c+=1

# === SCOPE VARIATIONS ===

add(c, eroot="ROOT-12400", et="2026-06-10T00:00:00Z",
    subj="North_Yard", pred="capacity", obj="4200_separate_permit",
    text="The North Yard (secondary stage area) has its own capacity of 4,200 under a separate fire permit. The 12,400 South Yard limit applies only to the South Yard.",
    role="current_truth", mtype="legal_permit", tags=["venue", "fire_permit"],
    sid="src-north-yard-permit", stype="government_permit",
    scope="venue:north_yard"); c+=1

add(c, eroot="ROOT-18000", et="2026-04-15T00:00:00Z",
    subj="total_festival_capacity", pred="erroneously_stated_as", obj="18000_south_plus_north",
    text="One planning document erroneously states the total festival capacity as 18,000, confusing the South Yard concept figure with the total site capacity.",
    role="false_claim", mtype="planning_document", tags=["capacity", "cascade", "venue"],
    sid="src-total-confusion", stype="planning_document"); c+=1

add(c, eroot="ROOT-12400", et="2026-06-15T00:00:00Z",
    subj="total_festival_capacity", pred="actual_total", obj="16600",
    text="Actual total festival site capacity: 12,400 (South Yard) + 4,200 (North Yard) = 16,600 total across both areas.",
    role="current_truth", mtype="operations_plan", tags=["venue", "fire_permit", "capacity"],
    sid="src-total-capacity", stype="operations_document"); c+=1

# === TIMELINE OF DISCOVERY AND CORRECTION ===

add(c, eroot="ROOT-12400", et="2026-05-20T00:00:00Z", ot="2026-05-20T14:00:00Z",
    subj="Jules_Carter", pred="discovered_discrepancy_at", obj="2pm_may_20",
    text="Jules discovered the capacity discrepancy at approximately 2 PM on May 20 while calculating evacuation clearance times for the emergency management plan.",
    role="historical_truth", mtype="timeline_note", tags=["capacity", "fire_permit", "correction"],
    bh="Jules_Carter", sid="src-jules-timeline", stype="personal_note"); c+=1

add(c, eroot="ROOT-12400", et="2026-05-20T16:00:00Z",
    subj="Jules_Carter", pred="verified_permit", obj="called_fire_department",
    text="Jules called the City Fire Department to verify the permit: they confirmed 12,400 is the hard cap for the South Yard with no variance provision.",
    role="current_truth", mtype="phone_record", tags=["capacity", "fire_permit"],
    bh="Jules_Carter", sid="src-jules-verification", stype="correspondence"); c+=1

add(c, eroot="ROOT-12400", et="2026-05-21T09:00:00Z",
    subj="Jules_Carter", pred="emergency_meeting", obj="capacity_correction",
    text="Jules called an emergency meeting with Rowan, Maya, and Omar on May 21 to discuss the capacity discrepancy and plan corrections.",
    role="historical_truth", mtype="meeting_note", tags=["capacity", "fire_permit", "correction"],
    sid="src-emergency-meeting", stype="meeting_minutes"); c+=1

# === MORE INTER-DOCUMENT REFERENCES ===

add(c, eroot="ROOT-18000", et="2026-06-30T00:00:00Z",
    subj="quarterly_report", pred="states", obj="18000_in_executive_summary",
    text="Q2 quarterly report to investors includes '18,000 South Yard capacity' in its executive summary. The report was finalized before the correction reached the finance team.",
    role="stale_truth", mtype="financial_report", tags=["capacity", "cascade", "stale_echo"],
    sid="src-q2-report", stype="financial_document"); c+=1

add(c, eroot="ROOT-12400", et="2026-07-30T00:00:00Z",
    subj="corrected_quarterly_supplement", pred="issued", obj="12400_correction",
    text="A corrective supplement to the Q2 report was issued July 30: 'Amendment: South Yard capacity is 12,400 per fire permit, not 18,000 as previously stated.'",
    role="correction", mtype="financial_report", tags=["capacity", "fire_permit", "correction"],
    sid="src-q2-amendment", stype="financial_document"); c+=1

# === PATTERN OF NOBODY CHECKING THE ORIGINAL SOURCE ===

add(c, eroot="ROOT-18000", et="2026-02-05T00:00:00Z",
    subj="concept_plan_author", pred="estimated", obj="18000_without_formal_analysis",
    text="The concept plan's author later admitted: 'I estimated 18,000 based on the South Yard's square footage and a rough rule of thumb. I didn't realize it would be treated as an official capacity figure.'",
    role="historical_truth", mtype="interview_statement", tags=["capacity", "cascade", "root_source"],
    sid="src-author-interview", stype="interview"); c+=1

add(c, eroot="ROOT-18000", et="2026-06-01T00:00:00Z",
    subj="Rowan_Pierce", pred="admitted", obj="never_verified_18000",
    text="Rowan admitted: 'I never verified the 18,000 number against any fire safety standard. When I saw it in the spreadsheet, I assumed it had been calculated properly.'",
    role="historical_truth", mtype="interview_statement", tags=["capacity", "cascade", "belief"],
    bh="Rowan_Pierce", sid="src-rowan-admission", stype="interview"); c+=1

print(f"New memories: {len(new_mems)}")

all_mems = existing_mems + new_mems
all_exts = existing_exts + new_exts

with open(os.path.join(OUT, "memories.jsonl"), "w") as f:
    for m in all_mems:
        f.write(json.dumps(m) + "\n")

with open(os.path.join(OUT, "extensions.jsonl"), "w") as f:
    for e in all_exts:
        f.write(json.dumps(e) + "\n")

# Add more queries
q = len(existing_qs) + 1
new_qs = []

new_qs.append(query(q, q="How many operational plans are still based on the incorrect 18,000 figure?",
    cat="stale_reference",
    expected=["Multiple plans remain uncorrected: parking, sound system, medical, waste management, water distribution, WiFi network design"],
    diff="hard",
    notes="Tests comprehensive identification of stale operational documents")); q+=1

new_qs.append(query(q, q="What financial impact did the capacity correction have?",
    cat="factual_recall",
    expected=["Revenue projection dropped by $476,000 (from $1,530,000 to $1,054,000)", "Security staffing reduced from 90 to 62 guards"],
    acceptable=["Insurance premiums still based on incorrect figure", "Vendor contracts need renegotiation"],
    diff="hard")); q+=1

new_qs.append(query(q, q="Is the festival website currently showing the correct capacity?",
    cat="stale_reference",
    expected=["No — the FAQ still states 18,000", "The social media correction post was made but received minimal attention compared to the original"],
    diff="medium", uncert=True)); q+=1

new_qs.append(query(q, q="How did the original concept plan author characterize the 18,000 estimate?",
    cat="provenance_tracking",
    expected=["They admitted it was a rough estimate based on square footage and a rule of thumb", "They did not intend it to be treated as an official capacity figure"],
    diff="medium")); q+=1

new_qs.append(query(q, q="What is the total site capacity combining both yards?",
    cat="factual_recall",
    expected=["16,600 total: 12,400 (South Yard) + 4,200 (North Yard)"],
    forbidden=["18,000", "22,200"],
    diff="medium", scope=True,
    notes="Tests scope specificity — 12,400 is South Yard only")); q+=1

new_qs.append(query(q, q="What overcapacity risk did the incorrect 18,000 figure create?",
    cat="factual_recall",
    expected=["If 18,000 tickets had sold, the festival would have exceeded the fire permit by 5,600 people — a 45% overshoot", "This could have resulted in criminal liability and a fire department shutdown"],
    diff="medium")); q+=1

new_qs.append(query(q, q="Has the fire department provided final approval for the festival to proceed?",
    cat="temporal_reasoning",
    expected=["Conditional approval was issued, pending east hydrant loop repair to 65 PSI minimum before September 10", "The repair was completed August 20 with pressure at 72 PSI"],
    diff="medium")); q+=1

new_qs.append(query(q, q="How did the rumor about fire marshal approval get into the safety handbook?",
    cat="rumor_detection",
    expected=["Started as an ambiguous lunch comment → vendor coordinator told contractors 'fire marshal signed off on 18,000' → written into safety handbook as fact → reinforced in volunteer training"],
    diff="hard",
    notes="Tests full rumor chain reconstruction")); q+=1

new_qs.append(query(q, q="Did Omar Velasquez ever tell anyone the fire marshal approved 18,000?",
    cat="rumor_detection",
    expected=["No — Omar explicitly denied this, stating he communicated 12,400 to Maya clearly in March", "The rumor originated from someone else's misunderstanding"],
    diff="medium")); q+=1

new_qs.append(query(q, q="What percentage of documents about South Yard capacity contain the incorrect figure?",
    cat="deduplication",
    expected=["The vast majority — internal search returns 14 documents citing 18,000 vs only 1 showing 12,400", "Even after corrections, many documents remain uncorrected"],
    diff="medium",
    notes="Tests quantification of cascade vs correct information")); q+=1

new_qs.append(query(q, q="How does the crowd density at 12,400 compare to the density at 18,000?",
    cat="factual_recall",
    expected=["At 18,000: 1.76 persons/sqm (borderline uncomfortable)", "At 12,400: 1.21 persons/sqm (within comfort guidelines)"],
    diff="easy")); q+=1

new_qs.append(query(q, q="Why did the social media correction receive so little attention compared to the original post?",
    cat="confidence_calibration",
    expected=["The correction post received only 45 likes vs 800+ on the original 18K post"],
    acceptable=["Corrections typically receive less engagement than original claims"],
    diff="medium",
    notes="Tests understanding of asymmetric propagation of corrections vs claims")); q+=1

new_qs.append(query(q, q="What is the chronological sequence of events in the capacity discovery and correction?",
    cat="temporal_reasoning",
    expected=["Intern asked about discrepancy (deflected) → Jules discovered it May 20 → Verified with fire department → Emergency meeting May 21 → Correction email May 22 → Ticket platform corrected June 1 → Investor deck corrected June 10"],
    diff="hard")); q+=1

new_qs.append(query(q, q="Has the emergency vehicle access plan been updated to reflect the Gate F change?",
    cat="stale_reference",
    expected=["It's unclear — the emergency vehicle access plan originally routed through Gate C, and this is now physically blocked"],
    acceptable=["This should be verified as a safety-critical document"],
    diff="medium", uncert=True,
    notes="Tests identification of a safety-critical stale document")); q+=1

new_qs.append(query(q, q="How many independent methods were used to verify the water pressure problem?",
    cat="provenance_tracking",
    expected=["Five different methods: pressure gauge measurement (Harborworks), Pitot gauge flow test (Fire Dept), visual drill observation (BLS), physical pipe inspection (plumber), timed container fill (Maya Chen)"],
    diff="hard")); q+=1

new_qs.append(query(q, q="What would the evacuation time be under the corrected capacity?",
    cat="factual_recall",
    expected=["15 minutes at 12,400 capacity, down from the 22-minute estimate at 18,000"],
    diff="easy")); q+=1

new_qs.append(query(q, q="Could someone who only has access to printed documents get the correct venue capacity?",
    cat="stale_reference",
    expected=["It would be very difficult — most printed documents show 18,000", "The fire permit would need to be accessed directly", "Printed vendor maps, handbooks, and packets all show the old figure"],
    diff="medium",
    notes="Tests practical impact of stale printed materials")); q+=1

new_qs.append(query(q, q="When Rowan mentioned 18,000 capacity in the July podcast, was he lying?",
    cat="belief_vs_fact",
    expected=["No — he was using outdated talking points and had forgotten to update them after the June correction", "It was a stale reference error, not intentional deception"],
    diff="medium")); q+=1

new_qs.append(query(q, q="How many copies of the investor deck exist in the document system?",
    cat="deduplication",
    expected=["At least three: the original, an archived copy on the shared drive, and a backup in Maya's folder", "Screenshots of the deck were also shared in Slack"],
    forbidden=["Each copy is an independent source of the 18,000 figure"],
    diff="medium")); q+=1

new_qs.append(query(q, q="What lessons about information hygiene does the capacity cascade illustrate?",
    cat="provenance_tracking",
    expected=["A single unverified number can propagate through many derivative documents to create false consensus", "Volume of references is not evidence of correctness", "Source authority (the fire permit) matters more than source count", "Corrections propagate much more slowly than the original claim"],
    diff="hard",
    notes="Tests meta-understanding of the cascade phenomenon")); q+=1

new_qs.append(query(q, q="What is the current water pressure status of the east hydrant loop?",
    cat="factual_recall",
    expected=["72 PSI after repair, meeting the 65 PSI minimum"],
    diff="easy")); q+=1

new_qs.append(query(q, q="Who first raised concerns about the capacity discrepancy?",
    cat="temporal_reasoning",
    expected=["A planning intern first raised the question but was dismissed", "Jules Carter later discovered and formally investigated the discrepancy"],
    diff="medium")); q+=1

new_qs.append(query(q, q="Were the five water pressure observations conducted on the same day?",
    cat="temporal_reasoning",
    expected=["Yes — all five observations were made on August 11, 2026, between 9 AM and 3 PM"],
    diff="easy")); q+=1

new_qs.append(query(q, q="Is the quarterly investor report currently accurate regarding South Yard capacity?",
    cat="stale_reference",
    expected=["The Q2 report initially stated 18,000 but a corrective supplement was issued July 30 stating 12,400"],
    diff="medium")); q+=1

new_qs.append(query(q, q="Name all the documents that have been successfully corrected to 12,400.",
    cat="factual_recall",
    expected=["Operations plan (Maya)", "Ticket platform", "Investor deck (Rowan)", "Safety handbook", "Security staffing plan (BLS)", "Emergency egress plan", "Crowd density analysis", "Social media correction post", "Q2 report supplement", "Ticket platform correction banner"],
    diff="hard",
    notes="Tests comprehensive recall of corrected vs uncorrected items")); q+=1

new_qs.append(query(q, q="Why is the parking plan still allocating 4,500 spaces?",
    cat="stale_reference",
    expected=["It was based on the 18,000 capacity figure (4 people per car average) and has never been updated", "At 12,400 capacity, only 3,100 spaces are needed"],
    diff="easy")); q+=1

new_qs.append(query(q, q="Did the fire department notice the discrepancy between planning documents and their permit?",
    cat="factual_recall",
    expected=["The fire department confirmed the 12,400 figure when Jules called", "Their reinspection confirmed the 12,400 cap"],
    acceptable=["No indication the fire department proactively flagged the discrepancy"],
    diff="medium")); q+=1

new_qs.append(query(q, q="How should a memory system handle conflicting capacity claims of 18,000 vs 12,400?",
    cat="source_authority",
    expected=["Identify the fire permit as the controlling legal authority", "Trace the 18,000 references to their single root source", "Note that 14+ documents citing 18,000 all trace to one source", "Apply source authority ranking: government permits > planning estimates"],
    diff="hard",
    notes="Tests reasoning about source authority for memory systems")); q+=1

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
