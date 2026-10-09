"""Self-test of the experiment (design.md section 10). run.sh runs it before the analysis and stops on failure.

  selftest.py            all checks (needs SudachiPy for the preprocessing checks)
  selftest.py --no-sudachi

Exit 0 when every check passes, 1 otherwise.
"""
import argparse
import math
import os
import random
import sys
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import romaji_table as rt  # noqa: E402
import matching as mt  # noqa: E402
import uniqueness as un  # noqa: E402
import build_segments as bs  # noqa: E402

FAILS = []
N_CHECKS = [0]


def check(name, cond, detail=""):
    N_CHECKS[0] += 1
    if not cond:
        FAILS.append(name + (": " + str(detail) if detail else ""))


def chi2_z(counts, expected):
    chi2 = sum((o - expected) ** 2 / expected for o in counts)
    df = len(counts) - 1
    return (chi2 - df) / math.sqrt(2 * df)


# ---------------------------------------------------------------- 1. romaji table
def test_romaji():
    sys.path.insert(0, os.path.join(REPO, "papers", "ime-observation", "kit", "gen"))
    import romaji  # the original table
    rng = random.Random(1)
    alphabet = [ch for ch in romaji.ALPHABET if ch not in "、。"]
    bad = 0
    for _ in range(5000):
        s = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 12)))
        if rt.count_keys(s) != len(romaji.to_keys(s)):
            bad += 1
    check("standard count equals romaji.py to_keys", bad == 0, "%d mismatches" % bad)
    known = [
        ("しんぶん", frozenset(), 9), ("しんぶん", frozenset(["si", "n"]), 7),
        ("ちょっと", frozenset(["ti"]), 6), ("つっつく", frozenset(), 9), ("つっつく", frozenset(["tu"]), 7),
        ("じゃあ", frozenset(), 3), ("じゃあ", frozenset(["jya"]), 4), ("んな", frozenset(["n"]), 4),
        ("んや", frozenset(["n"]), 4), ("さんか", frozenset(["n"]), 5), ("あん", frozenset(["n"]), 3),
        ("#ー", frozenset(), 2), ("", frozenset(), 0), ("っち", frozenset(["ti"]), 3),
    ]
    for s, habits, want in known:
        got = rt.count_keys(s, habits)
        check("known count %s %s" % (s, sorted(habits)), got == want, "got %d want %d" % (got, want))


# ---------------------------------------------------------------- 2. scoring
def test_scoring():
    check("tie of two scores 1/2", mt.credit_l1((1, 2), [(1, 2), (1, 2), (3, 4)], 0) == 0.5)
    check("a closer wrong candidate scores 0", mt.credit_l1((3, 4), [(1, 2), (3, 4)], 0) == 0.0)
    check("all identical scores 1/N", abs(mt.credit_l1((5,), [(5,)] * 7, 3) - 1 / 7) < 1e-12)
    check("unique nearest scores 1", mt.credit_l1((2, 2), [(2, 3), (9, 9), (0, 0)], 0) == 1.0)
    check("tie at a nonzero distance", mt.credit_l1((0, 0), [(1, 0), (0, 1), (5, 5)], 1) == 0.5)


# ---------------------------------------------------------------- 3. how the true candidate is chosen
def test_sampler():
    rng = random.Random(7)
    # 60 works of very unequal size; work 0 has 20000 windows, others 1 to 5; works 1 and 2 hold the same
    # sequence (a duplicate across candidates)
    sizes = [20000] + [rng.randint(1, 5) for _ in range(59)]
    starts = [array("i", range(s)) for s in sizes]
    eligible = list(range(len(sizes)))
    N, T = 10, 30000
    rs = random.Random(11)
    true_work = [0] * len(sizes)
    true_index = [0] * N
    hit_random = hit_max = 0.0
    rd = random.Random(12)
    for _ in range(T):
        ws, wins, true = mt.draw_trial(rs, eligible, starts, N)
        check_unique = len(set(ws)) == N
        if not check_unique:
            check("candidates come from different works", False)
            break
        true_work[ws[true]] += 1
        true_index[true] += 1
        hit_random += 1.0 if rd.randrange(N) == true else 0.0
        sz = [sizes[w] for w in ws]
        top = max(sz)
        hit_max += 1.0 / sz.count(top) if sz[true] == top else 0.0
    zw = chi2_z(true_work, T / len(sizes))
    zi = chi2_z(true_index, T / N)
    check("true work frequency is uniform over works (|z| < 4)", abs(zw) < 4, "z=%.2f" % zw)
    check("true index frequency is uniform (|z| < 4)", abs(zi) < 4, "z=%.2f" % zi)
    se = math.sqrt((1 / N) * (1 - 1 / N) / T)
    check("random predictor near 1/N", abs(hit_random / T - 1 / N) < 4 * se, hit_random / T)
    check("largest-work predictor near 1/N", abs(hit_max / T - 1 / N) < 4 * se, hit_max / T)
    # negative control: a sampler that pools all windows makes the largest-work predictor far above 1/N
    pooled = [(w, i) for w, s in enumerate(sizes) for i in range(s)]
    hits = 0.0
    rs2 = random.Random(13)
    for _ in range(3000):
        true_w, _i = rs2.choice(pooled)
        others = rs2.sample([w for w in eligible if w != true_w], N - 1)
        ws = others + [true_w]
        sz = [sizes[w] for w in ws]
        top = max(sz)
        hits += 1.0 / sz.count(top) if sizes[true_w] == top else 0.0
    check("negative control: pooled windows bias the largest-work predictor", hits / 3000 > 0.5, hits / 3000)
    # identical sequences across candidates are checked end to end in test_run_cell


# ---------------------------------------------------------------- 4. BackSpace model
def test_backspace():
    rng = random.Random(3)
    kana = [ch for ch in rt.KANA_CHARS if ch not in "ゕゖ"] + ["#"]
    strings = ["".join(rng.choice(kana) for _ in range(rng.randint(3, 20))) for _ in range(4000)]
    parts_all = [rt.unit_keys(s) for s in strings]
    r_bar = sum(len(p) for ps in parts_all for p in ps) / sum(len(ps) for ps in parts_all)
    for share in (0.018, 0.063, 0.108):
        p = mt.bs_prob(share, r_bar, 0.5)
        text = bsp = 0
        r2 = random.Random(int(share * 1000))
        for ps in parts_all:
            for part in ps:
                text += len(part)
                if r2.random() < p:
                    bsp += 1
                    text += len(part) if r2.random() < 0.5 else 1
        got = bsp / (text + bsp)
        check("BackSpace share %.3f reproduced" % share, abs(got - share) < 0.003, "got %.4f" % got)
    s = "かしゃ#"
    parts = rt.unit_keys(s)
    cond = {"habit_prob": 0.0, "shift_prob": 0.0}
    all_kana = mt.noisy_counts([s], cond, 1.0, 1.0, random.Random(1))[0]
    check("kana-level corrections add r-1 per unit", all_kana == sum(2 * len(x) - 1 for x in parts), all_kana)
    letter = mt.noisy_counts([s], cond, 1.0, 0.0, random.Random(1))[0]
    check("letter-level corrections cancel in the net count", letter == rt.count_keys(s), letter)
    shifted = {mt.noisy_counts([""], {"habit_prob": 0.0, "shift_prob": 1.0}, 0.0, 0.5, random.Random(sd))[0]
               for sd in range(60)}
    check("a shift of -1 from zero is clamped to 0 and +1 gives 1", shifted == {0, 1}, shifted)


# ---------------------------------------------------------------- 3b. run_cell end to end on a synthetic corpus
def _write_derived(tmp, works_segs):
    import hashlib
    import json
    import pickle
    keys, units = [], []
    for segs in works_segs:
        k, u = bs.pack(segs)
        keys.append(k)
        units.append(u)
    path = os.path.join(tmp, "corpus_B0.pkl")
    with open(path, "wb") as f:
        pickle.dump({"work_ids": ["w%d" % i for i in range(len(works_segs))], "sha256": [""] * len(works_segs),
                     "keys": keys, "units": units}, f, protocol=4)
    stats = os.path.join(tmp, "stats.json")
    with open(stats, "w", encoding="utf-8") as f:
        json.dump({"derived_files_sha256": {"corpus_B0.pkl": hashlib.sha256(open(path, "rb").read()).hexdigest()}}, f)
    return stats


def test_run_cell():
    import tempfile
    mcfg = {"trials": 300, "bootstrap": 60, "ci": 0.95, "bs_kana_level_fraction": 0.5,
            "conditions": {"ideal": {"reading": "plain", "habit_prob": 0.0, "bs_share": 0.0, "shift_prob": 0.0},
                           "mid": {"reading": "writer", "habit_prob": 0.5, "bs_share": 0.063, "shift_prob": 0.05}}}
    rng = random.Random(21)
    kana = "あかさたなはまやらわんしちつ"

    def seg(s):
        return (rt.count_keys(s), s, s, True)
    works = [[seg("".join(rng.choice(kana) for _ in range(rng.randint(0, 3)))) for _ in range(rng.randint(2, 9))]
             for _ in range(25)]
    with tempfile.TemporaryDirectory() as tmp:
        stats = _write_derived(tmp, works)
        mt._DATA.clear()
        cell = mt.run_cell((tmp, stats, "B0", 2, 6, mcfg, "s", 1.9))
        # recompute the ideal credits from the same draws with the plain scoring function
        keys = [bs.pack(w)[0] for w in works]
        starts = [mt.valid_starts(kk, 2) for kk in keys]
        eligible = [w for w in range(len(keys)) if len(starts[w])]
        rs = random.Random(mt.seed_int("s", "struct", "B0", 2, 6))
        total = 0.0
        for _ in range(mcfg["trials"]):
            ws, wins, true = mt.draw_trial(rs, eligible, starts, 6)
            cands = [tuple(keys[w][i:i + 2]) for w, i in zip(ws, wins)]
            total += mt.credit_l1(cands[true], cands, true)
        check("run_cell ideal credit equals credit_l1 on the same draws",
              abs(cell["results"]["ideal"]["acc"] - total / mcfg["trials"]) < 1e-12,
              (cell["results"]["ideal"]["acc"], total / mcfg["trials"]))
        lo, hi = cell["results"]["ideal"]["ci"]
        check("bootstrap interval contains the estimate", lo <= cell["results"]["ideal"]["acc"] <= hi, (lo, hi))
        check("noisy condition scored", 0.0 <= cell["results"]["mid"]["acc"] <= 1.0, cell["results"]["mid"])
        mt._DATA.clear()
        cell = mt.run_cell((tmp, stats, "B0", 2, 26, mcfg, "s", 1.9))
        check("a cell with fewer eligible works than N is not computed", cell["status"].startswith("not computable"),
              cell["status"])
    same = [[seg("かな"), seg("さた")] for _ in range(8)]  # one window of k = 2 per work, the same everywhere
    with tempfile.TemporaryDirectory() as tmp:
        stats = _write_derived(tmp, same)
        mt._DATA.clear()
        cell = mt.run_cell((tmp, stats, "B0", 2, 4, mcfg, "s", 1.9))
        check("identical candidates score exactly 1/N", abs(cell["results"]["ideal"]["acc"] - 0.25) < 1e-12,
              cell["results"]["ideal"]["acc"])
    with tempfile.TemporaryDirectory() as tmp:
        stats = _write_derived(tmp, [[seg("かな"), seg("さた"), seg("な")]])
        mt._DATA.clear()
        cell = mt.run_cell((tmp, stats, "B0", 2, 1, mcfg, "s", 1.9))
        check("one work and N = 1: score 1 and a point interval",
              cell["results"]["ideal"]["acc"] == 1.0 and cell["results"]["ideal"]["ci"] == [1.0, 1.0], cell["results"]["ideal"])
        with open(os.path.join(tmp, "corpus_B0.pkl"), "ab") as f:
            f.write(b"x")
        mt._DATA.clear()
        try:
            mt.run_cell((tmp, stats, "B0", 2, 1, mcfg, "s", 1.9))
            check("a derived file that differs from corpus_stats.json is refused", False)
        except SystemExit:
            check("a derived file that differs from corpus_stats.json is refused", True)
    mt._DATA.clear()


# ---------------------------------------------------------------- 3c. fetching and the manifest (offline)
def test_fetch_offline():
    import json
    import tempfile
    import zipfile
    import fetch_works as fw
    for bad_id, bad_url in (("../x", "https://www.aozora.gr.jp/cards/000001/files/1.zip"),
                            ("000001", "file:///etc/passwd"), ("000001", "https://example.com/cards/1.zip")):
        try:
            fw.check_entry(bad_id, bad_url)
            check("rejects %s %s" % (bad_id, bad_url), False)
        except SystemExit:
            check("rejects %s %s" % (bad_id, bad_url), True)
    with tempfile.TemporaryDirectory() as tmp:
        zips = os.path.join(tmp, "zips")
        os.makedirs(zips)
        zpath = os.path.join(zips, "000001.zip")
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr("a.txt", "text")
        url = "https://www.aozora.gr.jp/cards/000001/files/1_ruby_1.zip"
        man = os.path.join(tmp, "manifest.json")
        check("verify-only without a manifest fails", fw.verify_only(man, zips) == 1)
        check("verify-only writes no manifest", not os.path.exists(man))
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"works": [{"work_id": "000001", "role": "corpus", "url": url,
                                  "sha256": fw.sha256_file(zpath)}]}, f)
        check("verify-only passes on a matching zip", fw.verify_only(man, zips) == 0)
        with open(zpath, "ab") as f:
            f.write(b"x")
        check("verify-only fails on a changed zip", fw.verify_only(man, zips) == 1)
        sel = os.path.join(tmp, "sel.json")
        cfgp = os.path.join(tmp, "cfg.json")
        with open(sel, "w", encoding="utf-8") as f:
            json.dump({"seed": "1", "ordered": [{"work_id": "000002", "text_url": url}], "reference": []}, f)
        with open(cfgp, "w", encoding="utf-8") as f:
            json.dump({"fetch": {"interval_s": 1, "retries": 1, "user_agent": "t"},
                       "selection": {"fetch_count": 1, "reference_works": []}}, f)
        rc = fw.main(["--selection", sel, "--config", cfgp, "--zips", zips, "--manifest", man])
        check("a selection that differs from the committed manifest stops before any download", rc == 1, rc)


def test_dedupe_lines():
    a = bs.line_hashes(["　吾輩《わがはい》は猫である。名前はまだ無い。どこで生れたか見当がつかぬ。", "短い行"], 20)
    b = bs.line_hashes(["吾輩は猫である。 名前はまだ無い。どこで生れたか見当がつかぬ。"], 20)
    check("text dedupe ignores ruby and whitespace", a == b and len(a) == 1, (a, b))
    check("lines shorter than the minimum are ignored", bs.line_hashes(["短い行"], 20) == set())
    c = bs.line_hashes(["吾輩は犬である。名前はまだ無い。どこで生れたか見当がつかぬ。"], 20)
    check("a different text of the same length is not a duplicate", c.isdisjoint(a))


# ---------------------------------------------------------------- 5. measure 1
def test_uniqueness():
    r = un.measure([array("i", [1, 2, 1, 2]), array("i", [1, 2, 3])], {1, 2})
    by = {x["k"]: x for x in r}
    check("k=1 unique count", by[1]["unique"] == 1 and by[1]["windows"] == 7, by[1])
    check("k=2 unique count", by[2]["unique"] == 2 and by[2]["windows"] == 5, by[2])
    check("k=2 distinct count", by[2]["distinct"] == 3, by[2])
    r = un.measure([array("i", [1, -1, 1])], {2})
    check("an invalid segment breaks windows", r[0]["windows"] == 0, r)
    r = un.measure([array("i", [4, 5]), array("i", [6])], {2})
    check("a window never crosses works", r[0]["windows"] == 1, r)
    r = un.measure([array("i", [0, 5]), array("i", [5, 0]), array("i", [0, 5])], {2})
    check("zero-length segments are compared by position", r[0]["unique"] == 1 and r[0]["distinct"] == 2, r)
    st = mt.valid_starts(array("i", [1, 1, -1, 1, 1, 1]), 2)
    check("valid starts", list(st) == [0, 3, 4], list(st))


# ---------------------------------------------------------------- 6. preprocessing (real SudachiPy)
SAMPLE = "\n".join([
    "題名", "著者名", "",
    "-------------------------------------------------------",
    "【テキスト中に現れる記号について】", "《》：ルビ",
    "-------------------------------------------------------",
    "［＃３字下げ］一［＃「一」は中見出し］",
    "［＃改ページ］",
    "　吾輩《わがはい》は猫である。名前はまだ無い。",
    "「どこで生れたか、とんと見当《けんとう》がつかぬ……」と泣いていた。",
    "",
    "第1の話、ＡＢＣ社。",
    "",
    "底本：「吾輩は猫である」",
    "入力：誰か",
])


def test_preprocessing(use_sudachi):
    lines, no_dash = bs.body_lines(SAMPLE)
    check("body lines", lines == ["一", "　吾輩《わがはい》は猫である。名前はまだ無い。",
                                  "「どこで生れたか、とんと見当《けんとう》がつかぬ……」と泣いていた。", "",
                                  "第1の話、ＡＢＣ社。"] and not no_dash, lines)
    plain, writer, cut_map, n_ruby, n_sub = bs.parse_ruby("｜何でも薄暗い《なんでもうすぐらい》所で種《たね》")
    check("ruby plain", plain == "何でも薄暗い所で種", plain)
    check("ruby writer", writer == "なんでもうすぐらい所でたね", writer)
    check("ruby counts", (n_ruby, n_sub) == (2, 2), (n_ruby, n_sub))
    check("adjacent implicit ruby keeps both readings",
          bs.parse_ruby("漢字《かんじ》漢字《かんじ》")[:2] == ("漢字漢字", "かんじかんじ"), bs.parse_ruby("漢字《かんじ》漢字《かんじ》")[:2])
    check("adjacent implicit ruby with following text",
          bs.parse_ruby("吾輩《わがはい》猫《ねこ》である")[:2] == ("吾輩猫である", "わがはいねこである"))
    check("kana iteration marks are invalid (design 4.3)", bs.token_units(0, "こゝろ", "ココロ")[0][1] == "X")
    items = [(1, "U", "わがはい"), (3, "U", "は"), (4, "U", "ねこ"), (8, "B", "period")]
    cf = [c[0] for c in bs.line_cuts("　吾輩は猫である。", items, [1, 4], "bunsetsu") if c[2] == "CF"]
    check("no confirm before anything is typed (indented line start)", cf == [4, 9], cf)
    cf = [c[0] for c in bs.line_cuts("一", [(0, "U", "いち")], [0], "bunsetsu") if c[2] == "CF"]
    check("a line that was typed ends with one confirm", cf == [1], cf)
    cf = [c[0] for c in bs.line_cuts("", [], [], "sentence") if c[2] == "CF"]
    check("a blank line gets no confirm", cf == [], cf)
    check("cut map is monotonic and spans the writer line",
          all(cut_map[i] <= cut_map[i + 1] for i in range(len(cut_map) - 1)) and cut_map[-1] == len(writer)
          and cut_map[6] == 9, cut_map)
    p2, w2, _, n2, s2 = bs.parse_ruby("Ｘ線《エックスせん》とカタカナ《かたかな》")
    check("ruby without a kanji base is dropped", (p2, s2) == ("Ｘ線とカタカナ", 1) and w2 == "Ｘえっくすせんとカタカナ", (p2, w2, s2))
    tok = type("T", (), {"_max": 40})()
    chunks = bs.Tokenizer.chunks(tok, "あいう。" * 30)
    check("long lines are split after 。 and rejoin exactly",
          "".join(c for _, c in chunks) == "あいう。" * 30 and all(len(c.encode("utf-8")) <= 40 for _, c in chunks)
          and all(c.endswith("。") for _, c in chunks), chunks[:3])
    check("ellipsis is invalid", bs.token_units(0, "…", "．") == [(0, "X", "…")])
    check("symbol with a kana reading is invalid", bs.token_units(0, "※", "キゴウ")[0][1] == "X")
    check("mixed digit and kanji is invalid", bs.token_units(0, "第1", "ダイイチ")[0][1] == "X")
    check("digits, a period and letters are typed one by one",
          [k for _, k, _ in bs.token_units(0, "３．１４", "サン．イチヨン")] == ["U", "B", "U", "U"])
    check("dash is one key", bs.token_units(0, "――", "キゴウ") == [(0, "U", "#"), (1, "U", "#")])
    if not use_sudachi:
        return
    tok = bs.Tokenizer(40000)
    segs, st = bs.segments_of_work(lines, tok)

    def keys(name):
        return [(s[0] if s[3] else None) for s in segs[name]]
    check("B0 key counts", keys("B0") == [4, 18, 14, 0, 16, None, 0, 0, 13, 6, 0], keys("B0"))
    check("B3 key counts", keys("B3") == [22, 14, 16, None, 13, 6], keys("B3"))
    check("B1 key counts", keys("B1") == [4, 0, 18, 0, 14, 0, 0, 16, None, 0, 0, 0, 13, 6, 0, 0], keys("B1"))
    b2 = keys("B2")
    check("B2 key counts (counted by hand)",
          b2 == [4, 0, 9, 9, 0, 7, 7, 0, 0, 7, 9, 0, 6, None, 8, 0, 0, 0, 6, 7, 0, 6, 0, 0], b2)
    joined ={name: "".join(s[1] for s in segs[name]) for name in segs}
    check("every segmentation keeps the same units in the same order", len(set(joined.values())) == 1, joined)
    joined_w = {name: "".join(s[2] for s in segs[name]) for name in segs}
    check("the same holds for the writer", len(set(joined_w.values())) == 1, joined_w)
    check("B2 is finer than B0", len(b2) > len(keys("B0")), b2)
    check("ruby that agrees with SudachiPy leaves the writer equal", segs["B0"][1][2] == segs["B0"][1][1],
          segs["B0"][1])
    lines2 = ["種《たね》を蒔く。"]
    segs2, _ = bs.segments_of_work(lines2, tok)
    au, wu = segs2["B0"][0][1], segs2["B0"][0][2]
    check("writer uses the ruby where SudachiPy differs", wu.startswith("たね") and au != wu, (au, wu))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sudachi", action="store_true")
    a = ap.parse_args(argv)
    test_romaji()
    test_scoring()
    test_sampler()
    test_backspace()
    test_run_cell()
    test_fetch_offline()
    test_dedupe_lines()
    test_uniqueness()
    test_preprocessing(not a.no_sudachi)
    if FAILS:
        for f in FAILS:
            print("FAIL " + f)
        print("selftest failed: %d / %d" % (len(FAILS), N_CHECKS[0]))
        return 1
    print("selftest OK (%d checks)" % N_CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
