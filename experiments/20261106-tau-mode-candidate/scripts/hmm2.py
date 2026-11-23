"""ふつうの HMM（K × 26 記号）と AR(1)-HMM（放出が状態と前の記号に条件づく）の前向き・後ろ向き・MAP-EM。

conditions.md の E1〜E5。numpy・系列を詰めて時刻ごとに一括（B の hmm.py と同じ作り）。
放出の行列 E（n × T × K）を母数から一度作り、前向き・後ろ向きは E だけを見る（構造に依らない）。

母数（dict）:
  kind="hmm": pi（K）・A（K × K）・B（K × 26）
  kind="ar":  pi・A・H（K × 26・本当の系列の頭の記号）・C（K × 26 × 26・C[k, 前, 今]）
系列の頭（prev = −1）は、ふつうの HMM では B、AR では H を使う。当てはめだけ長い系列を CHUNK 記号の
切れ端に分ける（切れ端の頭で状態の分布を π に戻す・AR は切れ端の頭でも切れる前の記号を前として使う）。
評価は切らない。変異の切り替え（MUT）は ml.py の --mutate が設定する。
"""
import numpy as np

NSYM = 26
BASE = dict(pi=1.0, A=1.0, B=0.5, H=0.5, C=0.5)  # 基の擬似度数（B と r1・r0 と同じ）
TOL, MAX_ITER = 1e-7, 500
CHUNK = 900
BATCH = 256
MUT = set()  # "m1" 漏れ・"m2" AR で今の記号を前として使う・"m3" 事前分布の S̄ の A を転置・"m15" τ を min(τ, 10^4) にする・
#             "m25" 最頻値の和 0 の行を一様にせず 0 のままにする


def make_rows(seqs, chunk=None):
    """系列 → [(観測, 前の記号)]。chunk があれば切れ端に分ける（切れ端の頭の前の記号は切れる前の記号・本当の頭は −1）。"""
    rows = []
    for s in seqs:
        s = np.asarray(s, dtype=np.int64)
        if len(s) == 0:
            continue
        if chunk and len(s) > chunk:
            for i in range(0, len(s), chunk):
                o = s[i:i + chunk]
                p = np.empty(len(o), dtype=np.int64)
                p[1:] = o[:-1]
                p[0] = s[i - 1] if i > 0 else -1
                rows.append((o, p))
        else:
            p = np.empty(len(s), dtype=np.int64)
            p[1:] = s[:-1]
            p[0] = -1
            rows.append((s, p))
    return rows


class Batched:
    """当てはめの系列を BATCH 本ずつの束に分けたもの（E 段の度数と尤度を束ごとに足す・メモリのため・判断 8）。"""

    def __init__(self, seqs, chunk=None, size=None):
        rows = make_rows(seqs, chunk)
        size = size or BATCH
        self.parts = [Data(None, rows=rows[i:i + size]) for i in range(0, len(rows), size)]
        self.nobs = sum(p.nobs for p in self.parts)


def parts_of(D):
    return D.parts if isinstance(D, Batched) else [D]


class Data:
    """詰めた系列。O（観測）・P（前の記号・本当の頭は −1）・M（マスク）。"""

    def __init__(self, seqs, chunk=None, rows=None):
        rows = make_rows(seqs, chunk) if rows is None else rows
        n, T = len(rows), max(len(o) for o, _ in rows)
        self.O = np.zeros((n, T), dtype=np.int64)
        self.P = np.full((n, T), -1, dtype=np.int64)
        self.M = np.zeros((n, T), dtype=bool)
        for i, (o, p) in enumerate(rows):
            self.O[i, :len(o)] = o
            self.P[i, :len(o)] = p
            self.M[i, :len(o)] = True
        self.nobs = int(self.M.sum())


def n_free(kind, K):
    """自由な母数の数（同点のときに小さい方を採る並べに使う）。"""
    base = (K - 1) + K * (K - 1)
    return base + (K * 25 if kind == "hmm" else K * 25 + K * 26 * 25)


def emis(m, D):
    """放出の行列（n × T × K）。"""
    if m["kind"] == "hmm":
        return np.moveaxis(m["B"][:, D.O], 0, -1)
    head = D.P < 0
    prev = D.O if "m2" in MUT else np.where(head, 0, D.P)
    E = np.moveaxis(m["C"][:, prev, D.O], 0, -1)
    Eh = np.moveaxis(m["H"][:, D.O], 0, -1)
    if "m2" in MUT:
        return E
    return np.where(head[..., None], Eh, E)


def forward(m, D, E=None):
    """スケーリングした前向き。alpha[:, t] はフィルタ、c[:, t] = p(o_t | o_<t)。"""
    E = emis(m, D) if E is None else E
    n, T, K = E.shape
    A = m["A"]
    alpha = np.zeros((n, T, K))
    c = np.ones((n, T))
    a = m["pi"][None, :] * E[:, 0]
    c[:, 0] = a.sum(1)
    alpha[:, 0] = a / c[:, 0:1]
    for t in range(1, T):
        mk = D.M[:, t]
        a = (alpha[:, t - 1] @ A) * E[:, t]
        s = a.sum(1)
        c[mk, t] = s[mk]
        alpha[mk, t] = a[mk] / s[mk, None]
        alpha[~mk, t] = alpha[~mk, t - 1]
    return alpha, c, E


def pred_logprob(m, D):
    """1 歩先の予測の対数確率（n × T・マスクの外は 0）。m1 は o_t を見たフィルタから o_t を予測する漏れ。"""
    alpha, c, E = forward(m, D)
    if "m1" in MUT:
        lp = np.log(np.clip((alpha * E).sum(2), 1e-300, None))
    else:
        lp = np.log(c)
    return np.where(D.M, lp, 0.0)


def pred_dist(m, D):
    """各時刻の予測の分布（n × T × 26）と、その o_t の値（P-EM3 用・評価と同じ前向きの経路）。"""
    alpha, c, E = forward(m, D)
    n, T, K = E.shape
    prior = np.zeros((n, T, K))
    prior[:, 0] = m["pi"][None, :]
    prior[:, 1:] = alpha[:, :-1] @ m["A"]
    if m["kind"] == "hmm":
        dist = prior @ m["B"]
    else:
        head = D.P < 0
        prev = np.where(head, 0, D.P)
        Cp = np.moveaxis(m["C"][:, prev, :], 0, 2)  # n × T × K × 26
        dist = np.einsum("ntk,ntks->nts", prior, Cp)
        dist_h = prior @ m["H"]
        dist = np.where(head[..., None], dist_h, dist)
    at = np.take_along_axis(dist, D.O[..., None], 2)[..., 0]
    return dist, at, c


def backward(m, D, E, c):
    n, T, K = E.shape
    A = m["A"]
    beta = np.ones((n, T, K))
    for t in range(T - 2, -1, -1):
        mk = D.M[:, t + 1]
        b = (E[:, t + 1] * beta[:, t + 1]) @ A.T
        beta[mk, t] = b[mk] / c[mk, t + 1, None]
    return beta


def xi_counts_loop(A, alpha, beta, E, c, M):
    """遷移の期待度数（時刻ごとのループ・B の hmm.py と同じ作り）。xi_counts の照合にだけ使う。"""
    K = A.shape[0]
    xi = np.zeros((K, K))
    for t in range(M.shape[1] - 1):
        mk = M[:, t + 1]
        if not mk.any():
            break
        x = alpha[mk, t][:, :, None] * A[None] * (E[mk, t + 1] * beta[mk, t + 1])[:, None, :]
        xi += (x / c[mk, t + 1][:, None, None]).sum(0)
    return xi


def xi_counts(A, alpha, beta, E, c, M):
    """遷移の期待度数を全時刻で一度に足す（ループ版と同じ量・selftest の P-XI で照らす）。
    Σ_{n,t: M[n,t+1]} alpha[n,t,i] A[i,j] E[n,t+1,j] beta[n,t+1,j] / c[n,t+1]。"""
    w = np.where(M[:, 1:], 1.0 / c[:, 1:], 0.0)
    R = E[:, 1:] * beta[:, 1:] * w[..., None]
    return np.einsum("nti,ntj->ij", alpha[:, :-1], R) * A


def keys_of(kind):
    return ("pi", "A", "B") if kind == "hmm" else ("pi", "A", "H", "C")


def counts(m, D):
    """E 段。期待度数（母数と同じ形）と対数尤度。D が束（Batched）なら束ごとに足す。"""
    if isinstance(D, Batched):
        S, ll = None, 0.0
        for part in D.parts:
            s, l_ = counts_one(m, part)
            S = s if S is None else {k: S[k] + s[k] for k in S}
            ll += l_
        return S, ll
    return counts_one(m, D)


def counts_one(m, D):
    alpha, c, E = forward(m, D)
    beta = backward(m, D, E, c)
    gamma = alpha * beta
    gamma /= gamma.sum(2, keepdims=True)
    K = len(m["pi"])
    xi = xi_counts(m["A"], alpha, beta, E, c, D.M)
    S = dict(pi=gamma[:, 0].sum(0), A=xi)
    if m["kind"] == "hmm":
        em = np.zeros((NSYM, K))
        np.add.at(em, D.O[D.M], gamma[D.M])
        S["B"] = em.T
    else:
        hm = D.M & (D.P < 0)
        cm = D.M & (D.P >= 0)
        eh = np.zeros((NSYM, K))
        np.add.at(eh, D.O[hm], gamma[hm])
        ec = np.zeros((NSYM * NSYM, K))
        np.add.at(ec, D.P[cm] * NSYM + D.O[cm], gamma[cm])
        S["H"] = eh.T
        S["C"] = ec.T.reshape(K, NSYM, NSYM)
    return S, float(np.log(c[D.M]).sum())


def base_prior(kind, K):
    pr = dict(pi=np.full(K, BASE["pi"]), A=np.full((K, K), BASE["A"]))
    if kind == "hmm":
        pr["B"] = np.full((K, NSYM), BASE["B"])
    else:
        pr["H"] = np.full((K, NSYM), BASE["H"])
        pr["C"] = np.full((K, NSYM, NSYM), BASE["C"])
    return pr


def make_prior(kind, K, tau, sbar=None):
    """c_r = 基の擬似度数 + τ · S̄_r（S̄ は共通の 1 記号あたりの期待度数・全セルの和 = 1 になるように作る）。"""
    pr = base_prior(kind, K)
    if "m15" in MUT:
        tau = min(tau, 10_000)
    if tau > 0:
        for key in keys_of(kind):
            s = sbar[key]
            if key == "A" and "m3" in MUT:
                s = s.T
            pr[key] = pr[key] + tau * s
    return pr


def sbar_of(S, nobs):
    """期待度数 → 1 記号あたり。各記号は π か A のどちらか 1 つと、放出の 1 つに入るので、π＋A と放出がそれぞれ和 1 になる。"""
    return {k: v / nobs for k, v in S.items()}


def log_prior(m, pr):
    return float(sum((pr[k] * np.log(m[k])).sum() for k in keys_of(m["kind"])))


def normalize(kind, X):
    out = dict(kind=kind, pi=X["pi"] / X["pi"].sum(), A=X["A"] / X["A"].sum(1, keepdims=True))
    if kind == "hmm":
        out["B"] = X["B"] / X["B"].sum(1, keepdims=True)
    else:
        out["H"] = X["H"] / X["H"].sum(1, keepdims=True)
        out["C"] = X["C"] / X["C"].sum(2, keepdims=True)
    return out


def mode_of(kind, sbar):
    """事前分布の最頻値 normalize(S̄)（τ → ∞ の行き先・本人の記録を入れない点・判断 1・8）。
    和が正の行は normalize と同じ割り算（ビットまで同じ）。和が 0 の行（AR の C の [k, j, :] で、前の記号 j が
    共通に一度も出ないとき）は一様（1/26）を置く（m25 は 0 のまま）。返り値: (母数, 和 0 の行の印 {鍵: bool の配列})。"""
    out = dict(kind=kind)
    zero = {}
    for key in keys_of(kind):
        X = sbar[key]
        axis = 0 if key == "pi" else (2 if key == "C" else 1)
        tot = X.sum(axis, keepdims=True)
        z = tot == 0
        if key in ("pi", "A"):
            assert not z.any(), "最頻値の %s（%s）の和が 0" % (key, kind)  # 期待度数が正の共通から作るので起きない
        Y = np.divide(X, tot, out=np.zeros_like(X), where=~z)
        if z.any() and "m25" not in MUT:
            Y = np.where(z, 1.0 / X.shape[axis], Y)
        out[key] = Y
        zero[key] = np.squeeze(z, axis)
    return out, zero


def pred_logprob_zero(m, D):
    """確率 0 のセルを持ちうる母数（最頻値）の 1 歩先の対数確率（n × T・マスクの外は 0）。
    forward は、ある時刻で全状態の放出が 0 だと c = 0（log は −∞）、alpha = 0/0 = NaN になり、以後の c も NaN になる。
    系列ごとに、マスクの中で最初に c = 0 になる時刻 t0 から後を −∞ とする（判断 4）。t0 より前に非有限があれば誤り。"""
    with np.errstate(divide="ignore", invalid="ignore"):
        _, c, _ = forward(m, D)
        lp = np.log(c)
    zero = (c == 0) & D.M
    after = np.cumsum(zero, axis=1) > 0
    before_bad = D.M & ~after & ~np.isfinite(lp)
    if before_bad.any():
        raise ValueError("確率 0 の前に非有限の対数確率がある")
    lp = np.where(after, -np.inf, lp)
    return np.where(D.M, lp, 0.0)


def zero_row_hit(m_zero, D):
    """評価の系列が、和 0 の行（一様を置いた行）を使う位置を持つか（AR の C だけ・前の記号が j の位置）。"""
    if "C" not in m_zero:
        return False
    rows = m_zero["C"].any(0)  # 前の記号 j ごと（どれかの状態で和 0）
    cm = D.M & (D.P >= 0)
    return bool(rows[D.P[cm]].any())


def loglik(m, D):
    """当てはめの系列（切れ端・束）の対数尤度の和。"""
    tot = 0.0
    for part in parts_of(D):
        _, c, _ = forward(m, part)
        tot += float(np.log(c[part.M]).sum())
    return tot


def objective(m, D, pr):
    return loglik(m, D) + log_prior(m, pr)


def em_from(m, D, pr):
    """1 つの開始点から。返り値: 母数・1 記号あたりの目的・回数・収束したか・減った回の数。"""
    prev, dec, conv = None, 0, False
    it = 0
    for it in range(1, MAX_ITER + 1):
        S, ll = counts(m, D)
        o = (ll + log_prior(m, pr)) / D.nobs  # 更新前の母数の目的
        if prev is not None:
            if o < prev - 1e-9:
                dec += 1
            if abs(o - prev) < TOL:
                conv = True
                break
        prev = o
        m = normalize(m["kind"], {k: S[k] + pr[k] for k in keys_of(m["kind"])})
    return m, objective(m, D, pr) / D.nobs, it, conv, dec


def fit(starts, D, pr):
    """開始点 [(名前, 母数)] から、目的がいちばん大きいものを採る。"""
    res = [(name,) + em_from(m, D, pr) for name, m in starts]
    objs = [r[2] for r in res]
    order = np.argsort(objs)[::-1]
    best = res[order[0]]
    diag = dict(winner=best[0], gap12=float(objs[order[0]] - objs[order[1]]) if len(res) > 1 else None,
                nonconv=sum(not r[4] for r in res), decreases=sum(r[5] for r in res), iters=[r[3] for r in res])
    return best[1], diag


def random_model(kind, K, rng, r1=None, r0=None):
    """Dirichlet(1) の開始点。AR の C は r1 に Dirichlet(50 · 行) の揺らぎ（ランダムな 26 × 26 は遠すぎる）。"""
    m = dict(kind=kind, pi=rng.dirichlet(np.ones(K)), A=rng.dirichlet(np.ones(K), K))
    if kind == "hmm":
        m["B"] = rng.dirichlet(np.ones(NSYM), K)
    else:
        m["H"] = np.stack([rng.dirichlet(50 * r0 + 1e-3) for _ in range(K)])
        m["C"] = np.stack([np.stack([rng.dirichlet(50 * r1[j] + 1e-3) for j in range(NSYM)]) for _ in range(K)])
        m["H"] = np.clip(m["H"], 1e-12, None); m["H"] /= m["H"].sum(1, keepdims=True)
        m["C"] = np.clip(m["C"], 1e-12, None); m["C"] /= m["C"].sum(2, keepdims=True)
    return m


def r0_r1(seqs):
    """閉じた形の参照。r0 = 全記号の頻度（各 +0.5）。r1 = 頭の記号の頻度（頭だけ・各 +0.5）と 1 次の遷移（各 +0.5）。
    r1 の頭は AR(1)-HMM の K = 1・τ = 0 と一致させるため、頭の記号だけで数える（B の r1 は頭に r0 を使った・条件に書く）。"""
    c0 = np.full(NSYM, 0.5)
    h = np.full(NSYM, 0.5)
    T = np.full((NSYM, NSYM), 0.5)
    for s in seqs:
        s = np.asarray(s, dtype=np.int64)
        if len(s) == 0:
            continue
        np.add.at(c0, s, 1)
        h[s[0]] += 1
        np.add.at(T, (s[:-1], s[1:]), 1)
    return c0 / c0.sum(), h / h.sum(), T / T.sum(1, keepdims=True)


def ll_r0(p, seqs):
    return float(sum(np.log(p[np.asarray(s)]).sum() for s in seqs if len(s)))


def ll_r1(h, T, seqs):
    tot = 0.0
    for s in seqs:
        s = np.asarray(s)
        if len(s):
            tot += np.log(h[s[0]]) + np.log(T[s[:-1], s[1:]]).sum()
    return float(tot)


def r1_model(h, T):
    """r1 を K = 1 の AR(1)-HMM の母数として表す（P-AR1 の比べ・開始点に使う）。"""
    return dict(kind="ar", pi=np.ones(1), A=np.ones((1, 1)), H=h[None, :].copy(), C=T[None].copy())


def sample(m, lengths, rng):
    """合成の系列（対照用）。"""
    K = len(m["pi"])
    seqs = []
    for L in lengths:
        z = np.empty(L, dtype=np.int64)
        s = np.empty(L, dtype=np.int64)
        z[0] = rng.choice(K, p=m["pi"])
        for t in range(L):
            if t > 0:
                z[t] = rng.choice(K, p=m["A"][z[t - 1]])
            if m["kind"] == "hmm":
                p = m["B"][z[t]]
            else:
                p = m["H"][z[t]] if t == 0 else m["C"][z[t], s[t - 1]]
            s[t] = rng.choice(NSYM, p=p)
        seqs.append(s)
    return seqs


def order_states(m):
    """状態を放出の x_bin の期待値の昇順に並べる添字（名前は付けない・S1〜SK）。AR は頭の分布 H で並べる。"""
    xb = np.array([o // 5 if o < 25 else 5 for o in range(NSYM)], dtype=float)
    return np.argsort((m["B"] if m["kind"] == "hmm" else m["H"]) @ xb)
