"""離散の HMM（K 状態 × M 記号）の前向き・後ろ向き・Baum–Welch（numpy・系列を詰めて時刻ごとに一括）。

系列は長さの違う整数の配列の list。詰めた行列 O（n × T）とマスク（n × T）で扱う。
各系列は初期分布 pi から始まる。スケーリングで対数尤度を出す。
"""
import numpy as np

# HMM 0.5.0（src-tauri/src/analysis/engine.rs の new_for_domain と INITIAL_PROBS）。放出は行の和が 1 でない。
A0 = np.array([0.75, 0.17, 0.08, 0.12, 0.80, 0.08, 0.06, 0.18, 0.76]).reshape(3, 3)
PI0 = np.array([0.80, 0.15, 0.05])
_E = [
    0.01, 0.02, 0.08, 0.12, 0.14, 0.01, 0.02, 0.08, 0.12, 0.13, 0.01, 0.01, 0.02, 0.01, 0.08,
    0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
    0.15, 0.10, 0.04, 0.03, 0.02, 0.14, 0.08, 0.04, 0.03, 0.02, 0.10, 0.08, 0.03, 0.02, 0.01,
    0.05, 0.04, 0.01, 0.01, 0.01, 0.04, 0.03, 0.01, 0.01, 0.01, 0.01,
    0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.04, 0.04, 0.05, 0.01,
    0.10, 0.16, 0.05, 0.07, 0.01, 0.16, 0.22, 0.12, 0.05, 0.02, 0.99,
]
B0_RAW = np.array(_E).reshape(3, 26)
B0 = B0_RAW / B0_RAW.sum(axis=1, keepdims=True)

MUTATE_BACKWARD = False  # 変異 m1: 後ろ向きで遷移を転置する


def pad(seqs):
    n, T = len(seqs), max(len(s) for s in seqs)
    O = np.zeros((n, T), dtype=np.int64)
    M = np.zeros((n, T), dtype=bool)
    for i, s in enumerate(seqs):
        O[i, :len(s)] = s
        M[i, :len(s)] = True
    return O, M


def forward(pi, A, B, O, M):
    """スケーリングした前向き。返り値: alpha（n×T×K・各時刻で正規化）、c（n×T・log c が 1 観測の予測の対数尤度）。"""
    n, T = O.shape
    K = len(pi)
    alpha = np.zeros((n, T, K))
    c = np.ones((n, T))
    a = pi[None, :] * B[:, O[:, 0]].T
    c[:, 0] = a.sum(1)
    alpha[:, 0] = a / c[:, 0:1]
    for t in range(1, T):
        a = (alpha[:, t - 1] @ A) * B[:, O[:, t]].T
        s = a.sum(1)
        m = M[:, t]
        c[m, t] = s[m]
        alpha[m, t] = a[m] / s[m, None]
        alpha[~m, t] = alpha[~m, t - 1]
    return alpha, c


def loglik(pi, A, B, O, M):
    """系列ごとの対数尤度の和と観測数。"""
    _, c = forward(pi, A, B, O, M)
    return float(np.log(c[M]).sum()), int(M.sum())


def backward(A, B, O, M, c):
    n, T = O.shape
    K = A.shape[0]
    beta = np.ones((n, T, K))
    At = A.T if MUTATE_BACKWARD else A
    for t in range(T - 2, -1, -1):
        m = M[:, t + 1]
        b = (B[:, O[:, t + 1]].T * beta[:, t + 1]) @ At.T
        beta[m, t] = b[m] / c[m, t + 1, None]
    return beta


def em_step(pi, A, B, O, M, pseudo):
    alpha, c = forward(pi, A, B, O, M)
    beta = backward(A, B, O, M, c)
    gamma = alpha * beta
    gamma /= gamma.sum(2, keepdims=True)
    K, Msym = B.shape
    # 遷移の期待値
    xi_sum = np.zeros((K, K))
    for t in range(O.shape[1] - 1):
        m = M[:, t + 1]
        if not m.any():
            break
        x = alpha[m, t][:, :, None] * A[None] * (B[:, O[m, t + 1]].T * beta[m, t + 1])[:, None, :]
        x /= c[m, t + 1][:, None, None]
        xi_sum += x.sum(0)
    em = np.zeros((K, Msym))
    g = gamma[M]
    np.add.at(em.T, O[M], g)
    pi_n = gamma[:, 0].sum(0) + pseudo
    A_n = xi_sum + pseudo
    B_n = em + pseudo
    return (pi_n / pi_n.sum(), A_n / A_n.sum(1, keepdims=True), B_n / B_n.sum(1, keepdims=True),
            float(np.log(c[M]).sum()))


def baum_welch(pi, A, B, O, M, pseudo, tol, max_iter):
    """1 観測あたりの対数尤度の変化が tol 未満で止める。返り値: (pi, A, B, 学習の 1 観測あたりの対数尤度, 回数, 収束したか)。"""
    nobs = int(M.sum())
    prev = None
    for it in range(1, max_iter + 1):
        pi, A, B, ll = em_step(pi, A, B, O, M, pseudo)
        ll /= nobs
        if prev is not None and abs(ll - prev) < tol:
            break
        prev = ll
    ll_final, _ = loglik(pi, A, B, O, M)
    return pi, A, B, ll_final / nobs, it, it < max_iter


def sample(pi, A, B, lengths, rng):
    seqs = []
    for L in lengths:
        s = np.empty(L, dtype=np.int64)
        z = rng.choice(len(pi), p=pi)
        for t in range(L):
            if t:
                z = rng.choice(len(pi), p=A[z])
            s[t] = rng.choice(B.shape[1], p=B[z])
        seqs.append(s)
    return seqs


def brute_loglik(pi, A, B, s):
    """全経路の和（短い系列の確かめ用）。"""
    import itertools
    K = len(pi)
    tot = 0.0
    for path in itertools.product(range(K), repeat=len(s)):
        p = pi[path[0]] * B[path[0], s[0]]
        for t in range(1, len(s)):
            p *= A[path[t - 1], path[t]] * B[path[t], s[t]]
        tot += p
    return float(np.log(tot))
