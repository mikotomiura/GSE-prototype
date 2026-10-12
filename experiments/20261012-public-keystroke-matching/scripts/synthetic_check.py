"""The pre-freeze check on synthetic logs (preregistration.md, "公開の他の列から長さが戻らないかの検査"). No human data.

Parts (results/synthetic_check.json; numbers in notes.md):
1. paths: per form, which published columns give back the segment lengths (final-draft word lengths) and how well.
2. twins: records that share every key category and time but differ in hidden choices; a form whose output is
   identical for the two cannot give back what differs (columns other than categories and times carry nothing).
3. r7: share of true groups above the cap, the true text's path cut, cost of the true correspondence vs the DP cost.
4. a3_r3u: how one replay error lowers the true text's timing term (decision 38).
"""
import hashlib
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import align_ext  # noqa: E402
from replay import a1_r2, a1_text, a1prime, lengths_of_items  # noqa: E402
from synthetic_logs import (ALL_CATS, CHAR_CATS, DEFAULT_OPS, MOD_CATS, NAV_CATS, NO_OPS, Writer, category, form_R0, form_R1, form_R2,  # noqa: E402
                            form_R3, form_R3t, form_R3u, form_R5, form_R6, form_R7, record_segments,
                            word_lengths)

EXP = os.path.dirname(HERE)
LIGHT_OPS = {k: v / 4 for k, v in DEFAULT_OPS.items()}
MUTATE = os.environ.get("SYNTH_MUTATE", "")
LAM = 8


def no_dup(pairs):
    keys = [k for k, _ in pairs]
    dup = {k for k in keys if keys.count(k) > 1}
    if dup:
        raise ValueError("duplicate keys in config.json: %s" % sorted(dup))
    return dict(pairs)


def load_config():
    with open(os.path.join(EXP, "config.json"), encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=no_dup)


def read_seed():
    with open(os.path.join(EXP, "SEED"), encoding="utf-8") as f:
        return f.read().strip()


def seed_int(use, prompt="", writer="", N="", k="", draw=""):
    s = "%s:%s:%s:%s:%s:%s:%s" % (read_seed(), use, prompt, writer, N, k, draw)
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def rec_seeds(part, i, twin=0):
    return (seed_int("synthetic", part, str(i), "", "", "keys"),
            seed_int("synthetic", part, str(i), "", "", "hidden%d" % twin),
            seed_int("synthetic", part, str(i), "", "", "letters%d" % twin))


def summary(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return None
    a = np.array(xs, dtype=float)
    return {"n": len(xs), "mean": round(float(a.mean()), 4), "p10": round(float(np.percentile(a, 10)), 4),
            "median": round(float(np.median(a)), 4), "p90": round(float(np.percentile(a, 90)), 4),
            "min": round(float(a.min()), 4), "max": round(float(a.max()), 4)}


def keys_of(rows):
    return [r["down_event"] for r in rows]


def cats_of_rows(rows):
    return [r["down_event"] if r["down_event"] in ALL_CATS else category(r["down_event"]) for r in rows]


# --- 1. paths -----------------------------------------------------------------------------------------------------

def ned(a, b):
    """Normalised edit distance of two sequences."""
    if not a and not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1] / max(len(a), len(b))


def part_paths(n, ops, label):
    res = defaultdict(lambda: {"wl_exact": 0, "total_exact": 0, "abs_total": [], "ned": [], "n": 0})
    wc_exact = 0
    for i in range(n):
        ks, hs, ls = rec_seeds("paths_" + label, i)
        rec = Writer(ks, hs, ls, ops=ops).run()
        wl = word_lengths(rec.final)
        total = sum(wl)
        rng = np.random.default_rng(seed_int("synthetic", "paths_form_" + label, str(i)))

        def put(name, est_wl):
            d = res[name]
            d["n"] += 1
            d["wl_exact"] += int(est_wl == wl)
            d["total_exact"] += int(sum(est_wl) == total)
            d["abs_total"].append(abs(sum(est_wl) - total))
            d["ned"].append(ned(est_wl, wl))

        for fname, rows in (("R0", form_R0(rec)), ("R1", form_R1(rec)), ("R5", form_R5(rec, rng)),
                            ("R6", form_R6(rec, rng))):
            put(fname + ":A1(text_change+position)", word_lengths(a1_text(rows)))
        r2 = form_R2(rec)
        wc_exact += int(r2[-1]["word_count"] == len(rec.final.split()))
        put("R2:A1(category+position)", lengths_of_items(a1_r2(cats_of_rows(r2), [r["cursor_position"] for r in r2])))
        put("R2:A1'", lengths_of_items(a1prime(cats_of_rows(r2))))
        put("R3:A1'", lengths_of_items(a1prime(cats_of_rows(form_R3(rec)))))
        # R3-u: only the char count can come back
        u = a1prime(cats_of_rows(form_R3u(rec)), uncertain_home_end=True)
        d = res["R3-u:A1'_charcount"]
        d["n"] += 1
        d["total_exact"] += int(len(u) == len(rec.final))
        d["abs_total"].append(abs(len(u) - len(rec.final)))
    out = {}
    for k, d in sorted(res.items()):
        out[k] = {"n": d["n"], "word_lengths_exact": round(d["wl_exact"] / d["n"], 4) if "charcount" not in k else None,
                  "total_exact": round(d["total_exact"] / d["n"], 4), "abs_total": summary(d["abs_total"]),
                  "word_lengths_ned": summary(d["ned"]) if d["ned"] else None}
    out["R2:word_count_last_row_equals_whitespace_words"] = round(wc_exact / n, 4)
    return out


# --- 2. twins -----------------------------------------------------------------------------------------------------

def forms_for_twins(rec, i):
    rng7 = np.random.default_rng(seed_int("synthetic", "twins_r7", str(i)))
    return {
        "R0": form_R0(rec), "R1": form_R1(rec), "R2": form_R2(rec),
        "R3": form_R3(rec, mutate=MUTATE or None), "R3-u": form_R3u(rec), "R3-t(100)": form_R3t(rec, 100),
        "R7(0.25)": form_R7(rec, 0.25, rng7)[0],
    }


def same(a, b):
    if MUTATE == "twins_always_same":
        return True
    return a == b


def part_twins(n, timing):
    structural, differ_final = 0, 0
    identical = defaultdict(int)
    cols = defaultdict(lambda: defaultdict(int))
    for i in range(n):
        a = Writer(*rec_seeds("twins", i, 0), timing=timing).run()
        b = Writer(*rec_seeds("twins", i, 1), timing=timing).run()
        if [category(r["down_event"]) for r in a.rows] != [category(r["down_event"]) for r in b.rows]:
            continue
        structural += 1
        if word_lengths(a.final) == word_lengths(b.final):
            continue
        differ_final += 1
        fa, fb = forms_for_twins(a, i), forms_for_twins(b, i)
        for f in fa:
            if same(fa[f], fb[f]):
                identical[f] += 1
            else:
                for c in fa[f][0]:
                    if any(x[c] != y[c] for x, y in zip(fa[f], fb[f])):
                        cols[f][c] += 1
    return {"pairs": n, "same_category_sequence": structural, "different_final_word_lengths": differ_final,
            "identical_output_share": {f: round(identical[f] / differ_final, 4) if differ_final else None
                                       for f in ("R0", "R1", "R2", "R3", "R3-u", "R3-t(100)", "R7(0.25)")},
            "columns_that_differ": {f: dict(v) for f, v in cols.items()}}


# --- 3. R7 --------------------------------------------------------------------------------------------------------

def word_index_of_char(final):
    idx, w, inword = [None] * len(final), -1, False
    for i, ch in enumerate(final):
        if ch.isalnum():
            if not inword:
                w += 1
                inword = True
            idx[i] = w
        else:
            inword = False
    return idx


def true_groups(segs, row_word, n_words):
    """Groups (i0, i1, j0, j1) of the true correspondence; non-monotone pieces are merged (counted)."""
    spans = []
    for v, idx in segs:
        ws = [row_word[i] for i in idx if row_word.get(i) is not None]
        spans.append((min(ws), max(ws)) if ws else None)
    groups, nonmono = [], 0
    for si, sp in enumerate(spans):
        if sp is None:
            if groups:
                groups[-1][1] = si + 1
            else:
                groups.append([si, si + 1, 0, 0])
            continue
        a, b = sp
        if groups and groups[-1][3] > a:  # overlaps or goes back: merge
            if a < groups[-1][2]:
                nonmono += 1
            g = groups[-1]
            g[1], g[2], g[3] = si + 1, min(g[2], a), max(g[3], b + 1)
            # merge earlier groups the span reaches back into
            while len(groups) > 1 and groups[-2][3] > groups[-1][2]:
                h = groups.pop()
                groups[-1][1], groups[-1][2], groups[-1][3] = h[1], min(groups[-1][2], h[2]), max(groups[-1][3], h[3])
        elif groups and groups[-1][3] == groups[-1][2]:  # a leading group with no word yet
            groups[-1][1], groups[-1][2], groups[-1][3] = si + 1, a, b + 1
        else:
            groups.append([si, si + 1, a, b + 1])
    # text words between groups go to the group on the left (the first group takes leading words)
    if not groups:
        return [], nonmono
    groups[0][2] = 0
    for g, h in zip(groups, groups[1:]):
        g[3] = h[2]
    groups[-1][3] = n_words
    return [tuple(g) for g in groups if not (g[0] == g[1] and g[2] == g[3])], nonmono


def part_r7(n, cfg, ops, label):
    out = {}
    for p in (0.0, 0.1, 0.25, 0.5):
        if p:
            groups, cap = align_ext.r7_groups(cfg, p)
        else:
            groups, cap = list(align_ext.T.ORDER), 3
        above, n_groups, rec_above, cut, cut_window, used4 = 0, 0, 0, 0, defaultdict(int), 0
        diff, true_cost, dp_cost, nonmono_recs = [], [], [], 0
        win_n = defaultdict(int)
        for i in range(n):
            rec = Writer(*rec_seeds("r7_" + label, i), ops=ops).run()
            keep = np.random.default_rng(seed_int("r7_drop", "synthetic", str(i), "", "", str(p))).random(len(rec.rows)) >= p
            kept = [j for j in range(len(rec.rows)) if keep[j]]
            cats = [category(rec.rows[j]["down_event"]) for j in kept]
            segs = record_segments(cats)
            surv = rec.surviving()
            widx = word_index_of_char(rec.final)
            row_word = {}
            for jj, j in enumerate(kept):
                fi = surv.get(rec.rows[j]["event_id"])
                if fi is not None and widx[fi] is not None:
                    row_word[jj] = widx[fi]
            y = word_lengths(rec.final)
            yy = [(1 - p) * v for v in y]
            x = [v for v, _ in segs]
            tg, nonmono = true_groups(segs, row_word, len(y))
            nonmono_recs += int(nonmono > 0)
            big = [g for g in tg if (g[1] - g[0]) > cap or (g[3] - g[2]) > cap]
            above += len(big)
            n_groups += len(tg)
            rec_above += int(bool(big))
            tc = align_ext.path_cost(x, yy, tg, LAM)
            c, g = align_ext.align(x, yy, LAM, "full", groups=groups, max_group=cap)
            true_cost.append(tc / max(1, len(y)))
            if c == align_ext.INF:
                cut += 1
            else:
                dp_cost.append(c / max(1, len(y)))
                diff.append((c - tc) / max(1, len(y)))
                used4 += int(any(max(b - a, d - e) >= 4 for a, b, e, d in g))
            # windows: k consecutive R0 segments, the presses inside, suppressed, re-segmented, window end
            r0segs = record_segments([category(r["down_event"]) for r in rec.rows])
            r0_row_word = {}
            for j, r in enumerate(rec.rows):
                fi = surv.get(r["event_id"])
                if fi is not None and widx[fi] is not None:
                    r0_row_word[j] = widx[fi]
            wrng = np.random.default_rng(seed_int("synthetic", "r7_window", str(i), "", "", str(p)))
            for k in (5, 10, 20, 50):
                starts = [s for s in range(len(r0segs) - k + 1) if r0segs[s][1]]
                if not starts:
                    continue
                s = starts[int(wrng.integers(0, len(starts)))]
                first = [r0_row_word[j] for j in r0segs[s][1] if j in r0_row_word]
                if not first:
                    continue
                w0 = max(set(first), key=lambda w: (first.count(w), -w))
                if w0 + k > len(y):
                    continue
                lo = r0segs[s][1][0]
                last_idx = r0segs[s + k - 1][1]
                hi = (last_idx[-1] if last_idx else lo)
                # include the separator that closes the window's last segment
                while hi + 1 < len(rec.rows) and category(rec.rows[hi + 1]["down_event"]) not in ("space", "punctuation", "enter"):
                    hi += 1
                hi = min(hi + 1, len(rec.rows) - 1)
                wk = [j for j in range(lo, hi + 1) if keep[j]]
                xw = [v for v, _ in record_segments([category(rec.rows[j]["down_event"]) for j in wk])]
                cw, _ = align_ext.align(xw, [(1 - p) * v for v in y[w0:w0 + k]], LAM, "window", groups=groups,
                                        max_group=cap)
                win_n[k] += 1
                cut_window[k] += int(cw == align_ext.INF)
        out[str(p)] = {
            "records": n, "cap": cap, "groups": len(groups),
            "true_groups_above_cap_share": round(above / n_groups, 5) if n_groups else None,
            "records_with_a_true_group_above_cap": round(rec_above / n, 4),
            "records_with_nonmonotone_true_correspondence": round(nonmono_recs / n, 4),
            "true_text_path_cut_full": round(cut / n, 4),
            "true_text_path_cut_window": {str(k): (round(cut_window[k] / win_n[k], 4) if win_n[k] else None)
                                          for k in (5, 10, 20, 50)},
            "window_records": {str(k): win_n[k] for k in (5, 10, 20, 50)},
            "dp_uses_group_of_4_or_more": round(used4 / max(1, n - cut), 4),
            "true_correspondence_cost_per_word": summary(true_cost),
            "dp_cost_per_word": summary(dp_cost),
            "dp_minus_true_cost_per_word": summary(diff),
        }
    return out


# --- 4. A3 on R3-u with one replay error ----------------------------------------------------------------------------

def char_rows(rows):
    """Indices of char presses with the previous char press when the two were consecutive char presses
    (modifier and navigation presses skipped; any other press breaks the chain)."""
    prev_char = {}
    last = None
    for j, r in enumerate(rows):
        c = category(r["down_event"])
        if c in CHAR_CATS:
            if last is not None:
                prev_char[j] = last
            last = j
        elif c in MOD_CATS + NAV_CATS:
            continue
        else:
            last = None
    return prev_char


def ctype(ch):
    return "L" if ch.isalpha() else ("D" if ch.isdigit() else ("S" if ch == " " else ("N" if ch == "\n" else "P")))


def train_table(recs):
    by_pair, by_type = defaultdict(list), defaultdict(list)
    for rec in recs:
        prev = char_rows(rec.rows)
        for j, i in prev.items():
            a = rec.rows[i]["down_event"]
            b = rec.rows[j]["down_event"]
            ca, cb = (" " if a == "Space" else "\n" if a == "Enter" else a), (" " if b == "Space" else "\n" if b == "Enter" else b)
            li = math.log(max(1, rec.rows[j]["down_time"] - rec.rows[i]["down_time"]))
            by_pair[(ca.lower(), cb.lower())].append(li)
            by_type[(ctype(ca), ctype(cb))].append(li)
    stat = lambda v: (float(np.mean(v)), float(np.var(v)) + 1e-6)
    allv = [x for v in by_type.values() for x in v]
    # the preregistration fills pairs seen fewer than 20 times with the character-type pair; a type pair seen fewer
    # than 20 times is filled with all intervals (not in the preregistration; notes.md)
    return ({k: stat(v) for k, v in by_pair.items() if len(v) >= 20},
            {k: stat(v) for k, v in by_type.items() if len(v) >= 20}, stat(allv))


def timing_term(doc, rows, prev, text, table):
    pair, typ, glob = table
    lls = []
    m = min(len(doc), len(text))
    for i in range(1, m):
        a, b = doc[i - 1][1], doc[i][1]
        if a is None or b is None or prev.get(b) != a:
            continue
        ca, cb = text[i - 1].lower(), text[i].lower()
        mu, var = pair.get((ca, cb)) or typ.get((ctype(ca), ctype(cb)), glob)
        li = math.log(max(1, rows[b]["down_time"] - rows[a]["down_time"]))
        lls.append(-0.5 * math.log(2 * math.pi * var) - (li - mu) ** 2 / (2 * var))
    if not lls:
        return 0.0, 0.0, 0
    return float(np.sum(lls)), float(np.mean(lls)), len(lls)


def part_a3(n_train, n_test, n_decoys):
    train = [Writer(*rec_seeds("a3_train", i), timing="digraph", ops=NO_OPS).run() for i in range(n_train)]
    table = train_table(train)
    test = [Writer(*rec_seeds("a3_test", i), timing="digraph", ops=NO_OPS).run() for i in range(n_test)]
    pool = [Writer(*rec_seeds("a3_decoy", i), timing="digraph", ops=NO_OPS).run().final for i in range(n_decoys)]
    exact = 0
    res = defaultdict(list)
    for t, rec in enumerate(test):
        rows = rec.rows
        cats = [category(r["down_event"]) for r in rows]
        merged = ["char" if c in CHAR_CATS else c for c in cats]
        doc = a1prime(merged, uncertain_home_end=True)
        surv = rec.surviving()
        if [surv.get(rows[j]["event_id"]) for _, j in doc] != list(range(len(rec.final))):
            continue
        exact += 1
        prev = char_rows(rows)
        variants = {"none": doc}
        for f in (0.1, 0.5, 0.9):
            pos = max(1, int(f * len(doc)))
            variants["insert_%.1f" % f] = doc[:pos] + [("c", None)] + doc[pos:]
            variants["delete_%.1f" % f] = doc[:pos] + doc[pos + 1:]
        for name, d in variants.items():
            ts, tm, tn = timing_term(d, rows, prev, rec.final, table)
            dm = [timing_term(d, rows, prev, txt, table)[1] for txt in pool]
            dsum = [timing_term(d, rows, prev, txt, table)[0] for txt in pool]
            res[name + ":true_mean"].append(tm)
            res[name + ":decoy_mean"].append(float(np.mean(dm)))
            res[name + ":top1_mean_version"].append(float(tm > max(dm)))
            res[name + ":top1_sum_version"].append(float(ts > max(dsum)))
    out = {"train": n_train, "test": n_test, "decoys": n_decoys, "test_with_exact_replay": exact}
    base_gap = [a - b for a, b in zip(res["none:true_mean"], res["none:decoy_mean"])]
    out["none"] = {"true_mean": summary(res["none:true_mean"]), "decoy_mean": summary(res["none:decoy_mean"]),
                   "top1_mean_version": round(float(np.mean(res["none:top1_mean_version"])), 4),
                   "top1_sum_version": round(float(np.mean(res["none:top1_sum_version"])), 4)}
    for name in sorted({k.split(":")[0] for k in res} - {"none"}):
        kept = [(a - d) / g for a, d, g in zip(res[name + ":true_mean"], res[name + ":decoy_mean"], base_gap) if g > 0]
        out[name] = {"true_mean": summary(res[name + ":true_mean"]),
                     "share_of_true_minus_decoy_gap_kept": summary(kept),
                     "top1_mean_version": round(float(np.mean(res[name + ":top1_mean_version"])), 4),
                     "top1_sum_version": round(float(np.mean(res[name + ":top1_sum_version"])), 4)}
    return out


def main(argv):
    quick = "--quick" in argv
    cfg = load_config()
    scale = 0.2 if quick else 1.0
    n = lambda v: max(10, int(v * scale))
    result = {
        "note": "synthetic logs only (scripts/synthetic_logs.py); magnitudes depend on the simulator's assumptions",
        "align_template_sha256": align_ext.template_sha256(),
        "numpy": np.__version__,
        "paths_with_edits": part_paths(n(300), DEFAULT_OPS, "edits"),
        "paths_light_edits": part_paths(n(300), LIGHT_OPS, "light"),
        "paths_without_edits": part_paths(n(100), NO_OPS, "clean"),
        "twins_timing_free": part_twins(n(400), "free"),
        "twins_timing_drag": part_twins(n(400), "drag"),
        "r7_without_edits": part_r7(n(200), cfg, NO_OPS, "clean"),
        "r7_with_edits": part_r7(n(200), cfg, DEFAULT_OPS, "edits"),
        "a3_r3u": part_a3(n(80), n(60), n(99)),
    }
    if "--out" in argv:
        path = argv[argv.index("--out") + 1]
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(result, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True))
    return result


if __name__ == "__main__":
    main(sys.argv[1:])
