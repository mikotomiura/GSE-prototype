"""S-04: 0 段目の補い（decisions.md 判断 10）。

stage0_filter.py の比較のデザインの正規表現に「preintervention / postintervention / prospective / retrospective /
usual care / wait-list / comparative」などが無く、種文献（Olson ほか 2025・前後比較）が落ちていた。
AI の語と疲労・負荷の語は当たるがデザインの語だけが当たらなかった記録に、下の EXTRA を当てて拾い直す。
残す条件は 0 段目と同じ（Europe PMC の 3 本は全部、ほかは burnout|fatigue|exhaust を含むもの）。
使い方: python stage0_supplement.py <stage0 の JSON> <search の抄録 JSON（repo の外）> <出力 JSON> <抽出用の抄録の置き場（repo の外）>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stage0_filter import AI, DESIGN, OUT  # noqa: E402

EXTRA = re.compile(r"(?i)pre-?intervention|post-?intervention|pre-? and post-?|pre- ?and post|prospective|retrospective|"
                   r"interrupted time|time series|compared (with|to) (a |the )?(control|usual|non-?users?)|usual care|"
                   r"historical control|survey(s)? (before|after)|\b(pre|post)-?survey|pre-?pilot|post-?pilot|waiting list|"
                   r"wait-?list|comparative")
FT = re.compile(r"(?i)burn-?out|fatigue|exhaust")


def main(stage0, abs_all, out, out_abs):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    d = json.load(open(stage0, encoding="utf-8"))
    ab = json.load(open(abs_all, encoding="utf-8"))
    sel, sel_abs = [], []
    for r in d["records"]:
        if r["stage0"]:
            continue
        txt = (r["title"] or "") + " " + (ab.get(r["key"]) or "")
        if AI.search(txt) and OUT.search(txt) and not DESIGN.search(txt) and EXTRA.search(txt):
            if any(s.startswith("Europe") for s in r["sources"]) or FT.search(txt):
                i = f"C{len(sel) + 1:03d}"
                sel.append({"id": i, "doi": r["doi"], "title": r["title"], "year": r["year"], "journal": r["journal"],
                            "sources": r["sources"]})
                sel_abs.append({**sel[-1], "abstract": re.sub(r"<[^>]+>", " ", ab.get(r["key"]) or "")})
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"design": "decisions.md 判断 10", "records": sel}, fh, ensure_ascii=False, indent=1)
    with open(out_abs, "w", encoding="utf-8") as fh:
        json.dump(sel_abs, fh, ensure_ascii=False, indent=0)
    print(len(sel))


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:5])
