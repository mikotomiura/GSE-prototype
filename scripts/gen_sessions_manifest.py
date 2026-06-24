#!/usr/bin/env python3
"""Generate (or refresh) ``sessions.csv`` -- the phase manifest consumed by
``build_analysis_db.py`` (pilot-pipeline-runbook GAP②, decisions.md D-PP3).

``build_analysis_db.py`` buckets each session's metrics into a pre/post ``phase``
using ``<dataset>/sessions.csv`` with columns
``participant_id,session_id,os,phase``. Which session is pre vs post is a research
-design decision that cannot be auto-derived, so this helper does the mechanical
half: it walks the metrics tree and emits one row per session with an **empty
phase** for the researcher to fill in (``pre`` / ``post``).

Key contract (must match build_analysis_db.py exactly):
  * sessions live at ``<dataset>/metrics/P*/<os>/*.metrics.json``
  * ``session_id`` = filename minus the ``.metrics.json`` suffix
  * ``*.range*`` exports are excluded (HMM-accuracy variant without outcome fields)

Idempotency / safety (D-PP3): re-running **preserves** phase values already filled
in for existing (participant_id, session_id, os) rows -- it never clobbers the
researcher's manual pre/post assignments. New sessions are appended with empty
phase; rows whose metrics file has disappeared are dropped (with a notice).

Privacy: only P-ID / os / session-id (all content-free path components) are read;
the JSON bodies are never opened. Nothing is sent anywhere.

Exit codes:
    0 = OK (manifest written)
    2 = --dataset path not found
    3 = no metrics sessions found under metrics/
    4 = invalid arguments / I/O error

Usage:
    python scripts/gen_sessions_manifest.py --dataset C:/gse-dataset
    python scripts/gen_sessions_manifest.py --dataset <root> --out <root>/sessions.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_DATASET_MISSING = 2
EXIT_NO_DATA = 3
EXIT_USAGE = 4

_METRICS_SUFFIX = ".metrics.json"
_FIELDS = ("participant_id", "session_id", "os", "phase")
# build_analysis_db.py buckets on these phase strings; anything else becomes its own
# silent bucket in cross_section. Empty = "not yet assigned by the researcher".
_VALID_PHASES = ("", "pre", "post")


def _discover_sessions(metrics_root: Path) -> list[tuple[str, str, str]]:
    """Return sorted unique (participant_id, session_id, os) for every metrics file.

    Mirrors _collect_metrics_rows() in build_analysis_db.py: path-derived keys,
    ``.range`` excluded, session_id = filename without ``.metrics.json``."""
    found: set[tuple[str, str, str]] = set()
    if not metrics_root.is_dir():
        return []
    for p in metrics_root.glob("P*/*/*.metrics.json"):
        if "range" in p.name:
            continue
        rel = p.relative_to(metrics_root).parts  # (P###, <os>, <file>)
        if len(rel) != 3:
            continue
        participant_id, os_name = rel[0], rel[1]
        session_id = p.name[: -len(_METRICS_SUFFIX)]
        found.add((participant_id, session_id, os_name))
    return sorted(found)


def _load_existing_phases(out_path: Path) -> dict[tuple[str, str, str], str]:
    """Read existing (participant_id, session_id, os) -> phase from a prior manifest.

    Tolerates a missing file (returns empty). A malformed/partial row is skipped so
    a hand-edit typo never aborts regeneration."""
    phases: dict[tuple[str, str, str], str] = {}
    if not out_path.is_file():
        return phases
    with open(out_path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pid = (row.get("participant_id") or "").strip()
            sid = (row.get("session_id") or "").strip()
            os_name = (row.get("os") or "").strip()
            if not (pid and sid and os_name):
                continue
            phase = (row.get("phase") or "").strip()
            if phase not in _VALID_PHASES:
                # Preserve it (don't silently drop the researcher's edit) but warn: a
                # typo like "Pre"/"prev"/"pre " becomes a separate bucket downstream.
                print(
                    f"[gen_sessions_manifest] WARNING: unexpected phase '{phase}' for "
                    f"{pid}/{os_name}/{sid} (expected pre|post). It will be kept as-is "
                    f"but build_analysis_db buckets on it verbatim.",
                    file=sys.stderr,
                )
            phases[(pid, sid, os_name)] = phase
    return phases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate/refresh sessions.csv (phase manifest) for "
        "build_analysis_db.py by walking the gse-dataset metrics tree.",
    )
    parser.add_argument(
        "--dataset", required=True,
        help="Path to the gse-dataset repo root (contains metrics/).",
    )
    parser.add_argument(
        "--metrics-subdir", default="metrics",
        help="Subdir of --dataset holding metrics JSON (default: metrics).",
    )
    parser.add_argument(
        "--out", default=None,
        help="Output CSV path (default: <dataset>/sessions.csv).",
    )
    args = parser.parse_args(argv)

    dataset = Path(args.dataset)
    if not dataset.is_dir():
        print(f"[gen_sessions_manifest] ERROR: --dataset not found: {dataset}", file=sys.stderr)
        return EXIT_DATASET_MISSING

    metrics_root = dataset / args.metrics_subdir
    sessions = _discover_sessions(metrics_root)
    if not sessions:
        print(
            f"[gen_sessions_manifest] ERROR: no sessions found under "
            f"{metrics_root}/P*/<os>/*.metrics.json",
            file=sys.stderr,
        )
        return EXIT_NO_DATA

    out_path = Path(args.out) if args.out else (dataset / "sessions.csv")
    existing = _load_existing_phases(out_path)

    preserved = 0
    new_rows = 0
    rows: list[tuple[str, str, str, str]] = []
    for pid, sid, os_name in sessions:
        phase = existing.get((pid, sid, os_name), "")
        if (pid, sid, os_name) in existing:
            preserved += 1
        else:
            new_rows += 1
        rows.append((pid, sid, os_name, phase))

    dropped = sorted(set(existing) - set(sessions))

    try:
        if out_path.parent and not out_path.parent.exists():
            out_path.parent.mkdir(parents=True, exist_ok=True)
        # newline="" + LF lineterminator: deterministic, git-diff friendly.
        with open(out_path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(_FIELDS)
            writer.writerows(rows)
    except OSError as e:
        print(f"[gen_sessions_manifest] ERROR: cannot write {out_path}: {e}", file=sys.stderr)
        return EXIT_USAGE

    blank = sum(1 for *_keys, phase in rows if not phase)
    print(
        f"[gen_sessions_manifest] OK: {out_path} ({len(rows)} session(s); "
        f"{new_rows} new, {preserved} preserved). {blank} row(s) still need a pre/post phase."
    )
    if dropped:
        # keys are (participant_id, session_id, os); display in metrics-path order
        # P###/<os>/<session> so the researcher can locate the gone file directly.
        listing = ", ".join(
            f"{pid}/{os_name}/{sid}" for pid, sid, os_name in dropped
        )
        print(
            f"[gen_sessions_manifest] NOTE: dropped {len(dropped)} stale row(s) whose metrics "
            f"file is gone: {listing}"
        )
    if blank:
        print("[gen_sessions_manifest] -> open the CSV and set phase=pre|post for the blank rows.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
