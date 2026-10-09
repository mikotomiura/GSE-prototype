"""Exploratory, post hoc (not in preregistration.md): the accuracy of L_none and S_no_time split by how many
trials of the window come from a scenario that changes the key count (S6, S8, S10; design.md section 4).

  explore_procedure_noise.py --trials raw/trials.json --prepare results/prepare.json --dist-dir raw/dist
                             --dist-summary results/distances.json --out results/explore_procedure_noise.json

Added after the results, to explain why the accuracy of the length-only attacker does not grow monotonically
with k. The windows and the decoys are drawn with the same seeds as matching.py, so every window gets the same
candidates as in the main computation; only the grouping is new. Accuracies are means over windows (no interval).
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402
import data as dataload  # noqa: E402
import matching  # noqa: E402

COUNT_CHANGING = ("S6", "S8", "S10")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for name in ("trials", "prepare", "dist-dir", "dist-summary", "out"):
        ap.add_argument("--" + name, required=True)
    a = ap.parse_args(argv)
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg)
    d = dataload.load(cfg, kit, a.trials, a.prepare, a.dist_dir, a.dist_summary, ["S_no_time"])
    seed = kitload.read_seed()
    trials, pools, typed, R, true_j = d["trials"], d["pools"], d["typed"], d["R"], d["true_j"]
    out = []
    for k in cfg["windows"]["k"]:
        for N in cfg["N"]:
            groups = {}
            for b, st, tids in matching.windows_of(trials, k):
                scs = [trials[t]["scenario"] for t in tids]
                rng = random.Random(kitload.seed_int(seed, matching.TAG, "decoys", k, N, b, st))
                decoys, _ = matching.draw_decoys(rng, N, [len(pools[s]) for s in scs], [typed[s] for s in scs],
                                                 [trials[t]["typed"] for t in tids])
                jcols = [list(col) for col in zip(*decoys)]
                tjs = [true_j[t] for t in tids]
                rcols = [list(map(R[s].__getitem__, col)) for s, col in zip(scs, jcols)]
                rtrue = [R[s][j] for s, j in zip(scs, tjs)]
                x = [trials[t]["c"] for t in tids]
                cl = matching.credit(*matching.l_scores(cfg["variants"]["L_none"], x, rcols, rtrue))
                cs_ = matching.credit(*matching.s_scores(d["dist"]["S_no_time"], tids, jcols, tjs))
                n_noisy = sum(1 for s in scs if s in COUNT_CHANGING)
                key = "0" if n_noisy == 0 else ("1" if n_noisy == 1 else "2+")
                g = groups.setdefault(key, [0, 0.0, 0.0])
                g[0] += 1
                g[1] += cl
                g[2] += cs_
            out.append({"k": k, "N": N, "by_n_count_changing": dict(
                (key, {"n_windows": g[0], "L_none": g[1] / g[0], "S_no_time": g[2] / g[0]})
                for key, g in sorted(groups.items()))})
    kitload.write_json(a.out, {"format": "matching-attack-explore-procedure-noise/1", "post_hoc": True,
                               "count_changing_scenarios": list(COUNT_CHANGING), "cells": out})
    for c in out:
        print("k=%d N=%d " % (c["k"], c["N"]) + "  ".join(
            "%s: n=%d L %.3f S %.3f" % (key, v["n_windows"], v["L_none"], v["S_no_time"])
            for key, v in c["by_n_count_changing"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
