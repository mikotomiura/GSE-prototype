"""記入表 1（抄録段の 1 回目）の検査（design.md §5・§6）。

★ 期待は書き込み側（build_ta_sheet.py）と独立に組む: 出典は見出しの名前で引き、語彙・見出し・並べ方の性質は本ファイルが持つ。
★ 規則は RULES_* に 1 行 1 つで登録する（meta_mutate.py が 1 行ずつ外した写しで selftest が落ちることを確かめる）。

使い方:
  check_ta_sheet.py                 Downloads の記入表 1 が作ったままか（記入前）
  check_ta_sheet.py --path P        P を記入前として検査（dry-run の出力など）
  check_ta_sheet.py --filled        記入した記入表 1 を検査（途中なら進み具合を出して終了コード 2）
  check_ta_sheet.py --filled --final  全部記入されていなければ赤
  check_ta_sheet.py --selftest      陰性対照と変異
"""
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata

import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

import common as C
from check_workbook import STAGE1_BANNED  # 前のタスク（34 件）の 1 回目の禁止語

E_SHEETS = ["はじめに", "判定基準", "追加候補", "探索の記録"]
E_VERDICTS = ["含める", "除外", "保留"]
E_ECODES = ["E1", "E2", "E3", "E4 背景（レビュー・尺度の原著・理論）", "E4 方法論", "E4 訂正通知", "E5", "E7"]
E_ADD = ["足す", "足さない"]
E_CAND_HEADER = ["順", "候補番号", "題名", "年", "掲載誌", "DOI（リンク）", "抄録（原文）", "抄録の出どころ",
                 "要点（事実のファイルの記述）", "同じ研究の群", "内容の群（並べ替えのため・判定の材料ではない）",
                 "本文の入手（OpenAlex）", "判定【記入】", "除外理由【記入】", "メモ【記入】"]
E_SEARCH_HEADER = ["順", "記録", "題名", "年", "種別（API の記録）", "DOI（リンク）", "抄録（原文）", "抄録の出どころ",
                   "本文の入手（OpenAlex）", "重なり", "候補に足す【記入】", "判定【記入】", "除外理由【記入】", "メモ【記入】"]
HR = 4  # 見出しの行
N_UNJUDGED = 213
N_SEARCH = 46
# 判定者用ファイル『追加候補』の見出し（出典の列を名前で引く）
J_ID, J_TITLE, J_YEAR, J_VENUE, J_DOI, J_OA, J_POINT, J_GROUP, J_CONTENT = (
    "候補番号", "題名（書誌の記録）", "年", "掲載誌", "DOI", "本文の入手（OpenAlex）", "要点（事実のファイルの記述）",
    "同じ研究の群", "内容の群（機械の分類・並べ替えのため・判定の材料ではない）")


def nf(s):
    return unicodedata.normalize("NFKC", s) if isinstance(s, str) else s


def cl(v):
    return ILLEGAL_CHARACTERS_RE.sub("", v) if isinstance(v, str) else v


def blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


# ---------------------------------------------------------------- 出典（独立に読む）
def sources():
    s = {}
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))
    hdr = list(rows[C.JUDGE_HEADER_ROW - 1])
    ix = {h: hdr.index(h) for h in (J_ID, J_TITLE, J_YEAR, J_VENUE, J_DOI, J_OA, J_POINT, J_GROUP, J_CONTENT)}
    judged = {json.loads(l)["item"] for l in open(C.PREV_LOG, encoding="utf-8")}
    s["cands"] = {r[ix[J_ID]]: {k: r[i] for k, i in ix.items()} for r in rows[C.JUDGE_HEADER_ROW:]
                  if r and r[ix[J_ID]] and r[ix[J_ID]] not in judged}
    s["criteria"] = [list(r) for r in jw["判定基準"].iter_rows(values_only=True)]
    recs = json.load(open(C.SEARCH_RECORDS, encoding="utf-8"))
    s["search"] = {r["reading"]: r for r in recs if r.get("reading") and re.fullmatch(r"R\d\d", r["reading"])}
    s["abs"] = json.load(open(C.ABSTRACTS, encoding="utf-8"))
    s["status"] = json.load(open(C.ABSTRACT_STATUS, encoding="utf-8"))
    # 評価版にしかない文（15 字以上で、出典のどこにも無いもの）
    corpus = []
    for r in rows:
        corpus += [str(v) for v in r if v is not None]
    corpus += [str(v) for r in s["criteria"] for v in r if v is not None]
    corpus += [(v.get("text") or "") for v in s["abs"].values()]
    corpus += [r["title"] for r in recs]
    corpus = "\n".join(nf(x) for x in corpus)
    aw = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)
    ai = set()
    for sh in ("Claude適格性評価", "Claudeスクリーニング案", "Claude方法論メモ", "Claude照合事項"):
        for r in aw[sh].iter_rows(values_only=True):
            for v in r:
                if isinstance(v, str) and len(v.strip()) >= 15 and nf(v.strip()) not in corpus:
                    ai.add(nf(v.strip()))
    s["ai_only"] = sorted(ai)
    return s


def oa_label(oa):
    if not oa:
        return "未確認"
    return "無料の版なし" if oa == "closed" else f"無料の版あり（{oa}）"


def exp_abstract(src, i):
    st = src["status"].get(i) or {}
    t = (src["abs"].get(i) or {}).get("text") or ""
    return (cl(t), st.get("source")) if st.get("chars") and t else (None, None)


# ---------------------------------------------------------------- 規則
def body(ws, ncol):
    out = []
    r = HR + 1
    while ws.cell(r, 2).value is not None or ws.cell(r, 1).value is not None:
        out.append((r, [ws.cell(r, c).value for c in range(1, ncol + 1)]))
        r += 1
    return out


def r_sheets(ctx):
    return [] if ctx["wb"].sheetnames == E_SHEETS else [f"シート名・順: {ctx['wb'].sheetnames}"]


def r_cand_rows(ctx):
    v, ws = [], ctx["wb"]["追加候補"]
    if [ws.cell(HR, c).value for c in range(1, 16)] != E_CAND_HEADER:
        v.append("追加候補: 見出し")
    rows = body(ws, 15)
    ids = [x[1] for _, x in rows]
    if len(ids) != N_UNJUDGED or len(set(ids)) != len(ids) or set(ids) != set(ctx["src"]["cands"]):
        v.append(f"追加候補: 行の ID（{len(ids)} 行・重複 {len(ids) - len(set(ids))}・期待との差 "
                 f"{sorted(set(ids) ^ set(ctx['src']['cands']))[:5]}）")
    if [x[0] for _, x in rows] != list(range(1, len(rows) + 1)):
        v.append("追加候補: 順の列が 1 から連番でない")
    return v


def r_cand_sources(ctx):
    v, ws = [], ctx["wb"]["追加候補"]
    for r, x in body(ws, 15):
        e = ctx["src"]["cands"].get(x[1])
        if not e:
            continue
        ab, src = exp_abstract(ctx["src"], x[1])
        want = [cl(e[J_TITLE]), e[J_YEAR], cl(e[J_VENUE]), e[J_DOI], ab, None, cl(e[J_POINT]), cl(e[J_GROUP]),
                cl(e[J_CONTENT]), cl(e[J_OA])]
        got = [x[2], x[3], x[4], x[5], x[6], None, x[8], x[9], x[10], x[11]]
        for k, (a, b) in enumerate(zip(got, want)):
            if k != 5 and not (a == b or (blank(a) and blank(b))):
                v.append(f"追加候補 {x[1]}: {E_CAND_HEADER[k + 2]} が出典と違う")
        if src and x[7] != src:
            v.append(f"追加候補 {x[1]}: 抄録の出どころ {x[7]!r} ≠ {src!r}")
        if not src and not str(x[7] or "").startswith("抄録なし"):
            v.append(f"追加候補 {x[1]}: 抄録が無いのに出どころが「抄録なし」でない")
    return v


def r_cand_order(ctx):
    """同じ研究の群は隣どうし・群に入らない記録は内容の群ごとにひと続き（並べ方の性質だけを見る）。"""
    v, rows = [], [x for _, x in body(ctx["wb"]["追加候補"], 15)]
    gid = [(re.match(r"\s*([GU]\d+)", str(x[9] or "")) or [None, None])[1] for x in rows]
    for g in {g for g in gid if g}:
        pos = [k for k, h in enumerate(gid) if h == g]
        if pos != list(range(pos[0], pos[0] + len(pos))):
            v.append(f"追加候補: 同じ研究の群 {g} が隣どうしでない")
    seq = [x[10] for x, g in zip(rows, gid) if not g]
    seen = []
    for k, c in enumerate(seq):
        if k and c != seq[k - 1]:
            if c in seen:
                v.append(f"追加候補: 内容の群「{c}」がひと続きでない")
                break
        if not seen or seen[-1] != c:
            seen.append(c)
    return v


def r_search_rows(ctx):
    v, ws = [], ctx["wb"]["探索の記録"]
    if [ws.cell(HR, c).value for c in range(1, 15)] != E_SEARCH_HEADER:
        v.append("探索の記録: 見出し")
    rows = body(ws, 14)
    ids = [x[1] for _, x in rows]
    if ids != sorted(ctx["src"]["search"]) or len(ids) != N_SEARCH:
        v.append(f"探索の記録: 行が読む一覧 {N_SEARCH} 件の R の順と違う（{len(ids)} 行）")
    if [x[0] for _, x in rows] != list(range(1, len(rows) + 1)):
        v.append("探索の記録: 順の列が 1 から連番でない")
    return v


def r_search_sources(ctx):
    v = []
    for r, x in body(ctx["wb"]["探索の記録"], 14):
        e = ctx["src"]["search"].get(x[1])
        if not e:
            continue
        ab, src = exp_abstract(ctx["src"], x[1])
        doi = e["key"] if e["key"].startswith("10.") else None
        for name, a, b in (("題名", x[2], cl(e["title"])), ("年", x[3], e["year"]), ("種別", x[4], e["type"]),
                           ("DOI", x[5], doi), ("抄録", x[6], ab), ("本文の入手", x[8], oa_label(e["oa"]))):
            if not (a == b or (blank(a) and blank(b))):
                v.append(f"探索の記録 {x[1]}: {name} が出典と違う")
        if src and x[7] != src:
            v.append(f"探索の記録 {x[1]}: 抄録の出どころ")
        if not src and not str(x[7] or "").startswith("抄録なし"):
            v.append(f"探索の記録 {x[1]}: 抄録が無いのに出どころが「抄録なし」でない")
        ov = e.get("overlap")
        ovid = ov.split(":")[-1] if ov else None
        if ovid and ovid not in str(x[9] or ""):
            v.append(f"探索の記録 {x[1]}: 重なり（{ovid}）が書かれていない")
        if not ovid and not blank(x[9]):
            v.append(f"探索の記録 {x[1]}: 重ならないのに重なりの欄がある")
    return v


def r_criteria(ctx):
    ws = ctx["wb"]["判定基準"]
    for r, row in enumerate(ctx["src"]["criteria"], 1):
        for c, val in enumerate(row, 1):
            got = ws.cell(r, c).value
            if not (got == cl(val) or (blank(got) and blank(val))):
                return [f"判定基準: {ws.cell(r, c).coordinate} が判定者用ファイルと違う"]
    if ws.max_row > len(ctx["src"]["criteria"]):
        return ["判定基準: 判定者用ファイルに無い行がある"]
    return []


def authored_cells(wb):
    """Claude が書いたセル（出典から写していないもの）。"""
    out = [c for row in wb["はじめに"].iter_rows() for c in row]
    for sh, cols in (("追加候補", (8,)), ("探索の記録", (8, 9, 10))):
        ws = wb[sh]
        out += [c for row in ws.iter_rows(min_row=1, max_row=HR) for c in row]
        for r in range(HR + 1, ws.max_row + 1):
            out += [ws.cell(r, c) for c in cols]
    return out


def r_banned(ctx):
    v = []
    for c in authored_cells(ctx["wb"]):
        if isinstance(c.value, str):
            m = STAGE1_BANNED.search(nf(c.value))
            if m:
                v.append(f"{c.parent.title}!{c.coordinate}: 禁止語 {m.group(0)!r}")
    return v


def r_ai_only(ctx):
    text = "\n".join(nf(str(c.value)) for ws in ctx["wb"].worksheets for row in ws.iter_rows() for c in row
                     if c.value is not None)
    hits = [s for s in ctx["src"]["ai_only"] if s in text]
    return [f"評価版にしかない文が入っている: {hits[0][:40]!r}…（{len(hits)} 件）"] if hits else []


def r_links(ctx):
    v = []
    for sh, doicol in (("追加候補", 6), ("探索の記録", 6)):
        ws = ctx["wb"][sh]
        for row in ws.iter_rows():
            for c in row:
                link = c.hyperlink.target if c.hyperlink else None
                if c.column == doicol and c.row > HR and not blank(c.value):
                    if link != "https://doi.org/" + str(c.value):
                        v.append(f"{sh}!{c.coordinate}: DOI のリンクが違う")
                elif link:
                    v.append(f"{sh}!{c.coordinate}: DOI の欄の外にリンク")
    for ws in ctx["wb"].worksheets:
        if ws.title not in ("追加候補", "探索の記録"):
            if any(c.hyperlink for row in ws.iter_rows() for c in row):
                v.append(f"{ws.title}: リンクがある")
    return v


def _dv_cells(ws):
    out = {}
    for dv in ws.data_validations.dataValidation:
        f = (dv.formula1 or "").strip('"')
        for rng in dv.sqref.ranges:
            for row in ws.iter_rows(min_row=rng.min_row, max_row=rng.max_row, min_col=rng.min_col, max_col=rng.max_col):
                for c in row:
                    out.setdefault(c.coordinate, []).append((dv.type, f))
    return out


def r_validation(ctx):
    v = []
    ws = ctx["wb"]["追加候補"]
    rows = [r for r, _ in body(ws, 15)]
    want = {}
    for r in rows:
        want[f"M{r}"] = [("list", ",".join(E_VERDICTS))]
        want[f"N{r}"] = [("list", ",".join(E_ECODES))]
    if _dv_cells(ws) != want:
        v.append("追加候補: 入力規則（範囲か語彙）が違う")
    ws = ctx["wb"]["探索の記録"]
    want = {}
    for r, x in body(ws, 14):
        if (ctx["src"]["search"].get(x[1]) or {}).get("overlap"):
            continue
        want[f"K{r}"] = [("list", ",".join(E_ADD))]
        want[f"L{r}"] = [("list", ",".join(E_VERDICTS))]
        want[f"M{r}"] = [("list", ",".join(E_ECODES))]
    if _dv_cells(ws) != want:
        v.append("探索の記録: 入力規則（範囲か語彙）が違う（重なりの行に置いていないか）")
    return v


def inputs(wb, src):
    """(sheet, ID, {列: 値}, 重なりか) の一覧。"""
    out = []
    for r, x in body(wb["追加候補"], 15):
        out.append(("追加候補", x[1], {"M": x[12], "N": x[13], "O": x[14]}, False))
    for r, x in body(wb["探索の記録"], 14):
        out.append(("探索の記録", x[1], {"K": x[10], "L": x[11], "M": x[12], "N": x[13]},
                    bool((src["search"].get(x[1]) or {}).get("overlap"))))
    return out


def r_inputs_blank(ctx):
    v = [f"{sh} {i}: 記入前なのに {k} に値" for sh, i, d, _ in inputs(ctx["wb"], ctx["src"]) for k, x in d.items()
         if not blank(x)]
    return v[:10]


def r_unchanged(ctx):
    """記入欄の外のセルが、作った時点の原本と同じ（原本の SHA が記録と同じ）。"""
    if not os.path.exists(ctx["orig_path"]) or C.sha256(ctx["orig_path"]) != ctx["orig_sha"]:
        return ["原本が無いか、原本の SHA-256 が記録と違う"]
    o = openpyxl.load_workbook(ctx["orig_path"])
    w = ctx["wb"]
    if o.sheetnames != w.sheetnames:
        return ["シートが原本と違う"]
    inp = {"追加候補": {13, 14, 15}, "探索の記録": {11, 12, 13, 14}}
    v = []
    for ws in o.worksheets:
        wf = w[ws.title]
        mr, mc = max(ws.max_row, wf.max_row), max(ws.max_column, wf.max_column)
        for r in range(1, mr + 1):
            for c in range(1, mc + 1):
                if r > HR and c in inp.get(ws.title, ()):
                    continue
                if ws.cell(r, c).value != wf.cell(r, c).value:
                    v.append(f"{ws.title}!{ws.cell(r, c).coordinate}: 記入欄の外が原本と違う")
    return v[:10]


def r_inputs_vocab(ctx):
    v = []
    for sh, i, d, ov in inputs(ctx["wb"], ctx["src"]):
        if ov:
            if any(not blank(x) for x in d.values()):
                v.append(f"{sh} {i}: 重なりの行に記入がある")
            continue
        if sh == "追加候補":
            verdict, code = d["M"], d["N"]
        else:
            add, verdict, code = d["K"], d["L"], d["M"]
            if not blank(add) and add not in E_ADD:
                v.append(f"{sh} {i}: 候補に足す {add!r} は語彙の外")
            if add == "足さない" and (not blank(verdict) or not blank(code)):
                v.append(f"{sh} {i}: 足さないのに判定か除外理由がある")
            if blank(add) and (not blank(verdict) or not blank(code)):
                v.append(f"{sh} {i}: 候補に足すが空なのに判定がある")
        if not blank(verdict) and verdict not in E_VERDICTS:
            v.append(f"{sh} {i}: 判定 {verdict!r} は語彙の外")
        if not blank(code) and code not in E_ECODES:
            v.append(f"{sh} {i}: 除外理由 {code!r} は語彙の外")
        if verdict == "除外" and blank(code):
            v.append(f"{sh} {i}: 除外なのに除外理由が無い")
        if verdict in ("含める", "保留") and not blank(code):
            v.append(f"{sh} {i}: {verdict}なのに除外理由がある")
        if blank(verdict) and not blank(code):
            v.append(f"{sh} {i}: 判定が空なのに除外理由がある")
    return v


def missing(ctx):
    out = []
    for sh, i, d, ov in inputs(ctx["wb"], ctx["src"]):
        if ov:
            continue
        if sh == "追加候補" and blank(d["M"]):
            out.append(i)
        if sh == "探索の記録" and (blank(d["K"]) or (d["K"] == "足す" and blank(d["L"]))):
            out.append(i)
    return out


def r_complete(ctx):
    m = missing(ctx)
    return [f"未記入 {len(m)} 件（{', '.join(m[:8])}…）"] if m else []


# ★ 1 行 1 規則（meta_mutate.py が 1 行ずつ外す）
RULES_COMMON = [
    r_sheets,
    r_cand_rows,
    r_cand_sources,
    r_cand_order,
    r_search_rows,
    r_search_sources,
    r_criteria,
    r_banned,
    r_ai_only,
    r_links,
    r_validation,
]
RULES_BLANK = [
    r_inputs_blank,
]
RULES_FILLED = [
    r_unchanged,
    r_inputs_vocab,
]
RULES_FINAL = [
    r_complete,
]


def recorded_sha(key="sheet1"):
    if os.path.exists(C.TA_SHA_RECORD):
        for line in open(C.TA_SHA_RECORD, encoding="utf-8"):
            if line.startswith(key + " "):
                return line.split()[1]
    return None


def check(path, src, mode="blank", final=False, orig_path=None, orig_sha=None):
    wb = openpyxl.load_workbook(path)
    ctx = {"wb": wb, "src": src, "orig_path": orig_path or C.TA_SHEET1_ORIG, "orig_sha": orig_sha or recorded_sha()}
    rules = list(RULES_COMMON) + (RULES_BLANK if mode == "blank" else RULES_FILLED) + (RULES_FINAL if final else [])
    v = []
    for rule in rules:
        try:
            v += rule(ctx)
        except Exception as e:  # ★ 形が崩れた表で規則が例外を出したら赤
            v.append(f"{rule.__name__}: 例外 {type(e).__name__}: {e}")
    return v, (missing(ctx) if mode == "filled" else [])


# ---------------------------------------------------------------- selftest
def selftest():
    import build_ta_sheet as B
    src = sources()
    tmpd = tempfile.mkdtemp(prefix="ta1-self-")
    base = os.path.join(tmpd, "base.xlsx")
    B.build().save(base)
    ok = True

    def expect(name, path, red, **kw):
        nonlocal ok
        v, _ = check(path, src, **kw)
        good = bool(v) == red
        ok &= good
        print(("PASS" if good else "FAIL"), name, "" if good else v[:3])

    expect("陰性対照（作ったまま）", base, False)

    def mut(name, fn, red=True, **kw):
        p = os.path.join(tmpd, f"m{abs(hash(name))}.xlsx")
        wb = openpyxl.load_workbook(base)
        fn(wb)
        wb.save(p)
        expect(name, p, red, **kw)

    ca, se = "追加候補", "探索の記録"
    rows = body(openpyxl.load_workbook(base)[ca], 15)
    grow = next(r for r, x in rows if re.match(r"\s*G\d+", str(x[9] or "")))
    nongroup = [r for r, x in rows if not re.match(r"\s*[GU]\d+", str(x[9] or ""))]

    def swap_rows(ws, a, b):
        for c in range(1, 16):
            if c == 1:
                continue
            x, y = ws.cell(a, c), ws.cell(b, c)
            x.value, y.value = y.value, x.value
            xl, yl = (x.hyperlink.target if x.hyperlink else None), (y.hyperlink.target if y.hyperlink else None)
            x.hyperlink, y.hyperlink = yl, xl

    first_ng, last_ng = nongroup[0], nongroup[-1]
    mut("行を 1 つ消す", lambda wb: wb[ca].delete_rows(HR + 3))
    mut("ID を書き換える", lambda wb: setattr(wb[ca].cell(HR + 1, 2), "value", "S99-99"))
    mut("題名を変える", lambda wb: setattr(wb[ca].cell(HR + 2, 3), "value", "x" + str(wb[ca].cell(HR + 2, 3).value)))
    mut("抄録を変える", lambda wb: setattr(wb[ca].cell(HR + 5, 7), "value", "y" + str(wb[ca].cell(HR + 5, 7).value)))
    mut("要点を変える", lambda wb: setattr(wb[ca].cell(HR + 5, 9), "value", "z"))
    mut("出どころを別の API に", lambda wb: setattr(wb[ca].cell(HR + 5, 8), "value", "Crossref?"))
    mut("同じ研究の群を離す", lambda wb: swap_rows(wb[ca], grow, last_ng if last_ng != grow + 1 else first_ng))
    mut("内容の群を混ぜる", lambda wb: swap_rows(wb[ca], first_ng, last_ng))
    mut("順を変える", lambda wb: setattr(wb[ca].cell(HR + 2, 1), "value", 99))
    mut("見出しを変える", lambda wb: setattr(wb[ca].cell(HR, 13), "value", "判定"))
    mut("シート名を変える", lambda wb: setattr(wb[se], "title", "探索"))
    mut("シートを足す", lambda wb: wb.create_sheet("メモ"))                       # ★ r_sheets だけが拾う（メタ変異）
    mut("シートの順を入れ替える", lambda wb: wb.move_sheet("はじめに", offset=3))
    mut("探索の順を変える", lambda wb: setattr(wb[se].cell(HR + 2, 1), "value", 7))  # ★ r_search_rows だけが拾う
    mut("探索の見出しを変える", lambda wb: setattr(wb[se].cell(HR, 11), "value", "足す"))
    mut("判定基準を変える", lambda wb: setattr(wb["判定基準"].cell(3, 2), "value", "変えた"))
    mut("はじめにに禁止語", lambda wb: setattr(wb["はじめに"].cell(5, 2), "value", "含めるのを推奨します"))
    mut("出どころに禁止語", lambda wb: setattr(wb[ca].cell(HR + 1, 8), "value", "Claude の判定"))
    mut("評価版の文を混ぜる", lambda wb: setattr(wb[ca]["A2"], "value", src["ai_only"][len(src["ai_only"]) // 2]))
    mut("DOI のリンクを消す", lambda wb: setattr(wb[ca].cell(HR + 1, 6), "hyperlink", None))
    mut("題名にリンク", lambda wb: setattr(wb[ca].cell(HR + 1, 3), "hyperlink", "https://example.org/"))
    mut("探索の重なりの印を消す", lambda wb: [setattr(wb[se].cell(r, 10), "value", None) for r in range(HR + 1, HR + 47)
                                       if wb[se].cell(r, 2).value == "R29"])

    def dv_drop(wb):
        dv = wb[ca].data_validations.dataValidation[0]
        dv.formula1 = '"含める,除外"'
    mut("入力規則の語彙を減らす", dv_drop)

    def dv_overlap(wb):
        from openpyxl.worksheet.datavalidation import DataValidation
        dv = DataValidation(type="list", formula1='"' + ",".join(E_ADD) + '"', allow_blank=True)
        wb[se].add_data_validation(dv)
        r = next(r for r in range(HR + 1, HR + 47) if wb[se].cell(r, 2).value == "R28")
        dv.add(f"K{r}")
    mut("重なりの行に入力規則", dv_overlap)
    mut("記入前に記入", lambda wb: setattr(wb[ca].cell(HR + 1, 13), "value", "含める"))

    # 記入した表（原本 = base）
    rec = C.sha256(base)
    filled = os.path.join(tmpd, "filled.xlsx")
    wb = openpyxl.load_workbook(base)
    for r, x in body(wb[ca], 15):
        wb[ca].cell(r, 13).value = "含める"
    for r, x in body(wb[se], 14):
        if not (src["search"].get(x[1]) or {}).get("overlap"):
            wb[se].cell(r, 11).value = "足さない"
    wb.save(filled)
    kw = {"mode": "filled", "final": True, "orig_path": base, "orig_sha": rec}
    expect("記入済みの対照（--final）", filled, False, **kw)

    def fmut(name, fn, red=True, **extra):
        p = os.path.join(tmpd, f"f{abs(hash(name))}.xlsx")
        w = openpyxl.load_workbook(filled)
        fn(w)
        w.save(p)
        expect(name, p, red, **{**kw, **extra})

    srow = next(r for r, x in body(openpyxl.load_workbook(base)[se], 14) if not (src["search"].get(x[1]) or {}).get("overlap"))
    orow = next(r for r, x in body(openpyxl.load_workbook(base)[se], 14) if (src["search"].get(x[1]) or {}).get("overlap"))
    fmut("除外なのに除外理由なし", lambda w: setattr(w[ca].cell(HR + 1, 13), "value", "除外"))
    fmut("含めるのに除外理由", lambda w: setattr(w[ca].cell(HR + 1, 14), "value", "E2"))
    fmut("判定が語彙の外", lambda w: setattr(w[ca].cell(HR + 1, 13), "value", "含む"))
    fmut("除外理由が語彙の外", lambda w: [setattr(w[ca].cell(HR + 1, 13), "value", "除外"),
                                     setattr(w[ca].cell(HR + 1, 14), "value", "E6")])
    fmut("判定が空で除外理由だけ", lambda w: [setattr(w[ca].cell(HR + 2, 13), "value", None),
                                        setattr(w[ca].cell(HR + 2, 14), "value", "E1")], final=False)
    fmut("足さないのに判定", lambda w: setattr(w[se].cell(srow, 12), "value", "含める"))
    fmut("足すが語彙の外", lambda w: setattr(w[se].cell(srow, 11), "value", "加える"))
    fmut("足すのに判定なし（--final）", lambda w: setattr(w[se].cell(srow, 11), "value", "足す"))
    fmut("足すが空で判定", lambda w: [setattr(w[se].cell(srow, 11), "value", None),
                                  setattr(w[se].cell(srow, 12), "value", "保留")], final=False)
    fmut("重なりの行に記入", lambda w: setattr(w[se].cell(orow, 14), "value", "メモ"))
    fmut("記入欄の外を変える", lambda w: setattr(w[ca].cell(HR + 3, 3), "value", "変えた題名"))
    fmut("記入漏れ（--final）", lambda w: setattr(w[ca].cell(HR + 4, 13), "value", None))
    fmut("記入漏れは --final でなければ赤でない", lambda w: setattr(w[ca].cell(HR + 4, 13), "value", None), red=False, final=False)
    fmut("原本の SHA が記録と違う", lambda w: None, orig_sha="0" * 64)
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        sys.exit(0 if selftest() else 1)
    src = sources()
    if "--path" in a:
        path = a[a.index("--path") + 1]
    else:
        path = C.TA_SHEET1
        rec = recorded_sha()
        if "--filled" not in a and (rec is None or C.sha256(path) != rec):
            print("違反: Downloads の記入表 1 が記録した SHA-256 と違う（記入前の検査）")
            sys.exit(1)
    mode = "filled" if "--filled" in a else "blank"
    v, miss = check(path, src, mode=mode, final="--final" in a)
    for x in v:
        print("違反:", x)
    if v:
        print(f"違反 {len(v)} 件")
        sys.exit(1)
    if mode == "filled" and miss:
        print(f"記入の途中: 未記入 {len(miss)} 件（{', '.join(miss[:10])}…）")
        sys.exit(2)
    print("違反 0")


if __name__ == "__main__":
    main()
