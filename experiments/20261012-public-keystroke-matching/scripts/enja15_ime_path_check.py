"""The IME path check of the ENJA15 section (after acquisition, before the main computation): in records with
composition updates, cancelled conversions and commits, no string of the log (Value, IMEtext, Text or any other
attribute) remains in any column after R3j. Counts only.

    python -I scripts/enja15_ime_path_check.py --root raw/enja15 --out results/enja15_ime_path_check.json
    ENJA_MUTATE=keep_value python -I scripts/enja15_ime_path_check.py ...   # must FAIL (exit 1)
    (mutants: keep_value, category_from_value, drop_rows, duplicate_first; an empty --root must also FAIL)

Checks per session: (1) every R3j row has exactly the keys time, type and category; (2) time is an int, type is in
TYPES and category in R3J_CATEGORIES (closed lists, so no value can carry a string of the log); (3) no R3j value
is non-ASCII, equals a string of the session's attributes other than Time and Type (strings of two or more
characters, and every non-ASCII string), or contains one of its non-ASCII strings.
"""
import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import enja15  # noqa: E402

MUTATE = os.environ.get("ENJA_MUTATE", "")


def r3j(events):
    rows = enja15.r3j(events)
    if MUTATE == "keep_value":
        for row, (_, _, a) in zip(rows, events):
            row["value"] = a.get("Value")
    if MUTATE == "drop_rows":
        rows = []
    if MUTATE == "duplicate_first" and rows:
        rows = [dict(rows[0]) for _ in rows]
    if MUTATE == "category_from_value":
        for row, (_, _, a) in zip(rows, events):
            if row["category"] in ("commit", "commit_punct"):
                row["category"] = a.get("Value")
    return rows


def check_session(path):
    ev = enja15.key_events(path)
    rows = r3j(ev)
    c = Counter()
    strings = set()
    for _, _, a in ev:
        for k, v in a.items():
            if k in ("Time", "Type") or v is None:
                continue
            if len(v) >= 2 or not v.isascii():
                strings.add(v)
    # what the session contains (the records the check must cover)
    vals = [(t, a.get("Value") or "") for _, t, a in ev]
    c["has_composition_update"] = int(any(t == "IME" and enja15.LETTER_KEY.match(v) for t, v in vals))
    c["has_conversion"] = int(any(t == "IME" and v in enja15.CONVERT_KEYS for t, v in vals))
    c["has_cancel_escape_or_back_after_convert"] = int(any(
        t == "IME" and v in ("[Escape]", "[Back]") and any(
            t2 == "IME" and v2 in enja15.CONVERT_KEYS for t2, v2 in vals[max(0, i - 3):i])
        for i, (t, v) in enumerate(vals)))
    c["has_commit"] = int(any(t == "insert" and v and not (len(v) == 1 and v.isascii()) for t, v in vals))
    c["has_imetext"] = int(any("IMEtext" in a for _, _, a in ev))
    c["has_text_attribute"] = int(any("Text" in a for _, _, a in ev))
    for row in rows:
        if set(row) != {"time", "type", "category"}:
            c["fail_keys"] += 1
        if not isinstance(row.get("time"), int) or row.get("type") not in enja15.TYPES \
                or row.get("category") not in enja15.R3J_CATEGORIES:
            c["fail_closed_vocabulary"] += 1
        for k, v in row.items():
            # equality with any string; containment only for non-ASCII strings (an ASCII romaji such as "mi" is
            # a substring of the category name "commit" by accident)
            if isinstance(v, str) and (not v.isascii() or any(v == s or (not s.isascii() and s in v)
                                                                for s in strings)):
                c["fail_string_remains"] += 1
    c["rows"] = len(rows)
    c["key_events"] = len(ev)
    if len(rows) != len(ev):
        c["fail_rows_differ_from_key_events"] += 1
    # each row is the R3j of its own Key event: the same time and Type, and the category of that event
    for row, (tm, t, a) in zip(rows, ev):
        if row.get("time") != tm or row.get("type") != t or row.get("category") != enja15.category(t, a):
            c["fail_row_not_its_event"] += 1
    for row in rows:
        c["category " + str(row.get("category")) if row.get("category") in enja15.R3J_CATEGORIES else "category <not in list>"] += 1
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    d = os.path.join(args.root, "Translog-II")
    tot, sessions = Counter(), 0
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".xml"):
            tot.update(check_session(os.path.join(d, fn)))
            sessions += 1
    # the check must not pass vacuously (review): sessions exist, every Key event gives one R3j row, and the paths
    # the check is about (composition update, conversion, cancel, commit, IMEtext, Text) occur
    if sessions == 0:
        tot["fail_no_session"] += 1
    if tot["rows"] == 0:
        tot["fail_no_row"] += 1
    for k in ("has_composition_update", "has_conversion", "has_cancel_escape_or_back_after_convert", "has_commit",
              "has_imetext", "has_text_attribute"):
        if tot[k] == 0:
            tot["fail_path_absent_" + k] += 1
    fails = {k: v for k, v in tot.items() if k.startswith("fail")}
    out = {"sessions": sessions, "mutate": MUTATE or None, "pass": not fails, "fails": fails,
           "counts": dict(sorted(tot.items()))}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("PASS" if not fails else "FAIL %s" % fails)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
