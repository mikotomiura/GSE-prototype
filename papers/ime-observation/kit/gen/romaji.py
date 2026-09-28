#!/usr/bin/env python3
# kit: selftest
"""ひらがな → ローマ字のキー列（keyname の列）。Python 標準ライブラリだけ。

  romaji.py --keys 'がっこう'     キー列を空白区切りで出す（g a k k o u）
  romaji.py --selftest            表の網羅・一意性（逆写像で元に戻る）・既知例（速い既定・1 秒未満）

決定的な 1 つの表（ヘボン式寄り）。方針:
  - `ん` は常に `nn`。
  - 促音 `っ` は次の子音を重ねる。次が母音・`ん`・小書き（`x` で始まる）・記号・語末なら `xtu`。
    ⚠️ `n` は重ねない（`nna` は「んあ」になるので「っな」にならない）。
  - 小書き（ぁぃぅぇぉゃゅょゎゕゖ）は、拗音（きゃ・しゃ・ふぁ など下の表にあるもの）でなければ `x` 接頭の 1 字。
  - `ー` は minus、`、` は comma、`。` は period。
  - ⚠️ 実際の IME がこの綴りをどう解釈するかは OS・IME で違いうる。手順は較正パイロットで確かめて直す
    （この表を直せば逆写像の一意性 selftest がすぐ赤で教える）。
"""
import argparse
import random
import sys

# 1 字（ぁ〜ゖ の 86 字 ＋ ー ＋ 、。）。記号は内部表記の 1 文字（ー はハイフン・、 はカンマ・。 はピリオド）
_SINGLE = {
    "ぁ": "xa", "あ": "a", "ぃ": "xi", "い": "i", "ぅ": "xu", "う": "u", "ぇ": "xe", "え": "e", "ぉ": "xo", "お": "o",
    "か": "ka", "が": "ga", "き": "ki", "ぎ": "gi", "く": "ku", "ぐ": "gu", "け": "ke", "げ": "ge", "こ": "ko", "ご": "go",
    "さ": "sa", "ざ": "za", "し": "shi", "じ": "ji", "す": "su", "ず": "zu", "せ": "se", "ぜ": "ze", "そ": "so", "ぞ": "zo",
    "た": "ta", "だ": "da", "ち": "chi", "ぢ": "di", "っ": "xtu", "つ": "tsu", "づ": "du", "て": "te", "で": "de",
    "と": "to", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ば": "ba", "ぱ": "pa", "ひ": "hi", "び": "bi", "ぴ": "pi", "ふ": "fu", "ぶ": "bu", "ぷ": "pu",
    "へ": "he", "べ": "be", "ぺ": "pe", "ほ": "ho", "ぼ": "bo", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "ゃ": "xya", "や": "ya", "ゅ": "xyu", "ゆ": "yu", "ょ": "xyo", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "ゎ": "xwa", "わ": "wa", "ゐ": "wi", "ゑ": "we", "を": "wo", "ん": "nn",
    "ゔ": "vu", "ゕ": "xka", "ゖ": "xke",
    "ー": "-", "、": ",", "。": ".",
}

# 2 字（拗音と ふぁ 行）。ここに無い「かな＋小書き」は 1 字ずつ（小書きは x 接頭）に落ちる。
_DIGRAPH = {}
for _base, _cons in (("き", "ky"), ("ぎ", "gy"), ("に", "ny"), ("ひ", "hy"), ("び", "by"), ("ぴ", "py"),
                     ("み", "my"), ("り", "ry"), ("ぢ", "dy"), ("し", "sh"), ("ち", "ch"), ("じ", "j")):
    for _small, _vowel in (("ゃ", "a"), ("ゅ", "u"), ("ょ", "o")):
        _DIGRAPH[_base + _small] = _cons + _vowel
for _small, _vowel in (("ぁ", "a"), ("ぃ", "i"), ("ぇ", "e"), ("ぉ", "o")):
    _DIGRAPH["ふ" + _small] = "f" + _vowel

_REV = {}
for _k, _r in list(_SINGLE.items()) + list(_DIGRAPH.items()):
    _REV[_r] = _k
_MAXLEN = max(len(r) for r in _REV)

# 促音で重ねてよい先頭の文字（母音・n・x・記号は重ねない）
_DOUBLABLE = frozenset("bcdfghjklmpqrstvwyz")

_SYMBOL_TO_KEY = {"-": "minus", ",": "comma", ".": "period"}
_KEY_TO_SYMBOL = dict((v, k) for k, v in _SYMBOL_TO_KEY.items())

# ひらがなの範囲（ぁ U+3041 〜 ゖ U+3096）
HIRAGANA_RANGE = (0x3041, 0x3096)


def _tokens(hira):
    """ひらがな列 → [(かな, 内部ローマ字)]。表に無い文字は ValueError。"""
    out = []
    i = 0
    while i < len(hira):
        two = hira[i:i + 2]
        if len(two) == 2 and two in _DIGRAPH:
            out.append((two, _DIGRAPH[two]))
            i += 2
            continue
        c = hira[i]
        if c not in _SINGLE:
            raise ValueError("表に無い文字（U+%04X）" % ord(c))
        out.append((c, _SINGLE[c]))
        i += 1
    return out


def to_romaji(hira):
    """ひらがな → 内部ローマ字（記号は - , .）。"""
    toks = _tokens(hira)
    parts = []
    for idx, (kana, rom) in enumerate(toks):
        if kana == "っ":
            nxt = toks[idx + 1][1] if idx + 1 < len(toks) else ""
            parts.append(nxt[0] if nxt and nxt[0] in _DOUBLABLE else rom)
        else:
            parts.append(rom)
    return "".join(parts)


def to_keys(hira):
    """ひらがな → keyname の列（a-z と minus / comma / period だけが出る）。"""
    return [_SYMBOL_TO_KEY.get(ch, ch) for ch in to_romaji(hira)]


def _match(s, i):
    for length in range(_MAXLEN, 0, -1):
        tok = s[i:i + length]
        if len(tok) == length and tok in _REV:
            return tok
    return None


def from_romaji(s):
    """内部ローマ字 → ひらがな（逆写像・最長一致）。表で書けない列は ValueError。"""
    out = []
    i = 0
    while i < len(s):
        if i + 1 < len(s) and s[i] == s[i + 1] and s[i] in _DOUBLABLE and _match(s, i + 1) is not None:
            out.append("っ")
            i += 1
            continue
        tok = _match(s, i)
        if tok is None:
            raise ValueError("ローマ字として読めない（位置 %d）" % i)
        out.append(_REV[tok])
        i += len(tok)
    return "".join(out)


def from_keys(keys):
    """keyname の列 → ひらがな。"""
    chars = []
    for k in keys:
        if k in _KEY_TO_SYMBOL:
            chars.append(_KEY_TO_SYMBOL[k])
        elif len(k) == 1 and "a" <= k <= "z":
            chars.append(k)
        else:
            raise ValueError("かなのキーではない keyname")
    return from_romaji("".join(chars))


ALPHABET = tuple(chr(c) for c in range(HIRAGANA_RANGE[0], HIRAGANA_RANGE[1] + 1)) + ("ー", "、", "。")


# ---------------------------------------------------------------- selftest

def selftest():
    fails = []
    n = 0

    def check(name, cond, detail=""):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name + (": " + detail if detail else ""))

    # 1. 網羅: ぁ〜ゖ のすべてと ー、。に写像がある
    for ch in ALPHABET:
        check("網羅 U+%04X" % ord(ch), ch in _SINGLE)
    check("表に余計な 1 字が無い", set(_SINGLE) == set(ALPHABET), str(sorted(set(_SINGLE) ^ set(ALPHABET))))

    # 2. 表の一意性: 同じ綴りが 2 つの項目に割り当たっていない
    values = list(_SINGLE.values()) + list(_DIGRAPH.values())
    check("綴りが重複していない", len(values) == len(set(values)))
    for kana, rom in list(_SINGLE.items()) + list(_DIGRAPH.items()):
        check("逆表が元に戻る %s" % kana, _REV[rom] == kana)
    # 出るキーは a-z と minus / comma / period だけ
    allowed = set("abcdefghijklmnopqrstuvwxyz") | {"minus", "comma", "period"}
    for ch in ALPHABET:
        check("キーが範囲内 U+%04X" % ord(ch), set(to_keys(ch)) <= allowed)

    # 3. 既知例（決定的な表の固定）
    known = [
        ("がっこう", "g a k k o u"), ("しゃしん", "s h a s h i n n"), ("きょう", "k y o u"),
        ("ん", "n n"), ("あっ", "a x t u"), ("いっしょ", "i s s h o"), ("らーめん", "r a minus m e n n"),
        ("っ", "x t u"), ("んな", "n n n a"), ("っん", "x t u n n"), ("っな", "x t u n a"),
        ("っっか", "x t u k k a"), ("ふぁ", "f a"), ("てぃ", "t e x i"), ("ゔ", "v u"), ("ちょっと", "c h o t t o"),
        ("ー", "minus"), ("、。", "comma period"), ("ぁ", "x a"), ("っち", "c c h i"), ("っつ", "t t s u"),
        ("にゃ", "n y a"), ("んや", "n n y a"), ("じゃ", "j a"), ("ぢゃ", "d y a"), ("ゎ", "x w a"),
    ]
    for hira, want in known:
        got = " ".join(to_keys(hira))
        check("既知例 %s" % hira, got == want, "期待 %s・実際 %s" % (want, got))

    # 4. 全ペア往復（隣り合う 2 字のすべての組で、ローマ字から元のひらがなに戻る）
    bad = 0
    for a in ALPHABET:
        for b in ALPHABET:
            s = a + b
            try:
                back = from_keys(to_keys(s))
            except ValueError:
                back = None
            if back != s:
                bad += 1
                if bad <= 5:
                    fails.append("ペア往復 %s → %s" % (s, back))
    n += len(ALPHABET) ** 2
    # 5. 乱択の 3〜8 字の往復（seed 固定・random() だけを使う）
    rng = random.Random(1)
    for _ in range(3000):
        k = 3 + int(rng.random() * 6)
        s = "".join(ALPHABET[int(rng.random() * len(ALPHABET))] for _ in range(k))
        try:
            back = from_keys(to_keys(s))
        except ValueError:
            back = None
        n += 1
        if back != s:
            fails.append("乱択往復 %s → %s" % (s, back))
            break

    # 6. 表に無い文字・ローマ字として読めない列は例外
    for name, fn in (("漢字", lambda: to_keys("漢")), ("カタカナ", lambda: to_keys("ア")),
                     ("ラテン文字", lambda: to_keys("a")), ("孤立した子音", lambda: from_romaji("k")),
                     ("かなのキーでない keyname", lambda: from_keys(["space"])), ("未知の綴り", lambda: from_romaji("qa"))):
        n += 1
        try:
            fn()
            fails.append("例外にならない: " + name)
        except ValueError:
            pass

    if fails:
        for m in fails:
            print("FAIL " + m)
        print("selftest 失敗 %d 件 / %d 件" % (len(fails), n))
        return 1
    print("selftest OK（%d 件）" % n)
    return 0


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="ひらがな → ローマ字のキー列")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--keys", metavar="HIRAGANA")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.keys is None:
        ap.error("--keys HIRAGANA か --selftest が要る")
    try:
        print(" ".join(to_keys(args.keys)))
    except ValueError as e:
        print("romaji.py: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
