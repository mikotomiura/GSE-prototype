"""Recompute the round 5 verdicts from e13.json with the formulas of design 3.2-3.4 only, and compare them with
summary.json. Independent of checks.judge: the thresholds are written from the design text, the maxima are taken
from the per-attacker records, and null95 is recomputed from the per-permutation null gains.

Usage: python verify_verdicts.py <e13.json> <summary.json>
"""

import json
import math
import sys

import numpy as np

MARGIN = 0.03        # green: upper max < 0.03; null passes: null95 < 0.03; baseline: upper max < 0.03
PC1_LOWER = 0.10     # PC1 works: lower max > 0.10; oracle open: lower max > 0.10
CAL_LO, CAL_HI = 0.03, 0.08   # PCcal, PCsize and PCahead: lower max > 0.03 and point max <= 0.08
FORMS = ["raw-none", "raw-diffuse", "lattice-none", "lattice-diffuse"]
KEYS = [f"{fs}/{k}" for fs in ("full", "small") for k in ("hgb", "lr")]
SCHEDS = ["I300-W5", "I300-W5-recent60"]
AHEAD = [f"{fo}-{sc}" for sc in SCHEDS for fo in FORMS]  # <form>-<sched> = the name of the real configuration
LABELS = ["L300", "L60", "L1800"]
N_NAMES = 43         # null passes: all 43 null95 < 0.03


def f(x):
    return float(x)


def stats(rec):
    ups = [f(rec[k]["ci95"][1]) for k in KEYS]
    los = [f(rec[k]["ci95"][0]) for k in KEYS]
    gs = [f(rec[k]["gain"]) for k in KEYS]
    nan = sum(math.isnan(v) for v in ups + los)
    return {"up": max(ups) if not nan else math.nan, "lo": max(los) if not nan else math.nan,
            "pt": max(gs) if not any(math.isnan(g) for g in gs) else math.nan, "nan": nan}


def gt(a, b):
    return math.isfinite(a) and a > b


def lt(a, b):
    return math.isfinite(a) and a < b


def kind(n):
    if n.startswith("PCahead0-"):
        return "abase"
    if n.startswith("PCahead-"):
        return "desc" if "@" in n else "pcahead"
    if n == "PC1":
        return "pc1"
    if n == "PCcal":
        return "pccal"
    if n == "PCcal0":
        return "desc"
    if n.startswith("PCsize0-"):
        return "base"
    if n.startswith("PCsize-"):
        return "desc" if "@" in n else "pcsize"
    if n.startswith(("ORC300-", "ORCgap-", "ORCcum-", "ORCband-")):
        return "oracle"
    return "config"


def form(n):
    p = n.split("-")
    return f"{p[1]}-{p[2]}" if kind(n) in ("pcsize", "base", "pcahead", "abase") else f"{p[0]}-{p[1]}"


def akey(n):
    return "-".join(n.split("-")[1:]) if kind(n) in ("pcahead", "abase") else n


def main():
    e13 = json.load(open(sys.argv[1], encoding="utf-8"))
    summ = json.load(open(sys.argv[2], encoding="utf-8"))
    names = [n for n in summ if not n.startswith("_")]
    agree = disagree = 0
    # The set to check must not come from the summary alone: a name dropped from the summary would otherwise drop
    # out of the null and NaN checks too. Design 3.2: 43 names, the same in every label of e13.json.
    if len(names) != N_NAMES:
        print(f"  ! summary has {len(names)} names, design says {N_NAMES}")
        disagree += 1
    for t in LABELS:
        lab = e13[t]
        cs = lab["configs"]
        if set(cs) != set(names):
            print(f"  ! {t}: e13 names differ from summary names: only e13 {sorted(set(cs) - set(names))}, "
                  f"only summary {sorted(set(names) - set(cs))}")
            disagree += 1
        fit_failed = lab.get("auc_A") is None
        S = {n: stats(cs[n]) for n in names if n in cs}
        nan = any(s["nan"] > 0 for s in S.values())
        broken = fit_failed or nan
        pc1_ok = (not nan) and gt(S["PC1"]["lo"], PC1_LOWER)
        pcc = S["PCcal"]
        pccal_ok = (not nan) and gt(pcc["lo"], CAL_LO) and math.isfinite(pcc["pt"]) and pcc["pt"] <= CAL_HI
        null95 = {}
        for n in names:
            v = cs.get(n, {}).get("null_gain_max_by_perm")
            if v is not None:
                null95[n] = float(np.percentile([f(x) for x in v], 95))
                stored = f(cs[n]["null95"])
                if not (math.isfinite(stored) and abs(null95[n] - stored) <= 1e-12):
                    print(f"  ! {t} {n}: null95 recomputed {null95[n]} != stored {cs[n]['null95']}")
                    disagree += 1
        null_ok = len(null95) == len(names) and all(lt(v, MARGIN) for v in null95.values())
        forms = {}
        for fo in FORMS:
            p, b = S[f"PCsize-{fo}"], S[f"PCsize0-{fo}"]
            size_ok = (not nan) and gt(p["lo"], CAL_LO) and math.isfinite(p["pt"]) and p["pt"] <= CAL_HI
            base_ok = (not nan) and lt(b["up"], MARGIN)
            reasons = []
            if fit_failed:
                reasons.append("fit_failed")
            if nan:
                reasons.append("nan")
            if not broken and not (pc1_ok and pccal_ok):
                reasons.append("weak_detector")
            if not broken and not size_ok:
                reasons.append("weak_shape_pc")
            if not broken and not base_ok:
                reasons.append("shape_baseline")
            if not null_ok:
                reasons.append("null")
            forms[fo] = {"detector_ok": not reasons, "reasons": reasons, "size_ok": size_ok, "base_ok": base_ok}
        ahead, confd = {}, {}
        for k in AHEAD:
            p, b = S[f"PCahead-{k}"], S[f"PCahead0-{k}"]
            a_ok = (not nan) and gt(p["lo"], CAL_LO) and math.isfinite(p["pt"]) and p["pt"] <= CAL_HI
            b_ok = (not nan) and lt(b["up"], MARGIN)
            ahead[k] = {"a_ok": a_ok, "b_ok": b_ok}
            fr = forms[form(k)]["reasons"]
            reasons = [r for r in fr if r != "null"]
            if not broken and not a_ok:
                reasons.append("weak_ahead_pc")
            if not broken and not b_ok:
                reasons.append("ahead_baseline")
            if "null" in fr:
                reasons.append("null")
            confd[k] = {"detector_ok": not reasons, "reasons": reasons}
        det = summ["_detector"][t]
        for key, mine in (("pc1_ok", pc1_ok), ("pccal_ok", pccal_ok), ("null_ok", null_ok), ("nan", nan),
                          ("fit_failed", fit_failed)):
            if bool(det[key]) != bool(mine):
                print(f"  ! {t} {key}: recomputed {mine} != summary {det[key]}")
                disagree += 1
        for fo in FORMS:
            d = det["forms"][fo]
            if d["detector_ok"] != forms[fo]["detector_ok"] or d["reasons"] != forms[fo]["reasons"]:
                print(f"  ! {t} {fo}: recomputed {forms[fo]} != summary {d}")
                disagree += 1
        for k in AHEAD:
            d, da = det["detector"][k], det["ahead"][k]
            if d["detector_ok"] != confd[k]["detector_ok"] or d["reasons"] != confd[k]["reasons"]:
                print(f"  ! {t} {k}: recomputed {confd[k]} != summary {d}")
                disagree += 1
            if (da["pcahead_detects"], da["baseline_ok"]) != (ahead[k]["a_ok"], ahead[k]["b_ok"]):
                print(f"  ! {t} {k}: recomputed PCahead {ahead[k]} != summary {da}")
                disagree += 1
        print(f"{t}: pc1_ok={pc1_ok} (lo {S['PC1']['lo']:+.4f}) pccal_ok={pccal_ok} (lo {pcc['lo']:+.4f}, "
              f"pt {pcc['pt']:+.4f}) null_ok={null_ok} (max null95 {max(null95.values()) if null95 else math.nan:+.4f}) "
              f"nan={nan} fit_failed={fit_failed}")
        for fo in FORMS:
            p, b = S[f"PCsize-{fo}"], S[f"PCsize0-{fo}"]
            print(f"   {fo}: PCsize pt {p['pt']:+.4f} lo {p['lo']:+.4f} up {p['up']:+.4f} | PCsize0 pt {b['pt']:+.4f} "
                  f"lo {b['lo']:+.4f} up {b['up']:+.4f} | detector_ok={forms[fo]['detector_ok']} {forms[fo]['reasons']}")
        for k in AHEAD:
            p, b = S[f"PCahead-{k}"], S[f"PCahead0-{k}"]
            print(f"   {k}: PCahead pt {p['pt']:+.4f} lo {p['lo']:+.4f} up {p['up']:+.4f} | PCahead0 pt {b['pt']:+.4f} "
                  f"lo {b['lo']:+.4f} up {b['up']:+.4f} | detector_ok={confd[k]['detector_ok']} {confd[k]['reasons']}")
        for n in names:
            k, s = kind(n), S[n]
            if k == "pc1":
                v = "works" if pc1_ok else "fails"
            elif k == "pccal":
                v = "works" if pccal_ok else "fails"
            elif k == "pcsize":
                v = "works" if forms[form(n)]["size_ok"] and forms[form(n)]["base_ok"] else "fails"
            elif k == "base":
                v = "baseline_below" if forms[form(n)]["base_ok"] else "baseline_not_below"
            elif k == "pcahead":
                v = "works" if ahead[akey(n)]["a_ok"] and ahead[akey(n)]["b_ok"] else "fails"
            elif k == "abase":
                v = "baseline_below" if ahead[akey(n)]["b_ok"] else "baseline_not_below"
            elif k == "desc":
                v = "descriptive"
            elif k == "oracle":
                if broken:
                    v = "undecidable"
                elif lt(s["up"], MARGIN) and null_ok and pccal_ok:
                    v = "channel_narrow"
                elif gt(s["lo"], PC1_LOWER):
                    v = "channel_open"
                else:
                    v = "channel_partial"
            else:
                if n not in confd or not confd[n]["detector_ok"]:
                    v = "undecidable"
                else:
                    v = "green" if lt(s["up"], MARGIN) else "red"
            ok = v == summ[n][t]
            agree += ok
            disagree += not ok
            if k in ("config", "oracle"):
                print(f"   {n:34s} pt {s['pt']:+.4f} lo {s['lo']:+.4f} up {s['up']:+.4f} null95 "
                      f"{null95.get(n, math.nan):+.4f} -> {v}{'' if ok else '  != summary ' + summ[n][t]}")
            elif not ok:
                print(f"   ! {n}: recomputed {v} != summary {summ[n][t]}")
    print(f"verdicts: {agree} agree, {disagree} disagree (incl. flags)")
    return 0 if disagree == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
