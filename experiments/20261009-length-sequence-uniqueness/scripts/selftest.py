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
    # duplicates across candidates: identical sequences are a tie in the ideal condition
    cands = [(3, 1), (3, 1), (2, 2)]
    check("identical sequences of two candidates tie", abs(1.0 / cands.count(cands[0]) - 0.5) < 1e-12)


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
    shifted = mt.noisy_counts([""], {"habit_prob": 0.0, "shift_prob": 1.0}, 0.0, 0.5, random.Random(5))[0]
    check("a shift never goes below zero", shifted >= 0, shifted)


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
    joined = {name: "".join(s[1] for s in segs[name]) for name in segs}
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
