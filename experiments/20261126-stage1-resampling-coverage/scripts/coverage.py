"""S1-E5 の区間の作り方とブロックの長さを、段 1 に近い日の揺れの模擬の被覆で選ぶ（conditions.md）。

daysim（第 2.1 版）の生成・較正・巡回するブロックをそのまま使い、被覆は区間が出た模擬の中で数える。
使い方:
  python3 -I coverage.py <seed> <out_dir> [--quick]   本計算（--quick は各点 20 回の動作確認で、選びには使わない）
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "20261103-mhd-dryrun-v2", "scripts"))
import daysim as ds  # noqa: E402

R_SIMS = 400
BAND = (0.90, 0.98)
METHODS = ("percentile", "normal", "basic")
LRULES = {"L1": lambda m: 1, "L2": lambda m: 2, "Lcube": ds.rule_main}
LAM, SD = 11.75, 0.5


def grid():
    return [dict(D=D, pi=pi, AUC=auc, rho=rho)
            for D in (25, 30, 40) for pi in (0.05, 0.10, 0.20) for auc in (0.60, 0.70) for rho in (0.3, 0.5)]


def run_cell(seed, idx, p, lname, R):
    rng = np.random.default_rng(np.random.SeedSequence([seed, idx]))
    a, s, prev, av = ds.solve_params(p["pi"], p["AUC"], SD, seed)
    if abs(prev - p["pi"]) > 0.002 or abs(av - p["AUC"]) > 0.002:
        # Pool のワーカーの中で sys.exit すると親が結果を待ち続けうるので、例外で親へ返す（Codex の指摘）
        raise ValueError("点 %d で a・s が狙いから ±0.002 を超えた" % idx)
    ti, tsl, tconv = ds.population_values(rng, LAM, a, s, SD, p["rho"])
    cov = {(q, m): 0 for q in "is" for m in METHODS}
    wid = {(q, m): [] for q in "is" for m in METHODS}
    n_ci = 0
    for _ in range(R):
        o = ds.one_sim(rng, p["D"], LAM, a, s, SD, p["rho"], "block", LRULES[lname])
        if o["ci"] is None:
            continue
        n_ci += 1
        for q, tv in (("i", ti), ("s", tsl)):
            for m in METHODS:
                lo, hi = o["ci"][q][m]
                cov[(q, m)] += lo <= tv <= hi
                wid[(q, m)].append(hi - lo)
    res = dict(**p, L=lname, L_value=LRULES[lname](p["D"] - math.ceil(ds.TRAIN_FRAC * p["D"])), R=R, n_ci=n_ci,
               no_ci_frac=1 - n_ci / R, population=dict(intercept=ti, slope=tsl, converged=tconv), by_method={})
    for m in METHODS:
        res["by_method"][m] = dict(
            cov_i=cov[("i", m)] / n_ci if n_ci else None, cov_s=cov[("s", m)] / n_ci if n_ci else None,
            width_s_median=float(np.median(wid[("s", m)])) if n_ci else None,
            width_i_median=float(np.median(wid[("i", m)])) if n_ci else None)
    return res


def choose(rows):
    """conditions.md K3: 全点で切片と傾きの被覆が帯に入る組のうち、傾きの幅の中央値の最大が最小のもの。
    無ければ、被覆の最小（切片と傾きの両方・全点）が最大の組。区間が 1 回も出ない点は帯の外と数える。"""
    combos = [(l, m) for l in LRULES for m in METHODS]
    summary = {}
    for l, m in combos:
        rs = [r for r in rows if r["L"] == l]
        covs = []
        for r in rs:
            b = r["by_method"][m]
            covs += [b["cov_i"] if b["cov_i"] is not None else -1.0, b["cov_s"] if b["cov_s"] is not None else -1.0]
        widths = [r["by_method"][m]["width_s_median"] for r in rs if r["by_method"][m]["width_s_median"] is not None]
        summary["%s/%s" % (l, m)] = dict(min_cov=min(covs), max_cov=max(covs),
                                         all_in_band=all(BAND[0] <= c <= BAND[1] for c in covs),
                                         max_width_s_median=max(widths) if widths else None)
    inband = [k for k, v in summary.items() if v["all_in_band"]]
    if inband:
        pick = min(inband, key=lambda k: summary[k]["max_width_s_median"])
        how = "in_band_min_width"
    else:
        pick = max(summary, key=lambda k: summary[k]["min_cov"])
        how = "no_combo_in_band_max_min_coverage"
    return dict(pick=pick, how=how, summary=summary)


def main():
    seed, out = int(sys.argv[1]), sys.argv[2]
    quick = "--quick" in sys.argv
    R = 20 if quick else R_SIMS
    os.makedirs(out, exist_ok=True)
    t = time.time()
    jobs = [(seed, i * len(LRULES) + j, p, lname, R) for i, p in enumerate(grid()) for j, lname in enumerate(LRULES)]
    from multiprocessing import Pool
    with Pool(4) as pool:  # 4 本まで（gse-next の邪魔をしない）。種は点と L ごとに固定なので並べ方によらない
        rows = pool.starmap(run_cell, jobs)
    for (_, idx, p, lname, _), r in zip(jobs, rows):
        print(idx, p, lname, "no_ci %.2f" % r["no_ci_frac"],
              {m: (None if v["cov_s"] is None else round(v["cov_i"], 3), None if v["cov_s"] is None else round(v["cov_s"], 3)) for m, v in r["by_method"].items()})
    print("%.0fs" % (time.time() - t), flush=True)
    ch = choose(rows)
    name = "coverage_quick.json" if quick else "coverage.json"
    json.dump(dict(seed=seed, R=R, band=BAND, lam=LAM, sd=SD, rows=rows, choice=ch), open(os.path.join(out, name), "w"), indent=1)
    print(json.dumps(ch, indent=1))


if __name__ == "__main__":
    main()
