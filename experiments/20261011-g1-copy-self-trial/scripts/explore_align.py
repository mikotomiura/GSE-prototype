"""Post-hoc exploration (not in preregistration.md; notes.md "逸脱" 3): an attacker that tolerates inserted and
missing boundaries.

  explore_align.py --work <dir outside the repository> --copy results/copy_segments.json --corpus raw/corpus_g1.json
                   --corpus-stats results/corpus_g1_stats.json --out results/explore_align.json [--processes 4]

L_align scores a candidate by the alignment cost of align.py (groups (1,1), (2,1), (1,2), (3,1), (1,3), cost
|sum difference| + 8 per extra segment in a group) between the record window and the candidate window, both used
from the first to the last segment. The windows, the truths and the decoys are those of matching.py (the same
seeds), restricted to the first 10 draws per window; L_none is scored again on the same draws for comparison.
The attacker does not know the alignment of the record with the text. Copy blocks, plain record, N = 100 and 1,000.

Both attackers are also reported split by whether the window holds a record segment of a group that is not 1:1 in
the alignment of the whole block with the text (an inserted or a missing boundary): "clean" windows hold none.
"""
import argparse
import os
import statistics
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matching  # noqa: E402
from align import ORDER, align  # noqa: E402
from common import check_corpus_current, load_config, read_json, read_seed, seed_int, write_json  # noqa: E402

DRAWS = 10
NS = (100, 1000)


def align_cost(x, C, lam):
    """Global alignment cost of record window x (k,) against each row of C (n, k), both fully used."""
    k = len(x)
    n = C.shape[0]
    px = np.concatenate([[0], np.cumsum(x)])
    pc = np.concatenate([np.zeros((n, 1), dtype=np.int64), np.cumsum(C, axis=1)], axis=1)
    INF = np.iinfo(np.int64).max // 4
    cost = np.full((k + 1, k + 1, n), INF, dtype=np.int64)
    cost[0, 0] = 0
    for i in range(k + 1):
        for j in range(k + 1):
            if i == 0 and j == 0:
                continue
            best = np.full(n, INF, dtype=np.int64)
            for p, q in ORDER:
                i0, j0 = i - p, j - q
                if i0 < 0 or j0 < 0:
                    continue
                prev = cost[i0, j0]
                c = prev + np.abs((px[i] - px[i0]) - (pc[:, j] - pc[:, j0])) + lam * (p - 1 + q - 1)
                c = np.where(prev >= INF, INF, c)
                best = np.minimum(best, c)
            cost[i, j] = best
    return cost[k, k]


_G = {}


def _init(*args):
    matching._init(*args)


def run_task(task):
    matching.check_init()
    label, k, N = task
    g = matching._G
    cfg, seed, corpus, y = g["cfg"], g["seed"], g["corpus"], g["y"]
    lam = cfg["alignment"]["lambda"]
    x_all = np.asarray(g["recs"][label]["plain"], dtype=np.int64)
    groups = align(list(int(v) for v in x_all), list(int(v) for v in y), lam, cfg["alignment"]["max_group"])
    irregular = set()
    for i0, i1, j0, j1 in groups:
        if (i1 - i0, j1 - j0) != (1, 1):
            irregular.update(range(i0, i1))
    out = {"L_align": [], "L_none": [], "clean": []}
    for i, t in matching.window_truths(list(x_all), y, k, "copy", cfg):
        out["clean"].append(not any(j in irregular for j in range(i, i + k)))
        x = x_all[i:i + k]
        va, vn = [], []
        for d in range(DRAWS):
            rng = np.random.default_rng(seed_int(seed, "decoy", "copy", label, k, N, i, d))
            D = corpus.draw(rng, k, N - 1)
            ts = int(align_cost(x, t[None, :], lam)[0])
            va.append(matching.credit(ts, align_cost(x, D, lam)))
            vn.append(matching.credit(*matching.scores({"kind": "none"}, x, t, D)))
        out["L_align"].append(statistics.fmean(va))
        out["L_none"].append(statistics.fmean(vn))
    return task, out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--copy", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--corpus-stats", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--processes", type=int, default=4)
    a = ap.parse_args(argv)
    cfg = load_config()
    seed = read_seed()
    cstats = check_corpus_current(cfg, a.corpus_stats, a.corpus, a.copy)
    blocks = cfg["records"]["copy_blocks"]
    tasks = [(lab, k, N) for k in cfg["matching"]["k"] for N in NS for lab in blocks]
    args = (a.corpus, a.copy, a.work, cfg, seed, cstats["median_valid"])
    if a.processes > 1:
        with Pool(a.processes, initializer=_init, initargs=args) as pool:
            done = pool.map(run_task, tasks, chunksize=1)
    else:
        _init(*args)
        done = [run_task(t) for t in tasks]
    acc = {}
    for (lab, k, N), out in done:
        flags = out.pop("clean")
        for v, means in out.items():
            sub = {}
            for name, keep in (("clean", True), ("irregular", False)):
                m = [x for x, f in zip(means, flags) if f == keep]
                sub[name] = {"windows": len(m), "acc": statistics.fmean(m) if m else None}
            acc.setdefault((v, k, N), {})[lab] = {"windows": len(means), "acc": statistics.fmean(means) if means else None,
                                                  "split": sub}
    cells = []
    for (v, k, N), bl in sorted(acc.items()):
        vals = [b["acc"] for b in bl.values() if b["acc"] is not None]
        split = {}
        n_all = sum(b["windows"] for b in bl.values())
        hit_all = sum(b["acc"] * b["windows"] for b in bl.values() if b["windows"])
        for name in ("clean", "irregular"):
            n = sum(b["split"][name]["windows"] for b in bl.values())
            hit = sum(b["split"][name]["acc"] * b["split"][name]["windows"] for b in bl.values() if b["split"][name]["windows"])
            split[name] = {"windows": n, "acc_pooled": hit / n if n else None}
        cells.append({"variant": v, "k": k, "N": N, "chance": 1.0 / N, "blocks": bl, "split_pooled_windows": split,
                      "overall_pooled": hit_all / n_all if n_all else None, "windows": n_all,
                      "overall": statistics.fmean(vals) if vals else None,
                      "min": min(vals) if vals else None, "max": max(vals) if vals else None})
    write_json(a.out, {"format": "g1-explore-align/1", "draws_per_window": DRAWS, "seed": seed,
                       "corpus_sha256": cstats["corpus_sha256"], "cells": cells})
    print("explore_align: %d cells" % len(cells))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
