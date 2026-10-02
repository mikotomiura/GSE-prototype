"""提案のドキュメント v2 の検査（design.md §11 を判断 5・6 に合わせて縮めた形・引き継ぎ §2 の 4）。

★ 期待は書き込み側（build_proposal.py は追加候補の表から数える）と独立に組む: ログ（前のタスク・本タスク）・判定者用ファイル・
  評価版・34 件の写しと 34 件のログ・探索の data を自分で読んで数える。
★ 規則は RULES_* に 1 行 1 つ（meta_mutate.py が 1 行ずつ外す）。違反の文は規則の名前で始める。
★ 判断 5: 判定者 1 が判定していない記録は「AI の予備判定」「人の判定ではない」と書き分ける。判断 6: E4 背景は意図を書く。
★ 単独の版（前の版に触れない）・研究者は repo と作業の語を知らない。
使い方: check_proposal.py | --selftest
"""
import json
import os
import re
import shutil
import sys
import tempfile

import openpyxl
from docx import Document

import common as C

MD = os.path.join(C.TASK, "proposal", "proposal-v2.md")
DOCX_NAME = "AI疲労DB_判定者1からの提案_v2.docx"
DOCX_ARCHIVE = os.path.join(C.TASK, "archive", DOCX_NAME)
DOCX_DOWNLOADS = os.path.join(C.DOWNLOADS, DOCX_NAME)
SHA_RECORD = os.path.join(C.TASK, "archive", "proposal-sha256.txt")
LOG34 = os.path.join(C.STEER, "20261001-ai-fatigue-34-screening", "screening-log.jsonl")
WARN = "判定者 2 に渡さない"
# ★ 作業の語・内部の参照・前の版への言及（研究者は repo を読めない・単独の版）
BANNED = re.compile(r"GSE|\.steering|scratchpad|screening-log|cross-review|Codex|worktree|\.jsonl|check_\w+\.py|build_\w+\.py|"
                    r"判断 ?\d|設計 ?§|\bv1\b|v2|前の版|ta1e?\b|ai_ta|評価版（ed78|記入表", re.I)
BLOCKS = {"counts": "## 1 ", "pop": "## 7 ", "agree": "## 7 ", "search43": "## 7 ", "appendix": "## 8 "}
USE34_E4 = {"既存レビュー": "背景保持", "尺度・理論": "背景保持", "方法論": "方法論保持", "訂正通知": "訂正連結",
            "直接研究": "背景保持", "隣接研究": "背景保持"}
USEC_E4 = {"レビュー": "背景保持", "論考": "背景保持", "研究計画": "背景保持", "一次研究": "背景保持",
           "方法論": "方法論保持", "訂正通知": "訂正連結"}
BASIS_C = {"全文": "全文", "抄録": "抄録", "なし": "題名と書誌だけ"}
BASIS34 = {"全文": "全文", "抄録": "抄録", "なし": "なし"}
POP = ["学生・学習者", "教員・研究者", "働く人（医療・教育の外）", "医療者", "消費者・一般の利用者", "不明"]
VS = ("含める", "保留", "除外")


def read_log(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def finals(log):
    """前の作業の形のログ → 件ごとの最終（2/2e の最後・無ければ 1/1e の最後）。"""
    first, second = {}, {}
    for r in log:
        if r["stage"] in ("1", "1e"):
            first[r["item"]] = r["result"]
        elif r["stage"] in ("2", "2e"):
            second[r["item"]] = r["result"]
    return {i: second.get(i, first[i]) for i in first}


def use_label(res, e4_kind):
    v, e = res["verdict"], res.get("ecode")
    if v == "含める":
        return res["use"]
    if v == "保留" or e == "E6":
        return "保留"
    if e == "E2":
        return "背景保持"
    if e == "E4":
        return e4_kind
    return "除外"


def short_ok(md_title, full):
    t = re.sub(r"\s+", " ", full or "").strip().replace("|", "／")
    m = md_title.rstrip("…")
    return t == md_title or (md_title.endswith("…") and t.startswith(m) and len(m) >= 20)


def sources():
    s = {"md": open(MD, encoding="utf-8").read()}
    jw = openpyxl.load_workbook(C.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(jw[C.JUDGE_SHEET].iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    ic = next(k for k, c in enumerate(h) if c and str(c).startswith("内容の群"))
    s["title"] = {r[0]: r[h.index("題名（書誌の記録）")] for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]}
    s["content"] = {r[0]: r[ic] for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0]}
    for x in json.load(open(C.PREV_EXTRA_RECORDS, encoding="utf-8")):
        s["title"][x["id"]] = x["title"]
    s["prev"] = finals(read_log(C.PREV_LOG))
    j1, ai = {}, {}
    for r in read_log(C.LOG):
        if r["stage"] in ("ta1", "ta1e"):
            j1[r["item"]] = r["result"]
        elif r["stage"] == "ai_ta":
            ai[r["item"]] = r["result"]
    s["j1"], s["ai"] = j1, ai
    aw = openpyxl.load_workbook(C.APPRAISAL, read_only=True, data_only=True)
    rr = list(aw["Claudeスクリーニング案"].iter_rows(values_only=True))
    k = next(k for k, r in enumerate(rr) if r and r[0] == "候補番号")
    hh = list(rr[k])
    s["ai_ta"] = {r[0]: (r[hh.index("Claude予備判定（題名・抄録段）")], r[hh.index("除外理由")]) for r in rr[k + 1:] if r and r[0]}
    w = openpyxl.load_workbook(C.COPY34_ARCHIVE, read_only=True)["スクリーニング"]
    s["copy34"] = [list(r) for r in w.iter_rows(min_row=5, max_row=38, values_only=True)]
    s["log34"] = finals(read_log(LOG34))
    recs = json.load(open(C.SEARCH_RECORDS, encoding="utf-8"))
    s["search43"] = sorted(((r["reading"], r["title"], r.get("year")) for r in recs
                            if re.fullmatch(r"R\d\d", r.get("reading") or "") and not r.get("overlap")))
    return s


def table_after(md, anchor):
    """anchor の後の最初の表（見出し行と区切りを除く行のセルの列）。次の見出しで止まる。"""
    i = md.index(anchor)
    out, seen = [], False
    for line in md[i:].splitlines()[1:]:
        if line.startswith("#"):
            break
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not seen:
                seen = True
                continue
            if all(re.fullmatch(r"-+", c) for c in cells):
                continue
            out.append(cells)
        elif seen and line.strip():
            break
    return out


def norm(s):
    s = re.sub(r"\*\*|`", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def md_texts(md):
    out = []
    for line in md.splitlines():
        t = line.strip()
        if not t or t.startswith("<!--"):
            continue
        if t.startswith("|"):
            cells = [c.strip() for c in t.strip("|").split("|")]
            if all(re.fullmatch(r"-+", c) for c in cells):
                continue
            out += [norm(c) for c in cells]
            continue
        out.append(norm(re.sub(r"^(#{1,3} |- )", "", t)))
    return [x for x in out if x]


def docx_texts(path):
    out = []
    for el in Document(path).element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            t = "".join(x.text or "" for x in el.iter() if x.tag.endswith("}t"))
            if t.strip():
                out.append(norm(t))
        elif tag == "tbl":
            for tc in el.iter():
                if tc.tag.endswith("}tc"):
                    out.append(norm("".join(x.text or "" for x in tc.iter() if x.tag.endswith("}t"))))
    return [x for x in out if x]


# ---------------------------------------------------------------- 規則
def r_heads(ctx):
    heads = re.findall(r"^## (\d) ", ctx["md"], re.M)
    return [] if heads == [str(k) for k in range(10)] else [f"r_heads: 見出し ## 0〜## 9 の並びが違う: {heads}"]


def r_warn(ctx):
    paras = [p for p in ctx["md"].split("\n\n") if p.strip() and not p.strip().startswith("<!--")]
    return [] if any(WARN in p for p in paras[:5]) else ["r_warn: 冒頭の 5 段落に「判定者 2 に渡さない」が無い"]


def r_banned(ctx):
    v = [f"r_banned: 禁止の語: {m.group(0)}" for m in BANNED.finditer(ctx["md"])]
    for line in ctx["md"].splitlines():
        m = C.find_local(line)
        if m:
            v.append(f"r_banned: 手元のパス・ユーザー名・メールアドレス: {m.group(0)}")
    return v[:10]


def r_blocks(ctx):
    v, md = [], ctx["md"]
    for name, sec in BLOCKS.items():
        b, e = f"<!-- {name}:begin -->", f"<!-- {name}:end -->"
        if md.count(b) != 1 or md.count(e) != 1 or md.index(b) > md.index(e):
            v.append(f"r_blocks: 自動の区画 {name} が 1 組でない")
            continue
        i = md.index(b)
        heads = [m for m in re.finditer(r"^## \d ", md, re.M) if m.start() < i]
        if not heads or not md[heads[-1].start():].startswith(sec):
            v.append(f"r_blocks: 自動の区画 {name} が {sec.strip()} の中に無い")
        if not md[i + len(b):md.index(e)].strip():
            v.append(f"r_blocks: 自動の区画 {name} が空")
    return v


def r_counts(ctx):
    """§1 の数（判定者 1 と AI の内訳）を、ログと評価版から独立に数えて、文に出ているか。"""
    s, md = ctx["src"], ctx["md"]
    pv = [r["verdict"] for r in s["prev"].values()]
    jv = [r["verdict"] for r in s["j1"].values()]
    av = [s["ai_ta"][i][0] for i in s["ai"]]
    n_all = len(s["title"])
    med = [i for i, c in s["content"].items() if str(c or "").startswith("医療者")]
    med_ai = [i for i in med if i in s["ai"]]
    e4 = sum(1 for r in s["j1"].values() if str(r.get("ecode") or "").startswith("E4 背景"))
    want = [f"計 {n_all} 件のうち、判定者 1 が判定したのは {len(pv) + len(jv)} 件",
            f"全文段で {len(pv)} 件（除外 {pv.count('除外')}・保留 {pv.count('保留')}・含める {pv.count('含める')}）",
            f"題名・抄録段で {len(jv)} 件（含める {jv.count('含める')}・保留 {jv.count('保留')}・除外 {jv.count('除外')}）",
            f"除外のうち {e4} 件は、判定者 1 の意図が「範囲の外・背景として残す」",
            f"残りの {len(av)} 件は判定者 1 が判定していません",
            f"予備判定（含める {av.count('含める')}・除外 {av.count('除外')}）だけで、人の判定ではありません",
            (f"医療者の記録 {len(med)} 件は、すべてこちら" if len(med_ai) == len(med) else f"医療者の記録 {len(med)} 件のうち {len(med_ai)} 件"),
            f"含める・保留にした {jv.count('含める') + jv.count('保留')} 件の全文段"]
    i, j = md.index("<!-- counts:begin -->"), md.index("<!-- counts:end -->")
    block = md[i:j]
    return [f"r_counts: §1 の数が独立に数えた値と違う（期待「{w}」）" for w in want if w not in block]


def r_pop(ctx):
    s = ctx["src"]
    want = []
    for p in POP + ["計"]:
        ids = [i for i in list(s["j1"]) + list(s["ai"]) if p == "計" or str(s["content"][i]).split("｜")[0] == p]
        if not ids:
            continue
        j = [s["j1"][i]["verdict"] for i in ids if i in s["j1"]]
        a = [s["ai_ta"][i][0] for i in ids if i in s["ai"]]
        want.append([p, str(len(ids)), str(len(j)), "・".join(str(j.count(x)) for x in VS), str(len(a)), "・".join(str(a.count(x)) for x in VS)])
    got = table_after(ctx["md"], "<!-- pop:begin -->")
    return [] if got == want else [f"r_pop: 対象者ごとの表が独立に数えた値と違う（{len(got)} 行 / {len(want)}）"]


def r_agree(ctx):
    s, v = ctx["src"], []
    pairs = {i: (r["verdict"], s["ai_ta"][i][0]) for i, r in s["j1"].items()}
    want = []
    for x in VS:
        n = [sum(1 for a, b in pairs.values() if a == x and b == y) for y in VS]
        want.append([x] + [str(k) for k in n] + [str(sum(n))])
    n = [sum(1 for a, b in pairs.values() if b == y) for y in VS]
    want.append(["計"] + [str(k) for k in n] + [str(sum(n))])
    if table_after(ctx["md"], "<!-- agree:begin -->") != want:
        v.append("r_agree: 一致の表（判定者 1 × AI）が独立に数えた値と違う")
    same = sum(1 for a, b in pairs.values() if a == b)
    both = [i for i, (a, b) in pairs.items() if a == b == "除外"]
    bg = [i for i in both if str(s["j1"][i].get("ecode") or "").startswith("E4 背景")]
    code_same = sum(1 for i in both if i not in bg and re.match(r"(E\d)", s["ai_ta"][i][1] or "").group(1) == s["j1"][i]["ecode"])
    i0, i1 = ctx["md"].index("<!-- agree:begin -->"), ctx["md"].index("<!-- agree:end -->")
    block = ctx["md"][i0:i1]
    for w in (f"判定が一致したのは {len(pairs)} 件中 {same} 件", f"両方が除外の {len(both)} 件のうち、除外理由（E コード）が一致したのは {code_same} 件",
              f"比べなかったのは {len(bg)} 件"):
        if w not in block:
            v.append(f"r_agree: 一致の文が独立に数えた値と違う（期待「{w}」）")
    diff = sorted(i for i, (a, b) in pairs.items() if a != b)
    m = re.search(r"判定が一致しなかった (\d+) 件：(.*)。", block)
    got = sorted(re.findall(r"(S\d\d-\d\d)（判定者 1 (\S+?)・AI (\S+?)）", m.group(2))) if m else []
    if not m or int(m.group(1)) != len(diff) or [g[0] for g in got] != diff or \
            any((g[1], g[2]) != pairs[g[0]] for g in got):
        v.append("r_agree: 一致しなかった記録の列挙が独立に組んだ値と違う")
    return v


def r_search43(ctx):
    got = table_after(ctx["md"], "<!-- search43:begin -->")
    want = ctx["src"]["search43"]
    if len(got) != len(want) or len(want) != 43:
        return [f"r_search43: 探索の一覧が {len(got)} 行（data は {len(want)}・43 のはず）"]
    for g, (rid, title, year) in zip(got, want):
        if g[0] != rid or not short_ok(g[1], title) or g[2] != str(year or ""):
            return [f"r_search43: {rid}: 番号・題名・年が data と違う"]
    return []


def r_app91(ctx):
    s = ctx["src"]
    want = []
    for r in s["copy34"]:
        x = s["log34"].get(r[0])
        want.append((r[0], r[3], use_label(x, USE34_E4.get(r[2])) if x else "（ログに無い）",
                     BASIS34.get(x.get("basis", "全文"), "（語彙の外）") if x else "（ログに無い）"))
    got = [(c[0], c[2], c[3], c[4]) for c in table_after(ctx["md"], "### 9.1")]
    titles = all(short_ok(c[1], r[1]) for c, r in zip(table_after(ctx["md"], "### 9.1"), s["copy34"]))
    return [] if got == want and titles else ["r_app91: 付録 9.1 が 34 件の判定（写しの判定者1・ログの用途と材料）と違う"]


def r_app92(ctx):
    s = ctx["src"]
    want = []
    for i, r in s["prev"].items():
        want.append((i, r["verdict"], r.get("ecode") if r["verdict"] == "除外" else "—", "全文段",
                     use_label(r, USEC_E4.get(r.get("kind_detail"))), BASIS_C.get(r.get("basis", "全文"), "（語彙の外）")))
    for i, r in s["j1"].items():
        g = "—" if r["verdict"] != "除外" else ("E4 背景" if str(r.get("ecode") or "").startswith("E4 背景") else r["ecode"])
        want.append((i, r["verdict"], g, "題名・抄録段", {"含める": "未定", "保留": "保留", "除外": "背景保持"}[r["verdict"]], "抄録"))
    rows = table_after(ctx["md"], "### 9.2")
    got = [(c[0], c[2], c[3], c[4], c[5], c[6]) for c in rows]
    titles = all(short_ok(c[1], s["title"].get(c[0])) for c in rows)
    return [] if sorted(got) == sorted(want) and len(got) == len(want) and titles else \
        [f"r_app92: 付録 9.2 が判定者 1 の判定（前の作業と今回のログ）と違う（{len(got)} 行 / {len(want)}）"]


def r_app93(ctx):
    s = ctx["src"]
    want = sorted((i, s["ai_ta"][i][0], (re.match(r"(E\d)", s["ai_ta"][i][1] or "").group(1) if s["ai_ta"][i][0] == "除外" else "—"))
                  for i in s["ai"])
    rows = table_after(ctx["md"], "### 9.3")
    got = sorted((c[0], c[2], c[3]) for c in rows)
    i = ctx["md"].index("### 9.3")
    head = ctx["md"][i:ctx["md"].index("|", i)]
    titles = all(short_ok(c[1], s["title"].get(c[0])) for c in rows)
    v = [] if got == want and titles else [f"r_app93: 付録 9.3 が AI の予備判定（ログと評価版）と違う（{len(got)} 行 / {len(want)}）"]
    if "人の判定ではありません" not in head or "AI" not in head:
        v.append("r_app93: 付録 9.3 に「AI の予備判定・人の判定ではない」の注意が無い")
    return v


def r_docx_text(ctx):
    mt, dt = md_texts(ctx["md"]), docx_texts(ctx["docx"])
    if mt == dt:
        return []
    k = next((k for k, (x, y) in enumerate(zip(mt, dt)) if x != y), min(len(mt), len(dt)))
    return [f"r_docx_text: .docx の本文が原稿と違う（{k} 番目・原稿 {mt[k:k + 1]} / docx {dt[k:k + 1]}）"]


def r_docx_props(ctx):
    cp = Document(ctx["docx"]).core_properties
    v = []
    if "python-docx" in (cp.comments or "") or not cp.created or cp.created.year < 2026 or cp.author != "判定者 1" \
            or cp.last_modified_by != "判定者 1" or cp.title != "AI 疲労の文献 DB：判定者 1 からの報告と提案":
        v.append(f"r_docx_props: .docx の属性が雛形のまま・違う（author={cp.author!r}・title={cp.title!r}）")
    for x in (cp.title, cp.subject, cp.keywords, cp.comments, cp.category):
        if x and BANNED.search(x):
            v.append("r_docx_props: .docx の属性に禁止の語")
    return v


def r_docx_scan(ctx):
    return [f"r_docx_scan: .docx に手元のパス・メールアドレスの形・外へのリンク: {x}" for x in C.scan_package(ctx["docx"])]


RULES_PROPOSAL = [
    r_heads,
    r_warn,
    r_banned,
    r_blocks,
    r_counts,
    r_pop,
    r_agree,
    r_search43,
    r_app91,
    r_app92,
    r_app93,
    r_docx_text,
    r_docx_props,
    r_docx_scan,
]


def check(md, docx_path, src):
    ctx = {"md": md, "docx": docx_path, "src": src}
    v = []
    for rule in RULES_PROPOSAL:
        try:
            v += rule(ctx)
        except Exception as e:
            v.append(f"{rule.__name__}: 例外 {type(e).__name__}: {e}")
    return v


def selftest():
    import build_proposal as B
    ok = True
    src = sources()
    _, md = B.compose_md()  # ★ 自動の区画を作り直した原稿（書き戻さない）
    tmpd = tempfile.mkdtemp(prefix="propchk-")

    def run(name, md2, must=None, mutate_docx=None):
        nonlocal ok
        p = os.path.join(tmpd, "t.docx")
        B.build_docx(md2, p)
        if mutate_docx:
            d = Document(p)
            mutate_docx(d)
            d.save(p)
        v = check(md2, p, {**src, "md": md2})
        good = (not v) if must is None else any(x.startswith(must) for x in v)
        ok &= good
        print(("PASS" if good else "FAIL"), name, "" if good else v[:3])

    def sub(old, new, count=1):
        assert old in md, old
        return md.replace(old, new, count)

    def row(prefix, col, new):
        ls = md.splitlines()
        k = next(i for i, x in enumerate(ls) if x.startswith(prefix))
        cells = ls[k].strip().strip("|").split("|")
        cells[col] = f" {new} "
        ls[k] = "|" + "|".join(cells) + "|"
        return "\n".join(ls)

    run("陰性対照（実の原稿で作った .docx）", md)
    run("見出しを消す", sub("\n## 4 ", "\n## X "), "r_heads")
    run("注意を冒頭から外す", sub(WARN, "判定者 2 にお渡しにならない"), "r_warn")
    run("作業の語（GSE）", md + "\nGSE の話\n", "r_banned")
    run("前の版に触れる（v1）", md + "\nv1 からの変更\n", "r_banned")
    run("内部の参照（判断 5）", md + "\n判断 5 のとおり\n", "r_banned")
    run("ログの段の名前（ai_ta）", md + "\nai_ta の行\n", "r_banned")
    run("手元のパス", md + "\nC:/wt/x を見た\n", "r_banned")
    run("自動の区画を 2 つにする", md + "\n<!-- pop:begin -->\n| a |\n<!-- pop:end -->\n", "r_blocks")
    run("自動の区画を §1 から §2 へ動かす", md.replace("<!-- counts:begin -->", "").replace("<!-- counts:end -->", "")
        .replace("## 3 決めていただきたいこと", "<!-- counts:begin -->\n- x\n<!-- counts:end -->\n\n## 3 決めていただきたいこと"), "r_blocks")
    run("§1 の判定者 1 の数を変える", sub("含める 49・保留 15・除外 7", "含める 50・保留 14・除外 7"), "r_counts")
    run("§1 の AI の数を変える", sub("含める 83・除外 59", "含める 84・除外 58"), "r_counts")
    run("§1 から「人の判定ではありません」を消す", sub("だけで、人の判定ではありません", "だけです"), "r_counts")
    run("対象者の表の数を変える", row("| 医療者 |", 2, "1"), "r_pop")
    run("一致の表の数を変える", row("| 保留 | 14 |", 1, "13"), "r_agree")
    run("一致の文の数を変える", sub("判定が一致したのは 71 件中 48 件", "判定が一致したのは 71 件中 49 件"), "r_agree")
    run("一致しなかった記録を 1 件落とす", sub("S12-03（判定者 1 含める・AI 除外）／", ""), "r_agree")
    run("探索の一覧の年を変える", row("| R01 |", 2, "1999"), "r_search43")
    run("探索の一覧の行を消す", "\n".join(x for x in md.splitlines() if not x.startswith("| R05 |")), "r_search43")
    run("付録 9.1 の用途をずらす", row("| AF001 |", 3, "中心-B"), "r_app91")
    run("付録 9.2 の判定者 1 の判定をずらす", row("| S02-06 |", 2, "保留"), "r_app92")
    run("付録 9.2 の E4 背景を E4 と書く（判断 6）", row("| S04-85 |", 3, "E4"), "r_app92")
    run("付録 9.2 に AI の行を混ぜる（判断 5）", md.replace("| S02-06 |", "| S14-23 | Burnout | 含める | — | 題名・抄録段 | 未定 | 抄録 |\n| S02-06 |", 1),
        "r_app92")
    run("付録 9.2 の前の作業の材料をずらす", row("| S08-03 |", 6, "全文"), "r_app92")
    run("付録 9.3 の AI の判定をずらす", row("| S02-10 |", 2, "含める"), "r_app93")
    run("付録 9.3 から注意を消す", sub("★ 人の判定ではありません。", "★ "), "r_app93")
    run("付録 9.3 の題名を別の記録のものにする", row("| S02-05 |", 1, "Ambient AI Scribes in Clinical Practice: A Randomized Trial."), "r_app93")

    def para(d):
        for p in d.paragraphs:
            if p.text.startswith("宛先"):
                p.runs[0].text = "宛先：別の人"
                break
    run(".docx の段落を変える", md, "r_docx_text", para)
    run(".docx の属性が雛形", md, "r_docx_props", lambda d: setattr(d.core_properties, "comments", "generated by python-docx"))
    run(".docx の属性に手元のパス", md, "r_docx_scan", lambda d: setattr(d.core_properties, "category", "C:/wt/x"))
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    src = sources()
    v = check(src["md"], DOCX_ARCHIVE, src)
    rec = open(SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(SHA_RECORD) else None
    for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):
        if not os.path.exists(p) or C.sha256(p) != rec:
            v.append(f".docx の SHA-256 が記録と違う・無い: {os.path.basename(p)}")
    for e in v:
        print("違反:", e)
    print(f"違反 {len(v)}")
    sys.exit(1 if v else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
