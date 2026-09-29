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
   candidates.py と同じ順・要点と表記が事実のファイルから抜き出し直したものと一致し、要点の各値が事実のファイルの本文にある。
3. golden（生成物との一致）: judge_xlsx.build() が作るものと、記入欄以外のすべてのセルの値・塗り・リンク・結合・入力規則・
   条件付き書式が一致する（許す格納先の中身・語を使わない塗りで AI の判定が伝わるのを防ぐ）。
★ 語の一覧は前タスクの check_survey_files.py（SSOT）を import し、ここでは判定者用ファイル固有の語だけを足す。

使い方:
  python check_judge_xlsx.py <xlsx>
  python check_judge_xlsx.py --selftest   # 陰性対照が緑・変異がそれぞれ指定の検査で赤・出力の保護
"""
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
JUDGE_RE = S.JUDGE_RE
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
                    gpt_ok = ws.title in JUDGE_SHEETS and c.row >= 5 and c.column <= len(head) and head[c.column - 1] in bib_cols
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
    if "追加候補" in wb.sheetnames:
        ws = wb["追加候補"]
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        jp = head.index("要点（事実のファイルの記述）") + 1
        jl = head.index("事実のファイルでの表記") + 1
        cids = [c["cid"] for c in CAND.CANDIDATES]
        got = [ws.cell(r, 1).value for r in range(5, ws.max_row + 1)]
        if got != cids:
            errs.append("追加候補の番号が candidates.py と違う")
        facts = {}
        for r, c in zip(range(5, ws.max_row + 1), CAND.CANDIDATES):
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
    return errs


_GOLDEN = {}


def _val(v):
    return None if v == "" else v  # ★ 空の文字列は保存すると空（None）として読まれる


def _fill(c):
    f = c.fill
    return (f.fill_type, getattr(f.fgColor, "rgb", None)) if f is not None and f.fill_type else None


def _cf(ws):
    out = []
    for rng in ws.conditional_formatting:
        for rule in rng.rules:
            color = getattr(getattr(rule.dxf, "fill", None), "bgColor", None) if rule.dxf else None
            out.append((str(rng.sqref), tuple(rule.formula or ()), getattr(color, "rgb", None)))
    return sorted(out)


def _dv(ws):
    return sorted((str(dv.sqref), dv.type, dv.formula1) for dv in ws.data_validations.dataValidation)


def check_golden(wb):
    judge = judge_of(wb)
    if judge not in (1, 2):
        return ["『はじめに』に判定者の番号が無い"]
    if judge not in _GOLDEN:
        _GOLDEN[judge] = J.build(judge)[0]
    exp = _GOLDEN[judge]
    errs = []
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
        errs += check_golden(wb)
    return errs


# ---------------------------------------------------------------- 変異試験
def _mut_cell(sheet, coord, val):
    def f(wb):
        wb[sheet][coord].value = val
    return f


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
    ("判定シートの根拠メモに評価の語（記入欄）", _mut_cell("判定シート", "O5", "十分な研究"), "words"),
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
    ("判定シートの記入欄に判定の既定値", _mut_cell("判定シート", "J5", "含める"), "structure"),
    ("追加候補の根拠メモに記入", _mut_cell("追加候補", "O5", "メモ"), "structure"),
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
]
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
         ("書誌の列の評価の語（題名の insufficient）", _mut_cell("判定シート", "B5", "Why AI support is insufficient"), "words")]


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
        for label, fn, part in MUTANTS + GREEN:
            p = os.path.join(tmpdir, "m.xlsx")
            w = openpyxl.load_workbook(base)
            fn(w)
            w.save(p)
            hit = bool(check(p, parts=(part,)))
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
        w["判定シート"]["J5"].value = "含める"
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
