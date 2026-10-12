"""Reconstructions of the final draft from a released form (preregistration.md, attackers A1 and A1').

- a1_text: A1 for forms with text_change and position (R0, R1, R5, R6), the [V279] type of reconstruction.
- a1_r2: A1 for R2 (categories and position only).
- a1prime: A1' (categories only), the editor replay; uncertain moves put the cursor at the end.
Each returns the final draft as a list of items (type, row index); type 'a' letter/digit, 's' space/punctuation,
'n' Enter, 'c' an R3-u char; or a string for a1_text.
"""
import re

from synthetic_logs import SEP_CATS, record_segments, shortcut_flags  # noqa: F401

MOVE = re.compile(r"Move From \[(\d+), (\d+)\] To \[(\d+), (\d+)\]")


def a1_text(rows):
    t = ""
    for r in rows:
        act, tc, pos = r["activity"], r["text_change"], r["cursor_position"]
        if act == "Input" or act == "Paste":
            if tc == "NoChange":
                continue
            s = pos - len(tc)
            t = t[:s] + tc + t[s:]
        elif act == "Remove/Cut":
            if tc == "NoChange":
                continue
            t = t[:pos] + t[pos + len(tc):]
        elif act == "Replace":
            a, b = tc.split(" => ")
            s = pos - len(b)
            t = t[:s] + b + t[s + len(a):]
        elif act.startswith("Move From"):
            a, b, c, _ = map(int, MOVE.match(act).groups())
            sub = t[a:b]
            t = t[:a] + t[b:]
            t = t[:c] + sub + t[c:]
    return t


def item_type(cat):
    if cat in ("letter", "digit"):
        return "a"
    if cat == "enter":
        return "n"
    if cat == "char":
        return "c"
    return "s"


def a1prime(cats, uncertain_home_end=False, modifier_arms=True):
    """Editor replay of the category column. Shortcuts (the next letter/digit/char after a modifier) are ignored."""
    sc = shortcut_flags(cats, None, modifier_arms)
    doc, cur = [], 0
    for i, c in enumerate(cats):
        if sc[i]:
            continue
        if c in ("letter", "digit", "char") + SEP_CATS:
            doc.insert(cur, (item_type(c), i))
            cur += 1
        elif c == "backspace":
            if cur > 0:
                del doc[cur - 1]
                cur -= 1
        elif c == "delete":
            if cur < len(doc):
                del doc[cur]
        elif c == "navigation_left":
            cur = max(0, cur - 1)
        elif c == "navigation_right":
            cur = min(len(doc), cur + 1)
        elif c == "navigation_home":
            if uncertain_home_end:
                cur = len(doc)
            else:
                while cur > 0 and doc[cur - 1][0] != "n":
                    cur -= 1
        elif c == "navigation_end":
            if uncertain_home_end:
                cur = len(doc)
            else:
                while cur < len(doc) and doc[cur][0] != "n":
                    cur += 1
        elif c in ("navigation", "mouse"):
            cur = len(doc)
    return doc


def nav_detail(cats, keys):
    """Released categories do not tell ArrowLeft from ArrowUp. The preregistration's A1' uses the key names of the
    navigation presses (left/right, Home, End, the rest uncertain); in R3 those names are not in the category column.
    This helper is used only where keys are given; see notes.md (the category list needs navigation sub-categories)."""
    out = []
    for c, k in zip(cats, keys):
        if c == "navigation":
            out.append({"ArrowLeft": "navigation_left", "ArrowRight": "navigation_right", "Home": "navigation_home",
                        "End": "navigation_end"}.get(k, "navigation"))
        else:
            out.append(c)
    return out


def a1_r2(cats, positions, modifier_arms=True):
    """A1 on R2: categories and the position after each row. A selection is only visible through the position."""
    sc = shortcut_flags(cats, None, modifier_arms)
    doc, prev = [], 0
    for i, (c, pos) in enumerate(zip(cats, positions)):
        if sc[i]:
            # paste (pos jumps right) or cut/undo (pos may move left); the length is the position difference
            if pos > prev:
                doc[prev:prev] = [("a", i)] * (pos - prev)
            elif pos < prev:
                del doc[pos:prev]
        elif c in ("letter", "digit") + SEP_CATS:
            s = pos - 1
            if s < prev:  # typed over a selection [s, prev)
                del doc[s:prev]
            s = min(s, len(doc))
            doc.insert(max(s, 0), (item_type(c), i))
        elif c == "backspace" or c == "delete":
            if c == "backspace" and pos == prev - 1:
                del doc[pos:prev]
            elif pos < prev:
                del doc[pos:prev]
            elif c == "delete" and pos == prev and pos < len(doc):
                del doc[pos]
        prev = pos
        if prev > len(doc):  # a position beyond the believed length reveals hidden characters
            doc.extend([("a", i)] * (prev - len(doc)))
    return doc


def lengths_of_items(doc):
    out, n = [], 0
    for t, _ in doc:
        if t == "a":
            n += 1
        else:
            if n:
                out.append(n)
            n = 0
    if n:
        out.append(n)
    return out
