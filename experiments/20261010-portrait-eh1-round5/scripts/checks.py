"""EH1 round 5 checks of the portrait: E1-3 only (L300, L60, L1800), with the calibrated positive controls PCcal
(colour), PCsize (the size level of each of the four forms on the 60 s clock, with its baseline PCsize0) and
PCahead (the size level on the real scheduler, reading the labels after the update, with its baseline PCahead0),
four oracles per scheduler, plus the descriptions and the replicates of the 0.035 controls.

Criteria are frozen in .steering/20261010-portrait-eh1-round5/design.md section 3 (commit 92d262fd).
Every verdict is per label and per generator configuration; there is no overall pass. Whether the checks work is
decided per label and per configuration (its form and its scheduler).

Usage: checks.py <config.json> <SEED> <work dir> <results dir> --world v2 [--jobs N]
                 [--smoke | --pilot | --pilot-replicate | --replicate R]
  --pilot            design 3.9: PC1 and PCahead of each form and scheduler on the lambda grid only (target 0.05);
                     writes pilot_e13.json
  --pilot-replicate  design 3.9: the 12 replicate controls on the lambda grid, L300 only (target 0.035), one
                     control at a time; writes pilot_replicate_e13.json
  --replicate R      design 3.10: the 12 replicate controls at their 0.035 lambdas, L300 only; writes
                     replicate_<R>.json
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import portrait as pt

CFG: dict = {}
SEED = 0
WORK = Path()
KINDS = ("hgb", "lr")
FSETS = ("full", "small")
F_COLS = ("f1", "f3", "f4", "f5", "f6")
LABELS = ("L300", "L60", "L1800")
LABEL_ID = {"L300": 0, "L60": 1, "L1800": 2}  # seeds the bootstrap and the permutations of each label
ORACLE_PREFIXES = ("ORC300-", "ORCgap-", "ORCcum-", "ORCband-")


def _init(cfg: dict, seed: int, work: str) -> None:
    global CFG, SEED, WORK
    CFG, SEED, WORK = cfg, seed, Path(work)
    os.environ["OMP_NUM_THREADS"] = "1"


@functools.lru_cache(maxsize=8)
def _session(sid: str) -> pt.Session:
    manifest = {m["sid"]: m for m in json.loads((WORK / "sessions.json").read_text(encoding="utf-8"))}
    return pt.load_session(WORK, manifest[sid])


def _task(args: tuple) -> dict:
    sid, conf = args
    return pt.run(_session(sid), conf, CFG, SEED, True, False)


def forms(cfg: dict) -> list[str]:
    """round 4 design 1.3: the four forms (mapping x drift) of the real configurations."""
    return [f"{m}-{dr}" for m in cfg["mappings"] for dr in cfg["drifts"]]


def scheds(cfg: dict) -> tuple:
    """The two schedulers of the real configurations: the default and recent60 (round 3 design 1.2)."""
    d = cfg["scheduler_default"]
    return (pt.Sched("clock", d["interval_s"], d["window_s"], False, False),
            pt.Sched("recent", d["interval_s"], d["window_s"], False, False))


def ahead_keys(cfg: dict) -> list:
    """round 5 design 1.4: <form>-<sched> of each PCahead; equal to the name of the real configuration it serves."""
    return [f"{f}-{s.name}" for s in scheds(cfg) for f in forms(cfg)]


def replicate_bases(cfg: dict) -> list:
    """round 5 design 3.10: the 12 replicate controls in the fixed order of the report (PCsize of the 4 forms,
    then PCahead of the 4 forms on the default scheduler, then on recent60)."""
    return [f"PCsize-{f}" for f in forms(cfg)] + [f"PCahead-{k}" for k in ahead_keys(cfg)]


def control_config(base: str, lam: float, cfg: dict) -> pt.Config:
    """A replicate control at lambda, named base@<lambda with 2 decimals> (round 5 design 1.4)."""
    parts = base.split("-")
    m, dr = parts[1], parts[2]
    name = f"{base}@{lam:.2f}"
    if parts[0] == "PCsize":
        return pt.Config(m, dr, pt.Sched("fixed", cfg["pcsize"]["interval_s"]), pc="PCsize", lam=lam, name_override=name)
    sched = {s.name: s for s in scheds(cfg)}["-".join(parts[3:])]
    return pt.Config(m, dr, sched, pc="PCahead", lam=lam, name_override=name)


def configs(cfg: dict) -> dict:
    """round 4 design 1.3-1.4 and round 5 design 1.4: the 8 configurations, PC1, PCcal, PCcal0, PCsize and PCsize0
    of each form, PCahead and PCahead0 of each form and scheduler, the 8 oracles, the pilot's grid (PCahead at
    lambda = 0 and on the grid), the replicate pilot's grid (the 12 controls on the grid) and the 12 replicate
    controls at their chosen lambdas."""
    default, recent = scheds(cfg)
    fixed = pt.Sched("fixed", cfg["pccal"]["interval_s"])
    fixed_s = pt.Sched("fixed", cfg["pcsize"]["interval_s"])
    main = [pt.Config(m, dr, s) for s in (default, recent) for m in cfg["mappings"] for dr in cfg["drifts"]]
    pc1 = pt.Config("raw", "none", pt.Sched("stop"), pc="PC1")
    lam = cfg["pccal"]["lam"]
    pccal = pt.Config("raw", "none", fixed, pc="PCcal", lam=lam) if lam is not None else None
    pccal0 = pt.Config("raw", "none", fixed, pc="PCcal", lam=0.0, name_override="PCcal0")
    lams = cfg["pcsize"]["lam"]
    pcsize, pcsize0, grid = [], [], []
    for f in forms(cfg):
        m, dr = f.split("-")
        if lams.get(f) is not None:
            pcsize.append(pt.Config(m, dr, fixed_s, pc="PCsize", lam=float(lams[f]), name_override=f"PCsize-{f}"))
        pcsize0.append(pt.Config(m, dr, fixed_s, pc="PCsize", lam=0.0, name_override=f"PCsize0-{f}"))
        grid += [pt.Config(m, dr, fixed_s, pc="PCsize", lam=float(x), name_override=f"PCsize-{f}@{float(x):.2f}")
                 for x in [0.0] + list(cfg["pcsize"]["pilot_grid"])]
    orc = [pt.Config("ordinal", "none", s, pc=k) for k in ("ORC300", "ORCgap", "ORCcum", "ORCband")
           for s in (default, recent)]
    ah = cfg["pcahead"]
    pcahead, pcahead0, grid_ahead = [], [], []
    for s in (default, recent):
        for f in forms(cfg):
            m, dr = f.split("-")
            key = f"{f}-{s.name}"
            if ah["lam"].get(key) is not None:
                pcahead.append(pt.Config(m, dr, s, pc="PCahead", lam=float(ah["lam"][key]),
                                         name_override=f"PCahead-{key}"))
            pcahead0.append(pt.Config(m, dr, s, pc="PCahead", lam=0.0, name_override=f"PCahead0-{key}"))
            grid_ahead += [pt.Config(m, dr, s, pc="PCahead", lam=float(x), name_override=f"PCahead-{key}@{float(x):.2f}")
                           for x in [0.0] + list(ah["pilot_grid"])]
    rp = cfg["replicate"]
    grid_rep = {b: [control_config(b, float(x), cfg) for x in rp["pilot_grid"]] for b in replicate_bases(cfg)}
    rep_ctl = [control_config(b, float(rp["lam"][b]), cfg) for b in replicate_bases(cfg) if rp["lam"].get(b) is not None]
    return {"main": main, "pc1": pc1, "pccal": pccal, "pccal0": pccal0, "pcsize": pcsize, "pcsize0": pcsize0,
            "orc": orc, "grid": grid, "pcahead": pcahead, "pcahead0": pcahead0, "grid_ahead": grid_ahead,
            "grid_rep": grid_rep, "replicate": rep_ctl}


def kind_of(name: str) -> str:
    """round 4 / 5 design 1.4, 3.2-3.4: which rule a name is judged by. The prefixes are told apart exactly
    (PCsize- without "@", PCsize0-, PCsize-...@, PCahead- without "@", PCahead0-, PCahead-...@, ORCband-), never by
    a bare "PCsize" or "PCa" prefix."""
    if name.startswith("PCahead0-"):
        return "ahead_baseline"
    if name.startswith("PCahead-"):
        return "descriptive" if "@" in name else "pcahead"
    if name == "PC1":
        return "pc1"
    if name == "PCcal":
        return "pccal"
    if name == "PCcal0" or name.startswith("PCcal@"):
        return "descriptive"
    if name.startswith("PCsize0-"):
        return "baseline"
    if name.startswith("PCsize-"):
        return "descriptive" if "@" in name else "pcsize"
    if name.startswith(ORACLE_PREFIXES):
        return "oracle"
    return "config"


def form_of(name: str) -> str:
    """The form (mapping-drift) of a real configuration, a PCsize, PCsize0, PCahead or PCahead0 name."""
    parts = name.split("-")
    return ("-".join(parts[1:3]) if kind_of(name) in ("pcsize", "baseline", "pcahead", "ahead_baseline")
            else "-".join(parts[0:2]))


def ahead_key_of(name: str) -> str:
    """round 5 design 3.2: the <form>-<sched> a real configuration, a PCahead or a PCahead0 name belongs to."""
    return "-".join(name.split("-")[1:]) if kind_of(name) in ("pcahead", "ahead_baseline") else name


# ---------------------------------------------------------------------------
# Statistics (round 2, unchanged)
# ---------------------------------------------------------------------------

def auc_prep(score: np.ndarray, y: np.ndarray) -> tuple:
    order = np.argsort(score, kind="mergesort")
    _, start = np.unique(score[order], return_index=True)
    return order, start, y[order].astype(float)


def auc_w(prep: tuple, w: np.ndarray) -> float:
    """Weighted AUC (ties count one half) on a presorted score; equal to weighted_auc."""
    order, start, ys = prep
    ww = w[order]
    pos_g = np.add.reduceat(ww * ys, start)
    neg_g = np.add.reduceat(ww * (1 - ys), start)
    neg_before = np.concatenate([[0.0], np.cumsum(neg_g)[:-1]])
    num = (pos_g * (neg_before + 0.5 * neg_g)).sum()
    den = pos_g.sum() * neg_g.sum()
    return float(num / den) if den > 0 else float("nan")


def weighted_auc(score: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    return auc_w(auc_prep(score, y), w)


def oof_predict(X: np.ndarray, y: np.ndarray, groups: np.ndarray, kind: str, seed: int, folds: int) -> np.ndarray:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits

    pred = np.zeros(len(y))
    with threadpool_limits(1):
        for tr, te in GroupKFold(n_splits=folds).split(X, y, groups):
            if kind == "hgb":
                model = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, early_stopping=False,
                                                       random_state=seed)
            else:
                model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                      LogisticRegression(max_iter=2000))
            model.fit(X[tr], y[tr])
            pred[te] = model.predict_proba(X[te])[:, 1]
    return pred


def _fit_job(args: tuple) -> tuple:
    """design 3.1: a fold whose training side holds one class cannot be fitted; that is reported, not raised."""
    key, X, y, groups, kind, seed, folds = args
    try:
        return key, oof_predict(X, y, groups, kind, seed, folds)
    except ValueError:
        return key, None


def _boot_job(args: tuple) -> tuple:
    """Bootstrap gains of one configuration: (fset/kind) -> array of AUC(B) - AUC(A) over the draws."""
    name, preds_b, preds_a, y, groups, mults = args
    prep_a = {k: auc_prep(preds_a[k], y) for k in KINDS}
    out = {}
    for (fs, k), pb in preds_b.items():
        prep_b = auc_prep(pb, y)
        out[f"{fs}/{k}"] = np.array([auc_w(prep_b, m[groups]) - auc_w(prep_a[k], m[groups]) for m in mults])
    return name, out


def stratified_permutation(y: np.ndarray, strata: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = y.copy()
    for s in np.unique(strata):
        idx = np.nonzero(strata == s)[0]
        out[idx] = y[rng.permutation(idx)]
    return out


def lagged(F: np.ndarray, sess_idx: np.ndarray, lags: int) -> np.ndarray:
    parts = [F]
    for k in range(1, lags + 1):
        L = np.zeros_like(F)
        L[k:] = F[:-k]
        same = np.zeros(len(F), dtype=bool)
        same[k:] = sess_idx[k:] == sess_idx[:-k]
        L[~same] = 0.0
        parts.append(L)
    return np.hstack(parts)


def clean(o):
    """Standard JSON: non-finite floats become the strings "inf", "-inf" and "nan"."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, np.ndarray):
        return [clean(v) for v in o.tolist()]
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.generic):
        o = o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return "nan" if np.isnan(o) else ("inf" if o > 0 else "-inf")
    return o


def dump(path: Path, obj) -> None:
    """Write through a temporary file so that a stopped run never leaves a half-written JSON (round 5 design 3.10:
    written replicates are kept when a run resumes)."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(clean(obj), indent=1, allow_nan=False), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Verdicts (design 3.1-3.4) and the choice of lambda (design 3.9): pure functions, unit-tested in selftest.py
# ---------------------------------------------------------------------------

def _gt(a: float, b: float) -> bool:
    return bool(np.isfinite(a) and a > b)


def _lt(a: float, b: float) -> bool:
    return bool(np.isfinite(a) and a < b)


def judge(recs: dict, null95: dict | None, cfg: dict, fit_failed: bool) -> dict:
    """recs: name -> {"upper_max", "lower_max", "gain_max", "n_nan_bounds"} (empty when the fits failed).
    null95: name -> 95th percentile of the null (None when no permutation was run).
    Returns the label-level flags, the per-form flags (round 4 design 3.2), the per-form-and-scheduler PCahead
    flags and the per-configuration detector and reasons (round 5 design 3.2), and a verdict per name. A real
    configuration is judged by its own detector (its form's and its own PCahead's)."""
    e = cfg["e13"]
    margin, pc_lower = e["margin"], e["pc_lower"]
    lo, hi = cfg["pccal"]["lower"], cfg["pccal"]["upper"]
    nan = any(r["n_nan_bounds"] > 0 for r in recs.values())
    pc1 = recs.get("PC1")
    pcc = recs.get("PCcal")
    pc1_ok = pc1 is not None and not nan and _gt(pc1["lower_max"], pc_lower)
    pccal_ok = (pcc is not None and not nan and _gt(pcc["lower_max"], lo)
                and bool(np.isfinite(pcc["gain_max"]) and pcc["gain_max"] <= hi))
    if null95 is None:
        null_ok = None
    else:
        null_ok = bool(len(null95) > 0 and all(_lt(v, margin) for v in null95.values()))
    broken = bool(fit_failed or nan)  # round 4 design 3.2: label-wide; then no weak_* or shape_baseline
    slo, shi = cfg["pcsize"]["lower"], cfg["pcsize"]["upper"]
    by_form = {}
    for f in forms(cfg):
        pcs, base = recs.get(f"PCsize-{f}"), recs.get(f"PCsize0-{f}")
        # design 3.2: 1 lower > 0.03, 2 point <= 0.08 (as PCcal), 3 the lambda = 0 baseline's upper < 0.03
        size_ok = (pcs is not None and not nan and _gt(pcs["lower_max"], slo)
                   and bool(np.isfinite(pcs["gain_max"]) and pcs["gain_max"] <= shi))
        base_ok = base is not None and not nan and _lt(base["upper_max"], margin)
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
        if null_ok is not True:
            reasons.append("null")
        by_form[f] = {"pcsize_ok": bool(size_ok and base_ok), "pcsize_detects": bool(size_ok),
                      "baseline_ok": bool(base_ok), "detector_ok": not reasons, "reasons": reasons}
    # round 5 design 3.2: PCahead of each form and scheduler, the same three conditions as PCsize; a real
    # configuration is judged only when the detector of its form works and its own PCahead works
    alo, ahi = cfg["pcahead"]["lower"], cfg["pcahead"]["upper"]
    by_ahead, by_config = {}, {}
    for key in ahead_keys(cfg):
        pa, b0 = recs.get(f"PCahead-{key}"), recs.get(f"PCahead0-{key}")
        a_ok = (pa is not None and not nan and _gt(pa["lower_max"], alo)
                and bool(np.isfinite(pa["gain_max"]) and pa["gain_max"] <= ahi))
        b_ok = b0 is not None and not nan and _lt(b0["upper_max"], margin)
        by_ahead[key] = {"pcahead_ok": bool(a_ok and b_ok), "pcahead_detects": bool(a_ok), "baseline_ok": bool(b_ok)}
        fr = by_form[form_of(key)]["reasons"]
        reasons = [r for r in fr if r != "null"]
        if not broken and not a_ok:
            reasons.append("weak_ahead_pc")
        if not broken and not b_ok:
            reasons.append("ahead_baseline")
        if "null" in fr:
            reasons.append("null")
        by_config[key] = {"detector_ok": not reasons, "reasons": reasons}
    verdicts = {}
    for n, r in recs.items():
        k = kind_of(n)
        if k == "pc1":
            verdicts[n] = "works" if pc1_ok else "fails"
        elif k == "pccal":
            verdicts[n] = "works" if pccal_ok else "fails"
        elif k == "pcsize":
            fo = by_form.get(form_of(n))
            verdicts[n] = "works" if fo is not None and fo["pcsize_ok"] else "fails"
        elif k == "baseline":
            fo = by_form.get(form_of(n))
            verdicts[n] = "baseline_below" if fo is not None and fo["baseline_ok"] else "baseline_not_below"
        elif k == "pcahead":
            ao = by_ahead.get(ahead_key_of(n))
            verdicts[n] = "works" if ao is not None and ao["pcahead_ok"] else "fails"
        elif k == "ahead_baseline":
            ao = by_ahead.get(ahead_key_of(n))
            verdicts[n] = "baseline_below" if ao is not None and ao["baseline_ok"] else "baseline_not_below"
        elif k == "descriptive":
            verdicts[n] = "descriptive"
        elif k == "oracle":
            if broken:
                verdicts[n] = "undecidable"
            elif _lt(r["upper_max"], margin) and null_ok is True and pccal_ok:
                verdicts[n] = "channel_narrow"
            elif _gt(r["lower_max"], pc_lower):
                verdicts[n] = "channel_open"
            else:
                verdicts[n] = "channel_partial"
        else:
            co = by_config.get(n)
            if co is None or not co["detector_ok"]:
                verdicts[n] = "undecidable"
            else:
                verdicts[n] = "green" if _lt(r["upper_max"], margin) else "red"
    return {"pc1_ok": bool(pc1_ok), "pccal_ok": bool(pccal_ok), "null_ok": null_ok, "nan": bool(nan),
            "fit_failed": bool(fit_failed), "forms": by_form, "ahead": by_ahead, "detector": by_config,
            "verdicts": verdicts}


def isotonic_blocks(y: list[float]) -> list[tuple[int, int, float]]:
    """Pool-adjacent-violators with equal weights: non-decreasing fit as blocks (start, end inclusive, value)."""
    blocks: list[list] = []
    for i, v in enumerate(y):
        blocks.append([i, i, float(v), 1])
        while len(blocks) > 1 and blocks[-2][2] > blocks[-1][2]:
            a, b = blocks[-2], blocks[-1]
            n = a[3] + b[3]
            blocks[-2:] = [[a[0], b[1], (a[2] * a[3] + b[2] * b[3]) / n, n]]
    return [(b[0], b[1], b[2]) for b in blocks]


def select_lambda(lams: list[float], vals: list[float], target: float, upper: float) -> dict:
    """design 3.9: choose lambda from the L300 point estimates of the candidates (lambda > 0)."""
    pairs = sorted((float(l), float(v)) for l, v in zip(lams, vals) if np.isfinite(v))
    excluded = sorted(float(l) for l, v in zip(lams, vals) if not np.isfinite(v))
    if not pairs:
        return {"lam": 1.0, "rule": "no finite candidate -> 1.0", "excluded": excluded, "fit": []}
    xs = [p[0] for p in pairs]
    blocks = isotonic_blocks([p[1] for p in pairs])
    fit = [0.0] * len(xs)
    for s, e, v in blocks:
        for i in range(s, e + 1):
            fit[i] = v
    out = {"excluded": excluded, "fit": [[x, f] for x, f in zip(xs, fit)]}
    if all(f < target for f in fit):
        return {**out, "lam": 1.0, "rule": "all fitted values below the target -> 1.0"}
    if xs[0] == min(lams) and fit[0] > upper:
        return {**out, "lam": xs[0], "rule": "the smallest candidate is already above the upper bound -> it"}
    dist = [round(abs(f - target), 6) for f in fit]
    best = min(dist)
    # the run of equal fitted values holding the smallest lambda among the closest ones (two runs only when the
    # target lies between them: the smaller lambda side). A run is a maximal stretch of equal fitted values,
    # whether PAVA pooled it or the raw values were equal.
    i0 = min(i for i, d in enumerate(dist) if d == best)
    s = e = i0
    while s > 0 and round(fit[s - 1], 12) == round(fit[i0], 12):
        s -= 1
    while e < len(fit) - 1 and round(fit[e + 1], 12) == round(fit[i0], 12):
        e += 1
    mid = s + (e - s) // 2  # the middle of the run (the smaller of two middles)
    return {**out, "lam": xs[mid], "rule": "closest fitted value; the middle of its run of equal values"}


def select_grid(l300: dict, bases: list, grid: list, target: float, upper: float) -> dict:
    """round 5 design 3.9: one lambda per control base, each from its own L300 point estimates on the grid
    (names base@<lambda>); the lambda = 0 baseline is not used. A missing or non-finite candidate is left out."""
    grid = [float(x) for x in grid]
    sels = {}
    for b in bases:
        keys = [f"{b}@{x:.2f}" for x in grid]
        vals = [l300[k]["gain_max"] if k in l300 else float("nan") for k in keys]
        sels[b] = select_lambda(grid, vals, target, upper)
    return sels


def select_by_form(l300: dict, cfg: dict) -> dict:
    """round 4 design 3.9: one lambda per form for PCsize (target 0.05); keyed by the form."""
    pc = cfg["pcsize"]
    s = select_grid(l300, [f"PCsize-{f}" for f in forms(cfg)], pc["pilot_grid"], pc["target"], pc["upper"])
    return {b[len("PCsize-"):]: v for b, v in s.items()}


def select_ahead(l300: dict, cfg: dict) -> dict:
    """round 5 design 3.9 (the main run's pilot): one lambda per form and scheduler for PCahead (target 0.05);
    keyed by <form>-<sched>."""
    pa = cfg["pcahead"]
    s = select_grid(l300, [f"PCahead-{k}" for k in ahead_keys(cfg)], pa["pilot_grid"], pa["target"], pa["upper"])
    return {b[len("PCahead-"):]: v for b, v in s.items()}


def select_replicate(l300: dict, cfg: dict) -> dict:
    """round 5 design 3.9 (the replicate pilot): one lambda per replicate control (target 0.035, upper bound
    replicate.upper); keyed by the control base."""
    rp = cfg["replicate"]
    return select_grid(l300, replicate_bases(cfg), rp["pilot_grid"], rp["target"], rp["upper"])


# ---------------------------------------------------------------------------
# E1-3 (design 3.1-3.4)
# ---------------------------------------------------------------------------

def _to_memmap(arr: np.ndarray, d: Path, name: str) -> np.ndarray:
    """Write once, pass by file: joblib sends a memmap by reference instead of dumping it again per call."""
    path = d / f"{name}.npy"
    np.save(path, np.ascontiguousarray(arr))
    return np.load(path, mmap_mode="r")


def e13_target(tag: str, XA: np.ndarray, Y: np.ndarray, G: np.ndarray, strata: np.ndarray, XB: dict,
               cfg: dict, seed: int, jobs: int, nboot: int, nperm: int, scratch: Path | None = None) -> dict:
    """One label. XB: config name -> {"full": X, "small": X}."""
    from joblib import Parallel, delayed

    folds = cfg["e13"]["folds"]
    names = list(XB)
    if scratch is not None:
        scratch.mkdir(parents=True, exist_ok=True)
        XA = _to_memmap(XA, scratch, f"{tag}-A")
        XB = {n: {fs: _to_memmap(XB[n][fs], scratch, f"{tag}-{i}-{fs}") for fs in FSETS} for i, n in enumerate(names)}

    def fit_all(y: np.ndarray, t: str) -> dict:
        js = [((t, "A", None, k), XA, y, G, k, seed, folds) for k in KINDS]
        js += [((t, n, fs, k), XB[n][fs], y, G, k, seed, folds) for n in names for fs in FSETS for k in KINDS]
        return dict(Parallel(n_jobs=jobs, backend="loky")(delayed(_fit_job)(j) for j in js))

    n_sess = int(G.max()) + 1
    res = {"label": tag, "n_windows": int(len(Y)), "n_sessions": n_sess, "prevalence": float(Y.mean()),
           "n_positive_windows": int(Y.sum()), "n_sessions_with_positive": int(len(np.unique(G[Y == 1]))),
           "configs": {}}
    preds = fit_all(Y, "obs")
    if any(v is None for v in preds.values()):
        res["auc_A"] = None
        res.update(judge({}, None if not nperm else {}, cfg, True))
        return res
    ones = np.ones(len(Y))
    auc_a = {k: weighted_auc(preds[("obs", "A", None, k)], Y, ones) for k in KINDS}
    res["auc_A"] = auc_a
    rng = np.random.default_rng(np.random.SeedSequence([seed, 313, LABEL_ID[tag]]))
    mults = [np.bincount(rng.integers(0, n_sess, size=n_sess), minlength=n_sess).astype(float) for _ in range(nboot)]
    boot_jobs = [(n, {(fs, k): preds[("obs", n, fs, k)] for fs in FSETS for k in KINDS},
                  {k: preds[("obs", "A", None, k)] for k in KINDS}, Y, G, mults) for n in names]
    boots = dict(Parallel(n_jobs=jobs, backend="loky")(delayed(_boot_job)(j) for j in boot_jobs))
    for n in names:
        rec = {}
        for fs in FSETS:
            for k in KINDS:
                key = f"{fs}/{k}"
                gain = weighted_auc(preds[("obs", n, fs, k)], Y, ones) - auc_a[k]
                b = boots[n][key]
                rec[key] = {"auc_B": auc_a[k] + gain, "gain": gain,
                            "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]}
        ups = [rec[f"{fs}/{k}"]["ci95"][1] for fs in FSETS for k in KINDS]
        los = [rec[f"{fs}/{k}"]["ci95"][0] for fs in FSETS for k in KINDS]
        gains = [rec[f"{fs}/{k}"]["gain"] for fs in FSETS for k in KINDS]
        rec["n_nan_bounds"] = int(np.isnan(ups).sum() + np.isnan(los).sum())
        rec["upper_max"] = float("nan") if any(np.isnan(ups)) else max(ups)
        rec["lower_max"] = float("nan") if any(np.isnan(los)) else max(los)
        rec["gain_max"] = float("nan") if any(np.isnan(gains)) else max(gains)  # the point estimate (design 3.1)
        res["configs"][n] = rec
    # round 4 / 5 design 3.6 (descriptive): PCsize - PCsize0 of each form and PCahead - PCahead0 of each form and
    # scheduler, per attacker, on the same bootstrap draws
    def pair_diffs(pairs: list) -> dict:
        out = {}
        for tag_, a, b in pairs:
            if a in boots and b in boots:
                out[tag_] = {}
                for fs in FSETS:
                    for k in KINDS:
                        key = f"{fs}/{k}"
                        d = boots[a][key] - boots[b][key]
                        out[tag_][key] = {"gain_diff": res["configs"][a][key]["gain"] - res["configs"][b][key]["gain"],
                                          "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}
        return out

    res["pcsize_minus_baseline"] = pair_diffs([(f, f"PCsize-{f}", f"PCsize0-{f}") for f in forms(cfg)])
    res["pcahead_minus_baseline"] = pair_diffs([(k, f"PCahead-{k}", f"PCahead0-{k}") for k in ahead_keys(cfg)])
    null95 = None
    if nperm:
        null = {n: [] for n in names}
        prng = np.random.default_rng(np.random.SeedSequence([seed, 911, LABEL_ID[tag]]))
        fit_failed_null = False
        for pi in range(nperm):
            yp = stratified_permutation(Y, strata, prng)
            pp = fit_all(yp, f"perm{pi}")
            if any(v is None for v in pp.values()):
                fit_failed_null = True
                break
            aa = {k: weighted_auc(pp[(f"perm{pi}", "A", None, k)], yp, ones) for k in KINDS}
            for n in names:
                null[n].append(max(weighted_auc(pp[(f"perm{pi}", n, fs, k)], yp, ones) - aa[k]
                                   for fs in FSETS for k in KINDS))
        if fit_failed_null:
            res.update(judge(res["configs"], None, cfg, True))
            return res
        null95 = {n: float(np.percentile(v, 95)) for n, v in null.items()}
        for n in names:
            res["configs"][n]["null_gain_max_by_perm"] = null[n]
            res["configs"][n]["null95"] = null95[n]
    j = judge(res["configs"], null95, cfg, False)
    for n, v in j.pop("verdicts").items():
        res["configs"][n]["verdict"] = v
    res.update(j)
    return res


def e13_labels(p_sids: list, cfg: dict) -> dict:
    """The three labels (design 1.5): model A, labels, groups, null strata, and the rows each label uses.
    Rows are all 60 s windows of the P sessions in order; L300 and L1800 keep the windows with a full span."""
    spans = {"L300": cfg["e13"]["long_s"], "L1800": cfg["e13"]["long_s_1800"]}
    edges = {"L300": cfg["e13"]["strata_edges_long"], "L1800": cfg["e13"]["strata_edges_1800"]}
    parts: dict[str, list] = {"XA": [], "Y": [], "ACT": [], "G": []}
    long_parts = {t: {"EX": [], "YL": [], "ACTL": [], "V": []} for t in spans}
    for i, sid in enumerate(p_sids):
        s = _session(sid)
        fa, lab, act_n = pt.presence_features(s, cfg)
        for k, v in zip(("XA", "Y", "ACT", "G"), (fa, lab, act_n, np.full(len(lab), i))):
            parts[k].append(v)
        for t, L in spans.items():
            ex, labl, actl, valid = pt.presence_features_long(s, cfg, L)
            for k, v in zip(("EX", "YL", "ACTL", "V"), (ex, labl, actl, valid)):
                long_parts[t][k].append(v)
    XA = np.vstack(parts["XA"])
    Y, ACT, G = (np.concatenate(parts[k]) for k in ("Y", "ACT", "G"))
    e60 = cfg["e13"]["strata_edges"]
    out = {"L60": {"XA": XA, "Y": Y, "G": G, "strata": np.digitize(ACT, e60[1:-1]),
                   "rows": np.ones(len(Y), dtype=bool), "G_all": G}}
    for t in spans:
        lp = long_parts[t]
        EX = np.vstack(lp["EX"])
        YL, ACTL, V = (np.concatenate(lp[k]) for k in ("YL", "ACTL", "V"))
        out[t] = {"XA": np.hstack([XA, EX])[V], "Y": YL[V], "G": G[V],
                  "strata": np.digitize(ACTL[V], edges[t][1:-1]), "rows": V, "G_all": G}
    return out


def attacker_sets(lab: dict, shape: dict, cfg: dict) -> dict:
    """The two attacker feature sets per configuration for one label (round 2 design 1.4). The lags are taken
    on all windows before the label's rows are selected. shape: config name -> stacked window features."""
    rows, xa = lab["rows"], lab["XA"]
    out = {}
    for n, F in shape.items():
        full = lagged(F, lab["G_all"], cfg["e13"]["lags"])[rows]
        out[n] = {"full": np.hstack([xa, full]), "small": np.hstack([xa, F[rows]])}
    return out


def material_info(p_sids: list, inputs: dict, cfg: dict, seed: int) -> dict:
    """design 3.6 (descriptive): gain of model A plus the span mean of p_stuck, or of the F levels."""
    ws = cfg["e13"]["window_s"]
    spans = {"L300": cfg["e13"]["long_s"], "L60": ws, "L1800": cfg["e13"]["long_s_1800"]}
    res = {}
    for tag, span in spans.items():
        PS, FL = [], []
        for sid in p_sids:
            s = _session(sid)
            n_w = s.duration_s // ws
            for w in range(n_w):
                e = (w + 1) * ws
                a = max(0, e - span)
                with np.errstate(all="ignore"):
                    PS.append([np.nanmean(s.feat["p_stuck"][a:e])])
                    FL.append([np.nanmean(s.feat[c][a:e]) for c in F_COLS])
        inp = inputs[tag]
        PS, FL = np.asarray(PS)[inp["rows"]], np.asarray(FL)[inp["rows"]]
        XA, Y, G = inp["XA"], inp["Y"], inp["G"]
        ones = np.ones(len(Y))
        r = {}
        try:
            for k in KINDS:
                a = weighted_auc(oof_predict(XA, Y, G, k, seed, cfg["e13"]["folds"]), Y, ones)
                bp = weighted_auc(oof_predict(np.hstack([XA, PS]), Y, G, k, seed, cfg["e13"]["folds"]), Y, ones)
                bf = weighted_auc(oof_predict(np.hstack([XA, FL]), Y, G, k, seed, cfg["e13"]["folds"]), Y, ones)
                r[k] = {"auc_A": a, "gain_p_stuck": bp - a, "gain_F_levels": bf - a}
        except ValueError:
            r = {"fit_failed": True}
        res[tag] = r
    return res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def git_info(exp_dir: Path) -> dict:
    """The instruments' commit and whether the experiment directory (results/ excluded) is dirty; None when git
    itself fails (an empty output would read as clean)."""
    def run(args: list) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(exp_dir)] + args, capture_output=True, text=True)
    c = run(["rev-parse", "HEAD"])
    d = run(["status", "--porcelain", "--", ".", ":(exclude)results"])
    return {"commit": c.stdout.strip() if c.returncode == 0 else None,
            "dirty": bool(d.stdout.strip()) if d.returncode == 0 else None}


def run_shapes(confs: list, p_sids: list, cfg: dict, seed: int, work: Path, jobs: int) -> dict:
    """Run every configuration on every P session; config name -> the stacked window features (P order)."""
    tasks = [(sid, c) for sid in p_sids for c in confs]
    results: dict = {}
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init, initargs=(cfg, seed, str(work))) as ex:
        for (sid, c), r in zip(tasks, ex.map(_task, tasks, chunksize=8)):
            results[(sid, c.name)] = r["windows"]
    return {c.name: np.vstack([results[(sid, c.name)] for sid in p_sids]) for c in confs}


def e13_l300(confs: list, p_sids: list, inputs: dict, cfg: dict, seed: int, work: Path, jobs: int) -> dict:
    """E1-3 on L300 only for the given configurations (the replicate pilot and the replicates, design 3.9-3.10)."""
    shape = run_shapes(confs, p_sids, cfg, seed, work, jobs)
    inp = inputs["L300"]
    XB = attacker_sets(inp, shape, cfg)
    del shape
    scratch = Path(tempfile.mkdtemp(prefix="e13-", dir=work))
    try:
        return e13_target("L300", inp["XA"], inp["Y"], inp["G"], inp["strata"], XB, cfg, seed, jobs,
                          cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"], scratch / "L300")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


REC_KEYS = ("upper_max", "lower_max", "gain_max", "n_nan_bounds")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("work")
    ap.add_argument("results")
    ap.add_argument("--world", choices=("v2",), required=True)  # design 1.1: world v2 only
    ap.add_argument("--jobs", type=int, default=16)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--smoke", action="store_true", help="fewer bootstrap draws and permutations (pipeline check only)")
    g.add_argument("--pilot", action="store_true", help="design 3.9: PC1 and PCahead on the lambda grid only")
    g.add_argument("--pilot-replicate", action="store_true",
                   help="design 3.9: the 12 replicate controls on the lambda grid, L300 only")
    g.add_argument("--replicate", type=int, default=None, metavar="R",
                   help="design 3.10: the 12 replicate controls at their 0.035 lambdas, L300 only")
    a = ap.parse_args()
    cfg_bytes = Path(a.config).read_bytes()
    cfg = json.loads(cfg_bytes.decode("utf-8"))
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = 200, 2
    if a.pilot:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = cfg["sets"]["pilot"]["bootstrap"], 0
    if a.pilot_replicate or a.replicate is not None:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = cfg["replicate"]["bootstrap"], 0
    seed = int(Path(a.seed_file).read_text().strip())
    work, out = Path(a.work), Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    p_sids = [m["sid"] for m in manifest if m["set"] == "P"]
    C = configs(cfg)
    t0 = time.time()
    _init(cfg, seed, str(work))

    if a.pilot_replicate:
        # design 3.9: one control at a time (the choice is per control, so the result does not depend on it)
        inputs = e13_labels(p_sids, cfg)
        merged, per = {}, {}
        for b, confs in C["grid_rep"].items():
            r = e13_l300(confs, p_sids, inputs, cfg, seed, work, a.jobs)
            merged.update(r["configs"])
            per[b] = {"fit_failed": r["auc_A"] is None, "n_windows": r["n_windows"],
                      "n_positive_windows": r["n_positive_windows"]}
            print(f"replicate pilot {b} done at {time.time() - t0:.0f} s (fit_failed={per[b]['fit_failed']})", flush=True)
        sels = select_replicate(merged, cfg)
        dump(out / "pilot_replicate_e13.json",
             {"_note": ("Replicate pilot (round 5 design 3.9): SEED + 2, P sessions as in the replicates, the 12 controls "
                        "on the grid, L300 only; not a result of round 5. The numbers go to design section 8; this file "
                        "is not committed."), "seed": seed, "per_control": per, "configs": merged, "selection": sels})
        for b in replicate_bases(cfg):
            for x in cfg["replicate"]["pilot_grid"]:
                rr = merged.get(f"{b}@{float(x):.2f}")
                if rr is not None:
                    print(f"  {b}@{float(x):.2f}: gain_max={rr['gain_max']:+.4f} lower_max={rr['lower_max']:+.4f} "
                          f"upper_max={rr['upper_max']:+.4f}")
            print(f"selected lambda {b} = {sels[b]['lam']} ({sels[b]['rule']})")
        print(f"replicate pilot done in {time.time() - t0:.0f} s", flush=True)
        return 0

    if a.replicate is not None:
        bases = replicate_bases(cfg)
        if len(C["replicate"]) != len(bases):
            raise SystemExit("config.json replicate.lam is not set for every control: run the replicate pilot first")
        inputs = e13_labels(p_sids, cfg)
        r = e13_l300(C["replicate"], p_sids, inputs, cfg, seed, work, a.jobs)
        fit_failed = r["auc_A"] is None
        recs = {}
        for c in C["replicate"]:
            rc = r["configs"].get(c.name)
            if rc is not None:
                recs[c.name] = {k: rc[k] for k in REC_KEYS}
                recs[c.name]["attackers"] = {f"{fs}/{k}": {"gain": rc[f"{fs}/{k}"]["gain"],
                                                           "ci95": rc[f"{fs}/{k}"]["ci95"]}
                                             for fs in FSETS for k in KINDS}
        gi = git_info(Path(a.config).resolve().parent)
        dump(out / f"replicate_{a.replicate:02d}.json",
             {"_note": "Replicate (round 5 design 3.10): L300 only, bootstrap from replicate.bootstrap, no null.",
              "rep_index": a.replicate, "seed": seed, "crashed": False, "fit_failed": fit_failed,
              "controls": {c.name: c.lam for c in C["replicate"]},
              "config_sha256": hashlib.sha256(cfg_bytes).hexdigest(), "instrument_commit": gi["commit"],
              "instrument_dirty": gi["dirty"], "bootstrap": cfg["e13"]["bootstrap"], "n_sessions": len(p_sids),
              "n_windows": r["n_windows"], "n_positive_windows": r["n_positive_windows"], "configs": recs})
        print(f"replicate {a.replicate} (seed {seed}) done in {time.time() - t0:.0f} s; fit_failed={fit_failed}", flush=True)
        return 0

    if a.pilot:
        confs = [C["pc1"]] + C["grid_ahead"]
    else:
        if C["pccal"] is None:
            raise SystemExit("config.json pccal.lam is not set (round 3 value 0.1)")
        if len(C["pcsize"]) != len(forms(cfg)):
            raise SystemExit("config.json pcsize.lam is not set for every form (round 4 value 0.35)")
        if len(C["pcahead"]) != len(ahead_keys(cfg)):
            raise SystemExit("config.json pcahead.lam is not set for every form and scheduler: run the pilot first")
        confs = (C["main"] + [C["pc1"], C["pccal"], C["pccal0"]] + C["pcsize"] + C["pcsize0"] + C["orc"]
                 + C["pcahead"] + C["pcahead0"])
    names = [c.name for c in confs]

    # ---------------- runs (P only) ----------------
    shape = run_shapes(confs, p_sids, cfg, seed, work, a.jobs)
    print(f"runs: {len(names) * len(p_sids)} in {time.time() - t0:.0f} s", flush=True)
    _init(cfg, seed, str(work))

    # ---------------- E1-3 ----------------
    inputs = e13_labels(p_sids, cfg)
    e13 = {}
    scratch = Path(tempfile.mkdtemp(prefix="e13-", dir=work))  # under the git-ignored work dir
    try:
        for tag in LABELS:
            inp = inputs[tag]
            XB = attacker_sets(inp, shape, cfg)  # built per label to bound memory
            e13[tag] = e13_target(tag, inp["XA"], inp["Y"], inp["G"], inp["strata"], XB, cfg, seed, a.jobs,
                                  cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"], scratch / tag)
            del XB
            shutil.rmtree(scratch / tag, ignore_errors=True)  # free the disk before the next label
            de = e13[tag]["detector"]
            print(f"E1-3 {tag} done at {time.time() - t0:.0f} s: "
                  + "; ".join(f"{k} detector_ok={de[k]['detector_ok']} {de[k]['reasons']}" for k in de), flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    del shape
    e13["primary"] = "L300"
    e13["seed"] = seed

    if a.pilot:
        sels = select_ahead(e13["L300"]["configs"], cfg)
        e13["selection"] = sels
        e13["_note"] = ("Pilot (round 5 design 3.9): SEED + offset, PC1 and PCahead of each form and scheduler only; "
                        "not a result of round 5. The numbers go to design section 8; this file is not committed.")
        dump(out / "pilot_e13.json", e13)
        for tag in LABELS:
            cs = e13[tag]["configs"]
            print(f"pilot {tag}: positives {e13[tag]['n_positive_windows']} windows in "
                  f"{e13[tag]['n_sessions_with_positive']} sessions; fit_failed={e13[tag]['fit_failed']}")
            for n in names:
                if n in cs:
                    r = cs[n]
                    print(f"  {n}: gain_max={r['gain_max']:+.4f} lower_max={r['lower_max']:+.4f} "
                          f"upper_max={r['upper_max']:+.4f}")
        for k, sel in sels.items():
            print(f"selected lambda {k} = {sel['lam']} ({sel['rule']})")
        return 0

    dump(out / "e13.json", e13)
    dump(out / "material_info.json", {"_note": "Descriptive (design 3.6): no verdict.",
                                      **material_info(p_sids, inputs, cfg, seed)})
    print(f"material info done at {time.time() - t0:.0f} s", flush=True)

    summ = {}
    for n in names:
        summ[n] = {t: e13[t]["configs"].get(n, {}).get("verdict", "undecidable") for t in LABELS}
    summ["_detector"] = {t: {k: e13[t][k] for k in ("pc1_ok", "pccal_ok", "null_ok", "nan", "fit_failed", "forms",
                                                    "ahead", "detector")}
                         for t in LABELS}
    dump(out / "summary.json", summ)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
