"""P1 の episode 表を使い捨ての DuckDB に載せる CLI (issue 003)。

## ★ 何をするか

`scripts/run-features-all-poles.sh` の出力を `<root>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json`
に並べたもの (レイアウトは `p1_features_io.py` の冒頭) を読み、**極ごとの episode (onset) 表**を DuckDB に作る。

    python scripts/build_p1_episode_db.py --root <root> --out <DB> [--sessions <sessions.csv>]

DB は**使い捨て**で、repo の外に置き、共有しない (`decisions.md` 判断 10)。既存のファイルは上書きしない。
結合するのは episode 表と `sessions.csv` (参加者・OS・phase) だけで、metrics・probe・survey・転帰とは結合しない。

## ⚠️★★★ `t0` の時点で使える量と、使えない量を「スキーマで」分ける

事前宣言 v1.1 冒頭 (1)・規則 (e) は `ime_overlap` を **retrospective** (`t` は変換の終端で、`t0` より後の行に依りうる) と定め、
ADR-030 補訂 1 項目 7 は `restart` (`T1d`) を**転帰側の量**として、同じ episode の予測にもオンラインの推論・介入の入力にも使わないと定める。
→ ★ 列を分けるだけでなく**表を分ける**:

| 表 / ビュー | 中身 |
|---|---|
| `sessions` | 1 行 = (participant_id, session_id, pole)。適用可否と理由・事前宣言の版・設定の由来・overrides・行数と onset 数 |
| `episodes_t0` | 1 行 = 1 onset。キー `(participant_id, session_id, pole, t0_ms)` ＋ `s_ms` / `theta_person_ms` / `theta_sample_n` / `task_kind` / `phase` ＋ onset 行の `activity` / `boundary` / `dispersion` / `revision` / `quality` (JSON 文字列) |
| `episodes_retrospective` | 同じキー ＋ `ime_overlap` (真偽) ＋ `restart` (JSON 文字列)。⚠️ **`t0` の予測・推論の入力に使わない側** |
| `manifest` | `--sessions` の CSV (無ければ空)。`episodes_with_manifest` を作るためだけの表 |
| ビュー `episodes_with_manifest` | `episodes_t0` と `manifest` を **`(participant_id, session_id)` の複合キーで**結合 (★ セッション名は参加者間で重複しうる)。`has_manifest` / `os` / `manifest_phase` を足す |

- ⚠️ **`ime_overlap` / `restart` の列は `episodes_t0` にも、ビューにも無い。** `episodes_t0` の JSON 列の中にも、
  `ime_overlap` / `restart` / `restop_ms` のキーは (どの深さにも) 無い。
- ⚠️ **許可リストで組み立てる**: 上の名指しのブロックとキーだけを取り込む。封筒に将来増えた未知のブロック・キーは自動では取り込まない。
  ★ さらに、許可したブロックの**中**に上の 3 つのキーが現れたら、黙って落とさず・黙って載せず **exit 3** にする
  (封筒の形が変わっており、`t0` の側に退行量が紛れ込みうるため)。
- ⚠️ 極は `pole` 列で分けるだけ。**極をまたいだ結合・集計のビューは作らない** (事前宣言 §3 規律 4)。

## ⚠️ 非適用の極 (`pole_applicable = false`)

非適用の極の封筒は、行の `stall_onset` / `restart` が **baseline と恒等**である (`replay.rs`)。onset を載せると baseline の episode が
極の名前を変えて二重に入る。→ ★ 非適用の (セッション, 極) は **`sessions` にだけ**理由つきで載せ、`episodes_t0` /
`episodes_retrospective` には**行を載せない**。`sessions.n_onsets` は「`episodes_t0` に載せた onset の本数」で、
非適用なら **NULL** (適用可で onset が 0 本の `0` と区別できる)。`n_rows` は封筒の行数で、常に入る。

## exit

| code | 意味 |
|---|---|
| 0 | OK |
| 2 | 引数・出力先のガード (`--root` がディレクトリでない・`--sessions` がファイルでない・`--out` が既にある・`--out` が git の作業ツリーの中・git の判定が失敗) |
| 3 | レイアウト・封筒・`--sessions` の CSV の形が違う (`p1_features_io` の `LayoutError` / `EnvelopeError`、CSV の列の欠け・キーの重複) |
| 4 | DB の書き込みに失敗した / ファイルを読めない |
| 5 | duckdb が無い (`pip install -r scripts/requirements-dev.txt`) |

⚠️ 入力の検査はすべて DB を作る**前**に済ませる。拒否したときは出力もそのディレクトリも作らず、DB の構築中に失敗したときは書きかけの DB を消す。

⚠️ `p1_features_io.project_pg1` は PG-1 専用なので**使わない** (読み込みは `discover` / `load_session` だけ)。

使い方 (テスト): `python -m unittest scripts.tests.test_p1_episode_db -v` (repo 直下から・★ duckdb 入り)。
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import p1_features_io as fio
import p1_pg1_distribution as pg1
from p1_bounds import POLES

TOOL = "build_p1_episode_db"
EXIT_OK, EXIT_GUARD, EXIT_LAYOUT, EXIT_IO, EXIT_NO_DUCKDB = 0, 2, 3, 4, 5

# ★ `episodes_t0` に載せる onset 行のブロック (許可リスト)。封筒に未知のブロックが増えても取り込まない。
T0_BLOCKS = ("activity", "boundary", "dispersion", "revision", "quality")
# ⚠️★★★ `t0` の側に**現れてはならない**キー (規則 (e)・補訂 1 項目 7)。許可したブロックの中も再帰的に検査する。
RETROSPECTIVE_KEYS = frozenset({"ime_overlap", "restart", "restop_ms"})

_INT64_MAX = 2**63 - 1

_KEY3 = (
    ("participant_id", "VARCHAR NOT NULL"),
    ("session_id", "VARCHAR NOT NULL"),
    ("pole", "VARCHAR NOT NULL"),
)
_KEY4 = _KEY3 + (("t0_ms", "BIGINT NOT NULL"),)

# ★ 列の定義は 1 か所 (DDL と INSERT の順序をここから作る)。先頭の `key_count` 列が主キー。
SESSIONS_COLUMNS = _KEY3 + (
    ("pole_applicable", "BOOLEAN NOT NULL"),
    ("pole_not_applicable_reason", "VARCHAR"),
    ("prereg_version", "VARCHAR NOT NULL"),
    ("prereg_sha256_prefix", "VARCHAR NOT NULL"),
    ("config_source", "VARCHAR NOT NULL"),
    ("overrides_json", "VARCHAR NOT NULL"),
    ("n_rows", "BIGINT NOT NULL"),
    ("n_onsets", "BIGINT"),
)
EPISODES_T0_COLUMNS = _KEY4 + (
    ("s_ms", "BIGINT NOT NULL"),
    ("theta_person_ms", "BIGINT"),
    ("theta_sample_n", "BIGINT"),
    ("task_kind", "VARCHAR"),
    ("phase", "VARCHAR NOT NULL"),
) + tuple((block, "VARCHAR NOT NULL") for block in T0_BLOCKS)
EPISODES_RETROSPECTIVE_COLUMNS = _KEY4 + (
    ("ime_overlap", "BOOLEAN"),
    ("restart", "VARCHAR NOT NULL"),
)
MANIFEST_COLUMNS = (
    ("participant_id", "VARCHAR NOT NULL"),
    ("session_id", "VARCHAR NOT NULL"),
    ("os", "VARCHAR"),
    ("phase", "VARCHAR"),
)

# `sessions.csv` の契約 (`gen_sessions_manifest.py`)。★ 結合キーは (participant_id, session_id) の 2 つだけ。
MANIFEST_CSV_COLUMNS = ("participant_id", "session_id", "os", "phase")

_VIEW_SQL = """
CREATE VIEW episodes_with_manifest AS
SELECT e.*,
       (m.participant_id IS NOT NULL) AS has_manifest,
       m.os AS os,
       m.phase AS manifest_phase
FROM episodes_t0 e
LEFT JOIN manifest m
  ON e.participant_id = m.participant_id AND e.session_id = m.session_id
"""


class ManifestError(fio.FeaturesIOError):
    """`--sessions` の CSV の形が契約と違う (列の欠け・空のキー・キーの重複)。"""


def _dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _find_retrospective_key(value):
    """`value` の中 (どの深さでも) に `RETROSPECTIVE_KEYS` のキーがあれば、その場所を返す。無ければ `None`。

    ⚠️ 再帰ではなく明示のスタックで辿る (深い入れ子で `RecursionError` にしない)。
    """
    stack = [("", value)]
    while stack:
        where, node = stack.pop()
        if isinstance(node, dict):
            for key, child in node.items():
                if key in RETROSPECTIVE_KEYS:
                    return f"{where}.{key}"
                stack.append((f"{where}.{key}", child))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                stack.append((f"{where}[{index}]", child))
    return None


def _is_int64(value):
    # ★ bool は int の子だが、時刻・件数としては受け付けない
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= _INT64_MAX


def _is_text(value):
    return isinstance(value, str)


def _is_bool(value):
    return isinstance(value, bool)


def _onset_field(onset, key, at, check, describe, nullable=False):
    """`stall_onset` の 1 キーを取り出して型を検査する。無い・型が違えば `EnvelopeError` (⚠️ 黙って NULL にしない)。"""
    if key not in onset:
        raise fio.EnvelopeError(f"{at}.stall_onset に {key!r} が無い")
    value = onset[key]
    if value is None and nullable:
        return None
    if not check(value):
        raise fio.EnvelopeError(f"{at}.stall_onset.{key} が {describe} ではない: {value!r}")
    return value


def _onset_rows(participant, session, pole, envelope, where):
    """検証済みの封筒から、`is_onset == true` の行を `(t0 表の行, retrospective 表の行)` の列にして返す。

    ⚠️ ここで名指しするキー・ブロックだけを読む (許可リスト)。許可したブロックの中に退行キーがあれば `EnvelopeError`。
    """
    rows, seen = [], set()
    for index, row in enumerate(envelope["rows"]):
        onset = row["stall_onset"]
        if not onset["is_onset"]:
            continue
        at = f"{where}: rows[{index}]"
        s_ms = _onset_field(onset, "s_ms", at, _is_int64, "0 以上の整数")
        t0_ms = _onset_field(onset, "t0_ms", at, _is_int64, "0 以上の整数")
        theta_person_ms = _onset_field(onset, "theta_person_ms", at, _is_int64, "0 以上の整数か null", nullable=True)
        theta_sample_n = _onset_field(onset, "theta_sample_n", at, _is_int64, "0 以上の整数か null", nullable=True)
        task_kind = _onset_field(onset, "task_kind", at, _is_text, "文字列か null", nullable=True)
        phase = _onset_field(onset, "phase", at, _is_text, "文字列")
        ime_overlap = _onset_field(onset, "ime_overlap", at, _is_bool, "真偽か null", nullable=True)
        if t0_ms in seen:
            raise fio.EnvelopeError(f"{at}: t0_ms={t0_ms} の onset が同じ極の中に 2 行以上ある (★ episode のキーが一意でない)")
        seen.add(t0_ms)

        blocks = []
        for block in T0_BLOCKS:
            value = row.get(block)
            if not isinstance(value, dict):
                raise fio.EnvelopeError(f"{at}.{block} がオブジェクトではない (★ onset 行に要る)")
            leaked = _find_retrospective_key(value)
            if leaked is not None:
                raise fio.EnvelopeError(
                    f"{at}.{block}{leaked}: t0 の側に載せてはならないキー {sorted(RETROSPECTIVE_KEYS)} がある "
                    "(★ 封筒の形が変わった。規則 (e)・ADR-030 補訂 1 項目 7)"
                )
            blocks.append(_dumps(value))
        restart = row.get("restart")
        if not isinstance(restart, dict):
            raise fio.EnvelopeError(f"{at}.restart がオブジェクトではない (★ onset 行に要る)")

        key = (participant, session, pole, t0_ms)
        rows.append(
            (
                key + (s_ms, theta_person_ms, theta_sample_n, task_kind, phase, *blocks),
                key + (ime_overlap, _dumps(restart)),
            )
        )
    return rows


def collect(root):
    """レイアウトを読み、`(sessions の行, episodes_t0 の行, episodes_retrospective の行)` を返す。書き込みはしない。

    `LayoutError` / `EnvelopeError` を送出する。⚠️ 非適用の極の onset は載せない (冒頭の「非適用の極」)。
    """
    sessions, t0_rows, retrospective_rows = [], [], []
    for participant, session, paths in fio.discover(root):
        envelopes = fio.load_session(paths)
        for pole in POLES:
            envelope = envelopes[pole]
            config = envelope["config"]
            applicable = config["pole_applicable"]
            onsets = None
            if applicable:
                onsets = _onset_rows(participant, session, pole, envelope, f"{participant}/{session} の極 {pole}")
                t0_rows.extend(t0 for t0, _ in onsets)
                retrospective_rows.extend(retrospective for _, retrospective in onsets)
            sessions.append(
                (
                    participant,
                    session,
                    pole,
                    applicable,
                    config["pole_not_applicable_reason"],
                    config["prereg_version"],
                    config["prereg_sha256_prefix"],
                    config["config_source"],
                    _dumps(config["overrides"]),
                    len(envelope["rows"]),
                    None if onsets is None else len(onsets),
                )
            )
    return sessions, t0_rows, retrospective_rows


def read_manifest(path):
    """`sessions.csv` を読み、`{(participant_id, session_id): (os, phase)}` を返す。

    ⚠️ 同じ `(participant_id, session_id)` の行が 2 本以上あれば `ManifestError` (黙って片方を採らない)。
    列の欠け・列数の違う行・空のキーも同じ。値は文字列のまま読む (数字に見えるセッション名を数値にしない)。
    """
    path = Path(path)
    manifest, first_line = {}, {}
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            missing = [column for column in MANIFEST_CSV_COLUMNS if column not in (reader.fieldnames or [])]
            if missing:
                raise ManifestError(f"{path}: 列が無い: {missing} (★ 契約は {','.join(MANIFEST_CSV_COLUMNS)})")
            for row in reader:
                line = reader.line_num
                if None in row or any(row[column] is None for column in MANIFEST_CSV_COLUMNS):
                    raise ManifestError(f"{path}:{line}: 列数がヘッダと合わない行")
                participant, session, os_name, phase = (row[column].strip() for column in MANIFEST_CSV_COLUMNS)
                if not participant or not session:
                    raise ManifestError(f"{path}:{line}: participant_id / session_id が空 (★ 結合キーに使えない)")
                key = (participant, session)
                if key in manifest:
                    raise ManifestError(
                        f"{path}:{line}: (participant_id, session_id)=({participant!r}, {session!r}) が重複している "
                        f"(★ 行 {first_line[key]} と同じキー。黙って片方を採らない)"
                    )
                manifest[key] = (os_name or None, phase or None)
                first_line[key] = line
    except (UnicodeDecodeError, csv.Error) as e:
        raise ManifestError(f"{path}: CSV として読めない: {e}") from e
    return manifest


def guard_paths(root, out, sessions):
    """`--root` / `--out` / `--sessions` のガード。通れば絶対パスの `out` を返す。違反は `pg1.GuardError`。

    ★ `--root` / `--out` の判定は PG-1 の CLI (issue 002) と同じ (`p1_pg1_distribution.guard_paths`):
    `--out` が git の作業ツリーの中・既に在る・判定そのものが失敗したときは拒否する。
    """
    if sessions is not None and not Path(sessions).is_file():
        raise pg1.GuardError(f"--sessions がファイルではない: {sessions}")
    return pg1.guard_paths(root, out)


def _create_table(con, name, columns, key_count):
    definitions = ", ".join(f"{column} {sql_type}" for column, sql_type in columns)
    key = ", ".join(column for column, _ in columns[:key_count])
    con.execute(f"CREATE TABLE {name} ({definitions}, PRIMARY KEY ({key}))")


def _insert(con, name, columns, rows):
    if rows:
        placeholders = ", ".join("?" for _ in columns)
        con.executemany(f"INSERT INTO {name} VALUES ({placeholders})", rows)


def _remove_partial(out_path):
    for path in (out_path, Path(f"{out_path}.wal")):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass  # ★ 消せなくても、元の失敗の報告を優先する


def write_db(duckdb, out_path, sessions, t0_rows, retrospective_rows, manifest):
    """DB を作る。⚠️ 失敗したら書きかけの DB を消して例外を伝える。"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_rows = [(participant, session, os_name, phase) for (participant, session), (os_name, phase) in sorted(manifest.items())]
    try:
        con = duckdb.connect(str(out_path))
        try:
            _create_table(con, "sessions", SESSIONS_COLUMNS, len(_KEY3))
            _create_table(con, "episodes_t0", EPISODES_T0_COLUMNS, len(_KEY4))
            _create_table(con, "episodes_retrospective", EPISODES_RETROSPECTIVE_COLUMNS, len(_KEY4))
            _create_table(con, "manifest", MANIFEST_COLUMNS, 2)
            _insert(con, "sessions", SESSIONS_COLUMNS, sessions)
            _insert(con, "episodes_t0", EPISODES_T0_COLUMNS, t0_rows)
            _insert(con, "episodes_retrospective", EPISODES_RETROSPECTIVE_COLUMNS, retrospective_rows)
            _insert(con, "manifest", MANIFEST_COLUMNS, manifest_rows)
            con.execute(_VIEW_SQL)
        finally:
            con.close()
    except BaseException:
        _remove_partial(out_path)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="build_p1_episode_db.py",
        description="3 極の出力から極ごとの episode 表を使い捨ての DuckDB に作る (ime_overlap・restart は別の表)。",
    )
    parser.add_argument("--root", required=True, help="<root>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json")
    parser.add_argument("--out", required=True, help="出力 DuckDB (★ repo の外。既存のファイルは上書きしない)")
    parser.add_argument("--sessions", default=None, help="sessions.csv (participant_id,session_id,os,phase)。無ければ os / manifest_phase は NULL")
    args = parser.parse_args(argv)  # ⚠️ 引数の不備は argparse が exit 2 にする

    try:
        import duckdb  # noqa: PLC0415 -- 遅延 import (無ければ traceback ではなく exit 5)
    except ImportError:
        print(f"[{TOOL}] NG: duckdb が無い。run: pip install -r scripts/requirements-dev.txt", file=sys.stderr)
        return EXIT_NO_DUCKDB

    try:
        out_path = guard_paths(args.root, args.out, args.sessions)
    except pg1.GuardError as e:
        print(f"[{TOOL}] NG (引数・出力先のガード): {e}", file=sys.stderr)
        return EXIT_GUARD
    try:
        manifest = read_manifest(args.sessions) if args.sessions is not None else {}
        sessions, t0_rows, retrospective_rows = collect(args.root)
    except fio.FeaturesIOError as e:  # LayoutError / EnvelopeError / ManifestError
        print(f"[{TOOL}] NG (レイアウト・封筒・sessions.csv の形): {e}", file=sys.stderr)
        return EXIT_LAYOUT
    except OSError as e:
        print(f"[{TOOL}] NG (読めない): {e}", file=sys.stderr)
        return EXIT_IO
    try:
        write_db(duckdb, out_path, sessions, t0_rows, retrospective_rows, manifest)
    except (duckdb.Error, OSError) as e:
        print(f"[{TOOL}] NG (DB を作れない): {e}", file=sys.stderr)
        return EXIT_IO
    print(
        f"[{TOOL}] OK: sessions={len(sessions)} (セッション x 極) / episodes_t0={len(t0_rows)} / "
        f"manifest={len(manifest)} → {out_path}"
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
