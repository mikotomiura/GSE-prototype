"""Round 4 design check: raw walker with n6 drawn uniformly per drawn update (no data; formulas of _draw/_step).
Reports x/y std of mark centres, the share of marks pinned at the 10 px clamp, and the share in the 2nd half."""
import math
import numpy as np


def sim(n_upd, mfun, sfun, n6fun, seed):
    r = np.random.default_rng(seed)
    W, H = 320, 180
    x = r.uniform(.3, .7) * W
    y = r.uniform(.3, .7) * H
    ph = r.uniform(0, 2 * math.pi)
    pts = []
    for k in range(n_upd):
        n6 = n6fun(r, k)
        m = mfun(r)
        n4 = sfun(r)
        for i in range(m):
            th = 2 * math.pi * n6 + ph + 0.25 * math.sin(i * 2.3)
            st = 4 + 6 * n4
            x += st * math.cos(th)
            y += st * math.sin(th)
            x = min(max(x, 10), W - 10)
            y = min(max(y, 10), H - 10)
            pts.append((x, y))
    p = np.array(pts)
    pinned = (np.isclose(p[:, 0], 10) | np.isclose(p[:, 0], W - 10) | np.isclose(p[:, 1], 10) | np.isclose(p[:, 1], H - 10))
    half = pinned[len(pinned) // 2:]
    return p[:, 0].std(), p[:, 1].std(), pinned.mean(), half.mean()


n6s = {"uniform": lambda r, k: r.uniform(), "golden": lambda r, k: (k * 0.6180339887) % 1, "const": lambda r, k: 0.5}
for nn, f6 in n6s.items():
    for name, mf in [("m=6", lambda r: 6), ("m=1..6", lambda r: int(r.integers(1, 7))), ("m=1", lambda r: 1)]:
        for n in [30, 120, 480]:
            s = [sim(n, mf, lambda r: r.uniform(), f6, i) for i in range(5)]
            print(nn, name, n, " ".join(f"{a:.0f}/{b:.0f} pin{c:.2f}/{d:.2f}" for a, b, c, d in s))
