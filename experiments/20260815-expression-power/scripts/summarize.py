#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""power.json ＋ block_variance.json を、研究者が読む Markdown 表に畳む。

★ ここで初めて「δ80 = 0.886」と「1 SD = 76.7 keys/min」が突き合わされる。
⚠️ 標準ライブラリのみ。
"""

from __future__ import annotations

import argparse
import json


def _mean_of(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "OK" if x else "**不能**"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--power", required=True)
    ap.add_argument("--anchor", required=True)
    ap.add_argument("--power-mc", default=None, help="power_mc.json（★ 主経路）")
    ap.add_argument("--anchor-cohort", default=None, help="block_variance_cohort.json（★ 主アンカー）")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.power, encoding="utf-8") as fh:
        P = json.load(fh)
    with open(args.anchor, encoding="utf-8") as fh:
        A = json.load(fh)
    MC = None
    if args.power_mc:
        with open(args.power_mc, encoding="utf-8") as fh:
            MC = json.load(fh)
    AC = None
    if args.anchor_cohort:
        with open(args.anchor_cohort, encoding="utf-8") as fh:
            AC = json.load(fh)

    alpha = P["config_echo"]["alpha"]
    target = P["config_echo"]["target_power"]
    L = []
    w = L.append

    w("# 表現層の検出力計算 — 結果表")
    w("")
    w(f"> 生成: `scripts/summarize.py` / seed = `{P['seed']}` / α = {alpha} / 目標検出力 = {target}")
    w(f"> 刻印: HMM_VERSION `{P['config_echo']['hmm_version']}` / "
      f"EXPR_VERSION `{P['config_echo']['expr_version']}` / repo `{P['config_echo']['repo_commit']}`")
    w("")
    w("⚠️ **本ファイルは機械生成である。手で編集しない**（`run.sh` で再生成される）。")
    w("")

    # --- 検算 ---
    w("## 0. 検算（★ これが緑でなければ以下の数字を読まない）")
    w("")
    w("| n | B | δ | 解析式 | モンテカルロ | 差 | 許容 | 一致 |")
    w("|---|---|---|---|---|---|---|---|")
    for r in P["analytic_vs_monte_carlo"]:
        w(f"| {r['n']} | {r['blocks']} | {r['delta']} | {fmt(r['analytic'])} | {fmt(r['monte_carlo'])} | "
          f"{fmt(r['abs_diff'])} | {r['tolerance']} | {fmt(r['agree'])} |")
    w("")

    # --- 1. AUC 厳密帰無 ---
    w("## 1. ★★★ 「実質 AUC≈1.0 が要る」はどこから来るのか（★ 効果量を 1 つも仮定しない）")
    w("")
    w("★ 半々に割った B ブロックを順位統計量（AUC）で判定するときの**厳密帰無**。")
    w("★ G1 の実測（`20260802-g1-execution-prep/decisions.md:44`「帰無 95%点 AUC ≈ 0.94」）を第一原理で再現する。")
    w("")
    w("| B | 帰無空間 `C(B,B/2)` | 到達可能な最小 p | **p<0.05 に届く最小 AUC** | 帰無 95%点 AUC |")
    w("|---|---|---|---|---|")
    for r in P["auc_null"]:
        w(f"| {r['blocks']} | {r['null_space']:,} | {fmt(r['min_p_one_sided'], 4)} | "
          f"**{fmt(r['smallest_auc_reaching_alpha'], 4)}** | {fmt(r['null_auc_p95'], 4)} |")
    w("")
    w("> ★★★ **B=8 では AUC 0.9375 以上でなければ p<0.05 に届かない。**"
      " これは G1 の分類器の性質ではなく **C(8,4)=70 の性質**である。")
    w("> ★★★ **そして B を増やすと消える**（B=16 → 0.766 / B=32 → 0.676）。"
      " ⚠️ **要素数とは無関係である。**")
    w("")

    # --- 2. 到達可能性 × 要素数 ---
    w("## 2. ★★★ 要素数 k を入れたときの到達可能性（Bonferroni α/k・片側）")
    w("")
    ks = P["config_echo"]["grid"]["k_values"]
    w("### 2-1 個人水準（★ G1 と同じ判定）")
    w("")
    w("| B | " + " | ".join(f"k={k}" for k in ks) + " | 最小 p |")
    w("|---|" + "---|" * (len(ks) + 1))
    for b in P["config_echo"]["grid"]["blocks"]:
        cells = []
        minp = None
        for k in ks:
            r = next(x for x in P["reachability"]
                     if x["level"] == "individual" and x["blocks"] == b and x["k"] == k)
            cells.append(fmt(r["reachable_one_sided"]))
            minp = r["min_p_one_sided"]
        w(f"| {b} | " + " | ".join(cells) + f" | {fmt(minp, 4)} |")
    w("")
    w("> ★★★ **B=8 では k=4 が『不能』になる** —— `1/70 = 0.0143 > 0.05/4 = 0.0125`。")
    w("> ★ **完全に分離しても有意にならない。**⚠️ **これが「要素数の算術」の実体である。**")
    w("> ★★★ **ただし解き方は「要素を 4→1 に減らす」ではなく「ブロックを 8→10 に増やす」でよい**"
      "（B=10 なら k=12 まで到達可能・★ 1 人あたり +10 分）。")
    w("")
    w("### 2-2 符号検定（★ 方向しか使わない頑健版）")
    w("")
    w("| n | " + " | ".join(f"k={k}" for k in ks) + " | 最小 p |")
    w("|---|" + "---|" * (len(ks) + 1))
    for n in P["config_echo"]["grid"]["participants"]:
        cells = []
        minp = None
        for k in ks:
            r = next(x for x in P["reachability"]
                     if x["level"] == "sign_test" and x["participants"] == n and x["k"] == k)
            cells.append(fmt(r["reachable_one_sided"]))
            minp = r["min_p_one_sided"]
        w(f"| {n} | " + " | ".join(cells) + f" | {fmt(minp, 4)} |")
    w("")
    w("> ⚠️★★★ **n=3・n=4 は、どの要素数でも、どんな効果でも棄却できない。**")
    w("> ★ **PS-D9 の指定範囲 n=3–10 の下端は、この検定では判定に到達しない。**")
    w("")

    # --- 3. δ80 の格子 ---
    if MC:
        w("## 3. ★★★ 80% 検出力に要る効果量 δ80（★ 主経路 = 並べ替え検定をそのまま模擬）")
        w("")
        w(f"> 模擬: {MC['sims']} 標本 × 並べ替え {MC['perms']} 通り / 目標検出力 {MC['target_power']}")
        w("> ⚠️★★★ **解析式（σ 既知の正規近似）は楽観側に外れる** —— 並べ替え帰無は**観測データに条件付き**で、")
        w("> H1 では処置が観測分散を膨らませるため**帰無分布そのものが広がる**（膨張率 = `sqrt(1 + Bδ²/(4(B−1)))`）。")
        w("> ★ 併記して差を見せる（`oracle_check.py` O5a が向きを検査に固定している）。")
        w("")
        w("| 検定本数 | α_eff | n | B | **δ80（MC・主）** | δ80（解析式・楽観） | 楽観幅 |")
        w("|---|---|---|---|---|---|---|")
        for r in MC["halves"]:
            if r["n_tests"] not in (1, 4) or r["blocks"] not in (8, 10, 16, 32):
                continue
            w(f"| {r['n_tests']} | {fmt(r['alpha_effective'], 4)} | {r['n']} | {r['blocks']} | "
              f"**{fmt(r['delta80_mc'])}** | {fmt(r['delta80_analytic'])} | "
              f"{fmt(r['analytic_optimism_pct'], 1)}% |")
        w("")
        w("> ★★★ **同じ B で 4 要素を識別する代価**（n=5・B=8）: **0.909 → 1.113 = +22%**。")
        w("> ⚠️ **『要素を増やすと検出力が割り算される』ではない。**")
        w("")
        w("### 3-1 dismantling（[P110] が集めた設計）—— ★ ここだけは本当に割り算になる")
        w("")
        w("| k | B | 1 条件あたり | n | **δ80（MC）** |")
        w("|---|---|---|---|---|")
        for r in MC["dismantling"]:
            w(f"| {r['k']} | {r['blocks']} | {r['blocks_per_condition']} ブロック | {r['n']} | "
              f"**{fmt(r['delta80_mc'])}** |")
        w("")
        w("### 3-2 帰無較正（★ δ=0 で棄却率が α を超えないこと）")
        w("")
        w("| n | B | 棄却率 | α | 判定 |")
        w("|---|---|---|---|---|")
        for r in MC["null_calibration"]:
            w(f"| {r['n']} | {r['blocks']} | {fmt(r['rejection_rate'], 4)} | {r['alpha']} | "
              f"{fmt(r['ok'])} |")
        w("")
        w("### 3-3 参考: 解析式で掃いた全格子（★ 楽観側・向きの比較用）")
        w("")
    else:
        w("## 3. ★★★ 80% 検出力に要る効果量 δ（★ 解析式・コホート水準・両側）")
        w("")
    w("| 設計 | k | B | n | 検定本数 | α_eff | **δ80** | AUC 換算 | 1 人あたり |")
    w("|---|---|---|---|---|---|---|---|---|")
    want = [("bundle", 1), ("factorial_fractional", 4), ("factorial_full", 4), ("dismantling", 4),
            ("factorial_fractional", 12)]
    for design, k in want:
        for b in (8, 16, 32):
            for n in (3, 5, 10):
                rs = [x for x in P["power_grid"]
                      if x["design"] == design and x["k"] == k and x["blocks"] == b and x["n"] == n]
                if not rs:
                    continue
                r = rs[0]
                ntest = round(alpha / r["alpha_effective"])
                w(f"| {design} | {k} | {b} | {n} | {ntest} | {fmt(r['alpha_effective'], 4)} | "
                  f"**{fmt(r['delta_for_target_power'])}** | {fmt(r['auc_equivalent'])} | "
                  f"{r['minutes_per_participant']} 分 |")
    w("")
    w("> ★★★ **同じ B なら、4 要素を識別する一部実施 factorial の代価は δ80 が 0.886 → 1.056（+19%）だけである**"
      "（n=5・B=8）。")
    w("> ⚠️★★★ **『要素を増やすと検出力が割り算される』が正しいのは dismantling だけ**"
      "（0.886 → 1.670・+88%）。★ **[P110] が集めたのはこの設計である。**")
    w("")

    # --- 4. 識別 ---
    w("## 4. 識別 —— 「k 要素のうち 1 つだけが δ=1.0 で効く」とき（n=5）")
    w("")
    w("| 設計 | k | B | 成立 | 検定本数 | 検出力 | **真の要素を名指しできる確率** | 偽陽性(FWER) |")
    w("|---|---|---|---|---|---|---|---|")
    for r in P["identification"]:
        if r["n"] != 5 or r["k"] not in (1, 4, 12) or r["blocks"] not in (8, 16, 32):
            continue
        fe = "○" if r["feasible"] else f"× (要 {r['blocks_required']})"
        w(f"| {r['design']} | {r['k']} | {r['blocks']} | {fe} | {r['n_tests']} | "
          f"{fmt(r['power_for_delta'])} | **{fmt(r['p_identify_true_element'])}** | "
          f"{fmt(r['p_any_false_positive'])} |")
    w("")
    w("> ★★★ **束ねる設計は、要素数によらず検出力が変わらない代わりに、名指し確率が恒久的に 0 である。**")
    w("> ★ **これが [P110] の逐語「どの要素が効くか意味ある結論を出せない」の設計上の正体。**")
    w("")

    # --- 5. 個人水準の検出力 ---
    w("## 5. 個人水準（G1 と同じ判定）の検出力 —— 厳密並べ替え・全数列挙・片側")
    w("")
    deltas = sorted({r["delta"] for r in P["individual_level_power"]})
    w("| B | " + " | ".join(f"δ={d}" for d in deltas) + " |")
    w("|---|" + "---|" * len(deltas))
    for b in sorted({r["blocks"] for r in P["individual_level_power"]}):
        cells = []
        for d in deltas:
            rs = [x for x in P["individual_level_power"] if x["blocks"] == b and x["delta"] == d]
            cells.append(fmt(rs[0]["power_one_sided"]) if rs else "—")
        w(f"| {b} | " + " | ".join(cells) + " |")
    w("")
    w("> ⚠️★★★ **1 人だけを見る判定は、δ=2.0（= 2 SD）でも B=8 で検出力が 1.0 に届かない。**")
    w("> ★ **コホート水準に上げるだけで同じデータの検出力が上がる**（表 3 と比べる）。")
    w("> ★ **B=4 / B=6 の 0.000 はバグではない** —— 表 1 のとおり到達可能な最小 p が"
      " 0.1667 / 0.0500 で、`p < 0.05` を満たせないため**効果量をいくら大きくしても棄却しない**"
      "（`power_selftest.py` 検査 4 がこれを固定している）。")
    w("")

    # --- 6. 実測アンカー ---
    kr = A["block_level_keystroke_rate_per_min"]
    ps = A["block_level_p_stuck_fraction"]
    w("## 6. ★★★ 実測アンカー —— δ=1.0 は GSE の実データで何を意味するか")
    w("")
    if AC:
        cc = AC["prereg_cross_check"]
        w("### 6-0 ★★★ 主アンカー: Phase1 コホート P010–P014（★ 5 名・**5 分窓 = 1 ブロック**）")
        w("")
        w(f"★ 参加者 **{AC['participants']} 名** / 窓 **{AC['windows_total']}** 個 / 窓長 {AC['window_minutes']} 分。")
        w("★ **集計値のみ**（`data.md` 参照・★ ファイル名を 1 つも出力していない）。")
        w("")
        w("| 参加者 | セッション | 窓 | 平均 (keys/min) | SD | **CV** |")
        w("|---|---|---|---|---|---|")
        for p in AC["per_participant"]:
            w(f"| {p['participant']} | {p['sessions']} | {p['windows']} | {fmt(p['rate_mean'], 2)} | "
              f"{fmt(p['rate_sd'], 2)} | **{fmt(p['rate_cv'], 3)}** |")
        wc = AC["within_participant_cv"]
        bp = AC["between_participant"]
        w("")
        w(f"- ★★★ **参加者内 CV の中央値 = {fmt(wc['median'], 3)}**（範囲 {fmt(wc['min'], 3)}–{fmt(wc['max'], 3)}）"
          " ←★ **被験者内設計で使うべき σ/μ はこれ**")
        w(f"- ★ 参加者間: 平均 {fmt(bp['mean_of_participant_means'], 2)} / "
          f"SD {fmt(bp['sd_of_participant_means'], 2)} keys/min "
          "——⚠️ **人によって桁が違う**（★ だから被験者内で組む）")
        w("")
        w("#### ⚠️ 事前登録の記録との突き合わせ（★ 一致しない。理由も書く）")
        w("")
        w("| | G1 事前登録 §2.9 の記録 | ★ 本実験の再計算 |")
        w("|---|---|---|")
        w(f"| 窓の数 | {cc['recorded_windows']} | **{cc['recomputed_windows']}** |")
        w(f"| 中央値 (keydown/窓) | {cc['recorded_median']} | {fmt(cc['recomputed_median'], 1)} |")
        w(f"| 第 1 四分位 | {cc['recorded_q1']} | {fmt(cc['recomputed_q1'], 1)} |")
        w(f"| 100 未満の割合 | {cc['recorded_frac_below_100']} | {fmt(cc['recomputed_frac_below_100'], 4)} |")
        w("")
        w("> ⚠️★★★ **一致しないのは想定どおりで、矛盾ではない** —— 事前登録は **「論述セッション」に絞った 360 窓**、")
        w("> ★ 本実験は**全セッション**の 617 窓である（★ 読解・離席を多く含むぶん本実験の方が散らばりが大きい）。")
        w("> ⚠️ **したがって「事前登録の数字を再現した」とは書かない。**★ **本実験の CV は上限側である。**")
        w("")
        # --- 活動ゲート ---
        gates = AC.get("activity_gates", [])
        gate100 = next((g for g in gates if g["min_keydown_per_window"] == 100), None)
        if gates:
            w("#### ★★★ 6-0b 非打鍵ノイズを剥がす —— G1 の事前登録ゲートを当てる")
            w("")
            w("> ⚠️★★★ **研究者の指摘（2026-08-15）**: **「これらのデータは打鍵以外のノイズなども入っている。")
            w("> G1 で純粋な打鍵データを集めている」** —— ★ **Phase1 は自然ログで、読解・離席・別作業が窓に入る。**")
            w("> ★ そこで **G1 が事前登録 §2.9 で凍結した適格性ゲート（ブロックあたり `keydown ≥ 100`）** を")
            w("> **そのまま窓に当てて**、ノイズが CV のどれだけを占めるかを測る（★ 閾値は事後に決めていない）。")
            w("")
            w("| ゲート | 残る窓 | 落ちる窓 | **参加者内 CV 中央値** | 範囲 |")
            w("|---|---|---|---|---|")
            for g in gates:
                lab = f"`keydown ≥ {g['min_keydown_per_window']}`"
                if g["min_keydown_per_window"] == 100:
                    lab += " ★**G1 の凍結ゲート**"
                elif g["min_keydown_per_window"] == 0:
                    lab = "なし（全窓）"
                w(f"| {lab} | {g['windows_kept']} | {g['windows_dropped']} | "
                  f"**{fmt(g['within_participant_cv_median'], 3)}** | "
                  f"{fmt(g['within_participant_cv_min'], 3)}–{fmt(g['within_participant_cv_max'], 3)} |")
            w("")
            w("> ★★★ **非打鍵ノイズが CV のおよそ半分を占めている**（1.053 → 0.502）。")
            w("> ⚠️★★★ **ただし残る 0.502 も統制下の値ではない** —— ★ 日も課題も資料も揃っていない。")
            w("> ★ **G1 が統制するのはまさにそこ**（同一課題・照合済み資料・1 回の来所・順序の相殺）なので、")
            w("> ★★★ **統制下 CV は 0.502 よりさらに下がるはずで、どこまで下がるかが G1 のデータで初めて分かる。**")
            w("")
        if gate100 and gate100["within_participant_cv_median"]:
            cv = gate100["within_participant_cv_median"]
            cv_label = (f"P010–P014 に **G1 の凍結ゲート `keydown ≥ 100`** を当てた参加者内 CV 中央値 "
                        f"**{fmt(cv, 3)}**（★ ゲート無しなら {fmt(wc['median'], 3)}）")
            sd_for_rate = cv * _mean_of([r["rate_mean"] for r in gate100["per_participant"]])
        else:
            cv = wc["median"]
            cv_label = f"P010–P014 の参加者内 CV 中央値 {fmt(cv, 3)}"
            sd_for_rate = cv * bp["mean_of_participant_means"]
    else:
        cv = kr["cv"]
        cv_label = f"P000 の CV {fmt(cv, 3)}"
        sd_for_rate = kr["sd"]

    w("### 6-1 副アンカー: P000（★ 1 名・セッション = ブロック）")
    w("")
    w("| 指標 | ブロック数 | 平均 | SD（= δ 1.0 分） | CV |")
    w("|---|---|---|---|---|")
    w(f"| 打鍵率 (keys/min) | {kr['n_blocks']} | {fmt(kr['mean'], 2)} | {fmt(kr['sd'], 2)} | "
      f"{fmt(kr['cv'], 3)} |")
    w(f"| `p_stuck > 0.70` の割合 | {ps['n_blocks']} | {fmt(ps['mean'], 4)} | {fmt(ps['sd'], 4)} | "
      f"{fmt(ps['sd'] / ps['mean'], 3) if ps['mean'] else '—'} |")
    w("")
    w("> ★ P000 は**能動的な作業セッションだけ**なので CV が小さく出る（0.657）。")
    w("> ⚠️ **コホート（1.05）との差そのものが「どのセッションを混ぜるかで分散が倍動く」ことを示している。**")
    w("")

    def d80_of(n_tests, n, b):
        if MC:
            rs = [x for x in MC["halves"]
                  if x["n_tests"] == n_tests and x["n"] == n and x["blocks"] == b]
            if rs and rs[0]["delta80_mc"] is not None:
                return rs[0]["delta80_mc"], "MC"
        design = "bundle" if n_tests == 1 else "factorial_fractional"
        k = 1 if n_tests == 1 else n_tests
        rs = [x for x in P["power_grid"]
              if x["design"] == design and x["k"] == k and x["blocks"] == b and x["n"] == n]
        return (rs[0]["delta_for_target_power"], "解析式") if rs else (None, "—")

    w("### 6-2 ★★★ 突き合わせ（★ ここが PS-Q1 の実質）")
    w("")
    w(f"★ 使う CV = **{cv_label}**。★ δ80 は表 3 の **MC 値**。")
    w("")
    w("| 検定本数 | n | B | δ80 | 打鍵率でいうと | **要る相対変化** |")
    w("|---|---|---|---|---|---|")
    for n_tests, n, b in ((1, 3, 8), (1, 5, 8), (1, 10, 8), (1, 10, 16), (1, 10, 32),
                          (4, 5, 8), (4, 10, 16), (4, 10, 32)):
        d80, src = d80_of(n_tests, n, b)
        if d80 is None:
            continue
        w(f"| {n_tests} | {n} | {b} | {fmt(d80)} ({src}) | {fmt(d80 * sd_for_rate, 1)} keys/min | "
          f"**{fmt(100 * d80 * cv, 1)}%** |")
    w("")
    w("> ⚠️★★★ **この CV も統制下の値ではない。**★ Phase1 は自然ログであり、")
    w("> ★ ゲートで非打鍵ノイズを剥がしてなお**日・課題・資料・時刻が揃っていない**。")
    w("> ★ **G1 が統制するのはまさにそこ**（同一課題・照合済み資料・1 回の来所・順序の相殺・copy 陽性対照）。")
    w("> ⚠️★★★ **G1 はまだ収集中**（★ 確証標本 3 名のうち P010 が実施済み・残り 2 名。")
    w("> ★ `experiments/20260801-controlled-friction-task/results/` は空 ＝ `analyze.py` は一度も判定を出していない）。")
    w("> ★★★ **したがって『表現層パイロットが成立するか』の可否は、G1 が出す統制下 CV にかかっている。**")
    w("")
    w("### 6-3 ★★★ 逆に読む —— 統制下 CV がいくつなら成立するか")
    w("")
    w("| 検定本数 | n | B | 1 人あたり | δ80 | **10% 検出に要る CV** | ゲート後 CV からの必要縮小 |")
    w("|---|---|---|---|---|---|---|")
    for n_tests, n, b in ((1, 5, 8), (1, 10, 8), (1, 10, 16), (1, 10, 32), (4, 10, 32)):
        d80, _ = d80_of(n_tests, n, b)
        if d80 is None:
            continue
        need_cv = 0.10 / d80
        w(f"| {n_tests} | {n} | {b} | {b * 5} 分 | {fmt(d80)} | **{fmt(need_cv, 3)}** | "
          f"**{fmt(cv / need_cv, 2)} 倍** |")
    w("")
    w("> ★★★ **ゲート後の 0.502 は、既に『あと 1.6 倍』の距離まで来ている**（n=10・B=32 の場合）。")
    w("> ★ **統制手続きがそれだけ分散を削れるかどうかが、成立の分かれ目である。**")
    w("> ⚠️ **これは楽観論ではない** —— ★ **1 人あたり 160 分**の設計であることは変わらない。")
    w("")

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
