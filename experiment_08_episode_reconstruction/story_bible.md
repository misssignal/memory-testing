# Story Bible

A synthetic infrastructure software team operates Northstar, a control-plane service for scheduling jobs across edge clusters. The year contains recurring reliability work, interleaved maintenance, long-lived tickets, cross-repository fixes, pauses, resumptions, and downstream remediation.

## Canonical episodes

### EP01 — January scheduler lease-expiry investigation
- Start: 2028-01-08T09:12:00
- End: 2028-01-12T16:40:00
- Type: incident_investigation
- Goals: reproduce stuck leases, identify renewal race, ship mitigation
- Participants: P01, P02, P05
- Entities: scheduler, lease-manager
- Notes: Distributed across issue, chat, commits, CI, and release. Includes a two-day wait for a stress rig.

### EP02 — January docs navigation cleanup
- Start: 2028-01-08T09:25:00
- End: 2028-01-08T11:20:00
- Type: maintenance
- Goals: repair broken docs navigation
- Participants: P04
- Entities: docs-site
- Notes: Temporally interleaved with EP01 but unrelated.

### EP03 — February auth token refresh regression
- Start: 2028-02-14T13:05:00
- End: 2028-02-15T17:10:00
- Type: incident_investigation
- Goals: diagnose 401 spike, fix token refresh regression
- Participants: P01, P03, P04
- Entities: auth-gateway, node-agent
- Notes: Semantically resembles EP07 but is distinct.

### EP04 — March long-lived issue 73 minor lease telemetry patch
- Start: 2028-03-04T10:00:00
- End: 2028-03-05T14:30:00
- Type: maintenance
- Goals: add lease telemetry
- Participants: P07, P02
- Entities: lease-manager, telemetry-pipeline
- Notes: First distinct burst inside long-lived Issue #73.

### EP05 — June long-lived issue 73 lease protocol redesign
- Start: 2028-06-10T08:45:00
- End: 2028-06-21T18:20:00
- Type: redesign
- Goals: replace renewal handshake, validate new lease protocol
- Participants: P01, P02, P05, P06
- Entities: scheduler, lease-manager
- Notes: Second, much larger burst in Issue #73; must not merge with EP04.

### EP06 — June startup deadlock investigation
- Start: 2028-06-12T09:10:00
- End: 2028-06-19T16:22:00
- Type: incident_investigation
- Goals: reproduce startup freeze, identify dependency cycle, ship mitigation
- Participants: P02, P04, P05
- Entities: node-agent, config-service, worker-runtime
- Notes: Interrupted for hardware availability, resumed after several days; vocabulary evolves from freeze to deadlock.

### EP07 — August service-to-service token expiry incident
- Start: 2028-08-06T07:50:00
- End: 2028-08-08T19:15:00
- Type: incident_investigation
- Goals: diagnose service token expiry, restore auth stability
- Participants: P01, P03, P04
- Entities: auth-gateway, config-service
- Notes: Highly similar terminology to EP03 but different identity and mechanism.

### EP08 — September deployment rollback loop
- Start: 2028-09-17T14:05:00
- End: 2028-09-18T22:10:00
- Type: incident_investigation
- Goals: stop rollback loop, repair deployment state
- Participants: P01, P03, P05
- Entities: deployment-controller, scheduler
- Notes: One episode spans incident ticket, release chat, ops repo, and control-plane repo.

### EP09 — October scheduler latency recurrence
- Start: 2028-10-03T11:30:00
- End: 2028-10-04T20:00:00
- Type: incident_investigation
- Goals: diagnose scheduler latency recurrence
- Participants: P01, P02, P07
- Entities: scheduler, telemetry-pipeline
- Notes: Looks superficially like EP01/EP05 but is a new occurrence.

### EP10 — November startup freeze recurrence
- Start: 2028-11-11T08:15:00
- End: 2028-11-12T15:45:00
- Type: incident_investigation
- Goals: diagnose new startup freeze instance
- Participants: P02, P04, P05
- Entities: node-agent, worker-runtime
- Notes: Same symptom family as EP06 but new trigger and new episode.

### EP11 — December architecture hardening after startup incidents
- Start: 2028-12-02T09:00:00
- End: 2028-12-13T17:00:00
- Type: follow_up
- Goals: remove startup ordering hazard class, add dependency graph checks
- Participants: P02, P04, P06
- Entities: node-agent, config-service, worker-runtime
- Notes: Consequence/follow-up to EP06 and EP10, not member of either.

### EP12 — December unrelated config cache cleanup
- Start: 2028-12-04T10:20:00
- End: 2028-12-04T15:00:00
- Type: maintenance
- Goals: remove stale cache warnings
- Participants: P04
- Entities: config-service
- Notes: Semantically adjacent to EP11 and intentionally distracts.

## Ontology

The benchmark distinguishes `MEMBER_OF`, `PRECURSOR_TO`, `TRIGGERS`, `CAUSES`,
`CONSEQUENCE_OF`, `FOLLOW_UP_TO`, `INTERRUPTS`, `RESUMES`, `OVERLAPS`, `SIMILAR_TO`,
and `UNRELATED_TO`.

Episode ground truth is defined before memory generation. A shared issue, repository, author,
component, or time window is never sufficient by itself to establish episode membership.
