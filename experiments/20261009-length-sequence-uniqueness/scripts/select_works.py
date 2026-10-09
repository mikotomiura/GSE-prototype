"""Select Aozora Bunko works for the corpus (design.md section 3). Standard library only.

  select_works.py --index raw/index/list_person_all_extended_utf8.zip --seed-file SEED --config config.json
                  --out results/selection.json

Writes the head (`fetch_count` works) of the ordered list of eligible works (the fetch step takes them from
the top) and the reference list of the IME paper's 12 works. Nothing here depends on the texts.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile

COL_WORK_ID, COL_TITLE, COL_NDC, COL_ORTHO, COL_WORK_COPYRIGHT = 0, 1, 8, 9, 10
COL_PERSON_ID, COL_LAST, COL_FIRST, COL_ROLE, COL_TEXT_URL = 14, 15, 16, 23, 45
EXPECTED_HEADER = {COL_WORK_ID: "作品ID", COL_TITLE: "作品名", COL_NDC: "分類番号", COL_ORTHO: "文字遣い種別",
                   COL_WORK_COPYRIGHT: "作品著作権フラグ", COL_PERSON_ID: "人物ID", COL_ROLE: "役割フラグ",
                   COL_TEXT_URL: "テキストファイルURL"}


def read_index(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith(".csv")]
        if len(names) != 1:
            raise SystemExit("select_works: expected one CSV in the index zip, found %r" % names)
        rows = list(csv.reader(io.TextIOWrapper(z.open(names[0]), encoding="utf-8-sig")))
    header, rows = rows[0], rows[1:]
    for col, name in EXPECTED_HEADER.items():
        if header[col] != name:
            raise SystemExit("select_works: column %d is %r, expected %r" % (col, header[col], name))
    return rows


def is_poetry(ndc):
    """NDC 911 (poetry), including the children's-literature form K911."""
    return any(code.lstrip("K").startswith("911") for code in ndc.replace("NDC", " ").split())


def rank(seed, work_id):
    return hashlib.sha256(("%s:%s" % (seed, work_id)).encode("utf-8")).hexdigest()


def select(rows, seed, cfg):
    by_work = {}
    for r in rows:
        by_work.setdefault(r[COL_WORK_ID], []).append(r)
    eligible = []
    for wid, rs in by_work.items():
        first = rs[0]
        if first[COL_ORTHO] != cfg["orthography"] or first[COL_WORK_COPYRIGHT] != cfg["work_copyright"]:
            continue
        if not first[COL_TEXT_URL].endswith(".zip"):
            continue
        if cfg["exclude_poetry"] and is_poetry(first[COL_NDC]):
            continue
        authors = [r for r in rs if r[COL_ROLE] == "著者"] or rs
        eligible.append({
            "work_id": wid,
            "title": first[COL_TITLE],
            "author_person_id": authors[0][COL_PERSON_ID],
            "author": authors[0][COL_LAST] + authors[0][COL_FIRST],
            "ndc": first[COL_NDC],
            "text_url": first[COL_TEXT_URL],
            "rank": rank(seed, wid),
        })
    eligible.sort(key=lambda w: w["rank"])
    seen, ordered, dup = set(), [], []
    for w in eligible:
        key = (w["author_person_id"], re.sub(r"\s", "", w["title"]))
        if key in seen:
            dup.append(w["work_id"])
            continue
        seen.add(key)
        ordered.append(w)
    return ordered, dup, len(by_work)


def reference_works(rows, ids):
    by_work = {}
    for r in rows:
        by_work.setdefault(r[COL_WORK_ID], r)
    out = []
    for wid in ids:
        r = by_work.get(wid)
        if r is None:
            raise SystemExit("select_works: reference work %s is not in the index" % wid)
        out.append({"work_id": wid, "title": r[COL_TITLE], "text_url": r[COL_TEXT_URL]})
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--seed-file", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    seed = open(a.seed_file, encoding="utf-8").read().strip()
    cfg = json.load(open(a.config, encoding="utf-8"))["selection"]
    rows = read_index(a.index)
    ordered, dup, n_works = select(rows, seed, cfg)
    ref = reference_works(rows, [r["work_id"] for r in cfg["reference_works"]])
    n_eligible = len(ordered)
    ordered = ordered[:cfg["fetch_count"]]  # only the head is fetched; the rest follows from the index and the seed
    out = {
        "format": "selection/1",
        "seed": seed,
        "n_index_rows": len(rows),
        "n_index_works": n_works,
        "n_eligible_after_title_dedupe": n_eligible,
        "n_listed": len(ordered),
        "n_title_duplicates_dropped": len(dup),
        "title_duplicates_dropped": dup,
        "ordered": ordered,
        "reference": ref,
    }
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("select_works: %d works in the index, %d eligible, %d title duplicates dropped, %d listed"
          % (n_works, n_eligible, len(dup), len(ordered)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
