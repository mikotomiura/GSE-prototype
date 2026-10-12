"""Utility: the 10 process measures of Tian et al. (2025), Table 5, on R0 and each form (preregistration, "Utility";
config.json utility.formulas). The same code computes R0 and every form; Inputlog values are used only in check 7.

Details fixed here before any data (listed in notes.md, "Implementation choices"):
- pauses are intervals between consecutive rows (down to down) of the released record;
- a P-burst or R-burst without a char press is not counted in the mean;
- between-word pauses: from a separator press to the first later letter or digit press when no other separator
  press lies between them;
- the cursor of the approximations is that of the A1' replay (R3-u: Home and End uncertain);
- R0 insertion: an Input or Paste row whose inserted text starts before the end of the current text;
  produced characters are char presses in every form (R0 included);
- the 10 equal time intervals divide the time from the first to the last row; the SD uses ddof = 0.
"""
import numpy as np

from replay import item_type
from synthetic_logs import SEP_CATS, shortcut_flags

METRICS = ["p_burst_mean_len", "r_burst_mean_len", "pause_mean_200ms", "within_word_pause_mean",
           "between_word_pause_mean", "deletion_mean_len", "deletion_proportion", "insertion_mean_len",
           "insertion_proportion", "interval_variance_10"]
OK, APPROX, NONE = "ok", "approx", "none"
_ROW = {
    # metric: (R0/R1/R5/R6, R2, R3, R3-u, R3-t(10, 100), R3-t(1000), R7, R4)
    "p_burst_mean_len": (OK, OK, OK, OK, APPROX, NONE, APPROX, NONE),
    "r_burst_mean_len": (OK, APPROX, APPROX, APPROX, APPROX, NONE, APPROX, NONE),
    "pause_mean_200ms": (OK, OK, OK, OK, APPROX, NONE, APPROX, NONE),
    "within_word_pause_mean": (OK, OK, OK, NONE, APPROX, NONE, APPROX, NONE),
    "between_word_pause_mean": (OK, OK, OK, NONE, APPROX, NONE, APPROX, NONE),
    "deletion_mean_len": (OK, APPROX, APPROX, APPROX, APPROX, APPROX, APPROX, NONE),
    "deletion_proportion": (OK, APPROX, APPROX, APPROX, APPROX, APPROX, APPROX, NONE),
    "insertion_mean_len": (OK, APPROX, APPROX, APPROX, APPROX, APPROX, APPROX, NONE),
    "insertion_proportion": (OK, APPROX, APPROX, APPROX, APPROX, APPROX, APPROX, NONE),
    "interval_variance_10": (OK, OK, OK, OK, APPROX, APPROX, APPROX, NONE),
}


def column(form):
    base = form.split("(")[0]
    if base in ("R0", "R1", "R5", "R6"):
        return 0
    if base == "R3-t":
        return 5 if form == "R3-t(1000)" else 4
    return {"R2": 1, "R3": 2, "R3-u": 3, "R7": 6, "R4": 7}[base]


def cell(metric, form):
    return _ROW[metric][column(form)]


def is_char(c):
    return c in ("letter", "digit", "space", "punctuation", "enter", "char")


def cursor_flags(cats, uncertain_home_end):
    """For each row, whether the A1' cursor is away from the end of the replayed document before the row."""
    sc = shortcut_flags(cats)
    doc, cur, ctrl = [], 0, False
    away = [False] * len(cats)
    for i, c in enumerate(cats):
        away[i] = cur < len(doc)
        if c in ("control", "modifier"):
            ctrl = ctrl or c == "control"
            continue
        after_ctrl, ctrl = ctrl, False
        if sc[i]:
            continue
        if is_char(c):
            doc.insert(cur, item_type(c))
            cur += 1
        elif c == "backspace":
            if cur > 0:
                del doc[cur - 1]
                cur -= 1
        elif c == "delete":
            if cur < len(doc):
                del doc[cur]
        elif c in ("arrow_left", "arrow_right") and after_ctrl:
            cur = len(doc)
        elif c == "arrow_left":
            cur = max(0, cur - 1)
        elif c == "arrow_right":
            cur = min(len(doc), cur + 1)
        elif c == "home":
            if uncertain_home_end:
                cur = len(doc)
            elif after_ctrl:
                cur = 0
            else:
                while cur > 0 and doc[cur - 1] != "n":
                    cur -= 1
        elif c == "end":
            if uncertain_home_end or after_ctrl:
                cur = len(doc)
            else:
                while cur < len(doc) and doc[cur] != "n":
                    cur += 1
        elif c in ("navigation", "mouse"):
            cur = len(doc)
    return away


def r0_edits(rows):
    """R0: per row, (deleted characters, inserted away from the leading edge, revision) from activity, text change
    and position, replaying the text length."""
    n = 0
    out = []
    for r in rows:
        act, tc, pos = r["activity"], r["text_change"], r["cursor_position"]
        deleted, away, revision = 0, False, False
        if act in ("Input", "Paste") and tc != "NoChange":
            start = pos - len(tc)
            away = start < n
            n += len(tc)
        elif act == "Remove/Cut" and tc != "NoChange":
            deleted = len(tc)
            n -= len(tc)
            revision = True
        elif act == "Replace":
            a, b = tc.rsplit(" => ", 1)
            deleted = len(a)
            n += len(b) - len(a)
            revision = True
        elif act.startswith("Move From"):
            revision = True
        out.append((deleted, away, revision or away))
    return out


def _mean(v):
    return float(np.mean(v)) if len(v) else None


def metrics(rel, task_max, r0_rows=None):
    """{metric: value or None} for a released record; None where the cell is 'none' or the value is undefined.
    rel: forms.Released (rows with categories and times). task_max: the interval_variance_10 denominator."""
    form = rel.form
    out = {m: None for m in METRICS}
    if column(form) == 7:
        return out
    cats = rel.cats()
    times = rel.times()
    scale = 1.0 / (1 - rel.p) if rel.base == "R7" else 1.0
    exact = column(form) == 0
    sc = shortcut_flags(cats)
    charp = [is_char(c) and not sc[i] for i, c in enumerate(cats)]
    iv = [times[i] - times[i - 1] for i in range(1, len(times))]
    away = cursor_flags(cats, rel.base == "R3-u")
    if exact:
        ed = r0_edits(rel.rows)
        deleted = [d for d, _, _ in ed]
        ins_away = [a for _, a, _ in ed]
        revision = [r for _, _, r in ed]
    else:
        deleted = [1 if c in ("backspace", "delete") else 0 for c in cats]
        ins_away = [charp[i] and away[i] for i in range(len(cats))]
        revision = [c in ("backspace", "delete") or (charp[i] and away[i]) for i, c in enumerate(cats)]
    produced = sum(charp) * scale

    def bursts(ends_at):
        lens, n = [], 0
        for i in range(len(cats)):
            if i and ends_at(i):
                if n:
                    lens.append(n)
                n = 0
            if charp[i]:
                n += 1
        if n:
            lens.append(n)
        return [v * scale for v in lens]

    def want(m):
        return cell(m, form) != NONE

    if want("p_burst_mean_len"):
        out["p_burst_mean_len"] = _mean(bursts(lambda i: iv[i - 1] > 2000))
    if want("r_burst_mean_len"):
        out["r_burst_mean_len"] = _mean(bursts(lambda i: iv[i - 1] > 2000 or revision[i]))
    if want("pause_mean_200ms"):
        out["pause_mean_200ms"] = _mean([v for v in iv if v > 200])
    alnum = [c in ("letter", "digit") and not sc[i] for i, c in enumerate(cats)]
    if want("within_word_pause_mean"):
        out["within_word_pause_mean"] = _mean([iv[i - 1] for i in range(1, len(cats))
                                               if alnum[i] and alnum[i - 1] and iv[i - 1] > 200])
    if want("between_word_pause_mean"):
        v, last_sep = [], None
        for i, c in enumerate(cats):
            if c in SEP_CATS and not sc[i]:
                last_sep = i
            elif alnum[i] and last_sep is not None:
                d = times[i] - times[last_sep]
                if d > 200:
                    v.append(d)
                last_sep = None
        out["between_word_pause_mean"] = _mean(v)
    if want("deletion_mean_len"):
        runs, n = [], 0
        for d in deleted:
            if d:
                n += d
            elif n:
                runs.append(n)
                n = 0
        if n:
            runs.append(n)
        out["deletion_mean_len"] = _mean([r * scale for r in runs]) if not exact else _mean(runs)
    if want("deletion_proportion"):
        out["deletion_proportion"] = (sum(deleted) * scale / produced) if produced else None
    if want("insertion_mean_len") or want("insertion_proportion"):
        runs, n = [], 0
        for i in range(len(cats)):
            if ins_away[i]:
                n += (len(rel.rows[i]["text_change"]) if exact else 1)
            elif n:
                runs.append(n)
                n = 0
        if n:
            runs.append(n)
        if not exact:
            runs = [r * scale for r in runs]
        out["insertion_mean_len"] = _mean(runs)
        out["insertion_proportion"] = (sum(runs) / produced) if produced else None
    if want("interval_variance_10") and len(times) > 1 and task_max:
        t0, t1 = times[0], times[-1]
        edges = np.linspace(t0, t1, 11)
        rates = []
        for a, b in zip(edges[:-1], edges[1:]):
            n = sum(1 for i, t in enumerate(times) if charp[i] and (a <= t < b or (b == t1 and t == t1)))
            rates.append(n * scale / (b - a) if b > a else 0.0)
        out["interval_variance_10"] = float(np.std(np.array(rates) / task_max))
    return out


def interval_max(rel):
    """The largest of the 10 interval production rates of an R0 record (for the task maximum of its prompt)."""
    cats = rel.cats()
    times = rel.times()
    sc = shortcut_flags(cats)
    if len(times) < 2:
        return 0.0
    edges = np.linspace(times[0], times[-1], 11)
    best = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        n = sum(1 for i, t in enumerate(times) if is_char(cats[i]) and not sc[i]
                and (a <= t < b or (b == times[-1] and t == times[-1])))
        if b > a:
            best = max(best, n / (b - a))
    return best
