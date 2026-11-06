"""paper-write Step 4: 7 語以上の同じ並びが節をまたいで繰り返されていないかを数える（本文の節だけ）。
使い方: python3 ngram_check.py <sections の dir>"""
import re
import sys
from collections import defaultdict

N = 7
SECS = ["introduction", "related", "data", "design", "results", "discussion", "limitations", "conclusion"]


def words(path):
    s = open(path).read()
    s = re.sub(r"(?m)%.*$", "", s)
    s = re.sub(r"\\(cite|ref|label|url|Description)\{[^}]*\}", " ", s)
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)
    return re.findall(r"[a-z0-9]+(?:[.\-][a-z0-9]+)*", s.lower())


def main(d):
    seen = defaultdict(set)
    for sec in SECS:
        w = words(f"{d}/{sec}.tex")
        for i in range(len(w) - N + 1):
            seen[" ".join(w[i:i + N])].add(sec)
    rep = {g: sorted(s) for g, s in seen.items() if len(s) > 1}
    # 重なる並びをまとめず、件数と並びを出す
    print(len(rep))
    for g, s in sorted(rep.items(), key=lambda x: (x[1], x[0])):
        print(",".join(s), "|", g)


if __name__ == "__main__":
    main(sys.argv[1])
