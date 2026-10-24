"""Self-test of a4_without_cpu_writer.py on synthetic writers (no human data, no GPU): a run_main.run with fake A4
reconstructions and a cache, then (a) without --exclude the A4 cells are identical to the run's reference_A4,
(b) one excluded writer is gone from every A4 cell, with the means of a naive count and the new sample name,
(c) a writer to exclude that is not in the sample stops the script, and the other guards stop it too.

    python -I scripts/selftest_a4_without_cpu_writer.py            # PASS, then each mutant must be killed
"""
import argparse
import glob
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
import a4_keytar  # noqa: E402
import a4_without_cpu_writer as T  # noqa: E402
import aggregate  # noqa: E402
import corpus  # noqa: E402
import evaluate  # noqa: E402
import matching  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402

FAIL = []
MUTANTS = {"no_exclude": "excluded", "absent_ok": "absent", "main500_name": "new_name", "unsorted": "positive",
           "keep_cost_only": "positive"}


def check(name, cond):
    if not cond:
        FAIL.append(name)
        print("FAIL", name)


def fake_a4(seed, tmp, per, take):
    """Reconstructions equal to the true text and windows (as selftest_a4.py); returns the sample."""
    ws = corpus.synthetic_corpus(seed, prompts=4, per_prompt=per, tag="main")
    kept = {}
    for w in ws:
        w.rows = corpus.active_rows(w.rows)
        if not corpus.exclusion_reason(w):
            kept.setdefault(w.prompt, {})[w.writer] = w
    sample = matching.eval_sample(seed, {p: list(v) for p, v in kept.items()}, take)
    for p, ids in sample.items():
        for wid in ids:
            w = kept[p][wid]
            inputs = a4_keytar.writer_inputs(w.rows, w.text, seed, p, wid)
            words = re.findall(r"[A-Za-z0-9]+", w.text)
            # every other writer gets the text of another writer of the prompt, so that A4 is not right for all
            other = kept[p][ids[(ids.index(wid) + 1) % len(ids)]].text if ids.index(wid) % 2 else None
            rec = {}
            for v, d in inputs.items():
                win = {}
                for key in d["windows"]:
                    k, si = map(int, key.split(":"))
                    final, origins = corpus.replay_origins(w.rows)
                    valid, _ = matching.true_window_starts(w.rows, final, origins,
                                                           re.findall(r"[A-Za-z0-9]+", final), words, k)
                    s = valid[si][2]
                    win[key] = " ".join((re.findall(r"[A-Za-z0-9]+", other)[:k]) if other else words[s:s + k])
                rec[v] = {"full": other or w.text, "windows": win}
            with open(os.path.join(tmp, "%s__%s.json" % (p, wid)), "w", encoding="utf-8") as f:
                json.dump({"prompt": p, "writer": wid, "variants": rec, "stats": {},
                           "source": a4_keytar.source_hashes(w),
                           "fingerprint": dict(a4_keytar.fingerprint(), dry=False)}, f)
    return sample


def ns(**kw):
    d = dict(exclude=None, expect_excluded=None, compare=None)
    d.update(kw)
    return argparse.Namespace(**d)


def stops(args):
    try:
        T.run(args)
    except SystemExit:
        return True
    return False


def tests(tmp, cache, run_out, sample):
    seed = seeds.read_seed()
    with open(run_out, encoding="utf-8") as f:
        want = json.load(f)["main500"]["reference_A4"]
    # (a) positive control: no exclusion, the run's sample name
    a = T.run(ns(cache=cache, sample_name="main500", compare=run_out, out=os.path.join(tmp, "a.json")))
    check("positive", a["writers"] == sum(len(v) for v in sample.values()) and a["excluded_writers"] == 0
          and T._dump(a["reference_A4"]) == T._dump(want))
    # (b) one writer excluded
    p0 = sorted(sample)[1]
    w0 = sample[p0][0]
    ex = os.path.join(tmp, "exclude.json")
    with open(ex, "w", encoding="utf-8") as f:
        json.dump([{"n": 0, "prompt": p0, "writer": w0, "where": []}], f)
    b = T.run(ns(cache=cache, exclude=ex, expect_excluded=1, sample_name="sel_without",
                 out=os.path.join(tmp, "b.json")))
    full = {k: v for k, v in want.items()}
    check("excluded", b["writers"] == a["writers"] - 1 and b["excluded_writers"] == 1
          and b["sample_sizes"][p0] == a["sample_sizes"][p0] - 1
          and all(b["reference_A4"][k]["writers"] == full[k]["writers"] - 1 for k in full))
    # naive: the mean over the kept writers of each A4 cell, from the pickles read here directly
    rs = []
    for path in glob.glob(os.path.join(cache, "*.pkl")):
        with open(path, "rb") as f:
            key, r = pickle.load(f)
        if key[2] and (r["prompt"], r["writer"]) != (p0, w0):
            rs.append(r)
    ok = True
    for name, c in b["reference_A4"].items():
        sc = name.split("|")[0]
        vals = [r[sc][k]["acc"] for r in rs for k in r[sc] if aggregate._name(k) == name]
        ok = ok and len(vals) == c["writers"] and abs(np.mean(vals) - c["acc"]) < 1e-12
    check("naive", ok and len(b["reference_A4"]) == len(want))
    check("not all one", any(c["acc"] < 1 for c in b["reference_A4"].values()))
    # the intervals are those of the new sample name, not of main500
    kept = sorted(rs, key=lambda r: (r["prompt"], r["writer"]))
    R, _ = aggregate.resamples(seed, [r["prompt"] for r in kept], "sel_without")
    R0, _ = aggregate.resamples(seed, [r["prompt"] for r in kept], "main500")
    st = {"full": evaluate.STRONGEST_FULL, "window": evaluate.STRONGEST_WINDOW}
    c1 = aggregate.reference_rows(aggregate.summarise_cells(kept, R, st)[0])
    c0 = aggregate.reference_rows(aggregate.summarise_cells(kept, R0, st)[0])
    check("new_name", b["sample"] == "sel_without" and T._dump(b["reference_A4"]) == T._dump(c1)
          and T._dump(c1) != T._dump(c0))
    # (c) guards
    with open(ex, "w", encoding="utf-8") as f:
        json.dump([{"n": 0, "prompt": p0, "writer": "not-a-writer", "where": []}], f)
    check("absent", stops(ns(cache=cache, exclude=ex, sample_name="x", out=os.path.join(tmp, "c.json"))))
    with open(ex, "w", encoding="utf-8") as f:
        json.dump([{"prompt": p0, "writer": w} for w in sample[p0][:2]], f)
    check("expect_count", stops(ns(cache=cache, exclude=ex, expect_excluded=1, sample_name="x",
                                   out=os.path.join(tmp, "c.json"))))
    check("name_guard", stops(ns(cache=cache, exclude=ex, sample_name="main500", out=os.path.join(tmp, "c.json")))
          and stops(ns(cache=cache, sample_name="x", out=os.path.join(tmp, "c.json"))))
    # no writer ID in the outputs
    ids = {w for v in sample.values() for w in v}
    text = open(os.path.join(tmp, "b.json"), encoding="utf-8").read()
    check("no_ids", not any(re.search(r"\b%s\b" % re.escape(w), text) for w in ids))


def main():
    if os.environ.get("A4WO_MUTATE"):  # a mutant, on the run of the parent (A4WO_SELFTEST_DIR)
        tmp = os.environ["A4WO_SELFTEST_DIR"]
        with open(os.path.join(tmp, "sample.json"), encoding="utf-8") as f:
            sample = json.load(f)
        try:
            tests(tmp, glob.glob(os.path.join(tmp, "cache", "*"))[0], os.path.join(tmp, "run.json"), sample)
        except SystemExit as e:  # a guard that stops a valid call is a failure of the test it is in
            FAIL.extend(["positive", "excluded"])
            print("FAIL positive\nFAIL excluded\n(stopped: %s)" % e)
        print("FAIL" if FAIL else "PASS", len(FAIL))
        return 1 if FAIL else 0
    tmp = tempfile.mkdtemp(prefix="a4woselftest")
    try:
        return with_run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def with_run(tmp):
    build(tmp)
    with open(os.path.join(tmp, "sample.json"), encoding="utf-8") as f:
        sample = json.load(f)
    tests(tmp, glob.glob(os.path.join(tmp, "cache", "*"))[0], os.path.join(tmp, "run.json"), sample)
    if FAIL:
        print("FAIL", len(FAIL))
        return 1
    print("PASS (unmutated)")
    for m, killer in MUTANTS.items():
        p = subprocess.run([sys.executable, "-I", os.path.abspath(__file__)], capture_output=True, text=True,
                           env=dict(os.environ, A4WO_MUTATE=m, A4WO_SELFTEST_DIR=tmp))
        failed = {l.split()[1] for l in p.stdout.splitlines() if l.startswith("FAIL ") and len(l.split()) == 2
                  and not l.split()[1].isdigit()}
        killed = p.returncode != 0 and killer in failed
        print("mutant %-15s -> %s" % (m, ("killed by " + ",".join(sorted(failed))) if killed
                                     else "NOT KILLED (wanted %s; %s)" % (killer, sorted(failed))))
        if not killed:
            FAIL.append("mutant " + m)
    print("FAIL" if FAIL else "PASS", len(FAIL))
    return 1 if FAIL else 0


def build(tmp):
    """One synthetic run_main.run with the fake A4 and a cache in tmp (run.json, cache/, sample.json)."""
    seed = seeds.read_seed()
    per, take = 14, 4
    a4 = os.path.join(tmp, "a4")
    os.makedirs(a4)
    sample = fake_a4(seed, a4, per, take)
    with open(os.path.join(tmp, "sample.json"), "w", encoding="utf-8") as f:
        json.dump(sample, f)
    args = argparse.Namespace(source="synthetic", root=None, out=os.path.join(tmp, "run.json"), workers=1, all=False,
                              forms="main", a4_dir=a4, a4_partial=False, per_prompt=per, per_prompt_sample=take,
                              open_world_n=10, no_timing=True, cache_dir=os.path.join(tmp, "cache"),
                              exploratory_3_5=None)
    run_main.run(args)
    assert len(glob.glob(os.path.join(tmp, "cache", "*"))) == 1


if __name__ == "__main__":
    sys.exit(main())
