"""Make the workbook in which author 1 re-checks every exclusion of author 1 at stage 1 and stage 2 against the
registered rules of attachment 6 (decision 92): the order of the exclusion codes, the meaning of E3 (Q2, Q5), the
narrow stage-1 E2 (Q4) and "if the input says nothing on a question, the answer is unclear, not no".

Rows are author 1's latest committed judgement of each record at each stage (screening/s1, s2 *.author1.csv) that is
an exclusion. Author 2's judgements and the AI safety net's answers are not shown (author 1 re-checks alone). Each
row carries author 1's original decision, code, read range and note (from the database, which must agree with the
committed code), a mechanical reading aid (abstract present; a fatigue word in the title or abstract), and input
columns: the result (keep / change the code / include, and at stage 2 also pending), the new code and a note.

Run from ~/TRACE/scripts (openpyxl via uv):
    uv run -q --with openpyxl python -I <this file> --out <new directory>
"""

import argparse
import csv
import glob
import os
import re
import sys

sys.path.insert(0, os.getcwd())   # ~/TRACE/scripts

import openpyxl
from openpyxl import Workbook

import c_screening as c
import make_trace_db as db
import trace_style as st

FATIGUE = re.compile(r"fatigu|exhaust|burn-?out|deplet|tired|weari|drain", re.I)   # Q4's names, as stems
ORDER1, ORDER2 = ["E2", "E4", "E1", "E3", "E7"], ["E2", "E3", "E4", "E1", "E5", "E7"]
JA = {"include": "含める", "exclude": "除外", "pending": "保留"}
READ_JA = {"abstract": "抄録", "title only": "題名のみ", "full text": "全文", "part of full text": "全文の一部"}
RESULT1 = "元のまま,理由を変える,含めるに変える"
RESULT2 = "元のまま,理由を変える,含めるに変える,保留に変える"
CODES1, CODES2 = "E1,E2,E3,E4,E7", "E1,E2,E3,E4,E5,E7"

# attachment 6 (registration-attachments/ai-screening/instructions.md), sections 3 and 4: the English text is the
# registered rule; the Japanese is a reading aid
RULES = [
    ("Q1（→ E4）", "一次研究か。人からデータを集めるか分析するか（量的・質的）。レビュー・研究やレビューのプロトコル・論評・社説・方法論の論文・訂正通知は一次研究でない。AI の利用・監督に関わる疲労の尺度でない尺度（一般の疲労・ビデオ会議疲労・AI 不安・認知負荷・テクノストレスなど）の開発・妥当化が主な貢献の論文は、標本があっても一次研究でない。AI の利用・監督に関わる疲労の尺度の開発・妥当化の論文は一次研究。"),
    ("Q2（→ E3）", "参加者が AI の系を使う・監督する・評価するか、または研究が AI の利用を導入・操作・比較するか（範囲の決定 (a)）。自動化には範囲の決定 (b) を当てる。論文が手法として AI を使っているかどうかではない。"),
    ("Q3（→ E1）", "AI が疲労を検知・予測する道具としてだけ使われ、AI を使う・監督する・評価する人が研究の対象でないか。"),
    ("Q4（→ E2）", "疲労（消耗・疲弊・燃え尽き様の消耗）が定義・測定・質的に分析されているか。題名・抄録の段では、題名・抄録が疲労の測定や分析が無いと述べるときだけ no。抄録が疲労を含まない測定や結果を並べているだけなら不明（抄録は副次の測定を省くことが多い）。全文の段では、全文が報告する測定と分析から答える。"),
    ("Q5（→ E3）", "その疲労が AI の利用と関係づけて（AI の利用の結果・相関・媒介・主題として）調べられているか。AI と関係のない部分でだけ測られていれば no。"),
    ("Q6（→ E7）", "全文の言語が英語か日本語か、または英語・日本語の版があるか。題名・抄録の段では、入力が本文の言語を述べない限り不明。"),
    ("Q7（→ E5・全文の段だけ）", "全文が、別の記録と同じ標本を重複・二次の報告として報告しているか。全文自身がそう述べるときだけ yes。"),
    ("答え方", "どの問いも yes・no・不明で答える。入力が何も述べていなければ答えは不明で、no ではない。"),
    ("題名・抄録の段の決め方", "除外につながる答えが 1 つでもあれば除外。2 つ以上当たるときは E4、E1、E3、E2、E7 の順で先のもの。そうでなければ含める（迷ったら含める）。"),
    ("全文の段の決め方", "無料の全文が無ければ保留＋E6（本文が英語・日本語以外と分かり英語・日本語の版も無ければ E7）。除外につながる答えがあれば除外で、E4、E1、E3、E2、E5、E7 の順で先のもの。全文を読んでも Q1〜Q5 のどれかが不明のままなら保留（理由なし）。そうでなければ含める。"),
]


def registered_text():
    """item -> the verbatim registered English of attachment 6 (the table rows Q1-Q7 and the decision bullets)."""
    lines = open(c.ATT / "ai-screening" / "instructions.md", encoding="utf-8").read().splitlines()
    q = {l.split("|")[1].strip(): l.strip() for l in lines if re.match(r"\| Q[1-7] \|", l)}
    s1 = lines.index("### Stage 1 (title and abstract)")
    s2 = lines.index("### Stage 2 (full text)")
    s3 = lines.index("### Stage 3 (centre), for records included at stage 2")
    bullets = lambda a, b: " ".join(l[2:] for l in lines[a:b] if l.startswith("- "))
    out = {f"Q{n}": q[f"Q{n}"] for n in range(1, 8)}
    out["答え方"] = next(l for l in lines if "If the input says nothing on a question" in l)
    out["題名・抄録の段の決め方"] = bullets(s1, s2)
    out["全文の段の決め方"] = bullets(s2, s3)
    return out


def latest(stage):
    """record ID -> (batch, row) of author 1's latest committed judgement at the stage."""
    out = {}
    for f in sorted(glob.glob(str(c.DEFAULTS["state"] / f"s{stage}" / "b*.author1.csv"))):
        b = os.path.basename(f).split(".")[0]
        for r in csv.DictReader(open(f)):
            if r["stage"] == str(stage):
                out[r["record_id"]] = (b, r)
    return out


def sheet_rows(sheet):
    ws = openpyxl.load_workbook(c.DEFAULTS["xlsx"])[sheet]
    head = [x.value for x in ws[1]]
    out = {}
    for row in ws.iter_rows(min_row=2):
        if row[0].value:
            out[row[0].value] = ({h: x.value for h, x in zip(head, row)},
                                 {h: x.hyperlink.target for h, x in zip(head, row) if x.hyperlink})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", default="~/Documents/TRACE/data")
    a = ap.parse_args()
    out, data = os.path.expanduser(a.out), os.path.expanduser(a.data)
    if os.path.exists(out) and os.listdir(out):
        raise SystemExit(f"{out} is not empty")
    recs = {r["id"]: r for r in db.load_records(data)}
    meta = db.load(os.path.join(data, "meta.json"), {})
    ja = db.load(os.path.join(data, "ja.json"), {})
    jt = lambda i: (ja.get(i) or {}).get("title_ja", "")
    abstract = lambda i: (meta.get(i, {}).get("abstract") or "").strip()
    d1, d2 = sheet_rows("段1"), sheet_rows("段2・3")
    s1 = {i: v for i, v in latest(1).items() if v[1]["decision"] == "exclude"}
    s2 = {i: v for i, v in latest(2).items() if v[1]["decision"] == "exclude"}
    bad = [i for i, (b, r) in s1.items() if (d1[i][0]["除外理由"] or "") != r["code"]] + \
          [i for i, (b, r) in s2.items() if (d2[i][0]["除外理由"] or "") != r["code"]]
    if bad:
        raise SystemExit(f"the database's code differs from the committed one: {bad}")
    rows1 = []
    for i, (b, r) in sorted(s1.items(), key=lambda kv: (ORDER1.index(kv[1][1]["code"]), kv[1][0], kv[0])):
        x = d1[i][0]
        text = f"{recs[i]['title']} {abstract(i)}"
        rows1.append([i, b, x["対象の群"], recs[i]["title"], jt(i), JA[r["decision"]], r["code"],
                      READ_JA.get(r["read"], r["read"]), x["根拠メモ"] or "", "あり" if abstract(i) else "なし",
                      "あり" if FATIGUE.search(text) else "なし", "", "", ""])
    rows2 = []
    for i, (b, r) in sorted(s2.items(), key=lambda kv: (ORDER2.index(kv[1][1]["code"]), kv[1][0], kv[0])):
        x, links = d2[i]
        rows2.append([i, b, x["対象の群"], recs[i]["title"], jt(i), x["全文"] or "", x["ファイル"] or "",
                      JA[r["decision"]], r["code"], READ_JA.get(r["read"], r["read"]), x["根拠メモ"] or "", "", "", "",
                      links.get("ファイル")])
    wb = Workbook()
    st.intro(wb.active, "TRACE｜著者 1 の除外の見直し", f"題名・抄録の段 {len(rows1)} 件・全文の段 {len(rows2)} 件", [
        ("このファイルについて", [
            "著者 1 が除外にした記録（題名・抄録の段と全文の段）を、登録の決まり（付録 6 の問い Q1〜Q7 と決め方）に照らして見直すための一覧。",
            "決まりは『決まり』のシートにある（英語が登録の文、日本語は読む助け）。2 人の冊の『判定基準』には、理由の順・E3 の意味・題名・抄録の段の E2 の狭さが書かれていなかった。",
            "共著者の判定と AI の網の答えは載せていない。著者 1 が 1 人で見直す。",
        ]),
        ("記入する欄（青）", [
            "『見直しの結果』を選ぶ。元のままなら「元のまま」。理由だけが違えば「理由を変える」で、『見直しの除外理由』に理由を入れる。",
            "題名・抄録の段で除外につながる答えが無ければ「含めるに変える」。全文の段で Q1〜Q5 のどれかが不明のままなら「保留に変える」。",
            "変えたときは『見直しの根拠メモ』に、どの問いの答えでそうなるかを書く。",
        ]),
        ("読む助けの列", [
            "『抄録』は抄録が取れているか。『疲労の語』は題名か抄録に疲労の語（fatigue・exhaust・burnout・deplet・tired・weari・drain）が出るかを機械的に見ただけで、判定ではない。",
            "ID を押すと『文献DB』のその記録の抄録へ飛ぶ。全文の段の『ファイル』は全文のリンク。",
        ]),
    ])
    c1 = ["ID", "束", "対象の群", "論文タイトル", "題名（日本語・機械訳）", "元の判定", "元の除外理由", "元の読んだ範囲",
          "元の根拠メモ", "抄録", "疲労の語", "見直しの結果", "見直しの除外理由", "見直しの根拠メモ"]
    c2 = ["ID", "束", "対象の群", "論文タイトル", "題名（日本語・機械訳）", "全文", "ファイル", "元の判定", "元の除外理由",
          "元の読んだ範囲", "元の根拠メモ", "見直しの結果", "見直しの除外理由", "見直しの根拠メモ"]
    ids = [v[0] for v in rows1] + [v[0] for v in rows2 if v[0] not in {w[0] for w in rows1}]
    bib_row = {i: n + 2 for n, i in enumerate(ids)}
    inputs = {"見直しの結果", "見直しの除外理由", "見直しの根拠メモ"}
    w1 = wb.create_sheet("段1の見直し")
    st.table(w1, c1, [10, 5, 12, 40, 32, 8, 8, 9, 34, 6, 7, 13, 10, 30], rows1, inputs=inputs,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "元の根拠メモ", "見直しの根拠メモ"},
             links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0])}, tab="2563EB",
             height=lambda v: st.text_height((v[3], 40), (v[4], 32), (v[8], 34)))
    st.choices(w1, c1, [("見直しの結果", RESULT1), ("見直しの除外理由", CODES1)])
    w2 = wb.create_sheet("段2の見直し")
    st.table(w2, c2, [10, 5, 12, 40, 32, 12, 13, 8, 8, 10, 34, 13, 10, 30], [v[:14] for v in rows2], inputs=inputs,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "元の根拠メモ", "見直しの根拠メモ"},
             links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0]),
                    "ファイル": lambda v: (dict((w[0], w[14]) for w in rows2)[v[0]], v[6]) if v[6] and dict((w[0], w[14]) for w in rows2)[v[0]] else None},
             tab="0D9488", height=lambda v: st.text_height((v[3], 40), (v[4], 32), (v[10], 34)))
    st.choices(w2, c2, [("見直しの結果", RESULT2), ("見直しの除外理由", CODES2)])
    bib = wb.create_sheet("文献DB")
    brows = []
    for i in ids:
        r = recs[i]
        doi = str(r.get("doi") or "")
        doi = doi if doi.startswith("10.") else ""
        brows.append([i, r["title"], jt(i), abstract(i) or "（抄録なし: どの出どころにも見つからなかった）",
                      (ja.get(i) or {}).get("abstract_ja", ""), meta.get(i, {}).get("authors", ""), r.get("year"),
                      r.get("journal"), doi])
    st.table(bib, ["ID", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体",
                   "DOI"], [10, 36, 30, 70, 60, 24, 6, 22, 24], brows,
             wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体"},
             links={"DOI": lambda v: ("https://doi.org/" + v[8], v[8]) if v[8] else None}, tab="64748B",
             height=lambda v: st.text_height((v[1], 36), (v[2], 30), (v[3], 70), (v[4], 60)))
    ru = wb.create_sheet("決まり")
    reg = registered_text()
    rule_rows = [[k, v, reg[k.split("（")[0]]] for k, v in RULES]
    st.table(ru, ["項目", "内容（日本語・読む助け）", "登録の文（付録 6・英語）"], [22, 80, 70], rule_rows,
             wrap={"内容（日本語・読む助け）", "登録の文（付録 6・英語）"}, tab="64748B",
             height=lambda v: st.text_height((v[1], 80), (v[2], 70)))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "TRACE_author1_exclusion_review.xlsx")
    wb.save(path)
    print(f"wrote {path}: stage 1 {len(rows1)}, stage 2 {len(rows2)}")


if __name__ == "__main__":
    main()
