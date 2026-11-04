"""P-REPRO（conditions V1）: 今回の summary.json のうち前回と重なるセルが、前回の summary.json と相対 1e-9 で一致するかを機械で照らす。

重なるセル: データ × パネル × k × 構造 ∈ {hmm3, ar1, ar2, ar3} × 行 ∈ {τ = 0, 100, 1,000, 10,000 の固定}
× 相手 ∈ {r1, 同じ構造の共通, K = 3 の共通, F-b} × {全記号, 押下のある記号} の中央値・四分位・良い側の割合・人数
（伏せたセルは人数と伏せの印）。区間（ci）は照らさない（行の数が変わり乱数の流れが違う・D5）。
出力は外れたセルの数と最大の差だけ（どのセルかは書かない）。

使い方:
  python3 -I repro_check.py <今回の summary.json> <前回の summary.json> <out.json>
  python3 -I repro_check.py --selftest
返り値: 0 = すべて一致、3 = 外れたセルがある（または照らすセルが 0）。
HP Z2 で回す門（Mac では版が違うので照らさない・引き継ぎ）。
"""
import json
import sys

STRUCTS = ["hmm3", "ar1", "ar2", "ar3"]
ROWS = ["tau_0", "tau_100", "tau_1000", "tau_10000"]
OPPS = ["r1", "pool_same", "pool_hmm3", "fb"]
LABS = ["all", "pressed"]
FIELDS = ["median", "q25", "q75", "better_share", "n"]
REL = 1e-9


def rel_diff(a, b):
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b))


def compare(new, old):
    """返り値: dict(cells, mismatched, max_rel_diff)。"""
    cells, bad, worst = 0, 0, 0.0
    for ds, Dold in old["datasets"].items():
        Dnew = new["datasets"].get(ds, {}).get("em", {})
        for pn, Pold in Dold["em"].items():
            for k, Eold in Pold.items():
                for s in STRUCTS:
                    for r in ROWS:
                        for lab in LABS:
                            for o in OPPS:
                                key = lab + "/self_minus_" + o
                                a = Eold["structs"][s][r][key]
                                try:
                                    b = Dnew[pn][k]["structs"][s][r][key]
                                except (KeyError, TypeError):
                                    b = "missing"
                                cells += 1
                                if a is None or b is None or b == "missing":
                                    if a != b:
                                        bad += 1
                                        worst = float("inf")
                                    continue
                                if a.get("suppressed") or b.get("suppressed"):
                                    if (a.get("suppressed"), a.get("n")) != (b.get("suppressed"), b.get("n")):
                                        bad += 1
                                        worst = float("inf")
                                    continue
                                d = max(rel_diff(a[f], b[f]) for f in FIELDS)
                                worst = max(worst, d)
                                if d > REL:
                                    bad += 1
    return dict(cells=cells, mismatched=bad, max_rel_diff=worst, tolerance_rel=REL)


def selftest():
    """測定器の対照: 同じものは 0 件・1 セルを相対 1e-6 ずらすと 1 件・1 セルを消すと 1 件・伏せの人数違いで 1 件。"""
    def cell(x):
        return dict(median=x, q25=x - 1, q75=x + 1, better_share=0.5, n=10, ci=[0, 1])

    def summ():
        st = {s: {r: {l + "/self_minus_" + o: cell(0.1 * (i + 1)) for l in LABS for o in OPPS}
                  for i, r in enumerate(ROWS + ["tau_inf"])} for s in STRUCTS}
        return dict(datasets={"coauthor": dict(em={"P15": {"1": dict(structs=st)}})})
    a = summ()
    ok = compare(a, summ())["mismatched"] == 0
    b = summ()
    b["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar2"]["tau_100"]["all/self_minus_r1"]["median"] *= 1 + 1e-6
    ok = ok and compare(b, a)["mismatched"] == 1
    c = summ()
    del c["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar3"]["tau_0"]["pressed/self_minus_fb"]
    ok = ok and compare(c, a)["mismatched"] == 1
    d = summ()
    d["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["hmm3"]["tau_0"]["all/self_minus_fb"]["ci"] = [5, 6]
    ok = ok and compare(d, a)["mismatched"] == 0  # 区間は照らさない
    e, f = summ(), summ()
    e["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_r1"] = dict(n=4, suppressed=True)
    f["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["ar1"]["tau_0"]["all/self_minus_r1"] = dict(n=5, suppressed=True)
    ok = ok and compare(e, f)["mismatched"] == 1
    ok = ok and compare(a, a)["cells"] == len(STRUCTS) * len(ROWS) * len(LABS) * len(OPPS)
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
