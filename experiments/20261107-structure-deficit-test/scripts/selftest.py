"""陽性対照（合成のデータだけ・conditions.md の V2）。ml.py --selftest から呼ぶ。

返り値: 0 = すべて通った・3 = 通らない対照がある（変異の門は 3 を「赤」と読む）。例外は Python の既定（1）。
判定の数は合成の正しさの門で、実データの判定の閾値ではない。
前の試験（tau-mode-candidate）の selftest から、EM の部品の対照（P-XI・P-BATCH・P-EM3・P-AR1・P-PRIOR・P-CH・P-S・P-OTH）を
引き継ぎ（P-XI・P-EM3・P-AR1 は記号の数 10・26・50 で回す）、本人の当てはめの対照は今回の経路（run_one）で作り直した
（P-LEAK・P-TAU・P-EM2）。足す対照: P-Q・P-SHUF・P-QW・P-D・P-OTHER・P-COMP・P-PERS・P-SAME（conditions V2）。
"""
import json
import math
import os
import pickle
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import data as DT
import forms
import hmm2 as H
import ml

NAMES = ["P-XI", "P-BATCH", "P-EM3", "P-AR1", "P-PRIOR", "P-CH", "P-S", "P-OTH",
         "P-Q", "P-SHUF", "P-QW", "P-D", "P-TAU", "P-OTHER", "P-LEAK", "P-COMP", "P-PERS", "P-EM2", "P-SAME"]
STICKY = 0.9
HERE = os.path.dirname(os.path.abspath(__file__))
NSYMS = (10, 26, 50)


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


def ar_model(rng, K=2, conc=0.3):
    """AR(1)-HMM の合成: 状態ごとに別の 1 次のマルコフ（行は Dirichlet(conc)・粘る状態）。"""
    A = 0.95 * np.eye(K) + 0.05 * rng.dirichlet(np.ones(K), K)
    return dict(kind="ar", pi=np.ones(K) / K, A=A / A.sum(1, keepdims=True), H=rng.dirichlet(np.ones(H.NSYM), K),
                C=np.stack([rng.dirichlet(np.full(H.NSYM, conc), H.NSYM) for _ in range(K)]))


def unit_of(seq):
    return dict(start=0, seqs=[np.asarray(seq, dtype=np.int64)], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


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


def at_nsym(n, f, *a):
    H.set_nsym(n)
    try:
        return f(*a)
    finally:
        H.set_nsym(26)


def med(st):
    return ml.med_of(st)


# ---------------------------------------------------------------- 引き継ぐ対照（EM の部品）
def p_xi_one(seed):
    rng = np.random.default_rng([seed, 1, H.NSYM])
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
    return worst


def p_xi(seed):
    w = {str(n): at_nsym(n, p_xi_one, seed) for n in NSYMS}
    return dict(passed=max(w.values()) < 1e-9, worst_rel=w)


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


def p_em3_one(seed):
    rng = np.random.default_rng([seed, 3, H.NSYM])
    seqs = H.sample(common_model(rng), [700, 1500, 300], rng)
    _, h, T = H.r0_r1(seqs)
    sum_dev, at_dev = 0.0, 0.0
    for kind, K in [("hmm", 3), ("ar", 2)]:
        m = H.random_model(kind, K, rng, r1=T, r0=h)
        for D in (H.Data(seqs, chunk=H.CHUNK), H.Data(seqs)):
            dist, at, c = H.pred_dist(m, D)
            sum_dev = max(sum_dev, float(np.abs(dist.sum(2) - 1)[D.M].max()))
            at_dev = max(at_dev, float(np.abs(np.exp(np.log(c)) - at)[D.M].max()))
    return sum_dev, at_dev


def p_em3(seed):
    r = {str(n): at_nsym(n, p_em3_one, seed) for n in NSYMS}
    ok = all(a < 1e-9 and b < 1e-12 for a, b in r.values())
    return dict(passed=ok, sum_dev_at_dev=r)


def p_ar1_one(seed):
    rng = np.random.default_rng([seed, 4, H.NSYM])
    worst = 0.0
    for _ in range(3):
        tr = H.sample(ar_model(rng), [1500, 2500, 700], rng)
        te = H.sample(ar_model(rng), [800, 1200], rng)
        _, h, T = H.r0_r1(tr)
        m, _ = H.fit([("rand", H.random_model("ar", 1, rng, r1=T, r0=h))], H.Data(tr, chunk=H.CHUNK), H.base_prior("ar", 1))
        ev = ml.Eval(te, [np.ones(len(s), dtype=bool) for s in te])
        worst = max(worst, abs(ev.ll(m)[0] - ev.ll_r1(h, T)[0]))
    return worst


def p_ar1(seed):
    w = {str(n): at_nsym(n, p_ar1_one, seed) for n in NSYMS}
    return dict(passed=max(w.values()) < 1e-9, worst=w)


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


def ch_job(args):
    mut, seed, r = args
    ml.set_mut(mut)
    rng = np.random.default_rng([seed, 77, r])
    cm = common_model(rng)
    seqs = H.sample(cm, [20_000] * 5, rng)
    pr = H.base_prior("hmm", 3)
    mc, _, _, _, _ = H.em_from(cm, H.Data(seqs, chunk=H.CHUNK), pr)
    mu, _, _, _, _ = H.em_from(cm, H.Data(seqs), pr)
    return float(max(np.abs(mc["A"] - mu["A"]).max(), np.abs(mc["B"] - mu["B"]).max()))


def p_ch(seed, mut, ex):
    d = list(ex.map(ch_job, [(mut, seed, r) for r in range(10)]))
    return dict(passed=float(np.median(d)) < 0.02, median=float(np.median(d)), runs=len(d))


def p_s():
    ok = True
    for Hh, grid in ((5, ml.DATASETS["coauthor"]["grid"]), (1, ml.DATASETS["cs1"]["grid"])):
        for n in range(Hh + 1, 60):
            for k in grid:
                if k <= n - Hh:
                    ok = ok and DT.check_split(n, k, Hh)
        writers = [[dict(tag=(w, i)) for i in range(n)] for w, n in enumerate([3, 8, 12, Hh, Hh + 1, 30])]
        for w in range(len(writers)):
            tags = {u["tag"] for u in ml.pool_units(writers, Hh, exclude=w)}
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


# ---------------------------------------------------------------- 足す対照: 列・並べ替え・幅・D
def rust_bin(v, q_):
    """engine.rs の (x * q).floor().min(q − 1) as usize（Rust の float → usize は負を 0 に飽和）を 1 つずつ写した参照（NaN は扱わない）。"""
    x = min(math.floor(v * q_), q_ - 1)
    return 0 if x < 0 else int(x)


def p_q(seed):
    rng = np.random.default_rng([seed, 21])
    vals = [i / q_ + e for q_ in (3, 5, 7) for i in range(0, q_ + 1) for e in (-1e-12, 0.0, 1e-12)]
    vals += [-0.5, -1e-9, 0.0, 1.0, 1.0 + 1e-9, 1.7] + list(rng.uniform(-0.2, 1.2, 500))
    bin_ok = all(int(DT.axis_bin(np.array([v]), q_)[0]) == rust_bin(v, q_) for q_ in (3, 5, 7) for v in vals)
    # 合成の feat 行: obs は engine の式で作る（25 は backspace 連打）
    n = 3000
    ex, ey = rng.uniform(-0.1, 1.1, n), rng.uniform(-0.1, 1.1, n)
    ex[:20] = 1.0
    obs = np.array([rust_bin(a, 5) * 5 + rust_bin(b, 5) for a, b in zip(ex, ey)])
    pen = rng.random(n) < 0.05
    obs[pen] = 25
    rows = np.stack([ex, ey, obs], 1)
    q5 = bool(np.array_equal(DT.quantize(rows, 5), obs))
    pen_ok = all(bool(np.all(DT.quantize(rows, q_)[pen] == q_ * q_)) and int(DT.quantize(rows, q_).max()) <= q_ * q_
                 for q_ in (3, 5, 7))
    ref37 = all(bool(np.array_equal(DT.quantize(rows, q_)[~pen],
                                    np.array([rust_bin(a, q_) * q_ + rust_bin(b, q_) for a, b in zip(ex[~pen], ey[~pen])])))
                for q_ in (3, 7))
    # 門の陽性・陰性: 一致する単位で外れ 0、obs を 1 行だけ変えると外れ 1
    w = [[dict(rows=[rows[:1000], rows[1000:]], seqs=[obs[:1000], obs[1000:]])]]
    g0 = DT.q_gate(w)
    obs2 = obs.copy()
    obs2[5] = (obs2[5] + 1) % 25
    g1 = DT.q_gate([[dict(rows=[rows], seqs=[obs2])]])
    ok = bin_ok and q5 and pen_ok and ref37 and g0 == (n, 0) and g1 == (n, 1)
    return dict(passed=bool(ok), bins_equal_rust=bool(bin_ok), q5_equals_obs=q5, penalty=bool(pen_ok), q3_q7_ref=bool(ref37),
                gate_clean=list(g0), gate_one_off=list(g1))


def shuf_writers(rng):
    """P-SHUF の合成: 各系列の行は q = 7 の 49 個の格子の記号が互いに違う（記号から行が分かる）。CS1 の形（単位に系列が複数・H = 1）。"""
    cells = [(i, j) for i in range(7) for j in range(7)]
    writers = []
    for _ in range(4):
        ss = []
        for _ in range(4):
            rows, pf = [], []
            for _ in range(3):
                L = int(rng.integers(8, 40))
                pick = rng.permutation(49)[:L]
                r = np.array([[(cells[c][0] + 0.5) / 7, (cells[c][1] + 0.5) / 7, 0.0] for c in pick])
                r[:, 2] = [rust_bin(a, 5) * 5 + rust_bin(b, 5) for a, b in r[:, :2]]
                rows.append(r)
                pf.append(rng.random(L) < 0.5)
            ss.append(dict(rows=rows, pflag=pf, seqs=[DT.quantize(r, 5) for r in rows]))
        writers.append(ss)
    return writers


def p_shuf(seed):
    rng = np.random.default_rng([seed, 22])
    W = shuf_writers(rng)
    H_ = 1
    o7 = DT.variant(W, 7, "o", seed, 1, H_)
    p7, p3, p5 = (DT.variant(W, q_, "p", seed, 1, H_) for q_ in (7, 3, 5))
    same_o = all(np.array_equal(a, DT.quantize(r, 7)) for ss, ws in zip(o7, W) for u, wu in zip(ss, ws)
                 for a, r in zip(u["seqs"], wu["rows"]))
    multiset, changed, total, same_perm, pflag_ok, eval_changed = True, 0, 0, True, True, 0
    for wi, (ws, a7, a3, a5) in enumerate(zip(W, p7, p3, p5)):
        for ui, (wu, u7, u3, u5) in enumerate(zip(ws, a7, a3, a5)):
            for r, f, s7, s3, s5, f7 in zip(wu["rows"], wu["pflag"], u7["seqs"], u3["seqs"], u5["seqs"], u7["pflag"]):
                orig7 = DT.quantize(r, 7)
                multiset = multiset and sorted(orig7.tolist()) == sorted(np.asarray(s7).tolist())
                if not multiset:
                    continue
                pos = {int(v): i for i, v in enumerate(orig7)}
                perm = np.array([pos[int(v)] for v in s7])
                total += 1
                ch = not np.array_equal(perm, np.arange(len(perm)))
                changed += ch
                if ui >= len(ws) - H_ and ch:
                    eval_changed += 1
                same_perm = (same_perm and np.array_equal(s3, DT.quantize(r[perm], 3))
                             and np.array_equal(s5, DT.quantize(r[perm], 5)))
                pflag_ok = pflag_ok and np.array_equal(np.asarray(f7), np.asarray(f)[perm])
    ok = same_o and multiset and changed == total and total > 0 and same_perm and pflag_ok and eval_changed > 0
    return dict(passed=bool(ok), order_o_unchanged=bool(same_o), per_seq_multiset=bool(multiset), changed=int(changed),
                seqs=int(total), same_perm_3_cols=bool(same_perm), pflag_moves=bool(pflag_ok), eval_seqs_changed=int(eval_changed))


def p_qw(seed):
    rng = np.random.default_rng([seed, 23])
    ok = True
    for q_ in (3, 7):
        H.set_nsym(q_ * q_ + 1)
        try:
            n = q_ * q_ + 1
            seqs = [rng.integers(0, n, 400) for _ in range(4)]
            for kind, K in (("hmm", 3), ("ar", 2)):
                _, h, T = H.r0_r1(seqs)
                m, _ = H.fit([("r", H.random_model(kind, K, rng, r1=T, r0=h))], H.Data(seqs, chunk=H.CHUNK), H.base_prior(kind, K))
                if kind == "hmm":
                    ok = ok and m["B"].shape == (K, n)
                else:
                    ok = ok and m["H"].shape == (K, n) and m["C"].shape == (K, n, n)
                ok = ok and T.shape == (n, n)
        finally:
            H.set_nsym(26)
    return dict(passed=bool(ok))


def p_d(seed):
    rng = np.random.default_rng([seed, 24])
    ws = list(range(9))
    results = {w: dict(em=dict(pool={"hmm3": [float(rng.normal()), float(rng.normal())]},
                               k={"5": dict(r1=[float(rng.normal()), float(rng.normal())])})) for w in ws}
    dev = 0.0
    for j in (0, 1):
        got = ml.pool_r1_values(results, ws, 5, "hmm3", j, sign=-1)
        want = [results[w]["em"]["k"]["5"]["r1"][j] - results[w]["em"]["pool"]["hmm3"][j] for w in ws]
        dev = max(dev, float(np.max(np.abs(np.array(got) - np.array(want)))))
    return dict(passed=bool(dev < 1e-12), max_abs_dev=dev)


# ---------------------------------------------------------------- 足す対照: 経路を通す（run_one）
HMM3 = [("hmm", 3)]


def writers_from(models, rng, n_us=(40, 40, 20, 20, 20, 20, 20, 20), L=300):
    """書き手ごとの単位の数 n_us（40 の 2 人は P30 にも入る・P-OTHER のパネルの照らし・code-reviewer MEDIUM-2）。"""
    return [[unit_of(s) for s in H.sample(models[w], [L] * n, rng)] for w, n in enumerate(n_us)]


def shuffled(writers, rng):
    out = []
    for ss in writers:
        nu = []
        for u in ss:
            perms = [rng.permutation(len(s)) for s in u["seqs"]]
            nu.append(dict(u, seqs=[np.asarray(s)[p] for s, p in zip(u["seqs"], perms)],
                           pflag=[np.asarray(f)[p] for f, p in zip(u["pflag"], perms)]))
        out.append(nu)
    return out


def cell(D, k, name):
    return D["em"]["P15"][str(k)]["structs"][name]


def part_vals(Do, Dp, k, name):
    o, p = cell(Do, k, name), cell(Dp, k, name)
    return dict(G_o=med(o["tau_other"]["all/self_minus_pool_same"]), G_p=med(p["tau_other"]["all/self_minus_pool_same"]),
                G0_o=med(o["G0r"]["all"]), D_o=med(o["deficit"]["all"]), D_p=med(p["deficit"]["all"]),
                S0_o=med(o["S0"]["all"]))


part1, part2 = forms.part1, forms.part2


def run_pair(writers, seed, structs=HMM3):
    rng = np.random.default_rng([seed, 31])
    Do, Xo = ml.run_one("coauthor", None, seed, 5, "o", 4, ex_writers=writers, structs=structs)
    Dp, Xp = ml.run_one("coauthor", None, seed, 5, "p", 4, ex_writers=shuffled(writers, rng), structs=structs)
    return Do, Xo, Dp, Xp


def comp_models(rng, n_w):
    """P-COMP: 1 次の依存の強い AR(1)（K = 1）。書き手ごとに遷移の行を少しずらす（共通の行と書き手の行の混ぜ）。"""
    base = ar_model(rng, K=1, conc=0.2)
    out = []
    for _ in range(n_w):
        C = 0.6 * base["C"][0] + 0.4 * rng.dirichlet(np.full(H.NSYM, 0.2), H.NSYM)
        out.append(dict(kind="ar", pi=np.ones(1), A=np.ones((1, 1)), H=base["H"].copy(), C=C[None]))
    return out


def pers_models(rng, n_w):
    """P-PERS: 順の依存が無い（K = 1 のふつうの HMM）。書き手ごとに記号の頻度が大きく違う。"""
    return [dict(kind="hmm", pi=np.ones(1), A=np.ones((1, 1)), B=rng.dirichlet(np.full(H.NSYM, 0.5))[None]) for _ in range(n_w)]


def p_other(X, writers):
    """S0 を書き手ごとに作り直して照らす: v ≠ w・同じパネル（P15 の k = 1・5・15 と P30 の k = 30）・同じ k・
    v の τ = 0 の乱数の開始点の解（v の評価で self0r と一致）。P30 は単位 40 の 2 人だけ。"""
    res, S0, fits, ns = X["results"], X["S0"], X["fits"], X["ns"]
    dev, self_dev, cnt, p30 = 0.0, 0.0, 0, 0
    for k, nmin in ((1, 20), (5, 20), (15, 20), (30, 35)):
        ws = [w for w in res if ns[w] >= nmin]
        for w in ws:
            ev = ml.eval_of(writers[w], 5)
            pool = res[w]["em"]["pool"]["hmm3"]
            vals = [ev.ll(fits[v]["hmm3"][str(k)]["0r"])[0] - pool[0] for v in ws if v != w]
            dev = max(dev, abs(float(np.median(vals)) - S0[w][str(k)]["hmm3"][0]))
            cnt += 1
            p30 += k == 30
        for v in ws:
            a = ml.eval_of(writers[v], 5).ll(fits[v]["hmm3"][str(k)]["0r"])
            b = res[v]["em"]["k"][str(k)]["self0r"]["hmm3"]
            self_dev = max(self_dev, abs(a[0] - b[0]))
    ok = dev < 1e-12 and self_dev < 1e-12 and cnt > 0 and p30 == 2
    return dict(passed=bool(ok), max_abs_dev=dev, v_model_dev=self_dev, cells=cnt, p30_cells=p30)


def p_leak(X, writers, truths):
    """m1 の漏れ: 本人（全 τ）の評価 − 真の母数の評価（独立の前向き）の中央値が 0.002 以下。"""
    res = X["results"]
    out = {}
    for k in (1, 5, 15):
        for t in ml.TAU_KEYS:
            d = []
            for w in res:
                te = [u["seqs"][0] for u in writers[w][-5:]]
                tl, tn = honest_ll(truths[w], te)
                d.append(res[w]["em"]["k"][str(k)]["self"]["hmm3"][t][0] - tl / tn)
            out["k%d_tau%s" % (k, t)] = float(np.median(d))
    return dict(passed=bool(max(out.values()) <= 0.002), worst=max(out.values()))


def decs_summary(D):
    n = sum(v["decreases"] for v in D["pool_full_diag"].values()) + sum(v["decreases"] for v in D["pool_excl_diag"].values())
    for pn in D["em"].values():
        for E in pn.values():
            for St in E.get("structs", {}).values():
                n += sum(v["decreases"] for v in St["diag"].values())
    return n


def p_tau(seed, ex, mut):
    """m15: AR の合成で、本人の母数の A・C と事前分布の最頻値 normalize(S̄) の最大の絶対差（書き手の中央値）が
    τ ∈ {10^3, …, 10^6} で増えず、10^6 で 0.02 未満、w を除く共通との差も 10^6 で 0.02 未満（tau-extend の判断 6）。"""
    rng = np.random.default_rng([seed, 7])
    tm = ar_model(rng, 2)
    writers = [[unit_of(s) for s in H.sample(tm, [650] * 10, rng)] for _ in range(17)]
    s = ("ar", 2)
    full, _ = ml.fit_pool_full(dict(ds="coauthor", writers=writers, si=ml.SEQ_NO[s], seed=seed + 100))
    pres = list(ex.map(pool_excl_job, [(mut, dict(ds="coauthor", writers=writers, w=w, start=full)) for w in range(17)]))
    res = list(ex.map(tau_job, [(mut, writers[w], {"ar2": pres[w][:2]}, seed, w) for w in range(17)]))
    taus = [t for t in ml.TAUS_FIT if t >= 1000]
    mode_med, pool_med = {}, {}
    for t in taus:
        dm, dp = [], []
        for w, r in enumerate(res):
            m, pm = r["fits"]["ar2"]["5"][str(t)], pres[w][0]
            mode = H.normalize("ar", pres[w][1])
            dm.append(float(max(np.abs(m["A"] - mode["A"]).max(), np.abs(m["C"] - mode["C"]).max())))
            dp.append(float(max(np.abs(m["A"] - pm["A"]).max(), np.abs(m["C"] - pm["C"]).max())))
        mode_med[str(t)], pool_med[str(t)] = float(np.median(dm)), float(np.median(dp))
    tv = [mode_med[str(t)] for t in taus]
    ok = all(b <= a for a, b in zip(tv, tv[1:])) and tv[-1] < 0.02 and pool_med[str(taus[-1])] < 0.02
    decs = sum(p[2]["decreases"] for p in pres) + sum(dd["decreases"] for r in res for rk in r["k"].values()
                                                         for v in rk["diag"].values() for dd in v.values())
    return dict(passed=bool(ok), to_prior_mode=mode_med, to_pool=pool_med), decs


def pool_excl_job(args):
    mut, job = args
    ml.set_mut(mut)
    return ml.fit_pool_excl(job)


def tau_job(args):
    mut, units, pools, seed, w = args
    ml.set_mut(mut)
    rng = np.random.default_rng([seed + 10, w])
    return ml.em_writer(units, 5, [5], [5], pools, rng, structs=[("ar", 2)], keep="all")


# ---------------------------------------------------------------- P-SAME（前の試験の em_writer と別のプロセスで照らす）
def same_job(args):
    mut, units, Hh, ks, fit_ks, pools, seed, w = args
    ml.set_mut(mut)
    H.set_nsym(26)
    rng = np.random.default_rng([seed + 10, w])
    return ml.em_writer(units, Hh, ks, fit_ks, pools, rng)


def p_same(seed, mut, ex):
    """合成の書き手 3 人で、26 記号のそのままの組の em_writer（作らない k・折り目の乱数を捨てる）が、
    tau-extend の em_writer（hmm3・ar1〜ar3 の全 τ・診断）と ml-improve の em_writer（6 構造の τ ∈ {0, 100, 1,000, 10,000}）
    と、作る k の本人・共通・r1・記号の数でちょうど一致する。"""
    rng = np.random.default_rng([seed, 41])
    cm = common_model(rng)
    writers = [[unit_of(s) for s in H.sample(perturb(cm, rng), [300] * 11, rng)] for _ in range(3)]
    pool = H.sample(cm, [600] * 20, rng)
    _, hp, Tp = H.r0_r1(pool)
    Dp = H.Data(pool, chunk=H.CHUNK)
    pools6 = {}
    for s in ml.PREV_STRUCTS:
        m = H.random_model(s[0], s[1], rng, r1=Tp, r0=hp)
        S, _ = H.counts(m, Dp)
        pools6[ml.sname(s)] = (m, H.sbar_of(S, Dp.nobs))
    Hh, ks, fit_ks = 5, [1, 2, 3, 5], [1, 5]
    new = list(ex.map(same_job, [(mut, writers[w], Hh, ks, fit_ks, pools6, seed, w) for w in range(3)]))
    old = {}
    with tempfile.TemporaryDirectory() as td:
        pin = os.path.join(td, "in.pkl")
        pickle.dump(dict(writers=writers, pools=pools6, seed=seed, H=Hh, ks=ks), open(pin, "wb"))
        for which in ("tau", "mli"):
            pout = os.path.join(td, which + ".pkl")
            r = subprocess.run([sys.executable, "-I", "-B", "-X", "utf8", os.path.join(HERE, "same_old.py"), which, pin, pout],
                               capture_output=True, text=True)
            if r.returncode != 0:
                return dict(passed=False, note="前の試験のコードが走らない: " + which, stderr=r.stderr[-2000:])
            old[which] = pickle.load(open(pout, "rb"))
    cells, diff = 0, 0
    for w in range(3):
        a = new[w]
        for which, names, taus, keys in (("tau", ["hmm3", "ar1", "ar2", "ar3"], ml.TAU_KEYS, ("r1", "diag")),
                                         ("mli", [ml.sname(s) for s in ml.PREV_STRUCTS], ["0", "100", "1000", "10000"], ("r1",))):
            b = old[which][w]
            for nm in names:
                cells += 1
                diff += a["pool"][nm] != b["pool"][nm]
            for k in fit_ks:
                ak, bk = a["k"][str(k)], b["k"][str(k)]
                for key in keys:
                    if key == "diag":
                        for nm in names:
                            cells += 1
                            diff += ak["diag"][nm] != bk["diag"][nm]
                    else:
                        cells += 1
                        diff += ak[key] != bk[key]
                for nm in names:
                    for t in taus:
                        cells += 1
                        diff += ak["self"][nm][t] != bk["self"][nm][t]
                if "n_train" in bk:
                    cells += 1
                    diff += ak["n_train"] != bk["n_train"]
    return dict(passed=bool(diff == 0 and cells > 0), cells=cells, differing=int(diff))


# ---------------------------------------------------------------- 入口
def main(seed, out, only, mut, run_id):
    ml.set_mut(mut)  # ml.py を __main__ として起動すると、ここで import した ml は別の写し（前の試験の判断 13）
    H.set_nsym(26)
    t0 = time.time()
    want = set(only) if only else set(NAMES)
    R = dict(run_id=run_id, mutate=mut)
    simple = {"P-XI": p_xi, "P-BATCH": p_batch, "P-EM3": p_em3, "P-AR1": p_ar1, "P-PRIOR": p_prior, "P-OTH": p_oth,
              "P-Q": p_q, "P-SHUF": p_shuf, "P-QW": p_qw, "P-D": p_d}
    for nm, f in simple.items():
        if nm in want:
            R[nm] = f(seed)
    if "P-S" in want:
        R["P-S"] = p_s()
    decs = 0
    if want & {"P-CH", "P-TAU", "P-SAME", "P-EM2"}:
        with ProcessPoolExecutor(6) as ex:
            if "P-CH" in want:
                R["P-CH"] = p_ch(seed, mut, ex)
            if want & {"P-TAU", "P-EM2"}:
                R_tau, d = p_tau(seed, ex, mut)
                decs += d
                if "P-TAU" in want:
                    R["P-TAU"] = R_tau
            if "P-SAME" in want:
                R["P-SAME"] = p_same(seed, mut, ex)
    if want & {"P-OTHER", "P-LEAK", "P-COMP", "P-EM2"}:
        rng = np.random.default_rng([seed, 32])
        truths = comp_models(rng, 8)
        writers = writers_from(truths, rng)
        Do, Xo, Dp, Xp = run_pair(writers, seed)
        decs += decs_summary(Do) + decs_summary(Dp)
        if "P-OTHER" in want:
            R["P-OTHER"] = p_other(Xo, writers)
        if "P-LEAK" in want:
            R["P-LEAK"] = p_leak(Xo, writers, truths)
        if "P-COMP" in want:
            v = part_vals(Do, Dp, 15, "hmm3")
            R["P-COMP"] = dict(passed=part1(v) == "vanish", part1=part1(v), part2=part2(v), values=v)
    if want & {"P-PERS", "P-EM2"}:
        rng = np.random.default_rng([seed, 33])
        writers = writers_from(pers_models(rng, 8), rng)
        Do, _, Dp, _ = run_pair(writers, seed + 1)
        decs += decs_summary(Do) + decs_summary(Dp)
        if "P-PERS" in want:
            v = part_vals(Do, Dp, 15, "hmm3")
            R["P-PERS"] = dict(passed=part2(v) == "own" and part1(v) != "vanish", part1=part1(v), part2=part2(v), values=v)
    if "P-EM2" in want:
        R["P-EM2"] = dict(passed=decs == 0, decreases=int(decs))
    R["seconds"] = time.time() - t0
    R["all_passed"] = all(R[n]["passed"] for n in NAMES if n in R)
    ml.dump_json(R, out, indent=1)
    print(json.dumps({n: R[n]["passed"] for n in NAMES if n in R}))
    return 0 if R["all_passed"] else 3
