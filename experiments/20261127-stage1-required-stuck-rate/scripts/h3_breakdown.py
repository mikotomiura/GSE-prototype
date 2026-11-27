"""結果を見た後の追加（notes の逸脱 1）: H3 の「判定不能でない」を支持と反証に分け、前期の詰まりの件数と並べる。"""
import json, math, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import required_rate as rr

def h3_kind(rng, day, y, score, ndays):
    pos, neg = y == 1, y == 0
    if pos.sum() == 0 or neg.sum() == 0:
        return "none"
    G = (score[pos][:, None] > score[neg][None, :]).astype(float)
    M = rr.boot_mult(rng, ndays)
    wp, wn = M[:, day[pos]], M[:, day[neg]]
    sp, sn = wp.sum(1), wn.sum(1)
    ok = (sp > 0) & (sn > 0)
    if ok.sum() < rr.H3_MIN_OK:
        return "none"
    a = np.einsum("ri,ij,rj->r", wp[ok], G, wn[ok]) / (sp[ok] * sn[ok])
    est = rr.auc(y, score); sd = a.std(ddof=1)
    lo, hi = est - rr.Z * sd, est + rr.Z * sd
    if lo >= rr.H3_LO and hi <= rr.H3_HI: return "support"
    if lo > rr.H3_HI: return "refute"
    return "undet"

seed = int(sys.argv[1]); out = []
for k, (pi, a) in enumerate([(p, a) for p in (0.007, 0.03, 0.05, 0.10, 0.20) for a in (0.5, 0.8)]):
    rng = np.random.default_rng([seed, 9000 + k]); c = {"support": 0, "refute": 0, "undet": 0, "none": 0}; npos = []
    for _ in range(300):
        f, sd, scale = 0.65, 0.5, 1.0
        obs = rng.random(rr.DAYS) < f; od = np.flatnonzero(obs)
        el = int(rng.integers(28, 36)); u = rr.ar1(rng, rr.DAYS, sd, rr.RHO)
        p = rr.sigmoid(math.log(pi / (1 - pi)) + u)[od]
        n = rng.poisson(rr.PER_DAY["c0"] * scale / f, len(od)); s = rng.binomial(n, p)
        ei = np.flatnonzero(od < el)
        day = np.repeat(np.arange(len(ei)), n[ei])
        y = np.concatenate([np.r_[np.ones(x), np.zeros(m - x)] for x, m in zip(s[ei], n[ei])])
        z = rng.normal(0, 1, len(y)) + math.sqrt(2) * rr._ppf(a) * y
        c[h3_kind(rng, day, y, z, len(ei))] += 1; npos.append(int(y.sum()))
    out.append({"pi": pi, "auc": a, **{k2: v / 300 for k2, v in c.items()}, "median_early_stuck": float(np.median(npos))})
    print(out[-1], flush=True)
json.dump(out, open(sys.argv[2], "w"), indent=1)
