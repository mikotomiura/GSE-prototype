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


def probe(pid, t, stratum, cat, answered=True, debug=False, latency=5000):
    a = {"type": "probe_assignment", "probe_id": pid, "scheduled_ts": t, "session_elapsed_ms": 1000, "stratum": stratum}
    lab = {"type": "activity_label", "t": t + 5000, "probe_id": pid, "category": cat if answered else "cannot_answer",
           "answered": answered, "latency_ms": latency, "recall_window_start_ms": t - 31_000, "recall_window_end_ms": t - 1000}
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


def run_count(lines_list, episodes, max_days=None, table=None):
    tmp = tempfile.mkdtemp()
    recs = []
    for i, lines in enumerate(lines_list):
        p = os.path.join(tmp, "r%03d.ndjson" % i)
        write(p, lines)
        recs.append(sr.read_record(p))
    tb = None
    if table is not None:
        tp = os.path.join(tmp, "handmark_assignment.json")
        with open(tp, "w", encoding="utf-8") as f:
            json.dump(table, f)
        tb = sr.read_table(tp)
    return sr.count(recs, episodes, JST, max_days=max_days, table=tb)


VALUES = {"min_days": 10, "min_stuck": 10, "min_nonstuck": 10, "min_in_c1": 3, "min_in_c2": 3,
          "min_assigned_days": 4, "max_days": 20}


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
    lines = [{"type": "meta", "session_start": t4 - H, "s1_mode": "marker"}]   # 前の日の 3:00 から（窓の 1 日目）
    lines += probe("a", t4 - 59_000 + 1000, "random", "stuck")    # 窓の終わり 3:59:01 → 前の日
    lines += probe("b", t4 + 61_000 + 1000, "random", "stuck")    # 窓の終わり 4:01:01 → この日
    c = run_count([lines], [{"C1": [], "C2": []}])
    check("4:00 の区切りで 2 日に分かれる", c["observed_days"] == 2)

    # ---- 回答の遅れの上限（S1-A4・10 分ちょうどは数え、超えたら未回答と同じ）
    tl = day_start_ms(0) + 6 * H
    lines = [{"type": "meta", "session_start": tl, "s1_mode": "marker"}]
    lines += probe("l1", tl, "random", "stuck", latency=600_000)
    lines += probe("l2", tl + H, "random", "stuck", latency=600_001)
    c = run_count([lines], [{"C1": [], "C2": []}])
    check("遅れ 10 分ちょうどは数え、超えた回答は数えない",
          c["random_answered"] == 1 and c["random_stuck"] == 1 and c["random_over_latency_cap"] == 1)

    # ---- 窓が日の切れ目をまたぐ回答は数えない（S1-D1）
    lines = [{"type": "meta", "session_start": t4, "s1_mode": "marker"}]
    lines += probe("c", t4 + 10_000, "random", "stuck")       # 窓 [3:59:39, 4:00:09] → またぐ
    lines += probe("d", t4 + 40_000, "random", "stuck")       # 窓 [4:00:09, 4:00:39] → またがない
    c = run_count([lines], [{"C1": [], "C2": []}])
    check("日をまたぐ窓は数えず、件数を別に出す",
          c["random_answered"] == 1 and c["random_cross_day"] == 1 and c["random_stuck"] == 1)

    # ---- 停滞の中の対応（閉区間の境の内と外）
    tt = day_start_ms(0) + 6 * H
    lines = [{"type": "meta", "session_start": tt, "s1_mode": "marker"}]
    lines += probe("x", tt, "random", "stuck")             # 窓の終わり tt − 1000
    lines += probe("y", tt + H, "random", "deliberating")  # 窓の終わり tt + H − 1000
    # 窓は [t − 31 000, t − 1000]（30 秒）。過半の規則（S1-B1・判断 22）: 重なりが 15 秒ちょうどなら中、1 ms 足りなければ外
    c = run_count([lines], [{"C1": [(tt - 16_000, tt + 5000)], "C2": [(tt + H - 15_999, tt + H + 5000)]}])
    check("窓の半分ちょうどが停滞に入れば中", c["in_C1"]["answered"] == 1 and c["in_C1"]["stuck"] == 1)
    check("半分に 1 ms 足りなければ外（窓の終わりは停滞の中でも）", c["in_C2"]["answered"] == 0)
    # 窓の後半が停滞・前半が別の停滞（同じ種類）なら、重なりの和で数える
    c = run_count([lines], [{"C1": [(tt - 31_000, tt - 24_000), (tt - 8000, tt)], "C2": []}])
    check("同じ種類の停滞 2 つの重なりの和（7 + 7 秒）は半分に足りず外", c["in_C1"]["answered"] == 0)
    c = run_count([lines], [{"C1": [(tt - 31_000, tt - 23_000), (tt - 8000, tt)], "C2": []}])
    check("重なりの和が 8 + 7 秒で半分ちょうどなら中", c["in_C1"]["answered"] == 1)
    # 丸ごとの規則（感度）は引数で選べる
    tmp = tempfile.mkdtemp()
    pth = os.path.join(tmp, "r.ndjson")
    write(pth, lines)
    cc = sr.count([sr.read_record(pth)], [{"C1": [(tt - 31_000, tt)], "C2": [(tt - 30_999, tt)]}], JST, rule="contain")
    check("丸ごとの規則: 窓の始まりちょうどからなら中・1 ms 遅れれば外",
          cc["in_C1"]["answered"] == 1 and cc["in_C2"]["answered"] == 0)

    # ---- 時点不明（S1-B2・判断 23）: 窓が 1 つの観測区間に丸ごと入らない回答は数えない
    c = run_count([lines], [{"C1": [], "C2": [], "obs": [(tt - 31_000, tt + 10 * H)]}])
    check("窓の始まりちょうどから観測されていれば数える", c["random_answered"] == 2 and c["random_window_unobserved"] == 0)
    c = run_count([lines], [{"C1": [], "C2": [], "obs": [(tt - 30_999, tt + 10 * H)]}])
    check("窓の始まりが観測区間の 1 ms 前なら時点不明で数えない",
          c["random_answered"] == 1 and c["random_window_unobserved"] == 1)
    c = run_count([lines], [{"C1": [], "C2": [], "obs": [(tt - 40_000, tt - 20_000), (tt - 19_000, tt + 10 * H)]}])
    check("窓の中に観測の空きがあれば時点不明", c["random_window_unobserved"] == 1)

    # ---- 時計の狂った起動で始まった記録は名前で除く（PR #435 の判断 3）
    check("1976 年・1970 年の名前は除き、2026 年は残す",
          sr.clock_excluded("gse_o1_19760331_150024.ndjson") and sr.clock_excluded("gse_s1_19700101_090000.ndjson")
          and not sr.clock_excluded("gse_s1_20261126_100000.ndjson"))

    # ---- 割付の日数（日ごとの最後の行）
    d0 = sr.local_day(tt, JST)
    lines = [{"type": "meta", "session_start": tt, "s1_mode": "marker"},
             {"type": "handmark_day", "t": tt, "day": d0, "assigned": "on"},
             {"type": "handmark_day", "t": tt + 1000, "day": d0, "assigned": "unknown"},
             {"type": "handmark_day", "t": tt, "day": d0 + 1, "assigned": "late_first"},
             {"type": "handmark_day", "t": tt + 86_400_000, "day": d0 + 2, "assigned": "off"}]
    c = run_count([lines], [{"C1": [], "C2": []}])
    check("割付の日数は日ごとの最後の行の on・off", c["assigned_days"] == 1)

    # ---- 判定の陽性対照（第 2 版: 最長の期間まで続け、達したら判定できる／判定不能）
    M = VALUES["max_days"]
    eps = {"C1": [], "C2": []}
    full = make(M + 5, 3, 3, late_on_off=6)        # 最長の期間より 5 日長い記録
    # 停滞の中の回答: 各日の最初の 2 件を C1・C2 に入れる
    for d in range(M + 5):
        t0 = day_start_ms(d) + 6 * H
        eps["C1"].append((t0 - 31_000, t0))
        eps["C2"].append((t0 + 30 * 60_000 - 31_000, t0 + 30 * 60_000))
    c = run_count([full], [eps], max_days=M)
    check("窓の中だけ数える（観測日 20・回答 60・割付は窓の中の 1 日）",
          c["observed_days"] == M and c["random_answered"] == 3 * M and c["assigned_days"] == 1)
    check("経過日数は窓で切らない", c["elapsed_days"] == M + 5)
    v, parts = sr.verdict(c, dict(VALUES, min_assigned_days=1))
    check("足りる記録が最長の期間に達して「判定できる」", v == "decidable")
    v, _ = sr.verdict(c, VALUES)
    check("割付の日数が足りなければ「判定不能」", v == "undecidable")

    early = run_count([make(M - 1, 3, 3, late_on_off=6)], [eps], max_days=M)
    check("下限は満たす（期間の手前）", early["observed_days"] == M - 1 and early["random_stuck"] >= 10)
    v, _ = sr.verdict(early, VALUES)
    check("下限を満たしても最長の期間の手前は「続ける」（早く終わらない）", v == "continue")

    short = make(5, 1, 2)
    short_c = run_count([short], [{"C1": [], "C2": []}], max_days=M)
    v, _ = sr.verdict(short_c, VALUES)
    check("足りず期間内の記録で「続ける」", v == "continue")
    short_c["elapsed_days"] = M    # 最長の期間ちょうど
    v, _ = sr.verdict(short_c, VALUES)
    check("足りないまま最長の期間ちょうどで「判定不能」", v == "undecidable")

    # 下限ちょうど（≥ で届く）
    edge = dict(c)
    edge["observed_days"] = VALUES["min_days"]
    v, _ = sr.verdict(edge, dict(VALUES, min_assigned_days=1))
    check("下限ちょうどで判定できる", v == "decidable")

    # 値が欠けていれば止める・窓で数えていなければ止める
    try:
        sr.verdict(c, {k: x for k, x in VALUES.items() if k != "max_days"})
        check("値の欠けで止める", False)
    except ValueError:
        check("値の欠けで止める", True)
    try:
        sr.verdict(run_count([full], [eps]), VALUES)
        check("窓なしの数えで止める", False)
    except ValueError:
        check("窓なしの数えで止める", True)

    # 入力と値の検査（Codex の指摘・止める側に倒す）
    def bad_record(name, lines):
        try:
            run_count([lines], [eps])
            check(name, False)
        except (ValueError, KeyError):
            check(name, True)
    base = make(1, 1, 1)
    rev = json.loads(json.dumps(base))
    for x in rev:
        if x.get("type") == "activity_label":
            x["recall_window_start_ms"], x["recall_window_end_ms"] = x["recall_window_end_ms"], x["recall_window_end_ms"]
    bad_record("長さ 0 の回答の窓で止める", rev)
    unk = json.loads(json.dumps(base))
    for x in unk:
        if x.get("type") == "activity_label":
            x["category"] = "napping"
    bad_record("知らない回答の類で止める", unk)
    dup = base + [x for x in base if x.get("type") == "activity_label"]
    bad_record("同じ問いの回答の行が 2 つで止める", dup)
    neg = json.loads(json.dumps(base))
    for x in neg:
        if x.get("type") == "activity_label":
            x["latency_ms"] = -1
    bad_record("負の遅れで止める", neg)
    for name, vv in (("値が 0 で止める", dict(VALUES, min_stuck=0)), ("min_days が max_days を越えると止める",
                     dict(VALUES, min_days=VALUES["max_days"] + 1))):
        try:
            sr.check_values(vv)
            check(name, False)
        except ValueError:
            check(name, True)
    cx = run_count([make(2, 3, 3, extra=probe("px", day_start_ms(0) + 9 * H, "random", "cannot_answer"))], [eps])
    check("日数の見込みの λ は cannot_answer を除く",
          cx["lambda_valid_per_observed_day"] == (cx["random_stuck"] + cx["random_nonstuck"]) / cx["observed_days"]
          and cx["lambda_valid_per_observed_day"] < cx["lambda_per_observed_day"])

    # ---- 窓の 1 日目は段 1 の行（最初の meta の session_start）から（判断 51）
    dS = sr.local_day(day_start_ms(0) + 6 * H, JST)
    stray = make(M + 5, 3, 3)
    stray.insert(1, {"type": "key", "t": day_start_ms(-30) + 6 * H, "category": "alphabetic", "press": True})
    cs = run_count([stray], [eps], max_days=M)
    check("時計の狂った早い行があっても窓の 1 日目は session_start の日（経過・観測日・回答）",
          cs["elapsed_days"] == M + 5 and cs["observed_days"] == M and cs["random_answered"] == 3 * M)
    stray_ans = make(3, 3, 3, extra=probe("old", day_start_ms(-30) + 6 * H, "random", "stuck"))
    cs = run_count([stray_ans], [eps], max_days=M)
    check("窓の 1 日目より前の回答は数えない", cs["random_answered"] == 9)
    # 表の s1_start_day はずれの日数を出すだけで、窓は記録の 1 日目のまま（S1-F2）
    tb = {"version": 1, "s1_start_day": dS + 2, "early_days": 10, "late_start_day": dS + 12, "days": [True, False]}
    ct = run_count([full], [eps], max_days=M, table=tb)
    check("表の s1_start_day が 2 日ずれても窓は記録の 1 日目から（ずれは +2 と出す）",
          ct["table_start_offset_days"] == 2 and ct["observed_days"] == M and ct["random_answered"] == 3 * M)
    check("表が無ければずれは None", c["table_start_offset_days"] is None)

    # ---- 前期の件数（記述・判断 47・51）: 窓の 1 日目から late_start_day の前日まで
    ex = make(6, 3, 3)    # 1 日 3 件・各日の 1 件目が詰まり
    ex.append({"type": "handmark_day", "t": day_start_ms(3) + 6 * H, "day": dS + 3, "assigned": "late_first",
               "late_start_day": dS + 3})
    ex.append({"type": "handmark_day", "t": day_start_ms(4) + 6 * H, "day": dS + 4, "assigned": "on",
               "late_start_day": None})
    e1 = run_count([ex], [eps], max_days=M)["early"]
    check("前期は late_start_day の前日まで（観測日 3・詰まり 3・詰まりでない 6・日数 3）",
          e1 is not None and e1["early_days"] == 3 and e1["observed_days"] == 3
          and e1["random_stuck"] == 3 and e1["random_nonstuck"] == 6)
    check("前期の C1・C2 の中（各日の 1 件目・2 件目）",
          e1["in_C1"] == {"answered": 3, "stuck": 3, "nonstuck": 0}
          and e1["in_C2"] == {"answered": 3, "stuck": 0, "nonstuck": 3})
    e2 = run_count([make(6, 3, 3)], [eps], max_days=M, table=dict(tb, s1_start_day=dS, late_start_day=dS + 2,
                                                                  early_days=2))["early"]
    check("表だけでも前期を数える（late_start_day は表から）", e2 is not None and e2["observed_days"] == 2)
    check("late_start_day が分からなければ前期は None", run_count([make(6, 3, 3)], [eps])["early"] is None)
    ca = run_count([ex], [eps], table=dict(tb, s1_start_day=dS, late_start_day=dS + 5, early_days=5))
    check("late_start_day が記録と表で食い違えば判定は止めず前期は None（理由つき）",
          ca["early"] is None and ca["early_unavailable"] == "late_start_day_ambiguous")
    cb = run_count([make(6, 3, 3)], [eps], table=dict(tb, s1_start_day=dS - 5, late_start_day=dS, early_days=5))
    check("前期の終わりが窓の 1 日目より後でなければ前期は None（理由つき）",
          cb["early"] is None and cb["early_unavailable"] == "late_start_not_after_window_start")
    check("前期の cannot_answer を数える",
          run_count([make(4, 3, 3, extra=probe("ce", day_start_ms(1) + 9 * H, "random", "cannot_answer"))], [eps],
                    table=dict(tb, s1_start_day=dS, late_start_day=dS + 3, early_days=3))["early"]["random_excluded"] == 1)
    check("前期の出力のキーは件数だけ", set(e1) == {"early_days", "observed_days", "random_stuck", "random_nonstuck",
                                          "random_excluded", "in_C1", "in_C2"})
    cl = run_count([stray_ans], [eps])
    check("max_days が無くても窓の 1 日目より前の回答は数えない", cl["random_answered"] == 9)
    fut = make(3, 3, 3)
    fut.insert(1, {"type": "key", "t": 4_102_444_800_000 + 86_400_000, "category": "alphabetic", "press": True})  # 2100 年
    check("年の範囲の外へ跳んだ時刻は経過に数えない", run_count([fut], [eps], max_days=M)["elapsed_days"] == 3)
    try:
        run_count([make(1, 1, 1)], [eps], table=dict(tb, early_days=0, late_start_day=tb["s1_start_day"]))
        check("表の early_days が 1 未満なら止める", False)
    except ValueError:
        check("表の early_days が 1 未満なら止める", True)
    try:
        run_count([make(1, 1, 1)], [eps], table=dict(tb, early_days=3))
        check("表の late_start_day が s1_start_day + early_days でなければ止める", False)
    except ValueError:
        check("表の late_start_day が s1_start_day + early_days でなければ止める", True)
    nometa = [x for x in make(1, 1, 1) if x.get("type") != "meta"]
    bad_record("最初の meta に session_start が無ければ止める", nometa)

    # 出力に日付・時刻・日ごとの値を含まない（キーの集合で縛る）
    allowed = {"elapsed_days", "observed_days", "probes_by_stratum", "answered_by_stratum", "random_unanswered",
               "random_answered", "random_stuck", "random_nonstuck", "random_excluded", "in_C1", "in_C2",
               "episodes", "assigned_days", "answers_per_observed_day_q", "lambda_per_observed_day",
               "lambda_valid_per_observed_day", "pi_stuck", "rules",
               "window_days", "random_cross_day", "random_over_latency_cap", "random_window_unobserved",
               "early", "early_unavailable", "table_start_offset_days"}
    check("出力のキーは件数・率・要約だけ", set(c) == allowed)

    print("SELFTEST", "FAIL" if FAILS else "PASS", "mutate=%s" % sr.MUTATE)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
