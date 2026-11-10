"""感度の合成の真の生成（conditions.md D1・D2）。実データは使わない。

- 共通の真の母数 m0（AR(1)-HMM・K = 3 または 5）
- 書き手ごとの真の母数 m_w: C の行を C0 と D_w（Dirichlet(2 · C0 の行)）で混ぜる（λ_w）
- 大きさの物差し g_w = 評価の系列での m_w − m0 の 1 記号あたり対数尤度
- λ の較正（二分法）
- 形（CoAuthor・CS1）ごとの単位の生成（共通の乱数で段を揃える）

当てはめと選びのコードは tau-extend の scripts/ を写さずに読み込む（pinned.py）。
"""
import bisect
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pinned import H, ml  # noqa: E402

NSYM = H.NSYM
RHO = {3: (0.6, 0.8, 0.9), 5: (0.5, 0.65, 0.8, 0.9, 0.95)}
A_DIAG = 0.97
D_CONC = 2.0
SHAPES = {
    "coauthor": dict(i=0, ds="coauthor", H=5, P=17, Pu=20, O=26, Ou=5, nseq=1, L=(600, 700), ks=[1, 5, 15]),
    "cs1": dict(i=1, ds="cs1", H=1, P=23, Pu=6, O=8, Ou=3, nseq=2, L=(5000, 8000), ks=[1, 5]),
}
CAL_WRITERS, CAL_LEN, CAL_ITERS, CAL_TOL = 40, 20000, 40, 0.10
MUT = set()  # v1: D_w を全員で 1 つ・v2: g を w を除く共通の当てはめで測る・v4: 分布の筋の印を 1 つずらす・v6: D_w の濃度を一様にする


# ---------------------------------------------------------------- 真の母数
def make_m0(K, seed):
    rng = np.random.default_rng([seed + 2, K])
    A = np.full((K, K), (1 - A_DIAG) / (K - 1))
    np.fill_diagonal(A, A_DIAG)
    Hh = rng.dirichlet(np.ones(NSYM), K)
    C = np.empty((K, NSYM, NSYM))
    for k in range(K):
        for j in range(NSYM):
            qv = rng.dirichlet(np.ones(NSYM))
            C[k, j] = (1 - RHO[K][k]) * qv
            C[k, j, j] += RHO[K][k]
    return dict(kind="ar", pi=np.full(K, 1.0 / K), A=A, H=Hh, C=C)


def draw_D(m0, rng):
    """D_w[k, j, :] ~ Dirichlet(2 · C0[k, j, :])（期待値が C0 の行）。"""
    K = len(m0["pi"])
    D = np.empty_like(m0["C"])
    for k in range(K):
        for j in range(NSYM):
            alpha = np.full(NSYM, D_CONC / NSYM) if "v6" in MUT else D_CONC * m0["C"][k, j]
            D[k, j] = rng.dirichlet(alpha)
    return D


def writer_model(m0, D, lam):
    m = dict(kind="ar", pi=m0["pi"].copy(), A=m0["A"].copy(), H=m0["H"].copy())
    m["C"] = m0["C"].copy() if lam == 0 else (1 - lam) * m0["C"] + lam * D
    return m


# ---------------------------------------------------------------- 系列（逆関数法・一様乱数は呼ぶ側が渡す）
class Sampler:
    def __init__(self, m):
        self.cpi = np.cumsum(m["pi"]).tolist()
        self.cA = [np.cumsum(r).tolist() for r in m["A"]]
        self.cH = [np.cumsum(r).tolist() for r in m["H"]]
        self.cC = [[np.cumsum(r).tolist() for r in Ck] for Ck in m["C"]]
        self.K = len(m["pi"])

    @staticmethod
    def _pick(c, u):
        i = bisect.bisect_right(c, u)
        return i if i < len(c) else len(c) - 1

    def seq(self, u):
        """u: (L, 2) の一様乱数。頭は π と H、以後は A[z_{t-1}] と C[z_t, s_{t-1}]（hmm2.sample と同じ意味）。"""
        L = len(u)
        out = np.empty(L, dtype=np.int64)
        uu = u.tolist()
        z = self._pick(self.cpi, uu[0][0])
        s = self._pick(self.cH[z], uu[0][1])
        out[0] = s
        cA, cC, pk = self.cA, self.cC, self._pick
        for t in range(1, L):
            z = pk(cA[z], uu[t][0])
            s = pk(cC[z][s], uu[t][1])
            out[t] = s
        return out


def gain(m_w, m0, seqs, ref=None):
    """g_w = 評価の系列での m_w − m0 の 1 記号あたりの対数尤度（ml.Eval と同じ量）。v2 は m0 の代わりに ref（当てはめ）。"""
    ev = ml.Eval(list(seqs), [np.ones(len(s), dtype=bool) for s in seqs])
    base = ref if ("v2" in MUT and ref is not None) else m0
    return ev.ll(m_w)[0] - ev.ll(base)[0]


# ---------------------------------------------------------------- λ の較正
def calibrate(m0, target, seed, n_w=CAL_WRITERS, L=CAL_LEN, iters=CAL_ITERS):
    """g_cal(λ) = 較正の書き手の g_w の中央値。λ ∈ [0, 1] の二分法。返り値: dict(lam, g, ok, g_hi)。"""
    K = len(m0["pi"])
    if target == 0:
        return dict(lam=0.0, g=0.0, ok=True, target=0.0)
    rng = np.random.default_rng([seed + 3, K])
    Ds = [draw_D(m0, rng) for _ in range(n_w)]
    rng_u = np.random.default_rng([seed + 3, K, 1])
    Us = [rng_u.random((L, 2)) for _ in range(n_w)]

    def g_of(lam):
        gs = []
        for D, u in zip(Ds, Us):
            mw = writer_model(m0, D, lam)
            gs.append(gain(mw, m0, [Sampler(mw).seq(u)]))
        return float(np.median(gs))

    g_hi = g_of(1.0)
    if g_hi < target:
        return dict(lam=None, g=g_hi, ok=False, target=target, g_hi=g_hi)
    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if g_of(mid) < target:
            lo = mid
        else:
            hi = mid
    lam = 0.5 * (lo + hi)
    g = g_of(lam)
    return dict(lam=lam, g=g, ok=abs(g / target - 1) <= CAL_TOL, target=target, g_hi=g_hi)


# ---------------------------------------------------------------- 形ごとの書き手
def lam_rule(strand, lam):
    """書き手の通し番号 → λ_w。dose・struct は全員 lam、dist は 4 で割った余りが 0 だけ lam（v4 はずらす）。"""
    if strand != "dist":
        return lambda i: lam
    off = 1 if "v4" in MUT else 0
    return lambda i: lam if (i + off) % 4 == 0 else 0.0


def build(shape, K, rep_seed, lam_of, m0, seed):
    """返り値: writers（ml の単位の形のリスト）・models（真の m_w）・lams・P（パネルは 0..P-1）。
    D_w と長さは [seed + 1, K, 形, 種]、系列の一様乱数は [seed + 4, K, 形, 種]（段に依らない）。"""
    sh = SHAPES[shape]
    N = sh["P"] + sh["O"]
    rng1 = np.random.default_rng([seed + 1, K, sh["i"], rep_seed])
    rng4 = np.random.default_rng([seed + 4, K, sh["i"], rep_seed])
    writers, models, lams = [], [], []
    D0 = None
    for i in range(N):
        D = draw_D(m0, rng1)
        if "v1" in MUT:
            D0 = D if D0 is None else D0
            D = D0
        nu = sh["Pu"] if i < sh["P"] else sh["Ou"]
        lens = [rng1.integers(sh["L"][0], sh["L"][1] + 1, size=sh["nseq"]).tolist() for _ in range(nu)]
        lam = lam_of(i)
        mw = writer_model(m0, D, lam)
        smp = Sampler(mw)
        units = []
        for ls in lens:
            seqs = [smp.seq(rng4.random((L, 2))) for L in ls]
            units.append(dict(seqs=seqs, pflag=[np.ones(len(s), dtype=bool) for s in seqs]))
        writers.append(units)
        models.append(mw)
        lams.append(lam)
    return writers, models, lams, sh["P"]
