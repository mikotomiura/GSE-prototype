"""提案のドキュメント v1 の検査（design.md §8・requirement.md の受け入れ条件）。

(1) .docx の本文（段落と表のセル）が原稿の Markdown と一致する（記号を落として、空でない文の列で比べる）。
(2) 見出し「## 0」〜「## 9」がこの順で 1 回ずつある。
(3) 冒頭の 5 段落以内に「判定者 2 に渡さない」がある。
(4) 禁止: 内部の名前・手元のパス・メールアドレス（研究者は repo を読めない・GSE を知らない）。
(5) 付録の 34 行が 34 件の写しの判定者1 と、追加候補の行が追加候補の表の判定者1 と一致する（本検査器が独立に読む）。
(6) archive と Downloads の .docx の SHA-256 が記録と同じ。
--selftest: 実の原稿で作った .docx が緑・変異（見出しを消す・注意を冒頭から外す・禁止語・付録の行をずらす・.docx の段落を変える）が赤。
使い方: python check_proposal.py [--selftest]
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

MD = os.path.join(C.TASK, "proposal", "proposal-v1.md")
DOCX_NAME = "AI疲労DB_判定者1からの提案_v1.docx"
DOCX_ARCHIVE = os.path.join(C.TASK, "archive", DOCX_NAME)
DOCX_DOWNLOADS = os.path.join(C.DOWNLOADS, DOCX_NAME)
SHA_RECORD = os.path.join(C.TASK, "archive", "proposal-sha256.txt")
WARN = "判定者 2 に渡さない"
# ★ 作業の語（GSE・道具の名前など）は BANNED、手元のパス・ユーザー名・メールアドレスは common.find_local（判断 11・12）
BANNED = re.compile(r"GSE|\.steering|scratchpad|screening-log|/cross-review|cross-review|Codex|worktree|\.jsonl|"
                    r"check_\w+\.py|build_\w+\.py", re.I)
LOG34 = os.path.join(C.STEER, "20261001-ai-fatigue-34-screening", "screening-log.jsonl")
# 付録の用途（★ build_proposal.py は写しの自由記入から読む。本検査器はログの最終の判定から独立に組む）
USE34_E4 = {"既存レビュー": "背景保持", "尺度・理論": "背景保持", "方法論": "方法論保持", "訂正通知": "訂正連結",
            "直接研究": "背景保持", "隣接研究": "背景保持"}
USEC_E4 = {"レビュー": "背景保持", "論考": "背景保持", "研究計画": "背景保持", "一次研究": "背景保持",
           "方法論": "方法論保持", "訂正通知": "訂正連結"}
BASIS_LABEL = {"全文": "全文", "抄録": "抄録", "なし": "題名と書誌だけ"}  # 追加候補の表の自由記入の書き方
BASIS34 = {"全文": "全文", "抄録": "抄録", "なし": "なし"}  # 34 件の写しの自由記入の書き方（前のタスクの道具は生の値を書く）


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
        t = re.sub(r"^(#{1,3} |- )", "", t)
        out.append(norm(t))
    return [x for x in out if x]


def docx_texts(path):
    d = Document(path)
    out = []
    body = d.element.body
    for el in body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            t = "".join(x.text or "" for x in el.iter() if x.tag.endswith("}t"))
            if t.strip():
                out.append(norm(t))
        elif tag == "tbl":
            for tc in el.iter():
                if tc.tag.endswith("}tc"):
                    t = "".join(x.text or "" for x in tc.iter() if x.tag.endswith("}t"))
                    out.append(norm(t))
    return [x for x in out if x]


def final_results(path):
    """ログ → 件ごとの最終の判定（2/2e の最後・無ければ 1/1e の最後）と、2 回目があるか。"""
    first, second = {}, {}
    for x in open(path, encoding="utf-8"):
        if x.strip():
            r = json.loads(x)
            if r["stage"] in ("1", "1e"):
                first[r["item"]] = r["result"]
            elif r["stage"] in ("2", "2e"):
                second[r["item"]] = r["result"]
    return {i: second.get(i, first[i]) for i in first}, set(second)


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


def expected_appendix():
    """本検査器が独立に組む付録の行: 34 件 = (ID, 判定者1, 用途, 材料)・追加候補 = (ID, 判定者1, 用途, 材料, AI の判定)。
    ★ 判定者1 は表から、用途・材料・AI の判定はログの最終の判定から（書き込み側は自由記入を正規表現で切り出す・判断 11）。"""
    w = openpyxl.load_workbook(C.COPY34_ARCHIVE, read_only=True)["スクリーニング"]
    res34, _ = final_results(LOG34)
    a = []
    for r in w.iter_rows(min_row=5, max_row=38, values_only=True):
        x = res34.get(r[0])
        a.append((r[0], r[3], use_label(x, USE34_E4.get(r[2])) if x else "（ログに無い）",
                  BASIS34.get(x.get("basis", "全文"), "（語彙の外）") if x else "（ログに無い）"))
    resc, has2 = final_results(C.LOG)
    c = openpyxl.load_workbook(C.CAND_ARCHIVE, read_only=True)["スクリーニング"]
    b = []
    for r in c.iter_rows(min_row=5, values_only=True):
        if r[0] is None:
            break
        if r[3] != "未判定":
            x = resc.get(r[0])
            if x is None:
                b.append((r[0], r[3], "（ログに無い）", "（ログに無い）", "（ログに無い）"))
                continue
            b.append((r[0], r[3], use_label(x, USEC_E4.get(x.get("kind_detail"))), BASIS_LABEL.get(x.get("basis", "全文"), "（語彙の外）"),
                      "Claude 版" if r[0] in has2 else "なし"))
    return a, b


def appendix_rows(md, title):
    i = md.index(title)
    rows = []
    for line in md[i:].splitlines()[1:]:
        if line.startswith("### ") or line.startswith("## "):  # ★ 付録の後の節の表を混ぜない（code-reviewer・判断 12）
            break
        if line.startswith("| ") and not line.startswith("| ID") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(tuple([cells[0]] + cells[2:]))
    return rows


def check(md, docx_path):
    errs = []
    heads = re.findall(r"^## (\d) ", md, re.M)
    if heads != [str(k) for k in range(10)]:
        errs.append(f"見出し ## 0〜## 9 の並びが違う: {heads}")
    paras = [p for p in md.split("\n\n") if p.strip() and not p.strip().startswith("<!--")]
    if not any(WARN in p for p in paras[:5]):
        errs.append("冒頭の 5 段落に「判定者 2 に渡さない」が無い")
    for m in BANNED.finditer(md):
        errs.append(f"禁止の語: {m.group(0)}")
    for line in md.splitlines():
        m = C.find_local(line)
        if m:
            errs.append(f"禁止の語（手元のパス・ユーザー名・メールアドレス）: {m.group(0)}")
    a, b = expected_appendix()
    if "### 9.1" not in md or appendix_rows(md, "### 9.1") != a:
        errs.append("付録 9.1 が 34 件の判定（写しの判定者1・ログの用途と材料）と違う")
    if "### 9.2" not in md or appendix_rows(md, "### 9.2") != b:
        errs.append("付録 9.2 が追加候補の判定（表の判定者1・ログの用途・材料・AI の判定）と違う")
    # ★ .docx の属性: 雛形の値（作成日 2013 年・「generated by python-docx」）が残っていない（判断 11）
    cp = Document(docx_path).core_properties
    if "python-docx" in (cp.comments or "") or not cp.created or cp.created.year < 2026 or cp.author != "判定者 1" \
            or cp.last_modified_by != "判定者 1":
        errs.append(f".docx の属性が雛形のまま・違う（comments={cp.comments!r}・created={cp.created}・author={cp.author!r}）")
    for v_ in (cp.title, cp.subject, cp.keywords, cp.comments, cp.category, cp.author, cp.last_modified_by):
        if v_ and BANNED.search(v_):
            errs.append(".docx の属性に禁止の語")
    # ★ 属性（core・app）・本文・リンク先など、zip の XML の部品をすべて見る（security-checker・判断 12）
    errs += [f".docx に手元のパス・メールアドレスの形・外へのリンク: {x}" for x in C.scan_package(docx_path)]
    mt, dt = md_texts(md), docx_texts(docx_path)
    if mt != dt:
        k = next((k for k, (x, y) in enumerate(zip(mt, dt)) if x != y), min(len(mt), len(dt)))
        errs.append(f".docx の本文が原稿と違う（{k} 番目・原稿 {mt[k:k+1]} / docx {dt[k:k+1]}・件数 {len(mt)} / {len(dt)}）")
    return errs


def selftest():
    import build_proposal as B
    ok = True
    md = open(MD, encoding="utf-8").read()
    tmpd = tempfile.mkdtemp(prefix="propchk-")

    def run(name, md2, red, mutate_docx=None, must=None):
        nonlocal ok
        p = os.path.join(tmpd, "t.docx")
        B.build_docx(md2, p)
        if mutate_docx:
            d = Document(p)
            mutate_docx(d)
            d.save(p)
        errs = check(md2, p)
        hit = bool(errs) if must is None else any(must in e for e in errs)
        good = hit if red else not errs
        print(("PASS" if good else "FAIL"), name, "" if good else errs[:3])
        ok &= good
    run("negative-control（実の原稿）", md, red=False)
    run("heading-removed", md.replace("\n## 4 ", "\n## X ", 1), red=True, must="見出し")
    run("warning-moved", md.replace(WARN, "判定者 2 にお渡しにならない", 1), red=True, must="冒頭の 5 段落")
    run("banned-path", md.replace("## 0 この文書について", "## 0 この文書について（C:\\Users）", 1), red=True, must="禁止の語")
    run("banned-gse", md + "\nGSE の話\n", red=True, must="禁止の語")
    run("banned-forward-slash-path", md + "\nC:/wt/x を見た\n", red=True, must="禁止の語")
    run("banned-gitbash-path", md + "\n/c/Users/x を見た\n", red=True, must="禁止の語")
    run("banned-yen-path", md + "\nC:¥wt¥x を見た\n", red=True, must="禁止の語")
    run("banned-fullwidth-path（全角）", md + "\nＣ：＼ｗｔ を見た\n", red=True, must="禁止の語")

    def prop_path(d):
        d.core_properties.category = "C:/wt/x"  # ★ 本文の外（属性）は zip の XML でしか見えない
    run("docx-path-in-properties", md, red=True, mutate_docx=prop_path, must=".docx に手元のパス")
    run("banned-username-next-to-kana", md + "\n" + os.path.basename(os.path.expanduser("~")) + "のフォルダ\n", red=True, must="禁止の語")
    run("recall-at-not-email（対照）", md.replace("## 0 この文書について", "## 0 この文書について（Recall@0.5・ASE@ICSE.2024）", 1), red=False)
    run("colon-slash-not-path（対照）", md.replace("## 0 この文書について", "## 0 この文書について（systems:/ と https://x）", 1), red=False)

    def cell_line(md_, idx, col, new):
        ls = md_.splitlines()
        k_ = next(i for i, x in enumerate(ls) if x.startswith(f"| {idx} |"))
        cells = ls[k_].strip().strip("|").split("|")
        cells[col] = f" {new} "
        ls[k_] = "|" + "|".join(cells) + "|"
        return "\n".join(ls)
    run("appendix-use-shifted（9.1 の用途）", cell_line(md, "AF001", 3, "中心-B"), red=True, must="付録 9.1")
    run("appendix-basis-shifted（9.1 の材料）", cell_line(md, "AF002", 4, "全文"), red=True, must="付録 9.1")
    run("appendix-ai-shifted（9.2 の AI の判定）", cell_line(md, "X01", 5, "Claude 版"), red=True, must="付録 9.2")
    run("appendix-use-shifted（9.2 の用途）", cell_line(md, "X01", 3, "方法論保持"), red=True, must="付録 9.2")
    run("appendix-basis-shifted（9.2 の材料）", cell_line(md, "S08-03", 4, "全文"), red=True, must="付録 9.2")

    def meta(d):
        d.core_properties.comments = "generated by python-docx"
    run("docx-template-metadata", md, red=True, mutate_docx=meta, must=".docx の属性")
    lines = md.splitlines()
    k = next(i for i, x in enumerate(lines) if x.startswith("| AF001 |"))
    lines[k] = lines[k].replace("| 含める |", "| 除外 |", 1)
    run("appendix-shifted", "\n".join(lines), red=True, must="付録 9.1")

    def mut(d):
        for p in d.paragraphs:
            if p.text.startswith("宛先"):
                p.runs[0].text = "宛先：別の人"
                break
    run("docx-paragraph-changed", md, red=True, mutate_docx=mut, must=".docx の本文")
    shutil.rmtree(tmpd, ignore_errors=True)
    print("selftest", "PASS" if ok else "FAIL")
    return ok


def main(argv):
    if "--selftest" in argv:
        sys.exit(0 if selftest() else 1)
    md = open(MD, encoding="utf-8").read()
    errs = check(md, DOCX_ARCHIVE)
    rec = open(SHA_RECORD, encoding="utf-8").read().strip() if os.path.exists(SHA_RECORD) else None
    for p in (DOCX_ARCHIVE, DOCX_DOWNLOADS):
        if not os.path.exists(p) or C.sha256(p) != rec:
            errs.append(f".docx の SHA-256 が記録と違う・無い: {p}")
    for e in errs:
        print("NG", e)
    print("違反", len(errs))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
