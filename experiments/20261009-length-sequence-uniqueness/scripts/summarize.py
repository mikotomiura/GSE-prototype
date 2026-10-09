"""Tables of the results as Markdown (no new numbers are computed here except formatting).

  summarize.py --results results --out results/summary.md
"""
import argparse
import json
import os
import sys

DEF_LABEL = {
    "B0": "B0 読点・句点と改行",
    "B1": "B1 B0＋確定の Enter（文ごと）",
    "B2": "B2 B0＋確定の Enter（文節ごと）",
    "B3": "B3 読点・句点だけ（Enter を捨てる）",
}
COND_ORDER = ["ideal", "weak", "mid", "strong", "ruby_only", "habit_only", "bs_only", "shift_only"]
K1_SHOW = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]


def pct(x, digits=1):
    return "—" if x is None else ("%.*f" % (digits, 100 * x))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    stats = json.load(open(os.path.join(a.results, "corpus_stats.json"), encoding="utf-8"))
    uniq = json.load(open(os.path.join(a.results, "uniqueness.json"), encoding="utf-8"))
    match = json.load(open(os.path.join(a.results, "matching.json"), encoding="utf-8"))
    L = []
    L.append("# 結果の表（自動生成・`scripts/summarize.py`）")
    L.append("")
    L.append("数値は `results/*.json` から写しただけ。割合は % で、[ ] は 95% の区間（正解の作品を単位にした百分位のブートストラップ）。")
    L.append("")
    L.append("## コーパス")
    L.append("")
    L.append("作品 %d（参照 %d）。r̄（書き手の読みの単位あたりの標準の打鍵数）= %.4f。落とした作品 %d。"
             % (stats["n_corpus"], stats["n_reference"], stats["r_bar"], len(stats["dropped"])))
    L.append("")
    L.append("| 区切り | 区間 | 有効 | 有効のうち長さ 0 | 有効な区間の平均打鍵数 | 書き手の読みが違う区間 |")
    L.append("|---|---|---|---|---|---|")
    for name, d in stats["corpus_by_definition"].items():
        L.append("| %s | %d | %s%% | %d | %.1f | %s%% |" % (
            DEF_LABEL[name], d["segments"], pct(d["valid_fraction"]), d["zero_length_valid"],
            d["mean_keys_valid"], pct(d["writer_reading_differs_fraction_valid"])))
    L.append("")
    L.append("## 指標 1: k 個の長さの並びが、コーパスの中で 1 回だけ現れる窓の割合（%）")
    L.append("")
    by = {}
    for r in uniq["results"]:
        by.setdefault(r["definition"], []).append(r)
    for name in DEF_LABEL:
        rows = by.get(name, [])
        if not rows:
            continue
        L.append("### %s" % DEF_LABEL[name])
        L.append("")
        L.append("| k | " + " | ".join("%s（%d 作品）" % (r["corpus"], r["works"]) for r in rows) + " |")
        L.append("|---|" + "---|" * len(rows))
        for k in K1_SHOW:
            cells = []
            for r in rows:
                e = next((x for x in r["by_k"] if x["k"] == k), None)
                cells.append("—" if e is None or e["windows"] == 0 else "%s（%d 窓）" % (pct(e["unique_fraction"]), e["windows"]))
            L.append("| %d | %s |" % (k, " | ".join(cells)))
        L.append("")
    L.append("## 指標 2: 候補 N 本からの照合の正答率（%）と偶然の水準 1/N")
    L.append("")
    cells = match["cells"]
    for name in DEF_LABEL:
        for N in match["config"]["N"]:
            sub = [c for c in cells if c["definition"] == name and c["N"] == N]
            if not sub:
                continue
            L.append("### %s・N = %d（偶然の水準 %s%%）" % (DEF_LABEL[name], N, pct(1.0 / N, 2)))
            L.append("")
            L.append("| k | 使える作品 | " + " | ".join(COND_ORDER) + " |")
            L.append("|---|---|" + "---|" * len(COND_ORDER))
            for c in sorted(sub, key=lambda c: c["k"]):
                if c["status"] != "ok":
                    L.append("| %d | %d | %s |" % (c["k"], c["eligible_works"], " | ".join(["計算不能"] * len(COND_ORDER))))
                    continue
                vals = []
                for cond in COND_ORDER:
                    r = c["results"][cond]
                    vals.append("%s [%s, %s]" % (pct(r["acc"]), pct(r["ci"][0]), pct(r["ci"][1])))
                L.append("| %d | %d | %s |" % (c["k"], c["eligible_works"], " | ".join(vals)))
            L.append("")
    L.append("## 診断（理想の条件の試行で、情報を使わない予測）")
    L.append("")
    L.append("| 区切り | k | N | 無作為の予測 | 窓の数がいちばん多い作品を選ぶ予測 | 正解の位置の偏り（z） |")
    L.append("|---|---|---|---|---|---|")
    for c in cells:
        if c["status"] != "ok":
            continue
        d = c["diagnostics"]
        L.append("| %s | %d | %d | %s [%s, %s] | %s [%s, %s] | %.2f |" % (
            c["definition"], c["k"], c["N"],
            pct(d["random_predictor"]["acc"], 2), pct(d["random_predictor"]["ci"][0], 2),
            pct(d["random_predictor"]["ci"][1], 2),
            pct(d["max_windows_predictor"]["acc"], 2), pct(d["max_windows_predictor"]["ci"][0], 2),
            pct(d["max_windows_predictor"]["ci"][1], 2), d["true_index_z"]))
    L.append("")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
