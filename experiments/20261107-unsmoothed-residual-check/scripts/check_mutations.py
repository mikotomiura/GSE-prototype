"""変異の結果を確かめて selftest.json にまとめる（tau-extend と同じ門・今回は conditions V2 の m41〜m51）。

使い方: python3 -I check_mutations.py <mutations_dir> <selftest.json> <run_id>
各変異について、すべてを確かめる: 出力がある・run_id が今回のもの・mutate 欄が名前どおり・終了コードが 3（対照の赤。
落ちた・例外・変異が当たらないは 1 などの別の値）・名指しの対照がすべて passed = false。
返り値: 0 = すべての変異が名指しの対照を赤にした、3 = 当たらない変異がある。
"""
import json
import os
import sys

NAMED = {"m41": ["P-RAW"], "m42": ["P-U"], "m43": ["P-THIN"], "m44": ["P-THIN"], "m45": ["P-RES-CAL"], "m46": ["P-RES-CAL"],
         "m47": ["P-RES-MIS"], "m48": ["P-CRN"], "m49": ["P-NPZ"], "m50": ["P-SAME"], "m51": ["P-PIN"]}


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
