"""Make the screening workbooks for author 2, the second human screener (decision 34).

Author 2 screens independently: the workbooks carry no judgement of author 1 or of the AI screener and no
'最終…' columns (differences are decided by both authors together, and recorded by author 1).

    --stage 1   one workbook with the random 20% sample of the additional candidates for the title and abstract
                stage (ceil(0.2 n) records, drawn with SAMPLE_SEED from the sorted record IDs, listed in the
                screening order)
    --stage 2   one workbook per batch of the full-text stage, for the records named in --ids (the records that
                author 1 or the AI screener sent on), with their free full texts copied next to it

The output directory is what is shared with author 2 (a shared folder): the workbook and, at stage 2, fulltext/.
Abstracts and full texts stay outside the repository.

Run (openpyxl via uv):
    uv run --with openpyxl python make_coauthor_db.py --stage 1 --out ~/TRACE-coauthor/stage1
    uv run --with openpyxl python make_coauthor_db.py --stage 2 --batch b01 --ids ids.txt --out ~/TRACE-coauthor/s2-b01
"""

import argparse
import datetime
import math
import os
import random
import shutil

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

import make_trace_db as db

SAMPLE_SHARE = 0.20
SAMPLE_SEED = 20261018  # fixed before registration (decision 34)
WRAP = Alignment(wrap_text=True, vertical="top")
STAGE1_COLS = ["ID", "順", "論文タイトル", "判定", "除外理由", "読んだ範囲", "根拠メモ"]
STAGE2_COLS = ["ID", "順", "論文タイトル", "全文", "ファイル", "判定", "除外理由", "中心", "読んだ範囲", "根拠メモ"]


def stage1_sample(ids):
    """The records author 2 screens at the title and abstract stage: ceil(0.2 n), at least 5 (all if fewer)."""
    ids = sorted(ids)
    k = min(len(ids), max(5, math.ceil(SAMPLE_SHARE * len(ids))))
    return set(random.Random(SAMPLE_SEED).sample(ids, k))


def intro(wb, lines, preview=False):
    if preview:  # before registration nobody screens (GSRR-33): the workbook only shows the work
        lines = [lines[0] + "【見本】", "見本です。登録の後に配り直すまで、判定は始めないでください。"] + lines[1:]
    ws = wb.active
    ws.title = "はじめに"
    for ln in lines:
        ws.append([ln])
    ws.column_dimensions["A"].width = 140
    for row in ws.iter_rows():
        row[0].alignment = WRAP
    ws["A1"].font = Font(bold=True, size=13)


def bib_sheet(wb, recs, meta):
    s = wb.create_sheet("文献DB")
    db.header(s, ["ID", "論文タイトル", "著者", "年", "掲載誌・媒体", "DOI", "リンク", "抄録"], [9, 50, 30, 6, 28, 26, 30, 90])
    for r in recs:
        m = meta.get(r["id"], {})
        doi = str(r.get("doi") or "")
        doi = doi if doi.startswith("10.") else ""
        s.append([r["id"], r["title"], m.get("authors", ""), r.get("year"), r.get("journal"), doi,
                  "https://doi.org/" + doi if doi else "", m.get("abstract", "")])
    for row in s.iter_rows(min_row=2):
        row[1].alignment = WRAP
        row[7].alignment = WRAP


def criteria_sheet(wb):
    cr = wb.create_sheet("判定基準")
    db.header(cr, ["項目", "内容"], [22, 120])
    for k, v in db.CRITERIA:
        cr.append([k, v])
    for row in cr.iter_rows(min_row=2):
        row[1].alignment = WRAP


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=[1, 2], required=True)
    ap.add_argument("--batch", help="stage 2: the batch ID, as c_screening.py names it")
    ap.add_argument("--ids", help="stage 2: a file with the record IDs of the batch, one per line")
    ap.add_argument("--data", default="~/Documents/TRACE/data")
    ap.add_argument("--fulltext", default="~/Documents/TRACE/fulltext")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", action="store_true", help="mark the workbook as a preview (before registration)")
    a = ap.parse_args(argv)
    data, ftdir, out = (os.path.expanduser(x) for x in (a.data, a.fulltext, a.out))
    recs = sorted(db.load(os.path.join(data, "records264.json")), key=lambda r: r["order"])
    meta = db.load(os.path.join(data, "meta.json"), {})
    chrome = db.load(os.path.join(data, "chrome_status.json"), {})
    if os.path.exists(out) and os.listdir(out):
        raise SystemExit(f"{out} is not empty; author 2 may have filled a workbook there")
    os.makedirs(out, exist_ok=True)
    today = datetime.date.today().isoformat()
    wb = Workbook()
    if a.stage == 1:
        pick = stage1_sample([r["id"] for r in recs])
        rows = [r for r in recs if r["id"] in pick]
        intro(wb, [
            "TRACE｜選別の 2 人目（題名・抄録の段・無作為の 2 割）",
            f"作成 {today}。追加候補 {len(recs)} 件のうち無作為に選んだ {len(rows)} 件（seed {SAMPLE_SEED}）。",
            "『段1』の青い欄に記入する。抄録は『文献DB』にある（取れなかった件は題名だけで判定し、読んだ範囲を「題名のみ」にする）。基準は『判定基準』。",
            "題名と抄録だけで判定する。全文やウェブのページは開かない。迷ったら含める（全文の段へ回す）。除外なら除外理由を 1 つ選ぶ。",
            "このファイルには、著者 1 の判定も AI の判定も入っていない。ほかの人と相談せず、1 人で判定する。",
            "記入が終わったら、ファイル名を変えずに共有フォルダへ戻す。著者 1 がそのまま記録する。食い違いは、その後で一緒に決める。",
        ], a.preview)
        ws = wb.create_sheet("段1")
        db.header(ws, STAGE1_COLS, [9, 5, 60, 12, 12, 12, 40])
        for r in rows:
            ws.append([r["id"], r["order"] + 1, r["title"], "未判定", "", "", ""])
        db.fill_inputs(ws, STAGE1_COLS, [("判定", "未判定,含める,除外"), ("除外理由", db.CODE_CHOICES),
                                         ("読んだ範囲", "題名のみ,抄録")])
        name = "TRACE_共著者_段1" + ("_見本" if a.preview else "") + ".xlsx"
    else:
        if not (a.batch and a.ids):
            raise SystemExit("--stage 2 needs --batch and --ids")
        with open(os.path.expanduser(a.ids), encoding="utf-8") as f:
            want = [ln.strip() for ln in f if ln.strip()]
        byid = {r["id"]: r for r in recs}
        missing = [i for i in want if i not in byid]
        if missing:
            raise SystemExit(f"not among the candidates: {missing}")
        rows = sorted((byid[i] for i in want), key=lambda r: r["order"])
        os.makedirs(os.path.join(out, "fulltext"))
        n_ft = 0
        for r in rows:
            fn = db.fulltext_file(r["id"], ftdir)
            if fn:
                shutil.copyfile(os.path.join(ftdir, fn), os.path.join(out, "fulltext", fn))
                if fn.endswith(".xml") and os.path.exists(os.path.join(ftdir, r["id"] + ".txt")):
                    shutil.copyfile(os.path.join(ftdir, r["id"] + ".txt"), os.path.join(out, "fulltext", r["id"] + ".txt"))
                n_ft += 1
        intro(wb, [
            f"TRACE｜選別の 2 人目（全文の段と中心の段・束 {a.batch}）",
            f"作成 {today}。{len(rows)} 件（全文あり {n_ft} 件）。全文は同じフォルダの fulltext/ にある（<ID>.pdf・.html・.xml。.xml と同じ名前の .txt は本文を機械で抜き出したもの）。",
            "『段2・3』の青い欄に記入する。基準は『判定基準』。全文が無い記録は、保留＋E6 にする。",
            "含めるときは、同じときに中心（中心-A・中心-B・境界（保留））も付ける。規則だけで決まらなければ保留にする。",
            "このファイルには、著者 1 の判定も AI の判定も入っていない。ほかの人と相談せず、1 人で判定する。",
            "記入が終わったら、ファイル名を変えずに共有フォルダへ戻す。著者 1 がそのまま記録する。食い違いは、その後で一緒に全文を見て決める。",
        ], a.preview)
        ws = wb.create_sheet("段2・3")
        db.header(ws, STAGE2_COLS, [9, 5, 60, 18, 14, 10, 12, 14, 12, 40])
        for r in rows:
            st = db.fulltext_status(r["id"], meta, chrome, ftdir)[0]
            ws.append([r["id"], r["order"] + 1, r["title"], st, db.fulltext_file(r["id"], ftdir), "未判定", "",
                       "未判定", "", ""])
        db.fill_inputs(ws, STAGE2_COLS, [("判定", db.STAGE_CHOICES), ("除外理由", db.CODE_CHOICES),
                                         ("中心", db.CENTRE_CHOICES), ("読んだ範囲", db.READ_CHOICES)])
        name = f"TRACE_共著者_段2_{a.batch}.xlsx"
    bib_sheet(wb, rows, meta)
    criteria_sheet(wb)
    wb.save(os.path.join(out, name))
    print(f"wrote {os.path.join(out, name)}: {len(rows)} records")


if __name__ == "__main__":
    main()
