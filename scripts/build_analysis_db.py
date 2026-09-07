#!/usr/bin/env python3
"""Build a disposable DuckDB analysis database joining the three GSE validation
data streams on ``participant_id`` (GSE issue #6 / decisions.md **D5**).

The three streams (D5):

  (3) metrics  -- ``<dataset>/metrics/P*/<os>/*.metrics.json`` : aggregated,
                  content-free SessionMetrics from ``gse-replay --metrics --json``.
                  Holds (a) AI-dependence and (b) self-resolution outcome metrics
                  under the nested ``outcome`` object. participant_id / os /
                  session_id are NOT in the JSON body -- they come from the
                  **file path** and are derived here.
  (2) survey   -- ``<dataset>/survey/*.csv`` : low/medium-sensitivity Google-Form
                  data keyed by ``participant_id`` + ``phase`` (pre/post). Holds
                  (c) GSE self-efficacy (``gse_total`` 10-40), NASA-TLX, demographics.
  manifest     -- ``<dataset>/sessions.csv`` (optional) : maps each session to a
                  ``phase`` (pre/post) so session metrics can be bucketed for the
                  pre/post cross-section. Sessions absent from the manifest get
                  ``phase = 'unknown'``.

Design (decisions.md D5): files are the source of truth; DuckDB is only an
analysis layer. ``analysis.db`` is **disposable** -- delete it and re-run to
regenerate deterministically. We never load raw NDJSON, real names, or the
real-name<->P-ID enrolment map; only P-ID, phase, os, and numeric metrics flow
into the DB (data-privacy Skill).

The final ``cross_section`` view is at (participant_id, phase) grain, built with a
FULL OUTER JOIN so a missing stream surfaces as NULL columns plus explicit
``has_metrics`` / ``has_survey`` flags -- this keeps "no data" distinct from a
genuine measured zero (e.g. ``external_paste_count = 0``), matching #19's
outcome=None philosophy.

Exit codes:
    0 = OK
    2 = --dataset path not found
    3 = no data found in any stream (nothing to join)
    4 = invalid arguments / I/O error
    5 = duckdb not installed (run: pip install -r scripts/requirements-dev.txt)
    6 = privacy guard tripped (forbidden PII column in a survey CSV)

Usage:
    pip install -r scripts/requirements-dev.txt
    python scripts/build_analysis_db.py --dataset C:/gse-dataset --out analysis.db
    python scripts/build_analysis_db.py --dataset <root> --out analysis.db \
        --export-dir out/ --format both
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_DATASET_MISSING = 2
EXIT_NO_DATA = 3
EXIT_USAGE = 4
EXIT_NO_DUCKDB = 5
EXIT_PRIVACY = 6


class _SurveyDuplicateError(Exception):
    """Raised when survey rows are not unique on (participant_id, phase)."""

# data-privacy: a survey CSV must never carry real-world identifiers. The
# real-name<->P-ID map lives outside the repo (decisions.md D1). If any of these
# tokens appears *as a substring* of a column name (case-insensitive) we refuse
# to build rather than let PII leak into analysis.db.
#
# Substring (not exact) matching is deliberate: the real Google-Form column names
# are not yet frozen (PreReg) and the forms are Japanese, so PII can arrive as
# `email_address`, `お名前`, `氏名（フリガナ）`, `連絡先メール` etc. A blacklist can
# never be complete, so this is an early-detection net, not the sole defence --
# fail-closed renaming by the researcher is the intended response. English tokens
# are matched lowercased; Japanese tokens are matched as-is.
FORBIDDEN_SURVEY_SUBSTRINGS = (
    # English
    "name",  # name, full_name, surname, username, first/last_name
    "mail",  # email, e-mail, mail, email_address, gmail
    "phone",
    "tel",
    "address",
    "zip",
    "postal",
    "dob",
    "birth",  # birthdate, birthday, date_of_birth
    "ssn",
    "student_id",
    "employee_id",
    "ip_addr",
    "furigana",
    "kana",
    # Japanese
    "氏名",
    "名前",
    "お名前",
    "ふりがな",
    "フリガナ",
    "メール",
    "電話",
    "連絡先",
    "住所",
    "生年月日",
    "誕生日",
    "所属",
)

# Numeric outcome metric fields (decisions.md D7 / metrics.rs OutcomeMetrics) that
# we lift out of the nested ``outcome`` struct. Count-like -> SUM, ratio-like ->
# AVG when aggregating per (participant_id, phase).
OUTCOME_SUM_FIELDS = (
    "external_paste_count",
    "external_paste_chars_total",
    "excluded_paste_count",
    "manual_insert_chars",
    "stuck_episode_count",
    "pflow_exit_episode_count",
    # ADR-024 primary outcome (receipt_free_resumption): event counts. These are
    # the parts that CAN be pooled correctly across sessions by SUM.
    "rfr_event_count",
    "rfr_source_episode_count",
    "rfr_receipt_count",
    "rfr_next_away_candidate_count",
    "rfr_censored_count",
    # Diagnostics: read these BEFORE the CIF values.
    #   degenerate  = resumptions with zero follow-up time (excluded from the CIF)
    #   n_at_risk_* = events still under follow-up at the horizon; 0 means the
    #                 per-session CIF value is an extrapolation, not an estimate.
    "rfr_degenerate_count",
    "rfr_n_at_risk_at_5min",
    "rfr_n_at_risk_at_10min",
)
OUTCOME_AVG_FIELDS = (
    "manual_contribution_ratio",
    "pflow_exit_manual_gain_rate",
    "large_paste_rate",
    "paste_after_stuck_rate",
    "pflow_exit_without_receipt",
    "paste_count_per_hour",
    # ADR-024 primary outcome: per-session CIF-derived values.
    # WARNING: averaging per-session CIF estimates is NOT the same as pooling the
    # underlying events. For a proper competing-risks estimate, pool the rfr_*
    # counts (or re-run gse-replay over the pooled sessions) instead of reading
    # the _avg columns. The _avg columns are carried for eyeballing only.
    "rfr_receipt_free_at_5min",
    "rfr_receipt_free_at_10min",
)

# Fields nested one level deeper, under outcome["receipt_free_resumption"].
# Column name = "rfr_" + nested key (see _lift_outcome_field).
_RFR_PREFIX = "rfr_"
_RFR_KEY = "receipt_free_resumption"

# Field names emitted by gse-replay BEFORE the ADR-024 rename. Kept so that
# metrics.json produced by older builds still populate the columns instead of
# silently landing as all-NULL (this file is not covered by the schema drift
# check, so a silent break would not be caught by CI).
LEGACY_FIELD_ALIASES = {
    "pflow_exit_without_receipt": "self_recovery_without_paste",
    "pflow_exit_manual_gain_rate": "productive_manual_recovery_rate",
    "pflow_exit_episode_count": "recovered_episode_count",
}


def _lift_outcome_field(outcome: dict, name: str):
    """Read one column's value out of the nested ``outcome`` struct.

    Handles three cases: fields nested under ``receipt_free_resumption``
    (``rfr_`` prefix), fields renamed by ADR-024 (legacy alias fallback), and
    plain top-level outcome fields. Missing -> None, matching the outcome=None
    philosophy documented at the top of this module.
    """
    if name.startswith(_RFR_PREFIX):
        nested = outcome.get(_RFR_KEY) or {}
        return nested.get(name[len(_RFR_PREFIX):]) if isinstance(nested, dict) else None
    value = outcome.get(name)
    # NOTE: `is None` deliberately treats "key absent" and "value is JSON null"
    # the same, so a new-schema file that carries an explicit null still falls
    # back to the legacy key. No file currently holds both spellings, so this
    # cannot mask a real new-schema null.
    if value is None:
        legacy = LEGACY_FIELD_ALIASES.get(name)
        if legacy is not None:
            value = outcome.get(legacy)
    return value
# Top-level (non-outcome) HMM-accuracy fields worth carrying for context.
TOPLEVEL_AVG_FIELDS = ("macro_f1", "micro_f1")


_METRICS_SUFFIX = ".metrics.json"

# Column order for the metrics_per_session table (keys first, then numeric fields).
_METRICS_KEY_COLS = ("participant_id", "os", "session_id")


def _to_posix(p: Path) -> str:
    """DuckDB on Windows accepts forward slashes; posix strings keep CSV file
    paths separator-predictable when passed as bind parameters."""
    return p.resolve().as_posix()


def _collect_metrics_rows(metrics_root: Path) -> tuple[list[tuple], str | None]:
    """Parse per-session metrics JSON under ``<metrics_root>/P*/<os>/*.metrics.json``.

    participant_id / os / session_id are derived in Python from the path
    **relative to metrics_root** -- not from a hardcoded ``/metrics/`` regex --
    so any ``--metrics-subdir`` (e.g. recomputed anonymized metrics, stream 3
    variant) works identically. The JSON body is parsed with the stdlib (like
    check_schema_parity.py); missing fields / missing ``outcome`` / JSON null all
    become None (-> SQL NULL), tolerating pre-v0.4 files.

    Excludes ``*.range*`` variants (a separate HMM-accuracy export without (a)(b)
    outcome fields). Returns (rows, error): each row is a tuple ordered as
    _METRICS_KEY_COLS + OUTCOME_SUM_FIELDS + OUTCOME_AVG_FIELDS + TOPLEVEL_AVG_FIELDS.
    On a corrupt/unreadable file, returns ([], message)."""
    if not metrics_root.is_dir():
        return [], None
    rows: list[tuple] = []
    for p in sorted(metrics_root.glob("P*/*/*.metrics.json")):
        if "range" in p.name:
            continue
        rel = p.relative_to(metrics_root).parts  # (P###, <os>, <file>)
        participant_id, os_name = rel[0], rel[1]
        session_id = p.name[: -len(_METRICS_SUFFIX)]
        try:
            data = json.loads(p.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as e:
            return [], f"cannot read metrics JSON {p}: {e}"
        if not isinstance(data, dict):
            return [], f"metrics JSON {p} is not a JSON object"
        outcome = data.get("outcome") or {}
        row = (
            participant_id, os_name, session_id,
            *(_lift_outcome_field(outcome, name) for name in OUTCOME_SUM_FIELDS),
            *(_lift_outcome_field(outcome, name) for name in OUTCOME_AVG_FIELDS),
            *(data.get(name) for name in TOPLEVEL_AVG_FIELDS),
        )
        rows.append(row)
    return rows, None


def _collect_survey_files(survey_root: Path) -> list[Path]:
    if not survey_root.is_dir():
        return []
    return sorted(survey_root.glob("*.csv"))


def _check_survey_privacy(survey_files: list[Path]) -> str | None:
    """Return an error message if any survey CSV header contains a forbidden PII
    column, else None. Reads only the header row.

    Scope: this is a column-NAME gate only. Cell-value PII (e.g. a real name
    typed into a free-text ``comments`` column) is NOT detected here -- per
    data-privacy / decisions.md D1 the primary control is operational (researchers
    must not put PII into survey CSVs at all; the real-name<->P-ID map lives
    outside the repo). The gate is an early-detection net, not the sole defence."""
    for f in survey_files:
        try:
            with open(f, encoding="utf-8-sig", newline="") as fh:
                header = next(csv.reader(fh), [])
        except OSError as e:
            return f"cannot read survey CSV header {f}: {e}"
        for col in header:
            stripped = col.strip()
            low = stripped.lower()
            for tok in FORBIDDEN_SURVEY_SUBSTRINGS:
                # ASCII tokens match against the lowercased name; Japanese tokens
                # (non-ascii) match against the raw name.
                hay = low if tok.isascii() else stripped
                if tok in hay:
                    return (
                        f"forbidden PII token '{tok}' in column '{stripped}' of {f}. "
                        "Survey CSVs must contain only P-ID + numeric scale scores "
                        "(data-privacy / decisions.md D1). Rename/remove the column."
                    )
    return None


def _build(con, metrics_rows: list[tuple], survey_files: list[Path],
           sessions_csv: Path | None) -> None:
    """Create the analysis tables/views inside an open DuckDB connection.

    ``metrics_rows`` are tuples from _collect_metrics_rows() ordered as
    _METRICS_KEY_COLS + OUTCOME_SUM_FIELDS + OUTCOME_AVG_FIELDS + TOPLEVEL_AVG_FIELDS."""
    # ---- (3) metrics: insert pre-parsed rows --------------------------------
    # Keys are typed VARCHAR; count-like fields BIGINT; ratio/accuracy DOUBLE.
    col_defs = [f"{c} VARCHAR" for c in _METRICS_KEY_COLS]
    col_defs += [f"{c} BIGINT" for c in OUTCOME_SUM_FIELDS]
    col_defs += [f"{c} DOUBLE" for c in (*OUTCOME_AVG_FIELDS, *TOPLEVEL_AVG_FIELDS)]
    con.execute(f"CREATE TABLE metrics_per_session ({', '.join(col_defs)})")
    if metrics_rows:
        placeholders = ", ".join(["?"] * len(metrics_rows[0]))
        con.executemany(
            f"INSERT INTO metrics_per_session VALUES ({placeholders})", metrics_rows
        )

    # ---- manifest: map session -> phase (optional) --------------------------
    if sessions_csv is not None and sessions_csv.is_file():
        # Force join keys to VARCHAR so type inference (e.g. a form exporting
        # phase as 1/2, or numeric-looking session ids) cannot silently produce a
        # zero-row join against the VARCHAR metrics keys.
        con.execute(
            "CREATE TABLE sessions AS SELECT * REPLACE ("
            "CAST(participant_id AS VARCHAR) AS participant_id, "
            "CAST(session_id AS VARCHAR) AS session_id, "
            "CAST(os AS VARCHAR) AS os, "
            "CAST(phase AS VARCHAR) AS phase) "
            "FROM read_csv($p, header = true)",
            {"p": _to_posix(sessions_csv)},
        )
        con.execute(
            """
            CREATE VIEW metrics_phased AS
            SELECT m.*, COALESCE(s.phase, 'unknown') AS phase
            FROM metrics_per_session m
            LEFT JOIN sessions s
              ON m.participant_id = s.participant_id
             AND m.session_id = s.session_id
             AND m.os = s.os
            """
        )
    else:
        con.execute(
            "CREATE VIEW metrics_phased AS SELECT m.*, 'unknown' AS phase "
            "FROM metrics_per_session m"
        )

    # ---- metrics_agg: (participant_id, phase) grain --------------------------
    sum_aggs = ",\n            ".join(
        f"SUM({name}) AS {name}_sum" for name in OUTCOME_SUM_FIELDS
    )
    avg_aggs = ",\n            ".join(
        f"AVG({name}) AS {name}_avg"
        for name in (*OUTCOME_AVG_FIELDS, *TOPLEVEL_AVG_FIELDS)
    )
    # NOTE: ratio fields are simple (unweighted) means across a participant's
    # sessions in a phase; session_count is carried so analysts can re-weight.
    con.execute(
        f"""
        CREATE VIEW metrics_agg AS
        SELECT
            participant_id,
            phase,
            COUNT(*) AS session_count,
            {sum_aggs},
            {avg_aggs}
        FROM metrics_phased
        GROUP BY participant_id, phase
        """
    )

    # ---- (2) survey: union all CSVs, (participant_id, phase) grain -----------
    if survey_files:
        # Same VARCHAR coercion on the join keys as for sessions (see above).
        con.execute(
            "CREATE TABLE survey AS SELECT * REPLACE ("
            "CAST(participant_id AS VARCHAR) AS participant_id, "
            "CAST(phase AS VARCHAR) AS phase) "
            "FROM read_csv($files, header = true, union_by_name = true)",
            {"files": [_to_posix(f) for f in survey_files]},
        )
    else:
        con.execute(
            "CREATE TABLE survey (participant_id VARCHAR, phase VARCHAR)"
        )

    # survey grain MUST be unique on (participant_id, phase): the cross_section
    # FULL OUTER JOIN is against the GROUP BY-ed metrics_agg, so a duplicated
    # survey key (re-submitted Google Form, overlapping CSVs) would multiply rows.
    # Per D2/D3 exactly one survey row is expected per (P-ID, pre|post); a
    # duplicate is a data error we surface (fail-closed) rather than silently
    # pick one nondeterministically.
    dups = con.execute(
        "SELECT participant_id, phase, COUNT(*) AS n FROM survey "
        "GROUP BY participant_id, phase HAVING COUNT(*) > 1 "
        "ORDER BY participant_id, phase"
    ).fetchall()
    if dups:
        listing = ", ".join(f"({p},{ph})x{n}" for p, ph, n in dups)
        raise _SurveyDuplicateError(
            f"survey has duplicate (participant_id, phase) rows: {listing}. "
            "Expected exactly one row per participant per pre/post (D2/D3); "
            "de-duplicate the survey CSV(s) and retry."
        )

    # ---- cross_section: FULL OUTER JOIN, explicit missing-stream flags -------
    con.execute(
        """
        CREATE VIEW cross_section AS
        SELECT
            COALESCE(m.participant_id, s.participant_id) AS participant_id,
            COALESCE(m.phase, s.phase) AS phase,
            (m.participant_id IS NOT NULL) AS has_metrics,
            (s.participant_id IS NOT NULL) AS has_survey,
            m.* EXCLUDE (participant_id, phase),
            s.* EXCLUDE (participant_id, phase)
        FROM metrics_agg m
        FULL OUTER JOIN survey s
          ON m.participant_id = s.participant_id AND m.phase = s.phase
        """
    )


def _export(con, export_dir: Path, fmt: str) -> list[Path]:
    """Export cross_section deterministically (ORDER BY) to csv/parquet."""
    export_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    ordered = "SELECT * FROM cross_section ORDER BY participant_id, phase"
    if fmt in ("csv", "both"):
        out = export_dir / "cross_section.csv"
        con.execute(
            f"COPY ({ordered}) TO $p (FORMAT CSV, HEADER true)", {"p": _to_posix(out)}
        )
        written.append(out)
    if fmt in ("parquet", "both"):
        out = export_dir / "cross_section.parquet"
        con.execute(f"COPY ({ordered}) TO $p (FORMAT PARQUET)", {"p": _to_posix(out)})
        written.append(out)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Join GSE validation streams (metrics/survey/sessions) into a "
        "disposable DuckDB analysis.db on participant_id (decisions.md D5).",
    )
    parser.add_argument(
        "--dataset", required=True,
        help="Path to the gse-dataset repo root (contains metrics/, survey/, "
        "optionally sessions.csv).",
    )
    parser.add_argument(
        "--out", default="analysis.db",
        help="Output DuckDB file path (disposable; deleted+recreated). "
        "Default: analysis.db",
    )
    parser.add_argument(
        "--metrics-subdir", default="metrics",
        help="Subdir of --dataset holding metrics JSON (default: metrics). Point "
        "at e.g. recomputed anonymized metrics to use stream (3) variant.",
    )
    parser.add_argument(
        "--export-dir", default=None,
        help="Directory for cross_section export (default: alongside --out).",
    )
    parser.add_argument(
        "--format", choices=("csv", "parquet", "both"), default="csv",
        help="Export format for cross_section (default: csv).",
    )
    args = parser.parse_args(argv)

    try:
        import duckdb  # noqa: PLC0415 -- lazy so missing dep -> exit 5, not crash
    except ImportError:
        print(
            "[build_analysis_db] ERROR: duckdb not installed.\n"
            "  run: pip install -r scripts/requirements-dev.txt",
            file=sys.stderr,
        )
        return EXIT_NO_DUCKDB

    dataset = Path(args.dataset)
    if not dataset.is_dir():
        print(f"[build_analysis_db] ERROR: --dataset not found: {dataset}", file=sys.stderr)
        return EXIT_DATASET_MISSING

    metrics_root = dataset / args.metrics_subdir
    survey_root = dataset / "survey"
    sessions_csv = dataset / "sessions.csv"

    metrics_rows, metrics_err = _collect_metrics_rows(metrics_root)
    if metrics_err is not None:
        print(f"[build_analysis_db] ERROR: {metrics_err}", file=sys.stderr)
        return EXIT_USAGE
    survey_files = _collect_survey_files(survey_root)

    if not metrics_rows and not survey_files:
        print(
            f"[build_analysis_db] ERROR: no data found. Looked for "
            f"{metrics_root}/P*/<os>/*.metrics.json and {survey_root}/*.csv",
            file=sys.stderr,
        )
        return EXIT_NO_DATA

    privacy_err = _check_survey_privacy(survey_files)
    if privacy_err is not None:
        print(f"[build_analysis_db] PRIVACY GUARD: {privacy_err}", file=sys.stderr)
        return EXIT_PRIVACY

    out_path = Path(args.out)
    # Disposable: a stale DB must never be silently reused (D5 "regenerate-able").
    try:
        out_path.unlink(missing_ok=True)
        if out_path.parent and not out_path.parent.exists():
            out_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[build_analysis_db] ERROR: cannot reset {out_path}: {e}", file=sys.stderr)
        return EXIT_USAGE

    export_dir = Path(args.export_dir) if args.export_dir else (out_path.parent or Path("."))

    try:
        con = duckdb.connect(str(out_path))
        try:
            _build(con, metrics_rows, survey_files,
                   sessions_csv if sessions_csv.is_file() else None)
            n_rows = con.execute("SELECT COUNT(*) FROM cross_section").fetchone()[0]
            written = _export(con, export_dir, args.format)
        finally:
            con.close()
    except _SurveyDuplicateError as e:
        print(f"[build_analysis_db] ERROR: {e}", file=sys.stderr)
        return EXIT_USAGE
    except duckdb.Error as e:
        print(f"[build_analysis_db] ERROR: DuckDB build failed: {e}", file=sys.stderr)
        return EXIT_USAGE
    except OSError as e:
        print(f"[build_analysis_db] ERROR: I/O during build: {e}", file=sys.stderr)
        return EXIT_USAGE

    print(
        f"[build_analysis_db] OK: {out_path} built "
        f"({len(metrics_rows)} metrics file(s), {len(survey_files)} survey CSV(s), "
        f"cross_section rows={n_rows})."
    )
    for w in written:
        print(f"  exported: {w}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
