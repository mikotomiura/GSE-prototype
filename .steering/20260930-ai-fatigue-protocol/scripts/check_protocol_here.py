"""プロトコルの草稿（protocol-ja.md）と issue の状態（issue-status.md）の機械検査（design.md §5）。

protocol-ja.md は判定の規則そのもの（含める・除外・E1〜E7・中心-A/B）を書く文書なので、前タスクの検査器
（`../../20260929-ai-fatigue-surveys/scripts/check_survey_files.py`）の禁止語を文書の全体には当てられない。
★ そこで「1 件ずつの判定案・見立て」を次の形で止める（decisions.md 判断 12）:

1. 記録の鍵（AF001・S04-44 など）を含む行に、判定の語・評価の語（前タスクの JUDGE・EVAL と正規表現。E7 を足す）と、
   用法の区分（U1〜U5）・内容の群の区切り（｜）・見立ての語が無いこと
2. 研究チームの別の研究の内部の語（前タスクの GSE と正規表現）が文書のどこにも無いこと
3. メールアドレスが無いこと・引用符の中の逐語が長すぎないこと（前タスクと同じ閾値）
4. GSRR の 65 項目（van den Akker ほか 2023・PMC10514995 の様式）が、見出しにちょうど 1 回ずつ順に出ること。
   付録 E の対応表の各行が、項目の英語の名（一次の様式のまま）と、その見出しがある節の番号に一致すること

issue-status.md には、前タスクの事実のファイルと同じ検査（check_fact）をそのまま当てる。
evidence/ には前タスクの check_evidence（抄録の鍵・メールアドレス・500 字を超える文字列）、md には check_emails_md を当てる。

使い方:
  python check_protocol_here.py              # 本物を検査（違反があれば終了コード 1）
  python check_protocol_here.py --selftest   # 一時ディレクトリで変異を作り、どれもが意図した理由で赤になることを確かめる
"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
PREV_SCRIPTS = os.path.join(os.path.dirname(TASK), "20260929-ai-fatigue-surveys", "scripts")
sys.path.insert(0, PREV_SCRIPTS)
import check_survey_files as C  # noqa: E402

PROTOCOL = "protocol-ja.md"
ISSUE_STATUS = "issue-status.md"
DEDUP = "dedup-259.md"  # ★ 判断 17: 判定者 2 も読むので、鍵の行・内部の語・メールの規則を当てる

KEY_RE = re.compile(r"(?<![A-Za-z0-9])(?:AF\d{3}|S\d{2}-\d{2}|TH\d{2})(?![0-9])")
# ★ 判断 17（2026-10-01 のレビュー）: 内容の群の値（design.md §7.7 の値）も鍵の行で止める（区切りの｜だけでは値の書き方が通った）
CONTENT_VALUES = ["レビュー等", "一次研究", "医療者", "教員・研究者", "学生・学習者", "働く人（医療・教育の外）",
                  "消費者・一般の利用者", "記録支援・下書き", "意思決定支援・警報・予測", "生成 AI・対話", "生成AI・対話",
                  "AI 一般・導入", "AI一般・導入", "比較（非無作為化・前後）", "尺度開発", "実験・模擬", "横断調査", "不明"]
KEY_WORDS = list(C.JUDGE) + list(C.EVAL) + ["見立て", "｜"] + CONTENT_VALUES
KEY_PATS = [r"(?<![A-Za-z0-9])E[1-7](?![0-9])", r"(?<![A-Za-z0-9])U[1-5](?![0-9])"] + list(C.EVAL_RE)

# GSRR の 65 項目の英語の名（PMC10514995 の本文の様式から。2026-10-01 に XML から抜き出した）
GSRR = [
    "Title", "Contributors", "Subjects", "Tasks and roles", "Type of review", "Review stages",
    "Current review stage", "Start date", "End date", "Background", "Primary research question(s)",
    "Secondary research question(s)", "Expectations / hypotheses",
    "Dependent variable(s) / outcome(s) / main variables",
    "Independent variable(s) / intervention(s) / treatment(s)", "Additional variable(s) / covariate(s)",
    "Software", "Funding", "Conflicts of interest", "Overlapping authorships", "Databases", "Interfaces",
    "Grey literature", "Inclusion and exclusion criteria", "Query strings", "Search validation procedure",
    "Other search strategies", "Procedures to contact authors", "Results of contacting authors",
    "Search expiration and repetition", "Search strategy justification", "Miscellaneous search strategy details",
    "Screening stages", "Screened fields / blinding", "Used exclusion criteria", "Screener instructions",
    "Screening reliability", "Screening reconciliation procedure", "Sampling and sample size",
    "Screening procedure justification", "Data management and sharing", "Miscellaneous screening details",
    "Entities to extract", "Extraction stages", "Extractor instructions", "Extractor blinding",
    "Extraction reliability", "Extraction reconciliation procedure", "Extraction procedure justification",
    "Data management and sharing", "Miscellaneous extraction details", "Planned data transformations",
    "Missing data", "Data validation", "Quality assessment", "Synthesis plan",
    "Criteria for conclusions / inference criteria", "Synthesist blinding", "Synthesis reliability",
    "Synthesis reconciliation procedure", "Publication bias analyses", "Sensitivity analyses / robustness checks",
    "Synthesis procedure justification", "Synthesis data management and sharing", "Miscellaneous synthesis details",
]
assert len(GSRR) == 65

TAG_RE = re.compile(r"\[GSRR-(\d+)\]")
SECTION_RE = re.compile(r"^## (\d+)\. ")
APPX_E = "## 付録 E"
ROW_E = re.compile(r"^\| (\d+) \| (.+?) \| §(\d+) \|$")


def check_key_lines(lines, name, pats=None):
    errs = []
    for i, line in enumerate(lines, 1):
        if not KEY_RE.search(line):
            continue
        for w in KEY_WORDS:
            if w in line:
                errs.append(f"{name}:{i}: 記録の鍵と同じ行に『{w}』（1 件ずつの判定・見立て）")
        for p in (KEY_PATS if pats is None else pats):
            m = re.search(p, line)
            if m:
                errs.append(f"{name}:{i}: 記録の鍵と同じ行に『{m.group(0)}』（1 件ずつの判定・見立て）")
    return errs


def check_gse(text, name):
    errs = []
    for w in C.GSE:
        if w in text:
            errs.append(f"{name}: 別の研究の内部の語『{w}』")
    for p in C.GSE_RE:
        m = re.search(p, text)
        if m:
            errs.append(f"{name}: 別の研究の内部の語『{m.group(0)}』")
    return errs


def check_quotes_and_email(text, name):
    errs = []
    for m in re.finditer(r'「([^「」]*)」|“([^“”]*)”|"([^"\n]*)"', C.strip_code(text)):
        q = m.group(1) or m.group(2) or m.group(3) or ""
        n_en = len(re.findall(r"[A-Za-z]+", q))
        n_ja = len(re.sub(r"[\sA-Za-z0-9]", "", q))
        if n_ja > 80 or n_en > 40:
            errs.append(f"{name}: 引用が長い（日本語 {n_ja} 字・英語 {n_en} 語）: {q[:30]}…")
    if C.EMAIL.search(text):
        errs.append(f"{name}: メールアドレスがある")
    return errs


def check_gsrr(lines, name):
    errs = []
    heads = {}  # 番号 → (行, 節)
    order = []
    section = None
    in_appx = False
    rows = {}
    for i, line in enumerate(lines, 1):
        m = SECTION_RE.match(line)
        if m:
            section = int(m.group(1))
        if line.startswith("## 付録"):
            section = None
            in_appx = line.startswith(APPX_E)
        if line.startswith("#"):
            for t in TAG_RE.finditer(line):
                n = int(t.group(1))
                if not 1 <= n <= 65:
                    errs.append(f"{name}:{i}: 範囲の外の項目の番号 [GSRR-{n}]")
                    continue
                if n in heads:
                    errs.append(f"{name}:{i}: [GSRR-{n}] の見出しが 2 回ある（{heads[n][0]} 行と）")
                    continue
                if section is None:
                    errs.append(f"{name}:{i}: [GSRR-{n}] の見出しが本文の節の外にある")
                heads[n] = (i, section)
                order.append(n)
        if in_appx:
            r = ROW_E.match(line)
            if r:
                rows[int(r.group(1))] = (i, r.group(2), int(r.group(3)))
    for n in range(1, 66):
        if n not in heads:
            errs.append(f"{name}: [GSRR-{n}]（{GSRR[n - 1]}）の見出しが無い")
    if order != sorted(order):
        errs.append(f"{name}: GSRR の見出しの順が様式の順と違う")
    for n in range(1, 66):
        if n not in rows:
            errs.append(f"{name}: 付録 E に項目 {n} の行が無い")
            continue
        i, en, sec = rows[n]
        if en != GSRR[n - 1]:
            errs.append(f"{name}:{i}: 付録 E の項目 {n} の名『{en}』が様式の名『{GSRR[n - 1]}』と違う")
        if n in heads and heads[n][1] != sec:
            errs.append(f"{name}:{i}: 付録 E の項目 {n} の節 §{sec} が見出しの節 §{heads[n][1]} と違う")
    extra = sorted(set(rows) - set(range(1, 66)))
    if extra:
        errs.append(f"{name}: 付録 E に範囲の外の行 {extra}")
    return errs


def run(root):
    errs = []
    p = os.path.join(root, PROTOCOL)
    if not os.path.exists(p):
        return [f"{PROTOCOL} が無い"]
    text = open(p, encoding="utf-8").read()
    lines = text.splitlines()
    errs += check_key_lines(lines, PROTOCOL)
    errs += check_gse(text, PROTOCOL)
    errs += check_quotes_and_email(text, PROTOCOL)
    errs += check_gsrr(lines, PROTOCOL)
    d = os.path.join(root, DEDUP)
    if os.path.exists(d):
        dt = open(d, encoding="utf-8").read()
        # dedup-259.md の U1・U2 は「同じ研究の群」の要確認の群の名（用法の区分ではない）ので、U の規則だけ外す
        errs += check_key_lines(dt.splitlines(), DEDUP, pats=[p for p in KEY_PATS if "U[1-5]" not in p])
        errs += check_gse(dt, DEDUP)
        errs += check_quotes_and_email(dt, DEDUP)
    else:
        errs.append(f"{DEDUP} が無い")
    s = os.path.join(root, ISSUE_STATUS)
    if os.path.exists(s):
        errs += C.check_fact(s)
    else:
        errs.append(f"{ISSUE_STATUS} が無い")
    # 前タスクと同じ: evidence の JSON・TSV に抄録の鍵・メールアドレス・500 字を超える文字列が無い／md にメールアドレスが無い
    errs += C.check_evidence(root)
    errs += C.check_emails_md(root)
    return errs


def selftest():
    ok = True
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "t")
        os.makedirs(base)
        for fn in (PROTOCOL, ISSUE_STATUS, DEDUP):
            shutil.copy(os.path.join(TASK, fn), base)
        errs = run(base)
        print(("OK " if not errs else "NG ") + "陰性対照（変異なしで緑）", errs[:3])
        ok &= not errs
        p = os.path.join(base, PROTOCOL)
        orig = open(p, encoding="utf-8").read()

        def mutate(label, new, expect, fn=PROTOCOL):
            nonlocal ok
            path = os.path.join(base, fn)
            before = open(path, encoding="utf-8").read()
            open(path, "w", encoding="utf-8", newline="\n").write(new(before))
            e = run(base)
            open(path, "w", encoding="utf-8", newline="\n").write(before)
            hit = any(expect in x for x in e)
            print(("OK " if hit else "NG ") + label, "" if hit else e[:3])
            ok &= hit

        # 1. 記録の鍵と同じ行の判定・評価・見立て
        for w, why in [("AF001 は含める", "『含める』"), ("S04-44 は E7", "『E7』"), ("S12-11 は E2", "『E2』"),
                       ("AF019 の懸念", "『懸念』"), ("S14-04 は中心-B", "『中心-B』"), ("AF024 は U1", "『U1』"),
                       ("S02-07 は医療者｜記録支援・下書き｜横断調査", "『｜』"), ("AF011 の見立て", "『見立て』"),
                       ("`AF001` は `除外`", "『除外』"), ("S08-02 is very good", "very good")]:
            mutate(f"鍵の行: {w}", lambda t, w=w: t + f"\n- {w}\n", why)
        # 2. 別の研究の内部の語
        for w, why in [("GSE", "『GSE』"), ("docs/", "『docs/』"), (".steering/", "『.steering/』"), ("[P362]", "『[P362]』"),
                       ("ADR-015", "『ADR-』"), ("Nudge", "『Nudge』")]:
            mutate(f"内部の語: {w}", lambda t, w=w: t + f"\n- {w}\n", why)
        # 3. メール・長い引用
        mutate("メールアドレス", lambda t: t + "\n連絡 someone@example.org\n", "メールアドレス")
        mutate("長い引用", lambda t: t + "\n「" + "あ" * 85 + "」\n", "引用が長い")
        # 4. GSRR の見出しと対応表
        mutate("見出しの欠け", lambda t: t.replace("### [GSRR-37] ", "### ", 1), "[GSRR-37]（Screening reliability）の見出しが無い")
        mutate("見出しの重複", lambda t: t.replace("### [GSRR-38] ", "### [GSRR-37] ", 1), "の見出しが 2 回ある")
        mutate("範囲の外の番号", lambda t: t.replace("### [GSRR-65] ", "### [GSRR-65] [GSRR-66] ", 1), "範囲の外の項目の番号")
        mutate("見出しの順", lambda t: t.replace("### [GSRR-11] ", "### [GSRR-99x] ", 1).replace(
            "### [GSRR-12] ", "### [GSRR-11] ", 1).replace("### [GSRR-99x] ", "### [GSRR-12] ", 1), "順が様式の順と違う")
        mutate("付録 E の名", lambda t: t.replace("| 37 | Screening reliability | §5 |", "| 37 | Screening reliabilty | §5 |"),
               "付録 E の項目 37 の名")
        mutate("付録 E の節", lambda t: t.replace("| 37 | Screening reliability | §5 |", "| 37 | Screening reliability | §6 |"),
               "付録 E の項目 37 の節")
        mutate("付録 E の行の欠け", lambda t: t.replace("| 64 | Synthesis data management and sharing | §7 |\n", ""),
               "付録 E に項目 64 の行が無い")
        mutate("見出しを付録へ動かす", lambda t: t.replace("### [GSRR-65] ", "### ", 1) + "\n### [GSRR-65] x\n",
               "本文の節の外にある")
        # 4b. dedup-259.md（判定者 2 も読む）の鍵の行と内部の語
        mutate("dedup の鍵の行の内容の群の値", lambda t: t + "\n- S12-11 は生成 AI・対話から不明にした\n", "『生成 AI・対話』", fn=DEDUP)
        mutate("dedup の鍵の行の判定の語", lambda t: t + "\n- S04-44 は除外\n", "『除外』", fn=DEDUP)
        mutate("dedup の内部の語", lambda t: t + "\n- GSE\n", "別の研究の内部の語『GSE』", fn=DEDUP)
        dp = os.path.join(base, DEDUP)
        keep = open(dp, encoding="utf-8").read()
        os.remove(dp)
        e = run(base)
        open(dp, "w", encoding="utf-8", newline="\n").write(keep)
        hit = any(f"{DEDUP} が無い" in x for x in e)
        print(("OK " if hit else "NG ") + "dedup が無い", "" if hit else e[:3])
        ok &= hit
        # 5. issue-status.md は前タスクの事実のファイルと同じ検査
        mutate("issue-status の判定の語", lambda t: t + "\n- 含める\n", "禁止語（judge）", fn=ISSUE_STATUS)
        mutate("issue-status の内部の語", lambda t: t + "\n- GSE\n", "禁止語（gse）", fn=ISSUE_STATUS)
    # 鍵の無い行の規則の語は止めない（規則の文書として書けること）の確かめ
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "t")
        os.makedirs(base)
        for fn in (PROTOCOL, ISSUE_STATUS, DEDUP):
            shutil.copy(os.path.join(TASK, fn), base)
        p = os.path.join(base, PROTOCOL)
        # ★ 判断 17: 規則の語（含める・除外・中心-A・E4・U1・懸念・内容の群の値）が鍵の無い行なら緑
        open(p, "a", encoding="utf-8", newline="\n").write(
            "\n- 含める・除外・中心-A・E4・U1 の規則。懸念は文章で書く。医療者｜記録支援・下書き｜横断調査 の群。\n")
        e = run(base)
        print(("OK " if not e else "NG ") + "鍵の無い行の規則の語は赤にしない", e[:3])
        ok &= not e
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    errs = run(TASK)
    for e in errs:
        print("NG", e)
    print(f"違反 {len(errs)} 件")
    sys.exit(1 if errs else 0)
