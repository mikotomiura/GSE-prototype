"""抄録段の 1 回目の問い（AskUserQuestion）の答えを、セッションの記録から取り出す（判断 3）。

★ Claude は答えを手で写さない。問いの文・選択肢・答え・添えた文（notes）は Claude Code のセッションの記録
  （git の外・%USERPROFILE%\\.claude\\projects\\C--GSE-prototype\\<session>.jsonl）から読むだけ。
★ 取り出す問い（問いの文の先頭の印で見分ける）:
  - `【<候補番号>・抄録段 1 回目】` … 『追加候補』の判定（kind = ta1）
  - `【<候補番号>・除外理由】` … ta1 で「除外（ほかの理由）」の件の理由（kind = ta1e）
  - `【<R..>・探索の記録】` … 『探索の記録』の足す／判定（kind = s）
  - `【<R..>・除外理由】` … s で「足して除外」の件の理由（kind = se）
★ 出力:
  - git の外: `Downloads\\ai-fatigue-fulltext\\_abstracts\\ta-questions-verbatim.jsonl`（問いの逐語。抄録の訳・要約を含むのでコミットしない）
  - repo: `data/ta-answers.json`（項目・種類・選択肢・答え・notes・問いの逐語の SHA-256・セッションと行）
★ 止まる条件: 同じ項目・種類に答えが 2 つ以上／理由の問いが判定の問いの前か、判定が「ほかの理由」でない／
  答えが選択肢に無い（Other）のに `data/ta-overrides.json` に読み方が無い。
使い方: PYTHONIOENCODING=utf-8 uv run --with openpyxl python ta_from_session.py [--write]
        （セッションの ID は data/ta-sessions.txt に 1 行 1 つ。--write なしは数えるだけ）
"""
import hashlib
import json
import os
import re
import sys

import openpyxl

import common as C
import check_ta_sheet as K

PROJ = os.path.join(os.path.expanduser("~"), ".claude", "projects", "C--GSE-prototype")
SESSIONS = os.path.join(C.DATA, "ta-sessions.txt")
ANSWERS = os.path.join(C.DATA, "ta-answers.json")
OVERRIDES = os.path.join(C.DATA, "ta-overrides.json")
VERBATIM = os.path.join(C.FULLTEXT_DIR, "_abstracts", "ta-questions-verbatim.jsonl")
HEAD = re.compile(r"^【([A-Z0-9-]+)・(抄録段 1 回目|除外理由|探索の記録)】")

# 選択肢（固定の順・判断 3）。★ 読み方（セルの値への対応）は fill 側が独立に持つ
OPT_TA1 = ["含める", "保留", "除外 E4 背景（レビュー・尺度の原著・理論）", "除外（ほかの理由）"]
OPT_TA1E = ["E1", "E2", "E3"]
OPT_S = ["足さない", "足して含める", "足して保留", "足して除外"]
OPT_SE = ["E1", "E2", "E3", "E4 背景（レビュー・尺度の原著・理論）"]


def kind_of(item, tag):
    search = item.startswith("R")
    if tag == "抄録段 1 回目":
        return "ta1" if not search else None
    if tag == "探索の記録":
        return "s" if search else None
    return "se" if search else "ta1e"


def read_sessions():
    sids = [l.strip() for l in open(SESSIONS, encoding="utf-8") if l.strip() and not l.startswith("#")]
    out = []
    for sid in sids:
        uses = {}
        with open(os.path.join(PROJ, sid + ".jsonl"), encoding="utf-8") as f:
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
                        tur = tur if isinstance(tur, dict) else {}  # 断られた問いは結果が文字列（答えなし）
                        answers, notes = tur.get("answers") or {}, tur.get("annotations") or {}
                        for q in inp.get("questions", []):
                            m = HEAD.match(q.get("question", ""))
                            if not m or not answers.get(q["question"]):
                                continue
                            kind = kind_of(m.group(1), m.group(2))
                            if kind is None:
                                sys.exit(f"問いの印と項目が合わない: {m.group(0)}（{sid}:{ln0}）")
                            out.append({"item": m.group(1), "kind": kind, "question": q["question"],
                                        "options": [o.get("label") for o in q.get("options", [])],
                                        "answer": answers[q["question"]],
                                        "note": (notes.get(q["question"]) or {}).get("notes", "") or "",
                                        "answered_at": d.get("timestamp"),
                                        "source": {"session": sid, "line_question": ln0, "line_answer": ln}})
    return out


def check(recs, overrides):
    errs, seen = [], {}
    expect = {"ta1": OPT_TA1, "ta1e": OPT_TA1E, "s": OPT_S, "se": OPT_SE}
    for k, r in enumerate(recs):
        key = (r["item"], r["kind"])
        if key in seen:
            errs.append(f"答えが 2 つ: {key}")
        seen[key] = k
        if r["options"] != expect[r["kind"]]:
            errs.append(f"選択肢が固定の順と違う: {key} {r['options']}")
        if r["answer"] not in r["options"] and f"{r['item']}:{r['kind']}" not in overrides:
            errs.append(f"選択肢に無い答え（Other）で読み方が無い: {key} {r['answer']!r}")
    for (item, kind), k in seen.items():
        if kind in ("ta1e", "se"):
            parent = "ta1" if kind == "ta1e" else "s"
            want = "除外（ほかの理由）" if kind == "ta1e" else "足して除外"
            p = seen.get((item, parent))
            if p is None or p > k or recs[p]["answer"] != want:
                errs.append(f"理由の問いの前に「{want}」の答えが無い: {item}")
        if kind in ("ta1", "s"):
            want = "除外（ほかの理由）" if kind == "ta1" else "足して除外"
            if recs[k]["answer"] == want and (item, kind + "e") not in seen:
                errs.append(f"理由が未回答: {item}")
    return errs


def sheet_order():
    wb = openpyxl.load_workbook(C.TA_SHEET1_ORIG)
    cand = [x[1] for _, x in K.body(wb["追加候補"], 15)]
    src = K.sources()
    search = [x[1] for _, x in K.body(wb["探索の記録"], 14) if not (src["search"].get(x[1]) or {}).get("overlap")]
    return cand, search


def main():
    write = "--write" in sys.argv
    recs = read_sessions()
    overrides = json.load(open(OVERRIDES, encoding="utf-8")) if os.path.exists(OVERRIDES) else {}
    errs = check(recs, overrides)
    cand, search = sheet_order()
    got = {(r["item"], r["kind"]) for r in recs}
    rest_c = [i for i in cand if (i, "ta1") not in got]
    rest_s = [i for i in search if (i, "s") not in got]
    stray = sorted({r["item"] for r in recs} - set(cand) - set(search))
    if stray:
        errs.append(f"記入表に無い項目: {stray}")
    print(f"答え {len(recs)} 件（ta1 {sum(r['kind'] == 'ta1' for r in recs)}・ta1e {sum(r['kind'] == 'ta1e' for r in recs)}・"
          f"s {sum(r['kind'] == 's' for r in recs)}・se {sum(r['kind'] == 'se' for r in recs)}）")
    print(f"残り: 追加候補 {len(rest_c)} 件（次: {rest_c[:1]}・順 {len(cand) - len(rest_c) + 1}）・探索の記録 {len(rest_s)} 件")
    if errs:
        print("違反:\n" + "\n".join(errs))
        sys.exit(1)
    if not write:
        return
    os.makedirs(os.path.dirname(VERBATIM), exist_ok=True)
    with open(VERBATIM, "w", encoding="utf-8", newline="\n") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    out = [{k: v for k, v in r.items() if k != "question"} | {
        "question_sha256": hashlib.sha256(r["question"].encode("utf-8")).hexdigest()} for r in recs]
    with open(ANSWERS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"書いた: {os.path.relpath(ANSWERS, C.TASK)}・逐語は git の外")


if __name__ == "__main__":
    main()
