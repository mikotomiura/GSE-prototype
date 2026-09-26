"""P1 の grouped nested CV の fold を組み、fold × 一式 × 極の 3 metric の「素の値」を表にする CLI (issue 005)。

## ★ 何をするか (⚠️ 表まで。選ばない)

事前宣言 §2.2 の grouped nested CV の **fold** を組み、issue 004 の格子の出力
(`scripts/p1_run_grid.py` の `--out`) から、**fold × 一式 × 極ごとの 3 metric の素の値**を計算した表を出す。

    python scripts/p1_select.py --grid-out <格子の出力> --labels <転帰 CSV> --out <出力 JSON> [--prereg <凍結 JSON>]

⚠️★★★ **fold をまたぐ集約・同点の崩し方・最終の 1 つの選び方は実装しない** (`decisions.md` 判断 18・研究者裁定)。
事前宣言 §2.2 / §2.3 はこれらを決めておらず (例: inner の検証側が 1 人だと変動係数は定義上 0)、実装者が決めると
手続きを実装の中で決めることになる。→ PG-1 と同じ新版 (v1.2) で宣言してから、別タスクで実装する。
出力に「選ばれた一式」を表すキーは作らない (`test_no_selection_output`・acceptance の静的検査)。

## ★ fold (`make_folds`)

- group = 参加者。outer = **leave-one-participant-out** (N 人なら N 個・各 1 人が test)。
  inner = その訓練側 (N − 1 人) の **grouped k-fold** で、`k = min(5, N − 1)` (★ N は全参加者数)。
- seed は**凍結 JSON の `search_protocol.seed` から読む** (コードに書き写さない)。
  ★ 割り当ては `random` を使わず、`sha256(seed, outer の test の参加者, 参加者)` の昇順に並べて k 個へ**巡回で**配る
  (Python の版・OS に依らず同じ fold になる。seed を変えると並びが変わる)。
- ★ **fold は 1 回だけ作り、全一式・全極で同じ fold を使う**。参加者の母集団は `grid_manifest.json` の `sessions` から決める
  (episode から列挙しない ＝ onset が 0 本の参加者も fold に入る)。
- ⚠️ **N < 3 は拒否する** (exit 3・判断 21): N = 2 で `k = 1` になり grouped k-fold が組めない。事前宣言はこの場合を
  定めていないので、手続きを発明しない。

## ★ 入力

- `--grid-out`: `p1_run_grid.py` の出力。⚠️ **`grid_manifest.json` に列挙されたファイルだけを、sha256 を確かめて読む**
  (`complete: true` でない・列挙されたファイルが無い・sha256 が合わない・列挙が configs × sessions × 極と一致しない、は exit 3。
  列挙されていないファイルは読まない)。
- `--labels`: 転帰のラベル (CSV)。列は `config_id,participant_id,session_id,pole,t0_ms,outcome` で 1 行 1 episode
  (★ 転帰は**外から渡す**・判断 11。episode の特徴量から転帰を作らない)。`outcome` は不透明な文字列で、
  異なる文字列が異なる転帰カテゴリになる (語彙は外が決める)。同じキー (`config_id, participant_id, session_id, pole, t0_ms`) の
  行が 2 本以上あれば、`outcome` が同じでも違っても exit 3。
- PG-1 の値 (一人あたり episode 数の下限 `L`) は `pg1.min_episodes_per_participant` (`p1_run_grid.declared_pg1_min`・判断 19)。
  ⚠️ 無い・型や範囲が違えば **exit 6**。⚠️★ **PG-1 は転帰を見ない**ので、この確認は `--labels` の中身を読む**前**に行う
  (`--labels` は存在と読み取り可否しか確かめない)。

## ★ episode の対応 (⚠️ `project_pg1` を使わない理由)

`p1_features_io.project_pg1` は onset の**本数**だけを返し、時刻 (`t0_ms`) を意図して返さない (PG-1 が時系列を見ないため)。
ラベルとの対応には `t0_ms` が要るので、ここは検証済みの封筒 (`load_session`) の行から `stall_onset.is_onset` と `t0_ms` だけを読む。
⚠️ `p1_features_io.py` は変更しない (PG-1 の射影を広げない)。

episode = **適用可 (`pole_applicable`) かつ規則 (d) で除外されていない**セッションの onset 行。
- 規則 (d): manifest の `excluded_rule_d` に載った (一式, 参加者, セッション, 極) は表から外し、出力の `excluded` に載せる。
  ★ さらに封筒 `config` を `is_valid_search_run` で**独立に判定し直し**、manifest に載っていなくても偽なら外す
  (`listed_in_manifest: false` で区別する)。
- `pole_applicable=false` のセッションは episode 数に入れず、`n_not_applicable_sessions` に数える (判断 12)。
- ⚠️ 極ごとに独立: 極の値を混ぜない (事前宣言 §3 規律 4)。

## ★ 3 metric の素の値 (事前宣言 §2.3・`metrics_for`)

参加者の集合 S (fold の一辺) に対し、**その (一式, 極) で使えるセッション (適用可・除外されていない) を 1 本以上持つ参加者**だけを
数える。持たない参加者は `n_participants_without_applicable_sessions` に数え、metric に入れない。

| 列 | 意味 |
|---|---|
| `min_episodes` / `meets_min_episodes` | 主: 参加者ごとの episode 数の最小値と、それが `L` 以上か (数える参加者が 0 人なら両方 `null`) |
| `outcome_counts` / `n_outcome_categories` | 副: 転帰カテゴリごとの件数と、カテゴリ数 (1 なら退化)。ラベルの無い episode は `n_episodes_unlabeled` |
| `episodes_cv` | 第 3: 参加者間の episode 数の `pstdev / mean` (参加者 1 人以下・平均 0 は `null`。⚠️ 0 で埋めない) |

⚠️ 予測成績を metric にしない (§2.3・ADR-008 D4 の会計規則)。

## ★ 出力 (JSON)

    {
      "provenance": {"tool", "prereg_source", "prereg_sha256_prefix", "seed", "k_inner", "n_participants",
                     "pg1_min_episodes_per_participant", "grid_prereg_source", "grid_prereg_sha256_prefix"},
      "folds": [{"outer_fold", "test": [P], "train": [...], "inner_folds": [{"inner_fold", "train": [...], "validation": [...]}]}],
      "table": [1 行 = (outer_fold, inner_fold または "outer_test", side = train / validation / test, config_id, role, pole) + metric],
      "excluded": [{"config_id", "participant", "session", "pole", "reasons": [...], "listed_in_manifest"}],
      "label_mismatch": {"n_labels", "labels_without_episode", "episodes_without_label", "by_config_pole": [...]}
    }

- `role` は `selection` / `sensitivity_only` (manifest の `kind` から)。★ 感度の一式は選択に入れない (表の上で区別できる)。
- `label_mismatch`: episode と対応しないラベル・ラベルの無い episode を**数えて**載せる (黙って捨てない)。
  ★ 数えるのは (一式, 極) ごとの episode (同じ episode が一式・極をまたいで重複して数えられうる)。
- `--out` は既存のファイルを上書きしない (★ 出し直しで forking paths を作らない)。⚠️ 出力は repo の外に置く。

## exit

| code | 意味 |
|---|---|
| 0 | OK |
| 1 | 出力を書けない |
| 2 | 引数・入力・出力先のガード (`--out` が既にある / git の作業ツリーの中・`--grid-out` がディレクトリでない・`--labels` を読めない・`--prereg` を読めない) |
| 3 | 入力の形が違う (manifest / 封筒 / ラベルの中身・重複キー・sha256 不一致・`--prereg` の形・seed・参加者が 3 人未満) |
| 6 | PG-1 未宣言 (⚠️ `--labels` の中身も格子の中身も読まない) |

使い方 (テスト): `python -m unittest scripts.tests.test_p1_select -v` (repo 直下から)。
"""

import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

import p1_features_io as fio
import p1_run_grid as grid
from p1_bounds import POLES
from p1_pg1_distribution import GuardError, _inside_git_work_tree
from p1_run_grid import _emit, _sha256_file

TOOL = "p1_select"
EXIT_OK, EXIT_WRITE_FAILED, EXIT_GUARD, EXIT_BAD_INPUT, EXIT_PG1_UNDECLARED = 0, 1, 2, 3, 6

MIN_PARTICIPANTS = 3
INNER_K_MAX = 5
OUTER_TEST = "outer_test"
LABEL_COLUMNS = ("config_id", "participant_id", "session_id", "pole", "t0_ms", "outcome")
ROLE_BY_KIND = {"selection": "selection", "sensitivity": "sensitivity_only"}

_CONFIG_ID_RE = re.compile(r"[0-9A-Za-z_][0-9A-Za-z_.=-]*")
_SESSION_RE = re.compile(r"[0-9A-Za-z_][0-9A-Za-z_.-]*")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_T0_RE = re.compile(r"[0-9]+")


class InputError(Exception):
    """格子の出力・ラベル・事前宣言の形が違う、または参加者が足りない (exit 3)。"""


def _require(condition, message):
    if not condition:
        raise InputError(message)


def _is_text(value):
    return isinstance(value, str) and value != ""


# ── fold ──────────────────────────────────────────────────────────────


def k_inner(n_participants):
    """inner の fold 数 `min(5, N − 1)` (★ N は全参加者数・事前宣言 §2.2)。"""
    return min(INNER_K_MAX, n_participants - 1)


def _rank(seed, outer_test, participant):
    """割り当ての並び順の鍵。⚠️ `random` を使わない (版・OS に依らず同じ並びになる)。"""
    return hashlib.sha256(f"{seed}\x1f{outer_test}\x1f{participant}".encode("utf-8")).hexdigest()


def make_folds(participants, seed):
    """outer (leave-one-participant-out) と各 outer の inner (grouped k-fold) を組む。

    ★ 決定的 (同じ参加者の集合・同じ seed なら、入力の並びに依らず同じ fold)。参加者 (group) が 1 つの fold の 2 つの側に
    またがらない。⚠️ 参加者が 3 人未満・重複・seed が bool でない int でない、は `InputError` (判断 21)。
    """
    people = sorted(participants)
    _require(len(set(people)) == len(people), f"参加者に重複がある: {people}")
    _require(type(seed) is int, f"seed が整数でない: {seed!r}")
    _require(
        len(people) >= MIN_PARTICIPANTS,
        f"参加者が {len(people)} 人 (★ {MIN_PARTICIPANTS} 人未満は nested CV を組まない: k = min(5, N − 1) が N = 2 で 1 になり "
        "grouped k-fold が組めない。事前宣言はこの場合を定めていない・判断 21)",
    )
    k = k_inner(len(people))
    folds = []
    for outer, test in enumerate(people):
        train = [person for person in people if person != test]
        ordered = sorted(train, key=lambda person: _rank(seed, test, person))
        inner_folds = []
        for j in range(k):
            validation = sorted(ordered[j::k])  # ★ 巡回で配る (各 fold は 1 人以上・大きさの差は高々 1)
            inner_folds.append(
                {
                    "inner_fold": j,
                    "train": [person for person in train if person not in validation],
                    "validation": validation,
                }
            )
        folds.append({"outer_fold": outer, "test": [test], "train": train, "inner_folds": inner_folds})
    return folds


def declared_seed(prereg):
    """凍結 JSON の `search_protocol.seed` (bool でない int)。⚠️ 無い・型が違えば `PreregError` (コードに書き写さない)。"""
    protocol = prereg.get("search_protocol")
    seed = protocol.get("seed") if isinstance(protocol, dict) else None
    if type(seed) is not int:
        raise grid.PreregError(f"search_protocol.seed が整数でない: {seed!r} (★ seed は凍結 JSON から読む)")
    return seed


# ── 入力・出力先のガード ────────────────────────────────────────────────


def guard_out(out):
    """`--out` のガード。通れば絶対パスを返す。⚠️ 作らない (作るのは全ての検査を通った後)。"""
    out_path = Path(out).resolve()
    if out_path.exists():
        raise GuardError(f"--out が既にある (★ 上書きしない。出し直しで forking paths を作らない): {out_path}")
    probe = out_path.parent
    while not probe.exists():  # ★ 実在する最も近い祖先で判定する (祖先が作業ツリーの中なら、その下も中)
        probe = probe.parent
    if not probe.is_dir():
        raise GuardError(f"--out の親がディレクトリではない: {probe}")
    if _inside_git_work_tree(probe):
        raise GuardError(f"--out が git の管理下: {out_path} (★ 出力は repo の外に置く)")
    return out_path


def guard_grid_dir(grid_out):
    path = Path(grid_out)
    if not path.is_dir():
        raise GuardError(f"--grid-out がディレクトリではない: {path}")
    return path


def guard_labels(labels):
    """`--labels` の存在と読み取り可否だけを見る。⚠️ 中身は読まない (PG-1 の後まで転帰を見ない)。"""
    path = Path(labels)
    if not path.is_file() or not os.access(path, os.R_OK):
        raise GuardError(f"--labels を読めない (無い・ファイルでない): {path}")
    return path


# ── manifest ───────────────────────────────────────────────────────────


def _reject_constant(name):
    raise ValueError(f"JSON に非有限の定数がある: {name}")


def _load_json(path, what):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f, parse_constant=_reject_constant)
    except (OSError, ValueError) as e:  # JSONDecodeError / UnicodeDecodeError は ValueError の子
        raise InputError(f"{what}を読めない: {path}: {e}") from e


def _load_sessions(manifest):
    raw = manifest.get("sessions")
    _require(isinstance(raw, list) and raw, "sessions が空でない配列ではない")
    sessions = []
    for i, item in enumerate(raw):
        _require(isinstance(item, dict), f"sessions[{i}] がオブジェクトではない")
        participant, session = item.get("participant"), item.get("session")
        _require(
            isinstance(participant, str) and fio.P_ID_RE.fullmatch(participant) is not None,
            f"sessions[{i}].participant が P-ID の形でない: {participant!r}",
        )
        _require(
            isinstance(session, str) and _SESSION_RE.fullmatch(session) is not None,
            f"sessions[{i}].session がセッション名の形でない: {session!r}",
        )
        sessions.append((participant, session))
    _require(len(set(sessions)) == len(sessions), "sessions に重複がある")
    sessions.sort()
    participants = sorted({participant for participant, _ in sessions})
    _require(
        type(manifest.get("n_sessions")) is int and manifest["n_sessions"] == len(sessions),
        f"n_sessions が sessions の数 ({len(sessions)}) と合わない: {manifest.get('n_sessions')!r}",
    )
    _require(
        type(manifest.get("n_participants")) is int and manifest["n_participants"] == len(participants),
        f"n_participants が sessions の参加者数 ({len(participants)}) と合わない: {manifest.get('n_participants')!r}",
    )
    return sessions, participants


def _load_configs(manifest):
    raw = manifest.get("configs")
    _require(isinstance(raw, list) and raw, "configs が空でない配列ではない")
    configs = []
    for i, item in enumerate(raw):
        _require(isinstance(item, dict), f"configs[{i}] がオブジェクトではない")
        config_id, kind = item.get("id"), item.get("kind")
        _require(
            isinstance(config_id, str) and _CONFIG_ID_RE.fullmatch(config_id) is not None,
            f"configs[{i}].id が一式 ID の形でない: {config_id!r}",
        )
        _require(kind in ROLE_BY_KIND, f"configs[{i}].kind が知らない種類: {kind!r} (知っている種類: {sorted(ROLE_BY_KIND)})")
        configs.append({"id": config_id, "role": ROLE_BY_KIND[kind]})
    ids = [config["id"] for config in configs]
    _require(len(set(ids)) == len(ids), "configs に ID の重複がある")
    return configs


def _load_outputs(manifest, configs, sessions):
    """`{相対パス: sha256}`。⚠️ 列挙が configs × sessions × 極と一致しなければ `InputError` (列挙されていないファイルは読まない)。"""
    raw = manifest.get("outputs")
    _require(isinstance(raw, list), "outputs が配列ではない")
    listed = {}
    for i, item in enumerate(raw):
        _require(isinstance(item, dict), f"outputs[{i}] がオブジェクトではない")
        path, sha = item.get("path"), item.get("sha256")
        _require(isinstance(path, str), f"outputs[{i}].path が文字列でない: {path!r}")
        _require(isinstance(sha, str) and _SHA256_RE.fullmatch(sha) is not None, f"outputs[{i}].sha256 が sha256 (小文字 16 進 64 桁) でない")
        _require(path not in listed, f"outputs に同じパスが 2 回ある: {path}")
        listed[path] = sha
    expected = {
        f"{config['id']}/{participant}/{session}/{pole}.json"
        for config in configs
        for participant, session in sessions
        for pole in POLES
    }
    missing, unexpected = sorted(expected - set(listed)), sorted(set(listed) - expected)
    _require(
        not missing and not unexpected,
        f"outputs の列挙が configs × sessions × 極と一致しない (欠け {len(missing)} 件: {missing[:3]} / 余り {len(unexpected)} 件: {unexpected[:3]})",
    )
    return listed


def _load_excluded(manifest, configs, sessions):
    """`{(config_id, participant, session, pole): [reason, ...]}`。⚠️ 知らない実行を指す・重複する項目は `InputError`。"""
    raw = manifest.get("excluded_rule_d")
    _require(isinstance(raw, list), "excluded_rule_d が配列ではない")
    known_ids = {config["id"] for config in configs}
    known_sessions = set(sessions)
    excluded = {}
    for i, item in enumerate(raw):
        _require(isinstance(item, dict), f"excluded_rule_d[{i}] がオブジェクトではない")
        config_id, participant, session, pole = (item.get(key) for key in ("config_id", "participant", "session", "pole"))
        _require(config_id in known_ids, f"excluded_rule_d[{i}].config_id が configs に無い: {config_id!r}")
        _require((participant, session) in known_sessions, f"excluded_rule_d[{i}] のセッションが sessions に無い: {participant!r}/{session!r}")
        _require(pole in POLES, f"excluded_rule_d[{i}].pole が知らない極: {pole!r}")
        reasons = item.get("reasons")
        _require(
            isinstance(reasons, list) and reasons and all(_is_text(reason) for reason in reasons),
            f"excluded_rule_d[{i}].reasons が空でない文字列の配列ではない: {reasons!r}",
        )
        key = (config_id, participant, session, pole)
        _require(key not in excluded, f"excluded_rule_d に同じ実行が 2 回ある: {key}")
        excluded[key] = list(reasons)
    return excluded


def load_manifest(grid_dir):
    """`grid_manifest.json` を検査して読む。⚠️ `complete: true` でない・形が違えば `InputError` (exit 3)。"""
    manifest = _load_json(Path(grid_dir) / grid.MANIFEST_NAME, "manifest")
    _require(isinstance(manifest, dict), "manifest のトップが JSON オブジェクトではない")
    _require(manifest.get("tool") == grid.TOOL, f"manifest.tool が {grid.TOOL!r} でない: {manifest.get('tool')!r}")
    _require(
        manifest.get("complete") is True,
        "manifest が complete: true でない (★ 実行が終わっていない・途中で失敗した格子は読まない)",
    )
    sessions, participants = _load_sessions(manifest)
    configs = _load_configs(manifest)
    return {
        "sessions": sessions,
        "participants": participants,
        "configs": configs,
        "outputs": _load_outputs(manifest, configs, sessions),
        "excluded": _load_excluded(manifest, configs, sessions),
        "prereg_source": manifest.get("prereg_source"),
        "prereg_sha256_prefix": manifest.get("prereg_sha256_prefix"),
    }


# ── ラベル ─────────────────────────────────────────────────────────────


def load_labels(path):
    """転帰ラベルの CSV を読み、`{(config_id, participant_id, session_id, pole, t0_ms): outcome}` を返す。

    ⚠️ 読めなければ `GuardError` (exit 2)・ヘッダ / 列数 / 空の項目 / `t0_ms` の形が違う・同じキーの行が 2 本以上
    (`outcome` が同じでも違っても) は `InputError` (exit 3)。
    """
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise GuardError(f"--labels を読めない: {path}: {e}") from e
    _require(rows and tuple(rows[0]) == LABEL_COLUMNS, f"--labels のヘッダが {','.join(LABEL_COLUMNS)} でない: {rows[0] if rows else '(空)'}")
    labels, first_line = {}, {}
    for lineno, row in enumerate(rows[1:], start=2):
        if not row:  # 空行
            continue
        _require(len(row) == len(LABEL_COLUMNS), f"--labels {lineno} 行目: 列数が {len(row)} (期待: {len(LABEL_COLUMNS)})")
        config_id, participant_id, session_id, pole, t0_text, outcome = row
        for name, value in zip(LABEL_COLUMNS, row):
            _require(value != "", f"--labels {lineno} 行目: {name} が空")
        _require(_T0_RE.fullmatch(t0_text) is not None, f"--labels {lineno} 行目: t0_ms が 0 以上の整数でない: {t0_text!r}")
        key = (config_id, participant_id, session_id, pole, int(t0_text))
        if key in labels:  # ⚠️ `_require` にしない (メッセージの f-string が新規キーでも先に評価されて落ちる)
            raise InputError(
                f"--labels {lineno} 行目: 同じキー (1 行 1 episode) が {first_line[key]} 行目にもある "
                "(★ outcome が同じでも違っても拒否する)"
            )
        labels[key] = outcome
        first_line[key] = lineno
    return labels


# ── 格子の読み込みと単位ごとの集計 ──────────────────────────────────────


def _new_unit():
    return {"usable_sessions": 0, "not_applicable_sessions": 0, "excluded_sessions": 0, "outcomes": []}


def _verified_path(grid_dir, relative, expected_sha):
    path = Path(grid_dir) / relative
    _require(path.is_file(), f"manifest に列挙されたファイルが無い: {relative}")
    actual = _sha256_file(path)
    _require(actual == expected_sha, f"sha256 が manifest と合わない: {relative} (manifest {expected_sha[:16]}… / 実際 {actual[:16]}…)")
    return path


def _onset_times(envelope, where):
    """onset 行の `t0_ms` の列。⚠️ onset なのに `t0_ms` が 0 以上の整数でない・重複するなら `InputError`。"""
    times = []
    for i, row in enumerate(envelope["rows"]):
        onset = row["stall_onset"]
        if not onset["is_onset"]:
            continue
        t0 = onset.get("t0_ms")
        _require(type(t0) is int and t0 >= 0, f"{where}: rows[{i}] は onset なのに stall_onset.t0_ms が 0 以上の整数でない: {t0!r}")
        times.append(t0)
    _require(len(set(times)) == len(times), f"{where}: t0_ms が重複する onset がある (★ ラベルの鍵が一意にならない)")
    return times


def load_units(grid_dir, manifest, labels):
    """格子の出力を読み、`(units, excluded, label_mismatch)` を返す。

    `units[(config_id, pole)][participant]` = `{"usable_sessions", "not_applicable_sessions", "excluded_sessions", "outcomes"}`
    (`outcomes` は episode ごとの転帰。ラベルの無い episode は `None`)。
    ⚠️ manifest に列挙されたファイルだけを、sha256 を確かめて読む。
    """
    units, excluded = {}, []
    unlabeled, matched = Counter(), set()
    for config in manifest["configs"]:
        config_id = config["id"]
        for pole in POLES:
            units[(config_id, pole)] = {participant: _new_unit() for participant in manifest["participants"]}
        for participant, session in manifest["sessions"]:
            paths = {}
            for pole in POLES:
                relative = f"{config_id}/{participant}/{session}/{pole}.json"
                paths[pole] = _verified_path(grid_dir, relative, manifest["outputs"][relative])
            envelopes = fio.load_session(paths)
            for pole in POLES:
                envelope = envelopes[pole]
                where = f"{config_id}/{participant}/{session}/{pole}.json"
                unit = units[(config_id, pole)][participant]
                listed_reasons = manifest["excluded"].get((config_id, participant, session, pole))
                invalid = not grid.is_valid_search_run(envelope["config"])
                if listed_reasons is not None or invalid:
                    unit["excluded_sessions"] += 1
                    reasons = list(listed_reasons or [])
                    if invalid and grid.REASON_RULE_D not in reasons:
                        reasons.append(grid.REASON_RULE_D)
                    excluded.append(
                        {
                            "config_id": config_id,
                            "participant": participant,
                            "session": session,
                            "pole": pole,
                            "reasons": reasons,
                            "listed_in_manifest": listed_reasons is not None,
                        }
                    )
                    continue
                if not envelope["config"]["pole_applicable"]:
                    unit["not_applicable_sessions"] += 1  # ★ episode 数に入れない (baseline と恒等の出力を二重に数えない)
                    continue
                unit["usable_sessions"] += 1
                for t0_ms in _onset_times(envelope, where):
                    key = (config_id, participant, session, pole, t0_ms)
                    outcome = labels.get(key)
                    if outcome is None:
                        unlabeled[(config_id, pole)] += 1
                    else:
                        matched.add(key)
                    unit["outcomes"].append(outcome)
    excluded.sort(key=lambda item: (item["config_id"], item["participant"], item["session"], item["pole"]))
    orphan = Counter((key[0], key[3]) for key in labels if key not in matched)
    by_config_pole = [
        {
            "config_id": config_id,
            "pole": pole,
            "labels_without_episode": orphan[(config_id, pole)],
            "episodes_without_label": unlabeled[(config_id, pole)],
        }
        for config_id, pole in sorted(set(orphan) | set(unlabeled))
    ]
    label_mismatch = {
        "n_labels": len(labels),
        "labels_without_episode": sum(orphan.values()),
        "episodes_without_label": sum(unlabeled.values()),
        "by_config_pole": by_config_pole,
    }
    return units, excluded, label_mismatch


# ── 3 metric の素の値 ───────────────────────────────────────────────────


def episodes_cv(counts):
    """`pstdev / mean`。⚠️ 参加者が 1 人以下・平均 0 は `None` (0 で埋めない)。"""
    if len(counts) < 2:
        return None
    mean = statistics.mean(counts)
    if mean == 0:
        return None
    return statistics.pstdev(counts) / mean


def metrics_for(per_participant, participants, min_episodes):
    """参加者の集合 `participants` の 3 metric の素の値 (★ 1 つの (一式, 極) について)。

    `per_participant[p]` は `{"usable_sessions", "not_applicable_sessions", "excluded_sessions", "outcomes"}`。
    使えるセッション (`usable_sessions`) を 1 本以上持つ参加者だけを数え、持たない参加者は
    `n_participants_without_applicable_sessions` に数える。⚠️ 集約も選択もしない (1 つの集合の素の値だけ)。
    """
    counted = [participant for participant in participants if per_participant[participant]["usable_sessions"] > 0]
    counts = [len(per_participant[participant]["outcomes"]) for participant in counted]
    outcomes = [outcome for participant in counted for outcome in per_participant[participant]["outcomes"]]
    outcome_counts = Counter(outcome for outcome in outcomes if outcome is not None)
    return {
        "n_participants": len(participants),
        "n_participants_without_applicable_sessions": len(participants) - len(counted),
        "n_not_applicable_sessions": sum(per_participant[participant]["not_applicable_sessions"] for participant in participants),
        "n_excluded_sessions": sum(per_participant[participant]["excluded_sessions"] for participant in participants),
        "min_episodes": min(counts) if counts else None,
        "meets_min_episodes": (min(counts) >= min_episodes) if counts else None,
        "n_episodes": len(outcomes),
        "n_episodes_unlabeled": sum(1 for outcome in outcomes if outcome is None),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "n_outcome_categories": len(outcome_counts),
        "episodes_cv": episodes_cv(counts),
    }


def build_table(folds, configs, units, min_episodes):
    """fold × 一式 × 極の表。⚠️ 全一式・全極で同じ `folds` を使う (fold は 1 回だけ作る)。"""
    rows = []

    def emit(outer_fold, inner_fold, side, participants):
        for config in configs:
            for pole in POLES:
                rows.append(
                    {
                        "outer_fold": outer_fold,
                        "inner_fold": inner_fold,
                        "side": side,
                        "config_id": config["id"],
                        "role": config["role"],
                        "pole": pole,
                        **metrics_for(units[(config["id"], pole)], participants, min_episodes),
                    }
                )

    for fold in folds:
        for inner in fold["inner_folds"]:
            emit(fold["outer_fold"], inner["inner_fold"], "train", inner["train"])
            emit(fold["outer_fold"], inner["inner_fold"], "validation", inner["validation"])
        emit(fold["outer_fold"], OUTER_TEST, "test", fold["test"])
    return rows


def render(result):
    """出力 JSON の文字列。⚠️ `table` だけは 1 行 1 要素にする (数万行を indent で展開すると読めない)。"""
    lines = ["{"]
    keys = list(result)
    for i, key in enumerate(keys):
        value = result[key]
        if key == "table":
            rows = [json.dumps(row, ensure_ascii=False, allow_nan=False) for row in value]
            body = "[\n" + ",\n".join("    " + row for row in rows) + "\n  ]" if rows else "[]"
        else:
            body = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2).replace("\n", "\n  ")
        lines.append(f"  {json.dumps(key)}: {body}{',' if i < len(keys) - 1 else ''}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="p1_select.py",
        description="P1 の grouped nested CV の fold を組み、fold × 一式 × 極の 3 metric の素の値を表にする (集約も選択もしない)。",
    )
    parser.add_argument("--grid-out", required=True, help="p1_run_grid.py の出力ディレクトリ (grid_manifest.json を含む)")
    parser.add_argument("--labels", required=True, help="転帰ラベルの CSV (config_id,participant_id,session_id,pole,t0_ms,outcome)")
    parser.add_argument("--out", required=True, help="出力 JSON (★ repo の外。既存のファイルは上書きしない)")
    parser.add_argument("--prereg", default=None, help="凍結 JSON の新版 (既定: src-tauri/prereg/p1-episode.json)")
    args = parser.parse_args(argv)  # ⚠️ 引数の不備 (--labels 無しを含む) は argparse が exit 2 にする

    try:
        # ★ 順序: 副作用の無いガード (2) → 事前宣言 (2/3) → PG-1 (6) → seed (3) → 格子 (3) → ラベルの中身 (2/3)
        #   ⚠️ PG-1 は転帰を見ないので、ラベルの中身を読むのは PG-1 の確認の後
        out_path = guard_out(args.out)
        grid_dir = guard_grid_dir(args.grid_out)
        labels_path = guard_labels(args.labels)
        prereg_path, prereg_source = grid.resolve_prereg(args.prereg)
        prereg, prereg_sha256_prefix = grid.load_prereg(prereg_path)
        min_episodes = grid.declared_pg1_min(prereg)
        seed = declared_seed(prereg)
        manifest = load_manifest(grid_dir)
        folds = make_folds(manifest["participants"], seed)  # ★ 1 回だけ作る (N < 3 はここで拒否)
        labels = load_labels(labels_path)
        units, excluded, label_mismatch = load_units(grid_dir, manifest, labels)
        result = {
            "provenance": {
                "tool": TOOL,
                "prereg_source": prereg_source,
                "prereg_sha256_prefix": prereg_sha256_prefix,
                "seed": seed,
                "k_inner": k_inner(len(manifest["participants"])),
                "n_participants": len(manifest["participants"]),
                "pg1_min_episodes_per_participant": min_episodes,
                "grid_prereg_source": manifest["prereg_source"],
                "grid_prereg_sha256_prefix": manifest["prereg_sha256_prefix"],
            },
            "folds": folds,
            "table": build_table(folds, manifest["configs"], units, min_episodes),
            "excluded": excluded,
            "label_mismatch": label_mismatch,
        }
        text = render(result)
    except GuardError as e:
        _emit(sys.stderr, f"[select] NG (guard): {e}")
        return EXIT_GUARD
    except grid.Pg1UndeclaredError as e:
        _emit(sys.stderr, f"[select] NG (PG-1): {e}")
        return EXIT_PG1_UNDECLARED
    except (InputError, grid.PreregError, fio.FeaturesIOError) as e:
        _emit(sys.stderr, f"[select] NG (input): {e}")
        return EXIT_BAD_INPUT

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "x", encoding="utf-8", newline="\n") as f:  # ★ "x": 既存を上書きしない
            f.write(text)
    except OSError as e:
        _emit(sys.stderr, f"[select] NG (write): 出力を書けない: {e}")
        return EXIT_WRITE_FAILED

    if manifest["prereg_sha256_prefix"] != prereg_sha256_prefix:
        _emit(
            sys.stderr,
            "[select] note: 格子を回した事前宣言の sha256 (%s) と --prereg の sha256 (%s) が違う (provenance に両方載せた)"
            % (manifest["prereg_sha256_prefix"], prereg_sha256_prefix),
        )
    if label_mismatch["labels_without_episode"] or label_mismatch["episodes_without_label"]:
        _emit(
            sys.stderr,
            "[select] note: episode と対応しないラベル %d 件・ラベルの無い episode %d 件 (label_mismatch)"
            % (label_mismatch["labels_without_episode"], label_mismatch["episodes_without_label"]),
        )
    if excluded:
        _emit(sys.stderr, f"[select] note: {len(excluded)} run(s) excluded by rule (d) / param mismatch (see excluded)")
    _emit(
        sys.stdout,
        f"[select] OK: {len(manifest['participants'])} participants, {len(manifest['configs'])} configs, "
        f"{len(result['table'])} table rows -> {out_path}",
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
