"""変えた理由・保留の理由の問い（AskUserQuestion）の逐語を、セッションの記録から復元する（Codex の指摘・判断 14）。

★ 2 回目の後に重ねた「理由の問い」は、当時ログに独立の行として残さず、stage 2 の note に答えだけを入れた（判断 12）。
  問いの文と選択肢は Claude Code のセッションの記録（git の外・%USERPROFILE%\\.claude\\projects\\C--GSE-prototype\\<session>.jsonl）に
  残っていたので、そこから読むだけで取り出し、`reason-questions-restored.jsonl` に書く。ログ（screening-log.jsonl）は書き換えない。
★ 取り出すのは、問いの文に「理由はどれに近いですか」を含む AskUserQuestion だけ（除外のコードの問いは stage 1e としてログにある）。
★ 各行に、答えを持つログの行（stage 2 の note に「理由の問い」）の seq を付ける。対応が 1 対 1 でなければ止まる。
使い方: python restore_reason_questions.py <session-id> [<session-id> ...]
"""
import json
import os
import re
import sys

import common34 as C

PROJ = os.path.join(os.path.expanduser("~"), ".claude", "projects", "C--GSE-prototype")
OUT = os.path.join(C.TASK, "reason-questions-restored.jsonl")
MARK = "理由はどれに近いですか"
ANSWERED = re.compile(r"理由の問い[^。]*の答え: ")


def from_session(sid):
    path = os.path.join(PROJ, sid + ".jsonl")
    uses, out = {}, []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = (d.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if c.get("type") == "tool_use" and c.get("name") == "AskUserQuestion":
                    uses[c["id"]] = (ln, c["input"])
                elif c.get("type") == "tool_result" and c.get("tool_use_id") in uses:
                    ln0, inp = uses[c["tool_use_id"]]
                    tur = d.get("toolUseResult")
                    tur = tur if isinstance(tur, dict) else {}  # ★ 断られた問いは結果が文字列（答えなし）
                    answers, notes = tur.get("answers") or {}, tur.get("annotations") or {}
                    for q in inp.get("questions", []):
                        if MARK not in q.get("question", "") or not answers.get(q["question"]):
                            continue  # ★ 答えの無い問い（断られて聞き直した等）は採らない
                        out.append({"question": q["question"], "options": [o.get("label") for o in q.get("options", [])],
                                    "multiSelect": bool(q.get("multiSelect")), "answer": answers.get(q["question"]),
                                    "user_note": (notes.get(q["question"]) or {}).get("notes", ""),
                                    "answered_at": d.get("timestamp"),  # ★ 答えの行の時刻（問いの行の時刻ではない）
                                    "source": {"session": sid, "line_question": ln0, "line_answer": ln}})
    return out


def main(sids):
    log = [json.loads(x) for x in open(C.LOG, encoding="utf-8") if x.strip()]
    # 答えを持つログの行: stage 2 で note に「理由の問い … の答え: 」がある行（件ごとに 1 行）。
    # ★ AF002・AF003 の note は「理由の問いを重ねず」（問うていない）なので当たらない
    by_item = {}
    for r in log:
        if r["stage"] in ("2", "2e") and ANSWERED.search(r.get("note") or ""):
            if r["item"] in by_item:
                sys.exit(f"理由の問いの答えを持つログの行が 2 つある: {r['item']}")
            by_item[r["item"]] = r
    recs = [x for s in sids for x in from_session(s)]
    out, seen = [], set()
    for x in recs:
        ids = [i for i in C.IDS if f"【{i}" in x["question"] or f"{i}（" in x["question"]]
        if len(ids) != 1:
            sys.exit(f"問いの文から件が 1 つに決まらない: {ids} {x['question'][:60]}")
        i = ids[0]
        if i in seen or i not in by_item:
            sys.exit(f"件の対応が 1 対 1 でない: {i}")
        if not x["answer"] or ("の答え: " + x["answer"]) not in by_item[i]["note"]:
            sys.exit(f"答えがログの note と合わない: {i} {x['answer']!r}")
        seen.add(i)
        out.append({"item": i, "log_seq": by_item[i]["seq"], **x})
    if seen != set(by_item):
        sys.exit(f"ログに答えがあるのに問いが見つからない: {sorted(set(by_item) - seen)}")
    out.sort(key=lambda x: x["log_seq"])
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in out)
    print("ok", len(out), OUT)


if __name__ == "__main__":
    main(sys.argv[1:])
