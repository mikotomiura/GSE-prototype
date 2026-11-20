"""SHA-256 hashes of the symbol sequences of single records, for checking a re-run of the kit.

A record is one CoAuthor session (keyed by its session id, the name of its .jsonl file in the
public archive) or one CS1 2021 (SubjectID, AssignmentID) pair (its work blocks in time order).
For each record two hashes are given:

- sha256_symbols: of the symbols, written as decimal numbers joined by "," within a work block,
  blocks joined by ";" (a CoAuthor session is one block), UTF-8 encoded;
- sha256_rows: of one line per row, "t_ms,symbol,x,y\\n", with x and y written by float.hex(),
  so that a match also confirms x and y bit for bit.

The published lists cover the records analysed in the paper. They contain hashes only: no
symbols, no per-writer values and no text.

Usage (standard library only, run from this directory):
  python3 -I hashes.py check coauthor <coauthor.zip> coauthor_sha256.csv
  python3 -I hashes.py check cs1 <keystrokes.csv> cs1_2021_sha256.csv
  python3 -I hashes.py make coauthor <coauthor.zip> <ids.txt> <out.csv>
  python3 -I hashes.py make cs1 <keystrokes.csv> <ids.txt> <out.csv>
ids.txt holds one session id (CoAuthor) or "SubjectID,AssignmentID" (CS1) per line.
"""
import csv
import hashlib
import json
import os
import sys
import zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from adapters import coauthor, cs1_2021  # noqa: E402
from symbolizer import symbolize  # noqa: E402

FIELDS = ["n_blocks", "n_rows", "sha256_symbols", "sha256_rows"]


def digest(blocks):
    """blocks: list of symbolize() outputs (rows t_ms, x, y, symbol, alpha, path)."""
    sym = ";".join(",".join(str(r[3]) for r in rows) for rows in blocks)
    h = hashlib.sha256()
    for rows in blocks:
        for t, x, y, s, _a, _p in rows:
            h.update(("%d,%d,%s,%s\n" % (t, s, float(x).hex(), float(y).hex())).encode("ascii"))
    return dict(n_blocks=len(blocks), n_rows=sum(len(b) for b in blocks),
                sha256_symbols=hashlib.sha256(sym.encode("utf-8")).hexdigest(),
                sha256_rows=h.hexdigest())


def coauthor_records(zip_path, ids):
    """Yields (session_id, digest) for the given session ids."""
    with zipfile.ZipFile(zip_path) as z:
        by_sid = {os.path.basename(m)[:-len(".jsonl")]: m for m in z.namelist() if m.endswith(".jsonl")}
        for sid in ids:
            rows = [json.loads(l) for l in z.read(by_sid[sid]).decode("utf-8").splitlines() if l.strip()]
            t0, presses = coauthor.presses_from_rows(rows)
            out = symbolize(t0, presses)
            yield sid, digest([out] if out else [])


def cs1_records(csv_path, ids):
    """Yields ("SubjectID,AssignmentID", digest) for the given pairs."""
    want = {tuple(i.split(",")) for i in ids}
    csv.field_size_limit(10 ** 9)
    raw = defaultdict(list)
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            k = (row["SubjectID"], row["AssignmentID"])
            if k in want:
                raw[k].append(row)
    for i in ids:
        k = tuple(i.split(","))
        blocks = [symbolize(t0, p) for t0, p in cs1_2021.blocks_from_rows(raw[k])]
        yield i, digest([b for b in blocks if b])


def records(kind, path, ids):
    return coauthor_records(path, ids) if kind == "coauthor" else cs1_records(path, ids)


def key_name(kind):
    return "session_id" if kind == "coauthor" else "subject_assignment"


def make(kind, path, ids_path, out):
    ids = [l.strip() for l in open(ids_path, encoding="utf-8") if l.strip()]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow([key_name(kind)] + FIELDS)
        for rid, d in records(kind, path, ids):
            w.writerow([rid] + [d[k] for k in FIELDS])


def check(kind, path, table):
    rows = list(csv.DictReader(open(table, encoding="utf-8")))
    ids = [r[key_name(kind)] for r in rows]
    bad = 0
    for r, (rid, d) in zip(rows, records(kind, path, ids)):
        if any(str(d[k]) != r[k] for k in FIELDS):
            bad += 1
            print("mismatch: %s" % rid)
    print(json.dumps(dict(records=len(rows), mismatched=bad, rows=sum(int(r["n_rows"]) for r in rows))))
    return 1 if bad else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "check" and a[1] in ("coauthor", "cs1"):
        sys.exit(check(a[1], a[2], a[3]))
    if len(a) == 5 and a[0] == "make" and a[1] in ("coauthor", "cs1"):
        make(a[1], a[2], a[3], a[4])
        sys.exit(0)
    sys.exit(__doc__)
