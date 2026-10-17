"""Dummy code tables (no real records) and boundary tests for c_synthesis.py (GSRR-64).

Usage: python3 make_dummy.py [out_dir]   (default: a fresh temporary directory)
Builds the dummy tables, runs the synthesis on them, and checks expected values with assert.
"""

import csv
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_synthesis as cs  # noqa: E402

rng = random.Random(1)
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="gse_dummy_"))
out.mkdir(parents=True, exist_ok=True)

LV = cs.C1_LEVELS


def write(name, rows):
    with open(out / name, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader()
        w.writerows(rows)


def rec(rid, set_name):
    r = {"record_id": rid, "set": set_name,
         "population": rng.choice(["students_learners", "workers_other", "health_professionals"]),
         "centre": rng.choice(["A", "B"]), "peer_reviewed": rng.choice(["0", "1"])}
    lv = rng.choice(LV)
    for x in LV:
        r[f"C1_{x}"] = "1" if x == lv else "0"
    r["C3"] = rng.choice(["amount_of_use", "dependence", "attitude", "none"])
    r["C4a"] = rng.choice(["consistent", "inconsistent", "no_comparison_possible"])
    for k in ["C4b", "C4c", "C4d"]:
        r[k] = rng.choice(["consistent", "inconsistent", "not_verifiable"])
    r["C4e_codebook"] = rng.choice(["yes", "no", "not_applicable"])
    r["C4e_agreement"] = rng.choice(["value_given", "index_only", "none", "not_applicable"])
    r["C5"] = rng.choice(["e5_group", "signs_not_confirmed", "no_signs"])
    r["C6a"] = rng.choice(["same_family", "different_family", "no_construct_term", "no_family_term",
                           "instrument_unnamed"])
    r["C6b"] = rng.choice(["match", "mismatch"])
    r["title_ai_fatigue_term"] = rng.choice(["yes", "no"])
    r["conclusion_identified"] = "1"
    r["main_instrument_identified"] = "1"
    r["conclusion_sentence"] = f"s-{rid}"
    r["conclusion_ai_fatigue_term"] = rng.choice(["0", "1"])
    r["conclusion_family"] = rng.choice(["fatigue", "exhaustion", "burnout", "none"])
    r["main_instrument_family"] = rng.choice(["fatigue", "exhaustion|fatigue", "burnout"])
    return r


ids = [f"D{i:03d}" for i in range(1, 33)]
sets = {}
for n, i in enumerate(ids):
    sets[i] = "exploration" if n < 10 else "calibration" if n < 15 else "late" if n >= 30 else "main"
recs = [rec(i, sets[i]) for i in ids]
insts, items = [], []
for n, i in enumerate(ids):
    vid = "VCAL" if i == "D015" else f"V{n % 14:02d}"        # VCAL: used by a calibration record only
    inst = {"record_id": i, "instrument_id": "main", "version_id": vid,
            "origin": rng.choice(["new", "existing_ai", "adapted_general", "unchanged_general",
                                  "general_not_verifiable"]),
            "format": "multi_item", "language": "en", "items_full": "12"}
    for k in cs.INSTRUMENT_CODES:
        inst.setdefault(k, rng.choice(["stated", "found_not_stated", "no_change", "not_verifiable"]))
    insts.append(inst)
for v in range(13):            # V13 has no items -> items unavailable
    for k in range(1, 9):
        t = rng.choice(["MOT", "AVO", "FUT", "IRR", "FAT", "FAT", "OTH"])
        items.append({"version_id": f"V{v:02d}", "item_no": str(k), "type": t,
                      "item_source": "printed",
                      "boundary": rng.choice(["0", "0", "1"]), "secondary_type": rng.choice(["MOT", "FAT"]),
                      "target": rng.choice(["TASK", "AI_USE"]) if t in cs.TARGETED_TYPES else ""})
c4f = []
for i in ids:
    for k in range(2):
        cons = rng.choice(["yes", "yes", "no", "na"])
        c4f.append({"record_id": i, "result_id": f"{i}-r{k}", "source": "table" if k else "text",
                    "consistent": cons,
                    "gross": "1" if cons == "no" and rng.random() < 0.5 else "0"})
links = [{"record_id": "D016", "group_id": "G1"}, {"record_id": "D017", "group_id": "G1"},
         {"record_id": "D020", "group_id": "G2"}, {"record_id": "D021", "group_id": "G2"}]

for coder in ["reconciled", "coder1", "coder2"]:
    rr = [dict(r) for r in recs]
    it = [dict(x) for x in items]
    cc = [dict(x) for x in c4f]
    if coder == "coder2":
        for r in rr[::4]:
            r["C6b"] = "match" if r["C6b"] != "match" else "mismatch"
        for r in rr[::3]:
            r["title_ai_fatigue_term"] = "no" if r["title_ai_fatigue_term"] == "yes" else "yes"
        for r in rr[::6]:
            r["conclusion_family"] = "burnout" if r["conclusion_family"] != "burnout" else "fatigue"
        for x in it[::5]:
            x["type"] = "OTH"
        dropped = cc[::9]                                              # results recalculated by coder 1 only
        cc = [x for x in cc if x not in dropped]
        cc.append({"record_id": "D016", "result_id": "D016-extra", "source": "text", "consistent": "yes",
                   "gross": "0"})                                      # a result recalculated by coder 2 only
        for x in cc[::5]:
            x["consistent"] = "no" if x["consistent"] == "yes" else "yes"
    write(f"records_{coder}.csv", rr)
    write(f"instruments_{coder}.csv", insts)
    write(f"items_{coder}.csv", it)
    write(f"c4f_{coder}.csv", cc)
write("links.csv", links)
write("c4f_ai.csv", [dict(r, consistent=("no" if r["consistent"] == "yes" and rng.random() < 0.1 else r["consistent"])) for r in c4f])
pool = [i for i in ids if sets[i] in ("main", "calibration")]
(out / "pool_ids.txt").write_text("\n".join(pool), encoding="utf-8")
(out / "exploration_ids.txt").write_text("\n".join(i for i in ids if sets[i] == "exploration"), encoding="utf-8")
write("candidates.csv", [{"record_id": r["record_id"], "population": r["population"]} for r in recs])

# --- boundary tests ---------------------------------------------------------
res = cs.build_tables(out)
conf = [r for r in res["recs"] if r["set"] == "main"]
assert res["n_main"] == 15 == len(conf), res["n_main"]
assert not any(t["set"] == "calibration" for t in res["tables"]), "calibration records leaked into tables"
# versions: V10-V13 are first used by calibration records (n = 10..13) and also by main
# records (n = 24..27 -> V10..V13), so they are first seen in the main set
assert res["vsets"]["V10"] == "main" and res["vsets"]["V00"] == "exploration", res["vsets"]
summ = [r for r in res["c2b"] if r["version_id"] == "SUMMARY" and r["set"] == "main"][0]
assert summ["with_items"] == 3 and summ["items_unavailable"] == 1, summ          # V13 has no items
per_version = [r for r in res["c2b"] if r["set"] == "main" and r["version_id"].startswith("V")]
assert per_version and all(r["proportion"] is not None for r in per_version)
# cannot_decide stays in the denominator (GSRR-53)
ct = cs.count_table([{"record_id": str(k), "C7": v} for k, v in enumerate(["beyond"] * 9 + ["cannot_decide"])], "C7", {})
assert {r["value"]: r["denominator"] for r in ct}["cannot_decide"] == 10
# minimum size counts studies, not instruments: 5 studies with 3 instruments each
rows15 = [{"record_id": f"S{k // 3}", "origin": "new"} for k in range(15)]
assert cs.count_table(rows15, "origin", {})[0]["proportion"] is None
# multi-value C3
c3 = cs.count_table([{"record_id": "a", "C3": "amount_of_use|attitude"}], "C3", {})
assert {r["value"] for r in c3} == {"amount_of_use", "attitude"}
# centre tables drop (ii): an unresolved C1 does not make C7 unresolved
assert cs.c7(dict(base := {"conclusion_identified": "1", "main_instrument_identified": "1", "C6b": "match",
                            "conclusion_ai_fatigue_term": "0", "conclusion_family": "fatigue",
                            "main_instrument_family": "fatigue"}), "") == "within"
assert cs.c7(dict(base, conclusion_identified="unresolved"), "L1a") == "unresolved"
assert cs.c7(dict(base, conclusion_family="none|fatigue", main_instrument_family="none|burnout"), "L1a") == "beyond"
# C4f per result: counts match the reconciled rows of the set; records without results count as 0
rr_ = [{"record_id": "a", "set": "main"}, {"record_id": "b", "set": "main"},
       {"record_id": "c", "set": "exploration"}]
cr_ = [{"record_id": "a", "consistent": "no", "gross": "1"}, {"record_id": "a", "consistent": "yes", "gross": "0"},
       {"record_id": "c", "consistent": "no", "gross": "0"}]
t4 = {(r["row"], r["value"]): r["count"] for r in cs.c4f_result_table(rr_, cr_, "main")}
assert t4[("results", "no")] == 1 and t4[("results", "yes")] == 1 and t4[("results", "gross")] == 1, t4
assert t4[("results_per_record", "2")] == 1 and t4[("results_per_record", "0")] == 1, t4
conf_res = [r for r in res["c4f_results"] if r["set"] == "main" and r["row"] == "results_per_record"]
assert sum(r["count"] for r in conf_res) == 15, conf_res
# instruments used: a version first seen in exploration is listed for the main set too
iu = cs.instruments_used([{"record_id": "x", "set": "exploration"}, {"record_id": "y", "set": "main"}],
                         [{"record_id": "x", "version_id": "E1", "origin": "new"},
                          {"record_id": "y", "version_id": "E1", "origin": "new"},
                          {"record_id": "y", "version_id": "N9", "origin": "adapted"}],
                         [{"version_id": "E1", "type": "FAT"}, {"version_id": "E1", "type": "AVO"}],
                         {"E1": "exploration", "N9": "main"}, "main")
assert [(r["version_id"], r["first_seen"], r["records_using"]) for r in iu] == [("E1", "exploration", 1), ("N9", "main", 1)]
assert iu[0]["FAT"] == 1 and iu[0]["AVO"] == 1 and iu[1]["FAT"] is None    # no items -> no counts
assert iu[0]["refers_to_ai"] == "not_main_instrument"          # instrument_id missing -> not the main one
# CHANGED (item 9): refers_to_ai is L1a only; an L1b-only record is "no"
assert cs.refers_to_ai([{"C1_L1a": "1", "C1_L1b": "0"}, {"C1_L1a": "0", "C1_L1b": "1"}]) == "no|yes"
assert cs.refers_to_ai([{"C1_L1a": "0", "C1_L1b": "1"}]) == "no"
# a version whose records differ in instructions (L1b), origin and item disclosure: counts per value
iu2 = cs.instruments_used(
    [{"record_id": k, "set": "main", "C1_L1a": "0", "C1_L1b": b} for k, b in
     [("a", "1"), ("b", "1"), ("c", "1"), ("d", "0"), ("e", "0")]],
    [{"record_id": k, "instrument_id": "main", "version_id": "W1", "origin": o, "C2d_item_disclosure": dsc}
     for k, o, dsc in [("a", "new", "all"), ("b", "new", "some"), ("c", "adapted", "all"),
                       ("d", "new", "none"), ("e", "new", "none")]],
    [], {"W1": "main"}, "main")
assert iu2[0]["instructions_refer_to_ai"] == "L1b:3; none:2", iu2[0]
assert iu2[0]["origin"] == "adapted:1; new:4" and iu2[0]["C2d_item_disclosure"] == "all:2; none:2; some:1", iu2[0]
assert iu2[0]["refers_to_ai"] == "no"
assert all("instructions_refer_to_ai" in r and r["origin"] for r in res["instruments_used"])
assert all(r["refers_to_ai"] in {"yes", "no", "no|yes", "unresolved"} or "|" in r["refers_to_ai"]
           for r in res["instruments_used"]), {r["refers_to_ai"] for r in res["instruments_used"]}
assert all(r["set"] != "calibration" for r in res["instruments_used"])
# per-study table: primary sets only, no calibration records
ps_ = res["per_study"]
assert ps_ and all(r["set"] in cs.PRIMARY_SETS for r in ps_)
assert sum(1 for r in ps_ if r["set"] == "main") == 15
# lenient C2b: secondary types count in the per-version and the aggregate rows alike
li = [{"version_id": "N1", "type": "OTH", "boundary": "1", "secondary_type": "FAT", "target": ""},
      {"version_id": "N1", "type": "OTH", "boundary": "1", "secondary_type": "OTH", "target": ""}]
lt = cs.c2b_tables(li, {"N1": "main"}, "main", lenient=True)
assert [r for r in lt if r["version_id"] == "N1" and r["type"] == "FAT"][0]["count"] == 1
assert [r for r in lt if r["version_id"] == "N1" and r["type"] == "OTH"][0]["count"] == 2   # same type not doubled
assert [r for r in lt if r["version_id"] == "ALL" and r["type"] == "FAT"][0]["instruments_with_type"] == 1
rq4 = [r for r in res["rq4"] if r["set"] == "main"][0]
assert rq4["records"] == 15 and rq4["studies"] == 13, rq4          # G1 (D016, D017), G2 (D020, D021)
# C7: two-family instrument name matches either family
base = {"conclusion_identified": "1", "main_instrument_identified": "1", "C6b": "match",
        "conclusion_ai_fatigue_term": "0"}
assert cs.c7(dict(base, conclusion_family="fatigue", main_instrument_family="exhaustion|fatigue"), "L1a") == "within"
assert cs.c7(dict(base, conclusion_family="burnout", main_instrument_family="exhaustion|fatigue"), "L1a") == "beyond"
assert cs.c7(dict(base, conclusion_family="none", main_instrument_family="fatigue"), "L1a") == "within"
assert cs.c7(dict(base, conclusion_family="fatigue", main_instrument_family="fatigue", conclusion_ai_fatigue_term="1"), "L3") == "beyond"
assert cs.c7(dict(base, conclusion_identified="0", C6b="mismatch"), "L1a") == "cannot_decide"
assert cs.c7(dict(base, C6b="unresolved", conclusion_family="fatigue", main_instrument_family="fatigue"), "L1a") == "unresolved"
# C7 by condition (GSRR-57): each condition is its own problem type
cc = cs.c7_conditions(dict(base, conclusion_family="burnout", main_instrument_family="fatigue",
                           C6b="mismatch", conclusion_ai_fatigue_term="1"), "L1a")
assert cc == {"C7_i": "met", "C7_ii": "not_met", "C7_iii": "met"}, cc
cc = cs.c7_conditions(dict(base, conclusion_family="fatigue", main_instrument_family="fatigue",
                           conclusion_ai_fatigue_term="1"), "L4")
assert cc == {"C7_i": "not_met", "C7_ii": "met", "C7_iii": "not_met"}, cc
# an unresolved input makes only its own condition unresolved
cc = cs.c7_conditions(dict(base, conclusion_family="fatigue", main_instrument_family="fatigue",
                           C6b="unresolved"), "L1a")
assert cc == {"C7_i": "unresolved", "C7_ii": "not_met", "C7_iii": "not_met"}, cc
assert cs.c7_conditions(dict(base, conclusion_family="fatigue", main_instrument_family="fatigue"), "")["C7_ii"] == "not_applicable"
assert set(cs.c7_conditions(dict(base, conclusion_identified="0"), "L1a").values()) == {"cannot_decide"}
names = [p_["problem_type"] for p_ in res["problems"]]
assert sum(1 for n_ in names if n_.startswith("C7 (")) == 3 and "C7 beyond" not in names, names
assert cs.c6a_c7iii_overlap([{"C6a": "different_family", "C7_iii": "met"}, {"C6a": "same_family", "C7_iii": "met"}]) == 1
# CHANGED (item 7): the centre tables leave out C1, C6c and C7 (ii) (they no longer list C7_ii as not_applicable)
centre = [t for t in res["tables"] if t["split"] == "centre"]
assert centre and not {t["code"] for t in centre} & {"C1_rep", "C6c", "C7_ii"}, {t["code"] for t in centre}
assert {"C7_i", "C7_iii", "C6a", "C6b"} <= {t["code"] for t in centre}
assert {"C6c", "C1_rep", "C7_ii"} <= {t["code"] for t in res["tables"] if t["split"] in ("all", "population")}
# C4f results by source (text / table)
src_rows = {(r["row"], r["value"]): r["count"] for r in res["c4f_results"] if r["set"] == "main"}
assert sum(src_rows[(f"results_from_{so}", k)] for so in ["text", "table"] for k in ["yes", "no", "na", "unresolved"]) == \
    sum(src_rows[("results", k)] for k in ["yes", "no", "na", "unresolved"])
# C1 representative
assert cs.c1_representative({"C1_L1b": "1", "C1_L2": "1"}) == "L1b"
assert cs.c1_representative({"C1_L3": "unresolved"}) == "unresolved"
# problem statements: no evaluable values -> not evaluable
ps = cs.problem_statements([{"C4a": "not_verifiable"}, {"C4a": "unresolved"}])
assert ps[0]["statement"] == "could not be evaluated" and ps[0]["unresolved"] == 1
# minimum sizes
assert cs.count_table([{"record_id": str(k), "x": "a"} for k in range(9)], "x", {})[0]["proportion"] is None
assert cs.count_table([{"record_id": str(k), "x": "a"} for k in range(10)], "x", {})[0]["proportion"] == 1.0
two = cs.c2b_tables([{"version_id": v, "type": "FAT"} for v in ["N1", "N2"]],
                    {"N1": "main", "N2": "main", "N3": "main"}, "main")
assert two[-1]["with_items"] == 2 and two[-1]["items_unavailable"] == 1 and not two[-1]["proportions_reported"]
assert [r for r in two if r["version_id"] == "N1" and r["type"] == "FAT"][0]["count"] == 1   # counts kept
assert [r for r in two if r["version_id"] == "N1" and r["type"] == "FAT"][0]["proportion"] is None
# agreement covers C4f, C4f_gross, the conclusion sentence and human-AI C4f
ag = cs.run_agreement(out)
codes = {(r["set"], r["code"]) for r in ag}
for c in ["C4f", "C4f_gross", "C1_rep", "conclusion_sentence", "type", "secondary_type", "origin"]:
    assert ("main", c) in codes, c
assert ("all", "C4f_human_vs_ai") in codes
assert [r for r in ag if r["set"] == "main" and r["code"] == "type"][0]["n"] > 0
# input validation stops on a bad value and on a missing file
bad = out / "bad"
bad.mkdir(exist_ok=True)
for kind in ["records", "instruments", "items", "c4f"]:
    (bad / f"{kind}_reconciled.csv").write_text((out / f"{kind}_reconciled.csv").read_text(encoding="utf-8"), encoding="utf-8")
bad_items = cs.read_csv(bad / "items_reconciled.csv")
bad_items[0]["type"] = "FATIGUE"                                  # not in the code list
write_to = bad / "items_reconciled.csv"
with open(write_to, "w", encoding="utf-8", newline="") as f_:
    w_ = csv.DictWriter(f_, fieldnames=list(bad_items[0]))
    w_.writeheader()
    w_.writerows(bad_items)
try:
    cs.build_tables(bad)
    raise AssertionError("bad vocabulary must stop")
except cs.InputError:
    pass
(bad / "c4f_reconciled.csv").unlink()
try:
    cs.build_tables(bad)
    raise AssertionError("missing file must stop")
except cs.InputError:
    pass
sens, s3 = cs.sensitivity(out)
assert {r["analysis"] for r in sens} >= {"S1 peer-reviewed only", "S2 signs-not-confirmed removed",
                                         "S4 coder1 values", "S4 coder2 values"} and s3
# draws
pool25 = [f"P{i:02d}" for i in range(25)]
assert cs.draw_calibration(pool25, 1)[0].startswith("P")
try:
    cs.draw_calibration(pool25[:24], 1)
    raise AssertionError("small pool without exploration IDs must fail")
except ValueError:
    pass
assert cs.draw_calibration(pool25[:24], 1, (), [f"E{i}" for i in range(10)])[0].startswith("E")
r1 = cs.draw_calibration(pool25, 1)
r2 = cs.draw_calibration(pool25, 2, r1)
assert not set(r1) & set(r2)
# kappa
assert cs.cohen_kappa(list("aabb"), list("aabb")) == 1.0
assert cs.cohen_kappa(list("aaaa"), list("aaaa")) is None
order = cs.screening_order([{"record_id": f"R{i}", "population": g} for i, g in
                            enumerate(["students_learners"] * 3 + ["health_professionals"] * 3)])
assert [g for g, _ in order[:2]] == ["students_learners", "health_professionals"]
# === registration draft 0.10 assertions ====================================
# item 1: the set label is "main"; "confirmation" is gone from the vocabulary and from the output text
assert "main" in cs.VOCAB["set"] and "confirmation" not in cs.VOCAB["set"] and "confirmation" not in cs.PRIMARY_SETS
assert all(r["statement"].endswith("the main set") for r in res["problems"] if r["evaluable"]), res["problems"]
assert {r["set"] for r in res["tables"]} == {"main", "exploration", "late"}
# item 2: evaluable records per problem type (GSRR-57)
ps = {p_["problem_type"]: p_ for p_ in cs.problem_statements(
    [{"C4a": "inconsistent"}, {"C4a": "consistent"}, {"C4a": "no_comparison_possible"}, {"C4a": "not_verifiable"},
     {"C4a": "unresolved"}])}
c4a_ = ps["C4a inconsistent"]
assert (c4a_["count"], c4a_["evaluable"], c4a_["not_evaluable"], c4a_["unresolved"]) == (1, 2, 2, 1), c4a_
assert c4a_["statement"] == "was observed in the main set"
ps = {p_["problem_type"]: p_ for p_ in cs.problem_statements([{"C4a": "consistent"}, {"C4a": "no_comparison_possible"}])}
assert ps["C4a inconsistent"]["statement"] == "was not observed in the main set" and ps["C4a inconsistent"]["evaluable"] == 1
# a set in which every record is "cannot be calculated" for C4f -> could not be evaluated
ps = {p_["problem_type"]: p_ for p_ in cs.problem_statements(
    [{"C4f": "cannot_be_calculated", "C4f_gross": "cannot_be_calculated"} for _ in range(3)]
    + [{"C4f": "not_applicable", "C4f_gross": "not_applicable"}])}
assert ps["C4f any inconsistency"]["statement"] == "could not be evaluated", ps["C4f any inconsistency"]
assert ps["C4f any gross inconsistency"]["statement"] == "could not be evaluated"
assert ps["C4f any inconsistency"]["evaluable"] == 0 and ps["C4f any inconsistency"]["not_evaluable"] == 4
# other values are not evaluable for their problem type (and stay in the descriptive denominators, GSRR-53)
ps = {p_["problem_type"]: p_ for p_ in cs.problem_statements(
    [{"C4e_codebook": "not_applicable", "C4e_agreement": "index_only", "C6a": "no_family_term", "C6b": "match",
      "C7_iii": "no_term_to_compare", "C7_i": "cannot_decide", "C6c": "cannot_decide", "C5": "no_signs"}])}
assert ps["C4e codebook not available"]["evaluable"] == 0 and ps["C4e agreement none"]["evaluable"] == 1
assert ps["C6a different family"]["evaluable"] == 0 and ps["C6b mismatch"]["evaluable"] == 1
assert ps["C7 (iii) conclusion term and instrument name in different term families"]["evaluable"] == 0
assert ps["C7 (i) causal wording not supported by the design"]["evaluable"] == 0
assert ps["C6c AI-fatigue term with L3 to L6"]["evaluable"] == 0 and ps["C5 signs not confirmed"]["evaluable"] == 1
dn = {r["value"]: r["denominator"] for r in cs.count_table(
    [{"record_id": str(k), "C4a": v} for k, v in enumerate(["consistent", "no_comparison_possible", "not_verifiable"])],
    "C4a", {})}
assert dn["no_comparison_possible"] == 2 and dn["not_verifiable"] == 2, dn          # finding stays; not_verifiable out
assert all(p_["evaluable"] + p_["not_evaluable"] == res["n_main"] for p_ in res["problems"])
# item 3: C4f summary order (GSRR-43 Unit)
yes_, no_, na_ = ({"consistent": v, "gross": "0"} for v in ("yes", "no", "na"))
assert cs.c4f_summary([yes_, na_]) == "none"                         # consistent + incalculable -> none
assert cs.c4f_summary([no_, na_, yes_]) == "any_inconsistency"
assert cs.c4f_summary([na_, na_]) == "cannot_be_calculated" and cs.c4f_summary([]) == "not_applicable"
g1_ = {"consistent": "no", "gross": "1"}
assert cs.c4f_gross([g1_, na_]) == "any_gross" and cs.c4f_gross([yes_, na_]) == "no_gross"
assert cs.c4f_gross([na_]) == "cannot_be_calculated" and cs.c4f_gross([]) == "not_applicable"
assert cs.c4f_gross([no_, yes_]) == "no_gross"                       # inconsistent but not gross
assert {r["value"] for r in res["tables"] if r["code"] == "C4f"} <= \
    {"any_inconsistency", "none", "cannot_be_calculated", "not_applicable", "unresolved"}
# item 4: renamed / split values and the vocabularies used by validation
assert "no_comparison_possible" in cs.VOCAB["C4a"]
assert "instrument_unnamed" in cs.VOCAB["C6a"] and "not_verifiable" in cs.VOCAB["C6a"]
assert "unnamed_or_not_verifiable" not in cs.VOCAB["C6a"] and "unnamed_or_not_verifiable" not in cs.NO_FAMILY
vbad = out / "vbad"
vbad.mkdir(exist_ok=True)
for kind in ["records", "instruments", "items", "c4f"]:
    (vbad / f"{kind}_reconciled.csv").write_text((out / f"{kind}_reconciled.csv").read_text(encoding="utf-8"), encoding="utf-8")
vr = cs.read_csv(vbad / "records_reconciled.csv")
vr[0]["C6a"] = "unnamed_or_not_verifiable"                           # the old combined value is refused
with open(vbad / "records_reconciled.csv", "w", encoding="utf-8", newline="") as f_:
    w_ = csv.DictWriter(f_, fieldnames=list(vr[0]))
    w_.writeheader()
    w_.writerows(vr)
try:
    cs.build_tables(vbad)
    raise AssertionError("old C6a value must stop")
except cs.InputError:
    pass
vr[0]["C6a"] = "instrument_unnamed"
vr[0]["title_ai_fatigue_term"] = "maybe"                             # outside yes / no / unresolved
with open(vbad / "records_reconciled.csv", "w", encoding="utf-8", newline="") as f_:
    w_ = csv.DictWriter(f_, fieldnames=list(vr[0]))
    w_.writeheader()
    w_.writerows(vr)
try:
    cs.build_tables(vbad)
    raise AssertionError("bad title input must stop")
except cs.InputError:
    pass
# (iii) no term to compare: no construct term in the conclusion, or no family term in the instrument name
cb = dict(base, C6b="match", conclusion_ai_fatigue_term="0")
assert cs.c7_conditions(dict(cb, conclusion_family="none", main_instrument_family="fatigue"), "L1a")["C7_iii"] == "no_term_to_compare"
assert cs.c7_conditions(dict(cb, conclusion_family="fatigue", main_instrument_family="no_family_term"), "L1a")["C7_iii"] == "no_term_to_compare"
assert cs.c7_conditions(dict(cb, conclusion_family="fatigue", main_instrument_family="instrument_unnamed"), "L1a")["C7_iii"] == "no_term_to_compare"
# item 5: "cannot decide"
cd_ = cs.c7_conditions(dict(cb, main_instrument_identified="0", C6b="mismatch"), "L4")
assert cd_ == {"C7_i": "met", "C7_ii": "cannot_decide", "C7_iii": "cannot_decide"}, cd_       # only the main instrument unknown
assert cs.c7_conditions(dict(cb, main_instrument_identified="0"), "L4")["C7_i"] == "not_met"
assert cs.c7(dict(cb, main_instrument_identified="0", C6b="mismatch"), "L4") == "beyond"
assert cs.c7(dict(cb, main_instrument_identified="0"), "L4") == "cannot_decide"
assert set(cs.c7_conditions(dict(cb, conclusion_identified="0", C6b="mismatch"), "L4").values()) == {"cannot_decide"}
# item 6: C6c
t_ = dict(base, title_ai_fatigue_term="yes")
assert cs.c6c(t_, "L3") == "ai_term_L3_L6" and cs.c6c(t_, "L6") == "ai_term_L3_L6"
assert cs.c6c(t_, "L1a") == "ai_term_L1a_L2" and cs.c6c(t_, "L2") == "ai_term_L1a_L2"
assert cs.c6c(dict(t_, title_ai_fatigue_term="no"), "L4") == "no_ai_term"
assert cs.c6c(dict(t_, main_instrument_identified="0"), "L4") == "cannot_decide"
assert cs.c6c(dict(t_, title_ai_fatigue_term="unresolved"), "L4") == "unresolved"
assert cs.c6c(t_, "unresolved") == "unresolved"
assert all(r["C6c"] in {"ai_term_L3_L6", "ai_term_L1a_L2", "no_ai_term", "cannot_decide", "unresolved"} for r in res["recs"])
assert "C6c AI-fatigue term with L3 to L6" in names and "C6c" in res["per_study"][0]
assert any(r["analysis"].startswith("S1") and r["problem_type"].startswith("C6c") for r in sens)
assert any(r["analysis"].startswith("S4 coder2") and r["problem_type"].startswith("C6c") for r in sens)
assert ("main", "title_ai_fatigue_term") in codes and ("main", "C6c") not in codes and ("main", "C7") not in codes
# item 8: C2b denominator = coded items (printed or item_source = source); full count beside it; unresolved stays in
c2i = [{"version_id": "N1", "item_no": str(k), "type": t, "item_source": "source", "boundary": "0",
        "secondary_type": "", "target": ""} for k, t in enumerate(["FAT", "FAT", "OTH", "unresolved"])]
c2t = cs.c2b_tables(c2i, {"N1": "main", "N2": "main"}, "main",
                    insts=[{"version_id": "N1", "items_full": "10"}, {"version_id": "N2", "items_full": "8"}])
n1 = {r["type"]: r for r in c2t if r["version_id"] == "N1"}
assert all(r["denominator"] == 4 for r in n1.values()), n1                           # coded items, not the full 10
assert n1["unresolved"]["count"] == 1 and n1["FAT"]["count"] == 2
assert n1["FAT"]["items_full"] == "10" and n1["FAT"]["items_from_source"] == 4
sm_ = [r for r in c2t if r["version_id"] == "SUMMARY"][0]
assert sm_["with_items"] == 1 and sm_["items_unavailable"] == 1                      # N2 counted outside the denominators
assert not [r for r in c2t if r["version_id"] == "N2"]
assert all(r["denominator"] == 8 for r in res["c2b"] if r["version_id"] == "V00" and r["set"] == "exploration")
assert all(r["items_full"] == "12" for r in res["c2b"] if r["version_id"].startswith("V") and r["set"] == "main")
# item 10: agreement
ag_ = {(r["set"], r["code"]): r for r in ag}
for st_ in ("main", "exploration"):
    assert (st_, "C4f_results_one_coder_only") in ag_ and (st_, "C4f_result_judgement") in ag_
    assert ag_[(st_, "conclusion_family")]["percent_agreement"] is not None
    assert (st_, "C4e_codebook") in ag_ and (st_, "C4e_agreement") in ag_          # C4 (e): one row per column
assert sum(ag_[(st_, "C4f_results_one_coder_only")]["n"] for st_ in ("main", "exploration", "late", "calibration")
           if (st_, "C4f_results_one_coder_only") in ag_) > 0
j_ = ag_[("main", "C4f_result_judgement")]
assert j_["n"] > 0 and j_["percent_agreement"] is not None and j_["percent_agreement"] < 1 and "kappa" in j_, j_
hv_ = [r for r in ag if r["code"] == "C4f_human_vs_ai"][0]
assert hv_["note"] == "report_only"
# the judgement keeps 'grossly inconsistent' as its own category and matches results on record + result id
assert cs.c4f_judgement({"consistent": "no", "gross": "1"}) == "grossly_inconsistent"
assert cs.c4f_judgement({"consistent": "no", "gross": "0"}) == "inconsistent"
assert cs.c4f_judgement({"consistent": "na", "gross": "0"}) == "cannot_be_calculated"
assert cs.family_key("fatigue|burnout") == cs.family_key("burnout|fatigue")
# item 11: small pool -> exploration draws use study record IDs only; all drawn -> calibration material
expl_recs = [r for r in res["recs"] if r["set"] == "exploration"]
expl_ids = cs.exploration_study_ids(res["recs"])
assert len(expl_ids) == 10 and expl_ids == sorted(r["record_id"] for r in expl_recs)
inst_ids = sorted({i["version_id"] for i in insts} | {"main"})
d1 = cs.draw_calibration(pool25[:24], 1, (), expl_ids, inst_ids)
assert set(d1) <= set(expl_ids) and not set(d1) & set(inst_ids)
assert not cs.all_exploration_drawn(d1, expl_ids)
d2 = cs.draw_calibration(pool25[:24], 2, d1, expl_ids, inst_ids)
assert cs.all_exploration_drawn(d1 + d2, expl_ids) and not set(d1) & set(d2)
try:
    cs.draw_calibration(pool25[:24], 3, d1 + d2, expl_ids, inst_ids)
    raise AssertionError("small pool allows two rounds only")
except ValueError:
    pass
try:
    cs.draw_calibration(pool25[:24], 1, (), expl_ids + ["V01"], inst_ids)
    raise AssertionError("instrument IDs must be refused")
except ValueError:
    pass
assert res["exploration_calibration_material"] is False and not any(t["calibration_material"] for t in res["tables"]
                                                                   if t["set"] == "exploration")
flag = out / "flag"
flag.mkdir(exist_ok=True)
for kind in ["records", "instruments", "items", "c4f"]:
    (flag / f"{kind}_reconciled.csv").write_text((out / f"{kind}_reconciled.csv").read_text(encoding="utf-8"), encoding="utf-8")
fr = cs.read_csv(flag / "records_reconciled.csv")
for r_ in fr:
    r_["calibration_draw"] = "1" if r_["set"] == "exploration" else "0"
with open(flag / "records_reconciled.csv", "w", encoding="utf-8", newline="") as f_:
    w_ = csv.DictWriter(f_, fieldnames=list(fr[0]))
    w_.writeheader()
    w_.writerows(fr)
fres = cs.build_tables(flag)
assert fres["exploration_calibration_material"] is True
assert all(t["calibration_material"] is True for t in fres["tables"] if t["set"] == "exploration")
assert all("calibration_material" not in t for t in fres["tables"] if t["set"] == "main")
fr[0]["calibration_draw"] = "0"                                      # one exploration study not drawn -> not flagged
fr_exp = [r_ for r_ in fr if r_["set"] == "exploration"]
fr_exp[0]["calibration_draw"] = "0"
assert not cs.exploration_calibration_flag(fr)
# item 12: a version used only by calibration records belongs to no set and appears in no set table
assert res["vsets"]["VCAL"] == cs.CAL_ONLY and cs.CAL_ONLY not in cs.PRIMARY_SETS
assert not any(r["version_id"] == "VCAL" for r in res["c2b"] + res["instruments_used"])
assert all(r["set"] != cs.CAL_ONLY for r in res["c2b"] + res["instruments_used"])
cal_only = cs.version_sets([{"record_id": "c1", "version_id": "Z"}, {"record_id": "m1", "version_id": "Y"},
                            {"record_id": "c1", "version_id": "Y"}],
                           [{"record_id": "c1", "set": "calibration"}, {"record_id": "m1", "set": "main"}])
assert cal_only == {"Z": cs.CAL_ONLY, "Y": "main"}, cal_only
# C6b has no "no causal wording" value: such a record is coded match (GSRR-43), so the value is refused
vr = cs.read_csv(out / "records_reconciled.csv")
vr[0]["C6b"] = "no_causal_wording"
with open(vbad / "records_reconciled.csv", "w", encoding="utf-8", newline="") as f_:
    w_ = csv.DictWriter(f_, fieldnames=list(vr[0]))
    w_.writeheader()
    w_.writerows(vr)
try:
    cs.build_tables(vbad)
    raise AssertionError("a C6b value outside the code list must stop")
except cs.InputError:
    pass
# the C7 summary value is reported only in the per-study table (GSRR-43), never in the set tables
assert "C7" not in {t_["code"] for t_ in res["tables"]}, "C7 summary must not be in the tables"
print(f"dummy tables in {out}; all boundary tests passed")
