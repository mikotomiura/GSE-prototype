#!/usr/bin/env python3
"""設計スライドのデザイン基盤 (`.pptx` テンプレート) を **自前で** 生成する。

## ⚠️★★★ なぜ自前で作るのか (2026-09-04)

★ 研究者が指定したデザイン基盤 `deck_temp1.pptx` を repo へ取り込もうとしたが、
⚠️★★★ **security-checker の指摘で、それが第三者の資料であることが判明した**
（★ 私も独立に開いて確認した）:

| 実測したもの | 中身 |
|---|---|
| `ppt/slides/slide1.xml` | 逐語「**許諾なく撮影や第三者への開示を禁止します**」 |
| `ppt/slides/slide2.xml` | 「アジェンダ / 1)背景 / 2-1)生成AIの基礎知識 …」＝ **生成AI 講座の見本** |
| `ppt/media/image3.png` | **「松尾・岩澤研究室 / Matsuo-Iwasawa Lab UTokyo」のロゴ** |
| `ppt/media/image4.png` | 同研究室の「M」マーク |
| `ppt/fonts/*.fntdata` | Tahoma 2 本（★ 本文では 1 文字も使っていない・519 KB） |

⚠️★★★ **ロゴは `slideMaster1` と `slideLayout5` から参照されているため、
同梱スライドを全部消しても生成物に残り続ける**（★ 実測: 出力 `.pptx` を unzip すると
ロゴのバイト列が出た）。⚠️ **画面には出ない**（全スライドが `showMasterSp="0"`）が、
**IPA 未踏へ出す成果物に第三者研究室のロゴが同梱される**ことに変わりはない。
⚠️ しかも **一度コミットすれば git 履歴から消えない**。

→ ★★★ **第三者のファイルは取り込まず、デザインだけを自前で再現する。**
★ 再現するのは**汎用的な体裁**だけである —— 版面寸法・地の色・左端の帯・配色。
⚠️ **ロゴ・見本スライド・埋め込みフォントは 1 バイトも持ち込まない。**

## 何を再現するか（すべて 2026-09-04 に実測した値）

| 項目 | 値 | 出所 |
|---|---|---|
| 版面 | **10.00 x 5.625 inch**（9144000 x 5143500 EMU） | `Presentation(deck_temp1).slide_width/height` |
| 地 | 全面 `#F4F4F4` の矩形 | `slide4.xml` の `custGeom` + `solidFill` |
| 左端の帯 | 幅 **0.16 inch** の青いグラデーション | `image6.png` (59 x 2029) を実測 |
| 帯の色 | 上 `#B4CBE6` → 中 `#92B3DA` → 下 `#7BA2D2` | 同 PNG を 5 点サンプリング |
| 主色 | `dk2 #158158` | `ppt/theme/theme1.xml` |

★ 帯は **ビットマップではなくグラデーション図形**で描く（★ 画像を持ち込まないため）。

## 使い方

    PYTHONUTF8=1 python scripts/make_deck_template.py

★ 出力先は `docs/mitou_submission/mitou_pptx/_template/gse-deck-template.pptx`。
★ 中身は **python-pptx の既定テンプレート（ライブラリ同梱・MIT）＋ 本スクリプトが描いた図形**だけである。
"""
from __future__ import annotations

import pathlib
import sys
import zipfile

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Emu
except ImportError:  # pragma: no cover - 環境依存
    print("[make_deck_template] FAILED: python-pptx が入っていません。", file=sys.stderr)
    print("  run: pip install -r scripts/requirements-dev.txt", file=sys.stderr)
    raise SystemExit(5)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "docs/mitou_submission/mitou_pptx/_template/gse-deck-template.pptx"

EMU_W, EMU_H = 9144000, 5143500  # ★ 10.00 x 5.625 inch
GROUND = RGBColor(0xF4, 0xF4, 0xF4)
BAR_TOP = RGBColor(0xB4, 0xCB, 0xE6)
BAR_BOTTOM = RGBColor(0x7B, 0xA2, 0xD2)
BAR_W = int(0.16 * 914400)

ZIP_TS = (2026, 1, 1, 0, 0, 0)
FIXED_TS = __import__("datetime").datetime(2026, 1, 1, 0, 0, 0)


def _pick_layout(prs):
    """タイトル(idx=0)と本文(idx=1)を持つレイアウト（★ 見本スライド用）。"""
    for lay in prs.slide_layouts:
        if {0, 1} <= {ph.element.ph_idx for ph in lay.placeholders}:
            return lay
    raise SystemExit("[NG] 既定テンプレートに idx 0/1 を持つレイアウトが無い")


def build(out: pathlib.Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(EMU_W), Emu(EMU_H)
    cp = prs.core_properties
    cp.author, cp.last_modified_by, cp.title = "GSE", "GSE", ""
    cp.created, cp.modified, cp.revision = FIXED_TS, FIXED_TS, 1

    # ★ 「地」だけを持つ見本スライドを 1 枚置く。
    #   `md2pptx.py` の `capture_chrome()` が **図形数が最小のスライド**を見本に選び、
    #   **プレースホルダでなく文字を持たない図形**だけを複製するので、この 2 図形が拾われる。
    slide = prs.slides.add_slide(_pick_layout(prs))

    ground = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(0), Emu(0), Emu(EMU_W), Emu(EMU_H))
    ground.fill.solid()
    ground.fill.fore_color.rgb = GROUND
    ground.line.fill.background()
    ground.shadow.inherit = False

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(0), Emu(0), Emu(BAR_W), Emu(EMU_H))
    bar.fill.gradient()
    bar.fill.gradient_angle = 90.0  # ★ 上から下へ
    stops = bar.fill.gradient_stops
    stops[0].color.rgb = BAR_TOP
    stops[0].position = 0.0
    stops[1].color.rgb = BAR_BOTTOM
    stops[1].position = 1.0
    bar.line.fill.background()
    bar.shadow.inherit = False

    # ⚠️ プレースホルダは見本の飾りなので消す（★ 残すと "Click to add title" が chrome に混ざる）。
    for shape in list(slide.shapes):
        if shape.is_placeholder:
            shape._element.getparent().remove(shape._element)

    # ★ マスタ側の装飾は使わない（`md2pptx.py` が生成スライドにも同じ指定を入れる）。
    slide._element.set("showMasterSp", "0")

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    _normalize_zip(out)


def _normalize_zip(path: pathlib.Path) -> None:
    """ZIP の日時を固定して再生成の差分を消す（★ `md2pptx.py` と同じ理由）。"""
    with zipfile.ZipFile(path) as z:
        items = [(n, z.read(n)) for n in z.namelist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            info = zipfile.ZipInfo(name, date_time=ZIP_TS)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, data)


def audit(path: pathlib.Path) -> list[str]:
    """⚠️★★★ 第三者の素材が 1 バイトも入っていないことを機械で確かめる。"""
    bad: list[str] = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        media = [n for n in names if "/media/" in n]
        if media:
            bad.append(f"画像パートが入っている: {media}")
        fonts = [n for n in names if "/fonts/" in n or n.endswith(".fntdata")]
        if fonts:
            bad.append(f"埋め込みフォントが入っている: {fonts}")
        blob = b"".join(z.read(n) for n in names if n.endswith((".xml", ".rels")))
        for token in ("松尾", "岩澤", "Matsuo", "Iwasawa", "UTokyo", "許諾", "アジェンダ", "Tahoma"):
            if token.encode("utf-8") in blob:
                bad.append(f"第三者由来の文字列が残っている: {token}")
    return bad


def main(argv: list[str]) -> int:
    build(OUT)
    bad = audit(OUT)
    for b in bad:
        print(f"[NG] {b}", file=sys.stderr)
    if bad:
        return 1
    print(f"[ok] {OUT.relative_to(REPO_ROOT).as_posix()}  ({OUT.stat().st_size:,} bytes)")
    print("     画像 0 / 埋め込みフォント 0 / 第三者由来の文字列 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
