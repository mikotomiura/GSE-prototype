#!/usr/bin/env python3
"""論文 2 の公開物（stall-shape-multiverse）を、GSE の作業ツリーの追跡済みのファイルから組み立てる。

usage: python3 -I assemble.py <GSE の checkout> <論文 1 の公開 repo> <出力先（無いか空）>
写す一覧はこのファイルが単一の記録。
- 実験の dir（experiments/20261107-stall-shape-multiverse）: 追跡済みの全部。md と run.sh は内部の参照を伏せた写し
  （研究者の判断 9）。伏せた数と元の SHA-256 を REDACTED.md に書く。
- 依存のスクリプト（KLiCKe・CS1・CoAuthor の変換）: 論文 1 の公開 repo と同じバイトであることを確かめて写す。
- 検出器の部品: candidates.py のうち使う Acc と gap_pool だけを、元の文字列のまま抜き出した写し（元のファイルは
  公開しない研究の解析を import するので、全体は出さない）。抜き出した文字列が元と同じであることを確かめる。
- 原稿: papers/stall-shape-multiverse/manuscript の追跡済みの全部（figdata を含む）を paper/ へ。
- tools/check_release.py と LICENSE は論文 1 の公開 repo から写す。
終了コード: 0 = 写した / 1 = 確かめが通らない / 2 = 使い方
"""
import ast
import hashlib
import os
import re
import shutil
import subprocess
import sys

EXP = "experiments/20261107-stall-shape-multiverse"
DEPS = ("experiments/20261101-klicke-early-stall-trigger/scripts",
        "experiments/20261104-cs1-landscape/scripts",
        "experiments/20261031-coauthor-pre-request-signal/scripts")
CAND = "experiments/20261103-stall-candidates-c1c2c6/candidates.py"
CAND_KEEP = ("Acc", "gap_pool")
PAPER = "papers/stall-shape-multiverse/manuscript"
FROM_P1 = ("tools/check_release.py", "LICENSE-MIT", "LICENSE-APACHE", "LICENSE-docs")
MARK = "[internal reference removed]"
PATTERNS = [
    re.compile(r"`(?:\.steering|docs|src-tauri)/[^`]*`"),
    re.compile(r"(?:\.steering|src-tauri)/[^\s）)、・`]+"),
    re.compile(r"\bdocs/[A-Za-z0-9_./-]+\.md\b"),
    re.compile(r"\[[VP]\d+\]"),
    re.compile(r"ADR-\d+(?: の \w+)?"),
    re.compile(r"(?:外枠の|原稿の|論文の)?判断 ?\d+(?: ?\(\d+\))?"),
]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def redact(text):
    n = 0
    for p in PATTERNS:
        text, k = p.subn(MARK, text)
        n += k
    return text, n


def tracked(src, path):
    out = subprocess.run(["git", "-C", src, "ls-files", "--", path], capture_output=True, text=True, check=True).stdout
    return [x for x in out.splitlines() if x]


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def main(src, p1, out):
    src, p1 = os.path.realpath(src), os.path.realpath(p1)
    if os.path.exists(out) and [x for x in os.listdir(out) if x != ".git"]:
        print("output dir is not empty", file=sys.stderr)
        sys.exit(2)
    os.makedirs(out, exist_ok=True)
    out = os.path.realpath(out)
    if out.startswith(src + os.sep):
        print("output must be outside the checkout", file=sys.stderr)
        sys.exit(2)
    dirty = subprocess.run(["git", "-C", src, "status", "--porcelain", "--", EXP, PAPER, CAND, *DEPS],
                           capture_output=True, text=True, check=True).stdout
    if dirty.strip():
        die("uncommitted changes:\n" + dirty)

    def put(rel, data):
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "wb").write(data)

    # 1) 実験の dir
    red = []
    files = tracked(src, EXP)
    if not files:
        die("no tracked files under " + EXP)
    for f in files:
        raw = open(os.path.join(src, f), "rb").read()
        if f.endswith(".md") or f.endswith("/run.sh"):
            text, n = redact(raw.decode("utf-8"))
            if n:
                red.append((f[len(EXP) + 1:], hashlib.sha256(raw).hexdigest(), n))
            put(f, text.encode("utf-8"))
        else:
            put(f, raw)
    lines = ["# Redacted copies", "",
             "In these files, references to the author's internal records (paths of working notes and design documents,",
             "numbers of internal decisions and of the internal reference list) were replaced by `%s`." % MARK,
             "Nothing else was changed. The SHA-256 is that of the original file in the author's repository.", "",
             "| File | SHA-256 of the original | References removed |", "|---|---|---|"]
    lines += ["| `%s` | `%s` | %d |" % r for r in red]
    put(EXP + "/REDACTED.md", ("\n".join(lines) + "\n").encode("utf-8"))

    # 2) 依存のスクリプト（論文 1 の公開 repo と同じバイト）
    for d in DEPS:
        fs = tracked(src, d)
        if not fs:
            die("no tracked files under " + d)
        for f in fs:
            a = os.path.join(src, f)
            b = os.path.join(p1, f)
            if not os.path.exists(b) or sha(a) != sha(b):
                die("differs from the paper 1 archive: " + f)
            put(f, open(a, "rb").read())

    # 3) 検出器の部品（Acc と gap_pool を元の文字列のまま）
    csrc = open(os.path.join(src, CAND), encoding="utf-8").read()
    tree = ast.parse(csrc)
    segs = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in CAND_KEEP:
            segs[n.name] = ast.get_source_segment(csrc, n)
    if set(segs) != set(CAND_KEEP):
        die("Acc / gap_pool not found in " + CAND)
    body = ['"""Excerpt of candidates.py: the two definitions the stall-shape scripts use, copied verbatim.',
            "",
            "The original file also imports analyses of a study that is not published, so only these two definitions",
            "are released. SHA-256 of the original file: %s" % sha(os.path.join(src, CAND)),
            '"""', "import bisect", "import math", "", ""]
    stub = "\n".join(body) + "\n\n\n".join(segs[k] for k in CAND_KEEP) + "\n"
    t2 = ast.parse(stub)
    for n in t2.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and ast.get_source_segment(stub, n) != segs[n.name]:
            die("excerpt differs from the original: " + n.name)
    put(CAND, stub.encode("utf-8"))

    # 4) 原稿
    fs = tracked(src, PAPER)
    if not fs:
        die("no tracked files under " + PAPER)
    for f in fs:
        put("paper/" + f[len(PAPER) + 1:], open(os.path.join(src, f), "rb").read())

    # 5) 論文 1 の公開 repo から
    for f in FROM_P1:
        put(f, open(os.path.join(p1, f), "rb").read())

    here = os.path.dirname(os.path.abspath(__file__))
    for a, b in (("verify.py", "tools/verify.py"), ("readme_media.py", "tools/readme_media.py"),
                 ("README.md", "README.md"), ("README.ja.md", "README.ja.md"), ("CITATION.cff", "CITATION.cff")):
        put(b, open(os.path.join(here, a), "rb").read())

    # 6) 出どころの表（GSE の commit）
    head = subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    put("source-commit.txt", (head + "\n").encode())
    subprocess.run([sys.executable, "-I", os.path.join(out, "tools/readme_media.py")], check=True, capture_output=True)
    print("assembled %d experiment files, %d redacted, into %s" % (len(files), len(red), out))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    main(*sys.argv[1:])
