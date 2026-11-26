"""時間の感覚の量 T を O1 の学習器に足す比べ（conditions.md）。

usage: time_sense.py <work_dir> <out_json>   |   --selftest
20261116-o1-conduct-record の auc.py の部品（停滞と対照の引き方・K・N・学習器・折り）をそのまま使う。
rhythm.py も、この evaluate_group を使う。
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
# 同じ秒の衝突を避ける接尾辞（_2 など）も許す（逸脱 2）
NAME = re.compile(r"_(\d{8})_(\d{6})(?:_\d+)?\.ndjson$")
N_PERM = 20          # 並べ替えの帰無の回数（逸脱 1）
MIN_BOOT_OK = 150    # 区間を出す成功の下限（200 回のうち・逸脱 3）


def start_epoch_from_name(name):
    m = NAME.search(name)
    if not m:
        raise ValueError("ファイル名に時刻が無い")
    t = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)
    return int(t.timestamp() * 1000)


def local_day(abs_ms):
    """現地の日（4 時の境）の通し番号。"""
    return (abs_ms + UTC_OFFSET_MS - DAY_BOUNDARY_H * 3600_000) // 86_400_000


def day_start_abs(day):
    return day * 86_400_000 + DAY_BOUNDARY_H * 3600_000 - UTC_OFFSET_MS


class Person:
    """1 人の本の並びと、本をまたぐ観測区間（実時刻）。all_ivs は観測区間を持つすべての本から作る（逸脱 4）。"""

    def __init__(self, files, starts, all_ivs=None):
        self.files, self.starts = files, starts
        if all_ivs is None:
            all_ivs = []
            for f, s in zip(files, starts):
                all_ivs += [(s + a, s + b) for a, b in f.iv]
        self.ivs = sorted(all_ivs)
        self.iv_a = [a for a, _ in self.ivs]
        self.overlaps = sum(1 for (a0, b0), (a1, _) in zip(self.ivs, self.ivs[1:]) if a1 < b0)

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
        t6 = min(CAP_MIN, max(0, brk_len) / 60_000) if brk_len is not None else float("nan")
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


def plain_names(work):
    out = {}
    for p in glob.glob(os.path.join(work, "plain", "*", "*.ndjson")):
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        out[h] = os.path.basename(p)
    return out


def build(work):
    _table, people = cm.load_people(work)
    names = plain_names(work)
    out = {}
    for sym, rows in sorted(people.items()):
        pok = conduct.pointer_usable(rows)
        files, starts, all_ivs = [], [], []
        for f, d, x in sorted(rows, key=lambda r: r[0]["inter"]):
            nm = names.get(f["plain_sha256"])          # 対応はすべての本で照らす（逸脱 4）
            if nm is None:
                sys.exit(f"平文が見つからない（人 {sym}）")
            s = start_epoch_from_name(nm)
            all_ivs += [(s + iv["a_ms"], s + iv["b_ms"]) for iv in d["observed_intervals"]]
            if not (d["focus"] and cm.obs_ms(d) > 0):
                continue
            files.append(auc.F(f["inter"], d, x, pok, f["date"]))
            starts.append(s)
        out[sym] = Person(files, starts, all_ivs)
    return out


def _stack(a, b):
    return (np.hstack([a[0], b[0]]), np.hstack([a[1], b[1]]))


def evaluate_group(p, seed, label, feat_fn, g, perm_offset):
    """K・K+G・K+N・K+N+G と、G の行を並べ替えた K+G（N_PERM 回）。G は追加の量の群の名前（T や B）。"""
    files = p.files
    srows, crows, pairs, _ = auc.match(files, auc.CTRL_LO, f"{seed}-{label}-main")
    nd = len({files[fi].date for fi, _ in srows})
    res = {"stalls_used": len(srows), "controls_used": len(crows), "days_with_stalls": nd,
           "interval_overlaps": p.overlaps}
    if len(srows) < auc.MIN_STALLS or nd < auc.MIN_DAYS:
        res["status"] = "数が足りない"
        return res
    XK = (np.array([auc.feat_k(files[fi], u) for fi, u in srows]), np.array([auc.feat_k(files[fi], u) for fi, u in crows]))
    XN = (np.array([auc.feat_n(files[fi], u, False) for fi, u in srows]), np.array([auc.feat_n(files[fi], u, False) for fi, u in crows]))
    XG = (np.array([feat_fn(fi, u) for fi, u in srows]), np.array([feat_fn(fi, u) for fi, u in crows]))
    models = {"K": XK, "K" + g: _stack(XK, XG), "KN": _stack(XK, XN), "KN" + g: _stack(_stack(XK, XN), XG)}
    s_unit = [files[fi].date for fi, _ in srows]
    c_unit = [files[fi].date for fi, _ in crows]
    units = sorted({*s_unit, *c_unit})
    allS, allC = list(range(len(srows))), list(range(len(crows)))

    def fit(A, B, sunit, cunit, srcs, crcs, prs, rs):
        r = auc.cv_scores(A[srcs], B[crcs], sunit, cunit, random.Random(rs))
        return None if r is None else auc.matched_auc(r[0], r[1], prs)

    def one(sunit, cunit, srcs, crcs, prs, rs):
        o = {}
        for nm, (A, B) in models.items():
            v = fit(A, B, sunit, cunit, srcs, crcs, prs, rs)
            if v is None:
                return None
            o[nm] = v
        o["d" + g] = o["K" + g] - o["K"]
        o["d" + g + "_given_N"] = o["KN" + g] - o["KN"]
        return o

    main = one(s_unit, c_unit, allS, allC, pairs, seed)
    if main is None:
        res["status"] = "学習に失敗"
        return res
    # 並べ替えの帰無: G の行を停滞と対照の全体で並べ替えて K+G を当て直す（同じ折り）。N_PERM 回の ΔAUC の分布（逸脱 1）
    rngp = random.Random(seed + perm_offset)
    allG = np.vstack(XG)
    null = []
    for _ in range(N_PERM):
        perm = list(range(len(allG)))
        rngp.shuffle(perm)
        Gs = allG[perm]
        v = fit(*_stack(XK, (Gs[:len(srows)], Gs[len(srows):])), s_unit, c_unit, allS, allC, pairs, seed)
        if v is not None:
            null.append(v - main["K"])
    null.sort()
    res["null_d" + g] = {"n": len(null), "q025": cm.ci95(null)[0] if null else None,
                         "q975": cm.ci95(null)[1] if null else None,
                         "share_ge_observed": (sum(1 for x in null if x >= main["d" + g]) / len(null)) if null else None}
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
    res["boot_failures"] = fails
    res["ci95"] = {k: (cm.ci95(v) if auc.NBOOT - fails >= MIN_BOOT_OK else None) for k, v in boots.items()}
    if auc.NBOOT - fails < MIN_BOOT_OK:
        res["ci_status"] = "区間推定不能（成功が下限に届かない）"
    return res


def publish(full, keys, out):
    pub = {}
    for sym, r in full.items():
        q = {"status": r.get("status", "ok"), "stalls_used": cm_round_count(r["stalls_used"]),
             "controls_used": cm_round_count(r["controls_used"]),
             "days_with_stalls": cm_round_count(r["days_with_stalls"]),
             "interval_overlaps": r.get("interval_overlaps")}
        if "boot_failures" in r:
            q["boot_failures"] = r["boot_failures"]
            q["ci_status"] = r.get("ci_status", "ok")
        for k in keys:
            if k in r:
                q[k] = round(r[k], 2)
                ci = (r.get("ci95") or {}).get(k)
                q[k + "_ci95"] = [round(ci[0], 2), round(ci[1], 2)] if ci else None
        for k, v in r.items():
            if k.startswith("null_"):
                q[k] = {"n": v["n"], "q025": round(v["q025"], 2) if v["q025"] is not None else None,
                        "q975": round(v["q975"], 2) if v["q975"] is not None else None,
                        "share_ge_observed": round(v["share_ge_observed"], 2) if v["share_ge_observed"] is not None else None}
        pub[sym] = q
    with open(out, "w") as fh:
        json.dump(pub, fh, indent=1, ensure_ascii=False)
    print(json.dumps(pub, indent=1, ensure_ascii=False))


def run(work, out):
    people = build(work)
    full = {sym: evaluate_group(p, SEED, sym, p.feat_t, "T", 7) for sym, p in people.items()}
    with open(os.path.join(work, "time_sense.full.json"), "w") as fh:
        json.dump(full, fh, indent=1, ensure_ascii=False)
    publish(full, ("K", "KT", "KN", "KNT", "dT", "dT_given_N"), out)


def cm_round_count(n):
    """20261116 の公開の丸め（50 未満は 5 単位・50 以上は 100 単位・半分以上は切り上げ）。"""
    step = 5 if n < 50 else 100
    return int(math.floor(n / step + 0.5)) * step


class _FF:
    def __init__(self, iv, tt):
        self.iv, self.tt = iv, tt

    def interval_of(self, t):
        for a, b in self.iv:
            if a <= t <= b:
                return (a, b)
        return None


def selftest():
    start = start_epoch_from_name("x_gse_o1_20261121_010000.ndjson")  # UTC 01:00 = 現地 10:00・土曜
    f = _FF([(0, 3_600_000)], [10_000, 20_000, 220_000, 230_000])     # 20s→220s が 200 秒の離れ
    p = Person([f], [start])
    v = p.feat_t(0, 230_000)
    loc_h = 10 + 230 / 3600
    exp = [math.sin(2 * math.pi * loc_h / 24), math.cos(2 * math.pi * loc_h / 24), 1.0,
           230_000 / 60_000, (230_000 - 220_000) / 60_000, 200_000 / 60_000, 230_000 / 60_000]
    for a, b in zip(v, exp):
        assert abs(a - b) < 1e-9, (v, exp)
    # 離れが無く前の区間も無い: T5 は区間の始まりから・T6 は欠け
    v2 = p.feat_t(0, 20_000)
    assert abs(v2[4] - 20_000 / 60_000) < 1e-9 and math.isnan(v2[5])
    # 本をまたぐ T6・T7 の複数区間の和: 前の本の区間 [現地 9:00, 9:30]、今の本は 10:00 から
    prev_s = start_epoch_from_name("gse_o1_20261121_000000.ndjson")    # 現地 9:00
    f0 = _FF([(0, 1_800_000)], [1000])
    p2 = Person([f0, f], [prev_s, start])
    v3 = p2.feat_t(1, 20_000)
    assert abs(v3[5] - 30.0) < 1e-9, v3            # 9:30 から 10:00 の離れ
    assert abs(v3[6] - (30.0 + 20_000 / 60_000)) < 1e-9, v3
    # 240 分の上限: 前の本が 6 時間前に終わる
    far_s = start_epoch_from_name("gse_o1_20261120_180000.ndjson")     # 現地 3:00（前の日の扱い）
    f1 = _FF([(0, 1_000)], [500])
    v4 = Person([f1, f], [far_s, start]).feat_t(1, 20_000)
    assert v4[5] == CAP_MIN, v4
    # T7 の 4 時の境: 現地 3:00〜3:00:01 の区間は今日（4 時以降）に数えない
    assert abs(v4[6] - 20_000 / 60_000) < 1e-9, v4
    # 日の境（現地 4 時）
    a = start_epoch_from_name("gse_o1_20261120_185900.ndjson")
    b = start_epoch_from_name("gse_o1_20261120_190100_2.ndjson")       # 接尾辞つき
    assert local_day(a) + 1 == local_day(b)
    # 区間の重なりを数える
    assert Person([f, f], [start, start]).overlaps == 1
    assert cm_round_count(47) == 45 and cm_round_count(48) == 50 and cm_round_count(149) == 100 and cm_round_count(150) == 200
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(sys.argv[1], sys.argv[2])
