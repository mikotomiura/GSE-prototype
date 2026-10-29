"""Self-test of exploratory analyses 6 and 7 (exploratory_lambda.py, exploratory_scan.py, align_local.py) on synthetic
writers (no human data). One synthetic run_main.run with a cache gives main.json and the main cache; then
(a) align_local: start fixed equals align_vec (window and full end); a free start equals the minimum over the suffixes
of the text (align_vec); a sequence embedded in a text costs 0; the chunks of 20 drop a last chunk under 5;
(b) analysis 6 passes its positive controls, agrees per writer with a naive scalar alignment (align_ext) at lambda 2
and 16, resumes from its cache with the same output, and stops on another seed, another pool, a main cache without a
writer, a main cache or main.json that differs in a control cell, a main strongest attacker that differs, and a cache
folder inside the main cache; (c) analysis 7 passes, agrees per writer with a naive scan (align_ext on every suffix,
chunk sums) and stops on an exploratory_lambda.json that differs; (d) no writer ID in the outputs or printed lines.
The synthetic pool (14 writers per prompt) is too small for N = 1,000, so the lambda 4 and 16 controls against
A2-lam4/A2-lam16 are exercised only on the real data.

    python -I scripts/selftest_exploratory_lambda.py       # PASS, then each mutant must be killed
"""
import argparse
import contextlib
import copy
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
import align_ext  # noqa: E402
import align_local as L  # noqa: E402
import align_vec  # noqa: E402
import attackers as A  # noqa: E402
import exploratory_lambda as X  # noqa: E402
import forms  # noqa: E402
import matching  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402

FAIL = []
PER, TAKE = 14, 4
MUTANTS = {"ignore_lam": "naive_lam", "decoy_draw": "positive6", "skip_positive": "guard_cells",
           "unsorted": "positive6", "skip_provenance": "guard_seed", "fixed_start": "unit_free",
           "keep_short_chunk": "unit_chunks", "chunk_min": "naive_scan"}


def check(name, cond):
    if not cond:
        FAIL.append(name)
        print("FAIL", name)


def ns(tmp, **kw):
    d = dict(source="synthetic", root=None, per_prompt=PER, per_prompt_sample=TAKE,
             main_cache=main_cache(tmp), compare_main=os.path.join(tmp, "main.json"),
             cache_dir=os.path.join(tmp, "xcache"), workers=1, time_first=0, out=os.path.join(tmp, "x6.json"))
    d.update(kw)
    return argparse.Namespace(**d)


def main_cache(tmp):
    return os.path.join(tmp, "cache_main", os.listdir(os.path.join(tmp, "cache_main"))[0])


def run(args, analysis, log=None):
    with contextlib.redirect_stdout(log if log is not None else io.StringIO()):
        return X.run(args, analysis)


def stops(args, analysis, why="", printed=""):
    out = io.StringIO()
    try:
        run(args, analysis, out)
    except SystemExit as e:
        return why in str(e) and printed in out.getvalue()
    return False


def unit():
    g = np.random.default_rng(5)
    ys = [list(g.integers(1, 9, g.integers(5, 40))) for _ in range(25)]
    prep = L.prepare(ys)
    first = free = True
    for _ in range(15):
        x = list(g.integers(1, 9, g.integers(1, 25)))
        for lam in (2, 8):
            for end in ("full", "window"):
                first &= np.array_equal(align_vec.costs(x, ys, lam, end), L.costs(x, prep, lam, "first", end))
            bf = [min(align_vec.costs(x, [y[s:]], lam, "window")[0] for s in range(len(y) + 1)) for y in ys]
            free &= np.array_equal(np.array(bf), L.costs(x, prep, lam, "free", "window"))
    check("unit_first", first)
    y = ys[0]
    check("unit_free", free and L.costs(y[4:12], L.prepare([y]), 8, "free", "window")[0] == 0)
    check("unit_chunks", [len(c) for c in L.chunks(list(range(44)))] == [20, 20]
          and [len(c) for c in L.chunks(list(range(45)))] == [20, 20, 5] and L.chunks([1, 2, 3]) == []
          and list(L.scan_costs([1, 2], prep, 8)) == [0.0] * len(ys))


def writers_and_pools(tmp):
    """The synthetic writers, pools and sample as exploratory_lambda.setup builds them."""
    cfg, seed, by_prompt, pool_ids, pools, sample, _ = X.setup(ns(tmp), 1)
    return cfg, seed, by_prompt, pool_ids, pools, sample


def naive_credit(seed, p, wid, ids, cost_of):
    """Mean credit over the N = 10 draws of a writer, the costs computed one candidate at a time."""
    me = ids.index(wid)
    cr = []
    for d in range(matching.DRAWS[10]):
        dec = matching.draw_decoys(seed, p, wid, 10, ids, {me}, d)
        cand = [me] + dec[0]
        c = np.array([cost_of(i) for i in cand])
        cr.append(matching.credit_stats(0, c)[0])
    return float(np.mean(cr))


def naive_checks(tmp, analysis, cache):
    cfg, seed, by_prompt, pool_ids, pools, sample = writers_and_pools(tmp)
    ok, n = True, 0
    for p in sorted(sample)[:2]:
        wid = sample[p][0]
        w = by_prompt[p][wid]
        r = run_main._cache_load(cache, (w, True, False))
        for f in ("R3", "R4(2)", "R7(0.25)"):
            rel = forms.release(w.rows, f, seed, p, wid)
            groups, cap = A._groups(rel, cfg)
            x = A.record_values(rel)
            ys = [A.text_values(c, rel) for c in pools[p]]
            for lam in (2, 16):
                if analysis == 6:
                    cost_of = lambda i: align_ext.align(x, ys[i], lam, "full", groups, cap)[0]  # noqa: E731
                    att = X.name("A2", lam)
                else:
                    def cost_of(i):
                        tot = 0.0
                        for ch in naive_chunks(x):
                            tot += min(align_ext.align(ch, ys[i][s:], lam, "window", groups, cap)[0]
                                       for s in range(len(ys[i]) + 1))
                        return tot
                    att = X.name("A2scan", lam)
                got = r["full"][("full", f, att, 10)]["acc"]
                n += 1
                ok &= abs(naive_credit(seed, p, wid, pool_ids[p], cost_of) - got) < 1e-12
    return ok and n == 12


def naive_chunks(x):
    out = [x[i:i + 20] for i in range(0, len(x), 20)]
    return out[:-1] if out and len(out[-1]) < 5 else out


def tests(tmp):
    unit()
    with open(os.path.join(tmp, "main.json"), encoding="utf-8") as f:
        want = json.load(f)
    log = io.StringIO()
    try:
        a = run(ns(tmp), 6, log)
    except SystemExit as e:
        check("positive6", False)
        print("(stopped: %s)" % e)
        return
    check("positive6", all(v["acc"] is not None for v in a["cells"].values()) and
          all(X.dp_utility_r0._dump(a["cells"]["full|%s|%s|10" % (f, X.name("A2", 8))])
              == X.dp_utility_r0._dump(want["main500"]["cells"]["full|%s|A2|10" % f])
              for f in X.FORMS))
    check("strongest6", set(a["strongest"]) == {"full|%s|10" % f for f in X.FORMS} and
          all(e["acc"] >= e["main_strongest"]["acc"] for e in a["strongest"].values()))
    cache6 = os.path.join(tmp, "xcache", "analysis6", a["caches"]["this"])
    check("naive_lam", naive_checks(tmp, 6, cache6))
    # resume: from a full cache and from a half-deleted one, the same output
    pk = sorted(os.listdir(cache6))
    for x in pk[::2]:
        os.remove(os.path.join(cache6, x))
    b = run(ns(tmp, out=os.path.join(tmp, "x6b.json")), 6)
    check("resume", X.dp_utility_r0._dump(b) == X.dp_utility_r0._dump(a))
    # guards
    c_out = os.path.join(tmp, "c.json")

    def bad_json(change, fname):
        other = copy.deepcopy(want)
        change(other)
        path = os.path.join(tmp, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(other, f)
        return path

    check("guard_seed", stops(ns(tmp, out=c_out, compare_main=bad_json(
        lambda o: o.update(seed_file_sha256="0" * 64), "s.json")), 6, "seed or the config"))
    p0 = sorted(want["writers_after_exclusion"])[0]
    check("guard_pool", stops(ns(tmp, out=c_out, compare_main=bad_json(
        lambda o: o["writers_after_exclusion"].update({p0: 1}), "p.json")), 6, "pool or the sample"))
    check("guard_cells", stops(ns(tmp, out=c_out, compare_main=bad_json(
        lambda o: o["main500"]["cells"]["full|R3|A2|10"].update(acc=-1.0), "c1.json")), 6, "2",
        "positive control cells against main.json: 1 differ"))
    check("guard_strongest", stops(ns(tmp, out=c_out, compare_main=bad_json(
        lambda o: o["main500"]["strongest"]["full|R3|10"].update(acc=-1.0), "c2.json")), 6, "2",
        "positive control main strongest attacker: 1 differ"))
    bad_dir = os.path.join(tmp, "main_bad")
    for change, why, printed, label in (("drop", "lacks 1 of", "", "guard_keys"),
                                        ("cell", "2", "positive control A2 and A1' at lambda 8: 1 differ",
                                         "guard_writer")):
        shutil.rmtree(bad_dir, ignore_errors=True)
        shutil.copytree(main_cache(tmp), bad_dir)
        p = sorted(want["sample_sizes"])[0]
        cfg, seed, by_prompt, pool_ids, pools, sample = writers_and_pools(tmp)
        path = run_main._cache_path(bad_dir, (by_prompt[p][sample[p][0]], True, False))
        if not os.path.exists(path):
            path = run_main._cache_path(bad_dir, (by_prompt[p][sample[p][0]], True, True))
        if change == "drop":
            os.remove(path)
        else:
            with open(path, "rb") as f:
                key, r = pickle.load(f)
            r["full"][("full", "R7(0.5)", "A1p", 10)]["acc"] += 0.5
            with open(path, "wb") as f:
                pickle.dump((key, r), f)
        check(label, stops(ns(tmp, out=c_out, main_cache=bad_dir), 6, why, printed))
    shutil.rmtree(bad_dir, ignore_errors=True)
    check("guard_cache_dir", stops(ns(tmp, out=c_out, cache_dir=os.path.join(tmp, "main_cache")), 6,
                                   "not be the main cache"))
    # analysis 7
    a6_path = os.path.join(tmp, "x6.json")
    args7 = ns(tmp, out=os.path.join(tmp, "x7.json"), lambda_cache=cache6, compare_lambda=a6_path)
    try:
        s = run(args7, 7, log)
    except SystemExit as e:
        check("positive7", False)
        print("(stopped: %s)" % e)
        return
    check("positive7", all(v["acc"] is not None for v in s["cells"].values())
          and {k.split("|")[2] for k in s["cells"]} == set(X.variants(7))
          and all(e["acc"] >= a["strongest"][g]["acc"] for g, e in s["strongest"].items()))
    cache7 = os.path.join(tmp, "xcache", "analysis7", s["caches"]["this"])
    check("naive_scan", naive_checks(tmp, 7, cache7))
    with open(a6_path, encoding="utf-8") as f:
        want6 = json.load(f)
    k6 = sorted(want6["cells"])[0]
    want6["cells"][k6]["acc"] = -1.0
    bad6 = os.path.join(tmp, "bad6.json")
    with open(bad6, "w", encoding="utf-8") as f:
        json.dump(want6, f)
    check("guard_lambda", stops(ns(tmp, out=c_out, lambda_cache=cache6, compare_lambda=bad6), 7, "2",
                                "positive control analysis 6 cells against bad6.json: 1 differ"))
    # no writer ID
    ids = {w for p in want["sample_sizes"] for w in writers_and_pools(tmp)[3][p]}
    text = "".join(open(os.path.join(tmp, n), encoding="utf-8").read() for n in ("x6.json", "x7.json")) \
        + log.getvalue()
    check("no_ids", not any(re.search(r"\b%s\b" % re.escape(w), text) for w in ids))


def build(tmp):
    args = argparse.Namespace(source="synthetic", root=None, out=os.path.join(tmp, "main.json"), workers=1,
                              all=False, forms="main", a4_dir=None, a4_partial=False, per_prompt=PER,
                              per_prompt_sample=TAKE, open_world_n=10, no_timing=True,
                              cache_dir=os.path.join(tmp, "cache_main"), exploratory_3_5=None)
    with contextlib.redirect_stdout(io.StringIO()):
        run_main.run(args)


def with_run(tmp, build_main=True):
    if build_main:
        build(tmp)
    tests(tmp)
    if FAIL:
        print("FAIL", len(FAIL))
        return 1
    print("PASS (unmutated)")
    for m, killer in MUTANTS.items():
        p = subprocess.run([sys.executable, "-I", os.path.abspath(__file__)], capture_output=True, text=True,
                           env=dict(os.environ, EXL_MUTATE=m, EXL_SELFTEST_DIR=tmp))
        failed = {l.split()[1] for l in p.stdout.splitlines() if l.startswith("FAIL ") and len(l.split()) == 2
                  and not l.split()[1].isdigit()}
        killed = p.returncode != 0 and killer in failed
        print("mutant %-16s -> %s" % (m, ("killed by " + ",".join(sorted(failed))) if killed
                                      else "NOT KILLED (wanted %s; %s)" % (killer, sorted(failed))))
        if not killed:
            FAIL.append("mutant " + m)
    print("FAIL" if FAIL else "PASS", len(FAIL))
    return 1 if FAIL else 0


def main():
    if os.environ.get("EXL_MUTATE"):  # a mutant, on the main run of the parent (EXL_SELFTEST_DIR)
        tmp = os.environ["EXL_SELFTEST_DIR"]
        try:
            tests(tmp)
        except Exception as e:  # noqa: BLE001  (a crash of a mutant is reported, not lost)
            FAIL.append("crash")
            print("FAIL crash\n(%s)" % type(e).__name__)
        print("FAIL" if FAIL else "PASS", len(FAIL))
        return 1 if FAIL else 0
    keep = os.environ.get("EXL_KEEP_DIR")  # reuse the synthetic main run of an earlier self-test (debugging)
    tmp = keep or tempfile.mkdtemp(prefix="exlselftest")
    try:
        return with_run(tmp, build_main=not (keep and os.path.exists(os.path.join(tmp, "main.json"))))
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
