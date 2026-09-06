import json, collections, re, os, sys, hashlib
from datetime import datetime
E=sys.argv[1]
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def j(p): return json.load(open(p))
man=j(f"{E}/manifest.json")
print("== checksums")
bad=0
for f in man["files"]:
    p=f"{E}/{f['path']}"; b=open(p,"rb").read()
    ok = len(b)==f["bytes"] and hashlib.sha256(b).hexdigest()==f["sha256"]
    if not ok: bad+=1; print("  MISMATCH",f["path"],len(b),f["bytes"])
listed={f["path"] for f in man["files"]}
actual={os.path.relpath(os.path.join(r,fn),E) for r,_,fs in os.walk(E) for fn in fs}-{"manifest.json"}
print("  files checked",len(man["files"]),"mismatches",bad,"unlisted",actual-listed,"missing",listed-actual)
mem=jl(f"{E}/memories.jsonl"); q=jl(f"{E}/queries.jsonl"); prov=j(f"{E}/provenance.json"); ts=j(f"{E}/truth_state.json"); stats=j(f"{E}/analysis/corpus_stats.json")
mm={m["memory_id"]:m for m in mem}
print("== counts")
print(" memories",len(mem),man["canonical_memory_count"],stats["canonical_memory_count"]," queries",len(q),man["query_count"])
ids=[m["memory_id"] for m in mem]; print(" unique",len(set(ids))==len(ids)); nums=sorted(int(i.split("M")[1]) for i in ids); print(" range",nums[0],nums[-1],"gaps",[n for n in range(1,nums[-1]+1) if n not in set(nums)][:10])
print(" keysets",len({tuple(sorted(m.keys())) for m in mem}), collections.Counter(tuple(sorted(m.keys())) for m in mem).most_common(3) if len({tuple(sorted(m.keys())) for m in mem})>1 else "")
print(" truth_role",collections.Counter(m["truth_role"] for m in mem))
print(" derived count",sum(1 for m in mem if m["derived_from"]),"stats",stats["derived_memory_count"]," superseding",sum(1 for m in mem if m["supersedes"]),"stats",stats["superseding_memory_count"]," late_arrival tag",sum(1 for m in mem if "late_arrival" in m["tags"]),"stats",stats["late_arrival_tagged_count"])
print(" control/distractor",sum(1 for m in mem if "control" in m["tags"] or "distractor" in m["tags"]),"stats",stats["control_or_distractor_count"])
mt=collections.Counter(m["memory_type"] for m in mem); print(" memory_types match stats",mt==collections.Counter(stats["memory_types"]))
st=collections.Counter(m["source_type"] for m in mem); print(" source_types match stats",st==collections.Counter(stats["source_types"]))
tg=collections.Counter(t for m in mem for t in m["tags"]); print(" top_tags match", [(t,c) for t,c in stats["top_tags"]]==tg.most_common(len(stats["top_tags"])))
print("== timestamps")
def P(s): return datetime.fromisoformat(s.replace("Z","+00:00"))
viol=collections.Counter(); ex=[]
for m in mem:
    e,o,a,i=P(m["event_time"]),P(m["observation_time"]),P(m["authored_time"]),P(m["ingestion_time"])
    if not e<=o: viol["event>obs"]+=1; ex.append((m["memory_id"],"e>o",m["tags"]))
    if not o<=a: viol["obs>authored"]+=1; ex.append((m["memory_id"],"o>a",m["tags"]))
    if not a<=i: viol["authored>ingest"]+=1; ex.append((m["memory_id"],"a>i",m["tags"]))
print(" violations",dict(viol)); [print("   ",x) for x in ex[:15]]
print("== relations")
dang=[]; cnt=collections.Counter()
for m in mem:
    for f in ("derived_from","supersedes","contradicts","duplicates"):
        for r in m[f]:
            cnt[f]+=1
            if r not in mm: dang.append((m["memory_id"],f,r))
print(" counts",dict(cnt),"dangling",dang[:10])
# supersedes: superseding must have later authored/ingest? and derived_from: source event_time consistency
for m in mem:
    for r in m["supersedes"]:
        s=mm[r]
        if P(m["authored_time"])<P(s["authored_time"]): print("  supersedes-before-original(authored)",m["memory_id"],"->",r,m["authored_time"],s["authored_time"])
# derived_from cycles / self
for m in mem:
    if m["memory_id"] in m["derived_from"]: print("  self-derived",m["memory_id"])
print("== provenance")
for root,d in prov["canonical_roots"].items():
    for x in d["primary_memories"]+d["derived"]:
        if x not in mm: print("  dangling prov ref",root,x)
    for x in d["derived"]:
        print(f"  {root} derived {x} derived_from={mm[x]['derived_from']} tags={mm[x]['tags']}")
for e in prov["correction_edges"]:
    print("  correction edge",e, "supersedes field of to:",mm[e["to"]]["supersedes"], "text from:",mm[e["from"]]["text"][:90],"| to:",mm[e["to"]]["text"][:90])
print("== queries")
print(" unique",len({x["query_id"] for x in q})==len(q)," keysets",len({tuple(sorted(x.keys())) for x in q}))
print(" categories",collections.Counter(x["category"] for x in q))
d=[(x["query_id"],r) for x in q for r in x["relevant_memory_ids"]+x["distractor_memory_ids"] if r not in mm]; print(" dangling refs",d)
print(" empty relevant",[x["query_id"] for x in q if not x["relevant_memory_ids"]])
print(" flags",{k:sum(1 for x in q if x.get(k)) for k in ("must_surface_uncertainty","must_surface_conflict","must_disambiguate","must_preserve_scope","should_abstain","run_invariant")})
print(" required_source_roots nonempty",[(x["query_id"],x["required_source_roots"]) for x in q if x["required_source_roots"]][:10])
print(" expected_temporal_order nonempty",sum(1 for x in q if x["expected_temporal_order"]))
print(" nonempty notes",sum(1 for x in q if x["notes"]))
dupq=[k for k,v in collections.Counter(x["query"] for x in q).items() if v>1]; print(" dup query text",dupq)
print("== delivery runs")
allids=set(ids)
runs=sorted(os.listdir(f"{E}/delivery_runs"))
r00=j(f"{E}/delivery_runs/R00_canonical_ingestion.json")
for rf in runs:
    r=j(f"{E}/delivery_runs/{rf}")
    seq=r["delivery_sequence"]; c=collections.Counter(seq)
    extra={k:v for k,v in r.items() if k not in ("run_id","description","delivery_sequence")}
    missing=allids-set(seq); unknown=set(seq)-allids; reps=[k for k,v in c.items() if v>1]
    print(f"  {rf}: len={len(seq)} uniq={len(set(seq))} missing={len(missing)} unknown={len(unknown)} replayed={len(reps)} sameAsR00={seq==r00['delivery_sequence']} extra_keys={list(extra.keys())} desc={r['description'][:80]}")
    if unknown: print("     unknown",sorted(unknown)[:5])
    if reps and len(reps)<40: print("     replayed",reps)
    if extra: print("     extra", json.dumps(extra)[:600])
# R00 order vs ingestion_time sort
seq=r00["delivery_sequence"]
srt=sorted(mem,key=lambda m:(P(m["ingestion_time"]),m["memory_id"]))
print(" R00 == sort by ingestion_time?", [m["memory_id"] for m in srt]==seq)
srt2=sorted(mem,key=lambda m:P(m["ingestion_time"]))
inv=sum(1 for a,b in zip(seq,seq[1:]) if P(mm[a]["ingestion_time"])>P(mm[b]["ingestion_time"])); print(" R00 ingestion-time inversions",inv)
print("== checkpoints")
cp=j(f"{E}/checkpoints/R00_progressive.json")
for k,v in cp.items():
    ok = v["available_memory_ids"]==seq[:int(k)] and v["count"]==len(v["available_memory_ids"])
    ex={kk:vv for kk,vv in v.items() if kk not in("count","available_memory_ids")}
    print(f"  cp {k}: prefix-of-R00={ok} count={v['count']} extra={json.dumps(ex)[:400]}")
print("== truth vs text")
for m in ["K10-M017","K10-M018","K10-M008","K10-M009","K10-M010","K10-M020","K10-M021","K10-M040","K10-M041","K10-M029","K10-M030","K10-M038"]:
    x=mm[m]; print(f"  {m} e={x['event_time']} i={x['ingestion_time']} {x['truth_role']} {x['memory_type']} sup={x['supersedes']} df={x['derived_from']}\n     {x['text'][:200]}")
