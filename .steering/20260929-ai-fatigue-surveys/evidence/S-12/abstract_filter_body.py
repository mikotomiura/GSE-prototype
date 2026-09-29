"""S-12: 抄録ふるいの補い（decisions.md 判断 2）。

abstract_filter.py で <meta name="abstract"> が無かった記録（fetch = no-abstract-meta）について、
論文ページの本文側の抄録の枠（article-overiew-abstract-wrap）から抄録を取り、同じ 2 つの正規表現を当てる。
★ 抄録そのものは repo の外にだけ書く。

使い方: python abstract_filter_body.py <abstract_filter の結果 JSON> <出力 JSON> <抄録の保存先（repo の外）>
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search_ja import AI_EN_RE, AI_RE, FT_RE, UA  # noqa: E402


def body_abstract(page):
    i = page.find("article-overiew-abstract-wrap")
    if i < 0:
        return ""
    seg = page[i:i + 6000]
    j = seg.find('id="author-information-wrap"')
    seg = seg[: j if j > 0 else len(seg)]
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", seg))).strip()


def main(src, out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    os.makedirs(abs_dir, exist_ok=True)
    d = json.load(open(src, encoding="utf-8"))
    results, saved = [], {}
    for r in d["results"]:
        if r["fetch"] != "no-abstract-meta":
            continue
        page = urllib.request.urlopen(urllib.request.Request(r["url"], headers=UA), timeout=90).read().decode("utf-8", "replace")
        ab = body_abstract(page)
        saved[r["url"]] = ab
        ai = sorted({x.group(0) for x in AI_RE.finditer(ab)} | {x.group(0).lower() for x in AI_EN_RE.finditer(ab)})
        ft = sorted({x.group(0).lower() for x in FT_RE.finditer(ab)})
        results.append({k: r[k] for k in ("url", "title", "year", "journal", "queries")}
                       | {"fetch": "body" if ab else "no-abstract", "ai_terms": ai, "fatigue_terms": ft,
                          "abstract_filter": bool(ai and ft)})
        print(r["title"][:60], bool(ai and ft), ai, ft, flush=True)
        time.sleep(1)
    with open(os.path.join(abs_dir, "s12_abstracts_body.json"), "w", encoding="utf-8") as fh:
        json.dump(saved, fh, ensure_ascii=False, indent=1)
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §1.4・判断 2"},
                   "results": results}, fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:4])
