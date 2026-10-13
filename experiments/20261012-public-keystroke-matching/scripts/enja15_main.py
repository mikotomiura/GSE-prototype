"""The ENJA15 section of the main computation (preregistration, "ENJA15 section"; config.json enja15). Writes
aggregates only (no string of the logs or the translations, no value per session).

    python -I scripts/enja15_main.py --root raw/enja15 --out results/enja15_main.json

Details fixed before any matching value (notes.md, "Implementation choices: ENJA15"):
- a session is Translog-II/P<translator>_T<source text>.xml; the translation is its LogFile/FinalTextUTF8;
- forms R0j, R3j, R3j-t(10, 100, 1000) and R4(1, 2, 4, 8); the attackers A0 and A2 read the category column only, so
  R0j, R3j and R3j-t(w) give the same costs (reported as they are);
- record segments: enja15.record_segments (both [Back] of Type IME and Type delete count -1, the literal reading);
  text segments: enja15.text_segments (SudachiPy readings, romaji_table counts);
- A2: the alignment of the preregistration (groups, lambda = 8, full-text end) of the record segment values with the
  text segment values; R4(w): floor(value / w) on both sides; A0: |record count - text count|;
- candidates: the sessions of the same source text (sorted by name); N = all is every session of the source text;
  N = 10 draws 9 decoys without replacement from the other sessions, 20 draws, seed use enja_decoys (prompt = source
  text, writer = session name, N = 10, draw = draw number); ties 1/m;
- aggregation (question 4): mean over the records of each source text, then mean over the source texts; chance 1/N
  aggregated the same way; differences inside each resample; the bootstrap resamples translators with all their
  sessions (crossed design, check 5), 2,000 resamples, seed use bootstrap with the sample name 'enja15'; a source
  text with no record in a resample is dropped from that resample's mean and the number of such resamples is
  reported; 'exceeds' only when the lower bounds of both differences are above 0.
"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import align_vec  # noqa: E402
import enja15  # noqa: E402
import matching  # noqa: E402
import seeds  # noqa: E402

NAME = re.compile(r"^P(\d+)_T(\d+)$")
FORMS = ["R0j", "R3j", "R3j-t(10)", "R3j-t(100)", "R3j-t(1000)", "R4(1)", "R4(2)", "R4(4)", "R4(8)"]
ATTACKERS = ("A0", "A2")
LAM = 8
B = 2000
DRAWS_N10 = 20
MUTATE = os.environ.get("ENJA_MUTATE", "")


class Session:
    def __init__(self, name, translator, source, rows, text_values):
        self.name, self.translator, self.source = name, translator, source
        self.rows, self.text_values = rows, text_values


def form_param(form):
    if "(" not in form:
        return form, None
    base, v = form[:-1].split("(")
    return base, int(v)


def released_values(s, form):
    """(record segment values, A0 record count) of a session in a form."""
    base, w = form_param(form)
    rows = s.rows
    if base == "R3j-t":
        rows = enja15.r3j_t(rows, w)
    segs = enja15.record_segments(rows)
    if base == "R4":
        segs = [v // w for v in segs]
        return segs, float(sum(segs))
    return segs, float(enja15.a0_record(rows))


def text_side(s, form):
    base, w = form_param(form)
    if base == "R4":
        return [v // w for v in s.text_values]
    return list(s.text_values)


def costs(rec, pool, form):
    """{attacker: costs over the pool} for one record."""
    x, a0 = released_values(rec, form)
    ys = [text_side(c, form) for c in pool]
    out = {"A0": np.array([abs(a0 - float(sum(y))) for y in ys])}
    out["A2"] = align_vec.costs(x, ys, LAM, "full")
    if MUTATE == "a2_window_end":
        out["A2"] = align_vec.costs(x, ys, LAM, "window")
    return out


def record_credits(sessions, seed):
    """{(form, attacker, N): {session name: credit}} with N 'all' and 10."""
    by_src = {}
    for s in sessions:
        by_src.setdefault(s.source, []).append(s)
    out, counts = {}, {"sources_under_10": 0}
    for src, pool in sorted(by_src.items()):
        pool = sorted(pool, key=lambda s: s.name)
        if len(pool) < 10:
            counts["sources_under_10"] += 1
        for i, rec in enumerate(pool):
            for form in FORMS:
                cv = costs(rec, pool, form)
                for att, c in cv.items():
                    out.setdefault((form, att, "all"), {})[rec.name] = matching.credit_stats(i, c)[0]
                    if len(pool) < 10:
                        continue
                    others = [j for j in range(len(pool)) if j != i]
                    if MUTATE == "decoys_include_true":
                        others = list(range(len(pool)))
                    tot = 0.0
                    for d in range(DRAWS_N10):
                        g = seeds.rng(seed, "enja_decoys", src, rec.name, 10, "", d)
                        pick = [others[k] for k in g.choice(len(others), 9, replace=False)]
                        cand = [i] + pick
                        tot += matching.credit_stats(0, c[cand])[0]
                    out.setdefault((form, att, 10), {})[rec.name] = tot / DRAWS_N10
    return out, counts


def chance_of(sessions, N):
    n_src = {}
    for s in sessions:
        n_src[s.source] = n_src.get(s.source, 0) + 1
    return {s.name: (1.0 / n_src[s.source] if N == "all" else 1.0 / N) for s in sessions}


def source_mean(values, sessions, weights=None):
    """Mean over the records of each source text, then over the source texts (weights: multiplicity per session)."""
    per = {}
    for s in sessions:
        wt = 1 if weights is None else weights.get(s.translator, 0)
        if not wt or s.name not in values:
            continue
        a = per.setdefault(s.source, [0.0, 0])
        a[0] += wt * values[s.name]
        a[1] += wt
    if not per:
        return np.nan, {}
    means = {src: v / n for src, (v, n) in per.items()}
    if MUTATE == "pool_records":
        return sum(v for v, _ in per.values()) / sum(n for _, n in per.values()), means
    return float(np.mean(list(means.values()))), means


def _records_per_source(sessions, values):
    out = {}
    for s in sessions:
        if s.name in values:
            out[s.source] = out.get(s.source, 0) + 1
    return out


def resample_weights(sessions, seed, n=B):
    translators = sorted({s.translator for s in sessions})
    g = seeds.rng(seed, "bootstrap", "", "enja15")
    out = []
    for _ in range(n):
        pick = g.integers(0, len(translators), len(translators))
        w = {}
        for k in pick:
            w[translators[k]] = w.get(translators[k], 0) + 1
        out.append(w)
    return out


def ci(v):
    v = np.asarray(v, dtype=float)
    v = v[~np.isnan(v)]
    if not len(v):
        return None
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]


def summarise(sessions, credits, seed):
    W = resample_weights(sessions, seed)
    n_src = len({s.source for s in sessions})
    missing = sum(1 for w in W if len({s.source for s in sessions if w.get(s.translator)}) < n_src)
    cells = {}
    for N in ("all", 10):
        ch = chance_of(sessions, N)
        ch_pt, _ = source_mean(ch, sessions)
        ch_b = np.array([source_mean(ch, sessions, w)[0] for w in W])
        for form in FORMS:
            vals = {}
            for att in ATTACKERS:
                v = credits.get((form, att, N))
                if v is None:
                    continue
                pt, per = source_mean(v, sessions)
                vals[att] = (pt, per, np.array([source_mean(v, sessions, w)[0] for w in W]))
            for att, (pt, per, bt) in vals.items():
                e = {"acc": pt, "ci": ci(bt), "chance": ch_pt, "x_chance": pt / ch_pt,
                     "diff_chance": pt - ch_pt, "diff_chance_ci": ci(bt - ch_b),
                     "per_source": {k: per[k] for k in sorted(per)},
                     "records_per_source": {k: n for k, n in sorted(_records_per_source(sessions, credits[(form, att, N)]).items())},
                     "records": len(credits[(form, att, N)])}
                if att != "A0" and "A0" in vals:
                    e["diff_A0"] = pt - vals["A0"][0]
                    e["diff_A0_ci"] = ci(bt - vals["A0"][2])
                    lo1 = e["diff_chance_ci"][0] if e["diff_chance_ci"] else None
                    lo2 = e["diff_A0_ci"][0] if e["diff_A0_ci"] else None
                    e["exceeds"] = bool(lo1 is not None and lo2 is not None and lo1 > 0 and lo2 > 0)
                cells["%s|%s|%s" % (form, att, N)] = e
    return cells, {"resamples": B, "resamples_missing_a_source": missing}


def load_sessions(root, reader, stats):
    xml_dir = os.path.join(root, "Translog-II")
    out, excluded = [], {}
    for fn in sorted(os.listdir(xml_dir)):
        if not fn.endswith(".xml"):
            continue
        m = NAME.match(fn[:-4])
        if not m:
            excluded["unexpected file name"] = excluded.get("unexpected file name", 0) + 1
            continue
        path = os.path.join(xml_dir, fn)
        ev = enja15.key_events(path)
        text = enja15.final_text(path)
        rows = enja15.r3j(ev)
        if not ev or text is None:
            why = "missing log or translation"
        elif not text.strip():
            why = "empty translation"
        elif not any(r["type"] == "IME" or (r["type"] == "insert" and r["category"] == "letter") for r in rows):
            why = "no Type=IME and no letter Type=insert event"
        else:
            why = None
        if why:
            excluded[why] = excluded.get(why, 0) + 1
            continue
        out.append(Session(fn[:-4], m.group(1), m.group(2), rows, enja15.text_segments(text, reader, stats)))
    return out, excluded


def describe(sessions):
    rec = [len(enja15.record_segments(s.rows)) for s in sessions]
    txt = [len(s.text_values) for s in sessions]
    q = lambda v: [float(np.quantile(v, x)) for x in (0.1, 0.5, 0.9)] if len(v) else None  # noqa: E731
    return {"sessions": len(sessions), "translators": len({s.translator for s in sessions}),
            "source_texts": len({s.source for s in sessions}),
            "sessions_without_text_segment": sum(1 for t in txt if t == 0),
            "record_segments_p10_p50_p90": q(rec), "text_segments_p10_p50_p90": q(txt),
            "record_to_text_segment_ratio_p10_p50_p90": q([a / b for a, b in zip(rec, txt) if b])}


def run(sessions, seed, extra=None):
    credits, counts = record_credits(sessions, seed)
    cells, boot = summarise(sessions, credits, seed)
    q4 = cells.get("R3j|A2|all")
    out = {"describe": describe(sessions), "counts": counts, "bootstrap": boot, "cells": cells,
           "question4": {"form": "R3j", "attacker": "A2", "N": "all",
                         "exceeds": q4.get("exceeds") if q4 else None},
           "note": "R0j, R3j and R3j-t(w) have the same costs for A0 and A2 (the rules read the category column)",
           "mutate": MUTATE}
    if extra:
        out.update(extra)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    seed = seeds.read_seed()
    stats = {}
    sessions, excluded = load_sessions(args.root, enja15.Reader(), stats)
    per_tr = {}
    for s in sessions:
        per_tr.setdefault(s.translator, set()).add(s.source)
    if not any(len(v) >= 2 for v in per_tr.values()):
        raise SystemExit("the design is nested (check 5 found it crossed): the bootstrap for a nested design "
                         "(stratified by source text) is not implemented")
    out = run(sessions, seed, {"excluded": excluded, "text_token_fallbacks": stats})
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
