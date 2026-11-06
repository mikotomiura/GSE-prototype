"""Keystroke symbolization: a sequence of key presses -> one symbol per second.

The input is a list of key presses (time in integer milliseconds and a key category).
The output has one row per one-second tick at which a symbol is emitted:
(t_ms, x, y, symbol, alpha, path). Symbols 0 to 24 index a 5 x 5 grid over two
smoothed features, x (friction) and y (fluency); symbol 25 marks a run of 14 or more
deletions. No key identity or text is used: only times and the category of each key.

All numeric constants are read from constants.json. Floating-point expressions are written
in a fixed order (left-to-right sums, literal smoothing weights) so that the output is
bit-for-bit reproducible; the conformance check in conformance/ relies on this.

Only the Python standard library is used.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load_constants(path=None):
    with open(path or os.path.join(HERE, "constants.json"), encoding="utf-8") as f:
        return json.load(f)


def clamp01(v):
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def fmax(a, b):
    """Maximum of two finite floats (ties return a)."""
    return b if b > a else a


def phi(x, beta, kappa):
    """Normalization of a raw feature: clamp((x - beta) / (kappa * beta), 0, 1)."""
    if beta <= 0.0:
        return 0.0
    return clamp01((x - beta) / (kappa * beta))


def with_releases(presses, dwell_ms):
    """Add a synthetic release to each press.

    The release of press i is at min(t_i + dwell, max(t_i, t_{i+1} - 1)); the last press is
    released at t + dwell. Returns events (t, is_press, category) in press/release order.
    """
    out = []
    n = len(presses)
    for i, (t, cat) in enumerate(presses):
        rel = t + dwell_ms
        if i + 1 < n:
            rel = min(rel, max(t, presses[i + 1][0] - 1))
        out.append((t, True, cat))
        out.append((rel, False, cat))
    return out


class Features:
    __slots__ = ("f1", "f3", "f4", "f5", "f6")

    def __init__(self, f1=0.0, f3=0.0, f4=0.0, f5=0.0, f6=0.0):
        self.f1, self.f3, self.f4, self.f5, self.f6 = f1, f3, f4, f5, f6

    def copy(self):
        return Features(self.f1, self.f3, self.f4, self.f5, self.f6)


def window_features(buffer, c):
    """Five features over the events within window_ms of the last buffered event.

    buffer: list of (t, is_press, is_deletion). Repeats do not occur in this input.
    f1: median flight time (press minus previous release, kept if below flight_time_max_ms).
    f3: share of presses that are deletions. f4: mean burst length (a burst continues while
    the gap from the previous release is below burst_gap_ms). f5: number of gaps between
    consecutive presses of at least pause_threshold_ms. f6: share of deletion presses
    followed by such a pause.
    """
    if not buffer:
        return Features()
    last_ts = buffer[-1][0]
    cutoff = max(0, last_ts - c["window_ms"])
    events = [e for e in buffer if e[0] >= cutoff]
    if not events:
        return Features()
    fts = []
    last_release = None
    for t, is_press, _ in events:
        if is_press:
            if last_release is not None and t >= last_release:
                ft = float(t - last_release)
                if ft < c["flight_time_max_ms"]:
                    fts.append(ft)
        else:
            last_release = t
    if not fts:
        f1 = 0.0
    else:
        fts.sort()
        n = len(fts)
        f1 = (fts[n // 2 - 1] + fts[n // 2]) / 2.0 if n % 2 == 0 else fts[n // 2]
    presses = [e for e in events if e[1]]
    total = len(presses)
    deletions = sum(1 for e in presses if e[2])
    f3 = deletions / total if total > 0 else 0.0
    bursts = []
    cur = 0
    last_rel = None
    for t, is_press, _ in events:
        if is_press:
            if last_rel is not None:
                gap = max(0, t - last_rel)
                if gap < c["burst_gap_ms"]:
                    cur += 1
                else:
                    if cur > 0:
                        bursts.append(cur)
                    cur = 1
            else:
                cur = 1
        else:
            last_rel = t
    if cur > 0:
        bursts.append(cur)
    f4 = sum(bursts) / len(bursts) if bursts else 0.0
    pause = c["pause_threshold_ms"]
    f5 = float(sum(1 for a, b in zip(presses, presses[1:]) if max(0, b[0] - a[0]) >= pause))
    del_pause = sum(1 for a, b in zip(presses, presses[1:]) if a[2] and max(0, b[0] - a[0]) >= pause)
    f6 = del_pause / deletions if deletions > 0 else 0.0
    return Features(f1, f3, f4, f5, f6)


def silence_observation(s, ctx, c):
    """Features used when no flight time is available and the silence is at least 2 s."""
    so = c["silence_observation"]
    if ctx is not None:
        ts = clamp01((s - so["context_start_s"]) / so["context_span_s"])
        f3c = clamp01(ctx.f3)
        f6c = clamp01(ctx.f6)
        f3 = clamp01(f3c + ts * (1.0 - f3c) * f3c)
        f6 = clamp01(f6c + ts * (1.0 - f6c) * f6c)
    else:
        f6 = clamp01((s - so["no_context_f6_start_s"]) / so["no_context_f6_span_s"])
        f3 = clamp01((s - so["no_context_f3_start_s"]) / so["no_context_f3_span_s"])
        if s >= so["no_context_min_s"]:
            f6 = fmax(f6, so["no_context_f6_min"])
            f3 = fmax(f3, so["no_context_f3_min"])
    return Features(so["f1"], f3, 0.0, s / 2.0, f6)


def transition_adjust(feat, s, ctx, c):
    """Adjust window features during a pause of at least 2 s that follows typing."""
    tf = c["transition_floor"]
    feat.f5 += s / 2.0
    if s >= tf["start_s"]:
        if ctx is not None:
            ts = clamp01((s - tf["start_s"]) / tf["span_s"])
            f6_floor = clamp01(ctx.f6) * ts
            f3_floor = clamp01(ctx.f3) * ts
        else:
            f6_floor = clamp01((s - tf["start_s"]) / tf["span_s"])
            f3_floor = clamp01((s - tf["no_context_f3_start_s"]) / tf["no_context_f3_span_s"])
            if s >= tf["no_context_min_s"]:
                f6_floor = fmax(f6_floor, tf["no_context_f6_min"])
                f3_floor = fmax(f3_floor, tf["no_context_f3_min"])
        feat.f6 = fmax(feat.f6, f6_floor)
        feat.f3 = fmax(feat.f3, f3_floor)


def latent_axes(feat, c):
    b, k = c["beta"], c["normalization_kappa"]
    p1 = phi(feat.f1, b["f1"], k)
    p3 = phi(feat.f3, b["f3"], k)
    p4 = phi(feat.f4, b["f4"], k)
    p5 = phi(feat.f5, b["f5"], k)
    p6 = phi(feat.f6, b["f6"], k)
    xw, yw = c["x_weights"], c["y_weights"]
    x = clamp01(xw["f3"] * p3 + xw["f6"] * p6 + xw["f1"] * p1 + xw["f5"] * p5)
    y = clamp01(yw["f4"] * p4 + yw["f1_complement"] * (1.0 - p1) + yw["f5_complement"] * (1.0 - p5))
    return x, y


def grid_symbol(x, y, c):
    g = c["grid_bins"]
    top = float(g - 1)
    xb = int(min(math.floor(x * float(g)), top))
    yb = int(min(math.floor(y * float(g)), top))
    return max(0, xb) * g + max(0, yb)


class Symbolizer:
    """State machine over ticks and key events for one recording (one session or work block)."""

    def __init__(self, t0, c):
        self.c = c
        self.feature_cats = set(c["key_categories"]["feature"])
        self.deletion_cats = set(c["key_categories"]["deletion"])
        known = self.feature_cats | set(c["key_categories"]["ignored"])
        self.known_cats = known
        self.ex, self.ey = c["smoothing_initial"]["x"], c["smoothing_initial"]["y"]
        self.del_run = 0
        self.pending_run_symbol = False
        self.reset(t0)

    def reset(self, t0):
        self.buffer = []
        self.last_event_ms = t0
        self.next_tick_ms = t0
        self.presses_since_silence = 0
        self.context = None
        self._cache = None

    def key(self, t, is_press, cat):
        if cat not in self.known_cats:
            raise ValueError("unknown key category")
        if cat not in self.feature_cats:
            return
        is_del = cat in self.deletion_cats
        if len(self.buffer) >= self.c["buffer_capacity_events"]:
            self.buffer.pop(0)
        self.buffer.append((t, is_press, is_del))
        self._cache = None
        if is_press:
            elapsed = max(0, t - self.last_event_ms)
            if elapsed > self.c["silence_reset_ms"]:
                self.presses_since_silence += 1
                if self.presses_since_silence >= self.c["silence_reset_presses"]:
                    self.last_event_ms = t
                    self.presses_since_silence = 0
                    self.context = None
            else:
                self.last_event_ms = t
                self.presses_since_silence = 0
            if is_del:
                self.del_run += 1
                if self.del_run >= self.c["backspace_run_threshold"]:
                    self.pending_run_symbol = True
            else:
                self.del_run = 0

    def _features(self):
        if self._cache is None:
            self._cache = window_features(self.buffer, self.c)
        return self._cache.copy()

    def tick(self, now):
        """Process the tick at time now (== next_tick_ms). Returns a row or None."""
        c = self.c
        self.next_tick_ms += c["tick_ms"]
        if self.next_tick_ms < now:
            self.next_tick_ms = now + c["tick_ms"]
        s = max(0, now - self.last_event_ms) / 1000.0
        feat = self._features()
        if feat.f1 > 0.0 and s < c["silence_typing_max_s"]:
            self.context = feat.copy()
            x_raw, y_raw = latent_axes(feat, c)
            self.ex = c["typing_alpha"] * x_raw + c["typing_keep"] * self.ex
            self.ey = c["typing_alpha"] * y_raw + c["typing_keep"] * self.ey
            sym = grid_symbol(self.ex, self.ey, c)
            if self.pending_run_symbol:
                self.pending_run_symbol = False
                sym = c["backspace_run_symbol"]
            return (now, self.ex, self.ey, sym, c["typing_alpha"], "typing")
        if feat.f1 > 0.0:
            transition_adjust(feat, s, self.context, c)
            path = "transition"
        elif s >= c["silence_typing_max_s"]:
            feat = silence_observation(s, self.context, c)
            path = "silence"
        else:
            return None
        alpha = None
        for row in c["silence_alpha"]:
            if s >= row["min_silence_s"]:
                alpha = row["alpha"]
                break
        x_raw, y_raw = latent_axes(feat, c)
        self.ex = alpha * x_raw + (1.0 - alpha) * self.ex
        self.ey = alpha * y_raw + (1.0 - alpha) * self.ey
        return (now, self.ex, self.ey, grid_symbol(self.ex, self.ey, c), alpha, path)


def symbolize(t0, presses, c=None):
    """Symbolize one recording.

    t0: start time of the recording in ms (ticks fall on t0 + k * tick_ms).
    presses: list of (t_ms, category), sorted by time (ties keep their order).
    Returns rows (t_ms, x, y, symbol, alpha, path). Ticks are processed before key events at
    the same time, and no tick is processed after the last event.
    """
    c = c or load_constants()
    sym = Symbolizer(t0, c)
    events = [(t0, "start", None, None), (t0, "start", None, None)]
    events += [(t, "key", p, cat) for t, p, cat in with_releases(presses, c["synthetic_release_ms"])]
    events.sort(key=lambda e: e[0])
    rows = []
    starts_seen = 0
    for t, kind, is_press, cat in events:
        while sym.next_tick_ms <= t:
            r = sym.tick(sym.next_tick_ms)
            if r is not None:
                rows.append(r)
        if kind == "start":
            starts_seen += 1
            if starts_seen == 2:
                sym.reset(t)
        else:
            sym.key(t, is_press, cat)
    return rows
