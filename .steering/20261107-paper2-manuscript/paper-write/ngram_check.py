#!/usr/bin/env python3
"""本文の節をまたいで 7 語以上の同じ並びが繰り返されていないかを数える（paper-write Step 4）。

  python3 ngram_check.py <manuscript-dir> [n]
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

d = Path(sys.argv[1])
n = int(sys.argv[2]) if len(sys.argv) > 2 else 7
secs = ["abstract", "introduction", "related", "methods", "results", "discussion", "limitations", "conclusion"]
seen = defaultdict(set)
for s in secs:
    t = (d / "sections" / f"{s}.tex").read_text()
    t = re.sub(r"%.*", "", t)
    t = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", t, flags=re.S)
    t = re.sub(r"\\(cite|ref|label)\{[^}]*\}", " ", t)
    t = re.sub(r"\\[a-zA-Z]+", " ", t)
    w = re.findall(r"[A-Za-z0-9.\-]+", t.lower())
    for i in range(len(w) - n + 1):
        seen[" ".join(w[i:i + n])].add(s)
hits = {k: v for k, v in seen.items() if len(v) > 1}
print(f"{n}-grams in more than one section: {len(hits)}")
for k, v in sorted(hits.items(), key=lambda x: sorted(x[1])):
    print(f"  {sorted(v)}: {k}")
