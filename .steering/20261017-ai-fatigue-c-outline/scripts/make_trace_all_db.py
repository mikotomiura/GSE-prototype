"""Make the whole TRACE database (xlsx): the 34 exploratory records and the 264 additional candidates in one book
(decision 36). It is for reading; nobody screens in it.

The 34 exploratory records carry the final decisions of the source database (sheet 'スクリーニング': the column
'最終判定', the exclusion code of '除外理由' and the centre written as '用途: 中心-A/B' in '自由記入'). The final
version is AI_fatigue_database_2026-10-18_judge_final_fixed.xlsx (AF002 included on 2026-10-18 from its full text,
decision 37). The decisions differing from registration-attachments/ai-screening/check-34.csv (the decisions as of
2026-10-17, against which the AI screener was checked) are printed and noted in the book. The 264 additional candidates carry no decision: they are
screened only after registration, in author 1's workbook (make_trace_db.py), and this book holds none of author 1's,
the AI screener's or author 2's judgements. Full-text links of the 264 are left out, so that the book cannot be a
way round GSRR-33 (no full text before a batch's stage 1 is committed); they are in author 1's workbook.

Inputs (outside the repository, except check-34.csv):
    <data>/records264.json, meta.json, ja.json       as for make_trace_db.py
    <data>/ja34.json (optional)                      machine translations of the 34 titles and abstracts
    --source-db   the source database, final version (AI_fatigue_database_2026-10-18_judge_final_fixed.xlsx)
    --abstracts34 the stage-1 inputs of the check on the 34 records (<ID>.stage1.txt), which hold the abstracts

Run (openpyxl via uv):
    uv run --with openpyxl python make_trace_all_db.py --data ~/Documents/TRACE/data \
        --source-db "$TRACE_DRIVE/../AI_fatigue_database_2026-10-18_judge_final_fixed.xlsx" \
        --abstracts34 ~/TRACE-screening/check34-r3/in --out "$TRACE_DRIVE/TRACE_database_all.xlsx"
    --dump34 <file> writes the 34 records (title and abstract) as JSON, the input of the translation.
"""

import argparse
import csv
import datetime
import json
import os
import re
from pathlib import Path

from openpyxl import load_workbook

import trace_style as st
from openpyxl import Workbook

TASK = Path(__file__).resolve().parent.parent
CHECK34 = TASK / "registration-attachments" / "ai-screening" / "check-34.csv"
DECISION = {"include": "含める", "exclude": "除外", "pending": "保留"}
NO_ABSTRACT = "（抄録なし: どの出どころにも見つからなかった。題名だけで判定する）"


def load(path, default=None):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def sheet(wb, name, key="ID"):
    """Rows of a sheet of the source database as dicts, keyed by ID; the header is the row whose first cell is ID."""
    rows = list(wb[name].iter_rows(values_only=True))
    h = next(i for i, r in enumerate(rows) if r and r[0] == key)
    head = [str(c) if c is not None else "" for c in rows[h]]
    return {str(r[0]).strip(): dict(zip(head, r)) for r in rows[h + 1:] if r and r[0] and re.match(r"AF\d{3}$", str(r[0]))}


def abstract34(path):
    """The abstract and its source from a stage-1 input: the lines after 'Abstract (<source>):'."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    i = next(k for k, ln in enumerate(lines) if ln.startswith("Abstract ("))
    src = lines[i][len("Abstract ("):].split(")")[0]
    text = "\n".join(lines[i + 1:]).strip()
    return ("", "") if src == "not retrieved" else (text, {"openalex": "OpenAlex", "europepmc": "Europe PMC"}.get(src, src))


def records34(source_db, abstracts_dir):
    wb = load_workbook(os.path.expanduser(source_db), read_only=True, data_only=True)
    bib, scr = sheet(wb, "文献DB"), sheet(wb, "スクリーニング")
    with open(CHECK34, encoding="utf-8") as f:
        human = {r["record_id"]: r for r in csv.DictReader(f)}
    if not set(human) == set(bib) == set(scr):
        raise SystemExit(f"check-34.csv and the source database list different records: {sorted(set(human) ^ set(bib))}")
    out = []
    for rid in sorted(human):
        b, s = bib[rid], scr[rid]
        dec = str(s.get("最終判定") or "").strip()
        if dec not in DECISION.values():
            raise SystemExit(f"{rid}: 最終判定 {dec!r} is not 含める, 除外 or 保留")
        code, centre = "", ""
        if dec == "除外":
            m = re.search(r"E\d", str(s.get("除外理由") or ""))
            code = m.group(0) if m else ""
        if dec == "含める":
            m = re.search(r"用途: (中心-[AB])", str(s.get("自由記入") or ""))
            if m:
                centre = m.group(1)
            elif human[rid]["human_final"] == "include":  # decided by the researcher (AF006, decision 4)
                centre = {"centre-A": "中心-A", "centre-B": "中心-B"}[human[rid]["human_centre"]]
            else:
                raise SystemExit(f"{rid}: included, with no centre in 自由記入 or check-34.csv")
        ab, src = abstract34(os.path.join(os.path.expanduser(abstracts_dir), f"{rid}.stage1.txt"))
        note = ""
        if rid == "AF006":
            note = "最終判定: 要協議の後、研究者が含めると決めた（2026-10-17・判断 4）。"
        if rid == "AF024":
            note = "最終判定: 要協議の後、研究者が除外と決めた（2026-10-17・判断 4）。除外理由は判定者 2 の推奨（E2）。"
        if dec != DECISION[human[rid]["human_final"]]:
            print(f"{rid}: {DECISION[human[rid]['human_final']]} in check-34.csv (2026-10-17) -> {dec} in the final version")
            note = (note + " ").lstrip() + (f"2026-10-17 の最終判定（AI の選別者の確かめの相手・check-34.csv）は"
                                            f"{DECISION[human[rid]['human_final']]}。")
        if rid == "AF002":
            note += "2026-10-18 に研究者が共有した出版社の版の全文で判定者 1 が判定し直し、含める（中心-A）にした（E6 の理由がなくなった）。"
        doi = str(b.get("DOI") or "")
        out.append({"id": rid, "title": str(b.get("論文タイトル") or ""), "authors": str(b.get("著者（短縮表示）") or ""),
                    "year": b.get("巻号年"), "journal": str(b.get("掲載誌・媒体") or ""),
                    "doi": doi if doi.startswith("10.") else "", "abstract": ab, "abstract_source": src,
                    "decision": dec, "code": code, "centre": centre, "note": note})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--source-db", required=True)
    ap.add_argument("--abstracts34", required=True)
    ap.add_argument("--out")
    ap.add_argument("--dump34")
    a = ap.parse_args()
    data = os.path.expanduser(a.data)
    r34 = records34(a.source_db, a.abstracts34)
    if a.dump34:
        with open(os.path.expanduser(a.dump34), "w", encoding="utf-8") as f:
            json.dump([{"id": r["id"], "title": r["title"], "abstract": r["abstract"]} for r in r34], f,
                      ensure_ascii=False, indent=1)
        print(f"wrote {a.dump34}: {len(r34)} records")
        return
    if not a.out:
        raise SystemExit("--out is needed")
    recs = sorted(load(os.path.join(data, "records264.json")), key=lambda r: r["order"])
    meta = load(os.path.join(data, "meta.json"), {})
    ja = {**load(os.path.join(data, "ja.json"), {}), **load(os.path.join(data, "ja34.json"), {})}

    def jt(rid, k="title_ja"):
        return (ja.get(rid) or {}).get(k, "")

    rows = []  # one row per record: list sheet and bibliography sheet share the order
    for r in r34:
        rows.append({**r, "set": "探索（34 件）", "order": "", "population": "", "source": "元の文献 DB",
                     "group": ""})
    for r in recs:
        m = meta.get(r["id"], {})
        doi = str(r.get("doi") or "")
        rows.append({"id": r["id"], "set": "追加候補（264 件）", "order": r["order"] + 1, "population": r["population"],
                     "title": r["title"], "authors": m.get("authors", ""), "year": r.get("year"),
                     "journal": r.get("journal") or "", "doi": doi if doi.startswith("10.") else "",
                     "abstract": (m.get("abstract") or "").strip(), "abstract_source": m.get("abstract_source", ""),
                     "decision": "未判定（登録の後）", "code": "", "centre": "", "source": r.get("source") or "",
                     "group": r.get("group", ""),
                     "note": "　".join(x for x in (r.get("population_note", ""), m.get("abstract_note", "")) if x)})
    bib_row = {x["id"]: i + 2 for i, x in enumerate(rows)}
    n34 = {k: sum(r["decision"] == k for r in r34) for k in ("含める", "保留", "除外")}

    wb = Workbook()
    st.intro(wb.active, "TRACE｜全体の文献 DB（探索 34 件＋追加候補 264 件）",
             f"作成 {datetime.date.today().isoformat()}・{len(rows)} 件・読むための一覧で、ここでは判定しない", [
        ("中身", [
            f"探索の 34 件（AF001〜AF034）: 元の文献 DB の最終版（2026-10-18）の最終判定（含める {n34['含める']}・保留 {n34['保留']}・除外 {n34['除外']}）。"
            "判定者 1 と 2 の合意で、要協議の 2 件は研究者が決めた（AF006 含める・AF024 除外）。AF002 は全文を得て 2026-10-18 に含めた。",
            f"追加候補の {len(recs)} 件: 判定は空欄。登録の後に判定者 1・AI・共著者が判定する。",
        ]),
        ("この冊に入れていないもの", [
            "追加候補について、判定者 1・AI・共著者のどの判定も入れていない。判定者 1 が記入するのは『TRACE_database.xlsx』（同じフォルダ）。",
            "追加候補の全文へのリンク。全文は判定者 1 用の DB の『段2・3』から開く（束の段 1 を終えるまで全文を開かない決まりのため）。",
        ]),
        ("日本語訳について", [
            "題名と抄録の日本語は Claude による機械訳で、読む助けにすぎない。判定の根拠は英語の原文。",
        ]),
    ])

    ls = wb.create_sheet("一覧")
    cols = ["ID", "集合", "順", "対象の群", "論文タイトル", "題名（日本語・機械訳）", "年", "最終判定", "除外理由", "中心", "注記"]
    st.table(ls, cols, [10, 16, 5, 14, 52, 40, 6, 16, 9, 10, 40],
             [[x["id"], x["set"], x["order"], x["population"], x["title"], jt(x["id"]), x["year"], x["decision"],
               x["code"], x["centre"], x["note"] if x["set"].startswith("探索") else ""] for x in rows],
             wrap={"対象の群", "論文タイトル", "題名（日本語・機械訳）", "注記"},
             links={"ID": lambda v: (f"#'文献DB'!A{bib_row[v[0]]}", v[0])},
             tab="2563EB", height=lambda v: st.text_height((v[3], 14), (v[4], 52), (v[5], 40), (v[10], 40)))
    st.choices(ls, cols, [("最終判定", "含める,除外,保留"), ("中心", "中心-A,中心-B")])  # for the colours only

    db = wb.create_sheet("文献DB")
    cols = ["ID", "集合", "論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "年", "掲載誌・媒体",
            "DOI", "抄録の出どころ", "同じ研究の群", "出どころ", "注記"]
    st.table(db, cols, [10, 16, 36, 30, 70, 60, 24, 6, 22, 24, 12, 18, 16, 24],
             [[x["id"], x["set"], x["title"], jt(x["id"]), x["abstract"] or NO_ABSTRACT, jt(x["id"], "abstract_ja"),
               x["authors"], x["year"], x["journal"], x["doi"], x["abstract_source"], x["group"], x["source"], x["note"]]
              for x in rows],
             wrap={"論文タイトル", "題名（日本語・機械訳）", "抄録", "抄録（日本語・機械訳）", "著者", "掲載誌・媒体", "注記"},
             links={"DOI": lambda v: ("https://doi.org/" + v[9], v[9]) if v[9] else None},
             tab="64748B", height=lambda v: st.text_height((v[2], 36), (v[3], 30), (v[4], 70), (v[5], 60)))

    out = os.path.expanduser(a.out)
    tmp = out + ".tmp.xlsx"
    wb.save(tmp)
    os.replace(tmp, out)
    print(f"wrote {out}: {len(r34)} + {len(recs)} records, 34: {n34}, translations {sum(bool(jt(x['id'])) for x in rows)}")


if __name__ == "__main__":
    main()
