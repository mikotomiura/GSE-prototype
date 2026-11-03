"""MhD の配管の空回し 第 2 版 (a) 合成の日の模擬（conditions.md の A1〜A6）。

打鍵は作らない。1 人の中の日を単位に、ラベルと凍結したモデルの予測だけを作り、
評価の側の日の巡回するブロックの再標本化で、較正の切片と傾きの区間の幅と被覆を出す。
値（λ・π・AUC・日の揺れ）は仮置きで、段 1 の見込みではない（conditions.md「読まないこと」）。

使い方:
  python3 -I daysim.py --selftest <seed> <out_dir>             陽性対照 P1〜P4（selftest_daysim.json に書く）
  python3 -I daysim.py --selftest --mutate m1|m2 <seed> <out>  変異で P3 が赤になるか（書き出しは selftest_daysim_<m>.json）
  python3 -I daysim.py <seed> <out_dir>                        本計算（daysim.json）
"""
import json
import math
import os
import sys
import time

import numpy as np

MUTATE = None  # None / "m1"（傾きで y と p̂ を取り違える）/ "m2"（切片のオフセットを外す）
B = 500
MIN_OK = 100
SEP = 50.0
POP_DAYS = 50_000
TRAIN_FRAC = 0.6


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -35, 35)))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


# ---------------------------------------------------------------- 重み付きの Newton 法（反復をまとめて解く）
def wfit(X, y, W, offset=None, tol=1e-8, maxit=100):
    """X: (n, k)（切片の列を含む）・y: (n,)・W: (R, n) 非負の重み。戻り値 beta (R, k)・converged (R,)。"""
    R, n = W.shape
    k = X.shape[1]
    off = np.zeros(n) if offset is None else offset
    beta = np.zeros((R, k))
    conv = np.zeros(R, dtype=bool)
    for _ in range(maxit):
        eta = beta @ X.T + off  # (R, n)
        p = sigmoid(eta)
        g = ((W * (y - p)) @ X)  # (R, k)
        w = W * p * (1 - p)
        H = np.einsum("rn,ni,nj->rij", w, X, X) + 1e-12 * np.eye(k)
        step = np.linalg.solve(H, g[..., None])[..., 0]
        step[conv] = 0.0
        beta = beta + step
        done = np.max(np.abs(step), axis=1) < tol
        conv |= done
        if conv.all():
            break
    bad = ~np.isfinite(beta).all(axis=1)
    conv &= ~bad
    return beta, conv


def calib_w(y, phat, W):
    """較正の切片と傾き（重みの行ごと）。戻り値 inter, slope, conv_i, conv_s。"""
    lp = logit(phat)
    n = len(y)
    one = np.ones((n, 1))
    if MUTATE == "m2":
        bi, ci_ = wfit(one, y, W)
    else:
        bi, ci_ = wfit(one, y, W, offset=lp)
    if MUTATE == "m1":
        ly = logit(y.astype(float))
        bs, cs = wfit(np.hstack([one, ly[:, None]]), phat, W)
    else:
        bs, cs = wfit(np.hstack([one, lp[:, None]]), y, W)
    return bi[:, 0], bs[:, 1], ci_, cs


# ---------------------------------------------------------------- 生成
def ar1(rng, D, sd, rho):
    u = np.empty(D)
    if sd == 0:
        return np.zeros(D)
    u[0] = rng.normal(0, sd)
    e = rng.normal(0, sd, D)
    for d in range(1, D):
        u[d] = rho * u[d - 1] + math.sqrt(1 - rho * rho) * e[d]
    return u


def gen(rng, D, lam, a, s, sd, rho):
    u = ar1(rng, D, sd, rho)
    n = rng.poisson(lam, D)
    day = np.repeat(np.arange(D), n)
    z = rng.normal(0, 1, len(day))
    eta = a + s * z
    y = (rng.random(len(day)) < sigmoid(eta + u[day])).astype(float)
    return day, sigmoid(eta), y


def auc(y, p):
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty(len(allv))
    ranks[order] = np.arange(1, len(allv) + 1)
    # 連続な値なので同順位は無い見込み（z は正規乱数）
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def solve_params(pi, target_auc, sd, seed):
    """母集団（固定した乱数）で陽性の割合 pi・AUC target_auc になる a, s を二分法で解く。"""
    rng = np.random.default_rng([seed, 999])
    N = 200_000
    z = rng.normal(0, 1, N)
    u = rng.normal(0, sd, N) if sd > 0 else np.zeros(N)
    r = rng.random(N)

    def prev(a, s):
        return float(np.mean(sigmoid(a + s * z + u)))

    def solve_a(s):
        lo, hi = -12.0, 12.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if prev(mid, s) < pi:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def auc_of(s):
        a = solve_a(s)
        y = (r < sigmoid(a + s * z + u)).astype(float)
        return auc(y, z), a  # p̂ は z の単調関数なので z で AUC を数える

    lo, hi = 0.0, 6.0
    for _ in range(50):
        mid = (lo + hi) / 2
        v, _ = auc_of(mid)
        if v < target_auc:
            lo = mid
        else:
            hi = mid
    s = (lo + hi) / 2
    v, a = auc_of(s)
    return a, s, prev(a, s), v


def population_values(rng, lam, a, s, sd, rho):
    """母集団の値は変異を外した正しい計算で出す（変異が基準の側にも効いて打ち消し合わないように）。"""
    global MUTATE
    saved, MUTATE = MUTATE, None
    try:
        day, phat, y = gen(rng, POP_DAYS, lam, a, s, sd, rho)
        W = np.ones((1, len(y)))
        i, sl, ci_, cs = calib_w(y, phat, W)
    finally:
        MUTATE = saved
    return float(i[0]), float(sl[0]), bool(ci_[0] and cs[0])


# ---------------------------------------------------------------- 再標本化
def circ_counts(rng, m, L, R):
    """巡回するブロック: m 日を円に並べ、長さ L のブロックを m 日に達するまで並べて切る。戻り値 (R, m) の選ばれた回数。"""
    nb = math.ceil(m / L)
    starts = rng.integers(0, m, (R, nb))
    idx = (starts[:, :, None] + np.arange(L)[None, None, :]).reshape(R, -1)[:, :m] % m
    C = np.zeros((R, m))
    np.add.at(C, (np.repeat(np.arange(R), m), idx.ravel()), 1.0)
    return C


def one_sim(rng, D, lam, a, s, sd, rho, mode, Lrule):
    day, phat, y = gen(rng, D, lam, a, s, sd, rho)
    t0 = math.ceil(TRAIN_FRAC * D)
    keep = day >= t0
    day, phat, y = day[keep] - t0, phat[keep], y[keep]
    m = D - t0
    n = len(y)
    out = dict(n=n, pos=int(y.sum()), m=m)
    if n == 0 or y.min() == y.max():
        out.update(point=None, ci=None, discarded=B, nonconv=0, sep=0)
        return out
    pi_, ps_, ci0, cs0 = calib_w(y, phat, np.ones((1, n)))
    out["point"] = (float(pi_[0]), float(ps_[0])) if (ci0[0] and cs0[0]) else None
    if mode == "label":
        Wl = rng.multinomial(n, np.full(n, 1.0 / n), B).astype(float)
    else:
        L = Lrule(m)
        C = circ_counts(rng, m, L, B)
        Wl = C[:, day]
    w1 = (Wl * y).sum(axis=1)
    w0 = (Wl * (1 - y)).sum(axis=1)
    okc = (w1 > 0) & (w0 > 0)
    discarded = int((~okc).sum())
    Wl = Wl[okc]
    bi, bs, ci_, cs = calib_w(y, phat, Wl)
    conv = ci_ & cs
    sep = int((np.abs(bs[conv]) > SEP).sum())
    out.update(discarded=discarded, nonconv=int((~conv).sum()), sep=sep)
    if conv.sum() < MIN_OK:
        out["ci"] = None
        return out
    bi, bs = bi[conv], bs[conv]
    out["ci"] = (np.percentile(bi, [2.5, 97.5]).tolist(), np.percentile(bs, [2.5, 97.5]).tolist())
    return out


def rule_main(m):
    return max(2, int(round(m ** (1 / 3))))


def run_point(seed, idx, D, AUC, pi, lam, sd, rho, R, mode="block", Lrule=rule_main):
    ss = np.random.SeedSequence([seed, idx])
    rng = np.random.default_rng(ss)
    a, s, prev, av = solve_params(pi, AUC, sd, seed)
    ti, tsl, tconv = population_values(rng, lam, a, s, sd, rho)
    cov_i = cov_s = 0
    wi, ws, ns, ps = [], [], [], []
    disc = nonc = sepc = noci = 0
    for _ in range(R):
        o = one_sim(rng, D, lam, a, s, sd, rho, mode, Lrule)
        ns.append(o["n"])
        ps.append(o["pos"])
        disc += o["discarded"]
        nonc += o["nonconv"]
        sepc += o["sep"]
        if o["ci"] is None:
            noci += 1
            continue
        (li, hi_), (ls, hs) = o["ci"]
        cov_i += li <= ti <= hi_
        cov_s += ls <= tsl <= hs
        wi.append(hi_ - li)
        ws.append(hs - ls)

    def q(v):
        return [float(x) for x in np.percentile(v, [25, 50, 75])] if v else None

    return dict(D=D, eval_days=D - math.ceil(TRAIN_FRAC * D), AUC=AUC, pi=pi, lam=lam, sd=sd, rho=rho, mode=mode,
                L=(None if mode == "label" else Lrule(D - math.ceil(TRAIN_FRAC * D))), R=R,
                solved=dict(a=a, s=s, prevalence=prev, auc=av),
                population=dict(cal_intercept=ti, cal_slope=tsl, converged=tconv),
                n_label_q=q(ns), n_pos_q=q(ps),
                width_intercept_q=q(wi), width_slope_q=q(ws),
                coverage_intercept=cov_i / R, coverage_slope=cov_s / R,
                sims_without_ci=noci, resamples_discarded_one_class=disc, resamples_nonconverged=nonc,
                resamples_slope_abs_gt_50=sepc)


# ---------------------------------------------------------------- 陽性対照
def selftest(seed):
    res = {}
    ok = True
    # P1
    rng = np.random.default_rng([seed, 1])
    n = 300
    X = np.hstack([np.ones((n, 1)), rng.normal(size=(n, 1))])
    y = (rng.random(n) < sigmoid(X @ np.array([-0.4, 1.1]))).astype(float)
    w = rng.integers(0, 4, n).astype(float)
    b1, c1 = wfit(X, y, w[None, :])
    rep = np.repeat(np.arange(n), w.astype(int))
    b2, c2 = wfit(X[rep], y[rep], np.ones((1, len(rep))))
    eq = bool(c1[0] and c2[0] and np.max(np.abs(b1 - b2)) < 1e-6)
    N = 20000
    X = np.hstack([np.ones((N, 1)), rng.normal(size=(N, 2))])
    yy = (rng.random(N) < sigmoid(X @ np.array([-0.3, 0.8, -1.2]))).astype(float)
    b3, _ = wfit(X, yy, np.ones((1, N)))
    rec = bool(np.all(np.abs(b3[0] - np.array([-0.3, 0.8, -1.2])) < 0.05))
    res["P1"] = dict(weights_equal_replication=eq, recovery=b3[0].round(3).tolist(), recovery_ok=rec, pass_=eq and rec)
    ok &= eq and rec
    # P2
    a, s, prev, av = solve_params(0.30, 0.70, 0.5, seed)
    p2 = abs(prev - 0.30) <= 0.005 and abs(av - 0.70) <= 0.005
    res["P2"] = dict(a=a, s=s, prevalence=prev, auc=av, pass_=bool(p2))
    ok &= p2
    # P3
    r3 = run_point(seed, 10_001, 100, 0.70, 0.30, 6, 0.0, 0.0, 400)
    tv = r3["population"]
    truth_ok = abs(tv["cal_intercept"]) < 0.03 and abs(tv["cal_slope"] - 1) < 0.03  # 日の揺れが無ければ真は (0, 1)
    p3 = truth_ok and 0.92 <= r3["coverage_intercept"] <= 0.98 and 0.92 <= r3["coverage_slope"] <= 0.98
    res["P3"] = dict(result=r3, pass_=bool(p3))
    ok &= p3
    # P4
    r4b = run_point(seed, 10_002, 50, 0.70, 0.30, 6, 1.0, 0.6, 300)
    r4l = run_point(seed, 10_002, 50, 0.70, 0.30, 6, 1.0, 0.6, 300, mode="label")
    p4 = r4l["coverage_intercept"] <= r4b["coverage_intercept"] - 0.03
    res["P4"] = dict(block=r4b, label=r4l, pass_=bool(p4))
    ok &= p4
    res["mutate"] = MUTATE
    res["SELFTEST"] = "PASS" if ok else "FAIL"
    for k in ("P1", "P2", "P3", "P4"):
        v = res[k]
        extra = ""
        if k == "P3":
            extra = " cov_i %.3f cov_s %.3f" % (v["result"]["coverage_intercept"], v["result"]["coverage_slope"])
        if k == "P4":
            extra = " block cov_i %.3f label cov_i %.3f" % (v["block"]["coverage_intercept"], v["label"]["coverage_intercept"])
        print(k, v["pass_"], extra)
    print("SELFTEST", res["SELFTEST"])
    return ok, res


# ---------------------------------------------------------------- 本計算
def grid():
    pts = []
    for D in (20, 35, 50, 75, 100):
        for AUC in (0.60, 0.70, 0.80):
            for pi in (0.15, 0.30, 0.50):
                pts.append(dict(kind="main", D=D, AUC=AUC, pi=pi, lam=6, sd=0.5, rho=0.3, mode="block", Lmul=1))
    base = dict(kind="sens", D=50, AUC=0.70, pi=0.30, lam=6, sd=0.5, rho=0.3, mode="block", Lmul=1)
    for k, vs in (("sd", (0.0, 1.0)), ("rho", (0.0, 0.6)), ("lam", (3, 10))):
        for v in vs:
            pts.append({**base, k: v, "vary": k})
    pts.append({**base, "Lmul": 0, "vary": "L=1"})
    pts.append({**base, "Lmul": 2, "vary": "L=2x"})
    pts.append({**base, "mode": "label", "vary": "label"})
    return pts


def run(seed, out):
    t = time.time()
    rows = []
    for i, p in enumerate(grid()):
        if p["Lmul"] == 0:
            Lr = lambda m: 1  # noqa: E731
        elif p["Lmul"] == 2:
            Lr = lambda m: 2 * rule_main(m)  # noqa: E731
        else:
            Lr = rule_main
        r = run_point(seed, i, p["D"], p["AUC"], p["pi"], p["lam"], p["sd"], p["rho"], 200, mode=p["mode"], Lrule=Lr)
        r["kind"] = p["kind"]
        r["vary"] = p.get("vary")
        rows.append(r)
        print(i, p["kind"], p.get("vary"), p["D"], p["AUC"], p["pi"], "cov_i %.3f cov_s %.3f w_s %s" % (r["coverage_intercept"], r["coverage_slope"], r["width_slope_q"]), "%.0fs" % (time.time() - t), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(dict(note="合成の日の模擬。値は仮置きで段 1 の見込みではない。詰まりの推定ではない（conditions.md）。", B=B, rows=rows),
              open(os.path.join(out, "daysim.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--selftest":
        a = a[1:]
        tag = ""
        if a and a[0] == "--mutate":
            MUTATE = a[1]
            tag = "_" + a[1]
            a = a[2:]
        ok, res = selftest(int(a[0]))
        os.makedirs(a[1], exist_ok=True)
        json.dump(res, open(os.path.join(a[1], "selftest_daysim%s.json" % tag), "w"), ensure_ascii=False, indent=1, default=float)
        sys.exit(0 if ok else 1)
    run(int(a[0]), a[1])
