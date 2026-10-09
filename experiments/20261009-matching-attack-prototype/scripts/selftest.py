"""Self-test (design.md section 9). Runs before the main computation; a failure stops run.sh.

  selftest.py

Reads no observation: the checks use synthetic worlds, hand-counted category sequences, the committed phrase
corpus and the IME paper's generator (to build synthetic trials).
"""
import math
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitload  # noqa: E402
import crosscheck  # noqa: E402
import distances  # noqa: E402
import matching  # noqa: E402
import prepare  # noqa: E402

FAILS = []
N_CHECKS = [0]


def check(name, cond, detail=""):
    N_CHECKS[0] += 1
    if not cond:
        FAILS.append(name)
        print("FAIL %s %s" % (name, detail))


def raises(name, fn, exc=Exception):
    try:
        fn()
    except exc:
        check(name, True)
        return
    check(name, False, "(no exception)")


# ---------------------------------------------------------------- 1. guards
def test_guards():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "x.txt")
        with open(p, "wb") as f:
            f.write(b"abc")
        check("sha256 of a file", kitload.sha256_file(p) ==
              "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    raises("a path outside the repository is refused", lambda: kitload.repo_path("../x"), kitload.CheckError)
    raises("an absolute path is refused", lambda: kitload.repo_path(os.path.abspath(os.sep)), kitload.CheckError)
    cfg = kitload.load_config()
    rel = "papers/ime-observation/kit/gen/romaji.py"
    raises("a code file with another SHA-256 stops the run", lambda: kitload.check_file(rel, "0" * 64),
           kitload.CheckError)
    check("the recorded SHA-256 of romaji.py is accepted", kitload.check_file(rel, cfg["code"][rel]) is not None)
    bad = dict(cfg)
    bad["code"] = dict(cfg["code"])
    bad["code"]["papers/ime-observation/kit/e2/closed_set.py"] = "0" * 64
    raises("import_kit refuses a changed kit file", lambda: kitload.import_kit(bad), kitload.CheckError)


# ---------------------------------------------------------------- 2-3. counting and segments
def test_counting():
    cfg = kitload.load_config()
    counted = frozenset(cfg["counted_categories"])
    minus = frozenset(cfg["minus_categories"])
    bounds = frozenset(cfg["boundary_categories"])
    a = "alphabetic"
    cats = [a] * 5 + ["punctuation"] + [a] * 3 + ["space", "space", "numeric", "enter"]
    check("key count: letters + minus + digit, Space and Enter not counted",
          prepare.key_count(cats, counted, minus) == 10)
    cats = [a] * 6 + ["backspace"] * 3
    check("key count: BackSpace subtracts", prepare.key_count(cats, counted, minus) == 3)
    check("key count: navigation, escape, tab not counted",
          prepare.key_count([a, "navigation", "escape", "tab", "modifier"], counted, minus) == 1)
    seg = crosscheck.record_segments
    check("segments: closed by Enter, no open segment", seg([a, a, "space", "enter"], counted, minus, bounds) ==
          ([2], None))
    check("segments: no boundary gives an open segment", seg([a, a, a, "space", "escape"], counted, minus,
                                                             bounds) == ([], 3))
    check("segments: two Enters give an empty closed segment", seg([a, "enter", "enter"], counted, minus,
                                                                   bounds) == ([1, 0], None))
    check("segments: presses after the last Enter are open", seg([a, "enter", a, a], counted, minus, bounds) ==
          ([1], 2))
    check("segments: a sentence-punctuation key is a boundary",
          seg([a, "sentence_punctuation", a], counted, minus, bounds) == ([1], 1))
    check("segments: an open segment of uncounted keys is 0, not None",
          seg([a, "enter", "space"], counted, minus, bounds) == ([1], 0))


# ---------------------------------------------------------------- 4. variants
def test_variants(kit):
    cs = kit.closed_set
    cfg = kitload.load_config()
    V = cfg["variants"]
    x = [10, 21, 5]
    rcols = [[12, 10], [20, 30], [5, 9]]      # two decoys
    rtrue = [10, 22, 6]
    check("L_none", matching.l_scores(V["L_none"], x, rcols, rtrue) == (2, [2 + 1 + 0, 0 + 9 + 4]))
    # bin 4: x -> 2, 5, 1; decoys (3, 5, 1) and (2, 7, 2); truth (2, 5, 1)
    check("L_bin4", matching.l_scores(V["L_bin4"], x, rcols, rtrue) == (0, [1, 3]))
    check("L_bininf: every score 0", matching.l_scores(V["L_bininf"], x, rcols, rtrue) == (0, [0, 0]))
    # merge 2: groups (0,1) and (2): x sums 31, 5; decoy sums (32, 5) and (40, 9); truth (32, 6)
    check("L_merge2", matching.l_scores(V["L_merge2"], x, rcols, rtrue) == (2, [1, 13]))
    check("L_mergeall", matching.l_scores(V["L_mergeall"], x, rcols, rtrue) == (2, [1, 13]))
    check("L_merge5 equals the total when k < 5", matching.l_scores(V["L_merge5"], x, rcols, rtrue) == (2, [1, 13]))
    # sort: x sorted (5, 10, 21); decoy 1 (12, 20, 5) -> (5, 12, 20): 0+2+1; decoy 2 (10, 30, 9) -> (9, 10, 30): 4+0+9;
    # truth (10, 22, 6) -> (6, 10, 22): 1+0+1
    check("L_sort", matching.l_scores(V["L_sort"], x, rcols, rtrue) == (2, [3, 13]))
    check("L_sort ignores the order", matching.l_scores(V["L_sort"], [21, 5, 10], rcols, rtrue)[1] == [3, 13])
    toks = (("alphabetic", 1, 0),) * 3 + (("punctuation", 1, 0), ("alphabetic", 1, 0), ("space", 1, 0),
                                          ("space", 1, 0), ("enter", 1, 0))
    check("rle w=1", distances.rle(toks, 1) == (("alphabetic", 3, 0), ("punctuation", 1, 0), ("alphabetic", 1, 0),
                                                 ("space", 2, 0), ("enter", 1, 0)))
    check("rle w=2 rounds up", distances.rle(toks, 2) == (("alphabetic", 2, 0), ("punctuation", 1, 0),
                                                           ("alphabetic", 1, 0), ("space", 1, 0), ("enter", 1, 0)))
    check("rle w=inf keeps only the runs", distances.rle(toks, None) == (
        ("alphabetic", 1, 0), ("punctuation", 1, 0), ("alphabetic", 1, 0), ("space", 1, 0), ("enter", 1, 0)))
    g = V["S_mboth"]["groups"]
    check("merge categories", distances.rename(toks, g)[3] == ("char", 1, 0) and
          distances.rename(toks, g)[-1] == ("bound", 1, 0) and distances.rename(toks, g)[0] == ("char", 1, 0))

    def ev(n):
        return [(i * 100, "alphabetic") for i in range(n)] + [(n * 100, "space"), (n * 100 + 100, "enter")]
    d = {}
    for name in ("S_no_time", "S_counts_only", "S_rle1", "S_rle4", "S_rleinf", "S_mchar"):
        a = distances.obs_tokens(kit, ev(10), V[name])
        b = distances.obs_tokens(kit, ev(20), V[name])
        d[name] = cs._distance(a, b, "none")
    check("no_time keeps the run length", d["S_no_time"] == 10)
    check("counts_only keeps the run length (the IME paper's set)", d["S_counts_only"] == 10, str(d))
    check("rle w=1 keeps the run length", d["S_rle1"] == 10)
    check("rle w=4 coarsens it (3 vs 5)", d["S_rle4"] == 2)
    check("rle w=inf removes it", d["S_rleinf"] == 0)
    check("merging the text keys keeps the count of keys", d["S_mchar"] == 10)
    bs = [(i * 100, "alphabetic") for i in range(10)] + [(1000 + i * 100, "backspace") for i in range(5)]
    bs2 = [(i * 100, "alphabetic") for i in range(10)] + [(1000 + i * 100, "backspace") for i in range(9)]
    check("rle w=inf removes the BackSpace count too", cs._distance(
        distances.obs_tokens(kit, bs, V["S_rleinf"]), distances.obs_tokens(kit, bs2, V["S_rleinf"]), "none") == 0)
    check("counts_only keeps the BackSpace count", cs._distance(
        distances.obs_tokens(kit, bs, V["S_counts_only"]), distances.obs_tokens(kit, bs2, V["S_counts_only"]),
        "none") == 4)


def test_distance_matches_attack(kit):
    """distances.py's tokens and _distance give the distances closed_set.attack gives (no_time, counts_only)."""
    cs, gp = kit.closed_set, kit.generate_plan
    cfg = kitload.load_config()
    corpus, recipes, pcfg = kitload.load_inputs(cfg, kit)
    rng = random.Random(5)
    phrases = [corpus[rng.randrange(len(corpus))] for _ in range(12)]
    pred = cs.Predictor(recipes, pcfg, "windows", cfg["attacker_seed"])
    ok = True
    for sc in ("S1", "S6", "S8", "S10", "S2", "S7"):
        for speed in ("slow", "fast"):
            true = phrases[rng.randrange(len(phrases))]
            row = gp.build_trial(true, sc, speed, "windows", recipes, pcfg, gp.trial_rng(99, sc + speed), "t00001", 0)
            observed = kit.simulate_obs.simulate(row, kit.simulate_obs.KEYCAT)
            for f, name in (("no_time", "S_no_time"), ("counts_only", "S_counts_only")):
                r = cs.attack(observed, phrases, sc, "windows", recipes, pcfg, f, cfg["attacker_seed"], speed=speed)
                ot = distances.obs_tokens(kit, [list(e) for e in observed], cfg["variants"][name])
                mine = [cs._distance(ot, distances.pred_tokens(pred, p, sc, speed, cfg["variants"][name]), "none")
                        for p in phrases]
                if mine != r["distances"]:
                    ok = False
    check("per-trial distances equal closed_set.attack's (6 scenarios x 2 speeds x 2 sets)", ok)


# ---------------------------------------------------------------- 5. scoring
def test_credit():
    check("credit: truth alone closest", matching.credit(1, [2, 3, 5]) == 1.0)
    check("credit: truth farther", matching.credit(4, [2, 3, 5]) == 0.0)
    check("credit: tie of 3 including the truth", matching.credit(2, [2, 2, 5]) == 1.0 / 3)
    check("credit: every candidate equal gives 1/N", matching.credit(0, [0] * 9) == 0.1)


# ---------------------------------------------------------------- 6. sampler (synthetic world)
def synthetic_world(n_blocks, per_block, scenarios, pool_n, seed):
    rng = random.Random(seed)
    R = [rng.randint(10, 60) for _ in range(pool_n)]
    typed = dict((s, ["r%d" % j if s != "half" else "h%d" % (j // 2) for j in range(pool_n)]) for s in scenarios)
    trials = []
    for b in range(n_blocks):
        for i in range(per_block):
            s = scenarios[rng.randrange(len(scenarios))]
            j = rng.randrange(pool_n)
            trials.append({"block_id": b, "scenario": s, "j": j, "typed": typed[s][j], "c": R[j]})
    return trials, R, typed


def run_synthetic(trials, R, typed, k, N, informative, seed):
    wins = matching.windows_of(trials, k)
    total = 0.0
    n = 0
    for b, st, tids in wins:
        rng = random.Random(kitload.seed_int(seed, "test", k, N, b, st))
        scs = [trials[t]["scenario"] for t in tids]
        decoys, _ = matching.draw_decoys(rng, N, [len(R)] * k, [typed[s] for s in scs],
                                         [trials[t]["typed"] for t in tids])
        jcols = [list(c) for c in zip(*decoys)]
        rcols = [[R[j] for j in col] for col in jcols]
        rtrue = [R[trials[t]["j"]] for t in tids]
        if informative:
            x = [trials[t]["c"] for t in tids]
        else:
            x = [random.Random(kitload.seed_int(seed, "noise", b, st, i)).randint(10, 60) for i in range(k)]
        ts, sc = matching.l_scores({"kind": "none"}, x, rcols, rtrue)
        total += matching.credit(ts, sc)
        n += 1
    return total / n, n


def test_sampler():
    trials, R, typed = synthetic_world(40, 12, ["a", "b", "half"], 300, 1)
    for k in (1, 2, 3):
        wins = matching.windows_of(trials, k)
        check("windows: count k=%d" % k, len(wins) == 40 * (12 - k + 1))
        check("windows: no window crosses a block (k=%d)" % k,
              all(len(set(trials[t]["block_id"] for t in tids)) == 1 for _, _, tids in wins))
    for k, N in ((1, 10), (1, 100), (2, 10), (3, 10), (2, 100)):
        acc, n = run_synthetic(trials, R, typed, k, N, False, 7)
        se = math.sqrt((1.0 / N) * (1 - 1.0 / N) / n)
        check("uninformative record gives about 1/N (k=%d N=%d)" % (k, N), abs(acc - 1.0 / N) <= 3 * se + 1e-9,
              "%.4f vs %.4f (se %.4f)" % (acc, 1.0 / N, se))
    acc, _ = run_synthetic(trials, R, typed, 3, 10, True, 7)
    check("an exact record of 3 trials is nearly always found", acc > 0.95, "%.4f" % acc)
    rng = random.Random(3)
    tt = ["r1", "r2"]
    decoys, _ = matching.draw_decoys(rng, 200, [300, 300], [typed["a"], typed["a"]], tt)
    check("decoys: N - 1 of them", len(decoys) == 199)
    check("decoys: distinct", len(set(decoys)) == 199)
    check("decoys: none types the truth at every position",
          all(not (typed["a"][d[0]] == tt[0] and typed["a"][d[1]] == tt[1]) for d in decoys))
    d1, _ = matching.draw_decoys(random.Random(3), 50, [300], [typed["half"]], ["h4"])
    check("decoys k=1: distinct phrases", len(set(d1)) == 49)
    check("decoys k=1: none types the truth's reading (half readings collide)",
          all(typed["half"][d[0]] != "h4" for d in d1))
    d2, _ = matching.draw_decoys(random.Random(3), 50, [300], [typed["half"]], ["h4"])
    check("decoys: the same seed gives the same decoys", d1 == d2)
    raises("decoys k=1: too few distinct readings stop", lambda: matching.draw_decoys(
        random.Random(1), 400, [300], [typed["a"]], ["r1"]), ValueError)
    # small pools, where a missing exclusion would show at once
    small = ["p0", "p1", "p2"]
    others = sorted((a, b) for a in range(3) for b in range(3) if (a, b) != (1, 1))
    bad = [sd for sd in range(20)
           if sorted(matching.draw_decoys(random.Random(sd), 9, [3, 3], [small, small], ["p1", "p1"])[0]) != others]
    check("decoys k=2, 3 x 3 tuples: the 8 tuples other than the truth's, each once (20 seeds)", not bad, str(bad))
    halves = ["q0", "q0", "q1", "q1", "q2", "q2", "q3", "q3", "q4", "q4"]
    d4, _ = matching.draw_decoys(random.Random(4), 9, [10], [halves], ["q2"])
    check("decoys k=1, two phrases share the truth's typed reading: the other 8 phrases",
          sorted(d4) == [(j,) for j in range(10) if j not in (4, 5)], str(sorted(d4)))
    raises("decoys k=1: one more than the phrases with another typed reading stops", lambda: matching.draw_decoys(
        random.Random(4), 10, [10], [halves], ["q2"]), ValueError)
    d5, nre = matching.draw_decoys(random.Random(4), 9, [3, 3], [small, small], ["p1", "p1"])
    check("decoys: redraws are counted", nre > 0)
    # a truth drawn from a different law than the decoys would move the uninformative accuracy away from 1/N; the
    # record-independent "typical" choice must stay near 1/N when truth and decoys come from the same law
    total = 0.0
    n = 0
    med = sorted(R)[len(R) // 2]
    for b, st, tids in matching.windows_of(trials, 1):
        rng = random.Random(kitload.seed_int(9, b, st))
        decoys, _ = matching.draw_decoys(rng, 10, [len(R)], [typed[trials[tids[0]]["scenario"]]],
                                         [trials[tids[0]]["typed"]])
        sc = [abs(R[d[0]] - med) for d in decoys]
        total += matching.credit(abs(R[trials[tids[0]]["j"]] - med), sc)
        n += 1
    se = math.sqrt(0.1 * 0.9 / n)
    check("record-independent choice gives about 1/N", abs(total / n - 0.1) <= 3 * se + 1e-9, "%.4f" % (total / n))


# ---------------------------------------------------------------- 7. swap
def test_swap():
    trials = [{"block_id": b, "scenario": s} for b in range(5) for s in ("x", "y")]
    same = [i for i, t in enumerate(trials) if t["scenario"] == "x"]
    rng = random.Random(1)
    picks = [matching.pick_swap(rng, same, trials, 2) for _ in range(200)]
    check("swap: always another block", all(trials[u]["block_id"] != 2 for u in picks))
    check("swap: always the same scenario", all(trials[u]["scenario"] == "x" for u in picks))
    check("swap: every other block is used", len(set(trials[u]["block_id"] for u in picks)) == 4)
    raises("swap: no trial outside the block stops", lambda: matching.pick_swap(
        rng, [0], [{"block_id": 0, "scenario": "x"}], 0), ValueError)


# ---------------------------------------------------------------- 8. bootstrap
def test_bootstrap():
    m1 = matching.boot_multiplicities(1, 5, 50)
    m2 = matching.boot_multiplicities(1, 5, 50)
    check("bootstrap: same seed, same resamples", m1 == m2)
    check("bootstrap: each resample draws every block count once", all(sum(m) == 5 for m in m1))
    s = matching.summarise([1.0, 0.0, 1.0], [7, 7, 7], {7: 0, 8: 1}, matching.boot_multiplicities(1, 2, 50), 0.1,
                           0.95)
    check("bootstrap: one block gives no interval", s["ci"] == [None, None] and s["ci_status"] ==
          "fewer_than_two_blocks")
    s = matching.summarise([1.0, 0.0, 1.0, 0.0], [7, 7, 8, 8], {7: 0, 8: 1}, matching.boot_multiplicities(1, 2, 400),
                           0.1, 0.95)
    check("bootstrap: acc and its interval", s["acc"] == 0.5 and s["ci"][0] <= 0.5 <= s["ci"][1])
    check("bootstrap: excess and ratio", abs(s["excess"] - 0.4) < 1e-12 and abs(s["ratio"] - 5.0) < 1e-12)


# ---------------------------------------------------------------- 9. tables
def test_tables(kit):
    cfg = kitload.load_config()
    corpus, _, _ = kitload.load_inputs(cfg, kit)
    rt, romaji = kit.romaji_table, kit.romaji
    bad = sum(1 for p in corpus if rt.count_keys(p["reading"]) != len(romaji.to_keys(p["reading"])))
    check("the previous task's table and romaji.to_keys agree on every corpus reading", bad == 0, str(bad))
    check("every key of a romaji reading is counted (letters or minus)",
          all(k in "abcdefghijklmnopqrstuvwxyz" or k == "minus" for p in corpus for k in romaji.to_keys(p["reading"])))


def main():
    cfg = kitload.load_config()
    kit = kitload.import_kit(cfg, prior=True)
    test_guards()
    test_counting()
    test_variants(kit)
    test_distance_matches_attack(kit)
    test_credit()
    test_sampler()
    test_swap()
    test_bootstrap()
    test_tables(kit)
    print("selftest: %d checks, %d failed" % (N_CHECKS[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
