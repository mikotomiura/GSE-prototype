"""共著者の冊の『はじめに』の 2 行を、判断 88 で研究者が決めた文に直す（1 回目の冊の Drive 上の直しに合わせる）。

uv run -q --with openpyxl python -I edit_coauthor_intro.py <make_coauthor_db.py の冊> <直した冊（配る名前）.xlsx>

直すのは 2 セルだけ。ほかのセル・入力規則の数・リンクの数が変わらないことを確かめて件数を出す。
道具の文が変わって、直す行が 1 つずつ見つからなければ止まる。
"""
import sys

from openpyxl import load_workbook

OLD1 = "著者 1 の判定も AI の判定も入っていない。ほかの人と相談せず、1 人で判定する。"
NEW1 = "著者 1 の判定は入っていない。"
OLD2 = "ファイル名を変えずに共有フォルダへ戻す。"
NEW2 = "ファイル名を変えずに、Excel の形（.xlsx）のまま共有フォルダへ戻す。"


def links(wb):
    return [sum(1 for r in wb[s].iter_rows() for c in r if c.hyperlink) for s in wb.sheetnames]


def checks(wb):
    return [len(wb[s].data_validations.dataValidation) for s in wb.sheetnames]


def main(src, out):
    wb = load_workbook(src)
    n1 = n2 = 0
    for row in wb["はじめに"].iter_rows():
        for c in row:
            if c.value == OLD1:
                c.value, n1 = NEW1, n1 + 1
            elif isinstance(c.value, str) and c.value.startswith(OLD2):
                c.value, n2 = NEW2 + c.value[len(OLD2):], n2 + 1
    if (n1, n2) != (1, 1):
        sys.exit(f"the lines to edit were found {n1} and {n2} times (want 1 and 1); not written")
    wb.save(out)
    A, B = load_workbook(src), load_workbook(out)
    cells = sum(1 for s in A.sheetnames for x, y in zip(A[s].iter_rows(), B[s].iter_rows())
                for p, q in zip(x, y) if p.value != q.value)
    print(f"changed cells {cells}; validations {checks(A)} -> {checks(B)}; links {links(A)} -> {links(B)}")
    if cells != 2 or checks(A) != checks(B) or links(A) != links(B):
        sys.exit("more than the 2 lines changed: do not hand this workbook over")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
