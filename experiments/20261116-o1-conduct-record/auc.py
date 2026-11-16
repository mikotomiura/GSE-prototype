"""R5 探索の AUC（人ごと・判定しない）。usage: auc.py <work_dir> <seed> <out_json> | --selftest

停滞の u（t0 以前で最後の文字の入力）と、短い休止の u′（対照）を、打鍵の 18 量（K）と、K に打鍵以外の量（N）を
足したもので見分ける。学習器はロジスティック回帰（numpy・論文 1 と同じ設定）。人の中で日（名前の日付）を単位に 5 分割。
"""
import bisect
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_common as cm  # noqa: E402
import conduct  # noqa: E402

TEXT = {"alphabetic", "numeric", "punctuation", "sentence_punctuation", "space", "enter", "tab"}
BOUNDARY = {"space", "enter", "sentence_punctuation"}
STALL_GAP, CTRL_LO, CTRL_HI, CTRL_LO_EARLY = 30_000, 2_000, 30_000, 5_000
WARM, D_WIN, EARLY = 60_000, 30_000, 5_000
N_MATCHED, MIN_STALLS, MIN_DAYS, FOLDS, NBOOT = 5, 30, 5, 5, 200
SINCE_CAP_S = 600
C_L2, TOL, MAX_IT = 1.0, 1e-8, 100


# ---------- 1 本の時刻の並び ----------

class F:
    def __init__(self, name, d, x, pointer_ok, date=None):
        self.name = name
        self.date = date if date is not None else name  # 分割の単位（名前の日付）
        self.iv = sorted((iv["a_ms"], iv["b_ms"]) for iv in d["observed_intervals"])
        ks = sorted(d["keys"], key=lambda k: k[0])
        self.press = [(t, c) for t, c in ks if c in TEXT or c == "backspace"]
        self.pt = [t for t, _ in self.press]
        self.text = [(t, c) for t, c in ks if c in TEXT]
        self.tt = [t for t, _ in self.text]
        self.onsets = [tuple(o) for o in d["onsets"]]
        self.feat = [r for r in x["feat"]]
        self.ft = [r[0] for r in self.feat]
        self.focus = sorted(d["focus"])
        self.paste = sorted(p[0] for p in d["paste"])
        self.ime = [r for r in x["ime_state"]]
        self.imet = [r[0] for r in self.ime]
        self.shadow = sorted(x["ime_shadow"])
        self.ptr = sorted(d["pointer"]) if pointer_ok else None
        self.ptrt = [p[0] for p in self.ptr] if pointer_ok else None

    def interval_of(self, t):
        i = bisect.bisect_right([a for a, _ in self.iv], t) - 1
        return self.iv[i] if i >= 0 and self.iv[i][0] <= t <= self.iv[i][1] else None

    def gap_after(self, i):
        """文字の入力 i の後の最初の文字の入力までの時間と、それが同じ観測区間にあるか。"""
        t = self.tt[i]
        iv = self.interval_of(t)
        nxt = self.tt[i + 1] if i + 1 < len(self.tt) else None
        if nxt is not None and iv is not None and nxt <= iv[1]:
            return nxt - t, True
        return (iv[1] - t) if iv else 0, False

    def has_feat_before(self, t):
        return bisect.bisect_right(self.ft, t - D_WIN) > 0

    def feat_at(self, t):
        i = bisect.bisect_right(self.ft, t) - 1
        return self.feat[i] if i >= 0 else None


def count(ts, a, b):
    """(a, b] の数。"""
    return bisect.bisect_right(ts, b) - bisect.bisect_right(ts, a)


# ---------- R5.1 停滞と対照 ----------

def stalls_and_candidates(f, ctrl_lo):
    ex = {"excl_no_interval": 0, "excl_u_ge_s": 0, "excl_short_gap": 0, "excl_early": 0, "excl_no_feat": 0,
          "excl_dup_u": 0}
    stalls, seen_u = [], set()
    for s, t0 in f.onsets:
        iv = f.interval_of(t0)
        j = bisect.bisect_right(f.tt, t0) - 1
        if iv is None or j < 0 or f.tt[j] < iv[0]:
            ex["excl_no_interval"] += 1
            continue
        u = f.tt[j]
        if u >= s:
            ex["excl_u_ge_s"] += 1
            continue
        g, _ = f.gap_after(j)
        if g < STALL_GAP:
            ex["excl_short_gap"] += 1
            continue
        if u < iv[0] + WARM:
            ex["excl_early"] += 1
            continue
        if not f.has_feat_before(u):
            ex["excl_no_feat"] += 1
            continue
        if u in seen_u:  # 1 つの沈黙に始まりが 2 つあると同じ u になる。最初の 1 件だけを使う
            ex["excl_dup_u"] += 1
            continue
        seen_u.add(u)
        stalls.append((u, f.text[j][1] in BOUNDARY, s, t0))
    cands = []
    for i, (u, c) in enumerate(f.text):
        g, inside = f.gap_after(i)
        if not inside or not (ctrl_lo <= g < CTRL_HI):
            continue
        iv = f.interval_of(u)
        if iv is None or u < iv[0] + WARM or not f.has_feat_before(u):
            continue
        if any(s - D_WIN <= u <= t0 for s, t0 in f.onsets):
            continue
        cands.append((u, c in BOUNDARY))
    return stalls, cands, ex


def match(files, ctrl_lo, seed):
    """戻り値: 停滞の行 [(本の番号, u)]・対照の行 [(本の番号, u)]・対 [(停滞の行番号, 対照の行番号)]・除外の数。"""
    rng = random.Random(seed)
    srows, crows, pairs = [], [], []
    cidx = {}
    ex = {"excl_no_control": 0}
    for fi, f in enumerate(files):
        st, ca, e = stalls_and_candidates(f, ctrl_lo)
        for k, v in e.items():
            ex[k] = ex.get(k, 0) + v
        for u, b, _, _ in sorted(st):
            pool = [c for c in ca if c[1] == b]
            if not pool:
                ex["excl_no_control"] += 1
                continue
            pick = rng.sample(pool, min(N_MATCHED, len(pool)))
            si = len(srows)
            srows.append((fi, u))
            for cu, _ in sorted(pick):
                key = (fi, cu)
                if key not in cidx:
                    cidx[key] = len(crows)
                    crows.append(key)
                pairs.append((si, cidx[key]))
    return srows, crows, pairs, ex


# ---------- R5.2 量 ----------

def nearest_rank(xs, q):
    s = sorted(xs)
    return s[min(max(math.ceil(q * len(s)), 1), len(s)) - 1]


def k9(f, a, b):
    """(a, b] の打鍵の 9 量（論文 1）。定義できないものは nan。"""
    lo, hi = bisect.bisect_right(f.pt, a), bisect.bisect_right(f.pt, b)
    pr = f.press[lo:hi]
    ts = [t for t, _ in pr]
    n = len(ts)
    gaps = [y - x for x, y in zip(ts, ts[1:])]
    g50 = [g for g in gaps if g > 50]
    nan = float("nan")
    pcts = [nearest_rank(g50, q) for q in (0.1, 0.5, 0.9)] if g50 else [nan] * 3
    ge2 = sum(1 for g in gaps if g >= 2000) if n >= 2 else nan
    ge10 = sum(1 for g in gaps if g >= 10000) if n >= 2 else nan
    bs = sum(1 for _, c in pr if c == "backspace") / n if n else nan
    if n:
        bursts, cur = [], 1
        for g in gaps:
            if g >= 2000:
                bursts.append(cur)
                cur = 1
            else:
                cur += 1
        bursts.append(cur)
        burst = sum(bursts) / len(bursts)
    else:
        burst = nan
    chars = sum(1 for _, c in pr if c != "backspace") * 60_000 / (b - a)
    return [float(n), *map(float, pcts), float(ge2), float(ge10), float(bs), float(burst), float(chars)]


def feat_k(f, u):
    w1 = k9(f, u - D_WIN, u)
    w0 = k9(f, u - 2 * D_WIN, u - D_WIN)
    return w1 + [x - y for x, y in zip(w1, w0)]


def n_counts(f, a, b):
    xs = [count(f.focus, a, b), count(f.paste, a, b), count(f.imet, a, b), count(f.shadow, a, b)]
    if f.ptr is not None:
        lo, hi = bisect.bisect_right(f.ptrt, a), bisect.bisect_right(f.ptrt, b)
        seg = f.ptr[lo:hi]
        xs += [sum(p[1] for p in seg), sum(1 for p in seg if p[2] > 0), sum(1 for p in seg if p[3] > 0)]
    return [float(x) for x in xs]


def feat_n(f, u, early):
    w1 = n_counts(f, u - D_WIN, u)
    w0 = n_counts(f, u - 2 * D_WIN, u - D_WIN)
    i = bisect.bisect_right(f.focus, u) - 1
    since = min((u - f.focus[i]) / 1000, SINCE_CAP_S) if i >= 0 else float("nan")
    j = bisect.bisect_right(f.imet, u) - 1
    on, act = (float(f.ime[j][1]), float(f.ime[j][2])) if j >= 0 else (float("nan"), float("nan"))
    out = w1 + [x - y for x, y in zip(w1, w0)] + [since, on, act]
    if early:
        out += n_counts(f, u, u + EARLY)
    return out


def signals(f, u):
    a, b = f.feat_at(u), f.feat_at(u - D_WIN)
    return [a[1] - b[1], a[2] - b[2]]


# ---------- R5.3 学習器と評価 ----------

def prep(Xtr, Xte):
    """学習の折りで: 欠けのある列は中央値で埋めて印の列を足し、標準化（SD 0 は 1）。"""
    miss = np.isnan(Xtr).any(axis=0)
    med = np.array([np.nanmedian(Xtr[:, j]) if (~np.isnan(Xtr[:, j])).any() else 0.0 for j in range(Xtr.shape[1])])

    def fill(X):
        M = np.isnan(X)
        Y = np.where(M, med, X)
        return np.hstack([Y, M[:, miss].astype(float)])
    A, Bm = fill(Xtr), fill(Xte)
    mu, sd = A.mean(axis=0), A.std(axis=0)
    sd[sd == 0] = 1.0
    return (A - mu) / sd, (Bm - mu) / sd


def fit_logistic(X, y):
    """目的: 対数損失の和 + ‖w‖² / (2C)（切片は罰さない）。Newton 法。収束しなければ None。"""
    n, p = X.shape
    Z = np.hstack([np.ones((n, 1)), X])
    w = np.zeros(p + 1)
    pen = np.full(p + 1, 1.0 / C_L2)
    pen[0] = 0.0
    for _ in range(MAX_IT):
        eta = np.clip(Z @ w, -35, 35)
        mu = 1 / (1 + np.exp(-eta))
        g = Z.T @ (mu - y) + pen * w
        Hs = (Z * (mu * (1 - mu))[:, None]).T @ Z + np.diag(pen) + 1e-12 * np.eye(p + 1)
        step = np.linalg.solve(Hs, g)
        w -= step
        if np.max(np.abs(step)) < TOL:
            return w
    return None


def matched_auc(score_s, score_c, pairs):
    if not pairs:
        return None
    v = 0.0
    for si, ci in pairs:
        a, b = score_s[si], score_c[ci]
        v += 1.0 if a > b else 0.5 if a == b else 0.0
    return v / len(pairs)


def fold_of(units, rng):
    """日（元の単位）を 5 つに分ける。復元抽出の写しも元の日と同じ折りに入る（学習と評価が交わらない）。"""
    order = sorted(set(units))
    rng.shuffle(order)
    return {u: i % FOLDS for i, u in enumerate(order)}


def cv_scores(Xs, Xc, s_unit, c_unit, rng):
    """日の単位で 5 分割して予測値を返す。失敗（学習に片方の類が無い・収束しない）なら None。"""
    fold = fold_of([*s_unit, *c_unit], rng)
    fs = [fold[u] for u in s_unit]
    fc = [fold[u] for u in c_unit]
    ps, pc = np.full(len(Xs), np.nan), np.full(len(Xc), np.nan)
    for k in range(FOLDS):
        trs = [i for i, f in enumerate(fs) if f != k]
        trc = [i for i, f in enumerate(fc) if f != k]
        tes = [i for i, f in enumerate(fs) if f == k]
        tec = [i for i, f in enumerate(fc) if f == k]
        if not tes and not tec:
            continue
        if not trs or not trc:
            return None
        Xtr = np.vstack([Xs[trs], Xc[trc]])
        y = np.r_[np.ones(len(trs)), np.zeros(len(trc))]
        Xte = np.vstack([Xs[tes], Xc[tec]])
        A, Bm = prep(Xtr, Xte)
        w = fit_logistic(A, y)
        if w is None:
            return None
        pr = np.hstack([np.ones((len(Bm), 1)), Bm]) @ w
        ps[tes] = pr[:len(tes)]
        pc[tec] = pr[len(tes):]
    return ps, pc


def resample(draw, by_unit_s, by_unit_c, pairs):
    """引いた日の並び draw から行と対を作る。写しの行も元の日の名前を単位に持つ（同じ折りに入る）。"""
    srcs, crcs, sunit, cunit, prs = [], [], [], [], []
    for u in draw:
        smap, cmap = {}, {}
        for i in by_unit_s[u]:
            smap[i] = len(srcs)
            srcs.append(i)
            sunit.append(u)
        for i in by_unit_c[u]:
            cmap[i] = len(crcs)
            crcs.append(i)
            cunit.append(u)
        prs += [(smap[a], cmap[b]) for a, b in pairs if a in smap and b in cmap]
    return srcs, crcs, sunit, cunit, prs


def evaluate(files, srows, crows, pairs, early, seed):
    """K と K+N の AUC・ΔAUC・推定器の信号の AUC・日の復元抽出の区間。"""
    XK_s = np.array([feat_k(files[fi], u) for fi, u in srows])
    XK_c = np.array([feat_k(files[fi], u) for fi, u in crows])
    XN_s = np.array([feat_n(files[fi], u, early) for fi, u in srows])
    XN_c = np.array([feat_n(files[fi], u, early) for fi, u in crows])
    XKN_s, XKN_c = np.hstack([XK_s, XN_s]), np.hstack([XK_c, XN_c])
    s_unit = [files[fi].date for fi, _ in srows]
    c_unit = [files[fi].date for fi, _ in crows]
    units = sorted({*s_unit, *c_unit})
    sig_s = [signals(files[fi], u) for fi, u in srows]
    sig_c = [signals(files[fi], u) for fi, u in crows]

    def one(sunit, cunit, srcs, crcs, prs, rng):
        out = {}
        for name, (A, Bm) in (("K", (XK_s, XK_c)), ("KN", (XKN_s, XKN_c))):
            r = cv_scores(A[srcs], Bm[crcs], sunit, cunit, random.Random(rng))
            if r is None:
                return None
            out[name] = matched_auc(r[0], r[1], prs)
        out["delta"] = out["KN"] - out["K"]
        return out

    main = one(s_unit, c_unit, list(range(len(srows))), list(range(len(crows))), pairs, seed)
    res = {"stalls_used": len(srows), "controls_used": len(crows), "pairs": len(pairs),
           "files_with_stalls": len({fi for fi, _ in srows}), "days_with_stalls": len(set(s_unit)), "n_features": {"K": XK_s.shape[1], "KN": XKN_s.shape[1]}}
    if main is None:
        res["status"] = "学習に失敗"
        return res
    res.update({"auc_K": round(main["K"], 4), "auc_KN": round(main["KN"], 4), "delta_auc": round(main["delta"], 4),
                "signal_auc": {nm: round(matched_auc([s[i] for s in sig_s], [c[i] for c in sig_c], pairs), 4)
                               for i, nm in enumerate(("d_p_stuck", "d_ewma_x"))}})
    # 区間: 日を復元抽出して学び直す。写しは元の日の番号を持つので、同じ折りに入る（学習と評価が交わらない）
    rng = random.Random(seed + 1)
    by_unit_s = {u: [i for i, x in enumerate(s_unit) if x == u] for u in units}
    by_unit_c = {u: [i for i, x in enumerate(c_unit) if x == u] for u in units}
    boots, fails = {"K": [], "KN": [], "delta": []}, 0
    for _ in range(NBOOT):
        draw = [units[rng.randrange(len(units))] for _ in units]
        srcs, crcs, sunit, cunit, prs = resample(draw, by_unit_s, by_unit_c, pairs)
        r = one(sunit, cunit, srcs, crcs, prs, rng.randrange(1 << 30)) if prs else None
        if r is None:
            fails += 1
            continue
        for k in boots:
            boots[k].append(r[k])

    res.update({"ci95": {"K": cm.ci95(boots["K"]), "KN": cm.ci95(boots["KN"]), "delta": cm.ci95(boots["delta"])},
                "boot_failures": fails})
    return res


def person(rows, seed, label):
    pok = conduct.pointer_usable(rows)
    files = [F(f["inter"], d, x, pok, f["date"]) for f, d, x in sorted(rows, key=lambda r: r[0]["inter"])
             if d["focus"] and cm.obs_ms(d) > 0]
    res = {"files_used": len(files), "pointer_usable": pok}
    for name, early, lo in (("main", False, CTRL_LO), ("early_5s", True, CTRL_LO_EARLY)):
        srows, crows, pairs, ex = match(files, lo, f"{seed}-{label}-{name}")
        r = {"stalls_onsets": sum(len(f.onsets) for f in files), **ex}
        nd = len({files[fi].date for fi, _ in srows})
        if len(srows) < MIN_STALLS or nd < MIN_DAYS:
            r.update({"status": "数が足りない", "stalls_used": len(srows), "days_with_stalls": nd})
        else:
            r.update(evaluate(files, srows, crows, pairs, early, seed))
        res[name] = r
    return res


def run(work, seed, out):
    seed = int(seed)
    table, people = cm.load_people(work)
    res = {"people": {k: person(v, seed, k) for k, v in sorted(people.items())}}
    cm.write_public(res, work, "auc", out, table)


# ---------- R8 陽性対照 ----------

def synth_file(rng, n_stall, focus_in_stall_w1, stall_slow, nfile, focus_early=False, raw=False):
    """合成の 1 本。2 時間の観測区間。打鍵は 300 ms ごとに打ち、停滞（45 秒の止まり）と短い休止（3〜20 秒）を挟む。"""
    t, keys, onsets, focus = 100_000.0, [], [], []
    end = 2 * cm.H
    feat = [[x, 0.1, 0.0] for x in range(0, int(end), 1000)]
    i = 0
    while t < end - 200_000:
        burst = rng.randint(30, 60)
        for _ in range(burst):
            keys.append([int(t), "alphabetic" if rng.random() > 0.05 else "backspace"])
            t += 300 + rng.uniform(-50, 50)
        keys.append([int(t), "alphabetic"])
        if i % 4 == 0 and len(onsets) < n_stall:
            if stall_slow:  # 停滞の手前の 30 秒の押下を間引く
                cut = int(t) - 30_000
                keys = [k for k in keys if not (cut < k[0] < int(t)) or rng.random() < 0.3]
            u = int(t)
            if focus_in_stall_w1:
                focus.append(u - 5_000)
            if focus_early:
                focus.append(u + 2_000)
            onsets.append([u + 1_000, u + 31_000])
            t += 45_000
        else:
            t += rng.uniform(3_000, 20_000)
        i += 1
    focus += [int(rng.uniform(0, end)) for _ in range(30)]  # 背景の遷移は構造と無関係に一様に置く
    keys.sort()
    d = {"observed_intervals": [{"a_ms": 0, "b_ms": end}], "keys": keys, "onsets": onsets,
         "focus": sorted(focus) or [1], "paste": [], "pointer": []}
    x = {"feat": feat, "ime_state": [], "ime_shadow": []}
    if raw:
        return d, x
    return F(f"f{nfile:02d}", d, x, False)


def selftest():
    # (a) 対の AUC
    assert matched_auc([3, 1], [2, 1, 0], [(0, 0), (0, 1), (1, 1), (1, 2)]) == (1 + 1 + 0.5 + 1) / 4
    # (b) 打鍵の 9 量
    d = {"observed_intervals": [{"a_ms": 0, "b_ms": 100_000}], "keys": [[1000, "alphabetic"], [1040, "alphabetic"],
         [3500, "backspace"], [16000, "space"], [16100, "navigation"]], "onsets": [], "focus": [], "paste": [], "pointer": []}
    f = F("x", d, {"feat": [], "ime_state": [], "ime_shadow": []}, False)
    k = k9(f, 0, 30_000)
    # 押下 4（navigation は数えない）・間隔 40, 2460, 12500 → 50 超は 2460, 12500
    assert k[0] == 4 and k[1] == 2460 and k[2] == 2460 and k[3] == 12500, k
    assert k[4] == 2 and k[5] == 1 and k[6] == 0.25, k
    assert abs(k[7] - 4 / 3) < 1e-9 and k[8] == 3 * 2, k  # まとまり [2, 1, 1]・文字 3 × 2 / 分
    e = k9(f, 50_000, 80_000)
    assert e[0] == 0 and all(math.isnan(v) for v in e[1:8]) and e[8] == 0, e
    # (f) 選び方
    d2 = {"observed_intervals": [{"a_ms": 0, "b_ms": 1_000_000}],
          "keys": [[30_000, "alphabetic"], [100_000, "alphabetic"], [140_000, "space"], [143_000, "alphabetic"],
                   [200_000, "alphabetic"], [205_000, "alphabetic"], [280_000, "alphabetic"], [283_000, "alphabetic"],
                   [300_000, "alphabetic"], [400_000, "alphabetic"]],
          "onsets": [[101_000, 130_000], [102_000, 135_000], [299_000, 330_000], [31_000, 60_000]], "focus": [1],
          "paste": [], "pointer": []}
    f2 = F("y", d2, {"feat": [[0, 0.1, 0]], "ime_state": [], "ime_shadow": []}, False)
    st, ca, ex = stalls_and_candidates(f2, CTRL_LO)
    assert [s[0] for s in st] == [100_000], (st, ex)  # 300_000 は u ≥ s、30_000 は始まりから 60 秒未満
    assert ex["excl_u_ge_s"] == 1 and ex["excl_early"] == 1 and ex["excl_dup_u"] == 1, ex  # 2 件目は同じ u
    # 140_000: G 3 秒・区切り。200_000: G 5 秒。280_000・283_000 は停滞の窓 [269_000, 330_000] の中で外れる
    assert ca == [(140_000, True), (200_000, False)], ca
    _, ca2, _ = stalls_and_candidates(f2, CTRL_LO_EARLY)
    assert ca2 == [(200_000, False)], ca2  # 副は G ≥ 5 秒
    # 区切りの種類を揃える: 停滞 u = 100_000（区切りでない）の対照は 200_000 だけ
    srows, crows, pairs, _ = match([f2], CTRL_LO, 1)
    assert srows == [(0, 100_000)] and crows == [(0, 200_000)] and pairs == [(0, 0)], (srows, crows, pairs)
    # K の前半 9 個は W1 = (u − 30 秒, u]、後半は W1 − W0
    kk = feat_k(f, 30_000)
    w1 = k9(f, 0, 30_000)  # 押下 4・量はすべて定義される（上の (b)）
    assert kk[:9] == w1 and kk[0] == 4.0, kk
    assert kk[9] == 4.0 and kk[17] == w1[8], kk  # W0 = (−30 秒, 0] は押下 0
    # (c)(d)(e) 合成の人
    def person_files(rng, focus, slow):
        return [synth_file(rng, 12, focus, slow, i) for i in range(8)]
    # 写しは元の日と同じ折り: 同じ日を重ねて引いても、ある折りの学習と評価に同じ日が入らない
    fold = fold_of(["d1", "d1", "d2", "d3", "d3", "d3", "d4", "d5", "d6"], random.Random(2))
    assert len(fold) == 6 and set(fold.values()) <= set(range(FOLDS)), fold
    su = ["d1", "d1", "d3", "d3", "d6"]
    cu = ["d1", "d3", "d6", "d6"]
    fs, fc = [fold[u] for u in su], [fold[u] for u in cu]
    for k in range(FOLDS):
        tr = {u for u, f in zip(su + cu, fs + fc) if f != k}
        te = {u for u, f in zip(su + cu, fs + fc) if f == k}
        assert not tr & te, (k, tr, te)
    # 復元抽出: 同じ日を 2 回引くと、行も対も 2 倍になり、写しの単位は元の日の名前のまま
    srcs, crcs, sunit, cunit, prs = resample(["d1", "d1", "d2"], {"d1": [0], "d2": [1]}, {"d1": [0, 1], "d2": [2]},
                                             [(0, 0), (0, 1), (1, 2)])
    assert srcs == [0, 0, 1] and crcs == [0, 1, 0, 1, 2] and sunit == ["d1", "d1", "d2"], (srcs, crcs, sunit)
    assert cunit == ["d1", "d1", "d1", "d1", "d2"] and prs == [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4)], (cunit, prs)
    # 行で分けると漏れる: 日の中の行が同じ値の写しなら、日で分けると当てられず、行で分けると当たる
    rs = np.random.default_rng(4)
    Xs, Xc, su, cu, prs = [], [], [], [], []
    for d in range(40):
        vs, vc = rs.normal(size=30), rs.normal(size=30)
        for _ in range(3):
            Xs.append(vs)
            su.append(f"d{d}")
        for _ in range(3):
            Xc.append(vc)
            cu.append(f"d{d}")
        prs += [(3 * d + i, 3 * d + j) for i in range(3) for j in range(3)]
    r = cv_scores(np.array(Xs), np.array(Xc), su, cu, random.Random(1))
    leak_auc = matched_auc(r[0], r[1], prs)
    assert 0.3 < leak_auc < 0.7, leak_auc
    # 補完と標準化は学習の折りだけから決める
    A, Bm = prep(np.array([[1.0], [2.0], [3.0], [float("nan")]]), np.array([[float("nan")], [100.0]]))
    mu, sd = np.mean([1, 2, 3, 2]), np.std([1, 2, 3, 2])
    assert abs(Bm[0, 0] - (2 - mu) / sd) < 1e-9 and abs(Bm[1, 0] - (100 - mu) / sd) < 1e-9, Bm
    assert abs(A[:, 0].mean()) < 1e-9 and Bm.shape[1] == 2 and Bm[0, 1] > Bm[1, 1], (A, Bm)
    for focus, slow, want, sd_ in ((True, False, "delta_pos", 11), (False, False, "delta_null", 11),
                                   (False, False, "delta_null", 12), (False, False, "delta_null", 13),
                                   (False, True, "k_pos", 11)):
        rng = random.Random(sd_)
        files = person_files(rng, focus, slow)
        srows, crows, pairs, _ = match(files, CTRL_LO, 5)
        assert len(srows) >= MIN_STALLS, len(srows)
        r = evaluate(files, srows, crows, pairs, False, 5)
        ci = r["ci95"]
        if want == "delta_pos":
            assert ci["delta"][0] > 0, r
        elif want == "delta_null":
            assert ci["delta"][0] <= 0 <= ci["delta"][1], r
        else:
            assert ci["K"][0] > 0.5, r
    # 副: 停滞の初めの 5 秒にだけ遷移を入れると、副の ΔAUC の下限が 0 を超え、主（u の時点）では区間が 0 を含む
    rng = random.Random(13)
    files = [synth_file(rng, 12, False, False, i, focus_early=True) for i in range(8)]
    srows, crows, pairs, _ = match(files, CTRL_LO_EARLY, 5)
    r = evaluate(files, srows, crows, pairs, True, 5)
    assert r["ci95"]["delta"][0] > 0, r
    # 副の量は (u, u + 5 秒] だけを数える（u ちょうどは入らない・5 秒ちょうどは入る）
    d3 = {"observed_intervals": [{"a_ms": 0, "b_ms": 500_000}], "keys": [[100_000, "alphabetic"]], "onsets": [],
          "focus": [70_000, 100_000, 103_000, 105_000, 105_001], "paste": [[104_000, 3]], "pointer": []}
    f3 = F("z", d3, {"feat": [], "ime_state": [[101_000, 1, 0]], "ime_shadow": []}, False)
    v = feat_n(f3, 100_000, True)
    assert v[-4:] == [2.0, 1.0, 1.0, 0.0], v
    assert v[0] == 1.0 and v[8] == 0.0, v  # W1 = (70_000, 100_000] の遷移は 1（左端は開）・u に遷移があれば since = 0
    assert math.isnan(v[9]) and math.isnan(v[10]), v  # u 以前に ime_state が無ければ欠け
    assert len(feat_n(f3, 100_000, False)) == len(v) - 4
    print("auc selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
