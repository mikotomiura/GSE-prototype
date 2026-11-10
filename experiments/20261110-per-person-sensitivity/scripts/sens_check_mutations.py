"""変異の結果を確かめて selftest.json にまとめる（conditions.md V1）。

使い方: python3 -I sens_check_mutations.py <mutations_dir> <selftest.json> <run_id>
各変異: 出力がある・run_id が今回のもの・mutate 欄が名前どおり・終了コードが 3・名指しの対照が passed = false。
返り値: 0 = すべての変異が名指しの対照を赤にした、3 = 当たらない変異がある。
"""
import json
import os
import sys

NAMED = {"v1": ["P-DIFF"], "v2": ["P-PLANT0"], "v3": ["P-JOINTW"], "v4": ["P-GROUP"], "v5": ["P-SPLIT"]}


def check(d, m, ctls, run_id):
    p, pe = os.path.join(d, m + ".json"), os.path.join(d, m + ".exit")
    if not (os.path.exists(p) and os.path.exists(pe)):
        return dict(hit=False, note="出力か終了コードが無い")
    code = int(open(pe).read().strip())
    j = json.load(open(p))
    r = dict(exit=code, run_id_ok=j.get("run_id") == run_id, mutate_ok=j.get("mutate") == [m],
             controls={c: j.get(c, {}).get("passed") for c in ctls})
    r["hit"] = r["run_id_ok"] and r["mutate_ok"] and code == 3 and all(v is False for v in r["controls"].values())
    return r


def main():
    d, st, run_id = sys.argv[1:4]
    res = {m: check(d, m, c, run_id) for m, c in NAMED.items()}
    S = json.load(open(st))
    S["mutations"] = res
    json.dump(S, open(st, "w"), indent=1)
    print(json.dumps({m: r["hit"] for m, r in res.items()}))
    return 0 if all(r["hit"] for r in res.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
