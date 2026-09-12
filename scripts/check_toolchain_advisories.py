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
import contextlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import tempfile
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


def parse_pages(raw: str) -> List[dict]:
    """Parse one or more concatenated JSON arrays into a single list.

    The REST API returns one array per page. `gh api --paginate` concatenates
    them (`[...][...]`), so a single `json.loads` succeeds only when there
    happens to be exactly one page -- a silent single-page assumption. This
    decodes repeatedly instead, which handles both shapes the same way.
    """
    raw = raw.strip()
    if not raw:
        raise RuntimeError("empty response body")
    out: List[dict] = []
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(raw):
        obj, end = decoder.raw_decode(raw, idx)
        if isinstance(obj, list):
            out.extend(obj)
        elif isinstance(obj, dict):
            out.append(obj)
        else:
            raise RuntimeError("unexpected payload type " + type(obj).__name__)
        idx = end
        while idx < len(raw) and raw[idx] in " \t\r\n":
            idx += 1
    return out


def _next_link(link_header: Optional[str]) -> Optional[str]:
    """Extract the `rel="next"` URL from a RFC 5988 `Link` header."""
    if not link_header:
        return None
    for part in link_header.split(","):
        segments = part.split(";")
        if len(segments) < 2:
            continue
        url = segments[0].strip()
        if not (url.startswith("<") and url.endswith(">")):
            continue
        for attr in segments[1:]:
            if attr.strip().replace(" ", "") in ('rel="next"', "rel=next"):
                return url[1:-1]
    return None


def fetch_advisories(repo: str = REPO, token: Optional[str] = None) -> List[dict]:
    """Fetch `repos/<repo>/security-advisories` over plain HTTPS.

    Deliberately **not** shelling out to `gh`:

    - `gh` is an extra dependency, and on a fork pull request the repository
      secrets are not provided, so a `gh`-based step would fail for a reason
      that has nothing to do with security.
    - Measured 2026-09-12: this endpoint answers **HTTP 200 with all 6
      advisories unauthenticated**, so a token is only needed to lift the
      60-requests-per-hour per-IP limit (which matters on shared CI runners).
    - It also sidesteps a real trap: git-bash on Windows rewrites a leading
      `/repos/...` argument into `C:/Program Files/Git/repos/...`, and `gh`
      then rejects it (measured; this is why the old manual procedure did not
      run on the Windows machine).

    `token` defaults to `$GH_TOKEN` / `$GITHUB_TOKEN` when either is set.
    """
    if token is None:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "gse-prototype-supply-chain-check",
    }
    if token:
        headers["Authorization"] = "Bearer " + token

    url = "https://api.github.com/repos/" + repo + "/security-advisories?per_page=100"
    out: List[dict] = []
    seen = 0
    while url:
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                link = response.headers.get("Link")
        except urllib.error.HTTPError as exc:  # pragma: no cover - network
            raise RuntimeError(
                "GET " + url + " -> HTTP " + str(exc.code) + " " + str(exc.reason)
            ) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network
            raise RuntimeError("GET " + url + " failed: " + str(exc.reason)) from exc
        out.extend(parse_pages(body))
        seen += 1
        if seen > 20:  # pragma: no cover - defensive
            raise RuntimeError("refusing to follow more than 20 pages")
        url = _next_link(link)
    return out


# --- evaluation ---------------------------------------------------------------


def coerce_advisories(data: object) -> List[dict]:
    """Accept only a list of advisory objects.

    `--advisories-file` can be handed anything -- an error payload such as
    `{"message": "Not Found"}` used to reach `evaluate()` and die with an
    uncaught `AttributeError`, which exits 1: **the same code as "an advisory
    applies"**. That is precisely the confusion this script exists to prevent,
    so the shape is checked before it is used.
    """
    if not isinstance(data, list):
        raise RangeError(
            "expected a JSON array of advisories, got " + type(data).__name__
        )
    for item in data:
        if not isinstance(item, dict):
            raise RangeError(
                "advisory entries must be objects, found " + type(item).__name__
            )
    return data


def evaluate(
    channel_version: Tuple[int, int, int], advisories: Sequence[dict]
) -> Tuple[List[str], List[str]]:
    """Return `(lines, hits)`: one report line per advisory, plus the hit ids."""
    lines: List[str] = []
    hits: List[str] = []
    for adv in advisories:
        # A withdrawn advisory is one GitHub has retracted; treating it as a hit
        # would be a false red that nobody can act on.
        if adv.get("withdrawn_at"):
            lines.append(
                "  wdrw"
                + (adv.get("cve_id") or adv.get("ghsa_id") or "(no id)").ljust(21)
                + "withdrawn by the publisher on "
                + str(adv.get("withdrawn_at"))
            )
            continue
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
        packages = sorted(
            {
                str((v.get("package") or {}).get("name") or "?")
                for v in vulns
            }
        )
        lines.append(
            "  {}{:<20} {:<8} {:<6} [{}]  {}".format(
                verdict,
                ident,
                severity,
                ",".join(packages)[:6],
                " | ".join(all_ranges),
                summary[:60],
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
    # (10) an empty advisory list must not read as "nothing applies".
    #      The guard lives in main(), not report(), so pin main() itself here --
    #      otherwise this case would quietly certify the wrong layer.
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td) / "empty.json"
        empty.write_text("[]", encoding="utf-8")
        # Swallow the expected error text: an "ERROR:" line inside a passing
        # self-test reads as a failure to anyone skimming the CI log.
        with contextlib.redirect_stderr(io.StringIO()):
            code = main(["--channel", "1.98.1", "--advisories-file", str(empty)])
        if code != EXIT_FETCH_OR_PARSE:
            failures.append("(10) an empty advisory list must exit 3, not 0")

    # (11) concatenated pages (what `--paginate` style output looks like)
    if len(parse_pages('[{"a":1}] [{"b":2},{"c":3}]')) != 3:
        failures.append("(11) concatenated JSON arrays must all be parsed")
    if len(parse_pages('[{"a":1}]')) != 1:
        failures.append("(11) a single page must still parse")
    for bad_body in ("", "   "):
        try:
            parse_pages(bad_body)
        except RuntimeError:
            pass
        else:
            failures.append("(11) an empty body must raise, not yield []")

    # (13) a non-list payload must not reach evaluate() (it would exit 1 = HIT)
    for bad_payload in ({"message": "Not Found"}, "nope", 3, None):
        try:
            coerce_advisories(bad_payload)
        except RangeError:
            pass
        else:
            failures.append("(13) " + repr(bad_payload) + " must be refused")
    if coerce_advisories([]) != []:
        failures.append("(13) an empty list is a valid shape (main() guards emptiness)")
    try:
        coerce_advisories(["not-an-object"])
    except RangeError:
        pass
    else:
        failures.append("(13) a list of non-objects must be refused")

    # (14) a withdrawn advisory must never be reported as a hit
    withdrawn = [
        {
            "cve_id": "CVE-2099-0001",
            "severity": "critical",
            "summary": "retracted",
            "withdrawn_at": "2026-01-01T00:00:00Z",
            "vulnerabilities": [{"vulnerable_version_range": "< 99.0.0"}],
        }
    ]
    if code_for("1.98.1", withdrawn) != EXIT_OK:
        failures.append("(14) a withdrawn advisory must not count as a hit")

    # (12) Link header parsing (pagination must not stop after page 1 silently)
    nxt = _next_link('<https://api.github.com/x?page=2>; rel="next", <https://x?page=9>; rel="last"')
    if nxt != "https://api.github.com/x?page=2":
        failures.append("(12) rel=next must be extracted, got " + repr(nxt))
    if _next_link('<https://x?page=9>; rel="last"') is not None:
        failures.append("(12) a header without rel=next must yield None")
    if _next_link(None) is not None:
        failures.append("(12) a missing Link header must yield None")

    if failures:
        for f in failures:
            print("NG self-test: " + f, file=sys.stderr)
        return EXIT_USAGE
    print(
        "OK self-test: "
        + str(len(_FIXTURE))
        + " fixture advisories x 14 groups (pinned / closed-range / upper bound / "
        "critical / uncomparable channel / bad range / empty advisory / operators / "
        "normalisation / empty list / page concatenation / Link header / payload shape / withdrawn)"
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
            advisories = coerce_advisories(
                json.loads(Path(args.advisories_file).read_text(encoding="utf-8"))
            )
        else:
            advisories = coerce_advisories(fetch_advisories())
    except (OSError, RuntimeError, RangeError, json.JSONDecodeError) as exc:
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
