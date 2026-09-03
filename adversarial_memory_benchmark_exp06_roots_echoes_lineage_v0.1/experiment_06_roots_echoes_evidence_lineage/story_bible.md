# Story Bible — Experiment 06: Roots, Echoes, and Evidence Lineage

Story ID: `thornfield_sentinel`

## Stage 1 — Candidate arcs and selection

Three candidate arcs were scored before any corpus file was written:

| Candidate | Story strength | Artifact-type variety | Lineage richness | Independent + derivative evidence | Natural cycles | Deterministic ground truth | Semantic-shortcut resistance |
|---|---|---|---|---|---|---|---|
| **A. Industrial telemetry incident** (chosen) | High — concrete, physical, falsifiable events | High (sensor logs, field notes, tickets, PRs/commits, postmortems, status emails, exec decks, customer emails, AI summaries) | Very high — matches the spec's own worked cascade and unsupported-claim examples almost exactly | High — SCADA/weather/technician observations are naturally independent of vendor telemetry | High — retros citing tickets citing wikis citing retros is an everyday failure mode | Very high — every claim is a discrete physical measurement with a timestamp | High — near-duplicate incident write-ups differ enough in surface wording to resist trivial string-matching shortcuts |
| B. Scientific controversy (coral-bleaching study) | Medium-high | Medium (notebooks, preprints, papers, press) | High for citation cascades | Medium — independent measurement is expensive to make convincing at scale | Medium | Medium — scientific truth is often itself contested, muddying ground truth | Medium — press coverage tends to reuse identical phrasing, which risks teaching shortcut detection rather than genuine lineage reasoning |
| C. Journalism investigation (transit incident) | High | Medium (eyewitness, interview notes, wire report, derivative articles) | High for hidden shared roots specifically | Medium | Low — journalism citation chains are usually strictly forward, cycles are contrived | Medium — eyewitness reliability is itself a variable, complicating ground truth | Medium |

**Selected: Candidate A — the Thornfield Sentinel incident cascade.** It is the only candidate that
naturally supports all twelve required subfamilies (06.1–06.12) without forcing any of them, gives
fully deterministic ground truth (a pump either stopped at 14:02:00Z or it didn't), and lets the
same small cast of people plausibly produce every artifact type the spec asks for, including the
reingestion of AI-generated summaries (06.12), which is difficult to motivate naturally in the
other two candidates.

## World

**Thornfield Systems** manufactures **Sentinel** units — remote industrial monitoring devices
installed at customer sites to track pumps, coolant loops, compressors, generators, and structural
vibration. Each unit streams telemetry to Thornfield's own backend and is separately observable
through the customer's own SCADA/facility systems, which is what makes genuinely independent
corroboration possible in this world (Control B, §06.3) as well as its opposite — many
copies of one root pretending to be several (§06.2, §06.10 World A).

Ten customer sites host Sentinel deployments: Ashgrove Processing Plant, Brackwater Terminal,
Caldera Fabrication Yard, Duskford Cold Storage, Elmsgate Refinery Annex, Farrow Point Substation,
Greywick Water Treatment, Halden Ridge Mine, Ironmoor Foundry, and Juniper Bay Desalination.
Individual Sentinel units are identified as `SN-####`; each is attached to one of six subsystem
classes (coolant pump, temperature probe, vibration sensor, relay valve, intake compressor, backup
generator), each with its own numbered instance (e.g. "coolant pump P-3").

## Cast

| Person | Role | Typical artifact types they author |
|---|---|---|
| Priya Nandakumar | Senior Field Engineer | field notes (primary on-site observation) |
| Marcus Oyelaran | On-call SRE | incident tickets, ticket comments |
| Dana Ferreira | Customer Success Lead | customer emails |
| Wei Tan | Reliability Engineer | postmortem reports |
| Sofia Kowalczyk | QA / Test Engineer | technical notes, test-bench reports |
| Amir Hossain | Firmware Engineer | (referenced in firmware-version records, not a memory author in this bundle) |
| Lena Vogt | Program Manager | status emails |
| Oscar Delgado | Support Engineer | chat messages |
| Ingrid Solberg | VP Engineering | executive deck bullets |
| Tobias Reyes | Technical Writer | wiki pages |
| Harriet Okafor | Site Reliability Manager | retrospective reports, technical notes |
| Felix Nakamura | Data/Analytics Engineer | technical notes, status emails |
| Grace Moreau | Independent auditor (3rd party) | (referenced for future extension; not a memory author in this bundle) |
| Dmitri Pavlenko | Customer facility technician, Ashgrove | technician notes (independent physical observation) |
| Nadia Husseini | Customer facility technician, Brackwater | technician notes |
| Leo Bertrand | Field Engineer | field notes |
| Thornfield Assist | internal AI summarizer (system, not a person) | AI-assistant summaries — the origin point of §06.12 reingestion |

`system:telemetry`, `system:customer_scada`, and `system:site_weather` are non-human primary
sources (automated logging systems), used as evidence roots wherever the spec calls for a
machine-generated primary observation.

## Timeframe

The incident window runs from **2026-05-04** through roughly **2026-08-15**, spread across 88
distinct claim clusters ("fact instances") so that no two incidents collide on exact timestamps.
Each fact instance picks its own base date pseudorandomly within that window (see
`generate_corpus.py`, `SEED = 20260614`). Today, in-story, is treated as shortly after the last
ingestion date in the corpus — consistent with a memory system that has been running continuously
since the incident window opened.

## The narrative thread, in outline

Thornfield's fleet of Sentinel units experiences a cluster of unrelated-but-similar incidents
across the ten sites over about three and a half months: pressure trips, vibration excursions,
overtemperature events, overcurrent events, relay dropouts following a firmware push, restart
loops, and a stuck-relay-valve failure mode that keeps recurring in slightly different tellings.
Each incident generates its own small evidence-and-derivation graph — sensor logs and field
inspections at the root, working up through tickets, technical notes, postmortems, wikis, status
emails, and occasionally an executive deck bullet or a customer email.

This is deliberately *not* one single incident with one single provenance graph. It is ~88 small,
mostly-independent incident graphs, so that:

- fan-out, cascade, convergence, and cycle motifs can each be demonstrated cleanly without
  interference from unrelated claims sharing the same nodes;
- perturbation pairs (e.g. root-substitution World A vs. World B, or the cyclic vs. acyclic
  relay-valve pair) can hold wording nearly constant while changing exactly one topology variable;
- scale (350–750 preferred memories) is reached through genuine narrative repetition — the same
  *kind* of incident recurring at different sites with different units — rather than through
  mechanically duplicated text.

## Where the twelve subfamilies live

See `provenance_bible.md` for the explicit evidence-topology definition of each family (this is
the artifact that had to exist *before* any memory text was generated, per the Stage 2 invariant).
In brief:

| Family key | Spec §, motif | Sentinel-world realization |
|---|---|---|
| `cascade` | 06.1 | pressure-drop trip: sensor log → field note → ticket comment → postmortem → status email → exec deck (6-hop single-root chain) |
| `fanout` | 06.2, P06-A | vibration excursion: one field note fans out into 1 / 4 / 5 / 25 derivative write-ups |
| `convergent` | 06.3, Control B | overtemperature event confirmed by Thornfield telemetry + customer SCADA + an unprompted technician observation |
| `hidden_root` | 06.4 | relay dropouts at two different sites, both actually sourced from one unattributed ops-channel message about a firmware push |
| `depth_chain` | 06.5, P06-C | flow-rate drop, summarized-of-summarized 1 / 2 / 4 / 8 times |
| `partial_loss` | 06.6, Control E | overcurrent event: an early technical note cites both its sources, a later wiki page only carries forward one |
| `unsupported` | 06.7, Control F/G | the spec's own pump-stop / temperature-rise example, with an added unsupported "known firmware bug" causal clause |
| `circular` | 06.8, P06-E | stuck relay valve: ticket → wiki → retro → back to ticket (3-cycle), paired with an acyclic sibling that terminates at a real field note |
| `contradiction` | 06.9 | a status email claims six hours of downtime while the telemetry it cites shows the unit online throughout |
| `root_sub` | 06.10, Control C, P06-B | intermittent pressure fault: World A (5 copies of 1 root) vs. World B (5 independently instrumented roots) |
| `disappearance` | 06.11, P06-H | a component-limitation finding traced to an archived vendor test-bench report that is now tombstoned |
| `reentry` | 06.12, P06-G | restart-loop finding: postmortem → AI-assistant summary → the same text pasted into a wiki page as if new → status email |
