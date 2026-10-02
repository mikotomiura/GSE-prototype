"""提案のドキュメント v1 を作る（design.md §8）。

1. 付録（<!-- appendix:begin --> 〜 <!-- appendix:end -->）を、34 件の写しと追加候補の表から作り直して原稿に書き戻す。
2. 原稿（Markdown の小さな部分集合: # / ## / ### 見出し・段落・「- 」の箇条・| の表・**太字**・<!-- --> は飛ばす）から .docx を作る。
3. archive と Downloads に同じものを置き、SHA-256 を archive/proposal-sha256.txt に記録する。
★ Downloads の .docx が記録と違えば止まる（研究者に渡す前に手で直された可能性）。
使い方: python build_proposal.py [--dry-run]
"""
import os
import re
import shutil
import sys
import tempfile

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


def refresh_appendix():
    s = open(MD, encoding="utf-8").read()
    i, j = s.index(BEGIN), s.index(END)
    s2 = s[:i + len(BEGIN)] + "\n" + appendix() + "\n" + s[j:]
    if s2 != s:
        with open(MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(s2)
    return s2


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
            # 列の幅は中身の平均の長さで配分する（短い列〈番号・ID〉を細く・本文の列を広く）
            ncol = len(x[0])
            mean = [sum(len(row[j]) for row in x) / len(x) for j in range(ncol)]
            weight = [min(max(m, 6.0), 40.0) for m in mean]
            total = Cm(16.0)
            for j in range(ncol):
                w = int(total * weight[j] / sum(weight))
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
    doc.core_properties.author = "判定者 1"
    doc.core_properties.title = "AI 疲労の文献 DB：判定者 1 からの報告と提案（v1）"
    doc.save(dst)


def main(dry):
    md = refresh_appendix()
    if dry:
        fd, tmp = tempfile.mkstemp(suffix=".docx", prefix="proposal-dry-")
        os.close(fd)
        build_docx(md, tmp)
        print("dry-run ok（repo の外）", tmp)
        return
    last = open(SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(SHA_RECORD) else None
    for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):
        if os.path.exists(p) and C.sha256(p) != last:
            sys.exit(f".docx が最後に書いたものと違う（手で直された可能性・止まって聞く）: {p}")
    fd, tmp = tempfile.mkstemp(suffix=".docx", dir=os.path.dirname(DOCX_ARCHIVE), prefix=".tmp-")
    os.close(fd)
    try:
        build_docx(md, tmp)
        shutil.copyfile(tmp, DOCX_DOWNLOADS + ".tmp")
        os.replace(DOCX_DOWNLOADS + ".tmp", DOCX_DOWNLOADS)
        os.replace(tmp, DOCX_ARCHIVE)
    finally:
        for t in (tmp, DOCX_DOWNLOADS + ".tmp"):
            if os.path.exists(t):
                os.remove(t)
    new = C.sha256(DOCX_ARCHIVE)
    if C.sha256(DOCX_DOWNLOADS) != new:
        sys.exit("archive と Downloads の .docx が合わない")
    with open(SHA_RECORD, "w", encoding="utf-8", newline="\n") as f:
        f.write(new + "\n")
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
