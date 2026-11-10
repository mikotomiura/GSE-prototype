"""陽性対照（合成のデータだけ・conditions.md の V2）。ml.py --selftest から呼ぶ。

返り値: 0 = すべて通った・3 = 通らない対照がある（変異の門は 3 を「赤」と読む）。例外は Python の既定（1）。
判定の数は合成の正しさの門で、実データの判定の閾値ではない。
前回（experiments/20261104-coauthor-ml-improve/scripts/selftest.py）から、ロジスティックの対照
（P-LAM・P-LINF・P-C1・P-SIMP・P-PROBE・P-EMPTY）を外し、P-INF・P-TAU・P-JOINT・P-PR1・P-SUBSET を足した。
"""
import json
import os
import pickle
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import data as DT
import hmm2 as H
import ml

NAMES = ["P-XI", "P-BATCH", "P-EM3", "P-AR1", "P-PRIOR", "P-CH", "P-POOL", "P-AR", "P-LEAK", "P-EM2", "P-S", "P-OTH",
         "P-INF", "P-TAU", "P-JOINT", "P-PR1", "P-SUBSET"]
STICKY = 0.9
HERE = os.path.dirname(os.path.abspath(__file__))


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
    """1 書き手の EM（ワーカー）。structs = None は本計算と同じ並べ（外した構造の乱数を引いて捨てる）。"""
    mut, units, Hh, ks, pools, seed, w, structs, do_folds, full, keep = args
    ml.set_mut(mut)
    rng = np.random.default_rng([seed + 10, w])
    return ml.em_writer(units, Hh, ks, pools, rng, structs=structs, do_folds=do_folds, full=full, keep_fits=keep)


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


def decs_of(r):
    return sum(dd["decreases"] for rk in r["k"].values() for v in rk["diag"].values() for dd in v.values())


# ---------------------------------------------------------------- 引き継ぐ対照（範囲は今回の構造と τ）
def p_xi(seed):
    rng = np.random.default_rng([seed, 1])
    worst = 0.0
    for kind, K in [("hmm", 3), ("ar", 1), ("ar", 3)]:
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
    for kind, K in [("hmm", 3), ("ar", 2)]:
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
    """w を除く共通。返り値: (書き手ごとの {構造名: (母数, S̄)}, 目的が減った回の和)。"""
    out, decs = [], 0
    for w in range(len(writers)):
        P = {}
        for s in structs:
            m, sb, d = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=w, start=start[ml.sname(s)]))
            P[ml.sname(s)] = (m, sb)
            decs += d["decreases"]
        out.append(P)
    return out, decs


def p_pool_leak(seed, mut, ex):
    """P-POOL・P-LEAK・P-INF・P-PR1（P-POOL の合成・K = 3 のふつうの HMM・全 τ（∞ を含む））。"""
    rng = np.random.default_rng([seed, 6])
    cm = common_model(rng)
    truths, writers = synth_writers(rng, cm)
    Hh, ks, s = 5, [1, 15], ("hmm", 3)
    pools, pdecs = pools_for(writers, Hh, [s], {"hmm3": cm})
    res = list(ex.map(em_job, [(mut, w_units, Hh, ks, pools[w], seed, w, [s], False, None, False)
                               for w, w_units in enumerate(writers)]))
    results = {w: dict(em=r) for w, r in enumerate(res)}
    taus = sorted(ml.TAU_KEYS, key=ml.tau_val, reverse=True)
    med = {}
    for k in ks:
        vals = ml.em_values(results, list(results), k, s)
        d = []
        for w in results:
            t_o = ml.select_other(vals, w, taus)
            rk = results[w]["em"]["k"][str(k)]["self"]["hmm3"]
            d.append(rk[t_o][0] - rk["0"][0])
        med[k] = float(np.median(d))
    pool_ok = med[1] > 0 and med[15] < med[1]
    leak = {}
    for k in ks:
        for t in ml.TAU_KEYS:
            d = []
            for w in results:
                te = [u["seqs"][0] for u in writers[w][-Hh:]]
                tl, tn = honest_ll(truths[w], te)
                d.append(results[w]["em"]["k"][str(k)]["self"]["hmm3"][t][0] - tl / tn)
            leak["k%d_tau%s" % (k, t)] = float(np.median(d))
    decs = pdecs + sum(decs_of(r) for r in res)
    # P-PR1: 「共通 − r1」は書き手ごとの差（中央値どうしの差ではない）
    pr1_dev, pr1_med_dev = 0.0, 0.0
    for k in ks:
        ws = list(results)
        for j in (0, 1):
            got = ml.pool_r1_values(results, ws, k, "hmm3", j)
            want = [results[w]["em"]["pool"]["hmm3"][j] - results[w]["em"]["k"][str(k)]["r1"][j] for w in ws]
            pr1_dev = max(pr1_dev, float(np.max(np.abs(np.array(got) - np.array(want)))))
            st = ml.delta_stats(got, np.random.default_rng(0))
            wq = float(np.quantile(np.array(want), 0.5, method="inverted_cdf"))
            pr1_med_dev = max(pr1_med_dev, abs(st["median"] - wq))
    pr1 = dict(passed=bool(pr1_dev < 1e-12 and pr1_med_dev < 1e-12), max_abs_dev=pr1_dev, median_dev=pr1_med_dev)
    # P-INF: τ = ∞ は w を除く共通（全員の共通ではない）。折り目つきで 4 人・k = 3
    full_m, _, dfull = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=None, start=cm))
    decs += dfull["decreases"]
    wi = list(range(4))
    rinf = list(ex.map(em_job, [(mut, writers[w], Hh, [3], pools[w], seed, w, [s], True, {"hmm3": full_m}, False)
                                for w in wi]))
    decs += sum(decs_of(r) for r in rinf)
    eq_eval, fold_dev, full_diff = True, 0.0, []
    for w, r in zip(wi, rinf):
        rk = r["k"]["3"]
        eq_eval = eq_eval and rk["self"]["hmm3"][ml.INF] == r["pool"]["hmm3"]
        pm = pools[w]["hmm3"][0]
        train, test = DT.split(len(writers[w]), 3, Hh)
        a_sum, a_n = 0.0, 0
        for _, ev_i in DT.folds(train, mut=set()):
            e = ml.Eval([writers[w][i]["seqs"][0] for i in ev_i], [writers[w][i]["pflag"][0] for i in ev_i])
            a, b = e.sum_ll(pm)
            a_sum += a
            a_n += b
        got = rk["fold"]["hmm3"][ml.INF]
        fold_dev = max(fold_dev, abs(got[0] - a_sum) / max(1.0, abs(a_sum)) + abs(got[1] - a_n))
        ev = ml.Eval([writers[w][i]["seqs"][0] for i in test], [writers[w][i]["pflag"][0] for i in test])
        full_diff.append(abs(ev.ll(full_m)[0] - ev.ll(pm)[0]))
    inf_ok = bool(eq_eval and fold_dev < 1e-12 and min(full_diff) > 0)
    pinf = dict(passed=inf_ok, eval_equal_to_excl_pool=bool(eq_eval), fold_rel_dev=fold_dev, min_abs_full_minus_excl=min(full_diff))
    return (dict(passed=pool_ok, median_other_minus_tau0=med),
            dict(leak_medians=leak, worst=max(leak.values())), decs, pr1, pinf)


def pool_full_job(args):
    mut, job = args
    ml.set_mut(mut)
    return ml.fit_pool_full(job)


def pool_excl_job(args):
    mut, job = args
    ml.set_mut(mut)
    return ml.fit_pool_excl(job)


def p_ar_leak(seed, mut, ex):
    """P-AR・P-LEAK・P-TAU（P-TAU は判断 6 で、単調さを事前分布の最頻値 normalize(S̄) との距離で見る）（AR の合成・本計算と同じ経路: 全員の共通 10 開始点 → w を除く共通 → 本人）。
    書き手 17 人・各 10 本（650 記号）・評価 5 本・k = 5。構造は AR K = 2 と K = 1（全 τ・∞ を含む）。"""
    rng = np.random.default_rng([seed, 7])
    structs = [("ar", 2), ("ar", 1)]
    out, leak, decs, tau_med, mode_med, pm_mode = {}, {}, 0, None, None, None
    for ci, case in enumerate(("A", "B")):
        tm = ar_model(rng, 2) if case == "A" else ar_model(rng, 1)
        writers = [[unit_of(s) for s in H.sample(tm, [650] * 10, rng)] for _ in range(17)]
        sis = [ml.SEQ_NO[s] for s in structs]
        full = list(ex.map(pool_full_job, [(mut, dict(ds="coauthor", writers=writers, si=si, seed=seed + 100 * (ci + 1)))
                                           for si in sis]))
        decs += sum(d["decreases"] for _, d in full)
        jobs = [(mut, dict(ds="coauthor", writers=writers, w=w, start=full[j][0])) for w in range(17) for j in range(len(structs))]
        pres = list(ex.map(pool_excl_job, jobs, chunksize=1))
        pools = [{ml.sname(s): pres[w * len(structs) + j][:2] for j, s in enumerate(structs)} for w in range(17)]
        decs += sum(p[2]["decreases"] for p in pres)
        res = list(ex.map(em_job, [(mut, writers[w], 5, [5], pools[w], seed + 100 * (ci + 1), w, structs, True, None, case == "A")
                                   for w in range(17)]))
        d_ar = []
        for w, r in enumerate(res):
            rk = r["k"]["5"]
            d_ar.append(rk["self"]["ar2"]["0"][0] - rk["r1"][0])
            tl, tn = honest_ll(tm, [u["seqs"][0] for u in writers[w][-5:]])
            for s in structs:
                for t in ml.TAU_KEYS:
                    leak.setdefault("%s_%s_tau%s" % (case, ml.sname(s), t), []).append(rk["self"][ml.sname(s)][t][0] - tl / tn)
            decs += decs_of(r)
        out[case] = float(np.median(d_ar))
        if case == "A":
            # P-TAU: 本人の母数と w を除く共通の母数の A・C の最大の絶対差（書き手の中央値）
            taus = [t for t in ml.TAUS_FIT if t >= 1000]
            tau_med, mode_med = {}, {}
            for t in taus:
                d, dm = [], []
                for w, r in enumerate(res):
                    m, pm = r["fits"]["ar2"]["5"][str(t)], pools[w]["ar2"][0]
                    d.append(float(max(np.abs(m["A"] - pm["A"]).max(), np.abs(m["C"] - pm["C"]).max())))
                    mode = H.normalize("ar", pools[w]["ar2"][1])  # 事前分布の最頻値（τ → ∞ の行き先）
                    dm.append(float(max(np.abs(m["A"] - mode["A"]).max(), np.abs(m["C"] - mode["C"]).max())))
                tau_med[str(t)] = float(np.median(d))
                mode_med[str(t)] = float(np.median(dm))
            pm_mode = [float(max(np.abs(pools[w]["ar2"][0]["A"] - H.normalize("ar", pools[w]["ar2"][1])["A"]).max(),
                                 np.abs(pools[w]["ar2"][0]["C"] - H.normalize("ar", pools[w]["ar2"][1])["C"]).max()))
                       for w in range(17)]
    ok = out["A"] > 0 and out["B"] <= 0.002
    # 判断 6（条件の後の変更）: 単調さは事前分布の最頻値（τ → ∞ の行き先）との距離で見る。共通との距離は 10^6 で 0.02 未満
    tv = [mode_med[str(t)] for t in ml.TAUS_FIT if t >= 1000]
    tau_ok = all(b <= a for a, b in zip(tv, tv[1:])) and tv[-1] < 0.02 and tau_med[str(ml.TAUS_FIT[-1])] < 0.02
    return (dict(passed=ok, median_ar2_minus_r1=out), {k: float(np.median(v)) for k, v in leak.items()}, decs,
            dict(passed=bool(tau_ok), median_max_abs_diff_AC=tau_med, median_max_abs_diff_AC_to_prior_mode=mode_med,
                 median_pool_vs_prior_mode=float(np.median(pm_mode))))


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


# ---------------------------------------------------------------- 足す対照
def separate_select(values, w, snames, taus):
    """比べのための「別々に選ぶ」形: 各 v（w を除く）の τ を、v を除く他の書き手（w を含む）の中央値で構造ごとに選び、
    構造は w を除く v の「本人_v(構造, τ_v) − r1_v」の中央値で選ぶ。v の τ の選びに w の値が混ざる。"""
    vs = [v for v in values if v != w]
    best, bv = None, None
    for s in snames:
        xs = []
        for v in vs:
            others = [u for u in values if u != v]
            tb, tbv = None, None
            for t in taus:
                m = float(np.median([values[u][(s, t)] for u in others]))
                if tbv is None or m > tbv:
                    tb, tbv = t, m
            xs.append(values[v][(s, tb)])
        m = float(np.median(xs))
        if bv is None or m > bv:
            best, bv = (s, None), m
    return best[0]


def brute_joint(values, w, cands):
    """総当たり: w を除く v の中央値の表を作り、最大の最初の候補（cands の並べ = 同点の規則）。"""
    vs = [v for v in values if v != w]
    meds = np.array([np.median([values[v][c] for v in vs]) for c in cands])
    return cands[int(np.argmax(meds))]


def p_joint(seed):
    rng = np.random.default_rng([seed, 15])
    snames, taus = ["a", "b"], ["t2", "t1", "t0"]
    cands = [(s, t) for t in taus for s in snames]
    ok, found = True, None
    # 作った例: 別々に選ぶと違う構造になる例（構造が違えば組も違う）を、決まった乱数の中から 1 つ取る
    for _ in range(2000):
        n = 7
        v = {i: {c: float(rng.normal()) for c in cands} for i in range(n)}
        jw = ml.select_joint(v, 0, cands)
        if separate_select(v, 0, snames, taus) != jw[0]:
            found = v
            break
    made_ok = found is not None
    if made_ok:
        b = ml.select_joint(found, 0, cands)
        ok = ok and b == brute_joint(found, 0, cands)
        f2 = {**found, 0: {c: float(rng.normal() * 100) for c in cands}}
        ok = ok and ml.select_joint(f2, 0, cands) == b
    # 乱数の 200 回: w の値をでたらめに書き換えても選びが変わらない・総当たりと一致
    for _ in range(200):
        n = int(rng.integers(3, 9))
        v = {i: {c: float(rng.normal()) for c in cands} for i in range(n)}
        w = int(rng.integers(0, n))
        b = ml.select_joint(v, w, cands)
        ok = ok and b == brute_joint(v, w, cands)
        v[w] = {c: float(rng.normal() * 100) for c in cands}
        ok = ok and ml.select_joint(v, w, cands) == b
    # 本計算の候補の並べ（大きい τ が先・同じ τ では自由な母数の少ない構造が先）
    jc = ml.joint_cands()
    # 自由な母数: hmm3 = 83 < ar1 = 675 < ar2 < ar3（H.n_free）
    order_ok = ([c[0] for c in jc[:4]] == ["hmm3", "ar1", "ar2", "ar3"] and all(c[1] == ml.INF for c in jc[:4])
                and jc[-1] == ("ar3", "0") and len(jc) == 36)
    return dict(passed=bool(ok and made_ok and order_ok), made_example_found=made_ok, cand_order_ok=bool(order_ok))


def p_subset(seed, mut, ex):
    """P-SUBSET: 合成の書き手 3 人で、前回の 6 構造の em_writer（前回のディレクトリのコードを別のプロセスで）と、
    今回の 4 構造の em_writer（外した構造の乱数を引いて捨てる）の、重なる構造・τ ∈ {0, 100, 1,000, 10,000} の
    評価の尤度と折り目の量が完全に一致する。"""
    rng = np.random.default_rng([seed, 14])
    cm = common_model(rng)
    _, writers = synth_writers(rng, cm, n_w=3, n_u=8, L=500)
    pool = H.sample(cm, [600] * 20, rng)
    _, hp, Tp = H.r0_r1(pool)
    Dp = H.Data(pool, chunk=H.CHUNK)
    pools6 = {}
    for s in ml.PREV_STRUCTS:
        m = H.random_model(s[0], s[1], rng, r1=Tp, r0=hp)
        S, _ = H.counts(m, Dp)
        pools6[ml.sname(s)] = (m, H.sbar_of(S, Dp.nobs))
    pools4 = {ml.sname(s): pools6[ml.sname(s)] for s in ml.STRUCTS}
    Hh, ks = 5, [1, 3]
    new = list(ex.map(em_job, [(mut, writers[w], Hh, ks, pools4, seed, w, None, True, None, False) for w in range(3)]))
    with tempfile.TemporaryDirectory() as td:
        pin, pout = os.path.join(td, "in.pkl"), os.path.join(td, "out.pkl")
        pickle.dump(dict(mut=[m for m in mut if m not in ("m14",)], writers=writers, pools=pools6, seed=seed, H=Hh, ks=ks),
                    open(pin, "wb"))
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(HERE, "subset_old.py"), pin, pout],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return dict(passed=False, note="前回のコードが走らない", stderr=r.stderr[-2000:]), 0
        old = pickle.load(open(pout, "rb"))
    same, cells, diff = True, 0, 0
    for w in range(3):
        for k in ks:
            a, b = new[w]["k"][str(k)], old[w]["k"][str(k)]
            for s in ml.STRUCTS:
                nm = ml.sname(s)
                for t in ml.PREV_TAU_KEYS:
                    cells += 2
                    if a["self"][nm][t] != b["self"][nm][t]:
                        diff += 1
                    fa = a["fold"][nm][t] if a["fold"][nm] is not None else None
                    fb = b["fold"][nm][t] if b["fold"][nm] is not None else None
                    if fa != fb:
                        diff += 1
            same = same and a["r1"] == b["r1"]
        same = same and all(new[w]["pool"][ml.sname(s)] == old[w]["pool"][ml.sname(s)] for s in ml.STRUCTS)
    folds_present = all(new[w]["k"]["3"]["fold"]["ar2"] is not None for w in range(3))
    return (dict(passed=bool(same and diff == 0 and folds_present), cells=cells, differing_cells=diff,
                 r1_pool_equal=bool(same), folds_present=bool(folds_present)), sum(decs_of(r) for r in new))


# ---------------------------------------------------------------- 入口
def main(seed, out, only, mut, run_id):
    # ml.py を __main__ として起動すると、ここで import した ml は別の写しで、切り替えが入っていない（前回の判断 13）
    ml.set_mut(mut)
    t0 = time.time()
    want = set(only) if only else set(NAMES)
    R = dict(run_id=run_id, mutate=mut)
    simple = {"P-XI": p_xi, "P-BATCH": p_batch, "P-EM3": p_em3, "P-AR1": p_ar1, "P-PRIOR": p_prior, "P-OTH": p_oth,
              "P-JOINT": p_joint}
    for nm, f in simple.items():
        if nm in want:
            R[nm] = f(seed)
    if "P-S" in want:
        R["P-S"] = p_s()
    decs = 0
    need_ex = want & {"P-CH", "P-POOL", "P-AR", "P-LEAK", "P-EM2", "P-INF", "P-PR1", "P-TAU", "P-SUBSET"}
    if need_ex:
        with ProcessPoolExecutor(6) as ex:
            if "P-CH" in want:
                R["P-CH"] = p_ch(seed, mut, ex)
            if want & {"P-POOL", "P-LEAK", "P-EM2", "P-INF", "P-PR1"}:
                pool, leak_pool, d1, pr1, pinf = p_pool_leak(seed, mut, ex)
                decs += d1
                for nm, v in (("P-POOL", pool), ("P-PR1", pr1), ("P-INF", pinf)):
                    if nm in want:
                        R[nm] = v
            if want & {"P-AR", "P-LEAK", "P-EM2", "P-TAU"}:
                ar, leak_ar, d2, ptau = p_ar_leak(seed, mut, ex)
                decs += d2
                for nm, v in (("P-AR", ar), ("P-TAU", ptau)):
                    if nm in want:
                        R[nm] = v
            if want & {"P-SUBSET", "P-EM2"}:
                sub, d3 = p_subset(seed, mut, ex)
                decs += d3
                if "P-SUBSET" in want:
                    R["P-SUBSET"] = sub
    if "P-LEAK" in want:
        allv = dict(leak_pool["leak_medians"], **leak_ar)
        R["P-LEAK"] = dict(passed=max(allv.values()) <= 0.002, medians=allv)
    if "P-EM2" in want:
        R["P-EM2"] = dict(passed=decs == 0, decreases=int(decs))
    R["seconds"] = time.time() - t0
    R["all_passed"] = all(R[n]["passed"] for n in NAMES if n in R)
    json.dump(R, open(out, "w"), indent=1, default=float)
    print(json.dumps({n: R[n]["passed"] for n in NAMES if n in R}))
    return 0 if R["all_passed"] else 3
