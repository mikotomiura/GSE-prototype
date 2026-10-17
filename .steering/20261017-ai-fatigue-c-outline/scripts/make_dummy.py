"""Build a dummy code table (no real records) to test c_synthesis.py before stage 5 (GSRR-64)."""

import csv
import random
import sys
from pathlib import Path

rng = random.Random(1)
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

LV = ["L1a", "L1b", "L2", "L3", "L4", "L5", "L6"]
FAM = ["fatigue", "exhaustion", "burnout", "none"]


def rec(rid, set_name, coder):
    r = {"record_id": rid, "set": set_name, "coder": coder,
         "population": rng.choice(["students_learners", "workers_other", "health_professionals"]),
         "centre": rng.choice(["A", "B"])}
    lv = rng.choice(LV)
    for x in LV:
        r[f"C1_{x}"] = "1" if x == lv else "0"
    r["C3"] = rng.choice(["amount_of_use", "dependence", "attitude", "none"])
    for k in ["C4a", "C4b", "C4c", "C4d"]:
        r[k] = rng.choice(["consistent", "inconsistent", "not_verifiable"])
    r["C4e"] = rng.choice(["not_applicable", "codebook_no", "agreement_none", "codebook_yes"])
    r["C5"] = rng.choice(["e5_group", "signs_not_confirmed", "no_signs"])
    r["C6a"] = rng.choice(["same_family", "different_family", "no_construct_term"])
    r["C6b"] = rng.choice(["match", "mismatch", "no_causal_wording"])
    r["conclusion_ai_fatigue_term"] = rng.choice(["0", "1"])
    r["conclusion_family"] = rng.choice(FAM)
    r["main_instrument_family"] = rng.choice(FAM[:3])
    return r


def write(name, rows):
    with open(out / name, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


ids = [f"D{i:03d}" for i in range(1, 31)]
sets = {i: ("exploration" if n < 10 else "late" if n >= 28 else "confirmation") for n, i in enumerate(ids)}
reconciled = [rec(i, sets[i], "reconciled") for i in ids]
write("records_reconciled.csv", reconciled)
coders = []
for r in reconciled:
    c1 = dict(r, coder="coder1")
    c2 = dict(r, coder="coder2")
    if rng.random() < 0.2:
        c2["C6b"] = "match" if r["C6b"] != "match" else "mismatch"
    coders += [c1, c2]
write("records_coders.csv", coders)
write("c4f_reconciled.csv", [{"record_id": i, "result_id": f"{i}-r{k}", "consistent": rng.choice(["yes", "yes", "no", "na"])}
                              for i in ids for k in range(2)])
insts = [{"record_id": i, "set": sets[i], "version_id": f"V{n % 12:02d}"} for n, i in enumerate(ids)]
write("instruments_reconciled.csv", insts)
items = [{"version_id": f"V{v:02d}", "item_no": str(k), "type": rng.choice(["MOT", "AVO", "FUT", "IRR", "FAT", "FAT", "OTH"])}
         for v in range(12) for k in range(1, 9)]
write("items_reconciled.csv", items)
(out / "pool_ids.txt").write_text("\n".join(i for i in ids if sets[i] == "confirmation"), encoding="utf-8")
write("candidates.csv", [{"record_id": i, "population": r["population"]} for i, r in zip(ids, reconciled)])
print(f"dummy tables in {out}")
