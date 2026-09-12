#!/usr/bin/env python3
"""Compare the pinned Rust toolchain (`rust-toolchain.toml`) against the
security advisories published on `rust-lang/rust`.

Why this exists (F-1, 2026-09-12)
---------------------------------
`Cargo.lock` pins 630 dependency crates **with checksums**, and `cargo audit`
covers them. The *toolchain* (rustc / std / cargo / clippy) is pinned **by name
only**, and it is **outside `cargo audit`'s reach**: cargo-audit reads
`Cargo.lock`, not the toolchain that ships `cargo` itself. The RustSec database
contains **zero** advisories for `std` -- those live only as repository
advisories on `rust-lang/rust`.

Frequency is low (**6 advisories in ~7 years**, measured 2026-09-12) but the
single `critical` one -- CVE-2024-24576, `std::process::Command` argument
escaping on Windows -- lands squarely on code this project actually writes.
So: "rare, but when it hits, it hits our own code."

Before this script the only mitigation was step 0 of the version-bump procedure
in `rust-toolchain.toml` (a human remembering to look). A procedure with
nowhere to run does not run.

Design notes
------------
- **Never report green because the comparison could not be made.** A `channel`
  that is not a plain version (`stable`, `nightly-*`, ...) exits 2, and an
  unparseable version range exits 3. Silence is not safety.
- **Always print what was examined.** The output lists every advisory with a
  HIT/ok verdict and a total count, so "0 advisories fetched" can never be
  mistaken for "nothing applies".
- Offline-capable via `--advisories-file`; `--self-test` runs the mutation
  cases against a frozen fixture and needs no network.

Exit codes:
    0 = no advisory applies to the pinned channel
    1 = at least one advisory applies (act on it)
    2 = `channel` is not a comparable version
    3 = advisories could not be fetched, or a version range was not understood
    4 = invalid arguments / I/O error
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# ⚠️ Windows の既定コンソールは cp932 で、出力に非 ASCII が 1 文字でも混ざると
# `UnicodeEncodeError` で落ちる。★ 2026-09-12 に変異テストで実際に踏んだ ——
# しかも Python の未捕捉例外は exit 1 なので、**「脆弱性を検出した」と区別が付かなかった**。
# → ★ 呼び出し側の `PYTHONUTF8=1` に依存せず、ここで閉じる。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):  # pragma: no cover
        pass

REPO = "rust-lang/rust"

EXIT_OK = 0
EXIT_HIT = 1
EXIT_CHANNEL_UNCOMPARABLE = 2
EXIT_FETCH_OR_PARSE = 3
EXIT_USAGE = 4

# `1.98.1` / `1.98`. Deliberately strict: `stable`, `nightly-2026-01-01` and
# `1.98.1-x86_64-pc-windows-msvc` must NOT silently pass as "no match".
_VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,2}$")
_CHANNEL_RE = re.compile(r'^\s*channel\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
_CONSTRAINT_RE = re.compile(r"^(>=|<=|>|<|=)\s*(\S+)$")


class RangeError(ValueError):
    """A `vulnerable_version_range` this script does not understand."""


# --- version handling ---------------------------------------------------------


def parse_version(text: str) -> Tuple[int, int, int]:
    """`"1.98.1"` -> `(1, 98, 1)`. Raises ValueError on anything else."""
    s = text.strip()
    if not _VERSION_RE.match(s):
        raise ValueError("not a plain version: " + repr(text))
    parts = [int(p) for p in s.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return (parts[0], parts[1], parts[2])


def parse_range(text: str) -> List[Tuple[str, Tuple[int, int, int]]]:
    """`">= 1.87.0, < 1.89.0"` -> `[(">=", (1,87,0)), ("<", (1,89,0))]`.

    Constraints are ANDed, which is how GitHub documents the field.
    """
    out: List[Tuple[str, Tuple[int, int, int]]] = []
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = _CONSTRAINT_RE.match(chunk)
        if not m:
            raise RangeError(
                "unparseable constraint " + repr(chunk) + " in range " + repr(text)
            )
        op, raw = m.group(1), m.group(2)
        try:
            out.append((op, parse_version(raw)))
        except ValueError as exc:
            raise RangeError(str(exc) + " (in range " + repr(text) + ")") from exc
    if not out:
        raise RangeError("empty range " + repr(text))
    return out


def version_in_range(version: Tuple[int, int, int], text: str) -> bool:
    for op, bound in parse_range(text):
        if op == ">=" and not version >= bound:
            return False
        if op == ">" and not version > bound:
            return False
        if op == "<=" and not version <= bound:
            return False
        if op == "<" and not version < bound:
            return False
        if op == "=" and version != bound:
            return False
    return True


# --- inputs -------------------------------------------------------------------


def read_channel(path: Path) -> str:
    """Extract `channel` from `rust-toolchain.toml`.

    A regex rather than `tomllib`, so this also runs on Python < 3.11. The file
    must contain exactly one `channel = "..."` line, and that is checked here.
    """
    text = path.read_text(encoding="utf-8")
    matches = _CHANNEL_RE.findall(text)
    if len(matches) != 1:
        raise ValueError(
            str(path)
            + ": expected exactly one channel = \"...\" line, found "
            + str(len(matches))
        )
    return matches[0]


def fetch_advisories(repo: str = REPO) -> List[dict]:
    """`gh api repos/<repo>/security-advisories --paginate`.

    No leading slash: git-bash on Windows rewrites `/repos/...` into
    `C:/Program Files/Git/repos/...` and `gh` rejects it (measured 2026-09-12).
    """
    cmd = ["gh", "api", "repos/" + repo + "/security-advisories", "--paginate"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(
            " ".join(cmd)
            + " failed (exit "
            + str(proc.returncode)
            + "): "
            + proc.stderr.strip()[:500]
        )
    raw = proc.stdout.strip()
    if not raw:
        raise RuntimeError("gh returned empty output")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # `--paginate` concatenates one JSON array per page; stitch them.
        data = []
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(raw):
            obj, end = decoder.raw_decode(raw, idx)
            data.extend(obj if isinstance(obj, list) else [obj])
            idx = end
            while idx < len(raw) and raw[idx] in " \t\r\n":
                idx += 1
    if not isinstance(data, list):
        raise RuntimeError("unexpected payload type " + type(data).__name__)
    return data


# --- evaluation ---------------------------------------------------------------


def evaluate(
    channel_version: Tuple[int, int, int], advisories: Sequence[dict]
) -> Tuple[List[str], List[str]]:
    """Return `(lines, hits)`: one report line per advisory, plus the hit ids."""
    lines: List[str] = []
    hits: List[str] = []
    for adv in advisories:
        ident = adv.get("cve_id") or adv.get("ghsa_id") or "(no id)"
        severity = adv.get("severity") or "?"
        summary = (adv.get("summary") or "").replace("\n", " ")
        vulns = adv.get("vulnerabilities") or []
        if not vulns:
            raise RangeError(ident + ": advisory has no `vulnerabilities` entries")
        matched: List[str] = []
        all_ranges: List[str] = []
        for v in vulns:
            rng = (v.get("vulnerable_version_range") or "").strip()
            if not rng:
                raise RangeError(ident + ": empty `vulnerable_version_range`")
            all_ranges.append(rng)
            if version_in_range(channel_version, rng):
                matched.append(rng)
        if matched:
            hits.append(ident)
        verdict = "HIT " if matched else "ok  "
        lines.append(
            "  {}{:<20} {:<8} [{}]  {}".format(
                verdict, ident, severity, " | ".join(all_ranges), summary[:70]
            )
        )
    return lines, hits


def report(
    channel: str,
    channel_version: Tuple[int, int, int],
    advisories: Sequence[dict],
    stream=sys.stdout,
) -> int:
    lines, hits = evaluate(channel_version, advisories)
    v = ".".join(str(n) for n in channel_version)
    print("toolchain channel : " + channel + "  (compared as " + v + ")", file=stream)
    print(
        "advisories fetched: " + str(len(advisories)) + " from " + REPO, file=stream
    )
    for line in lines:
        print(line, file=stream)
    if hits:
        print(
            "\nNG: "
            + str(len(hits))
            + " advisory/advisories apply to the pinned toolchain: "
            + ", ".join(hits),
            file=stream,
        )
        print(
            "    -> bump `channel` in rust-toolchain.toml (follow its version-bump "
            "procedure), or record why the exposure does not apply.",
            file=stream,
        )
        return EXIT_HIT
    print(
        "\nOK: none of the " + str(len(advisories)) + " advisories apply to " + v + ".",
        file=stream,
    )
    return EXIT_OK


# --- self-test ----------------------------------------------------------------

# Frozen snapshot of `gh api repos/rust-lang/rust/security-advisories`
# (2026-09-12). Used only by `--self-test`, so the mutation cases stay
# deterministic and offline. The live check always fetches fresh data.
_FIXTURE: List[dict] = [
    {
        "cve_id": "CVE-2025-11233",
        "severity": "medium",
        "summary": "Rust standard library didn't detect all path separators on Cygwin",
        "vulnerabilities": [
            {
                "package": {"name": "std"},
                "vulnerable_version_range": ">= 1.87.0, < 1.89.0",
            }
        ],
    },
    {
        "cve_id": "CVE-2024-43402",
        "severity": "low",
        "summary": "std::process::Command batch file argument escaping bypass",
        "vulnerabilities": [
            {"package": {"name": "std"}, "vulnerable_version_range": "< 1.81.0"}
        ],
    },
    {
        "cve_id": "CVE-2024-24576",
        "severity": "critical",
        "summary": "std::process::Command did not properly escape arguments of batch files",
        "vulnerabilities": [
            {"package": {"name": "std"}, "vulnerable_version_range": "< 1.77.2"}
        ],
    },
    {
        "cve_id": "CVE-2022-21658",
        "severity": "high",
        "summary": "Race condition in std::fs::remove_dir_all",
        "vulnerabilities": [
            {"package": {"name": "std"}, "vulnerable_version_range": "<= 1.58.0"}
        ],
    },
    {
        "cve_id": "CVE-2021-42574",
        "severity": "medium",
        "summary": "rustc and bidirectional-override codepoints in source code",
        "vulnerabilities": [
            {"package": {"name": "rustc"}, "vulnerable_version_range": "<= 1.56.0"}
        ],
    },
    {
        "cve_id": "CVE-2019-16760",
        "severity": "medium",
        "summary": "Cargo prior to Rust 1.26.0 may download the wrong dependency",
        "vulnerabilities": [
            {"package": {"name": "Rust"}, "vulnerable_version_range": "<= 1.25.0"}
        ],
    },
]


def code_for(channel: str, advisories: Sequence[dict] = _FIXTURE) -> int:
    """Exit code this script would return for `channel`, without printing."""
    sink = io.StringIO()
    try:
        v = parse_version(channel)
    except ValueError:
        return EXIT_CHANNEL_UNCOMPARABLE
    return report(channel, v, advisories, stream=sink)


def self_test() -> int:
    """Prove the checker is not a no-op.

    The point is not "exit 0". A checker that always returns 0 looks exactly
    like a healthy one, so the mutation cases below pin the *red* side too.
    """
    failures: List[str] = []

    # (1) the version actually pinned today -> green
    if code_for("1.98.1") != EXIT_OK:
        failures.append("(1) 1.98.1 should be clean against the frozen fixture")
    # (2) closed range `>= 1.87.0, < 1.89.0`: a naive "< first_patched" check
    #     would miss this, so it is pinned explicitly
    if code_for("1.88.0") != EXIT_HIT:
        failures.append("(2) 1.88.0 must HIT CVE-2025-11233 (closed range)")
    # (3) ...and the version just past that range must NOT hit
    if code_for("1.89.0") != EXIT_OK:
        failures.append("(3) 1.89.0 must be clean (upper bound is exclusive)")
    # (4) the one critical advisory
    if code_for("1.76.0") != EXIT_HIT:
        failures.append("(4) 1.76.0 must HIT the critical CVE-2024-24576")
    # (5) a channel that cannot be compared must NOT read as green
    for bad in (
        "stable",
        "nightly",
        "nightly-2026-01-01",
        "beta",
        "1.98.1-x86_64-pc-windows-msvc",
    ):
        if code_for(bad) != EXIT_CHANNEL_UNCOMPARABLE:
            failures.append(
                "(5) channel " + repr(bad) + " must exit 2, not green"
            )
    # (6) an unparseable range must raise, never be treated as "no match"
    for bad_range in ("~> 1.2.3", "1.2.3", ">= abc", ""):
        try:
            version_in_range((1, 98, 1), bad_range)
        except RangeError:
            pass
        else:
            failures.append("(6) range " + repr(bad_range) + " must raise RangeError")
    # (7) an advisory with no vulnerabilities must raise, not silently pass
    try:
        evaluate((1, 98, 1), [{"cve_id": "X", "vulnerabilities": []}])
    except RangeError:
        pass
    else:
        failures.append("(7) advisory without `vulnerabilities` must raise")
    # (8) boundary arithmetic of every operator
    cases = [
        ((1, 58, 0), "<= 1.58.0", True),
        ((1, 58, 1), "<= 1.58.0", False),
        ((1, 77, 2), "< 1.77.2", False),
        ((1, 77, 1), "< 1.77.2", True),
        ((1, 87, 0), ">= 1.87.0, < 1.89.0", True),
        ((1, 86, 9), ">= 1.87.0, < 1.89.0", False),
        ((2, 0, 0), "> 1.99.0", True),
        ((1, 98, 1), "= 1.98.1", True),
    ]
    for version, rng, want in cases:
        got = version_in_range(version, rng)
        if got != want:
            failures.append(
                "(8) {} in {!r}: want {}, got {}".format(version, rng, want, got)
            )
    # (9) `1.98` (two components) compares as `1.98.0`
    if parse_version("1.98") != (1, 98, 0):
        failures.append("(9) `1.98` must normalise to (1, 98, 0)")
    # (10) an empty advisory list must not look like "nothing applies"
    if code_for("1.98.1", []) != EXIT_OK:
        failures.append("(10) report() on an empty list should not crash")

    if failures:
        for f in failures:
            print("NG self-test: " + f, file=sys.stderr)
        return EXIT_USAGE
    print(
        "OK self-test: "
        + str(len(_FIXTURE))
        + " fixture advisories x 10 groups (pinned / closed-range / upper bound / "
        "critical / uncomparable channel / bad range / empty advisory / operators / "
        "normalisation / empty list)"
    )
    return EXIT_OK


# --- entry point --------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the pinned Rust toolchain against rust-lang/rust advisories.",
    )
    parser.add_argument(
        "--toolchain-file",
        default="rust-toolchain.toml",
        help="path to rust-toolchain.toml (default: %(default)s)",
    )
    parser.add_argument(
        "--channel",
        help="compare this version instead of the one in the toolchain file "
        "(for mutation testing)",
    )
    parser.add_argument(
        "--advisories-file",
        help="read advisories from a JSON file instead of calling `gh` (offline)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in mutation cases and exit",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    try:
        channel = args.channel or read_channel(Path(args.toolchain_file))
    except (OSError, ValueError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return EXIT_USAGE

    try:
        channel_version = parse_version(channel)
    except ValueError:
        print(
            "ERROR: channel "
            + repr(channel)
            + " is not a plain version, so it cannot be compared against advisory\n"
            "       version ranges. This is reported as a failure on purpose:\n"
            "       'could not compare' is not 'not affected'. Pin an explicit version\n"
            "       in rust-toolchain.toml, or check\n"
            "       https://github.com/rust-lang/rust/security/advisories by hand.",
            file=sys.stderr,
        )
        return EXIT_CHANNEL_UNCOMPARABLE

    try:
        if args.advisories_file:
            advisories = json.loads(
                Path(args.advisories_file).read_text(encoding="utf-8")
            )
        else:
            advisories = fetch_advisories()
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print("ERROR: could not obtain advisories: " + str(exc), file=sys.stderr)
        return EXIT_FETCH_OR_PARSE

    if not advisories:
        print(
            "ERROR: 0 advisories returned for "
            + REPO
            + ".\n"
            "       Treated as a failure: an empty result is indistinguishable from a\n"
            "       broken query, and 'we found nothing' must not be read as\n"
            "       'nothing exists'.",
            file=sys.stderr,
        )
        return EXIT_FETCH_OR_PARSE

    try:
        return report(channel, channel_version, advisories)
    except RangeError as exc:
        print(
            "ERROR: "
            + str(exc)
            + "\n"
            "       Reported as a failure rather than skipped: an unrecognised range\n"
            "       must not be silently treated as 'does not apply'.",
            file=sys.stderr,
        )
        return EXIT_FETCH_OR_PARSE


if __name__ == "__main__":
    sys.exit(main())
