"""作業を「様式の出方を決める隠れた状態」とする隠れマルコフモデル（auto-context-task-level・v2）。

設計は `.steering/20261121-auto-context-task-level/design.md`（v2 を本体にするハイブリッド・判断 7）。

- 観測は 1 段目（`experiments/20261121-auto-context-segmentation/acs_core.py`）の 180 秒の窓ごとの様式の名前。
- 状態は作業。出力は状態ごとに様式の上のカテゴリ分布（ディリクレの疑似カウント付きの MAP）。
- 遷移は学ばない。自己遷移の確率を平均の滞在 `D` 窓から `1 - 1/D` に固定し、ほかの状態へは均等に分ける。
- 欠測（無操作・操作の有無が分からない窓）は観測の無い時間の歩みとして扱う。列の中では観測だけを持ち、
  観測の間の欠測の数 `gap` に応じて遷移を `gap + 1` 歩ぶんにする（和は A の冪、最大は 1 回の乗り換えまで）。
- 推定や介入の入力にしない（ADR-010 D3・ADR-014 D4b）。名前は work-A, work-B, … で、宣言の名前に写し替えない（ADR-012 D3）。
- 依存は numpy だけ。
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

MISSING = -1


@dataclass
class Seq:
    """1 本の観測の列。`obs[i]` は様式の番号、`gap[i]` はその観測の前の欠測の窓の数（`gap[0]` は使わない）。

    `index[i]` は元の窓の列の中での位置（復号の結果を窓へ戻すため）。
    """

    obs: np.ndarray
    gap: np.ndarray
    index: np.ndarray


def build_sequences(labels: np.ndarray, missing: np.ndarray, reset_before: np.ndarray) -> list[Seq]:
    """窓の列から観測の列を作る。

    - `labels[i]` は窓 i の様式（`missing[i]` が真なら読まない）。
    - `reset_before[i]` が真なら、窓 i の前で列を切る（状態を初期分布に戻す）。
    列の頭の欠測は捨てる（初期分布から始めるので、頭の欠測の数は尤度に効かない）。
    """
    m = len(labels)
    seqs: list[Seq] = []
    obs: list[int] = []
    gap: list[int] = []
    idx: list[int] = []
    pending = 0
    for i in range(m):
        if reset_before[i] and obs:
            seqs.append(Seq(np.array(obs), np.array(gap), np.array(idx)))
            obs, gap, idx = [], [], []
        if reset_before[i]:
            pending = 0
        if missing[i]:
            pending += 1
            continue
        obs.append(int(labels[i]))
        gap.append(pending if obs[:-1] else 0)
        idx.append(i)
        pending = 0
    if obs:
        seqs.append(Seq(np.array(obs), np.array(gap), np.array(idx)))
    return seqs


def stay_prob(mean_stay_windows: float) -> float:
    if mean_stay_windows <= 1:
        raise ValueError("mean_stay_windows must be > 1")
    return 1.0 - 1.0 / mean_stay_windows


def trans_sum(k: int, p: float, steps: int) -> np.ndarray:
    """自己遷移 p・ほかへ均等の遷移行列の `steps` 乗（前向き後ろ向き用）。"""
    if k == 1:
        return np.ones((1, 1))
    q = (1.0 - p) / (k - 1)
    lam = p - q  # 固有値（1 以外）
    pn = 1.0 / k + (1.0 - 1.0 / k) * lam**steps
    qn = (1.0 - pn) / (k - 1)
    a = np.full((k, k), qn)
    np.fill_diagonal(a, pn)
    return a


def trans_max(k: int, p: float, steps: int) -> np.ndarray:
    """`steps` 歩の経路のうち確率が最大のものの確率（Viterbi 用）。

    同じ状態にとどまるのは p^steps（いったん離れて戻るより大きい: p > q のとき）。違う状態へは
    1 回だけ乗り換える経路 q * p^(steps-1) が最大（p > q のとき）。
    """
    if k == 1:
        return np.ones((1, 1))
    q = (1.0 - p) / (k - 1)
    if p <= q:
        raise ValueError("self transition must dominate (p > q)")
    a = np.full((k, k), q * p ** (steps - 1))
    np.fill_diagonal(a, p**steps)
    return a


@dataclass
class Hmm:
    pi: np.ndarray  # (K,)
    emis: np.ndarray  # (K, S)
    p_stay: float
    loglik: float = -math.inf
    bic: float = math.inf

    @property
    def k(self) -> int:
        return len(self.pi)


class _TransCache:
    def __init__(self, k: int, p: float):
        self.k, self.p = k, p
        self.s: dict[int, np.ndarray] = {}
        self.m: dict[int, np.ndarray] = {}

    def sum(self, steps: int) -> np.ndarray:
        if steps not in self.s:
            self.s[steps] = trans_sum(self.k, self.p, steps)
        return self.s[steps]

    def max(self, steps: int) -> np.ndarray:
        if steps not in self.m:
            self.m[steps] = trans_max(self.k, self.p, steps)
        return self.m[steps]


def forward_backward(seq: Seq, h: Hmm, cache: _TransCache | None = None) -> tuple[np.ndarray, float]:
    """事後確率 gamma（T, K）と対数尤度を返す（スケーリング法）。"""
    cache = cache or _TransCache(h.k, h.p_stay)
    n = len(seq.obs)
    k = h.k
    e = h.emis[:, seq.obs].T  # (T, K)
    alpha = np.empty((n, k))
    c = np.empty(n)
    a = h.pi * e[0]
    c[0] = a.sum()
    alpha[0] = a / c[0]
    for t in range(1, n):
        a = (alpha[t - 1] @ cache.sum(int(seq.gap[t]) + 1)) * e[t]
        c[t] = a.sum()
        alpha[t] = a / c[t]
    beta = np.empty((n, k))
    beta[n - 1] = 1.0
    for t in range(n - 2, -1, -1):
        beta[t] = (cache.sum(int(seq.gap[t + 1]) + 1) @ (e[t + 1] * beta[t + 1])) / c[t + 1]
    gamma = alpha * beta
    gamma /= gamma.sum(axis=1, keepdims=True)
    return gamma, float(np.log(c).sum())


def loglik(seqs: list[Seq], h: Hmm) -> float:
    cache = _TransCache(h.k, h.p_stay)
    return float(sum(forward_backward(s, h, cache)[1] for s in seqs))


def fit_hmm(seqs: list[Seq], n_symbols: int, k: int, p_stay: float, rng: np.random.Generator,
            n_init: int, pseudo: float, max_iter: int = 200, tol: float = 1e-6) -> Hmm:
    """出力と初期分布だけを EM（MAP）で学ぶ。初期値を変えて `n_init` 回走らせ、尤度の高いものを採る。"""
    best: Hmm | None = None
    for _ in range(n_init if k > 1 else 1):
        emis = rng.dirichlet(np.ones(n_symbols), size=k) if k > 1 else np.full((1, n_symbols), 1.0 / n_symbols)
        h = Hmm(np.full(k, 1.0 / k), emis, p_stay)
        prev = -math.inf
        for _ in range(max_iter):
            cache = _TransCache(k, p_stay)
            cnt = np.full((k, n_symbols), pseudo)
            pi_cnt = np.full(k, pseudo)
            ll = 0.0
            for s in seqs:
                g, l_s = forward_backward(s, h, cache)
                ll += l_s
                np.add.at(cnt.T, s.obs, g)
                pi_cnt += g[0]
            h.emis = cnt / cnt.sum(axis=1, keepdims=True)
            h.pi = pi_cnt / pi_cnt.sum()
            if ll - prev < tol * abs(ll):
                break
            prev = ll
        h.loglik = loglik(seqs, h)
        if best is None or h.loglik > best.loglik:
            best = h
    assert best is not None
    n_obs = sum(len(s.obs) for s in seqs)
    n_params = k * (n_symbols - 1) + (k - 1)
    best.bic = -2.0 * best.loglik + n_params * math.log(max(n_obs, 1))
    return best


def select_hmm(seqs: list[Seq], n_symbols: int, k_max: int, p_stay: float, seed: int, n_init: int,
               pseudo: float) -> Hmm:
    """K = 1..k_max から BIC が最小のものを選ぶ（K = 1 を許す）。"""
    rng = np.random.default_rng(seed)
    best: Hmm | None = None
    for k in range(1, k_max + 1):
        h = fit_hmm(seqs, n_symbols, k, p_stay, rng, n_init, pseudo)
        if best is None or h.bic < best.bic:
            best = h
    assert best is not None
    return best


def viterbi(seq: Seq, h: Hmm, cache: _TransCache | None = None) -> np.ndarray:
    cache = cache or _TransCache(h.k, h.p_stay)
    n, k = len(seq.obs), h.k
    with np.errstate(divide="ignore"):
        le = np.log(h.emis[:, seq.obs].T)
        lpi = np.log(h.pi)
    delta = lpi + le[0]
    back = np.zeros((n, k), dtype=int)
    for t in range(1, n):
        with np.errstate(divide="ignore"):
            la = np.log(cache.max(int(seq.gap[t]) + 1))
        sc = delta[:, None] + la
        back[t] = sc.argmax(axis=0)
        delta = sc.max(axis=0) + le[t]
    path = np.zeros(n, dtype=int)
    path[-1] = int(delta.argmax())
    for t in range(n - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path


def decode(seqs: list[Seq], h: Hmm, m: int) -> np.ndarray:
    """全部の列を復号し、長さ m の窓の列に戻す（観測の無い窓は MISSING）。"""
    out = np.full(m, MISSING, dtype=int)
    cache = _TransCache(h.k, h.p_stay)
    for s in seqs:
        out[s.index] = viterbi(s, h, cache)
    return out


def reset_points(known_idle: np.ndarray, seams: np.ndarray | None, window_s: int, reset_idle_s: int) -> np.ndarray:
    """列を切る点（長さ m）。ファイルの継ぎ目と、操作が無いと分かっている窓が `reset_idle_s` 以上続いた後。

    切るのは無操作の連続が終わった直後の窓の前（連続の中は欠測なので、どこで切っても尤度は同じ）。
    操作の有無が分からない窓は無操作の長さに数えない（1 段目の判断 22 と同じ）。
    """
    m = len(known_idle)
    r = np.zeros(m, dtype=bool)
    if seams is not None:
        r |= seams[:m]
    run = 0
    for i in range(m):
        if seams is not None and seams[i]:
            run = 0
        if known_idle[i]:
            run += 1
            continue
        if run * window_s >= reset_idle_s:
            r[i] = True
        run = 0
    return r


def name_states(lab: np.ndarray, durations_s: np.ndarray) -> dict[int, str]:
    """合計時間の多い順に work-A, work-B, … を付ける（観測の無い窓は none）。"""
    totals: dict[int, float] = {}
    for v, d in zip(lab, durations_s):
        if v != MISSING:
            totals[int(v)] = totals.get(int(v), 0.0) + float(d)
    order = sorted(totals, key=lambda v: (-totals[v], v))
    names = {v: f"work-{chr(ord('A') + i)}" for i, v in enumerate(order)}
    names[MISSING] = "none"
    return names
