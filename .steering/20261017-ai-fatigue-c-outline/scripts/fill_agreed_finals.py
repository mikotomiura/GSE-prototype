"""Decision 114: the sheet of the two humans after author 2 answered author 1's proposal. Starting from the
sheet as author 1 left it (decision 113, which keeps the validations and filters), it carries over author 2's
answer and comment from the returned workbook, and for the records author 2 agreed to writes the proposal into
'最終', '最終の除外理由', '最終の中心' (the two humans' decision is the proposal and the agreement). The records
author 2 did not agree to keep '未判定' (段2) or an empty '最終の中心' (段3) and get a line in '注意': the two
decide them together (GSRR-33). Each written final passes the tool's check_decision.
Usage: fill_agreed_finals.py <author 1's proposal.xlsx> <returned.xlsx> <out.xlsx>"""
import os, sys
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
from openpyxl import load_workbook
import c_screening as c

BASE, RET, OUT = sys.argv[1:4]
NOTE = "著者 2 が案に同意しなかった記録。2 人で話して『最終…』を書く。"
DEC = {k: v for k, v in c.JA_DECISION.items() if k}
CEN = {k: v for k, v in c.JA_CENTRE.items() if k}


def cols(ws):
    return {cell.value: cell.column for cell in ws[1]}


def blank(v):
    return v in (None, "")


wb, rb = load_workbook(BASE), load_workbook(RET)
n = {}
for name in ("段2", "段3"):
    w, r = wb[name], rb[name]
    hw, hr = cols(w), cols(r)
    if hw != hr or w.max_row != r.max_row:
        sys.exit(f"{name}: the returned sheet's columns or rows differ from the proposal's")
    stage2 = name == "段2"
    for i in range(2, w.max_row + 1):
        g = lambda h: w.cell(i, hw[h]).value
        rid = g("ID")
        if r.cell(i, hr["ID"]).value != rid:
            sys.exit(f"{name} row {i}: ID {rid} vs {r.cell(i, hr['ID']).value}")
        for h in ("著者 2 の同意", "著者 2 のコメント"):
            w.cell(i, hw[h]).value = r.cell(i, hr[h]).value
        ans = g("著者 2 の同意")
        fin = [g("最終"), g("最終の除外理由"), g("最終の中心"), g("同じ標本の相手（E5）")] if stage2 else [g("最終の中心")]
        if [v for v in fin if not blank(v) and v != "未判定"]:
            sys.exit(f"{name} {rid}: a final is already written")
        if ans == "同意する":
            if stage2:
                dec, code, cen = g("著者 1 の案"), g("著者 1 の案の除外理由") or "", g("著者 1 の案の中心") or ""
                c.check_decision(rid, 2, DEC[dec], code, CEN[cen] if cen else "")
                if code == "E5":
                    sys.exit(f"{rid}: E5 needs the other record, which the proposal does not carry")
                w.cell(i, hw["最終"]).value = dec
                w.cell(i, hw["最終の除外理由"]).value = code or None
                w.cell(i, hw["最終の中心"]).value = cen or None
            else:
                cen = g("著者 1 の案の中心")
                if cen not in ("中心-A", "中心-B"):
                    sys.exit(f"{rid}: stage 3 proposal {cen!r}")
                w.cell(i, hw["最終の中心"]).value = cen
        elif ans == "同意しない":
            old = g("注意")
            w.cell(i, hw["注意"]).value = f"{NOTE}\n{old}" if old else NOTE
        else:
            sys.exit(f"{name} {rid}: author 2's answer {ans!r}")
        n[(name, ans)] = n.get((name, ans), 0) + 1
wb.save(OUT)
for k, v in sorted(n.items()):
    print(*k, v)
