#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自己検査 — ★ 主経路（`analyse` / `decompose` / 外挿）を実際に呼んで守る検査。

⚠️★★★ なぜこの形か:
1. 姉妹実験 `20260815-expression-power` の **EP-Q9**: 「**自己検査が主経路を 1 件も守っておらず、
   系統バイアスがあっても緑のままになる**」。
2. ⚠️★★★ **本実験の初版も同じ欠陥を持っていた**（2026-08-16・`code-reviewer` MEDIUM）——
   検査 4 は share の式を**ハードコードした 3 定数の上に再実装**しており、
   `s0+s1==1` は任意の a≠c で恒等的に成立するので **何も守っていなかった**。
   ★ 本版は `gate_null.decompose` を**実際に呼ぶ**。
3. ⚠️ 初版は窓数 60,000–200,000 で試験しており、**実データの 32–171 と桁が違った**。
   ★ 本版は **realistic-n（32–171）でのバイアス**を測る検査を常設する。

検査:
  1. 打ち切り MLE が真の (mu, sigma) を回収する／打ち切りを無視すると σ が過小になる
  2. H0 が **真**なら外挿予測 ≈ 観測（★ CV と **低打鍵窓数**の両方）
  3. H0 が **偽**（低打鍵側に余分な集団）なら検出できる（★ CV と窓数の両方）
  4. ★ **主経路 `decompose` を呼ぶ**（★ 再実装しない）
  5. ★ **realistic-n（実データと同じ 32–171 窓）での外挿バイアス**が許容内
  6. ★ **参加者ラベルの負検査** —— 擬似 ID の形でないファイル名が出力に現れない
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gate_null import (GATE, analyse, cv, decompose,  # noqa: E402
                       fit_truncated_lognormal, implied_low_window_count,
                       lognormal_cv_above, mixture_cv)

FAIL = []


def check(name, cond, detail=""):
    print(f"{'OK  ' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAIL.append(name)


def main() -> int:
    rng = np.random.default_rng(20260816)
    MU, SIGMA = math.log(300.0), 0.55       # 真値（実データの当てはめ帯域に合わせる）

    # --- 検査 1: 打ち切り MLE ---
    x = rng.lognormal(MU, SIGMA, size=200_000)
    gated = x[x >= GATE]
    mu_hat, sigma_hat = fit_truncated_lognormal(gated, GATE)
    check("1a 打ち切り MLE が mu を回収", abs(mu_hat - MU) < 0.05,
          f"(true={MU:.3f} hat={mu_hat:.3f})")
    check("1b 打ち切り MLE が sigma を回収", abs(sigma_hat - SIGMA) < 0.03,
          f"(true={SIGMA:.3f} hat={sigma_hat:.3f})")
    naive_sigma = float(np.std(np.log(gated), ddof=1))
    # ★ 余裕の無い定数比較にしない（初版は 0.003 しか余裕が無く、パラメータを少し
    #   動かすと無故障で赤くなった・code-reviewer LOW）。★ 主張は「向き」だけにする。
    check("1c 打ち切り無視の素当てはめは sigma を過小にする", naive_sigma < sigma_hat,
          f"(naive={naive_sigma:.3f} < mle={sigma_hat:.3f}) ★ 補正しないと結論が偏る")

    # --- 検査 2: H0 が真なら外挿が当たる ---
    p0, n = 0.20, 60_000
    body = rng.lognormal(MU, SIGMA, size=n)
    w = np.where(rng.random(n) < p0, 0.0, body)
    mu_h, sig_h = fit_truncated_lognormal(w[w >= GATE], GATE)
    check("2a H0 真: 全窓 CV の予測が観測に一致",
          abs(mixture_cv(mu_h, sig_h, float(np.mean(w == 0))) - cv(w)) < 0.05)
    check("2b H0 真: ge1 CV の予測が観測に一致",
          abs(lognormal_cv_above(mu_h, sig_h, 1.0) - cv(w[w >= 1])) < 0.05)
    obs_low = int(((w >= 1) & (w < GATE)).sum())
    exp_low = implied_low_window_count(mu_h, sig_h, int((w >= GATE).sum()), GATE)
    check("2c H0 真: 低打鍵窓数の予測が観測に一致", 0.6 < obs_low / exp_low < 1.6,
          f"(obs={obs_low} exp={exp_low:.1f} ratio={obs_low / exp_low:.2f})")

    # --- 検査 3: H0 が偽なら検出できる（★ 緑のままにならないことの担保） ---
    extra = rng.uniform(1, 60, size=int(n * 0.25))
    w2 = np.concatenate([w, extra])
    mu2, sig2 = fit_truncated_lognormal(w2[w2 >= GATE], GATE)
    check("3a H0 偽: CV で検出できる",
          cv(w2[w2 >= 1]) - lognormal_cv_above(mu2, sig2, 1.0) > 0.05)
    obs2 = int(((w2 >= 1) & (w2 < GATE)).sum())
    exp2 = implied_low_window_count(mu2, sig2, int((w2 >= GATE).sum()), GATE)
    check("3b H0 偽: 低打鍵窓数で検出できる（★ CV より鋭い）", obs2 / exp2 > 2.0,
          f"(obs={obs2} exp={exp2:.1f} ratio={obs2 / exp2:.1f} 倍)")

    # --- 検査 4: 主経路 decompose を呼ぶ ---
    d = decompose(1.0, 0.8, 0.5)
    ok = (d is not None
          and abs(d["total_drop_all_to_gate"] - 0.5) < 1e-9
          and abs(d["share_from_removing_zero_windows"] - 0.4) < 1e-9
          and abs(d["share_from_removing_low_windows_1_to_gate"] - 0.6) < 1e-9)
    check("4 主経路 decompose が既知の入力で正しい内訳を返す", ok, f"({d})")
    check("4b decompose は退化入力で None を返す", decompose(0.5, 0.5, 0.5) is None)

    # --- 検査 5: realistic-n（実データと同じ 32–171 窓）での外挿バイアス ---
    worst = 0.0
    for n_gated in (32, 74, 171):
        biases = []
        for _ in range(200):
            s = rng.lognormal(MU, SIGMA, size=int(n_gated / 0.75))
            s = s[s >= GATE][:n_gated]
            if s.size < n_gated:
                continue
            m_, sg_ = fit_truncated_lognormal(s, GATE)
            biases.append(lognormal_cv_above(m_, sg_, 1.0)
                          - lognormal_cv_above(MU, SIGMA, 1.0))
        b = float(np.median(biases))
        worst = max(worst, abs(b))
        print(f"     n_gated={n_gated:3d} -> 外挿 CV バイアス中央値 {b:+.4f}")
    check("5 realistic-n での外挿バイアスが許容内", worst < 0.10, f"(最大 |bias|={worst:.4f})")

    # --- 検査 6: 参加者ラベルの負検査（★ ファイル名が出力に漏れない） ---
    with tempfile.TemporaryDirectory() as td:
        bad = "realname-terminal_gse_20260101_000000.ndjson"
        # ★ 40 分ぶん（5 分窓 × 8・各 200 打）＝ 参加者として実際に集計される長さにする。
        #   ⚠️ 短いと窓が 1 つも作れず参加者ごと落ちて、検査が**空振りで緑**になる。
        with open(os.path.join(td, bad), "w", encoding="utf-8") as fh:
            fh.write('{"type":"meta","session_start":0}\n')
            for i in range(1600):
                fh.write('{"type":"key","press":true,"t":%d}\n' % (i * 1500))
        out = analyse(td, 5, 20260816, 5)
        labels = [r["participant"] for r in (out or {}).get("per_participant", [])]
        blob = json.dumps(out, ensure_ascii=False)
        check("6a 参加者として実際に集計されている（★ 空振り防止）", len(labels) == 1,
              f"(labels={labels})")
        check("6b 擬似 ID の形でないファイル名が出力に現れない",
              "realname" not in blob and "terminal" not in blob and labels == ["UNK-1"],
              f"(labels={labels})")

    print()
    if FAIL:
        print(f"FAILED: {len(FAIL)} 件 -> {FAIL}")
        return 1
    print("すべて緑")
    return 0


if __name__ == "__main__":
    sys.exit(main())
