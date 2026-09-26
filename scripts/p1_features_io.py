"""P1 の `--features` 出力 (封筒) の読み込み層 (issue 002・後続の 003 / 004 / 005 も使う)。

## ★ 何をする層か

`scripts/run-features-all-poles.sh <in> <outdir>` の outdir を、参加者のレイアウトに並べたものを歩き、
封筒 (`{provenance, config, rows}`) を **fail-closed で読む**。

    <root>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json

- P-ID は**パスの構成要素**から取る (封筒に参加者 ID は無い・`.steering/20260926-p1-main-prep/decisions.md` 判断 5)。
- ⚠️ 形が違えば**例外**にする。黙って 0 にしない・黙って読み飛ばさない (★ 欠けた極や壊れた封筒を 0 として
  数えると、PG-1 に渡す分布の下側が楽観化される)。
- ★ 契約: **メタデータの検証はこの層で済ませてから射影する** (`load_envelope` → `load_session` → `project_*`)。
  射影は検証済みの封筒だけを受け取る。

## ⚠️★★★ PG-1 が「見てよいもの」と、それを構造で保証する理由

事前宣言 §2.3 の宣言ゲート **PG-1** は、見てよいものを「★ 参加者ごとの episode 数の分布**だけ**
(⚠️ 転帰も予測成績も見ない)」と定めている。値が PG-1 で宣言されるまで、探索は 1 度も回さない。

→ ★ **`project_pg1` は行から `stall_onset.is_onset` の真偽だけを読み、数える。** 次のものは射影が**返さない**ので、
PG-1 の側 (`p1_pg1_distribution.py`) には型として渡らない (⚠️ CLI 側で「読まない」と誓うのではなく、
射影が返さないことで**構造的に**読めなくしている):

| 返さないもの | なぜ |
|---|---|
| `restart` (`T1d`) | 転帰側の量。PG-1 は転帰を見ない (ADR-030 補訂 1 項目 7) |
| `dispersion` (`T1a`)・`activity`・`boundary`・`revision`・`quality` | 特徴量。episode の**数**に要らない |
| `theta_person_ms` / `theta_sample_n` | θ は探索の対象。PG-1 の前に見ると探索を 1 度回したのと同じ |
| `t0_ms` / `s_ms` / `t_ms` (時刻) | 分布は数であって時系列ではない。時刻は個人を同定しうる |
| `ime_overlap`・`task_kind`・`phase` | 行の属性。episode の**数**に要らない |

⚠️ この表の項目を射影へ足す前に、`docs/preregistration-p1-episode.md` §2.3 の PG-1 の行を読み直すこと
(足すなら、PG-1 の**後**の別の射影として足す。★ PG-1 の射影を広げない)。

## 例外

- `LayoutError`: ディレクトリのレイアウトが違う (極の欠け・`.all-poles.lock` の残り・P-ID の形違い ほか)。
- `EnvelopeError`: 封筒の形・型が違う、または 3 極の間でメタデータが食い違う。
- どちらも `FeaturesIOError` (= `ValueError`) の子。CLI は両方を exit 3 にする。
"""

import json
import math
import re
from pathlib import Path

from p1_bounds import POLES

PREREG_ID = "p1-episode"
# ⚠️ fullmatch で使う (★ `$` は末尾の改行の手前にも合致してしまうため、`match` + `$` にしない)
P_ID_RE = re.compile(r"P[0-9A-Za-z_-]+")
# ★ `run-features-all-poles.sh` は outdir に `.all-poles.lock` (二重起動の排他) と
#   `.all-poles.XXXXXX` (staging) を作る。**正常終了ならどちらも消える**ので、残っていれば
#   実行中か、強制終了された outdir である (⚠️ 3 ファイルが揃っていても信用しない)。
_IN_PROGRESS_PREFIX = ".all-poles."
_POLE_FILES = {f"{pole}.json": pole for pole in POLES}

# ★ 3 極の間で**必ず一致する**メタデータ。3 極は同じ入力に対する 1 回の実行の出力なので、
#   食い違うなら別々の実行 (別の binary・別の設定) が混ざっている (Codex TASK-PRE 指摘 7)。
#   ⚠️ `hmm_version` は 2 か所にある: `provenance` は**収集時**、`config` は**解析時** (このバイナリ)。
#   どちらも極が違っても変わらない値なので、両方を見る。
_CROSS_POLE_KEYS = (
    ("provenance", "hmm_version"),
    ("config", "hmm_version"),
    ("config", "prereg_version"),
    ("config", "prereg_sha256_prefix"),
    ("config", "config_source"),
    ("config", "overrides"),
)


class FeaturesIOError(ValueError):
    """読み込み層の失敗の親。"""


class LayoutError(FeaturesIOError):
    """ディレクトリのレイアウトが契約と違う。"""


class EnvelopeError(FeaturesIOError):
    """封筒の形・型が違う、または 3 極の間でメタデータが食い違う。"""


def _listdir(path):
    try:
        return sorted(path.iterdir(), key=lambda entry: entry.name)
    except OSError as e:
        raise LayoutError(f"{path}: 中身を列挙できない: {e}") from e


def _session_paths(session_dir):
    entries = _listdir(session_dir)
    names = [entry.name for entry in entries]
    for name in names:
        if name.startswith(_IN_PROGRESS_PREFIX):
            raise LayoutError(
                f"{session_dir}: {name} が残っている (★ run-features-all-poles.sh が実行中か、強制終了された outdir。"
                "3 ファイルが揃っていても信用しない)"
            )
    unexpected = [name for name in names if name not in _POLE_FILES]
    if unexpected:
        raise LayoutError(f"{session_dir}: 契約に無いエントリがある: {unexpected}")
    missing = [name for name in _POLE_FILES if name not in names]
    if missing:
        raise LayoutError(f"{session_dir}: 極のファイルが欠けている: {missing}")
    paths = {}
    for pole in POLES:
        path = session_dir / f"{pole}.json"
        if not path.is_file():
            raise LayoutError(f"{path}: 通常のファイルではない")
        paths[pole] = path
    return paths


def discover(root):
    """レイアウトを歩き、`[(participant_id, session_id, {pole: path})]` を返す (⚠️ 参加者・セッション名の昇順)。

    fail-closed: 3 極のファイルが揃わないセッション・`.all-poles.lock` / staging が残るセッション・
    P-ID の形 (`^P[0-9A-Za-z_-]+$`) に合わないディレクトリ・契約に無いエントリ・セッションが 1 つも無い root は
    `LayoutError`。★ 参加者の母集団はここで決まる (episode の有無からは決めない)。
    """
    root = Path(root)
    if not root.is_dir():
        raise LayoutError(f"root がディレクトリではない: {root}")
    found = []
    for participant_dir in _listdir(root):
        if not participant_dir.is_dir():
            raise LayoutError(f"{participant_dir}: 参加者ディレクトリではない (★ root 直下は <P-ID>/ だけ)")
        if P_ID_RE.fullmatch(participant_dir.name) is None:
            raise LayoutError(
                f"{participant_dir}: P-ID の形 (^P[0-9A-Za-z_-]+$) に合わないディレクトリ名: {participant_dir.name!r}"
            )
        session_dirs = _listdir(participant_dir)
        if not session_dirs:
            raise LayoutError(f"{participant_dir}: セッションが 1 つも無い")
        for session_dir in session_dirs:
            if not session_dir.is_dir():
                raise LayoutError(f"{session_dir}: セッションのディレクトリではない (★ <P-ID>/ 直下は <session>/ だけ)")
            found.append((participant_dir.name, session_dir.name, _session_paths(session_dir)))
    if not found:
        raise LayoutError(f"{root}: セッションが 1 つも無い (★ --root の指定違いを疑う)")
    return found


def _reject_constant(name):
    raise ValueError(f"JSON に非有限の定数がある: {name}")


def _parse_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"JSON の数値が有限でない: {text}")
    return value


def _is_text(value):
    return isinstance(value, str) and value != ""


def check_envelope(envelope, expected_pole=None, where="封筒"):
    """封筒の形と型を検査する (⚠️ 値の意味は見ない)。違えば `EnvelopeError`。

    読むのは `config` / `provenance` のメタデータと、各行の `stall_onset.is_onset` の型だけ。
    ★ `expected_pole` が `None` なら、`config.pole` が 3 極のどれかであることだけを見る。
    """

    def bad(message):
        raise EnvelopeError(f"{where}: {message}")

    if not isinstance(envelope, dict):
        bad("トップが JSON オブジェクトではない")
    for key in ("provenance", "config", "rows"):
        if key not in envelope:
            bad(f"トップに {key!r} が無い")
    provenance, config, rows = envelope["provenance"], envelope["config"], envelope["rows"]
    if not isinstance(provenance, dict):
        bad("provenance がオブジェクトではない")
    if not isinstance(config, dict):
        bad("config がオブジェクトではない")
    if not isinstance(rows, list):
        bad("rows が配列ではない")

    # 収集時の hmm_version (★ 旧ログでは null。キー自体は常に出る)
    if "hmm_version" not in provenance:
        bad("provenance に 'hmm_version' が無い")
    if provenance["hmm_version"] is not None and not _is_text(provenance["hmm_version"]):
        bad(f"provenance.hmm_version が文字列でも null でもない: {provenance['hmm_version']!r}")

    for key in ("pole", "pole_applicable", "pole_not_applicable_reason", "prereg_id", "prereg_version",
                "prereg_sha256_prefix", "config_source", "overrides", "hmm_version"):
        if key not in config:
            bad(f"config に {key!r} が無い")
    pole = config["pole"]
    if pole not in POLES:
        bad(f"config.pole が知らない極: {pole!r} (知っている極: {POLES})")
    if expected_pole is not None and pole != expected_pole:
        bad(f"config.pole が {pole!r} (期待: {expected_pole!r}。★ ファイル名と中身の極が食い違う)")
    if config["prereg_id"] != PREREG_ID:
        bad(f"config.prereg_id が {config['prereg_id']!r} (期待: {PREREG_ID!r})")
    for key in ("prereg_version", "prereg_sha256_prefix", "config_source", "hmm_version"):
        if not _is_text(config[key]):
            bad(f"config.{key} が空でない文字列ではない: {config[key]!r}")
    if not isinstance(config["overrides"], list):
        bad(f"config.overrides が配列ではない: {config['overrides']!r}")
    applicable, reason = config["pole_applicable"], config["pole_not_applicable_reason"]
    if not isinstance(applicable, bool):
        bad(f"config.pole_applicable が bool ではない: {applicable!r}")
    # ★ 適用可なら理由は null・非適用なら理由がある (Rust 側の契約)。食い違いは封筒が壊れている
    if applicable and reason is not None:
        bad(f"適用可 (pole_applicable=true) なのに理由がある: {reason!r}")
    if not applicable and not _is_text(reason):
        bad(f"非適用 (pole_applicable=false) なのに理由が無い: {reason!r}")
    if pole == "baseline" and not applicable:
        bad("baseline が非適用 (★ baseline は常に適用可)")

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            bad(f"rows[{i}] がオブジェクトではない")
        onset = row.get("stall_onset")
        if not isinstance(onset, dict):
            bad(f"rows[{i}].stall_onset がオブジェクトではない")
        if not isinstance(onset.get("is_onset"), bool):
            bad(f"rows[{i}].stall_onset.is_onset が bool ではない: {onset.get('is_onset')!r}")
    return envelope


def load_envelope(path, expected_pole):
    """封筒 1 つを読んで検査する。形・型・極が違えば `EnvelopeError` (⚠️ 黙って 0 にしない)。

    検査: `config.pole == expected_pole`・`config.prereg_id == "p1-episode"`・必要なキーの存在と型
    (`overrides` は配列・`pole_applicable` は bool・数値は有限 [NaN / Infinity / 桁あふれを拒否])。
    """
    path = Path(path)
    try:
        with open(path, encoding="utf-8") as f:
            envelope = json.load(f, parse_constant=_reject_constant, parse_float=_parse_float)
    except (OSError, ValueError) as e:  # JSONDecodeError / UnicodeDecodeError は ValueError の子
        raise EnvelopeError(f"{path}: 読めない: {e}") from e
    return check_envelope(envelope, expected_pole, where=str(path))


def load_session(paths):
    """1 セッションの 3 極を読み、`{pole: 封筒}` を返す。

    ⚠️ 極の間で `hmm_version` (収集時・解析時) / `prereg_version` / `prereg_sha256_prefix` / `config_source` /
    `overrides` が一致しなければ `EnvelopeError` (★ 3 極は同じ入力への 1 回の実行の出力のはず)。
    """
    if set(paths) != set(POLES):
        raise LayoutError(f"極の集合が違う: {sorted(paths)} (期待: {sorted(POLES)})")
    envelopes = {pole: load_envelope(paths[pole], pole) for pole in POLES}
    first = POLES[0]
    for pole in POLES[1:]:
        for section, key in _CROSS_POLE_KEYS:
            mine, theirs = envelopes[first][section][key], envelopes[pole][section][key]
            if mine != theirs:
                raise EnvelopeError(
                    f"極 {first!r} と {pole!r} で {section}.{key} が食い違う: {mine!r} != {theirs!r} "
                    "(★ 3 極が別々の実行の出力である)"
                )
    return envelopes


def project_pg1(envelope):
    """PG-1 用の**射影** (★ 検証済みの封筒を受け取る。冒頭の「PG-1 が見てよいもの」の表を読むこと)。

    返すのは次の 8 キーだけ。行からは `stall_onset.is_onset` の真偽だけを読み、`onsets` に数える。
    `overrides_count` は CLI が「凍結既定の出力か」を射影だけで判定するために要る。
    """
    check_envelope(envelope, where="project_pg1 の入力")
    config = envelope["config"]
    return {
        "pole": config["pole"],
        "pole_applicable": config["pole_applicable"],
        "pole_not_applicable_reason": config["pole_not_applicable_reason"],
        "onsets": sum(1 for row in envelope["rows"] if row["stall_onset"]["is_onset"]),
        "prereg_version": config["prereg_version"],
        "prereg_sha256_prefix": config["prereg_sha256_prefix"],
        "config_source": config["config_source"],
        "overrides_count": len(config["overrides"]),
    }
