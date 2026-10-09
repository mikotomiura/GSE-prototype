#!/usr/bin/env python3
"""公開物の書き方（判断 36）の機械検査。★ .steering に置く内部の道具で、公開 repo には書き出さない。

  python _style_check.py [--root <repo>] [PATH ...]   PATH を省くと papers/ime-observation 全体
  python _style_check.py --selftest

検査すること（違反は file:line と種類を出して exit 1。違反なしは exit 0。読めない・使い方の誤りは exit 2）:
  1. 禁止語（テキスト全体。ただし逐語コピーの範囲と manifest の出どころの欄は除く）:
     語としての GSE（大文字小文字を問わない）・src-tauri・.steering・★・⚠
  2. 日本語（ひらがな・カタカナ・漢字・全角の句読点）が「地の文」にあること:
     - Python: コメントと docstring
     - Rust: コメント（// /// //! /* */）。文字列リテラルは見ない
     - shell / .gitignore / .gitattributes: # 以降のコメント
     - Markdown: 地の文（``` のコードブロックとバッククォートの中は除く）
     - JSON: manifest の "reason"、規則ファイルの "_note"
     ★ 地の文の中でもバッククォートで囲んだ部分（例: `がっこう`）は許す（読みの例を示すため）。
     ★ README の日本語訳（論文の dir の根の README.ja.md・判断 219）は 2 を見ない（1 は見る）。

対象外: 逐語コピー（kit/logger/manifest*.json の kind が file のファイル全体と、excerpt の目印の間）、
kit/corpus/data/、*.internal.md、Cargo.lock、target/・__pycache__/ などの生成物、.jsonl / .ndjson。
"""
import argparse
import ast
import html
import io
import json
import os
import posixpath
import re
import sys
import tempfile
import tokenize
import unicodedata

FORBIDDEN = [
    ("gse", re.compile(r"(?<![A-Za-z0-9])gse(?![A-Za-z0-9])", re.IGNORECASE)),
    # 識別子の頭に大文字で続く形（例 GseRefInput・gseFoo・GSEState）も拾う
    ("gse", re.compile(r"(?<![A-Za-z0-9])(?:[Gg]se|GSE)(?=[A-Z])")),
    ("src-tauri", re.compile(r"src-tauri")),
    (".steering", re.compile(r"\.steering")),
    ("star", re.compile("★")),
    ("warning-sign", re.compile("⚠")),
    # 内部の番号（判断・issue・マイルストーン）は公開の読者に意味が無い
    ("internal-ref", re.compile(r"(?<![A-Za-z0-9])(decision|issue|judge?ment)s?\s+#?\d{1,3}(?![0-9])", re.IGNORECASE)),
    ("internal-ref", re.compile(r"(?<![A-Za-z0-9_])M(1[0-3]|[0-9])(?![A-Za-z0-9_])")),
    # 判断 43: 写した元（別の実装）との関係の説明も公開物に書かない
    ("relation", re.compile(r"reference (implementation|source)|upstream|verbatim cop(y|ies)", re.IGNORECASE)),
]
CJK = re.compile("[　-〿぀-ヿ㐀-䶿一-鿿！-｠]")
BACKTICK = re.compile(r"`[^`\n]*`")
SKIP_DIRS = {"target", ".build", "__pycache__", ".venv", "venv", "runs", "sealed"}
SKIP_SUFFIX = (".jsonl", ".ndjson", ".lock", ".pyc", ".png", ".pdf", ".zip")
TEXT_SUFFIX = (".py", ".rs", ".sh", ".md", ".json", ".toml", ".swift", ".txt", ".cff", ".tex", ".bib", ".svg")
UPSTREAM_KEYS = re.compile(r"^(gse_|upstream_)|^(start_anchor|end_anchor)$")
# 判断 219: 日本語の地の文を許すのは README の日本語訳だけ（論文の dir の根と、書き出した木の根）
TRANSLATIONS = ("README.ja.md", "papers/ime-observation/README.ja.md")
# 訳では日本語の検査が外れるので、内部の言葉の日本語の形も止める（全角は NFKC で半角に寄せてから見る）
JA_FORBIDDEN = [
    ("internal-ref", re.compile(r"(判断|課題|マイルストーン)\s*#?\d")),
    ("relation", re.compile(r"上流|逐語|参照実装|写した元")),
    ("gse", re.compile(r"苦闘")),
]


class Violation(object):
    def __init__(self, path, line, kind, detail):
        self.path, self.line, self.kind, self.detail = path, line, kind, detail

    def __str__(self):
        return "%s:%d: [%s] %s" % (self.path, self.line, self.kind, self.detail)


# ---------------------------------------------------------------- verbatim regions

def verbatim_map(root):
    """manifest*.json から {repo 相対パス: None（ファイル全体） or [excerpt id...]} を作る。"""
    out = {}
    base = os.path.join(root, "papers", "ime-observation", "kit", "logger")
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        if not (name.startswith("manifest") and name.endswith(".json")):
            continue
        try:
            with io.open(os.path.join(base, name), encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        for e in data.get("entries", []) if isinstance(data, dict) else []:
            if not isinstance(e, dict) or not isinstance(e.get("path"), str):
                continue
            rel = "papers/ime-observation/kit/logger/" + e["path"]
            if e.get("kind") == "file":
                out[rel] = None
            elif e.get("kind") == "excerpt":
                cur = out.get(rel, [])
                if cur is not None:
                    cur.append(e.get("id"))
                    out[rel] = cur
    return out


def mask_excerpts(lines, ids):
    """excerpt の目印の間（目印の行を含む）を空行に置き換える（行番号は保つ）。"""
    masked = list(lines)
    inside = None
    for i, line in enumerate(lines):
        s = line.strip()
        if inside is None:
            for x in ids:
                if s == "// @excerpt-begin %s" % x:
                    inside = x
                    masked[i] = ""
                    break
        else:
            masked[i] = ""
            if s == "// @excerpt-end %s" % inside:
                inside = None
    return masked


# ---------------------------------------------------------------- prose extraction

def py_prose(text):
    """(行番号, 文字列) のコメントと docstring。"""
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                out.append((tok.start[0], tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    nodes = [tree] + [n for n in ast.walk(tree)
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    for n in nodes:
        body = getattr(n, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            first = body[0].lineno
            for k, ln in enumerate(body[0].value.value.split("\n")):
                out.append((first + k, ln))
    return out


def rs_prose(text):
    """Rust のコメントだけを取り出す（文字列・文字リテラル・生文字列を飛ばす）。"""
    out = []
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append((line, text[i:j]))
            i = j
        elif text.startswith("/*", i):
            depth, j, start_line = 1, i + 2, line
            buf_start = i
            while j < n and depth:
                if text.startswith("/*", j):
                    depth += 1
                    j += 2
                elif text.startswith("*/", j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            chunk = text[buf_start:j]
            for k, ln in enumerate(chunk.split("\n")):
                out.append((start_line + k, ln))
            line += chunk.count("\n")
            i = j
        elif c == "r" and re.match(r'r#*"', text[i:i + 10]) and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")):
            m = re.match(r'r(#*)"', text[i:])
            hashes = m.group(1)
            end = text.find('"' + hashes, i + len(m.group(0)))
            end = n if end < 0 else end + 1 + len(hashes)
            line += text.count("\n", i, end)
            i = end
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == "\\":
                    j += 1
                j += 1
            line += text.count("\n", i, j)
            i = j + 1
        elif c == "'":
            m = re.match(r"'(\\.[^']*|[^\\'\n])'", text[i:])
            i = i + len(m.group(0)) if m else i + 1
        else:
            i += 1
    return out


def hash_prose(text):
    out = []
    for no, ln in enumerate(text.split("\n"), 1):
        in_s = in_d = False
        for k, ch in enumerate(ln):
            if ch == "'" and not in_d:
                in_s = not in_s
            elif ch == '"' and not in_s:
                in_d = not in_d
            elif ch == "#" and not in_s and not in_d and (k == 0 or ln[k - 1] in " \t"):
                out.append((no, ln[k:]))
                break
    return out


def md_prose(text):
    out, fence = [], False
    for no, ln in enumerate(text.split("\n"), 1):
        if ln.strip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            out.append((no, ln))
    return out


# 判断 212: 属性の値の中の > でタグを切らない（引用符の中を読み飛ばす）。空の <text/> は中身を持たない
SVG_ATTRS = r"""(?:[^>"']|"[^"]*"|'[^']*')*"""
SVG_TEXT_BODY = re.compile(r"(<text\b" + SVG_ATTRS + r"(?<!/)>)(.*?)(</text>)", re.S)
SVG_TAG = re.compile(r"<!--.*?-->|<(/?)([A-Za-z_][\w:.-]*)" + SVG_ATTRS + r"?(/?)>", re.S)
SVG_DRAWN = ("tspan", "textpath")


def svg_drawn_blank(body):
    """<text> の中身から、<text> 自身と <tspan>・<textPath> の直下の文字データ（図に描く文字）だけを消す。
    その中の別の要素（<title>・<desc> など）の文字データ・属性・コメントは残す（判断 212）。改行は保つ。"""
    out, stack, pos = [], [], 0

    def data(s):
        return re.sub(r"[^\n]", "", s) if not stack or stack[-1] in SVG_DRAWN else s
    for t in SVG_TAG.finditer(body):
        out.append(data(body[pos:t.start()]) + t.group(0))
        pos = t.end()
        if t.group(2) is None:  # コメント
            continue
        if t.group(1):
            if stack:
                stack.pop()
        elif not t.group(3):
            stack.append(t.group(2).split(":")[-1].lower())
    out.append(data(body[pos:]))
    return "".join(out)


def svg_prose(text):
    """判断 210・211・212: 公開 repo の図（SVG）。<text> の文字データ（図の中の入力の例として日本語を描く）だけを除き、
    残り（属性・<title>・<desc>・<style>・<metadata>・コメント・<tspan> の属性・<text> の中の <title> など）は
    すべて地の文として見る。文字参照（&#x…; など）は戻してから見る。行の番号は保つ。"""
    def blank(m):
        return m.group(1) + svg_drawn_blank(m.group(2)) + m.group(3)
    return [(no, html.unescape(ln)) for no, ln in enumerate(SVG_TEXT_BODY.sub(blank, text).split("\n"), 1)]


def json_prose(text):
    out = []
    try:
        data = json.loads(text)
    except ValueError:
        return out

    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(k, str) and UPSTREAM_KEYS.search(k):
                    continue
                if k in ("reason", "_note") and isinstance(x, str):
                    out.append((0, x))
                else:
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(data)
    return out


def json_forbidden_text(text):
    """JSON は出どころの欄を除いた値だけを禁止語の対象にする。"""
    try:
        data = json.loads(text)
    except ValueError:
        return text
    parts = []

    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(k, str) and UPSTREAM_KEYS.search(k):
                    continue
                parts.append(str(k))
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            parts.append(v)
    walk(data)
    return "\n".join(parts)


# ---------------------------------------------------------------- checking

def check_text(rel, text, verbatim):
    vs = []
    if rel in verbatim and verbatim[rel] is None:
        return vs
    lines = text.split("\n")
    if rel in verbatim and verbatim[rel]:
        lines = mask_excerpts(lines, verbatim[rel])
        text = "\n".join(lines)
    ext = os.path.splitext(rel)[1]
    body = json_forbidden_text(text) if ext == ".json" else text
    for kind, rx in FORBIDDEN:
        if ext == ".json":
            if rx.search(body):
                vs.append(Violation(rel, 0, "forbidden:" + kind, "禁止語がある"))
            continue
        for no, ln in enumerate(lines, 1):
            # 判断 211: SVG は文字参照（G&#x53;E など）を戻しても見る
            if rx.search(ln) or (ext == ".svg" and rx.search(html.unescape(ln))):
                vs.append(Violation(rel, no, "forbidden:" + kind, "禁止語がある"))
    base = os.path.basename(rel)
    if posixpath.normpath(rel.replace("\\", "/")) in TRANSLATIONS:
        # 判断 219: README の日本語訳（研究者の選択）だけは地の文が日本語。ほかの検査（禁止語）は見る
        prose = []
        for no, ln in enumerate(lines, 1):
            folded = unicodedata.normalize("NFKC", ln)
            for kind, rx in FORBIDDEN + JA_FORBIDDEN:
                if rx.search(folded) and not rx.search(ln):
                    vs.append(Violation(rel, no, "forbidden:" + kind, "禁止語がある（全角や日本語の形）"))
                elif rx.search(ln) and (kind, rx) in JA_FORBIDDEN:
                    vs.append(Violation(rel, no, "forbidden:" + kind, "禁止語がある（日本語の形）"))
    elif ext == ".py":
        prose = py_prose(text)
    elif ext in (".rs", ".swift"):
        prose = rs_prose(text)
    elif ext == ".sh" or base in (".gitignore", ".gitattributes") or ext == ".toml":
        prose = hash_prose(text)
    elif ext == ".md":
        prose = md_prose(text)
    elif ext == ".json":
        prose = json_prose(text)
    elif ext == ".svg":
        prose = svg_prose(text)
    elif ext in (".tex", ".bib"):
        # 判断 148: 原稿（LaTeX）と書誌は全文が公開の文なので、コメントも含めて全行を見る
        prose = list(enumerate(lines, 1))
    else:
        prose = []
    for no, ln in prose:
        if CJK.search(BACKTICK.sub("", ln)):
            vs.append(Violation(rel, no, "japanese-prose", "地の文に日本語がある"))
    return vs


def iter_files(root, paths):
    for p in paths:
        full = os.path.join(root, p)
        if os.path.isfile(full):
            # 明示したファイルでも *.internal.* は対象外（判断 43。style_ok は git diff の名前を直接渡す）
            if ".internal." not in os.path.basename(full):
                yield p.replace(os.sep, "/")
            continue
        for d, dirs, files in os.walk(full):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
            reld = os.path.relpath(d, root).replace(os.sep, "/")
            # repo の中（papers/ime-observation/kit/...）でも書き出した側（kit/...）でも除く
            if ("/" + reld + "/").find("/kit/corpus/data/") >= 0:
                continue
            for f in sorted(files):
                if f.endswith(SKIP_SUFFIX) or ".internal." in f:
                    continue
                if not (f.endswith(TEXT_SUFFIX) or f in (".gitignore", ".gitattributes")):
                    continue
                yield (reld + "/" + f) if reld != "." else f


def run(root, paths):
    verbatim = verbatim_map(root)
    vs = []
    for rel in iter_files(root, paths):
        try:
            with io.open(os.path.join(root, rel), encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            vs.append(Violation(rel, 0, "unreadable", type(e).__name__))
            continue
        vs.extend(check_text(rel, text, verbatim))
    return vs


# ---------------------------------------------------------------- selftest

def selftest():
    fails = []

    def expect(name, rel, text, kinds, verbatim=None):
        got = sorted(set(v.kind for v in check_text(rel, text, verbatim or {})))
        if got != sorted(kinds):
            fails.append("%s: 期待 %s・実際 %s" % (name, sorted(kinds), got))

    J = "日本語"  # 日本語
    expect("py 英語のコメントは通る", "a.py", "# English comment\nx = 1\n", [])
    expect("py 日本語のコメントは赤", "a.py", "# " + J + "\nx = 1\n", ["japanese-prose"])
    expect("py 日本語の docstring は赤", "a.py", '"""' + J + '"""\n', ["japanese-prose"])
    expect("py 文字列の日本語は通る", "a.py", "x = '" + J + "'\n", [])
    expect("py バッククォートの中の日本語は通る", "a.py", "# reading `" + J + "`\n", [])
    expect("py 禁止語 GSE は赤", "a.py", "# derived from the GSE logger\n", ["forbidden:gse"])
    expect("py 識別子の gse も赤", "a.py", "against_gse = 1\n", ["forbidden:gse"])
    expect("py gsettings のような語の一部は通る", "a.py", "# gsettings and diagnose\n", [])
    expect("rs 語の頭の Gse＋大文字は赤", "a.rs", 'fn f() { let c = "GseRefInputImm"; }\n', ["forbidden:gse"])
    expect("rs Gsettings のような語は通る", "a.rs", "// Gsettings and Gseq\n", [])
    expect("py 星印は赤", "a.py", "# ★ note\n", ["forbidden:star"])
    expect("py 内部の判断の番号は赤", "a.py", "# see decision 38\n", ["forbidden:internal-ref"])
    expect("py 内部の issue の番号は赤", "a.py", "# imported by issue 021\n", ["forbidden:internal-ref"])
    expect("py judgment の番号も赤", "a.py", "# see judgment 39/2\n", ["forbidden:internal-ref"])
    expect("rs 参照実装への言及は赤", "a.rs", "// matching the reference implementation's thread\n", ["forbidden:relation"])
    expect("py upstream は赤", "a.py", "def against_upstream(): pass\n", ["forbidden:relation"])
    expect("md verbatim copy は赤", "a.md", "This file is a verbatim copy.\n", ["forbidden:relation"])
    expect("py マイルストーンの番号は赤", "a.py", "# confirmed in the M5 pilot\n", ["forbidden:internal-ref"])
    expect("py M を含む普通の語は通る", "a.py", "# MAP decoding and M-estimators\nx_M1a = 1\n", [])
    expect("rs 日本語のコメントは赤", "a.rs", "// " + J + "\nfn f() {}\n", ["japanese-prose"])
    expect("rs 文字列の日本語は通る", "a.rs", 'fn f() { let s = "' + J + '"; }\n', [])
    expect("rs 文字列の中の // は注釈でない", "a.rs", 'fn f() { let s = "a // ' + J + '"; }\n', [])
    expect("rs ライフタイムで崩れない", "a.rs", "fn f<'a>(x: &'a str) {} // English\n", [])
    expect("rs ブロックコメントの日本語は赤", "a.rs", "/* " + J + " */\nfn f() {}\n", ["japanese-prose"])
    expect("rs src-tauri は赤", "a.rs", "// see src-tauri/x.rs\n", ["forbidden:src-tauri"])
    expect("md 地の文の日本語は赤", "a.md", "# Title\n" + J + "\n", ["japanese-prose"])
    expect("README の日本語訳は通る", "README.ja.md", "# Title\n" + J + "\n", [])
    expect("repo の中の README の日本語訳も通る", "papers/ime-observation/README.ja.md", J + "\n", [])
    expect("ほかの dir の README.ja.md は赤", "kit/README.ja.md", J + "\n", ["japanese-prose"])
    expect("ほかの名前の訳は赤", "README.zh.md", J + "\n", ["japanese-prose"])
    expect("README の日本語訳でも禁止語は赤", "README.ja.md", J + " GSE\n", ["forbidden:gse"])
    expect("./ の付いた README の日本語訳も通る", "./README.ja.md", J + "\n", [])
    expect("README の日本語訳の全角の禁止語は赤", "README.ja.md", "ＧＳＥ\n", ["forbidden:gse"])
    expect("README の日本語訳の判断の番号は赤", "README.ja.md", "判断 219 による\n", ["forbidden:internal-ref"])
    expect("README の日本語訳の全角の判断の番号も赤", "README.ja.md", "判断 ＃２１９\n", ["forbidden:internal-ref"])
    expect("README の日本語訳の上流は赤", "README.ja.md", "上流の実装\n", ["forbidden:relation"])
    expect("README の日本語訳の苦闘は赤", "README.ja.md", "生産的苦闘\n", ["forbidden:gse"])
    expect("ほかの日本語は訳では通る", "README.ja.md", "判断の材料と 2 つの設定\n", [])
    expect("\\ で区切った README の日本語訳も通る", "papers\\ime-observation\\README.ja.md", J + "\n", [])
    expect("md コードブロックの日本語は通る", "a.md", "```\n" + J + "\n```\n", [])
    expect("md .steering は赤", "a.md", "see .steering/x\n", ["forbidden:.steering"])
    expect("sh 日本語のコメントは赤", "a.sh", "echo ok # " + J + "\n", ["japanese-prose"])
    expect("tex 本文の日本語は赤", "a.tex", "\\section{Method}\n" + J + "\n", ["japanese-prose"])
    expect("tex コメントの日本語も赤", "a.tex", "% " + J + "\nText.\n", ["japanese-prose"])
    expect("tex 英語だけは通る", "a.tex", "\\section{Method}\nThe logger writes rows.\n", [])
    expect("tex 禁止語 GSE は赤", "a.tex", "The GSE logger.\n", ["forbidden:gse"])
    expect("bib 日本語の書誌は赤", "r.bib", "@article{k, title={" + J + "}}\n", ["japanese-prose"])
    # 判断 210: SVG は <title>・<desc>・コメントが地の文。<text> の日本語（図の中の入力の例）は通す
    expect("svg 図の中の日本語は通る", "a.svg", "<svg>\n<title>Demo</title>\n<text>" + J + "</text>\n</svg>\n", [])
    expect("svg title の日本語は赤", "a.svg", "<svg>\n<title>" + J + "</title>\n</svg>\n", ["japanese-prose"])
    expect("svg 複数行の desc の日本語は赤", "a.svg", "<svg>\n<desc>English\n" + J + "</desc>\n</svg>\n", ["japanese-prose"])
    expect("svg コメントの日本語は赤", "a.svg", "<svg>\n<!-- " + J + " -->\n</svg>\n", ["japanese-prose"])
    expect("svg 禁止語は図の中でも赤", "a.svg", "<svg>\n<text>GSE</text>\n</svg>\n", ["forbidden:gse"])
    # 判断 211: 地の文は <text> の文字データ以外のすべて。文字参照は戻して見る
    expect("svg 属性の日本語は赤", "a.svg", '<svg aria-label="' + J + '">\n</svg>\n', ["japanese-prose"])
    expect("svg style のコメントの日本語は赤", "a.svg", "<svg>\n<style>/* " + J + " */</style>\n</svg>\n", ["japanese-prose"])
    expect("svg metadata の日本語は赤", "a.svg", "<svg>\n<metadata>" + J + "</metadata>\n</svg>\n", ["japanese-prose"])
    expect("svg 文字参照の日本語は赤", "a.svg", "<svg>\n<title>&#x65E5;&#26412;</title>\n</svg>\n", ["japanese-prose"])
    expect("svg 文字参照の禁止語は赤", "a.svg", "<svg>\n<text>G&#x53;E</text>\n</svg>\n", ["forbidden:gse"])
    expect("svg tspan の中の日本語は通る", "a.svg", '<svg>\n<text x="1"><tspan fill="#fff">' + J + "</tspan></text>\n</svg>\n", [])
    # 判断 212: <text> の中の <title>・<desc> は地の文（図に描く文字は <text>・<tspan> の直下だけ）
    expect("svg text の中の title の日本語は赤", "a.svg", "<svg>\n<text><title>" + J + "</title>x</text>\n</svg>\n",
           ["japanese-prose"])
    expect("svg text の中の複数行の desc の日本語は赤", "a.svg", "<svg>\n<text><desc>a\n" + J + "</desc></text>\n</svg>\n",
           ["japanese-prose"])
    expect("svg text の中の title の後の文字は通る", "a.svg",
           "<svg>\n<text><title>Demo</title>" + J + "<tspan>" + J + "</tspan>" + J + "</text>\n</svg>\n", [])
    expect("svg text の中の空の title の後の文字は通る", "a.svg", "<svg>\n<text><title/>" + J + "</text>\n</svg>\n", [])
    expect("svg text の中のコメントの日本語は赤", "a.svg", "<svg>\n<text>x<!-- " + J + " --></text>\n</svg>\n",
           ["japanese-prose"])
    # 判断 212（/cross-review 2 巡目）: 属性の値の中の > でタグを切らない・空の <text/> は中身を持たない
    expect("svg 値に > のある tspan の属性の日本語は赤", "a.svg",
           '<svg>\n<text><tspan data-note=">' + J + '">x</tspan></text>\n</svg>\n', ["japanese-prose"])
    expect("svg 値に > のある text の属性の日本語は赤", "a.svg",
           "<svg>\n<text data-note='>" + J + "'>x</text>\n</svg>\n", ["japanese-prose"])
    expect("svg 値に / と > のある tspan の後の文字は通る", "a.svg",
           '<svg>\n<text><tspan fill="a/>b">' + J + "</tspan></text>\n</svg>\n", [])
    expect("svg 空の text の後の title の日本語は赤", "a.svg",
           "<svg>\n<text/>\n<title>" + J + "</title>\n<text>x</text>\n</svg>\n", ["japanese-prose"])
    expect("svg 空の text の後の地の文字の日本語は赤", "a.svg",
           "<svg>\n<text/>" + J + "\n<text>x</text>\n</svg>\n", ["japanese-prose"])
    expect("svg tspan の属性の日本語は赤", "a.svg", '<svg>\n<text><tspan aria-label="' + J + '">x</tspan></text>\n</svg>\n',
           ["japanese-prose"])
    expect("json reason の日本語は赤", "m.json", '{"entries":[{"reason":"' + J + '"}]}', ["japanese-prose"])
    expect("json 出どころの欄は見ない", "m.json",
           '{"entries":[{"gse_path":"src-tauri/x.rs","start_anchor":"// ' + J + '","reason":"ok"}]}', [])
    expect("逐語コピーのファイル全体は見ない", "papers/ime-observation/kit/logger/src/x.rs",
           "// " + J + " GSE\n", [], {"papers/ime-observation/kit/logger/src/x.rs": None})
    expect("excerpt の目印の間は見ない", "papers/ime-observation/kit/logger/src/y.rs",
           "// @excerpt-begin k\n// " + J + " GSE\n// @excerpt-end k\n// English\n", [],
           {"papers/ime-observation/kit/logger/src/y.rs": ["k"]})
    expect("excerpt の外は見る", "papers/ime-observation/kit/logger/src/y.rs",
           "// @excerpt-begin k\n// ok\n// @excerpt-end k\n// " + J + "\n", ["japanese-prose"],
           {"papers/ime-observation/kit/logger/src/y.rs": ["k"]})
    # 走査の対象外
    tmp = tempfile.mkdtemp(prefix="style_check_")
    try:
        os.makedirs(os.path.join(tmp, "papers", "ime-observation", "kit", "corpus", "data"))
        os.makedirs(os.path.join(tmp, "papers", "ime-observation", "kit", "x", "target"))
        with io.open(os.path.join(tmp, "papers", "ime-observation", "kit", "corpus", "data", "p.md"), "w",
                     encoding="utf-8") as f:
            f.write(J + "\n")
        with io.open(os.path.join(tmp, "papers", "ime-observation", "kit", "x", "target", "t.md"), "w",
                     encoding="utf-8") as f:
            f.write(J + "\n")
        with io.open(os.path.join(tmp, "papers", "ime-observation", "kit", "x", "NOTES.internal.md"), "w",
                     encoding="utf-8") as f:
            f.write("GSE " + J + "\n")
        with io.open(os.path.join(tmp, "papers", "ime-observation", "kit", "x", "ok.md"), "w",
                     encoding="utf-8") as f:
            f.write("English only.\n")
        if run(tmp, ["papers/ime-observation"]):
            fails.append("走査: データ・生成物・*.internal.md は対象外のはず")
        if run(tmp, ["papers/ime-observation/kit/x/NOTES.internal.md"]):
            fails.append("走査: 明示したファイルでも *.internal.* は対象外のはず")
        with io.open(os.path.join(tmp, "papers", "ime-observation", "kit", "x", "bad.md"), "w",
                     encoding="utf-8") as f:
            f.write(J + "\n")
        if len(run(tmp, ["papers/ime-observation"])) != 1:
            fails.append("走査: 対象の中の違反を 1 件拾うはず")
        # 判断 219: README の日本語訳は、repo の走査でも書き出した木の走査（根を論文の dir にして "."）でも通る
        with io.open(os.path.join(tmp, "papers", "ime-observation", "README.ja.md"), "w", encoding="utf-8") as f:
            f.write("# " + J + "\n" + J + "\n")
        paper = os.path.join(tmp, "papers", "ime-observation")
        found = [v.path for v in run(tmp, ["papers/ime-observation"])] + [v.path for v in run(paper, ["."])]
        if found != ["papers/ime-observation/kit/x/bad.md", "kit/x/bad.md"]:
            fails.append("走査: README の日本語訳は repo でも書き出した木でも通るはず（判断 219）: %s" % found)
        os.remove(os.path.join(tmp, "papers", "ime-observation", "README.ja.md"))
        os.makedirs(os.path.join(tmp, "papers", "ime-observation", "manuscript"))
        with io.open(os.path.join(tmp, "papers", "ime-observation", "manuscript", "m.tex"), "w",
                     encoding="utf-8") as f:
            f.write("The GSE logger.\n")
        if len(run(tmp, ["papers/ime-observation"])) != 2:
            fails.append("走査: .tex も走査の対象のはず（判断 148）")
        os.remove(os.path.join(tmp, "papers", "ime-observation", "manuscript", "m.tex"))
        # 判断 209: 公開 repo の .gitattributes も書き出すので、コメントの日本語と禁止語を見る
        with io.open(os.path.join(tmp, "papers", "ime-observation", ".gitattributes"), "w",
                     encoding="utf-8") as f:
            f.write("# " + J + "\n* text=auto eol=lf\n")
        if len(run(tmp, ["papers/ime-observation"])) != 2:
            fails.append("走査: .gitattributes のコメントも走査の対象のはず（判断 209）")
        os.remove(os.path.join(tmp, "papers", "ime-observation", ".gitattributes"))
        # 判断 210: 公開 repo の図（SVG）も走査する
        os.makedirs(os.path.join(tmp, "papers", "ime-observation", "assets"))
        with io.open(os.path.join(tmp, "papers", "ime-observation", "assets", "a.svg"), "w",
                     encoding="utf-8") as f:
            f.write("<svg>\n<title>" + J + "</title>\n</svg>\n")
        if len(run(tmp, ["papers/ime-observation"])) != 2:
            fails.append("走査: .svg も走査の対象のはず（判断 210）")
        os.remove(os.path.join(tmp, "papers", "ime-observation", "assets", "a.svg"))
        if len(run(tmp, ["papers/ime-observation/kit/x/bad.md", "papers/ime-observation/kit/x/NOTES.internal.md"])) != 1:
            fails.append("走査: 明示したファイルの違反は拾い、明示した *.internal.* は拾わないはず")
    finally:
        for d, _, files in os.walk(tmp, topdown=False):
            for f in files:
                os.remove(os.path.join(d, f))
            os.rmdir(d)
    if fails:
        for m in fails:
            print("FAIL " + m)
        print("selftest 失敗 %d 件" % len(fails))
        return 1
    print("selftest OK")
    return 0


def main(argv):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    root = os.path.abspath(a.root)
    paths = a.paths or ["papers/ime-observation"]
    for p in paths:
        if not os.path.exists(os.path.join(root, p)):
            print("_style_check: 無い: %s" % p, file=sys.stderr)
            return 2
    vs = run(root, paths)
    for v in vs[:200]:
        print(v)
    if len(vs) > 200:
        print("…ほか %d 件" % (len(vs) - 200))
    print("違反 %d 件" % len(vs))
    return 1 if vs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
