"""CoAuthor (Lee, Liang and Yang, CHI 2022): one session log (JSON lines) -> (t0, presses).

Counted as key presses, from events whose source is the user only:
- text-insert of exactly one character -> the category of that character
  (insertions of more than one character are dropped);
- text-delete -> backspace;
- cursor-* -> navigation (ignored by the symbolizer, kept for completeness).
Suggestion events and insertions by the language model are not key presses.
t0 is the time of the first event of the session, of any kind.
"""
import ast
import json

from .categories import char_category


def _ops(delta):
    if not delta:
        return []
    if isinstance(delta, str):
        delta = ast.literal_eval(delta)
    return delta.get("ops", [])


def presses_from_rows(rows):
    """rows: parsed JSON objects of one session. Returns (t0, [(t_ms, category), ...])."""
    rows = sorted(rows, key=lambda e: (int(e["eventTimestamp"]), int(e["eventNum"])))
    t0 = int(rows[0]["eventTimestamp"])
    presses = []
    for e in rows:
        t = int(e["eventTimestamp"])
        name, source = e["eventName"], e["eventSource"]
        if name.startswith("suggestion") or source != "user":
            continue
        if name == "text-insert":
            s = "".join(o["insert"] for o in _ops(e["textDelta"]) if isinstance(o.get("insert"), str))
            if len(s) == 1:
                presses.append((t, char_category(s)))
        elif name == "text-delete":
            presses.append((t, "backspace"))
        elif name.startswith("cursor-"):
            presses.append((t, "navigation"))
    return t0, presses


def presses_from_file(path):
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    return presses_from_rows(rows)
