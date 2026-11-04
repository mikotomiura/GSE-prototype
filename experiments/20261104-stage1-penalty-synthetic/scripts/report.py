"""集計・案の値（conditions.md C3・C4）・主の結果での G7・G8（C5）。

使い方: python3 -I -X utf8 report.py RESULTS_DIR [--run-id ID]
RESULTS_DIR/raw/ を読み、summary.json・proposal.json・tables.md を書く。G7・G8 が落ちたら終了コード 3。
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selftest  # noqa: E402
import sim  # noqa: E402

EPS = 1e-6
L_N = [0, 10, 20, 30, 50, 80, 120, math.inf]
L_MIN = [0, 1, 2, 3, 5, 8, 10, 15, 20, 30, math.inf]
CV_KEYS = ["c_fwd", "c_1se"]


def tau_s(i):
    t = sim.TAUS[i]
    return "inf" if math.isinf(t) else ("0" if t == 0 else f"{t:g}")


def mci(v):
    v = np.asarray(v, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 2:
        return dict(mean=None, lo=None, hi=None, n=int(len(v)))
    m, se = float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))
    return dict(mean=m, lo=m - 1.96 * se, hi=m + 1.96 * se, n=int(len(v)))


def quart(v):
    v = np.asarray(v, dtype=float)
    v = v[~np.isnan(v)]
    if not len(v):
        return dict(q1=None, med=None, q3=None, n=0)
    q = np.percentile(v, [25, 50, 75])
    return dict(q1=float(q[0]), med=float(q[1]), q3=float(q[2]), n=int(len(v)))


def dist(ch):
    c = np.bincount(np.asarray(ch, dtype=int), minlength=sim.NT) / len(ch)
    return {tau_s(i): round(float(x), 4) for i, x in enumerate(c)}


def per_choice(arr, ch):
    """反復ごとの選び ch（番号の配列）のもとでの量。"""
    met = arr["met"]
    idx = np.arange(len(ch))
    ll = met[:, :, 0]
    sel = met[idx, ch]
    return dict(ll=mci(sel[:, 0]), brier=mci(sel[:, 1]), c=mci(sel[:, 2]), citl=quart(sel[:, 3]),
                slope=quart(sel[:, 4]), regret=mci(sel[:, 0] - ll.min(1)), harm=mci(sel[:, 0] - ll[:, 0]))


def cell_summary(c, arr):
    ll = arr["met"][:, :, 0]
    out = dict(cell={k: c[k] for k in ("id", "set", "n", "rate", "sd", "signal", "kind")},
               reps=int(len(ll)), oracle_ll=mci(arr["oracle"]))
    out["fixed"] = {tau_s(t): per_choice(arr, np.full(len(ll), t)) for t in range(sim.NT)}
    for k in ("c_fwd", "c_1se", "c_loo"):
        out[k] = per_choice(arr, arr[k])
        out[k]["dist"] = dist(arr[k])
    out["best_dist"] = dist(ll.argmin(1))
    out["diag"] = dict(one_class=int(np.sum((arr["npos"] == 0) | (arr["nneg"] == 0))),
                       cv_not_ok=int(np.sum(arr["cv_ok"] == 0)),
                       nonconv_full={tau_s(t): int(arr["nc_full"][:, t].sum()) for t in range(sim.NT)},
                       nonconv_fwd={tau_s(t): int(arr["nc_fwd"][:, t].sum()) for t in range(sim.NT)},
                       nonconv_loo={tau_s(t): int(arr["nc_loo"][:, t].sum()) for t in range(sim.NT)},
                       nonconv_slope={tau_s(t): int(np.nansum(arr["met"][:, t, 5])) for t in range(sim.NT)},
                       days=quart(arr["D"]), npos=quart(arr["npos"]))
    return out


def mean_regret(arr, ch):
    ll = arr["met"][:, :, 0]
    return float(np.mean(ll[np.arange(len(ch)), ch] - ll.min(1)))


def combo_choice(arr, q, L, tf, cvk):
    qv = arr["npos"] + arr["nneg"] if q == "n" else np.minimum(arr["npos"], arr["nneg"])
    return np.where(qv < L, tf, arr[cvk])


def rules(main):
    """C4 の 1〜3。main は [(c, arr)]。"""
    small = [(c, a) for c, a in main if c["n"] in (10, 20, 30)]
    if not small:
        return None
    mx = [max(mean_regret(a, np.full(len(a["D"]), t)) for _, a in small) for t in range(sim.NT)]
    tf = int(np.where(np.array(mx) <= min(mx) + EPS)[0][0])
    cvmx = {k: max(mean_regret(a, a[k]) for _, a in main) for k in CV_KEYS}
    cvk = "c_1se" if cvmx["c_1se"] <= cvmx["c_fwd"] + EPS else "c_fwd"
    out = dict(tau_f=tau_s(tf), tau_f_idx=tf, tau_f_max_regret={tau_s(t): mx[t] for t in range(sim.NT)},
               cv_version=cvk, cv_max_regret=cvmx, L={})
    for q, cands in (("n", L_N), ("min_class", L_MIN)):
        rows = []
        for L in cands:
            ex = []
            for _, a in main:
                base = min(mean_regret(a, np.full(len(a["D"]), tf)), mean_regret(a, a[cvk]))
                ex.append(mean_regret(a, combo_choice(a, q, L, tf, cvk)) - base)
            rows.append((L, max(ex)))
        best = min(r[1] for r in rows)
        Lsel = [r[0] for r in rows if r[1] <= best + EPS][-1]  # 同点は大きい L
        out["L"][q] = dict(L=("inf" if math.isinf(Lsel) else Lsel),
                           max_excess={("inf" if math.isinf(L) else str(L)): v for L, v in rows})
    return out


def posthoc(main, tf):
    """記述だけ（C4 の外・判断 8）: CV の版を前向きにした組み合わせの超過の最大と、
    n = 10 のセルの前向きの CV の後悔のうち τ = ∞ を選んだ反復の寄与。"""
    out = dict(combo_fwd={})
    for q, cands in (("n", L_N), ("min_class", L_MIN)):
        rows = {}
        for L in cands:
            ex = []
            for _, a in main:
                base = min(mean_regret(a, np.full(len(a["D"]), tf)), mean_regret(a, a["c_fwd"]))
                ex.append(mean_regret(a, combo_choice(a, q, L, tf, "c_fwd")) - base)
            rows["inf" if math.isinf(L) else str(L)] = max(ex)
        out["combo_fwd"][q] = rows
    contrib = []
    for c, a in main:
        if c["n"] != 10:
            continue
        ll = a["met"][:, :, 0]
        reg = ll[np.arange(len(ll)), a["c_fwd"]] - ll.min(1)
        m = a["c_fwd"] == sim.NT - 1
        contrib.append(dict(cell={k: c[k] for k in ("rate", "sd", "signal")}, frac_inf=float(m.mean()),
                            cond_regret_inf=(float(reg[m].mean()) if m.any() else None),
                            contrib_inf=float(reg[m].sum() / len(reg)), total=float(reg.mean())))
    out["inf_contrib_n10"] = contrib
    return out


def describe_proposal(cells_arr, pr):
    tf, cvk = pr["tau_f_idx"], pr["cv_version"]
    out = {}
    for q in ("n", "min_class"):
        L = pr["L"][q]["L"]
        L = math.inf if L == "inf" else L
        rows = []
        for c, a in cells_arr:
            ch = combo_choice(a, q, L, tf, cvk)
            s = per_choice(a, ch)
            s["dist"] = dist(ch)
            s["cell"] = {k: c[k] for k in ("id", "set", "n", "rate", "sd", "signal")}
            rows.append(s)
        out[q] = rows
    return out


def load(res_dir, run_id=None):
    """raw を読み、来歴を照らす（判断 8）: run_id が一致・変異なし・セルの id と条件が期待の集合と一致・
    反復の数が揃う。違えば ValueError。"""
    raw = os.path.join(res_dir, "raw")
    meta = json.load(open(os.path.join(raw, "cells.json")))
    if run_id is not None and meta.get("run_id") != run_id:
        raise ValueError(f"raw の run_id {meta.get('run_id')} が指定 {run_id} と違う")
    if meta.get("mutate"):
        raise ValueError(f"raw が変異つきの計算 {meta['mutate']}")
    expect = {c["id"]: c for c in sim.cells(meta["seed"], sorted({c["set"] for c in meta["cells"]}))}
    got = {c["id"]: c for c in meta["cells"]}
    if len(got) != len(meta["cells"]) or set(got) != set(expect):
        raise ValueError("セルの id が期待の集合と違う（重複か欠け）")
    for i, c in got.items():
        e = expect[i]
        if any(c[k] != e[k] for k in ("set", "n", "rate", "sd", "signal", "kind")) or abs(c["a"] - e["a"]) > 1e-12:
            raise ValueError(f"セル {i} の条件が期待と違う")
    cl = []
    for c in meta["cells"]:
        z = np.load(os.path.join(raw, f"cell{c['id']:03d}.npz"))
        arr = {k: z[k] for k in z.files}
        want = meta["reps"] if c["set"] != "cons" else min(meta["reps"], 100)
        if len(arr["D"]) != want:
            raise ValueError(f"セル {c['id']} の反復の数 {len(arr['D'])} が {want} でない")
        cl.append((c, arr))
    return meta, cl


def f3(x):
    return "—" if x is None else f"{x:.4f}"


def tables(summ, pr, desc):
    L = ["# 表（report.py が書く・手で直さない）", ""]
    if pr:
        L += ["## 案の値（C4 の規則を機械的に当てた）", "",
              f"- τ_f = {pr['tau_f']}（n ≤ 30 の 36 セルの平均の後悔の最大が最小）",
              f"- CV の版 = {pr['cv_version']}（72 セルの平均の後悔の最大: " +
              ", ".join(f"{k} {v:.4f}" for k, v in pr["cv_max_regret"].items()) + "）",
              f"- 下限 L（総件数）= {pr['L']['n']['L']}・下限 L（少ない方の類の件数）= {pr['L']['min_class']['L']}", "",
              "| τ | n ≤ 30 の平均の後悔の最大 |", "|---|---|"]
        L += [f"| {k} | {v:.4f} |" for k, v in pr["tau_f_max_regret"].items()]
        for q in ("n", "min_class"):
            L += ["", f"| L（{q}・q < L なら固定） | 超過の最大 |", "|---|---|"]
            L += [f"| {k} | {v:.4f} |" for k, v in pr["L"][q]["max_excess"].items()]
        if pr.get("excl"):
            e = pr["excl"]
            L += ["", f"- n = 10・r = 0.10 の 4 セルを除いた版: τ_f = {e['tau_f']}・CV の版 = {e['cv_version']}・"
                  f"L（総件数）= {e['L']['n']['L']}・L（少ない方の類）= {e['L']['min_class']['L']}"]
    if pr and pr.get("posthoc"):
        ph = pr["posthoc"]
        L += ["", "## 記述（C4 の外・判断 8）: CV の版を前向きにした組み合わせの超過の最大", "",
              "基準はセルごとの「τ_f の固定と前向きの CV の良い方」。C4 の表（1-SE が基準）とは基準が違う。"]
        for q in ("n", "min_class"):
            L += ["", f"| L（{q}・q < L なら固定） | 超過の最大 |", "|---|---|"]
            L += [f"| {k} | {v:.4f} |" for k, v in ph["combo_fwd"][q].items()]
        L += ["", "## 記述: n = 10 の前向きの CV の後悔のうち τ = ∞ を選んだ反復の寄与", "",
              "| r | σ_d | 信号 | τ=∞ を選んだ割合 | その反復の平均の後悔 | 寄与 | 後悔の全体 |", "|---|---|---|---|---|---|---|"]
        for r in ph["inf_contrib_n10"]:
            c = r["cell"]
            L.append(f"| {c['rate']} | {c['sd']} | {'あり' if c['signal'] else 'なし'} | {r['frac_inf']:.3f} | "
                     f"{f3(r['cond_regret_inf'])} | {r['contrib_inf']:.4f} | {r['total']:.4f} |")
    for st in ("main", "s1", "s2", "cons"):
        rows = [s for s in summ if s["cell"]["set"] == st]
        if not rows:
            continue
        L += ["", f"## {st}: 平均の後悔（固定の τ・CV）", "",
              "| n | r | σ_d | 信号 | " + " | ".join(f"τ={tau_s(t)}" for t in range(sim.NT)) +
              " | fwd | 1se | loo |", "|" + "---|" * (4 + sim.NT + 3)]
        for s in rows:
            c = s["cell"]
            L.append(f"| {c['n']} | {c['rate']} | {c['sd']} | {'あり' if c['signal'] else 'なし'} | " +
                     " | ".join(f3(s["fixed"][tau_s(t)]["regret"]["mean"]) for t in range(sim.NT)) + " | " +
                     " | ".join(f3(s[k]["regret"]["mean"]) for k in ("c_fwd", "c_1se", "c_loo")) + " |")
        L += ["", f"## {st}: 前向きの CV が選んだ τ の割合（と 1 類だけの反復の数）", "",
              "| n | r | σ_d | 信号 | " + " | ".join(f"τ={tau_s(t)}" for t in range(sim.NT)) + " | 1 類だけ |",
              "|" + "---|" * (4 + sim.NT + 1)]
        for s in rows:
            c = s["cell"]
            L.append(f"| {c['n']} | {c['rate']} | {c['sd']} | {'あり' if c['signal'] else 'なし'} | " +
                     " | ".join(f"{s['c_fwd']['dist'][tau_s(t)]:.2f}" for t in range(sim.NT)) +
                     f" | {s['diag']['one_class']} |")
    if desc:
        for q in ("n", "min_class"):
            L += ["", f"## 案（q = {q}）のもとでの量", "",
                  "| 集合 | n | r | σ_d | 信号 | 害の平均 [95%] | 後悔の平均 | C の平均 | 傾きの中央値 [四分位]（立った数） |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for s in desc[q]:
                c = s["cell"]
                h, sl = s["harm"], s["slope"]
                hs = "—" if h["mean"] is None else f"{h['mean']:.4f} [{h['lo']:.4f}, {h['hi']:.4f}]"
                ss = "—" if sl["med"] is None else f"{sl['med']:.2f} [{sl['q1']:.2f}, {sl['q3']:.2f}]（{sl['n']}）"
                L.append(f"| {c['set']} | {c['n']} | {c['rate']} | {c['sd']} | {'あり' if c['signal'] else 'なし'} | "
                         f"{hs} | {f3(s['regret']['mean'])} | {f3(s['c']['mean'])} | {ss} |")
    return "\n".join(L) + "\n"


def main(argv):
    res_dir = argv[0]
    opt = dict(zip(argv[1::2], argv[2::2]))
    meta, cl = load(res_dir, opt.get("--run-id"))
    summ = [cell_summary(c, a) for c, a in cl]
    main_cells = [(c, a) for c, a in cl if c["set"] == "main"]
    pr = rules(main_cells) if len(main_cells) == 72 else None
    desc = None
    if pr:
        excl = [(c, a) for c, a in main_cells if not (c["n"] == 10 and c["rate"] == 0.10)]
        pr["excl"] = rules(excl)
        pr["posthoc"] = posthoc(main_cells, pr["tau_f_idx"])
        desc = describe_proposal(cl, pr)
    gates = {}

    def find(sig):
        for c, a in main_cells:
            if c["n"] == 120 and c["rate"] == 0.25 and c["sd"] == 0.0 and c["signal"] == sig:
                return a
        return None

    for g, sig, fn in (("G7", True, selftest.g7_check), ("G8", False, selftest.g8_check)):
        a = find(sig)
        if a is not None:
            ok, d = fn(a)
            gates[g] = dict(ok=bool(ok), **d)
            print(g, "OK" if ok else "FAIL", d, flush=True)
    rid = opt.get("--run-id")
    json.dump(dict(run_id=rid, seed=meta["seed"], reps=meta["reps"], mutate=meta["mutate"], cells=summ),
              open(os.path.join(res_dir, "summary.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(dict(run_id=rid, proposal=pr, gates=gates, described=desc),
              open(os.path.join(res_dir, "proposal.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(res_dir, "tables.md"), "w").write(tables(summ, pr, desc))
    # 門が欠けたら通さない（「落ちていない」を「通った」と読まない）
    complete = len(main_cells) == 72 and set(gates) == {"G7", "G8"}
    if not complete:
        print("G7・G8 が揃わない（主のセルが 72 でないか、対照のセルが無い）", flush=True)
    sys.exit(0 if complete and all(v["ok"] for v in gates.values()) else 3)


if __name__ == "__main__":
    main(sys.argv[1:])
