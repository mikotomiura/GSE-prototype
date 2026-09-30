"""検索式の開発 v0 の集計（★ 2026-10-01 の code-reviewer MEDIUM・decisions.md 判断 17）。

search-dev.md の §1・§4・§5 の数（5 本の和・b1 が足す数・V2 が除いた数・259 件との突き合わせ・雑音の見積もりの機械の数）を、
取得した ID の一覧（repo の外）と雑音の見積もりの題名（repo の外）から数え直し、件数と一覧の SHA-256 だけを JSON に書く。
ネットワークに出ない。題名・ID の一覧そのものは書かない。

使い方（このディレクトリで）:
  python search_dev_summary.py --store <ID の一覧の dir> --noise <雑音の見積もりの JSON の dir> --out search_dev_summary_v0_2026-10-01.json
"""
import argparse
import collections
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search_dev as S  # noqa: E402

MAIN = [("epmc", "main"), ("s2", "main"), ("eric", "main"), ("arxiv", "main"), ("zenodo", "main")]


def group_of(key):
    """259 件の鍵を候補の出どころの群に分ける（search-dev.md §4 の表の行）。"""
    if key.startswith("AF"):
        return "DB"
    prefix, num = key.split("-")
    if prefix == "S04" and 41 <= int(num) <= 87:
        return "S04 作業負荷・時間の比較（S04-41〜S04-87）"
    if prefix in ("S08", "S15"):
        return "S08・S15"
    if prefix == "S04":
        return "S04 のほか"
    return prefix


def term_re(terms):
    alt = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    return re.compile(r"(?<![A-Za-z0-9])(" + alt + r")(?![A-Za-z0-9])", re.I)


def sha(items):
    return hashlib.sha256("\n".join(sorted(items)).encode("utf-8")).hexdigest()


def load_store(store):
    ids = {}
    for fn in sorted(os.listdir(store)):
        if fn.startswith("ids_") and fn.endswith(".json"):
            d = json.load(open(os.path.join(store, fn), encoding="utf-8"))
            ids[(d["source"], d["name"])] = {tuple(x) for x in d["ids"]}
    return ids


def dois(s):
    return {x[1] for x in s if x[0] == "doi"}


def summarize(ids, recs259, noise, version="v0"):
    runs = [dict(source=s, name=n, n_ids=len(v), n_doi=len(dois(v)), n_non_doi=len(v) - len(dois(v)))
            for (s, n), v in sorted(ids.items())]
    union = set()
    non_doi = 0
    for k in MAIN:
        union |= dois(ids[k])
        non_doi += sum(1 for x in ids[k] if x[0] != "doi")
    b1 = dois(ids[("epmc", "b1")]) | dois(ids[("s2", "b1")])
    d259 = {S.norm_doi(r["doi"]): r["key"] for r in recs259 if r.get("doi")}
    per_source = {k[0]: len(set(d259) & dois(ids[k])) for k in MAIN}
    groups = collections.OrderedDict()
    for r in recs259:
        g = group_of(r["key"])
        tot, miss = groups.get(g, (0, 0))
        hit = bool(r.get("doi")) and S.norm_doi(r["doi"]) in union
        groups[g] = (tot + 1, miss + (0 if hit else 1))
    v = S.VERSIONS[version]
    a_re, f_re = term_re(v["A"]), term_re(v["F"])
    nz = {}
    for src, d in sorted(noise.items()):
        t = [x["title"] for x in d["titles"]]
        nz[src] = dict(n=d["n"], population=d["n_doi_population"], sample_sha256=d["sample_sha256"],
                       titles=sum(1 for x in t if x), a_in_title=sum(1 for x in t if a_re.search(x)),
                       f_in_title=sum(1 for x in t if f_re.search(x)),
                       both=sum(1 for x in t if a_re.search(x) and f_re.search(x)))
    return dict(version=version, runs=runs,
                main_union=dict(n_doi=len(union), doi_sha256=sha(union), n_non_doi_not_deduplicated=non_doi),
                b1_doi=len(b1), b1_not_in_main=len(b1 - union),
                s2_main_minus_v2=len(dois(ids[("s2", "main")]) - dois(ids[("s2", "main_v2")])),
                overlap_259=dict(n=len(recs259), with_doi=len(d259), without_doi=len(recs259) - len(d259),
                                 in_main_union=len(set(d259) & union), per_source=per_source,
                                 groups={g: dict(total=a, not_in_union=b) for g, (a, b) in groups.items()}),
                noise=nz)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--noise", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    import dedup as D
    ids = load_store(a.store)
    noise = {src: json.load(open(os.path.join(a.noise, f"noise_{src}_main.json"), encoding="utf-8")) for src in ("epmc", "s2")}
    out = summarize(ids, D.load_259(), noise)
    out["executed"] = S.now()
    S.write_json(a.out, out)
    print(json.dumps({k: out[k] for k in ("main_union", "b1_not_in_main", "s2_main_minus_v2")}, ensure_ascii=False))
    print(json.dumps(out["overlap_259"], ensure_ascii=False))
    print(json.dumps(out["noise"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
