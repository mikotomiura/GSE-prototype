"""追加候補の新しいスプレッドシートを、元の資料から毎回作り直す（design.md §7）。

元の資料: 判定者用ファイルの『追加候補』220 件（読むだけ）・data/extra-records.json（X01〜）・
          本タスクのログ・data/*.json（抽出・品質・探索）・評価版（判定済みの記録の AI用途判定だけを読む）。
★ Downloads の表が最後に書いた SHA-256（archive/candidates-sha256.txt）と違えば止まる（手で記入された可能性）。
★ 未判定の記録の AI の判定は表に載せない（『AI判定比較』は判定済みで評価版に行がある記録だけ）。
使い方: python build_candidates.py [--dry-run]
"""
import json
import os
import shutil
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

import common as C

# --- 答え → 表の値（design.md §1・前のタスクの design.md §2.2）。★ 検査器は別に同じ表を持つ（import しない） ---
USE_TO_HUMAN = {"中心-A": "中心候補", "中心-B": "中心候補", "背景保持": "背景保持", "方法論保持": "方法論保持",
                "訂正連結": "訂正連結", "除外": "除外", "保留": "保留"}
E4_KIND = {"レビュー": "背景保持", "論考": "背景保持", "研究計画": "背景保持", "一次研究": "背景保持",
           "方法論": "方法論保持", "訂正通知": "訂正連結"}
CRITERIA_VERSION = "評価プロトコル v1.0＋2026-09-30 の範囲の決定＋2026-10-01 の読み方"
UNCLASSIFIED = "追加候補（未分類）"

SCR_HEADER = ["ID", "論文タイトル", "暫定分類", "判定者1", "判定者2", "最終判定", "除外理由", "全文確認・抽出", "品質評価", "自由記入",
              "出どころ", "DOI", "年", "掲載誌", "本文の入手（OpenAlex）", "同じ研究の群", "内容の群（機械の分類・判定の材料ではない）"]
CMP_HEADER = ["ID", "論文タイトル", "AI用途判定", "人間用途判定", "分類の一致", "人間判定の理由・版", "最終合意・次の作業"]
LOG_HEADER = ["seq", "ID", "段", "問い（逐語）", "選択肢", "答え", "補足（note）"]
VOCAB = {"D": '"未判定,含める,除外,保留"', "E": '"未判定,含める,除外,保留"', "F": '"未判定,含める,除外,保留"',
         "H": '"未完了,進行中,完了,入手不可,対象外"', "I": '"未実施,進行中,完了,対象外"'}


def load_json(p, default=None):
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding="utf-8"))


def load_log():
    if not os.path.exists(C.LOG):
        return []
    return [json.loads(x) for x in open(C.LOG, encoding="utf-8") if x.strip()]


def decisions(log):
    """件ごとに 1 回目と最終（2/2e の最後・無ければ 1 回目）・品質（q）・抽出の確定（x）。"""
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


def appraisal_use():
    """評価版『Claude適格性評価』の 候補番号 → 用途判定（Claude）。"""
    ws = openpyxl.load_workbook(C.APPRAISAL, read_only=True)["Claude適格性評価"]
    rows = list(ws.iter_rows(values_only=True))
    h = next(k for k, r in enumerate(rows[:8]) if r and r[0] == "候補番号")
    j = rows[h].index("用途判定（Claude）")
    return {r[0]: r[j] for r in rows[h + 1:] if r and r[0]}


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


def cells_for(i, first, final, quality, xconf, has_ai):
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
    basis_label = {"なし": "題名と書誌だけ"}.get(basis, basis)  # ★ basis「なし」= 本文も抄録も無く題名と書誌だけで判定
    j = (f"用途: {use} ／ 1回目: {label(f0)} → 最終: {label(f1)}{changed} ／ 材料: {basis_label} ／ AI の判定: {ai} ／ "
         f"{f1.get('date', '')} ／ ログ: 『問いと答え』")
    return {"D": f1["verdict"], "G": g, "H": h, "I": ival, "J": j, "human_use": USE_TO_HUMAN[use],
            "reason": f1.get("reason_summary", ""), "next": f1.get("next", "")}


def put(cell, v):
    """セルに値を書く。★ 先頭が = の文字列は式にしない（探索の題名など外の文が式になるのを防ぐ・判断 10）。"""
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


def intro_rows(n_rows, n_done, n_ai):
    return [
        ("このファイル", "研究者の DB（09-18）に無い追加候補（サーヴェイで見つかった 220 件と、判定者 1 が足した記録）を、研究者の『スクリーニング』と同じ列で並べた。"
                       "DB の記録ではなく提案で、DB に入れるかは研究者が決める。"),
        ("判定者 2 に渡すとき", "このファイルは判定者 2 に渡さない（判定者1 の欄と『AI判定比較』『問いと答え』があると、2 人の判定が独立でなくなる）。"
                             "判定者 2 に渡す版は、『スクリーニング』の D・G・H・I・J 列を初期値（判定者1 = 未判定・除外理由 = 空・全文確認 = 未完了・"
                             "品質評価 = 未実施・自由記入 = 空）に戻し、『AI判定比較』『全文抽出』『品質評価』『問いと答え』のシートを消して作る"
                             "（どれも判定者 1 の判定・理由・進み具合を含む）。"),
        ("基準の版", CRITERIA_VERSION + "（判定者用ファイルの『判定基準』と同じ）"),
        ("判定の段", "全文段の 1 回。各件を 2 段で記録: 1 回目は AI の判定を見ずに選び、2 回目に AI の判定を見て変えるかを選んだ。両方を自由記入に残した。"),
        ("AI の判定", "追加候補の AI の判定は Claude 版（2026-09-30 の評価版）だけで、GPT 版は無い。評価版に行が無い記録（判定者 1 が足した記録）は 2 回目を置かず、"
                    "新しい AI の判定も作っていない（自由記入に「AI の判定: なし」）。『AI判定比較』は判定済みで評価版に行がある記録だけを載せた（未判定の記録の AI の判定は載せない）。"),
        ("判定の前に読んだもの", "判定者 1 は、判定の前に、追加候補の AI の評価版（Claude 版）を読んでいる（盲検ではない）。"),
        ("暫定分類の列", f"研究者の DB の暫定分類は研究者が付けた。追加候補には研究者の分類が無いので、全行「{UNCLASSIFIED}」とした（AI の分類を入れていない）。"
                       "研究の種類は『全文抽出』の研究デザインに書いた。内容の群の列は機械の分類で、判定の材料ではない。"),
        ("答えと用途の対応", "含める（中心-A／中心-B）→ 中心候補／除外 E2 → 背景保持／除外 E4 → レビュー・論考・研究計画は背景保持、方法論は方法論保持、訂正通知は訂正連結／"
                         "除外 E1・E3・E5・E7 → 除外／保留（E6 を含む）→ 保留"),
        ("品質評価", "判定で含めた一次研究だけ確定する（JBI・尺度開発は COSMIN・6 領域・合計点なし）。レビュー・論考・除外は対象外。"),
        ("無料の本文", "有料の本文は使っていない。無料の全文が無い記録は全文確認を入手不可とし、抄録（無ければ題名と書誌）を材料に判定した（自由記入の「材料」）。"),
        ("Claude の関与", "本文の取得・抽出の下書き・原文との照合・レビューを狙った探索（無料の学術 API・メールアドレスは送っていない）は Claude（メインとサブエージェント）が行い、"
                        "判定者 1 が確かめて確定した。1 回目の問いには事実と基準だけを載せた。"),
        ("探索", "『探索の検索式』『探索の一覧』: AI の語 × 疲労の語 × レビューの語（2020 年以降）で 4 つの無料の学術 API を引き、条件を通った記録をすべて載せた。"
                "判定者 1 が候補に足したかを列に記した。"),
        ("記録", "質問と答えの逐語は『問いと答え』（作業記録の写し・1 行 1 問）。"),
        ("進み具合", f"判定済み {n_done} / {n_rows} 件（うち評価版に行がある記録 {n_ai} 件）。未判定の行は研究者の初期値のまま。"),
    ]


def build(dst):
    log = load_log()
    first, final, quality, xconf = decisions(log)
    cands = candidates()
    extra = load_json(C.EXTRA_RECORDS, [])
    ai_use = appraisal_use()
    rows_src = cands + [{"id": x["id"], "title": x["title"], "source": x["source"], "doi": x.get("doi"), "year": x.get("year"),
                         "venue": x.get("venue"), "oa": x.get("oa"), "group": None, "content": x.get("content")} for x in extra]
    ids = [r["id"] for r in rows_src]
    assert len(ids) == len(set(ids)), "ID の重複"
    unknown = [i for i in final if i not in ids]
    assert not unknown, f"ログに表に無い ID: {unknown}"

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    done = [i for i in ids if i in final]
    with_ai = [i for i in done if i in ai_use]
    add_sheet(wb, "はじめに", "追加候補（判定者 1）｜何のファイルか", "このファイルは判定者 1 が作った。研究者の DB とは別のファイル。",
              ["項目", "説明"], intro_rows(len(ids), len(done), len(with_ai)), {1: 22, 2: 110})
    scr_rows, cmp_rows = [], []
    for r in rows_src:
        i = r["id"]
        row = [i, r["title"], UNCLASSIFIED, "未判定", "未判定", "未判定", None, "未完了", "未実施", None,
               r["source"], r["doi"], r["year"], r["venue"], r["oa"], r["group"], r["content"]]
        if i in final:
            v = cells_for(i, first, final, quality, xconf, i in ai_use)
            row[3], row[6], row[7], row[8], row[9] = v["D"], v["G"] or None, v["H"], v["I"], v["J"]
            if i in ai_use:
                cmp_rows.append([i, r["title"], ai_use[i], v["human_use"], None,
                                 f"{v['reason']} ／ 基準の版: {CRITERIA_VERSION}".strip(" ／"),
                                 f"次の作業: {v['next']}（最終合意は判定者 2 の後）" if v["next"] else "（最終合意は判定者 2 の後）"])
        scr_rows.append(row)
    ws = add_sheet(wb, "スクリーニング", "追加候補｜文献選定・全文確認（研究者の『スクリーニング』と同じ列）",
                   "青字の欄は入力用（研究者と同じ）。判定者1・2は独立した人間の担当者を想定し、AIの予備整理を独立判定に数えません。判定者2・最終判定は未判定のまま。",
                   SCR_HEADER, scr_rows, {2: 50, 10: 50})
    last = 4 + len(scr_rows)
    for col, f in VOCAB.items():
        dv = DataValidation(type="list", formula1=f, allow_blank=True)
        dv.add(f"{col}5:{col}{last}")
        ws.add_data_validation(dv)
    wc = add_sheet(wb, "AI判定比較", "AI判定比較｜判定済みで評価版に行がある記録だけ",
                   "AI用途判定は Claude 版（2026-09-30 の評価版）。一致欄は用途分類の一致のみで、品質評価やκではありません。", CMP_HEADER, cmp_rows)
    for k in range(len(cmp_rows)):
        r = 5 + k
        wc[f"E{r}"] = f'=IF(D{r}="","",IF(C{r}=D{r},"一致","要照合"))'
    dv = DataValidation(type="list", formula1='"中心候補,背景保持,方法論保持,訂正連結,除外,保留"', allow_blank=True)
    dv.add(f"D5:D{max(5, 4 + len(cmp_rows))}")
    wc.add_data_validation(dv)
    ex = load_json(C.EXTRACT_ROWS)
    add_sheet(wb, "全文抽出", "追加候補の全文抽出｜34 件の写しの『判定者1_全文抽出』と同じ列",
              "Claude の下書きを判定者 1 が確かめた。数値は原文どおり。原文の箇所を右端に記す。",
              ex["header"] if ex else ["ID"], ex["rows"] if ex else [])
    qu = load_json(C.QUALITY_ROWS)
    if qu and qu["rows"]:
        add_sheet(wb, "品質評価", "追加候補の品質評価｜含めた一次研究",
                  "JBI（尺度開発は COSMIN）の項目と 6 領域。合計点・総合の格付けは付けない。", qu["header"], qu["rows"])
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
              "か読まない理由（題名の語の規則）。足した = 判定者 1 が候補に足したか（候補に足すかの判定は次のタスク）。",
              ["key", "題名", "年", "種別（API）", "掲載", "言語", "無料の版", "重なり", "見つかった API", "層", "読む一覧", "足した（ID）"],
              [[x["key"], x["title"], x.get("year"), x.get("type"), x.get("venue"), x.get("language"), x.get("oa"),
                x.get("overlap"), x.get("sources"), x.get("layer"), x.get("reading"), x.get("added_as") or "いいえ"] for x in recs])
    add_sheet(wb, "問いと答え", "判定者 1 の問いと答え｜作業記録の写し（1 行 1 問）",
              "段: 1 = 1 回目（AI の判定を見ない）・1e = 除外の理由・2 = 2 回目（AI の判定を見た）・q = 品質評価の確定・x = 抽出の確定・s = 探索の記録を候補に足すか。",
              LOG_HEADER, [[r.get("seq"), r["item"], r["stage"], r["question"], " ／ ".join(r.get("options") or []), r["answer"], r.get("note", "")]
                           for r in log])
    wb.save(dst)


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
    last = open(C.CAND_SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(C.CAND_SHA_RECORD) else None
    for p in (C.CAND_ARCHIVE, C.CAND_DOWNLOADS):
        if os.path.exists(p) and C.sha256(p) != last:
            sys.exit(f"表が最後に書いたものと違う（手で記入された可能性・止まって聞く）: {p}")
        if not os.path.exists(p) and last is not None:
            sys.exit(f"記録があるのに表が無い（止まって聞く）: {p}")
    os.makedirs(os.path.dirname(C.CAND_ARCHIVE), exist_ok=True)
    tmps = []
    try:
        fd, tmp_a = tempfile.mkstemp(suffix=".xlsx", dir=os.path.dirname(C.CAND_ARCHIVE), prefix=".tmp-")
        os.close(fd)
        tmps.append(tmp_a)
        build(tmp_a)
        fd, tmp_d = tempfile.mkstemp(suffix=".xlsx", dir=C.DOWNLOADS, prefix=".tmp-cand-")
        os.close(fd)
        tmps.append(tmp_d)
        shutil.copyfile(tmp_a, tmp_d)
        bak = None
        if os.path.exists(C.CAND_DOWNLOADS):
            if C.sha256(C.CAND_DOWNLOADS) != last:  # ★ 退避の直前にもう一度
                sys.exit(f"表が最後に書いたものと違う（止まって聞く）: {C.CAND_DOWNLOADS}")
            bak = C.CAND_DOWNLOADS + ".bak-" + last[:12]
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
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
