#!/usr/bin/env python3
"""Verify that the P1 pre-registration document and its frozen JSON agree.

The frozen JSON (`src-tauri/prereg/p1-episode.json`) is the SSOT for the
values; `gse-replay --features` embeds it with `include_str!`. The document
(`docs/preregistration-p1-episode.md`) is what a human reads. If the two
drift, the pre-registration is meaningless -- somebody reads one number and
the binary uses another.

This check is **strict** on the operational values (exact equality after
JSON-parsing each cell) and **structural** on the search space (same key set,
same explicit candidate lists, and the derived key declared as derived on
both sides).

Exit codes:
    0 = document and JSON agree
    1 = drift detected
    2 = document not found / unparsable
    3 = JSON not found / unparsable
    4 = invalid arguments / I/O error
    5 = --self-test found that the checker itself does not go red

Usage:
    python scripts/check_prereg_parity.py
    python scripts/check_prereg_parity.py --self-test
    python scripts/check_prereg_parity.py --doc <path> --json <path>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOC = REPO_ROOT / "docs" / "preregistration-p1-episode.md"
DEFAULT_JSON = REPO_ROOT / "src-tauri" / "prereg" / "p1-episode.json"

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_DOC_MISSING = 2
EXIT_JSON_MISSING = 3
EXIT_USAGE = 4
EXIT_SELFTEST_FAILED = 5

# Section anchors. The tables we read are the FIRST table after each anchor,
# and we stop at the next "###" so the sub-tables inside the section
# (e.g. "併せて出力に載せるもの") are never mistaken for the value table.
OPERATIONAL_ANCHOR = "## 1. 凍結する運用値"
SEARCH_ANCHOR = "### 2.1 探索空間"

DERIVED_MARK_DOC = "従属"
DERIVED_MARK_JSON = "derived:"

# The single message the self-test greps for. Deliberately distinctive so it
# cannot be produced for some other reason (see rule 5 of the review notes).
DRIFT_BANNER = "PREREG-PARITY-DRIFT"


def die(code: int, message: str) -> None:
    print(f"[check_prereg_parity] {message}", file=sys.stderr)
    sys.exit(code)


def section_lines(text: str, anchor: str) -> list[str]:
    """Return the lines from `anchor` up to (not including) the next heading
    at the same or shallower depth, or the next "###" heading."""
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.startswith(anchor))
    except StopIteration:
        return []
    out: list[str] = []
    for ln in lines[start + 1 :]:
        if ln.startswith("###") or ln.startswith("## "):
            break
        out.append(ln)
    return out


def parse_cell(cell: str) -> object:
    """Parse one table cell into a Python value.

    Strips markdown emphasis and backticks, then tries JSON. A cell that is
    not valid JSON comes back as the stripped string (so `nearest_rank` and
    `{30000}` are both handled by their own callers)."""
    s = cell.strip()
    s = s.strip("*").strip()
    s = s.strip("`").strip()
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return s


def parse_table(lines: list[str]) -> list[list[str]]:
    """Return the data rows of the first markdown table in `lines`."""
    rows: list[list[str]] = []
    seen_separator = False
    for ln in lines:
        stripped = ln.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [c for c in stripped.strip("|").split("|")]
        if not seen_separator:
            if all(set(c.strip()) <= set("-: ") and c.strip() for c in cells):
                seen_separator = True
            continue
        rows.append(cells)
    return rows


def read_operational_from_doc(text: str) -> dict[str, object]:
    lines = section_lines(text, OPERATIONAL_ANCHOR)
    if not lines:
        die(EXIT_DOC_MISSING, f"section not found in document: {OPERATIONAL_ANCHOR!r}")
    rows = parse_table(lines)
    if not rows:
        die(EXIT_DOC_MISSING, f"no table found under {OPERATIONAL_ANCHOR!r}")
    out: dict[str, object] = {}
    for cells in rows:
        if len(cells) < 2:
            continue
        key = str(parse_cell(cells[0]))
        if not re.fullmatch(r"[a-z0-9_]+", key):
            continue
        out[key] = parse_cell(cells[1])
    return out


def read_search_space_from_doc(text: str) -> dict[str, object]:
    lines = section_lines(text, SEARCH_ANCHOR)
    if not lines:
        die(EXIT_DOC_MISSING, f"section not found in document: {SEARCH_ANCHOR!r}")
    rows = parse_table(lines)
    if not rows:
        die(EXIT_DOC_MISSING, f"no table found under {SEARCH_ANCHOR!r}")
    out: dict[str, object] = {}
    for cells in rows:
        if len(cells) < 2:
            continue
        key = str(parse_cell(cells[0]))
        if not re.fullmatch(r"[a-z0-9_]+", key):
            continue
        raw = cells[1].strip()
        # An explicit candidate list wins over the derived marker. Matching on
        # the bare word 従属 anywhere in the cell is not safe: prose such as
        # "was 従属" would make an explicit list read as derived, and the check
        # would stay green while the document said something else entirely.
        # (Self-test mutation "doc: keep the derived marker but add a list"
        # is the positive control for exactly this.)
        m = re.search(r"\{([^{}]*)\}", raw)
        if m is None:
            if DERIVED_MARK_DOC in raw:
                out[key] = DERIVED_MARK_DOC
                continue
            out[key] = raw.strip("*").strip().strip("`").strip()
            continue
        inner = m.group(1).strip()
        if not inner:
            out[key] = []
            continue
        out[key] = [parse_cell(part) for part in inner.split(",")]
    return out


def compare(doc_ops, json_ops, doc_space, json_space) -> list[str]:
    problems: list[str] = []

    for key in sorted(set(doc_ops) | set(json_ops)):
        if key not in json_ops:
            problems.append(f"operational: {key!r} is in the document but not in the JSON")
        elif key not in doc_ops:
            problems.append(f"operational: {key!r} is in the JSON but not in the document")
        elif doc_ops[key] != json_ops[key]:
            problems.append(
                f"operational: {key!r} differs -- document={doc_ops[key]!r} json={json_ops[key]!r}"
            )

    for key in sorted(set(doc_space) | set(json_space)):
        if key not in json_space:
            problems.append(f"search_space: {key!r} is in the document but not in the JSON")
            continue
        if key not in doc_space:
            problems.append(f"search_space: {key!r} is in the JSON but not in the document")
            continue
        dv, jv = doc_space[key], json_space[key]
        if isinstance(jv, str):
            if not jv.startswith(DERIVED_MARK_JSON):
                problems.append(
                    f"search_space: {key!r} is a string in the JSON but does not start with "
                    f"{DERIVED_MARK_JSON!r}: {jv!r}"
                )
            elif dv != DERIVED_MARK_DOC:
                problems.append(
                    f"search_space: {key!r} is derived in the JSON but the document does not say "
                    f"{DERIVED_MARK_DOC!r}: {dv!r}"
                )
            continue
        if dv == DERIVED_MARK_DOC:
            problems.append(
                f"search_space: {key!r} is declared derived in the document but the JSON gives an "
                f"explicit list: {jv!r}"
            )
        elif dv != jv:
            problems.append(f"search_space: {key!r} differs -- document={dv!r} json={jv!r}")

    # The operational value must itself be inside the declared search space
    # (unless the space is derived): a pre-registration that searches a grid
    # not containing the value it froze is incoherent.
    for key, value in sorted(json_ops.items()):
        space = json_space.get(key)
        if isinstance(space, list) and value not in space:
            problems.append(
                f"coherence: operational {key}={value!r} is not inside its own search space {space!r}"
            )

    return problems


def run_check(doc_path: Path, json_path: Path) -> int:
    if not doc_path.is_file():
        die(EXIT_DOC_MISSING, f"document not found: {doc_path}")
    if not json_path.is_file():
        die(EXIT_JSON_MISSING, f"frozen JSON not found: {json_path}")

    text = doc_path.read_text(encoding="utf-8")
    try:
        frozen = json.loads(json_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        die(EXIT_JSON_MISSING, f"frozen JSON is not valid JSON: {exc}")

    json_ops = frozen.get("operational")
    json_space = frozen.get("search_space")
    if not isinstance(json_ops, dict):
        die(EXIT_JSON_MISSING, "frozen JSON has no object-valued 'operational'")
    if not isinstance(json_space, dict):
        die(EXIT_JSON_MISSING, "frozen JSON has no object-valued 'search_space'")

    doc_ops = read_operational_from_doc(text)
    doc_space = read_search_space_from_doc(text)

    problems = compare(doc_ops, json_ops, doc_space, json_space)
    if problems:
        print(f"{DRIFT_BANNER}: {len(problems)} problem(s)", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(
            "\nRepair: make docs/preregistration-p1-episode.md and "
            "src-tauri/prereg/p1-episode.json agree. The JSON is the SSOT.",
            file=sys.stderr,
        )
        return EXIT_DRIFT

    print(
        f"[check_prereg_parity] OK: {len(doc_ops)} operational value(s) and "
        f"{len(doc_space)} search-space entry(ies) agree"
    )
    return EXIT_OK


# --------------------------------------------------------------------------
# Self-test (positive control).
#
# A parity checker that cannot go red is worse than none: it reports green
# forever. The self-test therefore asserts BOTH branches are reachable --
# the real files pass, and each mutation fails. Every mutation also asserts
# that the text actually changed, so "the mutation silently did nothing" is
# not mistaken for "the checker caught it".
# --------------------------------------------------------------------------

MUTATIONS = [
    ("json: change an operational value", "json", '"w_ms": 30000', '"w_ms": 31000'),
    ("doc: change an operational value", "doc", "| `w_ms` | `30000` |", "| `w_ms` | `31000` |"),
    ("doc: drop an operational row", "doc", "| `q` | `0.99` |", "| ~~q~~ | `0.99` |"),
    (
        "json: add a key the document does not have",
        "json",
        '"net_diff_min": 1\n  },',
        '"net_diff_min": 1,\n    "bogus_key": 7\n  },',
    ),
    (
        "json: move the operational value outside its own search space",
        "json",
        '"q": [0.99, 0.995, 0.999]',
        '"q": [0.995, 0.999]',
    ),
    (
        "doc: turn a derived entry into an explicit list",
        "doc",
        "| `warmup_count` | **従属**",
        "| `warmup_count` | `{100}`",
    ),
    (
        "doc: keep the derived marker but add a list next to it",
        "doc",
        "| `warmup_count` | **従属**",
        "| `warmup_count` | **従属** `{100}`",
    ),
]


def self_test(doc_path: Path, json_path: Path) -> int:
    failures: list[str] = []

    baseline = run_check(doc_path, json_path)
    if baseline != EXIT_OK:
        failures.append(
            f"baseline: the real files do not pass (exit {baseline}); "
            "the OK branch is never taken, so the mutations prove nothing"
        )

    doc_src = doc_path.read_text(encoding="utf-8")
    json_src = json_path.read_text(encoding="utf-8")

    for name, target, needle, replacement in MUTATIONS:
        src = doc_src if target == "doc" else json_src
        if src.count(needle) != 1:
            failures.append(
                f"{name}: the anchor text occurs {src.count(needle)} time(s) in the source, "
                "expected exactly 1 -- the mutation cannot be applied unambiguously"
            )
            continue
        mutated = src.replace(needle, replacement)
        if mutated == src:
            failures.append(f"{name}: the mutation did not change the file")
            continue

        with tempfile.TemporaryDirectory() as tmp:
            tmp_doc = Path(tmp) / doc_path.name
            tmp_json = Path(tmp) / json_path.name
            tmp_doc.write_text(doc_src if target == "json" else mutated, encoding="utf-8")
            tmp_json.write_text(json_src if target == "doc" else mutated, encoding="utf-8")

            # ⚠️ The child prints Japanese key names in its drift messages. On
            # Windows its stdio defaults to the console code page (cp932), so
            # decoding as UTF-8 raises and `proc.stderr` comes back empty --
            # which would make the banner check below fail for a reason that
            # has nothing to do with the mutation. Force UTF-8 on both sides.
            env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--doc", str(tmp_doc), "--json", str(tmp_json)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            if proc.returncode != EXIT_DRIFT:
                failures.append(
                    f"{name}: expected exit {EXIT_DRIFT} (drift) but got {proc.returncode}"
                )
            elif DRIFT_BANNER not in (proc.stderr or ""):
                failures.append(
                    f"{name}: exited {EXIT_DRIFT} but did not print {DRIFT_BANNER} -- "
                    "it may have gone red for an unrelated reason"
                )
            else:
                print(f"[self-test] OK (went red): {name}")

    if failures:
        print("\n[self-test] FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return EXIT_SELFTEST_FAILED

    print(f"\n[self-test] OK: baseline green and all {len(MUTATIONS)} mutation(s) went red")
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="positive control: assert the real files pass AND each mutation makes the check go red",
    )
    args = parser.parse_args()

    if not shutil.which(sys.executable) and not Path(sys.executable).exists():
        die(EXIT_USAGE, "cannot locate the running python interpreter")

    if args.self_test:
        return self_test(args.doc, args.json)
    return run_check(args.doc, args.json)


if __name__ == "__main__":
    sys.exit(main())
