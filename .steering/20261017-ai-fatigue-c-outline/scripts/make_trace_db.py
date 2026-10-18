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

The workbook author 1 fills in lives in the Google Drive folder AI-fatigue/TRACE and is opened with the Excel app
(decision 36). If the output file exists, the values author 1 has entered in the blue columns of '段1' and '段2・3'
are carried over by ID into the new workbook, and the old file is first copied to <data>/../backup/; the script
stops if the old file has a record that the new one lacks, so a rebuild cannot drop a judgement.

Run (openpyxl via uv):
    uv run --with openpyxl python make_trace_db.py --data ~/Documents/TRACE/data \
        --fulltext ~/Documents/TRACE/fulltext --out "$TRACE_DRIVE/TRACE_database.xlsx"
"""

import argparse
import datetime
import json
import os
import shutil
import sys

from openpyxl import Workbook, load_workbook

import trace_style as st
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
STAGE1_COLS = ["ID", "順", "束", "対象の群", "論文タイトル", "題名（日本語・機械訳）", "判定", "除外理由", "読んだ範囲",
               "根拠メモ", "最終", "最終の除外理由"]
STAGE2_COLS = ["ID", "順", "対象の群", "論文タイトル", "題名（日本語・機械訳）", "全文", "ファイル", "判定", "除外理由", "中心",
               "読んだ範囲", "根拠メモ", "最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）"]

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


STAGE1_INPUTS = {"判定", "除外理由", "読んだ範囲", "根拠メモ", "最終", "最終の除外理由"}
STAGE2_INPUTS = {"判定", "除外理由", "中心", "読んだ範囲", "根拠メモ", "最終", "最終の除外理由", "最終の中心",
                 "同じ標本の相手（E5）"}


def entered(path):
    """What author 1 has entered in an existing workbook: {sheet: {ID: {column: value}}}, blue columns only."""
    if not os.path.exists(path):
        return {}
    wb = load_workbook(path, read_only=True)
    out = {}
    for name, inputs in (("段1", STAGE1_INPUTS), ("段2・3", STAGE2_INPUTS)):
        if name not in wb.sheetnames:
            continue
        rows = list(wb[name].iter_rows(values_only=True))
        head = [str(c) if c is not None else "" for c in rows[0]]
        out[name] = {str(d["ID"]).strip(): {k: d[k] for k in inputs if k in d and d[k] not in (None, "", "未判定")}
                     for d in (dict(zip(head, r)) for r in rows[1:]) if d.get("ID")}
    return out


def carry(rows, cols, kept):
    """Put the entered values back into the new rows (the ID is the first column). Returns the number of cells."""
    n = 0
    for vals in rows:
        for k, v in kept.get(vals[0], {}).items():
            vals[cols.index(k)] = v
            n += 1
    return n


def link_cell(target, label):
    return (target, label) if target else None


def drive_link(name, drive):
    """The Drive link of a full text. For Europe PMC XML, its machine-extracted text, which reads in a browser."""
    if name.endswith(".xml"):
        txt = name[:-4] + ".txt"
        if txt in drive:
            return drive[txt], txt
    return (drive[name], name) if name in drive else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--fulltext", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.expanduser(a.out)
    data = os.path.expanduser(a.data)
    ftdir = os.path.expanduser(a.fulltext)
    recs = sorted(load(os.path.join(data, "records264.json")), key=lambda r: r["order"])
    meta = load(os.path.join(data, "meta.json"), {})
    chrome = load(os.path.join(data, "chrome_status.json"), {})
    ja = load(os.path.join(data, "ja.json"), {})            # machine translations (decision 35), optional
    drive = load(os.path.join(data, "drive_links.json"), {})  # file name -> Google Drive URL, optional
    today = datetime.date.today().isoformat()
    n_ft = sum(fulltext_status(r["id"], meta, chrome, ftdir)[0] == "あり" for r in recs)
    bib_row = {r["id"]: i + 2 for i, r in enumerate(recs)}  # row of each record in '文献DB'
    old = entered(out)
    lost = sorted(set().union(*(set(v) for v in old.values())) - set(bib_row)) if old else []
    if lost:
        sys.exit(f"{out} has records not in records264.json ({', '.join(lost[:10])}); nothing written")

    wb = Workbook()
    st.intro(wb.active, "TRACE｜追加候補の文献 DB（判定者 1 用）",
             f"作成 {today}・追加候補 {len(recs)} 件・全文あり {n_ft} 件（無料で公開された版だけ）", [
        ("進め方", [
            "段 1（題名・抄録）は『段1』、段 2（全文）と段 3（中心）は『段2・3』の青い欄に記入する。行は登録で決めた選別の順。束（9 件ずつ）ごとに上から判定する。束の ID は c_screening.py が示す。",
            "段 1 は題名と抄録だけで判定する。ID を押すと『文献DB』のその記録の抄録（英語と日本語）へ飛ぶ。その束の段 1 をコミットするまで、『段2・3』『全文』のシートと全文のファイルは開かない。",
            "段 2 で含めた記録には、同じときに中心も付ける。全文は『段2・3』の「ファイル」のリンクから Google Drive で開く。",
            "『最終…』の欄は、AI と食い違った記録にだけ、AI の答えを読んでから記入する。",
        ]),
        ("このファイルに入っていないもの", [
            "AI の判定も、以前の判定（2026-10 の判定者 1 の判定・AI の評価版）も入れていない。264 件すべてを空欄から判定する。",
        ]),
        ("日本語訳について", [
            "題名と抄録の日本語は Claude による機械訳で、読む助けにすぎない。判定の根拠は英語の原文とする。AI の選別者には英語だけを渡している。",
        ]),
        ("注意", [
            "対象の群は並べ替えのためで、判定の材料ではない。群の無い記録（レビュー型など）は『不明』に入れた。基準は『判定基準』。",
        ]),
    ])

    def jt(r):
        return (ja.get(r["id"]) or {}).get("title_ja", "")

    s1 = wb.create_sheet("段1")
    rows1 = [[r["id"], r["order"] + 1, r["order"] // BATCH + 1, r["population"], r["title"], jt(r), "未判定", "", "",
              "", "", ""] for r in recs]
    kept = carry(rows1, STAGE1_COLS, old.get("段1", {}))
    st.table(s1, STAGE1_COLS, [10, 5, 5, 14, 52, 40, 11, 10, 11, 32, 10, 12], rows1,
             inputs=STAGE1_INPUTS,
             wrap={"対象の群", "論文タイトル", "題名（日本語・機械訳）", "根拠メモ"},
             links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0])},
             tab="2563EB", height=lambda v: st.text_height((v[3], 14), (v[4], 52), (v[5], 40)))
    st.choices(s1, STAGE1_COLS, [("判定", STAGE_CHOICES), ("除外理由", CODE_CHOICES), ("読んだ範囲", READ_CHOICES),
                                 ("最終", STAGE1_FINAL), ("最終の除外理由", CODE_CHOICES)])

    def ft_link(v):
        return drive_link(v[6], drive) if v[6] else None

    s2 = wb.create_sheet("段2・3")
    rows2 = [[r["id"], r["order"] + 1, r["population"], r["title"], jt(r), fulltext_status(r["id"], meta, chrome, ftdir)[0],
              fulltext_file(r["id"], ftdir), "未判定", "", "未判定", "", "", "", "", "", ""] for r in recs]
    kept += carry(rows2, STAGE2_COLS, old.get("段2・3", {}))
    st.table(s2, STAGE2_COLS, [10, 5, 14, 46, 34, 14, 14, 11, 10, 13, 11, 30, 10, 12, 12, 14], rows2,
             inputs=STAGE2_INPUTS,
             wrap={"対象の群", "論文タイトル", "題名（日本語・機械訳）", "根拠メモ"},
             links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0]), "ファイル": ft_link},
             tab="0D9488", height=lambda v: st.text_height((v[2], 14), (v[3], 46), (v[4], 34)))
    st.choices(s2, STAGE2_COLS, [("判定", STAGE_CHOICES), ("除外理由", CODE_CHOICES), ("中心", CENTRE_CHOICES),
                                 ("読んだ範囲", READ_CHOICES), ("最終", STAGE_CHOICES), ("最終の除外理由", CODE_CHOICES),
                                 ("最終の中心", CENTRE_FINAL)])

    db = wb.create_sheet("文献DB")
    cols = ["ID", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体",
            "DOI", "抄録の出どころ", "同じ研究の群", "対象の群", "出どころ", "注記"]
    rows = []
    for r in recs:
        m = meta.get(r["id"], {})
        doi = str(r.get("doi") or "")
        doi = doi if doi.startswith("10.") else ""
        note = r.get("population_note", "")
        if r["id"] == "S04-36":
            note = (note + " ").strip() + "全文はワーキングペーパー版（題名が少し違う）"
        ab = (m.get("abstract") or "").strip()
        note = "　".join(x for x in (note, m.get("abstract_note", "")) if x)
        rows.append([r["id"], r["title"], jt(r), ab or "（抄録なし: どの出どころにも見つからなかった。題名だけで判定する）", (ja.get(r["id"]) or {}).get("abstract_ja", ""),
                     m.get("authors", ""), r.get("year"), r.get("journal"), doi, m.get("abstract_source", ""),
                     r.get("group", ""), r["population"], r.get("source"), note])
    st.table(db, cols, [10, 36, 30, 70, 60, 24, 6, 22, 24, 12, 18, 14, 16, 24], rows,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体", "注記"},
             links={"DOI": lambda v: link_cell("https://doi.org/" + v[8] if v[8] else "", v[8])},
             tab="64748B", height=lambda v: st.text_height((v[1], 36), (v[2], 30), (v[3], 70), (v[4], 60)))

    ft = wb.create_sheet("全文")
    rows = []
    for r in recs:
        stt, url, how = fulltext_status(r["id"], meta, chrome, ftdir)
        rows.append([r["id"], stt, fulltext_file(r["id"], ftdir), url, how, meta.get(r["id"], {}).get("oa_status") or ""])
    st.table(ft, ["ID", "全文", "ファイル", "取得元", "取り方", "OA の状態（OpenAlex）"], [10, 24, 16, 60, 12, 18], rows,
             links={"ファイル": lambda v: drive_link(v[2], drive) if v[2] else None,
                    "取得元": lambda v: link_cell(v[3], v[3])}, tab="64748B")

    cr = wb.create_sheet("判定基準")
    st.table(cr, ["項目", "内容"], [22, 120], [list(x) for x in CRITERIA], wrap={"内容"}, tab="64748B",
             height=lambda v: st.text_height((v[1], 120)))

    lock = os.path.join(os.path.dirname(out), "~$" + os.path.basename(out))
    if os.path.exists(lock):  # Excel has the workbook open: its unsaved entries would be lost or would overwrite this
        sys.exit(f"{out} is open in Excel ({lock} exists); close it and run again. Nothing written")
    if os.path.exists(out):
        bak = os.path.join(os.path.dirname(data.rstrip("/")), "backup")
        os.makedirs(bak, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(out, os.path.join(bak, f"{os.path.splitext(os.path.basename(out))[0]}.{stamp}.xlsx"))
    tmp = out + ".tmp.xlsx"
    wb.save(tmp)
    os.replace(tmp, out)
    print(f"wrote {out}: {len(recs)} records, full text {n_ft}, translations {len(ja)}, Drive links {len(drive)}, "
          f"entered cells carried over {kept}")


if __name__ == "__main__":
    main()
