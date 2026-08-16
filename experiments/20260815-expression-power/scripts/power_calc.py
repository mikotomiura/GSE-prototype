#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表現層の検出力計算 — PS-Q1「第 1 版を 1 要素に絞るか」を数字にする。

出所:
  .steering/20260815-public-space-and-media-art/decisions.md  PS-D3 / PS-D9
  .steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md  §5 / §6 / §8
  .steering/20260802-g1-execution-prep/decisions.md  判断 E-2（帰無 95%点 AUC ≈ 0.94）

方針（.steering/20260815-expression-power-calculation/design.md）:
  * 骨格は G1 型（被験者内・ブロック無作為化・厳密並べ替え検定）。研究者判断 2026-08-15。
  * 判定水準を 2 つに分ける（個人水準 / コホート水準）。★ ここが計算の芯。
  * 要素数 k の扱いを 4 つに分ける（束ねる / 完全 factorial / 一部実施 / dismantling）。
  * 検出力は「解析式」と「並べ替えモンテカルロ」の 2 経路で出し、一致を検査にする。

⚠️ 標準ライブラリのみ（numpy / scipy は本機に無い。env.md に実測を記録）。
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from math import comb, erf, sqrt

# ---------------------------------------------------------------------------
# 正規分布（scipy が無いので自前）
# ---------------------------------------------------------------------------


def phi(z: float) -> float:
    """標準正規の累積分布関数。"""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


def z_quantile(p: float) -> float:
    """標準正規の分位点。二分法（stdlib のみ・十分な精度）。"""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0,1)")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# (A) 到達可能性 — ★ 効果量を 1 つも仮定せずに言える部分
# ---------------------------------------------------------------------------


def attainable_min_p(design_space_size: int, two_sided: bool) -> float:
    """帰無分布の大きさから決まる、到達可能な最小 p。

    連続な統計量（同値なし）を仮定する。同値があると実際はこれより大きくなる
    （G1 の実測: C(8,4)=70 で 2/70〜4/70 だった。★ 本値はその下限である）。
    """
    base = 1.0 / design_space_size
    return min(1.0, 2.0 * base) if two_sided else base


def reachability_table(blocks, participants, k_values, alpha):
    """判定水準ごとに「α に届きうるか」を返す（★ 効果量非依存）。"""
    rows = []
    for b in blocks:
        space = comb(b, b // 2)
        for k in k_values:
            a_eff = alpha / k
            rows.append(
                {
                    "level": "individual",
                    "blocks": b,
                    "participants": None,
                    "k": k,
                    "null_space": space,
                    "alpha_effective": a_eff,
                    "min_p_one_sided": attainable_min_p(space, False),
                    "min_p_two_sided": attainable_min_p(space, True),
                    "reachable_one_sided": attainable_min_p(space, False) <= a_eff,
                    "reachable_two_sided": attainable_min_p(space, True) <= a_eff,
                }
            )
    for n in participants:
        for k in k_values:
            a_eff = alpha / k
            space = 2 ** n
            rows.append(
                {
                    "level": "sign_test",
                    "blocks": None,
                    "participants": n,
                    "k": k,
                    "null_space": space,
                    "alpha_effective": a_eff,
                    "min_p_one_sided": attainable_min_p(space, False),
                    "min_p_two_sided": attainable_min_p(space, True),
                    "reachable_one_sided": attainable_min_p(space, False) <= a_eff,
                    "reachable_two_sided": attainable_min_p(space, True) <= a_eff,
                }
            )
    for b in blocks:
        for n in participants:
            for k in k_values:
                a_eff = alpha / k
                # 各参加者を独立に並べ替える → 帰無空間は積になる
                space = comb(b, b // 2) ** n
                rows.append(
                    {
                        "level": "cohort",
                        "blocks": b,
                        "participants": n,
                        "k": k,
                        "null_space": space,
                        "alpha_effective": a_eff,
                        "min_p_one_sided": attainable_min_p(space, False),
                        "min_p_two_sided": attainable_min_p(space, True),
                        "reachable_one_sided": attainable_min_p(space, False) <= a_eff,
                        "reachable_two_sided": attainable_min_p(space, True) <= a_eff,
                    }
                )
    return rows


# ---------------------------------------------------------------------------
# (B) Mann-Whitney 厳密帰無 — ★「実質 AUC≈1.0」がどこから来るのかを第一原理で出す
# ---------------------------------------------------------------------------


def mann_whitney_counts(n1: int, n2: int):
    """U = 0..n1*n2 のそれぞれを与える割付の数（合計 = C(n1+n2, n1)）。

    漸化式 C(m,n,u) = C(m-1,n,u-n) + C(m,n-1,u)。
    """
    # dp[m][n] は長さ m*n+1 のリスト
    dp = [[None] * (n2 + 1) for _ in range(n1 + 1)]
    for m in range(n1 + 1):
        for n in range(n2 + 1):
            if m == 0 or n == 0:
                dp[m][n] = [1]
                continue
            size = m * n + 1
            cur = [0] * size
            left = dp[m - 1][n]  # U を n だけずらす
            for u, c in enumerate(left):
                cur[u + n] += c
            down = dp[m][n - 1]
            for u, c in enumerate(down):
                cur[u] += c
            dp[m][n] = cur
    return dp[n1][n2]


def auc_null_summary(blocks: int, alpha: float):
    """B ブロックを半々に割った時、順位統計量（AUC）の厳密帰無から:
    * p<alpha に到達できる最小の AUC
    * 帰無分布の 95 パーセンタイル AUC
    を返す。★ G1 の「実質 AUC≈1.0 が要る」を第一原理で再現する部分。
    """
    n1 = n2 = blocks // 2
    counts = mann_whitney_counts(n1, n2)
    total = sum(counts)
    max_u = n1 * n2
    # 上側確率 P(U >= u)
    upper = [0] * (max_u + 2)
    acc = 0
    for u in range(max_u, -1, -1):
        acc += counts[u]
        upper[u] = acc
    smallest_sig_auc = None
    for u in range(0, max_u + 1):
        if upper[u] / total <= alpha:
            smallest_sig_auc = u / max_u
            break
    # 95 パーセンタイル: P(U >= u) <= 0.05 となる最小 u の 1 つ下（= 帰無で 95% が収まる上端）
    p95_u = 0
    for u in range(0, max_u + 1):
        if upper[u] / total > 0.05:
            p95_u = u
    return {
        "blocks": blocks,
        "n_per_arm": n1,
        "null_space": total,
        "max_u": max_u,
        "min_p_one_sided": upper[max_u] / total,
        "smallest_auc_reaching_alpha": smallest_sig_auc,
        "null_auc_p95": p95_u / max_u,
        "alpha": alpha,
    }


# ---------------------------------------------------------------------------
# (C) 要素数 k の 4 つの扱い
# ---------------------------------------------------------------------------

DESIGNS = ("bundle", "factorial_full", "factorial_fractional", "dismantling")


def design_properties(design: str, k: int, blocks: int):
    """設計 × 要素数 → (必要ブロック数, SE 倍率, 検定本数, 識別可能か)。

    ★ [V81] 逐語「factorial では各主効果を標本全体で推定できる」:
      factorial 系は SE 倍率 1.0（= 1 要素設計と同じ）。代価は必要ブロック数と多重補正。
    ⚠️ dismantling（[P110] が集めた設計）だけが SE を悪化させる。
    """
    if design == "bundle":
        return {"blocks_required": 2, "se_multiplier": 1.0, "n_tests": 1, "identifies": False}
    if design == "factorial_full":
        return {"blocks_required": 2 ** k, "se_multiplier": 1.0, "n_tests": k, "identifies": True}
    if design == "factorial_fractional":
        # 分解能 IV を保てる最小の一部実施（k<=4 なら 8、k<=8 なら 16、k<=12 なら 32）
        if k <= 2:
            req = 2 ** k
        elif k <= 4:
            req = 8
        elif k <= 8:
            req = 16
        else:
            req = 32
        return {"blocks_required": req, "se_multiplier": 1.0, "n_tests": k, "identifies": True}
    if design == "dismantling":
        # k+1 条件（full / full-j）。各比較は 2B/(k+1) ブロックしか使わない。
        return {
            "blocks_required": k + 1,
            "se_multiplier": sqrt((k + 1) / 2.0),
            "n_tests": k,
            "identifies": True,
        }
    raise ValueError(design)


# ---------------------------------------------------------------------------
# (D) 検出力 — 解析式（正規近似）
# ---------------------------------------------------------------------------


def cohort_se(n: int, blocks: int, se_multiplier: float) -> float:
    """コホート統計量（参加者内 ON-OFF 差の平均）の標準誤差。σ=1 単位。

    参加者 i の差 d_i の分散 = 1/(B/2) + 1/(B/2) = 4/B。
    n 人平均 → 4/(nB)。SE = 2/sqrt(nB)。dismantling はこれを se_multiplier 倍する。
    """
    return se_multiplier * 2.0 / sqrt(n * blocks)


def analytic_power(delta: float, n: int, blocks: int, alpha: float, se_multiplier: float,
                   two_sided: bool = True) -> float:
    se = cohort_se(n, blocks, se_multiplier)
    if two_sided:
        zc = z_quantile(1.0 - alpha / 2.0)
        return phi(delta / se - zc) + phi(-delta / se - zc)
    zc = z_quantile(1.0 - alpha)
    return phi(delta / se - zc)


def delta_for_power(target: float, n: int, blocks: int, alpha: float, se_multiplier: float,
                    two_sided: bool = True) -> float:
    """目標検出力に要る効果量 δ（σ 単位）。"""
    se = cohort_se(n, blocks, se_multiplier)
    zc = z_quantile(1.0 - alpha / 2.0) if two_sided else z_quantile(1.0 - alpha)
    return (zc + z_quantile(target)) * se


def delta_to_auc(delta: float) -> float:
    """ブロック水準の d を、ON/OFF ブロックの分離 AUC に換算する（等分散正規）。"""
    return phi(delta / sqrt(2.0))


# ---------------------------------------------------------------------------
# (E) 検出力 — 並べ替えモンテカルロ（★ 解析式の検算）
# ---------------------------------------------------------------------------


def _diff_stat(values, on_idx, total=None) -> float:
    """ON 群平均 − OFF 群平均。★ 半々割なので sum(ON) の単調関数に畳める。

    diff = S/h - (T-S)/h = (2S - T)/h   （h = blocks/2, T = 全体和, S = ON 群の和）
    """
    half = len(values) // 2
    if total is None:
        total = sum(values)
    s = 0.0
    for i in on_idx:
        s += values[i]
    return (2.0 * s - total) / half


def permutation_power_cohort(delta: float, n: int, blocks: int, alpha: float, rng: random.Random,
                             n_sims: int = 400, n_perms: int = 600, two_sided: bool = True) -> float:
    """コホート水準の並べ替え検定の検出力（モンテカルロ）。

    各参加者につき blocks 個のブロック（半分 ON）。参加者効果は差で消えるので入れない。
    帰無は「各参加者の中で ON/OFF ラベルを入れ替える」。
    """
    half = blocks // 2
    idx = list(range(blocks))
    rejects = 0
    for _ in range(n_sims):
        subjects = []
        for _i in range(n):
            on_idx = rng.sample(idx, half)
            on_set = set(on_idx)
            vals = [rng.gauss(0.0, 1.0) + (delta if b in on_set else 0.0) for b in idx]
            subjects.append((vals, sum(vals), on_idx))
        observed = sum(_diff_stat(v, o, t) for v, t, o in subjects) / n
        ge = 0
        for _p in range(n_perms):
            tot = 0.0
            for vals, tsum, _o in subjects:
                tot += _diff_stat(vals, rng.sample(idx, half), tsum)
            stat = tot / n
            if (abs(stat) >= abs(observed) - 1e-12) if two_sided else (stat >= observed - 1e-12):
                ge += 1
        p = (ge + 1) / (n_perms + 1)
        if p < alpha:
            rejects += 1
    return rejects / n_sims


def permutation_power_individual(delta: float, blocks: int, alpha: float, rng: random.Random,
                                 n_sims: int = 600, two_sided: bool = False) -> float:
    """個人水準（G1 と同じ）の厳密並べ替え検定の検出力。★ 全数列挙（乱択しない）。"""
    from itertools import combinations

    half = blocks // 2
    idx = list(range(blocks))
    assignments = list(combinations(idx, half))
    n_assign = len(assignments)
    rejects = 0
    for _ in range(n_sims):
        on_idx = rng.sample(idx, half)
        on_set = set(on_idx)
        vals = [rng.gauss(0.0, 1.0) + (delta if b in on_set else 0.0) for b in idx]
        tsum = sum(vals)
        observed = _diff_stat(vals, on_idx, tsum)
        ge = 0
        for a in assignments:
            stat = _diff_stat(vals, a, tsum)
            if (abs(stat) >= abs(observed) - 1e-12) if two_sided else (stat >= observed - 1e-12):
                ge += 1
        if ge / n_assign < alpha:
            rejects += 1
    return rejects / n_sims


# ---------------------------------------------------------------------------
# (F) 識別 — 「k 要素のうち 1 つだけが真」のとき何が起きるか
# ---------------------------------------------------------------------------


def identification(delta: float, n: int, blocks: int, k: int, alpha: float, design: str,
                   target_power: float):
    props = design_properties(design, k, blocks)
    feasible = blocks >= props["blocks_required"]
    a_eff = alpha / props["n_tests"]
    pw = analytic_power(delta, n, blocks, a_eff, props["se_multiplier"]) if feasible else 0.0
    # 束ねる設計では「どれが効いたか」は言えない（検定 1 本・要素の別名）
    p_identify = 0.0 if not props["identifies"] else pw
    false_pos_family = 0.0 if props["n_tests"] <= 1 else 1.0 - (1.0 - a_eff) ** (props["n_tests"] - 1)
    return {
        "design": design,
        "k": k,
        "n": n,
        "blocks": blocks,
        "feasible": feasible,
        "blocks_required": props["blocks_required"],
        "se_multiplier": round(props["se_multiplier"], 4),
        "n_tests": props["n_tests"],
        "alpha_effective": a_eff,
        "power_for_delta": round(pw, 4),
        "p_identify_true_element": round(p_identify, 4),
        "p_any_false_positive": round(false_pos_family, 4),
        "delta_for_target_power": (
            round(delta_for_power(target_power, n, blocks, a_eff, props["se_multiplier"]), 4)
            if feasible
            else None
        ),
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-monte-carlo", action="store_true",
                    help="解析式のみで走らせる（★ 検算を落とすので通常は使わない）")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)
    with open(args.seed, encoding="utf-8") as fh:
        seed = int(next(l for l in fh if l.strip() and not l.startswith("#")).split("=")[-1].strip())

    grid = cfg["grid"]
    alpha = cfg["alpha"]
    target = cfg["target_power"]
    blocks = grid["blocks"]
    participants = grid["participants"]
    k_values = grid["k_values"]

    out = {
        "schema": "expression-power/v1",
        "config_echo": {
            "alpha": alpha,
            "target_power": target,
            "grid": grid,
            "hmm_version": cfg["anchors"]["hmm_version"],
            "expr_version": cfg["anchors"]["expr_version"],
            "repo_commit": cfg["anchors"]["repo_commit"],
        },
        "seed": seed,
    }

    # (A) 到達可能性
    out["reachability"] = reachability_table(blocks, participants, k_values, alpha)

    # (B) AUC の厳密帰無
    # ⚠️★★★ 2026-08-16 訂正（code-reviewer HIGH-1）:
    #   ここは α を **固定** で渡している。★ したがって出力表に k が現れないのは
    #   「要素数と無関係だから」ではなく **構成上の必然** である。
    #   ⚠️ notes.md の反証 1「AUC 要求は k の関数ではない」はこの表を根拠にしていたので誤りだった。
    #   → ★ 下の (B') で **α/k の格子**を別に出し、k 依存が実際に出ることを示す。
    out["auc_null"] = [auc_null_summary(b, alpha) for b in blocks]

    # (B') ★ 要求 AUC を α/k の格子で出す（★ 到達可能性だけを見ると誤読する）
    #   ★ 片側 / 両側の別も併記する。design.md は α（両側）を宣言しているため、
    #   ⚠️ 片側だけで「到達可能」と書くと過大になる。
    auc_by_k = []
    for b in blocks:
        base = auc_null_summary(b, alpha)
        p1 = base["min_p_one_sided"]
        row = {"blocks": b, "min_p_one_sided": p1, "min_p_two_sided": 2 * p1, "by_k": []}
        for k in k_values:
            a_eff = alpha / k
            s = auc_null_summary(b, a_eff)
            row["by_k"].append({
                "k": k,
                "alpha_effective": a_eff,
                "reachable_one_sided": p1 <= a_eff,
                "reachable_two_sided": (2 * p1) <= a_eff,
                "smallest_auc_reaching_alpha": s["smallest_auc_reaching_alpha"],
            })
        auc_by_k.append(row)
    out["auc_null_by_k"] = auc_by_k

    # (C)(D) 検出力の格子（解析式）
    power_rows = []
    for design in DESIGNS:
        for k in k_values:
            for b in blocks:
                props = design_properties(design, k, b)
                if b < props["blocks_required"]:
                    continue
                a_eff = alpha / props["n_tests"]
                for n in participants:
                    d80 = delta_for_power(target, n, b, a_eff, props["se_multiplier"])
                    power_rows.append(
                        {
                            "design": design,
                            "k": k,
                            "n": n,
                            "blocks": b,
                            "total_blocks": n * b,
                            "minutes_per_participant": b * cfg["block_minutes"],
                            "alpha_effective": a_eff,
                            "se": round(cohort_se(n, b, props["se_multiplier"]), 4),
                            "delta_for_target_power": round(d80, 4),
                            "auc_equivalent": round(delta_to_auc(d80), 4),
                        }
                    )
    out["power_grid"] = power_rows

    # 個人水準（G1 と同じ判定）の検出力
    rng = random.Random(seed)
    indiv = []
    for b in blocks:
        if comb(b, b // 2) > 5000:  # 全数列挙が重くなる所で止める
            continue
        for d in cfg["delta_probe"]:
            pw = permutation_power_individual(d, b, alpha, random.Random(seed + b * 1000 + int(d * 100)),
                                              n_sims=cfg["monte_carlo"]["individual_sims"])
            indiv.append({"blocks": b, "delta": d, "alpha": alpha, "power_one_sided": round(pw, 4)})
    out["individual_level_power"] = indiv

    # (E) 検算: 解析式 ⇄ モンテカルロ
    checks = []
    if not args.skip_monte_carlo:
        for cell in cfg["monte_carlo"]["cells"]:
            n, b, d = cell["n"], cell["blocks"], cell["delta"]
            mc = permutation_power_cohort(
                d, n, b, alpha, random.Random(seed + n * 97 + b * 13 + int(d * 1000)),
                n_sims=cfg["monte_carlo"]["sims"], n_perms=cfg["monte_carlo"]["perms"]
            )
            an = analytic_power(d, n, b, alpha, 1.0)
            checks.append(
                {
                    "n": n, "blocks": b, "delta": d,
                    "analytic": round(an, 4),
                    "monte_carlo": round(mc, 4),
                    "abs_diff": round(abs(an - mc), 4),
                    "tolerance": cfg["monte_carlo"]["tolerance"],
                    "agree": abs(an - mc) <= cfg["monte_carlo"]["tolerance"],
                }
            )
    out["analytic_vs_monte_carlo"] = checks

    # (F) 識別
    ident = []
    for design in DESIGNS:
        for k in k_values:
            for b in cfg["identification"]["blocks"]:
                for n in cfg["identification"]["participants"]:
                    ident.append(
                        identification(cfg["identification"]["delta"], n, b, k, alpha, design, target)
                    )
    out["identification"] = ident

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    sys.stdout.write(f"wrote {args.out}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
