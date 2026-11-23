"""合成の系列で EM の 1 反復の時間と反復の数を測り、当てはめの数を掛けて計算の時間を見積もる（conditions D6 の測り直し）。

使い方: python3 -I timing.py <SEED> <out.json> [--procs 16]
実データは読まない。書き手の数（k ごと）は前回の results/timing.json の値を写した（結果の値ではない）。

見積もりは 2 つ出す。
  (1) 合成の絶対の見積もり（この機械の 1 反復の秒 × 反復の数 × 当てはめの数 / プロセスの数）
  (2) 前回の HP Z2 の実測（summary.json の seconds）に、同じ合成の式で出した「今回 / 前回」の比を掛けた値。
      共通（pools）と書き手（writers）を別々に掛ける。前回の書き手の実測にはロジスティックが入っている（上側に寄る）。
大きさ（前回と同じ）: coauthor_self 700 記号 × 15 本・coauthor_pool 700 × 900・cs1_self 2,340 × 20・cs1_pool 2,340 × 720。
反復の数は合成の書き手 3 人（共通の K = 3 に揺らぎ）で、構造ごとに、共通（乱数の開始点）・本人 τ = 0（共通の解から／乱数から）・
本人の有限の τ > 0 それぞれ（共通の解から／本人 τ = 0 の解から）を測る。
"""
import json
import os
import resource
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hmm2 as H  # noqa: E402
import ml  # noqa: E402

OLD_STRUCTS = ml.PREV_STRUCTS
OLD_TAUS = [0, 100, 1000, 10000]
NEW_STRUCTS = ml.STRUCTS
NEW_TAUS = ml.TAUS_FIT
ALL_TAUS = sorted(set(OLD_TAUS) | set(NEW_TAUS))
# 前回の results/timing.json から（k: その k に入る書き手の数）
COA_K = {1: 28, 2: 28, 3: 25, 5: 21, 8: 19, 12: 18, 15: 17, 20: 12, 30: 9}
CS1_K = {1: 25, 2: 23, 3: 23, 5: 23}
COA_POOL_FITS, CS1_POOL_FITS = 28, 25  # w を除く共通（評価の単位を持つ書き手ごと）
# 前回の HP Z2 の実測（experiments/20261104-coauthor-ml-improve/results/summary.json の seconds）
PREV_SEC = {"coauthor": dict(pools=1537.977656364441, writers=1172.7950475215912),
            "cs1": dict(pools=4950.7214233875275, writers=1329.0977821350098)}


def common_model(rng):
    m = H.random_model("hmm", 3, rng)
    m["A"] = 0.9 * np.eye(3) + 0.1 * m["A"]
    return m


def perturb(m, rng):
    q = dict(m)
    A = np.clip(m["A"] + np.diag(rng.uniform(-0.05, 0.05, 3)), 1e-6, None)
    q["A"] = A / A.sum(1, keepdims=True)
    q["B"] = np.stack([rng.dirichlet(200 * r + 1e-3) for r in m["B"]])
    return q


def one_iter(m, D, pr):
    t0 = time.perf_counter()
    S, _ = H.counts(m, D)
    H.normalize(m["kind"], {k: S[k] + pr[k] for k in H.keys_of(m["kind"])})
    return time.perf_counter() - t0


def main():
    seed, out = int(sys.argv[1]), sys.argv[2]
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 16
    t_start = time.time()
    rng = np.random.default_rng([seed, 99])
    cm = common_model(rng)
    sizes = {"coauthor_self": [700] * 15, "coauthor_pool": [700] * 900, "cs1_self": [2340] * 20, "cs1_pool": [2340] * 720}
    seqs = {k: H.sample(cm, L, rng) for k, L in sizes.items()}
    per_iter = {}
    for kind, K in OLD_STRUCTS:
        name = "%s%d" % (kind, K)
        for sz, ss in seqs.items():
            D = H.Batched(ss, chunk=H.CHUNK) if sz.endswith("pool") else H.Data(ss, chunk=H.CHUNK)
            _, h, T = H.r0_r1(ss)
            m = H.random_model(kind, K, rng, r1=T, r0=h)
            pr = H.base_prior(kind, K)
            per_iter.setdefault(name, {})[sz] = float(np.median([one_iter(m, D, pr) for _ in range(3)]))
            print(name, sz, "%.3f s/iter" % per_iter[name][sz], flush=True)
    iters = {}
    pool = H.sample(cm, [700] * 300, rng)
    for kind, K in OLD_STRUCTS:
        name = "%s%d" % (kind, K)
        Dp = H.Data(pool, chunk=H.CHUNK)
        _, hp, Tp = H.r0_r1(pool)
        mp, _, it_pool, _, _ = H.em_from(H.random_model(kind, K, rng, r1=Tp, r0=hp), Dp, H.base_prior(kind, K))
        S, _ = H.counts(mp, Dp)
        sb = H.sbar_of(S, Dp.nobs)
        rec = dict(pool=[it_pool], self0_from_pool=[], self0_random=[], **{"tau%d" % t: [] for t in ALL_TAUS if t > 0})
        for _ in range(3):
            ss = H.sample(perturb(cm, rng), [700] * 15, rng)
            D = H.Data(ss, chunk=H.CHUNK)
            _, h, T = H.r0_r1(ss)
            pr0 = H.base_prior(kind, K)
            m0, _, it, _, _ = H.em_from(mp, D, pr0)
            rec["self0_from_pool"].append(it)
            rec["self0_random"].append(H.em_from(H.random_model(kind, K, rng, r1=T, r0=h), D, pr0)[2])
            for t in ALL_TAUS:
                if t > 0:
                    pr1 = H.make_prior(kind, K, t, sb)
                    rec["tau%d" % t].append(H.em_from(mp, D, pr1)[2] + H.em_from(m0, D, pr1)[2])
        iters[name] = rec
        print(name, rec, flush=True)

    def med(x):
        return float(np.median(x))

    def sec_self(name, sz, taus):
        """1 書き手 × 1 k × 1 構造の本人の当てはめの秒（τ = 0 は 2 開始点、τ > 0 は 2 開始点の和）。"""
        r, p = iters[name], per_iter[name][sz]
        s = p * (med(r["self0_from_pool"]) + med(r["self0_random"]))
        s += p * sum(med(r["tau%d" % t]) for t in taus if t > 0)
        return s

    def estimate(structs, taus):
        pools = dict(coauthor=0.0, cs1=0.0)
        writers = dict(coauthor=0.0, cs1=0.0)
        for kind, K in structs:
            name = "%s%d" % (kind, K)
            pool_it = med(iters[name]["pool"])
            excl_it = med(iters[name]["self0_from_pool"])
            pools["coauthor"] += per_iter[name]["coauthor_pool"] * (ml.POOL_STARTS * pool_it + COA_POOL_FITS * excl_it)
            pools["cs1"] += per_iter[name]["cs1_pool"] * (ml.POOL_STARTS * pool_it + CS1_POOL_FITS * excl_it)
            for k, nw in COA_K.items():
                writers["coauthor"] += nw * sec_self(name, "coauthor_self", taus) * (1 + (2 if k >= 3 else 0))
            for k, nw in CS1_K.items():
                writers["cs1"] += nw * sec_self(name, "cs1_self", taus) * (1 + (2 if k >= 3 else 0))
        return dict(pools_cpu_sec=pools, writers_cpu_sec=writers,
                    wall_hours=(sum(pools.values()) + sum(writers.values())) / 3600 / procs)

    est_new, est_old = estimate(NEW_STRUCTS, NEW_TAUS), estimate(OLD_STRUCTS, OLD_TAUS)
    scaled = {}
    for ds in ("coauthor", "cs1"):
        rp = est_new["pools_cpu_sec"][ds] / est_old["pools_cpu_sec"][ds]
        rw = est_new["writers_cpu_sec"][ds] / est_old["writers_cpu_sec"][ds]
        scaled[ds] = dict(ratio_pools=rp, ratio_writers=rw, pools_sec=PREV_SEC[ds]["pools"] * rp,
                          writers_sec=PREV_SEC[ds]["writers"] * rw)
    scaled["total_hours"] = sum(v["pools_sec"] + v["writers_sec"] for k, v in scaled.items() if k != "total_hours") / 3600
    res = dict(per_iter_sec=per_iter, iters=iters, procs=procs, estimate_new=est_new, estimate_old_same_formula=est_old,
               scaled_from_prev_hp_z2=scaled, platform=sys.platform, seconds=time.time() - t_start,
               max_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20,  # macOS は bytes
               note="合成の系列による見積もり。実データの反復の数は違いうる。本人の折り目は主と同じ秒で数えた（上側）。"
                    "前回の書き手の実測はロジスティックを含む（比を掛けた値は上側）")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(dict(estimate_new=est_new, scaled=scaled), indent=1))


if __name__ == "__main__":
    main()
