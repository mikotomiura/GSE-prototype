#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""検出力の主経路 —— 並べ替え検定を**そのまま模擬**して δ80 を出す（numpy）。

⚠️★★★ なぜ解析式ではだめか（★ oracle_check.py の O5 が捕まえた）:
  ★ 並べ替え検定の帰無分布は **観測データに条件付き**である。
  ⚠️ H1 のもとでは処置が観測分散を膨らませる（B ブロック中 B/2 が δ ずれる）ので、
     **帰無分布そのものが広がり、検出力が下がる。**
  ★ 膨張率 = sqrt(1 + B·δ² / (4(B−1)σ²))。δ=1.0・B=8 で **1.134 倍**。
  → ⚠️★★★ **σ 既知の正規近似は検出力を過大評価する**（実測: n=3・B=8・δ=1.0 で +0.061）。
  → ★ **したがって δ80 はモンテカルロで解く。解析式は「楽観側の下界」として併記する。**

★ 共通乱数（同じ seed）を使うので power(δ) が δ について単調になり、二分法が安定する。
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from math import comb, sqrt

import numpy as np

MAX_CELLS = 2 * 10 ** 7  # 1 バッチのメモリ上限（float64 で約 160 MB）


def _mask_matrix(blocks: int, half: int, cap: int, rng: np.random.Generator):
    """割付マスク (P, blocks)。★ 全数列挙できるならそれを使う（乱択誤差ゼロ）。"""
    total = comb(blocks, half)
    if total <= cap:
        rows = list(combinations(range(blocks), half))
        M = np.zeros((len(rows), blocks))
        for i, r in enumerate(rows):
            M[i, list(r)] = 1.0
        return M, True
    M = np.zeros((cap, blocks))
    for i in range(cap):
        M[i, rng.choice(blocks, half, replace=False)] = 1.0
    return M, False


def permutation_power(delta: float, n: int, blocks: int, alpha: float, *, seed: int,
                      sims: int = 2500, perms: int = 1200, two_sided: bool = True,
                      arm_blocks: int | None = None) -> float:
    """コホート並べ替え検定の検出力。

    arm_blocks=None  → 束ねる / factorial 系（B ブロックを半々に割る）
    arm_blocks=m     → dismantling（1 比較が 2m ブロックしか使わない）
    """
    rng = np.random.default_rng(seed)
    b = blocks if arm_blocks is None else 2 * arm_blocks
    half = b // 2
    M, _ = _mask_matrix(b, half, perms, rng)
    P = M.shape[0]

    rejects = 0
    done = 0
    batch = max(1, min(sims, int(MAX_CELLS / max(1, n * P))))
    while done < sims:
        s = min(batch, sims - done)
        done += s
        true_mask = np.zeros((s, n, b))
        for i in range(s):
            for j in range(n):
                true_mask[i, j, rng.choice(b, half, replace=False)] = 1.0
        data = rng.standard_normal((s, n, b)) + delta * true_mask
        totals = data.sum(axis=2)
        obs = ((2.0 * (data * true_mask).sum(axis=2) - totals) / half).mean(axis=1)
        perm_stat = (2.0 * np.einsum("ijb,pb->ijp", data, M) - totals[:, :, None]) / half
        idx = rng.integers(0, P, size=(s, n, perms))
        picked = np.take_along_axis(perm_stat, idx, axis=2).mean(axis=1)
        if two_sided:
            ge = (np.abs(picked) >= np.abs(obs)[:, None] - 1e-12).sum(axis=1)
        else:
            ge = (picked >= obs[:, None] - 1e-12).sum(axis=1)
        rejects += int((((ge + 1) / (perms + 1)) < alpha).sum())
    return rejects / sims


def delta_for_power(target: float, n: int, blocks: int, alpha: float, *, seed: int,
                    sims: int, perms: int, arm_blocks: int | None = None,
                    lo: float = 0.02, hi: float = 6.0, iters: int = 14):
    """二分法で δ80 を解く。★ 共通乱数なので power(δ) は単調。"""
    def f(d):
        return permutation_power(d, n, blocks, alpha, seed=seed, sims=sims, perms=perms,
                                 arm_blocks=arm_blocks)

    if f(hi) < target:
        return None, f(hi)
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0, target


def analytic_delta(target: float, n: int, blocks: int, alpha: float, se_mult: float = 1.0) -> float:
    """σ 既知の正規近似（★ 楽観側の下界として併記する）。"""
    from statistics import NormalDist

    nd = NormalDist()
    se = se_mult * 2.0 / sqrt(n * blocks)
    return (nd.inv_cdf(1 - alpha / 2) + nd.inv_cdf(target)) * se


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)
    with open(args.seed, encoding="utf-8") as fh:
        seed = int(next(l for l in fh if l.strip() and not l.startswith("#")).split("=")[-1].strip())

    mc = cfg["monte_carlo_primary"]
    sims, perms = mc["sims"], mc["perms"]
    target = cfg["target_power"]
    alpha = cfg["alpha"]

    rows = []
    for k in mc["k_values"]:
        a_eff = alpha / k
        for n, b in mc["cells"]:
            d80, _ = delta_for_power(target, n, b, a_eff, seed=seed + 31 * n + 7 * b + k,
                                     sims=sims, perms=perms)
            an = analytic_delta(target, n, b, a_eff)
            rows.append({
                "family": "halves",  # 束ねる / factorial 系（B/2 vs B/2）
                "n_tests": k,
                "alpha_effective": a_eff,
                "n": n, "blocks": b,
                "delta80_mc": None if d80 is None else round(d80, 3),
                "delta80_analytic": round(an, 3),
                "analytic_optimism": None if d80 is None else round(d80 - an, 3),
                "analytic_optimism_pct": None if d80 is None else round(100 * (d80 - an) / an, 1),
            })

    dis = []
    for k, b, n in mc["dismantling_cells"]:
        if b % (k + 1) != 0:
            continue
        m = b // (k + 1)
        a_eff = alpha / k
        d80, _ = delta_for_power(target, n, b, a_eff, seed=seed + 101 * n + 11 * b + k,
                                 sims=sims, perms=perms, arm_blocks=m)
        dis.append({
            "family": "dismantling",
            "k": k, "n": n, "blocks": b,
            "blocks_per_condition": m,
            "n_tests": k,
            "alpha_effective": a_eff,
            "delta80_mc": None if d80 is None else round(d80, 3),
        })

    # 帰無較正（★ δ=0 で棄却率が α を超えないこと）
    null_rows = []
    for n, b in mc["null_cells"]:
        r = permutation_power(0.0, n, b, alpha, seed=seed + 997, sims=mc["null_sims"], perms=perms)
        null_rows.append({"n": n, "blocks": b, "alpha": alpha, "rejection_rate": round(r, 4),
                          "ok": r <= alpha + 3 * sqrt(alpha * (1 - alpha) / mc["null_sims"])})

    out = {
        "schema": "expression-power-mc/v1",
        "seed": seed,
        "sims": sims, "perms": perms, "target_power": target, "alpha": alpha,
        "note": "並べ替え検定をそのまま模擬した δ80。解析式は楽観側の下界として併記。",
        "halves": rows,
        "dismantling": dis,
        "null_calibration": null_rows,
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
