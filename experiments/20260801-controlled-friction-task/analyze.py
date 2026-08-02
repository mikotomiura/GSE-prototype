#!/usr/bin/env python3
"""G1 統制タスク実験 — ブロック単位の特徴量抽出と、凍結された判定パイプライン。

★ **判定基準の単一真実源は `preregistration.md §3`（凍結）である。**
   本スクリプトはそれを実装するだけで、変更しない。齟齬があれば `preregistration.md` が正。

実装している凍結事項:
  §2.9  ブロック水準の最小打鍵（適格性ゲート・**モデル当てはめより前**に評価する）
  §3.1  L2 罰則つきロジスティック回帰 / λ=1.0 固定 / 学習 fold のみで z 標準化 /
        被験者内 leave-one-block-pair-out / out-of-fold AUC
  §3.2  FS-A（F1/F3/F4/F5/F6）と FS-B（＋Tier 0/1）の 2 本のみ。3 本目を作らない
  §3.3  主判定 = 個人内の並べ替え検定（p<0.05）＋ 補助 = AUC 中央値 ≥0.70 / ≥80% が AUC>0.60
  §3.4  見る順序: 操作チェック → positive control → FS-A/FS-B
  §3.5  産出量交絡の報告義務（条件別産出量・標準化係数・`keys` 単独 AUC）
  §3.9  並べ替えは**全数列挙**（G1: C(8,4)=70 / positive control: C(10,2)=45）→ seed 非依存
  §5.1  分散ゼロ特徴は標準化後 0 とし、必ず報告する

依存: **Python 標準ライブラリのみ**（`requirements.txt` を作らない・`env.md` の方針）。

使い方:
    python3 analyze.py --verify-blocks --dataset ~/gse-dataset --subject P015
        → ★ ラベルを一切読まない。ブロック長と打鍵数だけを出す（実施当日の検算用）。
    python3 analyze.py --dataset ~/gse-dataset --blocks-dir blocks --out results/metrics.json
    python3 analyze.py --selftest

⚠️ 出力にセッション日時・ファイル名を出さない（本 repo は一時 public 化の運用がある）。
⚠️ 被験者が書いた本文は入力にも出力にも存在しない（content-free 原則）。
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import pathlib
import statistics
import sys

# ---------------------------------------------------------------------------
# 事前登録から来る定数（preregistration.md / config.json のミラー。ここで変えない）
# ---------------------------------------------------------------------------
LAMBDA = 1.0                     # §3.1 L2 罰則（z 標準化後）・事前固定・チューニングしない
SILENCE_MS = 2000                # §3.2 silence = IKI >= 2000ms（現行 F5 の閾値に揃える）
MIN_KEYDOWNS_PER_BLOCK = 100     # §2.9 適格性ゲート
AUC_MEDIAN_MIN = 0.70            # §3.3-2
AUC_PER_SUBJECT_MIN = 0.60       # §3.3-3
AUC_PER_SUBJECT_FRACTION = 0.80  # §3.3-3
ALPHA = 0.05                     # §3.3-1
MANIPULATION_CHECK_MIN = 0.70    # §2.6
CORRECTION_CATEGORIES = {"backspace", "delete"}

FS_A = ["f1", "f3", "f4", "f5", "f6"]
TIER0 = ["keys", "bs_rate", "external_paste_chars", "ime_dwell_med"]
TIER1 = ["silence_p50", "silence_p90", "silence_max", "burst_p50", "burst_p90"]
FS_B = FS_A + TIER0 + TIER1                       # §3.2: 14 特徴量
FEATURE_SETS = {"FS_A": FS_A, "FS_B": FS_B}
KEYS_ALONE = ["keys"]                             # §3.5: 3 本目のセットではなく記述統計

MAX_NEWTON_ITERS = 50
NEWTON_TOL = 1e-8


# ---------------------------------------------------------------------------
# NDJSON → ブロック特徴量
# ---------------------------------------------------------------------------
def _pct(sorted_vals: list[float], p: float) -> float:
    """最近傍順位法の分位点（同 repo の 20260802-within-person-scope-detector と同じ定義）。"""
    if not sorted_vals:
        return 0.0
    k = min(len(sorted_vals) - 1, max(0, int(round(p * (len(sorted_vals) - 1)))))
    return float(sorted_vals[k])


def read_block(path: pathlib.Path) -> dict:
    """匿名化 NDJSON 1 ファイル（= 1 ブロック）からブロック特徴量を計算する。

    入力は `analysis/anonymize.rs` を通した形式を前提とする:
      key        {t(相対ms), category, press}   ← vk は匿名化で category に置き換わっている
      paste      {t, external_paste_chars}
      ime_shadow {t, dwell_ms, nav, abandon}
      feat       {t, f1, f3, f4, f5, f6, ...}   ← FS-A の出所（§3.2 / design D-2）
    生の `vk` を持つ未匿名 NDJSON も受け付ける（`vk` から category を導けるため）。
    """
    keydowns: list[int] = []
    corrections = 0
    paste_chars = 0
    dwells: list[int] = []
    feats: list[dict] = []
    malformed = 0

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception:
            malformed += 1
            continue
        t = o.get("type")
        if t == "key":
            if o.get("press") is not True:
                continue
            keydowns.append(int(o["t"]))
            cat = o.get("category")
            if cat is None and "vk" in o:          # 未匿名ログのフォールバック
                cat = {0x08: "backspace", 0x2E: "delete"}.get(int(o["vk"]))
            if cat in CORRECTION_CATEGORIES:
                corrections += 1
        elif t == "paste":
            v = o.get("external_paste_chars")
            if isinstance(v, int):
                paste_chars += v
        elif t == "ime_shadow":
            v = o.get("dwell_ms")
            if isinstance(v, int):
                dwells.append(v)
        elif t == "feat":
            feats.append(o)

    keydowns.sort()
    n = len(keydowns)
    # §3.2: ブロックの計測は最初の keydown から最後の keydown まで
    span_ms = (keydowns[-1] - keydowns[0]) if n >= 2 else 0
    ikis = [b - a for a, b in zip(keydowns, keydowns[1:]) if b >= a]

    silences = sorted(x for x in ikis if x >= SILENCE_MS)
    # §3.2: silence が 0 個のブロックは 3 値とも 0（欠測にしない・事前宣言）
    bursts: list[int] = []
    run = 1
    for x in ikis:
        if x >= SILENCE_MS:
            bursts.append(run)
            run = 1
        else:
            run += 1
    if n > 0:
        bursts.append(run)
    bursts_sorted = sorted(bursts)

    # §3.2 / design D-2: FS-A は `feat` 行の中央値（最初の keydown 以降の行のみ）
    t0 = keydowns[0] if keydowns else 0
    rows = [f for f in feats if int(f.get("t", 0)) >= t0]
    fs_a = {}
    for k in FS_A:
        vals = [float(f[k]) for f in rows if isinstance(f.get(k), (int, float))]
        fs_a[k] = statistics.median(vals) if vals else 0.0

    return {
        "n_keydowns": n,
        "span_ms": span_ms,
        "n_feat_rows": len(rows),
        "malformed_lines": malformed,
        "features": dict(fs_a, **{
            "keys": float(n),
            "bs_rate": (corrections / n) if n else 0.0,
            "external_paste_chars": float(paste_chars),
            "ime_dwell_med": float(statistics.median(dwells)) if dwells else 0.0,
            "silence_p50": _pct(silences, 0.50),
            "silence_p90": _pct(silences, 0.90),
            "silence_max": float(silences[-1]) if silences else 0.0,
            "burst_p50": _pct(bursts_sorted, 0.50),
            "burst_p90": _pct(bursts_sorted, 0.90),
        }),
        "n_silences": len(silences),
        "ime_shadow_rows": len(dwells),
    }


# ---------------------------------------------------------------------------
# L2 罰則つきロジスティック回帰（§3.1・標準ライブラリのみ）
# ---------------------------------------------------------------------------
def _solve(A: list[list[float]], b: list[float]) -> list[float] | None:
    """部分ピボット選択つき Gauss 消去。特異なら None。"""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            return None
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / piv
            if f == 0.0:
                continue
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def fit_l2_logistic(X: list[list[float]], y: list[int]) -> dict:
    """切片つき L2 罰則ロジスティック回帰。切片は罰則しない。

    目的: Σ log(1+exp(-ỹ f(x))) + (λ/2)||w||²   （ỹ ∈ {-1,+1}, w は切片を除く係数）
    ⚠️ λ は事前固定（§3.1）。データから選ばない。
    """
    n = len(X)
    d = len(X[0]) if n else 0
    beta = [0.0] * (d + 1)          # beta[0] = 切片
    for _ in range(MAX_NEWTON_ITERS):
        g = [0.0] * (d + 1)
        H = [[0.0] * (d + 1) for _ in range(d + 1)]
        for i in range(n):
            z = beta[0] + sum(beta[j + 1] * X[i][j] for j in range(d))
            p = 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z))))
            r = p - y[i]
            w = max(p * (1.0 - p), 1e-10)
            xi = [1.0] + X[i]
            for a in range(d + 1):
                g[a] += r * xi[a]
                for b in range(d + 1):
                    H[a][b] += w * xi[a] * xi[b]
        for j in range(1, d + 1):
            g[j] += LAMBDA * beta[j]
            H[j][j] += LAMBDA
        H[0][0] += 1e-8             # 切片の数値安定化のみ（罰則ではない）
        step = _solve(H, [-v for v in g])
        if step is None:
            break
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < NEWTON_TOL:
            break

    # 学習側で完全分離したか（§3.1 の診断値）
    perfect = all(
        (beta[0] + sum(beta[j + 1] * X[i][j] for j in range(d)) > 0) == (y[i] == 1)
        for i in range(n)
    ) if n else False
    return {"beta": beta, "perfect_training_separation": perfect}


def _score(beta: list[float], x: list[float]) -> float:
    return beta[0] + sum(beta[j + 1] * x[j] for j in range(len(x)))


def standardize(train: list[list[float]], rows: list[list[float]]) -> tuple[list[list[float]], list[int]]:
    """§3.1: 学習 fold のみで z 標準化。§5.1: 分散ゼロ特徴は 0 に潰し、その添字を返す。

    標準偏差は**母標準偏差**（分母 = 学習 fold の標本数）を使う。事前登録は ddof を指定して
    いないため、罰則の強さと係数尺度が実装差で動かないようにここで固定する。
    λ=1.0 が事前固定であることと合わせて、**選択の余地を残さない**ためである。
    """
    d = len(train[0])
    out_rows = [row[:] for row in rows]
    degenerate: list[int] = []
    for j in range(d):
        col = [r[j] for r in train]
        mu = sum(col) / len(col)
        var = sum((v - mu) ** 2 for v in col) / len(col)
        sd = math.sqrt(var)
        if sd < 1e-12:
            degenerate.append(j)
            for r in out_rows:
                r[j] = 0.0
        else:
            for r in out_rows:
                r[j] = (r[j] - mu) / sd
    return out_rows, degenerate


def cv_auc(rows: list[list[float]], labels: list[int]) -> dict:
    """§3.1: 被験者内 leave-one-block-pair-out の out-of-fold AUC。

    fold = (held-out 陽性ブロック 1 個, held-out 陰性ブロック 1 個) の全組合せ。
    out-of-fold AUC = 「held-out 陽性が held-out 陰性より高いスコアを得た fold の割合」
    （同値は 0.5）。これは held-out 対上の AUC の定義そのもの（design D-3）。
    """
    pos = [i for i, v in enumerate(labels) if v == 1]
    neg = [i for i, v in enumerate(labels) if v == 0]
    wins = 0.0
    folds = 0
    max_abs_coef = 0.0
    perfect_folds = 0
    degenerate_counts: dict[int, int] = {}
    for i in pos:
        for j in neg:
            tr_idx = [k for k in range(len(rows)) if k not in (i, j)]
            train_raw = [rows[k] for k in tr_idx]
            all_std, degen = standardize(train_raw, rows)
            for jj in degen:
                degenerate_counts[jj] = degenerate_counts.get(jj, 0) + 1
            model = fit_l2_logistic([all_std[k] for k in tr_idx], [labels[k] for k in tr_idx])
            beta = model["beta"]
            max_abs_coef = max(max_abs_coef, max(abs(b) for b in beta[1:]) if len(beta) > 1 else 0.0)
            perfect_folds += 1 if model["perfect_training_separation"] else 0
            si, sj = _score(beta, all_std[i]), _score(beta, all_std[j])
            wins += 1.0 if si > sj else (0.5 if si == sj else 0.0)
            folds += 1
    return {
        "auc": wins / folds if folds else float("nan"),
        "n_folds": folds,
        "max_abs_coefficient": max_abs_coef,
        "folds_with_perfect_training_separation": perfect_folds,
        "degenerate_feature_folds": degenerate_counts,
    }


def full_fit_coefficients(rows: list[list[float]], labels: list[int], names: list[str]) -> dict:
    """§3.5: 各特徴の標準化係数（全ブロックで 1 回当てはめた記述統計）。

    ⚠️ **これは in-sample の当てはめである**（全ブロックで標準化し、全ブロックで当てはめる）。
    どの特徴がどちら向きに効いたかを読むためだけに出す。**性能の指標ではない**——
    性能は out-of-fold AUC（`cv_auc`）と並べ替え検定でのみ判断する（§3.3）。
    """
    std_rows, degen = standardize(rows, rows)
    model = fit_l2_logistic(std_rows, labels)
    beta = model["beta"]
    return {
        "IN_SAMPLE_descriptive_only": True,
        "intercept": round(beta[0], 4),
        "standardized_coefficients": {n: round(beta[k + 1], 4) for k, n in enumerate(names)},
        "degenerate_features": [names[j] for j in degen],
        "perfect_training_separation": model["perfect_training_separation"],
    }


# ---------------------------------------------------------------------------
# 並べ替え検定（§3.9: 全数列挙・seed 非依存）
# ---------------------------------------------------------------------------
def exact_permutation_test(rows: list[list[float]], labels: list[int]) -> dict:
    n = len(labels)
    k = sum(labels)
    observed = cv_auc(rows, labels)
    obs_auc = observed["auc"]
    ge = 0
    total = 0
    for combo in itertools.combinations(range(n), k):
        perm = [1 if i in combo else 0 for i in range(n)]
        total += 1
        if cv_auc(rows, perm)["auc"] >= obs_auc - 1e-12:
            ge += 1
    return {
        "observed_auc": round(obs_auc, 4),
        "n_permutations": total,
        "enumeration": "EXHAUSTIVE (not sampled) -> seed-independent",
        "n_ge_observed": ge,
        "p_value": round(ge / total, 6),
        "min_attainable_p": round(1.0 / total, 6),
        "alpha": ALPHA,
        "significant": (ge / total) < ALPHA,
        "one_sided": "larger AUC = more separation",
        "max_abs_coefficient": round(observed["max_abs_coefficient"], 4),
        "folds_with_perfect_training_separation": observed["folds_with_perfect_training_separation"],
        "n_folds": observed["n_folds"],
    }


def fisher_combine(pvals: list[float]) -> dict:
    """§3.3-1 / §3.9: Fisher 統合。n>=2 のときのみ使う。"""
    if len(pvals) < 2:
        return {"applied": False,
                "reason": "n<2: Fisher is applied only for n>=2 (preregistration.md 3.9); "
                          "the single within-subject p is reported as-is"}
    stat = -2.0 * sum(math.log(max(p, 1e-300)) for p in pvals)
    k = len(pvals)                       # 自由度 2k → 偶数なので閉形式で上側確率が出る
    x = stat / 2.0
    term = 1.0
    s = 1.0
    for i in range(1, k):
        term *= x / i
        s += term
    p = math.exp(-x) * s
    return {
        "applied": True,
        "k": k,
        "chi2": round(stat, 4),
        "df": 2 * k,
        "p_value": round(min(1.0, p), 6),
        "significant": p < ALPHA,
        "known_limitation": "within-subject p-values are discrete (min 1/70), so the combined p is "
                            "CONSERVATIVE. Frozen knowingly (preregistration.md 3.3).",
    }


# ---------------------------------------------------------------------------
# 適格性ゲート（§2.9・**モデル当てはめより前**）
# ---------------------------------------------------------------------------
def eligibility(blocks: list[dict]) -> dict:
    g1 = [b for b in blocks if b["condition"] in ("HI", "LO")]
    copy = [b for b in blocks if b["condition"] == "copy"]
    low_g1 = [b["block"] for b in g1 if b["n_keydowns"] < MIN_KEYDOWNS_PER_BLOCK]
    low_all = [b["block"] for b in (g1 + copy) if b["n_keydowns"] < MIN_KEYDOWNS_PER_BLOCK]
    return {
        "threshold_keydowns_per_block": MIN_KEYDOWNS_PER_BLOCK,
        "evaluated": "BEFORE any model is fitted (preregistration.md 2.9)",
        "keydowns_per_block": {b["block"]: b["n_keydowns"] for b in blocks},
        "blocks_below_threshold_g1": low_g1,
        "blocks_below_threshold_any": low_all,
        "eligible_for_primary": not low_g1,
        "eligible_for_positive_control": not low_all,
        "note": "Blocks are never dropped; the SUBJECT is excluded so that HI4/LO4 and C(8,4)=70 survive. "
                "Excluded subjects are not replaced (preregistration.md 2.4-7).",
    }


# ---------------------------------------------------------------------------
# 被験者 1 名分の解析
# ---------------------------------------------------------------------------
def analyse_subject(subject: str, blocks: list[dict]) -> dict:
    if not blocks:
        return {"subject": subject, "error": "no blocks in the assignment file"}
    elig = eligibility(blocks)
    g1 = [b for b in blocks if b["condition"] in ("HI", "LO")]
    order = sorted(blocks, key=lambda b: b["block"])

    result: dict = {
        "subject": subject,
        "arrangement": blocks[0].get("arrangement"),
        "n_blocks": len(blocks),
        "eligibility": elig,
        "block_summary": [
            {"block": b["block"], "condition": b["condition"], "topic_id": b.get("topic_id"),
             "n_keydowns": b["n_keydowns"], "span_ms": b["span_ms"],
             "n_feat_rows": b["n_feat_rows"], "produced_chars": b.get("produced_chars")}
            for b in order
        ],
    }

    # §3.5: 産出量交絡の報告（条件別の実産出量）
    def _summary(cond: str) -> dict:
        vals = [b["n_keydowns"] for b in blocks if b["condition"] == cond]
        chars = [b["produced_chars"] for b in blocks
                 if b["condition"] == cond and isinstance(b.get("produced_chars"), int)]
        return {
            "n_blocks": len(vals),
            "keys_median": statistics.median(vals) if vals else None,
            "keys_min": min(vals) if vals else None,
            "keys_max": max(vals) if vals else None,
            "produced_chars_median": statistics.median(chars) if chars else None,
            "produced_chars_reported": len(chars),
        }

    result["production_by_condition"] = {c: _summary(c) for c in ("HI", "LO", "copy")}
    if not any(isinstance(b.get("produced_chars"), int) for b in blocks):
        result["production_by_condition"]["warning"] = (
            "produced_chars not supplied. preregistration.md 3.5 requires reporting the realised "
            "output per condition (block `keys` AND final character count). The app never stores the "
            "written text (content-free), so the experimenter must record the character count on the "
            "recording sheet (protocol.md 2.2) and put it into the blocks file.")

    # --- positive control（§2.5・§3.4 で FS-A/FS-B より先に見る） ---
    if elig["eligible_for_positive_control"] and len(order) == 10:
        rows = [[b["features"][f] for f in FS_B] for b in order]
        labels = [1 if b["condition"] == "copy" else 0 for b in order]
        pc = exact_permutation_test(rows, labels)
        pc["labels"] = "copy(2) vs writing(8)"
        pc["known_limitation"] = ("copy blocks are position-fixed, so this separation is confounded with "
                                  "position. FLOOR CHECK on instrument health only; no effect size is claimed.")
        pc["passed"] = bool(pc["significant"])
    else:
        pc = {"skipped": True,
              "reason": "subject ineligible for the positive control, or the session does not have 10 blocks"}
    result["positive_control"] = pc

    # --- 主判定（§3.3） ---
    if not elig["eligible_for_primary"]:
        result["primary"] = {"skipped": True, "reason": "ineligible under the 2.9 gate"}
        return result
    if len(g1) != 8 or sum(1 for b in g1 if b["condition"] == "HI") != 4:
        result["primary"] = {"skipped": True,
                             "reason": f"expected 8 G1 blocks with HI4/LO4, got {len(g1)}"}
        return result

    g1_order = sorted(g1, key=lambda b: b["block"])
    labels = [1 if b["condition"] == "HI" else 0 for b in g1_order]
    primary: dict = {}
    for name, feats in FEATURE_SETS.items():
        rows = [[b["features"][f] for f in feats] for b in g1_order]
        primary[name] = exact_permutation_test(rows, labels)
        primary[name]["n_features"] = len(feats)
        primary[name]["coefficients"] = full_fit_coefficients(rows, labels, feats)
    # §3.5: `keys` 単独 AUC（3 本目の特徴量セットではない・descriptive）
    rows_keys = [[b["features"][f] for f in KEYS_ALONE] for b in g1_order]
    primary["keys_alone_DESCRIPTIVE"] = dict(
        cv_auc(rows_keys, labels),
        note="single-feature descriptive statistic (preregistration.md 3.5), NOT a third feature set. "
             "If FS_B's AUC does not substantially exceed this, the separation may be attributable to "
             "output volume and must be reported as such.")
    result["primary"] = primary
    return result


# ---------------------------------------------------------------------------
# 操作チェック（§2.6）
# ---------------------------------------------------------------------------
def manipulation_check(blocks: list[dict], answers: list[dict]) -> dict:
    """answers: [{"block": 3, "harder": 2}, ...]  harder = より詰まったと選ばれたブロック番号。"""
    cond = {b["block"]: b["condition"] for b in blocks}
    cross, hi_chosen, same = 0, 0, 0
    for a in answers:
        cur, prev = a.get("block"), a.get("block", 0) - 1
        if cur not in cond or prev not in cond:
            continue
        if cond[cur] not in ("HI", "LO") or cond[prev] not in ("HI", "LO"):
            continue
        if cond[cur] == cond[prev]:
            same += 1                     # §2.6: 同条件ペアは分母に入れない
            continue
        cross += 1
        if cond.get(a.get("harder")) == "HI":
            hi_chosen += 1
    rate = (hi_chosen / cross) if cross else None
    return {
        "n_answers": len(answers),
        "n_cross_condition_pairs_DENOMINATOR": cross,
        "n_same_condition_pairs_excluded": same,
        "hi_chosen_as_harder": hi_chosen,
        "rate": round(rate, 4) if rate is not None else None,
        "threshold": MANIPULATION_CHECK_MIN,
        "passed": (rate is not None and rate >= MANIPULATION_CHECK_MIN),
        "note": "Denominator is cross-condition pairs only (preregistration.md 2.6). "
                "This is NOT part of the verdict, but it is read FIRST (3.4).",
    }


# ---------------------------------------------------------------------------
# コホート水準の判定（§3.3）
# ---------------------------------------------------------------------------
def cohort_verdict(per_subject: list[dict], interpretable: bool, reason: str) -> dict:
    out: dict = {"interpretable": interpretable, "interpretability_reason": reason}
    for name in FEATURE_SETS:
        usable = [s for s in per_subject if "skipped" not in s.get("primary", {"skipped": True})]
        aucs = [s["primary"][name]["observed_auc"] for s in usable]
        pvals = [s["primary"][name]["p_value"] for s in usable]
        n = len(usable)
        need = math.ceil(AUC_PER_SUBJECT_FRACTION * n) if n else 0
        above = sum(1 for a in aucs if a > AUC_PER_SUBJECT_MIN)
        fisher = fisher_combine(pvals)
        primary_sig = (fisher["p_value"] < ALPHA) if fisher["applied"] else (
            pvals[0] < ALPHA if pvals else False)
        median_auc = statistics.median(aucs) if aucs else None
        out[name] = {
            "n_subjects_analysed": n,
            "per_subject_auc": [round(a, 4) for a in aucs],
            "per_subject_p": pvals,
            "fisher": fisher,
            "criterion_1_primary_permutation_significant": primary_sig,
            "criterion_2_median_auc": round(median_auc, 4) if median_auc is not None else None,
            "criterion_2_met": (median_auc is not None and median_auc >= AUC_MEDIAN_MIN),
            "criterion_3_subjects_above_0_60": f"{above}/{n} (need >= {need})",
            "criterion_3_met": (n > 0 and above >= need),
            "separated": bool(
                interpretable and primary_sig
                and median_auc is not None and median_auc >= AUC_MEDIAN_MIN
                and n > 0 and above >= need),
            "note": "'separated' requires ALL THREE criteria (preregistration.md 3.3). "
                    "A high AUC without permutation significance is NOT separation.",
        }
        if n == 1:
            out[name]["n_equals_1_caveat"] = (
                "With n=1 the descriptive criteria carry little practical meaning (preregistration.md 3.9), "
                "and topic-by-condition counterbalancing does not exist (2.7): topic confounding is NOT excluded.")
    return out


# ---------------------------------------------------------------------------
# 入出力
# ---------------------------------------------------------------------------
def load_subject_blocks(spec: dict, dataset: pathlib.Path) -> list[dict]:
    """割付ファイル（assign.py の JSON に `file` を書き足したもの）を読み、特徴量を付ける。"""
    subject = spec["subject"]
    out = []
    for b in spec["blocks"]:
        if "file" not in b:
            raise SystemExit(f"[NG] {subject} block {b['block']}: 'file' が無い "
                             f"(記録用紙の NDJSON ファイル名を書き足すこと・protocol.md §2.2)")
        p = dataset / "raw" / subject / b["file"]
        if not p.is_file():
            raise SystemExit(f"[NG] {subject} block {b['block']}: NDJSON が見つからない")
        blk = read_block(p)
        blk.update({"block": b["block"], "condition": b["condition"],
                    "topic_id": b.get("topic_id"), "arrangement": spec.get("arrangement"),
                    "produced_chars": b.get("produced_chars")})
        out.append(blk)
    return out


def cmd_verify_blocks(dataset: pathlib.Path, subject: str) -> int:
    """★ ラベルを一切読まない。ブロック長と打鍵数だけを出す（protocol.md §2.3-3）。

    これを走らせても「解析結果を見た」ことにならない（条件を読んでいないため）。
    """
    d = dataset / "raw" / subject
    if not d.is_dir():
        print(f"[NG] {d} が無い")
        return 1
    files = sorted(d.glob("*.ndjson"))
    if not files:
        print(f"[NG] {subject} の NDJSON が 1 本も無い")
        return 1
    print(f"[verify-blocks] {subject}: {len(files)} セッション"
          f"（★ 条件ラベルは読んでいない。長さと打鍵数だけ）")
    print("  #  | 打鍵数 | 長さ(mm:ss) | feat行 | 適格(>=100)")
    print("-----+--------+-------------+--------+------------")
    ok = True
    for i, f in enumerate(files, start=1):
        b = read_block(f)                       # ファイル名は出力しない（日時が入るため）
        secs = b["span_ms"] / 1000.0
        good = b["n_keydowns"] >= MIN_KEYDOWNS_PER_BLOCK
        ok = ok and good
        mmss = f"{int(secs)//60:d}:{int(secs)%60:02d}"
        print(f" {i:3d} | {b['n_keydowns']:6d} | {mmss:>11s} "
              f"| {b['n_feat_rows']:6d} | {'○' if good else '× ★要記録'}")
    print()
    print("  ★ 5 分ブロックなら長さは 4:00〜5:00 に収まるはず。大きく外れたら起動/停止の取り違えを疑う。")
    print("  ★ 打鍵数を記録用紙に転記する。閾値割れでも **その場でやり直さない**（protocol.md §7）。")
    if len(files) not in (4, 10):
        print(f"  ⚠️ セッション数が {len(files)} 本。確証デザインは 10 本 / パイロット P-1 は 4 本。")
    if not ok:
        print("  ⚠️ 閾値割れのブロックがある。§2.9 の適格性ゲートに掛かる可能性が高い。")
    # ★ 常に 0 を返す。ここは**情報提示専用**であり、赤にすると
    #   「当日その場で対処する」誘因が生まれる（＝結果を見た後の介入になる・protocol.md §7）。
    return 0


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="~/gse-dataset")
    ap.add_argument("--blocks-dir", default=str(here / "blocks"),
                    help="assign.py の JSON に NDJSON ファイル名を書き足したものを置くディレクトリ")
    ap.add_argument("--subject", help="--verify-blocks で対象にする被験者")
    ap.add_argument("--verify-blocks", action="store_true",
                    help="★ ラベルを読まずにブロック長と打鍵数だけを出す（実施当日の検算）")
    ap.add_argument("--out", default=str(here / "results" / "metrics.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    dataset = pathlib.Path(a.dataset).expanduser()
    if a.verify_blocks:
        if not a.subject:
            ap.error("--verify-blocks には --subject が要る")
        return cmd_verify_blocks(dataset, a.subject)

    bdir = pathlib.Path(a.blocks_dir)
    specs = sorted(bdir.glob("P*.json")) if bdir.is_dir() else []
    if not specs:
        print(f"[NG] {bdir} に割付ファイル（P0xx.json）が無い。")
        print("     手順: python3 assign.py --subject P0xx --json > blocks/P0xx.json")
        print("           → 各 block に \"file\"（NDJSON 名）と \"produced_chars\" を書き足す")
        return 1

    per_subject = []
    mchecks = {}
    for s in specs:
        spec = json.loads(s.read_text(encoding="utf-8"))
        blocks = load_subject_blocks(spec, dataset)
        if spec.get("manipulation_check_answers"):
            mchecks[spec["subject"]] = manipulation_check(blocks, spec["manipulation_check_answers"])
        per_subject.append(analyse_subject(spec["subject"], blocks))

    errored = [s for s in per_subject if "error" in s]
    per_subject = [s for s in per_subject if "error" not in s]
    if errored:
        print(f"[warn] 割付ファイルが不正な被験者 {len(errored)} 名を解析から外した: "
              f"{[s['subject'] for s in errored]}")
    if not per_subject:
        print("[NG] 解析できる被験者が 1 名もいない")
        return 1

    # §3.4 の見る順序: 1. 操作チェック → 2. positive control → 3. FS-A / FS-B
    mc_ok = bool(mchecks) and all(m["passed"] for m in mchecks.values())
    pcs = [s["positive_control"] for s in per_subject if not s["positive_control"].get("skipped")]
    pc_ok = bool(pcs) and all(p.get("passed") for p in pcs)
    if not mchecks:
        interp, why = False, ("manipulation check not supplied. Per 3.4 the separation result must not be "
                              "interpreted until the manipulation check has been read and passed.")
    elif not mc_ok:
        interp, why = False, "manipulation check FAILED (2.6): the friction was not manipulated; redesign the task."
    elif not pcs:
        interp, why = False, "positive control could not be run (no eligible 10-block subject)."
    elif not pc_ok:
        interp, why = False, ("positive control FAILED: G1 IS VOID (2.5). Instrument/pipeline fault suspected. "
                              "Do NOT read a negative result as a property of the world.")
    else:
        interp, why = True, "manipulation check passed and positive control passed (3.4 order satisfied)."

    result = {
        "experiment": "20260801-controlled-friction-task",
        "gate": "G1",
        "preregistration": "preregistration.md (frozen; authoritative over this output)",
        "reading_order_3_4": ["1_manipulation_check", "2_positive_control", "3_feature_sets"],
        "1_manipulation_check": mchecks or {"supplied": False},
        "2_positive_control": {s["subject"]: s["positive_control"] for s in per_subject},
        "3_verdict": cohort_verdict(per_subject, interp, why),
        "per_subject": per_subject,
        "subjects_with_invalid_assignment_files": errored,
        "constants": {"lambda": LAMBDA, "silence_ms": SILENCE_MS,
                      "min_keydowns_per_block": MIN_KEYDOWNS_PER_BLOCK,
                      "auc_median_min": AUC_MEDIAN_MIN, "alpha": ALPHA},
        "hmm_version": "TO_BE_STAMPED_AT_EXECUTION (env.md)",
        "privacy": "no session timestamps, no file names, no written text appear in this output",
    }
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] {out}  interpretable={interp}")
    for name in FEATURE_SETS:
        v = result["3_verdict"][name]
        print(f"  {name}: separated={v['separated']} median_auc={v['criterion_2_median_auc']} "
              f"fisher_p={v['fisher'].get('p_value')}")
    return 0


# ---------------------------------------------------------------------------
# 自己検証
# ---------------------------------------------------------------------------
def _synthetic(sep: float, n: int = 8, d: int = 14, seed: int = 0) -> tuple[list[list[float]], list[int]]:
    """再現可能な合成データ（乱数を使わず決定的に作る）。sep が大きいほど分離しやすい。"""
    labels = [1, 0] * (n // 2)
    rows = []
    for i, y in enumerate(labels):
        row = []
        for j in range(d):
            base = math.sin((i + 1) * (j + 1) * 1.7 + seed)   # 決定的な「雑音」
            row.append(base + (sep if (y == 1 and j == 0) else 0.0))
        rows.append(row)
    return rows, labels


def selftest() -> int:
    fails: list[str] = []

    # 1) 明確に分離する合成データ -> AUC 1.0 / p = 1/70
    rows, labels = _synthetic(sep=50.0)
    r = exact_permutation_test(rows, labels)
    if r["n_permutations"] != 70:
        fails.append(f"並べ替えが全数列挙になっていない: {r['n_permutations']} != 70")
    if r["observed_auc"] < 0.999:
        fails.append(f"分離する合成データで AUC={r['observed_auc']} (期待 1.0)")
    # ⚠️ p が厳密に 1/70 になるとは限らない。8 点 × 14 次元では**別のラベル割付でも**
    #    線形分離できてしまう（帰無分布の上端が縮退する）。ここで見るのは
    #    「有意に到達できること」と「最小 p が 1/70 として計算されていること」である。
    if not r["significant"] or r["p_value"] >= ALPHA:
        fails.append(f"分離する合成データで有意にならない: p={r['p_value']}")
    if abs(r["min_attainable_p"] - 1 / 70) > 1e-6:
        fails.append(f"最小到達可能 p が違う: {r['min_attainable_p']} != {1/70:.6f}")

    # 2) ラベルが無情報 -> 有意にならない
    rows2, labels2 = _synthetic(sep=0.0)
    r2 = exact_permutation_test(rows2, labels2)
    if r2["p_value"] < ALPHA:
        fails.append(f"無情報ラベルで p={r2['p_value']} < {ALPHA}（偽陽性）")

    # 3) 分散ゼロ特徴が潰れ、例外にならない（§5.1）
    rows3 = [row[:] for row in rows]
    for row in rows3:
        row[3] = 7.0                       # ime_dwell_med 相当を定数にする
    c = cv_auc(rows3, labels)
    if 3 not in c["degenerate_feature_folds"]:
        fails.append("分散ゼロ特徴が degenerate として報告されていない (§5.1)")
    if c["degenerate_feature_folds"].get(3) != c["n_folds"]:
        fails.append("分散ゼロ特徴が全 fold で潰れていない")

    # 4) positive control の並べ替えは C(10,2)=45
    rows4, _ = _synthetic(sep=50.0, n=10)
    lab4 = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    r4 = exact_permutation_test(rows4, lab4)
    if r4["n_permutations"] != 45:
        fails.append(f"positive control の並べ替えが {r4['n_permutations']} != 45")

    # 5) Fisher は n<2 で適用されない（§3.9）
    if fisher_combine([0.01])["applied"]:
        fails.append("n=1 で Fisher が適用されている (§3.9 違反)")
    f = fisher_combine([0.014, 0.014])
    if not (0.0 < f["p_value"] < 0.01):
        fails.append(f"Fisher の値が異常: {f}")

    # 6) 適格性ゲートは打鍵数だけで判定し、ブロックを落とさない（§2.9）
    blks = [{"block": i, "condition": ("HI" if i % 2 else "LO"), "n_keydowns": 500} for i in range(2, 10)]
    blks += [{"block": 1, "condition": "copy", "n_keydowns": 500},
             {"block": 10, "condition": "copy", "n_keydowns": 500}]
    e = eligibility(blks)
    if not (e["eligible_for_primary"] and e["eligible_for_positive_control"]):
        fails.append("十分な打鍵で不適格になっている")
    blks[0]["n_keydowns"] = 9              # P014 型
    e2 = eligibility(blks)
    if e2["eligible_for_primary"]:
        fails.append("9 打鍵のブロックがあるのに適格になっている (§2.9)")
    if len(e2["keydowns_per_block"]) != 10:
        fails.append("適格性ゲートがブロックを落としている（落としてはいけない）")

    # 7) ブロック特徴量: silence 0 個なら 3 値とも 0（§3.2 の事前宣言）
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "b.ndjson"
        lines = [json.dumps({"type": "meta", "session_start": 0, "hmm_version": "x"})]
        for i in range(120):               # 100ms 間隔 -> silence なし
            lines.append(json.dumps({"type": "key", "t": i * 100, "category": "alphabetic", "press": True}))
            lines.append(json.dumps({"type": "key", "t": i * 100 + 40, "category": "alphabetic", "press": False}))
        lines.append(json.dumps({"type": "key", "t": 500, "category": "backspace", "press": True}))
        lines.append(json.dumps({"type": "feat", "t": 1000, "f1": 100.0, "f3": 0.1, "f4": 5.0,
                                 "f5": 0.0, "f6": 0.0}))
        lines.append(json.dumps({"type": "paste", "t": 2000, "external_paste_chars": 12}))
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        b = read_block(p)
        ft = b["features"]
        if b["n_keydowns"] != 121:
            fails.append(f"keydown 数が違う: {b['n_keydowns']} != 121")
        if not (ft["silence_p50"] == ft["silence_p90"] == ft["silence_max"] == 0.0):
            fails.append("silence 0 個なのに 3 値が 0 でない (§3.2)")
        if abs(ft["bs_rate"] - 1 / 121) > 1e-9:
            fails.append(f"bs_rate が違う: {ft['bs_rate']}")
        if ft["external_paste_chars"] != 12.0:
            fails.append("external_paste_chars を拾えていない")
        if ft["ime_dwell_med"] != 0.0:
            fails.append("ime_shadow が無いのに ime_dwell_med が 0 でない (macOS 実施の想定・§5.1)")
        if ft["f1"] != 100.0:
            fails.append("FS-A が feat 行から取れていない (design D-2)")

        # silence / burst が定義どおり出るか
        p2 = pathlib.Path(td) / "c.ndjson"
        ts = [0, 100, 200, 5000, 5100, 12000]      # silence: 4800ms, 6900ms
        p2.write_text("\n".join(
            json.dumps({"type": "key", "t": t, "category": "alphabetic", "press": True}) for t in ts
        ) + "\n", encoding="utf-8")
        f2 = read_block(p2)["features"]
        if f2["silence_max"] != 6900.0:
            fails.append(f"silence_max が違う: {f2['silence_max']} != 6900")
        if f2["burst_p90"] != 3.0:
            fails.append(f"burst_p90 が違う: {f2['burst_p90']} != 3 (バースト長 [3,2,1])")

    if fails:
        print("[NG] analyze.py selftest 失敗:")
        for f_ in fails:
            print(f"  - {f_}")
        return 1
    print("[OK] analyze.py selftest 緑 "
          "(全数列挙 70/45・分離/非分離・分散ゼロ・Fisher・適格性ゲート・特徴量定義)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
