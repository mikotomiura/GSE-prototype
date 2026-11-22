"""V1 の陽性対照（conditions.md V1・追記 1）。合成だけ。

使い方:
  python3 -I selftest.py <out.json> [--mutate wN] [--jobs 8] [--run-id ID] [--npz PATH（第 2 の帰無の P-HASH）]
どれかが赤なら終了コード 3。変異のときも全部の対照を回して結果を残す（名指しの対照は check_mutations.py が見る）。
P-XMACH は、この機械の記号の列の SHA-256 を出すだけ（両機の一致は check_xmach.py が見る）。
"""
import hashlib
import itertools
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import gen as GN  # noqa: E402

T995_199 = 2.600760216058516   # t_{0.995, 199}（scipy.stats.t.ppf で求めた値を書いた）
MUTS = ("w1", "w2", "w3", "w4", "w5", "w6")


def pkey(null, strand, shape, k, g, seed):
    """D3 の入れ替えの乱数の鍵。"""
    return [GN.SEED, null, strand, shape, k, g, seed]


def set_mut(m):
    EY.MUT.clear()
    GN.MUT.clear()
    if m:
        (GN.MUT if m == "w6" else EY.MUT).add(m)


# ---------------------------------------------------------------- P-HAND
def naive_tables(writers, P, H, k, nsym, m=26.0):
    """独立に書いた素朴な作り（ループ）。S は ml.pool_units（論文 3 と同じ部品）の単位から。"""
    pool = GN.ml.pool_units(writers, H)
    M = [[0] * nsym for _ in range(nsym)]
    for u in pool:
        for s in u["seqs"]:
            for a, b in zip(s[:-1], s[1:]):
                M[a][b] += 1
    S = [[(M[j][c] + 0.5) / (sum(M[j]) + 0.5 * nsym) for c in range(nsym)] for j in range(nsym)]
    tot = sum(map(sum, M))
    pi = [sum(M[j]) / tot for j in range(nsym)]

    def cnt(units):
        N = [[0] * nsym for _ in range(nsym)]
        for u in units:
            for s in u["seqs"]:
                for a, b in zip(s[:-1], s[1:]):
                    N[a][b] += 1
        return N

    def own(N):
        return [[(N[j][c] + m * S[j][c]) / (sum(N[j]) + m) for c in range(nsym)] for j in range(nsym)]

    PA, PB, NB = [], [], []
    for v in range(P):
        tr, te = GN.DT.split(len(writers[v]), k, H)
        PA.append(own(cnt([writers[v][i] for i in tr])))
        nb = cnt([writers[v][i] for i in te])
        NB.append(nb)
        PB.append(own(nb))
    return S, pi, PA, PB, NB, len(pool)


def naive_sims(S, pi, PA, PB, NB, nsym):
    P = len(PA)
    J = range(nsym)
    e1 = [[0.0] * P for _ in range(P)]
    e2 = [[0.0] * P for _ in range(P)]
    e3 = [[0.0] * P for _ in range(P)]
    u = {(j, c): pi[j] * S[j][c] for j in J for c in J}
    us = sum(u.values())
    for w in range(P):
        for v in range(P):
            n = sum(map(sum, NB[v]))
            e1[w][v] = sum(NB[v][j][c] * math.log(PA[w][j][c]) for j in J for c in J) / n
            a = {(j, c): math.log(PA[w][j][c]) - math.log(S[j][c]) for j in J for c in J}
            b = {(j, c): math.log(PB[v][j][c]) - math.log(S[j][c]) for j in J for c in J}
            ma = sum(u[x] * a[x] for x in u) / us
            mb = sum(u[x] * b[x] for x in u) / us
            va = sum(u[x] * (a[x] - ma) ** 2 for x in u) / us
            vb = sum(u[x] * (b[x] - mb) ** 2 for x in u) / us
            cv = sum(u[x] * (a[x] - ma) * (b[x] - mb) for x in u) / us
            e2[w][v] = 0.0 if va == 0 or vb == 0 else cv / math.sqrt(va * vb)
            tot = 0.0
            for j in J:
                p, q = PA[w][j], PB[v][j]
                mm = [(x + y) / 2 for x, y in zip(p, q)]
                js = 0.5 * sum(x * math.log(x / z) for x, z in zip(p, mm)) + 0.5 * sum(y * math.log(y / z) for y, z in zip(q, mm))
                tot += pi[j] * js
            e3[w][v] = -tot
    return dict(E1=np.array(e1), E2=np.array(e2), E3=np.array(e3))


def naive_w(s, sigma):
    """W_σ を定義どおりのループで（勝ち 2・同点 1・同点を先に判定）。"""
    P = len(s)
    W = 0
    for v in range(P):
        a = sigma[v]
        for w in range(P):
            if w == a:
                continue
            d = s[w][v] - s[a][v]
            if abs(d) <= 1e-12:
                W += 1
            elif d < 0:
                W += 2
    return W


def naive_p_exact(s):
    P = len(s)
    W = naive_w(s, list(range(P)))
    perms = list(itertools.permutations(range(P)))
    return sum(naive_w(s, p) >= W for p in perms) / len(perms), W


def tiny_writers():
    """3 人（パネル）+ 1 人（パネル外）・3 記号。各 3 単位（H = 1・k = 1）。書き手 0 と 1 の A（単位 1）は同じ数 → 同点。"""
    def U(*seqs):
        return dict(seqs=[np.array(s, dtype=np.int64) for s in seqs], pflag=[np.ones(len(s), bool) for s in seqs])
    w0 = [U([0, 1, 2, 0, 1]), U([0, 0, 1, 1, 2, 2, 0]), U([0, 0, 1, 2, 2, 0, 0, 1])]
    w1 = [U([2, 1, 0, 2]), U([0, 0, 1, 1, 2, 2, 0]), U([1, 1, 2, 0, 1, 1])]
    w2 = [U([1, 2, 1, 2, 1]), U([2, 2, 2, 1, 0], [1, 0]), U([2, 2, 1, 0, 2, 2, 2])]
    o0 = [U([0, 2, 1, 0, 2, 1, 0]), U([1, 0, 2])]
    return [w0, w1, w2, o0], 3


def fake_shape(shape):
    sh = GN.SY.SHAPES[shape]
    one = dict(seqs=[np.array([0, 1], dtype=np.int64)] * sh["nseq"], pflag=[np.ones(2, bool)] * sh["nseq"])
    return [[one] * (sh["Pu"] if i < sh["P"] else sh["Ou"]) for i in range(sh["P"] + sh["O"])], sh


def p_hand():
    R = {}
    # (a) 手で数えた s（同点 1 つ）: W = 9・AUC = (0.75, 0.5, 1)・全 6 置換の正確な p = 2/6
    s = np.array([[0.9, 0.2, 0.1], [0.5, 0.6, 0.3], [0.9, 0.7, 0.8]])
    c = EY.score_matrix(s)
    pe, W = EY.p_exact(c)
    rng = np.random.default_rng(pkey(0, 0, 0, 0, 0, 8000))
    ps, _ = EY.p_sampled(c, EY.draw_perms(rng, 3))
    R["hand_literal"] = dict(W=W, auc=EY.auc_rows(c).tolist(), p_exact=pe, p_sampled=ps,
                             ok=bool(W == 9 and np.allclose(EY.auc_rows(c), [0.75, 0.5, 1.0]) and pe == 2 / 6),
                             ok_sampled=bool(abs(ps - 2 / 6) <= 0.03))
    # (b) すべての s が等しい: W = 6・p = 1（全列挙と引き）
    s1 = np.full((3, 3), 0.25)
    c1 = EY.score_matrix(s1)
    pe1, W1 = EY.p_exact(c1)
    ps1, _ = EY.p_sampled(c1, EY.draw_perms(np.random.default_rng(pkey(0, 0, 0, 0, 0, 8000)), 3))
    R["hand_all_ties"] = dict(W=W1, p_exact=pe1, p_sampled=ps1, ok=bool(W1 == 6 and pe1 == 1.0),
                              ok_sampled=bool(abs(ps1 - 1.0) <= 0.03))
    # (c) 3 人・3 記号の表から: 3 案の s・AUC・W・正確な p を素朴な作りと照らす
    writers, P = tiny_writers()
    H, k = 1, 1
    UC = EY.count_writers(writers, 3)
    T = EY.cell_tables(UC, P, H, k, 0)
    S3 = EY.sims(T)
    S, pi, PA, PB, NB, npool = naive_tables(writers, P, H, k, 3)
    NS = naive_sims(S, pi, PA, PB, NB, 3)
    rows = {}
    ok_c = bool(np.allclose(T["S"], S, rtol=1e-12, atol=0))
    for e in EY.EYES:
        c = EY.score_matrix(S3[e])
        pe, W = EY.p_exact(c)
        npe, nW = naive_p_exact(NS[e])
        same_s = bool(np.allclose(S3[e], NS[e], rtol=1e-10, atol=1e-13))
        ps, _ = EY.p_sampled(c, EY.draw_perms(np.random.default_rng(pkey(0, 0, 0, 0, 0, 8000)), P))
        rows[e] = dict(W=W, W_naive=nW, p_exact=pe, p_naive=npe, p_sampled=ps, same_s=same_s,
                       ok=bool(same_s and W == nW and pe == npe), ok_sampled=bool(abs(ps - pe) <= 0.03))
        ok_c = ok_c and rows[e]["ok"]
    has_tie = bool(np.abs(S3["E1"][0] - S3["E1"][1]).max() <= 1e-12)
    R["tables"] = dict(rows=rows, has_tie=has_tie, ok=bool(ok_c and has_tie))
    # (d) S に入る単位の数（ml.pool_units）と、A・B の単位の番号（data.split と間のセル）
    cnt = {}
    for shape, want in (("coauthor", 17 * 15 + 26 * 5), ("cs1", 23 * 5 + 8 * 2)):
        fw, sh = fake_shape(shape)
        n_pool = len(GN.ml.pool_units(fw, sh["H"]))
        n_mine = sum(len(EY.non_eval_idx(len(u), sh["H"])) for u in fw)
        cnt[shape] = dict(pool=n_pool, mine=n_mine, want=want, ok=bool(n_pool == n_mine == want))
    idx = {}
    for (shape, n, H_, k_, g, want) in (
            ("coauthor", 20, 5, 5, 5, list(range(5, 10))), ("coauthor", 20, 5, 5, 10, list(range(0, 5))),
            ("cs1", 6, 1, 1, 1, [3]), ("cs1", 6, 1, 1, 4, [0])):
        got = EY.a_idx(n, k_, H_, g)
        idx["%s_k%d_g%d" % (shape, k_, g)] = dict(got=got, want=want, ok=got == want)
    for shape, n, H_, ks in (("coauthor", 20, 5, (1, 5, 15)), ("cs1", 6, 1, (1, 5))):
        for k_ in ks:
            tr, te = GN.DT.split(n, k_, H_)
            got = (EY.a_idx(n, k_, H_, 0), EY.b_idx(n, H_))
            idx["%s_k%d_g0" % (shape, k_)] = dict(ok=got == (tr, te))
    R["units"] = dict(pool=cnt, idx=idx, ok=all(v["ok"] for v in cnt.values()) and all(v["ok"] for v in idx.values()))
    det = R["hand_literal"]["ok"] and R["hand_all_ties"]["ok"] and R["tables"]["ok"] and R["units"]["ok"]
    smp = R["hand_literal"]["ok_sampled"] and R["hand_all_ties"]["ok_sampled"] and \
        all(v["ok_sampled"] for v in R["tables"]["rows"].values())
    return dict(detail=R, ok_deterministic=bool(det), ok_sampled=bool(smp), ok=bool(det and smp))


# ---------------------------------------------------------------- 複製の対照（並列）
def _init(m):
    set_mut(m)
    GN.assert_clean()


def null_rep(a):
    """第 1 の帰無・CoAuthor・用量の筋（λ = lam）の 1 複製の 3 案の p と W。P0 はパネルとして使う人数（P-UNIF は 8）。"""
    seed, lam, k, P0 = a
    w, P = GN.build_sens("dose", "coauthor", 3, seed, lam, GN.m0_first(3))[:2]
    P = P if P0 is None else P0
    UC = EY.count_writers(w, GN.NSYM)
    perms = EY.draw_perms(np.random.default_rng(pkey(1, 0, 0, k, 0, seed)), P)
    T = EY.cell_tables(UC, P, 5, k, 0)
    S3 = EY.sims(T)
    out = {}
    for e in EY.EYES:
        c = EY.score_matrix(S3[e])
        p, W = EY.p_sampled(c, perms)
        out[e] = dict(p=p, T=EY.t_of_w(W, P))
    return out


def p_null(ex):
    reps = list(ex.map(null_rep, [(s, 0.0, 5, None) for s in range(5000, 5200)], chunksize=4))
    R = {}
    for e in EY.EYES:
        n_rej = sum(r[e]["p"] <= 0.05 for r in reps)
        Ts = np.array([r[e]["T"] for r in reps])
        m, sd = float(Ts.mean()), float(Ts.std(ddof=1))
        lo, hi = m - T995_199 * sd / math.sqrt(200), m + T995_199 * sd / math.sqrt(200)
        R[e] = dict(n_rej=int(n_rej), T_mean=m, ci99=[lo, hi], ok_count=bool(n_rej <= 19), ok_mean=bool(lo <= 0.5 <= hi))
    return dict(detail=R, ok=all(v["ok_count"] and v["ok_mean"] for v in R.values()))


def p_unif(ex):
    reps = list(ex.map(null_rep, [(s, 0.0, 5, 8) for s in range(5200, 5400)], chunksize=4))
    R = {}
    for e in EY.EYES:
        R[e] = {}
        for a in (0.05, 0.1):
            frac = sum(r[e]["p"] <= a for r in reps) / 200
            lim = a + 2 * math.sqrt(a * (1 - a) / 200)
            R[e][str(a)] = dict(frac=frac, limit=lim, ok=bool(frac <= lim))
    return dict(detail=R, ok=all(x["ok"] for v in R.values() for x in v.values()))


def p_pos(ex):
    reps = list(ex.map(null_rep, [(s, 1.0, 15, None) for s in range(6000, 6020)], chunksize=1))
    R = {e: dict(n_rej=int(sum(r[e]["p"] <= 0.05 for r in reps))) for e in EY.EYES}
    for e in R:
        R[e]["ok"] = bool(R[e]["n_rej"] >= 18)
    return dict(detail=R, ok=all(v["ok"] for v in R.values()))


def p_stat():
    """漂い ρ = 0.9・CoAuthor・種 6100〜6139 の先頭の書き手（40 人）。書き手の間の E の偏差の分散の全セルの平均の、単位 1 と単位 20 の比。"""
    m0 = GN.m0_first(3)
    lam = GN.lam_drift(0.9)
    E1, E20 = [], []
    for s in range(6100, 6140):
        _, _, uc = GN.build_new("drift", "coauthor", s, m0, rho=0.9, n_writers=1, seqs=False)
        Cs = uc[0]
        E1.append((Cs[0] - m0["C"]) / lam)
        E20.append((Cs[19] - m0["C"]) / lam)
    v1 = float(np.var(np.array(E1), axis=0, ddof=1).mean())
    v20 = float(np.var(np.array(E20), axis=0, ddof=1).mean())
    r = v1 / v20
    return dict(detail=dict(var_unit1=v1, var_unit20=v20, ratio=r), ok=bool(0.8 <= r <= 1.25))


def p_xmach():
    w, _ = GN.build_sens("dose", "coauthor", 3, 1000, 0.0, GN.m0_first(3))[:2]
    h = hashlib.sha256()
    for units in w:
        for u in units:
            for s in u["seqs"]:
                h.update(np.ascontiguousarray(s, dtype=np.int64).tobytes())
    import numpy
    return dict(sha256=h.hexdigest(), python=platform.python_version(), numpy=numpy.__version__,
                machine=platform.platform())


def main():
    argv = sys.argv[1:]
    opt = {}
    for key in ("--mutate", "--jobs", "--run-id", "--npz"):
        if key in argv:
            i = argv.index(key)
            opt[key] = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]
    out = argv[0]
    m = opt.get("--mutate")
    if m is not None and m not in MUTS:
        sys.exit("変異の名が違う: %s" % m)
    jobs = int(opt.get("--jobs", "8"))
    t0 = time.time()
    set_mut(m)
    GN.assert_clean()
    import run_eye
    R = dict(run_id=opt.get("--run-id"), mutate=m, seed=GN.SEED, code_hash=run_eye.code_hash())
    R["P-HASH"] = dict(hashes=GN.check_hashes(second="--npz" in opt, npz=opt.get("--npz")), ok=True)
    R["P-HAND"] = p_hand()
    R["P-STAT"] = p_stat()
    with ProcessPoolExecutor(jobs, initializer=_init, initargs=(m,)) as ex:
        R["P-NULL"] = p_null(ex)
        R["P-UNIF"] = p_unif(ex)
        R["P-POS"] = p_pos(ex)
    R["P-XMACH"] = p_xmach()
    names = ("P-HASH", "P-HAND", "P-STAT", "P-NULL", "P-UNIF", "P-POS")
    R["red"] = [n for n in names if not R[n]["ok"]]
    R["seconds"] = time.time() - t0
    json.dump(R, open(out, "w"), indent=1, ensure_ascii=False)
    print("%s: 赤 %s（%.0f 秒）" % (m or "変異なし", R["red"] or "なし", R["seconds"]), flush=True)
    sys.exit(3 if R["red"] else 0)


if __name__ == "__main__":
    main()
