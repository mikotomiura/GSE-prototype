"""段 1 の終了判定（conditions.md K1〜K4）。件数・率・分布の要約・区間の幅の見込み・判定だけを出す。

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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
CAND = os.path.join(EXP, "../20261103-stall-candidates-c1c2c6")
BUILD = os.path.join(EXP, "../20261102-stall-decomposition/o1")
DAYSIM = os.path.join(EXP, "../20261103-mhd-dryrun-v2/scripts")

# 変異（check_mutations.py だけが設定する）: strat / unanswered / cutoff0 / nomax / gt
MUTATE = os.environ.get("STOPRULE_MUTATE") or None

DAY_CUTOFF_HOUR = 4          # eh3::DAY_CUTOFF_HOUR
DAY_SECS = 86_400
STUCK = ("stuck",)           # S1-A3 が決めるまでの既定（引数で替える）
EXCLUDED = ("cannot_answer",)
STRATA = ("random", "low_operation_end", "resumption")
VALUE_KEYS = ("min_days", "min_stuck", "min_nonstuck", "min_in_c1", "min_in_c2", "min_assigned_days",
              "target_slope_width", "auc", "sd_day", "rho_day", "max_days")


def local_day(t_ms, utc_offset_secs):
    """eh3::local_day と同じ式（現地 4:00 区切り・時差は 1 つ）。"""
    cut = 0 if MUTATE == "cutoff0" else DAY_CUTOFF_HOUR
    local_secs = t_ms // 1000 + utc_offset_secs
    return (local_secs - cut * 3600) // DAY_SECS


# ---------------------------------------------------------------- 記録を読む
def read_record(path):
    """1 本の記録から、数えるのに要る行だけを取る（key 行の中身は読まない）。"""
    probes, debug_ids, labels, hm, times = {}, set(), [], {}, []
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
                labels.append((o.get("probe_id"), o["category"], o["answered"] is True, o["recall_window_end_ms"]))
            elif ty == "handmark_day":
                d = o["day"]
                if d not in hm or o["t"] >= hm[d][0]:
                    hm[d] = (o["t"], o["assigned"])   # 日ごとに最後の行
    return dict(probes=probes, debug_ids=debug_ids, labels=labels, hm=hm, times=times)


def in_spans(spans, t):
    """spans は [(a, b)] を a で昇順・互いに交わらない。t が閉区間 [a, b] のどれかに入るか。"""
    i = bisect.bisect_right([a for a, _ in spans], t) - 1
    return i >= 0 and spans[i][1] >= t


def quartiles(xs):
    if not xs:
        return None
    xs = sorted(xs)

    def q(p):   # nearest rank
        r = max(1, min(len(xs), math.ceil(p * len(xs))))
        return xs[r - 1]
    return [q(0.25), q(0.5), q(0.75)]


def count(records, episodes, utc_offset_secs, stuck=STUCK, excluded=EXCLUDED):
    """records: read_record の列。episodes: 同じ順の {"C1": [(a, b)], "C2": [(a, b)]}（ms・閉区間）。"""
    by_stratum = {s: 0 for s in STRATA}
    ans_by_stratum = {s: 0 for s in STRATA}
    n_unanswered_random = 0
    n_random_ans = n_stuck = n_nonstuck = n_excluded = 0
    in_c = {"C1": [0, 0, 0], "C2": [0, 0, 0]}   # [回答, 詰まり, 詰まりでない]
    per_day = {}
    all_days = set()
    hm_last = {}
    n_eps = {"C1": 0, "C2": 0}
    for rec, eps in zip(records, episodes):
        for t in rec["times"]:
            all_days.add(local_day(t, utc_offset_secs))
        for d, (t, a) in rec["hm"].items():
            if d not in hm_last or t >= hm_last[d][0]:
                hm_last[d] = (t, a)
        for st in rec["probes"].values():
            by_stratum[st] += 1
        spans = {k: sorted(v) for k, v in eps.items()}
        for k in n_eps:
            n_eps[k] += len(spans.get(k, []))
        for pid, cat, answered, t_end in rec["labels"]:
            if pid in rec["debug_ids"] or pid not in rec["probes"]:
                continue
            st = rec["probes"][pid]
            if not answered and MUTATE != "unanswered":
                if st == "random":
                    n_unanswered_random += 1
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
            for k in in_c:
                if in_spans(spans.get(k, []), t_end):
                    in_c[k][0] += 1
                    if cls is not None:
                        in_c[k][cls] += 1
    assigned = sum(1 for _, a in hm_last.values() if a in ("on", "off"))
    obs_days = len(per_day)
    elapsed = (max(all_days) - min(all_days) + 1) if all_days else 0
    return {
        "elapsed_days": elapsed,
        "observed_days": obs_days,
        "probes_by_stratum": by_stratum,
        "answered_by_stratum": ans_by_stratum,
        "random_unanswered": n_unanswered_random,
        "random_answered": n_random_ans,
        "random_stuck": n_stuck,
        "random_nonstuck": n_nonstuck,
        "random_excluded": n_excluded,
        "in_C1": dict(zip(("answered", "stuck", "nonstuck"), in_c["C1"])),
        "in_C2": dict(zip(("answered", "stuck", "nonstuck"), in_c["C2"])),
        "episodes": n_eps,
        "assigned_days": assigned,
        "answers_per_observed_day_q": quartiles(list(per_day.values())),
        "lambda_per_observed_day": (n_random_ans / obs_days) if obs_days else None,
        "pi_stuck": (n_stuck / (n_stuck + n_nonstuck)) if (n_stuck + n_nonstuck) else None,
        "rules": {"stuck": list(stuck), "excluded": list(excluded), "day_cutoff_hour": DAY_CUTOFF_HOUR,
                  "in_stall": "recall_window_end_ms in [onset, resume or interval end]"},
    }


# ---------------------------------------------------------------- 判定
def check_values(v):
    missing = [k for k in VALUE_KEYS if k not in v]
    if missing:
        raise ValueError("値が足りない: " + ",".join(missing))


def verdict(c, width, v):
    """c: count の出力・width: 今の観測日での傾きの区間の幅の見込み（None は見込めない）・v: 値。"""
    check_values(v)

    def ge(x, lo):
        return x > lo if MUTATE == "gt" else x >= lo
    need = {
        "days": ge(c["observed_days"], v["min_days"]),
        "stuck": ge(c["random_stuck"], v["min_stuck"]),
        "nonstuck": ge(c["random_nonstuck"], v["min_nonstuck"]),
        "in_C1": ge(c["in_C1"]["answered"], v["min_in_c1"]),
        "in_C2": ge(c["in_C2"]["answered"], v["min_in_c2"]),
        "assigned_days": ge(c["assigned_days"], v["min_assigned_days"]),
        "width": width is not None and width <= v["target_slope_width"],
    }
    if all(need.values()):
        out = "reached"        # 届いた
    elif MUTATE != "nomax" and c["elapsed_days"] >= v["max_days"]:
        out = "undecidable"    # 判定不能
    else:
        out = "continue"       # 続ける
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
        out.append(eps)
    if selfcheck["mismatch_files"]:
        sys.exit("検出器の C0 が gse-replay の onsets と一致しない記録がある " + json.dumps(selfcheck))
    return out, selfcheck


def cmd_count(a):
    paths = sorted(os.path.join(a.records, n) for n in os.listdir(a.records) if n.endswith(".ndjson"))
    if not paths:
        sys.exit("記録の写しが無い")
    recs = [read_record(p) for p in paths]
    eps, selfcheck = episodes_from_records(paths, a.work, a.replay)
    c = count(recs, eps, a.utc_offset_secs, tuple(a.stuck.split(",")), tuple(a.excluded.split(",")))
    c["files"] = len(paths)
    c["c0_selfcheck"] = selfcheck
    if a.values:
        v = json.load(open(a.values))
        check_values(v)
        w = None
        if c["observed_days"] and c["pi_stuck"] is not None:
            sw = slope_width(c["observed_days"], v["auc"], c["pi_stuck"], c["lambda_per_observed_day"],
                             v["sd_day"], v["rho_day"], a.reps, a.seed, 0)
            w = sw["percentile"][1] if sw and sw["percentile"] else None
            c["width_now"] = sw
        c["verdict"], c["verdict_parts"] = verdict(c, w, v)
        c["values"] = v
    json.dump(c, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: c[k] for k in ("files", "elapsed_days", "observed_days", "random_answered", "verdict")
                      if k in c}, ensure_ascii=False))


def cmd_need(a):
    c = json.load(open(a.counts))
    lam, pi_obs = c["lambda_per_observed_day"], c["pi_stuck"]
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
