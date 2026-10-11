"""Records -> segments (preregistration.md, "記録の区間").

  records.py --records <dir of decrypted NDJSON> --work <dir outside the repository>

Each block named in config.json records.copy_blocks / control_blocks is the one file under --records whose name
starts with "<label>_" and whose SHA-256 is config.json records.sha256[label] (a name holding "_dup" is the
duplicate upload of P010 block06 and is not used). The output
(<work>/records.json) holds, per block, the segment values of the plain and the cleaned record and per-segment
counts of the keys; it stays outside the repository. Only the number of blocks is printed.
"""
import argparse
import json
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_config, sha256_file, write_json

STAT_KEYS = ("alphabetic", "numeric", "backspace", "enter", "space")


def presses(path):
    """Categories of the key presses, in file order."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            if o.get("type") == "key" and o.get("press") is True:
                out.append(o["category"])
    return out


def segments(cats, rule, clean=False):
    """[(value, stats)] of the record. value = plus - minus inside the segment; a boundary category closes the
    segment; the segment after the last boundary is dropped. With clean, a boundary whose next relevant press
    (plus, minus or boundary category) is a minus is not a boundary, and that minus is not counted."""
    plus, minus, bound = set(rule["counted_plus"]), set(rule["counted_minus"]), set(rule["boundary"])
    relevant = plus | minus | bound
    skip_minus = set()
    skip_bound = set()
    if clean:
        i = 0
        n = len(cats)
        while i < n:
            if cats[i] in bound and i not in skip_bound:
                j = i + 1
                while j < n and cats[j] not in relevant:
                    j += 1
                if j < n and cats[j] in minus:
                    skip_bound.add(i)
                    skip_minus.add(j)
                    i = j + 1
                    continue
            i += 1
    out = []
    value = 0
    st = dict.fromkeys(STAT_KEYS, 0)
    for i, c in enumerate(cats):
        if c in st:
            st[c] += 1
        if c in bound and i not in skip_bound:
            out.append((value, st))
            value = 0
            st = dict.fromkeys(STAT_KEYS, 0)
        elif c in plus:
            value += 1
        elif c in minus and i not in skip_minus:
            value -= 1
    return out  # the open segment (after the last boundary) is not appended


def find_file(root, label, want):
    hits = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.startswith(label + "_") and fn.endswith(".ndjson") and "_dup" not in fn:  # the duplicate upload
                p = os.path.join(dirpath, fn)
                if sha256_file(p) == want:
                    hits.append(p)
    if len(hits) != 1:
        raise SystemExit("records: %s: expected one file with the recorded SHA-256, found %d" % (label, len(hits)))
    return hits[0]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args(argv)
    cfg = load_config()
    rcfg = cfg["records"]
    rule = cfg["record_rule"]
    out = {}
    for label in rcfg["copy_blocks"] + rcfg["control_blocks"]:
        cats = presses(find_file(a.records, label, rcfg["sha256"][label]))
        plain = segments(cats, rule)
        clean = segments(cats, rule, clean=True)
        out[label] = {"plain": [v for v, _ in plain], "plain_stats": [s for _, s in plain],
                      "clean": [v for v, _ in clean]}
    os.makedirs(a.work, exist_ok=True)
    write_json(os.path.join(a.work, "records.json"), {"format": "g1-records/1", "blocks": out})
    print("records: %d blocks" % len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
