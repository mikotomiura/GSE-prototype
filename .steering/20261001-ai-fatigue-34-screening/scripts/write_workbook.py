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

DATA_FILES = {
    "extract": os.path.join(C.TASK, "data", "extract-rows.json"),
    "quality": os.path.join(C.TASK, "data", "quality-rows.json"),
    "checks": os.path.join(C.TASK, "data", "checks-rows.json"),
}


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
    basis = f1.get("basis", "全文")
    use = use_of(f1, kind)
    g = ""
    if f1["verdict"] == "除外":
        g = f"{f1['ecode']} {f1.get('elabel', '')}".strip()
    h = "入手不可" if basis == "抄録" else ("完了" if i in xconf else "進行中")
    if f1["verdict"] == "含める" and kind in PRIMARY:
        q = quality.get(i)
        if q is None:
            ival = "未実施"
        elif basis == "抄録" or q.get("answer") == "保留":
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
         f"{f1.get('date', '')} ／ ログ: screening-log.jsonl")
    return {"D": f1["verdict"], "G": g, "H": h, "I": ival, "J": j,
            "human_use": USE_TO_HUMAN[use], "reason": f1.get("reason_summary", ""), "next": f1.get("next", "")}


def kinds(wb):
    ws = wb["スクリーニング"]
    return {ws.cell(r, 1).value: ws.cell(r, 3).value for r in range(C.FIRST_ROW, C.FIRST_ROW + 34)}


def add_sheet(wb, name, title, note, header, rows):
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=12)
    ws["A2"] = note
    for c, h in enumerate(header, 1):
        ws.cell(4, c, h).font = Font(bold=True)
    for r, row in enumerate(rows, 5):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v).alignment = Alignment(wrap_text=True, vertical="top")
    for c in range(1, len(header) + 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = 14 if c == 1 else 36
    ws.freeze_panes = "B5"
    return ws


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
    all_done = len(done) == len(C.IDS)
    for k, i in enumerate(C.IDS):
        r = C.FIRST_ROW + k
        assert scr.cell(r, 1).value == i and cmp_.cell(r, 1).value == i, (i, r)
        if i not in final:
            continue
        v = cells_for(i, kind[i], first, final, quality, xconf)
        for col in ("D", "G", "H", "I", "J"):
            if v[col] != "":
                scr[f"{col}{r}"] = v[col]
        if all_done:  # 『AI判定比較』は 34 件の判定がすべて終わってから（シートの逐語）
            cmp_[f"D{r}"] = v["human_use"]
            cmp_[f"F{r}"] = f"{v['reason']} ／ 基準の版: {CRITERIA_VERSION}".strip(" ／")
            cmp_[f"G{r}"] = f"次の作業: {v['next']}（最終合意は判定者 2 の後）" if v["next"] else "（最終合意は判定者 2 の後）"
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
        ("記録", "質問と答えの逐語は repo の .steering/20261001-ai-fatigue-34-screening/screening-log.jsonl。"),
        ("進み具合", f"判定済み {len(done)} / 34 件" + ("" if all_done else "（『AI判定比較』は 34 件の後に記入する）")),
    ]
    add_sheet(wb, C.ADDED_PREFIX + "はじめに", "判定者 1 の記入｜何をしたか", "このシートは判定者 1 が足した。", ["項目", "説明"], intro)
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
    fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=os.path.dirname(C.COPY_ARCHIVE), prefix=".tmp-")
    os.close(fd)
    build(tmp)
    if dry:
        print("dry-run ok", tmp)
        return
    shutil.copyfile(C.COPY_DOWNLOADS, C.COPY_DOWNLOADS + ".bak-" + last[:12])
    shutil.copyfile(tmp, C.COPY_DOWNLOADS)
    os.replace(tmp, C.COPY_ARCHIVE)
    new = C.sha256(C.COPY_ARCHIVE)
    if C.sha256(C.COPY_DOWNLOADS) != new:
        sys.exit("archive と Downloads の写しが合わない")
    with open(C.COPY_SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write(new + "\n")
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
