#!/usr/bin/env python3
"""要旨の語数を数える内部の道具（判断 182）。公開 repo には書き出さない。

  python .steering/20260927-ime-observation-paper-eval-design/issues/_count_abstract.py

papers/ime-observation/manuscript/main.tex の \\abstract{...} を取り出し、\\rv{<key>} を generated/values.json の text で
展開し、TeX の書式を落としてから空白で区切って数える（"0.280--1.000" は 1 語）。生成されていない鍵があれば exit 1。
BRM の上限は 250 語。投稿システムの数え方とは少しずれうるので、余裕を持たせる。
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.normpath(os.path.join(HERE, "..", "..", "..", "papers", "ime-observation", "manuscript"))


def main():
    s = open(os.path.join(M, "main.tex"), encoding="utf-8").read()
    i = s.index("\\abstract{") + len("\\abstract{")
    depth, j = 1, i
    while depth:
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        j += 1
    text = s[i:j - 1]
    vals = json.load(open(os.path.join(M, "generated", "values.json"), encoding="utf-8"))["values"]
    missing = []

    def rv(m):
        k = m.group(1)
        if k not in vals:
            missing.append(k)
            return "[" + k + "]"
        return vals[k]["text"]

    text = re.sub(r"\\rv\{([^}]*)\}", rv, text)
    text = text.replace("{,}", ",").replace("$-$", "-").replace("\\%", "%").replace("~", " ").replace("--", "-")
    text = re.sub(r"\\texttt\{([^}]*)\}", r"\1", text).replace("\\_", "_")
    words = text.split()
    print(" ".join(words))
    print("WORDS:", len(words), "MISSING:", missing)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
