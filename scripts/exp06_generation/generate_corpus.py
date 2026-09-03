#!/usr/bin/env python3
"""
Experiment 06 — Roots, Echoes, and Evidence Lineage
Corpus generator.

Design principle (Stage 2 invariant): the provenance graph topology for every
instance is defined FIRST, as pure data (node types, edges, evidence-root
flags, cycle membership, unsupported-claim flags, retrievability), and memory
text is rendered from that topology afterward. Nothing about lineage is
decided while writing prose.

Run: python3 generate_corpus.py
Deterministic given FIXED SEED below.
"""
import json, random, hashlib, os, sys
from collections import defaultdict

SEED = 20260614
random.seed(SEED)

OUT_DIR = os.environ.get("EXP06_OUT", "/tmp/claude-0/exp06_build")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# STORY WORLD
# ---------------------------------------------------------------------------

COMPANY = "Thornfield Systems"
PRODUCT_LINE = "Sentinel"  # remote industrial monitoring units

PEOPLE = {
    "priya_nandakumar":  {"name": "Priya Nandakumar",  "role": "Senior Field Engineer"},
    "marcus_oyelaran":   {"name": "Marcus Oyelaran",   "role": "On-call SRE"},
    "dana_ferreira":     {"name": "Dana Ferreira",     "role": "Customer Success Lead"},
    "wei_tan":           {"name": "Wei Tan",           "role": "Reliability Engineer"},
    "sofia_kowalczyk":   {"name": "Sofia Kowalczyk",   "role": "QA / Test Engineer"},
    "amir_hossain":      {"name": "Amir Hossain",      "role": "Firmware Engineer"},
    "lena_vogt":         {"name": "Lena Vogt",         "role": "Program Manager"},
    "oscar_delgado":     {"name": "Oscar Delgado",     "role": "Support Engineer"},
    "ingrid_solberg":    {"name": "Ingrid Solberg",    "role": "VP Engineering"},
    "tobias_reyes":      {"name": "Tobias Reyes",      "role": "Technical Writer"},
    "harriet_okafor":    {"name": "Harriet Okafor",    "role": "Site Reliability Manager"},
    "felix_nakamura":    {"name": "Felix Nakamura",    "role": "Data/Analytics Engineer"},
    "grace_moreau":      {"name": "Grace Moreau",      "role": "Independent Auditor (3rd party)"},
    "dmitri_pavlenko":   {"name": "Dmitri Pavlenko",   "role": "Customer Facility Technician (Ashgrove)"},
    "nadia_husseini":    {"name": "Nadia Husseini",    "role": "Customer Facility Technician (Brackwater)"},
    "leo_bertrand":      {"name": "Leo Bertrand",      "role": "Field Engineer"},
    "ai_summarizer":     {"name": "Thornfield Assist (internal AI summarizer)", "role": "automated tool"},
}

SITES = [
    "Ashgrove Processing Plant", "Brackwater Terminal", "Caldera Fabrication Yard",
    "Duskford Cold Storage", "Elmsgate Refinery Annex", "Farrow Point Substation",
    "Greywick Water Treatment", "Halden Ridge Mine", "Ironmoor Foundry",
    "Juniper Bay Desalination",
]

SUBSYSTEMS = [
    "coolant pump P-{n}", "temperature probe T-{n}", "vibration sensor V-{n}",
    "relay valve R-{n}", "intake compressor C-{n}", "backup generator G-{n}",
]

UNIT_IDS = [f"SN-{n}" for n in random.sample(range(1000, 9999), 60)]

# ---------------------------------------------------------------------------
# GLOBAL STATE for assembly
# ---------------------------------------------------------------------------

memories = []          # final memory_record dicts
memory_seq = 0
claim_seq = 0
fact_seq = 0
family_index = defaultdict(int)

def next_memory_id():
    global memory_seq
    memory_seq += 1
    return f"e06m_{memory_seq:04d}"

def next_claim_id():
    global claim_seq
    claim_seq += 1
    return f"e06c_{claim_seq:04d}"

def next_fact_id():
    global fact_seq
    fact_seq += 1
    return f"F06-{fact_seq:03d}"

def pick_site(rng):
    return rng.choice(SITES)

def pick_subsystem(rng):
    tmpl = rng.choice(SUBSYSTEMS)
    return tmpl.format(n=rng.randint(1, 9))

def pick_unit(rng):
    return rng.choice(UNIT_IDS)

def date_add(base, days):
    import datetime
    y, m, d = [int(x) for x in base.split("-")]
    dt = datetime.date(y, m, d) + datetime.timedelta(days=days)
    return dt.isoformat()

BASE_DATE = "2026-05-04"  # incident window start

SCOPE_KEYS = ["project","team","environment","platform","region","facility",
              "version","customer_tier","employment_class","release_channel","authority"]

def blank_scope():
    return {k: None for k in SCOPE_KEYS}

MEMORY_TYPE_TO_SOURCE_TYPE = {}  # identical in this experiment

# ---------------------------------------------------------------------------
# NODE HELPER
# ---------------------------------------------------------------------------

class Node:
    """One local node in a family-instance topology graph, pre-assembly."""
    def __init__(self, local_id, node_type, memory_type, author, day_offset,
                 text_fn, derived_from=(), is_evidence_root=False,
                 adds_new_evidence=None, retrievable=True, unsupported_clause=None,
                 truth_role="scoped_true", contradicts_root=False, tags_extra=None,
                 claims_override=None):
        self.local_id = local_id
        self.node_type = node_type            # primary_observation | interpretation | derived_summary
                                                # | quoted_claim | copied_claim | transformed_claim
                                                # | model_generated | reingested | evidence_root
        self.memory_type = memory_type
        self.author = author
        self.day_offset = day_offset
        self.text_fn = text_fn                # fn(ctx) -> str
        self.derived_from = list(derived_from)
        self.is_evidence_root = is_evidence_root
        self.adds_new_evidence = (is_evidence_root if adds_new_evidence is None else adds_new_evidence)
        self.retrievable = retrievable
        self.unsupported_clause = unsupported_clause  # extra sentence fn(ctx)->str with no support, or None
        self.truth_role = truth_role
        self.contradicts_root = contradicts_root
        self.tags_extra = tags_extra or []
        self.claims_override = claims_override  # optional list of (claim_text_fn, supported: bool, support_roots_local: list)

# ---------------------------------------------------------------------------
# FAMILY BUILDERS
# Each returns list[Node] describing ONE instance's topology.
# ctx dict carries site/subsystem/unit/people/base_date for text rendering.
# ---------------------------------------------------------------------------

def ctx_for(rng, extra_people=None):
    site = pick_site(rng)
    subsystem = pick_subsystem(rng)
    unit = pick_unit(rng)
    base = date_add(BASE_DATE, rng.randint(0, 95))
    return {"site": site, "subsystem": subsystem, "unit": unit, "base": base}

# --- 06.1 Citation cascade: E1 -> N1 -> C1 -> S1 -> S2 -> S3 -------------

def build_cascade(rng, ctx):
    nodes = []
    nodes.append(Node("E1", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: pressure reading dropped "
                  f"from 4.1 bar to 0.6 bar at {c['base']}T14:02:11Z. Auto-shutdown triggered at 14:02:19Z.",
        is_evidence_root=True))
    nodes.append(Node("N1", "primary_observation", "field_note", "priya_nandakumar", 1,
        lambda c: f"Field note: inspected {c['unit']} {c['subsystem']} at {c['site']} after the auto-shutdown "
                  f"flagged in the sensor log at {c['base']}T14:02Z. Pressure sensor confirms the drop; "
                  f"seal appears intact on visual inspection.",
        derived_from=["E1"]))
    nodes.append(Node("C1", "interpretation", "issue_comment", "marcus_oyelaran", 2,
        lambda c: f"Ticket comment: per Priya's field note, {c['unit']} {c['subsystem']} tripped on a pressure "
                  f"drop around 14:02Z on {c['base']}. Logging as the root cause candidate for INC-{rng.randint(4000,4999)}.",
        derived_from=["N1"]))
    nodes.append(Node("S1", "derived_summary", "postmortem_report", "wei_tan", 5,
        lambda c: f"Postmortem summary: {c['unit']} {c['subsystem']} at {c['site']} experienced a pressure-drop "
                  f"trip on {c['base']}, consistent with field inspection and the originating sensor log.",
        derived_from=["C1"]))
    nodes.append(Node("S2", "transformed_claim", "status_email", "lena_vogt", 8,
        lambda c: f"Status update: the {c['site']} incident (pressure trip, {c['unit']}) has a completed "
                  f"postmortem; root cause confirmed as a pressure drop in {c['subsystem']}.",
        derived_from=["S1"]))
    nodes.append(Node("S3", "copied_claim", "executive_deck", "ingrid_solberg", 12,
        lambda c: f"Leadership deck bullet: {c['site']} — pressure-drop trip in {c['subsystem']}, root cause "
                  f"confirmed, postmortem closed.",
        derived_from=["S2"]))
    return nodes

# --- 06.2 Branching descendants: E1 -> note -> {report A,B, ticket C, summary D}

def build_fanout(rng, ctx, fanout_n=4):
    nodes = []
    nodes.append(Node("E1", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: vibration RMS exceeded "
                  f"threshold (6.2 mm/s) at {c['base']}T09:14Z, sustained for 40s.",
        is_evidence_root=True))
    nodes.append(Node("note", "primary_observation", "field_note", "leo_bertrand", 1,
        lambda c: f"Field note: vibration excursion on {c['unit']} {c['subsystem']} at {c['site']} matches the "
                  f"09:14Z telemetry alert; bearing wear suspected pending teardown.",
        derived_from=["E1"]))
    labels = ["reportA","reportB","ticketC","summaryD","noteE","emailF","wikiG","deckH",
              "retroI","briefJ","memoK","digestL","tickerM","alertN","chatO","logP",
              "flashQ","syncR","updateS","recapT"]
    kinds = [
        ("technical_note", "harriet_okafor"), ("customer_email", "dana_ferreira"),
        ("incident_ticket", "marcus_oyelaran"), ("postmortem_report", "wei_tan"),
        ("wiki_page", "tobias_reyes"), ("status_email", "lena_vogt"),
        ("chat_message", "oscar_delgado"), ("executive_deck", "ingrid_solberg"),
        ("retrospective_report", "harriet_okafor"), ("customer_email", "dana_ferreira"),
        ("technical_note", "felix_nakamura"), ("status_email", "lena_vogt"),
        ("chat_message", "marcus_oyelaran"), ("wiki_page", "tobias_reyes"),
        ("chat_message", "oscar_delgado"), ("technical_note", "sofia_kowalczyk"),
        ("status_email", "dana_ferreira"), ("chat_message", "harriet_okafor"),
        ("status_email", "lena_vogt"), ("retrospective_report", "wei_tan"),
    ]
    for i in range(fanout_n):
        lbl = labels[i % len(labels)]
        mtype, author = kinds[i % len(kinds)]
        idx = i
        nodes.append(Node(f"desc{idx}", "transformed_claim", mtype, author, 2 + (idx % 5),
            (lambda c, ii=idx, mt=mtype: f"[{mt}] Re: {c['unit']} {c['subsystem']} vibration excursion at "
                                          f"{c['site']} on {c['base']} — flagged for follow-up (copy {ii+1})."),
            derived_from=["note"]))
    return nodes

# --- 06.3 Convergent independent evidence: E1,E2,E3 -> conclusion C -----

def build_convergent(rng, ctx):
    nodes = []
    nodes.append(Node("E1", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: internal temperature reached "
                  f"71.4C at {c['base']}T16:40Z, above the 65C operating ceiling.",
        is_evidence_root=True))
    nodes.append(Node("E2", "evidence_root", "scada_log", "system:customer_scada", 0,
        lambda c: f"[Customer SCADA log, {c['site']}] Independent facility monitoring shows {c['subsystem']} "
                  f"zone temperature at 71.1C at {c['base']}T16:41Z, logged by the site's own historian, "
                  f"no data path shared with Thornfield telemetry.",
        is_evidence_root=True))
    nodes.append(Node("E3", "evidence_root", "technician_note", "dmitri_pavlenko", 0,
        lambda c: f"[Facility technician note, {c['site']}] Touched the {c['subsystem']} housing at "
                  f"{c['base']}T16:45Z during a routine walk-through, unaware of any alert; housing was "
                  f"noticeably hot, consistent with an overtemperature condition around that time.",
        is_evidence_root=True))
    nodes.append(Node("C", "derived_summary", "postmortem_report", "wei_tan", 3,
        lambda c: f"Postmortem: {c['subsystem']} at {c['site']} ran hot on {c['base']} — confirmed independently "
                  f"by Thornfield telemetry, the customer's own SCADA historian, and an unprompted technician "
                  f"physical observation. Three independent evidence roots.",
        derived_from=["E1","E2","E3"]))
    return nodes

# --- 06.4 Hidden shared root: two "independent"-looking reports share root

def build_hidden_root(rng, ctx):
    nodes = []
    other_site = rng.choice([s for s in SITES if s != ctx["site"]])
    nodes.append(Node("E1", "evidence_root", "chat_message", "harriet_okafor", 0,
        lambda c: f"[Internal ops channel, unattributed relay] Fleet-wide firmware push v{rng.randint(3,9)}."
                  f"{rng.randint(0,9)} to {PRODUCT_LINE} units is being paused; early telemetry shows a "
                  f"handful of units reporting intermittent relay dropouts after the push.",
        is_evidence_root=True))
    nodes.append(Node("path1_note", "interpretation", "field_note", "leo_bertrand", 1,
        lambda c: f"Field note ({c['site']}): heard from the ops channel that some fleet units are seeing "
                  f"dropouts after the firmware push; checked {c['unit']} here and it also dropped a relay "
                  f"connection around the same window.",
        derived_from=["E1"]))
    nodes.append(Node("reportA", "transformed_claim", "postmortem_report", "wei_tan", 3,
        lambda c: f"Postmortem, {c['site']}: {c['unit']} relay dropout observed independently at this site "
                  f"following the firmware push, based on on-site inspection.",
        derived_from=["path1_note"]))
    nodes.append(Node("path2_note", "interpretation", "field_note", "sofia_kowalczyk", 1,
        lambda c, os=other_site: f"Field note ({os}): saw the same ops-channel mention of relay dropouts after "
                  f"the firmware push; the local unit here shows a matching drop in the relay heartbeat log.",
        derived_from=["E1"]))
    nodes.append(Node("reportB", "transformed_claim", "postmortem_report", "harriet_okafor", 3,
        lambda c, os=other_site: f"Postmortem, {os}: relay dropout confirmed at this site after the firmware "
                  f"push, based on local heartbeat log review.",
        derived_from=["path2_note"]))
    return nodes

# --- 06.5 Summary-of-summary depth chains: depth 1/2/4/8 -----------------

def build_depth_chain(rng, ctx, depth):
    nodes = []
    nodes.append(Node("D0", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: flow rate dropped to 12% of "
                  f"nominal at {c['base']}T02:11Z.",
        is_evidence_root=True))
    stage_types = ["field_note", "issue_comment", "technical_note", "postmortem_report",
                   "status_email", "wiki_page", "retrospective_report", "executive_deck"]
    stage_authors = ["priya_nandakumar","marcus_oyelaran","wei_tan","harriet_okafor",
                      "lena_vogt","tobias_reyes","felix_nakamura","ingrid_solberg"]
    prev = "D0"
    for depth_i in range(1, depth + 1):
        nid = f"D{depth_i}"
        mtype = stage_types[(depth_i - 1) % len(stage_types)]
        author = stage_authors[(depth_i - 1) % len(stage_authors)]
        nodes.append(Node(nid, "transformed_claim", mtype, author, depth_i,
            (lambda c, dd=depth_i, mt=mtype: f"[{mt}, derivation depth {dd}] {c['unit']} {c['subsystem']} at "
                                              f"{c['site']} had a flow-rate drop on {c['base']}; carried forward "
                                              f"from the prior-stage writeup without new measurement."),
            derived_from=[prev]))
        prev = nid
    return nodes

# --- 06.6 Partial provenance loss: derived claim retains only some roots

def build_partial_loss(rng, ctx):
    nodes = []
    nodes.append(Node("E1", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: current draw spiked to 18A "
                  f"at {c['base']}T11:05Z (nominal ceiling 12A).",
        is_evidence_root=True))
    nodes.append(Node("E2", "evidence_root", "field_note", "priya_nandakumar", 0,
        lambda c: f"Field note: motor housing on {c['unit']} {c['subsystem']} at {c['site']} showed discoloration "
                  f"consistent with an overcurrent event, inspected {c['base']}.",
        is_evidence_root=True, retrievable=True,
        tags_extra=["provenance_dropped_in_later_derivative"]))
    nodes.append(Node("mid", "derived_summary", "technical_note", "wei_tan", 2,
        lambda c: f"Technical note: overcurrent event on {c['unit']} {c['subsystem']} at {c['site']}, drawing on "
                  f"the current-draw telemetry and the field inspection.",
        derived_from=["E1","E2"]))
    nodes.append(Node("late", "derived_summary", "wiki_page", "tobias_reyes", 20,
        lambda c: f"Wiki summary (written later, field-note detail no longer linked in the tracker): "
                  f"overcurrent event on {c['unit']} {c['subsystem']} at {c['site']}, per the current-draw "
                  f"telemetry.",
        derived_from=["E1"],
        tags_extra=["partial_provenance"]))
    return nodes

# --- 06.7 Unsupported claim injection (+ Control F grounded sibling) ----

def build_unsupported(rng, ctx, grounded_only=False):
    nodes = []
    nodes.append(Node("A", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: pump stopped at "
                  f"{c['base']}T14:02:00Z.",
        is_evidence_root=True))
    nodes.append(Node("B", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: coolant temperature rose steadily "
                  f"beginning {c['base']}T14:03Z, reaching +9C above baseline by 14:20Z.",
        is_evidence_root=True))
    if grounded_only:
        nodes.append(Node("S", "derived_summary", "postmortem_report", "wei_tan", 3,
            lambda c: f"Postmortem: the pump on {c['unit']} {c['subsystem']} at {c['site']} stopped at "
                      f"{c['base']}T14:02Z, and coolant temperature rose afterward, consistent with loss of "
                      f"circulation. Both observations are drawn from telemetry.",
            derived_from=["A","B"]))
    else:
        nodes.append(Node("S", "derived_summary", "postmortem_report", "wei_tan", 3,
            lambda c: f"Postmortem: the pump on {c['unit']} {c['subsystem']} at {c['site']} stopped at "
                      f"{c['base']}T14:02Z, causing the coolant temperature to rise, because of a known "
                      f"firmware bug in the pump controller.",
            derived_from=["A","B"],
            unsupported_clause=lambda c: "because of a known firmware bug in the pump controller",
            truth_role="partially_true"))
    return nodes

# --- 06.8 Circular citation (+ P06-E acyclic sibling) --------------------

def build_circular(rng, ctx, cyclic=True):
    nodes = []
    if cyclic:
        nodes.append(Node("A", "interpretation", "incident_ticket", "marcus_oyelaran", 0,
            lambda c: f"Ticket A: {c['unit']} {c['subsystem']} at {c['site']} — root cause per the retro "
                      f"writeup (see ticket C) is a stuck relay valve.",
            derived_from=["C"], tags_extra=["cycle_member"]))
        nodes.append(Node("B", "interpretation", "wiki_page", "tobias_reyes", 1,
            lambda c: f"Wiki B: per ticket A, {c['unit']} {c['subsystem']} at {c['site']} failed due to a "
                      f"stuck relay valve.",
            derived_from=["A"], tags_extra=["cycle_member"]))
        nodes.append(Node("C", "transformed_claim", "retrospective_report", "harriet_okafor", 2,
            lambda c: f"Retro C: consistent with the wiki writeup (B), {c['unit']} {c['subsystem']} at {c['site']} "
                      f"failed due to a stuck relay valve.",
            derived_from=["B"], tags_extra=["cycle_member"]))
    else:
        nodes.append(Node("root", "evidence_root", "field_note", "priya_nandakumar", 0,
            lambda c: f"Field note: {c['unit']} {c['subsystem']} at {c['site']} — stuck relay valve found during "
                      f"teardown.",
            is_evidence_root=True))
        nodes.append(Node("A", "interpretation", "incident_ticket", "marcus_oyelaran", 1,
            lambda c: f"Ticket A: {c['unit']} {c['subsystem']} at {c['site']} — root cause per teardown is a "
                      f"stuck relay valve.",
            derived_from=["root"]))
        nodes.append(Node("B", "interpretation", "wiki_page", "tobias_reyes", 2,
            lambda c: f"Wiki B: per ticket A, {c['unit']} {c['subsystem']} at {c['site']} failed due to a "
                      f"stuck relay valve.",
            derived_from=["A"]))
        nodes.append(Node("C", "transformed_claim", "retrospective_report", "harriet_okafor", 3,
            lambda c: f"Retro C: consistent with the wiki writeup (B), {c['unit']} {c['subsystem']} at {c['site']} "
                      f"failed due to a stuck relay valve.",
            derived_from=["B"]))
    return nodes

# --- 06.9 Provenance contradiction ---------------------------------------

def build_contradiction(rng, ctx):
    nodes = []
    nodes.append(Node("E7", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: unit remained ONLINE throughout "
                  f"{c['base']}, no fault codes recorded.",
        is_evidence_root=True))
    nodes.append(Node("D", "transformed_claim", "status_email", "lena_vogt", 4,
        lambda c: f"Status email: per the {c['base']} telemetry (E7) for {c['unit']} {c['subsystem']} at "
                  f"{c['site']}, the unit went OFFLINE for six hours and missed two scheduled readings.",
        derived_from=["E7"], contradicts_root=True, truth_role="corrected"))
    return nodes

# --- 06.10 Root substitution worlds (World A: 1 root, World B: 5 roots) --

def build_root_sub_world(rng, ctx, world):
    nodes = []
    claim_text = (lambda c: f"[Report] {c['unit']} {c['subsystem']} at {c['site']} logged an intermittent "
                             f"pressure fault on {c['base']}.")
    if world == "A":
        nodes.append(Node("root", "evidence_root", "sensor_log", "system:telemetry", 0,
            lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: intermittent pressure fault "
                      f"logged {c['base']}T05:00Z, single sensor channel.",
            is_evidence_root=True))
        report_authors = [("field_note","priya_nandakumar"), ("technical_note","wei_tan"),
                           ("chat_message","marcus_oyelaran"), ("status_email","lena_vogt"),
                           ("wiki_page","tobias_reyes")]
        for i, (mt, author) in enumerate(report_authors):
            nodes.append(Node(f"r{i}", "transformed_claim", mt, author, i + 1,
                (lambda c, ii=i, mt2=mt: f"[{mt2}, copy {ii+1}] {c['unit']} {c['subsystem']} at {c['site']} "
                                         f"logged an intermittent pressure fault on {c['base']}, per the "
                                         f"telemetry channel."),
                derived_from=["root"]))
    else:
        roles = [
            ("sensor_log", "system:telemetry"), ("scada_log", "system:customer_scada"),
            ("technician_note", "dmitri_pavlenko"), ("test_bench_report", "sofia_kowalczyk"),
            ("weather_station_log", "system:site_weather"),
        ]
        for i, (mt, author) in enumerate(roles):
            nodes.append(Node(f"root{i}", "evidence_root", mt, author, 0,
                (lambda c, ii=i, mt2=mt: f"[{mt2}, independent source {ii+1}] {c['unit']} {c['subsystem']} at "
                                         f"{c['site']} independently observed to have an intermittent pressure "
                                         f"fault around {c['base']}, via a separate instrument/observer."),
                is_evidence_root=True))
        nodes.append(Node("conv", "derived_summary", "postmortem_report", "wei_tan", 5,
            lambda c: f"Postmortem: {c['unit']} {c['subsystem']} at {c['site']} intermittent pressure fault on "
                      f"{c['base']}, confirmed by five independently instrumented observations.",
            derived_from=[f"root{i}" for i in range(5)]))
    return nodes

# --- 06.11 Source disappearance ------------------------------------------

def build_disappearance(rng, ctx):
    nodes = []
    nodes.append(Node("root", "evidence_root", "test_bench_report", "sofia_kowalczyk", -60,
        lambda c: f"[Vendor test-bench report, {c['unit']} pump component, archived] Component failed load "
                  f"testing at 1.4x rated pressure; report filed with the original component vendor.",
        is_evidence_root=True, retrievable=False,
        tags_extra=["historically_sourced", "root_inaccessible"]))
    nodes.append(Node("note", "interpretation", "field_note", "priya_nandakumar", 0,
        lambda c: f"Field note: {c['unit']} {c['subsystem']} at {c['site']} failure is consistent with the "
                  f"vendor test-bench finding on this pump component (report on file with the component vendor "
                  f"as of the original qualification cycle).",
        derived_from=["root"]))
    nodes.append(Node("report", "transformed_claim", "postmortem_report", "wei_tan", 3,
        lambda c: f"Postmortem: {c['unit']} {c['subsystem']} at {c['site']} failure traced to a known "
                  f"component limitation identified in vendor qualification testing.",
        derived_from=["note"]))
    return nodes

# --- 06.12 Generated-output re-entry -------------------------------------

def build_reentry(rng, ctx):
    nodes = []
    nodes.append(Node("E1", "evidence_root", "sensor_log", "system:telemetry", 0,
        lambda c: f"[Sensor log] {c['unit']} {c['subsystem']} at {c['site']}: three restart cycles logged "
                  f"between {c['base']}T03:00Z and 03:40Z.",
        is_evidence_root=True))
    nodes.append(Node("S1", "derived_summary", "postmortem_report", "wei_tan", 1,
        lambda c: f"Postmortem: {c['unit']} {c['subsystem']} at {c['site']} cycled three times overnight per "
                  f"telemetry; watchdog reset loop suspected.",
        derived_from=["E1"]))
    nodes.append(Node("M1", "model_generated", "ai_assistant_summary", "ai_summarizer", 2,
        lambda c: f"[Thornfield Assist summary] Based on the postmortem, {c['unit']} {c['subsystem']} at "
                  f"{c['site']} experienced a watchdog reset loop overnight on {c['base']}.",
        derived_from=["S1"], adds_new_evidence=False))
    nodes.append(Node("M2", "reingested", "wiki_page", "tobias_reyes", 3,
        lambda c: f"Wiki page (pasted from the assistant summary): {c['unit']} {c['subsystem']} at {c['site']} "
                  f"experienced a watchdog reset loop overnight on {c['base']}.",
        derived_from=["M1"], adds_new_evidence=False, tags_extra=["reingested_model_output"]))
    nodes.append(Node("R1", "copied_claim", "status_email", "lena_vogt", 5,
        lambda c: f"Status email: confirmed watchdog reset loop on {c['unit']} {c['subsystem']} at {c['site']} "
                  f"(see wiki writeup) overnight on {c['base']}.",
        derived_from=["M2"], adds_new_evidence=False))
    return nodes

# ---------------------------------------------------------------------------
# ASSEMBLY
# ---------------------------------------------------------------------------

FAMILY_TAG = {
    "cascade": "06.1", "fanout": "06.2", "convergent": "06.3", "hidden_root": "06.4",
    "depth_chain": "06.5", "partial_loss": "06.6", "unsupported": "06.7",
    "circular": "06.8", "contradiction": "06.9", "root_sub": "06.10",
    "disappearance": "06.11", "reentry": "06.12",
}

provenance_nodes = {}   # memory_id -> dict for provenance_graph.json
claim_records = []      # for claim_lineage.json
instances_registry = [] # for docs/EXPERIMENT_MAP + queries generation
sources_md_rows = []

def assemble_instance(family_key, fact_id, node_list, ctx, instance_meta):
    """Assign global memory_ids, remap derived_from, compute ultimate roots, emit memories + provenance nodes."""
    local_to_global = {}
    order = node_list  # already topologically sorted root-first by construction
    for n in order:
        local_to_global[n.local_id] = next_memory_id()

    # first pass: build memory records
    fam_memories = []
    for n in order:
        mid = local_to_global[n.local_id]
        global_derived = [local_to_global[d] for d in n.derived_from]
        full_text = n.text_fn(ctx)
        archived_text = None
        if not n.retrievable:
            archived_text = full_text
            text = (f"[RECORD NO LONGER RETRIEVABLE IN FULL — tombstone only. This source is known to have "
                     f"existed (source_id below) and is cited by descendant records, but its content is not "
                     f"currently retrievable from this corpus.]")
        else:
            text = full_text
        event_time = date_add(ctx["base"], n.day_offset)
        obs_time = date_add(event_time, 0 if n.day_offset == 0 else 0)
        ingest_time = date_add(event_time, 1)
        scope = blank_scope()
        scope["facility"] = ctx["site"]
        scope["project"] = ctx["subsystem"].split(" ")[-1]
        rec = {
            "memory_id": mid,
            "experiment": "06",
            "story_id": "thornfield_sentinel",
            "event_time": event_time,
            "observation_time": obs_time,
            "ingestion_time": ingest_time,
            "subject_text": f"{ctx['unit']} {ctx['subsystem']}",
            "subject_entity_id": ctx["unit"].replace("-", "_").lower(),
            "predicate": "incident_evidence",
            "object": ctx["site"].replace(" ", "_").lower(),
            "text": text,
            "memory_type": n.memory_type,
            "truth_role": "corrected" if n.contradicts_root else n.truth_role,
            "scope": scope,
            "source_id": f"src_{fact_id.lower()}_{n.local_id}",
            "source_type": n.memory_type,
            "derived_from": global_derived,
            "supersedes": [],
            "contradicts": [local_to_global[n.derived_from[0]]] if (n.contradicts_root and n.derived_from) else [],
            "aliases_used": [],
            "tags": ["exp06", f"family_{FAMILY_TAG[family_key]}", fact_id],
            "_oracle": {
                "fact_id": fact_id,
                "adversarial_family": FAMILY_TAG[family_key],
                "family_key": family_key,
                "node_type": "evidence_root" if n.is_evidence_root else n.node_type,
                "is_evidence_root": n.is_evidence_root,
                "adds_new_evidence": n.adds_new_evidence,
                "retrievable": n.retrievable,
                "author": PEOPLE.get(n.author, {"name": n.author, "role": "system"})["name"],
                "unsupported_clause": n.unsupported_clause(ctx) if n.unsupported_clause else None,
                "archived_text_dev_only": archived_text,
                "dev_flags": n.tags_extra,
                "instance_meta": instance_meta,
            },
        }
        fam_memories.append((n, rec))
        memories.append(rec)

    # second pass: compute ultimate_evidence_roots via traversal (cycle-safe)
    id_to_rec = {rec["memory_id"]: rec for _, rec in fam_memories}
    def ultimate_roots(mid, visiting=None):
        visiting = visiting or set()
        if mid in visiting:
            return set()  # cycle guard
        visiting = visiting | {mid}
        rec = id_to_rec.get(mid)
        if rec is None:
            return set()
        if rec["_oracle"]["is_evidence_root"]:
            return {mid}
        roots = set()
        for d in rec["derived_from"]:
            roots |= ultimate_roots(d, visiting)
        return roots

    for n, rec in fam_memories:
        mid = rec["memory_id"]
        roots = sorted(ultimate_roots(mid))
        cycle_member = "cycle_member" in n.tags_extra
        claim_id_supported = next_claim_id()
        node_entry = {
            "node_id": mid,
            "node_type": rec["_oracle"]["node_type"],
            "family": FAMILY_TAG[family_key],
            "fact_id": fact_id,
            "claims": [claim_id_supported] + ([next_claim_id()] if n.unsupported_clause else []),
            "derived_from": rec["derived_from"],
            "ultimate_evidence_roots": roots if not cycle_member else [],
            "ultimate_evidence_roots_note": (
                "unresolvable: node participates in a citation cycle" if cycle_member else None
            ),
            "adds_new_evidence": rec["_oracle"]["adds_new_evidence"],
            "retrievable": rec["_oracle"]["retrievable"],
            "contradicts_derivation_source": bool(rec["contradicts"]),
        }
        provenance_nodes[mid] = node_entry

        # claim-level lineage
        main_path = None
        if roots and not cycle_member:
            # pick shortest path to first root for illustration; full roots list still recorded
            main_path = [roots[0]] + rec["derived_from"][:1] + [mid] if rec["derived_from"] else [mid]
        claim_records.append({
            "claim_id": claim_id_supported,
            "memory_id": mid,
            "claim_text": rec["text"] if not n.unsupported_clause else rec["text"].split(n.unsupported_clause(ctx))[0].strip(),
            "supported": bool(roots) or n.is_evidence_root,
            "support": [{"root": r, "path": _shortest_path(id_to_rec, mid, r)} for r in roots] if roots else [],
            "cycle_member": cycle_member,
        })
        if n.unsupported_clause:
            claim_records.append({
                "claim_id": provenance_nodes[mid]["claims"][1],
                "memory_id": mid,
                "claim_text": n.unsupported_clause(ctx),
                "supported": False,
                "support": [],
                "cycle_member": False,
                "note": "unsupported assertion embedded in an otherwise sourced summary (Invariant 06-E)",
            })

    instances_registry.append({
        "fact_id": fact_id, "family_key": family_key, "family_tag": FAMILY_TAG[family_key],
        "site": ctx["site"], "subsystem": ctx["subsystem"], "unit": ctx["unit"],
        "memory_ids": [rec["memory_id"] for _, rec in fam_memories],
        "instance_meta": instance_meta,
    })
    for n, rec in fam_memories:
        sources_md_rows.append((rec["source_id"], rec["memory_type"], rec["_oracle"]["author"],
                                 fact_id, rec["memory_id"]))
    return fam_memories

def _shortest_path(id_to_rec, mid, root):
    from collections import deque
    q = deque([[mid]])
    seen = {mid}
    while q:
        path = q.popleft()
        cur = path[-1]
        if cur == root:
            return list(reversed(path))
        rec = id_to_rec.get(cur)
        if not rec:
            continue
        for d in rec["derived_from"]:
            if d not in seen:
                seen.add(d)
                q.append(path + [d])
    return [root, mid]

# ---------------------------------------------------------------------------
# INSTANTIATION PLAN
# ---------------------------------------------------------------------------

def run():
    rng_master = random.Random(SEED)

    def new_ctx():
        return ctx_for(rng_master)

    # 1. cascade x8
    for i in range(8):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("cascade", fid, build_cascade(rng_master, ctx), ctx, {"index": i})

    # 2. fanout: 6 normal (fanout=4) + 3 special P06-A (1,5,25)
    for i in range(6):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("fanout", fid, build_fanout(rng_master, ctx, fanout_n=4), ctx,
                           {"index": i, "fanout_n": 4})
    for fanout_n, tag in [(1, "P06-A_fanout1"), (5, "P06-A_fanout5"), (25, "P06-A_fanout25")]:
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("fanout", fid, build_fanout(rng_master, ctx, fanout_n=fanout_n), ctx,
                           {"perturbation": tag, "fanout_n": fanout_n})

    # 3. convergent x6
    for i in range(6):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("convergent", fid, build_convergent(rng_master, ctx), ctx, {"index": i})

    # 4. hidden_root x6
    for i in range(6):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("hidden_root", fid, build_hidden_root(rng_master, ctx), ctx, {"index": i})

    # 5. depth_chain: depths 1,2,4,8 x3 topic sets = 12 instances
    for topic_i in range(3):
        for depth in [1, 2, 4, 8]:
            ctx = new_ctx()
            fid = next_fact_id()
            assemble_instance("depth_chain", fid, build_depth_chain(rng_master, ctx, depth), ctx,
                               {"topic_index": topic_i, "depth": depth, "perturbation": "P06-C_depth"})

    # 6. partial_loss x6
    for i in range(6):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("partial_loss", fid, build_partial_loss(rng_master, ctx), ctx, {"index": i})

    # 7. unsupported x8 (6 unsupported + 2 grounded Control F siblings)
    for i in range(6):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("unsupported", fid, build_unsupported(rng_master, ctx, grounded_only=False), ctx,
                           {"index": i, "control": "G_partially_unsupported"})
    for i in range(2):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("unsupported", fid, build_unsupported(rng_master, ctx, grounded_only=True), ctx,
                           {"index": i, "control": "F_fully_supported"})

    # 8. circular x5 cyclic + 5 acyclic siblings (P06-E)
    for i in range(5):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("circular", fid, build_circular(rng_master, ctx, cyclic=True), ctx,
                           {"index": i, "cyclic": True})
    for i in range(5):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("circular", fid, build_circular(rng_master, ctx, cyclic=False), ctx,
                           {"index": i, "cyclic": False, "perturbation": "P06-E_acyclic_sibling"})

    # 9. contradiction x5
    for i in range(5):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("contradiction", fid, build_contradiction(rng_master, ctx), ctx, {"index": i})

    # 10. root_sub worlds x4 topic-pairs (A+B each)
    for i in range(4):
        ctx = new_ctx()
        fid_a = next_fact_id()
        assemble_instance("root_sub", fid_a, build_root_sub_world(rng_master, ctx, "A"), ctx,
                           {"index": i, "world": "A", "perturbation": "P06-B_root_substitution"})
        fid_b = next_fact_id()
        assemble_instance("root_sub", fid_b, build_root_sub_world(rng_master, ctx, "B"), ctx,
                           {"index": i, "world": "B", "perturbation": "P06-B_root_substitution",
                            "paired_with": fid_a})

    # 11. disappearance x5
    for i in range(5):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("disappearance", fid, build_disappearance(rng_master, ctx), ctx, {"index": i})

    # 12. reentry x5
    for i in range(5):
        ctx = new_ctx()
        fid = next_fact_id()
        assemble_instance("reentry", fid, build_reentry(rng_master, ctx), ctx, {"index": i})

    return

run()

print(f"Total memories: {len(memories)}")
print(f"Total claims: {len(claim_records)}")
print(f"Total fact instances: {len(instances_registry)}")

# ---------------------------------------------------------------------------
# WRITE memories.jsonl (strip nothing here; oracle stays for dev bundle)
# ---------------------------------------------------------------------------
with open(os.path.join(OUT_DIR, "memories.jsonl"), "w") as f:
    for rec in memories:
        f.write(json.dumps(rec) + "\n")

with open(os.path.join(OUT_DIR, "provenance_graph.json"), "w") as f:
    json.dump({"experiment": "06", "nodes": list(provenance_nodes.values())}, f, indent=2)

with open(os.path.join(OUT_DIR, "claim_lineage.json"), "w") as f:
    json.dump({"experiment": "06", "claims": claim_records}, f, indent=2)

with open(os.path.join(OUT_DIR, "instances_registry.json"), "w") as f:
    json.dump(instances_registry, f, indent=2)

with open(os.path.join(OUT_DIR, "sources_rows.json"), "w") as f:
    json.dump(sources_md_rows, f, indent=2)

print("Wrote base artifacts to", OUT_DIR)
