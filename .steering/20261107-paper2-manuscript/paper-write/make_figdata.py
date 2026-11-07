#!/usr/bin/env python3
"""論文 2 の原稿の図と補足の表を、results/ の集計値（定義ごとの値）から作る。

書き手ごとの値・時刻・ID は results/ に無く、ここでも出さない。出力は papers/stall-shape-multiverse/manuscript/ の
figdata/（pgfplots が読む CSV）と appendix/tab_*.tex（補足の全表）。最後に本文で使う数を数え直して表示する
（外枠 v8 の値との照合用）。

  python3 make_figdata.py <repo-root>
"""
import json
import math
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
res = root / "experiments/20261107-stall-shape-multiverse/results"
out = root / "papers/stall-shape-multiverse/manuscript"
(out / "figdata").mkdir(parents=True, exist_ok=True)
(out / "appendix").mkdir(parents=True, exist_ok=True)

c3 = json.load(open(res / "c3_multiverse.json"))
r1 = json.load(open(res / "round1_extra.json"))
r3 = json.load(open(res / "round3_speed.json"))
r4 = json.load(open(res / "round4_speedvar.json"))
l90 = json.load(open(res / "c1_lengths90.json"))
r8 = json.load(open(res / "round8_causal.json"))       # 因果の二段の区間（追加の条件 8）: 読み方で一段を主に戻した
ln5 = json.load(open(res / "round5_length.json"))       # 作文と観測の長さを固定した偏相関（追加の条件 6 (c)）
pz5 = json.load(open(res / "round5_pause.json"))        # 休止の系統（追加の条件 6 (a)）
# 区間は一段（書き手の再標本だけ）を主にする。追加の条件 8 の読み方: φ で点が二段の区間の外に出た通りが 5% を超えた。
B0 = "W30_q0.99_net_replay"
DS = ["CS1 2019", "CS1 2021", "CoAuthor", "KLiCKe"]


def parse(k):
    w, th, rule, seg = k.split("_")
    W = int(w[1:])
    if th.startswith("q"):
        fam, thv = "q", th[1:]
    else:
        fam, thv = "fix", th[3:] if th.startswith("fix") else th
    return W, fam, th, rule, seg


keys = list(c3.keys())
assert len(keys) == 90 and B0 in keys
alt = [k for k in keys if k != B0]
th_labels = sorted({parse(k)[2] for k in keys})


def thlabel(th):
    if th.startswith("q"):
        return "q" + th[1:]
    return th


def seglabel(s):
    return {"replay": "obs", "g5": "gap 5 min", "g30": "gap 30 min"}[s]


def rulelabel(r):
    return {"net": "net", "ins": "char"}[r]


def thtex(th):
    if th.startswith("q"):
        return th[1:]
    # fixed seconds, e.g. 'fix10' or 's10'
    digits = "".join(ch for ch in th if ch.isdigit())
    return digits + "\\,s"


# ---------- Figure 2: score association ----------
rows = []
for k in keys:
    W, fam, th, rule, seg = parse(k)
    sc = r1["by_cfg"][k]["score"] if k != B0 else r1["summary"]["B"]["b0"]
    adj = r3["by_cfg"][k] if k != B0 else None
    if k == B0:
        a, alo, ahi = r3["summary"]["b0"]["S2"], *r3["summary"]["b0"]["S2_ci"]
    else:
        a, (alo, ahi) = adj["S2"], adj["S2_ci"]
    L = ln5["by_cfg"][k]
    rows.append(dict(k=k, W=W, fam=fam, th=th, rule=rule, seg=seg, rho=sc["rho"], lo=sc["ci"][0], hi=sc["ci"][1],
                     adj=a, alo=alo, ahi=ahi, b0=int(k == B0), ln=L["p_both"], llo=L["p_both_ci"][0],
                     lhi=L["p_both_ci"][1]))
rows.sort(key=lambda r: r["rho"])
with open(out / "figdata/score.csv", "w") as f:
    f.write("i rho lo hi adj alo ahi ln llo lhi fam b0 W15\n")
    for i, r in enumerate(rows, 1):
        f.write(f"{i} {r['rho']:.4f} {r['lo']:.4f} {r['hi']:.4f} {r['adj']:.4f} {r['alo']:.4f} {r['ahi']:.4f} "
                f"{r['ln']:.4f} {r['llo']:.4f} {r['lhi']:.4f} "
                f"{1 if r['fam']=='q' else 0} {r['b0']} {1 if r['W']==15 else 0}\n")

# ---------- Figure 3: ratios ----------
def ratio(k, pair):
    if k == B0:
        a = r1["summary"]["A1"][pair]
        return a["b0_point"], a["b0_ci"]
    x = r1["by_cfg"][k]["ratio"][pair]
    return x["point"], x["ci"]


for tag, pair in [("cs19_kl", "CS1 2019 / KLiCKe"), ("cs19_cs21", "CS1 2019 / CS1 2021")]:
    rr = []
    for k in keys:
        p, ci = ratio(k, pair)
        rr.append((math.log(p), math.log(ci[0]), math.log(ci[1]), parse(k)[1] == "q", k == B0))
    rr.sort(key=lambda x: x[0])
    with open(out / f"figdata/ratio_{tag}.csv", "w") as f:
        f.write("i lr lo hi fam b0\n")
        for i, (p, lo, hi, q, b) in enumerate(rr, 1):
            f.write(f"{i} {p:.4f} {lo:.4f} {hi:.4f} {int(q)} {int(b)}\n")

# ---------- Figure 4: phi ----------
CELLS = ["CS1 2019 block", "CS1 2019 task", "CS1 2021 block", "CS1 2021 task", "CoAuthor session"]


def phi(k, cell):
    if k == B0:
        x = r1["summary"]["phi_range"][cell]
        return x["b0"], x["b0_ci"]
    x = r1["by_cfg"][k]["phi_b"][cell]
    return x["phi"], x["ci"]


with open(out / "figdata/phi.csv", "w") as f:
    f.write("cell i phi lo hi b0\n")
    for ci_, cell in enumerate(CELLS, 1):
        vals = sorted([(phi(k, cell), k == B0) for k in keys], key=lambda x: x[0][0])
        for i, ((p, ci), b) in enumerate(vals, 1):
            f.write(f"{ci_} {i} {p:.4f} {ci[0]:.4f} {ci[1]:.4f} {int(b)}\n")

# ---------- Figure 5: length shares ----------
with open(out / "figdata/lengths.csv", "w") as f:
    f.write("ds i stall writer\n")
    for di, ds in enumerate(["CS1 2019", "CS1 2021", "CoAuthor"], 1):
        vals = sorted([(l90["by_cfg"][k][ds]["shares"]["stall"], l90["by_cfg"][k][ds]["shares"]["writer"])
                       for k in keys])
        for i, (s, w) in enumerate(vals, 1):
            f.write(f"{di} {i} {s:.4f} {w:.4f}\n")

# ---------- Supplement tables S3 (rates, ratios, score) and S4 (phi) ----------
def fmt(x, d=2):
    return f"{x:.{d}f}".replace("-", "$-$")


SEGO = {"replay": 0, "g5": 1, "g30": 2}
order = sorted(keys, key=lambda k: (parse(k)[1] != "q", parse(k)[2], parse(k)[0], parse(k)[3] != "net",
                                    SEGO[parse(k)[4]]))
s3, s4 = [], []
for k in order:
    W, fam, th, rule, seg = parse(k)
    head = [f"{thtex(th)}" + ("$^\\ast$" if k == B0 else ""), str(W), rulelabel(rule),
            {"replay": "def.", "g5": "5", "g30": "30"}[seg]]
    rates = [c3[k][d]["rate_pooled"] for d in DS]
    rk = "".join({"CS1 2019": "a", "CS1 2021": "b", "CoAuthor": "c", "KLiCKe": "k"}[d] for d in c3[k]["rank"])
    sc = r1["by_cfg"][k]["score"] if k != B0 else r1["summary"]["B"]["b0"]
    a = r3["summary"]["b0"]["S2"] if k == B0 else r3["by_cfg"][k]["S2"]
    zero = c3[k]["KLiCKe"]["writers_zero_share"] * 100
    p1, c1 = ratio(k, "CS1 2019 / KLiCKe")
    p2, c2 = ratio(k, "CS1 2019 / CS1 2021")
    s3.append(" & ".join(head + [f"{x:.1f}" for x in rates] + [rk, f"{p1:.2f} [{c1[0]:.2f}, {c1[1]:.2f}]",
              f"{p2:.2f} [{c2[0]:.2f}, {c2[1]:.2f}]", f"{fmt(sc['rho'], 3)} [{fmt(sc['ci'][0], 2)}, {fmt(sc['ci'][1], 2)}]",
              fmt(a, 3), fmt(ln5["by_cfg"][k]["p_both"], 3), f"{zero:.1f}"]) + " \\\\")
    s4.append(" & ".join(head + [f"{phi(k, c)[0]:.2f}" for c in CELLS]) + " \\\\")
# ---------- pause family table ----------
sp = []
pb = pz5["by_cfg"]
def pkey(k):
    _, kind, th, seg = k.split("_")
    return (kind != "all", not th.startswith("fix"), float(th[3:-1]) if th.startswith("fix") else float(th[1:]), SEGO[seg])
for k in sorted(pb, key=pkey):
    _, kind, th, seg = k.split("_")
    v = pb[k]
    rk = "".join({"CS1 2019": "a", "CS1 2021": "b", "CoAuthor": "c", "KLiCKe": "k"}[d] for d in v["rank"])
    thl = (th[3:-1] + "\\,s") if th.startswith("fix") else th[1:]
    sc_ = v["score"]
    sp.append(" & ".join([{"all": "any", "char": "char"}[kind], thl, {"replay": "def.", "g5": "5", "g30": "30"}[seg]]
              + [f"{v['rate'][d]:.1f}" for d in DS] + [rk,
              f"{fmt(sc_['rho'], 3)} [{fmt(sc_['ci'][0], 2)}, {fmt(sc_['ci'][1], 2)}]", fmt(sc_["partial_speed"], 3),
              fmt(ln5["by_cfg"][k]["p_both"], 3)]) + " \\\\")
for name, rows_ in [("tab_s3.tex", s3), ("tab_s4.tex", s4), ("tab_pause.tex", sp)]:
    with open(out / "appendix" / name, "w") as f:
        f.write("% Generated from the aggregate result files by the authors' script; do not edit by hand.\n")
        f.write("\n".join(rows_) + "\n")

# ---------- recount the numbers used in the text ----------
def cnt(cond):
    return sum(1 for k in alt if cond(k))


print("rank differs from B0:", cnt(lambda k: c3[k]["rank"] != c3[B0]["rank"]),
      "| q family:", sum(1 for k in alt if parse(k)[1] == "q" and c3[k]["rank"] != c3[B0]["rank"]),
      "/", sum(1 for k in alt if parse(k)[1] == "q"))
rs = [r1["by_cfg"][k]["score"] for k in alt]
print("rho min/median/max:", min(x["rho"] for x in rs), sorted(x["rho"] for x in rs)[44], max(x["rho"] for x in rs))
pos = [k for k in alt if r1["by_cfg"][k]["score"]["ci"][0] > 0]
neg = [k for k in alt if r1["by_cfg"][k]["score"]["ci"][1] < 0]
print("CI pos/neg/incl0:", len(pos), len(neg), 89 - len(pos) - len(neg))
print("|rho|>=0.1 neg/pos:", cnt(lambda k: r1["by_cfg"][k]["score"]["rho"] <= -0.1),
      cnt(lambda k: r1["by_cfg"][k]["score"]["rho"] >= 0.1))
print("pos all W15:", all(parse(k)[0] == 15 for k in pos), "| q in pos:", all(parse(k)[1] == "q" for k in pos))
print("pos theta:", sorted(parse(k)[2] for k in pos))
for fam in ["q", "fix"]:
    ks = [k for k in alt if parse(k)[1] == fam]
    print(fam, len(ks), "pos", sum(k in pos for k in ks), "neg", sum(k in neg for k in ks))
noW15 = [k for k in alt if parse(k)[0] != 15]
print("non-W15:", len(noW15), "pos", sum(k in pos for k in noW15))
z = [c3[k]["KLiCKe"]["writers_zero_share"] for k in alt]
zp = [c3[k]["KLiCKe"]["writers_zero_share"] for k in pos]
print("zero share all", min(z), max(z), "| pos", min(zp), max(zp))
pm = [r1["by_cfg"][k]["score"]["rho_prompt_median"] for k in alt]
print("prompt median neg/pos:", sum(x < 0 for x in pm), sum(x > 0 for x in pm))
print("S1 median q/fix:", r3["summary"]["groups"]["q"]["S1_median"], r3["summary"]["groups"]["fix"]["S1_median"])
print("A1 (one-stage):", r8["summary"]["recount_onestage"]["A1"])
print("A1 (causal two-stage):", r8["summary"]["recount_causal"]["A1"])
print("score (one-stage / causal):", {k: r8["summary"]["recount_onestage"]["score"][k] for k in ("neg","pos","other","b0_ci")}, {k: r8["summary"]["recount_causal"]["score"][k] for k in ("neg","pos","other","b0_ci")})
print("outside causal:", r8["summary"]["outside"])
lr = [math.log(r1["by_cfg"][k]["ratio"]["CS1 2019 / KLiCKe"]["point"]) for k in alt]
print("log ratio cs19/kl range:", min(lr), max(lr))
A2 = {c: sum(r1["by_cfg"][k]["phi_b"][c]["ci"] is not None and r1["by_cfg"][k]["phi_b"][c]["ci"][0] > 1 for k in alt)
      for c in CELLS}
print("A2 (one-stage):", A2, "| A3 one-stage:", r8["summary"]["recount_onestage"]["A3"], "| causal:", r8["summary"]["recount_causal"]["A3"])
print("phi range:", {c: (round(v["b0"], 2), round(v["median"], 2)) for c, v in r1["summary"]["phi_range"].items()})
cs = {ds: (min(l90["by_cfg"][k][ds]["shares"]["stall"] for k in keys),
           max(l90["by_cfg"][k][ds]["shares"]["writer"] for k in keys)) for ds in ["CS1 2019", "CS1 2021", "CoAuthor"]}
print("length stall-share min / writer-share max:", cs)
