#!/usr/bin/env python3
"""Count the pages of a built PDF on which text or a rule lies outside the page, where a reader cannot see it, or
covers the page number.

LaTeX does not always warn when a float is taller than the page: a sideways table set on a page of floats can run off
both edges of the paper and still give no overfull box, and a long table can run into the foot of the page over the
page number. This script reads the PDF that the build wrote and reports every page whose text (taken without clipping
to the page) or drawn rules extend beyond the page by more than a tolerance, and every page whose number is covered by
other text or crossed by a rule. It needs PyMuPDF; when PyMuPDF is not installed, or a PDF cannot be read, it says
that the pages were not checked and exits with 3, so that a missing tool is not read as a clean result.

usage: check_page_bounds.py <pdf> [<pdf> ...]
       check_page_bounds.py --selftest
"""
import sys

TOLERANCE = 1.0  # points; a glyph or a rule may touch the edge of the page


def outside(page, fitz):
    """The parts of a page that lie outside it: (kind, rectangle, text) for spans of text and for drawn paths. Text
    and paths come in the coordinates of the unrotated page with the origin at the corner of the crop box, so they
    are compared with a rectangle of the crop box's size at the origin, not with page.rect, which a landscape page
    (pdflscape) turns, nor with page.cropbox, which keeps the box's offset."""
    box = page.cropbox
    area = fitz.Rect(0, 0, box.width, box.height) + (-TOLERANCE, -TOLERANCE, TOLERANCE, TOLERANCE)
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


def over_number(page, number, fitz):
    """Text or rules that cover the page number: (kind, rectangle, text). The page number is a span whose text is the
    number alone; something covers it when it overlaps at least a quarter of the span's area. A long table that runs
    into the foot of the page prints over the number while staying on the paper."""
    spans = [(fitz.Rect(s["bbox"]), s["text"])
             for b in page.get_text("dict", clip=fitz.INFINITE_RECT())["blocks"] for l in b.get("lines", [])
             for s in l["spans"] if s["text"].strip()]
    rules = [p["rect"] for p in page.get_drawings()]
    found = []
    for rect, text in spans:
        if text.strip() != str(number) or rect.is_empty:
            continue
        least = 0.25 * rect.get_area()
        for other, t in spans:
            if other != rect and (other & rect).get_area() >= least:
                found.append(("text", other, t))
        for other in rules:
            # A rule has no area, so it is widened by half a point and found when it crosses the number at all.
            if (fitz.Rect(other) + (-0.5, -0.5, 0.5, 0.5) & rect).get_area() > 0:
                found.append(("rule", other, ""))
    return found


def check(path, fitz):
    """Print one line per page with content outside it or over its number; return the numbers of such pages."""
    bad = covered = 0
    with fitz.open(path) as doc:
        for number, page in enumerate(doc, 1):
            for label, parts in (("outside the page", outside(page, fitz)),
                                 ("over the page number", over_number(page, number, fitz))):
                if not parts:
                    continue
                if label == "outside the page":
                    bad += 1
                else:
                    covered += 1
                kind, rect, text = parts[0]
                # ascii() keeps a dash or a ligature of the text from stopping the print on a narrow console encoding.
                print("%s: page %d: %d parts %s, the first a %s at %s %s" % (
                    path, number, len(parts), label, kind, [round(v) for v in rect], ascii(text[:40])))
    return bad, covered


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
    # A rule inside a turned page, beyond the width the turned page would have: it passes.
    turned_rule = doc.new_page(width=200, height=400)
    turned_rule.draw_line((20, 300), (20, 390))
    turned_rule.set_rotation(90)
    # Text wholly past the edge, as a caption set beside a rotated page is: it is found only without clipping.
    off_whole = doc.new_page(width=200, height=200)
    off_whole.insert_text((-120, 60), "wholly outside")
    # A crop box whose corner is not at the origin: content inside the box passes, content past its far edge is found.
    cropped = doc.new_page(width=300, height=300)
    cropped.insert_text((70, 240), "inside the box")
    cropped.draw_line((60, 230), (240, 230))
    cropped.set_cropbox(fitz.Rect(50, 50, 250, 250))
    cropped_off = doc.new_page(width=300, height=300)
    cropped_off.insert_text((70, 100), "inside the box")
    cropped_off.draw_line((60, 120), (280, 120))
    cropped_off.set_cropbox(fitz.Rect(50, 50, 250, 250))
    results = [len(outside(p, fitz)) for p in doc]
    ok = (results[0] == 0 and results[1] >= 1 and results[2] >= 1 and results[3] == 0 and results[4] == 0
          and results[5] >= 1 and results[6] == 0 and results[7] >= 1 and results[8] == 0 and results[9] >= 1)
    # The page number: alone it passes; text printed over it or a rule across it is found; the same digit inside a
    # line of text, next to other words, is not taken for a cover.
    numbered = fitz.open()
    for _ in range(5):
        numbered.new_page(width=300, height=400)
    numbered[0].insert_text((150, 380), "1")
    numbered[0].insert_text((40, 100), "a line of text above")
    numbered[1].insert_text((150, 380), "2")
    numbered[1].insert_text((140, 381), "text printed over it")
    numbered[2].insert_text((150, 380), "3")
    numbered[2].draw_line((100, 377), (200, 377))
    numbered[3].insert_text((40, 100), "in 4 of the cases")
    numbered[4].insert_text((150, 380), "5")
    numbered[4].insert_text((152, 300), "text well above the number")
    covers = [len(over_number(p, n, fitz)) for n, p in enumerate(numbered, 1)]
    ok = ok and covers[0] == 0 and covers[1] >= 1 and covers[2] >= 1 and covers[3] == 0 and covers[4] == 0
    print("selftest %s (%s; %s)" % ("OK" if ok else "FAILED", results, covers))
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
    total, unchecked = 0, False
    for path in argv:
        # Every PDF gets one summary line, also when it cannot be read.
        try:
            n, covered = check(path, fitz)
        except Exception as e:  # a missing or unreadable PDF, or an older PyMuPDF
            print("%s: pages not checked: %s" % (path, type(e).__name__))
            unchecked = True
            continue
        print("%s: %d pages with content outside the page, %d pages with content over the page number" % (
            path, n, covered))
        total += n + covered
    return 3 if unchecked else (1 if total else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
