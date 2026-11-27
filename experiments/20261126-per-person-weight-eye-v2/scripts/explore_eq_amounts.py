"""探索（門の判定に使わない・判断 52）: 報告の組の合成で、揃えた後の A と B の総数（パネルの最小）の範囲を数える。

追記 1（D7）の量の規則の基準に使う。揃えた後の数は間引きの乱数に依らず、パネルの書き手の総数の最小で決まるので、
生成と数え上げだけで出る（目・入れ替えは回さない）。第 1 の帰無の差なしの筋（step 0）だけ。第 2 の帰無は HP Z2 の作業なので扱わない。
実データは読まない。

使い方: python -I explore_eq_amounts.py <出力 json> [並列の数]
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eye as EY  # noqa: E402
import gen as GN  # noqa: E402
import run_eye as RE  # noqa: E402


def one(r):
    w, P = GN.make(r)
    sh = GN.SY.SHAPES[r["shape"]]
    UC = EY.count_writers(w, GN.NSYM)
    out = {}
    for k, g in RE.CELLS[r["shape"]]:
        T = EY.cell_tables(UC, P, sh["H"], k, g)
        tA = T["NA"].reshape(P, -1).sum(1)
        tB = T["NB"].reshape(P, -1).sum(1)
        out["k%d_g%d" % (k, g)] = (int(tA.min()), int(tB.min()), float(np.median(tA)), float(np.median(tB)))
    return RE.group(r), out


def main():
    GN.assert_clean()
    rows = [r for r in RE.plan("report") if r["null"] == 1 and r["step"] == 0.0]
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    acc = {}
    with ProcessPoolExecutor(jobs) as ex:
        for grp, out in ex.map(one, rows, chunksize=8):
            for cell, (a, b, ma, mb) in out.items():
                d = acc.setdefault(grp, {}).setdefault(cell, dict(nA=[], nB=[], medA=[], medB=[]))
                d["nA"].append(a)
                d["nB"].append(b)
                d["medA"].append(ma)
                d["medB"].append(mb)
    res = {}
    for grp, cells in acc.items():
        for cell, d in cells.items():
            res.setdefault(grp, {})[cell] = dict(
                n=len(d["nA"]),
                nA_min=min(d["nA"]), nA_max=max(d["nA"]), nA_med=float(np.median(d["nA"])),
                nB_min=min(d["nB"]), nB_max=max(d["nB"]), nB_med=float(np.median(d["nB"])),
                ratioA_med=float(np.median(np.array(d["nA"]) / np.array(d["medA"]))),
                ratioB_med=float(np.median(np.array(d["nB"]) / np.array(d["medB"]))))
    allc = {}
    for grp, cells in res.items():
        shape = grp.split("_")[2]
        for cell, v in cells.items():
            a = allc.setdefault("%s/%s" % (shape, cell), dict(nA_min=10**12, nA_max=0, nB_min=10**12, nB_max=0))
            a["nA_min"] = min(a["nA_min"], v["nA_min"])
            a["nA_max"] = max(a["nA_max"], v["nA_max"])
            a["nB_min"] = min(a["nB_min"], v["nB_min"])
            a["nB_max"] = max(a["nB_max"], v["nB_max"])
    me = os.path.abspath(__file__)
    import hashlib
    json.dump(dict(script_sha256=hashlib.sha256(open(me, "rb").read()).hexdigest(), code_hash=RE.code_hash(),
                   by_cell=allc, by_group=res), open(sys.argv[1], "w"), indent=1, sort_keys=True)
    for c, v in sorted(allc.items()):
        print(c, v)


if __name__ == "__main__":
    main()
