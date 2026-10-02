"""逐語のログと抽出・品質・確認のデータから、ワークブックの写しを書き直す（design.md §2）。

★ 毎回、元のファイル（09-18・SHA-256 固定）から作り直す（前の写しに積み増さない）。
★ Downloads の写しが最後に書いた SHA-256（archive/copy-sha256.txt）と違えば止まる（手で記入された可能性）。
★ 元のシートで書くのは design.md §2.1 の入力欄だけ。ほかは `判定者1_` で始まるシートを足す。
使い方: python write_workbook.py [--dry-run]
"""
import json
import os
import shutil
import sys
import tempfile

import openpyxl
from openpyxl.styles import Alignment, Font

import common34 as C

# --- 答え → 写しの値（design.md §2.2）。★ 検査器は別に同じ表を持つ（import しない） ---
USE_TO_HUMAN = {
    "中心-A": "中心候補", "中心-B": "中心候補",
    "背景保持": "背景保持", "方法論保持": "方法論保持", "訂正連結": "訂正連結",
    "除外": "除外", "保留": "保留",
}
E4_KIND = {"既存レビュー": "背景保持", "尺度・理論": "背景保持", "方法論": "方法論保持", "訂正通知": "訂正連結",
           "直接研究": "背景保持", "隣接研究": "背景保持"}
PRIMARY = {"直接研究", "隣接研究"}
CRITERIA_VERSION = "評価プロトコル v1.0＋2026-09-30 の範囲の決定＋2026-10-01 の読み方"
# ★ 2 回目の前後に、AI の判定（GPT 版・Claude 版）のほかに本セッションの Claude の見立て・計算を判定者 1 が見た件
#   （ログの note に逐語。decisions.md 判断 4 の 2・4・5。security-checker の指摘で写しにも書く・判断 12）
CLAUDE_SHOWN = {
    "AF002": "2 回目の前に、判定者 1 の問いに答えて Claude（このセッション）が見立て（関係の深さは高い・証拠としての強さは中〜低）を会話で示した",
    "AF003": "2 回目の前に、判定者 1 の問いに答えて Claude（このセッション）が見立て（関係の深さは高い・証拠としての強さは中〜低）を会話で示した",
    "AF004": "2 回目の後の確認の前に、Claude が論文の数値から媒介を計算し直した結果と、AI に結びつく変数が AI 依存だけであることを会話で示した",
}

DATA_FILES = {
    "extract": os.path.join(C.TASK, "data", "extract-rows.json"),
    "quality": os.path.join(C.TASK, "data", "quality-rows.json"),
    "checks": os.path.join(C.TASK, "data", "checks-rows.json"),
}
REASONS = os.path.join(C.TASK, "reason-questions-restored.jsonl")  # ★ 理由の問いの逐語（セッションの記録から復元・判断 14）


def put(cell, v):
    """セルに値を書く。★ 先頭が = の文字列は式にしない（文字列として保存する。外の文が式になるのを防ぐ・判断 14）。"""
    cell.value = v
    if isinstance(v, str) and v.startswith("="):
        cell.data_type = "s"
    return cell


def load_log():
    if not os.path.exists(C.LOG):
        return []
    out = []
    with open(C.LOG, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                rec = json.loads(line)
                rec["_line"] = n
                out.append(rec)
    return out


def decisions(log):
    """件ごとに 1 回目と最終の判定（result）を返す。1 回目 = stage 1/1e の最後、最終 = 2/2e の最後（無ければ 1 回目）。"""
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


def use_of(result, kind):
    if result["verdict"] == "含める":
        return result["use"]  # 中心-A / 中心-B
    if result["verdict"] == "保留":
        return "保留"
    e = result.get("ecode") or ""
    if e == "E2":
        return "背景保持"
    if e == "E4":
        return E4_KIND[kind]
    if e == "E6":
        return "保留"
    return "除外"


def cells_for(i, kind, first, final, quality, xconf):
    f0, f1 = first[i], final[i]
    if f1["verdict"] == "含める" and kind not in PRIMARY:
        # ★ 「含める（一次研究として読む）」の用途・品質評価の規則は決めていない（design §3 の選択肢にはある・判断 14）
        sys.exit(f"{i}: 一次研究でない件を含めた（『一次研究として読む』の規則は未実装・止まって決める）")
    basis = f1.get("basis", "全文")
    use = use_of(f1, kind)
    g = ""
    if f1["verdict"] == "除外":
        g = f"{f1['ecode']} {f1.get('elabel', '')}".strip()
    h = "入手不可" if basis == "抄録" else ("完了" if i in xconf else "進行中")
    if f1["verdict"] == "含める" and kind in PRIMARY:
        q = quality.get(i)
        if basis == "抄録":  # ★ design §2.1: 含める一次研究で抄録だけ → 進行中（q の有無によらない・判断 13）
            ival = "進行中"
        elif q is None:
            ival = "未実施"
        elif str(q.get("answer", "")).startswith("保留"):  # ★ 選択肢は「保留（判定不能のまま）」
            ival = "進行中"
        else:
            ival = "完了"
    elif f1["verdict"] == "保留":
        ival = "未実施"
    else:
        ival = "対象外"

    def label(r):
        if r["verdict"] == "含める":
            return f"含める（{r['use']}）"
        if r["verdict"] == "除外":
            return f"除外 {r['ecode']}"
        return "保留"

    changed = "" if label(f0) == label(f1) else f"（変えた理由: {f1.get('reason', '')}）"
    j = (f"用途: {use} ／ 1回目: {label(f0)} → 最終: {label(f1)}{changed} ／ 材料: {basis} ／ "
         f"{f1.get('date', '')} ／ ログ: 『判定者1_問いと答え』")
    if i in CLAUDE_SHOWN:
        j += f" ／ Claude の関与: {CLAUDE_SHOWN[i]}"
    return {"D": f1["verdict"], "G": g, "H": h, "I": ival, "J": j,
            "human_use": USE_TO_HUMAN[use], "reason": f1.get("reason_summary", ""), "next": f1.get("next", "")}


def kinds(wb):
    ws = wb["スクリーニング"]
    return {ws.cell(r, 1).value: ws.cell(r, 3).value for r in range(C.FIRST_ROW, C.FIRST_ROW + 34)}


def add_sheet(wb, name, title, note, header, rows):
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    put(ws["A1"], title).font = Font(bold=True, size=12)
    put(ws["A2"], note)
    for c, h in enumerate(header, 1):
        put(ws.cell(4, c), h).font = Font(bold=True)
    for r, row in enumerate(rows, 5):
        for c, v in enumerate(row, 1):
            put(ws.cell(r, c), v).alignment = Alignment(wrap_text=True, vertical="top")
    for c in range(1, len(header) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = 14 if c == 1 else 36
    ws.freeze_panes = "B5"
    return ws


REASON_HEADER = ["seq（答えのログ）", "ID", "問い（逐語）", "選択肢", "複数選択", "答え", "補足（note）", "答えた時刻"]


def load_reasons():
    if not os.path.exists(REASONS):
        return []
    return [json.loads(x) for x in open(REASONS, encoding="utf-8") if x.strip()]


def load_rows(key):
    p = DATA_FILES[key]
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def build(dst):
    log = load_log()
    first, final, quality, xconf = decisions(log)
    wb = openpyxl.load_workbook(C.ORIGINAL)
    kind = kinds(wb)
    scr, cmp_ = wb["スクリーニング"], wb["AI判定比較"]
    done = [i for i in C.IDS if i in final]
    # ★ 『AI判定比較』は 34 件すべての 2 回目（stage 2/2e）の後（1 回目だけの件を最終と数えない・判断 14）
    done2 = [i for i in C.IDS if any(r["item"] == i and r["stage"] in ("2", "2e") for r in log)]
    all_done = len(done2) == len(C.IDS)
    for k, i in enumerate(C.IDS):
        r = C.FIRST_ROW + k
        assert scr.cell(r, 1).value == i and cmp_.cell(r, 1).value == i, (i, r)
        if i not in final:
            continue
        v = cells_for(i, kind[i], first, final, quality, xconf)
        for col in ("D", "G", "H", "I", "J"):
            if v[col] != "":
                put(scr[f"{col}{r}"], v[col])
        if all_done:  # 『AI判定比較』は 34 件の判定（2 回目まで）がすべて終わってから（シートの逐語「人間の独立判定終了後に入力」）
            put(cmp_[f"D{r}"], v["human_use"])
            put(cmp_[f"F{r}"], f"{v['reason']} ／ 基準の版: {CRITERIA_VERSION}".strip(" ／"))
            put(cmp_[f"G{r}"], f"次の作業: {v['next']}（最終合意は判定者 2 の後）" if v["next"] else "（最終合意は判定者 2 の後）")
    intro = [
        ("このシート群", "判定者 1 が記入した。元のシートで書いたのは『スクリーニング』の判定者1・除外理由・全文確認・抽出・品質評価・自由記入の欄と、"
                       "『AI判定比較』の人間用途判定・理由・次の作業の欄だけ。判定者2・最終判定は未判定のまま。"),
        ("基準の版", CRITERIA_VERSION + "（判定者用ファイルの『判定基準』と同じ）"),
        ("判定の段", "全文段の 1 回。各件を 2 段で記録: 1 回目は AI の判定を見ずに選び、2 回目に AI の判定（GPT 版・Claude 版）を見て変えるかを選んだ。両方を自由記入に残した。"),
        ("判定の前に読んだもの", "判定者 1 は、判定の前に、元の DB 34 件について評価版ファイル（GPT 版・Claude 版）の AI の評価を読んでいる（盲検ではない）。"),
        ("答えと用途の対応", "含める（中心-A／中心-B）→ 中心候補／除外 E2 → 背景保持／除外 E4 → 既存レビュー・尺度・理論は背景保持、方法論は方法論保持、訂正通知は訂正連結／"
                         "除外 E1・E3・E5・E7 → 除外／保留（E6 を含む）→ 保留"),
        ("品質評価", "判定で含めた一次研究だけ確定した（JBI・尺度開発は COSMIN・6 領域・合計点なし）。背景・方法論・訂正・除外は対象外。"),
        ("無料の本文", "有料の本文は使っていない。無料の全文が無い件は全文確認を入手不可とし、抄録を材料に判定した（自由記入に「材料: 抄録」）。"),
        ("Claude の関与", "本文の取得・抽出と品質評価の下書き・原文との照合は Claude（メインとサブエージェント）が行い、判定者 1 が確かめて確定した。"
                        "1 回目の問いには事実だけを載せ、2 回目に AI の判定（GPT 版・Claude 版）を見せた。このほか AF002・AF003 では 2 回目の前に Claude の見立てを、"
                        "AF004 では 2 回目の後の確認の前に Claude の再計算を、判定者 1 が見ている（各行の自由記入と『判定者1_問いと答え』の補足）。"),
        ("判定者 2 に渡すとき", "この写しは判定者 2 に渡さない（判定者1 の欄と 判定者1_ のシートがあると、2 人の判定が独立でなくなる）。"
                             "判定者 2 には元のファイル（09-18）を渡す。この写しから作るなら、"
                             + "と".join(f"『{s}』の {'・'.join(cols)} 列" for s, cols in C.INPUT_COLS.items())
                             + "を元のファイルの値に戻し、名前が 判定者1_ で始まるシートをすべて消す"
                             "（どれも判定者 1 の判定・理由・進み具合を含む）。"),
        ("記録", "質問と答えの逐語は『判定者1_問いと答え』（作業記録 screening-log.jsonl の写し・1 行 1 問）。"
                "2 回目の後に重ねた理由の問い（変えた理由・保留の理由）は、当時は答えだけを補足に入れたので、"
                "問いの文と選択肢を対話の記録から復元して『判定者1_理由の問い』に載せた（答えは補足と一致する）。"),
        ("元の『はじめに』の数式", "openpyxl で保存したため、元の『はじめに』シートの数式は計算済みの値を持たない。Excel で開くと再計算される"
                               "（プレビューや他の閲覧ソフトでは空に見えることがある）。"),
        ("進み具合", f"判定済み {len(done)} / 34 件（2 回目まで {len(done2)} 件）"
                     + ("" if all_done else "（『AI判定比較』は 34 件の 2 回目の後に記入する）")),
    ]
    add_sheet(wb, C.ADDED_PREFIX + "はじめに", "判定者 1 の記入｜何をしたか", "このシートは判定者 1 が足した。", ["項目", "説明"], intro)
    add_sheet(wb, C.ADDED_PREFIX + "問いと答え", "判定者 1 の問いと答え｜作業記録の写し（1 行 1 問）",
              "段: 1 = 1 回目（AI の判定を見ない）・1e = 除外の理由・2 = 2 回目（AI の判定を見た）・q = 品質評価の確定・x = 抽出の確定。",
              ["seq", "ID", "段", "問い（逐語）", "選択肢", "答え", "補足（note）"],
              [[r.get("seq"), r["item"], r["stage"], r["question"], " ／ ".join(r.get("options") or []), r["answer"], r.get("note", "")]
               for r in log])
    reasons = load_reasons()
    if reasons:
        add_sheet(wb, C.ADDED_PREFIX + "理由の問い", "判定者 1 の理由の問い｜2 回目の後に重ねた問いの逐語（対話の記録から復元）",
                  "答えは『判定者1_問いと答え』の同じ seq の補足（note）と一致する。問いと選択肢は当時の対話の記録から読み取った。",
                  REASON_HEADER,
                  [[x["log_seq"], x["item"], x["question"], " ／ ".join(x["options"]), "可" if x["multiSelect"] else "不可",
                    x["answer"], x.get("user_note", ""), (x.get("answered_at") or "")[:16].replace("T", " ") + "（UTC）"]
                   for x in reasons])
    ex = load_rows("extract")
    if ex:
        add_sheet(wb, C.ADDED_PREFIX + "全文抽出", "判定者 1 の全文抽出｜『研究情報』と同じ列の形",
                  "Claude の下書きを判定者 1 が確かめた。数値は原文どおり。原文の箇所を右端に記す。", ex["header"], ex["rows"])
    qu = load_rows("quality")
    if qu:
        add_sheet(wb, C.ADDED_PREFIX + "品質評価", "判定者 1 の品質評価｜含めた一次研究",
                  "JBI（尺度開発は COSMIN）の項目と 6 領域。合計点・総合の格付けは付けない。", qu["header"], qu["rows"])
    ch = load_rows("checks")
    if ch:
        add_sheet(wb, C.ADDED_PREFIX + "確認の結果", "判定者 1 の確認の結果｜確認事項・次の確認・作業・メモ",
                  "原文で確かめた結果と箇所。確かめた経路（メインが原文で／抽出だけ）を記す。", ch["header"], ch["rows"])
    wb.save(dst)


def main(dry):
    if C.sha256(C.ORIGINAL) != C.ORIGINAL_SHA256:
        sys.exit("元のファイルの SHA-256 が違う")
    last = open(C.COPY_SHA_RECORD, encoding="utf-8").read().strip()
    for p in (C.COPY_ARCHIVE, C.COPY_DOWNLOADS):
        if C.sha256(p) != last:
            sys.exit(f"写しが最後に書いたものと違う（手で記入された可能性・止まって聞く）: {p}")
    # ★ dry-run の出力は repo の外（OS の一時フォルダ）。本番は同じフォルダの一時ファイル → os.replace（途中で止まっても半端な写しを残さない）
    if dry:
        fd, tmp = tempfile.mkstemp(suffix=".xlsx", prefix="judge1-dry-")
        os.close(fd)
        build(tmp)
        print("dry-run ok（repo の外）", tmp)
        return
    tmps = []
    try:
        fd, tmp_a = tempfile.mkstemp(suffix=".xlsx", dir=os.path.dirname(C.COPY_ARCHIVE), prefix=".tmp-")
        os.close(fd)
        tmps.append(tmp_a)
        build(tmp_a)
        fd, tmp_d = tempfile.mkstemp(suffix=".xlsx", dir=os.path.dirname(C.COPY_DOWNLOADS), prefix=".tmp-judge1-")
        os.close(fd)
        tmps.append(tmp_d)
        shutil.copyfile(tmp_a, tmp_d)
        # ★ 退避の直前にもう一度確かめる（冒頭の照合から今までに Excel で保存されていないか・判断 13）
        if C.sha256(C.COPY_DOWNLOADS) != last:
            sys.exit(f"写しが最後に書いたものと違う（手で記入された可能性・止まって聞く）: {C.COPY_DOWNLOADS}")
        bak = C.COPY_DOWNLOADS + ".bak-" + last[:12]
        shutil.copyfile(C.COPY_DOWNLOADS, bak)
        os.replace(tmp_d, C.COPY_DOWNLOADS)
        try:
            os.replace(tmp_a, C.COPY_ARCHIVE)
        except OSError:
            shutil.copyfile(bak, C.COPY_DOWNLOADS)  # ★ archive が置き換わらなければ Downloads も前の写しに戻す（2 つの写しと記録の SHA を揃える）
            raise
    finally:
        for t in tmps:
            if os.path.exists(t):
                os.remove(t)
    new = C.sha256(C.COPY_ARCHIVE)
    if C.sha256(C.COPY_DOWNLOADS) != new:
        sys.exit("archive と Downloads の写しが合わない")
    with open(C.COPY_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write(new + "\n")
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
