"""コミットするファイルに、抄録の本文・問いの逐語（抄録の訳・抜き出し）が入っていないか（design §14・引き継ぎ §2 の 4）。

各抄録・各問いの本文から 40 字の窓を 5 つ取り、対象のファイルの文字（xlsx・docx は XML の部品をすべて）に含まれるかを見る。
★ 題名の断片は除く（問いの 2 行目が題名で、題名は表と提案に載せてよい）。
★ 前のセッションの scratchpad の使い捨ての道具を写した（パスはこのファイルの場所から組む）。
使い方: uv run --with openpyxl python leak_scan.py <タスクのディレクトリからの相対パス>... [--positive]
        （--positive: 陽性対照。抄録を 1 つ混ぜた一時ファイルが NG になることを確かめる）
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


def text_of(p):
    if p.endswith((".xlsx", ".docx")):
        with zipfile.ZipFile(p) as z:
            return "".join(z.read(n).decode("utf-8", "replace") for n in z.namelist() if n.endswith((".xml", ".rels")))
    return open(p, encoding="utf-8", errors="replace").read()


def norm(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")
    return re.sub(r"\s+", "", s)


def probes():
    abstracts = [v.get("text") or "" for v in json.load(open(os.path.join(FT, "abstracts.json"), encoding="utf-8")).values()]
    questions = [json.loads(x)["question"] for x in open(os.path.join(FT, "ta-questions-verbatim.jsonl"), encoding="utf-8") if x.strip()]
    out = []
    for src, kind in ((abstracts, "抄録"), (questions, "問い")):
        for t in src:
            t = norm(t.split("\n", 1)[1] if kind == "問い" and "\n" in t else t)
            if len(t) < 120:
                continue
            for k in range(5):
                i = (len(t) - 40) * k // 4
                out.append((kind, t[i:i + 40]))
    rows = list(openpyxl.load_workbook(C.JUDGE_FILE, read_only=True)[C.JUDGE_SHEET].iter_rows(values_only=True))
    h = list(rows[C.JUDGE_HEADER_ROW - 1])
    it = h.index("題名（書誌の記録）")
    titles = "|".join(norm(str(r[it] or "")) for r in rows[C.JUDGE_HEADER_ROW:] if r and r[0])
    titles += "|" + "|".join(norm(x["title"] or "") for x in json.load(open(C.SEARCH_RECORDS, encoding="utf-8")))
    n0 = len(out)
    out = [(k, w) for k, w in out if w not in titles]  # ★ 題名の断片は抄録・問いの本文の漏れではない
    print(f"題名に含まれる窓を除いた: {n0 - len(out)} 個")
    print(f"窓 {len(out)} 個（抄録 {sum(1 for k, _ in out if k == '抄録')}・問い {sum(1 for k, _ in out if k == '問い')}）")
    return out, abstracts


def main(argv):
    pr, abstracts = probes()
    files = [os.path.join(C.TASK, p) for p in argv if not p.startswith("--")]
    bad = 0
    for p in files:
        body = norm(text_of(p))
        hits = [(k, w) for k, w in pr if w in body]
        print(("NG" if hits else "OK"), os.path.relpath(p, C.TASK), len(hits), [w[:20] for _, w in hits[:3]])
        bad += bool(hits)
    if "--positive" in argv:
        a = next(x for x in abstracts if len(norm(x)) >= 200)
        fd, tmp = tempfile.mkstemp(suffix=".md", prefix="leak-pos-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write("前の文\n" + a + "\n後の文\n")
            hit = any(w in norm(text_of(tmp)) for _, w in pr)
        finally:
            os.remove(tmp)
        print(("PASS" if hit else "FAIL"), "陽性対照（抄録を 1 つ混ぜた一時ファイルが NG になる）")
        bad += not hit
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
