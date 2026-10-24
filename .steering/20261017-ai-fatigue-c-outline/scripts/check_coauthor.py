"""Name every record of author 2's returned workbook that import-coauthor would stop on (IDs and the rule only)."""
import os, sys, collections
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
import c_screening as cs
sheet = cs.sheet_rows(sys.argv[1], 2)
want = open(os.path.expanduser("~/TRACE/screening/coauthor/h1.ids")).read().split()
probs = collections.defaultdict(list)
for i in want:
    r = sheet[i]
    dec = cs.JA_DECISION.get(r.get("判定"), "?"); centre = cs.JA_CENTRE.get(r.get("中心", ""), "?"); read = cs.JA_READ.get(r.get("読んだ範囲", ""), "?")
    code = r.get("除外理由", "")
    if "?" in (dec, centre, read) or (code and code not in cs.CODES):
        probs["a value outside the drop-down list"].append(i); continue
    try:
        cs.check_decision(i, 2, dec, code, centre)
    except cs.Stop as e:
        probs[str(e).split(": ", 1)[1]].append(i)
for k, v in probs.items():
    print(len(v), k, v)
print("records with a stop:", sum(len(v) for v in probs.values()), "of", len(want))
