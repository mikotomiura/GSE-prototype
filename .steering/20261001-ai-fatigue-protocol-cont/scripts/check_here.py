"""研究者の確認票（researcher-check.md）と issue の状態（issue-status.md）の機械検査（design.md §3）。

確認票は判定者 2 に渡ることもありうるので、プロトコルの草稿と同じ規則で「1 件ずつの判定・見立て」を止める
（前タスクの `../../20260930-ai-fatigue-protocol/scripts/check_protocol_here.py` の関数をそのまま使う）:
1. 記録の鍵（AF001・S04-44 など）を含む行に、判定の語・評価の語・用法の区分・内容の群の値・見立ての語が無い
2. 研究チームの別の研究の内部の語が無い
3. メールアドレスが無い・引用符の中の逐語が長すぎない
加えて、確認票が草稿と食い違わないことを確かめる:
4. 草稿の付録 F の番号（`| F<n> |` の行）が、確認票の表の行にすべて出る。付録 F で「決定」の印の番号は確認票の §1
   （判定者 1 が決めたこと）に、ほかは §2〜§4 に出る（★ 2026-10-01 のレビュー: 番号を固定で持たない）
5. 確認票の【案】の表（§6）の節ごとの行の数が、草稿の本文の【案】の数と節ごとに一致する
   （最初の見出しより前〈版と印の説明〉と付録 F の中は数えない。★ 節の中の引用の行は数える）
6. 判定者用ファイルの道具（judge_xlsx.py）の『判定基準』と選択肢が、草稿の付録 B と一致する: 「基準の版」と
   「E4 の『尺度の原著』」の行の文・除外理由の選択肢（付録 B の「除外理由＝E1〜En」）。★ 道具は import せず（openpyxl が要る）
   ast で定数を読む（2026-10-01 のレビュー: golden は build() との比較なので、決定が道具に入っていることを確かめない）
issue-status.md には、前タスクの事実のファイルと同じ検査（check_fact）を当てる。

使い方:
  python check_here.py              # 本物を検査（違反があれば終了コード 1）
  python check_here.py --selftest   # 一時ディレクトリで変異を作り、どれもが意図した理由で赤になることを確かめる
"""
import ast
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
JUDGE_PY = os.path.join(STEER, "20260930-ai-fatigue-judge-file", "scripts", "judge_xlsx.py")
DECIDED_SECTION = "## 1. "
PENDING_SECTIONS = ("## 2. ", "## 3. ", "## 4. ")
B_ROWS = ["基準の版", "E4 の『尺度の原著』（2026-10-01）"]
PROPOSAL = "【案"
APPX_6 = "## 6. "
ROW_F = re.compile(r"^\| (F\d+) \|")


def section_key(heading):
    """見出しの文から節の鍵を作る（[GSRR-n]・§5.1・付録 C・付録 D.6）。"""
    m = re.match(r"\[GSRR-\d+\]", heading)  # ★ 見出しの先頭だけ（見出しの中の参照で別の節に数えない）
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
    """草稿の本文の【案】の数を節ごとに数える（最初の見出しより前と付録 F の中は数えない）。"""
    counts = collections.Counter()
    key = None
    in_f = False
    for line in protocol_text.splitlines():
        m = re.match(r"^#{2,3} (.*)", line)
        if m:
            key = section_key(m.group(1))
            if line.startswith("## "):
                in_f = m.group(1).startswith("付録 F")
        if in_f or key is None:
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


def appendix_rows(protocol_text, title):
    """草稿の付録の表の行を {1 列目: 2 列目} で返す（見出し `title` から次の `## ` まで）。"""
    rows = {}
    inside = False
    for line in protocol_text.splitlines():
        if line.startswith("## "):
            inside = line.startswith(title)
            continue
        m = re.match(r"^\| (.+?) \| (.*?) \|", line)
        if inside and m and not line.startswith("|---"):
            rows[m.group(1)] = m.group(2)
    rows.pop("#", None)
    rows.pop("項目", None)
    return rows


def sheet_f_rows(lines):
    """確認票の節（`## n. ` の頭）ごとの F の番号の集合。"""
    out = collections.defaultdict(set)
    cur = None
    for line in lines:
        if line.startswith("## "):
            cur = line[:6]
            continue
        m = ROW_F.match(line)
        if m and cur:
            out[cur].add(m.group(1))
    return out


def judge_constants(judge_path):
    """judge_xlsx.py の CHOICES と CRITERIA を、import せずに ast で読む。"""
    tree = ast.parse(open(judge_path, encoding="utf-8").read())
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("CHOICES", "CRITERIA"):
                found[node.targets[0].id] = ast.literal_eval(node.value)
    return found.get("CHOICES"), found.get("CRITERIA")


def check_judge_tool(protocol_text, judge_path):
    """道具の『判定基準』と選択肢が、草稿の付録 B と一致するか。"""
    errs = []
    choices, criteria = judge_constants(judge_path)
    if not choices or not criteria:
        return ["judge_xlsx.py に CHOICES か CRITERIA が無い"]
    crit = {k: v for k, v in criteria}
    b = appendix_rows(protocol_text, "## 付録 B")
    for key in B_ROWS:
        if key not in crit:
            errs.append(f"judge_xlsx.py の『判定基準』に『{key}』の行が無い")
        elif key not in b:
            errs.append(f"草稿の付録 B に『{key}』の行が無い")
        elif crit[key].rstrip("。") != b[key].rstrip("。"):
            errs.append(f"judge_xlsx.py の『{key}』の文が草稿の付録 B と違う")
    m = re.search(r"除外理由＝E1〜E(\d+)", protocol_text)
    want = [f"E{i}" for i in range(1, int(m.group(1)) + 1)] if m else None
    got = choices.get("除外理由", "").split(",")
    if want is None:
        errs.append("草稿の付録 B に「除外理由＝E1〜En」が無い")
    elif got != want:
        errs.append(f"judge_xlsx.py の除外理由の選択肢 {got} が草稿の付録 B（{want[0]}〜{want[-1]}）と違う")
    return errs


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
    ptext = open(protocol_path, encoding="utf-8").read()
    rows = appendix_rows(ptext, "## 付録 F")
    if not rows:
        errs.append("草稿の付録 F に F の行が無い（数え方が壊れている）")
    decided = {k for k, v in rows.items() if "に決定" in v}
    by_sec = sheet_f_rows(lines)
    in_decided = by_sec.get(DECIDED_SECTION, set())
    in_pending = set().union(*(by_sec.get(s, set()) for s in PENDING_SECTIONS))
    for f in sorted(rows, key=lambda x: int(x[1:])):
        want_sec = "§1（判定者 1 が決めたこと）" if f in decided else "§2〜§4"
        if f not in (in_decided if f in decided else in_pending):
            errs.append(f"{CHECK}: 付録 F の {f} の行が {want_sec} に無い")
    for f in sorted((in_decided | in_pending) - set(rows)):
        errs.append(f"{CHECK}: 草稿の付録 F に無い番号 {f} の行がある")
    want = proposal_counts(ptext)
    got = sheet_counts(lines)
    if sum(want.values()) == 0:
        errs.append("草稿に【案】が 1 つも無い（数え方が壊れている）")
    for k in sorted(set(want) | set(got)):
        if want.get(k, 0) != got.get(k, 0):
            errs.append(f"{CHECK}: 【案】の数が節 {k} で草稿と違う（草稿 {want.get(k, 0)}・票 {got.get(k, 0)}）")
    return errs


def run(root, protocol_path=PROTOCOL, judge_path=JUDGE_PY):
    errs = check_sheet(root, protocol_path)
    errs += check_judge_tool(open(protocol_path, encoding="utf-8").read(), judge_path)
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
        judge = os.path.join(td, "judge_xlsx.py")
        shutil.copy(JUDGE_PY, judge)
        errs = run(base, proto, judge)
        print(("OK " if not errs else "NG ") + "陰性対照（変異なしで緑）", errs[:3])
        ok &= not errs
        paths = {"proto": proto, "judge": judge}

        def mutate(label, new, expect, fn=CHECK):
            nonlocal ok
            path = paths.get(fn) or os.path.join(base, fn)
            before = open(path, encoding="utf-8").read()
            after = new(before)
            if after == before:  # 変異の対象が無い＝検査を確かめられていない
                print("NG " + label + "（変異の対象が無い）")
                ok = False
                return
            open(path, "w", encoding="utf-8", newline="\n").write(after)
            e = run(base, proto, judge)
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
        # 4. F の番号（草稿の付録 F から読む・決定は §1 に）
        mutate("F18 の行が無い", lambda t: re.sub(r"(?m)^\| F18 \|.*\n", "", t), "F18 の行が §2〜§4 に無い")
        mutate("F19 の行が無い（決定の節）", lambda t: re.sub(r"(?m)^\| F19 \|.*\n", "", t), "F19 の行が §1")
        mutate("F10 を §1 から §2 に移す", lambda t: re.sub(r"(?m)^\| F10 \|.*\n", "", t).replace(
            "| F11 |", "| F10 | 移した行 | | | | |\n| F11 |", 1), "F10 の行が §1")
        mutate("票に草稿に無い番号（F22）", lambda t: t.replace("| F11 |", "| F22 | 足した行 | | | | |\n| F11 |", 1),
               "草稿の付録 F に無い番号 F22")
        mutate("草稿の付録 F に F21 を足す", lambda t: t.replace("| F20 |", "| F21 | 足した項目 | 全体 |\n| F20 |", 1),
               "F21 の行が §2〜§4 に無い", fn="proto")
        mutate("草稿の F18 を決定にする", lambda t: re.sub(r"(?m)^(\| F18 \| [^|]*?) \|", r"\1 → **2026-10-01 に決定** |", t),
               "F18 の行が §1", fn="proto")
        # 5. 【案】の数
        mutate("票の【案】の行を 1 つ落とす", lambda t: re.sub(r"(?m)^\| \[GSRR-60\] \|.*\n", "", t), "節 [GSRR-60] で草稿と違う")
        mutate("票に【案】の行を足す", lambda t: t + "| [GSRR-9] | 終わる日を 2027 年 3 月にする | |\n", "節 [GSRR-9] で草稿と違う")
        mutate("草稿に【案】を足す", lambda t: t.replace("### [GSRR-58] まとめる人の盲検\n",
                                                      "### [GSRR-58] まとめる人の盲検\n\n- 【案】足した案。\n", 1),
               "節 [GSRR-58] で草稿と違う", fn="proto")
        mutate("草稿の節の中の引用の行に【案】", lambda t: t.replace("### [GSRR-58] まとめる人の盲検\n",
                                                            "### [GSRR-58] まとめる人の盲検\n\n> 注【案】引用の中の案。\n", 1),
               "節 [GSRR-58] で草稿と違う", fn="proto")
        mutate("草稿の付録 C の【案】を消す", lambda t: t.replace("## 付録 C 抽出フォーム【案】", "## 付録 C 抽出フォーム", 1),
               "節 付録 C で草稿と違う", fn="proto")
        # 6. 判定者用ファイルの道具と草稿の付録 B
        mutate("道具の除外理由から E7 を落とす", lambda t: t.replace('"E1,E2,E3,E4,E5,E6,E7"', '"E1,E2,E3,E4,E5,E6"', 1),
               "除外理由の選択肢", fn="judge")
        mutate("道具の尺度の原著の行を変える", lambda t: t.replace("標本の有無は問わない。", "標本を持つ研究は一次研究とする。", 1),
               "『E4 の『尺度の原著』（2026-10-01）』の文が草稿の付録 B と違う", fn="judge")
        mutate("草稿の付録 B の基準の版を変える", lambda t: re.sub(r"(?m)^(\| 基準の版 \| )", r"\1（変えた）", t, count=1),
               "『基準の版』の文が草稿の付録 B と違う", fn="proto")
        mutate("草稿の付録 B の選択肢を E1〜E6 に", lambda t: t.replace("除外理由＝E1〜E7", "除外理由＝E1〜E6", 1),
               "除外理由の選択肢", fn="proto")
        # 7. issue-status.md は前タスクの事実のファイルと同じ検査（と E7）
        mutate("issue-status の判定の語", lambda t: t + "\n- 含める\n", "禁止語（judge）", fn=ISSUE_STATUS)
        mutate("issue-status の E7", lambda t: t + "\n- E7\n", "『E7』", fn=ISSUE_STATUS)
    # 数え方の確かめ: 最初の見出しより前と付録 F の中の【案】は数えない。節の中の引用の行は数える。
    # 見出しの中のほかの項目の参照で別の節に数えない
    demo = ("> 印: 【案】は案。\n## 1. x\n### [GSRR-6] y\n- a【案】\n- b【案・確認待ち】\n### 5.1 z\n- c【案】\n"
            "> 注【案】\n### [GSRR-7] 見出しの中の [GSRR-6] の参照\n- e【案】\n"
            "## 付録 C 抽出フォーム【案】\n### D.6 w\n- d【案】\n## 付録 F 一覧\n| F15 | 【案】の採否 |\n")
    want = {"[GSRR-6]": 2, "§5.1": 2, "[GSRR-7]": 1, "付録 C": 1, "付録 D.6": 1}
    got = dict(proposal_counts(demo))
    print(("OK " if got == want else "NG ") + "【案】の数え方（見出しの前・付録 F を数えず、節の中の引用は数える）", got)
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


