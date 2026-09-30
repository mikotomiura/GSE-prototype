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
        elif e.get("c") in CODE:
            errs.append(f"{where}: 除外していないのに中心の段が {e['c']}（背景・除外は題名・抄録段か全文段で除外する）")
        if e.get("lv") == "本文関連箇所確認" and e.get("ta") != "除外" and "ft" not in e:
            errs.append(f"{where}: 本文を読んだ記録があるのに全文段の案（ft）が無い（未実施・E6 に落ちる）")
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
        targets = re.findall(r"[A-Z]\d\d-\d\d", c[1])
        for t in targets:
            if t not in A:
                errs.append(f"data {c[0]}: 対象の候補 {t} が案に無い")
        # 照合事項の「扱いの案」と各行の値が合うこと（「どちらも E2 の見立て」「どちらも境界（保留）」「どちらも計画として保留」）
        m = re.search(r"どちらも (E\d) の見立て", c[4])
        for t in targets:
            if t not in A:
                continue
            if m and m.group(1) not in ECODE.findall(A[t].get("r", "")):
                errs.append(f"data {c[0]}: 扱いの案は {m.group(1)} の見立てだが、{t} の除外理由は『{A[t].get('r', '')}』")
            if "どちらも境界（保留）" in c[4] and A[t].get("c") != "境界（保留）":
                errs.append(f"data {c[0]}: 扱いの案は境界（保留）だが、{t} の中心の段は {A[t].get('c')}")
            if "どちらも計画として保留" in c[4] and A[t].get("ta") != "保留":
                errs.append(f"data {c[0]}: 扱いの案は保留だが、{t} の題名・抄録段は {A[t].get('ta')}")
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
        link = wb["Claude適格性評価"].cell(X.FIRST + tabs["Claude適格性評価"].index(r), X.ELIG_HEADERS.index("DOI") + 1).hyperlink
        if (link is not None) != bool(r.get("DOI")):
            errs.append(f"cells 適格性 {r['候補番号']}: DOI とリンクの有無が合わない")
    for r in tabs["Claudeスクリーニング案"]:
        cid = r["候補番号"]
        ta, ft, final, full = r["Claude予備判定（題名・抄録段）"], r["Claude予備判定（全文段）"], r["Claude案（現時点）"], r["全文確認・抽出"]
        reason = str(r.get("除外理由") or "")
        oa = str((elig.get(cid) or {}).get("本文の入手（OpenAlex）") or "")
        for v, vocab, label in ((ta, X.TA, "題名・抄録段"), (ft, X.FT, "全文段"), (final, X.FINAL, "Claude案"), (full, X.FULLTEXT, "全文確認")):
            if v not in vocab:
                errs.append(f"cells スクリーニング {cid}: {label}『{v}』")
        level = (elig.get(cid) or {}).get("原文確認レベル")
        center = r["中心範囲の段"]
        if ta == "除外":
            if not ECODE.search(reason):
                errs.append(f"cells スクリーニング {cid}: 除外なのに除外理由に E コードが無い")
            if ft != "—" or full != "対象外" or final != "除外":
                errs.append(f"cells スクリーニング {cid}: 除外なのに全文段・全文確認・案が『—・対象外・除外』でない")
        elif ft == "—":
            errs.append(f"cells スクリーニング {cid}: 除外でないのに全文段が『—』")
        if ft == "除外" and not ECODE.search(reason):
            errs.append(f"cells スクリーニング {cid}: 全文段で除外なのに E コードが無い")
        if (ta == "除外" or ft == "除外") and ECODE.search(reason):
            if center not in CODE or CODE[center] not in ECODE.findall(reason):
                errs.append(f"cells スクリーニング {cid}: 除外の E コード（{ECODE.findall(reason)}）と中心の段（{center}）が合わない")
        elif center in CODE:
            errs.append(f"cells スクリーニング {cid}: 除外していないのに中心の段が {center}")
        # 本文を読んだ記録（原文確認レベル）と、全文段・全文確認の結びつき
        read = level == "本文関連箇所確認"
        if ta != "除外" and read != (full == "完了"):
            errs.append(f"cells スクリーニング {cid}: 全文確認『{full}』と原文確認レベル『{level}』が合わない")
        if ft in ("含める", "除外") and not read:
            errs.append(f"cells スクリーニング {cid}: 本文を読んでいないのに全文段が『{ft}』")
        if ft == "保留" and "E6" not in reason and not read:
            errs.append(f"cells スクリーニング {cid}: E6 でない全文段の保留なのに本文を読んでいない")
        if full == "完了" and (ft not in ("含める", "除外", "保留") or "E6" in reason):
            errs.append(f"cells スクリーニング {cid}: 本文を読んだ（完了）のに全文段が『{ft}』・理由が『{reason[:20]}』")
        if ft == "未実施" and oa == "無料の版なし":
            errs.append(f"cells スクリーニング {cid}: 無料の版が無いのに全文段が未実施")
        if full == "入手不可" and oa != "無料の版なし":
            errs.append(f"cells スクリーニング {cid}: 入手不可なのに本文の入手が『{oa}』")
        if full == "未完了" and not oa.startswith("無料の版あり"):
            errs.append(f"cells スクリーニング {cid}: 未完了（無料の版あり）なのに本文の入手が『{oa}』")
        if full == "入手不明" and oa not in X.UNKNOWN_OA:
            errs.append(f"cells スクリーニング {cid}: 入手不明なのに本文の入手が『{oa}』")
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


def expected_derived(e, oa):
    """派生の列の期待値（★ appraisal_xlsx.fill() を呼ばずに、design.md の語彙の表から独立に書いた）。"""
    ta, lv = e["ta"], e.get("lv", "抄録")
    if "ft" in e:
        ft = e["ft"]
    elif ta == "除外":
        ft = "—"
    elif oa == "無料の版なし":
        ft = "保留"
    else:
        ft = "未実施"
    if ta == "除外":
        full = "対象外"
    elif lv == "本文関連箇所確認":
        full = "完了"
    elif oa == "無料の版なし":
        full = "入手不可"
    elif oa.startswith("無料の版あり"):
        full = "未完了"
    else:
        full = "入手不明"
    final = ft if ft in ("含める", "除外", "保留") else ta
    return ft, full, final


def check_match(wb):
    """案のデータ（appraisal_data.A）と xlsx の各セルを、候補番号ごとに直に比べる（golden は build() 自身と比べるので、build の列の取り違えを捕まえない）。"""
    errs = []
    if wb.sheetnames != SHEETS:
        return ["match: シートの並びが違う"]
    tabs = {name: {r["候補番号"]: r for r in table(wb[name], headers)[1]} for name, headers in PER_CAND.items()}
    # ★ 書誌（出どころ・題名・DOI・本文の入手）も候補番号から独立に引いて比べる（build が別の候補の書誌を割り当てても捕まえる・Codex 2 巡目）
    recs = {m["cid"]: m for m in J.candidate_records(J.load_oa())}
    for cid, e in D.A.items():
        el, sc, me = (tabs[n].get(cid) for n in PER_CAND)
        if el is None or sc is None or me is None:
            errs.append(f"match {cid}: 行が無い")
            continue
        m = recs[cid]
        oa = m["oa"]
        title = m["title"] or m["label"]
        for label, got, want in (("適格性 出どころ", el["出どころ"], m["src"]), ("適格性 題名", el["題名"], title), ("適格性 DOI", el["DOI"] or "", m["doi"] or ""),
                                 ("適格性 本文の入手", el["本文の入手（OpenAlex）"], oa), ("スクリーニング 題名", sc["題名"], title), ("方法論 題名", me["題名"], title)):
            if got != want:
                errs.append(f"match {cid}: {label} が候補の一覧と違う")
        pairs = [("適格性 中心範囲の段", el["中心範囲の段"], e["c"]), ("適格性 判定根拠", el["判定根拠（プロトコル §2）"], e["b"]),
                 ("適格性 原文確認レベル", el["原文確認レベル"], e.get("lv", "抄録")), ("適格性 確認経路", el["確認経路"], e.get("rt", D.RT_FACT)),
                 ("適格性 次の確認", el["次の確認・作業"], e.get("n") or "—"), ("適格性 既存の案との違い", el["既存の案との違い"] or "", e.get("df", "")),
                 ("方法論 研究デザイン", me["研究デザイン（抄録・本文で確かめた範囲）"], e["d"]), ("方法論 懸念", me["懸念・限界（判定には使わない）"], e.get("k") or "—"),
                 ("スクリーニング 題名・抄録段", sc["Claude予備判定（題名・抄録段）"], e["ta"]), ("スクリーニング 中心範囲の段", sc["中心範囲の段"], e["c"])]
        ft, full, final = expected_derived(e, oa)
        pairs += [("スクリーニング 全文段", sc["Claude予備判定（全文段）"], ft), ("スクリーニング 全文確認", sc["全文確認・抽出"], full),
                  ("スクリーニング 案", sc["Claude案（現時点）"], final)]
        for label, got, want in pairs:
            if got != want:
                errs.append(f"match {cid}: {label} が案のデータと違う")
        reason = str(sc.get("除外理由") or "")
        if e.get("r") and e["r"] not in reason:
            errs.append(f"match {cid}: 除外理由に案のデータの理由が無い")
        if ft == "保留" and "ft" not in e and "E6" not in reason:
            errs.append(f"match {cid}: 無料の版が無いのに E6 が無い")
    return errs


def check_formulas(wb):
    """概要の数式の範囲が、各シートの表の行（FIRST〜最後の行）と合うこと。"""
    errs = []
    n = {name: len(table(wb[name], headers)[1]) for name, headers in PER_CAND.items()}
    n["Claude照合事項"] = len(table(wb["Claude照合事項"], X.CHK_HEADERS)[1])
    ws = wb["Claude評価概要"]
    for r in range(X.FIRST, ws.max_row + 1):
        v = ws.cell(r, 2).value
        if not (isinstance(v, str) and v.startswith("=")):
            continue
        for sheet, a, b in re.findall(r"'([^']+)'!\$?[A-Z]+\$?(\d+):\$?[A-Z]+\$?(\d+)", v):
            if sheet not in n:
                errs.append(f"formulas 概要 B{r}: 知らないシート『{sheet}』")
            elif int(a) != X.FIRST or int(b) != X.FIRST + n[sheet] - 1:
                errs.append(f"formulas 概要 B{r}: 範囲 {a}:{b} が表の行 {X.FIRST}:{X.FIRST + n[sheet] - 1} と合わない")
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
        m = LOCAL_PATH.search(t)
        if m:
            errs.append(f"words {where}: ローカルのパス『{m.group(0)}』")
    # リンクは DOI の解決先だけ（security-checker L-3）。数式は概要の B 列だけ（外部の書誌の文字列が数式にならない・Codex 1 巡目）
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if c.data_type == "f" and not (ws.title == "Claude評価概要" and c.column == 2):
                    errs.append(f"words {ws.title}!{c.coordinate}: 概要の B 列の外の数式")
                if c.hyperlink is not None:
                    target = c.hyperlink.target or ""
                    if not target.startswith("https://doi.org/"):
                        errs.append(f"words {ws.title}!{c.coordinate}: リンク先が DOI の解決先でない『{target[:60]}』")
                    if LOCAL_PATH.search(target) or LOCAL_PATH.search(c.hyperlink.display or ""):
                        errs.append(f"words {ws.title}!{c.coordinate}: リンクにローカルのパス")
    return errs


LOCAL_PATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|[\\/]Users[\\/]|AppData|file:/", re.I)


def check(path):
    wb = openpyxl.load_workbook(path)
    rows = check_rows(wb)
    if wb.sheetnames != SHEETS:  # ★ シートが欠けた・名前が違うときは後続の検査を打ち切る（例外で止まらない・Codex 1 巡目の指摘）
        return rows
    return rows + check_cells(wb) + check_match(wb) + check_formulas(wb) + check_golden(path, wb) + check_words(wb)


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
    runs = {"rows": check_rows, "cells": check_cells, "match": check_match, "formulas": check_formulas, "golden": None, "words": check_words}

    def run(kind, path):
        wb = openpyxl.load_workbook(path)
        if kind == "check":
            return check(path)
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
    unknown_cid = next(c for c, e in D.A.items() if e["ta"] != "除外" and "lv" not in e
                       and J.extract(next(x for x in CAND.CANDIDATES if x["cid"] == c))["doi"] is None)

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

    def basis_is_design(wb):  # build の列の取り違えを模す（判定根拠の欄に研究デザインの値）
        ws, wm = wb[E], wb[M]
        r = _find(ws, "S14-01")
        ws.cell(r, _col(X.ELIG_HEADERS, "判定根拠（プロトコル §2）")).value = wm.cell(_find(wm, "S14-01"), _col(X.METH_HEADERS, "研究デザイン（抄録・本文で確かめた範囲）")).value

    def unknown_as_free(wb):  # DOI の無い行を「未完了（無料の版あり）」に
        ws = wb[SC]
        ws.cell(_find(ws, unknown_cid), _col(X.SCR_HEADERS, "全文確認・抽出")).value = "未完了"

    def read_not_done(wb):  # 本文を読んだ行の全文確認を未完了に
        ws = wb[SC]
        ws.cell(_find(ws, "S02-02"), _col(X.SCR_HEADERS, "全文確認・抽出")).value = "未完了"

    def background_included(wb):  # 背景（E2）の行を題名・抄録段で含める（全文段は未実施）に
        ws = wb[SC]
        r = _find(ws, "S04-41")
        for h, v in (("Claude予備判定（題名・抄録段）", "含める"), ("Claude予備判定（全文段）", "未実施"), ("Claude案（現時点）", "含める"),
                     ("全文確認・抽出", "未完了"), ("除外理由", None)):
            ws.cell(r, _col(X.SCR_HEADERS, h)).value = v

    def code_mismatch(wb):  # 背景（E2）の行の除外理由を E4 に
        ws = wb[SC]
        ws.cell(_find(ws, "S02-10"), _col(X.SCR_HEADERS, "除外理由")).value = "E4（食い違い）"

    def formula_range(wb):
        ws = wb["Claude評価概要"]
        for r in range(X.FIRST, ws.max_row + 1):
            v = ws.cell(r, 2).value
            if isinstance(v, str) and "Claude適格性評価'!K" not in v and "'Claude適格性評価'!" in v:
                ws.cell(r, 2).value = re.sub(r":([A-Z]+)(\d+)\)", lambda m: f":{m.group(1)}{int(m.group(2)) - 1})", v, count=1)
                return

    def local_link(wb):
        ws = wb[E]
        ws.cell(_find(ws, "S14-01"), _col(X.ELIG_HEADERS, "DOI")).hyperlink = "file:///C:/Users/someone/x.pdf"

    def local_path(wb):
        ws = wb[M]
        c = ws.cell(_find(ws, "S14-03"), _col(X.METH_HEADERS, "懸念・限界（判定には使わない）"))
        c.value = str(c.value) + " " + "\\".join(["C:", "Users", "someone", "x.pdf"])

    def read_but_not_done(wb):  # 本文を読んだ行の全文段を未実施に（全文確認は完了のまま）
        ws = wb[SC]
        ws.cell(_find(ws, "S02-02"), _col(X.SCR_HEADERS, "Claude予備判定（全文段）")).value = "未実施"

    def formula_in_data(wb):  # 題名のセルを数式に
        ws = wb[E]
        ws.cell(_find(ws, "S14-01"), _col(X.ELIG_HEADERS, "題名")).value = '=HYPERLINK("https://example.org","x")'

    def swap_bib(wb):  # 2 つの候補の題名と DOI を入れ替える（別の候補の書誌の割り当て）
        ws = wb[E]
        r1, r2 = _find(ws, "S14-01"), _find(ws, "S14-02")
        for h in ("題名", "DOI"):
            j = _col(X.ELIG_HEADERS, h)
            ws.cell(r1, j).value, ws.cell(r2, j).value = ws.cell(r2, j).value, ws.cell(r1, j).value

    def drop_sheet(wb):
        del wb["Claude方法論メモ"]

    def email(wb):
        wb.properties.creator = "someone@example.com"

    cases = [("rows", "1 行を消す（スクリーニング案）", delete_row), ("rows", "2 行を入れ替える（方法論メモ）", swap), ("rows", "候補番号の重複", dup),
             ("cells", "判定根拠を空に", empty_basis), ("cells", "中心の段を語彙の外に", bad_vocab), ("cells", "用途判定を中心の段と合わない値に", use_mismatch),
             ("cells", "除外の理由から E コードを消す", excl_no_code), ("cells", "無料の版があるのに入手不可", unavailable_but_free),
             ("cells", "案を全文段・題名段と違う値に", final_mismatch), ("cells", "中心の段をシートの間で食い違わせる", center_differs),
             ("golden", "懸念の文を書き換える（ほかの検査は緑のはず）", text_edit), ("words", "GSE の語を入れる", gse), ("words", "作成者にメールアドレス", email),
             ("match", "判定根拠の欄に研究デザインの値（build の列の取り違え）", basis_is_design), ("cells", "DOI の無い行を未完了（無料の版あり）に", unknown_as_free),
             ("cells", "本文を読んだ行の全文確認を未完了に", read_not_done), ("cells", "背景（E2）の行を題名・抄録段で含めるに", background_included),
             ("cells", "除外の E コードを中心の段と食い違わせる", code_mismatch), ("formulas", "概要の数式の範囲を 1 行短く", formula_range),
             ("words", "リンク先をローカルのファイルに", local_link), ("words", "セルにローカルのパス", local_path),
             ("cells", "本文を読んだ行の全文段を未実施に", read_but_not_done), ("words", "題名のセルを数式に", formula_in_data),
             ("check", "シートを 1 枚消す（例外で止まらず赤）", drop_sheet), ("match", "2 つの候補の題名と DOI を入れ替える", swap_bib)]
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
        ("本文を読んだ記録があるのに全文段の案が無い", lambda A, C: A["S02-02"].pop("ft")),
        ("背景（E2）なのに題名・抄録段を含めるに", lambda A, C: (A["S04-41"].__setitem__("ta", "含める"), A["S04-41"].pop("r"))),
        ("照合事項の扱いの案（どちらも E2）と行の除外理由が合わない", lambda A, C: (A["S04-48"].__setitem__("c", "除外（E1）"), A["S04-48"].__setitem__("r", "E1（食い違い）"))),
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
