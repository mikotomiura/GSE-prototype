"""理論の文献の貼れる xlsx（evidence/theory_rows.py の出力）の検査（design.md §4・§5）。

生成の道具（theory_rows.py）の関数を使わず、別に書いた規則で確かめる:
1. シートの名と、3 シートの列名が元の DB（SHA-256 固定）の同じ名のシートの 4 行目と同じ名・同じ順
2. ID が TH01〜TH23 で、3 シートで同じ順
3. DOI が期待の 23 件（S-09 の提案の表）とちょうど一致し、重複が無い
4. 書誌（題名・掲載誌・巻・号・頁・年・著者リスト）が Crossref の記録（evidence/theory/）と一致する
5. 分類が「尺度・理論」、レビューでの位置づけが「理論｜<3 群のどれか>（…）」で、期待の群と一致する
6. 自我消耗の原典の行の関連 ID に、追試・メタ分析の 5 行が入り、関連 ID が TH どうしで対称
7. セルに数式が無い・研究チームの別の研究の内部の語が無い・Crossref の記録の JSON に抄録の欄が無い

使い方:
  python check_theory_rows.py <xlsx>     # 違反があれば終了コード 1
  python check_theory_rows.py --selftest # 変異がどれも意図した理由で赤・陰性対照が緑
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
sys.path.insert(0, os.path.join(STEER, "20260929-ai-fatigue-surveys", "scripts"))
import check_survey_files as C  # noqa: E402

DB_XLSX = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                       "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
DB_SHA = "48ba8b908413fc8112ec35852d4317389500f577092e7be47384628b5f7ce8b0"
CROSSREF = os.path.join(TASK, "evidence", "theory", "crossref_2026-10-01.json")
XLSX = os.path.join(TASK, "archive", "AI_fatigue_theory_rows_2026-10-01_claude.xlsx")
SHEETS = ["文献DB", "研究情報", "書誌・出典"]

# S-09 の提案の表（../20260930-ai-fatigue-theory-and-usage/survey-S-09-ai-judgments.md §2）の文献と群
EXPECTED = [
    ("10.1017/s0140525x12003196", "疲労の仕組み"), ("10.1037/rev0000309", "疲労の仕組み"),
    ("10.1016/s0301-0511(96)05223-4", "疲労の仕組み"), ("10.1037/0022-3514.74.5.1252", "疲労の仕組み"),
    ("10.1177/1745691616652873", "疲労の仕組み"), ("10.1037/xge0000083", "疲労の仕組み"),
    ("10.1177/0956797621989733", "疲労の仕組み"), ("10.1177/1948550619887702", "疲労の仕組み"),
    ("10.1177/1088868318762183", "疲労の仕組み"), ("10.1177/0956797616654911", "疲労の仕組み"),
    ("10.1027/1864-9335/a000376", "疲労の仕組み"), ("10.1111/psyp.12339", "疲労の仕組み"),
    ("10.1177/0956797620904990", "疲労の仕組み"), ("10.1207/s15516709cog1202_4", "疲労の仕組み"),
    ("10.1201/b12791-3.1", "自動化"), ("10.1037/a0034386", "自動化"), ("10.1016/j.aap.2018.04.004", "自動化"),
    ("10.1177/0018720810376055", "自動化"), ("10.1037/0021-9010.86.3.499", "職場のストレス"),
    ("10.1108/02683940710733115", "職場のストレス"), ("10.1037/0003-066x.44.3.513", "職場のストレス"),
    ("10.1146/annurev-orgpsych-032117-104640", "職場のストレス"), ("10.2753/mis0742-1222240109", "職場のストレス"),
]
BAUMEISTER = "10.1037/0022-3514.74.5.1252"
REPLICATIONS = ["10.1177/1745691616652873", "10.1037/xge0000083", "10.1177/0956797621989733",
                "10.1177/1948550619887702", "10.1177/1088868318762183"]
POSITION = re.compile(r"^理論｜(疲労の仕組み|自動化|職場のストレス)（.+）$")


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def clean(s):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(s.split())


def expected_bib(m):
    """Crossref の記録から、検査で比べる値を作る（生成の道具とは別に書く）。"""
    year = None
    for k in ("published-print", "issued"):
        dp = (m.get(k) or {}).get("date-parts") or [[]]
        if dp and dp[0]:
            year = int(dp[0][0])
            break
    names = []
    for a in m.get("author") or []:
        n = " ".join(x for x in (a.get("given", "").strip(), a.get("family", "").strip()) if x) or a.get("name", "")
        names.append(n)
    return {"論文タイトル": clean((m.get("title") or [""])[0]), "掲載誌・媒体": clean((m.get("container-title") or [""])[0]),
            "巻号年": year, "巻": m.get("volume"), "号": m.get("issue"), "頁・論文番号": m.get("page") or m.get("article-number"),
            "著者リスト": "; ".join(names)}


def has_key(obj, key):
    if isinstance(obj, dict):
        return any(str(k).lower() == key or has_key(v, key) for k, v in obj.items())
    if isinstance(obj, list):
        return any(has_key(v, key) for v in obj)
    return False


def read_sheet(ws):
    rows = list(ws.iter_rows(values_only=True))
    head = [h for h in rows[0] if h is not None]
    return head, [dict(zip(head, r)) for r in rows[1:] if any(v is not None for v in r)]


def check(xlsx, crossref_path=CROSSREF, db=DB_XLSX):
    import openpyxl
    errs = []
    if sha256(db) != DB_SHA:
        return [f"元の DB の SHA-256 が固定値と違う: {db}"]
    cr = json.load(open(crossref_path, encoding="utf-8"))
    if has_key(cr, "abstract"):
        errs.append("Crossref の記録の JSON に抄録の欄（abstract）がある")
    recs = {k.lower(): v for k, v in cr["records"].items()}
    dbwb = openpyxl.load_workbook(db, read_only=True)
    wb = openpyxl.load_workbook(xlsx)
    if wb.sheetnames != ["はじめに"] + SHEETS:
        errs.append(f"シートの名と順が違う: {wb.sheetnames}")
        return errs
    data = {}
    for s in SHEETS:
        want = [c for c in next(dbwb[s].iter_rows(min_row=4, max_row=4, values_only=True)) if c is not None]
        head, rows = read_sheet(wb[s])
        if head != want:
            errs.append(f"『{s}』の列名が元の DB と違う: {head} ≠ {want}")
        data[s] = rows
    for s in wb.sheetnames:
        for row in wb[s].iter_rows():
            for c in row:
                if c.data_type == "f":
                    errs.append(f"『{s}』{c.coordinate} に数式がある")
                if isinstance(c.value, str):
                    for w in C.GSE:
                        if w in c.value:
                            errs.append(f"『{s}』{c.coordinate} に別の研究の内部の語『{w}』")
                    for p in C.GSE_RE:  # ★ 判断 17（code-reviewer LOW）: [Pn]・O1 などの正規表現も当てる
                        m = re.search(p, c.value)
                        if m:
                            errs.append(f"『{s}』{c.coordinate} に別の研究の内部の語『{m.group(0)}』")
    ids = [f"TH{i:02d}" for i in range(1, len(EXPECTED) + 1)]
    for s in SHEETS:
        got = [r.get("ID") for r in data[s]]
        if got != ids:
            errs.append(f"『{s}』の ID の並びが TH01〜TH{len(EXPECTED):02d} でない: {got[:5]}…")
    if errs:
        return errs
    lit, info, bibs = data["文献DB"], data["研究情報"], data["書誌・出典"]
    dois = [str(r["DOI"]).lower() for r in lit]
    if len(set(dois)) != len(dois):
        errs.append("DOI に重複がある")
    if sorted(dois) != sorted(d for d, _g in EXPECTED):
        errs.append(f"DOI の集合が期待の 23 件と違う: 余り {sorted(set(dois) - {d for d, _ in EXPECTED})}")
    by_doi = {d: i for i, d in enumerate(dois)}
    group_of = dict(EXPECTED)
    for i, r in enumerate(lit):
        d = dois[i]
        if str(bibs[i]["DOI"]).lower() != d:
            errs.append(f"{r['ID']}: 『書誌・出典』の DOI が『文献DB』と違う")
        if d not in recs:
            errs.append(f"{r['ID']}: Crossref の記録が無い: {d}")
            continue
        e = expected_bib(recs[d])
        for k in ("論文タイトル", "掲載誌・媒体", "巻号年"):
            if r[k] != e[k]:
                errs.append(f"{r['ID']}: 『文献DB』の{k}『{r[k]}』が Crossref『{e[k]}』と違う")
        for k in ("巻", "号", "頁・論文番号", "著者リスト"):
            if bibs[i][k] != e[k]:
                errs.append(f"{r['ID']}: 『書誌・出典』の{k}『{bibs[i][k]}』が Crossref『{e[k]}』と違う")
        if r["分類"] != "尺度・理論":
            errs.append(f"{r['ID']}: 分類が『尺度・理論』でない")
        m = POSITION.match(str(info[i]["レビューでの位置づけ"] or ""))
        if not m:
            errs.append(f"{r['ID']}: レビューでの位置づけが「理論｜群（…）」の形でない")
        elif d in group_of and m.group(1) != group_of[d]:
            errs.append(f"{r['ID']}: 群『{m.group(1)}』が期待の『{group_of[d]}』と違う")
    rel = {r["ID"]: set(filter(None, str(r["関連ID"] or "").split("・"))) for r in lit}
    rel_b = {r["ID"]: set(filter(None, str(r["関連ID"] or "").split("・"))) for r in bibs}
    if rel != rel_b:
        errs.append("関連 ID が『文献DB』と『書誌・出典』で違う")
    if BAUMEISTER in by_doi:
        b_id = lit[by_doi[BAUMEISTER]]["ID"]
        for d in REPLICATIONS:
            if d in by_doi:
                x = lit[by_doi[d]]["ID"]
                if x not in rel[b_id]:
                    errs.append(f"{b_id}（自我消耗の原典）の関連 ID に追試・メタ分析の {x} が無い")
    for a, xs in rel.items():
        for x in xs:
            if x.startswith("TH") and a not in rel.get(x, set()):
                errs.append(f"関連 ID が対称でない: {a} → {x}")
    return errs


def selftest():
    import openpyxl
    ok = True
    e = check(XLSX)
    print(("OK " if not e else "NG ") + "陰性対照（本物が緑）", e[:3])
    ok &= not e

    def mut(label, fn, expect, cr_fn=None):
        nonlocal ok
        with tempfile.TemporaryDirectory() as td:
            x = os.path.join(td, "t.xlsx")
            shutil.copy(XLSX, x)
            crp = CROSSREF
            if fn:
                wb = openpyxl.load_workbook(x)
                fn(wb)
                wb.save(x)
            if cr_fn:
                crp = os.path.join(td, "cr.json")
                d = json.load(open(CROSSREF, encoding="utf-8"))
                cr_fn(d)
                json.dump(d, open(crp, "w", encoding="utf-8"), ensure_ascii=False)
            e = check(x, crp)
        hit = any(expect in m for m in e)
        print(("OK " if hit else "NG ") + label, "" if hit else e[:3])
        ok &= hit

    def cell(wb, s, col, id_):
        ws = wb[s]
        head = [c.value for c in ws[1]]
        for r in ws.iter_rows(min_row=2):
            if r[0].value == id_:
                return r[head.index(col)]
        raise KeyError(id_)

    mut("列名を変える", lambda wb: setattr(wb["研究情報"]["B1"], "value", "文献名"), "『研究情報』の列名が元の DB と違う")
    mut("巻を変える", lambda wb: setattr(cell(wb, "書誌・出典", "巻", "TH05"), "value", "12"), "TH05: 『書誌・出典』の巻")
    mut("題名を変える", lambda wb: setattr(cell(wb, "文献DB", "論文タイトル", "TH01"), "value", "x"), "TH01: 『文献DB』の論文タイトル")
    mut("著者を減らす", lambda wb: setattr(cell(wb, "書誌・出典", "著者リスト", "TH19"), "value", "Evangelia Demerouti"),
        "TH19: 『書誌・出典』の著者リスト")
    mut("原典の関連 ID から追試を消す", lambda wb: [setattr(cell(wb, s, "関連ID", "TH04"), "value",
                                                 "TH06・TH07・TH08・TH09・TH10・TH11") for s in ("文献DB", "書誌・出典")],
        "関連 ID に追試・メタ分析の TH05 が無い")
    mut("関連 ID の片側だけ", lambda wb: [setattr(cell(wb, s, "関連ID", "TH13"), "value", None) for s in ("文献DB", "書誌・出典")],
        "関連 ID が対称でない: TH12 → TH13")
    mut("DOI の重複", lambda wb: [setattr(cell(wb, s, "DOI", "TH02"), "value", "10.1017/s0140525x12003196")
                                  for s in ("文献DB", "書誌・出典")], "DOI に重複がある")
    mut("群を変える", lambda wb: setattr(cell(wb, "研究情報", "レビューでの位置づけ", "TH16"), "value", "理論｜疲労の仕組み（x）"),
        "TH16: 群『疲労の仕組み』")
    mut("位置づけの形", lambda wb: setattr(cell(wb, "研究情報", "レビューでの位置づけ", "TH03"), "value", "補償的制御"),
        "TH03: レビューでの位置づけ")
    mut("ID の並び", lambda wb: setattr(cell(wb, "研究情報", "ID", "TH02"), "value", "TH99"), "『研究情報』の ID の並び")
    mut("数式", lambda wb: setattr(cell(wb, "研究情報", "限界・要確認点", "TH01"), "value", "=1+1"), "に数式がある")
    mut("内部の語", lambda wb: setattr(cell(wb, "研究情報", "限界・要確認点", "TH01"), "value", "GSE で使う"), "内部の語『GSE』")
    mut("内部の語（正規表現）", lambda wb: setattr(cell(wb, "研究情報", "限界・要確認点", "TH02"), "value", "[P362] と同じ"),
        "内部の語『[P362]』")
    mut("シートを消す", lambda wb: wb.remove(wb["書誌・出典"]), "シートの名と順が違う")
    mut("Crossref の JSON に抄録", None, "抄録の欄",
        cr_fn=lambda d: d["records"]["10.1037/rev0000309"].__setitem__("abstract", "x"))
    # 読んで保存し直すだけの対照（緑）
    with tempfile.TemporaryDirectory() as td:
        x = os.path.join(td, "t.xlsx")
        shutil.copy(XLSX, x)
        wb = openpyxl.load_workbook(x)
        wb.save(x)
        e = check(x)
    print(("OK " if not e else "NG ") + "読んで保存し直すだけの対照（緑）", e[:3])
    ok &= not e
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    path = sys.argv[1] if len(sys.argv) > 1 else XLSX
    errs = check(path)
    for m in errs:
        print("NG", m)
    print(f"違反 {len(errs)} 件")
    sys.exit(1 if errs else 0)
