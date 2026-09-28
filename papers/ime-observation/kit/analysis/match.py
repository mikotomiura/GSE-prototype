#!/usr/bin/env python3
# kit: selftest
"""照合器と検出の指標: 正解側の変換セッション（gt_sessions.py の出力）と観測側の ime_shadow 行（obs/1）を
時間区間の重なりで照合し、検出の適合率・再現率・F1・分割率・併合率を Wilson 95% CI つきで出す。
Python 標準ライブラリだけ（統計は stats.py を import する。再実装しない）。

  match.py --sessions S.json --definition all|macos_def|windows_def --obs OBS --plan PLAN --oracle ORACLE
           [--config CFG.json] --out OUT.json
  match.py --selftest      速い既定（数秒）

区間と照合（design.md §1.2 / §1.3）:
  ・正解の区間 = [start_wall_ms, end_wall_ms]（壁時計 ms・両端を含む）。観測の区間 = [end - dwell_ms, end]、
    end = t + obs_end_offset_ms（★ 判断 22: ime_shadow の t は drain した時刻で、変換の終端ではない。
    既定 obs_end_offset_ms = 0 で [t - dwell_ms, t]。offset は区間全体を平行移動する（dwell_ms は長さ）。
    終端の遅れの平均を打ち消すなら負の値: 遅れが 0〜100 ms の一様分布なら -50）。
  ・IoU = 重なり / 和。1 対 1 = IoU >= iou_min（既定 0.5）を IoU の降順で貪欲に割り当てる。
    同点は 正解の開始時刻 → 観測の開始時刻 → 内容 の昇順（★ 入力の並びに依らない: 出力も内容で整列する）。
    長さ 0 の区間は、同じ点の長さ 0 の区間とだけ対になる。
  ・分割 = 1 対 1 で対にならなかった正解 1 件に、未使用の観測 2 件以上が重なり、その観測の和集合（区間の集合として測る）
    との IoU が iou_min 以上。併合 = その逆（観測 1 件に正解 2 件以上）。分割と併合の候補は、重なりで繋がる
    未使用の項目ごとに、IoU の高い候補から 1 つずつ確定する（確定したら使った項目を外して候補を作り直す）。
    残りの正解が取り逃し、残りの観測が偽検出。
  ⚠️ **この定義の性質**（研究者が M3 で凍結する定義に関わる・直さない）: 各断片が単独で IoU >= iou_min にならない
    ときだけ「分割」と数えられる。隣り合う 2 断片への分割は、大きい方（>= 50%）が 1 対 1 になり、残りは偽検出になる
    （selftest「定義の性質」で固定）。併合も同様（一方が併合区間の >= 50% を占めると、その正解が対になり、
    もう一方は取り逃しになる）。また観測の時刻がずれると、短いセッションほど対にならなくなる（長さ L の
    セッションが対になるのは平行移動が L/3 以下のとき）。→ 数字が動く型なので、報告では層ごとに読むこと。

Recount for split_rate / merge_rate (decision 38): the primary pairing above (used for "pairs", precision,
recall and F1) is never changed. Separately, detection_metrics() takes a second pass over the leftover
false_pos / miss items and reclassifies, for the purpose of split_rate / merge_rate only:
  (a) a false_pos row whose own length has a fraction >= theta covered by an already-paired ground-truth
      session's interval is counted as extra evidence that session was split;
  (b) a miss session whose own length has a fraction >= theta covered by an already-paired observation's
      interval is counted as extra evidence that observation was a merge.
theta defaults to 0.5 and is configurable (CLI config key "theta", 0 < theta <= 1). Each leftover item is
attributed to at most one paired counterpart (the one with the largest covered fraction; ties broken by the
counterpart's start time then content). This recount changes only split_rate / merge_rate and the new
n_split_gt_recount / n_merge_obs_recount / n_fp_as_split / n_miss_as_merge fields below; it never moves an
item between match()'s pairs / split / merge / miss / false_pos buckets, so n_gt, n_obs, precision, recall
and F1 are unaffected. See recount_split_merge() for the underlying computation.

戻り値の形（★ 018 / 019 / 020 がこの形に依存する）:
  match(...) = {"pairs": [{"gt", "obs", "iou"}], "split": [{"gt", "obs": [行…]}], "merge": [{"obs", "gt": [セッション…]}],
                "miss": [セッション…], "false_pos": [行…]}
  detection_metrics(result, strata, theta, obs_end_offset_ms) = 層ごとの [{"stratum", "n_gt", "n_obs", "n_pairs",
    "n_split_gt", "n_split_obs", "n_merge_obs", "n_merge_gt", "n_miss", "n_false_pos", "n_split_gt_recount",
    "n_merge_obs_recount", "n_fp_as_split", "n_miss_as_merge", "precision", "recall", "f1", "split_rate",
    "merge_rate", "miss_rate", "false_pos_rate"}]。各指標 = {"x", "n", "value", "lo", "hi"}（Wilson 95%・n = 0 は
    値も区間も None）: 適合率 = 対 / 観測  再現率 = 対 / 正解
      F1 = 2 x 対 / (正解 + 観測)（= 対に入った項目の割合。Wilson は近似だが、1 つの対が正解側と観測側の 2 つの
      「成功」として数えられており独立でない。区間は目安として扱うこと — see decision 38's follow-up note below)
      分割率 = (分割になった正解 + n_split_gt_recount) / 正解  併合率 = (併合になった観測 + n_merge_obs_recount) / 観測
      取り逃し率 = 取り逃し / 正解  偽検出率 = 偽検出 / 観測。
      n_gt = 対 + 分割の正解 + 併合の正解 + 取り逃し、 n_obs = 対 + 分割の観測 + 併合の観測 + 偽検出（this identity
      partitions gt / obs into disjoint buckets and is unaffected by the theta recount above; n_fp_as_split and
      n_miss_as_merge are informational breakdowns of n_false_pos / n_miss, not separate buckets).

CLI（--sessions は gt_sessions.py の出力・--definition でその中の 1 つを選ぶ）:
  ・層 = (cell, scenario, speed)。scenario / speed は plan の試行から、cell は設定の "cell"（既定 = plan の os）。
    試行に帰属できない項目（試行の外の偽検出など）は (cell, null, null)。併合は各正解を自分の層に数える
    （merge_obs は先頭の正解の層・merge_gt は各正解それぞれの層。decision 38 follow-up）。
  ・設定 CFG（JSON）: {"iou_min": 0.5, "obs_end_offset_ms": 0, "theta": 0.5, "clock_offsets_ms": {"<block_id>": ms},
    "cell": "<ラベル>", "drop_start_while_open": false}。
    Assumption: the ground-truth session timestamps (sessions.json) come from the same wall clock as the oracle
    log (gt_sessions.py builds both from one t_wall_ms series); clock_offsets_ms corrects only for the gap
    between that shared clock and the observation side's clock.
    clock_offsets_ms は「観測側の時計 - 正解側の時計」（kit/pilot/clock_sync.py の obs - gt と同じ符号）。観測行の
    "t" は常に元の値のまま変更せず、補正した時刻を常に別の欄 "t_gt_clock" に付ける（block が clock_offsets_ms に
    無ければ補正 0 の t_gt_clock を付け、その block_id を出力の config.uncorrected_blocks に列挙する）。照合は
    "t_gt_clock" があればそれを使う（obs_interval() を参照）。観測がどのブロックかは、補正後の時刻が oracle の
    block_begin〜block_end に最も近いブロックで決める（補正がブロックの間隔より十分小さい前提）。
  ・除外は**試行単位**（判断 28・区間では外さない）: excluded_by が空でないセッション、終わりの無いセッション
    （open_at_end）、drop_start_while_open が true のとき n_start_while_open > 0 のセッション、および excluded の
    要素の trial_ids に挙がった試行の正解と、その試行（oracle の trial_begin〜trial_end との最大の重なり）に入る
    観測を照合から外す。理由ごとの件数を出力に残す（除外は全部報告する）。Note: a session with trial_id == null
    (for example one dropped only via the open_at_end reason) can never appear in excluded[].trial_ids, so
    observations that fall in that time window are not excluded by trial membership alone; only the ground-truth
    session itself is dropped, and any nearby observation is still matched normally (it may end up false_pos).
    n_start_while_open (diagnostic, judgment 28) is not used to exclude anything by default; kept-session counts
    with n_start_while_open > 0 are reported per stratum in the output under "diagnostics.start_while_open".
  ・出力は path を含まず、同じ入力なら同じバイト列（sort_keys・LF・UTF-8・BOM なし）。入力の SHA-256 を残す。

exit: 0 = 出力した / 2 = 入力が読めない・使い方の誤り。
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from bisect import bisect_left, bisect_right

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import gt_sessions  # noqa: E402  oracle の読み取りと InputError を流用する
import stats  # noqa: E402  ★ Wilson は stats.wilson を使う（再実装しない）

InputError = gt_sessions.InputError
SCENARIO_RE = re.compile(r"^S([1-9]|1[0-5])$")
SPEEDS = ("slow", "mid", "fast")
CELL_RE = re.compile(r"^[A-Za-z0-9_.+-]{1,64}$")
DEFINITIONS = ("all", "macos_def", "windows_def")


# ---------------------------------------------------------------- 区間の幾何

def _is_int(v):
    return type(v) is int


def _check_iou_min(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0.0 < v <= 1.0):
        raise ValueError("iou_min は 0 より大きく 1 以下の数")


def gt_interval(s, where="gt"):
    """正解セッションの区間 (lo, hi)。整数でない・終わりが無い（open_at_end）・逆順は ValueError。"""
    if not isinstance(s, dict):
        raise ValueError("%s: セッションはオブジェクト" % where)
    lo, hi = s.get("start_wall_ms"), s.get("end_wall_ms")
    if not (_is_int(lo) and _is_int(hi)):
        raise ValueError("%s: start_wall_ms / end_wall_ms が整数でない（終わりの無い open_at_end は呼び出し側で外す）" % where)
    if hi < lo:
        raise ValueError("%s: end_wall_ms が start_wall_ms より前" % where)
    return (lo, hi)


def obs_interval(row, obs_end_offset_ms=0, where="obs"):
    """Observation interval (lo, hi) = [end - dwell_ms, end], end = t_ref + obs_end_offset_ms (the offset
    translates the whole interval; dwell_ms is the length). t_ref is row["t_gt_clock"] when present (the
    observation clock translated into the ground-truth clock; the CLI always attaches it) and row["t"]
    otherwise. Note: "t" itself is always the raw, uncorrected value; any clock correction only ever
    appears in t_gt_clock (decision 38 follow-up)."""
    if not isinstance(row, dict):
        raise ValueError("%s: 観測行はオブジェクト" % where)
    t = row.get("t_gt_clock")
    if t is None:
        t = row.get("t")
    d = row.get("dwell_ms")
    if not (_is_int(t) and _is_int(d)) or d < 0:
        raise ValueError("%s: t / dwell_ms が整数でない（dwell_ms は 0 以上）" % where)
    end = t + obs_end_offset_ms
    return (end - d, end)


def _check_theta(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0.0 < v <= 1.0):
        raise ValueError("theta は 0 より大きく 1 以下の数")


def _covered_frac(inner, outer):
    """Fraction of interval `inner`'s length that lies inside interval `outer`. A zero-length inner interval
    is fully covered (1.0) when its point lies within outer, else not covered (0.0)."""
    lo, hi = inner
    if lo == hi:
        return 1.0 if outer[0] <= lo <= outer[1] else 0.0
    inter = min(hi, outer[1]) - max(lo, outer[0])
    return max(0.0, inter) / (hi - lo)


def _iou(a, b):
    """閉区間 a, b の IoU（重なり / 和）。離れていれば 0。長さ 0 同士が同じ点なら 1。"""
    inter = min(a[1], b[1]) - max(a[0], b[0])
    if inter < 0:
        return 0.0
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    if union == 0:
        return 1.0
    return inter / union


def _overlaps(a, b):
    """1 対 1 の候補にも分割 / 併合の候補にも入る「重なり」: 正の長さで重なる、または同じ点の長さ 0 同士。"""
    inter = min(a[1], b[1]) - max(a[0], b[0])
    return inter > 0 or (a[0] == a[1] == b[0] == b[1])


def _segments(ivs):
    """区間の列 → 互いに素な区間の列（重なる・接する区間は 1 つにまとめる）。"""
    out = []
    for lo, hi in sorted(ivs):
        if out and lo <= out[-1][1]:
            if hi > out[-1][1]:
                out[-1] = (out[-1][0], hi)
        else:
            out.append((lo, hi))
    return out


def _group_iou(segs, iv):
    """区間の集合 segs（互いに素）と区間 iv の IoU（集合の測度で測る: 隙間は数えない）。"""
    a = sum(hi - lo for lo, hi in segs)
    b = iv[1] - iv[0]
    inter = sum(max(0, min(hi, iv[1]) - max(lo, iv[0])) for lo, hi in segs)
    union = a + b - inter
    return inter / union if union > 0 else 0.0


def _dump(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, default=str)


# ---------------------------------------------------------------- 照合

def _resolve_groups(unpaired_g, unpaired_o, adj_g, adj_o, g_iv, o_iv, gkey, okey, iou_min):
    """対にならなかった正解 / 観測を、重なりで繋がる成分ごとに分割・併合へ振り分ける。
    戻り値: (splits = [(gi, [oi…])], merges = [(oi, [gi…])])。"""
    ug, uo = set(unpaired_g), set(unpaired_o)
    seen_g = set()
    splits, merges = [], []
    for g0 in sorted(unpaired_g, key=lambda i: gkey[i]):
        if g0 in seen_g:
            continue
        cg, co = set(), set()
        stack = [("g", g0)]
        while stack:
            kind, i = stack.pop()
            if kind == "g":
                if i in cg:
                    continue
                cg.add(i)
                stack.extend(("o", o) for o in adj_g[i] if o in uo and o not in co)
            else:
                if i in co:
                    continue
                co.add(i)
                stack.extend(("g", g) for g in adj_o[i] if g in ug and g not in cg)
        seen_g |= cg
        while True:
            best = None
            for g in sorted(cg, key=lambda i: gkey[i]):
                s = [o for o in adj_g[g] if o in co]
                if len(s) >= 2:
                    v = _group_iou(_segments([o_iv[o] for o in s]), g_iv[g])
                    if v >= iou_min:
                        k = (-v, g_iv[g][0], 0, gkey[g])
                        if best is None or k < best[0]:
                            best = (k, "split", g, s)
            for o in sorted(co, key=lambda i: okey[i]):
                s = [g for g in adj_o[o] if g in cg]
                if len(s) >= 2:
                    v = _group_iou(_segments([g_iv[g] for g in s]), o_iv[o])
                    if v >= iou_min:
                        k = (-v, o_iv[o][0], 1, okey[o])
                        if best is None or k < best[0]:
                            best = (k, "merge", o, s)
            if best is None:
                break
            _k, kind, anchor, s = best
            if kind == "split":
                cg.discard(anchor)
                co.difference_update(s)
                splits.append((anchor, sorted(s, key=lambda i: okey[i])))
            else:
                co.discard(anchor)
                cg.difference_update(s)
                merges.append((anchor, sorted(s, key=lambda i: gkey[i])))
    return splits, merges


def match(gt_sessions, obs_rows, iou_min=0.5, obs_end_offset_ms=0):
    """正解セッションの配列と ime_shadow 行の配列を照合する（決定的・入力の並びに依らない）。

    gt_sessions: sessions.json の definitions[<定義>] の中身（配列）。obs_rows: ime_shadow 行の配列。
    戻り値は {"pairs", "split", "merge", "miss", "false_pos"}（モジュールの docstring を参照）。
    """
    _check_iou_min(iou_min)
    if not _is_int(obs_end_offset_ms):
        raise ValueError("obs_end_offset_ms は整数（ms）")
    gts, obs = list(gt_sessions), list(obs_rows)
    g_iv = [gt_interval(s, "gt_sessions[%d]" % i) for i, s in enumerate(gts)]
    o_iv = [obs_interval(r, obs_end_offset_ms, "obs_rows[%d]" % i) for i, r in enumerate(obs)]
    gkey = [(g_iv[i][0], g_iv[i][1], _dump(gts[i])) for i in range(len(gts))]
    okey = [(o_iv[i][0], o_iv[i][1], _dump(obs[i])) for i in range(len(obs))]

    order = sorted(range(len(obs)), key=lambda i: o_iv[i][0])
    starts = [o_iv[i][0] for i in order]
    max_len = max((hi - lo for lo, hi in o_iv), default=0)
    adj_g = [[] for _ in gts]
    adj_o = [[] for _ in obs]
    cand = []
    for gi, giv in enumerate(g_iv):
        a = bisect_left(starts, giv[0] - max_len)
        b = bisect_right(starts, giv[1])
        for k in range(a, b):
            oi = order[k]
            if not _overlaps(giv, o_iv[oi]):
                continue
            adj_g[gi].append(oi)
            adj_o[oi].append(gi)
            v = _iou(giv, o_iv[oi])
            if v >= iou_min:
                cand.append((-v, gkey[gi], okey[oi], gi, oi))
    cand.sort()
    paired_g, paired_o, pairs = set(), set(), []
    for negv, _gk, _ok, gi, oi in cand:
        if gi in paired_g or oi in paired_o:
            continue
        paired_g.add(gi)
        paired_o.add(oi)
        pairs.append((gi, oi, -negv))

    unpaired_g = [i for i in range(len(gts)) if i not in paired_g]
    unpaired_o = [i for i in range(len(obs)) if i not in paired_o]
    splits, merges = _resolve_groups(unpaired_g, unpaired_o, adj_g, adj_o, g_iv, o_iv, gkey, okey, iou_min)
    used_g = set(g for g, _ in splits) | set(g for _, gl in merges for g in gl)
    used_o = set(o for _, ol in splits for o in ol) | set(o for o, _ in merges)

    pairs.sort(key=lambda p: (gkey[p[0]], okey[p[1]]))
    splits.sort(key=lambda p: gkey[p[0]])
    merges.sort(key=lambda p: okey[p[0]])
    miss = sorted((i for i in unpaired_g if i not in used_g), key=lambda i: gkey[i])
    false_pos = sorted((i for i in unpaired_o if i not in used_o), key=lambda i: okey[i])
    return {
        "pairs": [{"gt": gts[g], "obs": obs[o], "iou": v} for g, o, v in pairs],
        "split": [{"gt": gts[g], "obs": [obs[o] for o in ol]} for g, ol in splits],
        "merge": [{"obs": obs[o], "gt": [gts[g] for g in gl]} for o, gl in merges],
        "miss": [gts[i] for i in miss],
        "false_pos": [obs[i] for i in false_pos],
    }


def recount_split_merge(result, theta=0.5, obs_end_offset_ms=0):
    """Second pass over match()'s leftover items for split_rate / merge_rate (decision 38 follow-up).

    The primary 1:1 pairing in match() is never revisited here. This function only looks for extra
    evidence among the items match() already left in "false_pos" / "miss":
      - a false_pos row whose own length has a fraction >= theta inside an already-paired ground-truth
        session's interval is recounted as evidence that session was split;
      - a miss session whose own length has a fraction >= theta inside an already-paired observation's
        interval is recounted as evidence that observation was a merge.
    Each leftover item is attributed to at most one paired counterpart: the one with the largest covered
    fraction (ties broken by the counterpart's start time, then end time, then content, so the result does
    not depend on input order).

    Returns {"split": [{"gt", "obs", "frac"}], "merge": [{"gt", "obs", "frac"}]}. "gt" / "obs" here refer to
    the already-paired session in "split" entries but to the leftover (miss) session in "merge" entries; see
    detection_metrics() for how these feed split_rate / merge_rate and the n_fp_as_split / n_miss_as_merge
    breakdowns.
    """
    _check_theta(theta)
    paired = [(gt_interval(p["gt"], "pairs[].gt"), p["gt"], obs_interval(p["obs"], obs_end_offset_ms, "pairs[].obs"), p["obs"])
              for p in result["pairs"]]

    split = []
    for row in result["false_pos"]:
        oiv = obs_interval(row, obs_end_offset_ms, "false_pos[]")
        best = None
        for giv, gt, _oiv2, _obs2 in paired:
            frac = _covered_frac(oiv, giv)
            if frac >= theta:
                key = (-frac, giv[0], giv[1], _dump(gt))
                if best is None or key < best[0]:
                    best = (key, gt, frac)
        if best is not None:
            split.append({"gt": best[1], "obs": row, "frac": best[2]})

    merge = []
    for s in result["miss"]:
        giv = gt_interval(s, "miss[]")
        best = None
        for _giv2, _gt2, oiv, obs in paired:
            frac = _covered_frac(giv, oiv)
            if frac >= theta:
                key = (-frac, oiv[0], oiv[1], _dump(obs))
                if best is None or key < best[0]:
                    best = (key, obs, frac)
        if best is not None:
            merge.append({"gt": s, "obs": best[1], "frac": best[2]})

    split.sort(key=lambda x: (gt_interval(x["gt"]), _dump(x["gt"]), obs_interval(x["obs"], obs_end_offset_ms), _dump(x["obs"])))
    merge.sort(key=lambda x: (gt_interval(x["gt"]), _dump(x["gt"]), obs_interval(x["obs"], obs_end_offset_ms), _dump(x["obs"])))
    return {"split": split, "merge": merge}


# ---------------------------------------------------------------- 検出の指標

def _prop(x, n):
    lo, hi = stats.wilson(x, n)
    return {"x": x, "n": n, "value": (x / n if n else None), "lo": lo, "hi": hi}


def _f1_prop(pairs, n_gt, n_obs):
    """F1 = 2 * pairs / (n_gt + n_obs). Unlike the other rates here, this ratio counts each matched pair
    twice (once toward the ground-truth side, once toward the observation side), so its two "successes" are
    perfectly correlated rather than independent Bernoulli trials. Feeding stats.wilson(2*pairs, n_gt+n_obs)
    would treat them as independent and understate the true uncertainty, so lo/hi are left None here
    (decision 38 follow-up) instead of being reported as a Wilson interval that is not one."""
    n = n_gt + n_obs
    return {"x": 2 * pairs, "n": n, "value": (2.0 * pairs / n if n else None), "lo": None, "hi": None,
            "note": "interval intentionally omitted: the doubled pair count is not an independent-trials proportion"}


def _metrics_row(label, c, names):
    n_gt = c["pairs"] + c["split_gt"] + c["merge_gt"] + c["miss"]
    n_obs = c["pairs"] + c["split_obs"] + c["merge_obs"] + c["fp"]
    if names and isinstance(label, tuple) and len(names) == len(label):
        shown = dict(zip(names, label))
    elif isinstance(label, tuple):
        shown = list(label)
    else:
        shown = label
    return {
        "stratum": shown, "n_gt": n_gt, "n_obs": n_obs, "n_pairs": c["pairs"],
        "n_split_gt": c["split_gt"], "n_split_obs": c["split_obs"],
        "n_merge_obs": c["merge_obs"], "n_merge_gt": c["merge_gt"],
        "n_miss": c["miss"], "n_false_pos": c["fp"],
        "n_split_gt_recount": c["split_gt_recount"], "n_fp_as_split": c["fp_as_split"],
        "n_merge_obs_recount": c["merge_obs_recount"], "n_miss_as_merge": c["miss_as_merge"],
        "precision": _prop(c["pairs"], n_obs),
        "recall": _prop(c["pairs"], n_gt),
        "f1": _f1_prop(c["pairs"], n_gt, n_obs),
        "split_rate": _prop(c["split_gt"] + c["split_gt_recount"], n_gt),
        "merge_rate": _prop(c["merge_obs"] + c["merge_obs_recount"], n_obs),
        "miss_rate": _prop(c["miss"], n_gt),
        "false_pos_rate": _prop(c["fp"], n_obs),
    }


def detection_metrics(result, strata=None, theta=0.5, obs_end_offset_ms=0):
    """match() の戻り値 → 層ごとの検出の指標（モジュールの docstring を参照）。

    strata: None（全部で 1 層 "all"）または {"gt": セッション → ラベル, "obs": 観測行 → ラベル,
    "names": [ラベルの各要素の名前]（任意）}。ラベルはハッシュできる値（タプル可）か None。
    対・分割・取り逃しは正解の層、併合は observed 行が先頭（最も早い）正解の層に数え、併合の各正解は
    それぞれ自分自身の層に数える（decision 38 follow-up）。偽検出は観測の層に数える。

    theta / obs_end_offset_ms: passed straight through to recount_split_merge() to compute the
    n_split_gt_recount / n_merge_obs_recount / n_fp_as_split / n_miss_as_merge fields and split_rate /
    merge_rate. They do not affect n_gt, n_obs, n_pairs, precision, recall or F1.
    """
    if strata is None:
        def gl(_s):
            return "all"
        ol = gl
        names = None
    else:
        gl, ol, names = strata["gt"], strata["obs"], strata.get("names")
    counts = {}

    def bucket(label):
        if label not in counts:
            counts[label] = {"pairs": 0, "split_gt": 0, "split_obs": 0, "merge_obs": 0, "merge_gt": 0, "miss": 0, "fp": 0,
                              "split_gt_recount": 0, "fp_as_split": 0, "merge_obs_recount": 0, "miss_as_merge": 0}
        return counts[label]

    for p in result["pairs"]:
        bucket(gl(p["gt"]))["pairs"] += 1
    for sp in result["split"]:
        c = bucket(gl(sp["gt"]))
        c["split_gt"] += 1
        c["split_obs"] += len(sp["obs"])
    for mg in result["merge"]:
        bucket(gl(mg["gt"][0]))["merge_obs"] += 1
        for g in mg["gt"]:
            bucket(gl(g))["merge_gt"] += 1
    for s in result["miss"]:
        bucket(gl(s))["miss"] += 1
    for r in result["false_pos"]:
        bucket(ol(r))["fp"] += 1

    rc = recount_split_merge(result, theta, obs_end_offset_ms)
    split_recount_seen = {}
    for e in rc["split"]:
        bucket(ol(e["obs"]))["fp_as_split"] += 1
        st = gl(e["gt"])
        bucket(st)
        split_recount_seen.setdefault(st, set()).add(_dump(e["gt"]))
    merge_recount_seen = {}
    for e in rc["merge"]:
        st = gl(e["gt"])
        bucket(st)["miss_as_merge"] += 1
        bucket(st)
        merge_recount_seen.setdefault(st, set()).add(_dump(e["obs"]))
    for st, s in split_recount_seen.items():
        bucket(st)["split_gt_recount"] = len(s)
    for st, s in merge_recount_seen.items():
        bucket(st)["merge_obs_recount"] = len(s)

    labels = sorted(counts, key=lambda L: (L is None, _dump(L)))
    return [_metrics_row(L, counts[L], names) for L in labels]


# ---------------------------------------------------------------- 入力の読み取り（CLI）

def _no_float(_s):
    raise InputError("小数・指数表記の数は読まない")


def _no_constant(_s):
    raise InputError("NaN / Infinity は読まない")


def _no_dup(pairs, where):
    out = {}
    for k, v in pairs:
        if k in out:
            raise InputError("%s: 同じキーが 2 回ある" % where)
        out[k] = v
    return out


def _json_loads(text, where, allow_float):
    try:
        return json.loads(text, parse_float=(None if allow_float else _no_float), parse_constant=_no_constant,
                          object_pairs_hook=lambda pairs: _no_dup(pairs, where))
    except InputError:
        raise
    except (ValueError, RecursionError):
        raise InputError("%s: JSON として読めない" % where)


def _decode(data, what):
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("%s: UTF-8 として読めない" % what)


def _jsonl(data, what):
    out = []
    for n, raw in enumerate(_decode(data, what).split("\n"), 1):
        raw = raw.rstrip("\r")
        if raw.strip():
            out.append((n, _json_loads(raw, "%s:%d" % (what, n), False)))
    return out


def parse_obs(data):
    """obs/1 → ime_shadow 行の配列（{"type","t","dwell_ms","nav","abandon"} だけ。key 行は読まない）。"""
    lines = _jsonl(data, "obs")
    if not lines:
        raise InputError("obs: 空のファイル")
    hdr = lines[0][1]
    if not (isinstance(hdr, dict) and hdr.get("type") == "meta" and hdr.get("format") == "obs/1"):
        raise InputError("obs: 1 行目が obs/1 のヘッダでない")
    rows = []
    for n, row in lines[1:]:
        if not isinstance(row, dict):
            raise InputError("obs:%d: オブジェクトでない" % n)
        if row.get("type") != "ime_shadow":
            continue
        t, d, nav, ab = row.get("t"), row.get("dwell_ms"), row.get("nav"), row.get("abandon")
        if not (_is_int(t) and _is_int(d) and _is_int(nav) and type(ab) is bool) or t < 0 or d < 0 or nav < 0:
            raise InputError("obs:%d: ime_shadow の t / dwell_ms / nav / abandon の型が違う" % n)
        rows.append({"type": "ime_shadow", "t": t, "dwell_ms": d, "nav": nav, "abandon": ab})
    return rows


def parse_plan_strata(data):
    """plan/1 → {"os", "sha256", "trials": {trial_id: {"block_id", "scenario", "speed"}}}（層の決定に要る欄だけ）。"""
    lines = _jsonl(data, "plan")
    if not lines:
        raise InputError("plan: 空のファイル")
    hdr = lines[0][1]
    if not (isinstance(hdr, dict) and hdr.get("kind") == "header" and hdr.get("format") == "plan/1"):
        raise InputError("plan: 1 行目が plan/1 のヘッダでない")
    if hdr.get("os") not in ("macos", "windows"):
        raise InputError("plan: ヘッダの os が macos / windows でない")
    trials = {}
    for n, row in lines[1:]:
        if not isinstance(row, dict) or row.get("kind") != "trial":
            continue
        tid, bid, sc, sp = row.get("trial_id"), row.get("block_id"), row.get("scenario"), row.get("speed")
        if not isinstance(tid, str) or not gt_sessions.TRIAL_ID_RE.fullmatch(tid):
            raise InputError("plan:%d: trial_id の形が違う" % n)
        if tid in trials:
            raise InputError("plan:%d: trial_id が重複している" % n)
        if not _is_int(bid) or not isinstance(sc, str) or not SCENARIO_RE.fullmatch(sc) or sp not in SPEEDS:
            raise InputError("plan:%d: block_id / scenario / speed の形が違う" % n)
        trials[tid] = {"block_id": bid, "scenario": sc, "speed": sp}
    return {"os": hdr["os"], "sha256": hashlib.sha256(data).hexdigest(), "trials": trials}


def parse_sessions(data, definition):
    """sessions.json → (src, definition のセッションの配列, excluded の配列)。★ 判断 28 の欄が無ければ拒否する。"""
    obj = _json_loads(_decode(data, "sessions"), "sessions", True)
    if not isinstance(obj, dict) or not isinstance(obj.get("definitions"), dict):
        raise InputError("sessions: definitions が無い（gt_sessions.py の出力でない）")
    if definition not in DEFINITIONS:
        raise InputError("definition は all / macos_def / windows_def")
    sess = obj["definitions"].get(definition)
    if sess is None:
        raise InputError("sessions: definitions.%s が null（この src では作れない定義）" % definition)
    if not isinstance(sess, list):
        raise InputError("sessions: definitions.%s が配列でない" % definition)
    for i, s in enumerate(sess):
        if not isinstance(s, dict) or not isinstance(s.get("excluded_by"), list):
            raise InputError("sessions: definitions.%s[%d] に excluded_by が無い（古い出力・gt_sessions.py で作り直す）" % (definition, i))
        if not _is_int(s.get("start_wall_ms")) or not (s.get("end_wall_ms") is None or _is_int(s.get("end_wall_ms"))):
            raise InputError("sessions: definitions.%s[%d] の start_wall_ms / end_wall_ms の型が違う" % (definition, i))
        nswo = s.get("n_start_while_open")
        if not (_is_int(nswo) and nswo >= 0):
            raise InputError("sessions: definitions.%s[%d] に n_start_while_open (0 以上の整数) が無い（古い出力・gt_sessions.py で作り直す）" % (definition, i))
    exc = obj.get("excluded")
    if not isinstance(exc, list) or any(
            not isinstance(e, dict) or not isinstance(e.get("type"), str) or not isinstance(e.get("trial_ids"), list)
            for e in exc):
        raise InputError("sessions: excluded の各要素に type と trial_ids が要る（古い出力・gt_sessions.py で作り直す）")
    return obj.get("src"), sess, exc


def parse_config(data):
    """設定 JSON（None なら既定）→ {"iou_min", "obs_end_offset_ms", "theta", "clock_offsets_ms": {int: int},
    "cell", "drop_start_while_open"}。"""
    cfg = {"iou_min": 0.5, "obs_end_offset_ms": 0, "theta": 0.5, "clock_offsets_ms": {}, "cell": None,
           "drop_start_while_open": False}
    if data is None:
        return cfg
    obj = _json_loads(_decode(data, "config"), "config", True)
    if not isinstance(obj, dict):
        raise InputError("config: 最上位はオブジェクト")
    for k, v in obj.items():
        if k.startswith("_"):
            continue
        if k == "iou_min":
            try:
                _check_iou_min(v)
            except ValueError as e:
                raise InputError("config: %s" % e)
            cfg[k] = v
        elif k == "obs_end_offset_ms":
            if not _is_int(v):
                raise InputError("config: obs_end_offset_ms は整数")
            cfg[k] = v
        elif k == "theta":
            try:
                _check_theta(v)
            except ValueError as e:
                raise InputError("config: %s" % e)
            cfg[k] = v
        elif k == "clock_offsets_ms":
            if not isinstance(v, dict):
                raise InputError("config: clock_offsets_ms はオブジェクト（block_id → ms）")
            for bk, bv in v.items():
                if not re.fullmatch(r"[0-9]{1,9}", bk) or not _is_int(bv):
                    raise InputError("config: clock_offsets_ms は 10 進の block_id → 整数 ms")
                cfg[k][int(bk)] = bv
        elif k == "cell":
            if not isinstance(v, str) or not CELL_RE.fullmatch(v):
                raise InputError("config: cell は ^[A-Za-z0-9_.+-]{1,64}$")
            cfg[k] = v
        elif k == "drop_start_while_open":
            if type(v) is not bool:
                raise InputError("config: drop_start_while_open は真偽値")
            cfg[k] = v
        else:
            raise InputError("config: 未知のキー '%s'" % k)
    return cfg


def _block_windows(oracle):
    wins = {}
    for row in oracle["rows"]:
        b = row.get("block_id")
        if row.get("kind") == "block_begin" and _is_int(b):
            wins.setdefault(b, [row["t_wall_ms"], None])
        elif row.get("kind") == "block_end" and b in wins:
            wins[b][1] = row["t_wall_ms"]
    last = oracle["rows"][-1]["t_wall_ms"] if oracle["rows"] else 0
    for w in wins.values():
        if w[1] is None:
            w[1] = last
    return wins


def _assign_block(t, wins, offsets):
    """補正後の t が最も近い（区間の中なら距離 0）ブロック。同じ距離なら block_id の小さい方。"""
    best = None
    for b in sorted(wins):
        tc = t - offsets.get(b, 0)
        lo, hi = wins[b]
        d = max(0, lo - tc, tc - hi)
        if best is None or d < best[0]:
            best = (d, b)
    return None if best is None else best[1]


def _assign_trial(lo, hi, trials, begins):
    """区間と最大の重なりを持つ試行の trial_id（同点は先の試行）。無ければ None。trials は開始の昇順・互いに素。"""
    best, best_ov = None, 0
    i = bisect_right(begins, hi) - 1
    while i >= 0:
        tr = trials[i]
        if tr["end_wall_ms"] < lo:
            break
        ov = min(hi, tr["end_wall_ms"]) - max(lo, tr["begin_wall_ms"])
        point = lo == hi and tr["begin_wall_ms"] <= lo <= tr["end_wall_ms"]
        if (ov > 0 and ov >= best_ov) or (best is None and point):
            best, best_ov = tr, max(ov, 0)
        i -= 1
    return None if best is None else best["trial_id"]


def evaluate(sessions_bytes, definition, obs_bytes, plan_bytes, oracle_bytes, config_bytes=None):
    """CLI の中身（バイト列 → 出力の辞書）。同じ入力なら同じ辞書。"""
    src, sess, excluded = parse_sessions(sessions_bytes, definition)
    cfg = parse_config(config_bytes)
    plan = parse_plan_strata(plan_bytes)
    oracle = gt_sessions.parse_oracle(oracle_bytes)
    want = oracle["plan_sha256"]
    if not isinstance(want, str) or want.lower() != plan["sha256"]:
        raise InputError("plan: SHA-256 が oracle のヘッダの plan_sha256 と違う（対応しない計画）")
    rows = parse_obs(obs_bytes)
    cell = cfg["cell"] if cfg["cell"] is not None else plan["os"]
    off_end = cfg["obs_end_offset_ms"]

    offsets = cfg["clock_offsets_ms"]
    wins = _block_windows(oracle)
    for b in offsets:
        if b not in wins:
            raise InputError("config: clock_offsets_ms の block_id %d が oracle に無い" % b)
    # "t" is never rewritten (always the raw observation time); the ground-truth-clock time always goes into
    # the new "t_gt_clock" field, whether or not that block had a configured offset (decision 38 follow-up).
    uncorrected_blocks = sorted(b for b in wins if b not in offsets)
    corrected = [dict(r, t_gt_clock=r["t"] - offsets.get(_assign_block(r["t"], wins, offsets), 0)) for r in rows]

    trials = sorted(oracle["trials"], key=lambda t: (t["begin_wall_ms"], t["end_wall_ms"]))
    begins = [t["begin_wall_ms"] for t in trials]
    trial_types = {}
    for e in excluded:
        for tid in e["trial_ids"]:
            trial_types.setdefault(tid, set()).add(e["type"])

    def bump(d, reasons):
        for r in reasons:
            d[r] = d.get(r, 0) + 1

    gt_reasons, kept_gt, n_gt_dropped = {}, [], 0
    for s in sess:
        reasons = set(s["excluded_by"]) | trial_types.get(s.get("trial_id"), set())
        if s["end_wall_ms"] is None:
            reasons.add("open_at_end")
        if cfg["drop_start_while_open"] and s["n_start_while_open"] > 0:
            reasons.add("start_while_open")
        if reasons:
            n_gt_dropped += 1
            bump(gt_reasons, reasons)
        else:
            kept_gt.append(s)
    obs_reasons, kept_obs, n_obs_dropped, obs_tid = {}, [], 0, {}
    for r in corrected:
        lo, hi = obs_interval(r, off_end)
        tid = _assign_trial(lo, hi, trials, begins)
        reasons = trial_types.get(tid, set())
        if reasons:
            n_obs_dropped += 1
            bump(obs_reasons, reasons)
        else:
            kept_obs.append(r)
            obs_tid[id(r)] = tid

    result = match(kept_gt, kept_obs, iou_min=cfg["iou_min"], obs_end_offset_ms=off_end)

    def label(tid):
        info = plan["trials"].get(tid)
        return (cell, info["scenario"], info["speed"]) if info else (cell, None, None)

    strata = {"gt": lambda s: label(s.get("trial_id")), "obs": lambda r: label(obs_tid.get(id(r))),
              "names": ["cell", "scenario", "speed"]}

    # Diagnostic only (decision 28 / 38 follow-up): counts, per stratum, of kept ground-truth sessions with
    # n_start_while_open > 0. Not used to exclude anything unless config.drop_start_while_open is true.
    swo_counts = {}
    for s in kept_gt:
        if s["n_start_while_open"] > 0:
            lbl = label(s.get("trial_id"))
            swo_counts[lbl] = swo_counts.get(lbl, 0) + 1
    swo_labels = sorted(swo_counts, key=lambda L: (L is None, _dump(L)))
    swo_by_stratum = [{"stratum": dict(zip(["cell", "scenario", "speed"], L)), "n": swo_counts[L]} for L in swo_labels]

    theta = cfg["theta"]
    return {
        "src": src,
        "definition": definition,
        "config": {"iou_min": cfg["iou_min"], "obs_end_offset_ms": off_end, "theta": theta,
                   "clock_offsets_ms": dict((str(b), v) for b, v in sorted(offsets.items())), "cell": cell,
                   "drop_start_while_open": cfg["drop_start_while_open"], "uncorrected_blocks": uncorrected_blocks},
        "inputs_sha256": {
            "sessions": hashlib.sha256(sessions_bytes).hexdigest(), "obs": hashlib.sha256(obs_bytes).hexdigest(),
            "plan": plan["sha256"], "oracle": hashlib.sha256(oracle_bytes).hexdigest(),
            "config": None if config_bytes is None else hashlib.sha256(config_bytes).hexdigest()},
        "input": {"n_gt": len(sess), "n_obs": len(rows)},
        "excluded": {
            "gt": {"n": n_gt_dropped, "by_reason": gt_reasons},
            "obs": {"n": n_obs_dropped, "by_reason": obs_reasons},
            "trials": {"n": len(trial_types), "by_type": _count_types(excluded)}},
        "used": {"n_gt": len(kept_gt), "n_obs": len(kept_obs)},
        "diagnostics": {"start_while_open": {"n": sum(swo_counts.values()), "by_stratum": swo_by_stratum}},
        "metrics": {"by_stratum": detection_metrics(result, strata, theta, off_end),
                    "pooled": detection_metrics(result, None, theta, off_end)[0] if (kept_gt or kept_obs) else None,
                    "note": "pooled は層の重みを付けない件数の合計（合成入力に自然な混合比は無い）。主推定値は層別"},
        "matching": result,
    }


def _count_types(excluded):
    by = {}
    for e in excluded:
        by.setdefault(e["type"], set()).update(e["trial_ids"])
    return dict((k, len(v)) for k, v in sorted(by.items()))


def render(out):
    """出力のバイト列（LF・UTF-8・BOM なし・キー順固定）。"""
    return (json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _read(path, what):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise InputError("%s: 開けない（%s）" % (what, type(e).__name__))


def _same_file(a, b):
    try:
        return os.path.exists(a) and os.path.exists(b) and os.path.samefile(a, b)
    except OSError:
        return False


def _write_atomic(path, data):
    d = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".match_tmp_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------- selftest

def _gt(tid, lo, hi, **kw):
    d = {"trial_id": tid, "start_wall_ms": lo, "end_wall_ms": hi, "start_mono_ns": lo * 1000000,
         "end_mono_ns": None if hi is None else hi * 1000000, "outcome": "commit", "candidate_shown": None, "nav_true": 0,
         "nav_true_cand": None, "excluded_by": [], "n_start_while_open": 0}
    d.update(kw)
    return d


def _ob(lo, hi, nav=0, abandon=False):
    """区間 [lo, hi] を既定（offset 0）で返す観測行。"""
    return {"type": "ime_shadow", "t": hi, "dwell_ms": hi - lo, "nav": nav, "abandon": abandon}


def _world(n, seed):
    """疎な合成の正解: 長さ 800〜2500 ms・間隔 30〜120 s（偶然の一致が起きにくい）。"""
    import random
    rng = random.Random(seed)
    t, out = 1700000000000, []
    for i in range(n):
        t += 30000 + int(rng.random() * 90001)
        length = 800 + int(rng.random() * 1701)
        out.append(_gt("t%05d" % (i + 1), t, t + length))
        t += length
    return out


def _shuffled(xs, seed):
    import random
    rng = random.Random(seed)
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def _sizes(r):
    return (len(r["pairs"]), len(r["split"]), len(r["merge"]), len(r["miss"]), len(r["false_pos"]))


def _case_five_types():
    f = []
    gts = [_gt("t1", 1000, 2000), _gt("t2", 10000, 13000), _gt("t3", 20000, 21000), _gt("t3", 21500, 22500),
           _gt("t4", 30000, 31000)]
    obs = [_ob(1000, 2000), _ob(10000, 11000), _ob(11000, 12000), _ob(12000, 13000), _ob(20000, 22500),
           _ob(40000, 41000)]
    r = match(gts, obs)
    if _sizes(r) != (1, 1, 1, 1, 1):
        f.append("5 型の件数が (対, 分割, 併合, 取り逃し, 偽検出) = (1,1,1,1,1) でない: %r" % (_sizes(r),))
        return f
    if r["pairs"][0]["gt"] is not gts[0] or r["pairs"][0]["obs"] is not obs[0] or r["pairs"][0]["iou"] != 1.0:
        f.append("完全一致の対が違う: %r" % (r["pairs"][0],))
    if r["split"][0]["gt"] is not gts[1] or r["split"][0]["obs"] != obs[1:4]:
        f.append("分割（3 断片・時刻順）が違う: %r" % (r["split"][0],))
    if r["merge"][0]["obs"] is not obs[4] or r["merge"][0]["gt"] != [gts[2], gts[3]]:
        f.append("併合（観測 1 件に正解 2 件・時刻順）が違う: %r" % (r["merge"][0],))
    if r["miss"] != [gts[4]]:
        f.append("取り逃しが違う: %r" % (r["miss"],))
    if r["false_pos"] != [obs[5]]:
        f.append("偽検出が違う: %r" % (r["false_pos"],))
    # 部分的な重なり: IoU = 800 / 1200
    r2 = match([_gt("t1", 50000, 51000)], [_ob(50200, 51200)])
    if _sizes(r2) != (1, 0, 0, 0, 0) or abs(r2["pairs"][0]["iou"] - 800.0 / 1200.0) > 1e-12:
        f.append("部分的な重なりの IoU が 800/1200 でない: %r" % (r2,))
    if _sizes(match([], [])) != (0, 0, 0, 0, 0):
        f.append("空の入力が空の結果にならない")
    return f


def _case_definition_properties():
    """定義の性質（docstring の ⚠️）: 直さず固定する。2 断片の隣接した分割は 対 + 偽検出、隙間のある 2 断片は分割。"""
    f = []
    r = match([_gt("t1", 0, 1000)], [_ob(0, 600), _ob(600, 1000)])
    if _sizes(r) != (1, 0, 0, 0, 1):
        f.append("隣り合う 2 断片（60% + 40%）が 対 1 + 偽検出 1 にならない: %r" % (_sizes(r),))
    r = match([_gt("t1", 0, 1000)], [_ob(0, 400), _ob(600, 1000)])
    if _sizes(r) != (0, 1, 0, 0, 0):
        f.append("隙間のある 2 断片（各 40%・和集合 80%）が分割にならない: %r" % (_sizes(r),))
    r = match([_gt("t1", 0, 3000), _gt("t2", 3000, 4000)], [_ob(0, 4000)])
    if _sizes(r) != (1, 0, 0, 1, 0):
        f.append("不均衡な併合（一方が 75%）が 対 1 + 取り逃し 1 にならない: %r" % (_sizes(r),))
    # 和集合の IoU は、区間の外へはみ出す分を「和」に数える（内側に収まる断片だけを試すと交わりを測り損ねる）
    #   断片 [-600,300] + [300,600]: 和集合 [-600,600]（1200）・交わり 600・和 1600 → 0.375 < 0.5 → 分割にならない
    r = match([_gt("t1", 0, 1000)], [_ob(-600, 300), _ob(300, 600)])
    if _sizes(r) != (0, 0, 0, 1, 2):
        f.append("はみ出す 2 断片（和集合の IoU 0.375）が 取り逃し 1 + 偽検出 2 にならない: %r" % (_sizes(r),))
    #   断片 [-100,300] + [300,600] + [600,1100]: 交わり 1000・和 1200 → 0.833 ≥ 0.5 → 分割（はみ出しは許容）
    r = match([_gt("t1", 0, 1000)], [_ob(-100, 300), _ob(300, 600), _ob(600, 1100)])
    if _sizes(r) != (0, 1, 0, 0, 0):
        f.append("少しはみ出す 3 断片（和集合の IoU 0.833）が分割にならない: %r" % (_sizes(r),))
    #   併合でも同じ: 観測 [0,1000] に 正解 [-800,300] + [300,600]: 交わり 600・和 1800 → 0.333 < 0.5 → 併合にならない
    r = match([_gt("t1", -800, 300), _gt("t2", 300, 600)], [_ob(0, 1000)])
    if _sizes(r) != (0, 0, 0, 2, 1):
        f.append("はみ出す正解 2 件（和集合の IoU 0.333）が 取り逃し 2 + 偽検出 1 にならない: %r" % (_sizes(r),))
    # 断片が多いほど、1 つが対になる余地が減る（3 断片は各 1/3 で単独では対にならない）
    r = match([_gt("t1", 0, 1200)], [_ob(0, 400), _ob(400, 800), _ob(800, 1200)])
    if _sizes(r) != (0, 1, 0, 0, 0):
        f.append("3 断片が分割にならない: %r" % (_sizes(r),))
    # 短いセッションは時刻のずれで対にならなくなる（長さ L が対になるのは平行移動が L/3 以下）
    r = match([_gt("t1", 0, 150)], [_ob(60, 210)])
    if _sizes(r) != (0, 0, 0, 1, 1):
        f.append("150 ms のセッションを 60 ms ずらしたら 取り逃し + 偽検出になるはず（L/3 = 50）: %r" % (_sizes(r),))
    return f


def _case_iou_boundary():
    f = []
    if _sizes(match([_gt("t1", 0, 300)], [_ob(100, 400)])) != (1, 0, 0, 0, 0):
        f.append("IoU ちょうど 0.5（200/400）は対になる（>=）")
    if _sizes(match([_gt("t1", 0, 300)], [_ob(101, 401)])) != (0, 0, 0, 1, 1):
        f.append("IoU 199/401 < 0.5 は対にならない")
    if _sizes(match([_gt("t1", 0, 300)], [_ob(50, 350)], iou_min=0.7)) != (1, 0, 0, 0, 0):
        f.append("iou_min = 0.7 で IoU 250/350 = 0.714 が対にならない")
    if _sizes(match([_gt("t1", 0, 300)], [_ob(60, 360)], iou_min=0.7)) != (0, 0, 0, 1, 1):
        f.append("iou_min = 0.7 で IoU 240/360 = 0.667 が対になった")
    # 長さ 0 は同じ点の長さ 0 とだけ対になる
    if _sizes(match([_gt("t1", 500, 500)], [_ob(500, 500)])) != (1, 0, 0, 0, 0):
        f.append("同じ点の長さ 0 同士が対にならない")
    if _sizes(match([_gt("t1", 500, 500)], [_ob(0, 1000)])) != (0, 0, 0, 1, 1):
        f.append("長さ 0 の正解が長い観測の中の点で対になった")
    return f


def _case_tie_determinism():
    f = []
    # 同じ区間・同じ IoU の観測 2 件: 並びを逆にしても同じ結果（内容の昇順で先に対になる）
    g = [_gt("t1", 0, 1000)]
    a, b = _ob(0, 1000, nav=1), _ob(0, 1000, nav=2)
    r1, r2 = match(g, [a, b]), match(g, [b, a])
    if _dump(r1) != _dump(r2) or r1["pairs"][0]["obs"]["nav"] != 1 or r1["false_pos"] != [b]:
        f.append("同点（同じ区間の観測 2 件）が入力の並びに依存する / 先に対になるのが内容の昇順でない")
    # 同じ区間の正解 2 件・観測 1 件
    g2 = [_gt("t1", 0, 1000), _gt("t2", 0, 1000)]
    r1, r2 = match(g2, [_ob(0, 1000)]), match(list(reversed(g2)), [_ob(0, 1000)])
    if _dump(r1) != _dump(r2) or r1["pairs"][0]["gt"]["trial_id"] != "t1":
        f.append("同点（同じ区間の正解 2 件）が入力の並びに依存する")
    # IoU が同点（1/3 ずつ）で開始時刻が違う 2 件の正解: 開始の早い方が先に対になる
    o = [_ob(1000, 2000)]
    g3 = [_gt("t2", 1500, 2500), _gt("t1", 500, 1500)]
    r = match(g3, o, iou_min=0.3)
    if _sizes(r) != (1, 0, 0, 1, 0) or r["pairs"][0]["gt"]["trial_id"] != "t1":
        f.append("IoU 同点のとき開始時刻の昇順で対にならない: %r" % (r["pairs"],))
    # 並べ替えても結果が変わらない（対・分割・併合・取り逃し・偽検出が混ざった入力）
    gts = _world(40, 3)
    obs = [_ob(g["start_wall_ms"] + 30, g["end_wall_ms"] + 30) for g in gts[:30]]
    obs += [_ob(gts[30]["start_wall_ms"], gts[30]["start_wall_ms"] + 300), _ob(gts[30]["start_wall_ms"] + 400, gts[30]["end_wall_ms"])]
    obs += [_ob(gts[35]["start_wall_ms"] - 2000, gts[36]["end_wall_ms"] + 2000)]
    base = _dump(match(gts, obs))
    for seed in range(1, 6):
        if _dump(match(_shuffled(gts, seed), _shuffled(obs, seed + 100))) != base:
            f.append("入力の並びを変えると結果が変わる（seed %d）" % seed)
            break
    return f


def _case_positive_control():
    """★ 陽性対照: 観測を 1 行消す・1 行をずらすと指標が悪化する。"""
    f = []
    gts = _world(60, 7)
    obs = [_ob(g["start_wall_ms"] + (i % 7) * 20 - 60, g["end_wall_ms"] + (i % 7) * 20 - 60) for i, g in enumerate(gts)]
    base = detection_metrics(match(gts, obs))[0]
    if base["recall"]["x"] != 60 or base["precision"]["x"] != 60 or base["n_miss"] or base["n_false_pos"]:
        f.append("基準（小さなずれだけ）が全部対にならない: %r" % (base,))
    dropped = detection_metrics(match(gts, obs[:20] + obs[21:]))[0]
    if not (dropped["recall"]["x"] == 59 and dropped["n_miss"] == 1 and dropped["recall"]["value"] < base["recall"]["value"]):
        f.append("観測を 1 行消しても再現率が下がらない: %r" % (dropped["recall"],))
    if dropped["precision"]["value"] != 1.0:
        f.append("観測を 1 行消しても適合率は 1 のはず（偽検出は増えない）")
    moved = list(obs)
    moved[20] = _ob(obs[20]["t"] - obs[20]["dwell_ms"] + 2000, obs[20]["t"] + 2000)
    r = match(gts, moved)
    m = detection_metrics(r)[0]
    if not (m["n_pairs"] == 59 and m["n_miss"] == 1 and m["n_false_pos"] == 1):
        f.append("1 行を 2 s ずらしたら 対が 1 つ減り 取り逃し 1・偽検出 1 になるはず: %r" % (_sizes(r),))
    if not (m["recall"]["value"] < base["recall"]["value"] and m["precision"]["value"] < base["precision"]["value"]
            and m["f1"]["value"] < base["f1"]["value"]):
        f.append("ずらしても 再現率・適合率・F1 が下がらない")
    if not (m["recall"]["hi"] < 1.0 or m["recall"]["lo"] < base["recall"]["lo"]):
        f.append("区間が悪化を反映しない")
    return f


def _case_negative_control():
    """★ 陰性対照: 観測を 60 s ずらす・時刻をシャッフルすると、対の数が偶然水準（ほぼ 0）になる。"""
    f = []
    n = 300
    gts = _world(n, 11)
    obs = [_ob(g["start_wall_ms"], g["end_wall_ms"]) for g in gts]
    if detection_metrics(match(gts, obs))[0]["n_pairs"] != n:
        f.append("基準（ずれなし）が全部対にならない")
    shifted = [dict(o, t=o["t"] + 60000) for o in obs]
    ms = detection_metrics(match(gts, shifted))[0]
    if ms["n_pairs"] > 0.05 * n:
        f.append("60 s ずらしても対が偶然水準（<= 5%%）に落ちない: %d / %d" % (ms["n_pairs"], n))
    # ⚠️ 時刻を行の間で並べ替えるだけでは、終端の時刻の集合が正解と揃ったままで対が残る（実測: 86%）。
    # 偶然水準を見るには、観測の時刻を記録の全区間へ一様に置き直す。
    import random
    rng = random.Random(5)
    lo_span, hi_span = gts[0]["start_wall_ms"], gts[-1]["end_wall_ms"]
    scrambled = [dict(o, t=lo_span + o["dwell_ms"] + int(rng.random() * (hi_span - lo_span))) for o in obs]
    mz = detection_metrics(match(gts, scrambled))[0]
    if mz["n_pairs"] > 0.05 * n:
        f.append("時刻をシャッフルしても対が偶然水準（<= 5%%）に落ちない: %d / %d" % (mz["n_pairs"], n))
    if not (ms["recall"]["hi"] < 0.15 and mz["recall"]["hi"] < 0.15):
        f.append("陰性対照の再現率の区間の上限が偶然水準を示さない: %r %r" % (ms["recall"], mz["recall"]))
    return f


def _case_byte_identical():
    f = []
    gts = _world(120, 21)
    obs = [_ob(g["start_wall_ms"] + 25, g["end_wall_ms"] + 25) for g in gts[:100]] + [_ob(5, 900)]
    outs = []
    for _ in range(2):
        r = match(gts, obs)
        blob = json.dumps({"r": r, "m": detection_metrics(r)}, sort_keys=True, ensure_ascii=False)
        outs.append(hashlib.sha256(blob.encode("utf-8")).hexdigest())
    if outs[0] != outs[1]:
        f.append("同じ入力で結果がバイト一致しない")
    return f


def _case_metrics():
    f = []
    gts = [_gt("t1", 1000, 2000), _gt("t2", 10000, 13000), _gt("t3", 20000, 21000), _gt("t3", 21500, 22500),
           _gt("t4", 30000, 31000)]
    obs = [_ob(1000, 2000), _ob(10000, 11000), _ob(11000, 12000), _ob(12000, 13000), _ob(20000, 22500),
           _ob(40000, 41000)]
    r = match(gts, obs)
    m = detection_metrics(r)
    if len(m) != 1 or m[0]["stratum"] != "all":
        f.append("層を渡さないと 1 層 'all' になるはず")
        return f
    m = m[0]
    want = {"precision": (1, 6), "recall": (1, 5), "split_rate": (1, 5), "merge_rate": (1, 6),
            "miss_rate": (1, 5), "false_pos_rate": (1, 6)}
    for k, (x, n) in want.items():
        if (m[k]["x"], m[k]["n"]) != (x, n) or abs(m[k]["value"] - x / n) > 1e-12:
            f.append("%s が %d/%d でない: %r" % (k, x, n, m[k]))
        if (m[k]["lo"], m[k]["hi"]) != stats.wilson(x, n):
            f.append("%s の区間が stats.wilson(%d, %d) でない" % (k, x, n))
    # F1 (decision 38 follow-up): the count is still 2*pairs/(n_gt+n_obs), but lo/hi are intentionally None
    # (the doubled pair count is not an independent-trials proportion; see _f1_prop's docstring).
    if (m["f1"]["x"], m["f1"]["n"]) != (2, 11) or abs(m["f1"]["value"] - 2.0 / 11.0) > 1e-12:
        f.append("f1 が 2/11 でない: %r" % (m["f1"],))
    if (m["f1"]["lo"], m["f1"]["hi"]) != (None, None):
        f.append("f1 の区間は意図的に None のはず（相関した成功を Wilson で扱わない）: %r" % (m["f1"],))
    if (m["n_gt"], m["n_obs"], m["n_split_obs"], m["n_merge_gt"]) != (5, 6, 3, 2):
        f.append("件数（n_gt / n_obs / n_split_obs / n_merge_gt）が違う: %r" % m)
    if (m["n_split_gt_recount"], m["n_fp_as_split"], m["n_merge_obs_recount"], m["n_miss_as_merge"]) != (0, 0, 0, 0):
        f.append("この例では θ の数え直しが何も足さないはず: %r" % (
            (m["n_split_gt_recount"], m["n_fp_as_split"], m["n_merge_obs_recount"], m["n_miss_as_merge"]),))
    # 層: 正解は trial_id、観測は時刻で決める
    strata = {"gt": lambda s: "A" if s["trial_id"] in ("t1", "t2") else "B",
              "obs": lambda o: "A" if o["t"] < 15000 else "B"}
    by = dict((x["stratum"], x) for x in detection_metrics(r, strata))
    a, b = by["A"], by["B"]
    if (a["n_pairs"], a["n_split_gt"], a["n_split_obs"], a["n_gt"], a["n_obs"]) != (1, 1, 3, 2, 4):
        f.append("層 A の件数が違う: %r" % a)
    if (b["n_merge_obs"], b["n_merge_gt"], b["n_miss"], b["n_false_pos"], b["n_gt"], b["n_obs"]) != (1, 2, 1, 1, 3, 2):
        f.append("層 B の件数が違う（併合は先頭の正解の層・偽検出は観測の層）: %r" % b)
    # 空 / 端
    if detection_metrics({"pairs": [], "split": [], "merge": [], "miss": [], "false_pos": []}) != []:
        f.append("空の結果が空にならない")
    only_fp = detection_metrics(match([], [_ob(0, 10)]))[0]
    if only_fp["recall"] != {"x": 0, "n": 0, "value": None, "lo": None, "hi": None}:
        f.append("正解 0 件の再現率は None（0 に丸めない）のはず: %r" % (only_fp["recall"],))
    only_miss = detection_metrics(match([_gt("t1", 0, 10)], []))[0]
    if only_miss["recall"]["value"] != 0.0 or only_miss["precision"]["value"] is not None:
        f.append("観測 0 件の適合率は None・再現率は 0 のはず")
    return f


def _case_offset():
    f = []
    # 終端の遅れ 100 ms（t が変換の終端より 100 ms 遅い）: 区間全体が 100 ms ずれる
    g = [_gt("t1", 0, 1000)]
    late = [{"type": "ime_shadow", "t": 1100, "dwell_ms": 1000, "nav": 0, "abandon": False}]
    if obs_interval(late[0]) != (100, 1100) or obs_interval(late[0], -100) != (0, 1000):
        f.append("obs_interval が [t + offset - dwell_ms, t + offset] でない")
    r0, r1, r2 = match(g, late), match(g, late, obs_end_offset_ms=-100), match(g, late, obs_end_offset_ms=100)
    if abs(r0["pairs"][0]["iou"] - 900.0 / 1100.0) > 1e-12 or r1["pairs"][0]["iou"] != 1.0 \
            or abs(r2["pairs"][0]["iou"] - 800.0 / 1200.0) > 1e-12:
        f.append("obs_end_offset_ms で IoU が 900/1100 → 1.0（-100）/ 800/1200（+100）にならない")
    # 短いセッション（200 ms）は遅れ 100 ms で対にならない（L/3 = 66）→ offset で救える
    gs, ls = [_gt("t1", 0, 200)], [{"type": "ime_shadow", "t": 300, "dwell_ms": 200, "nav": 0, "abandon": False}]
    if _sizes(match(gs, ls)) != (0, 0, 0, 1, 1) or _sizes(match(gs, ls, obs_end_offset_ms=-100)) != (1, 0, 0, 0, 0):
        f.append("短いセッションの遅れが offset で補正できない")
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

    g, o = [_gt("t1", 0, 100)], [_ob(0, 100)]
    raises("終わりが null", lambda: match([_gt("t1", 0, 100, end_wall_ms=None)], o))
    raises("start が小数", lambda: match([_gt("t1", 0, 100, start_wall_ms=0.5)], o))
    raises("start が真偽値", lambda: match([_gt("t1", 0, 100, start_wall_ms=True)], o))
    raises("終わりが開始より前", lambda: match([_gt("t1", 100, 50)], o))
    raises("セッションがオブジェクトでない", lambda: match([1], o))
    raises("dwell_ms が負", lambda: match(g, [dict(o[0], dwell_ms=-1)]))
    raises("t が無い", lambda: match(g, [{"dwell_ms": 1}]))
    raises("t が文字列", lambda: match(g, [dict(o[0], t="1")]))
    raises("iou_min = 0", lambda: match(g, o, iou_min=0))
    raises("iou_min = 1.5", lambda: match(g, o, iou_min=1.5))
    raises("iou_min が真偽値", lambda: match(g, o, iou_min=True))
    raises("obs_end_offset_ms が小数", lambda: match(g, o, obs_end_offset_ms=1.5))
    return f


def _case_recount():
    """theta の数え直し（decision 38 follow-up）。match() 自体の分割・併合・偽検出・取り逃しは変わらず、
    split_rate / merge_rate と n_split_gt_recount / n_fp_as_split / n_merge_obs_recount / n_miss_as_merge
    だけがこの数え直しで動く。"""
    f = []
    # 陽性対照: gt(0,1000) は ob(0,600) と対になり（IoU 0.6）、leftover の ob(600,1400)（長さ 800）は
    # 自分の長さのうち 400/800 = 0.5 が対になった正解の区間に入る（match() では対 1 + 偽検出 1 のまま）。
    r = match([_gt("t1", 0, 1000)], [_ob(0, 600), _ob(600, 1400)])
    if _sizes(r) != (1, 0, 0, 0, 1):
        f.append("match() 自体の分割が変わった（数え直しは match() を変えないはず）: %r" % (_sizes(r),))
    m = detection_metrics(r)[0]
    if (m["n_split_gt_recount"], m["n_fp_as_split"], m["split_rate"]["x"], m["split_rate"]["n"]) != (1, 1, 1, 1):
        f.append("leftover（frac 0.5）の分割が theta = 0.5 の既定で数え直されない: %r" % m)
    if m["n_split_gt"] != 0 or m["n_pairs"] != 1 or m["n_false_pos"] != 1:
        f.append("元の n_split_gt / n_pairs / n_false_pos が数え直しで動いている: %r" % m)
    # 陰性対照: theta = 0.6 まで上げると frac 0.5 では届かず、数え直されない
    m_strict = detection_metrics(r, theta=0.6)[0]
    if (m_strict["n_split_gt_recount"], m_strict["n_fp_as_split"], m_strict["split_rate"]["x"]) != (0, 0, 0):
        f.append("theta = 0.6 でも frac 0.5 の leftover が数え直された（閾値が効いていない）: %r" % m_strict)

    # 併合: gt1(0,3000) は ob(0,4000)（長さ 4000）と対になり（IoU 0.75）、gt2(3000,5000)（長さ 2000）は
    # 自分の長さのうち 1000/2000 = 0.5 が対になった観測の区間に入る（match() では対 1 + 取り逃し 1 のまま）。
    r2 = match([_gt("t1", 0, 3000), _gt("t2", 3000, 5000)], [_ob(0, 4000)])
    if _sizes(r2) != (1, 0, 0, 1, 0):
        f.append("match() 自体の併合が変わった: %r" % (_sizes(r2),))
    m2 = detection_metrics(r2)[0]
    if (m2["n_merge_obs_recount"], m2["n_miss_as_merge"], m2["merge_rate"]["x"], m2["merge_rate"]["n"]) != (1, 1, 1, 1):
        f.append("gt2（frac 0.5）の併合が theta = 0.5 の既定で数え直されない: %r" % m2)
    if m2["n_merge_obs"] != 0 or m2["n_miss"] != 1:
        f.append("元の n_merge_obs / n_miss が数え直しで動いている: %r" % m2)
    # 陰性対照: theta = 0.6 では frac 0.5 の gt2 は届かない
    m2_strict = detection_metrics(r2, theta=0.6)[0]
    if (m2_strict["n_merge_obs_recount"], m2_strict["n_miss_as_merge"]) != (0, 0):
        f.append("theta = 0.6 でも frac 0.5 の取り逃しが数え直された: %r" % m2_strict)

    # precision / recall / n_gt / n_obs は theta に依らない
    for th in (0.3, 0.5, 0.7, 0.9, 1.0):
        mm = detection_metrics(r, theta=th)[0]
        if (mm["n_pairs"], mm["n_gt"], mm["n_obs"], mm["precision"]["x"], mm["recall"]["x"]) != (1, 1, 2, 1, 1):
            f.append("theta = %r で n_pairs / n_gt / n_obs / precision / recall が変わった: %r" % (th, mm))

    def raises(name, fn):
        try:
            fn()
        except ValueError:
            return
        except Exception as e:
            f.append("%s: ValueError でなく %r" % (name, e))
            return
        f.append("%s: 例外が出なかった" % name)

    raises("theta = 0", lambda: detection_metrics(r, theta=0))
    raises("theta = 1.5", lambda: detection_metrics(r, theta=1.5))
    raises("theta が真偽値", lambda: detection_metrics(r, theta=True))
    raises("recount_split_merge の theta = 0", lambda: recount_split_merge(r, theta=0))

    # 並びに依らない: result の各リストを逆順にしても同じ答え
    r4 = match([_gt("t1", 0, 1000), _gt("t2", 2000, 2200), _gt("t3", 3000, 3200)],
               [_ob(0, 600), _ob(600, 1000), _ob(9000, 9200)])
    base = _dump(recount_split_merge(r4))
    shuffled = {"pairs": list(reversed(r4["pairs"])), "split": list(r4["split"]), "merge": list(r4["merge"]),
                "miss": list(reversed(r4["miss"])), "false_pos": list(reversed(r4["false_pos"]))}
    if _dump(recount_split_merge(shuffled)) != base:
        f.append("recount_split_merge が result の並びに依る")
    return f


def _case_merge_gt_per_stratum():
    """decision 38 follow-up: 併合の各正解は（先頭だけでなく）それぞれ自分の層に merge_gt を数える。
    merge_obs（観測 1 件）は従来どおり先頭の正解の層だけに数える。"""
    f = []
    # gt1 / gt2 は単独ではどちらも IoU < 0.5（0.4）なので、これは _resolve_groups の genuine な併合
    # （decision 38 が扱う「対 + 取り逃し」になる不均衡な併合ではない）。
    g1, g2 = _gt("t1", 20000, 21000), _gt("t2", 21500, 22500)
    r = match([g1, g2], [_ob(20000, 22500)])
    if _sizes(r) != (0, 0, 1, 0, 0):
        f.append("併合の基準の件数が違う: %r" % (_sizes(r),))
        return f
    strata = {"gt": lambda s: "A" if s["trial_id"] == "t1" else "B", "obs": lambda _o: "A"}
    by = dict((x["stratum"], x) for x in detection_metrics(r, strata))
    if by.get("A", {}).get("n_merge_gt") != 1 or by.get("B", {}).get("n_merge_gt") != 1:
        f.append("併合の 2 件目の正解が自分の層に数えられていない: %r" % (by,))
    if by["A"]["n_merge_obs"] != 1 or by.get("B", {}).get("n_merge_obs") != 0:
        f.append("併合の観測（1 件）は先頭の正解の層だけに数えるはず: %r" % (by,))
    if by["A"]["n_gt"] != 1 or by["B"]["n_gt"] != 1:
        f.append("層ごとの n_gt が違う（各 1 のはず）: %r" % (by,))
    return f


def _case_f1_interval():
    """decision 38 follow-up: F1 の lo/hi は常に None（相関した成功を Wilson で扱わない）。件数 0 件・全部対
    でも例外なく None で、value はそのまま点推定として使える。"""
    f = []
    gts = _world(20, 31)
    obs_full = [_ob(g["start_wall_ms"], g["end_wall_ms"]) for g in gts]
    results = [match([], []), match([_gt("t1", 0, 10)], []), match([], [_ob(0, 10)]),
               match([_gt("t1", 0, 10)], [_ob(0, 10)]), match(gts, obs_full), match(gts[:10], obs_full)]
    for r in results:
        for row in detection_metrics(r):
            if (row["f1"]["lo"], row["f1"]["hi"]) != (None, None):
                f.append("f1 の区間が None でない: %r" % (row["f1"],))
            if "note" not in row["f1"]:
                f.append("f1 に区間を出さない理由の note が無い: %r" % (row["f1"],))
    m = detection_metrics(match(gts, obs_full))[0]
    if abs(m["f1"]["value"] - 1.0) > 1e-12 or (m["f1"]["x"], m["f1"]["n"]) != (40, 40):
        f.append("全部対になった場合の f1 の値が 1.0 (40/40) でない: %r" % (m["f1"],))
    return f


def _case_t_gt_clock():
    """decision 38 follow-up: obs_interval() は行に t_gt_clock があればそれを使い、無ければ t を使う
    （直接 match() / inject() を呼ぶ既存の呼び出し側は t_gt_clock を持たず、挙動は変わらない）。"""
    f = []
    plain = {"type": "ime_shadow", "t": 1000, "dwell_ms": 500, "nav": 0, "abandon": False}
    if obs_interval(plain) != (500, 1000):
        f.append("t_gt_clock が無いとき obs_interval が t を使わない: %r" % (obs_interval(plain),))
    corrected = dict(plain, t_gt_clock=1300)
    if obs_interval(corrected) != (800, 1300):
        f.append("t_gt_clock があるとき obs_interval がそれを使わない: %r" % (obs_interval(corrected),))
    r = match([_gt("t1", 800, 1300)], [corrected])
    if not r["pairs"] or r["pairs"][0]["obs"]["t"] != 1000 or r["pairs"][0]["obs"]["t_gt_clock"] != 1300:
        f.append("match() の出力で t / t_gt_clock が保たれていない: %r" % (r["pairs"],))
    return f


def _case_start_while_open():
    """decision 28 / 38 follow-up: n_start_while_open は既定では診断だけ（層ごとの件数を出す・除外しない）。
    config.drop_start_while_open = true のときだけ試行単位の除外理由になる。"""
    f = []
    fx = _cli_fixture()
    obj = json.loads(fx["sessions"].decode("utf-8"))
    marked = 0
    for s in obj["definitions"]["all"]:
        if s.get("trial_id") in ("t00001", "t00002") and s["end_wall_ms"] is not None:
            s["n_start_while_open"] = 1
            marked += 1
    if marked != 2:
        f.append("フィクスチャの前提が崩れている（t00001 / t00002 が見つからない）")
        return f
    sessions_bytes = json.dumps(obj).encode("utf-8")

    default_out = evaluate(sessions_bytes, "all", fx["obs"], fx["plan"], fx["oracle"], fx["config"])
    if default_out["diagnostics"]["start_while_open"]["n"] != 2:
        f.append("既定（drop しない）で診断の件数が 2 でない: %r" % default_out["diagnostics"]["start_while_open"])
    if "start_while_open" in default_out["excluded"]["gt"]["by_reason"]:
        f.append("既定で n_start_while_open による除外理由が出ている（出さないはず）")
    if default_out["used"]["n_gt"] != 88:
        f.append("既定で n_start_while_open のセッションが照合から外れている: %r" % default_out["used"])

    cfg = json.loads(fx["config"].decode("utf-8"))
    cfg["drop_start_while_open"] = True
    drop_out = evaluate(sessions_bytes, "all", fx["obs"], fx["plan"], fx["oracle"], json.dumps(cfg).encode("utf-8"))
    if drop_out["excluded"]["gt"]["by_reason"].get("start_while_open") != 2:
        f.append("drop_start_while_open = true で除外理由に出ない: %r" % drop_out["excluded"])
    if drop_out["used"]["n_gt"] != 86:
        f.append("drop_start_while_open = true でも照合対象が減らない: %r" % drop_out["used"])
    if drop_out["diagnostics"]["start_while_open"]["n"] != 0:
        f.append("drop した後の診断は 0（kept_gt だけを数えるはず）: %r" % drop_out["diagnostics"])
    return f


def _jl(rows):
    return ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n").encode("utf-8")


def _cli_fixture():
    """3 ブロック x 30 試行の合成の計画・oracle・正解・観測。特殊な試行の位置は _case_cli の期待に対応する。"""
    T0 = 1700000000000
    plan_rows = [{"kind": "header", "format": "plan/1", "os": "macos", "seed": 1, "generator_version": "0",
                  "config_sha256": "0" * 64, "recipes_sha256": "0" * 64, "corpus_sha256": "0" * 64}]
    trials = []
    tno = 0
    for b in range(3):
        plan_rows.append({"kind": "block", "block_id": b, "speed": SPEEDS[b], "reset_ime": False, "marker": [],
                          "marker_gap_ms": 0})
        for k in range(30):
            tno += 1
            begin = T0 + b * 2000000 + k * 8000
            trials.append(("t%05d" % tno, b, k, begin, begin + 6000))
            plan_rows.append({"kind": "trial", "trial_id": "t%05d" % tno, "block_id": b, "speed": SPEEDS[b],
                              "scenario": "S%d" % (k % 3 + 1)})
    plan_bytes = _jl(plan_rows)
    orows = [{"kind": "header", "format": "oracle/1", "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
              "os": "macos", "emitter_version": "0", "backend": "dryrun"}]

    def orow(kind, t, **kw):
        return dict(kw, kind=kind, t_wall_ms=t, t_mono_ns=t * 1000000)

    for b in range(3):
        mine = [t for t in trials if t[1] == b]
        orows.append(orow("block_begin", mine[0][3] - 100, block_id=b))
        for tid, _b, _k, begin, end in mine:
            orows.append(orow("trial_begin", begin, trial_id=tid))
            orows.append(orow("trial_end", end, trial_id=tid))
        orows.append(orow("block_end", mine[-1][4] + 100, block_id=b))
    oracle_bytes = _jl(orows)

    sessions, obs = [], []
    for idx, (tid, b, k, begin, _end) in enumerate(trials):
        shift = 700 if b == 1 else 0            # ブロック 1 は観測側の時計が 700 ms 進んでいる
        length = 900 + (idx * 137) % 1500
        lo = begin + 500
        if tid == "t00016":                      # 1 試行に 2 セッション → 観測は 1 行に併合
            sessions += [_gt(tid, lo, lo + 1000), _gt(tid, lo + 1200, lo + 2200)]
            obs.append(_ob(lo + shift, lo + 2200 + shift))
        elif tid == "t00021":                    # 3 断片に分割
            sessions.append(_gt(tid, lo, lo + 3000))
            obs += [_ob(lo + i * 1000 + shift, lo + (i + 1) * 1000 + shift) for i in range(3)]
        elif tid == "t00011":                    # 取り逃し
            sessions.append(_gt(tid, lo, lo + length))
        elif tid == "t00090":                    # ログが閉じないまま終わった
            sessions.append(_gt(tid, lo, None, outcome="open_at_end", excluded_by=["log_truncated"]))
            obs.append(_ob(lo + shift, lo + 400 + shift))
        elif tid in ("t00006", "t00007"):        # 時計の跳びで除外
            sessions.append(_gt(tid, lo, lo + length, excluded_by=["clock_jump"]))
            obs.append(_ob(lo + shift, lo + length + shift))
        else:
            sessions.append(_gt(tid, lo, lo + length))
            obs.append(_ob(lo + shift, lo + length + shift))
        if tid == "t00045":                      # 試行の中の偽検出（層は試行から決まる）
            obs.append(_ob(begin + 4500 + shift, begin + 5000 + shift))
    obs.append(_ob(T0 - 3000, T0 - 2000))        # ブロックの前の偽検出（試行に帰属しない）
    obs_rows = [{"type": "meta", "format": "obs/1", "os": "macos", "logger_version": "0", "manifest_sha256": "0" * 64,
                 "capabilities": {"unconditional": ["key", "ime_shadow"], "threshold_gated": [], "config_gated": []}},
                {"type": "key", "t": T0, "category": "alphabetic", "press": True}] + obs
    excluded = [{"type": "clock_jump", "log": "oracle", "trial_ids": ["t00006", "t00007"]},
                {"type": "log_truncated", "log": "gt", "trial_ids": ["t00090"]}]
    sessions_obj = {"src": "mac_nstic", "rules_sha256": "0" * 64,
                    "definitions": {"all": sessions, "macos_def": sessions, "windows_def": None},
                    "oracle_agreement": {"plan_available": True, "n_trials": 90, "rate": 0.5}, "excluded": excluded}
    return {"sessions": json.dumps(sessions_obj, indent=2).encode("utf-8"), "obs": _jl(obs_rows), "plan": plan_bytes,
            "oracle": oracle_bytes, "config": json.dumps({"clock_offsets_ms": {"1": 700}, "cell": "mac-std"}).encode("utf-8")}


def _case_cli():
    import contextlib
    import io
    import subprocess
    f = []
    fx = _cli_fixture()
    ev = lambda **kw: evaluate(fx["sessions"], kw.get("definition", "all"), fx["obs"], fx["plan"], fx["oracle"],
                               kw.get("config", fx["config"]))
    out = ev()
    p = out["metrics"]["pooled"]
    if (p["n_pairs"], p["n_split_gt"], p["n_split_obs"], p["n_merge_obs"], p["n_merge_gt"], p["n_miss"], p["n_false_pos"]) \
            != (84, 1, 3, 1, 2, 1, 2) or (p["n_gt"], p["n_obs"]) != (88, 90):
        f.append("全体の件数が (84,1,3,1,2,1,2)・n_gt 88・n_obs 90 でない（クロック補正・除外・層の合算）: %r" % p)
    if any(x["iou"] != 1.0 for x in out["matching"]["pairs"]):
        f.append("クロック補正後は対が全部 IoU 1.0 のはず")
    # decision 38 follow-up: "t" never changes; the corrected time always lives in "t_gt_clock".
    moved = [p["obs"] for p in out["matching"]["pairs"] if p["obs"]["t"] != p["obs"]["t_gt_clock"]]
    all_obs_rows = [p["obs"] for p in out["matching"]["pairs"]] + \
        [o for sp in out["matching"]["split"] for o in sp["obs"]] + \
        [mg["obs"] for mg in out["matching"]["merge"]] + out["matching"]["false_pos"]
    if not all("t_gt_clock" in r for r in all_obs_rows) or len(moved) != 30 or \
            any(r["t"] - r["t_gt_clock"] != 700 for r in moved):
        f.append("補正した観測（ブロック 1 の対 30 件）が t_gt_clock = t - 700 で t を書き換えていない: %d 件" % len(moved))
    if out["config"]["uncorrected_blocks"] != [0, 2]:
        f.append("uncorrected_blocks が [0, 2] でない（ブロック 1 だけ clock_offsets_ms にある）: %r" % out["config"]["uncorrected_blocks"])
    if out["config"]["theta"] != 0.5 or out["config"]["drop_start_while_open"] is not False:
        f.append("theta / drop_start_while_open の既定が違う: %r" % out["config"])
    if out["diagnostics"]["start_while_open"] != {"n": 0, "by_stratum": []}:
        f.append("n_start_while_open が全部 0 の入力で診断が空でない: %r" % out["diagnostics"])
    if out["excluded"] != {"gt": {"n": 3, "by_reason": {"clock_jump": 2, "log_truncated": 1, "open_at_end": 1}},
                           "obs": {"n": 3, "by_reason": {"clock_jump": 2, "log_truncated": 1}},
                           "trials": {"n": 3, "by_type": {"clock_jump": 2, "log_truncated": 1}}}:
        f.append("除外の件数が理由ごとに出ない: %r" % (out["excluded"],))
    if (out["input"], out["used"]) != ({"n_gt": 91, "n_obs": 93}, {"n_gt": 88, "n_obs": 90}):
        f.append("入力・使用した件数が違う: %r %r" % (out["input"], out["used"]))
    strata = out["metrics"]["by_stratum"]
    if len(strata) != 10 or sum(s["n_pairs"] for s in strata) != 84:
        f.append("層が 3 シナリオ x 3 速さ + 試行外 の 10 個で、対の合計が 84 になるはず: %d 層" % len(strata))
    s1 = [s for s in strata if s["stratum"] == {"cell": "mac-std", "scenario": "S1", "speed": "slow"}]
    if len(s1) != 1 or (s1[0]["n_pairs"], s1[0]["n_merge_obs"], s1[0]["n_merge_gt"], s1[0]["n_gt"], s1[0]["n_obs"]) != (8, 1, 2, 10, 9):
        f.append("層 (mac-std, S1, slow) の件数が違う: %r" % (s1,))
    outside = [s for s in strata if s["stratum"] == {"cell": "mac-std", "scenario": None, "speed": None}]
    if len(outside) != 1 or outside[0]["n_false_pos"] != 1:
        f.append("試行に帰属しない偽検出が (cell, null, null) 層に 1 件出ない")
    # t00045 はブロック 1（mid）の k = 14 → シナリオ S3
    mid = [s for s in strata if s["stratum"] == {"cell": "mac-std", "scenario": "S3", "speed": "mid"}]
    if len(mid) != 1 or mid[0]["n_false_pos"] != 1:
        f.append("t00045 の中の偽検出が (S3, mid) 層に出ない: %r" % (mid,))
    if sum(s["n_false_pos"] for s in strata) != 2:
        f.append("偽検出が全層で 2 件（試行の外 1・t00045 の中 1）でない")
    # 補正なしだとブロック 1 が対にならない（補正が効いている証拠）
    no_cfg = ev(config=json.dumps({"cell": "mac-std"}).encode("utf-8"))
    if no_cfg["metrics"]["pooled"]["n_pairs"] >= 84:
        f.append("clock_offsets_ms を外しても対が減らない（補正が効いていない）")
    # 既定の設定でも動く（cell は plan の os）
    default = evaluate(fx["sessions"], "all", fx["obs"], fx["plan"], fx["oracle"], None)
    if default["config"]["cell"] != "macos" or default["config"]["iou_min"] != 0.5:
        f.append("設定なしの既定（cell = plan の os・iou_min 0.5）が違う")

    # バイト一致（同じ入力で 2 回・別の出力先・サブプロセス経由でも）
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for k in ("sessions", "obs", "plan", "oracle", "config"):
            paths[k] = os.path.join(d, k + ".dat")
            with open(paths[k], "wb") as fh:
                fh.write(fx[k])
        cfg_path = os.path.join(d, "cfg.json")
        with open(cfg_path, "wb") as fh:
            fh.write(fx["config"])

        def run(out_name, **over):
            a = dict(sessions=paths["sessions"], definition="all", obs=paths["obs"], plan=paths["plan"],
                     oracle=paths["oracle"], config=cfg_path, out=os.path.join(d, out_name))
            a.update(over)
            argv = []
            for k, v in a.items():
                if v is not None:
                    argv += ["--" + k, v]
            buf, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                    rc = main(argv)
            except SystemExit as e:
                rc = e.code
            return rc, err.getvalue()

        rc1, _ = run("o1.json")
        rc2, _ = run("o2.json")
        if rc1 != 0 or rc2 != 0:
            f.append("CLI が exit 0 で終わらない: %r %r" % (rc1, rc2))
        else:
            b1, b2 = open(os.path.join(d, "o1.json"), "rb").read(), open(os.path.join(d, "o2.json"), "rb").read()
            if b1 != b2 or b1 != render(out):
                f.append("CLI の出力が 2 回でバイト一致しない / evaluate と違う")
            if b"\r" in b1 or b1.startswith(b"\xef\xbb\xbf") or d.encode("utf-8") in b1:
                f.append("出力に CR・BOM・入力の path が入っている")
            sub = subprocess.run([sys.executable, os.path.abspath(__file__), "--sessions", paths["sessions"],
                                  "--definition", "all", "--obs", paths["obs"], "--plan", paths["plan"],
                                  "--oracle", paths["oracle"], "--config", cfg_path, "--out", os.path.join(d, "o3.json")],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if sub.returncode != 0 or open(os.path.join(d, "o3.json"), "rb").read() != b1:
                f.append("サブプロセスで走らせた CLI が exit 0 でない / バイト一致しない: %r" % sub.stderr[-200:])

        # 入力の誤りは exit 2（拒否であって異常終了ではない）
        def rc_of(name, want, **over):
            rc, err = run(name, **over)
            if rc != want or "Traceback" in err:
                f.append("%s: exit %r（期待 %d）%s" % (name, rc, want, err[-120:]))

        rc_of("e1.json", 2, definition="windows_def")
        rc_of("e2.json", 2, out=paths["obs"])
        rc_of("e3.json", 2, plan=os.path.join(d, "no-such-file"))
        bad_plan = os.path.join(d, "bad_plan.dat")
        with open(bad_plan, "wb") as fh:
            fh.write(fx["plan"] + b"\n")
        rc_of("e4.json", 2, plan=bad_plan)
        bad_cfg = os.path.join(d, "bad_cfg.json")
        for name, body in (("unknown key", {"iou": 0.5}), ("unknown block", {"clock_offsets_ms": {"9": 1}}),
                           ("float offset", {"obs_end_offset_ms": 1.5}), ("iou 0", {"iou_min": 0}),
                           ("theta 0", {"theta": 0}), ("drop_start_while_open が真偽値でない", {"drop_start_while_open": 1})):
            with open(bad_cfg, "wb") as fh:
                fh.write(json.dumps(body).encode("utf-8"))
            rc_of("e5.json", 2, config=bad_cfg)
        old = json.loads(fx["sessions"].decode("utf-8"))
        for s in old["definitions"]["all"]:
            s.pop("excluded_by")
        old_path = os.path.join(d, "old.json")
        with open(old_path, "wb") as fh:
            fh.write(json.dumps(old).encode("utf-8"))
        rc_of("e6.json", 2, sessions=old_path)
        no_swo = json.loads(fx["sessions"].decode("utf-8"))
        for s in no_swo["definitions"]["all"]:
            s.pop("n_start_while_open")
        no_swo_path = os.path.join(d, "no_swo.json")
        with open(no_swo_path, "wb") as fh:
            fh.write(json.dumps(no_swo).encode("utf-8"))
        rc_of("e6b.json", 2, sessions=no_swo_path)
        rc_of("e7.json", 2, obs=None)
        rc_of("e8.json", 2, definition="bogus")
    return f


CASES = [
    ("5 型（完全一致 / 分割 / 併合 / 取り逃し / 偽検出）", _case_five_types),
    ("定義の性質（隣接 2 断片・不均衡な併合・短いセッション）", _case_definition_properties),
    ("IoU の境界（>= 0.5・iou_min・長さ 0）", _case_iou_boundary),
    ("同点の決定性（入力の並びに依らない）", _case_tie_determinism),
    ("陽性対照（観測を 1 行消す・1 行をずらすと悪化）", _case_positive_control),
    ("陰性対照（60 s ずらす・シャッフルで偶然水準）", _case_negative_control),
    ("バイト一致（同じ入力で 2 回）", _case_byte_identical),
    ("検出の指標（件数・Wilson・層）", _case_metrics),
    ("obs_end_offset_ms（終端の遅れの補正）", _case_offset),
    ("入力の検証", _case_validation),
    ("theta の数え直し（分割・併合の陽性 / 陰性対照・decision 38）", _case_recount),
    ("併合の各正解を自分の層に数える（decision 38）", _case_merge_gt_per_stratum),
    ("F1 の区間は常に None（decision 38）", _case_f1_interval),
    ("t_gt_clock の優先・t は書き換えない（decision 38）", _case_t_gt_clock),
    ("n_start_while_open の診断・drop_start_while_open（decision 28 / 38）", _case_start_while_open),
    ("CLI（除外・層・クロック補正・バイト一致・exit 2）", _case_cli),
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
            for m in fails:
                print("     FAIL " + m)
        else:
            print("  ✅ " + name)
    if bad:
        print("selftest 失敗 %d 件 / %d 件" % (bad, len(CASES)))
        return 1
    print("selftest OK（%d 件）" % len(CASES))
    return 0


# ---------------------------------------------------------------- CLI

def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="照合器と検出の指標（正解のセッション × 観測の ime_shadow 行）")
    ap.add_argument("--sessions")
    ap.add_argument("--definition", choices=DEFINITIONS)
    ap.add_argument("--obs")
    ap.add_argument("--plan")
    ap.add_argument("--oracle")
    ap.add_argument("--config")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.sessions and args.definition and args.obs and args.plan and args.oracle and args.out):
        ap.error("--sessions / --definition / --obs / --plan / --oracle / --out が要る（--config は任意）")
    for inp in (args.sessions, args.obs, args.plan, args.oracle, args.config):
        if inp and _same_file(inp, args.out):
            print("match: --out が入力ファイルと同じ（%s）" % inp, file=sys.stderr)
            return 2
    try:
        out = evaluate(_read(args.sessions, "sessions"), args.definition, _read(args.obs, "obs"),
                       _read(args.plan, "plan"), _read(args.oracle, "oracle"),
                       None if args.config is None else _read(args.config, "config"))
        _write_atomic(args.out, render(out))
    except (InputError, ValueError) as e:
        print("match: %s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("match: 出力できない（%s）" % type(e).__name__, file=sys.stderr)
        return 2
    p = out["metrics"]["pooled"]
    if p is not None:
        print("match: 正解 %d 件・観測 %d 件 → 対 %d（再現率 %s・適合率 %s）除外 正解 %d / 観測 %d" % (
            p["n_gt"], p["n_obs"], p["n_pairs"], _fmt(p["recall"]["value"]), _fmt(p["precision"]["value"]),
            out["excluded"]["gt"]["n"], out["excluded"]["obs"]["n"]))
    return 0


def _fmt(v):
    return "n/a" if v is None else "%.3f" % v


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
