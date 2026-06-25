"""Tests for scripts/gen_sessions_manifest.py (pilot-pipeline-runbook GAP② / D-PP3).

Builds a tiny synthetic metrics tree in a temp dir -- no real data, no duckdb.

Run:
    cd gse-prototype
    python -m unittest scripts.tests.test_gen_sessions_manifest -v
"""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import gen_sessions_manifest as gsm  # noqa: E402


def _touch_metrics(root: Path, pid: str, os_name: str, session: str) -> None:
    d = root / "metrics" / pid / os_name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{session}.metrics.json").write_text("{}", encoding="utf-8")


def _read(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


class GenSessionsManifestTest(unittest.TestCase):
    def test_generates_rows_with_blank_phase(self) -> None:
        with TemporaryDirectory() as td:
            ds = Path(td)
            _touch_metrics(ds, "P101", "windows", "sess_a")
            _touch_metrics(ds, "P101", "windows", "sess_b")
            _touch_metrics(ds, "P102", "macos", "sess_c")
            rc = gsm.main(["--dataset", str(ds)])
            self.assertEqual(rc, gsm.EXIT_OK)
            rows = _read(ds / "sessions.csv")
            keys = {(r["participant_id"], r["session_id"], r["os"]) for r in rows}
            self.assertEqual(
                keys,
                {
                    ("P101", "sess_a", "windows"),
                    ("P101", "sess_b", "windows"),
                    ("P102", "sess_c", "macos"),
                },
            )
            # All phases blank on first generation.
            self.assertTrue(all(r["phase"] == "" for r in rows))
            # Header contract matches build_analysis_db expectations.
            self.assertEqual(
                list(rows[0].keys()), ["participant_id", "session_id", "os", "phase"]
            )

    def test_excludes_range_variant(self) -> None:
        with TemporaryDirectory() as td:
            ds = Path(td)
            _touch_metrics(ds, "P101", "windows", "sess_a")
            _touch_metrics(ds, "P101", "windows", "sess_a.range")
            gsm.main(["--dataset", str(ds)])
            rows = _read(ds / "sessions.csv")
            self.assertEqual([r["session_id"] for r in rows], ["sess_a"])

    def test_preserves_manual_phase_on_regen(self) -> None:
        with TemporaryDirectory() as td:
            ds = Path(td)
            _touch_metrics(ds, "P101", "windows", "sess_a")
            gsm.main(["--dataset", str(ds)])
            # Researcher fills phase=pre by hand.
            out = ds / "sessions.csv"
            rows = _read(out)
            rows[0]["phase"] = "pre"
            with open(out, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(
                    fh,
                    fieldnames=["participant_id", "session_id", "os", "phase"],
                    lineterminator="\n",
                )
                w.writeheader()
                w.writerows(rows)
            # A new session appears; regenerate.
            _touch_metrics(ds, "P101", "windows", "sess_b")
            gsm.main(["--dataset", str(ds)])
            rows2 = {r["session_id"]: r["phase"] for r in _read(out)}
            self.assertEqual(rows2["sess_a"], "pre")  # preserved
            self.assertEqual(rows2["sess_b"], "")  # new, blank

    def test_drops_stale_row_when_metrics_gone(self) -> None:
        with TemporaryDirectory() as td:
            ds = Path(td)
            _touch_metrics(ds, "P101", "windows", "sess_a")
            gsm.main(["--dataset", str(ds)])
            out = ds / "sessions.csv"
            # Add a row whose metrics file does not exist, then regenerate.
            with open(out, "a", encoding="utf-8", newline="") as fh:
                fh.write("P101,ghost,windows,pre\n")
            gsm.main(["--dataset", str(ds)])
            sids = {r["session_id"] for r in _read(out)}
            self.assertEqual(sids, {"sess_a"})  # ghost dropped

    def test_unexpected_phase_is_preserved_not_dropped(self) -> None:
        with TemporaryDirectory() as td:
            ds = Path(td)
            _touch_metrics(ds, "P101", "windows", "sess_a")
            gsm.main(["--dataset", str(ds)])
            out = ds / "sessions.csv"
            rows = _read(out)
            rows[0]["phase"] = "Pre"  # typo: not in {pre,post}
            with open(out, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(
                    fh,
                    fieldnames=["participant_id", "session_id", "os", "phase"],
                    lineterminator="\n",
                )
                w.writeheader()
                w.writerows(rows)
            gsm.main(["--dataset", str(ds)])  # warns on stderr, must not crash
            self.assertEqual(_read(out)[0]["phase"], "Pre")  # preserved verbatim

    def test_no_sessions_returns_exit_3(self) -> None:
        with TemporaryDirectory() as td:
            ds = Path(td)
            (ds / "metrics").mkdir()
            rc = gsm.main(["--dataset", str(ds)])
            self.assertEqual(rc, gsm.EXIT_NO_DATA)

    def test_missing_dataset_returns_exit_2(self) -> None:
        rc = gsm.main(["--dataset", str(Path("does-not-exist-xyz"))])
        self.assertEqual(rc, gsm.EXIT_DATASET_MISSING)


if __name__ == "__main__":
    unittest.main()
