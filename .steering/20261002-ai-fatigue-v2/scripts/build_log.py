"""本タスクのログ（screening-log.jsonl）を作る（判断 5・判断 6・引き継ぎ §2 の 1）。

1 行 1 記録。段（stage）は 3 つで、判定者 1 と AI を混ぜない:
  - `ta1`   … 判定者 1 の題名・抄録段（順 1〜71）。data/ta-answers.json（セッションの記録から ta_from_session.py が取り出した答え）を写す。
  - `ta1e`  … `ta1` で「除外（ほかの理由）」を選んだ件の理由（S12-04 = E2）。
  - `ai_ta` … 判定者 1 が判定していない残り 142 件（順 72〜213）。評価版（Claude 版・`ed788f53…`）の『Claudeスクリーニング案』の
              題名・抄録段の予備判定をそのまま写す。★ 判定者 1 の判定ではない（判断 5）。新しい AI の判定は作らない。
★ 問いの逐語は抄録の訳・要約を含むので、ログには載せない（SHA-256 だけ・逐語は git の外）。
★ 答え → 判定の対応はここに置き、検査器（check_log.py）は別に同じ対応を持つ（import しない）。
★ 前のタスクのログ（17 行・S02-08 など追加候補の 7 件と X01）は読むだけ。その記録はこのログに入れない。
使い方: PYTHONIOENCODING=utf-8 uv run --with openpyxl python build_log.py [--write]
        （--write なしは数えるだけ。既にログがあり中身が違えば止まる）
"""
import json
import os
import sys

import openpyxl

import common as C
from build_ta_sheet import order_cands

ANSWERS = os.path.join(C.DATA, "ta-answers.json")
JUDGE1 = "判定者 1"
AI = "AI（評価版・Claude の予備判定）"
SCR_SHEET = "Claudeスクリーニング案"
COL_TA = "Claude予備判定（題名・抄録段）"
COL_REASON = "除外理由"
LOGGED_AT = "2026-10-03"
# 判断 6: 判定者 1 の「除外 E4 背景」は、意図が「範囲の外・背景として残す」（一次研究でないの意味ではない）
E4_BG_ANSWER = "除外 E4 背景（レビュー・尺度の原著・理論）"
E4_BG_CODE = "E4 背景（判定者 1 の選択のまま）"
E4_BG_INTENT = "範囲の外・背景として残す（一次研究でないの意味ではない・判断 6）"


def ta1_result(answer):
    """判定者 1 の抄録段の答え（逐語）→ 判定。"""
    if answer == "含める":
        return {"verdict": "含める"}
    if answer == "保留":
        return {"verdict": "保留"}
    if answer == E4_BG_ANSWER:
        return {"verdict": "除外", "ecode": E4_BG_CODE, "intent": E4_BG_INTENT}
    if answer == "除外（ほかの理由）":
        return {"verdict": "除外", "ecode": None, "pending": "ta1e"}
    sys.exit(f"読めない答え: {answer!r}")


def ta1e_result(answer):
    if answer in ("E1", "E2", "E3"):
        return {"verdict": "除外", "ecode": answer}
    sys.exit(f"読めない理由: {answer!r}")


def ai_result(ta, reason):
    """評価版の題名・抄録段の予備判定 → 判定。★ 除外理由の列は、題名・抄録段で除外の件だけその段の理由（含めるの件は全文段の理由）。"""
    if ta == "含める":
        return {"verdict": "含める"}
    if ta == "除外":
        code = (reason or "")[:2]
        if code not in ("E1", "E2", "E3"):
            sys.exit(f"評価版の除外理由が読めない: {reason!r}")
        return {"verdict": "除外", "ecode": code, "ai_reason": reason}
    sys.exit(f"評価版の題名・抄録段の予備判定が読めない: {ta!r}")


def unjudged_in_order():
    """判定者用ファイルの『追加候補』から、前のタスクで判定した記録を除いた 213 件（記入表 1 の行の順）。"""
    if C.sha256(C.JUDGE_FILE) != C.JUDGE_FILE_SHA256:
        sys.exit("判定者用ファイルの SHA-256 が記録と違う")
    rows = list(openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)[C.JUDGE_SHEET].iter_rows(values_only=True))
    data = [r for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]]
    judged = {json.loads(x)["item"] for x in open(C.PREV_LOG, encoding="utf-8") if x.strip()}
    return [r[0] for r in order_cands([r for r in data if r[0] not in judged])]


def appraisal_rows():
    """評価版『Claudeスクリーニング案』: 候補番号 → (シートの行番号, 列の文字 → 値)。"""
    if C.sha256(C.APPRAISAL) != C.APPRAISAL_SHA256:
        sys.exit("評価版の SHA-256 が記録と違う")
    ws = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)[SCR_SHEET]
    rows = list(ws.iter_rows(values_only=True))
    hr = next(k for k, r in enumerate(rows) if r and r[0] == "候補番号")
    h = list(rows[hr])
    ct, cr = h.index(COL_TA), h.index(COL_REASON)
    letter = openpyxl.utils.get_column_letter
    return {r[0]: (k + 1, {letter(ct + 1): r[ct], letter(cr + 1): r[cr]}, {letter(ct + 1): COL_TA, letter(cr + 1): COL_REASON})
            for k, r in enumerate(rows) if k > hr and r and r[0]}


def build():
    order = unjudged_in_order()
    if len(order) != 213:
        sys.exit(f"未判定の追加候補が {len(order)} 件（213 のはず）")
    answers = json.load(open(ANSWERS, encoding="utf-8"))
    ta1 = [a for a in answers if a["kind"] == "ta1"]
    ta1e = {a["item"]: a for a in answers if a["kind"] == "ta1e"}
    if [a["item"] for a in ta1] != order[:len(ta1)]:
        sys.exit("判定者 1 の答えの順が記入表 1 の行の順の先頭と合わない")
    ai = appraisal_rows()
    out = []

    def add(rec):
        out.append({"seq": len(out) + 1, "logged_at": LOGGED_AT, **rec})

    # ★ 答えのファイルの順（＝聞いた順）のまま写す。理由の問い（ta1e）は判定の問いの後に別の回で聞いたので、その位置に置く
    order_of = {a["item"]: n for n, a in enumerate(ta1, 1)}
    if set(ta1e) - set(order_of):
        sys.exit("理由の答えに判定の答えが無い")
    for a in answers:
        if a["kind"] not in ("ta1", "ta1e"):
            sys.exit(f"想定外の種類の答え: {a['kind']}")
        result = ta1_result(a["answer"]) if a["kind"] == "ta1" else ta1e_result(a["answer"])
        add({"item": a["item"], "stage": a["kind"], "order": order_of[a["item"]], "judge": JUDGE1, "source": "AskUserQuestion",
             "session": a["source"]["session"], "line_question": a["source"]["line_question"],
             "line_answer": a["source"]["line_answer"], "answered_at": a["answered_at"], "question_sha256": a["question_sha256"],
             "options": a["options"], "answer": a["answer"], "note": a["note"], "result": result})
    for n, i in enumerate(order[len(ta1):], len(ta1) + 1):
        row, cells, headers = ai[i]
        add({"item": i, "stage": "ai_ta", "order": n, "judge": AI, "source": "評価版", "appraisal_sha256": C.APPRAISAL_SHA256,
             "sheet": SCR_SHEET, "row": row, "headers": headers, "cells": cells,
             "result": ai_result(cells[next(k for k, v in headers.items() if v == COL_TA)],
                                 cells[next(k for k, v in headers.items() if v == COL_REASON)])})
    return out


def dump(recs):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)


def main():
    recs = build()
    text = dump(recs)
    n = {s: sum(r["stage"] == s for r in recs) for s in ("ta1", "ta1e", "ai_ta")}
    print(f"ログ {len(recs)} 行（ta1 {n['ta1']}・ta1e {n['ta1e']}・ai_ta {n['ai_ta']}）")
    if os.path.exists(C.LOG):
        old = open(C.LOG, encoding="utf-8", newline="").read()
        if old == text:
            print("既にあるログと同じ")
            return
        sys.exit("既にあるログと中身が違う（止まって確かめる）")
    if "--write" in sys.argv[1:]:
        with open(C.LOG, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("書いた:", os.path.relpath(C.LOG, C.TASK))


if __name__ == "__main__":
    main()
