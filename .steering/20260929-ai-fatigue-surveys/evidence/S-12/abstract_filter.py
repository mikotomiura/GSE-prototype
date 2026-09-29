"""S-12: 抄録ふるい（design.md §1.4）。

J-STAGE の抄録の欄で当たり、題名ふるいを通らなかった記録について、論文ページの <meta name="abstract"> を取り、
題名ふるいと同じ 2 つの正規表現を当てる。★ 抄録そのものは repo の外（第 3 引数のディレクトリ）にだけ書く。
repo に書くのは、当たった語（正規表現の一致部分）と通過の真偽だけ。

使い方: python abstract_filter.py <search_ja の結果 JSON> <出力 JSON> <抄録の保存先（repo の外）>
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

META = re.compile(r'<meta name="abstract" content="([^"]*)"')


def main(src, out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    if os.path.abspath(abs_dir).startswith(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))):
        sys.exit("抄録の保存先が repo の中にある（repo の外を指定する）")
    os.makedirs(abs_dir, exist_ok=True)
    d = json.load(open(src, encoding="utf-8"))
    targets = {}
    for run in d["runs"]:
        if run["source"] != "J-STAGE" or run["field"] != "abst":
            continue
        for r in run["records"]:
            if r["title_filter"] or not r.get("url"):
                continue
            t = targets.setdefault(r["url"], {"url": r["url"], "title": r["title_ja"] or r["title_en"],
                                               "year": r["year"], "journal": r["journal"], "queries": []})
            t["queries"].append(run["query"])
    results, saved = [], {}
    for i, (url, t) in enumerate(sorted(targets.items())):
        try:
            page = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode("utf-8", "replace")
            m = META.search(page)
            ab = html.unescape(m.group(1)) if m else ""
            status = "ok" if m else "no-abstract-meta"
        except Exception as e:  # noqa: BLE001
            ab, status = "", f"ERR {e}"
        saved[url] = ab
        ai = sorted({x.group(0) for x in AI_RE.finditer(ab)} | {x.group(0).lower() for x in AI_EN_RE.finditer(ab)})
        ft = sorted({x.group(0).lower() for x in FT_RE.finditer(ab)})
        results.append({**t, "fetch": status, "ai_terms": ai, "fatigue_terms": ft,
                        "abstract_filter": bool(ai and ft)})
        print(i, status, bool(ai and ft), t["title"][:60], ai, ft, flush=True)
        time.sleep(1)
    with open(os.path.join(abs_dir, "s12_abstracts.json"), "w", encoding="utf-8") as fh:
        json.dump(saved, fh, ensure_ascii=False, indent=1)
    meta = {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §1.4",
            "note": "抄録は repo の外に保存。ここには一致した語と通過の真偽だけ。"}
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": meta, "results": results}, fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:4])
