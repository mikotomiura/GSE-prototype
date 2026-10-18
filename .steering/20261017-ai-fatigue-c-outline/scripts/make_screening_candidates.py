"""Make the input of the screening order (GSRR-33): the remaining candidates and their population group.

Remaining candidates: every additional candidate (GSRR-32: the 221 of the sheet 'スクリーニング' and the 43
review-search records of the sheet '探索の一覧'). All of them are screened again after registration, whatever was
decided before (GSRR-33, decision 28), so no earlier decision is read.
Population group: the first segment of the content group of the source database (column Q), mapped to the codes of
c_synthesis.py. Records with no population group in the source database (review-type records, records added by hand,
the review-search records) are put in the group 'unknown' (GSRR-16, decision of 2026-10-17); the reading that showed
why they have none is recorded in decisions.md (judgement 23), not used here.

With a second argument, the coverage sample (new-records.csv of c_search.py merge) is added as the group
coverage_sample (decision 38).

Run on the registration day against the current copy of the screening workbook:
    python3 make_screening_candidates.py <workbook.xlsx> ../registration-attachments/coverage/new-records.csv > candidates.csv
    python3 c_synthesis.py --screening-order candidates.csv > ../registration-attachments/screening-order.csv
Stops on a group label it does not know, a record listed twice, or a reading-list row it cannot read.
"""

import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
LABELS = {
    "学生・学習者": "students_learners",
    "教員・研究者": "teachers_researchers",
    "働く人（医療・教育の外）": "workers_other",
    "医療者": "health_professionals",
    "消費者・一般の利用者": "consumers_general",
    "不明": "unknown",
    "レビュー等": "unknown",  # review-type records have no participants, so no population group
    "": "unknown",            # no content group (a record added by hand)
}
FIRST_DATA_ROW = 5  # rows 1-4 of 'スクリーニング' are the title and the header


def sheet(z, name):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for s in wb.find(M + "sheets"):
        if s.get("name") == name:
            target = rels[s.get(REL)].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            rows = []
            for r in ET.fromstring(z.read(target)).iter(M + "row"):
                cells = {re.match(r"[A-Z]+", c.get("r")).group(): "".join(c.itertext()) for c in r.findall(M + "c")}
                rows.append((int(r.get("r")), cells))
            return rows
    raise SystemExit(f"sheet {name!r} not found")


def candidates(path):
    z = zipfile.ZipFile(path)
    out = []
    for n, v in sheet(z, "スクリーニング"):
        rid = v.get("A", "").strip()
        if n < FIRST_DATA_ROW or not rid:
            continue
        label = v.get("Q", "").split("｜")[0].strip()
        if label not in LABELS:
            raise SystemExit(f"row {n} ({rid}): unknown group label {label!r}")
        out.append((rid, LABELS[label]))  # every record, whatever its earlier decision (GSRR-33)
    for n, v in sheet(z, "探索の一覧"):
        k = v.get("K", "").strip()
        if not re.match(r"R\d\d", k):
            continue
        if not re.fullmatch(r"R\d\d", k):  # rows the reading list itself set aside (marked after the number)
            continue
        if v.get("H", "").strip():         # already in the source database (the 34 or the 221)
            continue
        out.append((k, "unknown"))
    ids = [i for i, _ in out]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"records listed twice: {dup}")
    return out


def coverage_sample(path):
    """The records drawn into the coverage sample (decision 38): new-records.csv of c_search.py merge, rows with
    coverage_sample 1. They form one more screening-order group, coverage_sample (GSRR-33)."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or "coverage_sample" not in rows[0]:
        raise SystemExit(f"{path}: not a new-records.csv (no column coverage_sample)")
    drawn = [(r["record_id"], "coverage_sample") for r in rows if r["coverage_sample"] == "1"]
    if len(drawn) != 300:
        raise SystemExit(f"{path}: {len(drawn)} drawn records, expected 300")
    return drawn


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["record_id", "population"])
    rows = candidates(sys.argv[1]) + (coverage_sample(sys.argv[2]) if len(sys.argv) == 3 else [])
    ids = [i for i, _ in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"a coverage record has the ID of a candidate: {dup[:5]}")
    for rid, pop in rows:
        w.writerow([rid, pop])
    counts = {}
    for _, pop in rows:
        counts[pop] = counts.get(pop, 0) + 1
    print(f"{len(rows)} remaining candidates: {counts}", file=sys.stderr)


if __name__ == "__main__":
    main()
