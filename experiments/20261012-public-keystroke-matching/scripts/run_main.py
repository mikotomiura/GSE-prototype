"""The main computation (preregistration.md). Writes aggregates only.

    python scripts/run_main.py --source synthetic --out results/main_synthetic.json [--workers 16] [--all]
    python -I scripts/run_main.py --source klicke --root raw/klicke/extracted/WritingTask --a4-dir raw/derived/a4 \
        --out results/main.json --workers 12 [--all]
    python -I scripts/run_main.py --source klicke --root raw/klicke/extracted/WritingTask --forms dp \
        --out results/exploratory_dp.json --workers 12

--source synthetic builds a small corpus of synthetic writers (no human data) to exercise the whole pipeline;
--source klicke reads the KLiCKe files (load_klicke.py). --all adds the appendix sample of all writers after
exclusion. --forms dp runs the exploratory form R-DP(eps) with R3 as the reference (decisions 55 and 56; contrasts
R3 - R-DP(eps); no negative control). --a4-dir adds the A4 cells from the reconstructions of scripts/a4_keytar.py.

With KLiCKe the rows are never all in memory (17M rows): a worker reads one writer's log, computes what the training
models and the task maximum need from it and drops the rows (train_contrib); the parent merges the contributions in
(prompt, writer) order, which gives the same models as the list-based build; the evaluation workers read the log
again.

--cache-dir makes the run resumable (deviation D4, notes.md): the result of each evaluation task is written to
<cache-dir>/<fingerprint>/ as soon as it returns, and a rerun with the same fingerprint (seed, config, code, library
versions, source, forms, A4 reconstructions, open-world N) loads it instead of evaluating again. A task's result
depends only on the writer, its two flags and the context, not on the order of the tasks or on the sample, so a
resumed run writes the same output as an uninterrupted one (selftest_main.py, run_resume). The cache holds per-writer
results: keep it under raw/ (not versioned).
"""
import argparse
import hashlib
import json
import os
import pickle
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import attackers as A  # noqa: E402
import corpus  # noqa: E402
import dp  # noqa: E402
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
    if source == "klicke":
        import load_klicke
        if not args.root:
            raise SystemExit("--root is required with --source klicke")
        writers, _ = load_klicke.load(args.root)
        return writers  # the rows are read in the workers (fill_rows)
    raise SystemExit("unknown source %r" % source)


def prepare(writers):
    """Writers with rows in memory (the self-test): active rows, text with \\r\\n -> \\n, exclusion."""
    kept, excluded = [], {}
    for w in writers:
        w.rows = corpus.active_rows(w.rows)
        w.extra["active"] = True
        w.text = (w.text or "").replace("\r\n", "\n")
        why = corpus.exclusion_reason(w)
        if why:
            excluded[why] = excluded.get(why, 0) + 1
        else:
            kept.append(w)
    return kept, excluded


def _read_active(w):
    """The active rows of w; reads the KLiCKe log in this process when the rows are not in memory."""
    if not w.rows and w.extra.get("log_path"):
        import load_klicke
        load_klicke.fill_rows(w)
        w.rows = corpus.active_rows(w.rows)
        w.extra["active"] = True
    elif not w.extra.get("active"):
        w.rows = corpus.active_rows(w.rows)
        w.extra["active"] = True
    return w.rows


def _drop_rows(w):
    if w.extra.get("log_path"):
        w.rows = []
        w.extra["active"] = False


def train_contrib(w, seed, cfg, dp_eps=()):
    """(contribution, None) or (None, exclusion reason) for one writer: what the training models and the task
    maximum need from it. Every writer trains the models of the other fold. The rows of a KLiCKe writer are dropped
    afterwards (read again by the evaluation worker)."""
    rows = _read_active(w)
    why = corpus.exclusion_reason(w)
    if why:
        _drop_rows(w)
        return None, why
    r3u = forms.release(rows, "R3-u", seed, w.prompt, w.writer)
    c = A.Cand(w.text)
    out = {"digraph": A.pack_triples(A.digraph_triples(rows)), "boundary": A.pack_xy(*A.boundary_xy(rows, r3u)),
           "diff": len(A.r3u_replay(r3u)) - c.nchars, "r7": {}, "dp": {},
           "interval_max": utility.interval_max(forms.release(rows, "R0", seed, w.prompt, w.writer))}
    for p in cfg["release_forms"]["R7"]["suppress_p"]:
        rel = forms.release(rows, "R7(%s)" % p, seed, w.prompt, w.writer)
        segs, al = A.r7_alignments(rel, [c], cfg)
        out["r7"][p] = A.r7_segment_pairs(segs, rel.times(), al[0][1], c) if al[0][1] is not None else []
    for eps, label in dp_eps:
        g = seeds.rng(seed, "exploratory_dp", w.prompt, w.writer, "", "", "eps:%s:train" % label)
        t = dp.noisy_times([r["down_time"] for r in rows], eps, g)
        out["dp"][eps] = A.pack_triples(A.digraph_triples([dict(r, down_time=x) for r, x in zip(rows, t)]))
    _drop_rows(w)
    return out, None


def _contrib_work(task):
    w, seed, cfg, dp_eps = task
    out, why = train_contrib(w, seed, cfg, dp_eps)
    return w.prompt, w.writer, out, why


def models_from(contribs, cfg, dp_eps=()):
    """Models of one fold from the contributions of its training writers (in (prompt, writer) order): the
    character-pair table (R0), the A2-b boundary model (R3-u), the R3-u length term, the R7 duration regressions and,
    with dp_eps, the R-DP tables (training times with the interval mechanism)."""
    mc = cfg["attackers"]["A3"]["min_digraph_count"]
    digraph = A.DigraphTable(None, mc, triples=(t for c in contribs for t in A.unpack_triples(c["digraph"])))
    X = np.concatenate([c["boundary"][0] for c in contribs]) if contribs else np.zeros((0, 4))
    y = np.concatenate([c["boundary"][1] for c in contribs]) if contribs else np.zeros(0, dtype=bool)
    boundary = A.BoundaryModel(None, cfg, xy=(X, y))
    length = A.LengthTerm([c["diff"] for c in contribs])
    r7 = {p: A.R7Duration([pr for c in contribs for pr in c["r7"][p]])
          for p in cfg["release_forms"]["R7"]["suppress_p"]}
    out = {"digraph": digraph, "boundary": boundary, "length": length, "r7": r7}
    if dp_eps:
        out["digraph_dp"] = {eps: A.DigraphTable(None, mc, triples=(t for c in contribs
                                                                    for t in A.unpack_triples(c["dp"][eps])))
                             for eps, _ in dp_eps}
    return out


def build_models(train, seed, cfg, dp_eps=()):
    """The models of one fold from training writers with rows in memory (the self-test). The training writers are
    taken in the order of (prompt, writer), so that the models do not depend on the order of the loader."""
    if MUTATE != "train_unsorted":
        train = sorted(train, key=lambda w: (w.prompt, w.writer))
    return models_from([train_contrib(w, seed, cfg, dp_eps)[0] for w in train], cfg, dp_eps)


_CTX = None


def _init(ctx):
    global _CTX
    _CTX = ctx


def _work(task):
    w, windows, keep_costs = task
    _CTX.windows, _CTX.keep_costs = windows, keep_costs
    _read_active(w)
    try:
        return evaluate.evaluate_writer(w, _CTX)
    finally:
        _drop_rows(w)


def _files_under(root):
    for d, dirs, names in os.walk(root):
        dirs.sort()
        for n in sorted(names):
            p = os.path.join(d, n)
            yield os.path.relpath(p, root).replace(os.sep, "/"), p


def cache_fingerprint(args):
    """SHA-256 of everything a task's result depends on besides the writer and its flags: seed, config, the code of
    this folder that the run imports (the modules imported lazily included), library versions, the content of every
    data file and A4 reconstruction, and the arguments that change a task's result. The sample (--per-prompt-sample)
    and --all are not in it: they choose the tasks, not their results."""
    import Levenshtein
    import scipy
    import sklearn
    import load_klicke  # noqa: F401  (imported lazily by the loader and the workers)
    import synthetic_logs  # noqa: F401
    if args.a4_dir:
        import a4_keytar  # noqa: F401  (imported lazily by evaluate.a4_cells)
    h = hashlib.sha256()

    def put(name, value):
        h.update(("%s=%s\n" % (name, value)).encode("utf-8"))

    put("seed", _sha(os.path.join(HERE, "..", "SEED")))
    put("config", _sha(os.path.join(HERE, "..", "config.json")))
    code = {os.path.basename(m.__file__) for m in list(sys.modules.values())
            if getattr(m, "__file__", None) and os.path.dirname(os.path.abspath(m.__file__)) == HERE}
    for n in sorted(code | {"run_main.py"}):
        put("code:" + n, _sha(os.path.join(HERE, n)))
    put("versions", (platform.python_version(), np.__version__, scipy.__version__, sklearn.__version__,
                     Levenshtein.__version__))
    put("args", (args.source, args.forms, args.open_world_n, args.per_prompt if args.source == "synthetic" else None,
                 MUTATE))
    if args.root:
        for rel, p in _files_under(args.root):
            put("data:" + rel, _sha(p))
    if args.a4_dir:
        for rel, p in _files_under(args.a4_dir):
            put("a4:" + rel, _sha(p))
    return h.hexdigest()


def _task_key(task):
    w, windows, keep_costs = task
    return [w.prompt, w.writer, bool(windows), bool(keep_costs)]


def _cache_path(cache, task):
    key = hashlib.sha256(json.dumps(_task_key(task)).encode("utf-8")).hexdigest()
    return os.path.join(cache, key[:32] + ".pkl")


def _cache_load(cache, task):
    """The cached result of task, or None (also for a damaged file, which is evaluated again). The cache folder is
    trusted (pickle): point --cache-dir only at a folder this script wrote; a cache is never shared or received."""
    path = _cache_path(cache, task)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            key, r = pickle.load(f)
    except (EOFError, pickle.UnpicklingError, ValueError) as e:
        print("cache file %s unreadable (%s): evaluated again" % (path, type(e).__name__), flush=True)
        return None
    if key != _task_key(task):
        raise SystemExit("cache file %s belongs to another task" % path)
    return r


def _cache_store(cache, task, r):
    path = _cache_path(cache, task)
    part = "%s.%d.part" % (path, os.getpid())
    with open(part, "wb") as f:
        pickle.dump((_task_key(task), r), f, protocol=pickle.HIGHEST_PROTOCOL)
        f.flush()
        os.fsync(f.fileno())
    os.replace(part, path)


def evaluate_tasks(tasks, ctx, workers, cache=None):
    """{(prompt, writer): result} of every task; with cache, done tasks are loaded and new ones stored on return.
    A failed task does not discard the others: they are still stored, and the first error is raised at the end."""
    results, todo, first_error = {}, [], None
    for t in tasks:
        r = _cache_load(cache, t) if cache else None
        if r is None:
            todo.append(t)
        else:
            results[(r["prompt"], r["writer"])] = r
    if cache:
        print("cache %s: %d of %d tasks done, %d to run" % (cache, len(results), len(tasks), len(todo)), flush=True)

    def take(t, get):
        nonlocal first_error
        if not cache:
            r = get()
        else:
            try:
                r = get()
                _cache_store(cache, t, r)
            except Exception as e:  # noqa: BLE001  (raised again after the other tasks)
                print("a task of %s failed (%s); the others go on" % (t[0].prompt, type(e).__name__), flush=True)
                first_error = first_error or e
                return
        results[(r["prompt"], r["writer"])] = r

    if workers > 1 and todo:
        with ProcessPoolExecutor(workers, initializer=_init, initargs=(ctx,)) as ex:
            futures = {ex.submit(_work, t): t for t in todo}
            try:
                for fut in as_completed(futures):
                    take(futures[fut], fut.result)
            except BaseException:
                ex.shutdown(cancel_futures=True)
                raise
    else:
        _init(ctx)
        for t in todo:
            take(t, lambda: _work(t))
    if first_error is not None:
        raise first_error
    return results


def run(args):
    t0 = time.time()
    cache = None
    if args.cache_dir:
        cache = os.path.join(args.cache_dir, cache_fingerprint(args)[:16])
        os.makedirs(cache, exist_ok=True)
    cfg = load_config()
    seed = seeds.read_seed()
    form_list = forms.DP if args.forms == "dp" else forms.ALL
    dp_eps = [(forms.param(f)[1], f[:-1].split("(")[1]) for f in form_list if f.startswith("R-DP(")]
    writers = load_writers(args.source, seed, args)
    for w in writers:
        w.text = (w.text or "").replace("\r\n", "\n")
    order = sorted(writers, key=lambda w: (w.prompt, w.writer))
    if args.workers > 1:
        with ProcessPoolExecutor(args.workers) as ex:
            contribs = list(ex.map(_contrib_work, [(w, seed, cfg, dp_eps) for w in order], chunksize=4))
    else:
        contribs = [_contrib_work((w, seed, cfg, dp_eps)) for w in order]
    excluded, contrib_of, by_prompt = {}, {}, {}
    for w, (p, wid, c, why) in zip(order, contribs):
        if why:
            excluded[why] = excluded.get(why, 0) + 1
            continue
        if not w.extra.get("log_path") and not w.extra.get("active"):  # synthetic rows from a worker: cut here
            w.rows = corpus.active_rows(w.rows)
            w.extra["active"] = True
        contrib_of[(p, wid)] = c
        by_prompt.setdefault(p, {})[wid] = w
    del contribs
    prompts = sorted(by_prompt)
    fold_a, fold_b = matching.split_folds(seed, prompts)
    fold_of_prompt = {p: (0 if p in fold_a else 1) for p in prompts}
    folds = (fold_a, fold_b)
    models = {}
    for f in (0, 1):
        eval_ids = {wid for p in folds[f] for wid in by_prompt[p]}
        train = [w for p in folds[1 - f] for w in by_prompt[p].values() if w.writer not in eval_ids]
        if MUTATE != "train_unsorted":
            train = sorted(train, key=lambda w: (w.prompt, w.writer))
        models[f] = models_from([contrib_of[(w.prompt, w.writer)] for w in train], cfg, dp_eps)
    pool_ids = {p: sorted(by_prompt[p]) for p in prompts}
    pools = {p: [A.Cand(by_prompt[p][wid].text) for wid in pool_ids[p]] for p in prompts}
    task_max = {p: max(contrib_of[(p, wid)]["interval_max"] for wid in pool_ids[p]) for p in prompts}
    del contrib_of
    sample = matching.eval_sample(seed, {p: list(by_prompt[p]) for p in prompts}, args.per_prompt_sample)
    sample_set = {(p, wid) for p, ids in sample.items() for wid in ids}
    nc_b = {}
    for p, ids in sample.items():
        for wid in ids:
            others = [x for x in pool_ids[p] if x != wid]
            nc_b[(p, wid)] = others[int(seeds.rng(seed, "negative_control", p, wid).integers(0, len(others)))]
    # only the records of the B writers return cost vectors (main forms, adaptive attackers)
    need_costs = {(p, b) for (p, _), b in nc_b.items()} if args.forms == "main" else set()
    n_values = [int(n) for n in cfg["matching"]["N"]]
    if args.open_world_n not in n_values:
        raise SystemExit("--open-world-n must be one of the registered N %s" % n_values)
    ctx = evaluate.Context(cfg, seed, pools, pool_ids, models, task_max, fold_of_prompt, form_list, n_values,
                           nc_forms=forms.MAIN, open_world_n=args.open_world_n, a4_dir=args.a4_dir)
    tasks = []
    for p in prompts:
        for wid in pool_ids[p]:
            in_sample = (p, wid) in sample_set
            if in_sample or (p, wid) in need_costs or args.all:
                tasks.append((by_prompt[p][wid], in_sample or args.all, (p, wid) in need_costs))
    results = evaluate_tasks(tasks, ctx, args.workers, cache)
    out = {"source": args.source, "seed_file_sha256": _sha(os.path.join(HERE, "..", "SEED")),
           "config_sha256": _sha(os.path.join(HERE, "..", "config.json")),
           "writers_after_exclusion": {p: len(pool_ids[p]) for p in prompts}, "excluded": excluded,
           "folds": [fold_a, fold_b], "sample_sizes": {p: len(v) for p, v in sample.items()},
           "open_world_n": args.open_world_n}
    if MUTATE:
        out["mutate"] = MUTATE
    if args.a4_dir and not args.a4_partial:
        have = {k for k, r in results.items() if r.get("a4")}
        if not sample_set <= have:
            raise SystemExit("--a4-dir lacks %d of the %d writers of the sample (--a4-partial to allow)"
                             % (len(sample_set - have), len(sample_set)))
    if args.forms != "main" or args.a4_dir:
        out["forms"] = form_list
        out["a4_writers"] = sum(1 for r in results.values() if r.get("a4"))
    strongest = {"full": evaluate.STRONGEST_FULL, "window": evaluate.STRONGEST_WINDOW}
    samples = {"main500": sorted(sample_set)}
    if args.all:
        samples["all"] = sorted((p, w) for p in prompts for w in pool_ids[p])
    for name, keys in samples.items():
        res = [results[k] for k in keys]
        R, cols = aggregate.resamples(seed, [r["prompt"] for r in res], name)
        out[name] = summarise_sample(res, R, cols, strongest, cfg, ctx.open_world_n,
                                     [by_prompt[r["prompt"]][r["writer"]].score for r in res], form_list)
        if name == "main500" and args.forms == "main":
            best = out[name].pop("_best")
            out[name]["negative_control"] = negative_control(res, results, nc_b, pool_ids, seed, R, strongest, best,
                                                             out[name]["cells"])
        out[name].pop("_best", None)
    out["seconds"] = None if args.no_timing else round(time.time() - t0, 1)
    with open(args.out + ".part", "w", encoding="utf-8", newline="\n") as f:  # never a half-written output
        json.dump(_clean(out), f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(args.out + ".part", args.out)
    print("wrote", args.out, "tasks", len(tasks))


def summarise_sample(res, R, cols, strongest, cfg, open_world_n, scores, form_list=None):
    """Every aggregate of one sample (500 writers or all writers). '_best' keeps the strongest attacker with its
    resamples for the negative control; the caller removes it before writing. The exploratory run (R-DP) has the
    contrasts R3 - R-DP(eps)."""
    form_list = forms.ALL if form_list is None else form_list
    cells, best, boot = aggregate.summarise_cells(res, R, strongest)
    pairs = [("R3", "R-DP")] if form_list == forms.DP else [tuple(c) for c in cfg["contrasts"]]
    con, missing = aggregate.contrasts(best, cells, boot, pairs, form_list)
    out = {"cells": cells, "strongest": aggregate.strip_boot(best), "contrasts": con, "contrasts_missing": missing,
           "reference_A4": aggregate.reference_rows(cells), "counts": _counts(res),
           "rebuilt_split": aggregate.split_by_rebuilt(res, R, cells),
           "open_world": aggregate.open_world(res, R, best, cells, form_list, open_world_n),
           "window_bias": aggregate.window_bias(res), "_best": best}
    out["utility"], out["utility_figure"] = aggregate.utility_summary(res, scores, form_list, R, cols)
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
    ap.add_argument("--root", default=None, help="the extracted WritingTask folder (--source klicke)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--forms", choices=("main", "dp"), default="main")
    ap.add_argument("--a4-dir", default=None, help="reconstructions of scripts/a4_keytar.py (adds the A4 cells)")
    ap.add_argument("--a4-partial", action="store_true", help="allow writers of the sample without a reconstruction")
    ap.add_argument("--per-prompt", type=int, default=40, help="synthetic writers per prompt")
    ap.add_argument("--per-prompt-sample", type=int, default=125)
    ap.add_argument("--open-world-n", type=int, default=evaluate.OPEN_WORLD_N,
                    help="N of the open-world diagnostic (1000 as registered; smaller only for the self-test)")
    ap.add_argument("--no-timing", action="store_true", help="omit the run time so that reruns are byte-identical")
    ap.add_argument("--cache-dir", default=None,
                    help="store each task's result here and reuse it on a rerun (resumable; keep it under raw/)")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
