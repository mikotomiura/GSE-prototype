"""Counts that notes.md cites and that no other output holds (design.md section 14). Standard library only.

  extra_counts.py --manifest results/corpus_manifest.json --zips raw/zips --derived raw/derived
                  --stats results/corpus_stats.json --out results/extra_counts.json

1. Ruby in the texts of the corpus works: all ruby markers, and implicit rubies that follow another ruby
   directly (a run of kanji between "》" and "《" with no "｜"), the case that the first implementation read
   wrongly.
2. B2 segments where the writer's reading and the attacker's reading differ, and where one of them is empty
   while the other is not (a writer's morpheme counted in the segment before a cut it crosses).
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_segments import load_derived, read_zip_text, unpack  # noqa: E402

ADJACENT_RE = re.compile("》[一-鿿㐀-䶿々〆〇ヶ仝]+《")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--zips", required=True)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    used = set(json.load(open(a.stats, encoding="utf-8"))["corpus_work_ids"])
    ruby = adjacent = works_adjacent = 0
    for e in json.load(open(a.manifest, encoding="utf-8"))["works"]:
        if e["role"] != "corpus" or e["work_id"] not in used:
            continue
        text, _ = read_zip_text(os.path.join(a.zips, e["work_id"] + ".zip"))
        n = len(ADJACENT_RE.findall(text))
        ruby += text.count("《")
        adjacent += n
        works_adjacent += int(n > 0)
    d = load_derived(a.derived, "corpus", "B2", a.stats)
    valid = differs = one_empty = 0
    for keys, blob in zip(d["keys"], d["units"]):
        att, wr = unpack(blob)
        for i, (x, y) in enumerate(zip(att, wr)):
            if keys[i] < 0:
                continue
            valid += 1
            differs += int(x != y)
            one_empty += int((x == "") != (y == ""))
    out = {
        "format": "extra-counts/1",
        "corpus_works": len(used),
        "ruby_markers": ruby,
        "adjacent_implicit_ruby": adjacent,
        "adjacent_implicit_ruby_fraction": adjacent / ruby if ruby else None,
        "works_with_adjacent_implicit_ruby": works_adjacent,
        "b2_valid_segments": valid,
        "b2_writer_reading_differs": differs,
        "b2_one_side_empty": one_empty,
    }
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
