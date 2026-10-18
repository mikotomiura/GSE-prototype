"""Make the Word copy of a Japanese guide (coauthor-guide.md) with pandoc, then fix its tables (decision 46).

pandoc writes a table with no rules and equal columns, so in Word a four-column table of Japanese text reads as
text broken into narrow strips. This script:
- sizes each column by the display width of its text (a full-width character counts 2, others 1): every column
  gets at least MIN_COL characters, and the rest of the width is shared by the length of its longest cell, capped
  at CAP characters so that one long column does not squeeze the others;
- draws all rules (a grid) and shades the header row;
- sets the table text in 9 pt;
- sets the page to A4 with 20 mm margins, and the default font to Hiragino Sans (Japanese).

Run: python3 make_guide_docx.py <in.md> <out.docx>
"""

import re
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from xml.sax.saxutils import unescape

PAGE_W, PAGE_H, MARGIN = 11906, 16838, 1134   # A4 in twips, 20 mm margins
TEXT_WIDTH = PAGE_W - 2 * MARGIN
MIN_COL, CAP = 8, 40                          # in display units (a full-width character = 2)
SIZE = 18                                     # half-points: 9 pt
RULE = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="808080"/>'


def width(text):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def cell_text(tc):
    return unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", tc)))


def column_widths(rows):
    ncol = max(len(r) for r in rows)
    need = []
    for i in range(ncol):
        longest = max((width(cell_text(r[i])) for r in rows if i < len(r)), default=1)
        need.append(min(max(longest, MIN_COL), CAP))
    total = sum(need)
    return [round(TEXT_WIDTH * n / total) for n in need]


def fix_table(tbl):
    rows = [re.findall(r"<w:tc>.*?</w:tc>", tr, flags=re.S) for tr in re.findall(r"<w:tr>.*?</w:tr>", tbl, flags=re.S)]
    widths = column_widths(rows)
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"
    tbl = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", grid, tbl, flags=re.S)
    borders = "<w:tblBorders>" + "".join(RULE.format(s) for s in
                                          ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"
    tbl = re.sub(r"<w:tblW [^>]*/>", f'<w:tblW w:type="dxa" w:w="{TEXT_WIDTH}"/>' + borders, tbl, count=1)
    trs = re.findall(r"<w:tr>.*?</w:tr>", tbl, flags=re.S)
    for r, tr in enumerate(trs):
        new_tr = tr
        for c, tc in enumerate(rows[r]):
            pr = f'<w:tcW w:type="dxa" w:w="{widths[c]}"/>'
            if r == 0:
                pr += '<w:shd w:val="clear" w:color="auto" w:fill="E7EEF6"/>'
            new_tc = re.sub(r"<w:tcPr\s*/>|<w:tcPr>.*?</w:tcPr>", f"<w:tcPr>{pr}</w:tcPr>", tc, count=1, flags=re.S)
            new_tr = new_tr.replace(tc, new_tc, 1)
        tbl = tbl.replace(tr, new_tr, 1)
    # 9 pt for every run in the table (bold header runs keep their bold)
    tbl = re.sub(r"<w:r>(?!<w:rPr>)", f'<w:r><w:rPr><w:sz w:val="{SIZE}"/><w:szCs w:val="{SIZE}"/></w:rPr>', tbl)
    tbl = re.sub(r"<w:r><w:rPr>(?!<w:sz )", f'<w:r><w:rPr><w:sz w:val="{SIZE}"/><w:szCs w:val="{SIZE}"/>', tbl)
    return tbl, widths


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "raw.docx"
        subprocess.run(["pandoc", str(src), "-o", str(raw)], check=True)
        zin = zipfile.ZipFile(raw)
        doc = zin.read("word/document.xml").decode("utf-8")
        report = []

        def fix(m):
            t, w = fix_table(m.group(0))
            report.append(w)
            return t
        doc = re.sub(r"<w:tbl>.*?</w:tbl>", fix, doc, flags=re.S)
        sect = (f'<w:sectPr><w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/><w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" '
                f'w:bottom="{MARGIN}" w:left="{MARGIN}" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')
        if "<w:sectPr" in doc:
            doc = re.sub(r"<w:sectPr.*?</w:sectPr>|<w:sectPr\s*/>", sect, doc, count=1, flags=re.S)
        else:
            doc = doc.replace("</w:body>", sect + "</w:body>")
        styles = zin.read("word/styles.xml").decode("utf-8")
        # Japanese text in a font that Word and LibreOffice on macOS both have (pandoc names none)
        font = '<w:rFonts w:ascii="Hiragino Sans" w:hAnsi="Hiragino Sans" w:eastAsia="Hiragino Sans" w:cs="Hiragino Sans"/>'
        styles = re.sub(r"(<w:rPrDefault>\s*<w:rPr>)\s*<w:rFonts[^>]*/>", r"\1" + font, styles, count=1)
        styles = re.sub(r'w:(ascii|hAnsi|eastAsia|cs)Theme="[^"]*"\s*', "", styles)   # theme fonts would override it
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = (doc.encode("utf-8") if item.filename == "word/document.xml" else
                        styles.encode("utf-8") if item.filename == "word/styles.xml" else zin.read(item.filename))
                zout.writestr(item, data)
    print(f"wrote {out}: {len(report)} table(s), column widths (twips) {report}")


if __name__ == "__main__":
    main()
