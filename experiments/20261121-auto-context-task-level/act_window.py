"""v1（記述用）: 様式の名前を長い窓の割合にして、混合ガウスでまとめる（auto-context-task-level）。

判定には使わない（判断 7・判定に使う案は v2 の `act_hmm.py` だけ）。同じ合成と同じ照合に通し、結果を並べる。
"""

from __future__ import annotations

import math

import numpy as np

import stage1

core = stage1.core
IDLE = core.IDLE


def task_windows(raw: np.ndarray, seams: np.ndarray, n_per: int) -> tuple[np.ndarray, np.ndarray]:
    """3 分の窓を `n_per` 本ずつの作業の窓に割り当てる（ファイルの継ぎ目で必ず切る）。

    戻り値は (各 3 分の窓の作業の窓の番号, 各作業の窓の前に継ぎ目があるか)。
    """
    m = len(raw)
    tw = np.zeros(m, dtype=int)
    starts_seam = []
    cur, count = -1, n_per
    for i in range(m):
        if seams[i] or count >= n_per:
            cur += 1
            count = 0
            starts_seam.append(bool(seams[i]))
        tw[i] = cur
        count += 1
    return tw, np.array(starts_seam, dtype=bool)


def run(raw: np.ndarray, seams: np.ndarray, n_symbols: int, cfg1: dict, cfg: dict, seed: int) -> dict:
    """作業の窓の割合 → 混合ガウス → 平滑化。3 分の窓ごとの作業の名前（観測の無い窓は IDLE）を返す。"""
    n_per = cfg["v1_task_window_windows"]
    tw, tw_seam = task_windows(raw, seams, n_per)
    n_tw = int(tw.max()) + 1 if len(tw) else 0
    feats, few = [], []
    for j in range(n_tw):
        lab = raw[tw == j]
        obs = lab[lab != IDLE]
        few.append(len(obs) < math.ceil(n_per * cfg["v1_min_observed_frac"]))
        cnt = np.array([(obs == s).sum() for s in range(n_symbols)], dtype=float) + cfg["v1_pseudo"]
        ref = int(np.argmax(np.bincount(raw[raw != IDLE], minlength=n_symbols))) if (raw != IDLE).any() else 0
        alr = [math.log(cnt[s] / cnt[ref]) for s in range(n_symbols) if s != ref]
        feats.append(alr + [1.0 - len(obs) / max(len(lab), 1)])
    few = np.array(few, dtype=bool)
    X = np.array(feats, dtype=float).reshape(n_tw, -1)
    lab_tw = np.full(n_tw, IDLE, dtype=int)
    k = 0
    if (~few).sum() >= 2:
        Xs, _ = core.standardize(X[~few])
        if Xs.shape[1] >= 1:
            g = core.select_gmm(Xs, cfg1["k_max"], seed, cfg1["n_init"], cfg1["var_floor"])
            pl, post = core.predict(Xs, g)
            k = post.shape[1]
            lab_tw[~few] = pl
            post_full = np.zeros((n_tw, k))
            post_full[~few] = post
            forced = np.zeros(n_tw + 1, dtype=bool)
            forced[:n_tw] = tw_seam
            forced[n_tw] = True
            lab_tw, _ = core.smooth_labels(lab_tw, post_full, few, forced, cfg["v1_min_run"])
    out = lab_tw[tw] if len(tw) else np.zeros(0, dtype=int)
    out = np.where(raw == IDLE, IDLE, out)
    return {"labels": out, "k": k, "task_windows": n_tw, "few_task_windows": int(few.sum())}
