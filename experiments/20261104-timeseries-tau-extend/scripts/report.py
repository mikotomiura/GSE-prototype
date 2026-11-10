"""results/summary.json（集計値だけ）から notes 用の表を Markdown で書き出す（EM だけ・ロジスティックは計算しない）。

書き手ごとの値（repo の外の writer_values）は読まない。数の読み替えはせず、summary の値をそのまま丸めて並べる。
使い方: python -I scripts/report.py results/summary.json > tables.md
"""
import json
import sys

STRUCTS = ["hmm3", "ar1", "ar2", "ar3"]
OPPS = ["r1", "pool_same", "pool_hmm3", "fb"]
OPP_JA = {"r1": "r1", "pool_same": "同じ構造の共通", "pool_hmm3": "K=3 の共通", "fb": "F-b"}
TAUS = ["0", "100", "1000", "10000", "30000", "100000", "300000", "1000000", "inf"]
TAU_JA = {"inf": "∞"}


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


def med(st):
    if st is None:
        return "—"
    return "伏せ" if st.get("suppressed") else f(st["median"])


def counts(c):
    if c is None:
        return "—"
    if c.get("suppressed"):
        return f"伏せ（{c['n']} 人）"
    return "・".join(f"{TAU_JA.get(k, k)}:{v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1]))


def region(c):
    if c is None:
        return "—"
    if c.get("suppressed"):
        return f"伏せ（{c['n']} 人）"
    return f"中 {c['inside']}・下の端 {c['low_end']}・上の有限の端 {c['high_finite_end']}・∞ {c['inf']}"


def qn(v):
    if v is None:
        return "—"
    if v.get("suppressed"):
        return f"伏せ（{v['n']}）"
    return f"{v['median']:.0f} [{v['q25']:.0f}, {v['q75']:.0f}]"


def em_tables(name, E, panels):
    out = []
    for pn in panels:
        P = E[pn]
        out.append(f"\n#### {name} {pn} 学習・評価の記号の数（書き手の中央値 [四分位]）\n")
        out.append("| k | 人数 | 学習の記号 | 評価の記号 |")
        out.append("|---|---|---|---|")
        for k, Ek in P.items():
            out.append(f"| {k} | {Ek['writers']} | {qn(Ek['n_train'])} | {qn(Ek['n_eval'])} |")
        for lab in ("all", "pressed"):
            out.append(f"\n#### {name} {pn} τ 他人（主）・{'全記号' if lab == 'all' else '窓に押下のある記号'}"
                       "（Δ = 本人 − 相手・1 記号あたりの対数尤度・正が本人の良い側・中央値 [四分位] 良 = 良い側の割合）\n")
            out.append("| k | 人数 | 構造 | " + " | ".join(OPP_JA[o] for o in OPPS) + " | 選ばれた τ | τ の位置 |")
            out.append("|---|---|---|" + "---|" * len(OPPS) + "---|---|")
            for k, Ek in P.items():
                for s in STRUCTS:
                    St = Ek["structs"][s]
                    row = St["tau_other"]
                    cells = [cell(row[f"{lab}/self_minus_{o}"]) for o in OPPS]
                    out.append(f"| {k} | {Ek['writers']} | {s} | " + " | ".join(cells) +
                               f" | {counts(St['chosen_tau_other'])} | {region(St['chosen_tau_other_region'])} |")
        out.append(f"\n#### {name} {pn} τ 他人・全記号の中央値の区間（書き手の復元抽出 2,000 回）\n")
        out.append("| k | 構造 | r1 | 同じ構造の共通 | K=3 の共通 | F-b |")
        out.append("|---|---|---|---|---|---|")
        for k, Ek in P.items():
            for s in STRUCTS:
                row = Ek["structs"][s]["tau_other"]
                cs = []
                for o in OPPS:
                    st = row[f"all/self_minus_{o}"]
                    cs.append("—" if not st or st.get("suppressed") or not st.get("ci") else f"[{f(st['ci'][0])}, {f(st['ci'][1])}]")
                out.append(f"| {k} | {s} | " + " | ".join(cs) + " |")
        out.append(f"\n#### {name} {pn} 共通 − r1（書き手ごとの差・w を除く共通・全記号 / 押下のある記号）\n")
        out.append("| k | 構造 | 全記号 | 押下のある記号 |")
        out.append("|---|---|---|---|")
        for k, Ek in P.items():
            for s in STRUCTS:
                pr = Ek["structs"][s]["pool_minus_r1"]
                out.append(f"| {k} | {s} | {cell(pr['all'], ci=True)} | {cell(pr['pressed'])} |")
        out.append(f"\n#### {name} {pn} τ 固定 9 行・τ 他人・τ 本人 CV（副）・全記号の Δ の中央値（相手: r1 / 同じ構造の共通）\n")
        out.append("| k | 構造 | " + " | ".join(f"τ={TAU_JA.get(t, t)}" for t in TAUS) + " | τ 他人 | τ 本人 CV | 本人 CV が選んだ τ | τ の位置 |")
        out.append("|---|---|" + "---|" * (len(TAUS) + 4))
        for k, Ek in P.items():
            for s in STRUCTS:
                St = Ek["structs"][s]

                def two(r):
                    if r not in St:
                        return "—"
                    return f"{med(St[r]['all/self_minus_r1'])} / {med(St[r]['all/self_minus_pool_same'])}"
                out.append(f"| {k} | {s} | " + " | ".join(two("tau_" + t) for t in TAUS) +
                           f" | {two('tau_other')} | {two('tau_cv')} | {counts(St.get('chosen_tau_cv'))} | "
                           f"{region(St.get('chosen_tau_cv_region'))} |")
        out.append(f"\n#### {name} {pn} 2 段の行・全記号（相手ごとの Δ）\n")
        out.append("| k | 行 | " + " | ".join(OPP_JA[o] for o in OPPS) + " | 選ばれた構造 | 選ばれた τ | τ の位置 |")
        out.append("|---|---|" + "---|" * len(OPPS) + "---|---|---|")
        for k, Ek in P.items():
            for key, rn, ja in (("other", "two_stage_other", "2 段（他人）"),
                                ("struct_other_tau_cv", "two_stage_struct_other_tau_cv", "2 段（構造は他人・τ は本人 CV）")):
                T = Ek["two_stage"].get(key)
                if T is None:
                    continue
                cells = [cell(T[rn][f"all/self_minus_{o}"]) for o in OPPS]
                out.append(f"| {k} | {ja} | " + " | ".join(cells) +
                           f" | {counts(T['chosen_struct'])} | {counts(T['chosen_tau'])} | {region(T['chosen_tau_region'])} |")
        out.append(f"\n#### {name} {pn} K 本人 CV（k ≥ 3・族ごと・全記号・各構造の τ は τ 他人）\n")
        out.append("| k | 族 | " + " | ".join(OPP_JA[o] for o in OPPS) + " | 選ばれた構造 |")
        out.append("|---|---|" + "---|" * len(OPPS) + "---|")
        for k, Ek in P.items():
            for fam, Kc in Ek["kcv"].items():
                cells = [cell(Kc["k_cv"][f"all/self_minus_{o}"]) for o in OPPS]
                out.append(f"| {k} | {fam} | " + " | ".join(cells) + f" | {counts(Kc['chosen_struct'])} |")
    return out


def em_diag(name, E, panels):
    out = [f"\n#### {name} 本人の当てはめの診断（有限の τ ごとに k と構造を通して足した数）\n",
           "| パネル | τ | 収束しなかった開始点 | 目的が減った回 | 勝った開始点 | 1 位と 2 位の差の中央値の範囲 |",
           "|---|---|---|---|---|---|"]
    for pn in panels:
        for t in TAUS[:-1]:
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


def main(path):
    S = json.load(open(path, encoding="utf-8"))
    out = [f"# 表（`scripts/report.py` が `results/summary.json` から生成・run_id {S['run_id']}）",
           "", "手で書き換えない。読みは `notes.md`。人数 6 未満は伏せて人数だけ（前回の条件 D5）。"]
    spec = {"coauthor": ["P15", "P30", "secondary"], "cs1": ["C5", "secondary"]}
    for ds, panels in spec.items():
        if ds not in S["datasets"]:
            continue
        D = S["datasets"][ds]
        out.append(f"\n## {ds}\n")
        ft = D["four_tuple"]
        u = ft["units_per_writer"]
        out.append(f"4 つ組: 人数 {ft['writers']}（全 {D['writers_total']}）・人ごとの単位 {u['median']:.0f} [{u['q25']:.0f}, {u['q75']:.0f}]・"
                   f"評価の記号 {ft['eval_symbols']}（問いは{ft['questions']}）・停滞のエピソード {ft['stall_episodes']}")
        out.append(f"\n時間（秒）: 共通 {D['seconds']['pools']:.0f}・書き手 {D['seconds']['writers']:.0f}")
        out += em_tables(ds, D["em"], panels)
        out += em_diag(ds, D["em"], panels)
        out.append("\n#### 全員の共通の当てはめ（10 開始点）と w を除く共通\n")
        out.append("| 構造 | 勝った開始点 | 1 位と 2 位の差 | 収束しなかった開始点 | 減った回 | w を除く: 収束せず / 減った回 / 反復の中央値 [四分位] |")
        out.append("|---|---|---|---|---|---|")
        for s in STRUCTS:
            a, b = D["pool_full_diag"][s], D["pool_excl_diag"][s]
            it = b["iters"]
            its = "—" if not it or it.get("suppressed") else f"{it['median']:.0f} [{it['q25']:.0f}, {it['q75']:.0f}]"
            out.append(f"| {s} | {a['winner']} | {f(a['gap12'], 4)} | {a['nonconv']} | {a['decreases']} | "
                       f"{b['nonconv']} / {b['decreases']} / {its} |")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
