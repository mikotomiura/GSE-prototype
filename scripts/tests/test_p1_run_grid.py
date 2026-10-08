"""Tests for scripts/p1_run_grid.py + scripts/run-features-all-poles.sh の `--` パススルー (探索格子の実行器・issue 004).

⚠️★★★ **規則を 1 つずつ固定する。** 特に:
- 格子は凍結 JSON から組む (27 + 5 = 32・ID は決定的)。全一式で `q` と `warmup_count` が対応表どおりに対になる。
- 規則 (d) は封筒 `config` の値で判定し、除外は「載せるだけ」(削除しない)。ほかの一式は載らない。
- PG-1 が宣言されていなければ `gse-replay` を **1 度も呼ばない** (exit 6)。
- manifest は最後に確定する (途中で失敗したら残らない)。

⚠️ 本 module は実データも Rust も読まない。`gse-replay` は**偽のコマンド**を `GSE_REPLAY_BIN` で差す
(★ `--set` を読んで最小の封筒を出す bash。実物の封筒の形は `scripts/tests/test_p1_pg1_distribution.py` が写している)。
本物の `gse-replay` に `--set` が届いて `config` に反映されることは `004-acceptance.sh` が実物で確かめる。
bash と jq が要る (`run-features-all-poles.sh` の前提)。

⚠️★ テスト名の行に `... ok` が同じ行に出ることを acceptance が見る。→ ★ テストに docstring を付けない
(verbose 出力が 2 行に割れる)。★ 標準出力・標準エラーは必ず捕捉する (行の途中に混ざると `... ok` が崩れる)。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_p1_run_grid -v
"""

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p1_bounds  # noqa: E402
import p1_run_grid as grid  # noqa: E402

POLES = p1_bounds.POLES
ALL_POLES_SCRIPT = SCRIPTS / "run-features-all-poles.sh"
FROZEN_PREREG = REPO_ROOT / "src-tauri" / "prereg" / "p1-episode.json"
_ABSENT = object()

# ★ 偽の gse-replay。`<ndjson> --features --pole <極> [--set <key>=<value>]...` を読み、最小の封筒を出す。
#   `FAKE_*` の環境変数で振る舞いを変える (★ 何も無ければ、渡された --set をそのまま `config` に映す忠実な偽物)。
#   - FAKE_CALL_LOG        : 呼ばれるたびに引数を 1 行追記する (⚠️ 「1 度も呼ばない」を検査するため)
#   - FAKE_FAIL_Q          : その q で呼ばれたら exit 1
#   - FAKE_SWAP_WARMUP_Q   : その q のとき `warmup_count` を 100 に取り違えて出す (--set は無視)
#   - FAKE_IGNORE_HOLE_GAP : `--set hole_gap_ms=` を無視して凍結値 (2000) を出す
#   - FAKE_HMM_FOR_Q       : その q のとき `hmm_version` を 9.9.9 にする (別の binary が混ざった状況)
FAKE_REPLAY = r"""#!/usr/bin/env bash
set -u
if [ -n "${FAKE_CALL_LOG:-}" ]; then printf '%s\n' "$*" >> "$FAKE_CALL_LOG"; fi
w_ms=30000; q=0.99; b_ms=30000; hole_gap_ms=2000; warmup_count=100; t1a_window_ms=30000; idle_trim_max_ms=1800000
pole=""
shift
while [ "$#" -gt 0 ]; do
  case "$1" in
    --features) shift ;;
    --pole) pole="$2"; shift 2 ;;
    --set)
      key="${2%%=*}"; val="${2#*=}"; shift 2
      case "$key" in
        w_ms) w_ms="$val" ;;
        q) q="$val" ;;
        b_ms) b_ms="$val" ;;
        hole_gap_ms) if [ "${FAKE_IGNORE_HOLE_GAP:-0}" != 1 ]; then hole_gap_ms="$val"; fi ;;
        warmup_count) warmup_count="$val" ;;
        t1a_window_ms) t1a_window_ms="$val" ;;
        idle_trim_max_ms) idle_trim_max_ms="$val" ;;
        *) echo "fake: unknown key ${key}" >&2; exit 1 ;;
      esac ;;
    *) echo "fake: unexpected arg $1" >&2; exit 1 ;;
  esac
done
if [ "${FAKE_FAIL_Q:-}" = "$q" ]; then exit 1; fi
if [ "${FAKE_SWAP_WARMUP_Q:-}" = "$q" ]; then warmup_count=100; fi
hmm=0.5.0
if [ "${FAKE_HMM_FOR_Q:-}" = "$q" ]; then hmm=9.9.9; fi
ov=""
add_ov() { if [ "$2" != "$3" ]; then ov="${ov:+$ov,}{\"key\":\"$1\",\"frozen\":$2,\"value\":$3}"; fi; }
add_ov w_ms 30000 "$w_ms"; add_ov q 0.99 "$q"; add_ov b_ms 30000 "$b_ms"
add_ov hole_gap_ms 2000 "$hole_gap_ms"; add_ov warmup_count 100 "$warmup_count"; add_ov t1a_window_ms 30000 "$t1a_window_ms"
add_ov idle_trim_max_ms 1800000 "$idle_trim_max_ms"
printf '{"provenance":{"hmm_version":"%s"},"config":{"w_ms":%s,"q":%s,"b_ms":%s,"hole_gap_ms":%s,"warmup_count":%s,"t1a_window_ms":%s,"idle_trim_max_ms":%s,"pole":"%s","pole_applicable":true,"pole_not_applicable_reason":null,"prereg_id":"p1-episode","prereg_version":"1.0.0","prereg_sha256_prefix":"0123456789abcdef","config_source":"frozen","overrides":[%s],"hmm_version":"%s"},"rows":[{"stall_onset":{"is_onset":false}}]}\n' \
  "$hmm" "$w_ms" "$q" "$b_ms" "$hole_gap_ms" "$warmup_count" "$t1a_window_ms" "$idle_trim_max_ms" "$pole" "$ov" "$hmm"
"""


def load_frozen():
    return json.loads(FROZEN_PREREG.read_text(encoding="utf-8"))


def load_frozen_text():
    return FROZEN_PREREG.read_text(encoding="utf-8")


def write_prereg(directory, pg1=3, mutate=None, name="prereg.json", text_edit=None):
    """凍結 JSON に `pg1` を足しただけの合成の prereg を書く (`pg1=_ABSENT` なら足さない)。"""
    data = load_frozen()
    if pg1 is not _ABSENT:
        data["pg1"] = {"min_episodes_per_participant": pg1}
    if mutate is not None:
        mutate(data)
    text = json.dumps(data)
    if text_edit is not None:
        text = text_edit(text)
    path = Path(directory) / name
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def make_fake_replay(directory):
    path = Path(directory) / "fake-gse-replay.sh"
    with open(path, "w", encoding="utf-8", newline="\n") as f:  # ⚠️ CRLF を混ぜない (bash が読めない)
        f.write(FAKE_REPLAY)
    os.chmod(path, 0o755)
    return path


def make_root(directory, layout=None):
    """`{P-ID: [session, ...]}` の入力ルートを作る (中身は何でもよい。偽の replay は読まない)。"""
    root = Path(directory) / "nd"
    for participant, sessions in (layout or {"P01": ["s1"]}).items():
        (root / participant).mkdir(parents=True)
        for session in sessions:
            (root / participant / f"{session}.ndjson").write_text('{"type":"meta"}\n', encoding="utf-8")
    return root


class GridCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)  # ★ system の temp の下 (git 管理外)
        self.fake = make_fake_replay(self.tmp)
        self.calls = self.tmp / "calls.log"
        self._n = 0

    def new_out(self):
        self._n += 1
        return self.tmp / f"out{self._n}"

    def env(self, **extra):
        return {"GSE_REPLAY_BIN": self.fake.as_posix(), "FAKE_CALL_LOG": self.calls.as_posix(), **extra}

    def call_lines(self):
        return self.calls.read_text(encoding="utf-8").splitlines() if self.calls.exists() else []

    def run_main(self, root, out, prereg=None, **fake_env):
        """CLI を同じプロセスで回し `(exit code, stdout, stderr)` を返す。⚠️ 標準出力・標準エラーは必ず捕捉する。"""
        argv = ["--ndjson-root", str(root), "--out", str(out)]
        if prereg is not None:
            argv += ["--prereg", str(prereg)]
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, self.env(**fake_env)), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                rc = grid.main(argv)
            except SystemExit as e:  # argparse の引数不備は exit 2
                rc = e.code
        return rc, stdout.getvalue(), stderr.getvalue()

    def assert_refused(self, rc_expected, root, out, prereg, label, **fake_env):
        """拒否 = 期待の exit code・`gse-replay` を 1 度も呼ばない・出力先を作らない。"""
        rc, _, err = self.run_main(root, out, prereg, **fake_env)
        self.assertEqual(rc, rc_expected, f"{label}: {err}")
        self.assertEqual(self.call_lines(), [], f"{label}: 拒否したのに gse-replay が呼ばれた")
        self.assertFalse(Path(out).exists(), f"{label}: 拒否したのに出力先が作られた")
        return err

    def subset(self, prereg_path, predicate):
        prereg, _ = grid.load_prereg(prereg_path)
        return [config for config in grid.build_grid(prereg) if predicate(config)]

    def run_subset(self, configs, root, out, prereg_path, source="file", sha=None, **fake_env):
        """格子の一部だけを `run_grid` で回す (★ CLI の全 32 一式を回すと遅い)。`(manifest or None, RunError or None)`。"""
        if sha is None:
            _, sha = grid.load_prereg(prereg_path)
        sessions = grid.list_sessions(root)
        with mock.patch.dict(os.environ, self.env(**fake_env)), contextlib.redirect_stdout(io.StringIO()):
            try:
                return grid.run_grid(configs, sessions, Path(out), source, sha, grid.find_bash()), None
            except grid.RunError as e:
                return None, e


class RuleDTableTest(unittest.TestCase):
    def test_rule_d_table(self):
        valid = grid.is_valid_search_run
        # ★ 対応表どおり
        self.assertEqual(grid.WARMUP_BY_Q, {Decimal("0.99"): 100, Decimal("0.995"): 200, Decimal("0.999"): 1000})
        for q, warmup in ((0.99, 100), (0.995, 200), (0.999, 1000)):
            self.assertTrue(valid({"q": q, "warmup_count": warmup}), (q, warmup))
        # ★ 対になっていない実行は偽 (v1.1 (5): 片方だけを変えた実行は「従属」を破っている)
        self.assertFalse(valid({"q": 0.995, "warmup_count": 100}))
        self.assertFalse(valid({"q": 0.99, "warmup_count": 200}))
        self.assertFalse(valid({"q": 0.999, "warmup_count": 200}))
        # ★ 表に無い q は探索空間の外 (⚠️ 倍精度で式を評価すると ⌈1/(1−q)⌉ が 1 ずれうる q)
        self.assertFalse(valid({"q": 0.9999, "warmup_count": 10000}))
        self.assertFalse(valid({"q": 0.9999, "warmup_count": 10001}))
        self.assertFalse(valid({"q": Decimal("0.9999"), "warmup_count": 10000}))
        # ★ `0.990` と `0.99` は同じ扱い (float でも Decimal でも JSON 由来の文字列 → 数でも)
        self.assertTrue(valid({"q": Decimal("0.990"), "warmup_count": 100}))
        self.assertTrue(valid({"q": float("0.990"), "warmup_count": 100}))
        self.assertTrue(valid(json.loads('{"q": 0.9950, "warmup_count": 200}')))
        self.assertTrue(valid(json.loads('{"q": 0.9950, "warmup_count": 200}', parse_float=Decimal)))
        # ⚠️ 型の違うものは偽 (bool は int の subclass・整数でない warmup・文字列の q・キーが無い・dict でない)
        self.assertFalse(valid({"q": True, "warmup_count": 100}))
        self.assertFalse(valid({"q": 0.99, "warmup_count": True}))
        self.assertFalse(valid({"q": 0.99, "warmup_count": 100.0}))
        self.assertFalse(valid({"q": 0.99, "warmup_count": "100"}))
        self.assertFalse(valid({"q": "0.99", "warmup_count": 100}))
        self.assertFalse(valid({"q": None, "warmup_count": 100}))
        self.assertFalse(valid({"q": float("nan"), "warmup_count": 100}))
        self.assertFalse(valid({"q": 0.99}))
        self.assertFalse(valid({"warmup_count": 100}))
        self.assertFalse(valid({}))
        self.assertFalse(valid(None))
        self.assertFalse(valid([0.99, 100]))
        # ★ 対応表は十進で厳密な ⌈1/(1−q)⌉ と一致する (⚠️ 表の書き間違いを検出する)
        for q, warmup in grid.WARMUP_BY_Q.items():
            ratio = Decimal(1) / (Decimal(1) - q)
            self.assertEqual(ratio, ratio.to_integral_value(), q)  # 割り切れる
            self.assertEqual(int(ratio), warmup, q)


class GridBuildTest(unittest.TestCase):
    def prereg_with_pg1(self):
        prereg, _ = grid.load_prereg(_write_tmp_prereg(self))
        return prereg

    def test_grid_has_32_configs(self):
        prereg = self.prereg_with_pg1()
        configs = grid.build_grid(prereg)
        ids = [config["id"] for config in configs]
        self.assertEqual(len(configs), 32)
        self.assertEqual(len(set(ids)), 32, "ID が重複している")
        self.assertEqual([config["kind"] for config in configs], ["selection"] * 27 + ["sensitivity"] * 5)
        # ★ 決定的: 何度組んでも同じ順・同じ ID
        self.assertEqual(ids, [config["id"] for config in grid.build_grid(prereg)])
        # ★ 選択 27 = q × hole_gap_ms × t1a_window_ms の全探索 (JSON の並び順・q が最も遅く動く)
        expected_selection = [
            f"sel__q={q}__hole_gap_ms={hole}__t1a_window_ms={window}"
            for q in ("0.99", "0.995", "0.999")
            for hole in (2000, 3000, 5000)
            for window in (15000, 30000, 60000)
        ]
        self.assertEqual(ids[:27], expected_selection)
        self.assertIn("sel__q=0.995__hole_gap_ms=3000__t1a_window_ms=15000", ids)
        # ★ 感度 5 = w_ms / b_ms を運用値 (30000) のまわりで OFAT ＋ idle_trim_max_ms=0 (前処理なし・事前宣言 v1.2 §6.3)
        #   (⚠️ 運用値そのものは入れない・Cartesian に組まない)
        self.assertEqual(
            ids[27:],
            ["ofat__w_ms=15000", "ofat__w_ms=60000", "ofat__b_ms=15000", "ofat__b_ms=60000", "ofat__idle_trim_max_ms=0"],
        )
        # ★ 値をコードに書き写していない: 凍結 JSON を変えれば格子が変わる
        smaller = json.loads(json.dumps(load_frozen()))
        smaller["search_space"]["hole_gap_ms"] = [2000, 3000]
        smaller["pg1"] = {"min_episodes_per_participant": 3}
        smaller_prereg, _ = grid.load_prereg(_write_json_tmp(self, smaller))
        self.assertEqual(len(grid.build_grid(smaller_prereg)), 18 + 5)

    def test_warmup_paired_with_q(self):
        configs = grid.build_grid(self.prereg_with_pg1())
        table = {"0.99": 100, "0.995": 200, "0.999": 1000}
        for config in configs:
            params = config["params"]
            self.assertEqual(sorted(params), sorted(grid.TUNABLE_KEYS), config["id"])
            if config["kind"] == "selection":
                q_text = config["id"].split("__")[1].split("=")[1]
                self.assertEqual(params["warmup_count"], table[q_text], config["id"])
                self.assertEqual(params["q"], Decimal(q_text), config["id"])
                # 選択でない 2 キーは運用値
                self.assertEqual((params["w_ms"], params["b_ms"]), (30000, 30000), config["id"])
            else:
                # ★ 感度 5 は運用値の 100 (q は運用値の 0.99)
                self.assertEqual(params["warmup_count"], 100, config["id"])
                self.assertEqual(params["q"], Decimal("0.99"), config["id"])
                self.assertEqual((params["hole_gap_ms"], params["t1a_window_ms"]), (2000, 30000), config["id"])
            # ★ `--set` の引数: 7 キーすべて・`q` と `warmup_count` は同じ呼び出しで対になる
            args = grid.set_args(params)
            self.assertEqual(args[0], "--")
            pairs = [args[i + 1] for i in range(1, len(args), 2)]
            self.assertEqual([p.split("=")[0] for p in pairs], list(grid.TUNABLE_KEYS))
            self.assertIn(f"q={params['q']}", pairs)
            self.assertIn(f"warmup_count={table[str(params['q'])]}", pairs)
            self.assertTrue(all(args[i] == "--set" for i in range(1, len(args), 2)))

    def test_grid_shape_errors_are_refused(self):
        # ⚠️ 対応表に無い q が search_space にあれば格子を作らない (exit 3 の元)
        def add_q(data):
            data["search_space"]["q"].append(0.9999)

        with self.assertRaises(grid.GridError):
            grid.build_grid(_load(self, add_q))
        # ⚠️ 形が想定と違えば作らない (JSON は直さない)
        def selection_untunable(data):
            data["search_roles"]["net_diff_min"] = "selection"

        def warmup_not_derived(data):
            data["search_roles"]["warmup_count"] = "selection"

        def missing_role(data):
            del data["search_roles"]["hole_gap_ms"]

        def bad_operational_warmup(data):
            data["operational"]["warmup_count"] = 200

        def operational_not_in_space(data):
            data["operational"]["hole_gap_ms"] = 2500

        def fixed_differs(data):
            data["search_space"]["net_diff_min"] = [1, 2]

        def duplicate_values(data):
            data["search_space"]["hole_gap_ms"] = [2000, 2000, 5000]

        def bool_value(data):
            data["search_space"]["hole_gap_ms"] = [2000, True]

        # ★ 0 を許すのは `idle_trim_max_ms` だけ (事前宣言 v1.2 §6.4)。負・bool は拒否し、
        #   ほかのキーの 0 は従来どおり拒否する (code-reviewer L-8 の陰性対照)。
        def idle_trim_negative(data):
            data["search_space"]["idle_trim_max_ms"] = [-1, 1800000]

        def idle_trim_bool(data):
            data["search_space"]["idle_trim_max_ms"] = [True, 1800000]

        def zero_elsewhere(data):
            data["search_space"]["w_ms"] = [0, 30000]

        for mutate in (
            idle_trim_negative,
            idle_trim_bool,
            zero_elsewhere,
            selection_untunable,
            warmup_not_derived,
            missing_role,
            bad_operational_warmup,
            operational_not_in_space,
            fixed_differs,
            duplicate_values,
            bool_value,
        ):
            with self.assertRaises(grid.GridError, msg=mutate.__name__):
                grid.build_grid(_load(self, mutate))
        with self.assertRaises(grid.GridError):
            grid.build_grid({})

    def test_q_written_with_trailing_zero_gives_the_same_grid(self):
        # ★ `0.990` と `0.99` を同じに扱う (JSON を Decimal で読み、normalize した文字列で対応表を引く)
        plain = [c["id"] for c in grid.build_grid(self.prereg_with_pg1())]
        path = write_prereg(Path(_tmpdir(self)), text_edit=lambda text: text.replace("0.99,", "0.990,"))
        self.assertIn("0.990", path.read_text(encoding="utf-8"))
        prereg, _ = grid.load_prereg(path)
        self.assertEqual([c["id"] for c in grid.build_grid(prereg)], plain)

    def test_pg1_value_must_be_a_positive_int(self):
        for value in (0, -1, True, False, "3", 2.5, 3.0, None, [3], {"x": 3}):
            path = write_prereg(Path(_tmpdir(self)), pg1=value)
            prereg, _ = grid.load_prereg(path)
            with self.assertRaises(grid.Pg1UndeclaredError, msg=repr(value)):
                grid.declared_pg1_min(prereg)
        for prereg in (load_frozen(), {"pg1": None}, {"pg1": []}, {"pg1": {}}, {"pg1": {"other": 3}}):
            with self.assertRaises(grid.Pg1UndeclaredError, msg=repr(prereg)[:60]):
                grid.declared_pg1_min(prereg)
        self.assertEqual(grid.declared_pg1_min({"pg1": {"min_episodes_per_participant": 1}}), 1)

    def test_default_prereg_is_the_frozen_json(self):
        path, source = grid.resolve_prereg(None)
        self.assertEqual((path.resolve(), source), (FROZEN_PREREG.resolve(), "frozen"))
        self.assertEqual(grid.resolve_prereg("x.json"), (Path("x.json"), "file"))


def _tmpdir(case):
    tmp = tempfile.TemporaryDirectory()
    case.addCleanup(tmp.cleanup)
    return tmp.name


def _write_tmp_prereg(case):
    return write_prereg(Path(_tmpdir(case)))


def _write_json_tmp(case, data):
    path = Path(_tmpdir(case)) / "p.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _load(case, mutate):
    data = load_frozen()
    data["pg1"] = {"min_episodes_per_participant": 3}
    mutate(data)
    prereg, _ = grid.load_prereg(_write_json_tmp(case, data))
    return prereg


class GridRunTest(GridCase):
    """偽の gse-replay で実際に回す。⚠️ 全 32 一式の実行は 1 回だけ (`setUpClass`)・残りは一部の一式だけ回す。"""

    full = None

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.full_tmp = Path(tmp.name)
        fake = make_fake_replay(cls.full_tmp)
        calls = cls.full_tmp / "calls.log"
        root = make_root(cls.full_tmp, {"P01": ["s1"], "P02": ["a-1"]})
        prereg = write_prereg(cls.full_tmp)
        out = cls.full_tmp / "out"
        argv = ["--ndjson-root", str(root), "--out", str(out), "--prereg", str(prereg)]
        stdout, stderr = io.StringIO(), io.StringIO()
        env = {"GSE_REPLAY_BIN": fake.as_posix(), "FAKE_CALL_LOG": calls.as_posix()}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = grid.main(argv)
        manifest_path = out / grid.MANIFEST_NAME
        cls.full = {
            "rc": rc,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
            "out": out,
            "manifest": json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None,
            "calls": calls.read_text(encoding="utf-8").splitlines() if calls.exists() else [],
            "prereg": prereg,
        }

    def test_full_run_writes_a_complete_verified_manifest(self):
        full = self.full
        self.assertEqual(full["rc"], 0, full["stderr"])
        manifest = full["manifest"]
        self.assertIs(manifest["complete"], True)
        self.assertEqual(manifest["tool"], "p1_run_grid")
        self.assertEqual(manifest["prereg_source"], "file")
        self.assertEqual(
            manifest["prereg_sha256_prefix"], hashlib.sha256(full["prereg"].read_bytes()).hexdigest()[:16]
        )
        self.assertEqual((manifest["n_participants"], manifest["n_sessions"]), (2, 2))
        self.assertEqual(manifest["sessions"], [{"participant": "P01", "session": "s1"}, {"participant": "P02", "session": "a-1"}])
        self.assertEqual(len(manifest["configs"]), 32)
        self.assertEqual(
            manifest["envelope_identity"],
            {
                "prereg_version": "1.0.0",
                "prereg_sha256_prefix": "0123456789abcdef",
                "hmm_version": "0.5.0",
                "provenance_hmm_version": "0.5.0",
                "config_source": "frozen",
            },
        )
        # ★ 忠実な偽物なら、除外は 1 件も無い (⚠️ 規則 (d) が正しい実行を除外していないこと)
        self.assertEqual(manifest["excluded_rule_d"], [])
        # ★ 32 一式 × 2 セッション × 3 極 = 192 ファイル・全部に sha256・実物と一致
        self.assertEqual(len(manifest["outputs"]), 32 * 2 * 3)
        on_disk = sorted(
            p.relative_to(full["out"]).as_posix() for p in full["out"].rglob("*.json") if p.name != grid.MANIFEST_NAME
        )
        self.assertEqual(sorted(o["path"] for o in manifest["outputs"]), on_disk)
        for output in manifest["outputs"]:
            actual = hashlib.sha256((full["out"] / output["path"]).read_bytes()).hexdigest()
            self.assertEqual(output["sha256"], actual, output["path"])
        self.assertEqual(
            sorted(p.name for p in full["out"].iterdir() if p.name != grid.MANIFEST_NAME),
            sorted(c["id"] for c in manifest["configs"]),
        )
        # ★ 一時名の manifest が残っていない・パラメータは 7 キー (q は数のまま)
        self.assertFalse((full["out"] / (grid.MANIFEST_NAME + ".tmp")).exists())
        by_id = {c["id"]: c["params"] for c in manifest["configs"]}
        self.assertEqual(
            by_id["sel__q=0.995__hole_gap_ms=3000__t1a_window_ms=15000"],
            {"w_ms": 30000, "q": 0.995, "b_ms": 30000, "hole_gap_ms": 3000, "warmup_count": 200, "t1a_window_ms": 15000, "idle_trim_max_ms": 1800000},
        )
        # ★ gse-replay は 32 一式 × 2 セッション × 3 極 = 192 回・全部に q と warmup_count が対で渡る
        self.assertEqual(len(full["calls"]), 32 * 2 * 3)
        for line in full["calls"]:
            self.assertRegex(line, r"--set q=(0\.99|0\.995|0\.999) .*--set warmup_count=(100|200|1000) ", line)
        self.assertEqual(sum("--set q=0.995 " in line and "--set warmup_count=200 " in line for line in full["calls"]), 9 * 2 * 3)
        self.assertFalse(any("--set q=0.995 " in line and "warmup_count=100 " in line for line in full["calls"]))

    def test_rule_d_excludes_mismatched_runs(self):
        prereg = write_prereg(self.tmp)
        root = make_root(self.tmp)
        # 対象: q=0.995 の 2 一式 (hole_gap_ms が違う) ＋ ほかの q の 2 一式 + 感度 1 つ
        wanted = {
            "sel__q=0.99__hole_gap_ms=2000__t1a_window_ms=30000",
            "sel__q=0.995__hole_gap_ms=2000__t1a_window_ms=30000",
            "sel__q=0.995__hole_gap_ms=3000__t1a_window_ms=15000",
            "sel__q=0.999__hole_gap_ms=5000__t1a_window_ms=60000",
            "ofat__w_ms=15000",
        }
        configs = self.subset(prereg, lambda c: c["id"] in wanted)
        self.assertEqual(len(configs), len(wanted))
        # ⚠️ 偽の replay が q=0.995 のとき warmup_count を 100 に取り違える
        out = self.new_out()
        manifest, error = self.run_subset(configs, root, out, prereg, FAKE_SWAP_WARMUP_Q="0.995")
        self.assertIsNone(error)
        excluded = manifest["excluded_rule_d"]
        expected = sorted(
            (config_id, pole)
            for config_id in wanted
            if "q=0.995" in config_id
            for pole in POLES
        )
        self.assertEqual(sorted((e["config_id"], e["pole"]) for e in excluded), expected)
        for entry in excluded:
            self.assertEqual(entry["reasons"], ["rule_d", "param_mismatch"], entry)
            self.assertEqual(entry["mismatch"], {"warmup_count": {"observed": 100, "intended": 200}}, entry)
            self.assertEqual((entry["participant"], entry["session"]), ("P01", "s1"))
        # ★ 除外は載せるだけ: ファイルは削除しない・manifest の outputs にも残る
        self.assertEqual(len(manifest["outputs"]), len(wanted) * 3)
        for config_id in wanted:
            for pole in POLES:
                self.assertTrue((out / config_id / "P01" / "s1" / f"{pole}.json").is_file())

        # ⚠️ ★ 別の型の食い違い: hole_gap_ms を無視する replay。q と warmup は対になっているので規則 (d) は満たすが、
        #   意図したパラメータと config が違う → param_mismatch だけが載る (⚠️ 運用値と同じ hole_gap_ms=2000 の一式は載らない)
        out2 = self.new_out()
        manifest2, error2 = self.run_subset(configs, root, out2, prereg, FAKE_IGNORE_HOLE_GAP="1")
        self.assertIsNone(error2)
        by_config = {}
        for entry in manifest2["excluded_rule_d"]:
            by_config.setdefault(entry["config_id"], []).append(entry)
        self.assertEqual(
            sorted(by_config),
            ["sel__q=0.995__hole_gap_ms=3000__t1a_window_ms=15000", "sel__q=0.999__hole_gap_ms=5000__t1a_window_ms=60000"],
        )
        for entries in by_config.values():
            self.assertEqual(sorted(e["pole"] for e in entries), sorted(POLES))
            for entry in entries:
                self.assertEqual(entry["reasons"], ["param_mismatch"], entry)
                self.assertEqual(list(entry["mismatch"]), ["hole_gap_ms"], entry)
                self.assertEqual(entry["mismatch"]["hole_gap_ms"]["observed"], 2000)

        # ★ 陽性対照: 忠実な偽物では何も除外されない (⚠️ 上の 2 件が「常に何かを除外する実装」で通らないこと)
        out3 = self.new_out()
        manifest3, error3 = self.run_subset(configs, root, out3, prereg)
        self.assertIsNone(error3)
        self.assertEqual(manifest3["excluded_rule_d"], [])

    def test_manifest_complete_only_on_success(self):
        # ★ 成功: 全 32 一式の run (setUpClass) で manifest が complete: true・sha256 が実物と一致 (別 test が全件検査)
        self.assertIs(self.full["manifest"]["complete"], True)
        # ⚠️ 途中 (q=0.995 の最初の一式) で 3 極スクリプトが失敗した実行: exit 1・complete の manifest を残さない
        prereg = write_prereg(self.tmp)
        root = make_root(self.tmp)
        out = self.new_out()
        rc, _, err = self.run_main(root, out, prereg, FAKE_FAIL_Q="0.995")
        self.assertEqual(rc, 1, err)
        self.assertFalse((out / grid.MANIFEST_NAME).exists(), "失敗した実行に manifest が残っている")
        self.assertFalse((out / (grid.MANIFEST_NAME + ".tmp")).exists())
        self.assertIn("q=0.99 ", self.call_lines()[0], "失敗の前に成功した実行があるはず (★ 途中で失敗した状況を作れていない)")
        done = [p.name for p in out.iterdir()]
        self.assertEqual(len(done), 9 + 1, done)  # q=0.99 の 9 一式 + 失敗した最初の q=0.995 の一式
        self.assertTrue(any((out / name / "P01" / "s1" / "baseline.json").is_file() for name in done), "出力が途中まで出来ている状況にならない")
        # ⚠️ 使い回し拒否: 途中で失敗した out へ再実行しない (出力が 1 つでもあれば空でない → exit 2)
        rc2, _, err2 = self.run_main(root, out, prereg)
        self.assertEqual(rc2, 2, err2)
        # ⚠️ 読み直しの段階で失敗する場合 (別の binary が混ざった格子: hmm_version が 1 通りでない): 同じく manifest を残さない
        out2 = self.new_out()
        configs = self.subset(prereg, lambda c: c["id"].startswith("sel__q=0.99__hole_gap_ms=2000") or "q=0.995__hole_gap_ms=2000" in c["id"])
        manifest, error = self.run_subset(configs, root, out2, prereg, FAKE_HMM_FOR_Q="0.995")
        self.assertIsNone(manifest)
        self.assertIn("identity", str(error))
        self.assertFalse((out2 / grid.MANIFEST_NAME).exists())
        self.assertFalse((out2 / (grid.MANIFEST_NAME + ".tmp")).exists())
        # ⚠️ 出力を書き換えた後の読み直し: 封筒が壊れていたら manifest を残さない (3 極スクリプトの後に壊れた状況)
        out3 = self.new_out()
        ok_configs = self.subset(prereg, lambda c: c["id"] == "ofat__w_ms=15000")
        real_run_poles = grid.run_poles

        def corrupt_after(bash, ndjson, outdir, params):
            real_run_poles(bash, ndjson, outdir, params)
            (Path(outdir) / "pointer_b.json").write_text("{not json", encoding="utf-8")

        with mock.patch.object(grid, "run_poles", corrupt_after):
            manifest3, error3 = self.run_subset(ok_configs, root, out3, prereg)
        self.assertIsNone(manifest3)
        self.assertIn("封筒", str(error3))
        self.assertFalse((out3 / grid.MANIFEST_NAME).exists())

    def test_frozen_source_requires_envelope_hash_match(self):
        # ⚠️★★★ 凍結 JSON 由来（source=frozen）の格子は、実行した gse-replay の封筒の prereg hash と一致しなければならない
        #   （★ 凍結 JSON に PG-1 を足した後で gse-replay を作り直さないと、古い刻印の封筒で新しい格子を回してしまう）
        prereg = write_prereg(self.tmp)
        root = make_root(self.tmp)
        configs = self.subset(prereg, lambda c: c["id"] == "ofat__w_ms=15000")
        fake_sha = "0123456789abcdef"  # 偽の replay が封筒に刻む hash
        # ★ 対照: 一致すれば frozen でも通る（下の拒否が別の理由でないことの裏づけ）
        manifest, error = self.run_subset(configs, root, self.new_out(), prereg, source="frozen", sha=fake_sha)
        self.assertIsNone(error, error)
        self.assertIs(manifest["complete"], True)
        # ⚠️ 食い違い → 拒否・manifest を残さない
        out = self.new_out()
        manifest, error = self.run_subset(configs, root, out, prereg, source="frozen", sha="fedcba9876543210")
        self.assertIsNone(manifest)
        self.assertIn("食い違う", str(error))
        self.assertFalse((out / grid.MANIFEST_NAME).exists())
        # ★ `--prereg` で差し替えた実行（file）は食い違って当然なので通し、manifest に両方の hash を残す
        manifest, error = self.run_subset(configs, root, self.new_out(), prereg, source="file", sha="fedcba9876543210")
        self.assertIsNone(error, error)
        self.assertEqual(
            (manifest["prereg_sha256_prefix"], manifest["envelope_identity"]["prereg_sha256_prefix"]),
            ("fedcba9876543210", fake_sha),
        )

    def test_refuses_without_pg1(self):
        root = make_root(self.tmp)
        cases = {
            "pg1 が無い (現行の凍結 JSON に足さない)": _ABSENT,
            "0": 0,
            "-1": -1,
            "true": True,
            "false": False,
            '"3"': "3",
            "2.5": 2.5,
            "3.0": 3.0,
            "null": None,
        }
        for label, value in cases.items():
            prereg = write_prereg(self.tmp, pg1=value, name="p.json")
            err = self.assert_refused(6, root, self.new_out(), prereg, label)
            self.assertIn("PG-1", err, label)
            os.remove(prereg)
        # ⚠️ pg1 が dict でない・キーが違う
        for label, mutate in (
            ("pg1 = []", lambda d: d.update(pg1=[])),
            ("pg1 = {}", lambda d: d.update(pg1={})),
            ("別のキー", lambda d: d.update(pg1={"min_episodes": 3})),
        ):
            prereg = write_prereg(self.tmp, pg1=_ABSENT, mutate=mutate, name="p.json")
            self.assert_refused(6, root, self.new_out(), prereg, label)
            os.remove(prereg)
        # ★ 現行の凍結 JSON そのもの (既定の読み先・`--prereg` なし) は pg1 を持たない → 必ず exit 6。
        #   ⚠️ v1.2 が凍結 JSON に pg1 を宣言したらここは落ちる (★ その時に、この期待と 004-acceptance.sh の AC5 を見直す)
        self.assertNotIn("pg1", load_frozen(), "凍結 JSON が pg1 を持った (★ 004 / 005 の既定の読み先を見直す時)")
        self.assert_refused(6, root, self.new_out(), None, "既定の凍結 JSON")
        # ★ 陽性対照: 正しい pg1 の同じ prereg では replay が呼ばれ、実行が進む (⚠️ 上が「常に拒否」で通っていないこと)
        self.assertEqual(self.full["rc"], 0)
        self.assertGreater(len(self.full["calls"]), 0)

    def test_guards(self):
        no_pg1 = write_prereg(self.tmp, pg1=_ABSENT, name="no_pg1.json")  # ★ ガードが破れても、exit 6 で止まり何も書かない
        root = make_root(self.tmp)
        ok_root = root  # ★ 以降の「レイアウト以外の拒否」では、入力は正しいものを使う
        # ⚠️ --out が git の作業ツリーの中 → exit 2 (★ まだ無いパス・既存のディレクトリの両方)
        inside = REPO_ROOT / "_p1_grid_guard_probe" / "out"
        self.assert_refused(2, root, inside, no_pg1, "--out が repo の中 (未作成)")
        self.assertFalse((REPO_ROOT / "_p1_grid_guard_probe").exists())
        self.assert_refused(2, root, SCRIPTS / "_p1_grid_guard_probe_out", no_pg1, "--out が scripts/ の中")
        # ⚠️ --out が空でない → exit 2 (使い回し拒否)
        used = self.new_out()
        used.mkdir()
        (used / "stale.txt").write_text("x", encoding="utf-8")
        rc, _, err = self.run_main(root, used, no_pg1)
        self.assertEqual(rc, 2, err)
        self.assertEqual([p.name for p in used.iterdir()], ["stale.txt"])
        # ⚠️ --out がファイル → exit 2
        as_file = self.new_out()
        as_file.write_text("x", encoding="utf-8")
        rc, _, err = self.run_main(root, as_file, no_pg1)
        self.assertEqual(rc, 2, err)
        # ★ 陽性対照: 空の既存ディレクトリ・まだ無いパスはガードを通る (→ PG-1 の段階まで進んで exit 6)
        empty = self.new_out()
        empty.mkdir()
        rc, _, err = self.run_main(root, empty, no_pg1)
        self.assertEqual((rc, list(empty.iterdir())), (6, []), err)
        self.assert_refused(6, root, self.new_out(), no_pg1, "まだ無いパス")
        # ⚠️ --ndjson-root のレイアウト違反 → exit 2
        def bad_root(name, build):
            base = self.tmp / name
            build(base)
            return base

        def nothing(base):
            base.mkdir()

        def stray_file(base):
            (base / "P01").mkdir(parents=True)
            (base / "P01" / "s1.ndjson").write_text("x", encoding="utf-8")
            (base / "README.txt").write_text("x", encoding="utf-8")

        def bad_p_id(base):
            (base / "X01").mkdir(parents=True)
            (base / "X01" / "s1.ndjson").write_text("x", encoding="utf-8")

        def not_ndjson(base):
            (base / "P01").mkdir(parents=True)
            (base / "P01" / "s1.ndjson").write_text("x", encoding="utf-8")
            (base / "P01" / "notes.txt").write_text("x", encoding="utf-8")

        def empty_participant(base):
            (base / "P01").mkdir(parents=True)

        def bad_session_name(base):
            (base / "P01").mkdir(parents=True)
            (base / "P01" / "a b.ndjson").write_text("x", encoding="utf-8")

        def nested(base):
            (base / "P01" / "sub").mkdir(parents=True)
            (base / "P01" / "sub" / "s1.ndjson").write_text("x", encoding="utf-8")

        for name, build in (
            ("empty_root", nothing),
            ("stray_file", stray_file),
            ("bad_p_id", bad_p_id),
            ("not_ndjson", not_ndjson),
            ("empty_participant", empty_participant),
            ("bad_session_name", bad_session_name),
            ("nested", nested),
        ):
            self.assert_refused(2, bad_root(name, build), self.new_out(), no_pg1, name)
        self.assert_refused(2, self.tmp / "no_such_root", self.new_out(), no_pg1, "root が無い")
        # ⚠️ --prereg を読めない → exit 2・bash が無い → exit 2
        self.assert_refused(2, ok_root, self.new_out(), self.tmp / "no_such_prereg.json", "prereg が無い")
        with mock.patch.object(grid.shutil, "which", return_value=None):
            self.assert_refused(2, ok_root, self.new_out(), no_pg1, "bash が無い")
        # ⚠️ 対応表に無い q を持つ prereg → exit 3 (★ pg1 は宣言済み・格子を作らず replay を 1 度も呼ばない)
        def add_q(data):
            data["search_space"]["q"].append(0.9999)

        err = self.assert_refused(3, ok_root, self.new_out(), write_prereg(self.tmp, mutate=add_q, name="bad_q.json"), "対応表に無い q")
        self.assertIn("0.9999", err)
        # ⚠️ prereg が JSON でない・オブジェクトでない・形が違う → exit 3
        broken = self.tmp / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        self.assert_refused(3, ok_root, self.new_out(), broken, "JSON でない")
        as_list = self.tmp / "list.json"
        as_list.write_text("[1, 2]", encoding="utf-8")
        self.assert_refused(3, ok_root, self.new_out(), as_list, "オブジェクトでない")
        nan = self.tmp / "nan.json"
        nan.write_text('{"pg1": {"min_episodes_per_participant": NaN}}', encoding="utf-8")
        self.assert_refused(3, ok_root, self.new_out(), nan, "NaN を含む")
        self.assert_refused(3, ok_root, self.new_out(), write_prereg(self.tmp, pg1=3, mutate=lambda d: d.pop("search_roles"), name="no_roles.json"), "search_roles が無い")
        # ⚠️ 引数の不備は exit 2 (argparse)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                grid.main([])
        self.assertEqual(raised.exception.code, 2)

    def run_script(self, in_path, outdir, *extra, **env):
        result = subprocess.run(
            ["bash", ALL_POLES_SCRIPT.as_posix(), Path(in_path).as_posix(), Path(outdir).as_posix(), *extra],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            env={**os.environ, **self.env(**env)},
        )
        return result.returncode, result.stderr

    def run_script_raw(self, in_path, outdir, printf_value):
        """`--set` の値を bash の中で `printf %b` して渡す (★ `\\n` が実際の改行になる)。"""
        result = subprocess.run(
            [
                "bash",
                "-c",
                'exec bash "$0" "$1" "$2" -- --set "$(printf %b "$3")"',
                ALL_POLES_SCRIPT.as_posix(),
                Path(in_path).as_posix(),
                Path(outdir).as_posix(),
                printf_value,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            env={**os.environ, **self.env()},
        )
        return result.returncode, result.stderr

    def test_all_poles_passthrough_whitelist(self):
        ndjson = make_root(self.tmp) / "P01" / "s1.ndjson"
        # ⚠️ `--` の後ろの白リスト違反はすべて exit 2・副作用の前 (outdir を作らない・gse-replay を呼ばない)
        rejected = {
            "--pole": ["--", "--pole", "baseline"],
            "--set の外の位置引数": ["--", "q=0.99"],
            "--features": ["--", "--features"],
            "--feature-config": ["--", "--feature-config", "x.json"],
            "知らないキー": ["--", "--set", "evil=1"],
            "net_diff_min (許可外)": ["--", "--set", "net_diff_min=1"],
            "theta_estimator (許可外)": ["--", "--set", "theta_estimator=nearest_rank"],
            "値にシェルのメタ文字": ["--", "--set", "q=0.99;rm"],
            "値が空": ["--", "--set", "q="],
            "キーが空": ["--", "--set", "=1"],
            "= が無い": ["--", "--set", "q"],
            "--set の後ろが無い": ["--", "--set"],
            "指数表記": ["--", "--set", "warmup_count=1e3"],
            "負": ["--", "--set", "hole_gap_ms=-1"],
            "先頭が小数点": ["--", "--set", "q=.5"],
            "末尾が小数点": ["--", "--set", "q=1."],
            "小数点が 2 つ": ["--", "--set", "q=0.9.9"],
            "空白を含む": ["--", "--set", "q= 0.99"],
            "--set=形": ["--", "--set=q=0.99"],
            "同じキーの 2 回指定 (値が違う)": ["--", "--set", "q=0.99", "--set", "q=0.999"],
            "同じキーの 2 回指定 (値が同じ)": ["--", "--set", "q=0.99", "--set", "q=0.99"],
            "正しい組 + 不正な組": ["--", "--set", "q=0.995", "--set", "warmup_count=200", "--pole", "baseline"],
            "-- の後ろが空": ["--"],
            "-- が無い余分な引数": ["--set", "q=0.99"],
            "-- が無い余分な引数 2": ["extra"],
        }
        for label, extra in rejected.items():
            outdir = self.new_out()
            rc, err = self.run_script(ndjson, outdir, *extra)
            self.assertEqual(rc, 2, f"{label}: {err}")
            self.assertFalse(outdir.exists(), f"{label}: 拒否したのに outdir が作られた")
            self.assertEqual(self.call_lines(), [], f"{label}: 拒否したのに gse-replay が呼ばれた")
        # ⚠️ 値に改行を含む場合 (★ 行単位の検査 (grep) だと 1 行目だけで通ってしまう)。
        #   argv に改行を載せられない環境 (Windows) があるので、bash の中で組み立てて渡す。陽性対照 (改行なし) も同じ経路で通す。
        outdir = self.new_out()
        rc, err = self.run_script_raw(ndjson, outdir, "q=0.99\\nfoo")
        self.assertEqual(rc, 2, f"改行を含む値: {err}")
        self.assertFalse(outdir.exists())
        self.assertEqual(self.call_lines(), [])
        rc, err = self.run_script_raw(ndjson, self.new_out(), "q=0.995")
        self.assertEqual(rc, 0, f"改行なしの同じ経路 (陽性対照): {err}")
        self.assertEqual(len(self.call_lines()), 3)
        self.calls.unlink()
        # ★ 後方互換 (陽性対照): `--` なしの 2 引数は従来どおり通り、gse-replay へは何も足さない
        rc, err = self.run_script(ndjson, self.new_out())
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.call_lines()), 3)
        for line in self.call_lines():
            self.assertNotIn("--set", line)
        self.calls.unlink()
        # ★ 陽性対照: 正しい組は通り、3 極すべてに渡り、封筒 config に反映される
        outdir = self.new_out()
        rc, err = self.run_script(ndjson, outdir, "--", "--set", "q=0.995", "--set", "warmup_count=200")
        self.assertEqual(rc, 0, err)
        lines = self.call_lines()
        self.assertEqual(len(lines), 3)
        for pole, line in zip(POLES, lines):
            self.assertTrue(line.endswith(f"--features --pole {pole} --set q=0.995 --set warmup_count=200"), line)
        for pole in POLES:
            config = json.loads((outdir / f"{pole}.json").read_text(encoding="utf-8"))["config"]
            self.assertEqual((config["pole"], config["q"], config["warmup_count"]), (pole, 0.995, 200))
        # ★ 7 キーすべて通る (値は整数・小数・0)
        outdir = self.new_out()
        rc, err = self.run_script(
            ndjson, outdir, "--",
            "--set", "w_ms=15000", "--set", "q=0.999", "--set", "b_ms=60000",
            "--set", "hole_gap_ms=3000", "--set", "warmup_count=1000", "--set", "t1a_window_ms=60000",
            "--set", "idle_trim_max_ms=0",
        )
        self.assertEqual(rc, 0, err)
        config = json.loads((outdir / "baseline.json").read_text(encoding="utf-8"))["config"]
        self.assertEqual(
            {k: config[k] for k in grid.TUNABLE_KEYS},
            {"w_ms": 15000, "q": 0.999, "b_ms": 60000, "hole_gap_ms": 3000, "warmup_count": 1000, "t1a_window_ms": 60000, "idle_trim_max_ms": 0},
        )
        # ★ 従来のガードは `--` の有無に依らず効く (使い回し拒否・失敗時は何も置かない)
        rc, _ = self.run_script(ndjson, outdir, "--", "--set", "q=0.99")
        self.assertEqual(rc, 2)
        failing = self.new_out()
        rc, _ = self.run_script(ndjson, failing, "--", "--set", "q=0.99", FAKE_FAIL_Q="0.99")
        self.assertEqual(rc, 1)
        self.assertEqual([p.name for p in failing.iterdir()], [], "失敗したのに outdir に何かが残った")


if __name__ == "__main__":
    unittest.main()
