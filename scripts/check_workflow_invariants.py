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
# The exemption is for *release tags*, not for anything at all. `actions/x@main`
# is a branch, and a branch is exactly what F-8 was raised about
# (`dtolnay/rust-toolchain@stable` was a branch, not even a tag).
FIRST_PARTY_TAG_RE = re.compile(r"^v\d+(?:\.\d+){0,2}$")
# `docker://image@sha256:<64 hex>` is immutable too; saying "not a 40-character
# commit SHA" about a container digest would be actively misleading.
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

# Workflows that must never run on a self-hosted runner.
HOSTED_ONLY = {"supply-chain.yml"}
# A hosted runner is named `ubuntu-*` / `windows-*` / `macos-*`. Everything else
# -- a bare custom label, an expression, a runner group -- is NOT provably
# hosted. Listing self-hosted labels instead would be a denial list, and
# `runs-on: gse-win` (no `self-hosted` label at all) would walk straight past it.
HOSTED_LABEL_RE = re.compile(r"^(?:ubuntu|windows|macos)-[\w.]+$", re.IGNORECASE)
# Composite actions live outside .github/workflows and are exempt as `./...`,
# so their own `uses:` lines would otherwise be a blind spot.
ACTION_DIR = REPO_ROOT / ".github" / "actions"

# Jobs allowed to hold a write scope, and which one. F-5 was not about
# *declaring* permissions -- it was about not holding broad ones. With a
# top-level `permissions:` in place, a presence-only check can never fire again,
# so the breadth is what gets checked.
WRITE_ALLOWED: Dict[Tuple[str, str], set] = {
    # Creates the GitHub Release; see the note in ci.yml.
    ("ci.yml", "release"): {"contents"},
}


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


def permission_violations(workflow: str, job_name: str, perms: object) -> List[str]:
    """Invariant (1): an effective, and narrow, `permissions`."""
    where = workflow + " / " + job_name + ": "
    if perms is None:
        return [
            where + "no effective `permissions`"
            " (declare it on the job, or once at the top level)"
        ]
    if isinstance(perms, str):
        if perms == "read-all":
            return []
        return [
            where + "`permissions: " + perms + "` grants every scope."
            " Use `read-all`, or list only the scopes this job needs."
        ]
    if not isinstance(perms, dict):
        return [where + "`permissions` is neither a mapping nor a keyword"]
    allowed = WRITE_ALLOWED.get((workflow, job_name), set())
    return [
        where + "grants `" + str(k) + ": " + str(v) + "`, which is not in the"
        " allowlist for this job. If it is genuinely needed, add it to"
        " WRITE_ALLOWED with the reason."
        for k, v in sorted(perms.items())
        if str(v) == "write" and k not in allowed
    ]


def _is_provably_hosted(runs_on: object) -> bool:
    """True only when every label is a GitHub-hosted runner image.

    Deliberately an allow list. `runs-on` has four shapes -- a string, a list, a
    `{group:, labels:}` mapping, and an expression resolved at run time -- and
    only the first two can be decided here. Asking "does it say self-hosted?"
    lets `runs-on: gse-win` (a self-hosted label that never spells out
    `self-hosted`) and `runs-on: ${{ ... }}` through, which is exactly the shape
    `ci.yml`'s `check` job already uses.
    """
    labels = runs_on if isinstance(runs_on, list) else [runs_on]
    return bool(labels) and all(
        isinstance(x, str) and HOSTED_LABEL_RE.match(x.strip()) for x in labels
    )


def _uses_ref(uses: str) -> Tuple[str, str]:
    """`"owner/repo@ref # comment"` -> `("owner/repo", "ref")`.

    The comment stripping is for hand-written fixtures only: real YAML has
    already removed `# ...` before this sees the value (measured). The version
    comment that humans actually rely on is guarded from the raw file text in
    `TestRealRepository`, not here -- so do not read the comment branch as
    coverage of that.
    """
    token = uses.split("#", 1)[0].strip()
    if "@" not in token:
        return token, ""
    name, _, ref = token.partition("@")
    return name, ref


def load_composite_actions(directory: Path) -> List[Tuple[str, dict]]:
    """Read `.github/actions/*/action.yml`.

    These are referenced as `./...`, which invariant (2) exempts -- correctly,
    since they live in this repo. But *their* `uses:` lines are not in this repo
    and nothing else looks at them, so a third-party action added inside one
    would be completely invisible. `disk-guard` in particular runs
    unconditionally on the machine that holds the participant key.
    """
    if not directory.is_dir():
        return []
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ParseError("PyYAML is required: " + str(exc)) from exc
    out: List[Tuple[str, dict]] = []
    for path in sorted(directory.glob("*/action.y*ml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ParseError(str(path) + ": " + str(exc)) from exc
        if not isinstance(data, dict):
            raise ParseError(str(path) + ": top level is not a mapping")
        out.append((str(path.relative_to(REPO_ROOT)).replace("\\", "/"), data))
    return out


def check(
    workflows: Sequence[Tuple[str, dict]],
    composites: Sequence[Tuple[str, dict]] = (),
) -> Tuple[List[str], Dict[str, int]]:
    """Return `(violations, counters)`."""
    violations: List[str] = []
    counters = {
        "workflows": 0,
        "jobs": 0,
        "uses": 0,
        "third_party": 0,
        "composites": 0,
    }

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

            # (1) effective permissions -- present AND narrow
            effective = job.get("permissions")
            if effective is None:
                effective = top_permissions
            violations.extend(permission_violations(name, job_name, effective))

            # (3) hosted-only workflows
            if name in HOSTED_ONLY and not _is_provably_hosted(job.get("runs-on")):
                violations.append(
                    name + " / " + job_name + ": `runs-on: "
                    + str(job.get("runs-on"))
                    + "` is not provably a GitHub-hosted runner."
                    " This workflow must stay hosted -- the self-hosted machine holds"
                    " the participant decryption key. Spell out `ubuntu-*` /"
                    " `windows-*` / `macos-*`; anything undecidable is a violation"
                    " rather than assumed safe."
                )

            steps = job.get("steps")
            if steps is not None and not isinstance(steps, list):
                violations.append(
                    name + " / " + job_name + ": `steps` is "
                    + type(steps).__name__
                    + ", not a list"
                )
                steps = []

            # (2) third-party actions pinned to a commit SHA.
            #     A job can reference something in two places: each step's
            #     `uses:`, and the job's own `uses:` when it calls a reusable
            #     workflow. Checking only steps leaves the second wide open --
            #     a third-party reusable workflow is *more* privileged than an
            #     action, since it brings its own jobs.
            step_uses = [
                s.get("uses")
                for s in (steps or [])
                if isinstance(s, dict) and s.get("uses")
            ]
            if job.get("uses"):
                step_uses.append(job["uses"])
            for uses in step_uses:
                counters["uses"] += 1
                action, ref = _uses_ref(str(uses))
                if action.startswith("./"):
                    continue
                if action.startswith(FIRST_PARTY_PREFIX):
                    if not FIRST_PARTY_TAG_RE.match(ref):
                        violations.append(
                            name + " / " + job_name + ": `" + action
                            + "` is exempt from SHA pinning only on a release tag"
                            " (`vN[.N[.N]]`), but is pinned to `"
                            + (ref or "(nothing)")
                            + "`. A branch is exactly what F-8 was raised about."
                        )
                    continue
                counters["third_party"] += 1
                if action.startswith("docker://"):
                    if not DIGEST_RE.match(ref):
                        violations.append(
                            name + " / " + job_name + ": container `" + action
                            + "` is pinned to `" + (ref or "(nothing)")
                            + "`, not a `sha256:` digest."
                        )
                    continue
                if not SHA_RE.match(ref):
                    violations.append(
                        name + " / " + job_name + ": third-party reference `" + action
                        + "` is pinned to `" + (ref or "(nothing)")
                        + "`, not a 40-character commit SHA."
                        " A tag or branch can be moved by whoever controls the upstream"
                        " account, and these run where the participant key lives."
                    )

    # Composite actions: only invariant (2) applies (they have no jobs,
    # permissions or runners of their own).
    for name, data in composites:
        counters["composites"] += 1
        steps = ((data.get("runs") or {}).get("steps")) or []
        if not isinstance(steps, list):
            violations.append(name + ": `runs.steps` is not a list")
            continue
        for step in steps:
            if not isinstance(step, dict) or not step.get("uses"):
                continue
            counters["uses"] += 1
            action, ref = _uses_ref(str(step["uses"]))
            if action.startswith("./"):
                continue
            if action.startswith(FIRST_PARTY_PREFIX):
                if not FIRST_PARTY_TAG_RE.match(ref):
                    violations.append(
                        name + ": `" + action + "` is exempt only on a release tag,"
                        " but is pinned to `" + (ref or "(nothing)") + "`."
                    )
                continue
            counters["third_party"] += 1
            if not SHA_RE.match(ref):
                violations.append(
                    name + ": third-party reference `" + action + "` is pinned to `"
                    + (ref or "(nothing)")
                    + "`, not a 40-character commit SHA. This composite action runs"
                    " where the participant key lives."
                )

    return violations, counters


def missing_hosted_only(workflows: Sequence[Tuple[str, dict]]) -> List[str]:
    """Hosted-only rules whose workflow is not present.

    Renaming `supply-chain.yml` would otherwise disarm invariant (3) in silence.
    Kept out of `check()` on purpose: `check()` is also called with synthetic
    fixtures that legitimately contain one workflow, and folding this in would
    make every one of those fail for an unrelated reason.
    """
    present = {n for n, _ in workflows}
    return sorted(HOSTED_ONLY - present)


def report(
    violations: Sequence[str], counters: Dict[str, int], stream=sys.stdout
) -> int:
    counters = {"workflows": 0, "composites": 0, "jobs": 0, "uses": 0,
                "third_party": 0, **counters}
    print(
        "scanned       : {workflows} workflow(s), {composites} composite action(s),"
        " {jobs} job(s), {uses} `uses:` reference(s) ({third_party} third-party)"
        .format(**counters),
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
                    # ★ job 側の宣言が top-level を上書きする形も 1 つ入れておく
                    "b": {"permissions": {"contents": "read"}, "steps": []},
                },
            },
        )
    ]
    v, c = check(clean)
    if v:
        failures.append("(1) a clean workflow must pass, got " + repr(v))
    if (c["workflows"], c["jobs"], c["uses"], c["third_party"], c["composites"]) != (1, 2, 3, 1, 0):
        failures.append("(1) counters wrong: " + repr(c))

    def one_job(job, wf="ci.yml", top=None):
        data = {"jobs": {"j": job}}
        if top is not None:
            data["permissions"] = top
        return [(wf, data)]

    # (2) permissions: present AND narrow
    v, _ = check(one_job({"runs-on": "ubuntu-latest", "steps": []}))
    if not any("no effective" in x for x in v):
        failures.append("(2) a job without permissions must be flagged")
    v, _ = check(one_job({"runs-on": "ubuntu-latest", "steps": []}, top={"contents": "read"}))
    if v:
        failures.append("(2) top-level permissions must satisfy the job")
    # ⚠️ the part a presence-only check could never catch
    for perms, want in (
        ("read-all", False),
        ("write-all", True),
        ({"contents": "read"}, False),
        ({}, False),
        ({"contents": "write"}, True),
        ({"contents": "read", "id-token": "write"}, True),
        (["nope"], True),
    ):
        v, _ = check(one_job({"permissions": perms, "runs-on": "ubuntu-latest", "steps": []}))
        if bool(v) != want:
            failures.append("(2) permissions " + repr(perms) + " flagged=" + str(bool(v)))
    # the release job's documented write scope is allowed
    v, _ = check([("ci.yml", {"jobs": {"release": {
        "permissions": {"contents": "write"}, "runs-on": "ubuntu-latest", "steps": []}}})])
    if v:
        failures.append("(2) the allowlisted write scope must pass: " + repr(v))

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

    # (3b) a job-level `uses:` (reusable workflow) is checked too
    v, c = check([("x.yml", {"permissions": {}, "jobs": {"call": {
        "uses": "evil/repo/.github/workflows/w.yml@v1"}}})])
    if not any("third-party" in x for x in v):
        failures.append("(3b) a third-party reusable workflow must be flagged")
    if c["uses"] != 1 or c["third_party"] != 1:
        failures.append("(3b) a job-level uses must be counted: " + repr(c))
    v, _ = check([("x.yml", {"permissions": {}, "jobs": {"call": {
        "uses": "evil/repo/.github/workflows/w.yml@" + sha}}})])
    if v:
        failures.append("(3b) a SHA-pinned reusable workflow must pass: " + repr(v))
    v, _ = check([("x.yml", {"permissions": {}, "jobs": {"call": {
        "uses": "./.github/workflows/local.yml"}}})])
    if v:
        failures.append("(3b) a local reusable workflow must be exempt: " + repr(v))

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

    # (3c) `actions/*` is exempt on a release tag only -- a branch is not
    for ref, want_flag in (("v4", False), ("v4.1.2", False), ("main", True),
                           ("master", True), ("attacker", True), ("", True)):
        step = {"uses": "actions/checkout" + (("@" + ref) if ref else "")}
        v, _ = check(one_job({"permissions": {}, "runs-on": "x", "steps": [step]}))
        if bool(v) != want_flag:
            failures.append("(3c) actions/checkout@" + repr(ref) + " flagged=" + str(bool(v)))

    # (3d) composite actions are scanned (they are exempt as `./`, so their own
    #      `uses:` would otherwise be invisible)
    comp = [("a/action.yml", {"runs": {"steps": [{"uses": "attacker/pwn@main"}]}})]
    v, c = check([], comp)
    if not any("third-party" in x for x in v):
        failures.append("(3d) a third-party action inside a composite must be flagged")
    if c["composites"] != 1 or c["uses"] != 1:
        failures.append("(3d) composite counters wrong: " + repr(c))
    v, _ = check([], [("a/action.yml", {"runs": {"steps": [{"uses": "attacker/pwn@" + sha}]}})])
    if v:
        failures.append("(3d) a SHA-pinned action inside a composite must pass")

    # (3e) a container reference is pinned by digest, not by commit SHA
    for ref, want in (("sha256:" + "b" * 64, False), ("latest", True), ("3.18", True)):
        step = {"uses": "docker://alpine@" + ref if ref.startswith("sha256:")
                else "docker://alpine:" + ref}
        v, _ = check(one_job({"permissions": {}, "runs-on": "ubuntu-latest", "steps": [step]}))
        if bool(v) != want:
            failures.append("(3e) docker ref " + repr(ref) + " flagged=" + str(bool(v)))

    # (4b) runs-on shapes that cannot be decided statically are violations
    for runs_on, want in (
        ("gse-win", True),                       # a custom label alone still reaches it
        (["self-hosted", "gse-mac"], True),
        ("${{ matrix.os }}", True),              # undecidable
        ({"group": "gse-group"}, True),          # undecidable
        ({"labels": ["gse-mac"]}, True),
        ("ubuntu-latest", False),
        (["ubuntu-latest"], False),
        ("ubuntu-24.04", False),
        ("macos-15", False),
        ("my-custom-runner", True),   # ⚠️ 未知ラベルは hosted と証明できない
        ([], True),
    ):
        v, _ = check(one_job({"permissions": {}, "runs-on": runs_on, "steps": []},
                             wf="supply-chain.yml"))
        if bool(v) != want:
            failures.append("(4b) runs-on " + repr(runs_on) + " flagged=" + str(bool(v)))

    # (4c) renaming a hosted-only workflow must not silently disarm the rule
    if missing_hosted_only([("ci.yml", {})]) != ["supply-chain.yml"]:
        failures.append("(4c) a renamed hosted-only workflow must be detected")
    if missing_hosted_only([("ci.yml", {}), ("supply-chain.yml", {})]) != []:
        failures.append("(4c) a present hosted-only workflow must not be reported")

    # (4d) a non-list `steps` must not be skipped silently
    v, _ = check(one_job({"permissions": {}, "runs-on": "x", "steps": "oops"}))
    if not any("not a list" in x for x in v):
        failures.append("(4d) a malformed `steps` must be flagged")

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
        "OK self-test: 13 groups (clean input + counters / permissions / third-party"
        " pinning / reusable workflows / first-party tag-only exemption / composite"
        " actions / hosted-only runner shapes / renamed hosted-only workflow /"
        " malformed steps / container digests / empty scan / exit codes)"
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

    try:
        composites = load_composite_actions(ACTION_DIR)
    except ParseError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return EXIT_PARSE

    violations, counters = check(workflows, composites)

    # ⚠️ Only meaningful against the real directory: renaming a hosted-only
    # workflow would otherwise retire invariant (3) without a word.
    if directory.resolve() == WORKFLOW_DIR.resolve():
        for name in missing_hosted_only(workflows):
            violations.append(
                "HOSTED_ONLY names `" + name + "`, which does not exist."
                " Either it was renamed (update HOSTED_ONLY in the same commit) or"
                " the rule stopped protecting anything."
            )
    return report(violations, counters)


if __name__ == "__main__":
    sys.exit(main())
