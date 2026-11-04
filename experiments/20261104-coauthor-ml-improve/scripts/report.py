"""results/summary.json（集計値だけ）から notes 用の表を Markdown で書き出す。

書き手ごとの値（repo の外の writer_values）は読まない。数の読み替えはせず、summary の値をそのまま丸めて並べる。
使い方: python -I scripts/report.py results/summary.json > tables.md
"""
import json
import sys

STRUCTS = ["hmm3", "hmm6", "hmm10", "ar1", "ar2", "ar3"]
OPPS = ["r1", "pool_same", "pool_hmm3", "fb"]
OPP_JA = {"r1": "r1", "pool_same": "同じ構造の共通", "pool_hmm3": "K=3 の共通", "fb": "F-b"}
TAUS = ["0", "100", "1000", "10000"]
LG_ROWS = ["self_main", "self_other", "lam_0.1", "lam_1.0", "lam_10.0", "lam_100.0", "lam_inf", "pooled_single",
           "b0_self", "b0_pool"]
LG_JA = {"self_main": "本人（λ 主）", "self_other": "本人（λ 副）", "lam_0.1": "λ=0.1", "lam_1.0": "λ=1",
         "lam_10.0": "λ=10", "lam_100.0": "λ=100", "lam_inf": "λ=∞", "pooled_single": "共通（1 つの切片）",
         "b0_self": "B0-self", "b0_pool": "B0-pool"}
FEAT = ["押下数", "backspace 数", "最長の間隔", "p_stuck", "ewma_x"]


def f(x, d=3):
    if x is None:
        return "—"
    if isinstance(x, float) and abs(x) < 10 ** (-d) and x != 0:
        return f"{x:.1e}"
    return f"{x:.{d}f}"


def cell(st, d=3, share=True, ci=False):
    """Δ の集計 1 つを「中央値 [q25, q75] 良 割合」に。伏せたものは「伏せ（n 人）」。"""
    if st is None:
        return "—"
    if st.get("suppressed"):
        return f"伏せ（{st['n']} 人）"
    s = f"{f(st['median'], d)} [{f(st['q25'], d)}, {f(st['q75'], d)}]"
    if share and "better_share" in st:
        s += f" 良 {st['better_share']:.2f}"
    if ci and st.get("ci"):
        s += f" 区間 [{f(st['ci'][0], d)}, {f(st['ci'][1], d)}]"
    return s


def counts(c):
    if c is None:
        return "—"
    if c.get("suppressed"):
        return f"伏せ（{c['n']} 人）"
    return "・".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1]))


def em_tables(name, E, panels):
    out = []
    for pn in panels:
        P = E[pn]
        for lab in ("all", "pressed"):
            out.append(f"\n#### {name} EM {pn} τ 他人（主）・{'全記号' if lab == 'all' else '窓に押下のある記号'}"
                       "（Δ = 本人 − 相手・1 記号あたりの対数尤度・正が本人の良い側・中央値 [四分位] 良 = 良い側の割合）\n")
            out.append("| k | 人数 | 構造 | " + " | ".join(OPP_JA[o] for o in OPPS) + " | 選ばれた τ |")
            out.append("|---|---|---|" + "---|" * len(OPPS) + "---|")
            for k, Ek in P.items():
                for s in STRUCTS:
                    St = Ek["structs"][s]
                    row = St["tau_other"]
                    cells = [cell(row[f"{lab}/self_minus_{o}"]) for o in OPPS]
                    out.append(f"| {k} | {Ek['writers']} | {s} | " + " | ".join(cells) + f" | {counts(St['chosen_tau_other'])} |")
        # 区間（主・全記号・r1 と同じ構造の共通）
        out.append(f"\n#### {name} EM {pn} τ 他人・全記号の中央値の区間（書き手の復元抽出 2,000 回）\n")
        out.append("| k | 構造 | r1 | 同じ構造の共通 | K=3 の共通 | F-b |")
        out.append("|---|---|---|---|---|---|")
        for k, Ek in P.items():
            for s in STRUCTS:
                row = Ek["structs"][s]["tau_other"]
                cs = []
                for o in OPPS:
                    st = row[f"all/self_minus_{o}"]
                    cs.append("—" if not st or st.get("suppressed") or not st.get("ci") else
                              f"[{f(st['ci'][0])}, {f(st['ci'][1])}]")
                out.append(f"| {k} | {s} | " + " | ".join(cs) + " |")
        # τ 固定と τ 本人 CV（r1 と同じ構造の共通・全記号の中央値）
        out.append(f"\n#### {name} EM {pn} τ 固定 4 行と τ 本人 CV（副）・全記号の Δ の中央値（相手: r1 / 同じ構造の共通）\n")
        out.append("| k | 構造 | " + " | ".join(f"τ={t}" for t in TAUS) + " | τ 他人 | τ 本人 CV | 本人 CV が選んだ τ |")
        out.append("|---|---|" + "---|" * (len(TAUS) + 3))
        for k, Ek in P.items():
            for s in STRUCTS:
                St = Ek["structs"][s]

                def two(r):
                    if r not in St:
                        return "—"
                    def one(st):
                        if st is None:
                            return "—"
                        return "伏せ" if st.get("suppressed") else f(st["median"])
                    return f"{one(St[r]['all/self_minus_r1'])} / {one(St[r]['all/self_minus_pool_same'])}"
                out.append(f"| {k} | {s} | " + " | ".join(two("tau_" + t) for t in TAUS) +
                           f" | {two('tau_other')} | {two('tau_cv')} | {counts(St.get('chosen_tau_cv'))} |")
        # K 本人 CV
        out.append(f"\n#### {name} EM {pn} K 本人 CV（k ≥ 3・族ごと・全記号）\n")
        out.append("| k | 族 | " + " | ".join(OPP_JA[o] for o in OPPS) + " | 選ばれた構造 |")
        out.append("|---|---|" + "---|" * len(OPPS) + "---|")
        for k, Ek in P.items():
            for fam, Kc in Ek["kcv"].items():
                cells = [cell(Kc["k_cv"][f"all/self_minus_{o}"]) for o in OPPS]
                out.append(f"| {k} | {fam} | " + " | ".join(cells) + f" | {counts(Kc['chosen_struct'])} |")
    return out


def em_diag(name, E, panels):
    out = [f"\n#### {name} EM 本人の当てはめの診断（τ ごとに k と構造を通して足した数）\n",
           "| パネル | τ | 収束しなかった開始点 | 目的が減った回 | 勝った開始点 | 1 位と 2 位の差の中央値の範囲 |",
           "|---|---|---|---|---|---|"]
    for pn in panels:
        for t in TAUS:
            nc = dec = 0
            win = {}
            gaps = []
            for k, Ek in E[pn].items():
                for s in STRUCTS:
                    d = Ek["structs"][s]["diag"][t]
                    nc += d["nonconv_starts"]
                    dec += d["decreases"]
                    if not d["winner"].get("suppressed"):
                        for a, b in d["winner"].items():
                            win[a] = win.get(a, 0) + b
                    if d["gap12"] and not d["gap12"].get("suppressed"):
                        gaps.append(d["gap12"]["median"])
            out.append(f"| {pn} | {t} | {nc} | {dec} | {counts(win)} | "
                       f"{f(min(gaps)) if gaps else '—'} 〜 {f(max(gaps)) if gaps else '—'} |")
    return out


def lg_tables(name, L, panels, sets, cs1):
    out = []
    for pn in panels:
        for key in sets:
            out.append(f"\n#### {name} ロジスティック {pn} {key}（C = 書き手の中の一致度・区間は書き手の復元抽出・"
                       "Brier は 本人 − B0-self の書き手ごとの中央値 [四分位] 良 = 負の割合）\n")
            hdr = "| k | 人数 | 行 | C | 組のある人数 | C の区間 | Brier − B0-self |" + (" 書き手ごとの AUC |" if cs1 else "")
            out.append(hdr)
            out.append("|---|---|---|---|---|---|---|" + ("---|" if cs1 else ""))
            for k, Pk in L[pn].items():
                X = Pk[key]
                for r in LG_ROWS:
                    m = X["models"][r]
                    ci = m["C_ci"]
                    s = (f"| {k} | {X['writers']} | {LG_JA[r]} | {f(m['C'])} | {m['writers_with_pairs']} | "
                         f"{'—' if not ci else '[' + f(ci[0]) + ', ' + f(ci[1]) + ']'} | {cell(m['brier_minus_b0_self'], 4, ci=True)} |")
                    if cs1:
                        a = m.get("auc_per_writer")
                        s += (" — |" if not a else (f" 伏せ（{a['n']} 人） |" if a.get("suppressed") else
                                                    f" {f(a['median'])} [{f(a['q25'])}, {f(a['q75'])}] |"))
                    out.append(s)
            out.append(f"\n{name} {pn} {key} の付帯（k ごと）\n")
            out.append("| k | 選ばれた λ（主） | 主が本人の CV / 他人 | 選ばれた λ（副） | 学習の問い | 学習の陽性 | 評価の問い | 評価の陽性 |"
                       " 1 類だけ | β と β共通 の差 > 10 | 収束せず | 共通の合わせた AUC |")
            out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
            for k, Pk in L[pn].items():
                X = Pk[key]
                ch = X["chosen_lambda"]

                def qq(v):
                    if v is None:
                        return "—"
                    if v.get("suppressed"):
                        return f"伏せ（{v['n']}）"
                    return f"{v['median']:.0f} [{v['q25']:.0f}, {v['q75']:.0f}]"
                pa = X["models"]["pooled_single"].get("pooled_auc")
                out.append(f"| {k} | {counts(ch['main'])} | {ch['main_source']['cv']} / {ch['main_source']['other']} | "
                           f"{counts(ch['other'])} | {qq(X['train_labels'])} | {qq(X['train_pos'])} | {qq(X['test_labels'])} | "
                           f"{qq(X['test_pos'])} | {X['one_class_train']} | {X['fit_flags_all_lambdas']['far']} | "
                           f"{X['fit_flags_all_lambdas']['nonconv']} | {f(pa) if pa is not None else '—'} |")
    return out


def main(path):
    S = json.load(open(path, encoding="utf-8"))
    out = [f"# 表（`scripts/report.py` が `results/summary.json` から生成・run_id {S['run_id']}）",
           "", "手で書き換えない。読みは `notes.md`。人数 6 未満は伏せて人数だけ（条件 D5）。"]
    spec = {"coauthor": (["P15", "P30"], ["main/tab", "main/recal"]),
            "cs1": (["C5"], ["main/tab", "main/recal", "all/tab", "all/recal"])}
    for ds, (panels, sets) in spec.items():
        D = S["datasets"][ds]
        out.append(f"\n## {ds}\n")
        ft = D["four_tuple"]
        u = ft["units_per_writer"]
        out.append(f"4 つ組: 人数 {ft['writers']}（全 {D['writers_total']}）・人ごとの単位 {u['median']:.0f} [{u['q25']:.0f}, {u['q75']:.0f}]・"
                   f"評価の問い {ft['labels_test']}（陽性 {ft['positives_test']}）・停滞のエピソード {ft['stall_episodes']}")
        out.append(f"\n捨てた問い: {json.dumps(D['probe_stats'], ensure_ascii=False)}・時間（秒）: 共通 {D['seconds']['pools']:.0f}・"
                   f"書き手 {D['seconds']['writers']:.0f}")
        out.append("\n### EM\n")
        out += em_tables(ds, D["em"], panels)
        out += em_diag(ds, D["em"], panels)
        out.append("\n#### 全員の共通の当てはめ（10 開始点）と w を除く共通\n")
        out.append("| 構造 | 勝った開始点 | 1 位と 2 位の差 | 収束しなかった開始点 | 減った回 | w を除く: 収束せず / 減った回 / 反復の中央値 [四分位] |")
        out.append("|---|---|---|---|---|---|")
        for s in STRUCTS:
            a, b = D["pool_full_diag"][s], D["pool_excl_diag"][s]
            it = b["iters"]
            out.append(f"| {s} | {a['winner']} | {f(a['gap12'], 4)} | {a['nonconv']} | {a['decreases']} | "
                       f"{b['nonconv']} / {b['decreases']} / {it['median']:.0f} [{it['q25']:.0f}, {it['q75']:.0f}] |")
        out.append("\n### ロジスティック\n")
        out += lg_tables(ds, D["lg"], panels, sets, ds == "cs1")
        out.append("\n#### 共通の逆向きの分け (b)（全員の評価以外の問い・標準化した尺度の係数）\n")
        out.append("| 問いの組 | 問い（陽性） | 特徴 | 1 つの切片 | 書き手の切片 | w を除く版で符号が変わる割合 |")
        out.append("|---|---|---|---|---|---|")
        for key, C in D["coef_split"].items():
            names = FEAT if key.endswith("tab") else ["logit(p_stuck)"]
            for j, nm in enumerate(names):
                out.append(f"| {key} | {C['probes']}（{C['positives']}） | {nm} | {f(C['single'][j])} | {f(C['fixed_effects'][j])} | "
                           f"{C['fe_sign_flip_share_over_w'][j]:.2f} |")
    # 副のパネル（各 k で n_w ≥ k + H の全員）は τ 他人の r1 と同じ構造の共通だけ
    for ds in ("coauthor", "cs1"):
        E = S["datasets"][ds]["em"]["secondary"]
        out.append(f"\n## {ds} 副のパネル（各 k で単位が k + 評価の数以上の全員）・EM τ 他人・全記号\n")
        out.append("| k | 人数 | 構造 | r1 | 同じ構造の共通 |")
        out.append("|---|---|---|---|---|")
        for k, Ek in E.items():
            for s in STRUCTS:
                row = Ek["structs"][s]["tau_other"]
                out.append(f"| {k} | {Ek['writers']} | {s} | {cell(row['all/self_minus_r1'])} | {cell(row['all/self_minus_pool_same'])} |")
        L = S["datasets"][ds]["lg"]["secondary"]
        out.append(f"\n## {ds} 副のパネル・ロジスティック（主の問い・V-tab）本人（λ 主）と共通（1 つの切片）の C\n")
        out.append("| k | 人数 | 本人（λ 主）C | 組のある人数 | 共通（1 つの切片）C |")
        out.append("|---|---|---|---|---|")
        for k, Pk in L.items():
            X = Pk["main/tab"]
            m, p = X["models"]["self_main"], X["models"]["pooled_single"]
            out.append(f"| {k} | {X['writers']} | {f(m['C'])} | {m['writers_with_pairs']} | {f(p['C'])} |")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
