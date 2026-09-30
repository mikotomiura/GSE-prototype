"""判定者用ファイルの検査（design.md「判定者用ファイル」の検査の表・decisions.md 判断 13 のレビュー対応）。

3 つの検査を別々に持ち、変異試験では「どの検査が単独で赤にするか」を指定して確かめる（ほかの検査に隠れた空振りを防ぐ）。
1. words（語の検査）
   - 常に禁止の語（評価の語・GSE の語・AI の名前と AI の評価の痕跡の語）: zip の全パーツの文字列と、セルの値（リッチテキストを
     結合した値）に 1 つも無い。読めない XML のパーツは赤。
   - 判定の語（含める・除外・保留・中心-A・全文段・E1〜E6 など）: 許す格納先（『判定基準』・判定の 2 シートの見出しの行・
     『集計』の A 列と数式）の外に無い。コメント・定義名・文書のプロパティ・シート名・ヘッダー／フッター・リンクの表示・
     入力規則の案内にも無い。
   - 単独の GPT: 書誌と要点の列の外に無い（題名の ChatGPT・GPT-4 は書誌なので書誌の列では許す）。
2. structure（構造の検査）: 記入欄の初期値が『未判定』か空・判定シートの ID が元の DB の 34 件と同じ順・追加候補の番号が
   candidates.py から寄せた記録を除いたものと同じ順・要点と表記が事実のファイルから抜き出し直したものと一致し、要点の各値が
   事実のファイルの本文にある。★ 2026-10-01（間引き）: 『寄せた記録』の鍵と代表が分けの記録（JSON）と一致・「同じ研究の群」の列が
   JSON の群の記録の行にだけあり、群の番号と群のすべての記録を書く・「内容の群」の列は判定者 1 だけにあり、値が JSON と一致する。
3. golden（生成物との一致）: judge_xlsx.build() が作るもの（一度保存して読み直したもの）と、記入欄以外のすべてのセルの値、
   すべてのセルの塗り・文字（字体名・色〈tint を含む〉・太字ほか）・表示形式・罫線・配置・リンク、結合・入力規則・条件付き書式
   （文字色を含む）・シートと行と列の表示と大きさ・表、zip のパーツの名前・リッチテキストの run の数が一致する
   （許す格納先の中身・語を使わない塗りや文字の見え方・隠す操作で AI の判定が伝わるのを防ぐ・判断 13・16・19・20）。
★ 語の一覧は前タスクの check_survey_files.py（SSOT）を import し、ここでは判定者用ファイル固有の語だけを足す。

使い方:
  python check_judge_xlsx.py <xlsx>
  python check_judge_xlsx.py --selftest   # 陰性対照が緑・変異がそれぞれ指定の検査で赤・出力の保護
"""
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "20260929-ai-fatigue-surveys", "scripts"))
import check_survey_files as S  # noqa: E402
import judge_xlsx as J  # noqa: E402
import candidates as CAND  # noqa: E402

EXTRA = ["AI 予備", "AI予備", "照合事項", "スクリーニング案", "AI用途", "AI評価", "見立て", "予備判定"]
# ★ 常に禁止（どのパーツ・どのセルでも）: GSE の語・AI の名前・AI の評価の痕跡の語
ALWAYS_WORDS = S.GSE + EXTRA
ALWAYS_RE = S.GSE_RE + [r"R-I\d+", r"(?i)claude"]
# ★ 評価の語: 書誌と要点の列（著者の語。例: 題名の「…No Longer Sufficient」）でだけ許し、ほかのセルとシート以外のパーツでは禁止
EVAL_WORDS = S.EVAL
EVAL_RE = S.EVAL_RE
SHEET_PART = re.compile(r"^xl/worksheets/sheet\d+\.xml$")
JUDGE_WORDS = S.JUDGE
# ★ 2026-10-01: 除外理由に E7（言語）を足したので、E7 も判定の語にする（前タスクの SSOT の E[1-6] は範囲の外なので、ここで足す）
JUDGE_RE = S.JUDGE_RE + [r"(?<![A-Za-z0-9])E7(?![0-9])"]
GPT_RE = r"(?<![A-Za-z])GPT(?![A-Za-z])"
HUMAN_ATTRS = {"name", "display", "tooltip", "prompt", "error", "promptTitle", "errorTitle", "title", "description", "comment"}
META_PARTS = re.compile(r"^(docProps/|customXml/|xl/workbook\.xml$|xl/comments|xl/threadedComments|xl/persons)")
JUDGE_SHEETS = ("判定シート", "追加候補")


def hits(text, words, pats):
    out = [w for w in words if w in text]
    out += [m.group(0) for p in pats for m in [re.search(p, text)] if m]
    return out


def zip_strings(path):
    """zip の全 XML パーツから、テキストと人が読む属性の値を集める（セルの座標などの属性は見ない）。読めないパーツは別に返す。"""
    out, bad = [], []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not (name.endswith(".xml") or name.endswith(".rels")):
                continue
            try:
                root = ET.fromstring(z.read(name))
            except ET.ParseError:
                bad.append(name)
                continue
            for el in root.iter():
                for t in (el.text, el.tail):
                    if t and t.strip():
                        out.append((name, t))
                for k, v in el.attrib.items():
                    if k.split("}")[-1] in HUMAN_ATTRS and v.strip():
                        out.append((name, v))
    return out, bad


def judge_of(wb):
    ws = wb["はじめに"] if "はじめに" in wb.sheetnames else None
    if ws is not None:
        for r in range(5, ws.max_row + 1):
            if ws.cell(r, 1).value == "判定者":
                m = re.search(r"判定者 (\d)", str(ws.cell(r, 2).value or ""))
                if m:
                    return int(m.group(1))
    return None


def check_words(path, wb):
    errs = []
    strings, bad = zip_strings(path)
    errs += [f"{name}: 読めない XML" for name in bad]
    for name, t in strings:
        for h in hits(t, ALWAYS_WORDS, ALWAYS_RE):
            errs.append(f"{name}: 常に禁止の語『{h}』")
        if not SHEET_PART.match(name):  # シートのセルは下でセルごとに（書誌の列を除いて）見る
            for h in hits(t, EVAL_WORDS, EVAL_RE):
                errs.append(f"{name}: 評価の語『{h}』")
        if META_PARTS.match(name):
            for h in hits(t, JUDGE_WORDS, JUDGE_RE) + hits(t, [], [GPT_RE]):
                errs.append(f"{name}: 判定の語・AI の名前『{h}』（メタデータ）")
    for ws in wb.worksheets:
        for h in hits(ws.title, JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
            errs.append(f"シート名『{ws.title}』: 『{h}』")
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        bib_cols = J.BIB_COLUMNS.get(ws.title, set())
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str):
                    for h in hits(v, ALWAYS_WORDS, ALWAYS_RE):
                        errs.append(f"{ws.title}!{c.coordinate}: 常に禁止の語『{h}』")
                    judge_ok = (ws.title == "判定基準" or (ws.title in JUDGE_SHEETS and c.row == 4)
                                or (ws.title == "集計" and (c.column == 1 or v.startswith("="))))
                    gpt_ok = c.row >= 5 and c.column <= len(head) and head[c.column - 1] in bib_cols  # 書誌の列（『寄せた記録』を含む）
                    if not gpt_ok:  # 書誌と要点の列の外では評価の語も禁止
                        for h in hits(v, EVAL_WORDS, EVAL_RE):
                            errs.append(f"{ws.title}!{c.coordinate}: 評価の語『{h}』")
                    if not judge_ok:
                        for h in hits(v, JUDGE_WORDS, JUDGE_RE):
                            errs.append(f"{ws.title}!{c.coordinate}: 判定の語『{h}』（許す格納先の外）")
                    if not gpt_ok:
                        for h in hits(v, [], [GPT_RE]):
                            errs.append(f"{ws.title}!{c.coordinate}: AI の名前『{h}』")
                if c.comment is not None:
                    for h in hits(c.comment.text or "", JUDGE_WORDS + ALWAYS_WORDS + EVAL_WORDS, JUDGE_RE + ALWAYS_RE + EVAL_RE + [GPT_RE]):
                        errs.append(f"{ws.title}!{c.coordinate} のコメント: 『{h}』")
                if c.hyperlink is not None:
                    for t in (c.hyperlink.display, c.hyperlink.tooltip):
                        for h in hits(t or "", JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
                            errs.append(f"{ws.title}!{c.coordinate} のリンクの表示: 『{h}』")
        for hf in (ws.oddHeader, ws.oddFooter, ws.evenHeader, ws.evenFooter, ws.firstHeader, ws.firstFooter):
            for part in (hf.left, hf.center, hf.right):
                for h in hits(part.text or "", JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
                    errs.append(f"{ws.title} のヘッダー／フッター: 『{h}』")
        for dv in ws.data_validations.dataValidation:
            for t in (dv.prompt, dv.error, dv.promptTitle, dv.errorTitle):
                for h in hits(t or "", JUDGE_WORDS + EVAL_WORDS, JUDGE_RE + EVAL_RE + [GPT_RE]):
                    errs.append(f"{ws.title} の入力規則の案内: 『{h}』")
            for h in hits(dv.formula1 or "", EVAL_WORDS, EVAL_RE + [GPT_RE]):  # 式の中の判定の語（選択肢）は許す
                errs.append(f"{ws.title} の入力規則の式: 『{h}』")
        for rng in ws.conditional_formatting:
            for rule in rng.rules:
                for f in rule.formula or ():
                    for h in hits(f, EVAL_WORDS, EVAL_RE + [GPT_RE]):
                        errs.append(f"{ws.title} の条件付き書式の式: 『{h}』")
    for nm, dn in wb.defined_names.items():
        for h in hits(f"{nm} {dn.attr_text or ''}", JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
            errs.append(f"定義名『{nm}』: 『{h}』")
    p = wb.properties
    for field in ("title", "subject", "creator", "keywords", "description", "category", "lastModifiedBy", "identifier", "version"):
        for h in hits(str(getattr(p, field, "") or ""), JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
            errs.append(f"文書のプロパティ {field}: 『{h}』")
    for prop in getattr(wb, "custom_doc_props", []) or []:
        for h in hits(f"{prop.name} {prop.value}", JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
            errs.append(f"文書のユーザー設定のプロパティ『{prop.name}』: 『{h}』")
    return errs


def check_structure(wb):
    errs = []
    for name in JUDGE_SHEETS:
        if name not in wb.sheetnames:
            errs.append(f"シート『{name}』が無い")
            continue
        ws = wb[name]
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        for h in J.INPUT_HEADERS:
            if h not in head:
                errs.append(f"{name}: 記入欄『{h}』が無い")
                continue
            j = head.index(h) + 1
            for r in range(5, ws.max_row + 1):
                v = ws.cell(r, j).value
                want = J.INITIAL.get(h)
                if (want and v != want) or (not want and v not in (None, "")):
                    errs.append(f"{name}!{ws.cell(r, j).coordinate}: 記入欄の初期値が『{v}』")
    if J.sha256(J.DB_XLSX) != J.DB_SHA:
        errs.append("元の DB の SHA-256 が固定値と違う")
    if "判定シート" in wb.sheetnames:
        db = openpyxl.load_workbook(J.DB_XLSX, read_only=True)["文献DB"]
        want = [r[0] for r in db.iter_rows(min_row=5, max_row=38, values_only=True)]
        got = [wb["判定シート"].cell(r, 1).value for r in range(5, 5 + len(want))]
        if got != want or wb["判定シート"].max_row != 4 + len(want):
            errs.append("判定シートの ID が元の DB の 34 件と違う")
    merged, groups, content = _dedup_expect()
    if "追加候補" in wb.sheetnames:
        ws = wb["追加候補"]
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        jp = head.index("要点（事実のファイルの記述）") + 1
        jl = head.index("事実のファイルでの表記") + 1
        kept = [c for c in CAND.CANDIDATES if c["cid"] not in merged]
        cids = [c["cid"] for c in kept]
        got = [ws.cell(r, 1).value for r in range(5, ws.max_row + 1)]
        if got != cids:
            errs.append("追加候補の番号が candidates.py から寄せた記録を除いたものと違う")
        facts = {}
        for r, c in zip(range(5, ws.max_row + 1), kept):
            e = J.extract(c)
            v = ws.cell(r, jp).value or ""
            if v != e["points"]:
                errs.append(f"追加候補 {c['cid']}: 要点が事実のファイルから抜き出したものと違う")
            if (ws.cell(r, jl).value or "") != e["label"]:
                errs.append(f"追加候補 {c['cid']}: 表記が事実のファイルから抜き出したものと違う")
            for path, _, _ in c["refs"]:
                if path not in facts:
                    facts[path] = J.strip_md(open(os.path.join(J.TASK, path), encoding="utf-8").read())
            for line in v.split("\n"):
                body = re.sub(r"^【[^】]*】", "", line)
                for seg in body.split(" ／ "):
                    val = seg.split(": ", 1)[1] if re.match(r"^[^:：]{1,20}: ", seg) else seg
                    if val and not any(val in t for t in facts.values()):
                        errs.append(f"追加候補 {c['cid']}: 要点の値が事実のファイルに無い: {val[:30]}…")
    errs += _check_dedup(wb, merged, groups, content)
    return errs


N_MERGED = 5  # dedup-259.md §2（追加候補 225 → 220）。★ 分けの記録が変わったら、ここと dedup-259.md を一緒に直す


def _dedup_expect():
    """分けの記録（JSON）を、judge_xlsx.dedup() とは別に読む: 寄せた鍵 → 代表、残る行の鍵 → 群の番号、群 → 残る行の鍵、鍵 → 内容の群。"""
    pairs = json.load(open(J.DEDUP_JSON, encoding="utf-8"))["pairs"]
    merged = {}
    for p in pairs:
        if p["cls"] == "同じ報告":
            merged[p["a"] if p["representative"] == p["b"] else p["b"]] = p["representative"]
    members = {}
    for p in pairs:
        if p["group"]:
            members.setdefault(p["group"], set()).update(merged.get(k, k) for k in (p["a"], p["b"]))
    content = {k: v["group"] for k, v in json.load(open(J.CONTENT_JSON, encoding="utf-8"))["groups"].items()}
    return merged, members, content


def _check_dedup(wb, merged, members, content):
    errs = []
    if len(merged) != N_MERGED:
        errs.append(f"寄せた記録の数が {len(merged)}（dedup-259.md は {N_MERGED}）")
    if "寄せた記録" not in wb.sheetnames:
        return errs + ["シート『寄せた記録』が無い"]
    wm = wb["寄せた記録"]
    mh = [wm.cell(4, c).value for c in range(1, wm.max_column + 1)]
    got = {wm.cell(r, 1).value: wm.cell(r, mh.index("代表（残した記録）") + 1).value for r in range(5, wm.max_row + 1)}
    if got != merged or wm.max_row != 4 + len(merged):
        errs.append("『寄せた記録』の鍵・代表が分けの記録と違う")
    in_group = {k: g for g, ks in members.items() for k in ks}
    judge = judge_of(wb)
    for name in JUDGE_SHEETS:
        if name not in wb.sheetnames:
            continue
        ws = wb[name]
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        keys = [ws.cell(r, 1).value for r in range(5, ws.max_row + 1)]
        if name == "追加候補" and set(keys) & set(merged):
            errs.append(f"追加候補に寄せた記録が残る: {sorted(set(keys) & set(merged))}")
        if J.GROUP_HEADER not in head:
            errs.append(f"{name}: 『{J.GROUP_HEADER}』の列が無い")
        else:
            j = head.index(J.GROUP_HEADER) + 1
            for r, k in zip(range(5, ws.max_row + 1), keys):
                v = ws.cell(r, j).value
                g = in_group.get(k)
                if g is None and v not in (None, ""):
                    errs.append(f"{name} {k}: 群の外の行に『{J.GROUP_HEADER}』が書かれている")
                elif g is not None and not (isinstance(v, str) and re.match(rf"{g}[:（]", v)
                                            and all(m in v for m in members[g])):
                    errs.append(f"{name} {k}: 『{J.GROUP_HEADER}』が群 {g} の番号とすべての記録を書いていない")
        has_content = J.CONTENT_HEADER in head
        if judge != 1:
            if has_content:
                errs.append(f"{name}: 判定者 {judge} のファイルに内容の群の列がある（判定者 1 だけ・判断 8）")
            continue
        if not has_content:
            errs.append(f"{name}: 判定者 1 のファイルに内容の群の列が無い")
            continue
        j = head.index(J.CONTENT_HEADER) + 1
        for r, k in zip(range(5, ws.max_row + 1), keys):
            if ws.cell(r, j).value != content.get(k):
                errs.append(f"{name} {k}: 内容の群が分けの記録と違う")
    return errs


_GOLDEN = {}


def _val(v):
    return None if v == "" else v  # ★ 空の文字列は保存すると空（None）として読まれる


def _fill(c):
    f = c.fill
    return (f.fill_type, _color(f.fgColor), _color(f.bgColor)) if f is not None and f.fill_type else None


def _color(c):
    """色の種類（rgb・theme・indexed・auto）と値に加え、tint（明るさの調整）も比べる。
    ★ tint だけを変えれば RGB が同じでも白く見せられる（2026-09-30 の /cross-review 2 巡目）。"""
    if c is None:
        return None
    return (getattr(c, "type", None), str(getattr(c, "rgb", None)), getattr(c, "theme", None), getattr(c, "indexed", None),
            getattr(c, "auto", None), getattr(c, "tint", None))


def _font(f):
    """文字の見え方（字体名・色・太字・斜体・取り消し線・下線・上下付き・大きさ）。白い文字や記号の字体で隠すなどを捉える（2026-09-30 の /cross-review・code-reviewer）。"""
    return None if f is None else (f.name, _color(f.color), f.b, f.i, f.strike, f.u, f.vertAlign, f.sz)


def _border(c):
    """罫線（太い色つきの枠で目立たせるのを捉える）。"""
    b = c.border
    if b is None:
        return None
    sides = tuple((getattr(getattr(b, n), "style", None), _color(getattr(getattr(b, n), "color", None)))
                  for n in ("left", "right", "top", "bottom", "diagonal"))
    return sides + (b.diagonalUp, b.diagonalDown, b.outline)


def _align(c):
    """配置（字下げで文字を画面の外に出す・回転などを捉える）。"""
    a = c.alignment
    return None if a is None else (a.horizontal, a.vertical, a.indent, a.textRotation, a.wrap_text, a.shrink_to_fit, a.readingOrder)


def _dxf(d):
    if d is None:
        return None
    fl = d.fill
    fill = None if fl is None else (getattr(fl, "fill_type", None), _color(getattr(fl, "fgColor", None)), _color(getattr(fl, "bgColor", None)))
    return (fill, _font(d.font), d.numFmt.formatCode if d.numFmt is not None else None)


def _cf(ws):
    """条件付き書式の範囲・種類・式・止めるか・書式（塗りだけでなく文字と表示形式も）。"""
    out = []
    for rng in ws.conditional_formatting:
        for rule in rng.rules:
            out.append((str(rng.sqref), rule.type, rule.operator, bool(rule.stopIfTrue), tuple(rule.formula or ()), repr(_dxf(rule.dxf))))
    return sorted(out)


def _layout(ws):
    """シートの非表示・行と列の非表示と大きさ・表の範囲と様式（値と塗りが同じでも、隠せば判定者に見えなくなる）。"""
    rows = sorted((k, bool(d.hidden), d.ht if d.customHeight else None, d.outlineLevel)
                  for k, d in ws.row_dimensions.items() if d.hidden or d.customHeight or d.outlineLevel)
    cols = sorted((k, d.min, d.max, bool(d.hidden), d.width if d.customWidth else None, d.outlineLevel)
                  for k, d in ws.column_dimensions.items() if d.hidden or d.customWidth or d.outlineLevel)  # ★ 既定値の列は除く（参照しただけで作られるため）
    tables = sorted((t.displayName, t.ref, getattr(t.tableStyleInfo, "name", None)) for t in ws.tables.values())
    return ws.sheet_state, rows, cols, tables


def _reload(wb):
    """生成物を一度保存して読み直す（比べる相手と同じ表現にそろえる。既定の文字色などが読み込みで付くため）。
    保存したものの zip の中身の要約（パーツの名前と、リッチテキストの run の数）も返す。"""
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    parts = _parts(buf)
    buf.seek(0)
    return openpyxl.load_workbook(buf), parts


_RUN = re.compile(r"<(?:\w+:)?r[ >]")


def _parts(src):
    """zip のパーツの名前と、共有文字列・シートの XML の中のリッチテキストの run（<r>）の数。
    ★ コメント・図・画像の追加はパーツの名前で、1 つの run だけの白い文字などは run の数で捉える（既定の読み込みでは平文に
    まとめられて値も同じになるため・2026-09-30 の code-reviewer）。"""
    with zipfile.ZipFile(src) as z:
        names = sorted(z.namelist())
        runs = {n: len(_RUN.findall(z.read(n).decode("utf-8", "replace")))
                for n in names if n == "xl/sharedStrings.xml" or n.startswith("xl/worksheets/sheet")}
    return names, runs


def _dv(ws):
    return sorted((str(dv.sqref), dv.type, dv.formula1) for dv in ws.data_validations.dataValidation)


def check_golden(wb, path=None):
    judge = judge_of(wb)
    if judge not in (1, 2):
        return ["『はじめに』に判定者の番号が無い"]
    if judge not in _GOLDEN:
        _GOLDEN[judge] = _reload(J.build(judge)[0])
    exp, exp_parts = _GOLDEN[judge]
    errs = []
    if path is not None:
        names, runs = _parts(path)
        if names != exp_parts[0]:
            errs.append(f"zip のパーツが生成物と違う: 増えた {sorted(set(names) - set(exp_parts[0]))}・減った {sorted(set(exp_parts[0]) - set(names))}")
        if runs != exp_parts[1]:
            errs.append("リッチテキストの run が生成物と違う")
    if wb.sheetnames != exp.sheetnames:
        return [f"シートの並びが生成物と違う: {wb.sheetnames}"]
    for name in exp.sheetnames:
        a, e = wb[name], exp[name]
        if (a.max_row, a.max_column) != (e.max_row, e.max_column):
            errs.append(f"{name}: 大きさが生成物と違う")
            continue
        head = [e.cell(4, c).value for c in range(1, e.max_column + 1)]
        inputs = {head.index(h) + 1 for h in J.INPUT_HEADERS if h in head} if name in JUDGE_SHEETS else set()
        for row in e.iter_rows():
            for ce in row:
                ca = a[ce.coordinate]
                is_input = ce.row >= 5 and ce.column in inputs
                if not is_input and _val(ca.value) != _val(ce.value):
                    errs.append(f"{name}!{ce.coordinate}: 値が生成物と違う")
                if _fill(ca) != _fill(ce):
                    errs.append(f"{name}!{ce.coordinate}: 塗りが生成物と違う")
                if _font(ca.font) != _font(ce.font) or ca.number_format != ce.number_format:
                    errs.append(f"{name}!{ce.coordinate}: 文字または表示形式が生成物と違う")
                if _border(ca) != _border(ce):
                    errs.append(f"{name}!{ce.coordinate}: 罫線が生成物と違う")
                if _align(ca) != _align(ce):
                    errs.append(f"{name}!{ce.coordinate}: 配置が生成物と違う")
                ta = ca.hyperlink.target if ca.hyperlink is not None else None
                te = ce.hyperlink.target if ce.hyperlink is not None else None
                if ta != te:
                    errs.append(f"{name}!{ce.coordinate}: リンクが生成物と違う")
        if sorted(map(str, a.merged_cells.ranges)) != sorted(map(str, e.merged_cells.ranges)):
            errs.append(f"{name}: 結合が生成物と違う")
        if _dv(a) != _dv(e):
            errs.append(f"{name}: 入力規則が生成物と違う")
        if _cf(a) != _cf(e):
            errs.append(f"{name}: 条件付き書式が生成物と違う")
        if _layout(a) != _layout(e):
            errs.append(f"{name}: シート・行・列の表示または表が生成物と違う")
    return errs


def check(path, parts=("words", "structure", "golden")):
    try:
        wb = openpyxl.load_workbook(path)
    except Exception as e:  # noqa: BLE001  読めないファイルは赤（語の検査の zip の走査だけは返す）
        strings, bad = zip_strings(path)
        return [f"openpyxl で読めない（{type(e).__name__}）"] + [f"{n}: 読めない XML" for n in bad]
    errs = []
    if "words" in parts:
        errs += check_words(path, wb)
    if "structure" in parts:
        errs += check_structure(wb)
    if "golden" in parts:
        errs += check_golden(wb, path)
    return errs


# ---------------------------------------------------------------- 変異試験
def _mut_cell(sheet, coord, val):
    def f(wb):
        wb[sheet][coord].value = val
    return f


def _addr(ws, header, key=None, row=5):
    """見出しの名前（と A 列の鍵）でセルの座標を引く（★ 2026-10-01: 列を足して座標がずれ、変異が別の列に当たって空振りしないように）。"""
    head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
    if key is not None:
        row = [ws.cell(r, 1).value for r in range(1, ws.max_row + 1)].index(key) + 1
    return f"{J.col(head.index(header) + 1)}{row}"


def _mut_at(sheet, header, val, key=None, row=5):
    def f(wb):
        wb[sheet][_addr(wb[sheet], header, key, row)].value = val
    return f


def _mut_judge2(wb):
    """判定者 1 のファイルの『はじめに』の番号だけを 2 にする（内容の群の列が残る）。"""
    ws = wb["はじめに"]
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "判定者":
            ws.cell(r, 2).value = "判定者 2"
            return
    raise RuntimeError("『はじめに』に判定者の行が無い（変異が空振りする）")


def _mut_comment(wb):
    from openpyxl.comments import Comment
    wb["判定シート"]["B5"].comment = Comment("中心-A と思う", "x")


def _mut_defname(wb):
    from openpyxl.workbook.defined_name import DefinedName
    wb.defined_names["memo"] = DefinedName("memo", attr_text='"保留"')


def _mut_prop(field, val):
    def f(wb):
        setattr(wb.properties, field, val)
    return f


def _mut_custom(wb):
    from openpyxl.packaging.custom import StringProperty
    wb.custom_doc_props.append(StringProperty(name="note", value="除外"))


def _mut_sheetname(wb):
    wb["集計"].title = "除外の集計"


def _mut_footer(wb):
    wb["判定シート"].oddFooter.center.text = "GPT の案"


def _mut_link(wb):
    wb["判定シート"]["G5"].hyperlink.display = "含める"


def _mut_dv_prompt(wb):
    wb["判定シート"].data_validations.dataValidation[0].prompt = "E3 を選ぶ"


def _mut_dv_formula(wb):
    wb["判定シート"].data_validations.dataValidation[0].formula1 = '"未判定,含める,推奨"'


def _mut_dv_formula_plain(wb):
    wb["判定シート"].data_validations.dataValidation[0].formula1 = '"含める,未判定"'  # 語は許す格納先の中・並びだけ違う


def _mut_cf_word(wb):
    from openpyxl.formatting.rule import FormulaRule
    wb["追加候補"].conditional_formatting.add("A5:A6", FormulaRule(formula=['A5="GSE"']))


def _mut_cf_row(wb):
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import PatternFill
    wb["追加候補"].conditional_formatting.add(
        "A7:P7", FormulaRule(formula=['$A7="S14-03"'], fill=PatternFill("solid", fgColor="FFD1FAE5", bgColor="FFD1FAE5")))


def _mut_static_fill(wb):
    from openpyxl.styles import PatternFill
    wb["判定シート"]["B6"].fill = PatternFill("solid", fgColor="FFD1FAE5")


def _mut_points(wb):
    ws = wb["追加候補"]
    head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
    c = ws.cell(5, head.index("要点（事実のファイルの記述）") + 1)
    c.value = c.value + " ／ 追記"


def _mut_label(wb):
    ws = wb["追加候補"]
    head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
    c = ws.cell(6, head.index("事実のファイルでの表記") + 1)
    c.value = (c.value or "") + "（重い）"


def _mut_swap_ids(wb):
    ws = wb["判定シート"]
    ws["A5"].value, ws["A6"].value = ws["A6"].value, ws["A5"].value


def _mut_cand_order(wb):
    ws = wb["追加候補"]
    ws["A5"].value, ws["A6"].value = ws["A6"].value, ws["A5"].value


def _mut_hide_row(wb):
    wb["追加候補"].row_dimensions[7].hidden = True


def _mut_white_font(wb):
    from openpyxl.styles import Font
    c = wb["追加候補"]["I7"]
    c.font = Font(name=c.font.name, size=c.font.sz, color="FFFFFFFF")


def _mut_font_tint(wb):
    """文字の RGB は同じまま tint だけを変える（白に近く見える）。"""
    import copy
    c = wb["追加候補"]["I7"]
    f, col = copy.copy(c.font), copy.copy(c.font.color)
    col.tint = 0.95
    f.color = col
    c.font = f


def _mut_fill_tint(wb):
    """入力欄の塗りの RGB は同じまま tint だけを変える。"""
    import copy
    c = wb["追加候補"][_addr(wb["追加候補"], "題名・抄録段", row=7)]
    fl, col = copy.copy(c.fill), copy.copy(c.fill.fgColor)
    col.tint = -0.5
    fl.fgColor = col
    c.fill = fl


def _mut_numfmt(wb):
    wb["追加候補"]["I7"].number_format = ";;;"


def _mut_hide_sheet(wb):
    wb["追加候補"].sheet_state = "hidden"


def _mut_col_width(wb):
    # ★ openpyxl は幅 0 を書き出さない（読み直すと既定の幅になる）ので、0.1 で「ほぼ見えない列」を作る（code-reviewer LOW）
    wb["追加候補"].column_dimensions["I"].width = 0.1


def _mut_rich_white(wb):
    """要点のセルを、白い文字の run 1 つのリッチテキストにする（既定の読み込みでは平文と同じ値になる）。"""
    from openpyxl.cell.rich_text import CellRichText, TextBlock
    from openpyxl.cell.text import InlineFont
    c = wb["追加候補"]["I7"]
    c.value = CellRichText([TextBlock(InlineFont(color="FFFFFFFF"), c.value)])


def _mut_border(wb):
    from openpyxl.styles import Border, Side
    s = Side(style="thick", color="FFFF0000")
    wb["追加候補"]["C7"].border = Border(left=s, right=s, top=s, bottom=s)


def _mut_comment_mark(wb):
    """語を含まないコメント（印だけ）を付ける。"""
    from openpyxl.comments import Comment
    wb["追加候補"]["A7"].comment = Comment("*", "a")


def _mut_font_name(wb):
    import copy
    c = wb["追加候補"]["I7"]
    f = copy.copy(c.font)
    f.name = "Wingdings"
    c.font = f


def _mut_indent(wb):
    import copy
    c = wb["追加候補"]["I7"]
    a = copy.copy(c.alignment)
    a.indent = 200
    c.alignment = a


def _mut_cf_font(wb):
    """既存の条件付き書式の文字色だけを変える（塗り・式・範囲は同じ）。
    ★ 書式の定義は読み込み後に 2 枚のシートの条件付き書式で共有されるので、両方のシートが赤になる。"""
    from openpyxl.styles import Font
    for rng in wb["判定シート"].conditional_formatting:
        for rule in rng.rules:
            rule.dxf.font = Font(color="FFFFFFFF")
            return
    raise RuntimeError("判定シートに条件付き書式が無い（変異が空振りする）")


def _mut_dv_drop_e7(wb):
    """除外理由の入力規則から E7 を落とす（語は許す格納先の中・選択肢だけが違う）。"""
    for dv in wb["判定シート"].data_validations.dataValidation:
        if dv.formula1 and "E7" in dv.formula1:
            dv.formula1 = dv.formula1.replace(",E7", "")
            return
    raise RuntimeError("除外理由の入力規則（E7 を含む）が無い")


def _mut_scale_row(wb):
    """『判定基準』の尺度の原著の読み方を、字面どおりの読み（尺度の開発は全部 E4）に書き換える。"""
    ws = wb["判定基準"]
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, 1).value == "E4 の『尺度の原著』（2026-10-01）":
            ws.cell(r, 2).value = "尺度を開発・検証した研究は、AI に関わるものも E4 とする。"
            return
    raise RuntimeError("『判定基準』に尺度の原著の行が無い")


def _zip_mut(part, find, repl):
    """zip のパーツを直接書き換える変異（openpyxl を通らない格納先）。"""
    def f(src, dst):
        with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
            if part not in zi.namelist():  # ★ パーツが無いと変異が空振りして緑になる（2026-09-30 に実際に起きた）
                raise RuntimeError(f"変異の対象のパーツが無い: {part}")
            for item in zi.infolist():
                data = zi.read(item.filename)
                if item.filename == part:
                    s = data.decode("utf-8")
                    if find not in s:
                        raise RuntimeError(f"{part} に {find} が無い")
                    data = s.replace(find, repl, 1).encode("utf-8")
                zo.writestr(item, data)
    return f


# (名前, 変異, 単独で赤にするべき検査)。★ words の変異は、ほかの検査を使わずに words だけで赤になることを確かめる
MUTANTS = [
    ("はじめにのセルに判定の語", _mut_cell("はじめに", "B7", "含める"), "words"),
    ("判定シートの公表区分に GPT（書誌でも記入欄でもない列）", _mut_cell("判定シート", "F5", "GPT の分類"), "words"),
    ("追加候補の出どころに E コード（書誌でも記入欄でもない列）", _mut_cell("追加候補", "B5", "S-02 §2 E2"), "words"),
    ("判定シートの根拠メモに評価の語（記入欄）", _mut_at("判定シート", "根拠メモ", "十分な研究"), "words"),
    ("寄せた記録の一致点に評価の語（書誌でない列）", _mut_at("寄せた記録", "一致点", "弱い一致"), "words"),
    ("同じ研究の群の列に判定の語", _mut_at("追加候補", J.GROUP_HEADER, "G04: S04-15・S04-27 ／ E5", key="S04-15"), "words"),
    ("内容の群の列に AI の名前", _mut_at("追加候補", J.CONTENT_HEADER, "GPT の分類", key="S04-15"), "words"),
    ("判定基準（許す格納先）に GSE の語", _mut_cell("判定基準", "B6", "GSE の観点"), "words"),
    ("集計の A 列に AI の名前（小文字）", _mut_cell("集計", "A5", "claude の数"), "words"),
    ("記入欄でも書誌でもない列に評価の語", _mut_cell("判定シート", "I5", "弱い研究"), "words"),
    ("コメント", _mut_comment, "words"),
    ("定義名", _mut_defname, "words"),
    ("文書のプロパティ title", _mut_prop("title", "判定案"), "words"),
    ("文書のプロパティ keywords", _mut_prop("keywords", "Claude"), "words"),
    ("文書のユーザー設定のプロパティ", _mut_custom, "words"),
    ("シート名", _mut_sheetname, "words"),
    ("フッター", _mut_footer, "words"),
    ("リンクの表示", _mut_link, "words"),
    ("入力規則の案内", _mut_dv_prompt, "words"),
    ("入力規則の式に評価の語", _mut_dv_formula, "words"),
    ("条件付き書式の式に GSE の語", _mut_cf_word, "words"),
    ("判定シートの記入欄に判定の既定値", _mut_at("判定シート", "題名・抄録段", "含める"), "structure"),
    ("追加候補の根拠メモに記入", _mut_at("追加候補", "根拠メモ", "メモ"), "structure"),
    # ★ 2026-10-01（間引き）
    ("寄せた記録が追加候補に残る", _mut_cell("追加候補", "A5", "S12-12"), "structure"),
    ("寄せた記録の代表を変える", _mut_at("寄せた記録", "代表（残した記録）", "S04-48"), "structure"),
    ("群の記録の行の群の列を消す", _mut_at("判定シート", J.GROUP_HEADER, None, key="AF006"), "structure"),
    ("群の外の行に群を書く", _mut_at("判定シート", J.GROUP_HEADER, "G01: AF006・AF007・AF009", key="AF001"), "structure"),
    ("群の番号を取り違える", _mut_at("追加候補", J.GROUP_HEADER, "G05: S04-15・S04-27 ／ 一致点: 著者 2 名", key="S04-15"), "structure"),
    ("群の文から記録を 1 つ落とす", _mut_at("判定シート", J.GROUP_HEADER, "G01: AF006・AF007 ／ 一致点: 著者 2 名", key="AF009"), "structure"),
    ("内容の群の値を変える", _mut_at("追加候補", J.CONTENT_HEADER, "レビュー等", key="S04-15"), "structure"),
    ("判定者 2 のファイルに内容の群の列", _mut_judge2, "structure"),
    ("要点の改変", _mut_points, "structure"),
    ("表記の改変", _mut_label, "structure"),
    ("判定シートの ID の入れ替え", _mut_swap_ids, "structure"),
    ("追加候補の番号の入れ替え", _mut_cand_order, "structure"),
    ("判定基準の中身（許す格納先）に候補の判定の式", _mut_cell("判定基準", "B7", '="S14-03 は除外"'), "golden"),
    ("集計の式（許す格納先）を変える", _mut_cell("集計", "B5", '=COUNTIF(\'追加候補\'!J5:J9,"含める")'), "golden"),
    ("条件付き書式で行に色（語を使わない）", _mut_cf_row, "golden"),
    ("書誌のセルに塗り（語を使わない）", _mut_static_fill, "golden"),
    ("入力規則の並びを変える（語は許す格納先の中）", _mut_dv_formula_plain, "golden"),
    ("書誌の列に評価の語（語の検査では許す列）", _mut_cell("判定シート", "B5", "弱い研究"), "golden"),
    # ★ 語も塗りも使わずに候補を隠す・目立たせる変異（2026-09-30 の /cross-review・判断 16）
    ("追加候補の行を非表示", _mut_hide_row, "golden"),
    ("要点の文字を白に（値と塗りは同じ）", _mut_white_font, "golden"),
    ("表示形式で値を隠す（;;;）", _mut_numfmt, "golden"),
    ("追加候補のシートを非表示", _mut_hide_sheet, "golden"),
    ("要点の列の幅を 0 に", _mut_col_width, "golden"),
    ("条件付き書式の文字色だけを変える", _mut_cf_font, "golden"),
    ("文字色の tint だけを変える（RGB は同じ）", _mut_font_tint, "golden"),
    ("入力欄の塗りの tint だけを変える（RGB は同じ）", _mut_fill_tint, "golden"),
    # ★ 2026-09-30 の code-reviewer（2 回目）: 語も塗りも使わずに隠す・目立たせる残りの手段
    ("要点を白い文字の run のリッチテキストに", _mut_rich_white, "golden"),
    ("表記のセルを太い赤の罫線で囲む", _mut_border, "golden"),
    ("語を含まないコメント（印だけ）", _mut_comment_mark, "golden"),
    ("要点の字体を記号の字体に", _mut_font_name, "golden"),
    ("要点を字下げで画面の外に", _mut_indent, "golden"),
    # ★ 2026-10-01: E7 と尺度の原著の読み方（../20261001-ai-fatigue-protocol-cont 判断 1）
    ("『はじめに』に E7（判定の語）", _mut_cell("はじめに", "B7", "E7 の記録は読まない"), "words"),
    ("除外理由の選択肢から E7 を落とす", _mut_dv_drop_e7, "golden"),
    ("尺度の原著の読み方を字面どおりに書き換える", _mut_scale_row, "golden"),
]
# ★ golden の変異が「意図した理由」で赤になることを確かめる（メッセージの一部・code-reviewer LOW）
EXPECT = {
    "追加候補の行を非表示": "表示または表", "要点の文字を白に（値と塗りは同じ）": "文字または表示形式",
    "表示形式で値を隠す（;;;）": "文字または表示形式", "追加候補のシートを非表示": "表示または表",
    "要点の列の幅を 0 に": "表示または表", "条件付き書式の文字色だけを変える": "条件付き書式",
    "文字色の tint だけを変える（RGB は同じ）": "文字または表示形式", "入力欄の塗りの tint だけを変える（RGB は同じ）": "塗り",
    "要点を白い文字の run のリッチテキストに": "リッチテキスト", "表記のセルを太い赤の罫線で囲む": "罫線",
    "語を含まないコメント（印だけ）": "zip のパーツ", "要点の字体を記号の字体に": "文字または表示形式", "要点を字下げで画面の外に": "配置",
    # ★ 2026-10-01: 間引きの structure の変異も、意図した理由で赤になることを確かめる
    "寄せた記録が追加候補に残る": "寄せた記録が残る", "寄せた記録の代表を変える": "『寄せた記録』の鍵・代表",
    "群の記録の行の群の列を消す": "群 G01 の番号", "群の外の行に群を書く": "群の外の行",
    "群の番号を取り違える": "群 G04 の番号", "群の文から記録を 1 つ落とす": "群 G01 の番号",
    "内容の群の値を変える": "内容の群が分けの記録と違う", "判定者 2 のファイルに内容の群の列": "内容の群の列がある",
    "『はじめに』に E7（判定の語）": "判定の語『E7』", "除外理由の選択肢から E7 を落とす": "入力規則が生成物と違う",
    "尺度の原著の読み方を字面どおりに書き換える": "判定基準!B",
}
ZIP_MUTANTS = [
    ("docProps/app.xml の会社名", _zip_mut("docProps/app.xml", "</Properties>", "<Company>GSE</Company></Properties>"), "words"),
    ("シートの XML に直接文字列（懸念）", _zip_mut("xl/worksheets/sheet1.xml", "</sheetData>",
                                          '<row r="999"><c r="A999" t="inlineStr"><is><t>懸念</t></is></c></row></sheetData>'), "words"),
    ("コアのプロパティを直接書き換え（Claude）", _zip_mut("docProps/core.xml", "</cp:coreProperties>",
                                                  "<dc:subject>Claude</dc:subject></cp:coreProperties>"), "words"),
    ("読めない XML のパーツ", _zip_mut("docProps/app.xml", "</Properties>", "</Properties><broken"), "words"),
]
# 陽性対照（赤にならないこと）: 書誌の列の GPT-4・評価の語（著者の語）は words で緑
GREEN = [("書誌の列の GPT-4（題名）", _mut_cell("判定シート", "B5", "Evaluating GPT-4 in writing"), "words"),
         ("書誌の列の評価の語（題名の insufficient）", _mut_cell("判定シート", "B5", "Why AI support is insufficient"), "words"),
         ("寄せた記録の題名の GPT-4・insufficient（書誌の列）", _mut_at("寄せた記録", "題名（書誌の記録）", "GPT-4 is insufficient"), "words"),
         # ★ 読んで保存し直すだけで golden が赤なら、golden の変異は保存し直しの差で赤になっている（空振り）
         ("変異なしで読んで保存し直す", lambda wb: None, "golden")]


def selftest():
    ok = True
    tmpdir = tempfile.mkdtemp(prefix="judge-selftest-")
    try:
        base = os.path.join(tmpdir, "base.xlsx")
        wb, _ = J.build(1)
        wb.save(base)
        e0 = check(base)
        print(("OK " if not e0 else "NG ") + f"変異なし（陰性対照）: 違反 {len(e0)} 件")
        for e in e0[:10]:
            print("   ", e)
        ok &= not e0
        # ★ 2026-10-01: 判定者 2 のファイル（内容の群の列が無い）も陰性対照で緑
        base2 = os.path.join(tmpdir, "base2.xlsx")
        J.build(2)[0].save(base2)
        e2 = check(base2)
        print(("OK " if not e2 else "NG ") + f"判定者 2 の変異なし（陰性対照）: 違反 {len(e2)} 件")
        for e in e2[:10]:
            print("   ", e)
        ok &= not e2
        for label, fn, part in MUTANTS + GREEN:
            p = os.path.join(tmpdir, "m.xlsx")
            w = openpyxl.load_workbook(base)
            fn(w)
            w.save(p)
            errs = check(p, parts=(part,))
            hit = bool(errs) and (label not in EXPECT or any(EXPECT[label] in e for e in errs))
            want = (label, fn, part) not in GREEN
            print(("OK " if hit == want else "NG ") + f"[{part}] {label}" + ("" if want else "（緑であること）"))
            ok &= hit == want
        for label, fn, part in ZIP_MUTANTS:
            p = os.path.join(tmpdir, "z.xlsx")
            try:
                fn(base, p)
                hit = bool(check(p, parts=(part,)))
            except RuntimeError as e:  # 変異を作れない＝検査を確かめられていない → 失敗として数える
                print("   ", e)
                hit = False
            print(("OK " if hit else "NG ") + f"[{part}] {label}")
            ok &= hit
        # 出力の保護（下書きの直すこと 1・3・security L-2）
        filled = os.path.join(tmpdir, "filled.xlsx")
        w = openpyxl.load_workbook(base)
        w["判定シート"][_addr(w["判定シート"], "題名・抄録段")].value = "含める"
        w.save(filled)
        cases = [
            ("既存の出力先で止まる", lambda: J.guard(base, False), True),
            ("記入のあるファイルは --force でも止まる", lambda: J.guard(filled, True), True),
            ("記入の無いファイルは --force で進む", lambda: J.guard(base, True), False),
            ("無いディレクトリで止まる", lambda: J.guard(os.path.join(tmpdir, "nodir", "x.xlsx"), False), True),
            ("置く直前に記入があれば止まる（place）", lambda: J.place(base, filled, True), True),
        ]
        for label, fn, want_exit in cases:
            try:
                fn()
                stopped = False
            except SystemExit:
                stopped = True
            good = stopped == want_exit
            print(("OK " if good else "NG ") + label)
            ok &= good
        # ★ 2026-10-01: 判定者に写す文（dedup-259.md）と分けの記録（JSON）が食い違えば、生成が止まる
        md_src = open(J.DEDUP_MD, encoding="utf-8").read()
        md_cases = [
            ("群の記録から 1 件落とすと止まる", "| G04 | S04-15・S04-27 |", "| G04 | S04-15 |"),
            ("代表を変えると止まる", "| S04-79（medRxiv の前刷り） | S04-61", "| S04-79（medRxiv の前刷り） | S04-49"),
            ("群を 1 つ消すと止まる", "| G11 | S14-05・S15-05 |", "| X11 | S14-05・S15-05 |"),
        ]
        saved = J.DEDUP_MD
        for label, find, repl in md_cases:
            p = os.path.join(tmpdir, "dedup.md")
            if find not in md_src:
                print("NG " + label + "（変異の対象が無い）")
                ok = False
                continue
            open(p, "w", encoding="utf-8").write(md_src.replace(find, repl, 1))
            J.DEDUP_MD = p
            try:
                J.dedup()
                stopped = False
            except ValueError:
                stopped = True
            finally:
                J.DEDUP_MD = saved
            print(("OK " if stopped else "NG ") + label)
            ok &= stopped
        # --force で置き換えると旧ファイルが退避される
        dst = os.path.join(tmpdir, "dst.xlsx")
        shutil.copyfile(base, dst)
        J.place(base, dst, True)
        backed = any(n.startswith("dst.xlsx.bak-") for n in os.listdir(tmpdir))
        print(("OK " if backed else "NG ") + "--force で旧ファイルを退避する")
        ok &= backed
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    es = check(sys.argv[1])
    for e in es:
        print("NG", e)
    print(f"違反 {len(es)} 件")
    sys.exit(1 if es else 0)
