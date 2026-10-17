"""Make the Word copy of the draft (main.docx) with pandoc, then fix the tables.

pandoc reads a tabularx table as equal columns without rules or a table number, so in Word a seven-column table
breaks words inside the cell ("Statemen-t"). This script:
- sizes each column from its text (never narrower than the longest word),
- draws the top rule, the rule under the header and the bottom rule (as booktabs does in the PDF),
- puts "Table N." before each caption, numbered as LaTeX numbers them (\\setcounter{table}, then one per \\caption).

Run from this directory: python3 make_docx.py
"""

import re
import subprocess
import zipfile
from pathlib import Path
from xml.sax.saxutils import unescape

HERE = Path(__file__).resolve().parent
TEX = HERE / "main.tex"
OUT = HERE / "main.docx"
TEXT_WIDTH = 9000  # twips; the width the table is spread over (100% of the text width in Word)
RULE = '<w:{0} w:val="single" w:sz="8" w:space="0" w:color="000000"/>'


def table_numbers(tex):
    """The number LaTeX gives each table caption, in order."""
    numbers, counter = [], 0
    for m in re.finditer(r"\\setcounter\{table\}\{(\d+)\}|\\caption\{", tex):
        if m.group(1) is not None:
            counter = int(m.group(1))
        else:
            counter += 1
            numbers.append(counter)
    return numbers


def cell_texts(tc):
    return unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", tc)))


def column_widths(rows):
    """Weight each column by its longest word, or by a share of its longest cell when that is larger."""
    ncol = max(len(r) for r in rows)
    weights = []
    for i in range(ncol):
        texts = [cell_texts(r[i]) for r in rows if i < len(r)]
        longest_word = max((len(w) for t in texts for w in t.split()), default=1)
        longest_cell = max((len(t) for t in texts), default=1)
        weights.append(max(longest_word + 3, 0.4 * longest_cell))  # +3 covers the cell margins
    total = sum(weights)
    return [round(TEXT_WIDTH * w / total) for w in weights]


def fix_table(tbl):
    rows = [re.findall(r"<w:tc>.*?</w:tc>", tr, flags=re.S) for tr in re.findall(r"<w:tr>.*?</w:tr>", tbl, flags=re.S)]
    widths = column_widths(rows)
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
    return tbl


def main():
    subprocess.run(["pandoc", "main.tex", "--citeproc", "--bibliography=refs.bib", "-o", str(OUT)], cwd=HERE, check=True)
    numbers = table_numbers(TEX.read_text(encoding="utf-8"))
    with zipfile.ZipFile(OUT) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    doc = parts["word/document.xml"].decode("utf-8")

    captions = iter(numbers)

    def number_caption(m):
        return m.group(1) + f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Table {next(captions)}. </w:t></w:r>'

    doc, n_captions = re.subn(r'(<w:p><w:pPr><w:pStyle w:val="TableCaption" /></w:pPr>)', number_caption, doc)
    doc, n_tables = re.subn(r"<w:tbl>.*?</w:tbl>", lambda m: fix_table(m.group(0)), doc, flags=re.S)
    if n_captions != len(numbers) or n_tables != len(numbers):
        raise SystemExit(f"captions in main.tex: {len(numbers)}, in docx: {n_captions}, tables in docx: {n_tables}")

    parts["word/document.xml"] = doc.encode("utf-8")
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    print(f"{OUT.name}: {n_tables} table(s) fixed, numbered {numbers}")


if __name__ == "__main__":
    main()
