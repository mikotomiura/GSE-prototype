"""Pilot 0 of the rhythm stage desk check: the ceiling of the baseline models. Graded world
(.steering/20261014-rhythm-stage-graded-world/design.md 3.0): run after the freeze on the three steps of
config.json ceiling.steps; each step is go, ceiling (both classifiers' L300 AUC(A_speed) >= ceiling.main_auc) or
unmeasured (a failed fit or a NaN in L300). The positions of the steps are not changed after this (decisions 16).
Round 1 and 2's rule (choose one world of ceiling.prefer by usable_max) is removed.

For each step, label (L300, L60, L1800) and classifier (hgb, lr): AUC(A) and AUC(A_speed), out of fold on the
P sessions (session-grouped 5-fold, as EH1). No stage candidate and no positive control is computed: the pilot
looks at the baseline models only (design 3.0).

The statistics (auc_prep, auc_w, weighted_auc, oof_predict) are copied unchanged from
experiments/20261010-portrait-eh1-round5/scripts/checks.py.

Usage: ceiling.py <config.json> <seed file> <out dir> --work t025=<work dir> --work t050=<work dir> ... [--jobs N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import baseline as bl

KINDS = ("hgb", "lr")
MODELS = ("A", "A_speed")


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


# ---------------------------------------------------------------------------
# Pilot 0
# ---------------------------------------------------------------------------

def _fit_job(args: tuple) -> tuple:
    """One OOF AUC. A fold whose training side holds one class cannot be fitted: that is checked before the fit
    and reported as None (as EH1). Any other error (a feature table that does not line up, a bad fold count) is an
    error of the instruments and stops the run instead of being read as a failed fit (/cross-review)."""
    from sklearn.model_selection import GroupKFold

    key, X, y, groups, kind, seed, folds = args
    os.environ["OMP_NUM_THREADS"] = "1"
    if any(len(np.unique(y[tr])) < 2 for tr, _ in GroupKFold(n_splits=folds).split(X, y, groups)):
        return key, None
    return key, weighted_auc(oof_predict(X, y, groups, kind, seed, folds), y, np.ones(len(y)))


def measure(tabs: dict, seed: int, folds: int, jobs: int) -> dict:
    """tabs: world -> baseline.tables(). Returns world -> label -> kind -> {auc_A, auc_A_speed, speed_minus_A}
    plus the row counts of each label."""
    jobs_in = []
    for world, tab in tabs.items():
        for label in bl.LABELS:
            t = tab[label]
            for kind in KINDS:
                for model, X in zip(MODELS, (t["XA"], t["XS"])):
                    jobs_in.append(((world, label, kind, model), X, t["Y"], t["G"], kind, seed, folds))
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        got = dict(ex.map(_fit_job, jobs_in))
    res: dict = {}
    for world, tab in tabs.items():
        res[world] = {}
        for label in bl.LABELS:
            t = tab[label]
            r = {"n_rows": int(len(t["Y"])), "n_pos": int(t["Y"].sum()), "n_sessions": int(len(np.unique(t["G"]))),
                 "n_features_A": int(t["XA"].shape[1]), "n_features_A_speed": int(t["XS"].shape[1])}
            for kind in KINDS:
                a, s = got[(world, label, kind, "A")], got[(world, label, kind, "A_speed")]
                ok = a is not None and s is not None
                r[kind] = {"auc_A": a, "auc_A_speed": s, "speed_minus_A": (s - a) if ok else None,
                           "fit_failed": not ok}
            res[world][label] = r
    return res


def cfg_fingerprint(cfg: dict) -> str:
    """graded world design 1.2 (cross-review round 2): the SHA-256 of config.json without the keys that start with _
    (comments) and without pc_stall.lam and pc_stall.lam_1800 (written after the pilots). pilot 0 and each pilot 1
    record it; the later steps refuse a record made under another config."""
    c = {k: v for k, v in cfg.items() if not k.startswith("_")}
    c["pc_stall"] = {k: v for k, v in c["pc_stall"].items() if k not in ("lam", "lam_1800")}
    return hashlib.sha256(json.dumps(c, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def step_status(res_step: dict, main_auc: float) -> dict:
    """graded world design 3.0: ceiling when both classifiers' L300 AUC(A_speed) are >= main_auc (equality is at the
    ceiling, as design 3.2); unmeasured when a fit failed or a value is NaN (not read as a ceiling); else go."""
    vals = [res_step["L300"][k]["auc_A_speed"] for k in KINDS]
    if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in vals):
        return {"L300_auc_A_speed": vals, "status": "unmeasured"}
    return {"L300_auc_A_speed": vals, "status": "ceiling" if all(v >= main_auc for v in vals) else "go"}


def choose_steps(res: dict, cfg: dict) -> dict:
    c = cfg["ceiling"]
    return {s: {"t": c["steps"][s], **step_status(res[s], c["main_auc"])} for s in c["steps"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("out")
    ap.add_argument("--work", action="append", required=True, help="<world>=<work dir>")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    seed = int(Path(a.seed_file).read_text().strip())
    works = dict(w.split("=", 1) for w in a.work)
    steps = cfg["ceiling"]["steps"]
    if sorted(works) != sorted(steps):
        raise SystemExit(f"--work must name exactly the steps {sorted(steps)}")
    tabs = {}
    n_p = {}
    for world, wd in works.items():
        w = json.loads((Path(wd) / "world.json").read_text(encoding="utf-8"))
        if w != {"world": "graded", "t": float(steps[world])}:
            raise SystemExit(f"{wd}/world.json is {w}, not the graded world at t = {steps[world]} ({world})")
        sids = bl.p_sids(Path(wd))
        if len(sids) != cfg["ceiling"]["P"]:
            raise SystemExit(f"{world}: {len(sids)} P sessions, expected {cfg['ceiling']['P']}")
        n_p[world] = len(sids)
        tabs[world] = bl.tables(Path(wd), sids, cfg)
    res = measure(tabs, seed, cfg["e13"]["folds"], a.jobs)
    out = {"design": ".steering/20261014-rhythm-stage-graded-world/design.md 3.0", "seed": seed, "P": n_p,
           "folds": cfg["e13"]["folds"], "main_auc": cfg["ceiling"]["main_auc"],
           "config_fingerprint": cfg_fingerprint(cfg), "results": res,
           "steps": choose_steps(res, cfg)}
    Path(a.out).mkdir(parents=True, exist_ok=True)
    with open(Path(a.out) / "ceiling.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    for world in works:
        for label in bl.LABELS:
            for kind in KINDS:
                r = res[world][label][kind]
                print(f"{world} {label} {kind}: AUC(A) {r['auc_A']} AUC(A_speed) {r['auc_A_speed']}")
    for s, v in out["steps"].items():
        print(f"step {s} (t = {v['t']}): {v['status']} (L300 AUC(A_speed) hgb / lr {v['L300_auc_A_speed']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
