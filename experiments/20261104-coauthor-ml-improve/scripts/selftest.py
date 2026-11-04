"""陽性対照（合成のデータだけ・design §6.1・conditions.md の V）。ml.py --selftest から呼ぶ。

返り値: 0 = すべて通った・3 = 通らない対照がある（変異の門は 3 を「赤」と読む）。例外は Python の既定（1）。
判定の数は合成の正しさの門で、実データの判定の閾値ではない。
"""
import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import data as DT
import hmm2 as H
import logit as LG
import ml

NAMES = ["P-XI", "P-BATCH", "P-EM3", "P-AR1", "P-PRIOR", "P-CH", "P-POOL", "P-AR", "P-LEAK", "P-EM2",
         "P-LAM", "P-LINF", "P-C1", "P-SIMP", "P-S", "P-OTH", "P-PROBE"]
STICKY = 0.9


# ---------------------------------------------------------------- 合成の部品
def common_model(rng):
    m = H.random_model("hmm", 3, rng)
    m["A"] = STICKY * np.eye(3) + (1 - STICKY) * m["A"]
    return m


def perturb(m, rng):
    q = dict(m)
    A = np.clip(m["A"] + np.diag(rng.uniform(-0.05, 0.05, 3)), 1e-6, None)
    q["A"] = A / A.sum(1, keepdims=True)
    q["B"] = np.stack([rng.dirichlet(200 * r + 1e-3) for r in m["B"]])
    return q


def ar_model(rng, K=2):
    """AR(1)-HMM の合成: 状態ごとに別の 1 次のマルコフ（行は Dirichlet(0.3)・粘る状態）。"""
    A = 0.95 * np.eye(K) + 0.05 * rng.dirichlet(np.ones(K), K)
    return dict(kind="ar", pi=np.ones(K) / K, A=A / A.sum(1, keepdims=True), H=rng.dirichlet(np.ones(H.NSYM), K),
                C=np.stack([rng.dirichlet(np.full(H.NSYM, 0.3), H.NSYM) for _ in range(K)]))


def unit_of(seq):
    return dict(start=0, seqs=[seq], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


def honest_ll(m, seqs):
    """変異の切り替えに触れない独立の前向き（1 系列ずつ・P-LEAK の「真」）。返り値: (対数尤度の和, 記号の数)。"""
    tot, n = 0.0, 0
    for s in seqs:
        s = np.asarray(s)
        a = None
        for t, o in enumerate(s):
            if m["kind"] == "hmm":
                e = m["B"][:, o]
            else:
                e = m["H"][:, o] if t == 0 else m["C"][:, s[t - 1], o]
            pred = m["pi"] if t == 0 else a @ m["A"]
            v = pred * e
            c = v.sum()
            tot += np.log(c)
            a = v / c
        n += len(s)
    return tot, n


def em_job(args):
    """P-POOL・P-LEAK の 1 書き手（ワーカー）。"""
    mut, units, Hh, ks, pools, seed, w, structs = args
    ml.set_mut(mut)
    rng = np.random.default_rng([seed + 10, w])
    return ml.em_writer(units, Hh, ks, pools, rng, structs=structs, do_folds=False)


def ch_job(args):
    """P-CH の 1 回: 切った当てはめと切らない当てはめの A・B の最大の絶対差。"""
    mut, seed, r = args
    ml.set_mut(mut)
    rng = np.random.default_rng([seed, 77, r])
    cm = common_model(rng)
    seqs = H.sample(cm, [20_000] * 5, rng)
    pr = H.base_prior("hmm", 3)
    mc, _, _, _, _ = H.em_from(cm, H.Data(seqs, chunk=H.CHUNK), pr)
    mu, _, _, _, _ = H.em_from(cm, H.Data(seqs), pr)
    return float(max(np.abs(mc["A"] - mu["A"]).max(), np.abs(mc["B"] - mu["B"]).max()))


# ---------------------------------------------------------------- 対照
def p_xi(seed):
    rng = np.random.default_rng([seed, 1])
    worst = 0.0
    for kind, K in [("hmm", 3), ("hmm", 10), ("ar", 3)]:
        seqs = H.sample(common_model(rng), [700, 1200, 300, 2500] * 3, rng)
        D = H.Data(seqs, chunk=H.CHUNK)
        _, h, T = H.r0_r1(seqs)
        m = H.random_model(kind, K, rng, r1=T, r0=h)
        al, c, E = H.forward(m, D)
        be = H.backward(m, D, E, c)
        a, b = H.xi_counts_loop(m["A"], al, be, E, c, D.M), H.xi_counts(m["A"], al, be, E, c, D.M)
        worst = max(worst, float(np.abs(a - b).max() / np.abs(a).max()))
    return dict(passed=worst < 1e-9, worst_rel=worst)


def p_batch(seed):
    rng = np.random.default_rng([seed, 2])
    worst = 0.0
    for kind, K in [("hmm", 6), ("ar", 2)]:
        seqs = H.sample(common_model(rng), [900] * 40 + [2000] * 5, rng)
        _, h, T = H.r0_r1(seqs)
        m = H.random_model(kind, K, rng, r1=T, r0=h)
        S1, l1 = H.counts(m, H.Data(seqs, chunk=H.CHUNK))
        S2, l2 = H.counts(m, H.Batched(seqs, chunk=H.CHUNK, size=7))
        for k in S1:
            worst = max(worst, float(np.abs(S1[k] - S2[k]).max() / max(np.abs(S1[k]).max(), 1e-300)))
        worst = max(worst, abs(l1 - l2) / abs(l1))
        pr = H.base_prior(kind, K)
        o1 = H.objective(m, H.Data(seqs, chunk=H.CHUNK), pr)
        o2 = H.objective(m, H.Batched(seqs, chunk=H.CHUNK, size=7), pr)
        worst = max(worst, abs(o1 - o2) / abs(o1))
    return dict(passed=worst < 1e-9, worst_rel=worst)


def p_em3(seed):
    rng = np.random.default_rng([seed, 3])
    seqs = H.sample(common_model(rng), [700, 1500, 300], rng)
    _, h, T = H.r0_r1(seqs)
    sum_dev, at_dev = 0.0, 0.0
    for kind, K in [("hmm", 3), ("ar", 2)]:
        m = H.random_model(kind, K, rng, r1=T, r0=h)
        for D in (H.Data(seqs, chunk=H.CHUNK), H.Data(seqs)):
            dist, at, c = H.pred_dist(m, D)
            sum_dev = max(sum_dev, float(np.abs(dist.sum(2) - 1)[D.M].max()))
            at_dev = max(at_dev, float(np.abs(np.exp(np.log(c)) - at)[D.M].max()))
    return dict(passed=sum_dev < 1e-9 and at_dev < 1e-12, sum_dev=sum_dev, at_dev=at_dev)


def p_ar1(seed):
    rng = np.random.default_rng([seed, 4])
    worst = 0.0
    for _ in range(3):
        tr = H.sample(ar_model(rng), [1500, 2500, 700], rng)
        te = H.sample(ar_model(rng), [800, 1200], rng)
        _, h, T = H.r0_r1(tr)
        m, _ = H.fit([("rand", H.random_model("ar", 1, rng, r1=T, r0=h))], H.Data(tr, chunk=H.CHUNK), H.base_prior("ar", 1))
        ev = ml.Eval(te, [np.ones(len(s), dtype=bool) for s in te])
        a, b = ev.ll(m)[0], ev.ll_r1(h, T)[0]
        worst = max(worst, abs(a - b))
    return dict(passed=worst < 1e-9, worst=worst)


def p_prior(seed):
    rng = np.random.default_rng([seed, 5])
    cm = common_model(rng)
    pool = H.sample(cm, [900] * 120, rng)
    Dp = H.Batched(pool, chunk=H.CHUNK)
    mp, _ = H.fit([("cm", cm)], Dp, H.base_prior("hmm", 3))
    S, _ = H.counts(mp, Dp)
    sb = H.sbar_of(S, Dp.nobs)
    own = H.sample(perturb(cm, rng), [700] * 3, rng)
    D = H.Data(own, chunk=H.CHUNK)
    m, _ = H.fit([("pool", mp)], D, H.make_prior("hmm", 3, 1e8, sb))
    diff = float(max(np.abs(m["A"] - mp["A"]).max(), np.abs(m["B"] - mp["B"]).max()))
    base_same = all(np.array_equal(H.make_prior("hmm", 3, 0, sb)[k], H.base_prior("hmm", 3)[k]) for k in ("pi", "A", "B"))
    sums = [float(sb["pi"].sum() + sb["A"].sum()), float(sb["B"].sum())]
    ok = diff < 1e-3 and base_same and all(abs(x - 1) < 1e-9 for x in sums)
    return dict(passed=ok, max_abs_diff_AB=diff, tau0_equals_base=base_same, sbar_sums=sums)


def p_ch(seed, mut, ex):
    d = list(ex.map(ch_job, [(mut, seed, r) for r in range(10)]))
    return dict(passed=float(np.median(d)) < 0.02, median=float(np.median(d)), runs=len(d))


def synth_writers(rng, cm, n_w=17, n_u=20, L=650, perturbed=True):
    truths, writers = [], []
    for _ in range(n_w):
        tm = perturb(cm, rng) if perturbed else cm
        truths.append(tm)
        writers.append([unit_of(s) for s in H.sample(tm, [L] * n_u, rng)])
    return truths, writers


def pools_for(writers, Hh, structs, start):
    out = []
    for w in range(len(writers)):
        P = {}
        for s in structs:
            m, sb, d = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=w, start=start[ml.sname(s)]))
            P[ml.sname(s)] = (m, sb)
        out.append(P)
    return out


def p_pool_leak(seed, mut, ex):
    """P-POOL と P-LEAK（P-POOL の合成・K = 3 のふつうの HMM・全 τ）。"""
    rng = np.random.default_rng([seed, 6])
    cm = common_model(rng)
    truths, writers = synth_writers(rng, cm)
    Hh, ks, s = 5, [1, 15], ("hmm", 3)
    pools = pools_for(writers, Hh, [s], {"hmm3": cm})
    res = list(ex.map(em_job, [(mut, w_units, Hh, ks, pools[w], seed, w, [s]) for w, w_units in enumerate(writers)]))
    results = {w: dict(em=r) for w, r in enumerate(res)}
    taus = [str(t) for t in ml.TAUS]
    med = {}
    for k in ks:
        vals = ml.em_values(results, list(results), k, s)
        d = []
        for w in results:
            t_o = ml.select_other(vals, w, taus[::-1])
            rk = results[w]["em"]["k"][str(k)]["self"]["hmm3"]
            d.append(rk[t_o][0] - rk["0"][0])
        med[k] = float(np.median(d))
    pool_ok = med[1] > 0 and med[15] < med[1]
    leak = {}
    for k in ks:
        for t in taus:
            d = []
            for w in results:
                te = [u["seqs"][0] for u in writers[w][-Hh:]]
                tl, tn = honest_ll(truths[w], te)
                d.append(results[w]["em"]["k"][str(k)]["self"]["hmm3"][t][0] - tl / tn)
            leak["k%d_tau%s" % (k, t)] = float(np.median(d))
    decs = sum(dd["decreases"] for r in res for rk in r["k"].values() for v in rk["diag"].values() for dd in v.values())
    return (dict(passed=pool_ok, median_other_minus_tau0=med),
            dict(leak_medians=leak, worst=max(leak.values())), decs)


def pool_full_job(args):
    mut, job = args
    ml.set_mut(mut)
    return ml.fit_pool_full(job)


def pool_excl_job(args):
    mut, job = args
    ml.set_mut(mut)
    return ml.fit_pool_excl(job)


def p_ar_leak(seed, mut, ex):
    """P-AR と P-LEAK（AR の合成・本計算と同じ経路: 全員の共通 10 開始点 → w を除く共通 → 本人）。
    書き手 17 人・各 10 本（650 記号）・評価 5 本・k = 5。構造は AR K = 2 と K = 1（全 τ）。"""
    rng = np.random.default_rng([seed, 7])
    structs = [("ar", 2), ("ar", 1)]
    out, leak, decs = {}, {}, 0
    for ci, case in enumerate(("A", "B")):
        tm = ar_model(rng, 2) if case == "A" else ar_model(rng, 1)
        writers = [[unit_of(s) for s in H.sample(tm, [650] * 10, rng)] for _ in range(17)]
        sis = [ml.STRUCTS.index(s) for s in structs]
        full = list(ex.map(pool_full_job, [(mut, dict(ds="coauthor", writers=writers, si=si, seed=seed + 100 * (ci + 1)))
                                           for si in sis]))
        decs += sum(d["decreases"] for _, d in full)
        jobs = [(mut, dict(ds="coauthor", writers=writers, w=w, start=full[j][0])) for w in range(17) for j in range(len(structs))]
        pres = list(ex.map(pool_excl_job, jobs, chunksize=1))
        pools = [{ml.sname(s): pres[w * len(structs) + j][:2] for j, s in enumerate(structs)} for w in range(17)]
        decs += sum(p[2]["decreases"] for p in pres)
        res = list(ex.map(em_job, [(mut, writers[w], 5, [5], pools[w], seed + 100 * (ci + 1), w, structs) for w in range(17)]))
        d_ar = []
        for w, r in enumerate(res):
            rk = r["k"]["5"]
            d_ar.append(rk["self"]["ar2"]["0"][0] - rk["r1"][0])
            tl, tn = honest_ll(tm, [u["seqs"][0] for u in writers[w][-5:]])
            for s in structs:
                for t in ml.TAUS:
                    leak.setdefault("%s_%s_tau%d" % (case, ml.sname(s), t), []).append(rk["self"][ml.sname(s)][str(t)][0] - tl / tn)
            decs += sum(dd["decreases"] for v in rk["diag"].values() for dd in v.values())
        out[case] = float(np.median(d_ar))
    ok = out["A"] > 0 and out["B"] <= 0.002
    return dict(passed=ok, median_ar2_minus_r1=out), {k: float(np.median(v)) for k, v in leak.items()}, decs


def lam_writers(rng, differ, n_w=17, n_u=20, per=3):
    beta_bar = np.array([0.8, -0.5, 0.3, 0.0, 0.4])
    writers = []
    for _ in range(n_w):
        b = beta_bar + (rng.normal(0, 1.0, 5) if differ else 0)
        a = rng.normal(-1.0, 0.5)
        units = []
        for _ in range(n_u):
            X = rng.normal(0, 1, (per, 5))
            y = (rng.uniform(size=per) < LG.sigmoid(a + X @ b)).astype(int)
            ps = [dict(tab=X[i].tolist(), recal=[float(X[i, 0])], y=int(y[i])) for i in range(per)]
            units.append(dict(start=0, seqs=[], pflag=[], probes=ps, probes_all=ps))
        writers.append(units)
    return writers


def p_lam_linf(seed):
    """門は 1 単位 30 問の合成（判断 10）。1 単位 3 問の版は門にせず、選ばれる λ の中央値を結果として出す。"""
    rng = np.random.default_rng([seed, 8])
    med3 = {}
    for case, differ in (("A", True), ("B", False)):
        writers = lam_writers(rng, differ, per=3)
        lams = [str(x) for x in LG.LAMS]
        ch = []
        for w in range(len(writers)):
            P = ml.pool_logistic(writers, 5, w, "tab", "main")
            r = ml.logistic_writer(writers[w], 5, [15], P, "tab", "main")
            c = ml.select_cv(r["k"]["15"]["fold"], lams[::-1], maximize=False)
            ch.append(float(c) if c is not None else np.nan)
        med3[case] = dict(median=float(np.nanmedian(ch)), counts={str(v): int(sum(1 for x in ch if x == v)) for v in sorted(set(ch))})
    med, linf = {}, dict(slope_dev=0.0, inf_vs_1e10=0.0, zero_vs_unpen=0.0)
    for case, differ in (("A", True), ("B", False)):
        writers = lam_writers(rng, differ, per=30)
        lams = [str(x) for x in LG.LAMS]
        chosen = []
        for w in range(len(writers)):
            P = ml.pool_logistic(writers, 5, w, "tab", "main")
            r = ml.logistic_writer(writers[w], 5, [15], P, "tab", "main")
            c = ml.select_cv(r["k"]["15"]["fold"], lams[::-1], maximize=False)
            chosen.append(float(c) if c is not None else np.nan)
            if case == "A":
                linf["slope_dev"] = max(linf["slope_dev"], float(np.abs(np.array(r["k"]["15"]["raw_slope_inf"])
                                                                        - P["beta_c"] / P["std"].sd).max()))
                tr, _ = DT.split(len(writers[w]), 15, 5)
                X, y = ml.xy(ml.probes_of([writers[w][i] for i in tr], "main"), "tab")
                Z = P["std"](X)
                b1, be1, _ = LG.fit_self(Z, y, P["beta_c"], 1e10)
                b2, be2, _ = LG.fit_self(Z, y, P["beta_c"], float("inf"))
                linf["inf_vs_1e10"] = max(linf["inf_vs_1e10"], float(np.abs(LG.predict(b1, be1, Z) - LG.predict(b2, be2, Z)).max()))
                b3, be3, _ = LG.fit_self(Z, y, P["beta_c"], 1e-8)
                th, _ = LG.fit_logistic(Z, y, lam=0.0, pseudo=True)
                linf["zero_vs_unpen"] = max(linf["zero_vs_unpen"], float(np.abs(be3 - th[1:]).max()))
        med[case] = float(np.nanmedian(chosen))
    lam_ok = med["A"] <= 1 and med["B"] >= 10
    linf_ok = linf["slope_dev"] < 1e-6 and linf["inf_vs_1e10"] < 1e-6 and linf["zero_vs_unpen"] < 1e-4
    return (dict(passed=lam_ok, median_chosen_lambda_30_per_unit=med, not_gate_3_per_unit=med3),
            dict(passed=linf_ok, **linf))


def p_c1(seed):
    rng = np.random.default_rng([seed, 9])
    ys, ps = [], []
    for _ in range(8):
        n = int(rng.integers(5, 30))
        y = (rng.uniform(size=n) < 0.3).astype(int)
        ys.append(y)
        ps.append(np.full(n, rng.uniform()))
    C, _ = LG.within_c(ys, ps)
    dev = 0.0
    for _ in range(20):
        y = (rng.uniform(size=25) < 0.4).astype(int)
        p = np.round(rng.uniform(size=25), 1)
        a, b = LG.conc_counts(y, p), LG.conc_counts_brute(y, p)
        dev = max(dev, abs(a[0] - b[0]), abs(a[1] - b[1]))
    return dict(passed=C is not None and abs(C - 0.5) < 1e-12 and dev < 1e-12, C_constant=C, brute_dev=dev)


def p_simp(seed):
    rng = np.random.default_rng([seed, 10])
    Xs, ys, ps = [], [], []
    for mu in np.linspace(-2, 2, 10):
        x = rng.normal(mu, 1, 200)
        y = (rng.uniform(size=200) < LG.sigmoid(-2.5 * mu + 1.0 * x)).astype(int)
        Xs.append(x[:, None])
        ys.append(y)
        ps.append(x)
    C, _ = LG.within_c(ys, ps)
    pa = LG.pooled_auc(ys, ps)
    single, _ = LG.fit_logistic(np.vstack(Xs), np.concatenate(ys), lam=1.0, pseudo=True)
    fe, _ = LG.fit_fe(Xs, ys)
    ok = pa < 0.5 and C > 0.5 and single[1] < 0 and fe[0] > 0
    return dict(passed=bool(ok), pooled_auc=pa, C=C, single_coef=float(single[1]), fe_coef=float(fe[0]))


def p_s():
    ok = True
    for Hh, grid in ((5, ml.DATASETS["coauthor"]["grid"]), (1, ml.DATASETS["cs1"]["grid"])):
        for n in range(Hh + 1, 60):
            for k in grid:
                if k <= n - Hh:
                    ok = ok and DT.check_split(n, k, Hh)
        writers = [[dict(tag=(w, i)) for i in range(n)] for w, n in enumerate([3, 8, 12, Hh, Hh + 1, 30])]
        for w in range(len(writers)):
            pu = ml.pool_units(writers, Hh, exclude=w)
            tags = {u["tag"] for u in pu}
            ok = ok and all(t[0] != w for t in tags)
            for v, ss in enumerate(writers):
                if len(ss) >= Hh + 1:
                    ok = ok and not any((v, i) in tags for i in range(len(ss) - Hh, len(ss)))
    return dict(passed=bool(ok))


def p_oth(seed):
    rng = np.random.default_rng([seed, 11])
    ok = True
    vals = {0: {"a": 1.0, "b": 0.0}, 1: {"a": 0.0, "b": 1.0}, 2: {"a": 0.3, "b": 0.3}}
    base = ml.select_other(vals, 2, ["a", "b"])
    vals2 = {**vals, 2: {"a": -10.0, "b": 10.0}}
    ok = ok and ml.select_other(vals2, 2, ["a", "b"]) == base
    for _ in range(200):
        n = int(rng.integers(3, 8))
        v = {i: {c: float(rng.normal()) for c in "abcd"} for i in range(n)}
        w = int(rng.integers(0, n))
        b = ml.select_other(v, w, list("abcd"))
        v[w] = {c: float(rng.normal() * 100) for c in "abcd"}
        ok = ok and ml.select_other(v, w, list("abcd")) == b
    return dict(passed=bool(ok))


def p_probe(seed):
    rng = np.random.default_rng([seed, 12])
    ok, n = True, 0
    for _ in range(30):
        a = 0
        b = int(rng.integers(20, 90)) * 60_000
        bursts = np.sort(rng.uniform(a, b, int(rng.integers(3, 15))))
        keys = np.sort(np.concatenate([t + np.cumsum(rng.exponential(300, int(rng.integers(5, 60)))) for t in bursts])).astype(np.int64)
        keys = keys[keys <= b]
        ts = DT.cs1_probe_times(np.random.default_rng([seed, n]), keys, a, b, True)
        n += 1
        for i, t in enumerate(ts):
            ok = ok and a + DT.WIN_START <= t <= b - DT.LABEL_MS
            ok = ok and bool(((keys >= t - DT.WIN_START) & (keys < t - DT.WIN_END)).any())
            if i:
                ok = ok and t - ts[i - 1] >= DT.GAP_MS
    return dict(passed=bool(ok), blocks=n)


# ---------------------------------------------------------------- 入口
def main(seed, out, only, mut, run_id):
    t0 = time.time()
    want = set(only) if only else set(NAMES)
    R = dict(run_id=run_id, mutate=mut)
    simple = {"P-XI": p_xi, "P-BATCH": p_batch, "P-EM3": p_em3, "P-AR1": p_ar1, "P-PRIOR": p_prior,
              "P-C1": p_c1, "P-SIMP": p_simp, "P-OTH": p_oth, "P-PROBE": p_probe}
    for nm, f in simple.items():
        if nm in want:
            R[nm] = f(seed)
    if "P-S" in want:
        R["P-S"] = p_s()
    decs = 0
    need_ex = want & {"P-CH", "P-POOL", "P-AR", "P-LEAK", "P-EM2"}
    if need_ex:
        with ProcessPoolExecutor(6) as ex:
            if "P-CH" in want:
                R["P-CH"] = p_ch(seed, mut, ex)
            if want & {"P-POOL", "P-LEAK", "P-EM2"}:
                pool, leak_pool, d1 = p_pool_leak(seed, mut, ex)
                decs += d1
                if "P-POOL" in want:
                    R["P-POOL"] = pool
            if want & {"P-AR", "P-LEAK", "P-EM2"}:
                ar, leak_ar, d2 = p_ar_leak(seed, mut, ex)
                decs += d2
                if "P-AR" in want:
                    R["P-AR"] = ar

    if "P-LEAK" in want:
        allv = dict(leak_pool["leak_medians"], **leak_ar)
        R["P-LEAK"] = dict(passed=max(allv.values()) <= 0.002, medians=allv)
    if "P-EM2" in want:
        R["P-EM2"] = dict(passed=decs == 0, decreases=int(decs))
    if want & {"P-LAM", "P-LINF"}:
        lam, linf = p_lam_linf(seed)
        if "P-LAM" in want:
            R["P-LAM"] = lam
        if "P-LINF" in want:
            R["P-LINF"] = linf
    R["seconds"] = time.time() - t0
    R["all_passed"] = all(R[n]["passed"] for n in NAMES if n in R)
    json.dump(R, open(out, "w"), indent=1, default=float)
    print(json.dumps({n: R[n]["passed"] for n in NAMES if n in R}))
    return 0 if R["all_passed"] else 3
