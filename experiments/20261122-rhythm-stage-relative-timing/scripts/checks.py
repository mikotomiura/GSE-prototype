"""Checks of the rhythm stage desk check, relative timing (plan D): item 1 (verdicts on two bases), the descriptions
(d0), (d1), (d2), items 2-4 and 6, the variants without the a side or the r side, and the pilot 1 (the lambda of each
PC-stall, per base).

Design: .steering/20261122-rhythm-stage-relative-timing/design.md 1.4-1.6, 3.0-3.7. Copied from
experiments/20261015-rhythm-stage-speed-shape-world/scripts/checks.py (the file of 1cf9fcb9) with these changes:
- L300 only (decisions 8): no L60, no L1800 and its controls (PC1-1800, PCl-), no r-side controls (PCrl-, PCrv-), no
  cause split and no comparison table (decisions 9).
- The verdict takes its base model as an argument (e13_target(..., base=)): "A" (model A, the primary verdict) and
  "S" (A_speed, the secondary verdict, as the earlier rounds; selftest.py checks that it equals the copied file's
  verdict byte for byte). The gain is AUC(base + the stage) - AUC(base); the ceiling rule (a classifier whose
  AUC(base) is >= 0.90 is left out) reads the base's own AUC (design 1.4).
- The PC-stall's lambda is chosen per base (design 1.5): the pilot fits each batch on both bases; pc_stall.lam.<step>
  is {"A": {candidate: lam}, "S": {...}}. The pilot's A part stopping stops the step (design 3.0); the S part
  stopping (e.g. AUC(A_speed) at the ceiling, expected in g050) leaves the secondary verdicts undecidable
  (pilot_stop) and the step goes on.
- The steps are g050 (the graded world at t = 0.5) and f200 (the factor world at c = 2) (design 1.3).
- Descriptions (design 0, 1.4, 1.6): (d0) the AUC of the drawing features alone; (d1) AUC(A_speed) - AUC(A) and each
  candidate's gain over A divided by it; (d2) R^2 of the window's press count and (f200) the session's speed factor u
  from the drawing features, also from the six smoothness features alone; the variants without the a side's ten or
  the r side's ten features for the red candidates (exploratory, no verdict word).

The statistics are copied from experiments/20261010-portrait-eh1-round5/scripts/checks.py (auc_prep, auc_w,
weighted_auc, oof_predict, stratified_permutation, isotonic_blocks, select_lambda, the bootstrap and the null). A fold
whose training side holds one class is reported as a failed fit (checked before the fit); any other error stops the
run.

Usage: checks.py <config.json> <seed file> <work dir> <results dir> --step <step> [--jobs N]
                 [--smoke | --pilot] [--pilot-json <results/<step>/pilot/pilot.json>]
  (no mode)  the main run: 6 candidates, PC1, PC-stall (per base) and PC0 of each candidate, PC-corr; both bases;
             bootstrap e13.bootstrap, e13.null_perms permutations; the descriptions (needs <work>/twins replayed);
             --pilot-json is required
  --smoke    the same with bootstrap 200 and 2 permutations (pipeline check only)
  --pilot    design 1.5: PC1 and the PC-stall of each candidate on [0] + the grid, on both bases, bootstrap
             sets.pilot.bootstrap, no null; one candidate at a time; writes pilot.json
       checks.py --apply-pilot <config.json> <results/<step>/pilot/pilot.json> <step>
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
import ceiling as ce
import gen_sessions as gs
import stage as st

KINDS = ("hgb", "lr")
FSETS = ("full", "small")
ATTACKERS = tuple(f"{fs}/{k}" for fs in FSETS for k in KINDS)
TAG = "L300"
LABEL_ID = {"L300": 0, "L60": 1, "L1800": 2}  # seeds the bootstrap and the permutations (as the copied file)
BASES = ("A", "S")  # model A (primary) and A_speed (secondary)
BASE_NAME = {"A": "A", "S": "A_speed"}
REC_KEYS = ("upper_max", "lower_max", "gain_max", "n_nan_bounds")
A_NAMES = [f"act_w{k}" for k in range(5)] + ["gap_max", "gaps_ge2", "gaps_ge10", "since_press", "act_last15m", "t_end"]
EX_NAMES = ["span_gap_max", "span_gaps_ge2", "span_gaps_ge10", "span_act"]
WS_NAMES = ["w_n", "w_med", "w_iqr", "w_run", "w_last10"] + [f"lag{k}_{q}" for k in range(1, 5) for q in ("n", "med")]
SS_NAMES = ["span_n", "span_med", "span_iqr", "span_run", "span_last10"]
DROP_COLS = {"a": list(range(10)), "r": list(range(10, 20))}  # design 1.6: the a side's and the r side's ten
SMOOTH_NAMES = ("a_sd", "a_absdiff", "a_ac1", "r_sd", "r_absdiff", "r_ac1")  # design 0 (d2), section 9 item 9
SMOOTH_COLS = [st.FEAT_NAMES.index(n) for n in SMOOTH_NAMES]


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


def select_lambda(lams: list[float], gains: list[float], lowers: list[float], aim: float, lower: float,
                  upper: float) -> dict:
    """Round 2 design 3.9: choose lambda (> 0) of one candidate from the pilot's maxima over the attackers in use.
    gains: the point estimate g, lowers: the lower bound l of the 95% interval, per lambda. In the band: l > lower and
    g <= upper (a NaN bound is out). The isotonic fit of g (NaN g left out) gives g_hat; among the lambdas in the band
    (else among all) the smallest |g_hat - aim| (rounded to 6 decimals) wins; the ties are the lambdas of that pool with
    the same distance, in ascending order, and of them the middle index (the smaller of two middles) wins. No finite
    g -> lam None (the pilot stops)."""
    trip = sorted((float(x), float(g), float(lo)) for x, g, lo in zip(lams, gains, lowers))
    excluded = [x for x, g, _ in trip if not np.isfinite(g)]
    kept = [(x, g, lo) for x, g, lo in trip if np.isfinite(g)]
    if not kept:
        return {"lam": None, "rule": "no finite point estimate -> no choice (back to the researcher)",
                "excluded": excluded, "fit": [], "band": []}
    xs = [t[0] for t in kept]
    fit = [0.0] * len(xs)
    for s, e, v in isotonic_blocks([t[1] for t in kept]):
        for i in range(s, e + 1):
            fit[i] = v
    band = [i for i, (_, g, lo) in enumerate(kept) if _gt(lo, lower) and g <= upper]
    pool, rule = (band, "in the band") if band else (list(range(len(xs))), "no lambda in the band -> over the grid")
    dist = {i: round(abs(fit[i] - aim), 6) for i in pool}
    best = min(dist.values())
    ties = [i for i in pool if dist[i] == best]
    pick = ties[(len(ties) - 1) // 2]  # the middle (the smaller of two middles)
    return {"lam": xs[pick], "rule": f"{rule}; the fitted value closest to the aim; the middle of the ties",
            "excluded": excluded, "fit": [[x, f] for x, f in zip(xs, fit)], "band": [xs[i] for i in band],
            "ties": [xs[i] for i in ties]}


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
# Names and verdicts (design 3.1): pure functions, unit-tested in selftest.py
# ---------------------------------------------------------------------------

def kind_of(name: str, tag: str = TAG) -> str:
    """The role of a name on L300. A PC-stall on the pilot's grid (with @) is descriptive."""
    if tag != TAG:
        raise ValueError(f"L300 only (decisions 8), not {tag}")
    if name == "PC1":
        return "pc1"
    if name == "PC-corr":
        return "descriptive"
    if name.startswith("PCs-"):
        return "descriptive" if "@" in name else "pcs"
    if name.startswith("PC0-"):
        return "pc0"
    if name.startswith(("S-", "D-")):
        return "candidate"
    raise ValueError(name)


def control_names(tag: str = TAG) -> tuple[str, str]:
    """(the strong control, the PC-stall prefix)."""
    return "PC1", "PCs-"


def _gt(a: float, b: float) -> bool:
    return bool(np.isfinite(a) and a > b)


def _lt(a: float, b: float) -> bool:
    return bool(np.isfinite(a) and a < b)


def ceiling_kinds(auc_b: dict | None, cfg: dict) -> list[str]:
    """The classifiers whose AUC(base) is >= ceiling.main_auc (0.90 exactly is at the ceiling)."""
    if auc_b is None:
        return []
    return [k for k in KINDS if np.isfinite(auc_b[k]) and auc_b[k] >= cfg["ceiling"]["main_auc"]]


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


def judge(attk: dict, nulls: dict | None, auc_s: dict | None, cands: list[str], cfg: dict, fit_failed: bool, *,
          tag: str = TAG, forced: str | None = None) -> dict:
    """One base on L300 (design 3.1; the copied file's rules). auc_s: kind -> AUC(base) (None when the fits failed).
    forced: a reason that makes every candidate undecidable (pilot_stop on the base whose pilot part stopped).
    attk: name -> attacker -> {"gain", "ci95"} (empty when the fits failed).
    nulls: name -> list over the permutations of attacker -> gain (None when no permutation was run)."""
    e = cfg["e13"]
    margin, pc_lower = e["margin"], e["pc_lower"]
    ps = cfg["pc_stall"]
    ceil = ceiling_kinds(auc_s, cfg)
    use = [a for a in ATTACKERS if a.split("/")[1] not in ceil]
    both_ceiling = not use
    rec = {n: maxima(v, use) for n, v in attk.items()}
    nan = any(r["n_nan_bounds"] > 0 for n, r in rec.items() if kind_of(n, tag) != "descriptive")
    null95 = None if nulls is None else {n: null95_of(v, use) for n, v in nulls.items()}
    broken = bool(fit_failed or nan or both_ceiling)
    pc1_name, prefix = control_names(tag)
    pc1 = rec.get(pc1_name)
    pc1_ok = pc1 is not None and not broken and _gt(pc1["lower_max"], pc_lower)
    detector, verdicts = {}, {}
    for c in cands:
        r, pcs, pc0 = rec.get(c), rec.get(f"{prefix}{c}"), rec.get(f"PC0-{c}")
        stall_ok = (pcs is not None and not broken and _gt(pcs["lower_max"], ps["lower"])
                    and bool(np.isfinite(pcs["gain_max"]) and pcs["gain_max"] <= ps["upper"]))
        base_ok = pc0 is not None and not broken and _lt(pc0["upper_max"], margin)
        if null95 is None:
            null_ok = None
        else:
            four = [c, f"{prefix}{c}", f"PC0-{c}", pc1_name]
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
        if forced:  # the forced reason first, the others kept
            reasons, stop_path = [forced] + reasons, False
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
        k = kind_of(n, tag)
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
    judged = [n for n in rec if kind_of(n, tag) != "descriptive"]
    null_all = None if (null95 is None or forced) else bool(judged and all(n in null95 and _lt(null95[n], margin)
                                                                          for n in judged))
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
    """B-full: the window's features minus those of the k-th earlier window (k = 1 .. lags); 0 when the earlier window
    is in another session or before the start."""
    parts = []
    for k in range(1, lags + 1):
        D = np.zeros_like(F)
        same = np.zeros(len(F), dtype=bool)
        same[k:] = sess_idx[k:] == sess_idx[:-k]
        D[k:] = F[k:] - F[:-k]
        D[~same] = 0.0
        parts.append(D)
    return np.hstack(parts)


def keep_cols(drop: str | None) -> list[int]:
    """design 1.6: the stage feature columns kept when the a side or the r side is dropped."""
    if drop is None:
        return list(range(len(st.FEAT_NAMES)))
    gone = set(DROP_COLS[drop])
    return [i for i in range(len(st.FEAT_NAMES)) if i not in gone]


def build_x(label: str, base: str | None, cname: str | None, fs: str | None, drop: str | None = None) -> np.ndarray:
    """base: "A" (model A), "S" (A_speed) or None (the stage alone, (d0)); cname: the stage name's index file or None;
    fs: "full" (+ the window's 20 + the differences to the two earlier windows) or "small" (+ the window's 20); drop:
    None, "a" or "r" (design 1.6: the side's ten features and their differences left out)."""
    if cname is None:
        return np.asarray(_mm(f"{label}-{base}"))
    rows = np.asarray(_mm(f"{label}-rows"))
    F = np.asarray(_mm(cname))
    if drop is not None:
        F = F[:, keep_cols(drop)]
    parts = [] if base is None else [np.asarray(_mm(f"{label}-{base}"))]
    parts.append(F[rows])
    if fs == "full":
        parts.append(diffs(F, np.asarray(_mm("G_all")), 2)[rows])
    return np.hstack(parts)


def one_class_fold(y: np.ndarray, groups: np.ndarray, folds: int) -> bool:
    from sklearn.model_selection import GroupKFold
    return any(len(np.unique(y[tr])) < 2 for tr, _ in GroupKFold(n_splits=folds).split(y, y, groups))


def _fit_job(args: tuple) -> tuple:
    """One OOF fit. Returns the predictions (want="pred") or the AUC (want="auc"); None when a training side holds
    one class (checked before the fit). Any other error stops the run."""
    key, label, base, cname, fs, kind, y, seed, folds, want, drop = args
    G = np.asarray(_mm(f"{label}-G"))
    if one_class_fold(y, G, folds):
        return key, None
    X = build_x(label, base, cname, fs, drop)
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


def _boot_auc_job(args: tuple) -> tuple:
    """Bootstrap draws of AUC(score) of one name per attacker ((d0) and AUC(A))."""
    name, preds, y, groups, mults = args
    out = {}
    for key, p in preds.items():
        prep = auc_prep(p, y)
        out[key] = np.array([auc_w(prep, m[groups]) for m in mults])
    return name, out


def fit_many(jobs_in: list[tuple], scratch: Path, jobs: int) -> dict:
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init, initargs=(str(scratch),)) as ex:
        return dict(ex.map(_fit_job, jobs_in, chunksize=1))


def ci95(draws: np.ndarray) -> list[float]:
    return [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]


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
    for key, name, lam, *mut in specs:
        a, r = st.series(sess, name, SEED, lam=lam, mutation=mut[0] if mut else None)
        out[key] = st.window_features(a, r, n_w).astype(np.float64)
    return m["sid"], out


def run_stage(specs: list[tuple], ms: list[dict], work: Path, seed: int, jobs: int) -> dict:
    """specs: (key, name, lambda[, mutation]). Returns key -> features of all windows of the sessions in ms, in order."""
    tasks = [(m, specs) for m in ms]
    got = {}
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init_stage, initargs=(str(work), seed)) as ex:
        for sid, out in ex.map(_stage_task, tasks, chunksize=1):
            got[sid] = out
    return {sp[0]: np.vstack([got[m["sid"]][sp[0]] for m in ms]) for sp in specs}


# ---------------------------------------------------------------------------
# Item 1 (design 1.4, 3.1)
# ---------------------------------------------------------------------------

def label_tables(work: Path, sids: list[str], cfg: dict, scratch: Path) -> dict:
    tab = bl.tables(work, sids, cfg)
    save(scratch, "G_all", tab["L60"]["G_all"])
    save(scratch, f"{TAG}-A", tab[TAG]["XA"])
    save(scratch, f"{TAG}-S", tab[TAG]["XS"])
    save(scratch, f"{TAG}-rows", np.nonzero(tab[TAG]["rows"])[0])
    save(scratch, f"{TAG}-G", tab[TAG]["G"])
    return tab


def names_base(base: str) -> str:
    """Seam: the base model the stage names are fitted on top of (the base itself; selftest's mutant swaps it)."""
    return base


def boot_mults(seed: int, n_sess: int, nboot: int, tag: str = TAG) -> list[np.ndarray]:
    """The session-level bootstrap weights of a label (the copied file's stream; the same draws for both bases)."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, 313, LABEL_ID[tag]]))
    return [np.bincount(rng.integers(0, n_sess, size=n_sess), minlength=n_sess).astype(float) for _ in range(nboot)]


def e13_target(tag: str, tab: dict, names: dict, cfg: dict, seed: int, jobs: int, nboot: int, nperm: int,
               scratch: Path, cands: list[str], *, base: str, forced: str | None = None) -> dict:
    """One base on one label (design 1.4). names: name -> scratch file of its window features. forced: see judge.
    The returned dict holds the observed predictions and the bootstrap weights under "_preds" and "_mults" (not
    written to the results)."""
    if base not in BASES:
        raise ValueError(base)
    nb = names_base(base)
    folds = cfg["e13"]["folds"]
    Y, G, strata = tab["Y"], tab["G"], tab["strata"]
    n_sess = int(G.max()) + 1
    timing: dict = {}

    def fit_all(y: np.ndarray, t: str) -> dict:
        want = "pred" if t == "obs" else "auc"
        js = [((t, "B", None, k), tag, base, None, None, k, y, seed, folds, want, None) for k in KINDS]
        js += [((t, n, fs, k), tag, nb, f, fs, k, y, seed, folds, want, None) for n, f in names.items()
               for fs in FSETS for k in KINDS]
        t0 = time.time()
        out = fit_many(js, scratch, jobs)
        w = "obs" if t == "obs" else "perm"
        timing["wall_s_" + w] = timing.get("wall_s_" + w, 0.0) + time.time() - t0
        timing["n_fits_" + w] = timing.get("n_fits_" + w, 0) + len(js)
        return out

    res = {"label": tag, "base": BASE_NAME[base], "n_windows": int(len(Y)), "n_sessions": n_sess,
           "prevalence": float(Y.mean()), "n_positive_windows": int(Y.sum()),
           "n_sessions_with_positive": int(len(np.unique(G[Y == 1]))), "configs": {}, "timing": timing}
    preds = fit_all(Y, "obs")
    if any(v is None for v in preds.values()):
        res["auc_base"] = None
        res.update(judge({}, None if not nperm else {}, None, cands, cfg, True, tag=tag, forced=forced))
        return res
    ones = np.ones(len(Y))
    auc_b = {k: weighted_auc(preds[("obs", "B", None, k)], Y, ones) for k in KINDS}
    res["auc_base"] = auc_b
    mults = boot_mults(seed, n_sess, nboot, tag)
    boot_jobs = [(n, {(fs, k): preds[("obs", n, fs, k)] for fs in FSETS for k in KINDS},
                  {k: preds[("obs", "B", None, k)] for k in KINDS}, Y, G, mults) for n in names]
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        boots = dict(ex.map(_boot_job, boot_jobs, chunksize=1))
    attk = {}
    for n in names:
        attk[n] = {}
        for fs in FSETS:
            for k in KINDS:
                key = f"{fs}/{k}"
                gain = weighted_auc(preds[("obs", n, fs, k)], Y, ones) - auc_b[k]
                attk[n][key] = {"auc_B": auc_b[k] + gain, "gain": gain, "ci95": ci95(boots[n][key])}
    res["_preds"], res["_mults"] = preds, mults
    nulls = None
    if nperm:
        nulls = {n: [] for n in names}
        prng = np.random.default_rng(np.random.SeedSequence([seed, 911, LABEL_ID[tag]]))
        for pi in range(nperm):
            yp = stratified_permutation(Y, strata, prng)
            pp = fit_all(yp, f"perm{pi}")
            if any(v is None for v in pp.values()):
                res["null_fit_failed"] = True
                res.update(judge(attk, None, auc_b, cands, cfg, True, tag=tag, forced=forced))
                res["configs"] = attk
                return res
            for n in names:
                nulls[n].append({f"{fs}/{k}": pp[(f"perm{pi}", n, fs, k)] - pp[(f"perm{pi}", "B", None, k)]
                                 for fs in FSETS for k in KINDS})
    j = judge(attk, nulls, auc_b, cands, cfg, False, tag=tag, forced=forced)
    for n in names:
        res["configs"][n] = {"attackers": attk[n], **j["maxima"][n], "verdict": j["verdicts"].get(n)}
        if nulls is not None and n in nulls:
            res["configs"][n]["null_by_perm"] = nulls[n]
            res["configs"][n]["null95"] = j["null95"][n]
    for k in ("ceiling_kinds", "attackers_used", "nan", "fit_failed", "pc1_ok", "null_all_73_ok", "detector"):
        res[k] = j[k]
    return res


def public(res: dict) -> dict:
    """An e13_target result without its private keys (the predictions and the bootstrap weights)."""
    return {k: v for k, v in res.items() if not k.startswith("_")}


def speed_minus_a(ra: dict, rs: dict, tab: dict) -> dict | None:
    """(d1): AUC(A_speed) - AUC(A) per classifier with its bootstrap interval (the copied file's speed_minus_A, on
    the bootstrap weights both bases share)."""
    if "_preds" not in ra or "_preds" not in rs:
        return None
    Y, G = tab["Y"], tab["G"]
    out = {}
    for k in KINDS:
        pa, ps_ = auc_prep(ra["_preds"][("obs", "B", None, k)], Y), auc_prep(rs["_preds"][("obs", "B", None, k)], Y)
        draws = np.array([auc_w(ps_, m[G]) - auc_w(pa, m[G]) for m in ra["_mults"]])
        out[k] = {"diff": rs["auc_base"][k] - ra["auc_base"][k], "ci95": ci95(draws)}
    return out


def ratio_to_speed(ra: dict, sma: dict | None, cands: list[str], cfg: dict) -> dict:
    """(d1): each candidate's gain over A divided by AUC(A_speed) - AUC(A) of the same classifier, per attacker; no
    ratio when that difference is below e13.margin (0.03) or not measured."""
    out = {}
    for c in cands:
        att = ra.get("configs", {}).get(c, {}).get("attackers")
        row = {}
        for a in ATTACKERS:
            k = a.split("/")[1]
            den = None if sma is None else sma[k]["diff"]
            ok = att is not None and den is not None and np.isfinite(den) and den >= cfg["e13"]["margin"]
            row[a] = att[a]["gain"] / den if ok else None
        out[c] = row
    return out


def stage_alone(tag: str, tab: dict, names: dict, cands: list[str], ra: dict, cfg: dict, seed: int, jobs: int,
                scratch: Path) -> dict | None:
    """(d0): the AUC of the drawing features alone (full and small x hgb and lr) per candidate with its bootstrap
    interval, and AUC(A) with its interval beside it."""
    if "_preds" not in ra:
        return None
    Y, G = tab["Y"], tab["G"]
    folds = cfg["e13"]["folds"]
    js = [((c, fs, k), tag, None, names[c], fs, k, Y, seed, folds, "pred", None) for c in cands for fs in FSETS
          for k in KINDS]
    preds = fit_many(js, scratch, jobs)
    if any(v is None for v in preds.values()):
        return {"fit_failed": True}
    bj = [(c, {f"{fs}/{k}": preds[(c, fs, k)] for fs in FSETS for k in KINDS}, Y, G, ra["_mults"]) for c in cands]
    bj.append(("A", {k: ra["_preds"][("obs", "B", None, k)] for k in KINDS}, Y, G, ra["_mults"]))
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        boots = dict(ex.map(_boot_auc_job, bj, chunksize=1))
    ones = np.ones(len(Y))
    out = {"fit_failed": False, "A": {k: {"auc": ra["auc_base"][k], "ci95": ci95(boots["A"][k])} for k in KINDS}}
    for c in cands:
        out[c] = {f"{fs}/{k}": {"auc": weighted_auc(preds[(c, fs, k)], Y, ones), "ci95": ci95(boots[c][f"{fs}/{k}"])}
                  for fs in FSETS for k in KINDS}
    return out


def dropped(tag: str, tab: dict, base: str, res: dict, names: dict, red: list[str], cfg: dict, seed: int, jobs: int,
            scratch: Path) -> dict:
    """design 1.6, 3.3 (c) (exploratory, no verdict word): for each red candidate of the base, the gain over the base
    without the a side's ten features or without the r side's ten (and their differences), per attacker, with the
    bootstrap interval."""
    if not red or "_preds" not in res:
        return {}
    Y, G = tab["Y"], tab["G"]
    folds = cfg["e13"]["folds"]
    nb = names_base(base)
    js = [((c, d, fs, k), tag, nb, names[c], fs, k, Y, seed, folds, "pred", d) for c in red for d in DROP_COLS
          for fs in FSETS for k in KINDS]
    preds = fit_many(js, scratch, jobs)
    if any(v is None for v in preds.values()):
        return {"fit_failed": True}
    base_p = {k: res["_preds"][("obs", "B", None, k)] for k in KINDS}
    bj = [(f"{c}|{d}", {(fs, k): preds[(c, d, fs, k)] for fs in FSETS for k in KINDS}, base_p, Y, G, res["_mults"])
          for c in red for d in DROP_COLS]
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        boots = dict(ex.map(_boot_job, bj, chunksize=1))
    ones = np.ones(len(Y))
    out = {}
    for c in red:
        out[c] = {}
        for d in DROP_COLS:
            out[c][f"without_{d}"] = {
                f"{fs}/{k}": {"gain": weighted_auc(preds[(c, d, fs, k)], Y, ones) - res["auc_base"][k],
                              "ci95": ci95(boots[f"{c}|{d}"][f"{fs}/{k}"])} for fs in FSETS for k in KINDS}
    return out


def feature_names(base: str) -> list[str]:
    a = A_NAMES + EX_NAMES
    s = a if base == "A" else a + WS_NAMES + SS_NAMES
    return s + list(st.FEAT_NAMES) + [f"d{k}_{f}" for k in (1, 2) for f in st.FEAT_NAMES]


def importance(tab: dict, cname: str, seed: int, base: str) -> list:
    """Descriptive: hgb on base + the stage (full) fitted on all rows, permutation importance (AUC, 5 repeats, seed
    fixed), the top five."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.inspection import permutation_importance

    X = build_x(TAG, base, cname, "full")
    y = tab["Y"]
    m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, early_stopping=False, random_state=seed)
    m.fit(X, y)
    pi = permutation_importance(m, X, y, scoring="roc_auc", n_repeats=5, random_state=seed, n_jobs=1)
    names = feature_names(base)
    order = np.argsort(-pi.importances_mean)[:5]
    return [[names[i], float(pi.importances_mean[i])] for i in order]


# ---------------------------------------------------------------------------
# Descriptions (items 2, 3, 4, 6 as the copied file; (d2))
# ---------------------------------------------------------------------------

def event_lag(x: np.ndarray, t_ev: float, cfg: dict) -> tuple[str, float]:
    """Item 2: the lag of the change of x after an event at t_ev (s). m0 = mean of [t_ev - 1, t_ev),
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


def lags_readable(name: str) -> bool:
    """The wobble of the jitter candidates alone moves the lag measure (none of this task's candidates is jitter)."""
    return not name.startswith("S-jitter-")


def stop_events(presses: np.ndarray, duration_s: int, cfg: dict) -> list[tuple[float, float]]:
    """(t_s, t_r): consecutive presses at least event_s apart, with the 1 s before t_s and the 10 s (+ 1 s hold)
    after t_r inside the session."""
    dsc = cfg["describe"]
    g = np.rint(np.diff(presses) * 1000.0)  # whole ms, as speed5 (10.0 s exactly is an event)
    out = []
    for i in np.nonzero(g >= dsc["event_s"] * 1000)[0]:
        ts, tr = float(presses[i]), float(presses[i + 1])
        if ts >= 1.0 and tr + dsc["event_s"] + dsc["hold_s"] + 0.1 <= duration_s:
            out.append((ts, tr))
    return out


def session_u(seed: int, sid: str) -> float:
    """(d2): the speed factor u of P session sid (gen_sessions.Speed draws it first from derive_rng(seed, "speed",
    "P", i); selftest checks it against Speed)."""
    if not (sid.startswith("P") and sid[1:].isdigit()):
        raise ValueError(sid)
    return float(gs.derive_rng(seed, "speed", "P", int(sid[1:])).standard_normal())


def _desc_task(args: tuple) -> tuple:
    """One session and one name: the rows of the per-second identification (item 2), the event lags (item 2), the
    window features (items 3, 4, (d2)) and the window press quantities."""
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
    if len(np.unique(g)) < folds or one_class_fold(y, g, folds):  # too few sessions left after a filter: NaN
        return float("nan")
    return weighted_auc(oof_predict(X, y, g, "lr", seed, folds), y, np.ones(len(y)))


def oof_r2(X: np.ndarray, y: np.ndarray, g: np.ndarray, folds: int, alpha: float) -> float:
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if len(np.unique(g)) < folds:  # too few sessions left after a filter
        return float("nan")
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
             jobs: int, u_by_sid: dict | None) -> dict:
    """Items 2-4 and 6 (as the copied file) and (d2): the R^2 of the window's press count from the drawing features
    and from the six smoothness features alone (typed windows), and with u_by_sid (f200) the R^2 of the session's
    speed factor u from the same (every window)."""
    from scipy.stats import spearmanr

    dsc = cfg["describe"]
    folds = dsc["folds"]
    res = {}
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init_stage, initargs=(str(work), seed)) as ex:
        for name in names:
            got = dict(ex.map(_desc_task, [(m, name, cfg) for m in ms], chunksize=1))
            parts = [got[m["sid"]] for m in ms]
            gs_ = np.concatenate([np.full(len(p["ys"]), i) for i, p in enumerate(parts)])
            Xs = np.vstack([p["Xs"] for p in parts]).astype(np.float64)
            ys = np.concatenate([p["ys"] for p in parts]).astype(int)
            lags = [x for p in parts for x in p["lags"]]
            F = np.vstack([p["F"] for p in parts])
            pq = np.vstack([p["pq"] for p in parts])
            since = np.concatenate([p["since"] for p in parts])
            gw = np.concatenate([np.full(len(p["since"]), i) for i, p in enumerate(parts)])
            r = {"item2_per_second_auc": oof_auc_lr(Xs, ys, gs_, folds, seed), "item2_lags": summarize_lags(lags),
                 "item2_lags_readable": lags_readable(name)}
            typed = pq[:, 0] > 0
            med_ok = typed & (pq[:, 1] < cfg["speed"]["short_ms"])  # a window with an interval below 2 s
            corr = {}
            for qn, qi, rows in (("presses", 0, typed), ("median_interval", 1, med_ok)):
                for pn, fi in (("a_mean", 0), ("r_mean", 10)):
                    c = spearmanr(pq[rows, qi], F[rows, fi]).statistic if rows.sum() > 2 else float("nan")
                    corr[f"{qn}~{pn}"] = float(c)
            r["item3_spearman"] = corr
            r["item3_presses_r2"] = oof_r2(F[typed], pq[typed, 0], gw[typed], folds, dsc["ridge_alpha"])
            r["d2_presses_r2_smooth"] = oof_r2(F[typed][:, SMOOTH_COLS], pq[typed, 0], gw[typed], folds,
                                               dsc["ridge_alpha"])
            if u_by_sid is not None:
                u = np.concatenate([np.full(len(p["since"]), u_by_sid[m["sid"]]) for m, p in zip(ms, parts)])
                r["d2_u_r2"] = oof_r2(F, u, gw, folds, dsc["ridge_alpha"])
                r["d2_u_r2_smooth"] = oof_r2(F[:, SMOOTH_COLS], u, gw, folds, dsc["ridge_alpha"])
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
# Steps, pilot 0 and pilot 1 (design 1.3, 1.5, 3.0)
# ---------------------------------------------------------------------------

def pilot_key(cand: str, lam: float, prefix: str = "PCs-") -> str:
    """The pilot's name of the PC-stall of a candidate at lambda (three decimals: 0.025 and 0.075 stay apart)."""
    return f"{prefix}{cand}@{float(lam):.3f}"


def pilot_stop(merged: dict, per: dict, cfg: dict, ceil: list[str], pc1_name: str = "PC1") -> str | None:
    """The pilot of a base chooses no lambda when a fit failed, both classifiers are at the base's ceiling, or the
    strong control does not work (its lower bound must be finite and > e13.pc_lower)."""
    if any(v.get("fit_failed") for v in per.values()) or not per:
        return "fit_failed"
    if all(k in ceil for k in KINDS):
        return "ceiling"
    pc1 = merged.get(pc1_name)
    if not pc1 or not _gt(pc1["lower_max"], cfg["e13"]["pc_lower"]):
        return "weak_detector"
    return None


def choose_all(merged: dict, cfg: dict, prefix: str = "PCs-") -> dict:
    """The lambda of every candidate from the pilot's maxima of one base (lambda = 0 is never a choice)."""
    ps = cfg["pc_stall"]
    grid = [float(x) for x in ps["pilot_grid"]]
    out = {}
    for c in st.candidates():
        recs = [merged.get(pilot_key(c, x, prefix)) for x in grid]
        g = [r["gain_max"] if r else float("nan") for r in recs]
        lo = [r["lower_max"] if r else float("nan") for r in recs]
        out[c] = select_lambda(grid, g, lo, ps["aim"], ps["lower"], ps["upper"])
    return out


RULE_KEYS = ("pilot_grid", "aim", "lower", "upper")


def pilot_decide(merged: dict, per: dict, cfg: dict, ceil: list[str]) -> tuple[str | None, dict]:
    """(stop, selection) of one base. A stop leaves no lambda to write: the pilot's own stop, or a candidate with no
    finite point estimate (its selection stays as a record)."""
    stop = pilot_stop(merged, per, cfg, ceil)
    if stop:
        return stop, {}
    sels = choose_all(merged, cfg)
    if any(s["lam"] is None for s in sels.values()):
        return "no_finite_pcs", sels
    return None, sels


def _num(v):
    """A maximum read back from pilot.json (clean() writes NaN as the string "nan")."""
    return float("nan") if v in ("nan", None) else float(v)


def step_value(cfg: dict, step: str) -> float:
    steps = cfg["ceiling"]["steps"]
    if step not in steps:
        raise SystemExit(f"unknown step {step!r}: not in config.json ceiling.steps {sorted(steps)}")
    return float(steps[step])


def step_world(cfg: dict, step: str) -> str:
    """design 1.3: the world of a step (config.json ceiling.worlds, which names every step)."""
    worlds = cfg["ceiling"]["worlds"]
    if step not in worlds or sorted(worlds) != sorted(cfg["ceiling"]["steps"]):
        raise SystemExit(f"step {step!r}: config.json ceiling.worlds {worlds} does not name it (or not every step)")
    if worlds[step] not in ("graded", "factor"):
        raise SystemExit(f"step {step!r}: world {worlds[step]!r} is not graded or factor (design 1.3)")
    return str(worlds[step])


def step_doc(cfg: dict, step: str) -> dict:
    """The world.json of the step: {"world": "graded", "t": t} or {"world": "factor", "c": c}."""
    return ce.world_doc(step_world(cfg, step), step_value(cfg, step))


def world_problems(work: Path, cfg: dict, step: str) -> list[str]:
    """The work directory was made with the step's world and value."""
    f = work / "world.json"
    if not f.exists():
        return [f"{f} is missing"]
    w = json.loads(f.read_text(encoding="utf-8"))
    want = step_doc(cfg, step)
    return [] if w == want else [f"{f} is {w}, not {want} (step {step})"]


def part_result(merged: dict, per: dict, auc_b: dict | None, cfg: dict) -> tuple[str | None, dict, list]:
    """(stop, selection, ceiling) of one base's part of the pilot from its own maxima, fits and AUC(base). pilot_part
    writes it; pilot_check recomputes it."""
    ceil = ceiling_kinds(auc_b, cfg)
    stop, sels = pilot_decide(merged, per, cfg, ceil)
    return stop, sels, ceil


def ceiling_problems(doc: dict, cfg: dict, base_seed: int, step: str) -> list[str]:
    """design 3.0: the step runs only when results/ceiling/ceiling.json says go for it (by model A) and was made under
    this config (fingerprint, seed, P, world and value, main_auc, the instruments)."""
    c = cfg["ceiling"]
    out = []
    s = doc.get("steps", {}).get(step)
    if not isinstance(s, dict):
        return [f"ceiling.json has no step {step} (run --ceiling first)"]
    if s.get("status") != "go":
        out.append(f"step {step} is {s.get('status')} in ceiling.json: not run (design 3.0)")
    res = doc.get("results", {}).get(step)
    try:  # the status must follow from the measured values
        again = ce.step_status(res, c["main_auc"])
    except (KeyError, TypeError):
        again = None
    keys = ("status", "status_A", "status_A_speed")
    if again is None or any(again[k] != s.get(k) for k in keys):
        out.append(f"step {step}: the statuses {[s.get(k) for k in keys]} do not follow from the measured values "
                   f"({None if again is None else [again[k] for k in keys]})")
    want = step_doc(cfg, step)
    if any(s.get(k) != v for k, v in want.items()):
        out.append(f"ceiling.json step {step} is not config.json's {want}")
    if doc.get("seed") != base_seed + c["seed_offset"]:
        out.append(f"ceiling.json seed {doc.get('seed')} is not SEED + {c['seed_offset']}")
    if doc.get("main_auc") != c["main_auc"] or doc.get("P", {}).get(step) != c["P"]:
        out.append(f"ceiling.json main_auc {doc.get('main_auc')} / P {doc.get('P', {}).get(step)} are not the config's")
    if doc.get("config_fingerprint") != ce.cfg_fingerprint(cfg):
        out.append("ceiling.json was made under another config.json (fingerprint)")
    if doc.get("code_fingerprint") != ce.code_fingerprint():
        out.append("ceiling.json was made by other instruments (code fingerprint): run --ceiling again")
    return out


def check_ceiling_file(cfg: dict, cfg_path: Path, step: str) -> None:
    base_seed = int((cfg_path.parent / "SEED").read_text().strip())
    f = cfg_path.parent / "results" / "ceiling" / "ceiling.json"
    if not f.exists():
        raise SystemExit(f"{f} is missing (run --ceiling first)")
    bad = ceiling_problems(json.loads(f.read_text(encoding="utf-8")), cfg, base_seed, step)
    if bad:
        raise SystemExit(f"{f}: {bad}")


def pilot_check(p: dict, cfg: dict, base_seed: int, step: str) -> dict:
    """Is this pilot.json the pilot of this config and this step? Checks the world and value, the step, the seed, P,
    bootstrap, rule and the fingerprints, then recomputes each base's stop and selection from its maxima, fits and
    AUC (part_result). Returns the errors, the lambdas per base (S absent when its part stopped) and the S stop."""
    sp, ps = cfg["sets"]["pilot"], cfg["pc_stall"]
    out = {"errors": [], "lam": None, "stop_S": None}
    err = out["errors"]
    if "parts" not in p or "rule" not in p or "stop" not in p:
        err.append("not a relative timing pilot.json (no parts, rule or stop)")
        return out
    if p.get("step") != step or p.get("world_doc") != step_doc(cfg, step):
        err.append(f"step {p.get('step')} / world {p.get('world_doc')} is not {step} / {step_doc(cfg, step)}")
    if p.get("seed") != base_seed + sp["seed_offset"]:
        err.append(f"seed {p.get('seed')} is not SEED + {sp['seed_offset']} = {base_seed + sp['seed_offset']}")
    if p.get("n_sessions") != sp["P"] or p.get("bootstrap") != sp["bootstrap"]:
        err.append(f"P {p.get('n_sessions')} / bootstrap {p.get('bootstrap')} is not {sp['P']} / {sp['bootstrap']}")
    if p["rule"] != {k: ps[k] for k in RULE_KEYS}:
        err.append(f"the rule {p['rule']} is not the config's")
    if p.get("config_fingerprint") != ce.cfg_fingerprint(cfg):
        err.append("the pilot was made under another config.json (fingerprint)")
    if p.get("code_fingerprint") != ce.code_fingerprint():
        err.append("the pilot was made by other instruments (code fingerprint): run it again")
    if p["stop"]:
        err.append(f"the A part of the pilot stopped ({p['stop']}): the step does not go on (design 3.0)")
    if not isinstance(p.get("parts"), dict) or sorted(p["parts"]) != sorted(BASES):
        err.append(f"the parts are not one per base {list(BASES)}")
    if err:
        return out
    lam = {}
    for b in BASES:
        part = p["parts"][b]
        need = ("stop", "selection", "configs", "per_batch", "auc_base")
        if not isinstance(part, dict) or any(k not in part for k in need):
            err.append(f"the {b} part is incomplete")
            continue
        merged = {k: ({kk: _num(v[kk]) for kk in ("gain_max", "lower_max")} if v else None)
                  for k, v in part["configs"].items()}
        auc = None if part["auc_base"] is None else {k: _num(v) for k, v in part["auc_base"].items()}
        stop, again, _ = part_result(merged, part["per_batch"], auc, cfg)
        if stop != part["stop"]:
            err.append(f"the {b} part's stop {part['stop']} does not follow from its values ({stop})")
            continue
        if b == "A" and part["stop"] != p["stop"]:
            err.append("the A part's stop is not the pilot's stop")
            continue
        if b == "S" and stop:
            out["stop_S"] = stop
            continue
        mine = {c: part["selection"].get(c, {}).get("lam") for c in st.candidates()}
        if {c: again[c]["lam"] for c in st.candidates()} != mine:
            err.append(f"the {b} selection does not follow from the pilot's maxima")
            continue
        lam[b] = mine
    if not err:
        out["lam"] = lam
    return out


def lam_problems(cfg: dict, step: str, base: str) -> list[str]:
    """Every candidate has a lambda chosen on the pilot's grid, for this step and base (a string, a NaN or a value
    off the grid is not a pilot's choice)."""
    ps = cfg["pc_stall"]
    grid = [float(x) for x in ps["pilot_grid"]]
    table = ps["lam"].get(step, {}).get(base) if isinstance(ps["lam"].get(step), dict) else None
    if not isinstance(table, dict):
        return [f"pc_stall.lam.{step}.{base}: not set (run the pilot of the step and --apply-pilot first)"]
    out = []
    for c in st.candidates():
        v = table.get(c)
        if v is None:
            out.append(f"lam.{step}.{base}.{c}: not set")
        elif type(v) not in (int, float) or not any(abs(float(v) - x) < 1e-12 for x in grid):
            out.append(f"lam.{step}.{base}.{c}: {v!r} is not a value of pc_stall.pilot_grid")
    extra = sorted(set(table) - set(st.candidates()))
    if extra:
        out.append(f"lam.{step}.{base}: unknown names {extra}")
    return out


def apply_pilot(cfg_path: Path, pilot_path: Path, step: str) -> int:
    """Write the pilot's choices to config.json pc_stall.lam.<step> = {"A": ..., "S": ...} (S left out when its part
    stopped); the rest of the file is kept as it is."""
    p = json.loads(pilot_path.read_text(encoding="utf-8"))
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_seed = int((cfg_path.parent / "SEED").read_text().strip())
    chk = pilot_check(p, cfg, base_seed, step)
    if chk["errors"]:
        raise SystemExit(f"refused to write pc_stall.lam.{step}: {chk['errors']}")
    cfg["pc_stall"]["lam"][step] = dict(chk["lam"])
    bad = [x for b in chk["lam"] for x in lam_problems(cfg, step, b)]
    if bad:
        raise SystemExit(f"pilot selection is not on the grid: {bad}")
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"lam": chk["lam"], "stop_S": chk["stop_S"]}, indent=1))
    return 0


def pilot_parts(tab: dict, ms: list[dict], work: Path, cfg: dict, seed: int, jobs: int, nboot: int, scratch: Path,
                t0: float) -> dict:
    """design 1.5: PC1 and the PC-stall of each candidate on [0] + the grid, one candidate at a time, each batch fitted
    on both bases. A base whose classifiers are both at its ceiling after the first batch (PC1) is not fitted further:
    its stop is "ceiling" either way (a failed fit depends on the labels and the folds only, the same in every batch,
    so pilot_stop reads the same)."""
    grid = [float(x) for x in cfg["pc_stall"]["pilot_grid"]]
    cands = st.candidates()
    batches = [("PC1", [("PC1", "PC1", None)])]
    batches += [(c, [(pilot_key(c, x), f"PCs-{c}", x) for x in [0.0] + grid]) for c in cands]
    keys = [k for _, sp in batches for k, _, _ in sp]
    if len(set(keys)) != len(keys):
        raise SystemExit("pc_stall.pilot_grid: two values share a name at three decimals")
    state = {b: {"merged": {}, "per": {}, "timing": [], "auc": None, "skipped_after": None} for b in BASES}
    active = list(BASES)
    for bname, specs in batches:
        if not active:
            break
        tb = time.time()
        F = run_stage(specs, ms, work, seed, jobs)
        names = {}
        for i, (key, *_) in enumerate(specs):
            save(scratch, f"F-{bname}-{i}", F[key])
            names[key] = f"F-{bname}-{i}"
        del F
        ts = time.time() - tb
        for b in list(active):
            s_ = state[b]
            r = e13_target(TAG, tab[TAG], names, cfg, seed, jobs, nboot, 0, scratch, [], base=b)
            if r.get("auc_base") is None:
                s_["per"][bname] = {"fit_failed": True}
                s_["merged"].update({k: None for k in names})
                continue
            s_["auc"] = r["auc_base"]
            s_["merged"].update(r["configs"])
            s_["timing"].append({"batch": bname, "n_configs": len(specs), "stage_s": ts, **r["timing"]})
            s_["per"][bname] = {"fit_failed": False}
            if bname == "PC1" and all(k in ceiling_kinds(r["auc_base"], cfg) for k in KINDS):
                s_["skipped_after"] = "PC1"
                active.remove(b)
        print(f"pilot {bname}: {time.time() - tb:.0f} s (total {time.time() - t0:.0f} s)", flush=True)
    parts = {}
    for b in BASES:
        s_ = state[b]
        stop, sels, ceil = part_result(s_["merged"], s_["per"], s_["auc"], cfg)
        for c in cands:
            line = " ".join(f"{x:.3f}:{s_['merged'][pilot_key(c, x)]['gain_max']:+.3f}/"
                            f"{s_['merged'][pilot_key(c, x)]['lower_max']:+.3f}"
                            for x in [0.0] + grid if s_["merged"].get(pilot_key(c, x)))
            print(f"{b} {c}: lambda {sels[c]['lam'] if sels else None} ({sels[c]['rule'] if sels else stop})\n   {line}")
        parts[b] = {"stop": stop, "auc_base": s_["auc"], "ceiling_kinds": ceil, "skipped_after": s_["skipped_after"],
                    "configs": {k: ({kk: v[kk] for kk in REC_KEYS} | {"attackers": v["attackers"]} if v else None)
                                for k, v in s_["merged"].items()},
                    "per_batch": s_["per"], "selection": sels, "timing": s_["timing"]}
    return parts


def pilot(cfg: dict, seed: int, work: Path, out: Path, jobs: int, step: str) -> int:
    """design 1.5, 3.0: pilot 1 of a step on both bases. A stopped A part stops the step; a stopped S part makes the
    secondary verdicts undecidable (pilot_stop)."""
    bad = world_problems(work, cfg, step)
    if bad:
        raise SystemExit(f"pilot: {bad}")
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    t0 = time.time()
    scratch = Path(tempfile.mkdtemp(prefix="pilot-", dir=work))
    nboot = cfg["sets"]["pilot"]["bootstrap"]
    ps = cfg["pc_stall"]
    try:
        tab = label_tables(work, sids, cfg, scratch)
        parts = pilot_parts(tab, ms, work, cfg, seed, jobs, nboot, scratch, t0)
        dump(out / "pilot.json", {
            "_note": ("Pilot 1 (design 1.5): SEED + 1, P sessions of the step's world; PC1 and the PC-stall of each "
                      "candidate on [0] + the grid, on base A and base A_speed (S), no null. Not a result of the main "
                      "run. `checks.py --apply-pilot config.json <this file> <step>` writes the chosen lambdas to "
                      "pc_stall.lam.<step>.<base>; the numbers go to design section 8. A stopped A part stops the "
                      "step; a stopped S part leaves the secondary verdicts undecidable (pilot_stop)."),
            "world_doc": step_doc(cfg, step), "step": step,
            "seed": seed, "n_sessions": len(sids), "bootstrap": nboot, "rule": {k: ps[k] for k in RULE_KEYS},
            "config_fingerprint": ce.cfg_fingerprint(cfg), "code_fingerprint": ce.code_fingerprint(),
            "stop": parts["A"]["stop"], "parts": parts, "wall_s": time.time() - t0})
        for b, part in parts.items():
            if part["stop"]:
                print(f"pilot {b} STOP: {part['stop']}", flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"pilot done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main_lams(cfg: dict, pilot_json: Path, base_seed: int, step: str) -> tuple[dict, str | None]:
    """The main run reads the step's pilot.json itself, not only config.json. Returns the lambdas per base (S absent
    when its part stopped) and the S stop."""
    if not pilot_json.exists():
        raise SystemExit(f"{pilot_json} is missing (run the pilot of step {step} first)")
    chk = pilot_check(json.loads(pilot_json.read_text(encoding="utf-8")), cfg, base_seed, step)
    if chk["errors"]:
        raise SystemExit(f"{pilot_json}: {chk['errors']}")
    bad = [x for b in chk["lam"] for x in lam_problems(cfg, step, b)]
    if bad or cfg["pc_stall"]["lam"].get(step) != chk["lam"]:
        raise SystemExit(f"config.json pc_stall.lam.{step} is not the pilot's choice: {bad}")
    return chk["lam"], chk["stop_S"]


def lam_of(lams: dict, base: str) -> dict:
    """Seam: the PC-stall lambdas of a base (selftest's mutant shares A's between the bases)."""
    return lams[base]


def main_specs(cands: list[str], lams: dict, stop_s: str | None) -> tuple[list[tuple], dict]:
    """design 1.4, 1.5: the stage names of the main run and, per base, name -> stage key. The PC-stall of a candidate
    is run at the base's own lambda (one run when the two bases chose the same); a base whose pilot part stopped has
    no PC-stall."""
    specs = ([(c, c, None) for c in cands] + [("PC1", "PC1", None)] + [(f"PC0-{c}", f"PC0-{c}", 0.0) for c in cands]
             + [("PC-corr", "PC-corr", None)])
    plain = [s[0] for s in specs]
    per_base = {}
    for b in BASES:
        m = {n: n for n in plain}
        if not (b == "S" and stop_s):
            lt = lam_of(lams, b)
            for c in cands:
                key = pilot_key(c, lt[c])
                if key not in [s[0] for s in specs]:
                    specs.append((key, f"PCs-{c}", float(lt[c])))
                m[f"PCs-{c}"] = key
        per_base[b] = m
    return specs, per_base


def main_run(cfg: dict, seed: int, work: Path, out: Path, jobs: int, step: str, lams: tuple[dict, str | None]) -> int:
    """lams: main_lams of the unmodified config (main() checks it before the smoke changes the bootstrap)."""
    bad = world_problems(work, cfg, step)
    if bad:
        raise SystemExit(f"main: {bad}")
    lam, stop_s = lams
    cands = st.candidates()
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    specs, per_base = main_specs(cands, lam, stop_s)
    t0 = time.time()
    scratch = Path(tempfile.mkdtemp(prefix="main-", dir=work))
    try:
        tab = label_tables(work, sids, cfg, scratch)
        F = run_stage(specs, ms, work, seed, jobs)
        files = {}
        for i, (key, *_) in enumerate(specs):
            save(scratch, f"F-{i}", F[key])
            files[key] = f"F-{i}"
        del F
        print(f"stage runs: {len(specs)} x {len(sids)} in {time.time() - t0:.0f} s", flush=True)
        e13 = {}
        for b in BASES:
            names = {n: files[k] for n, k in per_base[b].items()}
            forced = "pilot_stop" if (b == "S" and stop_s) else None
            nperm = 0 if forced else cfg["e13"]["null_perms"]
            e13[b] = e13_target(TAG, tab[TAG], names, cfg, seed, jobs, cfg["e13"]["bootstrap"], nperm, scratch, cands,
                                base=b, forced=forced)
            if forced:
                e13[b]["pilot_stop_S"] = stop_s
            verd = {c: e13[b]["configs"].get(c, {}).get("verdict", "undecidable") for c in cands}
            red = [c for c in cands if verd[c].startswith("red")]
            _init(str(scratch))
            e13[b]["importance_red"] = {c: importance(tab[TAG], files[c], seed, b) for c in red}
            e13[b]["dropped"] = dropped(TAG, tab[TAG], b, e13[b], {c: files[c] for c in cands}, red, cfg, seed, jobs,
                                        scratch)
            print(f"E1 base {BASE_NAME[b]} done at {time.time() - t0:.0f} s: "
                  + ", ".join(f"{v}={sum(x == v for x in verd.values())}" for v in sorted(set(verd.values()))),
                  flush=True)
        sma = speed_minus_a(e13["A"], e13["S"], tab[TAG])
        desc_e = {"speed_minus_A": sma, "ratio_to_speed": ratio_to_speed(e13["A"], sma, cands, cfg),
                  "stage_alone": stage_alone(TAG, tab[TAG], {c: files[c] for c in cands}, cands, e13["A"], cfg, seed,
                                             jobs, scratch)}
        doc = {b: public(e13[b]) for b in BASES}
        doc.update({"primary": "A", "label": TAG, "seed": seed, "step": step, "world": step_doc(cfg, step),
                    "lambdas": lam, "stop_S": stop_s, "descriptions": desc_e})
        dump(out / "e13.json", doc)
        u_by = ({m["sid"]: session_u(seed, m["sid"]) for m in ms} if step_world(cfg, step) == "factor" else None)
        desc = describe(cands + ["PC-corr"], cands, ms, cfg, seed, work, jobs, u_by)
        dump(out / "describe.json", {"_note": "Descriptive (items 2-4, 6 and (d2)): no verdict.", **desc})
        ctrl = ["PC1"] + [f"PCs-{c}" for c in cands] + [f"PC0-{c}" for c in cands] + ["PC-corr"]
        summ = {"verdicts": {BASE_NAME[b]: {c: e13[b]["configs"].get(c, {}).get("verdict", "undecidable")
                                            for c in cands} for b in BASES},
                "_controls": {BASE_NAME[b]: {n: e13[b]["configs"].get(n, {}).get("verdict") for n in ctrl}
                              for b in BASES},
                "_detector": {BASE_NAME[b]: {k: e13[b].get(k) for k in (
                    "auc_base", "ceiling_kinds", "pc1_ok", "null_all_73_ok", "nan", "fit_failed", "detector",
                    "pilot_stop_S")} for b in BASES},
                "auc": {BASE_NAME[b]: e13[b].get("auc_base") for b in BASES}, "speed_minus_A": sma,
                "_step": {"step": step, **step_doc(cfg, step)}}
        if step_world(cfg, step) == "factor":  # described only (the copied file's record of the factor world)
            jumps = work / "speed_jumps.json"
            if not jumps.exists():
                raise SystemExit(f"{jumps} is missing (factor world)")
            jd = json.loads(jumps.read_text(encoding="utf-8"))
            if jd.get("c") != step_value(cfg, step) or not jd.get("pairs"):
                raise SystemExit(f"{jumps} has c {jd.get('c')} and {len(jd.get('pairs') or {})} pairs, not step {step}'s")
            shutil.copyfile(jumps, out / "speed_jumps.json")
        summ["_wall_s"] = time.time() - t0
        dump(out / "summary.json", summ)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main() -> int:
    import sys
    if len(sys.argv) == 5 and sys.argv[1] == "--apply-pilot":  # checks.py --apply-pilot <config> <pilot.json> <step>
        return apply_pilot(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("work")
    ap.add_argument("results")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--step", required=True, help="design 1.3: g050 or f200")
    ap.add_argument("--pilot-json", default=None, help="the main run and the smoke: the step's pilot.json")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--smoke", action="store_true")
    g.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    step_value(cfg, a.step)
    check_ceiling_file(cfg, Path(a.config), a.step)  # design 3.0: a go step of this config only
    seed = int(Path(a.seed_file).read_text().strip())
    base_seed = int((Path(a.config).parent / "SEED").read_text().strip())
    work, out = Path(a.work), Path(a.results)
    if a.pilot:
        out.mkdir(parents=True, exist_ok=True)
        return pilot(cfg, seed, work, out, a.jobs, a.step)
    if not a.pilot_json:
        raise SystemExit("--pilot-json is required by the main run and the smoke")
    lams = main_lams(cfg, Path(a.pilot_json), base_seed, a.step)  # before the smoke changes the config
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = 200, 2
    out.mkdir(parents=True, exist_ok=True)
    return main_run(cfg, seed, work, out, a.jobs, a.step, lams)


if __name__ == "__main__":
    raise SystemExit(main())
