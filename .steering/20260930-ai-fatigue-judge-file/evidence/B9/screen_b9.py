"""B9（Nobles 2026・Zenodo の再現パッケージ）の採択 32 件のうち、DB と追加候補に無い 28 件のふるい（decisions.md 判断 15）。

★ 手順: 28 件の題名と抄録（OpenAlex の /works/doi:）に、S-15 の 0 段目の 3 群（依存・疲労・AI）のうち AI と疲労の 2 群を当てる
  （search_round.py から import）。⚠️ 0 段目の定義（3 群すべて）どおりではない。出力の `stage0` は「2 群がどちらも当たった」の意味。
  ⚠️ 結果を見る前に固定した手順ではない（2026-09-30 に、突き合わせの結果を見てから、既存の 0 段目の語群をそのまま当てた）。
書誌だけを repo の JSON に書き、抄録は repo の外（第 2 引数のディレクトリ）にだけ書く（common.write_pair で対にする）。
連絡先（メールアドレス）は送らない。

使い方: python screen_b9.py <書誌の出力 JSON（repo の中）> <抄録の置き場（repo の外のディレクトリ）>
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import search_round as SR  # noqa: E402  語群と common（repo の外・対の書き出し・URL の柵）を同じものにする

common = SR.common
ALLOWED = ["https://api.openalex.org/works/"]
OPENER = common.guarded_opener(ALLOWED)
GROUPS = {"AI": SR.AI_RE, "疲労": SR.SURVEYS["S-15"]["groups"]["疲労"]}

# 採択 32 件（原稿の文献一覧）から、DB の 3 件（AF006 10.26803/ijlter.25.3.29・AF007 10.26803/ijlter.25.5.5・
# AF008 10.11591/ijai.v15.i2.pp1963-1971）と S-02 #2 の 1 件（10.1038/s41598-026-45402-7）を除いた 28 件の DOI（方法の文献 5 件は採択に入らない）
# ⚠️ 取得の失敗は例外のクラス名だけを記録する（2026-09-30 の実行では 28 件とも ok）
DOIS = [
    "10.26803/ijlter.23.11.22", "10.1016/j.heliyon.2024.e40025", "10.47604/ajikm.2735", "10.70670/sra.v4i1.1983",
    "10.1080/10494820.2025.2492785", "10.1038/s41598-025-19851-5", "10.52783/jisem.v10i19s.3052", "10.5281/zenodo.3878572",
    "10.1007/s43681-025-00688-7", "10.7176/JEP/11-18-02", "10.36922/AIH025180038", "10.48550/arXiv.2402.08143",
    "10.3389/feduc.2025.1548104", "10.52206/jsmc.2024.14.4.957", "10.3389/fpsyg.2025.1498132", "10.3389/fpsyg.2026.1795301",
    "10.1109/EMR.2024.3394540", "10.1177/03400352241301780", "10.1109/SESAI61023.2024.10599402", "10.1080/2331186X.2024.2386892",
    "10.1016/S2468-2667(25)00036-2", "10.47772/IJRISS.2025.908000051", "10.47772/IJRISS.2025.90300209", "10.15575/join.v10i1.1549",
    "10.55056/cte.616", "10.17573/cepar.2024.1.05", "10.30773/pi.2026.0068", "10.3390/jrfm18040217",
]


def fetch(doi):
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi.lower(), safe="/:;()._-")
    if not common.allowed_url(url, ALLOWED):
        raise ValueError(f"許していない URL: {url}")
    with OPENER.open(urllib.request.Request(url, headers=SR.UA), timeout=60) as r:
        return json.loads(r.read())


def main(bib_path, abs_dir):
    common.ensure_outside_repo(abs_dir)
    recs, abstracts = [], {}
    for doi in DOIS:
        try:
            w = fetch(doi)
        except Exception as e:  # noqa: BLE001  取れなかったことを記録に残す
            recs.append({"doi": doi, "status": f"ERR {type(e).__name__}"})
            continue
        inv = w.get("abstract_inverted_index") or {}
        ab = " ".join(t for _, t in sorted((p, t) for t, ps in inv.items() for p in ps))
        title = w.get("title") or ""
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        hit = {g: bool(re.search(p, f"{title} {ab}")) for g, p in GROUPS.items()}
        recs.append({"doi": doi, "status": "ok", "title": title, "year": w.get("publication_year"), "journal": src,
                     "type": w.get("type"), "has_abstract": bool(ab), "hit": hit, "stage0": all(hit.values())})
        if ab:
            abstracts[doi] = ab
        time.sleep(0.3)
    bib = {"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "source": "OpenAlex /works/doi:（題名・年・掲載誌・抄録）",
                    "groups": GROUPS, "note": "抄録はこの JSON に持たない（repo の外に対で書いた）"},
           "runs": [{"id": "B9", "records": recs}]}
    common.write_pair(bib_path, os.path.join(abs_dir, os.path.basename(bib_path).replace(".json", "_abstracts.json")), bib, abstracts)
    n = sum(r.get("stage0", False) for r in recs)
    print(len(recs), "件・2 群（AI・疲労）の両方に当たった", n, "件・取得の失敗", sum(r["status"] != "ok" for r in recs), "件")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
