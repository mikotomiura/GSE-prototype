"""P-REPRO（conditions V1）: 組 (5, o) の summary の、前の試験と重なる葉を機械で照らす。

照らす葉（前の側を射影してから、その葉だけを辿る）:
- tau-extend（experiments/20261104-timeseries-tau-extend/results/summary.json）: hmm3・ar1〜ar3 の、作る k（CoAuthor P15 の
  1・5・15、P30 の 30、CS1 C5 の 1・5）の τ 固定 9 行と τ 他人の行 × 相手 r1・同じ構造の共通 × 全記号・押下、
  chosen_tau_other（と region）・pool_minus_r1・diag、セルの writers・n_train・n_eval、全員の共通の診断。
- ml-improve（experiments/20261104-coauthor-ml-improve/results/summary.json）: hmm6・hmm10 の、同じ k の
  τ ∈ {0, 100, 1,000, 10,000} の固定の行 × 同じ相手、diag（同じ τ）、セルの writers、全員の共通の診断。
数（float）は相対 1e-9、整数・文字列・真偽・None は一致。照らさない: ci・seconds・run_id（区間の乱数の位置がずれる）。
w を除く共通の診断・4 つ組は照らさない（今回はパネルに入る書き手だけを当てはめる）。
出力は照らした数・外れた数・最大の差・外れた節の名前（データ / 一番上の鍵 の 2 層だけ）。

使い方:
  python3 -I repro_check.py <今回の summary.json> <tau-extend の summary.json> <ml-improve の summary.json> <out.json>
  python3 -I repro_check.py --selftest
返り値: 0 = すべて一致、3 = 外れた葉がある（または照らす葉が 0）。HP Z2 で回す門。
"""
import copy
import json
import math
import sys

SKIP = {"ci", "ci_method", "seconds", "run_id"}
REL = 1e-9
KS = {"coauthor": {"P15": ["1", "5", "15"], "P30": ["30"]}, "cs1": {"C5": ["1", "5"]}}
OPP_KEYS = ["%s/self_minus_%s" % (j, o) for j in ("all", "pressed") for o in ("r1", "pool_same")]
TAU_ALL = ["0", "100", "1000", "10000", "30000", "100000", "300000", "1000000", "inf"]
TAU_PREV = ["0", "100", "1000", "10000"]
SPEC = {
    "tau": dict(names=["hmm3", "ar1", "ar2", "ar3"], rows=["tau_" + t for t in TAU_ALL] + ["tau_other"],
                extra=["chosen_tau_other", "chosen_tau_other_region", "pool_minus_r1"], diag_taus=None,
                cell=["writers", "n_train", "n_eval"]),
    "mli": dict(names=["hmm6", "hmm10"], rows=["tau_" + t for t in TAU_PREV], extra=[], diag_taus=TAU_PREV, cell=["writers"]),
}


def project(old, which):
    """前の summary から、照らす葉だけを残した木（今回の summary の datasets の形）を作る。"""
    sp = SPEC[which]
    out = {}
    for ds, panels in KS.items():
        if ds not in old.get("datasets", {}):
            continue
        D = old["datasets"][ds]
        em = {}
        for pn, ks in panels.items():
            for k in ks:
                E = D["em"][pn][k]
                c = {key: E[key] for key in sp["cell"] if key in E}
                c["structs"] = {}
                for nm in sp["names"]:
                    St = E["structs"][nm]
                    s = {r: {o: St[r][o] for o in OPP_KEYS if o in St[r]} for r in sp["rows"]}
                    for key in sp["extra"]:
                        s[key] = St[key]
                    s["diag"] = St["diag"] if sp["diag_taus"] is None else {t: St["diag"][t] for t in sp["diag_taus"]}
                    c["structs"][nm] = s
                em.setdefault(pn, {})[k] = c
        out[ds] = dict(em=em, pool_full_diag={nm: D["pool_full_diag"][nm] for nm in sp["names"]})
    return out


def rel_diff(a, b):
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b))


def walk(old, new, path, acc):
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
        if not (math.isfinite(old) and math.isfinite(float(new))):
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


def compare(new, olds):
    """new: 今回の summary 全体。olds: {"tau": 前の summary, "mli": 前の summary}。"""
    nd = new.get("groups", {}).get("q5_o", {}).get("datasets", {})
    out = {}
    for which, old in olds.items():
        acc = dict(cells=0, bad=0, worst=0.0, sections=set())
        walk(project(old, which), nd, [], acc)
        out[which] = dict(cells=acc["cells"], mismatched=acc["bad"], max_rel_diff=acc["worst"], tolerance_rel=REL,
                          mismatched_sections=sorted(acc["sections"]))
    return out


def selftest():
    """測定器の対照: 同じ値は 0 件・照らす葉を相対 1e-6 ずらすと 1 件・照らさない葉（tau_cv・fb・k = 3）を変えても 0 件・
    照らすセルを消すと 5 件（median・q25・q75・better_share・n）・区間を変えても 0 件・全員の共通の診断の違いで 1 件。"""
    def cell(x):
        return dict(median=x, q25=x - 1, q75=x + 1, better_share=0.5, n=10, ci=[0, 1])

    def old_summ(names, taus):
        def st(i):
            s = {"tau_" + t: {o: cell(0.1 * (i + 1)) for o in OPP_KEYS + ["all/self_minus_fb"]} for t in taus}
            s["tau_other"] = {o: cell(0.3) for o in OPP_KEYS}
            s["tau_cv"] = {o: cell(0.4) for o in OPP_KEYS}
            s.update(chosen_tau_other={"0": 9}, chosen_tau_other_region=dict(inside=9), pool_minus_r1={"all": cell(0.2)},
                     diag={t: dict(winner={"pool": 9}, gap12=None, nonconv_starts=0, decreases=0) for t in taus})
            return s
        em = {pn: {k: dict(writers=9, n_train=dict(median=1.0), n_eval=dict(median=2.0),
                           structs={nm: st(i) for i, nm in enumerate(names)}) for k in ks + ["3"]}
              for pn, ks in KS["coauthor"].items()}
        return dict(datasets=dict(coauthor=dict(em=em, pool_full_diag={nm: dict(winner="rand1", gap12=0.01) for nm in names})))

    tau = old_summ(SPEC["tau"]["names"], TAU_ALL)
    mli = old_summ(SPEC["mli"]["names"], TAU_PREV)
    new_ds = dict(coauthor=dict(em=copy.deepcopy(project(tau, "tau")["coauthor"]["em"]),
                                pool_full_diag={**tau["datasets"]["coauthor"]["pool_full_diag"],
                                                **mli["datasets"]["coauthor"]["pool_full_diag"]}))
    for pn, ks in KS["coauthor"].items():
        for k in ks:
            new_ds["coauthor"]["em"][pn][k]["structs"].update(project(mli, "mli")["coauthor"]["em"][pn][k]["structs"])
    new = dict(groups=dict(q5_o=dict(datasets=new_ds)))
    olds = dict(tau=tau, mli=mli)
    r0 = compare(new, olds)
    ok = all(v["mismatched"] == 0 and v["cells"] > 0 for v in r0.values())
    n1 = copy.deepcopy(new)
    n1["groups"]["q5_o"]["datasets"]["coauthor"]["em"]["P15"]["5"]["structs"]["ar2"]["tau_inf"]["all/self_minus_r1"]["median"] *= 1 + 1e-6
    ok = ok and compare(n1, olds)["tau"]["mismatched"] == 1
    o2 = copy.deepcopy(olds)
    o2["tau"]["datasets"]["coauthor"]["em"]["P15"]["5"]["structs"]["hmm3"]["tau_cv"]["all/self_minus_r1"]["median"] = 9.0
    o2["tau"]["datasets"]["coauthor"]["em"]["P15"]["5"]["structs"]["hmm3"]["tau_0"]["all/self_minus_fb"]["median"] = 9.0
    o2["mli"]["datasets"]["coauthor"]["em"]["P15"]["3"]["structs"]["hmm6"]["tau_0"]["all/self_minus_r1"]["median"] = 9.0
    ok = ok and all(v["mismatched"] == 0 for v in compare(new, o2).values())
    n3 = copy.deepcopy(new)
    del n3["groups"]["q5_o"]["datasets"]["coauthor"]["em"]["P30"]["30"]["structs"]["hmm10"]["tau_100"]["pressed/self_minus_pool_same"]
    ok = ok and compare(n3, olds)["mli"]["mismatched"] == 5  # 1 つのセル = median・q25・q75・better_share・n
    n4 = copy.deepcopy(new)
    n4["groups"]["q5_o"]["datasets"]["coauthor"]["em"]["P15"]["1"]["structs"]["hmm3"]["tau_0"]["all/self_minus_r1"]["ci"] = [5, 6]
    ok = ok and all(v["mismatched"] == 0 for v in compare(n4, olds).values())
    n5 = copy.deepcopy(new)
    n5["groups"]["q5_o"]["datasets"]["coauthor"]["pool_full_diag"]["hmm6"]["winner"] = "rand2"
    ok = ok and compare(n5, olds)["mli"]["mismatched"] == 1
    print(json.dumps(dict(selftest_passed=bool(ok))))
    return 0 if ok else 3


def main(argv):
    if argv[0] == "--selftest":
        return selftest()
    new, tau, mli, out = argv[:4]
    r = compare(json.load(open(new)), dict(tau=json.load(open(tau)), mli=json.load(open(mli))))
    json.dump(r, open(out, "w"), indent=1)
    print(json.dumps({k: dict(cells=v["cells"], mismatched=v["mismatched"]) for k, v in r.items()}))
    return 0 if all(v["mismatched"] == 0 and v["cells"] > 0 for v in r.values()) else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
