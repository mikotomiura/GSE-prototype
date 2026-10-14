"""Kana to romaji key counts, with the writer habits of the noisy conditions. Standard library only.

The standard table is copied from papers/ime-observation/kit/gen/romaji.py (Apache-2.0, same author;
SHA-256 of the copied file: 79db4d4ef74fb3e354aff769f0fe5c350cf57410c0adb2e7543d5594afd9f4b1). The copy
adds two units that the corpus needs: `#` (one key for a digit, a Latin letter or a symbol) and `ー`
(the minus key, as in the original). selftest.py checks that the standard count equals the length of
romaji.py's to_keys on random hiragana strings.

Habits (design.md section 4.5), each a property of one writer:
  "n"   ん is typed n (not nn) when the next unit in the same segment starts with a consonant other than n or y
  "si"  し is si (not shi); しゃ行 unchanged
  "ti"  ち is ti (not chi); ちゃ行 unchanged
  "tu"  つ is tu (not tsu)
  "jya" じゃ・じゅ・じょ are jya・jyu・jyo (not ja・ju・jo)
"""

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
    "ー": "-",
    # Added for this experiment: one key for a digit, a Latin letter or a symbol (design.md section 4.3).
    "#": "#",
}

_DIGRAPH = {}
for _base, _cons in (("き", "ky"), ("ぎ", "gy"), ("に", "ny"), ("ひ", "hy"), ("び", "by"), ("ぴ", "py"),
                     ("み", "my"), ("り", "ry"), ("ぢ", "dy"), ("し", "sh"), ("ち", "ch"), ("じ", "j")):
    for _small, _vowel in (("ゃ", "a"), ("ゅ", "u"), ("ょ", "o")):
        _DIGRAPH[_base + _small] = _cons + _vowel
for _small, _vowel in (("ぁ", "a"), ("ぃ", "i"), ("ぇ", "e"), ("ぉ", "o")):
    _DIGRAPH["ふ" + _small] = "f" + _vowel

_DOUBLABLE = frozenset("bcdfghjklmpqrstvwyz")
_N_ALONE_BEFORE = frozenset("bcdfghjklmpqrstvwxz")  # consonants other than n and y

HABITS = ("n", "si", "ti", "tu", "jya")
_HABIT_SINGLE = {"si": ("し", "si"), "ti": ("ち", "ti"), "tu": ("つ", "tu")}
_HABIT_JYA = {"じゃ": "jya", "じゅ": "jyu", "じょ": "jyo"}

KANA_CHARS = frozenset(k for k in _SINGLE if k != "#")


def units(s):
    """String of hiragana, `ー` and `#` -> [(unit, standard romaji)]. Raises ValueError on another character."""
    out = []
    i = 0
    while i < len(s):
        two = s[i:i + 2]
        if len(two) == 2 and two in _DIGRAPH:
            out.append((two, _DIGRAPH[two]))
            i += 2
            continue
        c = s[i]
        if c not in _SINGLE:
            raise ValueError("character not in the table (U+%04X)" % ord(c))
        out.append((c, _SINGLE[c]))
        i += 1
    return out


def unit_keys(s, habits=frozenset()):
    """Romaji spelling of each unit of s (a list of strings, one per unit) for a writer with `habits`."""
    toks = units(s)
    roms = []
    for kana, rom in toks:
        for h, (k, alt) in _HABIT_SINGLE.items():
            if h in habits and kana == k:
                rom = alt
        if "jya" in habits and kana in _HABIT_JYA:
            rom = _HABIT_JYA[kana]
        roms.append(rom)
    parts = []
    for idx, (kana, _rom) in enumerate(toks):
        nxt = roms[idx + 1] if idx + 1 < len(roms) else ""
        if kana == "っ":
            parts.append(nxt[0] if nxt and nxt[0] in _DOUBLABLE else roms[idx])
        elif kana == "ん" and "n" in habits and nxt and nxt[0] in _N_ALONE_BEFORE:
            parts.append("n")
        else:
            parts.append(roms[idx])
    return parts


def count_keys(s, habits=frozenset()):
    """Number of keys to type s (a segment's units) for a writer with `habits`."""
    if not s:
        return 0
    return sum(len(p) for p in unit_keys(s, habits))
