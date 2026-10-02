"""追加候補の表（v2）の検査（design.md §9 を判断 3〜6 に合わせて縮めた形・引き継ぎ §2 の 3）。

★ 期待は書き込み側（build_candidates.py）と独立に組む: 判定者用ファイル・評価版は見出しの名前で、前のタスクのログ・本タスクのログは
  自分で読み、答え → 表の値の対応は本検査器が別に持つ（import しない）。
★ 規則は RULES_* に 1 行 1 つ（meta_mutate.py が 1 行ずつ外す）。違反の文は規則の名前で始める（selftest が名前で当てる）。
★ 判断 5: AI の予備判定を判定者 1 の欄（D・G・J）に書かない・判定者 1 の行に AI の列（T〜V）を書かない。
★ 判断 6: 判定者 1 の「除外 E4 背景」は E4（一次研究でない）と書かず、意図（範囲の外・背景として残す）を書く。
使い方: check_candidates.py [--final] | --selftest
"""
import copy
import datetime
import json
import os
import re
import shutil
import sys
import tempfile

import openpyxl

import common as C

SHEETS = ["はじめに", "スクリーニング", "AI判定比較", "一致の表", "群ごとの一覧", "全文抽出", "探索の検索式", "探索の一覧", "問いと答え"]
SCR_HEADER = ["ID", "論文タイトル", "暫定分類", "判定者1", "判定者2", "最終判定", "除外理由", "全文確認・抽出", "品質評価", "自由記入",
              "出どころ", "DOI", "年", "掲載誌", "本文の入手（OpenAlex）", "同じ研究の群", "内容の群（機械の分類・判定の材料ではない）",
              "判定者", "判定の段", "AI の予備判定（題名・抄録段・評価版）", "AI の除外理由（評価版の逐語）", "AI の値の出どころ",
              "研究者の読みに依存（Q1／Q2）"]
NCOL = len(SCR_HEADER)
UNCLASSIFIED = "追加候補（未分類）"
VOCAB = {"D": {"未判定", "含める", "除外", "保留"}, "H": {"未完了", "進行中", "完了", "入手不可", "対象外"},
         "I": {"未実施", "進行中", "完了", "対象外"}}
DV_VOCAB = {"D": '"未判定,含める,除外,保留"', "E": '"未判定,含める,除外,保留"', "F": '"未判定,含める,除外,保留"',
            "H": '"未完了,進行中,完了,入手不可,対象外"', "I": '"未実施,進行中,完了,対象外"'}
CMP_DV_VOCAB = '"中心候補,背景保持,方法論保持,訂正連結,除外,保留"'
# 前のタスクの答え → 用途（★ build_candidates.py とは別に持つ）
EXPECT_HUMAN = {("含める", "中心-A"): "中心候補", ("含める", "中心-B"): "中心候補", ("除外", "E1"): "除外", ("除外", "E2"): "背景保持",
                ("除外", "E3"): "除外", ("除外", "E5"): "除外", ("除外", "E7"): "除外", ("除外", "E6"): "保留"}
EXPECT_E4 = {"レビュー": "背景保持", "論考": "背景保持", "研究計画": "背景保持", "一次研究": "背景保持",
             "方法論": "方法論保持", "訂正通知": "訂正連結"}
# 判定者 1 の題名・抄録段の判定 → 用途の書き出し（★ 別に持つ）
JUDGE1_USE = {"含める": "用途: 未定", "保留": "用途: 保留", "除外": "用途: 背景保持"}
N_PREV, N_J1, N_AI = 8, 71, 142
FULL_TRANSLATION = 8
INTRO_MUST = ["判定者 2 に渡さない", "Claude の関与", "Claude 版", "GPT 版は無い",
              "『スクリーニング』の D・G・H・I・J 列を初期値", "R〜W 列", "『探索の一覧』の「足した（ID）」列を空に",
              "『AI判定比較』『一致の表』『群ごとの一覧』『全文抽出』『品質評価』『問いと答え』のシートを消し",
              "『はじめに』を判定者 2 用に書き直し", "人の判定ではない", "範囲の外・背景として残す", "43 件"]
RUN_HEADER = ["API", "検索式（逐語）", "実行日時", "総数", "取得", "条件を通った", "打ち切り", "エラー"]
LIST_HEADER = ["key", "題名", "年", "種別（API）", "掲載", "言語", "無料の版", "重なり", "見つかった API", "層", "読む一覧", "足した（ID）"]
AGREE_HEADER = ["順", "ID", "論文タイトル", "判定者 1（題名・抄録段）", "判定者 1 の除外理由", "AI の予備判定（題名・抄録段・評価版）",
                "AI の除外理由（評価版の逐語）", "判定の一致", "除外理由の一致"]
GROUP_HEADER = ["対象者", "内容の群（機械の分類・判定の材料ではない）", "件数", "判定者 1：計", "判定者 1：含める", "判定者 1：保留",
                "判定者 1：除外", "AI の予備判定：計", "AI：含める", "AI：保留", "AI：除外"]
LOG_HEADER = ["作業", "seq", "ID", "段", "問い（逐語）", "選択肢", "答え", "補足（note）"]


def read_log(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()] if os.path.exists(p) else []


def load_json(p, default):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def nz(v):
    return None if blank(v) else v


def sources(log_path=None):
    s = {}
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    ix = {k: h.index(k) for k in ("候補番号", "題名（書誌の記録）", "DOI")}
    ic = next(k for k, c in enumerate(h) if c and str(c).startswith("内容の群"))
    s["judge"] = [(r[ix["候補番号"]], r[ix["題名（書誌の記録）"]], r[ix["DOI"]], r[ic]) for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]]
    s["extra"] = load_json(C.PREV_EXTRA_RECORDS, [])
    # 前のタスクのログ（全文段）
    s["prev_log"] = read_log(C.PREV_LOG)
    first, final, quality, xconf, has2 = {}, {}, {}, set(), set()
    for r in s["prev_log"]:
        i, st = r["item"], r["stage"]
        if st in ("1", "1e"):
            first[i] = r["result"]
        elif st in ("2", "2e"):
            final[i] = r["result"]
            has2.add(i)
        elif st == "q":
            quality[i] = r["result"]
        elif st == "x":
            xconf.update(r["result"]["items"])
    s["prev"] = {"first": first, "final": {i: final.get(i, first[i]) for i in first}, "quality": quality, "xconf": xconf, "has2": has2}
    # 本タスクのログ
    s["log"] = read_log(log_path or C.LOG)
    j1, ai = {}, {}
    for r in s["log"]:
        if r["stage"] in ("ta1", "ta1e"):
            j1[r["item"]] = {"res": r["result"], "order": r["order"], "at": r["answered_at"]}
        elif r["stage"] == "ai_ta":
            ai[r["item"]] = {"res": r["result"], "order": r["order"]}
    s["j1"], s["ai_items"] = j1, ai
    # 評価版（見出しの名前で）
    aw = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)

    def table(name):
        rr = list(aw[name].iter_rows(values_only=True))
        k = next(k for k, r in enumerate(rr) if r and r[0] == "候補番号")
        return rr, k, list(rr[k])
    rr, k, hh = table("Claude適格性評価")
    s["ai_use"] = {r[0]: r[hh.index("用途判定（Claude）")] for r in rr[k + 1:] if r and r[0]}
    rr, k, hh = table("Claudeスクリーニング案")
    s["ai_ta"] = {r[0]: (r[hh.index("Claude予備判定（題名・抄録段）")], r[hh.index("除外理由")], n + 1)
                  for n, r in enumerate(rr) if n > k and r and r[0]}
    s["runs"] = load_json(C.SEARCH_RUNS, [])
    s["recs"] = load_json(C.SEARCH_RECORDS, [])
    s["extract"] = load_json(C.PREV_EXTRACT_ROWS, None)
    s["sha"] = {"orig": C.ORIGINAL_SHA256, "judge": C.JUDGE_FILE_SHA256, "appraisal": C.APPRAISAL_SHA256}
    return s


def body(ws, n, start=5):
    """start 行目から、A 列が埋まっている行を n 列ずつ（空の行で止まる）。"""
    out, r = [], start
    while ws.cell(r, 1).value is not None:
        out.append((r, [ws.cell(r, c).value for c in range(1, n + 1)]))
        r += 1
    return out


def scr(ctx):
    return {x[0]: (r, x) for r, x in body(ctx["wb"]["スクリーニング"], NCOL)}


def jst(ts):
    t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return t.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()


def prev_label(r):
    return {"含める": f"含める（{r.get('use')}）", "除外": f"除外 {r.get('ecode')}"}.get(r["verdict"], "保留")


def prev_use(res):
    v, e = res["verdict"], res.get("ecode")
    if v == "含める":
        return EXPECT_HUMAN[(v, res["use"])]
    if v == "保留":
        return "保留"
    if e == "E4":
        return EXPECT_E4[res["kind_detail"]]
    return EXPECT_HUMAN[(v, e)]


def is_e4bg(res):
    return str(res.get("ecode") or "").startswith("E4 背景")


# ---------------------------------------------------------------- 規則
def r_sources(ctx):
    v = []
    for p, k in ((C.ORIGINAL, "orig"), (C.JUDGE_FILE, "judge"), (C.APPRAISAL, "appraisal")):
        if C.sha256(p) != ctx["src"]["sha"][k]:
            v.append(f"r_sources: 元の資料の SHA-256 が違う: {os.path.basename(p)}")
    rec = open(C.COPY34_SHA_RECORD, encoding="utf-8").read().strip()
    for p in (C.COPY34_ARCHIVE, os.path.join(C.DOWNLOADS, os.path.basename(C.COPY34_ARCHIVE))):
        if C.sha256(p) != rec:
            v.append(f"r_sources: 34 件の写しが前のタスクの記録と違う: {os.path.basename(p)}")
    return v


def r_sheets(ctx):
    return [] if ctx["wb"].sheetnames == SHEETS else [f"r_sheets: シートの並びが違う: {ctx['wb'].sheetnames}"]


def r_rows(ctx):
    ws, v = ctx["wb"]["スクリーニング"], []
    if [ws.cell(4, c).value for c in range(1, NCOL + 1)] != SCR_HEADER or ws.cell(4, NCOL + 1).value is not None:
        v.append("r_rows: 『スクリーニング』の見出しが違う")
    want = [(i, t, d) for i, t, d, _ in ctx["src"]["judge"]] + [(x["id"], x["title"], x.get("doi")) for x in ctx["src"]["extra"]]
    got = [(x[0], x[1], x[11]) for _, x in body(ws, NCOL)]
    if len(ctx["src"]["judge"]) != C.N_CANDIDATES:
        v.append(f"r_rows: 判定者用ファイルの件数が {len(ctx['src']['judge'])}")
    if got != want:
        k = next((k for k, (a, b) in enumerate(zip(got, want)) if a != b), min(len(got), len(want)))
        v.append(f"r_rows: 行の ID・題名・DOI が元と違う（{k + 5} 行目付近・行数 {len(got)} / {len(want)}）")
    return v


def r_static(ctx):
    v = []
    for i, (r, x) in scr(ctx).items():
        if x[2] != UNCLASSIFIED:
            v.append(f"r_static: {i}: 暫定分類が {x[2]}")
        if x[4] != "未判定" or x[5] != "未判定":
            v.append(f"r_static: {i}: 判定者2・最終判定が未判定でない")
        for col, k in (("D", 3), ("H", 7), ("I", 8)):
            if x[k] not in VOCAB[col]:
                v.append(f"r_static: {i}: {col} の値が語彙の外: {x[k]}")
    return v[:10]


def r_validation(ctx):
    ws, v = ctx["wb"]["スクリーニング"], []
    n = len(body(ws, 1))
    covered = {}
    for dv in ws.data_validations.dataValidation:
        for rng in str(dv.sqref).split():
            covered["".join(ch for ch in rng.split(":")[0] if ch.isalpha())] = (rng, dv.formula1, dv.type)
    for col in DV_VOCAB:
        if covered.get(col) != (f"{col}5:{col}{4 + n}", DV_VOCAB[col], "list"):
            v.append(f"r_validation: 入力規則が無い・範囲・語彙・種類が違う: {col}（{covered.get(col)}）")
    if set(covered) - set(DV_VOCAB):
        v.append(f"r_validation: 余分な入力規則: {sorted(set(covered) - set(DV_VOCAB))}")
    wc = ctx["wb"]["AI判定比較"]
    n_cmp = len(body(wc, 1))
    cdv = [(str(dv.sqref), dv.formula1) for dv in wc.data_validations.dataValidation]
    if cdv != [("D5" if n_cmp <= 1 else f"D5:D{4 + n_cmp}", CMP_DV_VOCAB)]:
        v.append(f"r_validation: AI判定比較の入力規則が違う: {cdv}")
    return v


def r_prev_rows(ctx):
    """前の作業で全文段まで判定した 8 件（前のタスクのログから独立に組む）。"""
    v, p = [], ctx["src"]["prev"]
    rows = scr(ctx)
    if len(p["final"]) != N_PREV:
        v.append(f"r_prev_rows: 前のタスクの判定が {len(p['final'])} 件（{N_PREV} のはず）")
    for i, f1 in p["final"].items():
        if i not in rows:
            v.append(f"r_prev_rows: {i}: 行が無い")
            continue
        r, x = rows[i]
        f0 = p["first"][i]
        basis = f1.get("basis", "全文")
        exp_h = "入手不可" if basis in ("抄録", "なし") else ("完了" if i in p["xconf"] else "進行中")
        if f1["verdict"] == "含める" and f1.get("kind_detail") == "一次研究":
            q = p["quality"].get(i)
            exp_i = "進行中" if basis in ("抄録", "なし") else ("未実施" if q is None else ("進行中" if str(q.get("answer", "")).startswith("保留") else "完了"))
        else:
            exp_i = "未実施" if f1["verdict"] == "保留" else "対象外"
        j = str(x[9] or "")
        bad = []
        if x[3] != f1["verdict"]:
            bad.append("判定者1")
        if (f1["verdict"] == "除外") != (not blank(x[6])) or (f1["verdict"] == "除外" and not str(x[6]).startswith(f1["ecode"])):
            bad.append("除外理由")
        if x[7] != exp_h or x[8] != exp_i:
            bad.append("全文確認・品質評価")
        if f"1回目: {prev_label(f0)} → 最終: {prev_label(f1)}" not in j or f"用途: {prev_use(f1)} " not in j or "段: 全文段" not in j:
            bad.append("自由記入の 1 回目・最終・用途・段")
        if ("AI の判定: Claude 版" in j) != (i in p["has2"]):
            bad.append("自由記入の AI の判定の有無")
        if x[17] != "判定者 1" or not str(x[18] or "").startswith("全文段") or any(not blank(y) for y in x[19:23]):
            bad.append("R〜W 列")
        if bad:
            v.append(f"r_prev_rows: {i}: {'・'.join(bad)} がログと違う")
    return v


def r_judge1_rows(ctx):
    """題名・抄録段で判定者 1 が判定した 71 件（本タスクのログから独立に組む）。"""
    v, rows = [], scr(ctx)
    for i, d in ctx["src"]["j1"].items():
        if i not in rows:
            v.append(f"r_judge1_rows: {i}: 行が無い")
            continue
        r, x = rows[i]
        res = d["res"]
        ex = res["verdict"] == "除外"
        j = str(x[9] or "")
        bad = []
        if x[3] != res["verdict"]:
            bad.append("判定者1")
        if not ex and not blank(x[6]):
            bad.append("除外でないのに除外理由")
        if ex and is_e4bg(res) and not (str(x[6]).startswith("E4 背景（判定者 1 の選択のまま") and "範囲の外" in str(x[6])):
            bad.append("E4 背景の除外理由と意図（判断 6）")
        if ex and not is_e4bg(res) and x[6] != res["ecode"]:
            bad.append("除外理由のコード")
        if (x[7], x[8]) != (("対象外", "対象外") if ex else ("未完了", "未実施")):
            bad.append("全文確認・品質評価")
        must = ["段: 題名・抄録段", "判定者: 判定者 1", f"判定: {res['verdict']}", JUDGE1_USE[res["verdict"]], "材料: 抄録",
                "全訳" if d["order"] <= FULL_TRANSLATION else "固定の欄", jst(d["at"]), "『一致の表』"]
        if any(m not in j for m in must) or "AI の判定: Claude 版" in j:
            bad.append("自由記入（段・判定者・判定・用途・材料・問いの形・日付・AI の判定）")
        if x[17] != "判定者 1" or x[18] != "題名・抄録段" or any(not blank(y) for y in x[19:23]):
            bad.append("R〜W 列（判定者 1 の行に AI の値を置かない）")
        if bad:
            v.append(f"r_judge1_rows: {i}: {'・'.join(bad)}")
    if len(ctx["src"]["j1"]) != N_J1:
        v.append(f"r_judge1_rows: 判定者 1 の題名・抄録段が {len(ctx['src']['j1'])} 件（{N_J1} のはず）")
    return v


def r_ai_rows(ctx):
    """判定者 1 が判定していない 142 件: 判定者 1 の欄は初期値・AI の値は T〜V 列だけ（判断 5）。"""
    v, rows = [], scr(ctx)
    for i in ctx["src"]["ai_items"]:
        if i not in rows:
            v.append(f"r_ai_rows: {i}: 行が無い")
            continue
        r, x = rows[i]
        ta, reason, row = ctx["src"]["ai_ta"][i]
        bad = []
        if (x[3], nz(x[6]), x[7], x[8], nz(x[9])) != ("未判定", None, "未完了", "未実施", None):
            bad.append("判定者 1 の欄（D・G・H・I・J）が初期値でない")
        if "AI" not in str(x[17]) or "判定者 1 は判定していない" not in str(x[17]) or x[18] != "題名・抄録段（AI の予備判定）":
            bad.append("判定者・段")
        if x[19] != ta or nz(x[20]) != (reason if ta == "除外" else None):
            bad.append("AI の予備判定・除外理由が評価版と違う")
        if f"{row} 行" not in str(x[21] or "") or "評価版" not in str(x[21] or ""):
            bad.append("AI の値の出どころ（評価版の行）")
        if not blank(x[22]):
            bad.append("Q1／Q2 の列")
        if bad:
            v.append(f"r_ai_rows: {i}: {'・'.join(bad)}")
    if len(ctx["src"]["ai_items"]) != N_AI:
        v.append(f"r_ai_rows: AI の予備判定が {len(ctx['src']['ai_items'])} 件（{N_AI} のはず）")
    return v


def r_unjudged_rows(ctx):
    """どのログにも無い行は、判定者 1 の欄・R〜W 列とも初期値（空）。"""
    v = []
    known = set(ctx["src"]["prev"]["final"]) | set(ctx["src"]["j1"]) | set(ctx["src"]["ai_items"])
    for i, (r, x) in scr(ctx).items():
        if i in known:
            continue
        if (x[3], nz(x[6]), x[7], x[8], nz(x[9])) != ("未判定", None, "未完了", "未実施", None) or any(not blank(y) for y in x[17:23]):
            v.append(f"r_unjudged_rows: {i}: どのログにも無いのに初期値でない")
    return v


def r_w_empty(ctx):
    """Q1／Q2 の列（W）は、全文段を行っていないので全行で空。"""
    return [f"r_w_empty: {i}: W 列に値" for i, (r, x) in scr(ctx).items() if not blank(x[22])][:5]


def r_cmp(ctx):
    wc, v, p = ctx["wb"]["AI判定比較"], [], ctx["src"]["prev"]
    ids = [x[0] for x in ctx["src"]["judge"]] + [x["id"] for x in ctx["src"]["extra"]]
    want = [i for i in ids if i in p["final"] and i in ctx["src"]["ai_use"]]
    got = body(wc, 7)
    if [x[0] for _, x in got] != want:
        v.append(f"r_cmp: AI判定比較の行が 全文段の判定 ∩ 評価版 と違う: {[x[0] for _, x in got]}")
    for r, x in got:
        i = x[0]
        if i not in p["final"] or i not in ctx["src"]["ai_use"]:
            continue
        if x[2] != ctx["src"]["ai_use"][i] or x[3] != prev_use(p["final"][i]) or \
                wc.cell(r, 5).value != f'=IF(D{r}="","",IF(C{r}=D{r},"一致","要照合"))':
            v.append(f"r_cmp: {i}: AI用途判定・人間用途判定・一致の式が違う")
    return v


def r_agree(ctx):
    w, v = ctx["wb"]["一致の表"], []
    if [w.cell(4, c).value for c in range(1, 10)] != AGREE_HEADER or w.cell(4, 10).value is not None:
        v.append("r_agree: 見出しが違う")
    title = {x[0]: x[1] for x in ctx["src"]["judge"]}
    want = []
    for i, d in sorted(ctx["src"]["j1"].items(), key=lambda kv: kv[1]["order"]):
        res = d["res"]
        ta, reason, _ = ctx["src"]["ai_ta"][i]
        g = None
        if res["verdict"] == "除外":
            g = "E4 背景" if is_e4bg(res) else res["ecode"]
        same = "一致" if res["verdict"] == ta else "不一致"
        if res["verdict"] == "除外" and ta == "除外":
            code = "比べない" if is_e4bg(res) else ("一致" if re.match(r"(E\d)", reason or "").group(1) == res["ecode"] else "不一致")
        else:
            code = "—"
        want.append([d["order"], i, title[i], res["verdict"], g, ta, reason if ta == "除外" else None, same, code])
    got = [x for _, x in body(w, 9)]
    if len(got) != len(want):
        v.append(f"r_agree: 行が {len(got)}（{len(want)} のはず）")
    for a, b in zip(got, want):
        g_ok = (b[4] is None and blank(a[4])) or (b[4] == "E4 背景" and str(a[4]).startswith("E4 背景")) or a[4] == b[4]
        c_ok = str(a[8] or "").startswith(b[8])
        if a[:4] != b[:4] or not g_ok or a[5] != b[5] or nz(a[6]) != b[6] or a[7] != b[7] or not c_ok:
            v.append(f"r_agree: {b[1]}: 一致の表の行が独立に組んだ値と違う")
    return v[:10]


def r_groups(ctx):
    w, v = ctx["wb"]["群ごとの一覧"], []
    if [w.cell(4, c).value for c in range(1, 12)] != GROUP_HEADER:
        v.append("r_groups: 見出しが違う")
    cg = {x[0]: x[3] for x in ctx["src"]["judge"]}
    cnt = {}
    for i, d in list(ctx["src"]["j1"].items()) + list(ctx["src"]["ai_items"].items()):
        who = "j" if i in ctx["src"]["j1"] else "a"
        c = cnt.setdefault(cg[i], {"j": {"含める": 0, "保留": 0, "除外": 0}, "a": {"含める": 0, "保留": 0, "除外": 0}})
        c[who][d["res"]["verdict"]] += 1
    want = sorted([g.split("｜")[0], g, sum(c["j"].values()) + sum(c["a"].values()), sum(c["j"].values()), c["j"]["含める"],
                   c["j"]["保留"], c["j"]["除外"], sum(c["a"].values()), c["a"]["含める"], c["a"]["保留"], c["a"]["除外"]]
                  for g, c in cnt.items())
    rows = [x for _, x in body(w, 11)]
    got, tot = rows[:-1], rows[-1] if rows else None
    if sorted(got) != want:
        v.append(f"r_groups: 群の行が独立に数えた値と違う（{len(got)} 行 / {len(want)}）")
    if tot is None or tot[0] != "計" or tot[2:] != [sum(x[k] for x in want) for k in range(2, 11)]:
        v.append("r_groups: 計の行が違う")
    if want and (sum(x[2] for x in want) != N_J1 + N_AI):
        v.append("r_groups: 計が 213 でない")
    return v


def r_qa(ctx):
    w, v = ctx["wb"]["問いと答え"], []
    if [w.cell(4, c).value for c in range(1, 9)] != LOG_HEADER:
        v.append("r_qa: 見出しが違う")
    got = [x for _, x in body(w, 8)]
    prev = ctx["src"]["prev_log"]
    mine = [r for r in ctx["src"]["log"] if r["stage"] in ("ta1", "ta1e")]
    if len(got) != len(prev) + len(mine):
        v.append(f"r_qa: 行が {len(got)}（{len(prev) + len(mine)} のはず・AI の行は載せない）")
        return v
    for a, r in zip(got, prev):
        if not str(a[0]).startswith("前の作業") or a[1:7] != [r.get("seq"), r["item"], r["stage"], r["question"],
                                                             " ／ ".join(r.get("options") or []), r["answer"]] or nz(a[7]) != nz(r.get("note")):
            v.append(f"r_qa: 前の作業の {r.get('seq')} がログと違う")
            break
    for a, r in zip(got[len(prev):], mine):
        q = str(a[4] or "")
        if not str(a[0]).startswith("今回の作業") or a[1:4] != [r["seq"], r["item"], r["stage"]] or \
                a[5] != " ／ ".join(r["options"]) or a[6] != r["answer"] or nz(a[7]) != nz(r["note"]) or \
                not q.startswith(f"【{r['item']}・") or r["question_sha256"][:16] not in q or len(q) > 200:
            v.append(f"r_qa: 今回の作業の {r['seq']}（{r['item']}）がログと違う・問いの逐語を載せている")
            break
    return v


def r_extract(ctx):
    we, v = ctx["wb"]["全文抽出"], []
    ex = ctx["src"]["extract"]
    if ex is None:
        return ["r_extract: 前のタスクの全文抽出の data が無い"]
    n = max(we.max_column, len(ex["header"]))
    rows = [[we.cell(r, c).value for c in range(1, n + 1)] for r in range(5, we.max_row + 1)]
    rows = [x for x in rows if any(not blank(y) for y in x)]

    def norm(row):
        return [nz(y) for y in row] + [None] * (n - len(row))
    if norm(ex["header"]) != norm([we.cell(4, c).value for c in range(1, n + 1)]) or [norm(x) for x in ex["rows"]] != [norm(x) for x in rows]:
        v.append("r_extract: 中身が前のタスクの data/extract-rows.json と違う")
    if {x[0] for x in rows} != ctx["src"]["prev"]["xconf"]:
        v.append("r_extract: ID が抽出を確定した件と違う")
    return v


def r_search(ctx):
    v = []
    wr, wq = ctx["wb"]["探索の検索式"], ctx["wb"]["探索の一覧"]

    def rows(ws, n):
        return [[nz(y) for y in x] for _, x in body(ws, n)]
    want_r = [[nz(y) for y in (x["api"], x["query"], x["executed_at"], x.get("total_hits"), x.get("fetched"), x.get("passed_filter"),
                               "はい" if x.get("truncated") else "いいえ", x.get("error"))] for x in ctx["src"]["runs"]]
    if rows(wr, 8) != want_r or [wr.cell(4, c).value for c in range(1, 9)] != RUN_HEADER or wr.max_column > 8:
        v.append("r_search: 探索の検索式が data と違う")
    want_l = [[nz(y) for y in (x["key"], x["title"], x.get("year"), x.get("type"), x.get("venue"), x.get("language"), x.get("oa"),
                               x.get("overlap"), x.get("sources"), x.get("layer"), x.get("reading"), x.get("added_as") or "いいえ")]
              for x in ctx["src"]["recs"]]
    if rows(wq, 12) != want_l or [wq.cell(4, c).value for c in range(1, 13)] != LIST_HEADER or wq.max_column > 12:
        v.append("r_search: 探索の一覧が data と違う")
    return v


def r_intro(ctx):
    wi = ctx["wb"]["はじめに"]
    text = "\n".join(str(wi.cell(r, c).value or "") for r in range(1, wi.max_row + 1) for c in (1, 2))
    v = [f"r_intro: 「{s}」が無い" for s in INTRO_MUST if s not in text]
    n_j1, n_ai = len(ctx["src"]["j1"]), len(ctx["src"]["ai_items"])
    want = f"判定者 1 の判定 {len(ctx['src']['prev']['final']) + n_j1} 件（全文段 8・題名・抄録段 {n_j1}）／AI の予備判定だけ {n_ai} 件"
    if want not in text:
        v.append(f"r_intro: 進み具合の数がログと違う（期待「{want}」）")
    return v


def r_local(ctx):
    v = []
    for ws in ctx["wb"].worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and C.find_local(c.value):
                    v.append(f"r_local: 手元のパス・メールアドレスの形: {ws.title}!{c.coordinate}")
                if c.hyperlink is not None:
                    v.append(f"r_local: リンクのセル: {ws.title}!{c.coordinate}")
    v += [f"r_local: 手元のパス・メールアドレスの形・外へのリンク: {x}" for x in C.scan_package(ctx["path"])]
    return v[:10]


def r_formula(ctx):
    n_cmp = len(body(ctx["wb"]["AI判定比較"], 1))
    v = []
    for ws in ctx["wb"].worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.data_type == "f" and not (ws.title == "AI判定比較" and c.column_letter == "E" and 5 <= c.row < 5 + n_cmp):
                    v.append(f"r_formula: 式のセル: {ws.title}!{c.coordinate}")
    return v


def r_final(ctx):
    """--final: 220 件と X01 のすべてが、判定者 1（全文段・題名・抄録段）か AI の予備判定のどれか 1 つに入る。"""
    v = []
    p, j1, ai = set(ctx["src"]["prev"]["final"]), set(ctx["src"]["j1"]), set(ctx["src"]["ai_items"])
    ids = [x[0] for x in ctx["src"]["judge"]] + [x["id"] for x in ctx["src"]["extra"]]
    miss = [i for i in ids if i not in p | j1 | ai]
    if miss:
        v.append(f"r_final: どれにも入らない記録 {len(miss)} 件: {miss[:3]}")
    if (p & j1) | (p & ai) | (j1 & ai):
        v.append("r_final: 2 つ以上に入る記録がある")
    if (len(p), len(j1), len(ai)) != (N_PREV, N_J1, N_AI):
        v.append(f"r_final: 件数 {len(p)}・{len(j1)}・{len(ai)}（{N_PREV}・{N_J1}・{N_AI} のはず）")
    return v


RULES_COMMON = [
    r_sources,
    r_sheets,
    r_rows,
    r_static,
    r_validation,
    r_prev_rows,
    r_judge1_rows,
    r_ai_rows,
    r_unjudged_rows,
    r_w_empty,
    r_cmp,
    r_agree,
    r_groups,
    r_qa,
    r_extract,
    r_search,
    r_intro,
    r_local,
    r_formula,
]
RULES_FINAL = [
    r_final,
]


def check(path, src, final=False):
    ctx = {"wb": openpyxl.load_workbook(path), "src": src, "path": path}
    v = []
    for rule in RULES_COMMON + (RULES_FINAL if final else []):
        try:
            v += rule(ctx)
        except Exception as e:
            v.append(f"{rule.__name__}: 例外 {type(e).__name__}: {e}")
    return v


def selftest():
    import build_candidates as B
    ok = True
    tmpd = tempfile.mkdtemp(prefix="candchk-")
    base = os.path.join(tmpd, "base.xlsx")
    B.build(base)
    src = sources()

    def expect(name, path, must=None, s=None, final=True):
        nonlocal ok
        v = check(path, s or src, final=final)
        good = (not v) if must is None else any(x.startswith(must) for x in v)
        ok &= good
        print(("PASS" if good else "FAIL"), name, "" if good else v[:3])

    expect("陰性対照（実のログで作った表・--final）", base)
    rows = {x[0]: r for r, x in body(openpyxl.load_workbook(base)["スクリーニング"], 1)}

    def mut(name, fn, must):
        p = os.path.join(tmpd, f"m{abs(hash(name))}.xlsx")
        wb = openpyxl.load_workbook(base)
        fn(wb)
        wb.save(p)
        expect(name, p, must)

    def cell(sheet, ref, val):
        return lambda wb: wb[sheet].__setitem__(ref, val)

    def at(i, col, val):
        return lambda wb: wb["スクリーニング"].__setitem__(f"{col}{rows[i]}", val)

    s = "スクリーニング"
    expect("元の資料の SHA が違う", base, "r_sources", s={**src, "sha": {**src["sha"], "judge": "0" * 64}})
    mut("シートを足す", lambda wb: wb.create_sheet("x"), "r_sheets")
    mut("題名を変える", cell(s, "B5", "別の題名"), "r_rows")
    mut("見出しに列を足す", cell(s, "X4", "メモ"), "r_rows")
    mut("判定者2 を埋める", at("S14-23", "E", "含める"), "r_static")
    mut("暫定分類を変える", at("S02-06", "C", "既存レビュー"), "r_static")
    mut("入力規則を消す", lambda wb: wb[s].data_validations.dataValidation.pop(0), "r_validation")
    mut("入力規則の種類を変える", lambda wb: setattr(wb[s].data_validations.dataValidation[1], "type", "textLength"), "r_validation")
    # 前の作業の 8 件
    mut("前の作業の判定者1 をずらす", at("X01", "D", "保留"), "r_prev_rows")
    mut("前の作業の自由記入の段", lambda wb: wb[s][f"J{rows['S02-08']}"].__setattr__(
        "value", wb[s][f"J{rows['S02-08']}"].value.replace("段: 全文段", "段: 題名・抄録段")), "r_prev_rows")
    mut("前の作業の行に AI の値", at("S12-05", "T", "含める"), "r_prev_rows")
    # 判定者 1 の 71 件
    mut("判定者 1 の判定をずらす", at("S02-06", "D", "保留"), "r_judge1_rows")
    mut("E4 背景を E4 と書く（判断 6）", at("S04-85", "G", "E4"), "r_judge1_rows")
    mut("E4 背景から意図を落とす（判断 6）", at("S04-85", "G", "E4 背景（判定者 1 の選択のまま）"), "r_judge1_rows")
    mut("判定者 1 の除外理由のコードを変える", at("S12-04", "G", "E3"), "r_judge1_rows")
    mut("判定者 1 の含めるの全文確認を完了に", at("S02-06", "H", "完了"), "r_judge1_rows")
    mut("判定者 1 の自由記入から段を落とす", lambda wb: wb[s][f"J{rows['S02-06']}"].__setattr__(
        "value", wb[s][f"J{rows['S02-06']}"].value.replace("段: 題名・抄録段", "段: 全文段")), "r_judge1_rows")
    mut("判定者 1 の自由記入の問いの形を変える", lambda wb: wb[s][f"J{rows['S02-06']}"].__setattr__(
        "value", wb[s][f"J{rows['S02-06']}"].value.replace("全訳", "固定の欄")), "r_judge1_rows")
    mut("判定者 1 の行に AI の値（判断 5）", at("S02-06", "T", "含める"), "r_judge1_rows")
    mut("判定者 1 の行を AI と書く", at("S02-06", "R", "AI（評価版の予備判定・判定者 1 は判定していない）"), "r_judge1_rows")
    # AI の 142 件
    mut("AI の予備判定を判定者1 の欄に書く（判断 5）", at("S14-23", "D", "含める"), "r_ai_rows")
    mut("AI の行の自由記入に書く", at("S14-23", "J", "AI: 含める"), "r_ai_rows")
    mut("AI の行を判定者 1 と書く", at("S14-23", "R", "判定者 1"), "r_ai_rows")
    mut("AI の予備判定の値を変える", at("S14-23", "T", "除外"), "r_ai_rows")
    ai_ex = next(i for i, d in src["ai_items"].items() if d["res"]["verdict"] == "除外")
    mut("AI の除外理由を変える", at(ai_ex, "U", "E2（別の理由）"), "r_ai_rows")
    mut("AI の値の出どころの行を変える", at("S14-23", "V", "評価版『Claudeスクリーニング案』3 行"), "r_ai_rows")
    mut("AI の含めるの件に全文段の除外理由を写す", at("S14-23", "U", src["ai_ta"]["S14-23"][1]), "r_ai_rows")
    # どのログにも無い行（実のログには無いので、ログから 1 行抜いた src で当てる）
    src_drop = copy.deepcopy(src)
    src_drop["ai_items"].pop("S14-23")
    src_drop["log"] = [r for r in src_drop["log"] if r["item"] != "S14-23"]
    expect("ログに無い行に値（AI の行を 1 件ログから抜く）", base, "r_unjudged_rows", s=src_drop)
    expect("--final: どれにも入らない記録", base, "r_final", s=src_drop)
    mut("W 列に値", at("S14-24" if "S14-24" in rows else "S14-26", "W", "Q1"), "r_w_empty")
    mut("AI判定比較の AI 用途を変える", cell("AI判定比較", "C5", "中心候補"), "r_cmp")
    mut("AI判定比較の行を足す", lambda wb: [wb["AI判定比較"].__setitem__(k, v) for k, v in (("A12", "S02-06"), ("C12", "中心候補"))],
        "r_cmp")
    mut("AI判定比較の式を変える", cell("AI判定比較", "E5", '=IF(D5="","","一致")'), "r_cmp")
    mut("一致の表の判定の一致を変える", cell("一致の表", "H5", "不一致"), "r_agree")
    mut("一致の表の AI の値を変える", cell("一致の表", "F5", "除外"), "r_agree")
    mut("一致の表の行を消す", lambda wb: wb["一致の表"].delete_rows(10), "r_agree")
    e4r = next(r for r in range(5, 80) if openpyxl.load_workbook(base)["一致の表"].cell(r, 2).value == "S13-19")
    mut("一致の表で E4 背景の除外理由を比べる（判断 6）", cell("一致の表", f"I{e4r}", "不一致"), "r_agree")
    mut("群ごとの一覧の数を変える", cell("群ごとの一覧", "E5", 99), "r_groups")
    mut("群ごとの一覧の計を変える", lambda wb: wb["群ごとの一覧"].__setitem__(f"C{body(wb['群ごとの一覧'], 1)[-1][0]}", 214), "r_groups")
    mut("問いと答えに問いの逐語", cell("問いと答え", "E30", "【S15-15・題名・抄録段】" + "抄録の訳" * 80), "r_qa")
    mut("問いと答えの答えを変える", cell("問いと答え", "G25", "保留"), "r_qa")
    mut("問いと答えに AI の行を足す", lambda wb: [wb["問いと答え"].__setitem__(f"{c}{5 + 17 + 72}", v)
                                         for c, v in zip("ABCD", ["今回の作業", 300, "S14-23", "ai_ta"])], "r_qa")
    mut("全文抽出のセルを変える", cell("全文抽出", "C5", "別の集団"), "r_extract")
    mut("探索の一覧の層を変える", cell("探索の一覧", "J5", "Z"), "r_search")
    mut("探索の検索式の件数を変える", cell("探索の検索式", "D5", 999999), "r_search")
    mut("はじめにの注意を消す", lambda wb: [wb["はじめに"].cell(r, 2).__setattr__("value", "")
                                     for r in range(5, 40) if "判定者 2 に渡さない" in str(wb["はじめに"].cell(r, 2).value or "")],
        "r_intro")
    mut("はじめにの進み具合の数を変える", lambda wb: [wb["はじめに"].cell(r, 2).__setattr__("value", str(wb["はじめに"].cell(r, 2).value).replace("142 件", "141 件"))
                                          for r in range(5, 40) if "AI の予備判定だけ" in str(wb["はじめに"].cell(r, 2).value or "")],
        "r_intro")
    mut("手元のパス", cell("問いと答え", "H5", "C:\\Users\\someone\\Downloads\\x.pdf"), "r_local")
    mut("メールアドレス", cell("探索の一覧", "B6", "contact a.b@example.org"), "r_local")
    mut("リンクのセル", lambda wb: setattr(wb["探索の一覧"]["B5"], "hyperlink", "https://example.org/x"), "r_local")
    mut("式のセル", cell("探索の一覧", "B5", "=1+1"), "r_formula")
    # 対照: 書き込み側の put は = で始まる文字列を式にしない
    p = os.path.join(tmpd, "put.xlsx")
    wb = openpyxl.load_workbook(base)
    B.put(wb["探索の一覧"]["B5"], "=1+1")
    wb.save(p)
    good = openpyxl.load_workbook(p)["探索の一覧"]["B5"].data_type == "s"
    print(("PASS" if good else "FAIL"), "put は = を文字列のまま書く（対照）")
    ok &= good
    expect("--final なしでも陰性対照は緑", base, final=False)
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    v = check(C.CAND_ARCHIVE, sources(), final="--final" in argv)
    if os.path.exists(C.CAND_SHA_RECORD):
        rec = open(C.CAND_SHA_RECORD, encoding="utf-8").read().strip()
        for p in (C.CAND_ARCHIVE, C.CAND_DOWNLOADS):
            if C.sha256(p) != rec:
                v.append(f"表の SHA-256 が記録と違う: {os.path.basename(p)}")
    else:
        v.append("表の SHA-256 の記録が無い")
    for e in v:
        print("違反:", e)
    print(f"違反 {len(v)}")
    sys.exit(1 if v else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
