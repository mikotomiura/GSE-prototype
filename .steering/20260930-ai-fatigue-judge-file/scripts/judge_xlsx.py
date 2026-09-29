"""判定者用ファイル（AI の判定・評価を含まない）を作る（design.md「判定者用ファイル」・decisions.md 判断 1〜3・7）。

出発点は ../20260929-ai-fatigue-db-readable-and-gaps/prior-draft/judge_xlsx.py。その README の「直すこと」6 点を直した:
  1 既存の出力を上書きしない（--force でも、記入のあるファイルは上書きしない）
  2 未コミットの build_xlsx.py に依存しない（行の高さ・書体を自前で持つ）
  3 出力先を必ず指定させ、無いディレクトリは作らない
  4 DOI のリンクは urllib.parse.quote を通す
  5 AI の判定・懸念の語が無いことは check_judge_xlsx.py が確かめる（本スクリプトも保存前に呼ぶ）
  6 data_d.py の文面を使い回さない（使っていない）

使い方（uv で openpyxl を入れて実行する）:
  python judge_xlsx.py --judge 1 --out <出力 .xlsx> [--copy-to <ディレクトリ>] [--force]
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.parse

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter as col

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
sys.path.insert(0, HERE)
import candidates as CAND  # noqa: E402

DB_XLSX = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                       "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
DB_SHA = "48ba8b908413fc8112ec35852d4317389500f577092e7be47384628b5f7ce8b0"  # Downloads の同名ファイルと一致（2026-09-30）
# ★ 試しに作るときだけ環境変数で差し替える。本番は evidence の oa_*.json をすべて合わせて読む（記録は上書きせず、足りない DOI だけ別のファイルに足す）
OA_JSON = os.environ.get("JUDGE_OA_JSON") or os.path.join(TASK, "evidence", "oa_2026-09-30.json")
OA_GLOB = os.path.join(TASK, "evidence", "oa_*.json")
EVID_PREV = os.path.join(STEER, "20260929-ai-fatigue-surveys", "evidence")

# ---------------------------------------------------------------- 見た目（build_readable.py と同じ）
FONT = "Noto Sans CJK JP"
TEXT = "FF22364A"
TITLE_FILL = PatternFill("solid", fgColor="FF143D48")
SUB_FILL = PatternFill("solid", fgColor="FFEAF4F6")
HEAD_FILL = PatternFill("solid", fgColor="FF0F766E")
INPUT_FILL = PatternFill("solid", fgColor="FFFEF9C3")
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
WRAP_CENTER = Alignment(wrap_text=True, vertical="center")
LINK = Font(name=FONT, size=11, color="FF0563C1", underline="single")
INPUT_FONT = Font(name=FONT, size=11, color="FF175CD3")

# ---------------------------------------------------------------- 記入欄（両方の判定シートで同じ）
UNDECIDED = "未判定"
INPUT_HEADERS = ["題名・抄録段", "全文段", "中心範囲の段", "除外理由", "読んだ範囲", "根拠メモ", "判定日"]
CHOICES = {
    "題名・抄録段": "未判定,含める,除外,保留",
    "全文段": "未判定,含める,除外,保留",
    "中心範囲の段": "未判定,中心-A,中心-B,境界（保留）,背景（E2）,背景（E4）,方法論,訂正",
    "除外理由": "E1,E2,E3,E4,E5,E6",
    "読んだ範囲": "題名のみ,抄録,全文の一部,全文",
}
INITIAL = {"題名・抄録段": UNDECIDED, "全文段": UNDECIDED, "中心範囲の段": UNDECIDED}
DB_HEADERS = ["ID", "論文タイトル", "著者（短縮）", "年", "掲載誌・媒体", "公表区分", "DOI", "一次情報URL", "本文の入手（OpenAlex）"]
DB_WIDTHS = [8, 46, 18, 7, 24, 14, 24, 28, 16]
CAND_HEADERS = ["候補番号", "出どころ", "事実のファイルでの表記", "題名（書誌の記録）", "年", "掲載誌", "DOI", "本文の入手（OpenAlex）",
                "要点（事実のファイルの記述）"]
CAND_WIDTHS = [9, 12, 30, 40, 6, 20, 24, 16, 70]
INPUT_WIDTHS = [13, 11, 14, 10, 12, 36, 11]
BIB_COLUMNS = {"判定シート": {"論文タイトル", "掲載誌・媒体"},
               "追加候補": {"事実のファイルでの表記", "題名（書誌の記録）", "掲載誌", "要点（事実のファイルの記述）"}}
LABEL_HEADERS = {"研究", "書誌", "年"}
SKIP_HEADERS = {"読んだ範囲"}  # サーヴェイで読んだ範囲（判定者の記入欄『読んだ範囲』と紛らわしいので要点に入れない）


def text_units(v):
    return sum(2.0 if ord(ch) > 0x2E7F else 1.1 for ch in str(v))


def row_height(values, widths):
    import math
    lines = 1
    for v, w in zip(values, widths):
        if v is None or v == "":
            continue
        per_line = max(1.0, w - 1.5)
        n = sum(max(1, math.ceil(text_units(part) / per_line)) for part in str(v).splitlines() or [""])
        lines = max(lines, n)
    return min(409, max(18, 15 * lines + 3))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for b in iter(lambda: fp.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- 事実のファイルからの抜き出し
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s|）)（(。,、;・〈〉\]]+", re.I)


def strip_md(s):
    return re.sub(r"\s+", " ", re.sub(r"\*\*|(?<!\w)\*|\*(?!\w)|`", "", s)).strip()


def _section(path, prefix):
    lines = open(os.path.join(TASK, path), encoding="utf-8").read().split("\n")
    key = prefix.lstrip("#").lstrip()  # ★ 末尾の空白は残す（『#1 』が『#10』『#11』に当たらないように）
    heads = [i for i, l in enumerate(lines) if l.startswith("#") and (l.lstrip("#").lstrip() + " ").startswith(key)
             and l.split(" ", 1)[0] == prefix.split(" ", 1)[0]]
    if len(heads) != 1:
        raise ValueError(f"{path}: 節『{prefix}』がちょうど 1 つではない（{len(heads)}）")
    i = heads[0]
    level = len(lines[i]) - len(lines[i].lstrip("#"))
    j = i + 1
    while j < len(lines) and not (lines[j].startswith("#") and len(lines[j]) - len(lines[j].lstrip("#")) <= level):
        j += 1
    return lines[i + 1:j]


SEP_RE = re.compile(r"^\|(\s*:?-+:?\s*\|)+\s*$")  # ★ 表の区切りの行だけ（『| -0.2 |』のような値の行を見出しと取り違えない）


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def find_row(path, sec, mark):
    """節の中の表で、目印を含む行（ちょうど 1 行）と、その表の見出しを返す。"""
    body = _section(path, sec)
    hits = []
    header = None
    for k, l in enumerate(body):
        if not l.startswith("|"):
            header = None
            continue
        if k + 1 < len(body) and SEP_RE.match(body[k + 1]):
            header = cells(l)
            continue
        if SEP_RE.match(l):
            continue
        if mark in l:
            hits.append((header, cells(l)))
    if len(hits) != 1 or hits[0][0] is None:
        raise ValueError(f"{path} {sec}: 目印『{mark}』の行がちょうど 1 行ではない（{len(hits)}）")
    return hits[0]


def find_bullets(path, heading):
    body = _section(path, heading)
    return [strip_md(l[2:]) for l in body if l.startswith("- ")]


def tag(path, sec):
    sid = re.search(r"survey-(S-\d\d)", path).group(1)
    if sec.startswith("§"):
        return f"{sid} {sec}"
    return f"{sid} §{sec.lstrip('#').strip().split(' ')[0].rstrip('.')}"


def extract(c):
    """候補 1 件の（表記・要点・DOI）を事実のファイルから作る。要点は『見出し: 値』を ／ でつなぐ。"""
    labels, parts, doi = [], [], c.get("doi")
    for path, sec, mark in c["refs"]:
        if mark.startswith("### #"):
            parts.append(f"【{tag(path, '§2')}】" + " ／ ".join(find_bullets(path, mark)))
            continue
        head, row = find_row(path, sec, mark)
        lab = " ".join(strip_md(v) for h, v in zip(head, row) if h in LABEL_HEADERS)
        labels.append(lab)
        body = " ／ ".join(f"{h}: {strip_md(v)}" for h, v in zip(head, row)
                          if h not in LABEL_HEADERS and h not in SKIP_HEADERS and strip_md(v))
        parts.append(f"【{tag(path, sec)}】" + body)
        if doi is None and "doi_from" not in c:
            m = DOI_RE.search(" ".join(row))
            doi = m.group(0).rstrip(".") if m else None
    if "bib" in c:
        path, sec, mark = c["bib"]
        head, row = find_row(path, sec, mark)
        labels.insert(0, strip_md(row[1]))
        m = DOI_RE.search(row[1])
        doi = doi or (m.group(0).rstrip(".") if m else None)
    return {"label": " ／ ".join(dict.fromkeys(labels)), "points": "\n".join(parts), "doi": doi}


def bib_index():
    """DOI → (題名, 年, 掲載誌)。前タスクと本タスクの evidence の書誌の記録だけを使う（抄録は使わない）。"""
    idx, by_tsv = {}, {}
    for p in glob.glob(os.path.join(EVID_PREV, "S-0[45]", "*_extraction_*.tsv")):
        with open(p, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r.get("doi"):
                    idx.setdefault(r["doi"].lower(), (r["title"], r["year"], r["journal"]))
                by_tsv[r["id"]] = (r["title"], r["year"], r["journal"])
    meta = json.load(open(os.path.join(EVID_PREV, "S-02", "s02_meta_2026-09-29.json"), encoding="utf-8"))
    for r in meta["records"]:
        idx.setdefault(r["doi"].lower(), (r["title"], (r.get("issued") or [None])[0], r.get("container", "")))
    for p in glob.glob(os.path.join(EVID_PREV, "S-12", "*_results_*.json")) + glob.glob(os.path.join(TASK, "evidence", "S-1*", "*_results_*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for run in d.get("runs", []):
            for r in run.get("records", []):
                if r.get("doi"):
                    idx.setdefault(r["doi"].lower(), (r.get("title", ""), r.get("year"), r.get("journal", "")))
    return idx, by_tsv


def oa_label(oa, doi):
    if not doi:
        return "DOI なし"
    rec = oa.get(doi.lower())
    if rec is None:
        return "未確認"
    if rec.get("status") != "ok":
        return "未確認（取得できず）"
    return f"無料の版あり（{rec.get('oa_status')}）" if rec.get("is_oa") else "無料の版なし"


def doi_url(doi):
    return "https://doi.org/" + urllib.parse.quote(doi, safe="/:;()._-")


# ---------------------------------------------------------------- シート
def header_block(ws, title, subtitle, ncol):
    last = col(ncol)
    for addr, val, fill, bold, color in (("A1", title, TITLE_FILL, True, "FFFFFFFF"), ("A2", subtitle, SUB_FILL, False, TEXT)):
        c = ws[addr]
        c.value, c.fill, c.alignment = val, fill, WRAP_TOP
        c.font = Font(name=FONT, size=11, bold=bold, color=color)
    ws.merge_cells(f"A1:{last}1")
    ws.merge_cells(f"A2:{last}2")
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 48


def put_table(ws, headers, widths, rows):
    for j, h in enumerate(headers, 1):
        c = ws.cell(4, j, h)
        c.font, c.fill, c.alignment = Font(name=FONT, size=11, bold=True, color="FFFFFFFF"), HEAD_FILL, WRAP_CENTER
    ws.row_dimensions[4].height = 36
    for i, row in enumerate(rows, 5):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v)
            if isinstance(v, str) and v.startswith("="):
                c.data_type = "s"  # 数式は集計シートだけ
            c.font, c.alignment = Font(name=FONT, size=11, color=TEXT), WRAP_TOP
        ws.row_dimensions[i].height = row_height(row, widths)
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[col(j)].width = w
    ws.freeze_panes = "B5"


def text_sheet(wb, name, title, subtitle, rows, first=False):
    ws = wb.active if first else wb.create_sheet(name)
    ws.title = name
    header_block(ws, title, subtitle, 2)
    put_table(ws, ["項目", "説明"], [24, 110], rows)
    return ws


def input_columns(ws, headers, first_input, last_row, table_name):
    n = len(headers)
    for r in range(5, last_row + 1):
        for cidx in range(first_input, n + 1):
            c = ws.cell(r, cidx)
            c.fill, c.font = INPUT_FILL, INPUT_FONT
            c.value = INITIAL.get(headers[cidx - 1])
    for h, opts in CHOICES.items():
        L = col(headers.index(h) + 1)
        dv = DataValidation(type="list", formula1='"' + opts + '"', allow_blank=True)
        dv.add(f"{L}5:{L}{last_row}")
        ws.add_data_validation(dv)
    for h in ("題名・抄録段", "全文段"):
        L = col(headers.index(h) + 1)
        for val, color in (("含める", "FFD1FAE5"), ("保留", "FFFEF3C7"), ("除外", "FFE5E7EB")):
            ws.conditional_formatting.add(f"{L}5:{L}{last_row}",
                                          FormulaRule(formula=[f'{L}5="{val}"'], fill=PatternFill("solid", fgColor=color, bgColor=color)))
    t = Table(displayName=table_name, ref=f"A4:{col(n)}{last_row}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=False)
    ws.add_table(t)


def link(cell, url):
    if url and str(url).startswith("http"):
        cell.hyperlink = url
        cell.font = LINK


def intro_rows(judge):
    rows = [
        ["このファイル", f"判定者 {judge} が、AI 疲労の文献を独立に判定するためのファイル。書誌・リンク・事実の要点・判定の基準だけを載せ、"
                        "AI が出した判定や評価は載せていない。"],
        ["判定者", f"判定者 {judge}"],
    ]
    if judge == 1:
        rows.append(["判定の前に読んだもの（記録）", "判定者 1 は、判定の前に、元の DB 34 件について評価版ファイルの AI の評価を読んでいる"
                                               "（2026-09-30 に研究者が決め、記録した）。"])
    else:
        rows.append(["判定の前に開かないもの", "判定が終わるまで、評価版ファイル（AI の評価のシートを足した xlsx）の AI の評価のシートと、元の DB の『AI…』のシート、"
                                        "研究のメモの一次確認のファイル（memo-issues.md）を開かない。開いた場合は、判定の記録にそのことを書く。"])
    rows += [
        ["追加候補について", "『追加候補』シートの文献には、AI の出力（サーヴェイの AI の案・評価版ファイルの『検索漏れ候補』シート）が別に"
                         "あるが、このファイルには載せていない。判定が終わるまで、それらのファイルを開かない。"],
        ["進め方", "『判定基準』シートの手順に従う。黄色の欄だけを入力する（ドロップダウンから選ぶ）。書誌と要点の欄は変えない。"],
        ["本文の入手", "有料の本文は入手しない（2026-09-30 の研究者の決定）。『本文の入手（OpenAlex）』の欄は OpenAlex の記録（2026-09-30）で、"
                    "無料の版が無いものは本文を読めない。"],
        ["要点の欄", "『追加候補』の要点は、サーヴェイの事実のファイルの記述をそのまま機械で写したもの（抄録・本文に書いてあることだけ）。"
                  "判定の根拠は、リンク先の抄録・本文で確かめる。"],
        ["終わったら", "このファイルを保存して渡す。2 人の判定がそろったら突き合わせる。"],
    ]
    return rows


CRITERIA = [
    ["基準の版", "評価プロトコル v1.0（2026-09-28 固定）に、2026-09-30 の範囲の決定を足したもの。"],
    ["問い（PCC）", "人が AI を使う・監督する・評価することに関連する疲労について、何が定義・測定・観察されているか（スコーピング型）。"
                "P＝AI を使う・監督する・評価する人。C＝疲労（認知・情動・身体・動機／行動面の消耗、exhaustion、weariness、燃え尽きのような枯渇）"
                "を定義・測定・質的に分析し、AI の利用・監督との関係の中で扱うもの。Context＝教育・職場・消費・研究など問わない。"
                "期間＝オンライン公開が 2026-09-28 以前（追加候補は 2026-09-30 の検索まで）。"],
    ["2026-09-30 の範囲の決定 (a)", "AI の導入・利用を操作・比較し、使う人の疲労・消耗・燃え尽きを測った研究は、デザイン（無作為化・非無作為化・前後比較）と"
                                 "結果の向きを問わず C に当たりうる。"],
    ["2026-09-30 の範囲の決定 (b)", "自動化の監視の研究は、論文が対象の系を AI・機械学習と書く場合だけ P に当たる。従来の自動化だけの研究は E3。"],
    ["手順 1: 題名・抄録段", "リンク先の題名・抄録を読み、P と C に当たる可能性のある一次研究は『含める』（迷ったら含める＝全文段へ回す）。"
                          "一次研究でない（レビュー・尺度の原著・方法論・訂正通知）は『除外』＋ E4（DB からは消さず背景として残す）。"],
    ["手順 2: 全文段", "『含める』『保留』にした件は本文を読み、全文段を選ぶ。本文を読めなかった件は『保留』＋ E6、読んだ範囲に『抄録』。"],
    ["手順 3: 中心範囲の段", "中心-A＝疲労を AI に帰属させて定義・測定している（項目文・定義・質問文に AI が出てくる、または AI 疲労の語りを分析する）。"
                          "中心-B＝疲労・消耗・燃え尽きを測るが、構成概念は一般的（項目に AI が出ない）で、AI の利用や AI 由来の要求と関係づけている。"
                          "境界（保留）＝規則だけでは決まらない。背景（E2）＝疲労を測っていない AI 利用の研究。背景（E4）＝一次研究でない。"],
    ["除外理由", "E1＝AI が人の疲労を検出・予測する道具であるだけ／E2＝疲労を定義・測定・質的分析していない（認知負荷・不安・過信だけなど）／"
             "E3＝疲労を測るが AI の利用・監督と関係づけていない／E4＝一次研究でない／E5＝重複出版・同じ標本・版違い／"
             "E6＝全文が手に入らず判定できない（→ 保留）。この表に無い理由で除外しない。"],
    ["注意", "研究デザインや報告の水準は、範囲の判断に使わない（引用の範囲で扱う）。結果の向き（疲労が増える・減る）で範囲を変えない。"],
    ["根拠メモ", "選んだ理由を短く書く（例: 項目文に AI が入る・疲労は一般の尺度・本文は有料で読めない）。"],
]


def build(judge):
    if sha256(DB_XLSX) != DB_SHA:
        sys.exit(f"元の DB の SHA-256 が固定値と違う: {DB_XLSX}")
    if not os.path.exists(OA_JSON):
        sys.exit(f"OpenAlex の記録が無い（先に fetch_oa.py を回す）: {OA_JSON}")
    oa = {}
    for p in ([OA_JSON] if os.environ.get("JUDGE_OA_JSON") else sorted(glob.glob(OA_GLOB))):
        oa.update({k.lower(): v for k, v in json.load(open(p, encoding="utf-8"))["records"].items()})
    db = openpyxl.load_workbook(DB_XLSX, data_only=True)["文献DB"]
    wb = openpyxl.Workbook()
    text_sheet(wb, "はじめに", "AI 疲労 文献 DB｜判定者用ファイル", "黄色の欄だけを入力する。", intro_rows(judge), first=True)
    text_sheet(wb, "判定基準", "判定基準（評価プロトコル v1.0 ＋ 2026-09-30 の範囲の決定）", "判定者 1・2 で共通の基準。", CRITERIA)

    # DB 34 件
    ws = wb.create_sheet("判定シート")
    headers = DB_HEADERS + INPUT_HEADERS
    rows, ids = [], []
    for r in range(5, 39):
        v = [db.cell(r, c).value for c in range(1, 15)]
        ids.append(v[0])
        doi = v[7] if v[7] and str(v[7]).startswith("10.") else None
        rows.append([v[0], v[4], v[5], v[3], v[6], v[8], v[7], v[10], oa_label(oa, doi)] + [None] * len(INPUT_HEADERS))
    header_block(ws, "判定シート｜元の DB 34 件", "DOI・URL から論文のページを開く。選択肢は『判定基準』シート。", len(headers))
    put_table(ws, headers, DB_WIDTHS + INPUT_WIDTHS, rows)
    last = 4 + len(rows)
    for r in range(5, last + 1):
        d = ws.cell(r, 7).value
        link(ws.cell(r, 7), doi_url(d) if d and str(d).startswith("10.") else None)
        link(ws.cell(r, 8), ws.cell(r, 8).value)
    input_columns(ws, headers, len(DB_HEADERS) + 1, last, "JudgeDB")

    # 追加候補
    idx, by_tsv = bib_index()
    wc = wb.create_sheet("追加候補")
    cheaders = CAND_HEADERS + INPUT_HEADERS
    crows = []
    for c in CAND.CANDIDATES:
        e = extract(c)
        doi = e["doi"]
        t = idx.get(doi.lower()) if doi else None
        if t is None and c.get("tsv_id"):
            t = by_tsv.get(c["tsv_id"])
        title, year, journal = t if t else ("", "", "")
        src = " ／ ".join(dict.fromkeys(tag(p, s) for p, s, _ in c["refs"]))
        crows.append([c["cid"], src, e["label"], title, year, journal, doi or "", oa_label(oa, doi), e["points"]] + [None] * len(INPUT_HEADERS))
    header_block(wc, f"追加候補｜サーヴェイで見つかった DB に無い文献（{len(crows)} 件）",
                 "DB の行には足していない。要点はサーヴェイの事実のファイルの記述の写し。判定はリンク先の抄録・本文で行う。", len(cheaders))
    put_table(wc, cheaders, CAND_WIDTHS + INPUT_WIDTHS, crows)
    clast = 4 + len(crows)
    for r in range(5, clast + 1):
        d = wc.cell(r, 7).value
        link(wc.cell(r, 7), doi_url(d) if d else None)
    input_columns(wc, cheaders, len(CAND_HEADERS) + 1, clast, "JudgeExtra")

    # 集計
    agg = []
    for sheet, n_last, n_in in (("判定シート", last, len(DB_HEADERS)), ("追加候補", clast, len(CAND_HEADERS))):
        for h in ("題名・抄録段", "全文段"):
            L = col(n_in + INPUT_HEADERS.index(h) + 1)
            for v in ("含める", "除外", "保留", UNDECIDED):
                agg.append([f"{sheet}｜{h}: {v}", f"=COUNTIF('{sheet}'!{L}5:{L}{n_last},\"{v}\")"])
    sa = wb.create_sheet("集計")
    header_block(sa, "集計｜進み具合", "判定シートと追加候補の記入を数える数式。", 2)
    put_table(sa, ["項目", "件数"], [34, 12], agg)
    for r in range(5, 5 + len(agg)):
        sa.cell(r, 2).data_type = "f"
    wb.active = wb.sheetnames.index("判定シート")
    for w in wb.worksheets:
        w.sheet_view.tabSelected = (w.title == "判定シート")
    wb.properties.title = "AI 疲労 文献 DB 判定者用ファイル"
    wb.properties.creator = "judge_xlsx.py"
    return wb, ids


def has_entries(path):
    """既存のファイルに記入（未判定・空以外）があるか。"""
    wb = openpyxl.load_workbook(path)
    for name in ("判定シート", "追加候補"):
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        for h in INPUT_HEADERS:
            if h in head:
                j = head.index(h) + 1
                for r in range(5, ws.max_row + 1):
                    if ws.cell(r, j).value not in (None, "", UNDECIDED):
                        return True
    return False


def guard(dst, force):
    d = os.path.dirname(os.path.abspath(dst))
    if not os.path.isdir(d):
        sys.exit(f"出力先のディレクトリが無い（作らない）: {d}")
    if os.path.exists(dst):
        if not force:
            sys.exit(f"出力先が既にある（上書きしない。--force で記入の無いファイルだけ上書き）: {dst}")
        if has_entries(dst):
            sys.exit(f"出力先に記入がある（--force でも上書きしない）: {dst}")


def place(src, dst, force):
    """src を dst に置く。★ 書く直前にもう一度確かめる（確かめてから書くまでの間の記入を消さない・security L-2）。
    --force で既存を置き換えるときは、旧ファイルを時刻つきの名前で退避してから置く。"""
    guard(dst, force)
    if os.path.exists(dst):
        import time
        os.replace(dst, f"{dst}.bak-{time.strftime('%Y%m%d%H%M%S')}")
    if os.path.exists(dst):
        sys.exit(f"退避できなかった: {dst}")
    with open(src, "rb") as fi, open(dst, "xb") as fo:  # ★ 排他的に作る（間に誰かが作っていたら止まる）
        shutil.copyfileobj(fi, fo)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", type=int, choices=(1, 2), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--copy-to")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    guard(a.out, a.force)
    copy_dst = os.path.join(a.copy_to, os.path.basename(a.out)) if a.copy_to else None
    if copy_dst:
        if os.path.normcase(os.path.abspath(copy_dst)) == os.path.normcase(os.path.abspath(a.out)):
            sys.exit("--copy-to の先が --out と同じ")
        guard(copy_dst, a.force)
    wb, ids = build(a.judge)
    import check_judge_xlsx as CHK
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".xlsx", dir=os.path.dirname(os.path.abspath(a.out)))
    os.close(fd)
    try:
        wb.save(tmp)
        errs = CHK.check(tmp)
        for e in errs:
            print("NG", e)
        if errs:
            sys.exit("判定者用ファイルの検査に失敗した（保存しない）")
        place(tmp, a.out, a.force)
        print("saved:", a.out)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    if copy_dst:
        place(a.out, copy_dst, a.force)
        print("copied:", copy_dst)


if __name__ == "__main__":
    main()
