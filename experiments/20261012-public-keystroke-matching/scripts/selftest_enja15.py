"""Self-test of the ENJA15 computation on synthetic sessions (no human data).

    python -I scripts/selftest_enja15.py            # PASS
    ENJA_MUTATE=<mutant> python -I scripts/selftest_enja15.py   # each mutant must FAIL
    mutants: a2_window_end, decoys_include_true, pool_records
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import enja15  # noqa: E402
import enja15_main as M  # noqa: E402

FAIL = []


def check(name, cond):
    if not cond:
        FAIL.append(name)
        print("FAIL", name)


def rows_of(values, t0=0):
    """R3j-like rows whose record segments are `values` (letters, a BackSpace when negative, a closing commit)."""
    rows, t = [], t0
    for v in values:
        for _ in range(max(v, 0)):
            rows.append({"time": t, "type": "IME", "category": "letter"})
            t += 100
        for _ in range(max(-v, 0)):
            rows.append({"time": t, "type": "IME", "category": "backspace"})
            t += 100
        rows.append({"time": t, "type": "insert", "category": "commit_punct"})
        t += 100
    return rows


def test_rules():
    rows = [{"category": c, "time": 0, "type": "IME"} for c in
            ["letter", "letter", "backspace", "convert", "commit", "commit_punct", "commit_punct", "navigation",
             "letter", "other"]]
    check("record_segments", enja15.record_segments(rows) == [1, 0, 1])
    check("a0_record", enja15.a0_record(rows) == 2)
    check("r3j_t", [r["time"] for r in enja15.r3j_t([{"time": 1234, "category": "x"}], 100)] == [1200])
    st = {}
    r = enja15.Reader()
    check("text_segments", enja15.text_segments("かな。カナ\n\nabc、　\nいった", r, st) == [4, 4, 3, 4])


def corpus(n_src=2, per_src=12, same_text=False, extend=False, seed=0):
    g = np.random.default_rng(seed)
    out = []
    for s in range(n_src):
        for i in range(per_src):
            vals = [int(x) for x in g.permutation([3, 5, 8, 12, 17, 21, 26, 29])]  # same sum: A0 at chance
            if same_text:
                vals = [10] * 8
            text = list(vals)
            out.append(M.Session("P%02d_T%d" % (i, s + 1), "%02d" % i, str(s + 1), rows_of(vals), text))
    if extend:  # a session whose text is another's text with extra segments (window end would tie them)
        base = out[0]
        out.append(M.Session("P90_T1", "90", "1", rows_of(base.text_values + [7, 7, 7]), base.text_values + [7, 7, 7]))
    return out


def main():
    seed = "selftest-enja15"
    test_rules()
    res = M.run(corpus(extend=True), seed)
    c = res["cells"]
    check("perfect A2 all", abs(c["R3j|A2|all"]["acc"] - 1.0) < 1e-12)
    check("perfect A2 N10", abs(c["R3j|A2|10"]["acc"] - 1.0) < 1e-12)
    check("same costs R0j R3j", c["R0j|A2|all"]["acc"] == c["R3j|A2|all"]["acc"] and
          c["R3j-t(1000)|A0|10"]["acc"] == c["R3j|A0|10"]["acc"])
    check("exceeds perfect", c["R3j|A2|all"]["exceeds"] is True)
    check("ci contains point", c["R3j|A0|all"]["ci"][0] - 1e-12 <= c["R3j|A0|all"]["acc"] <= c["R3j|A0|all"]["ci"][1] + 1e-12)
    res2 = M.run(corpus(same_text=True), seed)
    c2 = res2["cells"]
    for k in ("all", 10):
        e = c2["R3j|A2|%s" % k]
        check("no information = chance %s" % k, abs(e["acc"] - e["chance"]) < 1e-12)
        check("no information not exceeding %s" % k, e["exceeds"] is False)
    # unequal source sizes: the source-level mean differs from the pooled mean
    sess = corpus(n_src=1, per_src=12, seed=3) + corpus(n_src=1, per_src=24, same_text=True, seed=4)
    for s in sess[12:]:
        s.source, s.name = "9", s.name.replace("_T1", "_T9")
    res3 = M.run(sess, seed)
    e = res3["cells"]["R3j|A2|all"]
    check("source-level mean", abs(e["acc"] - (1.0 + 1.0 / 24) / 2) < 1e-9)
    check("reproducible", M.run(corpus(), seed) == M.run(corpus(), seed))
    print("FAIL" if FAIL else "PASS", len(FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
