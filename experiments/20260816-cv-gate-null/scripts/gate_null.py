#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EP-Q8 の帰無比較 —— 「非打鍵ノイズが CV の半分」は打ち切りの算術効果と分けられるか。

★ 問い（`.steering/_handoff/next-session-prompt-survey-synthesis-and-design.md` §5 EP-Q8）:
  `experiments/20260815-expression-power/notes.md §4-1` は、G1 の適格性ゲート
  （窓あたり keydown >= 100）を当てると参加者内 CV 中央値が **1.053 → 0.502** に下がることから
  「**非打鍵ノイズが CV のおよそ半分を占めていた**」と解釈している。
  ⚠️ しかし **正の分布の下側を切れば、中身が何であれ CV は算術的に下がる**。
  ★ 実際スイープは閾値に対して単調（0→1.053 / 1→0.758 / 100→0.502 / 200→0.395）で、
  **純粋な打ち切り効果と見分けがつかない。**

★ 本スクリプトの帰無（H0）:
  **「打鍵している窓」は 1 つの同質な過程（対数正規）から来ており、
  ゼロ打鍵の窓だけが別の点質量（離席・非打鍵作業）である。**

★ H0 の下で、**ゲート上の窓だけ**（keydown >= 100・左側打ち切り）から対数正規を MLE で当て、
  そこから **外挿**して次を予測し、観測と突き合わせる:

  | 予測対象 | 観測 (中央値) | 意味 |
  |---|---|---|
  | keydown >= 200 の CV | 0.3952 | ★ **モデルの検証**（同じ本体をさらに切るだけ） |
  | keydown >= 1 の CV | 0.7576 | ★ **低打鍵側に余分な質量があるか** |
  | 全窓の CV | 1.0526 | ★ ゼロ点質量を観測比率で足して再現できるか |

★ 判定:
  - 予測 ≈ 観測 → **H0 は棄却されない** ＝ 別集団は要らず、低下は打ち切りの算術効果
    → ⚠️ **「非打鍵ノイズが半分」は支持されない（撤回すべき）**
  - 観測 ≫ 予測 → **低打鍵側に余分な質量がある** ＝ notes の解釈が支持される

★ 併せて **分解**する: 1.0526 → 0.5019 のうち
  (i) ゼロ点質量の除去 と (ii) 本体の打ち切り が、それぞれ何割を説明するか。

⚠️★★★ プライバシー（`data-privacy` Skill / S5C-D8）:
  入力は repo 外の生 NDJSON。**出力は集計統計量のみ**。
  ★ セッション名・ファイル名・時刻・vk を 1 つも書き出さない。

⚠️ 独立実装での突き合わせ: MLE（scipy.optimize）と **打ち切りモーメント法**（自前）の 2 経路で
  同じ (mu, sigma) に到達するかを検算する（★ 2026-08-15 に解析式が系統的に外れた前例があるため）。
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np
from scipy import optimize, stats

# ★ 窓抽出は既存実装を再利用する（切り方を再発明して差が出ると比較が成立しない）
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(
    _HERE, "..", "..", "20260815-expression-power", "scripts")))
from block_variance import window_counts, _input_manifest  # noqa: E402

GATE = 100          # G1 事前登録 §2.9 の適格性ゲート（凍結済み・事後に決めた値ではない）
VALIDATE_GATE = 200  # モデル検証用（同じ本体をさらに切るだけ）


def cv(xs) -> float:
    a = np.asarray(xs, dtype=float)
    m = a.mean()
    return float(a.std(ddof=1) / m) if m > 0 and a.size > 1 else float("nan")


def fit_truncated_lognormal(x, lo):
    """左側打ち切り lo の対数正規を MLE で当てる。

    尤度: sum log f(x) - n log(1 - F(lo))。★ 打ち切りを無視して素の対数正規を当てると
    sigma が系統的に過小になり、外挿が「余分な質量は無い」側へ偏る（＝ H0 に有利な誤り）。
    """
    lx = np.log(np.asarray(x, dtype=float))
    llo = math.log(lo)

    def nll(p):
        mu, log_sigma = p
        sigma = math.exp(log_sigma)
        z = (lx - mu) / sigma
        # log f(x) = -log(x) - log(sigma) - 0.5 log(2pi) - z^2/2 (log x 項は定数なので省く)
        ll = -lx.size * (log_sigma + 0.5 * math.log(2 * math.pi)) - 0.5 * np.sum(z * z)
        surv = stats.norm.sf((llo - mu) / sigma)
        if surv <= 1e-300:
            return 1e30
        return -(ll - lx.size * math.log(surv))

    best = None
    for mu0 in (lx.mean(), lx.mean() - 1.0, lx.mean() - 2.0):
        for ls0 in (math.log(max(lx.std(ddof=1), 1e-3)), math.log(1.0), math.log(2.0)):
            r = optimize.minimize(nll, x0=[mu0, ls0], method="Nelder-Mead",
                                  options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 4000})
            if best is None or r.fun < best.fun:
                best = r
    return float(best.x[0]), float(math.exp(best.x[1]))


def moment_check(x, lo, mu, sigma):
    """独立検算 — 当てた (mu, sigma) の打ち切り分布の理論平均と、標本平均を突き合わせる。

    ★ MLE の実装ミスは「それらしい値」を返しうるので、別経路のモーメントで殴る。
    """
    a = (math.log(lo) - mu) / sigma
    # E[X | X > lo] = exp(mu + sigma^2/2) * Phi(sigma - a) / Phi(-a)
    num = stats.norm.sf(a - sigma)
    den = stats.norm.sf(a)
    theo = math.exp(mu + sigma ** 2 / 2) * num / den if den > 0 else float("nan")
    emp = float(np.mean(x))
    return {"theoretical_mean": round(theo, 2), "empirical_mean": round(emp, 2),
            "rel_error": round(abs(theo - emp) / emp, 4) if emp else None}


def lognormal_cv_above(mu, sigma, lo):
    """対数正規を lo で左側打ち切りしたときの CV（lo=0 なら素の CV）。"""
    if lo <= 0:
        return math.sqrt(math.exp(sigma ** 2) - 1.0)
    a = (math.log(lo) - mu) / sigma
    den = stats.norm.sf(a)
    m1 = math.exp(mu + sigma ** 2 / 2) * stats.norm.sf(a - sigma) / den
    m2 = math.exp(2 * mu + 2 * sigma ** 2) * stats.norm.sf(a - 2 * sigma) / den
    var = m2 - m1 ** 2
    return math.sqrt(var) / m1 if m1 > 0 and var > 0 else float("nan")


def mixture_cv(mu, sigma, p_zero):
    """ゼロ点質量 p_zero ＋ 対数正規本体 の混合の CV。"""
    m1 = (1 - p_zero) * math.exp(mu + sigma ** 2 / 2)
    m2 = (1 - p_zero) * math.exp(2 * mu + 2 * sigma ** 2)
    var = m2 - m1 ** 2
    return math.sqrt(var) / m1 if m1 > 0 and var > 0 else float("nan")


def analyse(flat_dir: str, window_minutes: int, seed: int, boot: int):
    files = sorted(glob.glob(os.path.join(flat_dir, "**", "*.ndjson"), recursive=True))
    if not files:
        sys.stderr.write(f"no sessions under {flat_dir}\n")
        return None
    by_pid: dict[str, list[str]] = {}
    for p in files:
        base = os.path.basename(p)
        by_pid.setdefault(base.split("_", 1)[0] if "_" in base else "UNKNOWN", []).append(p)

    rng = np.random.default_rng(seed)
    rows = []
    for pid in sorted(by_pid):
        w = []
        for p in by_pid[pid]:
            w.extend(window_counts(p, window_minutes))
        w = np.asarray(w, dtype=float)
        if w.size < 3:
            continue
        gated = w[w >= GATE]
        if gated.size < 5:      # 打ち切り MLE が立たない参加者は外す（★ 除外数を出力する）
            rows.append({"participant": pid, "windows": int(w.size),
                         "excluded": "gated windows < 5"})
            continue
        mu, sigma = fit_truncated_lognormal(gated, GATE)

        pred = {
            "ge200": lognormal_cv_above(mu, sigma, VALIDATE_GATE),
            "ge1": lognormal_cv_above(mu, sigma, 1.0),
            "all": mixture_cv(mu, sigma, float(np.mean(w == 0))),
        }
        obs = {
            "ge200": cv(w[w >= 200]) if (w >= 200).sum() > 1 else float("nan"),
            "ge1": cv(w[w >= 1]) if (w >= 1).sum() > 1 else float("nan"),
            "all": cv(w),
            "ge100": cv(gated),
        }
        # ★ レビュア提案の帰無（EP-D15 (b)）: 「打鍵率と無関係にランダムで同数を落とす」。
        #   ⚠️ これは *標本サイズの減少* が CV を動かすかを見る検査であって、
        #   「低い窓が別集団か」は判定しない（無作為間引きは CV を期待値として保存する）。
        #   → ★ 主判定は上の打ち切り外挿。本項は代替説明の消去のために出す。
        n_drop = int(w.size - gated.size)
        rand_cvs = []
        for _ in range(200):
            keep = rng.permutation(w.size)[n_drop:]
            if keep.size > 1:
                rand_cvs.append(cv(w[keep]))
        random_removal_cv = round(float(np.median(rand_cvs)), 4) if rand_cvs else None

        # ブートストラップ（打ち切り標本の再抽出）で予測の不確実性を出す
        bs = []
        for _ in range(boot):
            s = rng.choice(gated, size=gated.size, replace=True)
            try:
                m2_, s2_ = fit_truncated_lognormal(s, GATE)
                bs.append(lognormal_cv_above(m2_, s2_, 1.0))
            except Exception:
                pass
        rows.append({
            "participant": pid,
            "windows": int(w.size),
            "windows_zero": int((w == 0).sum()),
            "windows_ge100": int(gated.size),
            "fit": {"mu": round(mu, 4), "sigma": round(sigma, 4),
                    "moment_check": moment_check(gated, GATE, mu, sigma)},
            "observed_cv": {k: (round(v, 4) if v == v else None) for k, v in obs.items()},
            "random_removal_null_cv": random_removal_cv,
            "predicted_cv_under_H0": {k: (round(v, 4) if v == v else None)
                                      for k, v in pred.items()},
            "predicted_ge1_boot_ci": ([round(float(np.percentile(bs, 2.5)), 4),
                                       round(float(np.percentile(bs, 97.5)), 4)] if bs else None),
        })

    used = [r for r in rows if "fit" in r]

    def med(key, kind):
        vals = [r[kind][key] for r in used if r[kind].get(key) is not None]
        return round(float(np.median(vals)), 4) if vals else None

    # 分解: 1.0526 -> 0.5019 のうち、ゼロ点質量の除去と本体の打ち切りの寄与
    obs_all = med("all", "observed_cv")
    obs_ge1 = med("ge1", "observed_cv")
    obs_g = med("ge100", "observed_cv")
    drop_total = (obs_all - obs_g) if (obs_all and obs_g) else None
    return {
        "schema": "cv-gate-null/v1",
        "note": "集計統計量のみ。★ ファイル名・セッション名・時刻・vk を含まない。",
        "window_minutes": window_minutes,
        "gate": GATE,
        "seed": seed,
        "bootstrap": boot,
        "input_manifest": _input_manifest(files),
        "participants_used": len(used),
        "participants_excluded": [r for r in rows if "fit" not in r],
        "median_observed_cv": {k: med(k, "observed_cv")
                               for k in ("all", "ge1", "ge100", "ge200")},
        "median_random_removal_null_cv": (
            round(float(np.median([r["random_removal_null_cv"] for r in used
                                   if r.get("random_removal_null_cv") is not None])), 4)
            if used else None),
        "median_predicted_cv_under_H0": {k: med(k, "predicted_cv_under_H0")
                                         for k in ("all", "ge1", "ge200")},
        "decomposition": {
            "total_drop_all_to_ge100": round(drop_total, 4) if drop_total else None,
            "share_zero_atom": (round((obs_all - obs_ge1) / drop_total, 4)
                                if drop_total else None),
            "share_body_truncation": (round((obs_ge1 - obs_g) / drop_total, 4)
                                      if drop_total else None),
        },
        "per_participant": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat-dir", required=True)
    ap.add_argument("--window-minutes", type=int, default=5)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = analyse(a.flat_dir, a.window_minutes, a.seed, a.bootstrap)
    if out is None:
        return 2
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("median_observed_cv", "median_predicted_cv_under_H0",
                       "decomposition", "participants_used")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
