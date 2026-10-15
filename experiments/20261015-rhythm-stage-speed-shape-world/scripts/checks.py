"""Checks of the rhythm stage desk check: item 1 (verdicts, design 3.1-3.3), items 2-4 and 6 (descriptions, 3.4),
the importance of the red candidates (3.6) and the pilot 1 (the lambda of each PC-stall, 3.9).

Design: .steering/20261012-rhythm-stage-desk-check/design.md (frozen 2b7db259; world v4); round 2
(.steering/20261013-rhythm-stage-round2/design.md 3.9) replaces select_lambda and the pilot's choice (pilot_key,
pilot_stop, choose_all, apply_pilot). The graded world (.steering/20261014-rhythm-stage-graded-world/design.md 1.2,
1.4, 3.9) adds the L1800 controls (PC1-1800, PCl-; fitted on L1800 only), a pilot with an L300 and an L1800 part,
the lambdas per step, and the checks of the step (world.json, pilot.json). The confound world
(.steering/20261014-rhythm-stage-speed-confound-world/design.md 1.2) keeps all of it with the steps renamed: the
step's value is the width c of the speed confound (step_c) and the world is "confound". The shape world
(.steering/20261015-rhythm-stage-speed-shape-world/design.md 1.2, 1.3; copied from
experiments/20261014-rhythm-stage-speed-confound-world/scripts/checks.py at 7d38df98) reads each step's world from
config.json ceiling.worlds (step_world: "factor" or "drift") and adds the pilot's third part L300r: the r-side controls
PCrl- and PCrv- of each candidate on [0] + the grid, whose lambdas go to pc_r.lam.<step> (null for a family and
candidate with no finite point estimate; never a stop). The r-side controls are descriptive here (kind_of): item 1
does not use them; split.py fits them.

Usage (after the pilot of a step): checks.py --apply-pilot <config.json> <results/<step>/pilot/pilot.json> <step>

The statistics are copied from experiments/20261010-portrait-eh1-round5/scripts/checks.py (auc_prep, auc_w,
weighted_auc, oof_predict, stratified_permutation, isotonic_blocks, select_lambda, the bootstrap and the null) with
two changes the design asks for: the base model is A_speed (design 1.5; the gain is AUC(B) - AUC(A_speed)), and a
classifier whose AUC(A_speed) is at the ceiling is left out of every maximum of its label (design 3.2). A fold whose
training side holds one class is reported as a failed fit (checked before the fit, as ceiling.py); any other error
stops the run.

Usage: checks.py <config.json> <seed file> <work dir> <results dir> --step <step> [--jobs N]
                 [--smoke | --pilot] [--pilot-json <results/<step>/pilot/pilot.json>]
  (no mode)  the main run: 24 candidates, PC1, PC-stall and PC0 of each candidate, PC-corr; three labels, and on
             L1800 PC1-1800 and PCl- of each candidate; bootstrap e13.bootstrap, e13.null_perms permutations; the
             descriptions (needs <work>/twins replayed); --pilot-json is required
  --smoke    the same with bootstrap 200 and 2 permutations (pipeline check only)
  --pilot    design 3.9: the L300 part (PC1 and PCs-) and the L1800 part (PC1-1800 and PCl-) on the lambda grid,
             bootstrap sets.pilot.bootstrap, no null; one candidate at a time; writes pilot.json
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


def select_lambda(lams: list[float], gains: list[float], lowers: list[float], aim: float, lower: float,
                  upper: float) -> dict:
    """Round 2 design 3.9: choose lambda (> 0) of one candidate from the pilot's L300 maxima over the attackers in
    use. gains: the point estimate g, lowers: the lower bound l of the 95% interval, per lambda. In the band:
    l > lower and g <= upper (the comparisons of design 3.2; a NaN bound is out). The isotonic fit of g (NaN g left
    out) gives g_hat; among the lambdas in the band (else among all) the smallest |g_hat - aim| (rounded to 6
    decimals) wins; the ties are the lambdas of that pool with the same distance, in ascending order, and of them the
    middle index (the smaller of two middles) wins. No finite g -> lam None (the pilot stops)."""
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
# Names and verdicts (design 3.2, 3.3): pure functions, unit-tested in selftest.py
# ---------------------------------------------------------------------------

def kind_of(name: str, tag: str) -> str:
    """The role of a name on a label (graded world design 1.2, 1.4): on L1800 the strong control is PC1-1800 and the
    PC-stall is PCl-, and the round 2 PC1 and PCs- are descriptive; on L300 and L60 as round 2, and PC1-1800 and PCl-
    (fitted on L1800 only) are refused. A name on the pilot's grid (with @) is descriptive."""
    l1800 = tag == "L1800"
    if name.startswith(st.PCR_PREFIXES):  # shape world design 1.3: never judged on any label
        return "descriptive"
    if name == st.PC1L_NAME:
        if not l1800:
            raise ValueError(f"{name} is fitted on L1800 only, not on {tag}")
        return "pc1"
    if name == "PC1":
        return "descriptive" if l1800 else "pc1"
    if name == "PC-corr":
        return "descriptive"
    if name.startswith(st.PCL_PREFIX):
        if "@" in name:
            return "descriptive"
        if not l1800:
            raise ValueError(f"{name} is fitted on L1800 only, not on {tag}")
        return "pcs"
    if name.startswith("PCs-"):
        return "descriptive" if ("@" in name or l1800) else "pcs"
    if name.startswith("PC0-"):
        return "pc0"
    if name.startswith("S-"):
        return "candidate"
    raise ValueError(name)


def control_names(tag: str) -> tuple[str, str]:
    """(the strong control, the PC-stall prefix) judged on a label (graded world design 1.4)."""
    return (st.PC1L_NAME, st.PCL_PREFIX) if tag == "L1800" else ("PC1", "PCs-")


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


def judge(attk: dict, nulls: dict | None, auc_s: dict | None, cands: list[str], cfg: dict, fit_failed: bool, *,
          tag: str, forced: str | None = None) -> dict:
    """One label (design 3.2, 3.3). tag: the label (its controls, graded world design 1.4). forced: a reason that
    makes every candidate undecidable (pilot_stop on L1800 when the pilot's L1800 part stopped, design 3.9).
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
    # label-wide (design 3.1), over the judged names only: PC-corr is outside the detector (design 1.4)
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
        if forced:  # code-reviewer round 2 L2: the forced reason first, the others kept
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
               nperm: int, scratch: Path, cands: list[str], null_names: list[str] | None = None,
               forced: str | None = None) -> dict:
    """One label. names: name -> scratch file of its window features. desc_a: the names whose gain over model A
    (B' = A + the stage) is described (design 1.5). null_names: the names whose null is run (None = all; graded
    world design 1.2: on L1800 not the descriptive PC1 and PCs-). forced: see judge."""
    perm_names = list(names) if null_names is None else [n for n in names if n in set(null_names)]
    folds = cfg["e13"]["folds"]
    Y, G, strata = tab["Y"], tab["G"], tab["strata"]
    n_sess = int(G.max()) + 1
    timing: dict = {}

    def fit_all(y: np.ndarray, t: str, with_desc: bool) -> dict:
        want = "pred" if t == "obs" else "auc"
        which = names if t == "obs" else {n: names[n] for n in perm_names}
        js = [((t, "S", None, k), tag, "S", None, None, k, y, seed, folds, want) for k in KINDS]
        js += [((t, n, fs, k), tag, "S", f, fs, k, y, seed, folds, want) for n, f in which.items() for fs in FSETS
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
        res.update(judge({}, None if not nperm else {}, None, cands, cfg, True, tag=tag, forced=forced))
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
        nulls = {n: [] for n in perm_names}
        prng = np.random.default_rng(np.random.SeedSequence([seed, 911, LABEL_ID[tag]]))
        for pi in range(nperm):
            yp = stratified_permutation(Y, strata, prng)
            pp = fit_all(yp, f"perm{pi}", False)
            if any(v is None for v in pp.values()):
                res["null_fit_failed"] = True
                res.update(judge(attk, None, auc_s, cands, cfg, True, tag=tag, forced=forced))
                res["configs"] = attk
                return res
            for n in perm_names:
                nulls[n].append({f"{fs}/{k}": pp[(f"perm{pi}", n, fs, k)] - pp[(f"perm{pi}", "S", None, k)]
                                 for fs in FSETS for k in KINDS})
    j = judge(attk, nulls, auc_s, cands, cfg, False, tag=tag, forced=forced)
    for n in names:
        res["configs"][n] = {"attackers": attk[n], **j["maxima"][n], "verdict": j["verdicts"].get(n)}
        if nulls is not None and n in nulls:
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


def lags_readable(name: str) -> bool:
    """design section 8 (decisions 18): the wobble of the jitter candidates alone moves the lag measure in most events
    (|m1 - m0| >= 0.05 within 10 s), so their lags are reported but not read."""
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
            r = {"item2_per_second_auc": oof_auc_lr(Xs, ys, gs, folds, seed), "item2_lags": summarize_lags(lags),
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

def pilot_key(cand: str, lam: float, prefix: str = "PCs-") -> str:
    """The pilot's name of the PC-stall of a candidate at lambda (three decimals: 0.025 and 0.075 stay apart);
    prefix PCl- for the L1800 control (graded world design 1.4)."""
    return f"{prefix}{cand}@{float(lam):.3f}"


# graded world design 1.2, 1.4, 3.9: the pilot has two parts; each has its strong control and its PC-stall prefix
PILOT_PARTS = {"L300": ("PC1", "PCs-", "lam"), "L1800": (st.PC1L_NAME, st.PCL_PREFIX, "lam_1800")}


def pilot_stop(merged: dict, per: dict, cfg: dict, ceil: list[str], pc1_name: str = "PC1") -> str | None:
    """Round 2 design 3.9: the pilot chooses no lambda when a fit failed, both classifiers are at the ceiling, or
    the strong control does not work (its lower bound must be finite and > e13.pc_lower; Codex: a NaN must not pass).
    ceil is the ceiling of the part's own label (graded world design 3.7: L1800 reads L1800's AUC(A_speed))."""
    if any(v.get("fit_failed") for v in per.values()) or not per:
        return "fit_failed"
    if all(k in ceil for k in KINDS):
        return "ceiling"
    pc1 = merged.get(pc1_name)
    if not pc1 or not _gt(pc1["lower_max"], cfg["e13"]["pc_lower"]):
        return "weak_detector"
    return None


def choose_all(merged: dict, cfg: dict, prefix: str = "PCs-", grid: list[float] | None = None) -> dict:
    """Round 2 design 3.9: the lambda of every candidate from the pilot's maxima (lambda = 0 is never a choice).
    grid: the lambdas (default pc_stall.pilot_grid; the r-side controls use pc_r.pilot_grid, shape world design 1.3)."""
    ps = cfg["pc_stall"]
    grid = [float(x) for x in (ps["pilot_grid"] if grid is None else grid)]
    out = {}
    for c in st.candidates():
        recs = [merged.get(pilot_key(c, x, prefix)) for x in grid]
        g = [r["gain_max"] if r else float("nan") for r in recs]
        lo = [r["lower_max"] if r else float("nan") for r in recs]
        out[c] = select_lambda(grid, g, lo, ps["aim"], ps["lower"], ps["upper"])
    return out


RULE_KEYS = ("pilot_grid", "aim", "lower", "upper")


def pilot_decide(merged: dict, per: dict, cfg: dict, ceil: list[str], pc1_name: str = "PC1",
                 prefix: str = "PCs-") -> tuple[str | None, dict]:
    """Round 2 design 3.9: (stop, selection). A stop leaves no lambda to write: the pilot's own stop, or a candidate
    with no finite point estimate (its selection stays as a record)."""
    stop = pilot_stop(merged, per, cfg, ceil, pc1_name)
    if stop:
        return stop, {}
    sels = choose_all(merged, cfg, prefix)
    if any(s["lam"] is None for s in sels.values()):
        return "no_finite_pcs", sels
    return None, sels


def _num(v):
    """A maximum read back from pilot.json (clean() writes NaN as the string "nan")."""
    return float("nan") if v in ("nan", None) else float(v)


def step_c(cfg: dict, step: str) -> float:
    steps = cfg["ceiling"]["steps"]
    if step not in steps:
        raise SystemExit(f"unknown step {step!r}: not in config.json ceiling.steps {sorted(steps)}")
    return float(steps[step])


def step_world(cfg: dict, step: str) -> str:
    """shape world design 1.2: the world of a step (config.json ceiling.worlds, which names every step)."""
    worlds = cfg["ceiling"]["worlds"]
    if step not in worlds or sorted(worlds) != sorted(cfg["ceiling"]["steps"]):
        raise SystemExit(f"step {step!r}: config.json ceiling.worlds {worlds} does not name it (or not every step)")
    return str(worlds[step])


def world_problems(work: Path, cfg: dict, step: str) -> list[str]:
    """graded world design 1.2, 3.7 (confound world 1.2, shape world 1.2): the work directory was made with
    --world <the step's world> --c <the step's c>."""
    f = work / "world.json"
    if not f.exists():
        return [f"{f} is missing"]
    w = json.loads(f.read_text(encoding="utf-8"))
    want = {"world": step_world(cfg, step), "c": step_c(cfg, step)}
    return [] if w == want else [f"{f} is {w}, not {want} (step {step})"]


def part_result(tag: str, merged: dict, per: dict, auc_s: dict | None, cfg: dict) -> tuple[str | None, dict, list]:
    """design 3.9: (stop, selection, ceiling) of one part of the pilot from its own maxima, fits and AUC(A_speed)
    (the ceiling of the part's own label: code-reviewer round 2 M3). pilot_part writes it; pilot_check recomputes it."""
    pc1_name, prefix, _ = PILOT_PARTS[tag]
    ceil = ceiling_kinds(auc_s, cfg)
    stop, sels = pilot_decide(merged, per, cfg, ceil, pc1_name, prefix)
    return stop, sels, ceil


def ceiling_problems(doc: dict, cfg: dict, base_seed: int, step: str) -> list[str]:
    """graded world design 3.0 (cross-review round 2): the step runs only when results/ceiling/ceiling.json says go
    for it and was made under this config (fingerprint, seed, P, c, main_auc)."""
    c = cfg["ceiling"]
    out = []
    s = doc.get("steps", {}).get(step)
    if not isinstance(s, dict):
        return [f"ceiling.json has no step {step} (run --ceiling first)"]
    if s.get("status") != "go":
        out.append(f"step {step} is {s.get('status')} in ceiling.json: not run (design 3.0)")
    res = doc.get("results", {}).get(step)
    try:  # Codex round 3: the status must follow from the measured values
        again = ce.step_status(res, c["main_auc"])["status"]
    except (KeyError, TypeError):
        again = None
    if again != s.get("status"):
        out.append(f"step {step}: the status {s.get('status')} does not follow from the measured values ({again})")
    if s.get("c") != step_c(cfg, step) or s.get("world") != step_world(cfg, step):
        out.append(f"ceiling.json c {s.get('c')} / world {s.get('world')} are not config.json's "
                   f"{step_c(cfg, step)} / {step_world(cfg, step)}")
    if doc.get("seed") != base_seed + c["seed_offset"]:
        out.append(f"ceiling.json seed {doc.get('seed')} is not SEED + {c['seed_offset']}")
    if doc.get("main_auc") != c["main_auc"] or doc.get("P", {}).get(step) != c["P"]:
        out.append(f"ceiling.json main_auc {doc.get('main_auc')} / P {doc.get('P', {}).get(step)} are not the config's")
    if doc.get("config_fingerprint") != ce.cfg_fingerprint(cfg):
        out.append("ceiling.json was made under another config.json (fingerprint)")
    if doc.get("code_fingerprint") != ce.code_fingerprint():
        out.append("ceiling.json was made by other instruments (code fingerprint): run --ceiling again (design 3.3 (f))")
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
    """graded world design 1.2, 3.7: is this pilot.json the pilot of this config and this step? Checks the world, c
    and step (the three steps share a seed: Codex and code-reviewer round 1), the seed, P, bootstrap, rule and the
    config's fingerprint (cross-review round 2), then recomputes each part's stop and selection from its maxima, fits
    and AUC (part_result). Returns the errors, the L300 lambdas, the L1800 lambdas (None when the L1800 part stopped)
    and the L1800 stop."""
    sp, ps = cfg["sets"]["pilot"], cfg["pc_stall"]
    out = {"errors": [], "lam": None, "lam_1800": None, "stop_1800": None, "lam_r": None}
    err = out["errors"]
    if "parts" not in p or "rule" not in p or "stop" not in p:
        err.append("not a shape world pilot.json (no parts, rule or stop)")
        return out
    c, world = step_c(cfg, step), step_world(cfg, step)
    if p.get("world") != world or p.get("step") != step or p.get("c") != c:
        err.append(f"world {p.get('world')} / step {p.get('step')} / c {p.get('c')} is not {world} / {step} / {c}")
    if p.get("seed") != base_seed + sp["seed_offset"]:
        err.append(f"seed {p.get('seed')} is not SEED + {sp['seed_offset']} = {base_seed + sp['seed_offset']}")
    if p.get("n_sessions") != sp["P"] or p.get("bootstrap") != sp["bootstrap"]:
        err.append(f"P {p.get('n_sessions')} / bootstrap {p.get('bootstrap')} is not {sp['P']} / {sp['bootstrap']}")
    if p["rule"] != {k: ps[k] for k in RULE_KEYS}:
        err.append(f"the rule {p['rule']} is not the config's")
    if p.get("config_fingerprint") != ce.cfg_fingerprint(cfg):
        err.append("the pilot was made under another config.json (fingerprint)")
    if p.get("code_fingerprint") != ce.code_fingerprint():
        err.append("the pilot was made by other instruments (code fingerprint): run it again (design 3.3 (f))")
    if p["stop"]:
        err.append(f"the L300 part of the pilot stopped ({p['stop']}): the step does not go on (design 3.9)")
    if err:
        return out
    for tag, (_, prefix, key) in PILOT_PARTS.items():
        part = p["parts"].get(tag)
        need = ("stop", "selection", "configs", "per_batch", "auc_A_speed")
        if not isinstance(part, dict) or any(k not in part for k in need):
            err.append(f"the {tag} part is missing or incomplete")
            continue
        merged = {k: ({kk: _num(v[kk]) for kk in ("gain_max", "lower_max")} if v else None)
                  for k, v in part["configs"].items()}
        auc = None if part["auc_A_speed"] is None else {k: _num(v) for k, v in part["auc_A_speed"].items()}
        stop, again, _ = part_result(tag, merged, part["per_batch"], auc, cfg)
        if stop != part["stop"]:
            err.append(f"the {tag} part's stop {part['stop']} does not follow from its values ({stop})")
            continue
        if tag == "L300" and part["stop"] != p["stop"]:
            err.append("the L300 part's stop is not the pilot's stop")
            continue
        if tag == "L1800" and stop:
            out["stop_1800"] = stop
            continue
        mine = {c: part["selection"].get(c, {}).get("lam") for c in st.candidates()}
        if {c: again[c]["lam"] for c in st.candidates()} != mine:
            err.append(f"the {tag} selection does not follow from the pilot's maxima")
            continue
        out[key] = mine
    if not err:
        out["lam_r"] = pilot_r_check(p, cfg, err)
    return out


def pilot_r_check(p: dict, cfg: dict, err: list[str]) -> dict | None:
    """shape world design 1.3: the L300r part of a pilot.json whose L300 part did not stop. Recomputes each family's
    selection from the part's maxima and AUC (pilot_r_result). Returns {family: {candidate: lam or None}}."""
    part = p["parts"].get(PILOT_R_TAG)
    need = ("stop", "selection", "configs", "per_batch", "auc_A_speed")
    if not isinstance(part, dict) or any(k not in part for k in need):
        err.append(f"the {PILOT_R_TAG} part is missing or incomplete")
        return None
    if part["stop"] is not None:
        err.append(f"the {PILOT_R_TAG} part has stop {part['stop']} though the L300 part did not stop")
        return None
    if p.get("rule_r") != {"pilot_grid": pcr_grid(cfg)}:
        err.append(f"the {PILOT_R_TAG} rule {p.get('rule_r')} is not the config's pc_r.pilot_grid")
        return None
    merged = {k: ({kk: _num(v[kk]) for kk in ("gain_max", "lower_max")} if v else None)
              for k, v in part["configs"].items()}
    auc = None if part["auc_A_speed"] is None else {k: _num(v) for k, v in part["auc_A_speed"].items()}
    again, _ = pilot_r_result(merged, auc, cfg)
    mine = {f: {c: part["selection"].get(f, {}).get(c, {}).get("lam") for c in st.candidates()} for f in PCR_FAMILIES}
    if {f: {c: again[f][c]["lam"] for c in st.candidates()} for f in PCR_FAMILIES} != mine:
        err.append(f"the {PILOT_R_TAG} selection does not follow from the pilot's maxima")
        return None
    return mine


def apply_pilot(cfg_path: Path, pilot_path: Path, step: str) -> int:
    """Write the pilot's choices to config.json pc_stall.lam.<step> and pc_stall.lam_1800.<step> (the rest of the
    file is kept as it is). An L1800 part that stopped writes no lam_1800.<step> (graded world design 1.2)."""
    p = json.loads(pilot_path.read_text(encoding="utf-8"))
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_seed = int((cfg_path.parent / "SEED").read_text().strip())
    chk = pilot_check(p, cfg, base_seed, step)
    if chk["errors"]:
        raise SystemExit(f"refused to write pc_stall.lam.{step}: {chk['errors']}")
    cfg["pc_stall"]["lam"][step] = chk["lam"]
    if chk["lam_1800"] is not None:
        cfg["pc_stall"]["lam_1800"][step] = chk["lam_1800"]
    else:
        cfg["pc_stall"]["lam_1800"].pop(step, None)
    cfg["pc_r"]["lam"][step] = chk["lam_r"]  # shape world design 1.3 (pilot_check: set when the L300 part went on)
    bad = lam_problems(cfg, step, "lam") + (lam_problems(cfg, step, "lam_1800") if chk["lam_1800"] is not None else [])
    bad += lam_r_problems(cfg, step)
    if bad:
        raise SystemExit(f"pilot selection is not on the grid: {bad}")
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"lam": chk["lam"], "lam_1800": chk["lam_1800"], "stop_1800": chk["stop_1800"],
                      "lam_r": chk["lam_r"]}, indent=1))
    return 0


def pilot_part(tag: str, tab: dict, ms: list[dict], work: Path, cfg: dict, seed: int, jobs: int, nboot: int,
               scratch: Path, t0: float) -> dict:
    """design 3.9 (round 2) and its graded world addition: the strong control and the PC-stall of each candidate on
    [0] + the grid, on one label, one candidate at a time."""
    pc1_name, prefix, _ = PILOT_PARTS[tag]
    grid = [float(x) for x in cfg["pc_stall"]["pilot_grid"]]
    cands = st.candidates()
    merged, timing, per = {}, [], {}
    batches = [(f"{tag}-{pc1_name}", [(pc1_name, pc1_name, None)])]
    batches += [(f"{tag}-{c}", [(pilot_key(c, x, prefix), f"{prefix}{c}", x) for x in [0.0] + grid]) for c in cands]
    keys = [k for _, sp in batches for k, _, _ in sp]
    if len(set(keys)) != len(keys):  # Codex: two grid values that print alike would overwrite each other
        raise SystemExit("pc_stall.pilot_grid: two values share a name at three decimals")
    auc_s = None
    for b, specs in batches:
        tb = time.time()
        F = run_stage(specs, ms, work, seed, jobs)
        names = {}
        for i, (key, *_) in enumerate(specs):
            save(scratch, f"F-{b}-{i}", F[key])
            names[key] = f"F-{b}-{i}"
        del F
        ts = time.time() - tb
        r = e13_target(tag, tab[tag], names, [], cfg, seed, jobs, nboot, 0, scratch, [])
        if r.get("auc_A_speed") is None:
            per[b] = {"fit_failed": True}
            merged.update({k: None for k in names})
            continue
        auc_s = r["auc_A_speed"]
        merged.update({k: v for k, v in r["configs"].items()})
        timing.append({"batch": b, "n_configs": len(specs), "stage_s": ts, **r["timing"]})
        per[b] = {"fit_failed": False}
        print(f"pilot {b}: {time.time() - tb:.0f} s (total {time.time() - t0:.0f} s)", flush=True)
    stop, sels, ceil = part_result(tag, merged, per, auc_s, cfg)
    for c in cands:
        line = " ".join(f"{x:.3f}:{merged[pilot_key(c, x, prefix)]['gain_max']:+.3f}/"
                        f"{merged[pilot_key(c, x, prefix)]['lower_max']:+.3f}"
                        for x in [0.0] + grid if merged.get(pilot_key(c, x, prefix)))
        z = merged.get(pilot_key(c, 0.0, prefix))
        mark = ("  [lambda 0 upper >= 0.03: stall_baseline expected]"
                if z and not _lt(z["upper_max"], cfg["e13"]["margin"]) else "")
        print(f"{tag} {c}: lambda {sels[c]['lam'] if sels else None} ({sels[c]['rule'] if sels else 'stop'}){mark}"
              f"\n   {line}")
    return {"stop": stop, "auc_A_speed": auc_s, "ceiling_kinds": ceil,
            "configs": {k: ({kk: v[kk] for kk in REC_KEYS} | {"attackers": v["attackers"]} if v else None)
                        for k, v in merged.items()},
            "per_batch": per, "selection": sels, "timing": timing}


PILOT_R_TAG = "L300r"  # shape world design 1.3
PCR_FAMILIES = {"level": "PCrl-", "var": "PCrv-"}


def pcr_grid(cfg: dict) -> list[float]:
    """shape world design 1.3 (decisions 10): the lambdas of the r-side controls (pc_r.pilot_grid: the PC-stall's grid
    and coarser steps up to 1)."""
    return [float(x) for x in cfg["pc_r"]["pilot_grid"]]


def pilot_r_result(merged: dict, auc_s: dict | None, cfg: dict) -> tuple[dict, list]:
    """shape world design 1.3: (selection per family, ceiling) of the L300r part from its maxima (select_lambda with
    the PC-stall's rule; a candidate with no finite point estimate gets lam None, which does not stop the step)."""
    ceil = ceiling_kinds(auc_s, cfg)
    grid = pcr_grid(cfg)
    return {f: choose_all(merged, cfg, prefix, grid) for f, prefix in PCR_FAMILIES.items()}, ceil


def pilot_r_part(tab: dict, ms: list[dict], work: Path, cfg: dict, seed: int, jobs: int, nboot: int,
                 scratch: Path, t0: float) -> dict:
    """shape world design 1.3: PCrl- and PCrv- of each candidate on [0] + the grid, on L300, one candidate and family
    at a time (as pilot_part), on pc_r.pilot_grid."""
    grid = pcr_grid(cfg)
    merged, timing, per = {}, [], {}
    batches = [(f"{PILOT_R_TAG}-{f}-{c}", [(pilot_key(c, x, prefix), f"{prefix}{c}", x) for x in [0.0] + grid])
               for f, prefix in PCR_FAMILIES.items() for c in st.candidates()]
    auc_s = None
    for b, specs in batches:
        tb = time.time()
        F = run_stage(specs, ms, work, seed, jobs)
        names = {}
        for i, (key, *_) in enumerate(specs):
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
    sels, ceil = pilot_r_result(merged, auc_s, cfg)
    for f in PCR_FAMILIES:
        print(f"{PILOT_R_TAG} {f}: " + ", ".join(f"{c} {sels[f][c]['lam']}" for c in st.candidates()), flush=True)
    return {"stop": None, "auc_A_speed": auc_s, "ceiling_kinds": ceil,
            "configs": {k: ({kk: v[kk] for kk in REC_KEYS} | {"attackers": v["attackers"]} if v else None)
                        for k, v in merged.items()},
            "per_batch": per, "selection": sels, "timing": timing}


def pilot(cfg: dict, seed: int, work: Path, out: Path, jobs: int, step: str) -> int:
    """design 3.9 and the graded world addition: the L300 part (PC1, PCs-), then the L1800 part (PC1-1800, PCl-)
    on the same sessions. A stopped L300 part stops the step; the L1800 part is then not run."""
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
        parts = {"L300": pilot_part("L300", tab, ms, work, cfg, seed, jobs, nboot, scratch, t0)}
        if parts["L300"]["stop"]:
            parts["L1800"] = {"stop": "not_run_l300_stopped", "selection": {}, "configs": {}}
            parts[PILOT_R_TAG] = {"stop": "not_run_l300_stopped", "selection": {}, "configs": {}}
        else:
            parts["L1800"] = pilot_part("L1800", tab, ms, work, cfg, seed, jobs, nboot, scratch, t0)
            parts[PILOT_R_TAG] = pilot_r_part(tab, ms, work, cfg, seed, jobs, nboot, scratch, t0)
        dump(out / "pilot.json", {
            "_note": ("Pilot 1 (round 2 design 3.9, graded world design 3.9, shape world design 1.3): SEED + 1, P "
                      "sessions of the step's world; the L300 part (PC1 and the PC-stall of each candidate on [0] + the "
                      "grid), the L1800 part (PC1-1800 and PCl- of each candidate) and the L300r part (PCrl- and PCrv- "
                      "of each candidate), no null. Not a result of the main run. `checks.py --apply-pilot config.json "
                      "<this file> <step>` writes the chosen lambdas to pc_stall.lam.<step>, pc_stall.lam_1800.<step> "
                      "and pc_r.lam.<step>; the numbers go to design section 8. A stopped L300 part stops the step; a "
                      "stopped L1800 part leaves L1800 undecidable (pilot_stop); the L300r part never stops."),
            "world": step_world(cfg, step), "c": step_c(cfg, step), "step": step,
            "seed": seed, "n_sessions": len(sids), "bootstrap": nboot, "rule": {k: ps[k] for k in RULE_KEYS},
            "config_fingerprint": ce.cfg_fingerprint(cfg), "code_fingerprint": ce.code_fingerprint(),
            "rule_r": {"pilot_grid": pcr_grid(cfg)},
            "stop": parts["L300"]["stop"], "parts": parts, "wall_s": time.time() - t0})
        for tag, part in parts.items():
            if part["stop"]:
                print(f"pilot {tag} STOP: {part['stop']} (design 3.9)", flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"pilot done in {time.time() - t0:.0f} s", flush=True)
    return 0


def lam_problems(cfg: dict, step: str, key: str = "lam") -> list[str]:
    """design 3.9: every candidate has a lambda chosen on the pilot's grid, for this step (graded world design 1.2:
    pc_stall.lam and pc_stall.lam_1800 are tables per step; Codex round 2: a string, a NaN or a value off the grid
    is not a pilot's choice)."""
    ps = cfg["pc_stall"]
    grid = [float(x) for x in ps["pilot_grid"]]
    table = ps[key].get(step)
    if not isinstance(table, dict):
        return [f"pc_stall.{key}.{step}: not set (run the pilot of the step and --apply-pilot first)"]
    out = []
    for c in st.candidates():
        v = table.get(c)
        if v is None:
            out.append(f"{key}.{step}.{c}: not set")
        elif type(v) not in (int, float) or not any(abs(float(v) - x) < 1e-12 for x in grid):
            out.append(f"{key}.{step}.{c}: {v!r} is not a value of pc_stall.pilot_grid")
    extra = sorted(set(table) - set(st.candidates()))
    if extra:
        out.append(f"{key}.{step}: unknown names {extra}")
    return out


def lam_r_problems(cfg: dict, step: str) -> list[str]:
    """shape world design 1.3: pc_r.lam.<step> holds, per family, every candidate's lambda on pc_r.pilot_grid or null."""
    grid = pcr_grid(cfg)
    table = cfg["pc_r"]["lam"].get(step)
    if not isinstance(table, dict) or sorted(table) != sorted(PCR_FAMILIES):
        return [f"pc_r.lam.{step}: not a table of the families {sorted(PCR_FAMILIES)} (run the pilot and --apply-pilot)"]
    out = []
    for f in PCR_FAMILIES:
        t = table[f]
        if not isinstance(t, dict) or sorted(t) != sorted(st.candidates()):
            out.append(f"pc_r.lam.{step}.{f}: not one value per candidate")
            continue
        for c, v in t.items():
            if v is not None and (type(v) not in (int, float) or not any(abs(float(v) - x) < 1e-12 for x in grid)):
                out.append(f"pc_r.lam.{step}.{f}.{c}: {v!r} is neither null nor a value of pc_r.pilot_grid")
    return out


def main_lams_r(cfg: dict, pilot_json: Path, base_seed: int, step: str) -> dict:
    """shape world design 1.3, 1.4: pc_r.lam.<step> of config.json, checked against the step's pilot.json."""
    if not pilot_json.exists():
        raise SystemExit(f"{pilot_json} is missing (run the pilot of step {step} first)")
    chk = pilot_check(json.loads(pilot_json.read_text(encoding="utf-8")), cfg, base_seed, step)
    if chk["errors"]:
        raise SystemExit(f"{pilot_json}: {chk['errors']}")
    bad = lam_r_problems(cfg, step)
    if bad or cfg["pc_r"]["lam"][step] != chk["lam_r"]:
        raise SystemExit(f"config.json pc_r.lam.{step} is not the pilot's choice: {bad}")
    return chk["lam_r"]


def main_lams(cfg: dict, pilot_json: Path, base_seed: int, step: str) -> tuple[dict, dict | None, str | None]:
    """graded world design 1.2: the main run reads the step's pilot.json itself, not only config.json. Returns the
    L300 lambdas, the L1800 lambdas (None when the L1800 part stopped) and the L1800 stop."""
    if not pilot_json.exists():
        raise SystemExit(f"{pilot_json} is missing (run the pilot of step {step} first)")
    chk = pilot_check(json.loads(pilot_json.read_text(encoding="utf-8")), cfg, base_seed, step)
    if chk["errors"]:
        raise SystemExit(f"{pilot_json}: {chk['errors']}")
    bad = lam_problems(cfg, step, "lam")
    if bad or cfg["pc_stall"]["lam"][step] != chk["lam"]:
        raise SystemExit(f"config.json pc_stall.lam.{step} is not the pilot's choice: {bad}")
    if chk["stop_1800"] is None:
        bad = lam_problems(cfg, step, "lam_1800")
        if bad or cfg["pc_stall"]["lam_1800"][step] != chk["lam_1800"]:
            raise SystemExit(f"config.json pc_stall.lam_1800.{step} is not the pilot's choice: {bad}")
    elif step in cfg["pc_stall"]["lam_1800"]:
        raise SystemExit(f"config.json pc_stall.lam_1800.{step} is set but the pilot's L1800 part stopped")
    return chk["lam"], chk["lam_1800"], chk["stop_1800"]


def label_plan(names: dict, tag: str, cn: dict, stop1800: str | None) -> tuple[dict, list[str] | None, str | None]:
    """graded world design 1.2, 3.9: (the names fitted on the label, the names whose null is run, the forced reason).
    Only L1800 is forced to pilot_stop, and only when the pilot's L1800 part stopped (code-reviewer round 2 M3)."""
    fitted, nulls = label_names(names, tag, cn)
    return fitted, nulls, ("pilot_stop" if (tag == "L1800" and stop1800) else None)


def label_names(names: dict, tag: str, cn: dict) -> tuple[dict, list[str] | None]:
    """graded world design 1.2: the names fitted on a label and the names whose null is run (None = all). PC1-1800
    and PCl- are fitted on L1800 only; on L1800 the round 2 PC1 and PCs- are descriptive with no null."""
    extra = set(cn["pc1_1800"] + cn["pcl"])
    if tag != "L1800":
        return {n: f for n, f in names.items() if n not in extra}, None
    fitted = dict(names)
    nulls = [n for n in fitted if kind_of(n, tag) != "descriptive"] + [n for n in cn["pccorr"] if n in fitted]
    return fitted, nulls


def main_run(cfg: dict, seed: int, work: Path, out: Path, jobs: int, step: str,
             lams: tuple[dict, dict | None, str | None]) -> int:
    """lams: main_lams of the unmodified config (main() checks it before the smoke changes the bootstrap)."""
    bad = world_problems(work, cfg, step)
    if bad:
        raise SystemExit(f"main: {bad}")
    lam, lam1800, stop1800 = lams
    cands = st.candidates()
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    cn = st.config_names(cands)
    specs = ([(c, c, None) for c in cands] + [("PC1", "PC1", None)]
             + [(f"PCs-{c}", f"PCs-{c}", float(lam[c])) for c in cands]
             + [(f"PC0-{c}", f"PC0-{c}", 0.0) for c in cands] + [("PC-corr", "PC-corr", None)])
    if stop1800 is None:
        specs += ([(st.PC1L_NAME, st.PC1L_NAME, None)]
                  + [(f"{st.PCL_PREFIX}{c}", f"{st.PCL_PREFIX}{c}", float(lam1800[c])) for c in cands])
    t0 = time.time()
    scratch = Path(tempfile.mkdtemp(prefix="main-", dir=work))
    try:
        tab = label_tables(work, sids, cfg, scratch)
        F = run_stage(specs, ms, work, seed, jobs)
        names = {}
        for i, (key, *_) in enumerate(specs):
            save(scratch, f"F-{i}", F[key])
            names[key] = f"F-{i}"
        del F
        print(f"stage runs: {len(specs)} x {len(sids)} in {time.time() - t0:.0f} s", flush=True)
        desc_a = cands + cn["pccorr"]
        e13 = {}
        for tag in LABELS:
            fitted, null_names, forced = label_plan(names, tag, cn, stop1800)
            e13[tag] = e13_target(tag, tab[tag], fitted, desc_a, cfg, seed, jobs, cfg["e13"]["bootstrap"],
                                  cfg["e13"]["null_perms"], scratch, cands, null_names, forced)
            if forced:
                e13[tag]["pilot_stop_1800"] = stop1800
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
        e13["step"], e13["c"], e13["world"] = step, step_c(cfg, step), step_world(cfg, step)
        dump(out / "e13.json", e13)
        desc = describe(cands + cn["pccorr"], cands, ms, cfg, seed, work, jobs)
        dump(out / "describe.json", {"_note": "Descriptive (design 3.4): no verdict.", **desc})
        summ = {c: {t: e13[t]["configs"].get(c, {}).get("verdict", "undecidable") for t in LABELS} for c in cands}
        ctrl = cn["pc1"] + cn["pcs"] + cn["pc0"] + cn["pccorr"] + cn["pc1_1800"] + cn["pcl"]
        summ["_controls"] = {n: {t: e13[t]["configs"].get(n, {}).get("verdict") for t in LABELS} for n in ctrl}
        summ["_detector"] = {t: {k: e13[t].get(k) for k in ("auc_A_speed", "auc_A", "ceiling_kinds", "pc1_ok",
                                                            "null_all_73_ok", "nan", "fit_failed", "detector",
                                                            "pilot_stop_1800")}
                             for t in LABELS}
        summ["_step"] = {"step": step, "c": step_c(cfg, step), "world": step_world(cfg, step)}
        jumps = work / "speed_jumps.json"  # confound world design 3.3 (h): described only
        if not jumps.exists():  # code-reviewer round 2 L: every confound work directory has it
            raise SystemExit(f"{jumps} is missing (confound world design 1.2)")
        jd = json.loads(jumps.read_text(encoding="utf-8"))
        if jd.get("c") != step_c(cfg, step) or not jd.get("pairs"):  # Codex round 3: this step's record
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
    ap.add_argument("--step", required=True, help="shape world design 1.2: f100, f200, d100 or d200")
    ap.add_argument("--pilot-json", default=None, help="the main run and the smoke: the step's pilot.json")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--smoke", action="store_true")
    g.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    step_c(cfg, a.step)
    check_ceiling_file(cfg, Path(a.config), a.step)  # graded world design 3.0: a go step of this config only
    seed = int(Path(a.seed_file).read_text().strip())
    base_seed = int((Path(a.config).parent / "SEED").read_text().strip())
    work, out = Path(a.work), Path(a.results)
    if a.pilot:
        out.mkdir(parents=True, exist_ok=True)
        return pilot(cfg, seed, work, out, a.jobs, a.step)
    if not a.pilot_json:
        raise SystemExit("--pilot-json is required by the main run and the smoke (graded world design 1.2)")
    lams = main_lams(cfg, Path(a.pilot_json), base_seed, a.step)  # before the smoke changes the config
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = 200, 2
    out.mkdir(parents=True, exist_ok=True)
    return main_run(cfg, seed, work, out, a.jobs, a.step, lams)


if __name__ == "__main__":
    raise SystemExit(main())
