"""Write the coding form (registration attachment 2) from the column lists of c_synthesis.py.

The form is the set of empty CSV files the coder fills in (one copy per pass), one per unit, and a column dictionary that gives, for each
column, what is coded and the values the script accepts. Both are generated from c_synthesis.py (REQUIRED, VOCAB,
MULTI_VALUE, INTEGER_COLS, OPTIONAL_EMPTY, LINK_COLUMNS), so the form cannot drift from the script that reads it.
The rules for choosing a value are in the registration and the C2b codebook, not here.

Usage: python3 make_coding_form.py <output_dir>
Stops if a column of the script has no description here, or a description names a column the script does not read.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c_synthesis as cs  # noqa: E402

FILES = {
    "records": "One row per coded record (the one coded record of an E5 group included; the other records of the "
               "group are listed only in links.csv).",
    "instruments": "One row per fatigue instrument per record.",
    "items": "One row per coded item of an instrument version (printed items, or items taken from the cited "
             "source).",
    "c4f": "One row per recalculated result (C4f).",
    "links": "One row per record of an E5 group, coded or not.",
}

DESCRIPTIONS = {
    # records
    "record_id": "Record ID of the source database.",
    "set": "Set of the record (registration GSRR-39): exploration, main, late or coverage (the coverage stratum). Calibration codes go in their own directory, with every record in set exploration.",
    "population": "Population group of the source database (GSRR-16); for the coverage stratum, the group recorded by author 1 at the full-text stage.",
    "centre": "Centre of the source database.",
    "peer_reviewed": "1 if the record is peer reviewed (sensitivity analysis 1).",
    "C3": "AI-side variable instrument, all that apply.",
    "C4a": "C4 rule (a): N in the text against the table denominators.",
    "C4b": "C4 rule (b): direction of the main relation in the abstract, results and discussion.",
    "C4c": "C4 rule (c): discriminant validity, the report's own criterion against its reported values.",
    "C4d": "C4 rule (d): ethics statements within the report.",
    "C4e_codebook": "C4 rule (e): codebook available for qualitative coding (not_applicable for quantitative studies).",
    "C4e_agreement": "C4 rule (e): agreement for qualitative coding (not_applicable for quantitative studies).",
    "C5": "Sample overlap category.",
    "C6a": "Construct term of the title against the name of the main instrument.",
    "C6b": "Causal wording against the design (no causal wording is a match).",
    "conclusion_identified": "1 if the main conclusion sentence can be identified (C7).",
    "main_instrument_identified": "1 if the main instrument can be identified (C6c, C7).",
    "conclusion_ai_fatigue_term": "1 if the main conclusion uses an AI-fatigue term (C7 (ii)).",
    "conclusion_family": "Term family of the construct term in the main conclusion (C7 (iii)).",
    "main_instrument_family": "Term family or families in the name of the main instrument (C6a, C7 (iii)).",
    "conclusion_sentence": "The main conclusion, copied verbatim (empty if it cannot be identified).",
    "title_ai_fatigue_term": "Whether the title uses an AI-fatigue term (C6c).",
    # instruments
    "instrument_id": "Instrument ID within the record.",
    "version_id": "Instrument version ID: the same item wording in the same language gets the same ID.",
    "language": "Language of the items as administered.",
    "items_full": "Full item count of the instrument (a whole number, or a missing code).",
    "origin": "C2a origin.",
    "format": "C2a format.",
    "mod_items_dropped": "C2a modification: items dropped.",
    "mod_items_added": "C2a modification: items added.",
    "mod_reworded": "C2a modification: items reworded.",
    "mod_instructions_only": "C2a modification: AI added to the instructions only.",
    "mod_response_scale": "C2a modification: response scale changed.",
    "mod_scoring": "C2a modification: scoring changed.",
    "mod_translated": "C2a modification: translated.",
    "C2c_backtranslation": "C2c: back-translation reported (adapted instruments only).",
    "C2c_content_validity": "C2c: content validity reported (adapted instruments only).",
    "C2c_pilot": "C2c: pilot reported (adapted instruments only).",
    "C2c_factor_check": "C2c: factor check reported (adapted instruments only).",
    "C2d_item_disclosure": "C2d: item disclosure.",
    "C2d_reliability": "C2d: reliability in this sample.",
    "C2d_factor_analysis": "C2d: factor analysis in this sample.",
    "C2d_reason": "C2d: a reason for choosing the instrument (a citation alone does not count).",
    # items
    "item_no": "Item number within the version (a whole number).",
    "type": "C2b type (codebook version 2).",
    "boundary": "1 if the item is a boundary item.",
    "secondary_type": "C2b secondary type of a boundary item (empty otherwise).",
    "target": "C2b target, only when the type or secondary type is MOT, AVO or FUT (empty otherwise).",
    "item_source": "printed: the item is printed in the report; source: taken from the cited source.",
    # c4f
    "result_id": "Result ID within the record.",
    "source": "Where the result is reported: text or table.",
    "consistent": "Whether the recalculated value is consistent with the reported one (na: cannot be calculated).",
    "gross": "1 if the inconsistency changes the conclusion at alpha = .05 (only for inconsistent results).",
    # links
    "group_id": "E5 group ID of the source database.",
}
for _lv in cs.C1_LEVELS:
    DESCRIPTIONS[f"C1_{_lv}"] = f"C1 level {_lv} for the main instrument: 1 if it applies (all that apply)."


def columns():
    cols = {kind: list(cols) for kind, cols in cs.REQUIRED.items()}
    cols["links"] = list(cs.LINK_COLUMNS)
    return cols


def allowed(col):
    if col in cs.INTEGER_COLS:
        extra = " or " + ", ".join(sorted(cs.MISSING)) if col == "items_full" else ""
        return "a whole number" + extra
    values = cs.VOCAB.get(col)
    if values is None:
        return "free text" if col in cs.OPTIONAL_EMPTY else "an ID or free text"
    return ", ".join(sorted(v for v in values if v)) or "(empty)"


def main(out):
    cols = columns()
    used = {c for cs_ in cols.values() for c in cs_}
    missing = sorted(used - set(DESCRIPTIONS))
    unused = sorted(set(DESCRIPTIONS) - used)
    if missing or unused:
        raise SystemExit(f"descriptions missing for {missing}; descriptions for columns the script does not read: {unused}")
    out.mkdir(parents=True, exist_ok=True)
    for kind, names in cols.items():
        with open(out / f"{kind}.csv", "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(names)
    lines = ["# Coding form: column dictionary", "",
             "Generated by make_coding_form.py from c_synthesis.py. Author 1 fills in one copy of each file per coding pass, named",
             "`<file>_coder1.csv` (first pass) and `<file>_coder2.csv` (second pass); the reconciled copy is `<file>_reconciled.csv`; `links.csv`",
             "is shared. Cells are never left empty except where stated: a missing value has its own code and stands",
             "alone in a cell. Multi-value cells separate values with `|`, each value once. The rules for choosing a",
             "value are in the registration and the C2b codebook.", ""]
    for kind, names in cols.items():
        fname = "links.csv" if kind == "links" else f"{kind}_<coder>.csv"
        lines += [f"## {fname}", "", FILES[kind], "", "| Column | What is coded | Values accepted | Multi-value | May be empty |",
                  "|---|---|---|---|---|"]
        for c in names:
            lines.append(f"| `{c}` | {DESCRIPTIONS[c]} | {allowed(c)} | {'yes' if c in cs.MULTI_VALUE else ''} | "
                         f"{'yes' if c in cs.OPTIONAL_EMPTY or (c in cs.VOCAB and '' in cs.VOCAB[c]) else ''} |")
        lines.append("")
    (out / "columns.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {len(cols)} templates and columns.md to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
