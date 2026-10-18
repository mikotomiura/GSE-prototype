#!/usr/bin/env python3
"""探索役が書いた要約を検査して docs/literature/refdb/summaries.json に足す。

    python3 scripts/refdb/merge_summaries.py NEW.json --input missing_summaries.json [--write]

検査（2026-10-18 にメインが手で行ったもの）:
  - 形: summary・features・basis がそろい、basis が 抄録 / 接地のみ / 題のみ のどれか
  - 件数と key: 入力の key と同じ集合か（足りない・余る・既にある key）
  - 写し: 抄録と連続 15 語以上が重なっていないか（英語の語で数える）
  - 数値: 要約と特徴の数値が入力（抄録・接地・題・出典）にあるか。無いものは目で確かめる一覧に出す

--write を付けないときは検査だけ。重なりか形の誤りがあれば書かずに終了コード 1。
数値の一覧は止めない（「N = 290」を「290 人」と書くなど、正しい言い換えがあるため）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SUMMARIES = REPO / "docs" / "literature" / "refdb" / "summaries.json"
BASES = {"抄録", "接地のみ", "題のみ"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")
NGRAM = 15


def ngrams(text: str, n: int = NGRAM) -> set[tuple[str, ...]]:
    w = [x.lower() for x in WORD_RE.findall(text)]
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def numbers(text: str) -> set[str]:
    return {x.replace(",", "") for x in NUM_RE.findall(text)}


def check(new: dict, inputs: list[dict], existing: dict) -> dict:
    by_key = {x["key"]: x for x in inputs}
    errors, unverified = [], []
    missing = sorted(set(by_key) - set(new))
    extra = sorted(set(new) - set(by_key))
    if missing:
        errors.append(f"返っていない key: {missing}")
    if extra:
        errors.append(f"入力に無い key: {extra}")
    for k, v in new.items():
        if k in existing:
            errors.append(f"{k}: 既に summaries.json にある")
        if not isinstance(v, dict) or not all(isinstance(v.get(f), str) and v.get(f) for f in ("summary", "features", "basis")):
            errors.append(f"{k}: summary・features・basis がそろっていない")
            continue
        if v["basis"] not in BASES:
            errors.append(f"{k}: basis が {v['basis']!r}")
        src = by_key.get(k, {})
        abstract = src.get("abstract", "")
        if abstract and ngrams(v["summary"] + " " + v["features"]) & ngrams(abstract):
            errors.append(f"{k}: 抄録と連続 {NGRAM} 語以上が重なる")
        material = " ".join(src.get(f, "") for f in ("abstract", "gse_note", "title", "venue"))
        stray = sorted(numbers(v["summary"] + " " + v["features"]) - numbers(material))
        if stray:
            unverified.append({"key": k, "numbers": stray, "features": v["features"]})
    return {"errors": errors, "unverified_numbers": unverified}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("new", help="探索役が返した JSON（key → {summary, features, basis}）")
    p.add_argument("--input", required=True, help="束の入力（missing_summaries.json かその一部）")
    p.add_argument("--summaries", default=str(SUMMARIES))
    p.add_argument("--by", default="Claude Sonnet（抄録または接地の文から）・数値はメインが機械照合")
    p.add_argument("--write", action="store_true", help="検査が通れば summaries.json に足す")
    a = p.parse_args(argv)
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    inputs = json.loads(Path(a.input).read_text(encoding="utf-8"))
    spath = Path(a.summaries)
    existing = json.loads(spath.read_text(encoding="utf-8")) if spath.exists() else {}
    res = check(new, inputs, existing)
    for e in res["errors"]:
        print("誤り: " + e, file=sys.stderr)
    for u in res["unverified_numbers"]:
        print(f"数値を目で確かめる: {u['key']} {u['numbers']} ｜ {u['features']}")
    print(f"{len(new)} 件・誤り {len(res['errors'])}・数値を確かめる {len(res['unverified_numbers'])}")
    if res["errors"]:
        return 1
    if a.write:
        today = dt.date.today().isoformat()
        for k, v in new.items():
            existing[k] = {"summary": v["summary"], "features": v["features"], "basis": v["basis"],
                           "written": today, "by": a.by}
        spath.write_text(json.dumps(dict(sorted(existing.items())), ensure_ascii=False, indent=1),
                         encoding="utf-8")
        print(f"summaries.json に {len(new)} 件を足した（計 {len(existing)} 件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
