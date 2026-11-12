"""B1 の対称版（conditions.md の追記「B1 の対称版」・判断 19）: 本人の当てはめも共通と同じ基の倍率で当て直す。
CoAuthor P15・構造 ar3・倍率 1（照らし用）と 0.03。

使い方（HP Z2）: python3 -I sym.py <coauthor_work_obs> <raw_prefix> <bvals.pkl> <sym_out.pkl> <out_dir> <jobs> [--run-id ID]
出力: <sym_out.pkl>（repo の外・人は開かない）・<out_dir>/sym_summary.json・sym_tables.md・sym_check.json。
"""
import hashlib
import json
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ab as AB  # noqa: E402
import compute as CP  # noqa: E402
import pinned4  # noqa: E402
from pinned4 import H, ml  # noqa: E402

DT = ml.DT
MUT = set()  # y1: 折り目の乱数を引かない・y2: 基に倍率を掛けない・y3: 選びに w を入れる
SEED = pinned4.SEED
AR3 = ("ar", 3)
ALPHA = "0.03"
DS = "coauthor"


# ---------------------------------------------------------------- 当てはめ
def prior_sym(kind, K, tau, sbar, alpha):
    """倍率 α の基 + τ S̄（τ = 0 は基だけ）。α = 1 では H.make_prior と同じ。y2 は基に倍率を掛けない。"""
    pr = H.base_prior(kind, K)
    if "y2" not in MUT:
        pr = {k: v * alpha for k, v in pr.items()}
    if tau > 0:
        for key in H.keys_of(kind):
            pr[key] = pr[key] + tau * sbar[key]
    return pr


def fit_self_sym(kind, K, D, pool_m, sb, rng, h, T, alpha):
    """mode の fit_self_all と同じ開始点・同じ乱数の引き方で、事前分布だけを prior_sym にする。"""
    out = {}
    m0, _ = H.fit([("pool", pool_m), ("rand", H.random_model(kind, K, rng, r1=T, r0=h))], D, prior_sym(kind, K, 0, None, alpha))
    out[0] = m0
    for tau in ml.TAUS_FIT[1:]:
        out[tau], _ = H.fit([("pool", pool_m), ("self0", m0)], D, prior_sym(kind, K, tau, sb, alpha))
    return out


def replay_writer(units, H_, ks_all, ks_fit, pool_m, sb, rng, alpha):
    """mode の em_writer（structs = None・do_folds = True）と同じ並べで乱数を引き直し、ar3 の ks_fit の本人だけを当てはめる。
    返り値: {k: {τ: [全記号, 押下]}}。"""
    n = len(units)
    _, test = DT.split(n, 1, H_)
    ev = ml.Eval(ml.seqs_of([units[i] for i in test]), ml.pflags_of([units[i] for i in test]))
    out = {}
    for s in ml.PREV_STRUCTS:
        if s in ml.DROPPED:
            ml.discard_draws(s, units, H_, ks_all, rng, True)
            continue
        kind, K = s
        for k in ks_all:
            train, _ = DT.split(n, k, H_)
            tr = ml.seqs_of([units[i] for i in train])
            _, h, T = H.r0_r1(tr)
            if s == AR3 and k in ks_fit:
                fits = fit_self_sym(kind, K, H.Data(tr, chunk=H.CHUNK), pool_m, sb, rng, h, T, alpha)
                out[str(k)] = {str(t): ev.ll(fits[t]) for t in ml.TAUS_FIT}
            else:
                H.random_model(kind, K, rng, r1=T, r0=h)
            if "y1" in MUT:
                continue
            for fit_i, _ in DT.folds(train):
                _, hf, Tf = H.r0_r1(ml.seqs_of([units[i] for i in fit_i]))
                H.random_model(kind, K, rng, r1=Tf, r0=hf)
    return out


def job_excl_sb(job):
    """w を除く共通（ar3・倍率 α）と S̄ と評価。"""
    writers = CP.writers_of(job)
    H_ = ml.DATASETS[job["ds"]]["H"]
    seqs = ml.seqs_of(ml.pool_units(writers, H_, exclude=job["w"]))
    D = H.Batched(seqs, chunk=H.CHUNK)
    m, _ = H.fit([("full_pool", job["start"])], D, CP.prior_alpha("ar", 3, job["alpha"]))
    S, _ = H.counts(m, D)
    return dict(m=m, sb=H.sbar_of(S, D.nobs), ll=CP.eval_of(writers[job["w"]], H_).ll(m))


def job_self(job):
    writers = CP.writers_of(job)
    rng = np.random.default_rng([job["seed"] + 10, job["wseq"]])
    return replay_writer(writers[job["w"]], ml.DATASETS[job["ds"]]["H"], job["ks_all"], job["ks_fit"], job["pool_m"],
                         job["sb"], rng, job["alpha"])


# ---------------------------------------------------------------- 集計（conditions の追記「行と量」）
def sym_picks(ws, k, R, S03, P03):
    """対称 2 段（本人' − r1 で選ぶ）と対称 τ 他人（本人' − 共通(0.03) で選ぶ）の選び。w を除く v の中央値（y3 は w を入れる）。"""
    cands = ml.tau_cands()
    selfp = lambda v, t: P03[v][0] if t == ml.INF else S03[v][str(k)][t][0]  # noqa: E731
    mem = lambda w: [v for v in ws if v != w or "y3" in MUT]  # noqa: E731
    jv = {v: {t: selfp(v, t) - R[v]["em"]["k"][str(k)]["r1"][0] for t in cands} for v in ws}
    tv = {v: {t: (0.0 if t == ml.INF else selfp(v, t) - P03[v][0]) for t in cands} for v in ws}
    return {w: AB.pick(jv, mem(w), cands) for w in ws}, {w: AB.pick(tv, mem(w), cands) for w in ws}


def sym_cell(ws, k, R, S03, P03, rng):
    """R: mode の pickle。S03: {w: {k: {τ: [..]}}}（倍率 0.03 の本人）。P03: {w: [..]}（共通 0.03）。"""
    selfp = lambda v, t: P03[v][0] if t == ml.INF else S03[v][str(k)][t][0]  # noqa: E731
    r1 = lambda v: R[v]["em"]["k"][str(k)]["r1"][0]  # noqa: E731
    pool1 = lambda v: R[v]["em"]["pool"]["ar3"][0]  # noqa: E731
    pj, pt = sym_picks(ws, k, R, S03, P03)
    st = lambda d: ml.delta_stats(d, rng)  # noqa: E731
    return dict(
        joint=dict(self_minus_pool03=st([selfp(w, pj[w]) - P03[w][0] for w in ws]),
                   self_minus_r1=st([selfp(w, pj[w]) - r1(w) for w in ws]),
                   self_minus_pool1=st([selfp(w, pj[w]) - pool1(w) for w in ws]),
                   chosen_tau_region=ml.tau_region(pj.values())),
        tau_other=dict(self_minus_pool03=st([0.0 if pt[w] == ml.INF else selfp(w, pt[w]) - P03[w][0] for w in ws]),
                       chosen_tau_region=ml.tau_region(pt.values())),
        refit_minus_old={t: st([S03[w][str(k)][t][0] - R[w]["em"]["k"][str(k)]["self"]["ar3"][t][0] for w in ws])
                         for t in ("100000", "1000000")},
        pool03_minus_pool1=st([P03[w][0] - pool1(w) for w in ws]))


def sym_form(R0, Rs):
    if Rs <= 0:
        return "消えたまま"
    return "戻る" if Rs >= R0 / 2 else "縮む"


def write_tables(S, path):
    L = ["# B1 の対称版（本人も倍率 0.03 で当て直す・CoAuthor P15・ar3・集計値だけ）", "",
         "| k | 今 R0 | 対称 2 段 本人' − 共通(0.03) | 本人' − r1 | 本人' − 共通(1) | τ の領域 | 対称 τ 他人 本人' − 共通(0.03) | 共通(0.03) − 共通(1) | 形 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k, C in S["cells"].items():
        j = C["joint"]
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k, AB.fm(C["current"]), AB.st(j["self_minus_pool03"]), AB.st(j["self_minus_r1"]), AB.st(j["self_minus_pool1"]),
            " ".join("%s:%d" % kv for kv in j["chosen_tau_region"].items() if kv[1]), AB.st(C["tau_other"]["self_minus_pool03"]),
            AB.st(C["pool03_minus_pool1"]), S["readings"]["k_forms"][k]))
    L += ["", "パネルの形: %s" % S["readings"]["panel_form"]]
    open(path, "w", newline="\n").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- 本計算
def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    coa, raw, bvals, sout, out, jobs = argv[0], argv[1], argv[2], argv[3], argv[4], int(argv[5])
    pkl = raw + "." + DS + ".pkl"
    if not all(AB.outside_repo(p) for p in (pkl, bvals, sout)):
        sys.exit("書き手ごとの値が repo の中を指している")
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
    rc = json.load(open(os.path.join(out, "repro_check.json")))  # A・B の本計算の照らし（repo の中・集計だけ）
    if sha(pkl) != CP.PKL_SHA[DS] or sha(bvals) != rc["bvals_sha256"]:
        sys.exit("pickle か B の値が A・B の本計算と違う")
    with open(pkl, "rb") as fp:
        R = pickle.load(fp)  # mode の本計算の自前の pickle（人は開かない）
    with open(bvals, "rb") as fp:
        BV = pickle.load(fp)  # A・B の本計算の自前の pickle（人は開かない）
    cfg = ml.DATASETS[DS]
    H_ = cfg["H"]
    members = ml.panel_members(R, cfg, {w: R[w]["n"] for w in R})
    ws = next(iter(members["P15"].values()))
    ks_fit = sorted(members["P15"])
    if set(AB.alpha_star(BV[DS]["pool"], ws, "ar3").values()) != {ALPHA}:
        sys.exit("P15 の ar3 の α* が 0.03 でない書き手がいる（条件の追記の前提と違う）")
    elig = sorted(R)
    ck = dict(run_id=run_id)
    T = dict(run_id=run_id)
    t0 = time.time()
    V = {}
    with ProcessPoolExecutor(jobs, initializer=ml._init, initargs=({DS: coa}, SEED, [])) as ex:
        for a in ("1", ALPHA):
            full = ex.submit(CP.job_full, dict(ds=DS, s=AR3, alpha=float(a), seed=SEED)).result()
            ex_res = list(ex.map(job_excl_sb, [dict(ds=DS, w=w, start=full, alpha=float(a)) for w in ws], chunksize=1))
            pools = dict(zip(ws, ex_res))
            T["pool_%s_sec" % a] = time.time() - t0
            jl = [dict(ds=DS, w=w, wseq=elig.index(w), seed=SEED, alpha=float(a), pool_m=pools[w]["m"], sb=pools[w]["sb"],
                       ks_all=[k for k in cfg["grid"] if k <= R[w]["n"] - H_], ks_fit=ks_fit) for w in ws]
            selfs = dict(zip(ws, ex.map(job_self, jl, chunksize=1)))
            T["self_%s_sec" % a] = time.time() - t0
            V[a] = dict(pool={w: pools[w]["ll"] for w in ws}, self=selfs)
            if a == "1":
                cmp = [(selfs[w][str(k)][t], R[w]["em"]["k"][str(k)]["self"]["ar3"][t]) for w in ws for k in ks_fit
                       for t in map(str, ml.TAUS_FIT)]
                cmp_p = [(pools[w]["ll"], R[w]["em"]["pool"]["ar3"]) for w in ws]
                ck["p_repro_self"] = dict(passed=all(CP.same_bits(x, y) for x, y in cmp + cmp_p), compared=len(cmp) + len(cmp_p),
                                          max_abs_diff=float(max(abs(x[0] - y[0]) for x, y in cmp + cmp_p)))
                AB.write_json(ck, os.path.join(out, "sym_check.json"))
                if not ck["p_repro_self"]["passed"]:
                    sys.exit("P-REPRO-SELF が外れた（倍率 1 の引き直しが mode の本人と同じにならない）。止めて報告する")
                print("P-REPRO-SELF 通過（%.0f 秒）" % (time.time() - t0), flush=True)
            else:
                cmp = [(pools[w]["ll"], BV[DS]["pool"][w]["ar3"][ALPHA]) for w in ws]
                ck["p_repro_b1"] = dict(passed=all(CP.same_bits(x, y) for x, y in cmp), compared=len(cmp),
                                        max_abs_diff=float(max(abs(x[0] - y[0]) for x, y in cmp)))
                AB.write_json(ck, os.path.join(out, "sym_check.json"))
                if not ck["p_repro_b1"]["passed"]:
                    sys.exit("P-REPRO-B1 が外れた（倍率 0.03 の共通が B1 の値と違う）。止めて報告する")
    with open(sout, "wb") as fp:
        pickle.dump(V, fp)
    ck["sym_values_sha256"] = sha(sout)
    AB.write_json(ck, os.path.join(out, "sym_check.json"))
    AB.write_json(T, os.path.join(out, "sym_timing.json"))
    rng = np.random.default_rng([SEED + 4, 5])
    mode_em = json.load(open(pinned4.MODE_SUMMARY))["datasets"][DS]["em"]["P15"]
    S03, P03 = V[ALPHA]["self"], V[ALPHA]["pool"]
    cells = {}
    for k in ks_fit:
        C = sym_cell(ws, k, R, S03, P03, rng)
        C["current"] = mode_em[str(k)]["two_stage"]["other"]["two_stage_other"]["all/self_minus_pool_same"]["median"]
        cells[str(k)] = C
    forms = {k: sym_form(C["current"], C["joint"]["self_minus_pool03"]["median"]) for k, C in cells.items()}
    S = dict(run_id=run_id, writers=len(ws), alpha=ALPHA, cells=cells,
             readings=dict(k_forms=forms, panel_form=AB.panel_form(forms)))
    AB.write_json(S, os.path.join(out, "sym_summary.json"))
    write_tables(json.loads(json.dumps(ml.enc(S))), os.path.join(out, "sym_tables.md"))


if __name__ == "__main__":
    main()
