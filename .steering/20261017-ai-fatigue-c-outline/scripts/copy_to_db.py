import sys, os
from openpyxl import load_workbook
src, dbp, out = sys.argv[1:4]
FIX = {"S08-03": "除外", "CS03205": "除外"}   # 研究者の選択: 保留・E7 → 除外・E7（付録 6 §4）
INPUTS = ["判定", "除外理由", "中心", "読んだ範囲", "根拠メモ"]
ws = load_workbook(src, data_only=True)["判定"]
h = [c.value for c in ws[1]]
vals = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    d = dict(zip(h, r))
    if d["ID"]:
        vals[d["ID"]] = {k: d[k] for k in INPUTS}
for i, dec in FIX.items():
    assert vals[i]["判定"] == "保留" and vals[i]["除外理由"] == "E7"
    vals[i]["判定"] = dec
wb = load_workbook(dbp)
s2 = wb["段2・3"]; hd = [c.value for c in s2[1]]
done = 0
for row in s2.iter_rows(min_row=2):
    i = row[0].value
    if i in vals:
        for k in INPUTS:
            row[hd.index(k)].value = vals[i][k] if vals[i][k] not in ("",) else None
        done += 1
assert done == len(vals) == 149, done
wb.save(out); print("wrote", out, done)
