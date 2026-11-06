"""読みの形 1〜5 を summary.json から機械的に当てる（読みの補助・repo の外）。"""
import json, sys, math
from collections import Counter, defaultdict
D = json.load(open(sys.argv[1]))
MAIN = {"coauthor": ["P15", "P30"], "cs1": ["C5"]}
TAUS = ["100000", "300000", "1000000"]
def v(x):
    if x == "+inf": return math.inf
    if x == "-inf": return -math.inf
    return x
def form(a, b, c, share):
    a, b, c = v(a), v(b), v(c)
    if any(math.isinf(x) for x in (a, b, c)): return 5
    if abs(a) < abs(b) and (b > 0) == (c > 0) and b != 0 and c != 0: return 1
    if abs(a) > abs(b) and a > 0 and share > 0.5: return 2
    return 3
summ = defaultdict(Counter); f4 = defaultdict(Counter); rng = defaultdict(list)
detail = []
for ds, panels in MAIN.items():
    E = D["datasets"][ds]["em"]
    for pn in panels:
        for k, Ek in E[pn].items():
            for s in ["hmm3", "ar1", "ar2", "ar3"]:
                St = Ek["structs"][s]
                for lab in ("all", "pressed"):
                    # main
                    b = St["tau_mode"][f"{lab}/self_minus_pool_same"]
                    r = {t: St["tau_" + t] for t in TAUS}
                    a6 = r["1000000"][f"{lab}/self_minus_mode_same"]; c6 = r["1000000"][f"{lab}/self_minus_pool_same"]
                    fm = form(a6["median"], b["median"], c6["median"], a6["better_share"])
                    # sub
                    F = St["finite_mode"]
                    fb = F["tau_mode"]["stats"][f"{lab}/self_minus_pool_same"]
                    fa6 = F["tau_1000000"]["stats"][f"{lab}/self_minus_mode_same"]; fc6 = F["tau_1000000"]["stats"][f"{lab}/self_minus_pool_same"]
                    fs = form(fa6["median"], fb["median"], fc6["median"], fa6["better_share"])
                    am = [abs(v(r[t][f"{lab}/self_minus_mode_same"]["median"])) for t in TAUS]
                    m4 = am[0] > am[1] > am[2]
                    fam = [abs(v(F["tau_" + t]["stats"][f"{lab}/self_minus_mode_same"]["median"])) for t in TAUS]
                    s4 = fam[0] > fam[1] > fam[2]
                    key = (ds, pn, s, lab)
                    summ[key][(fm, fs)] += 1; f4[key][(m4, s4)] += 1
                    signdiff = (v(a6["median"]) > 0) != (v(fa6["median"]) > 0)
                    rng[key].append((k, St["mode_counts"]["neg_inf"], St["mode_counts"]["zero_row_hit"], St["mode_counts"]["writers"], F["tau_mode"]["writers"], a6["median"], b["median"], c6["median"], a6["better_share"], fa6["median"], fb["median"], fc6["median"], fa6["better_share"], signdiff))
for key in summ:
    print(key, "forms(main,sub):", dict(summ[key]), " form4(main,sub):", dict(f4[key]))
    ks = rng[key]
    print("   neg_inf", sorted({x[1] for x in ks}), "zero_row", sorted({x[2] for x in ks}), "writers", sorted({x[3] for x in ks}), "sub_n", sorted({x[4] for x in ks}),
          "a6 main [%.2g,%.2g]" % (min(v(x[5]) for x in ks), max(v(x[5]) for x in ks)),
          "b [%.2g,%.2g]" % (min(v(x[6]) for x in ks), max(v(x[6]) for x in ks)),
          "c6 [%.2g,%.2g]" % (min(v(x[7]) for x in ks), max(v(x[7]) for x in ks)),
          "share a6 [%.2f,%.2f]" % (min(x[8] for x in ks), max(x[8] for x in ks)),
          "sub a6 [%.2g,%.2g]" % (min(v(x[9]) for x in ks), max(v(x[9]) for x in ks)),
          "sub b [%.2g,%.2g]" % (min(v(x[10]) for x in ks), max(v(x[10]) for x in ks)),
          "sub share [%.2f,%.2f]" % (min(x[12] for x in ks), max(x[12] for x in ks)),
          "sign main!=sub k:", [x[0] for x in ks if x[13]])
