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


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_text(xml_bytes):
    """docx の本文 XML から段落ごとの文字列を作る（1 段落 1 行・文書の順）。

    ★ 段落の中の w:t は空白を入れずに連結する（語の途中で run が分かれても語を壊さない・Codex 1 巡目）。
    ★ w:tab・w:br・w:cr は空白にする（前後の語をつなげない）。入れ子の段落（テキストボックスの中など）は
      外の段落から外して別の行にする（外の段落の後ろの文を落とさない・Claude 2 巡目）。
    """
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_bytes)
    lines = []

    def para(p):
        buf = []
        idx = len(lines)
        lines.append("")  # 外の段落の行の位置を先に取る（入れ子の段落はその後ろの行になる）

        def walk(e):
            for c in e:
                if c.tag == W + "p":
                    para(c)
                elif c.tag == W + "t":
                    buf.append(c.text or "")
                elif c.tag in (W + "tab", W + "br", W + "cr"):
                    buf.append(" ")
                else:
                    walk(c)
        walk(p)
        lines[idx] = "".join(buf)

    def top(e):
        for c in e:
            if c.tag == W + "p":
                para(c)
            else:
                top(c)
    top(root)
    return "\n".join(lines)


def text_of(path):
    low = path.lower()
    if low.endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if low.endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            return docx_text(z.read("word/document.xml"))
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
