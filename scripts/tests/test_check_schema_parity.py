"""Regression tests for scripts/check_schema_parity.py.

TDD: これらのテストは helper が実装される前は全滅する想定。
実行方法:
    cd gse-prototype
    python -m unittest scripts.tests.test_check_schema_parity -v
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HELPER = REPO_ROOT / "scripts" / "check_schema_parity.py"


def _minimal_schema(variants):
    """Build a minimal JSON-Schema mirroring schema_dto.rs' tagged-union shape.

    variants: list[str] — enum values to include under the `type` field of
    one oneOf branch, representing the LogEntryDto discriminator.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "LogEntryDto",
        "oneOf": [
            {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"type": "string", "enum": [v]},
                },
            }
            for v in variants
        ],
    }


def _run(proto_path, dataset_path):
    """Run the helper against two schema paths; return CompletedProcess."""
    cmd = [
        sys.executable,
        str(HELPER),
        "--src-tauri-schema",
        str(proto_path),
        "--dataset-schema",
        str(dataset_path),
    ]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


class CheckSchemaParityTest(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.proto = self.tmp / "proto.json"
        self.dataset = self.tmp / "dataset.json"

    def _write(self, path, schema, newline=None):
        with open(path, "w", encoding="utf-8", newline=newline) as f:
            json.dump(schema, f, indent=2, sort_keys=False)

    def test_identical_schemas_exit_0(self):
        schema = _minimal_schema(["meta", "key", "feat"])
        self._write(self.proto, schema)
        self._write(self.dataset, schema)
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_crlf_vs_lf_is_not_drift(self):
        """改行コード差異は意味同値として扱う (false positive 回避)."""
        schema = _minimal_schema(["meta", "key"])
        self._write(self.proto, schema, newline="\n")
        self._write(self.dataset, schema, newline="\r\n")
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_key_order_difference_is_not_drift(self):
        """キー順序の揺れは意味同値として扱う."""
        schema_a = _minimal_schema(["meta", "key"])
        # 同一 variants だが dict 走査順が違う表現
        schema_b = json.loads(json.dumps(schema_a, sort_keys=True))
        self._write(self.proto, schema_a)
        with open(self.dataset, "w", encoding="utf-8") as f:
            json.dump(schema_b, f, indent=2, sort_keys=True)
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_variant_added_on_proto_side_reports_missing_in_b(self):
        proto_schema = _minimal_schema(["meta", "key", "ime_shadow"])
        dataset_schema = _minimal_schema(["meta", "key"])
        self._write(self.proto, proto_schema)
        self._write(self.dataset, dataset_schema)
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("ime_shadow", r.stdout + r.stderr)

    def test_variant_extra_on_dataset_side_reports_extra_in_b(self):
        proto_schema = _minimal_schema(["meta", "key"])
        dataset_schema = _minimal_schema(["meta", "key", "legacy_variant"])
        self._write(self.proto, proto_schema)
        self._write(self.dataset, dataset_schema)
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("legacy_variant", r.stdout + r.stderr)

    def test_proto_schema_missing_exit_2(self):
        self._write(self.dataset, _minimal_schema(["meta"]))
        # proto は書かない
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn(str(self.proto.name), r.stdout + r.stderr)

    def test_dataset_schema_missing_exit_3(self):
        self._write(self.proto, _minimal_schema(["meta"]))
        # dataset は書かない
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        # 修復手順メッセージにコピーコマンドが含まれる
        self.assertIn("cp ", r.stdout + r.stderr)

    def test_invalid_json_exits_cleanly_exit_4(self):
        """壊れた JSON の場合 exit 4 + どのファイルが壊れたか明示."""
        self._write(self.proto, _minimal_schema(["meta"]))
        with open(self.dataset, "w", encoding="utf-8") as f:
            f.write("{ this is not valid json")
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertIn("cannot parse", r.stdout + r.stderr)
        self.assertIn(self.dataset.name, r.stdout + r.stderr)
        # Python のトレースバックを生の状態で投げない (user-friendly message のみ)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_utf8_bom_on_windows_notepad_saved_file(self):
        """Windows Notepad 保存など UTF-8 BOM 付きの schema でも parse できる (exit 0)."""
        schema = _minimal_schema(["meta", "key"])
        with open(self.proto, "wb") as f:
            f.write(b"\xef\xbb\xbf")
            f.write(json.dumps(schema, indent=2).encode("utf-8"))
        with open(self.dataset, "wb") as f:
            f.write(b"\xef\xbb\xbf")
            f.write(json.dumps(schema, indent=2).encode("utf-8"))
        r = _run(self.proto, self.dataset)
        # helper は encoding="utf-8-sig" で読むため BOM を透過する契約。
        # BOM で exit 4 に落ちる実装は regression とみなす。
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_const_tag_variant_recognized(self):
        """schemars が単一 variant で吐く `"type": {"const": "foo"}` も認識."""
        def _const_schema(variant):
            return {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["type"],
                        "properties": {"type": {"const": variant}},
                    }
                ],
            }
        self._write(self.proto, _const_schema("new_variant"))
        self._write(self.dataset, _const_schema("old_variant"))
        r = _run(self.proto, self.dataset)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("new_variant", r.stdout + r.stderr)
        self.assertIn("old_variant", r.stdout + r.stderr)

    def test_machine_readable_emits_sentinel_on_ok(self):
        schema = _minimal_schema(["meta"])
        self._write(self.proto, schema)
        self._write(self.dataset, schema)
        cmd = [
            sys.executable, str(HELPER),
            "--src-tauri-schema", str(self.proto),
            "--dataset-schema", str(self.dataset),
            "--machine-readable",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0)
        self.assertIn("HELPER_EXITCODE=0", r.stdout)

    def test_machine_readable_emits_sentinel_on_drift(self):
        self._write(self.proto, _minimal_schema(["a", "b"]))
        self._write(self.dataset, _minimal_schema(["a"]))
        cmd = [
            sys.executable, str(HELPER),
            "--src-tauri-schema", str(self.proto),
            "--dataset-schema", str(self.dataset),
            "--machine-readable",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("HELPER_EXITCODE=1", r.stdout)


if __name__ == "__main__":
    unittest.main()
