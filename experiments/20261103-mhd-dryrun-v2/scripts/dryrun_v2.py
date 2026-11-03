"""MhD の配管の空回し 第 2 版 (b) CoAuthor の版の直し（conditions.md の (b)）。第 1 版の dryrun.py を写して直した。

直したこと: 巡回するブロック・収束と分離と捨てた再標本の回数・陽性対照の書き出し・人ごとのセッション数の四分位・変異 2 つ。

使い方:
  python3 -I dryrun_v2.py --selftest <work_dir> <seed> <out_dir>                  陽性対照（selftest_coauthor.json に書く）
  python3 -I dryrun_v2.py --selftest --mutate m1|m2 <work_dir> <seed> <out_dir>   変異で C1 が赤になるか
  python3 -I dryrun_v2.py <work_dir> <seed> <out_dir>                             本計算（summary_coauthor.json）
出力は集計値だけ。書き手・セッションの番号を書かない。結果は詰まりの推定ではない（conditions.md「読まないこと」）。
"""
import glob
import json
import math
import os
import sys

import numpy as np

WIN_START, WIN_END = 31_000, 1_000  # 窓 [t-31s, t-1s)
LABEL_MS = 60_000
GAP_MS = 6 * 60_000
MAX_PROBES = 3
MIN_SESSIONS = 4
MUTATE = None  # None / "m1"（傾きで y と p̂ を取り違える）/ "m2"（切片のオフセットを外す）
SEP = 50.0


# ---------------------------------------------------------------- K1・K2 データ
def load(work):
    summ = json.load(open(os.path.join(work, "build_summary.json")))
    if not (summ.get("held_out_sessions") == 288 and summ.get("attempted") == 1157 and summ.get("status") == {"ok": 1157}):
        sys.exit("build_summary.json が条件と違う（K1）")
    s2w = json.load(open(os.path.join(work, "sessions.json")))
    by_w = {}
    for f in sorted(glob.glob(os.path.join(work, "s*.json"))):
        name = os.path.basename(f)
        if name in ("sessions.json",):
            continue
        sid = name[1:-5]
        if sid not in s2w:
            continue
        d = json.load(open(f))
        if len(d["observed_intervals"]) != 1:
            continue
        a, b = d["observed_intervals"][0]
        keys = np.array([k[0] for k in d["keys"]], dtype=np.int64)
        bs = np.array([k[0] for k in d["keys"] if k[1] == "backspace"], dtype=np.int64)
        feat = np.array([[r[0], r[1]] for r in d["feat"]], dtype=np.float64)
        ewma = np.array([r[2] for r in d["feat"]], dtype=np.float64)
        gets = np.array([e[0] for e in d["events"] if e[1] == "suggestion-get"], dtype=np.int64)
        by_w.setdefault(s2w[sid], []).append(dict(a=a, b=b, keys=np.sort(keys), bs=np.sort(bs), feat=feat, ewma=ewma, gets=np.sort(gets)))
    writers = []
    for w in sorted(by_w):
        ss = sorted(by_w[w], key=lambda s: s["a"])
        if len(ss) >= MIN_SESSIONS:
            writers.append(ss)
    return writers


# ---------------------------------------------------------------- K3 問いの時刻
def draw_probes(rng, a, b):
    allowed = [(a + 31_000, b - LABEL_MS)]
    allowed = [(x, y) for x, y in allowed if y > x]
    out = []
    while allowed and len(out) < MAX_PROBES:
        lens = np.array([y - x for x, y in allowed], dtype=np.float64)
        u = rng.uniform(0, lens.sum())
        i = int(np.searchsorted(np.cumsum(lens), u, side="right"))
        i = min(i, len(allowed) - 1)
        x, y = allowed[i]
        t = int(x + (u - (lens[:i].sum())))
        t = min(max(t, x), y)
        out.append(t)
        lo, hi = t - GAP_MS, t + GAP_MS
        nxt = []
        for x, y in allowed:
            if y <= lo or x >= hi:
                nxt.append((x, y))
            else:
                if x < lo:
                    nxt.append((x, lo))
                if y > hi:
                    nxt.append((hi, y))
        allowed = [(x, y) for x, y in nxt if y > x]
    return sorted(out)


# ---------------------------------------------------------------- K5 特徴
def last_le(times, vals, t):
    i = int(np.searchsorted(times, t, side="right")) - 1
    return vals[max(i, 0)]


def features(s, t):
    w0, w1 = t - WIN_START, t - WIN_END
    k = s["keys"][(s["keys"] >= w0) & (s["keys"] < w1)]
    nb = int(((s["bs"] >= w0) & (s["bs"] < w1)).sum())
    gap = float(np.diff(k).max()) / 1000.0 if len(k) >= 2 else 30.0
    ft = s["feat"][:, 0]
    ps = last_le(ft, s["feat"][:, 1], w1)
    ew = last_le(ft, s["ewma"], w1)
    edges = w0 + np.arange(31) * 1000
    kc = np.histogram(k, bins=edges)[0].astype(np.float64)
    bc = np.histogram(s["bs"][(s["bs"] >= w0) & (s["bs"] < w1)], bins=edges)[0].astype(np.float64)
    pser = np.array([last_le(ft, s["feat"][:, 1], e) for e in edges[1:]])
    return [float(len(k)), float(nb), gap, float(ps), float(ew)], np.stack([kc, bc, pser])


def build(writers, seed):
    rng = np.random.default_rng(seed)
    P = []  # 1 問 = dict
    for wi, ss in enumerate(writers):
        for si, s in enumerate(ss):
            for t in draw_probes(rng, s["a"], s["b"]):
                tab, ser = features(s, t)
                y = int(((s["gets"] > t) & (s["gets"] <= t + LABEL_MS)).any())
                P.append(dict(w=wi, s=si, tab=tab, ser=ser, y_real=y))
    return P


def add_syn(P, writers, seed):
    rng = np.random.default_rng(seed)
    z = np.array([p["tab"][0] for p in P])
    z = (z - z.mean()) / z.std()
    u = rng.normal(0, 0.5, len(writers))
    v = {(wi, si): rng.normal(0, 0.5) for wi, ss in enumerate(writers) for si in range(len(ss))}
    for p, zi in zip(P, z):
        eta = -0.5 + 1.0 * zi + u[p["w"]] + v[(p["w"], p["s"])]
        p["p_star"] = 1 / (1 + math.exp(-eta))
    ys = rng.random(len(P))
    for p, r in zip(P, ys):
        p["y_syn"] = int(r < p["p_star"])


def resyn(P, rng):
    return np.array([int(rng.random() < p["p_star"]) for p in P])


# ---------------------------------------------------------------- K6 モデル
def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -35, 35)))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def fit_logistic(X, y, lam=0.0, offset=None):
    return fit_logistic_c(X, y, lam, offset)[0]


def fit_logistic_c(X, y, lam=0.0, offset=None):
    """切片つき（X の前に 1 の列を足す）。切片は罰しない。Newton 法。戻り値 (beta, 収束したか)。"""
    n = len(y)
    Xd = np.hstack([np.ones((n, 1)), X]) if X is not None and X.size else np.ones((n, 1))
    off = np.zeros(n) if offset is None else offset
    beta = np.zeros(Xd.shape[1])
    R = np.eye(Xd.shape[1]) * lam
    R[0, 0] = 0.0
    conv = False
    for _ in range(100):
        p = sigmoid(Xd @ beta + off)
        g = Xd.T @ (y - p) - R @ beta
        H = (Xd * (p * (1 - p))[:, None]).T @ Xd + R
        step = np.linalg.solve(H + 1e-12 * np.eye(len(beta)), g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            conv = True
            break
    return beta, bool(conv and np.isfinite(beta).all())


def predict(beta, X):
    n = X.shape[0]
    return sigmoid(np.hstack([np.ones((n, 1)), X]) @ beta)


class Rocket:
    def __init__(self, seed, n_kernels=500, length=9, series_len=30, n_ch=3):
        rng = np.random.default_rng(seed)
        self.k = []
        for _ in range(n_kernels):
            w = rng.normal(0, 1, length)
            w -= w.mean()
            b = rng.uniform(-1, 1)
            d = int(2 ** rng.uniform(0, math.log2(series_len / (length - 1))))
            ch = int(rng.integers(n_ch))
            self.k.append((w, b, max(d, 1), ch))
        self.length = length

    def transform(self, S):  # S: (N, ch, T)
        N, _, T = S.shape
        out = np.empty((N, 2 * len(self.k)))
        for j, (w, b, d, ch) in enumerate(self.k):
            span = (self.length - 1) * d
            L = T - span
            idx = np.arange(L)[:, None] + np.arange(self.length)[None, :] * d
            conv = S[:, ch, :][:, idx] @ w + b  # (N, L)
            out[:, 2 * j] = (conv > 0).mean(axis=1)
            out[:, 2 * j + 1] = conv.max(axis=1)
        return out


def standardize(train, test):
    mu, sd = train.mean(axis=0), train.std(axis=0)
    sd[sd == 0] = 1.0
    return (train - mu) / sd, (test - mu) / sd


def fit_predict(model, tr, te, ytr, rocket):
    if model == "B0":
        return np.full(len(te), ytr.mean())
    if model == "B1":
        xtr = logit(np.array([[p["tab"][3]] for p in tr]))
        xte = logit(np.array([[p["tab"][3]] for p in te]))
        return predict(fit_logistic(xtr, ytr), xte)
    if model == "M1":
        a, b = standardize(np.array([p["tab"] for p in tr]), np.array([p["tab"] for p in te]))
        return predict(fit_logistic(a, ytr, lam=1.0), b)
    if model == "M2":
        a = rocket.transform(np.array([p["ser"] for p in tr]))
        b = rocket.transform(np.array([p["ser"] for p in te]))
        a, b = standardize(a, b)
        return predict(fit_logistic(a, ytr, lam=10.0), b)
    raise ValueError(model)


# ---------------------------------------------------------------- K8 量
def calib(y, p):
    return calib_c(y, p)[:2]


def calib_c(y, p):
    """戻り値 (切片, 傾き, 両方とも収束したか)。"""
    lp = logit(p)
    conv_s = True
    if np.var(lp) < 1e-12:
        slope = None
    elif MUTATE == "m1":  # 変異: 傾きの計算で y と p̂ を取り違える
        b, conv_s = fit_logistic_c(logit(np.asarray(y, float))[:, None], np.asarray(p, float))
        slope = float(b[1])
    else:
        b, conv_s = fit_logistic_c(lp[:, None], y)
        slope = float(b[1])
    if MUTATE == "m2":  # 変異: 切片の計算でオフセットを外す
        b, conv_i = fit_logistic_c(None, y)
    else:
        b, conv_i = fit_logistic_c(None, y, offset=lp)
    return float(b[0]), slope, bool(conv_s and conv_i)


def auc(y, p):
    y = np.asarray(y)
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    order = np.argsort(np.concatenate([pos, neg]), kind="mergesort")
    allv = np.concatenate([pos, neg])[order]
    ranks = np.empty(len(allv))
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1] == allv[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2 + 1
        i = j + 1
    r = np.empty(len(allv))
    r[order] = ranks
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def metrics(y, p, base):
    y = np.asarray(y, dtype=float)
    inter, slope, conv = calib_c(y, p)
    brier = float(np.mean((p - y) ** 2))
    b0 = float(np.mean((base - y) ** 2))
    return dict(cal_intercept=inter, cal_slope=slope, brier=brier, brier_minus_b0=brier - b0, base_rate=float(y.mean()), auc=auc(y, p), n=int(len(y)), converged=conv)


def boot_index(groups, rng):
    """groups: 書き手ごとの [セッションごとの問いの添字のリスト] を時間順に。書き手を復元抽出し、中では長さ 2 の巡回するブロック。"""
    out = []
    W = len(groups)
    for wi in rng.integers(0, W, W):
        ss = groups[wi]
        n = len(ss)
        if n == 1:
            out.extend(ss[0])
            continue
        picked = []
        while len(picked) < n:  # 巡回するブロック（長さ 2）: 最後のセッションの次は最初のセッション
            st = int(rng.integers(0, n))
            picked.extend([st, (st + 1) % n])
        for si in picked[:n]:
            out.extend(ss[si])
    return np.array(out, dtype=int)


def ci(y, p, base, groups, rng, B, keys=("cal_intercept", "cal_slope", "brier_minus_b0"), counts=None):
    """収束しなかった再標本は区間から除き、counts（dict）に回数を足す。"""
    vals = {k: [] for k in keys}
    y = np.asarray(y, dtype=float)
    c = dict(discarded_one_class=0, nonconverged=0, slope_abs_gt_50=0, used=0)
    for _ in range(B):
        idx = boot_index(groups, rng)
        if len(idx) == 0 or y[idx].min() == y[idx].max():
            c["discarded_one_class"] += 1
            continue
        m = metrics(y[idx], p[idx], base)
        if not m["converged"]:
            c["nonconverged"] += 1
            continue
        if m["cal_slope"] is not None and abs(m["cal_slope"]) > SEP:
            c["slope_abs_gt_50"] += 1
        c["used"] += 1
        for k in keys:
            if m[k] is not None:
                vals[k].append(m[k])
    if counts is not None:
        for k, v in c.items():
            counts[k] = counts.get(k, 0) + v
    return {k: ([float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 20 else None) for k, v in vals.items()}


def eval_groups(P, idx):
    """評価の側の問いの添字を、書き手 → セッション（時間順）に束ねる。添字は idx の中の位置。"""
    g = {}
    for pos, i in enumerate(idx):
        g.setdefault(P[i]["w"], {}).setdefault(P[i]["s"], []).append(pos)
    return [[g[w][s] for s in sorted(g[w])] for w in sorted(g)]


# ---------------------------------------------------------------- K7 分け方
def split_primary(P, writers):
    tr, te = [], []
    for i, p in enumerate(P):
        n = len(writers[p["w"]])
        (tr if p["s"] < math.ceil(0.6 * n) else te).append(i)
    return tr, te


def split_subject(P, writers, seed):
    rng = np.random.default_rng(seed)
    W = len(writers)
    test_w = set(rng.choice(W, size=round(0.3 * W), replace=False).tolist())
    tr = [i for i, p in enumerate(P) if p["w"] not in test_w]
    te = [i for i, p in enumerate(P) if p["w"] in test_w]
    return tr, te


def four_tuple(P, idx, writers):
    ws = sorted({P[i]["w"] for i in idx})
    per = [len({P[i]["s"] for i in idx if P[i]["w"] == w}) for w in ws]
    return dict(persons=len(ws), sessions_per_person_median=float(np.median(per)) if per else None,
                sessions_per_person_quartiles=[float(x) for x in np.percentile(per, [25, 50, 75])] if per else None,
                n_label=len(idx), n_ep="使わない（0）")


# ---------------------------------------------------------------- K9 陽性対照
def selftest(work, seed):
    ok = True
    res = dict(mutate=MUTATE)
    # C3
    rng = np.random.default_rng(1)
    X = rng.normal(size=(20000, 2))
    yy = (rng.random(20000) < sigmoid(-0.3 + X @ np.array([0.8, -1.2]))).astype(float)
    b = fit_logistic(X, yy)
    c3 = bool(np.all(np.abs(b - np.array([-0.3, 0.8, -1.2])) < 0.05))
    print("C3 logistic recovery", b.round(3).tolist(), c3)
    res["C3"] = dict(coef=b.round(4).tolist(), pass_=c3)
    ok &= c3
    # C4
    r1, r2 = Rocket(seed + 2), Rocket(seed + 2)
    S = np.random.default_rng(2).normal(size=(5, 3, 30))
    det = bool(np.array_equal(r1.transform(S), r2.transform(S)))
    const = r1.transform(np.ones((1, 3, 30)) * 3.0)[0, 0::2]
    c4 = det and bool(np.all((const == 0) | (const == 1)))
    print("C4 rocket deterministic/constant", det, c4)
    res["C4"] = dict(deterministic=det, pass_=c4)
    ok &= c4
    # C1・C2（合成のラベルだけ・L-real は計算しない）
    writers = load(work)
    P = build(writers, seed)
    add_syn(P, writers, seed + 1)
    tr, te = split_primary(P, writers)
    groups = eval_groups(P, te)
    pstar = np.array([P[i]["p_star"] for i in te])
    rng = np.random.default_rng(seed + 4)
    cov_s = cov_i = 0
    R = 200
    cnt = {}
    for _ in range(R):
        y = resyn([P[i] for i in te], rng)
        c = ci(y, pstar, y.mean(), groups, rng, 500, keys=("cal_intercept", "cal_slope"), counts=cnt)
        cov_s += c["cal_slope"] is not None and c["cal_slope"][0] <= 1 <= c["cal_slope"][1]
        cov_i += c["cal_intercept"] is not None and c["cal_intercept"][0] <= 0 <= c["cal_intercept"][1]
    c1 = cov_s / R >= 0.90 and cov_i / R >= 0.90
    print("C1 oracle coverage slope %.3f intercept %.3f" % (cov_s / R, cov_i / R), c1)
    res["C1"] = dict(R=R, B=500, coverage_slope=cov_s / R, coverage_intercept=cov_i / R, resample_counts=cnt,
                     v1_coverage_slope=0.995, v1_coverage_intercept=0.990, pass_=bool(c1))
    ok &= c1
    y = np.array([P[i]["y_syn"] for i in te])
    over = sigmoid(2 * logit(pstar))
    m = metrics(y, over, y.mean())
    cnt2 = {}
    c = ci(y, over, y.mean(), groups, rng, 500, keys=("cal_slope",), counts=cnt2)
    c2 = m["cal_slope"] is not None and 0.4 <= m["cal_slope"] <= 0.6 and c["cal_slope"] is not None and not (c["cal_slope"][0] <= 1 <= c["cal_slope"][1])
    print("C2 overconfident slope %.3f ci %s" % (m["cal_slope"], c["cal_slope"]), c2)
    res["C2"] = dict(slope=m["cal_slope"], ci=c["cal_slope"], resample_counts=cnt2, pass_=bool(c2))
    ok &= c2
    res["SELFTEST"] = "PASS" if ok else "FAIL"
    print("SELFTEST", res["SELFTEST"])
    return ok, res


# ---------------------------------------------------------------- 本計算
def run(work, seed, out):
    writers = load(work)
    P = build(writers, seed)
    add_syn(P, writers, seed + 1)
    rocket = Rocket(seed + 2)
    res = dict(note="代理のラベルでの配管の空回し（第 2 版）。詰まりの推定ではない。判定・検定をしない（conditions.md）。")
    res["data"] = dict(writers_used=len(writers), sessions_used=sum(len(s) for s in writers), probes=len(P),
                       probes_per_session=dict(zip(*np.unique([sum(1 for p in P if p["w"] == wi and p["s"] == si) for wi, ss in enumerate(writers) for si in range(len(ss))], return_counts=True))))
    res["data"]["probes_per_session"] = {str(int(k)): int(v) for k, v in res["data"]["probes_per_session"].items()}
    brng = np.random.default_rng(seed + 4)
    for lab in ("y_real", "y_syn"):
        Y = np.array([p[lab] for p in P], dtype=float)
        block = {}
        for name, (tr, te) in (("primary", split_primary(P, writers)), ("subject_holdout", split_subject(P, writers, seed + 3))):
            ytr, yte = Y[tr], Y[te]
            groups = eval_groups(P, te)
            sub = dict(train=four_tuple(P, tr, writers), eval=four_tuple(P, te, writers),
                       train_positives=int(ytr.sum()), eval_positives=int(yte.sum()), models={})
            for model in ("B0", "B1", "M1", "M2"):
                p = fit_predict(model, [P[i] for i in tr], [P[i] for i in te], ytr, rocket)
                m = metrics(yte, p, ytr.mean())
                cnt = {}
                m["ci95"] = ci(yte, p, ytr.mean(), groups, brng, 2000, counts=cnt)
                m["resample_counts"] = cnt
                sub["models"][model] = m
            block[name] = sub
        # 副 1: 伸ばしていく分割（点推定だけ）
        roll = {}
        for r in range(3, 10):
            tr = [i for i, p in enumerate(P) if p["s"] + 1 < r]
            te = [i for i, p in enumerate(P) if p["s"] + 1 == r]
            if not te or Y[tr].min() == Y[tr].max():
                continue
            roll[str(r)] = {model: metrics(Y[te], fit_predict(model, [P[i] for i in tr], [P[i] for i in te], Y[tr], rocket), Y[tr].mean())
                            for model in ("B0", "B1", "M1", "M2")}
            roll[str(r)]["n_eval"] = len(te)
        block["rolling_origin"] = roll
        # K10: 評価の側を書き手ごとに最初の d 本に絞った M1 の傾きの区間の幅
        tr, te = split_primary(P, writers)
        p_all = fit_predict("M1", [P[i] for i in tr], [P[i] for i in te], Y[tr], rocket)
        first = {}
        for pos, i in enumerate(te):
            first.setdefault(P[i]["w"], []).append((P[i]["s"], pos))
        k10 = {}
        for d in (1, 2, 4, None):
            keep = []
            for w, lst in first.items():
                ss = sorted({s for s, _ in lst})[: (d or 10 ** 9)]
                keep += [pos for s, pos in lst if s in ss]
            keep = np.array(sorted(keep))
            g = {}
            for k_, pos in enumerate(keep):
                i = te[pos]
                g.setdefault(P[i]["w"], {}).setdefault(P[i]["s"], []).append(k_)
            groups = [[g[w][s] for s in sorted(g[w])] for w in sorted(g)]
            cnt = {}
            c = ci(Y[te][keep], p_all[keep], Y[tr].mean(), groups, brng, 2000, keys=("cal_slope",), counts=cnt)["cal_slope"]
            k10["all" if d is None else str(d)] = dict(n_label=int(len(keep)), positives=int(Y[te][keep].sum()), slope_ci=c,
                                                      width=(c[1] - c[0]) if c else None, resample_counts=cnt)
        block["k10_width_by_sessions"] = k10
        res[lab] = block
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "summary_coauthor.json"), "w"), ensure_ascii=False, indent=1, default=float)
    print("written", os.path.join(out, "summary_coauthor.json"))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--selftest":
        a = a[1:]
        tag = ""
        if a and a[0] == "--mutate":
            MUTATE = a[1]
            tag = "_" + a[1]
            a = a[2:]
        ok, res = selftest(a[0], int(a[1]))
        os.makedirs(a[2], exist_ok=True)
        json.dump(res, open(os.path.join(a[2], "selftest_coauthor%s.json" % tag), "w"), ensure_ascii=False, indent=1, default=float)
        sys.exit(0 if ok else 1)
    run(a[0], int(a[1]), a[2])
