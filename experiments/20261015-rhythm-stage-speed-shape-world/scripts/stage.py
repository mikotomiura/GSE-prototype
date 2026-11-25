"""The rhythm stage of the desk check: keystrokes -> two drawing parameters per frame (design 1.2-1.4).

Design: .steering/20261012-rhythm-stage-desk-check/design.md (frozen 2b7db259; world v4), with the L1800 controls of
.steering/20261014-rhythm-stage-graded-world/design.md 1.4 (PC1-1800 and PCl-<candidate>).

Every series is taken at 10 Hz (point j at t = j / 10 s) and has two parameters in [0, 1]: the amplitude a and the
tempo r. A candidate S-<mapping>-<stop>-<res> is built in this order: the drive values (res) -> the mapping -> the
behaviour while stopped -> (jitter only) the AR(1) wobble -> clip to [0, 1]. Every candidate is causal: the value at t
is fixed by the input up to t (design 1.3).

The mappings read the session only through StageInput, which holds the columns of ALLOWED_INPUT (design 1.2) and
raises on any other name. The controls (design 1.4) read the labels (seg) or f3 by declaration, outside StageInput.

Details Claude added to make the definitions computable (design section 9 lists the values; these are the readings):
- res=sec: second k is used from t = k + 1 (points j with j // 10 - 1 = k); before t = 1 nothing is known: the drive
  is 0 and the point is stopped. A NaN in keys or f1 holds the previous value (0 before the first value).
- res=sub: the presses are whole ms; a press at ms m counts from the first point with 100 j >= m. Stopped means no
  press in (t - 2 s, t], i.e. t - (the last press at or before t) >= 2 s, or no press yet. u_r is 0 before the
  second press.
- rank: the mid-rank (ties count one half) of the value among the moving points up to and including t, on the values
  rounded to 1/1000 (RANK_LEVELS); 0.5 for the first 60 s and while no point has moved yet.
- stop: the stopped value v0 is the mapped value at the last moving point (0 when the session starts stopped); decay
  is v0 exp(-(t - t_last_moving) / 60 s).
- PC-stall: the drive u_a is the block value at every point of the block (moving or stopped: the behaviour while
  stopped then acts as for the candidate); q of block b is the stall share of seconds [60 b - 300, 60 b) clipped at
  0 (0.0 for the first block, whose span is empty).
- PC1: a(t) is the stall share of seconds [floor(t) - 60, floor(t)) clipped at 0 (0.0 when empty).
- L1800 controls (graded world design 1.4): PC1-1800 is PC1 over [floor(t) - 1800, floor(t)); PCl-<candidate> is the
  PC-stall of the candidate with q of block b over [60 b - 1800, 60 b), and the same U and N (the same tag).
- r-side controls (shape world design 1.3; copied from experiments/20261014-rhythm-stage-speed-confound-world/scripts/
  stage.py at 7d38df98, the names above unchanged): the PC-stall with a and r swapped. The blocks are PC-stall's (60 s,
  q over the preceding 300 s, the value q if U < lam else N) from a stream of their own (tag PCR_TAG), shared by both
  families. PCrl-<candidate> (level): u_a = 0.5, u_r = the block value. PCrv-<candidate> (var): u_a = 0.5,
  u_r = 0.5 + var_sd * value * e_j, e_j independent standard normals per point (tag PCRV_TAG). PCrl0- and PCrv0- are the
  same at lam = 0. Both go through the candidate's stop, mapping and (jitter) wobble, as the PC-stall.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

HZ = 10
DT = 1.0 / HZ
WIN_POINTS = 600  # a 60 s window (design 1.5)
STOP_MS = 2000  # design 1.3 / section 9 item 4
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
PCL_SPAN_S = 1800  # graded world design 1.4: the L1800 controls
PC1L_NAME = "PC1-1800"
PCL_PREFIX = "PCl-"
JITTER_TAG = 31  # design 3.8
PC_TAG = 37
PCR_TAG = 43  # shape world design 1.3: the blocks of the r-side controls
PCRV_TAG = 47  # shape world design 1.3: the point noise of PCr-var
PCR_VAR_SD = 0.2  # shape world design 1.3 (config.json pc_r.var_sd; selftest checks they agree)
PCR_PREFIXES = ("PCrl-", "PCrl0-", "PCrv-", "PCrv0-")  # level, level at lam 0, var, var at lam 0

MAPPINGS = ("raw", "smooth", "rank", "jitter")
STOPS = ("hold", "decay", "ground")
RESOLUTIONS = ("sec", "sub")
ALLOWED_INPUT = ("presses", "active", "keys", "f1", "f4")
STALL_CODES = (1, 3)
FEAT_NAMES = tuple(f"{p}_{q}" for p in ("a", "r") for q in ("mean", "sd", "p10", "p50", "p90", "ground", "absdiff",
                                                             "ac1", "end", "since_change"))


def candidates() -> list[str]:
    """design 1.3: the 24 candidates."""
    return [f"S-{m}-{s}-{r}" for m in MAPPINGS for s in STOPS for r in RESOLUTIONS]


def parse(name: str) -> tuple[str, str, str]:
    _, m, s, r = name.split("-")
    assert m in MAPPINGS and s in STOPS and r in RESOLUTIONS, name
    return m, s, r


# ---------------------------------------------------------------------------
# The session and the closed input (design 1.2)
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
    """The only view of a session the mappings get: the columns of ALLOWED_INPUT. Any other name raises."""

    def __init__(self, duration_s: int, cols: dict):
        self.duration_s = int(duration_s)
        self._cols = {k: cols[k] for k in ALLOWED_INPUT}

    def __getitem__(self, name: str) -> np.ndarray:
        if name not in ALLOWED_INPUT:
            raise KeyError(f"design 1.2: the stage does not read {name!r}")
        return self._cols[name]


def stage_input(sess: Session) -> StageInput:
    return StageInput(sess.duration_s, {"presses": sess.presses, "active": sess.active, "keys": sess.feat["keys"],
                                        "f1": sess.feat["f1"], "f4": sess.feat["f4"]})


# ---------------------------------------------------------------------------
# Drive values and the stop (design 1.3)
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
    # decisions 19: gse-replay's F1 is 0.0 when the 30 s window holds no interval (features.rs); that second's tempo
    # is 0 (as res=sub's "no interval below 2 s"), not the fastest value of the formula. NaN still holds.
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
    if len(pm) == 0:  # no press: no drive and stopped everywhere (Codex: the indexing below needs a press)
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
# Mappings, stop behaviours and the wobble (design 1.3)
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
    """The wobble of a and r from one stream: the two start values, then the innovations of a and r drawn in pairs
    point by point, so that the first m points do not depend on the session length n (Codex: drawing a's n
    innovations before r's made r's start depend on n)."""
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
# Candidates and controls (design 1.3, 1.4)
# ---------------------------------------------------------------------------

def stall_share(seg: np.ndarray, a: int, b: int) -> float:
    """The stall share of seconds [max(0, a), b); 0.0 for an empty span."""
    st = np.isin(seg[max(0, a): max(0, b)], STALL_CODES)
    return float(st.mean()) if len(st) else 0.0


def pc_blocks(seg: np.ndarray, duration_s: int, key_seed: int, seed: int, lam: float, span_s: int = PC_SPAN_S,
              tag: int = PC_TAG) -> dict:
    """PC-stall (design 1.4): per 60 s block, U then N (always both, whatever lambda is), q = the stall share of the
    preceding span_s seconds (300; 1800 for PCl, graded world design 1.4), and the value q if U < lam else N. tag: the
    stream (PC_TAG; PCR_TAG for the r-side controls, shape world design 1.3)."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, key_seed & 0xFFFFFFFF, tag]))
    nb = -(-duration_s // PC_BLOCK_S)
    U, N, q = np.zeros(nb), np.zeros(nb), np.zeros(nb)
    for b in range(nb):
        U[b], N[b] = float(rng.random()), float(rng.random())
        q[b] = stall_share(seg, b * PC_BLOCK_S - span_s, b * PC_BLOCK_S)
    return {"U": U, "N": N, "q": q, "value": np.where(U < lam, q, N)}


def candidate_series(inp: StageInput, name: str, seed: int, key_seed: int) -> tuple[np.ndarray, np.ndarray]:
    """A candidate S-<mapping>-<stop>-<res>: reads only inp."""
    m, s, r = parse(name)
    ua, ur, stopped = drive(inp, r)
    return shape(ua, ur, stopped, m, s, seed, key_seed)


def pcr_parse(name: str) -> tuple[str, str, bool]:
    """shape world design 1.3: (family "level" or "var", the candidate, at lam 0) of an r-side control name."""
    head, _, cand = name.partition("-")
    fam = {"PCrl": ("level", False), "PCrl0": ("level", True), "PCrv": ("var", False), "PCrv0": ("var", True)}
    if head not in fam or not cand.startswith("S-"):
        raise ValueError(name)
    parse(cand)
    return fam[head][0], cand, fam[head][1]


def pcr_drive(sess: Session, family: str, lam: float, seed: int) -> np.ndarray:
    """shape world design 1.3: u_r of an r-side control at 10 Hz."""
    n = sess.duration_s * HZ
    blk = pc_blocks(sess.seg, sess.duration_s, sess.key_seed, seed, lam, PC_SPAN_S, PCR_TAG)["value"]
    v = np.repeat(blk, PC_BLOCK_S * HZ)[:n]
    if family == "level":
        return v
    if family == "var":
        e = np.random.default_rng(np.random.SeedSequence([seed, sess.key_seed & 0xFFFFFFFF, PCRV_TAG])).standard_normal(n)
        return 0.5 + PCR_VAR_SD * v * e
    raise ValueError(family)


def series(sess: Session, name: str, seed: int, lam: float | None = None, mutation: str | None = None
           ) -> tuple[np.ndarray, np.ndarray]:
    """(a, r) at 10 Hz of a candidate or a control. Names: S-..., PC1, PCs-S-...(lam), PC0-S-..., PC-corr, and the
    r-side controls PCrl-S-...(lam), PCrv-S-...(lam), PCrl0-S-..., PCrv0-S-... (shape world design 1.3).
    mutation "seg" (selftest only, design 3.7): the candidate's amplitude mixed half and half with the stall
    indicator of the last completed second."""
    n = sess.duration_s * HZ
    inp = stage_input(sess)
    if name.startswith("S-"):
        a, r = candidate_series(inp, name, seed, sess.key_seed)
        if mutation == "seg":
            k = np.maximum(np.arange(n) // HZ - 1, 0)
            a = 0.5 * a + 0.5 * np.isin(sess.seg[k], STALL_CODES)
        elif mutation is not None:
            raise ValueError(mutation)
        return a, r
    if name in ("PC1", PC1L_NAME):
        _, r = candidate_series(inp, "S-raw-hold-sec", seed, sess.key_seed)
        st = np.concatenate([[0.0], np.cumsum(np.isin(sess.seg, STALL_CODES))])
        f = np.arange(n) // HZ  # floor(t)
        lo = np.maximum(f - (PC1_SPAN_S if name == "PC1" else PCL_SPAN_S), 0)
        span = f - lo
        a = np.where(span > 0, (st[f] - st[lo]) / np.maximum(span, 1), 0.0)
        return a, r
    if name == "PC-corr":
        ua, _, stopped = drive_sec(inp)
        k = np.arange(n) // HZ - 1
        ur_s = hold_nan(np.clip(1.0 - sess.feat["f3"], 0.0, 1.0))  # declared exception: f3 (design 1.4)
        ur = np.where(k >= 0, ur_s[np.maximum(k, 0)], 0.0)
        return shape(ua, ur, stopped, "raw", "hold", seed, sess.key_seed)
    if name.startswith(("PCs-", "PC0-", PCL_PREFIX)):
        cand = name[4:]
        if name.startswith("PC0-"):
            lam = 0.0
        assert lam is not None, f"{name} needs lam"
        m, s, r = parse(cand)
        _, _, stopped = drive(inp, r)
        span = PCL_SPAN_S if name.startswith(PCL_PREFIX) else PC_SPAN_S
        blk = pc_blocks(sess.seg, sess.duration_s, sess.key_seed, seed, lam, span)["value"]
        ua = np.repeat(blk, PC_BLOCK_S * HZ)[:n]
        ur = np.full(n, 0.5)
        return shape(ua, ur, stopped, m, s, seed, sess.key_seed)
    if name.startswith(PCR_PREFIXES):
        family, cand, zero = pcr_parse(name)
        if zero:
            lam = 0.0
        assert lam is not None, f"{name} needs lam"
        m, s, r = parse(cand)
        _, _, stopped = drive(inp, r)
        ua = np.full(n, 0.5)
        return shape(ua, pcr_drive(sess, family, lam, seed), stopped, m, s, seed, sess.key_seed)
    raise ValueError(name)


# ---------------------------------------------------------------------------
# The attacker's window features (design 1.5)
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


def pcr_names(cands: list[str]) -> dict:
    """shape world design 1.4: the r-side controls of each candidate, per family: (control, its lam 0 baseline)."""
    return {"level": {c: (f"PCrl-{c}", f"PCrl0-{c}") for c in cands},
            "var": {c: (f"PCrv-{c}", f"PCrv0-{c}") for c in cands}}


def config_names(cands: list[str]) -> dict:
    """design 1.4: the 73 judged names plus PC-corr (descriptive); pc1_1800 and pcl are fitted on L1800 only
    (graded world design 1.2, 1.4)."""
    return {"candidates": list(cands), "pc1": ["PC1"], "pcs": [f"PCs-{c}" for c in cands],
            "pc0": [f"PC0-{c}" for c in cands], "pccorr": ["PC-corr"],
            "pc1_1800": [PC1L_NAME], "pcl": [f"{PCL_PREFIX}{c}" for c in cands]}


def manifest_p(work: Path) -> list[dict]:
    return [m for m in json.loads((work / "sessions.json").read_text(encoding="utf-8")) if m["set"] == "P"]
