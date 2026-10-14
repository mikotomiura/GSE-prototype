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
NAV_KEYS = {"[Left]", "[Right]", "[Up]", "[Down]", "[Home]", "[End]", "[PageUp]", "[Next]"}
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
