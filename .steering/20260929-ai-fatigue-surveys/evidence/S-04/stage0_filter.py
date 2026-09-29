"""S-04: 機械的な前ふるい（decisions.md 判断 9 の逸脱）。

題名＋抄録に、AI の語・疲労や負荷の語・比較のデザインの語の 3 つが当たる記録だけを残す。
★ 正規表現はこのファイルで固定し、通った記録を見る前に書いた。repo に書くのは書誌と一致した語だけ。
通った記録の抄録は、サブエージェントの抽出用に repo の外（第 3 引数）へ書く。

使い方: python stage0_filter.py <search_s04 の結果 JSON> <出力 JSON> <抄録の置き場（repo の外）>
"""
import json
import os
import re
import sys

AI = re.compile(r"(?i)\bAI\b|artificial intelligence|generative|chatgpt|copilot|large language model|\bLLMs?\b|"
                r"\bscribes?\b|ambient (listening|documentation|clinical|voice)|chatbot|\bGPT")
OUT = re.compile(r"(?i)burn-?out|fatigue|exhaust|workload|work load|task load|cognitive load|\bburden|NASA-?TLX|"
                 r"mini-?z|maslach|well-?being")
DESIGN = re.compile(r"(?i)randomi[sz]|\btrial\b|crossover|cross-over|pre-?post|pre- and post|before[- ]and[- ]after|"
                    r"quasi-?experiment|difference-in-differences|control(led)? group|comparison group|"
                    r"pre-?implementation|post-?implementation|\bbaseline\b|follow-?up|\bpilot\b|cohort|longitudinal|"
                    r"stepped-?wedge|matched|propensity|\bexperiment")


def main(src, out, abs_path):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    d = json.load(open(src, encoding="utf-8"))
    ab = json.load(open(os.path.join(os.path.dirname(abs_path), "s04_abstracts.json"), encoding="utf-8"))
    u = {}
    for run in d["runs"]:
        for r in run["records"]:
            k = (r.get("doi") or r["key"] or r["title"]).lower()
            e = u.setdefault(k, {"key": r["key"], "title": r["title"], "year": r.get("year"), "doi": r.get("doi", ""),
                                 "journal": r.get("journal", ""), "sources": []})
            e["sources"].append(f'{run["source"]}|{run["label"]}')
    kept, passed_abs = [], {}
    for k, e in u.items():
        txt = (e["title"] or "") + " " + (ab.get(e["key"]) or "")
        m = [x.search(txt) for x in (AI, OUT, DESIGN)]
        e["matched"] = [x.group(0) if x else None for x in m]
        e["has_abstract"] = bool(ab.get(e["key"]))
        e["stage0"] = all(m)
        if e["stage0"]:
            kept.append(e)
            passed_abs[e["key"]] = ab.get(e["key"]) or ""
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"design": "decisions.md 判断 9", "n_unique": len(u), "n_pass": len(kept),
                   "records": sorted(u.values(), key=lambda e: (not e["stage0"], str(e["year"])))},
                  fh, ensure_ascii=False, indent=1)
    with open(abs_path, "w", encoding="utf-8") as fh:
        json.dump(passed_abs, fh, ensure_ascii=False, indent=1)
    print("unique", len(u), "pass", len(kept))


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:4])
