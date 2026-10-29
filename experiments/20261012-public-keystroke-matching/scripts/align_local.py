"""The alignment of align_vec with a free start (exploratory analysis 7, notes.md "Exploratory analyses, part 3").

A copy of align_vec._last_row in which row 0 of the cost table may be 0 at every text position (start "free": the
record may begin at any word of the candidate) instead of only at position 0 (start "first": align_vec). The end is
that of align_vec ("full": the last word; "window": any word). Groups, penalties and the cap on the groups are those of
align_vec; align_vec.py is not changed (it is in the fingerprint of the main cache). The text side (prefix sums) is
prepared once per candidate list and reused across the chunks of a record and across lambda.
"""
import os

import numpy as np

import align_vec
from align_ext import INF

MUTATE = os.environ.get("EXL_MUTATE", "")
CHUNK, MIN_CHUNK = 20, 5


def prepare(ys):
    """(prefix sums, lengths) of the candidate texts (align_vec._prefix)."""
    return align_vec._prefix(ys)


def _last_row(x, prep, lam, order, start):
    py, lens = prep
    C, W = py.shape
    invalid = np.arange(W)[None, :] > lens[:, None]
    px = [0]
    for v in x:
        px.append(px[-1] + v)
    maxp = max(p for p, _ in order)
    rows = {0: np.full((C, W), INF)}
    if start == "free" and MUTATE != "fixed_start":
        rows[0][~invalid] = 0
    else:
        rows[0][:, 0] = 0
    dy = {q: py[:, q:] - py[:, :W - q] for q in {q for _, q in order} if q < W}  # q >= W never fits
    for i in range(1, len(x) + 1):
        best = np.full((C, W), INF)
        for p, q in order:
            if i - p < 0 or q >= W:
                continue
            tmp = np.abs((px[i] - px[i - p]) - dy[q])
            tmp += rows[i - p][:, :W - q]
            tmp += lam * (p - 1 + q - 1)
            np.minimum(best[:, q:], tmp, out=best[:, q:])
        best[invalid] = INF
        rows[i] = best
        rows.pop(i - maxp, None)
    return rows[len(x)], ~invalid, lens


def costs(x, prep, lam, start, end, groups=None, max_group=3):
    """Costs of aligning record x with each prepared text (numpy array; inf when no path). start: 'first' or
    'free'; end: 'full' or 'window'."""
    if start not in ("first", "free") or end not in ("full", "window"):
        raise ValueError("start must be first or free, end full or window")
    C = prep[0].shape[0]
    if not C:
        return np.zeros(0)
    order = align_vec._order(groups, max_group)
    last, valid, lens = _last_row(x, prep, lam, order, start)
    if end == "full":
        return last[np.arange(C), lens]
    return np.where(valid, last, INF).min(axis=1)


def chunks(x, k=CHUNK, min_len=MIN_CHUNK):
    """Consecutive chunks of k values from the start; the last one is dropped when shorter than min_len."""
    out = [list(x[i:i + k]) for i in range(0, len(x), k)]
    if out and len(out[-1]) < min_len and MUTATE != "keep_short_chunk":
        out.pop()
    return out


def scan_costs(x, prep, lam, groups=None, max_group=3):
    """A2-scan: the sum over the chunks of x of the free-start, free-end alignment cost (inf when a chunk has no
    path in a candidate); all candidates tie (0) when x has no chunk. Chunks may overlap or swap order in the
    candidate."""
    per = [costs(ch, prep, lam, "free", "window", groups, max_group) for ch in chunks(x)]
    if not per:
        return np.zeros(prep[0].shape[0])
    if MUTATE == "chunk_min":
        return np.min(per, axis=0)
    return np.sum(per, axis=0)
