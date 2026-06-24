"""End-to-end tests for scripts/build_analysis_db.py (GSE #6 / decisions.md D5).

Drives the harness against the committed synthetic fixture
(scripts/fixtures/analysis_join/) -- no real data required.

Run:
    cd gse-prototype
    python -m unittest scripts.tests.test_build_analysis_db -v

Requires duckdb (pip install -r scripts/requirements-dev.txt). If duckdb is
absent the data tests are skipped, but the exit-5 contract test still runs.
"""

from __future__ import annotations

import csv
import importlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "scripts"
FIXTURE = SCRIPTS / "fixtures" / "analysis_join"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_analysis_db as bad  # noqa: E402

try:
    import duckdb  # noqa: F401

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

requires_duckdb = unittest.skipUnless(HAS_DUCKDB, "duckdb not installed")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _row(rows: list[dict[str, str]], pid: str, phase: str) -> dict[str, str]:
    for r in rows:
        if r["participant_id"] == pid and r["phase"] == phase:
            return r
    raise AssertionError(f"no row for ({pid}, {phase})")


@requires_duckdb
class BuildAnalysisDbTest(unittest.TestCase):
    def _build(self, tmp: Path, dataset: Path = FIXTURE) -> tuple[int, Path, Path]:
        db = tmp / "analysis.db"
        export = tmp / "export"
        rc = bad.main(
            ["--dataset", str(dataset), "--out", str(db), "--export-dir", str(export)]
        )
        return rc, db, export / "cross_section.csv"

    def test_t1_cross_section_has_all_pid_phase_rows(self):
        with TemporaryDirectory() as d:
            rc, db, csv_path = self._build(Path(d))
            self.assertEqual(rc, bad.EXIT_OK)
            self.assertTrue(db.exists())
            rows = _read_csv_rows(csv_path)
            grain = {(r["participant_id"], r["phase"]) for r in rows}
            self.assertEqual(
                grain,
                {
                    ("P101", "pre"), ("P101", "post"),
                    ("P102", "pre"),
                    ("P103", "pre"), ("P103", "post"),
                    ("P104", "unknown"),
                },
            )

    def test_t2_regeneration_is_deterministic(self):
        with TemporaryDirectory() as d1, TemporaryDirectory() as d2:
            rc1, _, csv1 = self._build(Path(d1))
            rc2, _, csv2 = self._build(Path(d2))
            self.assertEqual(rc1, bad.EXIT_OK)
            self.assertEqual(rc2, bad.EXIT_OK)
            self.assertEqual(
                csv1.read_bytes(), csv2.read_bytes(),
                "cross_section export must be byte-equal across rebuilds (D5)",
            )

    def test_t2b_db_is_disposable_rebuild_in_place(self):
        # Building twice to the same --out must not error or accumulate state.
        with TemporaryDirectory() as d:
            rc1, db, csv1 = self._build(Path(d))
            first = csv1.read_bytes()
            rc2, _, csv2 = self._build(Path(d))
            self.assertEqual((rc1, rc2), (bad.EXIT_OK, bad.EXIT_OK))
            self.assertEqual(first, csv2.read_bytes())

    def test_t3_missing_stream_flags(self):
        with TemporaryDirectory() as d:
            _, _, csv_path = self._build(Path(d))
            rows = _read_csv_rows(csv_path)
            # P103: survey only -> has_metrics false, has_survey true
            p103 = _row(rows, "P103", "pre")
            self.assertEqual(p103["has_metrics"], "false")
            self.assertEqual(p103["has_survey"], "true")
            # P104: metrics only -> has_metrics true, has_survey false
            p104 = _row(rows, "P104", "unknown")
            self.assertEqual(p104["has_metrics"], "true")
            self.assertEqual(p104["has_survey"], "false")

    def test_t4_measured_zero_distinct_from_absent(self):
        with TemporaryDirectory() as d:
            _, _, csv_path = self._build(Path(d))
            rows = _read_csv_rows(csv_path)
            # P102 genuinely pasted zero times -> 0, NOT empty/NULL.
            p102 = _row(rows, "P102", "pre")
            self.assertEqual(p102["external_paste_count_sum"], "0")
            # P103 has no metrics stream -> the same column is empty (NULL).
            p103 = _row(rows, "P103", "pre")
            self.assertEqual(p103["external_paste_count_sum"], "")

    def test_t4b_survey_values_join_correctly(self):
        with TemporaryDirectory() as d:
            _, _, csv_path = self._build(Path(d))
            rows = _read_csv_rows(csv_path)
            self.assertEqual(_row(rows, "P101", "pre")["gse_total"], "22")
            self.assertEqual(_row(rows, "P101", "post")["gse_total"], "31")

    def test_t5_privacy_guard_rejects_pii_column(self):
        with TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            (ds / "survey").mkdir(parents=True)
            # Minimal metrics so the run reaches the privacy check (not exit 3).
            mdir = ds / "metrics" / "P900" / "windows"
            mdir.mkdir(parents=True)
            (mdir / "s.metrics.json").write_text('{"total_labels":0}', encoding="utf-8")
            (ds / "survey" / "survey.csv").write_text(
                "participant_id,phase,real_name,gse_total\nP900,pre,Alice,30\n",
                encoding="utf-8",
            )
            rc = bad.main(
                ["--dataset", str(ds), "--out", str(Path(d) / "a.db")]
            )
            self.assertEqual(rc, bad.EXIT_PRIVACY)

    def test_t7_legacy_metrics_without_outcome_yields_null_outcome_cols(self):
        # Pre-v0.4 metrics.json lack the `outcome` object entirely. The harness
        # must still ingest them: outcome columns NULL, HMM-accuracy populated.
        with TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            mdir = ds / "metrics" / "P900" / "windows"
            mdir.mkdir(parents=True)
            (mdir / "legacy.metrics.json").write_text(
                '{"total_labels": 2, "macro_f1": 0.5, "micro_f1": 0.5, '
                '"detection_lead_ms_median": null, "warnings": []}',
                encoding="utf-8",
            )
            rc, _, csv_path = self._build(Path(d), dataset=ds)
            self.assertEqual(rc, bad.EXIT_OK)
            row = _row(_read_csv_rows(csv_path), "P900", "unknown")
            self.assertEqual(row["external_paste_count_sum"], "")  # NULL, absent
            self.assertEqual(row["macro_f1_avg"], "0.5")  # top-level present

    def test_t5b_privacy_guard_rejects_japanese_pii_column(self):
        # Real forms are Japanese; the substring guard must catch e.g. お名前.
        for pii_col in ("お名前", "メールアドレス", "email_address"):
            with self.subTest(col=pii_col), TemporaryDirectory() as d:
                ds = Path(d) / "dataset"
                mdir = ds / "metrics" / "P900" / "windows"
                mdir.mkdir(parents=True)
                (mdir / "s.metrics.json").write_text(
                    '{"total_labels":0}', encoding="utf-8"
                )
                (ds / "survey").mkdir()
                (ds / "survey" / "survey.csv").write_text(
                    f"participant_id,phase,{pii_col},gse_total\nP900,pre,x,30\n",
                    encoding="utf-8",
                )
                rc = bad.main(["--dataset", str(ds), "--out", str(Path(d) / "a.db")])
                self.assertEqual(rc, bad.EXIT_PRIVACY)

    def test_t8_integer_phase_keys_coerce_and_join(self):
        # If a form exports phase/keys as integers, type inference must not break
        # the join (keys are coerced to VARCHAR). Without the fix this errors or
        # silently yields zero join rows.
        with TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            mdir = ds / "metrics" / "P900" / "windows"
            mdir.mkdir(parents=True)
            (mdir / "s1.metrics.json").write_text(
                '{"total_labels":1,"macro_f1":0.5,"micro_f1":0.5,'
                '"outcome":{"external_paste_count":3}}',
                encoding="utf-8",
            )
            (ds / "survey").mkdir()
            (ds / "survey" / "survey.csv").write_text(
                "participant_id,phase,gse_total\nP900,1,30\n", encoding="utf-8"
            )
            (ds / "sessions.csv").write_text(
                "participant_id,session_id,os,phase\nP900,s1,windows,1\n",
                encoding="utf-8",
            )
            rc, _, csv_path = self._build(Path(d), dataset=ds)
            self.assertEqual(rc, bad.EXIT_OK)
            row = _row(_read_csv_rows(csv_path), "P900", "1")
            self.assertEqual(row["has_metrics"], "true")
            self.assertEqual(row["has_survey"], "true")
            self.assertEqual(row["external_paste_count_sum"], "3")
            self.assertEqual(row["gse_total"], "30")

    def test_t9_metrics_subdir_nondefault_derives_keys(self):
        # --metrics-subdir other than 'metrics' must still derive participant_id/
        # os/session_id correctly (keys come from the path relative to the subdir,
        # not a hardcoded '/metrics/' literal). Regression guard for cross-review C1.
        with TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            mdir = ds / "recomputed_metrics" / "P201" / "macos"
            mdir.mkdir(parents=True)
            (mdir / "sX.metrics.json").write_text(
                '{"total_labels":1,"macro_f1":0.9,'
                '"outcome":{"external_paste_count":7}}',
                encoding="utf-8",
            )
            db = Path(d) / "a.db"
            export = Path(d) / "ex"
            rc = bad.main([
                "--dataset", str(ds), "--out", str(db),
                "--metrics-subdir", "recomputed_metrics",
                "--export-dir", str(export),
            ])
            self.assertEqual(rc, bad.EXIT_OK)
            row = _row(_read_csv_rows(export / "cross_section.csv"), "P201", "unknown")
            self.assertEqual(row["external_paste_count_sum"], "7")
            self.assertEqual(row["has_metrics"], "true")

    def test_t10_duplicate_survey_keys_rejected(self):
        # Two survey rows for the same (participant_id, phase) must fail-closed
        # rather than multiply cross_section rows. Cross-review C2.
        with TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            (ds / "survey").mkdir(parents=True)
            (ds / "survey" / "survey.csv").write_text(
                "participant_id,phase,gse_total\nP301,pre,20\nP301,pre,25\n",
                encoding="utf-8",
            )
            rc = bad.main(["--dataset", str(ds), "--out", str(Path(d) / "a.db")])
            self.assertEqual(rc, bad.EXIT_USAGE)

    def test_corrupt_metrics_json_returns_exit_4(self):
        with TemporaryDirectory() as d:
            ds = Path(d) / "dataset"
            mdir = ds / "metrics" / "P400" / "windows"
            mdir.mkdir(parents=True)
            (mdir / "bad.metrics.json").write_text("{not json", encoding="utf-8")
            rc = bad.main(["--dataset", str(ds), "--out", str(Path(d) / "a.db")])
            self.assertEqual(rc, bad.EXIT_USAGE)

    def test_no_data_returns_exit_3(self):
        with TemporaryDirectory() as d:
            ds = Path(d) / "empty"
            ds.mkdir()
            rc = bad.main(["--dataset", str(ds), "--out", str(Path(d) / "a.db")])
            self.assertEqual(rc, bad.EXIT_NO_DATA)

    def test_dataset_missing_returns_exit_2(self):
        with TemporaryDirectory() as d:
            rc = bad.main(
                ["--dataset", str(Path(d) / "nope"), "--out", str(Path(d) / "a.db")]
            )
            self.assertEqual(rc, bad.EXIT_DATASET_MISSING)


class DuckdbMissingTest(unittest.TestCase):
    def test_t6_missing_duckdb_returns_exit_5(self):
        # Make `import duckdb` raise ImportError regardless of install state by
        # poisoning sys.modules, then reload the module-under-test's main path.
        saved = sys.modules.get("duckdb")
        sys.modules["duckdb"] = None  # type: ignore[assignment]
        try:
            importlib.reload(bad)
            with TemporaryDirectory() as d:
                rc = bad.main(
                    ["--dataset", str(FIXTURE), "--out", str(Path(d) / "a.db")]
                )
            self.assertEqual(rc, bad.EXIT_NO_DUCKDB)
        finally:
            if saved is not None:
                sys.modules["duckdb"] = saved
            else:
                sys.modules.pop("duckdb", None)
            importlib.reload(bad)


if __name__ == "__main__":
    unittest.main()
