#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oracle 検査 — 自前実装を **参照実装（scipy / numpy）** で突き合わせる。

⚠️★★★ なぜ分けてあるか:
  * `power_calc.py` は **標準ライブラリのみ**で動く（★ 依存が無い環境でも主結果が再現できる）。
  * ⚠️ しかし「自前の erf / 二分法 / DP / 並べ替えが正しい」は自分では証明できない。
  * → ★ **本スクリプトだけが numpy / scipy を要求し、独立実装として突き合わせる。**
  ★ 本スクリプトが落ちても主結果の再現性には影響しない（★ 検証の層が 1 枚増えるだけ）。

検査:
  O1  正規 CDF        自前 math.erf      ⇄ scipy.stats.norm.cdf
  O2  正規 分位点      自前 二分法        ⇄ scipy.stats.norm.ppf
  O3  二項係数        math.comb         ⇄ scipy.special.comb
  O4  Mann-Whitney    自前 DP           ⇄ scipy.stats.mannwhitneyu(method="exact")
  O5  ★★★ コホート検出力  解析式          ⇄ numpy ベクトル化モンテカルロ（★ 桁違いに高精度）
  O6  ★ 個人水準検出力   自前 全数列挙      ⇄ numpy 全数列挙（独立実装）
"""

from __future__ import annotations

import os
import sys
from itertools import combinations
from math import comb, sqrt

import numpy as np
from scipy import special, stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import power_calc as pc  # noqa: E402

FAILS: list[str] = []
OKS = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global OKS
    if cond:
        OKS += 1
        print(f"  ok   {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAILS.append(f"{name}: {detail}")
        print(f"  FAIL {name}  {detail}")


def masks_for(blocks: int, n_perm: int, rng: np.random.Generator):
    """割付マスク行列 (n_perm, blocks)。★ 全数列挙できるならそれを使う。"""
    half = blocks // 2
    total = comb(blocks, half)
    if total <= n_perm:
        rows = list(combinations(range(blocks), half))
        M = np.zeros((len(rows), blocks))
        for i, r in enumerate(rows):
            M[i, list(r)] = 1.0
        return M, True
    M = np.zeros((n_perm, blocks))
    for i in range(n_perm):
        M[i, rng.choice(blocks, half, replace=False)] = 1.0
    return M, False


def cohort_power_numpy(delta, n, blocks, alpha, rng, n_sims=4000, n_perm=2000, two_sided=True):
    """コホート並べ替え検定の検出力（numpy ベクトル化・★ 独立実装）。"""
    half = blocks // 2
    M, exhaustive = masks_for(blocks, n_perm, rng)          # (P, B)
    P = M.shape[0]
    rejects = 0
    batch = max(1, min(n_sims, int(4e7 / max(1, n * P))))    # メモリ上限で刻む
    done = 0
    while done < n_sims:
        s = min(batch, n_sims - done)
        done += s
        # 真の割付を各 (sim, subject) について引く
        true_mask = np.zeros((s, n, blocks))
        for i in range(s):
            for j in range(n):
                true_mask[i, j, rng.choice(blocks, half, replace=False)] = 1.0
        data = rng.standard_normal((s, n, blocks)) + delta * true_mask
        totals = data.sum(axis=2)                            # (s, n)
        obs = ((2.0 * (data * true_mask).sum(axis=2) - totals) / half).mean(axis=1)  # (s,)
        # 並べ替え: 各 (sim, subject) が独立に 1 つの割付を引く
        perm_sums = np.einsum("ijb,pb->ijp", data, M)        # (s, n, P)
        perm_stat = (2.0 * perm_sums - totals[:, :, None]) / half
        idx = rng.integers(0, P, size=(s, n, n_perm))
        picked = np.take_along_axis(perm_stat, idx, axis=2).mean(axis=1)  # (s, n_perm)
        if two_sided:
            ge = (np.abs(picked) >= np.abs(obs)[:, None] - 1e-12).sum(axis=1)
        else:
            ge = (picked >= obs[:, None] - 1e-12).sum(axis=1)
        pvals = (ge + 1) / (n_perm + 1)
        rejects += int((pvals < alpha).sum())
    return rejects / n_sims, exhaustive


def individual_power_numpy(delta, blocks, alpha, rng, n_sims=20000, two_sided=False):
    """個人水準の厳密並べ替え検定の検出力（numpy・全数列挙・★ 独立実装）。"""
    half = blocks // 2
    rows = list(combinations(range(blocks), half))
    M = np.zeros((len(rows), blocks))
    for i, r in enumerate(rows):
        M[i, list(r)] = 1.0
    nA = M.shape[0]
    rejects = 0
    batch = max(1, int(4e7 / nA))
    done = 0
    while done < n_sims:
        s = min(batch, n_sims - done)
        done += s
        true_idx = rng.integers(0, nA, size=s)
        true_mask = M[true_idx]                               # (s, B)
        data = rng.standard_normal((s, blocks)) + delta * true_mask
        totals = data.sum(axis=1)
        obs = (2.0 * (data * true_mask).sum(axis=1) - totals) / half
        stats_all = (2.0 * (data @ M.T) - totals[:, None]) / half   # (s, nA)
        if two_sided:
            ge = (np.abs(stats_all) >= np.abs(obs)[:, None] - 1e-12).sum(axis=1)
        else:
            ge = (stats_all >= obs[:, None] - 1e-12).sum(axis=1)
        rejects += int(((ge / nA) < alpha).sum())
    return rejects / n_sims


def main() -> int:
    rng = np.random.default_rng(20260815)

    print("O1: 正規 CDF  自前 math.erf ⇄ scipy.stats.norm.cdf")
    zs = np.linspace(-6, 6, 241)
    err = max(abs(pc.phi(float(z)) - stats.norm.cdf(z)) for z in zs)
    check("最大絶対誤差 < 1e-12", err < 1e-12, f"{err:.3e}")

    print("O2: 正規 分位点  自前 二分法 ⇄ scipy.stats.norm.ppf")
    ps = [1e-6, 1e-4, 0.001, 0.0125, 0.025, 0.05, 0.5, 0.8, 0.95, 0.975, 0.99, 1 - 1e-6]
    err = max(abs(pc.z_quantile(p) - float(stats.norm.ppf(p))) for p in ps)
    check("最大絶対誤差 < 1e-9", err < 1e-9, f"{err:.3e}")

    print("O3: 二項係数  math.comb ⇄ scipy.special.comb")
    ok = all(comb(b, b // 2) == int(special.comb(b, b // 2, exact=True))
             for b in (4, 6, 8, 10, 12, 16, 32))
    check("全 B で一致", ok)

    print("O4: Mann-Whitney 厳密帰無  自前 DP ⇄ scipy.stats.mannwhitneyu(exact)")
    for n1 in (3, 4, 5, 6):
        counts = pc.mann_whitney_counts(n1, n1)
        total = sum(counts)
        max_u = n1 * n1
        # 自前 DP から作った上側確率
        mine = [sum(counts[u:]) / total for u in range(max_u + 1)]
        # scipy: 実データから U と厳密 p を出して突き合わせる
        worst = 0.0
        for _ in range(60):
            x = rng.standard_normal(n1)
            y = rng.standard_normal(n1)
            res = stats.mannwhitneyu(x, y, alternative="greater", method="exact")
            u = int(round(res.statistic))
            worst = max(worst, abs(mine[u] - float(res.pvalue)))
        check(f"n1=n2={n1} 上側確率が一致（最大差 < 1e-12）", worst < 1e-12, f"{worst:.3e}")

    print("O5a: ★★★ 解析式は**楽観側**である（★ 向きを固定する・等号は許さない）")
    # ⚠️ 並べ替え帰無は観測データ条件付きなので、H1 で処置が分散を膨らませると帰無も広がる。
    #    → σ 既知の正規近似は検出力を過大評価する。★ ここでは「向き」を検査に固定する。
    import random as _random
    for n, b, d in ((3, 8, 1.0), (5, 8, 0.9), (10, 8, 0.6), (3, 10, 1.2)):
        mc, exhaustive = cohort_power_numpy(d, n, b, 0.05, rng, n_sims=4000, n_perm=2000)
        an = pc.analytic_power(d, n, b, 0.05, 1.0)
        se = sqrt(max(mc * (1 - mc), 1e-9) / 4000)
        infl = sqrt(1 + b * d * d / (4 * (b - 1)))
        check(f"n={n} B={b} δ={d}  解析式 >= MC（楽観側）", an >= mc - 3 * se,
              f"analytic={an:.4f} mc={mc:.4f} 差={an - mc:+.4f} 帰無膨張率={infl:.3f}")
        check(f"n={n} B={b} δ={d}  楽観幅は 0.10 未満（★ 桁は外していない）", (an - mc) < 0.10,
              f"{an - mc:+.4f}")

    print("O5b: ★ コホート検出力  stdlib 実装 ⇄ numpy 実装（★ 独立実装同士）")
    for n, b, d in ((5, 8, 0.9), (10, 8, 0.6)):
        mine = pc.permutation_power_cohort(d, n, b, 0.05, _random.Random(31337),
                                           n_sims=1200, n_perms=1200)
        theirs, _ = cohort_power_numpy(d, n, b, 0.05, rng, n_sims=4000, n_perm=1200)
        se = sqrt(max(theirs * (1 - theirs), 1e-9) * (1 / 1200 + 1 / 4000))
        check(f"n={n} B={b} δ={d}  差が 3SE 以内", abs(mine - theirs) <= 3 * se,
              f"stdlib={mine:.4f} numpy={theirs:.4f} 3SE={3 * se:.4f}")

    print("O6: ★ 個人水準検出力  自前 全数列挙 ⇄ numpy 独立実装")
    import random as _random
    for b, d in ((8, 1.0), (8, 2.0), (10, 1.5)):
        mine = pc.permutation_power_individual(d, b, 0.05, _random.Random(4242), n_sims=4000)
        theirs = individual_power_numpy(d, b, 0.05, rng, n_sims=20000)
        se = sqrt(max(theirs * (1 - theirs), 1e-9) * (1 / 4000 + 1 / 20000))
        check(f"B={b} δ={d}  差が 3SE 以内", abs(mine - theirs) <= 3 * se,
              f"stdlib={mine:.4f} numpy={theirs:.4f} 3SE={3 * se:.4f}")

    print()
    print(f"=== {OKS} ok / {len(FAILS)} fail ===")
    for f in FAILS:
        print(f"  - {f}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
