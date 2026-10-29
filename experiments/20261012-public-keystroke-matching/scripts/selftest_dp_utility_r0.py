"""Self-test of dp_utility_r0.py on synthetic writers (no human data): two run_main.run with caches, the main forms
and --forms dp, then (a) the dp run alone has no ratio to R0 (the output of deviation D5 reproduced), (b) the script
fills the ratios and correlations with R0 for every form, agrees with a naive count and with both runs, gives the
same output when the main cache holds writers outside the sample (as the all stage adds them), and (c) a main
cache without a writer of the sample, a dp cache without one, an R3 that differs between the caches, or another
main.json stop it.

    python -I scripts/selftest_dp_utility_r0.py            # PASS, then each mutant must be killed
"""
import argparse
import contextlib
import glob
import io
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dp_utility_r0 as T  # noqa: E402
import forms  # noqa: E402
import run_main  # noqa: E402
import utility  # noqa: E402

FAIL = []
PER, TAKE = 14, 4
MUTANTS = {"no_r0": "positive", "unsorted": "positive", "sample_from_main": "superset", "skip_keys": "keys_guard",
           "skip_r3": "r3_guard", "no_positive": "compare_guard"}


def check(name, cond):
    if not cond:
        FAIL.append(name)
        print("FAIL", name)


def ns(tmp, main_cache, dp_cache, **kw):
    d = dict(source="synthetic", root=None, per_prompt=PER, main_cache=main_cache, dp_cache=dp_cache,
             compare_main=os.path.join(tmp, "main.json"), compare_dp=os.path.join(tmp, "dp.json"),
             out=os.path.join(tmp, "out.json"))
    d.update(kw)
    return argparse.Namespace(**d)


def stops(args, why=""):
    """True when T.run stops, with why in its message."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            T.run(args)
    except SystemExit as e:
        return why in str(e)
    return False


def caches(tmp):
    return (os.path.join(tmp, "cache_main", os.listdir(os.path.join(tmp, "cache_main"))[0]),
            os.path.join(tmp, "cache_dp", os.listdir(os.path.join(tmp, "cache_dp"))[0]))


def sample_pickles(cache):
    out = []
    for path in sorted(glob.glob(os.path.join(cache, "*.pkl"))):
        with open(path, "rb") as f:
            key, r = pickle.load(f)
        if key[2]:
            out.append((path, r))
    return out


def tests(tmp):
    main_cache, dp_cache = caches(tmp)
    with open(os.path.join(tmp, "main.json"), encoding="utf-8") as f:
        want_main = json.load(f)
    with open(os.path.join(tmp, "dp.json"), encoding="utf-8") as f:
        want_dp = json.load(f)
    du = want_dp["main500"]["utility"]
    # (a) the dp run alone: no ratio and no correlation with R0 for any form (D5)
    check("reproduce_empty", all(e["ratio_median"]["mean"] is None and e["spearman_r0"]["mean"] is None
                                 and e["ratio_dropped_r0"] == sum(want_dp["sample_sizes"].values())
                                 for e in du.values()))
    # (b) the script
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            a = T.run(ns(tmp, main_cache, dp_cache))
    except SystemExit as e:
        check("positive", False)
        print("(stopped: %s)" % e)
        return
    u = a["utility"]
    check("positive", a["writers"] == sum(want_main["sample_sizes"].values()) and set(u) == set(du)
          and all(T._dump(u[k]) == T._dump(want_main["main500"]["utility"][k]) for k in u if k.endswith("|R3")))
    check("filled", all(any(u["%s|%s" % (m, f)]["ratio_median"]["mean"] is not None for m in utility.METRICS)
                        and any(u["%s|%s" % (m, f)]["spearman_r0"]["mean"] is not None for m in utility.METRICS)
                        for f in forms.DP))
    # naive: the per-prompt median of form / R0 over the writers with both, then the mean over the prompts
    main_r = {(r["prompt"], r["writer"]): r for _, r in sample_pickles(main_cache)}
    dp_r = [r for _, r in sample_pickles(dp_cache)]
    ok, n = True, 0
    for f in forms.DP[1:]:
        for m in utility.METRICS:
            per = {}
            for r in dp_r:
                r0, v = main_r[(r["prompt"], r["writer"])]["utility"]["R0"].get(m), r["utility"][f].get(m)
                if r0 not in (None, 0) and v is not None and np.isfinite(r0) and np.isfinite(v):
                    per.setdefault(r["prompt"], []).append(v / r0)
            got = u["%s|%s" % (m, f)]["ratio_median"]["mean"]
            if per and len(per) == len(want_dp["sample_sizes"]):
                n += 1
                ok = ok and got is not None and abs(np.mean([np.median(x) for x in per.values()]) - got) < 1e-9
    check("naive", ok and n > 0)
    # a main cache with a writer outside the sample (as the all stage adds them): the same output
    big_dir = os.path.join(tmp, "main_big")
    shutil.rmtree(big_dir, ignore_errors=True)
    shutil.copytree(main_cache, big_dir)
    path, r = sample_pickles(big_dir)[0]
    with open(path, "rb") as f:
        key, r = pickle.load(f)
    r = dict(r, writer="extra-writer")
    with open(os.path.join(big_dir, "extra.pkl"), "wb") as f:
        pickle.dump(([key[0], "extra-writer", True, False], r), f)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            s = T.run(ns(tmp, big_dir, dp_cache, out=os.path.join(tmp, "s.json")))
        check("superset", T._dump(s["utility"]) == T._dump(u) and s["writers"] == a["writers"])
    except SystemExit:
        check("superset", False)
    # (c) guards, on copies of the caches
    os.remove(sample_pickles(big_dir)[1][0])
    check("keys_guard", stops(ns(tmp, big_dir, dp_cache, out=os.path.join(tmp, "c.json")), "lacks 1 of"))
    shutil.rmtree(big_dir)
    bad_dir = os.path.join(tmp, "dp_bad")
    shutil.rmtree(bad_dir, ignore_errors=True)
    shutil.copytree(dp_cache, bad_dir)
    os.remove(sample_pickles(bad_dir)[0][0])
    check("sizes_guard", stops(ns(tmp, main_cache, bad_dir, out=os.path.join(tmp, "c.json")), "not the sample"))
    shutil.rmtree(bad_dir)
    shutil.copytree(dp_cache, bad_dir)
    path, _ = sample_pickles(bad_dir)[0]
    with open(path, "rb") as f:
        key, r = pickle.load(f)
    m0 = next(m for m in utility.METRICS if r["utility"]["R3"].get(m) is not None)
    r["utility"]["R3"][m0] = r["utility"]["R3"][m0] + 1.0
    with open(path, "wb") as f:
        pickle.dump((key, r), f)
    check("r3_guard", stops(ns(tmp, main_cache, bad_dir, out=os.path.join(tmp, "c.json")), "R3 utility"))
    shutil.rmtree(bad_dir)
    other = json.loads(json.dumps(want_main))
    other["main500"]["utility_figure"]["R3"]["median_spearman_r0"] = -2.0
    bad = os.path.join(tmp, "bad_main.json")
    with open(bad, "w", encoding="utf-8") as f:
        json.dump(other, f)
    check("compare_guard", stops(ns(tmp, main_cache, dp_cache, compare_main=bad, out=os.path.join(tmp, "c.json"))))
    # no writer ID in the output or the printed lines
    ids = {w for _, w in main_r}
    text = open(os.path.join(tmp, "out.json"), encoding="utf-8").read() + log.getvalue()
    check("no_ids", not any(re.search(r"\b%s\b" % re.escape(w), text) for w in ids))


def build(tmp):
    """Two synthetic run_main.run (main forms, then --forms dp) with caches in tmp."""
    for name, fs in (("main", "main"), ("dp", "dp")):
        args = argparse.Namespace(source="synthetic", root=None, out=os.path.join(tmp, name + ".json"), workers=1,
                                  all=False, forms=fs, a4_dir=None, a4_partial=False, per_prompt=PER,
                                  per_prompt_sample=TAKE, open_world_n=10, no_timing=True,
                                  cache_dir=os.path.join(tmp, "cache_" + name), exploratory_3_5=None)
        with contextlib.redirect_stdout(io.StringIO()):
            run_main.run(args)


def with_run(tmp):
    build(tmp)
    tests(tmp)
    if FAIL:
        print("FAIL", len(FAIL))
        return 1
    print("PASS (unmutated)")
    for m, killer in MUTANTS.items():
        p = subprocess.run([sys.executable, "-I", os.path.abspath(__file__)], capture_output=True, text=True,
                           env=dict(os.environ, DPU_MUTATE=m, DPU_SELFTEST_DIR=tmp))
        failed = {l.split()[1] for l in p.stdout.splitlines() if l.startswith("FAIL ") and len(l.split()) == 2
                  and not l.split()[1].isdigit()}
        killed = p.returncode != 0 and killer in failed
        print("mutant %-15s -> %s" % (m, ("killed by " + ",".join(sorted(failed))) if killed
                                     else "NOT KILLED (wanted %s; %s)" % (killer, sorted(failed))))
        if not killed:
            FAIL.append("mutant " + m)
    print("FAIL" if FAIL else "PASS", len(FAIL))
    return 1 if FAIL else 0


def main():
    if os.environ.get("DPU_MUTATE"):  # a mutant, on the runs of the parent (DPU_SELFTEST_DIR)
        try:
            tests(os.environ["DPU_SELFTEST_DIR"])
        except Exception as e:  # noqa: BLE001  (a crash of a mutant is reported, not lost)
            FAIL.append("crash")
            print("FAIL crash\n(%s)" % type(e).__name__)
        print("FAIL" if FAIL else "PASS", len(FAIL))
        return 1 if FAIL else 0
    tmp = tempfile.mkdtemp(prefix="dpuselftest")
    try:
        return with_run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
