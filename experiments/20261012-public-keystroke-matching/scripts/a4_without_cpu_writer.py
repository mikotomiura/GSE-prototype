"""The A4 cells without the writer whose A4 chunks were generated on the CPU (deviation D3, notes.md): the same
aggregation as run_main.run does for main500 (aggregate.resamples -> aggregate.summarise_cells ->
aggregate.reference_rows), on the per-writer results that the main_a4 stage left in its cache (deviation D4), with
the excluded writers removed and resamples under a new sample name. Only aggregates are written; no writer ID.

This script is not imported by run_main.py, so it is not in the cache fingerprint; it never calls cache_fingerprint.
The cache folder is trusted (pickle): point --cache only at the folder run_main.py wrote.

    python -I scripts/a4_without_cpu_writer.py --cache raw/derived/main_cache/<fingerprint 16> \
        --compare results/main_a4.json --exclude raw/derived_a4_cpu_fallback_writers.json --expect-excluded 1 \
        --sample-name main500_without_cpu_writer --out results/main_a4_without_cpu_writer.json

Every run first recomputes the A4 cells of all the sample with the resamples main500 and stops unless they are
identical to reference_A4 of --compare (the positive control), and unless the sample sizes per prompt are those of
--compare; the excluded version is computed from the same loaded results. Without --exclude it writes the positive
control. The sample positions it prints can be turned back into IDs with the public seed: do not publish the log.
"""
import argparse
import glob
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import evaluate  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402

MUTATE = os.environ.get("A4WO_MUTATE", "")


def load_sample(cache):
    """Results of the tasks that evaluated windows (the sample; main_a4 runs without --all), sorted by (prompt,
    writer) as run_main.run sorts the sample."""
    res = []
    for path in sorted(glob.glob(os.path.join(cache, "*.pkl"))):
        with open(path, "rb") as f:
            key, r = pickle.load(f)
        if key[2] or MUTATE == "keep_cost_only":  # windows = in the sample (main_a4 runs without --all)
            res.append(r)
    if MUTATE != "unsorted":  # as run_main.run: [results[k] for k in sorted(sample_set)], k = (prompt, writer)
        res.sort(key=lambda r: (r["prompt"], r["writer"]))
    return res


def excluded_keys(path):
    with open(path, encoding="utf-8") as f:
        return {(e["prompt"], e["writer"]) for e in json.load(f)}


def a4_without(res, drop, seed, sample_name):
    """(reference_A4 cells, kept results) of res without the writers in drop."""
    keys = [(r["prompt"], r["writer"]) for r in res]
    absent = drop - set(keys)
    if absent and MUTATE != "absent_ok":
        raise SystemExit("%d writer(s) to exclude are not in the sample" % len(absent))
    if MUTATE == "no_exclude":
        drop = set()
    kept = [r for r in res if (r["prompt"], r["writer"]) not in drop]
    if MUTATE == "main500_name":
        sample_name = "main500"
    R, _ = aggregate.resamples(seed, [r["prompt"] for r in kept], sample_name)
    strongest = {"full": evaluate.STRONGEST_FULL, "window": evaluate.STRONGEST_WINDOW}
    cells, _, _ = aggregate.summarise_cells(kept, R, strongest)
    return aggregate.reference_rows(cells), kept


def _dump(x):
    return json.dumps(run_main._clean(x), indent=1, sort_keys=True)


def run(args):
    if MUTATE:
        parts = os.path.normpath(os.path.abspath(args.out)).split(os.sep)
        if "results" in parts and ".tmp" not in parts:
            raise SystemExit("A4WO_MUTATE is set: not writing into results/")
    res = load_sample(args.cache)
    keys = [(r["prompt"], r["writer"]) for r in res]
    missing_a4 = sum(1 for r in res if not r.get("a4"))
    if not res or missing_a4 or len(set(keys)) != len(keys):
        raise SystemExit("the cache has %d sample results, %d without A4, %d duplicated"
                         % (len(res), missing_a4, len(keys) - len(set(keys))))
    sizes = {}
    for p, _ in keys:
        sizes[p] = sizes.get(p, 0) + 1
    with open(args.compare, encoding="utf-8") as f:
        want = json.load(f)
    if sizes != want["sample_sizes"] and MUTATE != "no_sizes":
        raise SystemExit("the sample of the cache is not the sample of %s" % args.compare)
    seed = seeds.read_seed()
    ref0, _ = a4_without(res, set(), seed, "main500")
    same = _dump(ref0) == _dump(want["main500"]["reference_A4"])
    print("positive control: reference_A4 of %d writers, %d cells %s %s"
          % (len(res), len(ref0), "identical to" if same else "DIFFERENT from", args.compare), flush=True)
    if not same and MUTATE != "no_positive":
        raise SystemExit(2)
    name, ref, kept = "main500", ref0, res
    if args.exclude:
        if args.expect_excluded is None:
            raise SystemExit("--exclude needs --expect-excluded")
        if args.sample_name in (None, "main500", "all"):
            raise SystemExit("with --exclude the resamples need a new sample name, not %s" % args.sample_name)
        drop, name = excluded_keys(args.exclude), args.sample_name
        pos = [i for i, k in enumerate(keys) if k in drop]
        ref, kept = a4_without(res, drop, seed, name)
        print("excluded %d at position(s) %s of the sorted sample, kept %d" % (len(res) - len(kept), pos, len(kept)),
              flush=True)
        if len(res) - len(kept) != args.expect_excluded:
            raise SystemExit("%d writer(s) excluded, expected %d" % (len(res) - len(kept), args.expect_excluded))
    kept_sizes = {}
    for r in kept:
        kept_sizes[r["prompt"]] = kept_sizes.get(r["prompt"], 0) + 1
    out = {"seed_file_sha256": run_main._sha(os.path.join(HERE, "..", "SEED")),
           "config_sha256": run_main._sha(os.path.join(HERE, "..", "config.json")),
           "cache": os.path.basename(os.path.normpath(args.cache)), "sample": name,
           "writers": len(kept), "excluded_writers": len(res) - len(kept), "sample_sizes": kept_sizes,
           "positive_control": "reference_A4 of the %d writers with main500 identical to main_a4.json" % len(res),
           "note": "A4 cells without the writer of the CPU chunks (deviation D3); aggregates only",
           "reference_A4": ref}
    if MUTATE:
        out["mutate"] = MUTATE
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    part = "%s.%d.part" % (args.out, os.getpid())
    with open(part, "w", encoding="utf-8", newline="\n") as f:
        f.write(_dump(out) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(part, args.out)
    print("wrote", args.out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache", required=True, help="the cache folder of the main_a4 stage (with its fingerprint)")
    ap.add_argument("--compare", required=True, help="main_a4.json: the positive control and the sample sizes")
    ap.add_argument("--exclude", help="JSON list of {prompt, writer, ...} to exclude (not printed)")
    ap.add_argument("--expect-excluded", type=int, help="with --exclude: stop unless this many writers are removed")
    ap.add_argument("--sample-name", help="with --exclude: the new name of the resamples (seed use bootstrap)")
    ap.add_argument("--out", required=True)
    run(ap.parse_args())


if __name__ == "__main__":
    main()
