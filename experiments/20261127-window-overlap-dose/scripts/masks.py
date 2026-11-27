"""歩み s の列 A の印と列 B の位相（conditions D1）。行の時刻（ms）の列だけを受け、記号は見ない。

列 A: s = 1 は全行。s >= 2 は kit の thinned_mask(times, 1000 * s)（t0 + 1000 * s * j・j >= 1）。
列 B: s >= 2 で、位相 r = 0..s-1 の行の番号の列。位相 r は t - t0 = 1000 * (r + s * j)（j >= 1）の行。
位相どうしは行を共有せず、合わせて t - t0 >= 1000 * s の行の全部になる。位相 0 は列 A と同じ。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.environ.get("KIT_DIR", os.path.realpath(os.path.join(HERE, "../../../papers/per-person-learning/kit/symbols")))
STRIDES = (1, 5, 10, 15, 30)
TICK = 1000
MUT = set()  # m61: s = 1 にも thinned_mask／m62: 行の番号で間引く／m63: 位相 r（r >= 1）の頭に t0 + 1000 r の行を入れる（窓が最初の s 行に掛かる）／m64: 系列をつないで切る


def kit_variants():
    if KIT not in sys.path:
        sys.path.insert(0, KIT)
    import variants
    return variants


def mask_a(times, s):
    """1 系列の列 A の印（真偽の list）。"""
    if s == 1 and "m61" not in MUT:
        return [True] * len(times)
    if "m62" in MUT:
        return [i > 0 and i % s == 0 for i in range(len(times))]
    return kit_variants().thinned_mask(list(times), step_ms=TICK * s)


def phases_b(times, s):
    """1 系列の列 B の位相: 長さ s の list で、各要素は行の番号の list（時刻の順）。"""
    if s < 2:
        raise ValueError("列 B は s >= 2")
    if not len(times):
        return [[] for _ in range(s)]
    t0 = times[0]
    out = [[] for _ in range(s)]
    for i, t in enumerate(times):
        d = t - t0
        if d % TICK:
            continue
        m = d // TICK
        r = m % s
        if m >= s or ("m63" in MUT and m == r and r > 0):
            out[r].append(i)
    return out


def series_masks_a(series_times, s):
    if "m64" in MUT:
        flat = [t for ts in series_times for t in ts]
        m = mask_a(flat, s)
        res, i = [], 0
        for ts in series_times:
            res.append(m[i:i + len(ts)])
            i += len(ts)
        return res
    return [mask_a(ts, s) for ts in series_times]


def series_phases_b(series_times, s):
    if "m64" in MUT:
        flat = [t for ts in series_times for t in ts]
        ph = phases_b(flat, s)
        res, off = [], 0
        for ts in series_times:
            n = len(ts)
            res.append([[i - off for i in p if off <= i < off + n] for p in ph])
            off += n
        return res
    return [phases_b(ts, s) for ts in series_times]
