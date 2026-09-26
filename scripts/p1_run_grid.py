"""P1 の探索格子 (選択 27 + 感度 OFAT 4) の実行器と、規則 (d) の除外 (issue 004)。

## ★ 何をするか

事前宣言 §2.1 の探索格子を、**凍結 JSON から組み立て**、`q` と `warmup_count` を**対で**渡して
3 極すべてで回す。`scripts/run-features-all-poles.sh` (3 極の all-or-nothing) を 1 (一式 × セッション) ごとに呼ぶ。

    python scripts/p1_run_grid.py --ndjson-root <root> --out <出力ディレクトリ> [--prereg <凍結 JSON>]

- 入力: `<ndjson-root>/<P-ID>/<session>.ndjson` (P-ID は `^P[0-9A-Za-z_-]+$`。`<session>` は拡張子を除いたファイル名)。
- 出力: `<out>/<config_id>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json` (`p1_features_io` のレイアウトと同じ形)
  と `<out>/grid_manifest.json`。
- ★ 長いセッションは release で: `GSE_REPLAY_BIN=src-tauri/target/release/gse-replay python scripts/p1_run_grid.py ...`
  (`cargo run` は 1 呼び出しごとに起動するので、31 一式 × 3 極 × セッション数だけ遅い)。

## ★ 格子 (`build_grid`)

値は**凍結 JSON の `search_space` / `search_roles` / `operational` から読む** (コードに書き写さない。例外は下の対応表だけ)。

- 選択 (`role == "selection"`): そのキーの直積 (凍結 JSON では `q` × `hole_gap_ms` × `t1a_window_ms` = 27)。
  ID 例: `sel__q=0.995__hole_gap_ms=3000__t1a_window_ms=15000`。
- 感度 (`role == "sensitivity_only"`): キーを 1 つずつ、運用値以外の値へ振る (他は運用値。凍結 JSON では `w_ms` / `b_ms` で 4 実行)。
  **Cartesian に組まない。** ID 例: `ofat__w_ms=15000`。
- ⚠️★★★ **`warmup_count` は `q` の従属変数**。全一式に `q` と `warmup_count` を**対で** `--set` する (v1.1 冒頭 (5)・判断 7:
  CLI は連動しない)。⚠️ 判定は浮動小数点の式ではなく**対応表** `WARMUP_BY_Q` で行う
  (倍精度では `⌈1/(1−q)⌉` が `q` によって 1 ずれうる)。表に無い `q` が `search_space` にあれば格子を作らない (exit 3)。
- 全一式に 6 キー (`w_ms` / `q` / `b_ms` / `hole_gap_ms` / `warmup_count` / `t1a_window_ms`) を**明示的に** `--set` する
  (⚠️ 凍結値と同じキーは封筒の `overrides` に載らないだけ。意図を `config` の値で照合するため、運用値も渡す)。

## ⚠️★★★ 規則 (d) (`is_valid_search_run`)

封筒 `config` の `warmup_count` が対応表と合わない実行は、**探索の結果に使わない**。`overrides` は凍結値から外れたキーしか
載せないので、`overrides` ではなく **`config` の値**で判定する。回した後に全封筒を `load_envelope` / `load_session` で読み直し、
次の 2 つを `excluded_rule_d` に載せる (⚠️ **ファイルは削除しない**。除外するかは manifest を読む側の責務):

- `rule_d`: `config.q` / `config.warmup_count` が対応表と合わない。
- `param_mismatch`: 意図して渡したパラメータ (6 キー) と `config` の値が違う (CLI が `--set` を無視した、など)。

## ⚠️★★★ PG-1 (事前宣言 §2.3)

PG-1 の値 (一人あたり episode 数の下限) が宣言されるまで、探索を **1 度も回さない**。値は凍結 JSON の新版のキー
`pg1.min_episodes_per_participant` (bool でない int・1 以上) を読む (判断 19)。⚠️ 無い・型や範囲が違えば **exit 6**
(`gse-replay` を 1 度も呼ばない・出力先も作らない)。値を推測で埋めない。
既定の読み先は `src-tauri/prereg/p1-episode.json` (★ 現行 1.0.0 には無いので、既定では必ず exit 6)。テストは `--prereg` で差し替える。
manifest には、どちらを使ったか (`frozen` = 既定 / `file` = `--prereg`) と、その JSON の sha256 の先頭 16 桁を刻む。

## ★ manifest は最後に確定する

全実行が終わり、全封筒の読み直しが済んでから、`grid_manifest.json` を `complete: true` と**出力ファイルごとの sha256** つきで書く
(一時名に書いて rename)。途中で失敗したら manifest を残さない (★ 後続は manifest に列挙された検証済みの成果物だけを読む)。

    {
      "tool": "p1_run_grid", "complete": true,
      "prereg_source": "frozen" | "file", "prereg_sha256_prefix": "...",
      "envelope_identity": {"prereg_version", "prereg_sha256_prefix", "hmm_version", "provenance_hmm_version", "config_source"},
      "n_participants": n, "n_sessions": n, "sessions": [{"participant", "session"}, ...],
      "configs": [{"id", "kind": "selection" | "sensitivity", "params": {6 キー}}, ...],
      "excluded_rule_d": [{"config_id", "participant", "session", "pole", "reasons": [...], "mismatch": {key: {"observed", "intended"}}}, ...],
      "outputs": [{"path": "<config_id>/<P-ID>/<session>/<pole>.json", "sha256": "..."}, ...]
    }

⚠️ `envelope_identity` は全封筒で 1 通りでなければならない (別々の binary・別の凍結値が混ざった格子を作らない)。

## exit

| code | 意味 |
|---|---|
| 0 | OK (⚠️ `excluded_rule_d` が空でなくても 0。除外は manifest に載る) |
| 1 | 実行の失敗 (3 極スクリプトが非 0・封筒の読み直しに失敗・封筒の identity が混在・manifest を書けない) |
| 2 | 引数・入力・出力先のガード (`--out` が git の作業ツリーの中 / 空でない、`--ndjson-root` のレイアウト違反、`--prereg` を読めない、bash が無い) |
| 3 | 格子を作れない (`--prereg` が JSON でない・`search_space` / `search_roles` の形が違う・対応表に無い `q`) |
| 6 | PG-1 未宣言 (⚠️ `gse-replay` を 1 度も呼ばない) |

使い方 (テスト): `python -m unittest scripts.tests.test_p1_run_grid -v` (repo 直下から)。
"""

import argparse
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from decimal import Context, Decimal, InvalidOperation
from pathlib import Path

import p1_features_io as fio
from p1_bounds import POLES
from p1_pg1_distribution import GuardError, _inside_git_work_tree

TOOL = "p1_run_grid"
EXIT_OK, EXIT_RUN_FAILED, EXIT_GUARD, EXIT_BAD_GRID, EXIT_PG1_UNDECLARED = 0, 1, 2, 3, 6

SCRIPTS_DIR = Path(__file__).resolve().parent
ALL_POLES_SCRIPT = SCRIPTS_DIR / "run-features-all-poles.sh"
DEFAULT_PREREG = SCRIPTS_DIR.parent / "src-tauri" / "prereg" / "p1-episode.json"
MANIFEST_NAME = "grid_manifest.json"

# ★ 対応表 (事前宣言 v1.1 冒頭 (5))。十進で厳密に `⌈1/(1−q)⌉` を取った値。
#   ⚠️ **コードに書き写してよい値はこれだけ** (探索空間の値は凍結 JSON から読む)。式を浮動小数点で評価しない。
WARMUP_BY_Q = {Decimal("0.99"): 100, Decimal("0.995"): 200, Decimal("0.999"): 1000}

# ★ `--set` で渡す 6 キー (`run-features-all-poles.sh` の白リストと同じ。凍結 JSON の並び順)
TUNABLE_KEYS = ("w_ms", "q", "b_ms", "hole_gap_ms", "warmup_count", "t1a_window_ms")
# 探索の対象になれるキー (`warmup_count` は従属なので、単独では振らない)
_SEARCHED_KEYS = tuple(key for key in TUNABLE_KEYS if key != "warmup_count")
_ROLES = ("selection", "sensitivity_only", "derived", "fixed")

_WIDE = Context(prec=100)  # ⚠️ 既定の 28 桁だと `normalize` が桁を丸める
_SESSION_STEM_RE = re.compile(r"[0-9A-Za-z_][0-9A-Za-z_.-]*")
_NDJSON_SUFFIX = ".ndjson"

REASON_RULE_D = "rule_d"
REASON_PARAM_MISMATCH = "param_mismatch"


class PreregError(Exception):
    """`--prereg` が JSON でない・形が違う (exit 3)。"""


class GridError(PreregError):
    """格子を作れない (exit 3)。"""


class Pg1UndeclaredError(Exception):
    """PG-1 の値が宣言されていない (exit 6)。"""


class RunError(Exception):
    """実行の失敗 (exit 1)。"""


def _emit(stream, text):
    """1 行書く。⚠️ 端末の文字コードで表せない文字 (Windows の cp932 に ⚠️ など) で落ちないよう、表せない文字は置き換える。"""
    encoding = getattr(stream, "encoding", None) or "utf-8"
    stream.write(text.encode(encoding, errors="replace").decode(encoding, errors="replace") + "\n")


# ── 規則 (d) ──────────────────────────────────────────────────────────


def _q_key(value):
    """`q` を対応表の鍵 (`normalize` 済みの `Decimal`) にする。数でない・有限でないなら `None`。

    ★ `0.990` と `0.99` は同じ鍵になる。⚠️ bool は int の subclass なので数として扱わない。
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    return number.normalize(_WIDE) if number.is_finite() else None


def is_valid_search_run(config):
    """規則 (d): 封筒 `config` の `q` が対応表にあり、`warmup_count` がその値と一致するときだけ真。

    ⚠️ 表に無い `q` (探索空間の外)・`warmup_count` が整数でない (bool / float / 文字列)・キーが無い、は偽。
    """
    if not isinstance(config, dict):
        return False
    expected = WARMUP_BY_Q.get(_q_key(config.get("q")))
    warmup = config.get("warmup_count")
    return expected is not None and type(warmup) is int and warmup == expected


# ── 事前宣言 (凍結 JSON) の読み込みと PG-1 ─────────────────────────────


def resolve_prereg(prereg_arg):
    """`(読む JSON のパス, "frozen" | "file")`。`--prereg` が無ければ既定の凍結 JSON (`frozen`)。"""
    if prereg_arg is None:
        return DEFAULT_PREREG, "frozen"
    return Path(prereg_arg), "file"


def _reject_constant(name):
    raise ValueError(f"JSON に非有限の定数がある: {name}")


def load_prereg(path):
    """事前宣言の JSON を読み、`(dict, sha256 の先頭 16 桁)` を返す。

    ⚠️ 数は `Decimal` で読む (`q` を浮動小数点にしない)。読めなければ `GuardError` (exit 2)・JSON の形が違えば `PreregError` (exit 3)。
    """
    try:
        raw = Path(path).read_bytes()
    except OSError as e:
        raise GuardError(f"--prereg を読めない: {path}: {e}") from e
    try:
        prereg = json.loads(raw.decode("utf-8"), parse_float=Decimal, parse_constant=_reject_constant)
    except ValueError as e:  # JSONDecodeError / UnicodeDecodeError は ValueError の子
        raise PreregError(f"{path}: JSON として読めない: {e}") from e
    if not isinstance(prereg, dict):
        raise PreregError(f"{path}: トップが JSON オブジェクトではない")
    return prereg, hashlib.sha256(raw).hexdigest()[:16]


def declared_pg1_min(prereg):
    """PG-1 が宣言した「一人あたり episode 数の下限」を返す。⚠️ 無い・型や範囲が違えば `Pg1UndeclaredError`。

    `pg1.min_episodes_per_participant` は bool でない int で 1 以上 (判断 19・Codex TASK-PRE 指摘 1)。
    ⚠️ `0` / `-1` / `true` / `"3"` / `2.5` / `3.0` は宣言とみなさない。値を推測で埋めない。
    """
    pg1 = prereg.get("pg1")
    value = pg1.get("min_episodes_per_participant") if isinstance(pg1, dict) else None
    if type(value) is not int or value < 1:
        raise Pg1UndeclaredError(
            "PG-1 の値が宣言されていない (pg1.min_episodes_per_participant が 1 以上の整数でない: "
            f"{value!r}。事前宣言 §2.3: 宣言されるまで探索を 1 度も回さない。値を推測で埋めない)"
        )
    return value


# ── 格子 ──────────────────────────────────────────────────────────────


def _fmt_value(value):
    """`--set` の値・ID に出す文字列。⚠️ `q` は指数表記にしない (`^[0-9]+(\\.[0-9]+)?$` に合わせる)。"""
    if isinstance(value, Decimal):
        return format(value.normalize(_WIDE), "f")
    return str(value)


def _jsonable(value):
    return float(value) if isinstance(value, Decimal) else value


def _check_value(key, value, where):
    if key == "q":
        if _q_key(value) not in WARMUP_BY_Q:
            raise GridError(f"{where}: q={value!r} は対応表 {sorted(WARMUP_BY_Q)} に無い (探索空間の外)")
    elif type(value) is not int or value < 1:
        raise GridError(f"{where}: {key}={value!r} が 1 以上の整数でない")


def build_grid(prereg):
    """凍結 JSON から探索格子を組む。`[{"id", "kind", "params"}]` (選択 → 感度の順・JSON の並び順)。

    ⚠️ `search_space` / `search_roles` / `operational` の形が想定と違えば `GridError` (JSON は直さない)。
    `params` は 6 キー (`q` は `normalize` 済みの `Decimal`・残りは int)。
    """
    sections = {}
    for name in ("operational", "search_space", "search_roles"):
        sections[name] = prereg.get(name)
        if not isinstance(sections[name], dict):
            raise GridError(f"{name} がオブジェクトではない")
    operational, space, roles = sections["operational"], sections["search_space"], sections["search_roles"]
    if set(space) != set(roles):
        raise GridError(f"search_space と search_roles のキーが違う: {sorted(set(space) ^ set(roles))}")
    for key, role in roles.items():
        if role not in _ROLES:
            raise GridError(f"search_roles.{key} が知らない役割: {role!r} (知っている役割: {_ROLES})")
        if role == "derived" and key != "warmup_count":
            raise GridError(f"search_roles.{key} が derived (★ 従属にできるのは warmup_count だけ)")
    if roles.get("warmup_count") != "derived":
        raise GridError("search_roles.warmup_count が derived でない (★ warmup_count は q の従属変数)")
    for key in TUNABLE_KEYS:
        if key not in operational:
            raise GridError(f"operational に {key!r} が無い")
        if key != "warmup_count":
            _check_value(key, operational[key], f"operational.{key}")
    operational_q = _q_key(operational["q"])
    if operational["warmup_count"] != WARMUP_BY_Q[operational_q] or type(operational["warmup_count"]) is not int:
        raise GridError(
            f"operational.warmup_count={operational['warmup_count']!r} が対応表 (q={operational_q}: {WARMUP_BY_Q[operational_q]}) と合わない"
        )

    selection, sensitivity = [], []
    for key in space:  # ★ JSON の並び順 (ID の並びになる)
        role = roles[key]
        if role == "fixed":
            if key not in operational or space[key] != [operational[key]]:
                raise GridError(f"search_space.{key} は fixed なのに [operational.{key}] と違う: {space[key]!r}")
        elif role in ("selection", "sensitivity_only"):
            if key not in _SEARCHED_KEYS:
                raise GridError(f"search_space.{key} を {role} にしているが、--set で渡せるキーではない: {_SEARCHED_KEYS}")
            values = space[key]
            if not isinstance(values, list) or not values:
                raise GridError(f"search_space.{key} が空でない配列ではない: {values!r}")
            for value in values:
                _check_value(key, value, f"search_space.{key}")
            keys = [_q_key(v) if key == "q" else v for v in values]
            if len(set(keys)) != len(keys):
                raise GridError(f"search_space.{key} に重複がある: {values!r}")
            if (_q_key(operational[key]) if key == "q" else operational[key]) not in keys:
                raise GridError(f"operational.{key}={operational[key]!r} が search_space.{key} に含まれない")
            (selection if role == "selection" else sensitivity).append(key)

    def params_for(overrides):
        params = {key: operational[key] for key in TUNABLE_KEYS}
        params.update(overrides)
        params["q"] = _q_key(params["q"])
        params["warmup_count"] = WARMUP_BY_Q[params["q"]]  # ★ 必ず q と対で
        return params

    def make(prefix, kind, pairs, overrides):
        config_id = prefix + "__" + "__".join(f"{key}={_fmt_value(value)}" for key, value in pairs)
        return {"id": config_id, "kind": kind, "params": params_for(overrides)}

    configs = []
    if selection:
        for combo in itertools.product(*(space[key] for key in selection)):
            pairs = list(zip(selection, combo))
            configs.append(make("sel", "selection", pairs, dict(pairs)))
    for key in sensitivity:  # ★ OFAT: 運用値以外の値へ 1 キーずつ (Cartesian に組まない)
        for value in space[key]:
            same = (_q_key(value) == _q_key(operational[key])) if key == "q" else value == operational[key]
            if not same:
                configs.append(make("ofat", "sensitivity", [(key, value)], {key: value}))
    ids = [config["id"] for config in configs]
    if not configs or len(set(ids)) != len(ids):
        raise GridError(f"格子が空、または ID が重複している: {ids}")
    return configs


def set_args(params):
    """`run-features-all-poles.sh` に `--` の後ろで渡す引数 (6 キーすべて・`q` と `warmup_count` は対)。"""
    args = ["--"]
    for key in TUNABLE_KEYS:
        args += ["--set", f"{key}={_fmt_value(params[key])}"]
    return args


# ── 入力・出力先のガード ────────────────────────────────────────────────


def find_bash():
    bash = shutil.which("bash")
    if bash is None:
        raise GuardError("bash が見つからない (★ 3 極の実行は run-features-all-poles.sh に任せる。Windows は git-bash が必要)")
    return bash


def guard_out(out):
    """`--out` のガード。通れば絶対パスを返す。⚠️ 作らない (作るのは全てのゲートを通った後)。"""
    out_path = Path(out).resolve()
    if out_path.exists():
        if not out_path.is_dir():
            raise GuardError(f"--out がディレクトリではない: {out_path}")
        if any(out_path.iterdir()):
            raise GuardError(f"--out が空でない (★ 使い回し拒否。空のディレクトリか、まだ無いパスを指定する): {out_path}")
    probe = out_path
    while not probe.exists():  # ★ 実在する最も近い祖先で判定する (祖先が作業ツリーの中なら、その下も中)
        probe = probe.parent
    if not probe.is_dir():
        raise GuardError(f"--out の親がディレクトリではない: {probe}")
    if _inside_git_work_tree(probe):
        raise GuardError(f"--out が git の管理下: {out_path} (★ 特徴行は共有禁止。出力は repo の外に置く)")
    return out_path


def list_sessions(root):
    """`<root>/<P-ID>/<session>.ndjson` を歩き、`[(participant, session, path)]` (参加者・セッション名の昇順) を返す。

    ⚠️ fail-closed: root がディレクトリでない・P-ID の形 (`^P[0-9A-Za-z_-]+$`) に合わないディレクトリ・契約に無いエントリ
    (`*.ndjson` の通常ファイル以外)・セッション名が `[0-9A-Za-z_][0-9A-Za-z_.-]*` でない・セッションが 1 つも無い、は `GuardError`。
    """
    root = Path(root)
    if not root.is_dir():
        raise GuardError(f"--ndjson-root がディレクトリではない: {root}")
    sessions = []
    for participant_dir in sorted(root.iterdir(), key=lambda entry: entry.name):
        if not participant_dir.is_dir():
            raise GuardError(f"{participant_dir}: 参加者ディレクトリではない (root 直下は <P-ID>/ だけ)")
        if fio.P_ID_RE.fullmatch(participant_dir.name) is None:
            raise GuardError(f"{participant_dir}: P-ID の形 (^P[0-9A-Za-z_-]+$) に合わないディレクトリ名")
        entries = sorted(participant_dir.iterdir(), key=lambda entry: entry.name)
        if not entries:
            raise GuardError(f"{participant_dir}: セッションが 1 つも無い")
        for entry in entries:
            if not entry.is_file() or not entry.name.endswith(_NDJSON_SUFFIX):
                raise GuardError(f"{entry}: 契約に無いエントリ (<P-ID>/ 直下は <session>{_NDJSON_SUFFIX} だけ)")
            stem = entry.name[: -len(_NDJSON_SUFFIX)]
            if _SESSION_STEM_RE.fullmatch(stem) is None:
                raise GuardError(f"{entry}: セッション名 {stem!r} が [0-9A-Za-z_][0-9A-Za-z_.-]* に合わない")
            sessions.append((participant_dir.name, stem, entry))
    sessions.sort(key=lambda item: (item[0], item[1]))
    if not sessions:
        raise GuardError(f"{root}: セッションが 1 つも無い (★ --ndjson-root の指定違いを疑う)")
    return sessions


# ── 実行 → 読み直し → manifest ─────────────────────────────────────────


def run_poles(bash, ndjson, outdir, params):
    """1 (一式 × セッション) を 3 極で回す。⚠️ 3 極スクリプトが非 0 なら `RunError`。"""
    command = [bash, ALL_POLES_SCRIPT.as_posix(), Path(ndjson).as_posix(), Path(outdir).as_posix(), *set_args(params)]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
        )
    except OSError as e:
        raise RunError(f"3 極スクリプトを起動できない: {e}") from e
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-5:])
        raise RunError(f"3 極スクリプトが exit {result.returncode} ({Path(outdir).name}): {tail}")


def _param_diffs(config, intended):
    """意図して渡した 6 キーと封筒 `config` の値が違うキーを `{key: {"observed", "intended"}}` で返す。"""
    diffs = {}
    for key in TUNABLE_KEYS:
        observed, want = config.get(key), intended[key]
        if key == "q":
            same = _q_key(observed) is not None and _q_key(observed) == _q_key(want)
        else:
            same = type(observed) is int and observed == want
        if not same:
            diffs[key] = {"observed": observed, "intended": _jsonable(want)}
    return diffs


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect(configs, sessions, out_path):
    """全封筒を読み直し、`(outputs, excluded_rule_d, envelope_identity)` を返す。

    ⚠️ 読めない・形が違う・レイアウトが期待と違う・封筒の identity が混在している、は `RunError` (manifest を書かない)。
    """
    expected = [(participant, session) for participant, session, _ in sessions]
    outputs, excluded, identities = [], [], set()
    for config in configs:
        root = out_path / config["id"]
        try:
            found = fio.discover(root)
        except fio.FeaturesIOError as e:
            raise RunError(f"{config['id']}: 出力のレイアウトが期待と違う: {e}") from e
        if [(participant, session) for participant, session, _ in found] != expected:
            raise RunError(f"{config['id']}: 出力のセッションが入力と一致しない")
        for participant, session, paths in found:
            try:
                envelopes = fio.load_session(paths)
            except fio.FeaturesIOError as e:
                raise RunError(f"{config['id']}/{participant}/{session}: 封筒を読み直せない: {e}") from e
            for pole in POLES:
                envelope = envelopes[pole]
                run_config, provenance = envelope["config"], envelope["provenance"]
                identities.add(
                    (
                        run_config["prereg_version"],
                        run_config["prereg_sha256_prefix"],
                        run_config["hmm_version"],
                        provenance["hmm_version"],
                        run_config["config_source"],
                    )
                )
                reasons = []
                if not is_valid_search_run(run_config):
                    reasons.append(REASON_RULE_D)
                diffs = _param_diffs(run_config, config["params"])
                if diffs:
                    reasons.append(REASON_PARAM_MISMATCH)
                if reasons:
                    excluded.append(
                        {
                            "config_id": config["id"],
                            "participant": participant,
                            "session": session,
                            "pole": pole,
                            "reasons": reasons,
                            "mismatch": diffs,
                        }
                    )
                path = paths[pole]
                outputs.append(
                    {"path": path.relative_to(out_path).as_posix(), "sha256": _sha256_file(path)},
                )
    if len(identities) != 1:
        raise RunError(f"封筒の identity が 1 通りでない (別々の binary・凍結値が混ざっている): {sorted(identities)}")
    (identity,) = identities
    keys = ("prereg_version", "prereg_sha256_prefix", "hmm_version", "provenance_hmm_version", "config_source")
    identity = dict(zip(keys, identity))
    if identity["config_source"] != "frozen":
        raise RunError(f"封筒の config_source が frozen でない: {identity['config_source']!r} (★ --feature-config を渡していないはず)")
    return outputs, excluded, identity


def write_manifest(out_path, manifest):
    """manifest を一時名に書いてから rename する。⚠️ 失敗したら一時ファイルを残さず `RunError`。"""
    final = out_path / MANIFEST_NAME
    temp = out_path / (MANIFEST_NAME + ".tmp")
    try:
        with open(temp, "x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        os.replace(temp, final)
    except OSError as e:
        try:
            temp.unlink()
        except OSError:
            pass
        raise RunError(f"manifest を書けない: {e}") from e


def run_grid(configs, sessions, out_path, prereg_source, prereg_sha256_prefix, bash):
    """格子を回し、読み直し、manifest を最後に確定して返す。⚠️ 途中で失敗したら `RunError` (manifest は残らない)。"""
    out_path.mkdir(parents=True, exist_ok=True)
    for index, config in enumerate(configs, start=1):
        _emit(sys.stdout, f"[grid] {index}/{len(configs)} {config['id']}")
        for participant, session, ndjson in sessions:
            run_poles(bash, ndjson, out_path / config["id"] / participant / session, config["params"])
    outputs, excluded, identity = collect(configs, sessions, out_path)
    manifest = {
        "tool": TOOL,
        "complete": True,
        "prereg_source": prereg_source,
        "prereg_sha256_prefix": prereg_sha256_prefix,
        "envelope_identity": identity,
        "n_participants": len({participant for participant, _, _ in sessions}),
        "n_sessions": len(sessions),
        "sessions": [{"participant": participant, "session": session} for participant, session, _ in sessions],
        "configs": [
            {"id": config["id"], "kind": config["kind"], "params": {k: _jsonable(v) for k, v in config["params"].items()}}
            for config in configs
        ],
        "excluded_rule_d": excluded,
        "outputs": outputs,
    }
    write_manifest(out_path, manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="p1_run_grid.py",
        description="P1 の探索格子 (選択 27 + 感度 OFAT 4) を q と warmup_count を対で渡して 3 極で回す。PG-1 未宣言なら 1 実行も回さない。",
    )
    parser.add_argument("--ndjson-root", required=True, help="<root>/<P-ID>/<session>.ndjson")
    parser.add_argument("--out", required=True, help="出力ディレクトリ (★ repo の外・空か未作成)")
    parser.add_argument("--prereg", default=None, help="凍結 JSON の新版 (既定: src-tauri/prereg/p1-episode.json)")
    args = parser.parse_args(argv)  # ⚠️ 引数の不備は argparse が exit 2 にする

    try:
        # ★ 順序: 副作用の無いガード (2) → 事前宣言 (3) → PG-1 (6) → 格子 (3) → 実行 (1)
        out_path = guard_out(args.out)
        sessions = list_sessions(args.ndjson_root)
        bash = find_bash()
        prereg_path, prereg_source = resolve_prereg(args.prereg)
        prereg, prereg_sha256_prefix = load_prereg(prereg_path)
        declared_pg1_min(prereg)
        configs = build_grid(prereg)
        manifest = run_grid(configs, sessions, out_path, prereg_source, prereg_sha256_prefix, bash)
    except GuardError as e:
        _emit(sys.stderr, f"[grid] NG (guard): {e}")
        return EXIT_GUARD
    except Pg1UndeclaredError as e:
        _emit(sys.stderr, f"[grid] NG (PG-1): {e}")
        return EXIT_PG1_UNDECLARED
    except PreregError as e:
        _emit(sys.stderr, f"[grid] NG (grid): {e}")
        return EXIT_BAD_GRID
    except RunError as e:
        _emit(sys.stderr, f"[grid] NG (run): {e}")
        return EXIT_RUN_FAILED

    excluded = len(manifest["excluded_rule_d"])
    if excluded:
        _emit(sys.stderr, f"[grid] note: {excluded} run(s) excluded by rule (d) / param mismatch (see excluded_rule_d in the manifest)")
    _emit(sys.stdout, f"[grid] OK: {len(configs)} configs x {len(sessions)} sessions -> {out_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
