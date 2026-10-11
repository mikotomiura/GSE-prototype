"""Update scheduler, provisional portrait generators and per-session measurements for EH1 round 5.

The generators are provisional grammars, not product candidates. They differ in what they map
(levels of the F series, ordinal patterns, ordinal patterns through a per-session key, or coarse
level classes placed by update ordinal) and in whether the canvas evolves at every update (drift).
The positive controls (PC1, PCcal, PCsize, PCahead) and the oracles exist only to show what the checks can find.

Design (frozen before results): .steering/20261010-portrait-eh1-round5/design.md sections 1-3 (commit 92d262fd)
(round 4: .steering/20261010-portrait-eh1-round4/design.md; round 3: .steering/20261010-portrait-eh1-round3/design.md; round 2: .steering/20261009-portrait-eh1-round2/design.md).
"""

from __future__ import annotations

import colorsys
import functools
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import ndimage

# E1-1: the only columns a generator may receive. PC2 (round 2, not run in round 3) additionally receives
# p_stuck; PCcal and the oracles receive one value per update read from the labels (round 3 design 1.4).
ALLOWED_MATERIAL = ("f1", "f3", "f4", "f5", "f6", "active")
PC2_EXTRA = ("p_stuck",)
ORC_EXTRA = ("oracle",)
ORC_SPAN_S = 300
TINT_PCS = ("PC2", "ORC300", "ORCgap", "ORCcum", "PCcal")  # display-only tint (round 2 design 1.3, round 3 1.4)
ORACLE_PCS = ("ORC300", "ORCgap", "ORCcum", "PCcal")  # read the labels: E1-1 exceptions
PCCAL_RNG_TAG = 13  # round 3 design 1.4: a tag no other stream uses
# round 4 design 1.4: the shape PC (the size level only, on clock60) and the five-band oracle also read the labels
LABEL_PCS = ORACLE_PCS + ("PCsize", "ORCband", "PCahead")
PCSIZE_RNG_TAG = 17  # U and N of PCsize
PCSIZE_DIR_TAG = 18  # the heading level n6 of raw PCsize (and PCahead), one draw per drawn update
# round 5 design 1.4: the look-ahead PC (the size level only, on the real scheduler) reads the labels after u
PCAHEAD_RNG_TAG = 19  # U and N of PCahead
SIZE_PCS = ("PCsize", "PCahead")  # drawn alike: only the source of the value differs
N_BANDS = 5
BAND_S = 60
STALL_CODES = (1, 3)
SLEEP_CODE = 5


@dataclass
class Session:
    sid: str
    set: str
    duration_s: int
    presses: np.ndarray  # press times in seconds (float, sorted)
    active: np.ndarray  # bool per second: at least one press in [k, k+1)
    seg: np.ndarray  # segment code per second (labels: read only by the checks, never by the scheduler)
    feat: dict  # column -> float array per second (NaN where no tick)
    key_seed: int
    sleep: np.ndarray  # bool per second: the machine was asleep (the only thing the scheduler takes from the trace)


def load_session(work: Path, m: dict) -> Session:
    lab = np.load(work / "labels" / f"{m['sid']}.npz")
    feat = np.load(work / "feat" / f"{m['sid']}.npz")
    dur = int(lab["duration_s"])
    presses = np.sort(lab["presses_ms"].astype(np.float64) / 1000.0)
    active = np.zeros(dur, dtype=bool)
    idx = presses.astype(np.int64)
    active[idx[idx < dur]] = True
    seg = lab["seg"].astype(np.int8)
    return Session(m["sid"], m["set"], dur, presses, active, seg,
                   {c: feat[c] for c in ("f1", "f3", "f4", "f5", "f6", "p_stuck", "keys")}, int(m["key_seed"]),
                   seg == SLEEP_CODE)


# ---------------------------------------------------------------------------
# Scheduler (design 1.3)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Sched:
    kind: str = "clock"  # "clock", "stop" (PC1), "recent" or "fixed" (round 3 clock60: never looks at presses)
    interval_s: int = 300
    window_s: int = 5
    jitter: bool = False
    cap1: bool = False
    recent_s: int = 60  # "recent": update only if a press came within the last recent_s seconds

    @property
    def name(self) -> str:
        if self.kind == "stop":
            return "stop"
        if self.kind == "fixed":
            return f"I{self.interval_s}-fixed"
        n = f"I{self.interval_s}-W{self.window_s}{'-jit' if self.jitter else ''}{'-cap1' if self.cap1 else ''}"
        return n + (f"-recent{self.recent_s}" if self.kind == "recent" else "")


def _has_press(presses: np.ndarray, lo: float, hi: float) -> bool:
    """Is there a press p with lo < p <= hi?"""
    a = np.searchsorted(presses, lo, side="right")
    b = np.searchsorted(presses, hi, side="right")
    return b > a


def schedule(sess: Session, sc: Sched, jitter_frac: float, seed: int, pc1: dict | None = None) -> np.ndarray:
    """Actual update times (integer seconds; the new image is shown from that second on)."""
    dur = sess.duration_s
    sleep = sess.sleep
    out: list[int] = []
    if sc.kind == "stop":
        assert pc1 is not None
        last_u = -10**9
        p = sess.presses
        ends = np.append(p[1:], np.inf)
        for t_press, t_next in zip(p, ends):
            if t_next - t_press >= pc1["stop_silence_s"]:
                u = int(math.ceil(t_press + pc1["stop_silence_s"]))
                # u < t_next: the rounded update time must still fall in the silence (round 2 /cross-review)
                if u < dur and u < t_next and u - last_u >= pc1["min_gap_s"] and not sleep[u]:
                    out.append(u)
                    last_u = u
        return np.asarray(out, dtype=np.int64)
    if sc.kind == "fixed":
        # round 3 design 1.2 (clock60): every interval_s seconds, never skipped for presses (sleep only)
        return np.asarray([u for u in range(sc.interval_s, dur, sc.interval_s) if not sleep[u]], dtype=np.int64)
    rng = np.random.default_rng(np.random.SeedSequence([seed, sess.key_seed & 0xFFFFFFFF, 7]))
    last_u = 0.0
    k = 1
    while True:
        slot = k * sc.interval_s
        if sc.jitter:
            slot += float(rng.uniform(-jitter_frac, jitter_frac)) * sc.interval_s
        k += 1
        if slot >= dur:
            break
        u = int(round(slot))
        if u <= 0 or u >= dur or (out and u <= out[-1]):
            continue
        if sleep[u]:
            continue  # slots missed during sleep are not caught up
        if _has_press(sess.presses, u - sc.window_s, u):
            continue  # typing in progress: skip to the next slot
        if sc.cap1 and not _has_press(sess.presses, last_u, u):
            continue  # nothing typed since the last update
        if sc.kind == "recent" and not _has_press(sess.presses, u - sc.recent_s, u):
            continue  # exploratory: never update inside an absence of recent_s or more
        out.append(u)
        last_u = float(u)
    return np.asarray(out, dtype=np.int64)


def stall_share(sess: Session, a: int, b: int) -> float:
    """Share of stall seconds in [max(0, a), b) (round 3 design 1.4; NaN for an empty span)."""
    st = np.isin(sess.seg[max(0, a) : b], STALL_CODES)
    return float(st.mean()) if len(st) else float("nan")


def material_slice(sess: Session, a: int, b: int, pc2: bool = False, oracle: float | None = None) -> dict:
    """Material for an update covering seconds [a, b). E1-1 boundary. oracle: the one value an oracle or
    PCcal update receives (computed by run() from the labels; round 3 design 1.4)."""
    keys = ALLOWED_MATERIAL + (PC2_EXTRA if pc2 else ())
    out = {}
    for c in keys:
        out[c] = sess.active[a:b] if c == "active" else sess.feat[c][a:b]
    if oracle is not None:
        out["oracle"] = np.atleast_1d(np.asarray(oracle, dtype=float))  # ORCband: five values (round 4 design 1.4)
    return out


# ---------------------------------------------------------------------------
# Generators (design 1.4)
# ---------------------------------------------------------------------------

def hsv(h: float, s: float, v: float) -> np.ndarray:
    return np.asarray(colorsys.hsv_to_rgb(h % 1.0, s, v), dtype=np.float32)


def _ordinal_hist(v: np.ndarray) -> np.ndarray:
    """Histogram over 7 classes: the 6 strict ordinal patterns of length 3, plus 'tie'."""
    h = np.zeros(7)
    v = v[np.isfinite(v)]
    if len(v) < 3:
        return np.full(7, 1 / 7)
    a, b, c = v[:-2], v[1:-1], v[2:]
    tie = (a == b) | (b == c) | (a == c)
    h[6] = tie.sum()
    s = ~tie
    code = (a[s] < b[s]).astype(int) * 4 + (b[s] < c[s]).astype(int) * 2 + (a[s] < c[s]).astype(int)
    # codes 0..7 with 2 impossible combinations; map the 6 possible ones to 0..5
    lut = {0: 0, 1: -1, 2: 1, 3: 2, 4: 3, 5: 4, 6: -1, 7: 5}
    for cval, cnt in zip(*np.unique(code, return_counts=True)):
        h[lut[int(cval)]] += cnt
    return h / h.sum()


def _alloc(hist: np.ndarray, m: int) -> np.ndarray:
    """Deterministic proportional allocation of m marks to classes by quantile."""
    cdf = np.cumsum(hist)
    q = (np.arange(m) + 0.5) / m
    return np.minimum(np.searchsorted(cdf, q), len(hist) - 1)


LATTICE_BOUNDS = (1 / 3, 2 / 3)


def lattice_class(v: float, prev: int | None, delta: float) -> int:
    """Three coarse classes of a level in [0, 1]. Away from the first update a class changes only when
    the level crosses a boundary by more than delta (hysteresis, design 1.3)."""
    if prev is None:
        return int(sum(v >= b for b in LATTICE_BOUNDS))
    c = prev
    while c < 2 and v >= LATTICE_BOUNDS[c] + delta:
        c += 1
    while c > 0 and v < LATTICE_BOUNDS[c - 1] - delta:
        c -= 1
    return c


@functools.lru_cache(maxsize=4)
def lattice_cells(w: int, h: int, cell: int) -> tuple:
    """Cell centres ordered as a spiral from the centre outwards: by distance (rounded to a cell), then
    by angle. The order is fixed; the k-th drawn update goes to cell k (mod the number of cells)."""
    nx, ny = w // cell, h // cell
    cx, cy = (nx - 1) / 2, (ny - 1) / 2
    cells = []
    for j in range(ny):
        for i in range(nx):
            d = math.hypot(i - cx, j - cy)
            a = math.atan2(j - cy, i - cx) % (2 * math.pi)
            cells.append((round(d), a, (i + 0.5) * cell, (j + 0.5) * cell))
    cells.sort(key=lambda c: (c[0], c[1]))
    return tuple((c[2], c[3]) for c in cells)


class Generator:
    def __init__(self, mapping: str, drift: str, cfg: dict, key_seed: int, pc: str | None = None,
                 mutation: str | None = None, seed: int = 0):
        self.mapping, self.drift, self.pc, self.mutation = mapping, drift, pc, mutation
        cv, g = cfg["canvas"], cfg["generator"]
        self.W, self.H = cv["w"], cv["h"]
        self.ground = np.asarray(cv["ground"], dtype=np.float32)
        self.g = g
        self.cfg = cfg
        self.base = np.empty((self.H, self.W, 3), dtype=np.float32)
        self.base[:] = self.ground
        self.total_active = 0
        self.neutral = True
        self.buffer: list[dict] = []
        self.recent: list[tuple[int, int]] = []  # (time, active) for the E1-7 mutation
        r = np.random.default_rng(np.random.SeedSequence([key_seed & 0xFFFFFFFF, key_seed >> 32, 11]))
        self.x = float(r.uniform(0.3, 0.7) * self.W)
        self.y = float(r.uniform(0.3, 0.7) * self.H)
        self.theta = float(r.uniform(0, 2 * np.pi))
        self.phase = float(r.uniform(0, 2 * np.pi))
        self.hue_off = float(r.uniform(0, 1)) if mapping == "keyed" else 0.0
        self.tables = {
            "hue": np.arange(7) / 7.0,
            "sigma": np.linspace(2.0, 8.0, 7),
            "turn": np.linspace(-0.6, 0.6, 7),
            "light": np.linspace(0.35, 0.75, 7),
        }
        if mapping == "keyed":
            self.tables = {k: v[r.permutation(7)] for k, v in self.tables.items()}
        self.p_bar = 0.0
        self.hue_cum = float(cfg["pc2"]["h0"])  # ORCcum (round 3 design 1.4)
        self.lat_cls: dict[str, int | None] = {c: None for c in ("f1", "f3", "f4", "f6")}
        self.lat_k = 0  # drawn updates so far (lattice: the cell of the next one)
        self.lat_hist: list[tuple] = []  # the classes of each drawn update (self-test only)
        self.mut_rng = np.random.default_rng(np.random.SeedSequence([key_seed & 0xFFFFFFFF, 99]))
        # round 4 design 1.4: raw PCsize draws its heading level per drawn update from a stream of its own
        self.dir_rng = np.random.default_rng(np.random.SeedSequence([seed, key_seed & 0xFFFFFFFF, PCSIZE_DIR_TAG]))
        self.size_hist: list[tuple] = []  # PCsize and PCahead: (size level, n6 or None) of each drawn update (self-test only)
        self.mark_xy: list[tuple[float, float]] = []  # raw: the centre of each mark drawn (self-test only)
        self.band = np.full(N_BANDS, np.nan)  # ORCband: the five values of the last update
        yy, xx = np.mgrid[0 : self.H, 0 : self.W]
        self._yy, self._xx = yy.astype(np.float32), xx.astype(np.float32)

    # -- marks
    def _blob(self, x: float, y: float, sigma: float, col: np.ndarray, alpha: float) -> None:
        r = int(3 * sigma) + 1
        x0, x1 = max(0, int(x) - r), min(self.W, int(x) + r + 1)
        y0, y1 = max(0, int(y) - r), min(self.H, int(y) + r + 1)
        if x0 >= x1 or y0 >= y1:
            return
        gx = self._xx[y0:y1, x0:x1] - x
        gy = self._yy[y0:y1, x0:x1] - y
        w = (alpha * np.exp(-(gx * gx + gy * gy) / (2 * sigma * sigma)))[..., None]
        patch = self.base[y0:y1, x0:x1]
        patch *= 1 - w
        patch += w * col

    def _step(self, dtheta: float, step: float) -> None:
        self.theta += dtheta
        self.x += step * math.cos(self.theta)
        self.y += step * math.sin(self.theta)
        m = 10.0
        if self.x < m or self.x > self.W - m:
            self.theta = math.pi - self.theta
            self.x = min(max(self.x, m), self.W - m)
        if self.y < m or self.y > self.H - m:
            self.theta = -self.theta
            self.y = min(max(self.y, m), self.H - m)

    def _draw(self, mat: dict) -> None:
        act = mat["active"]
        a_u = int(act.sum())
        if a_u == 0:
            return
        m = int(math.ceil(a_u / self.g["active_per_mark"]))
        alpha = self.g["alpha"]
        rng_ = self.g["raw_ranges"]

        def lvl(c: str) -> float | None:
            v = mat[c][act]
            v = v[np.isfinite(v)]
            if len(v) == 0:
                return None
            lo, hi = rng_[c]
            return float(np.clip((v.mean() - lo) / (hi - lo), 0, 1))

        if self.pc in SIZE_PCS:
            # round 4 design 1.4 (round 5 design 1.4: PCahead is drawn the same way): the size level is the update's value v; f1 and f3 are 0.5; f6 is 0.5 (lattice)
            # or one uniform draw per drawn update (raw: a constant heading pins the walker to a corner)
            v = float(mat["oracle"][0])
            if self.mapping == "lattice":
                self.size_hist.append((v, None))
                self._draw_lattice({"f1": 0.5, "f3": 0.5, "f4": v, "f6": 0.5}, m, alpha)
                return
            n6 = float(self.dir_rng.random())
            if self.mutation == "constant_heading":  # self-test (design 3.7): the negative control of the walk
                n6 = 0.5
            self.size_hist.append((v, n6))
            levels = (0.5, 0.5, v, n6)
        elif self.mapping == "lattice":
            self._draw_lattice({c: lvl(c) for c in ("f1", "f3", "f4", "f6")}, m, alpha)
            return
        else:
            levels = None
        if self.mapping == "raw":
            if levels is None:
                levels = tuple(0.5 if v is None else v for v in (lvl("f1"), lvl("f3"), lvl("f4"), lvl("f6")))
            n1, n3, n4, n6 = levels
            if self.mutation == "random_levels":  # self-test (design 3.8): levels unrelated to the trace
                n1, n3, n4, n6 = (float(v) for v in self.mut_rng.random(4))
            for i in range(m):
                hue = 0.55 - 0.5 * n3 + 0.03 * math.sin(i * 1.7)
                sigma = 2 + 6 * n4
                col = hsv(hue, 0.55, 0.35 + 0.4 * n1)
                # the level sets the heading itself (design 1.4 "the direction of the walk"); mapping it to
                # the turn rate made every session circle on one spot
                heading = 2 * math.pi * n6 + self.phase + 0.25 * math.sin(i * 2.3)
                self._step(heading - self.theta, 4 + 6 * n4)
                self._blob(self.x, self.y, sigma, col, alpha)
                self.mark_xy.append((self.x, self.y))
            return
        hists = {c: _ordinal_hist(mat[c][act]) for c in ("f1", "f3", "f4", "f6")}
        p1, p3, p4, p6 = (_alloc(hists[c], m) for c in ("f1", "f3", "f4", "f6"))
        t = self.tables
        for i in range(m):
            sigma = float(t["sigma"][p4[i]])
            col = hsv(float(t["hue"][p1[i]]) + self.hue_off, 0.55, float(t["light"][p6[i]]))
            self._step(float(t["turn"][p3[i]]), 3 + sigma)
            self._blob(self.x, self.y, sigma, col, alpha)

    def _draw_lattice(self, levels: dict, m: int, alpha: float) -> None:
        """design 1.3: coarse classes with hysteresis; the cell is set by the update ordinal, not by a walk."""
        lc = self.g["lattice"]
        if self.mutation == "random_levels":  # self-test (design 3.8): levels unrelated to the trace
            levels = {c: float(self.mut_rng.random()) for c in levels}
        for c, v in levels.items():
            if v is not None:  # no finite material: the class stays
                self.lat_cls[c] = lattice_class(v, self.lat_cls[c], lc["delta"])
        k1, k3, k4, k6 = (1 if self.lat_cls[c] is None else self.lat_cls[c] for c in ("f1", "f3", "f4", "f6"))
        cells = lattice_cells(self.W, self.H, lc["cell_px"])
        cx, cy = cells[self.lat_k % len(cells)]
        self.lat_k += 1
        self.lat_hist.append((k1, k3, k4, k6))
        col = hsv(lc["hue"][k3], 0.55, lc["light"][k1])
        sigma = float(lc["sigma"][k4])
        rot = 2 * math.pi * k6 / 3
        for i in range(m):
            j = i % 7
            if j == 0:
                x, y = cx, cy
            else:
                a = rot + 2 * math.pi * (j - 1) / 6
                x, y = cx + lc["offset_px"] * math.cos(a), cy + lc["offset_px"] * math.sin(a)
            self._blob(x, y, sigma, col, alpha)

    def _diffuse(self) -> None:
        s = self.g["diffuse_sigma"]
        blurred = ndimage.gaussian_filter(self.base, sigma=(s, s, 0), mode="nearest")
        mix = self.g["diffuse_mix"]
        self.base *= 1 - mix
        self.base += mix * blurred

    def _display(self) -> np.ndarray:
        if self.pc == "ORCband":
            # round 4 design 1.4: five vertical bands along x, each tinted by its own 60 s share (display only);
            # a band whose span is empty (NaN) shows the drawn base
            c = self.cfg["pc2"]
            img = self.base.copy()
            for k, q in enumerate(self.band):
                if np.isfinite(q):
                    x0, x1 = k * self.W // N_BANDS, (k + 1) * self.W // N_BANDS
                    tint = hsv(c["h0"] + c["dh"] * float(q), 0.6, 0.8)
                    img[:, x0:x1] = (1 - c["beta"]) * self.base[:, x0:x1] + c["beta"] * tint
            return img.astype(np.float32)
        if self.pc in TINT_PCS:
            # round 2 (design 1.3, 3.11) and round 3 (design 1.4): the whole canvas is tinted in the display only
            # (the drawn base is never tinted). ORCcum takes the accumulated hue, the others h0 + dh * value.
            c = self.cfg["pc2"]
            h = self.hue_cum if self.pc == "ORCcum" else c["h0"] + c["dh"] * self.p_bar
            tint = hsv(h, 0.6, 0.8)
            return ((1 - c["beta"]) * self.base + c["beta"] * tint).astype(np.float32)
        return self.base.copy()

    def update(self, mat: dict, t: int) -> np.ndarray:
        allowed = set(ALLOWED_MATERIAL) | ({"PC2": set(PC2_EXTRA)}.get(self.pc or "", set())
                                           | (set(ORC_EXTRA) if self.pc in LABEL_PCS else set()))
        extra = set(mat) - allowed
        if extra:
            raise ValueError(f"E1-1: generator received non-material columns {sorted(extra)}")
        a_u = int(mat["active"].sum())
        self.total_active += a_u
        self.recent.append((t, a_u))
        if self.pc == "PC2" or self.pc in ORACLE_PCS:
            col = "p_stuck" if self.pc == "PC2" else "oracle"
            ps = mat[col][np.isfinite(mat[col])]
            if len(ps):
                self.p_bar = float(ps.mean())
                if self.pc == "ORCcum":  # round 3 design 1.4: advanced at every update, also while neutral
                    self.hue_cum = (self.hue_cum + self.cfg["pc2"]["dh"] * self.p_bar) % 1.0
        if self.pc == "ORCband":
            self.band = np.asarray(mat["oracle"], dtype=float).copy()
        if self.pc == "PCcal":
            # round 3 design 1.4: no marks and no neutral rule; only the colour of the ground changes
            return self._display()
        if self.neutral:
            self.buffer.append(mat)
            if self.total_active < self.g["neutral_active_s"]:
                return self.ground_image()
            self.neutral = False
            for b in self.buffer:
                self._draw(b)
            self.buffer = []
        else:
            self._draw(mat)
        if self.drift == "diffuse":
            self._diffuse()
        if self.mutation == "fade_in_absence" and a_u == 0:
            self.base += 0.05 * (self.ground - self.base)
        img = self._display()
        if self.mutation == "neutral_on_low_recent":
            recent = sum(a for (tt, a) in self.recent if tt > t - 600)
            if recent < 30:
                return self.ground_image()
        return img

    def ground_image(self) -> np.ndarray:
        img = np.empty((self.H, self.W, 3), dtype=np.float32)
        img[:] = self.ground
        return img


# ---------------------------------------------------------------------------
# Image measurements
# ---------------------------------------------------------------------------

def deviation(img: np.ndarray, ground: np.ndarray) -> np.ndarray:
    return np.abs(img - ground).max(axis=2)


def coverage(img: np.ndarray, ground: np.ndarray, eps: float) -> float:
    return float((deviation(img, ground) > eps).mean())


def luminance(img: np.ndarray) -> float:
    return float((0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]).mean())


def image_stats(img: np.ndarray, ground: np.ndarray, eps: float) -> np.ndarray:
    """15 values: mean RGB, luminance std, coverage, centroid (x, y), hue histogram (8)."""
    dev = deviation(img, ground)
    lum = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]
    mask = dev > eps
    out = np.zeros(15)
    out[0:3] = img.reshape(-1, 3).mean(axis=0)
    out[3] = lum.std()
    out[4] = mask.mean()
    if mask.any():
        w = dev * mask
        tot = w.sum()
        h, wd = img.shape[:2]
        out[5] = (w.sum(axis=0) * np.arange(wd)).sum() / tot / wd
        out[6] = (w.sum(axis=1) * np.arange(h)).sum() / tot / h
        px = img[mask]
        mx, mn = px.max(axis=1), px.min(axis=1)
        d = np.where(mx - mn > 1e-6, mx - mn, 1.0)
        r, g, b = px[:, 0], px[:, 1], px[:, 2]
        hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
        hist, _ = np.histogram(hue, bins=8, range=(0, 1), weights=w[mask])
        out[7:15] = hist / max(hist.sum(), 1e-12)
    else:
        out[5:7] = 0.5
    return out


def mad(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a - b).mean())


def project(img: np.ndarray, factor: int, sigma: float) -> np.ndarray:
    h, w = img.shape[0] // factor * factor, img.shape[1] // factor * factor
    small = img[:h, :w].reshape(h // factor, factor, w // factor, factor, 3).mean(axis=(1, 3))
    return ndimage.gaussian_filter(small, sigma=(sigma, sigma, 0), mode="nearest")


# ---------------------------------------------------------------------------
# One run: a generator configuration on one session
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Config:
    mapping: str
    drift: str
    sched: Sched
    pc: str | None = None
    mutation: str | None = None
    lam: float | None = None  # PCcal, PCsize, PCahead: the share of updates that show the truth (round 3-5 design 1.4)
    # PCcal0, PCsize-<form>, PCsize0-<form>, PCahead-<form>-<sched>, PCahead0-<form>-<sched>, the grids (...@0.35)
    name_override: str | None = None

    @property
    def name(self) -> str:
        if self.name_override:
            return self.name_override
        if self.pc in ("ORC300", "ORCgap", "ORCcum", "ORCband"):
            return f"{self.pc}-{self.sched.name}"
        if self.pc:
            return self.pc
        n = f"{self.mapping}-{self.drift}-{self.sched.name}"
        return n + (f"-MUT:{self.mutation}" if self.mutation else "")


def band_values(sess: Session, u: int) -> np.ndarray:
    """ORCband (round 4 design 1.4): band k (k = 0..4, left = oldest) holds the stall share of seconds
    [u - 300 + 60k, u - 240 + 60k); a band whose span is empty (end <= 0) is NaN and is not tinted."""
    out = np.full(N_BANDS, np.nan)
    for k in range(N_BANDS):
        a = u - N_BANDS * BAND_S + BAND_S * k
        b = a + BAND_S
        if b > 0:
            out[k] = stall_share(sess, a, b)
    return out


def ahead_values(sess: Session, ups: np.ndarray, ws: int = 60, span: int = ORC_SPAN_S) -> list[float]:
    """PCahead (round 5 design 1.4): a(u_j) is the mean of q300(e) = stall share of [e - 300, e) over the window
    ends e (multiples of ws, e >= span, e <= the session length) with u_j < e <= u_{j+1}, where u_{n+1} is the
    session length: the windows whose end image is the image of u_j (window_shape_features, je). When there is
    no such e, a(u_j) = q(u_j), the stall share of [max(0, u_j - 300), u_j)."""
    dur = sess.duration_s
    stall = np.isin(sess.seg, STALL_CODES).astype(float)
    cum = np.concatenate([[0.0], np.cumsum(stall)])
    out = []
    for j, u in enumerate(ups):
        u = int(u)
        nxt = int(ups[j + 1]) if j + 1 < len(ups) else dur
        first = max((u // ws + 1) * ws, span)  # the smallest multiple of ws above u, not below the span
        es = range(first, min(nxt, dur) + 1, ws)
        if len(es):
            out.append(float(np.mean([(cum[e] - cum[e - span]) / span for e in es])))
        else:
            out.append(stall_share(sess, u - ORC_SPAN_S, u))
    return out


def oracle_values(sess: Session, ups: np.ndarray, conf: Config, seed: int) -> list | None:
    """The value(s) each update of an oracle, PCcal, PCsize or PCahead receives (round 3-5 design 1.4); None for the
    others. Intervals are half-open second ranges [a, b), as seg[a:b]."""
    if conf.pc not in LABEL_PCS:
        return None
    if conf.pc in ("ORC300", "ORCcum"):
        return [stall_share(sess, int(u) - ORC_SPAN_S, int(u)) for u in ups]
    if conf.pc == "ORCgap":
        prevs = [0] + [int(u) for u in ups[:-1]]
        return [stall_share(sess, a, int(u)) for a, u in zip(prevs, ups)]
    if conf.pc == "ORCband":
        return [band_values(sess, int(u)) for u in ups]
    # PCcal, PCsize and PCahead: U then N at every actual update, whatever lambda is (the draws line up across
    # the pilot's grid); each from a stream of its own
    assert conf.lam is not None, f"{conf.pc} needs lam"
    tag = {"PCcal": PCCAL_RNG_TAG, "PCsize": PCSIZE_RNG_TAG, "PCahead": PCAHEAD_RNG_TAG}[conf.pc]
    rng = np.random.default_rng(np.random.SeedSequence([seed, sess.key_seed & 0xFFFFFFFF, tag]))
    truth = (ahead_values(sess, ups) if conf.pc == "PCahead"
             else [stall_share(sess, int(u) - ORC_SPAN_S, int(u)) for u in ups])
    out = []
    for t in truth:
        U, N = float(rng.random()), float(rng.random())
        out.append(t if U < conf.lam else N)
    return out


def run(sess: Session, conf: Config, cfg: dict, seed: int, want_windows: bool, want_final: bool) -> dict:
    ups = schedule(sess, conf.sched, cfg["scheduler_jitter_frac"], seed, cfg["pc1"])
    gen = Generator(conf.mapping, conf.drift, cfg, sess.key_seed, conf.pc, conf.mutation, seed)
    ground = gen.ground
    eps = cfg["canvas"]["coverage_eps"]
    images = [gen.ground_image()]  # images[j] = display after j actual updates
    values = oracle_values(sess, ups, conf, seed)
    prev = 0
    for k, u in enumerate(ups):
        images.append(gen.update(material_slice(sess, prev, int(u), conf.pc == "PC2",
                                                None if values is None else values[k]), int(u)))
        prev = int(u)
    visible = np.array([mad(images[j], images[j + 1]) > 0 for j in range(len(ups))], dtype=bool)
    is_neutral = [bool((img == ground).all()) for img in images]

    def disp_idx_le(t: float) -> int:  # number of updates u <= t
        return int(np.searchsorted(ups, t, side="right"))

    def disp_idx_lt(t: float) -> int:  # number of updates u < t
        return int(np.searchsorted(ups, t, side="left"))

    res: dict = {"sid": sess.sid, "config": conf.name, "n_updates": int(len(ups)), "n_visible": int(visible.sum())}

    # E1-7: neutral after a non-neutral display
    seen = False
    viol = 0
    for nz in is_neutral:
        if not nz:
            seen = True
        elif seen:
            viol += 1
    res["e17_violations"] = viol

    # E1-6 and E1-4: absences of 60 s or more between presses
    p = sess.presses
    gaps = np.diff(p)
    absences = []
    proj = cfg["order"]
    for i in np.nonzero(gaps >= cfg["e16"]["absence_min_s"])[0]:
        s, r = float(p[i]), float(p[i + 1])
        j0, jr = disp_idx_le(s), disp_idx_lt(r)
        change = mad(images[j0], images[jr])
        change_proj = mad(project(images[j0], proj["proj_factor"], proj["proj_sigma"]),
                          project(images[jr], proj["proj_factor"], proj["proj_sigma"]))
        inside = ups[(ups > s) & (ups < r)]
        e14 = e14_end = None
        if len(inside):
            j1 = disp_idx_le(float(inside[0]))
            c1, l1 = coverage(images[j1], ground, eps), luminance(images[j1])
            rd = cfg["e14"]["rel_drop"]

            def drop(j: int) -> bool:
                return coverage(images[j], ground, eps) < c1 * (1 - rd) or luminance(images[j]) < l1 * (1 - rd)

            # design 3.4 compares the display just after the first update with the one at the return;
            # every display in between is checked too (a shrink that recovers before the return is still
            # a shrink while the person may be looking: design section 8)
            # with a single update inside the absence (j1 == jr) there is nothing to compare: the display
            # is compared with itself and cannot fail, so it is not counted as checked (design section 8)
            if jr > j1:
                e14_end = bool(drop(jr))
                e14 = bool(any(drop(j) for j in range(j1 + 1, jr + 1)))
        absences.append({"len": r - s, "change": change, "change_proj": change_proj, "e14_violation": e14,
                         "e14_endpoint_violation": e14_end, "n_inside": int(len(inside))})
    res["absences"] = absences

    if want_final:
        res["final"] = images[-1]

    if want_windows:
        res["windows"] = window_shape_features(sess, ups, visible, images, ground, eps, cfg)
    return res


def window_shape_features(sess: Session, ups: np.ndarray, visible: np.ndarray, images: list, ground: np.ndarray,
                          eps: float, cfg: dict) -> np.ndarray:
    """Shape and update-time features per 60 s window (model B minus the presence part)."""
    ws = cfg["e13"]["window_s"]
    n_w = sess.duration_s // ws
    stats = np.array([image_stats(img, ground, eps) for img in images])
    vis_times = ups[visible]
    feats = np.zeros((n_w, 15 + 14 + 3 + 3))
    for w in range(n_w):
        s, e = w * ws, (w + 1) * ws
        js = int(np.searchsorted(ups, s, side="left"))
        je = int(np.searchsorted(ups, e, side="left"))
        st_e, st_s = stats[je], stats[js]
        d = np.zeros(14)
        d[0] = mad(images[js], images[je]) if je != js else 0.0
        d[1] = st_e[4] - st_s[4]
        d[2] = math.hypot(st_e[5] - st_s[5], st_e[6] - st_s[6])
        d[3:6] = st_e[0:3] - st_s[0:3]
        d[6:14] = st_e[7:15] - st_s[7:15]
        # update times: the visible ones, and every actual update (design 1.5; an update that changes
        # nothing may still be observable, for example as a flash when the wallpaper is set)
        timing = []
        for times in (vis_times, ups):
            n_in = int(((times >= s) & (times < e)).sum())
            before = times[times < e]
            since = float(e - before[-1]) if len(before) else float(e)
            last10 = int(((times >= e - 600) & (times < e)).sum())
            timing += [n_in, since, last10]
        feats[w] = np.concatenate([st_e, d, timing])
    return feats


def presence_features(sess: Session, cfg: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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


def presence_features_long(sess: Session, cfg: dict, L: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
