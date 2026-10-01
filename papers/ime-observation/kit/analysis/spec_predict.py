#!/usr/bin/env python3
# kit: selftest
"""The observer's specified behaviour applied to what was sent: the session rows the macOS observer
should write if it follows its own rules exactly, computed from the executor's record (the oracle)
and the plan. The observation is not read. Uses only the Python standard library.

  spec_predict.py --oracle ORACLE --plan PLAN [--keymap KEYMAP.json] --out OUT.json
  spec_predict.py --selftest

Why this exists. On macOS the observer infers each conversion session from key presses, so some
disagreements with the ground truth follow from its rules alone and can be predicted before any
observation is read (for example, Backspace keeps a session open, and Tab or a punctuation key
closes it). The prediction is the reference of a two-stage comparison:
  - ground truth against prediction: how well the observer's rules describe what the input method
    did (the validity of the inference rules);
  - prediction against observation: whether the observer carries out its rules faithfully (missed
    presses, timing, implementation).
It also marks, for every trial, whether the session it started reaches the 20-second cut-off, so
that the primary agreement estimates can be computed over the trials whose sessions the observer is
specified to report.

The rules mirror the observer's source (the selftest compares them with it, so a change on either
side turns the selftest red):
  - kit/logger/src/driver_macos/keymap.rs (macos_vk_to_vk): the macOS key code becomes a virtual-key
    code; a code with no explicit entry passes through unchanged;
  - kit/logger/src/driver_macos.rs (handle_key): an input-mode key first updates the open flag; only
    presses drive the session machine;
  - kit/logger/src/input/ime_mode.rs: Eisu sets the flag to closed, Kana to open;
  - kit/logger/src/input/ime_compose.rs (step / apply / finish):

    | virtual key                  | effect (while Japanese input is on)                              |
    |------------------------------|------------------------------------------------------------------|
    | 0x30-0x39, 0x41-0x5A         | candidate window off; opens a session if none is open            |
    | 0x20 (Space)                 | candidate window on, if a session is open                        |
    | 0x0D (Return)                | closes the session, committed                                    |
    | 0x1B (Escape)                | closes the session, abandoned                                    |
    | 0x08 (Backspace)             | candidate window off; the session stays open                     |
    | 0x25-0x28 (arrows)           | nav + 1, if a session is open                                    |
    | >= 0xF0, or 0x19 (mode keys) | nothing                                                          |
    | anything else                | closes the session, committed                                    |

    While Japanese input is off, every press closes an open session as committed. Before any of
    this, a press that comes 20,000 ms or more after the session opened cuts the session off without
    a row, and the press is then applied to an empty state (so a letter or digit opens a new
    session).

What the oracle does not record, and how it is modelled:
  - The runner switches the input method to Japanese before every block (its focus command presses
    the Kana key). This is modelled as a Kana press at the block's block_begin time.
  - A marker row is a press of the block's marker key (the plan's "marker" list, by "seq").
  - Pseudo-keys that send no key event (focus_away, focus_back) are skipped.
  - Modifier keys are not delivered to the observer's event tap and are not modelled: a plan that
    sends one as a key (for example "shift") is refused.
Times are the oracle's wall-clock times, taken immediately before each dispatch. A predicted row's
interval is [start, end] on that clock; the observer's own rows carry its clock and the time the row
was collected, which the comparison with the observation has to allow for.

Exit: 0 = written / 1 = selftest failure / 2 = usage error, unreadable or invalid input
"""
import argparse
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import gt_sessions  # noqa: E402  oracle parser

LIMIT_MS = 20000
DEFAULT_KEYMAP = os.path.join(_HERE, "..", "emit", "keymap_macos.json")
PSEUDO_KEYS = ("focus_away", "focus_back")
MODIFIER_KEYS = ("shift",)

# macos_vk_to_vk's explicit entries (macOS key code -> virtual-key code). Any other code passes
# through unchanged. The selftest compares this table with kit/logger/src/driver_macos/keymap.rs.
MAC_TO_VK = {
    0x00: 0x41, 0x01: 0x53, 0x02: 0x44, 0x03: 0x46, 0x04: 0x48, 0x05: 0x47, 0x06: 0x5A, 0x07: 0x58,
    0x08: 0x43, 0x09: 0x56, 0x0B: 0x42, 0x0C: 0x51, 0x0D: 0x57, 0x0E: 0x45, 0x0F: 0x52, 0x10: 0x59,
    0x11: 0x54, 0x12: 0x31, 0x13: 0x32, 0x14: 0x33, 0x15: 0x34, 0x16: 0x36, 0x17: 0x35, 0x18: 0xBB,
    0x19: 0x39, 0x1A: 0x37, 0x1B: 0xBD, 0x1C: 0x38, 0x1D: 0x30, 0x1E: 0xDD, 0x1F: 0x4F, 0x20: 0x55,
    0x21: 0xDB, 0x22: 0x49, 0x23: 0x50, 0x24: 0x0D, 0x25: 0x4C, 0x26: 0x4A, 0x27: 0xDE, 0x28: 0x4B,
    0x29: 0xBA, 0x2A: 0xDC, 0x2B: 0xBC, 0x2C: 0xBF, 0x2D: 0x4E, 0x2E: 0x4D, 0x2F: 0xBE, 0x30: 0x09,
    0x31: 0x20, 0x32: 0xC0, 0x33: 0x08, 0x35: 0x1B, 0x60: 0x74, 0x61: 0x75, 0x62: 0x76, 0x63: 0x72,
    0x64: 0x77, 0x65: 0x78, 0x66: 0xF0, 0x67: 0x7A, 0x68: 0xF2, 0x6D: 0x79, 0x6F: 0x7B, 0x75: 0x2E,
    0x76: 0x73, 0x78: 0x71, 0x7A: 0x70, 0x7B: 0x25, 0x7C: 0x27, 0x7D: 0x28, 0x7E: 0x26, 0x90: 0xF2,
    0x91: 0xF1,
}
MAC_KANA = 0x68
VK_KANJI = 0x19
VK_DBE_ALPHANUMERIC, VK_DBE_KATAKANA, VK_DBE_HIRAGANA, VK_DBE_SBCSCHAR, VK_DBE_DBCSCHAR = 0xF0, 0xF1, 0xF2, 0xF3, 0xF4

ALNUM, SPACE, ENTER, ESC, BACK, ARROW, MODE, OTHER = "alnum", "space", "enter", "esc", "back", "arrow", "mode", "other"


class InputError(ValueError):
    """An input the prediction cannot use (exit 2)."""


def mac_to_vk(code):
    """macos_vk_to_vk: an explicit entry, otherwise the code itself."""
    return MAC_TO_VK.get(code, code)


def vk_class(vk):
    """The branch of the session machine (apply) that a virtual-key code takes."""
    if 0x30 <= vk <= 0x39 or 0x41 <= vk <= 0x5A:
        return ALNUM
    if vk == 0x20:
        return SPACE
    if vk == 0x0D:
        return ENTER
    if vk == 0x1B:
        return ESC
    if vk == 0x08:
        return BACK
    if 0x25 <= vk <= 0x28:
        return ARROW
    if vk >= 0xF0 or vk == VK_KANJI:
        return MODE
    return OTHER


def mode_after(vk, press, is_open):
    """The open flag after a key transition (ime_open_after_press / ime_open_after_release)."""
    if press:
        if vk in (VK_DBE_ALPHANUMERIC, VK_DBE_SBCSCHAR):
            return False
        if vk in (VK_DBE_KATAKANA, VK_DBE_HIRAGANA, VK_DBE_DBCSCHAR):
            return True
        if vk == VK_KANJI:
            return not is_open
        return is_open
    if vk in (VK_DBE_KATAKANA, VK_DBE_HIRAGANA, VK_DBE_DBCSCHAR):
        return True
    if vk in (VK_DBE_ALPHANUMERIC, VK_DBE_SBCSCHAR):
        return False
    return is_open


class _Machine(object):
    """The session machine and the open flag, fed one key transition at a time."""

    def __init__(self, limit_ms=LIMIT_MS):
        self.limit_ms = limit_ms
        self.is_open = False
        self.start = None
        self.start_trial = None
        self.active = False
        self.nav = 0
        self.sessions = []

    def _close(self, t, trial, end, abandon=False):
        if self.start is None:
            return
        self.sessions.append({"start_wall_ms": self.start, "end_wall_ms": t, "dwell_ms": t - self.start,
                              "nav": self.nav, "abandon": abandon, "end": end,
                              "start_trial": self.start_trial, "end_trial": trial})
        self.start, self.start_trial, self.active, self.nav = None, None, False, 0

    def _apply(self, vk, t, trial):
        if not self.is_open:
            self._close(t, trial, "row")
            return
        c = vk_class(vk)
        if c == ALNUM:
            self.active = False
            if self.start is None:
                self.start, self.start_trial, self.nav = t, trial, 0
        elif c == SPACE:
            if self.start is not None and not self.active:
                self.active = True
        elif c == ENTER:
            self._close(t, trial, "row")
        elif c == ESC:
            self._close(t, trial, "row", abandon=True)
        elif c == BACK:
            self.active = False
        elif c == ARROW:
            if self.start is not None:
                self.nav += 1
        elif c == MODE:
            pass
        else:
            self._close(t, trial, "row")

    def key(self, vk, press, t, trial):
        """handle_key: the open flag first, then (presses only) the cut-off and the transition."""
        self.is_open = mode_after(vk, press, self.is_open)
        if not press:
            return
        if self.start is not None and t - self.start >= self.limit_ms:
            self._close(t, trial, "truncated")
        self._apply(vk, t, trial)

    def finish(self):
        """A session still open when the record ends."""
        if self.start is not None:
            self.sessions.append({"start_wall_ms": self.start, "end_wall_ms": None, "dwell_ms": None,
                                  "nav": self.nav, "abandon": False, "end": "open",
                                  "start_trial": self.start_trial, "end_trial": None})


def load_keymap(path):
    """The emitter's key map (key name -> macOS key code)."""
    try:
        with open(path, "rb") as f:
            km = json.loads(f.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        raise InputError("keymap: cannot read %s (%s)" % (path, e))
    if not isinstance(km, dict):
        raise InputError("keymap: not an object")
    out = {}
    for k, v in km.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            raise InputError("keymap: %r is not a key code" % k)
        out[k] = v
    return out


def parse_plan(data):
    """The plan's header (os) and each block's marker keys: {"os", "sha256", "markers": {block_id: [name]}}."""
    if not isinstance(data, bytes):
        raise InputError("plan: not bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError("plan: not UTF-8")
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if not lines:
        raise InputError("plan: empty file")
    try:
        rows = [json.loads(ln) for ln in lines]
    except ValueError as e:
        raise InputError("plan: a line is not JSON (%s)" % e)
    hdr = rows[0]
    if not isinstance(hdr, dict) or hdr.get("kind") != "header" or hdr.get("format") != "plan/1":
        raise InputError("plan: line 1 is not a plan/1 header")
    markers = {}
    for r in rows[1:]:
        if isinstance(r, dict) and r.get("kind") == "block":
            m = r.get("marker")
            if not isinstance(m, list) or not all(isinstance(x, str) for x in m):
                raise InputError("plan: block %r has no marker list" % r.get("block_id"))
            markers[r.get("block_id")] = m
    return {"os": hdr.get("os"), "sha256": hashlib.sha256(data).hexdigest(), "markers": markers}


def _code(name, keymap, where):
    if name in MODIFIER_KEYS:
        raise InputError("%s: modifier key %r sent as a key is not modelled" % (where, name))
    if name not in keymap:
        raise InputError("%s: key %r is not in the emitter's key map" % (where, name))
    return keymap[name]


def predict_rows(oracle, plan, keymap, limit_ms=LIMIT_MS):
    """Feeds the oracle's key transitions to the machine. Returns the list of predicted sessions in
    time order. oracle is gt_sessions.parse_oracle's output; plan is parse_plan's output."""
    m = _Machine(limit_ms)
    for n, row in enumerate(oracle["rows"]):
        kind, t = row["kind"], row["t_wall_ms"]
        where = "oracle row %d" % (n + 1)
        if kind == "block_begin":
            m.key(MAC_TO_VK[MAC_KANA], True, t, None)
            m.key(MAC_TO_VK[MAC_KANA], False, t, None)
        elif kind == "marker":
            names = plan["markers"].get(row.get("block_id"))
            seq = row.get("seq")
            if names is None or not isinstance(seq, int) or isinstance(seq, bool) or not 0 <= seq < len(names):
                raise InputError("%s: marker seq %r has no key in the plan's block %r" % (where, seq, row.get("block_id")))
            vk = mac_to_vk(_code(names[seq], keymap, where))
            m.key(vk, True, t, None)
            m.key(vk, False, t, None)
        elif kind == "sent":
            name = row.get("key")
            if not isinstance(name, str) or not isinstance(row.get("down"), bool):
                raise InputError("%s: a sent row needs key and down" % where)
            if name in PSEUDO_KEYS:
                continue
            m.key(mac_to_vk(_code(name, keymap, where)), row["down"], t, row.get("trial_id"))
    m.finish()
    return m.sessions


def summarise_trials(sessions, trial_ids):
    """Per trial: the predicted sessions it started, whether one of them reaches the cut-off (long),
    whether one ends after the trial (carried_out), and how many it started (split when > 1)."""
    out = dict((tid, {"sessions": [], "long": False, "carried_out": False}) for tid in trial_ids)
    for i, s in enumerate(sessions):
        tid = s["start_trial"]
        if tid not in out:
            continue
        d = out[tid]
        d["sessions"].append(i)
        if s["end"] == "truncated":
            d["long"] = True
        if s["end_trial"] != tid:
            d["carried_out"] = True
    for d in out.values():
        d["n_started"] = len(d["sessions"])
    return out


def as_obs_rows(sessions):
    """The predicted rows in the observation's row shape (t = end, dwell_ms, nav, abandon): only the
    sessions the observer is specified to report (not cut off, not open at the end)."""
    return [{"type": "ime_shadow", "t": s["end_wall_ms"], "dwell_ms": s["dwell_ms"], "nav": s["nav"],
             "abandon": s["abandon"]} for s in sessions if s["end"] == "row"]


def predict(oracle_bytes, plan_bytes, keymap, limit_ms=LIMIT_MS):
    """The CLI's core (bytes in, an output dict out). Identical input always yields an identical dict."""
    plan = parse_plan(plan_bytes)
    if plan["os"] != "macos":
        raise InputError("plan: the prediction models the macOS observer only (plan os is %r)" % (plan["os"],))
    try:
        oracle = gt_sessions.parse_oracle(oracle_bytes)
    except gt_sessions.InputError as e:
        raise InputError(str(e))
    want = oracle["plan_sha256"]
    if not isinstance(want, str) or want.lower() != plan["sha256"]:
        raise InputError("plan: SHA-256 does not match the oracle header's plan_sha256 (unrelated plan)")
    sessions = predict_rows(oracle, plan, keymap, limit_ms)
    trials = summarise_trials(sessions, [t["trial_id"] for t in oracle["trials"]])
    counts = {"row": 0, "truncated": 0, "open": 0}
    for s in sessions:
        counts[s["end"]] += 1
    return {"format": "spec_predict/1", "limit_ms": limit_ms,
            "inputs_sha256": {"oracle": hashlib.sha256(oracle_bytes).hexdigest(), "plan": plan["sha256"]},
            "counts": counts,
            "trials": {"n": len(trials), "n_long": sum(1 for d in trials.values() if d["long"]),
                       "n_carried_out": sum(1 for d in trials.values() if d["carried_out"]),
                       "n_split": sum(1 for d in trials.values() if d["n_started"] > 1),
                       "n_none": sum(1 for d in trials.values() if d["n_started"] == 0),
                       "by_trial": trials},
            "sessions": sessions}


def render(out):
    return (json.dumps(out, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


# ---------------------------------------------------------------- selftest

def _run(events, limit_ms=LIMIT_MS, open_at=0):
    """events: [(t, name_or_vk, press_or_None)]; a name is a key class shortcut for readability."""
    names = {"a": 0x41, "k": 0x4B, "1": 0x31, "space": 0x20, "enter": 0x0D, "esc": 0x1B, "bs": 0x08,
             "left": 0x25, "right": 0x27, "tab": 0x09, "minus": 0xBD, "kana": 0xF2, "eisu": 0xF0, "f1": 0x70}
    m = _Machine(limit_ms)
    if open_at is not None:
        m.key(0xF2, True, open_at, None)
    for t, k, trial in events:
        vk = names[k] if isinstance(k, str) else k
        m.key(vk, True, t, trial)
        m.key(vk, False, t, trial)
    m.finish()
    return m.sessions


def _one(sessions):
    return [(s["start_wall_ms"], s["end_wall_ms"], s["nav"], s["abandon"], s["end"]) for s in sessions]


def _case_rules():
    f = []
    s = _one(_run([(10, "k", "t1"), (20, "a", "t1"), (30, "space", "t1"), (40, "enter", "t1")]))
    if s != [(10, 40, 0, False, "row")]:
        f.append("Return should commit a session that starts at the first letter: %r" % s)
    s = _one(_run([(10, "k", "t1"), (30, "space", "t1"), (40, "esc", "t1")]))
    if s != [(10, 40, 0, True, "row")]:
        f.append("Escape should abandon: %r" % s)
    s = _one(_run([(10, "k", "t1"), (20, "space", "t1"), (25, "a", "t1"), (30, "space", "t1"), (40, "enter", "t1")]))
    if s != [(10, 40, 0, False, "row")]:
        f.append("typing during candidates should keep one session: %r" % s)
    s = _one(_run([(10, "k", "t1"), (20, "bs", "t1"), (30, "bs", "t1"), (5000, "a", "t2"), (5100, "enter", "t2")]))
    if s != [(10, 5100, 0, False, "row")]:
        f.append("Backspace should keep the session open into the next trial: %r" % s)
    for other in ("tab", "minus", "f1"):
        s = _one(_run([(10, "k", "t1"), (20, other, "t1"), (30, "a", "t1"), (40, "enter", "t1")]))
        if s != [(10, 20, 0, False, "row"), (30, 40, 0, False, "row")]:
            f.append("%s should close as committed and the next letter should open a new session: %r" % (other, s))
    s = _one(_run([(10, "k", "t1"), (20, "eisu", "t1"), (30, "a", "t1"), (40, "enter", "t1")]))
    if s != [(10, 20, 0, False, "row")]:
        f.append("leaving Japanese input should close as committed and nothing should open while off: %r" % s)
    s = _one(_run([(10, "enter", None), (20, "esc", None), (30, "tab", None)]))
    if s:
        f.append("terminating keys outside a session should produce nothing: %r" % s)
    s = _one(_run([(10, "k", "t1"), (20, "enter", "t1")], open_at=None))
    if s:
        f.append("nothing should be produced while Japanese input is off: %r" % s)
    s = _one(_run([(5, "left", None), (10, "k", "t1"), (20, "right", "t1"), (25, "right", "t1"), (30, "enter", "t1"),
                   (40, "left", None), (50, "a", "t2"), (60, "enter", "t2")]))
    if s != [(10, 30, 2, False, "row"), (50, 60, 0, False, "row")]:
        f.append("arrows should count only inside a session and not leak into the next: %r" % s)
    s = _one(_run([(10, "k", "t1"), (20, "kana", "t1"), (30, "enter", "t1")]))
    if s != [(10, 30, 0, False, "row")]:
        f.append("an input-mode key should be transparent while Japanese input is on: %r" % s)
    s = _one(_run([(10, "space", "t1"), (20, "enter", "t1")]))
    if s:
        f.append("Space alone should not open a session: %r" % s)
    return f


def _case_cutoff():
    f = []
    s = _one(_run([(100, "k", "t1"), (100 + LIMIT_MS - 1, "enter", "t1")]))
    if s != [(100, 100 + LIMIT_MS - 1, 0, False, "row")]:
        f.append("a session just under the cut-off should still produce a row: %r" % s)
    s = _one(_run([(100, "k", "t1"), (100 + LIMIT_MS, "enter", "t1")]))
    if s != [(100, 100 + LIMIT_MS, 0, False, "truncated")]:
        f.append("a session that reaches the cut-off should be cut off and the Return applied to an empty state: %r" % s)
    s = _one(_run([(100, "k", "t1"), (100 + LIMIT_MS + 5, "1", "t1"), (100 + LIMIT_MS + 50, "enter", "t1")]))
    if s != [(100, 100 + LIMIT_MS + 5, 0, False, "truncated"), (100 + LIMIT_MS + 5, 100 + LIMIT_MS + 50, 0, False, "row")]:
        f.append("a digit after the cut-off should open a fresh session (a fragment row): %r" % s)
    s = _one(_run([(100, "k", "t1"), (100 + LIMIT_MS + 5, "eisu", "t1")]))
    if s != [(100, 100 + LIMIT_MS + 5, 0, False, "truncated")]:
        f.append("a mode key after the cut-off should cut off and produce nothing more: %r" % s)
    return f


def _case_keymap():
    f = []
    if vk_class(mac_to_vk(0x4F)) != ALNUM or vk_class(mac_to_vk(0x50)) != ALNUM:
        f.append("an unmapped code that passes through into the letter range should count as a letter")
    if vk_class(mac_to_vk(0x69)) != OTHER:
        f.append("F13 (passes through as 0x69) should close a session")
    if vk_class(mac_to_vk(0x30)) != OTHER or vk_class(mac_to_vk(0x1B)) != OTHER:
        f.append("Tab and Minus should close a session")
    if mode_after(0xF0, True, True) is not False or mode_after(0xF2, True, False) is not True:
        f.append("Eisu should close and Kana should open the input mode")
    if mode_after(VK_KANJI, True, False) is not True or mode_after(VK_KANJI, False, False) is not False:
        f.append("the Kanji key should toggle on press only")
    return f


def _source(rel):
    with open(os.path.join(_HERE, "..", rel), "rb") as fh:
        return fh.read().decode("utf-8")


def _case_source():
    """The rules above against the observer's source (a change on either side turns this red)."""
    import re
    f = []
    try:
        km = _source(os.path.join("logger", "src", "driver_macos", "keymap.rs"))
        comp = _source(os.path.join("logger", "src", "input", "ime_compose.rs"))
        cloak = _source(os.path.join("logger", "src", "input", "ime_cloak.rs"))
        hook = _source(os.path.join("logger", "src", "input", "hook.rs"))
        drv = _source(os.path.join("logger", "src", "driver_macos.rs"))
    except OSError as e:
        return ["cannot read the observer's source: %s" % e]
    body = km[km.index("fn macos_vk_to_vk"):]
    body = body[:body.index("other => other as u32")]
    consts = {}
    for name, val in re.findall(r"pub const (VK_[A-Z_]+): u32 = (0x[0-9A-Fa-f]+);", hook):
        consts[name] = int(val, 16)
    arms = re.findall(r"^\s*(0x[0-9A-Fa-f]+)\s*=>\s*(0x[0-9A-Fa-f]+|VK_[A-Z_]+)\s*,", body, re.M)
    src_map = dict((int(a, 16), int(b, 16) if b.startswith("0x") else consts.get(b)) for a, b in arms)
    if src_map != MAC_TO_VK:
        f.append("MAC_TO_VK differs from keymap.rs: %r" % sorted(set(src_map.items()) ^ set(MAC_TO_VK.items())))
    if consts.get("VK_KANJI") != VK_KANJI or consts.get("VK_DBE_ALPHANUMERIC") != VK_DBE_ALPHANUMERIC \
            or consts.get("VK_DBE_HIRAGANA") != VK_DBE_HIRAGANA:
        f.append("the mode-key constants differ from hook.rs")
    if not re.search(r"pub const MAX_SESSION_MS: u64 = %s;" % ("{:,}".format(LIMIT_MS).replace(",", "_")), cloak):
        f.append("LIMIT_MS differs from MAX_SESSION_MS in ime_cloak.rs")
    for needle in ("now_ms.saturating_sub(start) >= MAX_SESSION_MS",
                   "let restarted = apply(ComposeState::default(), vk, ime_open, chord, now_ms);",
                   "if !ime_open {\n        return finish(prev, false, now_ms);",
                   "0x30..=0x39 | 0x41..=0x5A =>",
                   "0x0D => finish(prev, false, now_ms),",
                   "0x1B => finish(prev, true, now_ms),",
                   "0x08 => {\n            let mut next = prev;\n            next.active = false;",
                   "0x25..=0x28 => {",
                   "_ if vk >= 0xF0 || vk == VK_KANJI => ComposeStep {",
                   "_ => finish(prev, false, now_ms),"):
        if needle not in comp:
            f.append("ime_compose.rs no longer contains %r" % needle)
    for needle in ("apply_mode_key(vk, press, &SHARED_MODE_CELLS);\n    if drives_compose(press) {",
                   "fn drives_compose(press: bool) -> bool {\n    press\n}"):
        if needle not in drv:
            f.append("driver_macos.rs no longer contains %r" % needle)
    return f


def _jl(rows):
    return ("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n").encode("utf-8")


def _fixture():
    """A two-block plan and its oracle: S1-like, S6-like (carried into the next trial), a trial with a
    Tab, a trial cut off at 20 s, and a marker between blocks."""
    plan = _jl([{"kind": "header", "format": "plan/1", "os": "macos", "seed": 1},
                {"kind": "block", "block_id": 0, "speed": "slow", "reset_ime": False, "marker": ["left", "right"], "marker_gap_ms": 150},
                {"kind": "block", "block_id": 1, "speed": "fast", "reset_ime": False, "marker": ["left", "right"], "marker_gap_ms": 150}])
    sha = hashlib.sha256(plan).hexdigest()
    rows = [{"kind": "header", "format": "oracle/1", "plan_sha256": sha, "os": "macos", "emitter_version": "x", "backend": "dryrun"}]
    clock = [0]

    def at(t, **kw):
        clock[0] += 1
        r = dict(kw, t_wall_ms=t, t_mono_ns=clock[0])
        rows.append(r)

    def press(tid, key, t):
        at(t, kind="sent", trial_id=tid, step=0, key=key, down=True)
        at(t + 60, kind="sent", trial_id=tid, step=0, key=key, down=False)

    at(1000, kind="block_begin", block_id=0)
    at(1000, kind="marker", block_id=0, seq=0)
    at(1150, kind="marker", block_id=0, seq=1)
    at(2000, kind="trial_begin", trial_id="t1")
    for i, k in enumerate(["k", "a", "space"]):
        press("t1", k, 2000 + 200 * i)
    press("t1", "enter", 3000)
    press("t1", "enter", 3500)
    at(3600, kind="trial_end", trial_id="t1")
    at(5000, kind="trial_begin", trial_id="t2")
    press("t2", "k", 5000)
    press("t2", "a", 5200)
    press("t2", "backspace", 5400)
    press("t2", "backspace", 5600)
    at(5700, kind="trial_end", trial_id="t2")
    at(7000, kind="trial_begin", trial_id="t3")
    press("t3", "k", 7000)
    press("t3", "tab", 7200)
    press("t3", "enter", 9000)
    at(9100, kind="trial_end", trial_id="t3")
    at(9200, kind="block_end", block_id=0)
    at(10000, kind="block_begin", block_id=1)
    at(10000, kind="marker", block_id=1, seq=0)
    at(10150, kind="marker", block_id=1, seq=1)
    at(11000, kind="trial_begin", trial_id="t4")
    press("t4", "k", 11000)
    press("t4", "space", 11200)
    at(11300, kind="sent", trial_id="t4", step=2, key="focus_away", down=True)
    press("t4", "enter", 11000 + LIMIT_MS + 10)
    press("t4", "enter", 11000 + LIMIT_MS + 500)
    at(11000 + LIMIT_MS + 600, kind="trial_end", trial_id="t4")
    at(11000 + LIMIT_MS + 700, kind="block_end", block_id=1)
    return plan, _jl(rows)


def _keymap_fixture():
    return {"k": 0x28, "a": 0x00, "space": 0x31, "enter": 0x24, "backspace": 0x33, "tab": 0x30,
            "left": 0x7B, "right": 0x7C, "shift": 0x38}


def _case_end_to_end():
    f = []
    plan, oracle = _fixture()
    out = predict(oracle, plan, _keymap_fixture())
    got = [(s["start_wall_ms"], s["end_wall_ms"], s["end"], s["start_trial"], s["end_trial"]) for s in out["sessions"]]
    want = [(2000, 3000, "row", "t1", "t1"),          # first Return closes (the second has no session)
            (5000, 7200, "row", "t2", "t3"),          # Backspace keeps it open into t3, Tab closes it
            (11000, 11000 + LIMIT_MS + 10, "truncated", "t4", "t4")]
    if got != want:
        f.append("predicted sessions: %r != %r" % (got, want))
    by = out["trials"]["by_trial"]
    if not by["t2"]["carried_out"] or by["t3"]["n_started"] != 0 or not by["t4"]["long"] or by["t1"]["long"]:
        f.append("per-trial summary wrong: %r" % by)
    if out["trials"]["n_long"] != 1 or out["counts"] != {"row": 2, "truncated": 1, "open": 0}:
        f.append("counts wrong: %r / %r" % (out["trials"], out["counts"]))
    if len(as_obs_rows(out["sessions"])) != 2:
        f.append("only reported sessions should become rows")
    if render(predict(oracle, plan, _keymap_fixture())) != render(out):
        f.append("two runs on the same input should give the same bytes")
    return f


def _case_marker_inside_session():
    """A session left open at the end of a block (S6 last in its block) collects the next block's
    marker arrows as nav, the Kana press at block_begin does not close it, and the next trial's
    letters continue it until the cut-off."""
    f = []
    plan, oracle = _fixture()
    rows = [json.loads(x) for x in oracle.decode("utf-8").splitlines()]
    # drop t3 so that t2's session is still open at block 1's start
    rows = [r for r in rows if r.get("trial_id") != "t3"]
    out = predict(_jl(rows), plan, _keymap_fixture())
    s = out["sessions"][1]
    if not (s["start_trial"] == "t2" and s["nav"] == 2 and s["end"] == "truncated" and s["end_trial"] == "t4"):
        f.append("a session open across the block boundary: %r" % s)
    return f


def _case_refusals():
    f = []
    plan, oracle = _fixture()
    for label, call in (
            ("windows plan", lambda: predict(oracle, plan.replace(b'"os": "macos"', b'"os": "windows"', 1), _keymap_fixture())),
            ("unrelated plan", lambda: predict(oracle, plan + _jl([{"kind": "block", "block_id": 9, "marker": []}]), _keymap_fixture())),
            ("unknown key", lambda: predict(oracle, plan, dict((k, v) for k, v in _keymap_fixture().items() if k != "tab"))),
            ("modifier sent as a key", lambda: predict(oracle.replace(b'"key": "tab"', b'"key": "shift"'), plan, _keymap_fixture()))):
        try:
            call()
            f.append("%s was not refused" % label)
        except InputError:
            pass
    return f


def _case_cli():
    import contextlib
    import io
    import tempfile
    f = []
    plan, oracle = _fixture()
    with tempfile.TemporaryDirectory() as d:
        p, o, k, out = (os.path.join(d, n) for n in ("plan.jsonl", "oracle.jsonl", "km.json", "out.json"))
        for path, data in ((p, plan), (o, oracle), (k, json.dumps(_keymap_fixture()).encode("utf-8"))):
            with open(path, "wb") as fh:
                fh.write(data)
        if main(["--oracle", o, "--plan", p, "--keymap", k, "--out", out]) != 0:
            f.append("the CLI did not exit 0")
        elif json.loads(open(out, encoding="utf-8").read())["counts"]["truncated"] != 1:
            f.append("the CLI output is not the prediction")
        with contextlib.redirect_stderr(io.StringIO()):
            rc = main(["--oracle", o, "--plan", o, "--keymap", k, "--out", out + "2"])
        if rc != 2:
            f.append("a bad plan should exit 2")
    return f


def selftest():
    cases = [("rules", _case_rules), ("cutoff", _case_cutoff), ("keymap", _case_keymap),
             ("source", _case_source), ("end_to_end", _case_end_to_end),
             ("marker_inside_session", _case_marker_inside_session), ("refusals", _case_refusals),
             ("cli", _case_cli)]
    bad = 0
    for name, fn in cases:
        try:
            fails = fn()
        except Exception as e:  # a crash in a case is a failure of that case, not of the run
            fails = ["raised %s: %s" % (type(e).__name__, e)]
        print("%s %s" % ("ok  " if not fails else "FAIL", name))
        for x in fails:
            print("     " + x)
        bad += 1 if fails else 0
    print("%d of %d cases passed" % (len(cases) - bad, len(cases)))
    return 0 if bad == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(prog="spec_predict.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--oracle")
    ap.add_argument("--plan")
    ap.add_argument("--keymap", default=DEFAULT_KEYMAP)
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.oracle and a.plan and a.out):
        sys.stderr.write("spec_predict.py: --oracle, --plan and --out are required\n")
        return 2
    try:
        with open(a.oracle, "rb") as fh:
            ob = fh.read()
        with open(a.plan, "rb") as fh:
            pb = fh.read()
        out = predict(ob, pb, load_keymap(a.keymap))
    except (OSError, InputError) as e:
        sys.stderr.write("spec_predict.py: %s\n" % e)
        return 2
    if os.path.exists(a.out):
        sys.stderr.write("spec_predict.py: %s exists (not overwritten)\n" % a.out)
        return 2
    with open(a.out, "wb") as fh:
        fh.write(render(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
