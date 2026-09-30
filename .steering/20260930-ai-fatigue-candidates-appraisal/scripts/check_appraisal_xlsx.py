"""追加候補の AI の評価版の検査（design.md「テスト戦略」）。

検査を分けて持ち、変異試験では「どの検査が単独で赤にするか」を指定して確かめる（生成物との一致の検査に隠れた空振りを防ぐ）。
  data   : 案のデータ（appraisal_data.py）。候補の一覧（candidates.py）と同じ cid の集合・語彙・整合・既存の案の節が実在するか・照合事項の番号
  rows   : 1 件ごとの 3 シートの候補番号が candidates.py と同じ順・同じ数・重複なし
  cells  : 必須の欄が空でない・語彙の中・整合（除外なら E コード・全文段と全文確認と本文の入手・中心の段と用途）
  golden : 保存して読み直した生成物（appraisal_xlsx.build()）と、すべてのシートのすべてのセルの値が一致
  words  : GSE の語・メールアドレスが無い（セルと文書のプロパティ）

使い方:
  python check_appraisal_xlsx.py <xlsx>
  python check_appraisal_xlsx.py --selftest
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STEER, "20260930-ai-fatigue-judge-file", "scripts"))
sys.path.insert(0, os.path.join(STEER, "20260929-ai-fatigue-surveys", "scripts"))
import openpyxl  # noqa: E402
import candidates as CAND  # noqa: E402
import judge_xlsx as J  # noqa: E402
import check_survey_files as S  # noqa: E402
import appraisal_data as D  # noqa: E402
import appraisal_xlsx as X  # noqa: E402

SHEETS = ["Claude評価概要", "Claude適格性評価", "Claudeスクリーニング案", "Claude方法論メモ", "Claude照合事項", "Claude評価基準"]
PER_CAND = {"Claude適格性評価": X.ELIG_HEADERS, "Claudeスクリーニング案": X.SCR_HEADERS, "Claude方法論メモ": X.METH_HEADERS}
REQUIRED = {"Claude適格性評価": ["題名", "中心範囲の段", "用途判定（Claude）", "判定根拠（プロトコル §2）", "原文確認レベル", "確認経路", "既存の AI の案（ファイルと節）"],
            "Claudeスクリーニング案": ["Claude予備判定（題名・抄録段）", "Claude予備判定（全文段）", "Claude案（現時点）", "全文確認・抽出", "中心範囲の段"],
            "Claude方法論メモ": ["研究デザイン（抄録・本文で確かめた範囲）", "懸念・限界（判定には使わない）"]}
CODE = {"背景（E2）": "E2", "背景（E4）": "E4", "除外（E1）": "E1", "除外（E3）": "E3"}
ECODE = re.compile(r"(?<![A-Za-z0-9])E[1-6](?![0-9])")
EMAIL = S.EMAIL


# ---------------------------------------------------------------- data
def check_data(A=None, C=None):
    A = D.A if A is None else A
    C = D.C if C is None else C
    errs = []
    ids = [c["cid"] for c in CAND.CANDIDATES]
    if set(A) != set(ids):
        errs.append(f"data: 案の cid が候補の一覧と違う（無い {sorted(set(ids) - set(A))[:5]}・余分 {sorted(set(A) - set(ids))[:5]}）")
    cids_c = [c[0] for c in C]
    if len(set(cids_c)) != len(cids_c):
        errs.append("data: 照合事項の番号が重複")
    for cid, e in A.items():
        where = f"data {cid}"
        for k in ("ta", "c", "b", "d"):
            if not str(e.get(k, "")).strip():
                errs.append(f"{where}: 『{k}』が空")
        if e.get("ta") not in X.TA:
            errs.append(f"{where}: 題名・抄録段の値『{e.get('ta')}』")
        if e.get("c") not in X.CENTER:
            errs.append(f"{where}: 中心範囲の段の値『{e.get('c')}』")
        if "ft" in e and e["ft"] not in ("含める", "除外", "保留"):
            errs.append(f"{where}: 全文段の値『{e['ft']}』")
        if e.get("lv", "抄録") not in X.LEVEL:
            errs.append(f"{where}: 原文確認レベル『{e.get('lv')}』")
        pk = e.get("pk") or ("なし" if e.get("p") is None else "1件")
        if pk not in X.PK:
            errs.append(f"{where}: 既存の案の種類『{pk}』")
        excl = e.get("ta") == "除外" or e.get("ft") == "除外"
        if excl:
            codes = ECODE.findall(e.get("r", ""))
            if not codes:
                errs.append(f"{where}: 除外なのに除外理由に E コードが無い")
            if e.get("c") not in CODE:
                errs.append(f"{where}: 除外なのに中心の段が背景・除外でない（{e.get('c')}）")
            elif CODE[e["c"]] not in codes:
                errs.append(f"{where}: 中心の段（{e['c']}）と除外理由の E コード（{codes}）が合わない")
        elif e.get("c") in ("除外（E1）", "除外（E3）"):
            errs.append(f"{where}: 除外していないのに中心の段が {e['c']}")
        if e.get("ta") == "保留" and not e.get("r"):
            errs.append(f"{where}: 保留なのに理由が無い")
        if e.get("c", "").startswith("中心") and e.get("ta") != "含める":
            errs.append(f"{where}: 中心の段なのに題名・抄録段が含めるでない")
        p = e.get("p")
        if (p is None) != (pk == "なし"):
            errs.append(f"{where}: 既存の案の場所と種類が合わない（{p}・{pk}）")
        if p is not None:
            key, sec, mark = p
            path = D.P.get(key)
            if path is None:
                errs.append(f"{where}: 既存の案のファイルの鍵『{key}』が無い")
                continue
            full = os.path.normpath(os.path.join(J.TASK, path))
            if not os.path.exists(full):
                errs.append(f"{where}: 既存の案のファイルが無い: {path}")
                continue
            try:
                body = "\n".join(J._section(path, sec))
            except ValueError as ex:
                errs.append(f"{where}: {ex}")
                continue
            if mark and mark not in body:
                errs.append(f"{where}: 既存の案の節 {sec} に目印『{mark}』が無い")
        for ref in re.findall(r"照合事項 (C\d\d)", " ".join(str(e.get(k, "")) for k in ("b", "k", "n", "r", "df"))):
            if ref not in cids_c:
                errs.append(f"{where}: 照合事項 {ref} が無い")
    for c in C:
        for t in re.findall(r"[A-Z]\d\d-\d\d", c[1]):
            if t not in A:
                errs.append(f"data {c[0]}: 対象の候補 {t} が案に無い")
    # 出どころ（事実のファイルの行）が今も引けること
    for c in CAND.CANDIDATES:
        try:
            J.extract(c)
        except ValueError as ex:
            errs.append(f"data {c['cid']}: 出どころを事実のファイルから引けない（{ex}）")
    return errs


# ---------------------------------------------------------------- file
def table(ws, headers):
    head = [ws.cell(4, j).value for j in range(1, len(headers) + 1)]
    rows = []
    r = X.FIRST
    while ws.cell(r, 1).value not in (None, ""):
        rows.append({h: ws.cell(r, j).value for j, h in enumerate(headers, 1)})
        r += 1
    return head, rows


def check_rows(wb):
    errs = []
    ids = [c["cid"] for c in CAND.CANDIDATES]
    if wb.sheetnames != SHEETS:
        errs.append(f"rows: シートの並びが違う {wb.sheetnames}")
        return errs
    for name, headers in PER_CAND.items():
        head, rows = table(wb[name], headers)
        if head != headers:
            errs.append(f"rows {name}: 列の見出しが違う")
        got = [r["候補番号"] for r in rows]
        if len(got) != len(set(got)):
            errs.append(f"rows {name}: 候補番号が重複")
        if got != ids:
            errs.append(f"rows {name}: 候補番号の順・数が candidates.py と違う（{len(got)} 行・最初の違い "
                        f"{next((i for i, (a, b) in enumerate(zip(got, ids)) if a != b), min(len(got), len(ids)))} 行目）")
    return errs


def check_cells(wb):
    errs = []
    if wb.sheetnames != SHEETS:
        return ["cells: シートの並びが違う"]
    tabs = {name: table(wb[name], headers)[1] for name, headers in PER_CAND.items()}
    for name, cols in REQUIRED.items():
        for r in tabs[name]:
            for h in cols:
                if not str(r.get(h) or "").strip():
                    errs.append(f"cells {name} {r['候補番号']}: 『{h}』が空")
    elig = {r["候補番号"]: r for r in tabs["Claude適格性評価"]}
    for r in tabs["Claude適格性評価"]:
        c = r["中心範囲の段"]
        if c not in X.CENTER:
            errs.append(f"cells 適格性 {r['候補番号']}: 中心範囲の段『{c}』")
        elif r["用途判定（Claude）"] != X.USE[c]:
            errs.append(f"cells 適格性 {r['候補番号']}: 用途判定『{r['用途判定（Claude）']}』が中心の段『{c}』と合わない")
        if r["原文確認レベル"] not in X.LEVEL:
            errs.append(f"cells 適格性 {r['候補番号']}: 原文確認レベル『{r['原文確認レベル']}』")
    for r in tabs["Claudeスクリーニング案"]:
        cid = r["候補番号"]
        ta, ft, final, full = r["Claude予備判定（題名・抄録段）"], r["Claude予備判定（全文段）"], r["Claude案（現時点）"], r["全文確認・抽出"]
        reason = str(r.get("除外理由") or "")
        oa = str((elig.get(cid) or {}).get("本文の入手（OpenAlex）") or "")
        for v, vocab, label in ((ta, X.TA, "題名・抄録段"), (ft, X.FT, "全文段"), (final, X.FINAL, "Claude案"), (full, X.FULLTEXT, "全文確認")):
            if v not in vocab:
                errs.append(f"cells スクリーニング {cid}: {label}『{v}』")
        if ta == "除外":
            if not ECODE.search(reason):
                errs.append(f"cells スクリーニング {cid}: 除外なのに除外理由に E コードが無い")
            if ft != "—" or full != "対象外" or final != "除外":
                errs.append(f"cells スクリーニング {cid}: 除外なのに全文段・全文確認・案が『—・対象外・除外』でない")
        elif ft == "—":
            errs.append(f"cells スクリーニング {cid}: 除外でないのに全文段が『—』")
        if ft == "除外" and not ECODE.search(reason):
            errs.append(f"cells スクリーニング {cid}: 全文段で除外なのに E コードが無い")
        if ft == "未実施" and oa == "無料の版なし":
            errs.append(f"cells スクリーニング {cid}: 無料の版が無いのに全文段が未実施")
        if full == "入手不可" and oa != "無料の版なし":
            errs.append(f"cells スクリーニング {cid}: 入手不可なのに本文の入手が『{oa}』")
        if "E6" in reason and oa != "無料の版なし":
            errs.append(f"cells スクリーニング {cid}: E6 なのに本文の入手が『{oa}』")
        if ft in ("含める", "除外", "保留") and final != ft:
            errs.append(f"cells スクリーニング {cid}: 案が全文段と違う")
        if ft in ("未実施", "—") and final != ta:
            errs.append(f"cells スクリーニング {cid}: 案が題名・抄録段と違う")
        if r["中心範囲の段"] != (elig.get(cid) or {}).get("中心範囲の段"):
            errs.append(f"cells スクリーニング {cid}: 中心の段が適格性評価のシートと違う")
    _, chk = table(wb["Claude照合事項"], X.CHK_HEADERS)
    known = {r["番号"] for r in chk}
    for r in tabs["Claudeスクリーニング案"]:
        for ref in re.findall(r"C\d\d", str(r.get("自由記入") or "")):
            if ref not in known:
                errs.append(f"cells スクリーニング {r['候補番号']}: 自由記入の {ref} が照合事項に無い")
    return errs


def values(wb):
    """シートごとのセルの値。★ 末尾の空の行と、各行の末尾の空のセルは比べない（読んで保存し直すと空の行が 1 つ増えることがある）。"""
    out = {}
    for ws in wb.worksheets:
        rows = [[c.value for c in row] for row in ws.iter_rows()]
        rows = [r[:max((i + 1 for i, v in enumerate(r) if v is not None), default=0)] for r in rows]
        while rows and not rows[-1]:
            rows.pop()
        out[ws.title] = rows
    return out


def check_golden(path, wb):
    fd, tmp = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    try:
        X.build().save(tmp)
        ref = values(openpyxl.load_workbook(tmp))
    finally:
        os.remove(tmp)
    got = values(wb)
    if list(got) != list(ref):
        return [f"golden: シートが生成物と違う {list(got)}"]
    errs = []
    for name in ref:
        if len(got[name]) != len(ref[name]):
            errs.append(f"golden {name}: 行の数が生成物と違う（{len(got[name])} 対 {len(ref[name])}）")
            continue
        for i, (a, b) in enumerate(zip(got[name], ref[name]), 1):
            if a != b:
                errs.append(f"golden {name}: {i} 行目が生成物と違う")
                break
    return errs


def check_words(wb):
    errs = []
    texts = [(f"{ws.title}!{c.coordinate}", c.value) for ws in wb.worksheets for row in ws.iter_rows() for c in row if isinstance(c.value, str)]
    p = wb.properties
    texts += [(f"プロパティ {k}", getattr(p, k)) for k in ("title", "creator", "subject", "description", "keywords") if isinstance(getattr(p, k), str)]
    for where, t in texts:
        for w in S.GSE:
            if w in t:
                errs.append(f"words {where}: GSE の語『{w}』")
        for pat in S.GSE_RE:
            m = re.search(pat, t)
            if m:
                errs.append(f"words {where}: GSE の語『{m.group(0)}』")
        if EMAIL.search(t):
            errs.append(f"words {where}: メールアドレス")
    return errs


def check(path):
    wb = openpyxl.load_workbook(path)
    return check_rows(wb) + check_cells(wb) + check_golden(path, wb) + check_words(wb)


# ---------------------------------------------------------------- selftest
def _mutate(src, fn):
    fd, tmp = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    wb = openpyxl.load_workbook(src)
    fn(wb)
    wb.save(tmp)
    return tmp


def _find(ws, cid):
    for r in range(X.FIRST, ws.max_row + 1):
        if ws.cell(r, 1).value == cid:
            return r
    raise KeyError(cid)


def _col(headers, h):
    return headers.index(h) + 1


def selftest():
    fd, base = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    X.build().save(base)
    ok = True
    runs = {"rows": check_rows, "cells": check_cells, "golden": None, "words": check_words}

    def run(kind, path):
        wb = openpyxl.load_workbook(path)
        return check_golden(path, wb) if kind == "golden" else runs[kind](wb)

    for kind in runs:
        errs = run(kind, base)
        if errs:
            ok = False
            print(f"NG 陰性対照が赤（{kind}）: {errs[:3]}")
        else:
            print(f"OK 陰性対照（生成物そのまま）が緑（{kind}）")
    E, SC, M = "Claude適格性評価", "Claudeスクリーニング案", "Claude方法論メモ"
    free_cid = next(c for c, e in D.A.items() if e["ta"] != "除外" and "lv" not in e and "ft" not in e
                    and J.oa_label(J.load_oa(), J.extract(next(x for x in CAND.CANDIDATES if x["cid"] == c))["doi"]).startswith("無料の版あり"))
    excl_cid = next(c for c, e in D.A.items() if e["ta"] == "除外")

    def delete_row(wb):
        wb[SC].delete_rows(_find(wb[SC], "S04-10"), 1)

    def swap(wb):
        ws = wb[M]
        r1, r2 = _find(ws, "S02-01"), _find(ws, "S02-02")
        for j in range(1, ws.max_column + 1):
            a, b = ws.cell(r1, j).value, ws.cell(r2, j).value
            ws.cell(r1, j).value, ws.cell(r2, j).value = b, a

    def dup(wb):
        ws = wb[E]
        ws.cell(_find(ws, "S13-02"), 1).value = "S13-01"

    def empty_basis(wb):
        ws = wb[E]
        ws.cell(_find(ws, "S14-01"), _col(X.ELIG_HEADERS, "判定根拠（プロトコル §2）")).value = None

    def bad_vocab(wb):
        ws = wb[E]
        ws.cell(_find(ws, "S14-01"), _col(X.ELIG_HEADERS, "中心範囲の段")).value = "中心-C"

    def use_mismatch(wb):
        ws = wb[E]
        ws.cell(_find(ws, "S14-01"), _col(X.ELIG_HEADERS, "用途判定（Claude）")).value = "背景保持"

    def excl_no_code(wb):
        ws = wb[SC]
        ws.cell(_find(ws, excl_cid), _col(X.SCR_HEADERS, "除外理由")).value = "疲労を測っていない"

    def unavailable_but_free(wb):
        ws = wb[SC]
        ws.cell(_find(ws, free_cid), _col(X.SCR_HEADERS, "全文確認・抽出")).value = "入手不可"

    def final_mismatch(wb):
        ws = wb[SC]
        ws.cell(_find(ws, free_cid), _col(X.SCR_HEADERS, "Claude案（現時点）")).value = "除外"

    def center_differs(wb):
        ws = wb[SC]
        ws.cell(_find(ws, free_cid), _col(X.SCR_HEADERS, "中心範囲の段")).value = "中心-A"

    def text_edit(wb):
        ws = wb[M]
        c = ws.cell(_find(ws, "S14-03"), _col(X.METH_HEADERS, "懸念・限界（判定には使わない）"))
        c.value = str(c.value) + "（書き換え）"

    def gse(wb):
        ws = wb[M]
        c = ws.cell(_find(ws, "S14-03"), _col(X.METH_HEADERS, "懸念・限界（判定には使わない）"))
        c.value = str(c.value) + " GSE の Nudge"

    def email(wb):
        wb.properties.creator = "someone@example.com"

    cases = [("rows", "1 行を消す（スクリーニング案）", delete_row), ("rows", "2 行を入れ替える（方法論メモ）", swap), ("rows", "候補番号の重複", dup),
             ("cells", "判定根拠を空に", empty_basis), ("cells", "中心の段を語彙の外に", bad_vocab), ("cells", "用途判定を中心の段と合わない値に", use_mismatch),
             ("cells", "除外の理由から E コードを消す", excl_no_code), ("cells", "無料の版があるのに入手不可", unavailable_but_free),
             ("cells", "案を全文段・題名段と違う値に", final_mismatch), ("cells", "中心の段をシートの間で食い違わせる", center_differs),
             ("golden", "懸念の文を書き換える（ほかの検査は緑のはず）", text_edit), ("words", "GSE の語を入れる", gse), ("words", "作成者にメールアドレス", email)]
    for kind, label, fn in cases:
        tmp = _mutate(base, fn)
        try:
            errs = run(kind, tmp)
        finally:
            os.remove(tmp)
        if errs:
            print(f"OK [{kind}] {label}: {errs[0]}")
        else:
            ok = False
            print(f"NG [{kind}] {label}: 赤にならなかった")
    # 陰性対照: 読んで保存し直すだけ
    tmp = _mutate(base, lambda wb: None)
    try:
        errs = check(tmp)
    finally:
        os.remove(tmp)
    print(("OK" if not errs else "NG") + f" 読んで保存し直すだけ（全部の検査が緑であること）{errs[:2]}")
    ok = ok and not errs
    os.remove(base)
    # data の変異
    import copy
    dcases = [
        ("既存の案の節の見出しを無い節に", lambda A, C: A["S02-01"].__setitem__("p", ("S-02", "## 9.", "| 1 |"))),
        ("既存の案の目印を節に無い文字列に", lambda A, C: A["S15-01"].__setitem__("p", ("S-15", "## 2.", "存在しない目印"))),
        ("案を 1 件消す", lambda A, C: A.pop("S13-20")),
        ("除外の理由の E コードと中心の段を食い違わせる（E6 はどの中心の段とも対にならない）", lambda A, C: A[excl_cid].__setitem__("r", "E6（食い違い）")),
        ("照合事項の対象に無い候補", lambda A, C: C.append(("C99", "S99-01", "x", "x", "x", "x"))),
        ("本文に無い照合事項の番号を引く", lambda A, C: A["S14-03"].__setitem__("k", "照合事項 C98 を見る")),
        ("中心の段なのに題名・抄録段が除外", lambda A, C: A["S14-03"].__setitem__("ta", "除外")),
    ]
    if check_data():
        ok = False
        print("NG data の陰性対照が赤:", check_data()[:3])
    else:
        print("OK data の陰性対照が緑")
    for label, fn in dcases:
        A, C = copy.deepcopy(D.A), copy.deepcopy(D.C)
        fn(A, C)
        errs = check_data(A, C)
        if errs:
            print(f"OK [data] {label}: {errs[0]}")
        else:
            ok = False
            print(f"NG [data] {label}: 赤にならなかった")
    print("SELFTEST PASS" if ok else "SELFTEST FAIL")
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    errs = check_data() + check(sys.argv[1])
    for e in errs:
        print("NG", e)
    print(f"違反 {len(errs)} 件")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
