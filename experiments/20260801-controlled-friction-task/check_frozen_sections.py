#!/usr/bin/env python3
"""preregistration.md の凍結節が第 1 版から変わっていないことを機械的に検査する。

★ なぜ要るか
------------
`preregistration.md` は第 2 版から第 17 版まで、毎版こう主張してきた:

    ★ **`§3.1` / `§3.2` / `§3.4` / `§3.5` / `§3.6` は第 1 版から byte-identical のまま。**

⚠️ **この主張は 2026-09-03 まで一度も機械的に検算されていなかった。** 実際に測ると:

  - `§3.1` / `§3.2` / `§3.4` → ✅ 第 1 版から byte-identical（主張どおり）
  - `§3.5` / `§3.6`         → ⚠️ **byte-identical ではない**。
      `§3.5` は第 16 版が `§3.5-S`（中断ブロックの感度分析）を **21 行追記**、
      `§3.6` は第 2 版が注記を **7 行追記**している。
      ★ ただしどちらも **strictly append-only** で、第 1 版の行列は
        **現行の先頭にそのまま残っている**（＝禁止事項は 1 つも変わっていない）。

→ ★ 本スクリプトは**その 2 種類の凍結をそれぞれ正しく**検査する:

  | 節 | 契約 |
  |---|---|
  | `§3.1` / `§3.2` / `§3.4` | 節**全体**が第 1 版と byte-identical |
  | `§3.5` / `§3.6`          | 節の**先頭 N 行**が第 1 版と byte-identical（追記のみ許す） |

⚠️ `verify-before-claiming` ルール 6:「主張を書いたら、その主張を検査するものを一緒に置く」。

★ 測定器の落とし穴（2026-09-03 に私が実際に踏んだ）
--------------------------------------------------
最初は見出しを `^#{2,3} .*?(3\\.\\d+)` で拾い、**改訂履歴の中の
`### ⚠️★★【第 16 版で撤回】§3.6 との緊張 …` を `§3.6` 本体と誤認**した。
その結果「§3.6 は第 1 版と全然違う」という**偽の相違**を出しかけた。

→ ★ 対策を 2 つ入れてある:
   1. 見出しの正規表現を `^### (?:★ )?3\\.\\d+ ` に厳密化する（節番号が**行頭側**に来る形だけ）
   2. ⚠️ **同じ節番号の見出しが 2 回現れたら NG にする**（黙って最後のものを採らない）

pin 値の出所
------------
第 1 版 = commit `6013104`（2026-08-02 "test(experiments): G1 統制タスク実験を事前登録して凍結する"）。
★ git が無い環境でも動くよう、値は**定数として持つ**。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# ★ 本文の節見出しだけを拾う。改訂履歴の「§3.6 との緊張」のような言及見出しは拾わない。
SECTION_HEAD = re.compile(r"^### (?:★ )?(3\.\d+) ")
# ★ 節の終端 = 次の見出し（h1/h2/h3 のいずれか）
ANY_HEAD = re.compile(r"^#{1,3} ")

# ★ 第 1 版 (6013104) から取った pin。(行数, 先頭その行数ぶんの sha256)
#   full=True  → 節全体がこの行数・この hash でなければならない（byte-identical）
#   full=False → 節の先頭がこの行数・この hash でなければならない（append-only）
FIRST_VERSION = "6013104"
PINS: dict[str, tuple[int, str, bool]] = {
    "3.1": (16, "98ed0709efcee7bdf23b453b1c8fd99529b120e6c827111c7104815f7c1a08c5", True),
    "3.2": (19, "897961416c05bbf98cc6a3efb0a0ad862d3b4dc7281aa7964aabac7adad2da0f", True),
    "3.4": (6, "f0dad0b12b4d158786a31c7846da5a9f5c4b0367b0e87ea9ccd1321278ebe67d", True),
    "3.5": (16, "6c502073a0d38b5daa041f67c6d3d809f76a15ba34110182cc2af54b7af434c0", False),
    "3.6": (9, "b0bc1ef551687d99ed3d4f531f8cd872df85ddfc3c447ddf3ac3bb152351a401", False),
}


def _sha(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def extract_sections(text: str) -> dict[str, list[list[str]]]:
    """`### 3.x ...` から次の見出しの直前までを切り出す。

    ⚠️ 同じ節番号が複数回出うるので、**リストで返す**（呼び出し側が 2 個以上を NG にする）。
    """
    out: dict[str, list[list[str]]] = {}
    cur: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if cur is not None:
            out.setdefault(cur, []).append(buf[:])

    for line in text.split("\n"):
        m = SECTION_HEAD.match(line)
        if m:
            flush()
            cur = m.group(1)
            buf = [line]
            continue
        if cur is not None and ANY_HEAD.match(line):
            flush()
            cur = None
            buf = []
            continue
        if cur is not None:
            buf.append(line)
    flush()
    return out


def check(text: str) -> list[str]:
    """NG メッセージのリストを返す（空なら緑）。"""
    errors: list[str] = []
    found = extract_sections(text)

    for key, (n_lines, want, full) in sorted(PINS.items()):
        occurrences = found.get(key)
        if not occurrences:
            errors.append(
                f"[NG] §{key} が見つからない。★ 凍結節を消してはならない"
                f"（見出しの形は `### {key} ...`）"
            )
            continue
        if len(occurrences) > 1:
            errors.append(
                f"[NG] §{key} の見出しが {len(occurrences)} 回ある。"
                f"⚠️ どれが本体か機械的に決められない（★ 節番号の重複は測定器を壊す）"
            )
            continue

        body = occurrences[0]
        if full:
            got = _sha(body)
            if len(body) != n_lines or got != want:
                errors.append(
                    f"[NG] §{key} が第 1 版（{FIRST_VERSION}）と byte-identical でない。"
                    f"★ 期待 {n_lines} 行 / {want[:16]}…、実際 {len(body)} 行 / {got[:16]}…"
                )
        else:
            if len(body) < n_lines:
                errors.append(
                    f"[NG] §{key} が第 1 版より短い（{len(body)} 行 < {n_lines} 行）。"
                    f"⚠️ 追記は許すが**削除は許さない**"
                )
                continue
            got = _sha(body[:n_lines])
            if got != want:
                errors.append(
                    f"[NG] §{key} の第 1 版部分が書き換わっている（append-only 違反）。"
                    f"★ 先頭 {n_lines} 行の期待 {want[:16]}…、実際 {got[:16]}…"
                )
    return errors


def _selftest() -> int:
    """⚠️ 正常 / 不在 / 壊れ の 3 状態＋陰性対照で検査自体を試す。

    ★ 「正常なら緑」だけ試して満足しない（`verify-before-claiming` ルール 5b）。
    """
    here = Path(__file__).resolve().parent
    src = here / "preregistration.md"
    if not src.is_file():
        print("[NG] preregistration.md が無いので selftest できない")
        return 1
    text = src.read_text(encoding="utf-8")
    fails: list[str] = []
    ran = 0

    # --- 1. 正常 → 緑であること
    ran += 1
    errs = check(text)
    if errs:
        fails.append("★ 現行の preregistration.md が緑にならない: " + " / ".join(errs))

    lines = text.split("\n")

    def find_head(key: str) -> int:
        for i, ln in enumerate(lines):
            m = SECTION_HEAD.match(ln)
            if m and m.group(1) == key:
                return i
        raise AssertionError(f"§{key} の見出しが見つからない")

    def section_range(key: str) -> tuple[int, int]:
        start = find_head(key)
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if ANY_HEAD.match(lines[j]):
                end = j
                break
        return start, end

    # --- 2. 不在 → 赤であること（§3.6 の節ごと削る）
    ran += 1
    s, e = section_range("3.6")
    if not check("\n".join(lines[:s] + lines[e:])):
        fails.append("★ §3.6 を丸ごと削っても緑になった（不在を検出できていない）")

    # --- 3. 壊れ → 赤であること（§3.6 の禁止事項を 1 行書き換える）
    ran += 1
    broken = lines[:]
    hit = None
    for j in range(*section_range("3.6")):
        if broken[j].startswith("- ❌ **ブロックを事後に除外しない**"):
            hit = j
            break
    if hit is None:
        fails.append("★ §3.6 の「ブロックを事後に除外しない」行が見つからない（変異を当てられていない）")
    else:
        # ⚠️ 「技術的なログ欠損・切断のみ」を緩める向きの改竄を模す
        broken[hit] = "- ❌ **ブロックを事後に除外しない**（除外規則: 研究者が妥当と判断したもの）。"
        if not check("\n".join(broken)):
            fails.append("★ §3.6 の禁止事項を書き換えても緑になった（改竄を検出できていない)")

    # --- 3b. 壊れ（full 側） → 赤であること（§3.1 に 1 行足す）
    ran += 1
    s31, _ = section_range("3.1")
    appended31 = lines[:s31 + 1] + ["★ 事後に足した 1 行（byte-identical を壊す）"] + lines[s31 + 1:]
    if not check("\n".join(appended31)):
        fails.append("★ §3.1 に 1 行足しても緑になった（full 側の byte-identical が効いていない）")

    # --- 4. ★ 陰性対照: §3.6 への「追記だけ」は緑のままであること
    ran += 1
    _, e36 = section_range("3.6")
    appended36 = lines[:e36] + ["", "★ append-only の追記（第 1 版部分は触っていない）"] + lines[e36:]
    if check("\n".join(appended36)):
        fails.append("★ §3.6 に追記しただけで赤になった（append-only を殺している）")

    # --- 5. ★ 測定器の対照: 節番号が 2 回出たら止まること
    ran += 1
    dup = lines[:] + ["", "### 3.6 事前に宣言する「やらないこと」", "- ❌ dummy"]
    if not check("\n".join(dup)):
        fails.append("★ §3.6 の見出しが 2 回あっても緑になった（誤認の再発を塞げていない）")

    # ⚠️ 「FAIL が 1 件も出ていなければ赤」— 検査自体が空回りしていないことの確認
    if ran != 6:
        fails.append(f"★ selftest のケース数が想定と違う（{ran} != 6）。集計から漏れたケースがある")

    for f in fails:
        print("  " + f)
    print(f"[{'OK' if not fails else 'NG'}] check_frozen_sections selftest: {ran} ケース / NG {len(fails)} 件")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(Path(__file__).resolve().parent / "preregistration.md"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()

    path = Path(args.file)
    if not path.is_file():
        print(f"[NG] {path} が無い")
        return 1
    errors = check(path.read_text(encoding="utf-8"))
    for e in errors:
        print(e)
    if errors:
        print(f"[NG] 凍結節 {len(errors)} 件が第 1 版（{FIRST_VERSION}）と一致しない")
        return 1
    kinds = ", ".join(
        f"§{k}{'(全体)' if full else '(append-only)'}" for k, (_, _, full) in sorted(PINS.items())
    )
    print(f"[OK] 凍結節は第 1 版（{FIRST_VERSION}）と一致: {kinds}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
