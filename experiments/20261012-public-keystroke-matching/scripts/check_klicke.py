"""Checks 1 to 4 after acquisition (preregistration, "Checks after acquisition, before the main computation").
Counts, hashes and distributions only; no ID, no row, no text and no excerpt is written or printed.

    python -I scripts/check_klicke.py --root raw/klicke/extracted/WritingTask --out results/data_checks_klicke.json

1. rows, writers, writers per prompt, exclusions by reason, IDs in more than one prompt (SHA-256 of the files:
   raw/klicke/manifest_extracted.sha256, recorded at acquisition).
2. the pressed-key values outside the key_categories map (down_event values that fall to 'other'), the activity
   values (Move From collapsed) and the counts of the simulation's assumptions listed in check 2.
3. the R0 replay of the record (corpus.replay_origins, the same as the main computation) against the distributed
   text: exact match after whitespace normalisation (evaluate.norm_ws) and the normalised edit distance
   (Levenshtein over characters / the longer length).
4. the record segments of the segment rule (synthetic_logs.record_segments on the R0 categories) against the value
   from the true correspondence of R0: the letters and digits of the final draft typed by the segment's presses.
Checks 2 to 4 use the writers' rows as distributed for check 2 and the active rows after exclusion for 3 and 4.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus  # noqa: E402
import load_klicke  # noqa: E402
from synthetic_logs import category, record_segments, shortcut_flags  # noqa: E402

MODIFIER_KEYS = {"Shift", "Control", "Alt", "Meta", "CapsLock"}
NAME = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,23}$")
ALNUM = re.compile(r"[A-Za-z0-9]")


def safe_value(v):
    """A key or activity value is written only when it looks like a key name; otherwise its shape only."""
    if NAME.match(v) or v in ("Remove/Cut",):
        return v
    return "<other value: length %d>" % len(v)


def norm_ws(s):
    return " ".join(s.split())


def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    m = len(b)
    if m == 0:
        return len(a)
    bb = np.array([ord(c) for c in b], dtype=np.int64)
    idx = np.arange(m + 1, dtype=np.int64)
    prev = idx.copy()
    t = np.empty(m + 1, dtype=np.int64)
    for i, ch in enumerate(a, 1):
        cost = (bb != ord(ch)).astype(np.int64)
        t[0] = i
        np.minimum(prev[1:] + 1, prev[:-1] + cost, out=t[1:])
        prev = np.minimum.accumulate(t - idx) + idx
    return int(prev[m])


def check2(rows):
    c = Counter()
    act, other_keys, nonascii = Counter(), Counter(), Counter()
    cats = [category(r["down_event"]) for r in rows]
    sc = shortcut_flags(cats)
    for i, r in enumerate(rows):
        a, de, ue, tc = r["activity"], r["down_event"], r["up_event"], r["text_change"]
        act["Move From" if a.startswith("Move From") else safe_value(a)] += 1
        cat = cats[i]
        if cat == "other":
            other_keys[safe_value(de)] += 1
        if len(de) == 1 and not de.isascii():
            nonascii[cat] += 1
        if de != ue:
            c["down_event_differs_from_up_event"] += 1
        if tc.count(" => ") >= 2:
            c["text_change_two_or_more_arrows"] += 1
            if a == "Replace":
                c["text_change_two_or_more_arrows_replace"] += 1
        if a == "Paste" and tc == "NoChange":
            c["paste_nochange"] += 1
        # rows with the effect of a shortcut: a paste, or a letter/digit press that removes text or inserts more
        # than one character (cut, undo, redo)
        effect = None
        if a == "Paste":
            effect = "paste"
        elif cat in ("letter", "digit") and a == "Remove/Cut":
            effect = "letter_remove"
        elif cat in ("letter", "digit") and a == "Input" and tc != "NoChange" and len(tc) > 1:
            effect = "letter_multi_insert"
        if effect:
            c["shortcut_effect_" + effect] += 1
            if not sc[i]:
                c["shortcut_effect_not_after_control_" + effect] += 1
        if de in MODIFIER_KEYS and r["action_time"] != 0:
            c["modifier_action_time_nonzero"] += 1
            c["modifier_action_time_nonzero_" + de] += 1
        if de in MODIFIER_KEYS:
            c["modifier_rows_" + de] += 1
        if de == "Leftclick" and not (a.startswith("Move From") or a == "Nonproduction"):
            c["leftclick_activity_not_move_or_nonproduction"] += 1
            c["leftclick_activity_" + ("Move From" if a.startswith("Move From") else safe_value(a))] += 1
    return c, act, other_keys, nonascii, Counter(cats)


def check4(rows, final, origins):
    cats = [category(r["down_event"]) for r in rows]
    surv = Counter()
    for ci, o in enumerate(origins):
        if o is not None and ALNUM.match(final[ci]):
            surv[o] += 1
    diffs = []
    for v, idx in record_segments(cats):
        diffs.append(v - sum(surv.get(r, 0) for r in idx))
    return diffs


def work(w):
    load_klicke.fill_rows(w)
    out = {"prompt": w.prompt, "load_error": w.extra.get("load_error"), "rows": len(w.rows),
           "encoding": w.extra.get("encoding"), "text_encoding": w.extra.get("text_encoding"),
           "up_event_id_differs": w.extra.get("up_event_id_differs", 0),
           "row_number_from_1": w.extra.get("first_column_row_number_from_1"),
           "row_number_from_0": w.extra.get("first_column_row_number_from_0")}
    if w.rows:
        out["c2"] = check2(w.rows)
    w.rows = corpus.active_rows(w.rows)
    w.text = (w.text or "").replace("\r\n", "\n")
    out["active_rows"] = len(w.rows)
    why = corpus.exclusion_reason(w)
    out["excluded"] = why
    if why:
        return out
    final, origins = corpus.replay_origins(w.rows)
    a, b = norm_ws(final), norm_ws(w.text)
    out["match"] = a == b
    out["ned"] = 0.0 if a == b else levenshtein(a, b) / max(len(a), len(b))
    out["seg_diffs"] = check4(w.rows, final, origins)
    return out


def q(xs, ps=(0, 10, 25, 50, 75, 90, 100)):
    if not xs:
        return None
    return {str(p): round(float(np.percentile(xs, p)), 4) for p in ps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    writers, report = load_klicke.load(args.root)
    with ProcessPoolExecutor(args.workers) as ex:
        res = list(ex.map(work, writers, chunksize=16))

    prompts = sorted({r["prompt"] for r in res})
    c2, act, other, nonascii, cats = Counter(), Counter(), Counter(), Counter(), Counter()
    other_writers = Counter()
    for r in res:
        if "c2" in r:
            a, b, o, n, ca = r["c2"]
            c2.update(a)
            act.update(b)
            other.update(o)
            nonascii.update(n)
            cats.update(ca)
            other_writers.update(set(o))
    kept = [r for r in res if not r["excluded"]]
    ned = [r["ned"] for r in kept]
    diffs = [d for r in kept for d in r["seg_diffs"]]
    hist = Counter(max(-6, min(6, d)) for d in diffs)
    out = {
        "check1": {
            "files": report,
            "writers": len(res),
            "rows_total": sum(r["rows"] for r in res),
            "rows_per_writer": q([r["rows"] for r in res if r["rows"]]),
            "active_rows_total_kept": sum(r["active_rows"] for r in kept),
            "load_errors": dict(Counter(r["load_error"] for r in res if r["load_error"])),
            "log_encoding": dict(Counter(r["encoding"] for r in res)),
            "text_encoding": dict(Counter(r["text_encoding"] for r in res)),
            "first_column_row_number_from_1": sum(1 for r in res if r["row_number_from_1"]),
            "first_column_row_number_from_0": sum(1 for r in res if r["row_number_from_0"]),
            "prompts": len([p for p in prompts if p]),
            "writers_per_prompt": {("<no score row>" if not p else safe_prompt(p, i)): sum(1 for r in res if r["prompt"] == p)
                                   for i, p in enumerate(prompts)},
            "kept_per_prompt": {("<no score row>" if not p else safe_prompt(p, i)): sum(1 for r in kept if r["prompt"] == p)
                                for i, p in enumerate(prompts)},
            "excluded": dict(Counter(r["excluded"] for r in res if r["excluded"])),
            "kept": len(kept),
        },
        "check2": {
            "columns": load_klicke.EXPECTED_HEADER,
            "column_map": load_klicke.COLMAP,
            "columns_not_in_table": list(load_klicke.NOT_IN_TABLE),
            "activity_values": dict(act.most_common()),
            "key_values_not_in_map": {k: {"rows": v, "writers": other_writers[k]} for k, v in other.most_common()},
            "single_char_non_ascii_key_rows_by_category": dict(nonascii),
            "rows_by_category": dict(cats.most_common()),
            "up_event_id_differs_from_down_event_id": sum(r["up_event_id_differs"] for r in res),
            "assumption_counts": dict(sorted(c2.items())),
        },
        "check3": {
            "writers": len(kept),
            "exact_match_after_whitespace_normalisation": sum(1 for r in kept if r["match"]),
            "share": round(sum(1 for r in kept if r["match"]) / max(len(kept), 1), 4),
            "normalised_edit_distance": q(ned),
            "normalised_edit_distance_bins": {
                "0": sum(1 for x in ned if x == 0), "(0, 0.01]": sum(1 for x in ned if 0 < x <= 0.01),
                "(0.01, 0.05]": sum(1 for x in ned if 0.01 < x <= 0.05),
                "(0.05, 0.1]": sum(1 for x in ned if 0.05 < x <= 0.1),
                "(0.1, 0.5]": sum(1 for x in ned if 0.1 < x <= 0.5), "> 0.5": sum(1 for x in ned if x > 0.5)},
        },
        "check4": {
            "segments": len(diffs),
            "equal": sum(1 for d in diffs if d == 0),
            "share_equal": round(sum(1 for d in diffs if d == 0) / max(len(diffs), 1), 4),
            "rule_minus_true_histogram (clipped at +-6)": {str(k): hist[k] for k in sorted(hist)},
            "writers_all_segments_equal": sum(1 for r in kept if all(d == 0 for d in r["seg_diffs"])),
            "share_of_segments_equal_per_writer": q([sum(1 for d in r["seg_diffs"] if d == 0) / len(r["seg_diffs"])
                                                     for r in kept if r["seg_diffs"]]),
        },
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")


def safe_prompt(p, i):
    """Prompt names are the task names of the distribution (not the writers' content); long values are cut."""
    return p if len(p) <= 60 else p[:60] + "..."


if __name__ == "__main__":
    main()
