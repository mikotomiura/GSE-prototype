"""Claude 再評価シートを元ワークブックに追加して別名保存し、元シート不変を検算する。

入力: claude_eval.json（シート定義: name / title / subtitle / headers / widths / rows / table）
出力: archive/AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx（build_xlsx.py の第 2 引数で変更可）
"""
import json
import sys
import tempfile

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


# 比較する属性（Codex 2 巡目: stopIfTrue・カラースケール等・入力規則のエラー表示も含める）
DV_ATTRS = ("sqref", "type", "operator", "formula1", "formula2", "allow_blank", "showErrorMessage", "showInputMessage",
            "errorStyle", "error", "errorTitle", "prompt", "promptTitle", "showDropDown", "imeMode")
CF_ATTRS = ("type", "operator", "formula", "priority", "stopIfTrue", "text", "timePeriod", "rank", "percent", "bottom",
            "aboveAverage", "equalAverage", "stdDev", "colorScale", "dataBar", "iconSet")


def dxf_content(wb, dxf_id):
    """条件付き書式が指す差分書式の中身。★ openpyxl は保存時に差分書式の一覧を詰め直すので、dxfId の番号ではなく中身で比べる。"""
    if dxf_id is None:
        return None
    d = wb._differential_styles.dxf[dxf_id]
    return tuple(repr(getattr(d, a)) for a in ("font", "fill", "border", "numFmt", "alignment", "protection"))


def structure(wb, titles=None):
    """元シートの構成を内容レベルで写す（openpyxl の再保存で失われる・変わるもの）。
    入力規則（範囲・種類・式）、条件付き書式（範囲とルールの中身）、結合セル、テーブル（名前・範囲・スタイル）、定義名（名前と値）。"""
    titles = titles or [ws.title for ws in wb.worksheets]
    out = {}
    for t in titles:
        ws = wb[t]
        dv = sorted(tuple(str(getattr(d, a)) for a in DV_ATTRS) for d in ws.data_validations.dataValidation)
        cf = sorted((str(rng.sqref), tuple(sorted(tuple(str(getattr(r, a)) for a in CF_ATTRS) + (str(dxf_content(wb, r.dxfId)),) for r in rules)))
                    for rng, rules in ws.conditional_formatting._cf_rules.items())
        merged = sorted(str(m) for m in ws.merged_cells.ranges)
        tables = sorted((tb.name, tb.ref, tb.tableStyleInfo.name if tb.tableStyleInfo else None) for tb in ws.tables.values())
        names = sorted((n, d.attr_text) for n, d in ws.defined_names.items())
        out[t] = (dv, cf, merged, tables, names)
    out["__defined_names__"] = sorted((n, d.attr_text) for n, d in wb.defined_names.items())
    return out


def same_file(a, b):
    """別表記・大文字小文字違い・リンク経由でも同じファイルかを判定する（Codex 指摘）。"""
    if os.path.exists(a) and os.path.exists(b):
        return os.path.samefile(a, b)
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


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
            # 数式は spec の formula_cols（1 始まりの列番号）のセルだけに許す。題名など他の列が '=' で始まっても文字列として保存する
            if isinstance(v, str) and v.startswith("=") and j not in spec.get("formula_cols", ()):
                c.data_type = "s"
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
    if same_file(DST, SRC):
        sys.exit("出力先が入力 xlsx と同じパスです（入力のスナップショットを上書きしない）")
    sheets = json.load(open(spec_path, encoding="utf-8"))
    wb = openpyxl.load_workbook(SRC)
    before = snapshot(wb)
    struct_before = structure(wb)
    orig_titles = [ws.title for ws in wb.worksheets]
    for k, spec in enumerate(sheets, 1):
        add_sheet(wb, spec, k)
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    # 一時ファイルに保存して検算し、通ったときだけ出力先を置き換える（失敗時に既存の正常版を失わない）。
    # ★ mkstemp で排他的に一意に作る（既存のリンクや並行実行の一時ファイルを踏まない）。openpyxl は拡張子 .xlsx を要求する
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".xlsx", dir=os.path.dirname(os.path.abspath(DST)))
    os.close(fd)
    try:
        ok = save_and_verify(wb, tmp, before, struct_before, orig_titles, sheets)
        if not ok:
            sys.exit("検算に失敗したので出力先を置き換えなかった")
        os.replace(tmp, DST)
        print("saved:", DST)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def save_and_verify(wb, tmp, before, struct_before, orig_titles, sheets):
    wb.save(tmp)

    # 検算: 元シートの値が 1 つも変わっていない・判定欄が未判定のまま・構成が内容レベルで同じ
    wb2 = openpyxl.load_workbook(tmp)
    after = {k: v for k, v in snapshot(wb2).items() if k[0] in orig_titles}
    diff = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
    scr = wb2["スクリーニング"]
    undecided = all(scr.cell(r, c).value == "未判定" for r in range(5, 39) for c in (4, 5, 6))
    struct_after = structure(wb2, orig_titles)
    print(json.dumps({
        "target": DST,
        "orig_sheets": len(orig_titles),
        "added_sheets": [s["name"] for s in sheets],
        "orig_cells_changed": len(diff),
        "diff_sample": [list(d) for d in diff[:5]],
        "screening_D5_F38_all_undecided": undecided,
        "orig_structure_same": struct_before == struct_after,
    }, ensure_ascii=False, indent=1))
    wb2.close()
    return not diff and undecided and struct_before == struct_after


if __name__ == "__main__":
    main()
