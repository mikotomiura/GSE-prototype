#!/usr/bin/env python3
"""Markdown -> .docx（標準ライブラリのみ）。

対応: # 〜 #### 見出し / 段落 / **太字** / `コード` / 箇条書き(- *) / 番号付き /
      表 (| ... |) / 引用 (>) / 水平線 (---) / コードブロック (```)
用途: 配布用の手引き・解説を Word で開ける形にする。
"""
from __future__ import annotations

import pathlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

# ★ ZIP エントリの固定日時（★ 出力を再現可能にするため）
ZIP_TS = (2026, 1, 1, 0, 0, 0)

NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# --- インライン（**太字** / `コード` / *斜体*） -------------------------------
# ⚠️ 順序が意味を持つ: `**太字**` と `` `コード` `` を先に食わせてから `*斜体*` を見る。
#    ★ 先に斜体を見ると `**bold**` が `*` + `*bold*` + `*` に割れる。
#    ★ コード span を先に取るので、`` `silence_*` / `burst_*` `` のような
#      **コード内のアスタリスクは斜体にならない**（G1 の資材で実測）。
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\n]+?\*)")


def runs(text: str, base_bold: bool = False) -> str:
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        bold, mono, italic = base_bold, False, False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            bold, part = True, part[2:-2]
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            mono, part = True, part[1:-1]
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            italic, part = True, part[1:-1]
        props = []
        if bold:
            props.append("<w:b/>")
        if italic:
            props.append("<w:i/>")
        if mono:
            props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Yu Gothic"/>')
        rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
    return "".join(out) or '<w:r><w:t xml:space="preserve"></w:t></w:r>'


def para(text: str, style: str | None = None, ind: int = 0, bold: bool = False) -> str:
    p = []
    if style:
        p.append(f'<w:pStyle w:val="{style}"/>')
    if ind:
        p.append(f'<w:ind w:left="{ind}"/>')
    ppr = f"<w:pPr>{''.join(p)}</w:pPr>" if p else ""
    return f"<w:p>{ppr}{runs(text, bold)}</w:p>"


def table(rows: list[list[str]]) -> str:
    table_width = 9638
    col_width = table_width // len(rows[0])
    grid = "".join(f'<w:gridCol w:w="{col_width}"/>' for _ in rows[0])
    body = []
    for i, row in enumerate(rows):
        cells = []
        for c in row:
            shade = '<w:shd w:val="clear" w:fill="EFEFEF"/>' if i == 0 else ""
            cells.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{col_width}" w:type="dxa"/>'
                '<w:tcBorders>'
                '<w:top w:val="single" w:sz="4" w:color="999999"/>'
                '<w:left w:val="single" w:sz="4" w:color="999999"/>'
                '<w:bottom w:val="single" w:sz="4" w:color="999999"/>'
                '<w:right w:val="single" w:sz="4" w:color="999999"/>'
                "</w:tcBorders>" + shade + "</w:tcPr>"
                + para(c, bold=(i == 0)) + "</w:tc>")
        header = '<w:tblHeader/>' if i == 0 else ""
        row_props = f'<w:trPr><w:cantSplit/>{header}</w:trPr>'
        body.append(f"<w:tr>{row_props}{''.join(cells)}</w:tr>")
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{table_width}" w:type="dxa"/>'
            '<w:tblLayout w:type="fixed"/></w:tblPr>'
            f"<w:tblGrid>{grid}</w:tblGrid>{''.join(body)}</w:tbl><w:p/>")


IMAGE_LINE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")


def image_block(rid: str, alt: str, cx: int, cy: int, doc_id: int) -> str:
    """Inline image. Relationships and media are added by write_docx."""
    safe_alt = esc(alt or "GSE figure")
    return (
        '<w:p><w:r><w:drawing>'
        '<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{doc_id}" name="{safe_alt}" descr="{safe_alt}"/>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="figure.svg"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline>'
        '</w:drawing></w:r></w:p><w:p/>'
    )


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def image_display_size(image_path: pathlib.Path) -> tuple[int, int]:
    """Fit a PNG/SVG into the A4 text width while retaining its aspect ratio."""
    width_emu = 6000000
    if image_path.suffix.lower() == ".png":
        data = image_path.read_bytes()[:24]
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit(f"[NG] PNGヘッダが不正: {image_path}")
        pixel_width = int.from_bytes(data[16:20], "big")
        pixel_height = int.from_bytes(data[20:24], "big")
    else:
        svg = image_path.read_text(encoding="utf-8")
        viewbox = re.search(r'viewBox="[^"]*\\s([0-9.]+)\\s([0-9.]+)"', svg)
        if not viewbox:
            raise SystemExit(f"[NG] SVGのviewBoxが読めない: {image_path}")
        pixel_width, pixel_height = map(float, viewbox.groups())
    if not pixel_width or not pixel_height:
        raise SystemExit(f"[NG] 画像サイズが不正: {image_path}")
    return width_emu, round(width_emu * pixel_height / pixel_width)


def convert(md: str, base_dir: pathlib.Path) -> tuple[str, list[tuple[str, pathlib.Path]]]:
    out: list[str] = []
    images: list[tuple[str, pathlib.Path]] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        s = line.strip()

        if s.startswith("```"):                       # コードブロック
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                out.append(para(lines[i], style="Code"))
                i += 1
            i += 1
            continue

        if not s:
            i += 1
            continue

        image_match = IMAGE_LINE.fullmatch(s)
        if image_match:
            alt, target = image_match.groups()
            image_path = (base_dir / target).resolve()
            if not image_path.is_file():
                raise SystemExit(f"[NG] 画像が見つからない: {image_path}")
            rid = f"rId{len(images) + 2}"
            images.append((rid, image_path))
            if image_path.suffix.lower() not in {".png", ".svg"}:
                raise SystemExit(f"[NG] 対応画像形式は PNG / SVG のみ: {image_path}")
            cx, cy = image_display_size(image_path)
            out.append(image_block(rid, alt, cx, cy, len(images)))
            i += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s):    # 水平線
            out.append('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="6" '
                       'w:color="BBBBBB"/></w:pBdr></w:pPr></w:p>')
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)         # 見出し
        if m:
            out.append(para(m.group(2), style=f"Heading{len(m.group(1))}"))
            i += 1
            continue

        if s.startswith("|") and i + 1 < len(lines) and re.match(
                r"^\|[\s:|-]+\|$", lines[i + 1].strip()):   # 表
            rows = [split_row(s)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            out.append(table(rows))
            continue

        if s.startswith(">"):                         # 引用
            out.append(para(s.lstrip("> ").strip(), style="Quote", ind=360))
            i += 1
            continue

        m = re.match(r"^(\s*)[-*]\s+(.*)$", raw)      # 箇条書き
        if m:
            depth = len(m.group(1)) // 2
            out.append(para("・" + m.group(2), ind=360 + depth * 360))
            i += 1
            continue

        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", raw)   # 番号付き
        if m:
            depth = len(m.group(1)) // 2
            out.append(para(f"{m.group(2)}. {m.group(3)}", ind=360 + depth * 360))
            i += 1
            continue

        out.append(para(s))
        i += 1
    return "".join(out), images


STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {NS}>
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Yu Gothic" w:hAnsi="Yu Gothic" w:eastAsia="Yu Gothic" w:cs="Yu Gothic"/>
<w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:styleId="Normal" w:default="1"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>
<w:pPr><w:spacing w:before="360" w:after="160"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="34"/><w:color w:val="1A1A1A"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>
<w:pPr><w:spacing w:before="320" w:after="140"/><w:pBdr><w:bottom w:val="single" w:sz="6" w:color="CCCCCC"/></w:pBdr></w:pPr>
<w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="1A1A1A"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/>
<w:pPr><w:spacing w:before="260" w:after="120"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="333333"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading4"><w:name w:val="heading 4"/>
<w:pPr><w:spacing w:before="220" w:after="100"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="22"/><w:color w:val="444444"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/>
<w:pPr><w:pBdr><w:left w:val="single" w:sz="12" w:color="BBBBBB"/></w:pBdr><w:ind w:left="360"/></w:pPr>
<w:rPr><w:color w:val="444444"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/>
<w:pPr><w:spacing w:after="0"/><w:ind w:left="360"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:eastAsia="Yu Gothic"/><w:sz w:val="19"/></w:rPr></w:style>
</w:styles>"""

COMPACT_STYLES = (STYLES
    .replace('<w:spacing w:after="120" w:line="276" w:lineRule="auto"/>',
             '<w:spacing w:after="0" w:line="216" w:lineRule="auto"/>')
    .replace('<w:spacing w:before="360" w:after="160"/>',
             '<w:spacing w:before="200" w:after="80"/>')
    .replace('<w:spacing w:before="320" w:after="140"/>',
             '<w:spacing w:before="160" w:after="60"/>')
    .replace('<w:spacing w:before="260" w:after="120"/>',
             '<w:spacing w:before="140" w:after="50"/>'))

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Default Extension="svg" ContentType="image/svg+xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

def doc_rels(images: list[tuple[str, pathlib.Path]]) -> str:
    rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
    for index, (rid, image_path) in enumerate(images, start=1):
        rels.append(
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{index}{image_path.suffix.lower()}"/>'
        )
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + ''.join(rels) + '</Relationships>')


def write_docx(md: str, out: pathlib.Path, base_dir: pathlib.Path, compact: bool = False) -> None:
    body, images = convert(md, base_dir)
    margins = ('<w:pgMar w:top="700" w:right="1134" w:bottom="700" w:left="1134"/>'
               if compact else
               '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>')
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document {NS}>'
           f"<w:body>{body}"
           '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
           f'{margins}</w:sectPr>'
           "</w:body></w:document>")
    out.parent.mkdir(parents=True, exist_ok=True)
    # ⚠️★★★ 2026-09-02: ZIP エントリの日時を固定する。
    # ★ 既定では `writestr` が **実行時刻**を書くため、内容が 1 バイトも変わっていなくても
    # 再生成のたびにバイナリが変わり、`git status` に常に差分が出る（2026-09-02 に実測）。
    # → ★ 「再生成しても中身が同じなら差分ゼロ」を成立させる。
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in (
            ("[Content_Types].xml", CONTENT_TYPES),
            ("_rels/.rels", RELS),
            ("word/_rels/document.xml.rels", doc_rels(images)),
            ("word/styles.xml", COMPACT_STYLES if compact else STYLES),
            ("word/document.xml", doc),
        ):
            info = zipfile.ZipInfo(name, date_time=ZIP_TS)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, data)
        for index, (_, image_path) in enumerate(images, start=1):
            info = zipfile.ZipInfo(f"word/media/image{index}{image_path.suffix.lower()}", date_time=ZIP_TS)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, image_path.read_bytes())
    # ★ 書いた直後に全パートを検証する。壊れた .docx を黙って出荷しない。
    with zipfile.ZipFile(out) as z:
        for name in z.namelist():
            if name.endswith((".xml", ".rels")):
                try:
                    ET.fromstring(z.read(name))
                except ET.ParseError as e:
                    out.unlink(missing_ok=True)
                    raise SystemExit(f"[NG] {out.name} :: {name} が不正な XML: {e}")


if __name__ == "__main__":
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    text = src.read_text(encoding="utf-8")
    # ★ 実験者向け注記の切り落とし。--from= 以降 / --until= より前 だけを使う。
    #   ⚠️ マーカーが見つからなければ **黙って通さず落とす**（切り落とし漏れは配布事故になる）。
    compact = "--compact" in sys.argv[3:]
    for arg in sys.argv[3:]:
        if arg.startswith("--from="):
            marker = arg.split("=", 1)[1]
            if marker not in text:
                sys.exit(f"[NG] --from のマーカーが見つからない: {marker!r}")
            text = text[text.index(marker):]
        elif arg.startswith("--until="):
            marker = arg.split("=", 1)[1]
            if marker not in text:
                sys.exit(f"[NG] --until のマーカーが見つからない: {marker!r}")
            text = text[:text.index(marker)]
        elif arg.startswith("--title="):
            text = f"# {arg.split('=', 1)[1]}\n\n" + text
        elif arg == "--unescape":
            # ★ pandoc 由来のバックスラッシュ・エスケープ (`1\.` / `0.054\*`) を外す。
            # ⚠️ **opt-in にしてある**: 既存の呼び出し元 (G1 の make-handouts.sh) の markdown は
            #    コードブロック内に `\n` / `\g` / `\<` 等を含んでおり、無条件に外すと壊れる。
            # ★ 対象は markdown の句読点エスケープのみに絞る (`\n` 等の文字は触らない)。
            text = re.sub(r"\\([.*_\[\]()#+\-!~<>|`])", r"\1", text)
        elif arg == "--frontmatter-title":
            # ★ 課題文用: front matter を **落として** title と id だけを見出しにする。
            #   ⚠️ `version: lo|hi` と `sources:` を印刷すると条件が被験者に見えてしまう。
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
            if not m:
                sys.exit(f"[NG] front matter が無い: {src}")
            meta = dict(
                (k.strip(), v.strip())
                for k, v in (ln.split(":", 1) for ln in m.group(1).splitlines() if ":" in ln))
            head = meta.get("title", "課題")
            if meta.get("id") and meta["id"] != "copy":
                head += f"（{meta['id']}）"
            text = f"# {head}\n\n" + m.group(2)
    write_docx(text, dst, src.parent, compact=compact)
    print(f"[ok] {dst}  ({dst.stat().st_size:,} bytes)")
