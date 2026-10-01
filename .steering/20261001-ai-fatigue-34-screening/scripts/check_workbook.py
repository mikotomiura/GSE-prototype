"""ワークブックの写しと逐語のログの検査（design.md §6・requirement.md の受け入れ条件）。

(1) 元のシートのセル（数式は式のまま）が元のファイルと同じ（入力欄を除く）。シートの並びも同じで、足したシートは `判定者1_` で始まる。
(2) 入力欄の値が入力規則の語彙の中にある。判定者2・最終判定は 34 行とも `未判定`。
(3) ログの最終の答え → 本検査器が独自に持つ対応表 → 期待の値、を写しと突き合わせる（書き込み側の表を import しない）。
(4) ログの形: 1 回目（stage 1）の選択肢が種類ごとの固定の集合と完全に一致し、1 回目（1・1e）の問いに AI の判定・推奨の語が無い。2 回目は 1 回目の後。
    全文確認（H）・品質評価（I）を、ログの x（抽出の確定）・q（品質の確定）から独立に計算して突き合わせる。A 列の ID も見る。
(5) --final: 34 件すべて判定済み・各件に 1 回目（stage 1）と 2 回目（stage 2/2e）がある・含めた一次研究で全文ありは品質評価が完了・
    『AI判定比較』の人間用途判定が 34 行とも入っている・『判定者1_はじめに』に研究者への注意（判定者 2 に渡さない・Claude の関与）がある。
(6) 『判定者1_確認の結果』: 区分ごとの件数（12／34／8）・ID の順・結果と経路の語彙・空欄・元の DB の文との対応（--final では必須）。
(7) 『判定者1_問いと答え』: ログと 1 行ずつ一致する（--final では必須）。
(8) 『判定者1_品質評価』の ID = 品質を確定した含める一次研究。
--selftest: 既知の答えの検算と、変異（入力欄の外のセル・判定者2・ログと写しのずれ・推奨の印・余分なシート・確認の結果・問いと答え・
    品質評価のシート・H と I）がそれぞれ赤になること。禁止語の規則の単体の検査と、--final の対照つきの検査。
使い方: python check_workbook.py [--final] [--selftest]
"""
import copy
import json
import os
import re
import sys
import tempfile

import openpyxl

import common34 as C

VOCAB = {
    ("スクリーニング", "D"): {"未判定", "含める", "除外", "保留"},
    ("スクリーニング", "H"): {"未完了", "進行中", "完了", "入手不可", "対象外"},
    ("スクリーニング", "I"): {"未実施", "進行中", "完了", "対象外"},
    ("AI判定比較", "D"): {None, "中心候補", "背景保持", "方法論保持", "訂正連結", "除外", "保留"},
}
PRIMARY = {"直接研究", "隣接研究"}
# 1 回目の選択肢（design.md §3・固定の順）
STAGE1_OPTIONS = {
    "primary": ["含める（中心-A）", "含める（中心-B）", "除外", "保留"],
    "other": ["含める（一次研究として読む）", "除外 E4（保持の区分は対応表で決まる）", "除外（E4 以外）", "保留"],
}
# ★ 1 回目（stage 1・1e）の問いと選択肢に出てはいけない語。大文字小文字を区別しない（2026-10-02 に広げた・判断 12）
# ★ 製品名の ChatGPT（項目文の逐語に出る・AF004）は GPT 版の判定ではないので除く（判断 4）。ただし「ChatGPT 版」は赤
STAGE1_BANNED = re.compile(r"recommend|推奨|おすすめ|勧め|AI\s*の?\s*(判定|評価|2\s*版)|適格性評価|(?<!Chat)GPT|ChatGPT\s*版|"
                           r"Claude|中心候補", re.I)
# ★ 文献の中身として問いに載せた句（AI の推奨ではない）。件と逐語の句を対で限る（判断 9・12）
STAGE1_EXEMPT = {
    "AF031": ["（公開・登録を勧める）"],
    "AF032": ["選別は 2 名が独立に行うのが一般に推奨"],
}


def stage1_banned(item, question, options):
    t = (question or "") + "\n" + "\n".join(options or [])  # ★ 区切りを入れる（問いの末尾と選択肢の先頭がつながらない）
    for p in STAGE1_EXEMPT.get(item, []):
        t = t.replace(p, "")
    return STAGE1_BANNED.search(t)
# 答え → 期待（design.md §2.2）。★ 書き込み側（write_workbook.py）とは別に持つ
EXPECT_HUMAN = {
    ("含める", "中心-A"): "中心候補", ("含める", "中心-B"): "中心候補",
    ("除外", "E2"): "背景保持", ("除外", "E1"): "除外", ("除外", "E3"): "除外",
    ("除外", "E5"): "除外", ("除外", "E7"): "除外", ("保留", None): "保留", ("除外", "E6"): "保留",
}
EXPECT_E4 = {"既存レビュー": "背景保持", "尺度・理論": "背景保持", "方法論": "方法論保持", "訂正通知": "訂正連結",
             "直接研究": "背景保持", "隣接研究": "背景保持"}


def expect_human(result, kind):
    v, e = result["verdict"], result.get("ecode")
    if v == "含める":
        return EXPECT_HUMAN[(v, result["use"])]
    if v == "保留":
        return "保留"
    if e == "E4":
        return EXPECT_E4[kind]
    return EXPECT_HUMAN[(v, e)]


def read_log(path):
    if not os.path.exists(path):
        return []
    return [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]


# 『判定者1_確認の結果』の形（design.md §2.1・requirement の受け入れ条件 5・2026-10-02 に足した）
CHECKS_SHEET = C.ADDED_PREFIX + "確認の結果"
CHECKS_HEADER = ["区分", "対象ID", "確認すべきこと（逐語）", "結果", "分かったこと", "原文の箇所", "確かめた経路", "記録の場所"]
CHECKS_RESULT = {"一次で確認", "一次で一部確認", "一次で否定", "入手不可", "研究者の確認待ち", "未着手"}
CHECKS_ROUTE = {"メインが原文で", "メインが要点を原文で（細部は抽出だけ）", "サブエージェントの抽出だけ",
                "抄録・無料のプレビューだけ", "該当なし（作業の記録）"}
CHECKS_PARTS = [("確認事項", 12), ("次の確認・作業", 34), ("メモ", 8)]


QUALITY_SHEET = C.ADDED_PREFIX + "品質評価"
INTRO_SHEET = C.ADDED_PREFIX + "はじめに"
INTRO_MUST = ["判定者 2 に渡さない", "Claude の関与"]
LOG_SHEET = C.ADDED_PREFIX + "問いと答え"
LOG_HEADER = ["seq", "ID", "段", "問い（逐語）", "選択肢", "答え", "補足（note）"]


def check_log_sheet(w, log, final):
    """研究者が読めるログの写しが、repo のログと 1 行ずつ一致する（seq・ID・段・問い・答え）。"""
    if LOG_SHEET not in w.sheetnames:
        return [f"{LOG_SHEET} が無い（--final）"] if final else []
    ws = w[LOG_SHEET]
    if [ws.cell(4, c).value for c in range(1, len(LOG_HEADER) + 1)] != LOG_HEADER:
        return [f"{LOG_SHEET}: 見出しが違う"]
    rows = [[ws.cell(r, c).value for c in range(1, len(LOG_HEADER) + 1)] for r in range(5, ws.max_row + 1)]
    rows = [x for x in rows if any(v not in (None, "") for v in x)]
    if len(rows) != len(log):
        return [f"{LOG_SHEET}: 行数 {len(rows)} がログの {len(log)} と違う"]
    errs = []
    for n, (x, rec) in enumerate(zip(rows, log), 5):
        if [x[0], x[1], x[2], x[3], x[5]] != [rec.get("seq"), rec.get("item"), rec.get("stage"), rec.get("question"), rec.get("answer")]:
            errs.append(f"{LOG_SHEET}!A{n}: ログの seq {rec.get('seq')} と一致しない")
    return errs


def original_checks_texts(o):
    """元の DB の『確認事項』（対象ID・次の確認作業）と『AI適格性評価』（ID → 次の確認・作業）。"""
    rows = list(o["確認事項"].iter_rows(values_only=True))
    k0 = next(n for n, r in enumerate(rows) if r and r[0] == "対象ID")
    kak = [(r[0], r[3]) for r in rows[k0 + 1:] if r and r[0]]
    rows = list(o["AI適格性評価"].iter_rows(values_only=True))
    hdr = next(r for r in rows if r and r[0] == "ID")
    col = list(hdr).index("次の確認・作業")
    nxt = {r[0]: r[col] for r in rows if r and r[0] and str(r[0]).startswith("AF")}
    return kak, nxt


def check_checks_sheet(w, final, o=None):
    if CHECKS_SHEET not in w.sheetnames:
        return [f"{CHECKS_SHEET} が無い（--final）"] if final else []
    ws, errs = w[CHECKS_SHEET], []
    if [ws.cell(4, c).value for c in range(1, len(CHECKS_HEADER) + 1)] != CHECKS_HEADER:
        errs.append(f"{CHECKS_SHEET}: 見出しが違う")
        return errs
    rows = [[ws.cell(r, c).value for c in range(1, len(CHECKS_HEADER) + 1)] for r in range(5, ws.max_row + 1)]
    rows = [x for x in rows if any(v not in (None, "") for v in x)]
    want = [p for p, n in CHECKS_PARTS for _ in range(n)]
    if [x[0] for x in rows] != want:
        errs.append(f"{CHECKS_SHEET}: 区分の並び・件数が 確認事項 12／次の確認・作業 34／メモ 8 でない（{len(rows)} 行）")
    nxt = [x[1] for x in rows if x[0] == "次の確認・作業"]
    if nxt != C.IDS:
        errs.append(f"{CHECKS_SHEET}: 次の確認・作業の対象IDが AF001〜AF034 の順でない")
    for n, x in enumerate(rows, 5):
        if x[3] not in CHECKS_RESULT:
            errs.append(f"{CHECKS_SHEET}!D{n}: 結果が語彙の外 {x[3]!r}")
        if x[6] not in CHECKS_ROUTE:
            errs.append(f"{CHECKS_SHEET}!G{n}: 経路が語彙の外 {x[6]!r}")
        for c, name in ((2, "確認すべきこと"), (4, "分かったこと"), (5, "原文の箇所"), (7, "記録の場所")):
            if not str(x[c] if x[c] is not None else "").strip():
                errs.append(f"{CHECKS_SHEET}!{'ABCDEFGH'[c]}{n}: {name}が空")
    # 元の DB の文との対応（★ 取り違え・重複は件数が合っても赤にする）
    if o is not None and not errs:
        kak, nxt = original_checks_texts(o)
        part = {p: [x for x in rows if x[0] == p] for p, _ in CHECKS_PARTS}
        for x, (tid, text) in zip(part["確認事項"], kak):
            if x[1] != tid or str(text) not in str(x[2]):
                errs.append(f"{CHECKS_SHEET}: 確認事項 {x[1]!r} の行が元の『確認事項』（{tid}）の文を含まない")
        for x in part["次の確認・作業"]:
            if str(x[2]) != str(nxt.get(x[1])):
                errs.append(f"{CHECKS_SHEET}: 次の確認・作業 {x[1]} の文が元の『AI適格性評価』と違う")
    return errs


def check(copy_path, log_path, final=False, original=C.ORIGINAL):
    errs = []
    o = openpyxl.load_workbook(original)
    w = openpyxl.load_workbook(copy_path)
    # (1)
    on = o.sheetnames
    if w.sheetnames[:len(on)] != on:
        errs.append(f"元のシートの並びが違う: {w.sheetnames[:len(on)]}")
    for extra in w.sheetnames[len(on):]:
        if not extra.startswith(C.ADDED_PREFIX):
            errs.append(f"足したシートの名前が {C.ADDED_PREFIX} で始まらない: {extra}")
    allowed = {(s, f"{col}{r}") for s, cols in C.INPUT_COLS.items() for col in cols
               for r in range(C.FIRST_ROW, C.FIRST_ROW + 34)}
    for s in on:
        if s not in w.sheetnames:
            continue
        a, b = o[s], w[s]
        mr, mc = max(a.max_row, b.max_row), max(a.max_column, b.max_column)
        for r in range(1, mr + 1):
            for c in range(1, mc + 1):
                ref = f"{openpyxl.utils.get_column_letter(c)}{r}"
                if (s, ref) in allowed:
                    continue
                if a.cell(r, c).value != b.cell(r, c).value:
                    errs.append(f"入力欄の外のセルが変わった: {s}!{ref}")
    scr, cmp_ = w["スクリーニング"], w["AI判定比較"]
    kind = {scr.cell(r, 1).value: scr.cell(r, 3).value for r in range(C.FIRST_ROW, C.FIRST_ROW + 34)}
    # (2)
    for (s, col), voc in VOCAB.items():
        for r in range(C.FIRST_ROW, C.FIRST_ROW + 34):
            v = w[s][f"{col}{r}"].value
            if v not in voc:
                errs.append(f"語彙の外: {s}!{col}{r}={v!r}")
    for r in range(C.FIRST_ROW, C.FIRST_ROW + 34):
        for col in ("E", "F"):
            if scr[f"{col}{r}"].value != "未判定":
                errs.append(f"判定者2・最終判定が未判定でない: スクリーニング!{col}{r}={scr[f'{col}{r}'].value!r}")
    # (3)(4)
    log = read_log(log_path)
    seen1, seen2, final_res, qrec, xitems = {}, {}, {}, {}, set()
    for n, rec in enumerate(log, 1):
        i, st = rec.get("item"), rec.get("stage")
        if i not in kind:
            errs.append(f"ログ {n}: 知らない件 {i}")
            continue
        if st == "1":
            want = STAGE1_OPTIONS["primary" if kind[i] in PRIMARY else "other"]
            if rec.get("options") != want:
                errs.append(f"ログ {n} {i}: 1 回目の選択肢が固定の集合と違う: {rec.get('options')}")
            seen1[i] = True
        if st in ("1", "1e") and stage1_banned(i, rec.get("question"), rec.get("options")):
            errs.append(f"ログ {n} {i}: 1 回目の問いに AI の判定・推奨の語がある")
        if st in ("1", "1e", "2", "2e"):
            if st in ("2", "2e"):
                if i not in seen1:
                    errs.append(f"ログ {n} {i}: 2 回目が 1 回目より前")
                seen2[i] = True
            final_res[i] = rec["result"]
        if st == "q":
            qrec[i] = rec
        if st == "x":
            xitems.update(rec["result"].get("items", []))
    # 行と ID の対応（★ 書き込み側の assert とは別に持つ）
    for k, i in enumerate(C.IDS):
        r = C.FIRST_ROW + k
        if scr.cell(r, 1).value != i or cmp_.cell(r, 1).value != i:
            errs.append(f"{i}: 『スクリーニング』『AI判定比較』の A{r} が ID と合わない")
    for k, i in enumerate(C.IDS):
        r = C.FIRST_ROW + k
        d = scr[f"D{r}"].value
        if i not in final_res:
            if d != "未判定":
                errs.append(f"{i}: ログに判定が無いのに判定者1={d!r}")
            continue
        res = final_res[i]
        if d != res["verdict"]:
            errs.append(f"{i}: 判定者1={d!r} がログの最終 {res['verdict']!r} と違う")
        g = scr[f"G{r}"].value or ""
        if res["verdict"] == "除外":
            if not re.match(rf"^{res.get('ecode')}\b", g) or not re.match(r"^E[1-7]\b", g):
                errs.append(f"{i}: 除外理由 {g!r} がログの {res.get('ecode')!r} と合わない")
        elif g:
            errs.append(f"{i}: 除外でないのに除外理由がある {g!r}")
        iv = scr[f"I{r}"].value
        if res["verdict"] == "除外" and iv != "対象外":
            errs.append(f"{i}: 除外なのに品質評価={iv!r}")
        if res["verdict"] == "含める" and kind[i] not in PRIMARY and iv != "対象外":
            errs.append(f"{i}: 一次研究でない件の品質評価={iv!r}")
        if res.get("basis") == "抄録" and scr[f"H{r}"].value != "入手不可":
            errs.append(f"{i}: 材料が抄録なのに全文確認={scr[f'H{r}'].value!r}")
        # 全文確認（H）・品質評価（I）を、ログの x（抽出の確定）と q（品質の確定）から独立に計算する（design §2.1）
        want_h = "入手不可" if res.get("basis") == "抄録" else ("完了" if i in xitems else "進行中")
        if scr[f"H{r}"].value != want_h:
            errs.append(f"{i}: 全文確認={scr[f'H{r}'].value!r} がログからの期待 {want_h!r} と違う")
        if res["verdict"] == "含める" and kind[i] in PRIMARY:
            q = qrec.get(i)
            if q is None:
                want_i = "未実施"
            elif res.get("basis") == "抄録" or str(q.get("answer", "")).startswith("保留"):
                want_i = "進行中"
            else:
                want_i = "完了"
        elif res["verdict"] == "保留":
            want_i = "未実施"
        else:
            want_i = "対象外"
        if iv != want_i:
            errs.append(f"{i}: 品質評価={iv!r} がログからの期待 {want_i!r} と違う")
        if not (scr[f"J{r}"].value or "").startswith("用途: "):
            errs.append(f"{i}: 自由記入が規則の形でない")
        hu = cmp_[f"D{r}"].value
        if hu is not None and hu != expect_human(res, kind[i]):
            errs.append(f"{i}: 人間用途判定 {hu!r} が期待 {expect_human(res, kind[i])!r} と違う")
    # (6) 『判定者1_確認の結果』（あれば常に・--final では必須）
    errs += check_checks_sheet(w, final, o)
    # (7) 『判定者1_問いと答え』（研究者が読めるログの写し）: ログと 1 行ずつ一致する
    errs += check_log_sheet(w, log, final)
    # (8) 『判定者1_品質評価』の ID = 含めた一次研究で品質を確定（q）した件
    if QUALITY_SHEET in w.sheetnames:
        ws = w[QUALITY_SHEET]
        got = {ws.cell(rr, 1).value for rr in range(5, ws.max_row + 1)} - {None}
        want_q = {i for i in qrec if i in final_res and final_res[i]["verdict"] == "含める" and kind[i] in PRIMARY}
        if got != want_q:
            errs.append(f"{QUALITY_SHEET}: ID {sorted(got)} が品質を確定した含める一次研究 {sorted(want_q)} と違う")
    # (9) 『判定者1_はじめに』に研究者への注意がある（判定者 2 に渡さない・Claude の関与）
    if final:
        intro = " ".join(str(c.value or "") for row in w[INTRO_SHEET].iter_rows() for c in row) if INTRO_SHEET in w.sheetnames else ""
        for must in INTRO_MUST:
            if must not in intro:
                errs.append(f"{INTRO_SHEET}: 「{must}」の行が無い（--final）")
    # (5)
    if final:
        for k, i in enumerate(C.IDS):
            r = C.FIRST_ROW + k
            if i not in final_res:
                errs.append(f"{i}: 未判定（--final）")
                continue
            if cmp_[f"D{r}"].value is None:
                errs.append(f"{i}: 人間用途判定が空（--final）")
            # ★ 受け入れ条件 4: 1 回目（stage 1）と 2 回目（stage 2/2e）の両方を持つ
            if i not in seen1:
                errs.append(f"{i}: 1 回目（stage 1）の記録が無い（--final）")
            if i not in seen2:
                errs.append(f"{i}: 2 回目（stage 2）の記録が無い（--final）")
            res = final_res[i]
            if res["verdict"] == "含める" and kind[i] in PRIMARY and res.get("basis", "全文") == "全文" \
                    and scr[f"I{r}"].value != "完了":
                errs.append(f"{i}: 含めた一次研究（全文）の品質評価が完了でない（--final）")
    return errs


def selftest():
    import write_workbook as W
    bad = 0
    # 既知の答え（★ 期待は文字で書く。両方の対応表から行が消えても赤になる）
    known = [
        ({"verdict": "含める", "use": "中心-A"}, "直接研究", "中心候補"),
        ({"verdict": "含める", "use": "中心-B"}, "隣接研究", "中心候補"),
        ({"verdict": "除外", "ecode": "E2"}, "隣接研究", "背景保持"),
        ({"verdict": "除外", "ecode": "E4"}, "既存レビュー", "背景保持"),
        ({"verdict": "除外", "ecode": "E4"}, "尺度・理論", "背景保持"),
        ({"verdict": "除外", "ecode": "E4"}, "方法論", "方法論保持"),
        ({"verdict": "除外", "ecode": "E4"}, "訂正通知", "訂正連結"),
        ({"verdict": "除外", "ecode": "E1"}, "直接研究", "除外"),
        ({"verdict": "除外", "ecode": "E3"}, "直接研究", "除外"),
        ({"verdict": "除外", "ecode": "E5"}, "直接研究", "除外"),
        ({"verdict": "除外", "ecode": "E7"}, "直接研究", "除外"),
        ({"verdict": "除外", "ecode": "E6"}, "直接研究", "保留"),
        ({"verdict": "保留"}, "直接研究", "保留"),
        # ★ 2026-10-02（レビューの指摘）: 両方の表にあるのに既知の答えに無かった対応
        ({"verdict": "除外", "ecode": "E4"}, "直接研究", "背景保持"),
        ({"verdict": "除外", "ecode": "E4"}, "隣接研究", "背景保持"),
        ({"verdict": "除外", "ecode": "E2"}, "直接研究", "背景保持"),
    ]
    for res, kind, want in known:
        got_c = expect_human(res, kind)
        got_w = W.USE_TO_HUMAN[W.use_of(res, kind)]
        if got_c != want or got_w != want:
            print("FAIL 既知の答え", res, kind, want, got_c, got_w)
            bad += 1
    # 変異: 一時の写しとログで回す
    tmpd = tempfile.mkdtemp(prefix="chk34-")
    base_copy = os.path.join(tmpd, "copy.xlsx")
    base_log = os.path.join(tmpd, "log.jsonl")
    rec1 = {"item": "AF030", "stage": "1", "question": "AF030 の判定（事実のみ）",
            "options": STAGE1_OPTIONS["other"], "answer": STAGE1_OPTIONS["other"][1],
            "result": {"verdict": "除外", "ecode": "E4", "elabel": "方法論", "basis": "全文", "date": "2026-10-01"}}
    rec2 = dict(rec1, stage="2", question="AI の判定を見て", options=["1 回目のまま", "変える（Other に）"],
                answer="1 回目のまま")
    recx = {"item": "AF030", "stage": "x", "question": "抽出の確定", "options": ["確定"], "answer": "確定",
            "result": {"items": ["AF030"]}}
    with open(base_log, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in (rec1, rec2, recx))
    wb = openpyxl.load_workbook(C.ORIGINAL)
    r = C.FIRST_ROW + C.IDS.index("AF030")
    wb["スクリーニング"][f"D{r}"] = "除外"
    wb["スクリーニング"][f"G{r}"] = "E4 方法論"
    wb["スクリーニング"][f"H{r}"] = "完了"
    wb["スクリーニング"][f"I{r}"] = "対象外"
    wb["スクリーニング"][f"J{r}"] = "用途: 方法論保持 ／ 1回目: 除外 E4 → 最終: 除外 E4"
    wb.create_sheet(C.ADDED_PREFIX + "はじめに")
    wb.save(base_copy)
    e0 = check(base_copy, base_log)
    if e0:
        print("FAIL 基準の写しが緑にならない", e0[:3])
        bad += 1

    def mutate(name, fn_wb=None, fn_log=None):
        nonlocal bad
        cp, lg = os.path.join(tmpd, name + ".xlsx"), os.path.join(tmpd, name + ".jsonl")
        w2 = openpyxl.load_workbook(base_copy)
        if fn_wb:
            fn_wb(w2)
        w2.save(cp)
        recs = read_log(base_log)
        if fn_log:
            recs = fn_log(copy.deepcopy(recs))
        with open(lg, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in recs)
        es = check(cp, lg)
        if not es:
            print("FAIL 変異が緑のまま:", name)
            bad += 1
        else:
            print(f"  赤 {name}: {es[0]}")

    mutate("outside-cell", fn_wb=lambda w: w["研究情報"].cell(5, 5, "999"))
    mutate("judge2", fn_wb=lambda w: w["スクリーニング"].cell(r, 5, "含める"))
    mutate("log-copy-diff", fn_wb=lambda w: w["スクリーニング"].cell(r, 4, "保留"))
    mutate("ecode-diff", fn_wb=lambda w: w["スクリーニング"].cell(r, 7, "E2 疲労を測らない"))
    mutate("recommend-mark", fn_log=lambda L: [dict(x, options=[x["options"][0] + " (Recommended)"] + x["options"][1:])
                                               if x["stage"] == "1" else x for x in L])
    mutate("ai-in-stage1", fn_log=lambda L: [dict(x, question=x["question"] + " GPT 版は") if x["stage"] == "1" else x for x in L])
    mutate("ai-in-stage1-after-chatgpt", fn_log=lambda L: [dict(x, question=x["question"] + " ChatGPT の項目。GPT 版は")
                                                           if x["stage"] == "1" else x for x in L])
    # 陰性対照: 項目文の製品名 ChatGPT だけなら緑のまま
    lg_ok = os.path.join(tmpd, "chatgpt-only.jsonl")
    with open(lg_ok, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(dict(x, question=x["question"] + " 例 \"my use of ChatGPT\"") if x["stage"] == "1" else x,
                                ensure_ascii=False) + "\n" for x in read_log(base_log))
    if check(base_copy, lg_ok):
        print("FAIL 製品名 ChatGPT だけで赤になる")
        bad += 1
    mutate("recommend-after-guideline", fn_log=lambda L: [dict(x, question=x["question"] + " 一般に推奨。推奨は除外")
                                                          if x["stage"] == "1" else x for x in L])
    # 禁止語の規則（判断 12）: 除外は件と逐語の句の対だけに効く。区切りで境目を跨がない。1e にも効く。大文字小文字を区別しない
    o_other = STAGE1_OPTIONS["other"]
    unit = [
        ("AF032 の手引きの句だけ → 緑", stage1_banned("AF032", "・中身: 選別は 2 名が独立に行うのが一般に推奨・研究の質", o_other), False),
        ("同じ句でも別の件 → 赤", stage1_banned("AF030", "選別は 2 名が独立に行うのが一般に推奨", o_other), True),
        ("AF032 でも句の外の推奨 → 赤", stage1_banned("AF032", "選別は 2 名が独立に行うのが一般に推奨。推奨は除外", o_other), True),
        ("AF031 の句だけ → 緑", stage1_banned("AF031", "事前のプロトコル（公開・登録を勧める）・選別", o_other), False),
        ("問いの末尾と選択肢の先頭 → 赤", stage1_banned("AF030", "…一般に", ["推奨: 除外"] + o_other[1:]), True),
        ("小文字の recommended → 赤", stage1_banned("AF030", "this is recommended", o_other), True),
        ("ChatGPT 版 → 赤", stage1_banned("AF030", "ChatGPT 版の評価では", o_other), True),
        ("AI の評価 → 赤", stage1_banned("AF030", "AI の評価を見ると", o_other), True),
        ("項目文の ChatGPT だけ → 緑", stage1_banned("AF004", "例 \"my use of ChatGPT\"", o_other), False),
    ]
    for name, got, want_red in unit:
        if bool(got) != want_red:
            print("FAIL 禁止語の規則:", name)
            bad += 1
    mutate("ai-in-stage1e", fn_log=lambda L: L + [dict(L[0], stage="1e", question="除外のコード（GPT 版は E4）", options=["E1", "E2"])])
    # 『判定者1_確認の結果』: 実の data で作ったシートは緑（陰性対照）・1 か所ずらすと赤
    ch = json.load(open(os.path.join(C.TASK, "data", "checks-rows.json"), encoding="utf-8"))

    def add_checks(w2, edit=None):
        ws = w2.create_sheet(CHECKS_SHEET)
        for c, h in enumerate(ch["header"], 1):
            ws.cell(4, c, h)
        for rr, row in enumerate(ch["rows"], 5):
            for c, v in enumerate(row, 1):
                ws.cell(rr, c, v)
        if edit:
            edit(ws)
    w_ok = openpyxl.load_workbook(base_copy)
    add_checks(w_ok)
    cp_ok = os.path.join(tmpd, "checks-ok.xlsx")
    w_ok.save(cp_ok)
    if check(cp_ok, base_log):
        print("FAIL 実の確認の結果のシートで赤になる", check(cp_ok, base_log)[:3])
        bad += 1
    mutate("checks-result-vocab", fn_wb=lambda w: add_checks(w, lambda ws: ws.cell(10, 4, "済み")))
    mutate("checks-route-vocab", fn_wb=lambda w: add_checks(w, lambda ws: ws.cell(10, 7, "メインが確認")))
    # ★ ws.cell(r, c, None) は値を書き換えない（None は「指定なし」）。空にするのは .value に代入する
    mutate("checks-empty-location", fn_wb=lambda w: add_checks(w, lambda ws: setattr(ws.cell(20, 8), "value", None)))
    mutate("checks-row-missing", fn_wb=lambda w: add_checks(w, lambda ws: ws.delete_rows(30)))
    mutate("checks-id-order", fn_wb=lambda w: add_checks(w, lambda ws: ws.cell(5 + 12, 2, "AF002")))
    if not check(base_copy, base_log, final=True) or not any("確認の結果" in e for e in check(base_copy, base_log, final=True)):
        print("FAIL --final で確認の結果のシートが無いのに赤にならない")
        bad += 1
    mutate("checks-text-swap", fn_wb=lambda w: add_checks(w, lambda ws: ws.cell(5 + 12, 3, "別の文")))
    # 全文確認・品質評価をログ（x・q）から独立に計算する
    mutate("fulltext-not-logged", fn_log=lambda L: [x for x in L if x["stage"] != "x"])
    mutate("quality-done-without-q", fn_wb=lambda w: w["スクリーニング"].cell(r, 9, "完了"))
    mutate("quality-sheet-extra-id", fn_wb=lambda w: (lambda ws: (ws.cell(4, 1, "ID"), ws.cell(5, 1, "AF001")))(
        w.create_sheet(QUALITY_SHEET)))
    # 『判定者1_問いと答え』: ログと同じなら緑・1 か所ずらすと赤

    def add_log_sheet(w2, edit=None):
        ws = w2.create_sheet(LOG_SHEET)
        for c, h in enumerate(LOG_HEADER, 1):
            ws.cell(4, c, h)
        for rr, x in enumerate(read_log(base_log), 5):
            for c, v in enumerate([x.get("seq"), x["item"], x["stage"], x["question"], " ／ ".join(x["options"]), x["answer"], ""], 1):
                ws.cell(rr, c, v)
        if edit:
            edit(ws)
    w_ok2 = openpyxl.load_workbook(base_copy)
    add_log_sheet(w_ok2)
    cp_ok2 = os.path.join(tmpd, "logsheet-ok.xlsx")
    w_ok2.save(cp_ok2)
    if check(cp_ok2, base_log):
        print("FAIL ログと同じ問いと答えのシートで赤になる", check(cp_ok2, base_log)[:3])
        bad += 1
    mutate("logsheet-answer-diff", fn_wb=lambda w: add_log_sheet(w, lambda ws: ws.cell(5, 6, "保留")))
    # --final の受け入れ条件 4（1 回目と 2 回目の両方）と『はじめに』の注意: その件・その行の赤を名指しで見る（対照つき）

    def final_errs(fn_log=None, fn_wb=None):
        cp, lg = os.path.join(tmpd, "final.xlsx"), os.path.join(tmpd, "final.jsonl")
        w2 = openpyxl.load_workbook(base_copy)
        if fn_wb:
            fn_wb(w2)
        w2.save(cp)
        recs = read_log(base_log)
        if fn_log:
            recs = fn_log(copy.deepcopy(recs))
        with open(lg, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in recs)
        return check(cp, lg, final=True)
    msg2, msg1 = "AF030: 2 回目（stage 2）の記録が無い", "AF030: 1 回目（stage 1）の記録が無い"
    if any(msg2 in e or msg1 in e for e in final_errs()):
        print("FAIL 対照: 1 回目と 2 回目があるのに --final で無いと言う")
        bad += 1
    if not any(msg2 in e for e in final_errs(fn_log=lambda L: [x for x in L if x["stage"] != "2"])):
        print("FAIL 2 回目を消しても --final で赤にならない")
        bad += 1
    if not any(msg1 in e for e in final_errs(fn_log=lambda L: [dict(x, stage="1e") if x["stage"] == "1" else x for x in L])):
        print("FAIL 1 回目を 1e に差し替えても --final で赤にならない")
        bad += 1

    def intro_with(rows):
        def f(w2):
            ws = w2[INTRO_SHEET]
            for rr, v in enumerate(rows, 5):
                ws.cell(rr, 2, v)
        return f
    if any("「判定者 2 に渡さない」" in e for e in final_errs(fn_wb=intro_with(["この写しは判定者 2 に渡さない", "Claude の関与"]))):
        print("FAIL 対照: 『はじめに』に注意があるのに赤")
        bad += 1
    if not any("「判定者 2 に渡さない」" in e for e in final_errs(fn_wb=intro_with(["Claude の関与"]))):
        print("FAIL 『はじめに』に判定者 2 の注意が無いのに --final で赤にならない")
        bad += 1
    mutate("stage2-first", fn_log=lambda L: list(reversed(L)))
    mutate("extra-sheet", fn_wb=lambda w: w.create_sheet("メモ"))
    mutate("human-use-wrong", fn_wb=lambda w: w["AI判定比較"].cell(r, 4, "背景保持"))
    mutate("unlogged-verdict", fn_wb=lambda w: w["スクリーニング"].cell(C.FIRST_ROW, 4, "含める"))
    print("selftest", "PASS" if bad == 0 else f"FAIL {bad}")
    return bad == 0


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    errs = check(C.COPY_ARCHIVE, C.LOG, final="--final" in argv)
    if C.sha256(C.ORIGINAL) != C.ORIGINAL_SHA256 or C.sha256(C.ORIGINAL_DOWNLOADS) != C.ORIGINAL_SHA256:
        errs.append("元のファイルの SHA-256 が変わった")
    if C.sha256(C.COPY_ARCHIVE) != C.sha256(C.COPY_DOWNLOADS):
        errs.append("archive と Downloads の写しが違う")
    for e in errs:
        print("NG", e)
    print("違反", len(errs))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
