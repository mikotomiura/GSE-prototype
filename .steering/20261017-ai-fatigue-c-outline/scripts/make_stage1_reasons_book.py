"""Make the workbook in which author 1 proposes the final exclusion code of the stage-1 records both humans
excluded with different codes, and author 2 answers whether the proposed code is right (decision 90).

The records are the ones c_screening.py export-final --stage 1 names ("both exclude with different codes"). The
tool names only the first record of a batch, so its own decision function is called on every batch with a wrapper
that collects the named records and writes nothing. A batch that stops for any other reason stops this script.

Each row carries both humans' codes, read range and notes (author 1's from the database, author 2's from the
returned workbook the tool imported), an input column for author 1's proposal and its reason, and input columns
for author 2's answer. The agreed code is written by author 1 in the database's '段1' '最終の除外理由' afterwards.

Run from ~/TRACE/scripts (openpyxl via uv):
    uv run -q --with openpyxl python -I <this file> --out <new directory> --sample-book <id-restored sample .xlsx> \
        --net1-book <returned net1 .xlsx>
"""

import argparse
import os
import sys

sys.path.insert(0, os.getcwd())   # ~/TRACE/scripts: c_screening, make_trace_db, trace_style

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill

import c_screening as c
import make_trace_db as db
import trace_style as st

STAGE1_CODES = "E1,E2,E3,E4,E7"
ANSWERS = "この理由でよい,別の理由がよい"
CO_FILL = PatternFill("solid", fgColor="FEF6E4")   # author 2's input columns, apart from author 1's blue
COLS = ["ID", "束", "論文タイトル", "題名（日本語・機械訳）", "2 人の理由", "著者 1 の理由", "著者 1 の読んだ範囲",
        "著者 1 の根拠メモ", "共著者の理由", "共著者の読んだ範囲", "共著者の根拠メモ", "提案する理由", "提案の根拠",
        "共著者の返答", "共著者のコメント"]
A1_INPUTS = {"提案する理由", "提案の根拠"}
A2_INPUTS = {"共著者の返答", "共著者のコメント"}


def named_records():
    """(batch, record ID, author 1's code, author 2's code) of every record export-final --stage 1 would name."""
    out, orig = [], c.final_stage1_two

    def wrap(a, rid, A1, ai, C, *rest):
        try:
            return orig(a, rid, A1, ai, C, *rest)
        except c.Stop as e:
            if "both exclude with different codes" not in str(e):
                raise
            out.append((a.batch, rid, A1[1], C[1]))
            return {"final": "exclude", "code": "", "decided_by": "named"}

    c.final_stage1_two, c.write_csv = wrap, (lambda *x, **k: None)
    # nothing is written, so the tool's "wrote …; commit it" would mislead; its STOPPED lines are kept
    c.print = lambda *x, **k: str(x[0]).startswith("STOPPED") and print(*x, **k)
    done = {r["batch"] for r in c.read_csv(c.DEFAULTS["state"] / "batches.csv") if r["stage"] == "1"
            and (c.DEFAULTS["state"] / "s1" / f"{r['batch']}.final.csv").exists()}
    batches = sorted({r["batch"] for r in c.read_csv(c.DEFAULTS["state"] / "batches.csv") if r["stage"] == "1"} - done)
    for b in batches:
        if c.main(["export-final", "--stage", "1", "--batch", b]):
            raise SystemExit(f"{b}: export-final stopped for another reason (see above)")
    return out


def sheet_by_id(path, sheet):
    ws = openpyxl.load_workbook(path, read_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True))
    head = list(rows[0])
    return {r[0]: dict(zip(head, r)) for r in rows[1:] if r[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample-book", required=True, help="author 2's 20%% sample workbook as imported (id-restored)")
    ap.add_argument("--net1-book", required=True, help="author 2's net1 workbook as returned")
    ap.add_argument("--data", default="~/Documents/TRACE/data")
    a = ap.parse_args()
    out, data = os.path.expanduser(a.out), os.path.expanduser(a.data)
    if os.path.exists(out) and os.listdir(out):
        raise SystemExit(f"{out} is not empty")
    named = named_records()
    a1 = sheet_by_id(c.DEFAULTS["xlsx"], "段1")
    co = {**sheet_by_id(os.path.expanduser(a.sample_book), "段1"), **sheet_by_id(os.path.expanduser(a.net1_book), "段1")}
    co_csv = {}
    for book in ("sample", "net1"):   # net1 last: the tool reads the latest imported workbook
        for r in c.read_csv(c.DEFAULTS["state"] / "coauthor" / f"{book}.csv"):
            if r["stage"] == "1":
                co_csv[r["record_id"]] = (book, r)
    recs = {r["id"]: r for r in db.load_records(data)}
    meta = db.load(os.path.join(data, "meta.json"), {})
    ja = db.load(os.path.join(data, "ja.json"), {})
    body, bad = [], []
    for b, rid, c1, c2 in named:
        x, (book, y) = a1[rid], co_csv[rid]
        cy = co[rid] if book == "net1" else sheet_by_id(os.path.expanduser(a.sample_book), "段1")[rid]
        if (x["除外理由"] or "") != c1 or y["code"] != c2 or (cy["除外理由"] or "") != c2:
            bad.append(rid)
        r = recs[rid]
        body.append([rid, b, r["title"], (ja.get(rid) or {}).get("title_ja", ""), f"{c1} / {c2}", c1,
                     x["読んだ範囲"] or "", x["根拠メモ"] or "", c2, cy["読んだ範囲"] or "", cy["根拠メモ"] or "",
                     "", "", "", ""])
    if bad:
        raise SystemExit(f"the codes in the database or the workbooks differ from the committed ones: {bad}")
    body.sort(key=lambda v: (v[4], v[1], v[0]))   # the same pair of codes together, then batch
    wb = Workbook()
    st.intro(wb.active, "TRACE｜題名・抄録の段で除外理由が分かれた記録", f"{len(body)} 件", [
        ("このファイルについて", [
            "題名・抄録の段で、2 人とも除外にしたが、除外理由が分かれた記録の一覧。",
            "著者 1 が、記録ごとに最終の除外理由の案を『提案する理由』に、その根拠を『提案の根拠』に書いた（青い欄）。",
            "ID を押すと『文献DB』のその記録の抄録（英語と日本語）へ飛ぶ。基準は『判定基準』。",
        ]),
        ("お願いしたいこと", [
            "『共著者の返答』（黄色い欄）で、提案した理由でよいかを選ぶ。",
            "「別の理由がよい」のときは、『共著者のコメント』に、よいと思う理由とその訳を書く。",
        ]),
        ("日本語訳について", ["題名と抄録の日本語は Claude による機械訳で、読む助けにすぎない。判定の根拠は英語の原文とする。"]),
        ("終わったら", ["ファイル名を変えずに、Excel の形（.xlsx）のまま戻す。"]),
    ])
    ws = wb.create_sheet("除外理由")
    bib_row = {v[0]: i + 2 for i, v in enumerate(body)}
    widths = [10, 5, 40, 32, 9, 8, 10, 30, 8, 10, 30, 10, 34, 14, 34]
    st.table(ws, COLS, widths, body, inputs=A1_INPUTS | A2_INPUTS,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "著者 1 の根拠メモ", "共著者の根拠メモ", "提案の根拠", "共著者のコメント"},
             links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0])}, tab="2563EB",
             height=lambda v: st.text_height((v[2], 40), (v[3], 32), (v[7], 30), (v[10], 30)))
    for name in A2_INPUTS:
        col = COLS.index(name) + 1
        for r in range(2, ws.max_row + 1):
            ws.cell(row=r, column=col).fill = CO_FILL
    st.choices(ws, COLS, [("提案する理由", STAGE1_CODES), ("共著者の返答", ANSWERS)])
    bib = wb.create_sheet("文献DB")
    brows = []
    for v in body:
        r, m = recs[v[0]], meta.get(v[0], {})
        doi = str(r.get("doi") or "")
        doi = doi if doi.startswith("10.") else ""
        brows.append([v[0], r["title"], v[3], (m.get("abstract") or "").strip() or "（抄録なし: どの出どころにも見つからなかった）",
                      (ja.get(v[0]) or {}).get("abstract_ja", ""), m.get("authors", ""), r.get("year"), r.get("journal"), doi])
    st.table(bib, ["ID", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体",
                   "DOI"], [10, 36, 30, 70, 60, 24, 6, 22, 24], brows,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体"},
             links={"DOI": lambda v: ("https://doi.org/" + v[8], v[8]) if v[8] else None}, tab="64748B",
             height=lambda v: st.text_height((v[1], 36), (v[2], 30), (v[3], 70), (v[4], 60)))
    cr = wb.create_sheet("判定基準")
    st.table(cr, ["項目", "内容"], [22, 120], [list(x) for x in db.CRITERIA], wrap={"内容"}, tab="64748B",
             height=lambda v: st.text_height((v[1], 120)))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "TRACE_co-author_stage1_reasons.xlsx")
    wb.save(path)
    print(f"wrote {path}: {len(body)} records")


if __name__ == "__main__":
    main()
