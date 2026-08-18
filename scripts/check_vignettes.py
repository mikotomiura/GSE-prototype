#!/usr/bin/env python3
"""PreReg-1 尺度理解テストのビネット構成を機械検査する。

`src/components/VignetteTest.tsx` の `VIGNETTES` 配列を読み、次を検証する:

  C1  場面文に Q1/Q2 のアンカー語 (およびその明白な同義語) が含まれない
  C2  提示順で同一象限が連続しない
  C3  4 象限が各 2 問ずつ・合計 8 問
  C4  vignette_id が backend の不透明 ID 規則 (`[A-Za-z0-9_-]{1,16}`) を満たし、重複しない

背景 (`.steering/20260817-prereg1-scale-instructions/decisions.md` D-7 / D-8):
旧版のビネットは 8 問すべてが「前に進まない」「前進している感覚はある」のように
Q1/Q2 のアンカー語を**逐語で含んで**おり、尺度を理解していなくても文字列マッチングで
解けた。また同一象限が隣接していたため 2 問目が 1 問目の答えを写せた。
本検査はその再発を防ぐ。

⚠️ 本スクリプト自身の空振り検査は `--self-test` で走る (C1–C4 が
   「わざと壊した入力」で赤になることを確かめる)。CI/フックから呼ぶときも
   `--self-test` を併走させること。検査が常に緑を返していないかは、
   検査を書いた人間が確かめる責任がある。

使い方:
    PYTHONUTF8=1 python scripts/check_vignettes.py
    PYTHONUTF8=1 python scripts/check_vignettes.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VIGNETTE_TSX = REPO_ROOT / "src" / "components" / "VignetteTest.tsx"

# Q1/Q2 のアンカー語とその明白な同義語。場面文に現れてはならない。
# (教示文側では使ってよい。禁じているのは**場面文**だけ。)
BANNED_SUBSTRINGS = [
    "詰ま",      # Q1 アンカー
    "引っかか",  # Q1 アンカー
    "進",        # Q2 アンカー (前進 / 進む / 進んで …)
    "近づ",      # Q2 アンカー
    "手応え",
    "はかど",
    "停滞",
    "スラスラ",
    "すらすら",
]

EXPECTED_QUADRANTS = {"flow", "stuck", "incubation", "idle"}
EXPECTED_TOTAL = 8
EXPECTED_PER_QUADRANT = 2
OPAQUE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,16}$")

# `{ id: "...", quadrant: "...", text: "..." }` を順序どおり拾う。
ENTRY_RE = re.compile(
    r"id:\s*\"(?P<id>[^\"]*)\"\s*,\s*"
    r"quadrant:\s*\"(?P<quadrant>[^\"]*)\"\s*,\s*"
    r"text:\s*\"(?P<text>(?:[^\"\\]|\\.)*)\"",
    re.DOTALL,
)


class CheckError(Exception):
    """検査失敗。メッセージがそのまま人間向けの説明になる。"""


def parse_vignettes(source: str) -> list[dict[str, str]]:
    """`VIGNETTES` 配列の中身だけを取り出して (id, quadrant, text) を返す。"""
    start = source.find("const VIGNETTES")
    if start == -1:
        raise CheckError("VIGNETTES 配列が見つからない (VignetteTest.tsx の構造が変わった?)")
    open_bracket = source.find("[", start)
    close_bracket = source.find("\n];", open_bracket)
    if open_bracket == -1 or close_bracket == -1:
        raise CheckError("VIGNETTES 配列の範囲を特定できない")
    block = source[open_bracket : close_bracket + 1]
    entries = [m.groupdict() for m in ENTRY_RE.finditer(block)]
    if not entries:
        raise CheckError("VIGNETTES 配列から 1 件も抽出できなかった")
    return entries


def check_c1_no_anchor_words(entries: list[dict[str, str]]) -> list[str]:
    """C1: 場面文に Q1/Q2 のアンカー語が含まれない。"""
    errors = []
    for i, e in enumerate(entries, 1):
        hits = [w for w in BANNED_SUBSTRINGS if w in e["text"]]
        if hits:
            errors.append(
                f"C1 場面 {i} ({e['id']}): 禁止語 {hits} を含む — "
                f"尺度を理解しなくても文字列一致で解けてしまう\n    {e['text']}"
            )
    return errors


def check_c2_no_adjacent_same_quadrant(entries: list[dict[str, str]]) -> list[str]:
    """C2: 提示順で同一象限が連続しない。"""
    errors = []
    for i in range(1, len(entries)):
        if entries[i]["quadrant"] == entries[i - 1]["quadrant"]:
            errors.append(
                f"C2 場面 {i} と {i + 1} が同じ象限 ({entries[i]['quadrant']}) で隣接 — "
                f"2 問目が 1 問目の答えを写せてしまう"
            )
    return errors


def check_c3_balanced_quadrants(entries: list[dict[str, str]]) -> list[str]:
    """C3: 4 象限が各 2 問ずつ・合計 8 問。

    この均等配置が、どの定数回答 (straight-lining) でも一致が最大 2/8 にしかならない
    ことを保証している (合格条件 6/8 に構造的に届かない)。崩すと straight-lining が
    通り抜けうるため、合格条件と同じ重さで守る。
    """
    errors = []
    if len(entries) != EXPECTED_TOTAL:
        errors.append(f"C3 ビネット数が {len(entries)} 問 (PreReg-1 は 8 問)")
    counts = {q: 0 for q in EXPECTED_QUADRANTS}
    for i, e in enumerate(entries, 1):
        q = e["quadrant"]
        if q not in EXPECTED_QUADRANTS:
            errors.append(f"C3 場面 {i}: 未知の象限 {q!r}")
        else:
            counts[q] += 1
    for q in sorted(EXPECTED_QUADRANTS):
        if counts[q] != EXPECTED_PER_QUADRANT:
            errors.append(
                f"C3 象限 {q} が {counts[q]} 問 (各 2 問でないと "
                f"straight-lining の一致上限 2/8 が保証されない)"
            )
    return errors


def check_c4_opaque_ids(entries: list[dict[str, str]]) -> list[str]:
    """C4: vignette_id が backend の不透明 ID 規則を満たし、重複しない。"""
    errors = []
    seen: set[str] = set()
    for i, e in enumerate(entries, 1):
        vid = e["id"]
        if not OPAQUE_ID_RE.match(vid):
            errors.append(
                f"C4 場面 {i}: vignette_id {vid!r} が lib.rs::is_valid_opaque_id "
                f"([A-Za-z0-9_-] 1..=16 文字) を満たさない"
            )
        if vid in seen:
            errors.append(f"C4 vignette_id {vid!r} が重複している")
        seen.add(vid)
    return errors


ALL_CHECKS = (
    check_c1_no_anchor_words,
    check_c2_no_adjacent_same_quadrant,
    check_c3_balanced_quadrants,
    check_c4_opaque_ids,
)


def run_checks(entries: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for check in ALL_CHECKS:
        errors.extend(check(entries))
    return errors


# ---------------------------------------------------------------------------
# 空振り検査 (--self-test)
#
# ⚠️ 検査を書いたら「H0 が偽のとき赤になるか」を必ず確かめる
#    (`.steering/_handoff/next-session-prompt-prereg1-scale-instructions.md` §4.5 の教訓)。
#    以下は「わざと壊した入力」で各検査が実際に落ちることを確認する。
# ---------------------------------------------------------------------------

_GOOD = [
    {"id": "t1", "quadrant": "flow", "text": "打ち続けた。段落が 3 つ増えた。"},
    {"id": "t2", "quadrant": "stuck", "text": "同じ一文を書いては消している。"},
    {"id": "t3", "quadrant": "incubation", "text": "手が止まったが見取り図ができた。"},
    {"id": "t4", "quadrant": "idle", "text": "惰性で書式をそろえている。"},
    {"id": "t5", "quadrant": "flow", "text": "順番のまま打てている。"},
    {"id": "t6", "quadrant": "stuck", "text": "決められないままカーソルが点滅している。"},
    {"id": "t7", "quadrant": "incubation", "text": "何度も書き直して筋が一本になった。"},
    {"id": "t8", "quadrant": "idle", "text": "眺めているだけで何も打っていない。"},
]


def _mutate(index: int, **overrides) -> list[dict[str, str]]:
    broken = [dict(e) for e in _GOOD]
    broken[index].update(overrides)
    return broken


def self_test() -> int:
    """各検査が「壊した入力」で赤になり、「正しい入力」で緑になることを確かめる。"""
    failures: list[str] = []

    # 前提: 正しい入力では全検査が緑。
    if run_checks(_GOOD):
        failures.append(f"self-test: 正しい入力で赤になった → {run_checks(_GOOD)}")

    cases = [
        (
            "C1",
            check_c1_no_anchor_words,
            _mutate(1, text="同じ一文を書いては消し、まったく前に進まない。"),
        ),
        (
            "C2",
            check_c2_no_adjacent_same_quadrant,
            _mutate(1, quadrant="flow"),  # t1 も flow → 隣接
        ),
        (
            "C3",
            check_c3_balanced_quadrants,
            _mutate(1, quadrant="idle"),  # stuck 1 / idle 3 に崩す
        ),
        (
            "C4",
            check_c4_opaque_ids,
            _mutate(1, id="本文が入った ID"),
        ),
    ]
    for name, check, broken in cases:
        if not check(broken):
            failures.append(f"self-test: {name} が壊した入力で緑のまま (空振りしている)")

    # C3 の「問数」側も刺す。
    if not check_c3_balanced_quadrants(_GOOD[:7]):
        failures.append("self-test: C3 が 7 問の入力で緑のまま")

    if failures:
        for f in failures:
            print(f"NG {f}", file=sys.stderr)
        return 1
    print("OK self-test: C1-C4 はいずれも壊した入力で赤になる (空振りしていない)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="検査自身が H0 偽のとき赤になるかを確かめる (空振り検査)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not VIGNETTE_TSX.exists():
        print(f"NG {VIGNETTE_TSX} が見つからない", file=sys.stderr)
        return 1

    try:
        entries = parse_vignettes(VIGNETTE_TSX.read_text(encoding="utf-8"))
    except CheckError as e:
        print(f"NG {e}", file=sys.stderr)
        return 1

    errors = run_checks(entries)
    if errors:
        print(f"NG ビネット構成に {len(errors)} 件の問題:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    order = " -> ".join(e["quadrant"] for e in entries)
    print(f"OK ビネット {len(entries)} 問 / C1-C4 すべて通過")
    print(f"   提示順: {order}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
