"""Summary of the round 5 replicates (design 3.10): descriptive only, no pass or fail.

Usage: summarize_replicates.py <config.json> <SEED> <dir with replicate_<r>.json> <n expected> <out.json>
       summarize_replicates.py crashed <config.json> <SEED> <r> <out dir>   (writes replicate_<r>.json, crashed)
SEED is the main run's seed file; replicate r has seed SEED + replicate.seed_offset + r.
Exit 0 with the summary written; exit 1 without writing it when the replicates are not complete (design 3.10
"the 20 replicates line up": the seeds, the controls and their lambdas, the config hash and the instruments'
commit must match, every non-crashed replicate must hold the 12 controls with their four attackers).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ATTACKERS = ("full/hgb", "full/lr", "small/hgb", "small/lr")


def num(x) -> float:
    """JSON values written by checks.clean: non-finite floats are the strings "nan", "inf" and "-inf"."""
    return float(x) if x is not None else float("nan")


def classify(rec: dict | None, margin: float, lower: float, upper: float) -> dict:
    """design 3.10: one replicate of one control. "unmeasurable" when the record is missing or any of the four
    point estimates or interval ends is not finite; otherwise exactly one of "green_numeric" (upper max < margin),
    "detected" (lower max > lower and point max <= upper) and "middle", with "strong" (lower max > lower and
    point max > upper) as a part of "middle"."""
    if rec is None:
        return {"cls": "unmeasurable", "strong": False}
    vals = []
    for a in ATTACKERS:
        at = rec["attackers"][a]
        vals += [num(at["gain"]), num(at["ci95"][0]), num(at["ci95"][1])]
    if not all(math.isfinite(v) for v in vals):
        return {"cls": "unmeasurable", "strong": False}
    up = max(num(rec["attackers"][a]["ci95"][1]) for a in ATTACKERS)
    lo = max(num(rec["attackers"][a]["ci95"][0]) for a in ATTACKERS)
    gm = max(num(rec["attackers"][a]["gain"]) for a in ATTACKERS)
    if up < margin:
        return {"cls": "green_numeric", "strong": False}
    if lo > lower and gm <= upper:
        return {"cls": "detected", "strong": False}
    return {"cls": "middle", "strong": bool(lo > lower and gm > upper)}


def band_of(gain_max_mean: float, n_measured: int, rp: dict) -> str:
    """design 3.10: "not_judged" with fewer than min_measured measurable replicates; otherwise "in_band" when the
    mean of the point estimate max lies in [band_lo, band_hi), else "out_of_band"."""
    if n_measured < rp["min_measured"]:
        return "not_judged"
    return "in_band" if rp["band_lo"] <= gain_max_mean < rp["band_hi"] else "out_of_band"


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> list:
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def check_complete(reps: list, bases: list, seeds: list) -> None:
    """design 3.10: raise ValueError unless the replicates line up."""
    if len(reps) != len(seeds):
        raise ValueError(f"{len(reps)} replicate files, {len(seeds)} expected")
    got = [int(r["seed"]) for r in reps]
    if len(set(got)) != len(got):
        raise ValueError(f"duplicated seeds: {sorted(got)}")
    if sorted(got) != sorted(seeds):
        raise ValueError(f"seeds {sorted(got)} differ from the expected {sorted(seeds)}")
    for r in reps:
        if int(r["seed"]) != seeds[int(r["rep_index"])]:
            raise ValueError(f"replicate {r['rep_index']} has seed {r['seed']}, expected {seeds[int(r['rep_index'])]}")
    ref = reps[0]
    for r in reps:
        for k in ("controls", "config_sha256", "instrument_commit"):
            if r.get(k) != ref.get(k):
                raise ValueError(f"replicate {r['rep_index']}: {k} differs from replicate {ref['rep_index']}")
        if r.get("instrument_dirty") is not False:
            raise ValueError(f"replicate {r['rep_index']}: the instruments were dirty or unknown")
        names = list(r["controls"])
        if [n.split("@")[0] for n in names] != bases:
            raise ValueError(f"replicate {r['rep_index']}: controls {names} are not the 12 bases in order")
        if r.get("crashed") or r.get("fit_failed"):
            continue
        for n in names:
            rec = r["configs"].get(n)
            if rec is None:
                raise ValueError(f"replicate {r['rep_index']}: control {n} is missing")
            for a in ATTACKERS:
                at = rec.get("attackers", {}).get(a)
                if at is None or "gain" not in at or len(at.get("ci95", [])) != 2:
                    raise ValueError(f"replicate {r['rep_index']}: control {n} lacks attacker {a}")


def summarize(reps: list, cfg: dict, seed: int, n_expected: int) -> dict:
    rp = cfg["replicate"]
    from checks import replicate_bases  # the fixed order of the report (design 3.10)
    bases = replicate_bases(cfg)
    seeds = [seed + rp["seed_offset"] + r for r in range(n_expected)]
    check_complete(reps, bases, seeds)
    reps = sorted(reps, key=lambda r: int(r["rep_index"]))
    margin = cfg["e13"]["margin"]
    out = {"_note": ("Descriptive (round 5 design 3.10): how often the upper bound max of each 0.035 control falls "
                     "below the margin (the numeric condition of green), not an error rate or a power; no pass or "
                     "fail. Read each control with its point estimate and the band rule."),
           "seeds": seeds, "n_replicates": len(reps),
           "n_crashed": sum(bool(r.get("crashed")) for r in reps),
           "n_fit_failed": sum(bool(r.get("fit_failed")) for r in reps),
           "instrument_commit": reps[0]["instrument_commit"], "config_sha256": reps[0]["config_sha256"],
           "controls": {}}
    for b, name in zip(bases, reps[0]["controls"]):
        counts = {"green_numeric": 0, "detected": 0, "middle": 0, "strong": 0,
                  "unmeasurable_nan": 0, "unmeasurable_fit_failed": 0, "unmeasurable_crashed": 0}
        gmax, gmean, upmax = [], [], []
        for r in reps:
            if r.get("crashed"):
                counts["unmeasurable_crashed"] += 1
                continue
            if r.get("fit_failed"):
                counts["unmeasurable_fit_failed"] += 1
                continue
            rec = r["configs"].get(name)
            c = classify(rec, margin, rp["lower"], rp["upper"])
            if c["cls"] == "unmeasurable":
                counts["unmeasurable_nan"] += 1
                continue
            counts[c["cls"]] += 1
            counts["strong"] += int(c["strong"])
            gains = [num(rec["attackers"][a]["gain"]) for a in ATTACKERS]
            gmax.append(max(gains))
            gmean.append(float(np.mean(gains)))
            upmax.append(max(num(rec["attackers"][a]["ci95"][1]) for a in ATTACKERS))
        m = len(gmax)
        rec_out = {"name": name, "lam": reps[0]["controls"][name], "n_measured": m, "counts": counts}
        if m:
            rec_out["share_green_numeric"] = counts["green_numeric"] / m
            rec_out["share_green_numeric_ci95"] = clopper_pearson(counts["green_numeric"], m)
            rec_out["share_detected"] = counts["detected"] / m
            rec_out["share_middle"] = counts["middle"] / m
            for k, v in (("gain_max", gmax), ("gain_mean4", gmean)):
                rec_out[k] = {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)) if m > 1 else float("nan"),
                              "min": float(np.min(v)), "max": float(np.max(v))}
            rec_out["share_gain_max_in_band"] = float(np.mean([rp["band_lo"] <= g < rp["band_hi"] for g in gmax]))
            rec_out["upper_max"] = {"min": float(np.min(upmax)), "median": float(np.median(upmax)),
                                    "max": float(np.max(upmax))}
        else:
            rec_out["share_green_numeric"] = None  # not estimable (design 3.10)
        rec_out["band"] = band_of(rec_out["gain_max"]["mean"] if m else float("nan"), m, rp)
        out["controls"][b] = rec_out
    out["n_in_band"] = sum(c["band"] == "in_band" for c in out["controls"].values())
    if out["n_in_band"] == 0:
        out["reading"] = "no control is in the band: the replicates did not measure near 0.03 (design 3.10)"
    return out


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return "nan" if math.isnan(o) else ("inf" if o > 0 else "-inf")
    return o


def crashed_record(cfg_path: Path, seed: int, r: int) -> dict:
    """design 3.10: a replicate whose process still failed after max_retries runs counts as one replicate with all
    12 controls unmeasurable (reason crashed); it carries the same header as a written replicate."""
    import hashlib

    import checks
    cfg_bytes = cfg_path.read_bytes()
    cfg = json.loads(cfg_bytes.decode("utf-8"))
    gi = checks.git_info(cfg_path.resolve().parent)
    return {"_note": "Replicate (round 5 design 3.10): crashed after the retries; all 12 controls are unmeasurable.",
            "rep_index": r, "seed": seed + cfg["replicate"]["seed_offset"] + r, "crashed": True, "fit_failed": False,
            "controls": {c.name: c.lam for c in checks.configs(cfg)["replicate"]},
            "config_sha256": hashlib.sha256(cfg_bytes).hexdigest(), "instrument_commit": gi["commit"],
            "instrument_dirty": gi["dirty"], "configs": {}}


def main() -> int:
    if sys.argv[1] == "crashed":
        # summarize_replicates.py crashed <config.json> <SEED> <r> <out dir>
        rec = crashed_record(Path(sys.argv[2]), int(Path(sys.argv[3]).read_text().strip()), int(sys.argv[4]))
        Path(sys.argv[5], f"replicate_{int(sys.argv[4]):02d}.json").write_text(json.dumps(rec, indent=1),
                                                                             encoding="utf-8")
        return 0
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    seed = int(Path(sys.argv[2]).read_text().strip())
    d = Path(sys.argv[3])
    n_expected = int(sys.argv[4])
    reps = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("replicate_[0-9][0-9].json"))]
    try:
        s = summarize(reps, cfg, seed, n_expected)
    except ValueError as e:
        print(f"replicates incomplete: {e}", file=sys.stderr)
        return 1
    Path(sys.argv[5]).write_text(json.dumps(clean(s), indent=1, allow_nan=False), encoding="utf-8")
    for b, c in s["controls"].items():
        g = c.get("gain_max", {})
        print(f"{b}: lam={c['lam']} measured={c['n_measured']} green_numeric={c['counts']['green_numeric']} "
              f"detected={c['counts']['detected']} middle={c['counts']['middle']} band={c['band']} "
              f"gain_max_mean={g.get('mean', float('nan')):+.4f}")
    print(f"in band: {s['n_in_band']} of {len(s['controls'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
