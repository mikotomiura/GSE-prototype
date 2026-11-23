"""合成の系列で EM の 1 反復の時間と反復の数を測り、当てはめの数を掛けて壁時計を見積もる（design §7 の手順 1・2）。

使い方: python3 -I timing.py <SEED> <cs1_units.json> <out.json> [--procs 6]
実データの記号は読まない。CS1 の書き手ごとの課題の数だけを units.json から数える（課題の数は結果の値ではない・判断 2）。
CoAuthor の k ごとの人数は B の集計（results/summary.json の all_secondary・P15・P30）から写した。

大きさ（俯瞰と B の notes の分布から置いた値）:
  coauthor_self: 700 記号 × 15 本 ・ coauthor_pool: 700 記号 × 900 本（43 人 × 約 22 本）
  cs1_self: 課題 5 × まとまり 4 × 2,340 記号 → 900 で切って 60 本 ・ cs1_pool: 30 人 × 6 課題 × 4 × 2,340 → 1,872 本
反復の時間は 3 回の中央値。反復の数は合成の書き手（共通の K = 3 に揺らぎ）で、構造ごとに
  共通（乱数の開始点）・本人 τ = 0（共通の解から／乱数から）・本人 τ = 1,000（共通の解から／本人 τ = 0 の解から）を測る。
"""
import json
import os
import resource
import sys
import time
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hmm2 as H  # noqa: E402

STRUCTS = [("hmm", 3), ("hmm", 6), ("hmm", 10), ("ar", 1), ("ar", 2), ("ar", 3)]
TAUS = [0, 100, 1000, 10000]
# B の集計から（k: その k に入る書き手の数・副 = n_w ≥ k + 5）
COA_K = {1: 28, 2: 28, 3: 25, 5: 21, 8: 19, 12: 18, 15: 17, 20: 12, 30: 9}
COA_POOL_FITS = 28  # w を除く共通（評価の単位を持つ書き手ごと）
CS1_K = [1, 2, 3, 5]


def common_model(rng):
    m = H.random_model("hmm", 3, rng)
    m["A"] = 0.9 * np.eye(3) + 0.1 * m["A"]
    return m


def perturb(m, rng):
    q = dict(m)
    A = m["A"] + np.diag(rng.uniform(-0.05, 0.05, 3))
    A = np.clip(A, 1e-6, None)
    q["A"] = A / A.sum(1, keepdims=True)
    q["B"] = np.stack([rng.dirichlet(200 * r + 1e-3) for r in m["B"]])
    return q


def one_iter(m, D, pr):
    t0 = time.perf_counter()
    S, _ = H.counts(m, D)
    H.normalize(m["kind"], {k: S[k] + pr[k] for k in H.keys_of(m["kind"])})
    return time.perf_counter() - t0


def sbar(m, D):
    S, _ = H.counts(m, D)
    return H.sbar_of(S, D.nobs)


def main():
    seed, units_p, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 6
    rng = np.random.default_rng([seed, 99])
    cm = common_model(rng)
    # 1 反復の時間
    sizes = {"coauthor_self": [700] * 15, "coauthor_pool": [700] * 900,
             "cs1_self": [2340] * 20, "cs1_pool": [2340] * 720}
    seqs = {k: H.sample(cm, L, rng) for k, L in sizes.items()}
    per_iter = {}
    for kind, K in STRUCTS:
        name = "%s%d" % (kind, K)
        for sz, ss in seqs.items():
            D = H.Data(ss, chunk=H.CHUNK)
            _, h, T = H.r0_r1(ss)
            m = H.random_model(kind, K, rng, r1=T, r0=h)
            pr = H.base_prior(kind, K)
            per_iter.setdefault(name, {})[sz] = float(np.median([one_iter(m, D, pr) for _ in range(3)]))
            print(name, sz, "%.3f s/iter" % per_iter[name][sz], flush=True)
    # 反復の数（CoAuthor の大きさの合成の書き手 3 人）
    iters = {}
    pool = H.sample(cm, [700] * 300, rng)
    for kind, K in STRUCTS:
        name = "%s%d" % (kind, K)
        Dp = H.Data(pool, chunk=H.CHUNK)
        _, hp, Tp = H.r0_r1(pool)
        mp, _, it_pool, conv_pool, _ = H.em_from(H.random_model(kind, K, rng, r1=Tp, r0=hp), Dp, H.base_prior(kind, K))
        sb = sbar(mp, Dp)
        rec = dict(pool=[it_pool], self0_from_pool=[], self0_random=[], self1000_from_pool=[], self1000_from_self0=[])
        for _ in range(3):
            ss = H.sample(perturb(cm, rng), [700] * 15, rng)
            D = H.Data(ss, chunk=H.CHUNK)
            _, h, T = H.r0_r1(ss)
            pr0 = H.base_prior(kind, K)
            m0, _, it, _, _ = H.em_from(mp, D, pr0)
            rec["self0_from_pool"].append(it)
            rec["self0_random"].append(H.em_from(H.random_model(kind, K, rng, r1=T, r0=h), D, pr0)[2])
            pr1 = H.make_prior(kind, K, 1000, sb)
            rec["self1000_from_pool"].append(H.em_from(mp, D, pr1)[2])
            rec["self1000_from_self0"].append(H.em_from(m0, D, pr1)[2])
        iters[name] = rec
        print(name, {k: v for k, v in rec.items()}, flush=True)
    # 当てはめの数（design §3.3・§3.4・§2.2）
    units = json.load(open(units_p))
    n_cs1 = sorted(Counter(units.values()).values())
    cs1_k = {k: sum(1 for n in n_cs1 if n >= k + 1) for k in CS1_K}

    def med(x):
        return float(np.median(x))

    def sec_self(name, sz, taus):
        """1 書き手 × 1 k × 1 構造の本人の当てはめの秒（τ = 0 は 2 開始点、τ > 0 は 2 開始点）。"""
        r, p = iters[name], per_iter[name][sz]
        s = p * (med(r["self0_from_pool"]) + med(r["self0_random"]))
        s += p * (med(r["self1000_from_pool"]) + med(r["self1000_from_self0"])) * sum(1 for t in taus if t > 0)
        return s

    def estimate(cut):
        structs = [s for s in STRUCTS if not ("K10" in cut and s == ("hmm", 10))]
        taus = [t for t in TAUS if not ("tau100" in cut and t == 100)]
        coa_k = {k: v for k, v in COA_K.items() if not ("P30" in cut and k in (20, 30))}
        ck = {k: v for k, v in cs1_k.items() if not ("cs1k" in cut and k == 2)}
        tot = 0.0
        for kind, K in structs:
            name = "%s%d" % (kind, K)
            pool_it = med(iters[name]["pool"])
            # 共通: 全員 3 開始点 ＋ w を除く 1 開始点（反復は共通の解から・本人 τ = 0 の共通から始めた回数で近似）
            tot += per_iter[name]["coauthor_pool"] * (3 * pool_it + COA_POOL_FITS * med(iters[name]["self0_from_pool"]))
            tot += per_iter[name]["cs1_pool"] * (3 * pool_it + len(n_cs1) * med(iters[name]["self0_from_pool"]))
            # 本人: 主の当てはめ ＋ k ≥ 3 の折り目 2 つ（折り目の当てはめは k − 1・k − 2 単位で小さいが同じ秒で数える）
            for k, nw in coa_k.items():
                tot += nw * sec_self(name, "coauthor_self", taus) * (1 + (2 if k >= 3 else 0))
            for k, nw in ck.items():
                tot += nw * sec_self(name, "cs1_self", taus) * (1 + (2 if k >= 3 else 0))
        return dict(cpu_hours=tot / 3600, wall_hours=tot / 3600 / procs)

    cuts = {"none": [], "a_cs1k": ["cs1k"], "b_P30": ["cs1k", "P30"], "c_K10": ["cs1k", "P30", "K10"],
            "d_tau100": ["cs1k", "P30", "K10", "tau100"]}
    est = {k: estimate(v) for k, v in cuts.items()}
    res = dict(per_iter_sec=per_iter, iters=iters, cs1_writers=len(n_cs1), cs1_writers_per_k=cs1_k,
               coauthor_writers_per_k=COA_K, procs=procs, estimate=est,
               max_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20,  # macOS は bytes
               note="合成の系列による見積もり。実データの反復の数は違いうる。本人の折り目は主と同じ秒で数えた（上側）")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(est, indent=1))


if __name__ == "__main__":
    main()
