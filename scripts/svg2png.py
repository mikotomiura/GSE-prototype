#!/usr/bin/env python3
"""図の SVG を PNG へ書き出す（★ `docs/mitou_submission/figures/` の運用）。

## なぜ要るか

★ repo の規約は **SVG が正本・PNG が書き出し**である。⚠️ しかし
**どの手順で PNG を作ったのかがどの文書にも書かれていなかった**（2026-09-04 時点）。
→ ⚠️ 手順が分からないと、SVG だけ直して PNG を置き去りにする事故が起きる。
★ しかも `scripts/md2docx.py --selftest` は **`.png` と `.svg` の寸法一致**を検査するので、
片方だけ更新すると **無関係に見える FAILED** が出る。

## ★★★ 手順は実測で復元した（2026-09-04）

★ LibreOffice の `draw_png_Export` に **SVG の `viewBox` と同じ画素数**を渡すと、
コミット済みの `gse-architecture.png` と **md5 が完全に一致した**
（`661e8a91f4e9fa8ad43c605992c68086`）。→ ★ 既存 4 枚はこの手順で作られている。

⚠️★★★ **PyMuPDF (`fitz`) で書き出してはいけない。** 開けるし PNG も出るが、
★ **`ー`（長音）のグリフが落ち、`text-anchor` の解釈も違って文字が枠からはみ出す**（実測）。

## 使い方

    PYTHONUTF8=1 python scripts/svg2png.py                     # figures/ の全 SVG
    PYTHONUTF8=1 python scripts/svg2png.py path/to/one.svg ...  # 個別
    PYTHONUTF8=1 python scripts/svg2png.py --check              # 書き出さず縦横比だけ検査
    PYTHONUTF8=1 python scripts/svg2png.py --force              # 1 倍でない既存 PNG も上書きする

⚠️ `--force` を付けない限り、**1 倍で書き出されていない既存 PNG は skip する**
（★ `gse-workflow.png` は 3 倍。2026-09-04 に黙って縮小してしまい `git checkout` で戻した）。

⚠️ Windows コンソールは cp932 なので `PYTHONUTF8=1` を付ける。
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGURES = REPO_ROOT / "docs" / "mitou_submission" / "figures"

# ★ 既存 4 枚を作ったのと同じ実体（2026-09-04 に md5 一致で確認）
SOFFICE_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "soffice",
]

VIEWBOX = re.compile(r'viewBox="\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)\s*"')


def find_soffice() -> str:
    for cand in SOFFICE_CANDIDATES:
        if pathlib.Path(cand).is_file():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    raise SystemExit(
        "[NG] LibreOffice (soffice) が見つからない。"
        " / ★ 図の PNG 書き出しには LibreOffice が要る（既存 4 枚もこれで作られている）"
    )


def svg_size(path: pathlib.Path) -> tuple[int, int]:
    m = VIEWBOX.search(path.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"[NG] viewBox が読めない: {path}")
    return round(float(m.group(1))), round(float(m.group(2)))


def png_size(path: pathlib.Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"[NG] PNG ヘッダが不正: {path}")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def export(svg: pathlib.Path, soffice: str) -> pathlib.Path:
    w, h = svg_size(svg)
    opts = (
        'png:draw_png_Export:{"PixelWidth":{"type":"long","value":%d},'
        '"PixelHeight":{"type":"long","value":%d}}' % (w, h)
    )
    out = svg.with_suffix(".png")
    # ⚠️★★★ 先に消す。★ soffice は**何もせず終了コード 0 を返すことがある**
    #   （プロファイルが別プロセスにロックされている等）。古い PNG が残っていると
    #   1 バイトも変換していないのに `[ok]` を出してしまう（code-reviewer 指摘・2026-09-04）。
    out.unlink(missing_ok=True)
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", opts, "--outdir", str(svg.parent), str(svg)],
            check=True,
            capture_output=True,
            timeout=180,  # ⚠️ ロック時に soffice は無限に待つことがある
        )
    except subprocess.TimeoutExpired:
        raise SystemExit(f"[NG] soffice が応答しない（他の LibreOffice を閉じること）: {svg.name}")
    except subprocess.CalledProcessError as e:
        detail = e.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"[NG] soffice が失敗した: {svg.name} / {detail}")
    if not out.is_file():
        raise SystemExit(f"[NG] 書き出しに失敗した（PNG が出ていない）: {out}")
    got = png_size(out)
    if got != (w, h):
        raise SystemExit(f"[NG] 寸法が合わない: {out} {got} != {(w, h)}")
    return out


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    # ⚠️ 未知オプションを黙って無視していた（Codex 指摘）。★ `--chek` が通常実行になっていた。
    known = {"--check", "--force"}
    for a in argv[1:]:
        if a.startswith("--") and a not in known:
            print(f"[NG] 未知のオプション: {a}", file=sys.stderr)
            return 2
    args = [a for a in argv[1:] if not a.startswith("--")]
    targets = [pathlib.Path(a).resolve() for a in args] or sorted(FIGURES.glob("*.svg"))
    # ⚠️ repo 外を対象にしない（★ `md2pptx.resolve_image` と厳しさを揃える）。
    for t in targets:
        try:
            t.relative_to(REPO_ROOT)
        except ValueError:
            raise SystemExit(f"[NG] repo 外の SVG は扱わない: {t}")
    if not targets:
        print(f"[NG] SVG が 1 枚も無い: {FIGURES}", file=sys.stderr)
        return 1

    if check_only:
        # ⚠️★★★ 検査するのは **縦横比**であって画素数の同一ではない。
        # ★ `md2docx.py` は固定幅から高さを導いて比べており（`image_display_size`）、
        #   実際に効く契約は比のほうである。
        # ★ 実測: `gse-workflow.png` は SVG (1200x430) のちょうど **3 倍** (3600x1290) で
        #   コミットされている。→ 画素一致を要求すると**正常な既存図を違反と呼んでしまう**。
        ng = 0
        for svg in targets:
            png = svg.with_suffix(".png")
            if not png.is_file():
                print(f"[NG] 対の PNG が無い: {png}")
                ng += 1
                continue
            (sw, sh), (pw, ph) = svg_size(svg), png_size(png)
            # 比の一致（★ 丸めぶんの許容を 1 画素ぶん見る）
            if abs(pw * sh - ph * sw) > max(pw, ph):
                print(f"[NG] 縦横比が違う: {svg.name} svg={sw}x{sh} png={pw}x{ph}")
                ng += 1
                continue
            scale = pw / sw
            note = "" if abs(scale - 1.0) < 1e-6 else f"  (x{scale:g} で書き出されている)"
            print(f"[ok] {svg.name}  svg={sw}x{sh} png={pw}x{ph}{note}")
        print("[OK] 全対の縦横比が一致" if ng == 0 else f"[FAILED] {ng} 件")
        return 1 if ng else 0

    force = "--force" in argv
    soffice = find_soffice()
    for svg in targets:
        # ⚠️★★★ 既存 PNG が 1 倍で書き出されていない図がある（実測: `gse-workflow.png` は 3 倍）。
        # ★ 本スクリプトは常に 1 倍で出すので、**黙って縮小してしまう**。
        #   2026-09-04 に実際にこれを踏み、`git checkout` で戻した。→ 既定で拒む。
        png = svg.with_suffix(".png")
        if png.is_file() and not force:
            (sw, _sh), (pw, _ph) = svg_size(svg), png_size(png)
            if pw != sw:
                print(
                    f"[skip] {png.name} は x{pw / sw:g} で書き出されている。"
                    " / ★ 1 倍で上書きしてよいなら --force を付ける"
                )
                continue
        out = export(svg, soffice)
        w, h = png_size(out)
        print(f"[ok] {out.relative_to(REPO_ROOT).as_posix()}  {w}x{h}  ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
