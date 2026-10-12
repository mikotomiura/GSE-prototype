"""Pilot 0 of the rhythm stage desk check (design 3.0): the ceiling of the baseline models, before the freeze.

For each world, label (L300, L60, L1800) and classifier (hgb, lr): AUC(A) and AUC(A_speed), out of fold on the
P sessions (session-grouped 5-fold, as EH1). No stage candidate and no positive control is computed: the pilot
looks at the baseline models only (design 3.0). Then the world is chosen by the frozen rule: usable when the
smaller of the two classifiers' L300 AUC(A_speed) is <= ceiling.usable_max; the first usable world of
ceiling.prefer is chosen; when none is usable the main run does not start (back to the researcher).

The statistics (auc_prep, auc_w, weighted_auc, oof_predict) are copied unchanged from
experiments/20261010-portrait-eh1-round5/scripts/checks.py.

Usage: ceiling.py <config.json> <seed file> <out dir> --work v2=<work dir> --work v3=<work dir> [--jobs N]
"""

from __future__ import annotations

import argparse
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
    """One OOF AUC; a fold whose training side holds one class cannot be fitted (reported as None, as EH1)."""
    key, X, y, groups, kind, seed, folds = args
    os.environ["OMP_NUM_THREADS"] = "1"
    try:
        return key, weighted_auc(oof_predict(X, y, groups, kind, seed, folds), y, np.ones(len(y)))
    except ValueError:
        return key, None


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


def usable(res_world: dict, usable_max: float) -> dict:
    """design 3.0: the smaller of the two classifiers' L300 AUC(A_speed) <= usable_max (equality is usable).
    A failed fit or a NaN makes the world unusable (no value to judge on)."""
    vals = [res_world["L300"][k]["auc_A_speed"] for k in KINDS]
    if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in vals):
        return {"min_L300_auc_A_speed": None, "usable": False, "reason": "fit_failed_or_nan"}
    m = min(vals)
    return {"min_L300_auc_A_speed": m, "usable": bool(m <= usable_max)}


def choose(res: dict, cfg: dict) -> dict:
    c = cfg["ceiling"]
    per = {w: usable(res[w], c["usable_max"]) for w in c["prefer"]}
    chosen = next((w for w in c["prefer"] if per[w]["usable"]), None)
    return {"usable_max": c["usable_max"], "prefer": c["prefer"], "per_world": per, "chosen": chosen,
            "back_to_researcher": chosen is None}


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
    if sorted(works) != sorted(cfg["ceiling"]["prefer"]):
        raise SystemExit(f"--work must name exactly the worlds {cfg['ceiling']['prefer']}")
    tabs = {}
    n_p = {}
    for world, wd in works.items():
        sids = bl.p_sids(Path(wd))
        if len(sids) != cfg["ceiling"]["P"]:
            raise SystemExit(f"{world}: {len(sids)} P sessions, expected {cfg['ceiling']['P']}")
        n_p[world] = len(sids)
        tabs[world] = bl.tables(Path(wd), sids, cfg)
    res = measure(tabs, seed, cfg["e13"]["folds"], a.jobs)
    out = {"design": ".steering/20261012-rhythm-stage-desk-check/design.md 3.0", "seed": seed, "P": n_p,
           "folds": cfg["e13"]["folds"], "results": res, "choice": choose(res, cfg)}
    Path(a.out).mkdir(parents=True, exist_ok=True)
    with open(Path(a.out) / "ceiling.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    for world in works:
        for label in bl.LABELS:
            for kind in KINDS:
                r = res[world][label][kind]
                print(f"{world} {label} {kind}: AUC(A) {r['auc_A']} AUC(A_speed) {r['auc_A_speed']}")
    print(f"choice: {out['choice']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
