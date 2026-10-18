"""The look of the TRACE screening workbooks (author 1's and author 2's), in one place (decision 35).

Yu Gothic is shipped with Office on both macOS and Windows. Colours: a dark header, light blue input cells,
and conditional fills on the decision and centre cells so that a filled row can be read at a glance.
"""

from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.hyperlink import Hyperlink

FONT = "Yu Gothic"
INK, MUTED, LINE = "1F2937", "6B7280", "E5E7EB"
HEAD_FILL = PatternFill("solid", fgColor="1F2937")
INPUT_FILL = PatternFill("solid", fgColor="EAF2FD")
BODY = Font(name=FONT, size=10, color=INK)
HEAD = Font(name=FONT, size=10, bold=True, color="FFFFFF")
LINK = Font(name=FONT, size=10, color="2563EB", underline="single")
TITLE = Font(name=FONT, size=16, bold=True, color=INK)
SUB = Font(name=FONT, size=11, bold=True, color=INK)
NOTE = Font(name=FONT, size=10, color=MUTED)
WRAP = Alignment(wrap_text=True, vertical="top")
TOP = Alignment(vertical="top")
CENTER = Alignment(horizontal="center", vertical="top")
BOTTOM = Border(bottom=Side(style="thin", color=LINE))
# value -> (fill, font colour) for the decision and centre cells
STATES = {"含める": ("DCFCE7", "166534"), "除外": ("F3F4F6", "6B7280"), "保留": ("FEF3C7", "92400E"),
          "中心-A": ("E0E7FF", "3730A3"), "中心-B": ("CCFBF1", "115E59"), "境界（保留）": ("FEF3C7", "92400E")}


def table(ws, cols, widths, rows, inputs=(), wrap=(), links=None, tab=None, height=None):
    """Write a table: header, body rows, column widths, freeze, filter, input fills and row borders.
    links: {column name: function(row values) -> (url, label) or None}."""
    ws.append(cols)
    for i, w in enumerate(widths, start=1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill, c.alignment = HEAD, HEAD_FILL, Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = w
    ws.row_dimensions[1].height = 24
    for vals in rows:
        ws.append(vals)
        r = ws.max_row
        for i, name in enumerate(cols, start=1):
            c = ws.cell(row=r, column=i)
            c.font, c.border = BODY, BOTTOM
            c.alignment = WRAP if name in wrap else TOP
            if name in inputs:
                c.fill = INPUT_FILL
            if links and name in links:
                got = links[name](vals)
                if got:
                    target, c.value, c.font = got[0], got[1], LINK
                    if target.startswith("#"):  # a place in this workbook
                        c.hyperlink = Hyperlink(ref=c.coordinate, location=target[1:], display=str(got[1]))
                    else:
                        c.hyperlink = target
        if height:
            ws.row_dimensions[r].height = height(vals)
    ws.freeze_panes = "B2"
    last = max(ws.max_row, 2)
    ws.auto_filter.ref = f"A1:{ws.cell(row=1, column=len(cols)).column_letter}{last}"
    ws.sheet_view.showGridLines = False
    if tab:
        ws.sheet_properties.tabColor = tab


def choices(ws, cols, spec):
    """Drop-down lists and the state colours on the columns author 1 or 2 fills in."""
    last = max(ws.max_row, 2)
    for name, values in spec:
        letter = ws.cell(row=1, column=cols.index(name) + 1).column_letter
        rng = f"{letter}2:{letter}{last}"
        dv = DataValidation(type="list", formula1=f'"{values}"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(rng)
        for v in values.split(","):
            if v in STATES:
                fill, colour = STATES[v]
                ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{letter}2="{v}"'],
                                                               fill=PatternFill("solid", fgColor=fill),
                                                               font=Font(name=FONT, size=10, bold=True, color=colour)))


def intro(ws, title, lead, sections):
    """The first sheet: a title, a lead line and short sections (heading, lines)."""
    ws.title = "はじめに"
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 120
    ws["B2"], ws["B2"].font = title, TITLE
    ws["B3"], ws["B3"].font = lead, NOTE
    r = 5
    for head, lines in sections:
        ws.cell(row=r, column=2, value=head).font = SUB
        r += 1
        for ln in lines:
            c = ws.cell(row=r, column=2, value=ln)
            c.font, c.alignment = BODY, WRAP
            ws.row_dimensions[r].height = 17 * max(1, -(-display_width(ln) // 128))
            r += 1
        r += 1
    ws.sheet_properties.tabColor = "1F2937"


def display_width(text):
    """Width in Excel character units: a Japanese (full-width) character takes two."""
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(text or ""))


def text_height(*pairs):
    """A row height that shows the longest wrapped text; pairs are (text, column width). openpyxl does not size
    rows, so the height is estimated from the display width of the text."""
    lines = 1
    for text, width in pairs:
        per = max(1, int(width * 1.1) - 2)
        n = sum(max(1, -(-display_width(part) // per)) for part in str(text or "").split("\n"))
        lines = max(lines, n)
    return min(409, 14 * lines + 6)
