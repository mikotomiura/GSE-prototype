"""研究者の確認票（researcher-check.md）と issue の状態（issue-status.md）の機械検査（design.md §3）。

確認票は判定者 2 に渡ることもありうるので、プロトコルの草稿と同じ規則で「1 件ずつの判定・見立て」を止める
（前タスクの `../../20260930-ai-fatigue-protocol/scripts/check_protocol_here.py` の関数をそのまま使う）:
1. 記録の鍵（AF001・S04-44 など）を含む行に、判定の語・評価の語・用法の区分・内容の群の値・見立ての語が無い
2. 研究チームの別の研究の内部の語が無い
3. メールアドレスが無い・引用符の中の逐語が長すぎない
加えて、確認票が草稿と食い違わないことを確かめる:
4. 付録 F の F1〜F20 の番号が、確認票の表の行（`| F<n> |`）にすべて出る
5. 確認票の【案】の表（§6）の節ごとの行の数が、草稿の本文の【案】の数と節ごとに一致する
   （草稿の印の説明の行〈引用の行〉と付録 F の中は数えない）
issue-status.md には、前タスクの事実のファイルと同じ検査（check_fact）を当てる。

使い方:
  python check_here.py              # 本物を検査（違反があれば終了コード 1）
  python check_here.py --selftest   # 一時ディレクトリで変異を作り、どれもが意図した理由で赤になることを確かめる
"""
import collections
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
PROTO_TASK = os.path.join(STEER, "20260930-ai-fatigue-protocol")
sys.path.insert(0, os.path.join(PROTO_TASK, "scripts"))
import check_protocol_here as P  # noqa: E402

C = P.C  # 前タスクの check_survey_files（SSOT）
CHECK = "researcher-check.md"
ISSUE_STATUS = "issue-status.md"
PROTOCOL = os.path.join(PROTO_TASK, "protocol-ja.md")
PROPOSAL = "【案"
APPX_6 = "## 6. "
ROW_F = re.compile(r"^\| (F\d+) \|")


def section_key(heading):
    """見出しの文から節の鍵を作る（[GSRR-n]・§5.1・付録 C・付録 D.6）。"""
    m = re.search(r"\[GSRR-\d+\]", heading)
    if m:
        return m.group(0)
    m = re.match(r"(付録 [A-Z])", heading)
    if m:
        return m.group(1)
    m = re.match(r"([A-Z]\.\d+) ", heading)
    if m:
        return f"付録 {m.group(1)}"
    m = re.match(r"(\d+\.\d+) ", heading)
    if m:
        return f"§{m.group(1)}"
    return heading.strip()


def proposal_counts(protocol_text):
    """草稿の本文の【案】の数を節ごとに数える（引用の行と付録 F の中は数えない）。"""
    counts = collections.Counter()
    key = None
    in_f = False
    for line in protocol_text.splitlines():
        m = re.match(r"^#{2,3} (.*)", line)
        if m:
            key = section_key(m.group(1))
            if line.startswith("## "):
                in_f = m.group(1).startswith("付録 F")
        if line.startswith(">") or in_f or key is None:
            continue
        counts[key] += line.count(PROPOSAL)
    return +counts


def sheet_counts(lines):
    """確認票の §6 の表の、節ごとの行の数。"""
    counts = collections.Counter()
    in6 = False
    for line in lines:
        if line.startswith("## "):
            in6 = line.startswith(APPX_6)
            continue
        if in6 and line.startswith("| ") and not line.startswith("| 節 ") and not line.startswith("|---"):
            counts[line.split("|")[1].strip()] += 1
    return counts


def check_sheet(root, protocol_path):
    errs = []
    p = os.path.join(root, CHECK)
    if not os.path.exists(p):
        return [f"{CHECK} が無い"]
    text = open(p, encoding="utf-8").read()
    lines = text.splitlines()
    errs += P.check_key_lines(lines, CHECK)
    errs += P.check_gse(text, CHECK)
    errs += P.check_quotes_and_email(text, CHECK)
    seen = {m.group(1) for m in map(ROW_F.match, lines) if m}
    for n in range(1, 21):
        if f"F{n}" not in seen:
            errs.append(f"{CHECK}: 付録 F の F{n} の行が無い")
    want = proposal_counts(open(protocol_path, encoding="utf-8").read())
    got = sheet_counts(lines)
    if sum(want.values()) == 0:
        errs.append("草稿に【案】が 1 つも無い（数え方が壊れている）")
    for k in sorted(set(want) | set(got)):
        if want.get(k, 0) != got.get(k, 0):
            errs.append(f"{CHECK}: 【案】の数が節 {k} で草稿と違う（草稿 {want.get(k, 0)}・票 {got.get(k, 0)}）")
    return errs


def run(root, protocol_path=PROTOCOL):
    errs = check_sheet(root, protocol_path)
    s = os.path.join(root, ISSUE_STATUS)
    if os.path.exists(s):
        errs += C.check_fact(s)
        # ★ 前タスクの SSOT の判定の語の正規表現は E[1-6] なので、E7 はここで足す（判定者用ファイルの検査器と同じ扱い）
        m = re.search(r"(?<![A-Za-z0-9])E7(?![0-9])", open(s, encoding="utf-8").read())
        if m:
            errs.append(f"{ISSUE_STATUS}: 禁止語（judge）『E7』")
    else:
        errs.append(f"{ISSUE_STATUS} が無い")
    return errs


def selftest():
    ok = True
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "t")
        os.makedirs(base)
        for fn in (CHECK, ISSUE_STATUS):
            shutil.copy(os.path.join(TASK, fn), base)
        proto = os.path.join(td, "protocol-ja.md")
        shutil.copy(PROTOCOL, proto)
        errs = run(base, proto)
        print(("OK " if not errs else "NG ") + "陰性対照（変異なしで緑）", errs[:3])
        ok &= not errs

        def mutate(label, new, expect, fn=CHECK):
            nonlocal ok
            path = proto if fn is None else os.path.join(base, fn)
            before = open(path, encoding="utf-8").read()
            after = new(before)
            if after == before:  # 変異の対象が無い＝検査を確かめられていない
                print("NG " + label + "（変異の対象が無い）")
                ok = False
                return
            open(path, "w", encoding="utf-8", newline="\n").write(after)
            e = run(base, proto)
            open(path, "w", encoding="utf-8", newline="\n").write(before)
            hit = any(expect in x for x in e)
            print(("OK " if hit else "NG ") + label, "" if hit else e[:3])
            ok &= hit

        # 1〜3. 鍵の行・内部の語・メール
        mutate("鍵の行の判定の語", lambda t: t + "\n- AF001 は含める\n", "『含める』")
        mutate("鍵の行の E7", lambda t: t + "\n- S14-44 は E7\n", "『E7』")
        mutate("鍵の行の内容の群の値", lambda t: t + "\n- S04-15 は医療者\n", "『医療者』")
        mutate("内部の語", lambda t: t + "\n- GSE\n", "『GSE』")
        mutate("メールアドレス", lambda t: t + "\n連絡 someone@example.org\n", "メールアドレス")
        # 4. F の番号の欠け
        mutate("F18 の行が無い", lambda t: re.sub(r"(?m)^\| F18 \|.*\n", "", t), "F18 の行が無い")
        mutate("F19 の行が無い（決定の節）", lambda t: re.sub(r"(?m)^\| F19 \|.*\n", "", t), "F19 の行が無い")
        # 5. 【案】の数
        mutate("票の【案】の行を 1 つ落とす", lambda t: re.sub(r"(?m)^\| \[GSRR-60\] \|.*\n", "", t), "節 [GSRR-60] で草稿と違う")
        mutate("票に【案】の行を足す", lambda t: t + "| [GSRR-9] | 終わる日を 2027 年 3 月にする | |\n", "節 [GSRR-9] で草稿と違う")
        mutate("草稿に【案】を足す", lambda t: t.replace("### [GSRR-58] まとめる人の盲検\n",
                                                      "### [GSRR-58] まとめる人の盲検\n\n- 【案】足した案。\n", 1),
               "節 [GSRR-58] で草稿と違う", fn=None)
        mutate("草稿の付録 C の【案】を消す", lambda t: t.replace("## 付録 C 抽出フォーム【案】", "## 付録 C 抽出フォーム", 1),
               "節 付録 C で草稿と違う", fn=None)
        # 6. issue-status.md は前タスクの事実のファイルと同じ検査
        mutate("issue-status の判定の語", lambda t: t + "\n- 含める\n", "禁止語（judge）", fn=ISSUE_STATUS)
        mutate("issue-status の E7", lambda t: t + "\n- E7\n", "禁止語", fn=ISSUE_STATUS)
    # 数え方の確かめ: 印の説明の行（引用）と付録 F の中の【案】は数えない
    demo = ("> 印: 【案】は案。\n## 1. x\n### [GSRR-6] y\n- a【案】\n- b【案・確認待ち】\n### 5.1 z\n- c【案】\n"
            "## 付録 C 抽出フォーム【案】\n### D.6 w\n- d【案】\n## 付録 F 一覧\n| F15 | 【案】の採否 |\n")
    want = {"[GSRR-6]": 2, "§5.1": 1, "付録 C": 1, "付録 D.6": 1}
    got = dict(proposal_counts(demo))
    print(("OK " if got == want else "NG ") + "【案】の数え方（引用・付録 F を数えない）", got)
    ok &= got == want
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
