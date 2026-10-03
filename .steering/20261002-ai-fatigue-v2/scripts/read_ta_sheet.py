"""記入した記入表 1 を読み、ログ（screening-log.jsonl）に 1 記録 1 行で写す（design.md §6）。

- 先に `check_ta_sheet.check(..., mode="filled", final=True)` を通す（違反があれば何も書かない）。
- 段: 追加候補 = `ta1`／探索の記録 = `s`（候補に足すか）と、足した記録の `ta1`。答えはセルの値をそのまま（`cells`）。
- 探索で「足す」の記録に X の番号を R の順で振る（X02 から。X01 は前のタスク）→ `data/extra-records.json`。
- 記入した表の SHA-256 を `archive/ta-sheets-sha256.txt` に `sheet1_filled` として記録し、各行に `sheet_sha256` を持たせる。
- ★ 既に `ta1` の行があれば止まる（二重に写さない）。
使い方: uv run --with openpyxl python read_ta_sheet.py [--dry-run]
"""
import datetime
import json
import os
import sys

import openpyxl

import common as C
import check_ta_sheet as K

E4_PART = {"E4 背景（レビュー・尺度の原著・理論）": "背景", "E4 方法論": "方法論", "E4 訂正通知": "訂正通知"}
Q_CAND = ("記入表 1『追加候補』（題名・抄録段の 1 回目・評価版の値なし）: M 判定（含める／除外／保留）・"
          "N 除外理由（E1／E2／E3／E4 背景／E4 方法論／E4 訂正通知／E5／E7）・O メモ")
Q_ADD = "記入表 1『探索の記録』: K 候補に足す（足す／足さない）・N メモ"
Q_SEARCH = ("記入表 1『探索の記録』（足した記録の題名・抄録段の 1 回目・評価版の値なし）: L 判定（含める／除外／保留）・"
            "M 除外理由・N メモ")


def result(verdict, code, memo, basis, date):
    e = None if not code else ("E4" if code.startswith("E4") else code)
    return {"verdict": verdict, "ecode": e, "e4": E4_PART.get(code), "memo": memo or "", "basis": basis,
            "stage_name": "題名・抄録段", "date": date}


def main():
    dry = "--dry-run" in sys.argv
    if os.path.exists(C.LOG) and any(json.loads(l).get("stage") in ("ta1", "s") for l in open(C.LOG, encoding="utf-8")
                                     if l.strip()):
        sys.exit("ログに既に記入表 1 の行がある。止まる（二重に写さない）")
    src = K.sources()
    v, miss = K.check(C.TA_SHEET1, src, mode="filled", final=True)
    if v:
        sys.exit("記入表 1 に違反がある（check_ta_sheet.py --filled --final を見る）:\n" + "\n".join(v[:20]))
    sha = C.sha256(C.TA_SHEET1)
    wb = openpyxl.load_workbook(C.TA_SHEET1)
    status = json.load(open(C.ABSTRACT_STATUS, encoding="utf-8"))
    today = datetime.date.today().isoformat()
    n0 = sum(1 for l in open(C.LOG, encoding="utf-8") if l.strip()) if os.path.exists(C.LOG) else 0
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    recs = []

    def basis(i):
        return "抄録" if (status.get(i) or {}).get("chars") else "題名と書誌（抄録はリンク先）"

    for r, x in K.body(wb["追加候補"], 15):
        i, m, n, o = x[1], x[12], x[13], x[14]
        recs.append({"item": i, "stage": "ta1", "source": "記入表1", "sheet_sha256": sha, "question": Q_CAND,
                     "options": K.E_VERDICTS, "options_ecode": K.E_ECODES, "cells": {"M": m, "N": n, "O": o},
                     "answer": m, "result": result(m, n, o, basis(i), today)})
    extra, xn = [], 2
    for r, x in K.body(wb["探索の記録"], 14):
        rid = x[1]
        if (src["search"].get(rid) or {}).get("overlap"):
            continue
        k, l_, m, n = x[10], x[11], x[12], x[13]
        xid = f"X{xn:02d}" if k == "足す" else None
        recs.append({"item": rid, "stage": "s", "source": "記入表1", "sheet_sha256": sha, "question": Q_ADD,
                     "options": K.E_ADD, "cells": {"K": k, "N": n}, "answer": k,
                     "result": {"added": k == "足す", "as": xid, "memo": n or "", "date": today}})
        if xid:
            e = src["search"][rid]
            extra.append({"id": xid, "rid": rid, "title": e["title"], "source": f"探索の読む一覧（{rid}・前のタスクの review-search）",
                          "doi": e["key"] if e["key"].startswith("10.") else None, "year": e["year"], "venue": e.get("venue"),
                          "oa": e.get("oa"), "type": e.get("type"), "content": None})
            recs.append({"item": xid, "stage": "ta1", "source": "記入表1", "sheet_sha256": sha, "search_id": rid,
                         "question": Q_SEARCH, "options": K.E_VERDICTS, "options_ecode": K.E_ECODES,
                         "cells": {"L": l_, "M": m, "N": n}, "answer": l_, "result": result(l_, m, n, basis(rid), today)})
            xn += 1
    if dry:
        print(f"dry-run: {len(recs)} 行・足した記録 {len(extra)} 件")
        return
    with open(C.EXTRA_RECORDS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(extra, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(C.LOG, "a", encoding="utf-8", newline="\n") as f:
        for k, rr in enumerate(recs, 1):
            f.write(json.dumps({"seq": n0 + k, "logged_at": now, **rr}, ensure_ascii=False) + "\n")
    lines = open(C.TA_SHA_RECORD, encoding="utf-8").read().splitlines() if os.path.exists(C.TA_SHA_RECORD) else []
    lines = [l for l in lines if not l.startswith("sheet1_filled ")] + [f"sheet1_filled {sha} {os.path.basename(C.TA_SHEET1)}"]
    with open(C.TA_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"ログに {len(recs)} 行・足した記録 {len(extra)} 件（{', '.join(e['id'] + '=' + e['rid'] for e in extra)}）")


if __name__ == "__main__":
    main()
