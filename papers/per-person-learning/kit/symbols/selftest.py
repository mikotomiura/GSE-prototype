"""Self-test of the symbolization kit. Run: python3 selftest.py

Checks the adapters and the symbolizer on small hand-made inputs, checks that the stored
synthetic inputs are regenerated exactly from their seed, and runs the conformance check.
"""
import gzip
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from symbolizer import grid_symbol, load_constants, symbolize, with_releases  # noqa: E402
from adapters import coauthor, cs1_2021  # noqa: E402
from adapters.categories import char_category  # noqa: E402

C = load_constants()


def test_releases():
    ev = with_releases([(1000, "alphabetic"), (1000, "alphabetic"), (1050, "space"), (2000, "alphabetic")], 100)
    rel = [t for t, p, _ in ev if not p]
    assert rel == [1000, 1049, 1150, 2100], rel


def test_grid():
    assert grid_symbol(1.0, 1.0, C) == 24
    assert grid_symbol(0.0, 0.0, C) == 0
    assert grid_symbol(0.19999999999999998, 0.2, C) == 1
    assert grid_symbol(0.2, 0.0, C) == 5


def test_categories():
    cases = {"a": "alphabetic", "é": "alphabetic", "7": "numeric", "٣": "numeric", " ": "space",
             "\n": "enter", "\t": "tab", ".": "sentence_punctuation", ",": "sentence_punctuation",
             ";": "punctuation", "€": "other"}
    for ch, cat in cases.items():
        assert char_category(ch) == cat, (ch, char_category(ch))


def test_coauthor_adapter():
    rows = [
        {"eventTimestamp": 900, "eventNum": 0, "eventName": "system-initialize", "eventSource": "api", "textDelta": ""},
        {"eventTimestamp": 1000, "eventNum": 1, "eventName": "text-insert", "eventSource": "user",
         "textDelta": {"ops": [{"retain": 3}, {"insert": "a"}]}},
        {"eventTimestamp": 1100, "eventNum": 2, "eventName": "text-insert", "eventSource": "user",
         "textDelta": {"ops": [{"insert": "ab"}]}},
        {"eventTimestamp": 1200, "eventNum": 3, "eventName": "text-insert", "eventSource": "api",
         "textDelta": {"ops": [{"insert": "c"}]}},
        {"eventTimestamp": 1300, "eventNum": 4, "eventName": "suggestion-get", "eventSource": "user", "textDelta": ""},
        {"eventTimestamp": 1400, "eventNum": 5, "eventName": "text-delete", "eventSource": "user", "textDelta": ""},
        {"eventTimestamp": 1500, "eventNum": 6, "eventName": "cursor-forward", "eventSource": "user", "textDelta": ""},
    ]
    t0, presses = coauthor.presses_from_rows(rows[::-1])
    assert t0 == 900
    assert presses == [(1000, "alphabetic"), (1400, "backspace"), (1500, "navigation")], presses


def test_cs1_adapter():
    def row(t, eid, et, md="", edit="", ins=""):
        return {"ClientTimestamp": str(t) + ".7", "EventID": str(eid), "EventType": et, "X-Metadata": md,
                "EditType": edit, "InsertText": ins}
    gap = cs1_2021.BLOCK_GAP_MS
    rows = [row(1000, 1, "X-Keystroke", "a"), row(1100, 2, "X-Action", "Backspace"),
            row(1100 + gap, 3, "X-Keystroke", "b"),
            row(1100 + 2 * gap, 4, "X-Keystroke", "c"), row(1200 + 2 * gap, 5, "X-Action", "Left"),
            row(1300 + 2 * gap, 6, "X-Keystroke", "ab")]
    blocks = cs1_2021.blocks_from_rows(rows)
    assert blocks == [(1000, [(1000, "alphabetic"), (1100, "backspace")]),
                      (1100 + 2 * gap, [(1100 + 2 * gap, "alphabetic"), (1200 + 2 * gap, "navigation")])], blocks


def test_ticks_before_first_press():
    rows = symbolize(0, [(5000, "alphabetic"), (5200, "alphabetic")], C)
    assert [r[0] for r in rows[:3]] == [2000, 3000, 4000], rows[:3]
    assert all(r[5] == "silence" for r in rows[:3])


def test_run_symbol():
    presses = [(1000 + 150 * i, "alphabetic") for i in range(5)]
    presses += [(2000 + 120 * i, "backspace") for i in range(14)]
    presses += [(3800, "alphabetic"), (3950, "alphabetic")]
    rows = symbolize(1000, presses, C)
    assert any(r[3] == C["backspace_run_symbol"] for r in rows), [r[3] for r in rows]


def test_edge_inputs():
    assert symbolize(0, [], C) == []
    one = symbolize(0, [(5000, "alphabetic")], C)
    assert one and all(r[5] == "silence" for r in one) and one[0][0] == 2000, one[:2]
    ties = symbolize(0, [(1000, "alphabetic")] * 50 + [(1500, "space")], C)
    assert all(0 <= r[3] <= 25 for r in ties)
    for bad in ([(1, "Alphabetic")], [(2000, "alphabetic"), (1000, "alphabetic")]):
        try:
            symbolize(0, bad, C)
        except ValueError:
            continue
        raise AssertionError("expected ValueError for %r" % (bad,))
    assert cs1_2021.classify({"EventType": "X-Keystroke", "X-Metadata": None}) == (None, None)


def test_branch_coverage():
    with gzip.open(os.path.join(HERE, "conformance", "data", "inputs.json.gz"), "rt", encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    paths, alphas, run_symbols, dense = set(), set(), 0, 0
    for t0, presses in cases:
        rows = symbolize(t0, [tuple(p) for p in presses], C)
        paths |= {r[5] for r in rows}
        alphas |= {r[4] for r in rows}
        run_symbols += sum(1 for r in rows if r[3] == C["backspace_run_symbol"])
        p = [t for t, cat in presses if t >= t0 and cat in C["key_categories"]["feature"]]
        if any(p[i + 300] - p[i] <= C["window_ms"] for i in range(len(p) - 300)):
            dense += 1
    assert paths == {"typing", "transition", "silence"}, paths
    assert alphas == {0.3, 0.15, 0.18, 0.25}, alphas
    assert run_symbols > 0 and dense > 0, (run_symbols, dense)
    print("   coverage: run-symbol rows %d, cases with buffer overflow inside the window %d" % (run_symbols, dense))


def test_check_rejects_count_mismatch():
    with tempfile.TemporaryDirectory() as td:
        empty = os.path.join(td, "e.json")
        with open(empty, "w") as f:
            json.dump({"expected": []}, f)
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "conformance", "check.py"),
                            os.path.join(HERE, "conformance", "data", "inputs.json.gz"), empty],
                           capture_output=True)
        assert r.returncode != 0


def test_regenerate_inputs():
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "inputs.json")
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "conformance", "generate_inputs.py"),
                        "20261107", "300", out], check=True)
        with open(out, encoding="utf-8") as f:
            regenerated = json.load(f)
    with gzip.open(os.path.join(HERE, "conformance", "data", "inputs.json.gz"), "rt", encoding="utf-8") as f:
        stored = json.load(f)
    assert regenerated == stored


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "conformance", "check.py")])
    if r.returncode != 0:
        sys.exit("conformance check failed")
    print("selftest ok")


if __name__ == "__main__":
    main()
