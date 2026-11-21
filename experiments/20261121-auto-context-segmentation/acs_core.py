"""文脈の量で区間をまとめ、名前を付ける解析の本体（auto-context-segmentation）。

設計は `.steering/20261121-auto-context-segmentation/design.md`（v2 に v1 の 1 点を足した案）。

- 入力は `gse-replay --features` の封筒（特徴行は共有しない・外部へ送らない）。
- 推定や介入の入力にしない（ADR-010 D3）。名前は task-A, task-B, … で、宣言の名前に写し替えない（ADR-012 D3）。
- 依存は numpy だけ（scikit-learn は入れない）。
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# KeyCategory（`anonymize.rs` の as_str）を 5 群に畳む。構成比の次元を減らすため。
CATEGORY_GROUPS: dict[str, str] = {
    "alphabetic": "text",
    "numeric": "text",
    "punctuation": "text",
    "sentence_punctuation": "text",
    "space": "text",
    "backspace": "edit",
    "delete": "edit",
    "navigation": "nav",
    "tab": "nav",
    "enter": "nav",
    "modifier": "modifier",
}
GROUP_ORDER = ["text", "edit", "nav", "modifier", "other"]
# 加法対数比の基準の群（いちばん多いと見込まれる群）。
ALR_REF = "text"
ALR_PSEUDO = 0.5

FEATURE_NAMES = [
    "focus_rate_per_min",
    "pointer_frac",
    "key_rate_per_min",
    "log_pointer_key_ratio",
    "ime_frac",
    "alr_edit",
    "alr_nav",
    "alr_modifier",
    "alr_other",
]
# 「量」の軸（打鍵の多さ・ポインタの多さ）。循環の検査（量の軸だけで再現できるか）に使う。
QUANTITY_FEATURES = ["pointer_frac", "key_rate_per_min"]


@dataclass
class Ticks:
    t_ms: np.ndarray
    keys: np.ndarray
    group_counts: np.ndarray  # (n, 5)
    focus: np.ndarray  # float, nan = 計器なし/判定不能
    pointer_active: np.ndarray  # float 0/1, nan
    ime_on: np.ndarray  # float 0/1, nan


def load_envelope(path: Path) -> Ticks:
    """`--features` の封筒から、この解析が使う列だけを取り出す。"""
    env = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = env["rows"]
    n = len(rows)
    t_ms = np.zeros(n, dtype=np.int64)
    keys = np.zeros(n)
    groups = np.zeros((n, len(GROUP_ORDER)))
    focus = np.full(n, np.nan)
    pointer = np.full(n, np.nan)
    ime = np.full(n, np.nan)
    for i, r in enumerate(rows):
        t_ms[i] = r["t_ms"]
        keys[i] = r["activity"]["keys"]
        ctx = r["context"]
        for cat, c in ctx["cat_counts"].items():
            groups[i, GROUP_ORDER.index(CATEGORY_GROUPS.get(cat, "other"))] += c
        if ctx["focus_transitions"] is not None:
            focus[i] = ctx["focus_transitions"]
        if ctx["pointer_active"] is not None:
            pointer[i] = 1.0 if ctx["pointer_active"] else 0.0
        if ctx["ime_on"] is not None:
            ime[i] = 1.0 if ctx["ime_on"] else 0.0
    return Ticks(t_ms, keys, groups, focus, pointer, ime)


@dataclass
class Windows:
    start_ms: np.ndarray
    end_ms: np.ndarray
    X: np.ndarray  # (m, d) 生の文脈ベクトル（nan を含みうる）
    idle: np.ndarray  # bool


def _nanmean_or_nan(a: np.ndarray) -> float:
    a = a[~np.isnan(a)]
    return float(a.mean()) if a.size else math.nan


def make_windows(ticks: Ticks, window_s: int) -> Windows:
    """重ならない `window_s` 秒の窓に集める。打鍵もポインタも無い窓は無操作（idle）。"""
    n = len(ticks.t_ms)
    m = n // window_s
    starts, ends, rows, idle = [], [], [], []
    for w in range(m):
        sl = slice(w * window_s, (w + 1) * window_s)
        k = ticks.keys[sl]
        p = ticks.pointer_active[sl]
        f = ticks.focus[sl]
        g = ticks.group_counts[sl].sum(axis=0)
        key_total = float(k.sum())
        pointer_secs = float(np.nansum(p))
        minutes = window_s / 60.0
        focus_rate = float(np.nansum(f)) / minutes if not np.all(np.isnan(f)) else math.nan
        pointer_frac = pointer_secs / window_s if not np.all(np.isnan(p)) else math.nan
        ratio = (
            math.log((pointer_secs + 1.0) / (key_total + 1.0))
            if not np.all(np.isnan(p))
            else math.nan
        )
        ref = g[GROUP_ORDER.index(ALR_REF)] + ALR_PSEUDO
        alr = [
            math.log((g[GROUP_ORDER.index(gname)] + ALR_PSEUDO) / ref)
            for gname in GROUP_ORDER
            if gname != ALR_REF
        ]
        rows.append(
            [
                focus_rate,
                pointer_frac,
                key_total / minutes,
                ratio,
                _nanmean_or_nan(ticks.ime_on[sl]),
                *alr,
            ]
        )
        starts.append(int(ticks.t_ms[sl.start]))
        ends.append(int(ticks.t_ms[sl.stop - 1]) + 1000)
        idle.append(key_total == 0 and pointer_secs == 0)
    return Windows(
        np.array(starts, dtype=np.int64),
        np.array(ends, dtype=np.int64),
        np.array(rows, dtype=float).reshape(m, len(FEATURE_NAMES)),
        np.array(idle, dtype=bool),
    )


def standardize(X: np.ndarray) -> tuple[np.ndarray, list[int]]:
    """人の中で標準化する。全部 nan・分散 0 の列は落とし、残りの nan は列の中央値で埋める。"""
    keep = []
    cols = []
    for j in range(X.shape[1]):
        c = X[:, j]
        ok = ~np.isnan(c)
        if ok.sum() < 2:
            continue
        med = float(np.median(c[ok]))
        c = np.where(ok, c, med)
        sd = float(c.std())
        if sd < 1e-9:
            continue
        cols.append((c - c.mean()) / sd)
        keep.append(j)
    if not cols:
        return np.zeros((X.shape[0], 0)), []
    return np.stack(cols, axis=1), keep


@dataclass
class Gmm:
    weights: np.ndarray
    means: np.ndarray
    variances: np.ndarray
    loglik: float
    bic: float

    @property
    def k(self) -> int:
        return len(self.weights)


def _log_resp(X: np.ndarray, g: Gmm) -> tuple[np.ndarray, np.ndarray]:
    d = X.shape[1]
    diff = X[:, None, :] - g.means[None, :, :]
    log_pdf = -0.5 * (
        np.sum(diff**2 / g.variances[None, :, :], axis=2)
        + np.sum(np.log(g.variances), axis=1)[None, :]
        + d * math.log(2 * math.pi)
    )
    a = log_pdf + np.log(g.weights)[None, :]
    mx = a.max(axis=1, keepdims=True)
    lse = mx + np.log(np.exp(a - mx).sum(axis=1, keepdims=True))
    return a - lse, lse[:, 0]


def fit_gmm(X: np.ndarray, k: int, rng: np.random.Generator, n_init: int, max_iter: int = 300,
            reg: float = 1e-3) -> Gmm:
    """対角共分散の混合ガウスを EM で当てる。初期値を変えて `n_init` 回走らせ、尤度の高いものを採る。"""
    n, d = X.shape
    best: Gmm | None = None
    for _ in range(n_init):
        idx = rng.choice(n, size=k, replace=False)
        means = X[idx].copy()
        variances = np.tile(X.var(axis=0) + reg, (k, 1))
        weights = np.full(k, 1.0 / k)
        g = Gmm(weights, means, variances, -math.inf, math.inf)
        prev = -math.inf
        for _ in range(max_iter):
            log_r, lse = _log_resp(X, g)
            ll = float(lse.sum())
            r = np.exp(log_r)
            nk = r.sum(axis=0) + 1e-10
            g.weights = nk / n
            g.means = (r.T @ X) / nk[:, None]
            diff2 = (X[:, None, :] - g.means[None, :, :]) ** 2
            g.variances = np.einsum("nk,nkd->kd", r, diff2) / nk[:, None] + reg
            if ll - prev < 1e-6 * abs(ll):
                break
            prev = ll
        _, lse = _log_resp(X, g)
        g.loglik = float(lse.sum())
        n_params = k * 2 * d + (k - 1)
        g.bic = -2.0 * g.loglik + n_params * math.log(n)
        if best is None or g.loglik > best.loglik:
            best = g
    assert best is not None
    return best


def select_gmm(X: np.ndarray, k_max: int, seed: int, n_init: int, var_floor: float = 1e-3) -> Gmm:
    """k = 1..k_max から BIC が最小のものを選ぶ（k = 1 を許す）。"""
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    best: Gmm | None = None
    for k in range(1, min(k_max, n) + 1):
        g = fit_gmm(X, k, rng, n_init, reg=var_floor)
        if best is None or g.bic < best.bic:
            best = g
    assert best is not None
    return best


def predict(X: np.ndarray, g: Gmm) -> tuple[np.ndarray, np.ndarray]:
    log_r, _ = _log_resp(X, g)
    post = np.exp(log_r)
    return post.argmax(axis=1), post


IDLE = -1


def smooth_labels(labels: np.ndarray, post: np.ndarray, idle: np.ndarray, forced: np.ndarray,
                  min_run: int) -> tuple[np.ndarray, int]:
    """名前の列に最小の滞在長を課す。

    - 無操作の窓は `IDLE` のまま動かさない。
    - `forced[i]` が真なら、窓 i の前に強制の境界がある（吸収はこれを越えない）。
    - `min_run` より短い連続は、前後が同じ名前ならそれに、違えば事後確率の平均が高い方に吸収する。
    戻り値は平滑化した列と、吸収した連続の数。
    """
    lab = np.where(idle, IDLE, labels).astype(int)
    absorbed = 0
    for _ in range(len(lab) + 1):
        runs = _runs(lab, forced)
        changed = False
        for ri, (s, e, v) in enumerate(runs):
            if v == IDLE or e - s >= min_run:
                continue
            left = runs[ri - 1] if ri > 0 and not forced[s] else None
            right = runs[ri + 1] if ri + 1 < len(runs) and not forced[e] else None
            cands = [r for r in (left, right) if r is not None and r[2] != IDLE]
            if not cands:
                continue
            if len(cands) == 2 and cands[0][2] == cands[1][2]:
                target = cands[0][2]
            elif len(cands) == 1:
                target = cands[0][2]
            else:
                scores = [float(post[s:e, c[2]].mean()) for c in cands]
                target = cands[int(np.argmax(scores))][2]
            lab[s:e] = target
            absorbed += 1
            changed = True
            break
        if not changed:
            break
    return lab, absorbed


def _runs(lab: np.ndarray, forced: np.ndarray) -> list[tuple[int, int, int]]:
    runs = []
    s = 0
    for i in range(1, len(lab) + 1):
        if i == len(lab) or lab[i] != lab[s] or forced[i]:
            runs.append((s, i, int(lab[s])))
            s = i
    return runs


def forced_boundaries(win: Windows, idle_gap_s: int, seams: np.ndarray | None = None) -> np.ndarray:
    """無操作が `idle_gap_s` 以上続いた連続の、始まりの窓と終わった直後の窓に強制の境界を立てる。

    長さは窓の長さの合計で測る（窓と窓の間の記録の無い時間を数えない）。無操作の連続は
    ファイルの継ぎ目（`seams[i]` が真なら窓 i の前）で切る。戻り値は長さ m + 1（`forced[m]` は番兵で常に真）。
    """
    m = len(win.idle)
    forced = np.zeros(m + 1, dtype=bool)
    forced[m] = True
    dur = (win.end_ms - win.start_ms) / 1000.0
    i = 0
    while i < m:
        if win.idle[i]:
            j = i + 1
            while j < m and win.idle[j] and not (seams is not None and seams[j]):
                j += 1
            if float(dur[i:j].sum()) >= idle_gap_s:
                forced[i] = True
                if j < m:
                    forced[j] = True
            i = j
        else:
            i += 1
    return forced


def boundaries_of(lab: np.ndarray, starts: np.ndarray) -> list[int]:
    """名前が変わった窓の開始時刻（無操作との出入りも含む）。"""
    return [int(starts[i]) for i in range(1, len(lab)) if lab[i] != lab[i - 1]]


def name_labels(lab: np.ndarray, durations_s: np.ndarray) -> dict[int, str]:
    """合計時間の多い順に task-A, task-B, … を付ける（無操作は idle）。"""
    totals: dict[int, float] = {}
    for v, d in zip(lab, durations_s):
        if v != IDLE:
            totals[int(v)] = totals.get(int(v), 0.0) + float(d)
    order = sorted(totals, key=lambda v: (-totals[v], v))
    names = {v: f"task-{chr(ord('A') + i)}" for i, v in enumerate(order)}
    names[IDLE] = "idle"
    return names


# ---------------------------------------------------------------------------
# 一致の指標（numpy で書く）
# ---------------------------------------------------------------------------

def _contingency(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    _, ai = np.unique(a, return_inverse=True)
    _, bi = np.unique(b, return_inverse=True)
    c = np.zeros((ai.max() + 1, bi.max() + 1))
    np.add.at(c, (ai, bi), 1)
    return c


def ari(a: np.ndarray, b: np.ndarray) -> float:
    c = _contingency(np.asarray(a), np.asarray(b))
    n = c.sum()
    comb = lambda x: x * (x - 1) / 2.0  # noqa: E731
    sum_ij = comb(c).sum()
    sa = comb(c.sum(axis=1)).sum()
    sb = comb(c.sum(axis=0)).sum()
    expected = sa * sb / comb(n) if n > 1 else 0.0
    mx = 0.5 * (sa + sb)
    if mx == expected:
        return 1.0
    return float((sum_ij - expected) / (mx - expected))


def nmi(a: np.ndarray, b: np.ndarray) -> float:
    """算術平均で正規化した相互情報量。どちらかが 1 値だけなら 0。"""
    c = _contingency(np.asarray(a), np.asarray(b))
    n = c.sum()
    if n == 0:
        return 0.0
    p = c / n
    pa = p.sum(axis=1)
    pb = p.sum(axis=0)
    nz = p > 0
    mi = float((p[nz] * np.log(p[nz] / np.outer(pa, pb)[nz])).sum())
    ha = float(-(pa[pa > 0] * np.log(pa[pa > 0])).sum())
    hb = float(-(pb[pb > 0] * np.log(pb[pb > 0])).sum())
    if ha == 0 or hb == 0:
        return 0.0
    return mi / (0.5 * (ha + hb))


def boundary_f1(pred: list[int], truth: list[int], tol_ms: int) -> tuple[float, float, float]:
    """許容 `tol_ms` の中で 1 対 1 に対応づけた境界の適合率・再現率・F1。"""
    pred = sorted(pred)
    truth = sorted(truth)
    used = [False] * len(pred)
    hit = 0
    for t in truth:
        best = None
        for i, p in enumerate(pred):
            if not used[i] and abs(p - t) <= tol_ms and (best is None or abs(p - t) < abs(pred[best] - t)):
                best = i
        if best is not None:
            used[best] = True
            hit += 1
    precision = hit / len(pred) if pred else (1.0 if not truth else 0.0)
    recall = hit / len(truth) if truth else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    return precision, recall, f1


def block_permutation_pvalue(labels: np.ndarray, ref: np.ndarray, blocks: np.ndarray, n_perm: int,
                             rng: np.random.Generator) -> tuple[float, float]:
    """`ref` の値をブロックごとに入れ替えた帰無分布に対する NMI の片側 p 値（観測値, p）。

    `blocks[i]` は窓 i のブロックの番号で、1 つのブロックの中では `ref` が一定であること。
    ブロックの長さは保ち、各ブロックに付いた値だけを並べ替える。ブロックが少ないと、完全に一致していても
    小さい p には届かない（呼び出し側が `ref` を `ref` 自身と照合して確かめる・decisions.md 判断 14・15）。
    """
    labels, ref, blocks = np.asarray(labels), np.asarray(ref), np.asarray(blocks)
    obs = nmi(labels, ref)
    ids, inv = np.unique(blocks, return_inverse=True)
    if len(ids) < 2:
        return obs, math.nan
    vals = np.empty(len(ids), dtype=ref.dtype)
    for j in range(len(ids)):
        v = np.unique(ref[inv == j])
        if len(v) != 1:
            raise ValueError("ref must be constant within a block")
        vals[j] = v[0]
    ge = 0
    for _ in range(n_perm):
        if nmi(labels, rng.permutation(vals)[inv]) >= obs:
            ge += 1
    return obs, (1 + ge) / (1 + n_perm)


@dataclass
class Result:
    windows: Windows
    kept_features: list[str]
    gmm_k: int
    raw_labels: np.ndarray
    labels: np.ndarray
    names: dict[int, str]
    absorbed_runs: int
    boundaries_ms: list[int] = field(default_factory=list)


def segment_person(win: Windows, cfg: dict, seed: int, seams: np.ndarray | None = None) -> Result:
    """1 人ぶんの窓（複数ファイルをつないだもの）をまとめ、平滑化し、名前を付ける。

    `seams`（`concat_windows` の戻り値）は、ファイルの継ぎ目で時間が飛ぶことを平滑化に伝えるだけである。
    継ぎ目は検出した境界としては数えない（O1 は宣言が変わるとファイルが分かれるので、
    数えると宣言の境界をそのまま写してしまう）。まとめ自体はファイルを知らない。
    """
    active = ~win.idle
    m = len(win.idle)
    Xs, keep = standardize(win.X[active])
    raw = np.full(m, IDLE, dtype=int)
    post_full = np.zeros((m, 1))
    k = 0
    if Xs.shape[0] >= 2 and Xs.shape[1] >= 1:
        g = select_gmm(Xs, cfg["k_max"], seed, cfg["n_init"], cfg["var_floor"])
        k = g.k
        _, post = predict(Xs, g)
        k = post.shape[1]
        raw[active] = post.argmax(axis=1)
        post_full = np.zeros((m, k))
        post_full[active] = post
    elif Xs.shape[0] >= 1:
        k = 1
        raw[active] = 0
        post_full = np.ones((m, 1))
    forced = forced_boundaries(win, cfg["idle_gap_s"], seams)
    barrier = forced | seams if seams is not None else forced
    smoothed, absorbed = smooth_labels(raw, post_full, win.idle, barrier, cfg["min_run_windows"])
    durations = (win.end_ms - win.start_ms) / 1000.0
    names = name_labels(smoothed, durations)
    seam_ms = {int(win.start_ms[i]) for i in range(1, m) if seams is not None and seams[i]}
    bnd = sorted((set(boundaries_of(smoothed, win.start_ms)) | {
        int(win.start_ms[i]) for i in range(1, m) if forced[i]
    }) - seam_ms)
    return Result(win, [FEATURE_NAMES[j] for j in keep], k, raw, smoothed, names, absorbed, bnd)


def concat_windows(parts: list[Windows]) -> tuple[Windows, np.ndarray, dict]:
    """ファイルごとの窓を時刻の順につなぐ。戻り値は (窓, 継ぎ目の印, 重なりの数)。

    O1 の記録では、次のファイルが始まった後も前のファイルに feat 行が書かれ続けることがあり、
    グリッドの右端は feat 行まで伸びるので、ファイルの窓が時間で重なる（decisions.md 判断 17）。
    時刻の順に並べ、前のファイルの窓のうち次のファイルの最初の窓より後ろにかかるものを落とす。
    落とした窓の数と、そのうち操作のあった（無操作でない）窓の数を返す。
    """
    parts = sorted((p for p in parts if len(p.idle)), key=lambda p: int(p.start_ms[0]))
    kept: list[Windows] = []
    dropped = dropped_active = 0
    for i, p in enumerate(parts):
        if i + 1 < len(parts):
            nxt = int(parts[i + 1].start_ms[0])
            keep = p.end_ms <= nxt
            dropped += int((~keep).sum())
            dropped_active += int((~keep & ~p.idle).sum())
            p = Windows(p.start_ms[keep], p.end_ms[keep], p.X[keep], p.idle[keep])
        if len(p.idle):
            kept.append(p)
    starts = np.concatenate([p.start_ms for p in kept]) if kept else np.zeros(0, dtype=np.int64)
    ends = np.concatenate([p.end_ms for p in kept]) if kept else np.zeros(0, dtype=np.int64)
    X = np.concatenate([p.X for p in kept]) if kept else np.zeros((0, len(FEATURE_NAMES)))
    idle = np.concatenate([p.idle for p in kept]) if kept else np.zeros(0, dtype=bool)
    seams = np.zeros(len(idle) + 1, dtype=bool)
    off = 0
    for p in kept:
        seams[off] = True
        off += len(p.idle)
    seams[len(idle)] = True
    if len(starts) > 1 and np.any(starts[1:] < ends[:-1]):
        raise ValueError("windows still overlap after trimming (a file starts inside an earlier file's window)")
    return Windows(starts, ends, X, idle), seams, {"dropped_windows": dropped, "dropped_active_windows": dropped_active}
