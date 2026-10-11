"""Cross-check of the copy blocks' records against the segments synthesized from the copy text
(preregistration.md, "照らし合わせ").

  crosscheck.py --work <dir outside the repository> --copy results/copy_segments.json --out results/crosscheck.json

The alignment of every block (record segment values and groups) goes to <work>/alignment.json, outside the
repository. results/crosscheck.json holds aggregates only: counts, sums and the distribution of the differences.
"""
import argparse
import itertools
import os
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align import align  # noqa: E402
from common import load_config, prior_module, read_json, write_json, write_private_json  # noqa: E402

KINDS = {(1, 1): "1:1", (2, 1): "2:1", (1, 2): "1:2", (3, 1): "3:1", (1, 3): "1:3"}


def group_kind(g):
    return KINDS[(g[1] - g[0], g[3] - g[2])]


def diff_summary(diffs):
    if not diffs:
        return {"n": 0}
    return {"n": len(diffs), "exact": sum(1 for d in diffs if d == 0), "mean": statistics.fmean(diffs),
            "mean_abs": statistics.fmean(abs(d) for d in diffs), "min": min(diffs), "max": max(diffs),
            "hist": {str(k): v for k, v in sorted(Counter(diffs).items())}}


def habit_fit(pairs, rt):
    """pairs: [(record value, text units)]. Best habit set (smallest sum |diff|; ties: fewer habits, then the
    order of itertools.combinations over romaji_table.HABITS)."""
    best = None
    for r in range(len(rt.HABITS) + 1):
        for combo in itertools.combinations(rt.HABITS, r):
            hs = frozenset(combo)
            diffs = [x - rt.count_keys(u, hs) for x, u in pairs]
            s = sum(abs(d) for d in diffs)
            if best is None or s < best[0]:
                best = (s, list(combo), diffs)
    s, combo, diffs = best
    return {"habits": combo, "sum_abs": s, "exact": sum(1 for d in diffs if d == 0), "n": len(diffs),
            "mean": statistics.fmean(diffs) if diffs else None}


def check_block(x, stats, y, units, cfg, rt):
    lam, mg = cfg["alignment"]["lambda"], cfg["alignment"]["max_group"]
    groups = align(x, y, lam, mg)
    kinds = Counter(group_kind(g) for g in groups)
    cost = sum(abs(sum(x[g[0]:g[1]]) - sum(y[g[2]:g[3]])) for g in groups)
    out = {"segments": len(x), "groups": dict(sorted(kinds.items())), "text_reached": groups[-1][3] if groups else 0,
           "text_segments": len(y), "sum_abs_group_diff": cost,
           "record_keys": sum(x), "text_keys_aligned": sum(y[:groups[-1][3]]) if groups else 0}
    if stats is None:
        return out, groups
    classes = {"all": [], "no_bs_no_num": [], "bs": [], "num": []}
    habit_pairs = []
    for g in groups:
        if group_kind(g) != "1:1":
            continue
        i, j = g[0], g[2]
        d = x[i] - y[j]
        st = stats[i]
        classes["all"].append(d)
        if st["numeric"]:
            classes["num"].append(d)
        elif st["backspace"]:
            classes["bs"].append(d)
        else:
            classes["no_bs_no_num"].append(d)
            habit_pairs.append((x[i], units[j]))
    out["one_to_one"] = {c: diff_summary(v) for c, v in classes.items()}
    out["per_segment"] = {k: statistics.fmean(s[k] for s in stats) if stats else None
                          for k in ("enter", "space", "backspace", "numeric")}
    out["explore_habit_fit"] = habit_fit(habit_pairs, rt) if habit_pairs else None
    return out, groups


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--copy", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = load_config()
    rt = prior_module("romaji_table", cfg)
    recs = read_json(os.path.join(a.work, "records.json"))["blocks"]
    copy = read_json(a.copy)
    y, units = copy["keys"], copy["units"]
    res, detail = {}, {}
    for label in cfg["records"]["copy_blocks"]:
        b = recs[label]
        plain, g_plain = check_block(b["plain"], b["plain_stats"], y, units, cfg, rt)
        clean, g_clean = check_block(b["clean"], None, y, units, cfg, rt)
        res[label] = {"plain": plain, "clean": clean}
        detail[label] = {"plain": {"x": b["plain"], "groups": g_plain}, "clean": {"x": b["clean"], "groups": g_clean}}
    write_private_json(os.path.join(a.work, "alignment.json"), {"format": "g1-alignment/1", "blocks": detail})
    write_json(a.out, {"format": "g1-crosscheck/1", "alignment": cfg["alignment"], "blocks": res})
    print("crosscheck: %d blocks" % len(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
