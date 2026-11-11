"""他人で選ぶ目的を予測の良さ（平均）に替えた集計と、休止の秒の割合（conditions.md D2〜D5）。当てはめは回さない。

使い方（HP Z2）: python3 -I obj.py <raw_prefix> <coauthor_obs_dir> <cs1_obs_dir> <out_dir> [--run-id ID]
出力: <out_dir>/summary.json（集計値だけ）・tables.md・checks.json。
門: P-REPRO（sel の repro）・P-SAMESEL（中央値の目的のまま sel の summary と同じ）・P-NEVAL（評価の単位の記号の数が pickle と同じ）。
"""
import hashlib
import json
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned4  # noqa: E402
from pinned4 import SEL, ml  # noqa: E402

MUT = set()  # o1: 平均でなく中央値・o2: w 自身を入れる・o3: −∞ を平均から捨てる
_MEDIAN_SELECT = SEL._select


# ---------------------------------------------------------------- 選び（D2）
def select_agg(values, w, cands, agg):
    """w を除く v の値を agg でまとめ、いちばん大きい候補（同点は cands の先）。"""
    vs = [v for v in values if v != w or "o2" in MUT]
    best, bv = None, None
    for c in cands:
        xs = [values[v][c] for v in vs if values[v].get(c) is not None]
        if "o3" in MUT:
            xs = [x for x in xs if x != -np.inf]
        if not xs:
            continue
        with np.errstate(invalid="raise"):
            m = float(agg(xs))
        if np.isnan(m):
            raise ValueError("選びの量が NaN")
        if bv is None or m > bv:
            best, bv = c, m
    return best


def select_mean(values, w, cands):
    return select_agg(values, w, cands, np.median if "o1" in MUT else np.mean)


def summarize_with(results, ds, rng, select, with_mode=True):
    """sel の summarize を、選びの関数（と候補の並べ）だけ替えて当てる。終わったら元に戻す。"""
    saved = (SEL._select, SEL.tau_cands_mode, SEL.joint_cands_mode)
    try:
        SEL._select = select
        if not with_mode:
            base_tau = saved[1]
            SEL.tau_cands_mode = lambda: [t for t in base_tau() if t != SEL.MODE]
            SEL.joint_cands_mode = lambda: [(ml.sname(s), t) for t in SEL.tau_cands_mode()
                                            for s in sorted(ml.STRUCTS, key=lambda s: SEL.H.n_free(*s))]
        return SEL.summarize(results, ds, rng)
    finally:
        SEL._select, SEL.tau_cands_mode, SEL.joint_cands_mode = saved


def changed(results, ds):
    """2 段（他人）で、中央値の目的と平均の目的の選びが違った書き手の人数（パネル・k ごと）。"""
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    members = ml.panel_members(results, cfg, ns)
    out = {}
    for pn in SEL.MAIN_PANELS[ds]:
        out[pn] = {}
        for k, ws in members[pn].items():
            if not ws:
                continue
            jv = SEL.joint_values(results, ws, k)
            jc = SEL.joint_cands_mode()
            out[pn][str(k)] = dict(writers=len(ws), changed=sum(_MEDIAN_SELECT(jv, w, jc) != select_mean(jv, w, jc) for w in ws))
    return out


def mode_minus_pool(results, ds, rng):
    """パネルの書き手（k の和）ごとの「最頻値 − 共通」（構造ごと・全記号と押下のある記号）。"""
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    members = ml.panel_members(results, cfg, ns)
    out = {}
    for pn in SEL.MAIN_PANELS[ds]:
        ws = sorted({w for k, v in members[pn].items() for w in v})
        out[pn] = {ml.sname(s): {lab: ml.delta_stats([results[w]["em"]["mode"][ml.sname(s)][j] - results[w]["em"]["pool"][ml.sname(s)][j]
                                                      for w in ws], rng)
                                 for j, lab in enumerate(("all", "pressed"))} for s in ml.STRUCTS}
        out[pn]["writers"] = len(ws)
    return out


# ---------------------------------------------------------------- 休止の秒（D4）
def pause_share(results, ds, writers):
    """パネルの書き手ごとに、評価の単位の記号のうち押下の印が 0 の割合。P-NEVAL: 記号の数が pickle と同じ。"""
    cfg = ml.DATASETS[ds]
    ns = {w: results[w]["n"] for w in results}
    members = ml.panel_members(results, cfg, ns)
    out, neval_ok = {}, True
    for pn in SEL.MAIN_PANELS[ds]:
        ws = sorted({w for k, v in members[pn].items() for w in v})
        shares, tot_n, tot_p = [], 0, 0
        for w in ws:
            units = writers[w]
            _, test = ml.DT.split(len(units), 1, cfg["H"])
            ev = ml.Eval(ml.seqs_of([units[i] for i in test]), ml.pflags_of([units[i] for i in test]))
            n, npf = int(ev.D.M.sum()), int(ev.PF.sum())
            neval_ok = neval_ok and n == results[w]["em"]["n_eval"]
            shares.append(1.0 - npf / n)
            tot_n += n
            tot_p += npf
        q = np.quantile(shares, [0.25, 0.5, 0.75], method="inverted_cdf")
        out[pn] = dict(writers=len(ws), pooled=1.0 - tot_p / tot_n, median=float(q[1]), q25=float(q[0]), q75=float(q[2]),
                       min=float(min(shares)), max=float(max(shares)))
    return out, neval_ok


# ---------------------------------------------------------------- 本計算
def same_as_sel(datasets):
    want = json.load(open(pinned4.SEL_SUMMARY))["datasets"]
    got = json.loads(json.dumps(ml.enc(datasets), allow_nan=False))
    return got == want


def dump(obj, path):
    with open(path, "w", newline="\n") as f:
        json.dump(ml.enc(obj), f, indent=1, ensure_ascii=False, allow_nan=False)


def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    raw, paths, out = argv[0], {"coauthor": argv[1], "cs1": argv[2]}, argv[3]
    repo = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    for p in [raw] + list(paths.values()):
        if os.path.realpath(p).startswith(repo + os.sep):
            sys.exit("書き手ごとの値かデータが repo の中を指している")
    os.makedirs(out, exist_ok=True)
    seed = pinned4.SEED
    C = dict(run_id=run_id, pkl_sha256={}, p_repro={}, p_samesel=None, p_neval={})
    med, S = {}, dict(run_id=run_id, datasets_mean={}, datasets_mean_nomode={}, changed={}, mode_minus_pool={}, pause={})
    for ds in ("coauthor", "cs1"):
        p = raw + "." + ds + ".pkl"
        C["pkl_sha256"][ds] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        with open(p, "rb") as fp:
            results = pickle.load(fp)  # mode の本計算が書いた自前の pickle（人は開かない）
        C["p_repro"][ds] = SEL.repro(results, ds, seed)
        dump(C, os.path.join(out, "checks.json"))
        if not C["p_repro"][ds]:
            sys.exit("P-REPRO が外れた（%s）" % ds)
        med[ds] = summarize_with(results, ds, np.random.default_rng([seed + 4, 1]), _MEDIAN_SELECT)
        S["datasets_mean"][ds] = summarize_with(results, ds, np.random.default_rng([seed + 4, 1]), select_mean)
        S["datasets_mean_nomode"][ds] = summarize_with(results, ds, np.random.default_rng([seed + 4, 1]), select_mean, with_mode=False)
        S["changed"][ds] = changed(results, ds)
        S["mode_minus_pool"][ds] = mode_minus_pool(results, ds, np.random.default_rng([seed + 4, 2]))
        writers, _ = ml.load(ds, paths[ds], seed)  # 人は開かない
        S["pause"][ds], C["p_neval"][ds] = pause_share(results, ds, writers)
        dump(C, os.path.join(out, "checks.json"))
        if not C["p_neval"][ds]:
            sys.exit("P-NEVAL が外れた（%s）: 評価の単位の記号の数が pickle と違う" % ds)
    C["p_samesel"] = bool(same_as_sel(med))
    dump(C, os.path.join(out, "checks.json"))
    if not C["p_samesel"]:
        sys.exit("P-SAMESEL が外れた（中央値の目的の集計が sel の summary と違う）")
    S["readings"] = SEL.readings(S["datasets_mean"])
    S["readings_median"] = SEL.readings(med)
    dump(S, os.path.join(out, "summary.json"))
    write_tables(S, med, os.path.join(out, "tables.md"))


def write_tables(S, med, path):
    S = json.loads(json.dumps(ml.enc(S)))
    med = json.loads(json.dumps(ml.enc(med)))
    cv = SEL.cellv
    L = ["# 他人で選ぶ目的を平均に替えた主の表と、最頻値 − 共通・休止の秒の割合（集計値だけ）", "",
         "差は 1 記号あたりの対数尤度（全記号）・書き手ごとの差の中央値（良 = > 0 の割合）。中央値 = 計算 3 の目的・平均 = この試験の目的（最頻値を候補に入れる）。", "",
         "## 2 段（他人）", "",
         "| パネル | k | n | 中央値: 本人 − 最頻値 | 平均: 本人 − 共通 | 平均: 本人 − 最頻値 | 平均: 本人 − r1 | 平均: 選ばれた τ の領域 | 平均: 構造 | 選びが違った人数 | 形（平均） | 形（中央値） | 副（最頻値なし・平均）: 本人 − 共通 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for ds, panels in S["datasets_mean"].items():
        for pn, P in panels.items():
            for k, E in P.items():
                T, M = E["two_stage_other"], med[ds][pn][k]["two_stage_other"]
                N = S["datasets_mean_nomode"][ds][pn][k]["two_stage_other"]
                rg = " ".join("%s:%d" % kv for kv in T["chosen_region"].items() if kv[1])
                L.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %d | %s | %s | %s |" % (
                    pn, k, E["writers"], cv(M["all/self_minus_mode_same"]), cv(T["all/self_minus_pool_same"]),
                    cv(T["all/self_minus_mode_same"]), cv(T["all/self_minus_r1"]), rg,
                    " ".join("%s:%d" % kv for kv in T["chosen_struct"].items()), S["changed"][ds][pn][k]["changed"],
                    S["readings"][pn]["k_forms"][k], S["readings_median"][pn]["k_forms"][k], cv(N["all/self_minus_pool_same"])))
    L += ["", "## 最頻値 − 共通（パネルの書き手・構造ごと）", "", "| パネル | n | 構造 | 全記号 | 押下のある記号 |", "|---|---|---|---|---|"]
    for ds, panels in S["mode_minus_pool"].items():
        for pn, P in panels.items():
            for name, st in P.items():
                if name == "writers":
                    continue
                L.append("| %s | %d | %s | %s | %s |" % (pn, P["writers"], name, cv(st["all"]), cv(st["pressed"])))
    L += ["", "## 休止の秒の割合（評価の単位の記号のうち、直近 30 秒の窓に押下が無い秒）", "",
          "| パネル | n | 全員を合わせた割合 | 書き手ごとの中央値 [四分位] | 最小〜最大 |", "|---|---|---|---|---|"]
    for ds, panels in S["pause"].items():
        for pn, x in panels.items():
            L.append("| %s | %d | %.3f | %.3f [%.3f, %.3f] | %.3f〜%.3f |" % (pn, x["writers"], x["pooled"], x["median"], x["q25"], x["q75"], x["min"], x["max"]))
    L += ["", "## 読み（D5 の機械の当て・平均の目的）", "", "```", json.dumps(S["readings"], indent=1, ensure_ascii=False), "```"]
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
