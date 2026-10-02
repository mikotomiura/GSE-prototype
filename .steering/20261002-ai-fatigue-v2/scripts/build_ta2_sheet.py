"""記入表 2（抄録段で除外した件の 2 回目・AI の判定を見せる）を作る（design.md §7）。

対象 = ログの `ta1`（記入表 1『追加候補』）で `除外` にした記録。★ 記入表 1 を読んだ後でなければ作らない。
AI の値は評価版（Claude 版・`ed788f53…`）の『Claudeスクリーニング案』『Claude適格性評価』『Claude方法論メモ』から写す。
★ Downloads の記入表 2 が最後に書いた SHA-256（archive/ta-sheets-sha256.txt の sheet2）と違えば止まる。
使い方: uv run --with openpyxl python build_ta2_sheet.py [--dry-run]
"""
import json
import os
import re
import shutil
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

import common as C
from build_ta_sheet import ECODES, VERDICTS, fit_rows, put

TITLE = "AI 疲労 文献 DB｜抄録段で除外した記録の 2 回目の記入表 2（判定者 1）"
SAME = ["1 回目のまま", "変える"]
DIFF = ["1 回目のまま", "AI の判定に変える", "別の判定に変える"]
HEADER = ["候補番号", "題名", "1 回目（判定者 1）", "AI：題名・抄録段の予備判定", "AI：除外理由", "AI：中心範囲の段",
          "AI：用途判定", "AI：判定根拠", "AI：方法論メモ（懸念・限界）", "2 回目【記入】", "変えた後の判定【記入】",
          "変えた後の除外理由【記入】", "理由【記入】"]
INPUT = (10, 11, 12, 13)
HR = 4
YELLOW = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")
INTRO = [
    ("この表について", "記入表 1 で「除外」にした記録について、評価版（Claude による AI の予備判定・2026-09-30）の値を見て、"
                       "1 回目のままにするか変えるかを決める表です（2 回目）。研究者・判定者 2 には渡しません。"),
    ("記入する列", "黄色の見出しの列（J〜M）だけです。ほかのセルは変えないでください。"),
    ("2 回目", "AI の予備判定が 1 回目と同じ記録（判定が同じで、除外理由の E の番号も同じ）は「1 回目のまま／変える」、"
               "違う記録は「1 回目のまま／AI の判定に変える／別の判定に変える」から選びます。"),
    ("変えるとき", "K 変えた後の判定と、除外なら L 変えた後の除外理由を選び、M に理由を書いてください（理由は必須）。"
                   "「AI の判定に変える」は AI と同じ判定・同じ E の番号にします（E4 なら区分を選ぶ）。"
                   "含める・保留に変えた記録は全文段へ回します（その全文段は 1 問だけです）。"),
    ("1 回目のまま", "K・L は空のまま。M（理由）は任意です。"),
    ("AI の値について", "評価版の値は、抄録（一部は本文）を読んで AI が書いた予備判定で、人の判定の代わりではありません。"),
    ("保存したら", "上書き保存して、チャットで「記入表 2 を保存した」と伝えてください。"),
]


def e_num(s):
    m = re.match(r"\s*(E\d)", s or "")
    return m.group(1) if m else None


def first_round():
    """ログの ta1（追加候補）で除外の記録 → {ID: cells}（ログの順）。"""
    out = {}
    if not os.path.exists(C.LOG):
        return out
    for l in open(C.LOG, encoding="utf-8"):
        if not l.strip():
            continue
        d = json.loads(l)
        if d.get("stage") == "ta1" and C.is_cand_id(d["item"]) and d["item"].startswith("S") and d["cells"].get("M") == "除外":
            out[d["item"]] = d["cells"]
    return out


def appraisal():
    wb = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)
    def sheet(name):
        rows = list(wb[name].iter_rows(values_only=True))
        h = list(rows[3])
        return {r[0]: dict(zip(h, r)) for r in rows[4:] if r and r[0]}
    return sheet("Claudeスクリーニング案"), sheet("Claude適格性評価"), sheet("Claude方法論メモ")


def ai_values(i, scr, elig, meth):
    s, e, m = scr.get(i) or {}, elig.get(i) or {}, meth.get(i) or {}
    return [s.get("Claude予備判定（題名・抄録段）"), s.get("除外理由"), e.get("中心範囲の段"), e.get("用途判定（Claude）"),
            e.get("判定根拠（プロトコル §2）"), m.get("懸念・限界（判定には使わない）")]


def same_as_ai(cells, ai):
    v1, e1 = cells.get("M"), e_num(cells.get("N"))
    return ai[0] == v1 and (v1 != "除外" or e_num(ai[1]) == e1)


def build():
    if C.sha256(C.APPRAISAL) != C.APPRAISAL_SHA256:
        sys.exit("評価版の SHA-256 が記録と違う")
    fr = first_round()
    if not fr:
        sys.exit("ログに記入表 1 の除外の行が無い（記入表 1 を読んでから作る）")
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    jr = list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))
    title = {r[0]: r[3] for r in jr[C.JUDGE_HEADER_ROW:] if r and r[0]}
    scr, elig, meth = appraisal()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "はじめに"
    put(ws["A1"], TITLE).font = Font(bold=True, size=12)
    put(ws["A2"], f"作成: 記入表 1 を読んだ後 ／ 対象: 抄録段の 1 回目で除外にした {len(fr)} 件")
    for n, (k, v) in enumerate(INTRO, 4):
        put(ws.cell(n, 1), k).alignment = WRAP
        put(ws.cell(n, 2), v).alignment = WRAP
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 110
    fit_rows(ws, {"A": 16, "B": 110}, 4)

    w2 = wb.create_sheet("2 回目")
    put(w2["A1"], "抄録段で除外した記録｜2 回目（AI の予備判定を見て）").font = Font(bold=True, size=12)
    put(w2["A2"], "記入するのは黄色の見出しの列（J〜M）だけです。変えるときは K（除外なら L も）と M 理由が必須です。")
    for c, h in enumerate(HEADER, 1):
        cell = put(w2.cell(HR, c), h)
        cell.font = Font(bold=True)
        cell.alignment = WRAP
        if c in INPUT:
            cell.fill = YELLOW
    dv_same = DataValidation(type="list", formula1='"' + ",".join(SAME) + '"', allow_blank=True)
    dv_diff = DataValidation(type="list", formula1='"' + ",".join(DIFF) + '"', allow_blank=True)
    dv_v = DataValidation(type="list", formula1='"' + ",".join(VERDICTS) + '"', allow_blank=True)
    dv_e = DataValidation(type="list", formula1='"' + ",".join(ECODES) + '"', allow_blank=True)
    for dv in (dv_same, dv_diff, dv_v, dv_e):
        w2.add_data_validation(dv)
    for n, (i, cells) in enumerate(fr.items(), 1):
        r = HR + n
        ai = ai_values(i, scr, elig, meth)
        first = f"除外 ／ {cells.get('N')}" + (f" ／ メモ: {cells.get('O')}" if cells.get("O") else "")
        for c, v in enumerate([i, title.get(i), first] + ai, 1):
            put(w2.cell(r, c), v).alignment = WRAP
        for c in INPUT:
            w2.cell(r, c).fill = YELLOW
            w2.cell(r, c).alignment = WRAP
        (dv_same if same_as_ai(cells, ai) else dv_diff).add(f"J{r}")
        dv_v.add(f"K{r}")
        dv_e.add(f"L{r}")
    cw = dict(zip("ABCDEFGHIJKLM", (9, 40, 24, 12, 30, 14, 12, 60, 40, 16, 12, 16, 40)))
    for col, w in cw.items():
        w2.column_dimensions[col].width = w
    fit_rows(w2, cw, HR + 1)
    w2.freeze_panes = f"C{HR + 1}"
    wb.properties.creator = "判定者 1"
    wb.properties.lastModifiedBy = "判定者 1"
    return wb


def main():
    dry = "--dry-run" in sys.argv
    wb = build()
    if dry:
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", prefix="ta2-dry-")
        os.close(fd)
        wb.save(tmp)
        print("dry-run:", tmp)
        return
    lines = open(C.TA_SHA_RECORD, encoding="utf-8").read().splitlines() if os.path.exists(C.TA_SHA_RECORD) else []
    rec = next((l.split()[1] for l in lines if l.startswith("sheet2 ")), None)
    if os.path.exists(C.TA_SHEET2):
        if rec is None or C.sha256(C.TA_SHEET2) != rec:
            sys.exit("Downloads の記入表 2 が最後に書いたものと違う（記入が始まった可能性）。止まる")
    elif rec is not None:
        sys.exit("記録があるのに Downloads の記入表 2 が無い。止まる")
    fd, tmp = tempfile.mkstemp(suffix=".part", dir=C.DOWNLOADS, prefix=".tmp-ta2-")
    os.close(fd)
    try:
        wb.save(tmp)
        sha = C.sha256(tmp)
        if os.path.exists(C.TA_SHEET2) and C.sha256(C.TA_SHEET2) != rec:
            sys.exit("置き換えの直前に記入表 2 が変わった。止まる")
        os.makedirs(os.path.dirname(C.TA_SHEET2_ORIG), exist_ok=True)
        shutil.copyfile(tmp, C.TA_SHEET2_ORIG)
        os.replace(tmp, C.TA_SHEET2)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    lines = [l for l in lines if not l.startswith("sheet2 ")] + [f"sheet2 {sha} {os.path.basename(C.TA_SHEET2)}"]
    with open(C.TA_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"記入表 2: {sha}（{len(first_round())} 件）")


if __name__ == "__main__":
    main()
