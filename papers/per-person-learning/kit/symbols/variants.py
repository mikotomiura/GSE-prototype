"""Two variants of the symbol sequence that remove parts of the symbolization.

The symbols of the paper (column o) are grid symbols of the exponentially smoothed features x
and y, emitted every second over overlapping 30 s windows. Two variants are derived from the
same rows:

- Column u (unsmoothed): the grid symbol of the raw values x_raw and y_raw computed at the same
  tick before smoothing, with the same grid (band = min(max(floor(v * 5), 0), 4), symbol =
  x band * 5 + y band). A row whose symbol in o is the deletion-run symbol (25) keeps 25 in u.
  The rows are those of o (same times, same number).
- Column n (non-overlapping): within one recording (one session, or one work block), let s be the
  time of the first row. Only the rows at times exactly s + 30,000 ms * j (j = 1, 2, ...) are kept;
  when no row exists at such a time, that j is skipped. The 30 s windows [t - 30 s, t) of the kept
  rows do not overlap. The symbol of a kept row is its symbol in u.

Both variants still carry memory across windows: during pauses, the features depend on the time
since the last press and on the context of the preceding typing. Column n removes the smoothing
and the overlap of windows, not every source of dependence between symbols.

Only the Python standard library is used.
"""
from symbolizer import Symbolizer, grid_symbol, load_constants, with_releases

THIN_STEP_MS = 30_000


def unsmoothed_symbol(o, x_raw, y_raw, c):
    """Symbol of column u for one row: the deletion-run symbol is kept, otherwise the grid symbol of the raw values."""
    if o == c["backspace_run_symbol"]:
        return o
    return grid_symbol(x_raw, y_raw, c)


def variant_rows(t0, presses, c=None):
    """Symbolize one recording and return rows (t_ms, o, u, x_raw, y_raw, x, y, alpha, path).

    The input contract and the processing order are those of symbolizer.symbolize; the values
    t_ms, o (the symbol), x, y, alpha and path are the values that symbolize returns for the same
    input. x_raw and y_raw are the values of the same tick before smoothing.
    """
    def is_time(v):
        return type(v) is int and v >= 0
    if not is_time(t0) or not all(is_time(p[0]) for p in presses):
        raise ValueError("times must be non-negative integers (ms)")
    if any(b[0] < a[0] for a, b in zip(presses, presses[1:])):
        raise ValueError("presses must be sorted by time")
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
                x_raw, y_raw = sym.last_raw
                rows.append((r[0], r[3], unsmoothed_symbol(r[3], x_raw, y_raw, c), x_raw, y_raw, r[1], r[2], r[4], r[5]))
        if kind == "start":
            starts_seen += 1
            if starts_seen == 2:
                sym.reset(t)
        else:
            sym.key(t, is_press, cat)
    return rows


def thinned_mask(times, step_ms=THIN_STEP_MS):
    """Column n for one recording: True for the rows at times first + step_ms * j (j >= 1).

    times: the row times of one recording (one session or one work block), in order.
    """
    if not times:
        return []
    s = times[0]
    return [t > s and (t - s) % step_ms == 0 for t in times]
