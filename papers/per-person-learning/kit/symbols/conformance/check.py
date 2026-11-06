"""Conformance check: symbolize the synthetic cases and compare with the expected traces.

Each expected row is [t_ms, x (float hex), y (float hex), symbol, alpha]. A case matches when
the number of rows and every row are identical, with x and y compared bit for bit.

Usage: python3 check.py [<inputs.json[.gz]> <expected.json[.gz]>]
Without arguments, the files in conformance/data/ are used. Exit status 0 when every case matches.
"""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from symbolizer import load_constants, symbolize  # noqa: E402


def compare(got, exp):
    if len(got) != len(exp):
        return "row_count"
    for g, e in zip(got, exp):
        t, x, y, sym, alpha, _ = g
        if t != e[0]:
            return "time"
        if sym != e[3]:
            return "symbol"
        if x.hex() != e[1] or y.hex() != e[2]:
            return "xy_bits"
        if alpha != e[4]:
            return "alpha"
    return None


def load(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = sys.argv[1:] or [os.path.join(here, "data", "inputs.json.gz"), os.path.join(here, "data", "expected.json.gz")]
    cases = load(args[0])["cases"]
    expected = load(args[1])["expected"]
    c = load_constants()
    kinds = {}
    first = None
    for i, ((t0, presses), exp) in enumerate(zip(cases, expected)):
        k = compare(symbolize(t0, [tuple(p) for p in presses], c), exp)
        if k:
            kinds[k] = kinds.get(k, 0) + 1
            first = first if first is not None else i
    n_rows = sum(len(e) for e in expected)
    print(json.dumps({"cases": len(cases), "rows": n_rows, "mismatched_cases": sum(kinds.values()),
                      "mismatch_kinds": kinds, "first_mismatch_case": first}))
    sys.exit(1 if kinds else 0)


if __name__ == "__main__":
    main()
