"""Independent recount of the round 5 replicate summary (design 3.10) from the raw attacker values.

Usage: recount_replicates.py <dir with replicate_<r>.json and replicate_summary.json>
Recomputes per control: counts, shares, Clopper-Pearson, gain_max / mean4 stats, band, upper_max stats,
and compares with replicate_summary.json. Exit 1 on any mismatch.
"""
import json
import math
import statistics
import sys
from pathlib import Path

from scipy.stats import beta

d = Path(sys.argv[1])
reps = sorted(d.glob("replicate_[0-9][0-9].json"))
summ = json.loads((d / "replicate_summary.json").read_text(encoding="utf-8"))
MARGIN, STRONG, LO_BAND, HI_BAND, MIN_N = 0.03, 0.08, 0.030, 0.045, 10
ATT = ("full/hgb", "full/lr", "small/hgb", "small/lr")
bad = []


def fin(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


per = {}  # base -> list of dicts
for p in reps:
    r = json.loads(p.read_text(encoding="utf-8"))
    for full, lam in r["controls"].items():
        base = full.split("@")[0]
        rec = {"lam": lam, "seed": r["seed"]}
        if r.get("crashed"):
            rec["state"] = "unmeasurable_crashed"
        elif r.get("fit_failed"):
            rec["state"] = "unmeasurable_fit_failed"
        else:
            a = r["configs"][full]["attackers"]
            vals = [(a[k]["gain"], a[k]["ci95"][0], a[k]["ci95"][1]) for k in ATT]
            if not all(fin(x) for v in vals for x in v):
                rec["state"] = "unmeasurable_nan"
            else:
                g = [v[0] for v in vals]
                lo, up = max(v[1] for v in vals), max(v[2] for v in vals)
                rec.update(gmax=max(g), gmean=sum(g) / 4, up=up)
                if up < MARGIN:
                    rec["state"] = "green_numeric"
                elif lo > MARGIN and max(g) <= STRONG:
                    rec["state"] = "detected"
                else:
                    rec["state"] = "middle"
                    rec["strong"] = lo > MARGIN and max(g) > STRONG
        per.setdefault(base, []).append(rec)

print(f"replicates: {len(reps)}; seeds {sorted({x['seed'] for v in per.values() for x in v})[:3]}...")


def close(a, b):
    if isinstance(a, str) or isinstance(b, str) or a is None or b is None:
        return str(a) == str(b)
    return abs(a - b) <= 1e-9


def check(base, key, mine, theirs):
    if not close(mine, theirs):
        bad.append(f"{base} {key}: recount {mine} vs summary {theirs}")


for base, recs in per.items():
    s = summ["controls"][base]
    m = [x for x in recs if "gmax" in x]
    n = len(m)
    cnt = {k: sum(x["state"] == k for x in recs) for k in
           ("green_numeric", "detected", "middle", "unmeasurable_nan", "unmeasurable_fit_failed", "unmeasurable_crashed")}
    cnt["strong"] = sum(bool(x.get("strong")) for x in recs)
    check(base, "n_measured", n, s["n_measured"])
    for k, v in cnt.items():
        check(base, f"counts.{k}", v, s["counts"][k])
    if n:
        k = cnt["green_numeric"]
        lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
        hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
        check(base, "share_green", k / n, s["share_green_numeric"])
        check(base, "cp_lo", lo, s["share_green_numeric_ci95"][0])
        check(base, "cp_hi", hi, s["share_green_numeric_ci95"][1])
        check(base, "share_detected", cnt["detected"] / n, s["share_detected"])
        check(base, "share_middle", cnt["middle"] / n, s["share_middle"])
        for key, field in (("gain_max", "gmax"), ("gain_mean4", "gmean")):
            xs = [x[field] for x in m]
            check(base, f"{key}.mean", statistics.fmean(xs), s[key]["mean"])
            if n > 1:
                check(base, f"{key}.sd", statistics.stdev(xs), s[key]["sd"])
            check(base, f"{key}.min", min(xs), s[key]["min"])
            check(base, f"{key}.max", max(xs), s[key]["max"])
        check(base, "share_in_band", sum(LO_BAND <= x["gmax"] < HI_BAND for x in m) / n, s["share_gain_max_in_band"])
        ups = [x["up"] for x in m]
        check(base, "upper.min", min(ups), s["upper_max"]["min"])
        check(base, "upper.median", statistics.median(ups), s["upper_max"]["median"])
        check(base, "upper.max", max(ups), s["upper_max"]["max"])
        mean = statistics.fmean(x["gmax"] for x in m)
        band = "not_judged" if n < MIN_N else ("in_band" if LO_BAND <= mean < HI_BAND else "out_of_band")
        check(base, "band", band, s["band"])
        print(f"{base:42s} n {n:2d} green {k:2d} det {cnt['detected']:2d} mid {cnt['middle']:2d} (strong {cnt['strong']})"
              f" share {k/n:.2f} [{lo:.3f},{hi:.3f}] gmax {mean:+.4f} mean4 {statistics.fmean(x['gmean'] for x in m):+.4f}"
              f" up med {statistics.median(ups):+.4f} band {band}")
    else:
        check(base, "band", "not_judged", s["band"])
        print(f"{base}: no measured replicate; {cnt}")
check("_", "n_replicates", len(reps), summ["n_replicates"])
print(f"mismatches: {len(bad)}")
for b in bad:
    print("  ", b)
sys.exit(1 if bad else 0)
