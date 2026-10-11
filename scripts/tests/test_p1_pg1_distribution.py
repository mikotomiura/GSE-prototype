"""Tests for scripts/p1_features_io.py + scripts/p1_pg1_distribution.py (PG-1 に渡す分布だけを出す CLI・issue 002).

⚠️★★★ **規則を 1 つずつ固定する。** ★ 特に「分布だけを見る」(事前宣言 §2.3 PG-1) の構造の保証は、
行の中身を**消しても・書き換えても**出力がバイト単位で変わらないことで確かめる
(⚠️ 「onset だけ数える」実装と「転帰の量も見ている」実装は、素直な入力では同じ出力になる)。

⚠️ 本 module は実データも Rust も読まない (★ 入力はテストが `tempfile` の中で作る合成の封筒だけ。
封筒の形は実物の `gse-replay --features` の出力を実測して写した)。

⚠️★ テスト名の行に `... ok` が同じ行に出ることを acceptance が見る。→ ★ テストに docstring を付けない
(verbose 出力が 2 行に割れる)。★ 標準エラーは必ず捕捉する (行の途中に混ざると `... ok` が崩れる)。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_p1_pg1_distribution -v
"""

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p1_bounds  # noqa: E402
import p1_features_io as fio  # noqa: E402
import p1_pg1_distribution as pg1  # noqa: E402

POLES = p1_bounds.POLES
CLI = SCRIPTS / "p1_pg1_distribution.py"
PREREG_SHA = "0123456789abcdef"

# ★ 行の中身のキー (PG-1 が読んではいけないもの)。実物の行のキーを写した。
ROW_CONTENT_KEYS = ("restart", "dispersion", "activity", "boundary", "revision", "quality")
ONSET_OTHER_KEYS = ("s_ms", "t0_ms", "theta_person_ms", "theta_sample_n", "task_kind", "phase", "ime_overlap")


def make_row(i, is_onset):
    return {
        "t_ms": 1_700_000_000_000 + i * 1000,
        "activity": {"key_count": i % 7, "backspace_count": 1},
        "boundary": {"pauses": i % 3},
        "dispersion": {"pause_p50_ms": 2100 + i, "pause_p90_ms": 3000, "pause_max_ms": 4000, "iki_cv": 0.5},
        "stall_onset": {
            "is_onset": is_onset,
            "s_ms": 1_700_000_000_500 + i * 1000 if is_onset else None,
            "t0_ms": 1_700_000_003_500 + i * 1000 if is_onset else None,
            "theta_person_ms": 2500 if is_onset else None,
            "theta_sample_n": 120 if is_onset else None,
            "task_kind": "writing" if is_onset else None,
            "phase": "unspecified",
            "ime_overlap": False if is_onset else None,
        },
        "quality": {"missing_reasons": []},
        "revision": {"units_closed": 0},
        "restart": {"restop_ms": 4000 if is_onset else None},
    }


def make_envelope(pole, onsets, applicable=True, reason=None):
    if not applicable and reason is None:
        reason = "no_modifier_rows" if pole == "modifier_m_plus" else "no_pointer_rows"
    flags = [True, False] * onsets + [False] * 5  # ★ onset が丁度 `onsets` 本
    return {
        "provenance": {
            "sharing": {"gse_dataset": "prohibited", "anonymized": False, "absolute_epoch_ms": True, "rule": "x"},
            "tool": "gse-replay",
            "tool_version": "0.1.35",
            "source_basename": "synthetic.ndjson",
            "source_sha256_prefix": "7c132558261a9b02",
            "session_start": 1_700_000_000_000,
            "hmm_version": "0.5.0",
            "app_version": None,
            "capabilities": None,
            "observed_intervals": [{"a_ms": 1_700_000_001_000, "b_ms": 1_700_000_220_000}],
            # ★ 今の binary の形 (事前宣言 v1.2 §6.1): 3 極とも同じ値を持つ
            "idle_trim": {"dropped_feat_rows": 4, "spans": [{"a_ms": 1_700_000_221_000, "b_ms": 1_700_000_224_000}]},
            # ★ 事前宣言 v1.3 §7.1 (凍結 JSON 1.2.0 の binary の形)
            "input_gap_trim": {"dropped_feat_rows": 0, "spans": []},
        },
        "config": {
            "w_ms": 30000,
            "q": 0.99,
            "b_ms": 30000,
            "net_diff_min": 1,
            "hole_gap_ms": 2000,
            "warmup_count": 100,
            "theta_estimator": "nearest_rank",
            "t1a_window_ms": 30000,
            "idle_trim_min_gap_ms": 60000,
            "idle_trim_max_ms": 1800000,
            "idle_trim_input_gap_ms": 1800000,
            "pole": pole,
            "pole_applicable": applicable,
            "pole_not_applicable_reason": None if applicable else reason,
            "prereg_id": "p1-episode",
            "prereg_version": "1.0.0",
            "prereg_sha256_prefix": PREREG_SHA,
            "config_source": "frozen",
            "overrides": [],
            "max_feature_ticks": 1_000_000,
            "hmm_version": "0.5.0",
            "engine_tick_ms": 1000,
            "pause_threshold_ms": 2000,
        },
        "rows": [make_row(i, flag) for i, flag in enumerate(flags)],
    }


def write_session(root, participant, session, onsets, not_applicable=()):
    """`onsets`: 極 → onset の本数 (無い極は 0)。`not_applicable`: 非適用にする極。"""
    session_dir = Path(root) / participant / session
    session_dir.mkdir(parents=True)
    for pole in POLES:
        envelope = make_envelope(pole, onsets.get(pole, 0), applicable=pole not in not_applicable)
        (session_dir / f"{pole}.json").write_text(json.dumps(envelope), encoding="utf-8")
    return session_dir


def edit_envelope(path, fn):
    path = Path(path)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    fn(envelope)
    path.write_text(json.dumps(envelope), encoding="utf-8")


def run_cli(root, out):
    """CLI を同じプロセスで回し `(exit code, stderr)` を返す。⚠️ 標準出力・標準エラーは必ず捕捉する。"""
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        try:
            rc = pg1.main(["--root", str(root), "--out", str(out)])
        except SystemExit as e:  # argparse の引数不備は exit 2
            rc = e.code
    return rc, err.getvalue()


class LayoutCase(unittest.TestCase):
    def setUp(self):
        # ★ `TemporaryDirectory` は system の temp の下 (git 管理外) に作る
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self._n = 0

    def new_dir(self):
        self._n += 1
        path = self.tmp / f"d{self._n}"
        path.mkdir()
        return path

    def new_out(self):
        self._n += 1
        return self.tmp / f"out{self._n}" / "pg1.json"  # ★ 親ディレクトリはまだ無い

    def base_layout(self):
        root = self.new_dir()
        write_session(root, "P01", "s1", {"baseline": 2, "pointer_b": 1, "modifier_m_plus": 3})
        write_session(root, "P01", "s2", {"baseline": 3, "pointer_b": 0, "modifier_m_plus": 1})
        write_session(root, "P02", "s1", {"baseline": 4, "pointer_b": 4, "modifier_m_plus": 0})
        return root

    def run_ok(self, root):
        out = self.new_out()
        rc, err = run_cli(root, out)
        self.assertEqual(rc, 0, err)
        return out.read_bytes(), json.loads(out.read_text(encoding="utf-8"))

    def assert_rejected(self, root, expected_rc, label):
        out = self.new_out()
        rc, err = run_cli(root, out)
        self.assertEqual(rc, expected_rc, f"{label}: {err}")
        self.assertFalse(out.exists(), f"{label}: 拒否したのに出力が作られた")
        self.assertFalse(out.parent.exists(), f"{label}: 拒否したのに出力先のディレクトリが作られた")
        return err


class Pg1DistributionTest(LayoutCase):
    def test_counts_and_summary(self):
        _, result = self.run_ok(self.base_layout())
        self.assertEqual(
            result,
            {
                "poles": {
                    "baseline": {
                        "participants": {
                            "P01": {"sessions": 2, "sessions_not_applicable": 0, "episodes": 5},
                            "P02": {"sessions": 1, "sessions_not_applicable": 0, "episodes": 4},
                        },
                        "summary": {
                            "n_participants": 2,
                            "episodes_per_participant_sorted": [4, 5],
                            "min": 4,
                            "median": 4.5,
                            "max": 5,
                        },
                        "participants_without_applicable_sessions": 0,
                    },
                    "pointer_b": {
                        "participants": {
                            "P01": {"sessions": 2, "sessions_not_applicable": 0, "episodes": 1},
                            "P02": {"sessions": 1, "sessions_not_applicable": 0, "episodes": 4},
                        },
                        "summary": {
                            "n_participants": 2,
                            "episodes_per_participant_sorted": [1, 4],
                            "min": 1,
                            "median": 2.5,
                            "max": 4,
                        },
                        "participants_without_applicable_sessions": 0,
                    },
                    "modifier_m_plus": {
                        "participants": {
                            "P01": {"sessions": 2, "sessions_not_applicable": 0, "episodes": 4},
                            "P02": {"sessions": 1, "sessions_not_applicable": 0, "episodes": 0},
                        },
                        "summary": {
                            "n_participants": 2,
                            "episodes_per_participant_sorted": [0, 4],
                            "min": 0,
                            "median": 2,
                            "max": 4,
                        },
                        "participants_without_applicable_sessions": 0,
                    },
                },
                "provenance": {
                    "prereg_version": "1.0.0",
                    "prereg_sha256_prefix": PREREG_SHA,
                    "tool": "p1_pg1_distribution",
                    "n_sessions": 3,
                },
            },
        )

    def test_summarize_counts_edge_values(self):
        # ★ 中央値: 偶数個は 2 つの平均 (整数なら整数・そうでなければ x.5)・奇数個は真ん中
        self.assertEqual(
            pg1.summarize_counts([]),
            {"n_participants": 0, "episodes_per_participant_sorted": [], "min": None, "median": None, "max": None},
        )
        self.assertEqual(pg1.summarize_counts([3])["median"], 3)
        self.assertEqual(pg1.summarize_counts([9, 1, 2])["episodes_per_participant_sorted"], [1, 2, 9])
        self.assertEqual(pg1.summarize_counts([9, 1, 2])["median"], 2)
        self.assertEqual(pg1.summarize_counts([0, 5])["median"], 2.5)
        median = pg1.summarize_counts([2, 4])["median"]
        self.assertEqual(median, 3)
        self.assertIs(type(median), int)  # ⚠️ 3.0 ではなく 3

    def test_output_invariant_to_non_onset_fields(self):
        root = self.base_layout()
        reference, _ = self.run_ok(root)

        def strip_named(row):
            # AC の変異: 行の 6 キーと、stall_onset の is_onset 以外のキーを消す (t_ms は残す)
            for key in ROW_CONTENT_KEYS:
                del row[key]
            for key in ONSET_OTHER_KEYS:
                del row["stall_onset"][key]

        def strip_all(row):
            # ★ さらに強く: stall_onset だけの行にする (t_ms も消す)。⚠️ is_onset の値は mutate_all が元に戻す
            row.clear()
            row["stall_onset"] = {"is_onset": False}

        def rewrite_values(magnitude):
            # AC の変異: 値を書き換える (⚠️ config / provenance のメタデータには触れない・数値は有限)。
            # ★ 極小 (0) と極大 (10^12) の 2 通りで回す: 「閾値を超えたら数える」型の依存は片方でしか崩れない
            def rewrite(row):
                row["t_ms"] = magnitude
                row["restart"] = {"restop_ms": magnitude, "restop_kind": "none"}
                row["dispersion"] = [magnitude, 2, 3]
                row["activity"] = "garbage"
                row["boundary"] = None
                row["revision"] = magnitude + 0.5
                row["quality"] = {"missing_reasons": ["capability_undeclared"], "observability_mask": {"feat": False}}
                so = row["stall_onset"]
                so["s_ms"], so["t0_ms"] = magnitude, magnitude
                so["theta_person_ms"], so["theta_sample_n"] = magnitude, magnitude
                so["task_kind"], so["phase"] = "coding", "x"
                so["ime_overlap"] = not bool(so["ime_overlap"])

            return rewrite

        def mutate_all(source, fn):
            dest = self.new_dir() / "root"
            shutil.copytree(source, dest)
            for path in sorted(dest.glob("*/*/*.json")):
                envelope = json.loads(path.read_text(encoding="utf-8"))
                new_rows = []
                for row in envelope["rows"]:
                    flag = row["stall_onset"]["is_onset"]
                    fn(row)
                    row["stall_onset"]["is_onset"] = flag  # ★ is_onset だけは保つ (これが読まれる唯一の値)
                    new_rows.append(row)
                envelope["rows"] = new_rows
                path.write_text(json.dumps(envelope), encoding="utf-8")
            return dest

        variants = (
            ("strip_named", strip_named),
            ("strip_all", strip_all),
            ("rewrite_low", rewrite_values(0)),
            ("rewrite_high", rewrite_values(10**12)),
        )
        for name, fn in variants:
            with self.subTest(mutation=name):
                mutated = mutate_all(root, fn)
                # ★ 変異が空振りでないこと: 元と違うファイルになっている
                self.assertNotEqual(
                    (mutated / "P01" / "s1" / "baseline.json").read_text(encoding="utf-8"),
                    (root / "P01" / "s1" / "baseline.json").read_text(encoding="utf-8"),
                )
                got, _ = self.run_ok(mutated)
                self.assertEqual(got, reference)  # ★ バイト単位で同じ

        # ★ 陰性対照: is_onset を 1 つ変えれば出力は変わる (= 上の一致は「何も読んでいない」からではない)
        flipped = self.new_dir() / "root"
        shutil.copytree(root, flipped)
        edit_envelope(
            flipped / "P01" / "s1" / "baseline.json",
            lambda env: env["rows"][0]["stall_onset"].update(is_onset=not env["rows"][0]["stall_onset"]["is_onset"]),
        )
        got, _ = self.run_ok(flipped)
        self.assertNotEqual(got, reference)

    def test_projection_keys_are_fixed(self):
        projection = fio.project_pg1(make_envelope("baseline", 3))
        self.assertEqual(
            set(projection),
            {
                "pole",
                "pole_applicable",
                "pole_not_applicable_reason",
                "onsets",
                "prereg_version",
                "prereg_sha256_prefix",
                "config_source",
                "overrides_count",
            },
        )
        self.assertEqual(projection["onsets"], 3)
        self.assertIs(type(projection["onsets"]), int)
        self.assertEqual(projection["overrides_count"], 0)
        # ★ 行が 0 本でも読める (onset 0 本)
        empty = make_envelope("baseline", 0)
        empty["rows"] = []
        self.assertEqual(fio.project_pg1(empty)["onsets"], 0)

    def test_output_keys_whitelist(self):
        raw, result = self.run_ok(self.base_layout())
        self.assertEqual(set(result), {"poles", "provenance"})
        self.assertEqual(set(result["poles"]), set(POLES))
        for pole, block in result["poles"].items():
            with self.subTest(pole=pole):
                self.assertEqual(
                    set(block), {"participants", "summary", "participants_without_applicable_sessions"}
                )
                for participant, entry in block["participants"].items():
                    self.assertRegex(participant, r"^P[0-9A-Za-z_-]+$")
                    self.assertEqual(set(entry), {"sessions", "sessions_not_applicable", "episodes"})
                self.assertEqual(
                    set(block["summary"]),
                    {"n_participants", "episodes_per_participant_sorted", "min", "median", "max"},
                )
        self.assertEqual(set(result["provenance"]), {"prereg_version", "prereg_sha256_prefix", "tool", "n_sessions"})
        # ★ 行の中身のキー・共有禁止の印・転帰らしい語が出力のどこにも無い
        text = raw.decode("utf-8")
        for word in (*ROW_CONTENT_KEYS, *ONSET_OTHER_KEYS, "prohibited", "sharing", "outcome"):
            self.assertNotIn(word, text)

    def test_cli_source_does_not_name_row_content_keys(self):
        # ★ CLI は射影だけを使う。行の中身のキー名を名指ししない (acceptance も grep で見る)
        source = CLI.read_text(encoding="utf-8")
        for word in ("restart", "dispersion", "ime_overlap", "theta_person_ms", "theta_sample_n", "t0_ms", "s_ms"):
            self.assertNotIn(word, source)

    def test_not_applicable_counted_separately(self):
        root = self.new_dir()
        # ⚠️ 非適用の極の出力は baseline と恒等なので onset が載っている (= 数えると二重に数える)
        write_session(root, "P01", "s1", {"baseline": 1, "pointer_b": 7, "modifier_m_plus": 1}, not_applicable=("pointer_b",))
        write_session(root, "P01", "s2", {"baseline": 2, "pointer_b": 3, "modifier_m_plus": 0})
        write_session(
            root, "P02", "s1", {"baseline": 5, "pointer_b": 9, "modifier_m_plus": 5}, not_applicable=("pointer_b", "modifier_m_plus")
        )
        write_session(root, "P02", "s2", {"baseline": 0, "pointer_b": 9, "modifier_m_plus": 2}, not_applicable=("pointer_b",))
        _, result = self.run_ok(root)
        pointer = result["poles"]["pointer_b"]
        self.assertEqual(pointer["participants"]["P01"], {"sessions": 2, "sessions_not_applicable": 1, "episodes": 3})
        # ⚠️ P02 は全セッションが非適用: 「episode 0 本の参加者」ではなく、要約に入れず別に数える
        self.assertEqual(pointer["participants"]["P02"], {"sessions": 2, "sessions_not_applicable": 2, "episodes": 0})
        self.assertEqual(
            pointer["summary"],
            {"n_participants": 1, "episodes_per_participant_sorted": [3], "min": 3, "median": 3, "max": 3},
        )
        self.assertEqual(pointer["participants_without_applicable_sessions"], 1)
        # ★ 修飾キー軸: P02 は s1 が非適用・s2 が適用可 (2 本) → 要約に入る
        modifier = result["poles"]["modifier_m_plus"]
        self.assertEqual(modifier["participants"]["P02"], {"sessions": 2, "sessions_not_applicable": 1, "episodes": 2})
        self.assertEqual(modifier["summary"]["episodes_per_participant_sorted"], [1, 2])
        self.assertEqual(modifier["participants_without_applicable_sessions"], 0)
        # ★ baseline は影響を受けない (極を混ぜない)
        baseline = result["poles"]["baseline"]
        self.assertEqual(baseline["summary"]["episodes_per_participant_sorted"], [3, 5])
        self.assertEqual(baseline["participants_without_applicable_sessions"], 0)

    def test_zero_episode_participant_included(self):
        root = self.new_dir()
        write_session(root, "P01", "s1", {})
        write_session(root, "P01", "s2", {})
        write_session(root, "P02", "s1", {"baseline": 5, "pointer_b": 5, "modifier_m_plus": 5})
        _, result = self.run_ok(root)
        for pole in POLES:
            with self.subTest(pole=pole):
                block = result["poles"][pole]
                # ★ onset が 0 本の参加者も載る (⚠️ 消えると最小値が楽観化する)
                self.assertEqual(block["participants"]["P01"], {"sessions": 2, "sessions_not_applicable": 0, "episodes": 0})
                self.assertEqual(
                    block["summary"],
                    {"n_participants": 2, "episodes_per_participant_sorted": [0, 5], "min": 0, "median": 2.5, "max": 5},
                )
                self.assertEqual(block["participants_without_applicable_sessions"], 0)

    def test_fail_closed_layout(self):
        # ★ 対照: 何も壊さなければ通る (下の各拒否が「別の理由」で落ちていないことの裏づけ)
        self.run_ok(self.base_layout())

        def remove_pole_file(root):
            (root / "P02" / "s1" / "pointer_b.json").unlink()

        def pole_mismatch(root):
            shutil.copyfile(root / "P01" / "s1" / "baseline.json", root / "P01" / "s1" / "pointer_b.json")

        def lock_left(root):
            (root / "P01" / "s1" / ".all-poles.lock").mkdir()

        def staging_left(root):
            (root / "P01" / "s2" / ".all-poles.AbC123").mkdir()

        def extra_file(root):
            (root / "P01" / "s1" / "notes.txt").write_text("x", encoding="utf-8")

        def stray_root_file(root):
            (root / "README.txt").write_text("x", encoding="utf-8")

        def file_where_session_expected(root):
            (root / "P01" / "s3").write_text("x", encoding="utf-8")

        def participant_without_sessions(root):
            (root / "P03").mkdir()

        def empty_session_dir(root):
            (root / "P02" / "s2").mkdir()

        cases = {
            "極のファイルが欠ける": remove_pole_file,
            "config.pole がファイル名と食い違う": pole_mismatch,
            ".all-poles.lock が残る": lock_left,
            "staging が残る": staging_left,
            "契約に無いファイル": extra_file,
            "root 直下の余計なファイル": stray_root_file,
            "セッションの位置にファイル": file_where_session_expected,
            "セッションの無い参加者": participant_without_sessions,
            "空のセッション": empty_session_dir,
        }
        for label, fn in cases.items():
            with self.subTest(case=label):
                root = self.base_layout()
                fn(root)
                self.assert_rejected(root, 3, label)

        # P-ID の形違い
        for bad_name in ("X02", "p02", "P", "P 02", "P02.bak", "02", "P０２"):
            with self.subTest(p_id=bad_name):
                root = self.base_layout()
                (root / "P02").rename(root / bad_name)
                self.assert_rejected(root, 3, f"P-ID {bad_name!r}")

        # 空の root
        with self.subTest(case="空の root"):
            self.assert_rejected(self.new_dir(), 3, "空の root")

        # ⚠️★★★ 極の間のメタデータの不一致 (Codex TASK-PRE 指摘 7)
        mismatches = (
            ("provenance", "hmm_version", "0.1.0"),
            ("config", "hmm_version", "9.9.9"),
            ("config", "prereg_version", "1.0.1"),
            ("config", "prereg_sha256_prefix", "ffffffffffffffff"),
            ("config", "config_source", "file"),
            ("config", "overrides", [{"key": "q", "value": 0.995}]),
            ("provenance", "idle_trim", {"dropped_feat_rows": 3, "spans": [{"a_ms": 1, "b_ms": 3}]}),
            ("provenance", "input_gap_trim", {"dropped_feat_rows": 3, "spans": [{"a_ms": 1, "b_ms": 3}]}),
        )
        # ★ 1 極だけ `provenance.idle_trim` が欠ける / 形が壊れている封筒は拒否する (前処理の値を持つ封筒には必須)
        for label, broken in (
            ("欠ける", lambda env: env["provenance"].pop("idle_trim")),
            ("行数が負", lambda env: env["provenance"]["idle_trim"].__setitem__("dropped_feat_rows", -1)),
            ("spans の向きが逆", lambda env: env["provenance"]["idle_trim"].__setitem__("spans", [{"a_ms": 5, "b_ms": 4}])),
            # ★ v1.3 §7.1: `config.idle_trim_input_gap_ms` を持つ封筒は `provenance.input_gap_trim` も必須
            ("input_gap_trim が欠ける", lambda env: env["provenance"].pop("input_gap_trim")),
            ("input_gap_trim の行数が負", lambda env: env["provenance"]["input_gap_trim"].__setitem__("dropped_feat_rows", -1)),
        ):
            with self.subTest(idle_trim=label):
                root = self.base_layout()
                edit_envelope(root / "P01" / "s1" / "pointer_b.json", broken)
                self.assert_rejected(root, 3, f"idle_trim {label}")
        for section, key, value in mismatches:
            with self.subTest(mismatch=f"{section}.{key}"):
                root = self.base_layout()
                edit_envelope(root / "P01" / "s1" / "pointer_b.json", lambda env: env[section].__setitem__(key, value))
                self.assert_rejected(root, 3, f"{section}.{key}")
                # ★ 読み込み層は例外を投げる (CLI の exit 3 はこの例外から作られる)
                paths = {pole: root / "P01" / "s1" / f"{pole}.json" for pole in POLES}
                with self.assertRaises(fio.EnvelopeError):
                    fio.load_session(paths)

        # ⚠️★★★ 非有限の数値 (Python の json は NaN / Infinity を既定で受け付ける)
        for token in ("NaN", "Infinity", "-Infinity", "1e999"):
            for where in ("config", "row"):
                with self.subTest(non_finite=token, where=where):
                    root = self.base_layout()
                    path = root / "P01" / "s1" / "baseline.json"
                    text = path.read_text(encoding="utf-8")
                    target = '"q": 0.99' if where == "config" else '"iki_cv": 0.5'
                    replaced = text.replace(target, target.split(":")[0] + ": " + token, 1)
                    self.assertNotEqual(replaced, text)
                    path.write_text(replaced, encoding="utf-8")
                    self.assert_rejected(root, 3, f"非有限 {token} ({where})")

        # 壊れた封筒 (形・型が違う)
        def drop_top(key):
            return lambda env: env.pop(key)

        def set_config(key, value):
            return lambda env: env["config"].__setitem__(key, value)

        def drop_config(key):
            return lambda env: env["config"].pop(key)

        def set_first_onset_flag(value):
            return lambda env: env["rows"][0]["stall_onset"].__setitem__("is_onset", value)

        shape_cases = {
            "rows が無い": drop_top("rows"),
            "config が無い": drop_top("config"),
            "provenance が無い": drop_top("provenance"),
            "rows が配列でない": lambda env: env.__setitem__("rows", {}),
            "overrides が配列でない": set_config("overrides", {}),
            "overrides が無い": drop_config("overrides"),
            "pole_applicable が文字列": set_config("pole_applicable", "true"),
            "pole_applicable が 1": set_config("pole_applicable", 1),
            "適用可なのに理由がある": set_config("pole_not_applicable_reason", "no_pointer_rows"),
            "非適用なのに理由が無い": lambda env: env["config"].update(pole_applicable=False, pole_not_applicable_reason=None),
            "prereg_id が違う": set_config("prereg_id", "other"),
            "prereg_version が数": set_config("prereg_version", 1),
            "config_source が空": set_config("config_source", ""),
            "is_onset が 1": set_first_onset_flag(1),
            "is_onset が文字列": set_first_onset_flag("true"),
            "is_onset が null": set_first_onset_flag(None),
            "stall_onset が無い": lambda env: env["rows"][0].pop("stall_onset"),
            "行がオブジェクトでない": lambda env: env["rows"].__setitem__(0, 7),
        }
        for label, fn in shape_cases.items():
            with self.subTest(shape=label):
                root = self.base_layout()
                edit_envelope(root / "P01" / "s1" / "baseline.json", fn)
                self.assert_rejected(root, 3, label)

        # baseline は常に適用可 (非適用の baseline は封筒が壊れている)
        with self.subTest(shape="baseline が非適用"):
            root = self.base_layout()
            edit_envelope(
                root / "P01" / "s1" / "baseline.json",
                lambda env: env["config"].update(pole_applicable=False, pole_not_applicable_reason="no_pointer_rows"),
            )
            self.assert_rejected(root, 3, "baseline が非適用")

        # JSON として読めない (壊れ・空・トップが配列・UTF-8 でない)
        raw_cases = {
            "途中で切れた JSON": lambda text: text[: len(text) // 2].encode("utf-8"),
            "空ファイル": lambda text: b"",
            "トップが配列": lambda text: b"[]",
            "末尾に余計な文字": lambda text: (text + " garbage").encode("utf-8"),
            "UTF-8 でない": lambda text: b"\xff\xfe" + text.encode("utf-16-le"),
        }
        for label, fn in raw_cases.items():
            with self.subTest(raw=label):
                root = self.base_layout()
                path = root / "P02" / "s1" / "modifier_m_plus.json"
                path.write_bytes(fn(path.read_text(encoding="utf-8")))
                self.assert_rejected(root, 3, label)

        # ★ 形の不備 (exit 3) は凍結既定の検査 (exit 4) より先に拒否される
        with self.subTest(order="形の不備 + 非凍結"):
            root = self.base_layout()
            for pole in POLES:
                edit_envelope(root / "P01" / "s1" / f"{pole}.json", lambda env: env["config"].__setitem__("config_source", "file"))
            (root / "P02" / "s1" / "pointer_b.json").unlink()
            self.assert_rejected(root, 3, "形の不備 + 非凍結")

    def test_load_envelope_rejects_wrong_shape(self):
        # ★ 読み込み層を直接: 極の食い違い (ファイル名と中身) は EnvelopeError
        path = self.new_dir() / "baseline.json"
        path.write_text(json.dumps(make_envelope("baseline", 1)), encoding="utf-8")
        self.assertEqual(fio.load_envelope(path, "baseline")["config"]["pole"], "baseline")
        with self.assertRaises(fio.EnvelopeError):
            fio.load_envelope(path, "pointer_b")
        with self.assertRaises(fio.EnvelopeError):
            fio.load_envelope(self.tmp / "nowhere.json", "baseline")
        # ★ 射影も検証を素通りさせない
        broken = make_envelope("baseline", 1)
        broken["config"]["overrides"] = "none"
        with self.assertRaises(fio.EnvelopeError):
            fio.project_pg1(broken)

    def test_check_envelope_requires_trim_provenance_for_its_config_key(self):
        # ★ 1 枚の封筒を直接検査する (極の間の一致の検査を通さない)。⚠️ 3 極のうち 1 極だけを壊すと、
        #   極の間の不一致でも落ちるので、`config` に値があれば `provenance` も必須、という規則そのものを見られない。
        ok = make_envelope("baseline", 1)
        self.assertIs(fio.check_envelope(ok), ok)
        for config_key, trim_key in (("idle_trim_max_ms", "idle_trim"), ("idle_trim_input_gap_ms", "input_gap_trim")):
            for label, broken in (
                ("欠ける", lambda env, k=trim_key: env["provenance"].pop(k)),
                ("行数が負", lambda env, k=trim_key: env["provenance"][k].__setitem__("dropped_feat_rows", -1)),
                ("spans の向きが逆", lambda env, k=trim_key: env["provenance"][k].__setitem__("spans", [{"a_ms": 5, "b_ms": 4}])),
            ):
                with self.subTest(trim=trim_key, case=label):
                    env = make_envelope("baseline", 1)
                    broken(env)
                    with self.assertRaises(fio.EnvelopeError):
                        fio.check_envelope(env)
            # ★ 対照: 値を持たない旧い封筒には `provenance` を求めない
            with self.subTest(trim=trim_key, case="旧い封筒"):
                env = make_envelope("baseline", 1)
                env["config"].pop(config_key)
                env["provenance"].pop(trim_key)
                self.assertIs(fio.check_envelope(env), env)

    def test_discover_returns_sorted_layout(self):
        root = self.base_layout()
        found = fio.discover(root)
        self.assertEqual([(p, s) for p, s, _ in found], [("P01", "s1"), ("P01", "s2"), ("P02", "s1")])
        for _, _, paths in found:
            self.assertEqual(list(paths), list(POLES))
        # ★ P-ID の許容: 英数字・_・- (先頭は P)
        ok_root = self.new_dir()
        write_session(ok_root, "P_a-Z9", "any name", {})
        self.assertEqual(fio.discover(ok_root)[0][:2], ("P_a-Z9", "any name"))
        with self.assertRaises(fio.LayoutError):
            fio.discover(self.tmp / "nowhere")

    def test_rejects_non_frozen(self):
        # ★ 対照: 凍結既定なら通る
        self.run_ok(self.base_layout())

        def set_all_poles(session_dir, fn):
            for pole in POLES:
                edit_envelope(session_dir / f"{pole}.json", fn)

        def config_source_file(env):
            env["config"]["config_source"] = "file"

        def has_overrides(env):
            env["config"]["overrides"] = [{"key": "q", "value": 0.995}]

        def other_sha(env):
            env["config"]["prereg_sha256_prefix"] = "ffffffffffffffff"

        def other_version(env):
            env["config"]["prereg_version"] = "1.1.0"

        cases = {
            "全セッションが config_source=file": (("P01", "s1"), ("P01", "s2"), ("P02", "s1")),
            "1 セッションだけ config_source=file": (("P02", "s1"),),
        }
        for label, sessions in cases.items():
            with self.subTest(case=label):
                root = self.base_layout()
                for participant, session in sessions:
                    set_all_poles(root / participant / session, config_source_file)
                self.assert_rejected(root, 4, label)
        with self.subTest(case="overrides が非空 (3 極とも)"):
            root = self.base_layout()
            set_all_poles(root / "P01" / "s2", has_overrides)
            self.assert_rejected(root, 4, "overrides が非空")
        # ★ 凍結でも、別の版・別の sha のセッションが混ざれば拒否する (別の凍結値の出力を 1 つの分布にしない)
        with self.subTest(case="事前宣言の sha が混在"):
            root = self.base_layout()
            set_all_poles(root / "P02" / "s1", other_sha)
            self.assert_rejected(root, 4, "sha 混在")
        with self.subTest(case="事前宣言の版が混在"):
            root = self.base_layout()
            set_all_poles(root / "P01" / "s1", other_version)
            self.assert_rejected(root, 4, "版混在")
        # ★ 非適用の極のセッションも、凍結でなければ拒否する (適用可否に依らない)
        with self.subTest(case="非適用の極でも非凍結は拒否"):
            root = self.new_dir()
            write_session(root, "P01", "s1", {}, not_applicable=("pointer_b",))
            set_all_poles(root / "P01" / "s1", has_overrides)
            self.assert_rejected(root, 4, "非適用でも非凍結")

    def test_out_inside_git_rejected(self):
        root = self.base_layout()
        repo = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)  # ★ Windows は .git の読み取り専用で消せないことがある
        self.addCleanup(repo.cleanup)
        repo_dir = Path(repo.name)
        subprocess.run(["git", "init", "-q", str(repo_dir)], check=True, capture_output=True)

        # 作業ツリーの中 (直下・まだ無い深いディレクトリの下・.git の中) は exit 2 で、何も作らない
        for label, target in (
            ("直下", repo_dir / "pg1.json"),
            ("まだ無いディレクトリの下", repo_dir / "a" / "b" / "pg1.json"),
            (".git の中", repo_dir / ".git" / "pg1.json"),
        ):
            with self.subTest(out=label):
                rc, err = run_cli(root, target)
                self.assertEqual(rc, 2, err)
                self.assertFalse(target.exists())
        self.assertFalse((repo_dir / "a").exists())  # ★ 拒否するときにディレクトリを作らない

        # 対照: 管理外なら通る (⚠️ 上の拒否が「別の理由」で落ちていないことの裏づけ)
        outside = self.new_out()
        rc, err = run_cli(root, outside)
        self.assertEqual(rc, 0, err)

        # ⚠️★★★ 判定そのものが失敗したら、管理外とは見なさず拒否する (fail-closed)
        target = self.new_out()
        with mock.patch.object(pg1.subprocess, "run", side_effect=FileNotFoundError("git")):
            rc, err = run_cli(root, target)
        self.assertEqual(rc, 2, err)
        self.assertFalse(target.exists())
        dubious = subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="fatal: detected dubious ownership in repository at '/x'"
        )
        with mock.patch.object(pg1.subprocess, "run", return_value=dubious):
            rc, err = run_cli(root, target)
        self.assertEqual(rc, 2, err)
        self.assertFalse(target.exists())
        # ★ 「not a git repository」と言われたときだけ管理外と確定する
        not_a_repo = subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="fatal: not a git repository (or any of the parent directories): .git"
        )
        with mock.patch.object(pg1.subprocess, "run", return_value=not_a_repo):
            rc, err = run_cli(root, target)
        self.assertEqual(rc, 0, err)
        self.assertTrue(target.exists())

    def test_out_existing_and_root_guards(self):
        root = self.base_layout()
        existing = self.new_dir() / "pg1.json"
        existing.write_text("keep", encoding="utf-8")
        rc, err = run_cli(root, existing)
        self.assertEqual(rc, 2, err)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep")  # ★ 上書きしない
        rc, err = run_cli(root, self.new_dir())  # 既存のディレクトリ
        self.assertEqual(rc, 2, err)
        rc, err = run_cli(self.tmp / "nowhere", self.new_out())  # --root がディレクトリでない
        self.assertEqual(rc, 2, err)
        # ★ 引数の不備は argparse が exit 2
        err_buf = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err_buf):
            with self.assertRaises(SystemExit) as raised:
                pg1.main(["--root", str(root)])
        self.assertEqual(raised.exception.code, 2)

    def test_cli_process_exit_codes(self):
        # ★ 実プロセスとして回し、終了コードが本物であることを見る (⚠️ 標準出力・標準エラーは捕捉する)
        root = self.base_layout()
        env = {**os.environ, "PYTHONUTF8": "1"}

        def spawn(*args):
            return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, encoding="utf-8", env=env)

        out = self.new_out()
        done = spawn("--root", str(root), "--out", str(out))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(out.exists())
        self.assertIn("[pg1] OK", done.stdout)
        (root / "P02" / "s1" / "pointer_b.json").unlink()
        self.assertEqual(spawn("--root", str(root), "--out", str(self.new_out())).returncode, 3)
        self.assertEqual(spawn("--root", str(root)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
