"""Cause split of the red res=sub candidates of the confound world (L300): (a) the base A_speed with a non-linear
transform for lr (lrbin), (b) the stage's window features with groups dropped.

Design: .steering/20261015-rhythm-stage-speed-cause-split/design.md. The rows, the stage's window features, the
fits of lr and hgb, the AUC and the bootstrap are those of the confound world's instrument
(experiments/20261014-rhythm-stage-speed-confound-world/scripts, imported, not copied; its files are checked against
the SHA-256 in config.json before anything runs, design 1.1). New here: the lrbin models (design 1.3), the dropped
columns (1.4), the gate against the confound world's e13.json (1.5) and the readings (3.1-3.3).

Usage: split.py <config.json> <work dir> <out dir> --step <step> --seed <seed> [--jobs N] [--smoke]
                [--replay-sha <sha256>]
       split.py <config.json> --check-prev   (only the SHA-256 check of the confound world's instrument)
  --smoke  bootstrap smoke_bootstrap and no gate (the smoke has other sessions than the main run, design 3.6)
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

EXP_DIR = Path(__file__).resolve().parents[1]
PREV_DIR = (EXP_DIR.parent / "20261014-rhythm-stage-speed-confound-world").resolve()
sys.path.insert(0, str(PREV_DIR / "scripts"))

import checks as ck  # noqa: E402
import stage as st  # noqa: E402

LABEL = "L300"
FS = ("full", "small")
MODELS = ("lr", "hgb", "lrbin")
DESC_MODELS = ("lrbin2",)
DROPS = ("none", "R2", "Rall", "A2")
READ_KEYS = ("remains", "vanishes", "undetermined", "unreadable")


# ---------------------------------------------------------------------------
# Checks of the inputs (design 1.1, 1.5)
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prev_problems(cfg: dict, prev_dir: Path = PREV_DIR) -> list[str]:
    """design 1.1: the confound world's instrument is the one whose SHA-256 config.json holds (every file listed, and
    no other *.py in its scripts/)."""
    want = cfg["prev"]["sha256"]
    bad = []
    if (EXP_DIR / cfg["prev"]["dir"]).resolve() != PREV_DIR:
        bad.append(f"config.json prev.dir {cfg['prev']['dir']} is not {PREV_DIR}")
    for rel, h in want.items():
        p = prev_dir / rel
        if not p.is_file():
            bad.append(f"{p} is missing")
        elif sha256(p) != h:
            bad.append(f"{p} has SHA-256 {sha256(p)}, not {h}")
    listed = {r for r in want if r.startswith("scripts/") and r.endswith(".py")}
    have = {f"scripts/{p.name}" for p in (prev_dir / "scripts").glob("*.py")}
    if have != listed:
        bad.append(f"the scripts of {prev_dir} are {sorted(have)}, config.json lists {sorted(listed)}")
    return bad


def keep_columns(drop: list[str], fs: str) -> list[int]:
    """design 1.4: the indices of the stage block (the window's 20, and for full the differences to the two earlier
    windows, 20 each, in that order: checks.feature_names) that stay when the quantities in drop are dropped."""
    unknown = sorted(set(drop) - set(st.FEAT_NAMES))
    if unknown:
        raise ValueError(f"unknown stage features {unknown}")
    keep = [i for i, n in enumerate(st.FEAT_NAMES) if n not in set(drop)]
    nf = len(st.FEAT_NAMES)
    return keep if fs == "small" else keep + [nf + i for i in keep] + [2 * nf + i for i in keep]


def gate(prev_l300: dict, got: dict, tol: float) -> dict:
    """design 1.5: AUC(A_speed) of hgb and lr and, per name and attacker, the gain and both ends of its 95% interval
    of the rebuilt rows against the confound world's e13.json (L300). got: {"auc_A_speed": {k: v}, "configs":
    {name: {attacker: {"gain", "ci95"}}}}."""
    diffs, missing = [], []
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
    ok = not missing and not nonfinite and not over and len(diffs) > 0
    return {"ok": ok, "tol": tol, "n_compared": len(diffs), "max_abs_diff": worst, "missing": missing,
            "nonfinite": nonfinite, "over_tol": [[w, d] for d, w in over[:50]], "n_over_tol": len(over)}


# ---------------------------------------------------------------------------
# Readings (design 3.1-3.3)
# ---------------------------------------------------------------------------

def maxima(attk: dict) -> dict:
    """design 3.1: over the two attackers (full, small) of one variant."""
    return {"gain_max": max(r["gain"] for r in attk.values()),
            "lower_max": max(r["ci95"][0] for r in attk.values()),
            "upper_max": max(r["ci95"][1] for r in attk.values())}


def reading(cand: dict, pcs: dict, pc0: dict, margin: float, pc_lower: float) -> str:
    """design 3.2, 3.3 (the maxima of one variant). A NaN anywhere makes the comparison false: unreadable or
    undetermined, never remains or vanishes."""
    if not (pcs["lower_max"] > pc_lower and pc0["upper_max"] < margin):
        return "unreadable"
    if cand["lower_max"] > margin:
        return "remains"
    if cand["upper_max"] < margin:
        return "vanishes"
    return "undetermined"


# ---------------------------------------------------------------------------
# Models (design 1.3)
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
        # KBinsDiscretizer warns when it removes bins of a repeated value or a constant column (design 3.6)
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

def variants(cfg: dict) -> list[tuple[str, str]]:
    """design 1.3, 1.4: (model, drop); lrbin2 without drops (descriptive)."""
    return [(m, d) for m in MODELS for d in DROPS] + [(m, "none") for m in DESC_MODELS]


def git_state() -> dict:
    def run(*a):
        return subprocess.run(["git", *a], cwd=EXP_DIR, capture_output=True, text=True, check=False).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain", "--", "."))}


def main_split(cfg: dict, work: Path, out: Path, step: str, seed: int, jobs: int, smoke: bool,
               replay_sha: str | None) -> int:
    t0 = time.time()
    bad = prev_problems(cfg)
    if bad:
        raise SystemExit(f"design 1.1: {bad}")
    prev_cfg = json.loads((PREV_DIR / "config.json").read_text(encoding="utf-8"))
    if step not in cfg["steps"]:
        raise SystemExit(f"step {step} is not one of {cfg['steps']}")
    bad = ck.world_problems(work, prev_cfg, step)
    if bad:
        raise SystemExit(f"design 1.1: {bad}")
    lam = prev_cfg["pc_stall"]["lam"][step]
    cands = st.candidates()
    names = cands + [f"PCs-{c}" for c in cands] + [f"PC0-{c}" for c in cands]
    specs = ([(c, c, None) for c in cands] + [(f"PCs-{c}", f"PCs-{c}", float(lam[c])) for c in cands]
             + [(f"PC0-{c}", f"PC0-{c}", 0.0) for c in cands])
    ms = st.manifest_p(work)
    sids = [m["sid"] for m in ms]
    n_p = cfg["sets"]["smoke_P" if smoke else "P"]
    if len(sids) != n_p:
        raise SystemExit(f"{len(sids)} P sessions in {work}, design 1.1 wants {n_p}")
    folds = prev_cfg["e13"]["folds"]
    n_bins = cfg["bins"]
    nboot = cfg["smoke_bootstrap" if smoke else "bootstrap"]
    drops = {"none": [], **cfg["drops"]}
    scratch = Path(tempfile.mkdtemp(prefix="split-", dir=work))
    try:
        tab = ck.label_tables(work, sids, prev_cfg, scratch)[LABEL]
        F = ck.run_stage(specs, ms, work, seed, jobs)
        fname = {}
        for i, (key, *_) in enumerate(specs):
            ck.save(scratch, f"F-{i}", F[key])
            fname[key] = f"F-{i}"
        del F
        print(f"stage runs: {len(specs)} x {len(sids)} in {time.time() - t0:.0f} s", flush=True)
        Y, G = tab["Y"], tab["G"]
        n_sess = int(G.max()) + 1
        # the multipliers of checks.e13_target (L300: LABEL_ID 0), drawn the same way, shared by every variant
        rng = np.random.default_rng(np.random.SeedSequence([seed, 313, ck.LABEL_ID[LABEL]]))
        mults = np.array([np.bincount(rng.integers(0, n_sess, size=n_sess), minlength=n_sess).astype(float)
                          for _ in range(nboot)])
        np.save(scratch / "mults.npy", mults)
        auc_base = run_pool(_base_job, [(m, Y, seed, folds, n_bins) for m in MODELS], jobs, scratch)
        if any(v is None for v in auc_base.values()):
            raise SystemExit(f"a fold's training side holds one class: {auc_base}")
        print(f"bases {auc_base} at {time.time() - t0:.0f} s", flush=True)

        def fit(vs: list[tuple[str, str]]) -> dict:
            js = [((m, d, n, fs), m, fname[n], fs, drops[d], Y, seed, folds, n_bins)
                  for m, d in vs for n in names for fs in FS]
            got = run_pool(_fit_job, js, jobs, scratch)
            if any(v is None for v in got.values()):
                raise SystemExit("a fold's training side holds one class")
            return got

        res: dict = {}
        first = [("lr", "none"), ("hgb", "none")]
        res.update(fit(first))
        print(f"lr and hgb (no drop) at {time.time() - t0:.0f} s", flush=True)
        gate_doc: dict = {"skipped": "smoke"} if smoke else {}
        if not smoke:
            prev_e13 = json.loads((PREV_DIR / "results" / step / "main" / "e13.json").read_text(encoding="utf-8"))
            got = {"auc_A_speed": {k: auc_base[k] for k in ("hgb", "lr")},
                   "configs": {n: {f"{fs}/{m}": res[(m, "none", n, fs)] for m, _ in first for fs in FS}
                               for n in names}}
            gate_doc = gate(prev_e13[LABEL], got, cfg["gate_tol"])
            ck.dump(out / "reproduce.json", gate_doc)
            if not gate_doc["ok"]:
                print(f"=== GATE FAILED (design 1.5): {gate_doc['n_over_tol']} over tol, missing "
                      f"{len(gate_doc['missing'])}; (a) and (b) not run ===", file=sys.stderr, flush=True)
                return 3
            print(f"gate ok: {gate_doc['n_compared']} values, max |diff| {gate_doc['max_abs_diff']:.3g}", flush=True)
        rest = [v for v in variants(cfg) if v not in first]
        res.update(fit(rest))
        doc = {"_note": "Exploratory (design 0): readings, not verdicts; the confound world's verdicts stand.",
               "step": step, "seed": seed, "smoke": smoke, "n_sessions": n_sess, "n_windows": int(len(Y)),
               "auc_base": {**auc_base, "lrbin2": auc_base["lrbin"]}, "variants": {}, "readings": {}}
        rd = cfg["read"]
        for m, d in variants(cfg):
            vk = f"{m}|{d}"
            per = {}
            for n in names:
                attk = {f"{fs}/{m}": res[(m, d, n, fs)] for fs in FS}
                per[n] = {"attackers": attk, **maxima(attk)}
            doc["variants"][vk] = per
            doc["readings"][vk] = {c: reading(per[c], per[f"PCs-{c}"], per[f"PC0-{c}"], rd["margin"],
                                              rd["pc_lower"]) for c in cands}
        prev_summ = PREV_DIR / "results" / step / "main" / "summary.json"
        if prev_summ.exists():
            s = json.loads(prev_summ.read_text(encoding="utf-8"))
            doc["confound_world_verdicts_L300"] = {c: s[c][LABEL] for c in cands}
        doc["counts"] = {vk: {k: sum(v == k for v in r.values()) for k in READ_KEYS}
                         for vk, r in doc["readings"].items()}
        doc["wall_s"] = time.time() - t0
        ck.dump(out / "split.json", doc)
        prov_pkgs = {}
        for mod in ("numpy", "scipy", "sklearn", "threadpoolctl"):
            prov_pkgs[mod] = __import__(mod).__version__
        ck.dump(out / "provenance.json", {
            "seed": seed, "step": step, "smoke": smoke, "jobs": jobs, "git": git_state(),
            "config_sha256": sha256(EXP_DIR / "config.json"), "prev_dir": str(PREV_DIR),
            "prev_sha256_checked": cfg["prev"]["sha256"], "gse_replay_sha256": replay_sha,
            "python": platform.python_version(), "packages": prov_pkgs, "wall_s": time.time() - t0})
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("work", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--step")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--replay-sha")
    ap.add_argument("--check-prev", action="store_true")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.check_prev:
        bad = prev_problems(cfg)
        if bad:
            print("\n".join(bad), file=sys.stderr)
            return 2
        print(f"prev ok: {len(cfg['prev']['sha256'])} files")
        return 0
    if not (a.work and a.out and a.step and a.seed is not None):
        ap.error("work, out, --step and --seed are required")
    os.environ["OMP_NUM_THREADS"] = "1"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    return main_split(cfg, Path(a.work), out, a.step, a.seed, a.jobs, a.smoke, a.replay_sha)


if __name__ == "__main__":
    raise SystemExit(main())
