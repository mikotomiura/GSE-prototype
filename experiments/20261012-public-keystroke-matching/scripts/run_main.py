"""The main computation (preregistration.md). Writes aggregates only.

    python scripts/run_main.py --source synthetic --out results/main_synthetic.json [--workers 16] [--all]

--source synthetic builds a small corpus of synthetic writers (no human data) to exercise the whole pipeline; the
KLiCKe loader is written at check 2 after acquisition. --all adds the appendix sample of all writers after exclusion.
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import attackers as A  # noqa: E402
import corpus  # noqa: E402
import evaluate  # noqa: E402
import forms  # noqa: E402
import matching  # noqa: E402
import seeds  # noqa: E402
import utility  # noqa: E402

MUTATE = os.environ.get("MAIN_MUTATE", "")


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise ValueError("duplicate keys in config.json: %s" % dup)
    return dict(pairs)


def load_config():
    with open(os.path.join(HERE, "..", "config.json"), encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=_no_duplicate_keys)


def load_writers(source, seed, args):
    if source == "synthetic":
        return corpus.synthetic_corpus(seed, prompts=4, per_prompt=args.per_prompt, tag="main")
    raise SystemExit("source %r: the loader is written at check 2 after acquisition" % source)


def prepare(writers):
    kept, excluded = [], {}
    for w in writers:
        w.rows = corpus.active_rows(w.rows)
        w.text = (w.text or "").replace("\r\n", "\n")
        why = corpus.exclusion_reason(w)
        if why:
            excluded[why] = excluded.get(why, 0) + 1
        else:
            kept.append(w)
    return kept, excluded


def build_models(train, seed, cfg):
    """Per fold: the character-pair table (R0), the A2-b boundary model (R3-u), the R3-u length term and the R7
    duration regressions (training logs with the same processing). The training writers are taken in the order of
    (prompt, writer), so that the models do not depend on the order of the loader."""
    if MUTATE != "train_unsorted":
        train = sorted(train, key=lambda w: (w.prompt, w.writer))
    digraph = A.DigraphTable([w.rows for w in train], cfg["attackers"]["A3"]["min_digraph_count"])
    pairs = [(w.rows, forms.release(w.rows, "R3-u", seed, w.prompt, w.writer)) for w in train]
    boundary = A.BoundaryModel(pairs, cfg)
    diffs = [len(A.r3u_replay(r3u)) - A.Cand(w.text).nchars for w, (_, r3u) in zip(train, pairs)]
    length = A.LengthTerm(diffs)
    r7 = {}
    for p in cfg["release_forms"]["R7"]["suppress_p"]:
        prs = []
        for w in train:
            rel = forms.release(w.rows, "R7(%s)" % p, seed, w.prompt, w.writer)
            c = A.Cand(w.text)
            segs, al = A.r7_alignments(rel, [c], cfg)
            if al[0][1] is not None:
                prs.extend(A.r7_segment_pairs(segs, rel.times(), al[0][1], c))
        r7[p] = A.R7Duration(prs)
    return {"digraph": digraph, "boundary": boundary, "length": length, "r7": r7}


_CTX = None


def _init(ctx):
    global _CTX
    _CTX = ctx


def _work(task):
    w, windows, keep_costs = task
    _CTX.windows, _CTX.keep_costs = windows, keep_costs
    return evaluate.evaluate_writer(w, _CTX)


def run(args):
    t0 = time.time()
    cfg = load_config()
    seed = seeds.read_seed()
    writers, excluded = prepare(load_writers(args.source, seed, args))
    by_prompt = {}
    for w in writers:
        by_prompt.setdefault(w.prompt, {})[w.writer] = w
    prompts = sorted(by_prompt)
    fold_a, fold_b = matching.split_folds(seed, prompts)
    fold_of_prompt = {p: (0 if p in fold_a else 1) for p in prompts}
    folds = (fold_a, fold_b)
    models = {}
    for f in (0, 1):
        eval_ids = {wid for p in folds[f] for wid in by_prompt[p]}
        train = [w for p in folds[1 - f] for w in by_prompt[p].values() if w.writer not in eval_ids]
        models[f] = build_models(train, seed, cfg)
    pool_ids = {p: sorted(by_prompt[p]) for p in prompts}
    pools = {p: [A.Cand(by_prompt[p][wid].text) for wid in pool_ids[p]] for p in prompts}
    task_max = {p: max(utility.interval_max(forms.release(by_prompt[p][wid].rows, "R0", seed, p, wid))
                       for wid in pool_ids[p]) for p in prompts}
    sample = matching.eval_sample(seed, {p: list(by_prompt[p]) for p in prompts}, args.per_prompt_sample)
    sample_set = {(p, wid) for p, ids in sample.items() for wid in ids}
    nc_b = {}
    for p, ids in sample.items():
        for wid in ids:
            others = [x for x in pool_ids[p] if x != wid]
            nc_b[(p, wid)] = others[int(seeds.rng(seed, "negative_control", p, wid).integers(0, len(others)))]
    # only the records of the B writers return cost vectors (main forms, adaptive attackers)
    need_costs = {(p, b) for (p, _), b in nc_b.items()}
    n_values = [int(n) for n in cfg["matching"]["N"]]
    if args.open_world_n not in n_values:
        raise SystemExit("--open-world-n must be one of the registered N %s" % n_values)
    ctx = evaluate.Context(cfg, seed, pools, pool_ids, models, task_max, fold_of_prompt, forms.ALL, n_values,
                           nc_forms=forms.MAIN, open_world_n=args.open_world_n)
    tasks = []
    for p in prompts:
        for wid in pool_ids[p]:
            in_sample = (p, wid) in sample_set
            if in_sample or (p, wid) in need_costs or args.all:
                tasks.append((by_prompt[p][wid], in_sample or args.all, (p, wid) in need_costs))
    results = {}
    if args.workers > 1:
        with ProcessPoolExecutor(args.workers, initializer=_init, initargs=(ctx,)) as ex:
            for t, r in zip(tasks, ex.map(_work, tasks, chunksize=1)):
                results[(r["prompt"], r["writer"])] = r
    else:
        _init(ctx)
        for t in tasks:
            r = _work(t)
            results[(r["prompt"], r["writer"])] = r
    out = {"source": args.source, "seed_file_sha256": _sha(os.path.join(HERE, "..", "SEED")),
           "config_sha256": _sha(os.path.join(HERE, "..", "config.json")),
           "writers_after_exclusion": {p: len(pool_ids[p]) for p in prompts}, "excluded": excluded,
           "folds": [fold_a, fold_b], "sample_sizes": {p: len(v) for p, v in sample.items()},
           "open_world_n": args.open_world_n}
    strongest = {"full": evaluate.STRONGEST_FULL, "window": evaluate.STRONGEST_WINDOW}
    samples = {"main500": sorted(sample_set)}
    if args.all:
        samples["all"] = sorted((p, w) for p in prompts for w in pool_ids[p])
    for name, keys in samples.items():
        res = [results[k] for k in keys]
        R, cols = aggregate.resamples(seed, [r["prompt"] for r in res], name)
        out[name] = summarise_sample(res, R, cols, strongest, cfg, ctx.open_world_n,
                                     [by_prompt[r["prompt"]][r["writer"]].score for r in res])
        if name == "main500":
            best = out[name].pop("_best")
            out[name]["negative_control"] = negative_control(res, results, nc_b, pool_ids, seed, R, strongest, best,
                                                             out[name]["cells"])
        out[name].pop("_best", None)
    out["seconds"] = None if args.no_timing else round(time.time() - t0, 1)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(_clean(out), f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", args.out, "tasks", len(tasks))


def summarise_sample(res, R, cols, strongest, cfg, open_world_n, scores):
    """Every aggregate of one sample (500 writers or all writers). '_best' keeps the strongest attacker with its
    resamples for the negative control; the caller removes it before writing."""
    cells, best, boot = aggregate.summarise_cells(res, R, strongest)
    con, missing = aggregate.contrasts(best, cells, boot, [tuple(c) for c in cfg["contrasts"]], forms.ALL)
    out = {"cells": cells, "strongest": aggregate.strip_boot(best), "contrasts": con, "contrasts_missing": missing,
           "reference_A4": aggregate.reference_rows(cells), "counts": _counts(res),
           "rebuilt_split": aggregate.split_by_rebuilt(res, R, cells),
           "open_world": aggregate.open_world(res, R, best, cells, forms.ALL, open_world_n),
           "window_bias": aggregate.window_bias(res), "_best": best}
    out["utility"], out["utility_figure"] = aggregate.utility_summary(res, scores, forms.ALL, R, cols)
    return out


def negative_control(res, results, nc_b, pool_ids, seed, R, strongest, main_best, main_cells, Ns=(10, 1000)):
    """The record of A is replaced by the record of B (same prompt, evaluation fold); the true text stays A's; decoys
    exclude A and B. Main forms x adaptive attackers x N = 10 and 1000 x full text. The strongest attacker is fixed
    to the one selected by the point estimate of the main computation (same form and N, full text, 500 writers);
    it is not selected again here (preregistration, "Diagnostics"). On R3-u, "A3" is fixed to the version (sum or
    mean) with the larger point estimate in the main computation, so that the maximum of the two versions is not
    taken again here either. Every adaptive attacker is also reported."""
    fake = []
    for r in res:
        p, a = r["prompt"], r["writer"]
        b = nc_b[(p, a)]
        ids = pool_ids[p]
        me, bi = ids.index(a), ids.index(b)
        costs_b = results[(p, b)]["costs"]
        cells = {}
        for N in Ns:
            for d in range(matching.DRAWS[N]):
                dec = matching.draw_decoys(seed, p, a, N, ids, {me, bi}, d)
                if dec is None:
                    break
                cand = [me] + dec[0]
                for f in costs_b:
                    for att, cv in costs_b[f].items():
                        evaluate._add(cells, ("full", f, att, N), matching.credit_stats(0, cv[cand]))
        evaluate._finish(cells)
        fake.append({"prompt": p, "writer": a, "full": cells, "window": {}})
    cells, nc_best, boot = aggregate.summarise_cells(fake, R, strongest)
    fixed = {}
    nc_forms = {f for r in res for f in results[(r["prompt"], nc_b[(r["prompt"], r["writer"])])]["costs"]}
    for name, e in sorted(main_best.items()):
        scope, f, N = name.split("|")[0], name.split("|")[1], name.split("|")[2:]
        if scope != "full" or f not in nc_forms or len(N) != 1 or int(N[0]) not in Ns:
            continue
        att = e["attacker"]
        if MUTATE == "nc_reselect" and name in nc_best:
            att = nc_best[name]["attacker"]
            fixed[name] = {"attacker": att, "acc": nc_best[name]["acc"], "ci": aggregate.ci(nc_best[name]["_boot"]),
                           "x_chance": nc_best[name]["x_chance"], "chance": 1.0 / int(N[0])}
            continue
        costs_of = att
        if f == "R3-u" and att == "A3" and MUTATE != "nc_r3u_composite":
            costs_of = aggregate.r3u_a3_version(main_cells, "full", int(N[0]))
        key = ("full", f, costs_of, int(N[0]))
        c = cells.get(aggregate._name(key))
        if c is None:
            fixed[name] = {"attacker": att, "costs_of": costs_of, "missing": True}
            continue
        fixed[name] = {"attacker": att, "costs_of": costs_of, "acc": c["acc"], "ci": c["ci"],
                       "x_chance": c["x_chance"], "chance": 1.0 / int(N[0])}
    return {"fixed_attacker": fixed, "cells": cells}


def _counts(res):
    out = {}
    for r in res:
        for k, v in r["counts"].items():
            out[k] = out.get(k, 0) + v
    return out


def _sha(path):
    import hashlib
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _clean(x):
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return None if np.isnan(v) else (round(v, 6) if np.isfinite(v) else str(v))
    if isinstance(x, np.integer):
        return int(x)
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="synthetic")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--per-prompt", type=int, default=40, help="synthetic writers per prompt")
    ap.add_argument("--per-prompt-sample", type=int, default=125)
    ap.add_argument("--open-world-n", type=int, default=evaluate.OPEN_WORLD_N,
                    help="N of the open-world diagnostic (1000 as registered; smaller only for the self-test)")
    ap.add_argument("--no-timing", action="store_true", help="omit the run time so that reruns are byte-identical")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
