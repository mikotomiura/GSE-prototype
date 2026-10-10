"""EH1 round 3 checks of the portrait: E1-3 only (L300, L60, L1800), with the calibrated positive control PCcal
and three oracles per scheduler, plus the descriptions (PCcal0, material information, label positives).

Criteria are frozen in .steering/20261010-portrait-eh1-round3/design.md section 3 (commit 58634d65).
Every verdict is per label and per generator configuration; there is no overall pass.

Usage: checks.py <config.json> <SEED> <work dir> <results dir> --world v2 [--jobs N] [--smoke | --pilot]
  --pilot  design 3.9: PC1 and PCcal on the lambda grid only (no real configuration or oracle is run or
           reported); chooses lambda by the frozen rule and writes pilot_e13.json
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import os
import shutil
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
ORACLE_PREFIXES = ("ORC300-", "ORCgap-", "ORCcum-")


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


def configs(cfg: dict) -> dict:
    """design 1.3-1.4: the 8 configurations, PC1, PCcal, PCcal0, the 6 oracles, and the pilot's grid."""
    d = cfg["scheduler_default"]
    default = pt.Sched("clock", d["interval_s"], d["window_s"], False, False)
    recent = pt.Sched("recent", d["interval_s"], d["window_s"], False, False)
    fixed = pt.Sched("fixed", cfg["pccal"]["interval_s"])
    main = [pt.Config(m, dr, s) for s in (default, recent) for m in cfg["mappings"] for dr in cfg["drifts"]]
    pc1 = pt.Config("raw", "none", pt.Sched("stop"), pc="PC1")
    lam = cfg["pccal"]["lam"]
    pccal = pt.Config("raw", "none", fixed, pc="PCcal", lam=lam) if lam is not None else None
    pccal0 = pt.Config("raw", "none", fixed, pc="PCcal", lam=0.0, name_override="PCcal0")
    orc = [pt.Config("ordinal", "none", s, pc=k) for k in ("ORC300", "ORCgap", "ORCcum") for s in (default, recent)]
    grid = [pt.Config("raw", "none", fixed, pc="PCcal", lam=float(x), name_override=f"PCcal@{float(x):.2f}")
            for x in [0.0] + list(cfg["pccal"]["pilot_grid"])]
    return {"main": main, "pc1": pc1, "pccal": pccal, "pccal0": pccal0, "orc": orc, "grid": grid}


def kind_of(name: str) -> str:
    """design 3.2-3.4: which rule a name is judged by."""
    if name == "PC1":
        return "pc1"
    if name == "PCcal":
        return "pccal"
    if name == "PCcal0" or name.startswith("PCcal@"):
        return "descriptive"
    if name.startswith(ORACLE_PREFIXES):
        return "oracle"
    return "config"


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
    path.write_text(json.dumps(clean(obj), indent=1, allow_nan=False), encoding="utf-8")


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
    Returns the label-level flags and a verdict per name."""
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
    reasons = []
    if fit_failed:
        reasons.append("fit_failed")
    if nan:
        reasons.append("nan")
    if not fit_failed and not nan and not (pc1_ok and pccal_ok):
        reasons.append("weak_detector")
    if null_ok is not True:
        reasons.append("null")
    detector_ok = not reasons
    verdicts = {}
    for n, r in recs.items():
        k = kind_of(n)
        if k == "pc1":
            verdicts[n] = "works" if pc1_ok else "fails"
        elif k == "pccal":
            verdicts[n] = "works" if pccal_ok else "fails"
        elif k == "descriptive":
            verdicts[n] = "descriptive"
        elif k == "oracle":
            if fit_failed or nan:
                verdicts[n] = "undecidable"
            elif _lt(r["upper_max"], margin) and null_ok is True and pccal_ok:
                verdicts[n] = "channel_narrow"
            elif _gt(r["lower_max"], pc_lower):
                verdicts[n] = "channel_open"
            else:
                verdicts[n] = "channel_partial"
        else:
            if not detector_ok:
                verdicts[n] = "undecidable"
            else:
                verdicts[n] = "green" if _lt(r["upper_max"], margin) else "red"
    return {"pc1_ok": bool(pc1_ok), "pccal_ok": bool(pccal_ok), "null_ok": null_ok, "nan": bool(nan),
            "fit_failed": bool(fit_failed), "detector_ok": bool(detector_ok), "reasons": reasons,
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
    g.add_argument("--pilot", action="store_true", help="design 3.9: PC1 and PCcal on the lambda grid only")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = 200, 2
    if a.pilot:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = cfg["sets"]["pilot"]["bootstrap"], 0
    seed = int(Path(a.seed_file).read_text().strip())
    work, out = Path(a.work), Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    p_sids = [m["sid"] for m in manifest if m["set"] == "P"]
    C = configs(cfg)
    if a.pilot:
        confs = [C["pc1"]] + C["grid"]
    else:
        if C["pccal"] is None:
            raise SystemExit("config.json pccal.lam is not set: run the pilot first (design 3.9)")
        confs = C["main"] + [C["pc1"], C["pccal"], C["pccal0"]] + C["orc"]
    names = [c.name for c in confs]
    t0 = time.time()

    # ---------------- runs (P only) ----------------
    tasks = [(sid, c) for sid in p_sids for c in confs]
    results: dict[tuple[str, str], np.ndarray] = {}
    with ProcessPoolExecutor(max_workers=a.jobs, initializer=_init, initargs=(cfg, seed, str(work))) as ex:
        for (sid, c), r in zip(tasks, ex.map(_task, tasks, chunksize=8)):
            results[(sid, c.name)] = r["windows"]
    print(f"runs: {len(results)} in {time.time() - t0:.0f} s", flush=True)
    _init(cfg, seed, str(work))

    # ---------------- E1-3 ----------------
    shape = {n: np.vstack([results[(sid, n)] for sid in p_sids]) for n in names}
    del results
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
            print(f"E1-3 {tag} done at {time.time() - t0:.0f} s: detector_ok={e13[tag]['detector_ok']} "
                  f"{e13[tag]['reasons']}", flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    del shape
    e13["primary"] = "L300"
    e13["seed"] = seed

    if a.pilot:
        pc = cfg["pccal"]
        grid = [float(x) for x in pc["pilot_grid"]]
        l300 = e13["L300"]["configs"]
        vals = [l300[f"PCcal@{x:.2f}"]["gain_max"] if f"PCcal@{x:.2f}" in l300 else float("nan") for x in grid]
        sel = select_lambda(grid, vals, pc["target"], pc["upper"])
        e13["selection"] = sel
        e13["_note"] = ("Pilot (design 3.9): SEED + offset, PC1 and PCcal only; not a result of round 3. "
                        "The numbers go to design section 8; this file is not committed.")
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
        print(f"selected lambda = {sel['lam']} ({sel['rule']})")
        return 0

    dump(out / "e13.json", e13)
    dump(out / "material_info.json", {"_note": "Descriptive (design 3.6): no verdict.",
                                      **material_info(p_sids, inputs, cfg, seed)})
    print(f"material info done at {time.time() - t0:.0f} s", flush=True)

    summ = {}
    for n in names:
        summ[n] = {t: e13[t]["configs"].get(n, {}).get("verdict", "undecidable") for t in LABELS}
    summ["_detector"] = {t: {k: e13[t][k] for k in ("pc1_ok", "pccal_ok", "null_ok", "detector_ok", "reasons")}
                         for t in LABELS}
    dump(out / "summary.json", summ)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
