import json, collections, re, os, sys
from datetime import datetime
E=sys.argv[1]
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def j(p): return json.load(open(p))
mem=jl(f"{E}/memories.jsonl"); seed=jl(f"{E}/seed_memories.jsonl"); q=jl(f"{E}/queries.jsonl")
claims=j(f"{E}/causal_claims.json"); ev=j(f"{E}/causal_evidence.json"); graph=j(f"{E}/causal_graph.json")
ts=j(f"{E}/truth_state.json"); emap=j(f"{E}/experimental_map.json"); pert=j(f"{E}/perturbations/manifest.json"); man=j(f"{E}/manifest.json")
print("== counts vs manifest")
print(" memories",len(mem),"manifest",man["memory_count"])
print(" queries",len(q),"manifest",man["query_count"])
print(" claims",len(claims),"manifest",man["causal_claim_count"])
print(" cases",len(ts["cases"]),"manifest",man["case_count"])
bg=[m for m in mem if m["truth_role"]=="background"]
print(" background",len(bg),"manifest",man["background_memory_count"])
print(" perturbations",len(pert),"manifest",man["perturbation_count"], "traps",len(emap))
unres=[c for c in claims if c["status"]=="unresolved"]; print(" unresolved claims",len(unres),"cases",sorted({c["case_id"] for c in unres}),"manifest unresolved_case_count",man["unresolved_case_count"])
print("== ids")
ids=[m["memory_id"] for m in mem]; print(" unique ids",len(set(ids))==len(ids), "dups",[k for k,v in collections.Counter(ids).items() if v>1][:5])
nums=sorted(int(i[1:]) for i in ids); print(" id range",nums[0],nums[-1],"gaps",[n for n in range(nums[0],nums[-1]+1) if n not in set(nums)][:20])
print(" seed ⊆ memories", all(s["memory_id"] in set(ids) for s in seed), "seed count",len(seed))
memmap={m["memory_id"]:m for m in mem}
seed_diff=[s["memory_id"] for s in seed if memmap.get(s["memory_id"])!=s]
print(" seed records differing from memories:",len(seed_diff), seed_diff[:5])
print("== schema")
keys=collections.Counter(tuple(sorted(m.keys())) for m in mem); print(" key-set variants",len(keys))
print(" truth_role",collections.Counter(m["truth_role"] for m in mem))
print(" memory_type",collections.Counter(m["memory_type"] for m in mem).most_common())
print(" predicate",collections.Counter(m["predicate"] for m in mem).most_common(30))
print(" belief_holder non-null",sum(1 for m in mem if m["belief_holder"]))
print(" confidence null",sum(1 for m in mem if m["confidence"] is None))
print(" scope.case",collections.Counter(m["scope"].get("case") for m in mem))
print("== timestamps")
bad=[]
for m in mem:
    try:
        e=datetime.fromisoformat(m["event_time"]); o=datetime.fromisoformat(m["observation_time"]); i=datetime.fromisoformat(m["ingestion_time"])
        if not (e<=o<=i): bad.append((m["memory_id"],m["event_time"],m["observation_time"],m["ingestion_time"]))
    except Exception as ex: bad.append((m["memory_id"],"parse",str(ex)))
print(" event<=obs<=ingest violations",len(bad),bad[:5])
# case window check
cases={c["case_id"]:c for c in ts["cases"]}
import re
sb=open(f"{E}/story_bible.md").read()
win={}
for mm in re.finditer(r"## (C\d\d) —.*?\n- Start: (\S+)\n- End: (\S+)",sb): win[mm.group(1)]=(datetime.fromisoformat(mm.group(2)),datetime.fromisoformat(mm.group(3)))
out=[]
for m in mem:
    c=m["scope"].get("case")
    if c and c in win:
        e=datetime.fromisoformat(m["event_time"])
        if not (win[c][0]<=e<=win[c][1]): out.append((m["memory_id"],c,m["event_time"],m["tags"],m["memory_type"]))
print(" case-scoped memories outside story-bible window",len(out)); [print("   ",x) for x in out]
print("== relations")
allrefs=collections.Counter()
dangling=[]
for m in mem:
    for f in ("derived_from","supersedes","contradicts","duplicates"):
        for r in m[f]:
            allrefs[f]+=1
            if r not in memmap: dangling.append((m["memory_id"],f,r))
print(" relation counts",dict(allrefs),"dangling",dangling[:10])
print("== claims/evidence/graph")
cids={c["causal_claim_id"] for c in claims}; print(" evidence ids == claim ids",{e["causal_claim_id"] for e in ev}==cids)
gedges={(g["case_id"],e["source"],e["relation"],e["target"]) for g in graph for e in g["edges"]}
cedges={(c["case_id"],c["cause"],c["relation"],c["effect"]) for c in claims}
print(" graph edges == claim edges",gedges==cedges, "graph-only",gedges-cedges,"claim-only",cedges-gedges)
for e in ev:
    s,c=e["supporting_evidence"],e["contradicting_evidence"]
    dang=[x for x in s+c if x not in memmap]
    both=sorted(set(s)&set(c))
    cl=next(x for x in claims if x["causal_claim_id"]==e["causal_claim_id"])
    cases_of=collections.Counter(memmap[x]["scope"].get("case") for x in s+c if x in memmap)
    flags=[]
    if not s: flags.append("NO_SUPPORT")
    if both: flags.append(f"BOTH={both}")
    if dang: flags.append(f"DANGLING={dang}")
    if any(k!=cl["case_id"] for k in cases_of): flags.append(f"CROSS_CASE={dict(cases_of)}")
    print(f"  {e['causal_claim_id']} {cl['case_id']} {cl['status']:18} sup={len(s)} con={len(c)} {' '.join(flags)}")
# identical evidence lists across claims
sig=collections.defaultdict(list)
for e in ev: sig[(tuple(e["supporting_evidence"]),tuple(e["contradicting_evidence"]))].append(e["causal_claim_id"])
print(" claims sharing identical evidence lists:",[v for v in sig.values() if len(v)>1 and v!=[]])
print("== queries")
qids=[x["query_id"] for x in q]; print(" unique",len(set(qids))==len(qids))
print(" categories",collections.Counter(x["category"] for x in q))
print(" keys variants",len({tuple(sorted(x.keys())) for x in q}))
d=[(x["query_id"],r) for x in q for r in x["relevant_memory_ids"]+x["distractor_memory_ids"] if r not in memmap]
print(" dangling relevant/distractor refs",len(d),d[:5])
print(" empty relevant",[x["query_id"] for x in q if not x["relevant_memory_ids"]])
print(" empty expected_claims",[x["query_id"] for x in q if not x["expected_claims"]])
print(" flags:",{k:sum(1 for x in q if x[k]) for k in ("must_surface_uncertainty","must_surface_conflict","must_disambiguate","must_preserve_scope","should_abstain")})
print(" any acceptable/forbidden non-empty:",sum(1 for x in q if x["acceptable_claims"]),sum(1 for x in q if x["forbidden_claims"]))
print(" nonempty notes",sum(1 for x in q if x["notes"]))
# dup query texts
qt=collections.Counter(x["query"] for x in q); print(" duplicate query texts",[k for k,v in qt.items() if v>1])
# unresolved cases: do queries about them require uncertainty?
for x in q:
    if x["category"]=="causal_status":
        rel_cases={memmap[r]["scope"].get("case") for r in x["relevant_memory_ids"] if r in memmap}
        print(f"  {x['query_id']} cases={sorted(c for c in rel_cases if c)} unc={x['must_surface_uncertainty']} conf={x['must_surface_conflict']} abst={x['should_abstain']} :: {x['query'][:70]}")
# relevant ids by case consistency
print("== query relevant-id case consistency")
for x in q:
    rel=x["relevant_memory_ids"]
    cs=collections.Counter(memmap[r]["scope"].get("case") for r in rel if r in memmap)
    m=re.search(r"\bC(\d\d)\b",x["query"])
    if m and len(cs)>0:
        qc="C"+m.group(1)
        if any(k!=qc for k in cs): print("  MISMATCH",x["query_id"],qc,dict(cs),x["query"][:80])
print("== leakage: truth text in memory text / official claims")
for c in ts["cases"]:
    hits=[m["memory_id"] for m in mem if c["truth"].lower()[:60] in m["text"].lower()]
    if hits: print("  truth sentence appears verbatim in",c["case_id"],hits)
words=["not causal","noncausal","objective causal truth","ground truth","root cause was","truth:"]
for w in words:
    h=[m["memory_id"] for m in mem if w in m["text"].lower()]
    if h: print(f"  '{w}' in {len(h)} memories e.g. {h[:6]}")
