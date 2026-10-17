"""Make the TRACE screening database (xlsx) for author 1 (decisions 26 and 28).

The workbook holds bibliographic data, abstracts and the full-text status of the 264 additional candidates, and
empty screening columns in the fixed screening order (GSRR-33). It carries no AI judgement and none of author 1's
earlier judgements: author 1 screens all 264 records afresh, without seeing the AI screener's output, which is
kept in a separate file after registration (decision 26).

Author 1 judges stage 1 on the sheet '段1' (title and abstract only: it has no full-text column), and stages 2 and 3
together on the sheet '段2・3', which also shows the full-text status (GSRR-33, decision 33). The columns
'最終…' are filled only for records on which the two screeners differ; c_screening.py reads both sheets by
their headers.

Inputs live outside the repository (abstracts and full texts are not copied into it):
    <data>/records264.json   ID, title, DOI, year, journal, source, same-study group, population group, order
    <data>/meta.json         authors, abstract and its source, OA status and locations, script download
    <data>/chrome_status.json (optional) result of the browser pass per record
    <fulltext>/<ID>.pdf      saved free full texts
    <fulltext>/<ID>.xml      free full text as Europe PMC JATS XML (with <ID>.txt, its text extracted by machine)
    <fulltext>/<ID>.html     free full text as the publisher's article page, saved by the researcher

Run (openpyxl via uv):
    uv run --with openpyxl python make_trace_db.py --data ~/Documents/TRACE/data \
        --fulltext ~/Documents/TRACE/fulltext --out ~/Documents/TRACE/TRACE_database.xlsx
"""

import argparse
import datetime
import json
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

INPUT = PatternFill("solid", fgColor="DDEBF7")
HEAD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")

STAGE_CHOICES = "未判定,含める,除外,保留"
CENTRE_CHOICES = "未判定,中心-A,中心-B,境界（保留）"
CODE_CHOICES = "E1,E2,E3,E4,E5,E6,E7"
READ_CHOICES = "題名のみ,抄録,全文の一部,全文"
STAGE1_FINAL = "含める,除外"
CENTRE_FINAL = "中心-A,中心-B"
BATCH = 9  # records per batch (GSRR-33)
STAGE1_COLS = ["ID", "順", "束", "対象の群", "論文タイトル", "判定", "除外理由", "読んだ範囲", "根拠メモ", "最終",
               "最終の除外理由"]
STAGE2_COLS = ["ID", "順", "対象の群", "論文タイトル", "全文", "ファイル", "判定", "除外理由", "中心", "読んだ範囲",
               "根拠メモ", "最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）"]

CRITERIA = [
    ("問い", "AI の系を使う・監督する・評価する人の一次研究で、疲労をその AI の利用と関係づけて定義・測定・質的に分析しているもの。疲労＝認知・情動・身体・動機・行動の消耗、疲弊、燃え尽き様の消耗。"),
    ("範囲の決定 (a)", "AI の導入・利用を操作・比較し、使う人の疲労・消耗・燃え尽きを測った研究は、デザインと結果の向きを問わず当たりうる。"),
    ("範囲の決定 (b)", "自動化の監視の研究は、論文が対象の系を AI・機械学習と書く場合だけ当たる。従来の自動化だけの研究は E3。"),
    ("手順 1: 題名・抄録段", "題名・抄録を読み、当たる可能性のある一次研究は含める（迷ったら含める＝全文段へ回す）。一次研究でない（レビュー・尺度の原著・方法論・訂正通知）は除外＋E4。"),
    ("手順 2: 全文段", "含める・保留にした件は本文を読む。無料で公開された本文が無ければ保留＋E6（本文が英語・日本語以外と分かっていて英語・日本語の版も無ければ E7）。規則だけで決まらなければ保留。"),
    ("手順 3: 中心の段", "全文段で含めた件に付ける。中心-A＝疲労を AI に帰属させて定義・測定（項目文・定義・質問文に AI が出る、または AI 疲労の語りを分析）。中心-B＝一般の構成概念（項目に AI が出ない）で、AI の利用や AI 由来の要求と関係づける。境界（保留）＝規則だけでは決まらない。"),
    ("E1", "AI は疲労を検知・予測する道具であるだけ。"),
    ("E2", "疲労を測っていない。"),
    ("E3", "AI の利用と関係がない。"),
    ("E4", "一次研究でない（レビュー・プロトコル・論考・方法論・訂正通知、AI の利用・監督に関わる疲労の尺度でない尺度の原著）。AI の利用・監督に関わる疲労の尺度の研究は一次研究として判定する。"),
    ("E5", "同じ標本の重複・二次の報告（本文で確かめる）。"),
    ("E6", "無料で公開された本文が手に入らない。"),
    ("E7", "本文の言語が英語・日本語以外で、英語・日本語の版も無い。ほかの理由にも当たればそちらを選ぶ。"),
    ("注意", "研究デザインや報告の水準は範囲の判断に使わない。結果の向きで範囲を変えない。対象の群は並べ替えのためで、判定の材料ではない。"),
]


def load(path, default=None):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def header(ws, cols, widths):
    ws.append(cols)
    for i, w in enumerate(widths, start=1):
        ws.cell(row=ws.max_row, column=i).font = HEAD
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    ws.freeze_panes = "B2"  # a string: ws.cell(...) would create row 2 and push the data down


def fill_inputs(ws, cols, choices, free=("根拠メモ",)):
    """Drop-down lists and the blue fill on the columns author 1 fills in."""
    last = ws.max_row
    for name, values in choices:
        letter = ws.cell(row=1, column=cols.index(name) + 1).column_letter
        dv = DataValidation(type="list", formula1=f'"{values}"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{letter}2:{letter}{last}")
    idx = {cols.index(n) for n, _ in choices} | {cols.index(n) for n in free}
    for row in ws.iter_rows(min_row=2, max_row=last):
        for i in idx:
            row[i].fill = INPUT
        row[cols.index("論文タイトル")].alignment = WRAP
    ws.auto_filter.ref = f"A1:{ws.cell(row=1, column=len(cols)).column_letter}{last}"


def fulltext_file(rid, ftdir):
    for ext in (".pdf", ".xml", ".html"):
        if os.path.exists(os.path.join(ftdir, rid + ext)):
            return rid + ext
    return ""


def fulltext_status(rid, meta, chrome, ftdir):
    if fulltext_file(rid, ftdir).endswith(".xml"):
        return "あり", chrome.get(rid, {}).get("url", ""), "Europe PMC"
    if fulltext_file(rid, ftdir):
        m = meta.get(rid, {})
        if m.get("fulltext"):
            return "あり", m["fulltext"]["url"], "脚本"
        c = chrome.get(rid, {})
        return "あり", c.get("url", ""), c.get("how", "Chrome")
    c = chrome.get(rid)
    if c:
        label = {"paywalled": "無料の版なし（有料）", "captcha": "要確認（CAPTCHA）", "viewer": "要保存（PDF ビューア）",
                 "failed": "取れず", "nourl": "リンクなし", "nomatch": "取れず（別の論文）"}.get(c["status"], c["status"])
        return label, c.get("url", ""), "Chrome"
    oa = meta.get(rid, {}).get("oa_status")
    return ("無料の版なし（OpenAlex: closed）" if oa == "closed" else "未取得"), "", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--fulltext", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = os.path.expanduser(a.data)
    ftdir = os.path.expanduser(a.fulltext)
    recs = sorted(load(os.path.join(data, "records264.json")), key=lambda r: r["order"])
    meta = load(os.path.join(data, "meta.json"), {})
    chrome = load(os.path.join(data, "chrome_status.json"), {})
    today = datetime.date.today().isoformat()

    wb = Workbook()
    ws = wb.active
    ws.title = "はじめに"
    n_ft = sum(fulltext_status(r["id"], meta, chrome, ftdir)[0] == "あり" for r in recs)
    for line in [
        ["TRACE｜追加候補の文献 DB（判定者 1 用）"],
        [f"作成 {today}。追加候補 264 件（元の DB の追加候補 221 件と、レビューを狙った探索の 43 件）。"],
        ["段 1（題名・抄録）は『段1』、段 2（全文）と段 3（中心）は『段2・3』の青い欄に記入する。行は登録で決めた選別の順（群ごとに乱数で並べ、群を交互に並べた順）。束（9 件ずつ）ごとに上から判定する。束の ID は c_screening.py が示す。"],
        ["段 1 は題名と抄録だけで判定する。その束の段 1 をコミットするまで、『段2・3』『全文』のシートと fulltext フォルダを開かない。段 2 で含めた記録には、同じときに中心も付ける。『最終…』の欄は、AI と食い違った記録にだけ、AI の答えを読んでから記入する。"],
        ["このファイルには AI の判定も、以前の判定（2026-10 の判定者 1 の判定・AI の評価版）も入れていない。264 件すべてを空欄から判定する。AI の判定は登録の後に別のファイルで付け、両方がそろってから食い違いを見る。"],
        ["基準は『判定基準』。抄録は『文献DB』にある（取れなかった件はリンク先で読む）。全文は fulltext フォルダの <ID>.pdf・<ID>.html（出版社の記事ページ）・<ID>.xml（PMC の本文。同じ名前の .txt は本文を機械で抜き出したもの）。一覧は『全文』のシート。"],
        [f"全文あり: {n_ft} 件 / 264 件（無料で公開された版だけ。有料の版は使わない）。"],
        ["対象の群は並べ替えのためで、判定の材料ではない。群の無い記録（レビュー型など）は『不明』に入れた。"],
    ]:
        ws.append(line)
    ws.column_dimensions["A"].width = 140
    for row in ws.iter_rows():
        row[0].alignment = WRAP
    ws["A1"].font = Font(bold=True, size=13)

    s1 = wb.create_sheet("段1")
    header(s1, STAGE1_COLS, [9, 5, 5, 16, 60, 12, 12, 12, 40, 12, 14])
    for r in recs:
        s1.append([r["id"], r["order"] + 1, r["order"] // BATCH + 1, r["population"], r["title"], "未判定", "", "", "",
                   "", ""])
    fill_inputs(s1, STAGE1_COLS, [("判定", STAGE_CHOICES), ("除外理由", CODE_CHOICES), ("読んだ範囲", READ_CHOICES),
                                  ("最終", STAGE1_FINAL), ("最終の除外理由", CODE_CHOICES)])

    s2 = wb.create_sheet("段2・3")
    header(s2, STAGE2_COLS, [9, 5, 16, 60, 18, 14, 10, 12, 14, 12, 40, 10, 14, 12, 14])
    for r in recs:
        st = fulltext_status(r["id"], meta, chrome, ftdir)[0]
        s2.append([r["id"], r["order"] + 1, r["population"], r["title"], st, fulltext_file(r["id"], ftdir), "未判定", "",
                   "未判定", "", "", "", "", "", ""])
    fill_inputs(s2, STAGE2_COLS, [("判定", STAGE_CHOICES), ("除外理由", CODE_CHOICES), ("中心", CENTRE_CHOICES),
                                  ("読んだ範囲", READ_CHOICES), ("最終", STAGE_CHOICES), ("最終の除外理由", CODE_CHOICES),
                                  ("最終の中心", CENTRE_FINAL)], free=("根拠メモ", "同じ標本の相手（E5）"))

    db = wb.create_sheet("文献DB")
    cols = ["ID", "論文タイトル", "著者", "年", "掲載誌・媒体", "DOI", "リンク", "出どころ", "同じ研究の群", "対象の群",
            "抄録", "抄録の出どころ", "注記"]
    header(db, cols, [9, 50, 30, 6, 28, 26, 30, 16, 22, 16, 90, 14, 30])
    for r in recs:
        m = meta.get(r["id"], {})
        doi = str(r.get("doi") or "")
        link = "https://doi.org/" + doi if doi.startswith("10.") else ""
        note = r.get("population_note", "")
        if r["id"] == "S04-36":
            note = (note + " ").strip() + "全文はワーキングペーパー版（題名が少し違う）"
        db.append([r["id"], r["title"], m.get("authors", ""), r.get("year"), r.get("journal"), doi, link, r.get("source"),
                   r.get("group", ""), r["population"], m.get("abstract", ""), m.get("abstract_source", ""), note])
    for row in db.iter_rows(min_row=2):
        row[10].alignment = WRAP
        row[1].alignment = WRAP

    ft = wb.create_sheet("全文")
    header(ft, ["ID", "全文", "ファイル", "取得元", "取り方", "OA の状態（OpenAlex）"], [9, 26, 14, 70, 10, 18])
    for r in recs:
        st, url, how = fulltext_status(r["id"], meta, chrome, ftdir)
        ft.append([r["id"], st, fulltext_file(r["id"], ftdir), url, how, meta.get(r["id"], {}).get("oa_status") or ""])

    cr = wb.create_sheet("判定基準")
    header(cr, ["項目", "内容"], [22, 120])
    for k, v in CRITERIA:
        cr.append([k, v])
    for row in cr.iter_rows(min_row=2):
        row[1].alignment = WRAP

    wb.save(os.path.expanduser(a.out))
    print(f"wrote {a.out}: {len(recs)} records, full text {n_ft}")


if __name__ == "__main__":
    main()
