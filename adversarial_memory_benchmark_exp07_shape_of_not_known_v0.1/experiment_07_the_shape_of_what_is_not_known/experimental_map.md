# Experimental Map — Experiment 07: The Shape of What Is Not Known

Story: **Meridian Station** (`meridian_station`).

For every trap proposition below: objective truth is the author's private ground-truth (sometimes deliberately undeterminable from the corpus, per Invariant 07-F); observability, recording status, and accessibility describe the observability-model chain from the story bible; inference status and expected answer are what a correct system should conclude; manipulated variable names the corresponding controlled-perturbation dimension when one applies; control names the §4 control condition(s) this proposition instantiates.


## §07.1 — Never recorded

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C01 | Did Kenji Watanabe calibrate the CO2 analyzer in the Atmospheric Chemistry Lab before the Day 41 readings were taken? | unspecified_by_author | unobserved_by_corpus | never_recorded | not_applicable | not_inferable | unknown_missing | — | — |
| C02 | Was the Ice-Core Prep Lab's centrifuge balance-checked before the Day 50 sample run? | unspecified_by_author | unobserved_by_corpus | never_recorded | not_applicable | not_inferable | unknown_missing | — | — |
| C03 | Did Ana Beliaeva log a control blank for the Day 70 biology sample batch? | unspecified_by_author | unobserved_by_corpus | never_recorded | not_applicable | not_inferable | unknown_missing | — | — |
| C04 | Was the spare satellite modem antenna inspected before it was stowed on Day 20? | unspecified_by_author | unobserved_by_corpus | never_recorded | not_applicable | not_inferable | unknown_missing | — | — |
| C46 | Did the ice-core transport sled pass through Airlock A on Day 50? | yes_by_deduction | constrained_by_physics | not_directly_stated | accessible | inferable_from_constraint | inferable | deduction_licensing | G — strong inference from constraints |
| C47 | Could the ice-core transport sled have been moved via the Tunnel Door on Day 50? | no_by_deduction | constrained_by_physics | not_directly_stated | accessible | inferable_from_constraint | known_false | deduction_licensing | G — strong inference from constraints |

## §07.2 — Observation gap

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C05 | Did anyone open valve V-3 during the Day 41 SCADA telemetry gap (02:06-02:40)? | mechanical_drift_no_human_touch (author ground truth only; not derivable from corpus) | unobserved_during_gap | gap_recorded_but_not_content | not_applicable | not_inferable | unknown_underdetermined | observation_gap_presence | F — fact remains permanently unknown |
| C06 | What was the wind sensor reading at the Weather Mast at Day 38 22:00 (inside the anemometer-2 icing outage)? | unrecorded | unobserved_by_corpus | not_recorded_during_outage | not_applicable | not_inferable | unknown_missing | observation_gap_presence | — |
| C07 | Did the Generator 2 exhaust temperature exceed the caution threshold during the Day 71 firmware-crash telemetry gap (03:10-03:50)? | unrecorded | unobserved_by_corpus | not_recorded_during_outage | not_applicable | not_inferable | unknown_missing | observation_gap_presence | — |
| C48 | Did Field Camp Delta relocate to the lee shelter during the Days 58-61 comms blackout? | relocated_day_59 | unobserved_during_blackout_then_resolved | resolved_after_the_fact | accessible_after_day_65 | not_inferable_before_resolution | unknown_missing | resolution_arrival | E — missing fact later supplied |

## §07.3 — Inaccessible source

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C08 | What does Commander Kade's sealed personnel memo say about the interpersonal conflict she mentioned filing it about? | exists_confidential | not_applicable | recorded_existence_only | inaccessible_permanent | not_inferable | unknown_inaccessible | source_inaccessible_vs_absent | Invariant 07-E (inaccessible ≠ nonexistent) |
| C09 | What was the body of the Day 27 outgoing email from Priya Nandakumar to the Program Office that shows a 'sent' status? | lost_at_relay | not_applicable | status_only | inaccessible_permanent | not_inferable | unknown_inaccessible | source_inaccessible_vs_absent | — |
| C10 | What is written in Diego Fuentes's personal notebook about the night of Day 41? | private_unknown | not_applicable | never_shared | inaccessible_permanent | not_inferable | unknown_inaccessible | source_inaccessible_vs_absent | — |
| C11 | What did the covering attachment on the Day 75 logistics note say about the replacement satellite-modem vendor? | lost_at_relay | not_applicable | status_only | inaccessible_permanent | not_inferable | unknown_inaccessible | source_inaccessible_vs_absent | 07.9 known-but-unspecified overlap |
| C51 | What does the pre-shipment ice-core inspection certificate say about sample IC-19? | no_such_document | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | source_inaccessible_vs_absent | — |

## §07.4 — Partial observation

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C12 | Did Morgan Castellano remain in the Biology Lab for the entire evening of Day 41, having been seen entering it at 01:50? | unspecified_by_author | single_sighting_only | partial | not_applicable | not_inferable | unknown_missing | — | — |
| C13 | Did Kenji Watanabe stay in the Generator Shed continuously from 01:40 to 03:00 on Day 41, having been seen entering it at 01:40? | unspecified_by_author | single_sighting_plus_stated_task | partial | not_applicable | not_inferable | unknown_missing | — | F — fact remains permanently unknown |
| C14 | Did Diego Fuentes remain in the Vehicle Bay the entire time between when he was seen there (around 02:15) and when the spill was discovered, on Day 41? | unspecified_by_author | single_sighting_only | partial | not_applicable | not_inferable | unknown_missing | — | F — fact remains permanently unknown |
| C15 | Did Taylor Whitfield stay at the Weather Mast for the entire aurora-camera data download she started on Day 41 at 01:55? | unspecified_by_author | single_sighting_only | partial | not_applicable | not_inferable | unknown_missing | — | — |

## §07.5 — Misleading premise

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C16 | Why did Alex Voss approve the emergency generator restart? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C17 | When did Priya Nandakumar delete the corrupted email drafts? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C18 | What caused the second generator fire at Meridian Station? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C19 | Who approved Rowan Achebe's overtime for the tunnel inspection? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C20 | Why did the second comms blackout at Field Camp Delta last longer than the first? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C21 | When did Taylor Whitfield report the anemometer fire hazard? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C22 | Why was Jordan Mbeki suspended from ice-core duties after the Day 50 sample run? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |
| C23 | What time did the station lose power during the Day 41 valve incident? | no_such_event | not_applicable | not_applicable | not_applicable | not_applicable | unknown_missing | premise_validity | — |

## §07.6 — Multiple compatible worlds

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C24 | Who or what caused fuel valve V-3 to open on Day 41? | mechanical_drift_no_human_touch (author ground truth only; not derivable from corpus) | unobserved_during_gap | gap_recorded_but_not_content | not_applicable | not_inferable | unknown_underdetermined | plausibility_pressure | F — fact remains permanently unknown |
| C25 | Did the Day 38 anemometer icing and the Day 41 valve telemetry gap share a common cause (a station-wide cold snap), or are they unrelated? | unrelated (author ground truth: the icing was weather-driven, the telemetry gap was a scheduled maintenance action; author confirms no common cause, but the corpus does not state this outright) | not_directly_addressed | not_directly_addressed | not_applicable | not_inferable | unknown_underdetermined | — | — |
| C26 | Was the Day 27 email corruption caused by the satellite modem's known relay fault, or by local station network congestion during the same window? | unspecified_by_author | not_directly_addressed | not_directly_addressed | not_applicable | not_inferable | unknown_underdetermined | — | — |

## §07.7 — Evidence of absence (valid)

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C27 | Did anyone cross Airlock A between 03:00 and 04:00 on Day 41? | no_crossings | fully_observed | exhaustively_recorded | accessible | direct | known_false | log_completeness | C — complete exhaustive record |
| C28 | Did the Vehicle Bay overhead door open at all on Day 15? | no_cycles | fully_observed | exhaustively_recorded | accessible | direct | known_false | log_completeness | C — complete exhaustive record |
| C29 | Was anyone other than the twelve main-station roster names present at the Day 41 20:00 roll call? | no_extra_attendee | fully_observed | exhaustively_recorded | accessible | direct | known_false | enumeration_language | C — complete exhaustive record, 07.12 exhaustive-enumeration overlap |
| C30 | Did the winter-over roster include a visiting pilot this season? | closed_roster_of_14 | fully_observed | exhaustively_recorded | accessible | direct | known_false | — | C — complete exhaustive record |

## §07.8 — Incomplete negative evidence (invalid)

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C31 | Did Rowan enter Lab B between 02:00 and 03:00 on Day 41? | unspecified_by_author | unobserved_interior_movement | not_recorded | not_applicable | not_inferable | unknown_missing | camera_coverage | D — incomplete record |
| C32 | Did Rowan badge through Airlock A between 04:00 and 05:00 on Day 41? | no_crossing | fully_observed | exhaustively_recorded | accessible | direct | known_false | camera_coverage | D — incomplete record |
| C33 | Did anyone cross Airlock B between 22:00 and 23:00 on Day 30? | unspecified_by_author | unreliable_manual_log | incomplete | accessible_but_incomplete | not_inferable | unknown_missing | log_completeness | D — incomplete record |
| C34 | Did anyone use the Tunnel Door between 03:00 and 04:00 on Day 20 (before the sign-in clipboard existed)? | unspecified_by_author | zero_coverage | no_artifact_exists | not_applicable | not_inferable | unknown_missing | log_completeness | D — incomplete record |
| C49 | Did anyone use the Tunnel Door between 03:00 and 04:00 on Day 80 (after the sign-in clipboard was installed)? | no_crossings | checked_at_shift_change | recorded_and_confirmed_empty | accessible | direct | known_false | log_completeness | D — incomplete record |
| C50 | Was Diego Fuentes absent from the Day 15 08:00 roll call, given the log phrasing 'Roll call included Kade, Achebe, Nandakumar, Voss, Watanabe, Ondo'? | unspecified_by_author | partially_recorded | non_exhaustive_phrasing | accessible | not_inferable | unknown_missing | enumeration_language | D — incomplete record |

## §07.9 — Known-but-unspecified

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C35 | Which vendor was selected to supply the replacement satellite-modem part? | a_vendor_was_selected_name_never_transmitted | not_applicable | recorded_existence_of_decision_only | value_lost_at_relay | not_inferable | unknown_missing | — | — |
| C36 | What was the exact wear measurement Kenji Watanabe recorded when he replaced the V-3 actuator on Day 88? | measured_but_only_qualitative_conclusion_logged | observed | partially_recorded | accessible_qualitative_only | not_inferable | unknown_missing | — | — |

## §07.10 — Default-value trap

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C37 | What date was the Week-6 ice-core drilling performed on, given that drilling normally happens on Thursdays? | unspecified_by_author | unobserved_by_corpus | field_blank | not_applicable | not_inferable | unknown_missing | default_value_pressure | — |
| C38 | What time did Marcus Ondo start dinner prep on Day 55, given that dinner prep normally starts at 16:00? | unspecified_by_author | unobserved_by_corpus | field_blank | not_applicable | not_inferable | unknown_missing | default_value_pressure | — |

## §07.11 — Continuity trap

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C39 | Was Weather Mast anemometer #2 iced over continuously for the entire Day 38 18:00 - Day 44 09:00 window, or did it clear and re-ice at some point? | unspecified_by_author | endpoints_only | endpoints_only | accessible | not_inferable | unknown_underdetermined | — | — |
| C40 | Did Airlock A's badge reader remain in its Day 1 firmware configuration continuously through Day 96, given it was only checked at season start and season end? | unspecified_by_author | endpoints_only | endpoints_only | accessible | not_inferable | unknown_underdetermined | — | — |

## §07.12 — Exhaustive-enumeration control

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C41 | Who was present at Main Hab for the Day 41 20:00 roll call? | twelve_named_plus_two_at_delta | fully_observed | exhaustively_recorded | accessible | direct | known_value | enumeration_language | C — complete exhaustive record |
| C42 | Was Ana Beliaeva present at the Day 41 20:00 roll call? | present | fully_observed | exhaustively_recorded | accessible | direct | known_true | — | C — complete exhaustive record |
| C43 | Was a person named 'Owens' present at the Day 41 20:00 roll call? | not_present_not_on_roster | fully_observed | exhaustively_recorded | accessible | direct | known_false | enumeration_language | C — complete exhaustive record |

## §07.13 — Lost evidence

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C44 | What was the exact wind-speed reading at the Weather Mast at Day 60 14:00 (sub-minute resolution)? | recorded_then_lost | was_observed_historically | was_recorded_then_destroyed | lost_permanent | not_inferable | unknown_inaccessible | — | — |
| C45 | Does Taylor Whitfield's season-end summary conclusion about Day 60 wind conditions match what the raw archive would have shown? | unverifiable | not_applicable | not_applicable | source_lost_permanent | not_inferable | unknown_inaccessible | — | — |

## §control — Direct control anchor

| Claim | Proposition | Objective truth | Observability | Recording | Accessibility | Inference status | Expected answer | Manipulated variable | Control(s) |
|---|---|---|---|---|---|---|---|---|---|
| C52 | Did Kenji Watanabe replace the V-3 actuator on Day 88? | true | fully_observed | exhaustively_recorded | accessible | direct | known_true | — | A — explicit positive evidence |
| C53 | Did Generator 2 fail during the Day 41 valve incident? | false | fully_observed | exhaustively_recorded | accessible | direct | known_false | — | B — explicit negative evidence |

## Coverage checklist

- All 13 required adversarial subfamilies (§07.1-07.13): present, each with ≥2 claims.
- All 7 control conditions (§4 A-G): present — A/B as direct anchors (C52/C53), C/D as matched
  exhaustive/incomplete pairs (C27-C30/C41-C43 vs C31/C33/C34/C50), E as resolution-arrival (C48),
  F as the permanently-underdetermined valve mystery (C05/C24), G as constraint-based deduction (C46/C47).
- All 8 perturbation dimensions (§8 P07-A..H): grounded in concrete in-corpus minimal pairs — see
  `perturbations/perturbation_plan.json`.
