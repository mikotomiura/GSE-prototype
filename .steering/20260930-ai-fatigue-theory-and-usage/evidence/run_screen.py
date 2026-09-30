"""取得した抄録に screen.py のふるいを当てる（design.md §1.2・§1.3・§2.3）。

書誌だけの結果（鍵・当たった語の文字列・記号）を repo の JSON に書き、メインが読む束（抄録の全文と印）は repo の外にだけ書く。

使い方（本ファイルのディレクトリで実行する）:
  python run_screen.py <書誌の JSON（fetch_abstracts.py の records の出力）> <抄録の置き場（repo の外）>
                       <S-11 の結果 JSON（repo の中）> <S-09 の結果 JSON（repo の中）> <読む束の出力ディレクトリ（repo の外）>
"""
import collections
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_abstracts as F  # noqa: E402
import screen as S  # noqa: E402

common = F.common


def load_pair(bib_path, abs_dir):
    bib = json.load(open(bib_path, encoding="utf-8"))
    abs_path = os.path.join(abs_dir, os.path.basename(bib_path).replace(".json", "_abs.json"))
    ab = json.load(open(abs_path, encoding="utf-8"))
    if not common.same_run(bib, ab):
        raise SystemExit("書誌と抄録が同じ実行の対でない（run_id が違う）")
    return bib, ab["abstracts"]


def main():
    bib_path, abs_dir, out11, out09, pack_dir = sys.argv[1:6]
    common.ensure_outside_repo(abs_dir)
    common.ensure_outside_repo(pack_dir)
    bib, abstracts = load_pair(bib_path, abs_dir)
    executed = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    rows11, rows09, pack = [], [], []
    for rec in bib["records"]:
        key, title = rec["key"], rec["title"]
        text = abstracts.get(key) or ""
        both = title + " . " + text
        th, gh, fh = S.terms(both), S.general(both), S.frameworks(both)
        in_title = S.terms(title)
        rows11.append({"key": key, "has_text": bool(text), "terms": th, "terms_in_title": sorted(in_title),
                       "uses_term": S.uses_term(th), "general": sorted(gh)})
        rows09.append({"key": key, "has_text": bool(text), "frameworks": fh})
        if S.uses_term(th):
            cues = S.cue_sentences(text)
            sents = S.sentences(text)
            lines = [f"## {key}  {title}", f"- DOI: {rec.get('doi')}  OA: {rec.get('oa_status', '')} {rec.get('oa_url', '')}",
                     f"- 語形: {th}", ""]
            for i, s in enumerate(sents):
                mark = ""
                for j, cue in cues:
                    if j == i:
                        mark = "【語・手がかりあり】" if cue else "【語】"
                lines.append(f"{i}. {mark}{s}")
            pack.append("\n".join(lines) + "\n")
    n_use = sum(r["uses_term"] for r in rows11)
    c_terms = collections.Counter(k for r in rows11 for k in r["terms"])
    c_gen_use = collections.Counter(g for r in rows11 if r["uses_term"] for g in r["general"])
    c_gen_not = collections.Counter(g for r in rows11 if not r["uses_term"] for g in r["general"])
    c_fw = collections.Counter(k for r in rows09 for k in r["frameworks"])
    meta = {"executed": executed, "input": os.path.basename(bib_path), "input_run_id": bib.get("run_id"), "n": len(rows11)}
    with common.open_exclusive(out11) as fh:
        json.dump({**meta, "n_uses_term": n_use, "count_terms": dict(c_terms), "count_general_uses_term": dict(c_gen_use),
                   "count_general_not_uses_term": dict(c_gen_not), "records": rows11}, fh, ensure_ascii=False, indent=1)
    with common.open_exclusive(out09) as fh:
        json.dump({**meta, "count_frameworks": dict(c_fw), "records": rows09}, fh, ensure_ascii=False, indent=1)
    os.makedirs(pack_dir, exist_ok=True)
    with common.open_exclusive(os.path.join(pack_dir, "s11_pack.md")) as fh:
        fh.write("\n".join(pack))
    print(f"259 件中 語を使う記録 {n_use} 件・語形 {dict(c_terms)}")
    print(f"一般の語（語を使う記録）{dict(c_gen_use)}")
    print(f"一般の語（それ以外）{dict(c_gen_not)}")
    print(f"枠組み {dict(c_fw.most_common())}")


if __name__ == "__main__":
    main()
