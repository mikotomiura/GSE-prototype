"""Registered synthesis for the AI-fatigue methodological review (registration draft 0.10).

Implements, from the code tables (CSV):
- calibration draws and the post-registration screening order (GSRR-33, GSRR-39)
- derived values: C1 representative value, C4f record summary, C6c, C7 and each of its conditions (GSRR-43, GSRR-48)
- agreement per set: percentage agreement and Cohen's kappa with bootstrap CI (GSRR-47)
- tables per set, population group and centre; C2a/C2c/C2d; C2b per instrument;
  C4f per recalculated result; every instrument version used in a set; the per-study table;
  RQ4 study counts; records where C6a and C7 (iii) both hold; problem statements (evaluable records
  per problem type, GSRR-57; C7 by condition);
  sensitivity analyses 1-4 (GSRR-56, GSRR-57, GSRR-62)

Input files (one row per unit; `coder` is coder1 / coder2 / reconciled):
  records_<coder>.csv      record-level codes (C1 per main instrument, C3-C7 inputs)
  instruments_<coder>.csv  instrument-level codes (C2a, C2c, C2d)
  items_<coder>.csv        item-level codes (C2b), keyed by version_id and item_no
  c4f_<coder>.csv          one row per recalculated result (source: text/table; consistent: yes/no/na; gross: 1/0)
  c4f_ai.csv               the AI draft for C4f (optional; human-AI agreement, report-only)
  links.csv                E5 links (record_id, group_id)
The set of an instrument version (and of its items) is derived, never read: the first set,
in the order exploration, main, late, in which a record uses the version.
Missing files, missing columns and values outside the code lists stop the script.

Usage:
    python3 c_synthesis.py --tables <dir> [--coder reconciled]
    python3 c_synthesis.py --agreement <dir>
    python3 c_synthesis.py --draw-calibration <pool_ids.txt> --round K [--drawn <f>] [--exploration <f>]
    python3 c_synthesis.py --screening-order <candidates.csv>
"""

import argparse
import csv
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

C1_LEVELS = ["L1a", "L1b", "L2", "L3", "L4", "L5", "L6"]
C7_WEAK_LEVELS = {"L3", "L4", "L5", "L6"}
C2B_TYPES = ["MOT", "AVO", "FUT", "IRR", "FAT", "OTH"]
TARGETED_TYPES = {"MOT", "AVO", "FUT"}
POPULATION_ORDER = [
    "students_learners", "teachers_researchers", "workers_other",
    "health_professionals", "consumers_general", "unknown",
]
# GSRR-53: values excluded from denominators. All other values are substantive and stay in.
EXCLUDED = {"not_verifiable", "not_applicable", "unresolved", ""}
# Family cells that give no term to compare (C7 (iii)); also used for the C6a rules.
NO_FAMILY = {"no_family_term", "none", "instrument_unnamed", "not_verifiable"}
CAL_ONLY = "calibration_only"   # a version used only by calibration records: in no set (GSRR-43)
MIN_STUDIES = 10
MIN_NEW_INSTRUMENTS = 3
CAL_SEED = 20261017
EXPL_CAL_SEED = 20261019
SMALL_POOL = 24          # 15 removable by calibration + 10 needed - 1
SCREEN_SEED = 20261018
BOOT_SEED = 20261017
BOOT_N = 2000
PRIMARY_SETS = ["main", "exploration", "late"]
FIRST_SEEN_ORDER = ["exploration", "main", "late"]
VOCAB = {
    "set": {"exploration", "main", "late", "calibration"},
    "type": set(C2B_TYPES) | {"unresolved"},
    "consistent": {"yes", "no", "na", "unresolved"},
    "source": {"text", "table"},
    "C4a": {"consistent", "inconsistent", "no_comparison_possible", "not_verifiable", "not_applicable",
            "unresolved"},
    "C6a": {"same_family", "different_family", "no_family_term", "instrument_unnamed", "not_verifiable",
            "no_construct_term", "unresolved"},
    "title_ai_fatigue_term": {"yes", "no", "unresolved"},
    # C6b: "no causal wording" is a match (GSRR-43), so it is coded as match, not as its own value
    "C6b": {"match", "mismatch", "not_verifiable", "unresolved"},
}
REQUIRED = {
    "records": ["record_id", "set", "population", "centre", "peer_reviewed", "C3", "C4a", "C4b", "C4c",
                "C4d", "C4e_codebook", "C4e_agreement", "C5", "C6a", "C6b", "conclusion_identified",
                "main_instrument_identified", "conclusion_ai_fatigue_term", "conclusion_family",
                "main_instrument_family", "conclusion_sentence",
                "title_ai_fatigue_term"] + [f"C1_{lv}" for lv in C1_LEVELS],
    "instruments": ["record_id", "instrument_id", "version_id", "language", "items_full"],
    "items": ["version_id", "item_no", "type", "boundary", "secondary_type", "target"],
    "c4f": ["record_id", "result_id", "source", "consistent", "gross"],
}


class InputError(Exception):
    pass


def load(d, kind, coder):
    path = d / f"{kind}_{coder}.csv"
    if not path.exists():
        raise InputError(f"missing file {path.name}")
    rows = read_csv(path)
    cols = set(rows[0]) if rows else set()
    missing = [c for c in REQUIRED[kind] if rows and c not in cols]
    if missing:
        raise InputError(f"{path.name}: missing columns {missing}")
    for r in rows:
        for col, allowed in VOCAB.items():
            if col in r and r[col] not in allowed:
                raise InputError(f"{path.name}: value {r[col]!r} not allowed in column {col}")
        for col in REQUIRED[kind]:
            if r.get(col, "") == "" and col not in {"secondary_type", "target", "conclusion_sentence"}:
                raise InputError(f"{path.name}: empty cell in {col} (use not_verifiable / not_applicable)")
    return rows


def version_sets(insts, recs):
    """First set (exploration, main, late) in which a record uses each version.
    A version used only by calibration records belongs to no set (CAL_ONLY)."""
    rec_set = {r["record_id"]: r["set"] for r in recs}
    used = defaultdict(set)
    for i in insts:
        used[i["version_id"]].add(rec_set.get(i["record_id"], ""))
    out = {}
    for v, ss in used.items():
        out[v] = next((s for s in FIRST_SEEN_ORDER if s in ss), CAL_ONLY)
    return out


def read_csv(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def families(value):
    """A family cell may hold several families separated by '|'."""
    return {v for v in value.split("|") if v} if value else set()


# --- draws (GSRR-33, GSRR-39) ---------------------------------------------

def exploration_study_ids(recs):
    """Record IDs of the primary studies of the exploration set (never instrument IDs)."""
    return sorted({r["record_id"] for r in recs if r.get("set") == "exploration"})


def all_exploration_drawn(drawn, exploration_ids):
    """GSRR-39: True if every exploration study has been used for calibration."""
    return bool(exploration_ids) and set(exploration_ids) <= set(drawn)


def draw_calibration(pool_ids, round_k, already_drawn=(), exploration_ids=(), instrument_ids=()):
    """Round k draws 5 from the IDs not yet drawn (seed + k - 1).

    Pool of SMALL_POOL or fewer: draw from the record IDs of the primary studies of the
    exploration set (at most two rounds); instrument IDs are refused.
    Otherwise draw from the pool (at most three rounds).
    """
    if len(pool_ids) <= SMALL_POOL:
        if not exploration_ids:
            raise ValueError("small pool: exploration IDs are required (--exploration)")
        if set(exploration_ids) & set(instrument_ids):
            raise ValueError("small pool: exploration draws use study record IDs, not instrument IDs")
        if round_k > 2:
            raise ValueError("small pool: at most two calibration rounds on exploration records")
        source, seed = exploration_ids, EXPL_CAL_SEED
    else:
        if round_k > 3:
            raise ValueError("at most three calibration rounds")
        source, seed = pool_ids, CAL_SEED
    remaining = sorted(set(source) - set(already_drawn))
    if len(remaining) < 5:
        raise ValueError(f"only {len(remaining)} records left to draw")
    return sorted(random.Random(seed + round_k - 1).sample(remaining, 5))


def screening_order(candidates):
    """Per group: sort IDs, shuffle with a generator freshly seeded with SCREEN_SEED.
    Then interleave the groups one record at a time in the listed order (GSRR-33)."""
    by_group = defaultdict(list)
    for c in candidates:
        by_group[c["population"]].append(c["record_id"])
    groups = POPULATION_ORDER + sorted(set(by_group) - set(POPULATION_ORDER))
    queues = {}
    for g in groups:
        ids = sorted(by_group.get(g, []))
        random.Random(SCREEN_SEED).shuffle(ids)
        queues[g] = ids
    order = []
    while any(queues.values()):
        for g in groups:
            if queues[g]:
                order.append((g, queues[g].pop(0)))
    return order


# --- derived values (GSRR-43, GSRR-48) -------------------------------------

def c1_representative(rec):
    """First applicable level in the order listed. Unresolved input -> unresolved."""
    values = [rec.get(f"C1_{lv}", "") for lv in C1_LEVELS]
    if "unresolved" in values:
        return "unresolved"
    for lv, v in zip(C1_LEVELS, values):
        if v == "1":
            return lv
    return "not_verifiable"


def c4f_summary(results):
    """Per record, first value that applies (GSRR-43): any_inconsistency / none (>= 1 consistent,
    no inconsistent) / cannot_be_calculated / not_applicable (no results). Unresolved input -> unresolved."""
    vals = [r["consistent"] for r in results]
    if not vals:
        return "not_applicable"
    if "unresolved" in vals:
        return "unresolved"
    if "no" in vals:
        return "any_inconsistency"
    if "yes" in vals:
        return "none"
    return "cannot_be_calculated"


def c4f_gross(results):
    """Gross-inconsistency summary: same order and same four values, any_gross in place of
    any_inconsistency (no_gross = at least one calculated result and no gross inconsistency)."""
    if not results:
        return "not_applicable"
    if any(r["consistent"] == "unresolved" or r.get("gross") == "unresolved" for r in results):
        return "unresolved"
    if any(r.get("gross") == "1" for r in results):
        return "any_gross"
    if any(r["consistent"] in ("yes", "no") for r in results):
        return "no_gross"
    return "cannot_be_calculated"


def c6c(rec, rep):
    """C6c (GSRR-43): the title input and the main instrument's C1 representative value.
    Unresolved input -> unresolved; main instrument unknown (or no C1 level) -> cannot_decide."""
    title, mi = rec.get("title_ai_fatigue_term"), rec.get("main_instrument_identified")
    if "unresolved" in (title, mi):
        return "unresolved"
    if mi != "1":
        return "cannot_decide"
    if title == "no":
        return "no_ai_term"
    if rep == "unresolved":
        return "unresolved"
    if rep in C7_WEAK_LEVELS:
        return "ai_term_L3_L6"
    if rep in ("L1a", "L1b", "L2"):
        return "ai_term_L1a_L2"
    return "cannot_decide"


def c7_conditions(rec, rep):
    """GSRR-43 / GSRR-57: each condition of C7 is its own problem type. 'cannot_decide' is checked first:
    conclusion unknown -> all three; only the main instrument unknown -> (i) is still derived (from C6b),
    (ii) and (iii) are cannot_decide. A condition is unresolved only if one of its own inputs is.
    (ii) is not_applicable when rep is '' (centre tables). (iii) is no_term_to_compare when the conclusion
    has no construct term or the instrument name has no family term."""
    ci, mi = rec.get("conclusion_identified"), rec.get("main_instrument_identified")
    if ci == "unresolved":
        return {k: "unresolved" for k in ("C7_i", "C7_ii", "C7_iii")}
    if ci != "1":
        return {k: "cannot_decide" for k in ("C7_i", "C7_ii", "C7_iii")}
    out = {}
    out["C7_i"] = ("unresolved" if rec.get("C6b") == "unresolved"
                   else "met" if rec.get("C6b") == "mismatch" else "not_met")
    if mi == "unresolved":
        out["C7_ii"] = out["C7_iii"] = "unresolved"
        return out
    if mi != "1":
        out["C7_ii"] = out["C7_iii"] = "cannot_decide"
        return out
    if rep == "":
        out["C7_ii"] = "not_applicable"
    elif "unresolved" in (rec.get("conclusion_ai_fatigue_term"), rep):
        out["C7_ii"] = "unresolved"
    else:
        out["C7_ii"] = "met" if (rec.get("conclusion_ai_fatigue_term") == "1" and rep in C7_WEAK_LEVELS) else "not_met"
    if "unresolved" in (rec.get("conclusion_family"), rec.get("main_instrument_family")):
        out["C7_iii"] = "unresolved"
    else:
        cf = families(rec["conclusion_family"]) - NO_FAMILY
        mf = families(rec["main_instrument_family"]) - NO_FAMILY
        out["C7_iii"] = ("no_term_to_compare" if not (cf and mf)
                         else "met" if not (cf & mf) else "not_met")
    return out


def c7(rec, rep):
    """Summary of C7: unresolved if any condition is; beyond if any condition is met; cannot_decide if
    any condition cannot be decided; otherwise within."""
    vals = list(c7_conditions(rec, rep).values())
    if "unresolved" in vals:
        return "unresolved"
    if "met" in vals:
        return "beyond"
    if "cannot_decide" in vals:
        return "cannot_decide"
    return "within"


def derive(recs, c4f_rows):
    by_rec = defaultdict(list)
    for r in c4f_rows:
        by_rec[r["record_id"]].append(r)
    for r in recs:
        r["C1_rep"] = c1_representative(r)
        r["C4f"] = c4f_summary(by_rec[r["record_id"]])
        r["C4f_gross"] = c4f_gross(by_rec[r["record_id"]])
        r["C6c"] = c6c(r, r["C1_rep"])
        r["C7"] = c7(r, r["C1_rep"])
        r.update(c7_conditions(r, r["C1_rep"]))
    return recs


# --- agreement (GSRR-47) ---------------------------------------------------

def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)   # undefined when one category only


def agreement(pairs):
    """pairs: (unit_id, value1, value2). Bootstrap resamples units (records; instrument versions for items)."""
    if not pairs:
        return {"n": 0, "percent_agreement": None, "kappa": None, "ci_low": None, "ci_high": None}
    a = [p[1] for p in pairs]
    b = [p[2] for p in pairs]
    po = sum(x == y for x, y in zip(a, b)) / len(pairs)
    by_unit = defaultdict(list)
    for p in pairs:
        by_unit[p[0]].append(p)
    units = sorted(by_unit)
    rng = random.Random(BOOT_SEED)
    boots = []
    for _ in range(BOOT_N):
        sample = [p for u in (rng.choice(units) for _ in units) for p in by_unit[u]]
        kb = cohen_kappa([p[1] for p in sample], [p[2] for p in sample])
        if kb is not None:
            boots.append(kb)
    boots.sort()
    ci = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]) if boots else (None, None)
    return {"n": len(pairs), "percent_agreement": po, "kappa": cohen_kappa(a, b),
            "ci_low": ci[0], "ci_high": ci[1]}


def pair_rows(rows1, rows2, key_fields, code, filt=None, unit_field="record_id"):
    k = lambda r: tuple(r[f] for f in key_fields)
    m2 = {k(r): r for r in rows2}
    out = []
    for r1 in rows1:
        r2 = m2.get(k(r1))
        if r2 is None or (filt and not filt(r1, r2)):
            continue
        out.append((r1[unit_field], r1.get(code, ""), r2.get(code, "")))
    return out


def c4f_judgement(res):
    """Judgement on one recalculated result: consistent / inconsistent / grossly inconsistent /
    cannot be calculated (GSRR-47)."""
    c = res["consistent"]
    if c == "yes":
        return "consistent"
    if c == "no":
        return "grossly_inconsistent" if res.get("gross") == "1" else "inconsistent"
    return "cannot_be_calculated" if c == "na" else c


def family_key(value):
    """Order-free form of a family cell, so that 'a|b' and 'b|a' count as the same choice."""
    return "|".join(sorted(families(value)))


def run_agreement(d):
    out = []
    t = {c: {n: load(d, n, c) for n in ["records", "instruments", "items", "c4f"]}
         for c in ["coder1", "coder2"]}
    for c in t:
        derive(t[c]["records"], t[c]["c4f"])
        vs = version_sets(t[c]["instruments"], t[c]["records"])
        rs = {r["record_id"]: r["set"] for r in t[c]["records"]}
        for i in t[c]["instruments"]:
            i["set"] = rs.get(i["record_id"], "")
        for it in t[c]["items"]:
            v_set = vs.get(it["version_id"], "")
            it["set"] = "calibration" if v_set == CAL_ONLY else v_set   # agreement label only; no table
            it["record_id"] = it["version_id"]
        for x in t[c]["c4f"]:
            x["set"] = rs.get(x["record_id"], "")
            x["judgement"] = c4f_judgement(x)
    ids1 = {r["record_id"] for r in t["coder1"]["records"]}
    ids2 = {r["record_id"] for r in t["coder2"]["records"]}
    out.append({"set": "all", "unit": "record", "code": "unpaired_records",
                "n": len(ids1 ^ ids2)})
    sets = sorted({r["set"] for r in t["coder1"]["records"]})
    # C6c and C7 are derived: no kappa. The C6c title input is a coded input.
    rec_codes = [f"C1_{lv}" for lv in C1_LEVELS] + ["C1_rep", "C3", "C4a", "C4b", "C4c", "C4d",
                 "C4e_codebook", "C4e_agreement", "C4f", "C4f_gross", "C5", "C6a", "C6b",
                 "title_ai_fatigue_term"]
    inst_codes = ["origin", "format", "mod_items_dropped", "mod_items_added", "mod_reworded",
                  "mod_instructions_only", "mod_response_scale", "mod_scoring", "mod_translated",
                  "C2c_backtranslation", "C2c_content_validity", "C2c_pilot", "C2c_factor_check",
                  "C2d_item_disclosure", "C2d_reliability", "C2d_factor_analysis", "C2d_reason"]
    for s in sets:
        in_set = lambda rows: [r for r in rows if r.get("set") == s]
        for code in rec_codes:
            res = agreement(pair_rows(in_set(t["coder1"]["records"]), in_set(t["coder2"]["records"]),
                                      ["record_id"], code))
            out.append(dict(set=s, unit="record", code=code, **res))
        sp = pair_rows(in_set(t["coder1"]["records"]), in_set(t["coder2"]["records"]),
                       ["record_id"], "conclusion_sentence")
        out.append({"set": s, "unit": "record", "code": "conclusion_sentence", "n": len(sp),
                    "percent_agreement": (sum(a == b for _, a, b in sp) / len(sp)) if sp else None})
        fp = [(u, family_key(a), family_key(b)) for u, a, b in
              pair_rows(in_set(t["coder1"]["records"]), in_set(t["coder2"]["records"]),
                        ["record_id"], "conclusion_family")]
        out.append({"set": s, "unit": "record", "code": "conclusion_family", "n": len(fp),
                    "percent_agreement": (sum(a == b for _, a, b in fp) / len(fp)) if fp else None})
        r1 = {(x["record_id"], x["result_id"]): x for x in in_set(t["coder1"]["c4f"])}
        r2 = {(x["record_id"], x["result_id"]): x for x in in_set(t["coder2"]["c4f"])}
        out.append({"set": s, "unit": "result", "code": "C4f_results_one_coder_only",
                    "n": len(set(r1) ^ set(r2))})
        res = agreement([(k[0], r1[k]["judgement"], r2[k]["judgement"]) for k in sorted(set(r1) & set(r2))])
        out.append(dict(set=s, unit="result", code="C4f_result_judgement", **res))
        for code in inst_codes:
            res = agreement(pair_rows(in_set(t["coder1"]["instruments"]), in_set(t["coder2"]["instruments"]),
                                      ["record_id", "instrument_id"], code))
            out.append(dict(set=s, unit="instrument", code=code, **res))
        it1, it2 = in_set(t["coder1"]["items"]), in_set(t["coder2"]["items"])
        for code in ["type", "boundary", "target"]:
            res = agreement(pair_rows(it1, it2, ["version_id", "item_no"], code, unit_field="version_id"))
            out.append(dict(set=s, unit="item", code=code, **res))
        res = agreement(pair_rows(it1, it2, ["version_id", "item_no"], "secondary_type",
                                  filt=lambda a, b: a.get("boundary") == "1" and b.get("boundary") == "1",
                                  unit_field="version_id"))
        out.append(dict(set=s, unit="item", code="secondary_type", **res))
    ai_path = d / "c4f_ai.csv"
    if ai_path.exists():
        human = load(d, "c4f", "reconciled")
        ai = read_csv(ai_path)
        res = agreement(pair_rows(human, ai, ["record_id", "result_id"], "consistent"))
        out.append(dict(set="all", unit="result", code="C4f_human_vs_ai", note="report_only", **res))
    return out


# --- tables (GSRR-56, GSRR-57, GSRR-62) ------------------------------------

MULTI_VALUE = {"C3"}


def count_table(rows, key, label, n_studies=None):
    """Counts per value. Proportions only if the table's own study count is >= MIN_STUDIES.
    Multi-value codes (all that apply, '|'-separated) count each value once per row."""
    if n_studies is None:
        n_studies = len({r.get("record_id", id(r)) for r in rows})
    vals = []
    for r in rows:
        v = r.get(key, "")
        vals += v.split("|") if key in MULTI_VALUE and v else [v]
    denom_rows = [r for r in rows if r.get(key, "") not in EXCLUDED]
    allow_prop = n_studies >= MIN_STUDIES
    return [{**label, "code": key, "value": v, "count": n, "denominator": len(denom_rows),
             "studies": n_studies,
             "proportion": (n / len(denom_rows)) if (allow_prop and v not in EXCLUDED and denom_rows) else None}
            for v, n in sorted(Counter(vals).items())]


# The C7 summary value is reported only in the per-study table (GSRR-43); the tables count each condition.
RECORD_CODES = ["C1_rep", "C3", "C4a", "C4b", "C4c", "C4d", "C4e_codebook", "C4e_agreement",
                "C4f", "C4f_gross", "C5", "C6a", "C6b", "C6c", "C7_i", "C7_ii", "C7_iii"]
# GSRR-12 / GSRR-64: the centre tables are split by attribution, so they leave out C1, C6c and C7 (ii)
CENTRE_OMIT = {"C1_rep", "C6c", "C7_ii"}
INSTRUMENT_CODES = ["origin", "format", "mod_items_dropped", "mod_items_added", "mod_reworded",
                    "mod_instructions_only", "mod_response_scale", "mod_scoring", "mod_translated",
                    "C2c_backtranslation", "C2c_content_validity", "C2c_pilot", "C2c_factor_check",
                    "C2d_item_disclosure", "C2d_reliability", "C2d_factor_analysis", "C2d_reason"]


def record_tables(recs, insts, label):
    out = []
    n = len({r["record_id"] for r in recs})
    for key in RECORD_CODES:
        out += count_table(recs, key, label, n)
    for key in INSTRUMENT_CODES:
        out += count_table(insts, key, label, n)
    return out


def item_types(it, lenient):
    """Types an item counts for. Lenient: also its secondary type, once, if different."""
    ts = [it["type"]]
    if lenient and it.get("boundary") == "1" and it.get("secondary_type") and it["secondary_type"] != it["type"]:
        ts.append(it["secondary_type"])
    return ts


def c2b_tables(items, vsets, set_name, lenient=False, insts=()):
    """Per instrument version first seen in `set_name` (vsets from version_sets), with items available.
    The denominator is the number of coded items (printed, or item_source = source); unresolved items stay in it
    as their own category; the full item count (from `insts`) is shown beside it. Versions without items are
    counted outside ('items_unavailable'). Counts are always given; proportions only if
    >= MIN_NEW_INSTRUMENTS versions have items."""
    first_seen = {v for v, s in vsets.items() if s == set_name}
    by_version = defaultdict(list)
    for it in items:
        by_version[it["version_id"]].append(it)
    full = defaultdict(set)
    for i in insts:
        full[i["version_id"]].add(i.get("items_full", ""))
    available = sorted(v for v in first_seen if by_version.get(v))
    unavailable = sorted(v for v in first_seen if not by_version.get(v))
    prop_ok = len(available) >= MIN_NEW_INSTRUMENTS
    rows = []
    for vid in available:
        its = by_version[vid]
        c = Counter(t for it in its for t in item_types(it, lenient))
        full_n = "|".join(sorted(full.get(vid, ())))
        from_source = sum(1 for it in its if it.get("item_source") == "source")
        for t in C2B_TYPES + ["unresolved"]:
            rows.append({"set": set_name, "version_id": vid, "type": t, "count": c[t],
                         "denominator": len(its), "items_full": full_n, "items_from_source": from_source,
                         "proportion": (c[t] / len(its)) if prop_ok else None})
    for t in C2B_TYPES:
        rows.append({"set": set_name, "version_id": "ALL", "type": t,
                     "instruments_with_type": sum(1 for v in available
                                                  if any(t in item_types(i, lenient) for i in by_version[v])),
                     "denominator": len(available)})
    tg = Counter(it["target"] for v in available for it in by_version[v]
                 if set(item_types(it, lenient)) & TARGETED_TYPES)
    for tv, n in sorted(tg.items()):
        rows.append({"set": set_name, "version_id": "ALL", "type": "target:" + tv, "count": n})
    rows.append({"set": set_name, "version_id": "SUMMARY", "type": "instruments",
                 "with_items": len(available), "items_unavailable": len(unavailable),
                 "proportions_reported": prop_ok})
    return rows


def rq4_counts(recs, links, set_name):
    group = {l["record_id"]: l["group_id"] for l in links}
    rows = [r for r in recs if r["set"] == set_name]
    studies = {group.get(r["record_id"], r["record_id"]) for r in rows}
    linked = [r for r in rows if r["record_id"] in group]
    return {"set": set_name, "records": len(rows), "studies": len(studies),
            "records_in_e5_groups": len(linked),
            "signs_not_confirmed": sum(1 for r in rows if r.get("C5") == "signs_not_confirmed")}


PROBLEMS = {
    "C4a inconsistent": ("C4a", {"inconsistent"}),
    "C4b inconsistent": ("C4b", {"inconsistent"}),
    "C4c inconsistent": ("C4c", {"inconsistent"}),
    "C4d inconsistent": ("C4d", {"inconsistent"}),
    "C4e codebook not available": ("C4e_codebook", {"no"}),
    "C4e agreement none": ("C4e_agreement", {"none"}),
    "C4f any inconsistency": ("C4f", {"any_inconsistency"}),
    "C4f any gross inconsistency": ("C4f_gross", {"any_gross"}),
    "C5 signs not confirmed": ("C5", {"signs_not_confirmed"}),
    "C6a different family": ("C6a", {"different_family"}),
    "C6b mismatch": ("C6b", {"mismatch"}),
    "C6c AI-fatigue term with L3 to L6": ("C6c", {"ai_term_L3_L6"}),
    "C7 (i) causal wording not supported by the design": ("C7_i", {"met"}),
    "C7 (ii) AI-fatigue term with attribution at L3 to L6": ("C7_ii", {"met"}),
    "C7 (iii) conclusion term and instrument name in different term families": ("C7_iii", {"met"}),
}
# GSRR-57: values that can show or not show the problem. Every other value makes the record not evaluable.
EVALUABLE = {
    "C4a": {"consistent", "inconsistent"}, "C4b": {"consistent", "inconsistent"},
    "C4c": {"consistent", "inconsistent"}, "C4d": {"consistent", "inconsistent"},
    "C4e_codebook": {"yes", "no"}, "C4e_agreement": {"value_given", "index_only", "none"},
    "C4f": {"any_inconsistency", "none"}, "C4f_gross": {"any_gross", "no_gross"},
    "C5": {"e5_group", "signs_not_confirmed", "no_signs"},
    "C6a": {"same_family", "different_family"}, "C6b": {"match", "mismatch"},
    "C6c": {"ai_term_L3_L6", "ai_term_L1a_L2", "no_ai_term"},
    "C7_i": {"met", "not_met"}, "C7_ii": {"met", "not_met"}, "C7_iii": {"met", "not_met"},
}


def c6a_c7iii_overlap(rows):
    """Records in which both name checks (C6a and C7 (iii)) are met, so that the two problem
    types are not read as independent."""
    return sum(1 for r in rows if r.get("C6a") == "different_family" and r.get("C7_iii") == "met")


def problem_statements(rows):
    """GSRR-57: count among the records evaluable for the problem type (EVALUABLE); each statement gives the
    count, the evaluable records, the not-evaluable ones (unresolved counted separately) and the unresolved ones;
    none evaluable -> "could not be evaluated"."""
    out = []
    for name, (key, bad) in PROBLEMS.items():
        vals = [r.get(key, "") for r in rows]
        evaluable = [v for v in vals if v in EVALUABLE[key]]
        n = sum(1 for v in evaluable if v in bad)
        if not evaluable:
            st = "could not be evaluated"
        else:
            st = "was observed in the main set" if n else "was not observed in the main set"
        out.append({"problem_type": name, "count": n, "evaluable": len(evaluable),
                    "not_evaluable": len(vals) - len(evaluable) - vals.count("unresolved"),
                    "unresolved": vals.count("unresolved"), "statement": st})
    return out


def c4f_result_table(recs, c4f_rows, set_name):
    """GSRR-56: C4f per recalculated result, beside the record summary. Results cluster in records,
    so the number of recalculated results per record is given as a distribution."""
    ids = {r["record_id"] for r in recs if r["set"] == set_name}
    rows = [r for r in c4f_rows if r["record_id"] in ids]
    per_rec = Counter(r["record_id"] for r in rows)
    dist = Counter(per_rec.get(i, 0) for i in ids)
    vals = Counter(r["consistent"] for r in rows)
    out = [{"set": set_name, "row": "results", "value": k, "count": vals[k]}
           for k in ["yes", "no", "na", "unresolved"]]
    out.append({"set": set_name, "row": "results", "value": "gross", "count": sum(1 for r in rows if r.get("gross") == "1")})
    src = Counter((r.get("source", ""), r["consistent"]) for r in rows)
    out += [{"set": set_name, "row": f"results_from_{so}", "value": k, "count": src[(so, k)]}
            for so in ["text", "table"] for k in ["yes", "no", "na", "unresolved"]]
    out += [{"set": set_name, "row": "results_per_record", "value": str(k), "count": n}
            for k, n in sorted(dist.items())]
    return out


INSTRUMENT_USE_CODES = ["language", "format", "items_full"]       # one value per version expected; all listed
RECORD_COUNT_CODES = ["origin", "C2d_item_disclosure"]               # can differ between records of a version


def value_counts(values):
    """'a:3; b:2' (sorted by value): the number of records with each value."""
    return "; ".join(f"{v}:{n}" for v, n in sorted(Counter(values).items()))


def refers_to_ai(recs):
    """Whether the items of a version refer to AI (C1 L1a only; a property of the wording), from the records
    that use it as the main instrument. Values that differ across records are listed."""
    vals = set()
    for r in recs:
        v = r.get("C1_L1a", "")
        vals.add("unresolved" if v == "unresolved" else "yes" if v == "1" else "no")
    return "|".join(sorted(vals)) if vals else "not_main_instrument"


def instructions_refer_to_ai(recs):
    """Number of records with each value of C1 L1b (instructions or stem refer to AI), which can differ
    between records that use the same version: 'L1b:3; none:2'."""
    if not recs:
        return "not_main_instrument"
    return value_counts("unresolved" if r.get("C1_L1b") == "unresolved" else "L1b" if r.get("C1_L1b") == "1"
                        else "none" for r in recs)


def instruments_used(recs, insts, items, vsets, set_name):
    """GSRR-56: every instrument version used by a record of `set_name`, whichever set it was first
    seen in, with item-type counts (no proportions). Not a comparison between sets (GSRR-57).
    Calibration-only versions are in no set and never appear here."""
    ids = {r["record_id"] for r in recs if r["set"] == set_name}
    rec_by_id = {r["record_id"]: r for r in recs}
    by_version = defaultdict(list)
    for it in items:
        by_version[it["version_id"]].append(it)
    used = defaultdict(list)
    for i in insts:
        if i["record_id"] in ids:
            used[i["version_id"]].append(i)
    out = []
    for vid in sorted(used):
        its = by_version.get(vid, [])
        c = Counter(it["type"] for it in its)
        mains = [rec_by_id[i["record_id"]] for i in used[vid]
                 if i.get("instrument_id") == "main" and i["record_id"] in rec_by_id]
        row = {"set": set_name, "version_id": vid, "first_seen": vsets.get(vid, ""),
               "records_using": len({i["record_id"] for i in used[vid]}), "items_available": len(its),
               "refers_to_ai": refers_to_ai(mains), "instructions_refer_to_ai": instructions_refer_to_ai(mains)}
        for k in INSTRUMENT_USE_CODES:
            row[k] = "|".join(sorted({i.get(k, "") for i in used[vid]}))
        for k in RECORD_COUNT_CODES:
            row[k] = value_counts(i.get(k, "") for i in {(x["record_id"], x.get(k, "")): x
                                                         for x in used[vid]}.values())
        for t in C2B_TYPES + ["unresolved"]:
            row[t] = c[t] if its else None
        out.append(row)
    return out


PER_STUDY_CODES = ["C1_rep", "C3", "C4a", "C4b", "C4c", "C4d", "C4e_codebook", "C4e_agreement",
                   "C4f", "C4f_gross", "C5", "C6a", "C6b", "C6c", "C7", "C7_i", "C7_ii", "C7_iii"]


def exploration_calibration_flag(recs):
    """GSRR-39 (small pool): True if every exploration study was used for calibration (optional records
    column calibration_draw = 1). The whole exploration table is then calibration material."""
    expl = {r["record_id"] for r in recs if r["set"] == "exploration"}
    drawn = {r["record_id"] for r in recs if r["set"] == "exploration" and r.get("calibration_draw") == "1"}
    return all_exploration_drawn(drawn, expl)


def per_study_table(recs):
    """Supplementary table: one row per coded record of the primary sets, C1-C7 values (no item text)."""
    rows = [r for r in recs if r["set"] in PRIMARY_SETS]
    rows.sort(key=lambda r: (PRIMARY_SETS.index(r["set"]), r["record_id"]))
    return [{"record_id": r["record_id"], "set": r["set"], "population": r["population"],
             "centre": r["centre"], "calibration_draw": r.get("calibration_draw", ""),
             **{k: r.get(k, "") for k in PER_STUDY_CODES}} for r in rows]


def build_tables(d, coder="reconciled"):
    c4f_rows = load(d, "c4f", coder)
    recs = derive(load(d, "records", coder), c4f_rows)
    insts = load(d, "instruments", coder)
    items = load(d, "items", coder)
    links = read_csv(d / "links.csv")
    rs = {r["record_id"]: r["set"] for r in recs}
    for i in insts:
        i["set"] = rs.get(i["record_id"], "")
    vsets = version_sets(insts, recs)
    tables, c2b, rq4, c4f_res, used = [], [], [], [], []
    cal_flag = exploration_calibration_flag(recs)
    for s in PRIMARY_SETS:          # calibration records are never in these sets
        r_s = [r for r in recs if r["set"] == s]
        i_s = [i for i in insts if i["set"] == s]
        extra = {"calibration_material": cal_flag} if s == "exploration" else {}
        tables += record_tables(r_s, i_s, {"set": s, "split": "all", "group": "all", **extra})
        for g in sorted({r["population"] for r in r_s}):
            ids = {r["record_id"] for r in r_s if r["population"] == g}
            tables += record_tables([r for r in r_s if r["record_id"] in ids],
                                    [i for i in i_s if i["record_id"] in ids],
                                    {"set": s, "split": "population", "group": g, **extra})
        for c in ["A", "B"]:          # SQ1: RQ2-RQ5 and C7 (i), (iii)
            ids = {r["record_id"] for r in r_s if r["centre"] == c}
            sub = [dict(r) for r in r_s if r["record_id"] in ids]
            for r in sub:
                r["C7"] = c7(dict(r, conclusion_ai_fatigue_term="0"), "")
                r.update(c7_conditions(r, ""))
            t = record_tables(sub, [i for i in i_s if i["record_id"] in ids],
                              {"set": s, "split": "centre", "group": c, **extra})
            tables += [x for x in t if x["code"] not in CENTRE_OMIT]
        c2b += c2b_tables(items, vsets, s, insts=insts)
        rq4.append(rq4_counts(recs, links, s))
        c4f_res += c4f_result_table(recs, c4f_rows, s)
        used += instruments_used(recs, insts, items, vsets, s)
    conf = [r for r in recs if r["set"] == "main"]
    return {"recs": recs, "insts": insts, "exploration_calibration_material": cal_flag, "tables": tables, "c2b": c2b, "rq4": rq4, "vsets": vsets, "items": items,
            "c4f_results": c4f_res, "instruments_used": used, "per_study": per_study_table(recs),
            "problems": problem_statements(conf), "n_main": len(conf),
            "c6a_c7iii_overlap": c6a_c7iii_overlap(conf)}


def sensitivity(d):
    """GSRR-62: S1, S2 and S4 on the problem statements; S3 on C2b."""
    base = build_tables(d)
    recs = base["recs"]
    conf = [r for r in recs if r["set"] == "main"]
    out = []
    out += [dict(s, analysis="S1 peer-reviewed only") for s in
            problem_statements([r for r in conf if r.get("peer_reviewed") == "1"])]
    out += [dict(s, analysis="S2 signs-not-confirmed removed") for s in
            problem_statements([r for r in conf if r.get("C5") != "signs_not_confirmed"])]
    s3 = [dict(r, analysis="S3 lenient C2b") for r in c2b_tables(base["items"], base["vsets"], "main", lenient=True, insts=base["insts"])]
    s4 = []
    for c in ["coder1", "coder2"]:
        if all((d / f"{k}_{c}.csv").exists() for k in REQUIRED):
            s4 += [dict(s, analysis=f"S4 {c} values") for s in build_tables(d, c)["problems"]]
    return out + s4, s3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", type=Path)
    ap.add_argument("--coder", default="reconciled")
    ap.add_argument("--agreement", type=Path)
    ap.add_argument("--draw-calibration", type=Path)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--drawn", type=Path)
    ap.add_argument("--exploration", type=Path,
                    help="IDs (text) or a records CSV; only the primary studies of the exploration set are used")
    ap.add_argument("--instruments", type=Path, help="instruments CSV; its IDs are refused as draw sources")
    ap.add_argument("--screening-order", type=Path)
    a = ap.parse_args()
    if a.draw_calibration:
        ids = a.draw_calibration.read_text(encoding="utf-8").split()
        drawn = a.drawn.read_text(encoding="utf-8").split() if a.drawn else []
        expl, inst_ids = [], []
        if a.exploration and a.exploration.suffix == ".csv":      # a records table: primary studies only
            expl = exploration_study_ids(read_csv(a.exploration))
        elif a.exploration:
            expl = a.exploration.read_text(encoding="utf-8").split()
        if a.instruments:
            inst_ids = sorted({r["version_id"] for r in read_csv(a.instruments)} |
                              {r.get("instrument_id", "") for r in read_csv(a.instruments)})
        print("\n".join(draw_calibration(ids, a.round, drawn, expl, inst_ids)))
    elif a.screening_order:
        for g, i in screening_order(read_csv(a.screening_order)):
            print(f"{g},{i}")
    elif a.tables:
        try:
            res = build_tables(a.tables, a.coder)
        except InputError as e:
            print(f"STOPPED: {e}", file=sys.stderr)
            return 3
        sens, s3 = sensitivity(a.tables)
        out = a.tables / "out"
        out.mkdir(exist_ok=True)
        write_csv(out / "tables.csv", res["tables"])
        write_csv(out / "c2b.csv", res["c2b"])
        write_csv(out / "rq4.csv", res["rq4"])
        write_csv(out / "c4f_results.csv", res["c4f_results"])
        write_csv(out / "instruments_used.csv", res["instruments_used"])
        write_csv(out / "per_study.csv", res["per_study"])
        write_csv(out / "problem_statements.csv", res["problems"])
        write_csv(out / "sensitivity.csv", sens)
        write_csv(out / "sensitivity_c2b_lenient.csv", s3)
        write_csv(out / "c6a_c7iii_overlap.csv", [{"set": "main", "records_both_met": res["c6a_c7iii_overlap"]}])
        print(f"main studies={res['n_main']} proportions={'yes' if res['n_main'] >= MIN_STUDIES else 'no'}"
              f" exploration_calibration_material={res['exploration_calibration_material']}")
    elif a.agreement:
        out = a.agreement / "out"
        out.mkdir(exist_ok=True)
        try:
            rows = run_agreement(a.agreement)
        except InputError as e:
            print(f"STOPPED: {e}", file=sys.stderr)
            return 3
        write_csv(out / "agreement.csv", rows)
        print(f"agreement rows={len(rows)}")
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
