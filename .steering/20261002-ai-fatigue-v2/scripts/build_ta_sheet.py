"""記入表 1（抄録段の 1 回目・AI なし）を元の資料から作る（design.md §5）。

元の資料（読むだけ）: 判定者用ファイルの『判定基準』『追加候補』・前のタスクのログ（判定済みの 8 件を除く）・
                      前のタスクの `search-records.json`（読む一覧 46 件）・抄録（git の外）と `abstract-status.json`。
★ 評価版（AI の予備判定）は読まない。
★ Downloads の記入表が最後に書いた SHA-256（archive/ta-sheets-sha256.txt の sheet1）と違えば止まる（記入が始まった可能性）。
使い方: uv run --with openpyxl python build_ta_sheet.py [--dry-run]
"""
import json
import os
import re
import shutil
import sys
import tempfile

import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

import common as C

TITLE = "AI 疲労 文献 DB｜追加候補の題名・抄録段の記入表 1（判定者 1）"
VERDICTS = ["含める", "除外", "保留"]
ECODES = ["E1", "E2", "E3", "E4 背景（レビュー・尺度の原著・理論）", "E4 方法論", "E4 訂正通知", "E5", "E7"]
ADD = ["足す", "足さない"]

CAND_HEADER = ["順", "候補番号", "題名", "年", "掲載誌", "DOI（リンク）", "抄録（原文）", "抄録の出どころ",
               "要点（事実のファイルの記述）", "同じ研究の群", "内容の群（並べ替えのため・判定の材料ではない）",
               "本文の入手（OpenAlex）", "判定【記入】", "除外理由【記入】", "メモ【記入】"]
SEARCH_HEADER = ["順", "記録", "題名", "年", "種別（API の記録）", "DOI（リンク）", "抄録（原文）", "抄録の出どころ",
                 "本文の入手（OpenAlex）", "重なり", "候補に足す【記入】", "判定【記入】", "除外理由【記入】", "メモ【記入】"]
CAND_INPUT = (13, 14, 15)     # M・N・O
SEARCH_INPUT = (11, 12, 13, 14)  # K・L・M・N
HEADER_ROW = 4

# 内容の群の並べ方（対象者 → AI の種類 → デザイン）。★ 並びは読む順で、判定の材料ではない
POP = ["学生・学習者", "教員・研究者", "働く人（医療・教育の外）", "医療者", "消費者・一般の利用者", "不明"]
AI = ["生成 AI・対話", "AI 一般・導入", "意思決定支援・警報・予測", "記録支援・下書き", "不明"]
DESIGN = ["横断調査", "縦断", "比較（非無作為化・前後）", "無作為化", "実験・模擬", "質的", "不明"]

INTRO = [
    ("この表について", "追加候補の題名・抄録段（判定基準の手順 1）の 1 回目を、判定者 1 が記入する表です。研究者・判定者 2 には渡しません"
                       "（判定者 1 の作業用。抄録の原文を含みます）。"),
    ("記入する列", "黄色の見出しの列だけです（『追加候補』の M〜O 列・『探索の記録』の K〜N 列）。ほかのセルは変えないでください"
                   "（読み込むときに、作ったときと同じかを確かめます）。"),
    ("判定（手順 1）", "P と C に当たる可能性のある一次研究は「含める」。迷ったら「含める」（全文段で本文を読みます）。"
                       "抄録だけでは決められないときは「保留」（これも全文段へ回します）。P・C に当たらないことが抄録で分かるときは「除外」と除外理由。"),
    ("一次研究でないもの", "レビュー・尺度の原著・理論・方法論・訂正通知は「除外」と E4 の区分（背景／方法論／訂正通知）。"
                           "DB からは消さず、背景などとして残ります（尺度の原著の読み方は『判定基準』の E4 の行）。"),
    ("除外理由", "E1＝AI が人の疲労を検出・予測する道具であるだけ／E2＝疲労を定義・測定・質的分析していない／"
                 "E3＝疲労を測るが AI の利用・監督と関係づけていない／E4＝一次研究でない（区分を選ぶ）／E5＝重複出版・同じ標本・版違い／"
                 "E7＝本文の言語が英語・日本語以外。E6（全文が手に入らない）は全文段で使うので、この表では選びません。"),
    ("メモ", "選んだ理由を短く（任意）。全文段で確かめたいことも書けます。"),
    ("探索の記録", "レビューを狙った探索で読んだ 46 件です。「候補に足す」を選び、足すときだけ同じ行で判定してください"
                   "（足さない記録は判定・除外理由を空のまま。メモは書けます）。研究者の DB・追加候補と重なる 3 件（灰色）は記入しません。"),
    ("この表に無いもの", "記録ごとの予備判定・用途判定・中心範囲の段（評価版の値）は載せていません。抄録段で除外にした記録は、"
                         "記入の後に 2 枚目の表でそれらを見ていただきます。含める・保留にした記録は、全文段の 1 回目の後に見ていただきます。"),
    ("抄録", "無料の学術 API（Semantic Scholar・Europe PMC・OpenAlex・Crossref）から 2026-10-02 に取った原文です。"
             "「抄録の出どころ」の列に API の名前があります。「抄録なし」の記録は DOI のリンクから読めます。"),
    ("並び", "『追加候補』は内容の群（対象者 → AI の種類 → デザイン）でまとめ、同じ研究の群を隣に置いています。"
             "並びは読みやすさのためで、判定の材料ではありません。"),
    ("保存したら", "上書き保存して、チャットで「記入表 1 を保存した」と伝えてください。途中で止めても構いません"
                   "（読み込むのは全部を書き終えてからです）。"),
]

YELLOW = PatternFill("solid", fgColor="FFF2CC")
GRAY = PatternFill("solid", fgColor="D9D9D9")
WRAP = Alignment(wrap_text=True, vertical="top")


def clean(v):
    """openpyxl が書けない制御文字を落とす（★ 検査器も同じ規則で比べる）。"""
    return ILLEGAL_CHARACTERS_RE.sub("", v) if isinstance(v, str) else v


def put(cell, v):
    """★ 先頭が = の文字列は式にしない（外の文が式になるのを防ぐ・前のタスクの判断 10）。"""
    cell.value = clean(v)
    if isinstance(cell.value, str) and cell.value.startswith("="):
        cell.data_type = "s"
    return cell


def oa_label(oa):
    if not oa:
        return "未確認"
    return "無料の版なし" if oa == "closed" else f"無料の版あり（{oa}）"


def group_id(s):
    m = re.match(r"\s*([GU]\d+)", s or "")
    return m.group(1) if m else None


def content_key(s):
    parts = [p.strip() for p in (s or "").split("｜")]
    while len(parts) < 3:
        parts.append("不明")
    def ix(lst, v):
        return lst.index(v) if v in lst else len(lst)
    return (ix(POP, parts[0]), ix(AI, parts[1]), ix(DESIGN, parts[2]))


def load():
    if C.sha256(C.JUDGE_FILE) != C.JUDGE_FILE_SHA256:
        sys.exit("判定者用ファイルの SHA-256 が記録と違う")
    wb = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    crit = [list(r) for r in wb["判定基準"].iter_rows(values_only=True)]
    rows = list(wb[C.JUDGE_SHEET].iter_rows(values_only=True))
    data = [r for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]]
    if len(data) != C.N_CANDIDATES:
        sys.exit(f"追加候補が {len(data)} 行（220 のはず）")
    judged = {json.loads(l)["item"] for l in open(C.PREV_LOG, encoding="utf-8")}
    cands = [r for r in data if r[0] not in judged]
    recs = json.load(open(C.SEARCH_RECORDS, encoding="utf-8"))
    search = sorted((r for r in recs if r["reading"] and re.fullmatch(r"R\d\d", r["reading"])), key=lambda r: r["reading"])
    abstracts = json.load(open(C.ABSTRACTS, encoding="utf-8"))
    status = json.load(open(C.ABSTRACT_STATUS, encoding="utf-8"))
    return crit, cands, search, abstracts, status


def order_cands(cands):
    """内容の群でまとめ、同じ研究の群を隣に置く。群の位置は群の中でいちばん前の記録の位置。"""
    key = {r[0]: (content_key(r[10]), r[0]) for r in cands}
    gmin = {}
    for r in cands:
        g = group_id(r[9])
        if g:
            gmin[g] = min(gmin.get(g, key[r[0]]), key[r[0]])
    def k(r):
        g = group_id(r[9])
        return (gmin[g], g, r[0]) if g else (key[r[0]], "", r[0])
    return sorted(cands, key=k)


def abstract_of(i, abstracts, status):
    st = status.get(i) or {}
    t = (abstracts.get(i) or {}).get("text") or ""
    if st.get("chars") and t:
        return t, st.get("source")
    return "", "抄録なし（DOI のリンクから読めます）" if st.get("doi") else "抄録なし（DOI なし・題名と要点だけ）"


def build():
    crit, cands, search, abstracts, status = load()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "はじめに"
    put(ws["A1"], TITLE).font = Font(bold=True, size=12)
    put(ws["A2"], "作成: 2026-10-02 ／ 判定基準: 判定者用ファイルの『判定基準』と同じ版（このファイルの『判定基準』に写しがあります）")
    put(ws["A4"], "項目").font = Font(bold=True)
    put(ws["B4"], "説明").font = Font(bold=True)
    for n, (k, v) in enumerate(INTRO, 5):
        put(ws.cell(n, 1, None), k).alignment = WRAP
        put(ws.cell(n, 2, None), v).alignment = WRAP
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 110
    fit_rows(ws, {"A": 18, "B": 110}, 5)

    wc = wb.create_sheet("判定基準")
    for r, row in enumerate(crit, 1):
        for c, v in enumerate(row, 1):
            if v is not None:
                put(wc.cell(r, c), v).alignment = WRAP
    wc.column_dimensions["A"].width = 28
    wc.column_dimensions["B"].width = 110

    # 追加候補
    wa = wb.create_sheet("追加候補")
    put(wa["A1"], "追加候補（未判定の 213 件）｜題名・抄録段の 1 回目").font = Font(bold=True, size=12)
    put(wa["A2"], "記入するのは黄色の見出しの列（M 判定・N 除外理由・O メモ）だけです。除外のときは除外理由を選んでください。")
    for c, h in enumerate(CAND_HEADER, 1):
        cell = put(wa.cell(HEADER_ROW, c), h)
        cell.font = Font(bold=True)
        cell.alignment = WRAP
        if c in CAND_INPUT:
            cell.fill = YELLOW
    rows = order_cands(cands)
    for n, r in enumerate(rows, 1):
        rr = HEADER_ROW + n
        ab, src = abstract_of(r[0], abstracts, status)
        vals = [n, r[0], r[3], r[4], r[5], r[6], ab, src, r[8], r[9], r[10], r[7]]
        for c, v in enumerate(vals, 1):
            put(wa.cell(rr, c), v).alignment = WRAP
        if r[6]:
            wa.cell(rr, 6).hyperlink = "https://doi.org/" + str(r[6])
        for c in CAND_INPUT:
            wa.cell(rr, c).fill = YELLOW
    last = HEADER_ROW + len(rows)
    dv1 = DataValidation(type="list", formula1='"' + ",".join(VERDICTS) + '"', allow_blank=True)
    dv2 = DataValidation(type="list", formula1='"' + ",".join(ECODES) + '"', allow_blank=True)
    wa.add_data_validation(dv1)
    wa.add_data_validation(dv2)
    dv1.add(f"M{HEADER_ROW + 1}:M{last}")
    dv2.add(f"N{HEADER_ROW + 1}:N{last}")
    cw = dict(zip("ABCDEFGHIJKLMNO", (5, 9, 40, 6, 18, 16, 90, 14, 50, 22, 22, 14, 10, 16, 30)))
    for col, w in cw.items():
        wa.column_dimensions[col].width = w
    fit_rows(wa, cw, HEADER_ROW + 1)
    wa.freeze_panes = f"D{HEADER_ROW + 1}"

    # 探索の記録
    wsr = wb.create_sheet("探索の記録")
    put(wsr["A1"], "探索の記録（レビューを狙った探索の読む一覧 46 件）｜候補に足すか・題名・抄録段の 1 回目").font = Font(bold=True, size=12)
    put(wsr["A2"], "記入するのは黄色の見出しの列（K〜N）だけです。足さない記録は L・M を空のままにしてください（N メモは書けます）。灰色の 3 行は記入しません。")
    for c, h in enumerate(SEARCH_HEADER, 1):
        cell = put(wsr.cell(HEADER_ROW, c), h)
        cell.font = Font(bold=True)
        cell.alignment = WRAP
        if c in SEARCH_INPUT:
            cell.fill = YELLOW
    input_rows = []
    for n, r in enumerate(search, 1):
        rr = HEADER_ROW + n
        rid = r["reading"]
        ab, src = abstract_of(rid, abstracts, status)
        doi = r["key"] if r["key"].startswith("10.") else None
        ov = C.SEARCH_OVERLAP.get(rid)
        ov_label = (f"研究者の DB の {ov}（記入しない）" if ov and ov.startswith("AF") else
                    f"追加候補の {ov}（判定済み・記入しない）" if ov else "")
        vals = [n, rid, r["title"], r["year"], r["type"], doi, ab, src, oa_label(r["oa"]), ov_label]
        for c, v in enumerate(vals, 1):
            put(wsr.cell(rr, c), v).alignment = WRAP
        if doi:
            wsr.cell(rr, 6).hyperlink = "https://doi.org/" + doi
        for c in SEARCH_INPUT:
            wsr.cell(rr, c).fill = GRAY if ov else YELLOW
        if ov:
            for c in range(1, len(SEARCH_HEADER) + 1):
                wsr.cell(rr, c).fill = GRAY
        else:
            input_rows.append(rr)
    dv3 = DataValidation(type="list", formula1='"' + ",".join(ADD) + '"', allow_blank=True)
    dv4 = DataValidation(type="list", formula1='"' + ",".join(VERDICTS) + '"', allow_blank=True)
    dv5 = DataValidation(type="list", formula1='"' + ",".join(ECODES) + '"', allow_blank=True)
    for dv, col in ((dv3, "K"), (dv4, "L"), (dv5, "M")):
        wsr.add_data_validation(dv)
        for rr in input_rows:
            dv.add(f"{col}{rr}")
    cw = dict(zip("ABCDEFGHIJKLMN", (5, 7, 40, 6, 22, 16, 90, 14, 16, 22, 10, 10, 16, 30)))
    for col, w in cw.items():
        wsr.column_dimensions[col].width = w
    fit_rows(wsr, cw, HEADER_ROW + 1)
    wsr.freeze_panes = f"D{HEADER_ROW + 1}"

    wb.properties.creator = "判定者 1"
    wb.properties.lastModifiedBy = "判定者 1"
    return wb


def fit_rows(ws, widths, first_row):
    """折り返しの行の高さを中身の長さから見積もって入れる（Excel は開いたときに広げないことがある）。全角は 2 字と数える。"""
    import math
    import unicodedata
    for r in range(first_row, ws.max_row + 1):
        lines = 1
        for col, w in widths.items():
            v = ws[f"{col}{r}"].value
            if v is None:
                continue
            n = sum(2 if unicodedata.east_asian_width(ch) in "WFA" else 1 for ch in str(v))
            lines = max(lines, math.ceil(n / max(w - 1, 1)))
        ws.row_dimensions[r].height = min(409, max(15, 13 * lines))


def recorded_sha():
    if not os.path.exists(C.TA_SHA_RECORD):
        return None
    for line in open(C.TA_SHA_RECORD, encoding="utf-8"):
        if line.startswith("sheet1 "):
            return line.split()[1]
    return None


def write_record(sha):
    lines = [l for l in (open(C.TA_SHA_RECORD, encoding="utf-8").read().splitlines() if os.path.exists(C.TA_SHA_RECORD) else [])
             if not l.startswith("sheet1 ")]
    lines.insert(0, f"sheet1 {sha} {os.path.basename(C.TA_SHEET1)}")
    with open(C.TA_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def main():
    dry = "--dry-run" in sys.argv
    wb = build()
    if dry:
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", prefix="ta1-dry-")
        os.close(fd)
        wb.save(tmp)
        print("dry-run:", tmp)
        return
    rec = recorded_sha()
    if os.path.exists(C.TA_SHEET1):
        cur = C.sha256(C.TA_SHEET1)
        if rec is None or cur != rec:
            sys.exit(f"Downloads の記入表 1 が最後に書いたものと違う（記入が始まった可能性）。止まる: {cur[:8]}… / 記録 {str(rec)[:8]}…")
    elif rec is not None:
        sys.exit("記録があるのに Downloads の記入表 1 が無い。止まる（消したなら記録の行を消してから）")
    fd, tmp = tempfile.mkstemp(suffix=".part", dir=C.DOWNLOADS, prefix=".tmp-ta1-")
    os.close(fd)
    try:
        wb.save(tmp)
        sha = C.sha256(tmp)
        if os.path.exists(C.TA_SHEET1) and C.sha256(C.TA_SHEET1) != rec:  # ★ 置き換えの直前に再照合
            sys.exit("置き換えの直前に記入表 1 が変わった。止まる")
        os.makedirs(os.path.dirname(C.TA_SHEET1_ORIG), exist_ok=True)
        shutil.copyfile(tmp, C.TA_SHEET1_ORIG)   # ★ 記入の後に比べる原本（git の外）
        os.replace(tmp, C.TA_SHEET1)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    write_record(sha)
    print(f"記入表 1: {sha}")


if __name__ == "__main__":
    main()
