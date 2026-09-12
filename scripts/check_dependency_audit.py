#!/usr/bin/env python3
"""Audit the Rust dependency layer (`src-tauri/Cargo.lock`) with cargo-audit,
and keep the waiver list in `.cargo/audit.toml` from quietly rotting.

Why a wrapper instead of plain `cargo audit` (F-2, 2026-09-12)
--------------------------------------------------------------
Measured with cargo-audit 0.22.2: when an advisory is listed under
`[advisories] ignore`, **it disappears from the human-readable output
entirely** -- no "2 advisories ignored" line, no id, nothing. So a green run
and a green-because-suppressed run look identical. That is the same failure
mode this repo removed from the redaction test (a silent skip that read as a
pass), so it is removed here too.

This wrapper therefore:

1. runs cargo-audit in a sandbox with `CARGO_HOME` pointed at a temp directory,
   so **no configuration reaches it at all** -- neither the repo's
   `.cargo/audit.toml` (cwd-relative) nor a user's `$CARGO_HOME/audit.toml`
   (measured 2026-09-12: the latter *does* apply, so isolating cwd alone is not
   enough), and then asserts the run really saw an empty ignore list;
2. applies the waiver list from `.cargo/audit.toml` itself and **prints every
   suppressed id**, so a reader of the log always sees what was waived;
3. fails when a waiver is **stale** -- the advisory is no longer reported, so it
   has outlived its reason and must be deleted;
4. fails when a waiver has **no `# review-by: YYYY-MM-DD`, or that date has
   passed** -- otherwise a waiver for something upstream never fixes (our
   `quick-xml` case) stays green forever and nobody ever looks again;
5. refuses any key in `.cargo/audit.toml` other than `[advisories] ignore`,
   because every other cargo-audit setting would be silently dropped by (1) --
   including settings that *tighten* the check.

(3), (4) and (5) are the parts `cargo audit` cannot do for us.

Exit codes:
    0 = no vulnerability outside the waiver list, and every waiver is in order
    1 = at least one vulnerability is not covered by the waiver list
    2 = a waiver is stale, or its review-by date has passed
    3 = cargo-audit is missing, or failed in a way we cannot interpret
    4 = invalid arguments, unusable config, or I/O error
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

# Windows' default console is cp932 and dies with UnicodeEncodeError on a single
# non-ASCII character in the output. Measured 2026-09-12 in a mutation test --
# and because an uncaught Python exception exits 1, it was **indistinguishable
# from "a vulnerability was found"**. Close it here rather than relying on the
# caller to set PYTHONUTF8=1.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCKFILE = REPO_ROOT / "src-tauri" / "Cargo.lock"
DEFAULT_CONFIG = REPO_ROOT / ".cargo" / "audit.toml"

_SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
_IGNORE_BLOCK_RE = re.compile(r"^\s*ignore\s*=\s*\[(.*?)\]", re.DOTALL | re.MULTILINE)
_ID_RE = re.compile(r"""["']([^"']+)["']""")
# The `[,\]]?` matters: a one-element array closes on the same line
# (`ignore = ["X"]  # review-by: ...`), and without it that form silently looks
# like a waiver with no date.
_REVIEW_BY_RE = re.compile(
    r"""["']([^"']+)["']\s*[,\]]?\s*#\s*review-by:\s*(\d{4})-(\d{2})-(\d{2})"""
)


class ConfigError(ValueError):
    """`.cargo/audit.toml` says something this wrapper will not act on."""


# --- waiver list --------------------------------------------------------------


def read_ignore_config(path: Path) -> Dict[str, datetime.date]:
    """Return `{advisory_id: review_by_date}` from `.cargo/audit.toml`.

    Section-aware on purpose: cargo-audit only honours `ignore` under
    `[advisories]`, so reading the first `ignore = [...]` anywhere in the file
    would let a key under some other table read as a waiver -- the list would
    grow without anyone waiving anything. `tomllib` is used when available
    (Python >= 3.11); the fallback tracks the current table itself so it makes
    the same distinction rather than a looser one.

    Every id must carry a `# review-by: YYYY-MM-DD` comment. A missing file or
    a missing key both mean "nothing is waived", which is the preferable state.
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")

    ids = _parse_ignore_ids(path, text)
    if not ids:
        return {}

    # tomllib cannot see comments, so review-by dates are read from the raw text.
    dates: Dict[str, datetime.date] = {}
    for ident, year, month, day in _REVIEW_BY_RE.findall(text):
        try:
            dates[ident] = datetime.date(int(year), int(month), int(day))
        except ValueError as exc:
            raise ConfigError(
                str(path) + ": " + ident + " has an invalid review-by date: " + str(exc)
            ) from exc

    missing = [i for i in ids if i not in dates]
    if missing:
        raise ConfigError(
            str(path)
            + ": every waived id needs a `# review-by: YYYY-MM-DD` comment on its\n"
            + "       own line. Missing for: "
            + ", ".join(missing)
            + "\n       Without a date a waiver never expires, and nobody looks again."
        )
    return {i: dates[i] for i in ids}


def _parse_ignore_ids(path: Path, text: str) -> List[str]:
    """Ids under `[advisories] ignore`, rejecting any other configuration key."""
    try:
        import tomllib  # Python >= 3.11
    except ImportError:
        tomllib = None  # type: ignore[assignment]

    if tomllib is not None:
        try:
            data = tomllib.loads(text)
        except Exception as exc:  # tomllib.TOMLDecodeError and friends
            raise ConfigError(str(path) + ": invalid TOML: " + str(exc)) from exc
        _reject_unsupported_keys(path, data)
        raw = (data.get("advisories") or {}).get("ignore") or []
        if not isinstance(raw, list):
            raise ConfigError(str(path) + ": [advisories] ignore must be an array")
        return [str(x) for x in raw]

    # --- fallback for Python < 3.11 (repo policy allows 3.9+) ----------------
    stripped = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    section = ""
    lines = stripped.splitlines()
    for index, line in enumerate(lines):
        header = _SECTION_RE.match(line)
        if header:
            section = header.group(1).strip()
            continue
        if section != "advisories":
            continue
        m = _IGNORE_BLOCK_RE.match("\n".join(lines[index:]))
        if m:
            body = m.group(1)
            found = _ID_RE.findall(body)
            if not found and body.strip():
                # A non-empty array we could not read must not become "nothing
                # is waived" -- that is exactly the silent failure this guards.
                raise ConfigError(
                    str(path) + ": could not read any id out of ignore = [" + body + "]"
                )
            return found
    return []


def _reject_unsupported_keys(path: Path, data: dict) -> None:
    """Only `[advisories] ignore` is honoured; anything else would be dropped.

    The sandboxed cargo-audit run sees no config at all, so `severity`,
    `informational_warnings`, `[output] deny`, `[yanked] enabled` and friends
    would have no effect here while still applying to someone running
    `cargo-audit` directly. Two different answers from one file is worse than
    refusing the file.
    """
    extra: List[str] = []
    for table, value in data.items():
        if table != "advisories":
            extra.append("[" + table + "]")
            continue
        if isinstance(value, dict):
            extra.extend(
                "[advisories] " + k for k in value.keys() if k != "ignore"
            )
    if extra:
        raise ConfigError(
            str(path)
            + ": only `[advisories] ignore` is supported here, but found: "
            + ", ".join(sorted(extra))
            + "\n       Other cargo-audit settings would be silently dropped by this\n"
            + "       wrapper's sandboxed run, so they are refused instead."
        )


# --- running cargo-audit ------------------------------------------------------


def run_cargo_audit(lockfile: Path) -> dict:
    """Run cargo-audit on a copy of `lockfile` with no configuration in scope.

    `CARGO_HOME` is redirected at the sandbox because cargo-audit reads
    `$CARGO_HOME/audit.toml` as well as `./.cargo/audit.toml` (measured
    2026-09-12: a user-level file silently suppressed both `quick-xml`
    findings). The advisory database is passed explicitly so redirecting
    `CARGO_HOME` does not force a fresh clone when one is already on disk.
    """
    exe = shutil.which("cargo-audit")
    if exe is None:
        raise RuntimeError(
            "cargo-audit not found on PATH. Install it with "
            "`cargo install cargo-audit --locked`."
        )
    real_cargo_home = Path(os.environ.get("CARGO_HOME") or (Path.home() / ".cargo"))
    database = real_cargo_home / "advisory-db"

    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        shutil.copyfile(lockfile, sandbox / "Cargo.lock")
        env = dict(os.environ)
        env["CARGO_HOME"] = str(sandbox)
        cmd = [exe, "audit", "--file", "Cargo.lock", "--json"]
        if database.is_dir():
            cmd += ["--db", str(database)]
        proc = subprocess.run(
            cmd,
            cwd=str(sandbox),
            env=env,
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

    # Prove the isolation worked rather than assuming it: if any waiver reached
    # the sandbox, the finding set below is already filtered and everything
    # after this point would be reasoning about the wrong data.
    leaked = (report.get("settings") or {}).get("ignore") or []
    if leaked:
        raise RuntimeError(
            "cargo-audit ran with a non-empty ignore list ("
            + ", ".join(str(x) for x in leaked)
            + "), so some advisories were filtered before this wrapper could see\n"
            "       them. Configuration leaked into the sandbox; refusing to report."
        )
    return report


def extract_findings(report: dict) -> Tuple[List[dict], Set[str], int, int, str]:
    """Return `(vulnerabilities, all_advisory_ids, crates, db_size, db_date)`.

    `all_advisory_ids` includes informational warnings (unmaintained / unsound /
    yanked). cargo-audit's own `ignore` applies to those too, so a waiver for
    one must not be reported as stale just because it is not a vulnerability.
    """
    vulns: List[dict] = []
    ids: Set[str] = set()
    for v in (report.get("vulnerabilities") or {}).get("list") or []:
        adv = v.get("advisory") or {}
        pkg = v.get("package") or {}
        patched = (v.get("versions") or {}).get("patched") or []
        ident = adv.get("id") or "(no id)"
        ids.add(ident)
        vulns.append(
            {
                "id": ident,
                "crate": pkg.get("name") or "?",
                "version": pkg.get("version") or "?",
                "title": (adv.get("title") or "").replace("\n", " "),
                "patched": ", ".join(patched) if patched else "(none published)",
            }
        )
    warnings = report.get("warnings") or {}
    if isinstance(warnings, dict):
        for items in warnings.values():
            for item in items or []:
                adv = (item or {}).get("advisory") or {}
                ident = adv.get("id")
                if ident:
                    ids.add(ident)
    crate_count = (report.get("lockfile") or {}).get("dependency-count") or 0
    database = report.get("database") or {}
    return (
        vulns,
        ids,
        crate_count,
        database.get("advisory-count") or 0,
        str(database.get("last-updated") or "unknown"),
    )


def summarise_warnings(report: dict) -> List[Tuple[str, int]]:
    warnings = report.get("warnings") or {}
    if not isinstance(warnings, dict):
        return []
    return sorted((kind, len(items or [])) for kind, items in warnings.items())


# --- evaluation ---------------------------------------------------------------


def evaluate(
    vulns: Sequence[dict],
    all_ids: Set[str],
    waivers: Dict[str, datetime.date],
    today: Optional[datetime.date] = None,
) -> Tuple[List[dict], List[dict], List[str], List[str]]:
    """Split into `(blocking, waived, stale_ids, expired_ids)`."""
    today = today or datetime.date.today()
    blocking = [v for v in vulns if v["id"] not in waivers]
    waived = [v for v in vulns if v["id"] in waivers]
    stale = sorted(i for i in waivers if i not in all_ids)
    expired = sorted(i for i, due in waivers.items() if i in all_ids and due < today)
    return blocking, waived, stale, expired


def report_text(
    lockfile: Path,
    config: Path,
    crate_count: int,
    db_count: int,
    db_date: str,
    blocking: Sequence[dict],
    waived: Sequence[dict],
    stale: Sequence[str],
    expired: Sequence[str],
    waivers: Dict[str, datetime.date],
    warning_counts: Sequence[Tuple[str, int]],
) -> Tuple[str, int]:
    out: List[str] = []
    out.append("lockfile      : " + str(lockfile))
    out.append("waiver config : " + str(config))
    out.append(
        "scanned       : "
        + str(crate_count)
        + " crate dependencies against "
        + str(db_count)
        + " advisories (db last updated "
        + db_date
        + ")"
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

    # Always print the waived list: cargo-audit's own output hides it.
    if waived:
        out.append("")
        out.append("WAIVED (listed in " + str(config) + " -- rationale lives there):")
        for v in waived:
            due = waivers.get(v["id"])
            out.append(
                "  - {id}  {crate} {version}  patched: {patched}".format(**v)
                + "  review-by: "
                + (due.isoformat() if due else "?")
            )
            out.append("      " + v["title"][:100])
    if expired:
        out.append("")
        out.append("EXPIRED WAIVER: the review-by date has passed:")
        for i in expired:
            out.append("  - " + i + "  (review-by " + waivers[i].isoformat() + ")")
        out.append(
            "  -> re-check whether it is fixable now. If it still is not, move the"
        )
        out.append(
            "     date forward in " + str(config) + " AND say why it is still safe."
        )
    if stale:
        out.append("")
        out.append("STALE WAIVER: these ids are waived but no longer reported:")
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
            out.append("  - {id}  {crate} {version}  patched: {patched}".format(**v))
            out.append("      " + v["title"][:100])
        out.append("")
        out.append(
            "  -> try `cargo update -p <crate>` from src-tauri/ first. If semver has no"
        )
        out.append(
            "     solution, add the id to " + str(config) + " WITH a rationale, the"
        )
        out.append("     dependency path, and a `# review-by: YYYY-MM-DD` comment.")
        out.append(
            "  -> NOTE: `cargo update -p <crate>` can also re-resolve unrelated edges."
        )
        out.append(
            "     Check `git diff` and keep the lockfile change to the crate you meant."
        )

    if blocking:
        code = EXIT_VULN
        verdict = (
            "NG: " + str(len(blocking)) + " vulnerability/vulnerabilities need action."
        )
    elif stale or expired:
        code = EXIT_STALE_IGNORE
        verdict = (
            "NG: "
            + str(len(stale))
            + " stale and "
            + str(len(expired))
            + " expired waiver(s)."
        )
    else:
        code = EXIT_OK
        verdict = (
            "OK: "
            + str(crate_count)
            + " crates scanned, 0 vulnerabilities outside the waiver list, "
            + str(len(waived))
            + " waived, 0 stale, 0 expired."
        )
    out.append("")
    out.append(verdict)
    return "\n".join(out), code


# --- self-test ----------------------------------------------------------------


def self_test() -> int:
    """Prove the split, the stale detection and the expiry are not no-ops."""
    failures: List[str] = []
    today = datetime.date(2026, 9, 12)
    future = datetime.date(2026, 12, 12)
    past = datetime.date(2026, 1, 1)

    def vuln(i: str) -> dict:
        return {"id": i, "crate": "c", "version": "1", "title": "t", "patched": "p"}

    # (1) nothing found, nothing waived -> clean
    if evaluate([], set(), {}, today) != ([], [], [], []):
        failures.append("(1) empty input must produce empty output")

    # (2) a finding not in the waiver list blocks
    b, w, s, e = evaluate([vuln("A")], {"A"}, {}, today)
    if len(b) != 1 or w or s or e:
        failures.append("(2) an unwaived finding must block")

    # (3) a waived finding is reported as waived, not dropped
    b, w, s, e = evaluate([vuln("A")], {"A"}, {"A": future}, today)
    if b or len(w) != 1 or s or e:
        failures.append("(3) a waived finding must still be reported as waived")

    # (4) a waiver that matches nothing is stale
    b, w, s, e = evaluate([], set(), {"A": future}, today)
    if b or w or s != ["A"] or e:
        failures.append("(4) a waiver matching nothing must be flagged stale")

    # (5) a waiver whose review-by has passed is expired, even while it applies
    b, w, s, e = evaluate([vuln("A")], {"A"}, {"A": past}, today)
    if b or len(w) != 1 or s or e != ["A"]:
        failures.append("(5) an expired waiver must be flagged")

    # (6) an informational-only advisory id still counts as "reported"
    #     (cargo-audit's ignore applies to warnings too, so waiving one must not
    #      read as stale just because it is not a vulnerability)
    b, w, s, e = evaluate([], {"WARN-1"}, {"WARN-1": future}, today)
    if b or w or s or e:
        failures.append("(6) waiving a warnings-only id must not be called stale")

    # (7) exit codes follow the verdicts
    cases = [
        ([], [], [], [], EXIT_OK),
        ([vuln("A")], [], [], [], EXIT_VULN),
        ([], [vuln("B")], [], [], EXIT_OK),
        ([], [], ["C"], [], EXIT_STALE_IGNORE),
        ([], [], [], ["D"], EXIT_STALE_IGNORE),
        ([vuln("A")], [], ["C"], ["D"], EXIT_VULN),  # a real finding outranks both
    ]
    for blocking, waived, stale, expired, want in cases:
        waivers = {i: future for i in list(stale) + list(expired)}
        waivers.update({v["id"]: future for v in waived})
        _, got = report_text(
            Path("l"), Path("c"), 1, 1, "d", blocking, waived, stale, expired, waivers, []
        )
        if got != want:
            failures.append(
                "(7) exit code for ({}, {}, {}, {}): want {}, got {}".format(
                    len(blocking), len(waived), len(stale), len(expired), want, got
                )
            )

    # (8) the waived ids must appear in the printed text (cargo-audit hides them)
    text, _ = report_text(
        Path("l"),
        Path("c"),
        1,
        1,
        "d",
        [],
        [vuln("RUSTSEC-WAIVED")],
        [],
        [],
        {"RUSTSEC-WAIVED": future},
        [],
    )
    if "RUSTSEC-WAIVED" not in text:
        failures.append("(8) a waived id must be printed")
    try:
        text.encode("cp932")
    except UnicodeEncodeError:
        failures.append("(8) the report must survive a cp932 console")

    # (9) config parsing
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "audit.toml"

        def write(body: str) -> None:
            p.write_text(body, encoding="utf-8")

        write(
            "# see RUSTSEC-9999-9999 for background\n"
            "[advisories]\n"
            'ignore = [\n    "RUSTSEC-2026-0194",  # review-by: 2026-12-12\n'
            '    "RUSTSEC-2026-0195",  # review-by: 2026-12-12\n]\n'
        )
        got = read_ignore_config(p)
        if sorted(got) != ["RUSTSEC-2026-0194", "RUSTSEC-2026-0195"]:
            failures.append("(9) ignore parsing wrong: " + repr(got))
        if got.get("RUSTSEC-2026-0194") != future:
            failures.append("(9) review-by date not read")

        # an `ignore` under another table must not be read as a waiver
        write(
            "[packages]\n"
            'ignore = ["NOT-A-WAIVER"]\n'
            "[advisories]\n"
            'ignore = ["REAL-1"]  # review-by: 2026-12-12\n'
        )
        try:
            read_ignore_config(p)
        except ConfigError:
            pass  # rejected because [packages] is an unsupported table
        else:
            failures.append("(9) a key outside [advisories] must be refused")

        # any other cargo-audit setting must be refused, not silently dropped
        write("[advisories]\nignore = []\nseverity = \"low\"\n")
        try:
            read_ignore_config(p)
        except ConfigError:
            pass
        else:
            failures.append("(9) [advisories] severity must be refused")

        # a waiver without review-by must be refused
        write('[advisories]\nignore = ["X-1"]\n')
        try:
            read_ignore_config(p)
        except ConfigError:
            pass
        else:
            failures.append("(9) a waiver without review-by must be refused")

        write("[advisories]\nignore = []\n")
        if read_ignore_config(p) != {}:
            failures.append("(9) an empty ignore list must mean 'nothing waived'")
        if read_ignore_config(Path(td) / "nope.toml") != {}:
            failures.append("(9) a missing config must mean 'nothing waived'")

    if failures:
        for f in failures:
            print("NG self-test: " + f, file=sys.stderr)
        return EXIT_USAGE
    print(
        "OK self-test: 9 groups (empty / unwaived blocks / waived reported / stale / "
        "expired / warnings ids / exit codes / printed + cp932 / config parsing)"
    )
    return EXIT_OK


# --- entry point --------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit src-tauri/Cargo.lock and validate the cargo-audit waiver list.",
    )
    parser.add_argument("--lockfile", default=str(DEFAULT_LOCKFILE))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
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
        waivers = read_ignore_config(config)
    except (OSError, ConfigError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return EXIT_USAGE

    try:
        report = run_cargo_audit(lockfile)
    except RuntimeError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return EXIT_TOOL

    vulns, all_ids, crate_count, db_count, db_date = extract_findings(report)
    if crate_count == 0 or db_count == 0:
        print(
            "ERROR: cargo-audit reported "
            + str(crate_count)
            + " scanned crates against "
            + str(db_count)
            + " advisories.\n"
            "       Treated as a failure: an empty scan, or an empty advisory\n"
            "       database, is indistinguishable from a broken invocation and must\n"
            "       not be read as 'nothing is vulnerable'.",
            file=sys.stderr,
        )
        return EXIT_TOOL

    blocking, waived, stale, expired = evaluate(vulns, all_ids, waivers)
    text, code = report_text(
        lockfile,
        config,
        crate_count,
        db_count,
        db_date,
        blocking,
        waived,
        stale,
        expired,
        waivers,
        summarise_warnings(report),
    )
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
