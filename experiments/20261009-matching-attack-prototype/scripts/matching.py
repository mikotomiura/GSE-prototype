"""Closed-set matching of k-trial records against N candidate tuples (design.md sections 5 and 6; goals 2 and 3).

  matching.py --trials raw/trials.json --prepare results/prepare.json --dist-dir raw/dist
              --dist-summary results/distances.json --out results/matching.json [--processes 4]

Cell = (k, N). Records are the windows of k consecutive scored trials (skipped scenarios removed) inside a block.
For each window the N - 1 decoy tuples are drawn once and shared by every attacker and variant: position i is
drawn uniformly and independently from the pool of the trial's scenario; a tuple whose typed readings equal the
truth at every position, or that repeats an earlier decoy tuple, is drawn again (for k = 1: N - 1 distinct
phrases whose typed reading differs from the truth's). The attacker chooses the candidate with the smallest
distance; a tie of m candidates that includes the truth scores 1/m. The order of the candidates plays no part.

Attackers and variants (config.json "variants"):
  L  per-trial key count of the record against the whole reading's standard key count of the candidate (L1);
     none / bin w (floor(value / w)) / bin inf (every value 0) / merge m (sums of m consecutive trials; null:
     the total) / sort (the k values sorted)
  S  the sum of the per-trial distances of raw/dist (distances.py)
Diagnostics for every cell: a random choice, a choice that ignores the record (the candidate whose key counts
are closest to the median of its pool), and a negative control in which each trial of the record is replaced by
a trial of the same scenario from another block (for L_none and S_no_time).

Intervals: percentile bootstrap over the blocks (the windows of a block are dependent), the same resamples for
every cell and variant. Standard library only (multiprocessing over the cells; the output does not depend on
the number of processes).
"""
import argparse
import operator
import os
import random
import statistics
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402
import data as dataload  # noqa: E402

FORMAT = "matching-attack/1"
TAG = "matching-attack"
_add, _sub = operator.add, operator.sub


# ---------------------------------------------------------------- records and candidates
def windows_of(trials, k):
    """[(block_id, start, [trial indices])]: every run of k consecutive trials inside one block, in plan order."""
    by_block = {}
    order = []
    for i, t in enumerate(trials):
        if t["block_id"] not in by_block:
            by_block[t["block_id"]] = []
            order.append(t["block_id"])
        by_block[t["block_id"]].append(i)
    out = []
    for b in order:
        idx = by_block[b]
        for s in range(len(idx) - k + 1):
            out.append((b, s, idx[s:s + k]))
    return out


def draw_decoys(rng, N, pool_sizes, typed_pos, truth_typed):
    """N - 1 decoy tuples of pool indices (see the module docstring). Returns (tuples, number redrawn)."""
    k = len(pool_sizes)
    below = kitload.below
    # tuples a decoy may take: all tuples minus those typing the truth at every position
    same = 1
    total = 1
    for i in range(k):
        same *= sum(1 for t in typed_pos[i] if t == truth_typed[i])
        total *= pool_sizes[i]
    if total - same < N - 1:
        raise ValueError("too few tuples with a typed reading different from the truth (N = %d)" % N)
    if k == 1:
        tt = truth_typed[0]
        tp = typed_pos[0]
        elig = [j for j in range(pool_sizes[0]) if tp[j] != tt]
        if len(elig) < N - 1:
            raise ValueError("too few phrases with a typed reading different from the truth (N = %d)" % N)
        for i in range(N - 1):
            j = i + below(rng, len(elig) - i)
            elig[i], elig[j] = elig[j], elig[i]
        return [(j,) for j in elig[:N - 1]], 0
    seen = set()
    out = []
    redrawn = 0
    while len(out) < N - 1:
        tup = tuple(below(rng, pool_sizes[i]) for i in range(k))
        if tup in seen or all(typed_pos[i][tup[i]] == truth_typed[i] for i in range(k)):
            redrawn += 1
            continue
        seen.add(tup)
        out.append(tup)
    return out, redrawn


def credit(true_score, scores):
    """1 when the truth alone is closest, 1/m when it is one of m closest, 0 otherwise."""
    best = min(scores) if scores else true_score
    if true_score < best:
        return 1.0
    if true_score > best:
        return 0.0
    return 1.0 / (1 + scores.count(true_score))


def pick_swap(rng, same_scenario, trials, block):
    """A trial drawn uniformly among `same_scenario` (indices of the trials of one scenario) outside `block`."""
    if all(trials[u]["block_id"] == block for u in same_scenario):
        raise ValueError("no trial of this scenario outside the block")
    while True:
        u = same_scenario[kitload.below(rng, len(same_scenario))]
        if trials[u]["block_id"] != block:
            return u


def column_sum(cols):
    """Element-wise sum of equally long lists."""
    acc = list(cols[0])
    for col in cols[1:]:
        acc = list(map(_add, acc, col))
    return acc


# ---------------------------------------------------------------- the L variants
def l_value(v, variant):
    kind = variant["kind"]
    if kind == "bin":
        return 0 if variant["w"] is None else v // variant["w"]
    return v


def l_scores(variant, x, rcols, rtrue):
    """(truth score, decoy scores) of an L variant. x: record values; rcols[i]: the decoys' standard key counts at
    position i; rtrue[i]: the truth's."""
    kind = variant["kind"]
    if kind in ("none", "bin"):
        cols = []
        tscore = 0
        for xi, col, ri in zip(x, rcols, rtrue):
            xv = l_value(xi, variant)
            cols.append([abs(l_value(r, variant) - xv) for r in col])
            tscore += abs(l_value(ri, variant) - xv)
        return tscore, column_sum(cols)
    if kind == "merge":
        m = variant["m"] or len(x)
        cols = []
        tscore = 0
        for g in range(0, len(x), m):
            xg = sum(x[g:g + m])
            gsum = column_sum(rcols[g:g + m])
            cols.append([abs(v - xg) for v in gsum])
            tscore += abs(sum(rtrue[g:g + m]) - xg)
        return tscore, column_sum(cols)
    if kind == "sort":
        sx = sorted(x)
        tscore = sum(map(abs, map(_sub, sorted(rtrue), sx)))
        scores = [sum(map(abs, map(_sub, sorted(vals), sx))) for vals in zip(*rcols)]
        return tscore, scores
    raise ValueError("unknown L variant kind %s" % kind)


def s_scores(dists, tids, jcols, true_js):
    """(truth score, decoy scores) of an S variant: per-trial distance arrays summed over the positions."""
    tscore = 0
    cols = []
    for t, col, tj in zip(tids, jcols, true_js):
        dv = dists[t]
        cols.append(list(map(dv.__getitem__, col)))
        tscore += dv[tj]
    return tscore, column_sum(cols)


# ---------------------------------------------------------------- bootstrap
def boot_multiplicities(seed, n_blocks, B):
    rng = random.Random(kitload.seed_int(seed, TAG, "bootstrap"))
    out = []
    for _ in range(B):
        m = [0] * n_blocks
        for _ in range(n_blocks):
            m[kitload.below(rng, n_blocks)] += 1
        out.append(m)
    return out


def summarise(credits, wblocks, block_index, mults, chance, ci):
    """acc, its percentile bootstrap interval over the blocks, the excess over chance and the ratio to chance."""
    nb = len(block_index)
    sums = [0.0] * nb
    cnts = [0] * nb
    for c, b in zip(credits, wblocks):
        sums[block_index[b]] += c
        cnts[block_index[b]] += 1
    n = len(credits)
    acc = sum(credits) / n
    out = {"acc": acc, "excess": acc - chance, "ratio": acc / chance}
    if sum(1 for c in cnts if c) < 2:
        out.update({"ci": [None, None], "excess_ci": [None, None], "ci_status": "fewer_than_two_blocks"})
        return out
    boots = []
    for m in mults:
        den = sum(map(operator.mul, m, cnts))
        if den:
            boots.append(sum(map(operator.mul, m, sums)) / den)
    boots.sort()
    lo = kitload.percentile(boots, (1 - ci) / 2)
    hi = kitload.percentile(boots, 1 - (1 - ci) / 2)
    out.update({"ci": [lo, hi], "excess_ci": [lo - chance, hi - chance], "ci_status": "ok",
                "n_boot_used": len(boots)})
    return out


# ---------------------------------------------------------------- one cell
_D = {}


def _init(trials_path, prepare_path, dist_dir, dist_summary):
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg)
    names = [n for n, v in cfg["variants"].items() if v["attacker"] == "S"]
    d = dataload.load(cfg, kit, trials_path, prepare_path, dist_dir, dist_summary, names)
    by_sc = {}
    for i, t in enumerate(d["trials"]):
        by_sc.setdefault(t["scenario"], []).append(i)
    med = dict((s, statistics.median_low(list(r))) for s, r in d["R"].items())
    blocks = []
    for t in d["trials"]:
        if not blocks or blocks[-1] != t["block_id"]:
            if t["block_id"] in blocks:
                raise ValueError("the trials of a block are not contiguous")
            blocks.append(t["block_id"])
    _D.update({"cfg": cfg, "d": d, "by_sc": by_sc, "med": med, "seed": kitload.read_seed(),
               "block_index": dict((b, i) for i, b in enumerate(blocks))})
    _D["mults"] = boot_multiplicities(_D["seed"], len(blocks), cfg["bootstrap"])


def run_cell(task):
    kitload.check_init()
    k, N = task
    cfg, d, seed = _D["cfg"], _D["d"], _D["seed"]
    trials, pools, typed, R, true_j = d["trials"], d["pools"], d["typed"], d["R"], d["true_j"]
    variants = cfg["variants"]
    names = list(variants)
    wins = windows_of(trials, k)
    credits = dict((n, []) for n in names)
    diag = dict((n, []) for n in ("random", "typical", "swap_L_none", "swap_S_no_time"))
    by_sc = {}
    redrawn = 0
    below = kitload.below
    for b, st, tids in wins:
        scs = [trials[t]["scenario"] for t in tids]
        rng = random.Random(kitload.seed_int(seed, TAG, "decoys", k, N, b, st))
        decoys, nre = draw_decoys(rng, N, [len(pools[s]) for s in scs], [typed[s] for s in scs],
                                  [trials[t]["typed"] for t in tids])
        redrawn += nre
        jcols = [list(col) for col in zip(*decoys)]
        tjs = [true_j[t] for t in tids]
        x = [trials[t]["c"] for t in tids]
        rcols = [list(map(R[s].__getitem__, col)) for s, col in zip(scs, jcols)]
        rtrue = [R[s][j] for s, j in zip(scs, tjs)]
        for name in names:
            v = variants[name]
            if v["attacker"] == "L":
                ts, sc = l_scores(v, x, rcols, rtrue)
            else:
                ts, sc = s_scores(d["dist"][name], tids, jcols, tjs)
            c = credit(ts, sc)
            credits[name].append(c)
            if k == 1:
                e = by_sc.setdefault(name, {}).setdefault(scs[0], [0.0, 0])
                e[0] += c
                e[1] += 1
        # diagnostics
        rr = random.Random(kitload.seed_int(seed, TAG, "random", k, N, b, st))
        diag["random"].append(1.0 if below(rr, N) == 0 else 0.0)
        med = [_D["med"][s] for s in scs]
        tcols = [[abs(r - m) for r in col] for col, m in zip(rcols, med)]
        diag["typical"].append(credit(sum(abs(r - m) for r, m in zip(rtrue, med)), column_sum(tcols)))
        rs = random.Random(kitload.seed_int(seed, TAG, "swap", k, N, b, st))
        swapped = [pick_swap(rs, _D["by_sc"][s], trials, b) for s in scs]
        xs = [trials[u]["c"] for u in swapped]
        ts, sc = l_scores(variants["L_none"], xs, rcols, rtrue)
        diag["swap_L_none"].append(credit(ts, sc))
        ts, sc = s_scores(d["dist"]["S_no_time"], swapped, jcols, tjs)
        diag["swap_S_no_time"].append(credit(ts, sc))
    chance = 1.0 / N
    wblocks = [w[0] for w in wins]
    res = {"k": k, "N": N, "chance": chance, "n_windows": len(wins), "n_blocks": len(set(wblocks)),
           "n_decoys_redrawn": redrawn, "results": {}, "diagnostics": {}}
    for name in names:
        res["results"][name] = summarise(credits[name], wblocks, _D["block_index"], _D["mults"], chance,
                                         cfg["ci"])
    for name, cr in diag.items():
        res["diagnostics"][name] = summarise(cr, wblocks, _D["block_index"], _D["mults"], chance, cfg["ci"])
    if k == 1:
        res["by_scenario"] = dict((name, dict((s, {"acc": v[0] / v[1], "n": v[1]}) for s, v in sorted(m.items())))
                                  for name, m in by_sc.items())
    return res


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--trials", required=True)
    ap.add_argument("--prepare", required=True)
    ap.add_argument("--dist-dir", required=True)
    ap.add_argument("--dist-summary", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--processes", type=int, default=4)
    ap.add_argument("--only", default=None, help="k:N cells to compute (for trying the code; not for results)")
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    args = tuple(os.path.abspath(p) for p in (a.trials, a.prepare, a.dist_dir, a.dist_summary))
    cells = [(k, N) for k in cfg["windows"]["k"] for N in cfg["N"]]
    if a.only:
        want = set(tuple(int(v) for v in c.split(":")) for c in a.only.split(","))
        cells = [c for c in cells if c in want]
    order = sorted(cells, key=lambda c: -(c[0] * c[1]))   # the largest cells first
    with Pool(a.processes, initializer=kitload.guarded_init, initargs=(_init,) + args) as pool:
        done = {}
        for r in pool.imap_unordered(run_cell, order):
            done[(r["k"], r["N"])] = r
            print("  k=%d N=%d: L_none %.4f  S_no_time %.4f  (%d windows)" % (
                r["k"], r["N"], r["results"]["L_none"]["acc"], r["results"]["S_no_time"]["acc"],
                r["n_windows"]), flush=True)
    prep, _ = kitload.read_json(a.prepare)
    dsum, dsha = kitload.read_json(a.dist_summary)
    out = {"format": FORMAT, "seed": kitload.read_seed(), "config_sha256": kitload.sha256_file(kitload.CONFIG),
           "trials_json_sha256": prep["trials_json_sha256"], "distances_json_sha256": dsha,
           "n_blocks_with_windows": max(r["n_blocks"] for r in done.values()),
           "cells": [done[c] for c in cells]}
    if a.only:
        out["partial"] = True
    kitload.write_json(a.out, out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except kitload.CheckError as e:
        print("!! %s" % e, file=sys.stderr)
        sys.exit(1)
