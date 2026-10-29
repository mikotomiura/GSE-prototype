"""The workbook in which author 1 marks the AI screener's quotations as scale items or not, before `release`
(GSRR-41). `release` reads ~/TRACE-screening/quote-review.csv and needs scale_item to be yes or no on every row; this
script only moves that column between the CSV and a workbook that is easier to fill. It never fills a value itself.

  make  <quote-review.csv> <book.xlsx>   a workbook with the flagged rows first, a yes/no list in scale_item and the
                                         CSV's row number in the first column; refuses to overwrite an existing book
  back  <quote-review.csv> <book.xlsx>   writes the workbook's scale_item into the CSV, after checking that every row
                                         of the CSV is in the book once, with the same key and text; keeps a copy of the
                                         CSV beside it first; blank cells stay blank (release will stop on them)

Run with the TRACE environment (openpyxl): cd ~/TRACE && uv run python <this script> make|back <csv> <xlsx>
The workbook holds quotations from abstracts and full texts: keep it outside the repositories and off shared drives."""
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

COLS = ["batch", "record_id", "stage", "field", "where", "text", "flag", "scale_item"]
KEY = ("batch", "record_id", "stage", "field")
SHEET = "quotes"
HEAD = ["row"] + COLS + ["memo"]
INTRO = [
    "Mark every row in scale_item: yes or no.",
    "yes = the text reproduces, in whole or in part, the wording of an item of a questionnaire or scale "
    "(registration GSRR-41). Rows marked yes are removed from the released files.",
    "The flag column 'check' is a script's guess (place or wording looks like an item); it decides nothing.",
    "Rows with flag 'check' come first. Do not change any column other than scale_item and memo, "
    "and do not delete or reorder rows.",
]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames != COLS:
            sys.exit(f"{path}: columns {r.fieldnames}, expected {COLS}")
        return list(r)


def key(r):
    return tuple(str(r[k]) for k in KEY)


def make(csv_path, book_path):
    rows = read_csv(csv_path)
    if len({key(r) for r in rows}) != len(rows):
        sys.exit(f"{csv_path}: a key (batch, record_id, stage, field) appears twice")
    if Path(book_path).exists():
        sys.exit(f"{book_path} exists; author 1 may have filled it. Move it away to make a new one")
    order = sorted(range(len(rows)), key=lambda i: (rows[i]["flag"] != "check", i))
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET
    ws.append(HEAD)
    for i in order:
        r = rows[i]
        ws.append([i + 2] + [r[c] for c in COLS] + [""])  # the CSV's line number, with the header as line 1
    for c in ws[1]:
        c.font = Font(bold=True)
    widths = {"A": 7, "B": 9, "C": 10, "D": 6, "E": 8, "F": 22, "G": 80, "H": 7, "I": 11, "J": 30}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2, min_col=6, max_col=7):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    flagged = PatternFill("solid", fgColor="FFF2CC")
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 8).value == "check":
            for c in range(1, len(HEAD) + 1):
                ws.cell(r, c).fill = flagged
    dv = DataValidation(type="list", formula1='"yes,no"', allow_blank=True, showErrorMessage=True,
                        errorTitle="scale_item", error="yes or no")
    ws.add_data_validation(dv)
    dv.add(f"I2:I{ws.max_row}")
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    info = wb.create_sheet("how to")
    for line in INTRO:
        info.append([line])
    info.column_dimensions["A"].width = 120
    wb.save(book_path)
    print(f"wrote {book_path}: {len(rows)} rows, {sum(r['flag'] == 'check' for r in rows)} flagged first")


def back(csv_path, book_path):
    rows = read_csv(csv_path)
    ws = load_workbook(book_path)[SHEET]
    head = [c.value for c in ws[1]]
    if head != HEAD:
        sys.exit(f"{book_path}: header {head}, expected {HEAD}")
    seen = {}
    for n, cells in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if all(v in (None, "") for v in cells):
            continue
        v = {h: ("" if x is None else str(x)) for h, x in zip(HEAD, cells)}
        n_row = float(v["row"])  # Google Sheets writes the row number back as 165.0
        if n_row != int(n_row):
            sys.exit(f"{book_path} line {n}: row {v['row']} is not a whole number")
        i = int(n_row) - 2
        if not 0 <= i < len(rows) or i in seen:
            sys.exit(f"{book_path} line {n}: row {v['row']} is not a row of the CSV or appears twice")
        r = rows[i]
        if any(v[c] != str(r[c]) for c in COLS if c != "scale_item"):
            sys.exit(f"{book_path} line {n}: the key or text differs from line {v['row']} of the CSV")
        s = v["scale_item"].strip().lower()
        if s not in ("", "yes", "no"):
            sys.exit(f"{book_path} line {n}: scale_item {v['scale_item']!r} is not yes or no")
        seen[i] = s
    if len(seen) != len(rows):
        sys.exit(f"{book_path}: {len(rows) - len(seen)} rows of the CSV are missing from the book")
    changed = [i for i in seen if rows[i]["scale_item"] and rows[i]["scale_item"] != seen[i]]
    if changed:
        print(f"note: {len(changed)} rows had another scale_item in the CSV and are overwritten")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    copy = Path(csv_path).with_name(f"{Path(csv_path).stem}.before-back-{stamp}.csv")
    shutil.copy2(csv_path, copy)
    for i, s in seen.items():
        rows[i]["scale_item"] = s
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")  # as c_screening.write_csv
        w.writeheader()
        w.writerows(rows)
    filled = sum(1 for s in seen.values() if s)
    yes = sum(1 for s in seen.values() if s == "yes")
    print(f"wrote {csv_path} (copy {copy.name}): {filled} of {len(rows)} rows marked ({yes} yes); "
          f"{len(rows) - filled} still blank")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("make", "back"):
        sys.exit(__doc__)
    (make if sys.argv[1] == "make" else back)(sys.argv[2], sys.argv[3])
