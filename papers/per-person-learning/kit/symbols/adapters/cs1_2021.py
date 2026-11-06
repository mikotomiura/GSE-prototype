"""CS1 keystroke data, 2021 release (Edwards, Hart and Shrestha, JEDM 2023): rows of one
(student, assignment) -> work blocks, each (t0, presses).

Counted as key presses:
- X-Keystroke whose X-Metadata is exactly one character -> the category of that character;
- X-Action: arrow, Home, End, PageUp, PageDown -> navigation; Backspace -> backspace;
  Delete -> delete; Enter -> enter; Tab -> tab; Escape -> escape; Paste, Copy, Cut,
  Undefined -> other.
Other rows are kept only as non-key events, which matter for splitting blocks. Rows are
ordered by (ClientTimestamp truncated to integer ms, EventID). A new work block starts where
the gap between consecutive kept rows is at least 30 minutes. Blocks with fewer than two key
presses are dropped. t0 of a block is its first key press. Each block is symbolized
separately (no state is carried across blocks).
"""
from .categories import char_category

NAV = {"Left", "Right", "Up", "Down", "Home", "End", "PageUp", "PageDown"}
KEYS = {"Backspace": "backspace", "Delete": "delete", "Enter": "enter", "Tab": "tab", "Escape": "escape",
        "Paste": "other", "Copy": "other", "Cut": "other", "Undefined": "other"}
BLOCK_GAP_MS = 1_800_000


def classify(row):
    """One CSV row -> ("key", category), ("ev", None) or (None, None) for rows that are not kept."""
    et = row.get("EventType") or ""
    md = row.get("X-Metadata") or ""
    if et == "X-Keystroke":
        return ("key", char_category(md)) if len(md) == 1 else (None, None)
    if et == "X-Action":
        if md in NAV:
            return ("key", "navigation")
        if md in KEYS:
            return ("key", KEYS[md])
        return ("ev", None)
    if et == "File.Edit":
        insert = (row.get("EditType") or "") == "Insert" and len(row.get("InsertText") or "") >= 2
        return ("ev", None) if insert else (None, None)
    if et in ("X-Paste", "X-Copy"):
        return ("ev", None)
    if et == "Run.Program":
        return ("ev", None) if md == "Start" else (None, None)
    if et == "X-Attention":
        return ("ev", None) if md in ("Lockout", "ON", "OFF") else (None, None)
    return (None, None)


def blocks_from_rows(rows):
    """rows: CSV dict rows of one (student, assignment). Returns [(t0, [(t_ms, category), ...]), ...]."""
    items = []
    for row in rows:
        kind, cat = classify(row)
        if kind is None:
            continue
        items.append((int(float(row["ClientTimestamp"])), int(row["EventID"]), kind, cat))
    items.sort(key=lambda x: (x[0], x[1]))
    blocks, cur = [], []
    for it in items:
        if cur and it[0] - cur[-1][0] >= BLOCK_GAP_MS:
            blocks.append(cur)
            cur = []
        cur.append(it)
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        presses = [(t, cat) for t, _, k, cat in b if k == "key"]
        if len(presses) >= 2:
            out.append((presses[0][0], presses))
    return out
