"""記入表 1 の原本（git の外）から、問いに載せる行を表示する（判断 3: 記入表の代わりに問いで聞く）。

★ 読むのは原本（`ta_sheet1_original.xlsx`）の記入欄の外のセルだけ。評価版（AI の判定）は開かない。
★ 表示するのは問いの材料（題名・年・掲載誌・DOI・抄録・抄録の出どころ・要点・同じ研究の群・内容の群）。
使い方: PYTHONIOENCODING=utf-8 uv run --with openpyxl python dump_ta_rows.py 追加候補 1 4
        PYTHONIOENCODING=utf-8 uv run --with openpyxl python dump_ta_rows.py 探索の記録 1 4
（範囲は A 列の「順」で、両端を含む）
"""
import sys

import openpyxl

import common as C
import check_ta_sheet as K

COLS = {
    "追加候補": [("順", 0), ("ID", 1), ("題名", 2), ("年", 3), ("掲載誌", 4), ("DOI", 5), ("抄録", 6),
               ("抄録の出どころ", 7), ("要点", 8), ("同じ研究の群", 9), ("内容の群", 10)],
    "探索の記録": [("順", 0), ("ID", 1), ("題名", 2), ("年", 3), ("種別", 4), ("DOI", 5), ("抄録", 6),
                ("抄録の出どころ", 7), ("重なり", 9)],
}
NCOL = {"追加候補": 15, "探索の記録": 14}


def main():
    sheet, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    wb = openpyxl.load_workbook(C.TA_SHEET1_ORIG, read_only=False)
    ws = wb[sheet]
    for r, x in K.body(ws, NCOL[sheet]):
        if not (a <= int(x[0]) <= b):
            continue
        print("=" * 60)
        for name, k in COLS[sheet]:
            v = x[k]
            if name == "DOI" and ws.cell(r, k + 1).hyperlink is not None:
                v = f"{v}  <{ws.cell(r, k + 1).hyperlink.target}>"
            print(f"[{name}] {'' if v is None else v}")


if __name__ == "__main__":
    main()
