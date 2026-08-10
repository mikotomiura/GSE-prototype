#!/usr/bin/env python3
"""open-questions-decision-material.md / decisions.md の数値主張を再計算する claim-checker。

`verify-before-claiming` ルール 6（主張を書いたら、それを検査するものを一緒に置く）と
cross-review 指摘 #5（数値主張に再実行コマンドが無い）への対応。

    cd /c/gse-dataset && python <repo>/.steering/20260810-.../verify-claims.py

⚠️ 入力は gse-dataset の metrics/P000/**/*.metrics.json（`range` を除く 31 本）。
⚠️★★ このうち 13 本は gse-dataset で **未コミット（untracked）**なので、
   **commit hash では固定できない**。代わりに入力集合の sha256 を刻む。
   → 実行時ハッシュが下記と違えば、本ドキュメントの数値は再現していない。

期待値（2026-08-10 時点・EXPECTED を参照）。
"""

import glob
import hashlib
import json
import os
import statistics as st
import sys

# Windows の既定コンソールは cp932 で、本ファイルの日本語と em-dash を出力できない。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

EXPECTED = {
    "input_sha16": "665b56cf9a1ea1fd",
    "n_files": 31,
    # F5: 予測クラスの分布（ラベルが付いた時点のセルのみ）
    "windows_pred_pct": (33.7, 42.2, 24.1),
    "macos_pred_pct": (35.2, 42.2, 22.7),
    # Δ の桁を与える最近傍測定（★ ADR-009 D2 とは構成概念が違う）
    "recovery_median_ms": 1005,
    "recovery_p25_ms": 667,
    "recovery_p75_ms": 13179,
    "lead_median_ms": -176,
}
NAMES = ("flow", "incubation", "stuck")


def inputs():
    fs = sorted(
        f.replace(os.sep, "/")
        for f in glob.glob("metrics/P000/*/*.metrics.json")
        if "range" not in f
    )
    h = hashlib.sha256()
    for f in fs:
        h.update(f.encode())
        h.update(open(f, "rb").read())
    return fs, h.hexdigest()[:16]


def confusion(pattern):
    """rows = true label, cols = predicted（per_class.support が行和と一致することで確認済み）。"""
    tot = [[0] * 3 for _ in range(3)]
    n = 0
    for f in sorted(glob.glob(pattern)):
        if "range" in f:
            continue
        m = json.load(open(f)).get("confusion", {}).get("matrix")
        if not m:
            continue
        n += 1
        for i in range(3):
            for j in range(3):
                tot[i][j] += m[i][j]
    return n, tot


def latencies():
    rec, lead = [], []
    for f in sorted(glob.glob("metrics/P000/*/*.metrics.json")):
        if "range" in f:
            continue
        d = json.load(open(f))
        r, l = d.get("stuck_recovery_ms_median"), d.get("detection_lead_ms_median")
        if isinstance(r, (int, float)):
            rec.append(r)
        if isinstance(l, (int, float)):
            lead.append(l)
    return sorted(rec), sorted(lead)


def sessions_needed(d, alloc=0.5):
    """F6 の逆算。対応のある設計・両側 alpha=0.05・検出力 80%。"""
    k = (1.959963985 + 0.841621234) ** 2  # 7.8489
    pairs = k / (d * d)
    return pairs, 2 * pairs / (4 * alloc * (1 - alloc))


def main():
    fails = []
    fs, sha = inputs()
    print(f"input files (non-range): {len(fs)}   sha256[:16] = {sha}")
    if not fs:
        # ★ 検査が「入力ゼロ」で黙って通らないようにする（verify-before-claiming ルール 5b）。
        print("\nRESULT: FAIL - metrics/P000/**/*.metrics.json が 1 本も見つからない。")
        print("  gse-dataset のクローン直下で実行すること: cd /c/gse-dataset && python <this>")
        return 1
    if sha != EXPECTED["input_sha16"]:
        fails.append(
            f"INPUT DRIFT: sha256 {sha} != expected {EXPECTED['input_sha16']} "
            "→ 以下の数値はドキュメントの主張と対応しない"
        )

    print("\n== F5: 予測クラス分布（D16 の根拠）==")
    for os_name, pat, exp in (
        ("windows", "metrics/P000/windows/*.metrics.json", EXPECTED["windows_pred_pct"]),
        ("macos", "metrics/P000/macos/*.metrics.json", EXPECTED["macos_pred_pct"]),
    ):
        n, tot = confusion(pat)
        N = sum(sum(r) for r in tot)
        cols = [sum(tot[i][j] for i in range(3)) for j in range(3)]
        pct = tuple(round(100 * c / N, 1) for c in cols)
        print(f"  {os_name:<8} sessions={n:>2} cells={N:>3}  predicted {dict(zip(NAMES, pct))}")
        if pct != exp:
            fails.append(f"F5 {os_name}: {pct} != expected {exp}")
        if not (pct[1] > pct[2]):
            fails.append(f"F5 {os_name}: Incubation({pct[1]}%) が Stuck({pct[2]}%) を上回っていない → D16 の前提が崩れる")

    print("\n== Δ の桁を与える最近傍測定（★ ADR-009 D2 とは別構成概念）==")
    rec, lead = latencies()
    got = {
        "recovery_median_ms": st.median(rec),
        "recovery_p25_ms": rec[len(rec) // 4],
        "recovery_p75_ms": rec[3 * len(rec) // 4],
        "lead_median_ms": st.median(lead),
    }
    print(f"  stuck_recovery_ms_median: n={len(rec)} min={rec[0]} p25={got['recovery_p25_ms']} "
          f"median={got['recovery_median_ms']} p75={got['recovery_p75_ms']} max={rec[-1]}")
    print(f"  detection_lead_ms_median: n={len(lead)} median={got['lead_median_ms']}")
    for k, v in got.items():
        if v != EXPECTED[k]:
            fails.append(f"{k}: {v} != expected {EXPECTED[k]}")

    print("\n== F6: 必要セッション数の逆算（50/50・両側a=.05・検出力80%）==")
    print("   d    pairs   総セッション   /人(n=5)   /人(n=3)   70/30 総数")
    for d in (0.8, 0.5, 0.3):
        pairs, tot50 = sessions_needed(d, 0.5)
        _, tot70 = sessions_needed(d, 0.7)
        print(f" {d:.1f}   {pairs:6.1f}   {tot50:10.1f}   {tot50/5:8.1f}   {tot50/3:8.1f}   {tot70:10.1f}")
    ratio = (1 / (4 * 0.7 * 0.3))
    print(f"  70/30 の相対効率 = {ratio:.3f}  (= 19% 多いセッションが要る)")
    if abs(ratio - 1.190) > 0.001:
        fails.append(f"F6 allocation ratio {ratio} != 1.190")

    print()
    if fails:
        print("RESULT: FAIL")
        for f in fails:
            print("  -", f)
        return 1
    print("RESULT: PASS — ドキュメントの数値主張はすべて再現した")
    return 0


if __name__ == "__main__":
    sys.exit(main())
