"""取っておく書き手を決める（extend/conditions.md E2）。変換・replay の前に回す。

使い方: python3 -I make_holdout.py <seed> <out_holdout.json> <dux_v0.csv> <dux_v1.csv>
DUX は session 列だけを読む（振り分けの識別子・時刻や型は読まない）。
標準出力には人数と一覧の SHA-256 だけを出す。
"""
import csv
import hashlib
import json
import random
import sys

FRAC = 0.3
SWELL_PEOPLE = list(range(1, 26))

csv.field_size_limit(1 << 30)


def dux_ids(paths):
    ids = set()
    for ver, p in zip(("v0", "v1"), paths):
        with open(p, newline="", encoding="utf-8") as f:
            r = csv.reader(f, delimiter="\t")
            head = next(r)
            i = head.index("session")
            for row in r:
                ids.add("%s:%s" % (ver, row[i]))
    return sorted(ids)


def main():
    seed, out, v0, v1 = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    ids = dux_ids([v0, v1])
    d_hold = sorted(random.Random(seed + 2).sample(ids, round(FRAC * len(ids))))
    s_hold = sorted(random.Random(seed + 3).sample(SWELL_PEOPLE, round(FRAC * len(SWELL_PEOPLE))))
    rec = {"dux": d_hold, "swell": s_hold}
    blob = json.dumps(rec, sort_keys=True)
    with open(out, "w") as f:
        f.write(blob)
    print(json.dumps({"dux_sessions": len(ids), "dux_holdout": len(d_hold), "swell_people": len(SWELL_PEOPLE),
                      "swell_holdout": len(s_hold), "sha256": hashlib.sha256(blob.encode()).hexdigest(),
                      "python": sys.version.split()[0]}))


if __name__ == "__main__":
    main()
