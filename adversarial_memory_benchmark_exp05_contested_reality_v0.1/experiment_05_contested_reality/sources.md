# Sources

This story is fully synthetic. No real company, product, regulator, or incident is being asserted
as factual. Meridian Tidal Energy, Kelvinbridge Marine Systems, the Marine Energy Safety Board,
Solway Grid Connections, and all named individuals are fictional benchmark artifacts.

## Source types in this corpus

- `sensor_log` -- automated SCADA/instrumentation readings (`automated_scada`).
- `handwritten_log` / `technical_note` -- direct technician or engineer observations.
- `status_summary` / `executive_summary` / `meeting_summary` -- institutional documents, often
  derivative of an earlier technical note (see `derived_from`).
- `investigation_report` / `rca_report` / `teardown_report` / `inspection_report` -- formal
  findings, some provisional (see `truth_role` and `_oracle.confidence_label`).
- `press_statement` -- an official public position, which may diverge from the internal
  evidentiary record (Invariant 05-C). Never treat as automatically authoritative.
- `rumor` / `dockside_rumor` -- explicitly unattributed, no evidentiary chain.
- `authoritative_record` -- nameplate data, regulatory records, utility logs, commissioning
  reports; still subject to Invariant 05-C (authoritative does not mean automatically correct
  for interpretive claims, though several Control-A/C records here are both authoritative and
  correct by design).

## Reading `_oracle`

Each memory's `_oracle` block records development-only ground truth: `fact_id`, `claim_id`
(cross-referencing `claim_ledger.json`), `adversarial_subfamily`, `is_distractor`,
`confidence_label` (the *stated* confidence at the time, not necessarily justified confidence),
`evidence_role` (`independent_primary` / `derivative_copy` / `synthesis` / `context`), `stance`
(`supports` / `contradicts` / `neutral_observation` relative to the claim), `source_authority`,
and `evidence_root` (a label shared by all derivative copies of one underlying observation --
used to compute `independent_evidence_roots` in `claim_ledger.json`). Strip `_oracle` for blind
runs, per `manifest.json`.
