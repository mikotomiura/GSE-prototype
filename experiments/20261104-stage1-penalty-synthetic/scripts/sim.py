"""段 1 のロジスティックの罰の強さの決め方を合成で比べる（conditions.md C0〜C3）。

使い方: python3 -I -X utf8 sim.py SEED OUT JOBS [--set main,s1,s2] [--reps 400] [--mutate m1] [--run-id ID]
反復ごとの値を OUT/raw/<セル>.npz に書く（git に入れない）。集計と案の値は report.py。

変異（conditions C5・MUT に入る）:
  m1: 標準化に評価の側の件を混ぜる
  m2: 前向きの CV の日を並べ替えてからブロックに分ける
  m3: 切片も罰する
  m4: 評価の量（後悔・後知恵の最良を含む）を学習の側で数える
  m5: 1-SE で最も弱い罰を選ぶ・同点を弱い罰に切る
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

TAUS = [0.0, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, math.inf]  # 強い罰 → 弱い罰。0 = 切片だけ（B0-self）・inf = 罰なし
NT = len(TAUS)
P = 5
RHO = 0.3
BETA = np.array([0.8, -0.5, 0.3, 0.0, 0.0])
N_EVAL = 5000
NS = [10, 20, 30, 50, 80, 120]
RATES = [0.10, 0.25, 0.40]
SDS = [0.0, 0.5]
SIGNALS = [True, False]
N_CALIB = 200_000
TIE = 1e-9
MUT = set()

_SIG = np.full((P, P), RHO) + np.eye(P) * (1 - RHO)
CHOL = np.linalg.cholesky(_SIG)
# s2 の真の標準化（対数正規 exp(0.8 z) と 1[z > 1] の理論値）
_S = 0.8
LN_MU = math.exp(_S ** 2 / 2)
LN_SD = math.sqrt((math.exp(_S ** 2) - 1) * math.exp(_S ** 2))
BIN_P = 0.5 * math.erfc(1 / math.sqrt(2))
BIN_SD = math.sqrt(BIN_P * (1 - BIN_P))


# ---------- 当てはめ（logit.py の fit_logistic を写した・m3 だけ足した） ----------

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -35, 35)))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def fit_logistic(X, y, lam=0.0, offset=None, pseudo=True):
    """切片つき・切片は罰しない（m3 は罰する）・Newton 法（許容 1e-8・最大 100 回）。
    pseudo は特徴 0・オフセット 0 の y=1 と y=0 を重み 0.5 ずつ足す。返り値: (係数 [切片, β…], 収束したか)。"""
    X = np.zeros((len(y), 0)) if X is None else np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.ones(len(y))
    off = np.zeros(len(y)) if offset is None else np.asarray(offset, dtype=float)
    if pseudo:
        X = np.vstack([X, np.zeros((2, X.shape[1]))])
        y = np.concatenate([y, [1.0, 0.0]])
        w = np.concatenate([w, [0.5, 0.5]])
        off = np.concatenate([off, [0.0, 0.0]])
    Xd = np.hstack([np.ones((len(y), 1)), X])
    beta = np.zeros(Xd.shape[1])
    R = np.eye(Xd.shape[1]) * lam
    if "m3" not in MUT:
        R[0, 0] = 0.0
    conv = False
    for _ in range(100):
        p = sigmoid(Xd @ beta + off)
        g = Xd.T @ (w * (y - p)) - R @ beta
        Hs = (Xd * (w * p * (1 - p))[:, None]).T @ Xd + R
        step = np.linalg.solve(Hs + 1e-12 * np.eye(len(beta)), g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            conv = True
            break
    return beta, conv


def fit_tau(Z, y, tau):
    """τ で当てはめる。τ = 0 は切片だけ。返り値: (切片, β, 収束したか)。"""
    if tau == 0.0:
        th, conv = fit_logistic(None, y)
        return float(th[0]), np.zeros(Z.shape[1]), conv
    lam = 0.0 if math.isinf(tau) else 1.0 / tau ** 2
    th, conv = fit_logistic(Z, y, lam=lam)
    return float(th[0]), th[1:], conv


class Std:
    """標準化（平均・SD・SD が 0 なら 1）。"""

    def __init__(self, X):
        X = np.asarray(X, dtype=float)
        self.mu = X.mean(0)
        sd = X.std(0)
        sd[sd == 0] = 1.0
        self.sd = sd

    def __call__(self, X):
        return (np.asarray(X, dtype=float) - self.mu) / self.sd


def make_std(Xtr, Xev):
    """全件の当てはめの標準化。学習の側だけ（m1 は評価の側も混ぜる）。"""
    return Std(np.vstack([Xtr, Xev])) if "m1" in MUT else Std(Xtr)


def fold_std(Xtr, mt, mv):
    """CV の折の標準化。折の学習の件だけ（m1 は検証の件も混ぜる）。"""
    return Std(Xtr[mt | mv]) if "m1" in MUT else Std(Xtr[mt])


# ---------- 評価の量 ----------

def logloss_sum(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def auc(y, p):
    """順位による AUC（同点は平均の順位）。陽性か陰性が無ければ nan。"""
    y = np.asarray(y)
    npos = int(y.sum())
    nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return math.nan
    order = np.argsort(p, kind="mergesort")
    sp = np.asarray(p)[order]
    _, inv, cnt = np.unique(sp, return_inverse=True, return_counts=True)
    ends = np.cumsum(cnt)
    avg = (ends - cnt + 1 + ends) / 2.0
    r = np.empty(len(sp))
    r[order] = avg[inv]
    return float((r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def evaluate(y, p):
    """(対数損失の平均, Brier, C, 較正の切片, 較正の傾き, 傾きの当てはめが収束しなかったか 0/1)。
    p̂ の logit の SD < 1e-8 なら C と傾きは nan（収束の列は 0）。"""
    y = np.asarray(y, dtype=float)
    ll = logloss_sum(y, p) / len(y)
    br = float(np.mean((p - y) ** 2))
    lp = logit(p)
    th, _ = fit_logistic(None, y, offset=lp, pseudo=False)
    citl = float(th[0])
    if np.std(lp) < 1e-8:
        return ll, br, math.nan, citl, math.nan, 0.0
    th2, conv2 = fit_logistic(lp[:, None], y, pseudo=False)
    return ll, br, auc(y, p), citl, float(th2[1]), float(not conv2)


# ---------- 生成器 ----------

def features(z, kind):
    """(学習のモデルが見る x, 真の線形の部分に掛ける標準化した量)。"""
    if kind == "main":
        return z, z
    x = z.copy()
    x[:, 2] = np.exp(_S * z[:, 2])
    x[:, 3] = np.exp(_S * z[:, 3])
    x[:, 4] = (z[:, 4] > 1).astype(float)
    L = x.copy()
    L[:, 2:4] = (x[:, 2:4] - LN_MU) / LN_SD
    L[:, 4] = (x[:, 4] - BIN_P) / BIN_SD
    return x, L


def gen(rng, n, sigma_d, a, beta, kind, drift, day0=0, beta_day=None):
    """日の順に n 件。返り値: (x, y, day, p)。beta_day が与えられたら係数をその日の値に固定（s1 の評価の側）。"""
    m = rng.integers(1, 4, size=n)
    cum = np.cumsum(m)
    D = int(np.searchsorted(cum, n)) + 1
    counts = m[:D].copy()
    counts[-1] -= int(cum[D - 1] - n)
    day = np.repeat(np.arange(D), counts) + day0
    u = rng.standard_normal(D) * sigma_d
    z = rng.standard_normal((n, P)) @ CHOL.T
    x, L = features(z, kind)
    if drift:
        dd = day if beta_day is None else np.full(n, beta_day)
        fac = np.maximum(0.5, 1 - 0.5 * dd / 60.0)
        lin = (L * beta[None, :]).sum(1) * fac
    else:
        lin = L @ beta
    p = sigmoid(a + lin + u[day - day0])
    y = (rng.random(n) < p).astype(float)
    return x, y, day, p


def acells():
    """切片を合わせるセル（陽性の率・σ_d・信号・特徴の形）の一覧。番号は並びの位置。"""
    out = [(r, s, sig, "main") for r in RATES for s in SDS for sig in SIGNALS]
    out.append((0.25, 0.5, True, "s2"))
    return out


def calib_a(seed, aid, r, sd, sig, kind, n=N_CALIB, stream=99):
    rng = np.random.default_rng([seed, stream, aid])
    beta = BETA if sig else np.zeros(P)
    _, _, day, _ = gen(rng, n, 0.0, 0.0, beta, kind, False)  # 日の並びだけ使う
    D = int(day.max()) + 1
    u = rng.standard_normal(D) * sd
    z = rng.standard_normal((n, P)) @ CHOL.T
    _, L = features(z, kind)
    lin = L @ beta + u[day]
    lo, hi = -15.0, 15.0
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        if sigmoid(mid + lin).mean() < r:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------- 決め方 ----------

def pick_min(tot):
    """合計が最小の τ の番号。差 TIE 以内の同点は強い罰（前）。m5 は弱い罰（後）。"""
    tot = np.asarray(tot, dtype=float)
    ok = np.where(tot <= tot.min() + TIE)[0]
    return int(ok[-1] if "m5" in MUT else ok[0])


def pick_1se(F, main):
    """F[k, τ] は折 k の検証の対数損失の和。1-SE の範囲で最も強い罰（m5 は最も弱い罰）。"""
    K = F.shape[0]
    if K < 2:
        return main
    d = F - F[:, [main]]
    mean = d.mean(0)
    se = d.std(0, ddof=1) / math.sqrt(K)
    ok = np.where(mean <= se + 1e-12)[0]
    return int(ok[-1] if "m5" in MUT else ok[0])


def blocks_of(D, rng=None):
    """日の順の B = min(5, D) 個の連続するブロック（日の番号の配列のリスト）。m2 は日を並べ替える。"""
    days = np.arange(D)
    if "m2" in MUT and rng is not None:
        days = rng.permutation(days)
    return np.array_split(days, min(5, D))


def cv_matrix(Xtr, ytr, dtr, folds):
    """folds は (学習の日, 検証の日) の組のリスト。返り値: (F[k, τ], 収束しなかった数[τ])。"""
    F = np.zeros((len(folds), NT))
    nc = np.zeros(NT, dtype=int)
    for k, (tr_days, va_days) in enumerate(folds):
        mt = np.isin(dtr, tr_days)
        mv = np.isin(dtr, va_days)
        std = fold_std(Xtr, mt, mv)
        Zt, Zv = std(Xtr[mt]), std(Xtr[mv])
        for t, tau in enumerate(TAUS):
            b, be, conv = fit_tau(Zt, ytr[mt], tau)
            F[k, t] = logloss_sum(ytr[mv], sigmoid(b + Zv @ be))
            nc[t] += not conv
    return F, nc


def fwd_folds(D, rng=None):
    bl = blocks_of(D, rng)
    return [(np.concatenate(bl[:k]), bl[k]) for k in range(1, len(bl))]


def loo_folds(D):
    bl = np.array_split(np.arange(D), min(5, D))
    return [(np.concatenate([bl[j] for j in range(len(bl)) if j != k]), bl[k]) for k in range(len(bl))]


# ---------- 1 反復 ----------

def one_rep(cell, rep, seed):
    rng = np.random.default_rng(np.random.SeedSequence([seed, cell["id"], rep]))
    beta = BETA if cell["signal"] else np.zeros(P)
    drift = cell["set"] == "s1"
    Xtr, ytr, dtr, ptr = gen(rng, cell["n"], cell["sd"], cell["a"], beta, cell["kind"], drift)
    D = int(dtr.max()) + 1
    Xev, yev, dev, pev = gen(rng, N_EVAL, cell["sd"], cell["a"], beta, cell["kind"], drift, day0=D,
                             beta_day=D if drift else None)
    if "m4" in MUT:
        Xev, yev, pev = Xtr, ytr, ptr
    std = make_std(Xtr, Xev)
    Ztr, Zev = std(Xtr), std(Xev)
    met = np.full((NT, 6), np.nan)
    nc_full = np.zeros(NT, dtype=int)
    for t, tau in enumerate(TAUS):
        b, be, conv = fit_tau(Ztr, ytr, tau)
        nc_full[t] = not conv
        met[t] = evaluate(yev, sigmoid(b + Zev @ be))
    oracle = logloss_sum(yev, pev) / len(yev)
    cv_ok = D >= 2
    if cv_ok:
        Ff, nc_f = cv_matrix(Xtr, ytr, dtr, fwd_folds(D, rng))
        Fl, nc_l = cv_matrix(Xtr, ytr, dtr, loo_folds(D))
        c_fwd = pick_min(Ff.sum(0))
        c_1se = pick_1se(Ff, c_fwd)
        c_loo = pick_min(Fl.sum(0))
        nb = len(Ff) + 1
    else:
        nc_f = nc_l = np.zeros(NT, dtype=int)
        c_fwd = c_1se = c_loo = 0
        nb = 1
    npos = int(ytr.sum())
    return dict(met=met, oracle=oracle, c_fwd=c_fwd, c_1se=c_1se, c_loo=c_loo, cv_ok=int(cv_ok), nblocks=nb,
                D=D, npos=npos, nneg=int(len(ytr) - npos), nc_full=nc_full, nc_fwd=nc_f, nc_loo=nc_l)


def _job(args):
    cell, rep, seed, mut = args
    MUT.clear()
    MUT.update(mut)
    return one_rep(cell, rep, seed)


def cells(seed, sets):
    """セルの一覧（id は乱数の流れの番号: 主 0〜71・s1 100+・s2 200+・cons 300）。"""
    al = acells()
    a_of = {c: calib_a(seed, i, *c) for i, c in enumerate(al)}
    out = []
    if "main" in sets:
        i = 0
        for n in NS:
            for r in RATES:
                for sd in SDS:
                    for sig in SIGNALS:
                        out.append(dict(id=i, set="main", n=n, rate=r, sd=sd, signal=sig, kind="main",
                                        a=a_of[(r, sd, sig, "main")]))
                        i += 1
    for sname, base, kind in (("s1", 100, "main"), ("s2", 200, "s2")):
        if sname in sets:
            for j, n in enumerate(NS):
                out.append(dict(id=base + j, set=sname, n=n, rate=0.25, sd=0.5, signal=True, kind=kind,
                                a=a_of[(0.25, 0.5, True, kind)]))
    if "cons" in sets:
        out.append(dict(id=300, set="cons", n=2000, rate=0.25, sd=0.0, signal=True, kind="main",
                        a=a_of[(0.25, 0.0, True, "main")]))
    return out


def stack(res):
    keys = res[0].keys()
    return {k: np.array([r[k] for r in res]) for k in keys}


def run_cells(seed, cl, reps, jobs, mut=()):
    out = {}
    with Pool(jobs) as pool:
        for c in cl:
            nrep = reps if c["set"] != "cons" else min(reps, 100)
            res = pool.map(_job, [(c, r, seed, tuple(mut)) for r in range(nrep)], chunksize=8)
            out[c["id"]] = (c, stack(res))
    return out


def main(argv):
    seed, out, jobs = int(argv[0]), argv[1], int(argv[2])
    opt = dict(zip(argv[3::2], argv[4::2]))
    sets = opt.get("--set", "main,s1,s2,cons").split(",")
    reps = int(opt.get("--reps", 400))
    mut = [m for m in opt.get("--mutate", "").split(",") if m]
    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    cl = cells(seed, sets)
    res = run_cells(seed, cl, reps, jobs, mut)
    index = []
    for cid, (c, arr) in res.items():
        np.savez_compressed(os.path.join(raw, f"cell{cid:03d}.npz"), **arr)
        index.append(c)
    with open(os.path.join(raw, "cells.json"), "w") as f:
        json.dump(dict(seed=seed, reps=reps, mutate=mut, run_id=opt.get("--run-id"), taus=[str(t) for t in TAUS],
                       cells=index), f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
