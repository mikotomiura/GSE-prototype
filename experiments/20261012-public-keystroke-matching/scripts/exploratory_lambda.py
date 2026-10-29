"""Exploratory analyses 6 (the penalty lambda grid) and 7 (A2-scan) of notes.md, "Exploratory analyses, part 3"
(decision 86; decided after the results of the main computation; not preregistered; not used for questions 1 to 4).

Full text, the forms R3, R4(w) and R7(p), N = 10 and 1,000, the 500 writers of the main sample. Analysis 6: A2 (R3,
R4(w), R7(p)) and A1' (R3, R7(p)) with lambda in {2, 4, 8, 16}, through attackers.align_costs as in the main
computation. Analysis 7 (scripts/exploratory_scan.py): A2-scan, the sum over chunks of 20 record values of a
free-start, free-end alignment (align_local.py), with the same lambda. The decoys, draws, credit and resamples are
those of the main computation, from the same seed and the same functions (matching, evaluate, aggregate); the pool
and the sample come from run_main as in run_main.run. Only aggregates are written; no writer ID, no per-writer value.

    python -I scripts/exploratory_lambda.py --source klicke --root raw/klicke/extracted/WritingTask \
        --main-cache raw/derived/main_cache/33fa95833296d7a5 --compare-main results/main.json \
        --cache-dir raw/derived/explore_cache --out results/exploratory_lambda.json --workers 12 [--time-first 10]

Resumable (as run_main, deviation D4): each writer's result is stored under <cache-dir>/<analysis>/<fingerprint>/
when it returns. The fingerprint is this script's own (seed, config, the code of this folder that the run imports,
library versions, the data files, the analysis); run_main.cache_fingerprint is never called and the main cache is
only read. It stops, writing nothing, unless the pool and the sample are those of main.json and every positive
control passes: per writer, A2 and A1' at lambda 8 equal the main cache (N = 10 and 1,000) and A2 at lambda 4 and 16
equal A2-lam4 and A2-lam16 of the main cache (R3 and R4(w), N = 1,000); the cells of those attackers equal main.json;
the strongest attacker of the main attackers, formed again from the main cache, equals main.json. With --time-first n
it evaluates n writers spread over the sample, prints the seconds per writer and writes no output.
"""
import argparse
import hashlib
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import align_local  # noqa: E402
import attackers as A  # noqa: E402
import corpus  # noqa: E402
import dp_utility_r0  # noqa: E402  (load_main_of, _dump: reading the main cache)
import evaluate  # noqa: E402
import forms  # noqa: E402
import matching  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402

MUTATE = os.environ.get("EXL_MUTATE", "")
FORMS = ["R3", "R4(1)", "R4(2)", "R4(4)", "R4(8)", "R7(0.1)", "R7(0.25)", "R7(0.5)"]
LAMS = (2, 4, 8, 16)
NS = (10, 1000)
MAIN_LAM = {4: "A2-lam4", 16: "A2-lam16"}  # the lambda side analysis of the main computation (not on R7)
NOTE = {6: "exploratory analysis 6 (decision 86), decided after the main results, not preregistered; not used for "
           "questions 1 to 4; aggregates only",
        7: "exploratory analysis 7 (decision 86), decided after the main results, not preregistered; not used for "
           "questions 1 to 4; aggregates only"}


def name(attacker, lam):
    return "%s.lam%d" % (attacker, lam)


def variants(analysis):
    """The attacker names of an analysis (every form does not have every one)."""
    if analysis == 6:
        return [name(a, lam) for a in ("A2", "A1p") for lam in LAMS]
    return [name("A2scan", lam) for lam in LAMS]


def costs_of(rel, pool, cfg, analysis, memo):
    """{variant: costs over the pool} for one released record (full text)."""
    out = {}
    for lam in LAMS:
        use = A.LAM if MUTATE == "ignore_lam" else lam
        if analysis == 6:
            if A.applies("A2", rel.base):
                out[name("A2", lam)] = A.align_costs(A.record_values(rel), rel, pool, cfg, lam=use, memo=memo)
            if A.applies("A1p", rel.base):
                out[name("A1p", lam)] = A.align_costs(A.a1_lengths(rel), rel, pool, cfg, lam=use, memo=memo)
        else:
            if "prep" not in memo:
                groups, cap = A._groups(rel, cfg)
                memo["prep"] = (align_local.prepare([A.text_values(c, rel) for c in pool]), groups, cap)
            prep, groups, cap = memo["prep"]
            out[name("A2scan", lam)] = align_local.scan_costs(A.record_values(rel), prep, use, groups, cap)
    return out


class Context:
    def __init__(self, cfg, seed, pools, pool_ids, analysis):
        self.cfg, self.seed, self.pools, self.pool_ids, self.analysis = cfg, seed, pools, pool_ids, analysis


def evaluate_writer(w, ctx):
    """{'prompt', 'writer', 'full': {('full', form, variant, N): stats}, 'counts'} for one writer of the sample: the
    draws and the credit of evaluate.evaluate_writer (full text)."""
    seed, p = ctx.seed, w.prompt
    pool, ids = ctx.pools[p], ctx.pool_ids[p]
    me = ids.index(w.writer)
    costs, memo = {}, {}
    for f in FORMS:
        rel = forms.release(w.rows, f, seed, p, w.writer)
        costs[f] = costs_of(rel, pool, ctx.cfg, ctx.analysis, memo if ctx.analysis == 6 else {})
    res = {"prompt": p, "writer": w.writer, "full": {}, "window": {}, "counts": {}}
    for N in NS:
        for d in range(matching.DRAWS[N]):
            dec = matching.draw_decoys(seed, p, w.writer, N, ids, {me}, d + 1 if MUTATE == "decoy_draw" else d)
            if dec is None:
                res["counts"]["full_too_few_%d" % N] = 1
                break
            cand = [me] + dec[0]
            for f in FORMS:
                for a, cv in costs[f].items():
                    evaluate._add(res["full"], ("full", f, a, N), matching.credit_stats(0, cv[cand]))
    evaluate._finish(res["full"])
    return res


_CTX = None


def _init(ctx):
    global _CTX
    _CTX = ctx


def _work(w):
    run_main._read_active(w)
    try:
        return evaluate_writer(w, _CTX)
    finally:
        run_main._drop_rows(w)


def _exclusion(w):
    """The exclusion reason of run_main.train_contrib (on the active rows), or None."""
    run_main._read_active(w)
    try:
        return corpus.exclusion_reason(w)
    finally:
        run_main._drop_rows(w)


def fingerprint(args, analysis):
    """SHA-256 of what a writer's result depends on (this script's own; not run_main.cache_fingerprint)."""
    import Levenshtein
    import scipy
    import sklearn
    import load_klicke  # noqa: F401
    import synthetic_logs  # noqa: F401
    h = hashlib.sha256()

    def put(k, v):
        h.update(("%s=%s\n" % (k, v)).encode("utf-8"))

    put("seed", run_main._sha(os.path.join(HERE, "..", "SEED")))
    put("config", run_main._sha(os.path.join(HERE, "..", "config.json")))
    code = {os.path.basename(m.__file__) for m in list(sys.modules.values())
            if getattr(m, "__file__", None) and os.path.dirname(os.path.abspath(m.__file__)) == HERE}
    for n in sorted((code | {"exploratory_lambda.py", "align_local.py"}) - {"aggregate.py"}):
        put("code:" + n, run_main._sha(os.path.join(HERE, n)))
    put("versions", (platform.python_version(), np.__version__, scipy.__version__, sklearn.__version__,
                     Levenshtein.__version__))
    put("args", (args.source, args.per_prompt if args.source == "synthetic" else None, analysis, FORMS, LAMS, NS,
                 MUTATE))
    if args.root:
        for rel, p in run_main._files_under(args.root):
            put("data:" + rel, run_main._sha(p))
    return h.hexdigest()


def setup(args, workers):
    """cfg, seed, the pools and the sample as run_main.run builds them; stops unless they are those of main.json."""
    cfg, seed = run_main.load_config(), seeds.read_seed()
    writers = run_main.load_writers(args.source, seed, args)
    for w in writers:
        w.text = (w.text or "").replace("\r\n", "\n")
    order = sorted(writers, key=lambda w: (w.prompt, w.writer))
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            why = list(ex.map(_exclusion, order, chunksize=4))
    else:
        why = [_exclusion(w) for w in order]
    excluded, by_prompt = {}, {}
    for w, y in zip(order, why):
        if y:
            excluded[y] = excluded.get(y, 0) + 1
        else:
            by_prompt.setdefault(w.prompt, {})[w.writer] = w
    prompts = sorted(by_prompt)
    pool_ids = {p: sorted(by_prompt[p]) for p in prompts}
    pools = {p: [A.Cand(by_prompt[p][wid].text) for wid in pool_ids[p]] for p in prompts}
    sample = matching.eval_sample(seed, {p: list(by_prompt[p]) for p in prompts}, args.per_prompt_sample)
    return cfg, seed, by_prompt, pool_ids, pools, sample, excluded


def evaluate_all(ws, ctx, workers, cache):
    """{(prompt, writer): result}; with cache, done writers are loaded and new ones stored as they return (counts
    and the prompt only are printed on failure)."""
    results, todo, first_error = {}, [], None
    for w in ws:
        r = run_main._cache_load(cache, (w, True, False)) if cache else None
        if r is None:
            todo.append(w)
        else:
            results[(r["prompt"], r["writer"])] = r
    print("cache: %d of %d writers done, %d to run" % (len(results), len(ws), len(todo)), flush=True)
    t0 = time.time()

    def take(w, get):
        nonlocal first_error
        try:
            r = get()
            if cache:
                run_main._cache_store(cache, (w, True, False), r)
        except Exception as e:  # noqa: BLE001  (raised again after the others)
            print("a writer of %s failed (%s); the others go on" % (w.prompt, type(e).__name__), flush=True)
            first_error = first_error or e
            return
        results[(r["prompt"], r["writer"])] = r
        done = len(results)
        if done % 10 == 0 or done == len(ws):
            print("%d of %d writers, %.0f s since start" % (done, len(ws), time.time() - t0), flush=True)

    if workers > 1 and todo:
        with ProcessPoolExecutor(workers, initializer=_init, initargs=(ctx,)) as ex:
            futures = {ex.submit(_work, w): w for w in todo}
            try:
                for fut in as_completed(futures):
                    take(futures[fut], fut.result)
            except BaseException:
                ex.shutdown(cancel_futures=True)
                raise
    else:
        _init(ctx)
        for w in todo:
            take(w, lambda: _work(w))
    if first_error is not None:
        raise first_error
    return results


def main_part(main_of, keys):
    """The main cache's full-text cells of the forms and N of this analysis, per writer of keys."""
    return [{"prompt": p, "writer": w, "window": {},
             "full": {k: v for k, v in main_of[(p, w)]["full"].items() if k[1] in FORMS and k[3] in NS}}
            for p, w in keys]


def merge(*parts):
    """Per writer: the union of the full-text cells of several result lists (same writers, same order)."""
    out = []
    for rs in zip(*parts):
        if len({(r["prompt"], r["writer"]) for r in rs}) != 1:
            raise SystemExit("the result lists are not in the same order")
        full = {}
        for r in rs:
            if set(full) & set(r["full"]):
                raise SystemExit("two result lists have the same cell")
            full.update(r["full"])
        out.append({"prompt": rs[0]["prompt"], "writer": rs[0]["writer"], "full": full, "window": {}})
    return out


def positive_writers(res, main_of):
    """{control: writers that differ}: per writer, lambda 8 against the main A2 and A1' cells, lambda 4 and 16
    against A2-lam4 and A2-lam16 (a cell present on one side only differs too)."""
    out = {"A2 and A1' at lambda 8": 0, "A2 at lambda 4 and 16": 0}
    for r in res:
        m = main_of[(r["prompt"], r["writer"])]["full"]
        d8 = d416 = False
        for f in FORMS:
            for N in NS:
                for a in ("A2", "A1p"):
                    d8 |= dp_utility_r0._dump(r["full"].get(("full", f, name(a, 8), N))) != \
                        dp_utility_r0._dump(m.get(("full", f, a, N)))
                if forms.param(f)[0] != "R7" and N == 1000:
                    for lam, old in MAIN_LAM.items():
                        d416 |= dp_utility_r0._dump(r["full"].get(("full", f, name("A2", lam), N))) != \
                            dp_utility_r0._dump(m.get(("full", f, old, N)))
        out["A2 and A1' at lambda 8"] += d8
        out["A2 at lambda 4 and 16"] += d416
    return out


def positive_cells(cells, want):
    """Cells of this run that must equal main.json: lambda 8 -> A2 and A1', lambda 4 and 16 -> A2-lam4/A2-lam16."""
    pairs = []
    for f in FORMS:
        for N in NS:
            for a in ("A2", "A1p"):
                pairs.append(("full|%s|%s|%d" % (f, name(a, 8), N), "full|%s|%s|%d" % (f, a, N)))
            if forms.param(f)[0] != "R7" and N == 1000:
                for lam, old in MAIN_LAM.items():
                    pairs.append(("full|%s|%s|%d" % (f, name("A2", lam), N), "full|%s|%s|%d" % (f, old, N)))
    return [old for new, old in pairs
            if dp_utility_r0._dump(cells.get(new)) != dp_utility_r0._dump(want["main500"]["cells"].get(old))]


def best_of(res, R, strongest):
    """{'full|form|N': entry} of the strongest among the attackers named, with its resample maximum ('_boot')."""
    _, best, _ = aggregate.summarise_cells(res, R, {"full": tuple(strongest), "window": ()})
    return best


def strongest_report(base_best, all_best, new_best):
    """Per form and N: the strongest with the exploratory variants (interval of the resample maximum, the share
    selected) and its difference to the main strongest attacker; the best exploratory variant against the main
    strongest attacker (difference and interval)."""
    out = {}
    for g in sorted(all_best):
        e = all_best[g]
        b = base_best[g]
        rep = dict(aggregate.strip_boot({g: e})[g])
        rep["main_strongest"] = {"attacker": b["attacker"], "acc": b["acc"], "ci": aggregate.ci(b["_boot"])}
        rep["diff_to_main"] = e["acc"] - b["acc"]
        rep["diff_to_main_ci"] = aggregate.ci(e["_boot"] - b["_boot"])
        if g in new_best:
            n = new_best[g]
            rep["best_exploratory"] = {"attacker": n["attacker"], "acc": n["acc"], "ci": aggregate.ci(n["_boot"]),
                                       "minus_main": n["acc"] - b["acc"],
                                       "minus_main_ci": aggregate.ci(n["_boot"] - b["_boot"])}
        out[g] = rep
    return out


def run(args, analysis=6):
    if MUTATE:
        parts = os.path.normpath(os.path.abspath(args.out)).split(os.sep)
        if "results" in parts and ".tmp" not in parts:
            raise SystemExit("EXL_MUTATE is set: not writing into results/")
    if args.cache_dir and "main_cache" in os.path.normpath(os.path.abspath(args.cache_dir)).split(os.sep):
        raise SystemExit("--cache-dir must not be the main cache")
    import json
    with open(args.compare_main, encoding="utf-8") as f:
        want = json.load(f)
    here = {"seed_file_sha256": run_main._sha(os.path.join(HERE, "..", "SEED")),
            "config_sha256": run_main._sha(os.path.join(HERE, "..", "config.json"))}
    if any(want.get(k) != v for k, v in here.items()) and MUTATE != "skip_provenance":
        raise SystemExit("the seed or the config of %s is not the one of this folder" % args.compare_main)
    cfg, seed, by_prompt, pool_ids, pools, sample, excluded = setup(args, args.workers)
    if ({p: len(v) for p, v in pool_ids.items()} != want["writers_after_exclusion"] or excluded != want["excluded"]
            or {p: len(v) for p, v in sample.items()} != want["sample_sizes"]):
        raise SystemExit("the pool or the sample is not the one of %s" % args.compare_main)
    keys = sorted((p, w) for p, ids in sample.items() for w in ids)
    if MUTATE == "unsorted":
        keys = keys[::-1]
    cache = None
    if args.cache_dir:
        cache = os.path.join(args.cache_dir, "analysis%d" % analysis, fingerprint(args, analysis)[:16])
        os.makedirs(cache, exist_ok=True)
    ctx = Context(cfg, seed, pools, pool_ids, analysis)
    ws = [by_prompt[p][w] for p, w in keys]
    if args.time_first:
        step = max(1, len(ws) // args.time_first)
        pick = ws[::step][:args.time_first]
        t0 = time.time()
        evaluate_all(pick, ctx, min(args.workers, len(pick)), cache)
        dt = time.time() - t0
        print("timing: %d writers, %d workers, %.0f s wall, %.1f s per writer per worker, %.1f h for %d writers "
              "with %d workers" % (len(pick), min(args.workers, len(pick)), dt,
                                   dt * min(args.workers, len(pick)) / len(pick),
                                   dt * min(args.workers, len(pick)) / len(pick) * len(ws) / args.workers / 3600,
                                   len(ws), args.workers), flush=True)
        return None
    results = evaluate_all(ws, ctx, args.workers, cache)
    res = [results[k] for k in keys]
    R, _ = aggregate.resamples(seed, [r["prompt"] for r in res], "main500")
    main_of = dp_utility_r0.load_main_of(args.main_cache, keys)
    main_res = main_part(main_of, keys)
    cells, _, _ = aggregate.summarise_cells(res, R, {"full": (), "window": ()})

    bad = {}
    base_best = best_of(main_res, R, evaluate.STRONGEST_FULL)
    bad["main strongest attacker"] = [g for g in base_best if dp_utility_r0._dump(aggregate.strip_boot(
        {g: base_best[g]})[g]) != dp_utility_r0._dump(want["main500"]["strongest"].get(g))]
    if analysis == 6:
        bad.update({k: ["%d writers" % v] if v else [] for k, v in positive_writers(res, main_of).items()})
        bad["cells against main.json"] = positive_cells(cells, want)
        parts, new_names = [main_res, res], variants(6)
    else:
        lam_res, lam_cells = load_lambda(args, keys, R)
        bad["analysis 6 cells against %s" % os.path.basename(args.compare_lambda)] = lam_cells
        parts, new_names = [main_res, lam_res, res], variants(6) + variants(7)
    if MUTATE == "skip_positive":
        bad = {k: [] for k in bad}
    for k, v in bad.items():
        print("positive control %s: %s" % (k, "%d differ" % len(v) if v else "identical"), flush=True)
    if any(bad.values()):
        raise SystemExit(2)

    all_best = best_of(merge(*parts), R, tuple(evaluate.STRONGEST_FULL) + tuple(new_names))
    new_best = best_of(merge(*parts[1:]) if len(parts) > 2 else res, R, new_names)
    head = dict(here, source=args.source, sample="main500", sample_sizes=want["sample_sizes"], forms=FORMS,
                lams=list(LAMS), N=list(NS), attackers=variants(analysis), note=NOTE[analysis],
                caches={"main500": os.path.basename(os.path.normpath(args.main_cache)),
                        "this": os.path.basename(cache) if cache else None},
                counts=run_main._counts(res),
                positive_control=("per writer, A2 and A1' at lambda 8 equal the main cache and A2 at lambda 4 and "
                                  "16 equal A2-lam4/A2-lam16; their cells equal main.json; the main strongest "
                                  "attacker formed again equals main.json") if analysis == 6 else
                ("the main strongest attacker formed again equals main.json; the analysis 6 cells formed again "
                 "from its cache equal exploratory_lambda.json"))
    if MUTATE:
        head["mutate"] = MUTATE
    out = dict(head, cells=cells, strongest=strongest_report(base_best, all_best, new_best),
               strongest_attackers=list(evaluate.STRONGEST_FULL) + new_names)
    write(out, args.out)
    return out


def load_lambda(args, keys, R):
    """Analysis 6's per-writer results from its cache (only the files of keys) and the cells of
    exploratory_lambda.json that they do not give again."""
    import json
    from types import SimpleNamespace
    with open(args.compare_lambda, encoding="utf-8") as f:
        want6 = json.load(f)
    out, missing = [], 0
    for p, w in keys:
        r = run_main._cache_load(args.lambda_cache, (SimpleNamespace(prompt=p, writer=w), True, False))
        if r is None:
            missing += 1
            continue
        out.append(r)
    if missing:
        raise SystemExit("the analysis 6 cache lacks %d of the %d writers" % (missing, len(keys)))
    cells, _, _ = aggregate.summarise_cells(out, R, {"full": (), "window": ()})
    diff = sorted(set(cells) ^ set(want6["cells"])) + [
        k for k in sorted(set(cells) & set(want6["cells"]))
        if dp_utility_r0._dump(cells[k]) != dp_utility_r0._dump(want6["cells"][k])]
    return out, diff


def write(out, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    part = "%s.%d.part" % (path, os.getpid())
    try:
        with open(part, "w", encoding="utf-8", newline="\n") as f:
            f.write(dp_utility_r0._dump(out) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(part, path)
    finally:
        if os.path.exists(part):
            os.remove(part)
    print("wrote", path, flush=True)


def parser(desc):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--source", choices=["klicke", "synthetic"], default="klicke")
    ap.add_argument("--root", help="with --source klicke: the KLiCKe folder")
    ap.add_argument("--per-prompt", type=int, default=40, help="with --source synthetic (the self-test)")
    ap.add_argument("--per-prompt-sample", type=int, default=125)
    ap.add_argument("--main-cache", required=True, help="the cache folder of the main500 stage (read only)")
    ap.add_argument("--compare-main", required=True, help="main.json")
    ap.add_argument("--cache-dir", default=None, help="this analysis's own cache root (not the main cache)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--time-first", type=int, default=0, help="time this many writers and stop (no output)")
    ap.add_argument("--out", required=True)
    return ap


def main():
    run(parser(__doc__.split("\n")[0]).parse_args(), 6)


if __name__ == "__main__":
    main()
