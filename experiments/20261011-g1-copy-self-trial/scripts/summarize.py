"""Tables (results/summary.md) from crosscheck.json, matching.json and the earlier experiments' results.

  summarize.py --crosscheck results/crosscheck.json --matching results/matching.json --corpus-stats
               results/corpus_g1_stats.json --out results/summary.md
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_config, read_json, repo_path, sha256_file  # noqa: E402


def pct(v, digits=1):
    return "—" if v is None else ("%.*f" % (digits, 100 * v))


def prior_values(cfg):
    pc = cfg["prior_comparison"]
    out = {}
    u, p = pc["uniqueness"], pc["prototype"]
    if sha256_file(repo_path(u["path"])) != u["sha256"] or sha256_file(repo_path(p["path"])) != p["sha256"]:
        raise SystemExit("summarize: an earlier result does not match config.json")
    for c in read_json(repo_path(u["path"]))["cells"]:
        if c["definition"] == u["definition"] and c.get("status") == "ok":
            for cond in u["conditions"]:
                out[("B0_" + cond, c["k"], c["N"])] = c["results"][cond]["acc"]
    for c in read_json(repo_path(p["path"]))["cells"]:
        for v in p["variants"]:
            out[("proto_" + v, c["k"], c["N"])] = c["results"][v]["acc"]
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--crosscheck", required=True)
    ap.add_argument("--matching", required=True)
    ap.add_argument("--corpus-stats", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--explore", default=None, help="results/explore_align.json (post-hoc; notes.md 逸脱 3)")
    a = ap.parse_args(argv)
    cfg = load_config()
    cc = read_json(a.crosscheck)["blocks"]
    mm = read_json(a.matching)
    cs = read_json(a.corpus_stats)
    cells = {(c["group"], c["variant"], c["k"], c["N"]): c for c in mm["cells"]}
    ks, Ns = cfg["matching"]["k"], cfg["matching"]["N"]
    copy_blocks = cfg["records"]["copy_blocks"]
    prior = prior_values(cfg)
    L = []
    w = L.append
    w("# 表（研究者本人の G1 の書き写し・自動生成）")
    w("")
    w("`scripts/summarize.py` が `results/*.json` から作る。読み方と限界は `notes.md`。値は % で、偶然の水準は 1/N。")
    w("")
    w("## 1. 照らし合わせ（記録 ↔ 原文から合成した区間）")
    w("")
    w("原文は %d 区間（標準の打鍵数の合計 %d）。おとりのコーパスは %d 作品・%d 区間（有効 %.1f%%・有効な区間の中央値 %s 打）。"
      % (cs["copy_segments"], cs["copy_keys_total"], cs["works"], cs["segments"], 100 * cs["valid_fraction"],
         cs["median_valid"]))
    w("")
    w("| ブロック | 記録 | 区間 | 揃えの組 | 揃った原文の位置 | 組の差の絶対値の和 | 記録の打鍵数 | 揃った原文の打鍵数 |")
    w("|---|---|---|---|---|---|---|---|")
    for lab in copy_blocks:
        for rk in ("plain", "clean"):
            b = cc[lab][rk]
            g = "・".join("%s %d" % kv for kv in b["groups"].items())
            w("| %s | %s | %d | %s | %d / %d | %d | %d | %d |" % (lab, rk, b["segments"], g, b["text_reached"],
              b["text_segments"], b["sum_abs_group_diff"], b["record_keys"], b["text_keys_aligned"]))
    w("")
    w("### 1 対 1 の組の差（記録 − 合成・plain）")
    w("")
    w("| ブロック | 種類 | 組 | 一致 | 平均 | 絶対値の平均 | 最小 | 最大 |")
    w("|---|---|---|---|---|---|---|---|")
    names = {"all": "すべて", "no_bs_no_num": "BS も数字も無い", "bs": "BS あり", "num": "数字あり"}
    for lab in copy_blocks:
        for c, nm in names.items():
            d = cc[lab]["plain"]["one_to_one"][c]
            if d["n"] == 0:
                w("| %s | %s | 0 | — | — | — | — | — |" % (lab, nm))
                continue
            w("| %s | %s | %d | %d | %+.2f | %.2f | %d | %d |" % (lab, nm, d["n"], d["exact"], d["mean"], d["mean_abs"],
              d["min"], d["max"]))
    w("")
    w("### 区間あたりの押下（plain）と癖の当てはめ（探索）")
    w("")
    w("| ブロック | Enter | Space | BackSpace | 数字 | 最良の癖 | 差の絶対値の和（最良） | 一致（最良） |")
    w("|---|---|---|---|---|---|---|---|")
    for lab in copy_blocks:
        b = cc[lab]["plain"]
        ps, hf = b["per_segment"], b["explore_habit_fit"]
        hs = "—" if hf is None else ("・".join(hf["habits"]) or "なし（標準）")
        w("| %s | %.2f | %.2f | %.2f | %.2f | %s | %s | %s |" % (lab, ps["enter"], ps["space"], ps["backspace"],
          ps["numeric"], hs, "—" if hf is None else hf["sum_abs"], "—" if hf is None else "%d / %d" % (hf["exact"], hf["n"])))
    w("")
    w("## 2. 照合（N = 1,000・L_none と L_clean）")
    w("")
    w("全体はブロックの平均（窓のあるブロックだけ）。[ ] はブロックの最小〜最大。± はモンテカルロの標準誤差（抽選の揺れだけ）。"
      "前の実測の値は条件が違うので同じ量ではない（notes.md）。")
    w("")
    w("| k | L_none 全体 | [最小, 最大] | ± | P009 | P010 | L_clean 全体 | 前の実測 B0 理想 | 前の実測 B0 強 | 前の試作 L |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for k in ks:
        c = cells[("main", "L_none", k, 1000)]["overall"]
        cl = cells[("main", "Lclean_none", k, 1000)]["overall"]
        if c["acc"] is None:
            w("| %d | — | | | | | %s | | | |" % (k, pct(cl["acc"])))
            continue
        w("| %d | %s | [%s, %s] | %s | %s | %s | %s | %s | %s | %s |" % (k, pct(c["acc"]), pct(c["min"]), pct(c["max"]),
          pct(c["mc_se"], 2), pct(c["P009"]), pct(c["P010"]), pct(cl["acc"]), pct(prior.get(("B0_ideal", k, 1000))),
          pct(prior.get(("B0_strong", k, 1000))), pct(prior.get(("proto_L_none", k, 1000)))))
    w("")
    w("### ブロックごと（L_none）")
    w("")
    w("| N | k | " + " | ".join(copy_blocks) + " |")
    w("|---|---|" + "---|" * len(copy_blocks))
    for N in Ns:
        for k in ks:
            bl = cells[("main", "L_none", k, N)]["blocks"]
            w("| %d | %d | " % (N, k) + " | ".join("%s (%d 窓)" % (pct(bl[lab]["acc"]), bl[lab]["windows"]) for lab in copy_blocks) + " |")
    w("")
    w("## 3. 加工（全体・全セル）")
    w("")
    for N in Ns:
        w("### N = %d（偶然の水準 %s%%）" % (N, pct(1.0 / N, 2)))
        w("")
        w("| 変種 | " + " | ".join("k = %d" % k for k in ks) + " |")
        w("|---|" + "---|" * len(ks))
        for v in cfg["variants"]:
            w("| %s | " % v + " | ".join(pct(cells[("main", v, k, N)]["overall"]["acc"], 2) for k in ks) + " |")
        w("")
    w("## 4. 診断")
    w("")
    w("記録を使わない予測（書き写しのブロック）と、陰性対照（書き写し以外の 16 ブロックの記録・正解は原文の同じ番号の窓・L_none）。")
    w("")
    w("| N | 偶然 | 診断 | " + " | ".join("k = %d" % k for k in ks) + " |")
    w("|---|---|---|" + "---|" * len(ks))
    for N in Ns:
        for grp, v, nm in (("diagnostic", "no_record", "記録を使わない"), ("control", "L_none", "陰性対照")):
            row = []
            for k in ks:
                o = cells[(grp, v, k, N)]["overall"]
                row.append("—" if o["acc"] is None else "%s [%s, %s] (%d)" % (pct(o["acc"], 2), pct(o["min"], 2),
                                                                           pct(o["max"], 2), o["n_blocks"]))
            w("| %d | %s | %s | " % (N, pct(1.0 / N, 2), nm) + " | ".join(row) + " |")
    w("")
    w("陰性対照の ( ) は窓のあるブロックの数。")
    w("")
    if a.explore:
        ex = read_json(a.explore)
        ec = {(c["variant"], c["k"], c["N"]): c for c in ex["cells"]}
        w("## 5. 事後の探索: 区切りの乱れと、それを許す攻撃者（事前の固定に無い・notes.md 逸脱 3）")
        w("")
        w("1 窓あたり %d 回の抽選（本計算と同じ種の最初の %d 回）。L_align は区間の結合と分割を許す揃えの費用で比べる。"
          "「乱れなし」は、ブロック全体の揃えで 1 対 1 でない組（区切りの挿入・欠落）の区間を含まない窓。"
          "ブロック平均は 4 ブロックの値の平均（§2 と同じ単位）、ほかの列は 4 ブロックの窓をまとめた割合。"
          "乱れの有無は記録の値で決めた揃えに依存する（独立な分類ではない・notes.md）。"
          % (ex["draws_per_window"], ex["draws_per_window"]))
        w("")
        w("| N | k | 窓 | L（ブロック平均） | L_align（ブロック平均） | L（まとめた） | L_align（まとめた） | 乱れなしの窓 | L（乱れなし） | L_align（乱れなし） | 乱れありの窓 | L（乱れあり） | L_align（乱れあり） |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for N in sorted({c["N"] for c in ex["cells"]}):
            for k in ks:
                n, al = ec[("L_none", k, N)], ec[("L_align", k, N)]
                sc, si = n["split_pooled_windows"]["clean"], n["split_pooled_windows"]["irregular"]
                ac, ai = al["split_pooled_windows"]["clean"], al["split_pooled_windows"]["irregular"]
                w("| %d | %d | %d | %s | %s | %s | %s | %d | %s | %s | %d | %s | %s |" % (
                  N, k, n["windows"], pct(n["overall"]), pct(al["overall"]), pct(n["overall_pooled"]),
                  pct(al["overall_pooled"]), sc["windows"], pct(sc["acc_pooled"]), pct(ac["acc_pooled"]),
                  si["windows"], pct(si["acc_pooled"]), pct(ai["acc_pooled"])))
        w("")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("summarize: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
