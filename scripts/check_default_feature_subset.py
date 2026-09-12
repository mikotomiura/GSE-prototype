#!/usr/bin/env python3
"""default features が `--features package` の **真部分集合**であり続けることを守る検査器。

⚠️★★★ **これは F-4 (CI に default features の clippy を足す) を「やらない」判断の担保である。**

★ 経緯 (2026-09-12・PR #199):
  CI の clippy は `ci.yml` の **1 箇所だけ**で `--all-targets --features package` である。
  ⚠️ default features のみの clippy は CI に存在しない。
  → ★ しかし `cfg(not(feature = "package"))` が **repo 全体で 0 件**であることを実測したので、
    **default スコープは package スコープの真部分集合**であり、
    ⚠️ **F-4 を足してもカバレッジは 1 mm も増えない**と判断した。

⚠️★★★ **その判断が成り立つ条件は 1 つだけである**:
  **誰も `#[cfg(not(feature = "package"))]` を書かないこと。**
  → ★ 書かれた瞬間「default にしか無いコード」が生まれ、**CI が二度と見ない領域**になる。
  ⚠️ 人の記憶で守らない。**これが機械の側である。**

★ 破れたときにやること (⚠️ この検査器を黙らせるのではない):
  1. ★ その `cfg(not(...))` が本当に必要か問う (⚠️ たいてい `cfg(feature = ...)` の反転で済む)。
  2. ★ 本当に必要なら **F-4 を実施する** —— CI に default features の clippy job を足す。
  3. ⚠️ そのうえで本検査器の対象から外す (★ 理由を添えて)。

## ⚠️ 実装上の注意 (★ 本 repo が 2 回踏んだ罠)

**検査対象に検査パターンをリテラルで書かない。** ★ 書くと自分自身にヒットして
「常に赤」か、除外した結果「常に緑」になり、⚠️ **どちらも実在の欠陥と見分けがつかない**。
→ ★ 本ファイルは `scripts/` にあり検査対象 (`src-tauri/`) の外だが、
  **それに依存せず実行時連結でパターンを作る**。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ★ 走査対象。⚠️ Cargo がビルドするものと一致させる (build.rs を忘れない)。
TARGETS = ("src-tauri/src", "src-tauri/tests", "src-tauri/build.rs")

# ⚠️★★★ パターンは**実行時に連結して作る** (★ 上記「実装上の注意」)。
_NOT = "n" + "ot"
_FEATURE = "fe" + "ature"
_PACKAGE = "pack" + "age"
_FEAT_EQ = _FEATURE + r"\s*=\s*\"" + _PACKAGE + r"\""

# ⚠️★★★ **`cfg(` の直後に限定しない** (★ 2026-09-12 に陽性対照が穴を見つけた)。
#   ⚠️ 初版は `cfg\(\s*not\(` に限定していたため、
#     `#[cfg(all(unix, not(feature = "package")))]` のような**入れ子を素通り**させた。
#   → ★ `not(...)` 単位で探す。★ 空白・クォートの揺れも吸収する。
PATTERNS = (
    # ★ 形 1: `not(feature = "package")` —— 単独でも `all(..)` / `any(..)` の中でも当たる
    re.compile(_NOT + r"\s*\(\s*" + _FEAT_EQ + r"\s*\)"),
    # ★ 形 2: `not(all(feature = "package", ..))` / `not(any(.., feature = "package"))`
    #   ⚠️ これも「package でないときに有効」な枝を生むので違反である。
    re.compile(_NOT + r"\s*\(\s*(?:all|any)\s*\([^)]*" + _FEAT_EQ),
)

# ⚠️★★★ **既知の限界を隠さない** (★ 「全部見ている」と誤解させない)。
#   ・1 行に収まらない `cfg` (★ 改行を跨ぐ) は見ない —— ⚠️ rustfmt が 1 行に収めるので実害は薄い。
#   ・`cfg_attr` の中の入れ子や、マクロ経由で組み立てられた cfg は見ない。
#   → ★ これらは**検出できない**。⚠️ 本検査は「うっかり」を止めるものであって証明ではない。
KNOWN_LIMITS = (
    "複数行に跨る cfg",
    "cfg_attr / マクロ経由で組み立てられた cfg",
)


def _matches(line: str) -> bool:
    return any(p.search(line) for p in PATTERNS)


def scan(root: Path) -> tuple[list[tuple[Path, int, str]], int]:
    """違反の一覧と、**実際に読んだファイル数**を返す。

    ⚠️ ファイル数を返すのは、★ **1 つも読まずに「違反 0 件」で緑になる**のを
    呼び出し側が弾けるようにするため (`silent-failure-in-guard-scripts` の型)。
    """
    hits: list[tuple[Path, int, str]] = []
    scanned = 0
    for target in TARGETS:
        p = root / target
        files = [p] if p.is_file() else sorted(p.rglob("*.rs")) if p.is_dir() else []
        for f in files:
            if f.suffix != ".rs":
                continue
            scanned += 1
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if _matches(line):
                    hits.append((f.relative_to(root), i, line.strip()))
    return hits, scanned


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    hits, scanned = scan(root)

    # ⚠️★★★ **0 ファイルは「違反なし」ではなく「検査できていない」。**
    #   ★ パスを間違えた / 走査対象が消えた場合に**黙って緑**になるのを防ぐ。
    if scanned == 0:
        print(
            f"FAIL: 検査対象の .rs を 1 つも読めなかった (root={root})\n"
            f"  ⚠️ これは「違反 0 件」ではなく「**検査が動いていない**」。\n"
            f"  ★ 対象: {', '.join(TARGETS)}",
            file=sys.stderr,
        )
        return 2

    if hits:
        print(
            f"FAIL: default features 専用コードが {len(hits)} 件見つかった "
            f"({scanned} ファイルを走査)",
            file=sys.stderr,
        )
        for path, line_no, text in hits:
            print(f"  {path}:{line_no}: {text}", file=sys.stderr)
        print(
            "\n"
            "⚠️★★★ これが入ると default スコープは `--features package` の真部分集合でなくなる。\n"
            "★ CI の clippy は `--features package` の 1 本だけなので、\n"
            "  ⚠️ **この行のコードは CI で二度と lint されない。**\n"
            "\n"
            "★ どうするか (⚠️ この検査を黙らせるのではない):\n"
            "  1. その cfg が本当に必要か問う (★ たいてい肯定形の cfg で書ける)。\n"
            "  2. 必要なら **F-4 を実施する** = CI に default features の clippy job を足す。\n"
            "  3. そのうえで本検査の対象から外す (★ 理由を添えて)。\n"
            "\n"
            "★ 経緯: .steering/20260912-mac-default-clippy-green/ / "
            ".steering/20260912-f3-f4-clippy-scope/",
            file=sys.stderr,
        )
        return 1

    print(f"OK: default features 専用コードは 0 件 ({scanned} ファイルを走査)")
    print("  ⚠️ 既知の限界 (★ 検出できない形): " + " / ".join(KNOWN_LIMITS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
