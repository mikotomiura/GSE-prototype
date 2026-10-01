"""ワークブックの写しと逐語のログの検査（design.md §6・requirement.md の受け入れ条件）。

(1) 元のシートのセル（数式は式のまま）が元のファイルと同じ（入力欄を除く）。シートの並びも同じで、足したシートは `判定者1_` で始まる。
(2) 入力欄の値が入力規則の語彙の中にある。判定者2・最終判定は 34 行とも `未判定`。
(3) ログの最終の答え → 本検査器が独自に持つ対応表 → 期待の値、を写しと突き合わせる（書き込み側の表を import しない）。
(4) ログの形: 1 回目（stage 1）の選択肢が種類ごとの固定の集合と完全に一致し、問いの文に AI の判定・推奨の語が無い。2 回目は 1 回目の後。
(5) --final: 34 件すべて判定済み・含めた一次研究で全文ありは品質評価が完了・『AI判定比較』の人間用途判定が 34 行とも入っている。
--selftest: 既知の答えの検算と、変異（入力欄の外のセル・判定者2・ログと写しのずれ・推奨の印・余分なシート）がそれぞれ赤になること。
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
# ★ 製品名の ChatGPT（項目文の逐語に出る・AF004）は GPT 版の判定ではないので除く（decisions.md 判断 4）
# ★ 手引きの中身「一般に推奨」（AF032 の Step 4 の要約）は AI の推奨ではないので除く（decisions.md 判断 9）
STAGE1_BANNED = re.compile(r"Recommended|(?<!一般に)推奨|AI の判定|AIの判定|(?<!Chat)GPT|Claude|中心候補")
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
    seen1, final_res = {}, {}
    for n, rec in enumerate(log, 1):
        i, st = rec.get("item"), rec.get("stage")
        if i not in kind:
            errs.append(f"ログ {n}: 知らない件 {i}")
            continue
        if st == "1":
            want = STAGE1_OPTIONS["primary" if kind[i] in PRIMARY else "other"]
            if rec.get("options") != want:
                errs.append(f"ログ {n} {i}: 1 回目の選択肢が固定の集合と違う: {rec.get('options')}")
            if STAGE1_BANNED.search(rec.get("question", "") + " ".join(rec.get("options") or [])):
                errs.append(f"ログ {n} {i}: 1 回目の問いに AI の判定・推奨の語がある")
            seen1[i] = True
        if st in ("1", "1e", "2", "2e"):
            if st in ("2", "2e") and i not in seen1:
                errs.append(f"ログ {n} {i}: 2 回目が 1 回目より前")
            final_res[i] = rec["result"]
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
        if not (scr[f"J{r}"].value or "").startswith("用途: "):
            errs.append(f"{i}: 自由記入が規則の形でない")
        hu = cmp_[f"D{r}"].value
        if hu is not None and hu != expect_human(res, kind[i]):
            errs.append(f"{i}: 人間用途判定 {hu!r} が期待 {expect_human(res, kind[i])!r} と違う")
    # (5)
    if final:
        for k, i in enumerate(C.IDS):
            r = C.FIRST_ROW + k
            if i not in final_res:
                errs.append(f"{i}: 未判定（--final）")
                continue
            if cmp_[f"D{r}"].value is None:
                errs.append(f"{i}: 人間用途判定が空（--final）")
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
    with open(base_log, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec1, ensure_ascii=False) + "\n" + json.dumps(rec2, ensure_ascii=False) + "\n")
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
    # 陰性対照: 手引きの中身の「一般に推奨」だけなら緑のまま
    lg_ok2 = os.path.join(tmpd, "guideline-only.jsonl")
    with open(lg_ok2, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(dict(x, question=x["question"] + " 選別は 2 名が独立に行うのが一般に推奨") if x["stage"] == "1" else x,
                                ensure_ascii=False) + "\n" for x in read_log(base_log))
    if check(base_copy, lg_ok2):
        print("FAIL 手引きの中身の「一般に推奨」だけで赤になる")
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
