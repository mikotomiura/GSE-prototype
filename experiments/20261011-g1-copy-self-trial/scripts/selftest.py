"""Self-test (run.sh runs it before anything else; a failure stops the run). Reads no record."""
import copy as copymod
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matching  # noqa: E402
from align import align, start_map  # noqa: E402
from common import REPO, assert_private_dir, check_inputs, corpus_build_key, load_config, repo_path, write_json  # noqa: E402
from g1rule import G1Rule, copy_lines  # noqa: E402
from records import segments  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


def test_rule(cfg):
    r = G1Rule(cfg)
    rt = r.rt
    check(r.token_items("、", "、") == [("B", None)], "comma is a boundary")
    check(r.token_items("。", "。") == [("B", None)], "period is a boundary")
    check(r.token_items("ー", "ー") == [("B", None)], "a lone long-vowel mark is a boundary")
    check(r.token_items("・", "・") == [("B", None)], "middle dot is a boundary")
    check(r.token_items("「", "「") == [("B", None)], "bracket is a boundary")
    check(r.token_items("A", "アール") == [("U", "#")], "a Latin letter is one key")
    check(r.token_items("3", "3") == [("U", "#")], "a digit is one key")
    check(r.token_items("！", "！") == [("U", "#")], "Shift+digit symbol is one key")
    check(r.token_items("（", "（") == [("U", "#")], "parenthesis (Shift+digit) is one key")
    check(r.token_items("メートル", "メートル") == [("U", "め"), ("B", None), ("U", "とる")], "ー inside a reading splits")
    check(r.token_items("A判", "エーハン") == [("X", None)], "a token mixing Latin and kanji is invalid")
    check(r.token_items("…", "…") == [("X", None)], "an undetermined symbol is invalid")
    check(r.token_items("　", "　") == [], "whitespace is nothing")
    segs = r.segments([("U", "かみ"), ("B", None), ("U", "#"), ("U", "はん"), ("B", None), ("B", None)])
    check(segs == [(rt.count_keys("かみ"), "かみ"), (1 + rt.count_keys("はん"), "#はん"), (0, "")],
          "segments keep empty segments between boundaries and drop the empty last one: %r" % (segs,))
    segs = r.segments([("U", "かみ"), ("X", None), ("B", None), ("U", "は")])
    check(segs == [(-1, "かみ"), (rt.count_keys("は"), "は")], "an X item makes its segment invalid")
    # lines are joined without a boundary
    check([k for k, _ in r.segments_of_lines(["かみ", "の。"])] == [rt.count_keys("かみの")], "newline is not a boundary")
    cs = r.segments_of_lines(copy_lines(repo_path(cfg["inputs"]["copy_text"]["path"])))
    check(len(cs) == 48, "copy text has 48 segments (got %d)" % len(cs))
    check(cs[0] == (rt.count_keys("かみのおおきさにはきまりがあり"), "かみのおおきさにはきまりがあり"), "first copy segment")
    check(all(k >= 0 for k, _ in cs), "copy text has no invalid segment")


def test_records(cfg):
    rule = cfg["record_rule"]
    a, o, b, e, s, n = "alphabetic", "other", "backspace", "enter", "space", "numeric"
    plain = [v for v, _ in segments([a, a, o, a, b, o, a], rule)]
    check(plain == [2, 0], "plain segments drop the open last segment: %r" % plain)
    cats = [a, o, e, b, a, o, a]
    check([v for v, _ in segments(cats, rule)] == [1, 0], "plain keeps a deleted boundary")
    check([v for v, _ in segments(cats, rule, clean=True)] == [2], "clean removes a boundary deleted right after")
    cats = [a, o, a, b, o, a]
    check([v for v, _ in segments(cats, rule, clean=True)] == [1, 0], "clean keeps a boundary followed by a letter")
    st = segments([a, n, s, e, b, o], rule)[0][1]
    check(st == {"alphabetic": 1, "numeric": 1, "backspace": 1, "enter": 1, "space": 1}, "per-segment counts: %r" % st)
    check([v for v, _ in segments([n, a, o], rule)] == [2], "digits count")
    cats = [a, o, o, b, a, o]
    check([v for v, _ in segments(cats, rule)] == [1, 0, 0], "plain with two boundaries in a row")
    check([v for v, _ in segments(cats, rule, clean=True)] == [1, 1], "clean: only the boundary right before the minus")
    cats = [a, o, b, b, a, o]
    check([v for v, _ in segments(cats, rule, clean=True)] == [1], "clean: only the first of two minuses is skipped")
    try:
        segments([a, "punctuation", o], rule)
        check(False, "an unknown category stops")
    except SystemExit:
        pass


def test_align():
    y = [10, 20, 30]
    check(align([10, 20, 30], y, 8) == [(0, 1, 0, 1), (1, 2, 1, 2), (2, 3, 2, 3)], "identity alignment")
    check(align([10, 8, 12, 30], y, 8) == [(0, 1, 0, 1), (1, 3, 1, 2), (3, 4, 2, 3)], "inserted boundary")
    check(align([30, 30], y, 8) == [(0, 1, 0, 2), (1, 2, 2, 3)], "missing boundary")
    g = align([10, 20], [10, 20, 30, 40], 8)
    check(g == [(0, 1, 0, 1), (1, 2, 1, 2)], "the text may end early")
    check(start_map(align([10, 8, 12, 30], y, 8)) == {0: 0, 1: 1, 2: 1, 3: 2}, "start map")
    check(align([12, 19, 31], y, 8) == [(0, 1, 0, 1), (1, 2, 1, 2), (2, 3, 2, 3)], "small differences stay 1:1")
    check(align([10], [10, 0], 0) == [(0, 1, 0, 1)], "end tie: the smallest text position")
    check(align([5, 5], [10, 0], 0)[0] == (0, 2, 0, 1), "a 2:1 group when it costs less than 1:1 steps")


def test_processing():
    x = np.array([5, -3, 9, 2])
    check(list(matching.process(x, {"kind": "bin", "w": 4})) == [1, -1, 2, 0], "bin floors like Python //")
    check(list(matching.process(x, {"kind": "bin", "w": None})) == [0, 0, 0, 0], "bin inf")
    check(list(matching.process(x, {"kind": "merge", "m": 3})) == [11, 2], "merge with a short last group")
    check(list(matching.process(x, {"kind": "merge", "m": None})) == [13], "merge all")
    check(list(matching.process(x, {"kind": "sort"})) == [-3, 2, 5, 9], "sort")
    D = np.array([[5, -3, 9, 2], [0, 0, 0, 0]])
    ts, ds = matching.scores({"kind": "none"}, x, np.array([5, -3, 9, 3]), D)
    check(ts == 1 and list(ds) == [0, 19], "L1 scores")
    check(matching.credit(1, np.array([0, 19])) == 0.0, "credit 0")
    check(matching.credit(0, np.array([1, 2])) == 1.0, "credit 1")
    check(matching.credit(2, np.array([2, 2, 5])) == 1 / 3, "credit with ties")
    t = np.array([5, -3, 9, 3])
    ts, ds = matching.scores({"kind": "bin", "w": 4}, x, t, np.array([t, [50, 50, 50, 50]]))
    check(matching.credit(ts, ds) == 0.5, "a decoy equal to the truth halves the credit")
    check(matching.credit(1.0, np.array([1.5, 2.0])) == 1.0, "credit compares floats without truncation")


def test_end_to_end(cfg):
    rng = np.random.default_rng(1)
    works = [list(rng.integers(100, 200, size=30)) for _ in range(40)]
    works[0][5] = -1  # an invalid segment
    y = [10, 20, 30, 40, 50, 60]
    with tempfile.TemporaryDirectory() as d:
        write_json(os.path.join(d, "corpus.json"), {"keys": [[int(v) for v in w] for w in works]})
        write_json(os.path.join(d, "copy.json"), {"keys": y})
        recs = {"B": {"plain": [10, 20, 30, 40, 50], "clean": [10, 20, 30, 40, 50]},
                "C": {"plain": [10, 21, 30, 40, 50, 60, 70], "clean": []},
                "E": {"plain": [10, 20, 30, 40, 50, 60], "clean": []}}
        write_json(os.path.join(d, "records.json"), {"blocks": recs})
        c2 = copymod.deepcopy(cfg)
        c2["matching"]["draws_per_window"] = 5
        matching._init(os.path.join(d, "corpus.json"), os.path.join(d, "copy.json"), d, c2, "test", 0.0)
        corpus = matching._G["corpus"]
        for k in (1, 3, 30):
            el, counts, flat, soff = corpus.windows(k)
            D = corpus.draw(np.random.default_rng(2), k, min(10, len(el)))
            check(D.shape[1] == k and (D >= 0).all(), "draw gives valid windows of length k=%d" % k)
        check(len(corpus.windows(30)[0]) == 39, "a work with an invalid segment has no full-length window")
        _, per = matching.run_task(("copy", "B", 2, 10))
        check(len(per["L_none"]["mean"]) == 4, "4 windows of k=2 in 5 segments")
        check(all(m == 1.0 for m in per["L_none"]["mean"]), "the exact record is matched")
        check(all(abs(m - 0.1) < 1e-12 for m in per["L_bininf"]["mean"]), "bin inf scores exactly 1/N")
        check(all(m == 1.0 for m in per["no_record"]["mean"]), "no-record predictor (target 0): the small truth is closest")
        _, per = matching.run_task(("copy", "E", 2, 10))
        check(len(per["L_none"]["mean"]) == 5, "a window may end at the last text segment")
        _, per = matching.run_task(("control", "C", 3, 10))
        check(len(per["L_none"]["mean"]) == 5, "control: every window of the record")
        _, per = matching.run_task(("clean", "B", 5, 10))
        check(list(per) == ["Lclean_none"] and len(per["Lclean_none"]["mean"]) == 1, "clean task")
        # determinism
        _, p1 = matching.run_task(("copy", "B", 1, 10))
        _, p2 = matching.run_task(("copy", "B", 1, 10))
        check(p1 == p2, "run_task is deterministic")


def test_explore_align():
    import functools
    import explore_align
    from align import ORDER

    def brute(x, c, lam):
        @functools.lru_cache(None)
        def f(i, j):
            if i == 0 and j == 0:
                return 0
            best = None
            for p, q in ORDER:
                if i - p < 0 or j - q < 0:
                    continue
                prev = f(i - p, j - q)
                if prev is None:
                    continue
                v = prev + abs(sum(x[i - p:i]) - sum(c[j - q:j])) + lam * (p - 1 + q - 1)
                best = v if best is None or v < best else best
            return best
        return f(len(x), len(c))

    rng = np.random.default_rng(3)
    for k in (1, 2, 3, 5, 8):
        x = rng.integers(-2, 40, size=k)
        C = rng.integers(0, 40, size=(6, k))
        got = explore_align.align_cost(x, C, 8)
        want = [brute(tuple(int(v) for v in x), tuple(int(v) for v in row), 8) for row in C]
        check(list(int(v) for v in got) == want, "align_cost equals the brute force (k=%d)" % k)
    check(int(explore_align.align_cost(np.array([10, 8, 12, 30]), np.array([[10, 20, 30, 7]]), 8)[0]) == 8 + (7 + 8),  # 2:1 then 1:2 (both windows are used to the end); 1:1 throughout costs 53
          "align_cost: an inserted boundary costs 8 instead of shifting every later segment")


def test_guards(cfg):
    try:
        assert_private_dir(REPO)
        check(False, "the repository is refused as a work directory")
    except SystemExit:
        pass
    with tempfile.TemporaryDirectory() as d:
        assert_private_dir(d)  # a temporary directory outside any checkout is accepted
    check(corpus_build_key(cfg) == corpus_build_key(cfg), "build key is deterministic")
    c2 = copymod.deepcopy(cfg)
    c2["text_rule"]["counted_symbols"] += "x"
    check(corpus_build_key(c2) != corpus_build_key(cfg), "build key follows the text rule")
    import build_corpus
    from multiprocessing import Pool
    with Pool(1, initializer=build_corpus._init) as pool:
        try:
            pool.map(build_corpus.work_keys, [("x", os.path.join(REPO, "README.md"), "0" * 64)])
            check(False, "a zip with the wrong SHA-256 stops the pool")
        except RuntimeError:
            pass


def test_round2_guards():
    import build_corpus
    from common import read_json, stats_body_sha256, write_private_json
    # an initialiser failure is raised by the task, not swallowed by a respawning pool
    build_corpus._INIT_ERROR = "test"
    try:
        build_corpus.work_keys(("x", "nofile", "0" * 64))
        check(False, "build_corpus: an initialiser failure is raised by the task")
    except RuntimeError:
        pass
    finally:
        build_corpus._INIT_ERROR = None
    matching._G["init_error"] = "test"
    try:
        matching.run_task(("copy", "B", 1, 10))
        check(False, "matching: an initialiser failure is raised by the task")
    except RuntimeError:
        pass
    finally:
        del matching._G["init_error"]
    # a hard link to another file is replaced, not written through
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        target = os.path.join(d1, "target.json")
        write_json(target, {"keep": 1})
        linked = os.path.join(d2, "records.json")
        try:
            os.link(target, linked)
        except OSError:
            linked = None
        if linked:
            write_private_json(linked, {"secret": 1})
            check(read_json(target) == {"keep": 1}, "write_private_json does not write through a hard link")
            check(read_json(linked) == {"secret": 1}, "write_private_json writes the new file")
            check([n for n in os.listdir(d2) if n.startswith(".tmp-")] == [], "no temporary file is left")
    st = {"a": 1, "median_valid": 23.0}
    st["body_sha256"] = stats_body_sha256(st)
    st2 = dict(st, median_valid=22.0)
    check(stats_body_sha256(st2) != st["body_sha256"], "an edited stats value changes the body hash")


def main():
    cfg = load_config()
    check_inputs(cfg)
    test_rule(cfg)
    test_records(cfg)
    test_align()
    test_processing()
    test_end_to_end(cfg)
    test_explore_align()
    test_guards(cfg)
    test_round2_guards()
    if FAILS:
        print("selftest: %d failures" % len(FAILS))
        return 1
    print("selftest: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
