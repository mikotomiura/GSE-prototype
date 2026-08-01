#!/usr/bin/env python3
"""`notes.md` / `metrics.json` の数値が `results/diagnostics.json` と整合するか検査する。

notes.md は手で書く文書なので、`diagnostics.py` を直したときに**黙って古い数値が残る**。
`experiments/` は Rust を触らないので `cargo test` / lint は無条件に緑になり、
このドリフトを捕まえる層が他に無い。

検査の形: 「results から導いた文字列が、notes.md の**該当行**に現れること」。

空振りしないために 2 つの条件を強制する (どちらも独立レビューで穴を実証された):

1. **アンカーは行を一意に決めること**。複数行にマッチすると `any()` 判定になり、
   「§1 の値を壊しても §3 の同じ数字で通る」が成立してしまう。
   一意でないアンカーはその場で FAIL にして、書いた人に直させる。
2. **数値は境界付きで照合すること**。部分文字列一致だと `777` が `7770` に、
   `0.265` が `0.2650` にマッチして桁の追加を見逃す。

usage: check_notes.py <notes.md> <results/diagnostics.json> <metrics.json>
                      [results/probe_variants.json]
exit: 0=一致 / 1=不一致 (どこがどう違うかを全件表示してから落ちる)
"""
import json
import re
import sys


def fmt(v, nd):
    return f"{v:.{nd}f}"


def num(v):
    """人が notes に書く形。整数値の float は `0.0` でなく `0` と書かれる。"""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def build_checks(d):
    """(アンカー, 期待文字列, 説明) の列を results から組み立てる。"""
    inv = d["inventory_total"]
    dd = d["D1_D5_cindex_permutation"]
    r = d["D2_D3_phi_rails_and_x"]
    rails = r["rails"]["beta_writing_fixed"]
    icc = d["D4_icc"]
    dp = d["D6_D7_dead_fields_and_paste"]
    resid = r["x_recalc_vs_logged"]["ime_state_derived"]["residual"]
    pe = d["phi_equivalence_check"]["observed"]
    corr_w = r["term_correlations_with_logged_x"]
    corr_r = r["term_correlations_real_beta"]
    corr_x = r["term_correlations_with_recalc_x_beta_writing"]
    std = r["standardized_contributions"]

    C = []

    def add(anchor, expect, what):
        C.append((anchor, expect, what))

    # ---- §1 突合表
    add("| §1.3 | 124,517 サンプル", f"{inv['feat']:,}", "feat 総数")
    add("| §1.1 | X 系で名目有意ゼロ", f"{dd['x_axis_cells_computable']} セル",
        "X 系の算出可能セル数")
    add("| §1.1 | X 系で名目有意ゼロ", f"名目有意 {dd['x_axis_nominal_sig_count']} 件",
        "X 系の名目有意件数")
    add("| §1.1 | Bonferroni 通過ゼロ", f"{dd['bonferroni_threshold']:.6f}", "Bonferroni 閾値")
    add("| §1.1 | Bonferroni 通過ゼロ",
        f"{dd['bonferroni_attainable_count']}/{dd['cells_computable']}", "到達可能セル")
    add("並べ替え検定 **68 件**",
        f"**{dd['cells_core_computable']}/{dd['cells_core_total']}**", "既存特徴量セル")
    add("並べ替え検定 **68 件**",
        f"{dd['cells_computable']}/{dd['cells_total']}", "全体セル")
    for f, jp in (("f3", "φ(F3)"), ("f6", "φ(F6)"), ("f1", "φ(F1)"), ("f5", "φ(F5)")):
        v = rails[f]
        add(f"{jp} レール上", f"**{fmt(v['rail_pct'], 1)}%**", f"{jp} レール率")
        add(f"{jp} レール上", f"(0={fmt(v['zero_pct'], 1)} / 1={fmt(v['one_pct'], 1)})",
            f"{jp} 内訳")
    add("実 X と 0.25·φ(F1) の r=**0.78**",
        f"**{fmt(corr_x['r(x_recalc_beta_writing, phi1_term)'], 4)}**",
        "r (両辺 β_writing)")
    add("実 X と 0.25·φ(F1) の r=**0.78**",
        f"{fmt(corr_w['r(x_logged, phi1_term)'], 3)}", "r (β_writing 項 × 記録 X)")
    add("実 X と 0.25·φ(F1) の r=**0.78**",
        f"{fmt(corr_r['r(x_logged, phi1_term)'], 3)}", "r (実 β 項 × 記録 X)")
    add("| §1.4 | ICC",
        " ".join(f"{f}={fmt(icc[f]['eta_squared'], 4)}" for f in ("f1", "f3", "f4", "f5")),
        "η² (= `.idea` の値)")
    add("| §1.4 | ICC",
        " ".join(f"{f}={fmt(icc[f]['icc'], 3)}" for f in ("f1", "f3", "f4", "f5")),
        "ICC(1) 点推定")
    add("被験者間 **97 倍**", f"**{dp['paste_rate_max_min_ratio']} 倍**", "paste 比")

    # ---- §2-B 相関表 (値ごとに検査する。太字装飾に依存させない)
    for i in (3, 6, 1, 5):
        add("| 相関 r (β_writing 項 × 記録 X) |",
            fmt(corr_w[f"r(x_logged, phi{i}_term)"], 4), f"§2-B β_writing項×記録X φ{i}")
        add("| 相関 r (実 β 項 × 記録 X",
            fmt(corr_r[f"r(x_logged, phi{i}_term)"], 4), f"§2-B 実β項×記録X φ{i}")
        add("| **相関 r (両辺 β_writing 基準",
            fmt(corr_x[f"r(x_recalc_beta_writing, phi{i}_term)"], 4),
            f"§2-B .idea の条件 φ{i}")
        add("| **標準化寄与 sd(項)/sd(X)** |", fmt(std[f"phi{i}"], 4),
            f"§2-B 標準化寄与 φ{i}")

    # ---- §2-C ICC/η² 表 (アンカーは `.idea` 側の値。LOO 表と行を取り違えない)
    IDEA_ICC = {"f1": "0.060", "f3": "0.055", "f4": "0.159", "f5": "0.156",
                "f6": "(記載なし)"}
    for f, idea in IDEA_ICC.items():
        v = icc[f]
        anchor = f"| {f} | {idea} |"
        # 比は diagnostics.json に載る**丸め後**の値から導く (SSOT を 1 つにする)
        add(anchor, fmt(v["eta_squared"], 4), f"§2-C {f} η²")
        add(anchor, fmt(v["icc"], 4), f"§2-C {f} ICC(1)")
        add(anchor, fmt(v["eta_squared"] / v["icc"], 4), f"§2-C {f} η²/ICC(1)")
    add("k=5・N=", f"N={inv['feat']:,}・k0={icc['f1']['k0']:,.2f}", "§2-C N と k0")
    # ---- §2-C LOO 範囲表 (アンカーは点推定 3 桁)
    for f in ("f1", "f3", "f4", "f5", "f6"):
        v = icc[f]
        lo, hi = fmt(v["loo_min"], 3), fmt(v["loo_max"], 3)
        hi_cell = f"**{hi}**" if f == "f4" else hi
        add(f"| {f} | {fmt(v['icc'], 3)} |", f"{lo} – {hi_cell} |", f"§2-C LOO 範囲 {f}")

    # ---- §2-F φ 等価性
    add("| Pearson r |", f"**{pe['pearson_r']}**", "φ 等価性 r")
    add("| 残差 中央値 |", f"**{num(resid['median'])}**", "残差中央値")
    add("| 残差 p95 |", f"{resid['p95']:.6f}", "残差 p95")
    add("| 残差 > 0.01 の割合 |",
        f"**{resid['gt_0_01_pct']}%** ({resid['gt_0_01']} / {inv['feat']:,})", "残差>0.01")
    add("| 残差 max |", f"{resid['max']:.3f}", "残差 max")

    # ---- §2-D ime_shadow
    for pid, v in dp["dead_fields"].items():
        n = v["ime_shadow_events"]
        cell = f"**{n}**" if n == 0 else str(n)
        add(f"| {pid} |", cell, f"§2-D {pid} ime_shadow 件数")

    # ---- §1 paste 率
    add("paste/1000打鍵 8.99",
        " / ".join(fmt(dp["paste"][p]["paste_per_1000_keys"], 2)
                   for p in ("P010", "P011", "P012", "P013", "P014")),
        "paste/1000 打鍵")
    add("paste=0 セッション 0/12",
        "**{}/{}**".format(dp["paste"]["P010"]["sessions_with_zero_paste"],
                           dp["paste"]["P010"]["sessions"]),
        "P010 の paste=0 セッション")

    return C


def check_metrics(d, m):
    """metrics.json が diagnostics.json から導かれた値と一致するか。"""
    dd = d["D1_D5_cindex_permutation"]
    rails = d["D2_D3_phi_rails_and_x"]["rails"]["beta_writing_fixed"]
    bad = []
    exp = {
        "n_feat": d["inventory_total"]["feat"],
        "n_labels": d["inventory_total"]["answered_random_probe"],
        "x_axis_cells_computable": dd["x_axis_cells_computable"],
        "x_axis_nominal_sig_count": dd["x_axis_nominal_sig_count"],
        "nominal_sig_count": dd["nominal_sig_count"],
        "bonferroni_attainable_count": dd["bonferroni_attainable_count"],
        "bonferroni_passed_count": dd["bonferroni_passed_count"],
        "paste_rate_max_min_ratio":
            d["D6_D7_dead_fields_and_paste"]["paste_rate_max_min_ratio"],
    }
    for k, v in exp.items():
        if m.get(k) != v:
            bad.append(f"metrics.json[{k}]={m.get(k)!r} ≠ diagnostics {v!r}")
    for f, v in rails.items():
        got = m.get("phi_rail_pct_beta_writing", {}).get(f)
        if got != v["rail_pct"]:
            bad.append(f"metrics.json.phi_rail_pct_beta_writing[{f}]={got!r} "
                       f"≠ {v['rail_pct']!r}")
    for f, v in d["D4_icc"].items():
        got = m.get("icc", {}).get(f, {})
        for key, src in (("point", "icc"), ("loo_min", "loo_min"),
                         ("loo_max", "loo_max"), ("eta_squared", "eta_squared")):
            if got.get(key) != v.get(src):
                bad.append(f"metrics.json.icc[{f}].{key}={got.get(key)!r} "
                           f"≠ {v.get(src)!r}")
    if m.get("phi_equivalence_check") is not True:
        bad.append("metrics.json.phi_equivalence_check が True でない")
    return bad


def check_probe(notes, p):
    """notes.md が主張する「総当たり N 通り」「一致は 1 つだけ」を probe 出力と照合する。

    候補集合を 1 つ足した瞬間に notes が黙って古くなるのを防ぐ。
    ここが無いと D5 (総当たりを acceptance から回す) が防ごうとした腐敗が
    「スクリプトは動くが notes の数字は嘘」という形で残る。
    """
    blob = "\n".join(notes)
    bad = []
    want = [
        (f"= **{len(p['P1_permutation_cell_count']['rows'])} 通り**", "P1 の総当たり通り数"),
        (f"= **{len(p['P2_correlation']['rows'])} 通り**", "P2 の総当たり通り数"),
        (f"= **{len(p['P3_icc']['rows'])} 通り**", "P3 の総当たり通り数"),
    ]
    for s, what in want:
        if s not in blob:
            bad.append(f"[{what}] {s!r} が notes.md に無い "
                       f"(probe_variants.py の候補集合を変えたら notes も直すこと)")
    # ---- 件数だけでなく**中身**まで見る。
    # 件数チェックだけだと、候補集合を変えて別の解釈が偶然同じ件数になっても通る
    # (D7 で塞いだ「広いが意味を見ていない検査」と同じ型の穴)。
    p1 = p["P1_permutation_cell_count"]["matches"]
    if len(p1) != 10:
        bad.append(f"P1 の一致が {len(p1)} 件 (notes は「10 行に見えるが定義としては 1 つ」)")
    want_p1 = {"n_features": 17, "n_subjects": 4, "n_targets": 1,
               "count_mode": "全セル", "pooled": False}
    for r in p1:
        wrong = {k: r.get(k) for k, v in want_p1.items() if r.get(k) != v}
        if wrong:
            bad.append(f"P1 の一致が notes の解釈 (17 特徴量 × 4 被験者 × 1 ターゲット・"
                       f"全セル・pooled なし) と違う: {wrong}")
            break
    if {r["targets"] for r in p1} != {"Q1のみ", "Q2のみ"}:
        bad.append(f"P1 の一致ターゲットが {sorted({r['targets'] for r in p1})} "
                   f"(notes は「Q1/Q2 のどちらでも数は同じ・Q1 は意味論的根拠」)")

    p2 = p["P2_correlation"]["matches_f1_only"]
    if len(p2) != 1:
        bad.append(f"P2 の φ(F1) 一致が {len(p2)} 件 (notes は「この 1 つだけ」)")
    elif not (p2[0]["x"] == "x_recalc_writing" and p2[0]["term"] == "w_f1"
              and p2[0]["agg"] == "pooled" and p2[0]["scope"] == "feat全件"):
        bad.append(f"P2 の一致条件が notes の記述 (両辺 β_writing 基準・feat 全件・"
                   f"pooled) と違う: x={p2[0]['x']} term={p2[0]['term']} "
                   f"agg={p2[0]['agg']} scope={p2[0]['scope']}")

    p3 = p["P3_icc"]["exact_matches"]
    if len(p3) != 2:
        bad.append(f"P3 の 3 桁一致が {len(p3)} 件 (notes は「該当は 2 件」)")
    for r in p3:
        if r["preproc"] != "feat全件 [現行]" or not r["subjects"].startswith("all"):
            bad.append(f"P3 の一致が notes の記述 (前処理は現行と同じ feat 全件・全被験者) "
                       f"と違う: preproc={r['preproc']} subjects={r['subjects']}")
            break
    if {r["formula"] for r in p3} != {"η² = SSB/SST", "ω² (バイアス補正η²)"}:
        bad.append(f"P3 の一致式が {sorted({r['formula'] for r in p3})} "
                   f"(notes は η²=SSB/SST と ω²)")
    return bad


def main():
    if len(sys.argv) not in (4, 5):
        print("usage: check_notes.py <notes.md> <diagnostics.json> <metrics.json> "
              "[probe_variants.json]", file=sys.stderr)
        sys.exit(1)
    notes_path, diag_path, metrics_path = sys.argv[1:4]
    notes = open(notes_path, encoding="utf-8").read().splitlines()
    d = json.load(open(diag_path, encoding="utf-8"))
    m = json.load(open(metrics_path, encoding="utf-8"))

    bad = []
    n_ok = 0
    for anchor, expect, what in build_checks(d):
        hits = [(i, ln) for i, ln in enumerate(notes, 1) if anchor in ln]
        if not hits:
            bad.append(f"[{what}] アンカーが notes.md に無い: {anchor!r}")
            continue
        if len(hits) > 1:
            # 複数行にマッチすると any() 判定になり、片方が壊れても他方で通る。
            # 検査の穴なのでアンカー側を直させる。
            bad.append(f"[{what}] アンカー {anchor!r} が {len(hits)} 行にマッチする "
                       f"(行 {[i for i, _ in hits]})。アンカーを一意にすること")
            continue
        lineno, line = hits[0]
        # 数値の前後に別の数字が続いていないことまで見る (777 ⊄ 7770)。
        pat = r"(?<![0-9.])" + re.escape(expect) + r"(?![0-9])"
        if not re.search(pat, line):
            bad.append(f"[{what}] 期待値 {expect!r} が該当行に無い\n"
                       f"        anchor={anchor!r}\n"
                       f"        {lineno} 行={line.strip()!r}")
            continue
        n_ok += 1

    bad += check_metrics(d, m)
    if len(sys.argv) == 5:
        bad += check_probe(notes, json.load(open(sys.argv[4], encoding="utf-8")))

    if bad:
        print(f"[check_notes] FAILED: {len(bad)} 件の不整合", file=sys.stderr)
        for b in bad:
            print(f"  - {b}", file=sys.stderr)
        print("  notes.md / metrics.json を results/diagnostics.json に合わせて更新すること",
              file=sys.stderr)
        sys.exit(1)
    print(f"[check_notes] OK: notes.md {n_ok} 項目 + metrics.json が "
          f"results/diagnostics.json と整合")


if __name__ == "__main__":
    main()
