"""語・文の境界のリズムの量 B を O1 の学習器に足す比べ（conditions.md C8・ADR-019 D6）。

usage: rhythm.py <work_dir> <out_json>   |   --selftest
評価の手順は time_sense.evaluate_group と同じ（並べ替えの種だけ違う）。
"""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import time_sense as ts  # noqa: E402
from time_sense import auc  # noqa: E402

BOUND = {"space", "enter", "sentence_punctuation"}
SENT = {"sentence_punctuation", "enter"}
MIN_GAP = 50


def b_window(press, a, b):
    """(a, b] の押下の並び [(t, c)] から B の 6 量。間隔は 50 ms を超えるものだけ。"""
    w = [(t, c) for t, c in press if a < t <= b]
    nan = float("nan")
    n_b = float(sum(1 for _, c in w if c in BOUND))
    before, after, inner, sent_after = [], [], [], []
    for (t0, c0), (t1, c1) in zip(w, w[1:]):
        g = t1 - t0
        if g <= MIN_GAP:
            continue
        if c1 in BOUND:
            before.append(g)
        if c0 in BOUND:
            after.append(g)
        if c0 not in BOUND and c1 not in BOUND:
            inner.append(g)
        if c0 in SENT:
            sent_after.append(g)
    med = lambda xs: statistics.median(xs) if xs else nan  # noqa: E731
    b2, b3, b4 = med(before), med(after), med(inner)
    b5 = b3 / b4 if (not math.isnan(b3) and not math.isnan(b4) and b4 > 0) else nan
    b6 = max(sent_after) if sent_after else nan
    return [n_b, b2, b3, b4, b5, b6]


def feat_b(f, u):
    w1 = b_window(f.press, u - auc.D_WIN, u)
    w0 = b_window(f.press, u - 2 * auc.D_WIN, u - auc.D_WIN)
    return w1 + [x - y for x, y in zip(w1, w0)]


def run(work, out):
    people = ts.build(work)
    full = {sym: ts.evaluate_group(p, ts.SEED, sym, (lambda fi, u, p=p: feat_b(p.files[fi], u)), "B", 11)
            for sym, p in people.items()}
    with open(os.path.join(work, "rhythm.full.json"), "w") as fh:
        json.dump(full, fh, indent=1, ensure_ascii=False)
    ts.publish(full, ("K", "KB", "KN", "KNB", "dB", "dB_given_N"), out)


def selftest():
    press = [(1000, "alphabetic"), (1200, "alphabetic"), (1500, "space"), (2300, "alphabetic"),
             (2400, "alphabetic"), (2420, "alphabetic"), (3000, "sentence_punctuation"), (5000, "alphabetic")]
    v = b_window(press, 0, 10_000)
    # 間隔: 200(in) 300(before) 800(after) 100(in) 20(<=50 除く) 580(before) 2000(after・sent)
    assert v[0] == 2.0
    assert v[1] == statistics.median([300, 580])
    assert v[2] == statistics.median([800, 2000])
    assert v[3] == statistics.median([200, 100])
    assert abs(v[4] - v[2] / v[3]) < 1e-12
    assert v[5] == 2000
    e = b_window([], 0, 1)
    assert e[0] == 0.0 and all(math.isnan(x) for x in e[1:])
    # 窓の端: (a, b] なので a ちょうどの押下は入らず、b ちょうどは入る
    edge = [(0, "space"), (100, "alphabetic"), (200, "space")]
    ve = b_window(edge, 0, 200)
    assert ve[0] == 1.0 and ve[1] == 100 and math.isnan(ve[2])
    # ちょうど 50 ms の間隔は数えない
    v50 = b_window([(0, "alphabetic"), (50, "alphabetic"), (151, "alphabetic")], -1, 1000)
    assert v50[3] == 101
    # W1 − W0 の差（欠けの差は欠け）
    class F:
        pass
    f = F()
    f.press = [(31_000, "alphabetic"), (31_400, "alphabetic"), (61_000, "space"), (61_500, "alphabetic"), (62_000, "alphabetic")]
    fb = feat_b(f, 62_000)                   # W1 = (32 s, 62 s]・W0 = (2 s, 32 s]
    assert fb[0] == 1.0 and fb[6] == 1.0 - 0.0
    assert fb[3] == 500 and fb[9] == 500 - 400
    assert math.isnan(fb[7])                 # W1 の直前の間は欠けではない（61_000 の前の押下は W1 の外）→ 欠け − 欠け
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(sys.argv[1], sys.argv[2])
