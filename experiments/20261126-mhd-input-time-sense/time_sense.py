"""時間の感覚の量 T を O1 の学習器に足す比べ（conditions.md）。

usage: time_sense.py <work_dir> <out_json>   |   --selftest
20261116-o1-conduct-record の auc.py の部品（停滞と対照の引き方・K・N・学習器・折り）をそのまま使う。
"""
import bisect
import datetime as dt
import glob
import hashlib
import json
import math
import os
import random
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
O1 = os.path.join(HERE, "..", "20261116-o1-conduct-record")
sys.path.insert(0, O1)
import auc  # noqa: E402
import conduct  # noqa: E402
import cr_common as cm  # noqa: E402

SEED = int(open(os.path.join(HERE, "SEED")).read().strip())
UTC_OFFSET_MS = 9 * 3600 * 1000
DAY_BOUNDARY_H = 4
LONG_BREAK_MS = 180_000
CAP_MIN = 240.0
NAME = re.compile(r"_(\d{8})_(\d{6})\.ndjson$")


def start_epoch_from_name(name):
    m = NAME.search(name)
    if not m:
        raise ValueError("ファイル名に時刻が無い")
    t = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)
    return int(t.timestamp() * 1000)


def local_day(abs_ms):
    """現地の日（4 時の境）の通し番号。"""
    return (abs_ms + UTC_OFFSET_MS - DAY_BOUNDARY_H * 3600_000) // 86_400_000


class Person:
    """1 人の本の並びと、本をまたぐ観測区間（実時刻）。"""

    def __init__(self, files, starts):
        self.files, self.starts = files, starts
        ivs = []
        for f, s in zip(files, starts):
            ivs += [(s + a, s + b) for a, b in f.iv]
        self.ivs = sorted(ivs)
        self.iv_a = [a for a, _ in self.ivs]

    def feat_t(self, fi, u):
        f, s = self.files[fi], self.starts[fi]
        a_abs = s + u
        loc_h = ((a_abs + UTC_OFFSET_MS) % 86_400_000) / 3_600_000
        t1, t2 = math.sin(2 * math.pi * loc_h / 24), math.cos(2 * math.pi * loc_h / 24)
        wd = dt.datetime.fromtimestamp((a_abs + UTC_OFFSET_MS) / 1000, dt.timezone.utc).weekday()
        t3 = 1.0 if wd >= 5 else 0.0
        iv = f.interval_of(u)
        if iv is None:
            raise ValueError("u が観測区間の外")
        t4 = min(CAP_MIN, (u - iv[0]) / 60_000)
        # 長い離れ: 同じ観測区間の中の隣り合う文字の入力の間が 180 秒以上
        i = bisect.bisect_right(f.tt, u) - 1
        brk_end, brk_len = None, None
        j = i
        while j >= 1 and f.tt[j - 1] >= iv[0]:
            if f.tt[j] - f.tt[j - 1] >= LONG_BREAK_MS:
                brk_end, brk_len = f.tt[j], f.tt[j] - f.tt[j - 1]
                break
            j -= 1
        if brk_end is None:
            brk_end = iv[0]
            k = bisect.bisect_left(self.iv_a, s + iv[0]) - 1
            brk_len = (s + iv[0] - self.ivs[k][1]) if k >= 0 else None
        t5 = min(CAP_MIN, (u - brk_end) / 60_000)
        t6 = min(CAP_MIN, brk_len / 60_000) if brk_len is not None else float("nan")
        day = local_day(a_abs)
        t7 = 0.0
        for a, b in self.ivs:
            if a >= a_abs:
                break
            lo = max(a, day_start_abs(day))
            hi = min(b, a_abs)
            if hi > lo:
                t7 += (hi - lo) / 60_000
        return [t1, t2, t3, t4, t5, t6, t7]


def day_start_abs(day):
    return day * 86_400_000 + DAY_BOUNDARY_H * 3600_000 - UTC_OFFSET_MS


def plain_names(work):
    """平文の SHA-256 → ファイル名。"""
    out = {}
    for p in glob.glob(os.path.join(work, "plain", "*", "*.ndjson")):
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        out[h] = os.path.basename(p)
    return out


def build(work):
    table, people = cm.load_people(work)
    names = plain_names(work)
    out = {}
    for sym, rows in sorted(people.items()):
        pok = conduct.pointer_usable(rows)
        files, starts = [], []
        for f, d, x in sorted(rows, key=lambda r: r[0]["inter"]):
            if not (d["focus"] and cm.obs_ms(d) > 0):
                continue
            nm = names.get(f["plain_sha256"])
            if nm is None:
                sys.exit(f"平文が見つからない（人 {sym}）")
            files.append(auc.F(f["inter"], d, x, pok, f["date"]))
            starts.append(start_epoch_from_name(nm))
        out[sym] = Person(files, starts)
    return out


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
    XT = (np.array([p.feat_t(fi, u) for fi, u in srows]), np.array([p.feat_t(fi, u) for fi, u in crows]))
    # 負の対照: T の行を停滞と対照の全体で並べ替える
    rng0 = random.Random(seed + 7)
    allT = np.vstack(XT)
    perm = list(range(len(allT)))
    rng0.shuffle(perm)
    allT = allT[perm]
    XTs = (allT[:len(srows)], allT[len(srows):])
    models = {
        "K": XK,
        "KT": (np.hstack([XK[0], XT[0]]), np.hstack([XK[1], XT[1]])),
        "KN": (np.hstack([XK[0], XN[0]]), np.hstack([XK[1], XN[1]])),
        "KNT": (np.hstack([XK[0], XN[0], XT[0]]), np.hstack([XK[1], XN[1], XT[1]])),
        "KTshuf": (np.hstack([XK[0], XTs[0]]), np.hstack([XK[1], XTs[1]])),
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
        o["dT"] = o["KT"] - o["K"]
        o["dT_given_N"] = o["KNT"] - o["KN"]
        o["dT_shuffled"] = o["KTshuf"] - o["K"]
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
    res["pointer_usable"] = files[0].ptr is not None if files else None
    return res


def run(work, out):
    people = build(work)
    full = {sym: evaluate(p, SEED, sym) for sym, p in people.items()}
    with open(os.path.join(work, "time_sense.full.json"), "w") as fh:
        json.dump(full, fh, indent=1, ensure_ascii=False)
    pub = {}
    for sym, r in full.items():
        q = {"status": r.get("status", "ok"),
             "stalls_used": cm_round_count(r["stalls_used"]), "days_with_stalls": cm_round_count(r["days_with_stalls"])}
        for k in ("K", "KT", "KN", "KNT", "dT", "dT_given_N", "dT_shuffled"):
            if k in r:
                q[k] = round(r[k], 2)
                lo, hi = r["ci95"][k] if r["ci95"].get(k) else (None, None)
                q[k + "_ci95"] = [round(lo, 2), round(hi, 2)] if lo is not None else None
        pub[sym] = q
    with open(out, "w") as fh:
        json.dump(pub, fh, indent=1, ensure_ascii=False)
    print(json.dumps(pub, indent=1, ensure_ascii=False))


def cm_round_count(n):
    """20261116 の公開の丸め（50 未満は 5 単位・50 以上は 100 単位・半分以上は切り上げ）。"""
    step = 5 if n < 50 else 100
    return int(math.floor(n / step + 0.5)) * step


def selftest():
    class FF:
        pass
    f = FF()
    f.iv = [(0, 3_600_000)]
    f.tt = [10_000, 20_000, 220_000, 230_000]  # 20s→220s が 200 秒の離れ
    f.interval_of = lambda t: (0, 3_600_000) if 0 <= t <= 3_600_000 else None
    start = start_epoch_from_name("x_gse_o1_20261121_010000.ndjson")  # UTC 01:00 = 現地 10:00・土曜
    p = Person([f], [start])
    v = p.feat_t(0, 230_000)
    loc_h = 10 + 230 / 3600
    exp = [math.sin(2 * math.pi * loc_h / 24), math.cos(2 * math.pi * loc_h / 24), 1.0,
           230_000 / 60_000, (230_000 - 220_000) / 60_000, 200_000 / 60_000, 230_000 / 60_000]
    for a, b in zip(v, exp):
        assert abs(a - b) < 1e-9, (v, exp)
    # 離れが無いとき: 観測区間の始まりから・前の区間が無いので T6 は欠け
    v2 = p.feat_t(0, 20_000)
    assert abs(v2[4] - 20_000 / 60_000) < 1e-9 and math.isnan(v2[5])
    # 日の境（現地 4 時）: 現地 03:59 と 04:01 は別の日
    a = start_epoch_from_name("gse_o1_20261120_185900.ndjson")  # 現地 03:59
    b = start_epoch_from_name("gse_o1_20261120_190100.ndjson")  # 現地 04:01
    assert local_day(a) + 1 == local_day(b)
    assert cm_round_count(47) == 45 and cm_round_count(48) == 50 and cm_round_count(149) == 100 and cm_round_count(150) == 200
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(sys.argv[1], sys.argv[2])
