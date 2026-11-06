"""summary.json から読みの材料の表（tables.md）を作る。値の計算はしない（中央値を並べ、forms.py の判定を当てるだけ）。

使い方: python3 -I report.py <summary.json> <tables.md>
表 1: 主のセル × 構造 × 列の G（τ 他人）・G0・D・S0（そのまま o）と G・D（並べ替え p）、部分 1・2 の列ごとの判定。
表 2: 主のセルの部分 1・2（hmm3 の 3 列）と形（conditions D5）。
表 3: 記述（判定に使わない）: 各セル・各組の 6 構造の D と G・G0 の Kendall の τ_b。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forms  # noqa: E402

QS = (3, 5, 7)
STRUCTS = ["hmm3", "hmm6", "hmm10", "ar1", "ar2", "ar3"]
MAIN = {"coauthor": [("P15", "5"), ("P15", "15"), ("P30", "30")], "cs1": [("C5", "5")]}
ALL = {"coauthor": [("P15", "1"), ("P15", "5"), ("P15", "15"), ("P30", "30")], "cs1": [("C5", "1"), ("C5", "5")]}


def med(st):
    return None if st is None or st.get("suppressed") else st["median"]


def f(x, d=3):
    return "—" if x is None else ("%+.*f" % (d, x)).replace("-", "−")


def cell_of(S, q_, order, ds, pn, k):
    try:
        return S["groups"]["q%d_%s" % (q_, order)]["datasets"][ds]["em"][pn][k]
    except KeyError:
        return None


def vals(S, ds, pn, k, q_, name):
    o, p = cell_of(S, q_, "o", ds, pn, k), cell_of(S, q_, "p", ds, pn, k)
    if o is None or p is None:
        return None
    so, sp = o["structs"][name], p["structs"][name]
    return dict(G_o=med(so["tau_other"]["all/self_minus_pool_same"]), G_p=med(sp["tau_other"]["all/self_minus_pool_same"]),
                G0_o=med(so["tau_0"]["all/self_minus_pool_same"]), G0_p=med(sp["tau_0"]["all/self_minus_pool_same"]),
                D_o=med(so["deficit"]["all"]), D_p=med(sp["deficit"]["all"]), S0_o=med(so["S0"]["all"]),
                S0_p=med(sp["S0"]["all"]))


def main(path, out):
    S = json.load(open(path, encoding="utf-8"))
    L = ["# 表（report.py が summary.json から作る・手で書き換えない）", "",
         "run_id: `%s`。値は書き手ごとの差の中央値（全記号・nats/記号）。G = 本人（τ 他人）− 同じ構造の共通、"
         "G0 = 本人（τ = 0）− 共通、D = r1 − 共通（足りなさ）、S0 = 他の人の τ = 0 の当てはめ − 共通（v の中央値の、w の中央値）。"
         "o = そのまま、p = 並べ替え。部分 1・2 の判定は forms.py（conditions D5）。" % S.get("run_id"), ""]
    L += ["## 表 1 —— 構造 × 列（主のセルと k = 1）", ""]
    for ds, cells in ALL.items():
        for pn, k in cells:
            L += ["### %s %s k = %s" % (ds, pn, k), "",
                  "| 構造 | 列 | G_o | G_p | G0_o | D_o | D_p | S0_o | 部分 1 | 部分 2 |", "|---|---|---|---|---|---|---|---|---|---|"]
            for name in STRUCTS:
                for q_ in QS:
                    v = vals(S, ds, pn, k, q_, name)
                    if v is None:
                        L.append("| %s | %d | 未 | | | | | | | |" % (name, q_ * q_ + 1))
                        continue
                    L.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                        name, q_ * q_ + 1, f(v["G_o"]), f(v["G_p"]), f(v["G0_o"]), f(v["D_o"]), f(v["D_p"]), f(v["S0_o"]),
                        forms.part1(v) or "—", forms.part2(v) or "—"))
            L.append("")
    L += ["## 表 2 —— 読みの形（hmm3・主のセル）", "", "| データ | セル | 部分 1（3 列） | 部分 2（3 列） | 形 |", "|---|---|---|---|---|"]
    for ds, cells in MAIN.items():
        fs = []
        for pn, k in cells:
            vs = [vals(S, ds, pn, k, q_, "hmm3") for q_ in QS]
            if None in vs:
                L.append("| %s | %s k = %s | 未 | 未 | 未 |" % (ds, pn, k))
                fs.append(None)
                continue
            p1 = forms.cell_part1([forms.part1(v) for v in vs])
            p2 = forms.cell_part2([forms.part2(v) for v in vs])
            fm = forms.form(p1, p2)
            fs.append(fm)
            L.append("| %s | %s k = %s | %s | %s | %s |" % (ds, pn, k, p1, p2, fm))
        ov = forms.overall(fs) if None not in fs else "未"
        L.append("| %s | 全体 | | | %s |" % (ds, ov))
    L += ["", "CS1 は前の試験で hmm3 の G がもともと小さく、力が弱い（conditions D5）。", ""]
    L += ["## 表 3 —— 記述: 6 構造の D と G・G0 の Kendall の τ_b（判定に使わない）", "",
          "| データ | セル | 列 | 順 | τ_b(D, G) | τ_b(D, G0) |", "|---|---|---|---|---|---|"]
    for ds, cells in ALL.items():
        for pn, k in cells:
            for q_ in QS:
                for order in ("o", "p"):
                    c = cell_of(S, q_, order, ds, pn, k)
                    if c is None:
                        continue
                    kd = c.get("kendall", {})
                    L.append("| %s | %s k = %s | %d | %s | %s | %s |" % (ds, pn, k, q_ * q_ + 1, order, f(kd.get("G"), 2),
                                                                      f(kd.get("G0"), 2)))
    L.append("")
    open(out, "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
