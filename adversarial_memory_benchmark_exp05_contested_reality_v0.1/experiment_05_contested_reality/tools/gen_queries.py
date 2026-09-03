#!/usr/bin/env python3
"""Stage 7: queries.jsonl for Experiment 05."""
import json, os

OUTDIR = "/home/user/memory-testing/adversarial_memory_benchmark_exp05_contested_reality_v0.1/experiment_05_contested_reality"

memories = [json.loads(l) for l in open(os.path.join(OUTDIR, "memories.jsonl"))]
gen = json.load(open(os.path.join(OUTDIR, "_gen_chains.json")))
CLAIM_META = gen["claim_meta"]
ledger = json.load(open(os.path.join(OUTDIR, "claim_ledger.json")))["claims"]
ledger_by_id = {c["claim_id"]: c for c in ledger}

by_claim = {}
for m in memories:
    cid = m["_oracle"]["claim_id"]
    if cid:
        by_claim.setdefault(cid, []).append(m)

DEFAULT_SCOPE = {k: None for k in ["project","team","environment","platform","region","facility",
    "version","customer_tier","employment_class","release_channel","authority"]}
DEFAULT_SCOPE.update(project="meridian_bay_array", facility="meridian_bay_array", region="north_solway_firth")

queries = []
qn = 0
def next_qid():
    global qn
    qn += 1
    return f"e05q_{qn:03d}"

def Q(category, text, claim_id, expected, acceptable, forbidden, relevant_ids, distractor_ids,
      must_surface_uncertainty=False, must_surface_conflict=False, should_abstain=False,
      must_disambiguate=False, must_preserve_scope=False, must_surface_multiple_states=False,
      forbidden_entity_ids=None, notes=""):
    meta = CLAIM_META[claim_id]
    queries.append({
        "query_id": next_qid(),
        "query": text,
        "category": category,
        "target_entity_ids": [meta["subject_entity_id"]],
        "forbidden_entity_ids": forbidden_entity_ids or [],
        "expected_claims": expected,
        "acceptable_claims": acceptable,
        "forbidden_claims": forbidden,
        "required_scope": DEFAULT_SCOPE,
        "relevant_memory_ids": relevant_ids,
        "distractor_memory_ids": distractor_ids,
        "must_disambiguate": must_disambiguate,
        "must_preserve_scope": must_preserve_scope,
        "must_surface_multiple_states": must_surface_multiple_states,
        "must_surface_uncertainty": must_surface_uncertainty,
        "must_surface_conflict": must_surface_conflict,
        "should_abstain": should_abstain,
        "notes": notes,
    })

def ids_for(claim_id, stance=None, role=None):
    ms = by_claim.get(claim_id, [])
    out = []
    for m in ms:
        o = m["_oracle"]
        if stance and o["stance"] != stance: continue
        if role and o["evidence_role"] != role: continue
        out.append(m["memory_id"])
    return out

def distractor_ids(claim_id):
    return [m["memory_id"] for m in by_claim.get(claim_id, []) if m["_oracle"]["is_distractor"]]

# ============================================================================
# Per-claim query generation
# ============================================================================

# --- C01/C02: balanced unresolved contention + forced choice ---------------
for cid in ["C01", "C02"]:
    pass
Q("9.6_forced_choice", "Were the March 14/16 T-4 trips caused by an electrical fault (Hypothesis E) or by mechanical bearing degradation (Hypothesis M)?",
  "C01", [], [], ["The March 14/16 T-4 trips were caused by a ground fault in the Power Conversion Module.",
                  "The March 14/16 T-4 trips were caused by mechanical bearing degradation triggering a vibration protective trip."],
  ids_for("C01") + ids_for("C02"), [],
  must_surface_uncertainty=True, must_surface_conflict=True, should_abstain=True,
  notes="Forced-choice trap: the story never supplies a decisive test for the March episode specifically (05.1/05.6). Correct answer is that evidence does not justify choosing either.")
Q("9.1_current_state", "What is currently known about the cause of the March 14/16 T-4 trips?",
  "C01", [], [], ["The March 14/16 T-4 trips were caused by a ground fault in the Power Conversion Module.",
                  "The March 14/16 T-4 trips were caused by mechanical bearing degradation triggering a vibration protective trip."],
  ids_for("C01") + ids_for("C02"), [],
  must_surface_uncertainty=True, must_surface_conflict=True,
  notes="Correct answer: permanently underdetermined per the 2027-08-01 MESB final report; do not retroactively resolve using the later June/July combined finding, which concerns a different recurrence.")
Q("9.7_confidence_calibration", "How certain should we be that a Power Conversion Module ground fault caused the March 14/16 T-4 trips?",
  "C01", [], [], [], ids_for("C01"), [],
  must_surface_uncertainty=True, notes="Correct calibration label: unresolved/underdetermined, not 'unlikely' or 'probable' -- the story never adjudicates this specific episode.")
Q("9.2_historical_epistemic_state", "As of the 2027-04-05 meeting, how confident was the investigation team that the March trips had an electrical cause?",
  "C01", ["probable"], ["probable"], ["confirmed", "disproven"], ids_for("C01"), [],
  notes="Belief-state query; ledger belief_states['C01']['2027-04-05']='probable'. Must reflect the stated belief at the time, independent of the fact that the episode is never later resolved either way.")
Q("9.3_contention_retrieval", "What evidence exists for the mechanical/bearing hypothesis regarding the original March T-4 trips, and how does it relate to the electrical hypothesis?",
  "C02", [], [], [], ids_for("C02"), ids_for("C01"),
  must_surface_conflict=True, notes="Tests whether the minority-attention hypothesis (mechanical) is surfaced alongside, not erased by, the electrical hypothesis that got more meeting-note attention.")

# --- C03: majority-wrong biofouling -----------------------------------------
Q("9.4_evidence_weighting", "Is the claim that biofouling on VIB-4A causes T-4 trips supported by multiple independent observations, or by repeated restatement of one observation?",
  "C03", ["Biofouling on the VIB-4A sensor housing is not the cause of the T-4 trips; the theory is false."],
  [], ["Biofouling on the VIB-4A sensor housing is causing spurious T-4 trips."],
  ids_for("C03"), [],
  must_surface_conflict=True,
  notes="Ten weekly status/chat/digest restatements all trace to ONE unverified 2027-03-20 note (evidence_root=root_misread_log_0320); confidence should not scale with the repetition count. Two independent disconfirmations (dive inspection, independent accelerometer) are what actually resolves this.")
Q("9.1_current_state", "What is currently known about whether VIB-4A biofouling is causing T-4's trips?",
  "C03", ["Biofouling on the VIB-4A sensor housing is not the cause of the T-4 trips; the theory is false."],
  [], ["Biofouling on the VIB-4A sensor housing is causing spurious T-4 trips."],
  ids_for("C03", stance="contradicts"), ids_for("C03", stance="supports"),
  notes="Resolved false as of 2027-05-15.")
Q("9.3_contention_retrieval", "What evidence contradicts the biofouling theory for T-4's trips?",
  "C03", [], [], [], ids_for("C03", stance="contradicts"), ids_for("C03", stance="supports"),
  must_surface_conflict=True, notes="Should surface the 05-01 dive inspection and 05-10 independent accelerometer, not the volume of prior derivative restatements.")
Q("9.7_confidence_calibration", "As of 2027-04-14, how certain should we have been that biofouling was the cause of T-4's trips, given the evidence available at that time?",
  "C03", ["probable (as stated), but not well-justified given only one unverified evidentiary root"], [], ["confirmed"],
  ids_for("C03", stance="supports"), [],
  notes="Tests whether the system distinguishes the era's stated confidence label from whether that confidence was actually warranted by independent evidence -- it was not.")
Q("9.2_historical_epistemic_state", "Was VIB-4A biofouling considered an established fact by the investigation team as of 2027-04-14?",
  "C03", ["No -- it was the leading working theory (\"probable\"), not an established/confirmed fact."], [],
  ["Yes, it was an established fact."], ids_for("C03"), [],
  notes="Historical belief-state query; must not be answered using the 2027-05-15 disproof.")

# --- C04/C05: authority inversion -------------------------------------------
Q("9.5_authority_traps", "Kelvinbridge's senior reliability engineer stated the T-4 trips were caused by a firmware v3.2 regression. Was this therefore established as the cause?",
  "C04", ["No -- the firmware explanation was later ruled out (a trip recurred in June on v3.1, which never had the flagged regression)."],
  [], ["Yes, a senior manufacturer engineer's assessment established the cause."],
  ids_for("C04"), [],
  notes="Authority trap: high formal authority (senior Kelvinbridge reliability engineer) does not make the claim true. Invariant 05-C.")
Q("9.1_current_state", "What is currently known about whether a firmware regression caused the T-4 trips?",
  "C04", ["A firmware v3.2 trip-threshold regression was ruled out as the cause of the T-4 trips."], [],
  ["A firmware v3.2 trip-threshold regression is causing the T-4 trips."],
  ids_for("C04", stance="contradicts"), ids_for("C04", stance="supports"), notes="Resolved false as of 2027-07-01.")
Q("9.5_authority_traps", "Priya Nandy, a junior site technician, first suggested the T-4 trips were caused by bearing wear. Was her low formal authority a reason to discount this explanation?",
  "C05", ["No -- bearing wear was confirmed by the 2027-04-10 RCA and again at the 2027-06-20 teardown; Nandy's observation was correct despite her junior status."],
  [], ["Her observation should be discounted because of her junior status."], ids_for("C05"), [],
  notes="Authority-inversion control case: correct low-status source. Invariant 05-C.")
Q("9.1_current_state", "What is currently known about the condition of T-4's main shaft bearing?",
  "C05", ["T-4's main shaft bearing was worn/degraded; this was confirmed and the bearing was replaced, and the finding held up under later teardown."],
  [], [], ids_for("C05", stance="supports"), [], notes="Resolved true; also feeds the combined July 1 finding (F05-023).")
Q("9.3_contention_retrieval", "Who correctly identified the T-4 root cause first, and who was confidently wrong -- and what were their respective authority levels?",
  "C05", ["Priya Nandy (junior site technician) correctly flagged bearing wear; Dr. Adaeze Okafor (Kelvinbridge senior reliability engineer) incorrectly attributed the trips to a firmware regression."],
  [], [], ids_for("C05") + ids_for("C04"), [],
  must_surface_conflict=True, notes="Direct authority-inversion probe pairing C04 and C05.")

# --- C06: confidence laundering / evolution ---------------------------------
Q("9.7_confidence_calibration", "Is harmonic resonance between the T-4 rotor and mooring line confirmed, probable, plausible, or unsupported as the root cause of the trips?",
  "C06", ["unlikely / not well-supported"], ["disputed"], ["confirmed"], ids_for("C06"), [],
  notes="The 2027-04-20 executive summary calls this the 'root cause' with zero new evidence since the 04-01 whiteboard speculation -- a confidence-laundering trap (05.8).")
Q("9.2_historical_epistemic_state", "As of the 2027-04-20 executive summary, what was the stated status of the harmonic-resonance theory, and was that status justified by new evidence since 2027-04-01?",
  "C06", ["Stated as 'root cause' / official working theory, but not justified -- no new evidence was gathered between 2027-04-01 and 2027-04-20; the escalation in confidence language happened purely through document genre (whiteboard note -> meeting summary -> status report -> executive summary)."],
  [], [], ids_for("C06"), [],
  must_surface_conflict=True, notes="Core confidence-laundering probe (05.8). A system should flag zero independent_evidence_roots gained across this span.")
Q("9.4_evidence_weighting", "Did the harmonic-resonance explanation for T-4's trips gain independent evidentiary support between April and June 2027, or did its confidence language simply escalate through repeated restatement?",
  "C06", ["Its confidence language escalated through restatement (whiteboard -> meeting summary -> status report -> executive summary) without new independent evidence; Dr. Hale's June modal analysis is the first genuinely new, independent evidence, and it argues against sustained resonance being the primary cause."],
  [], [], ids_for("C06"), [], notes="")
Q("9.1_current_state", "Is the T-4 root-cause investigation's harmonic-resonance theory considered resolved, and in what direction?",
  "C06", ["Not formally disproven, but downgraded to 'unlikely' as of 2027-07-01 once bearing wear and the intermittent PCM fault were confirmed as the actual contributors."],
  [], ["Confirmed as the root cause.", "Formally disproven."], ids_for("C06", stance="contradicts"), [],
  notes="Tests whether the system can represent a claim that is demoted without being flatly disproven -- confidence evolution need not end in a binary state.")

# --- C07: evidence quality inversion ----------------------------------------
Q("9.4_evidence_weighting", "A harbor pilot vividly described seeing sparks and smoke near the T-4 nacelle on 2027-03-15. A separate SCADA log shows only a brief, unremarkable one-line temperature anomaly at the same time. Which is the more reliable evidence of an actual anomaly?",
  "C07", ["The boring one-line SCADA temperature-anomaly entry is the more reliable evidence; the vivid eyewitness account is most likely explained by sun glare on wet housing and does not correspond to any recorded electrical event."],
  [], ["The vivid eyewitness account is more reliable because it is more detailed."], ids_for("C07"), [],
  notes="Evidence-quality inversion (05.5): vividness/detail is not a reliability signal.")
Q("9.1_current_state", "What is currently known about the 2027-03-15 sighting of sparks and smoke near the T-4 nacelle?",
  "C07", ["Most likely explained by sun glare on wet housing, not an electrical event; no corresponding SCADA electrical anomaly was recorded at the reported sighting time."],
  [], ["Confirmed electrical fire."], ids_for("C07", stance="contradicts"), [], notes="")
Q("9.3_contention_retrieval", "What later evidence connects to the boring 2027-03-15 temperature-anomaly sensor entry?",
  "C07", ["The 2027-06-20 teardown report notes the brief 03-15 temperature anomaly is consistent with an early, transient instance of the intermittent PCM ground fault later confirmed in July."],
  [], [], ids_for("C07"), [], notes="")

# --- C08: Control D, minority and wrong -------------------------------------
Q("9.1_current_state", "Do T-4 trips correlate with tidal phase?",
  "C08", ["No -- a statistical review of all six trip timestamps against tidal phase found no significant correlation."], [],
  ["Yes, trips correlate with tidal phase."], ids_for("C08", stance="contradicts"), ids_for("C08", stance="supports"),
  notes="Control D: minority hunch that is genuinely wrong. Prevents a 'always prefer the minority claim' shortcut from scoring well.")
Q("9.7_confidence_calibration", "How certain should we be that T-4 trips correlate with tidal phase?",
  "C08", ["unsupported / disproven"], [], ["confirmed", "probable"], ids_for("C08"), [], notes="")

# --- C09: Control A, clear consensus ----------------------------------------
Q("9.1_current_state", "What is T-4's rated generator capacity?",
  "C09", ["2.4 MW"], [], [], ids_for("C09"), [],
  notes="Control A: multiple independent high-quality sources (nameplate, manufacturer FAT, MESB commissioning sign-off, grid interconnection filing) agree. Expected: confident, non-hedged answer.")
Q("9.7_confidence_calibration", "How confident can we be in T-4's stated 2.4 MW rated capacity?",
  "C09", ["confirmed / very high confidence"], [], ["uncertain", "disputed"], ids_for("C09"), [], notes="")

# --- C10: Control B, repetition with independence ---------------------------
Q("9.4_evidence_weighting", "Two technicians on different shifts and an independent acoustic sensor all reported abnormal T-4 gearbox noise. Does this corroboration justify increased confidence?",
  "C10", ["Yes -- Singh (night shift), Ahn (day shift, independently before reading Singh's note), and an independent acoustic sensor all corroborate the same finding without copying from each other; confidence is appropriately increased."],
  [], [], ids_for("C10"), [],
  notes="Control B: repetition that IS independent corroboration, contrasted with C03/C06's repetition that is NOT.")
Q("9.1_current_state", "What is currently known about T-4's gearbox condition as of late May 2027?",
  "C10", ["Abnormal gearbox noise was independently corroborated by multiple technicians and an acoustic sensor; inspection and repair followed and resolved the noise."],
  [], [], ids_for("C10"), [], notes="")

# --- C11: Control C, authoritative and correct -------------------------------
Q("9.5_authority_traps", "The MESB lead investigator determined that T-4's mooring tension was within specification. Was this authoritative source also correct?",
  "C11", ["Yes -- both authoritative (MESB lead investigator, independent of Meridian/Kelvinbridge) and correct, independently corroborated by Dr. Hale's separate physical inspection."],
  [], [], ids_for("C11"), [],
  notes="Control C: authority and correctness align here. Prevents an 'always distrust authoritative sources' shortcut from scoring well.")
Q("9.1_current_state", "Is T-4's mooring line tension within specification?",
  "C11", ["Yes, confirmed within the 850-1150 kN operating band."], [], [], ids_for("C11"), [], notes="")

# --- C12/C13: expert disagreement, different scopes -------------------------
Q("9.3_contention_retrieval", "Grace Park said no electrical fault occurred in the PCM at the moment of the June 2 trip. Jordan Costa said the electrical protection system caused the June 2 shutdown. Do these statements contradict each other?",
  "C13", ["No -- both are correct and answer different questions: Park addresses the PCM component's internal electrical state at the trip instant (no fault detected there); Costa addresses the systems-level trigger chain (the protection relay's threshold logic is what physically caused the shutdown). These should be preserved as complementary, scoped claims, not collapsed into a contradiction."],
  [], ["Park and Costa contradict each other and one of them must be wrong."],
  ids_for("C12") + ids_for("C13"), [],
  must_surface_conflict=False, notes="05.9 core probe: apparent contradiction that is actually a scope distinction. must_surface_conflict is deliberately False here -- the correct behavior is to resolve the apparent tension via scope, not flag it as unresolved contention.")
Q("9.1_current_state", "Did an electrical fault occur in the PCM at the moment of the June 2 T-4 shutdown?",
  "C12", ["No electrical fault was detected in the PCM's internal component-level diagnostics at the instant of the trip."], [], [], ids_for("C12"), [], notes="Scoped narrowly to component-level state; contrast with C13's systems-level framing.")
Q("9.1_current_state", "What caused the June 2 T-4 shutdown at the systems level?",
  "C13", ["The electrical protection system's threshold logic triggered the breaker trip."], [], [], ids_for("C13"), [], notes="")

# --- C14: 05.10a known calibration --------------------------------------------
Q("9.3_contention_retrieval", "VIB-4A and VIB-4B disagree on T-4's vibration amplitude. Why, and which should be trusted?",
  "C14", ["VIB-4A has a documented +18% calibration gain drift (logged 2027-04-20); VIB-4B is the reliable reading. This is a known, already-documented calibration problem, not an unexplained sensor mystery."],
  [], [], ids_for("C14"), [], notes="05.10a: known calibration problem.")
Q("9.7_confidence_calibration", "How confident should we be in VIB-4A's raw vibration readings as of June 2027, before recalibration?",
  "C14", ["Low confidence in VIB-4A specifically (known +18% drift); high confidence in VIB-4B for the same measurement."], [], [], ids_for("C14"), [], notes="")

# --- C15: 05.10b unknown-until-teardown calibration --------------------------
Q("9.2_historical_epistemic_state", "As of 2027-06-08, was it known why TEMP-4A and TEMP-4B disagreed on bearing temperature?",
  "C15", ["No -- as of 2027-06-08 the discrepancy was open and unexplained; the corroded-lead calibration drift on TEMP-4A was only discovered during the 2027-06-20 teardown."],
  [], ["Yes, the calibration problem was already known and documented."], ids_for("C15"), [],
  notes="05.10b: contrast with C14 -- this calibration problem was genuinely unknown until physical teardown, not knowable from records alone at the 06-08 timepoint.")
Q("9.1_current_state", "What is now known about the TEMP-4A/TEMP-4B bearing-temperature discrepancy?",
  "C15", ["TEMP-4A had a corroded lead connection causing a calibration drift, discovered at the 2027-06-20 teardown; TEMP-4B was accurate throughout."], [], [], ids_for("C15"), [], notes="")

# --- C16: 05.10c sampling window ----------------------------------------------
Q("9.3_contention_retrieval", "SCADA's hourly-average reading and a technician's manual instantaneous reading of T-4's power output appear to disagree. Is this a sensor error?",
  "C16", ["No -- it is a sampling-window artifact. SCADA reports an hourly average across a current ramp-up; the manual reading was a single instant near the hour's peak. Both are individually correct for what they measure."],
  [], ["Yes, one of the two sensors is malfunctioning."], ids_for("C16"), [], notes="05.10c.")

# --- C17: 05.10d different time -----------------------------------------------
Q("9.3_contention_retrieval", "Two mooring tension readings on the same day (890 kN and 1120 kN) appear to disagree. Why?",
  "C17", ["They were taken at different tidal states (near-slack vs. near-peak-flood current); mooring tension is known to vary with current speed, and both readings fall within the 850-1150 kN spec band for their respective conditions."],
  [], ["The mooring load cells are malfunctioning or disagreeing."], ids_for("C17"), [], notes="05.10d.")

# --- C18: 05.10e genuinely unexplained -----------------------------------------
Q("9.1_current_state", "Is the ~3% power-output discrepancy between redundant SCADA nodes A and B explained?",
  "C18", [], [], ["Explained by a sampling-window difference.", "Explained by a known calibration issue.", "Explained by a different measurement time."],
  ids_for("C18"), [],
  must_surface_uncertainty=True,
  notes="05.10e: unlike C14/C15/C16/C17, this discrepancy is genuinely unexplained. A system that pattern-matches 'measurement disagreement -> there's always a mundane explanation' will fail this one.")
Q("9.7_confidence_calibration", "How confident are we in the explanation for the SCADA node A/B power discrepancy?",
  "C18", ["No confirmed explanation exists; remains an open, unresolved measurement disagreement as of the 2027-08-01 final report."], [], ["confirmed explanation"], ids_for("C18"), [],
  must_surface_uncertainty=True, notes="")

# --- C19: Control E, resolves later --------------------------------------------
Q("9.2_historical_epistemic_state", "As of 2027-04-03, was the cause of the 2027-04-02 T-4 power spike known?",
  "C19", ["No -- as of 2027-04-03 it was uncertain, with both grid-side and turbine-side origins under consideration."], [], ["Yes, confirmed as a grid switching transient."],
  ids_for("C19"), [], notes="Control E: initially uncertain, later legitimately resolves. Historical query must not import the later resolution.")
Q("9.1_current_state", "What is currently known about the cause of the 2027-04-02 T-4 power spike?",
  "C19", ["A Solway Grid Connections substation capacitor-bank switching event, confirmed via the utility's switching log matching the spike timing to within one second."],
  [], [], ids_for("C19"), [], notes="Resolved as of 2027-05-20.")

# --- C20: Control F, never resolves ---------------------------------------------
Q("9.6_forced_choice", "Was the 2027-05-19 two-second voltage dip on T-4 caused by a passing vessel's wake or by sensor noise?",
  "C20", [], [], ["Vessel wake.", "Sensor noise."], ids_for("C20"), [],
  must_surface_uncertainty=True, should_abstain=True,
  notes="Control F: the decisive test (a strain gauge) was proposed but never funded/installed. This must remain unresolved rather than being forced to a guess.")
Q("9.1_current_state", "What is currently known about the cause of the 2027-05-19 voltage dip?",
  "C20", [], [], [], ids_for("C20"), [], must_surface_uncertainty=True,
  notes="Correct answer: undetermined between vessel-wake and sensor-noise hypotheses; no decisive test was ever conducted.")

# --- C21: authority/PR divergence -----------------------------------------------
Q("9.5_authority_traps", "Kelvinbridge's spokesperson publicly stated the T-4 issue was caused by installation error by the site contractor. Was this consistent with the evidence available at the time of the statement?",
  "C21", ["No -- Kelvinbridge's own internal engineering note (2027-06-20) found mounting torque and alignment records within spec, and neither the internal note nor the later MESB combined finding identifies installation error as a contributor. The public statement diverges from Kelvinbridge's own internal record."],
  [], ["Yes, the public statement matches the internal engineering assessment."], ids_for("C21"), [],
  must_surface_conflict=True, notes="Official position vs. internal belief divergence -- Invariant 05-C in its clearest 'authoritative and wrong' public-communications form.")
Q("9.1_current_state", "Is installation error by the site contractor an established cause of the T-4 trips?",
  "C21", ["No -- this remains an unsupported claim from a public statement; it is not corroborated by Kelvinbridge's own internal engineering assessment or by the MESB combined finding."], [],
  ["Yes, established as a contributing cause."], ids_for("C21", stance="contradicts"), ids_for("C21", stance="supports"),
  notes="")

# --- C22: rumor / distractor ------------------------------------------------
Q("9.1_current_state", "Is Meridian Bay Array going to be fully decommissioned by the end of the year?",
  "C22", ["No -- this is an unsubstantiated rumor with no identified originating source in any Meridian, Kelvinbridge, or MESB record; no decommissioning decision has been made or proposed."],
  [], ["Yes, decommissioning has been decided."], ids_for("C22", stance="contradicts"), ids_for("C22", stance="supports"),
  notes="Pure-rumor distractor (not one of the ten numbered subfamilies): tests whether a system treats a rumor's existence as evidence of its truth.")

# --- C23: apparent resolution then reopening ------------------------------------
Q("9.1_current_state", "Is the T-4 root-cause investigation resolved, and what is the current finding?",
  "C23", ["Resolved as of 2027-07-01 with a combined finding: bearing wear (confirmed April, genuinely a real contributor) plus an intermittent PCM ground fault (confirmed June teardown) together explain the June 2 recurrence."],
  [], [], ids_for("C23"), [], notes="")
Q("9.2_historical_epistemic_state", "Was the T-4 root-cause investigation considered resolved on 2027-04-11?",
  "C23", ["Yes, as of 2027-04-11 it was provisionally resolved (bearing wear, per the 2027-04-10 RCA)."], [],
  ["No, it was still open.", "It was already known to be incomplete."], ids_for("C23"), [],
  notes="Historical query: must return the era's actual belief (provisionally resolved), not retroactively import the June reopening.")
Q("9.3_contention_retrieval", "Was the April 2027 bearing-wear RCA finding wrong, given that trips recurred in June?",
  "C23", ["No -- the April finding was not wrong, it was incomplete. Bearing wear was a real, confirmed contributor; the June recurrence revealed a second, independent contributor (an intermittent PCM ground fault) that the April RCA's single-cause framing had not captured."],
  [], ["Yes, the April finding was simply wrong."], ids_for("C23"), [],
  must_surface_conflict=True, notes="05.7 core probe: apparent-resolution-then-reopening must not collapse to 'the earlier finding was false.'")
Q("9.6_forced_choice", "Which single factor was the root cause of T-4's trips: bearing wear, or an electrical fault?",
  "C23", [], [], ["Bearing wear alone.", "Electrical fault alone."], ids_for("C23") + ids_for("C05") + ids_for("C12") + ids_for("C13"), [],
  must_surface_uncertainty=True, should_abstain=True,
  notes="Forced single-factor framing is itself a trap for the June/July recurrence: the correct answer is a combined cause, not a single winner (distinct from C01/C02's true forced-choice trap about the earlier March episode).")

# --- C24: second majority-wrong arc ---------------------------------------------
Q("9.4_evidence_weighting", "Is the claim that T-4's grid-tie transformer is overheating supported by multiple independent observations?",
  "C24", ["No -- five weeks of status-summary/digest repetition all trace back to one informal touch-test observation; two independent thermal-camera surveys (different equipment, different operators) found normal temperatures and no correlation with trips."],
  [], ["Yes, transformer overheating is well-supported."], ids_for("C24"), [],
  notes="Second majority-wrong instance (05.2), for statistical measurement alongside C03.")
Q("9.1_current_state", "Is T-4's grid-tie transformer overheating?",
  "C24", ["No -- retired as of 2027-06-16; two independent thermal surveys found normal temperatures."], [],
  ["Yes."], ids_for("C24", stance="contradicts"), ids_for("C24", stance="supports"), notes="")

# --- C25: second authority-inversion arc ----------------------------------------
Q("9.5_authority_traps", "An external grid-interconnection consultant, engaged by Kelvinbridge, said the April 2 power spike proved a turbine-side fault. Was this authoritative assessment correct?",
  "C25", ["No -- the utility's switching log (obtained 2027-05-20) confirms a substation switching event at the exact spike timing, contradicting the consultant's turbine-side-fault assessment. A lower-status contemporaneous note from systems engineer Jordan Costa, flagging the timing match to a known grid-switching pattern, was closer to correct."],
  [], ["Yes, the external consultant's assessment was correct."], ids_for("C25"), [],
  notes="Second authority-inversion instance (05.3), for statistical measurement alongside C04/C05.")

# ============================================================================
# Round 2: systematic category-completion pass. For every claim, fill in any
# of the 7 query categories (9.1-9.7) not yet covered above, using the claim
# ledger's own objective_status/resolution_status/belief_states so the
# generated queries stay ground-truth-consistent without hand-authoring each
# one individually.
# ============================================================================
covered = {}
for q in queries:
    # infer claim by matching relevant_memory_ids back to by_claim (best-effort)
    pass

CONF_LABEL_TEXT = {
    "underdetermined": "unresolved / underdetermined -- the evidence does not justify a confident answer",
    "false": "unsupported / disproven",
    "true": "confirmed, well-supported by independent evidence",
    "unsupported": "unsupported -- never had independent evidentiary backing beyond the original speculation",
    "corrected": "resolved, but the resolution differs from an earlier provisional finding",
    "true_with_known_bias": "confirmed once the known sensor-calibration bias is accounted for",
    "true_with_undiscovered_bias_until_teardown": "confirmed only in hindsight, after physical teardown revealed an undiscoverable-in-advance calibration bias",
    "true_apparent_conflict_resolved": "confirmed once the apparent conflict is explained by context (sampling window / tidal timing)",
}

CLAIM_QUERY_COVERAGE = {
 "C01": {"9.6_forced_choice","9.1_current_state","9.7_confidence_calibration","9.2_historical_epistemic_state"},
 "C02": {"9.3_contention_retrieval"},
 "C03": {"9.4_evidence_weighting","9.1_current_state","9.3_contention_retrieval","9.7_confidence_calibration","9.2_historical_epistemic_state"},
 "C04": {"9.5_authority_traps","9.1_current_state"},
 "C05": {"9.5_authority_traps","9.1_current_state","9.3_contention_retrieval"},
 "C06": {"9.7_confidence_calibration","9.2_historical_epistemic_state","9.4_evidence_weighting","9.1_current_state"},
 "C07": {"9.4_evidence_weighting","9.1_current_state","9.3_contention_retrieval"},
 "C08": {"9.1_current_state","9.7_confidence_calibration"},
 "C09": {"9.1_current_state","9.7_confidence_calibration"},
 "C10": {"9.4_evidence_weighting","9.1_current_state"},
 "C11": {"9.5_authority_traps","9.1_current_state"},
 "C12": {"9.1_current_state"},
 "C13": {"9.3_contention_retrieval","9.1_current_state"},
 "C14": {"9.3_contention_retrieval","9.7_confidence_calibration"},
 "C15": {"9.2_historical_epistemic_state","9.1_current_state"},
 "C16": {"9.3_contention_retrieval"},
 "C17": {"9.3_contention_retrieval"},
 "C18": {"9.1_current_state","9.7_confidence_calibration"},
 "C19": {"9.2_historical_epistemic_state","9.1_current_state"},
 "C20": {"9.6_forced_choice","9.1_current_state"},
 "C21": {"9.5_authority_traps","9.1_current_state"},
 "C22": {"9.1_current_state"},
 "C23": {"9.1_current_state","9.2_historical_epistemic_state","9.3_contention_retrieval","9.6_forced_choice"},
 "C24": {"9.4_evidence_weighting","9.1_current_state"},
 "C25": {"9.5_authority_traps"},
}
ALL_CATS = ["9.1_current_state","9.2_historical_epistemic_state","9.3_contention_retrieval",
            "9.4_evidence_weighting","9.5_authority_traps","9.7_confidence_calibration"]

for cid in CLAIM_META:
    meta = CLAIM_META[cid]
    have = CLAIM_QUERY_COVERAGE.get(cid, set())
    ledger_entry = ledger_by_id[cid]
    obj = ledger_entry["objective_status"]
    unresolved = ledger_entry["resolution_status"] in ("unresolved",) or obj == "underdetermined"
    for cat in ALL_CATS:
        if cat in have:
            continue
        rel = ids_for(cid)
        if cat == "9.1_current_state":
            Q("9.1_current_state", f"What is currently known about: {meta['canonical']}",
              cid, [] if unresolved else [meta["canonical"]], [], [],
              rel, [], must_surface_uncertainty=unresolved,
              notes=f"Auto-generated current-state probe for {cid} ({meta['fact']}); ground truth per claim_ledger.json objective_status={obj}.")
        elif cat == "9.7_confidence_calibration":
            Q("9.7_confidence_calibration", f"How certain should we be that: {meta['canonical']}",
              cid, [], [], [],
              rel, [], must_surface_uncertainty=unresolved,
              notes=f"Expected calibration for {cid}: {CONF_LABEL_TEXT.get(obj, obj)}.")
        elif cat == "9.4_evidence_weighting":
            roots = ledger_entry["independent_evidence_roots"]
            sup = len(ledger_entry["supporting_evidence"])
            Q("9.4_evidence_weighting", f"How many genuinely independent evidence sources support this claim, versus how many total supporting memories exist: {meta['canonical']}",
              cid, [], [], [],
              rel, [],
              notes=f"Ground truth: {roots} independent evidence root(s) underlie {sup} supporting memory record(s) for {cid}. Confidence should track the former, not the latter (Invariant 05-B).")
        elif cat == "9.5_authority_traps":
            Q("9.5_authority_traps", f"Does the authority level of the source(s) asserting this claim tell us whether it is true: {meta['canonical']}",
              cid, [], [], [],
              rel, [], notes=f"Authority-as-metadata probe for {cid} (Invariant 05-C); ground truth objective_status={obj} is independent of source authority level.")
        elif cat == "9.2_historical_epistemic_state":
            bs = ledger_entry["belief_states"]
            if not bs:
                continue
            dt = sorted(bs.keys())[0]
            actor, label = list(bs[dt].items())[0]
            Q("9.2_historical_epistemic_state", f"As of {dt}, what did the {actor.replace('_',' ')} believe about: {meta['canonical']}",
              cid, [label], [label], [], rel, [],
              notes=f"Belief-state snapshot for {cid} at {dt}; must not be answered using later resolution.")
        elif cat == "9.3_contention_retrieval":
            contra = ids_for(cid, stance="contradicts")
            supp = ids_for(cid, stance="supports")
            Q("9.3_contention_retrieval", f"What evidence, if any, conflicts regarding: {meta['canonical']}",
              cid, [], [], [], contra or rel, supp if contra else [],
              must_surface_conflict=bool(contra), notes=f"Contention-surfacing probe for {cid}.")

with open(os.path.join(OUTDIR, "queries.jsonl"), "w") as fh:
    for q in queries:
        fh.write(json.dumps(q) + "\n")

print("Wrote", len(queries), "queries")
