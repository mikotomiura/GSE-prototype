#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自己検査 — ★ 主経路（gate_null.py の当てはめと外挿）を実際に守る検査。

⚠️★★★ なぜこの形か: 姉妹実験 `20260815-expression-power` の **EP-Q9** で
「**自己検査が主経路（`power_mc.py`）を 1 件も守っておらず、系統バイアスがあっても緑のままになる**」
という構造上の欠陥が指摘された。→ ★ 本検査は **真値が分かっている合成データ**を作り、
**H0 が真のときは通し、H0 が偽のときは落ちる**ことを両方確かめる。

検査:
  1. 打ち切り MLE が真の (mu, sigma) を回収する（★ 打ち切りを無視した素の当てはめは落ちることも示す）
  2. H0 が **真**（ゼロ点質量 ＋ 単一対数正規）なら、外挿予測 ≈ 観測 になる
  3. H0 が **偽**（低打鍵側に余分な集団を混ぜる）なら、観測 > 予測 になり検出できる
  4. 判定量（分解の share）が [0,1] に収まり合計 1 になる
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_null import (GATE, cv, fit_truncated_lognormal,  # noqa: E402
                       lognormal_cv_above, mixture_cv)

FAIL = []


def check(name, cond, detail=""):
    print(f"{'OK  ' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAIL.append(name)


def main() -> int:
    rng = np.random.default_rng(20260816)
    MU, SIGMA = math.log(300.0), 0.55       # 真値（実データの当てはめ帯域に合わせる）

    # --- 検査 1: 打ち切り MLE が真値を回収する ---
    x = rng.lognormal(MU, SIGMA, size=200_000)
    gated = x[x >= GATE]
    mu_hat, sigma_hat = fit_truncated_lognormal(gated, GATE)
    check("1a 打ち切り MLE が mu を回収", abs(mu_hat - MU) < 0.05,
          f"(true={MU:.3f} hat={mu_hat:.3f})")
    check("1b 打ち切り MLE が sigma を回収", abs(sigma_hat - SIGMA) < 0.03,
          f"(true={SIGMA:.3f} hat={sigma_hat:.3f})")
    # ★ 打ち切りを無視した素の当てはめは sigma を過小にする（＝ H0 に有利な誤り）を示す
    naive_sigma = float(np.std(np.log(gated), ddof=1))
    check("1c 打ち切り無視の素当てはめは sigma を過小にする", naive_sigma < SIGMA - 0.03,
          f"(naive={naive_sigma:.3f} < true={SIGMA:.3f}) ★ この補正をしないと結論が偏る")

    # --- 検査 2: H0 が真なら外挿が当たる ---
    p0 = 0.20
    n = 60_000
    body = rng.lognormal(MU, SIGMA, size=n)
    w = np.where(rng.random(n) < p0, 0.0, body)
    mu_h, sig_h = fit_truncated_lognormal(w[w >= GATE], GATE)
    pred_all = mixture_cv(mu_h, sig_h, float(np.mean(w == 0)))
    pred_ge1 = lognormal_cv_above(mu_h, sig_h, 1.0)
    obs_all, obs_ge1 = cv(w), cv(w[w >= 1])
    check("2a H0 真: 全窓 CV の予測が観測に一致", abs(pred_all - obs_all) < 0.05,
          f"(pred={pred_all:.4f} obs={obs_all:.4f})")
    check("2b H0 真: ge1 CV の予測が観測に一致", abs(pred_ge1 - obs_ge1) < 0.05,
          f"(pred={pred_ge1:.4f} obs={obs_ge1:.4f})")

    # --- 検査 3: H0 が偽（低打鍵側に余分な集団）なら検出できる ---
    #     ★ ここが「緑のままにならない」ことの担保。
    extra = rng.uniform(1, 60, size=int(n * 0.25))       # ゼロではないが極端に低い窓
    w2 = np.concatenate([w, extra])
    mu2, sig2 = fit_truncated_lognormal(w2[w2 >= GATE], GATE)
    pred2 = lognormal_cv_above(mu2, sig2, 1.0)
    obs2 = cv(w2[w2 >= 1])
    check("3 H0 偽: 観測 > 予測 になり余分な低活動集団を検出できる", obs2 - pred2 > 0.05,
          f"(obs={obs2:.4f} > pred={pred2:.4f}, 差={obs2 - pred2:.4f})")

    # --- 検査 4: 分解の share が定義どおり ---
    a, b, c = 1.0526, 0.7576, 0.5019      # 実測の中央値（all / ge1 / ge100）
    total = a - c
    s0, s1 = (a - b) / total, (b - c) / total
    check("4 分解の share が [0,1] で合計 1", 0 <= s0 <= 1 and 0 <= s1 <= 1
          and abs(s0 + s1 - 1) < 1e-9, f"(zero={s0:.4f} body={s1:.4f})")

    print()
    if FAIL:
        print(f"FAILED: {len(FAIL)} 件 -> {FAIL}")
        return 1
    print("すべて緑")
    return 0


if __name__ == "__main__":
    sys.exit(main())
