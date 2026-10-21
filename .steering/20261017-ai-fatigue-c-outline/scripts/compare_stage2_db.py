"""段 2・3 の判定の後: 判定前の控えからの違いが『段2・3』の判定の欄（束の行）だけかを照らす。

uv run -q --with openpyxl python -I compare_stage2_db.py <控え.xlsx> <今の DB.xlsx> <段2の束.txt>
値は出さず、違いのあるシート・列・件数と、束の記録の判定の数だけを出す。
"""
import collections
import re
import sys

import openpyxl

ALLOWED = {"判定", "除外理由", "中心", "読んだ範囲", "根拠メモ"}


def load(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        out[ws.title] = rows
    return out


def main(base, now, batches):
    ids = set(re.findall(r"\b(?:S\d\d-\d\d|CS\d{5}|R\d+|X\d+)\b", open(batches, encoding="utf-8").read()))
    a, b = load(base), load(now)
    bad = 0
    if set(a) != set(b):
        print("sheets differ:", sorted(set(a) ^ set(b)))
        bad += 1
    for name in sorted(set(a) & set(b)):
        ra, rb = a[name], b[name]
        if len(ra) != len(rb) or (ra and ra[0] != rb[0]):
            print(f"{name}: shape or header differs ({len(ra)} vs {len(rb)} rows)")
            bad += 1
            continue
        head = [str(c) if c is not None else "" for c in ra[0]]
        diffs = collections.Counter()
        for x, y in zip(ra[1:], rb[1:]):
            rid = str(x[0]) if x and x[0] is not None else ""
            for col, u, v in zip(head, x, y):
                if u != v:
                    ok = name == "段2・3" and col in ALLOWED and rid in ids
                    diffs[(col, "ok" if ok else "NOT ALLOWED")] += 1
                    if not ok:
                        bad += 1
        for (col, tag), n in sorted(diffs.items()):
            print(f"{name}\t{col}\t{n}\t{tag}")
    s2 = b["段2・3"]
    head = [str(c) if c is not None else "" for c in s2[0]]
    c = collections.Counter()
    for r in s2[1:]:
        d = dict(zip(head, r))
        if str(d.get("ID")) in ids:
            c[(d.get("判定"), d.get("除外理由") or "")] += 1
    print("batch records by decision:", dict(sorted(c.items(), key=str)))
    print("NOT ALLOWED differences:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
