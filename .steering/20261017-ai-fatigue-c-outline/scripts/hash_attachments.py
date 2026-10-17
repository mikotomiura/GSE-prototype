"""List the registration attachments with their SHA-256 (registration, Attachments 1-6).

Run on the day of registration, after the screening order list has been made from all 264 additional candidates
(GSRR-33). Writes registration-attachments/sha256.txt and prints it. Stops if an attachment is missing, so a list with a gap cannot be attached.

Usage: python3 hash_attachments.py
"""

import datetime
import hashlib
import platform
import sys
from pathlib import Path

TASK = Path(__file__).resolve().parent.parent
REPO = TASK.parent.parent
ATT = TASK / "registration-attachments"

# (attachment number, what it is, path)
ATTACHMENTS = [
    (1, "C2b codebook, version 2", TASK / "codebook-c2b-en.md"),
    (2, "synthesis script", TASK / "scripts" / "c_synthesis.py"),
    (2, "dummy-table generator and checks", TASK / "scripts" / "make_dummy.py"),
    (2, "coding form generator", TASK / "scripts" / "make_coding_form.py"),
    (2, "coding form: column dictionary", ATT / "coding-form" / "columns.md"),
    (2, "coding form: records", ATT / "coding-form" / "records.csv"),
    (2, "coding form: instruments", ATT / "coding-form" / "instruments.csv"),
    (2, "coding form: items", ATT / "coding-form" / "items.csv"),
    (2, "coding form: C4f results", ATT / "coding-form" / "c4f.csv"),
    (2, "coding form: E5 links", ATT / "coding-form" / "links.csv"),
    (3, "query strings of the source database's searches", ATT / "query-strings.md"),
    (4, "screening order list", ATT / "screening-order.csv"),
    (5, "manuscript outline", REPO / "papers" / "ai-fatigue-measurement" / "manuscript" / "outline.md"),
    (6, "AI screener: instructions", ATT / "ai-screening" / "instructions.md"),
    (6, "AI screener: call wording and settings", ATT / "ai-screening" / "call.md"),
    (6, "AI screener: check on the 34 exploratory records", ATT / "ai-screening" / "check-34.csv"),
    (6, "AI screener: readme", ATT / "ai-screening" / "README.md"),
    (6, "screening tools: batches, inputs, format check, final decisions, release", TASK / "scripts" / "c_screening.py"),
    (6, "screening tools: checks on dummy records", TASK / "scripts" / "check_screening.py"),
    (6, "screening database generator", TASK / "scripts" / "make_trace_db.py"),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    missing = [str(p.relative_to(REPO)) for _, _, p in ATTACHMENTS if not p.exists()]
    if missing:
        raise SystemExit("missing attachments:\n  " + "\n  ".join(missing))
    lines = [f"# Registration attachments, {datetime.date.today().isoformat()}, Python {platform.python_version()}"]
    for n, what, p in ATTACHMENTS:
        lines.append(f"{sha256(p)}  attachment {n}  {p.name}  ({what})")
    text = "\n".join(lines) + "\n"
    (ATT / "sha256.txt").write_text(text, encoding="utf-8")
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
