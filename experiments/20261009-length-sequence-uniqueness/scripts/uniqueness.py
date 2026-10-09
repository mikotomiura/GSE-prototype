"""Measure 1: the fraction of windows of k segment lengths whose sequence occurs once in the corpus
(design.md section 6). Standard library only.

  uniqueness.py --derived raw/derived --config config.json --out results/uniqueness.json

A window is k consecutive valid segments inside one work. Its sequence is compared by a polynomial hash
modulo 2^61-1 of the k key counts (base larger than any count, so two different sequences of the same k
collide only through the modulus; a collision can only make a window look non-unique). Counting is done
in 16 buckets of the hash to keep memory low.
"""
import argparse
import json
import os
import pickle
import sys
from array import array
from collections import Counter

MOD = (1 << 61) - 1
BASE = (1 << 20) + 7
BUCKETS = 16


def load(derived, role, name):
    with open(os.path.join(derived, "%s_%s.pkl" % (role, name)), "rb") as f:
        d = pickle.load(f)
    return d["work_ids"], d["keys"]


def concat(keys_list):
    """One array with -1 between works (a window never crosses a work)."""
    x = array("i")
    for keys in keys_list:
        x.extend(keys)
        x.append(-1)
    return x


def valid_runs(x):
    """r[i] = number of consecutive valid segments starting at i."""
    n = len(x)
    r = array("i", [0]) * (n + 1)
    for i in range(n - 1, -1, -1):
        r[i] = r[i + 1] + 1 if x[i] >= 0 else 0
    return r


def count_unique(hashes):
    """(number of windows whose hash occurs once, number of distinct hashes)."""
    parts = [array("q") for _ in range(BUCKETS)]
    for h in hashes:
        parts[h & (BUCKETS - 1)].append(h)
    once = distinct = 0
    for p in parts:
        c = Counter(p)
        distinct += len(c)
        once += sum(1 for v in c.values() if v == 1)
    return once, distinct


def measure(keys_list, ks):
    x = concat(keys_list)
    if max(x, default=0) >= BASE:
        raise SystemExit("uniqueness: a key count reaches the hash base")
    runs = valid_runs(x)
    h = array("q", [0]) * len(x)
    idx = array("i", (i for i in range(len(x)) if runs[i] >= 1))
    out = []
    kmax = max(ks)
    for k in range(1, kmax + 1):
        idx = array("i", (i for i in idx if runs[i] >= k))
        for i in idx:
            h[i] = (h[i] * BASE + x[i + k - 1] + 1) % MOD
        if k in ks:
            once, distinct = count_unique(h[i] for i in idx)
            n = len(idx)
            out.append({"k": k, "windows": n, "unique": once, "distinct": distinct,
                        "unique_fraction": once / n if n else None,
                        "distinct_per_window": distinct / n if n else None})
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--derived", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config, encoding="utf-8"))
    ks = set(cfg["uniqueness"]["k"])
    sizes = cfg["selection"]["nested_sizes"]
    defs = cfg["segmentation"]["definitions"]
    res = {"format": "uniqueness/1", "k": sorted(ks), "results": []}
    for name in defs:
        wids, keys = load(a.derived, "corpus", name)
        for size in sizes:
            sub = keys[:size]
            r = measure(sub, ks)
            res["results"].append({"definition": name, "corpus": "first_%d" % size, "works": len(sub),
                                   "valid_segments": sum(sum(1 for v in kk if v >= 0) for kk in sub),
                                   "by_k": r})
            print("uniqueness: %s first_%d done" % (name, size), flush=True)
        rw, rkeys = load(a.derived, "reference", name)
        res["results"].append({"definition": name, "corpus": "reference_ime12", "works": len(rkeys),
                               "valid_segments": sum(sum(1 for v in kk if v >= 0) for kk in rkeys),
                               "by_k": measure(rkeys, ks)})
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
