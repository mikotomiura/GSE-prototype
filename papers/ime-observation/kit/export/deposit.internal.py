#!/usr/bin/env python3
# kit: selftest
"""Checks the files of the dataset deposit and uploads them to the reserved draft (Python standard library only).

  deposit.internal.py --from DIR [--allow-pending] [--export DIR]            check (no network)
  deposit.internal.py --from DIR [--export DIR] --remote [--token-file PATH] check, then read the draft
  deposit.internal.py --from DIR [--export DIR] --upload [--token-file PATH] check, then upload to the draft
  deposit.internal.py --table                                                print the rows of the datasheet table
  deposit.internal.py --selftest

This tool is internal: it is never exported (its name has the internal form). The list of the files of the deposit
is kit/export/deposit.internal.json. Each file has its name in the deposit, its part and what it holds, and either the
SHA-256 of an archive or a sample (found by that SHA-256 under the directory given with --from, whatever its local
name) or the path of a file of this directory (taken from the committed version, HEAD; a file that is untracked,
differs from HEAD or carries an assume-unchanged or skip-worktree mark is refused). A SHA-256 of null marks a file
that is not packed or recorded yet (pending). The check

  1. refuses a list whose names are not unique or not flat ([A-Za-z0-9._-]), or whose SHA-256 repeat;
  2. requires the SHA-256 of every archive (*.zip) to stand in the table "Deposits" of its record
     (experiment/data.md or experiment/data.windows.md) and every SHA-256 of those tables to belong to a file of the
     list, so that an archive packed and recorded on a measuring machine cannot be left out; the SHA-256 of any
     other file with a SHA-256 must stand somewhere in its record;
  3. requires every SHA-256 in the table "Files of the deposit" of the datasheet to be that of the file its row
     names, and every name there to be a file of the list;
  4. finds every file of the list under --from; a pending file fails the check unless --allow-pending is given, and
     a file under --from that the list does not name is reported;
  5. with --export DIR (a fresh export of the same commit), requires every file taken from this directory to be
     byte-identical to the file of the export at the same path.

--remote then reads the draft (GET only, also when files are missing): it must be the draft that reserved the DOI of
the list and be unsubmitted, and every file already in it must be a file of the list with the same MD5 and size
(a file that is missing here is not compared). --upload requires the final
state as well: nothing pending, no file under --from that the list does not name, the list, the records and the
datasheet equal to HEAD, every file of the list (but the datasheet itself) named in the datasheet table with its
SHA-256, and no "(to be filled in at deposit)" left in the datasheet. It then sends each file that the draft does not
hold yet to the bucket of the draft and compares the MD5 and size that the service returns. A file of the same name
with other content, or a file of the draft that the list does not name, stops it before anything is sent (remove
such a file in the web form). The tool never publishes: it has no call that submits or publishes a record. The token
is read from --token-file (default C:/zenodo/zenodo_token.txt) inside the process, sent only to the API host and
never printed; a token file inside the git work tree is refused.

Exit status: 0 the check passed (and the upload completed), 1 the check failed, 2 a usage or environment error.
"""

from __future__ import annotations

import argparse
import contextlib
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
TOKEN_FILE = "C:/zenodo/zenodo_token.txt"
PARTS = ("Measurement", "Calibration pilot", "Shared")
KEYS = {"name", "part", "contents", "sha256", "record", "repo", "datasheet"}
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
SHA_RE = re.compile(r"[0-9a-f]{64}")
CELL_SHA = re.compile(r"`([0-9a-f]{64})`")
CELL_NAME = re.compile(r"`([^`]+)`")
PENDING_MARK = "(to be filled in at deposit)"
TABLE_LEAD = "**Files of the deposit.**"
SELF_SHA_CELL = "not given (this file)"
CHUNK = 1 << 20


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
        return subprocess.run(["git", "-C", str(source), *args], capture_output=True)
    except OSError as e:
        raise Usage(f"cannot run git: {e.__class__.__name__}") from None


def committed(source: Path, rel: str) -> tuple[bytes | None, str | None]:
    """The committed bytes of a file of the source directory, or the reason why they cannot be used."""
    r = _git(source, "ls-files", "-v", "--", rel)
    if r.returncode != 0:
        raise Usage(f"git ls-files failed in {source}")
    tags = r.stdout.decode("utf-8", "replace").splitlines()
    if len(tags) != 1:
        return None, "is not tracked by git"
    if not tags[0].startswith("H "):
        return None, "carries an assume-unchanged or skip-worktree mark"
    if _git(source, "diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        return None, "differs from the committed version (HEAD)"
    r = _git(source, "show", f"HEAD:./{rel}")
    if r.returncode != 0:
        return None, "cannot be read from HEAD"
    return r.stdout, None


def read_text(source: Path, rel: str, require_committed: bool) -> tuple[str | None, str | None]:
    """The text of a file of the source directory (the committed one when required), or the reason."""
    if require_committed:
        blob, why = committed(source, rel)
        if blob is None:
            return None, why
        raw = blob
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


def file_digests(path: Path) -> tuple[str, str, int]:
    sha, md5, size = hashlib.sha256(), _md5(), 0
    with open(path, "rb") as f:
        while True:
            block = f.read(CHUNK)
            if not block:
                break
            sha.update(block)
            md5.update(block)
            size += len(block)
    return sha.hexdigest(), md5.hexdigest(), size


def _relative(rel: object) -> bool:
    if not isinstance(rel, str) or not rel or "\\" in rel or ":" in rel:
        return False
    p = PurePosixPath(rel)
    return not p.is_absolute() and ".." not in p.parts and "." not in p.parts


# ---------------------------------------------------------------- the list, the records and the datasheet

def load_list(text: str) -> tuple[dict, list[str]]:
    """The list and its problems of form (names, parts, keys, SHA-256)."""
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
        if not isinstance(e.get("contents"), str) or not e["contents"].strip():
            problems.append(f"{where}: 'contents' is empty")
        if ("repo" in e) == ("sha256" in e):
            problems.append(f"{where}: exactly one of 'repo' and 'sha256' must be given")
            continue
        if "repo" in e:
            if not _relative(e["repo"]):
                problems.append(f"{where}: 'repo' must be a relative path of this directory")
            if "record" in e:
                problems.append(f"{where}: a file of this directory has no 'record'")
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
        if "datasheet" in e:
            if e["datasheet"] is not True or "repo" not in e:
                problems.append(f"{where}: 'datasheet' marks the datasheet, a file of this directory")
            else:
                sheets += 1
    if sheets != 1:
        problems.append("exactly one file of the list must be marked as the datasheet")
    return data, problems


def deposits_shas(text: str) -> list[str] | None:
    """The SHA-256 of the archives in the table under the heading 'Deposits', or None without that heading."""
    found, inside, seen = [], False, False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Deposits"
            seen = seen or inside
            continue
        if inside and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3:
                m = CELL_SHA.fullmatch(cells[2])
                if m:
                    found.append(m.group(1))
    return found if seen else None


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
        rows.append([c.strip() for c in lines[k].strip().strip("|").split("|")])
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
    given: dict[str, str | None] = {}
    for cells in rows:
        if len(cells) != 4:
            problems.append(f"a row of the datasheet table has {len(cells)} cells: {' | '.join(cells)[:80]}")
            continue
        m = CELL_NAME.fullmatch(cells[0])
        name = m.group(1) if m else None
        if name is None and cells[0] != PENDING_MARK:
            problems.append(f"a file cell of the datasheet table is neither a name in backticks nor the mark: {cells[0][:60]}")
        m = CELL_SHA.fullmatch(cells[3])
        sha = m.group(1) if m else None
        if name is not None:
            if name not in by_name:
                problems.append(f"the datasheet table names {name}, which is not a file of the list")
            if name in given:
                problems.append(f"the datasheet table names {name} twice")
            given[name] = sha
        if sha is not None:
            if sha not in by_sha:
                problems.append(f"the datasheet table gives the SHA-256 {sha[:12]}..., which belongs to no file of the list")
            elif name is not None and by_sha[sha] != name:
                problems.append(f"the datasheet table gives {name} the SHA-256 of {by_sha[sha]}")
    if final:
        if PENDING_MARK in text:
            problems.append(f"the datasheet still holds '{PENDING_MARK}'")
        for it in items:
            if it.entry.get("datasheet"):
                if it.name not in given:
                    problems.append(f"the datasheet table does not name the datasheet itself ({it.name})")
                elif given[it.name] is not None:
                    problems.append("the datasheet table cannot give the SHA-256 of the datasheet itself")
            elif it.sha256 is None or given.get(it.name) != it.sha256:
                problems.append(f"the datasheet table does not give {it.name} with its SHA-256")
    return problems


# ---------------------------------------------------------------- the check

def run_check(source: Path, staging: Path | None, *, allow_pending: bool, final: bool,
              export: Path | None, out) -> tuple[list[str], list[Item], dict]:
    """Checks the list against the records, the datasheet, the committed files and the files under --from."""
    text, why = read_text(source, LIST_FILE, final)
    if text is None:
        return [f"{LIST_FILE} {why}"], [], {}
    data, problems = load_list(text)
    if problems:
        return problems, [], data
    items = [Item(e) for e in data["files"]]

    # 2. the records
    deposits: dict[str, list[str]] = {}
    for rel in RECORDS:
        rtext, why = read_text(source, rel, final)
        if rtext is None:
            problems.append(f"{rel} {why}")
            continue
        shas = deposits_shas(rtext)
        if shas is None:
            problems.append(f"{rel} has no table under the heading 'Deposits'")
            continue
        deposits[rel] = shas
        for it in items:
            if it.sha256 is None or it.entry.get("record") != rel:
                continue
            if it.name.endswith(".zip") and it.sha256 not in shas:
                problems.append(f"{it.name}: its SHA-256 is not in the table 'Deposits' of {rel}")
            elif not it.name.endswith(".zip") and it.sha256 not in rtext:
                problems.append(f"{it.name}: its SHA-256 is not in {rel}")
    listed = {it.sha256 for it in items if it.sha256}
    for rel, shas in deposits.items():
        for sha in shas:
            if sha not in listed:
                problems.append(f"{rel} records the archive {sha[:12]}... in 'Deposits', but the list has no file with it")

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
    found: dict[str, list[Path]] = {}
    if staging is not None:
        if not staging.is_dir():
            raise Usage(f"--from is not a directory: {staging}")
        for path in sorted(p for p in staging.rglob("*") if p.is_file() and not p.is_symlink()):
            sha, md5, size = file_digests(path)
            found.setdefault(sha, []).append(path)
            if sha in listed:
                it = next(i for i in items if i.sha256 == sha)
                if it.path is None:
                    it.path, it.md5, it.size = path, md5, size
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
    for sha, paths in found.items():
        if sha not in listed:
            for path in paths:
                print(f"  unlisted {path.relative_to(staging).as_posix()} (the list names no file with its SHA-256)",
                      file=out)
                if final:
                    problems.append(f"{path.name} under --from is not a file of the list")
    return problems, items, data


# ---------------------------------------------------------------- the draft

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
        with urllib.request.urlopen(req, timeout=900) as r:
            status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        return 0, f"network error ({e.__class__.__name__})"
    try:
        return status, (json.loads(raw.decode("utf-8")) if raw else None)
    except (ValueError, UnicodeDecodeError):
        return status, raw[:300].decode("utf-8", "replace")


def read_draft(data: dict, token: str, api: str) -> tuple[str | None, dict, list[str]]:
    """The bucket of the draft, its files {name: (md5, size)} and the problems of its state."""
    dep = data["deposition"]
    status, js = api_call("GET", f"{api}/deposit/depositions/{dep}", token, api)
    if status != 200 or not isinstance(js, dict):
        return None, {}, [f"cannot read the draft {dep} (HTTP {status})"]
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
            print(f"  to send  {it.name}", file=out)
        elif held[0] == it.md5 and held[1] in (None, it.size):
            print(f"  in draft {it.name}", file=out)
        else:
            problems.append(f"the draft holds {it.name} with other content (remove it in the web form first)")
    return problems


def upload(items: list[Item], data: dict, token: str, api: str, out) -> list[str]:
    bucket, remote, problems = read_draft(data, token, api)
    if not problems:
        problems = compare_draft(items, remote, out)
    if problems or bucket is None:
        return problems or ["the draft has no bucket"]
    for it in items:
        if it.name in remote:
            continue
        url = bucket + "/" + urllib.parse.quote(it.name)
        if it.blob is not None:
            status, js = api_call("PUT", url, token, api, body=it.blob)
        else:
            with open(it.path, "rb") as f:
                status, js = api_call("PUT", url, token, api, body=f, length=it.size)
        if status not in (200, 201) or not isinstance(js, dict):
            return [f"sending {it.name} failed (HTTP {status}); nothing after it was sent"]
        if js.get("key") != it.name or js.get("checksum") != "md5:" + it.md5 or js.get("size") != it.size:
            return [f"the service holds {it.name} with another MD5 or size than was sent; nothing after it was sent"]
        print(f"  sent     {it.name}  ({it.size} bytes)", file=out)
    _, remote, problems = read_draft(data, token, api)
    if not problems:
        if set(remote) != {it.name for it in items}:
            problems.append("after the upload the draft does not hold exactly the files of the list")
        for it in items:
            if remote.get(it.name, ("", None))[0] != it.md5:
                problems.append(f"after the upload the draft holds {it.name} with another MD5")
    return problems


def read_token(path: Path, source: Path) -> str:
    try:
        real = path.resolve(strict=True)
    except OSError:
        raise Usage(f"cannot find the token file {path}") from None
    top = _git(source, "rev-parse", "--show-toplevel")
    if top.returncode == 0:
        root = Path(top.stdout.decode("utf-8", "replace").strip()).resolve()
        if real == root or root in real.parents:
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
        token = read_token(Path(a.token_file), SOURCE) if (a.remote or a.upload) else None
        problems, items, data = run_check(SOURCE, staging, allow_pending=a.allow_pending, final=a.upload,
                                          export=export, out=sys.stdout)
        if a.remote and items:  # reading the draft changes nothing, so it is read even when files are missing
            _, remote, draft_problems = read_draft(data, token, API)
            if not draft_problems:
                draft_problems = compare_draft([it for it in items if it.md5], remote, sys.stdout)
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
        self.token, self.requests, self.files = token, [], {}
        self.state, self.submitted, self.doi, self.dep = "unsubmitted", False, "10.5281/zenodo.7", 7
        self.bucket_base: str | None = None
        self.corrupt = False
        self.drop = False
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


def selftest() -> int:
    fails: list[str] = []

    def expect(ok: bool, label: str) -> None:
        if not ok:
            fails.append(label)

    a_zip, w_zip, s_tsv, x_zip = b"archive-a" * 50, b"archive-w" * 70, b"t\tcpu\n0\t1\n", b"stray"
    shared = b"shared\n"
    sha_a, sha_w, sha_s, sha_x, sha_shared = map(_sha, (a_zip, w_zip, s_tsv, x_zip, shared))
    deposits = "| Cell label | Deposit location | SHA-256 of the archive | Date deposited |\n|---|---|---|---|\n"

    def base_files(final: bool) -> dict[str, str]:
        entries = [
            {"name": "a-1.zip", "part": "Measurement", "contents": "a", "sha256": sha_a, "record": RECORDS[0]},
            {"name": "w-2.zip", "part": "Measurement", "contents": "w", "sha256": sha_w, "record": RECORDS[1]},
            {"name": "s.tsv", "part": "Measurement", "contents": "s", "sha256": sha_s, "record": RECORDS[0]},
            {"name": "shared.txt", "part": "Shared", "contents": "x", "repo": "kit/shared.txt"},
            {"name": "datasheet.md", "part": "Shared", "contents": "d", "repo": "experiment/datasheet.md",
             "datasheet": True},
        ]
        if not final:
            entries.insert(3, {"name": "p.zip", "part": "Calibration pilot", "contents": "p", "sha256": None,
                               "record": RECORDS[1]})
            rows = (f"| {PENDING_MARK} | Measurement | a | `{sha_a}` |\n"
                    f"| `shared.txt` | Shared | x | `{sha_shared}` |\n")
        else:
            rows = (f"| `a-1.zip` | Measurement | a | `{sha_a}` |\n| `w-2.zip` | Measurement | w | `{sha_w}` |\n"
                    f"| `s.tsv` | Measurement | s | `{sha_s}` |\n| `shared.txt` | Shared | x | `{sha_shared}` |\n"
                    f"| `datasheet.md` | Shared | d | {SELF_SHA_CELL} |\n")
        return {
            LIST_FILE: json.dumps({"deposition": 7, "doi": "10.5281/zenodo.7", "files": entries}, indent=1),
            RECORDS[0]: f"# r\n\n## Deposits\n\n{deposits}| a (attempt 1) | no | `{sha_a}` | no |\n\n"
                        f"## Question 5\n\nSamples `{sha_s}`.\n",
            RECORDS[1]: f"# w\n\n## Deposits\n\n{deposits}| w (attempt 2) | no | `{sha_w}` | no |\n",
            "experiment/datasheet.md": f"# Datasheet\n\n{TABLE_LEAD} The files.\n\n"
                                       f"| File | Part | Contents | SHA-256 |\n|---|---|---|---|\n{rows}\nEnd.\n",
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
        (stage / "sub").mkdir(parents=True)
        for rel, data in (stage_files if stage_files is not None else
                          {"x/a.zip": a_zip, "w.zip": w_zip, "sub/samples.tsv": s_tsv}).items():
            (stage / rel).parent.mkdir(parents=True, exist_ok=True)
            (stage / rel).write_bytes(data)
        return src, stage

    def check(td, tag, *, allow_pending=True, final=False, export=None, **kw):
        src, stage = build(td, tag, final=final, **kw)
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

    tmp = tempfile.mkdtemp(prefix="deposit-selftest-")
    try:
        td = Path(tmp)
        p, items, _, text, _ = check(td, "base")
        expect(p == [], f"base: {p}")
        expect("pending  p.zip" in text and "unlisted" not in text, "base: report")
        p = check(td, "pend", allow_pending=False)[0]
        expect(has(p, "p.zip: pending"), "pending without --allow-pending")
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
        p = check(td, "nosheet", edit=jedit(lambda f: f[-1].pop("datasheet")))[0]
        expect(has(p, "marked as the datasheet"), "no datasheet")
        p = check(td, "doi", edit=lambda f: f.update({LIST_FILE: f[LIST_FILE].replace("zenodo.7", "zenodo.8")}))[0]
        expect(has(p, "'doi'"), "DOI of another draft")

        p = check(td, "notdep", edit=lambda f: f.update({RECORDS[0]: f[RECORDS[0]].replace(
            f"| a (attempt 1) | no | `{sha_a}` | no |", "")}))[0]
        expect(has(p, "a-1.zip: its SHA-256 is not in the table"), "archive missing from Deposits")
        p = check(td, "inprose", edit=lambda f: f.update({RECORDS[0]: f[RECORDS[0]].replace(
            f"| a (attempt 1) | no | `{sha_a}` | no |", "") + f"\nNot a row: `{sha_a}`\n"}))[0]
        expect(has(p, "a-1.zip: its SHA-256 is not in the table"), "archive only in prose")
        p = check(td, "extra", edit=lambda f: f.update({RECORDS[1]: f[RECORDS[1]] + f"| y | no | `{sha_x}` | no |\n"}))[0]
        expect(has(p, "the list has no file with it"), "Deposits row without a file of the list")
        p = check(td, "nohead", edit=lambda f: f.update({RECORDS[1]: f[RECORDS[1]].replace("## Deposits", "## Other")}))[0]
        expect(has(p, "has no table under the heading"), "record without Deposits")
        p = check(td, "sample", edit=lambda f: f.update({RECORDS[0]: f[RECORDS[0]].replace(f"Samples `{sha_s}`.", "")}))[0]
        expect(has(p, "s.tsv: its SHA-256 is not in"), "sample not in its record")

        sheet = "experiment/datasheet.md"
        p = check(td, "swap", edit=lambda f: f.update({sheet: f[sheet].replace(
            f"| `shared.txt` | Shared | x | `{sha_shared}` |", f"| `shared.txt` | Shared | x | `{sha_a}` |")}))[0]
        expect(has(p, "gives shared.txt the SHA-256 of a-1.zip"), "datasheet row with another file's SHA-256")
        p = check(td, "unknownsha", edit=lambda f: f.update({sheet: f[sheet].replace(sha_a, sha_x)}))[0]
        expect(has(p, "belongs to no file"), "datasheet SHA-256 of no file")
        p = check(td, "unknownname", edit=lambda f: f.update({sheet: f[sheet].replace("`shared.txt`", "`other.txt`")}))[0]
        expect(has(p, "names other.txt"), "datasheet names a file outside the list")
        p = check(td, "notable", edit=lambda f: f.update({sheet: f[sheet].replace(TABLE_LEAD, "**Files.**")}))[0]
        expect(has(p, "has no table 'Files of the deposit'"), "datasheet without the table")
        p = check(td, "header", edit=lambda f: f.update({sheet: f[sheet].replace(
            "| File | Part | Contents | SHA-256 |", "| File | Part | SHA-256 | Contents |")}))[0]
        expect(has(p, "has no table 'Files of the deposit'"), "datasheet table with other columns")

        p, _, _, text, _ = check(td, "missing", stage_files={"w.zip": w_zip, "s.tsv": s_tsv})
        expect(has(p, "a-1.zip: no file under --from"), "archive missing under --from")
        p, _, _, text, _ = check(td, "stray", stage_files={"a.zip": a_zip, "w.zip": w_zip, "s.tsv": s_tsv,
                                                          "stray.zip": x_zip})
        expect(p == [] and "unlisted stray.zip" in text, "unlisted file is reported in a check")
        p = check(td, "dirty", after=lambda s: (s / "kit/shared.txt").write_bytes(b"changed\n"))[0]
        expect(has(p, "differs from the committed version"), "file of this directory differs from HEAD")
        p = check(td, "untracked", edit=jedit(lambda f: f[4].update(repo="kit/none.txt")))[0]
        expect(has(p, "is not tracked"), "file of this directory not tracked")
        p = check(td, "skip", after=lambda s: _git(s, "update-index", "--skip-worktree", "kit/shared.txt"))[0]
        expect(has(p, "skip-worktree"), "file of this directory with skip-worktree")

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

        p, items, data, _, src = check(td, "final", final=True, allow_pending=False)
        expect(p == [], f"final: {p}")
        p = check(td, "final-stray", final=True, stage_files={"a.zip": a_zip, "w.zip": w_zip, "s.tsv": s_tsv,
                                                               "stray.zip": x_zip})[0]
        expect(has(p, "stray.zip under --from is not a file"), "final with an unlisted file")
        p = check(td, "final-mark", final=True, edit=lambda f: f.update({sheet: f[sheet] + PENDING_MARK + "\n"}))[0]
        expect(has(p, "still holds"), "final with the mark left")
        p = check(td, "final-row", final=True, edit=lambda f: f.update({sheet: f[sheet].replace(
            f"| `s.tsv` | Measurement | s | `{sha_s}` |\n", "")}))[0]
        expect(has(p, "does not give s.tsv"), "final with a row missing")
        p = check(td, "final-self", final=True, edit=lambda f: f.update({sheet: f[sheet].replace(
            "| `datasheet.md` | Shared | d | " + SELF_SHA_CELL + " |\n", "")}))[0]
        expect(has(p, "does not name the datasheet itself"), "final without the datasheet row")
        p = check(td, "final-pend", final=True, edit=jedit(lambda f: f.insert(0, {
            "name": "p.zip", "part": "Measurement", "contents": "p", "sha256": None, "record": RECORDS[1]})))[0]
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

        def fresh_items():
            return check(td, f"up{len(list(td.iterdir()))}", final=True, allow_pending=False)[1:3]

        mock = _Mock(token)
        try:
            items, data = fresh_items()
            data = dict(data, deposition=7, doi="10.5281/zenodo.7")
            p = upload(items, data, token, mock.base, logs)
            expect(p == [] and set(mock.files) == {it.name for it in items}, f"upload: {p}")
            puts = sum(1 for r in mock.requests if r[0] == "PUT")
            expect(puts == len(items), "upload sends every file once")
            expect(all(r[2] == "Bearer " + token for r in mock.requests), "every request carries the token")
            p = upload(items, data, token, mock.base, logs)
            expect(p == [] and sum(1 for r in mock.requests if r[0] == "PUT") == puts, "second upload sends nothing")

            mock.files["s.tsv"] = ("f" * 32, 3)
            before = len(mock.requests)
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "holds s.tsv with other content") and
                   not any(r[0] == "PUT" for r in mock.requests[before:]), "other content stops the upload")
            mock.files = {"extra.bin": ("e" * 32, 1)}
            before = len(mock.requests)
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "extra.bin") and not any(r[0] == "PUT" for r in mock.requests[before:]),
                   "a file of the draft outside the list stops the upload")

            mock.files, mock.corrupt = {}, True
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "another MD5 or size"), "a wrong MD5 from the service is caught")
            mock.files, mock.corrupt = {}, False
            mock.drop = True
            p = upload(items, data, token, mock.base, logs)
            expect(has(p, "does not hold exactly"), "a file the service did not keep is caught")
            mock.files, mock.drop = {}, False

            for attr, value, word in (("state", "done", "unsubmitted draft"), ("submitted", True, "unsubmitted draft"),
                                      ("doi", "10.5281/zenodo.9", "did not reserve")):
                old = getattr(mock, attr)
                setattr(mock, attr, value)
                before = len(mock.requests)
                p = upload(items, data, token, mock.base, logs)
                expect(has(p, word) and not any(r[0] == "PUT" for r in mock.requests[before:]), f"draft {attr}")
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

        inside = td / "base" / "token.txt"
        inside.write_text(token)
        try:
            read_token(inside, td / "base" / "paper")
            expect(False, "a token file inside the work tree is refused")
        except Usage:
            pass
        outside = td / "token.txt"
        outside.write_text(token + "\n")
        expect(read_token(outside, td / "base" / "paper") == token, "a token file outside is read")
        outside.write_text("two words")
        try:
            read_token(outside, td / "base" / "paper")
            expect(False, "a malformed token file is refused")
        except Usage:
            pass
        expect(token not in logs.getvalue(), "the token is never printed")
    finally:
        for dirpath, _dirs, names in os.walk(tmp):  # git writes read-only objects
            for n in names:
                os.chmod(os.path.join(dirpath, n), stat.S_IREAD | stat.S_IWRITE)
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print(f"selftest FAIL: {f}")
    if fails:
        return 1
    print("deposit selftest ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
