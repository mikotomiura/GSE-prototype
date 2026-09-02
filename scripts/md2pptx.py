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
★ `python-pptx` は既定テンプレート（本物の PowerPoint ファイル）を土台にするので、
notesMaster・11 レイアウト・docProps・presProps 等が**すべて実物どおり**に入る。

⚠️ **依存が 1 つ増えた**（`python-pptx`）。★ `scripts/md2docx.py` は標準ライブラリのままで、
本スクリプトだけがライブラリを使う。

## スライドの切り方（★ 規約・初版から不変）

- `---`（水平線）で **1 枚**に割る。★ これが唯一の区切りである。
- 各スライドの **最初の見出し行**（`#` 〜 `###`）がタイトルになる。無ければタイトル空欄。
- 残りが本文。`-` / `*` の箇条書きはビュレット、それ以外は段落として積む。
- ⚠️ **表とコードブロックは「行」として素朴に流す**（★ pptx の table まではやらない）。
  → ★ 表を出したいスライドは `md2docx.py` 側（技術設計書）に置くこと。

## 使い方

    PYTHONUTF8=1 python scripts/md2pptx.py <in.md> <out.pptx> [--unescape]

⚠️ Windows コンソールは cp932 なので **`PYTHONUTF8=1`** を付ける。
★ `--unescape` は `md2docx.py` と同じ意味（`1\\.` のような backslash escape を外す）。

## 検算

    PYTHONUTF8=1 python scripts/md2pptx.py --selftest

⚠️★★★ **「開けるか」は生成できたことと別である。** 本 selftest が見るのは
(1) ZIP (2) 必須パート (3) XML の parse (4) 枚数 (5) 関係の Target 実在
(6) content type の網羅 (7) **プレースホルダの継承チェーン** —— の 7 点であり、
★ **これが全部緑でも Google Slides で開けなかった実績がある**（上表）。
→ ⚠️ **表示は実機で確かめること。**
"""
from __future__ import annotations

import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

try:
    from pptx import Presentation
    from pptx.oxml.ns import qn
    from pptx.util import Emu, Pt
except ImportError:  # pragma: no cover - 環境依存
    # ★ `scripts/build_analysis_db.py` と同じ案内の形にそろえる（終了コード 5 も同じ）。
    print("[md2pptx] FAILED: python-pptx が入っていません。", file=sys.stderr)
    print("  run: pip install -r scripts/requirements-dev.txt", file=sys.stderr)
    raise SystemExit(5)

EMU_W, EMU_H = 12192000, 6858000  # 16:9

# ★ 固定タイムスタンプ（⚠️ now() にすると出力が毎回変わり、再生成の差分が読めなくなる）
FIXED_TS = __import__("datetime").datetime(2026, 1, 1, 0, 0, 0)

LATIN, EASTASIA, MONO = "Segoe UI", "Yu Gothic UI", "Consolas"

# --- インライン（md2docx.py と同じ順序規則）---------------------------------
# ⚠️ 順序が意味を持つ: `**太字**` と `` `コード` `` を先に食わせてから `*斜体*` を見る。
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\n]+?\*)")


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


def split_slides(md: str, unescape: bool) -> list[tuple[str, list[tuple[str, bool]]]]:
    """`---` で割り、(タイトル, [(本文行, ビュレットか)]) を返す。"""
    if unescape:
        md = re.sub(r"\\([.\-_*#>`\[\]()])", r"\1", md)
    chunks = re.split(r"^\s*---\s*$", md, flags=re.M)
    slides = []
    for ch in chunks:
        title, body = "", []
        in_code = False
        for raw in ch.split("\n"):
            line = raw.rstrip()
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if not line.strip():
                continue
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m and not in_code:
                t = m.group(2).replace("**", "").strip()
                if not title:
                    title = t
                else:
                    body.append((t, False))
                continue
            if line.lstrip().startswith(">"):
                line = line.lstrip()[1:].strip()
                if not line:
                    continue
            mb = re.match(r"^\s*[-*]\s+(.*)", line)
            if mb and not in_code:
                body.append((mb.group(1).strip(), True))
            else:
                body.append((line.strip(), False))
        if title or body:
            slides.append((title, body))
    return slides


# --- python-pptx の薄い補助 --------------------------------------------------
# ⚠️ python-pptx はビュレットの on/off と東アジアフォントを公開 API で出さないので、
# ★ ここだけ oxml へ降りる（★ 降りるのはこの 2 関数に閉じる）。


def _fonts(run, mono: bool) -> None:
    """`a:latin` / `a:ea` を明示する（★ 日本語がフォールバックで崩れないように）。"""
    rPr = run._r.get_or_add_rPr()
    for tag, face in ((qn("a:latin"), MONO if mono else LATIN), (qn("a:ea"), EASTASIA)):
        el = rPr.find(tag)
        if el is None:
            el = rPr.makeelement(tag, {})
            rPr.append(el)
        el.set("typeface", face)


def _bullet(par, on: bool) -> None:
    """段落のビュレットを明示的に付ける / 外す。"""
    pPr = par._p.get_or_add_pPr()
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    if on:
        pPr.set("marL", "342900")
        pPr.set("indent", "-342900")
        bf = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
        pPr.append(bf)
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "\u2022"}))
    else:
        pPr.set("marL", "0")
        pPr.set("indent", "0")
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))


def _pick_layout(prs):
    """「タイトルと本文」相当のレイアウトを選ぶ。

    ★ **どの経路で返しても `idx=0`（タイトル）と `idx=1`（本文）を両方持つ**ことを保証する。
    `build()` が `slide.placeholders[1]` を触るため、この不変条件が崩れると `KeyError` になる。

    ⚠️★★★ 2026-09-02 の `/cross-review` 指摘で書き直した。旧版は
    `if any(t == 13 for t, _ in types) or True:` という条件を持っていたが、
    (a) `or True` で常に真＝**分岐が死んでいた**、かつ
    (b) ★ **`13` は `TITLE` ではなく `SLIDE_NUMBER`**（実測: `PP_PLACEHOLDER.TITLE = 1`）。
    → ⚠️ `or True` だけを外すと **スライド番号を持つレイアウトしか通らなくなる**回帰を埋め込む形だった。
    ★ 併せて旧版の最終フォールバック `return prs.slide_layouts[1]` は
    **不変条件を検査せずに返していた**ため、テンプレート差し替えで静かに壊れた。→ 明示的に失敗させる。
    """
    qualified = [
        lay
        for lay in prs.slide_layouts
        if {0, 1} <= {ph.element.ph_idx for ph in lay.placeholders}
    ]
    if not qualified:
        raise RuntimeError(
            "タイトル(idx=0)と本文(idx=1)を両方持つレイアウトがテンプレートに無い。"
            " python-pptx の既定テンプレートが変わった可能性がある。"
        )
    for lay in qualified:
        if lay.name in ("Title and Content", "タイトルとコンテンツ"):
            return lay
    return qualified[0]


def build(slides, out: pathlib.Path) -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(EMU_W), Emu(EMU_H)
    cp = prs.core_properties
    cp.author, cp.last_modified_by, cp.title = "GSE", "GSE", ""
    cp.created, cp.modified, cp.revision = FIXED_TS, FIXED_TS, 1
    layout = _pick_layout(prs)

    for title, body in slides:
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text_frame.text = ""
        tp = slide.shapes.title.text_frame.paragraphs[0]
        for txt, b, i, mono in inline_parts(title):
            r = tp.add_run()
            r.text = txt
            r.font.bold = True if b else None
            r.font.italic = True if i else None
            r.font.size = Pt(28)
            _fonts(r, mono)

        ph = slide.placeholders[1]
        tf = ph.text_frame
        tf.word_wrap = True
        # ★ 本文が多いスライドは自動で字を詰める（⚠️ 目安であって組版ではない）
        n = sum(len(t) for t, _ in body)
        sz = Pt(18) if n < 300 else Pt(14) if n < 700 else Pt(11)
        first = True
        for line, is_bullet in body:
            par = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            _bullet(par, is_bullet)
            for txt, b, i, mono in inline_parts(line):
                r = par.add_run()
                r.text = txt
                r.font.bold = True if b else None
                r.font.italic = True if i else None
                r.font.size = sz
                _fonts(r, mono)

    prs.save(str(out))
    _normalize_zip(out)


ZIP_TS = (2026, 1, 1, 0, 0, 0)


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
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
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
                # **master と idx が違うのが正常**であり（2026-09-02 に既定テンプレートで実測:
                # master は dt:2 / ftr:3 / sldNum:4、layout は dt:10 / ftr:11 / sldNum:12）、
                # idx で照合すると **偽陽性を 6 件出す**。★ slide -> layout は idx まで一致が要る。
                mst_t = {w.split(":")[0] for w in _phs(z, masters[0])}
                for want in sorted({w.split(":")[0] for w in lay_ph}):
                    if want not in mst_t:
                        bad.append(
                            f"継承が切れている: {lay} の ph type {want} が {masters[0]} に無い "
                            f"(master={sorted(mst_t) or '無し'})"
                        )
    except zipfile.BadZipFile as e:
        bad.append(f"ZIP として開けない: {e}")
    return bad


def selftest() -> int:
    import tempfile

    md = (
        "# 表題\n\n本文A\n\n- 箇条書き1\n- **太字**の項目\n\n---\n\n"
        "## 2枚目\n\n> 引用は本文にする\n\n`コード` を含む行\n"
    )
    ng = 0
    with tempfile.TemporaryDirectory() as d:
        slides = split_slides(md, unescape=True)
        if len(slides) != 2:
            print(f"[NG] 分割数 {len(slides)} != 2")
            return 1
        # ★ `_pick_layout` の不変条件を明示的に検査する（★ /cross-review 指摘・2026-09-02）
        _idxs = {ph.element.ph_idx for ph in _pick_layout(Presentation()).placeholders}
        if not {0, 1} <= _idxs:
            print(f"[NG] _pick_layout が idx 0/1 を満たさないレイアウトを返した: {sorted(_idxs)}")
            ng += 1

        good = pathlib.Path(d) / "t0.pptx"
        build(slides, good)
        for b in verify(good, 2):
            print(f"[NG] {b}")
            ng += 1

        # ⚠️ 検査自体が空回りしていないかを見る（★ 3 種の退行を実際に作って落ちるか確かめる）
        broken = pathlib.Path(d) / "broken.pptx"
        broken.write_bytes(b"not a zip")
        if not verify(broken, 1):
            print("[NG] 壊れたファイルを検査が素通りした")
            ng += 1

        def _mutate(name: str, keep, mutate=None) -> pathlib.Path:
            out = pathlib.Path(d) / name
            with zipfile.ZipFile(good) as src, zipfile.ZipFile(
                out, "w", zipfile.ZIP_DEFLATED
            ) as dst:
                for n in src.namelist():
                    if not keep(n):
                        continue
                    data = src.read(n)
                    dst.writestr(n, mutate(n, data) if mutate else data)
            return out

        # 退行 1: 標準パートを落とす（★ Google Slides で落ちた形の一部）
        r1 = _mutate("no_parts.pptx", lambda n: n not in ("ppt/presProps.xml", "docProps/core.xml"))
        if not verify(r1, 2):
            print("[NG] 標準パート欠落を検査が素通りした")
            ng += 1

        # 退行 2: slideMaster からプレースホルダを剥ぐ（★ 継承チェーンを切る）
        def _strip_ph(n: str, data: bytes) -> bytes:
            if not re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", n):
                return data
            return re.sub(rb'<p:ph[^>]*/>', b"", data)

        r2 = _mutate("no_ph.pptx", lambda n: True, _strip_ph)
        if not verify(r2, 2):
            print("[NG] 継承の切れた master を検査が素通りした")
            ng += 1

    print("[OK] selftest 通過" if ng == 0 else f"[FAILED] {ng} 件")
    return 1 if ng else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    src, dst = pathlib.Path(args[0]), pathlib.Path(args[1])
    slides = split_slides(src.read_text(encoding="utf-8"), "--unescape" in argv)
    if not slides:
        print("[md2pptx] FAILED: スライドが 0 枚（`---` で区切られているか確認）", file=sys.stderr)
        return 1
    build(slides, dst)
    bad = verify(dst, len(slides))
    if bad:
        for b in bad:
            print(f"[md2pptx] FAILED: {b}", file=sys.stderr)
        return 1
    print(f"[ok] {dst}  ({dst.stat().st_size:,} bytes / {len(slides)} 枚)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
