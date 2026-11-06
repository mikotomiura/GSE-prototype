"""P-REPRO（conditions V1）: o の列の集計が tau-extend の summary.json と一致するかを機械で照らす（HP Z2）。

照らす葉: tau-extend の summary にある、P15 の k = 1・5・15 と C5 の k = 1・5 の
- 4 構造 × 行（τ 固定の 9 行・τ 他人）× 相手（r1・同じ構造の共通）× {全記号・押下のある記号} の中央値・四分位・良い側の割合・人数・伏せ
- 2 段（他人）× 相手（r1・同じ構造の共通）× {全記号・押下のある記号}、選ばれた構造・τ の人数
- 共通 − r1、選ばれた τ の人数（格子の区分を含む）、診断、人数・学習と評価の記号の数
- データごとの全員の共通の診断
数は相対 1e-9、文字列・真偽・None は一致。区間（ci）・時間・run_id は照らさない。
出力は照らした数・外れた数・最大の差・外れた節の名前だけ（値は書かない）。

使い方:
  python3 -I repro_check.py <今回の summary.json> <tau-extend の summary.json> <out.json>
  python3 -I repro_check.py --selftest
返り値: 0 = すべて一致、3 = 外れた葉がある（または照らす葉が 0）。
"""
import json
import sys

PANELS = {"coauthor": ("P15", ["1", "5", "15"]), "cs1": ("C5", ["1", "5"])}
STRUCTS = ["hmm3", "ar1", "ar2", "ar3"]
ROWS = ["tau_" + t for t in ["0", "100", "1000", "10000", "30000", "100000", "300000", "1000000", "inf"]] + ["tau_other"]
KEYS = [l + "/self_minus_" + o for l in ("all", "pressed") for o in ("r1", "pool_same")]
STRUCT_EXTRA = ["chosen_tau_other", "chosen_tau_other_region", "pool_minus_r1", "diag"]
TWO_EXTRA = ["chosen_struct", "chosen_tau", "chosen_tau_region"]
CELL_EXTRA = ["writers", "n_train", "n_eval"]
SKIP = {"ci"}
REL = 1e-9
MISSING = object()


def rel_diff(a, b):
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b))


class Acc:
    def __init__(self):
        self.leaves, self.bad, self.worst, self.sections = 0, 0, 0.0, set()

    def leaf(self, a, b, sec):
        self.leaves += 1
        num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)  # noqa: E731
        if num(a) and num(b):
            d = rel_diff(float(a), float(b))
            self.worst = max(self.worst, d)
            ok = d <= REL
        else:
            ok = b is not MISSING and type(a) is type(b) and a == b
            if not ok:
                self.worst = float("inf")
        if not ok:
            self.bad += 1
            self.sections.add(sec)

    def walk(self, a, b, sec):
        if isinstance(a, dict):
            if not isinstance(b, dict):
                self.leaf("dict", MISSING, sec)
                return
            for key, va in a.items():
                if key in SKIP:
                    continue
                self.walk(va, b.get(key, MISSING), sec)
        elif isinstance(a, list):
            if not isinstance(b, list) or len(a) != len(b):
                self.leaf("list", MISSING, sec)
                return
            for va, vb in zip(a, b):
                self.walk(va, vb, sec)
        else:
            self.leaf(a, b, sec)


def get(d, *path):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return MISSING
        d = d[p]
    return d


def compare(new, old):
    """new: この試験の summary.json。old: tau-extend の summary.json。"""
    A = Acc()
    for ds, (pn, ks) in PANELS.items():
        Dold = old["datasets"][ds]
        Dnew = get(new, "columns", "o", ds, "fit")
        A.walk(Dold["pool_full_diag"], get(Dnew, "pool_full_diag"), "%s/pool_full_diag" % ds)
        for k in ks:
            Eo, En = Dold["em"][pn][k], get(Dnew, "em", pn, k)
            base = "%s/%s/k%s" % (ds, pn, k)
            for f in CELL_EXTRA:
                A.walk(Eo[f], get(En, f), base + "/" + f)
            for s in STRUCTS:
                for r in ROWS:
                    for key in KEYS:
                        A.walk(Eo["structs"][s][r][key], get(En, "structs", s, r, key), "%s/%s/%s" % (base, s, r))
                for f in STRUCT_EXTRA:
                    A.walk(Eo["structs"][s][f], get(En, "structs", s, f), "%s/%s/%s" % (base, s, f))
            T_old = Eo["two_stage"]["other"]
            for key in KEYS:
                A.walk(T_old["two_stage_other"][key], get(En, "two_stage", "other", "two_stage_other", key), base + "/two_stage")
            for f in TWO_EXTRA:
                A.walk(T_old[f], get(En, "two_stage", "other", f), base + "/two_stage/" + f)
    return dict(leaves=A.leaves, mismatched=A.bad, max_rel_diff=A.worst, tolerance_rel=REL,
                mismatched_sections=sorted(A.sections))


def selftest():
    """測定器の対照: 同じものは 0 件・1 葉を相対 1e-6 ずらすと 1 件・1 葉を消すと 1 件・区間の違いは 0 件・
    伏せの人数違いで 1 件・文字列の違いで 1 件・相対 1e-10 のずれは 0 件。"""
    import copy

    def c(x):
        return dict(median=x, q25=x - 1, q75=x + 1, better_share=0.5, n=10, ci=[0, 1])

    def E():
        st = {s: dict({r: {key: c(0.1 * (i + 1)) for key in KEYS} for i, r in enumerate(ROWS)},
                      chosen_tau_other={"inf": 6, "0": 4}, chosen_tau_other_region=dict(inside=0, low_end=4, high_finite_end=0, inf=6),
                      pool_minus_r1={"all": c(0.3), "pressed": c(0.2)},
                      diag={"0": dict(winner={"pool": 10}, gap12=c(0.0), nonconv_starts=0, decreases=0)}) for s in STRUCTS}
        return dict(writers=10, n_train=c(5.0), n_eval=c(9.0), structs=st,
                    two_stage=dict(other=dict(two_stage_other={key: c(0.5) for key in KEYS}, chosen_struct={"ar1": 10},
                                              chosen_tau={"inf": 10}, chosen_tau_region=dict(inside=0, low_end=0, high_finite_end=0, inf=10))))

    def old():
        return dict(datasets={ds: dict(pool_full_diag={"hmm3": dict(winner="frozen", gap12=0.1, nonconv=0, decreases=0)},
                                       em={pn: {k: E() for k in ks}}) for ds, (pn, ks) in PANELS.items()})

    def new():
        o = old()
        return dict(columns=dict(o={ds: dict(fit=dict(pool_full_diag=o["datasets"][ds]["pool_full_diag"], em=o["datasets"][ds]["em"]))
                                    for ds in PANELS}))
    a, b = new(), old()
    ok = compare(a, b)["mismatched"] == 0 and compare(a, b)["leaves"] > 0
    x = copy.deepcopy(a)
    x["columns"]["o"]["coauthor"]["fit"]["em"]["P15"]["5"]["structs"]["ar2"]["tau_100"]["all/self_minus_r1"]["median"] *= 1 + 1e-6
    ok = ok and compare(x, b)["mismatched"] == 1
    x = copy.deepcopy(a)
    del x["columns"]["o"]["cs1"]["fit"]["em"]["C5"]["1"]["structs"]["ar3"]["tau_0"]["pressed/self_minus_pool_same"]
    ok = ok and compare(x, b)["mismatched"] >= 1
    x = copy.deepcopy(a)
    x["columns"]["o"]["coauthor"]["fit"]["em"]["P15"]["1"]["structs"]["hmm3"]["tau_0"]["all/self_minus_r1"]["ci"] = [5, 6]
    ok = ok and compare(x, b)["mismatched"] == 0
    x, y = copy.deepcopy(a), copy.deepcopy(b)
    x["columns"]["o"]["coauthor"]["fit"]["em"]["P15"]["15"]["structs"]["ar1"]["tau_inf"]["all/self_minus_r1"] = dict(n=4, suppressed=True)
    y["datasets"]["coauthor"]["em"]["P15"]["15"]["structs"]["ar1"]["tau_inf"]["all/self_minus_r1"] = dict(n=5, suppressed=True)
    ok = ok and compare(x, y)["mismatched"] == 1
    x = copy.deepcopy(a)
    x["columns"]["o"]["cs1"]["fit"]["pool_full_diag"]["hmm3"]["winner"] = "rand1"
    ok = ok and compare(x, b)["mismatched"] == 1
    x = copy.deepcopy(a)
    x["columns"]["o"]["cs1"]["fit"]["em"]["C5"]["5"]["two_stage"]["other"]["two_stage_other"]["all/self_minus_r1"]["q25"] *= 1 + 1e-10
    ok = ok and compare(x, b)["mismatched"] == 0
    x = copy.deepcopy(a)
    x["columns"]["o"]["cs1"]["fit"]["em"]["C5"]["5"]["two_stage"]["other"]["chosen_struct"] = {"ar2": 10}
    ok = ok and compare(x, b)["mismatched"] >= 1
    print(json.dumps(dict(repro_check_selftest=ok)))
    return 0 if ok else 3


def main(argv):
    if argv[0] == "--selftest":
        return selftest()
    new, old = json.load(open(argv[0], encoding="utf-8")), json.load(open(argv[1], encoding="utf-8"))
    r = compare(new, old)
    r["passed"] = r["leaves"] > 0 and r["mismatched"] == 0
    json.dump(r, open(argv[2], "w"), indent=1)
    print(json.dumps(r))
    return 0 if r["passed"] else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
