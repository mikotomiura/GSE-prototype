"""Format diagnostics after checks 2 and 3 (not a registered quantity of matching or utility): whether the loader
and the R0 replay read the distributed format as assumed. Counts by character class only; no ID, no text, no row.

    python -I scripts/check_klicke_format.py --root raw/klicke/extracted/WritingTask --out results/data_checks_klicke_format.json

- check 3: for the writers whose replayed final draft differs from the distributed text after whitespace
  normalisation, the length difference and the difflib opcodes counted by (operation, class of the replayed side,
  class of the distributed side); class = letter, digit, space, ascii punctuation (the character itself is
  written for ASCII punctuation only), non-ascii (its Unicode category only).
- check 2: the rows with the effect of a shortcut, by the category of their own key and of the previous press that
  is not a modifier; key values of length 2 by Unicode categories.
"""
import argparse
import difflib
import json
import os
import string
import sys
import unicodedata
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus  # noqa: E402
import load_klicke  # noqa: E402
from check_klicke import norm_ws  # noqa: E402
from synthetic_logs import MOD_CATS, category  # noqa: E402


def cls(c):
    if c.isascii():
        if c.isalpha():
            return "letter"
        if c.isdigit():
            return "digit"
        if c.isspace():
            return "space"
        if c in string.punctuation:
            return "punct " + c
        return "ascii other"
    return "non-ascii " + unicodedata.category(c)


def side(s):
    return "+".join(sorted({cls(c) for c in s})) if s else "-"


def work(w):
    load_klicke.fill_rows(w)
    out = {"ops": Counter(), "paste": Counter(), "len2": Counter(), "lendiff": None}
    rows = w.rows
    cats = [category(r["down_event"]) for r in rows]
    for i, r in enumerate(rows):
        de = r["down_event"]
        if len(de) == 2:
            out["len2"]["+".join(unicodedata.category(c) + ("(ascii)" if c.isascii() else "") for c in de)] += 1
        a, tc = r["activity"], r["text_change"]
        kind = None
        if a == "Paste":
            kind = "paste"
        elif cats[i] in ("letter", "digit") and a == "Remove/Cut":
            kind = "letter_remove"
        if kind:
            j = i - 1
            while j >= 0 and cats[j] == "modifier":
                j -= 1
            prev = cats[j] if j >= 0 else "none"
            out["paste"]["%s | own %s | previous non-modifier %s" % (kind, cats[i], prev)] += 1
    w.rows = corpus.active_rows(rows)
    if not w.rows:
        return out
    final, _ = corpus.replay_origins(w.rows)
    a, b = norm_ws(final), norm_ws((w.text or "").replace("\r\n", "\n"))
    if a == b:
        return out
    out["lendiff"] = len(a) - len(b)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            out["ops"]["%s | replay %s | text %s" % (tag, side(a[i1:i2]), side(b[j1:j2]))] += 1
            out["ops"]["_chars %s replay" % tag] += i2 - i1
            out["ops"]["_chars %s text" % tag] += j2 - j1
    first = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    out["first_diff_decile"] = int(10 * first / max(len(a), len(b), 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    writers, _ = load_klicke.load(args.root)
    with ProcessPoolExecutor(args.workers) as ex:
        res = list(ex.map(work, writers, chunksize=16))
    ops, paste, len2, ops_writers = Counter(), Counter(), Counter(), Counter()
    lend = Counter()
    first = Counter()
    for r in res:
        ops.update(r["ops"])
        ops_writers.update(set(k for k in r["ops"] if not k.startswith("_")))
        paste.update(r["paste"])
        len2.update(r["len2"])
        if r["lendiff"] is not None:
            d = r["lendiff"]
            lend["<=-10" if d <= -10 else ">=10" if d >= 10 else str(d)] += 1
            first[r["first_diff_decile"]] += 1
    out = {"check3_length_difference_replay_minus_text": dict(sorted(lend.items())),
           "check3_first_difference_decile": dict(sorted(first.items())),
           "check3_opcodes": {k: {"count": v, "writers": ops_writers.get(k)} for k, v in ops.most_common(60)},
           "check2_shortcut_effect_rows": dict(paste.most_common()),
           "check2_key_values_of_length_2": dict(len2.most_common())}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
