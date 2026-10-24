import os, sys, collections
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
import c_screening as cs, make_trace_db as db
from openpyxl import load_workbook
ws = load_workbook(sys.argv[1], data_only=True)["判定"]
rows = list(ws.iter_rows(values_only=True)); head = [str(c) for c in rows[0]]
ft = os.path.expanduser("~/Documents/TRACE/fulltext")
probs, cnt, codes, cent, reads = [], collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
for r in rows[1:]:
    d = {k: ("" if v is None else str(v).strip()) for k, v in zip(head, r)}
    i = d["ID"]
    if not i: continue
    dec = cs.JA_DECISION.get(d["判定"], "?"); centre = cs.JA_CENTRE.get(d["中心"], "?"); read = cs.JA_READ.get(d["読んだ範囲"], "?")
    code = d["除外理由"]
    if "?" in (dec, centre, read) or (code and code not in cs.CODES):
        probs.append((i, "選び肢の外の値")); continue
    try:
        cs.check_decision(i, 2, dec, code, centre)
    except cs.Stop as e:
        probs.append((i, str(e))); continue
    has = bool(db.fulltext_file(i, ft))
    if not d["読んだ範囲"]: probs.append((i, "読んだ範囲が空"))
    if not d["根拠メモ"]: probs.append((i, "根拠メモが空"))
    if code == "E6" and has: probs.append((i, "全文があるのに E6"))
    if not has and read in ("full text", "part of full text"): probs.append((i, "全文が無いのに読んだ範囲が全文"))
    if has and read in ("title only", "abstract"): probs.append((i, "全文があるのに読んだ範囲が題名か抄録（確かめる）"))
    cnt[dec] += 1; codes[(dec, code)] += 1; reads[read] += 1
    if dec == "include": cent[centre] += 1
print("records", sum(cnt.values()), dict(cnt)); print("codes", dict(codes)); print("centres", dict(cent)); print("read", dict(reads))
print("problems", len(probs))
for p in probs: print("  ", p)
