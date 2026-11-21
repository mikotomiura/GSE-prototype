"""終了判定の自己検査（conditions.md K5）。合成の記録だけを使う（人の記録を読まない）。

usage: python3 -I selftest.py   （失敗があれば終了コード 1）
変異は環境変数 STOPRULE_MUTATE で stoprule.py に効く（check_mutations.py が設定する）。
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stoprule as sr  # noqa: E402

JST = 9 * 3600
DAY0 = 1_795_000_000_000          # 合成の基準の時刻（UTC の ms）
H = 3_600_000
FAILS = []


def check(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def day_start_ms(k):
    """合成の k 日目の現地 4:00（JST）の UTC の ms。"""
    # stoprule の式を使わずに書く（区切りの変異が対照にも効いて打ち消し合わないように）
    d = (DAY0 // 1000 + JST - 4 * 3600) // 86_400
    return ((d + k) * 86_400 + 4 * 3600 - JST) * 1000


def write(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(x) for x in lines) + "\n")


def probe(pid, t, stratum, cat, answered=True, debug=False):
    a = {"type": "probe_assignment", "probe_id": pid, "scheduled_ts": t, "session_elapsed_ms": 1000, "stratum": stratum}
    lab = {"type": "activity_label", "t": t + 5000, "probe_id": pid, "category": cat if answered else "cannot_answer",
           "answered": answered, "latency_ms": 5000, "recall_window_start_ms": t - 31_000, "recall_window_end_ms": t - 1000}
    if debug:
        a["debug"] = True
        lab["debug"] = True
    return [a, lab]


def make(n_days, per_day, stuck_every, late_on_off=0, extra=None):
    """n_days 日・1 日 per_day 件の無作為の回答（stuck_every 件に 1 件が詰まり）・割付の日 late_on_off。"""
    lines = [{"type": "meta", "session_start": DAY0, "hmm_version": "0.5.0", "s1_mode": "marker"}]
    k = 0
    for d in range(n_days):
        t0 = day_start_ms(d) + 6 * H     # 現地 10:00
        lines.append({"type": "key", "t": t0, "category": "alphabetic", "press": True})
        for j in range(per_day):
            cat = "stuck" if k % stuck_every == 0 else "deliberating"
            lines += probe("p%d" % k, t0 + j * 30 * 60_000, "random", cat)
            k += 1
        if d >= n_days - late_on_off:
            lines.append({"type": "handmark_day", "t": t0, "day": sr.local_day(t0, JST), "assigned": "on" if d % 2 else "off"})
    return lines + (extra or [])


def run_count(lines_list, episodes):
    tmp = tempfile.mkdtemp()
    recs = []
    for i, lines in enumerate(lines_list):
        p = os.path.join(tmp, "r%03d.ndjson" % i)
        write(p, lines)
        recs.append(sr.read_record(p))
    return sr.count(recs, episodes, JST)


VALUES = {"min_days": 10, "min_stuck": 10, "min_nonstuck": 10, "min_in_c1": 3, "min_in_c2": 3,
          "min_assigned_days": 4, "target_slope_width": 2.0, "auc": 0.7, "sd_day": 0.5, "rho_day": 0.3, "max_days": 40}


def main():
    # ---- 数え方の対照
    t = day_start_ms(0) + 6 * H
    extra = (probe("s1", t + 10 * H, "low_operation_end", "stuck")           # 層化
             + probe("s2", t + 11 * H, "random", "stuck", answered=False)    # 未回答
             + probe("s3", t + 12 * H, "random", "stuck", debug=True)        # 確かめのカード
             + probe("s4", t + 13 * H, "random", "cannot_answer")            # 答えられない
             + probe("s5", t + 14 * H, "random", "working"))                 # 作業（詰まりでない側）
    c = run_count([make(1, 0, 1, extra=extra)], [{"C1": [], "C2": []}])
    check("層化は無作為に数えない", c["random_answered"] == 2 and c["answered_by_stratum"]["low_operation_end"] == 1)
    check("未回答は回答に数えない", c["random_unanswered"] == 1)
    check("確かめのカードは数えない", c["probes_by_stratum"]["random"] == 3)
    check("cannot_answer は詰まり・詰まりでないのどちらにも入れない",
          c["random_stuck"] == 0 and c["random_nonstuck"] == 1 and c["random_excluded"] == 1)

    # ---- 4:00 の区切り（現地 3:59 と 4:01 は別の日）
    t4 = day_start_ms(1)
    lines = [{"type": "meta", "session_start": t4, "s1_mode": "marker"}]
    lines += probe("a", t4 - 59_000 + 1000, "random", "stuck")    # 窓の終わり 3:59:01 → 前の日
    lines += probe("b", t4 + 61_000 + 1000, "random", "stuck")    # 窓の終わり 4:01:01 → この日
    c = run_count([lines], [{"C1": [], "C2": []}])
    check("4:00 の区切りで 2 日に分かれる", c["observed_days"] == 2)

    # ---- 停滞の中の対応（閉区間の境の内と外）
    tt = day_start_ms(0) + 6 * H
    lines = [{"type": "meta", "session_start": tt, "s1_mode": "marker"}]
    lines += probe("x", tt, "random", "stuck")             # 窓の終わり tt − 1000
    lines += probe("y", tt + H, "random", "deliberating")  # 窓の終わり tt + H − 1000
    e = tt - 1000
    c = run_count([lines], [{"C1": [(e, e + 10)], "C2": [(e + 1, tt + H - 1000)]}])
    check("C1 の始まりちょうどは中", c["in_C1"]["answered"] == 1 and c["in_C1"]["stuck"] == 1)
    check("C2 の始まりの手前は外・終わりちょうどは中", c["in_C2"]["answered"] == 1 and c["in_C2"]["nonstuck"] == 1)

    # ---- 割付の日数（日ごとの最後の行）
    d0 = sr.local_day(tt, JST)
    lines = [{"type": "meta", "session_start": tt, "s1_mode": "marker"},
             {"type": "handmark_day", "t": tt, "day": d0, "assigned": "on"},
             {"type": "handmark_day", "t": tt + 1000, "day": d0, "assigned": "unknown"},
             {"type": "handmark_day", "t": tt, "day": d0 + 1, "assigned": "late_first"},
             {"type": "handmark_day", "t": tt + 86_400_000, "day": d0 + 2, "assigned": "off"}]
    c = run_count([lines], [{"C1": [], "C2": []}])
    check("割付の日数は日ごとの最後の行の on・off", c["assigned_days"] == 1)

    # ---- 判定の陽性対照
    eps = {"C1": [], "C2": []}
    full = make(20, 3, 3, late_on_off=6)
    # 停滞の中の回答: 各日の最初の 2 件を C1・C2 に入れる
    for d in range(20):
        t0 = day_start_ms(d) + 6 * H
        eps["C1"].append((t0 - 2000, t0))
        eps["C2"].append((t0 + 30 * 60_000 - 2000, t0 + 30 * 60_000))
    c = run_count([full], [eps])
    check("足りる記録の数（観測日 20・回答 60）", c["observed_days"] == 20 and c["random_answered"] == 60)
    v, parts = sr.verdict(c, 1.5, VALUES)
    check("足りる記録で「届いた」", v == "reached")
    v, _ = sr.verdict(c, 2.5, VALUES)
    check("幅が目標より広ければ届かない（期間内なので続ける）", v == "continue")

    short = make(5, 1, 2)
    short_c = run_count([short], [{"C1": [], "C2": []}])
    short_c["elapsed_days"] = 41   # 期間を過ぎた
    v, _ = sr.verdict(short_c, None, VALUES)
    check("足りないまま最長の期間を過ぎた記録で「判定不能」", v == "undecidable")
    short_c["elapsed_days"] = 5
    v, _ = sr.verdict(short_c, None, VALUES)
    check("足りず期間内の記録で「続ける」", v == "continue")

    # 下限ちょうど（≥ で届く）
    edge = dict(c)
    edge["observed_days"] = VALUES["min_days"]
    v, _ = sr.verdict(edge, 1.5, VALUES)
    check("下限ちょうどで届く", v == "reached")
    # 最長の期間ちょうどで判定不能
    short_c["elapsed_days"] = VALUES["max_days"]
    v, _ = sr.verdict(short_c, None, VALUES)
    check("最長の期間ちょうどで判定不能", v == "undecidable")

    # 値が欠けていれば止める
    try:
        sr.verdict(c, 1.5, {k: v for k, v in VALUES.items() if k != "max_days"})
        check("値の欠けで止める", False)
    except ValueError:
        check("値の欠けで止める", True)

    # 出力に日付・時刻・日ごとの値を含まない（キーの集合で縛る）
    allowed = {"elapsed_days", "observed_days", "probes_by_stratum", "answered_by_stratum", "random_unanswered",
               "random_answered", "random_stuck", "random_nonstuck", "random_excluded", "in_C1", "in_C2",
               "episodes", "assigned_days", "answers_per_observed_day_q", "lambda_per_observed_day", "pi_stuck", "rules"}
    check("出力のキーは件数・率・要約だけ", set(c) == allowed)

    print("SELFTEST", "FAIL" if FAILS else "PASS", "mutate=%s" % sr.MUTATE)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
