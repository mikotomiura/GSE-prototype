#!/usr/bin/env python3
# kit: selftest
"""試行ごとの呼び出し列の型を数え、シナリオごとの分布と 1 試行の実時間を出す（Python 標準ライブラリだけ）。

  call_types.py --gt GT --oracle ORACLE --plan PLAN --out JSON [--clock wall|mono] [--pre-ms N] [--tail-ms N] [--skip-ev a,b,...]
  call_types.py --selftest                                  陽性対照と陰性対照（速い既定）

正解の定義（開始・確定・取消・候補窓）を実機の呼び出し列で決めるための材料と、試行数 n の見直しの材料を出す。
  * 試行の区間 = oracle の trial_begin から trial_end まで。gt の ev 行のうち、区間（の前 --pre-ms・後ろ --tail-ms の余裕を含む）に
    入る行をその試行の呼び出し列とする（既定の余裕は 50 / 500 ms。正解側の記録は送出の後に出るため、最後のキーの結果が
    trial_end の後に来る）。どの試行にも入らない行は unassigned_events に数える。時刻は --clock（既定 wall = 壁時計）で比べる。
  * 型の文字列 = 呼び出しの名前（ev）を時刻順に「 → 」でつないだもの。同じものが 2 回以上続くと「+」に畳む
    （set_marked が 3 回続いて insert_text → 「set_marked+ → insert_text」・1 回だけなら「set_marked → insert_text」）。
    do_command は cmd を、notify は imn を、ui_* は ui_kind を「[…]」で添える（do_command[insertNewline:]）。
    行が 1 つも無い試行は「(なし)」。
  * --skip-ev（既定 key_down）に挙げた ev は型に入れない（打鍵の記録は oracle の送出と重なる）。
    first_rect が変換のたびに挟まって型が細かくなりすぎるなら、--skip-ev key_down,first_rect で畳める。
  * 1 試行の実時間 = oracle の trial_begin から trial_end まで（単調時計・ms）。中央値と 95 パーセンタイル
    （最近順位法: 小さい順に並べた n 個の ceil(0.95·n) 番目）を、シナリオごとと全体で出す。

出力の JSON は src（gt のヘッダ）× シナリオ（plan の trial 行）ごと。Windows の 2 経路（IMM / TSF）を比べるときは、
経路ごとの gt で 2 回回して、出力の types を並べる。
exit 0 = 出した / 1 = 完結した試行（oracle に begin と end がそろい、plan にある）が 1 つも無い / 2 = 入力が読めない・使い方の誤り。
"""
import argparse
import bisect
import json
import math
import os
import subprocess
import sys
import tempfile

QUALIFIERS = {"do_command": "cmd", "notify": "imn"}  # ui_* は ui_kind


class InputError(Exception):
    """入力が読めない・契約に合わない。"""


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def read_jsonl(path):
    rows = []
    try:
        f = open(path, encoding="utf-8")
    except OSError as e:
        raise InputError("%s を開けない（%s）" % (path, e.__class__.__name__))
    with f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                raise InputError("%s の %d 行目が JSON として読めない" % (path, n))
    return rows


def load_plan(path):
    """{trial_id: scenario}。"""
    scen = {}
    for row in read_jsonl(path):
        if isinstance(row, dict) and row.get("kind") == "trial":
            tid, sc = row.get("trial_id"), row.get("scenario")
            if not isinstance(tid, str) or not isinstance(sc, str):
                raise InputError("%s: trial 行に trial_id / scenario（文字列）が無い" % path)
            scen[tid] = sc
    return scen


def load_oracle(path, clock):
    """完結した試行 [{trial_id, begin, end, dur_ms}]（begin / end は --clock の時刻 ms）と、未完結の数。"""
    trials, order = {}, []
    for row in read_jsonl(path):
        if not isinstance(row, dict) or row.get("kind") not in ("trial_begin", "trial_end"):
            continue
        tid = row.get("trial_id")
        wall, mono = row.get("t_wall_ms"), row.get("t_mono_ns")
        if not (isinstance(tid, str) and _is_int(wall) and _is_int(mono)):
            raise InputError("%s: %s に trial_id / t_wall_ms / t_mono_ns が無い" % (path, row["kind"]))
        if tid not in trials:
            trials[tid] = {"trial_id": tid}
            order.append(tid)
        field = "begin" if row["kind"] == "trial_begin" else "end"
        if field in trials[tid]:
            raise InputError("%s: 同じ trial_id に %s が 2 つある" % (path, row["kind"]))
        trials[tid][field] = (wall if clock == "wall" else mono / 1e6, mono / 1e6)
    done, incomplete = [], 0
    for tid in order:
        t = trials[tid]
        if "begin" in t and "end" in t:
            done.append({"trial_id": tid, "begin": t["begin"][0], "end": t["end"][0], "dur_ms": t["end"][1] - t["begin"][1]})
        else:
            incomplete += 1
    return done, incomplete


def token(row):
    ev = row["ev"]
    key = QUALIFIERS.get(ev, "ui_kind" if ev.startswith("ui_") else None)
    if key is not None and key in row:
        return "%s[%s]" % (ev, row[key])
    return ev


def load_gt(path, clock, skip):
    """(src, [(時刻 ms, token)])。ファイルの順のまま。"""
    src, events = None, []
    for row in read_jsonl(path):
        if not isinstance(row, dict):
            continue
        if row.get("kind") == "header":
            src = row.get("src")
        elif row.get("kind") == "ev":
            ev, wall, mono = row.get("ev"), row.get("t_wall_ms"), row.get("t_mono_ns")
            if not (isinstance(ev, str) and _is_int(wall) and _is_int(mono)):
                raise InputError("%s: ev 行に ev / t_wall_ms / t_mono_ns が無い" % path)
            if ev in skip:
                continue
            events.append((wall if clock == "wall" else mono / 1e6, token(row)))
    if not isinstance(src, str):
        raise InputError("%s: gt のヘッダ（src）が無い" % path)
    return src, events


def fold(tokens):
    out = []
    i = 0
    while i < len(tokens):
        j = i
        while j + 1 < len(tokens) and tokens[j + 1] == tokens[i]:
            j += 1
        out.append(tokens[i] + ("+" if j > i else ""))
        i = j + 1
    return " → ".join(out) if out else "(なし)"


def stats(values):
    if not values:
        return None
    v = sorted(values)
    n = len(v)
    median = v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
    p95 = v[max(0, math.ceil(0.95 * n) - 1)]
    r = lambda x: round(x, 3)
    return {"n": n, "median_ms": r(median), "p95_ms": r(p95), "min_ms": r(v[0]), "max_ms": r(v[-1])}


def analyze(src, events, trials, scenarios, pre_ms, tail_ms):
    unknown = [t["trial_id"] for t in trials if t["trial_id"] not in scenarios]
    if unknown:
        raise InputError("oracle の試行が plan に無い（%d 件・例 %s）。plan と oracle の組を確かめること" % (len(unknown), unknown[0]))
    trials = sorted(trials, key=lambda t: t["begin"])
    starts = [t["begin"] - pre_ms for t in trials]
    per = [[] for _ in trials]
    unassigned = 0
    for when, tok in events:
        i = bisect.bisect_right(starts, when) - 1
        if i >= 0 and when <= trials[i]["end"] + tail_ms:
            per[i].append(tok)
        else:
            unassigned += 1
    by = {}
    for t, toks in zip(trials, per):
        s = by.setdefault(scenarios[t["trial_id"]], {"trials": 0, "types": {}, "durations": []})
        s["trials"] += 1
        typ = fold(toks)
        s["types"][typ] = s["types"].get(typ, 0) + 1
        s["durations"].append(t["dur_ms"])
    out = {}
    for sc in sorted(by, key=lambda x: (len(x), x)):  # S1, S2, …, S10, …
        s = by[sc]
        ordered = sorted(s["types"].items(), key=lambda kv: (-kv[1], kv[0]))
        out[sc] = {"trials": s["trials"], "types": dict(ordered), "duration_ms": stats(s["durations"])}
    return {
        "src": src,
        "params": {"pre_ms": pre_ms, "tail_ms": tail_ms},
        "trials_measured": len(trials),
        "planned_not_run": len(set(scenarios) - set(t["trial_id"] for t in trials)),
        "unassigned_events": unassigned,
        "duration_ms": stats([t["dur_ms"] for t in trials]),
        "by_scenario": out,
    }


# --- selftest begin ---
def _selftest():
    fails = []

    def check(ok, what):
        print("  %s %s" % ("✅" if ok else "❌", what))
        if not ok:
            fails.append(what)

    def dump(path, rows):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")

    # gt の単調時計は oracle と 2.5 s ずれる（試行の間隔 4 s の半端。ちょうど 4 s だと次の試行の区間に入ってしまう）
    T0, MONO0, MONO_SKEW = 1_700_000_000_000, 9_000_000_000_000, 2_500_000_000
    # 試行: (trial_id, scenario, 長さ ms, gt の呼び出し列)。gt の行は (試行の先頭からの ms, ev, 付随)。
    def ev(at, name, **kw):
        return (at, name, kw)
    mac = [
        ("t00001", "S1", 1000, [ev(10, "key_down", vk=0), ev(20, "set_marked", len=1), ev(120, "set_marked", len=2),
                                ev(220, "set_marked", len=3), ev(320, "insert_text", len=3)]),
        ("t00002", "S1", 1000, [ev(10, "set_marked", len=1), ev(300, "insert_text", len=1)]),
        ("t00003", "S1", 1000, [ev(10, "set_marked", len=1), ev(120, "set_marked", len=2), ev(1040, "insert_text", len=2)]),  # trial_end の後（余裕の中）
        ("t00004", "S2", 1000, [ev(10, "set_marked", len=1), ev(200, "do_command", cmd="insertNewline:"), ev(300, "insert_text", len=1)]),
        ("t00005", "S2", 1000, [ev(10, "set_marked", len=1), ev(200, "do_command", cmd="cancelOperation:"), ev(210, "unmark")]),
        ("t00006", "S3", 1000, []),
    ]
    # 長さ 100…2000 ms の 20 試行（S4）→ 中央値 1050・p95 1900
    durs = [("t%05d" % (7 + k), "S4", 100 * (k + 1), [ev(10, "set_marked", len=1)]) for k in range(20)]
    GAP = 3000

    def build(rows, src, header_extra=None):
        oracle = [{"kind": "header", "format": "oracle/1"}]
        plan = [{"kind": "header", "format": "plan/1"}]
        gt = [{"kind": "header", "format": "gt/1", "src": src}]
        base = T0
        for tid, sc, length, evs in rows:
            plan.append({"kind": "trial", "trial_id": tid, "scenario": sc})
            oracle.append({"kind": "trial_begin", "trial_id": tid, "t_wall_ms": base, "t_mono_ns": MONO0 + (base - T0) * 1_000_000})
            oracle.append({"kind": "trial_end", "trial_id": tid, "t_wall_ms": base + length, "t_mono_ns": MONO0 + (base + length - T0) * 1_000_000})
            for at, name, kw in evs:
                row = {"kind": "ev", "t_wall_ms": base + at, "t_mono_ns": MONO0 + MONO_SKEW + (base + at - T0) * 1_000_000, "ev": name}
                row.update(kw)
                gt.append(row)
            base += length + GAP
        return oracle, plan, gt

    with tempfile.TemporaryDirectory() as tmp:
        def run(rows, src, clock="wall", skip=("key_down",), pre=50, tail=500, extra_gt=()):
            oracle, plan, gt = build(rows, src)
            gt = gt + list(extra_gt)
            paths = {n: os.path.join(tmp, n + ".jsonl") for n in ("oracle", "plan", "gt")}
            dump(paths["oracle"], oracle); dump(paths["plan"], plan); dump(paths["gt"], gt)
            trials, _ = load_oracle(paths["oracle"], clock)
            s, events = load_gt(paths["gt"], clock, set(skip))
            return analyze(s, events, trials, load_plan(paths["plan"]), pre, tail)

        r = run(mac + durs, "mac_nstic")
        s1, s2 = r["by_scenario"]["S1"]["types"], r["by_scenario"]["S2"]["types"]
        check(s1 == {"set_marked+ → insert_text": 2, "set_marked → insert_text": 1}, "既知の列が期待する型になり、連続は + に畳む（S1: %s）" % s1)
        check(s2 == {"set_marked → do_command[cancelOperation:] → unmark": 1, "set_marked → do_command[insertNewline:] → insert_text": 1},
              "do_command は cmd を添える（S2: %s）" % list(s2))
        check(r["by_scenario"]["S3"]["types"] == {"(なし)": 1}, "行が 1 つも無い試行は「(なし)」")
        check([k for k in r["by_scenario"]] == ["S1", "S2", "S3", "S4"] and r["by_scenario"]["S1"]["trials"] == 3 and r["by_scenario"]["S4"]["trials"] == 20,
              "シナリオ別の件数（%s）" % {k: v["trials"] for k, v in r["by_scenario"].items()})
        check("key_down" not in json.dumps(r, ensure_ascii=False), "既定では key_down を型に入れない")
        check(run(mac[:1], "mac_nstic", skip=())["by_scenario"]["S1"]["types"] == {"key_down → set_marked+ → insert_text": 1}, "--skip-ev を空にすると key_down も型に入る")
        d = r["by_scenario"]["S4"]["duration_ms"]
        check(d["n"] == 20 and d["median_ms"] == 1050 and d["p95_ms"] == 1900 and d["min_ms"] == 100 and d["max_ms"] == 2000,
              "試行の実時間: 中央値 %s・95 パーセンタイル %s ms" % (d["median_ms"], d["p95_ms"]))
        check(r["duration_ms"]["n"] == 26 and r["src"] == "mac_nstic", "全体の実時間と src（n=%d）" % r["duration_ms"]["n"])

        # 区間の外の行は数える（試行の間の待ちに入る行・余裕を 0 にすると trial_end の後の insert_text は外れる）
        stray = [{"kind": "ev", "t_wall_ms": T0 - 5000, "t_mono_ns": 0, "ev": "focus_in"}]
        r2 = run(mac, "mac_nstic", extra_gt=stray)
        check(r2["unassigned_events"] == 1, "どの試行の区間にも入らない行は unassigned_events に数える")
        r3 = run(mac, "mac_nstic", tail=0)
        check(r3["unassigned_events"] == 1 and r3["by_scenario"]["S1"]["types"].get("set_marked+", 0) == 1,
              "後ろの余裕が無いと、trial_end の後に来る呼び出しは外れる（型が変わる）")

        # 単調時計を選ぶと、gt の単調時計が 2.5 s ずれているので全部外れる（時計の選択が効く）
        rm = run(mac, "mac_nstic", clock="mono")
        check(rm["unassigned_events"] == sum(len(x[3]) for x in mac) - 1, "--clock mono は単調時計で比べる（ずれた時計では割り当たらない）")

        # Windows: notify は imn・ui_* は ui_kind を添える
        win = [("t00001", "S1", 1000, [ev(10, "tsf_start"), ev(20, "tsf_update", len=1), ev(120, "tsf_update", len=2), ev(200, "ui_begin", ui_kind="candidate"),
                                        ev(210, "ui_update", ui_kind="candidate"), ev(400, "ui_end", ui_kind="candidate"), ev(410, "tsf_end", result_len=2)]),
               ("t00002", "S2", 1000, [ev(10, "start_comp"), ev(20, "notify", imn=5), ev(30, "notify", imn=5), ev(40, "comp", flags=8, comp_len=1, result_len=0), ev(50, "end_comp")])]
        r = run(win, "win_tsf")
        check(r["by_scenario"]["S1"]["types"] == {"tsf_start → tsf_update+ → ui_begin[candidate] → ui_update[candidate] → ui_end[candidate] → tsf_end": 1},
              "ui_* は ui_kind を添える（TSF）")
        check(r["by_scenario"]["S2"]["types"] == {"start_comp → notify[5]+ → comp → end_comp": 1}, "notify は imn を添える（IMM）")

        # 入力の契約と終了コード
        me = os.path.abspath(__file__)
        oracle, plan, gt = build(mac, "mac_nstic")
        paths = {n: os.path.join(tmp, "cli-" + n + ".jsonl") for n in ("oracle", "plan", "gt")}
        dump(paths["oracle"], oracle); dump(paths["plan"], plan); dump(paths["gt"], gt)
        out = os.path.join(tmp, "out.json")

        def cli(o=out, **override):
            p = dict(paths)
            p.update(override)
            r = subprocess.run([sys.executable, me, "--gt", p["gt"], "--oracle", p["oracle"], "--plan", p["plan"], "--out", o],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return r.returncode, r.stdout.decode("utf-8", "replace")

        rc, text = cli()
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        check(rc == 0 and data["by_scenario"]["S1"]["types"]["set_marked+ → insert_text"] == 2, "CLI: 出力の JSON にシナリオ別の型（exit %d）" % rc)
        dump(paths["plan"] + "x", [x for x in plan if x.get("trial_id") != "t00001"])
        rc, text = cli(o=out + "2", plan=paths["plan"] + "x")
        check(rc == 2 and not os.path.exists(out + "2"), "oracle の試行が plan に無ければ拒否する（exit %d・出力を書かない）" % rc)
        dump(paths["oracle"] + "x", [{"kind": "header", "format": "oracle/1"}])
        rc, _ = cli(o=out + "3", oracle=paths["oracle"] + "x")
        check(rc == 1, "完結した試行が 1 つも無ければ空振りで exit 1（exit %d）" % rc)
        rc, _ = cli(o=out + "4", gt=os.path.join(tmp, "nothing"))
        check(rc == 2, "gt が開けなければ exit 2（exit %d）" % rc)

    if fails:
        print("  ---- call_types selftest 失敗 %d 件 ----" % len(fails))
        return 1
    print("  ---- call_types selftest すべて緑 ----")
    return 0
# --- selftest end ---


def main(argv=None):
    ap = argparse.ArgumentParser(description="試行ごとの呼び出し列の型を数え、シナリオごとの分布と 1 試行の実時間を出す")
    ap.add_argument("--selftest", action="store_true", help="陽性対照と陰性対照を回す")
    ap.add_argument("--gt", help="正解の生ログ（gt/1）")
    ap.add_argument("--oracle", help="実行器の出力（oracle/1）")
    ap.add_argument("--plan", help="計画（plan/1）")
    ap.add_argument("--out", help="結果の JSON の出力先")
    ap.add_argument("--clock", choices=("wall", "mono"), default="wall", help="gt と oracle の時刻を比べる時計（既定 wall）")
    ap.add_argument("--pre-ms", type=int, default=50, help="試行の区間の前の余裕（既定 50）")
    ap.add_argument("--tail-ms", type=int, default=500, help="試行の区間の後ろの余裕（既定 500）")
    ap.add_argument("--skip-ev", default="key_down", help="型に入れない ev のカンマ区切り（既定 key_down）")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.gt and args.oracle and args.plan and args.out):
        ap.error("--gt / --oracle / --plan / --out がすべて要る")
    if args.pre_ms < 0 or args.tail_ms < 0:
        ap.error("--pre-ms / --tail-ms は 0 以上")
    skip = set(x for x in args.skip_ev.split(",") if x)
    try:
        trials, incomplete = load_oracle(args.oracle, args.clock)
        src, events = load_gt(args.gt, args.clock, skip)
        result = analyze(src, events, trials, load_plan(args.plan), args.pre_ms, args.tail_ms)
    except InputError as e:
        print("call_types: %s" % e, file=sys.stderr)
        return 2
    result["trials_incomplete"] = incomplete
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("src %s・試行 %d（未完結 %d・計画にあって実行されなかった %d）・区間に入らなかった行 %d" % (
        result["src"], result["trials_measured"], incomplete, result["planned_not_run"], result["unassigned_events"]))
    for sc, s in result["by_scenario"].items():
        d = s["duration_ms"]
        print("%s（%d 試行・実時間 中央値 %s ms・p95 %s ms）" % (sc, s["trials"], d["median_ms"], d["p95_ms"]))
        for typ, n in s["types"].items():
            print("  %4d  %s" % (n, typ))
    if result["trials_measured"] == 0:
        print("call_types: 完結した試行が 1 つも無い（oracle の trial_begin / trial_end と plan を確かめること）", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
