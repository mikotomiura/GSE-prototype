"""Self-test of the synthetic-log check (unit checks, then mutants that must make it fail). Reads no record.

python scripts/selftest_synthetic.py           -> unit checks and the mutants
python scripts/selftest_synthetic.py --units   -> unit checks only (what each mutant run executes)
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import align_ext  # noqa: E402
import synthetic_check as sc  # noqa: E402
from replay import a1_text, a1prime, lengths_of_items  # noqa: E402
from synthetic_logs import (DEFAULT_OPS, NO_OPS, R2_COLS, R3_COLS, Writer, category, form_R0, form_R1,  # noqa: E402
                            form_R2, form_R3, form_R7, record_segments, shortcut_flags, word_lengths)

FAILS = []
MUTANTS = ["r3_keep_position", "r3_keep_up_time", "twins_always_same", "full_as_window", "r7_default_groups"]


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


def test_config():
    cfg = sc.load_config()
    check("0.25" in cfg["alignment"]["r7_groups"], "config has R7 groups")
    try:
        json.loads('{"a": {"b": 1, "b": 2}}', object_pairs_hook=sc.no_dup)
        check(False, "a nested duplicate key is detected")
    except ValueError:
        pass
    check(json.loads('{"a": 1, "b": 2}', object_pairs_hook=sc.no_dup) == {"a": 1, "b": 2}, "no false duplicate")
    return cfg


def test_categories():
    exp = {"a": "letter", "Z": "letter", "7": "digit", "Space": "space", ",": "punctuation", "Backspace": "backspace",
           "Delete": "delete", "Enter": "enter", "ArrowUp": "navigation", "PageDown": "navigation",
           "ArrowLeft": "arrow_left", "ArrowRight": "arrow_right", "Home": "home", "End": "end", "Shift": "modifier",
           "Alt": "modifier", "CapsLock": "modifier", "Control": "control", "Meta": "control", "Leftclick": "mouse",
           "Unidentified": "other"}
    for k, v in exp.items():
        check(category(k) == v, "category %s -> %s (got %s)" % (k, v, category(k)))
    check(shortcut_flags(["control", "letter"]) == [False, True], "Control arms a shortcut")
    check(shortcut_flags(["modifier", "letter"]) == [False, False], "Shift does not arm")
    check(shortcut_flags(["control", "modifier", "letter", "letter"]) == [False, False, True, False],
          "Control+Shift+letter: only the next non-modifier press")
    check(shortcut_flags(["control", "arrow_left", "letter"]) == [False, False, False], "a navigation press disarms")
    cfg_cats = sc.load_config()["key_categories"]
    for k in exp.values():
        check(k in cfg_cats, "category %s is in config.json key_categories" % k)
    segs = [v for v, _ in record_segments(["letter", "letter", "space", "letter", "backspace", "letter", "punctuation"])]
    check(segs == [2, 1], "record segments: %r" % segs)
    check(word_lengths("Ab1 c, d-ef\n") == [3, 1, 1, 2], "text segments")


def test_forms():
    rec = Writer(1, 2, 3).run()
    check(a1_text(form_R0(rec)) == rec.final, "A1 rebuilds the final text from R0")
    check(set(form_R0(rec)[0]) >= {"pause_time", "activity", "text_change"}, "R0 keeps every column")
    check("pause_time" not in form_R1(rec)[0], "R1 drops the column not in the table")
    check(tuple(form_R2(rec)[0]) == R2_COLS, "R2 columns")
    check(tuple(form_R3(rec)[0]) == R3_COLS == ("event_id", "down_time", "down_event", "up_event"),
          "R3 columns: the press time only (decision 41)")
    check(a1prime(["letter", "letter", "arrow_left", "letter", "end", "space", "home", "digit"]) ==
          [("a", 7), ("a", 0), ("a", 3), ("a", 1), ("s", 5)], "A1' moves with arrows, Home and End")
    check(a1prime(["letter", "letter", "navigation", "letter"]) == [("a", 0), ("a", 1), ("a", 3)],
          "other navigation puts the cursor at the end")
    r7, keep = form_R7(rec, 0.5, np.random.default_rng(0))
    check([r["event_id"] for r in r7] == list(range(1, len(r7) + 1)) and len(r7) == int(keep.sum()), "R7 renumbers")
    clean = Writer(4, 5, 6, ops=NO_OPS).run()
    items = a1prime([category(r["down_event"]) for r in clean.rows])
    check(lengths_of_items(items) == word_lengths(clean.final), "A1' is exact without edits")
    # negative control: with edits A1' is not always exact (the exact-recovery measure is not always true)
    exact = 0
    for i in range(10):
        r = Writer(10 + i, 20 + i, 30 + i, ops=DEFAULT_OPS).run()
        exact += lengths_of_items(a1prime([category(x["down_event"]) for x in r.rows])) == \
            word_lengths(r.final)
    check(exact < 10, "A1' is not exact on every edited record (%d/10)" % exact)


def test_align(cfg):
    rng = np.random.default_rng(7)
    for _ in range(300):
        x = [int(v) for v in rng.integers(-1, 9, int(rng.integers(0, 7)))]
        y = [int(v) for v in rng.integers(0, 9, int(rng.integers(0, 9)))]
        try:
            tg = align_ext.T.align(x, y, 8)
        except ValueError:
            tg = None
        c, g = align_ext.free_end(x, y, 8, list(align_ext.T.ORDER))
        check(g == tg, "free-end recurrence = template on %r %r" % (x, y))
        cw, gw = align_ext.align(x, y, 8, "window")
        check(gw == tg, "window end calls the template on %r %r" % (x, y))
    c_w, g_w = align_ext.align([5], [5, 9], 8, "window")
    c_f, g_f = align_ext.align([5], [5, 9], 8, "full")
    check(c_w == 0 and g_w == [(0, 1, 0, 1)], "window end stops early")
    check(c_f == 17 and g_f == [(0, 1, 0, 2)], "full end uses the whole text (%r %r)" % (c_f, g_f))
    c, g = align_ext.align([1] * 7, [7], 8, "full")
    check(c == align_ext.INF and g is None, "no path -> infinity")
    check(align_ext.credit(0, [align_ext.INF] * 4) == (0.25, True, False), "all infinite -> tie among all")
    check(align_ext.credit(0, [align_ext.INF, 3, 4]) == (0.0, False, True), "only the true text infinite")
    check(align_ext.credit(1, [5, 3, 3]) == (0.5, False, False), "ties 1/m")
    groups, cap = align_ext.r7_groups(cfg, 0.25)
    check(cap == 4, "R7 cap 4 at p = 0.25")
    c, g = align_ext.align([20], [5, 5, 5, 5], 8, "full", groups=groups, max_group=cap)
    check(g == [(0, 1, 0, 4)], "a (1,4) group is chosen with the R7 groups (%r)" % (g,))
    c3, _ = align_ext.align([20], [5, 5, 5, 5], 8, "full")
    check(c3 == align_ext.INF, "the default groups cannot do it")
    groups, cap = align_ext.r7_groups(cfg, 0.5)
    c, g = align_ext.align([1] * 6, [6], 8, "window", groups=groups, max_group=cap)
    check(g == [(0, 6, 0, 1)], "a (6,1) group through the template with max_group 6 (%r)" % (g,))


def test_parts(cfg):
    tw = sc.part_twins(40, "free")
    s = tw["identical_output_share"]
    check(tw["different_final_word_lengths"] >= 10, "enough twins (%d)" % tw["different_final_word_lengths"])
    check(s["R0"] == 0.0 and s["R2"] == 0.0, "positive control: R0 and R2 tell twins apart (%r)" % s)
    for f in ("R3", "R3-u", "R3-t(100)", "R7(0.25)"):
        check(s[f] == 1.0, "%s gives identical output for twins (%r)" % (f, s[f]))
    s = sc.part_twins(40, "drag")["identical_output_share"]
    for f in ("R3", "R3-u", "R3-t(100)", "R7(0.25)"):
        check(s[f] == 1.0, "%s: a drag's length in the hold time does not reach the output (%r)" % (f, s[f]))
    r7 = sc.part_r7(15, cfg, NO_OPS, "selftest")
    check(r7["0.0"]["true_groups_above_cap_share"] == 0.0, "p = 0, no edits: true groups within the cap")
    check(r7["0.0"]["dp_minus_true_cost_per_word"]["median"] == 0.0, "p = 0, no edits: DP finds the true path cost")
    check(r7["0.5"]["dp_uses_group_of_4_or_more"] > 0, "groups of 4 or more are chosen at p = 0.5")
    a3 = sc.part_a3(30, 10, 19)
    check(a3["test_with_exact_replay"] >= 5, "A3: enough exact replays")
    check(a3["none"]["top1_mean_version"] > a3["delete_0.1"]["top1_mean_version"], "an early replay error hurts A3")


def units():
    cfg = test_config()
    test_categories()
    test_forms()
    test_align(cfg)
    test_parts(cfg)
    return not FAILS


def main(argv):
    ok = units()
    print("units:", "PASS" if ok else "FAIL (%d)" % len(FAILS))
    if "--units" in argv or not ok:
        return 0 if ok else 1
    survived = []
    for m in MUTANTS:
        env = dict(os.environ, SYNTH_MUTATE=m)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--units"], env=env, capture_output=True,
                           text=True)
        print("mutant %-20s -> %s" % (m, "killed" if r.returncode else "SURVIVED"))
        if not r.returncode:
            survived.append(m)
    if survived:
        print("FAIL: mutants survived:", survived)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
