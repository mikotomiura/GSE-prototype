"""Decision 121: GSRR-33 decides a record left pending without a code together, and makes it unresolved if the two
cannot settle it; a final 'pending without a code' is not one of its outcomes. The records whose latest stage-2 final
(screening/s2/bNN.final2.csv, the last batch that holds the record) is pending without a code get 合意できない in
'最終' of the database's '段2・3'. It checks that each such cell holds 保留 and that 最終の除外理由, 最終の中心 and
同じ標本の相手（E5） are empty. It prints the batches to export again.
Usage: set_pending_unresolved.py <state dir> <db.xlsx> <out.xlsx>"""
import csv, sys
from pathlib import Path
from openpyxl import load_workbook

STATE, DB, OUT = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
last = {}
for f in sorted((STATE / "s2").glob("b*.final2.csv"), key=lambda p: int(p.name.split(".")[0][1:])):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        last[r["record_id"]] = (f.name.split(".")[0], r)
todo = {rid: b for rid, (b, r) in last.items() if r["final"] == "pending" and r["code"] == ""}
wb = load_workbook(DB)
ws = wb["段2・3"]
h = {c.value: c.column for c in ws[1]}
rows = {ws.cell(i, h["ID"]).value: i for i in range(2, ws.max_row + 1)}
for rid in todo:
    i = rows[rid]
    if ws.cell(i, h["最終"]).value != "保留":
        sys.exit(f"{rid}: 最終 is {ws.cell(i, h['最終']).value!r}, not 保留")
    if any(ws.cell(i, h[c]).value not in (None, "") for c in ("最終の除外理由", "最終の中心", "同じ標本の相手（E5）")):
        sys.exit(f"{rid}: another final cell is filled")
    ws.cell(i, h["最終"]).value = "合意できない"
wb.save(OUT)
batches = sorted(set(todo.values()), key=lambda b: int(b[1:]))
print(f"set 合意できない on {len(todo)} records")
print(" ".join(batches))
