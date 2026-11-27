"""3 名を合わせた H1〜H3 の判定と、H2・H3 の件数の下限を合成で確かめる（conditions.md 第 2 版）。

使い方:
  python3 -I pooled.py --selftest
  python3 -I pooled.py <seed> <out_dir> [n_sim] [workers]
打鍵も記録も読まない。生成は第 1 版（required_rate.py）と同じ部品を使う。
"""
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "20261103-mhd-dryrun-v2", "scripts"))
import required_rate as v1  # noqa: E402
from daysim import ar1, auc  # noqa: E402

R = 500
Z = v1.Z
F = 0.65
SD_DAY = 0.5
SD_PERSON = 0.5
PIS = v1.PIS
AUCS = v1.AUCS
CONFIGS = {"all_full": [1.0, 1.0, 1.0], "all_half": [0.5, 0.5, 0.5], "mixed": [1.0, 0.5, 0.5]}
HETS = {"common": 0.0, "varies": SD_PERSON}
FLOOR = 10
UNDET, SUPPORT, REFUTE = 0, 1, 2


def logit(p):
    return math.log(p / (1 - p))


def gen_person(rng, pi, scale, b):
    """1 人の前期のデータ（観測日ごとの件数と、H3 の C0 の中の回答）。b は人の効果（対数オッズ）。"""
    obs = rng.random(v1.DAYS) < F
    od = np.flatnonzero(obs)
    early_len = int(rng.integers(v1.EARLY[0], v1.EARLY[1] + 1))
    u = ar1(rng, v1.DAYS, SD_DAY, v1.RHO)
    p2 = min(2 * pi, 0.5)
    pday = v1.sigmoid(logit(pi) + b + u)
    p2day = v1.sigmoid(logit(p2) + b + u)
    lam = {k: v * scale / F for k, v in v1.PER_DAY.items() if k != "all"}
    n = {k: rng.poisson(lam[k], len(od)) for k in lam}
    s = {k: rng.binomial(n[k], pday[od]) for k in n}
    s2d = rng.binomial(n["c2"], p2day[od])
    ei = np.flatnonzero(od < early_len)
    d = {"nd": len(ei)}
    for k in ("c0", "c1", "c2"):
        d[f"{k}_n"] = n[k][ei].astype(float)
        d[f"{k}_s"] = s[k][ei].astype(float)
    d["c2_sd"] = s2d[ei].astype(float)
    if len(ei):
        d["h3_day"] = np.repeat(np.arange(len(ei)), n["c0"][ei])
        d["h3_y"] = np.concatenate([np.r_[np.ones(a), np.zeros(m - a)] for a, m in zip(s["c0"][ei], n["c0"][ei])])
    else:
        d["h3_day"], d["h3_y"] = np.zeros(0, int), np.zeros(0)
    d["h3_z"] = rng.normal(0, 1, len(d["h3_y"]))
    return d


def weights(rng, nds, two_stage):
    """(R, 日の総数) の重み。two_stage: 人を復元で 3 人引き、引いた人ごとに日を復元で引く。"""
    k = rng.multinomial(len(nds), np.full(len(nds), 1.0 / len(nds)), size=R) if two_stage \
        else np.ones((R, len(nds)), int)
    blocks = []
    for p, nd in enumerate(nds):
        if nd == 0:
            continue
        blocks.append(rng.multinomial(k[:, p] * nd, np.full(nd, 1.0 / nd)).astype(float))
    return np.hstack(blocks) if blocks else np.zeros((R, 0))


def judge_ratio(M, s, t):
    n = t.sum()
    if n == 0:
        return UNDET
    den = M @ t
    ok = den > 0
    share = (M @ s)[ok] / den[ok]
    est = s.sum() / n
    sd = share.std(ddof=1) if len(share) > 1 else 0.0
    if sd == 0:
        lo, hi = est, v1.wilson_upper(s.sum(), n)
    else:
        lo, hi = est - Z * sd, est + Z * sd
    return SUPPORT if hi < v1.P_STAR else REFUTE if lo >= v1.P_STAR else UNDET


def judge_diff(M, s1, t1, s2, t2, floor):
    if t1.sum() == 0 or t2.sum() == 0 or s1.sum() + s2.sum() < floor:
        return UNDET
    d1, d2 = M @ t1, M @ t2
    ok = (d1 > 0) & (d2 > 0)
    diff = (M @ s2)[ok] / d2[ok] - (M @ s1)[ok] / d1[ok]
    if len(diff) < 2:
        return UNDET
    sd = diff.std(ddof=1)
    if sd == 0:
        return UNDET
    est = s2.sum() / t2.sum() - s1.sum() / t1.sum()
    lo, hi = est - Z * sd, est + Z * sd
    return SUPPORT if lo > 0 else REFUTE if hi < v1.H2_REFUTE else UNDET


def judge_auc(M, day, y, score, floor):
    pos, neg = y == 1, y == 0
    if pos.sum() == 0 or neg.sum() == 0 or pos.sum() < floor or neg.sum() < floor:
        return UNDET
    G = (score[pos][:, None] > score[neg][None, :]).astype(float)
    wp, wn = M[:, day[pos]], M[:, day[neg]]
    sp, sn = wp.sum(1), wn.sum(1)
    ok = (sp > 0) & (sn > 0)
    if ok.sum() < v1.H3_MIN_OK:
        return UNDET
    a = np.einsum("ri,ij,rj->r", wp[ok], G, wn[ok]) / (sp[ok] * sn[ok])
    est = auc(y, score)
    sd = a.std(ddof=1)
    lo, hi = est - Z * sd, est + Z * sd
    if lo >= v1.H3_LO and hi <= v1.H3_HI:
        return SUPPORT
    return REFUTE if lo > v1.H3_HI else UNDET


def dlt(a):
    return math.sqrt(2) * v1._ppf(a)


def judge_all(M, people, floor):
    """people の前期のデータを日の軸でつないで、H1〜H3 を判定する（M の列はつないだ日）。"""
    cat = lambda k: np.concatenate([p[k] for p in people if p["nd"]]) if any(p["nd"] for p in people) else np.zeros(0)  # noqa: E731
    out = {"h1": judge_ratio(M, cat("c0_s"), cat("c0_n"))}
    out["h2_null"] = judge_diff(M, cat("c1_s"), cat("c1_n"), cat("c2_s"), cat("c2_n"), floor)
    out["h2_double"] = judge_diff(M, cat("c1_s"), cat("c1_n"), cat("c2_sd"), cat("c2_n"), floor)
    off, days, ys, zs = 0, [], [], []
    for p in people:
        if p["nd"]:
            days.append(p["h3_day"] + off)
            ys.append(p["h3_y"])
            zs.append(p["h3_z"])
            off += p["nd"]
    day = np.concatenate(days) if days else np.zeros(0, int)
    y = np.concatenate(ys) if ys else np.zeros(0)
    z = np.concatenate(zs) if zs else np.zeros(0)
    for a in AUCS:
        out[f"h3_{a}"] = judge_auc(M, day, y, z + dlt(a) * y, floor) if len(y) else UNDET
    return out


KEYS = ["h1", "h2_null", "h2_double"] + [f"h3_{a}" for a in AUCS]
METHODS = ["person_nofloor", "person_floor", "pool_two_stage", "pool_day_only"]


def one_set(rng, pi, scales, het):
    b = rng.normal(0, het, len(scales)) if het > 0 else np.zeros(len(scales))
    people = [gen_person(rng, pi, sc, bi) for sc, bi in zip(scales, b)]
    res = {}
    M1 = weights(rng, [people[0]["nd"]], False)
    res["person_nofloor"] = judge_all(M1, people[:1], 0)
    res["person_floor"] = judge_all(M1, people[:1], FLOOR)
    nds = [p["nd"] for p in people]
    res["pool_two_stage"] = judge_all(weights(rng, nds, True), people, FLOOR)
    res["pool_day_only"] = judge_all(weights(rng, nds, False), people, FLOOR)
    return res


def run_point(args):
    seed, idx, cfg, het, pi, n_sim = args
    rng = np.random.default_rng([seed, 1000 + idx])
    acc = {m: {k: [0, 0, 0] for k in KEYS} for m in METHODS}
    for _ in range(n_sim):
        r = one_set(rng, pi, CONFIGS[cfg], HETS[het])
        for m in METHODS:
            for k in KEYS:
                acc[m][k][r[m][k]] += 1
    row = {"config": cfg, "het": het, "pi": pi}
    for m in METHODS:
        for k in KEYS:
            u, s_, rf = acc[m][k]
            row[f"{m}:{k}"] = {"determined": (s_ + rf) / n_sim, "support": s_ / n_sim, "refute": rf / n_sim}
    return row


LAB = {"h1": "H1", "h2_null": "H2 差なし", "h2_double": "H2 C2 が 2 倍",
       **{f"h3_{a}": f"H3 AUC {a}" for a in AUCS}}
MLAB = {"person_nofloor": "人ごと・下限なし", "person_floor": "人ごと・下限あり",
        "pool_two_stage": "合わせた・人と日", "pool_day_only": "合わせた・日だけ"}
CLAB = {"all_full": "3 名とも本人並み", "all_half": "3 名とも半分", "mixed": "混在（本人並み 1・半分 2）"}
HLAB = {"common": "共通の π", "varies": "人でばらつく（SD 0.5）"}


def run(seed, out, n_sim, workers):
    jobs, idx = [], 0
    for cfg in CONFIGS:
        for het in HETS:
            for pi in PIS:
                jobs.append((seed, idx, cfg, het, pi, n_sim))
                idx += 1
    with ProcessPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(run_point, jobs))
    for r in rows:
        print(r["config"], r["het"], r["pi"],
              {m: {k: round(r[f"{m}:{k}"]["determined"], 2) for k in KEYS} for m in METHODS}, flush=True)
    req = []
    for cfg in CONFIGS:
        for het in HETS:
            sub = [r for r in rows if r["config"] == cfg and r["het"] == het]
            q = {"config": cfg, "het": het}
            for m in METHODS:
                for k in KEYS:
                    hit = [r["pi"] for r in sub if r[f"{m}:{k}"]["determined"] >= 0.8]
                    q[f"{m}:{k}"] = min(hit) if hit else None
            req.append(q)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "pooled.json"), "w") as fh:
        json.dump({"seed": seed, "n_sim": n_sim, "R": R, "floor": FLOOR, "f": F, "sd_day": SD_DAY,
                   "sd_person": SD_PERSON, "rows": rows, "required": req}, fh, indent=1)
    with open(os.path.join(out, "pooled.md"), "w") as fh:
        fh.write(f"# 3 名を合わせた判定と下限（第 2 版・各点 {n_sim} 組・seed {seed}・f {F}・σ_d {SD_DAY}）\n\n")
        fh.write("判定不能でない確率が 0.8 以上になる最小の π。「> 0.20」は格子の中に無い。人ごとは組の 1 人目（混在では本人並みの人）。"
                 f"下限: H2 は C1・C2 の中の詰まりが合わせて {FLOOR} 件以上、H3 は詰まり・詰まりでないがそれぞれ {FLOOR} 件以上。H1 は下限なし。\n\n")
        for k in KEYS:
            fh.write(f"## {LAB[k]}\n\n| 回答の数 | 人の間 | " + " | ".join(MLAB[m] for m in METHODS) + " |\n")
            fh.write("|" + "---|" * (2 + len(METHODS)) + "\n")
            for q in req:
                cells = ["> 0.20" if q[f"{m}:{k}"] is None else f"{q[f'{m}:{k}']:g}" for m in METHODS]
                fh.write(f"| {CLAB[q['config']]} | {HLAB[q['het']]} | " + " | ".join(cells) + " |\n")
            fh.write("\n")
        fh.write("## 各点の確率（判定不能でない／支持／反証）\n\n")
        for k in KEYS:
            fh.write(f"### {LAB[k]}\n\n| 回答の数 | 人の間 | π | " + " | ".join(MLAB[m] for m in METHODS) + " |\n")
            fh.write("|" + "---|" * (3 + len(METHODS)) + "\n")
            for r in rows:
                cells = []
                for m in METHODS:
                    v = r[f"{m}:{k}"]
                    cells.append(f"{v['determined']:.2f} / {v['support']:.2f} / {v['refute']:.2f}")
                fh.write(f"| {CLAB[r['config']]} | {HLAB[r['het']]} | {r['pi']:g} | " + " | ".join(cells) + " |\n")
            fh.write("\n")


def selftest():
    rng = np.random.default_rng(1)
    # 重み: 日だけなら人ごとの列の和は日の数、2 段なら全体の和は日の総数
    nds = [5, 0, 7]
    Md = weights(rng, nds, False)
    assert Md.shape == (R, 12) and np.allclose(Md[:, :5].sum(1), 5) and np.allclose(Md[:, 5:].sum(1), 7)
    Mt = weights(rng, nds, True)
    assert Mt.shape == (R, 12)
    tot = Mt.sum(1)
    assert set(np.unique(tot)).issubset({0.0, 5.0, 7.0, 10.0, 12.0, 14.0, 15.0, 17.0, 19.0, 21.0})
    # 下限: H2 は詰まり 9 件なら判定不能、H3 は詰まり 9 件なら判定不能
    M = weights(rng, [20], False)
    s1 = np.zeros(20); s1[:4] = 1; s2 = np.zeros(20); s2[:5] = 1
    t = np.full(20, 3.0)
    assert judge_diff(M, s1, t, s2, t, 10) == UNDET
    day = np.repeat(np.arange(20), 5); y = np.zeros(100); y[:9] = 1
    assert judge_auc(M, day, y, rng.normal(0, 1, 100), 10) == UNDET
    # 下限なし・同じ形なら判定が出うる（関数が動くこと）
    assert judge_diff(M, s1, t, s2, t, 0) in (UNDET, SUPPORT, REFUTE)
    # 1 人の日だけの再標本の判定は第 1 版の h1 と同じ向き（詰まり 0 件 → Wilson で支持）
    p = gen_person(np.random.default_rng(3), 0.05, 1.0, 0.0)
    assert set(["nd", "c0_n", "c0_s", "h3_day", "h3_y", "h3_z"]).issubset(p)
    z = {"nd": 20, "c0_s": np.zeros(20), "c0_n": np.full(20, 3.0)}
    assert judge_ratio(weights(rng, [20], False), z["c0_s"], z["c0_n"]) == SUPPORT
    r = one_set(np.random.default_rng(4), 0.05, CONFIGS["mixed"], SD_PERSON)
    assert set(r) == set(METHODS) and all(set(r[m]) == set(KEYS) for m in METHODS)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        run(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300,
            int(sys.argv[4]) if len(sys.argv) > 4 else 8)
