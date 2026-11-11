"""本文（序論〜結論）の 7 語以上の同じ並びが節をまたいで繰り返されるかを数える。
使い方: python3 ngram_repeats.py <main.tex> [n]"""
import re, sys, collections
src = open(sys.argv[1], encoding="utf-8").read()
n = int(sys.argv[2]) if len(sys.argv) > 2 else 7
body = src[src.index("\\section{Introduction}"):src.index("\\section*{Statements")]
parts = re.split(r"\\(?:sub)?section\{([^}]*)\}", body)
secs = list(zip(parts[1::2], parts[2::2]))
seen = collections.defaultdict(set)
for name, text in secs:
    t = re.sub(r"%.*", "", text)
    t = re.sub(r"\\begin\{(tabular|tikzpicture)\}.*?\\end\{\1\}", " ", t, flags=re.S)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    w = re.findall(r"[A-Za-z][A-Za-z'-]*", t.lower())
    for i in range(len(w) - n + 1):
        seen[" ".join(w[i:i + n])].add(name)
rep = {k: v for k, v in seen.items() if len(v) > 1}
print(len(rep))
for k, v in sorted(rep.items()):
    print(f"{k} | {sorted(v)}")
