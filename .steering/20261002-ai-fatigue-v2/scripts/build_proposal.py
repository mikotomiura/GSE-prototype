"""提案のドキュメント v2 を作る（design.md §11 を判断 5・6 に合わせて縮めた形・引き継ぎ §2 の 4）。

前のタスクの build_proposal.py を写して広げた（前のタスクの道具は変えない）。
1. 原稿の自動の区画（<!-- NAME:begin --> 〜 <!-- NAME:end -->）を、34 件の写し・追加候補の表（v2）・探索の data から作り直す:
   counts（§1 の追加候補の数）／pop（§7 の対象者ごとの表）／agree（§7 の一致の表）／search43（§7 の探索の 43 件）／appendix（§9）。
2. 原稿（Markdown の小さな部分集合）から .docx を作る。
3. archive と Downloads に同じものを置き、SHA-256 を archive/proposal-sha256.txt に記録する。
★ 書き込み側は追加候補の表（研究者に渡すもの）から数える。検査器（check_proposal.py）はログと評価版から独立に数える。
★ Downloads の .docx が記録と違えば止まる（研究者に渡す前に手で直された可能性）。
使い方: uv run --with openpyxl --with python-docx python build_proposal.py [--dry-run]
"""
import datetime
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata

import openpyxl
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

import common as C

MD = os.path.join(C.TASK, "proposal", "proposal-v2.md")
DOCX_NAME = "AI疲労DB_判定者1からの提案_v2.docx"
DOCX_ARCHIVE = os.path.join(C.TASK, "archive", DOCX_NAME)
DOCX_DOWNLOADS = os.path.join(C.DOWNLOADS, DOCX_NAME)
SHA_RECORD = os.path.join(C.TASK, "archive", "proposal-sha256.txt")
DOC_TITLE = "AI 疲労の文献 DB：判定者 1 からの報告と提案"
BLOCKS = ("counts", "pop", "agree", "search43", "appendix")


def field(j, name):
    m = re.search(name + r": ([^／]+)", j or "")
    return m.group(1).strip() if m else ""


def short(t, n=60):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t if len(t) <= n else t[:n - 1] + "…"


def cell(s):
    return str(s if s is not None else "").replace("|", "／")


def load_cand(path):
    """追加候補の表（既定は archive）を読み切って閉じる（★ read_only はファイルを開いたままにするので使わない）。"""
    return openpyxl.load_workbook(path or C.CAND_ARCHIVE)


def cand_rows(wb):
    """『スクリーニング』: ID → 列の名前 → 値。"""
    rows = list(wb["スクリーニング"].iter_rows(values_only=True))
    h = list(rows[3])
    return [dict(zip(h, r)) for r in rows[4:] if r and r[0]]


def sheet_rows(wb, name, ncol):
    return [list(r[:ncol]) for r in list(wb[name].iter_rows(values_only=True))[4:] if r and r[0] is not None]


def kinds(rows):
    """表の行を 3 つに分ける: 全文段（判定者 1）・題名・抄録段（判定者 1）・AI の予備判定。"""
    ft = [r for r in rows if r["判定者"] == "判定者 1" and str(r["判定の段"]).startswith("全文段")]
    ta = [r for r in rows if r["判定者"] == "判定者 1" and r["判定の段"] == "題名・抄録段"]
    ai = [r for r in rows if str(r["判定者"] or "").startswith("AI")]
    return ft, ta, ai


def count(rows, key, vals):
    return {v: sum(1 for r in rows if r[key] == v) for v in vals}


def block_counts(rows):
    ft, ta, ai = kinds(rows)
    a = count(ft, "判定者1", ("除外", "保留", "含める"))
    b = count(ta, "判定者1", ("含める", "保留", "除外"))
    c = count(ai, "AI の予備判定（題名・抄録段・評価版）", ("含める", "除外"))
    med = sum(1 for r in ai if str(r["内容の群（機械の分類・判定の材料ではない）"] or "").startswith("医療者"))
    med_all = sum(1 for r in rows if str(r["内容の群（機械の分類・判定の材料ではない）"] or "").startswith("医療者"))
    e4bg = sum(1 for r in ta if str(r["除外理由"] or "").startswith("E4 背景"))
    return "\n".join([
        f"- 追加候補（DB に無い記録）220 件と、判定者 1 が足した 1 件の計 {len(rows)} 件のうち、判定者 1 が判定したのは {len(ft) + len(ta)} 件です："
        f"全文段で {len(ft)} 件（除外 {a['除外']}・保留 {a['保留']}・含める {a['含める']}）、"
        f"題名・抄録段で {len(ta)} 件（含める {b['含める']}・保留 {b['保留']}・除外 {b['除外']}）。"
        f"題名・抄録段の除外のうち {e4bg} 件は、判定者 1 の意図が「範囲の外・背景として残す」です（§7.1）。",
        f"- 残りの {len(ai)} 件は判定者 1 が判定していません。あるのは、AI（Claude）の評価版の題名・抄録段の予備判定"
        f"（含める {c['含める']}・除外 {c['除外']}）だけで、人の判定ではありません。"
        + (f"医療者の記録 {med_all} 件は、すべてこちらです（§7.1）。" if med == med_all else
           f"医療者の記録 {med_all} 件のうち {med} 件がこちらです（§7.1）。"),
        f"- 題名・抄録段で判定者 1 が含める・保留にした {b['含める'] + b['保留']} 件の全文段と品質評価、レビューを狙った探索の読む一覧 43 件を"
        "候補に足すかの判定は、行っていません（§3 の Q11〜Q13）。",
    ])


def block_pop(wb):
    g = sheet_rows(wb, "群ごとの一覧", 11)
    body, total = g[:-1], g[-1]
    pops = []
    for r in body:
        if r[0] not in pops:
            pops.append(r[0])
    out = ["| 対象者（機械の分類） | 件数 | 判定者 1 が判定 | うち 含める・保留・除外 | 判定者 1 が判定していない（AI の予備判定だけ） | うち 含める・保留・除外 |",
           "|---|---|---|---|---|---|"]
    for p in pops + ["計"]:
        rs = [r for r in body if r[0] == p] if p != "計" else [total]
        s = [sum(r[k] for r in rs) for k in range(2, 11)]
        out.append(f"| {p} | {s[0]} | {s[1]} | {s[2]}・{s[3]}・{s[4]} | {s[5]} | {s[6]}・{s[7]}・{s[8]} |")
    return "\n".join(out)


def block_agree(wb):
    a = sheet_rows(wb, "一致の表", 9)
    vs = ("含める", "保留", "除外")
    out = ["| 判定者 1 ＼ AI の予備判定 | 含める | 保留 | 除外 | 計 |", "|---|---|---|---|---|"]
    for j in vs:
        n = [sum(1 for r in a if r[3] == j and r[5] == x) for x in vs]
        out.append(f"| {j} | {n[0]} | {n[1]} | {n[2]} | {sum(n)} |")
    n = [sum(1 for r in a if r[5] == x) for x in vs]
    out.append(f"| 計 | {n[0]} | {n[1]} | {n[2]} | {sum(n)} |")
    same = sum(1 for r in a if r[7] == "一致")
    both = [r for r in a if r[3] == "除外" and r[5] == "除外"]
    code_same = sum(1 for r in both if r[8] == "一致")
    code_skip = sum(1 for r in both if str(r[8]).startswith("比べない"))
    diff = [r for r in a if r[7] == "不一致"]
    out += ["", f"判定が一致したのは {len(a)} 件中 {same} 件です。両方が除外の {len(both)} 件のうち、除外理由（E コード）が一致したのは {code_same} 件、"
                f"判定者 1 の「E4 背景」（意図は範囲の外）で比べなかったのは {code_skip} 件です。"
                "一致の率は品質評価や κ ではありません（判定者 1 は判定の前に評価版を読んでいます）。",
            "", "判定が一致しなかった " + str(len(diff)) + " 件："
            + "／".join(f"{r[1]}（判定者 1 {r[3]}・AI {r[5]}）" for r in diff) + "。"]
    return "\n".join(out)


def block_search43():
    recs = json.load(open(C.SEARCH_RECORDS, encoding="utf-8"))
    rs = sorted((r for r in recs if re.fullmatch(r"R\d\d", r.get("reading") or "") and not r.get("overlap")), key=lambda r: r["reading"])
    out = ["| 番号 | 題名（短縮） | 年 |", "|---|---|---|"]
    out += [f"| {r['reading']} | {cell(short(r['title']))} | {r.get('year') or ''} |" for r in rs]
    return "\n".join(out)


def block_appendix(rows):
    w = openpyxl.load_workbook(C.COPY34_ARCHIVE, read_only=True)["スクリーニング"]
    a = ["## 9 付録", "", "### 9.1 34 件の判定（判定者 1）", "",
         "| ID | 題名（短縮） | 判定者1 | 用途 | 材料 |", "|---|---|---|---|---|"]
    for r in w.iter_rows(min_row=5, max_row=38, values_only=True):
        a.append(f"| {r[0]} | {cell(short(r[1]))} | {r[3]} | {field(r[9], '用途')} | {field(r[9], '材料')} |")
    ft, ta, ai = kinds(rows)
    a += ["", "### 9.2 追加候補で判定者 1 が判定した記録", "",
          "段: 全文段 = 全文段の 2 段（1 回目は問いに AI の判定を載せず、2 回目に AI の判定を見た）／題名・抄録段 = 判定者 1 の題名・抄録段の判定"
          "（問いに AI の判定を載せていない・全文段は未実施）。どちらの段でも、判定者 1 は判定の前に AI の評価版を読んでいる。"
          "除外理由の「E4 背景」は判定者 1 の選択のままで、意図は範囲の外・背景として残す（一次研究でないの意味ではない）。",
          "", "| ID | 題名（短縮） | 判定者1 | 除外理由 | 段 | 用途 | 材料 |", "|---|---|---|---|---|---|---|"]
    for r in ft + sorted(ta, key=lambda r: r["ID"]):
        g = r["除外理由"] or ""
        g = "E4 背景" if g.startswith("E4 背景") else g.split(" ")[0]
        stage = "全文段" if r in ft else "題名・抄録段"
        use = field(r["自由記入"], "用途")
        use = "未定" if use.startswith("未定") else ("保留" if use.startswith("保留") else use)
        basis = field(r["自由記入"], "材料")
        basis = "抄録" if basis.startswith("抄録（") else basis
        a.append(f"| {r['ID']} | {cell(short(r['論文タイトル']))} | {r['判定者1']} | {g or '—'} | {stage} | {use} | {basis} |")
    a += ["", "### 9.3 判定者 1 が判定していない記録（AI の予備判定だけ）", "",
          "★ 人の判定ではありません。AI（Claude）の評価版の題名・抄録段の予備判定を、そのまま写したものです。",
          "", "| ID | 題名（短縮） | AI の予備判定 | AI の除外理由 |", "|---|---|---|---|"]
    for r in sorted(ai, key=lambda r: r["ID"]):
        ta = r["AI の予備判定（題名・抄録段・評価版）"]
        # ★ E コードは AI の予備判定が除外のときだけ（含めるの件の除外理由の列は全文段の理由・判断 9 の 6）
        code = re.match(r"(E\d)", r["AI の除外理由（評価版の逐語）"] or "") if ta == "除外" else None
        a.append(f"| {r['ID']} | {cell(short(r['論文タイトル']))} | {ta} | {code.group(1) if code else '—'} |")
    return "\n".join(a)


def compose_md(cand_path=None):
    """原稿の自動の区画を作り直した文字列（★ ここでは書き戻さない）。cand_path は検査器の selftest の対照（表の写し）用。"""
    s = open(MD, encoding="utf-8").read()
    wb = load_cand(cand_path)
    rows = cand_rows(wb)
    gen = {"counts": block_counts(rows), "pop": block_pop(wb), "agree": block_agree(wb), "search43": block_search43(),
           "appendix": block_appendix(rows)}
    new = s
    for name in BLOCKS:
        b, e = f"<!-- {name}:begin -->", f"<!-- {name}:end -->"
        i, j = new.index(b), new.index(e)
        new = new[:i + len(b)] + "\n" + gen[name] + "\n" + new[j:]
    return s, new


def write_md(old, new):
    if new != old:
        C.write_text_atomic(MD, new)


def add_runs(p, text):
    for k, part in enumerate(re.split(r"\*\*", text)):
        if part:
            run = p.add_run(part)
            run.bold = (k % 2 == 1)


def set_font(doc):
    st = doc.styles["Normal"]
    st.font.name = "Yu Gothic"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")


def blocks(md):
    """Markdown を (種類, 中身) の列にする。種類: h1/h2/h3/p/li/table。"""
    out, table = [], []
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r"-+", c) for c in cells):
                table.append(cells)
            continue
        if table:
            out.append(("table", table))
            table = []
        if not line.strip() or line.strip().startswith("<!--"):
            continue
        if line.startswith("### "):
            out.append(("h3", line[4:]))
        elif line.startswith("## "):
            out.append(("h2", line[3:]))
        elif line.startswith("# "):
            out.append(("h1", line[2:]))
        elif line.startswith("- "):
            out.append(("li", line[2:]))
        else:
            out.append(("p", line))
    if table:
        out.append(("table", table))
    return out


def disp_width(s):
    """表示幅（全角・広い文字・曖昧幅 = 2、ほか = 1）。**太字**の記号は数えない。"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("F", "W", "A") else 1 for ch in s.replace("**", ""))


TABLE_CM, UNIT_CM, PAD_CM, SHORT = 16.0, 0.2, 0.5, 10


def column_widths(x):
    """表の列の幅（前のタスクと同じ規則）。短い列は 1〜2 行に収まる幅、残りを長い列に中身の平均の表示幅で配る。"""
    ncol = len(x[0])
    mean = [sum(disp_width(row[j]) for row in x) / len(x) for j in range(ncol)]
    longest = [max(disp_width(row[j]) for row in x) for j in range(ncol)]
    short_ = [lg <= 2 * SHORT for lg in longest]
    fixed = [(lg if lg <= SHORT else -(-lg // 2)) * UNIT_CM + PAD_CM for lg in longest]
    rest = TABLE_CM - sum(f for f, s in zip(fixed, short_) if s)
    weight = [min(max(m, 8.0), 40.0) for m in mean]
    wsum = sum(w for w, s in zip(weight, short_) if not s)
    if not wsum or rest < 4.0:
        weight = [min(max(m, 8.0), 40.0) if not s else f / UNIT_CM for m, s, f in zip(mean, short_, fixed)]
        return [int(Cm(TABLE_CM) * w / sum(weight)) for w in weight]
    return [int(Cm(fixed[j] if short_[j] else rest * weight[j] / wsum)) for j in range(ncol)]


def build_docx(md, dst):
    doc = Document()
    set_font(doc)
    for kind, x in blocks(md):
        if kind == "h1":
            h = doc.add_heading(x, level=0)
            h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif kind in ("h2", "h3"):
            doc.add_heading(x, level=1 if kind == "h2" else 2)
        elif kind == "li":
            add_runs(doc.add_paragraph(style="List Bullet"), x)
        elif kind == "p":
            add_runs(doc.add_paragraph(), x)
        else:
            t = doc.add_table(rows=len(x), cols=len(x[0]))
            t.style = "Table Grid"
            t.autofit = False
            for j, w in enumerate(column_widths(x)):
                t.columns[j].width = w
                for i in range(len(x)):
                    t.cell(i, j).width = w
            for i, row in enumerate(x):
                for j, c in enumerate(row):
                    t.cell(i, j).text = ""
                    add_runs(t.cell(i, j).paragraphs[0], c)
                    if i == 0:
                        for run in t.cell(i, j).paragraphs[0].runs:
                            run.bold = True
            doc.add_paragraph()
    # ★ 雛形の属性（作成日 2013 年・「generated by python-docx」）を残さない
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0, tzinfo=None)
    cp = doc.core_properties
    cp.author = cp.last_modified_by = "判定者 1"
    cp.title = DOC_TITLE
    cp.comments = cp.subject = cp.keywords = cp.category = ""
    cp.created = cp.modified = now
    cp.revision = 1
    doc.save(dst)
    neutralize_package(dst)


# ★ python-docx の雛形が持つ属性（判断 9 の 11）: 雛形の縮小画像（thumbnail）と、app.xml の Template・Application・AppVersion。
#   部品を消し、app.xml を中立の最小の形に置き換える。検査器（check_proposal.r_docx_parts）は部品の名前と app.xml を独立に確かめる。
APP_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><DocSecurity>0</DocSecurity>'
           '<LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged></Properties>')


def neutralize_package(path):
    """保存した .docx の zip から thumbnail の部品・関係・型の宣言を消し、app.xml を中立の値にする（同じフォルダで置き換える）。"""
    import zipfile
    with zipfile.ZipFile(path) as z:
        parts = [(i, z.read(i.filename)) for i in z.infolist()]
    thumbs = {i.filename for i, _ in parts if i.filename.startswith("docProps/thumbnail")}
    fd, tmp = tempfile.mkstemp(suffix=".part", dir=os.path.dirname(os.path.abspath(path)), prefix=".tmp-")
    os.close(fd)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
            for info, data in parts:
                name = info.filename
                if name in thumbs:
                    continue
                if name == "docProps/app.xml":
                    data = APP_XML.encode("utf-8")
                elif name == "_rels/.rels":
                    t = data.decode("utf-8")
                    t = re.sub(r'<Relationship [^>]*Target="/?docProps/thumbnail[^"]*"[^>]*/>', "", t)
                    data = t.encode("utf-8")
                elif name == "[Content_Types].xml":
                    t = data.decode("utf-8")
                    t = re.sub(r'<Override [^>]*PartName="/docProps/thumbnail[^"]*"[^>]*/>', "", t)
                    exts = {n.rsplit(".", 1)[-1].lower() for n in (i.filename for i, _ in parts) if n not in thumbs and "." in n}
                    for ext in ("jpeg", "jpg", "png", "emf", "wmf"):
                        if ext not in exts:  # ★ ほかに使う部品が無い画像の型の宣言だけ消す
                            t = re.sub(rf'<Default Extension="{ext}" [^>]*/>', "", t, flags=re.I)
                    data = t.encode("utf-8")
                out.writestr(info, data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def check_candidates_sha():
    """元にする追加候補の表（archive と Downloads）が記録の SHA-256 と同じ（★ 違う表から提案を作らない・判断 9 の 12）。"""
    if not os.path.exists(C.CAND_SHA_RECORD):
        sys.exit(f"追加候補の表の SHA-256 の記録が無い（止まって聞く）: {C.CAND_SHA_RECORD}")
    rec = open(C.CAND_SHA_RECORD, encoding="utf-8").read().strip()
    for p in (C.CAND_ARCHIVE, C.CAND_DOWNLOADS):
        if not os.path.exists(p) or C.sha256(p) != rec:
            sys.exit(f"追加候補の表が SHA-256 の記録と違う・無い{C.STOPPED_HINT}: {p}")


def dry_run(md):
    """作って検査し、消す（★ 判定入りの写しを %TEMP% に残さない・原稿は書き戻さない・判断 9 の 13）。"""
    import check_proposal as K
    fd, tmp = tempfile.mkstemp(suffix=".docx", prefix="proposal-dry-")
    os.close(fd)
    try:
        build_docx(md, tmp)
        src = K.sources()
        v = K.check(md, tmp, {**src, "md": md})
        sha = C.sha256(tmp)
    finally:
        os.remove(tmp)
    for x in v:
        print("違反:", x)
    print(f"dry-run: 違反 {len(v)}（作った .docx は検査の後に消した・原稿は書き戻していない・SHA-256 {sha}）")
    sys.exit(1 if v else 0)


def main(dry):
    check_candidates_sha()
    old_md, md = compose_md()
    if dry:
        dry_run(md)
        return
    last = open(SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(SHA_RECORD) else None
    for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):
        if os.path.exists(p) and C.sha256(p) != last:
            sys.exit(f".docx が SHA-256 の記録と違う{C.STOPPED_HINT}: {p}")
        if not os.path.exists(p) and last is not None:
            sys.exit(f"記録があるのに .docx が無い{C.STOPPED_HINT}: {p}")
    tmps, bak = [], None
    try:
        fd, tmp_a = tempfile.mkstemp(suffix=".part", dir=os.path.dirname(DOCX_ARCHIVE), prefix=".tmp-")
        os.close(fd)
        tmps.append(tmp_a)
        build_docx(md, tmp_a)
        fd, tmp_d = tempfile.mkstemp(suffix=".part", dir=C.DOWNLOADS, prefix=".tmp-proposal-")
        os.close(fd)
        tmps.append(tmp_d)
        shutil.copyfile(tmp_a, tmp_d)
        for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):  # ★ 置き換えの直前にもう一度
            if (os.path.exists(p) and C.sha256(p) != last) or (not os.path.exists(p) and last is not None):
                sys.exit(f".docx が SHA-256 の記録と違う・無い{C.STOPPED_HINT}: {p}")
        if os.path.exists(DOCX_DOWNLOADS):
            fd, bak = tempfile.mkstemp(suffix=".part", prefix="proposal-bak-")
            os.close(fd)
            shutil.copyfile(DOCX_DOWNLOADS, bak)
        os.replace(tmp_d, DOCX_DOWNLOADS)
        try:
            os.replace(tmp_a, DOCX_ARCHIVE)
        except OSError:
            if bak:
                shutil.copyfile(bak, DOCX_DOWNLOADS)
            else:
                os.remove(DOCX_DOWNLOADS)
            raise
        write_md(old_md, md)
        new = C.sha256(DOCX_ARCHIVE)
        if C.sha256(DOCX_DOWNLOADS) != new:
            sys.exit("archive と Downloads の .docx が合わない（SHA-256 の記録は書いていない）")
        C.write_text_atomic(SHA_RECORD, new + "\n")
    finally:
        # ★ 失敗の経路でも、一時ファイルと退避（判定入り）を残さない（判断 9 の 13）
        for t in tmps + ([bak] if bak else []):
            if os.path.exists(t):
                os.remove(t)
    print("ok", new)


if __name__ == "__main__":
    main("--dry-run" in sys.argv[1:])
