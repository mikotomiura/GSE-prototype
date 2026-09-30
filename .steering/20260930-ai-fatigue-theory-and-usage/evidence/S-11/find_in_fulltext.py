"""無料の本文（repo の外に保存した PDF・HTML・docx）から、語形（N1〜N4）を含む文と手がかりの有無を出す（design.md §1.3）。

★ 印は目安で、意味を与える文を決めるのはメイン。出力は標準出力だけ（本文を repo に書かない）。
使い方: python find_in_fulltext.py <本文のファイル（repo の外）> [--all]   # --all は語を含む文をすべて出す（既定は最初の 25 文）
"""
import html
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fetch_abstracts as F  # noqa: E402
import screen as S  # noqa: E402


def text_of(path):
    low = path.lower()
    if low.endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if low.endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        return html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"</w:p>", "\n", xml)))
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def main():
    path = sys.argv[1]
    F.common.ensure_outside_repo(path)
    text = re.sub(r"-\n(?=[a-z])", "", text_of(path))  # 行末のハイフンでの分かち書きを戻す
    text = re.sub(r"\s+", " ", text)
    sents = S.sentences(text)
    shown = 0
    for i, s in enumerate(sents):
        if S.uses_term(S.terms(s)):
            cue = "【手がかりあり】" if S.CUES.search(s) else ""
            print(f"[{i}] {cue}{s[:700]}")
            shown += 1
            if shown >= 25 and "--all" not in sys.argv:
                break
    print(f"-- 文 {len(sents)}・語を含む文を {shown} 件表示")


if __name__ == "__main__":
    main()
