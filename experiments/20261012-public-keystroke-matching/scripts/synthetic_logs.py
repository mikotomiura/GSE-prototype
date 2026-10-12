"""Synthetic keystroke logs for the pre-freeze check (preregistration.md, "公開の他の列から長さが戻らないかの検査").

No human data. An editor simulation writes rows with the KLiCKe columns ([V264] §2.1.5: event ID, down/up/pause/action
time, position, word count, text change, activity, and the pressed key) and keeps the true correspondence (which press
put each character of the final text there). The release forms of config.json "release_forms" are applied to the rows.

What is an assumption about the real logs (to be checked at check 2 after acquisition, not before):
- one row per key press or mouse operation; a paste, a cut, an undo and a drag are one row each;
- the position after a selection is the moving end of the selection ([V264] §2.1.5: "the endpoint of the selection");
- Control/Alt/Shift/Meta rows have action time 0 and up time = down time ([V264] §2.1.5 sets their operation time to 0);
- activity values and text change formats follow the Kaggle description [V265] (Input, Remove/Cut, Replace "a => b",
  Paste, Nonproduction, "Move From [a, b] To [c, d]", "NoChange");
- an undo removes the last typed word and is logged as Remove/Cut.

Three random streams make "twins": records that share the key stream (categories and times) but differ in hidden
choices (mouse targets, which word is copied, letters). Times depend only on the key stream unless the timing mode
says otherwise ("digraph": intervals depend on the letters; "drag": a drag lasts longer for a longer selection).
"""
import re

import numpy as np

LETTERS = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
NAV = {"ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", "PageUp", "PageDown"}
MOD = {"Shift", "Control", "Alt", "Meta", "CapsLock"}
MOUSE = {"Leftclick", "Rightclick", "Middleclick"}
CHAR_CATS = ("letter", "digit", "space", "punctuation", "enter")
SEP_CATS = ("space", "punctuation", "enter")

QWERTY_ROWS = ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"]


def category(key):
    """config.json key_categories from a pressed-key value."""
    if key == "Space":
        return "space"
    if key == "Backspace":
        return "backspace"
    if key == "Delete":
        return "delete"
    if key == "Enter":
        return "enter"
    if key in NAV:
        return "navigation"
    if key in MOD:
        return "modifier"
    if key in MOUSE:
        return "mouse"
    if len(key) == 1:
        if key.isalpha():
            return "letter"
        if key.isdigit():
            return "digit"
        return "punctuation"
    return "other"


def char_of_key(key):
    """The character a key types, or None."""
    if key == "Space":
        return " "
    if key == "Enter":
        return "\n"
    if len(key) == 1:
        return key
    return None


def key_of_char(c):
    return {" ": "Space", "\n": "Enter"}.get(c, c)


def word_lengths(text):
    """Text segments (preregistration.md 区間): runs of letters and digits, the value is the run length."""
    return [len(m) for m in re.findall(r"[A-Za-z0-9]+", text)]


def ws_word_count(text):
    return len(text.split())


class Editor:
    """A plain textarea: characters with the event ID that put them there, a cursor and an optional selection."""

    def __init__(self):
        self.chars = []  # [(char, origin)] origin = event ID of the insert, or ("paste", event ID)
        self.cursor = 0
        self.anchor = None  # selection = [min(anchor, cursor), max(...)) when anchor is not None
        self.clip = ""
        self.last_run = None  # (start, end) of the last typed word, for undo

    def text(self):
        return "".join(c for c, _ in self.chars)

    def sel(self):
        if self.anchor is None or self.anchor == self.cursor:
            return None
        return (min(self.anchor, self.cursor), max(self.anchor, self.cursor))

    def drop_sel(self):
        s = self.sel()
        self.anchor = None
        if s is None:
            return ""
        a, b = s
        removed = "".join(c for c, _ in self.chars[a:b])
        del self.chars[a:b]
        self.cursor = a
        return removed

    def line_bounds(self, pos):
        t = self.text()
        a = t.rfind("\n", 0, pos) + 1
        b = t.find("\n", pos)
        return a, (len(t) if b < 0 else b)


class Writer:
    """Generates one record. rng_k: key stream (structure, counts, times); rng_h: hidden choices; rng_l: letters."""

    def __init__(self, seed_keys, seed_hidden, seed_letters, timing="free", n_words=(60, 140), ops=None):
        self.k = np.random.default_rng(seed_keys)
        self.h = np.random.default_rng(seed_hidden)
        self.l = np.random.default_rng(seed_letters)
        self.timing = timing
        self.n_words = n_words
        self.ops = ops if ops is not None else DEFAULT_OPS
        self.ed = Editor()
        self.rows = []
        self.t = 1000
        self.prev_char = None

    # --- timing -------------------------------------------------------------------------------------------
    def gap(self, kind, c=None):
        base = {"char": 170, "word": 420, "sentence": 1600, "nav": 260, "mouse": 950, "mod": 140, "bs": 210}[kind]
        g = base * float(np.exp(self.k.normal(0, 0.35)))
        if self.timing == "digraph" and c is not None and self.prev_char is not None:
            g *= float(np.exp(digraph_offset(self.prev_char, c)))
        return max(15, int(round(g)))

    def hold(self, key, sel_len=0):
        if key in MOD:
            return 0
        if key in MOUSE:
            if self.timing == "drag" and sel_len:
                return 200 + 45 * sel_len + int(self.k.integers(0, 60))
            return 90 + int(self.k.integers(0, 60))
        return 60 + int(self.k.integers(0, 60))

    # --- rows ---------------------------------------------------------------------------------------------
    def row(self, key, activity="Nonproduction", text_change="NoChange", gap_kind="nav", c=None, sel_len=0):
        down = self.t + self.gap(gap_kind, c)
        hold = self.hold(key, sel_len)
        prev_down = self.rows[-1]["down_time"] if self.rows else down
        ed = self.ed
        r = {
            "event_id": len(self.rows) + 1, "down_time": down, "up_time": down + hold, "action_time": hold,
            "pause_time": down - prev_down, "down_event": key, "up_event": key, "activity": activity,
            "text_change": text_change, "cursor_position": ed.cursor, "word_count": ws_word_count(ed.text()),
        }
        self.rows.append(r)
        self.t = down
        if c is not None:
            self.prev_char = c
        return r

    def fix_last(self):
        """Position and word count after the editor state changed for the last row."""
        r = self.rows[-1]
        r["cursor_position"] = self.ed.cursor
        r["word_count"] = ws_word_count(self.ed.text())

    def type_char(self, c, gap_kind="char"):
        ed = self.ed
        eid = len(self.rows) + 1
        removed = ed.drop_sel()
        ed.chars.insert(ed.cursor, (c, eid))
        ed.cursor += 1
        if removed:
            self.row(key_of_char(c), "Replace", removed + " => " + c, gap_kind, c)
        else:
            self.row(key_of_char(c), "Input", c, gap_kind, c)
        self.fix_last()

    def backspace(self):
        ed = self.ed
        removed = ed.drop_sel()
        if not removed and ed.cursor > 0:
            removed = ed.chars[ed.cursor - 1][0]
            del ed.chars[ed.cursor - 1]
            ed.cursor -= 1
        self.row("Backspace", "Remove/Cut" if removed else "Nonproduction", removed or "NoChange", "bs")
        self.fix_last()

    def delete(self):
        ed = self.ed
        removed = ed.drop_sel()
        if not removed and ed.cursor < len(ed.chars):
            removed = ed.chars[ed.cursor][0]
            del ed.chars[ed.cursor]
        self.row("Delete", "Remove/Cut" if removed else "Nonproduction", removed or "NoChange", "bs")
        self.fix_last()

    def nav(self, key, shift=False):
        ed = self.ed
        if shift and ed.anchor is None:
            ed.anchor = ed.cursor
        if not shift:
            ed.anchor = None
        n = len(ed.chars)
        if key == "ArrowLeft":
            ed.cursor = max(0, ed.cursor - 1)
        elif key == "ArrowRight":
            ed.cursor = min(n, ed.cursor + 1)
        elif key == "Home":
            ed.cursor = ed.line_bounds(ed.cursor)[0]
        elif key == "End":
            ed.cursor = ed.line_bounds(ed.cursor)[1]
        elif key in ("ArrowUp", "ArrowDown"):
            a, b = ed.line_bounds(ed.cursor)
            col = ed.cursor - a
            if key == "ArrowUp":
                if a == 0:
                    ed.cursor = 0
                else:
                    pa, pb = ed.line_bounds(a - 1)
                    ed.cursor = min(pa + col, pb)
            else:
                if b >= n:
                    ed.cursor = n
                else:
                    na, nb = ed.line_bounds(b + 1)
                    ed.cursor = min(na + col, nb)
        self.row(key, gap_kind="nav")
        self.fix_last()

    def ctrl_end(self):
        self.row("Control", gap_kind="mod")
        self.ed.anchor = None
        self.ed.cursor = len(self.ed.chars)
        self.row("End", gap_kind="nav")

    def click(self, pos):
        self.ed.anchor = None
        self.ed.cursor = int(pos)
        self.row("Leftclick", gap_kind="mouse")

    def word_span(self, pos):
        t = self.ed.text()
        a = pos
        while a > 0 and t[a - 1].isalnum():
            a -= 1
        b = pos
        while b < len(t) and t[b].isalnum():
            b += 1
        return a, b

    def hidden_pos(self):
        n = len(self.ed.chars)
        return int(self.h.integers(0, n + 1)) if n else 0

    def dblclick_word(self):
        """Select the word at a hidden position (two click rows, the second selects)."""
        a, b = self.word_span(self.hidden_pos())
        self.click(a)
        self.ed.anchor, self.ed.cursor = a, b
        self.row("Leftclick", gap_kind="nav", sel_len=b - a)
        return a, b

    def drag_select(self):
        n = len(self.ed.chars)
        a = self.hidden_pos()
        span = int(self.h.integers(1, 12))
        b = min(n, a + span)
        if self.h.random() < 0.5:
            a, b = b, a
        self.ed.anchor, self.ed.cursor = a, b
        self.row("Leftclick", gap_kind="mouse", sel_len=abs(b - a))

    def shift_select_left(self, n):
        self.row("Shift", gap_kind="mod")
        for _ in range(n):
            self.nav("ArrowLeft", shift=True)

    def shortcut(self, letter):
        self.row("Control", gap_kind="mod")
        self.row(letter, gap_kind="char")

    def to_end(self):
        how = int(self.k.integers(0, 4))
        n = len(self.ed.chars)
        if how == 0:
            self.click(n)
        elif how == 1:
            self.ctrl_end()
        elif how == 2:
            while True:
                a, b = self.ed.line_bounds(self.ed.cursor)
                if b >= len(self.ed.chars):
                    break
                self.nav("ArrowDown")
            self.nav("End")
        else:
            self.row("PageDown", gap_kind="nav")
            self.ed.anchor = None
            self.ed.cursor = len(self.ed.chars)
            self.fix_last()

    def go_back(self):
        how = int(self.k.integers(0, 4))
        if how == 0:
            for _ in range(int(self.k.integers(1, 30))):
                self.nav("ArrowLeft")
        elif how == 1:
            self.click(self.hidden_pos())
        elif how == 2:
            self.nav("Home")
        else:
            self.nav("ArrowUp")

    # --- operations ---------------------------------------------------------------------------------------
    def type_word(self, w, first_gap="word", capital=False):
        start = self.ed.cursor
        if capital and w[0].isalpha():
            self.row("Shift", gap_kind="mod")
            w = w[0].upper() + w[1:]
        for i, c in enumerate(w):
            if self.k.random() < 0.03:
                m = int(self.k.integers(1, 3))
                for j in range(m):
                    self.type_char(LETTERS[int(self.l.integers(0, 26))], first_gap if (i == 0 and j == 0) else "char")
                for _ in range(m):
                    self.backspace()
                self.type_char(c, "char")
            else:
                self.type_char(c, first_gap if i == 0 else "char")
        self.ed.last_run = (start, self.ed.cursor)

    def rand_word(self, n=None):
        if n is None:
            n = int(min(12, 1 + self.k.geometric(0.22)))
        s = []
        for _ in range(n):
            s.append(DIGITS[int(self.l.integers(0, 10))] if self.k.random() < 0.02 else LETTERS[int(self.l.integers(0, 26))])
        return "".join(s)

    def op(self, kind):
        ed = self.ed
        if kind == "mid_insert":
            self.go_back()
            self.type_word(self.rand_word(), "word")
            self.type_char(" ")
            self.to_end()
        elif kind == "mid_delete":
            self.go_back()
            n = int(self.k.integers(1, 7))
            for _ in range(n):
                if self.k.random() < 0.5:
                    self.backspace()
                else:
                    self.delete()
            self.to_end()
        elif kind == "sel_delete":
            how = int(self.k.integers(0, 3))
            if how == 0:
                self.shift_select_left(int(self.k.integers(1, 10)))
            elif how == 1:
                self.dblclick_word()
            else:
                self.drag_select()
            if self.k.random() < 0.5:
                self.backspace()
            else:
                self.delete()
            self.to_end()
        elif kind == "replace":
            if self.k.random() < 0.5:
                self.dblclick_word()
            else:
                self.drag_select()
            self.type_word(self.rand_word(), "word")
            self.to_end()
        elif kind == "copy_paste":
            a, b = self.dblclick_word()
            ed.clip = ed.text()[a:b]
            self.shortcut("c")
            self.click(len(ed.chars))
            eid = len(self.rows) + 2  # the "v" row after the Control row
            for i, c in enumerate(ed.clip):
                ed.chars.insert(ed.cursor + i, (c, ("paste", eid)))
            ed.cursor += len(ed.clip)
            self.row("Control", gap_kind="mod")
            self.row("v", "Paste", ed.clip if ed.clip else "NoChange", "char")
            self.fix_last()
        elif kind == "cut":
            self.drag_select()
            removed = ed.drop_sel()
            ed.clip = removed
            self.row("Control", gap_kind="mod")
            self.row("x", "Remove/Cut" if removed else "Nonproduction", removed or "NoChange", "char")
            self.fix_last()
            self.to_end()
        elif kind == "undo":
            if ed.last_run and ed.last_run[1] == ed.cursor and ed.last_run[1] > ed.last_run[0]:
                a, b = ed.last_run
                removed = ed.text()[a:b]
                del ed.chars[a:b]
                ed.cursor = a
                ed.anchor = None
                self.row("Control", gap_kind="mod")
                self.row("z", "Remove/Cut", removed, "char")
                self.fix_last()
                ed.last_run = None
        elif kind == "drag_move":
            a, b = self.dblclick_word()
            if b > a:
                sub = ed.chars[a:b]
                del ed.chars[a:b]
                n = len(ed.chars)
                c = int(self.h.integers(0, n + 1))
                ed.chars[c:c] = sub
                ed.anchor = None
                ed.cursor = c + len(sub)
                self.row("Leftclick", "Move From [%d, %d] To [%d, %d]" % (a, b, c, c + len(sub)), "NoChange", "mouse",
                         sel_len=b - a)
                self.fix_last()
            self.to_end()

    def run(self):
        n_words = int(self.k.integers(*self.n_words))
        kinds = list(self.ops)
        probs = np.array([self.ops[x] for x in kinds])
        p_any = float(probs.sum())
        cap_next = False
        for i in range(n_words):
            if i > 3 and self.k.random() < p_any:
                self.op(kinds[int(self.k.choice(len(kinds), p=probs / p_any))])
            self.type_word(self.rand_word(), "word", capital=(i == 0 or cap_next or self.k.random() < 0.03))
            cap_next = False
            u = self.k.random()
            if u < 0.08:
                self.type_char("."), self.type_char("\n" if self.k.random() < 0.3 else " ", "sentence")
                cap_next = True
            elif u < 0.13:
                self.type_char(","), self.type_char(" ")
            elif i < n_words - 1:
                self.type_char(" ")
        self.type_char(".")
        return Record(self.rows, self.ed)


DEFAULT_OPS = {"mid_insert": 0.02, "mid_delete": 0.015, "sel_delete": 0.015, "replace": 0.01, "copy_paste": 0.01,
               "cut": 0.005, "undo": 0.01, "drag_move": 0.005}
NO_OPS = {}


def digraph_offset(a, b):
    """A fixed log-interval offset per character pair (the content-dependent timing of the "digraph" mode)."""
    h = (ord(a) * 131 + ord(b) * 31) % 97
    return (h / 96.0 - 0.5) * 0.9


class Record:
    def __init__(self, rows, ed):
        self.rows = rows
        self.final = ed.text()
        self.origin = [o for _, o in ed.chars]

    def surviving(self):
        """{event ID: final character index} for presses whose character is in the final text (pastes excluded)."""
        return {o: i for i, o in enumerate(self.origin) if not isinstance(o, tuple)}


# --- segments ---------------------------------------------------------------------------------------------------

def shortcut_flags(cats, keys=None, modifier_arms=True):
    """A letter or digit press right after a Control or Meta press (other modifiers skipped) is a shortcut.

    The preregistration says "while Control or Meta is held"; with the modifier action time set to 0 ([V264] §2.1.5)
    the held state is not in the times, so the rule is applied to the next non-modifier press. Category columns do
    not say which modifier it was; a modifier press counts as Control/Meta only when keys are known (R0, R1, R5, R6),
    otherwise any modifier other than a Shift-like one cannot be told apart, so every modifier is treated as a
    possible Control (see notes.md)."""
    flags = [False] * len(cats)
    armed = False
    for i, c in enumerate(cats):
        if c == "modifier":
            if keys is None:
                armed = modifier_arms
            elif keys[i] in ("Control", "Meta"):
                armed = True
            continue
        if armed and c in ("letter", "digit", "char"):
            flags[i] = True
        armed = False
    return flags


def record_segments(cats, keys=None, merge_char=False, modifier_arms=True):
    """Record segments (preregistration.md 区間): [(value, [row indices])]. A trailing open segment is kept if it has
    a counted press. merge_char: the R3-u 'char' category has no separator (returns one segment)."""
    sc = shortcut_flags(cats, keys, modifier_arms)
    segs = []
    v, idx, counted = 0, [], False
    for i, c in enumerate(cats):
        if sc[i]:
            continue
        if c in ("letter", "digit") or (merge_char and c == "char"):
            v += 1
            idx.append(i)
            counted = True
        elif c == "backspace":
            v -= 1
            idx.append(i)
            counted = True
        elif c in SEP_CATS:
            segs.append((v, idx))
            v, idx, counted = 0, [], False
    if counted:
        segs.append((v, idx))
    return segs


# --- release forms ----------------------------------------------------------------------------------------------

def mask_q(s):
    return re.sub(r"[A-Za-z0-9]", "q", s)


def keymap_row(r, f):
    out = dict(r)
    out["down_event"] = f(r["down_event"])
    out["up_event"] = f(r["up_event"])
    return out


def form_R0(rec):
    return [dict(r) for r in rec.rows]


def form_R1(rec):
    out = []
    for r in rec.rows:
        o = keymap_row(r, lambda k: "q" if len(k) == 1 and k.isalnum() else k)
        if not o["activity"].startswith("Move From"):
            o["text_change"] = mask_q(r["text_change"]) if r["text_change"] != "NoChange" else "NoChange"
        del o["pause_time"]
        out.append(o)
    return out


R2_COLS = ("event_id", "down_time", "up_time", "action_time", "down_event", "up_event", "cursor_position", "word_count")
R3_COLS = ("event_id", "down_time", "up_time", "action_time", "down_event", "up_event")


def form_R2(rec):
    return [{c: (category(r[c]) if c in ("down_event", "up_event") else r[c]) for c in R2_COLS} for r in rec.rows]


def form_R3(rec, mutate=None):
    cols = R3_COLS + (("cursor_position",) if mutate == "r3_keep_position" else ())
    return [{c: (category(r[c]) if c in ("down_event", "up_event") else r[c]) for c in cols} for r in rec.rows]


def form_R3u(rec):
    out = form_R3(rec)
    for o in out:
        for c in ("down_event", "up_event"):
            if o[c] in CHAR_CATS:
                o[c] = "char"
    return out


def form_R3t(rec, w):
    out = form_R3(rec)
    for o in out:
        o["down_time"] = (o["down_time"] // w) * w
        o["up_time"] = (o["up_time"] // w) * w
        o["action_time"] = o["up_time"] - o["down_time"]
    return out


def form_R7(rec, p, rng):
    keep = rng.random(len(rec.rows)) >= p
    out = []
    for r, k in zip(form_R3(rec), keep):
        if k:
            o = dict(r)
            o["event_id"] = len(out) + 1
            out.append(o)
    return out, keep


def form_R4(rec, w):
    cats = [category(r["down_event"]) for r in rec.rows]
    keys = [r["down_event"] for r in rec.rows]
    return [v // w for v, _ in record_segments(cats, keys)]


def neighbours(c):
    for ri, row in enumerate(QWERTY_ROWS):
        j = row.find(c.lower())
        if j < 0:
            continue
        out = []
        for dj in (-1, 1):
            if 0 <= j + dj < len(row):
                out.append(row[j + dj])
        for dr in (-1, 1):
            if 0 <= ri + dr < len(QWERTY_ROWS):
                r2 = QWERTY_ROWS[ri + dr]
                for jj in (j - 1, j, j + 1) if ri + dr else (j, j + 1):
                    if 0 <= jj < len(r2):
                        out.append(r2[jj])
        return sorted(set(out) - {c.lower()})
    return [c]


def form_R5(rec, rng):
    sub = lambda c: (neighbours(c)[int(rng.integers(0, len(neighbours(c))))] if c.isalnum() else c)
    out = []
    for r in rec.rows:
        o = dict(r)
        del o["pause_time"]
        if len(r["down_event"]) == 1 and r["down_event"].isalnum():
            s = sub(r["down_event"])
            o["down_event"] = o["up_event"] = s
            if r["activity"] == "Input":
                o["text_change"] = s
            elif r["activity"] == "Replace":
                a, b = r["text_change"].split(" => ")
                o["text_change"] = "".join(sub(c) for c in a) + " => " + s
            elif r["activity"] in ("Paste", "Remove/Cut") and r["text_change"] != "NoChange":
                o["text_change"] = "".join(sub(c) for c in r["text_change"])
        elif r["activity"] in ("Remove/Cut", "Replace") and r["text_change"] != "NoChange":
            o["text_change"] = "".join(sub(c) if c not in " =>" else c for c in r["text_change"])
        out.append(o)
    return out


def form_R6(rec, rng):
    cats = [category(r["down_event"]) for r in rec.rows]
    keys = [r["down_event"] for r in rec.rows]
    out = [dict(r) for r in rec.rows]
    for o in out:
        del o["pause_time"]
    for _, idx in record_segments(cats, keys):
        al = [i for i in idx if cats[i] in ("letter", "digit") and rec.rows[i]["activity"] == "Input"]
        perm = rng.permutation(len(al))
        for i, j in zip(al, perm):
            k = rec.rows[al[j]]["down_event"]
            out[i]["down_event"] = out[i]["up_event"] = out[i]["text_change"] = k
    return out
