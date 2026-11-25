"""本人ごとの重みを見る目（conditions.md D1〜D3・D6 の記述の量）。合成の値だけを扱う。

- 表: 系列ごとの隣り合う記号の組の数 N[j, c]（系列をまたがない）。共有の表 S は全員の ml.pool_units の単位から 1 つ。
- 本人の表: (N + m · S) / (行の和 + m)、m = 26。
- 3 案の近さ s[w, v]（書き手 v の B に対する書き手 w の A の近さ）: E1 交差尤度・E2 ずれの相関・E3 行ごとの JS。
- 整数の W（勝ち 2・同点 1）と、B の名札の入れ替えの p（引きの経路と全列挙の経路が同じ関数 w_of を呼ぶ）。

変異（V1）: w1 B に本人の A の単位を入れる・w2 各置換で σ(v) = v・w3 共有の表を書き手ごとに w を除いて作る・
w4 同点を 1 と数える（勝ちと同じ 2 点）・w5 間を空けたセルで A を空けずに取る。w6 は gen.py（空回しを外す）。
"""
import itertools

import numpy as np

MUT = set()
M_SHARE = 26.0
TIE = 1e-12
EYES = ("E1", "E2", "E3")
N_PERM = 2000


# ---------------------------------------------------------------- 記録の分け方（D1）
def a_idx(n, k, H, g=0):
    """A の単位の番号: B = 後ろの H 単位、A = B の前に g 単位を空けた k 単位（g = 0 は data.split の学習と同じ）。"""
    gg = 0 if "w5" in MUT else g
    lo = n - H - gg - k
    if lo < 0:
        raise ValueError("A の単位が足りない（n=%d k=%d H=%d g=%d）" % (n, k, H, g))
    return list(range(lo, n - H - gg))


def b_idx(n, H):
    return list(range(n - H, n))


# ---------------------------------------------------------------- 数え（D1）
def seq_counts(s, nsym):
    s = np.asarray(s, dtype=np.int64)
    if len(s) < 2:
        return np.zeros((nsym, nsym), dtype=np.int64)
    return np.bincount(s[:-1] * nsym + s[1:], minlength=nsym * nsym).reshape(nsym, nsym)


def unit_counts(unit, nsym):
    """1 単位の遷移の数（単位の中の系列の境目をまたがない）。"""
    out = np.zeros((nsym, nsym), dtype=np.int64)
    for s in unit["seqs"]:
        out += seq_counts(s, nsym)
    return out


def count_writers(writers, nsym):
    return [[unit_counts(u, nsym) for u in units] for units in writers]


def non_eval_idx(n, H):
    """ml.non_eval と同じ: 単位が H + 1 以上ある書き手は後ろの H 単位を落とす。"""
    return list(range(n - H)) if n >= H + 1 else list(range(n))


def shared_counts(UC, H, exclude=None):
    """ml.pool_units(writers, H, exclude) の単位の数の和 M。"""
    nsym = UC[0][0].shape[0]
    M = np.zeros((nsym, nsym), dtype=np.int64)
    for j, uc in enumerate(UC):
        if j == exclude:
            continue
        for i in non_eval_idx(len(uc), H):
            M += uc[i]
    return M


def shared_table(M):
    S = M + 0.5
    return S / S.sum(1, keepdims=True)


def occupancy(M):
    r = M.sum(1).astype(float)
    return r / r.sum()


def own_table(N, S, m=M_SHARE):
    return (N + m * S) / (N.sum(1, keepdims=True) + m)


# ---------------------------------------------------------------- 1 複製・1 セルの表
def cell_tables(UC, P, H, k, g=0):
    """返り値: dict(NA, NB（P×J×J の数）, S, pi, PA, PB（本人の表）, SA, SB（w3 のときの書き手ごとの共有の表）)。"""
    M = shared_counts(UC, H)
    S = shared_table(M)
    pi = occupancy(M)
    NA, NB = [], []
    for v in range(P):
        n = len(UC[v])
        a = a_idx(n, k, H, g)
        b = b_idx(n, H)
        if "w1" in MUT:
            b = b + a
        NA.append(sum(UC[v][i] for i in a))
        NB.append(sum(UC[v][i] for i in b))
    NA, NB = np.array(NA), np.array(NB)
    if "w3" in MUT:
        Ss = [shared_table(shared_counts(UC, H, exclude=w)) for w in range(P)]
    else:
        Ss = [S] * P
    PA = np.array([own_table(NA[w], Ss[w]) for w in range(P)])
    PB = np.array([own_table(NB[v], Ss[v]) for v in range(P)])
    return dict(NA=NA, NB=NB, S=S, pi=pi, PA=PA, PB=PB, Ss=Ss)


# ---------------------------------------------------------------- 量の揃え（v2 の D1・判断 49）
def thin(N, n, rng):
    """N（J×J の数）から n 個の遷移を重複なしで間引く（多変量の超幾何）。総数が n なら写しを返す（乱数を使わない）。"""
    flat = N.ravel()
    if int(flat.sum()) == n:
        return N.copy()
    return rng.multivariate_hypergeometric(flat, n).reshape(N.shape)


def equalize(T, key):
    """パネルの書き手の NA_v と NB_v を、それぞれパネルの最小の総数まで間引き、本人の表を作り直す。S・π・Ss は元のまま。
    乱数は書き手・側ごとに [*key, 側（A 0・B 1）, v]。key は [SEED + 93, 帰無, 筋, 形, k, g, 種]。w7 は揃えを外す。"""
    if "w7" in MUT:
        return dict(T, nA=None, nB=None)
    T = dict(T)
    P = len(T["NA"])
    nA = int(T["NA"].reshape(P, -1).sum(1).min())
    nB = int(T["NB"].reshape(P, -1).sum(1).min())
    NA = np.array([thin(T["NA"][v], nA, np.random.default_rng(list(key) + [0, v])) for v in range(P)])
    NB = np.array([thin(T["NB"][v], nB, np.random.default_rng(list(key) + [1, v])) for v in range(P)])
    T["NA"], T["NB"], T["nA"], T["nB"] = NA, NB, nA, nB
    T["PA"] = np.array([own_table(NA[w], T["Ss"][w]) for w in range(P)])
    T["PB"] = np.array([own_table(NB[v], T["Ss"][v]) for v in range(P)])
    return T


def eq_key(seed_base, null, strand, shape, k, g, seed):
    return [seed_base + 93, null, strand, shape, k, g, seed]


# ---------------------------------------------------------------- 3 案の近さ（D2）
def sim_e1(T):
    """s[w, v] = Σ NB_v · log PA_w / Σ NB_v。"""
    P = len(T["NA"])
    LA = np.log(T["PA"]).reshape(P, -1)
    NB = T["NB"].reshape(P, -1).astype(float)
    return (LA @ NB.T) / NB.sum(1)[None, :]


def sim_e2(T):
    """δ = log p − log S の、重み u = π_j S[j, c] の重み付きピアソン相関。重み付き分散が 0 なら 0。"""
    P = len(T["NA"])
    Ss = T["Ss"]
    dA = np.array([(np.log(T["PA"][w]) - np.log(Ss[w])).ravel() for w in range(P)])
    dB = np.array([(np.log(T["PB"][v]) - np.log(Ss[v])).ravel() for v in range(P)])
    u = (T["pi"][:, None] * T["S"]).ravel()
    u = u / u.sum()
    ca = dA - (dA @ u)[:, None]
    cb = dB - (dB @ u)[:, None]
    va = (ca * ca) @ u
    vb = (cb * cb) @ u
    cov = (ca * u[None, :]) @ cb.T
    out = np.zeros((P, P))
    ok = (va[:, None] > 0) & (vb[None, :] > 0)
    den = np.sqrt(np.outer(va, vb))
    out[ok] = cov[ok] / den[ok]
    return out


def sim_e3(T):
    """s[w, v] = − Σ_j π_j JS(PA_w[j], PB_v[j])（自然対数）。"""
    A = T["PA"][:, None]          # P×1×J×J
    B = T["PB"][None, :]          # 1×P×J×J
    Mx = 0.5 * (A + B)
    js = 0.5 * (A * (np.log(A) - np.log(Mx))).sum(-1) + 0.5 * (B * (np.log(B) - np.log(Mx))).sum(-1)
    return -(js * T["pi"][None, None, :]).sum(-1)


SIMS = dict(E1=sim_e1, E2=sim_e2, E3=sim_e3)


def sims(T):
    out = {e: SIMS[e](T) for e in EYES}
    for e in ("E1", "E3"):
        if not np.isfinite(out[e]).all():
            raise FloatingPointError("%s の近さに有限でない値（D2: 本計算を止める）" % e)
    if not np.isfinite(out["E2"]).all():
        raise FloatingPointError("E2 の近さに有限でない値")
    return out


# ---------------------------------------------------------------- 整数の W と入れ替え（D2・D3）
def score_matrix(s):
    """c[a, v] = Σ_{w ≠ a} (2 · [s[w, v] < s[a, v]] + [|s[w, v] − s[a, v]| ≤ 1e-12])（同点を先に判定）。整数。"""
    P = s.shape[0]
    c = np.zeros((P, P), dtype=np.int64)
    tie_pts = 2 if "w4" in MUT else 1
    for v in range(P):
        col = s[:, v]
        d = col[None, :] - col[:, None]       # d[a, w] = s[w, v] − s[a, v]
        tie = np.abs(d) <= TIE
        win = (~tie) & (d < 0)
        np.fill_diagonal(tie, False)
        np.fill_diagonal(win, False)
        c[:, v] = 2 * win.sum(1) + tie_pts * tie.sum(1)
    return c


def w_of(c, perm):
    """W_σ = Σ_v c[σ(v), v]（perm は σ の配列・2 次元なら行ごと）。T と T_σ はすべてこの関数で計算する。"""
    perm = np.asarray(perm)
    P = c.shape[0]
    return c[perm, np.arange(P)].sum(-1)


def auc_rows(c):
    P = c.shape[0]
    return np.diag(c) / (2.0 * (P - 1))


def t_of_w(W, P):
    return W / (2.0 * P * (P - 1))


def draw_perms(rng, P, n=N_PERM):
    """σ をそれぞれ独立に一様に引く（恒等も重複もありうる）。w2 は σ(v) = v を強制する。"""
    perms = np.array([rng.permutation(P) for _ in range(n)])
    if "w2" in MUT:
        perms[:] = np.arange(P)
    return perms


def p_sampled(c, perms):
    W = int(w_of(c, np.arange(c.shape[0])))
    Ws = w_of(c, perms)
    return (1 + int((Ws >= W).sum())) / (len(perms) + 1), W


def p_exact(c):
    """全列挙: #{σ : W_σ ≥ W} / P!（小さな P の P-HAND だけ）。"""
    P = c.shape[0]
    W = int(w_of(c, np.arange(P)))
    allp = np.array(list(itertools.permutations(range(P))))
    Ws = w_of(c, allp)
    return int((Ws >= W).sum()) / len(allp), W


# ---------------------------------------------------------------- 記述の量（D6）
def rank1(s):
    """列 v で s(v → v) が最大だった割合（同点は割る）。"""
    P = s.shape[0]
    tot = 0.0
    for v in range(P):
        col = s[:, v]
        mx = col.max()
        top = np.abs(col - mx) <= TIE
        if top[v]:
            tot += 1.0 / top.sum()
    return tot / P


def eer(gen, imp):
    """ROC（FAR, TPR）の操作点を直線でつなぎ、TPR = 1 − FAR と交わる FAR。閾値は 1e-12 以内を同じ値とまとめない（値そのまま）。"""
    gen = np.asarray(gen, float)
    imp = np.asarray(imp, float)
    th = np.unique(np.concatenate([gen, imp]))[::-1]
    far = [0.0] + [float((imp >= t).mean()) for t in th]
    tpr = [0.0] + [float((gen >= t).mean()) for t in th]
    f = [tp + fa - 1.0 for fa, tp in zip(far, tpr)]
    for i in range(1, len(f)):
        if f[i] >= 0:
            if f[i] == f[i - 1]:
                return far[i]
            r = -f[i - 1] / (f[i] - f[i - 1])
            return far[i - 1] + r * (far[i] - far[i - 1])
    return 1.0


def col_ranks(s):
    """列ごとに s を順位（平均順位・小さいほど遠い）に変える。"""
    return np.column_stack([avg_rank(s[:, v]) for v in range(s.shape[1])])


def avg_rank(x):
    """平均順位（1 始まり・完全に等しい値は平均）。scipy に依らない（両機で同じ結果にする）。"""
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort")
    xs = x[o]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = 0.5 * (i + j) + 1
        i = j + 1
    return r


def eer_pair(s):
    """(列ごとに順位で正規化した 1 つの閾値の EER, 書き手ごとの閾値の EER の平均)。"""
    P = s.shape[0]
    R = col_ranks(s)
    off = ~np.eye(P, dtype=bool)
    e_glob = eer(np.diag(R), R[off])
    e_each = float(np.mean([eer([s[v, v]], np.delete(s[:, v], v)) for v in range(P)]))
    return e_glob, e_each


def gain_own(T):
    """G_v = v の B での 1 記号あたりの対数尤度の、本人の A の表 − 共有の表（D6・目と独立）。"""
    P = len(T["NA"])
    NB = T["NB"].reshape(P, -1).astype(float)
    la = np.log(T["PA"]).reshape(P, -1)
    ls = np.log(T["S"]).ravel()
    return ((NB * la).sum(1) - NB @ ls) / NB.sum(1)


# ---------------------------------------------------------------- 1 セルの全部
def eval_cell(UC, P, H, k, g, perms, key):
    """3 案それぞれの W・p・AUC_v・rank-1・EER 2 つと、G_v。perms は 3 案で共通。表は揃えた表（v2・key は equalize の鍵）。"""
    T = equalize(cell_tables(UC, P, H, k, g), key)
    S3 = sims(T)
    out = dict(G=gain_own(T).tolist(), nA=T["nA"], nB=T["nB"])
    for e in EYES:
        s = S3[e]
        c = score_matrix(s)
        p, W = p_sampled(c, perms)
        eg, ee = eer_pair(s)
        out[e] = dict(W=W, p=p, auc=auc_rows(c).tolist(), rank1=rank1(s), eer_glob=eg, eer_each=ee)
    return out
