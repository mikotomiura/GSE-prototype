"""Checks of the rhythm stage desk check: item 1 (verdicts, design 3.1-3.3), items 2-4 and 6 (descriptions, 3.4),
the importance of the red candidates (3.6) and the pilot 1 (the lambda of each PC-stall, 3.9).

Design: .steering/20261012-rhythm-stage-desk-check/design.md (frozen 2b7db259; world v4).

The statistics are copied from experiments/20261010-portrait-eh1-round5/scripts/checks.py (auc_prep, auc_w,
weighted_auc, oof_predict, stratified_permutation, isotonic_blocks, select_lambda, the bootstrap and the null) with
two changes the design asks for: the base model is A_speed (design 1.5; the gain is AUC(B) - AUC(A_speed)), and a
classifier whose AUC(A_speed) is at the ceiling is left out of every maximum of its label (design 3.2). A fold whose
training side holds one class is reported as a failed fit (checked before the fit, as ceiling.py); any other error
stops the run.

Usage: checks.py <config.json> <seed file> <work dir> <results dir> [--jobs N] [--smoke | --pilot]
  (no mode)  the main run: 24 candidates, PC1, PC-stall and PC0 of each candidate, PC-corr; three labels; bootstrap
             e13.bootstrap, e13.null_perms permutations; the descriptions (needs <work>/twins replayed)
  --smoke    the same with bootstrap 200 and 2 permutations (pipeline check only)
  --pilot    design 3.9: PC1 and the PC-stall of each candidate on the lambda grid, L300 only, bootstrap
             sets.pilot.bootstrap, no null; one candidate at a time; writes pilot.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import baseline as bl
import stage as st

KINDS = ("hgb", "lr")
FSETS = ("full", "small")
ATTACKERS = tuple(f"{fs}/{k}" for fs in FSETS for k in KINDS)
LABELS = bl.LABELS
LABEL_ID = {"L300": 0, "L60": 1, "L1800": 2}  # seeds the bootstrap and the permutations of each label (as EH1)
REC_KEYS = ("upper_max", "lower_max", "gain_max", "n_nan_bounds")
A_NAMES = [f"act_w{k}" for k in range(5)] + ["gap_max", "gaps_ge2", "gaps_ge10", "since_press", "act_last15m", "t_end"]
EX_NAMES = ["span_gap_max", "span_gaps_ge2", "span_gaps_ge10", "span_act"]
WS_NAMES = ["w_n", "w_med", "w_iqr", "w_run", "w_last10"] + [f"lag{k}_{q}" for k in range(1, 5) for q in ("n", "med")]
SS_NAMES = ["span_n", "span_med", "span_iqr", "span_run", "span_last10"]


# ---------------------------------------------------------------------------
# Statistics (copied from EH1 round 5 checks.py, unchanged)
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


def stratified_permutation(y: np.ndarray, strata: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = y.copy()
    for s in np.unique(strata):
        idx = np.nonzero(strata == s)[0]
        out[idx] = y[rng.permutation(idx)]
    return out


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
    i0 = min(i for i, d in enumerate(dist) if d == best)
    s = e = i0
    while s > 0 and round(fit[s - 1], 12) == round(fit[i0], 12):
        s -= 1
    while e < len(fit) - 1 and round(fit[e + 1], 12) == round(fit[i0], 12):
        e += 1
    mid = s + (e - s) // 2  # the middle of the run (the smaller of two middles)
    return {**out, "lam": xs[mid], "rule": "closest fitted value; the middle of its run of equal values"}


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
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(clean(obj), indent=1, allow_nan=False), encoding="utf-8", newline="\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Names and verdicts (design 3.2, 3.3): pure functions, unit-tested in selftest.py
# ---------------------------------------------------------------------------

def kind_of(name: str) -> str:
    if name == "PC1":
        return "pc1"
    if name == "PC-corr":
        return "descriptive"
    if name.startswith("PCs-"):
        return "descriptive" if "@" in name else "pcs"
    if name.startswith("PC0-"):
        return "pc0"
    if name.startswith("S-"):
        return "candidate"
    raise ValueError(name)


def _gt(a: float, b: float) -> bool:
    return bool(np.isfinite(a) and a > b)


def _lt(a: float, b: float) -> bool:
    return bool(np.isfinite(a) and a < b)


def ceiling_kinds(auc_s: dict | None, cfg: dict) -> list[str]:
    """design 3.2: the classifiers whose AUC(A_speed) is >= ceiling.main_auc (0.90 exactly is at the ceiling)."""
    if auc_s is None:
        return []
    return [k for k in KINDS if np.isfinite(auc_s[k]) and auc_s[k] >= cfg["ceiling"]["main_auc"]]


def maxima(attk: dict, use: list[str]) -> dict:
    """The maxima over the attackers in use of one name: attk = attacker -> {"gain", "ci95"}."""
    ups = [attk[a]["ci95"][1] for a in use]
    los = [attk[a]["ci95"][0] for a in use]
    gains = [attk[a]["gain"] for a in use]
    n_nan = int(np.isnan(ups).sum() + np.isnan(los).sum()) if use else 0
    nanmax = lambda v: float("nan") if (not v or any(np.isnan(v))) else max(v)
    return {"upper_max": nanmax(ups), "lower_max": nanmax(los), "gain_max": nanmax(gains), "n_nan_bounds": n_nan}


def null95_of(null_by_perm: list[dict], use: list[str]) -> float:
    """The 95th percentile over the permutations of the maximum over the attackers in use."""
    if not null_by_perm or not use:
        return float("nan")
    return float(np.percentile([max(p[a] for a in use) for p in null_by_perm], 95))


def judge(attk: dict, nulls: dict | None, auc_s: dict | None, cands: list[str], cfg: dict, fit_failed: bool) -> dict:
    """One label (design 3.2, 3.3).
    attk: name -> attacker -> {"gain", "ci95"} (empty when the fits failed).
    nulls: name -> list over the permutations of attacker -> gain (None when no permutation was run).
    auc_s: kind -> AUC(A_speed) (None when the fits failed).
    Returns the ceiling, the per-name maxima over the attackers in use, the detector of each candidate with its
    reasons, the description of the null over all judged names, and a verdict per name."""
    e = cfg["e13"]
    margin, pc_lower = e["margin"], e["pc_lower"]
    ps = cfg["pc_stall"]
    ceil = ceiling_kinds(auc_s, cfg)
    use = [a for a in ATTACKERS if a.split("/")[1] not in ceil]
    both_ceiling = not use
    rec = {n: maxima(v, use) for n, v in attk.items()}
    nan = any(r["n_nan_bounds"] > 0 for r in rec.values())
    null95 = None if nulls is None else {n: null95_of(v, use) for n, v in nulls.items()}
    broken = bool(fit_failed or nan or both_ceiling)
    pc1 = rec.get("PC1")
    pc1_ok = pc1 is not None and not broken and _gt(pc1["lower_max"], pc_lower)
    detector, verdicts = {}, {}
    for c in cands:
        r, pcs, pc0 = rec.get(c), rec.get(f"PCs-{c}"), rec.get(f"PC0-{c}")
        stall_ok = (pcs is not None and not broken and _gt(pcs["lower_max"], ps["lower"])
                    and bool(np.isfinite(pcs["gain_max"]) and pcs["gain_max"] <= ps["upper"]))
        base_ok = pc0 is not None and not broken and _lt(pc0["upper_max"], margin)
        if null95 is None:
            null_ok = None
        else:
            four = [c, f"PCs-{c}", f"PC0-{c}", "PC1"]
            null_ok = bool(all(n in null95 and _lt(null95[n], margin) for n in four))
        reasons = []
        if fit_failed:
            reasons.append("fit_failed")
        if nan:
            reasons.append("nan")
        if both_ceiling:
            reasons.append("ceiling")
        if not broken and not pc1_ok:
            reasons.append("weak_detector")
        if null_ok is not True and not both_ceiling:  # with no classifier left there is no null to read
            reasons.append("null")
        if not broken and not stall_ok:
            reasons.append("weak_stall_pc")
        if not broken and not base_ok:
            reasons.append("stall_baseline")
        stop_path = (not broken and pc1_ok and null_ok is True and pc0 is not None
                     and _gt(pc0["lower_max"], ps["lower"]))
        detector[c] = {"detector_ok": not reasons, "reasons": reasons, "pcs_ok": bool(stall_ok),
                       "pc0_below": bool(base_ok), "null_ok": null_ok, "stop_path": bool(stop_path)}
        if stop_path:
            v = "red_detected_stop_path"
        elif reasons or r is None:
            v = "undecidable"
        elif _lt(r["upper_max"], margin):
            v = "green"
        elif _gt(r["lower_max"], margin):
            v = "red_detected"
        else:
            v = "red_unconfirmed"
        verdicts[c] = v
    for n in rec:
        k = kind_of(n)
        if k == "pc1":
            verdicts[n] = "works" if pc1_ok else "fails"
        elif k == "pcs":
            d = detector.get(n[4:])
            verdicts[n] = "works" if d is not None and d["pcs_ok"] else "fails"
        elif k == "pc0":
            d = detector.get(n[4:])
            verdicts[n] = "baseline_below" if d is not None and d["pc0_below"] else "baseline_not_below"
        elif k == "descriptive":
            verdicts[n] = "descriptive"
    judged = [n for n in rec if kind_of(n) != "descriptive"]
    null_all = None if null95 is None else bool(judged and all(_lt(null95[n], margin) for n in judged if n in null95))
    return {"ceiling_kinds": ceil, "attackers_used": use, "nan": bool(nan), "fit_failed": bool(fit_failed),
            "pc1_ok": bool(pc1_ok), "null_all_73_ok": null_all, "null95": null95, "maxima": rec,
            "detector": detector, "verdicts": verdicts}


# ---------------------------------------------------------------------------
# Feature tables in a scratch directory (shared by the worker processes through memory maps)
# ---------------------------------------------------------------------------

SCRATCH = Path()
_MM: dict = {}


def _init(scratch: str) -> None:
    global SCRATCH
    SCRATCH = Path(scratch)
    _MM.clear()
    os.environ["OMP_NUM_THREADS"] = "1"


def _mm(name: str) -> np.ndarray:
    if name not in _MM:
        _MM[name] = np.load(SCRATCH / f"{name}.npy", mmap_mode="r")
    return _MM[name]


def save(scratch: Path, name: str, arr: np.ndarray) -> None:
    np.save(scratch / f"{name}.npy", np.ascontiguousarray(arr))


def diffs(F: np.ndarray, sess_idx: np.ndarray, lags: int) -> np.ndarray:
    """design 1.5 (B-full): the window's features minus those of the k-th earlier window (k = 1 .. lags); 0 when the
    earlier window is in another session or before the start."""
    parts = []
    for k in range(1, lags + 1):
        D = np.zeros_like(F)
        same = np.zeros(len(F), dtype=bool)
        same[k:] = sess_idx[k:] == sess_idx[:-k]
        D[k:] = F[k:] - F[:-k]
        D[~same] = 0.0
        parts.append(D)
    return np.hstack(parts)


def build_x(label: str, base: str, cname: str | None, fs: str | None) -> np.ndarray:
    """base: "A" (model A) or "S" (A_speed) of the label; cname: the stage name's index file (F-<i>) or None; fs:
    "full" (+ the window's 20 + the differences to the two earlier windows) or "small" (+ the window's 20)."""
    B = np.asarray(_mm(f"{label}-{base}"))
    if cname is None:
        return B
    rows = np.asarray(_mm(f"{label}-rows"))
    F = np.asarray(_mm(cname))
    parts = [B, F[rows]]
    if fs == "full":
        parts.append(diffs(F, np.asarray(_mm("G_all")), 2)[rows])
    return np.hstack(parts)


def one_class_fold(y: np.ndarray, groups: np.ndarray, folds: int) -> bool:
    from sklearn.model_selection import GroupKFold
    return any(len(np.unique(y[tr])) < 2 for tr, _ in GroupKFold(n_splits=folds).split(y, y, groups))


def _fit_job(args: tuple) -> tuple:
    """One OOF fit. Returns the predictions (want="pred") or the AUC (want="auc"); None when a training side holds
    one class (checked before the fit). Any other error stops the run."""
    key, label, base, cname, fs, kind, y, seed, folds, want = args
    G = np.asarray(_mm(f"{label}-G"))
    if one_class_fold(y, G, folds):
        return key, None
    X = build_x(label, base, cname, fs)
    p = oof_predict(X, y, G, kind, seed, folds)
    return key, (p if want == "pred" else weighted_auc(p, y, np.ones(len(y))))


def _boot_job(args: tuple) -> tuple:
    """Bootstrap draws of AUC(B) - AUC(base) of one name per attacker."""
    name, preds_b, preds_base, y, groups, mults = args
    prep_a = {k: auc_prep(preds_base[k], y) for k in KINDS}
    out = {}
    for (fs, k), pb in preds_b.items():
        prep_b = auc_prep(pb, y)
        out[f"{fs}/{k}"] = np.array([auc_w(prep_b, m[groups]) - auc_w(prep_a[k], m[groups]) for m in mults])
    return name, out


# ---------------------------------------------------------------------------
# Stage runs
# ---------------------------------------------------------------------------

WORK = Path()
SEED = 0


def _init_stage(work: str, seed: int) -> None:
    global WORK, SEED
    WORK, SEED = Path(work), seed
    os.environ["OMP_NUM_THREADS"] = "1"


def _stage_task(args: tuple) -> tuple:
    """One session: the window features of each (name, lambda)."""
    m, specs = args
    sess = st.load_session(WORK, m)
    n_w = sess.duration_s // 60
    out = {}
    for key, name, lam in specs:
        a, r = st.series(sess, name, SEED, lam=lam)
        out[key] = st.window_features(a, r, n_w).astype(np.float64)
    return m["sid"], out


def run_stage(specs: list[tuple], ms: list[dict], work: Path, seed: int, jobs: int) -> dict:
    """specs: (key, name, lambda). Returns key -> features of all windows of the sessions in ms, in order."""
    tasks = [(m, specs) for m in ms]
    got = {}
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init_stage, initargs=(str(work), seed)) as ex:
        for sid, out in ex.map(_stage_task, tasks, chunksize=1):
            got[sid] = out
    return {k: np.vstack([got[m["sid"]][k] for m in ms]) for k, _, _ in specs}


# ---------------------------------------------------------------------------
# Item 1 (design 3.1-3.3)
# ---------------------------------------------------------------------------

def label_tables(work: Path, sids: list[str], cfg: dict, scratch: Path) -> dict:
    tab = bl.tables(work, sids, cfg)
    save(scratch, "G_all", tab["L60"]["G_all"])
    for t in LABELS:
        save(scratch, f"{t}-A", tab[t]["XA"])
        save(scratch, f"{t}-S", tab[t]["XS"])
        save(scratch, f"{t}-rows", np.nonzero(tab[t]["rows"])[0])
        save(scratch, f"{t}-G", tab[t]["G"])
    return tab


def e13_target(tag: str, tab: dict, names: dict, desc_a: list[str], cfg: dict, seed: int, jobs: int, nboot: int,
               nperm: int, scratch: Path, cands: list[str]) -> dict:
    """One label. names: name -> scratch file of its window features. desc_a: the names whose gain over model A
    (B' = A + the stage) is described (design 1.5)."""
    folds = cfg["e13"]["folds"]
    Y, G, strata = tab["Y"], tab["G"], tab["strata"]
    n_sess = int(G.max()) + 1
    timing: dict = {}

    def fit_all(y: np.ndarray, t: str, with_desc: bool) -> dict:
        want = "pred" if t == "obs" else "auc"
        js = [((t, "S", None, k), tag, "S", None, None, k, y, seed, folds, want) for k in KINDS]
        js += [((t, n, fs, k), tag, "S", f, fs, k, y, seed, folds, want) for n, f in names.items() for fs in FSETS
               for k in KINDS]
        if with_desc:
            js += [((t, "A", None, k), tag, "A", None, None, k, y, seed, folds, want) for k in KINDS]
            js += [((t, "A+" + n, fs, k), tag, "A", names[n], fs, k, y, seed, folds, want) for n in desc_a
                   for fs in FSETS for k in KINDS]
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init, initargs=(str(scratch),)) as ex:
            out = dict(ex.map(_fit_job, js, chunksize=1))
        timing["wall_s_" + ("obs" if t == "obs" else "perm")] = timing.get(
            "wall_s_" + ("obs" if t == "obs" else "perm"), 0.0) + time.time() - t0
        timing["n_fits_" + ("obs" if t == "obs" else "perm")] = timing.get(
            "n_fits_" + ("obs" if t == "obs" else "perm"), 0) + len(js)
        return out

    res = {"label": tag, "n_windows": int(len(Y)), "n_sessions": n_sess, "prevalence": float(Y.mean()),
           "n_positive_windows": int(Y.sum()), "n_sessions_with_positive": int(len(np.unique(G[Y == 1]))),
           "configs": {}, "timing": timing}
    preds = fit_all(Y, "obs", True)
    if any(v is None for v in preds.values()):
        res["auc_A_speed"] = None
        res.update(judge({}, None if not nperm else {}, None, cands, cfg, True))
        return res
    ones = np.ones(len(Y))
    auc_s = {k: weighted_auc(preds[("obs", "S", None, k)], Y, ones) for k in KINDS}
    auc_a = {k: weighted_auc(preds[("obs", "A", None, k)], Y, ones) for k in KINDS}
    res["auc_A_speed"], res["auc_A"] = auc_s, auc_a
    rng = np.random.default_rng(np.random.SeedSequence([seed, 313, LABEL_ID[tag]]))
    mults = [np.bincount(rng.integers(0, n_sess, size=n_sess), minlength=n_sess).astype(float) for _ in range(nboot)]
    boot_jobs = [(n, {(fs, k): preds[("obs", n, fs, k)] for fs in FSETS for k in KINDS},
                  {k: preds[("obs", "S", None, k)] for k in KINDS}, Y, G, mults) for n in names]
    boot_jobs += [("A+" + n, {(fs, k): preds[("obs", "A+" + n, fs, k)] for fs in FSETS for k in KINDS},
                   {k: preds[("obs", "A", None, k)] for k in KINDS}, Y, G, mults) for n in desc_a]
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        boots = dict(ex.map(_boot_job, boot_jobs, chunksize=1))
    attk = {}
    for n in names:
        attk[n] = {}
        for fs in FSETS:
            for k in KINDS:
                key = f"{fs}/{k}"
                gain = weighted_auc(preds[("obs", n, fs, k)], Y, ones) - auc_s[k]
                b = boots[n][key]
                attk[n][key] = {"auc_B": auc_s[k] + gain, "gain": gain,
                                "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]}
    # descriptive (design 1.5, 3.4 item 1): gain over model A of B' and AUC(A_speed) - AUC(A)
    over_a = {}
    for n in desc_a:
        d = {}
        for fs in FSETS:
            for k in KINDS:
                key = f"{fs}/{k}"
                gain = weighted_auc(preds[("obs", "A+" + n, fs, k)], Y, ones) - auc_a[k]
                b = boots["A+" + n][key]
                d[key] = {"gain": gain, "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]}
        over_a[n] = {"attackers": d, "gain_max": max(v["gain"] for v in d.values()),
                     "upper_max": max(v["ci95"][1] for v in d.values())}
    prep_mults = {}
    for k in KINDS:
        pa, ps_ = auc_prep(preds[("obs", "A", None, k)], Y), auc_prep(preds[("obs", "S", None, k)], Y)
        draws = np.array([auc_w(ps_, m[G]) - auc_w(pa, m[G]) for m in mults])
        prep_mults[k] = {"diff": auc_s[k] - auc_a[k],
                         "ci95": [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]}
    res["speed_minus_A"] = prep_mults
    res["gain_over_A"] = over_a
    nulls = None
    if nperm:
        nulls = {n: [] for n in names}
        prng = np.random.default_rng(np.random.SeedSequence([seed, 911, LABEL_ID[tag]]))
        for pi in range(nperm):
            yp = stratified_permutation(Y, strata, prng)
            pp = fit_all(yp, f"perm{pi}", False)
            if any(v is None for v in pp.values()):
                res["null_fit_failed"] = True
                res.update(judge(attk, None, auc_s, cands, cfg, True))
                res["configs"] = attk
                return res
            for n in names:
                nulls[n].append({f"{fs}/{k}": pp[(f"perm{pi}", n, fs, k)] - pp[(f"perm{pi}", "S", None, k)]
                                 for fs in FSETS for k in KINDS})
    j = judge(attk, nulls, auc_s, cands, cfg, False)
    for n in names:
        res["configs"][n] = {"attackers": attk[n], **j["maxima"][n], "verdict": j["verdicts"].get(n)}
        if nulls is not None:
            res["configs"][n]["null_by_perm"] = nulls[n]
            res["configs"][n]["null95"] = j["null95"][n]
    for k in ("ceiling_kinds", "attackers_used", "nan", "fit_failed", "pc1_ok", "null_all_73_ok", "detector"):
        res[k] = j[k]
    return res


def feature_names(tag: str) -> list[str]:
    a = A_NAMES if tag == "L60" else A_NAMES + EX_NAMES
    s = a + WS_NAMES + ([] if tag == "L60" else SS_NAMES)
    return s + list(st.FEAT_NAMES) + [f"d{k}_{f}" for k in (1, 2) for f in st.FEAT_NAMES]


def importance(tag: str, tab: dict, cname: str, seed: int) -> list:
    """design 3.6 (descriptive): hgb on B-full fitted on all rows, permutation importance (AUC, 5 repeats, seed
    fixed), the top five."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance

    X = build_x(tag, "S", cname, "full")
    y = tab["Y"]
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, early_stopping=False, random_state=seed)
    m.fit(X, y)
    pi = permutation_importance(m, X, y, scoring="roc_auc", n_repeats=5, random_state=seed, n_jobs=1)
    names = feature_names(tag)
    order = np.argsort(-pi.importances_mean)[:5]
    return [[names[i], float(pi.importances_mean[i])] for i in order]


# ---------------------------------------------------------------------------
# Descriptions (design 3.4 items 2, 3, 4, 6)
# ---------------------------------------------------------------------------

def event_lag(x: np.ndarray, t_ev: float, cfg: dict) -> tuple[str, float]:
    """design 3.4 item 2: the lag of the change of x after an event at t_ev (s). m0 = mean of [t_ev - 1, t_ev),
    m1 = mean of [t_ev + 9, t_ev + 10); "unchanged" when |m1 - m0| < 0.05; else the first t >= t_ev with
    d (x(t) - m0) > |m1 - m0| / 2 that stays so for the next 1 s (the points t .. t + 1 s), as t - t_ev; ">=10" when no
    such t below t_ev + 10. The points are j / 10 s; a span [u, v) holds the points with u <= j / 10 < v."""
    dsc = cfg["describe"]
    hz = st.HZ
    j_of = lambda u: int(np.ceil(round(u * hz, 9)))
    j0, j1 = j_of(t_ev), j_of(t_ev + dsc["event_s"])
    m0 = float(x[j_of(t_ev - 1): j0].mean())
    m1 = float(x[j_of(t_ev + dsc["event_s"] - 1): j1].mean())
    if abs(m1 - m0) < dsc["unchanged"]:
        return "unchanged", float("nan")
    d = np.sign(m1 - m0)
    ok = d * (x[j0: j1 + hz * dsc["hold_s"]] - m0) > abs(m1 - m0) / 2
    k = hz * dsc["hold_s"]
    for i in range(j1 - j0):
        if ok[i: i + k + 1].all():
            return "lag", (j0 + i) / hz - t_ev
    return "ge10", float("nan")


def stop_events(presses: np.ndarray, duration_s: int, cfg: dict) -> list[tuple[float, float]]:
    """(t_s, t_r): consecutive presses at least event_s apart, with the 1 s before t_s and the 10 s (+ 1 s hold)
    after t_r inside the session."""
    dsc = cfg["describe"]
    g = np.diff(presses)
    out = []
    for i in np.nonzero(g >= dsc["event_s"])[0]:
        ts, tr = float(presses[i]), float(presses[i + 1])
        if ts >= 1.0 and tr + dsc["event_s"] + dsc["hold_s"] + 0.1 <= duration_s:
            out.append((ts, tr))
    return out


def _desc_task(args: tuple) -> tuple:
    """One session and one name: the rows of the per-second identification (item 2), the event lags (item 2), the
    window features (items 3, 4) and the window press quantities."""
    m, name, cfg = args
    sess = st.load_session(WORK, m)
    a, r = st.series(sess, name, SEED)
    hz = st.HZ
    dur = sess.duration_s
    k = np.arange(dur - 1)
    j = hz * (k + 1)
    Xs = np.stack([a[j], r[j], a[j] - a[j - hz], r[j] - r[j - hz]], axis=1).astype(np.float32)
    ys = sess.active[k].astype(np.int8)
    lags = []
    for ts, tr in stop_events(sess.presses, dur, cfg):
        for ev, t in (("stop", ts), ("restart", tr)):
            for pname, x in (("a", a), ("r", r)):
                lags.append((ev, pname) + event_lag(x, t, cfg))
    n_w = dur // 60
    F = st.window_features(a, r, n_w)
    sp = cfg["speed"]
    pq = np.array([bl.speed5(sess.presses, w * 60, (w + 1) * 60, sp)[:2] for w in range(n_w)])
    since = np.zeros(n_w)
    for w in range(n_w):
        e = (w + 1) * 60
        before = sess.presses[sess.presses < e]
        since[w] = min(cfg["describe"]["since_cap_s"], e - before[-1] if len(before) else e)
    return m["sid"], {"Xs": Xs, "ys": ys, "lags": lags, "F": F, "pq": pq, "since": since}


def _twin_task(args: tuple) -> tuple:
    m, names, twin_work = args
    out = {}
    for which, wd in (("orig", WORK), ("twin", Path(twin_work))):
        sess = st.load_session(wd, m)
        n_w = sess.duration_s // 60
        has = np.array([bool(((sess.presses >= w * 60) & (sess.presses < (w + 1) * 60)).any()) for w in range(n_w)])
        out[which] = {"has": has, "F": {n: st.window_features(*st.series(sess, n, SEED), n_w) for n in names}}
    return m["sid"], out


def oof_auc_lr(X: np.ndarray, y: np.ndarray, g: np.ndarray, folds: int, seed: int) -> float:
    if one_class_fold(y, g, folds):
        return float("nan")
    return weighted_auc(oof_predict(X, y, g, "lr", seed, folds), y, np.ones(len(y)))


def oof_r2(X: np.ndarray, y: np.ndarray, g: np.ndarray, folds: int, alpha: float) -> float:
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    pred = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=folds).split(X, y, g):
        pred[te] = make_pipeline(StandardScaler(), Ridge(alpha=alpha)).fit(X[tr], y[tr]).predict(X[te])
    ss = float(((y - y.mean()) ** 2).sum())
    return 1.0 - float(((y - pred) ** 2).sum()) / ss if ss > 0 else float("nan")


def summarize_lags(lags: list) -> dict:
    out = {}
    for ev in ("stop", "restart"):
        for p in ("a", "r"):
            sel = [x for x in lags if x[0] == ev and x[1] == p]
            n = len(sel)
            got = [x[3] for x in sel if x[2] == "lag"]
            out[f"{ev}/{p}"] = {"n_events": n, "lag_median_s": float(np.median(got)) if got else float("nan"),
                                "share_unchanged": sum(x[2] == "unchanged" for x in sel) / n if n else float("nan"),
                                "share_ge10": sum(x[2] == "ge10" for x in sel) / n if n else float("nan")}
    return out


def describe(names: list[str], twin_names: list[str], ms: list[dict], cfg: dict, seed: int, work: Path,
             jobs: int) -> dict:
    from scipy.stats import spearmanr

    dsc = cfg["describe"]
    folds = dsc["folds"]
    res = {}
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init_stage, initargs=(str(work), seed)) as ex:
        for name in names:
            got = dict(ex.map(_desc_task, [(m, name, cfg) for m in ms], chunksize=1))
            parts = [got[m["sid"]] for m in ms]
            gs = np.concatenate([np.full(len(p["ys"]), i) for i, p in enumerate(parts)])
            Xs = np.vstack([p["Xs"] for p in parts]).astype(np.float64)
            ys = np.concatenate([p["ys"] for p in parts]).astype(int)
            lags = [x for p in parts for x in p["lags"]]
            F = np.vstack([p["F"] for p in parts])
            pq = np.vstack([p["pq"] for p in parts])
            since = np.concatenate([p["since"] for p in parts])
            gw = np.concatenate([np.full(len(p["since"]), i) for i, p in enumerate(parts)])
            r = {"item2_per_second_auc": oof_auc_lr(Xs, ys, gs, folds, seed), "item2_lags": summarize_lags(lags)}
            typed = pq[:, 0] > 0
            med_ok = typed & (pq[:, 1] < cfg["speed"]["short_ms"])  # a window with an interval below 2 s
            corr = {}
            for qn, qi, rows in (("presses", 0, typed), ("median_interval", 1, med_ok)):
                for pn, fi in (("a_mean", 0), ("r_mean", 10)):
                    c = spearmanr(pq[rows, qi], F[rows, fi]).statistic if rows.sum() > 2 else float("nan")
                    corr[f"{qn}~{pn}"] = float(c)
            r["item3_spearman"] = corr
            r["item3_presses_r2"] = oof_r2(F[typed], pq[typed, 0], gw[typed], folds, dsc["ridge_alpha"])
            cols = [8, 9, 18, 19]  # a_end, a_since_change, r_end, r_since_change
            r["item4_since_press_r2"] = oof_r2(F[:, cols], since, gw, folds, dsc["ridge_alpha"])
            r["n_windows"] = int(len(F))
            r["n_typed_windows"] = int(typed.sum())
            res[name] = r
            print(f"describe {name}: per-second AUC {r['item2_per_second_auc']:.3f}", flush=True)
    twin_dir = work / "twins"
    if twin_names:
        with ProcessPoolExecutor(max_workers=jobs, initializer=_init_stage, initargs=(str(work), seed)) as ex:
            got = dict(ex.map(_twin_task, [(m, twin_names, str(twin_dir)) for m in ms], chunksize=1))
        for name in twin_names:
            Xo, Xt, g = [], [], []
            for i, m in enumerate(ms):
                o, t = got[m["sid"]]["orig"], got[m["sid"]]["twin"]
                both = o["has"] & t["has"]
                Xo.append(o["F"][name][both])
                Xt.append(t["F"][name][both])
                g.append(np.full(int(both.sum()), i))
            Xo, Xt, g = np.vstack(Xo), np.vstack(Xt), np.concatenate(g)
            X = np.vstack([Xo, Xt])
            y = np.concatenate([np.zeros(len(Xo), dtype=int), np.ones(len(Xt), dtype=int)])
            res[name]["item6_twin_auc"] = oof_auc_lr(X, y, np.concatenate([g, g]), folds, seed)
            res[name]["item6_n_windows"] = int(len(Xo))
    return res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def pilot(cfg: dict, seed: int, work: Path, out: Path, jobs: int) -> int:
    """design 3.9: PC1 and the PC-stall of each candidate on [0] + the grid, L300 only, one candidate at a time."""
    ps = cfg["pc_stall"]
    grid = [float(x) for x in ps["pilot_grid"]]
    cands = st.candidates()
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    t0 = time.time()
    scratch = Path(tempfile.mkdtemp(prefix="pilot-", dir=work))
    nboot = cfg["sets"]["pilot"]["bootstrap"]
    try:
        tab = label_tables(work, sids, cfg, scratch)
        merged, timing, per = {}, [], {}
        batches = [("PC1", [("PC1", "PC1", None)])]
        batches += [(c, [(f"PCs-{c}@{x:.2f}", f"PCs-{c}", x) for x in [0.0] + grid]) for c in cands]
        auc_s = None
        for b, specs in batches:
            tb = time.time()
            F = run_stage(specs, ms, work, seed, jobs)
            names = {}
            for i, (key, _, _) in enumerate(specs):
                save(scratch, f"F-{b}-{i}", F[key])
                names[key] = f"F-{b}-{i}"
            del F
            ts = time.time() - tb
            r = e13_target("L300", tab["L300"], names, [], cfg, seed, jobs, nboot, 0, scratch, [])
            if r.get("auc_A_speed") is None:
                per[b] = {"fit_failed": True}
                merged.update({k: None for k in names})
                continue
            auc_s = r["auc_A_speed"]
            merged.update({k: v for k, v in r["configs"].items()})
            timing.append({"batch": b, "n_configs": len(specs), "stage_s": ts, **r["timing"]})
            per[b] = {"fit_failed": False}
            print(f"pilot {b}: {time.time() - tb:.0f} s (total {time.time() - t0:.0f} s)", flush=True)
        ceil = ceiling_kinds(auc_s, cfg)
        sels = {}
        for c in cands:
            vals = [merged[k]["gain_max"] if merged.get(k) else float("nan") for k in (f"PCs-{c}@{x:.2f}" for x in grid)]
            sels[c] = select_lambda(grid, vals, ps["target"], ps["upper"])
        dump(out / "pilot.json", {
            "_note": ("Pilot 1 (design 3.9): SEED + 1, P sessions of world v4, PC1 and the PC-stall of each candidate on "
                      "[0] + the grid, L300 only, no null. Not a result of the main run. The chosen lambdas go to "
                      "config.json pc_stall.lam and the numbers to design section 8."),
            "seed": seed, "n_sessions": len(sids), "bootstrap": nboot, "auc_A_speed": auc_s, "ceiling_kinds": ceil,
            "configs": {k: ({kk: v[kk] for kk in REC_KEYS} | {"attackers": v["attackers"]} if v else None)
                        for k, v in merged.items()},
            "per_batch": per, "selection": sels, "timing": timing, "wall_s": time.time() - t0})
        for c in cands:
            line = " ".join(f"{x:.2f}:{merged[f'PCs-{c}@{x:.2f}']['gain_max']:+.3f}" for x in [0.0] + grid
                            if merged.get(f"PCs-{c}@{x:.2f}"))
            print(f"{c}: lambda {sels[c]['lam']} ({sels[c]['rule']})\n   {line}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"pilot done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main_run(cfg: dict, seed: int, work: Path, out: Path, jobs: int) -> int:
    ps = cfg["pc_stall"]
    cands = st.candidates()
    missing = [c for c in cands if ps["lam"].get(c) is None]
    if missing:
        raise SystemExit(f"config.json pc_stall.lam is not set for {missing}: run the pilot first")
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    cn = st.config_names(cands)
    specs = ([(c, c, None) for c in cands] + [("PC1", "PC1", None)]
             + [(f"PCs-{c}", f"PCs-{c}", float(ps["lam"][c])) for c in cands]
             + [(f"PC0-{c}", f"PC0-{c}", 0.0) for c in cands] + [("PC-corr", "PC-corr", None)])
    t0 = time.time()
    scratch = Path(tempfile.mkdtemp(prefix="main-", dir=work))
    try:
        tab = label_tables(work, sids, cfg, scratch)
        F = run_stage(specs, ms, work, seed, jobs)
        names = {}
        for i, (key, _, _) in enumerate(specs):
            save(scratch, f"F-{i}", F[key])
            names[key] = f"F-{i}"
        del F
        print(f"stage runs: {len(specs)} x {len(sids)} in {time.time() - t0:.0f} s", flush=True)
        desc_a = cands + cn["pccorr"]
        e13 = {}
        for tag in LABELS:
            e13[tag] = e13_target(tag, tab[tag], names, desc_a, cfg, seed, jobs, cfg["e13"]["bootstrap"],
                                  cfg["e13"]["null_perms"], scratch, cands)
            verd = {c: e13[tag]["configs"].get(c, {}).get("verdict", "undecidable") for c in cands}
            imp = {}
            for c in cands:
                if verd[c].startswith("red"):
                    _init(str(scratch))
                    imp[c] = importance(tag, tab[tag], names[c], seed)
            e13[tag]["importance_red"] = imp
            print(f"E1 {tag} done at {time.time() - t0:.0f} s: "
                  + ", ".join(f"{v}={sum(x == v for x in verd.values())}" for v in sorted(set(verd.values()))),
                  flush=True)
        e13["primary"] = "L300"
        e13["seed"] = seed
        dump(out / "e13.json", e13)
        desc = describe(cands + cn["pccorr"], cands, ms, cfg, seed, work, jobs)
        dump(out / "describe.json", {"_note": "Descriptive (design 3.4): no verdict.", **desc})
        summ = {c: {t: e13[t]["configs"].get(c, {}).get("verdict", "undecidable") for t in LABELS} for c in cands}
        summ["_controls"] = {n: {t: e13[t]["configs"].get(n, {}).get("verdict") for t in LABELS}
                             for n in cn["pc1"] + cn["pcs"] + cn["pc0"] + cn["pccorr"]}
        summ["_detector"] = {t: {k: e13[t].get(k) for k in ("auc_A_speed", "auc_A", "ceiling_kinds", "pc1_ok",
                                                            "null_all_73_ok", "nan", "fit_failed", "detector")}
                             for t in LABELS}
        summ["_wall_s"] = time.time() - t0
        dump(out / "summary.json", summ)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("work")
    ap.add_argument("results")
    ap.add_argument("--jobs", type=int, default=8)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--smoke", action="store_true")
    g.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = 200, 2
    seed = int(Path(a.seed_file).read_text().strip())
    work, out = Path(a.work), Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    if a.pilot:
        return pilot(cfg, seed, work, out, a.jobs)
    return main_run(cfg, seed, work, out, a.jobs)


if __name__ == "__main__":
    raise SystemExit(main())
