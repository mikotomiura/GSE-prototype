"""Dummy code tables (no real records) and boundary tests for c_synthesis.py (GSRR-64).

Usage: python3 make_dummy.py <out_dir>
Builds the dummy tables, runs the synthesis on them, and checks expected values with assert.
"""

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_synthesis as cs  # noqa: E402

rng = random.Random(1)
out = Path(sys.argv[1])
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
    for k in ["C4a", "C4b", "C4c", "C4d"]:
        r[k] = rng.choice(["consistent", "inconsistent", "not_verifiable"])
    r["C4e_codebook"] = rng.choice(["yes", "no", "not_applicable"])
    r["C4e_agreement"] = rng.choice(["value_given", "index_only", "none", "not_applicable"])
    r["C5"] = rng.choice(["e5_group", "signs_not_confirmed", "no_signs"])
    r["C6a"] = rng.choice(["same_family", "different_family", "no_construct_term"])
    r["C6b"] = rng.choice(["match", "mismatch", "no_causal_wording"])
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
    sets[i] = "exploration" if n < 10 else "calibration" if n < 15 else "late" if n >= 30 else "confirmation"
recs = [rec(i, sets[i]) for i in ids]
insts, items = [], []
for n, i in enumerate(ids):
    vid = f"V{n % 14:02d}"
    inst = {"record_id": i, "set": sets[i], "instrument_id": "main", "version_id": vid,
            "origin": rng.choice(["new", "existing_ai", "adapted_general", "unchanged_general",
                                  "general_not_verifiable"]),
            "format": "multi_item"}
    for k in cs.INSTRUMENT_CODES:
        inst.setdefault(k, rng.choice(["stated", "found_not_stated", "no_change", "not_verifiable"]))
    insts.append(inst)
for v in range(13):            # V13 has no items -> items unavailable
    for k in range(1, 9):
        t = rng.choice(["MOT", "AVO", "FUT", "IRR", "FAT", "FAT", "OTH"])
        items.append({"record_id": "", "set": "", "version_id": f"V{v:02d}", "item_no": str(k), "type": t,
                      "boundary": rng.choice(["0", "0", "1"]), "secondary_type": rng.choice(["MOT", "FAT"]),
                      "target": rng.choice(["TASK", "AI_USE"]) if t in cs.TARGETED_TYPES else ""})
c4f = [{"record_id": i, "result_id": f"{i}-r{k}", "consistent": rng.choice(["yes", "yes", "no", "na"])}
       for i in ids for k in range(2)]
links = [{"record_id": "D016", "group_id": "G1"}, {"record_id": "D017", "group_id": "G1"},
         {"record_id": "D020", "group_id": "G2"}, {"record_id": "D021", "group_id": "G2"}]

for coder in ["reconciled", "coder1", "coder2"]:
    rr = [dict(r) for r in recs]
    it = [dict(x) for x in items]
    if coder == "coder2":
        for r in rr[::4]:
            r["C6b"] = "match" if r["C6b"] != "match" else "mismatch"
        for x in it[::5]:
            x["type"] = "OTH"
    for x in it:   # items carry the set of a record that uses the version (for per-set agreement)
        x["set"] = next((ii["set"] for ii in insts if ii["version_id"] == x["version_id"]), "")
    write(f"records_{coder}.csv", rr)
    write(f"instruments_{coder}.csv", insts)
    write(f"items_{coder}.csv", it)
    write(f"c4f_{coder}.csv", c4f)
write("links.csv", links)
pool = [i for i in ids if sets[i] in ("confirmation", "calibration")]
(out / "pool_ids.txt").write_text("\n".join(pool), encoding="utf-8")
(out / "exploration_ids.txt").write_text("\n".join(i for i in ids if sets[i] == "exploration"), encoding="utf-8")
write("candidates.csv", [{"record_id": r["record_id"], "population": r["population"]} for r in recs])

# --- boundary tests ---------------------------------------------------------
res = cs.build_tables(out)
conf = [r for r in res["recs"] if r["set"] == "confirmation"]
assert res["n_conf"] == 15 == len(conf), res["n_conf"]
assert not any(t["set"] == "calibration" for t in res["tables"]), "calibration records leaked into tables"
summ = [r for r in res["c2b"] if r["version_id"] == "SUMMARY" and r["set"] == "confirmation"][0]
assert summ["with_items"] + summ["items_unavailable"] >= 1
rq4 = [r for r in res["rq4"] if r["set"] == "confirmation"][0]
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
# C1 representative
assert cs.c1_representative({"C1_L1b": "1", "C1_L2": "1"}) == "L1b"
assert cs.c1_representative({"C1_L3": "unresolved"}) == "unresolved"
# problem statements: no evaluable values -> not evaluable
ps = cs.problem_statements([{"C4a": "not_verifiable"}, {"C4a": "unresolved"}])
assert ps[0]["statement"] == "could not be evaluated" and ps[0]["unresolved"] == 1
# minimum sizes
assert cs.count_table([{"x": "a"}] * 9, "x", {})[0]["proportion"] is None
assert cs.count_table([{"x": "a"}] * 10, "x", {})[0]["proportion"] == 1.0
two = cs.c2b_tables([{"version_id": v, "type": "FAT"} for v in ["N1", "N2"]],
                    [{"version_id": v, "set": "confirmation"} for v in ["N1", "N2", "N3"]], "confirmation")
assert two[-1]["with_items"] == 2 and two[-1]["items_unavailable"] == 1 and not two[-1]["proportions_reported"]
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
print(f"dummy tables in {out}; all boundary tests passed")
