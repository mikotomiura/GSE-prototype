"""サーヴェイの成果物の機械検査（design.md §0.3）。

1. 事実のファイル（survey-S-??.md・issue-status.md・researcher-requests.md）に、判定の語・評価の語・GSE の内部の語が
   1 つも無いこと（★ `コード` の中も対象。判断 13）
2. 事実のファイルの引用符（「」・“”・""）の中の逐語が長すぎないこと（design §0.3: 日本語 80 字・英語 40 語まで。
   ★ `コード` の中の検索式の引用符だけは対象外）
3. 判定案のファイル（survey-S-??-ai-judgments.md・db-proposals.md）の冒頭 15 行に「自分の判定が終わるまで読まない」があること
4. evidence/ の JSON・TSV に、抄録・本文の鍵（列）が無いこと、値にメールアドレスが無いこと、500 字を超える文字列が無いこと
5. このディレクトリのすべての md にメールアドレスが無いこと

⚠️ 評価の語の検査は部分一致なので、「誤り率」「強い相関」のような著者の語にも当たる（偽陽性）。
   事実のファイルでは著者の語を言い換える（例: 誤り → エラー）運用にしている。

使い方:
  python check_survey_files.py              # 本物を検査（違反があれば終了コード 1）
  python check_survey_files.py --selftest   # 一時ディレクトリで変異を作り、どれもが赤になることを確かめる
"""
import csv
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

JUDGE = ["含める", "除外", "保留", "中心-A", "中心-B", "中心候補", "中心-A/B", "背景保持", "方法論保持", "訂正連結",
         "判定案", "TA 段", "全文段"]
JUDGE_RE = [r"(?<![A-Za-z0-9])E[1-6](?![0-9])"]
EVAL = ["良い研究", "優れ", "問題がある", "問題点", "懸念", "弱い", "強い", "十分", "べき", "質が", "質の高", "質の低",
        "信頼できる", "妥当である", "妥当な", "望ましい", "推奨", "疑わしい", "誤り", "誤記", "誤表記", "欠陥",
        "限界がある", "偏りがある", "バイアスがある", "低懸念", "高懸念", "一部懸念"]
EVAL_RE = [r"(?i)\b(in)?sufficient\b", r"(?i)\bindeterminate\b", r"(?i)\bdoubtful\b", r"(?i)\binadequate\b",
           r"(?i)\bvery good\b"]
GSE = ["GSE", "gse", "EVAL-NCC", "ADR-", "Nudge", "返権", "二重台帳", "負担台帳", "Physical Anchor", "docs/", ".steering/"]
GSE_RE = [r"\[P\d+\]", r"\[V\d+\]", r"GR-H\d+", r"(?<![A-Za-z0-9-])J-\d+", r"(?<![A-Za-z0-9])[OG]1(?![0-9A-Za-z])"]
CATEGORIES = {"judge": (JUDGE, JUDGE_RE), "eval": (EVAL, EVAL_RE), "gse": (GSE, GSE_RE)}

WARN = "自分の判定が終わるまで読まない"
BAD_KEYS = {"abstract", "abstracttext", "description", "fulltext", "abstract_inverted_index", "body", "abstracts"}
FACT_RE = re.compile(r"^(survey-S-\d\d|issue-status|researcher-requests)\.md$")
JUDG_RE = re.compile(r"^(survey-S-\d\d-ai-judgments\.md|db-proposals\.md)$")


def strip_code(text):
    return re.sub(r"`[^`\n]*`", "``", text)


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
MAX_EVIDENCE_STR = 500


def check_fact(path):
    errs = []
    text = open(path, encoding="utf-8").read()
    body = text  # ★ 禁止語は元の文で走査する（コードの中の語もすり抜けさせない・判断 13）
    for cat, (words, pats) in CATEGORIES.items():
        for w in words:
            if w in body:
                errs.append(f"{os.path.basename(path)}: 禁止語（{cat}）『{w}』")
        for p in pats:
            m = re.search(p, body)
            if m:
                errs.append(f"{os.path.basename(path)}: 禁止語（{cat}）『{m.group(0)}』")
    for m in re.finditer(r'「([^「」]*)」|“([^“”]*)”|"([^"\n]*)"', strip_code(text)):
        q = m.group(1) or m.group(2) or m.group(3) or ""
        n_en = len(re.findall(r"[A-Za-z]+", q))
        n_ja = len(re.sub(r"[\sA-Za-z0-9]", "", q))
        if n_ja > 80 or n_en > 40:
            errs.append(f"{os.path.basename(path)}: 引用が長い（日本語 {n_ja} 字・英語 {n_en} 語）: {q[:30]}…")
    return errs


def check_judgment(path):
    head = "".join(open(path, encoding="utf-8").readlines()[:15])
    return [] if WARN in head else [f"{os.path.basename(path)}: 冒頭 15 行に『{WARN}』が無い"]


def walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_keys(v)


def walk_values(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk_values(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_values(v)
    elif isinstance(obj, str):
        yield obj


def check_evidence(root):
    errs = []
    ev = os.path.join(root, "evidence")
    for dp, _, fns in os.walk(ev):
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root)
            if fn.endswith(".json"):
                # ★ utf-8-sig で読む（BOM 付きでも鍵を見る・Codex 2 巡目）。読めない JSON は赤にする
                try:
                    with open(p, encoding="utf-8-sig") as fh:
                        obj = json.load(fh)
                except (ValueError, UnicodeDecodeError) as e:
                    errs.append(f"{rel}: JSON として読めない（{type(e).__name__}）")
                    continue
                keys = {str(k).lower() for k in walk_keys(obj)}
                bad = keys & BAD_KEYS
                values = list(walk_values(obj))
            elif fn.endswith((".tsv", ".csv")):
                # ★ 標準の csv で読む（引用符で囲んだ見出し "abstract" も見出しとして解釈する・判断 16）
                delim = "\t" if fn.endswith(".tsv") else ","
                # ★ utf-8-sig: BOM が先頭の見出しに付いて "abstract" と一致しなくなるのを防ぐ（Codex 2 巡目）
                with open(p, encoding="utf-8-sig", newline="") as fh:
                    table = list(csv.reader(fh, delimiter=delim))
                head = [c.strip().lower() for c in (table[0] if table else [])]
                bad = set(head) & BAD_KEYS
                values = [c for row in table for c in row]
            else:
                continue
            if bad:
                errs.append(f"{rel}: 抄録・本文の鍵 {sorted(bad)}")
            hit = next((v for v in values if EMAIL.search(v)), None)
            if hit is not None:
                errs.append(f"{rel}: メールアドレスがある")
            long_v = next((v for v in values if len(v) > MAX_EVIDENCE_STR), None)
            if long_v is not None:
                errs.append(f"{rel}: {MAX_EVIDENCE_STR} 字を超える文字列（{len(long_v)} 字）")
    return errs


def check_emails_md(root):
    errs = []
    for fn in sorted(os.listdir(root)):
        if fn.endswith(".md") and EMAIL.search(open(os.path.join(root, fn), encoding="utf-8").read()):
            errs.append(f"{fn}: メールアドレスがある")
    return errs


def run(root):
    errs, n_fact, n_judg = [], 0, 0
    for fn in sorted(os.listdir(root)):
        p = os.path.join(root, fn)
        if FACT_RE.match(fn):
            n_fact += 1
            errs += check_fact(p)
        elif JUDG_RE.match(fn):
            n_judg += 1
            errs += check_judgment(p)
    errs += check_evidence(root)
    errs += check_emails_md(root)
    return errs, n_fact, n_judg


def selftest():
    ok = True
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "t")
        shutil.copytree(ROOT, base, ignore=shutil.ignore_patterns("*.xlsx", "__pycache__"))
        errs, n_fact, n_judg = run(base)
        if errs or n_fact == 0:
            print("SELFTEST NG: 変異の無い写しが緑にならない、または事実のファイルが 0 本", errs[:3], n_fact)
            return False
        facts = [fn for fn in os.listdir(base) if FACT_RE.match(fn)]
        cases = {"judge": ["含める", "E4", "中心-A", "`E2`", "`中心-B`"],
                 "eval": ["懸念", "不十分", "very good", "insufficient", "inadequate", "`良い研究`"],
                 "gse": ["GSE", "[P362]", "GR-H12", "J-17", "O1", "`GSE`", "[V12]"]}
        for cat, words in cases.items():
            for w in words:
                for fn in facts:
                    p = os.path.join(base, fn)
                    orig = open(p, encoding="utf-8").read()
                    open(p, "w", encoding="utf-8").write(orig + f"\n変異 {w} を足した行\n")
                    e, _, _ = run(base)
                    open(p, "w", encoding="utf-8").write(orig)
                    hit = any(f"（{cat}）" in x and os.path.basename(p) in x for x in e)
                    print(("OK " if hit else "NG ") + f"{cat}: {w} → {fn}")
                    ok &= hit
        # 長い引用（英語の“”・ASCII の""・日本語の「」）
        p = os.path.join(base, facts[0])
        orig = open(p, encoding="utf-8").read()
        for label, add in [("long quote (curly)", "“" + " ".join(["word"] * 45) + "”"),
                           ("long quote (ascii)", '"' + " ".join(["word"] * 45) + '"'),
                           ("long quote (ja)", "「" + "あ" * 85 + "」")]:
            open(p, "w", encoding="utf-8").write(orig + "\n" + add + "\n")
            hit = any("引用が長い" in x for x in run(base)[0])
            open(p, "w", encoding="utf-8").write(orig)
            print(("OK " if hit else "NG ") + label)
            ok &= hit
        # コードの中の検索式の引用符は長さの検査の対象外（誤って赤にしない）
        open(p, "w", encoding="utf-8").write(orig + "\n`" + '"' + " ".join(["term"] * 45) + '"' + "`\n")
        hit = not any("引用が長い" in x for x in run(base)[0])
        open(p, "w", encoding="utf-8").write(orig)
        print(("OK " if hit else "NG ") + "quote inside code is not a long quote")
        ok &= hit
        # md のメールアドレス
        open(p, "w", encoding="utf-8").write(orig + "\n連絡先 someone@example.org\n")
        hit = any("メールアドレス" in x for x in run(base)[0])
        open(p, "w", encoding="utf-8").write(orig)
        print(("OK " if hit else "NG ") + "email in md")
        ok &= hit
        # 判定案の注意書きを消す
        judg = [fn for fn in os.listdir(base) if JUDG_RE.match(fn)]
        for fn in judg:
            p = os.path.join(base, fn)
            orig = open(p, encoding="utf-8").read()
            open(p, "w", encoding="utf-8").write(orig.replace(WARN, "（消した）"))
            hit = any("冒頭 15 行" in x for x in run(base)[0])
            open(p, "w", encoding="utf-8").write(orig)
            print(("OK " if hit else "NG ") + f"warning removed → {fn}")
            ok &= hit
        # evidence の変異: 抄録の鍵・メールアドレス・長い文字列（JSON）、抄録の列（TSV）
        muts = [("evidence abstract key", "zz_mutant.json", {"runs": [{"records": [{"title": "x", "abstract": "y"}]}]}),
                ("evidence email value", "zz_mutant.json", {"runs": [{"records": [{"affiliation": "Univ. a.b@example.com"}]}]}),
                ("evidence long string", "zz_mutant.json", {"runs": [{"records": [{"title": "x" * 600}]}]}),
                ("evidence tsv abstract column", "zz_mutant.tsv", "id\tabstract\n1\tx\n"),
                ("evidence tsv quoted abstract column", "zz_mutant.tsv", '"id"\t"Abstract"\n1\tx\n'),
                ("evidence csv abstract column", "zz_mutant.csv", 'id,"abstract"\n1,x\n'),
                ("evidence tsv BOM abstract column", "zz_mutant.tsv", "\ufeffabstract\tid\nx\t1\n"),
                ("evidence csv BOM abstract column", "zz_mutant.csv", "\ufeffabstract,id\nx,1\n"),
                ("evidence json BOM abstract key", "zz_mutant.json", "\ufeff" + json.dumps({"abstract": "y"})),
                ("evidence json unreadable", "zz_mutant.json", "{\"abstract\": ")]
        for label, name, content in muts:
            p = os.path.join(base, "evidence", name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            if isinstance(content, str):
                open(p, "w", encoding="utf-8").write(content)
            else:
                json.dump(content, open(p, "w", encoding="utf-8"))
            hit = any("zz_mutant" in x for x in run(base)[0])
            os.remove(p)
            print(("OK " if hit else "NG ") + label)
            ok &= hit
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    errs, n_fact, n_judg = run(ROOT)
    for e in errs:
        print("NG", e)
    print(f"事実のファイル {n_fact} 本・判定案のファイル {n_judg} 本・違反 {len(errs)} 件")
    sys.exit(1 if errs or n_fact == 0 else 0)
