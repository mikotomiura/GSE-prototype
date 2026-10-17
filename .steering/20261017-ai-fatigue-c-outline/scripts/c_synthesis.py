"""Registered synthesis for the AI-fatigue methodological review (registration draft 0.5).

Implements, from the code tables (CSV):
- calibration draws and the post-registration screening order (GSRR-33, GSRR-39)
- derived values: C1 representative value, C4f record summary, C7 (GSRR-43, GSRR-48)
- agreement per set: percentage agreement and Cohen's kappa with bootstrap CI (GSRR-47)
- tables per set, population group and centre; C2a/C2c/C2d; C2b per instrument;
  RQ4 study counts; problem statements; sensitivity analyses 1-4 (GSRR-56, GSRR-57, GSRR-62)

Input files (one row per unit; `coder` is coder1 / coder2 / reconciled):
  records_<coder>.csv      record-level codes (C1 per main instrument, C3-C7 inputs)
  instruments_<coder>.csv  instrument-level codes (C2a, C2c, C2d)
  items_<coder>.csv        item-level codes (C2b)
  c4f_<coder>.csv          one row per recalculated result
  links.csv                E5 links (record_id, group_id)

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
NO_FAMILY = {"no_family_term", "none", "unnamed_or_not_verifiable"}
MIN_STUDIES = 10
MIN_NEW_INSTRUMENTS = 3
CAL_SEED = 20261017
EXPL_CAL_SEED = 20261019
SMALL_POOL = 24          # 15 removable by calibration + 10 needed - 1
SCREEN_SEED = 20261018
BOOT_SEED = 20261017
BOOT_N = 2000
PRIMARY_SETS = ["confirmation", "exploration", "late"]


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

def draw_calibration(pool_ids, round_k, already_drawn=(), exploration_ids=()):
    """Round k draws 5 from the IDs not yet drawn (seed + k - 1).

    Pool of SMALL_POOL or fewer: draw from the exploration set (at most two rounds).
    Otherwise draw from the pool (at most three rounds).
    """
    if len(pool_ids) <= SMALL_POOL:
        if not exploration_ids:
            raise ValueError("small pool: exploration IDs are required (--exploration)")
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
    """Per record: any_inconsistency / none / cannot_be_calculated / not_applicable."""
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
    """(i)-(iii) of C7. 'cannot_decide' only if the conclusion or the main instrument
    cannot be identified."""
    if rec.get("conclusion_identified") != "1" or rec.get("main_instrument_identified") != "1":
        return "cannot_decide"
    inputs = [rec.get("C6b", ""), rec.get("conclusion_ai_fatigue_term", ""),
              rec.get("conclusion_family", ""), rec.get("main_instrument_family", ""), rep]
    if "unresolved" in inputs:
        return "unresolved"
    cond_i = rec.get("C6b") == "mismatch"
    cond_ii = rec.get("conclusion_ai_fatigue_term") == "1" and rep in C7_WEAK_LEVELS
    cf, mf = families(rec["conclusion_family"]), families(rec["main_instrument_family"])
    cond_iii = bool(cf - NO_FAMILY) and bool(mf - NO_FAMILY) and not (cf & mf)
    return "beyond" if (cond_i or cond_ii or cond_iii) else "within"


def derive(recs, c4f_rows):
    by_rec = defaultdict(list)
    for r in c4f_rows:
        by_rec[r["record_id"]].append(r)
    for r in recs:
        r["C1_rep"] = c1_representative(r)
        r["C4f"] = c4f_summary(by_rec[r["record_id"]])
        r["C7"] = c7(r, r["C1_rep"])
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


def run_agreement(d):
    out = []
    t = {c: {n: read_csv(d / f"{n}_{c}.csv") for n in ["records", "instruments", "items", "c4f"]}
         for c in ["coder1", "coder2"]}
    for c in t:
        derive(t[c]["records"], t[c]["c4f"])
    sets = sorted({r["set"] for r in t["coder1"]["records"]})
    rec_codes = [f"C1_{lv}" for lv in C1_LEVELS] + ["C1_rep", "C3", "C4a", "C4b", "C4c", "C4d",
                 "C4e_codebook", "C4e_agreement", "C5", "C6a", "C6b", "conclusion_sentence"]
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
    return out


# --- tables (GSRR-56, GSRR-57, GSRR-62) ------------------------------------

def count_table(rows, key, label):
    vals = [r.get(key, "") for r in rows]
    denom = [v for v in vals if v not in EXCLUDED]
    allow_prop = len(rows) >= MIN_STUDIES
    return [{**label, "code": key, "value": v, "count": n, "denominator": len(denom),
             "proportion": (n / len(denom)) if (allow_prop and v not in EXCLUDED and denom) else None}
            for v, n in sorted(Counter(vals).items())]


RECORD_CODES = ["C1_rep", "C3", "C4a", "C4b", "C4c", "C4d", "C4e_codebook", "C4e_agreement",
                "C4f", "C5", "C6a", "C6b", "C7"]
INSTRUMENT_CODES = ["origin", "format", "mod_items_dropped", "mod_items_added", "mod_reworded",
                    "mod_instructions_only", "mod_response_scale", "mod_scoring", "mod_translated",
                    "C2c_backtranslation", "C2c_content_validity", "C2c_pilot", "C2c_factor_check",
                    "C2d_item_disclosure", "C2d_reliability", "C2d_factor_analysis", "C2d_reason"]


def record_tables(recs, insts, label):
    out = []
    for key in RECORD_CODES:
        out += count_table(recs, key, label)
    for key in INSTRUMENT_CODES:
        out += count_table(insts, key, label)
    return out


def c2b_tables(items, insts, set_name, lenient=False):
    """Per instrument version first seen in `set_name` (not in exploration), with items available."""
    explore = {i["version_id"] for i in insts if i["set"] == "exploration"}
    in_set = {i["version_id"] for i in insts if i["set"] == set_name}
    first_seen = in_set - explore if set_name != "exploration" else in_set
    by_version = defaultdict(list)
    for it in items:
        by_version[it["version_id"]].append(it)
    available = sorted(v for v in first_seen if by_version.get(v))
    unavailable = sorted(v for v in first_seen if not by_version.get(v))
    rows = []
    if len(available) >= MIN_NEW_INSTRUMENTS:
        for vid in available:
            its = by_version[vid]
            c = Counter(it["type"] for it in its)
            if lenient:
                c.update(it["secondary_type"] for it in its if it.get("boundary") == "1" and it.get("secondary_type"))
            for t in C2B_TYPES + ["unresolved"]:
                rows.append({"set": set_name, "version_id": vid, "type": t, "count": c[t],
                             "denominator": len(its), "proportion": c[t] / len(its)})
        for t in C2B_TYPES:
            rows.append({"set": set_name, "version_id": "ALL", "type": t,
                         "instruments_with_type": sum(1 for v in available if any(i["type"] == t for i in by_version[v])),
                         "denominator": len(available)})
        tg = Counter(it["target"] for v in available for it in by_version[v] if it["type"] in TARGETED_TYPES)
        for tv, n in sorted(tg.items()):
            rows.append({"set": set_name, "version_id": "ALL", "type": "target:" + tv, "count": n})
    rows.append({"set": set_name, "version_id": "SUMMARY", "type": "instruments",
                 "with_items": len(available), "items_unavailable": len(unavailable),
                 "proportions_reported": len(available) >= MIN_NEW_INSTRUMENTS})
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
    "C5 signs not confirmed": ("C5", {"signs_not_confirmed"}),
    "C6a different family": ("C6a", {"different_family"}),
    "C6b mismatch": ("C6b", {"mismatch"}),
    "C7 beyond": ("C7", {"beyond"}),
}


def problem_statements(rows):
    """GSRR-57: count among evaluable records; unresolved shown; none evaluable -> not evaluable."""
    out = []
    for name, (key, bad) in PROBLEMS.items():
        vals = [r.get(key, "") for r in rows]
        evaluable = [v for v in vals if v not in EXCLUDED]
        n = sum(1 for v in evaluable if v in bad)
        if not evaluable:
            st = "could not be evaluated"
        else:
            st = "was observed in the confirmation set" if n else "was not observed in the confirmation set"
        out.append({"problem_type": name, "count": n, "evaluable": len(evaluable),
                    "unresolved": vals.count("unresolved"), "statement": st})
    return out


def build_tables(d, coder="reconciled"):
    recs = derive(read_csv(d / f"records_{coder}.csv"), read_csv(d / f"c4f_{coder}.csv"))
    insts = read_csv(d / f"instruments_{coder}.csv")
    items = read_csv(d / f"items_{coder}.csv")
    links = read_csv(d / "links.csv")
    tables, c2b, rq4 = [], [], []
    for s in PRIMARY_SETS:          # calibration records are never in these sets
        r_s = [r for r in recs if r["set"] == s]
        i_s = [i for i in insts if i["set"] == s]
        tables += record_tables(r_s, i_s, {"set": s, "split": "all", "group": "all"})
        for g in sorted({r["population"] for r in r_s}):
            ids = {r["record_id"] for r in r_s if r["population"] == g}
            tables += record_tables([r for r in r_s if r["record_id"] in ids],
                                    [i for i in i_s if i["record_id"] in ids],
                                    {"set": s, "split": "population", "group": g})
        for c in ["A", "B"]:          # SQ1: RQ2-RQ5 and C7 (i), (iii)
            ids = {r["record_id"] for r in r_s if r["centre"] == c}
            sub = [dict(r) for r in r_s if r["record_id"] in ids]
            for r in sub:
                r["C7"] = c7(dict(r, conclusion_ai_fatigue_term="0"), r["C1_rep"])
            t = record_tables(sub, [i for i in i_s if i["record_id"] in ids],
                              {"set": s, "split": "centre", "group": c})
            tables += [x for x in t if x["code"] != "C1_rep"]
        c2b += c2b_tables(items, insts, s)
        rq4.append(rq4_counts(recs, links, s))
    conf = [r for r in recs if r["set"] == "confirmation"]
    return {"recs": recs, "tables": tables, "c2b": c2b, "rq4": rq4,
            "problems": problem_statements(conf), "n_conf": len(conf)}


def sensitivity(d):
    base = build_tables(d)
    recs = base["recs"]
    conf = [r for r in recs if r["set"] == "confirmation"]
    insts = read_csv(d / "instruments_reconciled.csv")
    items = read_csv(d / "items_reconciled.csv")
    out = []
    out += [dict(s, analysis="S1 peer-reviewed only") for s in
            problem_statements([r for r in conf if r.get("peer_reviewed") == "1"])]
    out += [dict(s, analysis="S2 signs-not-confirmed removed") for s in
            problem_statements([r for r in conf if r.get("C5") != "signs_not_confirmed"])]
    s3 = [dict(r, analysis="S3 lenient C2b") for r in c2b_tables(items, insts, "confirmation", lenient=True)]
    s4 = []
    for c in ["coder1", "coder2"]:
        if (d / f"records_{c}.csv").exists():
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
    ap.add_argument("--exploration", type=Path)
    ap.add_argument("--screening-order", type=Path)
    a = ap.parse_args()
    if a.draw_calibration:
        ids = a.draw_calibration.read_text(encoding="utf-8").split()
        drawn = a.drawn.read_text(encoding="utf-8").split() if a.drawn else []
        expl = a.exploration.read_text(encoding="utf-8").split() if a.exploration else []
        print("\n".join(draw_calibration(ids, a.round, drawn, expl)))
    elif a.screening_order:
        for g, i in screening_order(read_csv(a.screening_order)):
            print(f"{g},{i}")
    elif a.tables:
        res = build_tables(a.tables, a.coder)
        sens, s3 = sensitivity(a.tables)
        out = a.tables / "out"
        out.mkdir(exist_ok=True)
        write_csv(out / "tables.csv", res["tables"])
        write_csv(out / "c2b.csv", res["c2b"])
        write_csv(out / "rq4.csv", res["rq4"])
        write_csv(out / "problem_statements.csv", res["problems"])
        write_csv(out / "sensitivity.csv", sens)
        write_csv(out / "sensitivity_c2b_lenient.csv", s3)
        print(f"confirmation studies={res['n_conf']} proportions={'yes' if res['n_conf'] >= MIN_STUDIES else 'no'}")
    elif a.agreement:
        out = a.agreement / "out"
        out.mkdir(exist_ok=True)
        rows = run_agreement(a.agreement)
        write_csv(out / "agreement.csv", rows)
        print(f"agreement rows={len(rows)}")
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
