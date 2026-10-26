"""Decision 115: the finals of the records author 2 did not agree to (decision 114), decided after reading the full
texts again. The values are in a CSV outside the repository (表, 段, ID, 最終, 最終の除外理由, 最終の中心). Starting
from the sheet of decision 114, it writes those cells for the named records only, after checking that each record
is one author 2 did not agree to and that its finals are still empty. 段2 values pass the two-human rules of the
tool (check_decision for include/exclude/pending; 合意できない in '最終の中心' only for an included record); 段3
takes 中心-A, 中心-B or 合意できない. The line decision 114 put in '注意' is replaced by one saying the two decided it.
Usage: fill_discussed_finals.py <decision 114 sheet.xlsx> <values.csv> <span, e.g. b01-22> <out.xlsx>"""
import csv, os, sys
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
from openpyxl import load_workbook
import c_screening as c

BASE, VALS, SPAN, OUT = sys.argv[1:5]
OLD = "著者 2 が案に同意しなかった記録。2 人で話して『最終…』を書く。"
NEW = "著者 2 が案に同意しなかった記録。全文を読み直して 2 人で『最終…』を決めた。"
DEC = {k: v for k, v in c.JA_DECISION.items() if k}

want = [r for r in csv.DictReader(open(VALS, encoding="utf-8")) if r["表"] == SPAN]
wb = load_workbook(BASE)
done = 0
for name in ("段2", "段3"):
    ws = wb[name]
    h = {cell.value: cell.column for cell in ws[1]}
    rows = {ws.cell(i, h["ID"]).value: i for i in range(2, ws.max_row + 1)}
    for v in (r for r in want if r["段"] == name):
        rid = v["ID"]
        if rid not in rows:
            sys.exit(f"{name} {rid}: not in the sheet")
        i = rows[rid]
        g = lambda col: ws.cell(i, h[col]).value
        if g("著者 2 の同意") != "同意しない":
            sys.exit(f"{name} {rid}: author 2 agreed to the proposal; not decided here")
        if not str(g("注意") or "").startswith(OLD):
            sys.exit(f"{name} {rid}: '注意' does not carry decision 114's line")
        if name == "段2":
            if g("最終") != "未判定" or any(g(x) not in (None, "") for x in ("最終の除外理由", "最終の中心", "同じ標本の相手（E5）")):
                sys.exit(f"{rid}: a final is already written")
            dec, code, cen = v["最終"], v["最終の除外理由"], v["最終の中心"]
            if dec == "含める":
                if cen not in ("中心-A", "中心-B", "合意できない"):
                    sys.exit(f"{rid}: an inclusion needs 最終の中心")
                c.check_decision(rid, 2, "include", code, "x")
            else:
                if cen:
                    sys.exit(f"{rid}: a centre for a record not included")
                c.check_decision(rid, 2, DEC[dec], code)
            if code == "E5":
                sys.exit(f"{rid}: E5 needs the other record")
            ws.cell(i, h["最終"]).value = dec
            ws.cell(i, h["最終の除外理由"]).value = code or None
            ws.cell(i, h["最終の中心"]).value = cen or None
        else:
            if g("最終の中心") not in (None, ""):
                sys.exit(f"{rid}: 最終の中心 is already written")
            if v["最終の中心"] not in ("中心-A", "中心-B", "合意できない"):
                sys.exit(f"{rid}: stage 3 takes 中心-A, 中心-B or 合意できない")
            ws.cell(i, h["最終の中心"]).value = v["最終の中心"]
        ws.cell(i, h["注意"]).value = NEW + str(g("注意"))[len(OLD):]
        done += 1
if done != len(want):
    sys.exit(f"wrote {done} of {len(want)}")
wb.save(OUT)
print(f"{SPAN}: wrote {done}")
