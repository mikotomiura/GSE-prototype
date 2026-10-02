"""追加候補の表（v2）を、元の資料とログから毎回作り直す（design.md §9 を判断 3〜6 に合わせて縮めた形・引き継ぎ §2 の 3）。

前のタスクの build_candidates.py を写して広げた（前のタスクの道具は変えない）。
元の資料: 判定者用ファイルの『追加候補』220 件（読むだけ）・前のタスクの X01 と 17 行のログ（全文段・読むだけ）・本タスクのログ
          （判定者 1 の題名・抄録段 71 件 = ta1/ta1e と、AI〈評価版〉の予備判定 142 件 = ai_ta）・評価版（読むだけ）・
          前のタスクの全文抽出・探索の data（読むだけ）。
★ AI の予備判定は判定者 1 の欄（D 判定者1・G 除外理由・J 自由記入）に書かない。AI の行は判定者 1 の欄を初期値のまま残し、
  R〜V 列に「AI（評価版）」と明記して載せる（判断 5）。
★ 判定者 1 の「除外 E4 背景」6 件は、意図が「範囲の外・背景として残す」（一次研究でないの意味ではない）と書く（判断 6）。
★ Downloads の表が最後に書いた SHA-256 と違えば止まる（手で記入された可能性）。本タスクの記録が無い初回は、前のタスクの記録
  （v1 の表）と比べる。
使い方: uv run --with openpyxl python build_candidates.py [--dry-run]
"""
import datetime
import json
import os
import shutil
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

import common as C
from build_ta_sheet import POP, content_key

PREV_CAND_SHA_RECORD = os.path.join(C.PREV_TASK, "archive", "candidates-sha256.txt")

# --- 答え → 表の値（前のタスクの design.md §1・§7）。★ 検査器は別に同じ表を持つ（import しない） ---
USE_TO_HUMAN = {"中心-A": "中心候補", "中心-B": "中心候補", "背景保持": "背景保持", "方法論保持": "方法論保持",
                "訂正連結": "訂正連結", "除外": "除外", "保留": "保留"}
E4_KIND = {"レビュー": "背景保持", "論考": "背景保持", "研究計画": "背景保持", "一次研究": "背景保持",
           "方法論": "方法論保持", "訂正通知": "訂正連結"}
CRITERIA_VERSION = "評価プロトコル v1.0＋2026-09-30 の範囲の決定＋2026-10-01 の読み方"
UNCLASSIFIED = "追加候補（未分類）"
JUDGE1 = "判定者 1"
AI_LABEL = "AI（評価版の予備判定・判定者 1 は判定していない）"
STAGE_FT = "全文段（1 回目・2 回目）"
STAGE_TA = "題名・抄録段"
STAGE_AI = "題名・抄録段（AI の予備判定）"
E4_BG_LABEL = "E4 背景（判定者 1 の選択のまま・意図は「範囲の外・背景として残す」で、一次研究でないの意味ではない）"
FULL_TRANSLATION = 8  # 順 1〜8 は抄録の全訳で聞いた・9 から固定の欄（判断 3）

SCR_HEADER = ["ID", "論文タイトル", "暫定分類", "判定者1", "判定者2", "最終判定", "除外理由", "全文確認・抽出", "品質評価", "自由記入",
              "出どころ", "DOI", "年", "掲載誌", "本文の入手（OpenAlex）", "同じ研究の群", "内容の群（機械の分類・判定の材料ではない）",
              "判定者", "判定の段", "AI の予備判定（題名・抄録段・評価版）", "AI の除外理由（評価版の逐語）", "AI の値の出どころ",
              "研究者の読みに依存（Q1／Q2）"]
CMP_HEADER = ["ID", "論文タイトル", "AI用途判定", "人間用途判定", "分類の一致", "人間判定の理由・版", "最終合意・次の作業"]
AGREE_HEADER = ["順", "ID", "論文タイトル", "判定者 1（題名・抄録段）", "判定者 1 の除外理由", "AI の予備判定（題名・抄録段・評価版）",
                "AI の除外理由（評価版の逐語）", "判定の一致", "除外理由の一致"]
GROUP_HEADER = ["対象者", "内容の群（機械の分類・判定の材料ではない）", "件数", "判定者 1：計", "判定者 1：含める", "判定者 1：保留",
                "判定者 1：除外", "AI の予備判定：計", "AI：含める", "AI：保留", "AI：除外"]
LOG_HEADER = ["作業", "seq", "ID", "段", "問い（逐語）", "選択肢", "答え", "補足（note）"]
PREV_WORK = "前の作業（10-02・全文段）"
THIS_WORK = "今回の作業（10-02〜03・題名・抄録段）"
VOCAB = {"D": '"未判定,含める,除外,保留"', "E": '"未判定,含める,除外,保留"', "F": '"未判定,含める,除外,保留"',
         "H": '"未完了,進行中,完了,入手不可,対象外"', "I": '"未実施,進行中,完了,対象外"'}


def load_json(p, default=None):
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding="utf-8"))


def read_log(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()] if os.path.exists(p) else []


def prev_decisions(log):
    """前のタスクのログ: 件ごとに 1 回目と最終（2/2e の最後・無ければ 1 回目）・品質（q）・抽出の確定（x）。"""
    first, final, quality, xconf = {}, {}, {}, set()
    for r in log:
        i, st = r["item"], r["stage"]
        if st in ("1", "1e"):
            first[i] = r["result"]
        elif st in ("2", "2e"):
            final[i] = r["result"]
        elif st == "q":
            quality[i] = r["result"]
        elif st == "x":
            xconf.update(r["result"]["items"])
    for i in first:
        final.setdefault(i, first[i])
    return first, final, quality, xconf


def this_decisions(log):
    """本タスクのログ: 件ごとに {judge: 判定者 1 / AI, result: 最終, order, rec（最後の行）}。"""
    out = {}
    for r in log:
        if r["stage"] in ("ta1", "ta1e"):
            out[r["item"]] = {"judge": JUDGE1, "result": r["result"], "order": r["order"], "rec": r}
        elif r["stage"] == "ai_ta":
            out[r["item"]] = {"judge": "AI", "result": r["result"], "order": r["order"], "rec": r}
    return out


def candidates():
    """判定者用ファイルの『追加候補』220 件（順のまま）。"""
    ws = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True)[C.JUDGE_SHEET]
    rows = list(ws.iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    col = {k: h.index(k) for k in ("候補番号", "出どころ", "題名（書誌の記録）", "年", "掲載誌", "DOI", "本文の入手（OpenAlex）", "同じ研究の群")}
    col["内容の群"] = next(k for k, c in enumerate(h) if c and str(c).startswith("内容の群"))
    out = []
    for r in rows[C.JUDGE_HEADER_ROW:]:
        if r and r[0]:
            out.append({"id": r[col["候補番号"]], "title": r[col["題名（書誌の記録）"]], "source": r[col["出どころ"]],
                        "doi": r[col["DOI"]], "year": r[col["年"]], "venue": r[col["掲載誌"]], "oa": r[col["本文の入手（OpenAlex）"]],
                        "group": r[col["同じ研究の群"]], "content": r[col["内容の群"]]})
    assert len(out) == C.N_CANDIDATES, len(out)
    return out


def appraisal():
    """評価版: 『Claude適格性評価』の用途判定と、『Claudeスクリーニング案』の題名・抄録段の予備判定・除外理由・行。"""
    wb = openpyxl.load_workbook(C.APPRAISAL, read_only=True)

    def sheet(name):
        rows = list(wb[name].iter_rows(values_only=True))
        h = next(k for k, r in enumerate(rows[:8]) if r and r[0] == "候補番号")
        return rows, h, list(rows[h])
    rows, h, hd = sheet("Claude適格性評価")
    use = {r[0]: r[hd.index("用途判定（Claude）")] for r in rows[h + 1:] if r and r[0]}
    rows, h, hd = sheet("Claudeスクリーニング案")
    ta = {r[0]: {"ta": r[hd.index("Claude予備判定（題名・抄録段）")], "reason": r[hd.index("除外理由")], "row": k + 1}
          for k, r in enumerate(rows) if k > h and r and r[0]}
    return use, ta


def use_of(result):
    if result["verdict"] == "含める":
        return result["use"]
    if result["verdict"] == "保留":
        return "保留"
    e = result.get("ecode") or ""
    if e == "E2":
        return "背景保持"
    if e == "E4":
        return E4_KIND[result["kind_detail"]]
    if e == "E6":
        return "保留"
    return "除外"


def label(r):
    if r["verdict"] == "含める":
        return f"含める（{r['use']}）"
    if r["verdict"] == "除外":
        return f"除外 {r['ecode']}"
    return "保留"


def prev_cells(i, first, final, quality, xconf, has_ai):
    """前のタスクで全文段まで判定した記録（S02-08 ほか 7 件と X01）の欄（前のタスクの書き方のまま）。"""
    f0, f1 = first[i], final[i]
    basis = f1.get("basis", "全文")
    use = use_of(f1)
    g = f"{f1['ecode']} {f1.get('elabel', '')}".strip() if f1["verdict"] == "除外" else ""
    h = "入手不可" if basis in ("抄録", "なし") else ("完了" if i in xconf else "進行中")
    if f1["verdict"] == "含める" and f1.get("kind_detail") == "一次研究":
        q = quality.get(i)
        if basis in ("抄録", "なし"):
            ival = "進行中"
        elif q is None:
            ival = "未実施"
        elif str(q.get("answer", "")).startswith("保留"):
            ival = "進行中"
        else:
            ival = "完了"
    elif f1["verdict"] == "保留":
        ival = "未実施"
    else:
        ival = "対象外"
    changed = "" if label(f0) == label(f1) else f"（変えた理由: {f1.get('reason', '')}）"
    ai = "Claude 版（2 回目で見た）" if has_ai else "なし（2 回目なし）"
    basis_label = {"なし": "題名と書誌だけ"}.get(basis, basis)
    j = (f"用途: {use} ／ 段: 全文段 ／ 1回目: {label(f0)} → 最終: {label(f1)}{changed} ／ 材料: {basis_label} ／ AI の判定: {ai} ／ "
         f"{f1.get('date', '')} ／ ログ: 『問いと答え』")
    return {"D": f1["verdict"], "G": g, "H": h, "I": ival, "J": j, "human_use": USE_TO_HUMAN[use],
            "reason": f1.get("reason_summary", ""), "next": f1.get("next", "")}


def jst_date(ts):
    t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return t.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()


def judge1_g(res):
    if res["verdict"] != "除外":
        return None
    return E4_BG_LABEL if str(res.get("ecode", "")).startswith("E4 背景") else res["ecode"]


def judge1_use(res):
    if res["verdict"] == "含める":
        return "未定（全文段で決まる・全文段は未実施）"
    if res["verdict"] == "保留":
        return "保留（全文段は未実施）"
    return "背景保持"  # E2・E4 背景（範囲の外・背景として残す）


def judge1_cells(d):
    """判定者 1 が題名・抄録段で判定した 71 件の欄。"""
    res, rec = d["result"], d["rec"]
    excluded = res["verdict"] == "除外"
    form = "抄録の日本語の全訳" if d["order"] <= FULL_TRANSLATION else "抄録の事実を固定の欄に抜き出したもの"
    j = (f"用途: {judge1_use(res)} ／ 段: 題名・抄録段 ／ 判定者: 判定者 1 ／ 判定: {res['verdict']}"
         + (f"（{judge1_g(res)}）" if excluded else "")
         + f" ／ 材料: 抄録（問いに{form}を載せ、原文は判定者 1 の手元の表にあった）／ AI の判定: 判定の時の問いには載せていない。"
           f"判定の後に機械で突き合わせた（『一致の表』）／ {jst_date(rec['answered_at'])} ／ ログ: 『問いと答え』")
    return {"D": res["verdict"], "G": judge1_g(res), "H": "対象外" if excluded else "未完了",
            "I": "対象外" if excluded else "未実施", "J": j}


def agree_flags(res, ai):
    v_same = "一致" if res["verdict"] == ai["ta"] else "不一致"
    if res["verdict"] == "除外" and ai["ta"] == "除外":
        if str(res.get("ecode", "")).startswith("E4 背景"):
            code = "比べない（判定者 1 の E4 背景は意図が範囲の外）"
        else:
            code = "一致" if (ai["reason"] or "")[:2] == res["ecode"] else "不一致"
    else:
        code = "—"
    return v_same, code


def group_rows(cands, dec):
    """未判定だった 213 件を内容の群で数える（行の順は対象者 → AI の種類 → デザイン）。"""
    by = {}
    for r in cands:
        d = dec.get(r["id"])
        if d is None:
            continue
        g = r["content"] or "不明｜不明｜不明"
        c = by.setdefault(g, {"n": 0, "j": {"含める": 0, "保留": 0, "除外": 0}, "a": {"含める": 0, "保留": 0, "除外": 0}})
        c["n"] += 1
        c["j" if d["judge"] == JUDGE1 else "a"][d["result"]["verdict"]] += 1
    out = []
    for g in sorted(by, key=content_key):
        c = by[g]
        out.append([g.split("｜")[0], g, c["n"], sum(c["j"].values()), c["j"]["含める"], c["j"]["保留"], c["j"]["除外"],
                    sum(c["a"].values()), c["a"]["含める"], c["a"]["保留"], c["a"]["除外"]])
    return out


def pop_rows(groups):
    """対象者ごとの小計と計（提案のドキュメント §7 の表と同じ数）。"""
    out = []
    for p in POP:
        rows = [x for x in groups if x[0] == p]
        if rows:
            out.append([p] + [sum(x[k] for x in rows) for k in range(2, 11)])
    out.append(["計"] + [sum(x[k] for x in groups) for k in range(2, 11)])
    return out


def put(cell, v):
    """セルに値を書く。★ 先頭が = の文字列は式にしない（探索の題名など外の文が式になるのを防ぐ）。"""
    cell.value = v
    if isinstance(v, str) and v.startswith("="):
        cell.data_type = "s"
    return cell


def add_sheet(wb, name, title, note, header, rows, widths=None):
    ws = wb.create_sheet(name)
    put(ws["A1"], title).font = Font(bold=True, size=12)
    put(ws["A2"], note)
    for c, hd in enumerate(header, 1):
        put(ws.cell(4, c), hd).font = Font(bold=True)
    for r, row in enumerate(rows, 5):
        for c, v in enumerate(row, 1):
            put(ws.cell(r, c), v).alignment = Alignment(wrap_text=True, vertical="top")
    for c in range(1, len(header) + 1):
        w = (widths or {}).get(c, 14 if c == 1 else 30)
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = w
    ws.freeze_panes = "B5"
    return ws


def intro_rows(n):
    return [
        ("このファイル", "研究者の DB（09-18）に無い追加候補（サーヴェイで見つかった 220 件と、判定者 1 が足した 1 件）を、研究者の『スクリーニング』と"
                       "同じ列で並べた。DB の記録ではなく提案で、DB に入れるかは研究者が決める。"),
        ("判定者 2 に渡すとき", "このファイルは判定者 2 に渡さない（判定者1 の欄・AI の予備判定・『AI判定比較』『一致の表』『問いと答え』があると、"
                             "2 人の判定が独立でなくなる）。判定者 2 に渡す版は、『スクリーニング』の D・G・H・I・J 列を初期値（判定者1 = 未判定・"
                             "除外理由 = 空・全文確認 = 未完了・品質評価 = 未実施・自由記入 = 空）に戻し、R〜W 列（判定者・判定の段・AI の予備判定・"
                             "AI の除外理由・AI の値の出どころ・研究者の読みに依存）を消し、『探索の一覧』の「足した（ID）」列を空にし、"
                             "『AI判定比較』『一致の表』『群ごとの一覧』『全文抽出』『品質評価』『問いと答え』のシートを消し、"
                             "『はじめに』を判定者 2 用に書き直して作る（どれも判定者 1 の判定・理由・進み具合・AI の判定を含む）。"),
        ("基準の版", CRITERIA_VERSION + "（判定者用ファイルの『判定基準』と同じ）"),
        ("判定者と段（R・S 列）", f"220 件と足した 1 件は、次の 3 つに分かれる。(1) 判定者 1 が全文段で判定した 8 件（S02-08 ほか 7 件と X01）／"
                              f"(2) 判定者 1 が題名・抄録段で判定した {n['j1']} 件／(3) 判定者 1 が判定していない {n['ai']} 件"
                              "（AI〈評価版〉の題名・抄録段の予備判定だけがある）。R 列に判定者、S 列に段を書いた。"),
        ("全文段の 8 件", "各件を 2 段で記録した: 1 回目は AI の判定を見ずに選び、2 回目に AI の判定（評価版）を見て変えるかを選んだ。"
                         "評価版に行が無い X01 は 2 回目を置かず、新しい AI の判定も作っていない。"),
        ("題名・抄録段の判定者 1", f"判定者 1 は {n['j1']} 件を、問い（1 回に 4 件まで）で判定した。問いには題名・年・掲載誌と、"
                                f"順 1〜{FULL_TRANSLATION} は抄録の日本語の全訳、順 {FULL_TRANSLATION + 1} からは抄録の事実を固定の欄"
                                "（種類・対象と N・AI・疲労・結果）に抜き出したものを載せ、原文は判定者 1 の手元の表にあった。"
                                "問いに AI の判定・推奨は載せていない。答えは対話の記録から機械で取り出し、手で写していない。"
                                "選択肢は 含める／保留／除外 E4 背景（レビュー・尺度の原著・理論）／除外（ほかの理由。続けて E コードを聞いた）。"),
        ("判定者 1 の「除外 E4 背景」", f"判定者 1 が「除外 E4 背景」を選んだ {n['e4bg']} 件は、判定者 1 に確かめたところ、意図は"
                                    "「範囲の外・背景として残す」で、一次研究でない（E4）の意味ではなかった。判定者 1 の選んだ値は変えず、"
                                    "除外理由に「E4 背景（判定者 1 の選択のまま…）」と書いた。E コードの付け直しは、研究者・判定者 2 との照合の段で行う。"),
        ("題名・抄録段の後", "判定者 1 が題名・抄録段で含める・保留にした件の全文段は、このファイルの時点では行っていない（全文確認 = 未完了・"
                           "品質評価 = 未実施・用途は未定）。抄録段で除外した件は全文確認・品質評価とも対象外。"),
        ("AI の予備判定の行", f"判定者 1 が判定していない {n['ai']} 件は、判定者 1 の欄（D 判定者1・G 除外理由・J 自由記入）を初期値のまま残し、"
                            "AI の予備判定（評価版『Claudeスクリーニング案』の題名・抄録段）と除外理由の逐語を T・U 列に、評価版の行を V 列に写した。"
                            "これは人の判定ではない。新しい AI の判定は作っていない（評価版の値をそのまま写した）。"),
        ("AI の判定", "追加候補の AI の判定は Claude 版（2026-09-30 の評価版）だけで、GPT 版は無い。『AI判定比較』は全文段の 7 件（評価版に行がある記録）、"
                    f"『一致の表』は題名・抄録段で判定者 1 が判定した {n['j1']} 件と評価版の題名・抄録段の予備判定を、判定の後に機械で突き合わせた。"),
        ("判定の前に読んだもの", "判定者 1 は、判定の前に、追加候補の AI の評価版（Claude 版）を読んでいる（盲検ではない）。"),
        ("暫定分類の列", f"研究者の DB の暫定分類は研究者が付けた。追加候補には研究者の分類が無いので、全行「{UNCLASSIFIED}」とした（AI の分類を入れていない）。"
                       "内容の群の列は機械の分類で、判定の材料ではない。『群ごとの一覧』はこの列で数えた。"),
        ("Q1／Q2 の列（W 列）", "基準の読み方（研究者に決めていただく Q1・Q2）で判定が変わりうる件の印。全文段で項目文・定義を確かめて付けるので、"
                             "全文段を行っていないこのファイルでは空。"),
        ("答えと用途の対応", "含める（中心-A／中心-B）→ 中心候補／除外 E2 → 背景保持／除外 E4 → レビュー・論考・研究計画は背景保持、方法論は方法論保持、"
                         "訂正通知は訂正連結／除外 E1・E3・E5・E7 → 除外／保留（E6 を含む）→ 保留。"
                         "題名・抄録段の含めるは用途が未定（全文段で決まる）。判定者 1 の「除外 E4 背景」は背景保持。"),
        ("品質評価", "判定で含めた一次研究だけ全文段で確定する（JBI・尺度開発は COSMIN・6 領域・合計点なし）。このファイルの時点で確定した件は無い。"),
        ("無料の本文", "有料の本文・有料のデータベースは使っていない。抄録は無料の学術 API（メールアドレス・鍵は送っていない）と、"
                     "DOI の行き先のページの抄録の欄から取った。"),
        ("Claude の関与", "抄録の取得・問いの作成（全訳・事実の欄の抜き出し）・本文の取得・抽出の下書き・原文との照合・レビューを狙った探索は、"
                        "Claude（メインとサブエージェント）が行い、判定は判定者 1 が行った。AI の予備判定の行（T〜V 列）は評価版の写しで、判定者 1 の判定ではない。"),
        ("探索", "『探索の検索式』『探索の一覧』: AI の語 × 疲労の語 × レビューの語（2020 年以降）で 4 つの無料の学術 API を引き、条件を通った記録をすべて載せた。"
                "読む一覧の 46 件のうち、重なりの 3 件を除く 43 件は、判定者 1 の作業量の都合でこのファイルでは候補に足していない"
                "（足した（ID）の列はすべて「いいえ」。X01 は探索ではなく、34 件の作業で判定者 1 が見つけた記録）。"),
        ("記録", "質問と答えは『問いと答え』（作業記録の写し・1 行 1 問）。題名・抄録段の問いの逐語は抄録の訳・要約を含むので載せず、"
                "判定者 1 の手元の記録と SHA-256 で結んだ。"),
        ("進み具合", f"判定者 1 の判定 {n['judged']} 件（全文段 8・題名・抄録段 {n['j1']}）／AI の予備判定だけ {n['ai']} 件／計 {n['rows']} 件。"),
    ]


def build(dst, log_path=None):
    prev_log = read_log(C.PREV_LOG)
    first, final, quality, xconf = prev_decisions(prev_log)
    this_log = read_log(log_path or C.LOG)
    dec = this_decisions(this_log)
    cands = candidates()
    extra = load_json(C.PREV_EXTRA_RECORDS, [])
    ai_use, ai_ta = appraisal()
    rows_src = cands + [{"id": x["id"], "title": x["title"], "source": x["source"], "doi": x.get("doi"), "year": x.get("year"),
                         "venue": x.get("venue"), "oa": x.get("oa"), "group": None, "content": x.get("content")} for x in extra]
    ids = [r["id"] for r in rows_src]
    assert len(ids) == len(set(ids)), "ID の重複"
    assert not (set(final) & set(dec)), "前のタスクと本タスクで同じ記録を判定している"
    unknown = [i for i in list(final) + list(dec) if i not in ids]
    assert not unknown, f"ログに表に無い ID: {unknown}"

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    wb.properties.creator = wb.properties.lastModifiedBy = JUDGE1
    n = {"j1": sum(d["judge"] == JUDGE1 for d in dec.values()), "ai": sum(d["judge"] == "AI" for d in dec.values()),
         "e4bg": sum(str(d["result"].get("ecode", "")).startswith("E4 背景") for d in dec.values()), "rows": len(ids)}
    n["judged"] = len(final) + n["j1"]
    add_sheet(wb, "はじめに", "追加候補（判定者 1）｜何のファイルか", "このファイルは判定者 1 が作った。研究者の DB とは別のファイル。",
              ["項目", "説明"], intro_rows(n), {1: 22, 2: 110})
    scr_rows, cmp_rows = [], []
    for r in rows_src:
        i = r["id"]
        row = [i, r["title"], UNCLASSIFIED, "未判定", "未判定", "未判定", None, "未完了", "未実施", None,
               r["source"], r["doi"], r["year"], r["venue"], r["oa"], r["group"], r["content"],
               None, None, None, None, None, None]
        if i in final:
            v = prev_cells(i, first, final, quality, xconf, i in ai_use)
            row[3], row[6], row[7], row[8], row[9] = v["D"], v["G"] or None, v["H"], v["I"], v["J"]
            row[17], row[18] = JUDGE1, STAGE_FT
            if i in ai_use:
                cmp_rows.append([i, r["title"], ai_use[i], v["human_use"], None,
                                 f"{v['reason']} ／ 基準の版: {CRITERIA_VERSION}".strip(" ／"),
                                 f"次の作業: {v['next']}（最終合意は判定者 2 の後）" if v["next"] else "（最終合意は判定者 2 の後）"])
        elif i in dec and dec[i]["judge"] == JUDGE1:
            v = judge1_cells(dec[i])
            row[3], row[6], row[7], row[8], row[9] = v["D"], v["G"], v["H"], v["I"], v["J"]
            row[17], row[18] = JUDGE1, STAGE_TA
        elif i in dec:
            a = ai_ta[i]
            row[17], row[18] = AI_LABEL, STAGE_AI
            row[19] = a["ta"]
            row[20] = a["reason"] if a["ta"] == "除外" else None
            row[21] = f"評価版『Claudeスクリーニング案』{a['row']} 行（題名・抄録段の予備判定と除外理由の列）"
        scr_rows.append(row)
    ws = add_sheet(wb, "スクリーニング", "追加候補｜文献選定・全文確認（研究者の『スクリーニング』と同じ列 ＋ R〜W 列）",
                   "青字の欄は入力用（研究者と同じ）。判定者1・2は独立した人間の担当者を想定し、AIの予備整理を独立判定に数えません。"
                   "判定者2・最終判定は未判定のまま。R〜W 列は判定者 1 が足した列（判定者・段・AI の予備判定）。",
                   SCR_HEADER, scr_rows, {2: 50, 10: 50, 21: 40, 22: 30})
    last = 4 + len(scr_rows)
    for col, f in VOCAB.items():
        dv = DataValidation(type="list", formula1=f, allow_blank=True)
        dv.add(f"{col}5:{col}{last}")
        ws.add_data_validation(dv)
    wc = add_sheet(wb, "AI判定比較", "AI判定比較｜全文段で判定者 1 が判定し、評価版に行がある記録",
                   "AI用途判定は Claude 版（2026-09-30 の評価版）。一致欄は用途分類の一致のみで、品質評価やκではありません。", CMP_HEADER, cmp_rows)
    for k in range(len(cmp_rows)):
        r = 5 + k
        wc[f"E{r}"] = f'=IF(D{r}="","",IF(C{r}=D{r},"一致","要照合"))'
    dv = DataValidation(type="list", formula1='"中心候補,背景保持,方法論保持,訂正連結,除外,保留"', allow_blank=True)
    dv.add(f"D5:D{max(5, 4 + len(cmp_rows))}")
    wc.add_data_validation(dv)
    title = {r["id"]: r["title"] for r in rows_src}
    agree = []
    for i, d in sorted(((i, d) for i, d in dec.items() if d["judge"] == JUDGE1), key=lambda x: x[1]["order"]):
        a = ai_ta[i]
        same, code = agree_flags(d["result"], a)
        agree.append([d["order"], i, title[i], d["result"]["verdict"], judge1_g(d["result"]), a["ta"],
                      a["reason"] if a["ta"] == "除外" else None, same, code])
    add_sheet(wb, "一致の表", "一致の表｜題名・抄録段で判定者 1 が判定した記録と、評価版の題名・抄録段の予備判定",
              "判定者 1 の判定の後に機械で突き合わせた（判定者 1 は判定の時の問いで AI の値を見ていない）。判定の一致は 含める／保留／除外 の一致、"
              "除外理由の一致は両方が除外のときの E コードの一致。一致の率は品質評価やκではない。", AGREE_HEADER, agree, {3: 50, 7: 40})
    groups = group_rows(cands, dec)
    add_sheet(wb, "群ごとの一覧", "群ごとの一覧｜未判定だった 213 件を内容の群で数えた（誰が判定したか・判定の内訳）",
              "内容の群は題名と抄録からの機械の分類で、判定の材料ではない。判定者 1 = 題名・抄録段で判定者 1 が判定／"
              "AI = 判定者 1 が判定していない（評価版の題名・抄録段の予備判定だけ）。前の作業で全文段まで判定した 7 件は含めない。",
              GROUP_HEADER, groups + [["計", None] + [sum(x[k] for x in groups) for k in range(2, 11)]], {2: 50})
    ex = load_json(C.PREV_EXTRACT_ROWS)
    add_sheet(wb, "全文抽出", "追加候補の全文抽出｜34 件の写しの『判定者1_全文抽出』と同じ列（全文段の記録だけ）",
              "Claude の下書きを判定者 1 が確かめた。数値は原文どおり。原文の箇所を右端に記す。",
              ex["header"] if ex else ["ID"], ex["rows"] if ex else [])
    runs = load_json(C.SEARCH_RUNS, [])
    add_sheet(wb, "探索の検索式", "レビューを狙った探索｜検索式・日時・件数",
              "無料の学術 API（メールアドレス・鍵なし）。条件: AI の語 × 疲労の語 ×（レビューの語 または 種別がレビュー）・2020-01-01 以降。",
              ["API", "検索式（逐語）", "実行日時", "総数", "取得", "条件を通った", "打ち切り", "エラー"],
              [[x["api"], x["query"], x["executed_at"], x.get("total_hits"), x.get("fetched"), x.get("passed_filter"),
                "はい" if x.get("truncated") else "いいえ", x.get("error")] for x in runs])
    recs = load_json(C.SEARCH_RECORDS, [])
    add_sheet(wb, "探索の一覧", "レビューを狙った探索｜条件を通った記録（すべて・抄録は載せない）",
              "重なり = 研究者の DB（DB34）・追加候補（C220）・寄せた記録（MERGED）。層（題名だけを見る機械の規則）: A1 = 題名に AI の語（狭い）・疲労の語・"
              "レビューの語が全部ある／B1 = AI の語が広い方（machine learning・automation など）で同じ／A2・B2 = 題名にレビューの語は無いが OpenAlex か Europe PMC の種別がレビュー／"
              "A3・B3 = 種別がレビューなのは Semantic Scholar だけ／C = 題名に疲労とレビューの語だけ／D = その他。読む一覧 = 新規性の確認で本文を読んだ番号（R01〜）"
              "か読まない理由（題名の語の規則）。足した = 判定者 1 が候補に足したか（読む一覧の 43 件は、判定者 1 の作業量の都合でこのファイルでは足していない）。",
              ["key", "題名", "年", "種別（API）", "掲載", "言語", "無料の版", "重なり", "見つかった API", "層", "読む一覧", "足した（ID）"],
              [[x["key"], x["title"], x.get("year"), x.get("type"), x.get("venue"), x.get("language"), x.get("oa"),
                x.get("overlap"), x.get("sources"), x.get("layer"), x.get("reading"), x.get("added_as") or "いいえ"] for x in recs])
    qa = [[PREV_WORK, r.get("seq"), r["item"], r["stage"], r["question"], " ／ ".join(r.get("options") or []), r["answer"], r.get("note", "")]
          for r in prev_log]
    qa += [[THIS_WORK, r["seq"], r["item"], r["stage"],
            f"【{r['item']}・{'題名・抄録段' if r['stage'] == 'ta1' else '除外理由'}】（問いの逐語は抄録の訳・要約を含むので載せない。"
            f"判定者 1 の手元の記録と SHA-256 {r['question_sha256'][:16]}… で結ぶ）",
            " ／ ".join(r["options"]), r["answer"], r["note"]] for r in this_log if r["stage"] in ("ta1", "ta1e")]
    add_sheet(wb, "問いと答え", "判定者 1 の問いと答え｜作業記録の写し（1 行 1 問）",
              "段: 1 = 全文段の 1 回目（AI の判定を見ない）・1e = 除外の理由・2 = 2 回目（AI の判定を見た）・q = 品質評価の確定・x = 抽出の確定／"
              "ta1 = 題名・抄録段（判定者 1・AI の判定を見ない）・ta1e = その除外理由。AI の予備判定は問いではないのでここに載せない（『スクリーニング』の T〜V 列）。",
              LOG_HEADER, qa, {5: 60})
    wb.save(dst)


def last_record():
    """Downloads の表と比べる SHA-256: 本タスクの記録。無い初回は前のタスクの記録（v1 の表）。"""
    for p in (C.CAND_SHA_RECORD, PREV_CAND_SHA_RECORD):
        if os.path.exists(p):
            return open(p, encoding="utf-8").read().strip(), p == C.CAND_SHA_RECORD
    return None, False


def main(dry):
    for p, s in ((C.JUDGE_FILE, C.JUDGE_FILE_SHA256), (C.APPRAISAL, C.APPRAISAL_SHA256)):
        if C.sha256(p) != s:
            sys.exit(f"元の資料の SHA-256 が違う: {p}")
    if dry:
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", prefix="cand-dry-")
        os.close(fd)
        build(tmp)
        print("dry-run ok（repo の外）", tmp)
        return
    last, own = last_record()
    # ★ archive は本タスクの記録とだけ比べる（初回は無いはず）。Downloads は初回だけ前のタスクの記録と比べる
    checks = ((C.CAND_ARCHIVE, last if own else None), (C.CAND_DOWNLOADS, last))
    for p, want in checks:
        if os.path.exists(p) and C.sha256(p) != want:
            sys.exit(f"表が最後に書いたものと違う（手で記入された可能性・止まって聞く）: {p}")
        if not os.path.exists(p) and want is not None:
            sys.exit(f"記録があるのに表が無い（止まって聞く）: {p}")
    os.makedirs(os.path.dirname(C.CAND_ARCHIVE), exist_ok=True)
    tmps, bak = [], None
    try:
        fd, tmp_a = tempfile.mkstemp(suffix=".part", dir=os.path.dirname(C.CAND_ARCHIVE), prefix=".tmp-")
        os.close(fd)
        tmps.append(tmp_a)
        build(tmp_a)
        fd, tmp_d = tempfile.mkstemp(suffix=".part", dir=C.DOWNLOADS, prefix=".tmp-cand-")
        os.close(fd)
        tmps.append(tmp_d)
        shutil.copyfile(tmp_a, tmp_d)
        for p, want in checks:  # ★ 置き換えの直前にもう一度
            if (os.path.exists(p) and C.sha256(p) != want) or (not os.path.exists(p) and want is not None):
                sys.exit(f"表が最後に書いたものと違う・無い（止まって聞く）: {p}")
        if os.path.exists(C.CAND_DOWNLOADS):
            fd, bak = tempfile.mkstemp(suffix=".part", prefix="cand-bak-")
            os.close(fd)
            shutil.copyfile(C.CAND_DOWNLOADS, bak)
        os.replace(tmp_d, C.CAND_DOWNLOADS)
        try:
            os.replace(tmp_a, C.CAND_ARCHIVE)
        except OSError:
            if bak:
                shutil.copyfile(bak, C.CAND_DOWNLOADS)
            else:
                os.remove(C.CAND_DOWNLOADS)
            raise
    finally:
        for t in tmps:
            if os.path.exists(t):
                os.remove(t)
    new = C.sha256(C.CAND_ARCHIVE)
    if C.sha256(C.CAND_DOWNLOADS) != new:
        sys.exit("archive と Downloads の表が合わない")
    with open(C.CAND_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write(new + "\n")
    if bak and os.path.exists(bak):
        os.remove(bak)
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
