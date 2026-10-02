"""記入表 2（抄録段で除外した件の 2 回目）の検査（design.md §7）。

★ 期待は書き込み側（build_ta2_sheet.py）と独立に組む: 対象はログを自分で読み、AI の値は評価版を見出しの名前で引く。
★ 規則は RULES_* に 1 行 1 つ（meta_mutate.py が 1 行ずつ外す）。
使い方: check_ta2_sheet.py [--path P] [--filled [--final]] | --selftest
"""
import json
import os
import re
import shutil
import sys
import tempfile

import openpyxl

import common as C

E_SHEETS = ["はじめに", "2 回目"]
E_HEADER = ["候補番号", "題名", "1 回目（判定者 1）", "AI：題名・抄録段の予備判定", "AI：除外理由", "AI：中心範囲の段",
            "AI：用途判定", "AI：判定根拠", "AI：方法論メモ（懸念・限界）", "2 回目【記入】", "変えた後の判定【記入】",
            "変えた後の除外理由【記入】", "理由【記入】"]
E_SAME = ["1 回目のまま", "変える"]
E_DIFF = ["1 回目のまま", "AI の判定に変える", "別の判定に変える"]
E_VERDICTS = ["含める", "除外", "保留"]
E_ECODES = ["E1", "E2", "E3", "E4 背景（レビュー・尺度の原著・理論）", "E4 方法論", "E4 訂正通知", "E5", "E7"]
HR = 4


def blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def en(s):
    m = re.match(r"\s*(E\d)", s or "")
    return m.group(1) if m else None


def sources(log_path=None):
    s = {"first": {}}
    for l in open(log_path or C.LOG, encoding="utf-8"):
        if l.strip():
            d = json.loads(l)
            if d.get("stage") == "ta1" and re.fullmatch(r"S\d\d-\d\d", d.get("item", "")) and d["cells"].get("M") == "除外":
                s["first"][d["item"]] = d["cells"]
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    s["title"] = {r[h.index("候補番号")]: r[h.index("題名（書誌の記録）")] for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]}
    aw = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)
    ai = {}
    for sh, cols in (("Claudeスクリーニング案", ("Claude予備判定（題名・抄録段）", "除外理由")),
                     ("Claude適格性評価", ("中心範囲の段", "用途判定（Claude）", "判定根拠（プロトコル §2）")),
                     ("Claude方法論メモ", ("懸念・限界（判定には使わない）",))):
        rr = list(aw[sh].iter_rows(values_only=True))
        hh = list(next(r for r in rr if r and r[0] == "候補番号"))
        start = rr.index(next(r for r in rr if r and r[0] == "候補番号")) + 1
        for r in rr[start:]:
            if r and r[0]:
                ai.setdefault(r[0], []).extend(r[hh.index(c)] for c in cols)
    s["ai"] = ai
    return s


def body(ws):
    out, r = [], HR + 1
    while ws.cell(r, 1).value is not None:
        out.append((r, [ws.cell(r, c).value for c in range(1, 14)]))
        r += 1
    return out


def is_same(first, ai):
    return ai[0] == "除外" and en(ai[1]) == en(first.get("N"))


def r_sheets(ctx):
    return [] if ctx["wb"].sheetnames == E_SHEETS else ["シート名・順"]


def r_rows(ctx):
    ws, v = ctx["wb"]["2 回目"], []
    if [ws.cell(HR, c).value for c in range(1, 14)] != E_HEADER:
        v.append("見出し")
    ids = [x[0] for _, x in body(ws)]
    if ids != list(ctx["src"]["first"]):
        v.append(f"行が記入表 1 の除外の記録（ログの順）と違う（{len(ids)} 行 / {len(ctx['src']['first'])}）")
    return v


def r_first(ctx):
    v = []
    for r, x in body(ctx["wb"]["2 回目"]):
        f = ctx["src"]["first"].get(x[0])
        if f is None:
            continue
        t = str(x[2] or "")
        if not t.startswith("除外") or str(f.get("N")) not in t or (f.get("O") and str(f["O"]) not in t):
            v.append(f"{x[0]}: 1 回目の欄がログと違う")
    return v


def r_title(ctx):
    return [f"{x[0]}: 題名" for r, x in body(ctx["wb"]["2 回目"]) if x[1] != ctx["src"]["title"].get(x[0])]


def r_ai(ctx):
    v = []
    for r, x in body(ctx["wb"]["2 回目"]):
        want = ctx["src"]["ai"].get(x[0])
        got = x[3:9]
        if want is None or any(not (a == b or (blank(a) and blank(b))) for a, b in zip(got, want)):
            v.append(f"{x[0]}: AI の値が評価版と違う")
    return v


def _dv(ws):
    out = {}
    for dv in ws.data_validations.dataValidation:
        for rng in dv.sqref.ranges:
            for row in ws.iter_rows(min_row=rng.min_row, max_row=rng.max_row, min_col=rng.min_col, max_col=rng.max_col):
                for c in row:
                    out.setdefault(c.coordinate, []).append((dv.type, (dv.formula1 or "").strip('"')))
    return out


def r_validation(ctx):
    ws, want = ctx["wb"]["2 回目"], {}
    for r, x in body(ws):
        f, ai = ctx["src"]["first"].get(x[0]), ctx["src"]["ai"].get(x[0])
        if f is None or ai is None:
            continue
        want[f"J{r}"] = [("list", ",".join(E_SAME if is_same(f, ai) else E_DIFF))]
        want[f"K{r}"] = [("list", ",".join(E_VERDICTS))]
        want[f"L{r}"] = [("list", ",".join(E_ECODES))]
    return [] if _dv(ws) == want else ["入力規則（範囲か語彙・同じ／違うの選択肢）が違う"]


def r_blank(ctx):
    return [f"{x[0]}: 記入前なのに値" for r, x in body(ctx["wb"]["2 回目"]) if any(not blank(y) for y in x[9:13])][:5]


def r_unchanged(ctx):
    if not os.path.exists(ctx["orig_path"]) or C.sha256(ctx["orig_path"]) != ctx["orig_sha"]:
        return ["原本が無いか、原本の SHA-256 が記録と違う"]
    o, w, v = openpyxl.load_workbook(ctx["orig_path"]), ctx["wb"], []
    if o.sheetnames != w.sheetnames:
        return ["シートが原本と違う"]
    for ws in o.worksheets:
        wf = w[ws.title]
        for r in range(1, max(ws.max_row, wf.max_row) + 1):
            for c in range(1, max(ws.max_column, wf.max_column) + 1):
                if ws.title == "2 回目" and r > HR and c >= 10:
                    continue
                if ws.cell(r, c).value != wf.cell(r, c).value:
                    v.append(f"{ws.title}!{ws.cell(r, c).coordinate}: 記入欄の外が原本と違う")
    return v[:10]


def r_vocab(ctx):
    v = []
    for r, x in body(ctx["wb"]["2 回目"]):
        f, ai = ctx["src"]["first"].get(x[0]), ctx["src"]["ai"].get(x[0])
        if f is None or ai is None:
            continue
        j, k, l_, m = x[9], x[10], x[11], x[12]
        allowed = E_SAME if is_same(f, ai) else E_DIFF
        if blank(j):
            if any(not blank(y) for y in (k, l_)):
                v.append(f"{x[0]}: 2 回目が空なのに変えた後の判定がある")
            continue
        if j not in allowed:
            v.append(f"{x[0]}: 2 回目 {j!r} はこの記録の選択肢の外")
            continue
        if j == "1 回目のまま":
            if not blank(k) or not blank(l_):
                v.append(f"{x[0]}: 1 回目のままなのに変えた後の判定がある")
            continue
        if k not in E_VERDICTS:
            v.append(f"{x[0]}: 変えたのに変えた後の判定が無いか語彙の外")
            continue
        if k == "除外" and l_ not in E_ECODES:
            v.append(f"{x[0]}: 除外に変えたのに除外理由が無いか語彙の外")
        if k != "除外" and not blank(l_):
            v.append(f"{x[0]}: {k}に変えたのに除外理由がある")
        if blank(m):
            v.append(f"{x[0]}: 変えたのに理由が無い")
        if (k, l_) == ("除外", f.get("N")):
            v.append(f"{x[0]}: 変えると言いながら 1 回目と同じ")
        ai_pair = (ai[0], en(ai[1]) if ai[0] == "除外" else None)
        new_pair = (k, en(l_) if k == "除外" else None)
        if j == "AI の判定に変える" and new_pair != ai_pair:
            v.append(f"{x[0]}: AI の判定に変えると言いながら AI と違う（{new_pair} / {ai_pair}）")
        if j == "別の判定に変える" and new_pair == ai_pair:
            v.append(f"{x[0]}: 別の判定と言いながら AI と同じ")
    return v


def missing(ctx):
    return [x[0] for r, x in body(ctx["wb"]["2 回目"]) if blank(x[9])]


def r_complete(ctx):
    m = missing(ctx)
    return [f"未記入 {len(m)} 件"] if m else []


RULES_COMMON = [
    r_sheets,
    r_rows,
    r_first,
    r_title,
    r_ai,
    r_validation,
]
RULES_BLANK = [
    r_blank,
]
RULES_FILLED = [
    r_unchanged,
    r_vocab,
]
RULES_FINAL = [
    r_complete,
]


def recorded(key):
    if os.path.exists(C.TA_SHA_RECORD):
        for line in open(C.TA_SHA_RECORD, encoding="utf-8"):
            if line.startswith(key + " "):
                return line.split()[1]
    return None


def check(path, src, mode="blank", final=False, orig_path=None, orig_sha=None):
    ctx = {"wb": openpyxl.load_workbook(path), "src": src, "orig_path": orig_path or C.TA_SHEET2_ORIG,
           "orig_sha": orig_sha or recorded("sheet2")}
    v = []
    for rule in RULES_COMMON + (RULES_BLANK if mode == "blank" else RULES_FILLED) + (RULES_FINAL if final else []):
        try:
            v += rule(ctx)
        except Exception as e:
            v.append(f"{rule.__name__}: 例外 {type(e).__name__}: {e}")
    return v, (missing(ctx) if mode == "filled" else [])


def selftest():
    import build_ta2_sheet as B
    tmpd = tempfile.mkdtemp(prefix="ta2-self-")
    # 自前のログ: 未判定の追加候補の先頭 24 件を除外にする（E コードを回す・AI と同じ件と違う件が混ざる）
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    judged = {json.loads(l)["item"] for l in open(C.PREV_LOG, encoding="utf-8")}
    ids = [r[0] for r in list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))[C.JUDGE_HEADER_ROW:] if r and r[0] and r[0] not in judged]
    log = os.path.join(tmpd, "log.jsonl")
    open(log, "w").close()
    ai = sources(log)["ai"]
    to_code = {"E1": "E1", "E2": "E2", "E3": "E3", "E4": "E4 背景（レビュー・尺度の原著・理論）", "E5": "E5", "E7": "E7"}
    # AI が除外した記録の 12 件は AI と同じコード（同じ）・AI が含めた記録の 12 件は E2（違う）・残りは含める
    same_ids = [i for i in ids if ai[i][0] == "除外" and en(ai[i][1]) in to_code][:12]
    diff_ids = [i for i in ids if ai[i][0] != "除外"][:12]
    with open(log, "w", encoding="utf-8") as f:
        for n, i in enumerate(ids):
            if i in same_ids:
                cells = {"M": "除外", "N": to_code[en(ai[i][1])], "O": "メモ" if i == same_ids[0] else None}
            elif i in diff_ids:
                cells = {"M": "除外", "N": "E2", "O": None}
            else:
                cells = {"M": "含める", "N": None, "O": None}
            f.write(json.dumps({"item": i, "stage": "ta1", "cells": cells}, ensure_ascii=False) + "\n")
    old = C.LOG
    C.LOG = log
    try:
        base = os.path.join(tmpd, "base.xlsx")
        B.build().save(base)
    finally:
        C.LOG = old
    src = sources(log)
    ok = True

    def expect(name, path, red, **kw):
        nonlocal ok
        v, _ = check(path, src, **kw)
        good = bool(v) == red
        ok &= good
        print(("PASS" if good else "FAIL"), name, "" if good else v[:3])

    expect("陰性対照（作ったまま）", base, False)
    rows = body(openpyxl.load_workbook(base)["2 回目"])
    same_r = next(r for r, x in rows if is_same(src["first"][x[0]], src["ai"][x[0]]))
    diff_rows = [(r, x) for r, x in rows if not is_same(src["first"][x[0]], src["ai"][x[0]])]
    diff_r, diff_x = diff_rows[0]
    print(f"  （対象 {len(rows)} 件・AI と同じ {len(rows) - len(diff_rows)} 件・違う {len(diff_rows)} 件）")

    def mut(name, fn, red=True, path=None, **kw):
        p = os.path.join(tmpd, f"m{abs(hash(name))}.xlsx")
        wb = openpyxl.load_workbook(path or base)
        fn(wb)
        wb.save(p)
        expect(name, p, red, **kw)

    s2 = "2 回目"
    mut("シートを足す", lambda wb: wb.create_sheet("x"))
    mut("見出しを変える", lambda wb: setattr(wb[s2].cell(HR, 10), "value", "2 回目"))
    mut("行を消す", lambda wb: wb[s2].delete_rows(HR + 2))
    mut("1 回目の欄を変える", lambda wb: setattr(wb[s2].cell(HR + 1, 3), "value", "除外 ／ E7"))
    mut("題名を変える", lambda wb: setattr(wb[s2].cell(HR + 1, 2), "value", "x"))
    mut("AI の値を変える", lambda wb: setattr(wb[s2].cell(HR + 1, 8), "value", "根拠を変えた"))
    mut("同じ／違うの選択肢を入れ替える", lambda wb: [setattr(dv, "formula1", '"' + ",".join(E_DIFF) + '"')
                                              for dv in wb[s2].data_validations.dataValidation
                                              if (dv.formula1 or "").strip('"') == ",".join(E_SAME)])
    mut("記入前に記入", lambda wb: setattr(wb[s2].cell(HR + 1, 10), "value", "1 回目のまま"))

    rec = C.sha256(base)
    filled = os.path.join(tmpd, "filled.xlsx")
    wb = openpyxl.load_workbook(base)
    for r, x in body(wb[s2]):
        wb[s2].cell(r, 10).value = "1 回目のまま"
    ai0 = src["ai"][diff_x[0]]
    wb[s2].cell(diff_r, 10).value = "AI の判定に変える"
    wb[s2].cell(diff_r, 11).value = ai0[0]
    if ai0[0] == "除外":
        wb[s2].cell(diff_r, 12).value = next(c for c in E_ECODES if en(c) == en(ai0[1]))
    wb[s2].cell(diff_r, 13).value = "AI の根拠に納得"
    wb.save(filled)
    kw = {"mode": "filled", "final": True, "orig_path": base, "orig_sha": rec}
    expect("記入済みの対照（--final・AI に変えた 1 件を含む）", filled, False, **kw)

    def fm(name, fn, red=True, **extra):
        mut(name, fn, red, path=filled, **{**kw, **extra})

    fm("同じ記録に「AI の判定に変える」", lambda w: setattr(w[s2].cell(same_r, 10), "value", "AI の判定に変える"))
    fm("1 回目のままなのに変えた後の判定", lambda w: setattr(w[s2].cell(same_r, 11), "value", "含める"))
    fm("変えたのに判定なし", lambda w: [setattr(w[s2].cell(same_r, 10), "value", "変える")])
    fm("除外に変えたのに理由コードなし", lambda w: [setattr(w[s2].cell(same_r, 10), "value", "変える"),
                                            setattr(w[s2].cell(same_r, 11), "value", "除外"),
                                            setattr(w[s2].cell(same_r, 13), "value", "理由")])
    fm("含めるに変えたのに除外理由", lambda w: [setattr(w[s2].cell(same_r, 10), "value", "変える"),
                                          setattr(w[s2].cell(same_r, 11), "value", "含める"),
                                          setattr(w[s2].cell(same_r, 12), "value", "E1"),
                                          setattr(w[s2].cell(same_r, 13), "value", "理由")])
    fm("変えたのに理由なし", lambda w: setattr(w[s2].cell(diff_r, 13), "value", None))
    fm("変えると言いながら 1 回目と同じ", lambda w: [setattr(w[s2].cell(same_r, 10), "value", "変える"),
                                               setattr(w[s2].cell(same_r, 11), "value", "除外"),
                                               setattr(w[s2].cell(same_r, 12), "value", src["first"][body(w[s2])[same_r - HR - 1][1][0]]["N"]),
                                               setattr(w[s2].cell(same_r, 13), "value", "理由")])
    fm("AI に変えると言いながら AI と違う", lambda w: setattr(w[s2].cell(diff_r, 11), "value",
                                                     "保留" if ai0[0] != "保留" else "含める"))
    fm("別の判定と言いながら AI と同じ", lambda w: setattr(w[s2].cell(diff_r, 10), "value", "別の判定に変える"))
    fm("記入欄の外を変える", lambda w: setattr(w[s2].cell(HR + 1, 9), "value", "x"))
    fm("記入漏れ（--final）", lambda w: setattr(w[s2].cell(HR + 1, 10), "value", None) if HR + 1 != diff_r
       else setattr(w[s2].cell(HR + 2, 10), "value", None))
    fm("原本の SHA が違う", lambda w: None, orig_sha="0" * 64)
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main():
    a = sys.argv[1:]
    if "--selftest" in a:
        sys.exit(0 if selftest() else 1)
    src = sources()
    path = a[a.index("--path") + 1] if "--path" in a else C.TA_SHEET2
    if "--path" not in a and "--filled" not in a and C.sha256(path) != recorded("sheet2"):
        print("違反: Downloads の記入表 2 が記録した SHA-256 と違う（記入前の検査）")
        sys.exit(1)
    mode = "filled" if "--filled" in a else "blank"
    v, miss = check(path, src, mode=mode, final="--final" in a)
    for x in v:
        print("違反:", x)
    if v:
        print(f"違反 {len(v)} 件")
        sys.exit(1)
    if mode == "filled" and miss:
        print(f"記入の途中: 未記入 {len(miss)} 件")
        sys.exit(2)
    print("違反 0")


if __name__ == "__main__":
    main()
