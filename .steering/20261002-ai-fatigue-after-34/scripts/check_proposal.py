"""提案のドキュメント v1 の検査（design.md §8・requirement.md の受け入れ条件）。

(1) .docx の本文（段落と表のセル）が原稿の Markdown と一致する（記号を落として、空でない文の列で比べる）。
(2) 見出し「## 0」〜「## 9」がこの順で 1 回ずつある。
(3) 冒頭の 5 段落以内に「判定者 2 に渡さない」がある。
(4) 禁止: 内部の名前・手元のパス・メールアドレス（研究者は repo を読めない・GSE を知らない）。
(5) 付録の 34 行が 34 件の写しの判定者1 と、追加候補の行が追加候補の表の判定者1 と一致する（本検査器が独立に読む）。
(6) archive と Downloads の .docx の SHA-256 が記録と同じ。
--selftest: 実の原稿で作った .docx が緑・変異（見出しを消す・注意を冒頭から外す・禁止語・付録の行をずらす・.docx の段落を変える）が赤。
使い方: python check_proposal.py [--selftest]
"""
import os
import re
import shutil
import sys
import tempfile

import openpyxl
from docx import Document

import common as C

MD = os.path.join(C.TASK, "proposal", "proposal-v1.md")
DOCX_NAME = "AI疲労DB_判定者1からの提案_v1.docx"
DOCX_ARCHIVE = os.path.join(C.TASK, "archive", DOCX_NAME)
DOCX_DOWNLOADS = os.path.join(C.DOWNLOADS, DOCX_NAME)
SHA_RECORD = os.path.join(C.TASK, "archive", "proposal-sha256.txt")
WARN = "判定者 2 に渡さない"
BANNED = re.compile(r"GSE|\.steering|[A-Za-z]:\\|Downloads\\|scratchpad|screening-log|/cross-review|cross-review|Codex|worktree|"
                    r"[\w.+-]+@[\w-]+\.[\w.]+|\.jsonl|check_\w+\.py|build_\w+\.py", re.I)


def norm(s):
    s = re.sub(r"\*\*|`", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def md_texts(md):
    out = []
    for line in md.splitlines():
        t = line.strip()
        if not t or t.startswith("<!--"):
            continue
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if all(re.fullmatch(r"-+", c) for c in cells):
                continue
            out += [norm(c) for c in cells]
            continue
        t = re.sub(r"^(#{1,3} |- )", "", t)
        out.append(norm(t))
    return [x for x in out if x]


def docx_texts(path):
    d = Document(path)
    out = []
    body = d.element.body
    for el in body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            t = "".join(x.text or "" for x in el.iter() if x.tag.endswith("}t"))
            if t.strip():
                out.append(norm(t))
        elif tag == "tbl":
            for tc in el.iter():
                if tc.tag.endswith("}tc"):
                    t = "".join(x.text or "" for x in tc.iter() if x.tag.endswith("}t"))
                    out.append(norm(t))
    return [x for x in out if x]


def expected_appendix():
    """本検査器が独立に読む: (ID, 判定者1) の列。"""
    w = openpyxl.load_workbook(C.COPY34_ARCHIVE, read_only=True)["スクリーニング"]
    a = [(r[0], r[3]) for r in w.iter_rows(min_row=5, max_row=38, values_only=True)]
    c = openpyxl.load_workbook(C.CAND_ARCHIVE, read_only=True)["スクリーニング"]
    b = []
    for r in c.iter_rows(min_row=5, values_only=True):
        if r[0] is None:
            break
        if r[3] != "未判定":
            b.append((r[0], r[3]))
    return a, b


def appendix_rows(md, title):
    i = md.index(title)
    rows = []
    for line in md[i:].splitlines()[1:]:
        if line.startswith("### "):
            break
        if line.startswith("| ") and not line.startswith("| ID") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append((cells[0], cells[2]))
    return rows


def check(md, docx_path):
    errs = []
    heads = re.findall(r"^## (\d) ", md, re.M)
    if heads != [str(k) for k in range(10)]:
        errs.append(f"見出し ## 0〜## 9 の並びが違う: {heads}")
    paras = [p for p in md.split("\n\n") if p.strip() and not p.strip().startswith("<!--")]
    if not any(WARN in p for p in paras[:5]):
        errs.append("冒頭の 5 段落に「判定者 2 に渡さない」が無い")
    for m in BANNED.finditer(md):
        errs.append(f"禁止の語: {m.group(0)}")
    a, b = expected_appendix()
    if "### 9.1" not in md or appendix_rows(md, "### 9.1") != a:
        errs.append("付録 9.1 が 34 件の写しの判定者1 と違う")
    if "### 9.2" not in md or appendix_rows(md, "### 9.2") != b:
        errs.append("付録 9.2 が追加候補の表の判定者1 と違う")
    mt, dt = md_texts(md), docx_texts(docx_path)
    if mt != dt:
        k = next((k for k, (x, y) in enumerate(zip(mt, dt)) if x != y), min(len(mt), len(dt)))
        errs.append(f".docx の本文が原稿と違う（{k} 番目・原稿 {mt[k:k+1]} / docx {dt[k:k+1]}・件数 {len(mt)} / {len(dt)}）")
    return errs


def selftest():
    import build_proposal as B
    ok = True
    md = open(MD, encoding="utf-8").read()
    tmpd = tempfile.mkdtemp(prefix="propchk-")

    def run(name, md2, red, mutate_docx=None, must=None):
        nonlocal ok
        p = os.path.join(tmpd, "t.docx")
        B.build_docx(md2, p)
        if mutate_docx:
            d = Document(p)
            mutate_docx(d)
            d.save(p)
        errs = check(md2, p)
        hit = bool(errs) if must is None else any(must in e for e in errs)
        good = hit if red else not errs
        print(("PASS" if good else "FAIL"), name, "" if good else errs[:3])
        ok &= good
    run("negative-control（実の原稿）", md, red=False)
    run("heading-removed", md.replace("\n## 4 ", "\n## X ", 1), red=True, must="見出し")
    run("warning-moved", md.replace(WARN, "判定者 2 にお渡しにならない", 1), red=True, must="冒頭の 5 段落")
    run("banned-path", md.replace("## 0 この文書について", "## 0 この文書について（C:\\Users）", 1), red=True, must="禁止の語")
    run("banned-gse", md + "\nGSE の話\n", red=True, must="禁止の語")
    lines = md.splitlines()
    k = next(i for i, x in enumerate(lines) if x.startswith("| AF001 |"))
    lines[k] = lines[k].replace("| 含める |", "| 除外 |", 1)
    run("appendix-shifted", "\n".join(lines), red=True, must="付録 9.1")

    def mut(d):
        for p in d.paragraphs:
            if p.text.startswith("宛先"):
                p.runs[0].text = "宛先：別の人"
                break
    run("docx-paragraph-changed", md, red=True, mutate_docx=mut, must=".docx の本文")
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    md = open(MD, encoding="utf-8").read()
    errs = check(md, DOCX_ARCHIVE)
    rec = open(SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(SHA_RECORD) else None
    for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):
        if not os.path.exists(p) or C.sha256(p) != rec:
            errs.append(f".docx の SHA-256 が記録と違う・無い: {p}")
    for e in errs:
        print("NG", e)
    print("違反", len(errs))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
