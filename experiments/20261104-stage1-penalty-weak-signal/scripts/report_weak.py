"""集計・読みの規則（conditions.md W2）・再現の門 W4。

使い方: python3 -I -X utf8 report_weak.py RESULTS_DIR [--run-id ID]
RESULTS_DIR/raw/ を読み、summary.json・tables.md を書く。W4 が落ちたら終了コード 3。
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weak  # noqa: E402

sim = weak.sim
sys.path.insert(0, weak.SIM_DIR)
import report  # noqa: E402  前の実験の集計の関数（per_choice・combo_choice）を使う

PREV_SUMMARY = os.path.normpath(os.path.join(weak.SIM_DIR, "..", "results", "summary.json"))
T_A = sim.TAUS.index(0.25)
T_B = sim.TAUS.index(0.5)
RULE_N = 50
RULE_LO, RULE_HI = 0.8, 1.25
W4_TOL = 1e-12


def load(res_dir, run_id=None):
    raw = os.path.join(res_dir, "raw")
    meta = json.load(open(os.path.join(raw, "cells.json")))
    if run_id is not None and meta.get("run_id") != run_id:
        raise ValueError(f"raw の run_id {meta.get('run_id')} が指定 {run_id} と違う")
    if meta.get("mutate"):
        raise ValueError(f"raw が変異つきの計算 {meta['mutate']}")
    expect = {c["id"]: c for c in weak.cells(meta["seed"])}
    got = {c["id"]: c for c in meta["cells"]}
    if len(got) != len(meta["cells"]) or set(got) != set(expect):
        raise ValueError("セルの id が期待の集合と違う")
    out = []
    for i, c in got.items():
        e = expect[i]
        if any(c[k] != e[k] for k in ("main_id", "scale", "n", "rate", "sd", "signal", "kind")) or abs(c["a"] - e["a"]) > 1e-12:
            raise ValueError(f"セル {i} の条件が期待と違う")
        fn = os.path.join(raw, f"cell{i:03d}.npz")
        if hashlib.sha256(open(fn, "rb").read()).hexdigest() != meta["sha256"][os.path.basename(fn)]:
            raise ValueError(f"{fn} の SHA-256 が cells.json と違う")
        arr = dict(np.load(fn))
        if len(arr["D"]) != meta["reps"]:
            raise ValueError(f"セル {i} の反復の数が違う")
        out.append((c, arr))
    out.sort(key=lambda x: (-x[0]["scale"], x[0]["main_id"]))
    return meta, out


def plans(arr):
    n = len(arr["D"])
    return {"A": np.full(n, T_A), "B": np.full(n, T_B),
            "Cp": report.combo_choice(arr, "min_class", 30, T_A, "c_fwd"), "fwd": arr["c_fwd"], "1se": arr["c_1se"]}


def cell_rows(cl):
    rows = []
    for c, a in cl:
        r = dict(cell={k: c[k] for k in ("id", "main_id", "scale", "n", "rate", "sd")}, reps=int(len(a["D"])))
        r["fixed"] = {report.tau_s(t): report.per_choice(a, np.full(len(a["D"]), t)) for t in range(sim.NT)}
        r["plans"] = {k: report.per_choice(a, ch) for k, ch in plans(a).items()}
        r["best_dist"] = report.dist(a["met"][:, :, 0].argmin(1))
        r["nonconv_slope"] = {report.tau_s(t): int(np.nansum(a["met"][:, t, 5])) for t in range(sim.NT)}
        r["one_class"] = int(np.sum((a["npos"] == 0) | (a["nneg"] == 0)))
        rows.append(r)
    return rows


def g_w4(rows):
    """係数 1 倍の固定の τ の傾きの四分位と後悔の平均が、前の実験の summary.json と一致する。"""
    prev = {r["cell"]["id"]: r for r in json.load(open(PREV_SUMMARY))["cells"] if r["cell"]["set"] == "main"}
    bad, n = [], 0
    for r in rows:
        if r["cell"]["scale"] != 1.0:
            continue
        p = prev[r["cell"]["main_id"]]
        for t, v in r["fixed"].items():
            for path in (("slope", "med"), ("slope", "q1"), ("slope", "q3"), ("regret", "mean"), ("ll", "mean")):
                a, b = v[path[0]][path[1]], p["fixed"][t][path[0]][path[1]]
                n += 1
                if (a is None) != (b is None) or (a is not None and abs(a - b) > W4_TOL):
                    bad.append(f"セル {r['cell']['main_id']} τ {t} {'.'.join(path)}: {a} 対 {b}")
    return dict(ok=not bad and n > 0, bad=bad[:10], n_compared=n)


def rule(rows):
    out = {}
    for k in weak.SCALES:
        sel = [r for r in rows if r["cell"]["scale"] == k and r["cell"]["n"] >= RULE_N]
        med = [(r["cell"], r["fixed"]["0.5"]["slope"]["med"]) for r in sel]
        outside = [dict(cell=c, med=m) for c, m in med if m is None or not (RULE_LO <= m <= RULE_HI)]
        vals = [m for _, m in med if m is not None]
        out[str(k)] = dict(n_cells=len(sel), med_min=min(vals) if vals else None, med_max=max(vals) if vals else None,
                           outside=outside, verdict=("keep_B" if not outside else "review_candidate"))
    return out


def f3(x):
    return "—" if x is None else f"{x:.3f}"


def f4(x):
    return "—" if x is None else f"{x:.4f}"


def tables(rows, rl, w4, meta):
    L = [f"# 表 —— 弱い信号（run_id {meta['run_id']}・各 {meta['reps']} 反復）", "",
         "W4（係数 1 倍が前の summary.json と一致）: " + ("PASS" if w4["ok"] else "FAIL") + f"（比べた値 {w4['n_compared']}）", "",
         f"## 読みの規則（W2）: n ≥ {RULE_N}・信号ありで τ = 0.5 の傾きの中央値が [{RULE_LO}, {RULE_HI}]", "",
         "| 係数の倍率 | セル | 中央値の最小 | 最大 | 外れたセル | 規則の答え |", "|---|---|---|---|---|---|"]
    for k, v in rl.items():
        L.append(f"| {k} | {v['n_cells']} | {f3(v['med_min'])} | {f3(v['med_max'])} | {len(v['outside'])} | "
                 + ("案 B を保つ" if v["verdict"] == "keep_B" else "見直しの候補") + " |")
    taus = [report.tau_s(t) for t in range(sim.NT)]
    for k in weak.SCALES:
        sub = [r for r in rows if r["cell"]["scale"] == k]
        L += ["", f"## 係数 {k} 倍: 固定の τ の傾きの中央値（σ_d 0.5 / 0 を / で並べる）", "",
              "| n | 率 | " + " | ".join(f"τ={t}" for t in taus[1:]) + " |", "|---|---|" + "---|" * (len(taus) - 1)]
        for n in sim.NS:
            for rt in sim.RATES:
                cs = {r["cell"]["sd"]: r for r in sub if r["cell"]["n"] == n and r["cell"]["rate"] == rt}
                L.append(f"| {n} | {rt} | " + " | ".join(
                    f"{f3(cs[0.5]['fixed'][t]['slope']['med'])} / {f3(cs[0.0]['fixed'][t]['slope']['med'])}" for t in taus[1:]) + " |")
        L += ["", f"## 係数 {k} 倍: 後悔の平均（後知恵の最良の固定の τ に対する対数損失の差・σ_d 0.5 / 0）", "",
              "| n | 率 | 案 A（τ=0.25） | 案 B（τ=0.5） | 案 C′ | 前向きの CV | 1-SE | τ=1 |", "|---|---|---|---|---|---|---|---|"]
        for n in sim.NS:
            for rt in sim.RATES:
                cs = {r["cell"]["sd"]: r for r in sub if r["cell"]["n"] == n and r["cell"]["rate"] == rt}
                g = lambda key, src="plans": " / ".join(f4(cs[s][src][key]["regret"]["mean"]) for s in (0.5, 0.0))
                L.append(f"| {n} | {rt} | {g('A')} | {g('B')} | {g('Cp')} | {g('fwd')} | {g('1se')} | {g('1', 'fixed')} |")
        L += ["", f"## 係数 {k} 倍: 案ごとの後悔の最大（信号ありの 36 セル）と傾きの中央値の範囲（n ≥ {RULE_N}）", "",
              "| 案 | 後悔の最大 | 傾きの中央値の最小 | 最大 |", "|---|---|---|---|"]
        big = [r for r in sub if r["cell"]["n"] >= RULE_N]
        for key, name in (("A", "案 A"), ("B", "案 B"), ("Cp", "案 C′"), ("fwd", "前向きの CV"), ("1se", "1-SE")):
            mx = max(r["plans"][key]["regret"]["mean"] for r in sub)
            ms = [r["plans"][key]["slope"]["med"] for r in big if r["plans"][key]["slope"]["med"] is not None]
            L.append(f"| {name} | {f4(mx)} | {f3(min(ms) if ms else None)} | {f3(max(ms) if ms else None)} |")
    return "\n".join(L) + "\n"


def main(argv):
    res_dir = argv[0]
    opt = dict(zip(argv[1::2], argv[2::2]))
    meta, cl = load(res_dir, opt.get("--run-id"))
    rows = cell_rows(cl)
    w4 = g_w4(rows)
    rl = rule(rows)
    json.dump(dict(run_id=meta["run_id"], seed=meta["seed"], reps=meta["reps"], w4=w4, rule=rl, cells=rows),
              open(os.path.join(res_dir, "summary.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(res_dir, "tables.md"), "w").write(tables(rows, rl, w4, meta))
    print("W4", "OK" if w4["ok"] else "FAIL", w4["bad"][:3])
    print({k: v["verdict"] for k, v in rl.items()})
    sys.exit(0 if w4["ok"] else 3)


if __name__ == "__main__":
    main(sys.argv[1:])
