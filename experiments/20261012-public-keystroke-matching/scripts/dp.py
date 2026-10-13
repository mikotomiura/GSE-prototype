"""R-DP(epsilon): the exploratory differential-privacy form (decisions 55 and 56; notes.md, "Exploratory analyses";
exploratory.json dp). Not in the preregistration; not used for the main conclusions.

Base R3 (event_id, down_time, category). Two mechanisms with the same epsilon, in this order:
(a) segment counts: the count c of counted letter and digit presses of each record segment (the registered segment
    rule; shortcuts not counted) gets two-sided geometric noise Z with alpha = exp(-epsilon) (sensitivity 1);
    Z > 0 adds Z 'letter' presses at slots drawn uniformly (before the first row of the segment, after each counted
    letter or digit press), at the floor of the midpoint of the previous and next rows' times (the previous row's
    time when there is no next row); Z < 0 removes min(|Z|, c) of the counted presses drawn uniformly without
    replacement. BackSpace and every other row are untouched.
(b) intervals: every interval between consecutive rows is clipped at CAP = 2000 ms and gets two-sided geometric noise
    with alpha = exp(-epsilon / CAP) (sensitivity CAP); negative values become 0; times are rebuilt from the first row.
The privacy unit is one segment count and one interval (event level), not a writer. Z = G1 - G2 with G1, G2
independent numpy geometric(1 - alpha) - 1, from the seed use exploratory_dp: a simulation for evaluation, not a
deployable implementation.

origin: for each output row, the index of an input row; an added press takes the index of the next input row after
it (the window rule: a window keeps the rows whose origin lies in its R0 row range).
"""
import math

import numpy as np

from synthetic_logs import SEP_CATS, shortcut_flags

CAP = 2000
MUTATE = __import__("os").environ.get("MAIN_MUTATE", "")


def two_sided_geometric(rng, alpha, size=None):
    p = 1.0 - alpha
    return rng.geometric(p, size) - rng.geometric(p, size)


def _segments(cats):
    """The record segments of the registered rule with their slot rows: [(first row, counted letter/digit rows)].
    A segment runs from the row after the previous closing separator to its closing separator (or the end)."""
    sc = shortcut_flags(cats)
    segs, start, counted = [], 0, []
    has = False
    for i, c in enumerate(cats):
        if sc[i]:
            continue
        if c in ("letter", "digit"):
            counted.append(i)
            has = True
        elif c == "backspace":
            has = True
        elif c in SEP_CATS:
            segs.append((start, counted))
            start, counted, has = i + 1, [], False
    if has:
        segs.append((start, counted))
    return segs


def count_mechanism(rows, eps, rng):
    """(rows, origin) after (a)."""
    cats = [r["down_event"] for r in rows]
    alpha = math.exp(-eps)
    remove, add_after = set(), {}  # add_after[slot row] = number of presses added after it (-1: before row 0)
    for first, counted in _segments(cats):
        z = int(two_sided_geometric(rng, alpha))
        if MUTATE == "dp_no_count_noise":
            z = 0
        if z < 0 and counted:
            k = min(-z, len(counted))
            for j in rng.choice(len(counted), k, replace=False):
                remove.add(counted[int(j)])
        elif z > 0:
            slots = [first - 1] + counted
            for j in rng.integers(0, len(slots), z):
                s = slots[int(j)]
                add_after[s] = add_after.get(s, 0) + 1
    out, origin = [], []

    def add(n, prev_t, next_t, next_idx):
        t = prev_t if next_t is None else (prev_t + next_t) // 2
        for _ in range(n):
            out.append({"event_id": 0, "down_time": t, "down_event": "letter"})
            origin.append(next_idx)

    n = len(rows)
    if add_after.get(-1):
        add(add_after[-1], rows[0]["down_time"], None, 0)
    for i, r in enumerate(rows):
        if i not in remove:
            out.append(dict(r))
            origin.append(i)
        if add_after.get(i):
            nxt = rows[i + 1]["down_time"] if i + 1 < n else None
            add(add_after[i], r["down_time"], nxt, min(i + 1, n - 1))
    return out, origin


def interval_mechanism(times, eps, rng):
    """Times after (b): clipped and noised intervals, rebuilt from the first time."""
    if len(times) < 2:
        return list(times)
    alpha = math.exp(-eps / CAP)
    d = np.diff(np.asarray(times, dtype=float))
    d = np.minimum(d, CAP)
    z = two_sided_geometric(rng, alpha, len(d))
    if MUTATE == "dp_no_interval_noise":
        z = np.zeros(len(d), dtype=np.int64)
    d = np.maximum(d + z, 0)
    return [float(times[0])] + list(float(times[0]) + np.cumsum(d))


def release(r3_rows, eps, rng):
    """(rows, origin) of R-DP(eps) from R3 rows (event_id, down_time, down_event = category)."""
    if not r3_rows:
        return [], []
    rows, origin = count_mechanism(r3_rows, eps, rng)
    times = interval_mechanism([r["down_time"] for r in rows], eps, rng)
    for k, (r, t) in enumerate(zip(rows, times)):
        r["down_time"] = t
        r["event_id"] = k + 1
    return rows, origin


def noisy_times(times, eps, rng):
    """(b) alone on R0 times (the A3 character-pair table of R-DP is built from training logs with these times)."""
    return interval_mechanism(times, eps, rng)
