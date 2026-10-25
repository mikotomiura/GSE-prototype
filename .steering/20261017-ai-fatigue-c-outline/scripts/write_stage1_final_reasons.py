"""判断 104: 2 人で決めた段 1 の除外理由（16 件の冊の L 列）を DB の『段1』の『最終の除外理由』に書く。
使い方: uv run -q --with openpyxl python write_stage1_final_reasons.py <戻った 16 件の冊> <TRACE_database.xlsx>
最終の理由は 16 件とも冊の L 列の案（共著者が別の理由を挙げた 7 件も研究者の選択で案のまま）。
"""
import sys, openpyxl
book, db = sys.argv[1], sys.argv[2]
ws = openpyxl.load_workbook(book)["除外理由"]
final = {}
for r in range(2, ws.max_row + 1):
    i = ws.cell(r, 1).value
    if i: final[i] = ws.cell(r, 12).value
assert len(final) == 16 and set(final.values()) <= {"E1","E2","E3","E4","E7"}, final
wb = openpyxl.load_workbook(db)
s = wb["段1"]
hdr = [c.value for c in s[1]]
ci, ck, cl = hdr.index("ID")+1, hdr.index("最終")+1, hdr.index("最終の除外理由")+1
seen = set()
for r in range(2, s.max_row + 1):
    i = s.cell(r, ci).value
    if i in final:
        assert s.cell(r, ck).value in (None, "", "除外"), (i, s.cell(r, ck).value)
        assert s.cell(r, cl).value in (None, ""), (i, s.cell(r, cl).value)
        s.cell(r, cl).value = final[i]; seen.add(i)
assert seen == set(final), set(final) - seen
wb.save(db)
print("wrote", len(seen))
