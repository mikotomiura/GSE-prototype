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


# E5 groups (GSRR-35): only one record per group is coded; the other members appear in links.csv only
E5_CODED = {"D016", "D020"}
E5_UNCODED = {"D017": "G1", "D021": "G2"}


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
    r["C5"] = "e5_group" if rid in E5_CODED else rng.choice(["signs_not_confirmed", "no_signs"])
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


all_ids = [f"D{i:03d}" for i in range(1, 33)]
sets = {}
for n, i in enumerate(all_ids):
    sets[i] = "exploration" if n < 10 else "late" if n >= 30 else "main"
ids = [i for i in all_ids if i not in E5_UNCODED]          # E5-linked duplicates are not coded
recs = [rec(i, sets[i]) for i in ids]
insts, items = [], []
for n, i in enumerate(all_ids):
    if i in E5_UNCODED:
        continue
    vid = f"V{n % 14:02d}"
    inst = {"record_id": i, "instrument_id": "main", "version_id": vid,
            "origin": rng.choice(["new", "existing_ai", "adapted_general", "unchanged_general",
                                  "general_not_verifiable"]),
            "format": "multi_item", "language": "en", "items_full": "12"}
    for k in cs.INSTRUMENT_CODES:
        inst.setdefault(k, rng.choice(sorted(cs.VOCAB[k] - {"unresolved"})))
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
assert not E5_UNCODED.keys() & {r["record_id"] for r in recs}, "E5-linked duplicates must not be coded"

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
            if x["consistent"] != "no":
                x["gross"] = "0"                                           # gross needs an inconsistent result
        for r in rr[::7]:
            r["conclusion_ai_fatigue_term"] = "1" if r["conclusion_ai_fatigue_term"] == "0" else "0"
        for r in rr[1::6]:
            r["conclusion_identified"] = "0" if r["conclusion_identified"] == "1" else "1"
        for r in rr[2::5]:
            r["main_instrument_identified"] = "0" if r["main_instrument_identified"] == "1" else "1"
    write(f"records_{coder}.csv", rr)
    write(f"instruments_{coder}.csv", insts)
    write(f"items_{coder}.csv", it)
    write(f"c4f_{coder}.csv", cc)
write("links.csv", links)
write("c4f_ai.csv", [dict(r, consistent=("no" if r["consistent"] == "yes" and rng.random() < 0.1 else r["consistent"])) for r in c4f])
write("candidates.csv", [{"record_id": r["record_id"], "population": r["population"]} for r in recs])

# --- boundary tests ---------------------------------------------------------
res = cs.build_tables(out)
conf = [r for r in res["recs"] if r["set"] == "main"]
assert res["n_main"] == 18 == len(conf), res["n_main"]     # 20 main studies minus 2 uncoded E5 duplicates
assert {t["set"] for t in res["tables"]} <= set(cs.PRIMARY_SETS)
# versions: V10-V13 are first used by main records (n = 10..13), so they are first seen in the main set
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
assert cs.c7(dict(base, conclusion_family="fatigue", main_instrument_family="burnout"), "L1a") == "beyond"
# C4f per result: counts match the reconciled rows of the set; records without results count as 0
rr_ = [{"record_id": "a", "set": "main"}, {"record_id": "b", "set": "main"},
       {"record_id": "c", "set": "exploration"}]
cr_ = [{"record_id": "a", "consistent": "no", "gross": "1"}, {"record_id": "a", "consistent": "yes", "gross": "0"},
       {"record_id": "c", "consistent": "no", "gross": "0"}]
t4 = {(r["row"], r["value"]): r["count"] for r in cs.c4f_result_table(rr_, cr_, "main")}
assert t4[("results", "no")] == 1 and t4[("results", "yes")] == 1 and t4[("results", "gross")] == 1, t4
assert t4[("results_per_record", "2")] == 1 and t4[("results_per_record", "0")] == 1, t4
conf_res = [r for r in res["c4f_results"] if r["set"] == "main" and r["row"] == "results_per_record"
            and r["split"] == "all"]          # CHANGED: the table now also has population rows
assert sum(r["count"] for r in conf_res) == 18, conf_res
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
assert all(r["set"] in cs.PRIMARY_SETS for r in res["instruments_used"])
# per-study table: primary sets only
ps_ = res["per_study"]
assert ps_ and all(r["set"] in cs.PRIMARY_SETS for r in ps_)
assert sum(1 for r in ps_ if r["set"] == "main") == 18
# lenient C2b: secondary types count in the per-version and the aggregate rows alike
li = [{"version_id": "N1", "type": "OTH", "boundary": "1", "secondary_type": "FAT", "target": ""},
      {"version_id": "N1", "type": "OTH", "boundary": "1", "secondary_type": "OTH", "target": ""}]
lt = cs.c2b_tables(li, {"N1": "main"}, "main", lenient=True)
assert [r for r in lt if r["version_id"] == "N1" and r["type"] == "FAT"][0]["count"] == 1
assert [r for r in lt if r["version_id"] == "N1" and r["type"] == "OTH"][0]["count"] == 2   # same type not doubled
assert [r for r in lt if r["version_id"] == "ALL" and r["type"] == "FAT"][0]["instruments_with_type"] == 1
rq4 = [r for r in res["rq4"] if r["set"] == "main" and r["split"] == "all"][0]
# CHANGED (E5 records are not coded): 18 coded records + 2 uncoded linked duplicates (D017, D021) = 20 records;
# each E5 group (G1, G2) is counted once, so 18 studies
assert rq4["records_coded"] == 18 and rq4["records_uncoded_linked"] == 2 and rq4["records"] == 20, rq4
assert rq4["studies"] == 18 and rq4["records_in_e5_groups"] == 4, rq4
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
src_rows = {(r["row"], r["value"]): r["count"] for r in res["c4f_results"]
            if r["set"] == "main" and r["split"] == "all"}
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
(bad / "links.csv").write_text((out / "links.csv").read_text(encoding="utf-8"), encoding="utf-8")
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
(vbad / "links.csv").write_text((out / "links.csv").read_text(encoding="utf-8"), encoding="utf-8")
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
assert sum(ag_[(st_, "C4f_results_one_coder_only")]["n"] for st_ in ("main", "exploration", "late")
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
# calibration protocol (GSRR-39, GSRR-44): the exploration set is always calibration material; no "calibration" set
assert res["exploration_calibration_material"] is True
assert all(t["calibration_material"] is True for t in res["tables"] if t["set"] == "exploration")
assert any(t["set"] == "exploration" for t in res["tables"])
assert all("calibration_material" not in t for t in res["tables"] if t["set"] in ("main", "late"))
assert "calibration_draw" not in cs.VOCAB and "calibration" not in cs.VOCAB["set"]
assert all("calibration_draw" not in r for r in res["per_study"])
for gone in ("draw_calibration", "all_exploration_drawn", "exploration_study_ids", "exploration_calibration_flag",
             "CAL_ONLY", "CAL_SEED", "EXPL_CAL_SEED", "SMALL_POOL"):
    assert not hasattr(cs, gone), gone
# a records CSV with set "calibration" stops the script
cdir = out / "calset"
cdir.mkdir(exist_ok=True)
for kind in ["records", "instruments", "items", "c4f"]:
    (cdir / f"{kind}_reconciled.csv").write_text((out / f"{kind}_reconciled.csv").read_text(encoding="utf-8"), encoding="utf-8")
(cdir / "links.csv").write_text((out / "links.csv").read_text(encoding="utf-8"), encoding="utf-8")
cr = cs.read_csv(cdir / "records_reconciled.csv")
cr[0]["set"] = "calibration"
with open(cdir / "records_reconciled.csv", "w", encoding="utf-8", newline="") as f_:
    w_ = csv.DictWriter(f_, fieldnames=list(cr[0]))
    w_.writeheader()
    w_.writerows(cr)
try:
    cs.build_tables(cdir)
    raise AssertionError('set "calibration" must stop')
except cs.InputError:
    pass
# version_sets: first set in FIRST_SEEN_ORDER; a version in no primary set is an input error
vs_ = cs.version_sets([{"record_id": "e1", "version_id": "Z"}, {"record_id": "m1", "version_id": "Z"},
                       {"record_id": "m1", "version_id": "Y"}],
                      [{"record_id": "e1", "set": "exploration"}, {"record_id": "m1", "set": "main"}])
assert vs_ == {"Z": "exploration", "Y": "main"}, vs_
try:
    cs.version_sets([{"record_id": "x1", "version_id": "Q"}], [{"record_id": "x1", "set": "calibration"}])
    raise AssertionError("a version in no primary set must stop")
except cs.InputError:
    pass
try:
    cs.version_sets([{"record_id": "unknown", "version_id": "Q"}], [{"record_id": "m1", "set": "main"}])
    raise AssertionError("a version whose record is unknown must stop")
except cs.InputError:
    pass
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
# === review round 2 assertions ===============================================
# fix 1: not_verifiable is its own value (excluded from denominators, not evaluable), not not_met / no_term_to_compare
nv_ = dict(base, conclusion_family="fatigue", main_instrument_family="fatigue", conclusion_ai_fatigue_term="0")
assert cs.c7_conditions(dict(nv_, C6b="not_verifiable"), "L1a") == \
    {"C7_i": "not_verifiable", "C7_ii": "not_met", "C7_iii": "not_met"}
assert cs.c7_conditions(dict(nv_, main_instrument_family="not_verifiable"), "L1a")["C7_iii"] == "not_verifiable"
assert cs.c7_conditions(dict(nv_, main_instrument_family="no_family_term"), "L1a")["C7_iii"] == "no_term_to_compare"
assert cs.c7_conditions(dict(nv_, conclusion_family="none"), "L1a")["C7_iii"] == "no_term_to_compare"
assert cs.c7_conditions(dict(nv_, main_instrument_family="not_verifiable", conclusion_family="none"),
                        "L1a")["C7_iii"] == "not_verifiable"                  # the unverifiable name comes first
assert cs.c7_conditions(dict(nv_, main_instrument_family="unresolved"), "L1a")["C7_iii"] == "unresolved"
assert cs.c7(dict(nv_, C6b="not_verifiable"), "L1a") == "not_verifiable"       # nothing met, one not verifiable
assert cs.c7(dict(nv_, C6b="not_verifiable", main_instrument_family="burnout"), "L1a") == "beyond"   # (iii) met
ps_nv = {p_["problem_type"]: p_ for p_ in cs.problem_statements([{"C7_i": "not_verifiable", "C7_iii": "not_verifiable"}])}
assert ps_nv["C7 (i) causal wording not supported by the design"]["evaluable"] == 0
assert ps_nv["C7 (iii) conclusion term and instrument name in different term families"]["evaluable"] == 0
dn_nv = {r["value"]: r["denominator"] for r in cs.count_table(
    [{"record_id": str(k), "C7_i": v} for k, v in enumerate(["met", "not_met", "not_verifiable"])], "C7_i", {})}
assert dn_nv["not_verifiable"] == 2, dn_nv                                     # excluded from the denominator (GSRR-53)
# fix 2: C6c order. Title 'no' wins whatever the main instrument
tc = dict(base, title_ai_fatigue_term="no")
assert cs.c6c(dict(tc, main_instrument_identified="0"), "L4") == "no_ai_term"
assert cs.c6c(dict(tc, main_instrument_identified="0"), "") == "no_ai_term"
assert cs.c6c(dict(tc, main_instrument_identified="unresolved"), "unresolved") == "no_ai_term"
ty = dict(base, title_ai_fatigue_term="yes")
assert cs.c6c(dict(ty, main_instrument_identified="0"), "L1a") == "cannot_decide"
assert cs.c6c(ty, "not_verifiable") == "cannot_decide" and cs.c6c(ty, "") == "cannot_decide"
assert cs.c6c(dict(ty, main_instrument_identified="unresolved"), "L3") == "unresolved"
assert cs.c6c(dict(ty, title_ai_fatigue_term="unresolved", main_instrument_identified="0"), "L3") == "unresolved"
assert cs.c6c(ty, "L1b") == "ai_term_L1a_L2" and cs.c6c(ty, "L5") == "ai_term_L3_L6"
# fix 3: only a non-gross inconsistency -> no_gross (a calculated result and no gross one)
assert cs.c4f_gross([{"consistent": "no", "gross": "0"}]) == "no_gross"
assert cs.c4f_summary([{"consistent": "no", "gross": "0"}]) == "any_inconsistency"
assert cs.c4f_gross([{"consistent": "no", "gross": "0"}, {"consistent": "na", "gross": "0"}]) == "no_gross"
# fix 4: input validation (GSRR-64). Positive control: an unchanged clone loads; each mutation stops
import shutil  # noqa: E402


def clone(name):
    dd = out / name
    if dd.exists():
        shutil.rmtree(dd)
    dd.mkdir()
    for f_ in [f"{k}_{c_}.csv" for k in ["records", "instruments", "items", "c4f"] for c_ in ["reconciled", "coder1", "coder2"]] \
            + ["links.csv"]:
        shutil.copy(out / f_, dd / f_)
    return dd


def rewrite(dd, kind, mutate=None, drop=None):
    path = dd / (f"{kind}_reconciled.csv" if kind != "links" else "links.csv")
    rows_ = cs.read_csv(path)
    if mutate:
        mutate(rows_)
    cols_ = [c_ for c_ in rows_[0] if c_ != drop]
    with open(path, "w", encoding="utf-8", newline="") as f_:
        w2 = csv.DictWriter(f_, fieldnames=cols_, extrasaction="ignore")
        w2.writeheader()
        w2.writerows(rows_)


def must_stop(label, kind, mutate=None, drop=None, needle=None):
    dd = clone("val_" + label)
    cs.build_tables(dd)                                     # positive control: the clone is valid
    rewrite(dd, kind, mutate, drop)
    try:
        cs.build_tables(dd)
    except cs.InputError as e_:
        assert needle is None or needle in str(e_), (label, str(e_))
        return
    raise AssertionError(f"{label}: invalid input must stop")


must_stop("c3_bad", "records", lambda rs: rs[0].update(C3="amount_of_use|sleep"), needle="'sleep' not allowed in column C3")
must_stop("c3_rep", "records", lambda rs: rs[0].update(C3="amount_of_use|amount_of_use"), needle="repeated value in column C3")
must_stop("family_rep", "records", lambda rs: rs[0].update(conclusion_family="fatigue|fatigue"), needle="repeated value in column conclusion_family")
must_stop("centre", "records", lambda rs: rs[0].update(centre="C"), needle="'C' not allowed in column centre")
must_stop("centre_empty_unknown", "records", lambda rs: rs[3].update(centre="a"), needle="'a' not allowed in column centre")   # case counts
must_stop("population", "records", lambda rs: rs[0].update(population="pensioners"), needle="'pensioners' not allowed in column population")
must_stop("peer", "records", lambda rs: rs[0].update(peer_reviewed="yes"), needle="'yes' not allowed in column peer_reviewed")
must_stop("c1", "records", lambda rs: rs[0].update(C1_L2="2"), needle="'2' not allowed in column C1_L2")
must_stop("c4b", "records", lambda rs: rs[0].update(C4b="maybe"), needle="'maybe' not allowed in column C4b")
must_stop("c4e", "records", lambda rs: rs[0].update(C4e_agreement="some"), needle="'some' not allowed in column C4e_agreement")
must_stop("c5", "records", lambda rs: rs[0].update(C5="linked"), needle="'linked' not allowed in column C5")
must_stop("ident", "records", lambda rs: rs[0].update(conclusion_identified="yes"), needle="'yes' not allowed in column conclusion_identified")
must_stop("mi_ident", "records", lambda rs: rs[0].update(main_instrument_identified="2"), needle="'2' not allowed in column main_instrument_identified")
must_stop("ai_term", "records", lambda rs: rs[0].update(conclusion_ai_fatigue_term="yes"), needle="'yes' not allowed in column conclusion_ai_fatigue_term")
must_stop("family", "records", lambda rs: rs[0].update(main_instrument_family="happiness"), needle="'happiness' not allowed in column main_instrument_family")
must_stop("set", "records", lambda rs: rs[0].update(set="pilot"), needle="'pilot' not allowed in column set")
must_stop("gross_pair", "c4f", lambda rs: rs[0].update(consistent="yes", gross="1"), needle="gross=1 in result")
must_stop("gross_na", "c4f", lambda rs: rs[0].update(consistent="na", gross="1"), needle="gross=1 in result")
must_stop("c4f_source", "c4f", lambda rs: rs[0].update(source="figure"), needle="'figure' not allowed in column source")
must_stop("origin_missing", "instruments", drop="origin", needle="missing columns ['origin']")
must_stop("c2d_missing", "instruments", drop="C2d_reason", needle="missing columns ['C2d_reason']")
must_stop("origin_bad", "instruments", lambda rs: rs[0].update(origin="invented"), needle="'invented' not allowed in column origin")
must_stop("mod_bad", "instruments", lambda rs: rs[0].update(mod_scoring="yes"), needle="'yes' not allowed in column mod_scoring")
must_stop("c2c_empty", "instruments", lambda rs: rs[0].update(C2c_pilot=""), needle="empty cell in C2c_pilot")
must_stop("items_full", "instruments", lambda rs: rs[0].update(items_full="twelve"), needle="'twelve' is not a whole number in column items_full")
must_stop("item_boundary", "items", lambda rs: rs[0].update(boundary="yes"), needle="'yes' not allowed in column boundary")
must_stop("item_target", "items", lambda rs: rs[0].update(target="NOWHERE"), needle="'NOWHERE' not allowed in column target")
must_stop("item_secondary", "items", lambda rs: rs[0].update(secondary_type="XYZ"), needle="'XYZ' not allowed in column secondary_type")
must_stop("item_source_missing", "items", drop="item_source", needle="missing columns ['item_source']")
# E5 (GSRR-35): a second coded record in one group, or a group without a coded record, stops
must_stop("e5_two_coded", "links", lambda rs: rs.append({"record_id": "D018", "group_id": "G1"}), needle="E5 group G1 has 2 coded records")
must_stop("e5_no_coded", "links", lambda rs: rs.append({"record_id": "D099", "group_id": "G9"}), needle="E5 group G9 has 0 coded records")
# GSRR-43: a missing code stands alone in a multi-value cell (positive control: must_stop clones are valid)
must_stop("mi_family_unresolved", "records", lambda rs: rs[0].update(main_instrument_family="fatigue|unresolved"),
          needle="must stand alone in column main_instrument_family")
must_stop("concl_family_nv", "records", lambda rs: rs[0].update(conclusion_family="fatigue|not_verifiable"),
          needle="must stand alone in column conclusion_family")
must_stop("family_none_combined", "records", lambda rs: rs[0].update(conclusion_family="none|fatigue"),
          needle="missing code 'none' must stand alone in column conclusion_family")
must_stop("c3_none_combined", "records", lambda rs: rs[0].update(C3="none|amount_of_use"),
          needle="must stand alone in column C3")
must_stop("c3_missing_combined", "records", lambda rs: rs[0].update(C3="attitude|not_applicable"),
          needle="'not_applicable' must stand alone in column C3")
# GSRR-35 / GSRR-43: C5 = e5_group exactly for the coded records of E5 groups (both directions)
must_stop("c5_linked_not_e5", "records",
          lambda rs: [r_.update(C5="no_signs") for r_ in rs if r_["record_id"] == "D016"],
          needle="coded record D016 is in E5 group but C5 is 'no_signs'")
must_stop("c5_e5_not_linked", "records",
          lambda rs: [r_.update(C5="e5_group") for r_ in rs if r_["record_id"] == "D001"],
          needle="record D001 has C5 e5_group but is not in links.csv")


def must_stop_short(label, kind, drop_n, needle):
    """Short rows (GSRR-64): the last drop_n cells of the last data row are missing, so DictReader gives None."""
    dd = clone("short_" + label)
    cs.build_tables(dd)                                     # positive control
    path = dd / (f"{kind}_reconciled.csv" if kind != "links" else "links.csv")
    lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
    lines[-1] = ",".join(lines[-1].split(",")[:-drop_n])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        cs.build_tables(dd)
    except cs.InputError as e_:
        assert needle in str(e_), (label, str(e_))
        return
    raise AssertionError(f"{label}: a short row must stop")


for kind_ in ["records", "instruments", "c4f"]:
    hdr_ = cs.read_table(out / f"{kind_}_reconciled.csv")[0]
    must_stop_short(kind_, kind_, 1, f"empty cell in {hdr_[-1]}")
must_stop_short("items_required", "items", 3, "empty cell in boundary")    # boundary, secondary_type, target missing
dd_ = clone("short_items_optional")                                        # optional trailing cells: None reads as empty
p_ = dd_ / "items_reconciled.csv"
ln_ = p_.read_text(encoding="utf-8").rstrip("\n").split("\n")
ln_[-1] = ",".join(ln_[-1].split(",")[:-1])
p_.write_text("\n".join(ln_) + "\n", encoding="utf-8")
assert cs.build_tables(dd_)["c2b"]
dd_ = clone("short_links")                                                 # a links row with only a record_id
cs.build_tables(dd_)
with open(dd_ / "links.csv", "a", encoding="utf-8", newline="") as f_:
    f_.write("D099\n")
try:
    cs.build_tables(dd_)
    raise AssertionError("a links row without group_id must stop")
except cs.InputError as e_:
    assert "links.csv: empty cell" in str(e_), e_
# an empty file still fails the header check; a header-only file passes the header check
for kind_ in ["records", "instruments", "items", "c4f"]:
    dd_ = clone("empty_" + kind_)
    (dd_ / f"{kind_}_reconciled.csv").write_text("", encoding="utf-8")
    try:
        cs.build_tables(dd_)
        raise AssertionError(f"empty {kind_} file must fail the header check")
    except cs.InputError as e_:
        assert "empty file" in str(e_) or "no header" in str(e_), e_
dd_ = clone("empty_links")
(dd_ / "links.csv").write_text("", encoding="utf-8")
try:
    cs.build_tables(dd_)
    raise AssertionError("empty links file must fail")
except cs.InputError:
    pass
dd_ = clone("header_only_items")
(dd_ / "items_reconciled.csv").write_text(",".join(cs.REQUIRED["items"]) + "\n", encoding="utf-8")
assert cs.build_tables(dd_)["c2b"]                           # no items: every instrument is "items unavailable"
dd_ = clone("header_only_cols")
(dd_ / "items_reconciled.csv").write_text("version_id,item_no\n", encoding="utf-8")
try:
    cs.build_tables(dd_)
    raise AssertionError("a header-only file with missing columns must fail")
except cs.InputError as e_:
    assert "missing columns" in str(e_)
# a repeated value in a multi-value cell counts once even if it got past validation
assert {r["value"]: r["count"] for r in cs.count_table(
    [{"record_id": "a", "C3": "amount_of_use|amount_of_use|attitude"}], "C3", {})} == {"amount_of_use": 1, "attitude": 1}
# the stop surfaces as exit code 3 from the command line
import subprocess  # noqa: E402
dd_ = clone("cli_stop")
rewrite(dd_, "records", lambda rs: rs[0].update(centre="C"))
proc = subprocess.run([sys.executable, str(Path(cs.__file__)), "--tables", str(dd_)], capture_output=True, text=True)
assert proc.returncode == 3 and "STOPPED" in proc.stderr, (proc.returncode, proc.stderr)
# fix 5: E5-linked records are not coded; they appear only in links.csv
coded_ids_ = {r["record_id"] for r in cs.read_csv(out / "records_reconciled.csv")}
assert not set(E5_UNCODED) & coded_ids_ and set(E5_UNCODED) <= {l_["record_id"] for l_ in links}
assert not set(E5_UNCODED) & {r["record_id"] for r in cs.read_csv(out / "c4f_reconciled.csv")}
assert not set(E5_UNCODED) & {r["record_id"] for r in cs.read_csv(out / "instruments_reconciled.csv")}
tab_main = {r["value"]: r for r in res["tables"] if r["set"] == "main" and r["split"] == "all" and r["code"] == "C6b"}
assert all(r["studies"] == 18 for r in tab_main.values()), tab_main      # the 10-study minimum counts coded records
rq_pop = [r for r in res["rq4"] if r["set"] == "main" and r["split"] == "population"]
assert sum(r["records_coded"] for r in rq_pop) == 18 and sum(r["records_uncoded_linked"] for r in rq_pop) == 2
assert sum(r["studies"] for r in rq_pop) == 18
# an uncoded E5 record counts under the set and population group of its group's coded record (GSRR-35)
pop_of_ = {r["record_id"]: r["population"] for r in res["recs"]}
for g_ in {r["group"] for r in rq_pop}:
    want_ = sum(1 for u_, c_ in (("D017", "D016"), ("D021", "D020")) if pop_of_[c_] == g_ and sets[c_] == "main")
    got_ = [r["records_uncoded_linked"] for r in rq_pop if r["group"] == g_]
    assert got_ == [want_], (g_, got_, want_)
assert any(r["records_uncoded_linked"] > 0 for r in rq_pop)
r4 = cs.rq4_counts([{"record_id": "a", "set": "main", "population": "p", "C5": "e5_group"},
                    {"record_id": "b", "set": "main", "population": "p", "C5": "signs_not_confirmed"},
                    {"record_id": "c", "set": "main", "population": "q", "C5": "no_signs"}],
                   [{"record_id": "a", "group_id": "G"}, {"record_id": "a2", "group_id": "G"},
                    {"record_id": "a3", "group_id": "G"}], "main")
assert (r4["records_coded"], r4["records_uncoded_linked"], r4["records"], r4["studies"]) == (3, 2, 5, 3), r4
assert r4["signs_not_confirmed"] == 1 and r4["records_in_e5_groups"] == 3, r4
r4p = cs.rq4_counts([{"record_id": "a", "set": "main", "population": "p"}, {"record_id": "c", "set": "main", "population": "q"}],
                    [{"record_id": "a", "group_id": "G"}, {"record_id": "a2", "group_id": "G"}], "main", "q")
assert (r4p["records"], r4p["studies"], r4p["group"]) == (1, 1, "q"), r4p       # another group's duplicates do not leak
# fix 6: agreement for the conclusion / main-instrument identification and the AI-fatigue-term code
for c_ in ["conclusion_identified", "main_instrument_identified", "conclusion_ai_fatigue_term"]:
    rows_c = [ag_[(st_, c_)] for st_ in ("main", "exploration") if (st_, c_) in ag_]
    assert len(rows_c) == 2 and all(r["n"] > 0 and r["percent_agreement"] is not None and "kappa" in r for r in rows_c), c_
    assert any(r["percent_agreement"] < 1 for r in rows_c), c_              # the dummy coder 2 differs on them
# fix 7: C4f per result and RQ4 are also given by population group; C2b and instruments used are not
c4f_pop = [r for r in res["c4f_results"] if r["set"] == "main" and r["split"] == "population"]
assert c4f_pop and {r["group"] for r in c4f_pop} == {r["group"] for r in rq_pop} and \
    {r["group"] for r in c4f_pop} <= set(cs.POPULATION_ORDER)
for row_ in ("results", "results_per_record"):
    for val_ in {r["value"] for r in res["c4f_results"] if r["set"] == "main" and r["row"] == row_ and r["split"] == "all"}:
        tot_ = sum(r["count"] for r in c4f_pop if r["row"] == row_ and r["value"] == val_)
        all_ = sum(r["count"] for r in res["c4f_results"] if r["set"] == "main" and r["split"] == "all"
                   and r["row"] == row_ and r["value"] == val_)
        assert tot_ == all_, (row_, val_, tot_, all_)                   # population groups partition the rows
    assert {r["value"] for r in res["c4f_results"] if r["set"] == "main" and r["row"] == row_ and r["split"] == "all"}, row_
assert "split" not in res["c2b"][0] and all("split" not in r for r in res["instruments_used"])
# fix 8: sensitivity() uses the coder it is given (S1-S3), not silently the reconciled values
s_rec, s3_rec = cs.sensitivity(out)
s_c2, s3_c2 = cs.sensitivity(out, "coder2")
b_c2 = cs.build_tables(out, "coder2")
b_main = [r for r in b_c2["recs"] if r["set"] == "main"]
exp_s1 = cs.problem_statements([r for r in b_main if r.get("peer_reviewed") == "1"])
got_s1 = [{k: v for k, v in r.items() if k != "analysis"} for r in s_c2 if r["analysis"] == "S1 peer-reviewed only"]
assert got_s1 == exp_s1, "S1 must use the coder given"
rec_s1 = [{k: v for k, v in r.items() if k != "analysis"} for r in s_rec if r["analysis"] == "S1 peer-reviewed only"]
assert got_s1 != rec_s1, "coder2 and reconciled values must give different S1 tables in the dummy"
c2b_exp = cs.c2b_tables(b_c2["items"], b_c2["vsets"], "main", lenient=True, insts=b_c2["insts"])
assert [{k: v for k, v in r.items() if k != "analysis"} for r in s3_c2] == c2b_exp, "S3 must use the coder given"
assert [r for r in s3_c2 if r["version_id"] != "SUMMARY"] != [r for r in s3_rec if r["version_id"] != "SUMMARY"]
# screening agreement (author 1 vs AI screener, three stages)
SCR_COLS = ["record_id", "population", "stage", "author1", "ai", "final"]
POP_ = "students_learners"
scr_rows = (
    # stage 1: 4 records. agree on 3 (i/i, e/e, i/i), differ on 1 (include vs exclude, author 1 decides include)
    [("S1", 1, "include", "include", "include"), ("S2", 1, "exclude", "exclude", "exclude"),
     ("S3", 1, "include", "include", "include"), ("S4", 1, "include", "exclude", "include")]
    # stage 2: 4 records. differ on 3: author1 wins, ai wins, neither
    + [("S1", 2, "include", "include", "include"), ("S3", 2, "include", "exclude", "include"),
       ("S4", 2, "exclude", "include", "include"), ("S5", 2, "pending", "exclude", "include")]
    # stage 3: 4 records. agree on 2 (A/A, boundary/boundary resolved B), differ on 2
    + [("S1", 3, "A", "A", "A"), ("S3", 3, "boundary", "boundary", "B"),
       ("S4", 3, "A", "B", "B"), ("S5", 3, "boundary", "A", "A")]
)


def scr_write(name, rows, cols=SCR_COLS):
    p = out / name
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for rid, st, a1, ai, fin in rows:
            w.writerow([rid, POP_, st, a1, ai, fin])
    return p


scr_p = scr_write("screening.csv", scr_rows)
sa = {r["stage"]: r for r in cs.screening_agreement(cs.load_screening(scr_p))}
# stage 1: n=4, agree 3 -> 0.75; kappa: a=[i,e,i,i] b=[i,e,i,e]: pe=(3*2+1*2)/16=0.5 -> (0.75-0.5)/0.5=0.5
assert sa[1]["n"] == 4 and sa[1]["percent_agreement"] == 0.75 and abs(sa[1]["kappa"] - 0.5) < 1e-12, sa[1]
assert (sa[1]["author1_sent_on"], sa[1]["ai_sent_on"]) == (3, 2), sa[1]
assert (sa[1]["differed"], sa[1]["decided_as_author1"], sa[1]["decided_as_ai"], sa[1]["decided_otherwise"]) == (1, 1, 0, 0)
assert sa[1]["boundary_either"] == ""
# stage 2: n=4, agree 1 -> 0.25; a=[i,i,e,p] b=[i,e,i,e]: pe=(2*2 + 1*2 + 1*0)/16 -> i:ca=2,cb=2 ->4; e:1*2=2; p:1*0 -> 6/16
#   kappa=(0.25-0.375)/(0.625)=-0.2
assert sa[2]["percent_agreement"] == 0.25 and abs(sa[2]["kappa"] - (-0.2)) < 1e-12, sa[2]
assert (sa[2]["author1_sent_on"], sa[2]["ai_sent_on"]) == (3, 2), sa[2]
assert (sa[2]["differed"], sa[2]["decided_as_author1"], sa[2]["decided_as_ai"], sa[2]["decided_otherwise"]) == (3, 1, 1, 1), sa[2]
# stage 3: n=4, agree 2 -> 0.5; a=[A,bd,A,bd] b=[A,bd,B,A]: pe=(A:2*2 + bd:2*1 + B:0)/16=6/16 -> kappa=(0.5-0.375)/0.625=0.2
assert sa[3]["percent_agreement"] == 0.5 and abs(sa[3]["kappa"] - 0.2) < 1e-12, sa[3]
assert (sa[3]["author1_sent_on"], sa[3]["ai_sent_on"]) == (4, 4), sa[3]
assert (sa[3]["differed"], sa[3]["decided_as_author1"], sa[3]["decided_as_ai"], sa[3]["decided_otherwise"]) == (2, 0, 2, 0), sa[3]
assert sa[3]["boundary_either"] == 2, sa[3]
assert cs.screening_agreement([])[0]["kappa"] is None and cs.screening_agreement([])[2]["boundary_either"] == 0
# CLI: writes out/screening_agreement.csv next to the input, exit 3 on bad input
assert cs.main.__module__ == "c_synthesis"
import subprocess
rc_ = subprocess.run([sys.executable, str(Path(cs.__file__)), "--screening", str(scr_p)], capture_output=True)
assert rc_.returncode == 0 and (out / "out" / "screening_agreement.csv").exists(), rc_
# kappa undefined when both screeners use one category only
assert cs.screening_agreement(cs.load_screening(scr_write("screening_one.csv", [("S1", 1, "include", "include", "include")])))[0]["kappa"] is None


def scr_must_stop(label, rows, needle, cols=SCR_COLS):
    p = scr_write(f"screening_bad_{label}.csv", rows, cols)
    try:
        cs.load_screening(p)
    except cs.InputError as e:
        assert needle in str(e), (label, str(e))
        bad = subprocess.run([sys.executable, str(Path(cs.__file__)), "--screening", str(p)], capture_output=True)
        assert bad.returncode == 3, (label, bad.returncode)
        return
    raise AssertionError(f"screening {label}: expected InputError")


scr_must_stop("final_boundary", [("S1", 3, "A", "B", "boundary")], "not allowed in column final")
scr_must_stop("final_pending_stage1", [("S1", 1, "include", "exclude", "pending")], "not allowed in column final")
scr_must_stop("duplicate", [("S1", 1, "include", "include", "include"), ("S1", 1, "include", "include", "include")], "twice")
scr_must_stop("agree_final_differs", [("S1", 2, "include", "include", "exclude")], "both screeners")
scr_must_stop("stage3_value_in_stage1", [("S1", 1, "A", "include", "include")], "not allowed in column author1")
scr_must_stop("missing_column", [("S1", 1, "include", "include", "include")], "missing columns", cols=SCR_COLS[:-1] + ["finl"])
scr_must_stop("empty_cell", [("S1", 1, "include", "", "include")], "empty cell in ai")
print(f"dummy tables in {out}; all boundary tests passed")
