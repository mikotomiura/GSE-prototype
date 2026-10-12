"""Aggregates over writers (preregistration, "Reported quantities", "Utility", "Diagnostics").

Writer-unit percentile bootstrap, 2,000 resamples, 95%, stratified by prompt; the same resamples for every cell of a
sample (seed use bootstrap, the sample name in the writer field). The strongest attacker is the maximum over the
adaptive attackers available for the form, taken inside each resample. Only aggregates are returned.
"""
import os

import numpy as np

import seeds
import utility

B = 2000
LEVEL = 0.95
MUTATE = os.environ.get("MAIN_MUTATE", "")


def resamples(seed, prompts_of_writers, sample_name, n=B):
    """(n, W) index matrix (within each prompt, writers drawn with replacement; the columns of a prompt are
    contiguous) and {prompt: column slice}."""
    g = seeds.rng(seed, "bootstrap", "", sample_name)
    W = len(prompts_of_writers)
    by_p = {}
    for i, p in enumerate(prompts_of_writers):
        by_p.setdefault(p, []).append(i)
    out = np.empty((n, W), dtype=np.int64)
    cols, col = {}, 0
    for p in sorted(by_p):
        cols[p] = slice(col, col + len(by_p[p]))
        col += len(by_p[p])
    for b in range(n):
        col = 0
        for p in sorted(by_p):
            ix = by_p[p]
            src = list(range(W)) if MUTATE == "bootstrap_unstratified" else ix
            out[b, col:col + len(ix)] = np.array(src)[g.integers(0, len(src), len(ix))]
            col += len(ix)
    return out, cols


def ci(v):
    a = (1 - LEVEL) / 2
    return [float(np.quantile(v, a)), float(np.quantile(v, 1 - a))]


def cell_matrix(results, key, field="acc"):
    """Per-writer values of a cell (nan where the writer has no such cell)."""
    sc = key[0]
    return np.array([r[sc].get(key, {}).get(field, np.nan) for r in results], dtype=float)


def _boot_mean(v, R):
    """Mean over the writers present in each resample (nan-aware)."""
    m = v[R]
    with np.errstate(invalid="ignore"):
        return np.nanmean(m, axis=1)


def summarise_cells(results, R, strongest):
    """Accuracy, interval, multiple of 1/N, uplift over A0 and the strongest attacker per (scope, form, N[, k])."""
    keys = sorted({k for r in results for sc in ("full", "window") for k in r[sc]}, key=str)
    cells, boot = {}, {}
    for key in keys:
        v = cell_matrix(results, key)
        if np.all(np.isnan(v)):
            continue
        bm = _boot_mean(v, R)
        boot[key] = bm
        N = key[3]
        point = float(np.nanmean(v))
        cells[_name(key)] = {"acc": point, "ci": ci(bm), "x_chance": point * N, "writers": int(np.sum(~np.isnan(v))),
                             "top5": float(np.nanmean(cell_matrix(results, key, "top5"))),
                             "mrr": float(np.nanmean(cell_matrix(results, key, "rr"))),
                             "all_inf": int(np.nansum(cell_matrix(results, key, "all_inf"))),
                             "only_true_inf": int(np.nansum(cell_matrix(results, key, "only_true_inf"))),
                             "writer_p10_p50_p90": [float(np.nanquantile(v, q)) for q in (0.1, 0.5, 0.9)]}
    groups = {}
    for key in boot:
        groups.setdefault((key[0], key[1]) + key[3:], []).append(key)
    best = {}
    for g, ks in groups.items():
        cand = [k for k in ks if k[2] in strongest[g[0]]]
        if not cand:
            continue
        M = np.vstack([boot[k] for k in cand])
        pts = [cells[_name(k)]["acc"] for k in cand]
        pick = int(np.argmax(pts))
        bmax = M.max(axis=0)
        sel = np.argmax(M, axis=0)
        a0 = [k for k in ks if k[2] == "A0"]
        entry = {"acc": pts[pick], "ci": ci(bmax), "attacker": cand[pick][2], "x_chance": pts[pick] * g[2],
                 "share_selected": {cand[i][2]: float(np.mean(sel == i)) for i in range(len(cand))}}
        if a0:
            up = bmax - boot[a0[0]]
            entry["uplift_over_A0"] = pts[pick] - cells[_name(a0[0])]["acc"]
            entry["uplift_ci"] = ci(up)
        best[_gname(g)] = entry
        best[_gname(g)]["_boot"] = bmax
    return cells, best


def contrasts(best, pairs):
    out = {}
    for name, entry in best.items():
        scope, form = name.split("|")[0], name.split("|")[1]
        for f1, f2 in pairs:
            if form != f1:
                continue
            other = name.replace("|%s|" % f1, "|%s|" % f2, 1)
            if other in best:
                d = entry["_boot"] - best[other]["_boot"]
                out["%s - %s|%s" % (f1, f2, "|".join(name.split("|")[2:]) + "|" + scope)] = {
                    "diff": entry["acc"] - best[other]["acc"], "ci": ci(d)}
    return out


def strip_boot(best):
    return {k: {a: b for a, b in v.items() if a != "_boot"} for k, v in best.items()}


def _name(key):
    return "|".join(str(x) for x in key)


def _gname(g):
    return "|".join(str(x) for x in g)


# --- utility -------------------------------------------------------------------------------------------------------

def rank(v):
    order = np.argsort(v, kind="mergesort")
    r = np.empty(len(v))
    r[order] = np.arange(len(v), dtype=float)
    sv = v[order]
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(a, b):
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3:
        return np.nan
    x, y = rank(a[ok]), rank(b[ok])
    if x.std() == 0 or y.std() == 0:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def utility_summary(results, scores, forms_list, R, cols):
    """Per metric and form: Spearman with R0, ratio to R0 (median and 10/90 percentiles), Spearman with the human
    score; per prompt, then the mean and range over prompts, with bootstrap intervals of the means."""
    prompts = [r["prompt"] for r in results]
    ps = sorted(set(prompts))
    out = {}
    for m in utility.METRICS:
        r0 = np.array([_val(r, "R0", m) for r in results])
        for f in forms_list:
            cellv = utility.cell(m, f)
            v = np.array([_val(r, f, m) for r in results])
            per_p, per_h, ratios, dropped = {}, {}, {}, 0
            for p in ps:
                ix = np.array([i for i, q in enumerate(prompts) if q == p])
                per_p[p] = spearman(r0[ix], v[ix])
                per_h[p] = spearman(np.array([scores[i] for i in ix], dtype=float), v[ix])
            ok = (~np.isnan(r0)) & (r0 != 0) & (~np.isnan(v))
            dropped = int(np.sum(~((~np.isnan(r0)) & (r0 != 0))))
            rat = v[ok] / r0[ok] if ok.any() else np.array([])
            boot = []
            for b in range(R.shape[0]):
                vals = []
                for p in ps:
                    ix = R[b, cols[p]]
                    vals.append(spearman(r0[ix], v[ix]))
                boot.append(np.nanmean(vals) if not np.all(np.isnan(vals)) else np.nan)
            boot = np.array(boot)
            pv = [x for x in per_p.values() if not np.isnan(x)]
            out["%s|%s" % (m, f)] = {
                "cell": cellv,
                "spearman_r0_by_prompt": {p: _f(x) for p, x in per_p.items()},
                "spearman_r0_mean": _f(np.mean(pv)) if pv else None,
                "spearman_r0_range": [_f(min(pv)), _f(max(pv))] if pv else None,
                "spearman_r0_ci": ci(boot[~np.isnan(boot)]) if np.any(~np.isnan(boot)) else None,
                "spearman_score_by_prompt": {p: _f(x) for p, x in per_h.items()},
                "ratio_median_p10_p90": [_f(np.quantile(rat, q)) for q in (0.5, 0.1, 0.9)] if len(rat) else None,
                "ratio_dropped": dropped,
            }
    fig = {}
    for f in forms_list:
        vals = []
        for m in utility.METRICS:
            e = out["%s|%s" % (m, f)]
            vals.append(0.0 if e["cell"] == utility.NONE or e["spearman_r0_mean"] is None else e["spearman_r0_mean"])
        cells = [utility.cell(m, f) for m in utility.METRICS]
        fig[f] = {"median_spearman_r0": float(np.median(vals)), "ok": cells.count(utility.OK),
                  "approx": cells.count(utility.APPROX), "none": cells.count(utility.NONE)}
    return out, fig


def _val(r, f, m):
    v = r["utility"].get(f, {}).get(m)
    return np.nan if v is None else float(v)


def _f(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else float(x)
