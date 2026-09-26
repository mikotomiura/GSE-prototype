"""Tests for scripts/build_p1_episode_db.py (episode 表を使い捨ての DuckDB に載せる CLI・issue 003).

⚠️★★★ **規則 (e)・補訂 1 項目 7 (`ime_overlap` / `restart` を `t0` の側に置かない) は、スキーマで確かめる**:
`information_schema` で列を見るだけでなく、`episodes_t0` の JSON 列を**再帰的に**たどってキーの有無まで見る。
封筒に未知のブロックを足しても取り込まれないこと (許可リスト) と、許可したブロックの中に退行キーが現れたら拒否することも固定する。

⚠️ 本 module は実データも Rust も読まない (★ 入力はテストが `tempfile` の中で作る合成の封筒だけ。
封筒の形は実物の `gse-replay --features` の出力を実測して写した)。

⚠️★ テスト名の行に `... ok` が同じ行に出ることを acceptance が見る。→ ★ テストに docstring を付けない
(verbose 出力が 2 行に割れる)。★ 標準出力・標準エラーは必ず捕捉する (行の途中に混ざると `... ok` が崩れる)。

実行方法 (★ duckdb 入り。無いと data テストは skip される):
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_p1_episode_db -v
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_p1_episode_db as bdb  # noqa: E402
import p1_bounds  # noqa: E402
import p1_pg1_distribution as pg1  # noqa: E402

try:
    import duckdb

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

requires_duckdb = unittest.skipUnless(HAS_DUCKDB, "duckdb not installed")

POLES = p1_bounds.POLES
CLI = SCRIPTS / "build_p1_episode_db.py"
PREREG_SHA = "0123456789abcdef"
T0_BASE = 1_700_000_010_000
RETROSPECTIVE = {"ime_overlap", "restart", "restop_ms"}
T0_COLUMNS = {
    "participant_id", "session_id", "pole", "t0_ms", "s_ms", "theta_person_ms", "theta_sample_n", "task_kind", "phase",
    "activity", "boundary", "dispersion", "revision", "quality",
}
RETROSPECTIVE_COLUMNS = {"participant_id", "session_id", "pole", "t0_ms", "ime_overlap", "restart"}

# レイアウト: (参加者, セッション, 極ごとの onset 本数)。★ s1 は P01 と P02 で重複する (複合キーの検査に使う)
LAYOUT = (
    ("P01", "s1", {"baseline": 2, "pointer_b": 1, "modifier_m_plus": 3}),
    ("P01", "s2", {"baseline": 3, "pointer_b": 0, "modifier_m_plus": 1}),
    ("P02", "s1", {"baseline": 4, "pointer_b": 4, "modifier_m_plus": 0}),
)


def t0_of(k):
    return T0_BASE + k * 10_000


def make_row(t_ms, t0=None):
    """`t0` が None なら onset でない行。onset 行は `t0` で値が一意になる (ime_overlap は真偽が交互)。"""
    onset = t0 is not None
    return {
        "t_ms": t_ms,
        "activity": {"key_count": 3, "backspace_count": 1},
        "boundary": {"pauses": 1},
        "dispersion": {"pause_p50_ms": 2100, "pause_p90_ms": 3000, "pause_max_ms": 4000, "iki_cv": 0.5},
        "stall_onset": {
            "is_onset": onset,
            "s_ms": t0 - 3000 if onset else None,
            "t0_ms": t0 if onset else None,
            "theta_person_ms": 2500 if onset else None,
            "theta_sample_n": 120 if onset else None,
            "task_kind": "writing" if onset else None,
            "phase": "unspecified",
            "ime_overlap": (t0 // 10_000) % 2 == 0 if onset else None,
        },
        "quality": {"missing_reasons": []},
        "revision": {"units_closed": 0},
        "restart": {"restop_ms": 4000 if onset else None, "stable_generation_ms": 9000 if onset else None},
    }


def make_rows(onsets):
    """onset を `onsets` 本持つ行の列 (各 onset の前後に onset でない行を挟む)。"""
    rows = [make_row(1_700_000_000_000)]
    for k in range(onsets):
        rows.append(make_row(1_700_000_001_000 + k * 1000, t0_of(k)))
        rows.append(make_row(1_700_000_002_000 + k * 1000))
    return rows


def make_envelope(pole, rows, applicable=True):
    reason = None
    if not applicable:
        reason = "no_modifier_rows" if pole == "modifier_m_plus" else "no_pointer_rows"
    return {
        "provenance": {"tool": "gse-replay", "source_basename": "synthetic.ndjson", "hmm_version": "0.5.0"},
        "config": {
            "pole": pole,
            "pole_applicable": applicable,
            "pole_not_applicable_reason": reason,
            "prereg_id": "p1-episode",
            "prereg_version": "1.0.0",
            "prereg_sha256_prefix": PREREG_SHA,
            "config_source": "frozen",
            "overrides": [],
            "hmm_version": "0.5.0",
        },
        "rows": rows,
    }


def write_session(root, participant, session, onsets, not_applicable=()):
    """`onsets`: 極 → onset の本数 (無い極は 0)。`not_applicable`: 非適用にする極 (★ 行は baseline と恒等にする)。"""
    session_dir = Path(root) / participant / session
    session_dir.mkdir(parents=True)
    baseline_rows = make_rows(onsets.get("baseline", 0))
    for pole in POLES:
        if pole in not_applicable:
            envelope = make_envelope(pole, baseline_rows, applicable=False)
        else:
            envelope = make_envelope(pole, make_rows(onsets.get(pole, 0)))
        (session_dir / f"{pole}.json").write_text(json.dumps(envelope), encoding="utf-8")
    return session_dir


def edit_envelope(path, fn):
    path = Path(path)
    envelope = json.loads(path.read_text(encoding="utf-8"))
    fn(envelope)
    path.write_text(json.dumps(envelope), encoding="utf-8")


def onset_rows(envelope):
    return [row for row in envelope["rows"] if row["stall_onset"]["is_onset"]]


def run_cli(root, out, sessions=None):
    """CLI を同じプロセスで回し `(exit code, stderr)` を返す。⚠️ 標準出力・標準エラーは必ず捕捉する。"""
    argv = ["--root", str(root), "--out", str(out)]
    if sessions is not None:
        argv += ["--sessions", str(sessions)]
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        try:
            rc = bdb.main(argv)
        except SystemExit as e:  # argparse の引数不備は exit 2
            rc = e.code
    return rc, err.getvalue()


def query(db, sql, params=()):
    con = duckdb.connect(str(db), read_only=True)
    try:
        return con.execute(sql, list(params)).fetchall()
    finally:
        con.close()


def find_keys(value):
    """JSON の値の中 (どの深さでも) のキーを集める。"""
    keys, stack = set(), [value]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            keys.update(node)
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return keys


class EpisodeDbCase(unittest.TestCase):
    def setUp(self):
        # ★ `TemporaryDirectory` は system の temp の下 (git 管理外) に作る
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
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
        return self.tmp / f"out{self._n}" / "ep.duckdb"  # ★ 親ディレクトリはまだ無い

    def base_layout(self):
        root = self.new_dir()
        for participant, session, onsets in LAYOUT:
            write_session(root, participant, session, onsets)
        return root

    def write_manifest(self, lines, header="participant_id,session_id,os,phase", encoding="utf-8", newline="\n"):
        path = self.new_dir() / "sessions.csv"
        path.write_bytes(newline.join([header, *lines, ""]).encode(encoding))
        return path

    def build(self, root, sessions=None):
        out = self.new_out()
        rc, err = run_cli(root, out, sessions)
        self.assertEqual(rc, 0, err)
        return out

    def assert_rejected(self, root, expected_rc, label, sessions=None):
        out = self.new_out()
        rc, err = run_cli(root, out, sessions)
        self.assertEqual(rc, expected_rc, f"{label}: {err}")
        self.assertFalse(out.exists(), f"{label}: 拒否したのに出力が作られた")
        self.assertFalse(out.parent.exists(), f"{label}: 拒否したのに出力先のディレクトリが作られた")
        return err


@requires_duckdb
class EpisodeDbTest(EpisodeDbCase):
    def test_tables_and_counts(self):
        db = self.build(self.base_layout())
        expected = {"baseline": 9, "pointer_b": 5, "modifier_m_plus": 4}  # ★ is_onset==true の行数の合計 (極ごと)
        for table in ("episodes_t0", "episodes_retrospective"):
            self.assertEqual(dict(query(db, f"SELECT pole, count(*) FROM {table} GROUP BY pole")), expected, table)
        keys_sql = "SELECT participant_id, session_id, pole, t0_ms FROM {} ORDER BY 1, 2, 3, 4"
        t0_keys = query(db, keys_sql.format("episodes_t0"))
        self.assertEqual(len(t0_keys), sum(expected.values()))
        self.assertEqual(t0_keys, query(db, keys_sql.format("episodes_retrospective")))  # ★ 同じキー

        sessions = query(db, "SELECT participant_id, session_id, pole, n_rows, n_onsets FROM sessions ORDER BY 1, 2, 3")
        self.assertEqual(
            sessions,
            sorted((p, s, pole, 1 + 2 * onsets.get(pole, 0), onsets.get(pole, 0)) for p, s, onsets in LAYOUT for pole in POLES),
        )
        (provenance,) = query(
            db,
            "SELECT DISTINCT pole_applicable, pole_not_applicable_reason, prereg_version, prereg_sha256_prefix, config_source, overrides_json "
            "FROM sessions",
        )
        self.assertEqual(provenance, (True, None, "1.0.0", PREREG_SHA, "frozen", "[]"))

        # ★ 値がそのまま載る (JSON の列は構造が同じ・時刻は整数の型)
        expected_row = make_row(0, T0_BASE)
        row = query(
            db,
            "SELECT s_ms, theta_person_ms, theta_sample_n, task_kind, phase, activity, boundary, dispersion, revision, quality "
            "FROM episodes_t0 WHERE participant_id = 'P01' AND session_id = 's1' AND pole = 'baseline' AND t0_ms = ?",
            [T0_BASE],
        )
        self.assertEqual(len(row), 1)
        s_ms, theta_person_ms, theta_sample_n, task_kind, phase, *blocks = row[0]
        self.assertEqual((s_ms, theta_person_ms, theta_sample_n, task_kind, phase), (T0_BASE - 3000, 2500, 120, "writing", "unspecified"))
        for block, cell in zip(bdb.T0_BLOCKS, blocks):
            self.assertEqual(json.loads(cell), expected_row[block], block)
        ((ime_overlap, restart),) = query(
            db,
            "SELECT ime_overlap, restart FROM episodes_retrospective "
            "WHERE participant_id = 'P01' AND session_id = 's1' AND pole = 'baseline' AND t0_ms = ?",
            [T0_BASE],
        )
        self.assertEqual(ime_overlap, expected_row["stall_onset"]["ime_overlap"])
        self.assertEqual(json.loads(restart), expected_row["restart"])
        types = dict(
            query(
                db,
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'episodes_t0' "
                "AND column_name IN ('t0_ms', 's_ms', 'theta_person_ms', 'theta_sample_n')",
            )
        )
        self.assertEqual(set(types.values()), {"BIGINT"}, types)

        # ★ 同じ入力なら同じ DB (使い捨てだが、作り直して結果が変わらない)
        again = self.build(self.base_layout())
        for table in ("sessions", "episodes_t0", "episodes_retrospective"):
            sql = f"SELECT * FROM {table} ORDER BY ALL"
            self.assertEqual(query(db, sql), query(again, sql), table)

    def test_t0_table_excludes_retrospective(self):
        db = self.build(self.base_layout())

        def columns(name):
            return {r[0] for r in query(db, "SELECT column_name FROM information_schema.columns WHERE table_name = ?", [name])}

        t0_columns = columns("episodes_t0")
        self.assertFalse(t0_columns & RETROSPECTIVE, t0_columns)
        self.assertEqual(t0_columns, T0_COLUMNS)  # ★ 許可リストと丁度一致する
        self.assertIn("ime_overlap", columns("episodes_retrospective"))
        self.assertIn("restart", columns("episodes_retrospective"))
        self.assertEqual(columns("episodes_retrospective"), RETROSPECTIVE_COLUMNS)
        self.assertEqual(columns("episodes_with_manifest"), T0_COLUMNS | {"has_manifest", "os", "manifest_phase"})
        # ★ どの表・ビューにあるか: 退行キーの列を持つのは episodes_retrospective だけ
        holders = query(
            db,
            "SELECT DISTINCT table_name FROM information_schema.columns WHERE column_name IN ('ime_overlap', 'restart', 'restop_ms')",
        )
        self.assertEqual(holders, [("episodes_retrospective",)])
        # ★ 極をまたぐビューは無い (§3 規律 4)。ビューは episodes_with_manifest だけ
        self.assertEqual(query(db, "SELECT view_name FROM duckdb_views() WHERE NOT internal"), [("episodes_with_manifest",)])

    def test_t0_json_has_no_retrospective_keys(self):
        root = self.base_layout()
        for path in root.glob("*/*/*.json"):

            def add_unknown(envelope):
                for row in onset_rows(envelope):
                    row["future_block"] = {"note": "将来増えたブロック"}
                    row["stall_onset"]["future_field"] = 1

            edit_envelope(path, add_unknown)
        db = self.build(root)
        cells = query(db, "SELECT activity, boundary, dispersion, revision, quality FROM episodes_t0")
        self.assertTrue(cells)
        for row in cells:
            for cell in row:
                self.assertFalse(find_keys(json.loads(cell)) & RETROSPECTIVE, cell)  # ★ 再帰的にたどっても無い
        # ★ 未知のブロック・キーは、列にも値にも現れない (許可リスト)
        self.assertEqual(
            {r[0] for r in query(db, "SELECT column_name FROM information_schema.columns WHERE table_name = 'episodes_t0'")},
            T0_COLUMNS,
        )
        everything = json.dumps(query(db, "SELECT * FROM episodes_t0"), ensure_ascii=False)
        for word in ("future_block", "future_field", "将来増えた"):
            self.assertNotIn(word, everything)

        # ⚠️★★★ 許可したブロックの中に退行キーが現れたら、黙って載せず・黙って落とさず拒否する (exit 3)
        # ★ エラー文には退行キー 3 つの一覧が常に入るので、**見つかった場所** (`<block><経路>`) まで照合する
        cases = (
            ("activity の直下の restop_ms", lambda row: row["activity"].update(restop_ms=1), "activity.restop_ms"),
            ("boundary の入れ子の中の ime_overlap", lambda row: row["boundary"].update(nested={"ime_overlap": True}), "boundary.nested.ime_overlap"),
            ("quality の直下の restart", lambda row: row["quality"].update(restart=1), "quality.restart"),
            ("配列の中の restart", lambda row: row["revision"].update(items=[{"restart": 1}]), "revision.items[0].restart"),
        )
        for label, mutate, location in cases:
            with self.subTest(case=label):
                root = self.base_layout()
                edit_envelope(root / "P01" / "s1" / "baseline.json", lambda envelope: mutate(onset_rows(envelope)[0]))
                err = self.assert_rejected(root, 3, label)
                self.assertIn(location, err)

    def test_manifest_join(self):
        root = self.base_layout()
        manifest = self.write_manifest(["P01,s1,windows,pre", "P02,s1,macos,post", "P09,s1,linux,pre"])  # ★ P09 はレイアウトに無い
        db = self.build(root, manifest)
        total = query(db, "SELECT count(*) FROM episodes_t0")[0][0]
        view = query(db, "SELECT participant_id, session_id, has_manifest, os, manifest_phase FROM episodes_with_manifest")
        self.assertEqual(len(view), total)  # ★ 結合で行が増えも減りもしない
        by_key = {(p, s): (h, o, ph) for p, s, h, o, ph in view}
        self.assertEqual(by_key[("P01", "s1")], (True, "windows", "pre"))
        self.assertEqual(by_key[("P02", "s1")], (True, "macos", "post"))  # ★ 同じセッション名でも参加者ごとに別の行と結合する
        self.assertEqual(by_key[("P01", "s2")], (False, None, None))  # ★ CSV に無いセッション
        self.assertEqual(query(db, "SELECT count(*) FROM manifest")[0][0], 3)

        # ★ 一方の参加者の行だけなら、同じセッション名の他方は誤結合しない
        db = self.build(root, self.write_manifest(["P01,s1,windows,pre"]))
        rows = query(db, "SELECT DISTINCT participant_id, session_id, has_manifest, os FROM episodes_with_manifest")
        self.assertEqual(
            sorted(rows),
            [("P01", "s1", True, "windows"), ("P01", "s2", False, None), ("P02", "s1", False, None)],
        )

        # ★ --sessions が無ければ、すべて has_manifest = false・os / manifest_phase は NULL
        db = self.build(root)
        self.assertEqual(
            query(db, "SELECT DISTINCT has_manifest, os, manifest_phase FROM episodes_with_manifest"),
            [(False, None, None)],
        )
        self.assertEqual(query(db, "SELECT count(*) FROM manifest")[0][0], 0)

        # ★ Excel 保存に多い BOM 付き・CRLF でも読める (P01/s1 の episode は 2 + 1 + 3 = 6 本)
        bom = self.write_manifest(["P01,s1,windows,pre"], encoding="utf-8-sig", newline="\r\n")
        db = self.build(root, bom)
        self.assertEqual(query(db, "SELECT count(*) FROM episodes_with_manifest WHERE has_manifest")[0][0], 6)

        # ⚠️ 契約違反は exit 3 (黙って片方を採らない・黙って読み飛ばさない)
        for label, lines, header in (
            ("キーの重複", ["P01,s1,windows,pre", "P02,s1,macos,post", "P01,s1,macos,post"], "participant_id,session_id,os,phase"),
            ("列の欠け", ["P01,s1,windows"], "participant_id,session_id,os"),
            ("列数が足りない行", ["P01,s1,windows"], "participant_id,session_id,os,phase"),
            ("列数が多い行", ["P01,s1,windows,pre,extra"], "participant_id,session_id,os,phase"),
            ("空の participant_id", [",s1,windows,pre"], "participant_id,session_id,os,phase"),
        ):
            with self.subTest(case=label):
                err = self.assert_rejected(root, 3, label, self.write_manifest(lines, header=header))
                if label == "キーの重複":
                    self.assertIn("重複", err)

    def test_not_applicable_sessions_recorded(self):
        root = self.new_dir()
        write_session(root, "P01", "s1", {"baseline": 3}, not_applicable=("pointer_b", "modifier_m_plus"))
        write_session(root, "P02", "s1", {"baseline": 2, "pointer_b": 1, "modifier_m_plus": 0})  # ★ 適用可で onset が 0 本
        db = self.build(root)
        rows = {
            (p, s, pole): rest
            for p, s, pole, *rest in query(
                db,
                "SELECT participant_id, session_id, pole, pole_applicable, pole_not_applicable_reason, n_rows, n_onsets FROM sessions",
            )
        }
        self.assertEqual(len(rows), 6)
        # ★ 非適用は理由つきで載り、onset 数は NULL (行は baseline と恒等なので数えない)
        self.assertEqual(rows[("P01", "s1", "pointer_b")], [False, "no_pointer_rows", 7, None])
        self.assertEqual(rows[("P01", "s1", "modifier_m_plus")], [False, "no_modifier_rows", 7, None])
        self.assertEqual(rows[("P01", "s1", "baseline")], [True, None, 7, 3])
        # ★ 適用可で onset が 0 本のセッションは、0 として載る (非適用の NULL と区別できる)
        self.assertEqual(rows[("P02", "s1", "modifier_m_plus")], [True, None, 1, 0])
        # ★ 非適用の極の onset は episode 表に載らない (載せると baseline の 3 本が極の名前を変えて二重に入る)
        for table in ("episodes_t0", "episodes_retrospective"):
            self.assertEqual(
                query(db, f"SELECT pole, count(*) FROM {table} WHERE participant_id = 'P01' GROUP BY pole"),
                [("baseline", 3)],
                table,
            )
        # ★ 全極が適用可のセッションの onset 数と、episode 表の行数が一致する (sessions.n_onsets = 載せた本数)
        self.assertEqual(
            query(db, "SELECT sum(n_onsets) FROM sessions")[0][0],
            query(db, "SELECT count(*) FROM episodes_t0")[0][0],
        )

    def test_guards(self):
        root = self.base_layout()

        # ── exit 2: --out が git の作業ツリーの中 (直下・まだ無い深いディレクトリの下・.git の中) は、何も作らない
        repo = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)  # ★ Windows は .git の読み取り専用で消せないことがある
        self.addCleanup(repo.cleanup)
        repo_dir = Path(repo.name)
        subprocess.run(["git", "init", "-q", str(repo_dir)], check=True, capture_output=True)
        for label, target in (
            ("直下", repo_dir / "ep.duckdb"),
            ("まだ無いディレクトリの下", repo_dir / "a" / "b" / "ep.duckdb"),
            (".git の中", repo_dir / ".git" / "ep.duckdb"),
        ):
            with self.subTest(out=label):
                rc, err = run_cli(root, target)
                self.assertEqual(rc, 2, err)
                self.assertFalse(target.exists())
        self.assertFalse((repo_dir / "a").exists())  # ★ 拒否するときにディレクトリを作らない
        self.build(root)  # 対照: 管理外なら通る (⚠️ 上の拒否が「別の理由」で落ちていないことの裏づけ)
        # ⚠️ 判定そのものが失敗したら、管理外とは見なさず拒否する (fail-closed)
        target = self.new_out()
        with mock.patch.object(pg1.subprocess, "run", side_effect=FileNotFoundError("git")):
            rc, err = run_cli(root, target)
        self.assertEqual(rc, 2, err)
        self.assertFalse(target.exists())

        # ── exit 2: 既存のファイルは上書きしない・--root / --sessions が違う
        existing = self.new_dir() / "ep.duckdb"
        existing.write_text("keep", encoding="utf-8")
        rc, err = run_cli(root, existing)
        self.assertEqual(rc, 2, err)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep")
        rc, err = run_cli(self.tmp / "nowhere", self.new_out())
        self.assertEqual(rc, 2, err)
        self.assert_rejected(root, 2, "--sessions が無いファイル", self.tmp / "nowhere.csv")
        err_buf = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err_buf):
            with self.assertRaises(SystemExit) as raised:
                bdb.main(["--root", str(root)])  # ★ 引数の不備は argparse が exit 2
        self.assertEqual(raised.exception.code, 2)

        # ── exit 3: レイアウト・封筒の形の違い・極の欠け (⚠️ どれも出力もそのディレクトリも作らない)
        def broken(label, mutate):
            with self.subTest(case=label):
                layout = self.base_layout()
                mutate(layout)
                self.assert_rejected(layout, 3, label)

        def first_onset(fn):
            return lambda layout: edit_envelope(layout / "P01" / "s1" / "baseline.json", lambda e: fn(onset_rows(e)[0]))

        broken("極のファイルが欠けている", lambda layout: (layout / "P02" / "s1" / "pointer_b.json").unlink())
        broken(".all-poles.lock が残っている", lambda layout: (layout / "P01" / "s1" / ".all-poles.lock").write_text("x"))
        broken("壊れた JSON", lambda layout: (layout / "P01" / "s1" / "baseline.json").write_text("{", encoding="utf-8"))
        broken("rows が配列でない", lambda layout: edit_envelope(layout / "P01" / "s1" / "baseline.json", lambda e: e.update(rows={})))
        broken(
            "ファイル名と config.pole が違う",
            lambda layout: edit_envelope(layout / "P01" / "s1" / "pointer_b.json", lambda e: e["config"].update(pole="baseline")),
        )
        broken("t0_ms が浮動小数", first_onset(lambda row: row["stall_onset"].update(t0_ms=1.5e12)))
        broken("t0_ms が文字列", first_onset(lambda row: row["stall_onset"].update(t0_ms="1")))
        broken("t0_ms が真偽", first_onset(lambda row: row["stall_onset"].update(t0_ms=True)))
        broken("onset なのに t0_ms が null", first_onset(lambda row: row["stall_onset"].update(t0_ms=None)))
        broken("s_ms が負", first_onset(lambda row: row["stall_onset"].update(s_ms=-1)))
        broken("theta_person_ms が桁あふれ", first_onset(lambda row: row["stall_onset"].update(theta_person_ms=2**63)))
        broken("ime_overlap が真偽でない", first_onset(lambda row: row["stall_onset"].update(ime_overlap="yes")))
        broken("phase が無い", first_onset(lambda row: row["stall_onset"].pop("phase")))
        broken("onset 行にブロックが無い", first_onset(lambda row: row.pop("quality")))
        broken("onset 行に restart が無い", first_onset(lambda row: row.pop("restart")))
        broken(
            "同じ極の中で t0_ms が重複",
            lambda layout: edit_envelope(
                layout / "P01" / "s1" / "baseline.json",
                lambda e: onset_rows(e)[1]["stall_onset"].update(t0_ms=onset_rows(e)[0]["stall_onset"]["t0_ms"]),
            ),
        )
        with self.subTest(case="セッションが 1 つも無い root"):
            self.assert_rejected(self.new_dir(), 3, "空の root")

    def test_partial_db_removed_on_failure(self):
        root = self.base_layout()
        out = self.new_out()
        with mock.patch.object(bdb, "_insert", side_effect=duckdb.Error("boom")):
            rc, err = run_cli(root, out)
        self.assertEqual(rc, 4, err)
        self.assertFalse(out.exists())  # ★ 書きかけの DB を残さない
        self.assertFalse(Path(f"{out}.wal").exists())

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
        self.assertIn(f"[{bdb.TOOL}] OK", done.stdout)
        self.assertEqual(spawn("--root", str(root), "--out", str(out)).returncode, 2)  # ★ 既にある
        (root / "P02" / "s1" / "pointer_b.json").unlink()
        self.assertEqual(spawn("--root", str(root), "--out", str(self.new_out())).returncode, 3)
        self.assertEqual(spawn("--root", str(root)).returncode, 2)


class NoDuckdbTest(EpisodeDbCase):
    def test_exit_5_when_duckdb_is_missing(self):
        # ★ duckdb が入っていなくても走る (⚠️ 無いことを `sys.modules` の None で作る)
        root = self.base_layout()
        out = self.new_out()
        with mock.patch.dict(sys.modules, {"duckdb": None}):
            rc, err = run_cli(root, out)
        self.assertEqual(rc, 5, err)
        self.assertIn("duckdb", err)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
