#!/usr/bin/env python3
"""within-person（個人基準・leave-one-out）な out-of-scope 検出器の検証。

事前登録: preregistration.md（結果を見る前に凍結済み・analyze.py と同時にコミット）
出力: metrics.json（集計値のみ。raw NDJSON は一切コピーしない）

★ 主検定 T-1 は導出集合（DERIVATION_PID）を除外して行う。
  判別特徴 bs_rate はその被験者の探索的分析から選ばれたため、含めると循環する。
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import random
import statistics
import sys

# --- 事前登録した定数（変更したら探索的結果として報告すること） ---
MIN_PRESSES = 200            # これ未満のセッションは統計が不安定なため除外（前ラウンドと同一）
MIN_SESSIONS_FOR_BASELINE = 5  # 有効セッションがこれ未満の被験者はスコアしない（LOO で 3 点以下になる）
LONG_PAUSE_MS = 10_000       # M4: 前ラウンドとの接続のため残す
PAUSE_BAND_LO_MS = 10_000    # M7: 計画ポーズ相当の下限
PAUSE_BAND_HI_MS = 120_000   # M7 の上限 / M8 の下限（離席相当）
FLAG_Z = -3.0                # D-2: 主フラグ（片側・bs_rate が低い方向のみ）
SECONDARY_Z = 3.0            # 副次指標の記述用（両側）
N_PERM = 10_000              # 並べ替え回数
PRIMARY_METRIC = "bs_rate"
METRICS = ["bs_rate", "keys_per_min", "enter_rate", "iki_p50", "iki_p90",
           "long_pause_rate_10s", "pause_rate_10_120s", "pause_rate_gt_120s"]
CORRECTION_CATS = {"backspace", "delete"}
# RQ-F / 予測 P-3: bs_rate-low フラグと協調して動くはずの指標と、その予測方向
COHERENCE = {"keys_per_min": +1, "enter_rate": -1}


def session_profile(path: pathlib.Path) -> dict:
    """1 セッションの NDJSON から事前登録した 8 指標を計算する。"""
    ts: list[int] = []
    cats: collections.Counter = collections.Counter()
    task_kind = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        t = o.get("type")
        if t == "session_meta":
            task_kind = o.get("task_kind")
        elif t == "key" and o.get("press") is True:
            ts.append(int(o["t"]))
            cats[o.get("category")] += 1

    n = len(ts)
    if n < MIN_PRESSES:
        return {"n_press": n, "excluded": True}

    ts.sort()
    ikis = [b - a for a, b in zip(ts, ts[1:]) if b >= a]
    if not ikis:
        return {"n_press": n, "excluded": True}

    span_min = (ts[-1] - ts[0]) / 60_000.0
    ikis_sorted = sorted(ikis)

    def pct(p: float) -> float:
        k = min(len(ikis_sorted) - 1, max(0, int(round(p * (len(ikis_sorted) - 1)))))
        return float(ikis_sorted[k])

    return {
        "n_press": n,
        "excluded": False,
        "task_kind": task_kind,
        "span_min": round(span_min, 2),
        "keys_per_min": round(n / span_min, 3) if span_min > 0 else 0.0,
        "iki_p50": pct(0.50),
        "iki_p90": pct(0.90),
        "long_pause_rate_10s": round(
            sum(1 for x in ikis if x > LONG_PAUSE_MS) / len(ikis), 6),
        "pause_rate_10_120s": round(
            sum(1 for x in ikis if PAUSE_BAND_LO_MS < x <= PAUSE_BAND_HI_MS) / len(ikis), 6),
        "pause_rate_gt_120s": round(
            sum(1 for x in ikis if x > PAUSE_BAND_HI_MS) / len(ikis), 6),
        "bs_rate": round(sum(cats[c] for c in CORRECTION_CATS) / n, 6),
        "enter_rate": round(cats["enter"] / n, 6),
    }


def robust_scale(values: list[float]) -> tuple[float, float]:
    med = statistics.median(values)
    mad = statistics.median([abs(v - med) for v in values])
    return med, 1.4826 * mad


def loo_z(sessions: list[dict], metric: str) -> list[float | None]:
    """D-1: leave-one-out 個人基準のロバスト z。scale==0 は None（unscorable）。"""
    out: list[float | None] = []
    for i, s in enumerate(sessions):
        baseline = [o[metric] for j, o in enumerate(sessions) if j != i]
        med, scale = robust_scale(baseline)
        out.append((s[metric] - med) / scale if scale > 0 else None)
    return out


def max_gap_statistic(labels: list[str], values: list[float], scale_cohort: float) -> float:
    """T-1 の統計量: 被験者内の最大ギャップ（コホート尺度で正規化）の平均。"""
    by: dict[str, list[float]] = collections.defaultdict(list)
    for lab, v in zip(labels, values):
        by[lab].append(v)
    gaps = []
    for vs in by.values():
        if len(vs) < 2:
            continue
        vs = sorted(vs)
        gaps.append(max(b - a for a, b in zip(vs, vs[1:])) / scale_cohort)
    return statistics.mean(gaps) if gaps else float("nan")


def permutation_test(labels: list[str], values: list[float], seed: int) -> dict:
    """被験者ラベルを（各被験者のセッション数を保存して）シャッフルする片側検定。"""
    _, scale_cohort = robust_scale(values)
    if scale_cohort <= 0:
        return {"error": "cohort MAD == 0"}
    observed = max_gap_statistic(labels, values, scale_cohort)
    rng = random.Random(seed)
    shuffled = list(labels)
    ge = 0
    for _ in range(N_PERM):
        rng.shuffle(shuffled)
        if max_gap_statistic(shuffled, values, scale_cohort) >= observed:
            ge += 1
    p = (ge + 1) / (N_PERM + 1)
    return {
        "statistic": "mean over participants of (max within-person gap in bs_rate) / cohort robust scale",
        "n_sessions": len(values),
        "n_participants": len(set(labels)),
        "cohort_robust_scale": round(scale_cohort, 6),
        "observed": round(observed, 4),
        "n_permutations": N_PERM,
        "p_value": round(p, 5),
        "alpha": 0.05,
        "one_sided": "larger statistic = more split",
        "significant": p < 0.05,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--derivation-pid", default="P013",
                    help="bs_rate を導出した被験者。主検定 T-1 から除外する（循環回避）")
    ap.add_argument("--out", default="metrics.json")
    a = ap.parse_args()

    root = pathlib.Path(a.dataset).expanduser() / "raw"
    sessions: list[dict] = []
    excluded: list[dict] = []
    for pdir in sorted(root.iterdir()):
        if not pdir.is_dir() or not pdir.name.startswith("P"):
            continue
        if pdir.name == "P000":          # 開発者の動作確認用。較正コホート外
            continue
        # ⚠️ セッション名には日時が入る (P0xx_gse_<YYYYMMDD>_<HHMMSS>.ndjson)。本 repo は
        #    ビルドのため一時 public にする運用があるため、被験者の作業時刻を出力しない。
        #    ファイル名順の安定した連番へ置き換える（前ラウンドと同一の対応になる）。
        for i, f in enumerate(sorted(pdir.glob("*.ndjson")), start=1):
            prof = session_profile(f)
            prof["pid"] = pdir.name
            prof["session"] = f"{pdir.name}-s{i:02d}"
            (excluded if prof["excluded"] else sessions).append(prof)

    by_pid: dict[str, list[dict]] = collections.defaultdict(list)
    for s in sessions:
        by_pid[s["pid"]].append(s)

    # --- D-1: 個人基準 LOO ロバスト z ---
    scored_pids, unscored_pids = [], []
    unscorable_cells = 0
    for pid, ss in sorted(by_pid.items()):
        if len(ss) < MIN_SESSIONS_FOR_BASELINE:
            unscored_pids.append({"pid": pid, "n_sessions": len(ss)})
            continue
        scored_pids.append(pid)
        for m in METRICS:
            for s, z in zip(ss, loo_z(ss, m)):
                s.setdefault("z_within", {})[m] = None if z is None else round(z, 3)
                if z is None:
                    unscorable_cells += 1

    # --- D-2: フラグ規則 ---
    flags, secondary = [], []
    for pid in scored_pids:
        for s in by_pid[pid]:
            zp = s["z_within"][PRIMARY_METRIC]
            if zp is not None and zp < FLAG_Z:
                coh = {m: s["z_within"][m] for m in COHERENCE}
                ok = all(coh[m] is not None and coh[m] * d > 0 for m, d in COHERENCE.items())
                flags.append({
                    "pid": pid, "session": s["session"],
                    "bs_rate": s[PRIMARY_METRIC], "z_within_bs_rate": zp,
                    "coherence_z": coh, "coherence_predicted_direction_met": ok,
                    "is_derivation_set": pid == a.derivation_pid,
                })
            hits = {m: s["z_within"][m] for m in METRICS
                    if m != PRIMARY_METRIC and s["z_within"][m] is not None
                    and abs(s["z_within"][m]) > SECONDARY_Z}
            if hits:
                secondary.append({"pid": pid, "session": s["session"], "z": hits,
                                  "is_derivation_set": pid == a.derivation_pid})

    # --- T-1（主・導出集合を除外） / T-2（サニティ・全体） ---
    held = [s for s in sessions if s["pid"] != a.derivation_pid and s["pid"] in scored_pids]
    allp = [s for s in sessions if s["pid"] in scored_pids]
    t1 = permutation_test([s["pid"] for s in held],
                          [s[PRIMARY_METRIC] for s in held], a.seed)
    t2 = permutation_test([s["pid"] for s in allp],
                          [s[PRIMARY_METRIC] for s in allp], a.seed)

    held_flags = [f for f in flags if not f["is_derivation_set"]]
    deriv_flags = [f for f in flags if f["is_derivation_set"]]

    result = {
        "experiment": "20260802-within-person-scope-detector",
        "preregistered": "preregistration.md",
        "seed": a.seed,
        "derivation_pid_excluded_from_primary_test": a.derivation_pid,
        "n_sessions_included": len(sessions),
        "n_sessions_excluded": len(excluded),
        "excluded_sessions": [{"pid": e["pid"], "session": e["session"],
                               "n_press": e["n_press"]} for e in excluded],
        "participants_scored": {p: len(by_pid[p]) for p in scored_pids},
        "participants_not_scored": unscored_pids,
        "unscorable_cells_scale_zero": unscorable_cells,
        "metrics": METRICS,
        "primary_metric": PRIMARY_METRIC,
        "flag_rule": f"z_within({PRIMARY_METRIC}) < {FLAG_Z} (one-sided)",
        "T1_primary_permutation_test_excluding_derivation": t1,
        "T2_sanity_permutation_test_including_derivation_CIRCULAR": t2,
        "P2_flags_held_out_participants": held_flags,
        "P1_flags_derivation_participant_SANITY_ONLY": deriv_flags,
        "flag_rate_held_out": round(len(held_flags) / len(held), 4) if held else None,
        "P3_coherence_held_out": {
            "n_flags": len(held_flags),
            "n_predicted_direction_met": sum(1 for f in held_flags
                                             if f["coherence_predicted_direction_met"]),
        },
        "secondary_two_sided_hits_DESCRIPTIVE_ONLY": secondary,
        "per_participant_median": {
            pid: {m: round(statistics.median([s[m] for s in ss]), 6) for m in METRICS}
                 | {"n_sessions": len(ss)}
            for pid, ss in sorted(by_pid.items())
        },
        "sessions": [{k: v for k, v in s.items() if k != "excluded"} for s in sessions],
    }
    pathlib.Path(a.out).write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] {a.out} (included={len(sessions)} excluded={len(excluded)} "
          f"T1 p={t1.get('p_value')} held-out flags={len(held_flags)}/{len(held)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
