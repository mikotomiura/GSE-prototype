#!/usr/bin/env python3
# kit: selftest
"""既知の誤りを注入した偽の観測ログを作る（照合器のパラメータ回復テスト・design.md §7）。Python 標準ライブラリだけ。

  inject.py --selftest      速い既定（数秒）。★ ケース「パラメータ回復」が最重要の検査

  inject(gt_sessions, rates, timing, seed, iou_min=0.5) -> (obs_rows, truth)

    gt_sessions: 正解のセッションの配列（sessions.json の definitions[<定義>] の中身・start / end が整数のもの）。
    rates = {"miss", "split", "merge", "false_pos"}（各 0〜1・miss + split + merge <= 1）。
      各正解セッションについて独立に 1 回引き、miss = 観測を落とす / split = 観測を 3 つ以上の断片に分ける /
      merge = 次のセッションと 1 行に併せる（2 件を使う）/ それ以外 = そのまま 1 対 1。false_pos は正解 1 件ごとに
      その率で、正解のどれとも重ならない観測を 1 行、正解の間の隙間に足す。
    timing = {"bias_ms", "sd_ms", "end_lag_ms_max"}: 観測行の時刻のずれ = bias_ms + N(0, sd_ms)（±4 sd で打ち切る）
      + 終端の遅れ U{0..end_lag_ms_max}（整数の一様分布）。★ ずれは行ごとに 1 つ引き、観測行の t にだけ足す
      （dwell_ms は正確な長さ）＝ 区間全体が平行移動する。分割の断片は同じずれを共有する。
    seed: 整数。乱数は random.Random(seed) の random() だけ（版を跨いで列が変わらない）。
    戻り値は必ずこの 2 要素のタプル。obs_rows = obs/1 の ime_shadow 行（{"type","t","dwell_ms","nav","abandon"}）を
    t の昇順に並べた配列。nav / abandon は正解の nav_true / outcome == "cancel" を写す（分割は nav が先頭・
    abandon が最後の断片、併合は nav の合計・abandon は後の方）。truth は注入した**実際の値**:
      {"n_gt", "n_obs", "n_exact", "n_miss", "n_split", "n_split_obs", "n_merge", "n_merge_gt", "n_false_pos",
       "skipped": {"split", "merge", "false_pos"}, "risk": {"short", "crowded"}, "max_shift_ms", "rates", "timing",
       "expected": {"precision", "recall", "f1", "split_rate", "merge_rate", "miss_rate", "false_pos_rate"}}
    expected は match.detection_metrics の同名の指標の {"x", "n"}（注入した実際の件数から計算した値）。

★ 何を注入するか（定義に合わせる）: 照合器の分割 / 併合は「各断片が単独では IoU >= iou_min にならない」ときだけ
  数えられる（match.py の docstring の ⚠️）。このため注入する誤りは**その型に限る**:
    ・分割 = ceil(1/iou_min) + 1 個（既定 3 個）の等分。各断片の IoU は 1/k 以下なのでどのずれでも単独では対にならず、
      和集合の IoU は最悪のずれ（max_shift_ms）でも iou_min 以上になる長さのときだけ注入する。
    ・併合 = 隣り合う 2 件を 1 行にする。どちらの IoU も iou_min 未満（一方が併合区間の半分以上を占めない）で、
      最悪のずれでも和集合の IoU が iou_min 以上になるときだけ注入する。
    ・条件に合わなければ正解のまま 1 対 1 で出し、truth["skipped"] に数える（注入した実際の件数が公称の率より少なくなる）。
  ⚠️ 呼び出し側の前提（満たさないと回復できない。truth["risk"] が件数を出す）: risk["short"] = 最悪のずれで 1 対 1 の
     IoU が iou_min を割りうる（長さ L が max_shift_ms・(1 + iou_min)/(1 - iou_min) 未満の）セッションの数、
     risk["crowded"] = 隣との間隔が max_shift_ms 未満（ずれた観測が隣の正解に食い込みうる）の組の数。0 なら
     「注入した種類ごとの件数を照合器が厳密に回復する」ことが保証される（max_shift_ms は打ち切った最悪のずれの上界）。

出典: 設計 design.md §7（パラメータ回復テスト・陽性 / 陰性対照）。
"""
import argparse
import json
import math
import os
import random
import sys
from statistics import NormalDist

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import match  # noqa: E402
import stats  # noqa: E402  ★ 統計は stats.py（Wilson・Bland-Altman）を使う。再実装しない

RATE_KEYS = ("miss", "split", "merge", "false_pos")
TIMING_KEYS = ("bias_ms", "sd_ms", "end_lag_ms_max")
_TRUNC_SD = 4.0          # 正規分布のずれを打ち切る sd の倍数（最悪のずれの上界を保証するため）
_FP_MIN_LEN, _FP_MAX_LEN = 200, 1500
_NORMAL = NormalDist()


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _check_args(rates, timing, seed, iou_min):
    if not isinstance(rates, dict) or set(rates) != set(RATE_KEYS):
        raise ValueError("rates のキーは %s だけ" % ", ".join(RATE_KEYS))
    if any(not _is_num(rates[k]) or not (0.0 <= rates[k] <= 1.0) for k in RATE_KEYS):
        raise ValueError("rates の値は 0 以上 1 以下の数")
    if rates["miss"] + rates["split"] + rates["merge"] > 1.0 + 1e-12:
        raise ValueError("rates の miss + split + merge は 1 以下")
    if not isinstance(timing, dict) or set(timing) != set(TIMING_KEYS):
        raise ValueError("timing のキーは %s だけ" % ", ".join(TIMING_KEYS))
    if not _is_num(timing["bias_ms"]) or not _is_num(timing["sd_ms"]) or timing["sd_ms"] < 0:
        raise ValueError("timing の bias_ms は数・sd_ms は 0 以上の数")
    if type(timing["end_lag_ms_max"]) is not int or timing["end_lag_ms_max"] < 0:
        raise ValueError("timing の end_lag_ms_max は 0 以上の整数")
    if type(seed) is not int:
        raise ValueError("seed は整数")
    match._check_iou_min(iou_min)


def _draw_shift(rng, timing):
    """観測行 1 行の時刻のずれ（整数 ms）= bias + 打ち切った正規分布 + 終端の遅れ（一様）。"""
    z = 0.0
    if timing["sd_ms"] > 0:
        while True:
            u = rng.random()
            if 0.0 < u < 1.0:
                z = _NORMAL.inv_cdf(u)
                if abs(z) <= _TRUNC_SD:
                    break
    lag = int(rng.random() * (timing["end_lag_ms_max"] + 1)) if timing["end_lag_ms_max"] > 0 else 0
    return int(round(timing["bias_ms"] + timing["sd_ms"] * z)) + lag


def _max_shift(timing):
    """ずれの絶対値の上界（打ち切りと丸めを含む）。"""
    b, s, lag = timing["bias_ms"], timing["sd_ms"], timing["end_lag_ms_max"]
    return int(math.ceil(max(abs(b - _TRUNC_SD * s), abs(b + _TRUNC_SD * s + lag)))) + 1


def _worst_pair_iou(length, w):
    """長さ length の区間を w だけ平行移動したときの IoU（最悪）。"""
    return 0.0 if w >= length else (length - w) / float(length + w)


def _row(t, dwell, nav, abandon):
    return {"type": "ime_shadow", "t": t, "dwell_ms": dwell, "nav": nav, "abandon": abandon}


def _nav(s):
    v = s.get("nav_true")
    return v if type(v) is int and v >= 0 else 0


def inject(gt_sessions, rates, timing, seed, iou_min=0.5):
    """既知の誤りを注入した偽の観測ログ (obs_rows, truth) を作る（モジュールの docstring を参照）。"""
    _check_args(rates, timing, seed, iou_min)
    order = sorted(range(len(gt_sessions)),
                   key=lambda i: (match.gt_interval(gt_sessions[i], "gt_sessions[%d]" % i), i))
    gts = [gt_sessions[i] for i in order]
    iv = [match.gt_interval(s) for s in gts]
    n = len(gts)
    rng = random.Random(seed)
    w = _max_shift(timing)
    k_pieces = max(3, int(1.0 / iou_min) + 1)
    split_need = (w * (1.0 + iou_min) / (1.0 - iou_min)) if iou_min < 1.0 else float("inf")
    p_miss, p_split, p_merge = rates["miss"], rates["miss"] + rates["split"], rates["miss"] + rates["split"] + rates["merge"]

    rows = []
    c = {"exact": 0, "miss": 0, "split": 0, "split_obs": 0, "merge": 0, "fp": 0,
         "skip_split": 0, "skip_merge": 0, "skip_fp": 0, "risk_short": 0}
    i = 0
    while i < n:
        lo, hi = iv[i]
        length = hi - lo
        u = rng.random()
        if u < p_miss:
            c["miss"] += 1
            i += 1
            continue
        if u < p_split:
            if length >= k_pieces and length >= split_need:
                d = _draw_shift(rng, timing)
                cuts = [lo + (length * j) // k_pieces for j in range(k_pieces + 1)]
                for j in range(k_pieces):
                    rows.append(_row(cuts[j + 1] + d, cuts[j + 1] - cuts[j], _nav(gts[i]) if j == 0 else 0,
                                     j == k_pieces - 1 and gts[i].get("outcome") == "cancel"))
                c["split"] += 1
                c["split_obs"] += k_pieces
                i += 1
                continue
            c["skip_split"] += 1
        elif u < p_merge:
            ok = False
            if i + 1 < n and hi <= iv[i + 1][0]:
                la, lb, hull = length, iv[i + 1][1] - iv[i + 1][0], iv[i + 1][1] - lo
                i0 = la + lb - 2 * w
                ok = (hull > 0 and max(la, lb) / float(hull) < iou_min and i0 > 0
                      and i0 / float(hull + 2 * w) >= iou_min)
            if ok:
                d = _draw_shift(rng, timing)
                rows.append(_row(iv[i + 1][1] + d, iv[i + 1][1] - lo, _nav(gts[i]) + _nav(gts[i + 1]),
                                 gts[i + 1].get("outcome") == "cancel"))
                c["merge"] += 1
                i += 2
                continue
            c["skip_merge"] += 1
        d = _draw_shift(rng, timing)
        rows.append(_row(hi + d, length, _nav(gts[i]), gts[i].get("outcome") == "cancel"))
        c["exact"] += 1
        if _worst_pair_iou(length, w) < iou_min:
            c["risk_short"] += 1
        i += 1

    # 偽検出: 正解のどれとも重ならない位置（ずれた観測にも当たらないよう max_shift_ms + 10 ms 離す）
    pad = w + 10
    usable = [g for g in range(n - 1) if (iv[g + 1][0] - iv[g][1]) - 2 * pad >= _FP_MIN_LEN]
    for _ in range(n):
        if not (rng.random() < rates["false_pos"]):
            continue
        if not usable:
            c["skip_fp"] += 1
            continue
        g = usable[int(rng.random() * len(usable))]
        avail = (iv[g + 1][0] - iv[g][1]) - 2 * pad
        d = _FP_MIN_LEN + int(rng.random() * (min(_FP_MAX_LEN, avail) - _FP_MIN_LEN + 1))
        start = iv[g][1] + pad + int(rng.random() * (avail - d + 1))
        rows.append(_row(start + d, d, 0, False))
        c["fp"] += 1

    rows.sort(key=lambda r: (r["t"], r["dwell_ms"], r["nav"], r["abandon"]))
    crowded = sum(1 for g in range(n - 1) if iv[g + 1][0] - iv[g][1] < w)
    n_obs = len(rows)
    truth = {
        "n_gt": n, "n_obs": n_obs, "n_exact": c["exact"], "n_miss": c["miss"], "n_split": c["split"],
        "n_split_obs": c["split_obs"], "n_merge": c["merge"], "n_merge_gt": 2 * c["merge"], "n_false_pos": c["fp"],
        "skipped": {"split": c["skip_split"], "merge": c["skip_merge"], "false_pos": c["skip_fp"]},
        "risk": {"short": c["risk_short"], "crowded": crowded}, "max_shift_ms": w,
        "rates": dict(rates), "timing": dict(timing),
        "expected": {
            "precision": {"x": c["exact"], "n": n_obs}, "recall": {"x": c["exact"], "n": n},
            "f1": {"x": 2 * c["exact"], "n": n + n_obs}, "split_rate": {"x": c["split"], "n": n},
            "merge_rate": {"x": c["merge"], "n": n_obs}, "miss_rate": {"x": c["miss"], "n": n},
            "false_pos_rate": {"x": c["fp"], "n": n_obs}},
    }
    return rows, truth


# ---------------------------------------------------------------- selftest

RATES = {"miss": 0.05, "split": 0.03, "merge": 0.03, "false_pos": 0.02}
TIMING = {"bias_ms": 20, "sd_ms": 50, "end_lag_ms_max": 100}


def _gt_population(n, seed, len_lo=1500, len_hi=6000, gap_lo=500, gap_hi=5000):
    """合成の正解: 長さ len_lo〜len_hi ms・間隔 gap_lo〜gap_hi ms（★ 既定は最悪のずれ 321 ms より十分大きい）。"""
    rng = random.Random(seed)
    t, out = 1700000000000, []
    for i in range(n):
        t += gap_lo + int(rng.random() * (gap_hi - gap_lo + 1))
        length = len_lo + int(rng.random() * (len_hi - len_lo + 1))
        out.append(match._gt("t%05d" % (i + 1), t, t + length, nav_true=i % 3,
                             outcome="cancel" if i % 7 == 0 else "commit"))
        t += length
    return out


def _recovery_failures(m, truth):
    """指標 m（detection_metrics の 1 層）が注入した値を回復しているか。回復していない項目の説明の配列。"""
    out = []
    for name, e in sorted(truth["expected"].items()):
        g = m[name]
        if (g["x"], g["n"]) != (e["x"], e["n"]):
            out.append("%s: 件数 %s/%s が注入した %s/%s と違う" % (name, g["x"], g["n"], e["x"], e["n"]))
        p = e["x"] / float(e["n"])
        if g["lo"] is None or not (g["lo"] <= p <= g["hi"]):
            out.append("%s: Wilson 95%% 区間 [%s, %s] が注入した率 %.4f を含まない" % (name, g["lo"], g["hi"], p))
    return out


def _case_parameter_recovery():
    """★ パラメータ回復: 正解 2,000 件に 取り逃し 5% / 分割 3% / 併合 3% / 偽検出 2% と 時間の偏り +20 ms・σ 50 ms・
    終端の遅れ 0〜100 ms を注入し、照合 → 指標の Wilson 95% 区間が注入した率（実際の件数から計算）を含む。
    seed を 5 つ変えて 5 回とも。★ 区間の包含に加え、件数そのものの一致（区間より強い）と、
    時間の偏り・ばらつきの回復（対の終端の差）も見る。"""
    f = []
    for seed in (1, 2, 3, 4, 5):
        gts = _gt_population(2000, 100 + seed)
        obs, truth = inject(gts, RATES, TIMING, seed)
        tag = "seed %d" % seed
        if truth["risk"] != {"short": 0, "crowded": 0}:
            f.append("%s: 前提（risk）が 0 でない: %r" % (tag, truth["risk"]))
        # 実際に注入されている（公称の率の近く・0 件で緑にならない）
        n = truth["n_gt"]
        if not (0.03 <= truth["n_miss"] / n <= 0.07):
            f.append("%s: 取り逃しが公称 5%% の近くに入っていない: %d / %d" % (tag, truth["n_miss"], n))
        if not (truth["n_split"] >= 25 and truth["n_merge"] >= 25 and truth["n_false_pos"] >= 15):
            f.append("%s: 分割 / 併合 / 偽検出が十分に注入されていない: %r" % (
                tag, (truth["n_split"], truth["n_merge"], truth["n_false_pos"])))
        for offset in (0, -50):     # -50 = 終端の遅れの平均（50 ms）を打ち消す設定
            r = match.match(gts, obs, obs_end_offset_ms=offset)
            m = match.detection_metrics(r)[0]
            for msg in _recovery_failures(m, truth):
                f.append("%s offset %d: %s" % (tag, offset, msg))
            if (len(r["split"]), len(r["merge"]), len(r["miss"]), len(r["false_pos"]), len(r["pairs"])) != (
                    truth["n_split"], truth["n_merge"], truth["n_miss"], truth["n_false_pos"], truth["n_exact"]):
                f.append("%s offset %d: 5 種の件数が注入と違う" % (tag, offset))
            # 時間の偏り・ばらつき: 対の終端の差（観測 - 正解）。期待 = bias + lag/2 + offset・sd = √(σ² + lag の分散)
            ba = stats.bland_altman([p["obs"]["t"] + offset for p in r["pairs"]],
                                    [p["gt"]["end_wall_ms"] for p in r["pairs"]])
            lag = TIMING["end_lag_ms_max"]
            want_mean = TIMING["bias_ms"] + lag / 2.0 + offset
            want_sd = math.sqrt(TIMING["sd_ms"] ** 2 + ((lag + 1) ** 2 - 1) / 12.0 + 1.0 / 12.0)
            se = ba["sd"] / math.sqrt(ba["n"])
            if abs(ba["bias"] - want_mean) > 4.0 * se:
                f.append("%s offset %d: 時間の偏り %.2f が期待 %.2f の 4 SE（%.2f）の外" % (tag, offset, ba["bias"], want_mean, 4.0 * se))
            if abs(ba["sd"] - want_sd) > 5.0 * want_sd / math.sqrt(2.0 * (ba["n"] - 1)):
                f.append("%s offset %d: ばらつき %.2f が期待 %.2f の外" % (tag, offset, ba["sd"], want_sd))
    return f


def _case_recovery_negative_control():
    """★ 回復の検査自体が赤くなりうること（陰性対照）: 壊した照合器・誤った補正では回復に失敗する。"""
    f = []
    gts = _gt_population(2000, 101)
    obs, truth = inject(gts, RATES, TIMING, 1)
    ok = match.detection_metrics(match.match(gts, obs))[0]
    if _recovery_failures(ok, truth):
        f.append("基準（正しい照合器）が回復できていない: %r" % (_recovery_failures(ok, truth),))
    for name, kw in (("誤った補正（+3 s）", {"obs_end_offset_ms": 3000}), ("厳しすぎる iou_min（0.99）", {"iou_min": 0.99}),
                     ("緩すぎる iou_min（0.05）", {"iou_min": 0.05})):
        m = match.detection_metrics(match.match(gts, obs, **kw))[0]
        if not _recovery_failures(m, truth):
            f.append("%s でも回復の検査が緑になった（検査が空振り）" % name)
    # 注入の記録（truth）を歪めても赤になる
    bad = json.loads(json.dumps(truth))
    bad["expected"]["recall"]["x"] += 5
    if not _recovery_failures(ok, bad):
        f.append("truth の件数を歪めても回復の検査が緑になった")
    # 観測を 1 行消すと 件数の一致が崩れる（1 行の変異で赤になる）
    m = match.detection_metrics(match.match(gts, obs[:50] + obs[51:]))[0]
    if not _recovery_failures(m, truth):
        f.append("観測を 1 行消しても回復の検査が緑になった")
    return f


def _case_sensitivity_of_definition():
    """IoU 定義の感度（Stop 条件の根拠・直さない）: 短いセッションは時刻のずれで対にならなくなる。
    risk が出て、再現率が落ち、終端の遅れの補正（offset）で回復する。"""
    f = []
    short = _gt_population(1000, 7, len_lo=200, len_hi=200, gap_lo=3000, gap_hi=3000)
    long_ = _gt_population(1000, 8, len_lo=3000, len_hi=3000, gap_lo=3000, gap_hi=3000)
    zero = {"miss": 0.0, "split": 0.0, "merge": 0.0, "false_pos": 0.0}
    so, st = inject(short, zero, TIMING, 3)
    lo_, lt = inject(long_, zero, TIMING, 3)
    if st["risk"]["short"] != 1000 or lt["risk"]["short"] != 0:
        f.append("risk[short] が 200 ms → 1000・3000 ms → 0 でない: %r %r" % (st["risk"], lt["risk"]))
    r_short0 = match.detection_metrics(match.match(short, so))[0]["recall"]["value"]
    r_short1 = match.detection_metrics(match.match(short, so, obs_end_offset_ms=-50))[0]["recall"]["value"]
    r_long = match.detection_metrics(match.match(long_, lo_))[0]["recall"]["value"]
    if r_long != 1.0:
        f.append("3000 ms のセッションは全部対になるはず: %r" % r_long)
    if not (r_short0 < 0.6 and r_short0 < r_short1 < 1.0):
        f.append("200 ms のセッションの再現率が (offset 0) < 0.6・(offset -50) でそれより上がるが 1 未満、でない: %.3f %.3f" % (r_short0, r_short1))
    # 長さ L が 3w 未満だと分割 / 併合の注入は見送る（検出できない型を注入しない）
    _o, sk = inject(short, {"miss": 0.0, "split": 0.5, "merge": 0.5, "false_pos": 0.0}, TIMING, 4)
    if sk["n_split"] != 0 or sk["n_merge"] != 0 or sk["skipped"]["split"] + sk["skipped"]["merge"] != 1000:
        f.append("短いセッションに分割 / 併合を注入した（見送るはず）: %r" % (sk["skipped"],))
    return f


def _case_identity_and_accounting():
    f = []
    gts = _gt_population(200, 5)
    zero = {"miss": 0.0, "split": 0.0, "merge": 0.0, "false_pos": 0.0}
    still = {"bias_ms": 0, "sd_ms": 0, "end_lag_ms_max": 0}
    obs, truth = inject(gts, zero, still, 1)
    if len(obs) != 200 or any(o["t"] != g["end_wall_ms"] or o["dwell_ms"] != g["end_wall_ms"] - g["start_wall_ms"]
                              or o["nav"] != g["nav_true"] or o["abandon"] != (g["outcome"] == "cancel")
                              for o, g in zip(obs, gts)):
        f.append("誤りなし・ずれなしの観測が正解の写しでない")
    if truth["n_exact"] != 200 or truth["n_obs"] != 200 or truth["max_shift_ms"] != 1:
        f.append("誤りなしの truth が違う: %r" % ({k: truth[k] for k in ("n_exact", "n_obs", "max_shift_ms")},))
    r = match.match(gts, obs)
    if len(r["pairs"]) != 200 or any(p["iou"] != 1.0 for p in r["pairs"]):
        f.append("誤りなしで全部 IoU 1.0 の対にならない")
    if not all(set(o) == {"type", "t", "dwell_ms", "nav", "abandon"} and o["type"] == "ime_shadow" for o in obs):
        f.append("観測行の形が obs/1 の ime_shadow でない")
    # 極端な率
    obs1, t1 = inject(gts, dict(zero, miss=1.0), still, 1)
    if obs1 != [] or t1["n_miss"] != 200:
        f.append("miss = 1.0 で全部落ちない")
    obs2, t2 = inject(gts, dict(zero, split=1.0), still, 1)
    r2 = match.match(gts, obs2)
    if t2["n_split"] != 200 or len(r2["split"]) != 200 or any(len(s["obs"]) != 3 for s in r2["split"]):
        f.append("split = 1.0 で全部が 3 断片の分割にならない")
    # ★ 併合は「どちらの IoU も iou_min 未満」の組だけ注入する。長さがばらつく母集団では不均衡な組を見送る
    #   （実測: 200 件で 86 行）ので、merge = 1.0 の厳密な件数は長さ・間隔を揃えた母集団で見る。
    even = _gt_population(200, 5, len_lo=2000, len_hi=2000, gap_lo=1000, gap_hi=1000)
    obs3, t3 = inject(even, dict(zero, merge=1.0), still, 1)
    r3 = match.match(even, obs3)
    if t3["n_merge"] != 100 or len(r3["merge"]) != 100 or len(r3["miss"]) != 0 or t3["skipped"]["merge"] != 0:
        f.append("merge = 1.0 で 2 件ずつ 100 行に併合されない: %r" % (t3["n_merge"],))
    _o, tu = inject(gts, dict(zero, merge=1.0), still, 1)
    if tu["skipped"]["merge"] == 0 or tu["n_merge"] * 2 + tu["n_exact"] != 200:
        f.append("長さがばらつく母集団で不均衡な併合を見送っていない: %r" % (tu["skipped"],))
    obs4, t4 = inject(gts, dict(zero, false_pos=1.0), still, 1)
    r4 = match.match(gts, obs4)
    if t4["n_false_pos"] != 200 or len(r4["false_pos"]) != 200 or len(r4["pairs"]) != 200:
        f.append("false_pos = 1.0 で正解の数だけ偽検出が足されない")
    # 会計: どの入力でも件数が閉じる
    for seed in range(1, 6):
        _o, t = inject(gts, {"miss": 0.1, "split": 0.2, "merge": 0.2, "false_pos": 0.3}, TIMING, seed)
        if t["n_exact"] + t["n_miss"] + t["n_split"] + t["n_merge_gt"] != t["n_gt"]:
            f.append("seed %d: 正解側の件数が閉じない" % seed)
        if t["n_exact"] + t["n_split_obs"] + t["n_merge"] + t["n_false_pos"] != len(_o):
            f.append("seed %d: 観測側の件数（対 + 断片 + 併合 + 偽検出）が行数と違う" % seed)
    return f


def _case_determinism():
    f = []
    gts = _gt_population(300, 9)
    snapshot = json.dumps(gts, sort_keys=True)
    g0 = random.getstate()
    a = inject(gts, RATES, TIMING, 11)
    b = inject(gts, RATES, TIMING, 11)
    c = inject(gts, RATES, TIMING, 12)
    if random.getstate() != g0:
        f.append("グローバルな乱数状態に触った")
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        f.append("同じ seed で結果が同じでない（バイト一致しない）")
    if json.dumps(a[0], sort_keys=True) == json.dumps(c[0], sort_keys=True):
        f.append("seed を変えても観測が変わらない")
    if json.dumps(gts, sort_keys=True) != snapshot:
        f.append("入力の正解を書き換えた")
    if inject(list(reversed(gts)), RATES, TIMING, 11) != a:
        f.append("正解の並びを変えると結果が変わる（開始時刻で整列するはず）")
    return f


def _case_validation():
    f = []

    def raises(name, fn):
        try:
            fn()
        except ValueError:
            return
        except Exception as e:
            f.append("%s: ValueError でなく %r" % (name, e))
            return
        f.append("%s: 例外が出なかった" % name)

    g = _gt_population(5, 1)
    ok = dict(RATES)
    raises("未知の rate キー", lambda: inject(g, dict(ok, extra=0.1), TIMING, 1))
    raises("rate キーが足りない", lambda: inject(g, {"miss": 0.1}, TIMING, 1))
    raises("rate が負", lambda: inject(g, dict(ok, miss=-0.1), TIMING, 1))
    raises("rate が 1 超", lambda: inject(g, dict(ok, false_pos=1.5), TIMING, 1))
    raises("miss + split + merge > 1", lambda: inject(g, dict(ok, miss=0.5, split=0.4, merge=0.3), TIMING, 1))
    raises("rate が真偽値", lambda: inject(g, dict(ok, miss=True), TIMING, 1))
    raises("timing のキーが足りない", lambda: inject(g, ok, {"bias_ms": 0}, 1))
    raises("sd が負", lambda: inject(g, ok, dict(TIMING, sd_ms=-1), 1))
    raises("end_lag が小数", lambda: inject(g, ok, dict(TIMING, end_lag_ms_max=10.5), 1))
    raises("seed が小数", lambda: inject(g, ok, TIMING, 1.5))
    raises("seed が真偽値", lambda: inject(g, ok, TIMING, True))
    raises("iou_min が 0", lambda: inject(g, ok, TIMING, 1, iou_min=0))
    raises("終わりの無いセッション", lambda: inject([match._gt("t1", 0, None)], ok, TIMING, 1))
    if inject([], ok, TIMING, 1)[0] != []:
        f.append("正解 0 件から観測が出た")
    return f


CASES = [
    ("パラメータ回復（5 seed・取り逃し 5% / 分割 3% / 併合 3% / 偽検出 2%・偏り +20 ms・σ 50 ms・終端の遅れ 0〜100 ms）",
     _case_parameter_recovery),
    ("パラメータ回復の陰性対照（壊した照合器・誤った補正・歪めた truth・1 行消しは回復に失敗する）",
     _case_recovery_negative_control),
    ("IoU 定義の感度（短いセッション・risk・offset での回復・見送り）", _case_sensitivity_of_definition),
    ("誤りなしの写し・極端な率・件数の会計", _case_identity_and_accounting),
    ("決定性（seed・グローバル乱数・入力の不変・並び）", _case_determinism),
    ("入力の検証", _case_validation),
]


def selftest():
    bad = 0
    for name, fn in CASES:
        try:
            fails = fn()
        except Exception as e:  # 想定外の例外は失敗
            fails = ["例外 %s: %s" % (type(e).__name__, e)]
        if fails:
            bad += 1
            print("  ❌ " + name)
            for m in fails[:12]:
                print("     FAIL " + m)
        else:
            print("  ✅ " + name)
    if bad:
        print("selftest 失敗 %d 件 / %d 件" % (bad, len(CASES)))
        return 1
    print("selftest OK（%d 件）" % len(CASES))
    return 0


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="既知の誤りを注入した偽の観測ログ（ライブラリ。単体で動かすのは --selftest だけ）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    ap.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
