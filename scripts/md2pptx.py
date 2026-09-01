#!/usr/bin/env python3
"""Markdown -> .pptx（標準ライブラリのみ）。

★ `scripts/md2docx.py` の姉妹。⚠️ **同じ理由で標準ライブラリだけで書く** ——
本機に `pandoc` は無く（2026-08-30 実測）、`python-pptx` も入っていない（2026-09-01 実測）。
`.pptx` は `.docx` と同じ OOXML（ZIP + XML）なので、`zipfile` と文字列組み立てで作れる。

## スライドの切り方（★ 規約）

- `---`（水平線）で **1 枚**に割る。★ これが唯一の区切りである。
- 各スライドの **最初の見出し行**（`#` 〜 `###`）がタイトルになる。無ければタイトル空欄。
- 残りが本文。`-` / `*` の箇条書きはビュレット、それ以外は段落として積む。
- ⚠️ **表とコードブロックは「行」として素朴に流す**（★ pptx の table まではやらない）。
  → ★ 表を出したいスライドは `md2docx.py` 側（技術設計書）に置くこと。

## 使い方

    PYTHONUTF8=1 python scripts/md2pptx.py <in.md> <out.pptx> [--unescape]

⚠️ Windows コンソールは cp932 なので **`PYTHONUTF8=1`** を付ける。
★ `--unescape` は `md2docx.py` と同じ意味（`1\.` のような backslash escape を外す）。

## 検算

    PYTHONUTF8=1 python scripts/md2pptx.py --selftest

⚠️★★★ **「開けるか」は生成できたことと別である。** 本 selftest が見るのは
(1) ZIP として開けるか (2) 必須パートが全部あるか (3) 各 XML が parse できるか
(4) スライド数が期待どおりか —— の 4 点であり、**PowerPoint での表示は目視で確かめること。**
"""
from __future__ import annotations

import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

EMU_W, EMU_H = 12192000, 6858000  # 16:9

# --- インライン（md2docx.py と同じ順序規則）---------------------------------
# ⚠️ 順序が意味を持つ: `**太字**` と `` `コード` `` を先に食わせてから `*斜体*` を見る。
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\n]+?\*)")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def runs(text: str) -> str:
    """インライン装飾を <a:r> の並びへ。"""
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        b = i = 0
        mono = False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            b, part = 1, part[2:-2]
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            mono, part = True, part[1:-1]
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            i, part = 1, part[1:-1]
        props = f'<a:rPr lang="ja-JP" dirty="0" b="{b}" i="{i}"'
        if mono:
            props += '><a:latin typeface="Consolas"/></a:rPr>'
        else:
            props += "/>"
        out.append(f"<a:r>{props}<a:t>{esc(part)}</a:t></a:r>")
    return "".join(out) or '<a:r><a:rPr lang="ja-JP"/><a:t></a:t></a:r>'


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


def slide_xml(title: str, body: list[tuple[str, bool]]) -> str:
    # ★ 本文が多いスライドは自動で字を詰める（⚠️ 目安であって組版ではない）
    n = sum(len(t) for t, _ in body)
    sz = 1800 if n < 300 else 1400 if n < 700 else 1100
    IND = ' marL="342900" indent="-342900"'
    BU_ON = '<a:buChar char="•"/>'
    BU_OFF = "<a:buNone/>"
    parts = []
    for t, b in body:
        ind = IND if b else ""
        bu = BU_ON if b else BU_OFF
        parts.append("<a:p><a:pPr" + ind + ">" + bu + "</a:pPr>" + runs(t) + "</a:p>")
    paras = "".join(parts) or "<a:p/>"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="685800" y="365760"/><a:ext cx="10820400" cy="1143000"/></a:xfrm></p:spPr><p:txBody><a:bodyPr><a:normAutofit/></a:bodyPr><a:lstStyle/><a:p><a:r><a:rPr lang="ja-JP" sz="2800" b="1"/><a:t>{esc(title)}</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="685800" y="1660000"/><a:ext cx="10820400" cy="4600000"/></a:xfrm></p:spPr><p:txBody><a:bodyPr><a:normAutofit/></a:bodyPr><a:lstStyle><a:lvl1pPr><a:defRPr sz="{sz}"/></a:lvl1pPr></a:lstStyle>{paras}</p:txBody></p:sp>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"""


MASTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>"""

LAYOUT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="obj" preserve="1"><p:cSld name="Title and Content"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"""

THEME = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="GSE"><a:themeElements><a:clrScheme name="GSE"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2430"/></a:dk2><a:lt2><a:srgbClr val="EEF1F5"/></a:lt2><a:accent1><a:srgbClr val="2E6DB4"/></a:accent1><a:accent2><a:srgbClr val="C0504D"/></a:accent2><a:accent3><a:srgbClr val="9BBB59"/></a:accent3><a:accent4><a:srgbClr val="8064A2"/></a:accent4><a:accent5><a:srgbClr val="4BACC6"/></a:accent5><a:accent6><a:srgbClr val="F79646"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme><a:fontScheme name="GSE"><a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface="Yu Gothic UI"/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface="Yu Gothic UI"/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="GSE"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>"""


def build(slides, out: pathlib.Path) -> None:
    n = len(slides)
    sld_ids = "".join(
        f'<p:sldId id="{256+i}" r:id="rId{i+2}"/>' for i in range(n))
    pres = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            f'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            f'<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
            f'<p:sldIdLst>{sld_ids}</p:sldIdLst>'
            f'<p:sldSz cx="{EMU_W}" cy="{EMU_H}"/><p:notesSz cx="{EMU_H}" cy="{EMU_W}"/>'
            f"</p:presentation>")
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 f'<Relationships xmlns="{R}">'
                 f'<Relationship Id="rId1" Type="{R}/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(n):
        pres_rels.append(
            f'<Relationship Id="rId{i+2}" Type="{R}/slide" Target="slides/slide{i+1}.xml"/>')
    pres_rels.append(
        f'<Relationship Id="rId{n+2}" Type="{R}/theme" Target="theme/theme1.xml"/></Relationships>')

    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>']
    for i in range(n):
        ct.append(f'<Override PartName="/ppt/slides/slide{i+1}.xml" '
                  f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
    ct.append("</Types>")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   f'<Relationships xmlns="{R}"><Relationship Id="rId1" '
                   f'Type="{R}/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", "".join(pres_rels))
        z.writestr("ppt/slideMasters/slideMaster1.xml", MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   f'<Relationships xmlns="{R}">'
                   f'<Relationship Id="rId1" Type="{R}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
                   f'<Relationship Id="rId2" Type="{R}/theme" Target="../theme/theme1.xml"/></Relationships>')
        z.writestr("ppt/slideLayouts/slideLayout1.xml", LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   f'<Relationships xmlns="{R}"><Relationship Id="rId1" '
                   f'Type="{R}/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>')
        z.writestr("ppt/theme/theme1.xml", THEME)
        for i, (t, b) in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(t, b))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       f'<Relationships xmlns="{R}"><Relationship Id="rId1" '
                       f'Type="{R}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>')


REQUIRED = ["[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml",
            "ppt/_rels/presentation.xml.rels", "ppt/slideMasters/slideMaster1.xml",
            "ppt/slideLayouts/slideLayout1.xml", "ppt/theme/theme1.xml"]


def verify(path: pathlib.Path, expect_slides: int) -> list[str]:
    """⚠️ 「生成できた」と「開ける」は別。ZIP / 必須パート / XML / 枚数を実際に見る。"""
    bad = []
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
    except zipfile.BadZipFile as e:
        bad.append(f"ZIP として開けない: {e}")
    return bad


def selftest() -> int:
    import tempfile
    md = ("# 表題\n\n本文A\n\n- 箇条書き1\n- **太字**の項目\n\n---\n\n"
          "## 2枚目\n\n> 引用は本文にする\n\n`コード` を含む行\n")
    cases = [(md, 2)]
    ng = 0
    with tempfile.TemporaryDirectory() as d:
        for i, (src, expect) in enumerate(cases):
            out = pathlib.Path(d) / f"t{i}.pptx"
            slides = split_slides(src, unescape=True)
            if len(slides) != expect:
                print(f"[NG] 分割数 {len(slides)} != {expect}")
                ng += 1
                continue
            build(slides, out)
            bad = verify(out, expect)
            for b in bad:
                print(f"[NG] {b}")
            ng += len(bad)
        # ⚠️ 壊れている入力も 1 度通す（★ 検査自体が空回りしていないかを見る）
        broken = pathlib.Path(d) / "broken.pptx"
        broken.write_bytes(b"not a zip")
        if not verify(broken, 1):
            print("[NG] 壊れたファイルを検査が素通りした（★ 検査が空回りしている）")
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
