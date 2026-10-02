"""コミットするファイルに、抄録の本文・問いの逐語（抄録の訳・抜き出し）が入っていないか（design §14・引き継ぎ §2 の 4）。

各抄録・各問いの本文（空白を除いた形）から 40 字の窓を 20 字おきに（末尾も）すべて取り、対象のファイルの文字
（xlsx・docx は XML の部品をすべて・タグと空白を除いた形）の 40 字の部分列と照らす。60 字以上続けて写すと、どこを写しても
窓が 1 つは丸ごと入る（Codex 2 巡目の P2: 5 つの窓だけの抜き取りでは、窓の間の一段落を逃した）。
★ 書誌の値（題名・掲載誌・同じ研究の群）の断片は除く（問いの 2 行目と最後の行は判定者用ファイルの書誌の値で、表と提案に載せてよい）。
★ 当たった文の断片は表示しない（検査の出力が新しい漏れの経路にならないように・Codex 2 巡目の P1）。種類と件数だけ。
★ 対象のファイルが 1 つも無ければ終了コード 2（何も見ずに緑にしない・Codex 2 巡目の P2）。
★ 前のセッションの scratchpad の使い捨ての道具を写して直した（パスはこのファイルの場所から組む）。
使い方: uv run --with openpyxl python leak_scan.py <タスクのディレクトリからの相対パス>... [--positive]
        （--positive: 陽性対照。抄録の全文・抄録の途中の 60 字・短い本文を混ぜた一時ファイルが、それぞれ NG になる）
"""
import json
import os
import re
import sys
import tempfile
import zipfile

import openpyxl

import common as C

FT = os.path.join(C.FULLTEXT_DIR, "_abstracts")
N, STEP = 40, 20


def text_of(p):
    if p.endswith((".xlsx", ".docx")):
        with zipfile.ZipFile(p) as z:
            return "".join(z.read(n).decode("utf-8", "replace") for n in z.namelist() if n.endswith((".xml", ".rels")))
    return open(p, encoding="utf-8", errors="replace").read()


def norm(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")
    return re.sub(r"\s+", "", s)


def windows(t):
    if len(t) < N:
        return []
    return [t[k:k + N] for k in range(0, len(t) - N + 1, STEP)] + [t[-N:]]


def sources():
    """（抄録の本文の列, 問いの本文の列）。どちらも空白を除いた形。"""
    abstracts = [norm(v.get("text") or "") for v in json.load(open(os.path.join(FT, "abstracts.json"), encoding="utf-8")).values()]
    questions = [json.loads(x)["question"] for x in open(os.path.join(FT, "ta-questions-verbatim.jsonl"), encoding="utf-8") if x.strip()]
    questions = [norm(q.split("\n", 1)[1] if "\n" in q else q) for q in questions]
    return abstracts, questions


def probes(abstracts, questions):
    """窓 → 種類（抄録／問い）。★ 題名の断片の窓は除く。"""
    out = {}
    for src, kind in ((abstracts, "抄録"), (questions, "問い")):
        for t in src:
            for w in windows(t):
                out.setdefault(w, kind)
    # ★ 書誌の値（判定者用ファイルの題名・掲載誌・同じ研究の群、探索の題名・掲載）の断片は、抄録・問いの本文の漏れではない。
    #   問いの 2 行目（題名・年・掲載誌）と最後の行（同じ研究の群）は、判定者用ファイルの同じ値を載せている。
    #   ★ 抄録の欄を持つ列は入れない（ここに入れた列の文は、窓から消えて検査されなくなる）
    rows = list(openpyxl.load_workbook(C.JUDGE_FILE, read_only=True)[C.JUDGE_SHEET].iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    cols = [h.index(c) for c in ("題名（書誌の記録）", "掲載誌", "同じ研究の群")]
    biblio = "|".join(norm(str(r[k] or "")) for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0] for k in cols)
    biblio += "|" + "|".join(norm(str(x.get(k) or "")) for x in json.load(open(C.SEARCH_RECORDS, encoding="utf-8"))
                             for k in ("title", "venue"))
    n0 = len(out)
    out = {w: k for w, k in out.items() if w not in biblio}
    print(f"書誌の値（題名・掲載誌・同じ研究の群）に含まれる窓を除いた: {n0 - len(out)} 個")
    print(f"窓 {len(out)} 個（抄録 {sum(1 for k in out.values() if k == '抄録')}・問い {sum(1 for k in out.values() if k == '問い')}）")
    return out


def hits(body, pr):
    """body の 40 字の部分列のうち、窓に当たったものの種類ごとの件数（★ 断片は返さない）。"""
    found = {}
    for i in range(len(body) - N + 1):
        k = pr.get(body[i:i + N])
        if k:
            found[k] = found.get(k, 0) + 1
    return found


def positive(pr, abstracts, questions):
    """陽性対照: 一時ファイルに混ぜて、どれも NG になる。"""
    a = next(t for t in abstracts if len(t) >= 300)
    cases = [("抄録の全文", a), ("抄録の途中の 60 字", a[150:210])]
    short = next((t for t in abstracts + questions if N <= len(t) < 120 and any(w in pr for w in windows(t))), None)
    cases.append(("短い本文（40〜119 字）", short))
    ok = True
    for name, text in cases:
        if text is None:
            print("SKIP", f"陽性対照（{name}）: その長さの本文が無い")
            continue
        fd, tmp = tempfile.mkstemp(suffix=".md", prefix="leak-pos-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write("前の文\n" + text + "\n後の文\n")
            hit = bool(hits(norm(text_of(tmp)), pr))
        finally:
            os.remove(tmp)
        print(("PASS" if hit else "FAIL"), f"陽性対照（{name}を混ぜた一時ファイルが NG になる）")
        ok &= hit
    return ok


def main(argv):
    files = [os.path.join(C.TASK, p) for p in argv if not p.startswith("--")]
    if not files:
        print("対象のファイルが無い（何も見ずに緑にしない）")
        sys.exit(2)
    abstracts, questions = sources()
    pr = probes(abstracts, questions)
    bad = 0
    for p in files:
        found = hits(norm(text_of(p)), pr)
        print(("NG" if found else "OK"), os.path.relpath(p, C.TASK), found or "")
        bad += bool(found)
    if "--positive" in argv:
        bad += not positive(pr, abstracts, questions)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
