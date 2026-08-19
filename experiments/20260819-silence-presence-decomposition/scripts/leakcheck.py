#!/usr/bin/env python
"""漏洩検査。★ `data-privacy` / S5C-D8 / `expression-power` の security-checker M1。

⚠️★★★ **NDJSON のファイル名形式は、S5C-D8 が実際に外部 LLM へ漏らした形式そのものである。**
→ 本実験のどのファイルにも書かない。OS ユーザー名・絶対パスも同様。

★ 走査範囲は `--root` で複数指定できる（既定は本実験ディレクトリ）。
⚠️ `requirement.md` の AC-8 は「**repo 内のどのファイルにも書かない**」と宣言しているので、
`run.sh` は `.steering/` と `docs/adr/` も渡す（★ 旧版は実験ディレクトリしか見ておらず、
**宣言と実装が矛盾していた** —— security-checker MEDIUM）。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

DEFAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

SKIP_DIRS = {"__pycache__", ".git", "node_modules", "target"}

# ★ 本ファイル自身はパターン定義を含むので除外する（自己言及で必ず当たる）。
SELF = os.path.abspath(__file__)


def _user_patterns():
    """⚠️★★★ **OS ユーザー名をソースに平文で埋めない**（security-checker MEDIUM）。

    検査器自身が検査対象の秘密を repo へ永久記録するのは本末転倒である
    （★ 本 repo は一時 public にする運用があり、git 履歴は消せない）。
    → **実行時に取得する。**
    """
    names = set()
    try:
        import getpass

        names.add(getpass.getuser())
    except Exception:
        pass
    for key in ("USERNAME", "USER", "LOGNAME"):
        v = os.environ.get(key)
        if v:
            names.add(v)
    pats = []
    for n in sorted(x for x in names if x and len(x) >= 3):
        pats.append((re.compile(r"\b" + re.escape(n) + r"\b", re.IGNORECASE), "OS ユーザー名"))
    return pats


PATTERNS = [
    # ★ NDJSON のファイル名形式（S5C-D8 が漏らした形）。
    #   ⚠️ id 幅は 2〜4 桁ありうる（`.gitignore` が「gse-package が受け付ける id 幅」として明記）。
    (re.compile(r"P\d{1,4}_gse_"), "NDJSON のファイル名形式 (P<id>_gse_...)"),
    # ★ logger が出す**素の**ファイル名（`data-privacy` ルール 2 の形式）。
    (re.compile(r"gse_\d{8}_\d{6}\.ndjson"), "NDJSON のファイル名形式 (gse_YYYYMMDD_HHMMSS)"),
    # ★ Windows 絶対パス。⚠️ 旧版は連続 2 個の区切りを要求していて
    #   `C:\gse-dataset\raw` のような**素のパスを素通り**させていた。
    (re.compile(r"[A-Za-z]:[\\/][A-Za-z0-9_.\- ]"), "Windows 絶対パス"),
    # ★ POSIX のホームパス / チルダ表記
    (re.compile(r"/(?:home|Users)/[A-Za-z0-9_.\-]+/"), "POSIX ホームパス"),
    (re.compile(r"~/[A-Za-z0-9_.\-/]*(?:GSE|gse)"), "チルダ表記のホームパス"),
] + _user_patterns()


def scan(root: str, hits: list[str]) -> int:
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            if os.path.abspath(p) == SELF:
                continue
            try:
                with open(p, encoding="utf-8") as fh:
                    body = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            for pat, label in PATTERNS:
                for m in pat.finditer(body):
                    line_no = body.count("\n", 0, m.start()) + 1
                    hits.append(f"{rel}:{line_no}  [{label}]  {m.group(0)!r}")
    return scanned


def selfcheck() -> list[str]:
    """★ **陽性対照**: 既知の漏洩形が確実に捕まることを毎回確かめる。

    ⚠️ 検査器が false green を返すのが最悪の失敗なので、
    「落ちるべきものが落ちる」ことを実行時に固定する（`.gitignore` の教訓）。
    """
    # ⚠️★★★ **陽性対照に実在形式のセッション名を書かない。**
    #   `scripts/secrets-filter.sh` 逐語「**『漏洩について書く』と『漏洩を再導入する』は同じ動作である**」。
    #   ★ repo の約束は **架空名（`_00000000_` / 年 2000）で書くこと**であり、
    #   `secrets-filter` は年 `202x` にのみ反応してこの形を素通りさせる設計になっている
    #   （★ 架空名まで止めると「人がフィルタを迂回する動機」を作ってしまうため）。
    probes = [
        ("P000_gse_20001231_000000.ndjson", "NDJSON のファイル名形式 (P<id>_gse_...)"),
        ("P9001_gse_x.ndjson", "NDJSON のファイル名形式 (P<id>_gse_...)"),
        ("gse_20001231_000000.ndjson", "NDJSON のファイル名形式 (gse_YYYYMMDD_HHMMSS)"),
        ("C:\\gse-dataset\\raw\\P010", "Windows 絶対パス"),
        ("D:/phase1-raw/", "Windows 絶対パス"),
        ("/home/someone/data/", "POSIX ホームパス"),
        ("~/Documents/GSE-sessions", "チルダ表記のホームパス"),
    ]
    failures = []
    for text, expect in probes:
        if not any(pat.search(text) for pat, label in PATTERNS if label == expect):
            failures.append(f"陽性対照が捕まらない: {text!r} (期待ラベル: {expect})")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", default=None, help="走査する根（複数可）")
    args = ap.parse_args()

    probe_failures = selfcheck()
    if probe_failures:
        print("!! 検査器そのものが壊れている（陽性対照が素通り）:", file=sys.stderr)
        for f in probe_failures:
            print(f"   - {f}", file=sys.stderr)
        return 2

    roots = args.root or [DEFAULT_ROOT]
    hits: list[str] = []
    scanned = 0
    for r in roots:
        if os.path.isdir(r):
            scanned += scan(os.path.abspath(r), hits)

    print(
        f"== 漏洩検査: {scanned} ファイルを走査"
        f"（root {len(roots)} 個・パターン {len(PATTERNS)} 種・陽性対照 ok）=="
    )
    if hits:
        print(f"!! {len(hits)} 件ヒット:")
        for h in hits:
            print(f"   - {h}")
        return 1
    print("漏洩なし")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
