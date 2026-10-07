#!/usr/bin/env python3
"""Count the pages of a built PDF on which text or a rule lies outside the page, where a reader cannot see it.

LaTeX does not always warn when a float is taller than the page: a sideways table set on a page of floats can run off
both edges of the paper and still give no overfull box. This script reads the PDF that the build wrote and reports
every page whose text (taken without clipping to the page) or drawn rules extend beyond the page by more than a
tolerance. It needs PyMuPDF; when PyMuPDF is not installed it says that the pages were not checked and exits with 3,
so that a missing tool is not read as a clean result.

usage: check_page_bounds.py <pdf> [<pdf> ...]
       check_page_bounds.py --selftest
"""
import sys

TOLERANCE = 1.0  # points; a glyph or a rule may touch the edge of the page


def outside(page, fitz):
    """The parts of a page that lie outside it: (kind, rectangle, text) for spans of text and for drawn paths. Text
    and paths come in the coordinates of the unrotated page, so they are compared with the crop box, not with
    page.rect, which a landscape page (pdflscape) turns."""
    area = page.cropbox + (-TOLERANCE, -TOLERANCE, TOLERANCE, TOLERANCE)
    found = []
    for block in page.get_text("dict", clip=fitz.INFINITE_RECT())["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                rect = fitz.Rect(span["bbox"])
                if span["text"].strip() and not area.contains(rect):
                    found.append(("text", rect, span["text"]))
    for path in page.get_drawings():
        rect = path["rect"]
        if not area.contains(rect):
            found.append(("rule", rect, ""))
    return found


def check(path, fitz):
    """Print one line per page with content outside it; return the number of such pages."""
    bad = 0
    with fitz.open(path) as doc:
        for number, page in enumerate(doc, 1):
            parts = outside(page, fitz)
            if parts:
                bad += 1
                kind, rect, text = parts[0]
                print("%s: page %d: %d parts outside the page, the first a %s at %s %s" % (
                    path, number, len(parts), kind, [round(v) for v in rect], text[:40]))
    return bad


def selftest(fitz):
    """A page with text inside it passes; text or a rule past an edge is found; a page with none is clean; a tall
    page turned to landscape with its content inside passes, and with content past its long edge is found; text
    wholly outside the page is found."""
    doc = fitz.open()
    inside = doc.new_page(width=200, height=200)
    inside.insert_text((20, 40), "inside")
    off_text = doc.new_page(width=200, height=200)
    off_text.insert_text((20, 40), "starts inside")
    off_text.insert_text((180, 80), "runs off the right edge")
    off_rule = doc.new_page(width=200, height=200)
    off_rule.draw_line((20, 100), (260, 100))
    doc.new_page(width=200, height=200)
    turned = doc.new_page(width=200, height=400)
    turned.insert_text((20, 380), "near the foot of the tall page")
    turned.set_rotation(90)
    turned_off = doc.new_page(width=200, height=400)
    turned_off.draw_line((20, 300), (20, 420))
    turned_off.set_rotation(90)
    # Text wholly past the edge, as a caption set beside a rotated page is: it is found only without clipping.
    off_whole = doc.new_page(width=200, height=200)
    off_whole.insert_text((-120, 60), "wholly outside")
    results = [len(outside(p, fitz)) for p in doc]
    ok = (results[0] == 0 and results[1] >= 1 and results[2] >= 1 and results[3] == 0 and results[4] == 0
          and results[5] >= 1 and results[6] >= 1)
    print("selftest %s (%s)" % ("OK" if ok else "FAILED", results))
    return 0 if ok else 1


def main(argv):
    try:
        import fitz
    except ImportError:
        print("check_page_bounds.py: pages not checked: PyMuPDF is not installed")
        return 3
    if argv == ["--selftest"]:
        return selftest(fitz)
    if not argv:
        print(__doc__.strip().splitlines()[-2])
        return 2
    total = 0
    for path in argv:
        n = check(path, fitz)
        print("%s: %d pages with content outside the page" % (path, n))
        total += n
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
