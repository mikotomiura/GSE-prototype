"""共著者の冊が Google スプレッドシートを通って戻り、判定のシートの ID の列がリンクの内部表記
（#gid=…&range=A2）に置き換わったときに、写しの A 列だけをリンク先の『文献DB』の ID で書き戻す（判断 88）。

uv run -q --with openpyxl python -I restore_coauthor_ids.py <戻った冊の写し> <書き戻した冊.xlsx> <作り直した冊.xlsx>

<作り直した冊> は make_coauthor_db.py で同じ --stage / --ids から一時の場所に作った冊（名前の照合に使う）。
判定の値は出さず、件数だけを出す。次のどれかが崩れたら書き戻した冊を作らずに止まる:
- 判定のシートの ID の列のすべてが #gid= の形で、リンク先が『文献DB』の A 列であること
- 書き戻した ID が一意で、作り直した冊の ID と順まで一致し、題名も一致すること
- 書き戻した冊が、A 列以外の全シート・全セルで戻った冊と同じであること
"""
import re
import sys

from openpyxl import load_workbook

JUDGE = ("段1", "段2・3")


def judge_sheet(wb):
    names = [n for n in JUDGE if n in wb.sheetnames]
    if len(names) != 1:
        sys.exit(f"the judgement sheet is not one of {JUDGE}: {wb.sheetnames}")
    return names[0]


def main(src, out, ref):
    wb = load_workbook(src)
    name = judge_sheet(wb)
    ws = wb[name]
    head = [c.value for c in ws[1]]
    ti = head.index("論文タイトル")
    db = {r[0].row: r[0].value for r in wb["文献DB"].iter_rows(min_row=2)}
    ids = []
    for row in ws.iter_rows(min_row=2):
        a = row[0]
        if a.value is None:
            continue
        loc = a.hyperlink.location if a.hyperlink else ""
        m = re.fullmatch(r"'文献DB'!A(\d+)", loc or "")
        if not str(a.value).startswith("#gid=") or not m:
            sys.exit(f"{a.coordinate}: not the shape this script repairs; stop and ask the researcher")
        a.value = db[int(m.group(1))]
        ids.append((a.value, row[ti].value))
    R = load_workbook(ref)
    want = [(r[0], r[ti]) for r in R[judge_sheet(R)].iter_rows(min_row=2, values_only=True) if r[0]]
    if len({i for i, _ in ids}) != len(ids) or ids != want:
        sys.exit("the restored IDs do not match the remade workbook (ID, order or title); not written")
    wb.save(out)
    A, B = load_workbook(src, data_only=True), load_workbook(out, data_only=True)
    other = changed = 0
    for s in A.sheetnames:
        ra, rb = list(A[s].iter_rows()), list(B[s].iter_rows())
        if len(ra) != len(rb):
            sys.exit(f"{s}: row count differs after saving")
        for x, y in zip(ra, rb):
            for p, q in zip(x, y):
                if s == name and p.column == 1 and p.row >= 2:
                    changed += p.value != q.value
                elif p.value != q.value:
                    other += 1
    print(f"{name}: restored {len(ids)} IDs (equal to the remade workbook in order); "
          f"cells differing outside column A: {other}; column A changed: {changed}")
    if other:
        sys.exit("cells outside column A differ: do not import the written copy")


if __name__ == "__main__":
    main(*sys.argv[1:4])
