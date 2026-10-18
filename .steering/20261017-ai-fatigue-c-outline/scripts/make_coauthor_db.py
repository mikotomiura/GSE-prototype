"""Make the screening workbooks for author 2, the second human screener (decisions 34 and 35).

Author 2 screens independently: the workbooks carry no judgement of author 1 or of the AI screener and no
'最終…' columns (differences are decided by both authors together, and recorded by author 1).

    --stage 1   one workbook with the random 20% sample of the additional candidates for the title and abstract
                stage (ceil(0.2 n) records, drawn with SAMPLE_SEED from the sorted record IDs, listed in the
                screening order)
    --stage 2   one workbook per batch of the full-text stage, for the records named in --ids (the records that
                author 1 or the AI screener sent on). The full texts are linked to the shared Google Drive folder
                (data/drive_links.json); without a link, the file is copied to fulltext/ next to the workbook.

Abstracts and full texts stay outside the repository. Titles and abstracts in Japanese are machine translations
(data/ja.json), shown next to the English, which is the basis of the judgement.

Run (openpyxl via uv):
    uv run --with openpyxl python make_coauthor_db.py --stage 1 --out ~/TRACE-coauthor/stage1 [--preview]
    uv run --with openpyxl python make_coauthor_db.py --stage 2 --batch b01 --ids ids.txt --out ~/TRACE-coauthor/s2-b01
"""

import argparse
import datetime
import math
import os
import random
import shutil
import sys

from openpyxl import Workbook

import make_trace_db as db
import trace_style as st

SAMPLE_SHARE = 0.20
SAMPLE_SEED = 20261018  # fixed before registration (decision 34)
STAGE1_COLS = ["ID", "順", "論文タイトル", "題名（日本語・機械訳）", "判定", "除外理由", "読んだ範囲", "根拠メモ"]
STAGE2_COLS = ["ID", "順", "論文タイトル", "題名（日本語・機械訳）", "全文", "ファイル", "判定", "除外理由", "中心", "読んだ範囲",
               "根拠メモ"]


def stage1_sample(ids):
    """The records author 2 screens at the title and abstract stage: ceil(0.2 n), at least 5 (all if fewer)."""
    ids = sorted(ids)
    k = min(len(ids), max(5, math.ceil(SAMPLE_SHARE * len(ids))))
    return set(random.Random(SAMPLE_SEED).sample(ids, k))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, choices=[1, 2], required=True)
    ap.add_argument("--batch", help="stage 2: the batch ID, as c_screening.py names it")
    ap.add_argument("--ids", help="stage 2: a file with the record IDs of the batch, one per line")
    ap.add_argument("--data", default="~/Documents/TRACE/data")
    ap.add_argument("--fulltext", default="~/Documents/TRACE/fulltext")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", action="store_true", help="mark the workbook as a preview (before registration)")
    ap.add_argument("--hold", action="store_true",
                    help="the real workbook, made in advance: it says not to start until the researcher reports "
                         "that the protocol is registered (GSRR-33)")
    a = ap.parse_args(argv)
    if a.preview and a.hold:
        ap.error("--preview and --hold exclude each other")
    data, ftdir, out = (os.path.expanduser(x) for x in (a.data, a.fulltext, a.out))
    recs = sorted(db.load(os.path.join(data, "records264.json")), key=lambda r: r["order"])
    meta = db.load(os.path.join(data, "meta.json"), {})
    chrome = db.load(os.path.join(data, "chrome_status.json"), {})
    ja = db.load(os.path.join(data, "ja.json"), {})
    drive = db.load(os.path.join(data, "drive_links.json"), {})
    if os.path.exists(out) and os.listdir(out):
        raise SystemExit(f"{out} is not empty; author 2 may have filled a workbook there")
    os.makedirs(out, exist_ok=True)
    today = datetime.date.today().isoformat()
    wb = Workbook()

    def jt(r):
        return (ja.get(r["id"]) or {}).get("title_ja", "")

    common = [
        ("このファイルに入っていないもの", ["著者 1 の判定も AI の判定も入っていない。ほかの人と相談せず、1 人で判定する。"]),
        ("日本語訳について", ["題名と抄録の日本語は Claude による機械訳で、読む助けにすぎない。判定の根拠は英語の原文とする。"]),
        ("終わったら", ["ファイル名を変えずに共有フォルダへ戻す。著者 1 がそのまま記録する。食い違いは、その後で一緒に決める。"]),
    ]
    if a.preview:  # before registration nobody screens (GSRR-33): the workbook only shows the work
        common = [("見本", ["見本です。登録の後に配り直すまで、判定は始めないでください。"])] + common
    elif a.hold:   # the real workbook, handed over before registration: screening starts only after it
        common = [("始める日", ["研究者から「登録が済んだ」と連絡があるまで、判定は始めないでください（登録の前には誰も判定しない決まりです）。"
                               "このファイルは、その連絡の後にそのまま使います。"])] + common
    if a.stage == 1:
        pick = stage1_sample([r["id"] for r in recs])
        rows = [r for r in recs if r["id"] in pick]
        st.intro(wb.active, "TRACE｜選別の 2 人目（題名・抄録の段）" + ("【見本】" if a.preview else ""),
                 f"作成 {today}・追加候補 {len(recs)} 件のうち無作為に選んだ {len(rows)} 件（seed {SAMPLE_SEED}）", [
                     ("進め方", [
                         "『段1』の青い欄に記入する。ID を押すと『文献DB』のその記録の抄録（英語と日本語）へ飛ぶ。基準は『判定基準』。",
                         "題名と抄録だけで判定する。全文やウェブのページは開かない。抄録が取れなかった件は題名だけで判定し、読んだ範囲を「題名のみ」にする。",
                         "迷ったら含める（全文の段へ回す）。除外なら除外理由を 1 つ選ぶ。",
                     ])] + common)
        cols, name = STAGE1_COLS, "TRACE_共著者_段1" + ("_見本" if a.preview else "") + ".xlsx"
        body = [[r["id"], r["order"] + 1, r["title"], jt(r), "未判定", "", "", ""] for r in rows]
        spec = [("判定", "未判定,含める,除外"), ("除外理由", db.CODE_CHOICES), ("読んだ範囲", "題名のみ,抄録")]
        inputs, widths, tab = {"判定", "除外理由", "読んだ範囲", "根拠メモ"}, [10, 5, 52, 40, 11, 10, 11, 34], "2563EB"
        sheet = "段1"
    else:
        if not (a.batch and a.ids):
            raise SystemExit("--stage 2 needs --batch and --ids")
        with open(os.path.expanduser(a.ids), encoding="utf-8") as f:
            want = [ln.strip() for ln in f if ln.strip()]
        cov = [i for i in want if i.startswith("CS")]
        if cov:   # the coverage sample is screened by author 1 and the AI screener only (decision 38)
            print(f"left out {len(cov)} records of the coverage sample: {cov[:5]}", file=sys.stderr)
            want = [i for i in want if not i.startswith("CS")]
        byid = {r["id"]: r for r in recs}
        missing = [i for i in want if i not in byid]
        if missing:
            raise SystemExit(f"not among the candidates: {missing}")
        rows = sorted((byid[i] for i in want), key=lambda r: r["order"])
        n_ft = 0
        for r in rows:
            fn = db.fulltext_file(r["id"], ftdir)
            if not fn:
                continue
            n_ft += 1
            if not db.drive_link(fn, drive):  # no shared link yet: hand the file over in the folder
                os.makedirs(os.path.join(out, "fulltext"), exist_ok=True)
                shutil.copyfile(os.path.join(ftdir, fn), os.path.join(out, "fulltext", fn))
                if fn.endswith(".xml") and os.path.exists(os.path.join(ftdir, r["id"] + ".txt")):
                    shutil.copyfile(os.path.join(ftdir, r["id"] + ".txt"), os.path.join(out, "fulltext", r["id"] + ".txt"))
        st.intro(wb.active, f"TRACE｜選別の 2 人目（全文の段と中心の段・束 {a.batch}）" + ("【見本】" if a.preview else ""),
                 f"作成 {today}・{len(rows)} 件（全文あり {n_ft} 件）", [
                     ("進め方", [
                         "『段2・3』の青い欄に記入する。全文は「ファイル」のリンク（Google Drive）から開く。リンクの無いものは同じフォルダの fulltext/ にある。",
                         "全文が無い記録は、保留＋E6 にする。含めるときは、同じときに中心（中心-A・中心-B・境界（保留））も付ける。規則だけで決まらなければ保留にする。",
                     ])] + common)
        cols, name = STAGE2_COLS, f"TRACE_共著者_段2_{a.batch}.xlsx"
        body = [[r["id"], r["order"] + 1, r["title"], jt(r), db.fulltext_status(r["id"], meta, chrome, ftdir)[0],
                 db.fulltext_file(r["id"], ftdir), "未判定", "", "未判定", "", ""] for r in rows]
        spec = [("判定", db.STAGE_CHOICES), ("除外理由", db.CODE_CHOICES), ("中心", db.CENTRE_CHOICES),
                ("読んだ範囲", db.READ_CHOICES)]
        inputs, widths, tab = {"判定", "除外理由", "中心", "読んだ範囲", "根拠メモ"}, [10, 5, 46, 34, 14, 14, 11, 10, 13, 11, 30], "0D9488"
        sheet = "段2・3"
    bib_row = {r["id"]: i + 2 for i, r in enumerate(rows)}
    ws = wb.create_sheet(sheet)
    links = {"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0])}
    if a.stage == 2:
        links["ファイル"] = lambda v: db.drive_link(v[5], drive) if v[5] else None
    st.table(ws, cols, widths, body, inputs=inputs, wrap={"論文タイトル", "題名（日本語・機械訳）", "根拠メモ"}, links=links,
             tab=tab, height=lambda v: st.text_height((v[2], 50), (v[3], 38)))
    st.choices(ws, cols, spec)
    bib = wb.create_sheet("文献DB")
    brows = []
    for r in rows:
        m = meta.get(r["id"], {})
        doi = str(r.get("doi") or "")
        doi = doi if doi.startswith("10.") else ""
        brows.append([r["id"], r["title"], jt(r), (m.get("abstract") or "").strip() or "（抄録なし: どの出どころにも見つからなかった。題名だけで判定する）",
                      (ja.get(r["id"]) or {}).get("abstract_ja", ""), m.get("authors", ""), r.get("year"),
                      r.get("journal"), doi])
    st.table(bib, ["ID", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体",
                   "DOI"], [10, 36, 30, 70, 60, 24, 6, 22, 24], brows,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体"},
             links={"DOI": lambda v: ("https://doi.org/" + v[8], v[8]) if v[8] else None}, tab="64748B",
             height=lambda v: st.text_height((v[1], 36), (v[2], 30), (v[3], 70), (v[4], 60)))
    cr = wb.create_sheet("判定基準")
    st.table(cr, ["項目", "内容"], [22, 120], [list(x) for x in db.CRITERIA], wrap={"内容"}, tab="64748B",
             height=lambda v: st.text_height((v[1], 120)))
    wb.save(os.path.join(out, name))
    print(f"wrote {os.path.join(out, name)}: {len(rows)} records")


if __name__ == "__main__":
    main()
