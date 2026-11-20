"""round 7 の計算 A（入れ替えの対照）と B（先頭の記号を除いた残り）（conditions.md の追記「入れ替えの対照（A）と
先頭の記号を除いた残り（B）」・判断 37 と 38）。CoAuthor P15 の 17 人・k = 5 と 15。

使い方（HP Z2）: python3 -I r7.py <coauthor_work_obs> <raw_prefix> <bvals.pkl> <sym_vals.pkl> <r7_out.pkl> <out_dir> <jobs> [--run-id ID]
出力: <r7_out.pkl>（repo の外・人は開かない）・<out_dir>/r7_summary.json・r7_tables.md・r7_check.json・r7_timing.json。
"""
import hashlib
import json
import math
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
import sym as SM  # noqa: E402
from pinned4 import H, ml  # noqa: E402

DT = ml.DT
MUT = set()  # f1: 先頭を外さない・f2: 折り目の乱数を引かない・f3: 倍率を本人に渡さない・f4: 主を先頭を除く量で選ぶ・
#              f5: 組の共通から v を外さない・f6: 入れ替えのデータに w の学習の単位・f7: 入れ替えの τ に v の選び・
#              f8: v の中央値でまとめる・f9: A の形の比べを D > Rs / 2 にする
BUDGET_HOURS = 4.0
SEED = pinned4.SEED
AR3 = ("ar", 3)
ALPHA = "0.03"
DS = "coauthor"
KS = [5, 15]
SYM_VALS_SHA = "8596a3c79c16377ba6239f5e79ef094b7b636e0755402ab6df1a7eae366fa32b"  # 対称版の本計算（sym_check.json）
INF = ml.INF


# ---------------------------------------------------------------- 評価（先頭を除く量を足す）
class Eval2(ml.Eval):
    """ml.Eval と同じ系列・同じ計算に、各系列の 0 番目の位置を外した量を 3 つ目として足す。f1 は外さない。"""

    def __init__(self, seqs, pflags):
        super().__init__(seqs, pflags)
        self.NF = self.D.M.copy()
        if "f1" not in MUT:
            self.NF[:, 0] = False

    def of_lp(self, lp):
        r = super().of_lp(lp)
        r.append(float(lp[self.NF].sum() / self.NF.sum()))
        return r

    def first_share(self):
        return float(self.D.M.shape[0] / self.D.M.sum())


def eval2_of(units, H_):
    _, test = DT.split(len(units), 1, H_)
    return Eval2(ml.seqs_of([units[i] for i in test]), ml.pflags_of([units[i] for i in test]))


def same2(x, y):
    """[全記号, 押下, 先頭を除く] の前の 2 つが [全記号, 押下] とビットまで同じ。"""
    return CP.same_bits(list(x[:2]), list(y))


# ---------------------------------------------------------------- 共通（w を除く・w と v を除く）
def pool_units2(writers, H_, excl):
    """excl の書き手を除く評価以外の単位（ml.pool_units と同じ並べ）。f5 は先頭の 1 人だけを除く。"""
    ex = set(excl[:1] if "f5" in MUT else excl)
    return [u for j, ss in enumerate(writers) if j not in ex for u in ml.non_eval(ss, H_)]


def job_full(job):
    return CP.job_full(job)


def job_excl(job):
    """excl を除く共通（開始点は同じ倍率の全員の共通の解）・S̄。score なら excl[0] の評価の単位で評価する。"""
    writers = CP.writers_of(job)
    H_ = ml.DATASETS[job["ds"]]["H"]
    m0 = job["start"]
    kind, K = m0["kind"], len(m0["pi"])
    D = H.Batched(ml.seqs_of(pool_units2(writers, H_, job["excl"])), chunk=H.CHUNK)
    m, _ = H.fit([("full_pool", m0)], D, CP.prior_alpha(kind, K, job["alpha"]))
    S, _ = H.counts(m, D)
    out = dict(m=m, sb=H.sbar_of(S, D.nobs))
    if job.get("score"):
        out["ll"] = eval2_of(writers[job["excl"][0]], H_).ll(m)
    return out


# ---------------------------------------------------------------- 本人の引き直し（B）
def replay(units, H_, ks_all, ks_fit, pools, rng, alpha, structs_fit):
    """mode の em_writer（structs = None・do_folds = True）と同じ並べで乱数を引き直し、structs_fit × ks_fit の本人だけを
    当てはめる。pools: {構造名: (w を除く共通の母数, S̄)}。返り値: self {構造名: {k: {τ: [全, 押下, 先頭除く]}}}・
    r1 {k: [..]}・first_share。f2 は折り目の乱数を引かない・f3 は倍率を 1 にする。"""
    n = len(units)
    ev = eval2_of(units, H_)
    a = 1.0 if "f3" in MUT else alpha
    out, r1 = {}, {}
    for s in ml.PREV_STRUCTS:
        if s in ml.DROPPED:
            ml.discard_draws(s, units, H_, ks_all, rng, True)
            continue
        kind, K = s
        name = ml.sname(s)
        for k in ks_all:
            train, _ = DT.split(n, k, H_)
            tr = ml.seqs_of([units[i] for i in train])
            _, h, T = H.r0_r1(tr)
            if k in ks_fit and str(k) not in r1:
                r1[str(k)] = ev.ll_r1(h, T)
            if s in structs_fit and k in ks_fit:
                fits = SM.fit_self_sym(kind, K, H.Data(tr, chunk=H.CHUNK), pools[name][0], pools[name][1], rng, h, T, a)
                out.setdefault(name, {})[str(k)] = {str(t): ev.ll(fits[t]) for t in ml.TAUS_FIT}
            else:
                H.random_model(kind, K, rng, r1=T, r0=h)
            if "f2" in MUT:
                continue
            for fit_i, _ in DT.folds(train):
                _, hf, Tf = H.r0_r1(ml.seqs_of([units[i] for i in fit_i]))
                H.random_model(kind, K, rng, r1=Tf, r0=hf)
    return dict(self=out, r1=r1, first_share=ev.first_share())


def job_replay(job):
    writers = CP.writers_of(job)
    H_ = ml.DATASETS[job["ds"]]["H"]
    units = writers[job["w"]]
    rng = np.random.default_rng([job["seed"] + 10, job["wseq"]])
    ks_all = [k for k in ml.DATASETS[job["ds"]]["grid"] if k <= len(units) - H_]
    return replay(units, H_, ks_all, job["ks_fit"], job["pools"], rng, job["alpha"], job["structs"])


# ---------------------------------------------------------------- 入れ替え（A）
def fit_prior(kind, K, D, pool_m, sb, rng, h, T, tau, alpha):
    """mode の fit_self_all と同じ開始点の形で τ（文字列）の当てはめ 1 つ（τ = 0 はその解そのもの）。"""
    m0, _ = H.fit([("pool", pool_m), ("rand", H.random_model(kind, K, rng, r1=T, r0=h))], D, SM.prior_sym(kind, K, 0, None, alpha))
    if tau == "0":
        return m0
    m, _ = H.fit([("pool", pool_m), ("self0", m0)], D, SM.prior_sym(kind, K, float(tau), sb, alpha))
    return m


def pair_job(w, v, wseq, vseq, picks, pool_wv, ks, ds=DS, writers=None):
    """picks: {k: {書き手: τ}}（対称 2 段の選び）。入れ替えの τ は w の選び（f7 は v の選び）。"""
    who = v if "f7" in MUT else w
    return dict(ds=ds, w=w, v=v, wseq=wseq, vseq=vseq, ks=ks, tau={str(k): picks[str(k)][who] for k in ks},
                pool_m=pool_wv["m"], sb=pool_wv["sb"], seed=SEED, writers=writers)


def job_pair(job):
    """入れ替え swap（v の学習の k 単位）と本人''（w 自身の学習の k 単位）。事前は 0.03 × 基 + τ_w S̄_{-w,-v}。
    採点は w の評価の単位。τ_w = ∞ は None（呼ぶ側が本人' の値に置く）。f6 は入れ替えのデータに w の単位を使う。"""
    writers = CP.writers_of(job)
    H_ = ml.DATASETS[job["ds"]]["H"]
    w, v = job["w"], job["v"]
    ev = eval2_of(writers[w], H_)
    out = {}
    for k in job["ks"]:
        tau = job["tau"][str(k)]
        res = {}
        for role, src, off in (("swap", w if "f6" in MUT else v, 30), ("self2", w, 31)):
            if tau == INF:
                res[role] = None
                continue
            units = writers[src]
            train, _ = DT.split(len(units), k, H_)
            tr = ml.seqs_of([units[i] for i in train])
            _, h, T = H.r0_r1(tr)
            rng = np.random.default_rng([job["seed"] + off, job["wseq"], job["vseq"], k])
            m = fit_prior("ar", 3, H.Data(tr, chunk=H.CHUNK), job["pool_m"], job["sb"], rng, h, T, tau, float(ALPHA))
            res[role] = ev.ll(m)
        out[str(k)] = res
    return out


# ---------------------------------------------------------------- 集計
def swap_mean(xs):
    """v の平均（−∞ が 1 つでもあれば −∞）。f8 は中央値。"""
    if "f8" in MUT:
        return float(np.median(xs))
    if any(x == -np.inf for x in xs):
        return -np.inf
    return float(np.mean(xs))


def a_cell(ws, k, picks, selfp, pool03, PAIR, rng):
    """picks: {w: τ}・selfp: {w: 本人' の全記号}・pool03: {w: 共通(0.03) の全記号}・PAIR: {(w, v): {k: {swap, self2}}}。"""
    sw, dp, beat, npair = {}, {}, 0, 0
    for w in ws:
        vs = [v for v in ws if v != w]
        if picks[w] == INF:
            sw[w], dp[w] = selfp[w], 0.0
            continue
        xs = [PAIR[(w, v)][str(k)]["swap"][0] for v in vs]
        sw[w] = swap_mean(xs)
        dps = [PAIR[(w, v)][str(k)]["self2"][0] - PAIR[(w, v)][str(k)]["swap"][0] for v in vs]
        dp[w] = float(np.median(dps)) if "f8" in MUT else float(np.mean(dps))
        beat += sum(x > selfp[w] for x in xs)
        npair += len(xs)
    st = lambda d: ml.delta_stats(d, rng)  # noqa: E731
    return dict(D=st([selfp[w] - sw[w] for w in ws]), Rs=st([selfp[w] - pool03[w] for w in ws]),
                E=st([sw[w] - pool03[w] for w in ws]), Dp=st([dp[w] for w in ws]),
                swap_neg_inf=int(sum(sw[w] == -np.inf for w in ws)),
                pair_swap_beats_self_share=(beat / npair if npair else None),
                tau_counts={t: int(sum(picks[w] == t for w in ws)) for t in sorted(set(picks.values()), key=ml.tau_val)})


def a_form(D, Rs):
    if D <= 0:
        return "担わない"
    ok = D > Rs / 2 if "f9" in MUT else D >= Rs / 2
    return "担う" if ok else "一部"


def b_form(F, R):
    if F <= 0:
        return "消える"
    return "残る" if F >= R / 2 else "縮む"


def panel_form(forms):
    return forms["5"] if forms["5"] == forms["15"] else "k で分かれる"


def b_fix_cell(ws, k, R, FX, P1, rng):
    """固定の平滑。R: mode の pickle（選びは全記号）。FX: {w: replay の返り値}・P1: {w: {構造名: [全, 押下, 先頭除く]}}。"""
    jc = ml.joint_cands()
    val = lambda v, n, t, j: P1[v][n][j] if t == INF else FX[v]["self"][n][str(k)][t][j]  # noqa: E731
    jv_all = ml.joint_values(R, ws, k)
    jv_nf = {v: {(n, t): val(v, n, t, 2) - FX[v]["r1"][str(k)][2] for n, t in jc} for v in ws}
    p_all = {w: ml.select_joint(jv_all, w, jc) for w in ws}
    p_nf = {w: ml.select_joint(jv_nf, w, jc) for w in ws}
    main = p_nf if "f4" in MUT else p_all
    rem = lambda p, w, j: val(w, p[w][0], p[w][1], j) - P1[w][p[w][0]][j]  # noqa: E731
    st = lambda d: ml.delta_stats(d, rng)  # noqa: E731
    return dict(R=st([rem(main, w, 0) for w in ws]), F=st([rem(main, w, 2) for w in ws]),
                F_reselected=st([rem(p_nf, w, 2) for w in ws]),
                first_share_median=float(np.median([FX[w]["first_share"] for w in ws])),
                chosen=dict(structs={n: int(sum(main[w][0] == n for w in ws)) for n in sorted({main[w][0] for w in ws})},
                            tau_region=ml.tau_region([main[w][1] for w in ws])))


def b_sym_cell(ws, k, R, S03, P03, SY, PS, rng):
    """対称版。選びは保存済みの全記号の値（sym_picks の対称 2 段）。SY: {w: replay の返り値}・PS: {w: [全, 押下, 先頭除く]}。"""
    pj, _ = SM.sym_picks(ws, k, R, S03, P03)
    val = lambda v, t, j: PS[v][j] if t == INF else SY[v]["self"]["ar3"][str(k)][t][j]  # noqa: E731
    cands = ml.tau_cands()
    jv_nf = {v: {t: val(v, t, 2) - SY[v]["r1"][str(k)][2] for t in cands} for v in ws}
    p_nf = {w: AB.pick(jv_nf, [v for v in ws if v != w], cands) for w in ws}
    main = p_nf if "f4" in MUT else pj
    rem = lambda p, w, j: val(w, p[w], j) - PS[w][j]  # noqa: E731
    st = lambda d: ml.delta_stats(d, rng)  # noqa: E731
    return dict(R=st([rem(main, w, 0) for w in ws]), F=st([rem(main, w, 2) for w in ws]),
                F_reselected=st([rem(p_nf, w, 2) for w in ws]),
                first_share_median=float(np.median([SY[w]["first_share"] for w in ws])),
                chosen=dict(tau_region=ml.tau_region([main[w] for w in ws])))


def write_tables(S, path):
    S = json.loads(json.dumps(ml.enc(S)))
    L = ["# round 7 の計算 A（入れ替えの対照）と B（先頭の記号を除いた残り）（CoAuthor P15・集計値だけ）", "",
         "## B 先頭の記号を除いた残り", "",
         "| 版 | k | 全記号の残り R | 先頭を除く残り F | 副 選び直し | 先頭の記号の割合（中央値） | 形 |",
         "|---|---|---|---|---|---|---|"]
    for ver in ("fix", "sym"):
        for k, C in S["B"][ver]["cells"].items():
            L.append("| %s | %s | %s | %s | %s | %.2e | %s |" % (ver, k, AB.st(C["R"]), AB.st(C["F"]), AB.st(C["F_reselected"]),
                                                             C["first_share_median"], S["B"][ver]["k_forms"][k]))
    L += ["", "パネルの形: 固定の平滑 %s・対称版 %s" % (S["B"]["fix"]["panel_form"], S["B"]["sym"]["panel_form"]), "",
          "## A 入れ替えの対照（ar3・倍率 0.03・v は 16 人の平均）", "",
          "| k | Rs 本人' − 共通(0.03) | D 本人' − 入れ替え | E 入れ替え − 共通(0.03) | 副 Dp 本人'' − 入れ替え | 入れ替えが本人' を上回った組 | τ の人数 | 形 |",
          "|---|---|---|---|---|---|---|---|"]
    for k, C in S["A"]["cells"].items():
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k, AB.st(C["Rs"]), AB.st(C["D"]), AB.st(C["E"]), AB.st(C["Dp"]),
            "—" if C["pair_swap_beats_self_share"] is None else "%.2f" % C["pair_swap_beats_self_share"],
            " ".join("%s:%d" % kv for kv in C["tau_counts"].items()), S["A"]["k_forms"][k]))
    L += ["", "パネルの形: %s（副 Dp: %s）・入れ替えの −∞: %s" % (
        S["A"]["panel_form"], S["A"]["panel_form_dp"], " ".join("k=%s:%d" % (k, C["swap_neg_inf"]) for k, C in S["A"]["cells"].items()))]
    open(path, "w", newline="\n").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- 本計算
def check(ck, out, key, pairs, msg, same=same2):
    ok = all(same(x, y) for x, y in pairs)
    ck[key] = dict(passed=bool(ok), compared=len(pairs),
                   max_abs_diff=float(max((abs(x[0] - y[0]) for x, y in pairs
                                           if np.isfinite(x[0]) and np.isfinite(y[0])), default=0.0)))
    AB.write_json(ck, os.path.join(out, "r7_check.json"))
    if not ok:
        sys.exit("%s が外れた（%s）。止めて報告する" % (key, msg))
    print("%s 通過" % key, flush=True)


def main():
    argv = sys.argv[1:]
    run_id = None
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    coa, raw, bvals, svals, rout, out, jobs = argv[0], argv[1], argv[2], argv[3], argv[4], argv[5], int(argv[6])
    pkl = raw + "." + DS + ".pkl"
    if not all(AB.outside_repo(p) for p in (pkl, bvals, svals, rout)):
        sys.exit("書き手ごとの値が repo の中を指している")
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
    rc = json.load(open(os.path.join(out, "repro_check.json")))
    if sha(pkl) != CP.PKL_SHA[DS] or sha(bvals) != rc["bvals_sha256"] or sha(svals) != SYM_VALS_SHA:
        sys.exit("pickle・B の値・対称版の値のどれかが本計算のものと違う")
    with open(pkl, "rb") as fp:
        R = pickle.load(fp)  # 人は開かない
    with open(svals, "rb") as fp:
        SV = pickle.load(fp)  # 人は開かない
    cfg = ml.DATASETS[DS]
    members = ml.panel_members(R, cfg, {w: R[w]["n"] for w in R})
    ws = next(iter(members["P15"].values()))
    if any(v != ws for v in members["P15"].values()) or len(ws) != 17:
        sys.exit("P15 の書き手が k で違うか 17 人でない")
    writers, _ = ml.load(DS, coa, SEED)
    if any(len(writers[w]) != R[w]["n"] for w in R):
        sys.exit("中間のデータの単位の数が pickle と違う")
    del writers
    elig = sorted(R)
    S03, P03 = SV[ALPHA]["self"], SV[ALPHA]["pool"]
    ck = dict(run_id=run_id, pkl_sha256=sha(pkl), bvals_sha256=sha(bvals), sym_values_sha256=sha(svals))
    T = dict(run_id=run_id)
    t0 = time.time()
    mode_em = json.load(open(pinned4.MODE_SUMMARY))["datasets"][DS]["em"]["P15"]
    sym_saved = json.load(open(os.path.join(out, "sym_summary.json")))["cells"]
    rng = np.random.default_rng([SEED + 4, 7])
    V = {}
    S = dict(run_id=run_id, writers=len(ws), ks=KS, B={}, A={})
    with ProcessPoolExecutor(jobs, initializer=ml._init, initargs=({DS: coa}, SEED, [])) as ex:
        # ---- B-fix: 倍率 1 の共通 4 構造 → 本人の引き直し
        full1 = dict(zip(ml.STRUCTS, ex.map(job_full, [dict(ds=DS, s=s, alpha=1.0, seed=SEED) for s in ml.STRUCTS])))
        jl = [dict(ds=DS, excl=[w], start=full1[s], alpha=1.0, score=True) for w in ws for s in ml.STRUCTS]
        it = iter(ex.map(job_excl, jl, chunksize=1))
        pools1 = {w: {ml.sname(s): next(it) for s in ml.STRUCTS} for w in ws}
        P1 = {w: {n: pools1[w][n]["ll"] for n in pools1[w]} for w in ws}
        T["pool_1_sec"] = time.time() - t0
        check(ck, out, "p_repro_pool1", [(P1[w][n], R[w]["em"]["pool"][n]) for w in ws for n in P1[w]],
              "倍率 1 の w を除く共通が mode の pickle と違う")
        jr = [dict(ds=DS, w=w, wseq=elig.index(w), seed=SEED, alpha=1.0, ks_fit=KS, structs=list(ml.STRUCTS),
                   pools={n: (pools1[w][n]["m"], pools1[w][n]["sb"]) for n in pools1[w]}) for w in ws]
        FX = dict(zip(ws, ex.map(job_replay, jr, chunksize=1)))
        del pools1
        T["replay_1_sec"] = time.time() - t0
        cmp = [(FX[w]["self"][ml.sname(s)][str(k)][t], R[w]["em"]["k"][str(k)]["self"][ml.sname(s)][t])
               for w in ws for s in ml.STRUCTS for k in KS for t in map(str, ml.TAUS_FIT)]
        cmp += [(FX[w]["r1"][str(k)], R[w]["em"]["k"][str(k)]["r1"]) for w in ws for k in KS]
        check(ck, out, "p_repro_fix", cmp, "引き直した本人か r1 が mode の pickle と違う")
        cells = {str(k): b_fix_cell(ws, k, R, FX, P1, rng) for k in KS}
        cur = [(cells[str(k)]["R"]["median"], mode_em[str(k)]["two_stage"]["other"]["two_stage_other"]
                ["all/self_minus_pool_same"]["median"]) for k in KS]
        check(ck, out, "p_repro_current", [([a], [b]) for a, b in cur], "B-fix の全記号の残りが mode の summary と違う",
              same=lambda x, y: np.float64(x[0]).tobytes() == np.float64(y[0]).tobytes())
        S["B"]["fix"] = dict(cells=cells)
        # ---- B-sym: 倍率 0.03 の共通 ar3 → 本人' の引き直し
        t1 = time.time()
        full03 = ex.submit(job_full, dict(ds=DS, s=AR3, alpha=float(ALPHA), seed=SEED)).result()
        T["full_03_sec"] = time.time() - t1
        t2 = time.time()
        p03 = dict(zip(ws, ex.map(job_excl, [dict(ds=DS, excl=[w], start=full03, alpha=float(ALPHA), score=True) for w in ws],
                                  chunksize=1)))
        T["excl_03_sec"] = time.time() - t2
        PS = {w: p03[w]["ll"] for w in ws}
        check(ck, out, "p_repro_pool03", [(PS[w], P03[w]) for w in ws], "倍率 0.03 の w を除く共通が対称版の値と違う")
        jr = [dict(ds=DS, w=w, wseq=elig.index(w), seed=SEED, alpha=float(ALPHA), ks_fit=KS, structs=[AR3],
                   pools={"ar3": (p03[w]["m"], p03[w]["sb"])}) for w in ws]
        SY = dict(zip(ws, ex.map(job_replay, jr, chunksize=1)))
        del p03
        T["replay_03_sec"] = time.time() - t0
        cmp = [(SY[w]["self"]["ar3"][str(k)][t], S03[w][str(k)][t]) for w in ws for k in KS for t in map(str, ml.TAUS_FIT)]
        check(ck, out, "p_repro_sym", cmp, "引き直した本人' が対称版の値と違う")
        cells = {str(k): b_sym_cell(ws, k, R, S03, P03, SY, PS, rng) for k in KS}
        rs = [([cells[str(k)]["R"]["median"]], [sym_saved[str(k)]["joint"]["self_minus_pool03"]["median"]]) for k in KS]
        check(ck, out, "p_repro_rs", rs, "B-sym の全記号の残りが sym_summary と違う", same=lambda x, y: abs(x[0] - y[0]) <= 1e-15)
        S["B"]["sym"] = dict(cells=cells)
        for ver in ("fix", "sym"):
            C = S["B"][ver]["cells"]
            f = {k: b_form(C[k]["F"]["median"], C[k]["R"]["median"]) for k in C}
            S["B"][ver].update(k_forms=f, panel_form=panel_form(f))
        # ---- A: 時間の見積もり → 組の共通 272 個 → 入れ替えと本人''
        rounds = math.ceil(len(ws) * (len(ws) - 1) / jobs)
        per_round = T["excl_03_sec"] / math.ceil(len(ws) / jobs)
        T["pair_pool_estimate_sec"] = rounds * per_round
        if (time.time() - t0 + T["pair_pool_estimate_sec"]) / 3600 > BUDGET_HOURS:
            AB.write_json(T, os.path.join(out, "r7_timing.json"))
            sys.exit("見積もりが 4 時間を超える（組の共通の前）。止めて報告する")
        pairs = [(w, v) for w in ws for v in ws if v != w]
        t3 = time.time()
        pp = dict(zip(pairs, ex.map(job_excl, [dict(ds=DS, excl=[w, v], start=full03, alpha=float(ALPHA)) for w, v in pairs],
                                    chunksize=1)))
        T["pair_pool_sec"] = time.time() - t3
        picks = {str(k): SM.sym_picks(ws, k, R, S03, P03)[0] for k in KS}
        jp = [pair_job(w, v, elig.index(w), elig.index(v), picks, pp[(w, v)], KS) for w, v in pairs]
        del pp
        PAIR = dict(zip(pairs, ex.map(job_pair, jp, chunksize=1)))
        T["pair_fit_sec"] = time.time() - t0
    V = dict(fix=FX, pool1=P1, sym=SY, pool03=PS, pair=PAIR)
    with open(rout, "wb") as fp:
        pickle.dump(V, fp)
    ck["r7_values_sha256"] = sha(rout)
    AB.write_json(ck, os.path.join(out, "r7_check.json"))
    AB.write_json(T, os.path.join(out, "r7_timing.json"))
    acells = {}
    for k in KS:
        pk = picks[str(k)]
        selfp = {w: P03[w][0] if pk[w] == INF else S03[w][str(k)][pk[w]][0] for w in ws}
        acells[str(k)] = a_cell(ws, k, pk, selfp, {w: P03[w][0] for w in ws}, PAIR, rng)
    fa = {k: a_form(C["D"]["median"], C["Rs"]["median"]) for k, C in acells.items()}
    fd = {k: a_form(C["Dp"]["median"], C["Rs"]["median"]) for k, C in acells.items()}
    S["A"] = dict(cells=acells, k_forms=fa, panel_form=panel_form(fa), k_forms_dp=fd, panel_form_dp=panel_form(fd))
    AB.write_json(S, os.path.join(out, "r7_summary.json"))
    write_tables(S, os.path.join(out, "r7_tables.md"))


if __name__ == "__main__":
    main()
