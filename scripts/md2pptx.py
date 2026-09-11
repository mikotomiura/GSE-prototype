#!/usr/bin/env python3
"""Markdown -> .pptx（python-pptx で生成する）。

## ⚠️★★★ 2026-09-02: 手組み OOXML をやめた

初版は **標準ライブラリだけ**で `.pptx`（ZIP + XML）を組み立てていた。理由は
「本機に `pandoc` が無く（2026-08-30 実測）、`python-pptx` も入っていない（2026-09-01 実測）」。

★ **その前提は 2026-09-02 に変わった** —— `python -m pip install python-pptx` が通り、**1.0.2 が入った**。

⚠️ そして手組み版は **Google Slides で 2 回続けて開けなかった**:

| 試み | やったこと | 結果 |
|---|---|---|
| 1 回目 | 必須パートと XML の妥当性だけ検査して出力 | ⚠️ **開けない** |
| 2 回目 | 標準パート 5 本を追加し、slideMaster にプレースホルダを置いて継承チェーンを繋いだ | ⚠️ **同じエラーで開けない** |

→ ★★★ **手組みで「PowerPoint が出す形」を推定し続けるのをやめ、実績のあるライブラリに委ねる。**

## ★★★ 2026-09-04: テンプレート / 図 / スライド単位のレイアウトに対応した

⚠️★★★ **それまでの版は「テンプレートも図も扱えない」ため、設計スライドの指定を満たせなかった。**
★ 塞いだ穴は 5 つ（すべて 2026-09-04 に実測してから直した）:

| # | 旧版の穴 | 直し方 |
|---|---|---|
| 1 | `build()` が `Presentation()`（python-pptx 既定）で始まる | `--template <path>` を足し `Presentation(template)` にした |
| 2 | ⚠️ スライドサイズを `12192000 x 6858000`（13.33 x 7.5 inch）へ**無条件に代入** | ★ **テンプレート指定時は代入しない**（`deck_temp1.pptx` は 10.00 x 5.625） |
| 3 | テンプレート同梱の見本スライドが出力に残る | 生成前に全削除（`_drop_all_slides`） |
| 4 | `![alt](path)` を写せない（＝**図を置けない**） | `md2docx.py` の埋め込み規約を移植（repo 外は拒否） |
| 5 | 表を「行」として素朴に流す | `a:tbl` を実際に作る（`_render_table`） |

★ 併せて **旧版最大の実務上の穴**を塞いだ —— 旧 `build()` は `layout = _pick_layout(prs)` を
**ループの外で 1 回だけ**呼んでおり、⚠️ **全スライドが 1 種類のレイアウト**になっていた。
★ `deck_temp1.pptx` の「タイトルとコンテンツ」の本文枠は **9.01 x 1.60 inch**（版面の 3 割弱）の
**バナー型**で、⚠️ **図も密度のある技術説明も入らない**（2026-09-04 実測）。

→ ★ **本版はスライドごとに種別 (`kind`) を決め、種別ごとにレイアウトを選ぶ。**

## スライドの切り方（★ 規約・初版から不変）

- `---`（水平線）で **1 枚**に割る。★ これが唯一の区切りである。
- 各スライドの **最初の見出し行**（`#` 〜 `###`）がタイトルになる。無ければタイトル空欄。
- 残りが本文。`-` / `*` の箇条書きはビュレット、それ以外は段落として積む。

## スライド種別 (`kind`)

★ 明示指定は本文中の `<!-- layout: ... -->`（1 スライドに 1 個）。無ければ **自動**で決まる。

| kind | 使う版面 | 自動で選ばれる条件 |
|---|---|---|
| `title` | 表紙（中央寄せの大見出し＋副題） | ⚠️ 自動では選ばれない（**明示指定のみ**） |
| `content` | タイトル＋本文 1 枠（全幅） | 図が無い（既定） |
| `two` | タイトル＋左右 2 枠（★ **図を左・説明を右**） | 図と本文の両方がある |
| `figure` | タイトル＋本文枠いっぱいの図 | 図だけで本文が無い |

⚠️★★★ **本版は版面の座標を明示的に置く**（プレースホルダの継承座標を使わない）。
★ 理由は上記のとおり `deck_temp1.pptx` の継承座標が本文 1.60 inch のバナー型だからである。
★ 座標は**スライド寸法に対する比**で持つので、寸法の違うテンプレートでも崩れない。

## テンプレートの「地」の引き継ぎ（chrome）

★ `deck_temp1.pptx` は Google スライド書き出しで、**同梱スライドが装飾を各スライドに直接持つ**
（`showMasterSp="0"` でマスタ図形を隠し、全面 `#F4F4F4` の矩形＋左端の青いグラデーション帯を置く）。
→ ⚠️ **レイアウトを継承するだけでは、テンプレートの見た目にならない。**

★ 本版は **同梱スライドのうち図形数が最小のもの**（同数なら先頭）を「地」の見本とみなし、
**プレースホルダでなく・文字を持たない図形だけ**を全スライドへ複製する。
★ 画像を含む図形は関係 (`r:embed`) を張り直す（`_ChromeSpec`）。
`--chrome-from N`（1 始まり）で見本を明示指定できる。`--no-chrome` で複製しない。

## 使い方

    PYTHONUTF8=1 python scripts/md2pptx.py <in.md> <out.pptx> [--unescape] \
        [--template <deck.pptx>] [--chrome-from N] [--no-chrome]

⚠️ Windows コンソールは cp932 なので **`PYTHONUTF8=1`** を付ける。
⚠️ 出力パスに拡張子は**付かない**ので `.pptx` まで渡すこと。
★ `--unescape` は `md2docx.py` と同じ意味（`1\\.` のような backslash escape を外す）。

## 図

★ `![代替文字列](../figures/foo.png)` を**単独行**で書く。
⚠️ **PNG / JPEG のみ**（`python-pptx` が SVG を画像として認識しないため）。
★ repo では **SVG が正本・PNG が書き出し**なので、スライドからは `.png` を指す。
⚠️ **repo 外のパスは拒否する**（`md2docx.py` と同じ事故の経路を塞ぐ）。

## 検算

    PYTHONUTF8=1 python scripts/md2pptx.py --selftest

⚠️★★★ **「開けるか」は生成できたことと別である。** 本 selftest が見るのは
(1) ZIP (2) 必須パート (3) XML の parse (4) 枚数 (5) 関係の Target 実在
(6) content type の網羅 (7) **プレースホルダの継承チェーン** —— の 7 点であり、
★ **これが全部緑でも Google Slides で開けなかった実績がある**（上表）。
→ ⚠️ **表示は実機で確かめること。**

★ 2026-09-04 に **新機能の変異体検査**を足した（`md2docx.py --selftest` の作法に倣う）——
サイズ上書きの復活 / 見本スライドの残留 / 図の未埋め込み / 表の非テーブル化 /
レイアウト単一化 / repo 外画像の素通り、の **6 つを実際に作って落ちることを確認する**。
"""
from __future__ import annotations

import copy
import math
import pathlib
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
    from pptx.oxml.ns import qn
    from pptx.util import Emu, Pt
except ImportError:  # pragma: no cover - 環境依存
    # ★ `scripts/build_analysis_db.py` と同じ案内の形にそろえる（終了コード 5 も同じ）。
    print("[md2pptx] FAILED: python-pptx が入っていません。", file=sys.stderr)
    print("  run: pip install -r scripts/requirements-dev.txt", file=sys.stderr)
    raise SystemExit(5)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# ⚠️★★★ これは **テンプレートを渡さなかったときだけ**使う既定値である。
# ★ `--template` を渡したら **1 バイトも代入しない**（旧版はここで版面を壊していた）。
FALLBACK_EMU_W, FALLBACK_EMU_H = 12192000, 6858000  # 16:9

# ★ 固定タイムスタンプ（⚠️ now() にすると出力が毎回変わり、再生成の差分が読めなくなる）
FIXED_TS = __import__("datetime").datetime(2026, 1, 1, 0, 0, 0)

LATIN, EASTASIA, MONO = "Segoe UI", "Yu Gothic UI", "Consolas"

# 文字色（★ テンプレートの地が #F4F4F4 なので、地に埋もれない濃さを明示する）
INK_TITLE = RGBColor(0x11, 0x11, 0x11)
INK_BODY = RGBColor(0x22, 0x22, 0x22)
INK_ON_ACCENT = RGBColor(0xFF, 0xFF, 0xFF)
# `deck_temp1.pptx` のテーマ dk2。★ 見出し下の罫と表ヘッダに使う
ACCENT = RGBColor(0x15, 0x81, 0x58)
TABLE_BAND = RGBColor(0xEA, 0xEA, 0xEA)
TABLE_BASE = RGBColor(0xFF, 0xFF, 0xFF)

# --- インライン（md2docx.py と同じ順序規則）---------------------------------
# ⚠️ 順序が意味を持つ: `**太字**` と `` `コード` `` を先に食わせてから `*斜体*` を見る。
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\n]+?\*)")
IMAGE_LINE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LAYOUT_DIRECTIVE = re.compile(r"<!--\s*layout:\s*([a-z]+)\s*-->", re.I)
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|[\s:\-|]+\|\s*$")

KINDS = ("title", "content", "two", "figure")


def inline_parts(text: str) -> list[tuple[str, bool, bool, bool]]:
    """行を (テキスト, 太字, 斜体, 等幅) の並びへ割る。"""
    out: list[tuple[str, bool, bool, bool]] = []
    for part in INLINE.split(text):
        if not part:
            continue
        b = i = mono = False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            b, part = True, part[2:-2]
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            mono, part = True, part[1:-1]
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            i, part = True, part[1:-1]
        out.append((part, b, i, mono))
    return out or [("", False, False, False)]


def plain(text: str) -> str:
    """装飾記法を外した素の文字列（★ 幅の見積りに使う）。"""
    return "".join(t for t, _, _, _ in inline_parts(text))


# --- 解析 --------------------------------------------------------------------


class SlideSpec:
    """1 枚ぶんの中身。`blocks` は ('text', 行, ビュレットか) / ('image', alt, パス)
    / ('table', 行の並び) のいずれか。"""

    __slots__ = ("title", "kind", "blocks")

    def __init__(self, title: str, kind: str | None, blocks: list) -> None:
        self.title, self.kind, self.blocks = title, kind, blocks

    @property
    def images(self) -> list:
        imgs = [b for b in self.blocks if b[0] == "image"]
        if len(imgs) > 1:
            # ⚠️ 旧版は 2 枚目以降を `[:1]` で**無言で捨てていた**（code-reviewer 指摘）。
            # ★ 1 スライド 1 図が規約なので、黙って消さず明示的に落とす。
            raise SystemExit(
                f"[NG] 1 スライドに図は 1 枚まで: {self.title!r} に {len(imgs)} 枚ある"
                " / ★ スライドを分けること"
            )
        return imgs

    @property
    def non_images(self) -> list:
        return [b for b in self.blocks if b[0] != "image"]

    def resolved_kind(self) -> str:
        """明示指定 > 自動判定。★ 自動規則は docstring の表と 1 対 1。"""
        if self.kind:
            return self.kind
        if self.images:
            return "two" if self.non_images else "figure"
        return "content"


def split_slides(md: str, unescape: bool) -> list[SlideSpec]:
    """`---` で割り、SlideSpec の並びを返す。"""
    if unescape:
        md = re.sub(r"\\([.\-_*#>`\[\]()])", r"\1", md)
    chunks = re.split(r"^\s*---\s*$", md, flags=re.M)
    slides: list[SlideSpec] = []
    for ch in chunks:
        title, kind = "", None
        blocks: list = []
        lines = ch.split("\n")
        in_code = False
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            s = line.strip()

            if s.startswith("```"):
                in_code = not in_code
                i += 1
                continue

            m_dir = LAYOUT_DIRECTIVE.search(s)
            if m_dir and not in_code:
                want = m_dir.group(1).lower()
                if want not in KINDS:
                    raise SystemExit(
                        f"[NG] 未知の layout 指定: {want!r} / 使えるのは {', '.join(KINDS)}"
                    )
                kind = want
                i += 1
                continue

            if not s:
                i += 1
                continue

            if not in_code and TABLE_ROW.match(s):
                rows: list[list[str]] = []
                while i < len(lines) and TABLE_ROW.match(lines[i].strip()):
                    row = lines[i].strip()
                    if not TABLE_SEP.match(row):
                        rows.append([c.strip() for c in row.strip().strip("|").split("|")])
                    i += 1
                if rows:
                    blocks.append(("table", rows))
                continue

            m = re.match(r"^(#{1,6})\s+(.*)", s)
            if m and not in_code:
                t = m.group(2).replace("**", "").strip()
                if not title:
                    title = t
                else:
                    blocks.append(("text", t, False, 0))
                i += 1
                continue

            if not in_code:
                m_img = IMAGE_LINE.fullmatch(s)
                if m_img:
                    blocks.append(("image", m_img.group(1), m_img.group(2)))
                    i += 1
                    continue

            if s.startswith(">"):
                s = s[1:].strip()
                if not s:
                    i += 1
                    continue

            mb = re.match(r"^(\s*)[-*]\s+(.*)", line)
            if mb and not in_code:
                # ★ 字下げ 2 つで 1 段。⚠️ 拾わないと入れ子が黙って平らになる（2026-09-04 実機で確認）
                blocks.append(("text", mb.group(2).strip(), True, min(len(mb.group(1)) // 2, 4)))
            else:
                blocks.append(("text", s, False, 0))
            i += 1

        if title or blocks:
            slides.append(SlideSpec(title, kind, blocks))
    return slides


# --- 画像 --------------------------------------------------------------------


def image_pixels(path: pathlib.Path) -> tuple[int, int]:
    """PNG / JPEG の画素寸法。★ 縦横比だけに使う。"""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:2] == b"\xff\xd8":  # JPEG
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h = int.from_bytes(data[i + 5 : i + 7], "big")
                w = int.from_bytes(data[i + 7 : i + 9], "big")
                return w, h
            i += 2 + int.from_bytes(data[i + 2 : i + 4], "big")
    raise SystemExit(f"[NG] 画素寸法を読めない画像: {path}")


def resolve_image(target: str, base_dir: pathlib.Path, root: pathlib.Path) -> pathlib.Path:
    """★ `md2docx.py` と同じ規約: 相対解決 / 実在確認 / **repo 外は拒否** / 形式の限定。"""
    # ⚠️★★★ **両側を resolve してから比べる。** ★ 画像側だけ `.resolve()` して
    #   未解決の `root` と `relative_to` すると、**repo 内の画像を「repo 外」と誤判定**する。
    #   ⚠️ macOS の `tempfile` は `/var/folders/...` (= `/private/var/...` への symlink) を
    #   返すため、selftest が macOS で必ず落ちていた (2026-09-11 に実測。
    #   ★ `render_slide()` は `build()` を経由せず呼ばれる経路があるので、
    #   正規化は**呼び出し側ではなくこの関門**に置く)。
    root = pathlib.Path(root).resolve()
    path = (base_dir / target).resolve()
    if not path.is_file():
        raise SystemExit(f"[NG] 画像が見つからない: {path}")
    try:
        path.relative_to(root)
    except ValueError:
        # ⚠️★★★ 悪意ある入力者は居ないが、**事故の経路は実在する** ——
        # `![](C:/Users/.../screenshot.png)` と 1 行貼るだけで提出物に混入する。
        raise SystemExit(
            f"[NG] repo 外の画像は埋め込まない: {path}"
            " / ★ 図は repo 内（例: docs/mitou_submission/figures/）へ置くこと"
        )
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        # ⚠️ python-pptx は SVG を画像として認識しない。★ repo の正本は SVG だが、
        #   スライドからは **書き出した .png** を指すこと。
        raise SystemExit(
            f"[NG] pptx に置けるのは PNG / JPEG のみ: {path}"
            " / ★ SVG は .png へ書き出してから参照する"
        )
    return path


# --- 版面（★ スライド寸法に対する比で持つ）-----------------------------------


class Geometry:
    """版面の矩形を EMU で返す。★ 比で持つので寸法の違うテンプレートでも崩れない。"""

    def __init__(self, width: int, height: int) -> None:
        w, h = width, height
        self.width, self.height = w, h
        self.title = (int(0.042 * w), int(0.048 * h), int(0.916 * w), int(0.115 * h))
        self.rule = (int(0.042 * w), int(0.176 * h), int(0.110 * w), int(0.006 * h))
        self.body = (int(0.050 * w), int(0.205 * h), int(0.900 * w), int(0.715 * h))
        self.left = (int(0.050 * w), int(0.205 * h), int(0.435 * w), int(0.715 * h))
        self.right = (int(0.515 * w), int(0.205 * h), int(0.435 * w), int(0.715 * h))
        self.cover_title = (int(0.080 * w), int(0.300 * h), int(0.840 * w), int(0.170 * h))
        self.cover_body = (int(0.080 * w), int(0.500 * h), int(0.840 * w), int(0.260 * h))


EMU_PER_INCH = 914400


def _wide(ch: str) -> bool:
    return unicodedata.east_asian_width(ch) in ("W", "F", "A")


def text_units(s: str) -> float:
    """全角 1.0 / 半角 0.55 で数えた「em 単位の行幅」。"""
    return sum(1.0 if _wide(c) else 0.55 for c in s)


def fit_pt(lines: list[tuple[str, bool, int]], box: tuple[int, int, int, int],
           candidates=(20, 18, 16, 14, 13, 12, 11, 10, 9, 8)) -> int:
    """枠に収まる最大のポイント数を返す（★ 文字数の閾値ではなく**実際に行数を積む**）。

    ⚠️ 組版そのものではない（PowerPoint の行分割規則までは真似ない）。
    ★ しかし旧版の「300 字 / 700 字」という枠幅を無視した閾値よりは遥かに近い。
    """
    box_w = box[2] / EMU_PER_INCH
    box_h = box[3] / EMU_PER_INCH
    for sz in candidates:
        em = sz / 72.0
        cols = max(1.0, box_w / em)
        line_h = 1.30 * em
        total = 0.0
        for text, is_bullet, level in lines:
            units = text_units(text) + (1.6 if is_bullet else 0.0) + 2.0 * level
            total += max(1, math.ceil(units / cols)) * line_h + 0.32 * em
        if total <= box_h:
            return sz
    return candidates[-1]


# --- python-pptx の薄い補助 --------------------------------------------------
# ⚠️ python-pptx はビュレットの on/off と東アジアフォントを公開 API で出さないので、
# ★ ここだけ oxml へ降りる。


def _fonts(run, mono: bool) -> None:
    """`a:latin` / `a:ea` を明示する（★ 日本語がフォールバックで崩れないように）。"""
    rPr = run._r.get_or_add_rPr()
    for tag, face in ((qn("a:latin"), MONO if mono else LATIN), (qn("a:ea"), EASTASIA)):
        el = rPr.find(tag)
        if el is None:
            el = rPr.makeelement(tag, {})
            rPr.append(el)
        el.set("typeface", face)


def _bullet(par, on: bool, level: int = 0) -> None:
    """段落のビュレットを明示的に付ける / 外す。`level` は入れ子の段（0 が最上位）。"""
    pPr = par._p.get_or_add_pPr()
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    if on:
        step = 228600
        pPr.set("marL", str(step * (level + 1)))
        pPr.set("indent", str(-step))
        pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"}))
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "\u2022"}))
    else:
        pPr.set("marL", str(228600 * level))
        pPr.set("indent", "0")
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))


def _write_runs(par, text: str, sz: int, color, bold_all: bool = False) -> None:
    for txt, b, i, mono in inline_parts(text):
        r = par.add_run()
        r.text = txt
        r.font.bold = True if (b or bold_all) else None
        r.font.italic = True if i else None
        r.font.size = Pt(sz)
        r.font.color.rgb = color
        _fonts(r, mono)


def _fill_text(tf, lines: list[tuple[str, bool, int]], sz: int, color) -> None:
    tf.word_wrap = True
    first = True
    for text, is_bullet, level in lines:
        par = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        _bullet(par, is_bullet, level)
        par.space_after = Pt(sz * 0.32)
        _write_runs(par, text, sz, color)


def _place(shape, box: tuple[int, int, int, int]) -> None:
    shape.left, shape.top, shape.width, shape.height = (Emu(v) for v in box)


def _drop(shape) -> None:
    shape._element.getparent().remove(shape._element)


# --- テンプレートの「地」（chrome）-------------------------------------------

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_R_ATTRS = (f"{{{R_NS}}}embed", f"{{{R_NS}}}link", f"{{{R_NS}}}id")


class _ChromeSpec:
    """同梱スライドから取り出した「装飾だけ」の図形と、その画像パート。

    ★ スライド削除の**前**に採取し、参照先パートを実体で握っておく
    （⚠️ 削除後に rId を引こうとしても解決できないため）。
    """

    __slots__ = ("elements", "parts", "source_index")

    def __init__(self, elements, parts, source_index) -> None:
        self.elements, self.parts, self.source_index = elements, parts, source_index

    def __len__(self) -> int:
        return len(self.elements)

    @property
    def image_count(self) -> int:
        """採取した装飾が抱えている画像パートの数（★ selftest が張り替えを検査するため）。"""
        return sum(1 for reltype, _ in self.parts.values() if reltype.endswith("/image"))


def capture_chrome(prs, index: int | None = None) -> _ChromeSpec | None:
    """★ 見本にするスライドを 1 枚選び、装飾図形を採取する。

    既定の選び方: **図形数が最小のスライド**（同数なら先頭）。
    ⚠️ 表紙のような装飾の多いスライドを選ぶと、全ページにその装飾が乗ってしまう。
    ★ 「装飾」の定義: プレースホルダでなく、かつ**文字を持たない**図形。
    """
    slides = list(prs.slides)
    if not slides:
        return None
    if index is None:
        index = min(range(len(slides)), key=lambda i: (len(slides[i].shapes), i))
    if not 0 <= index < len(slides):
        raise SystemExit(f"[NG] --chrome-from が範囲外: {index + 1} / 同梱 {len(slides)} 枚")
    src = slides[index]
    elements, parts = [], {}
    for sh in src.shapes:
        if sh.is_placeholder:
            continue
        if sh.has_text_frame and sh.text_frame.text.strip():
            continue
        el = copy.deepcopy(sh._element)
        for node in el.iter():
            for attr in _R_ATTRS:
                rid = node.get(attr)
                if rid and rid not in parts:
                    rel = src.part.rels[rid]
                    # ⚠️ 外部関係（ハイパーリンク等）は `related_part` が例外を投げる。
                    # ★ 張り替えも不要なので採取対象から外す（code-reviewer 指摘・2026-09-04）。
                    if getattr(rel, "is_external", False):
                        continue
                    parts[rid] = (rel.reltype, src.part.related_part(rid))
        elements.append(el)
    return _ChromeSpec(elements, parts, index)


def apply_chrome(slide, chrome: _ChromeSpec) -> None:
    """装飾図形を「最背面」へ複製する（★ 本文より後ろに来ないと文字が隠れる）。"""
    sp_tree = slide.shapes._spTree
    # spTree の先頭 2 要素は nvGrpSpPr / grpSpPr。★ その直後＝最背面。
    for offset, el in enumerate(chrome.elements):
        new_el = copy.deepcopy(el)
        for node in new_el.iter():
            for attr in _R_ATTRS:
                rid = node.get(attr)
                if rid and rid in chrome.parts:
                    reltype, part = chrome.parts[rid]
                    node.set(attr, slide.part.relate_to(part, reltype))
        sp_tree.insert(2 + offset, new_el)
    # ⚠️ テンプレート同梱スライドは `showMasterSp="0"`（マスタ図形を隠す）。
    # ★ 揃えないと、複製した「地」の上にマスタの装飾が二重に出る。
    slide._element.set("showMasterSp", "0")


# --- レイアウト選択 ----------------------------------------------------------

# ★ kind -> (優先する名前, 必要なプレースホルダ idx)
LAYOUT_WANT = {
    "title": (("タイトル スライド", "タイトルスライド", "Title Slide"), {0, 1}),
    "content": (("タイトルとコンテンツ", "Title and Content"), {0, 1}),
    "figure": (("タイトルとコンテンツ", "Title and Content"), {0, 1}),
    "two": (("2 つのコンテンツ", "2つのコンテンツ", "Two Content"), {0, 1, 2}),
}


def pick_layout(prs, kind: str):
    """種別に合うレイアウトを返す。

    ★ **どの経路で返しても、必要なプレースホルダ idx を満たす**ことを保証する。
    ⚠️★★★ 2026-09-02 の `/cross-review` 指摘で書き直した経緯（旧 `_pick_layout`）:
    (a) `or True` で分岐が死んでいた、(b) `13` は `TITLE` ではなく `SLIDE_NUMBER`、
    (c) 最終フォールバックが不変条件を検査せずに返していた。→ 明示的に失敗させる。
    """
    names, need = LAYOUT_WANT[kind]
    qualified = [
        lay for lay in prs.slide_layouts
        if need <= {ph.element.ph_idx for ph in lay.placeholders}
    ]
    for lay in qualified:
        if lay.name in names:
            return lay
    if qualified:
        return qualified[0]
    if kind == "two":
        # ⚠️ 2 枠レイアウトが無いテンプレートもある。★ 静かに壊さず 1 枠へ落とす。
        return pick_layout(prs, "content")
    raise SystemExit(
        f"[NG] kind={kind} に必要なプレースホルダ {sorted(need)} を持つレイアウトがテンプレートに無い"
    )


# --- 描画 --------------------------------------------------------------------


def _title_and_rule(slide, spec: SlideSpec, geo: Geometry, cover: bool) -> None:
    box = geo.cover_title if cover else geo.title
    ph = slide.shapes.title
    _place(ph, box)
    tf = ph.text_frame
    tf.word_wrap = True
    tf.text = ""
    sz = 30 if cover else fit_pt([(plain(spec.title), False, 0)], box, candidates=(22, 20, 18, 16, 14))
    par = tf.paragraphs[0]
    # ⚠️ テンプレートによって見出しが中央寄せになる（★ python-pptx 既定のマスタで実測）。
    # ★ 版面をこちらで決めている以上、揃えも明示しないとテンプレート差で崩れる。
    par.alignment = PP_ALIGN.LEFT
    _write_runs(par, spec.title, sz, INK_TITLE, bold_all=True)
    if not cover and spec.title:
        # ★ 見出し下の短い罫（テンプレート左端の帯と同じ dk2）。版面の骨を 1 本だけ立てる。
        rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, *(Emu(v) for v in geo.rule))
        rule.fill.solid()
        rule.fill.fore_color.rgb = ACCENT
        rule.line.fill.background()
        rule.shadow.inherit = False


def _column_widths(rows: list[list[str]], n_cols: int, total: int) -> list[int]:
    """列幅を中身の量で比例配分する。

    ⚠️★★★ 均等割りだと「記号」1 文字の列と説明文の列が同じ幅になり、
    ★ 版面の半分が空白のまま説明文だけが折り返す（2026-09-04 に実機で確認）。
    ★ 下限を置くのは、比例だけだと 1 文字の列が潰れて読めなくなるため。
    """
    want = []
    for c in range(n_cols):
        longest = max((text_units(plain(r[c])) for r in rows if c < len(r)), default=1.0)
        want.append(max(longest, 1.0))
    floor = total * 0.10
    widths = [max(floor, total * w / sum(want)) for w in want]
    scale = total / sum(widths)
    widths = [int(w * scale) for w in widths]
    widths[-1] += total - sum(widths)  # 丸め残りを最後の列へ
    return widths


def _table_pt(rows: list[list[str]], widths: list[int], row_h: int) -> int:
    """全セルがそれぞれの列幅と行高に収まる、最大のポイント数。"""
    row_in = row_h / EMU_PER_INCH
    for sz in (14, 13, 12, 11, 10, 9, 8):
        em = sz / 72.0
        ok = True
        for row in rows:
            for ci, text in enumerate(row):
                if ci >= len(widths):
                    continue
                cols = max(1.0, (widths[ci] / EMU_PER_INCH - 0.12) / em)
                lines = max(1, math.ceil(text_units(plain(text)) / cols))
                if lines * 1.28 * em + 0.06 > row_in:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return sz
    return 8


def _render_table(slide, rows: list[list[str]], box: tuple[int, int, int, int]) -> None:
    """markdown の表を **本物の `a:tbl`** にする（★ 旧版は行として流していた）。"""
    n_rows, n_cols = len(rows), max(len(r) for r in rows)
    frame = slide.shapes.add_table(n_rows, n_cols, *(Emu(v) for v in box))
    table = frame.table
    table.first_row = True
    table.horz_banding = False
    widths = _column_widths(rows, n_cols, box[2])
    for ci, c in enumerate(table.columns):
        c.width = Emu(widths[ci])
    row_h = box[3] // n_rows
    sz = _table_pt(rows, widths, row_h)
    for ri, row in enumerate(rows):
        table.rows[ri].height = Emu(row_h)
        for ci in range(n_cols):
            cell = table.cell(ri, ci)
            cell.margin_left = cell.margin_right = Emu(45720)
            cell.margin_top = cell.margin_bottom = Emu(18288)
            cell.fill.solid()
            head = ri == 0
            cell.fill.fore_color.rgb = (
                ACCENT if head else (TABLE_BAND if ri % 2 == 0 else TABLE_BASE)
            )
            tf = cell.text_frame
            tf.word_wrap = True
            tf.text = ""
            par = tf.paragraphs[0]
            _bullet(par, False)
            text = row[ci] if ci < len(row) else ""
            _write_runs(par, text, sz, INK_ON_ACCENT if head else INK_BODY, bold_all=head)


def _render_image(slide, path: pathlib.Path, box: tuple[int, int, int, int], alt: str = ""):
    """縦横比を保って枠へ収め、中央に置く。★ 代替文字列も載せる。"""
    px_w, px_h = image_pixels(path)
    scale = min(box[2] / px_w, box[3] / px_h)
    w, h = int(px_w * scale), int(px_h * scale)
    left = box[0] + (box[2] - w) // 2
    top = box[1] + (box[3] - h) // 2
    pic = slide.shapes.add_picture(str(path), Emu(left), Emu(top), Emu(w), Emu(h))
    # ★ `md2docx.py:109` が `docPr descr` に代替文字列を書いているのに合わせる。
    pic._element._nvXxPr.cNvPr.set("descr", alt or "GSE figure")
    return pic


def _text_lines(blocks) -> list[tuple[str, bool, int]]:
    return [(b[1], b[2], b[3] if len(b) > 3 else 0) for b in blocks if b[0] == "text"]


def _render_blocks(slide, ph, blocks, box: tuple[int, int, int, int],
                   base_dir: pathlib.Path, root: pathlib.Path) -> None:
    """1 つの枠に text / table を積む。★ 表がある枠は上下に割る。"""
    tables = [b for b in blocks if b[0] == "table"]
    lines = _text_lines(blocks)
    if not tables:
        _place(ph, box)
        _fill_text(ph.text_frame, lines, fit_pt(lines, box), INK_BODY)
        return
    # ★ 表があるときは「本文 -> 表」の順に積む（markdown 上の順序は保たない —— 版面が壊れるため）。
    n_tab_rows = sum(len(t[1]) for t in tables)
    text_share = 0.0 if not lines else min(0.55, 0.10 + 0.05 * len(lines))
    if n_tab_rows and lines:
        text_h = int(box[3] * text_share)
    elif lines:
        text_h = box[3]
    else:
        text_h = 0
    cursor = box[1]
    if lines:
        tbox = (box[0], cursor, box[2], text_h)
        _place(ph, tbox)
        _fill_text(ph.text_frame, lines, fit_pt(lines, tbox), INK_BODY)
        cursor += text_h + int(0.02 * box[3])
    else:
        _drop(ph)
    remain = box[1] + box[3] - cursor
    for t in tables:
        share = len(t[1]) / n_tab_rows
        h = int(remain * share)
        _render_table(slide, t[1], (box[0], cursor, box[2], h))
        cursor += h


def render_slide(prs, spec: SlideSpec, geo: Geometry, chrome: _ChromeSpec | None,
                 base_dir: pathlib.Path, root: pathlib.Path):
    kind = spec.resolved_kind()
    slide = prs.slides.add_slide(pick_layout(prs, kind))
    if chrome:
        apply_chrome(slide, chrome)

    _title_and_rule(slide, spec, geo, cover=(kind == "title"))

    body = slide.placeholders[1]
    second = slide.placeholders[2] if 2 in {p.element.ph_idx for p in slide.placeholders} else None

    if kind == "title":
        _place(body, geo.cover_body)
        lines = _text_lines(spec.blocks)
        _fill_text(body.text_frame, lines, fit_pt(lines, geo.cover_body, (18, 16, 14, 12)), INK_BODY)
        if second is not None:
            _drop(second)
        return slide

    if kind == "figure":
        _drop(body)
        if second is not None:
            _drop(second)
        for _, alt, target in spec.images:
            _render_image(slide, resolve_image(target, base_dir, root), geo.body, alt)
        return slide

    if kind == "two":
        if second is None:
            # ⚠️ 2 枠レイアウトが取れなかったときの縮退。★ 図は上、本文は下。
            top = (geo.body[0], geo.body[1], geo.body[2], int(geo.body[3] * 0.55))
            bottom = (geo.body[0], geo.body[1] + top[3], geo.body[2], geo.body[3] - top[3])
            for _, alt, target in spec.images:
                _render_image(slide, resolve_image(target, base_dir, root), top, alt)
            _render_blocks(slide, body, spec.non_images, bottom, base_dir, root)
            return slide
        imgs = spec.images
        if imgs:
            _drop(body)
            for _, alt, target in imgs:
                _render_image(slide, resolve_image(target, base_dir, root), geo.left, alt)
            _render_blocks(slide, second, spec.non_images, geo.right, base_dir, root)
        else:
            # ★ 図が無い `two` は本文を左右へ半分ずつ割る。
            rest = spec.non_images
            half = (len(rest) + 1) // 2
            _render_blocks(slide, body, rest[:half], geo.left, base_dir, root)
            _render_blocks(slide, second, rest[half:], geo.right, base_dir, root)
        return slide

    # kind == "content"
    if second is not None:
        _drop(second)
    _render_blocks(slide, body, spec.non_images, geo.body, base_dir, root)
    for _, alt, target in spec.images:
        _render_image(slide, resolve_image(target, base_dir, root), geo.body, alt)
    return slide


# --- 組み立て ----------------------------------------------------------------


def _drop_all_slides(prs) -> int:
    """テンプレート同梱のスライドを全部消す。

    ⚠️ python-pptx に公式 API が無い。★ `drop_rel` を省くと**関係だけが残る**ので必ず対で呼ぶ。
    """
    lst = prs.slides._sldIdLst
    removed = 0
    for sld in list(lst):
        prs.part.drop_rel(sld.rId)
        lst.remove(sld)
        removed += 1
    return removed


def _inherited_media(out: pathlib.Path, base_dir: pathlib.Path, root: pathlib.Path,
                     slides: list[SlideSpec]) -> list[str]:
    """出力に残った「テンプレート由来の画像」を列挙する。

    ⚠️★★★ 2026-09-04 に **実害**が出たので足した（Codex の指摘・security-checker の指摘）。
    ★ `capture_chrome()` は装飾を複製するとき画像も連れてくるし、
      **マスタやレイアウトが参照する画像は、同梱スライドを全部消しても出力に残る**。
    ⚠️ 実際、研究者指定のテンプレートに第三者研究室のロゴが入っており、
      **画面に出ないまま提出物へ同梱される**ところだった。
    → ★ 黙って運ばない。**何を引き継いだかを必ず表に出す。**
    """
    try:
        ours = set()
        for spec in slides:
            for _, _alt, target in spec.images:
                ours.add(resolve_image(target, base_dir, root).stat().st_size)
        with zipfile.ZipFile(out) as z:
            return sorted(
                n for n in z.namelist()
                if "/media/" in n and z.getinfo(n).file_size not in ours
            )
    except Exception:  # pragma: no cover - 監査は本処理を落とさない
        return []


def build(slides: list[SlideSpec], out: pathlib.Path, template: pathlib.Path | None = None,
          base_dir: pathlib.Path | None = None, root: pathlib.Path | None = None,
          chrome_from: int | None = None, use_chrome: bool = True) -> dict:
    base_dir = base_dir or out.parent
    root = root or REPO_ROOT

    if template is not None:
        prs = Presentation(str(template))
        # ⚠️★★★ ここで slide_width / slide_height を **代入しない**。
        # ★ 旧版はテンプレートの版面（10.00 x 5.625）を 13.33 x 7.5 で潰していた。
        chrome = capture_chrome(prs, chrome_from) if use_chrome else None
        dropped = _drop_all_slides(prs)
    else:
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(FALLBACK_EMU_W), Emu(FALLBACK_EMU_H)
        chrome, dropped = None, 0

    cp = prs.core_properties
    cp.author, cp.last_modified_by, cp.title = "GSE", "GSE", ""
    cp.created, cp.modified, cp.revision = FIXED_TS, FIXED_TS, 1

    geo = Geometry(prs.slide_width, prs.slide_height)
    kinds: list[str] = []
    for spec in slides:
        render_slide(prs, spec, geo, chrome, base_dir, root)
        kinds.append(spec.resolved_kind())

    prs.save(str(out))
    _ensure_app_xml(out, len(slides))
    _normalize_zip(out)
    inherited = _inherited_media(out, base_dir, root, slides)
    return {
        "inherited_media": inherited,
        "dropped": dropped,
        "chrome": 0 if chrome is None else len(chrome),
        "chrome_images": 0 if chrome is None else chrome.image_count,
        "chrome_from": None if chrome is None else chrome.source_index + 1,
        "kinds": kinds,
        "size": (prs.slide_width, prs.slide_height),
    }


ZIP_TS = (2026, 1, 1, 0, 0, 0)

APP_CT = "application/vnd.openxmlformats-officedocument.extended-properties+xml"
APP_RT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
APP_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"'
    ' xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    "<Application>GSE md2pptx</Application><PresentationFormat>Custom</PresentationFormat>"
    "<Slides>{n}</Slides><ScaleCrop>false</ScaleCrop><LinksUpToDate>false</LinksUpToDate>"
    "<SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged>"
    "<AppVersion>16.0000</AppVersion></Properties>"
)


def _ensure_app_xml(path: pathlib.Path, n_slides: int) -> bool:
    """`docProps/app.xml` が無ければ足す（★ content type と関係も対で足す）。

    ⚠️★★★ 2026-09-04 実測: **`deck_temp1.pptx` には `docProps/app.xml` が無い。**
    ★ Google スライドの書き出しが出力しないためで、**壊れているわけではない**
    （同ファイルは PowerPoint でも Google スライドでも開く）。
    → ⚠️ しかし `python-pptx` はテンプレートのパート構成をそのまま引き継ぐので、
      **テンプレート経由の出力にも app.xml が無くなる**。
    ★ 必須パート検査を緩めるのではなく、**出力側を標準形に揃える**ことで塞ぐ
      （検査を弱めると、テンプレート無しの経路で本当に欠落したときに気づけなくなる）。
    """
    with zipfile.ZipFile(path) as z:
        items = [(n, z.read(n)) for n in z.namelist()]
    if any(n == "docProps/app.xml" for n, _ in items):
        # ⚠️ 既にある場合、テンプレート由来の `<Slides>` が**古い枚数のまま残る**
        #   （Codex の指摘・2026-09-04）。★ 中身は引き継ぎつつ枚数だけ実際の値へ直す。
        out = []
        for name, data in items:
            if name == "docProps/app.xml":
                data = re.sub(rb"<Slides>\d+</Slides>",
                              f"<Slides>{n_slides}</Slides>".encode("utf-8"), data)
            out.append((name, data))
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in out:
                z.writestr(name, data)
        return False

    out: list[tuple[str, bytes]] = []
    for name, data in items:
        if name == "[Content_Types].xml":
            text = data.decode("utf-8")
            # ⚠️ パートが無くても**宣言だけ残っている**ことがある。★ 二重に足すと OPC 違反になる。
            if "docProps/app.xml" not in text:
                text = text.replace(
                    "</Types>",
                    f'<Override ContentType="{APP_CT}" PartName="/docProps/app.xml"/></Types>',
                )
            data = text.encode("utf-8")
        elif name == "_rels/.rels":
            text = data.decode("utf-8")
            if "docProps/app.xml" in text:
                out.append((name, data))
                continue
            used = set(re.findall(r'Id="(rId\d+)"', text))
            rid = next(f"rId{i}" for i in range(1, 1000) if f"rId{i}" not in used)
            text = text.replace(
                "</Relationships>",
                f'<Relationship Id="{rid}" Type="{APP_RT}" Target="docProps/app.xml"/>'
                "</Relationships>",
            )
            data = text.encode("utf-8")
        out.append((name, data))
    out.append(("docProps/app.xml", APP_XML.format(n=n_slides).encode("utf-8")))

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in out:
            z.writestr(name, data)
    return True


def _normalize_zip(path: pathlib.Path) -> None:
    """ZIP エントリの日時を固定して、出力を再現可能にする。

    ⚠️★★★ 2026-09-02: `python-pptx` の保存は各エントリに **実行時刻**を書くため、
    内容が 1 バイトも変わっていなくても再生成のたびにバイナリが変わり、
    `git status` に常に差分が出る（★ 実測）。→ ★ 順序と内容はそのままに、日時だけ揃える。
    """
    with zipfile.ZipFile(path) as z:
        items = [(n, z.read(n)) for n in z.namelist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            info = zipfile.ZipInfo(name, date_time=ZIP_TS)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, data)


# --- 検算 --------------------------------------------------------------------

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
# ★ 検査 (8) 用。`R_NS` は python-pptx を使う側の定数なので、検算側は別名で持つ。
R_NS_V = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

REQUIRED = [
    "[Content_Types].xml",
    "_rels/.rels",
    "ppt/presentation.xml",
    "ppt/_rels/presentation.xml.rels",
    # ⚠️★★★ 無くても PowerPoint は開くが、Google Slides で落ちた形（2026-09-02）
    "ppt/presProps.xml",
    "docProps/core.xml",
    "docProps/app.xml",
]


def _flat(base: str, target: str) -> str:
    parts: list[str] = []
    for seg in pathlib.PurePosixPath(base + target).parts:
        if seg == "..":
            if parts:
                parts.pop()
        elif seg != ".":
            parts.append(seg)
    return "/".join(parts)


def _rels_of(z, part: str) -> dict[str, str]:
    """パートの .rels を {Id: 解決済みパス} で返す。"""
    d, base = {}, part.rsplit("/", 1)
    rels = f"{base[0]}/_rels/{base[1]}.rels"
    if rels not in z.namelist():
        return d
    for rel in ET.fromstring(z.read(rels)).iter(f"{{{REL_NS}}}Relationship"):
        if rel.get("TargetMode") == "External":
            continue
        d[rel.get("Id")] = _flat(base[0] + "/", rel.get("Target", ""))
    return d


def _phs(z, part: str) -> set[str]:
    """そのパートが宣言しているプレースホルダの集合を `type:idx` で返す。"""
    return {
        f'{ph.get("type", "body")}:{ph.get("idx", "0")}'
        for ph in ET.fromstring(z.read(part)).iter(f"{{{P_NS}}}ph")
    }


# ⚠️★★★ layout の ph type は master の ph type と 1 対 1 ではない。
# ★ 表紙レイアウトの `ctrTitle` / `subTitle` は master の `title` / `body` を継承するのが**正常**であり
# （PowerPoint 既定テンプレートで実測・2026-09-04）、素朴に type 名で照合すると **偽陽性が出る**。
# ⚠️ 旧版でこれが露見しなかったのは、**全スライドが「タイトルとコンテンツ」1 種類だけ**を使っており
# 表紙レイアウトを 1 度も参照しなかったからである（★ 検査が空回りしていたのではなく、経路が無かった）。
PH_TYPE_BASE = {
    "ctrTitle": "title",
    "subTitle": "body",
    "obj": "body",
    "tbl": "body",
    "chart": "body",
    "clipArt": "body",
    "dgm": "body",
    "media": "body",
    "pic": "body",
}


def _base_type(t: str) -> str:
    return PH_TYPE_BASE.get(t, t)


def verify(path: pathlib.Path, expect_slides: int) -> list[str]:
    """⚠️ 「生成できた」と「開ける」は別。

    ★ 2026-09-02 に (5)(6)(7) を足した —— **Google Slides で開けなかった実物を、
    それまでの (1)〜(4) が全部素通りさせていた**ため（★ 検査が空回りしていた実例）。
    """
    bad: list[str] = []
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            for r in REQUIRED:
                if r not in names:
                    bad.append(f"必須パート欠落: {r}")
            got = sum(1 for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
            if got != expect_slides:
                bad.append(f"スライド数が不一致: {got} != {expect_slides}")
            for n in sorted(names):
                if n.endswith(".xml") or n.endswith(".rels"):
                    try:
                        ET.fromstring(z.read(n))
                    except ET.ParseError as e:
                        bad.append(f"XML が壊れている: {n} ({e})")
            if bad:
                return bad

            # (5) 関係の Target が実在するか
            for n in sorted(x for x in names if x.endswith(".rels")):
                base = n.rsplit("_rels/", 1)[0]
                for rel in ET.fromstring(z.read(n)).iter(f"{{{REL_NS}}}Relationship"):
                    if rel.get("TargetMode") == "External":
                        continue
                    tgt = rel.get("Target", "")
                    if _flat(base, tgt) not in names:
                        bad.append(f"関係の Target が実在しない: {n} -> {tgt}")

            # (6) 全パートに content type が付いているか
            ct = ET.fromstring(z.read("[Content_Types].xml"))
            defaults = {d.get("Extension", "").lower() for d in ct.iter(f"{{{CT_NS}}}Default")}
            overrides = {o.get("PartName", "").lstrip("/") for o in ct.iter(f"{{{CT_NS}}}Override")}
            for n in sorted(names):
                if n == "[Content_Types].xml":
                    continue
                ext = n.rsplit(".", 1)[-1].lower() if "." in n else ""
                if n not in overrides and ext not in defaults:
                    bad.append(f"content type が無いパート: {n}")

            # (7) ★★★ プレースホルダの継承チェーン（slide -> layout -> master）
            for sld in sorted(x for x in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", x)):
                lays = [t for t in _rels_of(z, sld).values() if "/slideLayouts/" in t]
                if not lays:
                    bad.append(f"slide がレイアウトを参照していない: {sld}")
                    continue
                lay = lays[0]
                lay_ph = _phs(z, lay)
                for want in sorted(_phs(z, sld)):
                    if want not in lay_ph:
                        bad.append(f"継承が切れている: {sld} の ph {want} が {lay} に無い")
                masters = [t for t in _rels_of(z, lay).values() if "/slideMasters/" in t]
                if not masters:
                    bad.append(f"layout がマスタを参照していない: {lay}")
                    continue
                # ⚠️★★★ layout -> master は **type だけ**で照合する（★ idx で照合しない）。
                # 実物の PowerPoint では layout の `dt` / `ftr` / `sldNum` は
                # **master と idx が違うのが正常**（2026-09-02 に既定テンプレートで実測:
                # master は dt:2 / ftr:3 / sldNum:4、layout は dt:10 / ftr:11 / sldNum:12）。
                # idx で照合すると **偽陽性を 6 件出す**。★ slide -> layout は idx まで一致が要る。
                mst_t = {_base_type(w.split(":")[0]) for w in _phs(z, masters[0])}
                for want in sorted({_base_type(w.split(":")[0]) for w in lay_ph}):
                    if want not in mst_t:
                        bad.append(
                            f"継承が切れている: {lay} の ph type {want} が {masters[0]} に無い "
                            f"(master={sorted(mst_t) or '無し'})"
                        )

            # (8) ★★★ パートが参照する rId が、そのパートの .rels に実在するか
            # ⚠️★★★ 2026-09-04 追加。★ 検査 (5) は「rels → パート」の向きしか見ておらず、
            # **宙吊りの `r:embed`（rels に無い rId を XML が指している）を素通りさせていた**
            # （★ code-reviewer の指摘。実測で `r:embed` を存在しない rId に書き換えても clean だった）。
            # ⚠️ `_ChromeSpec` の関係張り替えを失敗させると **まさにこの形**で壊れる ——
            # ★ 本版の中核機能が、それまで無検査だったということである。
            for part in sorted(n for n in names if n.endswith(".xml") and n.startswith("ppt/")):
                have = set(_rels_of(z, part))
                used = set()
                for node in ET.fromstring(z.read(part)).iter():
                    for attr in ("embed", "link", "id", "pict", "dm", "lo", "qs", "cs"):
                        rid = node.get(f"{{{R_NS_V}}}{attr}")
                        if rid:
                            used.add(rid)
                for rid in sorted(used - have):
                    bad.append(f"宙吊りの関係参照: {part} が {rid} を指しているが .rels に無い")
    except zipfile.BadZipFile as e:
        bad.append(f"ZIP として開けない: {e}")
    return bad


# --- 出力の中身を数える（★ 変異体検査の土台）--------------------------------


def measure(path: pathlib.Path) -> dict:
    """出来上がった .pptx を**中身で**数える。★ selftest はここを見て退行を判定する。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        pres = ET.fromstring(z.read("ppt/presentation.xml"))
        sz = pres.find(f"{{{P_NS}}}sldSz")
        slides = sorted(n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
        layouts, tables, pics, chrome = [], 0, 0, 0
        for s in slides:
            rels = _rels_of(z, s)
            layouts.append(next((v for v in rels.values() if "/slideLayouts/" in v), ""))
            root = ET.fromstring(z.read(s))
            tables += len(list(root.iter(f"{{{A_NS}}}tbl")))
            pics += len(list(root.iter(f"{{{P_NS}}}pic")))
            for sp in root.iter(f"{{{P_NS}}}sp"):
                if sp.find(f".//{{{P_NS}}}ph") is None:
                    chrome += 1
        return {
            "slides": len(slides),
            "width": int(sz.get("cx")) if sz is not None else 0,
            "height": int(sz.get("cy")) if sz is not None else 0,
            "layouts": layouts,
            "distinct_layouts": len(set(layouts)),
            "tables": tables,
            "pictures": pics,
            "nonplaceholder_shapes": chrome,
            "media": sorted(n for n in names if "/media/" in n),
        }


# --- selftest ----------------------------------------------------------------


def _tiny_png(path: pathlib.Path, w: int = 40, h: int = 24) -> None:
    import struct
    import zlib

    raw = b"".join(b"\x00" + b"\x66\x99\xcc" * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def _make_template(path: pathlib.Path, png: pathlib.Path) -> tuple[int, int]:
    """★ selftest 用の合成テンプレート。

    ⚠️ 研究者のテンプレート (`deck_temp1.pptx`) は repo 外にもコピーがあり、CI では当てにできない。
    → ★ **同じ性質**を持つものを作って検査する:
      既定と違う版面 / 同梱スライドあり / 装飾図形あり / ⚠️ **`docProps/app.xml` が無い**。
    """
    prs = Presentation()
    w, h = 9144000, 5143500  # ★ 10.00 x 5.625 inch —— python-pptx 既定と**違う**値であることが肝
    prs.slide_width, prs.slide_height = Emu(w), Emu(h)
    lay = next(
        l for l in prs.slide_layouts
        if {0, 1} <= {p.element.ph_idx for p in l.placeholders}
    )
    for i in range(3):
        s = prs.slides.add_slide(lay)
        s.shapes.title.text_frame.text = f"見本{i}"
        deco = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(0), Emu(0), Emu(w // 40), Emu(h))
        deco.fill.solid()
        deco.fill.fore_color.rgb = RGBColor(0x05, 0x8D, 0xC7)
        # ⚠️★★★ 装飾に**画像を含める**（★ code-reviewer の指摘で 2026-09-04 に直した）。
        # ★ 旧版は画像を 3 枚目にだけ置いていたが `capture_chrome` は図形数最小＝1 枚目を選ぶため、
        #   **`_ChromeSpec` の rId 張り替え（本版の中核）が selftest を 1 度も通らなかった**。
        s.shapes.add_picture(str(png), Emu(0), Emu(0), Emu(w // 10), Emu(h // 10))
        if i == 2:  # ★ 図形数を増やして「最小のものが選ばれる」規則を検査可能にする
            s.shapes.add_textbox(Emu(0), Emu(0), Emu(10), Emu(10))
        s._element.set("showMasterSp", "0")
    prs.save(str(path))

    # ⚠️★★★ `deck_temp1.pptx`（Google スライド書き出し）に倣って **app.xml を剥ぐ**。
    # ★ これを剥がないと `_ensure_app_xml` の経路が selftest で 1 度も走らない。
    with zipfile.ZipFile(path) as z:
        items = [(n, z.read(n)) for n in z.namelist() if n != "docProps/app.xml"]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            if name == "[Content_Types].xml":
                data = re.sub(rb'<Override[^>]*docProps/app\.xml"/>', b"", data)
                data = re.sub(rb'<Override[^>]*PartName="/docProps/app\.xml"[^>]*/>', b"", data)
            elif name == "_rels/.rels":
                data = re.sub(rb'<Relationship[^>]*docProps/app\.xml"[^>]*/>', b"", data)
            z.writestr(name, data)
    return w, h


def selftest() -> int:
    import tempfile

    ng = 0

    def check(label: str, ok: bool, detail: str = "") -> None:
        nonlocal ng
        if not ok:
            print(f"[NG] {label}{(' -- ' + detail) if detail else ''}")
            ng += 1

    md_basic = (
        "# 表題\n\n本文A\n\n- 箇条書き1\n- **太字**の項目\n\n---\n\n"
        "## 2枚目\n\n> 引用は本文にする\n\n`コード` を含む行\n"
    )

    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)

        # --- (A) 解析 -------------------------------------------------------
        slides = split_slides(md_basic, unescape=True)
        check("分割数", len(slides) == 2, f"{len(slides)} != 2")

        parsed = split_slides(
            "<!-- layout: two -->\n# T\n\n![a](fig.png)\n\n- x\n\n---\n\n# U\n\n![b](fig.png)\n"
            "\n---\n\n# V\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
            unescape=False,
        )
        check("レイアウト明示指定", parsed[0].resolved_kind() == "two", parsed[0].resolved_kind())
        check("図のみ -> figure", parsed[1].resolved_kind() == "figure", parsed[1].resolved_kind())
        check("既定 -> content", parsed[2].resolved_kind() == "content", parsed[2].resolved_kind())
        check("表の解析", parsed[2].blocks[0][0] == "table" and len(parsed[2].blocks[0][1]) == 2,
              str(parsed[2].blocks[0]))

        # ★ 入れ子のビュレット（⚠️ 拾わないと段が黙って平らになる）
        nested = split_slides("# T\n\n- 親\n  - 子\n    - 孫\n", unescape=False)
        levels = [b[3] for b in nested[0].blocks if b[0] == "text"]
        check("入れ子の段を拾う", levels == [0, 1, 2], str(levels))

        # ★ 枠幅を無視しないこと（旧版は文字数だけで決めていた）
        long_line = [("あ" * 400, False, 0)]
        wide = fit_pt(long_line, (0, 0, 8000000, 3000000))
        narrow = fit_pt(long_line, (0, 0, 2000000, 3000000))
        check("枠が狭いほど字が小さい", narrow < wide, f"narrow={narrow} wide={wide}")

        # --- (B) テンプレート無し（★ 旧経路の互換）--------------------------
        plain_out = d / "plain.pptx"
        build(slides, plain_out, base_dir=d, root=d)
        for b in verify(plain_out, 2):
            check("既定テンプレートの出力", False, b)
        m0 = measure(plain_out)
        check("既定テンプレートの版面", (m0["width"], m0["height"]) == (FALLBACK_EMU_W, FALLBACK_EMU_H),
              str((m0["width"], m0["height"])))

        # --- (C) テンプレートあり -------------------------------------------
        png = d / "fig.png"
        _tiny_png(png)
        tmpl = d / "tmpl.pptx"
        tw, th = _make_template(tmpl, png)
        with zipfile.ZipFile(tmpl) as z:
            check("見本テンプレートに app.xml が無い（前提）", "docProps/app.xml" not in z.namelist())

        md_full = (
            "<!-- layout: title -->\n# 表紙\n\n副題の行\n\n---\n\n"
            "# 図と説明\n\n![図](fig.png)\n\n- 右に来る説明\n- もう 1 行\n\n---\n\n"
            "# 図だけ\n\n![図](fig.png)\n\n---\n\n"
            "# 表\n\n本文\n\n| 見出し | 値 |\n|---|---|\n| a | 1 |\n| b | 2 |\n"
        )
        specs = split_slides(md_full, unescape=False)
        out = d / "tmpl_out.pptx"
        info = build(specs, out, template=tmpl, base_dir=d, root=d)
        for b in verify(out, len(specs)):
            check("テンプレート経路の出力", False, b)
        m = measure(out)

        # ★ テンプレートに無かった app.xml を、出力側で補ったこと
        with zipfile.ZipFile(out) as z:
            check("欠けていた app.xml を補った", "docProps/app.xml" in z.namelist())
        check("見本スライドを消した", info["dropped"] == 3, f"dropped={info['dropped']}")
        check("出力枚数", m["slides"] == 4, str(m["slides"]))
        # ⚠️★★★ 旧版の最大の穴。★ テンプレートの版面を上書きしていないこと。
        check("版面を上書きしていない", (m["width"], m["height"]) == (tw, th),
              f"{(m['width'], m['height'])} != {(tw, th)}")
        check("図を実際に埋め込んだ", m["pictures"] >= 2, f"pic={m['pictures']}")
        check("表を a:tbl にした", m["tables"] == 1, f"tbl={m['tables']}")
        # ★ スライドごとにレイアウトを選べていること（旧版は 1 種類しか使わなかった）
        check("レイアウトが 1 種類ではない", m["distinct_layouts"] >= 2, str(m["layouts"]))
        # ★ 「地」を全スライドへ複製したこと（見本の最小図形数スライドは装飾 1 個）
        check("chrome を採取した", info["chrome"] == 2, str(info["chrome"]))
        check("chrome の見本は図形数最小のもの", info["chrome_from"] in (1, 2), str(info["chrome_from"]))
        check("chrome を全スライドへ置いた", m["nonplaceholder_shapes"] >= m["slides"],
              f"shapes={m['nonplaceholder_shapes']} slides={m['slides']}")
        # ★★★ chrome に画像が含まれ、その関係が全スライドで張り替わっていること。
        # ⚠️ ここが本版の中核（`_ChromeSpec.parts`）で、旧 selftest は 1 度も通っていなかった。
        check("chrome の画像を採取した", info["chrome_images"] == 1, str(info["chrome_images"]))
        check("図 2 枚 ＋ chrome 4 枚ぶんの pic がある", m["pictures"] == 2 + m["slides"],
              f"pic={m['pictures']} slides={m['slides']}")
        with zipfile.ZipFile(out) as _z:
            for _s in sorted(x for x in _z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", x)):
                if not any("/media/" in v for v in _rels_of(_z, _s).values()):
                    check(f"chrome 画像の関係が張られている ({_s})", False)
                    break

        # --- (D) 変異体（★ 検査が空回りしていないか）------------------------
        # 退行 1: ZIP でない
        broken = d / "broken.pptx"
        broken.write_bytes(b"not a zip")
        check("壊れたファイルを検出する", bool(verify(broken, 1)))

        def _mutate(name: str, keep, mutate=None) -> pathlib.Path:
            o = d / name
            with zipfile.ZipFile(out) as src, zipfile.ZipFile(o, "w", zipfile.ZIP_DEFLATED) as dst:
                for n in src.namelist():
                    if not keep(n):
                        continue
                    data = src.read(n)
                    dst.writestr(n, mutate(n, data) if mutate else data)
            return o

        # 退行 2: 標準パートを落とす（★ Google Slides で落ちた形の一部）
        r1 = _mutate("no_parts.pptx", lambda n: n not in ("ppt/presProps.xml", "docProps/core.xml"))
        check("標準パート欠落を検出する", bool(verify(r1, 4)))

        # 退行 3: slideMaster からプレースホルダを剥ぐ（★ 継承チェーンを切る）
        def _strip_ph(n: str, data: bytes) -> bytes:
            if not re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", n):
                return data
            return re.sub(rb"<p:ph[^>]*/>", b"", data)

        r2 = _mutate("no_ph.pptx", lambda n: True, _strip_ph)
        check("継承の切れた master を検出する", bool(verify(r2, 4)))

        # 退行 3b: ⚠️★★★ 画像の関係を宙吊りにする（★ `_ChromeSpec` の張り替え失敗と同じ形）
        def _break_embed(n: str, data: bytes) -> bytes:
            if not re.fullmatch(r"ppt/slides/slide\d+\.xml", n):
                return data
            return data.replace(b'r:embed="rId', b'r:embed="rIdX', 1)

        r2b = _mutate("dangling.pptx", lambda n: True, _break_embed)
        check("宙吊りの関係参照を検出する", bool(verify(r2b, 4)))

        # 退行 4: ⚠️★★★ 版面の上書きを**復活させた**版を作り、measure が気づくか
        bad_size = d / "bad_size.pptx"
        prs = Presentation(str(tmpl))
        prs.slide_width, prs.slide_height = Emu(FALLBACK_EMU_W), Emu(FALLBACK_EMU_H)
        prs.save(str(bad_size))
        mb = measure(bad_size)
        check("版面の上書きを検出できる", (mb["width"], mb["height"]) != (tw, th))

        # 退行 5: 見本スライドを消さない版
        keep_out = d / "keep_samples.pptx"
        prs2 = Presentation(str(tmpl))
        geo2 = Geometry(prs2.slide_width, prs2.slide_height)
        for spec in specs:
            render_slide(prs2, spec, geo2, None, d, d)
        prs2.save(str(keep_out))
        mk = measure(keep_out)
        check("見本残留を検出できる", mk["slides"] == 3 + len(specs), str(mk["slides"]))

        # 退行 6: 図を書かない版（★ 画像記法を素通しした旧挙動の再現）
        no_img = [SlideSpec(s.title, "content", s.non_images) for s in specs]
        no_img_out = d / "no_img.pptx"
        build(no_img, no_img_out, template=tmpl, base_dir=d, root=d)
        mi = measure(no_img_out)
        check("図の欠落を検出できる", mi["pictures"] < m["pictures"],
              f"{mi['pictures']} vs {m['pictures']}")

        # 退行 7: 表を行として流した版（★ 旧挙動）
        flat = [SlideSpec(s.title, "content", [b for b in s.blocks if b[0] != "table"])
                for s in specs]
        flat_out = d / "flat.pptx"
        build(flat, flat_out, template=tmpl, base_dir=d, root=d)
        check("表の非テーブル化を検出できる", measure(flat_out)["tables"] == 0)

        # 退行 8: 全スライドを 1 レイアウトに固定した版（★ 旧挙動）
        one = [SlideSpec(s.title, "content", s.non_images) for s in specs]
        one_out = d / "one_layout.pptx"
        build(one, one_out, template=tmpl, base_dir=d, root=d)
        check("レイアウト単一化を検出できる", measure(one_out)["distinct_layouts"] == 1,
              str(measure(one_out)["layouts"]))

        # 退行 9: ⚠️ repo 外の画像を拒むこと
        outside = d.parent / "outside_repo_probe.png"
        _tiny_png(outside)
        try:
            resolve_image(str(outside), d, d)
            check("repo 外の画像を拒む", False, "素通りした")
        except SystemExit:
            pass
        finally:
            outside.unlink(missing_ok=True)

        # 退行 10: SVG を拒むこと（★ python-pptx は SVG を画像として認識しない）
        svg = d / "x.svg"
        svg.write_text('<svg viewBox="0 0 10 10"></svg>', encoding="utf-8")
        try:
            resolve_image("x.svg", d, d)
            check("SVG を拒む", False, "素通りした")
        except SystemExit:
            pass

    print("[OK] selftest 通過" if ng == 0 else f"[FAILED] {ng} 件")
    return 1 if ng else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()

    template = chrome_from = None
    use_chrome = "--no-chrome" not in argv
    rest: list[str] = []
    # ⚠️ 未知フラグを黙って捨てていた（code-reviewer 指摘）。★ `--nochrome` の打ち間違いが
    #   そのまま通り、chrome が付いたまま静かに成功していた。→ 既知の集合で弾く。
    known = {"--unescape", "--no-chrome", "--selftest"}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("--template", "--chrome-from"):
            if i + 1 >= len(argv):
                print(f"[md2pptx] FAILED: {a} に値がない", file=sys.stderr)
                return 2
            i += 1
            if a == "--template":
                template = pathlib.Path(argv[i]).resolve()
            else:
                try:
                    chrome_from = int(argv[i]) - 1
                except ValueError:
                    print(f"[md2pptx] FAILED: --chrome-from は整数: {argv[i]!r}", file=sys.stderr)
                    return 2
        elif a.startswith("--"):
            if a not in known:
                print(f"[md2pptx] FAILED: 未知のオプション: {a}", file=sys.stderr)
                return 2
        else:
            rest.append(a)
        i += 1

    if len(rest) != 2:
        print(__doc__)
        return 2
    src, dst = pathlib.Path(rest[0]), pathlib.Path(rest[1])
    if template is not None and not template.is_file():
        print(f"[md2pptx] FAILED: テンプレートが無い: {template}", file=sys.stderr)
        return 1

    slides = split_slides(src.read_text(encoding="utf-8"), "--unescape" in argv)
    if not slides:
        print("[md2pptx] FAILED: スライドが 0 枚（`---` で区切られているか確認）", file=sys.stderr)
        return 1

    info = build(slides, dst, template=template, base_dir=src.resolve().parent,
                 chrome_from=chrome_from, use_chrome=use_chrome)
    bad = verify(dst, len(slides))
    if bad:
        for b in bad:
            print(f"[md2pptx] FAILED: {b}", file=sys.stderr)
        return 1

    from collections import Counter

    kinds = ", ".join(f"{k}={v}" for k, v in sorted(Counter(info["kinds"]).items()))
    w, h = info["size"]
    print(
        f"[ok] {dst}  ({dst.stat().st_size:,} bytes / {len(slides)} 枚 / "
        f"{w / EMU_PER_INCH:.2f} x {h / EMU_PER_INCH:.2f} inch / {kinds})"
    )
    if template is not None:
        print(
            f"     template={template.name} / 見本 {info['dropped']} 枚を削除 / "
            f"chrome {info['chrome']} 図形を {info['chrome_from']} 枚目から複製"
        )
        # ⚠️★★★ テンプレート由来の画像を**黙って運ばない**（2026-09-04 に実害が出た）。
        inherited = info.get("inherited_media") or []
        if inherited:
            print(
                f"[warn] テンプレート由来の画像が {len(inherited)} 件、出力に残っている: "
                f"{', '.join(pathlib.PurePosixPath(x).name for x in inherited)}",
                file=sys.stderr,
            )
            print(
                "       ★ 提出物なら、それを配布してよいか確かめること"
                "（★ マスタ / レイアウトが参照する画像は見本スライドを消しても残る）",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
