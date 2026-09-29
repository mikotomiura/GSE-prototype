#!/usr/bin/env python3
# kit: selftest
"""Writes the public form of this directory to a new location (Python standard library only).

  export.py --out DIR [--allow-missing-license] [--also-user NAME ...] [--also-home PATH ...]
  export.py --selftest

The source is the directory two levels above kit/export/ (no version-control state is read). The
export

  1. leaves out raw logs, build products, sealed material and internal notes (every path the
     top-level ignore file names, plus *.internal.* and .DS_Store);
  2. removes the comments of the files and marked excerpts that the logger manifests pin to a
     checksum, replaces their non-ASCII string literals with the English literals of a translation
     table (kit/export/translations.internal.json, which is itself not exported), and adds a short
     English header to every whole pinned file;
  3. rewrites the manifests so that they keep only kind / id / path / symbol / sha256 / reason and
     recomputes every checksum from the exported bytes;
  4. rejects the export when any exported text contains a participant identifier, an e-mail address,
     an internal dataset or session name, an internal marker word or symbol, a home or repository
     path of the machine that runs the export, the login name of that machine, or a path that
     names a user (the fictional names in FICTIONAL are the only names that pass);
  5. verifies the exported logger manifests with check_manifest.py --self.

The output is byte-identical for the same source on any machine (LF line endings, sorted order, no
timestamps, no host-dependent content).

Exit code: 0 = exported / 1 = the export was refused because of its content (the partial export is
removed) / 2 = usage error, missing license text, unreadable or unsafe input.
"""
import argparse
import contextlib
import getpass
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):  # keeps non-ASCII output from crashing on a legacy console codepage
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_ROOT = os.path.dirname(os.path.dirname(HERE))
LOGGER = "kit/logger"
TRANSLATIONS = "kit/export/translations.internal.json"
HEADER = "// This file is checked against the manifest in this directory."
KEEP = ("kind", "id", "path", "symbol", "sha256", "reason")
# The only user names that may follow a home-directory prefix. Fictional examples used by the
# checkers and documents of this directory. It is a constant: nothing extends it at run time.
FICTIONAL = ("alice", "alice2", "bob", "carol", "dave", "erin", "gina", "harry", "YAMADA~1", "name")
LICENSES = ("LICENSE-CODE", "LICENSE-DATA")
NO_WORD_CHECK_PREFIX = "kit/corpus/data/"

# Words that must not reach the export. Built from pieces so that this file does not contain them.
_ORG = "G" + "SE"
_TAURI = "src" + "-tauri"
_STEER = "." + "steering"
_DATASET = "g" + "se-dataset"
_SESSION = "g" + r"se_\d{8}"
_STAR = chr(0x2605)
_WARN = chr(0x26A0)
AT = "@"
WORD_RULES = (
    ("internal-word", re.compile(r"(?<![A-Za-z0-9])" + _ORG[0] + _ORG[1:] + r"(?![A-Za-z0-9])", re.I)),
    ("internal-word", re.compile(r"(?<![A-Za-z0-9])(?:" + _ORG[0] + "se|" + _ORG + r")(?=[A-Z])")),
    ("internal-word", re.compile(re.escape(_TAURI))),
    ("internal-symbol", re.compile("[" + _STAR + _WARN + "]")),
)
ALWAYS_RULES = (
    ("participant-id", re.compile(r"(?<![A-Za-z0-9_])P\d{3}(?![A-Za-z0-9_])")),
    ("email-address", re.compile(r"[A-Za-z0-9._%+\-]+" + AT + r"[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+")),
    ("dataset-name", re.compile(re.escape(_DATASET), re.I)),
    ("session-name", re.compile(_SESSION, re.I)),
    ("internal-path", re.compile(re.escape(_STEER))),
)
BRACKETED_REF = re.compile(r"\[[PV]\d+(?:[,;\s\-]+[PV]?\d+)*\]")
_LB = r"(?<![A-Za-z0-9._~\-/\\])"
_NAME = r"([A-Za-z0-9_.~\-]+)"
_SEP = r"(?:\\\\|\\|/)"
USER_PATHS = (
    re.compile(_LB + r"[A-Za-z]:" + _SEP + r"(?i:Users)" + _SEP + _NAME),
    re.compile(_LB + r"/[A-Za-z]/(?i:Users)/" + _NAME),
    re.compile(_LB + r"/(?i:Users)/" + _NAME),
    re.compile(_LB + r"/home/" + _NAME),
)
MARKER = re.compile(r"^//\s*@excerpt-(?:begin|end)\s+\S+\s*$")
SL, SB = "\x00", "\x01"  # stand-ins for a removed line comment / block comment


class Stop(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code, self.msg = code, msg


# ---------------------------------------------------------------------------
# Rust lexing (just enough to tell comments from literals)
# ---------------------------------------------------------------------------
_IDENT = re.compile(r"[A-Za-z0-9_]+")
_CHAR = re.compile(r"'(?:\\(?:x[0-9A-Fa-f]{2}|u\{[0-9A-Fa-f_]+\}|[^\n])|[^\\'\n])'")
_RAW_OPEN = re.compile(r'(#*)"')


def _scan_string(text, j):
    """Returns the index just past the string literal whose opening quote is at j."""
    n, k = len(text), j + 1
    while k < n and text[k] != '"':
        k += 2 if text[k] == "\\" else 1
    return min(k + 1, n)


def lex_rust(text):
    """Splits Rust source into (kind, text) pieces: code / lc (line comment) / bc (block comment) /
    str (any string literal, prefix included) / chr (character literal)."""
    toks, i, n, cs = [], 0, len(text), 0

    def flush(upto):
        if upto > cs:
            toks.append(("code", text[cs:upto]))

    while i < n:
        c = text[i]
        if c == "/" and text.startswith("//", i):
            flush(i)
            j = text.find("\n", i)
            j = n if j < 0 else j
            toks.append(("lc", text[i:j]))
            i = cs = j
        elif c == "/" and text.startswith("/*", i):
            flush(i)
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/*", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("*/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            toks.append(("bc", text[i:j]))
            i = cs = j
        elif c == '"':
            flush(i)
            j = _scan_string(text, i)
            toks.append(("str", text[i:j]))
            i = cs = j
        elif c == "'":
            m = _CHAR.match(text, i)
            if m:
                flush(i)
                toks.append(("chr", m.group()))
                i = cs = m.end()
            else:
                i += 1  # a lifetime
        elif c.isascii() and (c.isalnum() or c == "_"):
            m = _IDENT.match(text, i)
            word, j = m.group(), m.end()
            end = None
            if word in ("r", "br", "cr"):
                m2 = _RAW_OPEN.match(text, j)
                if m2:
                    close = text.find('"' + m2.group(1), m2.end())
                    end = len(text) if close < 0 else close + 1 + len(m2.group(1))
            elif word in ("b", "c") and text.startswith('"', j):
                end = _scan_string(text, j)
            if end is not None:
                flush(i)
                toks.append(("str", text[i:end]))
                i = cs = end
            elif word == "b" and _CHAR.match(text, j):
                flush(i)
                m3 = _CHAR.match(text, j)
                toks.append(("chr", text[i:m3.end()]))
                i = cs = m3.end()
            else:
                i = j
        else:
            i += 1
    flush(n)
    return toks


def literal_kind(src):
    """The prefix of a string literal without its hashes (empty, r, b, br, c or cr)."""
    return src.split('"', 1)[0].replace("#", "")


def placeholders(src):
    body = src.replace("{{", "").replace("}}", "")
    return re.findall(r"\{[^{}]*\}", body)


def has_non_ascii(s):
    return any(ord(ch) > 127 for ch in s)


class Table(object):
    """The translation table: {(path, from): to}, plus which entries were used."""

    def __init__(self, entries):
        self.map, self.used = {}, set()
        for e in entries:
            self.map[(e["path"], e["from"])] = e["to"]

    def get(self, path, src):
        to = self.map.get((path, src))
        if to is not None:
            self.used.add((path, src))
        return to

    def unused(self):
        return sorted(k for k in self.map if k not in self.used)


def transform_rust(text, path, table, missing, base_line):
    """Removes comments and translates non-ASCII string literals. `missing` collects
    (line, path) for each untranslated literal. Returns the new text (with a final newline)."""
    out, line = [], base_line
    for kind, s in lex_rust(text):
        if kind == "lc":
            out.append(s if MARKER.match(s) else SL)
        elif kind == "bc":
            out.append("\n".join(SB for _ in s.split("\n")))
        elif kind == "str" and has_non_ascii(s):
            to = table.get(path, s)
            if to is None:
                missing.append((line, path))
                out.append(s)
            else:
                out.append(to)
        else:
            out.append(s)
        line += s.count("\n")
    kept = []
    for ln in "".join(out).split("\n"):
        if SL in ln or SB in ln:
            ln = ln.replace(SL, "").replace(SB, " ")
            if not ln.strip():
                continue
            ln = ln.rstrip()
        kept.append(ln)
    return "\n".join(kept)


def to_lines(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def marker_index(lines, want, what):
    hits = [i for i, l in enumerate(lines) if l.rstrip() == want]
    if len(hits) != 1:
        raise Stop(1, "%s does not occur exactly once (%d occurrences)" % (what, len(hits)))
    return hits[0]


def excerpt_bounds(lines, eid, rel):
    b = marker_index(lines, "// @excerpt-begin " + eid, rel + ": begin marker of " + eid)
    e = marker_index(lines, "// @excerpt-end " + eid, rel + ": end marker of " + eid)
    if e < b:
        raise Stop(1, "%s: the end marker of %s precedes its begin marker" % (rel, eid))
    return b, e


def entry_bytes(text, ent, rel):
    lines = to_lines(text)
    if ent["kind"] == "excerpt":
        b, e = excerpt_bounds(lines, ent["id"], rel)
        lines = lines[b + 1:e]
    return "".join(l + "\n" for l in lines).encode("utf-8")


def sha256_hex(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------
# collecting the source
# ---------------------------------------------------------------------------
_DIR_NAMES = frozenset(("target", ".build", "__pycache__", "runs", "sealed", ".venv", "venv", ".git"))
_ARCHIVE = (".zip", ".tar", ".tar.gz", ".tgz", ".zst")
_CORPUS_JSONL = re.compile(r"^kit/corpus/data/[^/]+\.jsonl$")


def excluded(rel, is_dir):
    parts = rel.split("/")
    if any(p in _DIR_NAMES or ".internal." in p for p in parts):
        return True
    if rel == "experiment/raw" or rel.startswith("experiment/raw/"):
        return True
    if is_dir:
        return False
    name = parts[-1]
    if name == ".DS_Store" or name.endswith(".ndjson") or ".ndjson." in name or ".jsonl." in name:
        return True
    if name.endswith(".jsonl"):
        return not _CORPUS_JSONL.match(rel)
    return name.endswith(_ARCHIVE)


def collect(root):
    """Returns {relative path: LF-normalized text} for every file that is exported."""
    files = {}
    for d, dirs, names in os.walk(root):
        reld = os.path.relpath(d, root).replace(os.sep, "/")
        reld = "" if reld == "." else reld
        keep = []
        for x in sorted(dirs):
            rel = (reld + "/" + x) if reld else x
            if excluded(rel, True):
                continue
            if os.path.islink(os.path.join(d, x)):
                raise Stop(2, "a symbolic link is not exported: " + rel)
            keep.append(x)
        dirs[:] = keep
        for x in sorted(names):
            rel = (reld + "/" + x) if reld else x
            if excluded(rel, False):
                continue
            full = os.path.join(d, x)
            if os.path.islink(full):
                raise Stop(2, "a symbolic link is not exported: " + rel)
            with open(full, "rb") as f:
                raw = f.read()
            try:
                if b"\x00" in raw:
                    raise ValueError("NUL")
                text = raw.decode("utf-8")
            except ValueError:
                raise Stop(2, "not a UTF-8 text file: " + rel)
            files[rel] = text.replace("\r\n", "\n").replace("\r", "\n")
    return files


def load_table(root):
    path = os.path.join(root, *TRANSLATIONS.split("/"))
    if not os.path.isfile(path):
        return Table([])
    try:
        with open(path, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        entries = data["entries"]
        for e in entries:
            if not (isinstance(e["path"], str) and isinstance(e["from"], str) and isinstance(e["to"], str)):
                raise TypeError("entry")
    except (ValueError, KeyError, TypeError, OSError):
        raise Stop(2, "the translation table is malformed: " + TRANSLATIONS)
    for i, e in enumerate(entries):
        where = "translation entry %d (%s)" % (i + 1, e["path"])
        to, src = e["to"], e["from"]
        if has_non_ascii(to):
            raise Stop(2, where + ": the replacement is not ASCII")
        pieces = lex_rust(to)
        if len(pieces) != 1 or pieces[0][0] != "str":
            raise Stop(2, where + ": the replacement is not a single string literal")
        if literal_kind(to) != literal_kind(src):
            raise Stop(2, where + ": the replacement is a different kind of literal")
        if placeholders(to) != placeholders(src):
            raise Stop(2, where + ": the format placeholders differ from the original")
        for _, rx in WORD_RULES + ALWAYS_RULES:
            if rx.search(to):
                raise Stop(2, where + ": the replacement contains a forbidden word")
    return Table(entries)


def load_manifests(files):
    out = []
    for rel in sorted(files):
        base = rel[len(LOGGER) + 1:] if rel.startswith(LOGGER + "/") else None
        if base and "/" not in base and base.startswith("manifest") and base.endswith(".json"):
            try:
                m = json.loads(files[rel])
                if not isinstance(m["entries"], list):
                    raise TypeError("entries")
                for e in m["entries"]:
                    e["kind"], e["path"], e["id"]
            except (ValueError, KeyError, TypeError):
                raise Stop(2, "the manifest is malformed: " + rel)
            out.append((rel, m))
    if not out:
        raise Stop(2, "no manifest found under " + LOGGER)
    return out


def convert_sources(files, manifests, table):
    """Applies the comment removal and the translation to the manifest-listed sources."""
    by_path = {}
    for _, m in manifests:
        for e in m["entries"]:
            by_path.setdefault(e["path"], []).append(e)
    missing = []
    for path in sorted(by_path):
        rel = LOGGER + "/" + path
        if rel not in files:
            raise Stop(1, "a manifest lists a file that does not exist: " + rel)
        ents = by_path[path]
        if any(e["kind"] == "file" for e in ents):
            body = transform_rust(files[rel], path, table, missing, 1)
            files[rel] = HEADER + "\n" + body
            continue
        lines = to_lines(files[rel])
        ranges = []
        for e in ents:
            if e["kind"] == "excerpt":
                ranges.append(excerpt_bounds(lines, e["id"], rel) + (e["id"],))
        for b, e, eid in sorted(ranges, reverse=True):
            inner = "\n".join(lines[b + 1:e]) + "\n"
            new = transform_rust(inner, path, table, missing, b + 2).split("\n")
            if new and new[-1] == "":
                new.pop()
            lines[b + 1:e] = new
        files[rel] = "\n".join(lines) + "\n"
    if missing:
        msg = ["a non-ASCII string literal has no translation:"]
        msg += ["  %s:%d" % (LOGGER + "/" + p, ln) for ln, p in sorted(set((ln, p) for ln, p in missing), key=lambda x: (x[1], x[0]))]
        raise Stop(1, "\n".join(msg))
    unused = table.unused()
    if unused:
        raise Stop(1, "translation entries that match nothing (update the table):\n" + "\n".join("  " + p for p, _ in unused))


def rewrite_manifests(files, manifests):
    for rel, m in manifests:
        entries = []
        for e in m["entries"]:
            ent = dict((k, e[k]) for k in KEEP if k in e)
            ent["sha256"] = sha256_hex(entry_bytes(files[LOGGER + "/" + e["path"]], e, LOGGER + "/" + e["path"]))
            entries.append(ent)
        files[rel] = json.dumps({"entries": entries}, ensure_ascii=False, indent=2) + "\n"


# ---------------------------------------------------------------------------
# the secrecy scan
# ---------------------------------------------------------------------------
def path_forms(p):
    p = p.strip()
    m = re.match(r"^/([A-Za-z])/(.*)$", p)
    if m:
        p = m.group(1).upper() + ":/" + m.group(2)
    fwd = p.replace("\\", "/").rstrip("/")
    forms = set([fwd, fwd.replace("/", "\\"), fwd.replace("/", "\\\\")])
    m = re.match(r"^([A-Za-z]):/(.*)$", fwd)
    if m:
        forms.add("/" + m.group(1).lower() + "/" + m.group(2))
    return sorted(f for f in forms if len(f) >= 4)


def machine_rules(root, also_users, also_homes):
    """Patterns for the values of the machine that runs the export: (kind, compiled pattern)."""
    homes = [os.path.expanduser("~"), os.environ.get("HOME", "")] + list(also_homes)
    top = ""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True, timeout=30)
        top = r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        pass
    tops = [top or os.path.dirname(os.path.dirname(os.path.abspath(root)))]
    rules = []
    for kind, values in (("home-directory", homes), ("repository-root", tops)):
        forms = set()
        for v in values:
            if v and v not in ("~", "/"):
                forms.update(path_forms(v))
        for f in sorted(forms):
            rules.append((kind, re.compile(_LB + re.escape(f) + r"(?![A-Za-z0-9_])", re.I)))
    names = set(n for n in also_users if n)
    for n in (os.environ.get("USERNAME"), os.environ.get("USER"), os.environ.get("LOGNAME")):
        if n:
            names.add(n)
    try:
        names.add(getpass.getuser())
    except Exception:
        pass
    for n in sorted(names):
        if len(n) >= 3:
            rules.append(("login-name", re.compile(r"(?<![A-Za-z0-9_])" + re.escape(n) + r"(?![A-Za-z0-9_])", re.I)))
    return rules


def scan(files, rules):
    """Returns [(path, line, kind)] for every hit. Values that matched are never reported."""
    hits = []
    for rel in sorted(files):
        word_check = not rel.startswith(NO_WORD_CHECK_PREFIX)
        for no, ln in enumerate(files[rel].split("\n"), 1):
            kinds = set()
            plain = BRACKETED_REF.sub(lambda m: " " * len(m.group()), ln)
            for kind, rx in ALWAYS_RULES:
                if rx.search(plain if kind == "participant-id" else ln):
                    kinds.add(kind)
            if word_check:
                for kind, rx in WORD_RULES:
                    if rx.search(ln):
                        kinds.add(kind)
            for kind, rx in rules:
                if rx.search(ln):
                    kinds.add(kind)
            for rx in USER_PATHS:
                for m in rx.finditer(ln):
                    name = m.group(1).rstrip(".")
                    if name and name not in FICTIONAL:
                        kinds.add("user-path")
            for kind in sorted(kinds):
                hits.append((rel, no, kind))
    return hits


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _inside(child, parent):
    a, b = os.path.realpath(child), os.path.realpath(parent)
    try:
        return os.path.commonpath([a, b]) == b
    except ValueError:
        return False


def _py_check_manifest(cwd_logger):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    return subprocess.run([sys.executable, os.path.join(cwd_logger, "check_manifest.py"), "--self", "--logger-dir", cwd_logger],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300)


def export(root, out, allow_missing_license, also_users, also_homes):
    root = os.path.abspath(root)
    if os.path.lexists(out):
        raise Stop(2, "the output path already exists (it is never overwritten)")
    if _inside(out, root):
        raise Stop(2, "the output path is inside the source directory")
    missing = [n for n in LICENSES if not os.path.isfile(os.path.join(root, n))]
    if missing and not allow_missing_license:
        raise Stop(2, "license text is missing: %s (place the official texts, or pass --allow-missing-license for a trial export)" % ", ".join(missing))
    ldir = os.path.join(root, *LOGGER.split("/"))
    if not os.path.isfile(os.path.join(ldir, "check_manifest.py")):
        raise Stop(2, "the source has no check_manifest.py under " + LOGGER)
    r = _py_check_manifest(ldir)
    if r.returncode != 0:
        raise Stop(1, "the source manifests do not match their files; nothing was exported:\n" + (r.stdout + r.stderr).strip()[-600:])
    files = collect(root)
    table = load_table(root)
    manifests = load_manifests(files)
    convert_sources(files, manifests, table)
    rewrite_manifests(files, manifests)
    hits = scan(files, machine_rules(root, also_users, also_homes))
    if hits:
        lines = ["the export contains content that must not be published (the matched text is not shown):"]
        lines += ["  %s:%d: %s" % h for h in hits[:200]]
        if len(hits) > 200:
            lines.append("  ... %d more" % (len(hits) - 200))
        raise Stop(1, "\n".join(lines))
    for rel in (".zenodo.json", "CITATION.cff"):
        if rel in files and "TODO" in files[rel]:
            print("WARNING: %s still contains TODO placeholders; fill them in before publishing." % rel)
    created = False
    try:
        os.makedirs(out)
        created = True
        for rel in sorted(files):
            p = os.path.join(out, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(files[rel].encode("utf-8"))
            if files[rel].startswith("#!"):
                os.chmod(p, 0o755)
        r = _py_check_manifest(os.path.join(out, *LOGGER.split("/")))
        if r.returncode != 0:
            raise Stop(1, "the exported manifests do not match the exported files:\n" + (r.stdout + r.stderr).strip()[-600:])
    except BaseException:
        if created:
            shutil.rmtree(out, ignore_errors=True)
        raise
    print("exported %d files to %s" % (len(files), out))
    return 0


def export_main(argv, root):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-missing-license", action="store_true")
    ap.add_argument("--also-user", action="append", nargs="+", default=[])
    ap.add_argument("--also-home", action="append", nargs="+", default=[])
    a = ap.parse_args(argv)
    flat = lambda xs: [x for group in xs for x in group]
    if a.allow_missing_license:
        print("NOTICE: this export is not for publication (--allow-missing-license). It is meant for trials and for building the measurement logger.")
    try:
        return export(root, os.path.abspath(a.out), a.allow_missing_license, flat(a.also_user), flat(a.also_home))
    except Stop as e:
        print(("ERROR: " if e.code == 2 else "REFUSED: ") + e.msg, file=sys.stderr)
        return e.code


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
def _jp(*codes):
    return "".join(chr(c) for c in codes)


JP1 = _jp(0x65E5, 0x672C, 0x8A9E)
JP2 = _jp(0x30C6, 0x30B9, 0x30C8)
JP3 = _jp(0x672A, 0x8A33)


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="export_selftest_")
    real_check = os.path.join(SOURCE_ROOT, "kit", "logger", "check_manifest.py")
    counter = [0]

    def ck(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    def put(base, rel, text):
        p = os.path.join(base, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(text.encode("utf-8"))

    a_rs = ("// header comment " + _STEER + "/x " + JP1 + "\n"
            "pub fn f<'a>(x: &'a str) -> &'a str { x } // trailing\n"
            "/// doc comment\n"
            'pub const S: &str = "a // not a comment /* nor this */";\n'
            'pub const R: &str = r#"raw // still "quoted" /* text */"#;\n'
            "pub const C: char = '\"'; /* block */\n"
            "/* outer /* nested */ still comment " + JP1 + " */\n"
            'pub const B: &[u8] = b"//";\n')
    e_rs = ("pub fn added() {} // kept: written for the logger\n"
            "// @excerpt-begin ex1\n"
            "// comment in range " + _STEER + "\n"
            "pub fn mirrored() {} // trailing " + JP1 + "\n"
            "// @excerpt-end ex1\n")
    t_rs = ("#[test]\nfn t() {\n"
            '    assert_eq!(1, 1, "' + JP1 + ' {} {x}");\n'
            '    assert!(true, r"' + JP2 + '");\n}\n')
    n_rs = 'pub const K: &str = "' + JP1 + '";\n'
    trans = {"entries": [
        {"path": "src/t.rs", "from": '"' + JP1 + ' {} {x}"', "to": '"Japanese text {} {x}"'},
        {"path": "src/t.rs", "from": 'r"' + JP2 + '"', "to": 'r"Second text"'},
    ]}
    specs = [("file", "a", "src/a.rs"), ("excerpt", "ex1", "src/e.rs"), ("new", "n", "src/n.rs"), ("file", "t", "src/t.rs")]

    def build(tag, extra=None, table=trans, crlf=()):
        base = os.path.join(tmp, tag, "papers", "ime-observation")
        files = {"README.md": "# Fake\n", "kit/notes.internal.md": "internal\n", "kit/data.jsonl": "{}\n",
                 "kit/corpus/data/p.jsonl": "{}\n", "src.txt": "x\n",
                 "kit/logger/src/a.rs": a_rs, "kit/logger/src/e.rs": e_rs, "kit/logger/src/t.rs": t_rs, "kit/logger/src/n.rs": n_rs}
        files.update(extra or {})
        for rel, text in files.items():
            put(base, rel, text.replace("\n", "\r\n") if rel in crlf else text)
        put(base, TRANSLATIONS, json.dumps(table))
        shutil.copy(real_check, os.path.join(base, "kit", "logger", "check_manifest.py"))
        entries = []
        for kind, eid, path in specs:
            ent = {"kind": kind, "id": eid, "path": path, "symbol": None, "sha256": "",
                   "reason": "written for the logger" if kind == "new" else None,
                   "up" + "stream_path": "x", "start_anchor": None, "check_decls": []}
            text = files["kit/logger/" + path]
            ent["sha256"] = sha256_hex(entry_bytes(text.replace("\r\n", "\n"), ent, path))
            entries.append(ent)
        put(base, "kit/logger/manifest.json", json.dumps({"up" + "stream_repo_commit": "0" * 40, "entries": entries}, indent=2))
        return base

    def run(tag, extra=None, argv=(), table=trans, crlf=(), license_files=False):
        base = build(tag, extra, table, crlf)
        if license_files:
            for n in LICENSES:
                put(base, n, "text\n")
        counter[0] += 1
        out = os.path.join(tmp, "out%d" % counter[0])
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = export_main(["--out", out] + ([] if license_files else ["--allow-missing-license"]) + list(argv), base)
        return rc, buf.getvalue() + err.getvalue(), out

    def read(out, rel):
        with open(os.path.join(out, *rel.split("/")), "rb") as f:
            return f.read().decode("utf-8")

    def refused(name, extra, needle, argv=(), forbid=()):
        rc, text, out = run(name.replace(" ", "-"), extra, argv)
        ck(name, rc == 1, "exit %d: %s" % (rc, text.strip()[-200:]))
        ck(name + " (nothing left behind)", not os.path.exists(out))
        ck(name + " (the file is named)", needle in text, text.strip()[-200:])
        for v in forbid:
            ck(name + " (the matched text is not shown)", v not in text)

    try:
        # lexer
        got = transform_rust(a_rs, "src/a.rs", Table([]), [], 1)
        ck("lexer keeps literals", '"a // not a comment /* nor this */"' in got and 'r#"raw // still "quoted" /* text */"#' in got
           and "'\"'" in got and 'b"//"' in got and "fn f<'a>(x: &'a str)" in got, got)
        ck("lexer removes comments", "//" not in got.replace("// not a comment", "").replace("raw //", "").replace('b"//"', "")
           and "header" not in got and "nested" not in got and JP1 not in got, got)

        rc, text, ok_out = run("base")
        ck("base export", rc == 0, text)
        if rc != 0:
            raise RuntimeError("the base export failed: " + text.strip())
        # a participant identifier stops the export
        pid = "P" + "017"
        refused("a participant identifier stops the export", {"README.md": "# Fake\nSession recorded by %s.\n" % pid}, "README.md", forbid=(pid,))
        addr = "who" + AT + "example.org"
        refused("an email address stops the export", {"README.md": "# Fake\nWrite to %s.\n" % addr}, "README.md", forbid=(addr,))
        rc, text, _ = run("ref", {"README.md": "# Fake\nSee [P269] and [V5].\n"})
        ck("a bracketed reference number passes", rc == 0, text)
        for word in (_ORG, _TAURI, _STAR, _WARN, _STEER + "/notes"):
            refused("an internal marker word stops the export", {"README.md": "# Fake\nSee %s here.\n" % word}, "README.md")
        # comments are stripped from manifest-listed sources
        ea, ee = read(ok_out, "kit/logger/src/a.rs"), read(ok_out, "kit/logger/src/e.rs")
        ck("comments are stripped from manifest-listed sources", ea.startswith(HEADER + "\n") and "header comment" not in ea
           and "trailing" not in ea and '"a // not a comment /* nor this */"' in ea and JP1 not in ea, ea)
        ck("comments are stripped from manifest-listed sources (excerpt)", "comment in range" not in ee and "// @excerpt-begin ex1" in ee
           and "// @excerpt-end ex1" in ee and "kept: written for the logger" in ee and "pub fn mirrored() {}" in ee and JP1 not in ee, ee)
        # internal fields are dropped from the public manifest
        m = json.loads(read(ok_out, "kit/logger/manifest.json"))
        ck("internal fields are dropped from the public manifest", list(m) == ["entries"]
           and all(set(e) <= set(KEEP) for e in m["entries"]) and len(m["entries"]) == len(specs), str(m)[:200])
        r = _py_check_manifest(os.path.join(ok_out, "kit", "logger"))
        ck("internal fields are dropped from the public manifest (the exported manifest verifies)", r.returncode == 0, r.stdout + r.stderr)
        # internal notes are not exported
        names = sorted(os.path.relpath(os.path.join(d, f), ok_out).replace(os.sep, "/") for d, _, fs in os.walk(ok_out) for f in fs)
        ck("internal notes are not exported", "kit/notes.internal.md" not in names and TRANSLATIONS not in names
           and "kit/data.jsonl" not in names and "kit/corpus/data/p.jsonl" in names, str(names))
        # home directory
        home = os.path.expanduser("~")
        for form in path_forms(home):
            refused("a real home directory stops the export", {"README.md": "# Fake\nOutput under %s/w.\n" % form}, "README.md", forbid=(form,))
        also = "Z:" + "\\lab\\zed-home"
        refused("a real home directory stops the export", {"README.md": "# Fake\nKept in %s\\runs.\n" % also}, "README.md", argv=["--also-home", also], forbid=(also,))
        rc, text, _ = run("also-off", {"README.md": "# Fake\nKept in %s\\runs.\n" % also})
        ck("a real home directory stops the export (not passed: exported)", rc == 0, text)
        refused("a real home directory stops the export", {"README.md": "# Fake\nPrepared by zedlogin.\n"}, "README.md", argv=["--also-user", "zedlogin"])
        # named user paths
        zed = "zed"
        for form in ("/Users/" + zed + "/x", "/home/" + zed + "/x", "C:\\Users\\" + zed + "\\x", "C:\\\\Users\\\\" + zed + "\\\\x", "/c/Users/" + zed + "/x", "D:/Users/" + zed):
            refused("a named user path stops the export", {"README.md": "# Fake\nPath %s.\n" % form}, "README.md", forbid=(form,))
        # fictional names
        ok_lines = ["/Users/alice/x", "C:\\Users\\bob\\x", "/home/dave/x", "/c/Users/name", "C:\\Users\\YAMADA~1\\x", "/Users/", "`/Users/`, `/home/`",
                    "kit/home/x ./Users/y", "/Users/alice2/z."]
        rc, text, _ = run("fiction", {"README.md": "# Fake\n" + "\n".join(ok_lines) + "\n"})
        ck("a fictional name on the allow list passes", rc == 0, text)
        # line endings
        rc, text, out = run("crlf", {"README.md": "# Fake\nline\n"}, crlf=("README.md", "kit/logger/src/a.rs", "kit/logger/src/n.rs"))
        ok = rc == 0 and all("\r" not in read(out, r) for r in ("README.md", "kit/logger/src/a.rs", "kit/logger/src/n.rs", "kit/logger/manifest.json"))
        ck("line endings are normalized to LF", ok, text)
        # translation
        et = read(ok_out, "kit/logger/src/t.rs")
        en = read(ok_out, "kit/logger/src/n.rs")
        ck("non-ASCII string literals are replaced from the translation table",
           '"Japanese text {} {x}"' in et and 'r"Second text"' in et and not has_non_ascii(et) and JP1 in en, et + en)
        refused("an untranslated string literal stops the export", {"kit/logger/src/t.rs": t_rs + 'const U: &str = "' + JP3 + '";\n'}, "t.rs")
        rc, text, _ = run("unused", table={"entries": trans["entries"] + [{"path": "src/t.rs", "from": '"' + JP3 + '"', "to": '"unused"'}]})
        ck("an untranslated string literal stops the export (an unused entry)", rc == 1, text)
        for label, bad in (("non-ASCII", '"caf' + chr(0xE9) + '"'), ("placeholders", '"Japanese text {} {y}"'), ("kind", '"Second text"'), ("word", '"' + _TAURI + '"')):
            tb = {"entries": [dict(trans["entries"][1], to=bad if label == "kind" else trans["entries"][1]["to"]),
                              dict(trans["entries"][0], to=bad if label != "kind" else trans["entries"][0]["to"])]}
            rc, text, _ = run("bad-" + label, table=tb)
            ck("an invalid replacement is a usage error (%s)" % label, rc == 2, "exit %d %s" % (rc, text))
        # license, existing output, output inside the source
        rc, text, out = run("lic", license_files=False, argv=())
        base = os.path.join(tmp, "lic2")
        b2 = build("lic2")
        counter[0] += 1
        o2 = os.path.join(tmp, "out%d" % counter[0])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc2 = export_main(["--out", o2], b2)
        ck("the export stops without the license text", rc2 == 2 and not os.path.exists(o2), "exit %d" % rc2)
        rc3, text3, _ = run("lic3", license_files=True)
        ck("the export passes with the license text", rc3 == 0 and "NOTICE" not in text3, text3)
        pre = os.path.join(tmp, "existing")
        put(pre, "keep.txt", "keep")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc4 = export_main(["--out", pre, "--allow-missing-license"], b2)
        ck("an existing output path is refused and left as it was", rc4 == 2 and os.listdir(pre) == ["keep.txt"], "exit %d" % rc4)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc5 = export_main(["--out", os.path.join(b2, "kit", "sub"), "--allow-missing-license"], b2)
        ck("an output path inside the source is refused", rc5 == 2, "exit %d" % rc5)
        # unsafe input
        rc, text, out = run("binary",{"README.md": "a\x00b\n"})
        ck("a binary file stops the export", rc == 2 and not os.path.exists(out), text)
        try:
            b3 = build("link")
            os.symlink(os.path.join(b3, "README.md"), os.path.join(b3, "link.md"))
            counter[0] += 1
            o3 = os.path.join(tmp, "out%d" % counter[0])
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc6 = export_main(["--out", o3, "--allow-missing-license"], b3)
            ck("a symbolic link stops the export", rc6 == 2 and not os.path.exists(o3), "exit %d" % rc6)
        except (OSError, NotImplementedError):
            pass
        # a manifest that no longer matches the source
        b4 = build("stale")
        put(b4, "kit/logger/src/n.rs", n_rs + "// changed\n")
        counter[0] += 1
        o4 = os.path.join(tmp, "out%d" % counter[0])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc7 = export_main(["--out", o4, "--allow-missing-license"], b4)
        ck("a source that does not match its manifest is refused", rc7 == 1 and not os.path.exists(o4), "exit %d" % rc7)
        # placeholders in the metadata warn
        rc, text, _ = run("todo", {".zenodo.json": '{"creators": [{"name": "TODO"}]}\n'})
        ck("a placeholder in the metadata warns without stopping", rc == 0 and "WARNING" in text, text)
        # two exports are byte-identical
        rc, _, o_a = run("twice-a")
        rc2, _, o_b = run("twice-b")
        def snap(o):
            return dict((os.path.relpath(os.path.join(d, f), o), open(os.path.join(d, f), "rb").read()) for d, _, fs in os.walk(o) for f in fs)
        ck("two exports are byte-identical", rc == 0 and rc2 == 0 and snap(o_a) == snap(o_b) and snap(o_a))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("NG:", f)
    if not fails:
        print("export selftest ok")
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv[1:]:
        return selftest()
    return export_main(sys.argv[1:], SOURCE_ROOT)


if __name__ == "__main__":
    sys.exit(main())
