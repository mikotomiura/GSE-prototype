"""D6 のうち、複製の行（jsonl・repo に入らない）が要る量を、機械ごとに出す（報告の組だけ）。

使い方:
  python3 -I d6_local.py <out_dir> --null <1|2> [--peer <他機の d6_local_null*.json>]
読む: <out_dir>/report/null<n>_*.jsonl
出力: <out_dir>/report/d6_local_null<n>.json

- quant: 差なしの群（段 0）× セルの G_v の 95% 点（パネルの全書き手 × 全複製・numpy の既定の線形補間・判断 42）。
- desc: 群 × セル × 案の記述の量（rank-1・EER 2 つ・AUC_v の平均・T の分布）と G_v の平均。
- --peer を渡すと、自機と他機の quant から閾値 c（セルごとに、D6 の差なしの筋の 95% 点の最大）を決め、
  書き手の水準の規則の率（群 × セル）を出す。c に要る群が欠けていれば止める。
両機で同じ c になることは d6_report.py が確かめる。
"""
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import run_eye as RE  # noqa: E402

# D6 の書き手の水準の規則に入れる差なしの筋（CoAuthor 7・CS1 5）
NULL_GROUPS = {
    "coauthor": ["null1_dose_coauthor_0.0", "null2_dose_coauthor_0.0", "null1_struct_coauthor_0.0",
                 "null1_wobble_coauthor_0.0", "null1_volume_coauthor_0.0", "null1_drift_coauthor_0.0",
                 "null1_stack_coauthor_0.0"],
    "cs1": ["null1_dose_cs1_0.0", "null1_wobble_cs1_0.0", "null1_volume_cs1_0.0", "null1_drift_cs1_0.0",
            "null1_stack_cs1_0.0"],
}
Q = 0.95


def shape_of(g):
    return g.split("_")[2]


def is_null(g):
    return g.split("_")[3] == "0.0"


def load_groups(out, null, ch):
    G = {}
    for p in sorted(glob.glob(os.path.join(out, "report", "null%d_*.jsonl" % null))):
        name = os.path.basename(p)[:-6]
        rows = [json.loads(x) for x in open(p)]
        if {r["code_hash"] for r in rows} != {ch}:
            sys.exit("%s にコードのハッシュが違う行がある" % p)
        if {r["row"]["null"] for r in rows} != {null}:
            sys.exit("%s に帰無の番号が違う行がある" % p)
        G[name] = sorted(rows, key=lambda r: r["seed"])
    if not G:
        sys.exit("報告の組の jsonl が無い: %s" % os.path.join(out, "report"))
    return G


def mean_se(x):
    x = np.asarray(x, float)
    n = len(x)
    return dict(mean=float(x.mean()), se=float(x.std(ddof=1) / math.sqrt(n)) if n > 1 else None, n=n)


def auc_two(pos, neg):
    """pos を neg から分ける AUC（同点は 0.5）。"""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    d = pos[:, None] - neg[None, :]
    return float(((d > 0) + 0.5 * (d == 0)).mean())


def describe(rows, cell):
    P = len(rows[0]["cells"][cell]["G"])
    out = dict(G=mean_se([np.mean(r["cells"][cell]["G"]) for r in rows]))
    for e in EY.EYES:
        T = np.array([EY.t_of_w(r["cells"][cell][e]["W"], P) for r in rows])
        out[e] = dict(
            rank1=mean_se([r["cells"][cell][e]["rank1"] for r in rows]),
            eer_glob=mean_se([r["cells"][cell][e]["eer_glob"] for r in rows]),
            eer_each=mean_se([r["cells"][cell][e]["eer_each"] for r in rows]),
            auc_v=mean_se([np.mean(r["cells"][cell][e]["auc"]) for r in rows]),
            T=dict(mean=float(T.mean()), q05=float(np.quantile(T, 0.05)), q50=float(np.quantile(T, 0.5)),
                   q95=float(np.quantile(T, 0.95))),
        )
    return out


def writer_rates(rows, cell, c):
    """G_v > c の割合（複製ごとの割合の平均と、複製を単位にした MC SE）。分布の筋は植えた・植えていないに分ける。"""
    over = [np.asarray(r["cells"][cell]["G"]) > c for r in rows]
    out = dict(all=mean_se([o.mean() for o in over]))
    if "planted" in rows[0]:
        pl = [np.asarray(r["planted"], bool) for r in rows]
        out["planted"] = mean_se([o[m].mean() for o, m in zip(over, pl)])
        out["unplanted"] = mean_se([o[~m].mean() for o, m in zip(over, pl)])
        out["auc_G"] = mean_se([auc_two(np.asarray(r["cells"][cell]["G"])[m], np.asarray(r["cells"][cell]["G"])[~m])
                                for r, m in zip(rows, pl)])
        for e in EY.EYES:
            out["auc_aucv_" + e] = mean_se([auc_two(np.asarray(r["cells"][cell][e]["auc"])[m],
                                                    np.asarray(r["cells"][cell][e]["auc"])[~m])
                                            for r, m in zip(rows, pl)])
    return out


def main():
    argv = sys.argv[1:]
    opt = {}
    for key in ("--null", "--peer"):
        if key in argv:
            i = argv.index(key)
            opt[key] = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
    out = argv[0]
    null = int(opt["--null"])
    ch = RE.code_hash()
    G = load_groups(out, null, ch)
    R = dict(code_hash=ch, null=null, quantile=Q, quant={}, desc={}, groups={g: len(r) for g, r in G.items()})
    for g, rows in G.items():
        R["desc"][g] = {cell: describe(rows, cell) for cell in rows[0]["cells"]}
        if is_null(g):
            R["quant"][g] = {cell: float(np.quantile(np.concatenate([r["cells"][cell]["G"] for r in rows]), Q))
                             for cell in rows[0]["cells"]}
    if "--peer" in opt:
        peer = json.load(open(opt["--peer"]))
        if peer["code_hash"] != ch or peer["null"] == null:
            sys.exit("--peer のコードのハッシュが違うか、同じ帰無の集計を渡している")
        allq = dict(peer["quant"])
        allq.update(R["quant"])
        c = {}
        for shape, need in NULL_GROUPS.items():
            miss = [g for g in need if g not in allq]
            if miss:
                sys.exit("c に要る差なしの群が無い: %r" % miss)
            cells = allq[need[0]].keys()
            for cell in cells:
                c["%s/%s" % (shape, cell)] = max(allq[g][cell] for g in need)
        R["c"] = c
        R["rates"] = {g: {cell: writer_rates(rows, cell, c["%s/%s" % (shape_of(g), cell)]) for cell in rows[0]["cells"]}
                      for g, rows in G.items()}
    path = os.path.join(out, "report", "d6_local_null%d.json" % null)
    json.dump(R, open(path, "w"), indent=1)
    print("書いた: %s（%d 群%s）" % (path, len(G), "・c と率あり" if "c" in R else "・95% 点だけ"))


if __name__ == "__main__":
    main()
