"""P3 が赤だったことの事後の確かめ（2026-11-03・計算の後）。条件は変えない。
P3 と同じ点（σ_d = 0・D = 100・AUC 0.70・π 0.30）で、(1) 点推定の偏りと模擬の間の SD、
(2) 再標本化の SD との比、(3) 日のブロックと 1 件ずつの再標本化の被覆、(4) 正規近似の区間（点推定 ± 1.96 × 再標本化の SD）の被覆を並べる。
"""
import math
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import daysim as D  # noqa: E402

seed = int(sys.argv[2])
R = int(sys.argv[3])
a, s, prev, av = D.solve_params(0.30, 0.70, 0.0, seed)
rng = np.random.default_rng([seed, 20_000])
ti, tsl, _ = D.population_values(rng, 6, a, s, 0.0, 0.0)
for mode in ("block", "label"):
    pts, sds, cov_p, cov_n, ws = [], [], 0, 0, []
    for _ in range(R):
        day, phat, y = D.gen(rng, 100, 6, a, s, 0.0, 0.0)
        t0 = math.ceil(0.6 * 100)
        k = day >= t0
        day, phat, y = day[k] - t0, phat[k], y[k]
        n = len(y)
        _, ps, _, cs = D.calib_w(y, phat, np.ones((1, n)))
        if mode == "label":
            W = rng.multinomial(n, np.full(n, 1.0 / n), D.B).astype(float)
        else:
            W = D.circ_counts(rng, 40, D.rule_main(40), D.B)[:, day]
        _, bs, ci_, cs2 = D.calib_w(y, phat, W)
        bs = bs[ci_ & cs2]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        sd = bs.std()
        pts.append(ps[0]); sds.append(sd); ws.append(hi - lo)
        cov_p += lo <= tsl <= hi
        cov_n += ps[0] - 1.96 * sd <= tsl <= ps[0] + 1.96 * sd
    pts = np.array(pts)
    print(mode, "truth %.4f" % tsl, "mean point %.4f" % pts.mean(), "median point %.4f" % np.median(pts),
          "SD across sims %.4f" % pts.std(), "mean boot SD %.4f" % np.mean(sds),
          "cov percentile %.3f" % (cov_p / R), "cov normal %.3f" % (cov_n / R), "median width %.3f" % np.median(ws))
