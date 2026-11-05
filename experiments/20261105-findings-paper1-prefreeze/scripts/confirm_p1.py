"""論文 1 の確認の解析（事前登録 v5 の P3〜P8）。凍結の前に見た書き手で空回しし、凍結の後に取り置きで 1 回だけ回す。

使い方:
  python -I confirm_p1.py seen    <cs1_work> <holdout.json> <klicke_work> <seed> <out_dir>
  python -I confirm_p1.py holdout <cs1_work> <holdout.json> <seed> <out_dir>
  python -I confirm_p1.py --selftest
<cs1_work> の横に、停滞の定義を変えて replay を回し直した中間 <cs1_work>_q995・<cs1_work>_w15・<cs1_work>_w60
（rebuild_onsets.py の出力）が要る（P8 の感度）。
seen: CS1 の見た書き手で全部を回し、判定の値（点推定・区間の位置・分岐・R）は書かない。書くのは件数・区間の幅・
      ほぼ同値の割合・|値| の分位・重みの集まり・幅の換算（仮の信号）・H3 の埋め込みの回収の可否だけ。
      感度（P8）は件数と区間の幅だけ。
holdout: 取り置きの書き手だけの中間で全部を回し、判定まで書く。
書き手の ID も番号も出さない。外部の LLM に送らない。
"""
import bisect
import copy
import glob
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys
from collections import Counter

if os.environ.get("OMP_NUM_THREADS") != "1":
    sys.exit("OMP_NUM_THREADS=1 で走らせる（小さいデータでスレッドを奪い合い、遅くなる・run の手順）")
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prefreeze as pf  # noqa: E402  make_unit・block_start・has_event・k6・c1
k6 = pf.k6

EPS = 0.001
EPS_SET = (0.001, 0.0)  # H1 の支持は両方で分岐 1（P7）
SIGS = ("d_p_stuck", "d_ewma_x")
LEVELS = ("p_stuck", "ewma_x")
STALL_GAP, CTRL_LO, WARM, N_MATCHED = 30_000, 2_000, 60_000, 5
STALL_PRE = 30_000   # 対照から除く停滞の区間 [s − 30 秒, t0]
LAYER_WIN = 30_000   # 層の窓 [u − 30 秒, u]
FEAT_WIN = 30_000    # H3 の量の窓
BAND_LO, BAND_HI, WIDTH_MAX = 0.45, 0.55, 0.10
N_BOOT, N_BOOT_ML, N_BOOT_GRID = 2_000, 200, 50
FAIL_MAX = 0.05      # 学習の失敗の割合の上限（P6）
H2_STEP = 5_000
MIN_WRITER_OBS = 10 * 60_000
TEXT = k6.TEXT
PRESS_SET = TEXT | {"backspace"}
SEP_SYM = {"space", "enter", "tab", "punctuation", "sentence_punctuation"}  # 区切りの感度（空白・記号）
H = 3_600_000
NAN = float("nan")

# 主の設定（P3〜P6）。感度（P8）はこの 1 つの値だけを変える
MAIN = {"d_win": 30_000, "ctrl_hi": 30_000, "ctrl_condA": True, "stall_condA": True, "align": "newline", "layer": "past30",
        "h2_look": 60_000, "h2_pos": "u", "h2_excl": "resume"}
# replay を回し直す感度: 中間の dir の接尾辞・Python の再現に当てる値・replay の上書き
REPLAY_VARIANTS = {
    "q995": {"k6": {"Q": 0.995, "WARMUP": 200}, "overrides": {"q": 0.995, "warmup_count": 200}},
    "w15": {"k6": {"W_MS": 15_000}, "overrides": {"w_ms": 15_000}},
    "w60": {"k6": {"W_MS": 60_000}, "overrides": {"w_ms": 60_000}},
}


def cfg_of(**kw):
    c = dict(MAIN)
    c.update(kw)
    return c


# ---------------- 共通 ----------------

def finite(v):
    return v is not None and isinstance(v, (int, float)) and math.isfinite(v)


def sig4(w, t, d_win=30_000):
    """t の信号 4 つ（差 2・水準 2）。t か t − d_win の行が無い・数値でなければ None。"""
    a, b = w.snap(t), w.snap(t - d_win)
    if a is None or b is None or not all(finite(x) for x in (a[1], a[2], b[1], b[2])):
        return None
    return {"d_p_stuck": a[1] - b[1], "d_ewma_x": a[2] - b[2], "p_stuck": a[1], "ewma_x": a[2]}


def net(w, t):
    """条件 A の量: 窓 (t − W, t] の挿入系 − 削除系の押下の数。W は中間の停滞の定義の W（既定 30 秒）。"""
    W = getattr(w, "w_ms", 30_000)
    hi = bisect.bisect_right(w.ca.press, t)
    lo = bisect.bisect_right(w.ca.press, t - W)
    return w.ca.pref[hi] - w.ca.pref[lo]


def wins_ties(pos, neg, eps=EPS):
    """全ての対（pos × neg）の勝ちの和・対の数・同値の数。|差| < eps を同値（0.5）、差 ≥ eps を勝ち。
    eps = 0 では、差が正なら勝ち・完全に等しければ同値（0.5）。"""
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


def pct_ci(vals):
    """再標本化の値の 95% 区間（パーセンタイル・昇順の int(0.025 k) 番目と min(k − 1, int(0.975 k)) 番目・K6 と同じ添字）。
    数値でない値は除き、除いた数を返す。"""
    v = np.asarray(vals, dtype=float)
    bad = int((~np.isfinite(v)).sum())
    v = np.sort(v[np.isfinite(v)])
    k = len(v)
    if k == 0:
        return None, bad
    return [float(v[int(0.025 * k)]), float(v[min(k - 1, int(0.975 * k))])], bad


def boot_ratio(wp, rng, n_boot=N_BOOT):
    """書き手の (勝ち, 対) を書き手で再標本化した比の 95% 区間。"""
    wp = np.asarray(wp, dtype=float)
    n = len(wp)
    b = rng.integers(0, n, (n_boot, n))
    num, den = wp[b, 0].sum(1), wp[b, 1].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        vals = np.where(den > 0, num / np.maximum(den, 1), np.nan)
    return pct_ci(vals)[0]


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


def h1_branch(tie_share_eps, ci):
    """退化は ε = 0.001 の同値の割合で決める（ε = 0 の分岐にも同じ判定を当てる）。"""
    if tie_share_eps is None or tie_share_eps > 0.5:
        return "degenerate"
    if ci is None:
        return "undeterminable"
    return branch(ci)


def h2_branch(ciu, cir):
    """P5: 1 = 揃えない AUC の下限 > 0.55 かつ R の下限 ≥ 0.5（支持）／2 = 下限 > 0.55 かつ R の上限 < 0.5
    （作業の時期では説明されない上がり）／3 = 下限 > 0.55 で R の区間が 0.5 をまたぐ（判定できない）／4 = それ以外。"""
    if ciu is None or not ciu[0] > BAND_HI:
        return 4
    if cir is None:
        return 3
    if cir[0] >= 0.5:
        return 1
    if cir[1] < 0.5:
        return 2
    return 3


def weight_concentration(pairs):
    p = np.sort(np.asarray([x for x in pairs if x > 0], dtype=float))[::-1]
    if len(p) == 0:
        return None
    top = max(1, int(math.ceil(0.1 * len(p))))
    return {"top10pct_share_of_pairs": float(p[:top].sum() / p.sum()),
            "effective_writers": float(p.sum() ** 2 / (p ** 2).sum()), "writers_with_pairs": int(len(p))}


# ---------------- H3 の量（P4） ----------------

def window_feats(w, a, b, burst=None):
    """(a, b] の押下（文字・空白・改行・後退）から 9 量と、旧い欠測の印（押下 3 未満か 50 ms を超える間隔が無い）。
    量: 押下の数・間隔（50 ms 超）の 10・50・90 分位・2 秒以上と 10 秒以上の間隔の数・後退の割合・バーストの長さの平均・
    1 分あたりの文字の押下。取れない量は NaN（間隔が無ければ分位・押下が無ければ後退の割合とバースト）。
    burst = None はバーストを 2 秒以上の間隔で切る。数を渡すと θ(b) のその倍で切る（θ が未定義なら NaN）。"""
    lo, hi = bisect.bisect_right(w.press, a), bisect.bisect_right(w.press, b)
    ps = [(w.press[i], w.cats[i]) for i in range(lo, hi) if w.cats[i] in PRESS_SET]
    n = len(ps)
    gaps = [g for g in (y[0] - x[0] for x, y in zip(ps, ps[1:])) if g > 50]
    old_missing = n < 3 or not gaps
    if gaps:
        gs = sorted(gaps)
        q = lambda p: gs[min(len(gs) - 1, int(p * len(gs)))]  # noqa: E731
        q10, q50, q90 = q(0.1), q(0.5), q(0.9)
    else:
        q10 = q50 = q90 = NAN
    n2, n10 = sum(g >= 2_000 for g in gaps), sum(g >= 10_000 for g in gaps)
    if burst is None:
        bg = 2_000
    else:
        th = w.theta.at(b)[0]
        bg = th * burst if th else None
    if n == 0:
        bs = bm = NAN
    else:
        bs = sum(1 for _, c in ps if c == "backspace") / n
        if bg is None:
            bm = NAN
        else:
            bursts, cur = [], 1
            for x, y in zip(ps, ps[1:]):
                if y[0] - x[0] >= bg:
                    bursts.append(cur)
                    cur = 1
                else:
                    cur += 1
            bursts.append(cur)
            bm = statistics.mean(bursts)
    rate = sum(1 for _, c in ps if c in TEXT) / ((b - a) / 60_000)
    return [float(n), q10, q50, q90, float(n2), float(n10), bs, bm, rate], old_missing


def feats18(w, u, burst=None):
    """u 以前 30 秒の 9 量と、その前の 30 秒との差 9 つ。と、旧い欠測の印 2 つ（u 以前・その前）。"""
    a, ma = window_feats(w, u - FEAT_WIN, u, burst)
    b, mb = window_feats(w, u - 2 * FEAT_WIN, u - FEAT_WIN, burst)
    return a + [x - y for x, y in zip(a, b)], ma, mb


RATE_DIFF_COL = 17  # 1 分あたりの文字の押下の差（埋め込みの回収に使う・常に数値）


# ---------------- H1（P3）: 書き手 1 人 ----------------

def stall_anchors(w, cfg=None):
    """onset ごとの u（G ≥ 30 秒・同じ u は 1 度〔最初の onset だけ〕・u < s・u の時点で条件 A が偽〔純産出 ≥ 1〕）。
    [(u, s0, nxt, i, t0)]。cfg["stall_condA"] が偽なら条件 A を見ない（v5 の版・感度）。"""
    cfg = MAIN if cfg is None else cfg
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
        if cfg["stall_condA"] and net(w, u) < 1:
            continue
        out.append((u, s0, nxt, i, t0))
    return out


def layer_of(w, u, end, mode):
    a, b = (u - LAYER_WIN, u) if mode == "past30" else (u - LAYER_WIN, end)
    return "event" if pf.has_event(w, a, b) else "none"


def align_of(w, i, cfg, cs1):
    c = w.text_cat[i]
    if not cs1:
        return "boundary" if c in k6.BOUNDARY else "mid"
    if cfg["align"] == "sep_sym":
        return "sep_sym" if c in SEP_SYM else "other"
    return "newline" if c == "enter" else "other"


def in_stall(w, t):
    return any(s0 - STALL_PRE <= t <= t0 for s0, t0, _, _ in w.onsets)


def control_ok(w, i, cfg, cs1, cnt=None):
    """i 番目の文字の入力 u から次の文字の入力までの休止が対照の候補か（P3）。"""
    u, v = w.text[i], w.text[i + 1]
    if not (CTRL_LO <= v - u < cfg["ctrl_hi"]):
        return False
    bs = pf.block_start(w, u) if cs1 else w.t_start
    if bs is None or u - bs < WARM or in_stall(w, u):
        return False
    if cfg["ctrl_condA"] and net(w, u) < 1:
        if cnt is not None:
            cnt["control_excluded_condA_true"] += 1
        return False
    return True


def h1_writer(units, rng, cnt, cfg, feats=False, cs1=True, burst=None):
    """停滞の行と引いた対照。cell = (区切り, 層)。対照の id は (課題, u)。"""
    stalls, cands = [], {}
    for k, w in enumerate(units):
        anchors = stall_anchors(w, cfg)
        cnt["stall_anchors"] += len(anchors)
        if cfg["stall_condA"]:
            cnt["stall_excluded_condA_true"] += len(stall_anchors(w, dict(cfg, stall_condA=False))) - len(anchors)
        for u, s0, nxt, i, _ in anchors:
            bs = pf.block_start(w, u) if cs1 else w.t_start
            if bs is None or u - bs < WARM:
                cnt["stall_warm"] += 1
                continue
            sv = sig4(w, u, cfg["d_win"])
            if sv is None:
                cnt["stall_no_signal"] += 1
                continue
            cell = (align_of(w, i, cfg, cs1), layer_of(w, u, nxt, cfg["layer"]) if cs1 else "none")
            stalls.append(((k, u), sv, cell, feats18(w, u, burst) if feats else None))
        for i in range(len(w.text) - 1):
            if not control_ok(w, i, cfg, cs1, cnt):
                continue
            u, v = w.text[i], w.text[i + 1]
            sv = sig4(w, u, cfg["d_win"])
            if sv is None:
                cnt["control_no_signal"] += 1
                continue
            cell = (align_of(w, i, cfg, cs1), layer_of(w, u, v, cfg["layer"]) if cs1 else "none")
            cands.setdefault(cell, []).append(((k, u), sv, feats18(w, u, burst) if feats else None))
            cnt["control_candidates"] += 1
    rows = []  # (cell, stall_sig, stall_feat, [(cid, sig, feat) ...])
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


def h1_summary(writer_rows, seed, layer="none", hide=True, sigs=SIGS + LEVELS, light=False):
    """各信号・各 ε の対・同値の割合・区間の幅（と、hide でなければ点推定・区間・分岐）。light は分位と重みを省く。"""
    out = {}
    for sig in sigs:
        e = {}
        for eps in EPS_SET:
            wpt = [h1_pairs(r, sig, layer, eps) for r in writer_rows]
            wp = [(a, b) for a, b, _ in wpt]
            tot_w, tot_n, tot_t = sum(a for a, _, _ in wpt), sum(b for _, b, _ in wpt), sum(c for _, _, c in wpt)
            ci = boot_ratio(wp, np.random.default_rng(seed + 1)) if tot_n else None
            x = {"pairs": tot_n, "tie_share": tot_t / tot_n if tot_n else None,
                 "ci_width": (ci[1] - ci[0]) if ci else None}
            if not hide:
                per = sorted(a / b for a, b in wp if b > 0)
                x |= {"pooled_auc": tot_w / tot_n if tot_n else None, "ci95": ci,
                      "diff_from_05_lower_gt_05": bool(ci and ci[0] > 0.5),
                      "per_writer_auc_quantiles": {str(q): float(np.quantile(per, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)} if per else None}
            e["eps_%g" % eps] = x
        if not light:
            vals = [abs(sv[sig]) for r in writer_rows for cell, sv, _, ctrl in r if cell[1] == layer] + \
                   [abs(cs[sig]) for r in writer_rows for cell, _, _, ctrl in r if cell[1] == layer for _, cs, _ in ctrl]
            e |= {"abs_value_quantiles": {str(q): float(np.quantile(vals, q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)} if vals else None,
                  "zero_change_share": (sum(1 for v in vals if v == 0) / len(vals)) if vals else None,
                  "weights": weight_concentration([h1_pairs(r, sig, layer)[1] for r in writer_rows])}
        if not hide:
            ts = e["eps_0.001"]["tie_share"]
            for eps in EPS_SET:
                e["eps_%g" % eps]["branch"] = h1_branch(ts, e["eps_%g" % eps]["ci95"])
        out[sig] = e
    if not hide and all(s in out for s in SIGS):
        out["H1_supported"] = all(out[s]["eps_%g" % eps]["branch"] == 1 for s in SIGS for eps in EPS_SET)
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

def h2_unit(w, cfg, cs1=True):
    """窓の終わり w ごとに (信号, 正例か, 経過の十分位, [w − 30, w] の文字の押下の数, 時刻)。と、
    正例の的（u か t0）の数と、正例の窓を 1 つ以上持てた的の数。"""
    anchors = stall_anchors(w, cfg)
    look = cfg["h2_look"]
    targets = sorted(a[0] if cfg["h2_pos"] == "u" else a[4] for a in anchors)
    if cfg["h2_excl"] == "resume":  # 30 秒以上の全ての休止の u から再開（次の文字の入力・無ければ課題の最後の押下）まで
        ends = w.text[1:] + [w.t_end]
        spans = sorted((a, b) for a, b in zip(w.text, ends) if b - a >= STALL_GAP)
    else:  # v5 の版: 停滞の行になった u の休止だけ
        spans = sorted((a[0], a[2]) for a in anchors)
    st = [(a[1], a[4]) for a in anchors]
    out, got, n_ex = [], set(), 0
    blocks = [tuple(b) for b in (w.blocks if cs1 else [[w.t_start, w.t_end]])]
    for b0, b1 in blocks:
        t = b0 + WARM
        while t <= b1 - look:
            if cfg["h2_excl"] in ("resume", "anchors"):
                j = bisect.bisect_right(spans, (t, float("inf"))) - 1
                excluded = j >= 0 and spans[j][0] <= t <= spans[j][1]
            else:  # v1: [w − 30 秒, w] が [s, t0] と重なる窓だけ
                excluded = any(s0 <= t and t0 >= t - 30_000 for s0, t0 in st)
            n_ex += excluded
            if not excluded:
                sv = sig4(w, t, cfg["d_win"])
                if sv is not None:
                    k = bisect.bisect_right(targets, t)
                    pos = k < len(targets) and targets[k] <= t + look
                    while k < len(targets) and targets[k] <= t + look:
                        got.add(targets[k])
                        k += 1
                    dec = min(9, int(10 * (t - b0) / max(1, b1 - b0)))
                    nt = bisect.bisect_right(w.text, t) - bisect.bisect_right(w.text, t - 30_000)
                    out.append((sv, pos, dec, nt, t))
            t += H2_STEP
    return out, len(set(targets)), len(got), n_ex


def h2_writer(units, rng, cfg, cs1=True):
    wins, n_tg, n_got, n_ex = [], 0, 0, 0
    for k, w in enumerate(units):
        o, a, b, c = h2_unit(w, cfg, cs1)
        n_tg, n_got, n_ex = n_tg + a, n_got + b, n_ex + c
        for sv, pos, dec, nt, t in o:
            wins.append({"sig": sv, "pos": pos, "dec": dec, "nt": nt, "id": (k, t)})
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
    return wins, matched, (n_tg, n_got, n_ex)


def h2_pairs(wins, matched, sig, key=None, eps=EPS):
    if key is None:
        pos = [x["sig"][sig] for x in wins if x["pos"]]
        neg = [x["sig"][sig] for x in wins if not x["pos"]]
        return wins_ties(pos, neg, eps)
    by = {}
    for cell, i, js in matched[key]:
        d = by.setdefault(cell, {"pos": [], "neg": {}})
        d["pos"].append(wins[i]["sig"][sig])
        for j in js:
            d["neg"][j] = wins[j]["sig"][sig]
    w = n = t = 0
    for d in by.values():
        a, b, c = wins_ties(d["pos"], list(d["neg"].values()), eps)
        w, n, t = w + a, n + b, t + c
    return w, n, t


def h2_summary(writer_h2, seed, hide=True):
    tg = sum(x[2][0] for x in writer_h2)
    gt = sum(x[2][1] for x in writer_h2)
    out = {"windows": sum(len(w) for w, _, _ in writer_h2),
           "positives": sum(sum(1 for x in w if x["pos"]) for w, _, _ in writer_h2),
           "matched_positives": sum(len(m["dec"]) for _, m, _ in writer_h2),
           "targets": tg, "targets_with_positive_window": gt, "share_targets_with_positive": gt / tg if tg else None,
           "windows_excluded": sum(x[2][2] for x in writer_h2)}
    for sig in SIGS:
        U3 = np.array([h2_pairs(w, m, sig) for w, m, _ in writer_h2], dtype=float)
        M3 = np.array([h2_pairs(w, m, sig, "dec") for w, m, _ in writer_h2], dtype=float)
        M2 = np.array([h2_pairs(w, m, sig, "dec_q5") for w, m, _ in writer_h2], dtype=float)
        rng = np.random.default_rng(seed + 3)
        n = len(U3)
        b = rng.integers(0, n, (N_BOOT, n))
        with np.errstate(invalid="ignore", divide="ignore"):
            au = U3[b, 0].sum(1) / U3[b, 1].sum(1)
            am = M3[b, 0].sum(1) / M3[b, 1].sum(1)
            r = (au - am) / (au - 0.5)
        (ciu, _), (cim, _), (cir, rbad) = pct_ci(au), pct_ci(am), pct_ci(r)
        e = {"unmatched_ci_width": (ciu[1] - ciu[0]) if ciu else None, "matched_ci_width": (cim[1] - cim[0]) if cim else None,
             "unmatched_tie_share": U3[:, 2].sum() / U3[:, 1].sum() if U3[:, 1].sum() else None,
             "R_boot_nonfinite": rbad, "unmatched_pairs": float(U3[:, 1].sum()), "matched_pairs": float(M3[:, 1].sum())}
        if not hide:
            AU, AM = U3[:, 0].sum() / U3[:, 1].sum(), M3[:, 0].sum() / M3[:, 1].sum()
            R = (AU - AM) / (AU - 0.5) if AU != 0.5 else None
            e |= {"unmatched_auc": AU, "unmatched_ci95": ciu, "matched_auc": AM, "matched_ci95": cim,
                  "matched_dec_q5_auc": M2[:, 0].sum() / M2[:, 1].sum(), "R": R, "R_ci95": cir,
                  "branch": h2_branch(ciu, None if rbad > FAIL_MAX * N_BOOT else cir)}  # 数値でない R が 5% を超えたら R は判定できない
        out[sig] = e
    if not hide:
        out["H2_supported"] = all(out[s]["branch"] == 1 for s in SIGS)
    return out


# ---------------- H3（P6） ----------------

def ml_rows(writer_rows, layer="none", exclude_missing=False):
    """停滞（1・重み 1）と、その停滞に引かれた対照（0・重み 1/k）。量の欠けは NaN のまま残す（主）。
    exclude_missing は旧い欠測（どちらかの窓で押下 3 未満か間隔なし）の停滞と対照を除く版（感度）。
    評価の対の id: 停滞は行ごと、対照は (課題, u)（同じ書き手 × 区切り × 層の中で重複は 1 回）。"""
    X, y, wt, g, cell, cid = [], [], [], [], [], []
    miss = Counter()
    sid = 0
    for wi, r in enumerate(writer_rows):
        for c, sv, fv, ctrl in r:
            if c[1] != layer:
                continue
            pat = lambda f: ("recent" if f[1] else "") + ("_prev" if f[2] else "") or "none"  # noqa: E731
            miss["stall_" + pat(fv)] += 1
            for _, _, f in ctrl:
                miss["control_row_" + pat(f)] += 1
            if exclude_missing:
                if fv[1] or fv[2]:
                    miss["stall_dropped"] += 1
                    continue
                cf = [x for x in ctrl if not (x[2][1] or x[2][2])]
                if not cf:
                    miss["stall_dropped_no_control"] += 1
                    continue
            else:
                cf = ctrl
            X.append(fv[0]), y.append(1), wt.append(1.0), g.append(wi), cell.append(c), cid.append(("s", sid))
            sid += 1
            for cc, _, f in cf:
                X.append(f[0]), y.append(0), wt.append(1.0 / len(cf)), g.append(wi), cell.append(c), cid.append(("c",) + tuple(cc))
    X = np.array(X, dtype=float)
    miss["rows_with_any_nan"] = int(np.isnan(X).any(1).sum()) if len(X) else 0
    return X, np.array(y), np.array(wt), np.array(g), cell, cid, dict(miss)


def models(seed, which=("logreg", "hgb")):
    """学習器の作り方と fit の追加の引数。logreg は訓練の分割の中で中央値の補完と欠測の印。hgb は NaN をそのまま。
    hgb_grid は入れ子の交差検証（書き手でまとめた 3 分割）で小さい格子を選ぶ（感度）。"""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GridSearchCV, GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    allm = {
        "logreg": (lambda: make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                                         LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=1000)),
                   lambda w, g: {"logisticregression__sample_weight": w}),
        "hgb": (lambda: HistGradientBoostingClassifier(random_state=seed + 2, early_stopping=False),
                lambda w, g: {"sample_weight": w}),
        "hgb_grid": (lambda: GridSearchCV(HistGradientBoostingClassifier(random_state=seed + 2, early_stopping=False),
                                          {"learning_rate": [0.05, 0.1], "max_depth": [3, None], "max_iter": [100, 300]},
                                          scoring="roc_auc", cv=GroupKFold(n_splits=3, shuffle=True, random_state=seed + 2),
                                          n_jobs=1, error_score="raise"),
                     lambda w, g: {"groups": g, "sample_weight": w}),
    }
    return {k: allm[k] for k in which}


def paired_auc(pred, y, keys, cids):
    """keys（書き手か写し × 区切り・層）の中の、停滞 × 対照（cid で重複は 1 回）の対を合わせた AUC（ε なし）。"""
    by = {}
    for i in range(len(y)):
        d = by.setdefault(keys[i], ([], {}))
        if y[i] == 1:
            d[0].append(pred[i])
        else:
            d[1][cids[i]] = pred[i]
    w = n = 0
    for pos, neg in by.values():
        a, b, _ = wins_ties(pos, list(neg.values()), 0.0)
        w, n = w + a, n + b
    return w / n if n else None


def oof_pred(X, y, wt, split_groups, spec, seed):
    """書き手でまとめた 5 分割の予測。学習が失敗したら None（失敗 = fit か predict が ValueError を出した回。
    収束しない警告は失敗に数えない・P6）。"""
    from sklearn.model_selection import GroupKFold
    make, fkw = spec
    pred = np.full(len(y), np.nan)
    try:
        for tr, te in GroupKFold(n_splits=5, shuffle=True, random_state=seed + 2).split(X, y, split_groups):
            m = make()
            m.fit(X[tr], y[tr], **fkw(wt[tr], split_groups[tr]))
            pred[te] = m.predict_proba(X[te])[:, 1]
    except ValueError:
        return None
    return pred


def oof_auc(X, y, wt, groups, cells, cids, spec, seed):
    pred = oof_pred(X, y, wt, groups, spec, seed)
    return None if pred is None else paired_auc(pred, y, [(groups[i], cells[i]) for i in range(len(y))], cids)


def boot_oof(X, y, wt, groups, cells, cids, spec, seed, n_rep=None):
    """書き手を復元で引き直すたびに分割と学習をやり直す。写しは元の書き手の番号でまとめ、同じ分割に入れる。
    対は写しの中で作る（写しごとに別の書き手として数える）。引き直しは先に全部決め、各回を並列に回す。"""
    from joblib import Parallel, delayed
    n_rep = N_BOOT_ML if n_rep is None else n_rep
    rng = np.random.default_rng(seed + 4)
    ids = np.unique(groups)
    idx_by = {g: np.where(groups == g)[0] for g in ids}
    picks = [rng.choice(ids, len(ids), replace=True) for _ in range(n_rep)]

    def one(pick):
        ix = np.concatenate([idx_by[g] for g in pick])
        copy_ = np.concatenate([np.full(len(idx_by[g]), c) for c, g in enumerate(pick)])
        pred = oof_pred(X[ix], y[ix], wt[ix], groups[ix], spec, seed)
        if pred is None:
            return None
        return paired_auc(pred, y[ix], [(copy_[j], cells[i]) for j, i in enumerate(ix)], [cids[i] for i in ix])
    res = Parallel(n_jobs=int(os.environ.get("CONFIRM_JOBS", "8")))(delayed(one)(p) for p in picks)
    fails = sum(1 for a in res if a is None)
    ci, _ = pct_ci([a for a in res if a is not None])
    return ci, fails


H2_ML_MAX_POS = 50


def h2_ml_rows(writers, writer_h2, rng):
    """陰性でないことの対照（P6）: 揃えない比べの正例を書き手ごとに最大 50 件（無作為）と、同じ書き手の負例を
    正例 1 つにつき 5 件（無作為）。量は窓の終わり w で作る（欠けは NaN のまま）。負例の重みは 正例の数 / 負例の数
    （書き手の中で正例と負例の重みの和を等しくする）。"""
    X, y, wt, g, cells, cids = [], [], [], [], [], []
    for wi, (units, (wins, _, _)) in enumerate(zip(writers, writer_h2)):
        pos = [x for x in wins if x["pos"]]
        neg = [x for x in wins if not x["pos"]]
        rng.shuffle(pos)
        rng.shuffle(neg)
        fp = [feats18(units[x["id"][0]], x["id"][1])[0] for x in pos[:H2_ML_MAX_POS]]
        fn = [feats18(units[x["id"][0]], x["id"][1])[0] for x in neg[:N_MATCHED * len(fp)]]
        if not fp or not fn:
            continue
        for f in fp:
            X.append(f), y.append(1), wt.append(1.0), g.append(wi), cells.append(None), cids.append(("p", len(cids)))
        for f in fn:
            X.append(f), y.append(0), wt.append(len(fp) / len(fn)), g.append(wi), cells.append(None), cids.append(("n", len(cids)))
    return np.array(X, dtype=float), np.array(y), np.array(wt), np.array(g), cells, cids


def h3_branch(ci, fails, n_rep, control_ok=True):
    if fails > FAIL_MAX * n_rep:
        return "undeterminable_fit_failures"
    if not control_ok or ci is None:
        return "undeterminable"
    return branch(ci)


def h3_summary(writers, writer_rows, writer_h2, seed, hide=True, n_rep=None, exclude_missing=False,
               control=True, which=("logreg", "hgb")):
    n_rep = N_BOOT_ML if n_rep is None else n_rep
    X, y, wt, g, cells, cids, miss = ml_rows(writer_rows, exclude_missing=exclude_missing)
    out = {"rows": int(len(y)), "stalls": int(y.sum()), "missing": miss, "n_rep": n_rep}
    if control:
        Xc, yc, wc, gc, cc, cic = h2_ml_rows(writers, writer_h2, random.Random(seed + 5))
        out["control_rows"] = int(len(yc))
    for name, spec in models(seed, which).items():
        ci, fails = boot_oof(X, y, wt, g, cells, cids, spec, seed, n_rep)
        e = {"ci_width": (ci[1] - ci[0]) if ci else None, "boot_failures": fails}
        if control:
            cci, cfails = boot_oof(Xc, yc, wc, gc, cc, cic, spec, seed, n_rep)
            cok = cfails <= FAIL_MAX * n_rep and cci is not None and cci[0] > BAND_HI
            e |= {"control_ci_width": (cci[1] - cci[0]) if cci else None, "control_boot_failures": cfails,
                  "control_passed": cok}  # 可否だけは seen でも出す（H1 の値は漏れない・判断 16）
        if not hide:
            a = oof_auc(X, y, wt, g, cells, cids, spec, seed)
            e |= {"auc": a, "ci95": ci}
            if control:
                ac = oof_auc(Xc, yc, wc, gc, cc, cic, spec, seed)
                e |= {"control_auc": ac, "control_ci95": cci,
                      "branch": h3_branch(ci, fails, n_rep, cok)}
            else:
                e["branch_without_control"] = h3_branch(ci, fails, n_rep)
        out[name] = e
    if not hide and control:
        out["H3_supported"] = all(out[m]["branch"] == 1 for m in which)
    return out


def h3_recovery(writer_rows, seed, target=0.58, n_rep=50):
    """凍結の前だけ: 停滞の行の 1 つの量（1 分あたりの文字の押下の差）に定数を足して、その量単独の AUC を
    目標にした仮のデータで、2 つの学習器の区間の下限が 0.55 を超えるか（回収できるか）。値は書かず可否だけ。"""
    X, y, wt, g, cells, cids, _ = ml_rows(writer_rows)
    col = RATE_DIFF_COL
    keys = [(g[i], cells[i]) for i in range(len(y))]

    def feat_auc(d):
        return paired_auc(X[:, col] + np.where(y == 1, d, 0.0), y, keys, cids)
    lo, hi = -50.0, 50.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if feat_auc(mid) < target else (lo, mid)
    Xs = X.copy()
    Xs[y == 1, col] += (lo + hi) / 2
    res = {}
    for name, spec in models(seed).items():
        ci, fails = boot_oof(Xs, y, wt, g, cells, cids, spec, seed, n_rep)
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


def writer_pauses(units, rows, cfg=MAIN):
    """換算用: 出来事なしの層の 2 秒以上の休止の信号と、対照の候補（出来事なし・主の対照の規則）の信号の並び。"""
    row_ids = {}
    for cell, sv, _, ctrl in rows:
        if cell[1] == "none":
            row_ids[sv["d_p_stuck"], sv["d_ewma_x"]] = True
    cand = {s: [] for s in SIGS}
    pauses = {s: [] for s in SIGS}
    obs = 0
    for k, w in enumerate(units):
        obs += sum(b - a for a, b in w.intervals)
        anchors = {a[0] for a in stall_anchors(w, cfg)}
        t0s = sorted(o[1] for o in w.onsets)
        for i in range(len(w.text) - 1):
            u, v = w.text[i], w.text[i + 1]
            if v - u < 2_000:
                continue
            bs = pf.block_start(w, u)
            if bs is None or u - bs < WARM or layer_of(w, u, v, "past30") != "none":
                continue
            sv = sig4(w, u, cfg["d_win"])
            if sv is None:
                continue
            j = bisect.bisect_right(t0s, u)
            is_stall = j < len(t0s) and t0s[j] <= v
            is_row = u in anchors and (sv["d_p_stuck"], sv["d_ewma_x"]) in row_ids
            is_cand = control_ok(w, i, cfg, True)
            for s in SIGS:
                pauses[s].append((sv[s], is_stall, is_row))
                if is_cand:
                    cand[s].append(sv[s])
    return {"cand_sorted": {s: sorted(cand[s]) for s in SIGS} if cand[SIGS[0]] else {}, "pauses": pauses, "obs_ms": obs}


# ---------------- 入力 ----------------

class CrossTheta:
    """θ(t) を書き手の課題をまたいで時刻の順に累積する版（感度）。各課題の観測区間の中の隣り合う押下の間隔を、
    書き手の全課題から集めて時刻で並べ、t 以前の分の 0.99 分位（nearest-rank）。標本が 100 未満なら未定義。
    k6.Theta と同じ規則で、集める範囲だけが違う。"""

    def __init__(self, units):
        pooled = []
        for w in units:
            for a, b in w.intervals:
                lo, hi = bisect.bisect_left(w.press, a), bisect.bisect_right(w.press, b)
                seg = w.press[lo:hi]
                pooled += [(y, y - x) for x, y in zip(seg, seg[1:])]
        pooled.sort(key=lambda r: r[0])
        self.ts = [r[0] for r in pooled]
        self.vals = np.array([r[1] for r in pooled], dtype=float)
        self.cache = {}

    def at(self, t):
        i = bisect.bisect_right(self.ts, t)
        if i < k6.WARMUP:
            return (None, i)
        if i not in self.cache:
            k = min(max(math.ceil(k6.Q * i), 1), i) - 1
            self.cache[i] = int(np.partition(self.vals[:i], k)[k])
        return (self.cache[i], i)


def cross_theta_writers(writers):
    """各書き手の課題の onset を、課題をまたいで累積した θ で Python の規則（付録 A1）から作り直した写し。"""
    out, n_in, n_out = [], 0, 0
    for units in writers:
        ct = CrossTheta(units)
        nu = []
        for w in units:
            w2 = copy.copy(w)
            w2.theta = ct
            w2.onsets = k6.replicate_onsets(w.ca, ct)
            n_in, n_out = n_in + len(w.onsets), n_out + len(w2.onsets)
            nu.append(w2)
        out.append(nu)
    return out, {"onsets_main": n_in, "onsets_cross_task_theta": n_out}


def load_cs1(work, hold_p, mode, variant=None):
    """mode=seen: 中間の書き手に取り置きが 1 人もいないこと。mode=holdout: 中間の書き手が全員、取り置きの一覧にいること。
    variant は REPLAY_VARIANTS の名前: Python の再現（付録 A1）に同じ値を当てて照合し、中間の replay の上書きも照らす。"""
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
           "override_mismatch_units": 0, "writers_with_units": len(by_w), "writers_excluded_obs_lt_10min": 0}
    saved = {k: getattr(k6, k) for k in ("Q", "WARMUP", "W_MS")}
    vk = REPLAY_VARIANTS[variant] if variant else {"k6": {}, "overrides": {}}
    writers = []
    try:
        for k, v in vk["k6"].items():
            setattr(k6, k, v)
        for wid in sorted(by_w):
            units = []
            for p in by_w[wid]:
                d = json.load(open(p))
                ov = {o["key"]: o["value"] for o in (d.get("config_overrides") or [])}
                if ov != vk["overrides"]:
                    chk["override_mismatch_units"] += 1
                w = pf.make_unit(d)
                w.blocks = d["blocks"]
                w.w_ms = k6.W_MS
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
    finally:
        for k, v in saved.items():
            setattr(k6, k, v)
    if chk["onset_mismatch_units"] or chk["theta_mismatch"] or chk["stderr_nonempty_units"] or chk["override_mismatch_units"]:
        sys.exit("照合が崩れた（P10）: " + json.dumps(chk))
    chk["writers_eligible"] = len(writers)
    return writers, chk


# ---------------- 感度（P8） ----------------

def h1_run(writers, cfg, seed, hide, feats=False, burst=None, light=True):
    cnt = Counter()
    rng = random.Random(seed)  # 主と同じ 1 本の流れ（書き手の順に引く）。対照の候補が同じなら主と同じ対照になる
    rows = [h1_writer(u, rng, cnt, cfg, feats=feats, burst=burst) for u in writers]
    return rows, {"counts": dict(cnt), "H1": h1_summary(rows, seed, "none", hide, SIGS, light)}


def h2_run(writers, cfg, seed, hide):
    rng2 = random.Random(seed + 6)
    h2 = [h2_writer(u, rng2, cfg) for u in writers]
    return h2, h2_summary(h2, seed, hide)


def sensitivities(writers, seed, hide, main_rows, main_h2, replay_dirs, hold_p, mode, n_keep=None):
    """P8 の感度。判定に使わない。seen では件数と区間の幅だけ（hide）。replay の中間は 1 本ずつ読み直す
    （照合は計算の前に一度済ませてある・読み直しでも同じ照合をかける）。"""
    S = {}
    # H1 だけが変わるもの
    for name, kw in (("ctrl_hi_10s", {"ctrl_hi": 10_000}), ("ctrl_hi_60s", {"ctrl_hi": 60_000}),
                     ("align_sep_sym", {"align": "sep_sym"}), ("layer_until_resume", {"layer": "until_resume"}),
                     ("stall_without_condA", {"stall_condA": False}),
                     ("neither_condA", {"stall_condA": False, "ctrl_condA": False})):
        S[name] = h1_run(writers, cfg_of(**kw), seed, hide)[1]
    # H2 だけが変わるもの
    for name, kw in (("h2_look_30s", {"h2_look": 30_000}), ("h2_look_120s", {"h2_look": 120_000}),
                     ("h2_positive_t0", {"h2_pos": "t0"}), ("h2_exclusion_v1", {"h2_excl": "v1"}),
                     ("h2_exclusion_stall_rows_only", {"h2_excl": "anchors"})):
        S[name] = {"H2": h2_run(writers, cfg_of(**kw), seed, hide)[1]}
    # 信号の差の窓（H1 と H2）
    for name, dw in (("signal_diff_window_15s", 15_000), ("signal_diff_window_60s", 60_000)):
        c = cfg_of(d_win=dw)
        S[name] = h1_run(writers, c, seed, hide)[1] | {"H2": h2_run(writers, c, seed, hide)[1]}
    # θ を課題をまたいで累積（H1 と H2）
    cw, cc = cross_theta_writers(writers)
    S["theta_cross_task"] = {"onsets": cc} | h1_run(cw, MAIN, seed, hide)[1] | {"H2": h2_run(cw, MAIN, seed, hide)[1]}
    del cw
    # 停滞の定義を変えて replay を回し直した中間（H1 と H2）
    for name, vw in replay_dirs.items():
        ws, chk = load_cs1(vw, hold_p, mode, name)
        if n_keep:
            ws = ws[:n_keep]
        S["replay_" + name] = {"checks": chk} | h1_run(ws, MAIN, seed, hide)[1] | {"H2": h2_run(ws, MAIN, seed, hide)[1]}
        del ws
    # H3: 欠測を除く版・バーストを θ で切る版・格子の調整（勾配ブースティングだけ）
    S["h3_exclude_missing"] = h3_summary(writers, main_rows, main_h2, seed, hide, exclude_missing=True, control=False)
    br, _ = h1_run(writers, MAIN, seed, True, feats=True, burst=1.0)
    S["h3_burst_theta_x1"] = h3_summary(writers, br, main_h2, seed, hide, control=False)
    del br
    S["h3_hgb_grid"] = h3_summary(writers, main_rows, main_h2, seed, hide, n_rep=N_BOOT_GRID, control=False,
                                  which=("hgb_grid",))
    return S


def run(mode, argv):
    if mode == "seen":
        work, hold_p, kwork, seed, out = argv
    else:
        work, hold_p, seed, out = argv
    seed = int(seed)
    os.makedirs(out, exist_ok=True)
    hide = mode == "seen"
    smoke = os.environ.get("CONFIRM_SMOKE")
    if smoke and os.path.realpath(out).startswith(os.path.realpath(os.path.join(HERE, ".."))):
        sys.exit("試しの走りは実験の dir の外に出す")
    if mode == "holdout":
        holdout_gate(out, smoke)
    # 照合は全部、計算の前に終える（P10）
    replay_dirs, replay_chk = {}, {}
    for name in REPLAY_VARIANTS:
        vw = work.rstrip("/") + "_" + name
        if not os.path.isdir(vw):
            sys.exit("感度の中間が無い: " + vw)
        replay_chk[name] = load_cs1(vw, hold_p, mode, name)[1]  # 照合だけ（読んだ中間は捨てる）
        replay_dirs[name] = vw
    writers, chk = load_cs1(work, hold_p, mode)
    n_keep = None
    if smoke:  # 試しの走り（正式の結果に書かない）: 書き手を減らし、反復を 3 回に
        global N_BOOT_ML, N_BOOT_GRID
        n_keep = int(smoke)
        writers, N_BOOT_ML, N_BOOT_GRID = writers[:n_keep], 3, 3
    res = {"mode": mode, "checks": chk, "replay_variant_checks": replay_chk, "eps": list(EPS_SET), "main_config": MAIN}
    cnt = Counter()
    rng = random.Random(seed)
    rows = [h1_writer(u, rng, cnt, MAIN, feats=True) for u in writers]
    res["h1_counts"] = dict(cnt)
    res["H1"] = h1_summary(rows, seed, "none", hide)
    ev = h1_summary(rows, seed, "event", hide)
    res["H1_event_layer_described"] = ev
    res["level_floor_ceiling"] = level_floor_share(rows)
    if not hide:
        res["threshold_table"] = threshold_table(rows)
    rng2 = random.Random(seed + 6)
    h2 = [h2_writer(u, rng2, MAIN) for u in writers]
    res["H2"] = h2_summary(h2, seed, hide)
    res["H3"] = h3_summary(writers, rows, h2, seed, hide)
    res["sensitivity"] = sensitivities(writers, seed, hide, rows, h2, replay_dirs, hold_p, mode, n_keep)
    if mode == "seen":
        res["H3_recovery"] = h3_recovery(rows, seed, n_rep=3 if smoke else 50)
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
        if smoke:
            paths = paths[:50]
        kcnt = Counter()
        krng = random.Random(20261101)
        krows = [h1_writer([k6.Writer(p)], krng, kcnt, MAIN, cs1=False) for p in paths]
        res["klicke_H1_described"] = {"counts": dict(kcnt)} | h1_summary(krows, seed, "none", False)
        if not smoke:
            res["precision_projection"] = precision_projection(rows, seed)
            res["boundary_calibration"] = boundary_calibration(rows, seed)
    dst = os.path.join(out, "confirm_%s.json" % mode)
    with open(dst + ".tmp", "w") as f:
        json.dump(res, f, indent=1, default=str)
    os.replace(dst + ".tmp", dst)  # 書く途中で落ちても、完成したファイルだけが残る
    print(json.dumps({"checks": chk}))


def holdout_gate(out, smoke):
    """取り置きは run-confirm-holdout.sh からだけ回す（P10）: 試しの走りを拒み、出力先は実験の results_holdout、
    開始の記録 start.json が HEAD にコミット済みで中身が同じこと。"""
    if smoke:
        sys.exit("取り置きでは試しの走り（CONFIRM_SMOKE）をしない")
    exp = os.path.realpath(os.path.join(HERE, ".."))
    if os.path.realpath(out) != os.path.join(exp, "results_holdout"):
        sys.exit("取り置きの出力先は実験の results_holdout だけ")
    sp = os.path.join(exp, "results_holdout", "start.json")
    repo = subprocess.run(["git", "-C", exp, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    rel = os.path.relpath(sp, repo)
    r = subprocess.run(["git", "-C", repo, "show", "HEAD:" + rel], capture_output=True)
    if r.returncode != 0 or not os.path.exists(sp) or r.stdout != open(sp, "rb").read():
        sys.exit("開始の記録がコミットされていない（run-confirm-holdout.sh を通す）")


def shifted_pairs(rows, sig, d, eps):
    """停滞の値に d を足した仮の信号での、書き手ごとの (勝ち, 対)（P7 の推定量・主の層）。"""
    by = {}
    for cell, sv, _, ctrl in rows:
        if cell[1] != "none":
            continue
        x = by.setdefault(cell, {"pos": [], "neg": {}})
        x["pos"].append(sv[sig] + d)
        for cid, cs, _ in ctrl:
            x["neg"][cid] = cs[sig]
    w = n = 0
    for x in by.values():
        a, b, _ = wins_ties(x["pos"], list(x["neg"].values()), eps)
        w, n = w + a, n + b
    return w, n


def boundary_calibration(rows, seed, n_draw=500, targets=(0.45, 0.50, 0.55)):
    """凍結の前だけ（Codex の round 4 の指摘）: 見た書き手の停滞の値に定数を足し、全員を合わせた AUC（ε = 0.001）を
    目標の値にした仮の信号で、取り置きの見込みの人数を引いた 500 回のそれぞれに確認と同じ区間と分岐を当てる。
    目標が境界（0.45・0.55）のときに分岐 1（同等）と判定する割合は、誤って同等とする割合の見積もりになる。
    ずらしの量は書かない（向きが分かるため）。ε = 0 の分岐も同じ仮の信号で出す。"""
    n_hold = round(146 * 319 / 338)
    out = {"n_hold": n_hold, "n_draw": n_draw}
    for sig in SIGS:
        out[sig] = {}
        for tgt in targets:
            lo, hi = -3.0, 3.0
            for _ in range(50):
                mid = (lo + hi) / 2
                a = [shifted_pairs(r, sig, mid, EPS) for r in rows]
                auc = sum(x for x, _ in a) / sum(y for _, y in a)
                lo, hi = (mid, hi) if auc < tgt else (lo, mid)
            d = (lo + hi) / 2
            wp = {eps: np.array([shifted_pairs(r, sig, d, eps) for r in rows], dtype=float) for eps in EPS_SET}
            rng = np.random.default_rng(seed + 8)
            res = {"eq_eps_0.001": 0, "eq_both_eps": 0, "precision_insufficient": 0}
            for _ in range(n_draw):
                sel = rng.choice(len(rows), n_hold, replace=False)
                br = {}
                for eps in EPS_SET:
                    ci = boot_ratio(wp[eps][sel], np.random.default_rng(int(rng.integers(1 << 31))))
                    br[eps] = branch(ci)
                res["eq_eps_0.001"] += br[0.001] == 1
                res["eq_both_eps"] += br[0.001] == 1 and br[0.0] == 1
                res["precision_insufficient"] += br[0.001] == "precision_insufficient"
            out[sig]["target_%.2f" % tgt] = {k: v / n_draw for k, v in res.items()}
    return out


def level_floor_share(rows, layer="none"):
    """推定の水準の床と天井（p_stuck が 0.02 未満か 0.98 を超える）にある、主の層の停滞と引かれた対照（重複は 1 回）の割合。"""
    st = [sv["p_stuck"] for r in rows for cell, sv, _, _ in r if cell[1] == layer]
    ct = list({cid: cs["p_stuck"] for r in rows for cell, _, _, ctrl in r if cell[1] == layer for cid, cs, _ in ctrl}.values())
    f = lambda v: {"floor_lt_002": float(np.mean(np.array(v) < 0.02)), "ceiling_gt_098": float(np.mean(np.array(v) > 0.98)), "n": len(v)} if v else None  # noqa: E731
    return {"stall": f(st), "control": f(ct)}


def precision_projection(rows, seed, n_draw=500):
    n_hold = round(146 * 319 / 338)  # 見た 338 人のうち観測 10 分以上が 319 人
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


# ---------------- selftest ----------------

def fake_unit(presses, onsets=None, events=(), feat_every=1_000):
    """[(t, cat)] から中間 1 課題の形を作る（feat は毎秒・p_stuck は t/1e6・ewma_x は 0）。onsets を渡さなければ Python の規則で作る。"""
    t_end = presses[-1][0]
    feat = [[t, t / 1e6, 0.0] for t in range(presses[0][0], t_end + 1, feat_every)]
    d = {"keys": [list(p) for p in presses], "feat": feat, "onsets": onsets or [],
         "observed_intervals": [[presses[0][0], t_end]], "blocks": [[presses[0][0], t_end]],
         "events": list(events), "replay_stderr_bytes": 0}
    w = pf.make_unit(d)
    w.blocks = d["blocks"]
    if onsets is None:
        w.onsets = k6.replicate_onsets(w.ca, w.theta)
    return w


def selftest():
    # ε の同値と勝ち
    w, n, t = wins_ties([0.0, 0.0005, 0.01], [0.0, 0.002], 0.001)
    assert (w, n, t) == (3.0, 6, 2), (w, n, t)
    w0, n0, t0 = wins_ties([0.1, 0.2], [0.1, 0.0], 0.0)
    assert (w0, n0, t0) == (3.5, 4, 1), (w0, n0, t0)  # ε = 0 でも完全な同値は 0.5
    assert branch([0.46, 0.54]) == 1 and branch([0.50, 0.56]) == 2 and branch([0.56, 0.58]) == 3
    assert branch([0.44, 0.50]) == 4 and branch([0.40, 0.44]) == 5 and branch([0.40, 0.52]) == "precision_insufficient"
    # 退化の分岐（ε = 0.001 の同値の割合で決め、ε = 0 にも当てる）
    assert h1_branch(0.51, [0.46, 0.54]) == "degenerate" and h1_branch(0.49, [0.46, 0.54]) == 1
    # H2 の分岐（R の下限）
    assert h2_branch([0.56, 0.60], [0.5, 0.9]) == 1 and h2_branch([0.56, 0.60], [0.1, 0.4]) == 2
    assert h2_branch([0.56, 0.60], [0.3, 0.8]) == 3 and h2_branch([0.54, 0.60], [0.6, 0.9]) == 4
    # パーセンタイルの添字
    assert pct_ci(list(range(100)) + [float("nan")]) == ([2.0, 97.0], 1)
    # 量: 押下 3 つ未満は旧い欠測の印・取れない量は NaN・押下の数を量に持つ
    w_ = object.__new__(k6.Writer)
    w_.press = [0, 1000, 1500, 4000, 4300]
    w_.cats = ["alphabetic", "space", "backspace", "alphabetic", "alphabetic"]
    f, m = window_feats(w_, -1, 4300)
    assert not m and f[0] == 5 and f[4] == 1 and abs(f[6] - 0.2) < 1e-9, f
    f, m = window_feats(w_, 3999, 4300)
    assert m and f[0] == 2 and f[1] == 300 and f[4] == 0 and f[6] == 0 and f[7] == 2, f
    f, m = window_feats(w_, 4200, 4300)
    assert m and f[0] == 1 and math.isnan(f[1]) and math.isnan(f[3]) and f[7] == 1, f
    f, m = window_feats(w_, 5000, 6000)
    assert m and f[0] == 0 and math.isnan(f[6]) and math.isnan(f[7]) and f[8] == 0, f
    # 停滞の選び方・対照の除外・H2 の正例（合成の 1 課題）
    pr = [(t, "alphabetic") for t in range(0, 65_001, 500)] + [(t, "alphabetic") for t in range(70_000, 100_001, 500)] + \
         [(t, "alphabetic") for t in range(160_000, 200_001, 500)]
    u1 = fake_unit(pr)
    assert [o[:2] for o in u1.onsets] == [[130_000, 130_500]], u1.onsets  # s = 100 s + 30 s・θ = 500 ms
    an = stall_anchors(u1)
    assert [(a[0], a[2]) for a in an] == [(100_000, 160_000)], an
    u_bad = fake_unit(pr, onsets=[[90_000, 130_500, 500, 150]])  # u ≥ s の停滞は除く
    assert stall_anchors(u_bad) == []
    ctr = [u1.text[i] for i in range(len(u1.text) - 1) if control_ok(u1, i, MAIN, True)]
    assert ctr == [65_000], ctr  # 5 秒の休止だけ（60 秒の休止は上限の外・停滞の区間は除く）
    cnt = Counter()
    rows = h1_writer([u1], random.Random(1), cnt, MAIN, feats=True)
    assert len(rows) == 1 and rows[0][0] == ("other", "none") and [c[0] for c in rows[0][3]] == [(0, 65_000)], rows
    assert abs(rows[0][1]["d_p_stuck"] - 0.03) < 1e-12  # feat の p_stuck = t/1e6 で u と u − 30 秒の差
    # 条件 A が真の休止は対照にしない（後退で純産出 < 1）・非対称の版では対照になる
    pr2 = [(t, "alphabetic") for t in range(0, 60_001, 500)] + [(60_500 + 300 * j, "backspace") for j in range(100)] + \
          [(91_000, "alphabetic"), (96_000, "alphabetic")] + [(t, "alphabetic") for t in range(96_500, 120_001, 500)]
    u2 = fake_unit(pr2, onsets=[])
    i2 = u2.text.index(91_000)
    assert net(u2, 91_000) < 1 and not control_ok(u2, i2, MAIN, True) and control_ok(u2, i2, cfg_of(ctrl_condA=False), True)
    # H2: u 基準の正例は w = 60〜95 秒の 8 窓（w ∈ [u, 再開] は除く）・t0 基準は 75〜95 秒の 5 窓
    o, ntg, ngot, nex = h2_unit(u1, MAIN)
    assert [x[4] for x in o] == list(range(60_000, 100_000, 5_000)) and all(x[1] for x in o) and (ntg, ngot) == (1, 1), o
    o, _, _, _ = h2_unit(u1, cfg_of(h2_pos="t0"))
    assert [x[4] for x in o if x[1]] == list(range(75_000, 100_000, 5_000)) and len(o) == 8, o
    # H2 の除外: 停滞の行にならない長い休止の中の窓も除く（主）・停滞の行の休止だけを除く版では負例に残る
    u0 = fake_unit(pr, onsets=[])
    o, _, _, nex = h2_unit(u0, MAIN)
    assert [x[4] for x in o] == list(range(60_000, 100_000, 5_000)) and not any(x[1] for x in o) and nex == 9, (o, nex)
    o, _, _, _ = h2_unit(u0, cfg_of(h2_excl="anchors"))
    assert len(o) == 17, len(o)
    # 停滞にも条件 A: u の時点で純産出 < 1 の停滞は除く（v5 の版では残る）
    pr3 = [(t, "alphabetic") for t in range(0, 60_001, 500)] + [(60_100 + 100 * j, "backspace") for j in range(130)] + \
          [(73_100, "alphabetic")] + [(t, "alphabetic") for t in range(150_000, 200_001, 500)]
    u3 = fake_unit(pr3, onsets=[[103_100, 103_600, 500, 300]])
    assert net(u3, 73_100) < 1 and stall_anchors(u3) == [] and len(stall_anchors(u3, cfg_of(stall_condA=False))) == 1
    # H3 の評価: 重複した対照は 1 回（同じ cid の予測は 1 つ）
    a = paired_auc([0.9, 0.1, 0.1, 0.5], [1, 0, 0, 0], [(0, "c")] * 4, [("s", 0), ("c", 1), ("c", 1), ("c", 2)])
    assert a == 1.0, a
    a = paired_auc([0.3, 0.5, 0.5, 0.1], [1, 0, 0, 0], [(0, "c")] * 4, [("s", 0), ("c", 1), ("c", 1), ("c", 2)])
    assert a == 0.5, a  # 重複を数えれば 1/3
    # 課題をまたぐ θ: 1 課題だけなら課題の中の θ と同じ onset
    cw, _ = cross_theta_writers([[u1]])
    assert cw[0][0].onsets == u1.onsets
    # 取り置きの門: 試しの走り・ほかの出力先は止める
    for args in (("/tmp/x", "3"), ("/tmp/x", None)):
        try:
            holdout_gate(*args)
            raise AssertionError("holdout_gate が通した")
        except SystemExit:
            pass
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(sys.argv[1], sys.argv[2:])
