"""Aggregates over writers (preregistration, "Reported quantities", "Utility", "Diagnostics").

Writer-unit percentile bootstrap, 2,000 resamples, 95%, stratified by prompt; the same resamples for every cell of a
sample (seed use bootstrap, the sample name in the writer field). The strongest attacker is the maximum over the
adaptive attackers available for the form, taken inside each resample. Only aggregates are returned.

Details fixed here before any data (listed in notes.md, "Implementation choices"):
- A3 on R3-u is the maximum of its sum and mean versions (preregistration, "Attackers"): the point estimate is the
  larger point estimate, and inside each resample the larger resample mean; it enters the strongest attacker as "A3";
- a resample in which no writer of a cell is present gives no value; intervals and the shares of the selected
  attacker are taken over the other resamples, and their number is reported (nan_resamples);
- the contrasts of config.json name base forms; "R3-t" stands for each R3-t(w), and a contrast whose pair is
  missing is listed under "missing" instead of being dropped;
- open world: in each draw of N = 1,000 (full text), the minimum cost over the N candidates (the true text
  included) against the minimum over the N - 1 decoys (the true text removed); the AUC is the probability that a
  pooled value of the first kind is below one of the second (ties 1/2), for the attacker selected by the point
  estimate (A3 on R3-u: the version with the larger point estimate);
- bias of true windows: the A2 cost per word of the true window (cost / k) against the A2 cost per word of the
  whole record aligned with the whole true text (full-text end), pooled over windows and writers.
"""
import os

import numpy as np
from scipy.stats import rankdata

import seeds
import utility

B = 2000
LEVEL = 0.95
MIN_WRITERS_PERCENTILE = 10
MUTATE = os.environ.get("MAIN_MUTATE", "")
R3U_A3 = ("A3-sum", "A3-mean")


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
    """Percentile interval over the resamples that have a value; None when none has."""
    v = np.asarray(v, dtype=float)
    v = v[~np.isnan(v)]
    if not len(v):
        return None
    a = (1 - LEVEL) / 2
    return [float(np.quantile(v, a)), float(np.quantile(v, 1 - a))]


def cell_matrix(results, key, field="acc"):
    """Per-writer values of a cell (nan where the writer has no such cell)."""
    sc = key[0]
    return np.array([r[sc].get(key, {}).get(field, np.nan) for r in results], dtype=float)


def _boot_mean(v, R):
    """Mean over the writers present in each resample (nan where none is present)."""
    m = v[R]
    with np.errstate(invalid="ignore"), np.testing.suppress_warnings() as sup:
        sup.filter(RuntimeWarning)
        return np.nanmean(m, axis=1)


def _nanmax_rows(M):
    """Column-wise maximum over the rows of M and the row of the maximum; nan (and -1) where every row is nan."""
    allnan = np.all(np.isnan(M), axis=0)
    filled = np.where(np.isnan(M), -np.inf, M)
    mx = filled.max(axis=0)
    arg = filled.argmax(axis=0)
    mx[allnan] = np.nan
    arg[allnan] = -1
    return mx, arg


def summarise_cells(results, R, strongest):
    """Cells (accuracy, interval, multiple of 1/N, ...) per (scope, form, attacker, N[, k]) and the strongest
    attacker per (scope, form, N[, k]). Returns (cells, best, boot); boot maps a cell key to its resample means."""
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
                             "nan_resamples": int(np.sum(np.isnan(bm))),
                             "top5": float(np.nanmean(cell_matrix(results, key, "top5"))),
                             "mrr": float(np.nanmean(cell_matrix(results, key, "rr"))),
                             "all_inf": int(np.nansum(cell_matrix(results, key, "all_inf"))),
                             "only_true_inf": int(np.nansum(cell_matrix(results, key, "only_true_inf"))),
                             # with few writers a percentile is one writer's value; it is not released then
                             "writer_p10_p50_p90": ([float(np.nanquantile(v, q)) for q in (0.1, 0.5, 0.9)]
                                                    if np.sum(~np.isnan(v)) >= MIN_WRITERS_PERCENTILE else None)}
    _r3u_a3(cells, boot)
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
        bmax, sel = _nanmax_rows(M)
        if MUTATE == "strongest_point_ci":
            bmax = M[pick]
        a0 = [k for k in ks if k[2] == "A0"]
        have = sel >= 0
        entry = {"acc": pts[pick], "ci": ci(bmax), "attacker": cand[pick][2], "x_chance": pts[pick] * g[2],
                 "nan_resamples": int(np.sum(~have)),
                 "share_selected": {cand[i][2]: (float(np.mean(sel[have] == i)) if have.any() else None)
                                    for i in range(len(cand))}}
        if a0:
            entry["uplift_over_A0"] = pts[pick] - cells[_name(a0[0])]["acc"]
            entry["uplift_ci"] = ci(bmax - boot[a0[0]])
        best[_gname(g)] = entry
        best[_gname(g)]["_boot"] = bmax
    return cells, best, boot


def _r3u_a3(cells, boot):
    """A3 on R3-u = the maximum of A3-sum and A3-mean (point: the larger point estimate; resample: the larger mean)."""
    for key in [k for k in boot if k[1] == "R3-u" and k[2] == R3U_A3[0]]:
        other = key[:2] + (R3U_A3[1],) + key[3:]
        if other not in boot:
            continue
        a3 = key[:2] + ("A3",) + key[3:]
        if MUTATE == "r3u_a3_sum_only":
            bm, pt = boot[key], cells[_name(key)]["acc"]
        else:
            bm, _ = _nanmax_rows(np.vstack([boot[key], boot[other]]))
            pt = max(cells[_name(key)]["acc"], cells[_name(other)]["acc"])
        boot[a3] = bm
        cells[_name(a3)] = {"acc": pt, "ci": ci(bm), "x_chance": pt * key[3], "of": list(R3U_A3),
                            "writers": cells[_name(key)]["writers"], "nan_resamples": int(np.sum(np.isnan(bm)))}


def r3u_a3_version(cells, scope, N, k=None):
    """The R3-u A3 version (A3-sum or A3-mean) with the larger point estimate (the first on a tie)."""
    tail = (N,) if k is None else (N, k)
    pts = [cells.get(_name((scope, "R3-u", v) + tail), {}).get("acc", -1.0) for v in R3U_A3]
    return R3U_A3[int(np.argmax(pts))]


def _expand(name, forms):
    """A config form name: itself, or every parameterised form of that base ('R3-t' -> 'R3-t(10)', ...)."""
    out = [f for f in forms if f == name or f.startswith(name + "(")]
    return out or [name]


def contrasts(best, cells, boot, pairs, forms):
    """Differences of the strongest attacker's accuracy (point and resample) for the config pairs, per scope, N and
    k. For R3 - R3-t(w) the A3 difference is added. Pairs without both cells are listed under "missing"."""
    out, missing = {}, []
    tails = sorted({tuple(n.split("|")[2:]) + (n.split("|")[0],) for n in best}, key=str)
    for f1, f2 in pairs:
        if MUTATE == "contrast_base_names":
            exp = [(f1, f2)]
        else:
            exp = [(a, b) for a in _expand(f1, forms) for b in _expand(f2, forms)]
        for a, b in exp:
            for tail in tails:
                scope, rest = tail[-1], list(tail[:-1])
                n1, n2 = "|".join([scope, a] + rest), "|".join([scope, b] + rest)
                label = "%s - %s|%s|%s" % (a, b, "|".join(rest), scope)
                if n1 not in best or n2 not in best:
                    missing.append(label)
                    continue
                e = {"diff": best[n1]["acc"] - best[n2]["acc"], "ci": ci(best[n1]["_boot"] - best[n2]["_boot"]),
                     "attackers": [best[n1]["attacker"], best[n2]["attacker"]]}
                if f2 == "R3-t":
                    tl = tuple(int(x) for x in rest)
                    k1, k2 = (scope, a, "A3") + tl, (scope, b, "A3") + tl
                    if k1 in boot and k2 in boot:
                        e["A3_diff"] = cells[_name(k1)]["acc"] - cells[_name(k2)]["acc"]
                        e["A3_ci"] = ci(boot[k1] - boot[k2])
                    else:
                        missing.append(label + "|A3")
                out[label] = e
    return out, sorted(set(missing))


def strip_boot(best):
    return {k: {a: b for a, b in v.items() if a != "_boot"} for k, v in best.items()}


def reference_rows(cells, attacker="A4"):
    """Cells of the non-adaptive reference attacker (A4), reported in their own rows, never in the strongest."""
    return {n: c for n, c in cells.items() if n.split("|")[2] == attacker}


def _name(key):
    return "|".join(str(x) for x in key)


def _gname(g):
    return "|".join(str(x) for x in g)


# --- secondary and diagnostics -------------------------------------------------------------------------------------

def split_by_rebuilt(results, R, cells):
    """Full-text accuracy of every cell among writers whose rebuilt draft matches the distributed text (after
    whitespace normalisation) and among the others, with intervals on the same resamples."""
    match = np.array([bool(r.get("rebuilt_match")) for r in results])
    out = {"writers_match": int(match.sum()), "writers_mismatch": int((~match).sum()), "cells": {}}
    for name in cells:
        parts = name.split("|")
        if parts[0] != "full" or "of" in cells[name]:
            continue
        key = (parts[0], parts[1], parts[2]) + tuple(int(x) for x in parts[3:])
        v = cell_matrix(results, key)
        e = {}
        for label, m in (("match", match), ("mismatch", ~match)):
            w = np.where(m, v, np.nan)
            n = int(np.sum(~np.isnan(w)))
            e[label] = {"acc": float(np.nanmean(w)) if n else None, "writers": n,
                        "ci": ci(_boot_mean(w, R)) if n else None}
        out["cells"][name] = e
    return out


def auc(pos, neg):
    """P(pos < neg) + P(pos = neg) / 2 over all pairs (lower cost = the true text is present)."""
    pos, neg = np.asarray(pos, dtype=float), np.asarray(neg, dtype=float)
    if not len(pos) or not len(neg):
        return np.nan
    r = rankdata(np.concatenate([pos, neg]))
    u = r[len(pos):].sum() - len(neg) * (len(neg) + 1) / 2.0
    a = float(u / (len(pos) * len(neg)))
    return 1 - a if MUTATE == "auc_flip" else a


def open_world(results, R, best, cells, forms, n_open):
    """Open-world AUC per form (full text, N = n_open) for the attacker selected by the point estimate, with an
    interval on the same resamples; the point AUC of every adaptive attacker is added."""
    out = {}
    for f in forms:
        name = "full|%s|%d" % (f, n_open)
        if name not in best:
            continue
        att = best[name]["attacker"]
        if f == "R3-u" and att == "A3":
            att = R3U_A3[0] if MUTATE == "open_world_r3u_sum" else r3u_a3_version(cells, "full", n_open)
        per = [r.get("open_world", {}).get((f, att)) for r in results]
        if not any(per):
            continue
        lens = np.array([len(p) if p else 0 for p in per], dtype=np.int64)
        pos = np.array([a for p in per if p for a, _ in p], dtype=float)
        neg = np.array([b for p in per if p for _, b in p], dtype=float)
        start = np.concatenate([[0], np.cumsum(lens)[:-1]])
        point = auc(pos, neg)
        bs = []
        for row in R:
            ix = np.repeat(start[row], lens[row]) + _ranges(lens[row])
            if MUTATE == "open_world_offsets":
                ix = np.repeat(start[row], lens[row])
            bs.append(auc(pos[ix], neg[ix]))
        bs = np.array(bs)
        each = {}
        atts = sorted({a for r in results for (ff, a) in r.get("open_world", {}) if ff == f})
        for a in atts:
            pp = [r["open_world"].get((f, a)) for r in results]
            each[a] = auc(np.concatenate([np.array([x for x, _ in p], dtype=float) for p in pp if p]),
                          np.concatenate([np.array([y for _, y in p], dtype=float) for p in pp if p]))
        out[name] = {"attacker": best[name]["attacker"], "costs_of": att, "auc": point, "ci": ci(bs),
                     "draws": int(lens.sum()), "auc_per_attacker": each}
    return out


def _ranges(lens):
    """[0..l0-1, 0..l1-1, ...] for the lengths."""
    if not len(lens) or lens.sum() == 0:
        return np.zeros(0, dtype=np.int64)
    ends = np.cumsum(lens)
    return np.arange(ends[-1]) - np.repeat(ends - lens, lens)


def window_bias(results):
    """Per form and k: the A2 cost per word at the true windows next to the A2 cost per word of the whole record
    (full-text end), pooled; infinite costs are counted, not pooled."""
    out = {}
    forms = sorted({f for r in results for f, _ in r.get("window_bias", {})})
    for f in forms:
        whole = np.array([r["window_bias_full"][f] for r in results if f in r.get("window_bias_full", {})], dtype=float)
        e = {"whole_record": _dist(whole)}
        ks = sorted({k for r in results for ff, k in r.get("window_bias", {}) if ff == f})
        for k in ks:
            v = np.array([x for r in results for x in r.get("window_bias", {}).get((f, k), [])], dtype=float)
            e["true_window_k%d" % k] = _dist(v)
        out[f] = e
    return out


def _dist(v):
    fin = v[np.isfinite(v)]
    return {"n": int(len(fin)), "infinite": int(np.sum(~np.isfinite(v))),
            "mean": float(fin.mean()) if len(fin) else None,
            "p10_p50_p90": [float(np.quantile(fin, q)) for q in (0.1, 0.5, 0.9)] if len(fin) else None}


# --- utility -------------------------------------------------------------------------------------------------------

def spearman(a, b):
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3:
        return np.nan
    x, y = rankdata(a[ok]), rankdata(b[ok])
    if x.std() == 0 or y.std() == 0:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def _spearman_rows(X, Y):
    """Spearman per row of X and Y (pairwise complete); rows without nan are computed together."""
    out = np.full(X.shape[0], np.nan)
    clean = ~(np.isnan(X).any(axis=1) | np.isnan(Y).any(axis=1))
    if clean.any() and X.shape[1] >= 3:
        rx, ry = rankdata(X[clean], axis=1), rankdata(Y[clean], axis=1)
        rx -= rx.mean(axis=1, keepdims=True)
        ry -= ry.mean(axis=1, keepdims=True)
        den = np.sqrt((rx ** 2).sum(axis=1) * (ry ** 2).sum(axis=1))
        with np.errstate(invalid="ignore", divide="ignore"):
            out[clean] = np.where(den > 0, (rx * ry).sum(axis=1) / np.where(den > 0, den, 1), np.nan)
    for i in np.where(~clean)[0]:
        out[i] = spearman(X[i], Y[i])
    return out


def _nanq_rows(M, q):
    with np.testing.suppress_warnings() as sup:
        sup.filter(RuntimeWarning)
        return np.nanquantile(M, q, axis=1)


def _mean_range_ci(per_p, boot_rows):
    """Mean and range over prompts of per-prompt values, and the interval of the mean over the resamples."""
    pv = [x for x in per_p.values() if x is not None and not np.isnan(x)]
    B_ = np.array(boot_rows, dtype=float)  # (prompts, resamples)
    with np.testing.suppress_warnings() as sup:
        sup.filter(RuntimeWarning)
        bm = np.nanmean(B_, axis=0) if B_.size else np.array([])
    # the mean is over the prompts with a value; how many there were, and in how many resamples a prompt had none
    return {"by_prompt": {p: _f(x) for p, x in per_p.items()},
            "mean": _f(np.mean(pv)) if pv else None,
            "range": [_f(min(pv)), _f(max(pv))] if pv else None,
            "prompts_with_value": len(pv),
            "resamples_with_a_prompt_missing": int(np.sum(np.isnan(B_).any(axis=0))) if B_.size else 0,
            "ci": ci(bm) if bm.size else None}


def utility_summary(results, scores, forms_list, R, cols):
    """Per metric and form, each per prompt and then the mean and range over prompts with the interval of the mean
    (preregistration, "Utility"): (a) Spearman with R0, (b) the ratio to R0 (median, 10th and 90th percentiles),
    (c) Spearman with the human score. Writers dropped from the ratio are counted on both sides: R0 value 0 or
    undefined, and the form's value undefined while R0 has one."""
    prompts = np.array([r["prompt"] for r in results])
    ps = sorted(set(prompts.tolist()))
    sc = np.array(scores, dtype=float)
    out = {}
    for m in utility.METRICS:
        r0 = np.array([_val(r, "R0", m) for r in results])
        r0_ok = (~np.isnan(r0)) & (r0 != 0)
        for f in forms_list:
            cellv = utility.cell(m, f)
            v = np.array([_val(r, f, m) for r in results])
            ratio = np.where(r0_ok & ~np.isnan(v), v / np.where(r0_ok, r0, 1.0), np.nan)
            if MUTATE == "utility_ratio_pooled":
                ratio = np.full_like(ratio, np.nanmedian(ratio) if np.any(~np.isnan(ratio)) else np.nan)
            sr, ss, rq = {}, {}, {q: {} for q in (0.5, 0.1, 0.9)}
            bsr, bss, brq = [], [], {q: [] for q in (0.5, 0.1, 0.9)}
            for p in ps:
                ix = np.where(prompts == p)[0]
                sr[p] = spearman(r0[ix], v[ix])
                ss[p] = spearman(sc[ix], v[ix])
                rp = ratio[ix][~np.isnan(ratio[ix])]
                for q in rq:
                    rq[q][p] = float(np.quantile(rp, q)) if len(rp) else np.nan
                Rp = R if MUTATE == "utility_rp_all" else R[:, cols[p]]
                bsr.append(_spearman_rows(r0[Rp], v[Rp]))
                bss.append(_spearman_rows(sc[Rp], v[Rp]))
                for q in rq:
                    brq[q].append(_nanq_rows(ratio[Rp], q))
            out["%s|%s" % (m, f)] = {
                "cell": cellv,
                "spearman_r0": _mean_range_ci(sr, bsr),
                "spearman_score": _mean_range_ci(ss, bss),
                "ratio_median": _mean_range_ci(rq[0.5], brq[0.5]),
                "ratio_p10": _mean_range_ci(rq[0.1], brq[0.1]),
                "ratio_p90": _mean_range_ci(rq[0.9], brq[0.9]),
                "ratio_dropped_r0": int(np.sum(~r0_ok)),
                "ratio_dropped_form": int(np.sum(r0_ok & np.isnan(v))),
                "ratio_dropped_by_prompt": {p: [int(np.sum(~r0_ok[prompts == p])),
                                                int(np.sum((r0_ok & np.isnan(v))[prompts == p]))] for p in ps},
            }
    fig = {}
    for f in forms_list:
        vals, undefined = [], 0
        for m in utility.METRICS:
            e = out["%s|%s" % (m, f)]
            mean = e["spearman_r0"]["mean"]
            undefined += e["cell"] != utility.NONE and mean is None
            vals.append(0.0 if e["cell"] == utility.NONE or mean is None else mean)
        cells = [utility.cell(m, f) for m in utility.METRICS]
        # computed metrics whose correlation is undefined in every prompt also count as 0; their number is shown
        fig[f] = {"median_spearman_r0": float(np.median(vals)), "ok": cells.count(utility.OK),
                  "approx": cells.count(utility.APPROX), "none": cells.count(utility.NONE),
                  "computed_but_undefined": int(undefined)}
    return out, fig


def _val(r, f, m):
    v = r["utility"].get(f, {}).get(m)
    return np.nan if v is None else float(v)


def _f(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else float(x)
