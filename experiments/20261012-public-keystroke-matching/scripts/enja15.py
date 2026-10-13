"""ENJA15 (preregistration, "ENJA15 section"): the Key events of a Translog-II session and the form R3j.

Written at check 5 after the element and attribute names and the kinds of the Type and Value values were counted
(results/enja15_structure.json, results/enja15_values.json):
- Key events carry Type (IME, insert, delete, navi, return, edit, speech), Value, Time and Cursor; IMEtext (the
  romaji of a commit), Text (deleted or selected text), Block, X, Y, Width and Height on some of them. Eye, Fix, Mouse,
  System and Interface events are not keyboard events and are not used.
- Type="IME" values are bracketed key names ("[A]" ... "[Z]", "[Back]", "[Space]", "[Return]", "[Oemcomma]", ...).
  Type="insert" values are mostly committed strings, and one ASCII letter for a direct-input letter.
- The translation is LogFile/FinalTextUTF8 of the same file (the final text of the session's own log).

R3j keeps, for each Key event, its time, its Type and a category from the closed list R3J_CATEGORIES; Value,
IMEtext, Text and every other attribute are dropped. The category of a committed string is "commit", or
"commit_punct" when the string contains a Japanese or full-width punctuation mark that closes a segment.
"""
import re
import xml.etree.ElementTree as ET

TYPES = ("IME", "insert", "delete", "navi", "return", "edit", "speech")
R3J_CATEGORIES = ("letter", "backspace", "convert", "commit", "commit_punct", "enter", "navigation", "other")
SEG_PUNCT = "、。，．"
LETTER_KEY = re.compile(r"^\[[A-Z]\]$")
NAV_KEYS = {"[Left]", "[Right]", "[Up]", "[Down]", "[Home]", "[End]", "[PageUp]", "[Next]", "[Prior]", "[PageDown]"}
CONVERT_KEYS = {"[Space]", "[F7]", "[F8]", "[F9]", "[F10]"}


def key_events(path):
    """[(time, type, attributes)] of the Key events in document order; the attributes stay inside this process."""
    out = []
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "Key":
            out.append((int(el.get("Time")), el.get("Type"), dict(el.attrib)))
        if el.tag in ("Key", "Eye", "Fix", "Mouse", "System", "CharPos", "Interface"):
            el.clear()
    return out


def final_text(path):
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag == "FinalTextUTF8":
            return el.text or ""
        if el.tag in ("Key", "Eye", "Fix", "Mouse", "System", "CharPos", "Interface"):
            el.clear()
    return None


def category(t, a):
    v = a.get("Value") or ""
    if v == "[Back]":
        return "backspace"
    if t == "IME":
        if LETTER_KEY.match(v):
            return "letter"
        if v in CONVERT_KEYS:
            return "convert"
        if v == "[Return]":
            return "commit"
        if v in NAV_KEYS:
            return "navigation"
        return "other"
    if t == "insert":
        if len(v) == 1 and v.isascii() and v.isalpha():
            return "letter"
        if v and not (len(v) == 1 and v.isascii()):
            return "commit_punct" if any(c in SEG_PUNCT for c in v) else "commit"
        return "other"
    if t == "return":
        return "enter"
    if t == "navi":
        return "navigation"
    return "other"


def r3j(events):
    """R3j rows: {time, type, category}."""
    return [{"time": tm, "type": t, "category": category(t, a)} for tm, t, a in events]


def r3j_t(rows, w):
    """R3j-t(w): R3j with the keydown time floored to w ms."""
    return [dict(r, time=(r["time"] // w) * w) for r in rows]


# --- segments (preregistration, "Segments", ENJA15 rows) --------------------------------------------------------------

def record_segments(rows):
    """Values of the record segments: a letter press (Type IME [A]..[Z], or Type insert of one ASCII letter) +1, a
    [Back] press (Type IME and Type delete) -1; a commit whose string holds 、。，． closes the segment (an empty
    segment too, as in the KLiCKe rule); a trailing open segment is kept if it has a counted press. Reads the
    category column only, so R0j, R3j and R3j-t(w) give the same values."""
    segs, v, counted = [], 0, False
    for r in rows:
        c = r["category"]
        if c == "letter":
            v, counted = v + 1, True
        elif c == "backspace":
            v, counted = v - 1, True
        elif c == "commit_punct":
            segs.append(v)
            v, counted = 0, False
    if counted:
        segs.append(v)
    return segs


def a0_record(rows):
    """Letter presses - [Back] presses (A0 of the ENJA15 section)."""
    return sum(1 for r in rows if r["category"] == "letter") - sum(1 for r in rows if r["category"] == "backspace")


def r0j(events):
    """R0j rows: R3j with every attribute kept (the reference form). The attackers read the category only."""
    return [{"time": tm, "type": t, "category": category(t, a), "attributes": a} for tm, t, a in events]


# --- the translation side -----------------------------------------------------------------------------------------
# The reading rules follow experiments/20261009-length-sequence-uniqueness/scripts/build_segments.py (token_units;
# SHA-256 7b84a46b...), restricted to the ENJA15 boundaries of the preregistration (、。，． and line breaks).

TEXT_SPLIT = re.compile("[、。，．\n]")
SYMBOL_ONE_KEY = frozenset(
    "「」『』〔〕［］【】〈〉｛｝{}[]（）()！!？?・／/―─—－‐-ー〜～：:；;＝=＋+＊*＃#＆&＠@％%＿_＾^＼\｜|\"“”'‘’,."
)
WHITESPACE = frozenset(" 　\t\r")
ITERATION_MARKS = frozenset("ゝゞヽヾ〃")


def _digit_or_latin(ch):
    return ("0" <= ch <= "9") or ("０" <= ch <= "９") or ("a" <= ch <= "z") or ("A" <= ch <= "Z") \
        or ("ａ" <= ch <= "ｚ") or ("Ａ" <= ch <= "Ｚ")


def _char_level(ch):
    return ch in SYMBOL_ONE_KEY or ch in WHITESPACE or _digit_or_latin(ch)


def kata_to_hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def _kana_only(s):
    from romaji_table import KANA_CHARS
    h = kata_to_hira(s)
    return bool(h) and all(c in KANA_CHARS for c in h)


def _word_char(ch):
    import unicodedata
    if _digit_or_latin(ch) or ch in ITERATION_MARKS:
        return False
    return unicodedata.category(ch).startswith("L") or ch == "〇"


def token_units(surface, reading, stats=None):
    """The units of one token as a string of hiragana, `ー` and `#` (one key for a digit, a Latin letter or a symbol),
    as build_segments.token_units: whitespace nothing; a token of characters typed one by one `#` per character that
    is not whitespace; a token of word characters with a kana reading, the reading in hiragana; any other token
    ('X'): the reading when it is kana only, otherwise `#` per character that is not whitespace (counted in stats)."""
    if surface == "" or all(ch in WHITESPACE for ch in surface):
        return ""
    if all(_char_level(ch) for ch in surface):
        return "#" * sum(1 for ch in surface if ch not in WHITESPACE)
    if all(_word_char(ch) for ch in surface) and _kana_only(reading):
        return kata_to_hira(reading)
    if _kana_only(reading):
        if stats is not None:
            stats["x_tokens_reading"] = stats.get("x_tokens_reading", 0) + 1
        return kata_to_hira(reading)
    if stats is not None:
        stats["x_tokens_per_char"] = stats.get("x_tokens_per_char", 0) + 1
    return "#" * sum(1 for ch in surface if ch not in WHITESPACE)


class Reader:
    """SudachiPy (config.json enja15.tools: SudachiPy 0.7.0, SudachiDict-core 20260723.1), split mode C."""

    def __init__(self):
        from sudachipy import Dictionary, SplitMode
        self._tok = Dictionary(dict="core").create()
        self._mode = SplitMode.C

    def tokens(self, s):
        return [(m.surface(), m.reading_form()) for m in self._tok.tokenize(s, self._mode)]


def text_segments(text, reader, stats=None):
    """Values of the translation's segments: split at 、。，． and line breaks; a segment of whitespace only is not a
    segment; the value is the standard romaji count (romaji_table.count_keys) of the units of its SudachiPy tokens,
    joined so that a small tsu sees the next unit across a token boundary."""
    from romaji_table import count_keys
    out = []
    for seg in TEXT_SPLIT.split(text.replace("\r\n", "\n")):
        if not seg.strip(" 　\t\r"):
            continue
        out.append(count_keys("".join(token_units(sf, rd, stats) for sf, rd in reader.tokens(seg))))
    return out
