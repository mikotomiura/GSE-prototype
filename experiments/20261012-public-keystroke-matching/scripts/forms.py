"""Release forms applied to a writer's active rows (preregistration, "Release forms"; config.json release_forms).

The transformations are those of synthetic_logs.py (checked before fixing). The random forms (R5, R6, R7) are drawn
once per record with the seed uses r5_sub, r6_perm and r7_drop (prompt, writer; for R7 the probability p is in the
draw field, so the three levels use separate streams), and the same processed record is used by matching and utility.
"""
import dp
import seeds
from corpus import Rec
from synthetic_logs import (category, form_R0, form_R1, form_R2, form_R3, form_R3t, form_R3u, form_R5, form_R6,
                            form_R7, record_segments)

MAIN = ["R0", "R1", "R2", "R3", "R3-u", "R3-t(10)", "R3-t(100)", "R3-t(1000)", "R4(1)", "R4(2)", "R4(4)", "R4(8)",
        "R7(0.1)", "R7(0.25)", "R7(0.5)"]
APPENDIX = ["R5", "R6"]
ALL = MAIN + APPENDIX
# exploratory (decisions 55 and 56; not in the preregistration): run separately with R3 as the reference
DP = ["R3", "R-DP(0.5)", "R-DP(1)", "R-DP(2)", "R-DP(4)"]


def param(form):
    """'R3-t(100)' -> ('R3-t', 100); 'R7(0.25)' -> ('R7', 0.25); 'R2' -> ('R2', None)."""
    if "(" not in form:
        return form, None
    base, v = form[:-1].split("(")
    return base, (float(v) if base in ("R7", "R-DP") else int(v))


class Released:
    """A released record: rows (or R4 values), the category column the attackers read and, for R7, the kept mask."""

    def __init__(self, form, rows=None, values=None, keep=None, origin=None):
        self.form = form
        self.base, self.p = param(form)
        self.rows = rows
        self.values = values
        self.keep = keep
        self.origin = origin

    def cats(self):
        """The category column: R2 and the R3 family release categories; other forms release keys."""
        if self.rows is None:
            return None
        if self.base in ("R2", "R3", "R3-u", "R3-t", "R7", "R-DP"):
            return [r["down_event"] for r in self.rows]
        return [category(r["down_event"]) for r in self.rows]

    def times(self):
        return [r["down_time"] for r in self.rows]


def release(rows, form, seed, prompt, writer):
    rec = Rec(rows)
    base, p = param(form)
    if base == "R0":
        return Released(form, form_R0(rec))
    if base == "R1":
        return Released(form, form_R1(rec))
    if base == "R2":
        return Released(form, form_R2(rec))
    if base == "R3":
        return Released(form, form_R3(rec))
    if base == "R3-u":
        return Released(form, form_R3u(rec))
    if base == "R3-t":
        return Released(form, form_R3t(rec, p))
    if base == "R4":
        return Released(form, values=r4_values(rows, p))
    if base == "R7":
        out, keep = form_R7(rec, p, seeds.rng(seed, "r7_drop", prompt, writer, "", "", str(p)))
        return Released(form, out, keep=[bool(k) for k in keep])
    if base == "R-DP":
        eps = form[:-1].split("(")[1]
        out, origin = dp.release(form_R3(rec), p, seeds.rng(seed, "exploratory_dp", prompt, writer, "", "", "eps:" + eps))
        return Released(form, out, origin=origin)
    if base == "R5":
        return Released(form, form_R5(rec, seeds.rng(seed, "r5_sub", prompt, writer)))
    if base == "R6":
        return Released(form, form_R6(rec, seeds.rng(seed, "r6_perm", prompt, writer)))
    raise ValueError("unknown form %r" % (form,))


def r4_values(rows, w):
    """R4(w): floor(value / w) of the record segments of the R0 category column."""
    return [v // w for v, _ in record_segments([category(r["down_event"]) for r in rows])]
