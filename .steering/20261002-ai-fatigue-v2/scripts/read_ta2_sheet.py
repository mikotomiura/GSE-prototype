"""記入した記入表 2 を読み、ログに `ta2` の行を 1 記録 1 行で写す（design.md §7）。

- 先に `check_ta2_sheet.check(..., mode="filled", final=True)` を通す（違反があれば何も書かない）。
- 最終の判定: 「1 回目のまま」なら 1 回目（除外・E コード）、変えたなら K・L。含める・保留に変えた記録は全文段へ
  （`result.to_fulltext_after_ai` = true。その全文段は 1 問だけ）。理由（M）は逐語で `result.reason` に。
- ★ 既に `ta2` の行があれば止まる。`ta1` の行が無ければ止まる（順の保証）。
使い方: uv run --with openpyxl python read_ta2_sheet.py [--dry-run]
"""
import datetime
import json
import os
import sys

import openpyxl

import common as C
import check_ta2_sheet as K

E4_PART = {"E4 背景（レビュー・尺度の原著・理論）": "背景", "E4 方法論": "方法論", "E4 訂正通知": "訂正通知"}
Q = ("記入表 2『2 回目』（抄録段で除外した記録・評価版の AI の予備判定を見て）: J 2 回目・K 変えた後の判定・"
     "L 変えた後の除外理由・M 理由")


def main():
    dry = "--dry-run" in sys.argv
    stages = [json.loads(l).get("stage") for l in open(C.LOG, encoding="utf-8") if l.strip()] if os.path.exists(C.LOG) else []
    if "ta1" not in stages:
        sys.exit("ログに記入表 1 の行が無い。止まる")
    if "ta2" in stages:
        sys.exit("ログに既に記入表 2 の行がある。止まる（二重に写さない）")
    src = K.sources()
    v, _ = K.check(C.TA_SHEET2, src, mode="filled", final=True)
    if v:
        sys.exit("記入表 2 に違反がある（check_ta2_sheet.py --filled --final を見る）:\n" + "\n".join(v[:20]))
    sha = C.sha256(C.TA_SHEET2)
    wb = openpyxl.load_workbook(C.TA_SHEET2)
    today = datetime.date.today().isoformat()
    n0 = len(stages)
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    recs = []
    for r, x in K.body(wb["2 回目"]):
        i, j, k, l_, m = x[0], x[9], x[10], x[11], x[12]
        f, ai = src["first"][i], src["ai"][i]
        changed = j != "1 回目のまま"
        verdict, code = (k, l_) if changed else ("除外", f["N"])
        recs.append({"item": i, "stage": "ta2", "source": "記入表2", "sheet_sha256": sha, "question": Q,
                     "options": K.E_SAME if K.is_same(f, ai) else K.E_DIFF, "cells": {"J": j, "K": k, "L": l_, "M": m},
                     "answer": j,
                     "result": {"choice": j, "changed": changed, "verdict": verdict,
                                "ecode": None if not code else ("E4" if code.startswith("E4") else code),
                                "e4": E4_PART.get(code), "reason": m or "",
                                "ai": {"verdict": ai[0], "ecode": K.en(ai[1]) if ai[0] == "除外" else None},
                                "to_fulltext_after_ai": verdict in ("含める", "保留"), "basis": "抄録",
                                "stage_name": "題名・抄録段", "date": today}})
    if dry:
        print(f"dry-run: {len(recs)} 行・変えた {sum(r['result']['changed'] for r in recs)} 件")
        return
    with open(C.LOG, "a", encoding="utf-8", newline="\n") as fh:
        for k_, rr in enumerate(recs, 1):
            fh.write(json.dumps({"seq": n0 + k_, "logged_at": now, **rr}, ensure_ascii=False) + "\n")
    lines = open(C.TA_SHA_RECORD, encoding="utf-8").read().splitlines()
    lines = [l for l in lines if not l.startswith("sheet2_filled ")] + [f"sheet2_filled {sha} {os.path.basename(C.TA_SHEET2)}"]
    with open(C.TA_SHA_RECORD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"ログに {len(recs)} 行・変えた {sum(r['result']['changed'] for r in recs)} 件・全文段へ "
          f"{sum(r['result']['to_fulltext_after_ai'] for r in recs)} 件")


if __name__ == "__main__":
    main()
