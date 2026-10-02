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
(10) 答えの逐語と判定（result）が合う（答えの文だけから期待を読む・読めない答えは赤）。一次研究でない件を含めたら赤（規則が未実装）。
(11) 『判定者1_全文抽出』の ID = 抽出を確定した件（重複なし）・中身は data/extract-rows.json と同じ（--final では必須）。
(12) 『AI判定比較』は 34 件すべての 2 回目の後に記入する。足したシートと入力欄に式のセルが無い。
(13) 理由の問いの復元（reason-questions-restored.jsonl）: 答えがログの同じ seq の note と一致し、note に答えのある行はどれも復元を持つ。
     『判定者1_理由の問い』は復元と 1 行ずつ一致する（--final では必須）。『はじめに』の「判定者 2 に渡すとき」が戻す列を名指しする。
--selftest: 既知の答えの検算と、変異（入力欄の外のセル・判定者2・ログと写しのずれ・推奨の印・余分なシート・確認の結果・問いと答え・
    品質評価のシート・H と I・答えと判定・全文抽出・理由の問い・式・2 回目の前の記入）がそれぞれ赤になること。
    禁止語の規則と答えの読み方の単体の検査と、--final の対照つきの検査。
使い方: python check_workbook.py [--final] [--selftest]
"""
import copy
import json
import os
import re
import sys
import tempfile
import unicodedata

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
# ★ 2026-10-02 の 2 巡目で語の間を広げた（ChatGPT・LLM・AI の後に「の／による／が」と 4 字までを挟む）・全角は NFKC で寄せる（判断 13）
STAGE1_BANNED = re.compile(r"recommend|推奨|おすすめ|勧め|(AI|LLM)\s*(の|による|が)?\s*\S{0,4}?(判定|評価|判断|2\s*版)|適格性評価|"
                           r"(?<!Chat)GPT|ChatGPT\s*(の|による)?\s*(版|判定|評価|見立て)|Claude|中心候補", re.I)
# ★ 文献の中身として問いに載せた句（AI の推奨ではない）。件と逐語の句を対で限り、問いの文だけに効かせる（判断 9・12・13）
STAGE1_EXEMPT = {
    "AF031": ["（公開・登録を勧める）"],
    "AF032": ["選別は 2 名が独立に行うのが一般に推奨"],
}


def _nfkc(s):
    return unicodedata.normalize("NFKC", s or "")


def stage1_banned(item, question, options):
    if not isinstance(options, list):
        return re.search(".", "選択肢が list でない")  # ★ 文字列だと 1 字ずつに割れて禁止語が素通りする
    q = _nfkc(question)
    for p in STAGE1_EXEMPT.get(item, []):
        q = q.replace(_nfkc(p), "\n")  # ★ 空文字で消すと前後がつながる（「Chat…GPT」が ChatGPT になる）
    t = q + "\n" + "\n".join(_nfkc(o) for o in options)  # ★ 問いの末尾と選択肢の先頭がつながらない
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


# ★ 答えの逐語 → 期待の判定（Codex の指摘・判断 14）。result を見ずに答えの文だけから読む（書き込み側の表とは別に持つ）
VERDICT_WORDS = ("含める", "除外", "保留")


def answer_mismatch(stage, answer, res, first_res):
    """答えの文と判定（result）が合わなければ理由の文を返す（合えば None）。first_res = その件の 1 回目（1・1e）の result。"""
    a = _nfkc(answer).strip()
    if "一次研究として読む" in a:
        return "『含める（一次研究として読む）』の規則は未実装（用途・品質評価が決まっていない）"
    if stage == "1e":
        if not re.fullmatch(r"E[1-7]", a):
            return f"除外のコードの答え {answer!r} を読めない"
        want = ("除外", None, a)
    else:
        body = a.replace("(E4 以外)", "")  # ★ NFKC で全角の括弧は半角になる。「E4 以外」はコードではない
        words = [v for v in VERDICT_WORDS if v in body]
        m_use, m_e = re.search(r"中心-([AB])", body), re.search(r"E[1-7]", body)
        use, ecode = (f"中心-{m_use.group(1)}" if m_use else None), (m_e.group(0) if m_e else None)
        if len(words) > 1:
            return f"答え {answer!r} に判定の語が 2 つある"
        verdict = words[0] if words else ("含める" if use else ("除外" if ecode else None))
        if a.startswith("1 回目のまま"):
            if first_res is None:
                return "「1 回目のまま」なのに 1 回目が無い"
            if verdict is None:  # 括弧の無い「1 回目のまま」→ 1 回目の判定
                want = (first_res.get("verdict"), first_res.get("use"), first_res.get("ecode"))
            elif verdict != first_res.get("verdict") or (use and use != first_res.get("use")):
                return f"答え {answer!r} が 1 回目の判定 {first_res.get('verdict')!r} と食い違う"
            else:
                want = (verdict, use, ecode)
        elif verdict is None:
            return f"答え {answer!r} を読めない（Other の自由記入は判定を確かめて読み方を足す）"
        else:
            want = (verdict, use, ecode)
    v, use, ecode = want
    if res.get("verdict") != v:
        return f"答えは {v!r}・判定は {res.get('verdict')!r}"
    if v == "含める" and (use is None or res.get("use") != use):
        return f"答えの中心 {use!r}・判定の中心 {res.get('use')!r}"
    if v == "除外" and res.get("ecode") != ecode:
        return f"答えのコード {ecode!r}・判定のコード {res.get('ecode')!r}"
    if v == "保留" and res.get("ecode") not in ((ecode,) if ecode else (None, "E6")):
        return f"保留のコード {res.get('ecode')!r} が答え {answer!r} と合わない"
    return None


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
# ★ 2 回目の前後に Claude の見立て・計算を判定者 1 が見た件（ログの note・decisions 判断 4。書き込み側の CLAUDE_SHOWN とは別に持つ）
EXPECT_CLAUDE_SHOWN = {"AF002", "AF003", "AF004"}
EXTRACT_SHEET = C.ADDED_PREFIX + "全文抽出"
EXTRACT_DATA = os.path.join(C.TASK, "data", "extract-rows.json")
REASON_SHEET = C.ADDED_PREFIX + "理由の問い"
REASON_HEADER = ["seq（答えのログ）", "ID", "問い（逐語）", "選択肢", "複数選択", "答え", "補足（note）", "答えた時刻"]
REASONS = os.path.join(C.TASK, "reason-questions-restored.jsonl")
REASON_ANSWERED = re.compile(r"理由の問い[^。]*の答え: ")
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
        want = [rec.get("seq"), rec.get("item"), rec.get("stage"), rec.get("question"),
                " ／ ".join(rec.get("options") or []), rec.get("answer"), rec.get("note") or ""]
        if [x[0], x[1], x[2], x[3], x[4] or "", x[5], x[6] or ""] != want:  # ★ 選択肢と補足（Claude の関与の開示）も見る
            errs.append(f"{LOG_SHEET}!A{n}: ログの seq {rec.get('seq')} と一致しない")
    return errs


def sheet_rows(ws, ncol):
    rows = [[ws.cell(r, c).value for c in range(1, ncol + 1)] for r in range(5, ws.max_row + 1)]
    return [x for x in rows if any(v not in (None, "") for v in x)]


def check_extract_sheet(w, xitems, final, data_path=None):
    """『判定者1_全文抽出』: ID = 抽出を確定した件（重複なし）・中身は data の行と同じ（--final では必須）。"""
    if EXTRACT_SHEET not in w.sheetnames:
        return [f"{EXTRACT_SHEET} が無い（抽出を確定した件 {len(xitems)} があるのに・--final）"] if final and xitems else []
    ws = w[EXTRACT_SHEET]
    if ws.cell(4, 1).value != "ID":
        return [f"{EXTRACT_SHEET}: 見出しの A 列が ID でない"]
    ncol = ws.max_column
    rows = sheet_rows(ws, ncol)
    ids = [x[0] for x in rows]
    errs = []
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errs.append(f"{EXTRACT_SHEET}: ID が重複 {dup}")
    if set(ids) != set(xitems):
        errs.append(f"{EXTRACT_SHEET}: ID が抽出を確定した件と違う（多い {sorted(set(ids) - set(xitems))}・無い {sorted(set(xitems) - set(ids))}）")
    if data_path and os.path.exists(data_path):
        d = json.load(open(data_path, encoding="utf-8"))
        hdr = [ws.cell(4, c).value for c in range(1, ncol + 1)]

        def norm(row):
            return [None if v in (None, "") else v for v in row] + [None] * (ncol - len(row))
        if norm(d["header"]) != norm(hdr) or [norm(x) for x in d["rows"]] != [norm(x) for x in rows]:
            errs.append(f"{EXTRACT_SHEET}: 中身が data/extract-rows.json と違う")
    return errs


def check_reasons(w, log, reasons_path, final):
    """理由の問いの復元: 答え = ログの同じ seq の note の答え・note に答えのある行はどれも復元を持つ・シートは復元と 1 行ずつ一致。"""
    if reasons_path is None:
        return []
    recs = read_log(reasons_path)
    by_seq = {r.get("seq"): r for r in log}
    answered = {r.get("seq") for r in log if r.get("stage") in ("2", "2e") and REASON_ANSWERED.search(r.get("note") or "")}
    errs, got = [], set()
    for x in recs:
        r, sq = by_seq.get(x.get("log_seq")), x.get("log_seq")
        if not r or r.get("item") != x.get("item") or r.get("stage") not in ("2", "2e"):
            errs.append(f"理由の問い {x.get('item')}: ログの seq {sq} が同じ件の 2 回目でない")
            continue
        if not x.get("answer") or ("の答え: " + x["answer"]) not in (r.get("note") or ""):
            errs.append(f"理由の問い {x.get('item')}: 答え {x.get('answer')!r} がログの seq {sq} の note と合わない")
        if "理由はどれに近いですか" not in (x.get("question") or "") or not isinstance(x.get("options"), list):
            errs.append(f"理由の問い {x.get('item')}: 問いの文・選択肢の形が違う")
        if sq in got:
            errs.append(f"理由の問い: seq {sq} が重複")
        got.add(sq)
    if answered - got:
        errs.append(f"理由の問い: note に答えがあるのに復元が無い seq {sorted(answered - got)}")
    if REASON_SHEET not in w.sheetnames:
        return errs + ([f"{REASON_SHEET} が無い（復元 {len(recs)} 件があるのに・--final）"] if final and recs else [])
    ws = w[REASON_SHEET]
    if [ws.cell(4, c).value for c in range(1, len(REASON_HEADER) + 1)] != REASON_HEADER:
        return errs + [f"{REASON_SHEET}: 見出しが違う"]
    rows = sheet_rows(ws, len(REASON_HEADER))
    want = [[x.get("log_seq"), x.get("item"), x.get("question"), " ／ ".join(x.get("options") or []),
             "可" if x.get("multiSelect") else "不可", x.get("answer"), x.get("user_note") or ""] for x in recs]
    if [[x[0], x[1], x[2], x[3], x[4], x[5], x[6] or ""] for x in rows] != want:
        errs.append(f"{REASON_SHEET}: 復元（reason-questions-restored.jsonl）と 1 行ずつ一致しない（{len(rows)} 行・復元 {len(recs)} 件）")
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


def check(copy_path, log_path, final=False, original=C.ORIGINAL, reasons_path=None, extract_path=None):
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
    seen1, seen2, final_res, qrec, xitems, first_res = {}, {}, {}, {}, set(), {}
    for n, rec in enumerate(log, 1):
        i, st = rec.get("item"), rec.get("stage")
        if i not in kind:
            errs.append(f"ログ {n}: 知らない件 {i}")
            continue
        if st in ("1", "1e", "2", "2e"):  # (10) 答えの逐語と判定（result）
            why = answer_mismatch(st, rec.get("answer"), rec.get("result") or {}, first_res.get(i))
            if why:
                errs.append(f"ログ {n} {i}: 答えと判定が合わない（{why}）")
            if st in ("1", "1e"):
                first_res[i] = rec.get("result") or {}
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
        if res["verdict"] == "含める" and kind[i] not in PRIMARY:  # ★ 規則が未実装（判断 14）
            errs.append(f"{i}: 一次研究でない件を含めた（『一次研究として読む』の規則は未実装）")
        if res.get("basis") == "抄録" and scr[f"H{r}"].value != "入手不可":
            errs.append(f"{i}: 材料が抄録なのに全文確認={scr[f'H{r}'].value!r}")
        # 全文確認（H）・品質評価（I）を、ログの x（抽出の確定）と q（品質の確定）から独立に計算する（design §2.1）
        want_h = "入手不可" if res.get("basis") == "抄録" else ("完了" if i in xitems else "進行中")
        if scr[f"H{r}"].value != want_h:
            errs.append(f"{i}: 全文確認={scr[f'H{r}'].value!r} がログからの期待 {want_h!r} と違う")
        # ★ design §2.1 の順に書き起こす: 含める一次研究で抄録だけ → 進行中（q の有無によらない）／q で確定 → 完了／
        #   q が無い → 未実施（まだ聞いていない）／q で保留 → 進行中。保留の件は 未実施（§2.1 に無い規則・判断 13 で決めた）
        if res["verdict"] == "含める" and kind[i] in PRIMARY:
            q = qrec.get(i)
            if res.get("basis") == "抄録":
                want_i = "進行中"
            elif q is None:
                want_i = "未実施"
            elif str(q.get("answer", "")).startswith("保留"):
                want_i = "進行中"
            else:
                want_i = "完了"
        elif res["verdict"] == "保留":
            want_i = "未実施"
        else:
            want_i = "対象外"
        if iv != want_i:
            errs.append(f"{i}: 品質評価={iv!r} がログからの期待 {want_i!r} と違う")
        jv = scr[f"J{r}"].value or ""
        if not jv.startswith("用途: "):
            errs.append(f"{i}: 自由記入が規則の形でない")
        # ★ Claude の見立て・計算を判定者 1 が見た件（検査器が独立に持つ・判断 12・13）だけが「Claude の関与」を持つ
        if ("Claude の関与" in jv) != (i in EXPECT_CLAUDE_SHOWN):
            errs.append(f"{i}: 自由記入の「Claude の関与」の有無が期待（{sorted(EXPECT_CLAUDE_SHOWN)} だけ）と違う")
        hu = cmp_[f"D{r}"].value
        if hu is not None and hu != expect_human(res, kind[i]):
            errs.append(f"{i}: 人間用途判定 {hu!r} が期待 {expect_human(res, kind[i])!r} と違う")
    # (6) 『判定者1_確認の結果』（あれば常に・--final では必須）
    errs += check_checks_sheet(w, final, o)
    # (7) 『判定者1_問いと答え』（研究者が読めるログの写し）: ログと 1 行ずつ一致する
    errs += check_log_sheet(w, log, final)
    # (8) 『判定者1_品質評価』の ID = 含めた一次研究で品質を確定（q）した件
    want_q = {i for i in qrec if i in final_res and final_res[i]["verdict"] == "含める" and kind[i] in PRIMARY}
    if QUALITY_SHEET in w.sheetnames:
        ws = w[QUALITY_SHEET]
        got = {ws.cell(rr, 1).value for rr in range(5, ws.max_row + 1)} - {None}
        if got != want_q:
            errs.append(f"{QUALITY_SHEET}: ID {sorted(got)} が品質を確定した含める一次研究 {sorted(want_q)} と違う")
    elif final and want_q:
        errs.append(f"{QUALITY_SHEET} が無い（品質を確定した件 {len(want_q)} があるのに・--final）")
    # (11) 『判定者1_全文抽出』
    errs += check_extract_sheet(w, xitems, final, extract_path)
    # (12) 『AI判定比較』は 34 件すべての 2 回目の後（1 回目だけの件があるうちは空）
    if not all(i in seen2 for i in C.IDS):
        early = [i for k, i in enumerate(C.IDS) if cmp_[f"D{C.FIRST_ROW + k}"].value is not None]
        if early:
            errs.append(f"『AI判定比較』が 34 件の 2 回目の前に記入されている: {early[:3]}")
    # (12) 式のセル（足したシートと入力欄）。★ 外の文の先頭の = が式になるのを防ぐ
    for s in w.sheetnames:
        if s.startswith(C.ADDED_PREFIX):
            cells = [c for row in w[s].iter_rows() for c in row]
        elif s in C.INPUT_COLS:
            cells = [w[s][f"{col}{r}"] for col in C.INPUT_COLS[s] for r in range(C.FIRST_ROW, C.FIRST_ROW + 34)]
        else:
            continue
        errs += [f"式のセル: {s}!{c.coordinate}" for c in cells if c.data_type == "f"]
    # (13) 理由の問いの復元と『判定者1_理由の問い』
    errs += check_reasons(w, log, reasons_path, final)
    # (9) 『判定者1_はじめに』に研究者への注意がある（判定者 2 に渡さない・Claude の関与）。★ 見出し（A 列）だけでなく説明（B 列）を見る
    if final:
        intro = {}
        if INTRO_SHEET in w.sheetnames:
            for row in w[INTRO_SHEET].iter_rows(min_row=5, values_only=True):
                if row and row[0]:
                    intro[str(row[0])] = str(row[1] or "")
        body = " ".join(intro.values())
        if "判定者 2 に渡さない" not in body:
            errs.append(f"{INTRO_SHEET}: 「判定者 2 に渡さない」の行が無い（--final）")
        hand = intro.get("判定者 2 に渡すとき", "")
        for s_, cols in C.INPUT_COLS.items():  # ★ 戻す列を名指しする（「判定者1 の列」だけでは G〜J・『AI判定比較』が残る・判断 14）
            if f"『{s_}』の {'・'.join(cols)} 列" not in hand:
                errs.append(f"{INTRO_SHEET}: 「判定者 2 に渡すとき」に『{s_}』の {'・'.join(cols)} 列が無い（--final）")
        claude_row = intro.get("Claude の関与", "")
        if not claude_row or any(i not in claude_row for i in EXPECT_CLAUDE_SHOWN):
            errs.append(f"{INTRO_SHEET}: 「Claude の関与」の行の説明に {sorted(EXPECT_CLAUDE_SHOWN)} が無い（--final）")
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
    # ★ 含める一次研究の件（AF001・中心-A・全文・品質を確定）も基準に入れる（品質評価の分岐を赤で見るため・判断 13）
    res_a = {"verdict": "含める", "use": "中心-A", "basis": "全文", "date": "2026-10-01"}
    recA1 = {"item": "AF001", "stage": "1", "question": "AF001 の判定（事実のみ）", "options": STAGE1_OPTIONS["primary"],
             "answer": STAGE1_OPTIONS["primary"][0], "result": res_a}
    recA2 = dict(recA1, stage="2", question="AI の判定を見て", options=["1 回目のまま", "変える"], answer="1 回目のまま")
    recAq = {"item": "AF001", "stage": "q", "question": "品質評価の確定", "options": ["下書きどおり確定 (Recommended)", "直す", "保留（判定不能のまま）"],
             "answer": "下書きどおり確定 (Recommended)", "result": {"answer": "確定"}}
    recx = {"item": "AF030", "stage": "x", "question": "抽出の確定", "options": ["確定"], "answer": "確定",
            "result": {"items": ["AF030", "AF001"]}}
    with open(base_log, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in (rec1, rec2, recA1, recA2, recAq, recx))
    wb = openpyxl.load_workbook(C.ORIGINAL)
    r = C.FIRST_ROW + C.IDS.index("AF030")
    wb["スクリーニング"][f"D{r}"] = "除外"
    wb["スクリーニング"][f"G{r}"] = "E4 方法論"
    wb["スクリーニング"][f"H{r}"] = "完了"
    wb["スクリーニング"][f"I{r}"] = "対象外"
    wb["スクリーニング"][f"J{r}"] = "用途: 方法論保持 ／ 1回目: 除外 E4 → 最終: 除外 E4"
    rA = C.FIRST_ROW + C.IDS.index("AF001")
    wb["スクリーニング"][f"D{rA}"] = "含める"
    wb["スクリーニング"][f"H{rA}"] = "完了"
    wb["スクリーニング"][f"I{rA}"] = "完了"
    wb["スクリーニング"][f"J{rA}"] = "用途: 中心-A ／ 1回目: 含める（中心-A） → 最終: 含める（中心-A）"
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
    # 禁止語の規則（判断 12・13）: 除外は件と逐語の句の対だけ・問いの文だけに効く。区切りで境目を跨がない。1e にも効く。大文字小文字・全角を区別しない
    o_other = STAGE1_OPTIONS["other"]
    unit = [
        ("AF032 の句を問いと選択肢に割る → 赤", stage1_banned("AF032", "選別は 2 名が独立に行うのが一般に", ["推奨: 除外"] + o_other[1:]), True),
        ("AF032 の句が選択肢にあるだけ → 赤（除外は問いの文だけ）", stage1_banned("AF032", "事実", ["選別は 2 名が独立に行うのが一般に推奨"]), True),
        ("除外の句を消して前後がつながる → 赤", stage1_banned("AF031", "Chat（公開・登録を勧める）GPT は除外", o_other), True),
        ("選択肢が文字列 → 赤", stage1_banned("AF030", "事実", "推奨"), True),
        ("全角の ＧＰＴ → 赤", stage1_banned("AF030", "ＧＰＴ版", o_other), True),
        ("全角の Ｃｌａｕｄｅ → 赤", stage1_banned("AF030", "Ｃｌａｕｄｅ版", o_other), True),
        ("ChatGPT の判定 → 赤", stage1_banned("AF030", "ChatGPT の判定は", o_other), True),
        ("ChatGPT による評価 → 赤", stage1_banned("AF030", "ChatGPT による評価", o_other), True),
        ("AI の用途判定 → 赤", stage1_banned("AF030", "AI の用途判定", o_other), True),
        ("AI による判定 → 赤", stage1_banned("AF030", "AI による判定", o_other), True),
        ("AI の判断 → 赤", stage1_banned("AF030", "AI の判断", o_other), True),
        ("LLM の判定 → 赤", stage1_banned("AF030", "LLM の判定", o_other), True),
        ("AI の利用（事実の語）→ 緑", stage1_banned("AF030", "AI の利用と疲労", o_other), False),
        ("AI 疲労の尺度の評価（事実の語）→ 緑", stage1_banned("AF030", "AI 疲労の尺度の評価", o_other), False),
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

    def mutate_named(name, must, fn_wb=None, fn_log=None, final=False):
        """★ 変異が「その規則で」赤になることを、エラーの文言で名指しして見る（別の理由の赤で通らない）。"""
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
        es = check(cp, lg, final=final)
        hit = [e for e in es if must in e]
        if not hit:
            print("FAIL 変異が名指しの規則で赤にならない:", name, "| 期待:", must, "| 実際:", es[:2])
            bad += 1
        else:
            print(f"  赤 {name}: {hit[0]}")

    mutate_named("checks-kakunin-swap", "確認事項",
                 fn_wb=lambda w: add_checks(w, lambda ws: (ws.cell(5, 2, "AF006–AF009"), ws.cell(6, 2, "AF004 / AF034"))))
    # 全文確認・品質評価をログ（x・q）から独立に計算する
    mutate_named("fulltext-not-logged", "AF030: 全文確認='完了' がログからの期待 '進行中'",
                 fn_log=lambda L: [x for x in L if x["stage"] != "x"])
    mutate_named("quality-done-no-q", "AF001: 品質評価='完了' がログからの期待 '未実施'",
                 fn_log=lambda L: [x for x in L if x["stage"] != "q"])
    mutate_named("quality-done-q-hold", "AF001: 品質評価='完了' がログからの期待 '進行中'",
                 fn_log=lambda L: [dict(x, answer="保留（判定不能のまま）", result={"answer": "保留"}) if x["stage"] == "q" else x for x in L])
    mutate_named("quality-sheet-extra-id", "判定者1_品質評価: ID",
                 fn_wb=lambda w: (lambda ws: (ws.cell(4, 1, "ID"), ws.cell(5, 1, "AF002")))(w.create_sheet(QUALITY_SHEET)))
    mutate_named("quality-sheet-missing-final", "判定者1_品質評価 が無い", final=True)
    mutate_named("claude-shown-not-expected", "「Claude の関与」の有無",
                 fn_wb=lambda w: w["スクリーニング"].cell(r, 10, "用途: 方法論保持 ／ Claude の関与: 見立て"))
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
    mutate_named("logsheet-note-diff", "判定者1_問いと答え", fn_wb=lambda w: add_log_sheet(w, lambda ws: ws.cell(6, 7, "Claude の見立てを見た")))
    mutate_named("logsheet-options-diff", "判定者1_問いと答え", fn_wb=lambda w: add_log_sheet(w, lambda ws: ws.cell(5, 5, "別の選択肢")))
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
            for rr, (k, v) in enumerate(rows, 5):
                ws.cell(rr, 1, k)
                ws.cell(rr, 2, v)
        return f
    good = [("判定者 2 に渡すとき", "この写しは判定者 2 に渡さない。『スクリーニング』の D・G・H・I・J 列と『AI判定比較』の D・F・G 列を戻す"),
            ("Claude の関与", "AF002・AF003 の見立て・AF004 の再計算")]
    if any(INTRO_SHEET in e for e in final_errs(fn_wb=intro_with(good))):
        print("FAIL 対照: 『はじめに』に注意があるのに赤", [e for e in final_errs(fn_wb=intro_with(good)) if INTRO_SHEET in e])
        bad += 1
    for nm, rows_, must in (("判定者 2 の注意が無い", good[1:], "「判定者 2 に渡さない」"),
                            ("Claude の関与が見出しだけ", [good[0], ("Claude の関与", "")], "「Claude の関与」"),
                            ("Claude の関与に AF004 が無い", [good[0], ("Claude の関与", "AF002・AF003 の見立て")], "「Claude の関与」"),
                            ("戻す列が D だけ", [("判定者 2 に渡すとき", "この写しは判定者 2 に渡さない。『スクリーニング』の D 列"), good[1]],
                             "『スクリーニング』の D・G・H・I・J 列が無い"),
                            ("『AI判定比較』の列が無い", [("判定者 2 に渡すとき", "この写しは判定者 2 に渡さない。『スクリーニング』の D・G・H・I・J 列"),
                                                     good[1]], "『AI判定比較』の D・F・G 列が無い")):
        if not any(must in e for e in final_errs(fn_wb=intro_with(rows_))):
            print("FAIL 『はじめに』の変異が --final で赤にならない:", nm)
            bad += 1
    mutate("stage2-first", fn_log=lambda L: list(reversed(L)))
    mutate("extra-sheet", fn_wb=lambda w: w.create_sheet("メモ"))
    mutate("human-use-wrong", fn_wb=lambda w: w["AI判定比較"].cell(r, 4, "背景保持"))
    mutate("unlogged-verdict", fn_wb=lambda w: w["スクリーニング"].cell(C.FIRST_ROW + 1, 4, "含める"))  # AF002（基準のログに無い件）

    # ---- 2026-10-02 Codex の指摘への対応（判断 14） ----
    # (10) 答えの読み方: 実データの答えの形（陰性対照）と、答え・判定の片方だけをずらした形
    f_hold, f_e2, f_b = {"verdict": "保留"}, {"verdict": "除外", "ecode": "E2"}, {"verdict": "含める", "use": "中心-B"}
    ans_unit = [
        ("保留 → 緑", "1", "保留", {"verdict": "保留"}, None, False),
        ("含める（中心-B）→ 緑", "1", "含める（中心-B）", f_b, None, False),
        ("除外（E4 以外）でコード無し → 緑", "1", "除外（E4 以外）", {"verdict": "除外"}, None, False),
        ("除外（E4 以外）なのに E4 → 赤", "1", "除外（E4 以外）", {"verdict": "除外", "ecode": "E4"}, None, True),
        ("除外 E4（保持の区分は対応表で決まる）→ 緑", "1", STAGE1_OPTIONS["other"][1], {"verdict": "除外", "ecode": "E4"}, None, False),
        ("1e の E2 → 緑", "1e", "E2", f_e2, {"verdict": "除外"}, False),
        ("1e の答え E2・判定 E3 → 赤", "1e", "E2", {"verdict": "除外", "ecode": "E3"}, {"verdict": "除外"}, True),
        ("1 回目のまま（保留・E6）→ 緑", "2", "1 回目のまま（保留・E6）", {"verdict": "保留", "ecode": "E6"}, f_hold, False),
        ("1 回目のまま（保留）で E6 → 緑（E6 は理由の問いの答え）", "2", "1 回目のまま（保留）", {"verdict": "保留", "ecode": "E6"}, f_hold, False),
        ("1 回目のまま（保留・E6）でコード無し → 赤", "2", "1 回目のまま（保留・E6）", {"verdict": "保留"}, f_hold, True),
        ("保留に E2 → 赤", "2", "1 回目のまま（保留）", {"verdict": "保留", "ecode": "E2"}, f_hold, True),
        ("括弧の無い 1 回目のまま → 緑", "2", "1 回目のまま", dict(f_e2), f_e2, False),
        ("括弧の無い 1 回目のまま・判定が違う → 赤", "2", "1 回目のまま", {"verdict": "除外", "ecode": "E4"}, f_e2, True),
        ("1 回目のまま（除外 E2）だが 1 回目は保留 → 赤", "2", "1 回目のまま（除外 E2）", f_e2, f_hold, True),
        ("AI の判定（除外 E4・背景保持）に変える → 緑", "2", "AI の判定（除外 E4・背景保持）に変える", {"verdict": "除外", "ecode": "E4"}, f_hold, False),
        ("AI の判定（含める・中心-A）に変える → 緑", "2", "AI の判定（含める・中心-A）に変える", {"verdict": "含める", "use": "中心-A"}, f_hold, False),
        ("Claude 版（中心-A）に変える → 緑", "2", "Claude 版（中心-A）に変える", {"verdict": "含める", "use": "中心-A"}, f_b, False),
        ("Claude 版（中心-A）・判定は中心-B → 赤", "2", "Claude 版（中心-A）に変える", f_b, f_b, True),
        ("中心-B のまま → 緑", "2", "中心-B のまま", f_b, f_hold, False),
        ("別の判定に変える（Other）→ 赤", "2", "別の判定に変える", {"verdict": "保留"}, f_hold, True),
        ("一次研究として読む → 赤", "1", STAGE1_OPTIONS["other"][0], {"verdict": "含める", "use": "中心-A"}, None, True),
        ("判定の語が 2 つ → 赤", "2", "含めるか除外", {"verdict": "含める", "use": "中心-A"}, f_hold, True),
        ("1 回目が無いのに 1 回目のまま → 赤", "2", "1 回目のまま", {"verdict": "保留"}, None, True),
        ("全角の Ａ の含める（中心-Ａ）→ 緑", "1", "含める（中心-Ａ）", {"verdict": "含める", "use": "中心-A"}, None, False),
    ]
    for name, st_, ans, res_, first_, want_red in ans_unit:
        if bool(answer_mismatch(st_, ans, res_, first_)) != want_red:
            print("FAIL 答えの読み方:", name, answer_mismatch(st_, ans, res_, first_))
            bad += 1
    mutate_named("answer-only-diff", "AF030: 答えと判定が合わない",
                 fn_log=lambda L: [dict(x, answer="保留") if (x["item"], x["stage"]) == ("AF030", "1") else x for x in L])
    mutate_named("result-only-diff", "AF030: 答えと判定が合わない",
                 fn_log=lambda L: [dict(x, result={"verdict": "保留", "basis": "全文"}) if (x["item"], x["stage"]) == ("AF030", "2") else x
                                   for x in L])
    mutate_named("read-as-primary", "AF030: 一次研究でない件を含めた",
                 fn_log=lambda L: [dict(x, answer=STAGE1_OPTIONS["other"][0] if x["stage"] == "1" else x["answer"],
                                        result={"verdict": "含める", "use": "中心-A", "basis": "全文"})
                                   if x["item"] == "AF030" and x["stage"] in ("1", "2") else x for x in L])
    # (12) 『AI判定比較』は 34 件の 2 回目の後: 期待どおりの値でも、2 回目の無い件があるうちは赤
    mutate_named("cmp-before-all-stage2", "34 件の 2 回目の前に記入", fn_wb=lambda w: w["AI判定比較"].cell(r, 4, "方法論保持"))
    # (12) 式のセル: 足したシートと入力欄の = は赤・書き込み側の put() で書いた = は文字列のまま（緑）
    mutate_named("formula-added-sheet", "式のセル: 判定者1_はじめに", fn_wb=lambda w: w[INTRO_SHEET].cell(10, 1, "=1+1"))
    mutate_named("formula-input-cell", f"式のセル: スクリーニング!J{r}", fn_wb=lambda w: w["スクリーニング"].cell(r, 10, "=A1"))
    w_put = openpyxl.load_workbook(base_copy)
    W.put(w_put[INTRO_SHEET].cell(10, 1), "=1+1")
    cp_put = os.path.join(tmpd, "put-string.xlsx")
    w_put.save(cp_put)
    if any("式のセル" in e for e in check(cp_put, base_log)) or openpyxl.load_workbook(cp_put)[INTRO_SHEET].cell(10, 1).value != "=1+1":
        print("FAIL 書き込み側の put() で書いた = が式になる・値が変わる")
        bad += 1
    # (11) 『判定者1_全文抽出』: 実の data で作ったシートは緑（34 件）・行の欠け・重複・中身のずれ・--final で無いは赤
    exd = json.load(open(EXTRACT_DATA, encoding="utf-8"))
    all_x = set(C.IDS)

    def ex_wb(edit=None, sheet=True):
        w2 = openpyxl.load_workbook(base_copy)
        if sheet:
            ws = w2.create_sheet(EXTRACT_SHEET)
            for c, h in enumerate(exd["header"], 1):
                ws.cell(4, c, h)
            for rr, row in enumerate(exd["rows"], 5):
                for c, v in enumerate(row, 1):
                    ws.cell(rr, c, v)
            if edit:
                edit(ws)
        return w2
    if check_extract_sheet(ex_wb(), all_x, True, EXTRACT_DATA):
        print("FAIL 対照: 実の全文抽出のシートで赤", check_extract_sheet(ex_wb(), all_x, True, EXTRACT_DATA)[:2])
        bad += 1
    # ★ check() からの呼び出しも見る（関数を直接呼ぶ変異だけだと、check() から外しても緑のまま・メタ変異で実測）
    mutate_named("extract-via-check", "判定者1_全文抽出: ID が抽出を確定した件と違う",
                 fn_wb=lambda w: (lambda ws: (ws.cell(4, 1, "ID"), ws.cell(5, 1, "AF002")))(w.create_sheet(EXTRACT_SHEET)))
    for nm, wb_, must in (("行が欠ける", ex_wb(lambda ws: ws.delete_rows(10)), "ID が抽出を確定した件と違う"),
                          ("ID が重複", ex_wb(lambda ws: ws.cell(10, 1, ws.cell(11, 1).value)), "ID が重複"),
                          ("中身がずれる", ex_wb(lambda ws: ws.cell(10, 3, "別の集団")), "中身が data/extract-rows.json と違う"),
                          ("--final で無い", ex_wb(sheet=False), "が無い")):
        es = check_extract_sheet(wb_, all_x, True, EXTRACT_DATA)
        if not any(must in e for e in es):
            print("FAIL 全文抽出の変異が赤にならない:", nm, es[:2])
            bad += 1
    # (13) 理由の問いの復元: 実のログと復元で作ったシートは緑・答えのずれ・行の欠け・シートのずれ・--final で無いは赤
    real_log = read_log(C.LOG)
    rq = read_log(REASONS)

    def rq_wb(recs, edit=None, sheet=True):
        w2 = openpyxl.load_workbook(base_copy)
        if sheet:
            ws = w2.create_sheet(REASON_SHEET)
            for c, h in enumerate(REASON_HEADER, 1):
                ws.cell(4, c, h)
            for rr, x in enumerate(recs, 5):
                for c, v in enumerate([x["log_seq"], x["item"], x["question"], " ／ ".join(x["options"]),
                                       "可" if x["multiSelect"] else "不可", x["answer"], x.get("user_note", ""), "t"], 1):
                    ws.cell(rr, c, v)
            if edit:
                edit(ws)
        return w2

    def rq_file(recs, name):
        pth = os.path.join(tmpd, name + ".jsonl")
        with open(pth, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in recs)
        return pth
    if len(rq) != 18 or check_reasons(rq_wb(rq), real_log, REASONS, True):
        print("FAIL 対照: 実の復元（18 件）とシートで赤", check_reasons(rq_wb(rq), real_log, REASONS, True)[:2])
        bad += 1
    if check_reasons(rq_wb(rq), real_log, None, True):
        print("FAIL 復元のパスが無いとき（selftest の既定）に赤")
        bad += 1
    # ★ check() からの呼び出しも見る: 基準のログに無い seq を指す復元は赤（check() から外すと緑になる）
    if not any("理由の問い" in e for e in check(base_copy, base_log, reasons_path=rq_file(rq[:1], "rq-via-check"))):
        print("FAIL check() に復元を渡しても理由の問いの検査が走らない")
        bad += 1
    bad_ans = [dict(x, answer="迷っていたので AI に寄せた") if k == 0 else x for k, x in enumerate(rq)]
    for nm, args, must in (("答えが note とずれる", (rq_wb(bad_ans), real_log, rq_file(bad_ans, "rq-ans"), True), "note と合わない"),
                           ("復元の行が欠ける", (rq_wb(rq[1:]), real_log, rq_file(rq[1:], "rq-miss"), True), "復元が無い"),
                           ("seq が別の件", (rq_wb(rq), real_log, rq_file([dict(rq[0], log_seq=rq[1]["log_seq"])] + rq[1:], "rq-seq"), True),
                            "同じ件の 2 回目でない"),
                           ("シートの選択肢がずれる", (rq_wb(rq, lambda ws: ws.cell(6, 4, "別の選択肢")), real_log, REASONS, True), "1 行ずつ一致しない"),
                           ("--final でシートが無い", (rq_wb(rq, sheet=False), real_log, REASONS, True), "が無い")):
        es = check_reasons(*args)
        if not any(must in e for e in es):
            print("FAIL 理由の問いの変異が赤にならない:", nm, es[:2])
            bad += 1
    print("selftest", "PASS" if bad == 0 else f"FAIL {bad}")
    return bad == 0


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    errs = check(C.COPY_ARCHIVE, C.LOG, final="--final" in argv, reasons_path=REASONS, extract_path=EXTRACT_DATA)
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
