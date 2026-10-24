"""The A4 cells without the writer whose A4 chunks were generated on the CPU (deviation D3, notes.md): the same
aggregation as run_main.run does for main500 (aggregate.resamples -> aggregate.summarise_cells ->
aggregate.reference_rows), on the per-writer results that the main_a4 stage left in its cache (deviation D4), with
the excluded writers removed and resamples under a new sample name. Only aggregates are written; no writer ID.

This script is not imported by run_main.py, so it is not in the cache fingerprint; it never calls cache_fingerprint.
The cache folder is trusted (pickle): point --cache only at the folder run_main.py wrote.

    python -I scripts/a4_without_cpu_writer.py --cache raw/derived/main_cache/<fingerprint 16> \
        --exclude raw/derived_a4_cpu_fallback_writers.json --sample-name main500_without_cpu_writer \
        --out results/main_a4_without_cpu_writer.json
    python -I scripts/a4_without_cpu_writer.py --cache ... --sample-name main500 --compare results/main_a4.json \
        --out results/.tmp/a4_positive_control.json      # no --exclude: positive control against main_a4.json
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
        if key[2] or MUTATE == "keep_cost_only":
            res.append(r)
    if MUTATE != "unsorted":
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
    res = load_sample(args.cache)
    missing_a4 = sum(1 for r in res if not r.get("a4"))
    if not res or missing_a4:
        raise SystemExit("the cache has %d sample results, %d without A4" % (len(res), missing_a4))
    drop = excluded_keys(args.exclude) if args.exclude else set()
    if args.expect_excluded is not None and len(drop) != args.expect_excluded:
        raise SystemExit("%d writer(s) to exclude, expected %d" % (len(drop), args.expect_excluded))
    if not drop and args.sample_name != "main500":
        raise SystemExit("without --exclude the sample name must be main500 (the positive control)")
    if drop and args.sample_name == "main500":
        raise SystemExit("with --exclude the resamples need a new sample name, not main500")
    pos = [i for i, r in enumerate(res) if (r["prompt"], r["writer"]) in drop]
    ref, kept = a4_without(res, drop, seeds.read_seed(), args.sample_name)
    print("sample %d writers, excluded %d at position(s) %s of the sorted sample, kept %d"
          % (len(res), len(res) - len(kept), pos, len(kept)), flush=True)
    sizes = {}
    for r in kept:
        sizes[r["prompt"]] = sizes.get(r["prompt"], 0) + 1
    out = {"seed_file_sha256": run_main._sha(os.path.join(HERE, "..", "SEED")),
           "config_sha256": run_main._sha(os.path.join(HERE, "..", "config.json")),
           "cache": os.path.basename(os.path.normpath(args.cache)), "sample": args.sample_name,
           "writers": len(kept), "excluded_writers": len(res) - len(kept), "sample_sizes": sizes,
           "note": "A4 cells without the writer of the CPU chunks (deviation D3); aggregates only",
           "reference_A4": ref}
    if MUTATE:
        out["mutate"] = MUTATE
    if args.compare:
        with open(args.compare, encoding="utf-8") as f:
            want = json.load(f)["main500"]["reference_A4"]
        same = _dump(ref) == _dump(want)
        print("positive control: reference_A4 of %d cells %s %s" % (len(want), "identical to" if same
                                                                       else "DIFFERENT from", args.compare))
        if not same:
            raise SystemExit(2)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out + ".part", "w", encoding="utf-8", newline="\n") as f:
        f.write(_dump(out) + "\n")
    os.replace(args.out + ".part", args.out)
    print("wrote", args.out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache", required=True, help="the cache folder of the main_a4 stage (with its fingerprint)")
    ap.add_argument("--exclude", help="JSON list of {prompt, writer, ...} to exclude (not printed)")
    ap.add_argument("--expect-excluded", type=int, help="stop unless --exclude lists this many writers")
    ap.add_argument("--sample-name", required=True, help="the name of the resamples (seed use bootstrap)")
    ap.add_argument("--compare", help="main_a4.json: stop unless reference_A4 is identical (positive control)")
    ap.add_argument("--out", required=True)
    run(ap.parse_args())


if __name__ == "__main__":
    main()
