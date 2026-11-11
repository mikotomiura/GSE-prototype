"""門（conditions.md V1・合成だけ）。P-HASH は pinned4 の読み込みで止める。

使い方: python3 -I selftest.py <out.json> [--mutate s1..s7] [--run-id ID]
返り値: 0 = すべて通った・3 = 通らない門がある。
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ab as AB  # noqa: E402
import compute as CP  # noqa: E402
import pinned4  # noqa: E402
from pinned4 import H, ml  # noqa: E402

NAMES = ["P-HASH", "P-HALF", "P-SPLITSEL", "P-HAND", "P-FLOOR", "P-SCALE", "P-POOLSAME", "P-INFSWAP", "P-ALPHAW", "P-R1BETA",
         "P-LOO", "P-REFW", "P-TIES"]
SEED = pinned4.SEED
SN = AB.SN


def fake_results(rng, n_w=8, ks=("5",), finite_neg=False):
    """合成の書き手の値（全記号と押下）。finite_neg は有限の τ の 本人 − 共通 をすべて負にする。τ = ∞ は共通と同じ値。"""
    R = {}
    for w in range(n_w):
        pool = {s: [float(-1.2 + 0.01 * rng.normal()), float(-1.3 + 0.01 * rng.normal())] for s in SN}
        k = {}
        for kk in ks:
            def val(s, t):
                if t == ml.INF:
                    return list(pool[s])
                d = -abs(float(rng.normal())) * 1e-3 - 1e-6 if finite_neg else float(1e-3 * rng.normal())
                return [pool[s][0] + d, pool[s][1] + d]
            k[kk] = dict(r1=[float(-1.25 + 0.01 * rng.normal()), -1.35], self={s: {t: val(s, t) for t in ml.TAU_KEYS} for s in SN})
        R[w] = dict(n=25, em=dict(pool=pool, k=k))
    return R


def p_hash():
    return dict(passed=True, hashes=pinned4.hashes())


def p_half():
    ok = True
    for n in (17, 9, 23):
        a = AB.split_pairs(n, np.random.default_rng([SEED, 1, n]), 200)
        b = AB.split_pairs(n, np.random.default_rng([SEED, 1, n]), 200)
        for (X, Y), (X2, Y2) in zip(a, b):
            ok = ok and len(np.intersect1d(X, Y)) == 0 and sorted(np.concatenate([X, Y]).tolist()) == list(range(n))
            ok = ok and len(X) == n // 2 and len(Y) == n - n // 2 and (X == X2).all() and (Y == Y2).all()
    return dict(passed=bool(ok))


def p_splitsel():
    """R の値を書き換えても c_S が変わらない（乱数 200 回）。c_S が ml.select_joint / select_other の w を除かない形と同じ。"""
    rng = np.random.default_rng([SEED, 2])
    flips = diff = 0
    for _ in range(200):
        V = rng.normal(size=(9, 12))
        X, Y = np.arange(4), np.arange(4, 9)
        c0 = AB.a_pairs(V, {"x": V}, [(X, Y)])[0][0]
        vals = {v: {c: float(V[v, c]) for c in range(12)} for v in X}
        diff += c0 != ml.select_joint(vals, None, list(range(12)))
        diff += c0 != ml.select_other(vals, None, list(range(12)))
        V2 = V.copy()
        V2[Y] = rng.normal(size=(5, 12)) * 10
        flips += c0 != AB.a_pairs(V2, {"x": V2}, [(X, Y)])[0][0]
    return dict(passed=bool(flips == 0 and diff == 0), flips=int(flips), diff=int(diff))


def p_hand():
    """6 人・3 候補の手の例。向き 1: S = {0,1,2} の中央値 [1,2,0] → c1、R = {3,4,5} の c1 は [0,0,0] → h = 0、
    R の中央値 [5,0,1] → c0 → i = 5、o = 5。向き 2: S = {3,4,5} → c0、R = {0,1,2} の c0 は [1,1,1] → h = 1、
    R の中央値 → c1 → i = 2、o = 1。"""
    V = np.array([[1, 2, 0], [1, 3, 0], [1, 1, 0], [5, 0, 0], [5, 0, 1], [0, 0, 2]], dtype=float)
    res = AB.a_pairs(V, {"x": V}, [(np.array([0, 1, 2]), np.array([3, 4, 5]))])
    got = [(r[1]["x"], r[2]["x"], r[2]["x"] - r[1]["x"]) for r in res]
    want = [(0.0, 5.0, 5.0), (1.0, 2.0, 1.0)]
    ok = all(abs(a - b) < 1e-12 for g, w in zip(got, want) for a, b in zip(g, w))
    S = AB.a_summary(res, ["c0", "c1", "c2"])
    ok = ok and abs(S["x"]["optimism"]["median"] - 3.0) < 1e-12 and S["x"]["honest_pos_share"] == 0.5
    return dict(passed=bool(ok), got=got)


def p_floor():
    """有限の τ の値がすべて負なら、τ 他人の同じ半分の値 i は 0 ちょうど（∞ が選ばれる）。"""
    R = fake_results(np.random.default_rng([SEED, 3]), n_w=9, finite_neg=True)
    ws = sorted(R)
    tc, V, reps = AB.tau_mats(R, ws, 5, "ar3")
    res = AB.a_pairs(V, reps, AB.split_pairs(9, np.random.default_rng([SEED, 4]), 50))
    ok = all(r[2]["self_minus_pool"] == 0.0 for r in res)
    return dict(passed=bool(ok), min_i=float(min(r[2]["self_minus_pool"] for r in res)))


def p_scale():
    ok = True
    for kind, K in ml.STRUCTS:
        base = H.base_prior(kind, K)
        p1 = CP.prior_alpha(kind, K, 1.0)
        p3 = CP.prior_alpha(kind, K, 0.3)
        ok = ok and set(p1) == set(base) and all((p1[k] == base[k]).all() for k in base)
        ok = ok and all(np.array_equal(p3[k], base[k] * 0.3) for k in base)
    return dict(passed=bool(ok))


def unit_of(seq):
    return dict(start=0, seqs=[seq], pflag=[np.ones(len(seq), dtype=bool)], probes=[], probes_all=[])


def p_poolsame():
    """合成の書き手 6 人で、α = 1 の当て直しが mode の fit_pool_full → fit_pool_excl と同じ母数・同じ評価（ビットまで）。"""
    rng = np.random.default_rng([SEED, 5])
    A = 0.95 * np.eye(2) + 0.05 * rng.dirichlet(np.ones(2), 2)
    m = dict(kind="ar", pi=np.ones(2) / 2, A=A / A.sum(1, keepdims=True), H=rng.dirichlet(np.ones(H.NSYM), 2),
             C=np.stack([rng.dirichlet(np.full(H.NSYM, 0.3), H.NSYM) for _ in range(2)]))
    writers = [[unit_of(s) for s in H.sample(m, [120] * 7, rng)] for _ in range(6)]
    ok, n = True, 0
    for s in [("hmm", 3), ("ar", 1), ("ar", 2)]:
        mine = CP.job_full(dict(ds="coauthor", s=s, alpha=1.0, seed=SEED, writers=writers))
        theirs = ml.fit_pool_full(dict(ds="coauthor", si=ml.SEQ_NO[s], seed=SEED, writers=writers))[0]
        ok = ok and all(np.array_equal(mine[k], theirs[k]) for k in H.keys_of(s[0]))
        for w in (0, 3):
            a = CP.job_excl(dict(ds="coauthor", w=w, start=mine, alpha=1.0, writers=writers, keep_model=True))
            b, _, _ = ml.fit_pool_excl(dict(ds="coauthor", w=w, start=theirs, writers=writers))
            ok = ok and all(np.array_equal(a["m"][k], b[k]) for k in H.keys_of(s[0]))
            ok = ok and CP.same_bits(a["ll"], CP.eval_of(writers[w], 5).ll(b))
            n += 1
    return dict(passed=bool(ok), compared=n)


def p_infswap():
    """B1 の 2 段で τ = ∞ が選ばれた書き手の 本人 − 共通(α*) がちょうど 0、∞ の候補の値が pool(α*) − r1。"""
    rng = np.random.default_rng([SEED, 6])
    R = fake_results(rng, n_w=8, finite_neg=True)
    ws = sorted(R)
    for w in ws:  # 有限の τ を r1 に対しても悪くする（∞ が選ばれる）
        for s in SN:
            for t in ml.TAU_KEYS:
                if t != ml.INF:
                    R[w]["em"]["k"]["5"]["self"][s][t][0] -= 1.0
    PV = {w: {n: {a: [R[w]["em"]["pool"][n][0] + (2e-3 if a == "0.3" else 0.0), None] for a in AB.ALPHAS} for n in SN} for w in ws}
    ast = {n: AB.alpha_star(PV, ws, n) for n in SN}
    ref = AB.Ref(R, 5, PV=PV, astar=ast)
    out, pk, dp = AB.joint_rows(ref, ws, np.random.default_rng([SEED, 7]))
    ok = all(c[1] == ml.INF for c in pk.values()) and all(x == 0.0 for x in dp)
    ok = ok and all(ast[n][w] == "0.3" for n in SN for w in ws)
    ok = ok and all(ref.me(v, n, ml.INF, 0) - ref.r1(v, 0) == PV[v][n]["0.3"][0] - R[v]["em"]["k"]["5"]["r1"][0]
                    for v in ws for n in SN)
    return dict(passed=bool(ok), max_abs_dp=float(max(abs(x) for x in dp)))


def p_alphaw():
    rng = np.random.default_rng([SEED, 8])
    flips = 0
    ws = list(range(8))
    for _ in range(200):
        PV = {v: {"ar3": {a: [float(rng.normal()), None] for a in AB.ALPHAS}} for v in ws}
        RV = {v: {"5": {b: [float(rng.normal()), None] for b in AB.BETAS}} for v in ws}
        a0, b0 = AB.alpha_star(PV, ws, "ar3")[0], AB.beta_star(RV, ws, 5)[0]
        PV[0] = {"ar3": {a: [float(rng.normal() * 10), None] for a in AB.ALPHAS}}
        RV[0] = {"5": {b: [float(rng.normal() * 10), None] for b in AB.BETAS}}
        flips += (a0 != AB.alpha_star(PV, ws, "ar3")[0]) + (b0 != AB.beta_star(RV, ws, 5)[0])
    return dict(passed=bool(flips == 0), flips=int(flips))


def p_r1beta():
    rng = np.random.default_rng([SEED, 9])
    seqs = [rng.integers(0, H.NSYM, 300) for _ in range(4)]
    _, h0, T0 = H.r0_r1(seqs)
    h1, T1 = CP.r1_beta(seqs, 0.5)
    ok = np.array_equal(h0, h1) and np.array_equal(T0, T1)
    h, T = CP.r1_beta([np.array([0, 1, 1])], 0.1)
    d = 1.1 + 25 * 0.1
    ok = ok and abs(h[0] - 1.1 / d) < 1e-15 and abs(h[2] - 0.1 / d) < 1e-15
    ok = ok and abs(T[0, 1] - 1.1 / d) < 1e-15 and abs(T[1, 1] - 1.1 / d) < 1e-15 and abs(T[2, 5] - 1 / 26) < 1e-15
    return dict(passed=bool(ok))


def p_loo():
    """行列（joint_mats・tau_mats）から w を除く選びで作った中央値が、mode の select_joint / select_other と row_deltas の
    中央値と同じ（乱数 30 回・レビュー MEDIUM 1。実データでは P-CURRENT が mode の summary とビットまで照らす）。"""
    rng = np.random.default_rng([SEED, 10])
    bad = 0
    for _ in range(30):
        R = fake_results(rng, n_w=9)
        ws = sorted(R)
        jc, sel, reps = AB.joint_mats(R, ws, 5)
        jv = ml.joint_values(R, ws, 5)
        pk = {w: ml.select_joint(jv, w, ml.joint_cands()) for w in ws}
        bad += AB.loo_median(sel, reps["self_minus_pool"]) != ml.q(ml.row_deltas(R, ws, 5, pk, 0, "pool_same"))["median"]
        for name in ("hmm3", "ar3"):
            tc, V, rp = AB.tau_mats(R, ws, 5, name)
            ev = ml.em_values(R, ws, 5, next(s for s in ml.STRUCTS if ml.sname(s) == name))
            pt = {w: (name, ml.select_other(ev, w, ml.tau_cands())) for w in ws}
            bad += AB.loo_median(V, rp["self_minus_pool"]) != ml.q(ml.row_deltas(R, ws, 5, pt, 0, "pool_same"))["median"]
    return dict(passed=bool(bad == 0), mismatches=int(bad))


def p_refw():
    """α*・β* が書き手で分かれる合成（半数ずつ別の値が良い）で、B1・B2 の 2 段の選びと差が、w の α*・β* で手で組んだ値と同じ
    （乱数 100 回・レビュー MEDIUM 2）。"""
    rng = np.random.default_rng([SEED, 11])
    jc = ml.joint_cands()
    bad, split_ok = 0, True
    for _ in range(100):
        R = fake_results(rng, n_w=8)
        ws = sorted(R)
        d = 1e-3 * (1 + rng.random())
        PV = {w: {n: {a: [R[w]["em"]["pool"][n][0] + (d if (a == "0.3" and w < 4) or (a == "0.1" and w >= 4) else 0.0), None]
                      for a in AB.ALPHAS} for n in SN} for w in ws}
        RV = {w: {"5": {b: [R[w]["em"]["k"]["5"]["r1"][0] + (d if (b == "0.1" and w < 4) or (b == "1" and w >= 4) else 0.0), None]
                        for b in AB.BETAS}} for w in ws}
        ast = {n: AB.alpha_star(PV, ws, n) for n in SN}
        bst = AB.beta_star(RV, ws, 5)
        split_ok = split_ok and {ast["ar3"][w] for w in ws} == {"0.1", "0.3"} and {bst[w] for w in ws} == {"0.1", "1"}
        for case, ref in (("a", AB.Ref(R, 5, PV=PV, astar=ast)), ("b", AB.Ref(R, 5, RV=RV, bstar=bst))):
            _, pk, dp = AB.joint_rows(ref, ws, np.random.default_rng(0))
            for i, w in enumerate(ws):
                def me(v, n, t):
                    if case == "a" and t == ml.INF:
                        return PV[v][n][ast[n][w]][0]
                    return R[v]["em"]["k"]["5"]["self"][n][t][0]
                r1 = lambda v: RV[v]["5"][bst[w]][0] if case == "b" else R[v]["em"]["k"]["5"]["r1"][0]  # noqa: E731
                pool = lambda v, n: PV[v][n][ast[n][w]][0] if case == "a" else R[v]["em"]["pool"][n][0]  # noqa: E731
                vals = {v: {(n, t): me(v, n, t) - r1(v) for n, t in jc} for v in ws}
                c = ml.select_joint(vals, w, jc)
                bad += pk[w] != c or dp[i] != me(w, *c) - pool(w, c[0])
    return dict(passed=bool(bad == 0 and split_ok), mismatches=int(bad), split_ok=bool(split_ok))


def p_ties():
    """同点の規則: 全員が同じ値なら α* = 1・β* = 0.5・2 段は joint_cands の先頭（τ = ∞）・τ 他人は ∞。"""
    ws = list(range(7))
    PV = {v: {"ar3": {a: [0.0, None] for a in AB.ALPHAS}} for v in ws}
    RV = {v: {"5": {b: [0.0, None] for b in AB.BETAS}} for v in ws}
    jc = ml.joint_cands()
    flat = {v: {c: 0.0 for c in jc} for v in ws}
    ok = set(AB.alpha_star(PV, ws, "ar3").values()) == {"1"} and set(AB.beta_star(RV, ws, 5).values()) == {"0.5"}
    ok = ok and AB.pick(flat, ws, jc) == jc[0] and jc[0][1] == ml.INF
    ok = ok and AB.pick({v: {t: 0.0 for t in ml.tau_cands()} for v in ws}, ws, ml.tau_cands()) == ml.INF
    V = np.zeros((7, len(jc)))
    ok = ok and AB.argbest(V, np.arange(7)) == 0
    return dict(passed=bool(ok))


FUNCS = {"P-HASH": p_hash, "P-HALF": p_half, "P-SPLITSEL": p_splitsel, "P-HAND": p_hand, "P-FLOOR": p_floor,
         "P-SCALE": p_scale, "P-POOLSAME": p_poolsame, "P-INFSWAP": p_infswap, "P-ALPHAW": p_alphaw, "P-R1BETA": p_r1beta,
         "P-LOO": p_loo, "P-REFW": p_refw, "P-TIES": p_ties}


def main():
    argv = sys.argv[1:]
    mut, run_id = [], None
    while "--mutate" in argv:
        i = argv.index("--mutate"); mut.append(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if "--run-id" in argv:
        i = argv.index("--run-id"); run_id = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    CP.set_mut(mut)
    S = dict(run_id=run_id, mutate=mut)
    for n in NAMES:
        S[n] = FUNCS[n]()
        print(n, S[n]["passed"], flush=True)
    S["passed"] = all(S[n]["passed"] for n in NAMES)
    json.dump(S, open(argv[0], "w"), indent=1, default=str)
    return 0 if S["passed"] else 3


if __name__ == "__main__":
    sys.exit(main())
