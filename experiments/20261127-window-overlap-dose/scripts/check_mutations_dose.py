"""変異の結果を確かめて selftest.json にまとめる（S13 と同じ門・conditions V2 の m61〜m83）。

使い方: python3 -I check_mutations_dose.py <mutations_dir> <selftest.json> <run_id>
各変異について、すべてを確かめる: 出力がある・run_id が今回のもの・mutate 欄が名前どおり・終了コードが 3（対照の赤。
落ちた・例外・変異が当たらないは 1 などの別の値）・名指しの対照がすべて passed = false。
返り値: 0 = すべての変異が名指しの対照を赤にした、3 = 当たらない変異がある。
"""
import json
import os
import sys

NAMED = {"m61": ["P-STRIDE"], "m62": ["P-STRIDE"], "m63": ["P-PHASE"], "m64": ["P-PHASE"], "m65": ["P-MI"], "m66": ["P-MI"],
         "m67": ["P-FIRST"], "m68": ["P-SWAP"], "m69": ["P-READ"], "m70": ["P-BLOCK"], "m71": ["P-BLOCK"], "m72": ["P-DS"],
         "m74": ["P-PAIR"], "m75": ["P-READ"], "m76": ["P-TIME"], "m77": ["P-MI"], "m79": ["P-READ"], "m80": ["P-MI"],
         "m81": ["P-PAIR"], "m82": ["P-READ"], "m83": ["P-READ"]}


def check(d, m, ctls, run_id):
    p, pe = os.path.join(d, m + ".json"), os.path.join(d, m + ".exit")
    if not (os.path.exists(p) and os.path.exists(pe)):
        return dict(hit=False, note="出力か終了コードが無い")
    code = int(open(pe).read().strip())
    j = json.load(open(p, encoding="utf-8"))
    r = dict(exit=code, run_id_ok=j.get("run_id") == run_id, mutate_ok=j.get("mutate") == [m],
             controls={c: j.get(c, {}).get("passed") for c in ctls})
    r["hit"] = r["run_id_ok"] and r["mutate_ok"] and code == 3 and all(v is False for v in r["controls"].values())
    return r


def main():
    d, st, run_id = sys.argv[1:4]
    res = {m: check(d, m, c, run_id) for m, c in NAMED.items()}
    S = json.load(open(st, encoding="utf-8"))
    S["mutations"] = res
    json.dump(S, open(st, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps({m: r["hit"] for m, r in res.items()}))
    return 0 if all(r["hit"] for r in res.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
