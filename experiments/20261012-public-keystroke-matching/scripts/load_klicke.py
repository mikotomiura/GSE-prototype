"""KLiCKe loader (preregistration, "Data" and check 2). Reads the extracted WritingTask files into WriterData.

Column map (check 2; the distributed CSV columns to the Kaggle names used by corpus.py and synthetic_logs.py):
    DownEventID -> event_id, DownTime -> down_time, UpTime -> up_time, ActionTime -> action_time,
    DownEvent -> down_event, UpEvent -> up_event, CursorPosition -> cursor_position, WordCount -> word_count,
    TextChange -> text_change, Activity -> activity.
Columns not in the release table (the unnamed first column, UpEventID, PauseTime) are not used: the rule of the
preregistration drops them in every form except R0, and the rows of the computation carry the Kaggle columns only.
The difference between DownEventID and UpEventID is counted in check 2 (extra["up_event_id_differs"]).

Task and score come from holistic_scores.csv (ID, Prompt, Score). Its Text column is never read into WriterData;
the distributed text is texts/<ID>.txt (the README's essays). The two are not compared (no such quantity is
registered).

Errors never carry row content: a log that cannot be read is reported by a reason code and the exception type name
(security-checker LOW 2). A row whose activity starts with "Move From" but does not match the format, or a Replace
row without " => ", makes the log unreadable (reason "unreadable log"), and the writer is excluded with that reason.
"""
import csv
import io
import math
import os
import re
from collections import Counter

from corpus import WriterData

COLMAP = {"DownEventID": "event_id", "DownTime": "down_time", "UpTime": "up_time", "ActionTime": "action_time",
          "DownEvent": "down_event", "UpEvent": "up_event", "CursorPosition": "cursor_position",
          "WordCount": "word_count", "TextChange": "text_change", "Activity": "activity"}
NOT_IN_TABLE = ("", "UpEventID", "PauseTime")
EXPECTED_HEADER = ["", "DownEventID", "UpEventID", "DownTime", "UpTime", "ActionTime", "DownEvent", "UpEvent",
                   "CursorPosition", "PauseTime", "WordCount", "TextChange", "Activity"]
INT_COLS = ("event_id", "cursor_position", "word_count")
TIME_COLS = ("down_time", "up_time", "action_time")
MOVE = re.compile(r"Move From \[(\d+), (\d+)\] To \[(\d+), (\d+)\]$")
# The distribution escapes four characters in TextChange, DownEvent and UpEvent (found at check 2): a newline is
# written as backslash-n, a tab as backslash-t, a double quote as backslash-quote and a backslash as two backslashes
# (no other backslash sequence occurs). They are read back to the characters, left to right in one pass.
ESCAPE = re.compile(r"\\([\\\"nt])")
UNESCAPE = {"\\": "\\", '"': '"', "n": "\n", "t": "\t"}
ESCAPED_COLS = ("down_event", "up_event", "text_change")


ANY_ESCAPE = re.compile(r"\\(.?)", re.S)


def count_escapes(s, where, c):
    """Counts the backslash sequences of a raw value by the character after the backslash (check 2; reproduces
    'no other backslash sequence occurs'): n, t, quote, backslash, or 'other' / 'end of value'."""
    for m in ANY_ESCAPE.finditer(s):
        k = m.group(1)
        c["%s backslash then %s" % (where, k if k in UNESCAPE else ("end of value" if k == "" else "other"))] += 1


def unescape(s):
    return ESCAPE.sub(lambda m: UNESCAPE[m.group(1)], s) if "\\" in s else s

csv.field_size_limit(16 << 20)  # 16 MiB; a larger field makes the log unreadable (type name only)


class LogError(Exception):
    """A reason code only (no row content)."""


def _num(s, integral):
    v = float(s)
    if not math.isfinite(v):
        raise LogError("non-finite number")
    if integral or v.is_integer():
        if not v.is_integer():
            raise LogError("non-integer value")
        return int(v)
    return v


def decode(b):
    """utf-8 (a BOM is dropped), else cp1252; the encoding used is returned with the string. Bytes that cp1252
    does not define are replaced and the encoding is then reported as 'cp1252 with replacement' (counted in check 1;
    such a log is read, not excluded)."""
    try:
        return b.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        return b.decode("cp1252"), "cp1252"
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace"), "cp1252 with replacement"


def read_log(path):
    """Rows with the Kaggle names and the counts of check 2 that need the columns outside the table:
    (rows, extra). Raises LogError with a reason code."""
    with open(path, "rb") as f:
        s, enc = decode(f.read())
    reader = csv.reader(_lines(s), strict=True)
    try:
        return _read_rows(reader, enc)
    except csv.Error:
        raise LogError("csv format") from None


def _read_rows(reader, enc):
    header = next(reader, None)
    if header != EXPECTED_HEADER:
        raise LogError("header differs")
    rows, id_diff, seq1, seq0 = [], 0, True, True
    esc = Counter()
    for n, rec in enumerate(reader):
        if len(rec) != len(header):
            raise LogError("field count differs")
        d = dict(zip(header, rec))
        try:
            r = {COLMAP[k]: d[k] for k in COLMAP}
            for c in ESCAPED_COLS:
                if "\\" in r[c]:
                    count_escapes(r[c], "text_change" if c == "text_change" else "key", esc)
                r[c] = unescape(r[c])
            for c in INT_COLS:
                r[c] = _num(r[c], True)
            for c in TIME_COLS:
                r[c] = _num(r[c], False)
            up_id = _num(d["UpEventID"], True)
            first = d[""]
        except (ValueError, KeyError):
            raise LogError("unparsable number") from None
        if r["event_id"] != up_id:
            id_diff += 1
        seq1 = seq1 and first == str(n + 1)
        seq0 = seq0 and first == str(n)
        act = r["activity"]
        if act.startswith("Move From") and not MOVE.match(act):
            raise LogError("Move From format")
        if act == "Replace" and " => " not in r["text_change"]:
            raise LogError("Replace without =>")
        rows.append(r)
    return rows, {"encoding": enc, "escapes": esc, "up_event_id_differs": id_diff, "first_column_row_number_from_1": seq1,
                  "first_column_row_number_from_0": seq0}


def read_scores(path):
    """{ID: [(prompt, score)]} from holistic_scores.csv (the Text column is skipped) and the counts of check 1."""
    out, bad_score = {}, 0
    with open(path, "rb") as f:
        s, enc = decode(f.read())
    reader = csv.DictReader(_lines(s))
    if reader.fieldnames != ["ID", "Prompt", "Text", "Score"]:
        raise LogError("score header differs")
    for d in reader:
        try:
            sc = float(d["Score"])
            if not math.isfinite(sc):
                raise ValueError
        except ValueError:
            sc, bad_score = None, bad_score + 1
        out.setdefault(d["ID"], []).append((d["Prompt"], sc))
    return out, {"encoding": enc, "score_unparsable": bad_score}


def _lines(s):
    return io.StringIO(s, newline="")


def load(root, with_rows=True):
    """WriterData for every ID seen in the logs, the texts or the scores, and a report of counts (no IDs).
    A writer whose log cannot be read has rows [] and extra['load_error'] = reason code."""
    log_dir = os.path.join(root, "keystrokelogs", "csv")
    text_dir = os.path.join(root, "texts")
    logs = {f[:-4] for f in os.listdir(log_dir) if f.endswith(".csv")}
    texts = {f[:-4] for f in os.listdir(text_dir) if f.endswith(".txt")}
    scores, srep = read_scores(os.path.join(root, "holistic_scores.csv"))
    ids = sorted(logs | texts | set(scores))
    report = {"scores": srep, "ids_logs": len(logs), "ids_texts": len(texts), "ids_scores": len(scores),
              "ids_union": len(ids), "score_rows": sum(len(v) for v in scores.values()),
              "ids_with_more_than_one_score_row": sum(1 for v in scores.values() if len(v) > 1),
              "ids_in_more_than_one_prompt": sum(1 for v in scores.values() if len({p for p, _ in v}) > 1)}
    out = []
    for i in ids:
        sc = scores.get(i)
        prompt = sc[0][0] if sc else ""
        score = sc[0][1] if sc and len({p for p, _ in sc}) == 1 else None
        w = WriterData(i, prompt, [], "", score)
        if i in texts:
            with open(os.path.join(text_dir, i + ".txt"), "rb") as f:
                w.text, w.extra["text_encoding"] = decode(f.read())
        if i in logs and with_rows:
            w.extra["log_path"] = os.path.join(log_dir, i + ".csv")
        out.append(w)
    return out, report


def fill_rows(w):
    """Reads the log of w in place (in a worker process). Errors become extra['load_error'] (reason code)."""
    p = w.extra.get("log_path")
    if not p:
        return w
    try:
        w.rows, ex = read_log(p)
        w.extra.update(ex)
    except LogError as e:
        w.rows, w.extra["load_error"] = [], str(e)
    except Exception as e:  # noqa: BLE001 - type name only, never the message (it may hold row content)
        w.rows, w.extra["load_error"] = [], "error " + type(e).__name__
    return w
