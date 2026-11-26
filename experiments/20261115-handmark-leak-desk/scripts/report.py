"""合成の対照の集計（results/controls/ の組ごとの summary から、λ ごとの判定の数と時間を表にする）。

  S2（陰性・λ = 0）: 「満たさない」の組が 1 組以下であること（20 組のうち）。組の数が足りないか、
                     全部が判定不能なら不合格（空の合格にしない）。
  S3（陽性）: B_state・B_pixel ごとに、80% 以上の組で「満たさない」が出る最小の λ。
  S5（引き直しの方式・判断 13）: λ = 0 の固定の予測の 90% 区間が、同じ日数の推定の組の平均を含む割合
                     （基準 0.85）。120 日の合成の差は参考として並べる。
使い方: python report.py <results/controls>（markdown を標準出力へ）。S2 が不合格なら終了コード 1。
"""
import json
import math
import os
import statistics
import sys
from collections import defaultdict

EXPECTED_NULL = 20
COVER_MIN = 0.85
B = ("state", "pixel")
T = ("T1", "T2")


def load(root, sub):
    p = os.path.join(root, sub, "controls.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main(root):
    rows = load(root, "graded") + load(root, "null")
    by_lam = defaultdict(list)
    for r in rows:
        by_lam[r["lam"]].append(r)
    out = ["# 合成の対照の集計", "", "| λ | 組 | 全体: 満たさない | T1 状態 | T1 画素 | T2 状態 | T2 画素 |",
           "|---|---|---|---|---|---|---|"]
    detect = {b: None for b in B}
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
    null_meets = sum(1 for r in null if r["overall"] == "meets")
    s2_ok = len(null) >= EXPECTED_NULL and null_meets > 0 and null_fail <= 1
    out += ["", "（各マスは「満たさない」の組の数）", "",
            f"- S2（陰性）: λ = 0 の {len(null)} 組（{EXPECTED_NULL} 組以上のはず）のうち、全体が「満たさない」は "
            f"{null_fail} 組・「満たす」は {null_meets} 組（1 組以下かつ満たすが 1 組以上で合格） → "
            f"{'合格' if s2_ok else '不合格'}",
            f"- S3（陽性）: 80% 以上の組で「満たさない」になる最小の λ: 状態 {detect['state']}・画素 {detect['pixel']}"]
    # λ = 0 の差の分布（画素の学習器が弱いと「満たす」に寄るので、差の向きを見る）
    out += ["", "λ = 0 の差 AUC(B) − AUC(A)（組の平均・SD・最小・最大）:"]
    means = {}
    for t in T:
        for b in B:
            d = [r["auc"][t][b] - r["auc"][t]["A"] for r in null
                 if r.get("auc", {}).get(t, {}).get(b) is not None]
            if len(d) >= 2:
                means[(t, b)] = statistics.mean(d)
                out.append(f"  - {t} {b}: {statistics.mean(d):+.4f}・{statistics.stdev(d):.4f}・"
                           f"{min(d):+.4f}・{max(d):+.4f}（{len(d)} 組）")
    # S5
    truth = None
    tp = os.path.join(root, "truth", "controls.json")
    if os.path.exists(tp):
        with open(tp, encoding="utf-8") as f:
            truth = json.load(f)[0]["truth"]
    out += ["", f"- S5（引き直しの方式・判断 13）: 固定の予測の 90% 区間が含む割合（基準 {COVER_MIN}）"]
    for t in T:
        for b in B:
            cis = [r["ci90"][t][b] for r in null if r.get("ci90", {}).get(t, {}).get(b)]
            if not cis or (t, b) not in means:
                out.append(f"  - {t} {b}: 区間が無い")
                continue
            m = means[(t, b)]
            cover = sum(1 for lo, hi in cis if lo <= m <= hi)
            width = statistics.mean(hi - lo for lo, hi in cis)
            line = (f"  - {t} {b}: 同じ日数の推定の平均 {m:+.4f} を含む {cover}/{len(cis)}"
                    f"（{'基準以上' if cover >= COVER_MIN * len(cis) else '基準未満'}）・区間の幅の平均 {width:.4f}")
            if truth and b in truth.get(t, {}):
                v = truth[t][b]
                c2 = sum(1 for lo, hi in cis if lo <= v <= hi)
                line += f"・参考: 120 日の合成の差 {v:+.4f} を含む {c2}/{len(cis)}"
            out.append(line)
    nc = [r.get("newton_nonconverged") for r in rows if r.get("newton_nonconverged") is not None]
    if nc:
        out += ["", f"ニュートン法が収束しなかった回数: 合計 {sum(nc)}（{len(nc)} 行）"]
    tm = [r["timing"] for r in rows if "timing" in r]
    if tm:
        keys = sorted({k for x in tm for k in x})
        out += ["", "時間（組あたりの平均・秒）: " + "・".join(
            f"{k} {sum(x.get(k, 0) for x in tm) / len(tm):.0f}" for k in keys
            if k.split("_")[0] in ("synth", "replay", "pixels", "stats") and k.endswith(("_s", "_s_0.0")))]
    print("\n".join(out))
    return 0 if s2_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
