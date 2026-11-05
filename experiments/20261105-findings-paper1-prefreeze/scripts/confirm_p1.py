"""論文 1 の確認の解析（事前登録 v4 の P3〜P7）。凍結の前に見た書き手で空回しし、凍結の後に取り置きで 1 回だけ回す。

使い方:
  python -I confirm_p1.py seen    <cs1_work> <holdout.json> <klicke_work> <seed> <out_dir>
  python -I confirm_p1.py holdout <cs1_work> <holdout.json> <seed> <out_dir>
  python -I confirm_p1.py --selftest
seen: CS1 の見た書き手で全部を回し、判定の値（点推定・区間の位置・分岐・R）は書かない。書くのは件数・区間の幅・
      ほぼ同値の割合・|値| の分位・重みの集まり・幅の換算（仮の信号）・H3 の埋め込みの回収の可否だけ。
holdout: 取り置きの書き手だけの中間で全部を回し、判定まで書く。
書き手の ID も番号も出さない。外部の LLM に送らない。
"""
import bisect
import glob
import hashlib
import json
import math
import os
import random
import statistics
import sys

if os.environ.get("OMP_NUM_THREADS") != "1":
    sys.exit("OMP_NUM_THREADS=1 で走らせる（小さいデータでスレッドを奪い合い、遅くなる・run の手順）")
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prefreeze as pf  # noqa: E402  make_unit・block_start・has_event・k6・c1
k6 = pf.k6

EPS = 0.001
SIGS = ("d_p_stuck", "d_ewma_x")
LEVELS = ("p_stuck", "ewma_x")
EVENTS = ("run", "paste", "switch")
STALL_GAP, CTRL_LO, CTRL_HI, WARM, D_WIN, N_MATCHED = 30_000, 2_000, 30_000, 60_000, 30_000, 5
BAND_LO, BAND_HI, WIDTH_MAX = 0.45, 0.55, 0.10
N_BOOT, N_BOOT_ML = 2_000, 200
H2_STEP, H2_LOOK, H2_END = 5_000, 60_000, 60_000
MIN_WRITER_OBS = 10 * 60_000
TEXT = k6.TEXT
PRESS_SET = TEXT | {"backspace"}
H = 3_600_000


# ---------------- 共通 ----------------

def finite(v):
    return v is not None and isinstance(v, (int, float)) and math.isfinite(v)


def sig4(w, t):
    """t の信号 4 つ（差 2・水準 2）。t か t − 30 秒の行が無い・数値でなければ None。"""
    a, b = w.snap(t), w.snap(t - D_WIN)
    if a is None or b is None or not all(finite(x) for x in (a[1], a[2], b[1], b[2])):
        return None
    return {"d_p_stuck": a[1] - b[1], "d_ewma_x": a[2] - b[2], "p_stuck": a[1], "ewma_x": a[2]}


def wins_ties(pos, neg, eps=EPS):
    """全ての対（pos × neg）の勝ちの和・対の数・同値の数。|差| < eps を同値（0.5）、差 ≥ eps を勝ち。"""
    if len(pos) == 0 or len(neg) == 0:
        return 0.0, 0, 0
    neg = np.sort(np.asarray(neg, dtype=float))
    p = np.asarray(pos, dtype=float)
    if eps > 0:
        lo = np.searchsorted(neg, p - eps, side="right")   # c ≤ s − eps → 勝ち
        hi = np.searchsorted(neg, p + eps, side="left")    # c < s + eps
    else:
        lo = np.searchsorted(neg, p, side="left")
        hi = np.searchsorted(neg, p, side="right")
    ties = int((hi - lo).sum())
    return float(lo.sum() + 0.5 * ties), len(p) * len(neg), ties


def boot_ratio(wp, rng, n_boot=N_BOOT):
    """書き手の (勝ち, 対) を書き手で再標本化した比の 95% 区間（2.5・97.5 の分位・K6 と同じ添字）。"""
    wp = np.asarray(wp, dtype=float)
    n = len(wp)
    b = rng.integers(0, n, (n_boot, n))
    num, den = wp[b, 0].sum(1), wp[b, 1].sum(1)
    vals = np.sort(np.where(den > 0, num / np.maximum(den, 1), np.nan))
    vals = vals[~np.isnan(vals)]
    k = len(vals)
    return [float(vals[int(0.025 * k)]), float(vals[min(k - 1, int(0.975 * k))])]


def branch(ci):
    lo, hi = ci
    if hi - lo > WIDTH_MAX:
        return "precision_insufficient"
    if lo >= BAND_LO and hi <= BAND_HI:
        return 1
    if lo > BAND_HI:
        return 3
    if hi < BAND_LO:
        return 5
    if lo <= BAND_HI < hi:
        return 2
    return 4


def weight_concentration(pairs):
    p = np.sort(np.asarray([x for x in pairs if x > 0], dtype=float))[::-1]
    if len(p) == 0:
        return None
    top = max(1, int(math.ceil(0.1 * len(p))))
    return {"top10pct_share_of_pairs": float(p[:top].sum() / p.sum()),
            "effective_writers": float(p.sum() ** 2 / (p ** 2).sum()), "writers_with_pairs": int(len(p))}


# ---------------- H3 の量（P4） ----------------

def window_feats(w, a, b):
    """(a, b] の押下（文字・空白・改行・後退）から 8 量。押下が 3 未満なら None。"""
    lo, hi = bisect.bisect_right(w.press, a), bisect.bisect_right(w.press, b)
    ps = [(w.press[i], w.cats[i]) for i in range(lo, hi) if w.cats[i] in PRESS_SET]
    if len(ps) < 3:
        return None
    gaps = [y[0] - x[0] for x, y in zip(ps, ps[1:])]
    gaps = [g for g in gaps if g > 50]
    if not gaps:
        return None
    gs = sorted(gaps)
    q = lambda p: gs[min(len(gs) - 1, int(p * len(gs)))]  # noqa: E731
    bursts, cur = [], 1
    for x, y in zip(ps, ps[1:]):
        if y[0] - x[0] >= 2_000:
            bursts.append(cur)
            cur = 1
        else:
            cur += 1
    bursts.append(cur)
    n_text = sum(1 for _, c in ps if c in TEXT)
    return [q(0.1), q(0.5), q(0.9), sum(g >= 2_000 for g in gaps), sum(g >= 10_000 for g in gaps),
            sum(1 for _, c in ps if c == "backspace") / len(ps), statistics.mean(bursts), n_text / ((b - a) / 60_000)]


def feats16(w, u):
    a = window_feats(w, u - D_WIN, u)
    b = window_feats(w, u - 2 * D_WIN, u - D_WIN)
    if a is None or b is None:
        return None
    return a + [x - y for x, y in zip(a, b)]


# ---------------- H1（P3）: 書き手 1 人 ----------------

def stall_anchors(w):
    """onset ごとの u（G ≥ 30 秒・同じ u は 1 度・u < s）。[(u, s0, nxt, i)]"""
    out, seen = [], set()
    for s0, t0, _, _ in w.onsets:
        i = bisect.bisect_right(w.text, t0) - 1
        if i < 0:
            continue
        u = w.text[i]
        nxt = w.text[i + 1] if i + 1 < len(w.text) else w.t_end
        if nxt - u < STALL_GAP or u in seen:
            continue
        seen.add(u)
        if u >= s0:
            continue
        out.append((u, s0, nxt, i))
    return out


def layer_of(w, u, end, mode):
    a, b = (u - D_WIN, u) if mode == "past30" else (u - D_WIN, end)
    return "event" if pf.has_event(w, a, b) else "none"


def h1_writer(units, rng, cnt, mode="past30", feats=False, cs1=True):
    """停滞の行と引いた対照。cell = (区切り, 層)。対照の id は (課題, u)。"""
    stalls, cands = [], {}
    for k, w in enumerate(units):
        anchors = stall_anchors(w)
        cnt["stall_anchors"] += len(anchors)
        for u, s0, nxt, i in anchors:
            bs = pf.block_start(w, u) if cs1 else w.t_start
            if bs is None or u - bs < WARM:
                cnt["stall_warm"] += 1
                continue
            sv = sig4(w, u)
            if sv is None:
                cnt["stall_no_signal"] += 1
                continue
            align = ("newline" if w.text_cat[i] == "enter" else "other") if cs1 else \
                ("boundary" if w.text_cat[i] in k6.BOUNDARY else "mid")
            layer = layer_of(w, u, nxt, mode) if cs1 else "none"
            fv = feats16(w, u) if feats else None
            stalls.append(((k, u), sv, (align, layer), fv))

        def in_stall(t):
            return any(a - D_WIN <= t <= b for a, b, _, _ in w.onsets)
        for i in range(len(w.text) - 1):
            u, v = w.text[i], w.text[i + 1]
            if not (CTRL_LO <= v - u < CTRL_HI):
                continue
            bs = pf.block_start(w, u) if cs1 else w.t_start
            if bs is None or u - bs < WARM or in_stall(u):
                continue
            sv = sig4(w, u)
            if sv is None:
                continue
            align = ("newline" if w.text_cat[i] == "enter" else "other") if cs1 else \
                ("boundary" if w.text_cat[i] in k6.BOUNDARY else "mid")
            layer = layer_of(w, u, v, mode) if cs1 else "none"
            cands.setdefault((align, layer), []).append(((k, u), sv, feats16(w, u) if feats else None))
    rows = []  # (cell, stall_sig, stall_feat, [ (cid, sig, feat) ... ])
    for sid, sv, cell, fv in stalls:
        pool = cands.get(cell, [])[:]
        rng.shuffle(pool)
        ctrl = pool[:N_MATCHED]
        if not ctrl:
            cnt["stall_no_control"] += 1
            continue
        cnt["stall_rows_%s_%s" % cell] += 1
        rows.append((cell, sv, fv, ctrl))
    return rows


def h1_pairs(rows, sig, layer="none", eps=EPS):
    """書き手 × 区切り × 層の中の、停滞 × 引かれた対照（重複は 1 回）の勝ち・対・同値。"""
    by = {}
    for cell, sv, _, ctrl in rows:
        if cell[1] != layer:
            continue
        d = by.setdefault(cell, {"pos": [], "neg": {}})
        d["pos"].append(sv[sig])
        for cid, cs, _ in ctrl:
            d["neg"][cid] = cs[sig]
    w = n = t = 0
    for d in by.values():
        a, b, c = wins_ties(d["pos"], list(d["neg"].values()), eps)
        w, n, t = w + a, n + b, t + c
    return w, n, t


def h1_summary(writer_rows, seed, layer="none", hide=True):
    out = {}
    for sig in SIGS + LEVELS:
        wpt = [h1_pairs(r, sig, layer) for r in writer_rows]
        wp = [(a, b) for a, b, _ in wpt]
        tot_w, tot_n, tot_t = sum(a for a, _, _ in wpt), sum(b for _, b, _ in wpt), sum(c for _, _, c in wpt)
        ci = boot_ratio(wp, np.random.default_rng(seed + 1))
        vals = [abs(sv[sig]) for r in writer_rows for cell, sv, _, ctrl in r if cell[1] == layer] + \
               [abs(cs[sig]) for r in writer_rows for cell, _, _, ctrl in r if cell[1] == layer for _, cs, _ in ctrl]
        e = {"pairs": tot_n, "eps_tie_share": tot_t / tot_n if tot_n else None,
             "ci_width": ci[1] - ci[0],
             "abs_value_quantiles": {str(q): float(np.quantile(vals, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)} if vals else None,
             "zero_change_share": (sum(1 for v in vals if v == 0) / len(vals)) if vals else None,
             "weights": weight_concentration([b for _, b in wp])}
        if not hide:
            per = [a / b for a, b in wp if b > 0]
            e |= {"pooled_auc": tot_w / tot_n if tot_n else None, "ci95": ci,
                  "branch": "degenerate" if (tot_t / tot_n if tot_n else 1) > 0.5 else branch(ci),
                  "diff_from_05_lower_gt_05": ci[0] > 0.5,
                  "per_writer_auc_median": statistics.median(per) if per else None}
        out[sig] = e
    if not hide:
        b1 = [out[s]["branch"] for s in SIGS]
        out["H1_supported"] = all(b == 1 for b in b1)
    return out


def threshold_table(writer_rows, layer="none"):
    """副の記述: 書き手ごとに引かれた対照の 80・90・95 分位を閾値にした当たりと超過（中央値と全員の比）。"""
    res = {}
    for sig in SIGS:
        res[sig] = {}
        for q in (0.8, 0.9, 0.95):
            hit, exc, hn, hd, en, ed = [], [], 0, 0, 0, 0
            for r in writer_rows:
                pos = [sv[sig] for cell, sv, _, _ in r if cell[1] == layer]
                neg = list({cid: cs[sig] for cell, _, _, ctrl in r if cell[1] == layer for cid, cs, _ in ctrl}.values())
                if not pos or not neg:
                    continue
                cv = sorted(neg)
                th = cv[min(len(cv) - 1, int(q * len(cv)))]
                h = sum(1 for v in pos if v > th)
                e = sum(1 for c in cv if c > th)
                hit.append(h / len(pos))
                exc.append(e / len(cv))
                hn, hd, en, ed = hn + h, hd + len(pos), en + e, ed + len(cv)
            res[sig][str(q)] = {"hit_median": statistics.median(hit) if hit else None,
                                "exceed_median": statistics.median(exc) if exc else None,
                                "hit_pooled": hn / hd if hd else None, "exceed_pooled": en / ed if ed else None}
    return res


# ---------------- H2（P5） ----------------

def h2_unit(w, cs1=True):
    """窓の終わり w ごとに (信号, 正例か, 経過の十分位, [w − 30, w] の文字の押下の数, 時刻)。"""
    anchors = stall_anchors(w)
    us = sorted(a[0] for a in anchors)
    spans = sorted((a[0], a[2]) for a in anchors)
    out = []
    blocks = [tuple(b) for b in (w.blocks if cs1 else [[w.t_start, w.t_end]])]
    for b0, b1 in blocks:
        t = b0 + WARM
        while t <= b1 - H2_END:
            j = bisect.bisect_right(spans, (t, float("inf"))) - 1
            inside = j >= 0 and spans[j][0] <= t <= spans[j][1]
            if not inside:
                sv = sig4(w, t)
                if sv is not None:
                    k = bisect.bisect_right(us, t)
                    pos = k < len(us) and us[k] <= t + H2_LOOK
                    dec = min(9, int(10 * (t - b0) / max(1, b1 - b0)))
                    nt = bisect.bisect_right(w.text, t) - bisect.bisect_right(w.text, t - D_WIN)
                    out.append((sv, pos, dec, nt, t))
            t += H2_STEP
    return out


def h2_writer(units, rng, cs1=True, keep_feats=False):
    wins = []
    for k, w in enumerate(units):
        for sv, pos, dec, nt, t in h2_unit(w, cs1):
            wins.append({"sig": sv, "pos": pos, "dec": dec, "nt": nt, "id": (k, t),
                         "feat": feats16(w, t) if keep_feats else None})
    # 押下の数の五分位（書き手の中）
    if wins:
        nts = sorted(x["nt"] for x in wins)
        cuts = [nts[min(len(nts) - 1, int(p * len(nts)))] for p in (0.2, 0.4, 0.6, 0.8)]
        for x in wins:
            x["q5"] = bisect.bisect_right(cuts, x["nt"])
    # 揃え直し: 正例 1 つに、同じ十分位の負例を最大 5 件（非復元）。併記は十分位 × 五分位
    matched = {"dec": [], "dec_q5": []}
    for key, kf in (("dec", lambda x: x["dec"]), ("dec_q5", lambda x: (x["dec"], x["q5"]))):
        negs = {}
        for i, x in enumerate(wins):
            if not x["pos"]:
                negs.setdefault(kf(x), []).append(i)
        for i, x in enumerate(wins):
            if x["pos"]:
                pool = negs.get(kf(x), [])[:]
                rng.shuffle(pool)
                if pool[:N_MATCHED]:
                    matched[key].append((kf(x), i, pool[:N_MATCHED]))
    return wins, matched


def h2_pairs(wins, matched, sig, key=None):
    if key is None:
        pos = [x["sig"][sig] for x in wins if x["pos"]]
        neg = [x["sig"][sig] for x in wins if not x["pos"]]
        a, b, _ = wins_ties(pos, neg)
        return a, b
    by = {}
    for cell, i, js in matched[key]:
        d = by.setdefault(cell, {"pos": [], "neg": {}})
        d["pos"].append(wins[i]["sig"][sig])
        for j in js:
            d["neg"][j] = wins[j]["sig"][sig]
    w = n = 0
    for d in by.values():
        a, b, _ = wins_ties(d["pos"], list(d["neg"].values()))
        w, n = w + a, n + b
    return w, n


def h2_summary(writer_h2, seed, hide=True):
    out = {"windows": sum(len(w) for w, _ in writer_h2),
           "positives": sum(sum(1 for x in w if x["pos"]) for w, _ in writer_h2),
           "matched_positives": sum(len(m["dec"]) for _, m in writer_h2)}
    for sig in SIGS:
        U = np.array([h2_pairs(w, m, sig) for w, m in writer_h2], dtype=float)
        M = np.array([h2_pairs(w, m, sig, "dec") for w, m in writer_h2], dtype=float)
        M2 = np.array([h2_pairs(w, m, sig, "dec_q5") for w, m in writer_h2], dtype=float)
        rng = np.random.default_rng(seed + 3)
        n = len(U)
        b = rng.integers(0, n, (N_BOOT, n))
        au = U[b, 0].sum(1) / U[b, 1].sum(1)
        am = M[b, 0].sum(1) / M[b, 1].sum(1)
        r = (au - am) / (au - 0.5)
        q = lambda x: [float(np.sort(x)[int(0.025 * N_BOOT)]), float(np.sort(x)[min(N_BOOT - 1, int(0.975 * N_BOOT))])]  # noqa: E731
        ciu, cim, cir = q(au), q(am), q(r)
        e = {"unmatched_ci_width": ciu[1] - ciu[0], "matched_ci_width": cim[1] - cim[0]}
        if not hide:
            AU, AM = U[:, 0].sum() / U[:, 1].sum(), M[:, 0].sum() / M[:, 1].sum()
            R = (AU - AM) / (AU - 0.5)
            e |= {"unmatched_auc": AU, "unmatched_ci95": ciu, "matched_auc": AM, "matched_ci95": cim,
                  "matched_dec_q5_auc": M2[:, 0].sum() / M2[:, 1].sum(), "R": R, "R_ci95": cir,
                  "branch": 1 if (ciu[0] > BAND_HI and R >= 0.5) else 2 if ciu[0] > BAND_HI else 3}
        out[sig] = e
    if not hide:
        out["H2_supported"] = all(out[s]["branch"] == 1 for s in SIGS)
    return out


# ---------------- H3（P6） ----------------

def ml_rows(writer_rows, layer="none"):
    """停滞（1・重み 1）と、その停滞に引かれた対照（0・重み 1/k）。量が欠ける行は除く。"""
    X, y, wt, g, cell, missing = [], [], [], [], [], 0
    for wi, r in enumerate(writer_rows):
        for c, sv, fv, ctrl in r:
            if c[1] != layer:
                continue
            cf = [(cid, cs, f) for cid, cs, f in ctrl if f is not None]
            if fv is None or not cf:
                missing += 1
                continue
            X.append(fv), y.append(1), wt.append(1.0), g.append(wi), cell.append(c)
            for _, _, f in cf:
                X.append(f), y.append(0), wt.append(1.0 / len(cf)), g.append(wi), cell.append(c)
    return np.array(X, dtype=float), np.array(y), np.array(wt), np.array(g), cell, missing


def models(seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return {"logreg": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=1000)),
            "hgb": lambda: HistGradientBoostingClassifier(random_state=seed + 2, early_stopping=False)}


def oof_auc(X, y, wt, groups, cells, make, seed, pairs_by_cell=True):
    """書き手でまとめた 5 分割の予測で、書き手 ×（区切り・層）の中の対を合わせた AUC。groups は元の書き手の番号。"""
    from sklearn.model_selection import GroupKFold
    pred = np.full(len(y), np.nan)
    for tr, te in GroupKFold(n_splits=5, shuffle=True, random_state=seed + 2).split(X, y, groups):
        m = make()
        try:
            m.fit(X[tr], y[tr], **({"logisticregression__sample_weight": wt[tr]} if hasattr(m, "steps") else {"sample_weight": wt[tr]}))
        except ValueError:
            return None
        pred[te] = m.predict_proba(X[te])[:, 1]
    by = {}
    for i in range(len(y)):
        key = (groups[i], cells[i] if pairs_by_cell else None)
        by.setdefault(key, ([], []))[0 if y[i] == 1 else 1].append(pred[i])
    w = n = 0
    for pos, neg in by.values():
        a, b, _ = wins_ties(pos, neg, 0.0)
        w, n = w + a, n + b
    return w / n if n else None


def boot_oof(X, y, wt, groups, cells, make, seed, n_rep=N_BOOT_ML, pairs_by_cell=True):
    """書き手を復元で引き直すたびに分割と学習をやり直す。写しは元の書き手の番号でまとめ、同じ分割に入れる。
    対は写しの中で作る（写しごとに別の書き手として数える）。引き直しは先に全部決め、各回を並列に回す（結果は順に並ぶ）。"""
    from joblib import Parallel, delayed
    rng = np.random.default_rng(seed + 4)
    ids = np.unique(groups)
    idx_by = {g: np.where(groups == g)[0] for g in ids}
    picks = [rng.choice(ids, len(ids), replace=True) for _ in range(n_rep)]

    def one(pick):
        rows, orig, copy = [], [], []
        for c, g in enumerate(pick):
            ix = idx_by[g]
            rows.append(ix)
            orig.append(np.full(len(ix), g))
            copy.append(np.full(len(ix), c))
        ix = np.concatenate(rows)
        return oof_auc_copies(X[ix], y[ix], wt[ix], np.concatenate(orig), np.concatenate(copy),
                              [cells[i] for i in ix], make, seed, pairs_by_cell)
    res = Parallel(n_jobs=int(os.environ.get("CONFIRM_JOBS", "8")))(delayed(one)(p) for p in picks)
    vals = np.sort([a for a in res if a is not None])
    fails = sum(1 for a in res if a is None)
    k = len(vals)
    return ([float(vals[int(0.025 * k)]), float(vals[min(k - 1, int(0.975 * k))])] if k else None), fails


def oof_auc_copies(X, y, wt, orig, copy, cells, make, seed, pairs_by_cell):
    from sklearn.model_selection import GroupKFold
    pred = np.full(len(y), np.nan)
    try:
        for tr, te in GroupKFold(n_splits=5, shuffle=True, random_state=seed + 2).split(X, y, orig):
            m = make()
            m.fit(X[tr], y[tr], **({"logisticregression__sample_weight": wt[tr]} if hasattr(m, "steps") else {"sample_weight": wt[tr]}))
            pred[te] = m.predict_proba(X[te])[:, 1]
    except ValueError:
        return None
    by = {}
    for i in range(len(y)):
        by.setdefault((copy[i], cells[i] if pairs_by_cell else None), ([], []))[0 if y[i] == 1 else 1].append(pred[i])
    w = n = 0
    for pos, neg in by.values():
        a, b, _ = wins_ties(pos, neg, 0.0)
        w, n = w + a, n + b
    return w / n if n else None


H2_ML_MAX_POS = 50


def h2_ml_rows(writers, writer_h2, rng):
    """陰性でないことの対照（P6）: 揃えない比べの正例を書き手ごとに最大 50 件（無作為）と、同じ書き手の負例を
    正例 1 つにつき 5 件（無作為）。量は窓の終わり w で作る。量が欠ける窓は除く。"""
    X, y, wt, g, cells = [], [], [], [], []
    for wi, (units, (wins, _)) in enumerate(zip(writers, writer_h2)):
        pos = [x for x in wins if x["pos"]]
        neg = [x for x in wins if not x["pos"]]
        rng.shuffle(pos)
        rng.shuffle(neg)
        fp = [f for f in (feats16(units[x["id"][0]], x["id"][1]) for x in pos[:H2_ML_MAX_POS]) if f is not None]
        if not fp:
            continue
        fn = []
        for x in neg:
            if len(fn) >= N_MATCHED * len(fp):
                break
            f = feats16(units[x["id"][0]], x["id"][1])
            if f is not None:
                fn.append(f)
        if not fn:
            continue
        for f in fp:
            X.append(f), y.append(1), wt.append(1.0), g.append(wi), cells.append(None)
        for f in fn:
            X.append(f), y.append(0), wt.append(len(fp) / len(fn)), g.append(wi), cells.append(None)
    return np.array(X, dtype=float), np.array(y), np.array(wt), np.array(g), cells


def h3_summary(writers, writer_rows, writer_h2, seed, hide=True, n_rep=N_BOOT_ML):
    X, y, wt, g, cells, missing = ml_rows(writer_rows)
    out = {"rows": int(len(y)), "stalls": int(y.sum()), "stalls_dropped_missing_feats": missing}
    Xc, yc, wc, gc, cc = h2_ml_rows(writers, writer_h2, random.Random(seed + 5))
    out["control_rows"] = int(len(yc))
    for name, make in models(seed).items():
        ci, fails = boot_oof(X, y, wt, g, cells, make, seed, n_rep)
        cci, cfails = boot_oof(Xc, yc, wc, gc, cc, make, seed, n_rep, pairs_by_cell=False)
        e = {"ci_width": (ci[1] - ci[0]) if ci else None, "boot_failures": fails,
             "control_ci_width": (cci[1] - cci[0]) if cci else None, "control_boot_failures": cfails}
        if not hide:
            a = oof_auc(X, y, wt, g, cells, make, seed)
            ac = oof_auc(Xc, yc, wc, gc, cc, make, seed, pairs_by_cell=False)
            control_ok = cci is not None and cci[0] > BAND_HI
            e |= {"auc": a, "ci95": ci, "control_auc": ac, "control_ci95": cci, "control_passed": control_ok,
                  "branch": branch(ci) if control_ok and ci else "undeterminable"}
        out[name] = e
    if not hide:
        out["H3_supported"] = all(out[m]["branch"] == 1 for m in ("logreg", "hgb"))
    return out


def h3_recovery(writer_rows, seed, target=0.58, n_rep=50):
    """凍結の前だけ: 停滞の行の 1 つの量（1 分あたりの文字の押下の差・列 15）に定数を足して、その量単独の AUC を
    目標にした仮のデータで、2 つの学習器の区間の下限が 0.55 を超えるか（回収できるか）。値は書かず可否だけ。"""
    X, y, wt, g, cells, _ = ml_rows(writer_rows)
    col = 15

    def feat_auc(d):
        by = {}
        for i in range(len(y)):
            by.setdefault((g[i], cells[i]), ([], []))[0 if y[i] == 1 else 1].append(X[i, col] + (d if y[i] == 1 else 0))
        w = n = 0
        for pos, neg in by.values():
            a, b, _ = wins_ties(pos, neg, 0.0)
            w, n = w + a, n + b
        return w / n
    lo, hi = -50.0, 50.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if feat_auc(mid) < target else (lo, mid)
    Xs = X.copy()
    Xs[y == 1, col] += (lo + hi) / 2
    res = {}
    for name, make in models(seed).items():
        ci, fails = boot_oof(Xs, y, wt, g, cells, make, seed, n_rep)
        res[name] = {"recovered_lower_gt_055": bool(ci and ci[0] > BAND_HI), "boot_failures": fails}
    return res


# ---------------- 幅の換算（凍結の前だけ・見た書き手） ----------------

def conversion(writer_rows, writer_pauses, sig, target, how):
    """仮の信号: 停滞の値を、対を合わせた AUC（ε あり）が target になるようにずらす。
    how = "shift"（定数を足す）/ "lehmann"（対照の分布の分位 u を u^(1/a) へ）。閾値は書き手の対照の候補の 90 分位。"""
    def transform(v, cand_sorted, p):
        if how == "shift":
            return v + p
        n = len(cand_sorted)
        r = (bisect.bisect_left(cand_sorted, v) + bisect.bisect_right(cand_sorted, v)) / 2 / n
        r = min(max(r, 0.5 / n), 1 - 0.5 / n) ** (1 / p)
        return cand_sorted[min(n - 1, int(r * n))]

    def pooled(p):
        w = n = 0
        for r, pz in zip(writer_rows, writer_pauses):
            cs = pz["cand_sorted"]
            if not cs:
                continue
            by = {}
            for cell, sv, _, ctrl in r:
                if cell[1] != "none":
                    continue
                d = by.setdefault(cell, {"pos": [], "neg": {}})
                d["pos"].append(transform(sv[sig], cs[sig], p))
                for cid, c, _ in ctrl:
                    d["neg"][cid] = c[sig]
            for d in by.values():
                a, b, _ = wins_ties(d["pos"], list(d["neg"].values()))
                w, n = w + a, n + b
        return w / n
    lo, hi = (-3.0, 3.0) if how == "shift" else (0.05, 20.0)
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if pooled(mid) < target else (lo, mid)
    p = (lo + hi) / 2
    hit_n = hit_d = exc_n = exc_d = fires = fires_stall = 0
    rates = []
    for r, pz in zip(writer_rows, writer_pauses):
        cs = pz["cand_sorted"][sig] if pz["cand_sorted"] else []
        if len(cs) < 10:
            continue
        thr = cs[min(len(cs) - 1, int(0.9 * len(cs)))]
        pos = [transform(sv[sig], cs, p) for cell, sv, _, _ in r if cell[1] == "none"]
        if not pos:
            continue
        hit_n += sum(1 for v in pos if v > thr)
        hit_d += len(pos)
        exc_n += sum(1 for c in cs if c > thr)
        exc_d += len(cs)
        f = fs = 0
        for v, is_stall, is_row in pz["pauses"][sig]:
            vv = transform(v, cs, p) if is_row else v
            if vv > thr:
                f += 1
                fs += is_stall
        fires, fires_stall = fires + f, fires_stall + fs
        rates.append(f / (pz["obs_ms"] / H))
    return {"stall_hit_pooled": hit_n / hit_d if hit_d else None, "control_exceed_pooled": exc_n / exc_d if exc_d else None,
            "fires_per_hour_median": statistics.median(rates) if rates else None,
            "share_of_fires_on_stall_pauses": fires_stall / fires if fires else None, "writers": len(rates)}


def writer_pauses(units, rows):
    """換算用: 出来事なしの層の 2 秒以上の休止の信号と、対照の候補（出来事なし）の信号の並び。"""
    row_ids = {}
    for cell, sv, _, ctrl in rows:
        if cell[1] == "none":
            row_ids[sv["d_p_stuck"], sv["d_ewma_x"]] = True
    cand = {s: [] for s in SIGS}
    pauses = {s: [] for s in SIGS}
    obs = 0
    row_keys = set()
    for k, w in enumerate(units):
        obs += sum(b - a for a, b in w.intervals)
        anchors = {a[0] for a in stall_anchors(w)}
        t0s = sorted(o[1] for o in w.onsets)

        def in_stall(t):
            return any(a - D_WIN <= t <= b for a, b, _, _ in w.onsets)
        for i in range(len(w.text) - 1):
            u, v = w.text[i], w.text[i + 1]
            if v - u < 2_000:
                continue
            bs = pf.block_start(w, u)
            if bs is None or u - bs < WARM or layer_of(w, u, v, "past30") != "none":
                continue
            sv = sig4(w, u)
            if sv is None:
                continue
            j = bisect.bisect_right(t0s, u)
            is_stall = j < len(t0s) and t0s[j] <= v
            is_row = u in anchors and (sv["d_p_stuck"], sv["d_ewma_x"]) in row_ids
            for s in SIGS:
                pauses[s].append((sv[s], is_stall, is_row))
                if CTRL_LO <= v - u < CTRL_HI and not in_stall(u):
                    cand[s].append(sv[s])
    return {"cand_sorted": {s: sorted(cand[s]) for s in SIGS} if cand[SIGS[0]] else {}, "pauses": pauses, "obs_ms": obs}


# ---------------- 入力 ----------------

def load_cs1(work, hold_p, mode):
    """mode=seen: 中間の書き手に取り置きが 1 人もいないこと。mode=holdout: 中間の書き手が全員、取り置きの一覧にいること。"""
    hold = set(json.load(open(hold_p))["2019"])
    hh = {hashlib.sha256(h.encode()).hexdigest() for h in hold}
    wh = json.load(open(os.path.join(work, "writers.json")))
    uw = json.load(open(os.path.join(work, "units.json")))
    present = {wh[str(v)] for v in uw.values()}
    if mode == "seen" and present & hh:
        sys.exit("見た書き手の中間に取り置きの書き手がいる")
    if mode == "holdout" and not present <= hh:
        sys.exit("取り置きの中間に一覧の外の書き手がいる")
    by_w = {}
    for p in sorted(glob.glob(os.path.join(work, "u[0-9]*.json"))):
        by_w.setdefault(uw[os.path.basename(p)[1:-5]], []).append(p)
    chk = {"units": 0, "onset_mismatch_units": 0, "theta_mismatch": 0, "stderr_nonempty_units": 0,
           "writers_with_units": len(by_w), "writers_excluded_obs_lt_10min": 0}
    writers = []
    for wid in sorted(by_w):
        units = []
        for p in by_w[wid]:
            d = json.load(open(p))
            w = pf.make_unit(d)
            w.blocks = d["blocks"]
            units.append(w)
            chk["units"] += 1
            if k6.replicate_onsets(w.ca, w.theta) != [list(o) for o in w.onsets]:
                chk["onset_mismatch_units"] += 1
            chk["theta_mismatch"] += sum(1 for s0, _, th, n in w.onsets if w.theta.at(s0) != (th, n))
            chk["stderr_nonempty_units"] += w.stderr_bytes != 0
        if sum(sum(b - a for a, b in w.intervals) for w in units) < MIN_WRITER_OBS:
            chk["writers_excluded_obs_lt_10min"] += 1
            continue
        writers.append(units)
    if chk["onset_mismatch_units"] or chk["theta_mismatch"] or chk["stderr_nonempty_units"]:
        sys.exit("照合が崩れた（P10）: " + json.dumps(chk))
    chk["writers_eligible"] = len(writers)
    return writers, chk


def new_cnt():
    c = {k: 0 for k in ("stall_anchors", "stall_warm", "stall_no_signal", "stall_no_control")}
    for a in ("newline", "other", "boundary", "mid"):
        for L in ("none", "event"):
            c["stall_rows_%s_%s" % (a, L)] = 0
    return c


def run(mode, argv):
    if mode == "seen":
        work, hold_p, kwork, seed, out = argv
    else:
        work, hold_p, seed, out = argv
    seed = int(seed)
    os.makedirs(out, exist_ok=True)
    hide = mode == "seen"
    writers, chk = load_cs1(work, hold_p, mode)
    if os.environ.get("CONFIRM_SMOKE"):  # 試しの走り（正式の結果に書かない）: 書き手を減らし、反復を 3 回に
        global N_BOOT_ML
        writers, N_BOOT_ML = writers[:int(os.environ["CONFIRM_SMOKE"])], 3
        if os.path.realpath(out).startswith(os.path.realpath(os.path.join(HERE, ".."))):
            sys.exit("試しの走りは実験の dir の外に出す")
    res = {"mode": mode, "checks": chk, "eps": EPS}
    cnt = new_cnt()
    rng = random.Random(seed)
    rows = [h1_writer(u, rng, cnt, "past30", feats=True) for u in writers]
    res["h1_counts"] = cnt
    res["H1"] = h1_summary(rows, seed, "none", hide)
    res["H1_event_layer"] = h1_summary(rows, seed, "event", True) | (
        {} if hide else {"described": {s: h1_summary(rows, seed, "event", False)[s].get("pooled_auc") for s in SIGS}})
    cnt_s = new_cnt()
    rows_s = [h1_writer(u, random.Random(seed), cnt_s, "until_resume") for u in writers]
    res["H1_sens_layer_until_resume"] = {"counts": cnt_s} | ({} if hide else {
        s: h1_summary(rows_s, seed, "none", False)[s] for s in SIGS})
    if not hide:
        res["threshold_table"] = threshold_table(rows)
    rng2 = random.Random(seed + 6)
    h2 = [h2_writer(u, rng2) for u in writers]
    res["H2"] = h2_summary(h2, seed, hide)
    res["H3"] = h3_summary(writers, rows, h2, seed, hide)
    if mode == "seen":
        res["H3_recovery"] = h3_recovery(rows, seed, n_rep=3 if os.environ.get("CONFIRM_SMOKE") else 50)
        pz = [writer_pauses(u, r) for u, r in zip(writers, rows)]
        conv = {}
        for s in SIGS:
            conv[s] = {}
            for how in ("shift", "lehmann"):
                for tgt in (0.50, 0.55, 0.60, 0.65, 0.70):
                    conv[s]["%s_%.2f" % (how, tgt)] = conversion(rows, pz, s, tgt, how)
        res["width_conversion_cs1"] = conv
        # KLiCKe（既に見たデータ・記述）: 同じ推定量で値を出す
        paths = sorted(glob.glob(os.path.join(kwork, "w*.json")))
        if os.environ.get("CONFIRM_SMOKE"):
            paths = paths[:50]
        kcnt = new_cnt()
        krng = random.Random(20261101)
        krows = []
        for p in paths:
            w = k6.Writer(p)
            krows.append(h1_writer([w], krng, kcnt, cs1=False))
        res["klicke_H1_described"] = {"counts": kcnt} | {s: v for s, v in h1_summary(krows, seed, "none", False).items()}
        # 精度の見込み（主の層・ε あり）: 見た書き手から取り置きの見込みの人数を引いた区間の幅
        if not os.environ.get("CONFIRM_SMOKE"):
            res["precision_projection"] = precision_projection(rows, seed)
    json.dump(res, open(os.path.join(out, "confirm_%s.json" % mode), "w"), indent=1, default=str)
    print(json.dumps({"checks": chk}))


def precision_projection(rows, seed, n_draw=500):
    n_hold = round(146 * 319 / 341)
    out = {"n_hold_expected_after_exclusion": n_hold}
    for sig in SIGS:
        wp = np.array([h1_pairs(r, sig)[:2] for r in rows], dtype=float)
        rng = np.random.default_rng(seed + 7)
        widths = []
        for _ in range(n_draw):
            sel = rng.choice(len(wp), n_hold, replace=False)
            ci = boot_ratio(wp[sel], rng)
            widths.append(ci[1] - ci[0])
        out[sig] = {"width_median": float(np.median(widths)), "width_p95": float(np.quantile(widths, 0.95)),
                    "share_le_010": float(np.mean(np.array(widths) <= WIDTH_MAX))}
    return out


def selftest():
    # ε の同値と勝ち
    w, n, t = wins_ties([0.0, 0.0005, 0.01], [0.0, 0.002], 0.001)
    # 0.0: vs 0.0 同値・vs 0.002 負け(差 −0.002) → 0.5 / 0.0005: vs 0.0 同値・vs 0.002 負け(−0.0015) → 0.5 / 0.01: 勝ち 2
    assert (w, n, t) == (3.0, 6, 2), (w, n, t)
    w0, n0, t0 = wins_ties([0.1, 0.2], [0.1, 0.0], 0.0)
    assert (w0, n0, t0) == (3.5, 4, 1), (w0, n0, t0)
    assert branch([0.46, 0.54]) == 1 and branch([0.50, 0.56]) == 2 and branch([0.56, 0.58]) == 3
    assert branch([0.44, 0.50]) == 4 and branch([0.40, 0.44]) == 5 and branch([0.40, 0.52]) == "precision_insufficient"
    # 量: 押下 3 つ未満は欠測
    w_ = object.__new__(k6.Writer)
    w_.press = [0, 1000, 1500, 4000, 4300]
    w_.cats = ["alphabetic", "space", "backspace", "alphabetic", "alphabetic"]
    f = window_feats(w_, -1, 4300)
    assert f is not None and f[3] == 1 and abs(f[5] - 0.2) < 1e-9, f
    assert window_feats(w_, 3999, 4300) is None
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(sys.argv[1], sys.argv[2:])
