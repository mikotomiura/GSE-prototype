"""判定者用ファイルの検査（design.md「判定者用ファイル」の検査の表）。

1. 常に禁止の語（評価の語・GSE の語・AI の評価の痕跡の語）: xlsx の zip の全パーツの文字列（テキストと、人が読む属性）に 1 つも無い
2. 判定の語（含める・除外・保留・中心-A・全文段・E1〜E6 など）: 許す格納先（『判定基準』シート・判定の 2 シートの見出しの行・
   『集計』の A 列と数式・データの入力規則の式・条件付き書式の式）の外に無い。コメント・定義名・文書のプロパティ・シート名・
   ヘッダー／フッター・リンクの表示にも無い
3. 単独の GPT: 書誌と要点の列の外に無い（題名の ChatGPT は書誌なので除く）
4. 記入欄の初期値が『未判定』か空・判定シートの ID が元の DB の 34 件と同じ順・追加候補の番号が candidates.py と同じ順
5. 追加候補の要点が、事実のファイルから抜き出し直したものと一致し、各値が事実のファイルの本文にそのままある
★ 語の一覧は前タスクの check_survey_files.py（SSOT）を import し、ここでは判定者用ファイル固有の語だけを足す。

使い方:
  python check_judge_xlsx.py <xlsx>
  python check_judge_xlsx.py --selftest   # 変異（格納先ごと）がすべて赤・変異なしが緑になることを確かめる
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

EXTRA = ["Claude", "AI 予備", "AI予備", "照合事項", "スクリーニング案", "AI用途", "AI評価", "見立て", "予備判定"]
ALWAYS_WORDS = S.EVAL + S.GSE + EXTRA
ALWAYS_RE = S.EVAL_RE + S.GSE_RE + [r"R-I\d+"]
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
    """zip の全 XML パーツから、テキストと人が読む属性の値を集める（セルの座標などの属性は見ない）。"""
    out = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not (name.endswith(".xml") or name.endswith(".rels")):
                continue
            try:
                root = ET.fromstring(z.read(name))
            except ET.ParseError:
                out.append((name, "<読めない XML>"))
                continue
            for el in root.iter():
                for t in (el.text, el.tail):
                    if t and t.strip():
                        out.append((name, t))
                for k, v in el.attrib.items():
                    if k.split("}")[-1] in HUMAN_ATTRS and v.strip():
                        out.append((name, v))
    return out


def check(path):
    errs = []
    # 1. 常に禁止の語（全パーツ）＋ 2 の一部（メタデータのパーツには判定の語も無い）
    for name, t in zip_strings(path):
        for h in hits(t, ALWAYS_WORDS, ALWAYS_RE):
            errs.append(f"{name}: 常に禁止の語『{h}』")
        if META_PARTS.match(name):
            for h in hits(t, JUDGE_WORDS, JUDGE_RE) + hits(t, [], [GPT_RE]):
                errs.append(f"{name}: 判定の語・AI の名前『{h}』（メタデータ）")
    wb = openpyxl.load_workbook(path)
    # 2・3. セルの格納先ごと
    for ws in wb.worksheets:
        for h in hits(ws.title, JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
            errs.append(f"シート名『{ws.title}』: 『{h}』")
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        bib_cols = J.BIB_COLUMNS.get(ws.title, set())
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str):
                    judge_ok = (ws.title == "判定基準" or (ws.title in JUDGE_SHEETS and c.row == 4)
                                or (ws.title == "集計" and (c.column == 1 or c.data_type == "f")))
                    gpt_ok = ws.title in JUDGE_SHEETS and c.row >= 5 and c.column <= len(head) and head[c.column - 1] in bib_cols
                    if not judge_ok:
                        for h in hits(v, JUDGE_WORDS, JUDGE_RE):
                            errs.append(f"{ws.title}!{c.coordinate}: 判定の語『{h}』（許す格納先の外）")
                    if not gpt_ok:
                        for h in hits(v, [], [GPT_RE]):
                            errs.append(f"{ws.title}!{c.coordinate}: AI の名前『{h}』")
                if c.comment is not None:
                    for h in hits(c.comment.text or "", JUDGE_WORDS + ALWAYS_WORDS, JUDGE_RE + ALWAYS_RE + [GPT_RE]):
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
                for h in hits(t or "", JUDGE_WORDS, JUDGE_RE + [GPT_RE]):
                    errs.append(f"{ws.title} の入力規則の案内: 『{h}』")
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
    # 4. 初期値・ID・候補番号
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
    # 5. 追加候補の要点の出どころ
    if "追加候補" in wb.sheetnames:
        ws = wb["追加候補"]
        head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
        jp = head.index("要点（事実のファイルの記述）") + 1
        cids = [c["cid"] for c in CAND.CANDIDATES]
        got = [ws.cell(r, 1).value for r in range(5, ws.max_row + 1)]
        if got != cids:
            errs.append("追加候補の番号が candidates.py と違う")
        facts = {}
        for r, c in zip(range(5, ws.max_row + 1), CAND.CANDIDATES):
            v = ws.cell(r, jp).value or ""
            if v != J.extract(c)["points"]:
                errs.append(f"追加候補 {c['cid']}: 要点が事実のファイルから抜き出したものと違う")
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
    c = wb["判定シート"]["G5"]
    c.hyperlink.display = "含める"


def _mut_dv(wb):
    wb["判定シート"].data_validations.dataValidation[0].prompt = "E3 を選ぶ"


def _mut_dv_formula(wb):
    wb["判定シート"].data_validations.dataValidation[0].formula1 = '"未判定,含める,推奨"'


def _mut_cf(wb):
    from openpyxl.formatting.rule import FormulaRule
    wb["追加候補"].conditional_formatting.add("A5:A6", FormulaRule(formula=['A5="GSE"']))


def _mut_points(wb):
    ws = wb["追加候補"]
    head = [ws.cell(4, c).value for c in range(1, ws.max_column + 1)]
    c = ws.cell(5, head.index("要点（事実のファイルの記述）") + 1)
    c.value = c.value + " ／ 追記"


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


MUTANTS = [
    ("はじめにのセルに判定の語", _mut_cell("はじめに", "B5", "含める")),
    ("判定シートの記入欄に判定の既定値", _mut_cell("判定シート", "J5", "含める")),
    ("判定シートの根拠メモに評価の語", _mut_cell("判定シート", "O5", "十分な研究")),
    ("判定シートの根拠メモに AI の名前", _mut_cell("判定シート", "O6", "GPT-4 の案")),
    ("追加候補の根拠メモに E コード", _mut_cell("追加候補", "T5", "E2")),
    ("判定基準（許す格納先）に GSE の語", _mut_cell("判定基準", "B6", "GSE の観点")),
    ("集計の A 列に Claude", _mut_cell("集計", "A5", "Claude の数")),
    ("書誌の列に評価の語", _mut_cell("判定シート", "B5", "弱い研究")),
    ("コメント", _mut_comment),
    ("定義名", _mut_defname),
    ("文書のプロパティ title", _mut_prop("title", "判定案")),
    ("文書のプロパティ keywords", _mut_prop("keywords", "Claude")),
    ("文書のユーザー設定のプロパティ", _mut_custom),
    ("シート名", _mut_sheetname),
    ("フッター", _mut_footer),
    ("リンクの表示", _mut_link),
    ("入力規則の案内", _mut_dv),
    ("入力規則の式に評価の語", _mut_dv_formula),
    ("条件付き書式の式に GSE の語", _mut_cf),
    ("要点の改変", _mut_points),
    ("判定シートの ID の入れ替え", _mut_swap_ids),
    ("追加候補の番号の入れ替え", _mut_cand_order),
]
ZIP_MUTANTS = [
    ("docProps/app.xml の会社名", _zip_mut("docProps/app.xml", "</Properties>", "<Company>GSE</Company></Properties>")),
    # ★ openpyxl はセルの文字列をシートに直接（inlineStr）書く版がある。シートの XML に直接差し込む
    ("シートの XML に直接文字列（懸念）", _zip_mut("xl/worksheets/sheet1.xml", "</sheetData>",
                                          '<row r="999"><c r="A999" t="inlineStr"><is><t>懸念</t></is></c></row></sheetData>')),
    ("コアのプロパティを直接書き換え（Claude）", _zip_mut("docProps/core.xml", "</cp:coreProperties>",
                                                  "<dc:subject>Claude</dc:subject></cp:coreProperties>")),
]


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
        for label, fn in MUTANTS:
            p = os.path.join(tmpdir, "m.xlsx")
            w = openpyxl.load_workbook(base)
            fn(w)
            w.save(p)
            hit = bool(check(p))
            print(("OK " if hit else "NG ") + label)
            ok &= hit
        for label, fn in ZIP_MUTANTS:
            p = os.path.join(tmpdir, "z.xlsx")
            try:
                fn(base, p)
                hit = bool(check(p))
            except RuntimeError as e:  # 変異を作れない＝検査を確かめられていない → 失敗として数える
                print("   ", e)
                hit = False
            print(("OK " if hit else "NG ") + label)
            ok &= hit
        # 出力の保護（下書きの直すこと 1・3）
        filled = os.path.join(tmpdir, "filled.xlsx")
        w = openpyxl.load_workbook(base)
        w["判定シート"]["J5"].value = "含める"
        w.save(filled)
        for label, args, want_exit in (
            ("既存の出力先で止まる", (base, False), True),
            ("記入のあるファイルは --force でも止まる", (filled, True), True),
            ("記入の無いファイルは --force で進む", (base, True), False),
            ("無いディレクトリで止まる", (os.path.join(tmpdir, "nodir", "x.xlsx"), False), True),
        ):
            try:
                J.guard(*args)
                stopped = False
            except SystemExit:
                stopped = True
            good = stopped == want_exit
            print(("OK " if good else "NG ") + label)
            ok &= good
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
