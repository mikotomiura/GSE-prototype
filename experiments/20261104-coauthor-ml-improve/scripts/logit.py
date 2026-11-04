"""ロジスティック・評価の量（design §4・§5）。B の perperson.py の fit_logistic・calib・auc・losses を写し、
寄せの罰（β を β_共通 へ）・書き手の切片の固定効果・書き手の中の一致度を足した。変異の切り替え（MUT）は ml.py が設定する。

  m4: 罰を λ/2‖β‖²（0 へ寄せる）にする
  m5: 一致度を書き手で層にせず、全問いの組で数える
"""
import numpy as np

LAM0 = 1.0          # 共通（1 つの切片・固定効果）の罰（B の λ と同じ）
LAMS = [0.1, 1.0, 10.0, 100.0, float("inf")]
MUT = set()


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -35, 35)))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def fit_logistic(X, y, lam=0.0, offset=None, w=None, pseudo=False):
    """切片つき・切片は罰しない・Newton 法（許容 1e-8・最大 100 回）。pseudo は特徴 0・オフセット 0 の y=1 と y=0 を重み 0.5 ずつ足す。
    返り値: (係数 [切片, β…], 収束したか)。B の perperson.py と同じ。"""
    X = np.zeros((len(y), 0)) if X is None else np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
    off = np.zeros(len(y)) if offset is None else np.asarray(offset, dtype=float)
    if pseudo:
        X = np.vstack([X, np.zeros((2, X.shape[1]))])
        y = np.concatenate([y, [1.0, 0.0]])
        w = np.concatenate([w, [0.5, 0.5]])
        off = np.concatenate([off, [0.0, 0.0]])
    Xd = np.hstack([np.ones((len(y), 1)), X])
    beta = np.zeros(Xd.shape[1])
    R = np.eye(Xd.shape[1]) * lam
    R[0, 0] = 0.0
    conv = False
    for _ in range(100):
        p = sigmoid(Xd @ beta + off)
        g = Xd.T @ (w * (y - p)) - R @ beta
        Hs = (Xd * (w * p * (1 - p))[:, None]).T @ Xd + R
        step = np.linalg.solve(Hs + 1e-12 * np.eye(len(beta)), g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            conv = True
            break
    return beta, conv


def fit_fe(Xs, ys, lam=LAM0):
    """書き手ごとの切片（固定効果・各書き手に擬似観測 2 つ）と共通の係数 β。β にだけ罰 lam。
    Xs・ys は書き手ごとの配列のリスト（問いの無い書き手は擬似観測だけが入る）。返り値: (β, 収束したか)。"""
    W = len(Xs)
    p_ = Xs[0].shape[1] if W and np.ndim(Xs[0]) == 2 else 0
    rows, yy, ww, wid = [], [], [], []
    for i, (X, y) in enumerate(zip(Xs, ys)):
        X = np.asarray(X, dtype=float).reshape(-1, p_)
        rows += [X, np.zeros((2, p_))]
        yy += list(y) + [1.0, 0.0]
        ww += [1.0] * len(y) + [0.5, 0.5]
        wid += [i] * (len(y) + 2)
    X = np.vstack(rows)
    y, w, wid = np.array(yy), np.array(ww), np.array(wid)
    D = np.zeros((len(y), W))
    D[np.arange(len(y)), wid] = 1.0
    Xd = np.hstack([D, X])
    theta = np.zeros(W + p_)
    R = np.zeros(W + p_)
    R[W:] = lam
    conv = False
    for _ in range(100):
        pr = sigmoid(Xd @ theta)
        g = Xd.T @ (w * (y - pr)) - R * theta
        Hs = (Xd * (w * pr * (1 - pr))[:, None]).T @ Xd + np.diag(R)
        step = np.linalg.solve(Hs + 1e-12 * np.eye(len(theta)), g)
        theta = theta + step
        if np.max(np.abs(step)) < 1e-8:
            conv = True
            break
    return theta[W:], conv


class Std:
    """標準化（平均・SD・SD が 0 なら 1）。本人と共通で同じもの（他人の評価以外の問い）を使う（design §4.2）。"""

    def __init__(self, X):
        X = np.asarray(X, dtype=float)
        self.mu = X.mean(0)
        sd = X.std(0)
        sd[sd == 0] = 1.0
        self.sd = sd

    def __call__(self, X):
        X = np.asarray(X, dtype=float)
        return (X - self.mu) / self.sd


def fit_self(Z, y, beta_c, lam):
    """本人: 切片 b（罰さない・擬似観測 2 つ）と β。目的は対数尤度 − λ/2‖β − β_c‖²。
    δ = β − β_c をオフセット Z β_c の上で罰 λ で当てる。λ = ∞ は δ = 0（切片だけ）。
    返り値: (切片, β, 収束したか)。m4 は 0 へ寄せる（β_c を使わない）。"""
    Z = np.asarray(Z, dtype=float).reshape(len(y), -1)
    bc = np.zeros(Z.shape[1]) if "m4" in MUT else np.asarray(beta_c, dtype=float)
    off = Z @ bc
    if np.isinf(lam):
        th, conv = fit_logistic(None, y, offset=off, pseudo=True)
        return float(th[0]), bc.copy(), conv
    th, conv = fit_logistic(Z, y, lam=lam, offset=off, pseudo=True)
    return float(th[0]), bc + th[1:], conv


def predict(b, beta, Z):
    Z = np.asarray(Z, dtype=float).reshape(-1, len(beta))
    return sigmoid(b + Z @ beta)


def losses(y, p):
    y, p = np.asarray(y, dtype=float), np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return float(np.mean((p - y) ** 2)), float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def logloss_sum(y, p):
    y, p = np.asarray(y, dtype=float), np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return float(-np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))


def auc(y, p):
    """順位による AUC（同点は平均の順位）。陽性か陰性が無ければ None。B と同じ。"""
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="mergesort")
    sv = allv[order]
    ranks = np.empty(len(sv))
    i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2 + 1
        i = j + 1
    r = np.empty(len(sv))
    r[order] = ranks
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def conc_counts(y, p):
    """1 書き手の (一致の数, 組の数)。一致 = 陽性 i・陰性 j で p_i > p_j を 1、同点を 0.5。"""
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.0, 0
    a = auc(y, p)
    return a * len(pos) * len(neg), len(pos) * len(neg)


def conc_counts_brute(y, p):
    """総当たりの数え上げ（P-C1 の照合用）。"""
    y, p = list(y), list(p)
    c = n = 0.0
    for i in range(len(y)):
        for j in range(len(y)):
            if y[i] == 1 and y[j] == 0:
                n += 1
                c += 1.0 if p[i] > p[j] else (0.5 if p[i] == p[j] else 0.0)
    return c, int(n)


def within_c(ys, ps):
    """書き手の中の一致度 C = Σ_w 一致_w / Σ_w 組_w（組の数で重みづけ）。組の無い書き手は入らない。
    返り値: (C または None, 組のある書き手の数)。m5 は書き手で層にせず全問いの組で数える。"""
    if "m5" in MUT:
        y = np.concatenate([np.asarray(v) for v in ys]) if ys else np.zeros(0)
        p = np.concatenate([np.asarray(v, dtype=float) for v in ps]) if ps else np.zeros(0)
        c, n = conc_counts(y, p)
        return (c / n if n else None), int(sum(1 for v in ys if 0 < np.sum(v) < len(v)))
    c = n = 0.0
    nw = 0
    for y, p in zip(ys, ps):
        cw, nn = conc_counts(y, p)
        c += cw
        n += nn
        nw += nn > 0
    return (c / n if n else None), nw


def pooled_auc(ys, ps):
    y = np.concatenate([np.asarray(v) for v in ys]) if ys else np.zeros(0)
    p = np.concatenate([np.asarray(v, dtype=float) for v in ps]) if ps else np.zeros(0)
    return auc(y, p)
