import json,glob,os,statistics,collections,sys
ROOT=sys.argv[1]
FEATS=["f1","f3","f4","f5","f6","raw_x","raw_y","ewma_x","ewma_y","p_stuck","p_flow","p_inc"]

def cindex(pairs):
    """pairs=[(v,q)] 方向付き順序 C-index: v の大小と q の大小の一致率。tie(v)=0.5"""
    c=0.0; n=0
    for i in range(len(pairs)):
        for j in range(i+1,len(pairs)):
            (v1,q1),(v2,q2)=pairs[i],pairs[j]
            if q1==q2: continue
            n+=1
            if v1==v2: c+=0.5
            elif (v1>v2)==(q1>q2): c+=1.0
    return c/n if n else None

per=collections.defaultdict(lambda: collections.defaultdict(list))
counts=collections.Counter()
for pid in sorted(os.listdir(ROOT)):
    d=os.path.join(ROOT,pid)
    if not pid.startswith("P0") or not os.path.isdir(d): continue
    for f in sorted(glob.glob(d+"/*.ndjson")):
        feats=[]; labels=[]
        for l in open(f):
            l=l.strip()
            if not l: continue
            try: o=json.loads(l)
            except: continue
            if o.get("type")=="feat": feats.append(o)
            elif o.get("type")=="realtime_label" and o.get("source")=="random_probe" and o.get("answered"):
                labels.append(o)
        feats.sort(key=lambda o:o["t"])
        for lb in labels:
            ws,we=lb["analysis_window_start_ms"],lb["analysis_window_end_ms"]
            win=[o for o in feats if ws<=o["t"]<=we]
            if not win: counts["no_feat_in_window"]+=1; continue
            counts["usable"]+=1
            row={k:statistics.median([o[k] for o in win if k in o]) for k in FEATS if any(k in o for o in win)}
            per[pid]["__q1"].append(lb["q1_friction"]); per[pid]["__q2"].append(lb["q2_progress"])
            for k in FEATS: per[pid][k].append(row.get(k))

print(f"# 窓内 feat あり={counts['usable']} / feat無しで除外={counts['no_feat_in_window']}\n")
for target in ("__q1","__q2"):
    nm="Q1 摩擦" if target=="__q1" else "Q2 前進"
    print(f"########## 各特徴量 → {nm} の C-index (0.5=偶然)")
    print(f"{'feature':<9}"+"".join(f"{p:>9}" for p in sorted(per))+f"{'|pooled':>10}")
    allq={}
    for k in FEATS:
        line=f"{k:<9}"; pool=[]
        for p in sorted(per):
            q=per[p][target]; v=per[p][k]
            pr=[(a,b) for a,b in zip(v,q) if a is not None]
            ci=cindex(pr)
            line+=f"{ci:>9.3f}" if ci is not None else f"{'—':>9}"
            pool+= [(a,b) for a,b in pr]
        # pooled は被験者間の絶対値差が混ざるので参考値
        pc=cindex(pool)
        line+=f"{pc:>10.3f}" if pc is not None else f"{'—':>10}"
        print(line)
    print(f"{'n(probe)':<9}"+"".join(f"{len(per[p][target]):>9}" for p in sorted(per)))
    print()
