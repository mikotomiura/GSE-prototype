"""門 G1〜G8（conditions.md C5）。G6〜G8 は小さな反復（100）で回す。G7・G8 は report.py が主の結果でも確かめる。

使い方: python3 -I -X utf8 selftest.py SEED OUT.json [--only G1,G4] [--mutate m1] [--jobs 8] [--run-id ID]
どれかの門が落ちたら終了コード 3。
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I でもスクリプトの隣を読む
import sim  # noqa: E402

GATES = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]


def g1(seed):
    rng = np.random.default_rng([seed, 901, 1])  # 主のセルの流れと重ならない
    n = 60
    Z = rng.standard_normal((n, sim.P))
    y = (rng.random(n) < sim.sigmoid(Z @ sim.BETA - 0.5)).astype(float)
    out = {}
    worst = 0.0
    for tau in sim.TAUS[1:-1]:
        lam = 1 / tau ** 2
        th, _ = sim.fit_logistic(Z, y, lam=lam)
        Zp = np.vstack([Z, np.zeros((2, sim.P))])
        yp = np.concatenate([y, [1.0, 0.0]])
        w = np.concatenate([np.ones(n), [0.5, 0.5]])
        Xd = np.hstack([np.ones((n + 2, 1)), Zp])
        R = np.eye(sim.P + 1) * lam
        R[0, 0] = 0.0
        g = Xd.T @ (w * (yp - sim.sigmoid(Xd @ th))) - R @ th
        worst = max(worst, float(np.max(np.abs(g))))
    out["a_grad_max"] = worst
    b0, _, _ = sim.fit_tau(Z, y, 0.0)
    closed = math.log((y.sum() + 0.5) / (n + 1 - y.sum() - 0.5))
    out["b_intercept_only_diff"] = abs(b0 - closed)
    th, _ = sim.fit_logistic(Z, y, lam=1e10)
    out["c_big_lam_intercept_diff"] = abs(float(th[0]) - closed)
    out["c_big_lam_beta_max"] = float(np.max(np.abs(th[1:])))
    n2 = 2000
    Z2 = rng.standard_normal((n2, sim.P))
    y2 = (rng.random(n2) < sim.sigmoid(Z2 @ sim.BETA - 1)).astype(float)
    th2, conv = sim.fit_logistic(Z2, y2, lam=0.0, pseudo=False)
    Xd2 = np.hstack([np.ones((n2, 1)), Z2])
    out["d_mle_grad_max"] = float(np.max(np.abs(Xd2.T @ (y2 - sim.sigmoid(Xd2 @ th2)))))
    out["d_conv"] = bool(conv)
    b3, be3, conv3 = sim.fit_tau(Z2, y2, math.inf)  # 本計算の τ = ∞ と同じ経路（擬似観測あり）
    th3 = np.concatenate([[b3], be3])
    Xd3 = np.vstack([Xd2, np.hstack([np.ones((2, 1)), np.zeros((2, sim.P))])])
    y3 = np.concatenate([y2, [1.0, 0.0]])
    w3 = np.concatenate([np.ones(n2), [0.5, 0.5]])
    out["d_fit_tau_grad_max"] = float(np.max(np.abs(Xd3.T @ (w3 * (y3 - sim.sigmoid(Xd3 @ th3))))))
    ok = (out["a_grad_max"] < 1e-6 and out["b_intercept_only_diff"] < 1e-8 and out["c_big_lam_intercept_diff"] < 1e-4
          and out["c_big_lam_beta_max"] < 1e-6 and out["d_mle_grad_max"] < 1e-6
          and out["d_fit_tau_grad_max"] < 1e-6)
    return ok, out


def g2(seed):
    """one_rep と同じ経路で作った標準化が学習の側だけの値と一致し、評価の側を混ぜた値と一致しない。"""
    rng = np.random.default_rng([seed, 902, 1])  # 主のセルの流れと重ならない
    a = 0.0
    Xtr, ytr, dtr, _ = sim.gen(rng, 50, 0.5, a, sim.BETA, "main", False)
    Xev, _, _, _ = sim.gen(rng, 500, 0.5, a, sim.BETA, "main", False, day0=int(dtr.max()) + 1)
    std = sim.make_std(Xtr, Xev)  # one_rep と同じ関数
    mu_tr, sd_tr = Xtr.mean(0), Xtr.std(0)
    allx = np.vstack([Xtr, Xev])
    out = dict(mu_diff=float(np.max(np.abs(std.mu - mu_tr))), sd_diff=float(np.max(np.abs(std.sd - sd_tr))),
               mu_diff_vs_all=float(np.max(np.abs(std.mu - allx.mean(0)))))
    D = int(dtr.max()) + 1
    fold_bad = 0
    for tr_days, va_days in sim.fwd_folds(D) + sim.loo_folds(D):
        mt, mv = np.isin(dtr, tr_days), np.isin(dtr, va_days)
        fs = sim.fold_std(Xtr, mt, mv)  # cv_matrix と同じ関数
        sd_t = Xtr[mt].std(0)
        sd_t[sd_t == 0] = 1.0
        fold_bad += not (np.max(np.abs(fs.mu - Xtr[mt].mean(0))) < 1e-12 and np.max(np.abs(fs.sd - sd_t)) < 1e-12)
    out["fold_bad"] = int(fold_bad)
    ok = out["mu_diff"] < 1e-12 and out["sd_diff"] < 1e-12 and out["mu_diff_vs_all"] > 1e-6 and fold_bad == 0
    return ok, out


def g3(seed):
    rng = np.random.default_rng([seed, 903, 1])  # 主のセルの流れと重ならない
    bad = 0
    for D in [2, 3, 5, 7, 23, 60]:
        for tr, va in sim.fwd_folds(D, rng):
            if not (tr.max() < va.min()):
                bad += 1
        bl = sim.blocks_of(D, rng)
        for b in bl:
            if not np.all(np.diff(b) == 1):
                bad += 1
        lo = sim.loo_folds(D)
        seen = np.concatenate([va for _, va in lo])
        if sorted(seen.tolist()) != list(range(D)) or len(lo) != min(5, D):
            bad += 1
    # 評価の側の日
    Xtr, ytr, dtr, _ = sim.gen(rng, 37, 0.5, 0.0, sim.BETA, "main", False)
    D = int(dtr.max()) + 1
    _, _, dev, _ = sim.gen(rng, 100, 0.5, 0.0, sim.BETA, "main", False, day0=D)
    if not dev.min() >= dtr.max() + 1:
        bad += 1
    return bad == 0, dict(bad=bad)


def g4(seed):
    # 同点: 番号 2 と 5 が最小で同じ → 2
    tot = np.array([5.0, 4.0, 3.0, 3.5, 3.2, 3.0, 4.0, 6.0])
    c = sim.pick_min(tot)
    # 1-SE: 3 折。main = 4。番号 2 の差は (0.1, 0.3, -0.1) → mean 0.1・se = sd/√3 = 0.2/1.732 = 0.115 → 範囲内
    # 番号 1 の差は (1, 1.2, 0.8) → mean 1.0 > se → 範囲外。強い罰の側で範囲内の最小の番号は 2
    F = np.array([[3.0, 3.0, 2.1, 2.5, 2.0, 2.2, 2.6, 3.0],
                  [3.2, 3.2, 2.3, 2.6, 2.0, 2.1, 2.5, 3.1],
                  [2.8, 2.8, 1.9, 2.4, 2.0, 2.3, 2.7, 3.2]])
    main = sim.pick_min(F.sum(0))
    one = sim.pick_1se(F, main)
    out = dict(tie_pick=c, main=main, one_se=one)
    return (c == 2 and main == 4 and one == 2), out


def g5(seed):
    out = {}
    worst = 0.0
    for i, (r, sd, sig, kind) in enumerate(sim.acells()):
        a = sim.calib_a(seed, i, r, sd, sig, kind)
        rng = np.random.default_rng([seed, 98, i])
        beta = sim.BETA if sig else np.zeros(sim.P)
        _, y, _, _ = sim.gen(rng, sim.N_CALIB, sd, a, beta, kind, False)
        dev = abs(float(y.mean()) - r)
        worst = max(worst, dev)
        out[f"{r}_{sd}_{sig}_{kind}"] = round(float(y.mean()), 4)
    out["worst"] = worst
    return worst < 0.005, out


def small(seed, sets, pick, jobs, reps=100):
    cl = [c for c in sim.cells(seed, sets) if pick(c)]
    res = sim.run_cells(seed, cl, reps, jobs, sorted(sim.MUT))
    return list(res.values())[0]


def regret_stats(arr, choice):
    ll = arr["met"][:, :, 0]
    best = ll.min(1)
    ch = arr[choice]
    reg = ll[np.arange(len(ll)), ch] - best
    return reg, ll.argmin(1)


def g6(seed, jobs):
    c, arr = small(seed, ["cons"], lambda c: True, jobs)
    reg, best = regret_stats(arr, "c_fwd")
    weak = float(np.mean(arr["c_fwd"] >= 2))  # τ ≥ 0.25（強すぎる罰を選ばない・判断 5）
    near = float(np.mean(np.abs(arr["c_fwd"] - best) <= 1))  # 記述だけ（2000 件では弱い罰の側が平らで雑音で決まる）
    out = dict(mean_regret=float(reg.mean()), weak_frac=weak, near_frac_descr=near, reps=len(reg))
    return out["mean_regret"] < 0.002 and weak >= 0.95, out


def g7_check(arr):
    ll = arr["met"][:, :, 0]
    harm = ll[np.arange(len(ll)), arr["c_fwd"]] - ll[:, 0]
    up = float(harm.mean() + 1.96 * harm.std(ddof=1) / math.sqrt(len(harm)))
    cc = arr["met"][np.arange(len(ll)), arr["c_fwd"], 2]
    cmean = float(np.nanmean(cc))
    out = dict(harm_mean=float(harm.mean()), harm_upper=up, c_mean=cmean, reps=len(harm))
    return up < 0 and cmean > 0.6, out


def g8_check(arr):
    cinf = arr["met"][:, -1, 2]
    cm = float(np.nanmean(cinf))
    best = arr["met"][:, :, 0].argmin(1)
    strong = float(np.mean(best <= 2))  # τ ∈ {0, 0.125, 0.25}
    out = dict(c_inf_mean=cm, best_strong_frac=strong, reps=len(best))
    return abs(cm - 0.5) <= 0.01 and strong >= 0.5, out


def is_cell(n, sig):
    return lambda c: c["n"] == n and c["rate"] == 0.25 and c["sd"] == 0.0 and c["signal"] == sig


def g7(seed, jobs):
    return g7_check(small(seed, ["main"], is_cell(120, True), jobs)[1])


def g8(seed, jobs):
    return g8_check(small(seed, ["main"], is_cell(120, False), jobs)[1])


def main(argv):
    seed, out = int(argv[0]), argv[1]
    opt = dict(zip(argv[2::2], argv[3::2]))
    only = opt.get("--only", ",".join(GATES)).split(",")
    sim.MUT.update(m for m in opt.get("--mutate", "").split(",") if m)
    jobs = int(opt.get("--jobs", 8))
    fn = dict(G1=lambda: g1(seed), G2=lambda: g2(seed), G3=lambda: g3(seed), G4=lambda: g4(seed),
              G5=lambda: g5(seed), G6=lambda: g6(seed, jobs), G7=lambda: g7(seed, jobs), G8=lambda: g8(seed, jobs))
    R = {}
    for g in only:
        ok, detail = fn[g]()
        R[g] = dict(ok=bool(ok), **detail)
        print(g, "OK" if ok else "FAIL", detail, flush=True)
    with open(out, "w") as f:
        json.dump(dict(seed=seed, run_id=opt.get("--run-id"), mutate=sorted(sim.MUT), gates=R), f,
                  ensure_ascii=False, indent=1)
    sys.exit(0 if all(v["ok"] for v in R.values()) else 3)


if __name__ == "__main__":
    main(sys.argv[1:])
