"""Self-test of the main computation on synthetic writers (no human data), with mutations.

    python scripts/selftest_main.py            # checks, then each mutation must make at least one check fail

Checks: the vectorised alignment equals align_ext.align (costs and groups); the seed formula; the R0 replay of
origins; credit with ties and infinities; positive controls (no edits: R0-A1, R3-A1', R3-A2 and R0-A3 rank the true
text first); the negative control near 1/N per attacker; true windows on records without edits; equal numbers of
A3 terms across candidates; stratified resamples; no text in the output.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aggregate  # noqa: E402
import align_ext  # noqa: E402
import align_vec  # noqa: E402
import attackers as A  # noqa: E402
import corpus  # noqa: E402
import evaluate  # noqa: E402
import forms  # noqa: E402
import matching  # noqa: E402
import run_main  # noqa: E402
import seeds  # noqa: E402
import utility  # noqa: E402
from synthetic_logs import DEFAULT_OPS, NO_OPS, Writer, category  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def t_align():
    rng = np.random.default_rng(7)
    g7 = [(1, 1), (2, 1), (1, 2), (3, 1), (1, 3), (4, 1), (1, 4), (5, 1), (1, 5), (6, 1), (1, 6)]
    bad = n = 0
    for t in range(150):
        x = [int(v) for v in rng.integers(-1, 9, int(rng.integers(0, 20)))]
        ys = [[(0.75 * int(v) if t % 3 == 0 else int(v)) for v in rng.integers(0, 9, int(rng.integers(0, 25)))]
              for _ in range(5)]
        for end in ("full", "window"):
            for groups, mg in ((None, 3), (g7, 6)):
                many = align_vec.align_many(x, ys, 8, end, groups, mg)
                cs = align_vec.costs(x, ys, 8, end, groups, mg)
                for c, y in enumerate(ys):
                    ref = align_ext.align(x, y, 8, end, groups, mg)
                    n += 1
                    bad += ref[0] != cs[c] or ref[0] != many[c][0] or ref[1] != many[c][1]
    check(bad == 0, "align_vec equals align_ext.align on %d cases (costs and groups) (%d differ)" % (n, bad))


def t_seeds():
    import hashlib
    s = "20261012:decoys:P1:w7:10::3"
    want = int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")
    check(seeds.seed_int("20261012", "decoys", "P1", "w7", 10, "", 3) == want, "seed formula")


def t_replay():
    bad = 0
    for i in range(40):
        rec = Writer(i, 500 + i, 900 + i, ops={k: v * 3 for k, v in DEFAULT_OPS.items()}).run()
        t, o = corpus.replay_origins(rec.rows)
        bad += t != rec.final or o != [None if isinstance(x, tuple) else x - 1 for x in rec.origin]
    check(bad == 0, "R0 replay of origins equals the simulator's truth (%d differ)" % bad)


def t_credit():
    inf = float("inf")
    ok = (matching.credit_stats(0, [1, 1, 2])[0] == 0.5 and matching.credit_stats(0, [inf, inf])[0] == 0.5
          and matching.credit_stats(0, [inf, 3])[0] == 0.0 and matching.credit_stats(0, [inf, 3])[4]
          and matching.credit_stats(1, [1, 2])[0] == 0.0)
    check(ok, "credit: ties 1/m, all infinite 1/N, only the true text infinite 0")


def small_context(seed, cfg, ops, per_prompt=24, sample=12):
    writers, _ = run_main.prepare(corpus.synthetic_corpus(seed, 4, per_prompt, ops=ops, tag="selftest"))
    by_prompt = {}
    for w in writers:
        by_prompt.setdefault(w.prompt, {})[w.writer] = w
    prompts = sorted(by_prompt)
    fa, fb = matching.split_folds(seed, prompts)
    fold_of = {p: (0 if p in fa else 1) for p in prompts}
    models = {f: run_main.build_models([w for p in (fb if f == 0 else fa) for w in by_prompt[p].values()], seed, cfg)
              for f in (0, 1)}
    pool_ids = {p: sorted(by_prompt[p]) for p in prompts}
    pools = {p: [A.Cand(by_prompt[p][i].text) for i in pool_ids[p]] for p in prompts}
    tmax = {p: max(utility.interval_max(forms.release(by_prompt[p][i].rows, "R0", seed, p, i)) for i in pool_ids[p])
            for p in prompts}
    ctx = evaluate.Context(cfg, seed, pools, pool_ids, models, tmax, fold_of, ["R0", "R3", "R3-u", "R7(0.25)"], [10])
    picked = [by_prompt[p][i] for p in prompts for i in pool_ids[p][:sample // 4]]
    return ctx, picked, by_prompt, pool_ids


def t_controls(seed, cfg):
    ctx, picked, by_prompt, pool_ids = small_context(seed, cfg, NO_OPS)
    ctx.windows, ctx.keep_costs = True, True
    res = [evaluate.evaluate_writer(w, ctx) for w in picked]

    def acc(form, att, scope="full", k=None):
        key = ("full", form, att, 10) if scope == "full" else ("window", form, att, 10, k)
        v = [r[scope][key]["acc"] for r in res if key in r[scope]]
        return float(np.mean(v)) if v else float("nan")

    for form, att in (("R0", "A1"), ("R3", "A1p"), ("R3", "A2"), ("R0", "A3")):
        check(acc(form, att) == 1.0, "positive control, no edits: %s %s ranks the true text first (%.3f)"
              % (form, att, acc(form, att)))
    check(acc("R3", "A2", "window", 20) > 0.9, "positive control, windows k = 20: R3 A2 (%.3f)"
          % acc("R3", "A2", "window", 20))
    # negative control: every writer's record replaced by the next writer's record of the same prompt
    nc = {}
    for p, ids in pool_ids.items():
        model = ctx.models[ctx.fold_of_prompt[p]]
        cost_of = {i: evaluate.full_costs(forms.release(by_prompt[p][i].rows, "R3", seed, p, i), ctx.pools[p], model,
                                          cfg) for i in ids}
        for me, a in enumerate(ids):
            bi = (me + 1) % len(ids)
            for d in range(20):
                dec, _ = matching.draw_decoys(seed, p, a, 10, ids, {me, bi}, d)
                cand = [me] + dec
                for att in ("A0", "A2", "A3"):
                    per = nc.setdefault(att, {}).setdefault(a, [])
                    per.append(matching.credit_stats(0, cost_of[ids[bi]][att][cand])[0])
    for att, by_w in nc.items():
        v = [np.mean(x) for x in by_w.values()]
        check(abs(np.mean(v) - 0.1) < 0.06, "negative control near 1/N: R3 %s (%.3f, %d writers)"
              % (att, np.mean(v), len(v)))
    # windows: on records without edits each non-empty segment is a word, so the true window starts at the word
    # whose index is the number of non-empty segments before it
    bad = 0
    for w in picked:
        final, origins = corpus.replay_origins(w.rows)
        words = A.Cand(w.text).words
        valid, _ = matching.true_window_starts(w.rows, final, origins, words, words, 10)
        cats = [category(r["down_event"]) for r in w.rows]
        runs = matching.nonempty_runs(cats)
        for _, (si, _), wd in valid:
            bad += wd != sum(1 for a, b, ne in runs[:si] if ne)
    check(bad == 0, "true windows on records without edits start at the matching word (%d differ)" % bad)
    # equal numbers of A3 terms across candidates
    w = picked[0]
    rel = forms.release(w.rows, "R3", seed, w.prompt, w.writer)
    segs = A.segment_presses(rel.cats())
    counts = set()
    pool = ctx.pools[w.prompt]
    for c, (cost, groups) in zip(pool, align_vec.align_many([v for v, _, _ in segs], [c.lens for c in pool], 8,
                                                            "full")):
        if groups is not None:
            counts.add(A.a3_segment_score(ctx.models[0]["digraph"], segs, rel.times(), groups, c)[1])
    check(len(counts) == 1, "A3 scores the same number of intervals for every candidate (%s)" % sorted(counts))
    # the vectorised A3 equals the reference loop (R0, R3 and the rounded-time version)
    bad = n = 0
    for form in ("R0", "R3", "R3-t(100)", "R3-t(1000)"):
        for w in picked[:4]:
            rel = forms.release(w.rows, form, seed, w.prompt, w.writer)
            segs = A.segment_presses(rel.cats())
            wv = rel.p if rel.base == "R3-t" else None
            table = ctx.models[ctx.fold_of_prompt[w.prompt]]["digraph"]
            al = align_vec.align_many([v for v, _, _ in segs], [c.lens for c in pool], 8, "full")
            vs, vn = A.a3_scores(table, A.SegPrep(segs, rel.times()), pool, [g for _, g in al], wv)
            for c, (_, groups) in enumerate(al):
                if groups is not None:
                    rs, rn = A.a3_segment_score(table, segs, rel.times(), groups, pool[c], wv)
                    n += 1
                    bad += abs(rs - vs[c]) > 1e-9 * max(1.0, abs(rs)) or rn != vn[c]
    check(n > 0 and bad == 0, "vectorised A3 equals the reference loop on %d cases (%d differ)" % (n, bad))
    return res


def t_resamples(seed):
    prompts = ["P0"] * 5 + ["P1"] * 7
    R, cols = aggregate.resamples(seed, prompts, "test", n=50)
    ok = all(all(prompts[i] == "P0" for i in R[b, cols["P0"]]) and all(prompts[i] == "P1" for i in R[b, cols["P1"]])
             for b in range(50))
    check(ok, "bootstrap resamples stay within prompts")


def t_no_text(seed, tmp):
    out = os.path.join(tmp, "selftest_main_run.json")
    subprocess.run([sys.executable, os.path.join(HERE, "run_main.py"), "--out", out, "--per-prompt", "16",
                    "--per-prompt-sample", "4", "--workers", "4", "--no-timing"], check=True, capture_output=True)
    with open(out, encoding="utf-8") as f:
        s = f.read()
    texts = [w.text for w in corpus.synthetic_corpus(seed, 4, 16, tag="main")]
    leaks = sum(1 for t in texts for wd in A.Cand(t).words if len(wd) >= 7 and wd in s)
    check(leaks == 0, "no word of the texts appears in the output (%d found)" % leaks)
    d = json.loads(s)
    check("main500" in d and d["main500"]["cells"], "the run writes aggregate cells")


def main():
    seed = seeds.read_seed()
    cfg = run_main.load_config()
    tmp = os.environ.get("SELFTEST_TMP", os.path.join(HERE, "..", "results", ".tmp"))
    os.makedirs(tmp, exist_ok=True)
    t_align()
    t_seeds()
    t_replay()
    t_credit()
    t_controls(seed, cfg)
    t_resamples(seed)
    if not os.environ.get("MAIN_MUTATE"):
        t_no_text(seed, tmp)
    print("PASS" if not FAILS else "FAIL (%d)" % len(FAILS))
    return 0 if not FAILS else 1


MUTANTS = ["true_index_shift", "decoys_include_true", "bootstrap_unstratified", "a3_sign", "a3_skip_missing",
           "align_vec_tie"]

if __name__ == "__main__":
    if os.environ.get("MAIN_MUTATE"):
        sys.exit(main())
    code = main()
    for m in MUTANTS:
        env = dict(os.environ, MAIN_MUTATE=m)
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, capture_output=True, text=True)
        killed = r.returncode != 0
        print("mutant %-24s -> %s" % (m, "killed" if killed else "SURVIVED"))
        code = code or (0 if killed else 1)
    print("PASS" if code == 0 else "FAIL")
    sys.exit(code)
