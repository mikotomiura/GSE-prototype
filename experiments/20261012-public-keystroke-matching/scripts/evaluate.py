"""Per-record computation of the main run: costs, credits over the draws, windows and utility for one writer.

Runs in worker processes. Only numbers leave this module (no rows, texts or keys).
"""
import os
import re

import numpy as np

import attackers as A
import forms
import matching
import utility
from align_ext import INF
from corpus import replay_origins
from synthetic_logs import category, record_segments

# the adaptive attackers of the strongest attacker; on R3-u, "A3" is the maximum of A3-sum and A3-mean, formed in
# aggregate.py from their cells
STRONGEST_FULL = ("A0", "A1", "A1p", "A2", "A2b", "A3")
STRONGEST_WINDOW = ("A0", "A2", "A2b", "A3")
R3U_A3 = ("A3-sum", "A3-mean")
WINDOW_A2_EXTRA = ("R0", "R1", "R5", "R6")
KS = (5, 10, 20, 50)
OPEN_WORLD_N = 1000
MUTATE = os.environ.get("MAIN_MUTATE", "")


def adaptive_costs(costs_of_form):
    """The cost vectors that the strongest attacker, the negative control and the open world read."""
    return {a: cv for a, cv in costs_of_form.items() if a in STRONGEST_FULL or a in R3U_A3}


def norm_ws(s):
    """Whitespace normalisation of check 3: runs of whitespace become one space; leading and trailing removed."""
    return " ".join(s.split())


class Context:
    """What a worker needs besides the writer: config, seed, pools (candidate texts per prompt), models per fold."""

    def __init__(self, cfg, seed, pools, pool_ids, models, task_max, fold_of_prompt, form_list, n_values,
                 windows=True, keep_costs=False, open_world_n=OPEN_WORLD_N, nc_forms=None):
        self.cfg = cfg
        self.seed = seed
        self.pools = pools
        self.pool_ids = pool_ids
        self.models = models
        self.task_max = task_max
        self.fold_of_prompt = fold_of_prompt
        self.forms = form_list
        self.n_values = n_values
        self.windows = windows
        self.keep_costs = keep_costs
        self.open_world_n = open_world_n
        self.nc_forms = form_list if nc_forms is None else nc_forms


def full_costs(rel, cands, model, cfg, memo=None):
    """{attacker: costs over the candidates} for one released record (full text)."""
    out, b = {}, rel.base
    out["A0"] = A.a0_costs(rel, cands)
    if A.applies("A1", b):
        out["A1"] = A.align_costs(A.a1_lengths(rel), rel, cands, cfg, memo=memo)
    if A.applies("A1p", b):
        out["A1p"] = A.align_costs(A.a1_lengths(rel), rel, cands, cfg, memo=memo)
    if A.applies("A2", b):
        x = A.record_values(rel)
        out["A2"] = A.align_costs(x, rel, cands, cfg, memo=memo)
        if b != "R7":
            out["A2-lam4"] = A.align_costs(x, rel, cands, cfg, lam=4, memo=memo)
            out["A2-lam16"] = A.align_costs(x, rel, cands, cfg, lam=16, memo=memo)
    if A.applies("A2b", b):
        x = [v for v, _ in model["boundary"].segments(rel)]
        out["A2b"] = A.align_vec.costs(x, [c.lens for c in cands], A.LAM, "full")
    if A.applies("A3", b):
        if b == "R3-u":
            sc = A.a3_r3u_scores(rel, cands, model["digraph"], model["length"])
            out["A3-sum"] = -np.array([s for s, _, _ in sc])
            out["A3-mean"] = -np.array([m for _, m, _ in sc])
            out["A3-len"] = -np.array([l for _, _, l in sc])
        elif b == "R7":
            out["A3"] = A.a3_r7_costs(rel, cands, model["r7"][rel.p], cfg)
        else:
            out["A3"] = A.a3_costs(rel, cands, model["digraph"])
    return out


def window_costs(rel, cands, model, cfg, cache):
    """{attacker: costs over the candidate windows} (window end). cache: a dict per released window that keeps the
    record side of A2-b and A3 across draws."""
    out, b = {}, rel.base
    out["A0"] = A.a0_costs(rel, cands)
    if A.applies("A2", b) or b in WINDOW_A2_EXTRA:
        out["A2"] = A.align_costs(A.record_values(rel), rel, cands, cfg, end="window")
    if b == "R3-u":
        if "a2b" not in cache:
            segs = model["boundary"].segments(rel)
            cats = rel.cats()
            segp = [(v, [i for i in idx if cats[i] != "backspace"], any(cats[i] == "backspace" for i in idx))
                    for v, idx in segs]
            cache["a2b"] = ([v for v, _ in segs], A.SegPrep(segp, rel.times()))
        x, prep = cache["a2b"]
        out["A2b"] = A.align_vec.costs(x, [c.lens for c in cands], A.LAM, "window")
        al = A.align_vec.align_many(x, [c.lens for c in cands], A.LAM, "window")
        tot, n = A.a3_scores(model["digraph"], prep, cands, [g for _, g in al])
        ok = ~np.isnan(tot)
        s_sum, s_mean = np.full(len(cands), INF), np.full(len(cands), INF)
        s_sum[ok] = -tot[ok]
        s_mean[ok] = -np.where(n[ok] > 0, tot[ok] / np.maximum(n[ok], 1), 0.0)
        out["A3-sum"], out["A3-mean"] = s_sum, s_mean
    elif A.applies("A3", b):
        if b == "R7":
            out["A3"] = A.a3_r7_costs(rel, cands, model["r7"][rel.p], cfg, end="window")
        else:
            out["A3"] = A.a3_costs(rel, cands, model["digraph"], end="window", cache=cache)
    return out


def window_release(rel, row_range, seg_range):
    a, b = row_range
    if rel.base == "R4":
        s0 = seg_range[0] + (1 if MUTATE == "window_r4_shift" else 0)
        return forms.Released(rel.form, values=rel.values[s0:seg_range[1] + 1])
    if rel.base == "R7":
        orig = [i for i, k in enumerate(rel.keep) if k]
        if MUTATE == "window_r7_shift":
            orig = list(range(len(rel.rows)))
        return forms.Released(rel.form, rows=[r for r, o in zip(rel.rows, orig) if a <= o <= b])
    return forms.Released(rel.form, rows=rel.rows[a:b + 1])


def evaluate_writer(w, ctx):
    """Cells for one writer: {('full', form, attacker, N): stats}, {('window', form, attacker, N, k): stats},
    utility values per form, counts, and the cost vectors when ctx.keep_costs (for the negative control)."""
    cfg, seed, p = ctx.cfg, ctx.seed, w.prompt
    model = ctx.models[ctx.fold_of_prompt[p]]
    pool, ids = ctx.pools[p], ctx.pool_ids[p]
    me = ids.index(w.writer)
    rels = {f: forms.release(w.rows, f, seed, p, w.writer) for f in ctx.forms}
    final, origins = replay_origins(w.rows)
    res = {"writer": w.writer, "prompt": p, "full": {}, "window": {}, "utility": {}, "counts": {}, "costs": None,
           "rebuilt_match": norm_ws(final) == norm_ws(pool[me].text), "open_world": {}}
    memo = {}
    costs = {f: full_costs(rel, pool, model, cfg, memo) for f, rel in rels.items()}
    for N in ctx.n_values:
        for d in range(matching.DRAWS[N]):
            dec = matching.draw_decoys(seed, p, w.writer, N, ids, {me}, d)
            if dec is None:
                res["counts"]["full_too_few_%d" % N] = 1
                break
            cand = [me] + dec[0]
            for f in ctx.forms:
                for a, cv in costs[f].items():
                    if a.startswith("A2-lam") and N != 1000:
                        continue
                    _add(res["full"], ("full", f, a, N), matching.credit_stats(0, cv[cand]))
                if N == ctx.open_world_n:
                    for a, cv in adaptive_costs(costs[f]).items():
                        res["open_world"].setdefault((f, a), []).append((float(np.min(cv[cand])),
                                                                         float(np.min(cv[dec[0]]))))
    _finish(res["full"])
    if ctx.keep_costs:
        res["costs"] = {f: adaptive_costs(costs[f]) for f in ctx.nc_forms if f in costs}
    if ctx.windows:
        _windows(w, ctx, rels, model, res, final, origins)
    tm = ctx.task_max[p]
    for f, rel in rels.items():
        res["utility"][f] = utility.metrics(rel, tm)
    return res


def _add(cells, key, st):
    credit, top5, rr, all_inf, only_true_inf = st
    c = cells.setdefault(key, [0.0, 0.0, 0.0, 0, 0, 0])
    c[0] += credit
    c[1] += top5
    c[2] += rr
    c[3] += int(all_inf)
    c[4] += int(only_true_inf)
    c[5] += 1


def _finish(cells):
    for k, c in cells.items():
        n = c[5]
        cells[k] = {"acc": c[0] / n, "top5": c[1] / n, "rr": c[2] / n, "all_inf": c[3], "only_true_inf": c[4],
                    "draws": n}


def _windows(w, ctx, rels, model, res, final, origins):
    cfg, seed, p = ctx.cfg, ctx.seed, w.prompt
    pool, ids = ctx.pools[p], ctx.pool_ids[p]
    me = ids.index(w.writer)
    words_final = re.findall(r"[A-Za-z0-9]+", final)
    words_dist = pool[me].words
    res["counts"]["final_words_match_text"] = int(words_final == words_dist)
    # bias of true windows: A2 cost per word of the whole record against the whole true text (full-text end)
    res["window_bias"], res["window_bias_full"] = {}, {}
    for f, rel in rels.items():
        if A.applies("A2", rel.base) or rel.base in WINDOW_A2_EXTRA:
            c = A.align_costs(A.record_values(rel), rel, [pool[me]], cfg)[0]
            res["window_bias_full"][f] = float(c) / max(len(pool[me].words), 1)
    for k in KS:
        valid, reasons = matching.true_window_starts(w.rows, final, origins, words_final, words_dist, k)
        for r, n in reasons.items():
            res["counts"]["window_k%d_%s" % (k, r)] = n
        if not valid:
            res["counts"]["window_k%d_none_valid" % k] = 1
            continue
        picks = matching.pick_window_starts(seed, p, w.writer, k, valid)
        for si in picks:
            row_range, seg_range, ts = valid[si]
            wrel = {f: window_release(rel, row_range, seg_range) for f, rel in rels.items()}
            caches = {f: {} for f in wrel}
            true_c = A.WindowCand(pool[me], ts, k)
            for f, rel in wrel.items():
                if f in res["window_bias_full"]:
                    c = A.align_costs(A.record_values(rel), rel, [true_c], cfg, end="window")[0]
                    res["window_bias"].setdefault((f, k), []).append(float(c) / k)
            for N in ctx.n_values:
                for d in range(matching.DRAWS[N]):
                    dec = matching.draw_decoys(seed, p, w.writer, N, ids, {me}, "%d:%d" % (si, d), k)
                    if dec is None:
                        break
                    idx, g = dec
                    cands = [true_c] + [A.WindowCand(pool[j], matching.decoy_window(g, len(pool[j].words), k), k)
                                        for j in idx]
                    for f, rel in wrel.items():
                        for a, cv in window_costs(rel, cands, model, cfg, caches[f]).items():
                            _add(res["window"], ("window", f, a, N, k), matching.credit_stats(0, cv))
    _finish(res["window"])
