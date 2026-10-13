"""Self-test of the exploratory analyses (decisions 55 and 56): the unicity of word-length windows and R-DP(eps).
Synthetic data only (no human data).

    python -I scripts/selftest_exploratory.py                                  # PASS
    UNI_MUTATE=<m> python -I scripts/selftest_exploratory.py                    # count_self, first_starts: FAIL
    MAIN_MUTATE=<m> python -I scripts/selftest_exploratory.py                   # dp_no_count_noise,
        dp_no_interval_noise, dp_plain_table: FAIL
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus  # noqa: E402
import matching  # noqa: E402,F401
import dp  # noqa: E402
import evaluate  # noqa: E402
import exploratory_unicity as U  # noqa: E402
import forms  # noqa: E402
from synthetic_logs import record_segments  # noqa: E402

FAIL = []
SEED = "selftest-exploratory"


def check(name, cond):
    if not cond:
        FAIL.append(name)
        print("FAIL", name)


# --- unicity ------------------------------------------------------------------------------------------------------

def test_index():
    g = np.random.default_rng(1)
    pool = [list(g.integers(1, 4, int(g.integers(5, 30)))) for _ in range(25)]
    ok = True
    for k in (1, 2, 3, 5):
        idx = U.pool_index(pool, k)
        for j, lens in enumerate(pool):
            h1, h2 = U._hashes(lens, k)
            for s in range(len(lens) - k + 1):
                want = sorted({o for o, t in enumerate(pool)
                               if any(t[i:i + k] == lens[s:s + k] for i in range(len(t) - k + 1))})
                ok &= sorted(U.owners_of(idx, h1[s], h2[s]).tolist()) == want
    check("owners equal brute force", ok)


def test_values():
    ids = ["w%02d" % i for i in range(12)]
    same = [[3, 1, 4, 1, 5, 9, 2, 6]] * 12
    _, out = U.prompt_values((SEED, "P", ids, same, [1, 3]))
    v = out["w00"][(3, 10)]
    check("identical texts: never unique", v[0] == 0.0)
    check("identical texts: credit 1/N", abs(v[1] - 0.1) < 1e-12)
    distinct = [[1000 * i + t for t in range(8)] for i in range(12)]
    _, out = U.prompt_values((SEED, "P", ids, distinct, [1, 3]))
    check("distinct texts: unique", out["w03"][(1, 10)] == (1.0, 1.0))
    # one decoy shares only the second half of w00's text: windows at the start are unique, later ones are not
    mixed = [list(range(100, 140))] + [[1000 * i + t for t in range(40)] for i in range(1, 12)]
    mixed[1] = [50000 + t for t in range(20)] + list(range(120, 140))
    _, out = U.prompt_values((SEED, "P", ids, mixed, [5]))
    starts = U.window_starts(SEED, "P", "w00", 5, 36)
    want = np.mean([1.0 if s < 20 else 0.0 for s in starts])
    # unique is 1 - (share of starts inside the shared half) * (share of draws whose decoys hold w01)
    held = np.mean([1 in U.matching.draw_decoys(SEED, "P", "w00", 10, ids, {0}, d)[0] for d in range(20)])
    exp = 1 - (1 - want) * held
    check("partial overlap", abs(out["w00"][(5, 10)][0] - exp) < 1e-12)
    check("starts are drawn", U.window_starts(SEED, "P", "w00", 5, 36) != list(range(5)))
    e = U.entropies([[1, 2] * 50])
    check("entropy order 0", abs(e["h0"] - 1.0) < 1e-12)
    check("entropy order 1", abs(e["h1"]) < 1e-12)


# --- R-DP -----------------------------------------------------------------------------------------------------------

def rec():
    w = corpus.synthetic_corpus(SEED, prompts=1, per_prompt=1, tag="dp")[0]
    return corpus.active_rows(w.rows)


def test_dp():
    rows = rec()
    r3 = forms.release(rows, "R3", SEED, "P", "w")
    big, origin = dp.release(r3.rows, 1e9, np.random.default_rng(0))
    merged = ["letter" if r["down_event"] == "digit" else r["down_event"] for r in r3.rows]
    check("large eps keeps the categories (digits as letters)", [r["down_event"] for r in big] == merged)
    check("synthetic record has digits", "digit" in [r["down_event"] for r in r3.rows])
    check("no digit category in R-DP", "digit" not in [r["down_event"] for r in big])
    check("large eps origin is the identity", origin == list(range(len(r3.rows))))
    t = [r["down_time"] for r in r3.rows]
    clip = [t[0]] + list(t[0] + np.cumsum(np.minimum(np.diff(t), dp.CAP)))
    check("large eps clips the intervals", np.allclose([r["down_time"] for r in big], clip))
    g = np.random.default_rng(5)
    z = dp.two_sided_geometric(g, np.exp(-1.0), 200000)
    check("geometric mean 0", abs(z.mean()) < 0.02)
    check("geometric P(0)", abs(np.mean(z == 0) - (1 - np.exp(-1)) / (1 + np.exp(-1))) < 0.005)
    small, origin = dp.release(r3.rows, 0.5, np.random.default_rng(1))
    cats0 = ["letter" if r["down_event"] == "digit" else r["down_event"] for r in r3.rows]
    cats1 = [r["down_event"] for r in small]
    check("count noise changes the letters", [c for c in cats0 if c == "letter"] != [c for c in cats1 if c == "letter"])
    check("other rows kept in order", [c for c in cats0 if c not in ("letter", "digit")] ==
          [c for c in cats1 if c not in ("letter", "digit")])
    check("segments as many", len(record_segments(cats0)) == len(record_segments(cats1)))
    check("origin non-decreasing", all(a <= b for a, b in zip(origin, origin[1:])))
    times = [r["down_time"] for r in small]
    check("times non-decreasing", all(a <= b for a, b in zip(times, times[1:])))
    d = np.diff(times)
    check("interval noise", np.mean(d == np.minimum(d, dp.CAP).round()) < 0.9 and np.mean(d == 0) > 0.01)
    rel = forms.release(rows, "R-DP(1)", SEED, "P", "w")
    check("released form", rel.base == "R-DP" and rel.p == 1.0 and len(rel.origin) == len(rel.rows))
    win = evaluate.window_release(rel, (10, 60), (0, 0))
    check("window by origin", [r["event_id"] for r in win.rows] ==
          [r["event_id"] for r, o in zip(rel.rows, rel.origin) if 10 <= o <= 60])
    model = {"digraph": "plain", "digraph_dp": {1.0: "dp"}}
    check("A3 table of R-DP", evaluate.a3_table(model, rel) == "dp")
    check("A3 table of R3", evaluate.a3_table(model, forms.release(rows, "R3", SEED, "P", "w")) == "plain")


def main():
    test_index()
    test_values()
    test_dp()
    print("FAIL" if FAIL else "PASS", len(FAIL))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
