"""PG-1 に渡す「参加者ごとの episode 数の分布」だけを出す CLI (issue 002)。

## ★ 何をするか

`scripts/run-features-all-poles.sh` の出力を `<root>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json`
に並べたものを読み、**極ごとに独立に** (⚠️ 混ぜない・事前宣言 §3 規律 4)、参加者ごとの episode 数と、
その分布の要約を出す。これが事前宣言 §2.3 の宣言ゲート **PG-1** に渡す**唯一の集計**である。

    python scripts/p1_pg1_distribution.py --root <root> --out <出力 JSON>

## ⚠️★★★ 「分布だけ」を構造で保証する

PG-1 が見てよいのは分布**だけ**で、転帰も予測成績も見ない。→ ★ このファイルは封筒に**直接触れない**。
`p1_features_io.project_pg1` が返す 8 キー (極・適用可否・その理由・onset の本数・事前宣言の版と sha・設定の由来・
overrides の件数) の**射影だけ**から集計する。射影が返さないものと、その理由は `p1_features_io.py` の冒頭に書いてある
(⚠️ ここに列挙しない: acceptance が、このファイルに行の中身のキー名が現れないことを grep で見る)。

## 出力 (JSON・キーは固定 — `test_output_keys_whitelist`)

    {
      "poles": {
        "<極>": {
          "participants": {"<P-ID>": {"sessions": n, "sessions_not_applicable": n, "episodes": n}, ...},
          "summary": {"n_participants": n, "episodes_per_participant_sorted": [...], "min": n, "median": n, "max": n},
          "participants_without_applicable_sessions": n
        }, ...
      },
      "provenance": {"prereg_version": "...", "prereg_sha256_prefix": "...", "tool": "p1_pg1_distribution", "n_sessions": n}
    }

- `sessions` = その参加者の**全セッション数** (適用可 + 非適用)。`sessions_not_applicable` = うち、その極が非適用のもの。
- ⚠️ `episodes` は**適用可のセッションの onset 本数の合計**。非適用のセッション (`pole_applicable=false`) は
  「episode 0 本」ではなく `sessions_not_applicable` に**別に数える** (★ 非適用の出力は baseline と恒等なので、
  onset を数えると二重に数える)。
- ⚠️★ **参加者の母集団は `discover` のセッションから決まる** (episode から列挙しない)。onset が 0 本の参加者も
  `episodes: 0` で載り、要約にも入る (★ 消えると最小値が楽観化する)。
- 要約は**適用可のセッションを 1 本以上持つ参加者だけ**で数える。その極で適用可のセッションが 1 本も無い参加者は
  要約に入れず、`participants_without_applicable_sessions` に数える。0 人なら `min` / `median` / `max` は `null`。
- `median` は要素数が偶数のとき 2 つの中央値の平均 (整数なら整数・そうでなければ `x.5`)。

## ⚠️ 凍結既定で出した出力だけを受け付ける (exit 4)

事前宣言 §3 規律 1: 主は §1 の運用値である。`config_source != "frozen"` (`--feature-config` で読んだ) か、
`overrides` が空でない (`--set` で凍結値から外れた) セッションが 1 本でもあれば拒否する。
事前宣言の版と sha が 1 セッションでも違えば (別の凍結値が混ざっている) 同じく拒否する。

## exit

| code | 意味 |
|---|---|
| 0 | OK |
| 2 | 引数・出力先のガード (`--root` がディレクトリでない・`--out` が既にある・`--out` が git の作業ツリーの中・git の判定が失敗) |
| 3 | レイアウトまたは封筒の形が違う (`p1_features_io` の `LayoutError` / `EnvelopeError`) |
| 4 | 凍結既定でない出力が混ざっている |

⚠️ `--out` は **git の作業ツリーの中なら拒否する** (`run-features-all-poles.sh` と同じ理由・同じ判定:
`git -C <dir> rev-parse --is-inside-work-tree`。判定そのものが失敗したら、管理外とは見なさず拒否する)。
既存のファイルは上書きしない (★ PG-1 は 1 回だけ通すゲートで、出し直しで forking paths を作らない)。

使い方 (テスト): `python -m unittest scripts.tests.test_p1_pg1_distribution -v` (repo 直下から)。
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import p1_features_io as fio
from p1_bounds import POLES

TOOL = "p1_pg1_distribution"
EXIT_OK, EXIT_GUARD, EXIT_LAYOUT, EXIT_NOT_FROZEN = 0, 2, 3, 4

# ★ 出力のキー (テストが固定する)
_PARTICIPANT_KEYS = ("sessions", "sessions_not_applicable", "episodes")


class GuardError(Exception):
    """引数・出力先のガードに違反した (exit 2)。"""


class NotFrozenError(Exception):
    """凍結既定でない出力が混ざっている (exit 4)。"""


def _git_env():
    env = {
        key: value
        for key, value in os.environ.items()
        # ⚠️ 親を辿る探索を狂わせる変数は外す (GIT_CEILING_DIRECTORIES があると、作業ツリーの中でも「管理外」に見える)
        if key not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_CEILING_DIRECTORIES")
    }
    env.update({"LC_ALL": "C", "LANGUAGE": "C"})  # ★ 「not a git repository」の判定が翻訳で崩れないように
    return env


def _inside_git_work_tree(directory):
    """`directory` が git の管理下なら True・管理外なら False。⚠️ 判定できなければ `GuardError` (fail-closed)。

    ★ `.git` の中 (`rev-parse` が `false` を返す) も True 扱い: 「管理外」と確定できたのは
    「not a git repository」と言われたときだけ。
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_git_env(),
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as e:
        raise GuardError(f"git の判定を実行できない (★ 管理外とは見なさず拒否する): {e}") from e
    if result.returncode == 0:
        return True
    if "not a git repository" in result.stderr.lower():
        return False
    raise GuardError(
        f"git の判定がエラー ('not a git repository' 以外・★ 所有権チェック等の失敗を管理外として素通りさせない): "
        f"{result.stderr.strip()}"
    )


def guard_paths(root, out):
    """`--root` / `--out` のガード。通れば絶対パスの `out` を返す。違反は `GuardError`。"""
    if not Path(root).is_dir():
        raise GuardError(f"--root がディレクトリではない: {root}")
    out_path = Path(out).resolve()
    if out_path.exists():
        raise GuardError(f"--out が既にある (★ 上書きしない。別のパスを指定する): {out_path}")
    # ★ まだ無いディレクトリの下に書く場合は、実在する最も近い祖先で判定する
    #   (作ってから判定して消す、を避ける。祖先が作業ツリーの中なら、その下も作業ツリーの中)
    probe = out_path.parent
    while not probe.exists():
        probe = probe.parent
    if not probe.is_dir():
        raise GuardError(f"--out の親がディレクトリではない: {probe}")
    if _inside_git_work_tree(probe):
        raise GuardError(
            f"--out が git の管理下: {out_path} (★ 出力は repo の外に置く。作業ツリーの中だと誤って stage される)"
        )
    return out_path


def check_frozen(sessions):
    """凍結既定で出した出力だけか確かめ、`(prereg_version, prereg_sha256_prefix)` を返す。違反は `NotFrozenError`。

    ⚠️ 射影の結果だけを見る (`config_source` / `overrides_count` / 事前宣言の版と sha)。
    """
    identities = set()
    for participant, session, poles in sessions:
        for pole, projection in poles.items():
            where = f"{participant}/{session} の極 {pole}"
            if projection["config_source"] != "frozen":
                raise NotFrozenError(
                    f"{where}: config_source={projection['config_source']!r} (★ 凍結既定でない。PG-1 は凍結既定の出力だけを受け付ける)"
                )
            if projection["overrides_count"] != 0:
                raise NotFrozenError(
                    f"{where}: overrides が {projection['overrides_count']} 件 (★ 凍結値から外れた実行の出力は PG-1 に使わない)"
                )
            identities.add((projection["prereg_version"], projection["prereg_sha256_prefix"]))
    if len(identities) != 1:
        raise NotFrozenError(f"事前宣言の版・sha が複数混在している: {sorted(identities)}")
    return next(iter(identities))


def _median(sorted_values):
    n = len(sorted_values)
    if n % 2 == 1:
        return sorted_values[n // 2]
    total = sorted_values[n // 2 - 1] + sorted_values[n // 2]
    return total // 2 if total % 2 == 0 else total / 2


def summarize_counts(episodes):
    """参加者ごとの episode 数の列から要約を作る。0 人なら `min` / `median` / `max` は `None`。"""
    ordered = sorted(episodes)
    if not ordered:
        return {"n_participants": 0, "episodes_per_participant_sorted": [], "min": None, "median": None, "max": None}
    return {
        "n_participants": len(ordered),
        "episodes_per_participant_sorted": ordered,
        "min": ordered[0],
        "median": _median(ordered),
        "max": ordered[-1],
    }


def aggregate(sessions, identity):
    """`sessions` = `[(participant_id, session_id, {pole: 射影})]` から、出力の dict を作る。"""
    poles_out = {}
    for pole in POLES:
        participants = {}
        for participant, _session, projections in sessions:
            projection = projections[pole]
            entry = participants.setdefault(participant, dict.fromkeys(_PARTICIPANT_KEYS, 0))
            entry["sessions"] += 1
            if projection["pole_applicable"]:
                entry["episodes"] += projection["onsets"]
            else:
                entry["sessions_not_applicable"] += 1
        with_applicable = [
            entry["episodes"] for entry in participants.values() if entry["sessions"] > entry["sessions_not_applicable"]
        ]
        poles_out[pole] = {
            "participants": participants,
            "summary": summarize_counts(with_applicable),
            "participants_without_applicable_sessions": len(participants) - len(with_applicable),
        }
    prereg_version, prereg_sha256_prefix = identity
    return {
        "poles": poles_out,
        "provenance": {
            "prereg_version": prereg_version,
            "prereg_sha256_prefix": prereg_sha256_prefix,
            "tool": TOOL,
            "n_sessions": len(sessions),
        },
    }


def run(root):
    """読む → 射影 → 凍結既定の検査 → 集計。書き込みはしない。`LayoutError` / `EnvelopeError` / `NotFrozenError` を送出する。"""
    sessions = []
    for participant, session, paths in fio.discover(root):
        envelopes = fio.load_session(paths)
        sessions.append((participant, session, {pole: fio.project_pg1(envelopes[pole]) for pole in POLES}))
    identity = check_frozen(sessions)
    return aggregate(sessions, identity)


def _write_new(out_path, text):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="p1_pg1_distribution.py",
        description="PG-1 に渡す「参加者ごとの episode 数の分布」だけを出す (転帰・予測成績・行の中身は読まない)。",
    )
    parser.add_argument("--root", required=True, help="<root>/<P-ID>/<session>/{baseline,pointer_b,modifier_m_plus}.json")
    parser.add_argument("--out", required=True, help="出力 JSON (★ repo の外。既存のファイルは上書きしない)")
    args = parser.parse_args(argv)  # ⚠️ 引数の不備は argparse が exit 2 にする

    try:
        out_path = guard_paths(args.root, args.out)
    except GuardError as e:
        print(f"[pg1] NG (出力先のガード): {e}", file=sys.stderr)
        return EXIT_GUARD
    try:
        result = run(args.root)
    except fio.FeaturesIOError as e:
        print(f"[pg1] NG (レイアウトまたは封筒の形): {e}", file=sys.stderr)
        return EXIT_LAYOUT
    except NotFrozenError as e:
        print(f"[pg1] NG (凍結既定でない出力): {e}", file=sys.stderr)
        return EXIT_NOT_FROZEN
    try:
        _write_new(out_path, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    except OSError as e:
        print(f"[pg1] NG (出力を書けない): {e}", file=sys.stderr)
        return EXIT_GUARD
    print(f"[pg1] OK: {result['provenance']['n_sessions']} sessions → {out_path}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
