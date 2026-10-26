"""Decision 116: copy the two humans' finals from the sheets of decision 115 to the database's '段2・3' (the tool reads
the database only). From '段2' it copies '最終', '最終の除外理由', '最終の中心', '同じ標本の相手（E5）'; from '段3'
'最終の中心'. The proposal and agreement columns are not copied (they stay in the sheets as the record of how the two
decided). The E5 partners author 1 withdrew in the re-check (S04-21, CS05713, decision 103) are cleared. It stops if
a record is in no row of the database, is in both sheets, or already has a value in a cell it would write.
Usage: copy_finals_to_db.py <db.xlsx> <out.xlsx> <sheet.xlsx>..."""
import sys
from openpyxl import load_workbook

DB, OUT, SHEETS = sys.argv[1], sys.argv[2], sys.argv[3:]
COLS2 = ["最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）"]
CLEAR_E5 = ["S04-21", "CS05713"]


def blank(v):
    return v in (None, "")


vals = {}
for p in SHEETS:
    wb = load_workbook(p)
    for name, cols in (("段2", COLS2), ("段3", ["最終の中心"])):
        ws = wb[name]
        h = {c.value: c.column for c in ws[1]}
        for i in range(2, ws.max_row + 1):
            rid = ws.cell(i, h["ID"]).value
            if rid in vals:
                sys.exit(f"{rid}: in more than one sheet")
            vals[rid] = {c: ws.cell(i, h[c]).value for c in cols}

wb = load_workbook(DB)
ws = wb["段2・3"]
h = {c.value: c.column for c in ws[1]}
rows = {ws.cell(i, h["ID"]).value: i for i in range(2, ws.max_row + 1)}
for rid in CLEAR_E5:
    i = rows[rid]
    if blank(ws.cell(i, h["同じ標本の相手（E5）"]).value):
        sys.exit(f"{rid}: no E5 partner to clear")
    ws.cell(i, h["同じ標本の相手（E5）"]).value = None
n = 0
for rid, v in vals.items():
    if rid not in rows:
        sys.exit(f"{rid}: not in the database")
    i = rows[rid]
    for col, x in v.items():
        if not blank(ws.cell(i, h[col]).value):
            sys.exit(f"{rid}: {col} already has a value")
        ws.cell(i, h[col]).value = None if blank(x) else x
    n += 1
wb.save(OUT)
print(f"copied {n} records; cleared E5 of {CLEAR_E5}")
