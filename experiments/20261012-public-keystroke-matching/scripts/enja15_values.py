"""Check 5: counts of ENJA15 (sessions, translations, translators per source text, source texts per translator,
crossed or nested) and the kinds of the Type, Value and IMEtext values. No string of the logs or the translations is
written: values are written as their shape (a bracketed key name, one ASCII letter, ...) and strings as the set of
their character classes.

    python -I scripts/enja15_values.py --root raw/enja15 --out results/enja15_values.json
"""
import argparse
import json
import os
import re
import string
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

NAME = re.compile(r"^P(\d+)_T(\d+)$")
# Closed lists (review): a bracketed value is written verbatim only when it is a key name of the .NET Keys
# enumeration used by Translog-II, optionally after Ctrl+ or Shift+; a Type only when it is a known Type.
BRACKET = re.compile(r"^\[(?:(?:Ctrl|Shift|Alt)\+)?([A-Za-z0-9]{1,24})\]$")
NET_KEYS = {
    "Back", "Tab", "Return", "Enter", "Escape", "Space", "Delete", "Insert", "Home", "End", "Left", "Right", "Up",
    "Down", "PageUp", "PageDown", "Prior", "Next", "Capital", "CapsLock", "ControlKey", "ShiftKey", "Menu",
    "LControlKey", "RControlKey", "LShiftKey", "RShiftKey", "LMenu", "RMenu", "LWin", "RWin", "Apps", "ProcessKey",
    "None", "Decimal", "Subtract", "Add", "Multiply", "Divide", "Separator", "NumLock", "Scroll", "Pause", "Clear",
    "LaunchApplication1", "LaunchApplication2", "KanaMode", "KanjiMode", "IMEConvert", "IMENonconvert",
    "IMEModeChange", "IMEAccept", "Oemcomma", "OemPeriod", "OemMinus", "Oemplus", "OemQuestion", "Oemtilde",
    "OemOpenBrackets", "OemCloseBrackets", "OemPipe", "OemQuotes", "OemSemicolon", "OemBackslash", "Oem1", "Oem2",
    "Oem3", "Oem4", "Oem5", "Oem6", "Oem7", "Oem8", "Oem102", "C", "V", "X", "Z", "A"} \
    | {chr(c) for c in range(ord("A"), ord("Z") + 1)} | {"D%d" % i for i in range(10)} \
    | {"NumPad%d" % i for i in range(10)} | {"F%d" % i for i in range(1, 25)}
TYPES = {"IME", "insert", "delete", "navi", "return", "edit", "speech"}


def char_class(c):
    if c.isascii():
        if c.isalpha():
            return "ascii letter"
        if c.isdigit():
            return "ascii digit"
        if c.isspace():
            return "ascii space"
        return "ascii punct"
    n = unicodedata.name(c, "")
    for k in ("HIRAGANA", "KATAKANA", "CJK UNIFIED", "FULLWIDTH", "IDEOGRAPHIC"):
        if k in n:
            return k.lower()
    return "other " + unicodedata.category(c)


def classes(s):
    return "+".join(sorted({char_class(c) for c in s})) if s else "<empty>"


def shape(v, t=None):
    if v is None:
        return "<absent>"
    if v == "":
        return "<empty>"
    m = BRACKET.match(v)
    if m and m.group(1) in NET_KEYS and t != "insert":  # insert values are typed text
        return v
    if v.startswith("[") and v.endswith("]"):
        return "<bracketed value not in the key list: length %d>" % len(v)
    if len(v) == 1:
        if v.isascii() and v.isalpha():
            return "<one ascii letter>"
        if v.isascii() and v.isdigit():
            return "<one ascii digit>"
        if v in string.punctuation or v == " ":
            return repr(v)
        return "<one char: %s>" % char_class(v)
    return "<string: %s>" % classes(v)


def session(path):
    c = Counter()
    final = None
    has_ime_or_letter_insert = False
    for ev, el in ET.iterparse(path, events=("end",)):
        tag = el.tag
        if tag == "Key":
            t = el.get("Type")
            t = t if t in TYPES else "<other type>"
            v = el.get("Value")
            c["Type " + str(t)] += 1
            c["Type %s | Value %s" % (t, shape(v, t))] += 1
            if el.get("IMEtext") is not None:
                c["Type %s | IMEtext %s" % (t, classes(el.get("IMEtext")))] += 1
            if el.get("Text") is not None:
                c["Type %s | Text %s" % (t, classes(el.get("Text")))] += 1
            if el.get("Block") is not None:
                c["Type %s | has Block" % t] += 1
            if t == "IME" or (t == "insert" and v is not None and len(v) == 1 and v.isascii() and v.isalpha()):
                has_ime_or_letter_insert = True
        elif tag == "Mouse":
            c["Mouse | Value %s" % shape(el.get("Value"))] += 1
        elif tag == "System":
            c["System | Value %s" % shape(el.get("Value"))] += 1
        elif tag == "FinalTextUTF8":
            final = el.text or ""
        if tag in ("Key", "Eye", "Fix", "Mouse", "System", "CharPos"):
            el.clear()
    return c, final, has_ime_or_letter_insert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    xml_dir = os.path.join(args.root, "Translog-II")
    tot = Counter()
    by_text, by_person = defaultdict(set), defaultdict(set)
    excl = Counter()
    final_classes = Counter()
    for fn in sorted(os.listdir(xml_dir)):
        if not fn.endswith(".xml"):
            continue
        m = NAME.match(fn[:-4])
        person, text = m.group(1), m.group(2)
        c, final, ok = session(os.path.join(xml_dir, fn))
        tot.update(c)
        by_text[text].add(person)
        by_person[person].add(text)
        if final is None:
            excl["missing translation"] += 1
        elif not final.strip():
            excl["empty translation"] += 1
        elif not ok:
            excl["no Type=IME and no letter Type=insert"] += 1
        if final:
            final_classes[classes(final)] += 1
    per_person = Counter(len(v) for v in by_person.values())
    out = {"sessions": sum(len(v) for v in by_text.values()),
           "translators": len(by_person), "source_texts": len(by_text),
           "translators_per_source_text": {t: len(v) for t, v in sorted(by_text.items())},
           "source_texts_per_translator": dict(sorted(per_person.items())),
           "design": "crossed" if any(len(v) >= 2 for v in by_person.values()) else "nested",
           "excluded": dict(excl),
           "final_text_character_classes": dict(final_classes.most_common()),
           "key_values": dict(sorted(tot.items()))}
    out["translations_nonempty"] = out["sessions"] - excl["missing translation"] - excl["empty translation"]
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
