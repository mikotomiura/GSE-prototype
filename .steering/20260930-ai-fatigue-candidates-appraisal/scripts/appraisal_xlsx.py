"""追加候補 225 件の AI（Claude）の評価版の xlsx を作る（design.md「評価版のシート」「値の語彙」）。

★ 候補の順・書誌・本文の入手は、判定者用ファイルと同じ関数（judge_xlsx.candidate_records）から作る。案は appraisal_data.py。
★ 判定者 1 が判定の前に読む。判定者 2 は開かない（判定者用ファイルの『はじめに』）。

使い方（uv で openpyxl を入れて実行する）:
  python appraisal_xlsx.py --out <出力 .xlsx> [--copy-to <ディレクトリ>] [--force]
"""
import argparse
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
JF_SCRIPTS = os.path.join(os.path.dirname(TASK), "20260930-ai-fatigue-judge-file", "scripts")
sys.path.insert(0, HERE)
sys.path.insert(0, JF_SCRIPTS)
import openpyxl  # noqa: E402
import judge_xlsx as J  # noqa: E402
import appraisal_data as D  # noqa: E402

OUT_NAME = "AI_fatigue_candidates_AI_appraisal_2026-09-30_claude.xlsx"

# ---------------------------------------------------------------- 語彙（design.md「値の語彙」）
TA = ("含める", "除外", "保留")
FT = ("含める", "除外", "保留", "未実施", "—")
FINAL = ("含める", "除外", "保留")
FULLTEXT = ("完了", "未完了", "入手不可", "入手不明", "対象外")
UNKNOWN_OA = ("DOI なし", "未確認", "未確認（取得できず）")  # OpenAlex の記録で本文の入手が分からないもの
LEVEL = ("題名のみ", "抄録", "本文関連箇所確認")
USE = {"中心-A": "中心候補", "中心-B": "中心候補", "中心（A/B 未確定）": "中心候補", "境界（保留）": "保留",
       "背景（E2）": "背景保持", "背景（E4）": "背景保持", "除外（E1）": "除外", "除外（E3）": "除外"}
CENTER = tuple(USE)
PK = {"1件": "1 件ずつの案", "種類": "種類ごとの案（1 件ずつは本評価で書いた）",
      "足しただけ": "判定者用ファイルに足しただけで案は無い（1 件ずつは本評価で書いた）", "なし": "なし（本評価で新たに書いた）"}
E6 = "E6（OpenAlex に無料の版の記録が無く、全文段は判定できない）"

ELIG_HEADERS = ["候補番号", "出どころ", "題名", "DOI", "本文の入手（OpenAlex）", "中心範囲の段", "用途判定（Claude）", "判定根拠（プロトコル §2）",
                "原文確認レベル", "確認経路", "次の確認・作業", "既存の AI の案（ファイルと節）", "既存の案との違い"]
ELIG_WIDTHS = [9, 12, 40, 22, 14, 14, 11, 60, 12, 30, 30, 40, 40]
SCR_HEADERS = ["候補番号", "題名", "Claude予備判定（題名・抄録段）", "Claude予備判定（全文段）", "Claude案（現時点）", "除外理由", "全文確認・抽出",
               "中心範囲の段", "自由記入"]
SCR_WIDTHS = [9, 40, 13, 13, 11, 34, 11, 14, 30]
METH_HEADERS = ["候補番号", "題名", "研究デザイン（抄録・本文で確かめた範囲）", "懸念・限界（判定には使わない）"]
METH_WIDTHS = [9, 40, 40, 70]
CHK_HEADERS = ["番号", "対象の候補", "論点", "確認された内容", "扱いの案", "根拠"]
CHK_WIDTHS = [6, 20, 22, 60, 44, 30]
FIRST = 5  # 表の最初の行（1〜2 行目は見出し、4 行目は列の見出し）


def section_label(sec):
    return "§" + sec.lstrip("#").strip().rstrip(".")


def prior_text(entry):
    p = entry.get("p")
    kind = PK[entry.get("pk") or ("なし" if p is None else "1件")]
    if p is None:
        return kind
    key, sec, mark = p
    path = D.P[key].replace("../", "")
    return f"{key} の判定案（{path}）{section_label(sec)} の『{mark}』（{kind}）"


def fill(cid, entry, oa):
    """案 1 件の派生の値（design.md の規則）。"""
    ta = entry["ta"]
    free = oa.startswith("無料の版あり")
    closed = oa == "無料の版なし"
    ft = entry.get("ft")
    reason = entry.get("r", "")
    if ft is None:
        if ta == "除外":
            ft = "—"
        elif closed:
            ft = "保留"
            reason = f"{reason}／{E6}" if reason else E6  # ★ 既存の理由（計画の論文など）があっても E6 を落とさない
        else:
            ft = "未実施"  # 無料の版がある、または本文の入手が分からない（DOI なし・OpenAlex に記録なし）
    if ta == "除外":
        full = "対象外"
    elif entry.get("lv") == "本文関連箇所確認":
        full = "完了"
    elif closed:
        full = "入手不可"
    elif free:
        full = "未完了"
    else:
        full = "入手不明"  # ★ DOI なし・OpenAlex に記録なしを「無料の版あり」と同じに扱わない（2026-09-30 の code-reviewer の指摘）
    final = ft if ft in FINAL else ta
    # 自由記入の C 番号: 照合事項の表の対象に挙がるもの（と、案の文で触れたもの）
    notes = sorted(set(re.findall(r"照合事項 (C\d\d)", " ".join(str(entry.get(k, "")) for k in ("k", "n", "b", "r", "df"))))
                   | {c[0] for c in D.C if cid in re.findall(r"[A-Z]\d\d-\d\d", c[1])})
    return dict(ft=ft, reason=reason, full=full, final=final, use=USE[entry["c"]], free=free,
                level=entry.get("lv", "抄録"), route=entry.get("rt", D.RT_FACT), note="・".join(notes))


def rows(oa_map):
    out = []
    for m in J.candidate_records(oa_map):
        e = D.A[m["cid"]]
        out.append((m, e, fill(m["cid"], e, m["oa"])))
    return out


def overview_rows(data):
    E, S = "'Claude適格性評価'", "'Claudeスクリーニング案'"
    n = len(data)
    last = FIRST + n - 1
    by = {}
    for m, e, _ in data:
        by.setdefault(e["c"], []).append(m["cid"])
    s04_load = [m["cid"] for m, e, _ in data if re.search(r"S-04 §3\.[12]", m["src"])]
    s04_b = [c for c in s04_load if c in by.get("中心-B", [])]
    # 境界のうち、評価項目（疲労系の測定の有無）が抄録から分からないもの。S04-77 は燃え尽きを測るが AI の役割が決まらない別の理由なので分けて書く
    s04_h = [c for c in s04_load if c in by.get("境界（保留）", []) and D.A[c].get("p") == D.P04_LOAD]
    s04_o = [c for c in s04_load if c in by.get("境界（保留）", []) and c not in s04_h]

    def cnt(sheet, colname, val, headers):
        L = J.col(headers.index(colname) + 1)
        return f'=COUNTIF({sheet}!{L}{FIRST}:{L}{last},"{val}")'
    r = [["評価の対象（件）", f"=COUNTA({E}!A{FIRST}:A{last})", f"判定者用ファイルの『追加候補』と同じ {n} 件・同じ順・同じ候補番号。"]]
    for v in CENTER:
        r.append([f"中心範囲の段: {v}", cnt(E, "中心範囲の段", v, ELIG_HEADERS), ""])
    for v in TA:
        r.append([f"題名・抄録段: {v}", cnt(S, "Claude予備判定（題名・抄録段）", v, SCR_HEADERS), ""])
    for v in FT:
        r.append([f"全文段: {v}", cnt(S, "Claude予備判定（全文段）", v, SCR_HEADERS),
                  {"未実施": "本文を読んでいない（研究者の決定で抄録段）。無料の版がある、または本文の入手が分からない（全文確認の列で分ける）。", "保留": "本文を読めない（E6）か、本文を読んでも決まらない。",
                   "—": "題名・抄録段で除外。"}.get(v, "前のタスクで本文を読んだもの。")])
    for v in FULLTEXT:
        r.append([f"全文確認・抽出: {v}", cnt(S, "全文確認・抽出", v, SCR_HEADERS), ""])
    L = J.col(ELIG_HEADERS.index("既存の案との違い") + 1)
    r.append(["既存の AI の案と違う判定", f'=COUNTIF({E}!{L}{FIRST}:{L}{last},"?*")', "違いの中身は『既存の案との違い』の列。"])
    r.append(["照合事項（同じ研究・同じ標本の疑い）", f"=COUNTA('Claude照合事項'!A{FIRST}:A{FIRST + len(D.C) - 1})", "E5 の判断は判定者に委ねる。"])
    r += [
        ["読む順番", "Claude適格性評価 → Claudeスクリーニング案 → Claude方法論メモ／Claude照合事項", "基準は Claude評価基準。"],
        ["主な所見 1", f"中心-A は {len(by.get('中心-A', []))} 件（{'・'.join(by.get('中心-A', []))}）で、抄録で AI への帰属を確かめきれない中心（A/B 未確定）が "
                       f"{len(by.get('中心（A/B 未確定）', []))} 件。", "S08-02（RecalibrateGPT）は 2026-09-30 に足した候補。"],
        ["主な所見 2", "中心-B の多くは、AI への気づき・不安と情動的消耗・燃え尽きの横断の調査（S-14）と、医療の AI の記録支援の試験・前後比較（S-04 §2）。",
         "前後比較は対照が無く、回答者の偏りを避けられない。"],
        ["主な所見 3", f"作業負荷・時間だけの比較（S-04 §3.1・§3.2 の {len(s04_load)} 件）の多くは E2（疲労系の測定が抄録に無い）。燃え尽きを問う "
                       f"{len(s04_b)} 件（{'・'.join(s04_b)}）は中心-B、調査の中身・測定が抄録から分からない {len(s04_h)} 件（{'・'.join(s04_h)}）は境界。"
                       + (f"{'・'.join(s04_o)} は燃え尽きを測るが、AI の役割が抄録から決まらないので境界。" if s04_o else ""),
         "研究者が候補にした種類（前タスクの判断 17）。"],
        ["主な所見 4", "境界（保留）が多い型: AI を疲労の対策に使う介入（範囲の決定 (a) と v1.0 の E3 の読み分け）・アラート疲労・変化の疲れ・AI に評価される側・データの由来が不明・抄録が無い。",
         "判定者の判断が要る論点。"],
        ["限界", "盲検ではない／抄録段（全文段は本文を読んだ一部だけ）／題名だけの候補がある／取得した抄録で文が欠けた候補がある／正式な JBI・COSMIN の判定ではない",
         "詳細は Claude評価基準。"],
    ]
    return r


def criteria_rows(n):
    return [
        ["評価の対象", f"判定者用ファイルの『追加候補』の {n} 件（サーヴェイで見つかった DB に無い文献）。2026-09-30 に 19 件を足した（206 → 225・S-08 の 3 件と S-12 の 16 件）。",
         "元の DB 34 件は 2026-09-29 の評価版（AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx）。"],
        ["評価日・評価主体", "2026-09-30。判定: Claude Opus 5.5（メイン）。抄録の取得はスクリプト、読むのと判定はメイン。サブエージェントは使っていない。", "温度などの実行設定は取得していない。"],
        ["盲検性", "盲検ではない。メインは判定の前に、前のタスクの AI の判定案（サーヴェイごとの Markdown）と、元の DB の評価版を読んだ。既存の案と違う判定は『既存の案との違い』の列に理由を書いた。", ""],
        ["人間の判定との関係", "AI の予備判定であり、人間 2 名の独立判定の代わりにならない。判定者 1 は判定の前にこのファイルを判断材料として読む（2026-09-30 の研究者の決定）。判定者 2 はこのファイルを開かない。",
         "判定者用ファイルの『はじめに』に書いた。"],
        ["評価の深さ", "抄録段（2026-09-30 の研究者の決定）。全件を、サーヴェイの事実のファイルの行（前のタスクでメインが抄録を読んで書いたもの）と抄録で 1 件ずつ判定した。全文段の案は、前のタスクで本文を読んだものだけ。",
         "JBI・COSMIN の項目と領域別評価は、全文が要るので載せない。"],
        ["基準", "評価プロトコル v1.0（2026-09-28 固定）に、2026-09-30 の範囲の決定を足したもの（判定者用ファイルの『判定基準』と同じ）。", ""],
        ["範囲の決定 (a)", "AI の導入・利用を操作・比較し、使う人の疲労・消耗・燃え尽きを測った研究は、デザインと結果の向きを問わず C に当たりうる。", "2026-09-30"],
        ["範囲の決定 (b)", "自動化の監視の研究は、論文が対象の系を AI・機械学習と書く場合だけ P に当たる。従来の自動化だけの研究は E3。", "2026-09-30"],
        ["中心-A（AI 特異）", "一次研究で、疲労の構成概念が AI に帰属させて定義・測定されている（項目文・定義・質問文に AI が出る、または AI 疲労としての語り・自由記述を分析する）。",
         "抄録で AI 疲労としての語りの分析と確かめられたものだけ A にした。"],
        ["中心-B（AI 文脈）", "一次研究で、疲労・消耗・燃え尽きを測る・質的に分析するが、構成概念は一般的（AI を項目に含まない）で、AI の利用・AI 由来の要求を説明変数・文脈・標本定義として関係づけている。",
         "★ 抄録段の規則: 抄録が一般の尺度の名前（MBI・CBI・Mini-Z・BAT・PFI など）や一般の構成概念（情動的消耗・仕事の燃え尽き）を書き、AI に帰属させた測定を示さないものは中心-B とした（項目文は未確認）。"],
        ["中心（A/B 未確定）", "疲労系を測るが、構成概念が AI に帰属するか（項目に AI が出るか）を抄録で確かめられないもの。構成概念の名前が AI に帰属する（AI 疲労など）もの、AI をきっかけとする消耗・燃え尽きの語りで AI への帰属を分けられないものを含む。",
         "9/29 の評価基準の規則（抄録だけで A/B を確定しない・AF002・AF003 の先例）。A にも B にも数えない。"],
        ["境界（保留）", "P と C のどちらかが規則だけでは閉じないもの。多かった型: AI を疲労の対策に使う介入（範囲の決定 (a) の文言には当たるが、v1.0 の E3 とも読める）・アラート疲労・変化の疲れ・AI に評価される側（P）・データの由来が不明・疲労の測定の有無が抄録から分からない・抄録が無い・試験の計画。",
         "範囲の判断を人間の判定者に委ねる。"],
        ["背景（E2）・背景（E4）", "E2＝疲労（または同等の消耗状態）を定義・測定・質的分析していない（作業負荷・認知負荷・不安・慢心・睡眠だけなど）。E4＝一次研究でない。", "証拠集合の外。DB からは削除しない。"],
        ["除外（E1）・除外（E3）", "E1＝AI が人の疲労を検出・予測・分析する道具であるだけ（参加者が AI を使っていないものを含む）。E3＝疲労を測るが AI の利用・監督と関係づけていない。", ""],
        ["除外理由コード", "E1〜E6（プロトコル v1.0 §3）。E5＝重複出版・同じ標本・版違い、E6＝全文を入手できず全文段は判定できない（→ 保留）。この表に無い理由で除外しない。",
         "質の低さは除外の理由にしない（『懸念・限界』は判定に使わない）。"],
        ["題名・抄録段", "P と C に当たる可能性のある一次研究は『含める』（迷ったら含める）。", ""],
        ["全文段", "前のタスクで本文を読んだものだけ『含める／除外／保留』。読んでいないものは『未実施』（無料の版がある、または本文の入手が分からない）、OpenAlex に無料の版の記録が無いものは『保留』＋ E6、題名・抄録段で除外したものは『—』。",
         "「無料の版なし」は OpenAlex に記録が無いという意味で、存在しないことの確認ではない。"],
        ["Claude案（現時点）", "全文段を判定したものはその値、未実施は題名・抄録段の値、E6 は『保留』。", ""],
        ["全文確認・抽出", "完了＝前のタスクで本文の該当の節を読んだ／未完了＝無料の版がある／入手不可＝OpenAlex に無料の版の記録が無い／入手不明＝DOI が無い・OpenAlex に記録が無く、本文の入手が分からない／対象外＝題名・抄録段で除外。", ""],
        ["確認経路", f"『{D.RT_FACT}』／『{D.RT_BODY}』／『{D.RT_NEW}』／題名だけ。", "抄録は無料の学術 API（Europe PMC・Semantic Scholar・OpenAlex・Crossref・CiNii Research）から取り、連絡先は送っていない。抄録・本文は保存していない（作業の場所の外）。"],
        ["既存の AI の案", "前のタスクのサーヴェイの判定案（Markdown）。1 件ずつの案・種類ごとの案（S-04・S-05・S-14 の既定など）・足しただけ（案なし）・なし（2026-09-30 に足した候補）。種類ごとの案は写さず、1 件ずつ本評価で判定した。",
         "既存の案と違う判定は『既存の案との違い』の列。"],
        ["照合事項", "同じ研究の別の記録・同じ標本の疑い・訂正通知を『Claude照合事項』にまとめた。E5 にするかは判定者に委ねる（各行の題名・抄録段は中身で判定した）。", "研究不正の認定ではない。"],
        ["有料の本文", "有料の本文・データベースは使わない（2026-09-30 の研究者の決定）。", ""],
        ["限界", "盲検ではない。抄録段で、項目文を確かめていない（中心-B の多くは抄録の尺度の名前による）。題名だけの候補がある。取得した抄録で文が欠けた候補がある（欠けた値は書いていない）。正式な JBI・COSMIN の判定ではない。", ""],
    ]


def build():
    oa_map = J.load_oa()
    data = rows(oa_map)
    wb = openpyxl.Workbook()
    ws0 = wb.active
    ws0.title = "Claude評価概要"
    J.header_block(ws0, f"AI 疲労 文献 DB｜追加候補 {len(data)} 件の Claude による評価（2026-09-30）",
                   "判定者 1 が判定の前に読む判断材料。★ 人間の独立判定の代わりではない（AI の予備判定）。数字の列は各シートを数える数式。", 3)
    ov = overview_rows(data)
    J.put_table(ws0, ["項目", "値", "説明"], [30, 44, 70], ov)
    for r in range(FIRST, FIRST + len(ov)):
        if str(ws0.cell(r, 2).value).startswith("="):
            ws0.cell(r, 2).data_type = "f"

    ws = wb.create_sheet("Claude適格性評価")
    J.header_block(ws, "Claude適格性評価｜225 件の中心範囲の段・用途・根拠", "判定者用ファイルの『追加候補』と同じ順。中心範囲の段はプロトコル §2。"
                   "AI の予備判定であり、人間の判定の代わりにならない。既存の AI の案（前のタスクのサーヴェイの判定案）と違う判定は右端に理由を書いた。", len(ELIG_HEADERS))
    er = [[m["cid"], m["src"], m["title"] or m["label"], m["doi"] or "", m["oa"], e["c"], f["use"], e["b"], f["level"], f["route"],
           e.get("n") or "—", prior_text(e), e.get("df", "")] for m, e, f in data]
    J.put_table(ws, ELIG_HEADERS, ELIG_WIDTHS, er)
    for r, (m, _, _) in enumerate(data, FIRST):
        J.link(ws.cell(r, 4), J.doi_url(m["doi"]) if m["doi"] else None)

    ws = wb.create_sheet("Claudeスクリーニング案")
    J.header_block(ws, "Claudeスクリーニング案｜題名・抄録段と全文段の AI 予備判定", "選択肢は判定者用ファイルと同じ（含める／除外／保留）。全文段の『未実施』は本文を読んでいない"
                   "（研究者の決定で抄録段）、『—』は題名・抄録段で除外。自由記入の C 番号は『Claude照合事項』。", len(SCR_HEADERS))
    sr = [[m["cid"], m["title"] or m["label"], e["ta"], f["ft"], f["final"], f["reason"], f["full"], e["c"], f["note"]] for m, e, f in data]
    J.put_table(ws, SCR_HEADERS, SCR_WIDTHS, sr)

    ws = wb.create_sheet("Claude方法論メモ")
    J.header_block(ws, "Claude方法論メモ｜研究デザインと懸念（判定には使わない）", "抄録（一部は本文）で確かめた範囲のデザインと、引用するときに添える懸念・限界。"
                   "質の低さは除外の理由にしない。合計点・総合の格付けは付けない。", len(METH_HEADERS))
    mr = [[m["cid"], m["title"] or m["label"], e["d"], e.get("k") or "—"] for m, e, f in data]
    J.put_table(ws, METH_HEADERS, METH_WIDTHS, mr)

    ws = wb.create_sheet("Claude照合事項")
    J.header_block(ws, "Claude照合事項｜同じ研究・同じ標本・版違いの疑い", "E5 にするかは判定者に委ねる。研究不正の認定ではない。", len(CHK_HEADERS))
    J.put_table(ws, CHK_HEADERS, CHK_WIDTHS, [list(c) for c in D.C])

    wsc = wb.create_sheet("Claude評価基準")
    J.header_block(wsc, "Claude評価基準｜範囲・手順・限界", "今回の評価で用いた操作的基準（design.md に書いてから判定した）。", 3)
    J.put_table(wsc, ["項目", "規則・説明", "備考"], [22, 90, 50], criteria_rows(len(data)))

    wb.active = 1
    for w in wb.worksheets:
        w.sheet_view.tabSelected = (w.title == "Claude適格性評価")
    wb.properties.title = "AI 疲労 文献 DB 追加候補の AI 評価版"
    wb.properties.creator = "appraisal_xlsx.py"
    return wb


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--copy-to")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    J.guard(a.out, a.force)
    copy_dst = os.path.join(a.copy_to, os.path.basename(a.out)) if a.copy_to else None
    if copy_dst:
        if os.path.normcase(os.path.abspath(copy_dst)) == os.path.normcase(os.path.abspath(a.out)):
            sys.exit("--copy-to の先が --out と同じ")
        J.guard(copy_dst, a.force)
        # ★ judge_xlsx.guard の「記入のあるファイルは上書きしない」は判定の 2 シートしか見ず、評価版には効かない（security-checker L-1）。
        #   評価版の写しは、archive の版（--out）と同じバイト列のときだけ置き換える（判定者 1 がメモを書いた写しを消さない）。
        if os.path.exists(copy_dst):
            if not os.path.exists(a.out) or J.sha256(copy_dst) != J.sha256(a.out):
                sys.exit(f"写しが archive の版と違う（書き込まれた可能性があるので置き換えない）: {copy_dst}")
    import check_appraisal_xlsx as CHK
    errs = CHK.check_data()
    if errs:
        for e in errs:
            print("NG", e)
        sys.exit("案のデータの検査に失敗した（作らない）")
    wb = build()
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".xlsx", dir=os.path.dirname(os.path.abspath(a.out)))
    os.close(fd)
    try:
        wb.save(tmp)
        errs = CHK.check(tmp)
        for e in errs:
            print("NG", e)
        if errs:
            sys.exit("評価版の検査に失敗した（保存しない）")
        J.place(tmp, a.out, a.force)
        print("saved:", a.out)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    if copy_dst:
        J.place(a.out, copy_dst, a.force)
        print("copied:", copy_dst)


if __name__ == "__main__":
    main()
