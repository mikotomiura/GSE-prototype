"""Exploratory analysis 1 (decisions 55 and 56; notes.md, "Exploratory analyses"; exploratory.json unicity): the
uniqueness of a window of k word lengths among N candidate texts. Not in the preregistration; not used for the main
conclusions. Reads the distributed texts only (the logs are read only to apply the registered exclusion). Writes
aggregates only.

    python -I scripts/exploratory_unicity.py --source klicke --root raw/klicke/extracted/WritingTask \
        --out results/exploratory_unicity.json [--workers 12]
    python -I scripts/exploratory_unicity.py --source synthetic --out <file>   # the self-test corpus

- words: runs of letters and digits; a length is the number of letters and digits of a word (attackers.Cand);
- windows: k = 1..50; per writer and k, 5 starts without replacement among the n - k + 1 starts (all when fewer),
  seed use exploratory_unicity (prompt, writer, k);
- candidates: the decoys of the main full-text matching (matching.draw_decoys, seed use decoys); draws 20, 20, 5;
- unique: no decoy contains the sequence at any position; credit: 1/m among the m candidates that contain it;
- per writer: the mean over starts and draws; the interval: the resamples of the main computation (aggregate.resamples
  with the sample name main500 or all);
- reference: plug-in conditional entropies of word lengths of order 0, 1 and 2 (pooled over all texts after
  exclusion, pairs and triples within a text) and k* = log2 N / h.
A window is matched exactly: each k-gram is keyed by two independent 64-bit polynomial hashes of its lengths (a
collision of both is not checked; its probability is negligible at these sizes).
"""
import argparse
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import attackers as A  # noqa: E402
import corpus  # noqa: E402
import matching  # noqa: E402
import seeds  # noqa: E402

KMAX = 50
STARTS = 5
NS = (10, 100, 1000)
MUTATE = os.environ.get("UNI_MUTATE", "")
_B1, _B2 = np.uint64(1000003), np.uint64(998244353)


def _hashes(lens, k):
    """Two hashes of every k-gram of lens (arrays of length n - k + 1)."""
    x = np.asarray(lens, dtype=np.uint64) + np.uint64(1)
    n = len(x) - k + 1
    if n <= 0:
        return np.zeros(0, np.uint64), np.zeros(0, np.uint64)
    h1 = np.zeros(n, np.uint64)
    h2 = np.zeros(n, np.uint64)
    with np.errstate(over="ignore"):
        for t in range(k):
            h1 = h1 * _B1 + x[t:t + n]
            h2 = h2 * _B2 + (x[t:t + n] * np.uint64(7) + np.uint64(3))
    return h1, h2


def pool_index(pool_lens, k):
    """Sorted arrays (h1, h2, owner) of the distinct k-grams of each pool text."""
    keys, owners = [], []
    for j, lens in enumerate(pool_lens):
        h1, h2 = _hashes(lens, k)
        if not len(h1):
            continue
        u = np.unique(np.stack([h1, h2], axis=1), axis=0)
        keys.append(u)
        owners.append(np.full(len(u), j, dtype=np.int64))
    K = np.concatenate(keys)
    O = np.concatenate(owners)
    order = np.lexsort((O, K[:, 1], K[:, 0]))
    return K[order, 0], K[order, 1], O[order]


def owners_of(index, h1, h2):
    """The pool indices whose text contains the k-gram (h1, h2)."""
    H1, H2, O = index
    a = np.searchsorted(H1, h1, side="left")
    b = np.searchsorted(H1, h1, side="right")
    return O[a:b][H2[a:b] == h2]


def window_starts(seed, p, wid, k, n):
    """5 starts without replacement among n (all when n <= 5), seed use exploratory_unicity."""
    if n <= STARTS or MUTATE == "first_starts":
        return list(range(min(n, STARTS)))
    g = seeds.rng(seed, "exploratory_unicity", p, wid, "", k)
    return sorted(int(i) for i in g.choice(n, STARTS, replace=False))


def prompt_values(task):
    """{writer: {(k, N): (mean unique, mean credit)}} for the writers of one prompt."""
    seed, p, ids, pool_lens, ks = task
    draws = {}
    for me, wid in enumerate(ids):
        for N in NS:
            ds = []
            for d in range(matching.DRAWS[N]):
                dec = matching.draw_decoys(seed, p, wid, N, ids, {me}, d)
                if dec is None:
                    break
                m = np.zeros(len(ids), dtype=bool)
                m[dec[0]] = True
                ds.append(m)
            draws[(me, N)] = ds
    out = {wid: {} for wid in ids}
    for k in ks:
        index = pool_index(pool_lens, k)
        for me, wid in enumerate(ids):
            lens = pool_lens[me]
            n = len(lens) - k + 1
            if n <= 0:
                continue
            starts = window_starts(seed, p, wid, k, n)
            h1, h2 = _hashes(lens, k)
            owners = [owners_of(index, h1[s], h2[s]) for s in starts]
            for N in NS:
                ds = draws[(me, N)]
                if not ds:
                    continue
                u = c = 0.0
                for o in owners:
                    if len(o) == 1 and o[0] == me and MUTATE != "count_self":
                        u += len(ds)
                        c += len(ds)
                        continue
                    for m in ds:
                        hit = int(m[o].sum()) + (1 if MUTATE == "count_self" else 0)
                        u += hit == 0
                        c += 1.0 / (1 + hit)
                out[wid][(k, N)] = (u / (len(owners) * len(ds)), c / (len(owners) * len(ds)))
    return p, out


def entropies(all_lens):
    """Plug-in entropies (bits per word): H(L), H(L_t | L_t-1), H(L_t | L_t-2, L_t-1)."""
    from collections import Counter

    def H(c):
        n = sum(c.values())
        return -sum(v / n * math.log2(v / n) for v in c.values())

    c1, c2, c3, p1, p2 = Counter(), Counter(), Counter(), Counter(), Counter()
    for lens in all_lens:
        c1.update(lens)
        c2.update(zip(lens, lens[1:]))
        p1.update(lens[:-1])
        c3.update(zip(lens, lens[1:], lens[2:]))
        p2.update(zip(lens, lens[1:-1]))
    return {"h0": H(c1), "h1": H(c2) - H(p1), "h2": H(c3) - H(p2)}


def load(args, seed):
    if args.source == "synthetic":
        ws = corpus.synthetic_corpus(seed, prompts=4, per_prompt=args.per_prompt, tag="main")
    else:
        import load_klicke
        ws, _ = load_klicke.load(args.root)
    kept, excluded = [], {}
    for w in ws:
        if w.extra.get("log_path"):
            import load_klicke
            load_klicke.fill_rows(w)
        w.rows = corpus.active_rows(w.rows)
        w.text = (w.text or "").replace("\r\n", "\n")
        why = corpus.exclusion_reason(w)
        w.rows = []
        if why:
            excluded[why] = excluded.get(why, 0) + 1
        else:
            kept.append(w)
    return kept, excluded


def summarise(values, keys, R, ks):
    out = {}
    for N in NS:
        e = {"k": [], "unique": [], "unique_ci": [], "credit": [], "credit_ci": [], "writers": []}
        for k in ks:
            u = np.array([values[key].get((k, N), (np.nan, np.nan))[0] for key in keys])
            c = np.array([values[key].get((k, N), (np.nan, np.nan))[1] for key in keys])
            if np.all(np.isnan(u)):
                continue
            e["k"].append(k)
            e["unique"].append(float(np.nanmean(u)))
            e["unique_ci"].append(aggregate.ci(aggregate._boot_mean(u, R)))
            e["credit"].append(float(np.nanmean(c)))
            e["credit_ci"].append(aggregate.ci(aggregate._boot_mean(c, R)))
            e["writers"].append(int(np.sum(~np.isnan(u))))
        out[str(N)] = e
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="klicke")
    ap.add_argument("--root", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--per-prompt", type=int, default=40)
    ap.add_argument("--per-prompt-sample", type=int, default=125)
    ap.add_argument("--kmax", type=int, default=KMAX)
    args = ap.parse_args()
    seed = seeds.read_seed()
    kept, excluded = load(args, seed)
    by_prompt = {}
    for w in kept:
        by_prompt.setdefault(w.prompt, {})[w.writer] = w
    prompts = sorted(by_prompt)
    pool_ids = {p: sorted(by_prompt[p]) for p in prompts}
    pool_lens = {p: [A.Cand(by_prompt[p][wid].text).lens for wid in pool_ids[p]] for p in prompts}
    ks = list(range(1, args.kmax + 1))
    sample = matching.eval_sample(seed, {p: list(by_prompt[p]) for p in prompts}, args.per_prompt_sample)
    tasks = [(seed, p, pool_ids[p], pool_lens[p], ks) for p in prompts]
    if args.workers > 1:
        with ProcessPoolExecutor(min(args.workers, len(tasks))) as ex:
            res = list(ex.map(prompt_values, tasks))
    else:
        res = [prompt_values(t) for t in tasks]
    values = {(p, wid): v for p, out in res for wid, v in out.items()}
    out = {"source": args.source, "excluded": excluded, "writers_after_exclusion": {p: len(pool_ids[p]) for p in prompts},
           "kmax": args.kmax, "starts_per_writer": STARTS, "N": list(NS)}
    samples = {"main500": sorted((p, w) for p, ids in sample.items() for w in ids),
               "all": sorted((p, w) for p in prompts for w in pool_ids[p])}
    for name, keys in samples.items():
        R, _ = aggregate.resamples(seed, [p for p, _ in keys], name)
        out[name] = summarise(values, keys, R, ks)
    h = entropies([l for p in prompts for l in pool_lens[p]])
    out["entropy_bits_per_word"] = h
    out["k_star"] = {str(N): {o: (math.log2(N) / v if v > 0 else None) for o, v in h.items()} for N in NS}
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
