"""P-REPRO（conditions V1）: 今回の summary.json のうち、前の試験（experiments/20261104-timeseries-tau-extend/）の
summary.json にある葉をすべて辿り、前の試験と一致するかを機械で照らす。

比べ方: 前の側の鍵だけを辿る（今回足した行・相手・人数の欄は見ない）。数（float）は相対 1e-9、整数・文字列・真偽・None は
一致、リストは長さが同じで要素ごと。照らさない鍵: ci・ci_method（相手が増え区間の乱数の位置がずれる）・seconds・run_id。
出力は照らした数・外れた数・最大の差・外れた節の名前（データ / 一番上の鍵 の 2 層だけ・パネルより下は書かない）。

使い方:
  python3 -I repro_check.py <今回の summary.json> <前の試験の summary.json> <out.json>
  python3 -I repro_check.py --selftest
返り値: 0 = すべて一致、3 = 外れた葉がある（または照らす葉が 0）。HP Z2 で回す門（Mac では版が違うので照らさない）。
"""
import copy
import json
import math
import sys

SKIP = {"ci", "ci_method", "seconds", "run_id"}
REL = 1e-9


def rel_diff(a, b):
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b))


def walk(old, new, path, acc):
    """old の葉ごとに new と比べる。acc: dict(cells, bad, worst, sections)。"""
    if isinstance(old, dict):
        for k, v in old.items():
            if k in SKIP:
                continue
            if not isinstance(new, dict) or k not in new:
                miss(v, path + [k], acc)
                continue
            walk(v, new[k], path + [k], acc)
        return
    if isinstance(old, list):
        if not isinstance(new, list) or len(new) != len(old):
            miss(old, path, acc)
            return
        for i, (a, b) in enumerate(zip(old, new)):
            walk(a, b, path + [str(i)], acc)
        return
    acc["cells"] += 1
    if isinstance(old, float) and isinstance(new, (int, float)) and not isinstance(new, bool):
        if not (math.isfinite(old) and math.isfinite(float(new))):  # inf/inf の比は NaN で「一致」に数えられてしまう
            if old != float(new):
                acc["worst"] = float("inf")
                bad(path, acc)
            return
        d = rel_diff(old, float(new))
        acc["worst"] = max(acc["worst"], d)
        if d > REL:
            bad(path, acc)
        return
    if type(old) is not type(new) or old != new:
        acc["worst"] = float("inf")
        bad(path, acc)


def miss(old, path, acc):
    """new に無い部分: その下の葉の数だけ外れとして数える。"""
    n = count_leaves(old)
    acc["cells"] += n
    acc["bad"] += n
    acc["worst"] = float("inf")
    acc["sections"].add("/".join(path[:2]))


def bad(path, acc):
    acc["bad"] += 1
    acc["sections"].add("/".join(path[:2]))


def count_leaves(x):
    if isinstance(x, dict):
        return sum(count_leaves(v) for k, v in x.items() if k not in SKIP)
    if isinstance(x, list):
        return sum(count_leaves(v) for v in x)
    return 1


def compare(new, old):
    acc = dict(cells=0, bad=0, worst=0.0, sections=set())
    walk(old.get("datasets", {}), new.get("datasets", {}), [], acc)
    return dict(cells=acc["cells"], mismatched=acc["bad"], max_rel_diff=acc["worst"], tolerance_rel=REL,
                mismatched_sections=sorted(acc["sections"]))


def selftest():
    """測定器の対照: 同じものは 0 件・数を相対 1e-6 ずらすと 1 件・葉を消すと 1 件・区間と時間と run_id を変えても 0 件・
    今回だけの鍵を足しても 0 件・伏せの人数違いで 1 件・数が文字列 "+inf" になると 1 件・選ばれた人数の違いで 1 件・
    診断の文字列の違いで 1 件（節の名前も確かめる）。"""
    def cell(x):
        return dict(median=x, q25=x - 1, q75=x + 1, better_share=0.5, n=10, ci=[0, 1])

    def summ():
        st = {s: {r: {"all/self_minus_" + o: cell(0.1 * (i + 1)) for o in ("r1", "pool_same")}
                  for i, r in enumerate(("tau_0", "tau_inf", "tau_other"))} for s in ("hmm3", "ar1")}
        st["ar1"]["chosen_tau_other"] = {"inf": 7, "1000000": 3}
        em = {"P15": {"1": dict(writers=10, structs=st, n_train=dict(median=500.0, q25=400.0, q75=600.0, n=10))}}
        return dict(run_id="x", datasets={"coauthor": dict(em=em, seconds=dict(pools=1.0), writers_total=12,
                                                           pool_full_diag={"ar1": dict(winner="rand1", gap12=0.5)})})
    a = summ()
    r0 = compare(a, summ())
    ok = r0["mismatched"] == 0 and r0["cells"] == count_leaves(a["datasets"]) == 70  # 区間（ci）と seconds は数えない
    b = summ()
    b["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_r1"]["median"] *= 1 + 1e-6
    rb = compare(b, a)
    ok = ok and rb["mismatched"] == 1 and rb["mismatched_sections"] == ["coauthor/em"]
    c = summ()
    del c["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["hmm3"]["tau_inf"]["all/self_minus_pool_same"]["q75"]
    ok = ok and compare(c, a)["mismatched"] == 1
    d = summ()
    d["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["hmm3"]["tau_0"]["all/self_minus_r1"]["ci"] = [5, 6]
    d["datasets"]["coauthor"]["seconds"]["pools"] = 99.0
    d["run_id"] = "y"
    ok = ok and compare(d, a)["mismatched"] == 0
    e = summ()
    e["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_mode"] = {"all/self_minus_r1": cell(9.0)}
    e["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_mode_same"] = cell(9.0)
    ok = ok and compare(e, a)["mismatched"] == 0
    f, g = summ(), summ()
    f["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_r1"] = dict(n=4, suppressed=True)
    g["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_r1"] = dict(n=5, suppressed=True)
    ok = ok and compare(f, g)["mismatched"] == 1
    h = summ()
    h["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_r1"]["median"] = "+inf"
    ok = ok and compare(h, a)["mismatched"] == 1
    i = copy.deepcopy(a)
    i["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["chosen_tau_other"]["inf"] = 8
    ok = ok and compare(i, a)["mismatched"] == 1
    j = summ()
    j["datasets"]["coauthor"]["pool_full_diag"]["ar1"]["winner"] = "rand2"
    rj = compare(j, a)
    ok = ok and rj["mismatched"] == 1 and rj["mismatched_sections"] == ["coauthor/pool_full_diag"]
    print(json.dumps(dict(repro_check_selftest=ok)))
    return 0 if ok else 3


def main(argv):
    if argv[0] == "--selftest":
        return selftest()
    new, old = json.load(open(argv[0], encoding="utf-8")), json.load(open(argv[1], encoding="utf-8"))
    r = compare(new, old)
    r["passed"] = r["cells"] > 0 and r["mismatched"] == 0
    json.dump(r, open(argv[2], "w"), indent=1)
    print(json.dumps(r))
    return 0 if r["passed"] else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
