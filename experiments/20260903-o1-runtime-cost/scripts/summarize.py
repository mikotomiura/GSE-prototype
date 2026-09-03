#!/usr/bin/env python3
"""results/ の samples.tsv をまとめ、README の判定表に照らす。

⚠️★★★ 「測れていない」を「合格」と読ませない。
★ 行が足りない / 対照が無い / 列が空 のときは **判定しない** (DataInsufficient)。
  memory: silent-success-is-not-visible / 成功は肯定形で、根拠は実測。
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
RESULTS = HERE / "results"

# ★ README の判定表。⚠️ 測った後に動かさない。
THRESHOLDS = {
    "cpu_mean_pct": (1.0, 3.0),
    "cpu_max_pct": (15.0, 30.0),
    "rss_slope_mb_per_h": (5.0, 20.0),
    "rss_final_mb": (300.0, None),
    "battery_drop_pt_per_8h": (5.0, 10.0),
    "ndjson_mb_per_day": (30.0, 48.0),
}
# ★ 8 時間ぶんを埋めるのに要る最小サンプル数 (間隔 30s の 8h = 960)。
#   ⚠️ 半分を切ったら「測れていない」とみなす。
MIN_SAMPLES = 480


def load(run: str):
    d = RESULTS / run
    tsv = d / "samples.tsv"
    if not tsv.is_file():
        return None
    rows = []
    for i, line in enumerate(tsv.read_text().splitlines()):
        if i == 0 or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        try:
            rows.append(
                {
                    "t": int(parts[0]),
                    "cpu": float(parts[1] or 0),
                    "rss_kb": float(parts[2] or 0),
                    "threads": int(float(parts[3] or 0)),
                    "batt": float(parts[4]) if parts[4].strip() else None,
                }
            )
        except ValueError:
            continue
    meta = {}
    if (d / "meta.json").is_file():
        meta = json.loads((d / "meta.json").read_text())
    return {"rows": rows, "meta": meta, "dir": d}


def slope_mb_per_h(rows) -> float | None:
    """RSS の傾き (最小二乗)。⚠️ 2 点未満なら None (★ 0 と書かない)。"""
    pts = [(r["t"], r["rss_kb"] / 1024.0) for r in rows if r["rss_kb"] > 0]
    n = len(pts)
    if n < 2:
        return None
    t0 = pts[0][0]
    xs = [(t - t0) / 3600.0 for t, _ in pts]
    ys = [y for _, y in pts]
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def battery_drop_per_8h(rows) -> float | None:
    pts = [(r["t"], r["batt"]) for r in rows if r["batt"] is not None]
    if len(pts) < 2:
        return None
    hours = (pts[-1][0] - pts[0][0]) / 3600.0
    if hours <= 0:
        return None
    return (pts[0][1] - pts[-1][1]) / hours * 8.0


def ndjson_mb_per_day(run_dir: pathlib.Path) -> float | None:
    tsv = run_dir / "ndjson-size.tsv"
    if not tsv.is_file():
        return None
    total = 0
    n = 0
    for i, line in enumerate(tsv.read_text().splitlines()):
        if i == 0 or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        try:
            total += int(parts[1])
            n += 1
        except ValueError:
            continue
    if n == 0:
        return None
    # ★ 1 ファイル = 1 日 (ROTATE_AFTER_MS = 24h)。⚠️ 平均を採る。
    return total / n / (1024 * 1024)


def verdict(name: str, value):
    good, bad = THRESHOLDS[name]
    if value is None:
        return "DataInsufficient", "⚠️ 測れていない"
    if value < good:
        return "PASS", "★ 合格"
    if bad is not None and value >= bad:
        return "FAIL", "⚠️ 要対処"
    return "MARGINAL", "⚠️ 判定表の合格域を外れている"


def main() -> int:
    with_gse = load("with-gse")
    without = load("without-gse")
    if with_gse is None:
        print("⚠️ results/with-gse/samples.tsv が無い。★ まだ測っていない。")
        return 1
    rows = with_gse["rows"]
    print(f"★ サンプル数: {len(rows)} (最小 {MIN_SAMPLES})")
    # ⚠️★★★ **サンプルが足りないなら 1 指標も PASS にしない。**
    #   ★ 2026-09-03 に自分の測定器で実測した欠陥: 100 サンプルでも個別欄が PASS と出た
    #     (★ 総合が FAIL になったのは *別の理由* で、たまたま隠れていただけである)。
    #   → ⚠️ memory `measurement-instrument-false-positives` と同型。
    enough = len(rows) >= MIN_SAMPLES
    if not enough:
        print("⚠️★★★ サンプルが足りない。**1 指標も判定しない**（★ 短時間の観測で「軽い」と言わない）。")
    cpus = [r["cpu"] for r in rows]
    metrics = {
        "cpu_mean_pct": (sum(cpus) / len(cpus)) if cpus else None,
        "cpu_max_pct": max(cpus) if cpus else None,
        "rss_slope_mb_per_h": slope_mb_per_h(rows),
        "rss_final_mb": (rows[-1]["rss_kb"] / 1024.0) if rows else None,
        "battery_drop_pt_per_8h": battery_drop_per_8h(rows),
        "ndjson_mb_per_day": ndjson_mb_per_day(with_gse["dir"]),
    }
    print()
    worst = "PASS"
    order = {"PASS": 0, "MARGINAL": 1, "DataInsufficient": 2, "FAIL": 3}
    for k, v in metrics.items():
        v_, why = verdict(k, v) if enough else ("DataInsufficient", "⚠️ サンプル不足")
        shown = "—" if v is None else f"{v:.2f}"
        print(f"  {k:26s} {shown:>10s}  {v_:<16s} {why}")
        if order[v_] > order[worst]:
            worst = v_
    print()
    # ⚠️★★★ 対照が無ければバッテリーの結論は出せない。
    if not enough:
        worst = "DataInsufficient" if worst != "FAIL" else worst
    if without is None or len(without["rows"]) < MIN_SAMPLES:
        print("⚠️★★ 対照 (without-gse) が無い/足りない → **バッテリーの増分は判定できない**。")
        if worst in ("PASS", "MARGINAL"):
            worst = "DataInsufficient"
    else:
        b_with = battery_drop_per_8h(rows)
        b_without = battery_drop_per_8h(without["rows"])
        if b_with is not None and b_without is not None:
            print(f"★ バッテリー消費の増分: {b_with - b_without:.2f} pt/8h "
                  f"(with={b_with:.2f} / without={b_without:.2f})")
        else:
            print("⚠️ バッテリーの値が取れていない → 増分は判定できない。")
            worst = "DataInsufficient"
    print()
    print(f"総合: {worst}")
    if worst != "PASS":
        print("⚠️ ★ notes.md に、どの指標がなぜ外れたかを書くこと。")
    return 0 if worst == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
