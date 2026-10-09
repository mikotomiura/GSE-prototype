"""EH1 checks of the portrait: E1-3, E1-6, order sensitivity, E1-4, E1-7, and the E1-2 description.

Criteria are frozen in .steering/20261009-portrait-eh1-eh2/design.md section 3 (commit abfb2c45).
Every verdict is per generator configuration; there is no overall pass.

Usage: checks.py <config.json> <SEED> <work dir> <results dir> [--jobs N]
"""

from __future__ import annotations

import argparse
import functools
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import portrait as pt

CFG: dict = {}
SEED = 0
WORK = Path()


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
    res = pt.run(_session(sid), conf, CFG, SEED, want_windows, want_final)
    if want_final:
        res["final"] = res["final"].astype(np.float16)
    return res


def configs(cfg: dict) -> dict:
    d = cfg["scheduler_default"]
    default = pt.Sched("clock", d["interval_s"], d["window_s"], False, False)
    scheds = [default,
              pt.Sched("clock", d["interval_s"], d["window_s"], True, False),
              pt.Sched("clock", d["interval_s"], d["window_s"], False, True),
              pt.Sched("clock", d["interval_s"], d["window_s"], True, True)]
    grid = [pt.Config(m, dr, s) for m in cfg["mappings"] for dr in cfg["drifts"] for s in scheds]
    base6 = [pt.Config(m, dr, default) for m in cfg["mappings"] for dr in cfg["drifts"]]
    pc1 = pt.Config("raw", "none", pt.Sched("stop"), pc="PC1")
    pc2 = pt.Config("ordinal", "none", default, pc="PC2")
    recent = pt.Sched("recent", d["interval_s"], d["window_s"], False, False)
    explo = [pt.Config(m, dr, recent) for m in cfg["mappings"] for dr in cfg["drifts"]]
    return {"grid": grid, "base6": base6, "pc1": pc1, "pc2": pc2, "explo": explo}


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def weighted_auc(score: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    s, yy, ww = score[order], y[order], w[order]
    _, start = np.unique(s, return_index=True)
    pos_g = np.add.reduceat(ww * yy, start)
    neg_g = np.add.reduceat(ww * (1 - yy), start)
    neg_before = np.concatenate([[0.0], np.cumsum(neg_g)[:-1]])
    num = (pos_g * (neg_before + 0.5 * neg_g)).sum()
    den = pos_g.sum() * neg_g.sum()
    return float(num / den) if den > 0 else float("nan")


def cluster_weights(groups: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    uniq, inv = np.unique(groups, return_inverse=True)
    draw = rng.integers(0, len(uniq), size=len(uniq))
    mult = np.bincount(draw, minlength=len(uniq)).astype(float)
    return mult[inv]


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


def ratio_of_medians(a: np.ndarray, b: np.ndarray) -> float:
    ma, mb = np.median(a) if len(a) else np.nan, np.median(b) if len(b) else np.nan
    if ma == 0 and mb == 0:
        return 1.0
    if mb == 0:
        return float("inf")
    return float(ma / mb)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("seed_file")
    ap.add_argument("work")
    ap.add_argument("results")
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--smoke", action="store_true", help="fewer bootstrap draws and permutations (pipeline check only)")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.smoke:
        cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"], cfg["e16"]["bootstrap"] = 200, 2, 200
    seed = int(Path(a.seed_file).read_text().strip())
    work, out = Path(a.work), Path(a.results)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((work / "sessions.json").read_text(encoding="utf-8"))
    by_set: dict[str, list[dict]] = {}
    for m in manifest:
        by_set.setdefault(m["set"], []).append(m)
    C = configs(cfg)
    base6_names = {c.name for c in C["base6"]}
    e13_confs = C["base6"] + [C["pc1"], C["pc2"]]
    e13_names = [c.name for c in e13_confs]
    t0 = time.time()

    # ---------------- runs ----------------
    tasks = []
    for m in by_set["P"]:
        for c in C["grid"] + [C["pc1"], C["pc2"]] + C["explo"]:
            tasks.append((m["sid"], c, c.name in e13_names, False))
    d_sets = [s for s in by_set if s.startswith("D_")]
    for s in d_sets:
        for m in by_set[s]:
            for c in C["grid"]:
                tasks.append((m["sid"], c, False, c.name in base6_names))
    for s in ("O", "J"):
        for m in by_set[s]:
            for c in C["base6"]:
                tasks.append((m["sid"], c, False, True))
    tasks.sort(key=lambda t: t[0])  # keeps a session's runs together for the per-worker cache
    results: dict[tuple[str, str], dict] = {}
    with ProcessPoolExecutor(max_workers=a.jobs, initializer=_init, initargs=(cfg, seed, str(work))) as ex:
        for r in ex.map(_task, tasks, chunksize=8):
            results[(r["sid"], r["config"])] = r
    print(f"runs: {len(results)} in {time.time() - t0:.0f} s")

    p_sids = [m["sid"] for m in by_set["P"]]
    _init(cfg, seed, str(work))

    # ---------------- E1-3 ----------------
    XA, Y, ACT, G = [], [], [], []
    for i, sid in enumerate(p_sids):
        fa, lab, act_n = pt.presence_features(_session(sid), cfg)
        XA.append(fa)
        Y.append(lab)
        ACT.append(act_n)
        G.append(np.full(len(lab), i))
    XA, Y, ACT, G = np.vstack(XA), np.concatenate(Y), np.concatenate(ACT), np.concatenate(G)
    edges = cfg["e13"]["strata_edges"]
    strata = np.digitize(ACT, edges[1:-1])
    XB = {}
    for c in e13_confs:
        F = np.vstack([results[(sid, c.name)]["windows"] for sid in p_sids])
        XB[c.name] = np.hstack([XA, lagged(F, G, cfg["e13"]["lags"])])
    folds, nboot, nperm = cfg["e13"]["folds"], cfg["e13"]["bootstrap"], cfg["e13"]["null_perms"]
    kinds = ("hgb", "lr")

    from joblib import Parallel, delayed

    def fit_all(y: np.ndarray, tag: str) -> dict:
        # joblib (loky) memory-maps the large arrays instead of pickling them per job
        jobs = [((tag, "A", k), XA, y, G, k, seed, folds) for k in kinds]
        jobs += [((tag, name, k), XB[name], y, G, k, seed, folds) for name in e13_names for k in kinds]
        return dict(Parallel(n_jobs=a.jobs, backend="loky")(delayed(_fit_job)(j) for j in jobs))

    preds = fit_all(Y, "obs")
    rng = np.random.default_rng(np.random.SeedSequence([seed, 313]))
    W = [cluster_weights(G, rng) for _ in range(nboot)]
    ones = np.ones(len(Y))
    e13 = {"n_windows": int(len(Y)), "n_sessions": len(p_sids), "prevalence": float(Y.mean()), "configs": {}}
    auc_a = {k: weighted_auc(preds[("obs", "A", k)], Y, ones) for k in kinds}
    for name in e13_names:
        rec = {}
        for k in kinds:
            pa, pb = preds[("obs", "A", k)], preds[("obs", name, k)]
            gain = weighted_auc(pb, Y, ones) - auc_a[k]
            boots = np.array([weighted_auc(pb, Y, w) - weighted_auc(pa, Y, w) for w in W])
            rec[k] = {"auc_A": auc_a[k], "auc_B": auc_a[k] + gain, "gain": gain,
                      "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
        rec["upper_max"] = max(rec[k]["ci95"][1] for k in kinds)
        rec["lower_max"] = max(rec[k]["ci95"][0] for k in kinds)
        e13["configs"][name] = rec
    print(f"E1-3 observed done at {time.time() - t0:.0f} s")
    null = {name: [] for name in e13_names}
    prng = np.random.default_rng(np.random.SeedSequence([seed, 911]))
    for pi in range(nperm):
        yp = stratified_permutation(Y, strata, prng)
        pp = fit_all(yp, f"perm{pi}")
        aa = {k: weighted_auc(pp[(f"perm{pi}", "A", k)], yp, ones) for k in kinds}
        for name in e13_names:
            null[name].append(max(weighted_auc(pp[(f"perm{pi}", name, k)], yp, ones) - aa[k] for k in kinds))
    margin, pc_lower = cfg["e13"]["margin"], cfg["e13"]["pc_lower"]
    null95 = {name: float(np.percentile(v, 95)) for name, v in null.items()}
    pcs_ok = all(e13["configs"][n]["lower_max"] > pc_lower for n in ("PC1", "PC2"))
    null_ok = all(v < margin for v in null95.values())
    for name in e13_names:
        rec = e13["configs"][name]
        rec["null_gain_max_by_perm"] = null[name]
        rec["null95"] = null95[name]
        if name in ("PC1", "PC2"):
            rec["verdict"] = "detector_ok" if rec["lower_max"] > pc_lower else "detector_failed"
        elif not (pcs_ok and null_ok):
            rec["verdict"] = "undecidable"
        else:
            rec["verdict"] = "green" if rec["upper_max"] < margin else "red"
    e13["positive_controls_ok"], e13["null_ok"] = pcs_ok, null_ok
    (out / "e13.json").write_text(json.dumps(e13, indent=1), encoding="utf-8")
    print(f"E1-3 done at {time.time() - t0:.0f} s")

    # ---------------- E1-6 / E1-4 / E1-7 ----------------
    e16c, e14c, e17c, spear = {}, {}, {}, {}
    from scipy.stats import spearmanr
    band_i = cfg["e16"]["band_invite_s"]
    band_o = cfg["e16"]["band_other_s"]
    brng = np.random.default_rng(np.random.SeedSequence([seed, 616]))
    sess_draws = [brng.integers(0, len(p_sids), size=len(p_sids)) for _ in range(cfg["e16"]["bootstrap"])]
    explo_names = {c.name for c in C["explo"]}
    for c in C["grid"] + [C["pc2"]] + C["explo"]:
        rows = []
        for i, sid in enumerate(p_sids):
            for ab in results[(sid, c.name)]["absences"]:
                rows.append((i, ab["len"], ab["change"], ab["change_proj"], ab["e14_violation"]))
        si = np.array([r[0] for r in rows])
        ln = np.array([r[1] for r in rows])
        ch = np.array([r[2] for r in rows])
        e14v = [r[4] for r in rows if r[4] is not None]
        e14c[c.name] = {"n_checked": len(e14v), "violations": int(sum(e14v)),
                        "verdict": "green" if sum(e14v) == 0 else "red"}
        if c.pc:
            continue
        inv = (ln >= band_i[0]) & (ln < band_i[1])
        oth = np.zeros(len(ln), dtype=bool)
        for lo, hi in band_o:
            oth |= (ln >= lo) & (ln < hi)
        obs = ratio_of_medians(ch[inv], ch[oth])
        boots = []
        per_sess_inv = [ch[inv & (si == k)] for k in range(len(p_sids))]
        per_sess_oth = [ch[oth & (si == k)] for k in range(len(p_sids))]
        for draw in sess_draws:
            ai = np.concatenate([per_sess_inv[k] for k in draw])
            ao = np.concatenate([per_sess_oth[k] for k in draw])
            boots.append(ratio_of_medians(ai, ao))
        boots = np.array(boots)
        lo_q, hi_q = (1 - cfg["e16"]["ci"]) / 2 * 100, (1 + cfg["e16"]["ci"]) / 2 * 100
        # inverted_cdf: the draws can hold +inf (design 3.2), which linear interpolation turns into NaN
        ci = [float(np.percentile(boots, lo_q, method="inverted_cdf")),
              float(np.percentile(boots, hi_q, method="inverted_cdf"))]
        green = cfg["e16"]["lo"] <= ci[0] and ci[1] <= cfg["e16"]["hi"]
        e16c[c.name] = {"n_invite": int(inv.sum()), "n_other": int(oth.sum()),
                        "median_invite": float(np.median(ch[inv])) if inv.any() else None,
                        "median_other": float(np.median(ch[oth])) if oth.any() else None,
                        "ratio": obs, "ci90": ci, "verdict": "green" if green else "red"}
        ok = ch > -1
        rho = spearmanr(ln[ok], ch[ok]).statistic if np.ptp(ch) > 0 else 0.0
        spear[c.name] = float(rho)
        if c.name in explo_names:
            continue  # exploratory: E1-6 and E1-4 only, on P
        viol = sum(results[(sid, c.name)]["e17_violations"] for sid in p_sids)
        n_d = 0
        for s in d_sets:
            for m in by_set[s]:
                viol += results[(m["sid"], c.name)]["e17_violations"]
                n_d += 1
        e17c[c.name] = {"sessions": len(p_sids) + n_d, "violations": int(viol), "verdict": "green" if viol == 0 else "red"}
    (out / "e16.json").write_text(json.dumps({k: v for k, v in e16c.items() if k not in explo_names}, indent=1),
                                  encoding="utf-8")
    (out / "e14.json").write_text(json.dumps({k: v for k, v in e14c.items() if k not in explo_names}, indent=1),
                                  encoding="utf-8")
    (out / "exploratory_recent.json").write_text(json.dumps(
        {"_note": "Outside the frozen criteria (design section 8): a scheduler that never updates inside an absence "
                  "of 60 s or more.",
         "e16": {k: v for k, v in e16c.items() if k in explo_names},
         "e14": {k: v for k, v in e14c.items() if k in explo_names},
         "spearman": {k: v for k, v in spear.items() if k in explo_names}}, indent=1), encoding="utf-8")
    (out / "e17.json").write_text(json.dumps(e17c, indent=1), encoding="utf-8")

    # ---------------- order sensitivity ----------------
    oc = cfg["order"]
    order = {}
    o_pairs = {m["pair"]: {} for m in by_set["O"]}
    for m in by_set["O"] + by_set["J"]:
        o_pairs[m["pair"]][m["role"]] = m["sid"]

    def proj(img: np.ndarray) -> np.ndarray:
        return pt.project(img.astype(np.float32), oc["proj_factor"], oc["proj_sigma"])

    for c in C["base6"]:
        dO, dJ, dOp, dJp = [], [], [], []
        for pair, roles in o_pairs.items():
            fa = results[(roles["a"], c.name)]["final"].astype(np.float32)
            fb = results[(roles["b"], c.name)]["final"].astype(np.float32)
            fj = results[(roles["j"], c.name)]["final"].astype(np.float32)
            dO.append(pt.mad(fa, fb))
            dJ.append(pt.mad(fa, fj))
            dOp.append(pt.mad(proj(fa), proj(fb)))
            dJp.append(pt.mad(proj(fa), proj(fj)))

        def rat(o: list, j: list) -> float:
            mo, mj = float(np.median(o)), float(np.median(j))
            if mj == 0:
                return float("inf") if mo > 0 else float("nan")
            return mo / mj

        r_full, r_proj = rat(dO, dJ), rat(dOp, dJp)
        order[c.name] = {"median_dO": float(np.median(dO)), "median_dJ": float(np.median(dJ)),
                         "ratio_full": r_full, "median_dO_proj": float(np.median(dOp)),
                         "median_dJ_proj": float(np.median(dJp)), "ratio_proj": r_proj,
                         "verdict": "green" if (r_full >= oc["ratio_min"] and r_proj >= oc["ratio_min"]) else "red"}
    (out / "order.json").write_text(json.dumps(order, indent=1), encoding="utf-8")

    # ---------------- descriptive: D pairs, Spearman ----------------
    desc = {"spearman_absence_len_vs_change": spear, "pairs": {}}
    for s in ("D_shuffled", "D_diffend"):
        pairs = {}
        for m in by_set.get(s, []):
            pairs.setdefault(m["pair"], {})[m["role"]] = m["sid"]
        desc["pairs"][s] = {}
        for c in C["base6"]:
            d = [pt.mad(results[(r["a"], c.name)]["final"].astype(np.float32),
                        results[(r["b"], c.name)]["final"].astype(np.float32)) for r in pairs.values()]
            desc["pairs"][s][c.name] = {"median": float(np.median(d)), "n": len(d)}
    (out / "describe.json").write_text(json.dumps(desc, indent=1), encoding="utf-8")

    # ---------------- E1-2 (scheduler only) ----------------
    g = cfg["e12_grid"]
    e12 = {}
    targets = p_sids + [m["sid"] for m in by_set.get("D_continuous", [])] + [m["sid"] for m in by_set.get("D_sleep", [])]
    for I in g["interval_s"]:
        for Wd in g["window_s"]:
            for cap in g["cap1"]:
                for jit in g["jitter"]:
                    sc = pt.Sched("clock", I, Wd, jit, cap)
                    since, per_hour, skipped, slots = [], [], 0, 0
                    cont_gap, sleep_ups = [], []
                    for sid in targets:
                        ss = _session(sid)
                        ups = pt.schedule(ss, sc, cfg["scheduler_jitter_frac"], seed)
                        n_slots = int(ss.duration_s // I)
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
    (out / "e12.json").write_text(json.dumps(e12, indent=1), encoding="utf-8")

    # ---------------- summary ----------------
    summ = {}
    for c in C["base6"]:
        summ[c.name] = {"E1-3": e13["configs"][c.name]["verdict"], "order": order[c.name]["verdict"]}
    for c in C["grid"]:
        summ.setdefault(c.name, {})
        summ[c.name].update({"E1-6": e16c[c.name]["verdict"], "E1-4": e14c[c.name]["verdict"],
                             "E1-7": e17c[c.name]["verdict"]})
    summ["PC1"] = {"E1-3": e13["configs"]["PC1"]["verdict"]}
    summ["PC2"] = {"E1-3": e13["configs"]["PC2"]["verdict"], "E1-4": e14c["PC2"]["verdict"]}
    (out / "summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(f"all done in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
