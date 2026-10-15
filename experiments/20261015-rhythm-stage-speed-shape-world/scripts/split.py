"""Cause split readings of a shape world step (L300), run after the main run on the same rows: (a) the base A_speed
with a non-linear transform for lr (lrbin), (b) the stage's window features with groups dropped, and the r-side
controls PCrl- / PCrv- (design 1.3, 3.3 (j)).

Design: .steering/20261015-rhythm-stage-speed-shape-world/design.md 1.4, 3.3 (j). Copied from
experiments/20261015-rhythm-stage-speed-cause-split/scripts/split.py (d282691d), changed: it imports this task's
checks and stage (no earlier instrument is imported, so the SHA-256 check of one is gone); the gate compares the
no-drop lr and hgb values with this step's own e13.json (the main run's, or the smoke's); the r-side controls of each
candidate (lambdas from pc_r.lam.<step>, checked against the step's pilot.json) are fitted with lr, hgb and lrbin on
the drops none / R2 and read (pcr_reading); git_state does not count results/.

Usage: split.py <config.json> <work dir> <out dir> --step <step> --seed <seed> --main-dir <results/<step>/main>
                [--jobs N] [--smoke] [--replay-sha <sha256>]
  --smoke  bootstrap split.smoke_bootstrap, P sets.smoke size (12); the gate reads --main-dir (the smoke's main run)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import checks as ck
import stage as st

EXP_DIR = Path(__file__).resolve().parents[1]
LABEL = "L300"
FS = ("full", "small")
MODELS = ("lr", "hgb", "lrbin")
DESC_MODELS = ("lrbin2",)
DROPS = ("none", "R2", "Rall", "A2")
READ_KEYS = ("remains", "vanishes", "undetermined", "unreadable")
PCR_READ_KEYS = ("works", "over", "fails", "unclear", "unreadable", "not_calibrated")
SMOKE_P = 12  # run.sh --smoke


# ---------------------------------------------------------------------------
# Checks of the inputs (design 1.4)
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def keep_columns(drop: list[str], fs: str) -> list[int]:
    """The indices of the stage block (the window's 20, and for full the differences to the two earlier windows, 20
    each, in that order: checks.feature_names) that stay when the quantities in drop are dropped."""
    unknown = sorted(set(drop) - set(st.FEAT_NAMES))
    if unknown:
        raise ValueError(f"unknown stage features {unknown}")
    keep = [i for i, n in enumerate(st.FEAT_NAMES) if n not in set(drop)]
    nf = len(st.FEAT_NAMES)
    return keep if fs == "small" else keep + [nf + i for i in keep] + [2 * nf + i for i in keep]


def gate(prev_l300: dict, got: dict, tol: float, names: list[str], attackers: list[str],
         kinds: tuple[str, ...] = ("hgb", "lr")) -> dict:
    """design 1.4 (the cause split's design 1.5): AUC(A_speed) of hgb and lr and, per name and attacker, the gain and
    both ends of its 95% interval of the split's fits against the step's e13.json (L300). got: {"auc_A_speed": {k: v},
    "configs": {name: {attacker: {"gain", "ci95"}}}}. Every expected value (kinds, names x attackers) must be in got and
    in e13.json, and nothing else in got."""
    diffs, missing = [], []
    want_keys = {(n, a) for n in names for a in attackers}
    got_keys = {(n, a) for n, attk in got["configs"].items() for a in attk}
    missing += [f"{n}/{a} (rebuilt)" for n, a in sorted(want_keys - got_keys)]
    missing += [f"{n}/{a} (unexpected)" for n, a in sorted(got_keys - want_keys)]
    missing += [f"auc_A_speed/{k} (rebuilt)" for k in kinds if k not in got["auc_A_speed"]]
    for k, v in got["auc_A_speed"].items():
        p = prev_l300.get("auc_A_speed", {}).get(k)
        if p is None:
            missing.append(f"auc_A_speed/{k}")
        else:
            diffs.append((abs(v - p), f"auc_A_speed/{k}"))
    for n, attk in got["configs"].items():
        for a, r in attk.items():
            p = prev_l300.get("configs", {}).get(n, {}).get("attackers", {}).get(a)
            if p is None:
                missing.append(f"{n}/{a}")
                continue
            diffs.append((abs(r["gain"] - p["gain"]), f"{n}/{a}/gain"))
            for i, end in enumerate(("lo", "hi")):
                diffs.append((abs(r["ci95"][i] - p["ci95"][i]), f"{n}/{a}/ci95_{end}"))
    nonfinite = [w for d, w in diffs if not np.isfinite(d)]
    over = sorted(((d, w) for d, w in diffs if np.isfinite(d) and d > tol), reverse=True)
    worst = max((d for d, _ in diffs if np.isfinite(d)), default=float("nan"))
    n_want = len(kinds) + 3 * len(want_keys)
    ok = not missing and not nonfinite and not over and len(diffs) == n_want and n_want > 0
    return {"ok": ok, "tol": tol, "n_compared": len(diffs), "n_expected": n_want, "max_abs_diff": worst,
            "missing": missing,
            "nonfinite": nonfinite, "over_tol": [[w, d] for d, w in over[:50]], "n_over_tol": len(over)}


# ---------------------------------------------------------------------------
# Readings (the cause split's design 3.1-3.3; design 3.3 (j))
# ---------------------------------------------------------------------------

def _max_or_nan(vals: list[float]) -> float:
    """The maximum, or NaN when any value is NaN (Python's max drops a NaN that is not first)."""
    vals = [float(v) for v in vals]
    return float("nan") if any(math.isnan(v) for v in vals) else max(vals)


def maxima(attk: dict) -> dict:
    """Over the two attackers (full, small) of one variant; NaN when either attacker's value is NaN."""
    return {"gain_max": _max_or_nan([r["gain"] for r in attk.values()]),
            "lower_max": _max_or_nan([r["ci95"][0] for r in attk.values()]),
            "upper_max": _max_or_nan([r["ci95"][1] for r in attk.values()]),
            "n_nan": sum(math.isnan(float(x)) for r in attk.values() for x in (r["gain"], *r["ci95"]))}


def reading(cand: dict, pcs: dict, pc0: dict, margin: float, pc_lower: float, pc_upper: float) -> str:
    """The cause split's design 3.2, 3.3 (the maxima of one variant). A NaN anywhere makes the comparison false:
    unreadable or undetermined, never remains or vanishes."""
    if pcs["n_nan"] or pc0["n_nan"]:
        return "unreadable"
    if not (pcs["lower_max"] > pc_lower and pcs["gain_max"] <= pc_upper and pc0["upper_max"] < margin):
        return "unreadable"
    if cand["n_nan"]:
        return "undetermined"
    if cand["lower_max"] > margin:
        return "remains"
    if cand["upper_max"] < margin:
        return "vanishes"
    return "undetermined"


def pcr_reading(ctl: dict | None, base: dict | None, margin: float, upper: float) -> str:
    """design 3.3 (j): an r-side control of one family and candidate in one variant. None (no lambda) ->
    not_calibrated; a NaN in either, or its lambda 0 baseline's upper bound max >= margin -> unreadable; then works
    (lower > margin, gain <= upper), over (lower > margin, gain > upper), fails (upper bound < margin), else unclear."""
    if ctl is None or base is None:
        return "not_calibrated"
    if ctl["n_nan"] or base["n_nan"] or not base["upper_max"] < margin:
        return "unreadable"
    if ctl["lower_max"] > margin:
        return "works" if ctl["gain_max"] <= upper else "over"
    if ctl["upper_max"] < margin:
        return "fails"
    return "unclear"


# ---------------------------------------------------------------------------
# Models (the cause split's design 1.3)
# ---------------------------------------------------------------------------

def make_lrbin(nb: int, nf: int, bin_stage: bool, n_bins: int):
    """lrbin: the nb base columns become the one-hot of n_bins quantile bins next to their values (median-imputed
    first); the nf stage columns are binned the same way only for lrbin2 (bin_stage). Then StandardScaler and
    LogisticRegression as checks.oof_predict's lr. The bin edges are fitted inside the pipeline, so on the training
    side of each fold only."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import FeatureUnion, Pipeline, make_pipeline
    from sklearn.preprocessing import FunctionTransformer, KBinsDiscretizer, StandardScaler

    def binner():
        return Pipeline([("imp", SimpleImputer(strategy="median")),
                         ("u", FeatureUnion([("bins", KBinsDiscretizer(n_bins=n_bins, encode="onehot-dense",
                                                                       strategy="quantile",
                                                                       quantile_method="averaged_inverted_cdf",
                                                                       subsample=None)),
                                             ("id", FunctionTransformer())]))])

    parts = [("base", binner(), list(range(nb)))]
    if nf:
        parts.append(("stage", binner() if bin_stage else SimpleImputer(strategy="median"),
                      list(range(nb, nb + nf))))
    return make_pipeline(ColumnTransformer(parts), StandardScaler(), LogisticRegression(max_iter=2000))


def oof_predict_bin(X: np.ndarray, y: np.ndarray, groups: np.ndarray, nb: int, bin_stage: bool, n_bins: int,
                    folds: int) -> np.ndarray:
    from sklearn.model_selection import GroupKFold
    from threadpoolctl import threadpool_limits

    pred = np.zeros(len(y))
    with threadpool_limits(1), warnings.catch_warnings():
        # KBinsDiscretizer warns when it removes bins of a repeated value or a constant column
        warnings.filterwarnings("ignore", category=UserWarning, module=r"sklearn\.preprocessing\._discretization")
        for tr, te in GroupKFold(n_splits=folds).split(X, y, groups):
            model = make_lrbin(nb, X.shape[1] - nb, bin_stage, n_bins)
            model.fit(X[tr], y[tr])
            pred[te] = model.predict_proba(X[te])[:, 1]
    return pred


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

SCR = Path()


def _init(scratch: str) -> None:
    global SCR
    SCR = Path(scratch)
    ck._init(scratch)


def build(cname: str | None, fs: str | None, drop: list[str]) -> tuple[np.ndarray, int]:
    """A_speed of L300 and, unless cname is None, the stage block of fs with the dropped columns left out."""
    B = np.asarray(ck._mm(f"{LABEL}-S"))
    if cname is None:
        return B, B.shape[1]
    X = ck.build_x(LABEL, "S", cname, fs)
    stage_block = X[:, B.shape[1]:]
    return np.hstack([B, stage_block[:, keep_columns(drop, fs)]]), B.shape[1]


def predict(model: str, X: np.ndarray, nb: int, y: np.ndarray, G: np.ndarray, seed: int, folds: int,
            n_bins: int) -> np.ndarray:
    if model in ("lr", "hgb"):
        return ck.oof_predict(X, y, G, model, seed, folds)
    if model in ("lrbin", "lrbin2"):
        return oof_predict_bin(X, y, G, nb, model == "lrbin2", n_bins, folds)
    raise ValueError(model)


def _base_job(args: tuple) -> tuple:
    """The base model of one kind: A_speed (lr, hgb) or the transformed A_speed (lrbin; lrbin2 shares it)."""
    model, y, seed, folds, n_bins = args
    G = np.asarray(ck._mm(f"{LABEL}-G"))
    if ck.one_class_fold(y, G, folds):
        return model, None
    X, nb = build(None, None, [])
    p = predict(model, X, nb, y, G, seed, folds, n_bins)
    np.save(SCR / f"base-{model}.npy", p)
    return model, float(ck.weighted_auc(p, y, np.ones(len(y))))


def _fit_job(args: tuple) -> tuple:
    """One B of one variant: its AUC, the gain over the variant's base and the bootstrap interval of the gain (the
    multipliers of mults.npy, as checks.e13_target)."""
    key, model, cname, fs, drop, y, seed, folds, n_bins = args
    G = np.asarray(ck._mm(f"{LABEL}-G"))
    if ck.one_class_fold(y, G, folds):
        return key, None
    X, nb = build(cname, fs, drop)
    p = predict(model, X, nb, y, G, seed, folds, n_bins)
    base = np.load(SCR / f"base-{'lrbin' if model == 'lrbin2' else model}.npy")
    mults = np.load(SCR / "mults.npy")
    prep_b, prep_a = ck.auc_prep(p, y), ck.auc_prep(base, y)
    ones = np.ones(len(y))
    auc_b, auc_a = ck.auc_w(prep_b, ones), ck.auc_w(prep_a, ones)
    draws = np.array([ck.auc_w(prep_b, m[G]) - ck.auc_w(prep_a, m[G]) for m in mults])
    return key, {"auc_B": auc_b, "gain": auc_b - auc_a,
                 "ci95": [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]}


def run_pool(fn, jobs_list: list, jobs: int, scratch: Path) -> dict:
    with ProcessPoolExecutor(max_workers=jobs, initializer=_init, initargs=(str(scratch),)) as ex:
        return dict(ex.map(fn, jobs_list, chunksize=1))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def multipliers(seed: int, n_sess: int, nboot: int) -> np.ndarray:
    """The bootstrap multipliers of checks.e13_target for L300 (LABEL_ID 0), drawn the same way; shared by every
    variant (the cause split's design 1.6)."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, 313, ck.LABEL_ID[LABEL]]))
    return np.array([np.bincount(rng.integers(0, n_sess, size=n_sess), minlength=n_sess).astype(float)
                     for _ in range(nboot)])


def package_problems(cfg: dict) -> list[str]:
    """The Python and package versions of the copied instruments (config.json split.versions)."""
    want = cfg["split"]["versions"]
    have = {"python": platform.python_version(),
            **{m: __import__(m).__version__ for m in ("numpy", "scipy", "sklearn", "threadpoolctl")}}
    return [f"{k} is {have[k]}, not {v}" for k, v in want.items() if have.get(k) != v]


def variants() -> list[tuple[str, str]]:
    """(model, drop) of the 72 names; lrbin2 without drops (descriptive)."""
    return [(m, d) for m in MODELS for d in DROPS] + [(m, "none") for m in DESC_MODELS]


def pcr_variants(cfg: dict) -> list[tuple[str, str]]:
    """design 1.4: (model, drop) of the r-side controls."""
    drops = list(cfg["split"]["pcr_drops"])
    # cross-review 1: with Rall (or A2) a control's remaining features are those of its lambda 0 baseline (its a does
    # not depend on lambda), so it could never work there
    if drops != ["none", "R2"]:
        raise SystemExit(f"split.pcr_drops {drops} must be none and R2 (design 1.4)")
    return [(m, d) for m in MODELS for d in drops]


def pcr_specs(lam_r: dict) -> list[tuple[str, str, float]]:
    """design 1.3, 1.4: (key, name, lambda) of the r-side controls whose family and candidate have a lambda; each with
    its lambda 0 baseline."""
    out = []
    for fam, table in st.pcr_names(st.candidates()).items():
        for c, (ctl, base) in table.items():
            lam = lam_r[fam][c]
            if lam is not None:
                out += [(ctl, ctl, float(lam)), (base, base, 0.0)]
    return out


def git_state() -> dict:
    """design 1.4: the commit and whether the experiment directory differs from it, results/ left out."""
    def run(*a):
        return subprocess.run(["git", *a], cwd=EXP_DIR, capture_output=True, text=True, check=False)
    r = run("status", "--porcelain", "--", ".", ":(exclude)results")
    return {"commit": run("rev-parse", "HEAD").stdout.strip(),
            "dirty": bool(r.stdout.strip()) if r.returncode == 0 else None}


def main_split(cfg: dict, work: Path, out: Path, step: str, seed: int, jobs: int, smoke: bool,
               replay_sha: str | None, main_dir: Path) -> int:
    t0 = time.time()
    bad = package_problems(cfg)
    if bad:
        raise SystemExit(f"design 1.1: {bad}")
    bad = ck.world_problems(work, cfg, step)
    if bad:
        raise SystemExit(f"design 1.4: {bad}")
    base_seed = int((EXP_DIR / "SEED").read_text().strip())
    pilot_json = EXP_DIR / "results" / step / "pilot" / "pilot.json"
    lam = ck.main_lams(cfg, pilot_json, base_seed, step)[0]
    lam_r = ck.main_lams_r(cfg, pilot_json, base_seed, step)
    sc = cfg["split"]
    cands = st.candidates()
    names = cands + [f"PCs-{c}" for c in cands] + [f"PC0-{c}" for c in cands]
    specs = ([(c, c, None) for c in cands] + [(f"PCs-{c}", f"PCs-{c}", float(lam[c])) for c in cands]
             + [(f"PC0-{c}", f"PC0-{c}", 0.0) for c in cands])
    rspecs = pcr_specs(lam_r)
    rnames = [k for k, _, _ in rspecs]
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    n_p = SMOKE_P if smoke else cfg["sets"]["P"]["n"]
    if len(sids) != n_p:
        raise SystemExit(f"{len(sids)} P sessions in {work}, design 1.4 wants {n_p}")
    folds = cfg["e13"]["folds"]
    n_bins = sc["bins"]
    nboot = sc["smoke_bootstrap" if smoke else "bootstrap"]
    drops = {"none": [], **sc["drops"]}
    e13_path = main_dir / "e13.json"
    if not e13_path.exists():
        raise SystemExit(f"{e13_path} is missing (the gate compares with the step's main run, design 1.4)")
    scratch = Path(tempfile.mkdtemp(prefix="split-", dir=work))
    try:
        tab = ck.label_tables(work, sids, cfg, scratch)[LABEL]
        F = ck.run_stage(specs + rspecs, ms, work, seed, jobs)
        fname = {}
        for i, (key, *_) in enumerate(specs + rspecs):
            ck.save(scratch, f"F-{i}", F[key])
            fname[key] = f"F-{i}"
        del F
        print(f"stage runs: {len(specs) + len(rspecs)} x {len(sids)} in {time.time() - t0:.0f} s", flush=True)
        Y, G = tab["Y"], tab["G"]
        n_sess = int(G.max()) + 1
        np.save(scratch / "mults.npy", multipliers(seed, n_sess, nboot))

        def bases(models: tuple[str, ...]) -> dict:
            got = run_pool(_base_job, [(m, Y, seed, folds, n_bins) for m in models], jobs, scratch)
            if any(v is None for v in got.values()):
                raise SystemExit(f"a fold's training side holds one class: {got}")
            return got

        # before the gate only what the gate compares (lr, hgb); lrbin after it
        auc_base = bases(("lr", "hgb"))
        print(f"bases {auc_base} at {time.time() - t0:.0f} s", flush=True)

        def fit(vs: list[tuple[str, str]], ns: list[str]) -> dict:
            js = [((m, d, n, fs), m, fname[n], fs, drops[d], Y, seed, folds, n_bins)
                  for m, d in vs for n in ns for fs in FS]
            got = run_pool(_fit_job, js, jobs, scratch)
            if any(v is None for v in got.values()):
                raise SystemExit("a fold's training side holds one class")
            return got

        res: dict = {}
        first = [("lr", "none"), ("hgb", "none")]
        res.update(fit(first, names))
        print(f"lr and hgb (no drop) at {time.time() - t0:.0f} s", flush=True)
        prev_e13 = json.loads(e13_path.read_text(encoding="utf-8"))
        got = {"auc_A_speed": {k: auc_base[k] for k in ("hgb", "lr")},
               "configs": {n: {f"{fs}/{m}": res[(m, "none", n, fs)] for m, _ in first for fs in FS} for n in names}}
        gate_doc = gate(prev_e13[LABEL], got, sc["gate_tol"], names, [f"{fs}/{m}" for m, _ in first for fs in FS])
        gate_doc["e13"] = str(e13_path)
        gate_doc["e13_sha256"] = sha256(e13_path)
        ck.dump(out / "reproduce.json", gate_doc)
        if not gate_doc["ok"]:
            print(f"=== GATE FAILED (design 1.4): {gate_doc['n_over_tol']} over tol, missing "
                  f"{len(gate_doc['missing'])}; the readings are not run ===", file=sys.stderr, flush=True)
            return 3
        print(f"gate ok: {gate_doc['n_compared']} values, max |diff| {gate_doc['max_abs_diff']:.3g}", flush=True)
        auc_base.update(bases(("lrbin",)))
        res.update(fit([v for v in variants() if v not in first], names))
        rv = pcr_variants(cfg)
        if rnames:
            res.update(fit(rv, rnames))
        print(f"fits done at {time.time() - t0:.0f} s", flush=True)
        doc = {"_note": "Exploratory (design 3.3 (j)): readings, not verdicts; the step's verdicts are in "
                        "results/<step>/main/summary.json.",
               "step": step, "world": ck.step_world(cfg, step), "c": ck.step_c(cfg, step), "seed": seed,
               "smoke": smoke, "n_sessions": n_sess, "n_windows": int(len(Y)),
               "auc_base": {**auc_base, "lrbin2": auc_base["lrbin"]}, "variants": {}, "readings": {},
               "pcr_lam": lam_r, "pcr_variants": {}, "pcr_readings": {}}
        rd = sc["read"]
        for m, d in variants():
            vk = f"{m}|{d}"
            per = {}
            for n in names:
                attk = {f"{fs}/{m}": res[(m, d, n, fs)] for fs in FS}
                per[n] = {"attackers": attk, **maxima(attk)}
            doc["variants"][vk] = per
            doc["readings"][vk] = {c: reading(per[c], per[f"PCs-{c}"], per[f"PC0-{c}"], rd["margin"],
                                              rd["pc_lower"], rd["pc_upper"]) for c in cands}
        for m, d in rv:
            vk = f"{m}|{d}"
            per = {}
            for n in rnames:
                attk = {f"{fs}/{m}": res[(m, d, n, fs)] for fs in FS}
                per[n] = {"attackers": attk, **maxima(attk)}
            doc["pcr_variants"][vk] = per
            doc["pcr_readings"][vk] = {
                fam: {c: pcr_reading(per.get(ctl), per.get(base), rd["margin"], rd["pcr_upper"])
                      for c, (ctl, base) in table.items()}
                for fam, table in st.pcr_names(cands).items()}
        # cross-review 1 (code-reviewer): the main run's ceiling (a model at the ceiling may leave a control short)
        doc["main_ceiling_kinds_L300"] = list(prev_e13[LABEL]["ceiling_kinds"])  # required (cross-review 2)
        summ = main_dir / "summary.json"
        if summ.exists():
            s = json.loads(summ.read_text(encoding="utf-8"))
            doc["verdicts_L300"] = {c: s[c][LABEL] for c in cands}
        doc["counts"] = {vk: {k: sum(v == k for v in r.values()) for k in READ_KEYS}
                         for vk, r in doc["readings"].items()}
        doc["pcr_counts"] = {vk: {fam: {k: sum(v == k for v in r.values()) for k in PCR_READ_KEYS}
                                  for fam, r in fams.items()}
                             for vk, fams in doc["pcr_readings"].items()}
        doc["wall_s"] = time.time() - t0
        ck.dump(out / "split.json", doc)
        prov_pkgs = {}
        for mod in ("numpy", "scipy", "sklearn", "threadpoolctl"):
            prov_pkgs[mod] = __import__(mod).__version__
        ck.dump(out / "provenance.json", {
            "seed": seed, "step": step, "smoke": smoke, "jobs": jobs, "git": git_state(),
            "config_sha256": sha256(EXP_DIR / "config.json"), "main_dir": str(main_dir),
            "gse_replay_sha256": replay_sha, "python": platform.python_version(), "packages": prov_pkgs,
            "wall_s": time.time() - t0})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("work")
    ap.add_argument("out")
    ap.add_argument("--step", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--main-dir", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--replay-sha")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    os.environ["OMP_NUM_THREADS"] = "1"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    return main_split(cfg, Path(a.work), out, a.step, a.seed, a.jobs, a.smoke, a.replay_sha, Path(a.main_dir))


if __name__ == "__main__":
    raise SystemExit(main())
