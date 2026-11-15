"""合成の対照の集計（results/controls/ の組ごとの summary から、λ ごとの判定の数と時間を表にする）。

  S2（陰性・λ = 0）: 「満たさない」の組が 1 組以下であること（20 組のうち）。
  S3（陽性）: B_state・B_pixel ごとに、80% 以上の組で「満たさない」が出る最小の λ。
使い方: python report.py <results/controls>（markdown を標準出力へ）
"""
import glob
import json
import os
import sys
from collections import defaultdict


def main(root):
    rows = []
    for sub in ("graded", "null"):
        p = os.path.join(root, sub, "controls.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                rows.extend(json.load(f))
    by_lam = defaultdict(list)
    for r in rows:
        by_lam[r["lam"]].append(r)
    out = ["# 合成の対照の集計", "", "| λ | 組 | 全体: 満たさない | T1 状態 | T1 画素 | T2 状態 | T2 画素 |", "|---|---|---|---|---|---|---|"]
    detect = {"state": None, "pixel": None}
    for lam in sorted(by_lam):
        rs = by_lam[lam]
        n = len(rs)

        def cnt(t, b):
            return sum(1 for r in rs if r[t][b] == "fails")

        out.append(f"| {lam} | {n} | {sum(1 for r in rs if r['overall'] == 'fails')} | "
                   f"{cnt('T1', 'state')} | {cnt('T1', 'pixel')} | {cnt('T2', 'state')} | {cnt('T2', 'pixel')} |")
        for b in detect:
            hit = sum(1 for r in rs if r["T1"][b] == "fails" or r["T2"][b] == "fails")
            if lam > 0 and detect[b] is None and hit >= 0.8 * n:
                detect[b] = lam
    null = by_lam.get(0.0, [])
    null_fail = sum(1 for r in null if r["overall"] == "fails")
    out += ["", "（各マスは「満たさない」の組の数）", "",
            f"- S2（陰性）: λ = 0 の {len(null)} 組のうち、全体が「満たさない」は {null_fail} 組（1 組以下が合格）"
            f" → {'合格' if null_fail <= 1 else '不合格'}",
            f"- S3（陽性）: 80% 以上の組で「満たさない」になる最小の λ: 状態 {detect['state']}・画素 {detect['pixel']}"]
    t = [r["timing"] for r in rows if "timing" in r]
    if t:
        keys = sorted({k for x in t for k in x})
        out += ["", "時間（組あたりの平均・秒）: " + "・".join(
            f"{k} {sum(x.get(k, 0) for x in t) / len(t):.0f}" for k in keys if k.split("_")[0] in ("synth", "replay", "pixels", "stats") and k.endswith(("_s", "_s_0.0")))]
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
