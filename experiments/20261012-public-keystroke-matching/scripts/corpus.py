"""Writers of the main computation (preregistration, "Data"): normalised rows, the distributed text and the score.

Rows use the Kaggle column names (event_id, down_time, up_time, action_time, down_event, up_event, activity,
text_change, cursor_position, word_count), the same as synthetic_logs.py. The KLiCKe column names are mapped at check 2
after acquisition (load_klicke.py); nothing here reads data files.
"""
import re
from dataclasses import dataclass, field

import seeds
from synthetic_logs import DEFAULT_OPS, Writer, category, word_lengths

MIN_WORDS = 50
MOVE = re.compile(r"Move From \[(\d+), (\d+)\] To \[(\d+), (\d+)\]")


@dataclass
class WriterData:
    writer: str
    prompt: str
    rows: list
    text: str
    score: float = None
    inputlog: dict = None
    extra: dict = field(default_factory=dict)


class Rec:
    """The object the release forms of synthetic_logs.py take (they read .rows only)."""

    def __init__(self, rows):
        self.rows = rows


def active_rows(rows):
    """The active writing time: from the first key press to the last event whose text change is not empty
    (config.json datasets.klicke.active_window). Mouse rows before the first key press are dropped."""
    first = next((i for i, r in enumerate(rows) if category(r["down_event"]) != "mouse"), None)
    last = None
    for i, r in enumerate(rows):
        if r["text_change"] not in ("", "NoChange"):
            last = i
    if first is None or last is None or last < first:
        return []
    out = [dict(r) for r in rows[first:last + 1]]
    for n, r in enumerate(out):
        r["event_id"] = n + 1
    return out


def exclusion_reason(w):
    """None when the writer is kept; otherwise the reason (preregistration, "Data", exclusion)."""
    if not w.rows:
        return "missing log"
    if not w.text:
        return "missing text"
    if w.score is None:
        return "missing score"
    if len(word_lengths(w.text)) < MIN_WORDS:
        return "text under 50 words"
    return None


def replay_origins(rows):
    """Replay R0 (text change and position) keeping, for each character of the final draft, the row index of the
    press that typed it, or None for pasted characters. Returns (final draft, origins). Used for the true windows."""
    chars = []
    for i, r in enumerate(rows):
        act, tc, pos = r["activity"], r["text_change"], r["cursor_position"]
        if act == "Input" and tc != "NoChange":
            s = pos - len(tc)
            chars[s:s] = [(c, i) for c in tc]
        elif act == "Paste" and tc != "NoChange":
            s = pos - len(tc)
            chars[s:s] = [(c, None) for c in tc]
        elif act == "Remove/Cut" and tc != "NoChange":
            del chars[pos:pos + len(tc)]
        elif act == "Replace":
            a, b = tc.rsplit(" => ", 1)  # the typed side is one key
            s = pos - len(b)
            chars[s:s + len(a)] = [(c, i) for c in b]
        elif act.startswith("Move From"):
            a, b, c, _ = map(int, MOVE.match(act).groups())
            sub = chars[a:b]
            del chars[a:b]
            chars[c:c] = sub
    return "".join(c for c, _ in chars), [o for _, o in chars]


def synthetic_corpus(seed, prompts=4, per_prompt=40, ops=None, timing="digraph", tag="corpus"):
    """A small corpus of synthetic writers for the self-test (no human data). The distributed text is the final
    draft; the score is a fixed function of length plus noise; writer IDs are strings as in the distribution."""
    out = []
    for p in range(prompts):
        for i in range(per_prompt):
            wid = "%s_p%d_w%03d" % (tag, p, i)
            ks = seeds.seed_int(seed, "synthetic", str(p), wid, "", "", tag + ":keys")
            hs = seeds.seed_int(seed, "synthetic", str(p), wid, "", "", tag + ":hidden")
            ls = seeds.seed_int(seed, "synthetic", str(p), wid, "", "", tag + ":letters")
            rec = Writer(ks, hs, ls, timing=timing, ops=DEFAULT_OPS if ops is None else ops).run()
            g = seeds.rng(seed, "synthetic", str(p), wid, "", "", tag + ":score")
            score = round(len(word_lengths(rec.final)) / 40.0 + float(g.normal(0, 0.5)), 3)
            out.append(WriterData(wid, "P%d" % p, rec.rows, rec.final, score))
    return out
