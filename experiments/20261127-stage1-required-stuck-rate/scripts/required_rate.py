"""段 1 の各判定が「判定不能でない」確率を、詰まりの率 π ごとに合成で出す（conditions.md 第 1 版）。

使い方:
  python3 -I required_rate.py --selftest
  python3 -I required_rate.py <seed> <out_dir> [n_sim]
打鍵も記録も読まない。値は conditions.md に書いた事前登録の集計だけ。
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "20261103-mhd-dryrun-v2", "scripts"))
from daysim import ar1, auc  # noqa: E402

DAYS = 56
EARLY = (28, 35)
RHO = 0.3
R = 500
Z = 1.959963984540054
PER_DAY = {"all": 6.35, "c0": 3.0, "c1": 1.75, "c2": 0.9}
PIS = [0.007, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20]
SCALES = [1.0, 0.5]
FS = [0.65, 0.53]
SDS = [0.0, 0.5, 1.0]
AUCS = [0.5, 0.6, 0.7, 0.8]
H3_MIN_OK = 100
P_STAR = 0.5
H2_REFUTE = 0.10
H3_LO, H3_HI = 0.30, 0.70


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def wilson_upper(k, n):
    p = k / n
    den = 1 + Z * Z / n
    c = p + Z * Z / (2 * n)
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (c + h) / den


def boot_mult(rng, n):
    return rng.multinomial(n, np.full(n, 1.0 / n), size=R).astype(float)


def h1(rng, s, t):
    n = int(t.sum())
    if n == 0:
        return False
    M = boot_mult(rng, len(t))
    den = M @ t
    ok = den > 0
    share = (M @ s)[ok] / den[ok]
    est = s.sum() / n
    sd = share.std(ddof=1) if len(share) > 1 else 0.0
    if sd == 0:
        lo, hi = est, wilson_upper(s.sum(), n)
    else:
        lo, hi = est - Z * sd, est + Z * sd
    return hi < P_STAR or lo >= P_STAR


def h2(rng, s1, t1, s2, t2):
    if t1.sum() == 0 or t2.sum() == 0:
        return False
    M = boot_mult(rng, len(t1))
    d1, d2 = M @ t1, M @ t2
    ok = (d1 > 0) & (d2 > 0)
    diff = (M @ s2)[ok] / d2[ok] - (M @ s1)[ok] / d1[ok]
    if len(diff) < 2:
        return False
    sd = diff.std(ddof=1)
    if sd == 0:
        return False
    est = s2.sum() / t2.sum() - s1.sum() / t1.sum()
    lo, hi = est - Z * sd, est + Z * sd
    return lo > 0 or hi < H2_REFUTE


def h3(rng, day, y, score, ndays):
    pos, neg = y == 1, y == 0
    if pos.sum() == 0 or neg.sum() == 0:
        return False
    G = (score[pos][:, None] > score[neg][None, :]).astype(float)
    M = boot_mult(rng, ndays)
    wp, wn = M[:, day[pos]], M[:, day[neg]]
    sp, sn = wp.sum(1), wn.sum(1)
    ok = (sp > 0) & (sn > 0)
    if ok.sum() < H3_MIN_OK:
        return False
    a = np.einsum("ri,ij,rj->r", wp[ok], G, wn[ok]) / (sp[ok] * sn[ok])
    est = auc(y, score)
    sd = a.std(ddof=1)
    lo, hi = est - Z * sd, est + Z * sd
    return (lo >= H3_LO and hi <= H3_HI) or lo > H3_HI


def one_person(rng, pi, scale, f, sd):
    obs = rng.random(DAYS) < f
    od = np.flatnonzero(obs)
    no = len(od)
    early_len = int(rng.integers(EARLY[0], EARLY[1] + 1))
    u = ar1(rng, DAYS, sd, RHO)
    pday = sigmoid(math.log(pi / (1 - pi)) + u)
    p2day = sigmoid(math.log(min(2 * pi, 0.5) / (1 - min(2 * pi, 0.5))) + u)
    lam = {k: v * scale / f for k, v in PER_DAY.items()}
    n = {k: rng.poisson(lam[k], no) for k in lam}
    s = {k: rng.binomial(n[k], pday[od]) for k in n}
    s2alt = rng.binomial(n["c2"], p2day[od])
    early = od < early_len
    ei = np.flatnonzero(early)
    res = {}
    res["h1"] = h1(rng, s["c0"][ei].astype(float), n["c0"][ei].astype(float))
    res["h2_null"] = h2(rng, s["c1"][ei].astype(float), n["c1"][ei].astype(float),
                        s["c2"][ei].astype(float), n["c2"][ei].astype(float))
    res["h2_double"] = h2(rng, s["c1"][ei].astype(float), n["c1"][ei].astype(float),
                          s2alt[ei].astype(float), n["c2"][ei].astype(float))
    # H3: 前期の C0 の中の回答を 1 件ずつに広げる
    day = np.repeat(np.arange(len(ei)), n["c0"][ei])
    y = np.concatenate([np.r_[np.ones(k), np.zeros(m - k)] for k, m in zip(s["c0"][ei], n["c0"][ei])]) if len(ei) else np.zeros(0)
    z = rng.normal(0, 1, len(y))
    for a in AUCS:
        dlt = math.sqrt(2) * _ppf(a)
        res[f"h3_{a}"] = h3(rng, day, y, z + dlt * y, len(ei)) if len(ei) else False
    stuck_days = int((s["all"] > 0).sum())
    stuck = int(s["all"].sum())
    nonstuck = int(n["all"].sum()) - stuck
    res["e4"] = no >= 50 and stuck_days >= 30
    res["e4_posdays"] = stuck_days >= 30
    res["g2"] = (no >= 25 and stuck >= 10 and nonstuck >= 10
                 and int(n["c1"].sum()) >= 20 and int(n["c2"].sum()) >= 20)
    res["g2_stuck"] = stuck >= 10
    return res


def _ppf(p):
    # 標準正規の分位点（二分法・p は 0.5〜0.8 程度）
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


KEYS = ["h1", "h2_null", "h2_double"] + [f"h3_{a}" for a in AUCS] + ["e4", "e4_posdays", "g2", "g2_stuck"]


def run(seed, out, n_sim):
    rows = []
    idx = 0
    for scale in SCALES:
        for f in FS:
            for sd in SDS:
                for pi in PIS:
                    rng = np.random.default_rng([seed, idx])
                    idx += 1
                    acc = {k: 0 for k in KEYS}
                    for _ in range(n_sim):
                        r = one_person(rng, pi, scale, f, sd)
                        for k in KEYS:
                            acc[k] += int(r[k])
                    rows.append({"scale": scale, "f": f, "sd": sd, "pi": pi,
                                 **{k: acc[k] / n_sim for k in KEYS}})
                    print(scale, f, sd, pi, {k: round(acc[k] / n_sim, 2) for k in KEYS}, flush=True)
    req = []
    for scale in SCALES:
        for f in FS:
            for sd in SDS:
                sub = [r for r in rows if r["scale"] == scale and r["f"] == f and r["sd"] == sd]
                m = {}
                for k in KEYS:
                    hit = [r["pi"] for r in sub if r[k] >= 0.8]
                    m[k] = min(hit) if hit else None
                req.append({"scale": scale, "f": f, "sd": sd, **m})
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "required_rate.json"), "w") as fh:
        json.dump({"seed": seed, "n_sim": n_sim, "R": R, "rows": rows, "required": req}, fh, indent=1)
    lab = {"h1": "H1", "h2_null": "H2 差なし", "h2_double": "H2 C2 が 2 倍",
           **{f"h3_{a}": f"H3 AUC {a}" for a in AUCS},
           "e4": "E4", "e4_posdays": "E4 陽性日だけ", "g2": "G2", "g2_stuck": "G2 詰まり 10 件だけ"}
    with open(os.path.join(out, "required_rate.md"), "w") as fh:
        fh.write(f"# 判定不能でない確率が 0.8 以上になる最小の π（各点 {n_sim} 回・seed {seed}）\n\n")
        fh.write("「> 0.20」は格子の中に無い。回答の数は本人並み（6.35/経過日）と半分。\n\n")
        fh.write("| 回答の数 | f | σ_d | " + " | ".join(lab[k] for k in KEYS) + " |\n")
        fh.write("|" + "---|" * (3 + len(KEYS)) + "\n")
        for q in req:
            cells = ["> 0.20" if q[k] is None else f"{q[k]:g}" for k in KEYS]
            fh.write(f"| {'本人並み' if q['scale'] == 1 else '半分'} | {q['f']} | {q['sd']} | " + " | ".join(cells) + " |\n")
        fh.write("\n## 各点の確率\n\n| 回答の数 | f | σ_d | π | " + " | ".join(lab[k] for k in KEYS) + " |\n")
        fh.write("|" + "---|" * (4 + len(KEYS)) + "\n")
        for r in rows:
            fh.write(f"| {'本人並み' if r['scale'] == 1 else '半分'} | {r['f']} | {r['sd']} | {r['pi']:g} | "
                     + " | ".join(f"{r[k]:.2f}" for k in KEYS) + " |\n")


def selftest():
    rng = np.random.default_rng(1)
    assert abs(wilson_upper(0, 60) - 0.0602) < 0.001
    # H1: 詰まり 0 件・60 件なら Wilson で支持
    assert h1(rng, np.zeros(20), np.full(20, 3.0))
    # H1: 割合 0.5 付近では判定不能になりやすい
    s = np.array([0, 2, 1, 0, 2, 1, 1, 0, 2, 1] * 2, float); t = np.full(20, 2.0)
    assert not h1(rng, s, t)
    # H2: どちらにも詰まりが無ければ SD 0 で判定不能
    assert not h2(rng, np.zeros(20), np.full(20, 2.0), np.zeros(20), np.full(20, 1.0))
    # H3: 詰まりが 0 件なら判定不能
    assert not h3(rng, np.arange(10), np.zeros(10), np.zeros(10), 10)
    # H3: 大きな標本・真の AUC 0.5 なら支持が多い
    r2 = np.random.default_rng(2)
    day = np.repeat(np.arange(60), 10); y = (r2.random(600) < 0.3).astype(float); sc = r2.normal(0, 1, 600)
    assert h3(r2, day, y, sc, 60)
    assert abs(_ppf(0.8) - 0.8416) < 1e-3
    # 一人の模擬の形
    r = one_person(np.random.default_rng(3), 0.05, 1.0, 0.65, 0.5)
    assert set(r) == set(KEYS)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300)
