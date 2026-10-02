"""逐語のログ（screening-log.jsonl）に 1 行ずつ足す。既存の行は書き換えない（追記だけ）。

入力: JSON の配列（1 要素 = 1 つの質問と答え）を標準入力から。各要素の鍵:
  item / stage（1・1e・2・2e・q・x）/ question（問いの逐語）/ options（選択肢の逐語）/ answer（答えの逐語）/
  note（任意・ユーザーが添えた文）/ result（判定: verdict・use・ecode・elabel・basis・reason・reason_summary・next・date）
使い方: python log_add.py < records.json
"""
import datetime
import json
import sys

import common34 as C

REQ = {"item", "stage", "question", "options", "answer", "result"}
STAGES = {"1", "1e", "2", "2e", "q", "x"}


def main():
    recs = json.load(sys.stdin)
    n0 = 0
    try:
        with open(C.LOG, encoding="utf-8") as f:
            n0 = sum(1 for x in f if x.strip())
    except FileNotFoundError:
        pass
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    lines = []
    for k, r in enumerate(recs, 1):
        miss = REQ - set(r)
        if miss or r["stage"] not in STAGES or r["item"] not in C.IDS:  # x（群の抽出の確定）は群の先頭の件で記録する
            sys.exit(f"形が違う: {r.get('item')} {r.get('stage')} 欠け={miss}")
        r = {"seq": n0 + k, "logged_at": now, **r}
        lines.append(json.dumps(r, ensure_ascii=False) + "\n")
    with open(C.LOG, "a", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)
    print("ok", n0 + len(lines))


if __name__ == "__main__":
    main()
