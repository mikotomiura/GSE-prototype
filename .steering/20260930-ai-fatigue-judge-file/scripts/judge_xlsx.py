"""判定者用ファイル（AI の判定・評価を含まない）を作る（design.md「判定者用ファイル」・decisions.md 判断 1〜3・7）。

出発点は ../20260929-ai-fatigue-db-readable-and-gaps/prior-draft/judge_xlsx.py。その README の「直すこと」6 点を直した:
  1 既存の出力を上書きしない（--force でも、記入のあるファイルは上書きしない）
  2 未コミットの build_xlsx.py に依存しない（行の高さ・書体を自前で持つ）
  3 出力先を必ず指定させ、無いディレクトリは作らない
  4 DOI のリンクは urllib.parse.quote を通す
  5 AI の判定・懸念の語が無いことは check_judge_xlsx.py が確かめる（本スクリプトも保存前に呼ぶ）
  6 data_d.py の文面を使い回さない（使っていない）

2026-10-01: 259 件の間引き（../20260930-ai-fatigue-protocol の decisions.md 判断 3〜8・dedup-259.md）を反映した。
  同じ報告の版違い 5 件を『追加候補』から外して『寄せた記録』シートに移し、両方の判定シートに「同じ研究の群」の列、
  判定者 1 のファイルだけに「内容の群」の列を足す（判定者 2 のファイルに出すかは研究者の確認待ち・判断 8）。
  ★ candidate_records() は追加候補の評価版と共有なので 225 件のまま返し、外すのは build() の中だけ。

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
    "除外理由": "E1,E2,E3,E4,E5,E6,E7",  # ★ 2026-10-01: E7（言語）を足した（../20261001-ai-fatigue-protocol-cont 判断 1）
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
               "追加候補": {"事実のファイルでの表記", "題名（書誌の記録）", "掲載誌", "要点（事実のファイルの記述）"},
               "寄せた記録": {"題名（書誌の記録）", "掲載誌"}}

# ---------------------------------------------------------------- 間引き（../20260930-ai-fatigue-protocol の判断 3〜8）
PROTO = os.path.join(STEER, "20260930-ai-fatigue-protocol")
DEDUP_JSON = os.path.join(PROTO, "evidence", "dedup", "classification_2026-09-30_final.json")
# ★ 2026-10-01: 全 259 件を確かめた値（design.md §7.7・判断 9・10）。機械の分類（_2026-09-30_final.json）から差し替えた
CONTENT_JSON = os.path.join(PROTO, "evidence", "dedup", "content_groups_2026-10-01_checked.json")
DEDUP_MD = os.path.join(PROTO, "dedup-259.md")
KEY_RE = re.compile(r"(?<![A-Za-z0-9-])(?:AF\d{3}|S\d\d-\d\d)(?![0-9])")
GROUP_HEADER = "同じ研究の群"
CONTENT_HEADER = "内容の群（機械の分類・並べ替えのため・判定の材料ではない）"
GROUP_WIDTH, CONTENT_WIDTH = 34, 22
MERGED_HEADERS = ["寄せた記録", "版", "題名（書誌の記録）", "年", "掲載誌", "DOI", "代表（残した記録）", "一致点"]
MERGED_WIDTHS = [11, 22, 50, 6, 22, 26, 13, 60]
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
    for p in sorted(glob.glob(os.path.join(EVID_PREV, "S-0[45]", "*_extraction_*.tsv"))):  # ★ 並びを固定（setdefault で先の記録が勝つ）
        with open(p, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r.get("doi"):
                    idx.setdefault(r["doi"].lower(), (r["title"], r["year"], r["journal"]))
                by_tsv[r["id"]] = (r["title"], r["year"], r["journal"])
    meta = json.load(open(os.path.join(EVID_PREV, "S-02", "s02_meta_2026-09-29.json"), encoding="utf-8"))
    for r in meta["records"]:
        idx.setdefault(r["doi"].lower(), (r["title"], (r.get("issued") or [None])[0], r.get("container", "")))
    for p in (sorted(glob.glob(os.path.join(EVID_PREV, "S-12", "*_results_*.json")))
              + sorted(glob.glob(os.path.join(TASK, "evidence", "S-1*", "*_results_*.json")))
              + sorted(glob.glob(os.path.join(TASK, "evidence", "B9", "*_screen_*.json")))  # B9 の採択研究のふるい（判断 15）
              + sorted(glob.glob(os.path.join(EVID_PREV, "S-04", "*_results_*.json")))  # S-04 の検索の記録（B10・B12 の書誌・判断 17）
              + sorted(glob.glob(os.path.join(EVID_PREV, "S-08", "*_results_*.json")))  # S-08 の記録（S08-01〜03・2026-09-30）
              + sorted(glob.glob(os.path.join(TASK, "evidence", "bib", "*_bib_*.json")))):  # 検索に当たらなかった種文献の書誌（判断 20）
        d = json.load(open(p, encoding="utf-8"))
        for run in d.get("runs", []):
            for r in run.get("records", []):
                title = r.get("title") or ""
                if not title:
                    continue  # ★ 題名の無い記録（J-STAGE の title_ja/title_en の形）が、後の記録の題名を塞がないように（2026-09-30）
                if r.get("doi"):
                    idx.setdefault(r["doi"].lower(), (title, r.get("year"), r.get("journal", "")))
                # DOI の無い記録は、記録の鍵（Europe PMC の PPR など）と CiNii の crid でも引けるようにする（candidates.py の bib_key）
                if r.get("key") and not str(r["key"]).startswith("10."):
                    idx.setdefault(str(r["key"]).lower(), (title, r.get("year"), r.get("journal", "")))
                m = re.match(r"https://cir\.nii\.ac\.jp/crid/(\d+)$", r.get("url") or "")
                if m:
                    idx.setdefault("crid:" + m.group(1), (title, r.get("year"), r.get("journal", "")))
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


def md_table(path, heading):
    """見出し（番号から始まる。ちょうど 1 つ）の直後の最初の表を、列の見出し → 値の辞書の列で返す（次の見出しで止まる）。"""
    lines = open(path, encoding="utf-8").read().split("\n")
    heads = [i for i, l in enumerate(lines) if l.startswith("#") and l.lstrip("#").strip().startswith(heading)]
    if len(heads) != 1:
        raise ValueError(f"{path}: 節『{heading}』がちょうど 1 つではない（{len(heads)}）")
    header, rows = None, []
    for l in lines[heads[0] + 1:]:
        if l.startswith("#"):
            break
        if not l.startswith("|"):
            if rows:
                break  # 最初の表だけ
            continue
        if SEP_RE.match(l):
            continue
        v = [strip_md(x).replace("★", "").strip() for x in cells(l)]
        if header is None:
            header = v
            continue
        if len(v) != len(header):
            raise ValueError(f"{path} {heading}: 列の数が見出しと違う: {l[:40]}")
        rows.append(dict(zip(header, v)))
    if not rows:
        raise ValueError(f"{path} {heading}: 表が無い")
    return rows


def one_key(text, where):
    keys = KEY_RE.findall(text)
    if len(keys) != 1:
        raise ValueError(f"dedup-259.md {where}: 記録の鍵がちょうど 1 つではない: {text}")
    return keys[0]


def dedup():
    """間引きの結果（dedup-259.md・decisions.md 判断 3〜7）。
    merged: 寄せた鍵 → (代表の鍵, 一致点, 版)。groups: 残る行の鍵 → 「同じ研究の群」の列の文。content: 鍵 → 内容の群。
    ★ 分けの記録（JSON）と、判定者に写す文（dedup-259.md の表）の鍵が一致しなければ止まる。"""
    pairs = json.load(open(DEDUP_JSON, encoding="utf-8"))["pairs"]
    merged = {}
    for p in pairs:
        if p["cls"] != "同じ報告":
            continue
        rep = p["representative"]
        if rep not in (p["a"], p["b"]):
            raise ValueError(f"同じ報告の代表が組の中に無い: {p['a']}・{p['b']}")
        drop = p["b"] if rep == p["a"] else p["a"]
        if drop.startswith("AF") or drop in merged:
            raise ValueError(f"DB の行・2 回目は寄せない: {drop}")  # design.md §7.3: DB の行は消さない
        merged[drop] = rep
    if set(merged) & set(merged.values()):
        raise ValueError("代表が別の組で寄せられている")
    md = {}
    for r in md_table(DEDUP_MD, "2. "):
        ver = re.fullmatch(r"\S+（(.+)）", r["寄せる記録"])  # 例: S04-44（medRxiv の前刷り）
        if ver is None:
            raise ValueError(f"dedup-259.md §2: 寄せる記録に版の括弧が無い: {r['寄せる記録']}")
        md[one_key(r["寄せる記録"], "§2")] = (one_key(r["代表（残す）"], "§2"), r["一致点"], ver.group(1))
    if {k: v[0] for k, v in md.items()} != merged:
        raise ValueError("dedup-259.md §2 の寄せる記録・代表が JSON と違う")
    raw = {}
    for p in pairs:
        if p["group"]:
            raw.setdefault(p["group"], set()).update((p["a"], p["b"]))
    texts = {}
    for r in md_table(DEDUP_MD, "3. "):
        texts[r["群"]] = (r["記録"], f"{r['群']}: {r['記録']} ／ 一致点: {r['一致点（事実）']} ／ 違う点: {r['違う点（事実）']}")
    for r in md_table(DEDUP_MD, "3.1 "):
        texts[r["群"]] = (r["記録"], f"{r['群']}（要確認）: {r['記録']} ／ 分からないこと: {r['何が分からないか']}")
    if set(texts) != set(raw):
        raise ValueError(f"dedup-259.md の群が JSON と違う: {sorted(set(texts) ^ set(raw))}")
    groups = {}
    for g, keys in sorted(raw.items()):
        shown = {merged.get(k, k) for k in keys}
        if set(KEY_RE.findall(texts[g][0])) != keys | shown:
            raise ValueError(f"dedup-259.md の {g} の記録が JSON と違う")
        for k in shown:
            if k in groups:
                raise ValueError(f"{k} が 2 つの群にある")
            groups[k] = texts[g][1]
    content = {k: v["group"] for k, v in json.load(open(CONTENT_JSON, encoding="utf-8"))["groups"].items()}
    return {"merged": md, "groups": groups, "content": content}


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
        ["このファイル", f"判定者 {judge} が、AI 疲労の文献を独立に判定するためのファイル。書誌・リンク・事実の要点・間引きの事実・判定の基準だけを載せ、"
                        "AI が出した判定や評価は載せていない。"
                        + ("（『内容の群』の列は機械の分類で、判定や評価ではない。）" if judge == 1 else "")],
        ["判定者", f"判定者 {judge}"],
        # ★ 2026-10-01: 判定の前に基準の 2 つを足した（『はじめに』では判定の語を使えないので語を使わずに書く）
        ["この版（2026-10-01）", "判定を始める前に、『判定基準』シートに 2 つを足した: 尺度の原著の読み方の行と、"
                               "本文が英語・日本語以外の記録の扱い（記入の選択肢も 1 つ増えた）。"],
    ]
    # ★ 2026-09-30: 追加候補にも AI の評価版を作り、判定者 1 は判定の前に読む（研究者の決定・decisions.md 判断 21）。
    #   判定者 2 は、追加候補の評価版も開かない。評価版のファイル名は語の検査に当たらない形（先頭の部分）で書く。
    cand_file = "追加候補の評価版ファイル（ファイル名が AI_fatigue_candidates_AI_appraisal で始まる xlsx）"
    if judge == 1:
        rows.append(["判定の前に読んだもの（記録）", "判定者 1 は、判定の前に、元の DB 34 件について評価版ファイルの AI の評価を読んでいる。"
                                               f"追加候補についても、判定の前に、{cand_file}を判断材料として読んだ（どちらも 2026-09-30 に研究者が決め、記録した）。"])
        rows.append(["追加候補について", f"『追加候補』シートの文献の AI の評価は、{cand_file}にあり、このファイルには載せていない。"
                                     "評価版は、サーヴェイの AI の案（元の案のファイルの場所も評価版に書いてある）を 1 件ずつ見直したもので、"
                                     "元の案のファイルと評価版ファイルの『検索漏れ候補』シートも同じ種類の AI の出力にあたる。"
                                     "評価版は間引きの前に作ったもので作り直していないので、『寄せた記録』の 5 件の行が残っている"
                                     "（このファイルではその 5 件を判定しない）。"])
    else:
        rows.append(["判定の前に開かないもの", "判定が終わるまで、評価版ファイル（AI の評価のシートを足した xlsx）の AI の評価のシートと、元の DB の『AI…』のシート、"
                                        f"{cand_file}、研究のメモの一次確認のファイル（memo-issues.md）を開かない。開いた場合は、判定の記録にそのことを書く。"])
        rows.append(["追加候補について", "『追加候補』シートの文献には、AI の出力（サーヴェイの AI の案・評価版ファイルの『検索漏れ候補』シート・"
                                     f"{cand_file}）が別にあるが、このファイルには載せていない。判定が終わるまで、それらのファイルを開かない。"])
    rows += [
        ["間引き（2026-09-30）", "同じ論文の版違い（前刷りと雑誌の版・リポジトリの写し）の 5 件を、判定の前に 1 件に寄せ、『追加候補』から外した"
                              "（225 件 → 220 件）。寄せた記録と、残した記録（代表）・一致点は『寄せた記録』シートにある。残す記録は、"
                              "雑誌の版 ＞ 会議録 ＞ 前刷り ＞ リポジトリの写しの順で選んだ（元の DB の行は消していない）。"
                              "同じ標本の別の論文と、内容が近い研究は消していない。"],
        ["『同じ研究の群』の列", "著者が重なり、標本の N・国・対象・収集の時期のうち 2 つ以上が一致するなど、同じ標本の別の論文である可能性を示す"
                             "事実がある記録を、群（G01〜G11）で結んだ（行は消していない）。U1・U2 は、抄録に標本の情報が無く確かめられなかった組"
                             "（要確認）。列には一致点と違う点の事実だけを書いた。同じ標本として扱うかは、判定者が本文で確かめて決める"
                             "（『判定基準』シートの「同じ研究の群と版違い」）。"],
    ]
    if judge == 1:
        rows.append(["『内容の群』の列", "対象｜AI の種類｜デザイン（一次研究でない記録は「レビュー等」）。題名・抄録の語による機械の分類と、"
                                     "別の読み手（AI）の分類を 259 件すべてで突き合わせ、4 つの軸がどれか違った 98 件は、このファイルを作った AI が"
                                     "題名・抄録を読んで決めた（一致した記録から無作為に 20 件を読み、間違いは無かった）。"
                                     "元の DB の 34 件は、DB の『研究情報』と『分類』（尺度・理論・既存レビュー）も使った。"
                                     "AI の種類は、参加者が使う・監督する・評価する AI（研究者が分析にだけ AI を使った研究は「不明」）。"
                                     "並べ替え・見比べのためのもので、判定の材料ではなく、間違いがありうる。"])
    rows += [
        ["間引きの記録", "間引きの手順・件数・調べて別の研究と分かった組は、研究の記録（dedup-259.md）にある。判定者 1・2 とも読んでよい。"],
        ["進め方", "『判定基準』シートの手順に従う。黄色の欄だけを入力する（ドロップダウンから選ぶ）。書誌と要点の欄は変えない。"],
        ["本文の入手", "有料の本文は入手しない（2026-09-30 の研究者の決定）。『本文の入手（OpenAlex）』の欄は OpenAlex の記録（2026-09-30）で、"
                    "無料の版が無いものは本文を読めない。"],
        ["要点の欄", "『追加候補』の要点は、サーヴェイの事実のファイルの記述をそのまま機械で写したもの（抄録・本文に書いてあることだけ）。"
                  "判定の根拠は、リンク先の抄録・本文で確かめる。"],
        ["終わったら", "このファイルを保存して渡す。2 人の判定がそろったら突き合わせる。"],
    ]
    return rows


CRITERIA = [
    ["基準の版", "評価プロトコル v1.0（2026-09-28 固定）に、2026-09-30 の範囲の決定（言語を含む）と、"
              "2026-10-01 の読み方の明文化（尺度の原著）を足したもの。"],
    ["問い（PCC）", "人が AI を使う・監督する・評価することに関連する疲労について、何が定義・測定・観察されているか（スコーピング型）。"
                "P＝AI を使う・監督する・評価する人。C＝疲労（認知・情動・身体・動機／行動面の消耗、exhaustion、weariness、燃え尽きのような枯渇）"
                "を定義・測定・質的に分析し、AI の利用・監督との関係の中で扱うもの。Context＝教育・職場・消費・研究など問わない。"
                "期間＝オンライン公開が 2026-09-28 以前（追加候補は 2026-09-30 の検索まで）。"],
    ["2026-09-30 の範囲の決定 (a)", "AI の導入・利用を操作・比較し、使う人の疲労・消耗・燃え尽きを測った研究は、デザイン（無作為化・非無作為化・前後比較）と"
                                 "結果の向きを問わず C に当たりうる。"],
    ["2026-09-30 の範囲の決定 (b)", "自動化の監視の研究は、論文が対象の系を AI・機械学習と書く場合だけ P に当たる。従来の自動化だけの研究は E3。"],
    ["手順 1: 題名・抄録段", "リンク先の題名・抄録を読み、P と C に当たる可能性のある一次研究は『含める』（迷ったら含める＝全文段へ回す）。"
                          "一次研究でない（レビュー・尺度の原著・方法論・訂正通知）は『除外』＋ E4（DB からは消さず背景として残す。"
                          "尺度の原著の読み方は下の行）。"],
    ["手順 2: 全文段", "『含める』『保留』にした件は本文を読み、全文段を選ぶ。本文を読めなかった件は『保留』＋ E6、読んだ範囲に『抄録』"
                    "（本文の言語が英語・日本語以外と分かっていれば E7。下の除外理由）。"],
    ["手順 3: 中心範囲の段", "中心-A＝疲労を AI に帰属させて定義・測定している（項目文・定義・質問文に AI が出てくる、または AI 疲労の語りを分析する）。"
                          "中心-B＝疲労・消耗・燃え尽きを測るが、構成概念は一般的（項目に AI が出ない）で、AI の利用や AI 由来の要求と関係づけている。"
                          "境界（保留）＝規則だけでは決まらない。背景（E2）＝疲労を測っていない AI 利用の研究。背景（E4）＝一次研究でない。"],
    # ★ 2026-10-01: E7 の当て方に、E6 との順を明文にした（../20261001-ai-fatigue-protocol-cont 判断 6）
    ["除外理由", "E1＝AI が人の疲労を検出・予測する道具であるだけ／E2＝疲労を定義・測定・質的分析していない（認知負荷・不安・過信だけなど）／"
             "E3＝疲労を測るが AI の利用・監督と関係づけていない／E4＝一次研究でない（尺度の原著の読み方は下の行）／"
             "E5＝重複出版・同じ標本・版違い／"
             "E6＝全文が手に入らず判定できない（→ 保留）／"
             "E7＝本文の言語が英語・日本語以外（2026-09-30 の決定。題名・抄録の言語だけでは決めず、本文の言語が分かった段で選ぶ。"
             "論文のページ・書誌に本文の言語が書いてあれば題名・抄録段で、そうでなければ全文段で。英語・日本語の版が別にあれば、"
             "その版で判定する。ほかの除外理由 E1〜E5 にも当たるときは、その理由を選ぶ。"
             "本文の言語が分かっていれば、本文が手に入らなくても E6 の保留にせず E7 を選ぶ）。"
             "この表に無い理由で除外しない。"],
    # ★ 2026-10-01: v1.0 の「尺度の原著」の読み方を明文にした（元の DB の定義 r7・r10・../20261001-ai-fatigue-protocol-cont 判断 1）
    ["E4 の『尺度の原著』（2026-10-01）", "その記録の主な寄与が、AI の利用・監督に関わる疲労の尺度でない尺度（一般の疲労・ビデオ会議の疲労・"
                                      "AI への不安・認知負荷・テクノストレスなど）の開発・検証であるものを指す。標本の有無は問わない。"
                                      "AI の利用・監督に関わる疲労の尺度（項目文・定義に AI が出る疲労・消耗の尺度や下位尺度、または AI の利用者・"
                                      "AI の利用の場面で開発・検証した疲労・消耗の尺度）の研究は、E4 に当てず、一次研究として P・C で判定する。"],
    ["同じ研究の群と版違い（2026-09-30）", "版違い（同じ論文の前刷りと雑誌の版など）の 5 件は、判定の前に 1 件に寄せた（『寄せた記録』シート。"
                                       "寄せた記録は判定しない）。『同じ研究の群』の列は、同じ標本の別の論文である可能性を示す事実で、"
                                       "E5 に当たるかは判定者が本文で確かめて決める。"],
    ["注意", "研究デザインや報告の水準は、範囲の判断に使わない（引用の範囲で扱う）。結果の向き（疲労が増える・減る）で範囲を変えない。"],
    ["根拠メモ", "選んだ理由を短く書く（例: 項目文に AI が入る・疲労は一般の尺度・本文は有料で読めない）。"],
]


def load_oa():
    if not os.path.exists(OA_JSON):
        sys.exit(f"OpenAlex の記録が無い（先に fetch_oa.py を回す）: {OA_JSON}")
    oa = {}
    for p in ([OA_JSON] if os.environ.get("JUDGE_OA_JSON") else sorted(glob.glob(OA_GLOB))):
        oa.update({k.lower(): v for k, v in json.load(open(p, encoding="utf-8"))["records"].items()})
    return oa


def candidate_records(oa):
    """追加候補の 1 件ずつの書誌と要点（判定者用ファイルと、追加候補の評価版〈../20260930-ai-fatigue-candidates-appraisal〉で共通）。"""
    idx, by_tsv = bib_index()
    out = []
    for c in CAND.CANDIDATES:
        e = extract(c)
        doi = e["doi"]
        t = idx.get(doi.lower()) if doi else None
        if t is None and c.get("tsv_id"):
            t = by_tsv.get(c["tsv_id"])
        if t is None and c.get("bib_key"):
            t = idx.get(c["bib_key"].lower())
        title, year, journal = t if t else ("", "", "")
        src = " ／ ".join(dict.fromkeys(tag(p, s) for p, s, _ in c["refs"]))
        out.append(dict(cid=c["cid"], src=src, label=e["label"], title=title, year=year, journal=journal, doi=doi,
                        oa=oa_label(oa, doi), points=e["points"]))
    return out


def build(judge):
    if sha256(DB_XLSX) != DB_SHA:
        sys.exit(f"元の DB の SHA-256 が固定値と違う: {DB_XLSX}")
    oa = load_oa()
    dd = dedup()
    db = openpyxl.load_workbook(DB_XLSX, data_only=True)["文献DB"]
    wb = openpyxl.Workbook()
    text_sheet(wb, "はじめに", "AI 疲労 文献 DB｜判定者用ファイル", "黄色の欄だけを入力する。", intro_rows(judge), first=True)
    text_sheet(wb, "判定基準", "判定基準（評価プロトコル v1.0 ＋ 2026-09-30 の範囲の決定 ＋ 2026-10-01 の読み方）",
               "判定者 1・2 で共通の基準。", CRITERIA)

    # 間引きの列（書誌・要点と記入欄の間）。★ 内容の群は判定者 1 だけ（判断 8）
    extra = [GROUP_HEADER] + ([CONTENT_HEADER] if judge == 1 else [])
    extra_w = [GROUP_WIDTH] + ([CONTENT_WIDTH] if judge == 1 else [])

    def extra_vals(key):
        if key not in dd["content"]:
            raise ValueError(f"内容の群に {key} が無い")
        return [dd["groups"].get(key)] + ([dd["content"][key]] if judge == 1 else [])

    # DB 34 件
    ws = wb.create_sheet("判定シート")
    headers = DB_HEADERS + extra + INPUT_HEADERS
    widths = DB_WIDTHS + extra_w + INPUT_WIDTHS
    rows, ids = [], []
    for r in range(5, 39):
        v = [db.cell(r, c).value for c in range(1, 15)]
        ids.append(v[0])
        doi = v[7] if v[7] and str(v[7]).startswith("10.") else None
        rows.append([v[0], v[4], v[5], v[3], v[6], v[8], v[7], v[10], oa_label(oa, doi)] + extra_vals(v[0]) + [None] * len(INPUT_HEADERS))
    header_block(ws, "判定シート｜元の DB 34 件", "DOI・URL から論文のページを開く。選択肢は『判定基準』シート。", len(headers))
    put_table(ws, headers, widths, rows)
    ws.row_dimensions[4].height = max(36, row_height(headers, widths))  # 長い列の見出し（put_table は評価版と共有なので変えない）
    last = 4 + len(rows)
    for r in range(5, last + 1):
        d = ws.cell(r, 7).value
        link(ws.cell(r, 7), doi_url(d) if d and str(d).startswith("10.") else None)
        link(ws.cell(r, 8), ws.cell(r, 8).value)
    input_columns(ws, headers, len(DB_HEADERS) + len(extra) + 1, last, "JudgeDB")

    # 追加候補（★ 同じ報告の版違いを外す・判断 3）
    recs = candidate_records(oa)
    keep = [m for m in recs if m["cid"] not in dd["merged"]]
    if len(recs) - len(keep) != len(dd["merged"]) or any(v[0] not in {m["cid"] for m in keep} for v in dd["merged"].values()):
        raise ValueError("寄せる記録・代表が追加候補に無い")
    wc = wb.create_sheet("追加候補")
    cheaders = CAND_HEADERS + extra + INPUT_HEADERS
    cwidths = CAND_WIDTHS + extra_w + INPUT_WIDTHS
    crows = []
    for m in keep:
        crows.append([m["cid"], m["src"], m["label"], m["title"], m["year"], m["journal"], m["doi"] or "", m["oa"], m["points"]]
                     + extra_vals(m["cid"]) + [None] * len(INPUT_HEADERS))
    header_block(wc, f"追加候補｜サーヴェイで見つかった DB に無い文献（{len(crows)} 件）",
                 f"DB の行には足していない。版違いの {len(dd['merged'])} 件は『寄せた記録』シートに移した。"
                 "要点はサーヴェイの事実のファイルの記述の写し。判定はリンク先の抄録・本文で行う。", len(cheaders))
    put_table(wc, cheaders, cwidths, crows)
    wc.row_dimensions[4].height = max(36, row_height(cheaders, cwidths))
    clast = 4 + len(crows)
    for r in range(5, clast + 1):
        d = wc.cell(r, 7).value
        link(wc.cell(r, 7), doi_url(d) if d else None)
    input_columns(wc, cheaders, len(CAND_HEADERS) + len(extra) + 1, clast, "JudgeExtra")

    # 寄せた記録（候補の並びの順）
    wm = wb.create_sheet("寄せた記録")
    mrows = []
    for m in recs:
        if m["cid"] in dd["merged"]:
            rep, match, ver = dd["merged"][m["cid"]]
            mrows.append([m["cid"], ver, m["title"], m["year"], m["journal"], m["doi"] or "", rep, match])
    header_block(wm, f"寄せた記録｜同じ論文の版違い（{len(mrows)} 件）",
                 "判定の前に 1 件に寄せ、『追加候補』から外した記録。代表（残した記録）の行で判定する。", len(MERGED_HEADERS))
    put_table(wm, MERGED_HEADERS, MERGED_WIDTHS, mrows)
    jd = MERGED_HEADERS.index("DOI") + 1
    for r in range(5, 5 + len(mrows)):
        d = wm.cell(r, jd).value
        link(wm.cell(r, jd), doi_url(d) if d else None)

    # 集計
    agg = []
    for sheet, n_last, n_in in (("判定シート", last, len(DB_HEADERS) + len(extra)), ("追加候補", clast, len(CAND_HEADERS) + len(extra))):
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
