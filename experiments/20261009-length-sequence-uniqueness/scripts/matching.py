"""Measure 2: closed-set matching of a record against N candidate texts (design.md section 7).

  matching.py --derived raw/derived --stats results/corpus_stats.json --config config.json --seed-file SEED
              --out results/matching.json [--processes 4]

Cell = (segmentation, k, N). For each cell the candidate sets and the true candidate are drawn once
(section 7.1) and shared by every noise condition. Candidates come from N different works chosen uniformly
without replacement among the works that have a valid window of k segments; inside a work the window is
uniform among its valid windows; the true candidate is uniform among the N. The record is the true window
typed by the writer of the condition; the attacker computes every candidate with the standard table and
chooses the smallest L1 distance; a tie of m candidates that includes the true one scores 1/m.

Intervals: percentile bootstrap over the true works (clusters), shared resamples across conditions.
Standard library only (multiprocessing for the cells).
"""
import argparse
import hashlib
import json
import math
import operator
import os
import random
import sys
from array import array
from collections import OrderedDict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from romaji_table import HABITS, unit_keys  # noqa: E402
from build_segments import expected_sha, load_derived, sha256_file, unpack  # noqa: E402  (no SudachiPy import)


def seed_int(*parts):
    return int.from_bytes(hashlib.sha256(":".join(str(p) for p in parts).encode("utf-8")).digest()[:8], "big")


def bs_prob(share, r_bar, kana_fraction):
    """Per-unit error probability that gives a BackSpace share `share` of (text keys + BackSpace)."""
    if share <= 0:
        return 0.0
    extra_text = (1 - kana_fraction) * 1 + kana_fraction * r_bar
    return share * r_bar / (1 - share * (extra_text + 1))


def noisy_counts(unit_strings, cond, p_bs, kana_fraction, rng):
    """Key counts (text keys minus BackSpace) of the segments as typed by one writer of the condition.
    The random draws are made in a fixed order: the five habits, then per segment the BackSpace draws
    unit by unit, then the shift."""
    habits = frozenset(h for h in HABITS if rng.random() < cond["habit_prob"])
    out = []
    for s in unit_strings:
        parts = unit_keys(s, habits) if s else []
        c = sum(len(p) for p in parts)
        if p_bs > 0:
            for p in parts:
                if rng.random() < p_bs and rng.random() < kana_fraction:
                    c += len(p) - 1
        if cond["shift_prob"] > 0 and rng.random() < cond["shift_prob"]:
            c += 1 if rng.random() < 0.5 else -1
            if c < 0:
                c = 0
        out.append(c)
    return out


def draw_trial(rs, eligible, starts, N):
    """One trial of section 7.1: N different works uniformly without replacement among `eligible`, one
    window uniformly inside each, and the index of the true candidate uniformly among the N."""
    ws = rs.sample(eligible, N)
    wins = [rs.choice(starts[w]) for w in ws]
    true = rs.randrange(N)
    return ws, wins, true


def credit_l1(rec, cands, true):
    sub, ab = operator.sub, abs
    dists = [sum(map(ab, map(sub, rec, c))) for c in cands]
    best = min(dists)
    if dists[true] != best:
        return 0.0
    return 1.0 / dists.count(best)


# ---------------------------------------------------------------- per-process data
_DATA = {}


def _load(derived, name, stats):
    """The corpus of one segmentation, kept between cells of the same process. The cache key holds the
    file's path, its current SHA-256 and the value recorded in corpus_stats.json, so another corpus, a
    changed file or a changed record is loaded (and checked) again."""
    path = os.path.abspath(os.path.join(derived, "corpus_%s.pkl" % name))
    key = (path, sha256_file(path), expected_sha(stats, path))
    if _DATA.get("key") != key:
        _DATA.clear()
        d = load_derived(derived, "corpus", name, stats)
        _DATA.update({"key": key, "work_ids": d["work_ids"], "keys": d["keys"], "units": d["units"],
                      "cache": OrderedDict()})
    return _DATA


def _units(data, w):
    cache = data["cache"]
    if w in cache:
        cache.move_to_end(w)
        return cache[w]
    v = unpack(data["units"][w])
    cache[w] = v
    if len(cache) > 64:
        cache.popitem(last=False)
    return v


def valid_starts(keys, k):
    """Start positions of the windows of k consecutive valid segments of one work."""
    out = array("i")
    run = 0
    for i in range(len(keys) - 1, -1, -1):
        run = run + 1 if keys[i] >= 0 else 0
        if run >= k:
            out.append(i)
    out.reverse()
    return out


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def run_cell(task):
    derived, stats, name, k, N, mcfg, seed, r_bar = task
    data = _load(derived, name, stats)
    keys = data["keys"]
    starts = [valid_starts(kk, k) for kk in keys]
    eligible = [w for w in range(len(keys)) if len(starts[w])]
    cell = {"definition": name, "k": k, "N": N, "eligible_works": len(eligible), "chance": 1.0 / N}
    if len(eligible) < N:
        cell["status"] = "not computable (fewer eligible works than N)"
        return cell
    T = mcfg["trials"]
    conds = mcfg["conditions"]
    kana_fraction = mcfg["bs_kana_level_fraction"]
    p_bs = {c: bs_prob(v["bs_share"], r_bar, kana_fraction) for c, v in conds.items()}
    rs = random.Random(seed_int(seed, "struct", name, k, N))
    rd = random.Random(seed_int(seed, "diag", name, k, N))
    names = list(conds)
    credits = {c: [] for c in names}
    diag = {"random": [], "max_windows": []}
    true_works, true_index = [], [0] * N
    for t in range(T):
        ws, wins, true = draw_trial(rs, eligible, starts, N)
        cands =[tuple(keys[w][i:i + k]) for w, i in zip(ws, wins)]
        tw, ti = ws[true], wins[true]
        true_works.append(tw)
        true_index[true] += 1
        att_u, wr_u = None, None
        for c in names:
            cond = conds[c]
            if cond["reading"] == "plain" and cond["habit_prob"] == 0 and p_bs[c] == 0 and cond["shift_prob"] == 0:
                credits[c].append(1.0 / cands.count(cands[true]))
                continue
            if att_u is None:
                a, w = _units(data, tw)
                att_u, wr_u = a[ti:ti + k], w[ti:ti + k]
            rng = random.Random(seed_int(seed, "noise", name, k, N, c, t))
            rec = noisy_counts(wr_u if cond["reading"] == "writer" else att_u, cond, p_bs[c], kana_fraction, rng)
            credits[c].append(credit_l1(rec, cands, true))
        pick = rd.randrange(N)
        diag["random"].append(1.0 if pick == true else 0.0)
        sizes = [len(starts[w]) for w in ws]
        top = max(sizes)
        diag["max_windows"].append(1.0 / sizes.count(top) if sizes[true] == top else 0.0)

    # cluster bootstrap over the true works, the same resamples for every condition
    clusters = sorted(set(true_works))
    pos = {w: j for j, w in enumerate(clusters)}
    C = len(clusters)
    n_c = [0] * C
    for w in true_works:
        n_c[pos[w]] += 1
    series = OrderedDict((c, credits[c]) for c in names)
    series["diag_random"] = diag["random"]
    series["diag_max_windows"] = diag["max_windows"]
    sums = {}
    for s, vals in series.items():
        acc = [0.0] * C
        for w, v in zip(true_works, vals):
            acc[pos[w]] += v
        sums[s] = acc
    rb = random.Random(seed_int(seed, "boot", name, k, N))
    boots = {s: [] for s in series}
    rng_idx = range(C)
    for _ in range(mcfg["bootstrap"]):
        idx = rb.choices(rng_idx, k=C)
        n = sum(n_c[j] for j in idx)
        for s in series:
            acc = sums[s]
            boots[s].append(sum(acc[j] for j in idx) / n)
    lo_q, hi_q = (1 - mcfg["ci"]) / 2, 1 - (1 - mcfg["ci"]) / 2
    out = {}
    for s, vals in series.items():
        b = sorted(boots[s])
        acc = sum(vals) / len(vals)
        lo, hi = percentile(b, lo_q), percentile(b, hi_q)
        out[s] = {"acc": acc, "ci": [lo, hi], "excess": acc - 1.0 / N,
                  "excess_ci": [lo - 1.0 / N, hi - 1.0 / N]}
    expected = T / N
    chi2 = sum((o - expected) ** 2 / expected for o in true_index)
    cell.update({
        "status": "ok",
        "trials": T,
        "true_works_distinct": C,
        "p_bs": p_bs,
        "results": {c: out[c] for c in names},
        "diagnostics": {
            "random_predictor": out["diag_random"],
            "max_windows_predictor": out["diag_max_windows"],
            "true_index_chi2": chi2,
            "true_index_df": N - 1,
            "true_index_z": (chi2 - (N - 1)) / math.sqrt(2 * (N - 1)) if N > 1 else None,
        },
    })
    return cell


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--derived", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--seed-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--processes", type=int, default=4)
    ap.add_argument("--only", default=None, help="comma-separated definitions (for testing)")
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config, encoding="utf-8"))
    mcfg = cfg["matching"]
    seed = open(a.seed_file, encoding="utf-8").read().strip()
    r_bar = json.load(open(a.stats, encoding="utf-8"))["r_bar"]
    defs = cfg["segmentation"]["definitions"] if not a.only else a.only.split(",")
    tasks = [(a.derived, a.stats, name, k, N, mcfg, seed, r_bar) for name in defs for k in mcfg["k"] for N in mcfg["N"]]
    # heavy cells first so that the pool stays busy; the output order does not depend on this
    tasks.sort(key=lambda t: -(t[3] * t[4]))
    if a.processes > 1:
        with Pool(a.processes) as pool:
            cells = []
            for cell in pool.imap_unordered(run_cell, tasks):
                cells.append(cell)
                print("matching: %s k=%d N=%d %s" % (cell["definition"], cell["k"], cell["N"], cell["status"]),
                      flush=True)
    else:
        cells = [run_cell(t) for t in tasks]
    order = {name: i for i, name in enumerate(defs)}
    cells.sort(key=lambda c: (order[c["definition"]], c["k"], c["N"]))
    res = {"format": "matching/1", "seed": seed, "r_bar": r_bar, "config": mcfg, "cells": cells}
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
