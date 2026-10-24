"""Write author 1's re-check (as the tool reads it) into the database's '段1' and '段2・3' (判定・除外理由・中心・読んだ範囲・根拠メモ)."""
import os, sys, csv, hashlib
sys.path.insert(0, os.path.expanduser("~/TRACE/scripts"))
import c_screening as cs
from types import SimpleNamespace
from pathlib import Path
from openpyxl import load_workbook
src, out = sys.argv[1], sys.argv[2]
a = SimpleNamespace(**{k: Path(os.path.expanduser(v)) for k, v in cs.DEFAULTS.items()})
cs.mode(a)
INV_D = {"include": "含める", "exclude": "除外", "pending": "保留"}
INV_C = {"A": "中心-A", "B": "中心-B", "boundary": "境界（保留）", "": "未判定"}
INV_R = {"title only": "題名のみ", "abstract": "抄録", "part of full text": "全文の一部", "full text": "全文", "": None}
R = os.path.expanduser("~/Documents/TRACE/author1-review-20261024/")
BOOK = {1: (R + "TRACE_author1_exclusion_review.研究者の見直し-20261024-1618.xlsx", "段1の見直し"),
        2: (R + "TRACE_author1_exclusion_review.研究者の中心-20261024-1925.xlsx", "段2の見直し")}
rec = list(csv.DictReader(open(a.state / "revisions.csv")))
wb = load_workbook(src)
total = 0
for st, (book, sheet) in BOOK.items():
    sha = hashlib.sha256(open(book, "rb").read()).hexdigest()
    assert {r["xlsx_sha256"] for r in rec if r["stage"] == str(st)} == {sha}, (st, sha)
    rb = load_workbook(book, read_only=True, data_only=True)[sheet]
    rows = list(rb.iter_rows(values_only=True)); h = rows[0]
    memo = {r[0]: r[h.index("見直しの根拠メモ")] for r in rows[1:] if r[0]}
    changed = set()
    for p in sorted((a.state / f"s{st}").glob("*.author1-revised.csv")):
        changed |= {r["record_id"] for r in csv.DictReader(open(p))}
    A = cs.author1_rows(a, st)
    ws = wb["段1" if st == 1 else "段2・3"]; hd = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        i = row[0].value
        if i not in changed: continue
        b, rr = A[i]
        dec, code = cs.value(rr, st)
        srow = [r for r in rr if r["stage"] == str(st)][0]
        row[hd.index("判定")].value = INV_D[dec]
        row[hd.index("除外理由")].value = code or None
        row[hd.index("読んだ範囲")].value = INV_R[srow["read"]]
        assert memo.get(i), i
        row[hd.index("根拠メモ")].value = "（見直し）" + str(memo[i]).strip()
        if st == 2:
            c3 = cs.value(rr, 3)
            row[hd.index("中心")].value = INV_C[c3[0]] if (dec == "include" and c3) else "未判定"
        total += 1
    print("stage", st, "rows written", len(changed))
wb.save(out); print("saved", out, total)
