#!/usr/bin/env python3
"""content-free な打鍵署名でセッションが分離するかを検証する。

事前登録: preregistration.md（結果を見る前に凍結済み）
出力: metrics.json（集計値のみ。raw NDJSON は一切コピーしない）
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
MIN_PRESSES = 200          # これ未満のセッションは統計が不安定なため除外
LONG_PAUSE_MS = 10_000     # M4: 計画ポーズのしきい値
OUTLIER_Z = 3.0            # 外れ値の定義
N_PERM = 10_000            # 並べ替え回数
METRICS = ["keys_per_min", "iki_p50", "iki_p90",
           "long_pause_rate_10s", "bs_rate", "enter_rate"]
CORRECTION_CATS = {"backspace", "delete"}


def session_profile(path: pathlib.Path) -> dict | None:
    """1 セッションの NDJSON から事前登録した 6 指標を計算する。"""
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
        "bs_rate": round(
            sum(cats[c] for c in CORRECTION_CATS) / n, 6),
        "enter_rate": round(cats["enter"] / n, 6),
    }


def robust_z(values: list[float]) -> tuple[list[float | None], float, float]:
    med = statistics.median(values)
    mad = statistics.median([abs(v - med) for v in values])
    if mad == 0:
        return [None] * len(values), med, 0.0
    scale = 1.4826 * mad
    return [(v - med) / scale for v in values], med, scale


def profile_vector(s: dict, stats: dict) -> list[float]:
    """ロバスト z 化したプロファイルベクトル（距離計算用）。"""
    out = []
    for m in METRICS:
        med, scale = stats[m]
        out.append((s[m] - med) / scale if scale > 0 else 0.0)
    return out


def mean_pair_distance(idx_a: list[int], idx_b: list[int], vecs) -> float:
    tot, cnt = 0.0, 0
    for i in idx_a:
        for j in idx_b:
            if i == j:
                continue
            tot += math.dist(vecs[i], vecs[j])
            cnt += 1
    return tot / cnt if cnt else float("nan")


def within_between_ratio(labels: list[str], vecs) -> float:
    by = collections.defaultdict(list)
    for i, lab in enumerate(labels):
        by[lab].append(i)
    within, between = [], []
    for lab, idx in by.items():
        if len(idx) > 1:
            within.append(mean_pair_distance(idx, idx, vecs))
        others = [i for i, l in enumerate(labels) if l != lab]
        if others:
            between.append(mean_pair_distance(idx, others, vecs))
    w = statistics.mean([x for x in within if not math.isnan(x)])
    b = statistics.mean([x for x in between if not math.isnan(x)])
    return w / b if b > 0 else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default="metrics.json")
    a = ap.parse_args()

    root = pathlib.Path(a.dataset).expanduser() / "raw"
    sessions, excluded = [], []
    for pdir in sorted(root.iterdir()):
        if not pdir.is_dir() or not pdir.name.startswith("P"):
            continue
        if pdir.name == "P000":          # 開発者の動作確認用。較正コホート外
            continue
        # ⚠️ セッション名には日時が入る (P0xx_gse_<YYYYMMDD>_<HHMMSS>.ndjson)。本 repo は
        #    ビルドのため一時 public にする運用があるため、被験者の作業時刻を出力しない。
        #    ファイル名順の安定した連番へ置き換える (対応表は repo に残さない)。
        for i, f in enumerate(sorted(pdir.glob("*.ndjson")), start=1):
            prof = session_profile(f)
            if prof is None:
                continue
            prof["pid"] = pdir.name
            prof["session"] = f"{pdir.name}-s{i:02d}"
            prof.pop("path", None)
            (excluded if prof["excluded"] else sessions).append(prof)

    if len(sessions) < 4:
        print(f"[ERROR] 有効セッションが少なすぎます: {len(sessions)}", file=sys.stderr)
        return 1

    # --- ロバスト z 化 ---
    stats, zs = {}, {}
    for m in METRICS:
        vals = [s[m] for s in sessions]
        z, med, scale = robust_z(vals)
        stats[m] = (med, scale)
        zs[m] = z

    outliers = []
    for i, s in enumerate(sessions):
        hits = {m: round(zs[m][i], 2) for m in METRICS
                if zs[m][i] is not None and abs(zs[m][i]) > OUTLIER_Z}
        if hits:
            outliers.append({"pid": s["pid"], "session": s["session"], "z": hits})

    # --- 並べ替え検定（被験者ラベル） ---
    vecs = [profile_vector(s, stats) for s in sessions]
    labels = [s["pid"] for s in sessions]
    observed = within_between_ratio(labels, vecs)
    rng = random.Random(a.seed)
    shuffled = list(labels)
    ge = 0
    for _ in range(N_PERM):
        rng.shuffle(shuffled)
        if within_between_ratio(shuffled, vecs) <= observed:
            ge += 1
    p_value = (ge + 1) / (N_PERM + 1)   # 小さいほど「被験者に沿って分離」

    per_pid = {}
    for s in sessions:
        per_pid.setdefault(s["pid"], []).append(s)
    pid_summary = {
        pid: {m: round(statistics.median([s[m] for s in ss]), 4) for m in METRICS}
        | {"n_sessions": len(ss)}
        for pid, ss in sorted(per_pid.items())
    }

    expected_false = len(sessions) * len(METRICS) * 0.0027  # |z|>3 の素朴な期待件数

    result = {
        "experiment": "20260802-task-scope-detector",
        "preregistered": "preregistration.md",
        "seed": a.seed,
        "n_sessions_included": len(sessions),
        "n_sessions_excluded": len(excluded),
        "excluded_sessions": [{"pid": e.get("pid"), "session": e.get("session"),
                               "n_press": e["n_press"]} for e in excluded],
        "metrics": METRICS,
        "robust_center_scale": {m: {"median": round(stats[m][0], 4),
                                    "scale": round(stats[m][1], 4)} for m in METRICS},
        "per_participant_median": pid_summary,
        "outliers_z_gt_3": outliers,
        "expected_outlier_cells_by_chance": round(expected_false, 2),
        "permutation_test": {
            "statistic": "mean_within_pid_distance / mean_between_pid_distance",
            "observed": round(observed, 4),
            "n_permutations": N_PERM,
            "p_value": round(p_value, 5),
            "alpha": 0.05,
            "significant": p_value < 0.05,
        },
        "sessions": [{k: v for k, v in s.items() if k != "excluded"} for s in sessions],
    }
    pathlib.Path(a.out).write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] {a.out} を書き出しました "
          f"(included={len(sessions)} excluded={len(excluded)} p={p_value:.5f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
