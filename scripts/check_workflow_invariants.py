#!/usr/bin/env python3
"""Check the invariants this repo has actually decided about its workflows.

Why this instead of a general workflow linter (F-9, 2026-09-13)
---------------------------------------------------------------
F-9 was raised as "there is no workflow syntax check". Measured before acting:

- **No syntax or expression error has ever broken anything here** -- every
  `.github/workflows/` commit in the last 40 is a semantic fix.
- The finding that prompted F-9 was a **false positive**: a reviewer read a
  diff whose `${{ secrets.GITHUB_TOKEN }}` had been redacted by
  `scripts/secrets-filter.sh` and called it a syntax error.
- Invalid YAML is already rejected by GitHub at push time.
- Adding `actionlint` means adding a third-party action or a downloaded
  binary, which grows exactly the surface F-8 was raised to shrink.

So a generic linter would buy little and cost the thing we are trying to
protect. What actually goes wrong here is different: **a decision gets made,
and then nothing checks that it still holds.** This file encodes the decisions
so that breaking one turns CI red:

1. **Every job has an effective `permissions`** (top-level or job-level).
   Decided in F-5; the failure mode is "someone adds a job and forgets", which
   is exactly how the four jobs that prompted F-5 came to exist.
2. **Third-party actions are pinned to a commit SHA.** Decided in F-8.
   `actions/*` is exempt on purpose (see the note in `ci.yml`), and so are
   in-repo `./...` actions.
3. **`supply-chain.yml` stays on hosted runners.** It must not gain access to
   the machine that holds the participant decryption key.
4. **Nothing is checked silently**: scanning zero workflows, or zero jobs, is
   reported as a failure rather than as "no violations".

Exit codes:
    0 = every invariant holds
    1 = at least one invariant is violated
    2 = nothing was scanned (the check itself is broken)
    3 = a workflow file could not be parsed
    4 = invalid arguments / I/O error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):  # pragma: no cover
        pass

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_NOTHING_SCANNED = 2
EXIT_PARSE = 3
EXIT_USAGE = 4

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# Owners exempt from SHA pinning, with the reason recorded in ci.yml.
FIRST_PARTY_PREFIX = "actions/"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# Workflows that must never run on a self-hosted runner.
HOSTED_ONLY = {"supply-chain.yml"}


class ParseError(RuntimeError):
    """A workflow file could not be read as YAML."""


def load_workflows(directory: Path) -> List[Tuple[str, dict]]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - PyYAML ships with the runner
        raise ParseError("PyYAML is required: " + str(exc)) from exc

    out: List[Tuple[str, dict]] = []
    for path in sorted(directory.glob("*.y*ml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ParseError(str(path) + ": " + str(exc)) from exc
        if not isinstance(data, dict):
            raise ParseError(str(path) + ": top level is not a mapping")
        out.append((path.name, data))
    return out


def _uses_ref(uses: str) -> Tuple[str, str]:
    """`"owner/repo@ref # comment"` -> `("owner/repo", "ref")`."""
    token = uses.split("#", 1)[0].strip()
    if "@" not in token:
        return token, ""
    name, _, ref = token.partition("@")
    return name, ref


def check(workflows: Sequence[Tuple[str, dict]]) -> Tuple[List[str], Dict[str, int]]:
    """Return `(violations, counters)`."""
    violations: List[str] = []
    counters = {"workflows": 0, "jobs": 0, "uses": 0, "third_party": 0}

    for name, data in workflows:
        counters["workflows"] += 1
        top_permissions = data.get("permissions")
        jobs = data.get("jobs") or {}
        if not isinstance(jobs, dict) or not jobs:
            violations.append(name + ": has no jobs")
            continue

        for job_name, job in jobs.items():
            counters["jobs"] += 1
            if not isinstance(job, dict):
                violations.append(name + " / " + job_name + ": job is not a mapping")
                continue

            # (1) effective permissions
            if job.get("permissions") is None and top_permissions is None:
                violations.append(
                    name + " / " + job_name + ": no effective `permissions`"
                    " (declare it on the job, or once at the top level)"
                )

            # (3) hosted-only workflows
            runs_on = str(job.get("runs-on", ""))
            if name in HOSTED_ONLY and "self-hosted" in runs_on:
                violations.append(
                    name + " / " + job_name + ": runs on a self-hosted runner."
                    " This workflow must stay hosted -- the self-hosted machine holds"
                    " the participant decryption key."
                )

            # (2) third-party actions pinned to a commit SHA
            for step in job.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                uses = step.get("uses")
                if not uses:
                    continue
                counters["uses"] += 1
                action, ref = _uses_ref(str(uses))
                if action.startswith("./") or action.startswith(FIRST_PARTY_PREFIX):
                    continue
                counters["third_party"] += 1
                if not SHA_RE.match(ref):
                    violations.append(
                        name + " / " + job_name + ": third-party action `" + action
                        + "` is pinned to `" + (ref or "(nothing)")
                        + "`, not a 40-character commit SHA."
                        " A tag or branch can be moved by whoever controls the upstream"
                        " account, and these run where the participant key lives."
                    )
    return violations, counters


def report(
    violations: Sequence[str], counters: Dict[str, int], stream=sys.stdout
) -> int:
    print(
        "scanned       : {workflows} workflow(s), {jobs} job(s), {uses} `uses:` step(s)"
        " ({third_party} third-party)".format(**counters),
        file=stream,
    )
    if counters["workflows"] == 0 or counters["jobs"] == 0:
        print(
            "\nNG: nothing was scanned. Treated as a failure: an empty scan is\n"
            "    indistinguishable from a broken check and must not read as"
            " 'no violations'.",
            file=stream,
        )
        return EXIT_NOTHING_SCANNED
    if violations:
        print("\nVIOLATIONS:", file=stream)
        for v in violations:
            print("  - " + v, file=stream)
        print(
            "\nNG: " + str(len(violations)) + " invariant violation(s).\n"
            "    These are decisions this repo already made -- see the notes in"
            " .github/workflows/ci.yml.\n"
            "    If a decision genuinely changed, change it there AND here, in the"
            " same commit.",
            file=stream,
        )
        return EXIT_VIOLATION
    print(
        "\nOK: {workflows} workflow(s) / {jobs} job(s) satisfy all invariants"
        " (permissions / third-party SHA pinning / hosted-only).".format(**counters),
        file=stream,
    )
    return EXIT_OK


# --- self-test ----------------------------------------------------------------


def self_test() -> int:
    """Prove each invariant actually fires, and that a clean input passes."""
    failures: List[str] = []
    sha = "a" * 40

    clean = [
        (
            "ci.yml",
            {
                "permissions": {"contents": "read"},
                "jobs": {
                    "a": {
                        "runs-on": ["self-hosted", "gse-mac"],
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {"uses": "dtolnay/rust-toolchain@" + sha + " # comment"},
                            {"uses": "./.github/actions/disk-guard"},
                            {"run": "echo hi"},
                        ],
                    },
                    "b": {"permissions": {"contents": "write"}, "steps": []},
                },
            },
        )
    ]
    v, c = check(clean)
    if v:
        failures.append("(1) a clean workflow must pass, got " + repr(v))
    if (c["workflows"], c["jobs"], c["uses"], c["third_party"]) != (1, 2, 3, 1):
        failures.append("(1) counters wrong: " + repr(c))

    def one_job(job, wf="ci.yml", top=None):
        data = {"jobs": {"j": job}}
        if top is not None:
            data["permissions"] = top
        return [(wf, data)]

    # (2) missing permissions
    v, _ = check(one_job({"runs-on": "ubuntu-latest", "steps": []}))
    if not any("permissions" in x for x in v):
        failures.append("(2) a job without permissions must be flagged")
    v, _ = check(one_job({"runs-on": "ubuntu-latest", "steps": []}, top={"contents": "read"}))
    if v:
        failures.append("(2) top-level permissions must satisfy the job")

    # (3) third-party pinned to a tag / branch / nothing
    for bad_ref in ("v2", "stable", "main", "v2.9.2", ""):
        step = {"uses": "Swatinem/rust-cache" + (("@" + bad_ref) if bad_ref else "")}
        v, _ = check(
            one_job({"permissions": {}, "runs-on": "ubuntu-latest", "steps": [step]})
        )
        if not any("third-party" in x for x in v):
            failures.append("(3) ref " + repr(bad_ref) + " must be flagged")
    # ...and a real SHA must pass, even with a trailing comment
    v, _ = check(
        one_job(
            {
                "permissions": {},
                "runs-on": "ubuntu-latest",
                "steps": [{"uses": "Swatinem/rust-cache@" + sha + " # v2.9.2"}],
            }
        )
    )
    if v:
        failures.append("(3) a SHA-pinned third-party action must pass: " + repr(v))
    # ...and first-party / local stay exempt
    for exempt in ("actions/checkout@v4", "./.github/actions/disk-guard"):
        v, _ = check(
            one_job(
                {
                    "permissions": {},
                    "runs-on": "ubuntu-latest",
                    "steps": [{"uses": exempt}],
                }
            )
        )
        if v:
            failures.append("(3) " + exempt + " must be exempt, got " + repr(v))

    # (4) hosted-only workflow on a self-hosted runner
    v, _ = check(
        one_job(
            {"permissions": {}, "runs-on": ["self-hosted", "gse-mac"], "steps": []},
            wf="supply-chain.yml",
        )
    )
    if not any("self-hosted" in x for x in v):
        failures.append("(4) supply-chain.yml on self-hosted must be flagged")
    v, _ = check(
        one_job(
            {"permissions": {}, "runs-on": ["self-hosted", "gse-mac"], "steps": []},
            wf="ci.yml",
        )
    )
    if v:
        failures.append("(4) ci.yml on self-hosted must be allowed")

    # (5) an empty scan must not read as "no violations"
    if report([], {"workflows": 0, "jobs": 0, "uses": 0, "third_party": 0},
              stream=_Sink()) != EXIT_NOTHING_SCANNED:
        failures.append("(5) zero workflows must exit 2")
    if report([], {"workflows": 1, "jobs": 0, "uses": 0, "third_party": 0},
              stream=_Sink()) != EXIT_NOTHING_SCANNED:
        failures.append("(5) zero jobs must exit 2")

    # (6) exit codes
    if report(["x"], {"workflows": 1, "jobs": 1, "uses": 0, "third_party": 0},
              stream=_Sink()) != EXIT_VIOLATION:
        failures.append("(6) a violation must exit 1")
    if report([], {"workflows": 1, "jobs": 1, "uses": 0, "third_party": 0},
              stream=_Sink()) != EXIT_OK:
        failures.append("(6) a clean run must exit 0")

    if failures:
        for f in failures:
            print("NG self-test: " + f, file=sys.stderr)
        return EXIT_USAGE
    print(
        "OK self-test: 6 groups (clean input + counters / permissions / third-party"
        " pinning + exemptions / hosted-only / empty scan / exit codes)"
    )
    return EXIT_OK


class _Sink:
    def write(self, *_a, **_k):
        return 0

    def flush(self):
        return None


# --- entry point --------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check invariants this repo decided about its GitHub workflows.",
    )
    parser.add_argument("--dir", default=str(WORKFLOW_DIR))
    parser.add_argument(
        "--self-test", action="store_true", help="run the built-in cases and exit"
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    directory = Path(args.dir)
    if not directory.is_dir():
        print("ERROR: not a directory: " + str(directory), file=sys.stderr)
        return EXIT_USAGE
    try:
        workflows = load_workflows(directory)
    except ParseError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return EXIT_PARSE

    violations, counters = check(workflows)
    return report(violations, counters)


if __name__ == "__main__":
    sys.exit(main())
