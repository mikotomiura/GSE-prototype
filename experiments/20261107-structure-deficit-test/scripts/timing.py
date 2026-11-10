"""本計算の時間の見積もり（conditions D6）。実データは読まない。

基は ml-improve の HP Z2 の実測（experiments/20261104-coauthor-ml-improve/results/summary.json の seconds・同じ 6 構造・26 記号・
τ 4 値・折り目つき・k の格子すべて・パネルの外の書き手も当てはめた）。これを次の 3 つで直す。
  (1) 記号の数の比 r(q): この Mac で、合成の系列の E 段（H.counts）の時間を構造ごとに測り、6 構造の和の比（q² + 1 対 26）。
  (2) 書き手の当てはめの量の比: Σ_k（当てはめの数 × 学習の単位の数）。前は τ 4 値 ×（本体 ＋ k ≥ 3 の折り目 2 つ）×
      k の格子、今回は τ 8 値 × 当てはめる k だけ。パネルの書き手の分だけで比べる（上側に見る）。
  (3) w を除く共通の数の比: パネルに入る書き手の数 / 前の当てはめた書き手の数（全員の共通の分は小さいので無視・上側）。
1 組の秒 = 共通 × (3) × r(q) ＋ 書き手 × (2) × r(q)。6 組の和に SAFETY を掛けて上側を出す（反復の回数が列で変わりうる）。

使い方: python3 -I timing.py <SEED> <out.json>
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
PREV = os.path.join(HERE, "../../20261104-coauthor-ml-improve/results/summary.json")
PREV_TAUS, NEW_TAUS = 4, 8
# 前の当てはめた書き手の数（ml-improve の four_tuple）と、今回パネルに入る書き手の数（tau-extend の P15・C5 の writers）
PREV_WRITERS = {"coauthor": 28, "cs1": 25}
NEW_WRITERS = {"coauthor": 17, "cs1": 23}
SAFETY = 1.5


def fit_units(ks, taus, folds):
    """Σ_k 当てはめの数 × 学習の単位の数（折り目の学習は k − 1・k − 2 単位）。"""
    tot = 0
    for k in ks:
        tot += taus * k
        if folds and k >= 3:
            tot += taus * ((k - 1) + (k - 2))
    return tot


def writer_ratio(ds):
    cfg = ml.DATASETS[ds]
    out = {}
    for pn, (nmin, ks) in cfg["panels"].items():
        grid = [k for k in cfg["grid"] if k <= max(ks)]
        out[pn] = fit_units(sorted({k for _, kk in cfg["panels"].values() for k in kk if k <= max(ks)}), NEW_TAUS, False) / \
            fit_units(grid, PREV_TAUS, True)
    return max(out.values()), out


def estep_seconds(rng, nsym):
    H.set_nsym(nsym)
    try:
        seqs = [rng.integers(0, nsym, 900) for _ in range(120)]
        _, h, T = H.r0_r1(seqs)
        D = H.Batched(seqs, chunk=H.CHUNK)
        per = {}
        for s in ml.STRUCTS:
            m = H.random_model(s[0], s[1], rng, r1=T, r0=h)
            best = None
            for _ in range(3):
                t0 = time.perf_counter()
                H.counts(m, D)
                dt = time.perf_counter() - t0
                best = dt if best is None else min(best, dt)
            per[ml.sname(s)] = best
        return per
    finally:
        H.set_nsym(26)


def main(seed, out):
    rng = np.random.default_rng([seed, 601])
    prev = json.load(open(PREV, encoding="utf-8"))
    est = {nsym: estep_seconds(rng, nsym) for nsym in (10, 26, 50)}
    r = {str(n): sum(est[n].values()) / sum(est[26].values()) for n in est}
    R = dict(estep_sec=est, ratio_by_nsym=r, groups={}, prev_seconds={})
    total = 0.0
    for ds in ("coauthor", "cs1"):
        ps = prev["datasets"][ds]["seconds"]
        R["prev_seconds"][ds] = dict(pools=ps["pools"], writers=ps["writers"])
        wr, wr_by = writer_ratio(ds)
        pr = NEW_WRITERS[ds] / PREV_WRITERS[ds]
        R.setdefault("writer_ratio", {})[ds] = wr_by
        R.setdefault("pool_ratio", {})[ds] = pr
        for q_, order in ml.GROUPS:
            n = q_ * q_ + 1
            sec = (ps["pools"] * pr + ps["writers"] * wr) * r[str(n)]
            R["groups"].setdefault(ml.gname(q_, order), {})[ds] = sec
            total += sec
    R["estimate_hours"] = total / 3600
    R["estimate_hours_upper"] = total * SAFETY / 3600
    R["safety"] = SAFETY
    json.dump(R, open(out, "w"), indent=1)
    print(json.dumps(dict(ratio_by_nsym={k: round(v, 3) for k, v in r.items()}, estimate_hours=round(R["estimate_hours"], 2),
                          estimate_hours_upper=round(R["estimate_hours_upper"], 2))))


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2])
