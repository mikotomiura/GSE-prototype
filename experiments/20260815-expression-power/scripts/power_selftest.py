#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自己検査 — 「単一の実装が正しい」と信じないための独立検算。

⚠️★★★ 本実験の主張は全部この 1 本の Python が出している。
  → ★ **既に実測されている数字を再現できること**と、**独立な 2 経路が一致すること**を検査にする。
  ★ 検査が赤なら results/ の数字を読まない。

検査:
  1  Mann-Whitney 厳密帰無の総和が C(n1+n2, n1) に一致する
  2  ★★★ G1 の実測（C(8,4)=70 / 実質 AUC≈1.0 / 帰無 95%点 AUC 0.81–0.94）を再現する
  3  解析式 ⇄ 並べ替えモンテカルロ が許容差内で一致する（results/power.json の記録を検査）
  4  ★ 到達不能の境界: 最小 p > α のとき、効果量を極端に大きくしても棄却しない
  5  帰無での偽陽性率が α を超えない（並べ替え検定の妥当性）
  6  ★ seed 固定で 2 回走らせて results が byte-equal
  7  ★ 決定的な部分（到達可能性 / AUC 帰無 / 解析式）は seed を変えても 1 文字も変わらない

⚠️ 標準ライブラリのみ。
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
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


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    results = os.path.join(ROOT, "results", "power.json")
    if not os.path.exists(results):
        print(f"results not found: {results} — run.sh を先に走らせる")
        return 2
    with open(results, encoding="utf-8") as fh:
        P = json.load(fh)

    print("検査 1: Mann-Whitney 厳密帰無の総和")
    for n1 in (2, 3, 4, 5, 6, 8):
        counts = pc.mann_whitney_counts(n1, n1)
        check(f"sum(counts) == C({2 * n1},{n1})", sum(counts) == comb(2 * n1, n1),
              f"{sum(counts)} vs {comb(2 * n1, n1)}")
        check(f"degree == {n1 * n1}", len(counts) - 1 == n1 * n1)
        check("対称である", counts == counts[::-1])

    print("検査 2: ★★★ G1 の実測の再現")
    s8 = pc.auc_null_summary(8, 0.05)
    check("C(8,4) = 70", s8["null_space"] == 70, str(s8["null_space"]))
    check("到達可能な最小 p = 1/70", abs(s8["min_p_one_sided"] - 1 / 70) < 1e-12,
          f"{s8['min_p_one_sided']:.6f}")
    check("p<0.05 に届く最小 AUC = 0.9375（★ 実質 AUC≈1.0）",
          abs(s8["smallest_auc_reaching_alpha"] - 0.9375) < 1e-12,
          str(s8["smallest_auc_reaching_alpha"]))
    check("帰無 95%点 AUC が G1 実測 0.812–0.938 の範囲",
          0.81 <= s8["null_auc_p95"] <= 0.94, str(s8["null_auc_p95"]))

    print("検査 3: 解析式 ⇄ モンテカルロ")
    checks = P.get("analytic_vs_monte_carlo", [])
    check("検算セルが 1 つ以上ある", len(checks) > 0, str(len(checks)))
    for r in checks:
        check(f"n={r['n']} B={r['blocks']} δ={r['delta']}", r["agree"],
              f"analytic={r['analytic']} mc={r['monte_carlo']} diff={r['abs_diff']}")

    print("検査 4: ★ 到達不能の境界（効果量を極端にしても棄却しない）")
    import random
    for b in (4, 6):
        pw = pc.permutation_power_individual(50.0, b, 0.05, random.Random(1), n_sims=100)
        check(f"B={b} は δ=50 でも棄却率 0", pw == 0.0, f"power={pw}")
    pw8 = pc.permutation_power_individual(50.0, 8, 0.05, random.Random(1), n_sims=100)
    check("B=8 は δ=50 で棄却率 1（★ 境界の反対側）", pw8 == 1.0, f"power={pw8}")

    print("検査 5: 帰無での偽陽性率（★ 厳密な理論値と照合する）")
    # 厳密検定の実際の第一種過誤は floor 側に丸まる: 到達可能な p は j/C なので
    # 棄却は j/C < alpha を満たす j の個数 / C になる。★ ここは名目 alpha ではない。
    n_sims_null = 3000
    for b in (8, 10):
        c = comb(b, b // 2)
        j_max = max(j for j in range(1, c + 1) if j / c < 0.05)
        exact = j_max / c
        fp = pc.permutation_power_individual(0.0, b, 0.05, random.Random(7), n_sims=n_sims_null)
        se = (exact * (1 - exact) / n_sims_null) ** 0.5
        check(f"B={b} 帰無棄却率が厳密値 {exact:.4f} と一致（3SE 以内）",
              abs(fp - exact) <= 3 * se, f"実測 {fp:.4f} / SE {se:.4f}")
        check(f"B={b} 厳密値は名目 α を超えない", exact <= 0.05, f"{exact:.4f}")
    fp_c = pc.permutation_power_cohort(0.0, 5, 8, 0.05, random.Random(11), n_sims=400, n_perms=400)
    check("コホート 帰無棄却率 <= 0.05 + 誤差", fp_c <= 0.09, f"{fp_c:.4f}")

    print("検査 6: ★ seed 固定で byte-equal（AC-6）")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "rerun.json")
        cmd = [sys.executable, os.path.join(HERE, "power_calc.py"),
               "--config", os.path.join(ROOT, "power.config.json"),
               "--seed", os.path.join(ROOT, "SEED"), "--out", out]
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        rc = subprocess.run(cmd, env=env, capture_output=True).returncode
        check("再実行が成功する", rc == 0, f"rc={rc}")
        if rc == 0:
            check("results/power.json と byte-equal", sha256(out) == sha256(results),
                  f"{sha256(out)[:16]} vs {sha256(results)[:16]}")

    print("検査 7: ★ 決定的な部分は seed に依存しない")
    with tempfile.TemporaryDirectory() as td:
        alt_seed = os.path.join(td, "SEED")
        with open(alt_seed, "w", encoding="utf-8") as fh:
            fh.write("SEED=99999999\n")
        out = os.path.join(td, "alt.json")
        cmd = [sys.executable, os.path.join(HERE, "power_calc.py"),
               "--config", os.path.join(ROOT, "power.config.json"),
               "--seed", alt_seed, "--out", out]
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        rc = subprocess.run(cmd, env=env, capture_output=True).returncode
        check("別 seed でも成功する", rc == 0, f"rc={rc}")
        if rc == 0:
            with open(out, encoding="utf-8") as fh:
                Q = json.load(fh)
            for key in ("reachability", "auc_null", "power_grid", "identification"):
                check(f"{key} は seed 非依存", P[key] == Q[key])
            check("individual_level_power は seed 依存（★ モンテカルロなので変わってよい）",
                  P["individual_level_power"] != Q["individual_level_power"])

    print()
    print(f"=== {OKS} ok / {len(FAILS)} fail ===")
    for f in FAILS:
        print(f"  - {f}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
