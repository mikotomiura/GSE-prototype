"""Tables of the results (results/summary.md).

  summarize.py --results results --out results/summary.md

Every cell is reported (preregistration.md). The previous task's values (B0, ideal and strong noise) are read
from its committed matching.json after its SHA-256 is checked, and placed next to this task's main attackers;
they come from other conditions (contiguous text windows and a noise model) and are not the same quantity.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402

SC_ORDER = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S10", "S12", "S13", "S14", "S15"]
CAUSE_ORDER = ["none", "comma", "reading", "comma+reading", "procedure", "procedure+comma", "procedure+reading",
               "procedure+comma+reading", "procedure+synthetic", "procedure+comma+synthetic"]


def pct(v):
    if v is None:
        return "–"
    p = 100.0 * v
    if abs(p) < 10:
        return "%.2f" % p
    return "%.1f" % p


def acc_ci(r):
    if r["ci"][0] is None:
        return "%s" % pct(r["acc"])
    return "%s [%s, %s]" % (pct(r["acc"]), pct(r["ci"][0]), pct(r["ci"][1]))


def crosscheck_tables(cc):
    out = ["## 1. 照らし合わせ（記録 ↔ 本文から合成した並び）", ""]
    al = cc["alignment"]
    out.append("割り当て: %d ブロック中 %d が計画と一致しない（採点しない）・試行 %d 中 %d を採点・押下 %d（割り当てられない押下 %d）。"
               "採点した試行のうちカテゴリ列が計画と違うもの %d。" % (
                   al["n_blocks"], al["n_blocks_unscored"], al["n_trials"], al["n_trials"] - al["n_trials_unscored"],
                   al["n_presses"], al["n_presses_unassigned"], cc["n_scored_trials_differing_from_plan"]))
    out.append("")
    out.append("説明のつかない不一致（原因の印が無いのに並びが違う試行）: **%d**。前のタスクの手順の読みがコーパスの読みと違う試行: %d"
               "（語句 %d 個の読みを合成）。" % (cc["n_unexplained"], cc["n_trials_reading_differs"],
                                     cc["n_phrases_synthesised"]))
    out.append("")
    out.append("| シナリオ | 試行 | 比べた | 並びが一致 | 合計が一致 | 開いた区間 | 閉じた区間の数 | 差 Δ の平均 [最小, 最大] | 原因の印 |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for s in SC_ORDER:
        v = cc["by_scenario"].get(s)
        if not v:
            continue
        dl = v["delta"]
        dtxt = "–" if dl["n"] == 0 else "%.2f [%d, %d]" % (dl["mean"], dl["min"], dl["max"])
        ncl = "・".join("%s 個 %d" % (k, n) for k, n in sorted(v["n_closed_segments"].items(), key=lambda kv: int(kv[0])))
        fl = "・".join("%s %d" % (k, n) for k, n in sorted(v["flags"].items()))
        out.append("| %s | %d | %d | %d | %d | %d | %s | %s | %s |" % (s, v["n"], v["n_compared"], v["seq_equal"],
                                                                 v["total_equal"], v["open_segment"], ncl, dtxt,
                                                                 fl or "–"))
    out.append("")
    out.append("| 原因の印 | 試行 | 比べた | 並びが一致 | 合計が一致 | 差 Δ の平均 [最小, 最大] |")
    out.append("|---|---|---|---|---|---|")
    keys = [c for c in CAUSE_ORDER if c in cc["by_cause"]] + sorted(c for c in cc["by_cause"] if c not in CAUSE_ORDER)
    for c in keys:
        v = cc["by_cause"][c]
        dl = v["delta"]
        dtxt = "–" if dl["n"] == 0 else "%.2f [%d, %d]" % (dl["mean"], dl["min"], dl["max"])
        out.append("| %s | %d | %d | %d | %d | %s |" % (c, v["n"], v["n_compared"], v["seq_equal"], v["total_equal"],
                                                     dtxt))
    out.append("")
    return out


def reproduce_table(rep):
    out = ["## 2. k = 1 の再現の確認（IME 論文の候補と同点の決め方）", "",
           "すべて一致: **%s**" % ("はい" if rep["all_match"] else "いいえ"), "",
           "| K | 組 | 正答 / 試行 | acc_raw（本タスク） | acc_raw（公開値） | 平均順位（本タスク / 公開値） |",
           "|---|---|---|---|---|---|"]
    for K in sorted(rep["results"], key=int):
        for f in sorted(rep["results"][K]):
            r = rep["results"][K][f]
            out.append("| %s | %s | %d / %d | %.6f | %.6f | %.4f / %.4f |" % (
                K, f, r["correct"], r["n"], r["acc_raw"], r["published_acc_raw"], r["mean_rank"],
                r["published_mean_rank"]))
    out.append("")
    return out


def prior_values(prior):
    out = {}
    for c in prior["cells"]:
        if c["definition"] == "B0" and c.get("status") == "ok":
            out[(c["k"], c["N"])] = c["results"]
    return out


def main_curves(m, prior):
    pv = prior_values(prior)
    out = ["## 3. 照合の正答率（% と 95% 区間・ブロックを単位にしたブートストラップ）", "",
           "前のタスクの値（B0・理想と強い雑音）は条件が違う（作品の続いた本文の窓・雑音のモデル・候補は別々の作品）ので、同じ量ではない。", ""]
    by = dict(((c["k"], c["N"]), c) for c in m["cells"])
    ks = sorted(set(c["k"] for c in m["cells"]))
    Ns = sorted(set(c["N"] for c in m["cells"]))
    for N in Ns:
        out.append("### N = %d（偶然の水準 %s%%）" % (N, pct(1.0 / N)))
        out.append("")
        out.append("| k | 窓 | 長さだけ L_none | シミュレーション S_no_time | 前のタスク B0 理想 | 前のタスク B0 強 |")
        out.append("|---|---|---|---|---|---|")
        for k in ks:
            c = by.get((k, N))
            if c is None:
                continue
            p = pv.get((k, N))
            pi = acc_ci(p["ideal"]) if p else "–"
            ps = acc_ci(p["strong"]) if p else "–"
            out.append("| %d | %d | %s | %s | %s | %s |" % (k, c["n_windows"], acc_ci(c["results"]["L_none"]),
                                                          acc_ci(c["results"]["S_no_time"]), pi, ps))
        out.append("")
    return out


def variant_tables(m, variants):
    out = ["## 4. 加工ごとの正答率（%・全セル）", ""]
    by = dict(((c["k"], c["N"]), c) for c in m["cells"])
    ks = sorted(set(c["k"] for c in m["cells"]))
    Ns = sorted(set(c["N"] for c in m["cells"]))
    for N in Ns:
        out.append("### N = %d（偶然の水準 %s%%）" % (N, pct(1.0 / N)))
        out.append("")
        out.append("| 加工 | " + " | ".join("k = %d" % k for k in ks) + " |")
        out.append("|---|" + "---|" * len(ks))
        for name in variants:
            cells = [by.get((k, N)) for k in ks]
            out.append("| %s | " % name + " | ".join(acc_ci(c["results"][name]) if c else "–" for c in cells) + " |")
        out.append("")
    return out


def diagnostics_table(m):
    out = ["## 5. 診断（%・偶然の水準の近くになるはずのもの）", "",
           "| k | N | 偶然の水準 | 無作為 | 記録を使わない | 入れ替え L_none | 入れ替え S_no_time | おとりの引き直し |",
           "|---|---|---|---|---|---|---|---|"]
    for c in m["cells"]:
        dg = c["diagnostics"]
        out.append("| %d | %d | %s | %s | %s | %s | %s | %d |" % (
            c["k"], c["N"], pct(c["chance"]), acc_ci(dg["random"]), acc_ci(dg["typical"]), acc_ci(dg["swap_L_none"]),
            acc_ci(dg["swap_S_no_time"]), c["n_decoys_redrawn"]))
    out.append("")
    return out


def by_scenario_table(m, names):
    out = ["## 6. k = 1 のシナリオごとの正答率（%・区間なし・記述）", ""]
    for c in m["cells"]:
        if c["k"] != 1:
            continue
        out.append("### N = %d" % c["N"])
        out.append("")
        out.append("| 加工 | " + " | ".join(SC_ORDER_K1) + " |")
        out.append("|---|" + "---|" * len(SC_ORDER_K1))
        for name in names:
            bs = c["by_scenario"][name]
            out.append("| %s | " % name + " | ".join(pct(bs[s]["acc"]) if s in bs else "–" for s in SC_ORDER_K1) + " |")
        out.append("")
    return out


SC_ORDER_K1 = [s for s in SC_ORDER if s != "S12"]


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    cc, _ = kitload.read_json(os.path.join(a.results, "crosscheck.json"))
    rep, _ = kitload.read_json(os.path.join(a.results, "reproduce_ime.json"))
    m, _ = kitload.read_json(os.path.join(a.results, "matching.json"))
    prior, _ = kitload.read_json(kitload.input_path(cfg, "prior_matching"))
    variants = list(cfg["variants"])
    lines = ["# 結果の表（自動生成・`scripts/summarize.py`）", "",
             "IME 論文の Windows のセル（合成入力）。合否の判定ではない。読み方と限界は `notes.md`。", ""]
    lines += crosscheck_tables(cc)
    lines += reproduce_table(rep)
    lines += main_curves(m, prior)
    lines += variant_tables(m, variants)
    lines += diagnostics_table(m)
    lines += by_scenario_table(m, variants)
    data = ("\n".join(lines).rstrip("\n") + "\n").encode("utf-8")
    with open(a.out, "wb") as f:
        f.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
