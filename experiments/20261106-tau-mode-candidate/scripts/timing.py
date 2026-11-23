"""合成の系列で、前の試験から足した計算の時間を測り、前の試験の HP Z2 の実測に足して本計算の時間を見積もる（conditions D6）。

使い方: python3 -I timing.py <SEED> <out.json>
実データは読まない。前の試験の実測は experiments/20261104-timeseries-tau-extend/results/summary.json の seconds（集計値）。
足した計算は 3 つ:
  (1) 全員の共通の S̄（構造ごとに、全員の共通の解で E 段を 1 回・fit_pool_full の末尾）
  (2) 最頻値の評価（書き手 × 構造ごとに、評価の単位で前向き 1 回）
  (3) 相手「最頻値」と行 tau_mode の集計（delta_stats の区間 2,000 回の増え）
大きさは前の試験の timing.py と同じ（coauthor の共通 700 × 900・cs1 の共通 2,340 × 720）。評価の単位は上側に取る
（coauthor 700 × 5・cs1 2,340 × 20）。書き手の数は coauthor 28・cs1 25。プロセスは 16（HP Z2）で割る。
この Mac の 1 回の秒をそのまま使う（HP Z2 の方が遅いことがあるので、足す分は 3 倍して上側に見る）。
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hmm2 as H  # noqa: E402
import ml  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, "../../20261104-timeseries-tau-extend/results/summary.json")
SIZES = {"coauthor": dict(pool=(700, 900), ev=(700, 5), writers=28), "cs1": dict(pool=(2340, 720), ev=(2340, 20), writers=25)}
PROCS, SAFETY = 16, 3.0


def main(seed, out):
    rng = np.random.default_rng([seed, 501])
    prev = json.load(open(PREV, encoding="utf-8"))
    R = dict(prev_seconds={d: prev["datasets"][d]["seconds"]["pools"] + prev["datasets"][d]["seconds"]["writers"]
                           for d in SIZES}, added={})
    cm = H.random_model("hmm", 3, rng)
    for ds, z in SIZES.items():
        L, n = z["pool"]
        pool = H.sample(cm, [L] * n, rng)
        Dp = H.Batched(pool, chunk=H.CHUNK)
        Le, ne = z["ev"]
        ev = ml.Eval(H.sample(cm, [Le] * ne, rng), [np.ones(Le, dtype=bool)] * ne)
        _, h, T = H.r0_r1(pool)
        estep, mode = 0.0, 0.0
        for kind, K in ml.STRUCTS:
            m = H.random_model(kind, K, rng, r1=T, r0=h)
            t0 = time.perf_counter()
            S, _ = H.counts(m, Dp)
            estep += time.perf_counter() - t0
            sb = H.sbar_of(S, Dp.nobs)
            t0 = time.perf_counter()
            mm, _ = H.mode_of(kind, sb)
            ev.ll_zero(mm)
            mode += time.perf_counter() - t0
        # 区間 2,000 回の 1 回分（書き手の数の値）× 足した集計の数（行 1 つ × 相手 5 ＋ 既存の行 × 相手 1・全記号と押下・k × 構造 × パネル）
        vals = list(rng.normal(size=z["writers"]))
        t0 = time.perf_counter()
        for _ in range(20):
            ml.delta_stats(vals, rng)
        one = (time.perf_counter() - t0) / 20
        cells = 2 * 9 * 4 * 3 * (5 + 16)  # 全記号・押下 × k（最大 9）× 構造 × パネル（主 2 ＋ 副）×（新しい行の相手 5 ＋ 既存の行 16 の新しい相手）
        added = estep + mode * z["writers"] / PROCS + one * cells
        R["added"][ds] = dict(full_estep_sec=estep, mode_eval_sec_per_writer=mode, delta_stats_sec=one, cells=cells,
                              added_sec=added, added_sec_upper=added * SAFETY)
    R["estimate_sec"] = sum(R["prev_seconds"].values()) + sum(a["added_sec_upper"] for a in R["added"].values())
    R["estimate_hours"] = R["estimate_sec"] / 3600
    json.dump(R, open(out, "w"), indent=1)
    print(json.dumps(dict(estimate_hours=round(R["estimate_hours"], 2),
                          added_upper_sec={d: round(a["added_sec_upper"]) for d, a in R["added"].items()})))


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2])
