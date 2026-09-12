#!/usr/bin/env python3
"""Audit the Rust dependency layer (`src-tauri/Cargo.lock`) with cargo-audit,
and keep the ignore list in `.cargo/audit.toml` from quietly rotting.

Why a wrapper instead of plain `cargo audit` (F-2, 2026-09-12)
--------------------------------------------------------------
Measured with cargo-audit 0.22.2: when an advisory is listed under
`[advisories] ignore`, **it disappears from the human-readable output
entirely** -- no "2 advisories ignored" line, no ID, nothing. So a green run
and a green-because-suppressed run look identical. That is the same failure
mode this repo removed from the redaction test (a silent skip that read as a
pass), so it is removed here too.

This wrapper therefore:

1. runs cargo-audit **without** the repo config (in a temp directory holding
   only a copy of the lockfile), so the raw finding set is visible;
2. applies the ignore list from `.cargo/audit.toml` itself and **prints every
   suppressed ID**, so a reader of the log always sees what was waived;
3. fails when an ignore entry is **stale** -- the advisory is no longer
   reported, so the waiver has outlived its reason and must be deleted.

Note that (3) is the part `cargo audit` cannot do for us: an ignore entry that
no longer matches anything is invisible and immortal.

Exit codes:
    0 = no vulnerability outside the ignore list, and no stale ignore entry
    1 = at least one vulnerability is not covered by the ignore list
    2 = an ignore entry is stale (delete it from .cargo/audit.toml)
    3 = cargo-audit is missing, or failed in a way we cannot interpret
    4 = invalid arguments / I/O error
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

# ⚠️ Windows の既定コンソールは cp932 で、出力に非 ASCII が 1 文字でも混ざると
# `UnicodeEncodeError` で落ちる。★ 2026-09-12 に変異テストで実際に踏んだ ——
# しかも Python の未捕捉例外は exit 1 なので、**「脆弱性を検出した」と区別が付かなかった**。
# → ★ 呼び出し側の `PYTHONUTF8=1` に依存せず、ここで閉じる。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):  # pragma: no cover
        pass

EXIT_OK = 0
EXIT_VULN = 1
EXIT_STALE_IGNORE = 2
EXIT_TOOL = 3
EXIT_USAGE = 4

DEFAULT_LOCKFILE = "src-tauri/Cargo.lock"
DEFAULT_CONFIG = ".cargo/audit.toml"

_IGNORE_BLOCK_RE = re.compile(r"ignore\s*=\s*\[(.*?)\]", re.DOTALL)
_ID_RE = re.compile(r'"([^"]+)"')


def read_ignore_list(path: Path) -> List[str]:
    """Extract `[advisories] ignore = [...]` from `.cargo/audit.toml`.

    A regex rather than `tomllib`, so this also runs on Python < 3.11. Missing
    file or missing key both mean "nothing is waived", which is a legitimate
    and preferable state.
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    # Drop comments so an ID mentioned in prose is not mistaken for an entry.
    text = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    m = _IGNORE_BLOCK_RE.search(text)
    if not m:
        return []
    return _ID_RE.findall(m.group(1))


def run_cargo_audit(lockfile: Path) -> Tuple[dict, str]:
    """Run cargo-audit on a copy of `lockfile` in a config-free directory.

    Returns `(report, raw_stderr)`. Raises RuntimeError if cargo-audit cannot
    be run or produced something unreadable.
    """
    exe = shutil.which("cargo-audit")
    if exe is None:
        raise RuntimeError(
            "cargo-audit not found on PATH. Install it with "
            "`cargo install cargo-audit --locked`."
        )
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        shutil.copyfile(lockfile, sandbox / "Cargo.lock")
        proc = subprocess.run(
            [exe, "audit", "--file", "Cargo.lock", "--json"],
            cwd=str(sandbox),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    raw = (proc.stdout or "").strip()
    if not raw:
        raise RuntimeError(
            "cargo-audit produced no JSON (exit "
            + str(proc.returncode)
            + "): "
            + (proc.stderr or "").strip()[:500]
        )
    try:
        report = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("cargo-audit JSON was unreadable: " + str(exc)) from exc
    return report, (proc.stderr or "")


def extract_findings(report: dict) -> Tuple[List[dict], int, int]:
    """Return `(vulnerabilities, crate_count, advisory_db_count)`.

    Each vulnerability is flattened to `{id, crate, version, title, patched}`.
    """
    vulns = []
    for v in (report.get("vulnerabilities") or {}).get("list") or []:
        adv = v.get("advisory") or {}
        pkg = v.get("package") or {}
        patched = (v.get("versions") or {}).get("patched") or []
        vulns.append(
            {
                "id": adv.get("id") or "(no id)",
                "crate": pkg.get("name") or "?",
                "version": pkg.get("version") or "?",
                "title": (adv.get("title") or "").replace("\n", " "),
                "patched": ", ".join(patched) if patched else "(none published)",
            }
        )
    crate_count = (report.get("lockfile") or {}).get("dependency-count") or 0
    db_count = (report.get("database") or {}).get("advisory-count") or 0
    return vulns, crate_count, db_count


def summarise_warnings(report: dict) -> List[Tuple[str, int]]:
    warnings = report.get("warnings") or {}
    if not isinstance(warnings, dict):
        return []
    return sorted((kind, len(items)) for kind, items in warnings.items())


def evaluate(
    vulns: Sequence[dict], ignore: Sequence[str]
) -> Tuple[List[dict], List[dict], List[str]]:
    """Split findings into `(blocking, waived, stale_ignores)`."""
    ignore_set: Set[str] = set(ignore)
    found_ids = {v["id"] for v in vulns}
    blocking = [v for v in vulns if v["id"] not in ignore_set]
    waived = [v for v in vulns if v["id"] in ignore_set]
    stale = sorted(ignore_set - found_ids)
    return blocking, waived, stale


def report_text(
    lockfile: Path,
    config: Path,
    crate_count: int,
    db_count: int,
    blocking: Sequence[dict],
    waived: Sequence[dict],
    stale: Sequence[str],
    warning_counts: Sequence[Tuple[str, int]],
) -> Tuple[str, int]:
    out: List[str] = []
    out.append("lockfile      : " + str(lockfile))
    out.append("ignore config : " + str(config))
    out.append(
        "scanned       : "
        + str(crate_count)
        + " crate dependencies against "
        + str(db_count)
        + " advisories"
    )
    out.append(
        "findings      : "
        + str(len(blocking) + len(waived))
        + " vulnerability/vulnerabilities ("
        + str(len(waived))
        + " waived by config)"
    )
    if warning_counts:
        out.append(
            "informational : "
            + ", ".join(k + "=" + str(n) for k, n in warning_counts)
            + "  (not a gate; cargo-audit reports these as warnings)"
        )

    # ⚠️ Always print the waived list: cargo-audit's own output hides it.
    if waived:
        out.append("")
        out.append("WAIVED (listed in " + str(config) + " -- rationale lives there):")
        for v in waived:
            out.append(
                "  - {id}  {crate} {version}  patched: {patched}".format(**v)
            )
            out.append("      " + v["title"][:100])
    if stale:
        out.append("")
        out.append("STALE IGNORE: these ids are waived but no longer reported:")
        for i in stale:
            out.append("  - " + i)
        out.append(
            "  -> delete them from "
            + str(config)
            + ". A waiver that matches nothing is invisible and never expires."
        )
    if blocking:
        out.append("")
        out.append("VULNERABLE:")
        for v in blocking:
            out.append(
                "  - {id}  {crate} {version}  patched: {patched}".format(**v)
            )
            out.append("      " + v["title"][:100])
        out.append("")
        out.append(
            "  -> try `cargo update -p <crate>` from src-tauri/ first. If semver has no"
        )
        out.append(
            "     solution, add the id to " + str(config) + " WITH a rationale,"
        )
        out.append("     the dependency path, and a review date.")
        out.append(
            "  -> NOTE: `cargo update -p <crate>` can also re-resolve unrelated edges."
        )
        out.append(
            "     Check `git diff` and keep the lockfile change to the crate you meant."
        )

    if blocking:
        code = EXIT_VULN
        verdict = "NG: " + str(len(blocking)) + " vulnerability/vulnerabilities need action."
    elif stale:
        code = EXIT_STALE_IGNORE
        verdict = "NG: " + str(len(stale)) + " stale ignore entry/entries."
    else:
        code = EXIT_OK
        verdict = (
            "OK: "
            + str(crate_count)
            + " crates scanned, 0 vulnerabilities outside the ignore list, "
            + str(len(waived))
            + " waived, 0 stale."
        )
    out.append("")
    out.append(verdict)
    return "\n".join(out), code


# --- self-test ----------------------------------------------------------------


def self_test() -> int:
    """Prove the split and the stale detection are not no-ops."""
    failures: List[str] = []

    def vuln(i: str) -> dict:
        return {
            "id": i,
            "crate": "c",
            "version": "1",
            "title": "t",
            "patched": "p",
        }

    # (1) nothing found, nothing waived -> clean
    b, w, s = evaluate([], [])
    if (b, w, s) != ([], [], []):
        failures.append("(1) empty input must produce empty output")

    # (2) a finding not in the ignore list blocks
    b, w, s = evaluate([vuln("RUSTSEC-1")], [])
    if len(b) != 1 or w or s:
        failures.append("(2) an unwaived finding must block")

    # (3) a finding in the ignore list is waived, not dropped
    b, w, s = evaluate([vuln("RUSTSEC-1")], ["RUSTSEC-1"])
    if b or len(w) != 1 or s:
        failures.append("(3) a waived finding must still be reported as waived")

    # (4) ⚠️ the core case: an ignore entry that matches nothing is stale
    b, w, s = evaluate([], ["RUSTSEC-1"])
    if b or w or s != ["RUSTSEC-1"]:
        failures.append("(4) an ignore entry matching nothing must be flagged stale")

    # (5) mixed
    b, w, s = evaluate([vuln("A"), vuln("B")], ["B", "C"])
    if [v["id"] for v in b] != ["A"] or [v["id"] for v in w] != ["B"] or s != ["C"]:
        failures.append("(5) mixed case mis-split")

    # (6) exit codes follow the verdicts
    cases = [
        ([], [], [], EXIT_OK),
        ([vuln("A")], [], [], EXIT_VULN),
        ([], [vuln("B")], [], EXIT_OK),
        ([], [], ["C"], EXIT_STALE_IGNORE),
        ([vuln("A")], [], ["C"], EXIT_VULN),  # a real vulnerability outranks stale
    ]
    for blocking, waived, stale, want in cases:
        _, got = report_text(
            Path("l"), Path("c"), 1, 1, blocking, waived, stale, []
        )
        if got != want:
            failures.append(
                "(6) exit code for ({}, {}, {}): want {}, got {}".format(
                    len(blocking), len(waived), len(stale), want, got
                )
            )

    # (7) the waived ids must appear in the printed text (cargo-audit hides them)
    text, _ = report_text(
        Path("l"), Path("c"), 1, 1, [], [vuln("RUSTSEC-WAIVED")], [], []
    )
    if "RUSTSEC-WAIVED" not in text:
        failures.append("(7) a waived id must be printed")

    # (8) ignore-list parsing: comments must not leak ids
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "audit.toml"
        p.write_text(
            '# see RUSTSEC-9999-9999 for background\n'
            "[advisories]\n"
            'ignore = [\n    "RUSTSEC-2026-0194",  # a comment\n    "RUSTSEC-2026-0195",\n]\n',
            encoding="utf-8",
        )
        got = read_ignore_list(p)
        if got != ["RUSTSEC-2026-0194", "RUSTSEC-2026-0195"]:
            failures.append("(8) ignore parsing wrong: " + repr(got))
        missing = Path(td) / "nope.toml"
        if read_ignore_list(missing) != []:
            failures.append("(8) a missing config must mean 'nothing waived'")
        p.write_text("[advisories]\n", encoding="utf-8")
        if read_ignore_list(p) != []:
            failures.append("(8) a config without `ignore` must mean 'nothing waived'")

    if failures:
        for f in failures:
            print("NG self-test: " + f, file=sys.stderr)
        return EXIT_USAGE
    print(
        "OK self-test: 8 groups (empty / unwaived blocks / waived reported / "
        "stale detected / mixed split / exit codes / waived printed / config parsing)"
    )
    return EXIT_OK


# --- entry point --------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit src-tauri/Cargo.lock and validate the cargo-audit ignore list.",
    )
    parser.add_argument("--lockfile", default=DEFAULT_LOCKFILE)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument(
        "--self-test", action="store_true", help="run the built-in cases and exit"
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    lockfile = Path(args.lockfile)
    config = Path(args.config)
    if not lockfile.exists():
        print("ERROR: lockfile not found: " + str(lockfile), file=sys.stderr)
        return EXIT_USAGE

    try:
        ignore = read_ignore_list(config)
    except OSError as exc:
        print("ERROR: could not read " + str(config) + ": " + str(exc), file=sys.stderr)
        return EXIT_USAGE

    try:
        report, _ = run_cargo_audit(lockfile)
    except RuntimeError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return EXIT_TOOL

    vulns, crate_count, db_count = extract_findings(report)
    if crate_count == 0:
        print(
            "ERROR: cargo-audit reported 0 scanned crates.\n"
            "       Treated as a failure: an empty scan is indistinguishable from a\n"
            "       broken invocation, and must not be read as 'nothing is vulnerable'.",
            file=sys.stderr,
        )
        return EXIT_TOOL

    blocking, waived, stale = evaluate(vulns, ignore)
    text, code = report_text(
        lockfile,
        config,
        crate_count,
        db_count,
        blocking,
        waived,
        stale,
        summarise_warnings(report),
    )
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
