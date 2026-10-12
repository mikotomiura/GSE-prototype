"""Labels and the baseline models of the rhythm stage desk check: model A (as in EH1) and model A_speed.

Model A (presence_features, presence_features_long) is copied unchanged from
experiments/20261010-portrait-eh1-round5/scripts/portrait.py. Model A_speed adds the five speed quantities
of design 1.5 (.steering/20261012-rhythm-stage-desk-check/design.md). Neither reads the F series, so the
pilot 0 (design 3.0) needs no gse-replay: only the press times and the segment labels of labels/*.npz.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

STALL_CODES = (1, 3)
LABELS = ("L300", "L60", "L1800")


@dataclass
class Trace:
    sid: str
    duration_s: int
    presses: np.ndarray  # press times in seconds (float, sorted); the key kind is never read
    active: np.ndarray  # bool per second: at least one press in [k, k+1)
    seg: np.ndarray  # segment code per second (the labels)


def load_trace(work: Path, sid: str) -> Trace:
    """As portrait.load_session, without the F series."""
    lab = np.load(work / "labels" / f"{sid}.npz")
    dur = int(lab["duration_s"])
    presses = np.sort(lab["presses_ms"].astype(np.float64) / 1000.0)
    active = np.zeros(dur, dtype=bool)
    idx = presses.astype(np.int64)
    active[idx[idx < dur]] = True
    return Trace(sid, dur, presses, active, lab["seg"].astype(np.int8))


def p_sids(work: Path) -> list[str]:
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    return [m["sid"] for m in manifest if m["set"] == "P"]


# ---------------------------------------------------------------------------
# Model A (copied from EH1 round 5 portrait.py, unchanged)
# ---------------------------------------------------------------------------

def presence_features(sess: Trace, cfg: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Model A features, labels and the active-second count per 60 s window."""
    ws = cfg["e13"]["window_s"]
    n_w = sess.duration_s // ws
    act = sess.active[: n_w * ws].reshape(n_w, ws)
    act_n = act.sum(axis=1).astype(float)
    p = sess.presses
    feats = np.zeros((n_w, 5 + 3 + 3))
    labels = np.zeros(n_w, dtype=int)
    stall = np.isin(sess.seg, STALL_CODES)
    for w in range(n_w):
        s, e = w * ws, (w + 1) * ws
        lags = [act_n[w - k] if w - k >= 0 else 0.0 for k in range(5)]
        inwin = p[(p >= s) & (p < e)]
        pts = np.concatenate([[s], inwin, [e]])
        g = np.diff(pts)
        before = p[p < e]
        since = float(e - before[-1]) if len(before) else float(e)
        last15 = float(sess.active[max(0, e - 900) : e].sum())
        feats[w] = lags + [g.max(), float((g >= 2).sum()), float((g >= 10).sum()), since, last15, float(e)]
        labels[w] = int(stall[s:e].mean() >= 0.5)
    return feats, labels, act_n


def presence_features_long(sess: Trace, cfg: dict, L: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """L300 / L1800 (round 2 design 1.4, round 3 design 1.5): per 60 s window ending at e, the presence pattern
    of seconds [e - L, e) that model A300 / A1800 adds to model A, the label of that span, its active-second
    count (the null strata), and which windows have a full span (e >= L)."""
    ws = cfg["e13"]["window_s"]
    n_w = sess.duration_s // ws
    p = sess.presses
    stall = np.isin(sess.seg, STALL_CODES)
    extra = np.zeros((n_w, 4))
    labels = np.zeros(n_w, dtype=int)
    act_n = np.zeros(n_w)
    valid = np.zeros(n_w, dtype=bool)
    for w in range(n_w):
        e = (w + 1) * ws
        s = e - L
        if s < 0:
            continue
        valid[w] = True
        inspan = p[(p >= s) & (p < e)]
        g = np.diff(np.concatenate([[s], inspan, [e]]))
        act_n[w] = float(sess.active[s:e].sum())
        extra[w] = [g.max(), float((g >= 2).sum()), float((g >= 10).sum()), act_n[w]]
        labels[w] = int(stall[s:e].mean() >= 0.5)
    return extra, labels, act_n, valid


# ---------------------------------------------------------------------------
# Model A_speed (design 1.5)
# ---------------------------------------------------------------------------

def speed5(presses: np.ndarray, s: float, e: float, sp: dict) -> list[float]:
    """The five speed quantities of the span [s, e) (design 1.5), from press times in seconds:
    1 the number of presses; 2 the median and 3 the interquartile range of the press-to-press intervals below
    short_ms (2000 ms and 0 when there is none); 4 the mean length of the runs of presses whose intervals are
    below run_ms (a lone press is a run of 1, as F4 counts it; 0 with no press); 5 the presses of the final
    last_s seconds. Only presses inside the span count (an interval needs both of its presses inside)."""
    p = presses[(presses >= s) & (presses < e)]
    n = len(p)
    d = np.diff(p) * 1000.0
    short = d[d < sp["short_ms"]]
    if len(short):
        med = float(np.median(short))
        q75, q25 = np.percentile(short, [75, 25])
        iqr = float(q75 - q25)
    else:
        med, iqr = float(sp["short_ms"]), 0.0
    if n:
        breaks = int((d >= sp["run_ms"]).sum())
        mean_run = n / (breaks + 1)  # the runs partition the presses
    else:
        mean_run = 0.0
    last = float(((p >= e - sp["last_s"]) & (p < e)).sum())
    return [float(n), med, iqr, mean_run, last]


def window_speed(sess: Trace, cfg: dict) -> np.ndarray:
    """Per 60 s window: the five quantities of the window and quantities 1 and 2 of each of the `lags` earlier
    windows (a window before the session start has 0 presses and quantity 2 = short_ms). Shape (n_w, 5 + 2 lags)."""
    ws = cfg["e13"]["window_s"]
    sp = cfg["speed"]
    n_w = sess.duration_s // ws
    cur = np.array([speed5(sess.presses, w * ws, (w + 1) * ws, sp) for w in range(n_w)]).reshape(n_w, 5)
    parts = [cur]
    empty = np.array([0.0, float(sp["short_ms"])])
    for k in range(1, sp["lags"] + 1):
        lag = np.tile(empty, (n_w, 1))
        lag[k:] = cur[: n_w - k, :2]
        parts.append(lag)
    return np.hstack(parts)


def span_speed(sess: Trace, cfg: dict, L: int) -> np.ndarray:
    """Per 60 s window ending at e: the five quantities of [e - L, e) (zeros for windows without a full span,
    which no label uses)."""
    ws = cfg["e13"]["window_s"]
    n_w = sess.duration_s // ws
    out = np.zeros((n_w, 5))
    for w in range(n_w):
        e = (w + 1) * ws
        if e - L >= 0:
            out[w] = speed5(sess.presses, e - L, e, cfg["speed"])
    return out


def tables(work: Path, sids: list[str], cfg: dict) -> dict:
    """Per label: model A (XA), model A_speed (XS), labels (Y), groups (G = session index), the null strata,
    and the rows the label uses, built as EH1 round 5 checks.e13_labels builds model A.
    A_speed (design 1.5): L60 = A + the window's five quantities + quantities 1 and 2 of the four earlier windows;
    L300 / L1800 = A300 / A1800 + the same window quantities + the five quantities of the span."""
    spans = {"L300": cfg["e13"]["long_s"], "L1800": cfg["e13"]["long_s_1800"]}
    edges = {"L300": cfg["e13"]["strata_edges_long"], "L1800": cfg["e13"]["strata_edges_1800"]}
    parts: dict[str, list] = {"XA": [], "WS": [], "Y": [], "ACT": [], "G": []}
    long_parts = {t: {"EX": [], "SS": [], "YL": [], "ACTL": [], "V": []} for t in spans}
    for i, sid in enumerate(sids):
        s = load_trace(work, sid)
        fa, lab, act_n = presence_features(s, cfg)
        for k, v in zip(("XA", "WS", "Y", "ACT", "G"), (fa, window_speed(s, cfg), lab, act_n, np.full(len(lab), i))):
            parts[k].append(v)
        for t, L in spans.items():
            ex, labl, actl, valid = presence_features_long(s, cfg, L)
            for k, v in zip(("EX", "SS", "YL", "ACTL", "V"), (ex, span_speed(s, cfg, L), labl, actl, valid)):
                long_parts[t][k].append(v)
    XA, WS = np.vstack(parts["XA"]), np.vstack(parts["WS"])
    Y, ACT, G = (np.concatenate(parts[k]) for k in ("Y", "ACT", "G"))
    e60 = cfg["e13"]["strata_edges"]
    out = {"L60": {"XA": XA, "XS": np.hstack([XA, WS]), "Y": Y, "G": G, "strata": np.digitize(ACT, e60[1:-1]),
                   "rows": np.ones(len(Y), dtype=bool), "G_all": G}}
    for t in spans:
        lp = long_parts[t]
        EX, SS = np.vstack(lp["EX"]), np.vstack(lp["SS"])
        YL, ACTL, V = (np.concatenate(lp[k]) for k in ("YL", "ACTL", "V"))
        xa = np.hstack([XA, EX])
        out[t] = {"XA": xa[V], "XS": np.hstack([xa, WS, SS])[V], "Y": YL[V], "G": G[V],
                  "strata": np.digitize(ACTL[V], edges[t][1:-1]), "rows": V, "G_all": G}
    return out
