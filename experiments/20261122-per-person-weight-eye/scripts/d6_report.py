"""D6 の報告（報告の組の集計から機械的に）と、追記 3 の論文 3 への統合の判定。

使い方: python3 -I d6_report.py <out_dir>
読む: <out_dir>/select/d5.json・<out_dir>/report/summary_null1.json・<out_dir>/hpz2/report/summary_null2.json・
      <out_dir>/report/d6_local_null1.json・<out_dir>/hpz2/report/d6_local_null2.json（どちらも c と率ありの版）
出力: <out_dir>/report/d6.json
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import run_eye as RE  # noqa: E402
from d6_local import NULL_GROUPS  # noqa: E402

GATE_MAX = 73          # D6 のセルの門（1,000 複製で 73 以下）
GAP_MIN = 35           # 間を空けたセルの基準（500 複製で 35 以上なら超えた）
WOBBLE_MARGIN = 0.03   # 揺れの筋の案どうしの比べ
CELLS = dict(coauthor=["k1_g0", "k5_g0", "k15_g0", "k5_g5", "k5_g10"], cs1=["k1_g0", "k5_g0", "k1_g1", "k1_g4"])
GAP = dict(coauthor=["k5_g5", "k5_g10"], cs1=["k1_g1", "k1_g4"])
ADJ = dict(coauthor="k5_g0", cs1="k1_g0")
DOSE = ["0.001", "0.003", "0.01", "0.03"]
# 論文 3 の数（D6「論文 3 との並べ」・10 種）
PAPER3 = {1: {"k5_g0": [0.0, 0.2, 0.9, 1.0], "k15_g0": [0.1, 0.6, 0.9, 1.0]},
          2: {"k5_g0": [0.0, 0.0, 0.0, 0.2], "k15_g0": [0.0, 0.0, 0.2, 0.3]}}
PAPER3_N = 10


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k, n, a=0.05):
    """正確な 95% 区間（二分法）。下限: P(X >= k | p) = a/2（p に増加）、上限: P(X <= k | p) = a/2（p に減少）。"""
    def root(f, target, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if (f(mid) < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else root(lambda p: 1 - binom_cdf(k - 1, n, p), a / 2, True)
    upper = 1.0 if k == n else root(lambda p: binom_cdf(k, n, p), a / 2, False)
    return [lower, upper]


def load(p):
    if not os.path.exists(p):
        sys.exit("無い: %s" % p)
    return json.load(open(p))


def main():
    out = sys.argv[1]
    ch = RE.code_hash()
    d5 = load(os.path.join(out, "select", "d5.json"))
    S = {1: load(os.path.join(out, "report", "summary_null1.json")),
         2: load(os.path.join(out, "hpz2", "report", "summary_null2.json"))}
    L = {1: load(os.path.join(out, "report", "d6_local_null1.json")),
         2: load(os.path.join(out, "hpz2", "report", "d6_local_null2.json"))}
    for n in (1, 2):
        if S[n]["code_hash"] != ch or S[n]["which"] != "report" or L[n]["code_hash"] != ch:
            sys.exit("null%d の集計のコードのハッシュか組が違う" % n)
        if "c" not in L[n]:
            sys.exit("null%d の d6_local に c が無い（--peer を渡して回し直す）" % n)
    if d5["code_hash"] != ch:
        sys.exit("d5.json のコードのハッシュが違う")
    if L[1]["c"] != L[2]["c"]:
        sys.exit("両機の c が一致しない")
    chosen = d5["chosen"]
    eyes = [chosen] + ([] if chosen == "E1" else ["E1"])

    def cell_of(g, cell):
        n = int(g[4])
        return S[n]["groups"][g][cell]

    def rate(g, cell, e, a="0.05"):
        return cell_of(g, cell)[e][a]

    R = dict(code_hash=ch, chosen=chosen, c=L[1]["c"], gates={}, gap={}, adjacent_drift={}, wobble={},
             secondary={}, paper3=[], judgments=[], writer_level={}, desc={1: L[1]["desc"], 2: L[2]["desc"]})

    # セルの門（55）
    for e in eyes:
        G = []
        for shape, cells in CELLS.items():
            for cell in cells:
                for g in NULL_GROUPS[shape]:
                    k = rate(g, cell, e)["n_rej"]
                    G.append(dict(shape=shape, cell=cell, group=g, n_rej=k, ok=k <= GATE_MAX))
        if len(G) != 55:
            sys.exit("門の数が 55 でない: %d" % len(G))
        R["gates"][e] = dict(all_ok=all(x["ok"] for x in G), n_red=sum(not x["ok"] for x in G), gates=G)

    # 間を空けたセルの基準（漂い ρ = 0.5・0.9）と、隣り合うセルの記述
    for e in eyes:
        R["gap"][e], R["adjacent_drift"][e] = [], []
        for shape in CELLS:
            for rho in ("0.5", "0.9"):
                g = "null1_drift_%s_%s" % (shape, rho)
                for cell in GAP[shape]:
                    r = rate(g, cell, e)
                    R["gap"][e].append(dict(group=g, cell=cell, n_rej=r["n_rej"], rate=r["rate"], se=r["se"],
                                            exceeded=r["n_rej"] >= GAP_MIN))
                r = rate(g, ADJ[shape], e)
                R["adjacent_drift"][e].append(dict(group=g, cell=ADJ[shape], rate=r["rate"], se=r["se"]))

    # 揺れの筋の案どうしの比べ（CoAuthor k = 5）
    for step in ("0.01", "0.03"):
        g = "null1_wobble_coauthor_%s" % step
        v = {e: rate(g, "k5_g0", e)["rate"] for e in EY.EYES}
        others = [e for e in EY.EYES if e != chosen and v[chosen] <= v[e] - WOBBLE_MARGIN]
        R["wobble"][step] = dict(rates=v, others_higher_by_margin=others)

    # 副次の水準（選んだ案・p ≤ 0.01・0.001）: 用量の検出力と差なしの拒否率
    for a in ("0.01", "0.001"):
        rows = {}
        for n, shapes in ((1, ("coauthor", "cs1")), (2, ("coauthor",))):
            for shape in shapes:
                for st in ["0.0"] + DOSE:
                    g = "null%d_dose_%s_%s" % (n, shape, st)
                    rows[g] = {cell: rate(g, cell, chosen, a) for cell in CELLS[shape]}
        for shape in CELLS:
            for g in NULL_GROUPS[shape]:
                rows.setdefault(g, {cell: rate(g, cell, chosen, a) for cell in CELLS[shape]})
        R["secondary"][a] = rows

    # 論文 3 との並べ（記述）と合成の段の読み（12 の判定）
    for n in (1, 2):
        for cell, p3 in PAPER3[n].items():
            for st, v3 in zip(DOSE, p3):
                g = "null%d_dose_coauthor_%s" % (n, st)
                r = rate(g, cell, chosen)
                k3 = round(v3 * PAPER3_N)
                row = dict(null=n, cell=cell, step=st, eye=r["rate"], se=r["se"], n=cell_of(g, cell)["n"],
                           paper3=v3, paper3_ci=clopper_pearson(k3, PAPER3_N))
                if r["rate"] in (0.0, 1.0):
                    row["eye_ci"] = clopper_pearson(r["n_rej"], cell_of(g, cell)["n"])
                R["paper3"].append(row)
                if v3 < 0.8:
                    hi, lo = 0.8 + 2 * r["se"], 0.8 - 2 * r["se"]
                    word = "拾った" if r["rate"] >= hi else ("拾わなかった" if r["rate"] < lo else "境目")
                    R["judgments"].append(dict(row, reading=word))
    if len(R["judgments"]) != 12:
        sys.exit("判定の数が 12 でない: %d" % len(R["judgments"]))

    # 書き手の水準の規則（両機の率）
    for n in (1, 2):
        R["writer_level"][n] = L[n]["rates"]

    # 追記 3: 論文 3 への統合
    a_ok = R["gates"][chosen]["all_ok"]
    b_ok = any(j["reading"] == "拾った" for j in R["judgments"])
    R["addendum3"] = dict(a_gates_all_pass=a_ok, b_any_picked=b_ok, integrate=a_ok and b_ok)

    path = os.path.join(out, "report", "d6.json")
    json.dump(R, open(path, "w"), indent=1, ensure_ascii=False)
    print("書いた: %s" % path)
    print("選んだ案 %s の門: %s（赤 %d）" % (chosen, "すべて通った" if a_ok else "赤あり", R["gates"][chosen]["n_red"]))
    if chosen != "E1":
        print("E1 の門: 赤 %d" % R["gates"]["E1"]["n_red"])
    print("12 の判定: 拾った %d・境目 %d・拾わなかった %d" % tuple(
        sum(j["reading"] == w for j in R["judgments"]) for w in ("拾った", "境目", "拾わなかった")))
    print("追記 3: (a) %s・(b) %s → %s" % (a_ok, b_ok, "論文 3 に統合する" if a_ok and b_ok else "統合しない"))


if __name__ == "__main__":
    main()
