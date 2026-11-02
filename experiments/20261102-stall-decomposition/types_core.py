"""停滞の型（conditions.md C2〜C4）の共通の定義。公開データ（public/）と O1（o1/）の両方が使う。

入力は時刻の並び（ms の整数）だけ。本文・ID は扱わない。
  python3 -I types_core.py --selftest
"""
import bisect
import statistics

PRE_WIN = 30_000
EARLY_MS = 10 * 60_000
BLOCK_GAP = 30 * 60_000
SHORT_MS, LONG_MS = 15_000, 180_000
MIN_STALLS_FOR_MEDIAN = 5
H = 3_600_000

CLASSES = ("focus", "move_or_click", "delete2", "silence")
POS = ("early", "later")
LEN = ("short", "mid", "long", "censored")


def count_in(ts, a, b, lo_open=False, hi_open=False):
    lo = bisect.bisect_right(ts, a) if lo_open else bisect.bisect_left(ts, a)
    hi = bisect.bisect_left(ts, b) if hi_open else bisect.bisect_right(ts, b)
    return max(0, hi - lo)


def quart(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    q = statistics.quantiles(xs, n=4, method="inclusive") if len(xs) > 1 else [xs[0]] * 3
    return {"n": len(xs), "q1": round(q[0], 4), "median": round(statistics.median(xs), 4), "q3": round(q[2], 4)}


def pooled(num, den):
    return {"num": num, "den": den, "ratio": round(num / den, 4) if den else None}


class Rec:
    """1 単位（公開データはセッション・O1 は 1 ファイル）の時刻の並び。

    text / delete / other_nontext: 押下の時刻（C2 の集合で分けたもの）
    clicks: クリックの時刻（KLiCKe はクリック・O1 は buttons>0 か wheel>0 の pointer_bin。無ければ空）
    focus: focus_transition の時刻（O1 だけ。公開データは None = 類 1 が無い）
    moves: moved>0 の pointer_bin の時刻（O1 だけ・沈黙の中の割合の記述用）
    intervals: 観測区間 [(a, b)]
    block_starts: 位置の開始（C3 の 2）
    """

    def __init__(self, text, delete, other_nontext, intervals, clicks=(), focus=None, moves=None,
                 block_starts=None):
        self.text, self.delete, self.other = sorted(text), sorted(delete), sorted(other_nontext)
        self.clicks = sorted(clicks)
        self.focus = sorted(focus) if focus is not None else None
        self.moves = sorted(moves) if moves is not None else None
        self.intervals = sorted(tuple(iv) for iv in intervals)
        allp = sorted(self.text + self.delete + self.other)
        self.press = allp
        if block_starts is None:
            block_starts = blocks_from_press(allp)
        self.block_starts = sorted(block_starts)

    def interval_of(self, t):
        i = bisect.bisect_right([a for a, _ in self.intervals], t) - 1
        if i >= 0 and self.intervals[i][0] <= t <= self.intervals[i][1]:
            return self.intervals[i]
        return None

    def flags(self, a, b, lo_open=False, hi_open=False):
        c = lambda ts: count_in(ts, a, b, lo_open, hi_open)  # noqa: E731
        return {"focus": self.focus is not None and c(self.focus) > 0,
                "other_nontext": c(self.other) > 0,
                "click": c(self.clicks) > 0,
                "delete2": c(self.delete) >= 2,
                "move": self.moves is not None and c(self.moves) > 0}

    @staticmethod
    def klass(fl):
        if fl["focus"]:
            return "focus"
        if fl["other_nontext"] or fl["click"]:
            return "move_or_click"
        if fl["delete2"]:
            return "delete2"
        return "silence"

    def position(self, t0):
        i = bisect.bisect_right(self.block_starts, t0) - 1
        if i < 0:
            return None, None
        st = self.block_starts[i]
        return ("early" if t0 - st < EARLY_MS else "later"), i

    def stall(self, s, t0):
        """1 件の停滞の行（台帳の 1 行）。"""
        iv = self.interval_of(t0)
        row = {"s": s, "t0": t0, "interval": iv}
        if iv is None:
            row["no_interval"] = True
            return row
        pre_a = s - PRE_WIN
        row["pre_complete"] = iv[0] <= pre_a
        fl = self.flags(pre_a, t0)
        row["pre_flags"] = fl
        row["pre_class"] = self.klass(fl) if row["pre_complete"] else None
        fx_a = t0 - PRE_WIN
        row["pre_fixed_class"] = self.klass(self.flags(fx_a, t0)) if iv[0] <= fx_a else None
        row["pos"], row["block"] = self.position(t0)
        j = bisect.bisect_right(self.text, t0)
        r = self.text[j] if j < len(self.text) and self.text[j] <= iv[1] else None
        row["resume"] = r
        if r is None:
            row["len_class"] = "censored"
            row["len_ms"] = None
            row["post_class"] = self.klass(self.flags(t0, iv[1], lo_open=True))
        else:
            d = r - t0
            row["len_ms"] = d
            row["len_class"] = "short" if d <= SHORT_MS else "mid" if d <= LONG_MS else "long"
            row["post_class"] = self.klass(self.flags(t0, r, lo_open=True, hi_open=True))
        return row


def blocks_from_press(press, gap=BLOCK_GAP):
    out = []
    prev = None
    for t in press:
        if prev is None or t - prev >= gap:
            out.append(t)
        prev = t
    return out


def typed(rows):
    return [r for r in rows if not r.get("no_interval") and r["pre_class"] is not None and r["pos"] is not None]


def summarize_types(units, classes=CLASSES):
    """units: [[row, ...], ...]（単位 = 書き手か日）。C4 の P1・P2。"""
    allrows = [r for u in units for r in u]
    ok = typed(allrows)
    res = {"stalls": len(allrows),
           "no_interval": sum(1 for r in allrows if r.get("no_interval")),
           "pre_window_incomplete": sum(1 for r in allrows if not r.get("no_interval") and not r["pre_complete"]),
           "no_position": sum(1 for r in allrows if not r.get("no_interval") and r["pre_complete"] and r["pos"] is None),
           "typed": len(ok)}
    cells = [(c, p) for c in classes for p in POS]
    res["P1_counts"] = {f"{c}|{p}": sum(1 for r in ok if r["pre_class"] == c and r["pos"] == p) for c, p in cells}
    res["P1_share_pooled"] = {k: pooled(v, len(ok)) for k, v in res["P1_counts"].items()}
    res["P1_class_share_pooled"] = {c: pooled(sum(1 for r in ok if r["pre_class"] == c), len(ok)) for c in classes}
    uok = [typed(u) for u in units]
    uok = [u for u in uok if len(u) >= MIN_STALLS_FOR_MEDIAN]
    res["P1_class_share_unit_median"] = {c: quart([sum(1 for r in u if r["pre_class"] == c) / len(u) for u in uok])
                                         for c in classes}
    res["P1_units_with_ge5"] = len(uok)
    fx = [r for r in ok if r.get("pre_fixed_class") is not None]
    res["P1_fixed_window_class_share"] = {c: pooled(sum(1 for r in fx if r["pre_fixed_class"] == c), len(fx))
                                          for c in classes}
    keys = ("focus", "other_nontext", "click", "delete2")
    combo = {}
    for r in ok:
        k = "".join("1" if r["pre_flags"][x] else "0" for x in keys)
        combo[k] = combo.get(k, 0) + 1
    res["P1_cooccurrence"] = {"order": list(keys), "counts": dict(sorted(combo.items()))}
    sil = [r for r in ok if r["pre_class"] == "silence"]
    res["P1_silence_with_pointer_move"] = pooled(sum(1 for r in sil if r["pre_flags"]["move"]), len(sil))
    p2 = {}
    for c in classes:
        rs = [r for r in ok if r["pre_class"] == c]
        p2[c] = {"n": len(rs),
                 "len_class": {lc: pooled(sum(1 for r in rs if r["len_class"] == lc), len(rs)) for lc in LEN},
                 "len_s_resumed": quart([r["len_ms"] / 1000 for r in rs if r["len_ms"] is not None]),
                 "post_class": {pc: sum(1 for r in rs if r["post_class"] == pc) for pc in classes}}
    res["P2"] = p2
    return res


def selftest():
    # 文字 1 秒ごと 0..99 秒、止まり、130 秒から再開。削除 2 回（95, 96 秒）は前の窓の中。
    text = [i * 1000 for i in range(100)] + [130_000 + i * 1000 for i in range(10)]
    rec = Rec(text, delete=[95_500, 96_500], other_nontext=[], intervals=[(0, 200_000)])
    row = rec.stall(105_000, 110_000)
    assert row["pre_complete"] and row["pre_class"] == "delete2", row
    assert row["resume"] == 130_000 and row["len_class"] == "mid" and row["len_ms"] == 20_000
    assert row["pos"] == "early" and row["post_class"] == "silence"
    # 優先順: クリックがあれば削除より上
    rec2 = Rec(text, delete=[95_500, 96_500], other_nontext=[], intervals=[(0, 200_000)], clicks=[100_000])
    assert rec2.stall(105_000, 110_000)["pre_class"] == "move_or_click"
    # フォーカスが最上位・公開データ（focus=None）では立たない
    rec3 = Rec(text, delete=[], other_nontext=[101_000], intervals=[(0, 200_000)], focus=[100_000])
    assert rec3.stall(105_000, 110_000)["pre_class"] == "focus"
    # 窓の端: s−30 秒ちょうど・t0 ちょうどは前の窓に入る
    rec4 = Rec(text, delete=[], other_nontext=[75_000], intervals=[(0, 200_000)])
    assert rec4.stall(105_000, 110_000)["pre_class"] == "move_or_click"
    rec4b = Rec(text, delete=[], other_nontext=[74_999], intervals=[(0, 200_000)])
    assert rec4b.stall(105_000, 110_000)["pre_class"] == "silence"
    rec4c = Rec(text, delete=[], other_nontext=[110_000], intervals=[(0, 200_000)])
    r4c = rec4c.stall(105_000, 110_000)
    assert r4c["pre_class"] == "move_or_click" and r4c["post_class"] == "silence"
    # 削除 1 回は沈黙
    rec5 = Rec(text, delete=[96_000], other_nontext=[], intervals=[(0, 200_000)])
    assert rec5.stall(105_000, 110_000)["pre_class"] == "silence"
    # 区間の外で再開 → 打ち切り。区間の切れ目の後の文字は再開にしない
    rec6 = Rec(text, delete=[], other_nontext=[], intervals=[(0, 120_000), (125_000, 200_000)])
    r6 = rec6.stall(105_000, 110_000)
    assert r6["resume"] is None and r6["len_class"] == "censored"
    # 前の窓が区間に収まらない → 型に入れない
    rec7 = Rec(text, delete=[], other_nontext=[], intervals=[(80_000, 200_000)])
    r7 = rec7.stall(105_000, 110_000)
    assert not r7["pre_complete"] and r7["pre_class"] is None
    # 長さの境界: 15 秒ちょうどは short、180 秒ちょうどは mid
    rec8 = Rec([0, 1000, 125_000], [], [], [(0, 400_000)])
    assert rec8.stall(5000, 110_000)["len_class"] == "short"
    rec9 = Rec([0, 1000, 290_000], [], [], [(0, 400_000)])
    assert rec9.stall(5000, 110_000)["len_class"] == "mid"
    rec10 = Rec([0, 1000, 290_001], [], [], [(0, 400_000)])
    assert rec10.stall(5000, 110_000)["len_class"] == "long"
    # 再開は t0 と同時刻を含めない
    rec11 = Rec([0, 110_000, 111_000], [], [], [(0, 400_000)])
    assert rec11.stall(5000, 110_000)["resume"] == 111_000
    # 位置: 30 分以上の空きで新しいまとまり。10 分ちょうどは later
    press = [0, 1000, 40 * 60_000, 40 * 60_000 + 1000]
    assert blocks_from_press(press) == [0, 40 * 60_000]
    recp = Rec(press, [], [], [(0, 10 ** 8)])
    assert recp.position(40 * 60_000 + 9 * 60_000)[0] == "early"
    assert recp.position(40 * 60_000 + 10 * 60_000)[0] == "later"
    assert recp.position(35 * 60_000)[0] == "later"
    # 集計
    s = summarize_types([[row, r7], [rec2.stall(105_000, 110_000)]])
    assert s["stalls"] == 3 and s["typed"] == 2 and s["pre_window_incomplete"] == 1
    assert s["P1_counts"]["delete2|early"] == 1 and s["P1_counts"]["move_or_click|early"] == 1
    assert s["P1_cooccurrence"]["counts"] == {"0001": 1, "0011": 1}
    print("types_core selftest ok")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--selftest"]:
        selftest()
