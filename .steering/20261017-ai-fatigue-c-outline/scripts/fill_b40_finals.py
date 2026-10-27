"""Decision 119: the finals of batch b40 the two humans decided together (the records `differences --stage 2 --batch
b40` names). The values are in a CSV outside the repository (ID, 最終, 最終の除外理由, 最終の中心). It writes those
cells of the database's '段2・3' for the named records only, after checking that each record is in batch b40, that its
'最終…' cells are empty, and that the values pass the tool's check_decision (E5 is refused: it needs the other record).
Usage: fill_b40_finals.py <db.xlsx> <values.csv> <out.xlsx>"""
import csv, os, sys
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
from openpyxl import load_workbook
import c_screening as c

DB, VALS, OUT = sys.argv[1:4]
B40 = {"S04-30", "X01", "CS00828", "S14-14", "CS07671", "CS07568", "CS07885"}
DEC = {k: v for k, v in c.JA_DECISION.items() if k}
FINALS = ("最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）")

want = list(csv.DictReader(open(VALS, encoding="utf-8")))
wb = load_workbook(DB)
ws = wb["段2・3"]
h = {cell.value: cell.column for cell in ws[1]}
rows = {ws.cell(i, h["ID"]).value: i for i in range(2, ws.max_row + 1)}
for v in want:
    rid = v["ID"]
    if rid not in B40 or rid not in rows:
        sys.exit(f"{rid}: not a b40 record of the database")
    i = rows[rid]
    if any(ws.cell(i, h[col]).value not in (None, "") for col in FINALS):
        sys.exit(f"{rid}: a final is already written")
    dec, code, cen = v["最終"], v["最終の除外理由"], v["最終の中心"]
    if dec not in DEC or code == "E5":
        sys.exit(f"{rid}: 最終 {dec!r} / code {code!r}")
    if dec == "含める":
        if cen not in ("中心-A", "中心-B", "合意できない"):
            sys.exit(f"{rid}: an inclusion needs 最終の中心")
        c.check_decision(rid, 2, "include", code, "x")
    else:
        if cen:
            sys.exit(f"{rid}: a centre for a record not included")
        c.check_decision(rid, 2, DEC[dec], code)
    ws.cell(i, h["最終"]).value = dec
    ws.cell(i, h["最終の除外理由"]).value = code or None
    ws.cell(i, h["最終の中心"]).value = cen or None
wb.save(OUT)
print(f"wrote {len(want)} records")
