"""Closed-set matching of the copy blocks' record windows against N candidates (preregistration.md, "照合" and
"診断").

  matching.py --work <dir outside the repository> --copy results/copy_segments.json --corpus raw/corpus_g1.json
              --corpus-stats results/corpus_g1_stats.json --out results/matching.json [--processes 4]

A window is k consecutive record segments of one block (every start). The truth is the k text segments from
the text position aligned with the window's first segment (align.py; control blocks: the text window with the
same index, the last one when it would run past the end). Decoys: N - 1 works drawn uniformly without
replacement among the works with a valid window of length k, one valid window uniform inside each; 50 draws per
window. The attacker chooses the candidate with the smallest L1 distance after the variant's processing; a tie
of m candidates that includes the truth scores 1/m. The order of the candidates plays no part.

Output: aggregates only (accuracy per block and over blocks, Monte Carlo standard errors).
"""
import argparse
import math
import os
import statistics
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align import align, start_map  # noqa: E402
from common import check_corpus_current, load_config, read_json, read_seed, seed_int, sha256_file, write_json  # noqa: E402


# ---------------------------------------------------------------- processing and scoring
def process(a, variant):
    """Processed values (last axis = the k positions). a: int array (..., k)."""
    kind = variant["kind"]
    if kind == "none":
        return a
    if kind == "bin":
        return np.zeros_like(a) if variant["w"] is None else np.floor_divide(a, variant["w"])
    if kind == "merge":
        k = a.shape[-1]
        m = variant["m"] or k
        return np.stack([a[..., g:g + m].sum(axis=-1) for g in range(0, k, m)], axis=-1)
    if kind == "sort":
        return np.sort(a, axis=-1)
    raise ValueError("unknown variant kind %s" % kind)


def scores(variant, x, t, D):
    """(truth score, decoy scores) of one variant. x, t: (k,), D: (N-1, k)."""
    px = process(x, variant)
    ts = int(np.abs(process(t, variant) - px).sum())
    ds = np.abs(process(D, variant) - px).sum(axis=-1)
    return ts, ds


def credit(ts, ds):
    """1 when the truth alone is closest, 1/m when it is one of m closest, 0 otherwise."""
    best = ds.min() if ds.size else ts
    if ts < best:
        return 1.0
    if ts > best:
        return 0.0
    return 1.0 / (1 + int((ds == ts).sum()))


# ---------------------------------------------------------------- corpus windows
class Corpus(object):
    def __init__(self, keys_per_work):
        self.big = np.concatenate([np.asarray(ks, dtype=np.int64) for ks in keys_per_work])
        lens = [len(ks) for ks in keys_per_work]
        self.off = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(np.int64)
        self.lens = np.asarray(lens, dtype=np.int64)
        self._k = {}

    def windows(self, k):
        """(eligible works, per-work count of valid starts, flat start positions, per-work offset into them)."""
        if k in self._k:
            return self._k[k]
        counts, flat = [], []
        invalid = (self.big < 0).astype(np.int64)
        cum = np.concatenate([[0], np.cumsum(invalid)])
        for w in range(len(self.lens)):
            o, n = int(self.off[w]), int(self.lens[w])
            if n < k:
                counts.append(0)
                continue
            s = np.arange(o, o + n - k + 1)
            ok = (cum[s + k] - cum[s]) == 0
            st = s[ok]
            counts.append(len(st))
            flat.append(st)
        counts = np.asarray(counts, dtype=np.int64)
        flat = np.concatenate(flat) if flat else np.zeros(0, dtype=np.int64)
        soff = np.concatenate([[0], np.cumsum(counts)[:-1]]).astype(np.int64)
        eligible = np.nonzero(counts > 0)[0]
        self._k[k] = (eligible, counts, flat, soff)
        return self._k[k]

    def draw(self, rng, k, n):
        eligible, counts, flat, soff = self.windows(k)
        if len(eligible) < n:
            raise ValueError("fewer eligible works than N - 1")
        works = rng.choice(eligible, size=n, replace=False)
        idx = rng.integers(0, counts[works])
        pos = flat[soff[works] + idx]
        return self.big[pos[:, None] + np.arange(k)]


# ---------------------------------------------------------------- tasks
_G = {}


def _init(*args):
    """Pool initializer. An exception here would make the pool respawn workers forever, so it is kept and
    raised by the first task instead."""
    try:
        _load(*args)
    except BaseException as ex:  # noqa: BLE001 - re-raised as RuntimeError in run_task
        _G["init_error"] = "%s: %s" % (type(ex).__name__, ex)


def _load(corpus_path, copy_path, work, cfg, seed, median):
    keys = read_json(corpus_path)["keys"]
    _G.update({"corpus": Corpus(keys), "y": np.asarray(read_json(copy_path)["keys"], dtype=np.int64),
               "recs": read_json(os.path.join(work, "records.json"))["blocks"], "cfg": cfg, "seed": seed,
               "median": median})


def window_truths(x, y, k, kind, cfg):
    """[(start, truth vector)] of the windows of one record."""
    T = len(y)
    out = []
    if kind == "control":
        for i in range(len(x) - k + 1):
            j = min(i, T - k)
            out.append((i, y[j:j + k]))
        return out
    sm = start_map(align(list(x), list(int(v) for v in y), cfg["alignment"]["lambda"], cfg["alignment"]["max_group"]))
    for i in range(len(x) - k + 1):
        j = sm[i]
        if j + k <= T:
            out.append((i, y[j:j + k]))
    return out


def check_init():
    if "init_error" in _G:
        raise RuntimeError("worker initialisation failed: %s" % _G["init_error"])


def run_task(task):
    check_init()
    kind, label, k, N = task
    cfg, seed, corpus, y = _G["cfg"], _G["seed"], _G["corpus"], _G["y"]
    rec_key = "clean" if kind == "clean" else "plain"
    x_all = np.asarray(_G["recs"][label][rec_key], dtype=np.int64)
    if kind == "copy":
        names = [v for v, d in cfg["variants"].items() if d["record"] == "plain"] + ["no_record"]
    elif kind == "clean":
        names = [v for v, d in cfg["variants"].items() if d["record"] == "clean"]
    else:
        names = list(cfg["control_variants"])
    D_draws = cfg["matching"]["draws_per_window"]
    target = k * _G["median"]
    per = {n: {"mean": [], "var": []} for n in names}
    for i, t in window_truths(list(x_all), y, k, kind, cfg):
        x = x_all[i:i + k]
        vals = {n: [] for n in names}
        for d in range(D_draws):
            rng = np.random.default_rng(seed_int(seed, "decoy", kind, label, k, N, i, d))
            D = corpus.draw(rng, k, N - 1)
            for n in names:
                if n == "no_record":
                    ts = abs(float(t.sum()) - target)
                    ds = np.abs(D.sum(axis=1).astype(float) - target)
                    vals[n].append(credit(ts, ds))
                else:
                    vals[n].append(credit(*scores(cfg["variants"][n], x, t, D)))
        for n in names:
            per[n]["mean"].append(statistics.fmean(vals[n]))
            per[n]["var"].append(statistics.variance(vals[n]))  # sample variance of the draws
    return task, per


def block_summary(per, D_draws):
    m = per["mean"]
    if not m:
        return {"windows": 0, "acc": None, "mc_se": None}
    se = math.sqrt(sum(v / D_draws for v in per["var"])) / len(m)
    return {"windows": len(m), "acc": statistics.fmean(m), "mc_se": se}


def combine(blocks):
    """Mean over the blocks that have windows (equal weight per block)."""
    vals = [b["acc"] for b in blocks.values() if b["acc"] is not None]
    ses = [b["mc_se"] for b in blocks.values() if b["acc"] is not None]
    if not vals:
        return {"acc": None, "n_blocks": 0}
    out = {"acc": statistics.fmean(vals), "n_blocks": len(vals), "min": min(vals), "max": max(vals),
           "mc_se": math.sqrt(sum(s * s for s in ses)) / len(vals)}
    for person in ("P009", "P010"):
        pv = [b["acc"] for lab, b in blocks.items() if lab.startswith(person) and b["acc"] is not None]
        out[person] = statistics.fmean(pv) if pv else None
    return out


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
    rc = cfg["records"]
    tasks = []
    for k in cfg["matching"]["k"]:
        for N in cfg["matching"]["N"]:
            tasks += [("copy", lab, k, N) for lab in rc["copy_blocks"]]
            tasks += [("clean", lab, k, N) for lab in rc["copy_blocks"]]
            tasks += [("control", lab, k, N) for lab in rc["control_blocks"]]
    args = (a.corpus, a.copy, a.work, cfg, seed, cstats["median_valid"])
    if a.processes > 1:
        with Pool(a.processes, initializer=_init, initargs=args) as pool:
            done = pool.map(run_task, tasks, chunksize=1)
    else:
        _init(*args)
        done = [run_task(t) for t in tasks]
    D_draws = cfg["matching"]["draws_per_window"]
    acc = {}
    for (kind, label, k, N), per in done:
        for name, p in per.items():
            group = "control" if kind == "control" else ("diagnostic" if name == "no_record" else "main")
            acc.setdefault((group, name, k, N), {})[label] = block_summary(p, D_draws)
    cells = []
    for (group, name, k, N), blocks in sorted(acc.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3])):
        cells.append({"group": group, "variant": name, "k": k, "N": N, "chance": 1.0 / N,
                      "overall": combine(blocks), "blocks": blocks})
    write_json(a.out, {"format": "g1-matching/1", "seed": seed, "config_sha256": sha256_file(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")),
        "corpus_sha256": cstats["corpus_sha256"], "draws_per_window": D_draws, "cells": cells})
    print("matching: %d cells" % len(cells))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
