"""DUX・SWELL-KW の停滞の型（extend/conditions.md E5 の X1〜X4）。記述だけ・検定なし。

使い方:
  python3 -I analyze_extend.py <seed> <holdout.json> <dux_work> <dux_work_tabnav> <swell_work> <out_dir>
  python3 -I analyze_extend.py --selftest
出力は集計値だけ（書き手・session・人の番号・ファイル名・日時を出さない）: <out_dir>/extend.json・counts.json。
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("..", "../public", "../checks", "../../20261102-public-data-landscape/scripts",
          "../../20261101-klicke-early-stall-trigger/scripts"):
    sys.path.insert(0, os.path.join(HERE, p))
import types_core as tc  # noqa: E402
import analyze_landscape as land  # noqa: E402
import analyze_public as ap  # noqa: E402
import analyze_checks as ac  # noqa: E402
import analyze_item2 as t2  # noqa: E402

DUX_CLASSES = ("move_or_click", "delete2", "silence")
SW_CLASSES = tc.CLASSES
SW3 = ("move_or_click", "delete2", "silence")


class Sess:
    """1 セッション（DUX は session・SWELL-KW は 1 ファイル）。"""

    def __init__(self, d, drop_focus=False):
        self.d = d
        self.s = land.Session(d, clicks=d["clicks"])
        focus = None if (drop_focus or d["focus"] is None) else d["focus"]
        self.rec = tc.Rec(self.s.text, self.s.delete, self.s.other_nontext, self.s.intervals, clicks=d["clicks"],
                          focus=focus, moves=d["moves"], block_starts=[self.s.t_start])
        self.cond = d["cond"]

    def rows(self):
        out = []
        for o in self.s.onsets:
            r = self.rec.stall(o[0], o[1])
            r["third"] = ap.third_of(self.s, o[1])
            out.append(r)
        return out

    def seg(self):
        tcat = [(t, c) for t, c in self.s.keys if c in t2.TEXT]
        return ac.Seg(self.rec, tcat, self.s.onsets)


def load(work, hold):
    ds = []
    for n in sorted(os.listdir(work)):
        if n == "build_summary.json" or not n.endswith(".json"):
            continue
        d = json.load(open(os.path.join(work, n)))
        if d["writer"] in hold:
            sys.exit("取っておく書き手が中間に入っている")
        ds.append(d)
    return ds


def group(sessions):
    w = {}
    for x in sessions:
        w.setdefault(x.d["writer"], []).append(x)
    return [w[k] for k in sorted(w)]


def eligible(writers):
    return [w for w in writers if sum(x.s.obs_ms() for x in w) >= land.MIN_WRITER_OBS]


def x1(writers, classes):
    units = [[r for x in w for r in x.rows()] for w in writers]
    res = tc.summarize_types(units, classes=classes)
    if "focus" not in classes and any(r["pre_class"] == "focus" for u in units for r in tc.typed(u)):
        sys.exit("遷移の無い集計に focus の型が立った")
    res["writers"] = len(writers)
    res["sessions"] = sum(len(w) for w in writers)
    res["P3"] = ap.p3_rates([[x.s for x in w] for w in writers], False)
    res["thirds_class_share"] = ap.thirds_share(units, classes)
    res["obs_h"] = round(sum(x.s.obs_ms() for w in writers for x in w) / tc.H, 3)
    if all(x.d["moves"] is None for w in writers for x in w):  # ポインタの移動の記録が無い（E3）
        res["P1_silence_with_pointer_move"] = None
    res["signal_counts"] = {"window_activated": sum(len(x.d["focus"] or []) for w in writers for x in w),
                            "clicks": sum(len(x.d["clicks"]) for w in writers for x in w)}
    return res


def by_condition(writers, classes):
    out = {}
    for c in ("c1", "c2", "c3"):
        ws = [[x for x in w if x.cond == c] for w in writers]
        ws = [w for w in ws if w]
        units = [[r for x in w for r in x.rows()] for w in ws]
        ok = [r for u in units for r in tc.typed(u)]
        obs = sum(x.s.obs_ms() for w in ws for x in w)
        out[c] = {"files": sum(len(w) for w in ws), "stalls": sum(len(u) for u in units), "typed": len(ok),
                  "stalls_per_h_pooled": round(sum(len(u) for u in units) / (obs / tc.H), 4) if obs else None,
                  "class_share_pooled": {k: tc.pooled(sum(1 for r in ok if r["pre_class"] == k), len(ok))
                                         for k in classes}}
    return out


def checks(writers, classes, rng, orders):
    """X2〜X4。対照・無作為な窓はセッションから、再標本化は書き手の単位（E5）。"""
    r1u, excl = [], {}
    for w in writers:
        u = []
        for x in w:
            out, ex = ac.r1_unit([x.seg()], rng, False)
            u.extend(out)
            for k, v in ex.items():
                excl[k] = excl.get(k, 0) + v
        r1u.append(u)
    rows = [r for w in writers for x in w for r in x.rows()]
    ucl = ac.u_class_lengths(r1u, classes)
    r3 = ac.r3_summary(rows, classes)
    r3 = {k: v for k, v in r3.items() if k in orders or k in ("n", "flag_share_overlapping")}
    return {"X2": {**ac.r1_summary([u for u in r1u if u], classes, rng), "excluded": excl},
            "X3": ac.r2_summary(rows, ucl, classes),
            "X3_same_set_three_windows": ac.same_set_three_windows(r1u, classes),
            "X4": r3}


def run(seed, hold_p, dux_w, dux_tab_w, sw_w, out_dir):
    rng = random.Random(int(seed))
    hold = json.load(open(hold_p))
    hd = set(hold["dux"])
    hs = {"pp%d" % i for i in hold["swell"]}
    res, counts = {}, {}
    # DUX
    dx = [Sess(d) for d in load(dux_w, hd)]
    dw = group(dx)
    de = eligible(dw)
    counts["dux"] = {"sessions_loaded": len(dx), "excluded_obs_lt_10min": len(dw) - len(de)}
    res["dux"] = x1(de, DUX_CLASSES)
    res["dux"].update(checks(de, DUX_CLASSES, rng, ("current", "delete_over_move")))
    dt = group([Sess(d) for d in load(dux_tab_w, hd)])
    dte = eligible(dt)
    t1 = x1(dte, DUX_CLASSES)
    res["dux_tab_as_nav"] = {k: t1[k] for k in ("writers", "stalls", "typed", "P1_class_share_pooled",
                                                  "P1_fixed_window_class_share", "pre_window_incomplete")}
    counts["dux_tab_as_nav"] = {"excluded_obs_lt_10min": len(dt) - len(dte)}
    # SWELL-KW（判断 17 の順）
    raw = load(sw_w, hs)
    any_focus = any(d["focus"] for d in raw)
    counts["swell"] = {"files_loaded": len(raw), "any_window_activated": any_focus,
                       "window_activated_loaded": sum(len(d["focus"] or []) for d in raw),
                       "clicks_loaded": sum(len(d["clicks"]) for d in raw)}
    if any_focus:
        zero = [d for d in raw if not d["focus"]]
        counts["swell"]["files_zero_window_activated"] = len(zero)
        counts["swell"]["presses_in_zero_files"] = sum(len(d["keys"]) for d in zero)
        main = group([Sess(d) for d in raw if d["focus"]])
        me = eligible(main)
        counts["swell"]["writers_main"] = len(main)
        counts["swell"]["excluded_obs_lt_10min_main"] = len(main) - len(me)
        res["swell"] = x1(me, SW_CLASSES)
        res["swell"]["by_condition"] = by_condition(me, SW_CLASSES)
        res["swell"].update(checks(me, SW_CLASSES, rng, ("current", "delete_over_move", "focus_last")))
        allf = eligible(group([Sess(d, drop_focus=True) for d in raw]))
        a1 = x1(allf, SW3)
        res["swell_all_files_focus_dropped"] = {k: a1[k] for k in ("writers", "sessions", "stalls", "typed",
                                                                    "P1_class_share_pooled")}
    else:
        allf = eligible(group([Sess(d, drop_focus=True) for d in raw]))
        res["swell"] = x1(allf, SW3)
        res["swell"]["by_condition"] = by_condition(allf, SW3)
        res["swell"].update(checks(allf, SW3, rng, ("current", "delete_over_move")))
        res["swell"]["note"] = "Window Activated が無く、遷移の類は作れない"
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "extend.json"), "w"), indent=1)
    json.dump(counts, open(os.path.join(out_dir, "counts.json"), "w"), indent=1)
    print(json.dumps(counts))


def selftest():
    tc.selftest()
    press = [i * 1000 for i in range(700)] + [760_000 + i * 1000 for i in range(50)]
    keys = [[t, "alphabetic"] for t in press] + [[690_500, "backspace"], [691_500, "backspace"]]
    keys.sort()
    d = {"keys": keys, "feat": [[t, 0.1, 0.1] for t in press], "onsets": [[705_000, 710_000, 5000, 199]],
         "observed_intervals": [[0, 900_000]], "clicks": [], "moves": [695_000], "focus": [100_000],
         "writer": "pp1", "cond": "c1", "stats": {}}
    x = Sess(d)
    r = x.rows()
    assert len(r) == 1 and r[0]["pre_class"] == "delete2" and r[0]["resume"] == 760_000, r
    assert r[0]["pos"] == "later" and r[0]["pre_flags"]["move"]
    d2 = dict(d, focus=[700_000])
    assert Sess(d2).rows()[0]["pre_class"] == "focus"
    assert Sess(d2, drop_focus=True).rows()[0]["pre_class"] == "delete2"
    w = [[x]]
    s = x1(w, SW_CLASSES)
    assert s["typed"] == 1 and s["P1_counts"]["delete2|later"] == 1 and s["P3"]["later"]["stalls"] == 1
    bc = by_condition(w, SW_CLASSES)
    assert bc["c1"]["stalls"] == 1 and bc["c2"]["files"] == 0
    assert eligible([[x]]) == [[x]]
    assert s["signal_counts"] == {"window_activated": 1, "clicks": 0}
    # 対照はセッションから取る: 停滞はセッション A、短い休止の候補はセッション B にだけある
    ta = [i * 1000 for i in range(200)] + [259_000 + i * 1000 for i in range(50)]
    da = {"keys": [[t, "alphabetic"] for t in ta], "feat": [[t, 0.1, 0.1] for t in ta],
          "onsets": [[229_000, 235_000, 5000, 199]], "observed_intervals": [[0, 400_000]], "clicks": [],
          "moves": None, "focus": None, "writer": "v0:1", "cond": None, "stats": {}}
    off = 10 ** 7
    tb = [off + i * 5000 for i in range(80)]
    db = dict(da, keys=[[t, "alphabetic"] for t in tb], feat=[[t, 0.1, 0.1] for t in tb], onsets=[],
              observed_intervals=[[off, off + 500_000]])
    ck = checks([[Sess(da), Sess(db)]], DUX_CLASSES, random.Random(1), ("current",))
    assert ck["X2"]["excluded"]["no_control"] == 1 and ck["X2"]["current"]["stalls"] == 0, ck["X2"]
    ck2 = checks([[Sess(da), Sess(dict(da, writer="v0:1"))]], DUX_CLASSES, random.Random(1), ("current",))
    assert ck2["X2"]["excluded"]["no_control"] == 2
    assert x1([[Sess(da)]], DUX_CLASSES)["P1_silence_with_pointer_move"] is None
    # 取っておく書き手が中間にあれば止まる
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        json.dump(da, open(os.path.join(td, "00001.json"), "w"))
        assert len(load(td, set())) == 1
        try:
            load(td, {"v0:1"})
            raise AssertionError("取っておく書き手で止まらない")
        except SystemExit:
            pass
    short = dict(d, observed_intervals=[[0, 500_000]])
    assert eligible([[Sess(short)]]) == []
    print("extend selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(*sys.argv[1:])
