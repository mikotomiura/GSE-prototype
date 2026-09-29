"""2026-09-28 の評価版に『読みやすさ』のシート 7 枚を足した 2026-09-29 版を作り、既存 26 シートの不変を検算する。
あわせて issues.md（repo の記録）を同じデータから書く。

使い方:
  python build_readable.py                 # archive/ に出力し、issues.md を書く
  python build_readable.py --copy-to DIR   # 出力を DIR にも複製する（研究者の Downloads など）
  python build_readable.py --mutate-test   # 既存シートに 1 セル書き込む変異を入れ、検算が止まることを確かめる（出力は置き換えない）
"""
import argparse
import hashlib
import importlib.util
import os
import re
import shutil
import sys
import tempfile

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.workbook.properties import CalcProperties
from openpyxl.workbook.views import BookView
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter as col

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
PREV = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive")
SRC = os.path.join(PREV, "AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx")
SRC_SHA = "a84c6e3fac93bdc765d179a6b5ccb7bfbff94b3945203f10ee8d36874ecaf091"
DST = os.path.join(TASK, "archive", "AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx")
ISSUES_MD = os.path.join(TASK, "issues.md")

sys.path.insert(0, HERE)
import papers_plain as PP  # noqa: E402
import issues_data as ID  # noqa: E402

# 前回の検算の道具（snapshot / structure / same_file / row_height）を再利用する
_spec = importlib.util.spec_from_file_location("bx", os.path.join(PREV, "scripts", "build_xlsx.py"))
bx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bx)

FONT = "Noto Sans CJK JP"  # ★ 元のワークブック（はじめに〜確認事項）の書体に合わせる
TEXT = "FF22364A"
INPUT = "FF175CD3"  # ★ 元の『スクリーニング』の記入欄の青
TAB = "FFEA580C"  # 今回の追加シート（前回の Claude シートは紫）
TITLE_FILL = PatternFill("solid", fgColor="FF143D48")
SUB_FILL = PatternFill("solid", fgColor="FFEAF4F6")
HEAD_FILL = PatternFill("solid", fgColor="FF0F766E")
SEC_FILL = PatternFill("solid", fgColor="FFFFF4E5")
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
WRAP_CENTER = Alignment(wrap_text=True, vertical="center")


def text_units(v):
    """列幅の単位でのおおよその文字幅（全角 ≈ 2、半角 ≈ 1.1）。前回の build_xlsx.py（作業版）と同じ見積もり。"""
    return sum(2.0 if ord(ch) > 0x2E7F else 1.1 for ch in str(v))


def row_height(values, widths):
    """折り返したときの行の高さ（pt）。★ openpyxl は行の高さを書かず、Excel は開いたときに自動で広げないため見積もって入れる。"""
    import math
    lines = 1
    for v, w in zip(values, widths):
        if v is None or v == "":
            continue
        per_line = max(1.0, w - 1.5)
        n = sum(max(1, math.ceil(text_units(part) / per_line)) for part in str(v).splitlines() or [""])
        lines = max(lines, n)
    return min(409, max(18, 15 * lines + 3))


def f(size=11, bold=False, color=TEXT, underline=None):
    return Font(name=FONT, size=size, bold=bold, color=color, underline=underline)


LINK = f(color="FF0563C1", underline="single")

ORDER = ["★まず読む", "論文ごとの要点", "証拠の地図", "調査不足とissue", "件数の目安と種文献", "照会の下書き", "用語の読み替え"]
CITE_COLORS = {  # 『どこまで引用してよいか』の色分け（条件付き書式）
    "中核として引用できる": "FFD1FAE5",
    "関連として引用できる（限界を併記）": "FFE8F5E9",
    "紹介まで（数値は引かない）": "FFFFF3CD",
    "全文を見るまで保留": "FFE3F2FD",
    "人間の判定待ち": "FFEDE7F6",
    "背景・方法の根拠として": "FFF1F3F5",
}
PRIO_COLORS = {"高": "FFFDE2E1", "中": "FFFFF3CD", "低": "FFF1F3F5"}
STATUS = "未着手,着手,完了,見送り"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for b in iter(lambda: fp.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def header_block(ws, title, subtitle, ncol, sub_h=48):
    last = col(ncol)
    ws["A1"] = title
    ws["A1"].font = f(bold=True, color="FFFFFFFF")
    ws["A1"].fill = TITLE_FILL
    ws["A1"].alignment = WRAP_TOP
    ws.merge_cells(f"A1:{last}1")
    ws["A2"] = subtitle
    ws["A2"].font = f()
    ws["A2"].fill = SUB_FILL
    ws["A2"].alignment = WRAP_TOP
    ws.merge_cells(f"A2:{last}2")
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = sub_h


def put(ws, r, c, v, font=None, fill=None, link=None, align=WRAP_TOP, text_only=True):
    cell = ws.cell(r, c, v)
    if text_only and isinstance(v, str) and v.startswith("="):
        cell.data_type = "s"  # 数式は明示した所だけに許す
    cell.font = font or f()
    if fill:
        cell.fill = fill
    if link:
        cell.hyperlink = Hyperlink(ref=cell.coordinate, location=link, display=str(v)) if not link.startswith("http") else link
        cell.font = LINK
    cell.alignment = align
    return cell


def table(ws, top, headers, widths, rows, name, formula_cols=(), links=None, input_cols=(), stripes=True, set_widths=True):
    """top 行に見出し、その下にデータを書き、Excel のテーブルにする。links = {(i, j): location}（i は 0 始まりの行）。"""
    links = links or {}
    for j, h in enumerate(headers, 1):
        c = ws.cell(top, j, h)
        c.font = f(bold=True, color="FFFFFFFF")
        c.fill = HEAD_FILL
        c.alignment = WRAP_CENTER
    ws.row_dimensions[top].height = 36
    for i, row in enumerate(rows):
        assert len(row) == len(headers), (name, i, len(row), len(headers))
        r = top + 1 + i
        for j, v in enumerate(row, 1):
            font = f(color=INPUT) if j in input_cols else None
            put(ws, r, j, v, font=font, link=links.get((i, j)), text_only=j not in formula_cols)
        ws.row_dimensions[r].height = row_height([str(x) for x in row], widths)
    if set_widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[col(j)].width = w
    ref = f"A{top}:{col(len(headers))}{top + len(rows)}"
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=stripes)
    ws.add_table(t)
    return top + len(rows)


def cf_exact(ws, column, first, last, colors):
    L = col(column)
    for val, color in colors.items():
        ws.conditional_formatting.add(f"{L}{first}:{L}{last}",
                                      FormulaRule(formula=[f'{L}{first}="{val}"'], fill=PatternFill("solid", fgColor=color, bgColor=color)))


def section(ws, r, text, ncol):
    put(ws, r, 1, text, font=f(bold=True), fill=SEC_FILL, align=WRAP_CENTER)
    ws.merge_cells(f"A{r}:{col(ncol)}{r}")
    ws.row_dimensions[r].height = 24


# ------------------------------------------------------------------ 各シート
def sheet_papers(wb, k_by_id):
    ws = wb.create_sheet("論文ごとの要点")
    headers = ["ID", "日本語の短い題名", "区分（平易）", "範囲の段（記号）", "誰を・どう調べたか", "何が分かったか", "どこまで引用してよいか",
               "その理由・補足", "注意点", "まだ分からないこと・次の一手", "関連 issue", "対象者", "デザイン", "国・地域", "詳細（判定の根拠）"]
    widths = [8, 30, 22, 14, 42, 48, 20, 36, 52, 40, 12, 16, 12, 16, 16]
    header_block(ws, "論文ごとの要点｜34 件を 1 行ずつ平易に（2026-09-29）",
                 "2026-09-28 の Claude 評価を、記号を知らなくても読めるように言い換えた。『どこまで引用してよいか』は各シートの『引用時の判断』の言い換えで、品質の点数ではない（合計点は付けない）。"
                 "対象者・デザイン・国は『証拠の地図』の数式が数える列。右端のリンクで『Claude適格性評価』の同じ行（判定の根拠・原文箇所）へ飛べる。★ AI の予備判定であり、人間 2 名の独立判定の代わりにならない。",
                 len(headers), 64)
    rows, links = [], {}
    for i, p in enumerate(PP.PAPERS):
        k = k_by_id[p["id"]]
        rows.append([p["id"], p["title_ja"], PP.GROUP_PLAIN[p["group"]], k, p["who_how"], p["found"], p["cite"], p["cite_note"],
                     p["caution"], p["open"], p["issues"] or "—", p["pop"], p["design"], p["country"], "Claude適格性評価へ"])
        links[(i, 15)] = f"'Claude適格性評価'!A{5 + i}"
    last = table(ws, 4, headers, widths, rows, "Readable1", links=links, stripes=False)
    cf_exact(ws, 7, 5, last, CITE_COLORS)
    ws.freeze_panes = "C5"
    return ws


def sheet_map(wb):
    ws = wb.create_sheet("証拠の地図")
    pops, designs = PP.POPS, PP.DESIGNS
    ncol = len(designs) + 2
    header_block(ws, "証拠の地図｜どこに研究があり、どこが空いているか（2026-09-29）",
                 "一次研究 18 件（中心候補 13・疲労を測っていない隣接研究 4・境界 1）を『対象者 × デザイン』に置いた。① は ID の一覧（2026-09-29 時点の値）、② と ③ は『論文ごとの要点』を数える数式（列を直せば更新される）。④ は空いている所と、それを埋める issue。",
                 ncol, 48)
    ws.column_dimensions["A"].width = 26
    for j in range(2, ncol + 1):
        ws.column_dimensions[col(j)].width = 20
    r = 4
    section(ws, r, "① 一次研究 18 件の分布（セルは ID と範囲の段。A = 中心-A、B = 中心-B、? = A/B 未確定、E2 = 疲労を測っていない、境界 = 人間の判定待ち）", ncol)
    r += 1
    heads = ["対象者 ＼ デザイン"] + designs + ["計"]
    for j, h in enumerate(heads, 1):
        put(ws, r, j, h, font=f(bold=True, color="FFFFFFFF"), fill=HEAD_FILL, align=WRAP_CENTER)
    tag = {"A": "A", "B": "B", "?": "?", "E2": "E2", "境界": "境界"}
    for pi, pop in enumerate(pops):
        rr = r + 1 + pi
        put(ws, rr, 1, pop, font=f(bold=True))
        total = 0
        for di, d in enumerate(designs):
            ids = [f"{p['id']}（{tag[p['group']]}）" for p in PP.PAPERS if p["pop"] == pop and p["design"] == d]
            total += len(ids)
            put(ws, rr, 2 + di, "\n".join(ids) if ids else "—", align=WRAP_TOP if ids else WRAP_CENTER)
        put(ws, rr, ncol, total, align=WRAP_CENTER)
        n_ids = max(1, max(sum(1 for p in PP.PAPERS if p["pop"] == pop and p["design"] == d) for d in designs))
        ws.row_dimensions[rr].height = max(row_height([pop], [26]), 16 * n_ids + 4)
    n_primary = sum(1 for p in PP.PAPERS if p["pop"] != "—")
    assert n_primary == 18, n_primary

    r = r + 1 + len(pops) + 1
    section(ws, r, "② 件数（中心候補 13 件だけ・数式）", ncol)
    r += 1
    for j, h in enumerate(heads, 1):
        put(ws, r, j, h, font=f(bold=True, color="FFFFFFFF"), fill=HEAD_FILL, align=WRAP_CENTER)
    top = r + 1
    rng = {"D": "'論文ごとの要点'!$D$5:$D$38", "L": "'論文ごとの要点'!$L$5:$L$38", "M": "'論文ごとの要点'!$M$5:$M$38", "N": "'論文ごとの要点'!$N$5:$N$38"}
    for pi, pop in enumerate(pops):
        rr = top + pi
        put(ws, rr, 1, pop, font=f(bold=True))
        for di, d in enumerate(designs):
            put(ws, rr, 2 + di, f'=COUNTIFS({rng["D"]},"中心*",{rng["L"]},"{pop}",{rng["M"]},"{d}")', align=WRAP_CENTER, text_only=False)
        put(ws, rr, ncol, f"=SUM(B{rr}:{col(ncol - 1)}{rr})", align=WRAP_CENTER, text_only=False)
    rr = top + len(pops)
    put(ws, rr, 1, "計", font=f(bold=True))
    for j in range(2, ncol + 1):
        put(ws, rr, j, f"=SUM({col(j)}{top}:{col(j)}{rr - 1})", font=f(bold=True), align=WRAP_CENTER, text_only=False)
    map_total_cell = f"{col(ncol)}{rr}"

    r = rr + 2
    section(ws, r, "③ 国・地域（中心候補 13 件・数式）", ncol)
    r += 1
    for j, h in enumerate(["国・地域", "件数", "該当"], 1):
        put(ws, r, j, h, font=f(bold=True, color="FFFFFFFF"), fill=HEAD_FILL, align=WRAP_CENTER)
    countries = [("フィリピン", "フィリピン*"), ("中国", "中国*"), ("インド", "インド*"), ("チュニジア", "チュニジア*"), ("台湾", "台湾*"),
                 ("米国・シンガポール", "米国・シンガポール*"), ("国の明記なし", "明記なし*")]
    central = [p for p in PP.PAPERS if p["group"] in ("A", "B", "?")]
    for ci, (label, pat) in enumerate(countries):
        rr = r + 1 + ci
        put(ws, rr, 1, label, font=f(bold=True))
        put(ws, rr, 2, f'=COUNTIFS({rng["D"]},"中心*",{rng["N"]},"{pat}")', align=WRAP_CENTER, text_only=False)
        stem = pat.rstrip("*")
        put(ws, rr, 3, "・".join(p["id"] for p in central if p["country"].startswith(stem)) or "—")
    rr = r + 1 + len(countries)
    put(ws, rr, 1, "計", font=f(bold=True))
    put(ws, rr, 2, f"=SUM(B{r + 1}:B{rr - 1})", font=f(bold=True), align=WRAP_CENTER, text_only=False)
    ws.merge_cells(f"C{r}:{col(ncol)}{r}")
    for x in range(r + 1, rr + 1):
        ws.merge_cells(f"C{x}:{col(ncol)}{x}")
    assert sum(1 for p in central for _, pat in countries if p["country"].startswith(pat.rstrip("*"))) == 13

    r = rr + 2
    section(ws, r, "④ 空いている所（＝調査不足）と、それを埋める issue", ncol)
    r += 1
    for j, h in enumerate(["空いている所", "だから言えないこと", "埋める issue"], 1):
        put(ws, r, j, h, font=f(bold=True, color="FFFFFFFF"), fill=HEAD_FILL, align=WRAP_CENTER)
    gaps = [
        ("中心候補に実験・介入研究が 0 件", "『AI を使うと疲れる（または疲れが減る）』という因果。★ 医療では AI 記録支援で燃え尽き・ウェルビーイングを測った RCT が既にある。", "S-04・S-10"),
        ("中心-A（AI に向けた疲労）で時間をずらして測った研究が 0 件", "疲労が先か AI 利用が先か。時間差があるのは中心-B の AF019 だけ。", "S-10"),
        ("中心-A に『働く人』の標本が 0 件（大学生 3・一般の利用者 4）", "職場・専門職（医療者・開発者など）で AI 疲労がどう現れるか。", "S-07"),
        ("AI を『見張る』人（監督）の研究が 0 件", "作業を任せて見張るだけになったときの疲労（受動的疲労）。対象の定義には『監督』が入っている。", "S-05"),
        ("『疲労が減る』向きの結果が 0 件", "AI 疲労の証拠が一方向に偏っていないか。基準は負担低下・差なしも記録すると定めている。", "S-04"),
        ("日本の対象者・日本語の文献が 0 件", "日本の利用者に当てはまるか。日本語で使える尺度もない（J-STAGE・CiNii の題名段で 0 件）。", "S-12・I-04"),
        ("フィリピンの 4 件は同じ地域・重なる著者群", "独立した証拠の数。AF006 と AF007 は同じ回答データの強い手がかりがあり、実質の独立標本は見かけより少ない。", "N-03・N-02"),
        ("本文未入手の中心候補が 3 件（AF002・AF003・AF009）", "中心-A の件数そのもの（全文で B になる可能性がある）。", "N-01"),
    ]
    for gi, g in enumerate(gaps):
        rr = r + 1 + gi
        for j, v in enumerate(g, 1):
            put(ws, rr, j, v, font=f(bold=(j == 1)))
        ws.merge_cells(f"B{rr}:{col(ncol - 1)}{rr}")
        ws.row_dimensions[rr].height = 48
    ws.freeze_panes = "B4"
    return ws, map_total_cell


def sort_key(i):
    return (["サーヴェイ", "アイディア", "通常"].index(i["type"]), ID.PRIORITIES.index(i["priority"]), i["id"])


def sheet_issues(wb):
    ws = wb.create_sheet("調査不足とissue")
    headers = ["番号", "種類", "優先度", "手間", "タイトル", "なぜ必要か（何が足りないか）", "根拠の場所（シート・ID）", "調べる価値の判断材料（件数・種文献）",
               "具体的な次の一手", "完了の条件", "GSE との関係（既決の禁止線を含む）", "依存・順序", "状態（記入欄）", "メモ（記入欄）"]
    widths = [7, 10, 7, 6, 34, 48, 30, 56, 48, 32, 44, 18, 11, 22]
    header_block(ws, f"調査不足とissue｜{len(ID.ISSUES)} 件（サーヴェイ・アイディア・通常）",
                 "種類: サーヴェイ = 文献を探して読む／アイディア = GSE のこれまでの研究から出てきた着想（GSE の既決の禁止線に反しないものだけ）／通常 = 全文入手・照会・DB 更新・人間の判定など手を動かせば閉じる作業。"
                 "並びは サーヴェイ → アイディア → 通常、その中で優先度順。件数は PRISMA の件数ではなく『調べる価値』の目安（出典は『件数の目安と種文献』）。★ 青字の 2 列（状態・メモ）は記入欄。状態はドロップダウン。★ GitHub の issue は起票していない。",
                 len(headers), 64)
    rows = []
    for i in sorted(ID.ISSUES, key=sort_key):
        rows.append([i["id"], i["type"], i["priority"], i["effort"], i["title"], i["why"], i["where"], i["evidence"], i["next"], i["done"],
                     i["gse"], i["depends"], "未着手", ""])
    last = table(ws, 4, headers, widths, rows, "Readable2", input_cols=(13, 14), stripes=False)
    cf_exact(ws, 3, 5, last, PRIO_COLORS)
    cf_exact(ws, 13, 5, last, {"完了": "FFD1FAE5", "見送り": "FFF1F3F5", "着手": "FFE3F2FD"})
    dv = DataValidation(type="list", formula1=f'"{STATUS}"', allow_blank=True)
    dv.add(f"M5:M{last}")
    ws.add_data_validation(dv)
    ws.freeze_panes = "F5"
    return ws, last


def sheet_counts(wb):
    ws = wb.create_sheet("件数の目安と種文献")
    headers = ["issue", "情報源", "検索式", "件数", "取得日", "注記"]
    widths = [8, 26, 70, 10, 12, 44]
    header_block(ws, "件数の目安と種文献｜『調べる価値がある』と判断した材料",
                 "① 件数: 学術 API で取った目安。⚠️ PRISMA の件数ではない（検索式・索引ごとに意味が違う）。語の一致が粗くて意味を持たない件数は載せず『未計測』とした。OpenAlex の匿名検索は 2026-09-29 に回数制限（HTTP 429）で途中から使えなかった。"
                 "② 種文献: 2026-09-29 に Crossref（Zenodo は DataCite）で実在を確認した。本文は読んでいない（読むのは各 issue の作業）。",
                 len(headers), 64)
    rows = [list(c) for c in ID.COUNTS]
    last = table(ws, 4, headers, widths, rows, "Readable3")
    top2 = last + 3
    section(ws, top2 - 1, "② 種文献（実在を確認済み・本文は未読）", len(headers))
    h2 = ["issue", "著者・年", "題名", "掲載誌", "DOI", "リンク"]
    rows2 = [[s[0], s[1], s[2], s[3], s[4], "開く"] for s in ID.SEEDS]
    links = {(i, 6): f"https://doi.org/{s[4]}" for i, s in enumerate(ID.SEEDS)}
    table(ws, top2, h2, [8, 26, 70, 10, 12, 44], rows2, "Readable4", links=links, set_widths=False)
    ws.freeze_panes = "A5"
    return ws


def sheet_inquiries(wb):
    ws = wb.create_sheet("照会の下書き")
    headers = ["番号", "宛先", "論点", "関連 issue", "照合事項", "送る前に確かめること", "下書き（英文）", "送付の記録（記入欄）"]
    widths = [7, 24, 26, 9, 12, 34, 96, 22]
    header_block(ws, "照会の下書き｜著者への問い合わせ 6 件（★ 送るかは研究者が決める）",
                 "Claude照合事項で一次に確認した食い違いについて、中立的な確認の依頼として書いた下書き。★ 送信はしていない（外部に出る操作のため）。宛先のメールアドレス・差出人名・送る相手（責任著者か編集部か）は研究者が決める。⚠️ 不整合の指摘は研究不正の認定ではない。",
                 len(headers), 56)
    rows = [[f"Q{i + 1}", q["to"], q["about"], q["issue"], q["ref"], q["check"], q["draft"], ""] for i, q in enumerate(ID.INQUIRIES)]
    table(ws, 4, headers, widths, rows, "Readable5", input_cols=(8,))
    ws.freeze_panes = "C5"
    return ws


def sheet_glossary(wb):
    ws = wb.create_sheet("用語の読み替え")
    headers = ["記号・用語", "平易な読み方", "例", "主に出てくるシート"]
    widths = [22, 80, 34, 28]
    header_block(ws, "用語の読み替え｜評価版の記号をふつうの言葉で",
                 "Claude 評価のシートで使った作業用の記号の読み方。判定のルールそのものは『Claude評価基準』にある。", len(headers), 36)
    table(ws, 4, headers, widths, [list(g) for g in ID.GLOSSARY], "Readable6")
    ws.freeze_panes = "B5"
    return ws


def sheet_start(wb, issues_last, map_total_cell):
    NT = {t: sum(1 for i in ID.ISSUES if i["type"] == t) for t in ID.TYPES}
    ws = wb.create_sheet("★まず読む")
    ncol = 3
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 100
    ws.column_dimensions["C"].width = 22
    header_block(ws, "AI 疲労 文献 DB｜読みやすい版（Claude・2026-09-29）",
                 "2026-09-28 の Claude 評価（右側の『Claude…』シート）を、記号を知らなくても読めるようにまとめ直し、調査が足りない所を issue にした。"
                 "既存の 26 シート（元の 16＋Claude 10）は 1 セルも変えていない（機械で確認）。橙のタブが今回の追加。★ AI の予備判定であり、人間 2 名の独立判定の代わりにならない。"
                 "⚠️ 判定者としてスクリーニングをする人は、判定が終わるまでこのシートと『論文ごとの要点』・Claude／GPT のシートを読まない（判定者用ファイルは AI の判定を含まない形で用意する・issue N-02）。",
                 ncol, 80)
    r = 4
    section(ws, r, "結論を 6 行で", ncol)
    concl = [
        ("1", "AI に向けた疲労を正面から測った一次研究は 7 件（中心-A）。ほかに本文未入手で A か B か未確定が 3 件。まとまった検証のある尺度は AF001 の 1 本だけ。", "N-01・S-08"),
        ("2", "中心候補 13 件は横断調査と質的研究が 10 件。AI を使って疲労を測った実験は 0 件、時間をずらして測ったのは AF019（中心-B）の 1 件だけ →『AI を使うと疲れる』という因果はまだ言えない。", "S-10"),
        ("3", "中心候補のうち 4 件はフィリピンの大学生で、著者群が重なる。AF006 と AF007 は同じ回答データの強い手がかりがある → 独立した証拠は見かけより少ない。", "N-03"),
        ("4", "数値をそのまま引けない研究がある: AF011（相関の単位が項目）・AF006（百分率の分母）・AF004（交互作用の向きが論文内で逆）・AF008（項目数・推定の安定性）。引ける範囲は『論文ごとの要点』の G 列。", "N-03"),
        ("5", "DB には『AI で疲労が減る』向きの研究と、AI を『見張る』疲労の研究が入っていない。医療では AI 記録支援で燃え尽きを測った RCT が既にある → 証拠が一方向に偏って見える最大の穴。", "S-04・S-05"),
        ("6", "日本語の文献・日本の対象者は 0 件（J-STAGE・CiNii の題名段）。検索漏れ候補には、査読誌の中心的な候補が 7 件（ほかに非査読の既存レビュー 1 件）ある。", "S-12・S-02"),
    ]
    for i, (n, t, iss) in enumerate(concl):
        rr = r + 1 + i
        put(ws, rr, 1, n, font=f(bold=True), align=WRAP_CENTER)
        put(ws, rr, 2, t)
        put(ws, rr, 3, iss, link="'調査不足とissue'!A4")
        ws.row_dimensions[rr].height = row_height(["", t, ""], [30, 100, 22])
    r = r + 1 + len(concl) + 1

    section(ws, r, "数字で見る（数式。元のシートや『論文ごとの要点』の列を編集すると更新される）", ncol)
    K = "'Claude適格性評価'!$K$5:$K$38"
    D, L, M, N = ("'論文ごとの要点'!$D$5:$D$38", "'論文ごとの要点'!$L$5:$L$38", "'論文ごとの要点'!$M$5:$M$38", "'論文ごとの要点'!$N$5:$N$38")
    IS = f"'調査不足とissue'!$C$5:$C${issues_last}"
    IT = f"'調査不足とissue'!$B$5:$B${issues_last}"
    ST = f"'調査不足とissue'!$M$5:$M${issues_last}"
    nums = [
        ("登録文献", "元 DB の 34 件。", "=COUNTA('Claude適格性評価'!$A$5:$A$38)", 34),
        ("中心-A（AI に向けた疲労）", "AF001・AF005〜AF008・AF010・AF011。", f'=COUNTIF({K},"中心-A")', 7),
        ("中心（A/B 未確定）", "本文未入手の AF002・AF003・AF009。", f'=COUNTIF({K},"中心（*")', 3),
        ("中心-B（一般的な疲労 × AI）", "AF004・AF012・AF019。中心-A と足し合わせない。", f'=COUNTIF({K},"中心-B")', 3),
        ("中心-A のうち大学生", "AF006・AF007・AF008（いずれもフィリピン）。", f'=COUNTIFS({D},"中心-A",{L},"大学生・学習者")', 3),
        ("中心候補のうち横断調査・質的研究", "", f'=COUNTIFS({D},"中心*",{M},"横断調査")+COUNTIFS({D},"中心*",{M},"質的研究")', 10),
        ("中心候補のうち時間差・縦断", "AF019 のみ（中心-B）。", f'=COUNTIFS({D},"中心*",{M},"時間差・縦断")', 1),
        ("中心候補のうち実験・介入", "", f'=COUNTIFS({D},"中心*",{M},"実験・介入")', 0),
        ("中心候補のうちフィリピン／中国", "", f'=COUNTIFS({D},"中心*",{N},"フィリピン*")&" / "&COUNTIFS({D},"中心*",{N},"中国*")', "4 / 4"),
        ("中心候補（地図の計）", "『証拠の地図』② の合計。上の中心-A＋未確定＋中心-B と一致するはず。", f"='証拠の地図'!{map_total_cell}", 13),
        ("issue の数（サーヴェイ / アイディア / 通常）", "", f'=COUNTIF({IT},"サーヴェイ")&" / "&COUNTIF({IT},"アイディア")&" / "&COUNTIF({IT},"通常")', f"{NT['サーヴェイ']} / {NT['アイディア']} / {NT['通常']}"),
        ("issue の優先度（高 / 中 / 低）", "", f'=COUNTIF({IS},"高")&" / "&COUNTIF({IS},"中")&" / "&COUNTIF({IS},"低")',
         " / ".join(str(sum(1 for i in ID.ISSUES if i["priority"] == p)) for p in ID.PRIORITIES)),
        ("issue の完了 / 全体", "『調査不足とissue』の状態の列（記入欄）を数える。", f'=COUNTIF({ST},"完了")&" / "&COUNTA(\'調査不足とissue\'!$A$5:$A${issues_last})', f"0 / {len(ID.ISSUES)}"),
    ]
    r += 1
    for j, h in enumerate(["項目", "説明", "値"], 1):
        put(ws, r, j, h, font=f(bold=True, color="FFFFFFFF"), fill=HEAD_FILL, align=WRAP_CENTER)
    expect = {}
    for i, (a, b, formula, exp) in enumerate(nums):
        rr = r + 1 + i
        put(ws, rr, 1, a, font=f(bold=True))
        put(ws, rr, 2, b)
        put(ws, rr, 3, formula, align=WRAP_CENTER, text_only=False)
        ws.row_dimensions[rr].height = row_height([a, b], [30, 100])
        if exp is not None:
            expect[f"C{rr}"] = exp
    r = r + 1 + len(nums) + 1

    section(ws, r, "おすすめの順番", ncol)
    for i, (n, a, b) in enumerate(ID.ROADMAP):
        rr = r + 1 + i
        put(ws, rr, 1, f"{n}. {a}", font=f(bold=True))
        put(ws, rr, 2, b)
        ws.merge_cells(f"B{rr}:C{rr}")
        ws.row_dimensions[rr].height = row_height(["", b], [30, 120])
    r = r + 1 + len(ID.ROADMAP) + 1

    section(ws, r, "どのシートを見ればよいか", ncol)
    guide = [
        ("1 本ずつ何が分かったか", "誰を・どう調べ、何が分かり、どこまで引用してよいか。", "論文ごとの要点"),
        ("研究がどこに偏っているか", "対象者 × デザインの分布と、空いている所。", "証拠の地図"),
        ("次に何を調べるか", f"サーヴェイ {NT['サーヴェイ']}・アイディア {NT['アイディア']}・通常 {NT['通常']} の issue。状態を記入できる。", "調査不足とissue"),
        ("調べる価値の根拠", "検索式つきの件数と、実在を確かめた種文献。", "件数の目安と種文献"),
        ("著者に問い合わせるなら", "英文の下書き 6 件（未送信）。", "照会の下書き"),
        ("記号の意味", "中心-A/B・E1〜E6・JBI・段階記号など。", "用語の読み替え"),
        ("判定の根拠・原文箇所", "2026-09-28 の Claude 評価の本体。", "Claude適格性評価"),
        ("判定のルール", "範囲・手順・限界。", "Claude評価基準"),
        ("元の DB", "研究者が作った 16 シート（変更なし）。", "はじめに"),
    ]
    for i, (a, b, s) in enumerate(guide):
        rr = r + 1 + i
        put(ws, rr, 1, a, font=f(bold=True))
        put(ws, rr, 2, b)
        put(ws, rr, 3, s, link=f"'{s}'!A1")
        ws.row_dimensions[rr].height = row_height([a, b, s], [30, 100, 22])
    r = r + 1 + len(guide) + 1

    section(ws, r, "今回やったこと／やっていないこと", ncol)
    notes = [
        ("やったこと", f"34 件の平易な要約、証拠の地図、用語の読み替え。調査不足の洗い出しと issue 化（{len(ID.ISSUES)} 件。前回のセッションが書きかけて止まっていた課題 T01〜T19・アイディア G01〜G09 も取り込んだ）。サーヴェイ issue ごとに学術 API で件数の目安を取り、種文献 31 件の実在を Crossref・DataCite で確認。日本語は J-STAGE・CiNii Research で点検。"),
        ("やっていないこと", "サーヴェイそのもの（本格的な検索・スクリーニング・精読）。種文献の本文は読んでいない。著者への照会の送信・GitHub の issue の起票（外部に出る操作）。元 DB と既存 26 シートの変更。人間の判定欄への書き込み。"),
        ("限界", "件数は目安で PRISMA の件数ではない。OpenAlex は回数制限で途中から使えず、開発者（Copilot）の件数は未計測、語の用法（プロンプト疲れなど）の件数は上位が無関係で目安にならなかった。日本語の点検は題名段・各上位 100 件だけで、不在の証明ではない。要約は 09-28 の評価と抽出ノートに基づき、新しい一次確認はしていない。"),
    ]
    for i, (a, b) in enumerate(notes):
        rr = r + 1 + i
        put(ws, rr, 1, a, font=f(bold=True))
        put(ws, rr, 2, b)
        ws.merge_cells(f"B{rr}:C{rr}")
        ws.row_dimensions[rr].height = row_height(["", b], [30, 120])
    ws.sheet_view.showGridLines = False
    return ws, expect


# ------------------------------------------------------------------ issues.md
def md_escape(s):
    return str(s).replace("|", "｜").replace("\n", " ")


def write_issues_md():
    out = []
    out.append("# AI 疲労 文献 DB：調査不足の issue 一覧（2026-09-29）\n")
    out.append("> ★ 生成物。`scripts/issues_data.py` から `scripts/build_readable.py` が書く（xlsx の『調査不足とissue』シートと同じデータ）。手で直さず、データを直して再生成する。")
    out.append("> ★ GitHub の issue は起票していない。著者への照会も送っていない（下書きのみ・付録 A）。")
    out.append("> ⚠️ 件数は『調べる価値』の目安で、PRISMA の件数ではない（付録 B）。\n")
    out.append("## 一覧\n")
    out.append("| 番号 | 種類 | 優先度 | 手間 | タイトル | 依存 |")
    out.append("|---|---|---|---|---|---|")
    for i in sorted(ID.ISSUES, key=sort_key):
        out.append(f"| {i['id']} | {i['type']} | {i['priority']} | {i['effort']} | {md_escape(i['title'])} | {md_escape(i['depends'])} |")
    out.append("\n## おすすめの順番\n")
    for n, a, b in ID.ROADMAP:
        out.append(f"{n}. **{a}**: {b}")
    for t in ["サーヴェイ", "アイディア", "通常"]:
        out.append(f"\n## {t} issue\n")
        for i in sorted([x for x in ID.ISSUES if x["type"] == t], key=sort_key):
            out.append(f"### {i['id']}（優先度 {i['priority']}・手間 {i['effort']}）{i['title']}\n")
            for label, key in [("なぜ必要か", "why"), ("根拠の場所", "where"), ("調べる価値の判断材料", "evidence"), ("次の一手", "next"),
                               ("完了の条件", "done"), ("GSE との関係", "gse"), ("依存・順序", "depends")]:
                out.append(f"- **{label}**: {i[key]}")
            out.append("")
    out.append("\n## 付録 A：照会の下書き（未送信・送るかは研究者が決める）\n")
    for n, q in enumerate(ID.INQUIRIES, 1):
        out.append(f"### Q{n}. {q['to']} —— {q['about']}（{q['issue']}・{q['ref']}）\n")
        out.append(f"- 送る前に確かめること: {q['check']}\n")
        out.append("```text")
        out.append(q["draft"])
        out.append("```\n")
    out.append("## 付録 B：件数の目安\n")
    out.append("| issue | 情報源 | 検索式 | 件数 | 取得日 | 注記 |")
    out.append("|---|---|---|---|---|---|")
    for c in ID.COUNTS:
        out.append("| " + " | ".join(md_escape(x) if k != 2 else "`" + str(x).replace("|", "¦") + "`" for k, x in enumerate(c)) + " |")
    out.append("\n## 付録 C：種文献（2026-09-29 に Crossref・DataCite で実在を確認・本文は未読）\n")
    for s in ID.SEEDS:
        out.append(f"- [{s[0]}] {s[1]}. {s[2]}. *{s[3]}*. https://doi.org/{s[4]}")
    with open(ISSUES_MD, "w", encoding="utf-8", newline="\n") as fp:
        fp.write("\n".join(out) + "\n")


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copy-to")
    ap.add_argument("--mutate-test", action="store_true")
    a = ap.parse_args()
    if sha256(SRC) != SRC_SHA:
        sys.exit("入力（09-28 版）の SHA-256 がアーカイブの記録と違う")
    if bx.same_file(DST, SRC):
        sys.exit("出力先が入力と同じ")
    wb = openpyxl.load_workbook(SRC)
    orig = list(wb.sheetnames)
    assert len(orig) == 26, len(orig)
    before = bx.snapshot(wb)
    struct_before = bx.structure(wb)

    # 範囲の段（記号）は 09-28 版の Claude適格性評価 K 列からそのまま写す（言い換えとの食い違いを防ぐ）
    ws_e = wb["Claude適格性評価"]
    k_by_id = {ws_e[f"A{r}"].value: ws_e[f"K{r}"].value for r in range(5, 39)}
    gmap = {"A": "中心-A", "B": "中心-B", "?": "中心（A/B 未確定）", "境界": "境界（保留）", "E2": "背景（E2）"}
    for i, p in enumerate(PP.PAPERS):
        assert ws_e[f"A{5 + i}"].value == p["id"], (i, p["id"])
        k = k_by_id[p["id"]]
        if p["group"] in gmap:
            assert k == gmap[p["group"]], (p["id"], k, p["group"])
        else:
            assert k.endswith("（E4）"), (p["id"], k)

    sheet_papers(wb, k_by_id)
    _, map_total = sheet_map(wb)
    _, issues_last = sheet_issues(wb)
    sheet_counts(wb)
    sheet_inquiries(wb)
    sheet_glossary(wb)
    _, expect = sheet_start(wb, issues_last, map_total)
    for name in ORDER:
        ws = wb[name]
        ws.sheet_properties.tabColor = TAB
        ws.page_setup.orientation = "landscape"  # 印刷は横向き・幅に合わせる（画面の見え方は変わらない）
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    # 並び: 元 16 → 今回の 7 → 前回の Claude 10
    pos = orig.index("Claude評価概要")
    new = [wb[n] for n in ORDER]
    rest = [ws for ws in wb._sheets if ws.title not in ORDER]
    wb._sheets = rest[:pos] + new + rest[pos:]
    if not wb.views:
        wb.views.append(BookView())
    for ws in wb.worksheets:
        ws.sheet_view.tabSelected = False
    wb.active = wb.sheetnames.index("★まず読む")
    wb.active.sheet_view.tabSelected = True
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    if a.mutate_test:
        wb["スクリーニング"]["F5"] = "含める"  # 変異: 人間の判定欄への書き込み

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".xlsx", dir=os.path.dirname(DST))
    os.close(fd)
    try:
        wb.save(tmp)
        chk = openpyxl.load_workbook(tmp)
        after = {k: v for k, v in bx.snapshot(chk).items() if k[0] in orig}
        if after != before:
            diff = sorted(set(before.items()) ^ set(after.items()))[:5]
            sys.exit(f"既存シートのセル値が変わった: {diff}")
        if bx.structure(chk, orig) != {k: v for k, v in struct_before.items()}:
            sys.exit("既存シートの構成（入力規則・条件付き書式・結合・テーブル・定義名）が変わった")
        if chk.sheetnames[:16] != orig[:16] or chk.sheetnames[16:23] != ORDER or chk.sheetnames[23:] != orig[16:]:
            sys.exit(f"シートの並びが想定と違う: {chk.sheetnames}")
        assert all(v == "未判定" for r in range(5, 39) for v in (chk["スクリーニング"][f"{c}{r}"].value for c in "DEF"))
        if a.mutate_test:
            sys.exit("変異試験: 検算が止まらなかった（異常）")
        os.replace(tmp, DST)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    write_issues_md()
    if a.copy_to:
        shutil.copy2(DST, os.path.join(a.copy_to, os.path.basename(DST)))
    print("OK", DST)
    print("expect", expect)
    print("sha256", sha256(DST))


if __name__ == "__main__":
    main()
