"""EH1 round 2 checks of the portrait: E1-3 (L300 and L60), E1-6, path sensitivity, E1-4, E1-7, and the
descriptions (E1-2, update incidence per absence band, material information, order only, pairs).

Criteria are frozen in .steering/20261009-portrait-eh1-round2/design.md section 3 (commit ea02e557; section 3.11,
the oracle, added before any real configuration was run: commit 6b8ef7de).
Every verdict is per generator configuration; there is no overall pass.

Usage: checks.py <config.json> <SEED> <work dir> <results dir> --world v1|v2 [--jobs N] [--smoke | --pilot]
  --pilot  design 3.10: E1-3 of the positive controls only (no real configuration is run or reported)
"""

from __future__ import annotations

import argparse
import functools
import json
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
LABEL_ID = {"L300": 0, "L60": 1}  # seeds the bootstrap and the permutations of each label


def _init(cfg: dict, seed: int, work: str) -> None:
    global CFG, SEED, WORK
    CFG, SEED, WORK = cfg, seed, Path(work)
    os.environ["OMP_NUM_THREADS"] = "1"


@functools.lru_cache(maxsize=8)
def _session(sid: str) -> pt.Session:
    manifest = {m["sid"]: m for m in json.loads((WORK / "sessions.json").read_text(encoding="utf-8"))}
    return pt.load_session(WORK, manifest[sid])


def _task(args: tuple) -> dict:
    sid, conf, want_windows, want_final = args
    return pt.run(_session(sid), conf, CFG, SEED, want_windows, want_final)


def configs(cfg: dict) -> dict:
    """design 1.2-1.3: main = mapping x drift x {default, recent}; grid = mapping x drift x 5 schedulers."""
    d = cfg["scheduler_default"]
    default = pt.Sched("clock", d["interval_s"], d["window_s"], False, False)
    recent = pt.Sched("recent", d["interval_s"], d["window_s"], False, False)
    scheds = [default,
              pt.Sched("clock", d["interval_s"], d["window_s"], True, False),
              pt.Sched("clock", d["interval_s"], d["window_s"], False, True),
              pt.Sched("clock", d["interval_s"], d["window_s"], True, True),
              recent]
    grid = [pt.Config(m, dr, s) for m in cfg["mappings"] for dr in cfg["drifts"] for s in scheds]
    main = [pt.Config(m, dr, s) for s in (default, recent) for m in cfg["mappings"] for dr in cfg["drifts"]]
    pc1 = pt.Config("raw", "none", pt.Sched("stop"), pc="PC1")
    pc2 = pt.Config("ordinal", "none", default, pc="PC2")
    orc = [pt.Config("ordinal", "none", s, pc="ORC") for s in (default, recent)]  # design 3.11
    return {"grid": grid, "main": main, "scheds": scheds, "pc1": pc1, "pc2": pc2, "orc": orc}


# ---------------------------------------------------------------------------
# Statistics
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
    key, X, y, groups, kind, seed, folds = args
    return key, oof_predict(X, y, groups, kind, seed, folds)


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


def ratio_of_medians(a: np.ndarray, b: np.ndarray) -> float:
    ma, mb = np.median(a) if len(a) else np.nan, np.median(b) if len(b) else np.nan
    if ma == 0 and mb == 0:
        return 1.0
    if mb == 0:
        return float("inf")
    return float(ma / mb)


# ---------------------------------------------------------------------------
# E1-3 (design 3.1)
# ---------------------------------------------------------------------------

def _to_memmap(arr: np.ndarray, d: Path, name: str) -> np.ndarray:
    """Write once, pass by file: joblib sends a memmap by reference instead of dumping it again per call."""
    path = d / f"{name}.npy"
    np.save(path, np.ascontiguousarray(arr))
    return np.load(path, mmap_mode="r")


def e13_target(tag: str, XA: np.ndarray, Y: np.ndarray, G: np.ndarray, strata: np.ndarray, XB: dict,
               cfg: dict, seed: int, jobs: int, nboot: int, nperm: int, applicable: bool,
               scratch: Path | None = None) -> dict:
    """One label. XB: config name -> {"full": X, "small": X}. Verdicts per design 3.1 and 3.11.
    scratch: a directory for the feature matrices (written once per label, read by every fit)."""
    from joblib import Parallel, delayed

    folds, margin, pc_lower = cfg["e13"]["folds"], cfg["e13"]["margin"], cfg["e13"]["pc_lower"]
    names = list(XB)
    if scratch is not None:
        scratch.mkdir(parents=True, exist_ok=True)
        XA = _to_memmap(XA, scratch, f"{tag}-A")
        XB = {n: {fs: _to_memmap(XB[n][fs], scratch, f"{tag}-{i}-{fs}") for fs in FSETS} for i, n in enumerate(names)}

    def fit_all(y: np.ndarray, t: str) -> dict:
        js = [((t, "A", None, k), XA, y, G, k, seed, folds) for k in KINDS]
        js += [((t, n, fs, k), XB[n][fs], y, G, k, seed, folds) for n in names for fs in FSETS for k in KINDS]
        return dict(Parallel(n_jobs=jobs, backend="loky")(delayed(_fit_job)(j) for j in js))

    preds = fit_all(Y, "obs")
    ones = np.ones(len(Y))
    auc_a = {k: weighted_auc(preds[("obs", "A", None, k)], Y, ones) for k in KINDS}
    n_sess = int(G.max()) + 1
    rng = np.random.default_rng(np.random.SeedSequence([seed, 313, LABEL_ID[tag]]))
    mults = [np.bincount(rng.integers(0, n_sess, size=n_sess), minlength=n_sess).astype(float) for _ in range(nboot)]
    boot_jobs = [(n, {(fs, k): preds[("obs", n, fs, k)] for fs in FSETS for k in KINDS},
                  {k: preds[("obs", "A", None, k)] for k in KINDS}, Y, G, mults) for n in names]
    boots = dict(Parallel(n_jobs=jobs, backend="loky")(delayed(_boot_job)(j) for j in boot_jobs))
    res = {"label": tag, "n_windows": int(len(Y)), "n_sessions": n_sess, "prevalence": float(Y.mean()),
           "auc_A": auc_a, "applicable": applicable, "configs": {}}
    for n in names:
        rec = {}
        for fs in FSETS:
            for k in KINDS:
                key = f"{fs}/{k}"
                gain = weighted_auc(preds[("obs", n, fs, k)], Y, ones) - auc_a[k]
                b = boots[n][key]
                rec[key] = {"auc_B": auc_a[k] + gain, "gain": gain,
                            "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]}
        # a NaN bound (a draw without positives) must not depend on the order of max(): it counts as the
        # side that keeps a verdict from passing (upper +inf, lower -inf)
        ups = [rec[f"{fs}/{k}"]["ci95"][1] for fs in FSETS for k in KINDS]
        los = [rec[f"{fs}/{k}"]["ci95"][0] for fs in FSETS for k in KINDS]
        rec["n_nan_bounds"] = int(np.isnan(ups).sum() + np.isnan(los).sum())
        rec["upper_max"] = float("inf") if any(np.isnan(ups)) else max(ups)
        rec["lower_max"] = float("-inf") if any(np.isnan(los)) else max(los)
        res["configs"][n] = rec
    pcs = [n for n in names if n in ("PC1", "PC2")]
    pcs_ok = all(res["configs"][n]["lower_max"] > pc_lower for n in pcs)
    null = {n: [] for n in names}
    prng = np.random.default_rng(np.random.SeedSequence([seed, 911, LABEL_ID[tag]]))
    for pi in range(nperm):
        yp = stratified_permutation(Y, strata, prng)
        pp = fit_all(yp, f"perm{pi}")
        aa = {k: weighted_auc(pp[(f"perm{pi}", "A", None, k)], yp, ones) for k in KINDS}
        for n in names:
            null[n].append(max(weighted_auc(pp[(f"perm{pi}", n, fs, k)], yp, ones) - aa[k]
                               for fs in FSETS for k in KINDS))
    null95 = {n: float(np.percentile(v, 95)) for n, v in null.items()} if nperm else {}
    null_ok = all(v < margin for v in null95.values()) if nperm else None
    for n in names:
        rec = res["configs"][n]
        if nperm:
            rec["null_gain_max_by_perm"] = null[n]
            rec["null95"] = null95[n]
        if n in pcs:
            rec["verdict"] = "detector_ok" if rec["lower_max"] > pc_lower else "detector_failed"
            if rec["n_nan_bounds"]:
                rec["verdict_reason"] = "a bootstrap draw without positives (NaN bound)"
        elif not applicable:  # world v1, declared before the results (design 3.1, 3.11)
            rec["verdict"] = "not_applicable"
        elif n.startswith("ORC-"):  # design 3.11: the reach of the scheduler's channel, not a verdict on a config
            if rec["n_nan_bounds"]:
                rec["verdict"] = "undecidable"  # a bootstrap draw without positives: no reading of the channel
            elif rec["upper_max"] < margin and null_ok:
                rec["verdict"] = "channel_narrow"
            elif rec["lower_max"] > pc_lower:
                rec["verdict"] = "channel_open"
            else:
                rec["verdict"] = "channel_partial"
        elif not (pcs_ok and null_ok):
            rec["verdict"] = "undecidable"
        else:
            rec["verdict"] = "green" if rec["upper_max"] < margin else "red"
    res["positive_controls_ok"], res["null_ok"] = pcs_ok, null_ok
    return res


def e13_labels(p_sids: list, cfg: dict) -> dict:
    """Both labels (design 1.4): model A, labels, groups, null strata, and the rows each label uses.
    Rows are all 60 s windows of the P sessions in order; L300 keeps the windows with a full span."""
    parts: dict[str, list] = {k: [] for k in ("XA", "Y", "ACT", "G", "EX", "YL", "ACTL", "V")}
    for i, sid in enumerate(p_sids):
        s = _session(sid)
        fa, lab, act_n = pt.presence_features(s, cfg)
        ex, labl, actl, valid = pt.presence_features_long(s, cfg)
        for k, v in zip(parts, (fa, lab, act_n, np.full(len(lab), i), ex, labl, actl, valid)):
            parts[k].append(v)
    XA, EX = np.vstack(parts["XA"]), np.vstack(parts["EX"])
    Y, ACT, G, YL, ACTL, V = (np.concatenate(parts[k]) for k in ("Y", "ACT", "G", "YL", "ACTL", "V"))
    e60, el = cfg["e13"]["strata_edges"], cfg["e13"]["strata_edges_long"]
    return {
        "L300": {"XA": np.hstack([XA, EX])[V], "Y": YL[V], "G": G[V], "strata": np.digitize(ACTL[V], el[1:-1]),
                 "rows": V, "G_all": G},
        "L60": {"XA": XA, "Y": Y, "G": G, "strata": np.digitize(ACT, e60[1:-1]),
                "rows": np.ones(len(Y), dtype=bool), "G_all": G},
    }


def attacker_sets(lab: dict, shape: dict, cfg: dict) -> dict:
    """The two attacker feature sets per configuration for one label (design 1.4). The lags are taken on
    all windows before the label's rows are selected. shape: config name -> stacked window features."""
    rows, xa = lab["rows"], lab["XA"]
    out = {}
    for n, F in shape.items():
        full = lagged(F, lab["G_all"], cfg["e13"]["lags"])[rows]
        out[n] = {"full": np.hstack([xa, full]), "small": np.hstack([xa, F[rows]])}
    return out


def material_info(p_sids: list, inputs: dict, cfg: dict, seed: int) -> dict:
    """design 3.7 (descriptive): gain of model A plus the span mean of p_stuck, or of the F levels."""
    ws, L = cfg["e13"]["window_s"], cfg["e13"]["long_s"]
    res = {}
    for tag, span in (("L300", L), ("L60", ws)):
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
        for k in KINDS:
            a = weighted_auc(oof_predict(XA, Y, G, k, seed, cfg["e13"]["folds"]), Y, ones)
            bp = weighted_auc(oof_predict(np.hstack([XA, PS]), Y, G, k, seed, cfg["e13"]["folds"]), Y, ones)
            bf = weighted_auc(oof_predict(np.hstack([XA, FL]), Y, G, k, seed, cfg["e13"]["folds"]), Y, ones)
            r[k] = {"auc_A": a, "gain_p_stuck": bp - a, "gain_F_levels": bf - a}
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
    ap.add_argument("--world", choices=("v1", "v2"), required=True)
    ap.add_argument("--jobs", type=int, default=16)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--smoke", action="store_true", help="fewer bootstrap draws and permutations (pipeline check only)")
    g.add_argument("--pilot", action="store_true", help="design 3.10: E1-3 of the positive controls only")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"], cfg["e16"]["bootstrap"] = 200, 2, 200
    if a.pilot:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"] = cfg["sets"]["pilot"]["bootstrap"], 0
    seed = int(Path(a.seed_file).read_text().strip())
    work, out = Path(a.work), Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    by_set: dict[str, list[dict]] = {}
    for m in manifest:
        by_set.setdefault(m["set"], []).append(m)
    C = configs(cfg)
    main_names = {c.name for c in C["main"]}
    e13_confs = ([] if a.pilot else C["main"] + C["orc"]) + [C["pc1"], C["pc2"]]
    e13_names = [c.name for c in e13_confs]
    t0 = time.time()

    # ---------------- runs ----------------
    tasks = []
    for m in by_set["P"]:
        for c in ([] if a.pilot else C["grid"] + C["orc"]) + [C["pc1"], C["pc2"]]:
            tasks.append((m["sid"], c, c.name in e13_names, False))
    d_sets = [s for s in by_set if s.startswith("D_")] if not a.pilot else []
    for s in d_sets:
        for m in by_set[s]:
            for c in C["grid"]:  # final images only where they are used (describe pairs, order only)
                tasks.append((m["sid"], c, False, c.name in main_names and s in ("D_shuffled", "D_diffend")))
    for s in (() if a.pilot else ("O", "J", "Jsh")):
        for m in by_set.get(s, []):
            for c in C["main"]:
                tasks.append((m["sid"], c, False, True))
    tasks.sort(key=lambda t: t[0])  # keeps a session's runs together for the per-worker cache
    results: dict[tuple[str, str], dict] = {}
    with ProcessPoolExecutor(max_workers=a.jobs, initializer=_init, initargs=(cfg, seed, str(work))) as ex:
        for r in ex.map(_task, tasks, chunksize=8):
            results[(r["sid"], r["config"])] = r
    print(f"runs: {len(results)} in {time.time() - t0:.0f} s", flush=True)

    p_sids = [m["sid"] for m in by_set["P"]]
    _init(cfg, seed, str(work))

    # ---------------- E1-3 ----------------
    shape = {n: np.vstack([results[(sid, n)]["windows"] for sid in p_sids]) for n in e13_names}
    inputs = e13_labels(p_sids, cfg)
    applicable = a.world != "v1"
    e13 = {}
    scratch = Path(tempfile.mkdtemp(prefix="e13-", dir=work))  # under the git-ignored work dir
    try:
        for tag in ("L300", "L60"):
            inp = inputs[tag]
            XB = attacker_sets(inp, shape, cfg)  # built per label to bound memory
            e13[tag] = e13_target(tag, inp["XA"], inp["Y"], inp["G"], inp["strata"], XB, cfg, seed, a.jobs,
                                  cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"], applicable, scratch / tag)
            del XB
            shutil.rmtree(scratch / tag, ignore_errors=True)  # free the disk before the next label
            print(f"E1-3 {tag} done at {time.time() - t0:.0f} s", flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    del shape
    e13["primary"] = "L300"
    e13["seed"] = seed
    if a.pilot:
        e13["_note"] = ("Pilot (design 3.10): SEED + offset, positive controls only; not a result of round 2. "
                        "The numbers go to design section 8; this file is not committed.")
        dump(out / "pilot_e13.json", e13)
        for tag in ("L300", "L60"):
            for n in ("PC1", "PC2"):
                r = e13[tag]["configs"][n]
                print(f"pilot {tag} {n}: lower_max={r['lower_max']:+.4f} upper_max={r['upper_max']:+.4f} {r['verdict']}")
        return 0
    dump(out / "e13.json", e13)
    dump(out / "material_info.json", {"_note": "Descriptive (design 3.7): no verdict.",
                                      **material_info(p_sids, inputs, cfg, seed)})
    del inputs
    print(f"material info done at {time.time() - t0:.0f} s", flush=True)

    # ---------------- E1-6 / E1-4 / E1-7 ----------------
    e16c, e14c, e17c, spear = {}, {}, {}, {}
    from scipy.stats import spearmanr
    band_i = cfg["e16"]["band_invite_s"]
    band_o = cfg["e16"]["band_other_s"]
    brng = np.random.default_rng(np.random.SeedSequence([seed, 616]))
    sess_draws = [brng.integers(0, len(p_sids), size=len(p_sids)) for _ in range(cfg["e16"]["bootstrap"])]
    for c in C["grid"]:
        rows = []
        for i, sid in enumerate(p_sids):
            for ab in results[(sid, c.name)]["absences"]:
                rows.append((i, ab["len"], ab["change"], ab["e14_violation"], ab["e14_endpoint_violation"]))
        si = np.array([r[0] for r in rows])
        ln = np.array([r[1] for r in rows])
        ch = np.array([r[2] for r in rows])
        e14v = [r[3] for r in rows if r[3] is not None]
        e14_end = [r[4] for r in rows if r[4] is not None]
        v14 = "undecidable" if not e14v else ("green" if sum(e14v) == 0 else "red")
        e14c[c.name] = {"n_checked": len(e14v), "violations": int(sum(e14v)),
                        "endpoint_only_violations": int(sum(e14_end)), "verdict": v14}
        inv = (ln >= band_i[0]) & (ln < band_i[1])
        oth = np.zeros(len(ln), dtype=bool)
        for lo, hi in band_o:
            oth |= (ln >= lo) & (ln < hi)
        obs = ratio_of_medians(ch[inv], ch[oth])
        per_sess_inv = [ch[inv & (si == k)] for k in range(len(p_sids))]
        per_sess_oth = [ch[oth & (si == k)] for k in range(len(p_sids))]
        boots = np.array([ratio_of_medians(np.concatenate([per_sess_inv[k] for k in draw]),
                                           np.concatenate([per_sess_oth[k] for k in draw])) for draw in sess_draws])
        lo_q, hi_q = (1 - cfg["e16"]["ci"]) / 2 * 100, (1 + cfg["e16"]["ci"]) / 2 * 100
        # inverted_cdf: the draws can hold +inf (round 1 design 3.2), which linear interpolation turns into NaN
        ci = [float(np.percentile(boots, lo_q, method="inverted_cdf")),
              float(np.percentile(boots, hi_q, method="inverted_cdf"))]
        green = cfg["e16"]["lo"] <= ci[0] and ci[1] <= cfg["e16"]["hi"]
        e16c[c.name] = {"n_invite": int(inv.sum()), "n_other": int(oth.sum()),
                        "median_invite": float(np.median(ch[inv])) if inv.any() else None,
                        "median_other": float(np.median(ch[oth])) if oth.any() else None,
                        "ratio": obs, "ci90": ci, "verdict": "green" if green else "red"}
        spear[c.name] = float(spearmanr(ln, ch).statistic) if len(ch) > 2 and np.ptp(ch) > 0 else 0.0
        viol = sum(results[(sid, c.name)]["e17_violations"] for sid in p_sids)
        n_d = 0
        for s in d_sets:
            for m in by_set[s]:
                viol += results[(m["sid"], c.name)]["e17_violations"]
                n_d += 1
        e17c[c.name] = {"sessions": len(p_sids) + n_d, "violations": int(viol), "verdict": "green" if viol == 0 else "red"}
    dump(out / "e16.json", e16c)
    dump(out / "e14.json", e14c)
    dump(out / "e17.json", e17c)

    # ---------------- update incidence per absence band (design 3.7, descriptive) ----------------
    bands = [[60, 300], [300, 1200], [1200, 5400]]
    incid = {}
    for sc in C["scheds"]:
        conf = pt.Config(cfg["mappings"][0], "none", sc)  # update times do not depend on the mapping
        rec = {}
        for lo, hi in bands:
            n_in = np.array([ab["n_inside"] for sid in p_sids for ab in results[(sid, conf.name)]["absences"]
                             if lo <= ab["len"] < hi])
            rec[f"{lo}-{hi}"] = {"n_absences": int(len(n_in)),
                                 "share_with_update": float((n_in >= 1).mean()) if len(n_in) else None,
                                 "median_updates": float(np.median(n_in)) if len(n_in) else None}
        incid[sc.name] = rec
    dump(out / "incidence.json", {"_note": "Descriptive (design 3.7): no verdict.", "by_scheduler": incid})

    # ---------------- path sensitivity (design 3.3) and order only (descriptive) ----------------
    oc = cfg["order"]
    order = {}
    o_pairs = {m["pair"]: {} for m in by_set["O"]}
    for m in by_set["O"] + by_set["J"]:
        o_pairs[m["pair"]][m["role"]] = m["sid"]

    def proj(img: np.ndarray) -> np.ndarray:
        return pt.project(img.astype(np.float32), oc["proj_factor"], oc["proj_sigma"])

    def rat(o: list, j: list) -> float:
        mo, mj = float(np.median(o)), float(np.median(j))
        if mj == 0:
            return float("inf") if mo > 0 else float("nan")
        return mo / mj

    def distances(pairs: dict, name: str) -> tuple:
        d, dj, dp, djp = [], [], [], []
        for roles in pairs.values():
            if not {"a", "b", "j"} <= set(roles):
                continue
            fa = results[(roles["a"], name)]["final"].astype(np.float32)
            fb = results[(roles["b"], name)]["final"].astype(np.float32)
            fj = results[(roles["j"], name)]["final"].astype(np.float32)
            d.append(pt.mad(fa, fb)), dj.append(pt.mad(fa, fj))
            dp.append(pt.mad(proj(fa), proj(fb))), djp.append(pt.mad(proj(fa), proj(fj)))
        return d, dj, dp, djp

    sh_pairs: dict = {}
    for m in by_set.get("D_shuffled", []) + by_set.get("Jsh", []):
        sh_pairs.setdefault(m["pair"], {})[m["role"]] = m["sid"]
    for c in C["main"]:
        dO, dJ, dOp, dJp = distances(o_pairs, c.name)
        r_full, r_proj = rat(dO, dJ), rat(dOp, dJp)
        order[c.name] = {"median_dO": float(np.median(dO)), "median_dJ": float(np.median(dJ)),
                         "ratio_full": r_full, "median_dO_proj": float(np.median(dOp)),
                         "median_dJ_proj": float(np.median(dJp)), "ratio_proj": r_proj,
                         "verdict": "green" if (r_full >= oc["ratio_min"] and r_proj >= oc["ratio_min"]) else "red"}
        dS, dJs, dSp, dJsp = distances(sh_pairs, c.name)
        if dS:
            order[c.name]["order_only"] = {  # descriptive (design 3.3)
                "n_pairs": len(dS), "median_d_shuffled": float(np.median(dS)), "median_d_jitter": float(np.median(dJs)),
                "ratio_full": rat(dS, dJs), "ratio_proj": rat(dSp, dJsp)}
    dump(out / "order.json", order)

    # ---------------- descriptive: D pairs, Spearman ----------------
    desc = {"spearman_absence_len_vs_change": spear, "pairs": {}}
    for s in ("D_shuffled", "D_diffend"):
        pairs = {}
        for m in by_set.get(s, []):
            pairs.setdefault(m["pair"], {})[m["role"]] = m["sid"]
        desc["pairs"][s] = {}
        for c in C["main"]:
            d = [pt.mad(results[(r["a"], c.name)]["final"].astype(np.float32),
                        results[(r["b"], c.name)]["final"].astype(np.float32)) for r in pairs.values()]
            desc["pairs"][s][c.name] = {"median": float(np.median(d)), "n": len(d)}
    dump(out / "describe.json", desc)

    # ---------------- E1-2 (scheduler only; design 3.7 adds recent) ----------------
    gr = cfg["e12_grid"]
    e12 = {}
    targets = p_sids + [m["sid"] for m in by_set.get("D_continuous", [])] + [m["sid"] for m in by_set.get("D_sleep", [])]
    scheds = [pt.Sched("clock", I, Wd, jit, cap) for I in gr["interval_s"] for Wd in gr["window_s"]
              for cap in gr["cap1"] for jit in gr["jitter"]]
    scheds += [pt.Sched("recent", I, Wd, jit, False) for I in gr["interval_s"] for Wd in gr["window_s"]
               for jit in gr["jitter"]]
    for sc in scheds:
        since, per_hour, skipped, slots = [], [], 0, 0
        cont_gap, sleep_ups = [], []
        for sid in targets:
            ss = _session(sid)
            ups = pt.schedule(ss, sc, cfg["scheduler_jitter_frac"], seed)
            n_slots = int((ss.duration_s - 1) // sc.interval_s)  # slots k*I with k >= 1 and k*I < duration
            if ss.set == "P":
                slots += n_slots
                skipped += n_slots - len(ups)
                for u in ups:
                    before = ss.presses[ss.presses <= u]
                    since.append(float(u - before[-1]) if len(before) else float(u))
                for h in range(ss.duration_s // 3600):
                    nu = int(((ups >= 3600 * h) & (ups < 3600 * (h + 1))).sum())
                    silent = float((~ss.active[3600 * h : 3600 * (h + 1)]).sum())
                    per_hour.append((nu, silent))
            elif ss.set == "D_continuous":
                pts = np.concatenate([[0], ups, [ss.duration_s]])
                cont_gap.append(float(np.diff(pts).max()))
            elif ss.set == "D_sleep":
                sl = ss.seg == pt.SLEEP_CODE
                sleep_ups.append(int(sl[ups].sum()) if len(ups) else 0)
        ph = np.array(per_hour, dtype=float)
        corr = float(np.corrcoef(ph[:, 0], ph[:, 1])[0, 1]) if len(ph) > 2 and ph[:, 0].std() > 0 else None
        since = np.array(since)
        e12[sc.name] = {
            "skipped_slot_fraction": skipped / max(slots, 1),
            "since_last_press_at_update_s": {q: float(np.percentile(since, q)) for q in (5, 25, 50, 75, 95)} if len(since) else None,
            "corr_updates_per_hour_vs_silent_s": corr,
            "continuous_max_gap_s": cont_gap,
            "updates_during_sleep": sleep_ups,
        }
    dump(out / "e12.json", e12)

    # ---------------- summary ----------------
    summ = {}
    for c in C["main"]:
        summ[c.name] = {"E1-3 L300": e13["L300"]["configs"][c.name]["verdict"],
                        "E1-3 L60": e13["L60"]["configs"][c.name]["verdict"], "path": order[c.name]["verdict"]}
    for c in C["grid"]:
        summ.setdefault(c.name, {})
        summ[c.name].update({"E1-6": e16c[c.name]["verdict"], "E1-4": e14c[c.name]["verdict"],
                             "E1-7": e17c[c.name]["verdict"]})
    for n in ["PC1", "PC2"] + [c.name for c in C["orc"]]:
        summ[n] = {f"E1-3 {t}": e13[t]["configs"][n]["verdict"] for t in ("L300", "L60")}
    dump(out / "summary.json", summ)
    print(f"all done in {time.time() - t0:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
