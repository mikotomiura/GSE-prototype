"""Independent recount of the round 5 replicate summary (design 3.10) from the raw attacker values.

Usage: recount_replicates.py <config.json> <dir> <n> <first seed> <bootstrap> <P>
  <dir> holds replicate_<r>.json and replicate_summary.json; <n>, <first seed>, <bootstrap> and <P> are the expected
  values written out by hand (round 5: 20, 20261109, 200, 240), not read from the instruments. The lambdas are read from
  config.json (replicate.lam, fixed before the run).
Checks: the replicate set (count, rep_index, seeds, no duplicates), each replicate's header (controls and lambdas,
config hash, commit, not dirty, bootstrap, P), and every field of the summary: top level (seeds, counts, commit, hash,
n_in_band, reading) and per control (name, lambda, counts, shares, Clopper-Pearson, gain_max / mean4 stats, share in
band, upper_max stats, band, and the not-estimable forms for 0 or 1 measured replicates). Exit 1 on any mismatch.
"""
import json
import math
import statistics
import sys
from pathlib import Path

from scipy.stats import beta

cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
d = Path(sys.argv[2])
N, SEED0, BOOT, P = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
LAM = cfg["replicate"]["lam"]
MARGIN, STRONG, LO_BAND, HI_BAND, MIN_N = 0.03, 0.08, 0.030, 0.045, 10
ATT = ("full/hgb", "full/lr", "small/hgb", "small/lr")
bad = []


def fin(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def is_nan(x):
    return x == "nan" or (isinstance(x, float) and math.isnan(x))


def close(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(a - b) <= 1e-9
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y) for x, y in zip(a, b))
    return a == b


def check(where, key, mine, theirs):
    if not close(mine, theirs):
        bad.append(f"{where} {key}: {mine!r} != {theirs!r}")


# the replicate set and each header
paths = sorted(d.glob("replicate_[0-9][0-9].json"))
reps = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
check("_", "number of replicate files", len(reps), N)
expected_controls = {f"{b}@{lam:.2f}": lam for b, lam in LAM.items()}
first = reps[0] if reps else {}
for i, (p, r) in enumerate(zip(paths, reps)):
    w = p.name
    check(w, "rep_index", r.get("rep_index"), i)
    check(w, "seed", r.get("seed"), SEED0 + i)
    check(w, "controls", r.get("controls"), expected_controls)
    check(w, "instrument_dirty", r.get("instrument_dirty"), False)
    check(w, "instrument_commit", r.get("instrument_commit"), first.get("instrument_commit"))
    check(w, "config_sha256", r.get("config_sha256"), first.get("config_sha256"))
    if not r.get("crashed"):
        check(w, "bootstrap", r.get("bootstrap"), BOOT)
        check(w, "n_sessions", r.get("n_sessions"), P)
check("_", "distinct seeds", len({r.get("seed") for r in reps}), len(reps))

# per replicate and control: the state from the four attackers' raw values
per = {b: [] for b in LAM}
for r in reps:
    for full in expected_controls:
        base = full.split("@")[0]
        rec = {}
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
        per[base].append(rec)

summ = json.loads((d / "replicate_summary.json").read_text(encoding="utf-8"))
check("_", "seeds", summ.get("seeds"), [SEED0 + i for i in range(N)])
check("_", "n_replicates", summ.get("n_replicates"), len(reps))
check("_", "n_crashed", summ.get("n_crashed"), sum(bool(r.get("crashed")) for r in reps))
check("_", "n_fit_failed", summ.get("n_fit_failed"), sum(bool(r.get("fit_failed")) for r in reps))
check("_", "instrument_commit", summ.get("instrument_commit"), first.get("instrument_commit"))
check("_", "config_sha256", summ.get("config_sha256"), first.get("config_sha256"))
check("_", "control set", sorted(summ.get("controls", {})), sorted(LAM))

n_in_band = 0
for base, recs in per.items():
    s = summ.get("controls", {}).get(base)
    if s is None:
        continue  # reported by the control set check
    check(base, "name", s.get("name"), f"{base}@{LAM[base]:.2f}")
    check(base, "lam", s.get("lam"), LAM[base])
    m = [x for x in recs if "gmax" in x]
    n = len(m)
    cnt = {k: sum(x["state"] == k for x in recs) for k in
           ("green_numeric", "detected", "middle", "unmeasurable_nan", "unmeasurable_fit_failed", "unmeasurable_crashed")}
    cnt["strong"] = sum(bool(x.get("strong")) for x in recs)
    check(base, "n_measured", n, s.get("n_measured"))
    check(base, "counts", cnt, s.get("counts"))
    if n == 0:
        check(base, "share_green_numeric (not estimable)", None, s.get("share_green_numeric"))
        check(base, "band", "not_judged", s.get("band"))
        print(f"{base}: no measured replicate; {cnt}")
        continue
    k = cnt["green_numeric"]
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    check(base, "share_green", k / n, s.get("share_green_numeric"))
    check(base, "cp", [lo, hi], s.get("share_green_numeric_ci95"))
    check(base, "share_detected", cnt["detected"] / n, s.get("share_detected"))
    check(base, "share_middle", cnt["middle"] / n, s.get("share_middle"))
    for key, field in (("gain_max", "gmax"), ("gain_mean4", "gmean")):
        xs = [x[field] for x in m]
        t = s.get(key, {})
        check(base, f"{key}.mean", statistics.fmean(xs), t.get("mean"))
        if n > 1:
            check(base, f"{key}.sd", statistics.stdev(xs), t.get("sd"))
        elif not is_nan(t.get("sd")):
            bad.append(f"{base} {key}.sd: one measured replicate, summary {t.get('sd')!r} (expected nan)")
        check(base, f"{key}.min", min(xs), t.get("min"))
        check(base, f"{key}.max", max(xs), t.get("max"))
    check(base, "share_in_band", sum(LO_BAND <= x["gmax"] < HI_BAND for x in m) / n, s.get("share_gain_max_in_band"))
    ups = [x["up"] for x in m]
    t = s.get("upper_max", {})
    check(base, "upper.min", min(ups), t.get("min"))
    check(base, "upper.median", statistics.median(ups), t.get("median"))
    check(base, "upper.max", max(ups), t.get("max"))
    mean = statistics.fmean(x["gmax"] for x in m)
    band = "not_judged" if n < MIN_N else ("in_band" if LO_BAND <= mean < HI_BAND else "out_of_band")
    n_in_band += band == "in_band"
    check(base, "band", band, s.get("band"))
    xs = [x["gmax"] for x in m]
    print(f"{base:42s} n {n:2d} green {k:2d} det {cnt['detected']:2d} mid {cnt['middle']:2d} (strong {cnt['strong']})"
          f" share {k/n:.2f} [{lo:.3f},{hi:.3f}] gmax {mean:+.4f} sd {statistics.stdev(xs) if n > 1 else float('nan'):.4f}"
          f" [{min(xs):+.4f},{max(xs):+.4f}] inband {sum(LO_BAND <= g < HI_BAND for g in xs) / n:.2f}"
          f" mean4 {statistics.fmean(x['gmean'] for x in m):+.4f} up [{min(ups):+.4f},{statistics.median(ups):+.4f},"
          f"{max(ups):+.4f}] band {band}")
check("_", "n_in_band", n_in_band, summ.get("n_in_band"))
check("_", "reading present iff no control in band", n_in_band == 0, "reading" in summ)
print(f"replicates: {len(reps)}; mismatches: {len(bad)}")
for b in bad:
    print("  ", b)
sys.exit(1 if bad else 0)
