"""段 1 の終了判定（conditions.md K1〜K4・第 2 版）。件数・率・分布の要約・区間の幅の見込み・判定だけを出す。

usage:
  stoprule.py count  --records DIR --work DIR --replay PATH --utc-offset-secs N --out JSON [--values JSON]
  stoprule.py need   --counts JSON --out JSON --seed N [--aucs 0.6,0.7,0.8] [--sds 0.5,1.0] [--rho 0.3]
                     [--days 20,30,...] [--reps 200]

`count` は記録の写し（prepare_records.py の出力）を読み、件数と（値があれば）判定を書く。
`need` は件数の要約（λ・π）だけから、想定する AUC と日の揺れごとに要る日数を見込む（記録を読まない）。
日付・時刻・ファイル名・日ごとの値・個々の申告を出力しない。
"""
import argparse
import bisect
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
CAND = os.path.join(EXP, "../20261103-stall-candidates-c1c2c6")
BUILD = os.path.join(EXP, "../20261102-stall-decomposition/o1")
DAYSIM = os.path.join(EXP, "../20261103-mhd-dryrun-v2/scripts")

# 変異（check_mutations.py だけが設定する）: strat / unanswered / cutoff0 / early / gt / nowindow / crossday / nolatcap
#   / endpoint（停滞の中の対応を窓の終わりに戻す）/ noclock（時計の狂った記録を除かない）
#   / noobs（窓が観測区間に収まらない回答を除かない）
#   / anytime（窓の 1 日目を段 1 の行ではなく全行の最小の時刻から取る）/ tablestart（表の s1_start_day を窓の 1 日目にする）
#   / earlyle（前期を late_start_day の日まで含めて数える）/ nolower（窓の 1 日目より前も数える）
#   / nocapyear（年の範囲の外の時刻も日に数える）
MUTATE = os.environ.get("STOPRULE_MUTATE") or None

DAY_CUTOFF_HOUR = 4          # eh3::DAY_CUTOFF_HOUR
DAY_SECS = 86_400
STUCK = ("stuck",)           # S1-A3 が決めるまでの既定（引数で替える）
EXCLUDED = ("cannot_answer",)
LATENCY_CAP_MS = 600_000     # S1-A4（判断 19）: これを超えて答えた回答は未回答と同じに扱う（2 分は感度の記述）
STRATA = ("random", "low_operation_end", "resumption")
# 停滞の中の対応（S1-B1・判断 22）: 回答の窓 [recall_window_start_ms, recall_window_end_ms] の半分以上が
# 停滞の区間に入るとき中と数える。end（第 2 版までの仮・窓の終わり）と contain（丸ごと・S1-B2 の感度）は引数で選ぶ
IN_STALL_RULES = ("majority", "end", "contain")
IN_STALL = "majority"
# 時計の狂った起動で始まった記録（名前の年が 2020〜2040 の外・PR #435 の判断 3）は名前で除く
CLOCK_YEAR_RANGE = (2020, 2040)
# 第 2 版（判断 8）: 区間の幅は判定に入れない（記述）。auc・sd_day・rho_day は幅の見込みを出すときだけ使う
VALUE_KEYS = ("min_days", "min_stuck", "min_nonstuck", "min_in_c1", "min_in_c2", "min_assigned_days", "max_days")
WIDTH_KEYS = ("auc", "sd_day", "rho_day")
# 回答の類（S1-A3・S1-B6・ADR-055）。知らない類は止める（黙って「詰まりでない」に数えない）
CATEGORIES = ("stuck", "deliberating", "external_material", "conversation", "away", "working", "cannot_answer")


def _year_bounds_ms():
    """CLOCK_YEAR_RANGE の UTC の ms の範囲 [lo, hi)。"""
    import datetime as _dt
    lo = _dt.datetime(CLOCK_YEAR_RANGE[0], 1, 1, tzinfo=_dt.timezone.utc)
    hi = _dt.datetime(CLOCK_YEAR_RANGE[1] + 1, 1, 1, tzinfo=_dt.timezone.utc)
    return int(lo.timestamp() * 1000), int(hi.timestamp() * 1000)


def local_day(t_ms, utc_offset_secs):
    """eh3::local_day と同じ式（現地 4:00 区切り・時差は 1 つ）。"""
    cut = 0 if MUTATE == "cutoff0" else DAY_CUTOFF_HOUR
    local_secs = t_ms // 1000 + utc_offset_secs
    return (local_secs - cut * 3600) // DAY_SECS


# ---------------------------------------------------------------- 記録を読む
def read_record(path):
    """1 本の記録から、数えるのに要る行だけを取る（key 行の中身は読まない）。"""
    probes, debug_ids, labels, hm, times = {}, set(), [], {}, []
    seen_labels = set()
    session_start = None    # 最初の meta（段 1 の行）の session_start。窓の 1 日目に使う（判断 51）
    late_starts = set()     # handmark_day の late_start_day（前期の終わり・null は除く）
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)   # 読めない行は止める（prepare_records が最後の切れた行だけを除いてある）
            if not isinstance(o, dict):
                raise ValueError("JSON の物でない行")
            ty = o.get("type")
            t = o.get("t", o.get("ts"))
            if isinstance(t, int) and not isinstance(t, bool):
                times.append(t)
            if ty == "meta" and "session_start" in o and session_start is None:
                ss = o["session_start"]
                if not isinstance(ss, int) or isinstance(ss, bool):
                    raise ValueError("session_start が整数でない")
                session_start = ss
            if ty == "probe_assignment":
                pid, st = o.get("probe_id"), o.get("stratum")
                if st is None:      # 段 1 より前のビルド（層を持たない）は数えない
                    continue
                if st not in STRATA:
                    raise ValueError("知らない stratum")
                if o.get("debug") is True:
                    debug_ids.add(pid)
                    continue
                probes[pid] = st
                times.append(o["scheduled_ts"])
            elif ty == "activity_label":
                if o.get("debug") is True:
                    debug_ids.add(o.get("probe_id"))
                    continue
                a, b, lat, cat = o["recall_window_start_ms"], o["recall_window_end_ms"], o.get("latency_ms"), o["category"]
                if not all(isinstance(x, int) and not isinstance(x, bool) for x in (a, b)) or a >= b:
                    raise ValueError("回答の窓の始まりが終わりより前でない")
                if isinstance(lat, int) and not isinstance(lat, bool) and lat < 0:
                    raise ValueError("回答の遅れが負")
                if o["answered"] is True and cat not in CATEGORIES:
                    raise ValueError("知らない回答の類")
                if o.get("probe_id") in seen_labels:
                    raise ValueError("同じ問いの回答の行が 2 つある")
                seen_labels.add(o.get("probe_id"))
                labels.append((o.get("probe_id"), o["category"], o["answered"] is True, o["recall_window_end_ms"],
                               o["recall_window_start_ms"], o.get("latency_ms")))
            elif ty == "handmark_day":
                d = o["day"]
                ls = o.get("late_start_day")
                if ls is not None:
                    if not isinstance(ls, int) or isinstance(ls, bool):
                        raise ValueError("late_start_day が整数でない")
                    late_starts.add(ls)
                if d not in hm or o["t"] >= hm[d][0]:
                    hm[d] = (o["t"], o["assigned"])   # 日ごとに最後の行
    if session_start is None:
        raise ValueError("最初の meta に session_start が無い")
    return dict(probes=probes, debug_ids=debug_ids, labels=labels, hm=hm, times=times,
                session_start=session_start, late_starts=late_starts)


def read_table(path):
    """割付の表（handmark_assignment.json）から s1_start_day と late_start_day だけを取る。"""
    t = json.load(open(path, encoding="utf-8"))
    for k in ("s1_start_day", "early_days", "late_start_day"):
        if not isinstance(t.get(k), int) or isinstance(t.get(k), bool):
            raise ValueError("表の " + k + " が整数でない")
    if t["early_days"] < 1:
        raise ValueError("表の early_days が 1 以上でない")
    if t["late_start_day"] != t["s1_start_day"] + t["early_days"]:
        raise ValueError("表の late_start_day が s1_start_day + early_days でない")
    return {"s1_start_day": t["s1_start_day"], "late_start_day": t["late_start_day"]}


def in_spans(spans, t):
    """spans は [(a, b)] を a で昇順・互いに交わらない。t が閉区間 [a, b] のどれかに入るか。"""
    i = bisect.bisect_right([a for a, _ in spans], t) - 1
    return i >= 0 and spans[i][1] >= t


def in_stall(spans, a, b, rule=IN_STALL):
    """回答の窓 [a, b] が停滞の区間（spans・閉区間・互いに交わらない）に入るか。

    majority: 窓と区間の重なりの長さの和が窓の長さの半分以上（ちょうど半分は中）。
    end: 窓の終わり b が区間のどれかに入る。contain: 窓が 1 つの区間に丸ごと入る。
    """
    if MUTATE == "endpoint":
        rule = "end"
    if rule == "end":
        return in_spans(spans, b)
    if rule == "contain":
        return any(s <= a and b <= e for s, e in spans)
    if rule != "majority":
        raise ValueError(rule)
    ov = sum(max(0, min(b, e) - max(a, s)) for s, e in spans if e >= a and s <= b)
    return 2 * ov >= (b - a)


def clock_excluded(name):
    """記録の名前（gse_<mode>_YYYYMMDD_HHMMSS.ndjson）の年が範囲の外なら True。"""
    if MUTATE == "noclock":
        return False
    m = re.search(r"_(\d{4})\d{4}_\d{6}", name)
    return bool(m) and not (CLOCK_YEAR_RANGE[0] <= int(m.group(1)) <= CLOCK_YEAR_RANGE[1])


def quartiles(xs):
    if not xs:
        return None
    xs = sorted(xs)

    def q(p):   # nearest rank
        r = max(1, min(len(xs), math.ceil(p * len(xs))))
        return xs[r - 1]
    return [q(0.25), q(0.5), q(0.75)]


def count(records, episodes, utc_offset_secs, stuck=STUCK, excluded=EXCLUDED, max_days=None, rule=IN_STALL,
          table=None):
    """records: read_record の列。episodes: 同じ順の {"C1": [(a, b)], "C2": [(a, b)]}（ms・閉区間）。

    max_days があれば、最初の日から max_days 日（両端を含む）の窓の中の回答と割付だけを数える
    （全員を同じ期間で比べる・判断 8）。経過日数は窓で切らずに数える（最長の期間に達したかを見るため）。
    最初の日（窓の 1 日目）は段 1 の記録の最初の meta の session_start の日（S1-G2・S1-F2）。
    table（read_table の出力）があれば、表の s1_start_day とのずれの日数を出す（窓の 1 日目を正とする）。
    前期（窓の 1 日目から late_start_day の前日まで）の件数を記述で出す（判定に使わない・判断 47・51）。
    """
    by_stratum = {s: 0 for s in STRATA}
    ans_by_stratum = {s: 0 for s in STRATA}
    n_unanswered_random = 0
    n_random_ans = n_stuck = n_nonstuck = n_excluded = 0
    n_cross_day = 0
    n_late = 0
    n_unobserved = 0
    in_c = {"C1": [0, 0, 0], "C2": [0, 0, 0]}   # [回答, 詰まり, 詰まりでない]
    per_day = {}
    all_days = set()
    hm_last = {}
    n_eps = {"C1": 0, "C2": 0}
    lo_ms, hi_ms = _year_bounds_ms()
    for rec in records:
        for t in rec["times"]:
            if MUTATE != "nocapyear" and not (lo_ms <= t < hi_ms):
                continue    # 年の範囲（CLOCK_YEAR_RANGE）の外の時刻は経過に数えない
            all_days.add(local_day(t, utc_offset_secs))
        all_days.add(local_day(rec["session_start"], utc_offset_secs))
    first = min(local_day(r["session_start"], utc_offset_secs) for r in records) if records else None
    if MUTATE == "anytime":
        first = min(all_days) if all_days else None
    if MUTATE == "tablestart" and table is not None:
        first = table["s1_start_day"]
    # 前期の終わり（late_start_day）は handmark_day の行と表から。食い違えば止める
    lates = set().union(*(r["late_starts"] for r in records)) if records else set()
    if table is not None:
        lates.add(table["late_start_day"])
    # 前期は記述なので、決まらないときは判定を止めずに early を null にして理由を出す
    early_unavailable = None
    late_start = None
    if len(lates) > 1:
        early_unavailable = "late_start_day_ambiguous"
    elif lates:
        late_start = next(iter(lates))
        if first is None or late_start <= first:
            early_unavailable = "late_start_not_after_window_start"
            late_start = None
    early_c = {"stuck": 0, "nonstuck": 0, "excluded": 0, "C1": [0, 0, 0], "C2": [0, 0, 0]}
    early_days_obs = set()

    def in_early(d):
        if late_start is None:
            return False
        return d <= late_start if MUTATE == "earlyle" else d < late_start

    def in_window(d):
        # 窓は [窓の 1 日目, 窓の 1 日目 + max_days)。1 日目より前（時計の狂った行）は max_days が無くても数えない
        if first is None or (d < first and MUTATE != "nolower"):
            return False
        return max_days is None or MUTATE == "nowindow" or d - first < max_days
    for rec, eps in zip(records, episodes):
        for d, (t, a) in rec["hm"].items():
            if not in_window(d):
                continue
            if d not in hm_last or t >= hm_last[d][0]:
                hm_last[d] = (t, a)
        for st in rec["probes"].values():
            by_stratum[st] += 1
        spans = {k: sorted(v) for k, v in eps.items() if k != "obs"}
        for k in n_eps:
            n_eps[k] += len(spans.get(k, []))
        for pid, cat, answered, t_end, t_start, latency in rec["labels"]:
            if pid in rec["debug_ids"] or pid not in rec["probes"]:
                continue
            st = rec["probes"][pid]
            if not in_window(local_day(t_end, utc_offset_secs)):
                continue
            if (answered and MUTATE != "nolatcap"
                    and (not isinstance(latency, int) or isinstance(latency, bool) or latency > LATENCY_CAP_MS)):
                if st == "random":
                    n_late += 1     # 上限を超えた（または遅れの無い）回答は未回答と同じに扱う
                continue
            if not answered and MUTATE != "unanswered":
                if st == "random":
                    n_unanswered_random += 1
                continue
            # 窓が日の切れ目をまたぐ回答は数えない（S1-D1・ADR-010 D4・判断 17）
            if (local_day(t_start, utc_offset_secs) != local_day(t_end, utc_offset_secs)
                    and MUTATE != "crossday"):
                if st == "random":
                    n_cross_day += 1
                continue
            # 窓が 1 つの観測区間に収まらない回答は時点不明として数えない（S1-B2・判断 23）
            obs = eps.get("obs")
            if (obs is not None and MUTATE != "noobs"
                    and not any(x <= t_start and t_end <= y for x, y in obs)):
                if st == "random":
                    n_unobserved += 1
                continue
            ans_by_stratum[st] += 1
            if st != "random" and MUTATE != "strat":
                continue
            n_random_ans += 1
            d = local_day(t_end, utc_offset_secs)
            per_day[d] = per_day.get(d, 0) + 1
            if cat in stuck:
                cls = 1
                n_stuck += 1
            elif cat in excluded:
                cls = None
                n_excluded += 1
            else:
                cls = 2
                n_nonstuck += 1
            early = in_early(d)
            if early:
                early_days_obs.add(d)
                early_c[{1: "stuck", 2: "nonstuck", None: "excluded"}[cls]] += 1
            for k in in_c:
                if in_stall(spans.get(k, []), t_start, t_end, rule):
                    in_c[k][0] += 1
                    if cls is not None:
                        in_c[k][cls] += 1
                    if early:
                        early_c[k][0] += 1
                        if cls is not None:
                            early_c[k][cls] += 1
    assigned = sum(1 for _, a in hm_last.values() if a in ("on", "off"))
    obs_days = len(per_day)
    elapsed = (max(all_days) - first + 1) if all_days else 0
    keys3 = ("answered", "stuck", "nonstuck")
    early_out = None
    if late_start is not None:
        early_out = {"early_days": late_start - first, "observed_days": len(early_days_obs),
                     "random_stuck": early_c["stuck"], "random_nonstuck": early_c["nonstuck"],
                     "random_excluded": early_c["excluded"],
                     "in_C1": dict(zip(keys3, early_c["C1"])), "in_C2": dict(zip(keys3, early_c["C2"]))}
    return {
        "elapsed_days": elapsed,
        "window_days": max_days,
        "observed_days": obs_days,
        "probes_by_stratum": by_stratum,
        "answered_by_stratum": ans_by_stratum,
        "random_unanswered": n_unanswered_random,
        "random_answered": n_random_ans,
        "random_stuck": n_stuck,
        "random_nonstuck": n_nonstuck,
        "random_excluded": n_excluded,
        "random_cross_day": n_cross_day,
        "random_over_latency_cap": n_late,
        "random_window_unobserved": n_unobserved,
        "in_C1": dict(zip(("answered", "stuck", "nonstuck"), in_c["C1"])),
        "in_C2": dict(zip(("answered", "stuck", "nonstuck"), in_c["C2"])),
        "episodes": n_eps,
        "assigned_days": assigned,
        # 前期の件数（記述・H1〜H3 は前期だけで判定する・判断 47）。late_start_day が分からなければ None
        "early": early_out,
        "early_unavailable": early_unavailable,
        # 表の s1_start_day − 窓の 1 日目（日数の差だけ・窓の 1 日目を正とする・S1-F2）。表が無ければ None
        "table_start_offset_days": (table["s1_start_day"] - first) if (table is not None and first is not None) else None,
        "answers_per_observed_day_q": quartiles(list(per_day.values())),
        "lambda_per_observed_day": (n_random_ans / obs_days) if obs_days else None,
        # 判定に使える回答（詰まり・詰まりでない。cannot_answer を除く）の観測日あたりの数。日数の見込みはこちらを使う
        "lambda_valid_per_observed_day": ((n_stuck + n_nonstuck) / obs_days) if obs_days else None,
        "pi_stuck": (n_stuck / (n_stuck + n_nonstuck)) if (n_stuck + n_nonstuck) else None,
        "rules": {"stuck": list(stuck), "excluded": list(excluded), "day_cutoff_hour": DAY_CUTOFF_HOUR,
                  "in_stall": {"majority": "at least half of [recall_window_start_ms, recall_window_end_ms] inside [onset, resume or interval end]",
                               "end": "recall_window_end_ms in [onset, resume or interval end]",
                               "contain": "whole recall window inside one [onset, resume or interval end]"}[rule],
                  "cross_day": "window start and end on different local days are not counted",
                  "latency_cap_ms": LATENCY_CAP_MS,
                  "unobserved": "window not inside one observed interval is not counted"},
    }


# ---------------------------------------------------------------- 判定
def check_values(v):
    missing = [k for k in VALUE_KEYS if k not in v]
    if missing:
        raise ValueError("値が足りない: " + ",".join(missing))
    bad = [k for k in VALUE_KEYS if not isinstance(v[k], int) or isinstance(v[k], bool) or v[k] < 1]
    if bad:
        raise ValueError("値が 1 以上の整数でない: " + ",".join(bad))
    if v["min_days"] > v["max_days"]:
        raise ValueError("min_days が max_days を越える")


def verdict(c, v):
    """c: count の出力（max_days の窓で数えたもの）・v: 値。

    第 2 版（判断 8）: 全員を最長の期間まで続け、早くは終わらない。最長の期間に達したら、
    下限をすべて満たせば「判定できる」、そうでなければ「判定不能」。区間の幅は判定に入れない。
    """
    check_values(v)
    if c.get("window_days") != v["max_days"]:
        raise ValueError("count を max_days の窓で数えていない")

    def ge(x, lo):
        return x > lo if MUTATE == "gt" else x >= lo
    need = {
        "days": ge(c["observed_days"], v["min_days"]),
        "stuck": ge(c["random_stuck"], v["min_stuck"]),
        "nonstuck": ge(c["random_nonstuck"], v["min_nonstuck"]),
        "in_C1": ge(c["in_C1"]["answered"], v["min_in_c1"]),
        "in_C2": ge(c["in_C2"]["answered"], v["min_in_c2"]),
        "assigned_days": ge(c["assigned_days"], v["min_assigned_days"]),
    }
    if c["elapsed_days"] < v["max_days"] and not (MUTATE == "early" and all(need.values())):
        out = "continue"       # 続ける（下限を満たしていても早くは終わらない）
    elif all(need.values()):
        out = "decidable"      # 判定できる
    else:
        out = "undecidable"    # 判定不能
    return out, need


# ---------------------------------------------------------------- 区間の幅の見込み（daysim を使う）
def _daysim():
    sys.path.insert(0, DAYSIM)
    import daysim  # noqa: E402
    return daysim


def slope_width(D, auc, pi, lam, sd, rho, reps, seed, idx):
    """全体 D 日（daysim の分割で評価は D − ceil(0.6 D) 日）での、傾きの区間の幅の中央値。"""
    ds = _daysim()
    if D < 5 or not (0 < pi < 1) or lam <= 0:
        return None
    r = ds.run_point(seed, idx, D, auc, pi, lam, sd, rho, reps)
    w = r["by_method"]
    return {"eval_days": r["eval_days"], "percentile": w["percentile"]["width_slope_q"],
            "normal": w["normal"]["width_slope_q"], "sims_without_ci": r["sims_without_ci"],
            "solve_ok": r["solve_ok"]}


# ---------------------------------------------------------------- 記録の側（gse-replay と停滞の候補の検出器）
def episodes_from_records(paths, work, replay):
    sys.path.insert(0, BUILD)
    sys.path.insert(0, CAND)
    import build_o1  # noqa: E402
    import candidates as cd  # noqa: E402
    os.makedirs(work, mode=0o700, exist_ok=True)
    out, selfcheck = [], {"files": 0, "mismatch_files": 0, "no_focus_files": 0}
    for p in paths:
        build_o1.build(replay, work, p)
        d = json.load(open(os.path.join(work, os.path.basename(p)[:-len(".ndjson")] + ".json")))
        if d["input_sha256"] != build_o1.sha256(p):
            sys.exit("中間と入力の SHA-256 が合わない")
        dy = cd.Day(d)
        selfcheck["files"] += 1
        if not d["focus"]:
            selfcheck["no_focus_files"] += 1   # フォーカスの行が無い記録（C1 の活動にフォーカスが入らない）。数だけ出す
        port = [(x[0], x[1]) for x in dy.c0()[0]]
        if port != dy.replay_onsets:
            selfcheck["mismatch_files"] += 1
            continue
        rows, _ = cd.day_rows(dy)
        cd.check_structure(dy, rows)
        eps = {}
        for k in ("C1", "C2"):
            sp = []
            for r in rows[k]:
                iv = dy.interval_of(r["o"])
                end = r["o"] + r["len"] if r["len"] is not None else iv[1]
                sp.append((r["s"], end))
            eps[k] = sp
        eps["obs"] = list(dy.intervals)
        out.append(eps)
    if selfcheck["mismatch_files"]:
        sys.exit("検出器の C0 が gse-replay の onsets と一致しない記録がある " + json.dumps(selfcheck))
    return out, selfcheck


def cmd_count(a):
    paths = sorted(os.path.join(a.records, n) for n in os.listdir(a.records) if n.endswith(".ndjson"))
    n_clock = 0
    if a.manifest:
        # 写しの名前（r001 など）から元の名前を引き、時計の狂った起動で始まった記録を除く（件数だけ出す）
        names = {os.path.basename(r["copy"]): r["name"] for r in json.load(open(a.manifest))["records"]}
        keep = [p for p in paths if not clock_excluded(names.get(os.path.basename(p), ""))]
        n_clock = len(paths) - len(keep)
        paths = keep
    if not paths:
        sys.exit("記録の写しが無い")
    recs = [read_record(p) for p in paths]
    eps, selfcheck = episodes_from_records(paths, a.work, a.replay)
    v = None
    if a.values:
        v = json.load(open(a.values))
        check_values(v)
    tb = read_table(a.table) if a.table else None
    c = count(recs, eps, a.utc_offset_secs, tuple(a.stuck.split(",")), tuple(a.excluded.split(",")),
              max_days=v["max_days"] if v else None, rule=a.in_stall, table=tb)
    c["files"] = len(paths)
    c["excluded_clock_files"] = n_clock
    c["c0_selfcheck"] = selfcheck
    if v:
        # 幅は記述だけ（判定に入れない・判断 8）。値に AUC と日の揺れがあるときだけ見込む
        if all(k in v for k in WIDTH_KEYS) and c["observed_days"] and c["pi_stuck"] is not None:
            c["width_now"] = slope_width(c["observed_days"], v["auc"], c["pi_stuck"], c["lambda_valid_per_observed_day"],
                                         v["sd_day"], v["rho_day"], a.reps, a.seed, 0)
        c["verdict"], c["verdict_parts"] = verdict(c, v)
        c["values"] = v
    json.dump(c, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: c[k] for k in ("files", "elapsed_days", "observed_days", "random_answered", "verdict")
                      if k in c}, ensure_ascii=False))


def cmd_need(a):
    c = json.load(open(a.counts))
    lam, pi_obs = c.get("lambda_valid_per_observed_day"), c["pi_stuck"]   # cannot_answer を除いた数（Codex の指摘）
    if lam is None:
        sys.exit("λ が無い（回答が無い）")
    # π は記録の値か、--pis で仮の幅を入れる（記録の π が 0 か 1 だと模擬にならない）
    pis = [float(x) for x in a.pis.split(",")] if a.pis else [pi_obs]
    if any(p is None or not (0 < p < 1) for p in pis):
        sys.exit("π が (0, 1) の外（--pis で仮の幅を入れる）")
    rows, idx = [], 0
    for pi in pis:
        for auc in [float(x) for x in a.aucs.split(",")]:
            for sd in [float(x) for x in a.sds.split(",")]:
                for D in [int(x) for x in a.days.split(",")]:
                    w = slope_width(D, auc, pi, lam, sd, a.rho, a.reps, a.seed, idx)
                    idx += 1
                    rows.append({"pi": pi, "auc": auc, "sd_day": sd, "rho_day": a.rho, "days": D, **(w or {})})
                    print(pi, auc, sd, D, (w or {}).get("percentile"), flush=True, file=sys.stderr)
    json.dump({"note": "件数の要約（λ）と、π・想定する AUC・日の揺れからの模擬。記録の予測と申告の関係は使っていない。"
               "days は観測日（無作為の枠の回答が 1 件以上ある日）の数。",
               "lambda_per_observed_day": lam, "pi_observed": pi_obs, "pis": pis, "reps": a.reps, "seed": a.seed,
               "rows": rows},
              open(a.out, "w"), ensure_ascii=False, indent=1)


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("count")
    p.add_argument("--records", required=True)
    p.add_argument("--work", required=True)
    p.add_argument("--replay", required=True)
    p.add_argument("--utc-offset-secs", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--values")
    p.add_argument("--manifest", help="prepare_records.py の対応表。あれば時計の狂った記録を名前で除く")
    p.add_argument("--table", help="割付の表（handmark_assignment.json）。s1_start_day のずれと前期の終わりを見る")
    p.add_argument("--in-stall", choices=IN_STALL_RULES, default=IN_STALL, help="停滞の中の対応（S1-B1）")
    p.add_argument("--stuck", default=",".join(STUCK))
    p.add_argument("--excluded", default=",".join(EXCLUDED))
    p.add_argument("--reps", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    q = sub.add_parser("need")
    q.add_argument("--counts", required=True)
    q.add_argument("--out", required=True)
    q.add_argument("--seed", type=int, required=True)
    q.add_argument("--aucs", default="0.6,0.7,0.8")
    q.add_argument("--sds", default="0.5,1.0")
    q.add_argument("--rho", type=float, default=0.3)
    q.add_argument("--pis", default=None, help="π の仮の幅（例 0.03,0.05,0.10,0.20）。省くと記録の π")
    q.add_argument("--days", default="20,30,40,50,60,80,100,120,150,200")
    q.add_argument("--reps", type=int, default=200)
    a = ap.parse_args(argv)
    (cmd_count if a.cmd == "count" else cmd_need)(a)


if __name__ == "__main__":
    main(sys.argv[1:])
