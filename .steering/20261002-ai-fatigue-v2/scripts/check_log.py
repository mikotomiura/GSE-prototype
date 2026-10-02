"""本タスクのログ（screening-log.jsonl）の検査（判断 5・判断 6・引き継ぎ §2 の 1）。

★ 期待は書き込み側（build_log.py）と独立に組む: 答えは data/ta-answers.json を、AI の値は評価版を見出しの名前で、
  行の順は記入表 1 の原本（git の外・あれば）を、それぞれ自分で読む。答え → 判定の対応は本検査器が別に持つ（import しない）。
★ 規則は RULES_* に 1 行 1 つ（meta_mutate.py が 1 行ずつ外す）。違反の文は規則の名前で始める（selftest が名前で当てる）。
使い方: check_log.py [--session] | --selftest
        （--session: セッションの記録から答えを取り直し、data/ta-answers.json と一致するかも見る）
"""
import copy
import json
import os
import re
import sys

import openpyxl

import common as C

ANSWERS = os.path.join(C.DATA, "ta-answers.json")
VERBATIM = os.path.join(C.FULLTEXT_DIR, "_abstracts", "ta-questions-verbatim.jsonl")
STAGES = {"ta1", "ta1e", "ai_ta"}
N_JUDGE1, N_ALL = 71, 213
# 判断 5 に書いた判定者 1 の抄録段の内訳（★ この道具より前に decisions.md に記録した値）
JUDGE1_COUNTS = {"含める": 49, "保留": 15, "除外": 7}
# 答え（逐語）→ 判定（★ build_log.py とは別に持つ）
EXPECT_TA1 = {
    "含める": {"verdict": "含める"},
    "保留": {"verdict": "保留"},
    "除外 E4 背景（レビュー・尺度の原著・理論）": {"verdict": "除外", "ecode": "E4 背景（判定者 1 の選択のまま）",
                                         "intent": "範囲の外・背景として残す（一次研究でないの意味ではない・判断 6）"},
    "除外（ほかの理由）": {"verdict": "除外", "ecode": None, "pending": "ta1e"},
}
EXPECT_TA1E = {e: {"verdict": "除外", "ecode": e} for e in ("E1", "E2", "E3")}
ANSWER_KEYS = ("options", "answer", "note", "question_sha256", "answered_at")


def read_log(path):
    return [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]


def sources():
    s = {}
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))
    s["all"] = [r[0] for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]]
    s["prev"] = {json.loads(x)["item"] for x in open(C.PREV_LOG, encoding="utf-8") if x.strip()}
    s["answers"] = json.load(open(ANSWERS, encoding="utf-8"))
    # 評価版: 見出しの名前で引く
    ws = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)["Claudeスクリーニング案"]
    rr = list(ws.iter_rows(values_only=True))
    hr = next(k for k, r in enumerate(rr) if r and r[0] == "候補番号")
    h = list(rr[hr])
    s["ai"] = {r[0]: {"row": k + 1, "ta": r[h.index("Claude予備判定（題名・抄録段）")], "reason": r[h.index("除外理由")],
                      "col_ta": openpyxl.utils.get_column_letter(h.index("Claude予備判定（題名・抄録段）") + 1),
                      "col_reason": openpyxl.utils.get_column_letter(h.index("除外理由") + 1)}
               for k, r in enumerate(rr) if k > hr and r and r[0]}
    # 行の順: 記入表 1 の原本（git の外）の『追加候補』の B 列。無ければ判定者用ファイルの順の並べ替えの規則
    if os.path.exists(C.TA_SHEET1_ORIG):
        w1 = openpyxl.load_workbook(C.TA_SHEET1_ORIG, read_only=True)["追加候補"]
        s["order"] = [r[1] for r in list(w1.iter_rows(values_only=True))[4:] if r and r[1]]
        s["order_from"] = "記入表 1 の原本"
    else:
        from build_ta_sheet import order_cands
        data = [r for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0] and r[0] not in s["prev"]]
        s["order"] = [r[0] for r in order_cands(data)]
        s["order_from"] = "並べ替えの規則（原本なし）"
    s["verbatim"] = [json.loads(x)["question"] for x in open(VERBATIM, encoding="utf-8") if x.strip()] if os.path.exists(VERBATIM) else []
    s["sha"] = {"judge": C.JUDGE_FILE_SHA256, "appraisal": C.APPRAISAL_SHA256}
    return s


def r_sources(ctx):
    v = []
    for p, k in ((C.JUDGE_FILE, "judge"), (C.APPRAISAL, "appraisal")):
        if C.sha256(p) != ctx["src"]["sha"][k]:
            v.append(f"r_sources: 元の資料の SHA-256 が記録と違う: {os.path.basename(p)}")
    return v


def r_seq(ctx):
    v = []
    for k, r in enumerate(ctx["log"], 1):
        if r.get("seq") != k:
            v.append(f"r_seq: {k} 行目の seq が {r.get('seq')}")
            break
        if not r.get("logged_at"):
            v.append(f"r_seq: {k} 行目に logged_at が無い")
    return v


def r_stages(ctx):
    v = []
    for r in ctx["log"]:
        st = r.get("stage")
        if st not in STAGES:
            v.append(f"r_stages: {r.get('item')}: 段が語彙の外 {st!r}")
            continue
        if st in ("ta1", "ta1e"):
            if r.get("judge") != "判定者 1" or r.get("source") != "AskUserQuestion" or "appraisal_sha256" in r:
                v.append(f"r_stages: {r['item']}: 判定者 1 の段なのに判定者・出どころが違う")
        else:
            # ★ AI の行に判定者 1 の名前・答えの欄を置かない（判断 5: 評価版の値を判定者 1 の判定として書かない）
            if "AI" not in str(r.get("judge")) or "判定者 1" in str(r.get("judge")) or r.get("source") != "評価版" \
                    or any(k in r for k in ("answer", "options", "question_sha256", "session")):
                v.append(f"r_stages: {r['item']}: AI の段なのに判定者・出どころ・答えの欄が違う")
    return v


def r_cover(ctx):
    v = []
    want = [i for i in ctx["src"]["all"] if i not in ctx["src"]["prev"]]
    j1 = [r["item"] for r in ctx["log"] if r.get("stage") == "ta1"]
    ai = [r["item"] for r in ctx["log"] if r.get("stage") == "ai_ta"]
    if len(want) != N_ALL:
        v.append(f"r_cover: 判定者用ファイルの未判定が {len(want)} 件")
    if len(j1) != N_JUDGE1 or len(ai) != N_ALL - N_JUDGE1:
        v.append(f"r_cover: 判定者 1 {len(j1)} 件・AI {len(ai)} 件（期待 {N_JUDGE1}・{N_ALL - N_JUDGE1}）")
    if len(set(j1 + ai)) != len(j1 + ai):
        v.append("r_cover: 同じ記録が 2 回（判定者 1 と AI の重なり・重複）")
    if set(j1 + ai) != set(want):
        v.append(f"r_cover: 記録の集合が未判定の 213 件と違う（多い {sorted(set(j1 + ai) - set(want))[:3]}・"
                 f"無い {sorted(set(want) - set(j1 + ai))[:3]}）")
    if {r["item"] for r in ctx["log"]} & ctx["src"]["prev"]:
        v.append("r_cover: 前のタスクで判定した記録（S02-08 ほか・X01）がこのログにある")
    return v


def r_order(ctx):
    v = []
    pos = {i: k for k, i in enumerate(ctx["src"]["order"], 1)}
    lines = [r for r in ctx["log"] if r.get("stage") in ("ta1", "ai_ta")]
    if [r.get("order") for r in lines] != list(range(1, len(lines) + 1)):
        v.append("r_order: 順（order）が 1 から連続しない")
    for r in lines:
        if pos.get(r["item"]) != r.get("order"):
            v.append(f"r_order: {r['item']}: 順 {r.get('order')} が{ctx['src']['order_from']}の {pos.get(r['item'])} と違う")
            break
    if any(r.get("stage") == "ai_ta" for r in lines[:N_JUDGE1]) or any(r.get("stage") == "ta1" for r in lines[N_JUDGE1:]):
        v.append("r_order: 判定者 1 の 71 件が先頭（順 1〜71）でない")
    return v


def r_answers(ctx):
    """判定者 1 の行が data/ta-answers.json の答えと 1 対 1 で一致する（逐語・選択肢・notes・問いの SHA・セッションと行）。"""
    v = []
    want = [(a["item"], a["kind"], a) for a in ctx["src"]["answers"]]
    got = [(r["item"], r["stage"], r) for r in ctx["log"] if r.get("stage") in ("ta1", "ta1e")]
    if [(i, k) for i, k, _ in got] != [(i, k) for i, k, _ in want]:
        v.append("r_answers: 判定者 1 の行の並び（記録・段）が答えのファイルと違う")
        return v
    for (i, k, r), (_, _, a) in zip(got, want):
        if any(r.get(x) != a.get(x) for x in ANSWER_KEYS) or \
                (r.get("session"), r.get("line_question"), r.get("line_answer")) != \
                (a["source"]["session"], a["source"]["line_question"], a["source"]["line_answer"]):
            v.append(f"r_answers: {i}（{k}）: 答え・選択肢・notes・問いの SHA・出どころが答えのファイルと違う")
    return v


def r_ta1_result(ctx):
    v = []
    for r in ctx["log"]:
        if r.get("stage") == "ta1":
            want = EXPECT_TA1.get(r.get("answer"))
            if want is None or r.get("result") != want:
                v.append(f"r_ta1_result: {r['item']}: 判定が答え {r.get('answer')!r} の対応と違う")
    return v


def r_ta1e(ctx):
    """理由の行（ta1e）は、同じ記録の「除外（ほかの理由）」の行より後に 1 つだけある（聞いた順のまま）。"""
    v = []
    log = ctx["log"]
    for k, r in enumerate(log):
        if r.get("stage") == "ta1e":
            p = next((x for x in log[:k] if x.get("stage") == "ta1" and x.get("item") == r["item"]), {})
            if p.get("answer") != "除外（ほかの理由）":
                v.append(f"r_ta1e: {r['item']}: 理由の行より前に同じ記録の「除外（ほかの理由）」が無い")
            if r.get("result") != EXPECT_TA1E.get(r.get("answer")) or r.get("order") != p.get("order"):
                v.append(f"r_ta1e: {r['item']}: 理由の判定・順が答えと違う")
        if r.get("stage") == "ta1" and r.get("answer") == "除外（ほかの理由）":
            if sum(1 for x in log[k + 1:] if x.get("stage") == "ta1e" and x.get("item") == r["item"]) != 1:
                v.append(f"r_ta1e: {r['item']}: 「除外（ほかの理由）」の後に理由の行が 1 つでない")
    return v


def r_ai_values(ctx):
    v = []
    for r in ctx["log"]:
        if r.get("stage") != "ai_ta":
            continue
        a = ctx["src"]["ai"].get(r["item"])
        want_cells = {a["col_ta"]: a["ta"], a["col_reason"]: a["reason"]} if a else None
        want_head = {a["col_ta"]: "Claude予備判定（題名・抄録段）", a["col_reason"]: "除外理由"} if a else None
        if a is None or r.get("cells") != want_cells or r.get("headers") != want_head or r.get("row") != a["row"] \
                or r.get("sheet") != "Claudeスクリーニング案" or r.get("appraisal_sha256") != ctx["src"]["sha"]["appraisal"]:
            v.append(f"r_ai_values: {r['item']}: 評価版の値・行・列・SHA が評価版と違う")
    return v


def r_ai_result(ctx):
    v = []
    for r in ctx["log"]:
        if r.get("stage") != "ai_ta":
            continue
        a = ctx["src"]["ai"].get(r["item"]) or {}
        if a.get("ta") == "含める":
            want = {"verdict": "含める"}  # ★ 除外理由の列は全文段の理由（E6 など）。題名・抄録段の判定に付けない
        elif a.get("ta") == "除外":
            m = re.match(r"(E[123])（", a.get("reason") or "")
            want = {"verdict": "除外", "ecode": m.group(1), "ai_reason": a["reason"]} if m else None
        else:
            want = None
        if want is None or r.get("result") != want:
            v.append(f"r_ai_result: {r['item']}: AI の判定が評価版の題名・抄録段の予備判定と違う")
    return v


def r_counts(ctx):
    final = {}
    for r in ctx["log"]:
        if r.get("stage") in ("ta1", "ta1e"):
            final[r["item"]] = r.get("result", {}).get("verdict")
    got = {k: sum(1 for x in final.values() if x == k) for k in JUDGE1_COUNTS}
    return [] if got == JUDGE1_COUNTS else [f"r_counts: 判定者 1 の内訳 {got} が判断 5 の記録 {JUDGE1_COUNTS} と違う"]


def r_no_verbatim(ctx):
    """問いの逐語（抄録の訳・要約を含む）をログに載せない。"""
    v = []
    text = json.dumps(ctx["log"], ensure_ascii=False)
    if any("question" in r for r in ctx["log"]):
        v.append("r_no_verbatim: ログに question の欄がある（逐語は git の外・SHA-256 だけ）")
    for q in ctx["src"]["verbatim"]:
        body = q.split("\n", 1)[1] if "\n" in q else ""
        if len(body) >= 40 and body[:40] in text:
            v.append("r_no_verbatim: ログに問いの逐語の文がある")
            break
    return v


RULES_LOG = [
    r_sources,
    r_seq,
    r_stages,
    r_cover,
    r_order,
    r_answers,
    r_ta1_result,
    r_ta1e,
    r_ai_values,
    r_ai_result,
    r_counts,
    r_no_verbatim,
]


def check(log, src):
    ctx = {"log": log, "src": src}
    v = []
    for rule in RULES_LOG:
        try:
            v += rule(ctx)
        except Exception as e:
            v.append(f"{rule.__name__}: 例外 {type(e).__name__}: {e}")
    return v


def check_session(src):
    """セッションの記録（git の外）から取り直した答えが data/ta-answers.json と同じ。"""
    import hashlib
    import ta_from_session as T
    recs = T.read_sessions()
    got = [{k: x for k, x in r.items() if k != "question"} | {"question_sha256": hashlib.sha256(r["question"].encode("utf-8")).hexdigest()}
           for r in recs]
    return [] if got == src["answers"] else ["session: セッションの記録の答えが data/ta-answers.json と違う"]


def selftest():
    import build_log as B
    src = sources()
    base = B.build()
    ok = True

    def expect(name, log, must=None, s=None):
        nonlocal ok
        v = check(log, s or src)
        good = (not v) if must is None else any(x.startswith(must) for x in v)
        ok &= good
        print(("PASS" if good else "FAIL"), name, "" if good else v[:3])

    expect("陰性対照（書き込み側で作ったログ）", base)

    def m(fn):
        lg = copy.deepcopy(base)
        fn(lg)
        return lg

    def at(lg, stage, k=0):
        return [r for r in lg if r["stage"] == stage][k]

    def item(lg, i, stage="ta1"):
        return next(r for r in lg if r["item"] == i and r["stage"] == stage)

    def renum(lg):
        for k, r in enumerate(lg, 1):
            r["seq"] = k
        return lg

    expect("元の資料の SHA が違う", base, "r_sources", s={**src, "sha": {**src["sha"], "appraisal": "0" * 64}})
    expect("seq が飛ぶ", m(lambda lg: lg[5].__setitem__("seq", 99)), "r_seq")
    expect("logged_at が無い", m(lambda lg: lg[5].pop("logged_at")), "r_seq")
    expect("段が語彙の外", m(lambda lg: at(lg, "ai_ta").__setitem__("stage", "ta2")), "r_stages")
    expect("AI の行を判定者 1 と書く", m(lambda lg: at(lg, "ai_ta").__setitem__("judge", "判定者 1")), "r_stages")
    expect("AI の行に答えの欄", m(lambda lg: at(lg, "ai_ta").__setitem__("answer", "含める")), "r_stages")
    def drop_ai(lg):
        lg.remove(at(lg, "ai_ta", len([r for r in lg if r["stage"] == "ai_ta"]) - 1))  # 最後の AI の行（順は崩れない）
    expect("AI の行を 1 行消す", m(drop_ai), "r_cover")
    expect("前のタスクの記録を足す", m(lambda lg: lg.append({**copy.deepcopy(at(lg, "ai_ta")), "seq": len(lg) + 1, "item": "S02-08"})),
           "r_cover")
    expect("判定者 1 の記録を AI にも入れる（重なり）",
           m(lambda lg: at(lg, "ai_ta", 5).__setitem__("item", at(lg, "ta1", 2)["item"])), "r_cover")

    def swap(lg):
        a, b = at(lg, "ai_ta", 10), at(lg, "ai_ta", 11)
        a["order"], b["order"] = b["order"], a["order"]
    expect("AI の 2 件の順を入れ替える", m(swap), "r_order")
    expect("答えだけを変える（判定はそのまま）", m(lambda lg: item(lg, "S02-06").__setitem__("note", "メモ")), "r_answers")
    expect("問いの SHA を変える", m(lambda lg: item(lg, "S02-06").__setitem__("question_sha256", "0" * 64)), "r_answers")
    expect("判定だけを変える（答えはそのまま）",
           m(lambda lg: item(lg, "S02-06").__setitem__("result", {"verdict": "保留"})), "r_ta1_result")
    # ★ 判断 6: 「除外 E4 背景」を E4（一次研究でない）と書く
    expect("E4 背景を E4 と書く",
           m(lambda lg: item(lg, "S04-85").__setitem__("result", {"verdict": "除外", "ecode": "E4"})), "r_ta1_result")
    expect("E4 背景の意図を落とす",
           m(lambda lg: item(lg, "S04-85")["result"].pop("intent")), "r_ta1_result")
    expect("理由の行の判定を変える", m(lambda lg: item(lg, "S12-04", "ta1e").__setitem__("result", {"verdict": "除外", "ecode": "E3"})),
           "r_ta1e")

    def move_e(lg):
        e = item(lg, "S12-04", "ta1e")
        lg.remove(e)
        lg.insert(0, e)
        renum(lg)
    expect("理由の行を判定の前に置く", m(move_e), "r_ta1e")
    expect("AI の値を変える", m(lambda lg: at(lg, "ai_ta").__setitem__("row", 3)), "r_ai_values")
    expect("AI の値のセルを変える", m(lambda lg: at(lg, "ai_ta")["cells"].__setitem__(next(iter(at(lg, "ai_ta")["cells"])), "保留")),
           "r_ai_values")
    ai_in = next(r for r in base if r["stage"] == "ai_ta" and r["result"]["verdict"] == "含める" and r["cells"].get("F"))
    expect("AI の含めるの件に全文段の除外理由を付ける",
           m(lambda lg: next(r for r in lg if r["item"] == ai_in["item"])["result"].__setitem__("ecode", "E6")), "r_ai_result")
    expect("AI の判定を変える", m(lambda lg: next(r for r in lg if r["stage"] == "ai_ta" and r["result"]["verdict"] == "除外")
                                   .__setitem__("result", {"verdict": "含める"})), "r_ai_result")

    def flip(lg):  # 答えと判定を揃えて変える（r_answers も当たるが、内訳の規則が独立に落とすこと）
        r = item(lg, "S02-06")
        r["answer"], r["result"] = "保留", {"verdict": "保留"}
    expect("判定者 1 の内訳が判断 5 の記録と違う", m(flip), "r_counts")
    expect("ログに問いの逐語", m(lambda lg: item(lg, "S02-06").__setitem__("question", "【S02-06・抄録段 1 回目】…")), "r_no_verbatim")
    if src["verbatim"]:
        q = src["verbatim"][0]
        expect("ログの notes に問いの文", m(lambda lg: item(lg, "S02-06").__setitem__("note", q.split("\n", 1)[1][:60])), "r_no_verbatim")
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        sys.exit(0 if selftest() else 1)
    src = sources()
    v = check(read_log(C.LOG), src)
    if "--session" in a:
        v += check_session(src)
    print(f"（行の順の出どころ: {src['order_from']}）")
    for x in v:
        print("違反:", x)
    print(f"違反 {len(v)}")
    sys.exit(1 if v else 0)


if __name__ == "__main__":
    main()
