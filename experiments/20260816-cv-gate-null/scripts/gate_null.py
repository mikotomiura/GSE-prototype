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

⚠️★★★ **主判定は CV ではなく「低打鍵窓 `[1, 100)` の *数*」で行う**（`implied_low_window_count`）——
  ★ CV の比較はブートストラップ CI が広く、5 名中 2 名しか CI の外に出なかった。
  ★ 窓数は直接カウントなので判別力が高い（★ 実測は 4.7〜19.9 倍・code-reviewer HIGH-2 の提案）。

★ 判定:
  - 予測 ≈ 観測 → **H0 は棄却されない** ＝ 別集団は要らず、低下は打ち切りの算術効果
    → ⚠️ **「非打鍵ノイズが半分」は支持されない（撤回すべき）**
  - 観測 ≫ 予測 → **低打鍵側に余分な質量がある** ＝ notes の解釈が（その部分だけ）支持される

★ 併せて **分解**する: 1.0526 → 0.5019 のうち
  (i) ゼロ打鍵窓（`=0`）の除去 と (ii) 低打鍵窓（`1–99`）の除去 が、それぞれ何割を説明するか。
  ⚠️ (ii) は **打ち切りの算術効果と余分な低活動集団の除去が混ざっている**（解釈を名前に埋めない）。

⚠️★★★ プライバシー（`data-privacy` Skill / S5C-D8）:
  入力は repo 外の生 NDJSON。**出力は集計統計量のみ**。
  ★ セッション名・時刻・vk を 1 つも書き出さない。
  ⚠️★★★ `participant` だけはファイル名の先頭断片に由来する。★ **擬似 ID の形
  (`P` + 英数 3–13 桁) に一致した場合のみ残し、一致しない名前は `UNK-n` へ落とす**
  (★ 初版は断片をそのまま書き出しており、実名や端末名を含むファイルが 1 つ混じれば
  逐語でコミットされる状態だった・security-checker MEDIUM)。

⚠️ 独立実装での突き合わせ: MLE（scipy.optimize）と **打ち切りモーメント法**（`fit_truncated_moments`）の
  2 経路で (mu, sigma) を**別々に解く**（★ 2026-08-15 に解析式が系統的に外れた前例があるため）。
  ⚠️★★★ **実測では一致しない** —— 5 名全員でモーメント法の sigma が小さい。
  ★ 原因は既知（2 次モーメントは裾に敏感で、小標本 n=32–171 では sigma を過小推定する）で、
  ★ **向きは結論に対して保守側**（sigma が小さいほど H0 の期待窓数は減り、上の比は大きくなる）。
  → ★ **「2 経路が一致した」とは書かない**（`notes.md §5-5`）。
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
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


def truncated_moments(mu, sigma, lo):
    """左側打ち切り対数正規の 1 次・2 次モーメント（理論値）。"""
    a = (math.log(lo) - mu) / sigma
    den = stats.norm.sf(a)
    m1 = math.exp(mu + sigma ** 2 / 2) * stats.norm.sf(a - sigma) / den
    m2 = math.exp(2 * mu + 2 * sigma ** 2) * stats.norm.sf(a - 2 * sigma) / den
    return m1, m2


def fit_truncated_moments(x, lo, x0):
    """★ 独立経路 — モーメント法で (mu, sigma) を **MLE とは別に解く**。

    ⚠️★★★ 初版はここで「MLE が返した (mu,sigma) の理論平均と標本平均を比べる」だけの
    適合度チェックをしており、**独立な当てはめではなかったのに `env.md` は
    「2 経路で同じ (mu,sigma) に到達するか検算する」と書いていた**（★ code-reviewer HIGH）。
    → ★ 1 次・2 次モーメントの 2 式を実際に解いて突き合わせる形に直した。
    """
    a = np.asarray(x, dtype=float)
    t1, t2 = float(a.mean()), float((a ** 2).mean())

    def eqs(p):
        mu, log_sigma = p
        m1, m2 = truncated_moments(mu, math.exp(log_sigma), lo)
        return [m1 / t1 - 1.0, m2 / t2 - 1.0]

    r = optimize.root(eqs, x0=[x0[0], math.log(x0[1])], method="hybr")
    if not r.success:
        return None
    return float(r.x[0]), float(math.exp(r.x[1]))


def moment_check(x, lo, mu, sigma):
    """MLE の解を独立なモーメント法の解と突き合わせる（★ 実装ミスの検出）。"""
    m1, _ = truncated_moments(mu, sigma, lo)
    emp = float(np.mean(x))
    out = {"theoretical_mean": round(m1, 2), "empirical_mean": round(emp, 2),
           "mean_rel_error": round(abs(m1 - emp) / emp, 4) if emp else None}
    mm = fit_truncated_moments(x, lo, (mu, sigma))
    if mm is None:
        out["moment_fit"] = None
        out["agrees_with_mle"] = None
    else:
        out["moment_fit"] = {"mu": round(mm[0], 4), "sigma": round(mm[1], 4)}
        # ★ 閾値判定を付ける（★ 出しっぱなしで誰も見ない数字にしない・code-reviewer LOW）
        out["agrees_with_mle"] = bool(abs(mm[0] - mu) < 0.10 and abs(mm[1] - sigma) < 0.10)
    return out


def implied_low_window_count(mu, sigma, n_gated, lo):
    """★★★ H0 の下で `[1, lo)` に何窓あるはずかを外挿する（★ CV 比較より鋭い統計量）。

    ★ 当てた分布の下で `P(X >= lo)` が分かるので、観測された `n_gated` から
      非ゼロ窓の総数を逆算し、`[1, lo)` の期待窓数を出す。
    ⚠️ CV の比較は標本ゆらぎが大きく（ブートストラップ CI が広い）5 名中 2 名しか
      CI の外に出なかった。★ 窓数は直接カウントなので判別力が高い（code-reviewer HIGH-2 の提案）。
    """
    p_ge = float(stats.norm.sf((math.log(lo) - mu) / sigma))
    if p_ge <= 0:
        return None
    n_nonzero_implied = n_gated / p_ge
    p_low = float(stats.norm.sf((math.log(1.0) - mu) / sigma)) - p_ge
    return n_nonzero_implied * p_low


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


def decompose(cv_all, cv_ge1, cv_gate):
    """CV 低下（全窓 → ゲート後）を、除去した窓の種類で内訳にする。

    ⚠️★★★ 初版はここを `share_zero_atom` / `share_body_truncation` と呼び、後者を
    「打鍵している *本体* を切った **算術効果**」と断定していた。★ しかし同じ実験が
    「`1–99` の窓にも余分な質量がある」と結論しており、`≥1 → ≥100` の段は
    **算術効果と余分な低活動集団の除去が混ざっている**（★ code-reviewer HIGH）。
    → ★ ラベルを **操作的**（何を除いたか）に改め、解釈を名前に埋め込まない。

    ⚠️ share は **CV の差の比**であって分散分解ではない。記述的な内訳として読む。
    """
    if cv_all is None or cv_ge1 is None or cv_gate is None:
        return None
    total = cv_all - cv_gate
    if not total:
        return None
    return {
        "total_drop_all_to_gate": round(total, 4),
        "share_from_removing_zero_windows": round((cv_all - cv_ge1) / total, 4),
        "share_from_removing_low_windows_1_to_gate": round((cv_ge1 - cv_gate) / total, 4),
        "note": ("share は CV の差の比であり分散分解ではない。"
                 "後者は『打ち切りの算術効果』と『余分な低活動集団の除去』が混ざっている。"),
    }


def analyse(flat_dir: str, window_minutes: int, seed: int, boot: int):
    files = sorted(glob.glob(os.path.join(flat_dir, "**", "*.ndjson"), recursive=True))
    if not files:
        # ⚠️ パスを出さない —— 「リポジトリに絶対パスを書かない」と決めているのに、
        #   失敗時のログは notes / 引き継ぎに貼られやすい（security-checker LOW）。
        sys.stderr.write("GSE_PHASE1_NDJSON 配下に .ndjson が見つからない\n")
        return None
    by_pid: dict[str, list[str]] = {}
    unknown_seq = 0
    label_of: dict[str, str] = {}
    for p in files:
        base = os.path.basename(p)
        frag = base.split("_", 1)[0] if "_" in base else base
        # ⚠️★★★ ファイル名の先頭断片をそのまま出力に書かない（security-checker MEDIUM）。
        #   ★ 擬似 ID の形（P + 英数 3–13 桁）に一致しない名前は位置ラベルへ落とす。
        #   ★ そうしないと、実名や端末名を含むファイルが 1 つ混じった瞬間に
        #     検査を通らずコミット対象 JSON へ逐語で入る。
        if re.fullmatch(r"P[0-9A-Za-z]{3,13}", frag):
            pid = frag
        else:
            if frag not in label_of:
                unknown_seq += 1
                label_of[frag] = f"UNK-{unknown_seq}"
            pid = label_of[frag]
        by_pid.setdefault(pid, []).append(p)

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
        obs_low = int(((w >= 1) & (w < GATE)).sum())
        exp_low = implied_low_window_count(mu, sigma, gated.size, GATE)
        rows.append({
            "participant": pid,
            "windows": int(w.size),
            "windows_zero": int((w == 0).sum()),
            "windows_ge100": int(gated.size),
            "low_windows_1_to_gate": {
                "observed": obs_low,
                "expected_under_H0": (round(exp_low, 1) if exp_low is not None else None),
                "ratio": (round(obs_low / exp_low, 1)
                          if exp_low and exp_low > 0 else None),
            },
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

    obs_all = med("all", "observed_cv")
    obs_ge1 = med("ge1", "observed_cv")
    obs_g = med("ge100", "observed_cv")
    # ★ 対応のある差（★ 中央値どうしの差は別々の参加者の値を引き算しうる・code-reviewer MEDIUM）
    paired = [r["observed_cv"]["ge1"] - r["predicted_cv_under_H0"]["ge1"] for r in used
              if r["observed_cv"].get("ge1") is not None
              and r["predicted_cv_under_H0"].get("ge1") is not None]
    return {
        "schema": "cv-gate-null/v1",
        "note": ("集計統計量のみ。セッション名・時刻・vk を含まない。"
                 "participant は擬似 ID の形 (P+英数3-13桁) に一致した場合のみ残し、"
                 "一致しないファイル名は UNK-n の位置ラベルへ落とす。"),
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
        "decomposition": decompose(obs_all, obs_ge1, obs_g),
        "paired_obs_minus_pred_ge1": {
            "median": round(float(np.median(paired)), 4) if paired else None,
            "values": [round(v, 4) for v in paired],
            "n_positive": int(sum(v > 0 for v in paired)),
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
