"""round 7 の計算 A・B の門（conditions.md の追記「入れ替えの対照（A）と先頭の記号を除いた残り（B）」の「門」・合成だけ）。

使い方: python3 -I selftest_r7.py <out.json> [--mutate f1..f9] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compute as CP  # noqa: E402
import pinned4  # noqa: E402
import r7 as R7  # noqa: E402
import sym as SM  # noqa: E402
from pinned4 import H, ml  # noqa: E402

NAMES = ["P-HASH", "P-NONFIRST", "P-REPLAYALL", "P-REPLAY03", "P-BPICK", "P-PAIRPOOL", "P-SWAP", "P-AGG", "P-FORMR7"]
SEED = pinned4.SEED
INF = ml.INF


def unit_of(seq):
    return dict(start=0, seqs=[seq], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


def synth_model(rng):
    A = 0.95 * np.eye(2) + 0.05 * rng.dirichlet(np.ones(2), 2)
    return dict(kind="ar", pi=np.ones(2) / 2, A=A / A.sum(1, keepdims=True), H=rng.dirichlet(np.ones(H.NSYM), 2),
                C=np.stack([rng.dirichlet(np.full(H.NSYM, 0.3), H.NSYM) for _ in range(2)]))


def synth_writers(rng, n_writers, n_units, length=80):
    m = synth_model(rng)
    return [[unit_of(s) for s in H.sample(m, [length] * n_units, rng)] for _ in range(n_writers)]


def p_hash():
    return dict(passed=True, hashes=pinned4.hashes())


def p_nonfirst():
    """手の例: 系列 3 本（長さ 5・7・4）。先頭を除く量が「1 番目以降の和 / (記号の数 − 3)」、全記号と押下は ml.Eval と同じ。
    r1 の先頭を除く量は遷移だけの平均。"""
    rng = np.random.default_rng([SEED, 41])
    m = synth_model(rng)
    seqs = [rng.integers(0, H.NSYM, n) for n in (5, 7, 4)]
    pf = [rng.random(len(s)) < 0.5 for s in seqs]
    e1, e2 = ml.Eval(seqs, pf), R7.Eval2(seqs, pf)
    a, b = e1.ll(m), e2.ll(m)
    lp = H.pred_logprob(m, H.Data(seqs))
    want = sum(float(lp[i, 1:len(s)].sum()) for i, s in enumerate(seqs)) / (sum(map(len, seqs)) - 3)
    ok = CP.same_bits(a, b[:2]) and abs(b[2] - want) < 1e-12
    h = rng.dirichlet(np.ones(H.NSYM))
    T = rng.dirichlet(np.ones(H.NSYM), H.NSYM)
    r = e2.ll_r1(h, T)
    want_r = float(np.mean(np.concatenate([np.log(T[s[:-1], s[1:]]) for s in seqs])))
    ok = ok and CP.same_bits(e1.ll_r1(h, T), r[:2]) and abs(r[2] - want_r) < 1e-12
    ok = ok and abs(e2.first_share() - 3 / 16) < 1e-15
    return dict(passed=bool(ok))


def pools_of(writers, w, alpha=None):
    full = {ml.sname(s): ml.fit_pool_full(dict(ds="coauthor", si=ml.SEQ_NO[s], seed=SEED, writers=writers))[0] for s in ml.STRUCTS}
    out = {}
    for s in ml.STRUCTS:
        pm, sb, _ = ml.fit_pool_excl(dict(ds="coauthor", writers=writers, w=w, start=full[ml.sname(s)]))
        out[ml.sname(s)] = (pm, sb)
    return out


def p_replayall():
    """合成の書き手 4 人（各 10 単位）: 倍率 1 の 4 構造の引き直し（k = 2・5）と r1 が mode の em_writer とビットまで同じで、
    書き手の乱数を引き終えた状態も同じ。"""
    rng = np.random.default_rng([SEED, 42])
    writers = synth_writers(rng, 4, 10)
    ok, n = True, 0
    for w in (0, 3):
        pools = pools_of(writers, w)
        ks = [k for k in ml.DATASETS["coauthor"]["grid"] if k <= len(writers[w]) - 5]
        r1 = np.random.default_rng([SEED + 10, w])
        res = ml.em_writer(writers[w], 5, ks, pools, r1)
        r2 = np.random.default_rng([SEED + 10, w])
        mine = R7.replay(writers[w], 5, ks, [2, 5], pools, r2, 1.0, list(ml.STRUCTS))
        for s in ml.STRUCTS:
            for k in ("2", "5"):
                for t in map(str, ml.TAUS_FIT):
                    ok = ok and R7.same2(mine["self"][ml.sname(s)][k][t], res["k"][k]["self"][ml.sname(s)][t])
                    n += 1
        for k in ("2", "5"):
            ok = ok and R7.same2(mine["r1"][k], res["k"][k]["r1"])
        ok = ok and r1.bit_generator.state == r2.bit_generator.state
    return dict(passed=bool(ok), compared=n)


def p_replay03():
    """倍率 0.03 の ar3 の引き直しが sym.py の replay_writer とビットまで同じで、倍率 1 とは違う。"""
    rng = np.random.default_rng([SEED, 43])
    writers = synth_writers(rng, 4, 9)
    pools = pools_of(writers, 1)
    ks = [k for k in ml.DATASETS["coauthor"]["grid"] if k <= len(writers[1]) - 5]
    ref = SM.replay_writer(writers[1], 5, ks, [3], pools["ar3"][0], pools["ar3"][1], np.random.default_rng([SEED + 10, 1]), 0.03)
    mine = R7.replay(writers[1], 5, ks, [3], pools, np.random.default_rng([SEED + 10, 1]), 0.03, [R7.AR3])
    one = R7.replay(writers[1], 5, ks, [3], pools, np.random.default_rng([SEED + 10, 1]), 1.0, [R7.AR3])
    ts = list(map(str, ml.TAUS_FIT))
    ok = all(R7.same2(mine["self"]["ar3"]["3"][t], ref["3"][t]) for t in ts)
    ok = ok and any(mine["self"]["ar3"]["3"][t][0] != one["self"]["ar3"]["3"][t][0] for t in ts)
    return dict(passed=bool(ok))


def p_bpick():
    """手の例（6 人・k = 5）: 全記号では ar3 の τ = 1000 が最良（−0.99 − r1）、先頭を除く量では ar1 の τ = 100 が最良。
    主は ar3・1000 の先頭を除く残り（−0.998 − (−1.0) = +2e-3）、全記号の残りは −0.99 − (−1.0) = +1e-2、
    副（選び直し）は ar1・100 の −0.5 − (−1.0) = +0.5。対称版も同じ形（τ = 1000 と τ = 100）。"""
    ws = list(range(6))
    k = 5
    R, FX, P1 = {}, {}, {}
    for v in ws:
        selfv = {n: {t: [-1.0, None] for t in ml.TAU_KEYS} for n in map(ml.sname, ml.STRUCTS)}
        selfv["ar3"]["1000"] = [-0.99, None]
        R[v] = dict(em=dict(pool={n: [-1.0, None] for n in selfv}, k={"5": dict(r1=[-1.1, None], self=selfv)}))
        fx = {n: {"5": {t: [-1.0, None, -1.0] for t in map(str, ml.TAUS_FIT)}} for n in selfv}
        fx["ar3"]["5"]["1000"] = [-0.99, None, -0.998]
        fx["ar1"]["5"]["100"] = [-1.0, None, -0.5]
        FX[v] = dict(self=fx, r1={"5": [-1.1, None, -1.1]}, first_share=0.01)
        P1[v] = {n: [-1.0, None, -1.0] for n in selfv}
    for v in ws:
        R[v]["em"]["k"]["5"]["self"] = {n: dict(d, **{INF: R[v]["em"]["pool"][n]}) for n, d in R[v]["em"]["k"]["5"]["self"].items()}
    C = R7.b_fix_cell(ws, k, R, FX, P1, np.random.default_rng(0))
    ok = abs(C["F"]["median"] - 2e-3) < 1e-12 and abs(C["R"]["median"] - 1e-2) < 1e-12
    ok = ok and abs(C["F_reselected"]["median"] - 0.5) < 1e-12
    # 対称版: 全記号は τ = 1000、先頭を除くと τ = 100
    S03 = {v: {"5": {t: [-1.0, None] for t in map(str, ml.TAUS_FIT)}} for v in ws}
    SY = {v: dict(self={"ar3": {"5": {t: [-1.0, None, -1.0] for t in map(str, ml.TAUS_FIT)}}}, r1={"5": [-1.1, None, -1.1]},
                  first_share=0.01) for v in ws}
    for v in ws:
        S03[v]["5"]["1000"] = [-0.99, None]
        SY[v]["self"]["ar3"]["5"]["1000"] = [-0.99, None, -0.998]
        SY[v]["self"]["ar3"]["5"]["100"] = [-1.0, None, -0.5]
    P03 = {v: [-1.0, None] for v in ws}
    PS = {v: [-1.0, None, -1.0] for v in ws}
    Cs = R7.b_sym_cell(ws, k, R, S03, P03, SY, PS, np.random.default_rng(0))
    ok = ok and abs(Cs["F"]["median"] - 2e-3) < 1e-12 and abs(Cs["R"]["median"] - 1e-2) < 1e-12
    ok = ok and abs(Cs["F_reselected"]["median"] - 0.5) < 1e-12
    return dict(passed=bool(ok))


def p_pairpool():
    rng = np.random.default_rng([SEED, 44])
    writers = synth_writers(rng, 5, 8, length=20)
    got = R7.pool_units2(writers, 5, [1, 3])
    want = [u for j in (0, 2, 4) for u in ml.non_eval(writers[j], 5)]
    ok = len(got) == len(want) and all(a is b for a, b in zip(got, want))
    one, ref = R7.pool_units2(writers, 5, [2]), ml.pool_units(writers, 5, exclude=2)
    ok = ok and len(one) == len(ref) and all(a is b for a, b in zip(one, ref))
    return dict(passed=bool(ok))


def p_swap():
    """合成の書き手 4 人（各 10 単位・k = 5）: 入れ替えの値は w の学習の単位を書き換えても同じで、v の学習の単位を書き換えると
    変わる。事前が 0.03 × 基 + τ_w S̄_{-w,-v}（w と v の選びを違えた手の参照とビットまで同じ）。"""
    rng = np.random.default_rng([SEED, 45])
    writers = synth_writers(rng, 4, 10)
    w, v = 0, 1
    full = CP.job_full(dict(ds="coauthor", s=R7.AR3, alpha=0.03, seed=SEED, writers=writers))
    pp = R7.job_excl(dict(ds="coauthor", excl=[w, v], start=full, alpha=0.03, writers=writers))
    picks = {"5": {w: "10000", v: "100"}}
    base = R7.job_pair(R7.pair_job(w, v, 0, 1, picks, pp, [5], writers=writers))["5"]
    # 手の参照: v の学習の 5 単位・τ_w = 10000・S̄_{-w,-v}・乱数 [SEED + 30, 0, 1, 5]
    train, _ = ml.DT.split(10, 5, 5)
    tr = ml.seqs_of([writers[v][i] for i in train])
    _, h, T = H.r0_r1(tr)
    r = np.random.default_rng([SEED + 30, 0, 1, 5])
    D = H.Data(tr, chunk=H.CHUNK)
    m0, _ = H.fit([("pool", pp["m"]), ("rand", H.random_model("ar", 3, r, r1=T, r0=h))], D, SM.prior_sym("ar", 3, 0, None, 0.03))
    pr = {k: x * 0.03 for k, x in H.base_prior("ar", 3).items()}
    for key in H.keys_of("ar"):
        pr[key] = pr[key] + 10000.0 * pp["sb"][key]
    m, _ = H.fit([("pool", pp["m"]), ("self0", m0)], D, pr)
    ref = R7.eval2_of(writers[w], 5).ll(m)
    ok = list(base["swap"]) == list(ref)
    w2 = [list(x) for x in writers]
    other = synth_writers(np.random.default_rng([SEED, 46]), 1, 10)[0]
    w2[w] = other[:5] + writers[w][5:]   # w の学習の単位（0〜4）だけを替える（評価の単位は同じ）
    a = R7.job_pair(R7.pair_job(w, v, 0, 1, picks, pp, [5], writers=w2))["5"]
    w3 = [list(x) for x in writers]
    w3[v] = other[:5] + writers[v][5:]
    b = R7.job_pair(R7.pair_job(w, v, 0, 1, picks, pp, [5], writers=w3))["5"]
    ok = ok and list(a["swap"]) == list(base["swap"]) and list(b["swap"]) != list(base["swap"])
    ok = ok and list(a["self2"]) != list(base["self2"])
    return dict(passed=bool(ok))


def p_agg():
    """手の例（書き手 6 人 × v 5 人・k = 5）: v の平均・−∞ の扱い（入れ替えの負け）・D・E・Dp の中央値。"""
    ws = list(range(6))
    picks = {w: "10000" for w in ws}
    picks[5] = INF
    selfp = {w: -1.0 + 0.01 * w for w in ws}
    pool03 = {w: -1.0 for w in ws}
    PAIR = {}
    for w in ws:
        for v in ws:
            if v != w:
                s = -1.0 + 1e-3 * v * v
                PAIR[(w, v)] = {"5": dict(swap=[(-np.inf if (w, v) == (4, 2) else s), None, s],
                                          self2=[s + 1e-3 * (v + 1), None, s])}
    C = R7.a_cell(ws, 5, picks, selfp, pool03, PAIR, np.random.default_rng(0))
    sw = {}
    for w in ws:
        vs = [v for v in ws if v != w]
        sw[w] = selfp[w] if w == 5 else (-np.inf if w == 4 else sum(-1.0 + 1e-3 * v * v for v in vs) / 5)
    med = lambda d: float(np.quantile(np.array(d), 0.5, method="inverted_cdf"))  # noqa: E731
    dp = [0.0 if w == 5 else (np.inf if w == 4 else sum(1e-3 * (v + 1) for v in ws if v != w) / 5) for w in ws]
    dp[4] = float(np.mean([PAIR[(4, v)]["5"]["self2"][0] - PAIR[(4, v)]["5"]["swap"][0] for v in ws if v != 4]))
    ok = abs(C["D"]["median"] - med([selfp[w] - sw[w] for w in ws])) < 1e-12
    ok = ok and abs(C["E"]["median"] - med([sw[w] - pool03[w] for w in ws])) < 1e-12
    ok = ok and abs(C["Dp"]["median"] - med(dp)) < 1e-12
    ok = ok and C["swap_neg_inf"] == 1 and C["D"]["n_pos_inf"] == 1 and C["E"]["n_neg_inf"] == 1
    return dict(passed=bool(ok))


def p_formr7():
    ok = R7.a_form(2e-3, 4e-3) == "担う" and R7.a_form(3e-3, 4e-3) == "担う"
    ok = ok and R7.a_form(1e-3, 4e-3) == "一部" and R7.a_form(0.0, 4e-3) == "担わない" and R7.a_form(-1e-3, 4e-3) == "担わない"
    ok = ok and R7.b_form(2e-3, 4e-3) == "残る" and R7.b_form(1e-3, 4e-3) == "縮む" and R7.b_form(0.0, 4e-3) == "消える"
    ok = ok and R7.panel_form({"5": "担う", "15": "担う"}) == "担う" and R7.panel_form({"5": "担う", "15": "一部"}) == "k で分かれる"
    return dict(passed=bool(ok))


FUNCS = {"P-HASH": p_hash, "P-NONFIRST": p_nonfirst, "P-REPLAYALL": p_replayall, "P-REPLAY03": p_replay03,
         "P-BPICK": p_bpick, "P-PAIRPOOL": p_pairpool, "P-SWAP": p_swap, "P-AGG": p_agg, "P-FORMR7": p_formr7}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    R7.MUT.clear()
    R7.MUT.update(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        S[n] = FUNCS[n]()
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(argv[0], "w", newline="\n"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
