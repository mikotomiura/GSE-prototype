"""parts/ の集計と repo の外の書き手ごとの値から、summary.json・readings.json・tables.md・図の元の CSV を作る（conditions D4・D5・V3）。

使い方: python3 -I analyze.py <out_dir> <raw_dir> <seed> [--run-id ID] [--cols A1,A30,...]
書くのは集計値だけ（書き手・セッションの番号を書かない）。書き手ごとの値は読むだけで、出力に写さない。
内部の照合: 書き手ごとの値から作った G・C2a の中央値が fit の summary の中央値と一致するか（外れれば終了コード 3）。
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swap  # noqa: E402,F401
from swap import load_dose as LD  # noqa: E402
from pinned import ml  # noqa: E402
import readings as RD  # noqa: E402

KS = ["1", "5", "15"]
MAIN_COLS = ["A1", "A5", "A10", "A15", "A30", "C5", "C10", "C15", "C30"]
WKEYS = ["G", "C2a", "R1P", "C2b", "JR", "R_ar3", "R_ar3_t10000", "G_t10000"]


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def tau_w(t):
    return None if t is None else (0.0 if t == ml.INF else float(t))


def writer_vals(WV, k):
    out = {key: {} for key in WKEYS}
    tau = {"hmm3": {}, "ar3": {}}
    ntr = {}
    for wseq in WV["panel"]:
        w = str(wseq)
        em = WV["results"][w]["em"]
        rk = em["k"].get(k)
        if rk is None:
            continue
        pool, S = em["pool"], rk["self"]
        pk = WV["picks"][k]
        th, ta = pk["tau_other"]["hmm3"].get(w), pk["tau_other"]["ar3"].get(w)
        if th is not None:
            out["G"][w] = S["hmm3"][th][0] - pool["hmm3"][0]
            out["C2a"][w] = S["hmm3"][th][0] - rk["r1"][0]
        out["R1P"][w] = rk["r1"][0] - pool["hmm3"][0]
        out["G_t10000"][w] = S["hmm3"]["10000"][0] - pool["hmm3"][0]
        if ta is not None:
            out["R_ar3"][w] = S["ar3"][ta][0] - pool["ar3"][0]
        out["R_ar3_t10000"][w] = S["ar3"]["10000"][0] - pool["ar3"][0]
        js = pk["two_stage"].get(w)
        if js is not None:
            out["C2b"][w] = S[js[0]][js[1]][0] - rk["r1"][0]
            out["JR"][w] = S[js[0]][js[1]][0] - pool[js[0]][0]
        tau["hmm3"][w], tau["ar3"][w] = th, ta
        ntr[w] = rk["n_train"]
    return out, tau, ntr


def weights(tau, ntr):
    """データの重み N / (N + τ)。N は学習の記号の数の中央値（セルの書き手）、τ は書き手ごとに選ばれた値（∞ は重み 0）。"""
    if not ntr:
        return None
    N = RD.med(list(ntr.values()))
    out = {}
    for s, tw in tau.items():
        ws = [N / (N + tau_w(t)) if t != ml.INF else 0.0 for t in tw.values() if t is not None]
        out[s] = dict(N_median=N, chosen=RD.med(ws), tau_10000=N / (N + 10000.0))
    return out


def q(xs):
    return ml.q([x for x in xs if x is not None])


def main(argv):
    out, raw, seed = argv[0], argv[1], int(argv[2])
    run_id = argv[argv.index("--run-id") + 1] if "--run-id" in argv else None
    cols = argv[argv.index("--cols") + 1].split(",") if "--cols" in argv else LD.ORDER
    P = os.path.join(out, "parts")
    S, V = dict(run_id=run_id, columns={}), dict(cells={k: {key: {} for key in WKEYS + ["G_nohead", "C2a_nohead"]} for k in KS},
                                                   constr={q_: {} for q_ in ("M_diff", "D_s", "rho_x", "rho_y")},
                                                   desc=dict(w_ar3={}, w_ar3_t10000={}, w_hmm3={}, resid_diff={}))
    consist_checked, consist_bad = 0, 0
    for col in cols:
        fp = os.path.join(P, "fit.coauthor.%s.json" % col)
        if not os.path.exists(fp):
            continue
        fitp, resp, extp = jload(fp), jload(os.path.join(P, "res.coauthor.%s.json" % col)), jload(
            os.path.join(P, "extra.coauthor.%s.json" % col))
        for d in (fitp, resp, extp):
            if run_id is not None and d.get("run_id") != run_id:
                raise SystemExit("parts の run_id が今回の実行と違う: %s" % col)
        WV = jload(os.path.join(raw, "unsmoothed_residual_writer_values.coauthor.%s.json" % col))
        EX = jload(os.path.join(raw, "extra_writer_values.coauthor.%s.json" % col))
        if run_id is not None and (WV.get("run_id") != run_id or EX.get("run_id") != run_id):
            raise SystemExit("書き手ごとの値の run_id が今回の実行と違う: %s" % col)
        em = fitp["fit"]["em"]["P15"]
        C = dict(fit=fitp["fit"], residual=resp["residual"], npz_check=resp["npz_check"], extra=extp, cells={})
        for k in KS:
            wv, tau, ntr = writer_vals(WV, k)
            for key in WKEYS:
                V["cells"][k][key][col] = wv[key]
            for key in ("G_nohead", "C2a_nohead"):
                V["cells"][k][key][col] = {w: r["k"][k][key] for w, r in EX["writers"].items() if k in r["k"]}
            # 内部の照合: 書き手ごとの値の中央値が fit の summary と一致するか
            for key, path in (("G", "all/self_minus_pool_same"), ("C2a", "all/self_minus_r1")):
                ref = em[k]["structs"]["hmm3"]["tau_other"][path]
                if ref and not ref.get("suppressed"):
                    consist_checked += 1
                    consist_bad += int(q(list(wv[key].values()))["median"] != ref["median"])
            wt = weights(tau, ntr)
            for name, src in (("w_ar3", "ar3"), ("w_hmm3", "hmm3")):
                V["desc"][name].setdefault(col, {})[k] = wt[src]["chosen"] if wt else None
            V["desc"]["w_ar3_t10000"].setdefault(col, {})[k] = wt["ar3"]["tau_10000"] if wt else None
            rd = {}
            for ax in ("x", "y"):
                rd[ax] = RD.med([r["k"][k]["rho_self_hmm3"][ax] - r["rho_pool_hmm3"][ax] for r in EX["writers"].values()
                                 if k in r["k"] and r["k"][k]["rho_self_hmm3"][ax] is not None and r["rho_pool_hmm3"][ax] is not None])
            V["desc"]["resid_diff"].setdefault(col, {})[k] = rd
            T = em[k]["two_stage"]["other"]
            C["cells"][k] = dict(
                writers=em[k]["writers"], missing=em[k]["missing"],
                quantities={key: q(list(wv[key].values())) for key in WKEYS},
                nohead={key: q(list(V["cells"][k][key][col].values())) for key in ("G_nohead", "C2a_nohead")},
                chosen_tau_hmm3=em[k]["structs"]["hmm3"]["chosen_tau_other"], chosen_tau_ar3=em[k]["structs"]["ar3"]["chosen_tau_other"],
                joint_chosen_struct=T["chosen_struct"], weights=wt,
                rho_self_minus_pool_hmm3=rd,
                rho_self_hmm3={ax: q([r["k"][k]["rho_self_hmm3"][ax] for r in EX["writers"].values() if k in r["k"]]) for ax in ("x", "y")})
        Wx = EX["writers"]
        V["constr"]["M_diff"][col] = {w: r["M_diff"] for w, r in Wx.items()}
        V["constr"]["D_s"][col] = {w: r.get("D_s") for w, r in Wx.items()}
        for ax in ("x", "y"):
            V["constr"]["rho_" + ax][col] = {w: (r.get("rho_pool_hmm3") or {}).get(ax) for w, r in Wx.items()}
        nser = sum(r["n_series"] for r in Wx.values())
        C["construction"] = dict(
            M=q([r["M"] for r in Wx.values()]), M_shuf=q([r["M_shuf"] for r in Wx.values()]),
            M_diff=q([r["M_diff"] for r in Wx.values()]), M_shuf_sd=q([r["M_shuf_sd"] for r in Wx.values()]),
            M_plugin=q([r.get("M_plugin") for r in Wx.values()]), pairs=q([r.get("pairs") for r in Wx.values()]),
            cells_used=q([r.get("cells") for r in Wx.values()]),
            const_series_share=(sum(r["const_series"] for r in Wx.values()) / nser) if nser else None,
            entropy=q([r["entropy"] for r in Wx.values()]),
            D_s=q([r.get("D_s") for r in Wx.values()]),
            rho_pool_hmm3={ax: q([(r.get("rho_pool_hmm3") or {}).get(ax) for r in Wx.values()]) for ax in ("x", "y")},
            rho_valid_share={ax: q([(r.get("rho_pool_hmm3") or {}).get("valid_" + ax) for r in Wx.values()]) for ax in ("x", "y")},
            writers_with_M=sum(1 for r in Wx.values() if r["M_diff"] is not None))
        S["columns"][col] = C
    need = set(MAIN_COLS) | {"P1-%d" % s for s in RD.STEPS} | {"P3-%d" % s for s in RD.STEPS}
    R = None
    if need <= set(S["columns"]):
        V["desc"]["stretch_C30_sec"] = (S["columns"]["C30"]["extra"]["panel_series_rows_median"] or {}).get("median")
        Vm = dict(cells={k: V["cells"][k] for k in RD.CELLS}, constr=V["constr"], desc=V["desc"])
        R = RD.assemble(Vm, seed, ml)
        # 記述: 列どうしの対応のある差（共通の集合）・良い側の数
        for k in RD.CELLS:
            G = V["cells"][k]["G"]
            ws = RD.cell_set(Vm, k) or []
            R["cells"][k]["count_G_C30_gt_A30"] = sum(1 for w in ws if G["C30"][w] > G["A30"][w])
            R["cells"][k]["count_G_A1_gt_A30"] = sum(1 for w in ws if G["A1"][w] > G["A30"][w])
            Rr = V["cells"][k]["R_ar3"]
            wr = sorted(set(Rr.get("C30", {})) & set(Rr.get("A30", {})), key=int)
            R["cells"][k]["stay_R_ar3_30"] = RD.med([Rr["C30"][w] - Rr["A30"][w] for w in wr])
            R["cells"][k]["C2a_medians"] = {c: RD.med_on(Vm, k, "C2a", c) for c in MAIN_COLS}
            R["cells"][k]["R1P_medians"] = {c: RD.med_on(Vm, k, "R1P", c) for c in MAIN_COLS}
            R["cells"][k]["G_medians"] = {c: RD.med_on(Vm, k, "G", c) for c in sorted(need)}
    S["internal_consistency"] = dict(checked=consist_checked, mismatched=consist_bad)
    S["readings"] = R
    json.dump(S, open(os.path.join(out, "summary.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=float)
    if R is not None:
        json.dump(R, open(os.path.join(out, "readings.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=float)
        write_figure_csv(S, R, os.path.join(out, "figure_medians.csv"))
    open(os.path.join(out, "tables.md"), "w", encoding="utf-8").write(tables(S, R))
    print(json.dumps(dict(columns=len(S["columns"]), internal_checked=consist_checked, internal_mismatched=consist_bad,
                          type=None if R is None else R["type"])))
    return 0 if consist_checked > 0 and consist_bad == 0 else 3


def med_of(c):
    return None if c is None or c.get("suppressed") else c.get("median")


def write_figure_csv(S, R, path):
    rows = []
    for col, C in S["columns"].items():
        arm, s = LD.parse(col)
        con = C["construction"]
        for k in RD.CELLS:
            qd = C["cells"][k]["quantities"]
            rows.append(dict(column=col, arm=arm, step=s, k=k, G_median=med_of(qd["G"]), R_ar3_median=med_of(qd["R_ar3"]),
                             D_s_median=med_of(con["D_s"]), rho_x_median=med_of(con["rho_pool_hmm3"]["x"]),
                             rho_y_median=med_of(con["rho_pool_hmm3"]["y"]), M_diff_median=med_of(con["M_diff"])))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fmt(x):
    if x is None:
        return "—"
    if isinstance(x, float):
        return "%.4f" % x
    return str(x)


def tables(S, R):
    L = ["# 表（analyze.py が集計から作る・集計値だけ）", ""]
    L += ["## 列ごとの量（中央値・パネル P15）", "", "| 列 | k | 人数 | G | C2a | r1 − 共有 hmm3 | C2b | ジョイントの残り | R_ar3 | R_ar3（τ = 10,000） | G（τ = 10,000） | G（頭を除く） |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for col, C in S["columns"].items():
        for k in KS:
            c = C["cells"][k]
            qd = c["quantities"]
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                col, k, c["writers"], *[fmt(med_of(qd[x])) for x in ("G", "C2a", "R1P", "C2b", "JR", "R_ar3", "R_ar3_t10000", "G_t10000")],
                fmt(med_of(c["nohead"]["G_nohead"]))))
    L += ["", "## 作りの確かめの量（列ごと・k に依らない）", "",
          "| 列 | M | M_shuf | M − M_shuf | M_shuf の SD | plug-in | 組 | セル | 一定の系列の割合 | エントロピー | D_s | ρ_h x | ρ_h y | 有効な組 x | 有効な組 y | 系列の行（パネル） | 切れ端の系列 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for col, C in S["columns"].items():
        c, e = C["construction"], C["extra"]
        L.append("| %s | %s |" % (col, " | ".join(fmt(v) for v in (
            med_of(c["M"]), med_of(c["M_shuf"]), med_of(c["M_diff"]), med_of(c["M_shuf_sd"]), med_of(c["M_plugin"]), med_of(c["pairs"]),
            med_of(c["cells_used"]), c["const_series_share"], med_of(c["entropy"]), med_of(c["D_s"]), med_of(c["rho_pool_hmm3"]["x"]),
            med_of(c["rho_pool_hmm3"]["y"]), med_of(c["rho_valid_share"]["x"]), med_of(c["rho_valid_share"]["y"]),
            med_of(e["panel_series_rows_median"]), e["series_over_chunk"]))))
    L += ["", "## データの重みと選ばれた構造（k = 5 / 15）", "", "| 列 | k | N（中央値） | hmm3 の重み（τ 他人） | ar3 の重み（τ 他人） | ar3 の重み（τ = 10,000） | ジョイントで選ばれた構造 |",
          "|---|---|---|---|---|---|---|"]
    for col, C in S["columns"].items():
        for k in ("5", "15"):
            w = C["cells"][k]["weights"] or {}
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (col, k, fmt((w.get("hmm3") or {}).get("N_median")),
                                                              fmt((w.get("hmm3") or {}).get("chosen")), fmt((w.get("ar3") or {}).get("chosen")),
                                                              fmt((w.get("ar3") or {}).get("tau_10000")),
                                                              json.dumps(C["cells"][k]["joint_chosen_struct"], ensure_ascii=False)))
    if R is not None:
        L += ["", "## 読み（D5・機械で組み立てた結果）", "", "- G の語: %s（%s）" % (R["word"], R["word_en"]),
              "- 型: %s（%s）" % (R["type"], R["type_name"]),
              "- 作りの確かめ: %s・D_s と ρ_h: %s" % ("通る" if R["construction"]["passed"] else "外れる",
                                                "見込みどおり" if R["construction"]["as_expected"] else "見込みと違った"),
              "- 頭を除く採点の語: %s・τ = 10,000 の語: %s・列 C′1 の語: %s・列 C′3 の語: %s" % (
                  R["word_nohead"], R["word_tau10000"], R["word_C1"], R["word_C3"]),
              "- 境の歩み s*: %s・分類: %s" % (R["boundary"]["s_star"], json.dumps(R["boundary"]["classes"], ensure_ascii=False)), ""]
        L += ["| k | m | 語 | shrink(30) | stay(30) | φ(30) | stay > 0 の数 | 区間 | 1 人抜きの一致 |", "|---|---|---|---|---|---|---|---|---|"]
        for k in RD.CELLS:
            c = R["cells"][k]
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
                k, c["m"], c["word"], fmt((c.get("shrink") or {}).get("30")), fmt((c.get("stay") or {}).get("30")),
                fmt((c.get("phi") or {}).get("30")), c.get("stay_pos"), R["interval"][k]["ci"], R["loo"][k]["same"], R["loo"][k]["m"]))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
