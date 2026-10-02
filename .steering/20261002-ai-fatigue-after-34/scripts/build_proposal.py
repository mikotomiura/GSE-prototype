"""提案のドキュメント v1 を作る（design.md §8）。

1. 付録（<!-- appendix:begin --> 〜 <!-- appendix:end -->）を、34 件の写しと追加候補の表から作り直して原稿に書き戻す。
2. 原稿（Markdown の小さな部分集合: # / ## / ### 見出し・段落・「- 」の箇条・| の表・**太字**・<!-- --> は飛ばす）から .docx を作る。
3. archive と Downloads に同じものを置き、SHA-256 を archive/proposal-sha256.txt に記録する。
★ Downloads の .docx が記録と違えば止まる（研究者に渡す前に手で直された可能性）。
使い方: python build_proposal.py [--dry-run]
"""
import datetime
import os
import re
import shutil
import sys
import tempfile
import unicodedata

import openpyxl
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

import common as C

MD = os.path.join(C.TASK, "proposal", "proposal-v1.md")
DOCX_NAME = "AI疲労DB_判定者1からの提案_v1.docx"
DOCX_ARCHIVE = os.path.join(C.TASK, "archive", DOCX_NAME)
DOCX_DOWNLOADS = os.path.join(C.DOWNLOADS, DOCX_NAME)
SHA_RECORD = os.path.join(C.TASK, "archive", "proposal-sha256.txt")
BEGIN, END = "<!-- appendix:begin -->", "<!-- appendix:end -->"


def field(j, name):
    m = re.search(name + r": ([^／]+)", j or "")
    return m.group(1).strip() if m else ""


def short(t, n=60):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t if len(t) <= n else t[:n - 1] + "…"


def appendix():
    w = openpyxl.load_workbook(C.COPY34_ARCHIVE, read_only=True)["スクリーニング"]
    a = ["## 9 付録", "", "### 9.1 34 件の判定（判定者 1）", "",
         "| ID | 題名（短縮） | 判定者1 | 用途 | 材料 |", "|---|---|---|---|---|"]
    for r in w.iter_rows(min_row=5, max_row=38, values_only=True):
        a.append(f"| {r[0]} | {short(r[1]).replace('|', '／')} | {r[3]} | {field(r[9], '用途')} | {field(r[9], '材料')} |")
    c = openpyxl.load_workbook(C.CAND_ARCHIVE, read_only=True)["スクリーニング"]
    a += ["", "### 9.2 追加候補で判定した記録（判定者 1）", "",
          "| ID | 題名（短縮） | 判定者1 | 用途 | 材料 | AI の判定 |", "|---|---|---|---|---|---|"]
    for r in c.iter_rows(min_row=5, values_only=True):
        if r[0] is None:
            break
        if r[3] != "未判定":
            ai = "Claude 版" if "AI の判定: Claude 版" in (r[9] or "") else "なし"
            a.append(f"| {r[0]} | {short(r[1]).replace('|', '／')} | {r[3]} | {field(r[9], '用途')} | {field(r[9], '材料')} | {ai} |")
    return "\n".join(a)


def compose_md():
    """原稿の付録を作り直した文字列（★ ここでは書き戻さない。dry-run・止まる判定の前に原稿を変えない・判断 11）。"""
    s = open(MD, encoding="utf-8").read()
    i, j = s.index(BEGIN), s.index(END)
    return s, s[:i + len(BEGIN)] + "\n" + appendix() + "\n" + s[j:]


def write_md(old, new):
    if new != old:
        with open(MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)


def add_runs(p, text):
    for k, part in enumerate(re.split(r"\*\*", text)):
        if part:
            run = p.add_run(part)
            run.bold = (k % 2 == 1)


def set_font(doc):
    st = doc.styles["Normal"]
    st.font.name = "Yu Gothic"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")


def blocks(md):
    """Markdown を (種類, 中身) の列にする。種類: h1/h2/h3/p/li/table。"""
    out, table = [], []
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r"-+", c) for c in cells):
                table.append(cells)
            continue
        if table:
            out.append(("table", table))
            table = []
        if not line.strip() or line.strip().startswith("<!--"):
            continue
        if line.startswith("### "):
            out.append(("h3", line[4:]))
        elif line.startswith("## "):
            out.append(("h2", line[3:]))
        elif line.startswith("# "):
            out.append(("h1", line[2:]))
        elif line.startswith("- "):
            out.append(("li", line[2:]))
        else:
            out.append(("p", line))
    if table:
        out.append(("table", table))
    return out


def disp_width(s):
    """表示幅（全角・広い文字・曖昧幅 = 2、ほか = 1）。**太字**の記号は数えない。
    ★ 曖昧幅（…・→・’ など）は日本語のフォントで全角に描かれる（code-reviewer・判断 11）。"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("F", "W", "A") else 1 for ch in s.replace("**", ""))


TABLE_CM, UNIT_CM, PAD_CM, SHORT = 16.0, 0.2, 0.5, 10  # 表の幅・表示幅 1 あたり・セルの余白・短い列の上限（表示幅）


def column_widths(x):
    """表の列の幅。短い列（最も長いセルの表示幅が SHORT の 2 倍以下: 番号・ID・判定・用途・材料）は中身が 1〜2 行に収まる幅を cm で取り、
    残りを長い列に、中身の平均の表示幅（8〜40 に丸める）で配る。
    ★ 比率だけで配ると本文の列に押されて「S15-23」「Claude 版」「番号」が折り返した（2026-10-02 に PDF で確かめた・判断 10）。"""
    ncol = len(x[0])
    mean = [sum(disp_width(row[j]) for row in x) / len(x) for j in range(ncol)]
    longest = [max(disp_width(row[j]) for row in x) for j in range(ncol)]
    short = [lg <= 2 * SHORT for lg in longest]
    # 表示幅が SHORT 以下は 1 行、2 倍以下は 2 行に収まる幅（「題名と書誌だけ」が 4 行に割れた）
    fixed = [(lg if lg <= SHORT else -(-lg // 2)) * UNIT_CM + PAD_CM for lg in longest]
    rest = TABLE_CM - sum(f for f, s in zip(fixed, short) if s)
    weight = [min(max(m, 8.0), 40.0) for m in mean]
    wsum = sum(w for w, s in zip(weight, short) if not s)
    if not wsum or rest < 4.0:  # 長い列が無い・短い列だけで埋まる → 全部を中身の比で配る
        weight = [min(max(m, 8.0), 40.0) if not s else f / UNIT_CM for m, s, f in zip(mean, short, fixed)]
        return [int(Cm(TABLE_CM) * w / sum(weight)) for w in weight]
    return [int(Cm(fixed[j] if short[j] else rest * weight[j] / wsum)) for j in range(ncol)]


def build_docx(md, dst):
    doc = Document()
    set_font(doc)
    for kind, x in blocks(md):
        if kind == "h1":
            h = doc.add_heading(x, level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif kind in ("h2", "h3"):
            doc.add_heading(x, level=1 if kind == "h2" else 2)
        elif kind == "li":
            add_runs(doc.add_paragraph(style="List Bullet"), x)
        elif kind == "p":
            add_runs(doc.add_paragraph(), x)
        else:
            t = doc.add_table(rows=len(x), cols=len(x[0]))
            t.style = "Table Grid"
            t.autofit = False
            for j, w in enumerate(column_widths(x)):
                t.columns[j].width = w  # ★ 表の列の定義（gridCol）。LibreOffice などはこちらを見る
                for i in range(len(x)):
                    t.cell(i, j).width = w
            for i, row in enumerate(x):
                for j, cell in enumerate(row):
                    t.cell(i, j).text = ""
                    add_runs(t.cell(i, j).paragraphs[0], cell)
                    if i == 0:
                        for run in t.cell(i, j).paragraphs[0].runs:
                            run.bold = True
            doc.add_paragraph()
    # ★ 雛形の属性（作成日 2013 年・「generated by python-docx」）を残さない（security-checker・判断 11）
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)
    cp = doc.core_properties
    cp.author = cp.last_modified_by = "判定者 1"
    cp.title = "AI 疲労の文献 DB：判定者 1 からの報告と提案（v1）"
    cp.comments = cp.subject = cp.keywords = cp.category = ""
    cp.created = cp.modified = now
    cp.revision = 1
    doc.save(dst)


def main(dry):
    old_md, md = compose_md()
    if dry:
        fd, tmp = tempfile.mkstemp(suffix=".docx", prefix="proposal-dry-")
        os.close(fd)
        build_docx(md, tmp)
        print("dry-run ok（repo の外・原稿は書き戻していない）", tmp)
        return
    # ★ 追加候補の表（build_candidates.py）と同じ守り: 記録と違えば・記録があるのに無ければ止まる・置き換えの直前に再照合・
    #   Downloads は退避して置き換え、archive の置き換えに失敗したら戻す（Codex・code-reviewer・判断 11）
    last = open(SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(SHA_RECORD) else None
    for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):
        if os.path.exists(p) and C.sha256(p) != last:
            sys.exit(f".docx が最後に書いたものと違う（手で直された可能性・止まって聞く）: {p}")
        if not os.path.exists(p) and last is not None:
            sys.exit(f"記録があるのに .docx が無い（止まって聞く）: {p}")
    # ★ 順: 一時ファイルに作る → 置き換えの直前に両方を再照合（存在と SHA）→ Downloads を退避（Downloads の外）して置き換え →
    #   archive を置き換え（失敗したら Downloads を戻す）→ 原稿を書き戻す → SHA を記録 → 退避を消す（Codex・code-reviewer・判断 12）。
    #   一時ファイルは .part（途中で止まっても .docx として開けない・security-checker）
    tmps, bak = [], None
    try:
        fd, tmp_a = tempfile.mkstemp(suffix=".part", dir=os.path.dirname(DOCX_ARCHIVE), prefix=".tmp-")
        os.close(fd)
        tmps.append(tmp_a)
        build_docx(md, tmp_a)
        fd, tmp_d = tempfile.mkstemp(suffix=".part", dir=C.DOWNLOADS, prefix=".tmp-proposal-")
        os.close(fd)
        tmps.append(tmp_d)
        shutil.copyfile(tmp_a, tmp_d)
        for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):  # ★ 置き換えの直前にもう一度（作っている間に保存・削除されていないか）
            if (os.path.exists(p) and C.sha256(p) != last) or (not os.path.exists(p) and last is not None):
                sys.exit(f".docx が最後に書いたものと違う・無い（止まって聞く）: {p}")
        if os.path.exists(DOCX_DOWNLOADS):
            fd, bak = tempfile.mkstemp(suffix=".part", prefix="proposal-bak-")  # ★ 研究者に渡すフォルダに古い版を残さない
            os.close(fd)
            shutil.copyfile(DOCX_DOWNLOADS, bak)
        os.replace(tmp_d, DOCX_DOWNLOADS)
        try:
            os.replace(tmp_a, DOCX_ARCHIVE)
        except OSError:
            if bak:
                shutil.copyfile(bak, DOCX_DOWNLOADS)
            else:
                os.remove(DOCX_DOWNLOADS)
            raise
        write_md(old_md, md)  # ★ 2 つの置き換えが済んでから原稿を書き戻す
    finally:
        for t in tmps:
            if os.path.exists(t):
                os.remove(t)
    new = C.sha256(DOCX_ARCHIVE)
    if C.sha256(DOCX_DOWNLOADS) != new:
        sys.exit("archive と Downloads の .docx が合わない")
    with open(SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write(new + "\n")
    if bak and os.path.exists(bak):
        os.remove(bak)
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
