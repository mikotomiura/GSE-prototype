"""Segments of the copy text and of the 1,500 decoy works under the G1 rule.

  build_corpus.py --zips <earlier experiment's raw/zips> --out raw/corpus_g1.json
                  --copy-out results/copy_segments.json --stats results/corpus_g1_stats.json [--processes 4]

The works are the earlier experiment's corpus (corpus_stats.json corpus_work_ids, in that order); every zip is
checked against corpus_manifest.json before it is read. The output holds only key counts per segment (-1 for an
invalid segment); it is public-domain text, derived. JSON, not pickle.
"""
import argparse
import os
import statistics
import sys
from multiprocessing import Pool


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (check_corpus_current, check_inputs, corpus_build_key, load_config, read_json, repo_path,  # noqa: E402
                    sha256_file, stats_body_sha256, write_json)
from g1rule import G1Rule, copy_lines

_RULE = None
_INIT_ERROR = None


def _init():
    """Pool initializer. An exception here would make the pool respawn workers forever, so it is kept and
    raised by the first task instead."""
    global _RULE, _INIT_ERROR
    try:
        _RULE = G1Rule(load_config())
    except BaseException as ex:  # noqa: BLE001 - re-raised as RuntimeError in work_keys
        _INIT_ERROR = "%s: %s" % (type(ex).__name__, ex)


def work_keys(task):
    if _INIT_ERROR is not None:
        raise RuntimeError("build_corpus: worker initialisation failed: %s" % _INIT_ERROR)
    work_id, path, want = task
    bs = _RULE.bs
    if sha256_file(path) != want:
        raise RuntimeError("build_corpus: %s does not match the manifest" % path)  # not SystemExit: a pool worker
    text, _ = bs.read_zip_text(path)
    lines, _ = bs.body_lines(text)
    return work_id, [k for k, _ in _RULE.segments_of_lines(lines)]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--copy-out", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--processes", type=int, default=4)
    ap.add_argument("--check", action="store_true", help="exit 0 when the outputs are current, 1 otherwise")
    a = ap.parse_args(argv)
    cfg = load_config()
    if a.check:
        try:
            check_inputs(cfg)
            check_corpus_current(cfg, a.stats, a.out, a.copy_out)
        except (SystemExit, OSError, ValueError) as ex:
            print("build_corpus: not current: %s" % ex)
            return 1
        print("build_corpus: current")
        return 0
    if not a.zips:
        raise SystemExit("build_corpus: --zips is required to build")
    check_inputs(cfg)

    rule = G1Rule(cfg)
    segs = rule.segments_of_lines(copy_lines(repo_path(cfg["inputs"]["copy_text"]["path"])))
    if any(k < 0 for k, _ in segs):
        raise SystemExit("build_corpus: the copy text has an invalid segment")
    write_json(a.copy_out, {"format": "copy-segments/1", "keys": [k for k, _ in segs], "units": [u for _, u in segs]})

    stats_in = read_json(repo_path(cfg["inputs"]["corpus_stats"]["path"]))
    manifest = read_json(repo_path(cfg["inputs"]["corpus_manifest"]["path"]))
    sha = {e["work_id"]: e["sha256"] for e in manifest["works"] if e["role"] == "corpus" and "sha256" in e}
    ids = stats_in["corpus_work_ids"]
    tasks = [(w, os.path.join(a.zips, w + ".zip"), sha[w]) for w in ids]
    out = {}
    if a.processes > 1:
        with Pool(a.processes, initializer=_init) as pool:
            for n, (w, keys) in enumerate(pool.imap(work_keys, tasks, chunksize=4), 1):
                out[w] = keys
                if n % 100 == 0:
                    print("build_corpus: %d works" % n, flush=True)
    else:
        _init()
        for t in tasks:
            w, keys = work_keys(t)
            out[w] = keys
    keys = [out[w] for w in ids]
    write_json(a.out, {"format": "corpus-g1/1", "work_ids": ids, "keys": keys})
    valid = [v for ks in keys for v in ks if v >= 0]
    n_seg = sum(len(ks) for ks in keys)
    stats = {
        "format": "corpus-g1-stats/1",
        "works": len(ids),
        "segments": n_seg,
        "valid": len(valid),
        "valid_fraction": len(valid) / n_seg,
        "zero_valid": sum(1 for v in valid if v == 0),
        "mean_valid": statistics.fmean(valid),
        "median_valid": statistics.median(valid),
        "copy_segments": len(segs),
        "copy_keys_total": sum(k for k, _ in segs),
        "corpus_sha256": sha256_file(a.out),
        "copy_segments_sha256": sha256_file(a.copy_out),
        "build_key": corpus_build_key(cfg),
    }
    stats["body_sha256"] = stats_body_sha256(stats)
    write_json(a.stats, stats)
    print("build_corpus: %d works, %d segments (%d valid), copy text %d segments"
          % (len(ids), n_seg, len(valid), len(segs)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
