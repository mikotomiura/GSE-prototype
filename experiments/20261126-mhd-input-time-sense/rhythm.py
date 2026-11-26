"""語・文の境界のリズムの量 B を O1 の学習器に足す比べ（conditions.md C8・ADR-019 D6）。

usage: rhythm.py <work_dir> <out_json>   |   --selftest
"""
import json
import math
import os
import random
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import time_sense as ts  # noqa: E402
from time_sense import auc, cm  # noqa: E402

BOUND = {"space", "enter", "sentence_punctuation"}
SENT = {"sentence_punctuation", "enter"}
MIN_GAP = 50


def b_window(press, a, b):
    """(a, b] の押下の並び [(t, c)] から B の 6 量。"""
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


def evaluate(p, seed, label):
    files = p.files
    srows, crows, pairs, _ = auc.match(files, auc.CTRL_LO, f"{seed}-{label}-main")
    nd = len({files[fi].date for fi, _ in srows})
    res = {"stalls_used": len(srows), "controls_used": len(crows), "days_with_stalls": nd}
    if len(srows) < auc.MIN_STALLS or nd < auc.MIN_DAYS:
        res["status"] = "数が足りない"
        return res
    XK = (np.array([auc.feat_k(files[fi], u) for fi, u in srows]), np.array([auc.feat_k(files[fi], u) for fi, u in crows]))
    XN = (np.array([auc.feat_n(files[fi], u, False) for fi, u in srows]), np.array([auc.feat_n(files[fi], u, False) for fi, u in crows]))
    XB = (np.array([feat_b(files[fi], u) for fi, u in srows]), np.array([feat_b(files[fi], u) for fi, u in crows]))
    rng0 = random.Random(seed + 7)
    allB = np.vstack(XB)
    perm = list(range(len(allB)))
    rng0.shuffle(perm)
    allB = allB[perm]
    XBs = (allB[:len(srows)], allB[len(srows):])
    models = {
        "K": XK,
        "KB": (np.hstack([XK[0], XB[0]]), np.hstack([XK[1], XB[1]])),
        "KN": (np.hstack([XK[0], XN[0]]), np.hstack([XK[1], XN[1]])),
        "KNB": (np.hstack([XK[0], XN[0], XB[0]]), np.hstack([XK[1], XN[1], XB[1]])),
        "KBshuf": (np.hstack([XK[0], XBs[0]]), np.hstack([XK[1], XBs[1]])),
    }
    s_unit = [files[fi].date for fi, _ in srows]
    c_unit = [files[fi].date for fi, _ in crows]
    units = sorted({*s_unit, *c_unit})

    def one(sunit, cunit, srcs, crcs, prs, rs):
        o = {}
        for nm, (A, B) in models.items():
            r = auc.cv_scores(A[srcs], B[crcs], sunit, cunit, random.Random(rs))
            if r is None:
                return None
            o[nm] = auc.matched_auc(r[0], r[1], prs)
        o["dB"] = o["KB"] - o["K"]
        o["dB_given_N"] = o["KNB"] - o["KN"]
        o["dB_shuffled"] = o["KBshuf"] - o["K"]
        return o

    main = one(s_unit, c_unit, list(range(len(srows))), list(range(len(crows))), pairs, seed)
    if main is None:
        res["status"] = "学習に失敗"
        return res
    rng = random.Random(seed + 1)
    by_s = {u: [i for i, x in enumerate(s_unit) if x == u] for u in units}
    by_c = {u: [i for i, x in enumerate(c_unit) if x == u] for u in units}
    boots, fails = {k: [] for k in main}, 0
    for _ in range(auc.NBOOT):
        draw = [units[rng.randrange(len(units))] for _ in units]
        srcs, crcs, su, cu, prs = auc.resample(draw, by_s, by_c, pairs)
        r = one(su, cu, srcs, crcs, prs, rng.randrange(1 << 30)) if prs else None
        if r is None:
            fails += 1
            continue
        for k in boots:
            boots[k].append(r[k])
    res.update({k: round(v, 4) for k, v in main.items()})
    res["ci95"] = {k: cm.ci95(v) for k, v in boots.items()}
    res["boot_failures"] = fails
    return res


def run(work, out):
    people = ts.build(work)
    full = {sym: evaluate(p, ts.SEED, sym) for sym, p in people.items()}
    with open(os.path.join(work, "rhythm.full.json"), "w") as fh:
        json.dump(full, fh, indent=1, ensure_ascii=False)
    pub = {}
    for sym, r in full.items():
        q = {"status": r.get("status", "ok"), "stalls_used": ts.cm_round_count(r["stalls_used"]),
             "days_with_stalls": ts.cm_round_count(r["days_with_stalls"])}
        for k in ("K", "KB", "KN", "KNB", "dB", "dB_given_N", "dB_shuffled"):
            if k in r:
                q[k] = round(r[k], 2)
                ci = r["ci95"].get(k)
                q[k + "_ci95"] = [round(ci[0], 2), round(ci[1], 2)] if ci else None
        pub[sym] = q
    with open(out, "w") as fh:
        json.dump(pub, fh, indent=1, ensure_ascii=False)
    print(json.dumps(pub, indent=1, ensure_ascii=False))


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
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(sys.argv[1], sys.argv[2])
