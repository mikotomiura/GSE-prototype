"""paper-write Step 3b・Step 4 の機械の測り（論文 3 の書き直し・2026-11-25）。

使い方: python3 readability.py <main.tex>

出すもの（要旨・本文〔序論〜結論〕・結論を別の行で）:
  文の数・平均の語数・40 語を超える文の数・
  1 文に否定や限定の語が 2 つ以上ある文の数（LIMIT の語のどれか、句は 1 つと数える）・
  本文に出る記号と略語の種類の数（ABBR の規則）、
  そして 7 語以上の同じ並びが節をまたいで繰り返される件数。

規則（版の間で同じにするため、ここに固定する）:
  - 本文は \\section{Introduction} から \\backmatter（無ければ \\section*{Statements）の前まで。
  - 表・tikz・数式の環境は除く。$...$ は 1 語「MATH」に置き換える（記号の種類は別に数える）。
  - 文の区切りは . ? ! の後の空白と大文字（e.g. i.e. vs. et al. は区切らない）。
  - LIMIT: not, no, only, cannot, neither, nor, without, never, unless, little, none,
    post hoc, not prespecified, exploratory, unknown, open（"remains open"）。
  - ABBR: 2 文字以上の大文字を含む語（HMM, AR-HMM, CS1, EM, MAP, DIC など）と、
    $...$ の中のラテン・ギリシャの記号名（\\tau, \\alpha, k, N, g など 1 文字の変数）。
"""
import collections
import re
import sys

LIMIT_PHRASES = ["post hoc", "not prespecified", "remains open"]
LIMIT_WORDS = {"not", "no", "only", "cannot", "neither", "nor", "without", "never",
               "unless", "little", "none", "exploratory", "unknown"}


def body_of(src):
    start = src.index("\\section{Introduction}")
    for end_mark in ("\\backmatter", "\\section*{Statements"):
        if end_mark in src:
            return src[start:src.index(end_mark)]
    raise SystemExit("end of body not found")


def abstract_of(src):
    m = re.search(r"\\abstract\{(.*?)\}\n", src, flags=re.S)
    return m.group(1) if m else ""


def conclusion_of(body):
    i = body.index("\\section{Conclusion}")
    return body[i:]


def symbols_in_math(text):
    syms = set()
    for m in re.findall(r"\$([^$]*)\$", text):
        for g in re.findall(r"\\(tau|alpha|bar|Pi|pi|infty)", m):
            syms.add("\\" + g)
        stripped = re.sub(r"\\[a-zA-Z]+", " ", m)
        for v in re.findall(r"(?<![A-Za-z])([A-Za-z])(?![A-Za-z])", stripped):
            if v not in {"e"}:
                syms.add(v)
    return syms


def clean(text):
    t = re.sub(r"(?<!\\)%.*", "", text)
    t = re.sub(r"\\begin\{(tabular|tikzpicture|equation|align)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
    t = re.sub(r"\\(begin|end)\{[a-z]+\*?\}(\[[^\]]*\])?", " ", t)
    t = re.sub(r"\$[^$]*\$", " MATH ", t)
    t = re.sub(r"\\(cite[pt]?|ref|label|Sref|url)\{[^}]*\}", " REF ", t)
    t = re.sub(r"\\(emph|textbf|textit|mbox|paragraph|section|subsection)\*?\{([^}]*)\}", r" \2. ", t)
    t = t.replace("\\hmmthree{}", "3-state HMM").replace("\\hmmten{}", "10-state HMM")
    t = t.replace("\\arone{}", "1-state AR-HMM").replace("\\artwo{}", "2-state AR-HMM")
    t = t.replace("\\arthree{}", "3-state AR-HMM").replace("\\arthree", "3-state AR-HMM")
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    t = re.sub(r"[{}~]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def sentences(t):
    t = re.sub(r"\b(e\.g|i\.e|vs|al|cf|approx)\.", lambda m: m.group(1) + "<DOT>", t)
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z(])", t)
    return [p.replace("<DOT>", ".") for p in parts if len(p.split()) >= 3]


def limit_count(s):
    low = s.lower()
    n = 0
    for ph in LIMIT_PHRASES:
        n += low.count(ph)
        low = low.replace(ph, " ")
    n += sum(1 for w in re.findall(r"[a-z']+", low) if w in LIMIT_WORDS)
    return n


def abbrevs(t):
    return {w for w in re.findall(r"\b[A-Za-z0-9-]*[A-Z][A-Za-z0-9-]*[A-Z0-9][A-Za-z0-9-]*\b", t)
            if w not in {"MATH", "REF"} and sum(c.isupper() for c in w) >= 2 or re.fullmatch(r"CS1", w or "")}


def report(name, raw):
    t = clean(raw)
    ss = sentences(t)
    lens = [len(s.split()) for s in ss]
    lim2 = sum(1 for s in ss if limit_count(s) >= 2)
    ab = abbrevs(t)
    sy = symbols_in_math(raw)
    print(f"{name}: 文 {len(ss)}・平均 {sum(lens)/max(len(ss),1):.1f} 語・40 語超 {sum(l > 40 for l in lens)}・"
          f"否定/限定 2 以上 {lim2}・略語 {len(ab)} {sorted(ab)}・記号 {len(sy)} {sorted(sy)}")


def ngram(body, n=7):
    parts = re.split(r"\\(?:sub)?section\{([^}]*)\}", body)
    secs = list(zip(parts[1::2], parts[2::2]))
    seen = collections.defaultdict(set)
    for name, text in secs:
        w = re.findall(r"[A-Za-z][A-Za-z'-]*", clean(text).lower())
        for i in range(len(w) - n + 1):
            seen[" ".join(w[i:i + n])].add(name[:40])
    rep = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"7 語以上の節をまたぐ繰り返し: {len(rep)}")
    for k, v in sorted(rep.items()):
        print(f"  {k} | {sorted(v)}")


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read()
    body = body_of(src)
    report("要旨", abstract_of(src))
    report("本文", body)
    report("結論", conclusion_of(body))
    ngram(body)
