"""The utility of R-DP against R0 (deviation D5, notes.md): the dp stage (--forms dp) has no R0, so the Spearman with
R0 and the ratios to R0 of exploratory_dp.json are empty. This script reads the per-writer results that the main500
stage and the dp stage left in their caches (deviation D4), adds to each writer of the sample the R0 utility of the
main500 stage (R3 and R-DP stay those of the dp stage), and calls aggregate.utility_summary with the scores and the
resamples main500 as run_main.run does. No new random numbers; no matching is computed again. Only aggregates are
written; no writer ID, no per-writer value.

This script is not imported by run_main.py, so it is not in the cache fingerprint; it never calls cache_fingerprint
and never writes into a cache. The cache folders are trusted (pickle): point them only at folders run_main.py wrote.
The all stage (--all) shares the fingerprint of the main500 stage and adds the writers outside the sample to its
cache while it runs; from the main cache this script opens only the files of the sample (run_main._cache_path),
which the all stage reads but never replaces.

    python -I scripts/dp_utility_r0.py --source klicke --root raw/klicke/extracted/WritingTask \
        --main-cache raw/derived/main_cache/33fa95833296d7a5 --dp-cache raw/derived/main_cache/1383e6ee6aca2c58 \
        --compare-main results/main.json --compare-dp results/exploratory_dp.json \
        --out results/exploratory_dp_utility_r0.json

It stops unless both JSON files have the seed and the config of this folder and the same sample sizes, unless the dp
cache holds that sample and the main cache holds every writer of it, unless every writer has one score, unless the
per-writer utility of R3 (computed in both stages) is identical in the two caches, and unless the output agrees with
the two JSON files (positive controls): the utility of R3 identical to main.json's, utility_figure of R3 identical to
main.json's, and the keys, spearman_score and cell of every form identical to exploratory_dp.json's.
"""
import argparse
import glob
import json
import os
import pickle
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import forms  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402
import utility  # noqa: E402

MUTATE = os.environ.get("DPU_MUTATE", "")


def load_dp_sample(cache):
    """Results of the tasks that evaluated windows (the sample; the dp stage ran without --all), sorted by (prompt,
    writer) as run_main.run sorts the sample."""
    res = []
    for path in sorted(glob.glob(os.path.join(cache, "*.pkl"))):
        with open(path, "rb") as f:
            key, r = pickle.load(f)
        if key[2]:
            res.append(r)
    if MUTATE != "unsorted":  # as run_main.run: [results[k] for k in sorted(sample_set)], k = (prompt, writer)
        res.sort(key=lambda r: (r["prompt"], r["writer"]))
    return res


def load_main_of(cache, keys):
    """{(prompt, writer): result} of the main500 stage for the writers in keys: only their files are opened (a writer
    of the sample has windows; it also has costs when it is a B of the negative control)."""
    out, missing = {}, 0
    for p, w in keys:
        paths = [run_main._cache_path(cache, (SimpleNamespace(prompt=p, writer=w), True, kc)) for kc in (False, True)]
        found = [x for x in paths if os.path.exists(x)]
        if len(found) != 1:
            missing += 1
            continue
        with open(found[0], "rb") as f:
            key, r = pickle.load(f)
        if key[:2] != [p, w] or (r["prompt"], r["writer"]) != (p, w):
            raise SystemExit("a file of the main cache belongs to another task")
        out[(p, w)] = r
    if missing and MUTATE != "skip_keys":
        raise SystemExit("the main cache lacks %d of the %d writers of the dp cache" % (missing, len(keys)))
    return out


def merge(main_of, dp_res):
    """Per writer of the sample: the utility of the dp stage with R0 of the main500 stage added."""
    keys = [(r["prompt"], r["writer"]) for r in dp_res]
    if len(set(keys)) != len(keys) and MUTATE != "skip_dup":
        raise SystemExit("the dp cache has %d duplicated writer(s)" % (len(keys) - len(set(keys))))
    out, r3_diff = [], 0
    for r in dp_res:
        m = main_of.get((r["prompt"], r["writer"]))
        if m is None:
            continue
        r3_diff += _dump(r["utility"].get("R3")) != _dump(m["utility"].get("R3"))
        u = dict(r["utility"])
        if MUTATE != "no_r0":
            u["R0"] = m["utility"]["R0"]
        out.append({"prompt": r["prompt"], "writer": r["writer"], "utility": u})
    if r3_diff and MUTATE != "skip_r3":
        raise SystemExit("the R3 utility of %d writer(s) differs between the two caches" % r3_diff)
    return out


def scores_for(res, writers):
    """The score of each writer of res, from the writers that run_main.load_writers gives (counts only on failure)."""
    score_of, dup = {}, 0
    for w in writers:
        dup += (w.prompt, w.writer) in score_of
        score_of[(w.prompt, w.writer)] = w.score
    missing = sum(1 for r in res if score_of.get((r["prompt"], r["writer"])) is None)
    if dup or missing:
        raise SystemExit("%d duplicated writer(s) in the source, %d writer(s) of the sample without a score"
                         % (dup, missing))
    return [score_of[(r["prompt"], r["writer"])] for r in res]


def _dump(x):
    return json.dumps(run_main._clean(x), indent=1, sort_keys=True)


def controls(u, fig, want_main, want_dp):
    """{name: keys that differ} of the positive controls (an empty list: identical)."""
    mu, du = want_main["main500"]["utility"], want_dp["main500"]["utility"]
    r3 = sorted(k for k in mu if k.endswith("|R3"))
    out = {"R3 utility": [k for k in r3 if _dump(u.get(k)) != _dump(mu[k])],
           "R3 utility_figure": [] if _dump(fig.get("R3")) == _dump(want_main["main500"]["utility_figure"]["R3"])
           else ["R3"],
           "keys, spearman_score and cell": sorted(set(u) ^ set(du)) + [
               k for k in sorted(set(u) & set(du))
               if _dump([u[k]["spearman_score"], u[k]["cell"]]) != _dump([du[k]["spearman_score"], du[k]["cell"]])]}
    for name, mutant in zip(out, ("no_positive_r3", "no_positive_fig", "no_positive_dp")):
        if MUTATE == mutant:
            out[name] = []
    return out


def run(args):
    if MUTATE:
        parts = os.path.normpath(os.path.abspath(args.out)).split(os.sep)
        if "results" in parts and ".tmp" not in parts:
            raise SystemExit("DPU_MUTATE is set: not writing into results/")
    with open(args.compare_main, encoding="utf-8") as f:
        want_main = json.load(f)
    with open(args.compare_dp, encoding="utf-8") as f:
        want_dp = json.load(f)
    here = {"seed_file_sha256": run_main._sha(os.path.join(HERE, "..", "SEED")),
            "config_sha256": run_main._sha(os.path.join(HERE, "..", "config.json"))}
    if any(w.get(k) != v for w in (want_main, want_dp) for k, v in here.items()) and MUTATE != "skip_provenance":
        raise SystemExit("the seed or the config of a JSON file is not the one of this folder")
    if want_main["sample_sizes"] != want_dp["sample_sizes"]:
        raise SystemExit("the two JSON files have different samples")
    dp_res = load_dp_sample(args.dp_cache)
    res = merge(load_main_of(args.main_cache, [(r["prompt"], r["writer"]) for r in dp_res]), dp_res)
    sizes = {}
    for r in res:
        sizes[r["prompt"]] = sizes.get(r["prompt"], 0) + 1
    if sizes != want_dp["sample_sizes"]:
        raise SystemExit("the sample of the caches is not the sample of %s" % args.compare_dp)
    seed = seeds.read_seed()
    scores = scores_for(res, run_main.load_writers(args.source, seed, args))
    R, cols = aggregate.resamples(seed, [r["prompt"] for r in res], "main500")
    u, fig = aggregate.utility_summary(res, scores, forms.DP, R, cols)

    bad = controls(u, fig, want_main, want_dp)
    for name, keys in bad.items():
        print("positive control %s: %s" % (name, "%d differ" % len(keys) if keys else "identical"), flush=True)
    if any(bad.values()):
        raise SystemExit(2)
    filled = sum(1 for k in u if u[k]["ratio_median"]["mean"] is not None)
    print("writers %d, utility entries %d, with a ratio to R0 %d" % (len(res), len(u), filled), flush=True)

    out = dict(here, source=args.source,
               caches={"main500": os.path.basename(os.path.normpath(args.main_cache)),
                       "dp": os.path.basename(os.path.normpath(args.dp_cache))},
               sample="main500", writers=len(res), sample_sizes=sizes, forms=forms.DP, metrics=utility.METRICS,
               positive_control="utility of R3 identical to main.json; utility_figure of R3 identical to main.json; "
                                "keys, spearman_score and cell of every form identical to exploratory_dp.json",
               note="exploratory (decision 55), not preregistered; utility of R-DP against R0 recomputed from the "
                    "caches (deviation D5); aggregates only",
               utility=u, utility_figure=fig)
    if MUTATE:
        out["mutate"] = MUTATE
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    part = "%s.%d.part" % (args.out, os.getpid())
    try:
        with open(part, "w", encoding="utf-8", newline="\n") as f:
            f.write(_dump(out) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(part, args.out)
    finally:
        if os.path.exists(part):
            os.remove(part)
    print("wrote", args.out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", choices=["klicke", "synthetic"], default="klicke", help="where the scores come from")
    ap.add_argument("--root", help="with --source klicke: the KLiCKe folder (for the scores)")
    ap.add_argument("--per-prompt", type=int, default=None, help="with --source synthetic (the self-test)")
    ap.add_argument("--main-cache", required=True, help="the cache folder of the main500 stage (with R0)")
    ap.add_argument("--dp-cache", required=True, help="the cache folder of the dp stage")
    ap.add_argument("--compare-main", required=True, help="main.json: R3, the seed, the config and the sample sizes")
    ap.add_argument("--compare-dp", required=True, help="exploratory_dp.json: the keys, spearman_score and cell")
    ap.add_argument("--out", required=True)
    run(ap.parse_args())


if __name__ == "__main__":
    main()
