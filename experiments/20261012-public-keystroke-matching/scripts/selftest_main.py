"""Self-test of the main computation on synthetic writers (no human data), with mutations.

    python scripts/selftest_main.py            # checks, then each mutation must fail its targeted checks

Every check has an id. A mutation counts as killed only when at least one of its targeted checks fails; a run that
ends with a traceback is an ERROR, not a kill.

Checks: the vectorised alignment equals align_ext.align (costs and groups); the seed formula; the R0 replay of
origins; credit with ties and infinities; positive controls (no edits: R0-A1, R3-A1', R3-A2 and R0-A3 rank the true
text first); a negative control near 1/N per attacker; true windows on records without edits; window slices of R4
and R7; equal numbers of A3 terms across candidates; the vectorised A3; character codes per table; the training
order; stratified resamples; the aggregation layer by value (strongest attacker per resample, uplift over A0, A3 on
R3-u, resamples without writers, contrasts with every config pair, utility per prompt with dropped counts, the
negative control with a fixed attacker, the open-world AUC, the split by the rebuilt draft); utility runs across
modifier rows; the exploratory analyses 3 to 5 (m, thresholds with infinities, tail, margin curve and intervals,
score bands, the fixed attacker and the R3-u version); the whole
run (no text in the output, every contrast and the fixed attacker of the negative control, the exploratory files);
resuming from the cache (deviation D4).
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
from synthetic_logs import DEFAULT_OPS, NO_OPS, Writer, category, record_segments  # noqa: E402

FAILS = []


def check(ok, cid, msg):
    print(("ok   " if ok else "FAIL ") + "[%s] %s" % (cid, msg))
    if not ok:
        FAILS.append(cid)


def close(a, b, tol=1e-12):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


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
    check(bad == 0, "align_vec", "align_vec equals align_ext.align on %d cases (costs and groups) (%d differ)"
          % (n, bad))


def t_seeds():
    import hashlib
    s = "20261012:decoys:P1:w7:10::3"
    want = int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")
    check(seeds.seed_int("20261012", "decoys", "P1", "w7", 10, "", 3) == want, "seeds", "seed formula")


def t_replay():
    bad = 0
    for i in range(40):
        rec = Writer(i, 500 + i, 900 + i, ops={k: v * 3 for k, v in DEFAULT_OPS.items()}).run()
        t, o = corpus.replay_origins(rec.rows)
        bad += t != rec.final or o != [None if isinstance(x, tuple) else x - 1 for x in rec.origin]
    check(bad == 0, "replay", "R0 replay of origins equals the simulator's truth (%d differ)" % bad)


def t_credit():
    inf = float("inf")
    ok = (matching.credit_stats(0, [1, 1, 2])[0] == 0.5 and matching.credit_stats(0, [inf, inf])[0] == 0.5
          and matching.credit_stats(0, [inf, 3])[0] == 0.0 and matching.credit_stats(0, [inf, 3])[4]
          and matching.credit_stats(1, [1, 2])[0] == 0.0)
    check(ok, "credit", "credit: ties 1/m, all infinite 1/N, only the true text infinite 0")


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
    ctx = evaluate.Context(cfg, seed, pools, pool_ids, models, tmax, fold_of, ["R0", "R3", "R3-u", "R7(0.25)"], [10],
                           open_world_n=10)
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
        check(acc(form, att) == 1.0, "pos_ctrl", "positive control, no edits: %s %s ranks the true text first (%.3f)"
              % (form, att, acc(form, att)))
    check(acc("R3", "A2", "window", 20) > 0.9, "pos_ctrl_window", "positive control, windows k = 20: R3 A2 (%.3f)"
          % acc("R3", "A2", "window", 20))
    check(all(r["rebuilt_match"] for r in res), "rebuilt_flag",
          "records without edits: the rebuilt draft matches the text after whitespace normalisation")
    ow = [r["open_world"].get(("R3", "A2")) for r in res]
    check(all(ow) and all(a <= b for p in ow for a, b in p), "open_world_draws",
          "open-world draws: the minimum with the true text never exceeds the minimum without it")
    wb = [x for r in res for x in r["window_bias"].get(("R3", 10), [])]
    nst = 0
    for w in picked:
        words = A.Cand(w.text).words
        valid, _ = matching.true_window_starts(w.rows, *corpus.replay_origins(w.rows), words, words, 10)
        nst += min(5, len(valid))
    check(len(wb) == nst and all(np.isfinite(x) and x >= 0 for x in wb)
          and all(np.isfinite(r["window_bias_full"]["R3"]) for r in res), "window_bias_values",
          "bias of true windows: one finite cost per used window start (%d of %d) and per record" % (len(wb), nst))
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
        check(abs(np.mean(v) - 0.1) < 0.06, "neg_ctrl", "negative control near 1/N: R3 %s (%.3f, %d writers)"
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
    check(bad == 0, "true_windows", "true windows on records without edits start at the matching word (%d differ)"
          % bad)
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
    check(len(counts) == 1, "a3_terms", "A3 scores the same number of intervals for every candidate (%s)"
          % sorted(counts))
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
    check(n > 0 and bad == 0, "a3_vec", "vectorised A3 equals the reference loop on %d cases (%d differ)" % (n, bad))
    return res


def t_window_slices(seed):
    """R4 and R7 windows: the slice of the released record equals the release of the window's rows."""
    bad_r4 = bad_r7 = n = 0
    for i in range(12):
        rec = Writer(40 + i, 600 + i, 1000 + i, ops={k: v * 3 for k, v in DEFAULT_OPS.items()}).run()
        rows = rec.rows
        cats = [category(r["down_event"]) for r in rows]
        r4 = forms.release(rows, "R4(2)", seed, "P0", "w%d" % i)
        r7 = forms.release(rows, "R7(0.25)", seed, "P0", "w%d" % i)
        r3 = forms.release(rows, "R3", seed, "P0", "w%d" % i).rows
        for a, b, si, sj in matching.window_row_ranges(cats, 10)[::7]:
            n += 1
            w4 = evaluate.window_release(r4, (a, b), (si, sj))
            want4 = [v // 2 for v, _ in record_segments(cats[a:b + 1])]
            bad_r4 += w4.values != want4
            w7 = evaluate.window_release(r7, (a, b), (si, sj))
            want7 = [(r["down_event"], r["down_time"]) for r, k in zip(r3[a:b + 1], r7.keep[a:b + 1]) if k]
            bad_r7 += [(r["down_event"], r["down_time"]) for r in w7.rows] != want7
    check(n > 0 and bad_r4 == 0, "window_r4", "R4 window values equal the segments of the window rows (%d of %d differ)"
          % (bad_r4, n))
    check(n > 0 and bad_r7 == 0, "window_r7", "R7 window rows equal the kept R3 rows of the window (%d of %d differ)"
          % (bad_r7, n))


def t_cand_codes():
    t1 = A.DigraphTable([], 20)
    t2 = A.DigraphTable([], 20)
    t2.encode("zyxwvu")
    c = A.Cand("Hello world again, 2 tests")
    c.codes(t1)
    check(list(c.codes(t2)) == list(t2.encode("".join(c.words))), "cand_codes",
          "candidate character codes are kept per table")


def t_train_order(seed, cfg):
    writers, _ = run_main.prepare(corpus.synthetic_corpus(seed, 2, 10, tag="order"))
    m1 = run_main.build_models(list(writers), seed, cfg)
    m2 = run_main.build_models(list(reversed(writers)), seed, cfg)
    same = (np.array_equal(m1["boundary"].clf.coef_, m2["boundary"].clf.coef_)
            and np.array_equal(m1["boundary"].mean, m2["boundary"].mean)
            and m1["digraph"].pair == m2["digraph"].pair and m1["digraph"].all == m2["digraph"].all
            and all(m1["r7"][p].a == m2["r7"][p].a and m1["r7"][p].var == m2["r7"][p].var for p in m1["r7"]))
    check(same, "train_order", "the models do not depend on the order of the training writers")


def t_resamples(seed):
    prompts = ["P0"] * 5 + ["P1"] * 7
    R, cols = aggregate.resamples(seed, prompts, "test", n=50)
    ok = all(all(prompts[i] == "P0" for i in R[b, cols["P0"]]) and all(prompts[i] == "P1" for i in R[b, cols["P1"]])
             for b in range(50))
    check(ok, "resamples", "bootstrap resamples stay within prompts")


# --- the aggregation layer, by value -------------------------------------------------------------------------------

STRONGEST = {"full": evaluate.STRONGEST_FULL, "window": evaluate.STRONGEST_WINDOW}


def _fake(prompt, writer, cells):
    """A per-writer result with full cells {(form, attacker): acc} at N = 10."""
    full = {("full", f, a, 10): {"acc": v, "top5": v, "rr": v, "all_inf": 0, "only_true_inf": 0, "draws": 1}
            for (f, a), v in cells.items() if v is not None}
    return {"prompt": prompt, "writer": writer, "full": full, "window": {}}


def t_aggregate(seed, cfg):
    rng = np.random.default_rng(11)
    forms_c = ["R1", "R2", "R3", "R3-u", "R3-t(10)", "R3-t(100)", "R3-t(1000)"]
    res = []
    for i in range(12):
        cells = {}
        for f in forms_c:
            if f == "R3-u":
                atts = ("A0", "A2b", "A3-sum", "A3-mean")
            elif f.startswith("R3"):
                atts = ("A0", "A1p", "A2", "A3")
            else:
                atts = ("A0", "A1", "A3")
            for a in atts:
                cells[(f, a)] = float(rng.integers(0, 21)) / 20
        cells[("R2", "A2")] = 1.0 if i == 0 else None  # one writer only: resamples without it have no value
        res.append(_fake("P%d" % (i % 2), "w%02d" % i, cells))
    R, _ = aggregate.resamples(seed, [r["prompt"] for r in res], "agg", n=300)
    cells, best, boot = aggregate.summarise_cells(res, R, STRONGEST)

    def means(f, a):
        v = np.array([r["full"].get(("full", f, a, 10), {}).get("acc", np.nan) for r in res])
        with np.errstate(invalid="ignore"):
            bm = np.array([np.nanmean(v[row]) if np.any(~np.isnan(v[row])) else np.nan for row in R])
        return float(np.nanmean(v)), bm

    atts = ("A0", "A1p", "A2", "A3")
    pts = {a: means("R3", a) for a in atts}
    bmax = np.max(np.vstack([pts[a][1] for a in atts]), axis=0)
    e = best["full|R3|10"]
    pick = max(atts, key=lambda a: (pts[a][0], -atts.index(a)))
    check(e["attacker"] == pick and close(e["acc"], pts[pick][0]), "agg_point",
          "strongest attacker: the point estimate's maximum and its attacker")
    check(close(e["ci"], aggregate.ci(bmax)), "agg_strongest_ci",
          "strongest attacker: interval of the maximum taken inside each resample")
    sel = np.argmax(np.vstack([pts[a][1] for a in atts]), axis=0)
    check(all(close(e["share_selected"][a], float(np.mean(sel == j))) for j, a in enumerate(atts)),
          "agg_share", "strongest attacker: share of resamples per selected attacker")
    check(close(e["uplift_over_A0"], pts[pick][0] - pts["A0"][0]) and close(e["uplift_ci"],
                                                                           aggregate.ci(bmax - pts["A0"][1])),
          "agg_uplift", "uplift over A0: point and resample differences")
    s, m = means("R3-u", "A3-sum"), means("R3-u", "A3-mean")
    c = cells.get("full|R3-u|A3|10")
    check(c is not None and close(c["acc"], max(s[0], m[0])) and close(c["ci"], aggregate.ci(np.fmax(s[1], m[1]))),
          "agg_r3u_a3", "A3 on R3-u is the maximum of the sum and mean versions (point and resamples)")
    check("A3" in best["full|R3-u|10"]["share_selected"] and "A3-sum" not in best["full|R3-u|10"]["share_selected"],
          "agg_r3u_strongest", "the strongest attacker on R3-u takes A3 (not its two versions separately)")
    c2 = cells.get("full|R2|A2|10")
    check(c2 is not None and c2["nan_resamples"] > 0 and c2["ci"] is not None, "agg_nan",
          "a cell with resamples without writers keeps an interval and counts those resamples")
    # contrasts: every config pair, R3 - R3-t(w) per w with the A3 difference
    con, missing = aggregate.contrasts(best, cells, boot, [tuple(x) for x in cfg["contrasts"]], forms_c)
    want = []
    for f1, f2 in cfg["contrasts"]:
        for a in [f for f in forms_c if f == f1 or f.startswith(f1 + "(")]:
            for b in [f for f in forms_c if f == f2 or f.startswith(f2 + "(")]:
                want.append("%s - %s|10|full" % (a, b))
    check(len(want) == 6 and all(w in con for w in want) and not missing, "contrast_all",
          "contrasts: every config pair appears (%d of %d; missing %s)" % (sum(w in con for w in want), len(want),
                                                                           missing))
    ok = True
    for w in (10, 100, 1000):
        k = "R3 - R3-t(%d)|10|full" % w
        a3, a3t = means("R3", "A3"), means("R3-t(%d)" % w, "A3")
        ok = ok and k in con and close(con[k].get("A3_diff"), a3[0] - a3t[0]) and close(con[k].get("A3_ci"),
                                                                                       aggregate.ci(a3[1] - a3t[1]))
        ok = ok and close(con[k]["ci"], aggregate.ci(best["full|R3|10"]["_boot"]
                                                     - best["full|R3-t(%d)|10" % w]["_boot"]))
    check(ok, "contrast_a3", "R3 - R3-t(w): difference of the strongest and of A3 (point and resamples)")
    # open-world AUC
    check(aggregate.auc([0, 0], [1, 1]) == 1.0 and aggregate.auc([1], [0]) == 0.0 and aggregate.auc([1], [1]) == 0.5
          and close(aggregate.auc([0, 2], [1, 3]), 0.75), "auc", "AUC: separated 1, reversed 0, tied 1/2, mixed 3/4")
    ow_best = {"full|R3|10": {"attacker": "A2"}, "full|R3-u|10": {"attacker": "A3"}}
    ow_cells = {"full|R3-u|A3-sum|10": {"acc": 0.2}, "full|R3-u|A3-mean|10": {"acc": 0.4}}
    for i, r in enumerate(res):
        r["open_world"] = {("R3", "A2"): [(0.0, 1.0), (float(i % 4), 2.0)], ("R3", "A0"): [(5.0, 1.0)],
                           ("R3-u", "A3-sum"): [(3.0, 1.0)], ("R3-u", "A3-mean"): [(float(i % 3), 1.5)]}
    ow = aggregate.open_world(res, R, ow_best, ow_cells, ["R3", "R3-u"], 10)
    pos = [[0.0, float(i % 4)] for i in range(12)]
    neg = [[1.0, 2.0] for _ in range(12)]
    want_ci = aggregate.ci([aggregate.auc(sum((pos[i] for i in row), []), sum((neg[i] for i in row), []))
                            for row in R])
    check("full|R3|10" in ow and close(ow["full|R3|10"]["auc"], aggregate.auc(sum(pos, []), sum(neg, [])))
          and close(ow["full|R3|10"]["ci"], want_ci) and ow["full|R3|10"]["draws"] == 24
          and close(ow["full|R3|10"]["auc_per_attacker"]["A0"], 0.0), "open_world",
          "open world: AUC and interval of the selected attacker over the pooled draws")
    # writers with different numbers of draws, and writers without draws, against a plain concatenation
    lens = [0, 1, 3, 2, 0, 5, 1, 1, 4, 0, 2, 3]
    g = np.random.default_rng(3)
    draws = [[(float(g.integers(0, 4)), float(g.integers(0, 4))) for _ in range(n)] for n in lens]
    for r, d in zip(res, draws):
        r["open_world"] = {("R3", "A2"): d} if d else {}
    ow2 = aggregate.open_world(res, R, ow_best, ow_cells, ["R3"], 10)
    cat = [aggregate.auc([a for i in row for a, _ in draws[i]], [b for i in row for _, b in draws[i]]) for row in R]
    check(close(ow2["full|R3|10"]["ci"], aggregate.ci(cat)) and ow2["full|R3|10"]["draws"] == sum(lens),
          "open_world_lengths", "open world: resamples of writers with unequal and missing draws equal a concatenation")
    check("full|R3-u|10" in ow and ow["full|R3-u|10"]["costs_of"] == "A3-mean"
          and close(ow["full|R3-u|10"]["auc"], aggregate.auc([float(i % 3) for i in range(12)], [1.5] * 12)),
          "open_world_r3u", "open world on R3-u: the A3 version with the larger point estimate")
    # split by the rebuilt draft
    for i, r in enumerate(res):
        r["rebuilt_match"] = i < 8
    sp = aggregate.split_by_rebuilt(res, R, cells)
    v = np.array([r["full"][("full", "R3", "A2", 10)]["acc"] for r in res])
    mm = np.where(np.arange(12) < 8, v, np.nan)
    with np.errstate(invalid="ignore"):
        bm = np.array([np.nanmean(mm[row]) if np.any(~np.isnan(mm[row])) else np.nan for row in R])
    check(sp["writers_match"] == 8 and close(sp["cells"]["full|R3|A2|10"]["match"]["acc"], v[:8].mean())
          and close(sp["cells"]["full|R3|A2|10"]["mismatch"]["acc"], v[8:].mean())
          and close(sp["cells"]["full|R3|A2|10"]["match"]["ci"], aggregate.ci(bm)), "rebuilt_split",
          "accuracy split by the rebuilt draft's match")


def t_utility_summary(seed):
    res, scores = [], []
    for i in range(16):
        p = "P%d" % (i % 2)
        base = float(i + 1)
        u = {"R0": {}, "R3": {}, "R3-u": {}}
        for m in utility.METRICS:
            u["R0"][m] = 0.0 if i == 0 else base
            u["R3"][m] = 2 * base
            u["R3-u"][m] = None if i == 1 else base * (1 + 0.1 * (i % 3) + 0.5 * (i % 2))
        res.append({"prompt": p, "writer": "w%02d" % i, "utility": u})
        scores.append(base)
    R, cols = aggregate.resamples(seed, [r["prompt"] for r in res], "util", n=200)
    out, fig = aggregate.utility_summary(res, scores, ["R0", "R3", "R3-u"], R, cols)
    e = out["p_burst_mean_len|R3"]
    check(close(e["ratio_median"]["mean"], 2.0) and close(e["ratio_p10"]["range"], [2.0, 2.0])
          and set(e["ratio_median"]["by_prompt"]) == {"P0", "P1"} and close(e["ratio_median"]["ci"], [2.0, 2.0]),
          "utility_ratio", "utility: ratio to R0 per prompt, mean, range and interval")
    check(close(e["spearman_r0"]["by_prompt"]["P0"], 1.0) and close(e["spearman_r0"]["mean"], 1.0)
          and close(e["spearman_score"]["by_prompt"]["P1"], 1.0), "utility_spearman",
          "utility: Spearman with R0 and with the human score per prompt")
    e2 = out["p_burst_mean_len|R3-u"]
    check(e2["ratio_dropped_r0"] == 1 and e2["ratio_dropped_form"] == 1 and e["ratio_dropped_form"] == 0,
          "utility_dropped", "utility: writers dropped from the ratio are counted on the R0 side and the form side")
    rp = [r["utility"]["R3-u"]["p_burst_mean_len"] / r["utility"]["R0"]["p_burst_mean_len"]
          for r in res if r["prompt"] == "P1" and r["writer"] != "w01"]
    check(close(e2["ratio_median"]["by_prompt"]["P1"], float(np.quantile(rp, 0.5))), "utility_ratio_prompt",
          "utility: the per-prompt ratio median uses that prompt's writers only")
    r0 = np.array([r["utility"]["R0"]["p_burst_mean_len"] for r in res])
    vu = np.array([np.nan if r["utility"]["R3-u"]["p_burst_mean_len"] is None
                   else r["utility"]["R3-u"]["p_burst_mean_len"] for r in res])
    rat = np.where((r0 != 0) & ~np.isnan(vu), vu / np.where(r0 != 0, r0, 1), np.nan)
    per = []
    for p in ("P0", "P1"):
        Rp = R[:, cols[p]]
        per.append([np.nanquantile(rat[row], 0.5) for row in Rp])
    check(close(e2["ratio_median"]["ci"], aggregate.ci(np.mean(np.array(per), axis=0)), 1e-9), "utility_ratio_ci",
          "utility: interval of the mean ratio median, recomputed from each prompt's resampled writers")


def t_utility_runs():
    """As registered, a run is a run of consecutive rows: a Shift press splits an insertion and a deletion run."""
    seq = ["letter"] * 6 + ["arrow_left"] * 3 + ["letter", "modifier", "letter", "letter"] + ["arrow_right"] * 3 + \
          ["backspace", "modifier", "backspace", "letter"]
    rows = [{"event_id": i + 1, "down_event": c, "down_time": 1000 * i} for i, c in enumerate(seq)]
    rel = forms.Released("R3", rows=rows)
    m = utility.metrics(rel, 1.0)
    check(m["insertion_mean_len"] == 1.5 and m["deletion_mean_len"] == 1, "utility_runs",
          "utility: a modifier row ends the runs (insertion 1 + 2, deletion 1 + 1; got %s, %s)"
          % (m["insertion_mean_len"], m["deletion_mean_len"]))


def t_negative_control(seed):
    """The real negative_control: the attacker is the one selected in the main computation, not again."""
    ids = ["w%02d" % i for i in range(12)]
    pool_ids = {"P0": ids}
    nc_b = {("P0", a): ids[(j + 1) % 12] for j, a in enumerate(ids)}
    results = {}
    rng = np.random.default_rng(5)
    for j, a in enumerate(ids):
        me = (j - 1) % 12  # this record is B of writer me: A0 always ranks writer me first
        a0 = np.ones(12)
        a0[me] = 0.0
        results[("P0", a)] = {"costs": {"R3": {"A0": a0, "A2": rng.random(12)},
                                        "R3-u": {"A0": rng.random(12), "A3-sum": a0, "A3-mean": rng.random(12)}}}
    res = [{"prompt": "P0", "writer": a} for a in ids]
    R, _ = aggregate.resamples(seed, ["P0"] * 12, "nc", n=100)
    main_best = {"full|R3|10": {"attacker": "A2"}, "full|R3-u|10": {"attacker": "A3"}}
    main_cells = {"full|R3-u|A3-sum|10": {"acc": 0.30}, "full|R3-u|A3-mean|10": {"acc": 0.32}}
    nc = run_main.negative_control(res, results, nc_b, pool_ids, seed, R, STRONGEST, main_best, main_cells, Ns=(10,))
    e = nc["fixed_attacker"].get("full|R3|10", {})
    a2 = nc["cells"]["full|R3|A2|10"]
    check(e.get("attacker") == "A2" and close(e.get("acc"), a2["acc"]) and close(e.get("ci"), a2["ci"])
          and nc["cells"]["full|R3|A0|10"]["acc"] == 1.0, "nc_fixed",
          "negative control: the attacker fixed by the main point estimate (A2 %.3f; A0 1.0 not taken)"
          % a2["acc"])
    e = nc["fixed_attacker"].get("full|R3-u|10", {})
    am = nc["cells"]["full|R3-u|A3-mean|10"]
    check(e.get("costs_of") == "A3-mean" and close(e.get("acc"), am["acc"]) and close(e.get("ci"), am["ci"]),
          "nc_fixed_r3u", "negative control on R3-u: the A3 version of the main point estimate (mean %.3f; "
          "sum 1.0 not taken)" % am["acc"])


def t_exploratory(seed):
    """Exploratory analyses 3 to 5 (decision 68): m against a plain sort (ties and infinities), the tail against
    numpy and a plain count, the margin curve against a plain count, the score bands against a plain ranking (ties by
    writer ID), and the attacker fixed by the main point estimate (not selected again)."""
    rng = np.random.default_rng(23)
    vecs = [rng.random(10), np.array([0.3, 0.1, 0.1, 0.5]), np.array([np.inf, 2.0, np.inf]),
            np.array([np.inf, np.inf, 1.0]), np.array([np.inf, np.inf]), np.array([5.0, 1.0, 3.0])]
    want = [float(np.sort(v)[1] - np.sort(v)[0]) for v in vecs[:2]] + [np.inf, np.inf, 0.0, 2.0]
    got = [evaluate.margin(v) for v in vecs]
    got.append(evaluate.margin(np.array([1.0, np.nan, np.nan])))
    want.append(np.inf)
    check(all(g == w or close(g, w) for g, w in zip(got, want)), "explore_margin",
          "m = second smallest - smallest (tie 0, infinite ties 0, only the smallest finite or NaN costs: inf): %s"
          % got)
    srt = np.array([0, 0, 1, 2, 3] + [np.inf] * 6, dtype=float)
    want_p = []
    for q in aggregate.MARGIN_Q:  # the linear definition by hand: s[lo] + (s[hi] - s[lo]) * frac, inf above
        h = (len(srt) - 1) * q / 100
        lo, hi = int(np.floor(h)), int(np.ceil(h))
        want_p.append(srt[lo] if lo == hi else (np.inf if np.isinf(srt[hi]) else srt[lo] + (srt[hi] - srt[lo]) *
                                                (h - lo)))
    got_p = [aggregate._pct_sorted(srt, q) for q in aggregate.MARGIN_Q]
    check(got_p == want_p and got_p[4] == 3.0 and np.isinf(got_p[5]), "explore_pct_inf",
          "thresholds with infinite m: the linear percentile by hand (numpy gives nan here): %s" % got_p)
    ids = ["w%02d" % i for i in range(30)]
    res = []
    for j, wid in enumerate(ids):
        p = "P%d" % (j % 2)
        acc = {"A2": 1.0 if j == 0 else round(0.4 + j / 50, 4), "A0": 1.0}  # p95 and p99 interpolate below 1
        full = {("full", "R3", a, 10): {"acc": v} for a, v in acc.items()}
        mg = [(float(rng.integers(0, 6)), float(rng.integers(0, 2))) for _ in range(1 + j % 5)]
        margin = {} if j == 5 else {("R3", "A2", 10): mg}  # one writer without records, unequal numbers of draws
        res.append({"prompt": p, "writer": wid, "full": full, "window": {}, "margin": margin})
    R, _ = aggregate.resamples(seed, [r["prompt"] for r in res], "explore", n=200)
    best = {"full|R3|10": {"attacker": "A2"}}
    cells = {"full|R3|A2|10": {"acc": 0.692}, "full|R3|A0|10": {"acc": 1.0}}
    st = evaluate.STRONGEST_FULL
    tail = aggregate.exploratory_tail(res, R, best, cells, ["R3"], st).get("full|R3|10", {})
    v = np.array([r["full"][("full", "R3", "A2", 10)]["acc"] for r in res])
    r3u = aggregate.fixed_attacker({"full|R3-u|10": {"attacker": "A3"}},
                                   {"full|R3-u|A3-sum|10": {"acc": 0.30}, "full|R3-u|A3-mean|10": {"acc": 0.32}},
                                   "R3-u", 10, st)
    check(tail.get("attacker") == "A2" and tail.get("costs_of") == "A2", "explore_fixed",
          "the exploratory analyses use the attacker of the main point estimate (A2; A0 1.0 not taken)")
    check(r3u == ("A3", "A3-mean"), "explore_fixed_r3u",
          "on R3-u, A3 reads the version of the main point estimate (A3-mean 0.32 over A3-sum 0.30): %s" % (r3u,))
    tv = {k: tail.get(k, {}).get("value", np.nan) for k in ("p95", "p99", "share_acc_1")}
    plain = np.array([[np.percentile(v[row], 95), np.percentile(v[row], 99), np.mean(v[row] == 1.0)] for row in R])
    check(close(tv["p95"], np.percentile(v, 95)) and close(tv["p99"], np.percentile(v, 99))
          and tv["p95"] < tv["p99"] < 1
          and close(tv["share_acc_1"], np.mean(v == 1.0))
          and all(close(tail.get(k, {}).get("ci"), aggregate.ci(plain[:, j]))
                  for j, k in enumerate(("p95", "p99", "share_acc_1"))),
          "explore_tail", "tail: p95 %.3f, p99 %.3f, share of accuracy 1 %.3f (plain: %.3f)"
          % (tv["p95"], tv["p99"], tv["share_acc_1"], np.mean(v == 1.0)))
    mg = aggregate.exploratory_margin(res, R, best, cells, ["R3"], st).get("full|R3|10", {"draws": -1, "curve": []})
    per = [r["margin"].get(("R3", "A2", 10), []) for r in res]
    m = np.array([x for d in per for x, _ in d])
    c = np.array([y for d in per for _, y in d])
    ok = mg.get("draws", -1) == len(m)
    for e in mg.get("curve", []):
        t = np.percentile(m, e["q"])
        ok = ok and close(e["t"], t) and close(e["coverage"], np.mean(m >= t)) and close(e["precision"],
                                                                                          np.mean(c[m >= t]))
        bc, bp = [], []
        for row in R:  # the draws of the resampled writers, a writer drawn twice counted twice
            mr = np.array([x for i in row for x, _ in per[i]])
            cr = np.array([y for i in row for _, y in per[i]])
            bc.append(np.mean(mr >= t))
            bp.append(np.mean(cr[mr >= t]) if np.any(mr >= t) else np.nan)
        ok = ok and close(e["coverage_ci"], aggregate.ci(bc)) and close(e["precision_ci"], aggregate.ci(bp))
    check(ok and bool(mg.get("curve")) and mg["curve"][0]["coverage"] == 1.0, "explore_margin_curve",
          "margin curve: thresholds at the 0th..90th percentiles of m, coverage and precision and their intervals as "
          "plain counts (unequal draws, a writer without records)")
    scores = [float(j % 4) for j in range(30)]
    scores[3] = None
    band = aggregate.score_bands(res, scores)
    ok = band[3] == -1
    for p in ("P0", "P1"):
        ix = [i for i, r in enumerate(res) if r["prompt"] == p and scores[i] is not None]
        order = sorted(ix, key=lambda i: (scores[i], res[i]["writer"]))
        ok = ok and all(band[i] == (3 * k) // len(order) for k, i in enumerate(order))
    sb = aggregate.exploratory_score_band(res, R, best, cells, ["R3"], scores, st)
    e = sb.get("full|R3|10", {})
    b0 = np.nanmean(np.where(band == 0, v, np.nan))
    b2 = np.nanmean(np.where(band == 2, v, np.nan))
    tb = e.get("top_minus_bottom", {})
    with np.errstate(invalid="ignore"):
        diff = [np.mean([v[i] for i in row if band[i] == 2]) - np.mean([v[i] for i in row if band[i] == 0])
                for row in R]
    check(ok and sb["writers_without_score"] == "<10" and close(e.get("band0", {}).get("acc"), b0)
          and close(e.get("band2", {}).get("acc"), b2) and close(tb.get("value"), b2 - b0)
          and close(tb.get("ci"), aggregate.ci(diff)),
          "explore_band", "score bands by (score, writer ID) in thirds per prompt; top - bottom %.3f"
          % (b2 - b0))


def t_run(seed, tmp, cfg):
    out = os.path.join(tmp, "selftest_main_run.json")
    exdir = os.path.join(tmp, "selftest_main_explore")
    subprocess.run([sys.executable, os.path.join(HERE, "run_main.py"), "--out", out, "--per-prompt", "16",
                    "--per-prompt-sample", "4", "--workers", "4", "--no-timing", "--open-world-n", "10",
                    "--exploratory-3-5", exdir], check=True, capture_output=True)
    with open(out, encoding="utf-8") as f:
        s = f.read()
    ex = {}
    for n in ("tail", "margin", "score_band"):
        with open(os.path.join(exdir, "exploratory_%s.json" % n), encoding="utf-8") as f:
            ex[n] = f.read()
    texts = [w.text for w in corpus.synthetic_corpus(seed, 4, 16, tag="main")]
    outs = [s] + list(ex.values())
    leaks = sum(1 for t in texts for wd in A.Cand(t).words if len(wd) >= 7 and any(wd in x for x in outs))
    check(leaks == 0, "no_text", "no word of the texts appears in the output or the exploratory files (%d found)"
          % leaks)
    strong = json.loads(s).get("main500", {}).get("strongest", {})
    want_ex = {n for n in strong if n.split("|")[0] == "full" and len(n.split("|")) == 3
               and n.split("|")[1] in forms.MAIN and int(n.split("|")[2]) in (10, 1000)}
    an = [json.loads(x)["analysis"] for x in ex.values()]
    got_ex = [set(k for k in a if k.startswith("full|")) for a in an]
    check(len(want_ex) > 0 and all(g == want_ex for g in got_ex)
          and not any(a[k].get("missing") for a in an for k in want_ex)
          and all(a[k]["attacker"] == strong[k]["attacker"] for a in an for k in want_ex), "run_explore",
          "the run writes the exploratory analyses 3 to 5 for every main form and N in (10, 1000) of the strongest "
          "attacker (%d each, its attacker; the main output is checked unchanged by run_resume)" % len(want_ex))
    d = json.loads(s)
    m = d.get("main500", {})
    check(bool(m.get("cells")), "run_cells", "the run writes aggregate cells")
    want = ["%s - %s|10|full" % (a, b) for f1, f2 in cfg["contrasts"]
            for a in [f for f in forms.ALL if f == f1 or f.startswith(f1 + "(")]
            for b in [f for f in forms.ALL if f == f2 or f.startswith(f2 + "(")]]
    check(all(w in m.get("contrasts", {}) for w in want) and not m.get("contrasts_missing"), "run_contrasts",
          "the run writes every config contrast (%d)" % len(want))
    fx = m.get("negative_control", {}).get("fixed_attacker", {})
    want_nc = {n for n in m.get("strongest", {}) if n.split("|")[0] == "full" and n.split("|")[1] in forms.MAIN
               and len(n.split("|")) == 3 and int(n.split("|")[2]) in (10, 1000)}
    check(len(want_nc) > 0 and set(fx) == want_nc and not any(e.get("missing") for e in fx.values())
          and all(fx[n]["attacker"] == m["strongest"][n]["attacker"] for n in fx), "run_nc",
          "the run's negative control has a value with the main strongest attacker for every main form and N (%d)"
          % len(want_nc))
    ow = m.get("open_world", {})
    want_ow = {"full|%s|10" % f for f in forms.ALL}
    sample = m.get("cells", {}).get("full|R0|A0|10", {}).get("writers", 0)
    check(set(ow) == want_ow and all(e["ci"] is not None and e["draws"] == 20 * sample for e in ow.values()),
          "run_open_world", "the run's open world has an AUC and interval for every form (%d draws each)"
          % (20 * sample))
    check(m.get("rebuilt_split", {}).get("cells") and m.get("window_bias"), "run_secondary",
          "the run writes the rebuilt split and the bias of true windows")
    t_run_resume(tmp, out, s)


def t_run_resume(tmp, plain_out, plain):
    """--cache-dir (deviation D4): a fresh cached run, and a run resumed after half of the cache is removed, write the
    same bytes as the run without the cache; --all with the cache of the run without --all writes the same bytes as
    --all without the cache and reuses the sample's tasks."""
    import shutil
    cache = os.path.join(tmp, "selftest_main_cache")
    shutil.rmtree(cache, ignore_errors=True)
    base = [sys.executable, os.path.join(HERE, "run_main.py"), "--per-prompt", "16", "--per-prompt-sample", "4",
            "--workers", "4", "--no-timing", "--open-world-n", "10"]

    def run(name, *extra):
        out = os.path.join(tmp, "selftest_main_run_%s.json" % name)
        r = subprocess.run(base + list(extra) + ["--out", out], check=True, capture_output=True, text=True)
        with open(out, encoding="utf-8") as f:
            return f.read(), r.stdout

    try:
        first, _ = run("cache0", "--cache-dir", cache)
        sub = [os.path.join(cache, d) for d in os.listdir(cache)]
        files = sorted(os.path.join(sub[0], n) for n in os.listdir(sub[0])) if len(sub) == 1 else []
        for p in files[::2]:
            os.remove(p)
        second, log = run("cache1", "--cache-dir", cache)
        resumed = "%d of %d tasks done" % (len(files) - len(files[::2]), len(files)) in log
        check(len(files) > 1 and resumed and first == plain and second == plain, "run_resume",
              "a cached run and a run resumed after removing %d of %d cached tasks write the same bytes as %s"
              % (len(files[::2]), len(files), os.path.basename(plain_out)))
        all_cached, log = run("all_cache", "--all", "--cache-dir", cache)
        reused = [line for line in log.splitlines() if " tasks done" in line]
        n_reused = int(reused[0].split(": ")[1].split()[0]) if reused else 0
        all_plain, _ = run("all", "--all")
        check(n_reused == 16 and all_cached == all_plain, "run_resume_all",
              "--all with the cache of the run without --all reuses %d tasks (the 16 of the sample) and writes the "
              "same bytes as --all without the cache" % n_reused)
    finally:
        shutil.rmtree(cache, ignore_errors=True)


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
    t_window_slices(seed)
    t_cand_codes()
    t_train_order(seed, cfg)
    t_resamples(seed)
    t_aggregate(seed, cfg)
    t_utility_summary(seed)
    t_utility_runs()
    t_negative_control(seed)
    t_exploratory(seed)
    if not os.environ.get("MAIN_MUTATE") or os.environ.get("MAIN_MUTATE") in RUN_MUTANTS:
        t_run(seed, tmp, cfg)
    print("PASS" if not FAILS else "FAIL (%d): %s" % (len(FAILS), " ".join(sorted(set(FAILS)))))
    return 0 if not FAILS else 1


# mutation -> the checks that must catch it
MUTANTS = {
    "true_index_shift": ["credit"],
    "decoys_include_true": ["pos_ctrl"],
    "bootstrap_unstratified": ["resamples"],
    "a3_sign": ["pos_ctrl"],
    "a3_skip_missing": ["a3_terms", "a3_vec"],
    "align_vec_tie": ["align_vec"],
    "strongest_point_ci": ["agg_strongest_ci"],
    "r3u_a3_sum_only": ["agg_r3u_a3"],
    "contrast_base_names": ["contrast_all", "contrast_a3"],
    "nc_reselect": ["nc_fixed"],
    "nc_r3u_composite": ["nc_fixed_r3u"],
    "open_world_r3u_sum": ["open_world_r3u"],
    "utility_rp_all": ["utility_ratio_ci"],
    "auc_flip": ["auc", "open_world"],
    "open_world_offsets": ["open_world_lengths"],
    "utility_ratio_pooled": ["utility_ratio_prompt"],
    "runs_modifier_transparent": ["utility_runs"],
    "window_r4_shift": ["window_r4"],
    "window_r7_shift": ["window_r7"],
    "cand_codes_shared": ["cand_codes"],
    "train_unsorted": ["train_order"],
    "margin_first_two": ["explore_margin"],
    "tail_share_ge": ["explore_tail"],
    "band_ties_reversed": ["explore_band"],
    "explore_reselect": ["explore_fixed"],
    "explore_r3u_sum": ["explore_fixed_r3u"],
}
RUN_MUTANTS = ()  # mutations checked without the whole run (each targets a unit check)

if __name__ == "__main__":
    if os.environ.get("MAIN_MUTATE"):
        sys.exit(main())
    code = main()
    for m, targets in MUTANTS.items():
        env = dict(os.environ, MAIN_MUTATE=m)
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, capture_output=True, text=True)
        if "Traceback" in r.stderr or "Traceback" in r.stdout:
            verdict = "ERROR (traceback)"
        else:
            failed = {line.split("]")[0][6:] for line in r.stdout.splitlines() if line.startswith("FAIL [")}
            hit = sorted(failed & set(targets))
            verdict = ("killed by " + ",".join(hit)) if hit else "SURVIVED (failed: %s)" % (",".join(sorted(failed))
                                                                                         or "none")
        print("mutant %-24s -> %s" % (m, verdict))
        code = code or (0 if verdict.startswith("killed") else 1)
    print("PASS" if code == 0 else "FAIL")
    sys.exit(code)
