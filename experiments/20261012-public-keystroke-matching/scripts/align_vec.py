"""The alignment of align_ext.align, vectorised over candidate texts (preregistration, "Alignment").

One record x is aligned with many candidate texts ys at once. Every group (p, q) has p >= 1, so row i of the cost
table depends only on rows i - 1 to i - max p; each row is computed for all candidates and text positions with numpy.
The tie rules are those of the template: groups are tried in their order and a later group replaces only on a strict
improvement; at a window end the smallest text position among the minimum wins (argmin returns the first).
The self-test compares costs and groups with align_ext.align.
"""
import os

import numpy as np

from align_ext import INF, T as TEMPLATE

ORDER = tuple(TEMPLATE.ORDER)
MUTATE = os.environ.get("MAIN_MUTATE", "")


def _order(groups, max_group):
    order = list(groups) if groups is not None else list(ORDER)
    return [(p, q) for p, q in order if p <= max_group and q <= max_group]


def _prefix(ys):
    lens = np.array([len(y) for y in ys], dtype=np.int64)
    tmax = int(lens.max()) if len(ys) else 0
    py = np.zeros((len(ys), tmax + 1))
    for c, y in enumerate(ys):
        if any(v < 0 for v in y):
            raise ValueError("align_vec: a text has an invalid segment")  # an input error, not "no path"
        acc = 0
        for j, v in enumerate(y):
            acc = acc + v
            py[c, j + 1] = acc
        py[c, len(y) + 1:] = acc
    return py, lens


def _table(x, ys, lam, order, keep_back):
    """Row M of the cost table (candidates x text positions), the validity mask and, if asked, the back pointers."""
    py, lens = _prefix(ys)
    C, W = py.shape
    valid = np.arange(W)[None, :] <= lens[:, None]
    px = [0]
    for v in x:
        px.append(px[-1] + v)
    M = len(x)
    maxp = max(p for p, _ in order)
    rows = {0: np.full((C, W), INF)}
    rows[0][:, 0] = 0
    back = np.full((M + 1, C, W), -1, dtype=np.int8) if keep_back else None
    pen = {(p, q): lam * (p - 1 + q - 1) for p, q in order}
    dy = {q: py[:, q:] - py[:, :W - q] for q in {q for _, q in order} if q < W}  # q >= W never fits
    for i in range(1, M + 1):
        best = np.full((C, W), INF)
        arg = np.full((C, W), -1, dtype=np.int8)
        for g, (p, q) in enumerate(order):
            if i - p < 0 or q >= W:
                continue
            prev = rows[i - p]
            cand = np.full((C, W), INF)
            cand[:, q:] = prev[:, :W - q] + np.abs((px[i] - px[i - p]) - dy[q]) + pen[(p, q)]
            better = (cand <= best) if MUTATE == "align_vec_tie" else (cand < best)
            best[better] = cand[better]
            arg[better] = g
        best[~valid] = INF
        rows[i] = best
        if keep_back:
            back[i] = arg
        rows.pop(i - maxp, None)
    return rows[M], valid, lens, back


def _last_row(x, ys, lam, order):
    """Row M of the cost table only. The tie rule chooses among paths of equal cost, so the minimum is the same."""
    py, lens = _prefix(ys)
    C, W = py.shape
    invalid = np.arange(W)[None, :] > lens[:, None]
    px = [0]
    for v in x:
        px.append(px[-1] + v)
    maxp = max(p for p, _ in order)
    rows = {0: np.full((C, W), INF)}
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


def costs(x, ys, lam, end, groups=None, max_group=3):
    """Costs of aligning record x with each text in ys (numpy array; inf when no path). end: 'full' or 'window'."""
    if end not in ("full", "window"):
        raise ValueError("end must be window or full")
    if not len(ys):
        return np.zeros(0)
    order = _order(groups, max_group)
    last, valid, lens = _last_row(x, ys, lam, order)
    if end == "full":
        return last[np.arange(len(ys)), lens]
    return np.where(valid, last, INF).min(axis=1)


def align_many(x, ys, lam, end, groups=None, max_group=3):
    """[(cost, groups)] per text, with groups [(i0, i1, j0, j1)] as in align_ext.align; (inf, None) when no path."""
    if end not in ("full", "window"):
        raise ValueError("end must be window or full")
    if not len(ys):
        return []
    order = _order(groups, max_group)
    last, valid, lens, back = _table(x, ys, lam, order, True)
    out = []
    for c in range(len(ys)):
        if end == "full":
            j = int(lens[c])
        else:
            row = np.where(valid[c], last[c], INF)
            j = int(np.argmin(row))
        cost = float(last[c, j])
        if cost == INF:
            out.append((INF, None))
            continue
        i, gs = len(x), []
        while i or j:
            p, q = order[int(back[i, c, j])]
            gs.append((i - p, i, j - q, j))
            i, j = i - p, j - q
        gs.reverse()
        out.append((cost, gs))
    return out
