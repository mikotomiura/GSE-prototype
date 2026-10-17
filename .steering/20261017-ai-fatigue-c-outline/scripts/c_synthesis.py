"""Registered synthesis for the AI-fatigue methodological review (registration draft 0.4).

Reads the code tables (CSV) and writes the descriptive tables. Implements:
- calibration draws and the post-registration screening order (GSRR-33, GSRR-39)
- derived values: C1 representative value, C4f record summary, C7 (GSRR-43, GSRR-48)
- agreement: percentage agreement and Cohen's kappa with bootstrap CI (GSRR-47)
- counts with the minimum-size rule (GSRR-39, GSRR-56, GSRR-57)

Usage:
    python3 c_synthesis.py --tables <dir>            # write tables from reconciled codes
    python3 c_synthesis.py --agreement <dir>         # agreement between coder1 and coder2
    python3 c_synthesis.py --draw-calibration <pool_ids.txt> --round K [--drawn <drawn.txt>] [--exploration <expl_ids.txt>]
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
MISSING = {"not_reported", "not_verifiable", "not_applicable", "unresolved", ""}
MIN_STUDIES = 10
MIN_NEW_INSTRUMENTS = 3
CAL_SEED = 20261017
EXPL_CAL_SEED = 20261019
SMALL_POOL = 25
SCREEN_SEED = 20261018
BOOT_SEED = 20261017
BOOT_N = 2000


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# --- draws (GSRR-33, GSRR-39) ---------------------------------------------

def draw_calibration(pool_ids, round_k, already_drawn=(), exploration_ids=()):
    """Round k draws 5 from the IDs not yet drawn.

    Pool of 25 or fewer: draw from the exploration set instead (seed EXPL_CAL_SEED + k - 1,
    at most two rounds). Otherwise draw from the pool (seed CAL_SEED + k - 1, at most three rounds).
    """
    if len(pool_ids) <= SMALL_POOL:
        if round_k > 2:
            raise ValueError("small pool: at most two calibration rounds on exploration records")
        source, seed = exploration_ids, EXPL_CAL_SEED
    else:
        if round_k > 3:
            raise ValueError("at most three calibration rounds")
        source, seed = pool_ids, CAL_SEED
    remaining = sorted(set(source) - set(already_drawn))
    rng = random.Random(seed + round_k - 1)
    return sorted(rng.sample(remaining, min(5, len(remaining))))


def screening_order(candidates):
    """Shuffle IDs (sorted alphabetically) within each group, then interleave the groups
    one record at a time in the listed order (GSRR-33)."""
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
    """Per-record summary: any inconsistency / none / cannot be calculated."""
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


def c7(rec, rep):
    """Derived from reconciled codes. Conditions (i)-(iii) of C7."""
    inputs = [rec.get("C6b", ""), rec.get("conclusion_ai_fatigue_term", ""),
              rec.get("conclusion_family", ""), rec.get("main_instrument_family", ""), rep]
    if "unresolved" in inputs:
        return "unresolved"
    if rec.get("conclusion_family", "") == "" or rec.get("main_instrument_family", "") == "":
        return "cannot_decide"
    cond_i = rec.get("C6b") == "mismatch"
    cond_ii = rec.get("conclusion_ai_fatigue_term") == "1" and rep in C7_WEAK_LEVELS
    no_term = {"none", "no_family_term"}
    cond_iii = (rec["conclusion_family"] not in no_term
                and rec["main_instrument_family"] not in no_term
                and rec["conclusion_family"] != rec["main_instrument_family"])
    return "beyond" if (cond_i or cond_ii or cond_iii) else "within"


# --- agreement (GSRR-47) ---------------------------------------------------

def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def agreement(pairs, unit_ids):
    """pairs: list of (unit_id, value1, value2). Bootstrap over records (unit_ids)."""
    a = [p[1] for p in pairs]
    b = [p[2] for p in pairs]
    po = sum(x == y for x, y in zip(a, b)) / len(pairs) if pairs else None
    k = cohen_kappa(a, b)
    by_unit = defaultdict(list)
    for uid, p in zip(unit_ids, pairs):
        by_unit[uid].append(p)
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
    return {"n": len(pairs), "percent_agreement": po, "kappa": k, "ci_low": ci[0], "ci_high": ci[1]}


# --- tables (GSRR-56, GSRR-57) ---------------------------------------------

def count_table(rows, key, set_name):
    vals = [r[key] for r in rows]
    denom = [v for v in vals if v not in MISSING]
    c = Counter(vals)
    out = []
    for v, n in sorted(c.items()):
        prop = (n / len(denom)) if (len(rows) >= MIN_STUDIES and v not in MISSING and denom) else None
        out.append({"set": set_name, "code": key, "value": v, "count": n,
                    "denominator": len(denom), "proportion": prop})
    return out


def c2b_per_instrument(items, versions_first_seen):
    out = []
    by_version = defaultdict(list)
    for it in items:
        by_version[it["version_id"]].append(it)
    for vid in sorted(versions_first_seen):
        its = by_version.get(vid, [])
        n = len(its)
        c = Counter(it["type"] for it in its)
        for t in C2B_TYPES:
            out.append({"version_id": vid, "type": t, "count": c[t], "denominator": n,
                        "proportion": c[t] / n if n else None})
    return out


def build_tables(d):
    recs = read_csv(d / "records_reconciled.csv")
    c4f_rows = read_csv(d / "c4f_reconciled.csv")
    items = read_csv(d / "items_reconciled.csv")
    insts = read_csv(d / "instruments_reconciled.csv")
    by_rec = defaultdict(list)
    for r in c4f_rows:
        by_rec[r["record_id"]].append(r)
    for r in recs:
        r["C1_rep"] = c1_representative(r)
        r["C4f"] = c4f_summary(by_rec[r["record_id"]])
        r["C7"] = c7(r, r["C1_rep"])
    tables = []
    for set_name in ["confirmation", "exploration", "late"]:
        rows = [r for r in recs if r["set"] == set_name]
        for key in ["C1_rep", "C3", "C4a", "C4b", "C4c", "C4d", "C4e", "C4f", "C5", "C6a", "C6b", "C7"]:
            tables.extend(count_table(rows, key, set_name))
    seen_explore = {i["version_id"] for i in insts if i["set"] == "exploration"}
    first_seen = {i["version_id"] for i in insts if i["set"] == "confirmation"} - seen_explore
    conf_studies = [r for r in recs if r["set"] == "confirmation"]
    c2b = c2b_per_instrument(items, first_seen) if len(first_seen) >= MIN_NEW_INSTRUMENTS else []
    observed = problem_statements([r for r in recs if r["set"] == "confirmation"])
    return recs, tables, c2b, observed, len(conf_studies), len(first_seen)


def problem_statements(rows):
    """GSRR-57: observed / not observed in the confirmation set, with count and denominator."""
    checks = {
        "C4a inconsistent": lambda r: r["C4a"] == "inconsistent",
        "C4b inconsistent": lambda r: r["C4b"] == "inconsistent",
        "C4c inconsistent": lambda r: r["C4c"] == "inconsistent",
        "C4d inconsistent": lambda r: r["C4d"] == "inconsistent",
        "C4e codebook not available or agreement none": lambda r: r["C4e"] in {"codebook_no", "agreement_none"},
        "C4f any inconsistency": lambda r: r["C4f"] == "any_inconsistency",
        "C5 signs not confirmed": lambda r: r["C5"] == "signs_not_confirmed",
        "C6a different family": lambda r: r["C6a"] == "different_family",
        "C6b mismatch": lambda r: r["C6b"] == "mismatch",
        "C7 beyond": lambda r: r["C7"] == "beyond",
    }
    out = []
    for name, f in checks.items():
        n = sum(1 for r in rows if f(r))
        out.append({"problem_type": name, "count": n, "denominator": len(rows),
                    "statement": "was observed in the confirmation set" if n else "was not observed in the confirmation set"})
    return out


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", type=Path)
    ap.add_argument("--agreement", type=Path)
    ap.add_argument("--draw-calibration", type=Path)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--drawn", type=Path)
    ap.add_argument("--exploration", type=Path)
    ap.add_argument("--screening-order", type=Path)
    a = ap.parse_args()
    if a.draw_calibration:
        ids = [x.strip() for x in a.draw_calibration.read_text(encoding="utf-8").split() if x.strip()]
        drawn = a.drawn.read_text(encoding="utf-8").split() if a.drawn else []
        expl = a.exploration.read_text(encoding="utf-8").split() if a.exploration else []
        print("\n".join(draw_calibration(ids, a.round, drawn, expl)))
    elif a.screening_order:
        for g, i in screening_order(read_csv(a.screening_order)):
            print(f"{g},{i}")
    elif a.tables:
        recs, tables, c2b, observed, n_conf, n_new = build_tables(a.tables)
        out = a.tables / "out"
        out.mkdir(exist_ok=True)
        write_csv(out / "tables.csv", tables)
        write_csv(out / "c2b_per_instrument.csv", c2b)
        write_csv(out / "problem_statements.csv", observed)
        print(f"confirmation studies={n_conf} new instruments={n_new} "
              f"proportions={'yes' if n_conf >= MIN_STUDIES else 'no'} "
              f"c2b_proportions={'yes' if n_new >= MIN_NEW_INSTRUMENTS else 'no'}")
    elif a.agreement:
        recs = read_csv(a.agreement / "records_coders.csv")
        by = defaultdict(dict)
        for r in recs:
            by[r["record_id"]][r["coder"]] = r
        rows = []
        for code in [f"C1_{lv}" for lv in C1_LEVELS] + ["C3", "C4a", "C4b", "C4c", "C4d", "C4e", "C5", "C6a", "C6b"]:
            pairs, units = [], []
            for rid, cs in sorted(by.items()):
                if "coder1" in cs and "coder2" in cs:
                    pairs.append((rid, cs["coder1"][code], cs["coder2"][code]))
                    units.append(rid)
            res = agreement(pairs, units)
            res["code"] = code
            rows.append(res)
        out = a.agreement / "out"
        out.mkdir(exist_ok=True)
        write_csv(out / "agreement.csv", rows)
        print(f"agreement rows={len(rows)}")
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
