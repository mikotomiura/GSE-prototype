"""Independent check of round 5 design 3.6: the names round 4 ran must carry exactly the same records in round 5
(per-attacker gain, ci95, null per permutation, null95), and the round 4 verdicts are listed beside round 5's.
Exits 1 if any record or label-level count differs, or a round 4 name is missing in round 5. A changed verdict is
reported but is not a failure by itself (design 3.6 classifies it), though with identical records it cannot occur."""
import json
import sys

r3 = json.load(open(sys.argv[1], encoding="utf-8"))
r4 = json.load(open(sys.argv[2], encoding="utf-8"))
KEYS = ["full/hgb", "full/lr", "small/hgb", "small/lr"]
bad = 0
for t in ["L300", "L60", "L1800"]:
    c3, c4 = r3[t]["configs"], r4[t]["configs"]
    same = diff = 0
    changed = []
    for n, a in c3.items():
        if n not in c4:
            print(f"  {t} {n}: missing in round 5")
            diff += 1
            continue
        b = c4[n]
        fields = [a[k] == b[k] for k in KEYS] + [a.get("null_gain_max_by_perm") == b.get("null_gain_max_by_perm"),
                                                  a.get("null95") == b.get("null95")]
        if all(fields):
            same += 1
        else:
            diff += 1
            print(f"  {t} {n}: differs")
        if a.get("verdict") != b.get("verdict"):
            changed.append((n, a.get("verdict"), b.get("verdict")))
    for k in ("n_windows", "n_positive_windows", "n_sessions_with_positive", "auc_A"):
        if r3[t][k] != r4[t][k]:
            print(f"  {t} {k}: {r3[t][k]} != {r4[t][k]}")
            diff += 1
    bad += diff
    print(f"{t}: {len(c3)} round 4 names, {same} identical, {diff} differ; verdict changes: {changed or 'none'}")
sys.exit(1 if bad else 0)
