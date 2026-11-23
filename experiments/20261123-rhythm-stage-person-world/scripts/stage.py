"""The rhythm stage of the desk check, relative timing (plan D): keystrokes -> two drawing parameters per frame.

Design: .steering/20261122-rhythm-stage-relative-timing/design.md 1.2, 1.5 (plan D and its PC-stall). Copied from
experiments/20261015-rhythm-stage-speed-shape-world/scripts/stage.py (the file of 1cf9fcb9); the anchors, PC1, PC-corr,
the PC-stall and PC0 of the anchors and the window features are unchanged (selftest.py compares them with that file).
Removed: the L1800 controls (PC1-1800, PCl-) and the r-side controls (PCrl-, PCrv-): this task uses L300 only and no
r-side control (design 1.6). The candidates are six: plan D's two (D-run-hold-sec, D-all-hold-sec) and four anchors
(S-raw-hold-sec, S-raw-hold-sub, S-rank-hold-sec, S-rank-hold-sub; decisions 5).

Every series is taken at 10 Hz (point j at t = j / 10 s) and has two parameters in [0, 1]: the amplitude a and the
tempo r. An anchor S-<mapping>-<stop>-<res> is built in this order: the drive values (res) -> the mapping -> the
behaviour while stopped -> clip to [0, 1]. Every candidate is causal: the value at t is fixed by the input up to t.

Plan D (design 1.2): D-<set>-hold-sec, set "run" or "all".
- Input: the press times (presses) and the active seconds (active, for the stop) only; never keys, f1 or f4
  (StageInput records what was read; selftest checks it).
- Intervals: the differences of consecutive presses in whole ms; "all" holds those with 0 < interval < 2000 ms (an
  interval of 0 ms has no ratio and is left out). The interval ends at its second press.
- The window of second k: the last N_WIN = 40 "all" intervals whose end lies in [1000 (k + 1 - 300), 1000 (k + 1)) ms
  (MAX_AGE_S = 300; an end exactly 300 s before t = k + 1 is in, 1 ms earlier is out).
- The set: "all" = every interval of the window; "run" = those below RUN_K = 3 times the median of the window's
  intervals (exactly 3 times is out).
- a = clip(log(p90 / p10) / log 10, 0, 1) over the set (numpy's linear percentiles); held from the previous second
  when the set has fewer than MIN_IVL = 8 intervals.
- r = clip(median of |log(I_i / I_(i-1))| / 1.0, 0, 1) over the pairs of intervals adjacent in the press sequence
  (consecutive indices) that are both in the window's set; held when there are fewer than MIN_PAIRS = 5 pairs.
- Both start at 0.5. Second k is used from t = k + 1 (points j with j // 10 - 1 = k), as res=sec. Stopped as res=sec
  (no press in the second used nor in the one before); the stop is hold (the value at the last moving point, 0 when
  the session starts stopped). No wobble.
- PC-stall of a D candidate (design 1.5): a of second k is the block value of block k // 60 (blocks of the anchors'
  PC-stall: 60 s, q = the stall share of the preceding 300 s, q if U < lam else N), held when the candidate's set
  has fewer than MIN_IVL intervals; r is 0.5 (held under MIN_PAIRS, so 0.5 throughout). Then the same points, stop and
  clip as the candidate. PC0- is the same at lam = 0.

Person controls (.steering/20261123-rhythm-stage-person-world/design.md 1.5, 1.8; added after the copied file; the names
above and their output are unchanged, selftest.py compares them with the shape world's file):
- (5) PC1-id: a = Phi(z'_p), the person's own standard normal from a stream of its own (derive_rng(seed, "pcid", p)),
  on every second; r = 0.5. PCp-<candidate> (lam): per 60 s block, the block value is Phi(z'_p) if U < lam else N (the
  PC-stall's U and N); the rest as PCs-. PC0-id-<candidate> (lam): the signal is Phi(e'_s), one value per session
  (derive_rng(seed, "pcid0", i)), not tied to the person. r is 0.5 throughout.
- (6) PC1-pers: per block, a = 0.5 + s_p (q - 0.5) with q the stall share of the preceding 300 s and s_p = +-1 per person
  (derive_rng(seed, "pcsign"): half of the persons each); r = 0.5. PCps-<candidate> (lam): the same signal where
  U < lam. PC0p-<candidate> (lam): s_p = +1 for everybody (this is the PC-stall's picture).
These read the session's id (to get the person) and the labels (q) only; never the generator's latent values.

The seams d_inputs, d_window_bounds, d_select and d_spread are separate functions so that selftest.py can put the
mutants of design 3.7 in their place.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.signal import lfilter
from scipy.special import ndtr

import gen_sessions as gs

HZ = 10
DT = 1.0 / HZ
WIN_POINTS = 600  # a 60 s window
STOP_MS = 2000
K_MAX = 150.0
F1_LO, F1_HI = 80.0, 600.0
TAU_S = 0.5
Z = 2.5
SMOOTH_TAU_S = 30.0
RANK_WARM_S = 60
RANK_LEVELS = 1000
JIT_PHI = 0.95
JIT_SD = 0.1
DECAY_TAU_S = 60.0
GROUND_EPS = 0.02
CHANGE_EPS = 1e-6
PC_BLOCK_S = 60
PC_SPAN_S = 300
PC1_SPAN_S = 60
JITTER_TAG = 31
PC_TAG = 37

# plan D (design 1.2 and section 9 items 3-6)
D_SETS = ("run", "all")
N_WIN = 40
MAX_AGE_S = 300
RUN_K = 3.0
SPREAD_SCALE = math.log(10.0)
IRREG_SCALE = 1.0
MIN_IVL = 8
MIN_PAIRS = 5
D_INIT = 0.5

MAPPINGS = ("raw", "smooth", "rank", "jitter")
STOPS = ("hold", "decay", "ground")
RESOLUTIONS = ("sec", "sub")
ALLOWED_INPUT = ("presses", "active", "keys", "f1", "f4")
D_INPUT = ("presses", "active")  # design 1.2: what plan D reads
STALL_CODES = (1, 3)
SLOTS = 6  # sessions per person (config person.sessions_per_person; checked by selftest.py)
N_PERSONS = 40
PERSON_NAMES = ("PC1-id", "PCp-", "PC0-id-", "PC1-pers", "PCps-", "PC0p-")
FEAT_NAMES = tuple(f"{p}_{q}" for p in ("a", "r") for q in ("mean", "sd", "p10", "p50", "p90", "ground", "absdiff",
                                                             "ac1", "end", "since_change"))
D_CANDIDATES = ("D-run-hold-sec", "D-all-hold-sec")
ANCHORS = ("S-raw-hold-sec", "S-raw-hold-sub", "S-rank-hold-sec", "S-rank-hold-sub")


def candidates() -> list[str]:
    """design 0: the six candidates (plan D's two, then the four anchors)."""
    return list(D_CANDIDATES) + list(ANCHORS)


def parse(name: str) -> tuple[str, str, str]:
    _, m, s, r = name.split("-")
    assert m in MAPPINGS and s in STOPS and r in RESOLUTIONS, name
    return m, s, r


def d_parse(name: str) -> str:
    """The set of a plan D name D-<set>-hold-sec."""
    head, dset, stop, res = name.split("-")
    if head != "D" or dset not in D_SETS or stop != "hold" or res != "sec":
        raise ValueError(name)
    return dset


# ---------------------------------------------------------------------------
# The session and the closed input
# ---------------------------------------------------------------------------

@dataclass
class Session:
    sid: str
    duration_s: int
    presses: np.ndarray  # press times in seconds (whole ms / 1000, sorted)
    active: np.ndarray  # bool per second: a press in [k, k + 1)
    seg: np.ndarray  # segment code per second: the labels, read only by the controls and the checks
    feat: dict  # column -> float per second (NaN where gse-replay emitted no tick)
    key_seed: int


def load_session(work: Path, m: dict) -> Session:
    lab = np.load(work / "labels" / f"{m['sid']}.npz")
    feat = np.load(work / "feat" / f"{m['sid']}.npz")
    dur = int(lab["duration_s"])
    presses = np.sort(lab["presses_ms"].astype(np.float64) / 1000.0)
    active = np.zeros(dur, dtype=bool)
    idx = presses.astype(np.int64)
    active[idx[idx < dur]] = True
    return Session(m["sid"], dur, presses, active, lab["seg"].astype(np.int8),
                   {c: feat[c] for c in ("f1", "f3", "f4", "f5", "f6", "p_stuck", "keys")}, int(m["key_seed"]))


class StageInput:
    """The only view of a session the mappings get: the columns of ALLOWED_INPUT. Any other name raises. The names
    read are recorded in .read (design 3.7: plan D reads presses and active only)."""

    def __init__(self, duration_s: int, cols: dict):
        self.duration_s = int(duration_s)
        self._cols = {k: cols[k] for k in ALLOWED_INPUT}
        self.read: set = set()

    def __getitem__(self, name: str) -> np.ndarray:
        if name not in ALLOWED_INPUT:
            raise KeyError(f"design 1.2: the stage does not read {name!r}")
        self.read.add(name)
        return self._cols[name]


def stage_input(sess: Session) -> StageInput:
    return StageInput(sess.duration_s, {"presses": sess.presses, "active": sess.active, "keys": sess.feat["keys"],
                                        "f1": sess.feat["f1"], "f4": sess.feat["f4"]})


# ---------------------------------------------------------------------------
# Drive values and the stop of the anchors (unchanged)
# ---------------------------------------------------------------------------

def hold_nan(x: np.ndarray, init: float = 0.0) -> np.ndarray:
    """Each NaN takes the previous finite value (init before the first one)."""
    idx = np.where(np.isfinite(x), np.arange(len(x)), -1)
    np.maximum.accumulate(idx, out=idx)
    return np.where(idx >= 0, x[np.maximum(idx, 0)], init)


def interval_to_u(ms: np.ndarray) -> np.ndarray:
    """1 - clip((ms - 80) / (600 - 80), 0, 1): a short interval is near 1."""
    return 1.0 - np.clip((ms - F1_LO) / (F1_HI - F1_LO), 0.0, 1.0)


def drive_sec(inp: StageInput) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """res=sec: (u_a, u_r, stopped) at 10 Hz from keys and f1 of the last completed second."""
    dur = inp.duration_s
    n = dur * HZ
    ua_s = hold_nan(np.minimum(1.0, inp["keys"] / K_MAX))
    f1 = inp["f1"]
    # gse-replay's F1 is 0.0 when the 30 s window holds no interval; that second's tempo is 0. NaN still holds.
    ur_s = hold_nan(np.where(f1 == 0, 0.0, interval_to_u(f1)))
    k = np.arange(n) // HZ - 1  # the second used at point j
    kk = np.maximum(k, 0)
    known = k >= 0
    ua = np.where(known, ua_s[kk], 0.0)
    ur = np.where(known, ur_s[kk], 0.0)
    act = inp["active"]
    prev = np.where(k >= 1, act[np.maximum(k - 1, 0)], False)
    stopped = ~known | (~act[kk] & ~prev)
    return ua, ur, stopped


def drive_sub(inp: StageInput) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """res=sub: (u_a, u_r, stopped) at 10 Hz from the press times."""
    n = inp.duration_s * HZ
    pm = np.rint(np.asarray(inp["presses"]) * 1000.0).astype(np.int64)
    if len(pm) == 0:  # no press: no drive and stopped everywhere
        return np.zeros(n), np.zeros(n), np.ones(n, dtype=bool)
    jj = -(-pm // 100)  # the first point j with 100 j >= m
    keep = jj < n
    w = np.exp(-((jj[keep] * 100 - pm[keep]) / 1000.0) / TAU_S)
    x = np.bincount(jj[keep], weights=w, minlength=n)[:n]
    s = lfilter([1.0], [1.0, -math.exp(-DT / TAU_S)], x)
    ua = np.minimum(1.0, s / Z)
    t_ms = np.arange(n, dtype=np.int64) * 100
    cnt = np.searchsorted(pm, t_ms, side="right")  # presses at or before t
    ivl = np.full(len(pm), np.iinfo(np.int64).max, dtype=np.int64)
    ivl[1:] = np.diff(pm)
    last_ivl = np.where(cnt >= 2, ivl[np.maximum(cnt - 1, 0)], np.iinfo(np.int64).max)
    ur = np.where(last_ivl < STOP_MS, interval_to_u(last_ivl.astype(np.float64)), 0.0)
    last = np.where(cnt > 0, pm[np.maximum(cnt - 1, 0)], 0)
    stopped = (cnt == 0) | (t_ms - last >= STOP_MS)
    return ua, ur, stopped


def drive(inp: StageInput, res: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return drive_sec(inp) if res == "sec" else drive_sub(inp)


# ---------------------------------------------------------------------------
# Mappings, stop behaviours and the wobble (unchanged)
# ---------------------------------------------------------------------------

def ema(x: np.ndarray, tau_s: float) -> np.ndarray:
    """y_j = y_{j-1} + alpha (x_j - y_{j-1}), y_{-1} = 0, alpha = 1 - exp(-dt / tau)."""
    al = 1.0 - math.exp(-DT / tau_s)
    return lfilter([al], [1.0, -(1.0 - al)], x)


def running_rank(x: np.ndarray, moving: np.ndarray, chunk: int = 1024) -> np.ndarray:
    """The mid-rank of x_j among the moving points j' <= j (values rounded to 1/RANK_LEVELS); 0.5 for t < 60 s and
    while no point has moved. Counts carried across chunks by level; pairs inside a chunk compared directly."""
    n = len(x)
    q = np.clip(np.rint(np.asarray(x) * RANK_LEVELS), 0, RANK_LEVELS).astype(np.int64)
    out = np.full(n, 0.5)
    carry = np.zeros(RANK_LEVELS + 1, dtype=np.int64)  # moving points before the chunk, per level
    for s in range(0, n, chunk):
        e = min(n, s + chunk)
        qq, mv = q[s:e], moving[s:e]
        cle = np.cumsum(carry)  # carried points with level <= l
        below = np.where(qq > 0, cle[np.maximum(qq - 1, 0)], 0).astype(np.float64)
        eq = carry[qq].astype(np.float64)
        # inside the chunk: points i <= j that move, with level below / equal to that of j
        tri = np.tril(np.ones((e - s, e - s), dtype=bool)) & mv[None, :]
        below += (tri & (qq[None, :] < qq[:, None])).sum(axis=1)
        eq += (tri & (qq[None, :] == qq[:, None])).sum(axis=1)
        tot = cle[-1] + np.cumsum(mv)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[s:e] = np.where(tot > 0, (below + 0.5 * eq) / np.maximum(tot, 1), 0.5)
        np.add.at(carry, qq[mv], 1)
    out[: RANK_WARM_S * HZ] = 0.5
    return out


def apply_stop(m: np.ndarray, stopped: np.ndarray, kind: str) -> np.ndarray:
    """hold: the value at the last moving point; decay: that value times exp(-elapsed / 60 s); ground: 0."""
    n = len(m)
    idx = np.arange(n)
    lastmv = np.where(~stopped, idx, -1)
    np.maximum.accumulate(lastmv, out=lastmv)
    v0 = np.where(lastmv >= 0, m[np.maximum(lastmv, 0)], 0.0)
    if kind == "hold":
        held = v0
    elif kind == "decay":
        held = v0 * np.exp(-((idx - lastmv) * DT) / DECAY_TAU_S)
    elif kind == "ground":
        held = np.zeros(n)
    else:
        raise ValueError(kind)
    return np.where(stopped, held, m)


def ar1_from(x0: np.ndarray, e: np.ndarray) -> np.ndarray:
    """AR(1) with coefficient JIT_PHI from the start values x0 (one per column) and standard normal innovations e
    (n x columns), scaled to the stationary standard deviation JIT_SD."""
    sd_e = JIT_SD * math.sqrt(1.0 - JIT_PHI ** 2)
    return lfilter([1.0], [1.0, -JIT_PHI], sd_e * e, axis=0, zi=(JIT_PHI * JIT_SD * x0)[None, :])[0]


def ar1(n: int, rng: np.random.Generator) -> np.ndarray:
    """One AR(1) series started from its stationary law (selftest)."""
    return ar1_from(rng.standard_normal(1), rng.standard_normal((n, 1)))[:, 0]


def wobble(n: int, seed: int, key_seed: int) -> tuple[np.ndarray, np.ndarray]:
    """The wobble of a and r from one stream (the jitter mapping; no candidate of this task uses it)."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, key_seed & 0xFFFFFFFF, JITTER_TAG]))
    w = ar1_from(rng.standard_normal(2), rng.standard_normal((n, 2)))
    return w[:, 0], w[:, 1]


def shape(ua: np.ndarray, ur: np.ndarray, stopped: np.ndarray, mapping: str, stop: str, seed: int,
          key_seed: int) -> tuple[np.ndarray, np.ndarray]:
    """The drive -> mapping -> stop -> (jitter) wobble -> clip, for both parameters."""
    moving = ~stopped
    if mapping in ("raw", "jitter"):
        ma, mr = ua, ur
    elif mapping == "smooth":
        ma, mr = ema(ua, SMOOTH_TAU_S), ema(ur, SMOOTH_TAU_S)
    elif mapping == "rank":
        ma, mr = running_rank(ua, moving), running_rank(ur, moving)
    else:
        raise ValueError(mapping)
    a, r = apply_stop(ma, stopped, stop), apply_stop(mr, stopped, stop)
    if mapping == "jitter":
        wa, wr = wobble(len(a), seed, key_seed)
        a, r = a + wa, r + wr
    return np.clip(a, 0.0, 1.0), np.clip(r, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Plan D (design 1.2)
# ---------------------------------------------------------------------------

def d_inputs(inp: StageInput) -> tuple[np.ndarray, np.ndarray]:
    """Seam: the columns plan D reads (the press times and the active seconds)."""
    return np.asarray(inp["presses"]), np.asarray(inp["active"])


def d_intervals(presses_s: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The "all" intervals (0 < interval < STOP_MS, whole ms) of a press sequence: (their values in ms, their end
    times in ms, their index in the press sequence; interval i ends at press i)."""
    pm = np.rint(np.asarray(presses_s, dtype=np.float64) * 1000.0).astype(np.int64)
    if len(pm) < 2:
        z = np.zeros(0, dtype=np.int64)
        return z.astype(np.float64), z, z
    d = np.diff(pm)
    idx = np.nonzero((d > 0) & (d < STOP_MS))[0] + 1
    return d[idx - 1].astype(np.float64), pm[idx], idx


def d_window_bounds(ends_ms: np.ndarray, duration_s: int) -> tuple[np.ndarray, np.ndarray]:
    """Seam: per second k, the window [lo, hi) over the "all" intervals: the last N_WIN whose end is in
    [1000 (k + 1 - MAX_AGE_S), 1000 (k + 1))."""
    t = (np.arange(duration_s, dtype=np.int64) + 1) * 1000
    hi = np.searchsorted(ends_ms, t, side="left")
    lo_age = np.searchsorted(ends_ms, t - MAX_AGE_S * 1000, side="left")
    return np.maximum(hi - N_WIN, lo_age), hi


def d_select(w: np.ndarray, dset: str) -> np.ndarray:
    """Seam: the set of a window's intervals (a bool mask): all, or those below RUN_K times the window's median."""
    if dset == "all":
        return np.ones(len(w), dtype=bool)
    if dset == "run":
        return w < RUN_K * float(np.median(w))
    raise ValueError(dset)


def d_spread(v: np.ndarray) -> float:
    """Seam: the amplitude of a set, log(p90 / p10) / log 10 clipped to [0, 1]."""
    p10, p90 = np.percentile(v, [10, 90])
    return float(np.clip(math.log(p90 / p10) / SPREAD_SCALE, 0.0, 1.0))


def d_irregularity(w: np.ndarray, adj: np.ndarray, sel: np.ndarray) -> tuple[float | None, int]:
    """The tempo of a window: the median of |log(I_i / I_(i-1))| over adjacent pairs both in the set, / IRREG_SCALE,
    clipped; (None, the number of pairs) when there are fewer than MIN_PAIRS pairs. adj[q]: interval q of the window
    follows interval q - 1 in the press sequence."""
    if len(w) < 2:
        return None, 0
    ok = adj[1:] & sel[1:] & sel[:-1]
    n = int(ok.sum())
    if n < MIN_PAIRS:
        return None, n
    lr = np.abs(np.log(w[1:][ok] / w[:-1][ok]))
    return float(np.clip(float(np.median(lr)) / IRREG_SCALE, 0.0, 1.0)), n


@dataclass
class DSeconds:
    a: np.ndarray  # per second, after the hold of an insufficient window
    r: np.ndarray
    n_set: np.ndarray  # intervals in the set per second
    n_pairs: np.ndarray
    lo: np.ndarray  # the window [lo, hi) over the "all" intervals per second
    hi: np.ndarray
    idx: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.int64))  # press index of each interval


def d_seconds(presses_s: np.ndarray, duration_s: int, dset: str, a_block: np.ndarray | None = None) -> DSeconds:
    """design 1.2: the per-second a and r of plan D. a_block (design 1.5, the PC-stall): the value of a per second
    in place of the spread (still held when the set has fewer than MIN_IVL intervals)."""
    vals, ends, idx = d_intervals(presses_s)
    lo, hi = d_window_bounds(ends, duration_s)
    adj_all = np.zeros(len(idx), dtype=bool)
    if len(idx) > 1:
        adj_all[1:] = idx[1:] == idx[:-1] + 1
    a = np.empty(duration_s)
    r = np.empty(duration_s)
    n_set = np.zeros(duration_s, dtype=np.int64)
    n_pairs = np.zeros(duration_s, dtype=np.int64)
    pa, pr = D_INIT, D_INIT
    last = None
    for k in range(duration_s):
        key = (int(lo[k]), int(hi[k]))
        if key != last:  # a new window: the set and its quantities
            w = vals[key[0]: key[1]]
            sel = d_select(w, dset) if len(w) else np.zeros(0, dtype=bool)
            ns = int(sel.sum())
            spread = d_spread(w[sel]) if ns >= MIN_IVL else None
            irr, npair = d_irregularity(w, adj_all[key[0]: key[1]], sel)
            last = key
        if a_block is not None:
            pa = float(a_block[k]) if ns >= MIN_IVL else pa
        elif spread is not None:
            pa = spread
        if irr is not None and a_block is None:
            pr = irr
        a[k], r[k], n_set[k], n_pairs[k] = pa, pr, ns, npair
    return DSeconds(a, r, n_set, n_pairs, lo, hi, idx)


def d_stopped(active: np.ndarray, duration_s: int) -> np.ndarray:
    """The stopped points of res=sec (as drive_sec): before t = 1, or no press in the second used nor the one
    before."""
    n = duration_s * HZ
    k = np.arange(n) // HZ - 1
    kk = np.maximum(k, 0)
    known = k >= 0
    prev = np.where(k >= 1, active[np.maximum(k - 1, 0)], False)
    return ~known | (~active[kk] & ~prev)


def d_points(a_s: np.ndarray, r_s: np.ndarray, active: np.ndarray, duration_s: int, seed: int, key_seed: int
             ) -> tuple[np.ndarray, np.ndarray]:
    """Second k is used from t = k + 1 (D_INIT before t = 1, where every point is stopped), then hold and clip."""
    n = duration_s * HZ
    k = np.arange(n) // HZ - 1
    kk = np.maximum(k, 0)
    ua = np.where(k >= 0, a_s[kk], D_INIT)
    ur = np.where(k >= 0, r_s[kk], D_INIT)
    return shape(ua, ur, d_stopped(active, duration_s), "raw", "hold", seed, key_seed)


def d_series(inp: StageInput, name: str, seed: int, key_seed: int, a_block: np.ndarray | None = None
             ) -> tuple[np.ndarray, np.ndarray]:
    """A plan D candidate (or, with a_block, its PC-stall): reads presses and active only."""
    dset = d_parse(name)
    presses, active = d_inputs(inp)
    ds = d_seconds(presses, inp.duration_s, dset, a_block)
    return d_points(ds.a, ds.r, active, inp.duration_s, seed, key_seed)


# ---------------------------------------------------------------------------
# Candidates and controls
# ---------------------------------------------------------------------------

def stall_share(seg: np.ndarray, a: int, b: int) -> float:
    """The stall share of seconds [max(0, a), b); 0.0 for an empty span."""
    st = np.isin(seg[max(0, a): max(0, b)], STALL_CODES)
    return float(st.mean()) if len(st) else 0.0


def pc_blocks(seg: np.ndarray, duration_s: int, key_seed: int, seed: int, lam: float, span_s: int = PC_SPAN_S,
              tag: int = PC_TAG) -> dict:
    """PC-stall: per 60 s block, U then N (always both, whatever lambda is), q = the stall share of the preceding
    span_s seconds, and the value q if U < lam else N."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, key_seed & 0xFFFFFFFF, tag]))
    nb = -(-duration_s // PC_BLOCK_S)
    U, N, q = np.zeros(nb), np.zeros(nb), np.zeros(nb)
    for b in range(nb):
        U[b], N[b] = float(rng.random()), float(rng.random())
        q[b] = stall_share(seg, b * PC_BLOCK_S - span_s, b * PC_BLOCK_S)
    return {"U": U, "N": N, "q": q, "value": np.where(U < lam, q, N)}


def candidate_series(inp: StageInput, name: str, seed: int, key_seed: int) -> tuple[np.ndarray, np.ndarray]:
    """A candidate: reads only inp."""
    if name.startswith("D-"):
        return d_series(inp, name, seed, key_seed)
    m, s, r = parse(name)
    ua, ur, stopped = drive(inp, r)
    return shape(ua, ur, stopped, m, s, seed, key_seed)

# ---------------------------------------------------------------------------
# Person controls (design 1.5, 1.8)
# ---------------------------------------------------------------------------

def person_of(sid: str, slots: int = SLOTS) -> int:
    """The person of session P<i>: i // slots (a session's name is all the controls read of the person)."""
    return int(sid[1:]) // slots


def pers_sign(seed: int, p: int, n_persons: int = N_PERSONS) -> float:
    """s_p: +1 for half of the persons and -1 for the others, drawn from derive_rng(seed, "pcsign")."""
    order = gs.derive_rng(seed, "pcsign").permutation(n_persons)
    s = np.full(n_persons, -1.0)
    s[order[: n_persons // 2]] = 1.0
    return float(s[p])


def pc0p_sign(seed: int, p: int, n_persons: int = N_PERSONS) -> float:
    """PC0p: the same direction for everybody (seam: selftest Q2 and the mutant)."""
    return 1.0


def pcid_value(seed: int, p: int) -> float:
    """Phi(z'_p): a person's own value, from a stream the generator does not use."""
    return float(ndtr(gs.derive_rng(seed, "pcid", p).standard_normal()))


def pcid0_value(seed: int, i: int) -> float:
    """Phi(e'_s): one value per session, tied to no person."""
    return float(ndtr(gs.derive_rng(seed, "pcid0", i).standard_normal()))


def person_blocks(sess: "Session", seed: int, lam: float, kind: str, n_persons: int, slots: int) -> np.ndarray:
    """The block values of a person control: U, N and q as pc_blocks; the signal replaces q where U < lam."""
    blk = pc_blocks(sess.seg, sess.duration_s, sess.key_seed, seed, lam)
    i, p = int(sess.sid[1:]), person_of(sess.sid, slots)
    if kind == "id":
        sig = np.full_like(blk["q"], pcid_value(seed, p))
    elif kind == "id0":
        sig = np.full_like(blk["q"], pcid0_value(seed, i))
    elif kind == "pers":
        sig = 0.5 + pers_sign(seed, p, n_persons) * (blk["q"] - 0.5)
    elif kind == "p0":
        sig = 0.5 + pc0p_sign(seed, p, n_persons) * (blk["q"] - 0.5)
    else:
        raise ValueError(kind)
    return np.where(blk["U"] < lam, sig, blk["N"])


def person_series(sess: "Session", name: str, seed: int, lam: float | None, n_persons: int, slots: int
                  ) -> tuple[np.ndarray, np.ndarray]:
    """(a, r) of the person controls (names PERSON_NAMES). The picture of a block control is built as the PC-stall's:
    an anchor takes the block value as its drive (r = 0.5) and its own stop; a plan D candidate takes it in place of
    the spread."""
    n = sess.duration_s * HZ
    if name in ("PC1-id", "PC1-pers"):
        if name == "PC1-id":
            a = np.full(n, pcid_value(seed, person_of(sess.sid, slots)))
        else:
            blk = person_blocks(sess, seed, 1.0, "pers", n_persons, slots)  # lam 1: every block is the signal
            a = np.repeat(blk, PC_BLOCK_S * HZ)[:n]
        return a, np.full(n, 0.5)
    for prefix, kind in (("PCp-", "id"), ("PC0-id-", "id0"), ("PCps-", "pers"), ("PC0p-", "p0")):
        if name.startswith(prefix):
            cand = name[len(prefix):]
            break
    else:
        raise ValueError(name)
    assert lam is not None, f"{name} needs lam"
    blk = person_blocks(sess, seed, lam, kind, n_persons, slots)
    inp = stage_input(sess)
    if cand.startswith("D-"):
        a_block = blk[np.arange(sess.duration_s) // PC_BLOCK_S]
        return d_series(inp, cand, seed, sess.key_seed, a_block=a_block)
    m, s, r = parse(cand)
    _, _, stopped = drive(inp, r)
    ua = np.repeat(blk, PC_BLOCK_S * HZ)[:n]
    return shape(ua, np.full(n, 0.5), stopped, m, s, seed, sess.key_seed)


def series(sess: Session, name: str, seed: int, lam: float | None = None, mutation: str | None = None,
           n_persons: int = N_PERSONS, slots: int = SLOTS) -> tuple[np.ndarray, np.ndarray]:
    """(a, r) at 10 Hz of a candidate or a control. Names: S-..., D-..., PC1, PCs-<candidate>(lam),
    PC0-<candidate>, PC-corr. mutation "seg" (selftest only): the candidate's amplitude mixed half and half with the
    stall indicator of the last completed second."""
    n = sess.duration_s * HZ
    if name == "PC1-id" or name == "PC1-pers" or name.startswith(("PCp-", "PC0-id-", "PCps-", "PC0p-")):
        return person_series(sess, name, seed, lam, n_persons, slots)  # design 1.5, 1.8
    inp = stage_input(sess)
    if name.startswith(("S-", "D-")):
        a, r = candidate_series(inp, name, seed, sess.key_seed)
        if mutation == "seg":
            k = np.maximum(np.arange(n) // HZ - 1, 0)
            a = 0.5 * a + 0.5 * np.isin(sess.seg[k], STALL_CODES)
        elif mutation is not None:
            raise ValueError(mutation)
        return a, r
    if name == "PC1":
        _, r = candidate_series(inp, "S-raw-hold-sec", seed, sess.key_seed)
        st = np.concatenate([[0.0], np.cumsum(np.isin(sess.seg, STALL_CODES))])
        f = np.arange(n) // HZ  # floor(t)
        lo = np.maximum(f - PC1_SPAN_S, 0)
        span = f - lo
        a = np.where(span > 0, (st[f] - st[lo]) / np.maximum(span, 1), 0.0)
        return a, r
    if name == "PC-corr":
        ua, _, stopped = drive_sec(inp)
        k = np.arange(n) // HZ - 1
        ur_s = hold_nan(np.clip(1.0 - sess.feat["f3"], 0.0, 1.0))  # declared exception: f3
        ur = np.where(k >= 0, ur_s[np.maximum(k, 0)], 0.0)
        return shape(ua, ur, stopped, "raw", "hold", seed, sess.key_seed)
    if name.startswith(("PCs-", "PC0-")):
        cand = name[4:]
        if name.startswith("PC0-"):
            lam = 0.0
        assert lam is not None, f"{name} needs lam"
        blk = pc_blocks(sess.seg, sess.duration_s, sess.key_seed, seed, lam)["value"]
        if cand.startswith("D-"):  # design 1.5: the block value in place of the spread, per second
            a_block = blk[np.arange(sess.duration_s) // PC_BLOCK_S]
            return d_series(inp, cand, seed, sess.key_seed, a_block=a_block)
        m, s, r = parse(cand)
        _, _, stopped = drive(inp, r)
        ua = np.repeat(blk, PC_BLOCK_S * HZ)[:n]
        ur = np.full(n, 0.5)
        return shape(ua, ur, stopped, m, s, seed, sess.key_seed)
    raise ValueError(name)


# ---------------------------------------------------------------------------
# The attacker's window features (unchanged)
# ---------------------------------------------------------------------------

def window_features(a: np.ndarray, r: np.ndarray, n_w: int) -> np.ndarray:
    """Per 60 s window, for a then r: mean, sd, p10, p50, p90, share below 0.02, mean |difference of adjacent
    points|, lag-1 autocorrelation (0 for a constant window), the final value, and the time (s) from the last point
    whose difference to its predecessor in the window exceeds 1e-6 to the window end (60 s when none)."""
    out = []
    for x in (a, r):
        X = np.asarray(x[: n_w * WIN_POINTS], dtype=np.float64).reshape(n_w, WIN_POINTS)
        mean = X.mean(axis=1)
        sd = X.std(axis=1)
        p10, p50, p90 = np.percentile(X, [10, 50, 90], axis=1)
        ground = (X < GROUND_EPS).mean(axis=1)
        d = np.diff(X, axis=1)
        absdiff = np.abs(d).mean(axis=1)
        xc = X - mean[:, None]
        num = (xc[:, 1:] * xc[:, :-1]).sum(axis=1)
        den = (xc ** 2).sum(axis=1)
        const = np.ptp(X, axis=1) == 0
        with np.errstate(invalid="ignore", divide="ignore"):
            ac = np.where(const | (den <= 0), 0.0, num / np.where(den > 0, den, 1.0))
        ch = np.abs(d) > CHANGE_EPS
        any_ch = ch.any(axis=1)
        last_i = WIN_POINTS - 2 - np.argmax(ch[:, ::-1], axis=1)  # the last diff index with a change
        since = np.where(any_ch, (WIN_POINTS - (last_i + 1)) * DT, WIN_POINTS * DT)
        out.append(np.stack([mean, sd, p10, p50, p90, ground, absdiff, ac, X[:, -1], since], axis=1))
    return np.hstack(out)


def config_names(cands: list[str]) -> dict:
    """The judged names plus PC-corr (descriptive)."""
    return {"candidates": list(cands), "pc1": ["PC1"], "pcs": [f"PCs-{c}" for c in cands],
            "pc0": [f"PC0-{c}" for c in cands], "pccorr": ["PC-corr"]}


def manifest_p(work: Path) -> list[dict]:
    return [m for m in json.loads((work / "sessions.json").read_text(encoding="utf-8")) if m["set"] == "P"]
