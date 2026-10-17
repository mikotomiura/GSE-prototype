"""Make the Word copy of the draft (main.docx) with pandoc, then fix the tables.

pandoc reads a tabularx table as equal columns without rules or a table number, so in Word a seven-column table
breaks words inside the cell ("Statemen-t"). This script:
- sizes each column from its text (never narrower than the longest word),
- draws the top rule, the rule under the header and the bottom rule (as booktabs does in the PDF),
- puts "Table N." and "Figure N." before each caption, numbered as LaTeX numbers them (one per \\caption inside a
  table or a figure environment),
- sets the table text in 10 pt, or in 8 or 7 pt when the longest words of the columns do not fit at 10 pt,
- sets the page to A4 and puts the tables that are landscape in the PDF on landscape pages of their own.
Figure 1 (figure1.tex) is built first and converted to PNG, because Word cannot show the PDF.

Run from this directory: python3 make_docx.py
"""

import re
import subprocess
import zipfile
from pathlib import Path
from xml.sax.saxutils import unescape

HERE = Path(__file__).resolve().parent
TEX = HERE / "main.tex"
TABLES = HERE / "tables.tex"
OUT = HERE / "main.docx"
# A4 with 1-inch margins, in twips; the text width is what a table is spread over.
PAGE_W, PAGE_H, MARGIN = 11906, 16838, 1440
TEXT_WIDTH = PAGE_W - 2 * MARGIN
LANDSCAPE_TEXT_WIDTH = PAGE_H - 2 * MARGIN
# Table text sizes tried in turn (half-points, twips per character as an upper estimate): 10 pt, 8 pt, 7 pt.
SIZES = [(20, 115), (16, 92), (14, 80)]
CELL_MARGINS = 480  # twips: the left and right cell margins (108 each) and room for wide letters (M, O)
RULE = '<w:{0} w:val="single" w:sz="8" w:space="0" w:color="000000"/>'


def table_numbers(tex):
    """The number LaTeX gives each table caption, in order, and whether the table is inside a landscape environment."""
    tables, counter = [], 0
    for m in re.finditer(r"\\setcounter\{table\}\{(\d+)\}|\\begin\{table\}.*?\\caption\{", tex, flags=re.S):
        if m.group(1) is not None:
            counter = int(m.group(1))
        else:
            counter += 1
            before = tex[: m.start()]
            tables.append((counter, before.count("\\begin{landscape}") > before.count("\\end{landscape}")))
    return tables


def section(landscape):
    """Section properties that end a section: A4, portrait or landscape."""
    w, h = (PAGE_H, PAGE_W) if landscape else (PAGE_W, PAGE_H)
    orient = ' w:orient="landscape"' if landscape else ""
    return (f'<w:sectPr><w:pgSz w:w="{w}" w:h="{h}"{orient}/><w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" '
            f'w:bottom="{MARGIN}" w:left="{MARGIN}" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')


def cell_texts(tc):
    return unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", tc)))


def column_widths(rows, char, text_width):
    """Give each column room for its longest word, then share the rest of the width by the length of its text.
    If the longest words alone do not fit, the columns are scaled down and fits is False."""
    ncol = max(len(r) for r in rows)
    floors, extras = [], []
    for i in range(ncol):
        texts = [cell_texts(r[i]) for r in rows if i < len(r)]
        longest_word = max((len(w) for t in texts for w in t.split()), default=1)
        longest_cell = max((len(t) for t in texts), default=1)
        floors.append(longest_word * char + CELL_MARGINS)
        extras.append(max(longest_cell - longest_word, 0))
    spare = text_width - sum(floors)
    if spare < 0:
        return [round(f * text_width / sum(floors)) for f in floors], False
    return [round(f + spare * e / (sum(extras) or 1)) for f, e in zip(floors, extras)], True


def fix_table(tbl, text_width):
    rows = [re.findall(r"<w:tc>.*?</w:tc>", tr, flags=re.S) for tr in re.findall(r"<w:tr>.*?</w:tr>", tbl, flags=re.S)]
    for size, char in SIZES:  # the first size at which every column fits; otherwise the smallest, scaled
        widths, fits = column_widths(rows, char, text_width)
        if fits:
            break
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"
    tbl = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", grid, tbl, flags=re.S)
    borders = "<w:tblBorders>" + RULE.format("top") + RULE.format("bottom") + "</w:tblBorders>"
    tbl = re.sub(r'<w:tblW [^>]*/>', '<w:tblW w:type="pct" w:w="5000"/><w:tblLayout w:type="fixed"/>' + borders, tbl)

    trs = re.findall(r"<w:tr>.*?</w:tr>", tbl, flags=re.S)
    for r, tr in enumerate(trs):
        new_tr = tr
        for c, tc in enumerate(rows[r]):
            pr = f'<w:tcW w:type="dxa" w:w="{widths[c]}"/>'
            if r == 0:
                pr += "<w:tcBorders>" + RULE.format("bottom") + "</w:tcBorders>"
            new_tr = new_tr.replace(tc, tc.replace("<w:tcPr />", f"<w:tcPr>{pr}</w:tcPr>", 1), 1)
        tbl = tbl.replace(tr, new_tr, 1)
    if size != SIZES[0][0]:
        tbl = tbl.replace('<w:pStyle w:val="Compact" />', f'<w:pStyle w:val="Compact" /><w:rPr><w:sz w:val="{size}"/></w:rPr>')
        tbl = re.sub(r"<w:r>(?!<w:rPr>)", f'<w:r><w:rPr><w:sz w:val="{size}"/></w:rPr>', tbl)
    return tbl


def main():
    subprocess.run(["latexmk", "-pdf", "-quiet", "figure1.tex"], cwd=HERE, check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "200", "-png", "-singlefile", "figure1.pdf", "figure1"], cwd=HERE, check=True)
    subprocess.run(["pandoc", "main.tex", "--citeproc", "--bibliography=refs.bib", "--default-image-extension=png",
                    "-o", str(OUT)], cwd=HERE, check=True)
    tex_all = TEX.read_text(encoding="utf-8") + TABLES.read_text(encoding="utf-8")
    tables = table_numbers(tex_all)
    numbers = [n for n, _ in tables]
    with zipfile.ZipFile(OUT) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = parts["word/document.xml"].decode("utf-8")

    captions = iter(numbers)

    def number_caption(m):
        return m.group(1) + f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Table {next(captions)}. </w:t></w:r>'

    doc, n_captions = re.subn(r'(<w:p><w:pPr><w:pStyle w:val="TableCaption" /></w:pPr>)', number_caption, doc)

    figures = iter(range(1, 1 + len(re.findall(r"\\begin\{figure\}.*?\\caption\{", tex_all, flags=re.S))))
    n_figures_tex = len(re.findall(r"\\begin\{figure\}.*?\\caption\{", tex_all, flags=re.S))

    def number_figure(m):
        return m.group(1) + f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Figure {next(figures)}. </w:t></w:r>'

    doc, n_figures = re.subn(r'(<w:p><w:pPr><w:pStyle w:val="ImageCaption" /></w:pPr>)', number_figure, doc)
    if n_figures != n_figures_tex:
        raise SystemExit(f"figure captions in main.tex: {n_figures_tex}, in docx: {n_figures}")
    landscape = iter(flag for _, flag in tables)

    def fix(m):
        flag = next(landscape)
        tbl = fix_table(m.group(0), LANDSCAPE_TEXT_WIDTH if flag else TEXT_WIDTH)
        return f"<!--landscape-->{tbl}" if flag else tbl

    doc, n_tables = re.subn(r"<w:tbl>.*?</w:tbl>", fix, doc, flags=re.S)
    if n_captions != len(numbers) or n_tables != len(numbers):
        raise SystemExit(f"captions in main.tex: {len(numbers)}, in docx: {n_captions}, tables in docx: {n_tables}")

    # A landscape table, with its caption before it and its note after it, gets a section of its own: the paragraph
    # before the caption ends the portrait section, and an empty paragraph after the note ends the landscape one.
    caption = r'<w:p><w:pPr><w:pStyle w:val="TableCaption" /></w:pPr>(?:(?!</w:p>).)*</w:p>\s*'
    note = r'(?:<w:p>(?:(?!</w:p>).)*</w:p>)?'
    doc, n_landscape = re.subn(
        rf"({caption})<!--landscape-->(<w:tbl>.*?</w:tbl>\s*{note})",
        lambda m: f"<w:p><w:pPr>{section(False)}</w:pPr></w:p>{m.group(1)}{m.group(2)}"
                  f"<w:p><w:pPr>{section(True)}</w:pPr></w:p>",
        doc, flags=re.S)
    if n_landscape != sum(flag for _, flag in tables):
        raise SystemExit(f"landscape tables in main.tex: {sum(flag for _, flag in tables)}, placed: {n_landscape}")
    doc = re.sub(r"<w:sectPr>(?:(?!<w:sectPr>).)*</w:sectPr>\s*</w:body>", section(False) + "</w:body>", doc, flags=re.S)

    parts["word/document.xml"] = doc.encode("utf-8")
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    print(f"{OUT.name}: {n_tables} table(s) fixed, numbered {numbers}; {n_figures} figure caption(s) numbered")


if __name__ == "__main__":
    main()
