"""追加候補の表と逐語のログの検査（design.md §9・requirement.md の受け入れ条件）。

(1) 元の資料（研究者の元のファイル・判定者用ファイル・評価版・34 件の写し）の SHA-256 が変わっていない。
(2) シートの並びと『スクリーニング』の見出し。行の ID・題名・DOI が判定者用ファイルの『追加候補』220 件と順に一致し、その後に X の行が
    data/extra-records.json と一致する。
(3) 全行: 暫定分類 = 追加候補（未分類）・判定者2/最終判定 = 未判定・語彙と入力規則。未判定の行は初期値のまま（除外理由・自由記入が空）。
(4) ログの最終の答え → 本検査器が独自に持つ対応表 → 期待の値を、表と突き合わせる（書き込み側の表を import しない）。
(5) 2 回目の有無: 評価版に行がある記録は 2 回目（2/2e）が 1 回目の後にある・無い記録は 2 回目が無い。1 回目の選択肢は種類ごとの
    固定の集合・1 回目（1・1e）に AI の判定・推奨の語が無い（前のタスクの関数）。
(6) 『AI判定比較』の行 = 判定済み ∩ 評価版の記録（順）・AI用途判定 = 評価版の値（独立に読む）・人間用途判定 = 期待。
(7) 『問いと答え』がログと 1 行ずつ一致・『探索の一覧』『探索の検索式』が data と一致・『はじめに』に研究者への注意がある。
(8) --final: 対象の記録（群 1〜3 と X の行）がすべて判定済み・含めた一次研究で全文ありは品質が確定・抽出の確定（x）がある。
(9) 答えの逐語と判定（result）が合う（前のタスクの answer_mismatch: 既知の形への全体一致）。式のセルは『AI判定比較』の
    一致の式（E 列）だけ。『全文抽出』の ID = 抽出を確定した件・中身は data/extract-rows.json と同じ。
    『はじめに』の「判定者 2 に渡すとき」が戻す列を名指しする（判断 10）。
--selftest: 自前のログで表を作り、陰性対照が緑・変異がそれぞれ赤になること。
使い方: python check_candidates.py [--final] [--selftest]
"""
import copy
import json
import os
import shutil
import sys
import tempfile

import openpyxl

import common as C
from check_workbook import STAGE1_OPTIONS, answer_mismatch, stage1_banned  # 前のタスク（34 件）の固定の選択肢・答えの読み方・禁止語の規則

SHEETS = ["はじめに", "スクリーニング", "AI判定比較", "全文抽出", "探索の検索式", "探索の一覧", "問いと答え"]
SCR_HEADER = ["ID", "論文タイトル", "暫定分類", "判定者1", "判定者2", "最終判定", "除外理由", "全文確認・抽出", "品質評価", "自由記入",
              "出どころ", "DOI", "年", "掲載誌", "本文の入手（OpenAlex）", "同じ研究の群", "内容の群（機械の分類・判定の材料ではない）"]
UNCLASSIFIED = "追加候補（未分類）"
VOCAB = {"D": {"未判定", "含める", "除外", "保留"}, "H": {"未完了", "進行中", "完了", "入手不可", "対象外"},
         "I": {"未実施", "進行中", "完了", "対象外"}}
VALIDATED = ("D", "E", "F", "H", "I")
# 答え → 用途（★ build_candidates.py とは別に持つ）
EXPECT_HUMAN = {("含める", "中心-A"): "中心候補", ("含める", "中心-B"): "中心候補", ("除外", "E1"): "除外", ("除外", "E2"): "背景保持",
                ("除外", "E3"): "除外", ("除外", "E5"): "除外", ("除外", "E7"): "除外", ("除外", "E6"): "保留"}
EXPECT_E4 = {"レビュー": "背景保持", "論考": "背景保持", "研究計画": "背景保持", "一次研究": "背景保持",
             "方法論": "方法論保持", "訂正通知": "訂正連結"}
# 本タスクで判定する記録（design.md §2 の群 1〜3）。X の行は data から足す
TARGET_IDS = ["S02-08", "S08-03", "S15-23", "S13-20", "S12-05", "S12-19", "S12-23"]
INTRO_MUST = ["判定者 2 に渡さない", "Claude の関与", "Claude 版", "GPT 版は無い",
              "『スクリーニング』の D・G・H・I・J 列を初期値", "『AI判定比較』『全文抽出』『品質評価』『問いと答え』のシートを消して"]


def read_log(path):
    if not os.path.exists(path):
        return []
    return [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]


def load_json(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def expect_human(res):
    v, e = res["verdict"], res.get("ecode")
    if v == "含める":
        return EXPECT_HUMAN[(v, res["use"])]
    if v == "保留":
        return "保留"
    if e == "E4":
        return EXPECT_E4[res["kind_detail"]]
    return EXPECT_HUMAN[(v, e)]


def lab(r):
    return {"含める": f"含める（{r.get('use')}）", "除外": f"除外 {r.get('ecode')}"}.get(r["verdict"], "保留")


def judge_rows():
    ws = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True)[C.JUDGE_SHEET]
    rows = list(ws.iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    a, t, d = h.index("候補番号"), h.index("題名（書誌の記録）"), h.index("DOI")
    return [(r[a], r[t], r[d]) for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]]


def appraisal_use():
    ws = openpyxl.load_workbook(C.APPRAISAL, read_only=True)["Claude適格性評価"]
    rows = list(ws.iter_rows(values_only=True))
    h = next(k for k, r in enumerate(rows[:8]) if r and r[0] == "候補番号")
    j = rows[h].index("用途判定（Claude）")
    return {r[0]: r[j] for r in rows[h + 1:] if r and r[0]}


def check_sources():
    errs = []
    for p, s in ((C.ORIGINAL, C.ORIGINAL_SHA256), (C.JUDGE_FILE, C.JUDGE_FILE_SHA256), (C.APPRAISAL, C.APPRAISAL_SHA256)):
        if C.sha256(p) != s:
            errs.append(f"元の資料の SHA-256 が違う: {p}")
    rec = open(C.COPY34_SHA_RECORD, encoding="utf-8").read().strip()
    for p in (C.COPY34_ARCHIVE, os.path.join(C.DOWNLOADS, os.path.basename(C.COPY34_ARCHIVE))):
        if C.sha256(p) != rec:
            errs.append(f"34 件の写しが前のタスクの記録と違う: {p}")
    return errs


def check(path, log_path, final=False, extra_path=None, runs_path=None, recs_path=None, extract_path=None):
    errs = []
    log = read_log(log_path)
    extra = load_json(extra_path or C.EXTRA_RECORDS, [])
    w = openpyxl.load_workbook(path)
    names = [n for n in w.sheetnames if n != "品質評価"]
    if names != SHEETS:
        errs.append(f"シートの並びが違う: {w.sheetnames}")
        return errs
    ws = w["スクリーニング"]
    if [ws.cell(4, c).value for c in range(1, len(SCR_HEADER) + 1)] != SCR_HEADER:
        errs.append("『スクリーニング』の見出しが違う")
    expect_rows = judge_rows() + [(x["id"], x["title"], x.get("doi")) for x in extra]
    if len(expect_rows) != C.N_CANDIDATES + len(extra):
        errs.append(f"判定者用ファイルの件数が違う: {len(expect_rows)}")
    last = 4
    while ws.cell(last + 1, 1).value is not None:
        last += 1
    n = last - 4
    if n != len(expect_rows):
        errs.append(f"行の数が違う: {n}（期待 {len(expect_rows)}）")
    for k, (i, t, d) in enumerate(expect_rows):
        r = 5 + k
        got = (ws.cell(r, 1).value, ws.cell(r, 2).value, ws.cell(r, 12).value)
        if got != (i, t, d):
            errs.append(f"行 {r}: ID・題名・DOI が元と違う: {got[0]}（期待 {i}）")
            break
    # 入力規則（D/E/F/H/I が全行に掛かっている）
    covered = {}
    for dv in ws.data_validations.dataValidation:
        for rng in str(dv.sqref).split():
            col = "".join(ch for ch in rng.split(":")[0] if ch.isalpha())
            covered[col] = rng
    for col in VALIDATED:
        if covered.get(col) != f"{col}5:{col}{4 + len(expect_rows)}":
            errs.append(f"入力規則が無い・範囲が違う: {col}（{covered.get(col)}）")
    # ログから最終と段
    first, final_res, stages, quality, xconf = {}, {}, {}, {}, set()
    first_ans, prev_res = {}, {}
    for rec in log:
        i, st = rec["item"], rec["stage"]
        stages.setdefault(i, []).append(st)
        if st in ("1", "1e", "2", "2e"):  # (9) 答えの逐語と判定（result）
            why = answer_mismatch(st, rec["answer"], rec["result"], first.get(i), prev_res.get(i), first_ans.get(i))
            if why:
                errs.append(f"{i}: 答えと判定が合わない（{why}）")
            if st == "1":
                first_ans[i] = rec["answer"]
            prev_res[i] = rec["result"]
        if st in ("1", "1e"):
            first[i] = rec["result"]
            if st == "1":
                kind = rec["result"].get("kind")
                want = STAGE1_OPTIONS["primary" if kind in ("一次研究", "不明") else "other"]
                if rec["options"] != want:
                    errs.append(f"{i}: 1 回目の選択肢が固定の集合と違う")
            m = stage1_banned(i, rec["question"], rec["options"])
            if m:
                errs.append(f"{i}: 1 回目に AI の判定・推奨を示す語: {m.group(0)}")
        elif st in ("2", "2e"):
            if i not in first:
                errs.append(f"{i}: 2 回目が 1 回目より前")
            final_res[i] = rec["result"]
        elif st == "q":
            quality[i] = rec["result"]
        elif st == "x":
            xconf.update(rec["result"]["items"])
    for i in first:
        final_res.setdefault(i, first[i])
    ai = appraisal_use()
    ids = [e[0] for e in expect_rows]
    for i in final_res:
        if i not in ids:
            errs.append(f"ログに表に無い ID: {i}")
        has2 = any(s in ("2", "2e") for s in stages.get(i, []))
        if i in ai and not has2:
            errs.append(f"{i}: 評価版に行があるのに 2 回目が無い")
        if i not in ai and has2:
            errs.append(f"{i}: 評価版に行が無いのに 2 回目がある（AI の判定を作っていない）")
    for k, i in enumerate(ids):
        r = 5 + k
        c = {col: ws[f"{col}{r}"].value for col in "CDEFGHIJ"}
        if c["C"] != UNCLASSIFIED:
            errs.append(f"{i}: 暫定分類が {c['C']}")
        if c["E"] != "未判定" or c["F"] != "未判定":
            errs.append(f"{i}: 判定者2・最終判定が未判定でない")
        for col, voc in VOCAB.items():
            if c[col] not in voc:
                errs.append(f"{i}: {col} の値が語彙の外: {c[col]}")
        if i not in final_res:
            if (c["D"], c["G"], c["H"], c["I"], c["J"]) != ("未判定", None, "未完了", "未実施", None):
                errs.append(f"{i}: 未判定の行が初期値でない")
            continue
        f1, f0 = final_res[i], first[i]
        basis = f1.get("basis", "全文")
        exp_h = "入手不可" if basis in ("抄録", "なし") else ("完了" if i in xconf else "進行中")
        if f1["verdict"] == "含める" and f1.get("kind_detail") == "一次研究":
            q = quality.get(i)
            exp_i = "進行中" if basis in ("抄録", "なし") else ("未実施" if q is None else ("進行中" if str(q.get("answer", "")).startswith("保留") else "完了"))
        else:
            exp_i = "未実施" if f1["verdict"] == "保留" else "対象外"
        if c["D"] != f1["verdict"]:
            errs.append(f"{i}: 判定者1 がログと違う（{c['D']} / {f1['verdict']}）")
        if f1["verdict"] == "除外" and not str(c["G"] or "").startswith(f1["ecode"]):
            errs.append(f"{i}: 除外理由のコードがログと違う")
        if f1["verdict"] != "除外" and c["G"]:
            errs.append(f"{i}: 除外でないのに除外理由がある")
        if c["H"] != exp_h:
            errs.append(f"{i}: 全文確認が期待と違う（{c['H']} / {exp_h}）")
        if c["I"] != exp_i:
            errs.append(f"{i}: 品質評価が期待と違う（{c['I']} / {exp_i}）")
        j = str(c["J"] or "")
        if f"1回目: {lab(f0)} → 最終: {lab(f1)}" not in j:
            errs.append(f"{i}: 自由記入の 1 回目と最終がログと違う")
        if ("AI の判定: Claude 版" in j) != (i in ai) or ("AI の判定: なし" in j) == (i in ai):
            errs.append(f"{i}: 自由記入の AI の判定の有無が違う")
        if final and f1["verdict"] == "含める" and f1.get("kind_detail") == "一次研究" and basis == "全文" and i not in quality:
            errs.append(f"{i}: 含めた一次研究（全文あり）で品質が確定していない")
    # 『AI判定比較』
    wc = w["AI判定比較"]
    want = [i for i in ids if i in final_res and i in ai]
    got = []
    r = 5
    while wc.cell(r, 1).value is not None:
        got.append(wc.cell(r, 1).value)
        i = wc.cell(r, 1).value
        if i in final_res and i in ai:
            if wc.cell(r, 3).value != ai[i]:
                errs.append(f"AI判定比較 {i}: AI用途判定が評価版と違う")
            if wc.cell(r, 4).value != expect_human(final_res[i]):
                errs.append(f"AI判定比較 {i}: 人間用途判定が期待と違う")
            if wc.cell(r, 5).value != f'=IF(D{r}="","",IF(C{r}=D{r},"一致","要照合"))':
                errs.append(f"AI判定比較 {i}: 一致の式が違う")
        r += 1
    if got != want:
        errs.append(f"AI判定比較の行が 判定済み ∩ 評価版 と違う: {got} / {want}")
    # (9) 式のセル: 『AI判定比較』の一致の式（E 列）のほかに無い（外の文の先頭の = が式になるのを防ぐ）
    for ws_ in w.worksheets:
        for row in ws_.iter_rows():
            for c in row:
                if c.data_type == "f" and not (ws_.title == "AI判定比較" and c.column_letter == "E" and c.row >= 5):
                    errs.append(f"式のセル: {ws_.title}!{c.coordinate}")
    # (9) 『全文抽出』: ID = 抽出を確定した件（重複なし）・中身は data と同じ
    we = w["全文抽出"]
    ex = load_json(extract_path or C.EXTRACT_ROWS, None)
    ex_rows = [[we.cell(r, c).value for c in range(1, we.max_column + 1)] for r in range(5, we.max_row + 1)]
    ex_rows = [x for x in ex_rows if any(v not in (None, "") for v in x)]
    ex_ids = [x[0] for x in ex_rows]
    if len(ex_ids) != len(set(ex_ids)) or set(ex_ids) != xconf:
        errs.append(f"全文抽出: ID が抽出を確定した件と違う（多い {sorted(set(ex_ids) - xconf)}・無い {sorted(xconf - set(ex_ids))}・重複を含む）")
    if ex is None:
        errs.append("全文抽出: 中身を比べる data が無い")
    else:
        def norm(row, n=we.max_column):
            return [None if v in (None, "") else v for v in row] + [None] * (n - len(row))
        if norm(ex["header"]) != norm([we.cell(4, c).value for c in range(1, we.max_column + 1)]) or \
                [norm(x) for x in ex["rows"]] != [norm(x) for x in ex_rows]:
            errs.append("全文抽出: 中身が data/extract-rows.json と違う")
    # 『問いと答え』
    wl = w["問いと答え"]
    for k, rec in enumerate(log):
        rr = 5 + k
        row = [wl.cell(rr, c).value for c in range(1, 8)]
        exp = [rec.get("seq"), rec["item"], rec["stage"], rec["question"], " ／ ".join(rec.get("options") or []), rec["answer"], rec.get("note", "") or None]
        if row[:6] != exp[:6] or (row[6] or None) != exp[6]:
            errs.append(f"問いと答え: {rr} 行目がログと違う")
            break
    if wl.cell(5 + len(log), 1).value is not None:
        errs.append("問いと答え: ログより行が多い")
    # 探索
    runs = load_json(runs_path or C.SEARCH_RUNS, [])
    recs = load_json(recs_path or C.SEARCH_RECORDS, [])
    wr, wq = w["探索の検索式"], w["探索の一覧"]
    if [wr.cell(5 + k, 2).value for k in range(len(runs))] != [x["query"] for x in runs] or wr.cell(5 + len(runs), 1).value is not None:
        errs.append("探索の検索式が data と違う")
    if [wq.cell(5 + k, 1).value for k in range(len(recs))] != [x["key"] for x in recs] or wq.cell(5 + len(recs), 1).value is not None:
        errs.append("探索の一覧が data と違う")
    elif [(wq.cell(5 + k, 10).value, wq.cell(5 + k, 11).value) for k in range(len(recs))] != [(x.get("layer"), x.get("reading")) for x in recs]:
        errs.append("探索の一覧の層・読む一覧が data と違う")
    for x in recs:
        if x.get("added_as") and x["added_as"] not in ids:
            errs.append(f"探索で足したとする {x['added_as']} が表の行に無い")
    # 『はじめに』
    wi = w["はじめに"]
    text = "\n".join(str(wi.cell(r, c).value or "") for r in range(1, wi.max_row + 1) for c in (1, 2))
    for s in INTRO_MUST:
        if s not in text:
            errs.append(f"はじめに: 「{s}」が無い")
    if final:
        targets = TARGET_IDS + [x["id"] for x in extra]
        miss = [i for i in targets if i not in final_res]
        if miss:
            errs.append(f"--final: 判定していない対象: {miss}")
        for i in targets:
            if i in final_res and final_res[i].get("basis", "全文") == "全文" and i not in xconf:
                errs.append(f"--final: {i} は全文ありで抽出が確定していない")
    return errs


def selftest():
    import build_candidates as B
    ok = True
    tmpd = tempfile.mkdtemp(prefix="candchk-")
    base_log = [
        {"seq": 1, "item": "S15-23", "stage": "1", "question": "S15-23 の事実と基準", "options": STAGE1_OPTIONS["other"],
         "answer": "除外 E4（保持の区分は対応表で決まる）", "note": "",
         "result": {"verdict": "除外", "ecode": "E4", "elabel": "レビュー（背景保持）", "kind": "一次研究でない", "kind_detail": "レビュー", "basis": "全文", "date": "2026-10-02"}},
        {"seq": 2, "item": "S15-23", "stage": "2", "question": "AI の判定を見て", "options": ["1 回目のまま", "変える"], "answer": "1 回目のまま", "note": "",
         "result": {"verdict": "除外", "ecode": "E4", "elabel": "レビュー（背景保持）", "kind": "一次研究でない", "kind_detail": "レビュー", "basis": "全文", "date": "2026-10-02",
                    "reason_summary": "叙述的レビュー"}},
        {"seq": 3, "item": "X01", "stage": "1", "question": "X01 の事実と基準", "options": STAGE1_OPTIONS["other"], "answer": "除外 E4（保持の区分は対応表で決まる）", "note": "",
         "result": {"verdict": "除外", "ecode": "E4", "elabel": "論考（背景保持）", "kind": "一次研究でない", "kind_detail": "論考", "basis": "全文", "date": "2026-10-02"}},
        {"seq": 4, "item": "S15-23", "stage": "x", "question": "抽出の確定", "options": ["確定"], "answer": "確定", "note": "", "result": {"items": ["S15-23", "X01"]}},
    ]

    def build_with(log, mutate_wb=None):
        lp = os.path.join(tmpd, "log.jsonl")
        with open(lp, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in log)
        old = C.LOG
        C.LOG = lp
        try:
            xp = os.path.join(tmpd, "t.xlsx")
            B.build(xp)
        finally:
            C.LOG = old
        if mutate_wb:
            wb = openpyxl.load_workbook(xp)
            mutate_wb(wb)
            wb.save(xp)
        return xp, lp

    def expect(name, log, mutate_wb=None, must=None, red=True):
        nonlocal ok
        xp, lp = build_with(log, mutate_wb)
        errs = check(xp, lp)
        hit = bool(errs) if must is None else any(must in e for e in errs)
        good = hit if red else not errs
        print(("PASS" if good else "FAIL"), name, "" if good else errs[:3])
        ok &= good

    # ★ 自前のログの x（S15-23・X01）に合わせた全文抽出の data（実の data から 2 行だけ）
    exd = json.load(open(C.EXTRACT_ROWS, encoding="utf-8"))
    ex_small = {"header": exd["header"], "rows": [r for r in exd["rows"] if r[0] in ("S15-23", "X01")]}
    ex_path = os.path.join(tmpd, "extract.json")
    with open(ex_path, "w", encoding="utf-8") as f:
        json.dump(ex_small, f, ensure_ascii=False)
    old_ex = C.EXTRACT_ROWS
    C.EXTRACT_ROWS = ex_path
    expect("negative-control（自前のログ）", base_log, red=False)

    def logm(fn):
        lg = copy.deepcopy(base_log)
        fn(lg)
        return lg
    expect("stage2-removed（評価版に行があるのに 2 回目なし）", logm(lambda lg: lg.pop(1)), must="2 回目が無い")
    expect("stage2-added-for-X01（AI の判定を作った）",
           logm(lambda lg: lg.append({**copy.deepcopy(lg[1]), "seq": 5, "item": "X01"})), must="評価版に行が無いのに")
    expect("banned-word（1 回目に推奨）", logm(lambda lg: lg[0].__setitem__("question", "S15-23 の事実（推奨: 除外）")), must="AI の判定・推奨")
    expect("options-changed（1 回目の選択肢）", logm(lambda lg: lg[0].__setitem__("options", STAGE1_OPTIONS["primary"])), must="固定の集合")

    def cell(sheet, ref, val):
        return lambda wb: wb[sheet].__setitem__(ref, val)
    expect("judge2-filled", base_log, cell("スクリーニング", "E7", "含める"), must="判定者2")
    expect("unclassified-changed", base_log, cell("スクリーニング", "C9", "既存レビュー"), must="暫定分類")
    expect("unjudged-free-text", base_log, cell("スクリーニング", "J6", "メモ"), must="初期値でない")
    expect("title-changed", base_log, cell("スクリーニング", "B5", "別の題名"), must="ID・題名・DOI")

    def row_of(wb, i):
        ws = wb["スクリーニング"]
        return next(r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == i)
    expect("log-vs-sheet（判定者1 をずらす）", base_log, lambda wb: wb["スクリーニング"].__setitem__(f"D{row_of(wb, 'X01')}", "保留"), must="判定者1 がログと違う")
    expect("H-changed", base_log, lambda wb: wb["スクリーニング"].__setitem__(f"H{row_of(wb, 'S15-23')}", "進行中"), must="全文確認")
    expect("delete-row", base_log, lambda wb: wb["スクリーニング"].delete_rows(10), must="ID・題名・DOI")
    expect("validation-removed", base_log, lambda wb: wb["スクリーニング"].data_validations.dataValidation.pop(0), must="入力規則")
    expect("cmp-row-for-unjudged", base_log,
           lambda wb: [wb["AI判定比較"].__setitem__(k, v) for k, v in (("A6", "S02-08"), ("C6", "中心候補"))], must="AI判定比較の行")
    expect("cmp-ai-value-changed", base_log, cell("AI判定比較", "C5", "中心候補"), must="AI用途判定")
    expect("logsheet-diff", base_log, cell("問いと答え", "F5", "別の答え"), must="問いと答え")
    expect("search-layer-changed", base_log, cell("探索の一覧", "J5", "Z"), must="層・読む一覧")
    expect("search-row-removed", base_log, lambda wb: wb["探索の一覧"].delete_rows(6), must="探索の一覧が data と違う")
    expect("intro-warning-removed", base_log,
           lambda wb: [wb["はじめに"].cell(r, 2).__setattr__("value", "") for r in range(5, 30) if "判定者 2 に渡さない" in str(wb["はじめに"].cell(r, 2).value or "")],
           must="判定者 2 に渡さない")
    # (9) 答えと判定・式・全文抽出・『はじめに』の列の名指し（判断 10）
    expect("answer-only-diff（答えだけをずらす）", logm(lambda lg: lg[0].__setitem__("answer", "保留")), must="答えと判定が合わない")
    expect("result-only-diff（判定だけをずらす）",
           logm(lambda lg: lg[1].__setitem__("result", {**lg[1]["result"], "ecode": "E2"})), must="答えと判定が合わない")
    expect("answer-unreadable（Other の自由記入）", logm(lambda lg: lg[1].__setitem__("answer", "別の判定に変える")), must="読めない")
    expect("formula-in-title", base_log, cell("探索の一覧", "B5", "=1+1"), must="式のセル: 探索の一覧!B5")
    expect("formula-cmp-E-is-allowed（対照）", base_log, red=False)
    expect("extract-row-removed", base_log, lambda wb: wb["全文抽出"].delete_rows(5), must="全文抽出: ID")
    expect("extract-cell-changed", base_log, cell("全文抽出", "C5", "別の集団"), must="全文抽出: 中身")
    expect("intro-columns-removed", base_log,
           lambda wb: [wb["はじめに"].cell(r, 2).__setattr__("value", "このファイルは判定者 2 に渡さない。") for r in range(5, 30)
                       if "判定者 2 に渡さない" in str(wb["はじめに"].cell(r, 2).value or "")],
           must="D・G・H・I・J 列を初期値")
    xp_put, _ = build_with(base_log)
    wbp = openpyxl.load_workbook(xp_put)
    B.put(wbp["探索の一覧"]["B5"], "=1+1")
    wbp.save(xp_put)
    wbr = openpyxl.load_workbook(xp_put)
    good = wbr["探索の一覧"]["B5"].value == "=1+1" and wbr["探索の一覧"]["B5"].data_type == "s"
    print(("PASS" if good else "FAIL"), "put-keeps-string（書き込み側の put で書いた = は文字列のまま）")
    ok &= good
    C.EXTRACT_ROWS = old_ex
    # --final: 対象が判定されていなければ赤（対照: 自前のログは未判定の対象を残すので必ず赤）
    xp, lp = build_with(base_log)
    errs = check(xp, lp, final=True)
    good = any("判定していない対象" in e for e in errs)
    print(("PASS" if good else "FAIL"), "final-requires-targets")
    ok &= good
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    errs = check_sources() + check(C.CAND_ARCHIVE, C.LOG, final="--final" in argv)
    if os.path.exists(C.CAND_SHA_RECORD):
        rec = open(C.CAND_SHA_RECORD, encoding="utf-8").read().strip()
        for p in (C.CAND_ARCHIVE, C.CAND_DOWNLOADS):
            if C.sha256(p) != rec:
                errs.append(f"表の SHA-256 が記録と違う: {p}")
    else:
        errs.append("表の SHA-256 の記録が無い")
    for e in errs:
        print("NG", e)
    print("違反", len(errs))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
