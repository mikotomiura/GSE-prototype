"""判定者用ファイル（AI の判定を含まない）を作る。

研究者が判定者 1 として独立判定するためのファイル（2026-09-29 研究者「独立判定のうちの一つは私が行う感じになります」）。
★ Claude・GPT の判定・評価・懸念は 1 つも入れない（書誌・リンク・共通の判定基準だけ）。保存後に機械で確かめる。
出力: archive/judge/AI_fatigue_judge-sheet_2026-09-29.xlsx（第 1 引数で変更可）
"""
import os
import sys
import tempfile

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

from build_xlsx import SRC, FONT, TEXT, TITLE_FILL, SUB_FILL, HEAD_FILL, WRAP_TOP, WRAP_CENTER, row_height, same_file

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(HERE), "judge", "AI_fatigue_judge-sheet_2026-09-29.xlsx")
INPUT_FILL = PatternFill("solid", fgColor="FFFEF9C3")
INPUT_FONT = Font(name=FONT, size=11, color="FF175CD3")
LINK = Font(name=FONT, size=11, color="FF0563C1", underline="single")
# ★ 判定者用ファイルに現れてはいけない語（AI の判定・評価の痕跡）。判定の語彙はブック全体で、AI の名前は判定シートの入力欄（I 列以降）と集計で禁止する（題名の ChatGPT などは書誌なので対象外）
FORBIDDEN_LABELS = ("中心候補", "背景保持", "方法論保持", "訂正連結", "懸念", "AI用途", "AI 予備", "AI予備", "照合事項", "R-I", "スクリーニング案")
FORBIDDEN_IN_SHEET = ("Claude", "GPT")

INTRO = [
 ["このファイルの目的", "判定者 1（研究者）が、AI の判定を見ずに 34 件を独立に判定するためのファイル。Claude・GPT の判定・評価は 1 つも入れていない（書誌・リンク・共通の判定基準だけ）。"],
 ["進め方", "① 『判定基準』シートを読む → ② 『判定シート』で DOI・URL から抄録を読み、題名・抄録段を選ぶ → ③ 『含める』『保留』にした件は全文を読み、全文段を選ぶ → ④ 中心範囲の段と、除外なら除外理由を選ぶ → ⑤ 根拠を短くメモする。"],
 ["入力する欄", "黄色の欄だけ（ドロップダウンで選ぶ）。書誌の欄は変えない。"],
 ["独立性の注意", "判定が終わるまで、評価版ファイル（…_claude.xlsx）の Claude のシートと、元ファイルの『AI…』のシートを開かない。★ チャットの要約で Claude の判定の一部を既に見ているので、完全な盲検ではない。判定者 2 には AI の結果を見ていない人を当てるのが望ましい。"],
 ["全文の入手", "購読制の論文は機関アクセスで。入手できない件は全文段を『保留』にし、読んだ範囲に『抄録』と書く。"],
 ["終わったら", "このファイルを Claude に渡すか、元ファイルの『スクリーニング』の判定者 1 欄へ写す。2 人の判定がそろったら『AI判定比較』で比べ、不一致を話し合う（Claude・GPT の案は話し合いの参考にだけ使う）。"],
 ["集計", "『集計』シートが進み具合を数える（数式）。"],
]
CRITERIA = [
 ["問い（PCC）", "人が AI を使う・監督する・評価することに関連する疲労について、何が定義・測定・観察されているか（スコーピング型）。P＝AI を使う・監督する・評価する人。C＝疲労（認知・情動・身体・動機／行動面の消耗、exhaustion、weariness、燃え尽きのような枯渇）を定義・測定・質的に分析し、AI の利用・監督との関係の中で扱うもの。Context＝教育・職場・消費・研究など問わない。期間＝オンライン公開が 2026-09-28 以前。"],
 ["題名・抄録段", "P と C に当たる可能性のある一次研究は『含める』（迷ったら含める＝全文段へ回す）。一次研究でない（レビュー・尺度の原著・方法論・訂正通知）は『除外』＋ E4（DB からは消さず背景として残す）。"],
 ["全文段", "全文を読めた件だけ判定する。読めなかった件は『保留』。"],
 ["中心範囲の段（含める場合）", "中心-A＝疲労を AI に帰属させて定義・測定している（項目文・定義・質問文に AI が出てくる、または AI 疲労の語りを分析する）。中心-B＝疲労・消耗・燃え尽きを測るが、構成概念は一般的（項目に AI が出ない）で、AI の利用や AI 由来の要求と関係づけている。境界（保留）＝規則だけでは決まらない。"],
 ["除外理由", "E1＝AI が人の疲労を検出・予測する道具であるだけ（疾患の症状としての疲労を AI が管理する場合を含む）／E2＝疲労を定義・測定・質的分析していない（認知負荷・不安・過信だけなど）／E3＝疲労を測るが AI の利用・監督と関係づけていない／E4＝一次研究でない／E5＝重複出版・同じ標本・版違い／E6＝全文が手に入らず判定できない（→保留）。"],
 ["注意", "研究の質の低さは除外の理由にしない（引用の範囲で扱う）。AI の利用で疲労が下がるかを測る介入研究も、方向にかかわらず対象になり得る。"],
 ["この基準の出どころ", "元ファイルの『項目定義・採択基準』シートを操作化したもの（Claude と同じ基準。判定の結果は入れていない）。"],
]


def styled_sheet(wb, name, title, subtitle, headers, widths, rows, first=False):
    ws = wb.active if first else wb.create_sheet(name)
    ws.title = name
    last = openpyxl.utils.get_column_letter(len(headers))
    for addr, val, fill, bold, color in (("A1", title, TITLE_FILL, True, "FFFFFFFF"), ("A2", subtitle, SUB_FILL, False, TEXT)):
        c = ws[addr]; c.value = val; c.fill = fill; c.font = Font(name=FONT, size=11, bold=bold, color=color); c.alignment = WRAP_TOP
    ws.merge_cells(f"A1:{last}1"); ws.merge_cells(f"A2:{last}2")
    ws.row_dimensions[1].height = 30; ws.row_dimensions[2].height = 48
    for j, h in enumerate(headers, 1):
        c = ws.cell(4, j, h); c.font = Font(name=FONT, size=11, bold=True, color="FFFFFFFF"); c.fill = HEAD_FILL; c.alignment = WRAP_CENTER
    ws.row_dimensions[4].height = 36
    for i, row in enumerate(rows, 5):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v)
            if isinstance(v, str) and v.startswith("="):
                c.data_type = "s"
            c.font = Font(name=FONT, size=11, color=TEXT); c.alignment = WRAP_TOP
        ws.row_dimensions[i].height = row_height(row, widths)
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = w
    ws.freeze_panes = "B5"
    return ws


def main():
    dst = sys.argv[1] if len(sys.argv) > 1 else DST
    if same_file(dst, SRC):
        sys.exit("出力先が入力 xlsx と同じです")
    src = openpyxl.load_workbook(SRC, data_only=True)
    db, bib = src["文献DB"], src["書誌・出典"]
    ids = [db.cell(r, 1).value for r in range(5, 39)]
    wb = openpyxl.Workbook()
    styled_sheet(wb, "はじめに（判定者向け）", "AI 疲労 文献 DB｜判定者用ファイル（AI の判定を含まない）",
                 "判定者 1 の独立判定用。黄色の欄だけを入力する。", ["項目", "説明"], [22, 110], INTRO, first=True)
    styled_sheet(wb, "判定基準", "判定基準｜判定者と Claude で共通の基準", "元ファイルの『項目定義・採択基準』を操作化したもの。",
                 ["項目", "規則"], [24, 110], CRITERIA)
    rows = []
    for k, i in enumerate(ids):
        r = 5 + k
        rows.append([i, db.cell(r, 5).value, db.cell(r, 6).value, db.cell(r, 4).value, db.cell(r, 7).value, db.cell(r, 9).value,
                     db.cell(r, 8).value, db.cell(r, 11).value, "未判定", "未判定", "未判定", "", "", "", ""])
    headers = ["ID", "論文タイトル", "著者（短縮）", "年", "掲載誌・媒体", "公表区分", "DOI", "一次情報URL",
               "題名・抄録段", "全文段", "中心範囲の段", "除外理由", "読んだ範囲", "根拠メモ", "判定日"]
    widths = [8, 46, 18, 7, 26, 14, 26, 30, 13, 11, 14, 10, 12, 40, 11]
    ws = styled_sheet(wb, "判定シート", "判定シート｜34 件（黄色の欄を入力）",
                      "DOI・URL をクリックすると論文のページが開く。判定の選択肢は『判定基準』シートを参照。", headers, widths, rows)
    last = 4 + len(rows)
    for r in range(5, last + 1):
        for col in (7, 8):  # DOI・URL は外部リンク（公開の論文ページ）
            c = ws.cell(r, col)
            url = ("https://doi.org/" + c.value) if col == 7 and c.value and str(c.value).startswith("10.") else c.value
            if url and str(url).startswith("http"):
                c.hyperlink = url; c.font = LINK
        for col in range(9, 16):
            c = ws.cell(r, col); c.fill = INPUT_FILL; c.font = INPUT_FONT
    for col, opts in ((9, "未判定,含める,除外,保留"), (10, "未判定,含める,除外,保留"),
                      (11, "未判定,中心-A,中心-B,境界（保留）,背景（E2）,背景（E4）,方法論,訂正"),
                      (12, "E1,E2,E3,E4,E5,E6"), (13, "題名のみ,抄録,全文の一部,全文")):
        L = openpyxl.utils.get_column_letter(col)
        dv = DataValidation(type="list", formula1='"' + opts + '"', allow_blank=True); dv.add(f"{L}5:{L}{last}"); ws.add_data_validation(dv)
    for col in (9, 10):
        L = openpyxl.utils.get_column_letter(col)
        for val, color in (("含める", "FFD1FAE5"), ("保留", "FFFEF3C7"), ("除外", "FFE5E7EB")):
            ws.conditional_formatting.add(f"{L}5:{L}{last}", FormulaRule(formula=[f'{L}5="{val}"'], fill=PatternFill("solid", fgColor=color, bgColor=color)))
    t = Table(displayName="JudgeSheet", ref=f"A4:O{last}"); t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=False); ws.add_table(t)
    agg = [["題名・抄録段: " + v, f'=COUNTIF(\'判定シート\'!I5:I{last},"{v}")'] for v in ("含める", "除外", "保留", "未判定")] + \
          [["全文段: " + v, f'=COUNTIF(\'判定シート\'!J5:J{last},"{v}")'] for v in ("含める", "除外", "保留", "未判定")]
    sa = styled_sheet(wb, "集計", "集計｜進み具合", "判定シートを数える数式。", ["項目", "件数"], [30, 12], agg)
    for r in range(5, 5 + len(agg)):
        sa.cell(r, 2).data_type = "f"  # 集計の列だけ数式として保存する
    wb.active = wb.sheetnames.index("判定シート")
    for w_ in wb.worksheets:
        w_.sheet_view.tabSelected = (w_.title == "判定シート")
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".xlsx", dir=os.path.dirname(os.path.abspath(dst)))
    os.close(fd)
    try:
        wb.save(tmp)
        chk = openpyxl.load_workbook(tmp)
        leaks = [(s.title, c.coordinate, str(c.value)[:30]) for s in chk.worksheets for row in s.iter_rows() for c in row
                 if isinstance(c.value, str) and (any(f in c.value for f in FORBIDDEN_LABELS)
                     or ((s.title == "集計" or (s.title == "判定シート" and c.column >= 9)) and any(f in c.value for f in FORBIDDEN_IN_SHEET)))]
        undecided = all(chk["判定シート"].cell(r, c).value == "未判定" for r in range(5, last + 1) for c in (9, 10, 11))
        ids_ok = [chk["判定シート"].cell(r, 1).value for r in range(5, last + 1)] == ids
        print({"leaks": leaks[:5], "n_leaks": len(leaks), "all_undecided": undecided, "ids_ok": ids_ok, "rows": len(rows)})
        if leaks or not undecided or not ids_ok:
            sys.exit("判定者用ファイルの検査に失敗した（AI の判定の混入・初期値・ID）")
        os.replace(tmp, dst)
        print("saved:", dst)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    main()
