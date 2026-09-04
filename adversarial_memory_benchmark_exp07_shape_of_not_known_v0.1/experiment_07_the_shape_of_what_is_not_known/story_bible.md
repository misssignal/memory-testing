# Story Bible — Experiment 07: The Shape of What Is Not Known

Story ID: `meridian_station`

## Research target

Can the system distinguish, and correctly explain, the boundary between: known,
unknown-but-eventually-knowable, unrecorded, unobserved, inaccessible, lost,
underdetermined, and known-not-to-have-occurred? Can it recognize when negative
evidence *is* meaningful (a complete log with no matching entry) versus when it is
merely absent evidence (nobody happened to mention it)?

## Setting

**Meridian Station**, a fictional 14-person multinational Antarctic research
station, during one austral winter isolation period (no aircraft access for ~5
months). Season clock runs from **Day 1** to **Day 96** of the winter-over
(narrative dates given as `Day N`; `event_time`/`observation_time`/
`ingestion_time` fields use ISO dates anchored to a fictional 2031 season,
`2031-04-04` = Day 1). This is a fully synthetic setting; no real station,
program, or incident is being described.

## Cast (14 winter-over crew)

| Entity ID | Name | Role |
|---|---|---|
| `person_kade` | Dr. Elena Kade | Station Commander |
| `person_achebe` | Rowan Achebe | Chief Engineer |
| `person_nandakumar` | Priya Nandakumar | Systems / IT & Comms Officer |
| `person_voss` | Alex Voss | Deputy Station Manager / Logistics |
| `person_castellano` | Morgan Castellano | Field Safety Officer |
| `person_whitfield` | Taylor Whitfield | Atmospheric Chemist |
| `person_mbeki` | Jordan Mbeki | Ice-Core Glaciologist |
| `person_lindqvist` | Dr. Sofia Lindqvist | Station Physician |
| `person_watanabe` | Kenji Watanabe | Power Systems / Generator Technician |
| `person_beliaeva` | Ana Beliaeva | Microbiology Researcher |
| `person_fuentes` | Diego Fuentes | Vehicle & Heavy Equipment Mechanic |
| `person_berger` | Nils Berger | Field Camp Delta Lead |
| `person_tanaka` | Yuki Tanaka | Field Camp Delta Second |
| `person_ondo` | Marcus Ondo | Station Chef / Stores |

Nils and Yuki are stationed at **Field Camp Delta**, 18 km from the main station,
for the whole season except for one resupply visit. The other 12 are based at
Meridian Station itself.

## Facility layout

```
Meridian Station
├── Main Hab (living quarters, mess, comms room, medical bay)
│    └── Airlock A — primary heated entrance, badge reader + door sensor
├── Generator Shed (Generator 1, Generator 2, fuel manifold incl. valve V-3)
│    └── connected to Vehicle Bay via a covered, unheated walkway (no sensor)
├── Vehicle Bay (snow vehicles, sledges, fuel drums)
│    └── overhead door sensor (exhaustive open/close log)
├── Science Wing (Atmospheric Chemistry Lab, Ice-Core Prep Lab a.k.a. "Lab B",
│    Biology Lab)
│    ├── Airlock B — secondary heated entrance, manual paper logbook only
│    └── Tunnel Door — underground tunnel to Main Hab, no sensor; a sign-in
│         clipboard was added at this door only starting Day 63 (post-incident)
└── Weather Mast — instrument tower ~40 m from Main Hab, continuous automated
     logger with two documented outage windows

Field Camp Delta (18 km away): two-person tent camp, HF radio only, scheduled
contact windows at 07:00 and 19:00 station time. No live telemetry link to the
station.
```

## Observability model

This section is the authoritative, closed-world definition of what generated
evidence, what was recorded, what remains accessible to the shipped corpus, and
what may be inferred. The corpus-generation process is bound by this table; no
memory may assert a fact outside what this model licenses.

| Channel | What it observes | Coverage | Known gaps | Accessible in corpus |
|---|---|---|---|---|
| Airlock A badge reader + door sensor | Every crossing of Airlock A, badge ID + timestamp | **Exhaustive** for Airlock A only | None — this reader has zero downtime all season | Yes (`sensor_airlockA_badge`) |
| Airlock B logbook | Crossings of Airlock B | **Incomplete** — a paper sheet crew are supposed to sign; compliance is spotty, especially on short trips | Unknown fraction of real crossings go unsigned; no way to bound the miss rate | Yes, but explicitly labeled non-exhaustive |
| Tunnel Door | Crossings of the Main Hab ↔ Science Wing tunnel | **Zero coverage Days 1–62**; a sign-in clipboard added Day 63, **near-complete Days 63–96** (station policy after the incident; still occasionally skipped on the clipboard by staff in a hurry) | Total absence before Day 63; sporadic misses after | Yes (post-63 only; pre-63 has no artifact to ingest, which is itself the point) |
| Vehicle Bay overhead door sensor | Every open/close cycle of the bay door | **Exhaustive** | None | Yes |
| Generator Shed valve V-3 position sensor (SCADA) | Continuous OPEN/CLOSED state of fuel valve V-3 | **Exhaustive except one 34-minute gap**, Day 41, 02:06–02:40, caused by a scheduled power-bus transfer test | The Day 41 gap is itself a first-class, dated fact in the corpus | Yes |
| Twice-daily roll call (08:00 / 20:00 station time) | Presence of all 12 Main-Station crew (Delta crew confirmed separately by radio) | **Exhaustive at the two sampled instants only** | Says nothing about anything between the two calls | Yes |
| Weather Mast automated logger | Wind, temperature, pressure, humidity | **Continuous with two documented outage windows**: (1) anemometer #2 iced over, Day 38 18:00 – Day 44 09:00, exact clearing moment not logged; (2) firmware crash, Day 71 03:10–03:50 | Outage windows are dated; behavior *during* an outage window is unobserved, not "normal" by default | Summary records yes; raw sub-minute archive lost (see Lost Evidence below) |
| Field Camp Delta radio log | Two scheduled contact windows/day, station-side log of what was said | **Only the two windows**; nothing between them is observed by the station | Days 58–61: total blackout, no contact at all (storm) | Yes |
| Station email/relay queue | Outgoing send status (queued/sent/failed) | **Exhaustive for status**, **not for content** — the satellite modem intermittently corrupts message bodies at the relay; a "sent" status does not guarantee a readable body survives | 6 known corrupted-body incidents this season | Status yes; several bodies inaccessible |
| Ice-core sample chain-of-custody log (Lab B) | Each sample's collection/prep timestamps | Per-sample logging is otherwise reliable, but **one entry (sample IC-14) has a blank timestamp field** from the pre-shipment repackaging scramble | Single internal gap, not a systemic one | Yes, gap included as-is |
| Personal diaries/journals | Whatever each crew member privately writes | Exist for several crew (mentioned in dialogue/logs) | **Private and never enter the shared station record**, except Nils Berger's Field Camp Delta journal, whose Day 65 entry is later read aloud on the radio and transcribed into the station log (see Resolution below) | Not accessible unless explicitly transcribed |
| Sealed personnel memo | Commander Kade's confidential note-to-file about an interpersonal conflict (filed, never detailed further) | Its **existence** is recorded (Kade mentions filing it); its **content** is confidential by station policy | N/A | Existence yes, content no — permanently, by design (not merely late-arriving) |
| Weather Mast raw high-frequency archive | Sub-minute-resolution raw sensor data for the whole season | Existed on a hot-swap drive that Taylor Whitfield reviewed before shipping | **Drive crushed in cargo damage on the final outbound supply flight (Day 96)** — the underlying data is gone; Taylor's written summary conclusions (filed Day 94, before the loss) survive | Summary yes; raw archive no, permanently |

### Closed-world guarantees (what may be treated as exhaustive)

The corpus-generation agent is licensed to treat the following as *complete
enumerations*, and only these:

1. **The 14-person winter-over roster** — no 15th person exists at Meridian
   Station or Field Camp Delta this season. Any query asking whether a person not
   on this roster was present has a justified `known_false` answer.
2. **Airlock A crossings** — exhaustive for that single doorway, for the whole
   season, with no downtime.
3. **Vehicle Bay door cycles** — exhaustive for the whole season.
4. **Roll-call presence at 08:00 and 20:00** — exhaustive *at those two instants
   only*; never extend to "and therefore present the rest of the day."
5. **Valve V-3 position** — exhaustive except the named Day 41 02:06–02:40 gap.
6. **The physical constraint that the ice-core transport sled (built for the
   Science Wing double-door bay) cannot fit through Airlock B or the Tunnel
   Door** — a stated engineering fact in the station's facilities log, licensing
   deduction (see Experimental Map, Control G / P07-H).

Nothing else in the station should be treated as exhaustively observed unless a
memory explicitly says so for that specific channel and window. In particular:
Airlock B, the Tunnel Door (pre-Day 63), personal movements inside Main Hab or
Science Wing between airlock crossings, Field Camp Delta between radio windows,
and the contents of any crew member's private time are **never** exhaustively
observed, and no combination of routine memories should be read as establishing
otherwise.

## Central incident (frame story)

Day 41, approximately 02:10–02:40: fuel valve V-3 in the Generator Shed is found
open, causing a contained diesel spill onto the shed floor (no injury, no fire —
cleaned up within the hour). Deputy Manager Alex Voss files Incident Report
IR-2031-07 the next day. The SCADA valve-position log has exactly the 34-minute
gap noted above, caused by a power-bus transfer test Kenji Watanabe was running
that night — an established, dated, legitimate maintenance activity, not a cover
story. Several crew were independently awake and moving around the station that
night for unrelated reasons (an aurora-camera data pull, an insomnia snack run, a
biology sample check), and partial sightings place two crew members
*near* — but not conclusively *at* — the Generator Shed around the relevant time.
Generator Shed maintenance logs separately establish that V-3's actuator had a
documented history of vibration-related drift.

**Objective world state (author's ground truth, for internal consistency only —
this is deliberately never fully resolvable from the shipped corpus and must not
leak into any memory or query):** the valve drifted open on its own due to the
known actuator wear; no one touched it that night. This is confirmed only in
part, and only weeks later, when Kenji replaces the actuator (Day 88) and finds
wear consistent with slow creep — evidence that narrows the space of explanations
without ever fully proving no human involvement. The corpus must preserve genuine
multi-world compatibility for "what caused the valve to open" through the end of
the season (Control F / §07.6) — no perturbation in this bundle resolves it.

## Resolution events (Control E / P07-E)

- **Field Camp Delta blackout, Days 58–61**: total radio silence during a storm.
  Whether Nils and Yuki relocated to the lee shelter per storm protocol is
  unknown for the duration of the blackout. Contact resumes Day 62; Nils's
  debrief and a Day 65 transcribed journal excerpt confirm the relocation
  occurred on Day 59. A query with an explicit "as of Day 60" cutoff must remain
  `unknown_missing`; the same question without a cutoff, asked after Day 65, is
  `known_true`.
- **Replacement satellite-modem part**: after repeated email-corruption
  incidents, the Program Office selects a replacement vendor (established by a
  terse Day 75 logistics note); the vendor's name was in the covering
  attachment, which itself was one of the corrupted message bodies — so the
  corpus establishes *that* a replacement was selected without ever naming the
  vendor (§07.9, known-but-unspecified). This one is never resolved in-bundle.

## Style and register

Sources are: logbook entries, SCADA/sensor exports, radio-transcript excerpts,
roll-call records, incident reports, maintenance logs, personal chat/intercom
messages, handover notes, email-status records, and season-end summary reports.
All content is fully synthetic; no real station, program, incident, or person is
being described. Tone stays low-stakes and procedural — the fuel spill is
contained and non-injurious, the HR memo is never detailed, and no content
depicts graphic harm.
