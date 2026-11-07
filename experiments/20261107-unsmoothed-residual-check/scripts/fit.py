"""列（o・u・n）ごとに、主のパネルだけで EM を当てはめ、尤度の差を集計し、母数を repo の外の npz に書く（conditions D2〜D4）。

数式は tau-extend の hmm2.py・data.py・ml.py を読み込んで使う（pinned.py が SHA-256 を照らす）。新しく書くのは、
範囲を絞った駆動（作る k・行・相手）と、作らない番の乱数の捨て方と、母数の保存だけ。
乱数の流れは tau-extend と同じ: 全員の共通は [SEED + 11, si]、書き手ごとの 1 本の流れ [SEED + 10, 書き手の通し番号] を
ml-improve の 6 構造の順 → k（tau-extend の格子の全部）→ τ = 0 の乱数の開始点 → 折り目 で引く。外した構造（hmm6・hmm10）・
作らない k・作らない折り目の番では、tau-extend と同じ形の乱数の開始点だけを引いて捨てる（AR の開始点は r1・r0 に依るので、
同じ学習の記号から r1・r0 を作って渡す）。

使い方:
  python3 -I fit.py <coauthor|cs1> <col> <work> <sidecar|-> <seed> <out_dir> <raw_dir> <jobs> [--run-id ID]
出力: <out_dir>/parts/fit.<データ>.<列>.json（集計値だけ）、<raw_dir>/unsmoothed_residual_writer_values.<データ>.<列>.json と
<raw_dir>/unsmoothed_residual_params.<データ>.<列>.npz（書き手ごと・repo の外・人は開かない・書き手の ID は書かず通し番号だけ）。
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I では自分のディレクトリが入らない
import pinned  # noqa: E402
from pinned import DT, H, ml
import load as L

PANELS = {"coauthor": ("P15", 20, [1, 5, 15]), "cs1": ("C5", 6, [1, 5])}
OPPS = ("r1", "pool_same")
MUT = set()  # m49: npz に τ の鍵を 1 つずらして書く・m50: 作らない k の乱数を捨てない


def set_mut(mut):
    MUT.clear()
    MUT.update(mut)
    ml.set_mut([])


def ntok(seqs):
    return int(sum(len(s) for s in seqs))


# ---------------------------------------------------------------- 1 書き手
def fit_writer(units, H_, ks_all, ks_make, pools, rng):
    """1 書き手の当てはめ。ks_all: tau-extend の格子のうちこの書き手に当たる k（乱数の並べのため）。ks_make: 作る k。
    返り値: (結果, 母数)。結果の形は tau-extend の em_writer の結果と同じ（fb・fold を除く）。
    評価の記号が 0 の書き手・学習の記号が 0 の k は、そのセルを None にする（n で起こりうる・conditions D1）。"""
    n = len(units)
    _, test = DT.split(n, 1, H_)
    te = [units[i] for i in test]
    n_eval = ntok(ml.seqs_of(te))
    ev = ml.Eval(ml.seqs_of(te), ml.pflags_of(te)) if n_eval else None
    res = dict(pool={}, k={}, n_eval=n_eval)
    par = dict(pool={}, self={}, r1={})
    trains = {}
    for k in ks_all:
        train, test2 = DT.split(n, k, H_)
        assert test2 == test
        seqs = ml.seqs_of([units[i] for i in train])
        _, h, T = H.r0_r1(seqs)
        trains[k] = (train, seqs, h, T)
        if k in ks_make:
            nt = ntok(seqs)
            if ev is None or nt == 0:
                res["k"][str(k)] = None
            else:
                res["k"][str(k)] = dict(r1=ev.ll_r1(h, T), self={}, diag={}, n_train=nt)
                par["r1"][str(k)] = (h, T)
    for s in ml.PREV_STRUCTS:
        if s in ml.DROPPED:
            ml.discard_draws(s, units, H_, ks_all, rng, True)
            continue
        kind, K = s
        name = ml.sname(s)
        pool_m, sb = pools[name]
        if ev is not None:
            res["pool"][name] = ev.ll(pool_m)
        par["pool"][name] = pool_m
        for k in ks_all:
            train, seqs, h, T = trains[k]
            make = k in ks_make
            if not make and "m50" in MUT:
                continue
            rk = res["k"].get(str(k)) if make else None
            if rk is not None:
                D = H.Data(seqs, chunk=H.CHUNK)
                fits, diag = ml.fit_self_all(kind, K, D, pool_m, sb, rng, h, T)
                rk["self"][name] = {str(t): ev.ll(fits[t]) for t in ml.TAUS_FIT}
                rk["self"][name][ml.INF] = ev.ll(pool_m)
                rk["diag"][name] = {str(t): dict(winner=diag[t]["winner"], gap12=diag[t]["gap12"], nonconv=diag[t]["nonconv"],
                                                 decreases=diag[t]["decreases"]) for t in ml.TAUS_FIT}
                par["self"].setdefault(name, {})[str(k)] = {str(t): fits[t] for t in ml.TAUS_FIT}
            else:
                H.random_model(kind, K, rng, r1=T, r0=h)  # τ = 0 の乱数の開始点（作らない k・空のセル）
            for fit_i, _ in DT.folds(train):  # 折り目は作らない（乱数の開始点だけを引いて捨てる）
                _, hf, Tf = H.r0_r1(ml.seqs_of([units[i] for i in fit_i]))
                H.random_model(kind, K, rng, r1=Tf, r0=hf)
    return res, par


# ---------------------------------------------------------------- 母数の保存（npz）
def flat_params(wseq, par):
    """{鍵: 配列}。鍵は w<通し番号>/pool/<構造>/<母数>・w/self/<構造>/k<k>/t<τ>/<母数>・w/r1/k<k>/h|T。m49 は τ を 1 つずらす。"""
    out = {}
    pre = "w%d/" % wseq
    for name, m in par["pool"].items():
        for key in H.keys_of(m["kind"]):
            out[pre + "pool/%s/%s" % (name, key)] = m[key]
    for name, byk in par["self"].items():
        for k, byt in byk.items():
            taus = [str(t) for t in ml.TAUS_FIT]
            for i, t in enumerate(taus):
                src = taus[(i + 1) % len(taus)] if "m49" in MUT else t
                m = byt[src]
                for key in H.keys_of(m["kind"]):
                    out[pre + "self/%s/k%s/t%s/%s" % (name, k, t, key)] = m[key]
    for k, (h, T) in par["r1"].items():
        out[pre + "r1/k%s/h" % k] = h
        out[pre + "r1/k%s/T" % k] = T
    return out


def kind_of(name):
    return "hmm" if name.startswith("hmm") else "ar"


def model_from(z, pre, name):
    kind = kind_of(name)
    m = dict(kind=kind)
    for key in H.keys_of(kind):
        m[key] = z[pre + "/" + key]
    return m


def get_pool(z, wseq, name):
    return model_from(z, "w%d/pool/%s" % (wseq, name), name)


def get_self(z, wseq, name, k, t):
    """τ = ∞ は w を除く共通の母数（conditions D3・tau-extend と同じ）。"""
    if t == ml.INF:
        return get_pool(z, wseq, name)
    return model_from(z, "w%d/self/%s/k%s/t%s" % (wseq, name, k, t), name)


def get_r1(z, wseq, k):
    return z["w%d/r1/k%s/h" % (wseq, k)], z["w%d/r1/k%s/T" % (wseq, k)]


# ---------------------------------------------------------------- ワーカー
_U = {}


def _init(ds, work, side, col, seed, mut):
    set_mut(mut)
    _U[ds] = L.load_column(ds, work, side, seed, col)
    ml._W[ds] = _U[ds]


def eval_writer(job):
    t0 = time.time()
    set_mut(job["mut"])
    units = _U[job["ds"]][job["w"]] if job.get("units") is None else job["units"]
    rng = np.random.default_rng([job["seed"] + 10, job["wseq"]])
    res, par = fit_writer(units, ml.DATASETS[job["ds"]]["H"], job["ks_all"], job["ks_make"], job["pools"], rng)
    return dict(n=len(units), em=res, sec=time.time() - t0), par


# ---------------------------------------------------------------- 集計（tau-extend の summarize_em の部品を使う）
def cell_ok(results, w, k):
    return results[w]["em"]["k"].get(str(k)) is not None


def em_rows(results, ws, k, rows, rng):
    """rows: {行: {書き手: (構造名, τ)}}。相手は r1 と同じ構造の共通（conditions D3）。全記号と窓に押下のある記号。"""
    out = {}
    for r, pick in rows.items():
        o = {}
        for j, lab in enumerate(("all", "pressed")):
            for opp in OPPS:
                d = []
                for w in ws:
                    name, t = pick[w] if pick[w] is not None else (None, None)
                    if t is None:
                        d.append(None)
                        continue
                    rk = results[w]["em"]["k"][str(k)]
                    me = rk["self"][name][t][j]
                    other = rk["r1"][j] if opp == "r1" else results[w]["em"]["pool"][name][j]
                    d.append(None if me is None or other is None else me - other)
                o[lab + "/self_minus_" + opp] = ml.delta_stats(d, rng)
        out[r] = o
    return out


def summarize(results, ds, ns, rng):
    """返り値: (集計, 選び)。選び: {k: {"tau_other": {構造: {w: τ}}, "two_stage": {w: (構造, τ)}}}（書き手ごと・repo の外）。"""
    pn, nmin, ks = PANELS[ds]
    panel = [w for w in results if ns[w] >= nmin]
    taus_desc = sorted(ml.TAU_KEYS, key=ml.tau_val, reverse=True)
    P, picks = {}, {}
    for k in ks:
        ws = [w for w in panel if cell_ok(results, w, k)]
        E = dict(writers=len(ws), missing=len(panel) - len(ws), structs={}, two_stage={},
                 n_train=ml.q([results[w]["em"]["k"][str(k)]["n_train"] for w in ws]),
                 n_eval=ml.q([results[w]["em"]["n_eval"] for w in ws]))
        pk = dict(tau_other={}, two_stage={})
        for s in ml.STRUCTS:
            name = ml.sname(s)
            vals = ml.em_values(results, ws, k, s)
            rows = {"tau_" + t: {w: t for w in ws} for t in ml.TAU_KEYS}
            rows["tau_other"] = {w: ml.select_other(vals, w, taus_desc) for w in ws}
            pk["tau_other"][name] = rows["tau_other"]
            St = em_rows(results, ws, k, {r: {w: (name, t) for w, t in m.items()} for r, m in rows.items()}, rng)
            St["chosen_tau_other"] = ml.count_vals(rows["tau_other"].values())
            St["chosen_tau_other_region"] = ml.tau_region(rows["tau_other"].values())
            St["pool_minus_r1"] = {lab: ml.delta_stats(ml.pool_r1_values(results, ws, k, name, j), rng)
                                   for j, lab in enumerate(("all", "pressed"))}
            St["diag"] = ml.em_diag(results, ws, k, name)
            E["structs"][name] = St
        jv = ml.joint_values(results, ws, k)
        jc = ml.joint_cands()
        pick = {w: ml.select_joint(jv, w, jc) for w in ws}
        pk["two_stage"] = pick
        T = em_rows(results, ws, k, {"two_stage_other": pick}, rng)
        T["chosen_struct"] = ml.count_vals(p[0] if p else None for p in pick.values())
        T["chosen_tau"] = ml.count_vals(p[1] if p else None for p in pick.values())
        T["chosen_tau_region"] = ml.tau_region(p[1] if p else None for p in pick.values())
        E["two_stage"]["other"] = T
        P[str(k)] = E
        picks[str(k)] = pk
    return {pn: P}, picks


# ---------------------------------------------------------------- 本計算
def check_outside_repo(path):
    repo = os.path.normcase(os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../..")))
    p = os.path.normcase(os.path.realpath(path))
    if p == repo or p.startswith(repo + os.sep):
        sys.exit("書き手ごとの値の置き場が repo の中を指している（repo の外だけ）")


def run(ds, col, work, side, seed, out, raw_dir, jobs, run_id):
    check_outside_repo(raw_dir)
    cfg = ml.DATASETS[ds]
    H_ = cfg["H"]
    pn, nmin, ks = PANELS[ds]
    t0 = time.time()
    writers = L.load_column(ds, work, side, seed, col)
    ns = [len(ss) for ss in writers]
    elig = [i for i, n in enumerate(ns) if n >= H_ + 1]
    panel = [w for w in elig if ns[w] >= nmin]
    for w in panel:
        assert all(DT.check_split(ns[w], k, H_) for k in cfg["grid"] if k <= ns[w] - H_)
    ex = ProcessPoolExecutor(jobs, initializer=_init, initargs=(ds, work, side, col, seed, sorted(MUT)))
    try:
        full = list(ex.map(ml.fit_pool_full, [dict(ds=ds, si=ml.SEQ_NO[s], seed=seed) for s in ml.STRUCTS]))
        pj = [dict(ds=ds, w=w, start=full[si][0]) for w in panel for si in range(len(ml.STRUCTS))]
        pres = list(ex.map(ml.fit_pool_excl, pj, chunksize=1))
        pools, pdiag = {}, []
        it = iter(pres)
        for w in panel:
            pools[w] = {}
            for s in ml.STRUCTS:
                m, sb, d = next(it)
                pools[w][ml.sname(s)] = (m, sb)
                pdiag.append((ml.sname(s), d))
        t1 = time.time()
        wseq = {w: j for j, w in enumerate(elig)}  # tau-extend と同じ書き手の通し番号（elig の中の位置）
        jl = [dict(ds=ds, w=w, wseq=wseq[w], seed=seed, ks_all=[k for k in cfg["grid"] if k <= ns[w] - H_], ks_make=ks,
                   pools=pools[w], mut=sorted(MUT)) for w in panel]
        outs = list(ex.map(eval_writer, jl, chunksize=1))
    finally:
        ex.shutdown()
    results = {w: r for w, (r, _) in zip(panel, outs)}
    flat = {}
    for w, (_, par) in zip(panel, outs):
        flat.update(flat_params(wseq[w], par))
    base = os.path.join(raw_dir, "unsmoothed_residual_%s.%s.%s")
    for suffix in (("params", ".npz"), ("writer_values", ".json")):
        check_outside_repo(base % (suffix[0], ds, col) + suffix[1])  # 出力ファイルの実体（リンクの先）も repo の外
    np.savez_compressed(base % ("params", ds, col) + ".npz", **flat)
    rng = np.random.default_rng(seed + 4)
    em, picks = summarize(results, ds, ns, rng)
    json.dump(dict(results={str(wseq[w]): r for w, r in results.items()},
                   picks={k: dict(tau_other={nm: {str(wseq[w]): t for w, t in m.items()} for nm, m in pk["tau_other"].items()},
                                  two_stage={str(wseq[w]): p for w, p in pk["two_stage"].items()})
                          for k, pk in picks.items()},
                   panel=[wseq[w] for w in panel], run_id=run_id),
              open(base % ("writer_values", ds, col) + ".json", "w"))
    D = dict(em=em)
    D["pool_full_diag"] = {ml.sname(s): dict(winner=d["winner"], gap12=d["gap12"], nonconv=d["nonconv"], decreases=d["decreases"])
                           for s, (_, d) in zip(ml.STRUCTS, full)}
    D["pool_excl_diag"] = {ml.sname(s): dict(nonconv=int(sum(d["nonconv"] for n_, d in pdiag if n_ == ml.sname(s))),
                                             decreases=int(sum(d["decreases"] for n_, d in pdiag if n_ == ml.sname(s))),
                                             iters=ml.q([d["iters"][0] for n_, d in pdiag if n_ == ml.sname(s)]))
                           for s in ml.STRUCTS}
    D["four_tuple"] = dict(writers=len(panel), units_per_writer=ml.q([ns[w] for w in panel]),
                           eval_symbols=int(sum(results[w]["em"]["n_eval"] for w in panel)),
                           questions="使わない", stall_episodes="使わない（0）")
    D["writers_total"] = len(writers)
    D["seconds"] = dict(pools=t1 - t0, writers=time.time() - t1, per_writer=ml.q([r["sec"] for r in results.values()]))
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    json.dump(dict(run_id=run_id, dataset=ds, column=col, pin_sha256=pinned.SHA, fit=D),
              open(os.path.join(out, "parts", "fit.%s.%s.json" % (ds, col)), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id")
        run_id = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    ds, col, work, side, seed, out, raw_dir, jobs = argv[:8]
    if col not in L.COLS:
        sys.exit("列は o・u・n のどれか")
    run(ds, col, work, None if side == "-" else side, int(seed), out, raw_dir, int(jobs), run_id)
