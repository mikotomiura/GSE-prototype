"""Claude 再評価シートを元ワークブックに追加して別名保存し、元シート不変を検算する。

入力: claude_eval.json（シート定義: name / title / subtitle / headers / widths / rows / table）
出力: archive/AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx（build_xlsx.py の第 2 引数で変更可）
"""
import json
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.table import Table, TableStyleInfo

import os
HERE = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.dirname(HERE)
SRC = os.path.join(ARCH, "input", "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
DST = os.path.join(ARCH, "AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx")
SP = HERE  # claude_eval.json の置き場所

FONT = "Carlito"
TEXT = "FF22343D"
TITLE_FILL = PatternFill("solid", fgColor="FF143D48")
SUB_FILL = PatternFill("solid", fgColor="FFEAF4F6")
HEAD_FILL = PatternFill("solid", fgColor="FF0F766E")
TAB = "FF7C3AED"  # 追加シートの識別用（元シートはタブ色なし）
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
WRAP_CENTER = Alignment(wrap_text=True, vertical="center")


def snapshot(wb):
    """元シートの全セル値（数式は文字列のまま）を辞書に写す。"""
    out = {}
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    out[(ws.title, c.coordinate)] = c.value
    return out


def add_sheet(wb, spec, table_idx):
    ws = wb.create_sheet(spec["name"])
    ws.sheet_properties.tabColor = TAB
    ncol = len(spec["headers"])
    last = openpyxl.utils.get_column_letter(ncol)
    ws["A1"] = spec["title"]
    ws["A1"].font = Font(name=FONT, size=11, bold=True, color="FFFFFFFF")
    ws["A1"].fill = TITLE_FILL
    ws["A1"].alignment = WRAP_TOP
    ws.merge_cells(f"A1:{last}1")
    ws["A2"] = spec["subtitle"]
    ws["A2"].font = Font(name=FONT, size=11, color=TEXT)
    ws["A2"].fill = SUB_FILL
    ws["A2"].alignment = WRAP_TOP
    ws.merge_cells(f"A2:{last}2")
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = spec.get("subtitle_height", 48)
    for j, h in enumerate(spec["headers"], 1):
        c = ws.cell(4, j, h)
        c.font = Font(name=FONT, size=11, bold=True, color="FFFFFFFF")
        c.fill = HEAD_FILL
        c.alignment = WRAP_CENTER
    ws.row_dimensions[4].height = 36
    for i, row in enumerate(spec["rows"], 5):
        if len(row) != ncol:
            raise ValueError(f"{spec['name']} row {i}: {len(row)} cols != {ncol}")
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v)
            c.font = Font(name=FONT, size=11, color=TEXT)
            c.alignment = WRAP_TOP
    for j, w in enumerate(spec["widths"], 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = w
    if spec.get("table", True) and spec["rows"]:
        ref = f"A4:{last}{4 + len(spec['rows'])}"
        t = Table(displayName=f"ClaudeEval{table_idx}", ref=ref)
        t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(t)
    ws.freeze_panes = "B5"
    return ws


def main():
    global DST
    spec_path = sys.argv[1] if len(sys.argv) > 1 else f"{SP}/claude_eval.json"
    if len(sys.argv) > 2:
        DST = sys.argv[2]
    sheets = json.load(open(spec_path, encoding="utf-8"))
    wb = openpyxl.load_workbook(SRC)
    before = snapshot(wb)
    n_tables_before = sum(len(ws.tables) for ws in wb.worksheets)
    orig_titles = [ws.title for ws in wb.worksheets]
    for k, spec in enumerate(sheets, 1):
        add_sheet(wb, spec, k)
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    wb.save(DST)

    # 検算: 元シートの値が 1 つも変わっていない・判定欄が未判定のまま
    wb2 = openpyxl.load_workbook(DST)
    after = {k: v for k, v in snapshot(wb2).items() if k[0] in orig_titles}
    diff = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
    scr = wb2["スクリーニング"]
    undecided = all(scr.cell(r, c).value == "未判定" for r in range(5, 39) for c in (4, 5, 6))
    n_tables_after = sum(len(wb2[t].tables) for t in orig_titles)
    print(json.dumps({
        "saved": DST,
        "orig_sheets": len(orig_titles),
        "added_sheets": [s["name"] for s in sheets],
        "orig_cells_changed": len(diff),
        "diff_sample": [list(d) for d in diff[:5]],
        "screening_D5_F38_all_undecided": undecided,
        "orig_tables_before_after": [n_tables_before, n_tables_after],
    }, ensure_ascii=False, indent=1))
    if diff or not undecided or n_tables_before != n_tables_after:
        sys.exit(1)


if __name__ == "__main__":
    main()
