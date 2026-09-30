#!/usr/bin/env python3
# kit: selftest
"""Writes the public form of this directory to a new location (Python standard library only).

  export.internal.py --out DIR [--allow-missing-license] [--style-check PATH]
                     [--also-user NAME ...] [--also-home PATH ...]
  export.internal.py --selftest

This tool is internal: it is never exported (its name has the internal form). The source is the
directory two levels above kit/export/. When the source lies inside a git work tree, every exported
file (and the translation table) must be tracked and equal to the committed version, without an
assume-unchanged or skip-worktree mark, and every tracked file that is not excluded must have been
collected (otherwise exit 2), so that one commit always yields one output. A file whose name looks
like a secret, or whose content carries the signature of a secret, stops the export in every case.
The export

  1. leaves out raw logs, build products, sealed material and internal notes (every path the
     top-level ignore file names, plus *.internal.* and .DS_Store);
  2. removes the comments of the files and marked excerpts that the logger manifests pin to a
     checksum, replaces their non-ASCII string literals with the English literals of a translation
     table (kit/export/translations.internal.json, which is itself not exported), adds a short
     English header to every whole pinned file, and checks that the pinned ranges are ASCII only;
  3. rewrites the manifests so that they keep only kind / id / path / symbol / sha256 / reason and
     recomputes every checksum from the exported bytes;
  4. rejects the export when any exported text or file name contains a participant identifier, an
     e-mail address, an internal dataset or session name, an internal marker word or symbol, a home
     or repository path of the machine that runs the export, the login name of that machine, or an
     absolute path that names a user (the fictional names in FICTIONAL are the only names that
     pass). Every line is also checked after its JSON / string escapes are decoded;
  5. verifies the exported logger manifests with check_manifest.py --self;
  6. runs the checker of the writing rules of published files (_style_check.py, located with
     --style-check or in the git work tree of the source; inside a git work tree it must be committed)
     on the output.

The output is written to a sibling directory and renamed to --out only after steps 5 and 6 passed. A file
of a kind that the checker does not read is refused (exit 2).

The output is byte-identical for the same source on any machine (LF line endings, sorted order, no
timestamps, no host-dependent content).

Exit code: 0 = exported / 1 = the export was refused because of its content (the partial export is
removed) / 2 = usage error, missing license text, unreadable or unsafe input, a source that is not
committed, an unexpected failure.
"""
import argparse
import contextlib
import fnmatch
import getpass
import io
import json
import os
import re
import shutil
import socket
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
HEADER = "// The checksum of this file is pinned by the manifests in kit/logger (manifest*.json)."
KEEP = ("kind", "id", "path", "symbol", "sha256", "reason")
# The only user names that may follow a home-directory prefix. Fictional examples used by the
# checkers and documents of this directory. It is a constant: nothing extends it at run time.
FICTIONAL = ("alice", "alice2", "bob", "carol", "dave", "erin", "gina", "harry", "YAMADA~1", "name")
LICENSES = ("LICENSE-CODE", "LICENSE-DATA")
# The effective lines of the ignore file of the source directory. The export mirrors exactly this
# set (see excluded()); a line added to or removed from the ignore file stops the export.
IGNORE_FILE = ".gitignore"
IGNORE_LINES = frozenset((
    "**/target/", "**/.build/", "**/__pycache__/", "*.jsonl", "*.ndjson", "runs/", "sealed/",
    "experiment/raw/", "*.jsonl.*", "*.ndjson.*", "*.zip", "*.tar", "*.tar.gz", "*.tgz", "*.zst",
    ".venv/", "venv/", "!kit/corpus/data/*.jsonl"))
# File names (case-insensitive) that look like secrets. They are never exported and never skipped.
SECRET_NAMES = (".env", ".env.*", "*.pem", "*.key", "*age-identity*", "*.agekey", "*.age", "*token*.json",
                "credentials*.json", "client_secret*", "g1-submit*.json", "o1_submit*.json", "*.log",
                "*token*.txt", "*.token", "*.env", "key.txt", "id_rsa*", "id_ed25519*", "id_ecdsa*", "id_dsa*",
                ".netrc", "_netrc", ".npmrc", ".pypirc", ".git-credentials", "credentials", "*.ppk", "*.asc",
                "*secret*", ".ssh", ".gnupg", ".aws", ".docker", ".kube", ".pgpass")
# Signatures of secrets in the content of a file. Built from pieces so that this file does not spell them.
SECRET_CONTENT = (
    re.compile("AGE-SEC" + "RET-KEY-1"),
    re.compile("-----BEG" + "IN[A-Z ]*PRIV" + "ATE KEY(?: BLO" + "CK)?-----"),
    re.compile(r"(?<![A-Za-z0-9_])(?:gh" + "[prous]_|github" + "_pat_)[A-Za-z0-9_]{8,}"),
    re.compile(r"(?<![A-Za-z0-9_])gl" + r"pat-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"(?<![A-Z0-9])A(?:K" + "IA|S" + r"IA)[A-Z0-9]{16}(?![A-Z0-9])"),
    re.compile(r"(?<![A-Za-z0-9_])sk" + r"-ant-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9_])sk" + r"-proj-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9_])AI" + r"za[A-Za-z0-9_\-]{35}"),
    re.compile(r"(?<![A-Za-z0-9])xo" + r"x[abprs]-[A-Za-z0-9\-]{8,}"),
)
STYLE_REL = ".steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py"
STYLE_TIMEOUT = 300

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
    ("participant-id", re.compile(r"(?<![A-Za-z0-9])P\d{3}(?![A-Za-z0-9])")),
    ("email-address", re.compile(r"[A-Za-z0-9._%+\-]+" + AT + r"[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+")),
    ("dataset-name", re.compile(re.escape(_DATASET), re.I)),
    ("session-name", re.compile(_SESSION, re.I)),
    ("internal-path", re.compile(re.escape(_STEER))),
)
# An absolute-path token starts at "/", "\", a drive letter ("X:") or "file:" that does not follow a
# character of a name (a ":" is not one, so a path after "host:" or inside a URL is found), and runs
# to the next space, quote, angle bracket, "|", "*" or "?".
_TOKEN_START = r"(?<![A-Za-z0-9._~\-/\\_])(?:[/\\]|[A-Za-z]:|[Ff][Ii][Ll][Ee]:)"
ABS_TOKEN = re.compile(_TOKEN_START + r"[^\s\"'`<>|*?]*")
_COMP_SPLIT = re.compile(r"[/\\]")
_NAME_TAIL = ".,;:)"
_ESC_RE = re.compile(r"\\(u[0-9a-fA-F]{4}|.)", re.DOTALL)
_SIMPLE_ESC = {"b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
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


def literal_closed(src):
    """True when the string literal src ends exactly at its own closing quote (and, for a raw string,
    the closing run of hash marks)."""
    head = src.split('"', 1)[0]
    if '"' not in src:
        return False
    hashes = len(head) - len(head.rstrip("#"))
    body_start = len(head) + 1
    if head.rstrip("#").endswith("r"):
        close = src.find('"' + "#" * hashes, body_start)
        return close >= 0 and close + 1 + hashes == len(src)
    k = body_start
    while k < len(src) and src[k] != '"':
        k += 2 if src[k] == "\\" else 1
    return k == len(src) - 1


def placeholders(src):
    body = src.replace("{{", "").replace("}}", "")
    return re.findall(r"\{[^{}]*\}", body)


def has_non_ascii(s):
    return any(ord(ch) > 127 for ch in s)


class Table(object):
    """The translation table: {(path, from): to}, plus which entries were used."""

    def __init__(self, entries):
        self.map, self.used, self.index = {}, set(), {}
        for i, e in enumerate(entries):
            self.map[(e["path"], e["from"])] = e["to"]
            self.index[(e["path"], e["from"])] = i + 1

    def get(self, path, src):
        to = self.map.get((path, src))
        if to is not None:
            self.used.add((path, src))
        return to

    def unused(self):
        """[(entry number, path)] of the entries that matched nothing."""
        return sorted((self.index[k], k[0]) for k in self.map if k not in self.used)


def transform_rust(text, path, table, missing, base_line):
    """Removes comments and translates non-ASCII string literals. `missing` collects
    (line, path) for each untranslated literal. Returns the new text (with a final newline)."""
    if SL in text or SB in text:
        raise Stop(2, "%s contains a control character that the comment removal uses as a marker" % (LOGGER + "/" + path))
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
            # Only the white space directly before a comment that ends the line is dropped, so that
            # trailing spaces inside a string that continues on the next line stay.
            ln = re.sub("[ \t]*[" + SL + SB + "]+[ \t]*$", "", ln)
            ln = ln.replace(SL, "").replace(SB, " ")
            if not ln.strip():
                continue
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
_REPARSE_POINT = 0x400  # FILE_ATTRIBUTE_REPARSE_POINT (symbolic links, junctions, mount points)
# A name that holds the word "internal" but not in the internal form (".internal.") is neither exported
# nor skipped silently.
# (a letter on either side makes another word: internals, international; a lower-case letter directly before a
# capital I is a camel-case join: notesInternal)
_INTERNAL_NAME = re.compile(r"(?i:(?<![A-Za-z])internal(?![A-Za-z]))|(?<=[a-z])Internal(?![a-z])")


def excluded(rel, is_dir):
    """True when the path is left out of the export. Names are compared without regard to case."""
    low = rel.lower()
    parts = low.split("/")
    if any(p in _DIR_NAMES or ".internal." in p for p in parts):
        return True
    if low == "experiment/raw" or low.startswith("experiment/raw/"):
        return True
    if is_dir:
        return False
    name = parts[-1]
    if name == ".ds_store" or name.endswith(".ndjson") or ".ndjson." in name or ".jsonl." in name:
        return True
    if name.endswith(".jsonl"):
        return not _CORPUS_JSONL.match(low)
    return name.endswith(_ARCHIVE)


def check_ignore_file(root):
    """The effective lines of the ignore file must be exactly the rules that excluded() implements."""
    try:
        with open(os.path.join(root, IGNORE_FILE), "rb") as f:
            text = f.read().decode("utf-8")
    except (OSError, ValueError):
        raise Stop(2, "the ignore file is missing or unreadable: " + IGNORE_FILE)
    lines = set()
    for ln in text.replace("\r\n", "\n").split("\n"):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            lines.add(ln)
    if lines != IGNORE_LINES:
        raise Stop(2, "the ignore file and the exclusion rules of the export differ (%d lines): %s"
                   % (len(lines ^ IGNORE_LINES), ", ".join(sorted(lines ^ IGNORE_LINES))))


def is_secret_name(name):
    low = name.lower()
    return any(fnmatch.fnmatchcase(low, pat) for pat in SECRET_NAMES)


def is_link(full, root):
    """True for a symbolic link, a reparse point (a junction on Windows), or anything that resolves
    to a place outside the source."""
    if os.path.islink(full):
        return True
    try:
        attrs = getattr(os.lstat(full), "st_file_attributes", 0)
    except OSError:
        return True
    return bool(attrs & _REPARSE_POINT) or not _inside(full, root)


# The kinds of file that the checker of the writing rules reads (its TEXT_SUFFIX, its ignore-file name) and the
# names of the other files of the source that are allowed. Anything else would be exported without being checked.
CHECKED_SUFFIX = (".py", ".rs", ".sh", ".md", ".json", ".toml", ".swift", ".txt", ".cff")
CHECKED_NAMES = (".gitignore", "SEED", "Cargo.lock", "LICENSE-CODE", "LICENSE-DATA")


def check_file_type(rel):
    """A file that the checker of the writing rules does not read is not exported (exit 2). Under
    kit/corpus/data/ only the *.jsonl files directly in it are allowed."""
    name = rel.rsplit("/", 1)[-1]
    if rel.startswith("kit/corpus/data/"):
        if _CORPUS_JSONL.match(rel):
            return
        raise Stop(2, "a file in the corpus data that is not a jsonl file directly in it is not exported: " + rel)
    if name.endswith(CHECKED_SUFFIX) or name in CHECKED_NAMES:
        return
    raise Stop(2, "a file of a kind that the checker of the writing rules does not read is not exported"
               " (add the kind to the checker, or leave the file out): " + rel)


def collect(root):
    """Returns {relative path: LF-normalized text} for every file that is exported."""
    files = {}

    def onerror(err):
        where = getattr(err, "filename", None) or root
        try:
            rel = os.path.relpath(where, root).replace(os.sep, "/")
        except ValueError:
            rel = "(unknown)"
        raise Stop(2, "unreadable directory: " + rel)

    for d, dirs, names in os.walk(root, onerror=onerror):
        reld = os.path.relpath(d, root).replace(os.sep, "/")
        reld = "" if reld == "." else reld
        keep = []
        for x in sorted(dirs):
            rel = (reld + "/" + x) if reld else x
            if excluded(rel, True):
                continue
            if _INTERNAL_NAME.search(x):
                raise Stop(2, "a name that holds the word internal outside the internal form is neither exported nor skipped (rename it): " + rel)
            if is_link(os.path.join(d, x), root):
                raise Stop(2, "a link is not exported: " + rel)
            if is_secret_name(x):
                raise Stop(2, "a directory with the name of a secret is not exported (remove it from the source, or rename it if the name matched by chance): " + rel)
            keep.append(x)
        dirs[:] = keep
        for x in sorted(names):
            rel = (reld + "/" + x) if reld else x
            if excluded(rel, False):
                continue
            if _INTERNAL_NAME.search(x):
                raise Stop(2, "a name that holds the word internal outside the internal form is neither exported nor skipped (rename it): " + rel)
            full = os.path.join(d, x)
            if is_link(full, root):
                raise Stop(2, "a link is not exported: " + rel)
            if is_secret_name(x):
                raise Stop(2, "a file with the name of a secret is not exported (remove it from the source, or rename it if the name matched by chance): " + rel)
            check_file_type(rel)
            try:
                with open(full, "rb") as f:
                    raw = f.read()
            except OSError:
                raise Stop(2, "unreadable file: " + rel)
            try:
                if b"\x00" in raw:
                    raise ValueError("NUL")
                text = raw.decode("utf-8")
            except ValueError:
                raise Stop(2, "not a UTF-8 text file: " + rel)
            files[rel] = text.replace("\r\n", "\n").replace("\r", "\n")
    return files


def _git_env():
    env = dict((k, v) for k, v in os.environ.items()
               if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM"))
    env["LC_ALL"] = "C"
    return env


def _git(root, *args):
    r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, env=_git_env(), timeout=120)
    return r.returncode, r.stdout.decode("utf-8", errors="replace"), r.stderr.decode("utf-8", errors="replace")


def _dot_git_above(root):
    """True when a .git (a directory or a file) exists in root or above it."""
    d = os.path.abspath(root)
    while True:
        if os.path.lexists(os.path.join(d, ".git")):
            return True
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent


def git_top(root):
    """The top directory of the git work tree that contains root, or None when there is none."""
    try:
        rc, out, err = _git(root, "rev-parse", "--show-toplevel")
    except FileNotFoundError:
        # git cannot be found: a source inside a git work tree cannot be checked, so it cannot be exported
        if _dot_git_above(root):
            raise Stop(2, "git cannot be run, and the source is inside a git work tree (the committed state cannot be checked)")
        return None
    except (OSError, subprocess.SubprocessError):
        raise Stop(2, "git could not be run")
    if rc == 0:
        return out.strip()
    if "not a git repository" in err.lower():
        # a pruned work tree, a broken .git or a file system boundary looks like this too: never trust it
        if _dot_git_above(root):
            raise Stop(2, "git reports no repository, but a .git exists above the source (the committed state cannot be checked)")
        return None
    raise Stop(2, "git could not determine the work tree of the source (exit %d)" % rc)


def check_committed(root, files, extras=()):
    """The source is inside a git work tree: every exported file, and every extra input (the
    translation table), must be tracked, equal to HEAD and free of an assume-unchanged or
    skip-worktree mark, and every tracked file that is not excluded must have been collected."""
    def run(*args):
        rc, out, _ = _git(root, *args)
        if rc != 0:
            raise Stop(2, "git %s failed (exit %d)" % (args[0], rc))
        return out
    prefix = run("rev-parse", "--show-prefix").strip()
    tracked = {}  # relative path -> the tag of git ls-files -v
    for x in run("ls-files", "-v", "-z", "--full-name", "--", ".").split("\0"):
        if len(x) > 2 + len(prefix) and x[1] == " " and x[2:].startswith(prefix):
            tracked[x[2 + len(prefix):]] = x[0]
    # an extra input counts when it is there or when git tracks it (a deleted one must not escape the check)
    want = set(files) | set(x for x in extras if x in tracked or os.path.lexists(os.path.join(root, *x.split("/"))))
    changed = set()
    for ent in run("status", "--porcelain", "-z", "--no-renames", "--untracked-files=no", "--", ".").split("\0"):
        rel = ent[3:]
        if len(ent) > 3 and rel.startswith(prefix):
            r = rel[len(prefix):]
            if not excluded(r, False) or r in extras:
                changed.add(r)
    bad = sorted(set(rel for rel in want if rel not in tracked) | changed)
    flagged = sorted(rel for rel in want if rel in tracked and (tracked[rel].islower() or tracked[rel] == "S"))
    missed = sorted(rel for rel in tracked if not excluded(rel, False) and rel not in files)

    def block(head, names):
        lines = [head] + ["  " + rel for rel in names[:100]]
        if len(names) > 100:
            lines.append("  ... %d more" % (len(names) - 100))
        return lines
    lines = []
    if bad:
        lines += block("the source is inside a git work tree, and these files are not committed as they are"
                       " (export from a clean checkout of the commit to release):", bad)
    if flagged:
        lines += block("these files carry an assume-unchanged or skip-worktree mark in the git index (the check"
                       " cannot see their changes; clear the mark):", flagged)
    if missed:
        lines += block("these tracked files were not collected from the source (the export would differ from"
                       " the commit):", missed)
    if lines:
        raise Stop(2, "\n".join(lines))


def load_table(root):
    path = os.path.join(root, *TRANSLATIONS.split("/"))
    if not os.path.lexists(path):
        return Table([])
    if is_link(path, root):
        raise Stop(2, "the translation table is a link (it is read only as an ordinary file): " + TRANSLATIONS)
    if not os.path.isfile(path):
        raise Stop(2, "the translation table is not a file: " + TRANSLATIONS)
    try:
        with open(path, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        entries = data["entries"]
        for e in entries:
            if not (isinstance(e["path"], str) and isinstance(e["from"], str) and isinstance(e["to"], str)):
                raise TypeError("entry")
    except (ValueError, KeyError, TypeError, OSError):
        raise Stop(2, "the translation table is malformed: " + TRANSLATIONS)
    seen = set()
    for i, e in enumerate(entries):
        where = "translation entry %d (%s)" % (i + 1, e["path"])
        to, src = e["to"], e["from"]
        if (e["path"], src) in seen:
            raise Stop(2, where + ": the same original literal occurs in an earlier entry")
        seen.add((e["path"], src))
        if has_non_ascii(to):
            raise Stop(2, where + ": the replacement is not ASCII")
        if any((ord(ch) < 32 and ch != "\n") or ord(ch) == 127 for ch in to):
            raise Stop(2, where + ": the replacement contains a control character")
        pieces = lex_rust(to)
        if len(pieces) != 1 or pieces[0][0] != "str" or not literal_closed(to):
            raise Stop(2, where + ": the replacement is not a single, terminated string literal")
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
        ranges = set()
        for e in ents:
            if e["kind"] == "excerpt":
                ranges.add(excerpt_bounds(lines, e["id"], rel) + (e["id"],))
        ordered = sorted(ranges)
        for (b1, e1, id1), (b2, e2, id2) in zip(ordered, ordered[1:]):
            if b2 <= e1:
                raise Stop(2, "%s: the excerpts %s and %s overlap" % (rel, id1, id2))
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
        raise Stop(1, "translation entries that match nothing (update the table):\n" + "\n".join("  entry %d (%s)" % (n, p) for n, p in unused))


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
def check_secret_content(files):
    """A file whose content carries the signature of a secret stops the export (exit 2). The matched
    text is never shown."""
    hits = []
    for rel in sorted(files):
        for no, ln in enumerate(files[rel].split("\n"), 1):
            if any(rx.search(ln) for rx in SECRET_CONTENT) or ("\\" in ln and any(rx.search(unescape(ln)) for rx in SECRET_CONTENT)):
                hits.append("  %s:%d" % (rel, no))
    if hits:
        raise Stop(2, "content that looks like a secret is not exported (the text is not shown; remove it from the source,"
                   " or reword it if it matched by chance):\n" + "\n".join(hits[:100]))


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


def _hostname():
    try:
        return socket.gethostname()
    except OSError:
        return ""


def machine_rules(top, also_users, also_homes):
    """Patterns for the values of the machine that runs the export: (kind, compiled pattern).
    A value is searched for wherever it occurs, with no boundary on its left."""
    homes = [os.path.expanduser("~"), os.environ.get("HOME", "")] + list(also_homes)
    rules = []
    for kind, values in (("home-directory", homes), ("repository-root", [top])):
        forms = set()
        for v in values:
            if v and v not in ("~", "/"):
                forms.update(path_forms(v))
        for f in sorted(forms):
            rules.append((kind, re.compile(re.escape(f) + r"(?![A-Za-z0-9_])", re.I)))
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
    hosts = set()
    for h in (_hostname(), os.environ.get("COMPUTERNAME"), os.environ.get("HOSTNAME")):
        if h:
            hosts.add(h.strip())
            hosts.add(h.strip().split(".")[0])
    for h in sorted(hosts):
        if len(h) >= 3 and h.lower() != "localhost":  # a generic name is not this machine's private value
            rules.append(("host-name", re.compile(r"(?<![A-Za-z0-9_])" + re.escape(h) + r"(?![A-Za-z0-9_])", re.I)))
    return rules


def unescape(line):
    """The line with the escapes of a JSON or program string decoded (so that C:\\\\Users, \\u002f and
    \\/ are seen as the characters they stand for)."""
    def rep(m):
        g = m.group(1)
        if g[0] == "u" and len(g) == 5:
            return chr(int(g[1:], 16))
        return _SIMPLE_ESC.get(g, g)
    return _ESC_RE.sub(rep, line)


_COMPONENT = re.compile(r"(?:^|[/\\])(?:[Uu][Ss][Ee][Rr][Ss]|[Hh][Oo][Mm][Ee])(?=[/\\])")
_FLAG_TOKEN = re.compile(r"(?:^|(?<=[\s\"'`=]))-[ILF]((?:[/\\]|[A-Za-z]:)[^\s\"'`<>|*?]*)")
_WEB_SCHEME = re.compile(r"[Hh][Tt][Tt][Pp][Ss]?:$")
_DRIVE_IN_PATH = re.compile(r"/[A-Za-z]:(?=[/\\])")


def _user_in_token(tok):
    """True when a Users or home component of the token is followed by a name that is not fictional.
    After the component, every run of separator characters (of either kind, mixed or not) and every
    component that is a single dot is skipped; the next component is the name."""
    for m in _COMPONENT.finditer(tok):
        parts = _COMP_SPLIT.split(tok[m.end():])
        name = ""
        for part in parts[1:]:
            if part in ("", "."):
                continue
            name = part.rstrip(_NAME_TAIL)
            break
        if name and name not in FICTIONAL:
            return True
    return False


def names_a_user(text):
    """True when an absolute-path token of the text has a Users or home component that is followed by
    a name that is not one of the fictional names (separator runs and dot components are skipped
    before the name). Besides the tokens, the path after a -I / -L / -F compiler flag is checked. In
    the path of an http or https URL only a drive-letter form (/C:/Users/name) counts: the Users and
    home of a web path are not directories. A singly escaped path is found after the line is
    unescaped; a doubly escaped one is a known limitation."""
    for m in ABS_TOKEN.finditer(text):
        tok = m.group()
        if tok.startswith("//") and _WEB_SCHEME.search(text[:m.start()]):
            for d in _DRIVE_IN_PATH.finditer(tok):
                if _user_in_token(tok[d.start() + 1:]):
                    return True
            continue
        if _user_in_token(tok):
            return True
    for m in _FLAG_TOKEN.finditer(text):
        if _user_in_token(m.group(1)):
            return True
    return False


def line_kinds(text, word_check, rules):
    kinds = set()
    for kind, rx in ALWAYS_RULES:
        if rx.search(text):
            kinds.add(kind)
    if word_check:
        for kind, rx in WORD_RULES:
            if rx.search(text):
                kinds.add(kind)
    for kind, rx in rules:
        if rx.search(text):
            kinds.add(kind)
    if names_a_user(text):
        kinds.add("user-path")
    return kinds


def scan(files, rules):
    """Returns [(path, line, kind)] for every hit; line 0 is the file name itself. Every line is
    checked as written and with its escapes decoded. Values that matched are never reported."""
    hits = []
    for rel in sorted(files):
        word_check = not _CORPUS_JSONL.match(rel)
        for no, ln in [(0, rel)] + list(enumerate(files[rel].split("\n"), 1)):
            kinds = line_kinds(ln, word_check, rules)
            if "\\" in ln:
                kinds |= line_kinds(unescape(ln), word_check, rules)
            for kind in sorted(kinds):
                hits.append((rel, no, kind))
    return hits


def verify_ascii(files, manifests):
    """The exported range of every pinned file and excerpt must be ASCII only."""
    bad = []
    for _, m in manifests:
        for e in m["entries"]:
            if e["kind"] not in ("file", "excerpt"):
                continue
            rel = LOGGER + "/" + e["path"]
            lines = to_lines(files[rel])
            lo, hi = 0, len(lines)
            if e["kind"] == "excerpt":
                b, en = excerpt_bounds(lines, e["id"], rel)
                lo, hi = b + 1, en
            for i in range(lo, hi):
                if has_non_ascii(lines[i]):
                    bad.append("%s:%d" % (rel, i + 1))
    if bad:
        bad = sorted(set(bad))
        raise Stop(1, "the pinned range still holds non-ASCII text:\n" + "\n".join("  " + b for b in bad[:100]))


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


def check_tool_committed(tool):
    """The source is inside a git work tree: the checker must be tracked in the git work tree that
    holds it, equal to HEAD and free of an assume-unchanged or skip-worktree mark (exit 2)."""
    tdir, tname = os.path.dirname(tool), os.path.basename(tool)
    try:
        rc, out, _ = _git(tdir, "rev-parse", "--show-toplevel")
    except (OSError, subprocess.SubprocessError):
        raise Stop(2, "git could not be run on the checker of the writing rules")
    if rc != 0 or not out.strip():
        raise Stop(2, "the checker of the writing rules is not inside a git work tree (the source is; commit the checker there): " + tool)
    try:
        rc1, listed, _ = _git(tdir, "ls-files", "-v", "--", tname)
        rc2, status, _ = _git(tdir, "status", "--porcelain", "--untracked-files=no", "--", tname)
    except (OSError, subprocess.SubprocessError):
        raise Stop(2, "git could not be run on the checker of the writing rules")
    if rc1 != 0 or rc2 != 0:
        raise Stop(2, "git could not inspect the checker of the writing rules")
    tag = listed[:1]
    if not listed.strip() or listed[1:2] != " ":
        raise Stop(2, "the checker of the writing rules is not tracked by git (commit it): " + tool)
    if tag.islower() or tag == "S":
        raise Stop(2, "the checker of the writing rules carries an assume-unchanged or skip-worktree mark in the git index (clear the mark): " + tool)
    if status.strip():
        raise Stop(2, "the checker of the writing rules differs from the committed version (commit or restore it): " + tool)


def resolve_style_tool(top, given):
    """The checker of the writing rules of published files: the given path, or the fixed place in the
    git work tree of the source. It is never skipped silently."""
    if given:
        path = os.path.abspath(given)
    elif top:
        path = os.path.join(top, *STYLE_REL.split("/"))
    else:
        raise Stop(2, "the checker of the writing rules cannot be located: the source is not inside a git work tree (pass --style-check PATH)")
    if not os.path.isfile(path):
        raise Stop(2, "the checker of the writing rules does not exist: " + path)
    return path


# An executable file starts with "#!", optional blanks and a "/" ("#![" of a Rust attribute does not).
_SHEBANG = re.compile(r"#![ \t]*/")
_VIOLATION = re.compile(r"^(.+?:\d+: \[[^\]\r\n]+\])")


def run_style_check(tool, out):
    """Runs the checker on the output. Exit 1 of the tool (violations) refuses the export with the
    location and kind of each violation only; anything else than 0 or 1 is a usage error (exit 2)."""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([sys.executable, tool, "--root", out, "."], capture_output=True, env=env, timeout=STYLE_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise Stop(2, "the checker of the writing rules did not finish in time")
    except (OSError, subprocess.SubprocessError):
        raise Stop(2, "the checker of the writing rules could not be run")
    if r.returncode == 0:
        return
    if r.returncode != 1:
        raise Stop(2, "the checker of the writing rules failed (exit %d)" % r.returncode)
    text = r.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    found = []
    for ln in text.split("\n"):
        m = _VIOLATION.match(ln)
        if m:
            found.append(m.group(1))
    if not found:  # exit 1 without a single violation line: the tool crashed
        raise Stop(2, "the checker of the writing rules failed (exit 1 without a report)")
    count = len(found)
    tail = [ln for ln in text.split("\n") if ln.strip()][-1:]
    m = re.search(r"(\d+)\D*$", tail[0]) if tail and not _VIOLATION.match(tail[0]) else None
    if m:
        count = max(count, int(m.group(1)))
    lines = ["the output does not follow the writing rules of published files (the detail is not shown):"]
    lines += ["  " + x for x in found[:200]]
    if len(found) > 200:
        lines.append("  ... %d more" % (len(found) - 200))
    lines.append("  %d violations" % count)
    raise Stop(1, "\n".join(lines))


def export(root, out, allow_missing_license, also_users, also_homes, style_check=None):
    root = os.path.abspath(root)
    for n in also_users:
        if len(n) < 3:
            raise Stop(2, "--also-user: a name of fewer than 3 characters cannot be searched for reliably")
    if os.path.lexists(out):
        raise Stop(2, "the output path already exists (it is never overwritten)")
    if _inside(out, root):
        raise Stop(2, "the output path is inside the source directory")
    if not os.path.isdir(os.path.dirname(out)):
        raise Stop(2, "the parent directory of the output path does not exist (it is not created)")
    missing = [n for n in LICENSES if not os.path.isfile(os.path.join(root, n))]
    if missing and not allow_missing_license:
        raise Stop(2, "license text is missing: %s (place the official texts, or pass --allow-missing-license for a trial export)" % ", ".join(missing))
    ldir = os.path.join(root, *LOGGER.split("/"))
    if not os.path.isfile(os.path.join(ldir, "check_manifest.py")):
        raise Stop(2, "the source has no check_manifest.py under " + LOGGER)
    check_ignore_file(root)
    top = git_top(root)
    if top and _inside(out, top):
        raise Stop(2, "the output path is inside the git work tree of the source")
    style_tool = resolve_style_tool(top, style_check)
    if top:
        check_tool_committed(style_tool)
    files = collect(root)
    check_secret_content(files)
    if top:
        check_committed(root, files, [TRANSLATIONS])
    r = _py_check_manifest(ldir)
    if r.returncode != 0:
        raise Stop(1, "the source manifests do not match their files; nothing was exported:\n" + (r.stdout + r.stderr).strip()[-600:])
    table = load_table(root)
    manifests = load_manifests(files)
    convert_sources(files, manifests, table)
    verify_ascii(files, manifests)
    rewrite_manifests(files, manifests)
    check_secret_content(files)  # again, after the translation and the comment removal
    hits = scan(files, machine_rules(top or os.path.dirname(os.path.dirname(root)), also_users, also_homes))
    if hits:
        lines = ["the export contains content that must not be published (the matched text is not shown):"]
        lines += ["  %s:%d: %s" % h for h in hits[:200]]
        if len(hits) > 200:
            lines.append("  ... %d more" % (len(hits) - 200))
        raise Stop(1, "\n".join(lines))
    for rel in (".zenodo.json", "CITATION.cff"):
        if rel in files and "TODO" in files[rel]:
            print("WARNING: %s still contains TODO placeholders; fill them in before publishing." % rel)
    # The output is written to a sibling directory (same parent, a name that starts with a dot) and gets its
    # name only after every check has passed, so that an interrupted export never leaves something that
    # looks finished.
    work = os.path.join(os.path.dirname(out), "." + os.path.basename(out) + ".tmp-%d-%s" % (os.getpid(), os.urandom(4).hex()))
    created = False
    try:
        os.mkdir(work)
        created = True
        for rel in sorted(files):
            p = os.path.join(work, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(files[rel].encode("utf-8"))
            if _SHEBANG.match(files[rel]):
                os.chmod(p, 0o755)
        r = _py_check_manifest(os.path.join(work, *LOGGER.split("/")))
        if r.returncode != 0:
            raise Stop(1, "the exported manifests do not match the exported files:\n" + (r.stdout + r.stderr).strip()[-600:])
        run_style_check(style_tool, work)
        if os.path.lexists(out):
            raise Stop(2, "the output path appeared while the export was running (it is never overwritten)")
        try:
            os.rename(work, out)
        except OSError:
            raise Stop(2, "the output could not be moved to its final name")
        created = False
    except BaseException:
        if created:
            shutil.rmtree(work, ignore_errors=True)
            if os.path.lexists(work):
                print("WARNING: the partial output could not be removed completely; delete it before another export: " + work, file=sys.stderr)
        raise
    print("exported %d files to %s" % (len(files), out))
    return 0


def export_main(argv, root):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-missing-license", action="store_true")
    ap.add_argument("--style-check", default=None)
    ap.add_argument("--also-user", action="append", nargs="+", default=[])
    ap.add_argument("--also-home", action="append", nargs="+", default=[])
    a = ap.parse_args(argv)
    flat = lambda xs: [x for group in xs for x in group]
    if a.allow_missing_license:
        print("NOTICE: this export is not for publication (--allow-missing-license). It is meant for trials and for building the measurement logger.")
    try:
        return export(root, os.path.abspath(a.out), a.allow_missing_license, flat(a.also_user), flat(a.also_home), a.style_check)
    except Stop as e:
        print(("ERROR: " if e.code == 2 else "REFUSED: ") + e.msg, file=sys.stderr)
        return e.code
    except Exception as e:  # the message of an unexpected failure may hold a private value
        print("ERROR: unexpected failure (%s); nothing was exported" % type(e).__name__, file=sys.stderr)
        return 2


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
    tools = os.path.join(tmp, "tools")
    os.makedirs(tools)

    def stub(fname, body):
        path = os.path.join(tools, fname)
        with open(path, "wb") as f:
            f.write(body.encode("utf-8"))
        return path

    head = ("import os, sys\n"
            "assert sys.argv[1] == '--root' and sys.argv[3] == '.' and os.path.isfile(os.path.join(sys.argv[2], 'README.md')), sys.argv\n"
            "assert os.environ.get('PYTHONUTF8') == '1' and os.environ.get('PYTHONIOENCODING') == 'utf-8'\n")
    style_ok = stub("style_ok.py", head + "sys.exit(0)\n")
    style_bad = stub("style_bad.py", head + "print('x.md:3: [forbidden:gse] SECRETDETAIL ' + chr(0x26A0))\n"
                     "print('y.md:9: [japanese-prose] SECRETDETAIL')\n"
                     "print(chr(0x9055) + chr(0x53CD) + ' 2 ' + chr(0x4EF6))\nsys.exit(1)\n")
    loose_tool = os.path.join(tmp, "loose-style-ok.py")  # outside every git work tree
    with open(loose_tool, "wb") as f:
        f.write(open(style_ok, "rb").read())
    style_exit2 = stub("style_exit2.py", head + "sys.exit(2)\n")
    style_exit3 = stub("style_exit3.py", head + "sys.exit(3)\n")
    style_crash = stub("style_crash.py", head + "raise RuntimeError('boom')\n")
    style_hang = stub("style_hang.py", head + "import time\ntime.sleep(60)\n")
    style_probe = stub("style_probe.py", head + "root, want = os.path.abspath(sys.argv[2]), os.path.abspath(os.environ['EXPECT_OUT'])\n"
                       "assert os.path.basename(root).startswith('.') and os.path.dirname(root) == os.path.dirname(want), (root, want)\n"
                       "assert not os.path.exists(want), want\nsys.exit(0)\n")
    SA = ["--style-check", style_ok]

    def git_here(cwd, *args):
        return subprocess.run(["git", "-c", "user.name=selftest", "-c", "user.email=selftest" + AT + "example.invalid",
                               "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", "-C", cwd] + list(args),
                              capture_output=True, env=_git_env())
    try:
        have_git = subprocess.run(["git", "--version"], capture_output=True).returncode == 0
    except (OSError, subprocess.SubprocessError):
        have_git = False
    if have_git:  # the checkers are committed: a source inside a git work tree needs a committed checker
        have_git = git_here(tools, "init", "-q").returncode == 0 and git_here(tools, "add", ".").returncode == 0 \
            and git_here(tools, "commit", "-q", "-m", "tools").returncode == 0
    try:
        real_top = git_top(SOURCE_ROOT)
    except Stop:
        real_top = None
    REAL_STYLE = os.path.join(real_top, *STYLE_REL.split("/")) if real_top else ""

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
        files[IGNORE_FILE] = "\n".join(sorted(IGNORE_LINES, key=lambda x: (x.startswith("!"), x))) + "\n"
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
            rc = export_main(["--out", out] + ([] if license_files else ["--allow-missing-license"])
                             + ([] if "--style-check" in argv else SA) + list(argv), base)
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
        for joined in (pid + "_windows", "run_" + pid, "a-" + pid + ".json"):
            refused("a participant identifier stops the export", {"README.md": "# Fake\nSee %s here.\n" % joined}, "README.md")
        addr = "who" + AT + "example.org"
        refused("an email address stops the export", {"README.md": "# Fake\nWrite to %s.\n" % addr}, "README.md", forbid=(addr,))
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
                rc6 = export_main(["--out", o3, "--allow-missing-license"] + SA, b3)
            ck("a symbolic link stops the export", rc6 == 2 and not os.path.exists(o3), "exit %d" % rc6)
        except (OSError, NotImplementedError):
            pass
        # a git checkout: only committed files are exported
        def export_at(base, argv=()):
            counter[0] += 1
            o = os.path.join(tmp, "out%d" % counter[0])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rcx = export_main(["--out", o, "--allow-missing-license"] + SA + list(argv), base)
            return rcx, buf.getvalue(), o

        name = "an untracked or modified file in a git checkout stops the export"
        if not have_git:
            print("note: git is not available; the case '%s' is skipped" % name)
        else:
            gb = build("gitrepo")
            gtop = os.path.join(tmp, "gitrepo")
            ok = git_here(gtop, "init", "-q").returncode == 0 and git_here(gtop, "add", "papers").returncode == 0 \
                and git_here(gtop, "commit", "-q", "-m", "base").returncode == 0
            ck(name + " (the checkout is prepared)", ok)
            rcx, text, o = export_at(gb)
            ck(name + " (a committed checkout is exported)", rcx == 0, text)
            put(gb, "kit/draft-note.md", "A draft.\n")
            rcx, text, o = export_at(gb)
            ck(name + " (untracked)", rcx == 2 and "draft-note.md" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            os.remove(os.path.join(gb, "kit", "draft-note.md"))
            put(gb, "README.md", "# Fake\nEdited after the commit.\n")
            rcx, text, o = export_at(gb)
            ck(name + " (modified)", rcx == 2 and "README.md" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            put(gb, "README.md", "# Fake\n")
            os.remove(os.path.join(gb, "src.txt"))
            rcx, text, o = export_at(gb)
            ck(name + " (deleted)", rcx == 2 and "src.txt" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            put(gb, "src.txt", "x\n")
            rcx, text, o = export_at(gb)
            ck(name + " (clean again)", rcx == 0, text)
        # a secret file name
        for i, nm in enumerate((".env", ".ENV.local", "keys/deploy.pem", "notes/site-token-1.json", "Credentials.JSON", "run.LOG",
                                "my-age-identity.txt", "client_secret_1.txt")):
            rcx, text, o = run("secret%d" % i, {"kit/" + nm: "x\n"})
            ck("a secret file name stops the export (%s)" % nm, rcx == 2 and os.path.basename(nm) in text and not os.path.exists(o),
               "exit %d %s" % (rcx, text.strip()[-200:]))
        # a file name is checked like its content
        for i, nm in enumerate(("experiment/notes-" + pid + ".md", "experiment/" + _ORG + "-notes.md", "experiment/notes-" + _STEER + ".md")):
            rcx, text, o = run("fname%d" % i, {nm: "x\n"})
            ck("a file name is checked like its content (%d)" % i, rcx == 1 and os.path.basename(nm) in text and not os.path.exists(o),
               "exit %d %s" % (rcx, text.strip()[-200:]))
        # absolute path tokens with a user component
        bad_tokens = ("file://" + "/Users/" + zed + "/notes.txt", "\\\\?\\C:\\" + "Users\\" + zed + "\\w", "/mnt/c/Users/" + zed,
                      "/var/home/" + zed, "/Users/" + JP1 + "/x", "/Users/" + "alice+" + zed + "/x", "C:/Users/" + zed, "(see /home/" + zed + ")")
        for i, tok in enumerate(bad_tokens):
            rcx, text, o = run("tok%d" % i, {"README.md": "# Fake\nPath %s here.\n" % tok})
            ck("an absolute path token with a user component stops the export (%d)" % i, rcx == 1 and "README.md" in text and not os.path.exists(o),
               "exit %d %s" % (rcx, text.strip()[-200:]))
        ok_tokens = ("kit/home/x", "./Users/y", "Users/y", "/Users/", "/home/", "file:///Users/alice/x", "\\\\?\\C:\\Users\\bob\\w", "/mnt/c/Users/name/")
        rcx, text, o = run("tok-ok", {"README.md": "# Fake\n" + "\n".join("Path %s here." % t for t in ok_tokens) + "\n"})
        ck("an absolute path token with a user component stops the export (fictional and relative paths pass)", rcx == 0, text)
        # a link that leaves the source
        b5 = build("outlink")
        outside = os.path.join(tmp, "outside-dir")
        put(outside, "f.txt", "x\n")
        link = os.path.join(b5, "kit", "linked")
        linked = False
        if os.name == "nt":
            try:
                linked = subprocess.run(["cmd", "/c", "mklink", "/J", link, outside], capture_output=True).returncode == 0 and os.path.isdir(link)
            except (OSError, subprocess.SubprocessError):
                linked = False
        if not linked:
            try:
                os.symlink(outside, link, target_is_directory=True)
                linked = True
            except (OSError, NotImplementedError):
                linked = False
        if linked:
            rcx, text, o = export_at(b5)
            ck("a link that leaves the source stops the export", rcx == 2 and "linked" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            try:
                os.rmdir(link)
            except OSError:
                os.remove(link)
        else:
            print("note: a directory link could not be created here; the case 'a link that leaves the source stops the export' is skipped")
        # escaped spellings are decoded before the check
        u = "\\u"
        esc_bad = ('{"note": "' + u + '0050' + '017"}', '{"path": "' + u + '002fUsers' + u + '002f' + zed + '"}', '{"path": "\\/home\\/' + zed + '"}',
                   '{"path": "C:\\\\Users\\\\' + zed + '"}')
        for i, txt in enumerate(esc_bad):
            rcx, text, o = run("esc%d" % i, {"experiment/data.json": txt + "\n"})
            ck("an escaped spelling in JSON is checked after unescaping (%d)" % i, rcx == 1 and "data.json" in text and not os.path.exists(o),
               "exit %d %s" % (rcx, text.strip()[-200:]))
        rcx, text, o = run("esc-ok", {"experiment/data.json": '{"path": "' + u + '002fUsers' + u + '002falice", "v": "\\/home\\/bob"}\n'})
        ck("an escaped spelling in JSON is checked after unescaping (fictional names pass)", rcx == 0, text)
        # smaller checks of the input rules
        got = transform_rust('let s = /* c */ "abc   \n def";\nlet t = 1; /* d */\n', "src/a.rs", Table([]), [], 1)
        ck("the trailing spaces of a continued string are kept", '"abc   \n' in got and got.endswith("let t = 1;\n"), repr(got))
        rcx, text, o = run("short-user", argv=["--also-user", "ab"])
        ck("a short --also-user is a usage error", rcx == 2 and not os.path.exists(o), text)
        try:
            transform_rust("fn f() {}\n// \x01\n", "src/a.rs", Table([]), [], 1)
            ck("a marker control character in a pinned source is a usage error", False)
        except Stop as e:
            ck("a marker control character in a pinned source is a usage error", e.code == 2, e.msg)
        rcx, text, o = run("badclose", table={"entries": [dict(trans["entries"][0], to='"Japanese text {} {x}'), trans["entries"][1]]})
        ck("an unterminated replacement is a usage error", rcx == 2, text)
        rcx, text, o = run("dup", table={"entries": trans["entries"] + [trans["entries"][0]]})
        ck("a duplicate translation entry is a usage error", rcx == 2, text)
        rcx, text, o = run("ctrlto", table={"entries": [dict(trans["entries"][0], to='"Japanese\ttext {} {x}"'), trans["entries"][1]]})
        ck("a control character in a replacement is a usage error", rcx == 2, text)
        bx = build("ignore-file")
        put(bx, ".gitignore", "*.jsonl\n")
        rcx, text, o = export_at(bx)
        ck("an ignore file that differs from the exclusion rules is a usage error", rcx == 2 and not os.path.exists(o), text)
        bx = build("noparent")
        counter[0] += 1
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rcx = export_main(["--out", os.path.join(tmp, "no-such-dir", "out"), "--allow-missing-license"], bx)
        ck("a missing parent of the output path is a usage error", rcx == 2 and not os.path.exists(os.path.join(tmp, "no-such-dir")), "exit %d" % rcx)
        both = {"kit/logger/src/x.rs": "// @excerpt-begin a\nfn f() {}\n// @excerpt-begin b\n// @excerpt-end a\n// @excerpt-end b\n"}
        try:
            convert_sources(dict(both), [("m", {"entries": [{"kind": "excerpt", "id": "a", "path": "src/x.rs"}, {"kind": "excerpt", "id": "b", "path": "src/x.rs"}]})], Table([]))
            ck("overlapping excerpts are a usage error", False)
        except Stop as e:
            ck("overlapping excerpts are a usage error", e.code == 2, e.msg)
        rcx, text, o = run("upper", {"Runs/x.txt": "x\n", "kit/X.NDJSON": "{}\n", "kit/a.INTERNAL.md": "i\n", "kit/.ds_store": "x\n"})
        ck("names are excluded without regard to case", rcx == 0 and not any(os.path.exists(os.path.join(o, *r.split("/"))) for r in ("Runs/x.txt", "kit/X.NDJSON", "kit/a.INTERNAL.md", "kit/.ds_store")), text)
        # a manifest that no longer matches the source
        b4 = build("stale")
        put(b4, "kit/logger/src/n.rs", n_rs + "// changed\n")
        counter[0] += 1
        o4 = os.path.join(tmp, "out%d" % counter[0])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc7 = export_main(["--out", o4, "--allow-missing-license"] + SA, b4)
        ck("a source that does not match its manifest is refused", rc7 == 1 and not os.path.exists(o4), "exit %d" % rc7)
        # placeholders in the metadata warn
        rc, text, _ = run("todo", {".zenodo.json": '{"creators": [{"name": "TODO"}]}\n'})
        ck("a placeholder in the metadata warns without stopping", rc == 0 and "WARNING" in text, text)
        # a bracketed participant identifier is not a reference number: it stops the export (no exception)
        name = "a bracketed participant identifier stops the export"
        for txt in ("See [%s]." % pid, "See [%s, P021] here." % pid, "Sessions [%s; P021; P034]." % pid):
            refused(name, {"README.md": "# Fake\n" + txt + "\n"}, "README.md", forbid=(pid,))
        rcx, text, o = run("brfile", {"experiment/notes-[%s].md" % pid: "x\n"})
        ck(name + " (file name)", rcx == 1 and "notes-[" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        rcx, text, o = run("brother", {"README.md": "# Fake\nSee [V5], [12] and [P12].\n"})
        ck(name + " (other bracketed numbers pass)", rcx == 0, text)
        # git that cannot be run inside a work tree; a tree outside git is unaffected
        name = "git that cannot be run inside a work tree stops the export"
        saved_path = os.environ.get("PATH", "")
        os.environ["PATH"] = os.path.join(tmp, "no-such-bin")
        try:
            if shutil.which("git") is not None:
                print("note: git could not be hidden from PATH; the case '%s' is skipped" % name)
            elif have_git:
                rcx, text, o = export_at(gb)
                ck(name, rcx == 2 and "git" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
                rcx, text, o = export_at(build("no-git-at-all"))
                ck(name + " (a tree outside git is exported)", rcx == 0, text)
        finally:
            os.environ["PATH"] = saved_path
        if have_git:
            gtop = os.path.join(tmp, "gitrepo")
            # a modified, untracked or linked translation table
            name = "a modified or linked translation table stops the export"
            tp = os.path.join(gb, *TRANSLATIONS.split("/"))
            with open(tp, "rb") as f:
                orig = f.read()
            with open(tp, "ab") as f:
                f.write(b"\n")
            rcx, text, o = export_at(gb)
            ck(name + " (modified)", rcx == 2 and "translations" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            with open(tp, "wb") as f:
                f.write(orig)
            git_here(gtop, "rm", "--cached", "-q", "papers/ime-observation/" + TRANSLATIONS)
            rcx, text, o = export_at(gb)
            ck(name + " (untracked)", rcx == 2 and "translations" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            git_here(gtop, "add", "papers/ime-observation/" + TRANSLATIONS)
            rcx, text, o = export_at(gb)
            ck(name + " (clean again)", rcx == 0, text)
            name = "a deleted tracked translation table stops the export"
            os.remove(tp)
            rcx, text, o = export_at(gb)
            ck(name, rcx == 2 and "translations" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            with open(tp, "wb") as f:
                f.write(orig)
            rcx, text, o = export_at(gb)
            ck(name + " (restored)", rcx == 0, text)
        lb = build("linked-table")
        ltp = os.path.join(lb, *TRANSLATIONS.split("/"))
        put(lb, "kit/export/real-table.json", json.dumps(trans))
        os.remove(ltp)
        real_is_link = is_link
        try:
            os.symlink(os.path.join(lb, "kit", "export", "real-table.json"), ltp)
            how = "a symbolic link"
        except (OSError, NotImplementedError):
            shutil.copy(os.path.join(lb, "kit", "export", "real-table.json"), ltp)
            globals()["is_link"] = lambda full, base_dir: full.endswith("translations.internal.json") or real_is_link(full, base_dir)
            how = "a replaced link check"
        try:
            rcx, text, o = export_at(lb)
        finally:
            globals()["is_link"] = real_is_link
        ck("a modified or linked translation table stops the export (%s)" % how,
           rcx == 2 and "translation" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        # an unreadable directory (the walk is replaced by one that reports the error the way os.walk does)
        name = "an unreadable directory stops the export"
        real_walk = os.walk

        def walk_denied(top, topdown=True, onerror=None, followlinks=False):
            for d, dirs, names in real_walk(top, topdown, onerror, followlinks):
                if "experiment" in dirs:
                    dirs.remove("experiment")
                    if onerror:
                        onerror(OSError(13, "Permission denied", os.path.join(d, "experiment")))
                yield d, dirs, names
        ub = build("unreadable", {"experiment/notes.txt": "x\n"})
        os.walk = walk_denied
        try:
            rcx, text, o = export_at(ub)
        finally:
            os.walk = real_walk
        ck(name, rcx == 2 and "experiment" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        if os.name != "nt" and hasattr(os, "geteuid") and os.geteuid() != 0:
            ub2 = build("unreadable2", {"experiment/notes.txt": "x\n"})
            os.chmod(os.path.join(ub2, "experiment"), 0)
            try:
                rcx, text, o = export_at(ub2)
            finally:
                os.chmod(os.path.join(ub2, "experiment"), 0o755)
            ck(name + " (a real one)", rcx == 2 and "experiment" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        if have_git:
            # a tracked file that the walk missed
            name = "a tracked file that was not collected stops the export"

            def walk_missing(top, topdown=True, onerror=None, followlinks=False):
                for d, dirs, names in real_walk(top, topdown, onerror, followlinks):
                    if os.path.basename(d) == "kit" and "corpus" in dirs:
                        dirs.remove("corpus")
                    yield d, dirs, names
            os.walk = walk_missing
            try:
                rcx, text, o = export_at(gb)
            finally:
                os.walk = real_walk
            ck(name, rcx == 2 and "kit/corpus/data/p.jsonl" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            # an assume-unchanged or skip-worktree mark hides changes from git status
            name = "a file flagged as unchanged in the index stops the export"
            grel = "papers/ime-observation/README.md"
            for flag, undo in (("--assume-unchanged", "--no-assume-unchanged"), ("--skip-worktree", "--no-skip-worktree")):
                git_here(gtop, "update-index", flag, grel)
                put(gb, "README.md", "# Fake\nA hidden change.\n")
                rcx, text, o = export_at(gb)
                ck(name + " (%s and changed)" % flag, rcx == 2 and "README.md" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
                put(gb, "README.md", "# Fake\n")
                rcx, text, o = export_at(gb)
                ck(name + " (%s alone)" % flag, rcx == 2 and "README.md" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
                git_here(gtop, "update-index", undo, grel)
                rcx, text, o = export_at(gb)
                ck(name + " (%s cleared)" % flag, rcx == 0, text)
            # the output path inside the work tree of the source
            name = "an output path inside the work tree stops the export"
            o = os.path.join(gtop, "public-out")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rcx = export_main(["--out", o, "--allow-missing-license"] + SA, gb)
            ck(name, rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
        # secret-looking content (built from pieces: this file does not spell a secret)
        name = "secret-looking content stops the export"
        sigs = ["AGE-SEC" + "RET-KEY-1" + "Q" * 58, "-----BEG" + "IN OPENSSH PRIV" + "ATE KEY-----", "-----BEG" + "IN PRIV" + "ATE KEY-----"]
        sigs += ["gh" + c + "_" + "a1" * 15 for c in "pous"] + ["github" + "_pat_" + "b2" * 15, "gl" + "pat-" + "c3" * 10]
        sigs += ["AK" + "IA" + "ABCDEFGHIJKLMNOP", "xo" + "xb-" + "1234567890abcd"]
        sigs += ["-----BEG" + "IN PGP PRIV" + "ATE KEY BLO" + "CK-----", "sk" + "-ant-" + "a1" * 12, "sk" + "-proj-" + "b2" * 12,
                 "AI" + "za" + "c3" * 18, "gh" + "r_" + "d4" * 10, "AS" + "IA" + "ABCDEFGHIJKLMNOP"]
        for i, sig in enumerate(sigs):
            rcx, text, o = run("sig%d" % i, {"README.md": "# Fake\nToken: %s\n" % sig})
            ck(name + " (%d)" % i, rcx == 2 and "README.md:2" in text and sig[-12:] not in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        harmless = ("the prefix gh" + "p_ names a token", "AK" + "IA is a prefix", "-----BEG" + "IN PUBLIC KEY-----", "xo" + "xb- alone",
                    "sk" + "-ant- alone", "AI" + "za is a prefix", "AS" + "IA is a prefix")
        rcx, text, o = run("sig-ok", {"README.md": "# Fake\n" + "\n".join(harmless) + "\n"})
        ck(name + " (prose that only names a prefix passes)", rcx == 0, text)
        for i, nm in enumerate(("zenodo-token.txt", "a.TOKEN", "prod.env", "Key.txt", "id_rsa", "id_rsa.pub", "id_ed25519", "id_ecdsa", "id_dsa",
                                ".netrc", "_netrc", ".npmrc", ".pypirc", ".git-credentials", "credentials", "x.ppk", "x.asc", "my-Secret-notes.md")):
            rcx, text, o = run("sname%d" % i, {"kit/" + nm: "x\n"})
            ck("a secret file name stops the export (%s)" % nm, rcx == 2 and nm in text and "renam" in text and not os.path.exists(o),
               "exit %d %s" % (rcx, text.strip()[-200:]))
        # a doubled separator
        name = "a doubled separator does not hide a user path"
        for form in ("/Users//" + zed + "/x", "\\Users\\\\" + zed, "C:\\Users\\\\" + zed + "\\x", "/home///" + zed):
            refused(name, {"README.md": "# Fake\nPath %s here.\n" % form}, "README.md", forbid=(form,))
        rcx, text, o = run("dbl-ok", {"README.md": "# Fake\nPath /Users//alice/x and /Users// and /home///bob.\n"})
        ck(name + " (fictional names pass)", rcx == 0, text)
        # a path after a colon or inside a URL
        name = "a user path after a colon or inside a URL stops the export"
        for form in ("zed" + AT + "labhost:/home/" + zed + "/data", "root:/Users/" + zed, "path:C:\\Users\\" + zed, "https://host/C:/Users/" + zed,
                     "sftp://host/Users/" + zed, "vscode://file/C:/Users/" + zed):
            refused(name, {"README.md": "# Fake\nCopied from %s today.\n" % form}, "README.md", forbid=(form,))
        ok_forms = ("https://example.org/Users/alice/x", "see:/Users/", "a_/Users/" + zed, "x-/home/" + zed, "https://example.org/home", "host:/home/bob")
        rcx, text, o = run("colon-ok", {"README.md": "# Fake\n" + "\n".join("Path %s here." % t for t in ok_forms) + "\n"})
        ck(name + " (relative and fictional forms pass)", rcx == 0, text)
        # secret-looking content that appears only in the converted output, or only after the escapes are decoded
        name = "secret-looking content in the converted output stops the export"
        sig = "AGE-SEC" + "RET-KEY-1" + "Q" * 58
        tb = {"entries": [dict(trans["entries"][0], to='"Japanese text {} {x} ' + sig + '"'), trans["entries"][1]]}
        rcx, text, o = run("convsig", table=tb)
        ck(name + " (from the translation table)", rcx == 2 and "t.rs" in text and sig[-12:] not in text and not os.path.exists(o),
           "exit %d %s" % (rcx, text.strip()[-200:]))
        rcx, text, o = run("escsig", {"experiment/data.json": '{"k": "' + "\\" + "u0041" + "GE-SEC" + "RET-KEY-1" + "Q" * 58 + '"}\n'})
        ck(name + " (spelled with an escape)", rcx == 2 and "data.json" in text and "QQQQQQQQ" not in text and not os.path.exists(o),
           "exit %d %s" % (rcx, text.strip()[-200:]))
        # a mixed or dotted separator
        name = "a mixed or dotted separator does not hide a user path"
        for form in ("C:/Users/\\" + zed + "/x", "/Users/\\/" + zed, "/Users/./" + zed + "/x", "\\Users\\/" + zed, "/home/./\\" + zed, "/Users/././" + zed):
            refused(name, {"README.md": "# Fake\nPath %s here.\n" % form}, "README.md", forbid=(form,))
        rcx, text, o = run("mix-ok", {"README.md": "# Fake\nPath /Users/./alice/x and /Users/\\/bob and /Users/. and /home/./ end.\n"})
        ck(name + " (fictional names and prefixes pass)", rcx == 0, text)
        # a web URL path
        name = "a web URL path is not a user path"
        rcx, text, o = run("web-ok", {"README.md": "# Fake\nSee https://stackoverflow.com/users/12345/name and https://github.com/users/octocat/projects/1,\n"
                                      "https://example.org/home/docs and HTTP://example.org/Users/zed/x for reference.\n"})
        ck(name + " (web paths pass)", rcx == 0, text)
        for form in ("https://host/C:/Users/" + zed, "http://host/c:/Users/" + zed + "/x", "https://host/a/b/D:\\Users\\" + zed,
                     "scp://host/home/" + zed, "sftp://host/Users/" + zed):
            refused(name, {"README.md": "# Fake\nCopied from %s today.\n" % form}, "README.md", forbid=(form,))
        # a compiler flag
        name = "a compiler flag does not hide a user path"
        for form in ("cc -L/Users/" + zed + "/lib", "-I/home/" + zed + "/include", 'gcc "-F/Users/' + zed + '/f"', "CFLAGS=-L/Users/" + zed + "/lib",
                     "-LC:\\Users\\" + zed + "\\lib", "make LDFLAGS='-L/home/" + zed + "'"):
            refused(name, {"README.md": "# Fake\n%s\n" % form}, "README.md", forbid=(form,))
        rcx, text, o = run("flag-ok", {"README.md": "# Fake\n-L/Users/alice/lib -Lrelative/Users/" + zed + " -I/usr/include cc -I/home/bob/x\n"})
        ck(name + " (fictional names and other paths pass)", rcx == 0, text)
        # a .git above the source while git reports no repository
        name = "git that reports no repository under a .git stops the export"
        real_git_fn = globals()["_git"]
        globals()["_git"] = lambda root, *args: (128, "", "fatal: not a git repository (or any parent up to mount point /)\n")
        try:
            dg = build("dotgit-dir")
            os.makedirs(os.path.join(os.path.dirname(os.path.dirname(dg)), ".git"))
            rcx, text, o = export_at(dg)
            ck(name + " (a .git directory)", rcx == 2 and ".git" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
            rcx, text, o = export_at(build("dotgit-none"))
            ck(name + " (no .git anywhere: exported)", rcx == 0, text)
        finally:
            globals()["_git"] = real_git_fn
        if have_git:
            dg = build("dotgit-file")
            put(os.path.dirname(os.path.dirname(dg)), ".git", "gitdir: " + os.path.join(tmp, "no-such-gitdir") + "\n")
            rcx, text, o = export_at(dg)
            ck(name + " (a .git file that points nowhere)", rcx == 2 and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        # a kind of file that the style checker does not read
        name = "a file type that the style checker does not read stops the export"
        for nm in ("manuscript/draft.tex", "kit/ci.yml", "kit/noext", "kit/README.MD", "kit/.gitattributes", "kit/data.csv"):
            rcx, text, o = run("type-" + nm.replace("/", "_"), {nm: "x\n"})
            ck(name + " (%s)" % nm, rcx == 2 and os.path.basename(nm) in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        kinds_ok = dict(("kit/kinds/" + n, "x\n") for n in ("a.py", "a.rs", "a.sh", "a.md", "a.json", "a.toml", "a.swift", "a.txt", "a.cff",
                                                           ".gitignore", "SEED", "Cargo.lock", "LICENSE-CODE", "LICENSE-DATA"))
        rcx, text, o = run("kinds-ok", kinds_ok)
        ck(name + " (the allowed kinds pass)", rcx == 0, text)
        # a secret-looking directory name
        name = "a secret-looking directory name stops the export"
        for nm in ("kit/.aws/config.md", "kit/.ssh/x.md", "kit/.gnupg/x.md", "kit/.docker/x.md", "kit/.kube/x.md", "kit/.pgpass/x.md", "kit/my-secret/x.md",
                   "kit/keys.pem/x.md", "kit/.env/x.md"):
            rcx, text, o = run("sdir-" + nm.replace("/", "_"), {nm: "x\n"})
            d = nm.split("/")[1]
            ck(name + " (%s)" % d, rcx == 2 and d in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        rcx, text, o = run("sdir-ok", {"kit/tokenizer/x.md": "x\n"})
        ck(name + " (a name that does not match passes)", rcx == 0, text)
        # the output is renamed into place only after every check has passed
        name = "the output appears only after every check passed"

        def dotted():
            return sorted(n for n in os.listdir(tmp) if n.startswith("."))
        counter[0] += 1
        os.environ["EXPECT_OUT"] = os.path.join(tmp, "out%d" % counter[0])
        try:
            counter[0] -= 1
            rcx, text, o = run("probe", argv=["--style-check", style_probe])
        finally:
            os.environ.pop("EXPECT_OUT", None)
        ck(name, rcx == 0 and os.path.isdir(o) and dotted() == [], "exit %d %s %s" % (rcx, text.strip()[-300:], dotted()))
        rcx, text, o = run("probe-bad", argv=["--style-check", style_bad])
        ck(name + " (a violation leaves nothing)", rcx == 1 and not os.path.exists(o) and dotted() == [], "exit %d %s" % (rcx, dotted()))
        real_rename = os.rename

        def bad_rename(a, b, *args, **kw):
            raise OSError(13, "denied")
        os.rename = bad_rename
        try:
            rcx, text, o = run("probe-rename")
        finally:
            os.rename = real_rename
        ck(name + " (a failed rename leaves nothing)", rcx == 2 and not os.path.exists(o) and dotted() == [], "exit %d %s" % (rcx, dotted()))
        rcx, text, o = run("probe-exists")
        ck(name + " (nothing is left after a success)", rcx == 0 and dotted() == [], "exit %d %s" % (rcx, dotted()))
        # the host name of the machine that runs the export
        name = "the host name stops the export"
        fake_host = "labhost" + "-7"
        saved_env, real_gethostname = os.environ.get("COMPUTERNAME"), socket.gethostname
        try:
            os.environ["COMPUTERNAME"] = fake_host + ".example.org"
            refused(name, {"README.md": "# Fake\nMeasured on %s last week.\n" % fake_host.upper()}, "README.md", forbid=(fake_host,))
            os.environ["COMPUTERNAME"] = "ab"
            socket.gethostname = lambda: "gearbox9.local"
            refused(name, {"README.md": "# Fake\nRun on gearbox9 twice.\n"}, "README.md", forbid=("gearbox9",))
            rcx, text, o = run("host-ok", {"README.md": "# Fake\nRun on gearbox90 and on %s twice.\n" % fake_host})
            ck(name + " (a longer word and a value that is not this machine's pass)", rcx == 0, text)
            # a generic host name is not a private value of the machine
            socket.gethostname = lambda: "localhost"
            rcx, text, o = run("host-generic", {"README.md": "# Fake\nThe server listens on localhost only.\n"})
            ck(name + " (the generic name localhost is not searched)", rcx == 0, text)
        finally:
            socket.gethostname = real_gethostname
            if saved_env is None:
                os.environ.pop("COMPUTERNAME", None)
            else:
                os.environ["COMPUTERNAME"] = saved_env
        # the word check is skipped only for the corpus data files
        name = "the word check is skipped only for corpus data files"
        rcx, text, o = run("corpus-ok", {"kit/corpus/data/q.jsonl": "a line about %s\n" % _ORG})
        ck(name + " (a corpus data file)", rcx == 0 and os.path.exists(os.path.join(o, "kit", "corpus", "data", "q.jsonl")), text)
        name = "a file in the corpus data other than a jsonl stops the export"
        for nm in ("kit/corpus/data/notes.md", "kit/corpus/data/sub/q.md", "kit/corpus/data/q.txt"):
            rcx, text, o = run("corp-" + nm.replace("/", "_"), {nm: "About %s.\n" % _ORG})
            ck(name + " (%s)" % nm, rcx == 2 and os.path.basename(nm) in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        name = "the word check is skipped only for corpus data files"
        refused(name, {"kit/corpus/data/q.jsonl": "a line about %s and %s\n" % (_ORG, pid)}, "q.jsonl")
        # a name with internal outside the internal form
        name = "a name with internal outside the internal form stops the export"
        for nm in ("kit/notes_internal.md", "kit/internal/x.md", "kit/Internal.md", "kit/a-internal", "kit/notes.internal",
                   "kit/internal2.md", "kit/internal notes.md", "kit/notes(internal).md", "kit/notesInternal.md", "kit/INTERNAL-x.md"):
            rcx, text, o = run("int-" + nm.replace("/", "_"), {nm: "x\n"})
            ck(name + " (%s)" % nm, rcx == 2 and "internal" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        rcx, text, o = run("int-ok", {"kit/internals.md": "x\n", "kit/international.md": "x\n", "kit/Internals.md": "x\n", "kit/notesInternals.md": "x\n"})
        ck(name + " (a longer word passes)", rcx == 0, text)
        # only files that start with a shebang are made executable (the calls are recorded: Windows has no such bit)
        name = "only files starting with a shebang are made executable"
        real_chmod, calls = os.chmod, []

        def rec_chmod(path, mode, *a, **k):
            # the output is written to a sibling directory first: the path below it is what counts
            calls.append(os.path.relpath(path, os.path.dirname(made[0])).replace(os.sep, "/").split("/", 1)[1])
            return real_chmod(path, mode, *a, **k)
        made = [""]
        counter[0] += 1
        made[0] = os.path.join(tmp, "out%d" % counter[0])
        sb = build("shebang", {"kit/tool.sh": "#!/bin/sh\necho ok\n", "kit/attr.rs": "#![allow(dead_code)]\nfn f() {}\n",
                               "kit/bang.txt": "#! not a shebang\n", "kit/plain.sh": "echo ok\n", "kit/spaced.sh": "#! /bin/sh\necho ok\n"})
        os.chmod = rec_chmod
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rcx = export_main(["--out", made[0], "--allow-missing-license"] + SA, sb)
        finally:
            os.chmod = real_chmod
        ck(name, rcx == 0 and "kit/tool.sh" in calls and "kit/spaced.sh" in calls and not any(c in calls for c in ("kit/attr.rs", "kit/bang.txt", "kit/plain.sh")),
           "exit %d %s" % (rcx, calls))
        if os.name != "nt" and rcx == 0:
            modes = dict((r, os.stat(os.path.join(made[0], *r.split("/"))).st_mode & 0o111) for r in ("kit/tool.sh", "kit/spaced.sh", "kit/attr.rs", "kit/plain.sh"))
            ck(name + " (the mode bits)", modes["kit/tool.sh"] and modes["kit/spaced.sh"] and not modes["kit/attr.rs"] and not modes["kit/plain.sh"], str(modes))
        # the checker of the writing rules runs on the output
        name = "a style violation in the output stops the export"
        rcx, text, o = run("style-bad", argv=["--style-check", style_bad])
        ck(name, rcx == 1 and "x.md:3: [forbidden:gse]" in text and "y.md:9: [japanese-prose]" in text and "2 violations" in text and not os.path.exists(o),
           "exit %d %s" % (rcx, text.strip()[-300:]))
        ck(name + " (the detail is not shown)", "SECRETDETAIL" not in text)
        if os.path.isfile(REAL_STYLE):
            rcx, text, o = run("style-real", argv=["--style-check", REAL_STYLE])
            ck(name + " (the real checker passes a clean output)", rcx == 0, "exit %d %s" % (rcx, text.strip()[-300:]))
            rcx, text, o = run("style-real-bad", {"README.md": "# Fake\nThis was settled in decision 72.\n"}, argv=["--style-check", REAL_STYLE])
            ck(name + " (the real checker stops an internal number)", rcx == 1 and "README.md:2: [forbidden:internal-ref]" in text and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-300:]))
        else:
            print("note: the real style checker is not at %s; its cases are skipped" % REAL_STYLE)
        # a checker that is missing or fails
        name = "a missing or failing style checker stops the export"
        rcx, text, o = run("style-none", argv=["--style-check", os.path.join(tmp, "no-such-checker.py")])
        ck(name + " (the given file is missing)", rcx == 2 and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        counter[0] += 1
        o = os.path.join(tmp, "out%d" % counter[0])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rcx = export_main(["--out", o, "--allow-missing-license"], build("style-flagless"))
        ck(name + " (no git work tree and no --style-check)", rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
        if have_git:
            counter[0] += 1
            o = os.path.join(tmp, "out%d" % counter[0])
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rcx = export_main(["--out", o, "--allow-missing-license"], gb)
            ck(name + " (the default place has no checker)", rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
            default_tool = os.path.join(gtop, *STYLE_REL.split("/"))
            os.makedirs(os.path.dirname(default_tool))
            shutil.copy(style_ok, default_tool)
            rel_tool = os.path.relpath(default_tool, gtop).replace(os.sep, "/")

            def export_default():
                counter[0] += 1
                od = os.path.join(tmp, "out%d" % counter[0])
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    rcd = export_main(["--out", od, "--allow-missing-license"], gb)
                return rcd, od
            # a style checker that is not committed stops the export
            name2 = "a style checker that is not committed stops the export"
            rcx, o = export_default()
            ck(name2 + " (untracked, at the default place)", rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
            ck(name2 + " (a loose file outside git, given)", export_at(gb, ["--style-check", loose_tool])[0] == 2)
            git_here(gtop, "add", rel_tool)
            rcx, o = export_default()
            ck(name2 + " (staged only)", rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
            ok = git_here(gtop, "commit", "-q", "-m", "checker").returncode == 0
            ck(name2 + " (the checker is committed)", ok)
            rcx, o = export_default()
            ck(name + " (the checker at the default place in the work tree is used)", rcx == 0 and os.path.isdir(o), "exit %d" % rcx)
            with open(default_tool, "ab") as f:
                f.write(b"# edited\n")
            rcx, o = export_default()
            ck(name2 + " (modified)", rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
            git_here(gtop, "update-index", "--assume-unchanged", rel_tool)
            rcx, o = export_default()
            ck(name2 + " (flagged as unchanged)", rcx == 2 and not os.path.exists(o), "exit %d" % rcx)
            git_here(gtop, "update-index", "--no-assume-unchanged", rel_tool)
            git_here(gtop, "checkout", "-q", "--", rel_tool)
            rcx, o = export_default()
            ck(name2 + " (restored)", rcx == 0, "exit %d" % rcx)
        real_timeout = STYLE_TIMEOUT
        try:
            globals()["STYLE_TIMEOUT"] = 2
            for label, tool in (("exit 2", style_exit2), ("exit 3", style_exit3), ("a crash", style_crash), ("a timeout", style_hang)):
                rcx, text, o = run("style-fail-" + label.replace(" ", ""), argv=["--style-check", tool])
                ck(name + " (%s)" % label, rcx == 2 and not os.path.exists(o), "exit %d %s" % (rcx, text.strip()[-200:]))
        finally:
            globals()["STYLE_TIMEOUT"] = real_timeout
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
