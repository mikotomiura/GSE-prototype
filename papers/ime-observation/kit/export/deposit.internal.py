#!/usr/bin/env python3
# kit: selftest
"""Checks the files of the dataset deposit and uploads them to the reserved draft (Python standard library only).

  deposit.internal.py --from DIR [--allow-pending] [--export DIR]            check (no network)
  deposit.internal.py --from DIR [--export DIR] --remote [--token-file PATH] check, then read the draft
  deposit.internal.py --from DIR [--export DIR] --upload [--token-file PATH] check, then upload to the draft
  deposit.internal.py --table                                                print the rows of the datasheet table
  deposit.internal.py --selftest

This tool is internal: it is never exported (its name has the internal form). Run it with python -I. The list of the
files of the deposit is kit/export/deposit.internal.json. Each file has its name in the deposit, its part and what it
holds, and either the SHA-256 of an archive or a sample with a label that ties it to its record (found under the
directory given with --from by that SHA-256, whatever its local name) or the path of a file of this directory (taken
from the committed version, HEAD; a path that is untracked, is not one file, differs from HEAD or carries an
assume-unchanged or skip-worktree mark is refused). A SHA-256 of null marks a file not packed or recorded yet
(pending). The check

  1. refuses a list whose names are not unique or not flat ([A-Za-z0-9._-]), or whose SHA-256 repeat;
  2. reads the table "Deposits" of each record (experiment/data.md, experiment/data.windows.md) and refuses a row that
     is not four cells with a SHA-256 in backticks in the third, and a SHA-256 of that section outside that column.
     Every archive (*.zip) of the list must have its row in its own record, and the first cell of that row must be
     its label, alone or followed by " (" (when the row says "(attempt N", the name must end in "-N.zip"); every
     row must belong to an archive of the list whose record is that file, so that an archive packed and recorded on
     a measuring machine cannot be left out or taken for another. Every other file with a SHA-256 must have a line
     in its record that holds its SHA-256 as the only SHA-256 of the line, with its label as a word, and with the
     word "conditions" exactly when its name holds that word (so that a sample is not taken for the file of its
     conditions, nor one condition for the other);
  3. requires every SHA-256 in the table "Files of the deposit" of the datasheet to be that of the file its row
     names, and every name there to be a file of the list;
  4. finds every file of the list under --from (links and junctions are not followed; .DS_Store, ._*, Thumbs.db and
     desktop.ini are ignored); a pending file fails the check unless --allow-pending is given, and a file under
     --from that the list does not name is reported;
  5. with --export DIR (a fresh export of the same commit), requires every file taken from this directory to be
     byte-identical to the file of the export at the same path.

--remote then reads the draft (GET only, also when files are missing here): it must be the draft that reserved the DOI
of the list and be unsubmitted, and every file already in it must be a file of the list, with the same MD5 and size
when the file is here. --upload requires the final state as well: nothing pending, no file under --from that the list
does not name, the list, the records and the datasheet equal to HEAD, every file of the list (but the datasheet
itself) named in the datasheet table with its part, contents and SHA-256, and no "(to be filled in at deposit)" left
in the datasheet. It then sends each file that the draft does not hold yet to the bucket of the draft, the smallest
first: a file under --from is hashed again through the handle it is sent from, sent up to its checked size only, and
the MD5 of the bytes sent and the MD5 and size that the service returns are compared with the check. A file of the
same name with other content, or a file of the draft that the list does not name, stops it before anything is sent
(remove such a file in the web form). The tool never publishes: it has no call that submits or publishes a record.
The token is read from --token-file (default C:/zenodo/zenodo_token.txt on Windows; required elsewhere) inside the
process, sent only to the API host and never printed; a token file inside the git work tree is refused. The commit
of the source is printed, so that what was sent can be tied to it.

Exit status: 0 the check passed (and the upload completed), 1 the check failed, 2 a usage or environment error.
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent
LIST_FILE = "kit/export/deposit.internal.json"
RECORDS = ("experiment/data.md", "experiment/data.windows.md")
API = "https://zenodo.org/api"
TOKEN_FILE = "C:/zenodo/zenodo_token.txt" if os.name == "nt" else None
PARTS = ("Measurement", "Calibration pilot", "Shared")
KEYS = {"name", "part", "contents", "sha256", "label", "record", "repo", "datasheet"}
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
SHA_RE = re.compile(r"[0-9a-f]{64}")
HEX_ANY = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{64}(?![0-9A-Fa-f])")
CELL_SHA = re.compile(r"`([0-9a-f]{64})`")
CELL_NAME = re.compile(r"`([^`]+)`")
SEPARATOR_CELL = re.compile(r":?-{3,}:?")
PENDING_MARK = "(to be filled in at deposit)"
TABLE_LEAD = "**Files of the deposit.**"
SELF_SHA_CELL = "not given (this file)"
SYSTEM_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
CHUNK = 1 << 20
_OPENER = urllib.request.build_opener()


class Usage(Exception):
    """A usage or environment error (exit status 2)."""


class Item:
    """One file of the list, resolved: its digests and where its bytes come from."""

    def __init__(self, entry: dict):
        self.entry = entry
        self.name: str = entry["name"]
        self.sha256: str | None = entry.get("sha256")
        self.md5: str | None = None
        self.size: int | None = None
        self.path: Path | None = None
        self.blob: bytes | None = None


# ---------------------------------------------------------------- git and files

def _git(source: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(source), "--literal-pathspecs", *args], capture_output=True)
    except OSError as e:
        raise Usage(f"cannot run git: {e.__class__.__name__}") from None


def committed(source: Path, rel: str) -> tuple[bytes | None, str | None]:
    """The committed bytes of one file of the source directory, or the reason why they cannot be used."""
    r = _git(source, "ls-files", "-v", "--", rel)
    if r.returncode != 0:
        raise Usage(f"git ls-files failed in {source}")
    tags = r.stdout.decode("utf-8", "replace").splitlines()
    if len(tags) != 1 or tags[0][2:] != rel:
        return None, "is not one file tracked by git"
    if not tags[0].startswith("H "):
        return None, "carries an assume-unchanged or skip-worktree mark"
    if _git(source, "diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        return None, "differs from the committed version (HEAD)"
    r = _git(source, "cat-file", "blob", f"HEAD:./{rel}")
    if r.returncode != 0:
        return None, "cannot be read from HEAD"
    return r.stdout, None


def read_text(source: Path, rel: str, require_committed: bool) -> tuple[str | None, str | None]:
    """The text of a file of the source directory (the committed one when required), or the reason."""
    if require_committed:
        raw, why = committed(source, rel)
        if raw is None:
            return None, why
    else:
        try:
            raw = (source / rel).read_bytes()
        except OSError:
            return None, "cannot be read"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "is not UTF-8"


def _md5(data: bytes = b""):
    try:
        return hashlib.md5(data, usedforsecurity=False)
    except TypeError:  # Python before 3.9
        return hashlib.md5(data)


def digests(f) -> tuple[str, str, int]:
    """SHA-256, MD5 and size of what an open binary file holds from where it stands."""
    sha, md5, size = hashlib.sha256(), _md5(), 0
    while True:
        block = f.read(CHUNK)
        if not block:
            break
        sha.update(block)
        md5.update(block)
        size += len(block)
    return sha.hexdigest(), md5.hexdigest(), size


def _plain(entry: os.DirEntry) -> bool:
    """Neither a symbolic link nor a junction (or other reparse point)."""
    if entry.is_symlink():
        return False
    return not getattr(entry.stat(follow_symlinks=False), "st_file_attributes", 0) & REPARSE


def staged_files(root: Path) -> tuple[list[Path], list[str]]:
    """The regular files under root, without following links or junctions, and what was passed over."""
    files, passed = [], []
    stack = [root]
    while stack:
        with os.scandir(stack.pop()) as it:
            entries = sorted(it, key=lambda e: e.name)
        for e in entries:
            path = Path(e.path)
            rel = path.relative_to(root).as_posix()
            if not _plain(e):
                passed.append(f"{rel} (a link or junction; not followed)")
            elif e.is_dir(follow_symlinks=False):
                stack.append(path)
            elif e.name in SYSTEM_FILES or e.name.startswith("._"):
                passed.append(f"{rel} (a file of the system; ignored)")
            elif e.is_file(follow_symlinks=False):
                files.append(path)
    return sorted(files), passed


def _relative(rel: object) -> bool:
    if not isinstance(rel, str) or not rel or "\\" in rel or ":" in rel:
        return False
    p = PurePosixPath(rel)
    return not p.is_absolute() and ".." not in p.parts and "." not in p.parts and p.as_posix() == rel


# ---------------------------------------------------------------- the list, the records and the datasheet

def load_list(text: str) -> tuple[dict, list[str]]:
    """The list and its problems of form (names, parts, keys, SHA-256, labels)."""
    try:
        data = json.loads(text)
    except ValueError as e:
        return {}, [f"the list is not valid JSON ({e})"]
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        return {}, ["the list must be an object with a list 'files'"]
    problems = []
    dep, doi = data.get("deposition"), data.get("doi")
    if not isinstance(dep, int) or isinstance(dep, bool) or dep <= 0:
        problems.append("'deposition' must be a positive integer")
    elif doi != f"10.5281/zenodo.{dep}":
        problems.append("'doi' must be the DOI that the draft 'deposition' reserved")
    names, shas, sheets = set(), set(), 0
    for i, e in enumerate(data["files"]):
        where = f"entry {i + 1}"
        if not isinstance(e, dict):
            problems.append(f"{where}: not an object")
            continue
        extra = set(e) - KEYS
        if extra:
            problems.append(f"{where}: unknown keys {sorted(extra)}")
        name = e.get("name")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            problems.append(f"{where}: the name must be flat and of [A-Za-z0-9._-]")
        elif name.lower() in names:
            problems.append(f"{where}: the name {name} is given twice")
        else:
            names.add(name.lower())
            where = name
        if e.get("part") not in PARTS:
            problems.append(f"{where}: the part must be one of {list(PARTS)}")
        if not isinstance(e.get("contents"), str) or not e["contents"].strip() or "|" in e["contents"]:
            problems.append(f"{where}: 'contents' is empty or holds '|'")
        if ("repo" in e) == ("sha256" in e):
            problems.append(f"{where}: exactly one of 'repo' and 'sha256' must be given")
            continue
        if "repo" in e:
            if not _relative(e["repo"]):
                problems.append(f"{where}: 'repo' must be a relative path of this directory")
            if "record" in e or "label" in e:
                problems.append(f"{where}: a file of this directory has no 'record' and no 'label'")
        else:
            sha = e["sha256"]
            if sha is not None and (not isinstance(sha, str) or not SHA_RE.fullmatch(sha)):
                problems.append(f"{where}: 'sha256' must be 64 lower-case hex digits or null")
            elif sha is not None and sha in shas:
                problems.append(f"{where}: the SHA-256 is given to another file too")
            elif sha is not None:
                shas.add(sha)
            if e.get("record") not in RECORDS:
                problems.append(f"{where}: 'record' must be one of {list(RECORDS)}")
            label = e.get("label")
            if not isinstance(label, str) or not label.strip() or "|" in label or "`" in label:
                problems.append(f"{where}: 'label' is missing or holds '|' or a backtick")
        if "datasheet" in e:
            if e["datasheet"] is not True or "repo" not in e:
                problems.append(f"{where}: 'datasheet' marks the datasheet, a file of this directory")
            else:
                sheets += 1
    if sheets != 1:
        problems.append("exactly one file of the list must be marked as the datasheet")
    return data, problems


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def deposits_table(text: str, rel: str) -> tuple[list[tuple[str, str]] | None, list[str]]:
    """The rows (first cell, SHA-256) of the table under the heading 'Deposits', and the problems of its form.

    None instead of the rows when the record has no such heading."""
    section, inside, seen = [], False, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Deposits"
            seen = seen or inside
            continue
        if inside:
            section.append(line)
    if not seen:
        return None, []
    table = [line for line in section if line.startswith("|")]
    if len(table) < 2 or not all(SEPARATOR_CELL.fullmatch(c) for c in _cells(table[1])):
        return [], [f"{rel}: the section 'Deposits' has no table"]
    rows, problems = [], []
    for line in table[2:]:
        cells = _cells(line)
        m = CELL_SHA.fullmatch(cells[2]) if len(cells) == 4 else None
        if m is None:
            problems.append(f"{rel}: a row of 'Deposits' is not four cells with a lower-case SHA-256 in backticks "
                            f"in the third: {line.strip()[:70]}")
            continue
        rows.append((cells[0], m.group(1)))
    found = {h for line in section for h in HEX_ANY.findall(line)}
    if found - {sha for _, sha in rows}:
        problems.append(f"{rel}: the section 'Deposits' holds a SHA-256 outside the third column of its rows")
    return rows, problems


def check_archive_row(it: Item, cell: str) -> str | None:
    label = it.entry["label"]
    if cell != label and not cell.startswith(label + " ("):
        return f"{it.name}: its row in 'Deposits' is labelled '{cell[:40]}', not '{label}'"
    m = re.match(re.escape(label) + r" \(attempt (\d+)\b", cell)
    if m and not it.name.endswith(f"-{m.group(1)}.zip"):
        return f"{it.name}: its row in 'Deposits' is attempt {m.group(1)}"
    return None


def check_sample_line(it: Item, text: str, rel: str) -> str | None:
    label, conditions = it.entry["label"], "conditions" in it.name
    word = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(label) + r"(?![A-Za-z0-9_-])")
    for line in text.splitlines():
        if it.sha256 in line and HEX_ANY.findall(line) == [it.sha256] and word.search(line) \
                and ("conditions" in line) == conditions:
            return None
    return (f"{it.name}: no line of {rel} holds its SHA-256 as the only SHA-256 of the line, with the word "
            f"'{label}' and {'with' if conditions else 'without'} the word 'conditions'")


def table_rows(text: str) -> list[list[str]] | None:
    """The body rows of the table 'Files of the deposit' of the datasheet, or None if it cannot be found."""
    lines = text.splitlines()
    start = next((k for k, line in enumerate(lines) if line.startswith(TABLE_LEAD)), None)
    if start is None:
        return None
    k = start + 1
    while k < len(lines) and not lines[k].startswith("|"):
        k += 1
    rows = []
    while k < len(lines) and lines[k].startswith("|"):
        rows.append(_cells(lines[k]))
        k += 1
    if len(rows) < 2 or rows[0] != ["File", "Part", "Contents", "SHA-256"]:
        return None
    return rows[2:]


def check_datasheet(text: str, items: list[Item], final: bool) -> list[str]:
    rows = table_rows(text)
    if rows is None:
        return ["the datasheet has no table 'Files of the deposit' with the columns File, Part, Contents, SHA-256"]
    problems = []
    by_name = {it.name: it for it in items}
    by_sha = {it.sha256: it.name for it in items if it.sha256}
    given: dict[str, list[str]] = {}
    for cells in rows:
        if len(cells) != 4:
            problems.append(f"a row of the datasheet table has {len(cells)} cells: {' | '.join(cells)[:80]}")
            continue
        m = CELL_NAME.fullmatch(cells[0])
        name = m.group(1) if m else None
        if name is None and cells[0] != PENDING_MARK:
            problems.append(f"a file cell of the datasheet table is neither a name in backticks nor the mark: "
                            f"{cells[0][:60]}")
        m = CELL_SHA.fullmatch(cells[3])
        sha = m.group(1) if m else None
        if name is not None:
            if name not in by_name:
                problems.append(f"the datasheet table names {name}, which is not a file of the list")
            if name in given:
                problems.append(f"the datasheet table names {name} twice")
            given[name] = cells
        if sha is not None:
            if sha not in by_sha:
                problems.append(f"the datasheet table gives the SHA-256 {sha[:12]}..., which belongs to no file of "
                                f"the list")
            elif name is not None and by_sha[sha] != name:
                problems.append(f"the datasheet table gives {name} the SHA-256 of {by_sha[sha]}")
    if final:
        if PENDING_MARK in text:
            problems.append(f"the datasheet still holds '{PENDING_MARK}'")
        for it in items:
            cells = given.get(it.name)
            if cells is None:
                problems.append(f"the datasheet table does not name {it.name}")
                continue
            if cells[1] != it.entry["part"] or cells[2] != it.entry["contents"]:
                problems.append(f"the datasheet table gives {it.name} another part or contents than the list")
            if it.entry.get("datasheet"):
                if CELL_SHA.fullmatch(cells[3]):
                    problems.append("the datasheet table cannot give the SHA-256 of the datasheet itself")
            elif it.sha256 is None or cells[3] != f"`{it.sha256}`":
                problems.append(f"the datasheet table does not give {it.name} with its SHA-256")
    return problems


# ---------------------------------------------------------------- the check

def run_check(source: Path, staging: Path | None, *, allow_pending: bool, final: bool,
              export: Path | None, out) -> tuple[list[str], list[Item], dict]:
    """Checks the list against the records, the datasheet, the committed files and the files under --from."""
    head = _git(source, "rev-parse", "HEAD")
    print(f"  source   commit {head.stdout.decode('ascii', 'replace').strip() if head.returncode == 0 else '?'}",
          file=out)
    text, why = read_text(source, LIST_FILE, final)
    if text is None:
        return [f"{LIST_FILE} {why}"], [], {}
    data, problems = load_list(text)
    if problems:
        return problems, [], data
    items = [Item(e) for e in data["files"]]
    by_sha = {it.sha256: it for it in items if it.sha256}

    # 2. the records
    for rel in RECORDS:
        rtext, why = read_text(source, rel, final)
        if rtext is None:
            problems.append(f"{rel} {why}")
            continue
        rows, form = deposits_table(rtext, rel)
        if rows is None:
            problems.append(f"{rel} has no section 'Deposits'")
            continue
        problems += form
        cell_of = {sha: cell for cell, sha in rows}
        for it in items:
            if it.sha256 is None or it.entry.get("record") != rel:
                continue
            if it.name.endswith(".zip"):
                why = (check_archive_row(it, cell_of[it.sha256]) if it.sha256 in cell_of else
                       f"{it.name}: its SHA-256 is not in the table 'Deposits' of {rel}")
            else:
                why = check_sample_line(it, rtext, rel)
            if why:
                problems.append(why)
        for cell, sha in rows:
            owner = by_sha.get(sha)
            if owner is None:
                problems.append(f"{rel} records the archive {sha[:12]}... in 'Deposits', but the list has no file "
                                f"with it")
            elif not owner.name.endswith(".zip") or owner.entry.get("record") != rel:
                problems.append(f"{rel} records in 'Deposits' the SHA-256 of {owner.name}, which is not an archive "
                                f"recorded there")

    # 1/5. the files of this directory
    for it in items:
        rel = it.entry.get("repo")
        if rel is None:
            continue
        blob, why = committed(source, rel)
        if blob is None:
            problems.append(f"{it.name}: {rel} {why}")
            continue
        it.blob, it.size = blob, len(blob)
        it.sha256 = hashlib.sha256(blob).hexdigest()
        it.md5 = _md5(blob).hexdigest()
        if export is not None:
            try:
                same = (export / rel).read_bytes() == blob
            except OSError:
                same = False
            if not same:
                problems.append(f"{it.name}: {rel} of the export differs from the committed file or is missing")
        print(f"  ok       {it.name}  (committed {rel}, {it.size} bytes)", file=out)

    # 3. the datasheet
    sheet = next(it for it in items if it.entry.get("datasheet"))
    if sheet.blob is not None:
        try:
            problems += check_datasheet(sheet.blob.decode("utf-8"), items, final)
        except UnicodeDecodeError:
            problems.append(f"{sheet.name} is not UTF-8")

    # 4. the files under --from
    from_repo = {it.sha256: it.name for it in items if it.blob is not None}
    unlisted: list[tuple[Path, str]] = []
    if staging is not None:
        if not staging.is_dir():
            raise Usage(f"--from is not a directory: {staging}")
        files, passed = staged_files(staging)
        for note in passed:
            print(f"  passed   {note}", file=out)
        for path in files:
            with open(path, "rb") as f:
                sha, md5, size = digests(f)
            owner = by_sha.get(sha)
            if owner is not None and owner.path is None:
                owner.path, owner.md5, owner.size = path, md5, size
            elif owner is None:
                unlisted.append((path, sha))
    for it in items:
        if "repo" in it.entry:
            continue
        if it.sha256 is None:
            print(f"  pending  {it.name}", file=out)
            if final or not allow_pending:
                problems.append(f"{it.name}: pending (not packed or recorded yet)")
        elif it.path is None:
            print(f"  MISSING  {it.name}", file=out)
            problems.append(f"{it.name}: no file under --from has its SHA-256")
        else:
            print(f"  ok       {it.name}  ({it.path.relative_to(staging).as_posix()}, {it.size} bytes)", file=out)
    for path, sha in unlisted:
        rel = path.relative_to(staging).as_posix()
        if sha in from_repo:
            print(f"  copy     {rel} (the same bytes as {from_repo[sha]}, which is sent from the repository)", file=out)
            continue
        print(f"  unlisted {rel} (the list names no file with its SHA-256)", file=out)
        if final:
            problems.append(f"{rel} under --from is not a file of the list")
    return problems, items, data


# ---------------------------------------------------------------- the draft

class _Capped:
    """Reads at most size bytes of a binary file and keeps the MD5 of what was read."""

    def __init__(self, f, size: int):
        self.f, self.left, self.md5 = f, size, _md5()

    def read(self, n: int = -1) -> bytes:
        if self.left <= 0:
            return b""
        block = self.f.read(self.left if n is None or n < 0 else min(n, self.left))
        self.left -= len(block)
        self.md5.update(block)
        return block


def api_call(method: str, url: str, token: str, api: str, body=None, length: int | None = None):
    """One request to the API host; the token goes in a header that is not passed on to a redirect."""
    if not url.startswith(api + "/"):
        raise Usage("refusing to send the token to a host other than the API")
    req = urllib.request.Request(url, data=body, method=method)
    req.add_unredirected_header("Authorization", "Bearer " + token)
    if body is not None:
        req.add_unredirected_header("Content-Type", "application/octet-stream")
        if length is not None:
            req.add_unredirected_header("Content-Length", str(length))
    try:
        with _OPENER.open(req, timeout=900) as r:
            status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        reason = getattr(e, "reason", e)
        return 0, f"network error ({type(reason).__name__}: {str(reason)[:160]})"
    try:
        return status, (json.loads(raw.decode("utf-8")) if raw else None)
    except (ValueError, UnicodeDecodeError):
        return status, raw[:300].decode("utf-8", "replace")


def read_draft(data: dict, token: str, api: str) -> tuple[str | None, dict, list[str]]:
    """The bucket of the draft, its files {name: (md5, size)} and the problems of its state."""
    dep = data["deposition"]
    status, js = api_call("GET", f"{api}/deposit/depositions/{dep}", token, api)
    if status != 200 or not isinstance(js, dict):
        detail = f": {js}" if status == 0 else ""
        return None, {}, [f"cannot read the draft {dep} (HTTP {status}){detail}"]
    problems = []
    if js.get("id") != dep:
        problems.append(f"the service answered for another record than {dep}")
    md = js.get("metadata") if isinstance(js.get("metadata"), dict) else {}
    pre = md.get("prereserve_doi") if isinstance(md.get("prereserve_doi"), dict) else {}
    if pre.get("doi") != data["doi"]:
        problems.append(f"the draft did not reserve the DOI {data['doi']}")
    if js.get("submitted") is not False or js.get("state") != "unsubmitted":
        problems.append("the record is not an unsubmitted draft (it may have been published)")
    links = js.get("links") if isinstance(js.get("links"), dict) else {}
    bucket = links.get("bucket")
    if not isinstance(bucket, str) or not bucket.startswith(api + "/files/"):
        problems.append("the bucket of the draft is not on the API host")
        bucket = None
    remote = {}
    for f in js.get("files") or []:
        if isinstance(f, dict) and isinstance(f.get("filename"), str):
            md5 = str(f.get("checksum", ""))
            remote[f["filename"]] = (md5[4:] if md5.startswith("md5:") else md5, f.get("filesize"))
    return bucket, remote, problems


def compare_draft(items: list[Item], remote: dict, out) -> list[str]:
    problems = []
    names = {it.name for it in items}
    for name in sorted(remote):
        if name not in names:
            problems.append(f"the draft holds {name}, which is not a file of the list (remove it in the web form)")
    for it in items:
        held = remote.get(it.name)
        if held is None:
            print(f"  to send  {it.name}" + ("" if it.md5 else " (missing here)"), file=out)
        elif it.md5 is None:
            print(f"  in draft {it.name} (not compared: missing here)", file=out)
        elif held == (it.md5, it.size):
            print(f"  in draft {it.name}", file=out)
        else:
            problems.append(f"the draft holds {it.name} with other content or size (remove it in the web form first)")
    return problems


def _unchanged(f, it: Item) -> bool:
    """Whether the open file still has the size and SHA-256 of the check."""
    sha, _, size = digests(f)
    return sha == it.sha256 and size == it.size


def upload(items: list[Item], data: dict, token: str, api: str, out) -> list[str]:
    bucket, remote, problems = read_draft(data, token, api)
    if not problems:
        problems = compare_draft(items, remote, out)
    if problems or bucket is None:
        return problems or ["the draft has no bucket"]
    for it in sorted(items, key=lambda i: (i.size, i.name)):
        if it.name in remote:
            continue
        url = bucket + "/" + urllib.parse.quote(it.name)
        if it.blob is not None:
            status, js = api_call("PUT", url, token, api, body=it.blob)
            sent = it.md5
        else:
            with open(it.path, "rb") as f:
                if not _unchanged(f, it):
                    return [f"{it.name} changed under --from since the check; it was not sent, nor anything after it "
                            f"(the files sent before it are in the draft)"]
                f.seek(0)
                body = _Capped(f, it.size)
                status, js = api_call("PUT", url, token, api, body=body, length=it.size)
                sent = body.md5.hexdigest() if body.left == 0 else None
        if status not in (200, 201) or not isinstance(js, dict):
            return [f"sending {it.name} failed (HTTP {status}); nothing after it was sent (look at the draft in the "
                    f"web form)"]
        if sent != it.md5 or js.get("key") != it.name or js.get("checksum") != "md5:" + it.md5 \
                or js.get("size") != it.size:
            return [f"the draft now holds {it.name} with another MD5 or size than the check; remove it in the web "
                    f"form (nothing after it was sent)"]
        print(f"  sent     {it.name}  ({it.size} bytes)", file=out)
    _, remote, problems = read_draft(data, token, api)
    if not problems:
        if set(remote) != {it.name for it in items}:
            problems.append("after the upload the draft does not hold exactly the files of the list")
        for it in items:
            if remote.get(it.name) != (it.md5, it.size):
                problems.append(f"after the upload the draft holds {it.name} with another MD5 or size")
    return problems


def read_token(path: Path, source: Path) -> str:
    try:
        real = path.resolve(strict=True)
    except OSError:
        raise Usage(f"cannot find the token file {path}") from None
    top = _git(source, "rev-parse", "--show-toplevel")
    if top.returncode == 0:
        root = Path(top.stdout.decode("utf-8", "replace").strip())
        for p in (real, *real.parents):
            try:
                inside = os.path.samefile(p, root)
            except OSError:
                continue
            if inside:
                raise Usage("the token file lies inside the git work tree; keep it outside")
    try:
        token = real.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        raise Usage("cannot read the token file") from None
    if not token or any(not 33 <= ord(ch) <= 126 for ch in token):
        raise Usage("the token file does not hold one token")
    return token


# ---------------------------------------------------------------- the table of the datasheet

def print_table(source: Path, out) -> int:
    text, why = read_text(source, LIST_FILE, False)
    if text is None:
        raise Usage(f"{LIST_FILE} {why}")
    data, problems = load_list(text)
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=out)
        return 1
    status = 0
    for e in data["files"]:
        if e.get("datasheet"):
            sha = SELF_SHA_CELL
        elif "repo" in e:
            blob, why = committed(source, e["repo"])
            if blob is None:
                print(f"FAIL: {e['name']}: {e['repo']} {why}", file=sys.stderr)
                status = 1
                continue
            sha = f"`{hashlib.sha256(blob).hexdigest()}`"
        else:
            sha = f"`{e['sha256']}`" if e["sha256"] else PENDING_MARK
        print(f"| `{e['name']}` | {e['part']} | {e['contents']} | {sha} |", file=out)
    return status


# ---------------------------------------------------------------- command line

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check and upload the files of the dataset deposit (internal).")
    ap.add_argument("--from", dest="staging", help="directory that holds the archives and samples")
    ap.add_argument("--allow-pending", action="store_true", help="do not fail on files not packed yet")
    ap.add_argument("--export", help="fresh export of the same commit to compare the files of this directory with")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--remote", action="store_true", help="also read the draft (GET only)")
    mode.add_argument("--upload", action="store_true", help="upload to the draft (never publishes)")
    mode.add_argument("--table", action="store_true", help="print the rows of the datasheet table")
    mode.add_argument("--selftest", action="store_true")
    ap.add_argument("--token-file", default=TOKEN_FILE)
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest()
        if a.table:
            return print_table(SOURCE, sys.stdout)
        if not a.staging:
            raise Usage("--from DIR is required")
        if a.upload and a.allow_pending:
            raise Usage("--upload cannot be combined with --allow-pending")
        staging = Path(a.staging)
        export = Path(a.export) if a.export else None
        if export is not None and not export.is_dir():
            raise Usage(f"--export is not a directory: {export}")
        token = None
        if a.remote or a.upload:
            if not a.token_file:
                raise Usage("--token-file is required on this system")
            token = read_token(Path(a.token_file), SOURCE)
        problems, items, data = run_check(SOURCE, staging, allow_pending=a.allow_pending, final=a.upload,
                                          export=export, out=sys.stdout)
        if a.remote and items:  # reading the draft changes nothing, so it is read even when files are missing
            _, remote, draft_problems = read_draft(data, token, API)
            if not draft_problems:
                draft_problems = compare_draft(items, remote, sys.stdout)
            problems += draft_problems
        elif not problems and a.upload:
            problems = upload(items, data, token, API, sys.stdout)
    except Usage as e:
        print(f"deposit: {e}", file=sys.stderr)
        return 2
    for p in problems:
        print(f"FAIL: {p}")
    if problems:
        print(f"deposit: {len(problems)} problem(s); nothing more was done")
        return 1
    print("deposit: uploaded; the draft holds exactly the files of the list" if a.upload else "deposit: check passed")
    return 0


# ---------------------------------------------------------------- selftest

def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class _Mock:
    """A stand-in for the deposit API: one draft and its bucket, on the loopback interface."""

    def __init__(self, token: str):
        self.token, self.requests, self.files, self.order = token, [], {}, []
        self.state, self.submitted, self.doi, self.dep = "unsubmitted", False, "10.5281/zenodo.7", 7
        self.bucket_base: str | None = None
        self.corrupt = self.drop = False
        mock = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, status: int, obj) -> None:
                raw = json.dumps(obj).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                mock.requests.append(("GET", self.path, self.headers.get("Authorization")))
                if self.headers.get("Authorization") != "Bearer " + mock.token:
                    return self._send(403, {"message": "denied"})
                if self.path != f"/api/deposit/depositions/{mock.dep}":
                    return self._send(404, {"message": "no such record"})
                files = [{"filename": n, "checksum": m, "filesize": s} for n, (m, s) in sorted(mock.files.items())]
                self._send(200, {"id": mock.dep, "state": mock.state, "submitted": mock.submitted,
                                 "metadata": {"prereserve_doi": {"doi": mock.doi}},
                                 "links": {"bucket": mock.bucket_base or f"{mock.base}/files/b1"},
                                 "files": files})

            def do_PUT(self):
                mock.requests.append(("PUT", self.path, self.headers.get("Authorization")))
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                if self.headers.get("Authorization") != "Bearer " + mock.token:
                    return self._send(403, {"message": "denied"})
                if not self.path.startswith("/api/files/b1/"):
                    return self._send(404, {"message": "no such bucket"})
                name = urllib.parse.unquote(self.path[len("/api/files/b1/"):])
                md5 = _md5(body).hexdigest()
                mock.order.append((name, len(body)))
                if not mock.drop:
                    mock.files[name] = (md5, len(body))
                self._send(201, {"key": name, "size": len(body),
                                 "checksum": "md5:" + ("0" * 32 if mock.corrupt else md5)})

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}/api"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def _link_dir(target: Path, link: Path) -> bool:
    """Makes a directory link (a junction on Windows); False where this system cannot."""
    try:
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
        else:
            os.symlink(target, link, target_is_directory=True)
        return True
    except (ImportError, AttributeError, OSError):
        return False


def selftest() -> int:
    global _OPENER
    fails: list[str] = []

    def expect(ok: bool, label: str) -> None:
        if not ok:
            fails.append(label)

    a_zip, b_zip, w_zip = b"archive-a" * 50, b"archive-b" * 30, b"archive-w" * 70
    s_idle, s_work, c_idle, x_zip = b"t\tcpu\n0\t1\n", b"t\tcpu\n0\t2\n3\t4\n", b"interval 30\n", b"stray"
    shared = b"shared\n"
    sha_a, sha_b, sha_w, sha_s, sha_s2, sha_c, sha_x, sha_shared = map(
        _sha, (a_zip, b_zip, w_zip, s_idle, s_work, c_idle, x_zip, shared))
    header = "| Cell label | Deposit location | SHA-256 of the archive | Date deposited |\n|---|---|---|---|\n"
    row_a = f"| a (attempt 1; packed) | no | `{sha_a}` | no |\n"
    row_b = f"| b-pilot-1 (calibration pilot) | no | `{sha_b}` | no |\n"
    line_s, line_s2 = f"`{sha_s}` (`idle`) and\n", f"`{sha_s2}` (`working`).\n"
    line_c = f"The `conditions.txt` of `idle`: `{sha_c}`.\n"
    sheet = "experiment/datasheet.md"
    stage_default = {"x/a.zip": a_zip, "b.zip": b_zip, "w.zip": w_zip, "sub/samples.tsv": s_idle,
                     "sub/samples2.tsv": s_work, "conditions.txt": c_idle}

    def entry(name, part, contents, sha, record, label):
        return {"name": name, "part": part, "contents": contents, "sha256": sha, "record": record, "label": label}

    def base_files(final: bool) -> dict[str, str]:
        entries = [
            entry("a-1.zip", "Measurement", "run a", sha_a, RECORDS[0], "a"),
            entry("b-pilot-1.zip", "Calibration pilot", "run b", sha_b, RECORDS[0], "b-pilot-1"),
            entry("w-2.zip", "Measurement", "run w", sha_w, RECORDS[1], "w"),
            entry("s-idle.tsv", "Measurement", "samples idle", sha_s, RECORDS[0], "idle"),
            entry("s-working.tsv", "Measurement", "samples working", sha_s2, RECORDS[0], "working"),
            entry("c-idle-conditions.txt", "Measurement", "conditions idle", sha_c, RECORDS[0], "idle"),
            {"name": "shared.txt", "part": "Shared", "contents": "shared", "repo": "kit/shared.txt"},
            {"name": "datasheet.md", "part": "Shared", "contents": "this", "repo": sheet, "datasheet": True},
        ]
        if not final:
            entries.insert(3, entry("p.zip", "Calibration pilot", "run p", None, RECORDS[1], "p"))
            rows = (f"| {PENDING_MARK} | Measurement | a | `{sha_a}` |\n"
                    f"| `shared.txt` | Shared | x | `{sha_shared}` |\n")
        else:
            rows = "".join(f"| `{e['name']}` | {e['part']} | {e['contents']} | "
                           f"{SELF_SHA_CELL if e.get('datasheet') else '`' + (e.get('sha256') or sha_shared) + '`'} |\n"
                           for e in entries)
        return {
            LIST_FILE: json.dumps({"deposition": 7, "doi": "10.5281/zenodo.7", "files": entries}, indent=1),
            RECORDS[0]: f"# r\n\n## Deposits\n\n{header}{row_a}{row_b}\n## Question 5\n\nThe samples\n"
                        f"{line_s}{line_s2}{line_c}",
            RECORDS[1]: f"# w\n\n## Deposits\n\n{header}| w (attempt 2) | no | `{sha_w}` | no |\n",
            sheet: f"# Datasheet\n\n{TABLE_LEAD} The files.\n\n| File | Part | Contents | SHA-256 |\n"
                   f"|---|---|---|---|\n{rows}\nEnd.\n",
            "kit/shared.txt": shared.decode(),
        }

    def build(td: Path, tag: str, edit=None, final: bool = False, stage_files=None, after=None):
        root = td / tag
        src = root / "paper"
        files = base_files(final)
        if edit:
            edit(files)
        for rel, text in files.items():
            (src / rel).parent.mkdir(parents=True, exist_ok=True)
            (src / rel).write_bytes(text.encode("utf-8"))
        hooks = td / "no-hooks"
        hooks.mkdir(exist_ok=True)
        for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["add", "."],
                     ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false",
                      "-c", f"core.hooksPath={hooks.as_posix()}", "commit", "-q", "-m", "t"]):
            if _git(root, *args).returncode != 0:
                raise Usage(f"selftest: git {args[0]} failed")
        if after:
            after(src)
        stage = root / "stage"
        stage.mkdir()
        for rel, data in (stage_default if stage_files is None else stage_files).items():
            (stage / rel).parent.mkdir(parents=True, exist_ok=True)
            (stage / rel).write_bytes(data)
        return src, stage

    def check(td, tag, *, allow_pending=True, final=False, export=None, stage_after=None, **kw):
        src, stage = build(td, tag, final=final, **kw)
        if stage_after:
            stage_after(stage)
        buf = io.StringIO()
        problems, items, data = run_check(src, stage, allow_pending=allow_pending, final=final,
                                          export=export(src) if export else None, out=buf)
        return problems, items, data, buf.getvalue(), src

    def has(problems: list[str], word: str) -> bool:
        return any(word in p for p in problems)

    def jedit(fn):
        def edit(files):
            data = json.loads(files[LIST_FILE])
            fn(data["files"])
            files[LIST_FILE] = json.dumps(data)
        return edit

    def tedit(rel, old, new):
        def edit(files):
            if old not in files[rel]:
                raise Usage(f"selftest: the text to replace is not in {rel}")
            files[rel] = files[rel].replace(old, new)
        return edit

    def swap(i, j, key="sha256"):
        def fn(f):
            f[i][key], f[j][key] = f[j][key], f[i][key]
        return fn

    tmp = tempfile.mkdtemp(prefix="deposit-selftest-")
    saved_opener, _OPENER = _OPENER, urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        td = Path(tmp)
        p, items, _, text, _ = check(td, "base")
        expect(p == [], f"base: {p}")
        expect("pending  p.zip" in text and "unlisted" not in text and "source   commit " in text, "base: report")
        p = check(td, "pend", allow_pending=False)[0]
        expect(has(p, "p.zip: pending"), "pending without --allow-pending")

        # 1. the list
        p = check(td, "dupname", edit=jedit(lambda f: f[1].update(name="A-1.zip")))[0]
        expect(has(p, "given twice"), "duplicate name (case)")
        p = check(td, "slash", edit=jedit(lambda f: f[0].update(name="x/a-1.zip")))[0]
        expect(has(p, "must be flat"), "name with a slash")
        p = check(td, "dupsha", edit=jedit(lambda f: f[1].update(sha256=sha_a)))[0]
        expect(has(p, "given to another file"), "SHA-256 given twice")
        p = check(td, "key", edit=jedit(lambda f: f[0].update(sha="x")))[0]
        expect(has(p, "unknown keys"), "unknown key")
        p = check(td, "both", edit=jedit(lambda f: f[0].update(repo="kit/shared.txt")))[0]
        expect(has(p, "exactly one of"), "repo and sha256 together")
        p = check(td, "rec", edit=jedit(lambda f: f[0].update(record="experiment/other.md")))[0]
        expect(has(p, "'record' must be"), "record outside the two records")
        p = check(td, "nolabel", edit=jedit(lambda f: f[0].pop("label")))[0]
        expect(has(p, "'label' is missing"), "archive without a label")
        p = check(td, "pipe", edit=jedit(lambda f: f[0].update(contents="a | b")))[0]
        expect(has(p, "holds '|'"), "contents with a pipe")
        p = check(td, "nosheet", edit=jedit(lambda f: f[-1].pop("datasheet")))[0]
        expect(has(p, "marked as the datasheet"), "no datasheet")
        p = check(td, "doi", edit=lambda f: f.update({LIST_FILE: f[LIST_FILE].replace("zenodo.7", "zenodo.8")}))[0]
        expect(has(p, "'doi'"), "DOI of another draft")

        # 2. the records
        p = check(td, "notdep", edit=tedit(RECORDS[0], row_a, ""))[0]
        expect(has(p, "a-1.zip: its SHA-256 is not in the table"), "archive missing from Deposits")
        p = check(td, "swapzip", edit=jedit(swap(0, 1)))[0]
        expect(has(p, "labelled"), "two archives with each other's SHA-256")
        p = check(td, "attempt", edit=jedit(lambda f: f[0].update(name="a-2.zip")))[0]
        expect(has(p, "is attempt 1"), "archive of another attempt")
        p = check(td, "extra", edit=tedit(RECORDS[1], f"`{sha_w}` | no |\n", f"`{sha_w}` | no |\n| y | no | `{sha_x}` | no |\n"))[0]
        expect(has(p, "the list has no file with it"), "Deposits row without a file of the list")
        p = check(td, "badrow", edit=tedit(RECORDS[1], f"`{sha_w}` | no |\n",
                                           f"`{sha_w}` | no |\n| y | no | `{sha_x}` (re-packed) | no |\n"))[0]
        expect(has(p, "is not four cells"), "Deposits row with more than the SHA-256 in its third cell")
        p = check(td, "upper", edit=tedit(RECORDS[1], f"`{sha_w}` | no |\n",
                                          f"`{sha_w}` | no |\n| y | no | `{sha_x.upper()}` | no |\n"))[0]
        expect(has(p, "is not four cells"), "Deposits row with an upper-case SHA-256")
        p = check(td, "fivecells", edit=tedit(RECORDS[1], f"`{sha_w}` | no |\n",
                                              f"`{sha_w}` | no |\n| `y|z` | no | `{sha_x}` | no |\n"))[0]
        expect(has(p, "is not four cells"), "Deposits row with a pipe in its label")
        p = check(td, "outside", edit=tedit(RECORDS[1], "## Deposits\n", f"## Deposits\n\nSee {sha_x}.\n"))[0]
        expect(has(p, "outside the third column"), "SHA-256 in Deposits outside the table")
        p = check(td, "otherrec", edit=tedit(RECORDS[1], f"`{sha_w}` | no |\n", f"`{sha_w}` | no |\n{row_a}"))[0]
        expect(has(p, "which is not an archive recorded there"), "Deposits row of an archive of the other record")
        p = check(td, "tsvrow", edit=tedit(RECORDS[0], row_b, row_b + f"| s | no | `{sha_s}` | no |\n"))[0]
        expect(has(p, "which is not an archive recorded there"), "Deposits row with the SHA-256 of a sample")
        p = check(td, "nohead", edit=tedit(RECORDS[1], "## Deposits", "## Other"))[0]
        expect(has(p, "has no section 'Deposits'"), "record without Deposits")
        p = check(td, "notable", edit=tedit(RECORDS[1], header, ""))[0]
        expect(has(p, "has no table"), "Deposits without a table")
        p = check(td, "noseparator", edit=tedit(RECORDS[0], header, ""))[0]
        expect(has(p, "has no table"), "Deposits rows without a header and separator")
        p = check(td, "sample", edit=tedit(RECORDS[0], line_s, "and\n"))[0]
        expect(has(p, "s-idle.tsv: no line"), "sample not in its record")
        p = check(td, "swapsample", edit=jedit(swap(4, 5)))[0]
        expect(has(p, "s-idle.tsv: no line") and has(p, "s-working.tsv: no line"), "idle and working swapped")
        p = check(td, "swapcond", edit=jedit(swap(4, 6)))[0]
        expect(has(p, "s-idle.tsv: no line") and has(p, "c-idle-conditions.txt: no line"),
               "sample and conditions swapped")
        p = check(td, "twoline", edit=tedit(RECORDS[0], line_s + line_s2, f"`{sha_s}` (`idle`), `{sha_s2}` (`working`)\n"))[0]
        expect(has(p, "s-idle.tsv: no line"), "two SHA-256 on one line")

        # 3. the datasheet
        p = check(td, "swap", edit=tedit(sheet, f"| `shared.txt` | Shared | x | `{sha_shared}` |",
                                         f"| `shared.txt` | Shared | x | `{sha_a}` |"))[0]
        expect(has(p, "gives shared.txt the SHA-256 of a-1.zip"), "datasheet row with another file's SHA-256")
        p = check(td, "unknownsha", edit=tedit(sheet, sha_a, sha_x))[0]
        expect(has(p, "belongs to no file"), "datasheet SHA-256 of no file")
        p = check(td, "unknownname", edit=tedit(sheet, "`shared.txt`", "`other.txt`"))[0]
        expect(has(p, "names other.txt"), "datasheet names a file outside the list")
        p = check(td, "notable2", edit=tedit(sheet, TABLE_LEAD, "**Files.**"))[0]
        expect(has(p, "has no table 'Files of the deposit'"), "datasheet without the table")
        p = check(td, "header", edit=tedit(sheet, "| File | Part | Contents | SHA-256 |",
                                           "| File | Part | SHA-256 | Contents |"))[0]
        expect(has(p, "has no table 'Files of the deposit'"), "datasheet table with other columns")

        # 4. the files under --from
        p = check(td, "missing", stage_files={k: v for k, v in stage_default.items() if k != "x/a.zip"})[0]
        expect(has(p, "a-1.zip: no file under --from"), "archive missing under --from")
        p, _, _, text, _ = check(td, "stray", stage_files=dict(stage_default, **{"stray.zip": x_zip}))
        expect(p == [] and "unlisted stray.zip" in text, "unlisted file is reported in a check")
        p, _, _, text, _ = check(td, "junk", final=True, allow_pending=False, stage_files=dict(
            stage_default, **{".DS_Store": b"x", "._a.zip": b"y", "sub/Thumbs.db": b"z", "shared.txt": shared}))
        expect(p == [] and "ignored" in text and "copy     shared.txt" in text, f"system files and a copy: {p}")
        outside_dir = td / "elsewhere"
        outside_dir.mkdir()
        (outside_dir / "a.zip").write_bytes(a_zip)
        if _link_dir(outside_dir, td / "probe-link"):
            p, _, _, text, _ = check(td, "link", stage_files={k: v for k, v in stage_default.items() if k != "x/a.zip"},
                                     stage_after=lambda s: _link_dir(outside_dir, s / "linked"))
            expect(has(p, "a-1.zip: no file under --from") and "not followed" in text, "a link is not followed")
        p = check(td, "dirty", after=lambda s: (s / "kit/shared.txt").write_bytes(b"changed\n"))[0]
        expect(has(p, "differs from the committed version"), "file of this directory differs from HEAD")
        p = check(td, "untracked", edit=jedit(lambda f: f[7].update(repo="kit/none.txt")))[0]
        expect(has(p, "is not one file tracked"), "file of this directory not tracked")
        p = check(td, "dir", edit=jedit(lambda f: f[7].update(repo="kit/export")))[0]
        expect(has(p, "is not one file tracked"), "a directory as a file of this directory")
        p = check(td, "skip", after=lambda s: _git(s, "update-index", "--skip-worktree", "kit/shared.txt"))[0]
        expect(has(p, "skip-worktree"), "file of this directory with skip-worktree")

        # 5. the export
        def export_of(content: bytes):
            def make(src: Path) -> Path:
                out = src.parent / "export"
                for rel in ("kit/shared.txt", sheet):
                    (out / rel).parent.mkdir(parents=True, exist_ok=True)
                    (out / rel).write_bytes((src / rel).read_bytes())
                (out / "kit/shared.txt").write_bytes(content)
                return out
            return make
        p = check(td, "export-same", export=export_of(shared))[0]
        expect(p == [], f"export identical: {p}")
        p = check(td, "export-diff", export=export_of(b"other\n"))[0]
        expect(has(p, "of the export differs"), "export differs")

        # the final state
        p, items, data, _, src = check(td, "final", final=True, allow_pending=False)
        expect(p == [], f"final: {p}")
        p = check(td, "final-stray", final=True, stage_files=dict(stage_default, **{"stray.zip": x_zip}))[0]
        expect(has(p, "stray.zip under --from is not a file"), "final with an unlisted file")
        p = check(td, "final-mark", final=True, edit=lambda f: f.update({sheet: f[sheet] + PENDING_MARK + "\n"}))[0]
        expect(has(p, "still holds"), "final with the mark left")
        p = check(td, "final-row", final=True, edit=lambda f: f.update({sheet: re.sub(r"\| `s-idle\.tsv` [^\n]*\n", "", f[sheet])}))[0]
        expect(has(p, "does not name s-idle.tsv"), "final with a row missing")
        p = check(td, "final-rowsha", final=True, edit=tedit(sheet, f"| samples idle | `{sha_s}` |", "| samples idle | (none) |"))[0]
        expect(has(p, "does not give s-idle.tsv with its SHA-256"), "final with a row without its SHA-256")
        p = check(td, "final-part", final=True, edit=tedit(sheet, "| `s-idle.tsv` | Measurement | samples idle |",
                                                             "| `s-idle.tsv` | Shared | samples idle |"))[0]
        expect(has(p, "another part or contents"), "final with another part")
        p = check(td, "final-self", final=True, edit=lambda f: f.update({sheet: re.sub(r"\| `datasheet\.md` [^\n]*\n", "", f[sheet])}))[0]
        expect(has(p, "does not name datasheet.md"), "final without the datasheet row")
        p = check(td, "final-selfsha", final=True, edit=tedit(sheet, SELF_SHA_CELL, f"`{sha_x}`"))[0]
        expect(has(p, "cannot give the SHA-256 of the datasheet"), "final with a SHA-256 for the datasheet")
        p = check(td, "final-pend", final=True, edit=jedit(lambda f: f.insert(0, entry(
            "p.zip", "Measurement", "p", None, RECORDS[1], "p"))))[0]
        expect(has(p, "p.zip: pending"), "final with a pending file")
        p = check(td, "final-dirtyrec", final=True,
                  after=lambda s: (s / RECORDS[1]).write_text((s / RECORDS[1]).read_text() + "x"))[0]
        expect(has(p, f"{RECORDS[1]} differs from the committed"), "final with a record differing from HEAD")
        p = check(td, "final-dirtylist", final=True,
                  after=lambda s: (s / LIST_FILE).write_text((s / LIST_FILE).read_text() + " "))[0]
        expect(has(p, "differs from the committed"), "final with the list differing from HEAD")

        # the draft, against a stand-in on the loopback interface
        token = "tok-selftest-0123"
        logs = io.StringIO()
        counter = iter(range(1000))

        def fresh_items():
            return check(td, f"up{next(counter)}", final=True, allow_pending=False)[1:3]

        def puts(mock, since=0):
            return [r for r in mock.requests[since:] if r[0] == "PUT"]

        mock = _Mock(token)
        try:
            items, data = fresh_items()
            p = upload(items, data, token, mock.base, logs)
            expect(p == [] and set(mock.files) == {it.name for it in items}, f"upload: {p}")
            expect(len(puts(mock)) == len(items), "upload sends every file once")
            expect([s for _, s in mock.order] == sorted(s for _, s in mock.order), "the smallest file first")
            expect(all(r[2] == "Bearer " + token for r in mock.requests), "every request carries the token")
            n = len(mock.requests)
            p = upload(items, data, token, mock.base, logs)
            expect(p == [] and not puts(mock, n), "second upload sends nothing")

            missing = [it for it in fresh_items()[0]]
            for it in missing:
                if it.name == "w-2.zip":
                    it.md5 = it.size = it.path = None
            p = compare_draft(missing, mock.files, logs)
            expect(p == [] and "not compared: missing here" in logs.getvalue(), "a file missing here is not compared")

            held = mock.files["s-idle.tsv"]
            mock.files["s-idle.tsv"] = ("f" * 32, held[1])
            n = len(mock.requests)
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "holds s-idle.tsv with other content") and not puts(mock, n), "other content stops it")
            mock.files["s-idle.tsv"] = (held[0], held[1] + 1)
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "holds s-idle.tsv with other content"), "another size stops it")
            mock.files["s-idle.tsv"] = (held[0], None)
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "holds s-idle.tsv with other content"), "a size not given stops it")
            mock.files = {"extra.bin": ("e" * 32, 1)}
            n = len(mock.requests)
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "extra.bin") and not puts(mock, n), "a file of the draft outside the list stops it")

            mock.files, mock.corrupt = {}, True
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "another MD5 or size than the check"), "a wrong MD5 from the service is caught")
            mock.files, mock.corrupt, mock.drop = {}, False, True
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "does not hold exactly"), "a file the service did not keep is caught")
            mock.files, mock.drop = {}, False

            items2, data2 = fresh_items()
            changed = next(it for it in items2 if it.name == "w-2.zip")
            changed.path.write_bytes(w_zip[:-1] + b"!")
            p = upload(items2, data2, token, mock.base, logs)
            expect(has(p, "w-2.zip changed under --from") and "w-2.zip" not in mock.files, "a file changed after the check")
            mock.files = {}
            items3, data3 = fresh_items()
            grown = next(it for it in items3 if it.name == "w-2.zip")
            with open(grown.path, "ab") as f:
                f.write(b"more")
            p = upload(items3, data3, token, mock.base, logs)
            expect(has(p, "w-2.zip changed under --from"), "a file that grew after the check")
            capped = _Capped(io.BytesIO(b"0123456789"), 4)
            expect(capped.read(100) + capped.read(100) == b"0123" and capped.md5.hexdigest() == _md5(b"0123").hexdigest(),
                   "the sent bytes stop at the checked size")
            mock.files = {}

            for attr, value, word in (("state", "done", "unsubmitted draft"), ("submitted", True, "unsubmitted draft"),
                                      ("doi", "10.5281/zenodo.9", "did not reserve")):
                old = getattr(mock, attr)
                setattr(mock, attr, value)
                n = len(mock.requests)
                p = upload(items, data, token, mock.base, logs)
                expect(has(p, word) and not puts(mock, n), f"draft {attr}")
                setattr(mock, attr, old)

            other = _Mock(token)
            try:
                mock.bucket_base = f"{other.base}/files/b1"
                p = upload(items, data, token, mock.base, logs)
                expect(has(p, "not on the API host") and other.requests == [], "bucket on another host")
            finally:
                other.close()
                mock.bucket_base = None
            try:
                api_call("GET", "http://127.0.0.2:1/api/x", token, mock.base)
                expect(False, "a URL outside the API is refused")
            except Usage:
                pass
        finally:
            mock.close()

        base_src = td / "base" / "paper"
        inside = td / "base" / "token.txt"
        inside.write_text(token)
        upper = Path(str(inside).upper())  # the same file on a file system that ignores case (Windows, macOS)
        for probe in (inside, upper) if upper.exists() else (inside,):
            try:
                read_token(probe, base_src)
                expect(False, f"a token file inside the work tree is refused ({probe.name})")
            except Usage:
                pass
        outside = td / "token.txt"
        outside.write_text(token + "\n")
        expect(read_token(outside, base_src) == token, "a token file outside is read")
        outside.write_text("two words")
        try:
            read_token(outside, base_src)
            expect(False, "a malformed token file is refused")
        except Usage:
            pass
        expect(token not in logs.getvalue(), "the token is never printed")
    finally:
        _OPENER = saved_opener
        for dirpath, _dirs, names in os.walk(tmp):  # git writes read-only objects
            for n in names:
                with_mode = os.path.join(dirpath, n)
                try:
                    os.chmod(with_mode, stat.S_IREAD | stat.S_IWRITE)
                except OSError:
                    pass
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print(f"selftest FAIL: {f}")
    if fails:
        return 1
    print("deposit selftest ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
