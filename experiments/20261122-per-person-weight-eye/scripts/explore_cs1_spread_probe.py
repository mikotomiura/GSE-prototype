"""探索（門の判定に使わない・判断 48）: CS1 の書き手ごとの量の幅を実データに寄せたとき、量を揃えた目の差なしと検出力。

使い方: python3 -I explore_cs1_spread_probe.py <out_json> [--jobs 8]
- 生成（この探索だけの作り・gen.py は変えない）: CS1 の形（パネル 23 人 × 6 単位・他 8 人 × 3 単位・1 単位 2 本・
  長さ 5,000〜8,000）で、書き手ごとに r_w を対数一様に引き、その書き手のすべての長さに掛ける。
  幅は wide = 0.2〜5 倍（四分位で約 4.9 倍。論文 3 の補足 S2 の評価の側の四分位 2,965〜16,640 は 5.6 倍）と、flat = 1 倍。
  植えた差は書き手ごとに D_w を 1 つ引き、全単位の C を (1 − λ) C0 + λ D_w にする（λ = lam_first(3, g)・用量の筋と同じ）。
- 揃え方・入れ替え・目は explore_equalize_probe.py と同じ（元の目と揃えた目を対で出す）。
- 群: wide の差なし 1,000 複製、wide と flat の g = 1e-3・3e-3・1e-2・3e-2 を各 500 複製。種 920000 から。
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
from explore_equalize_probe import equalize, score  # noqa: E402

SY = GN.SY
SEED0 = 920000
WIDTH = dict(wide=(0.2, 5.0), flat=(1.0, 1.0))
GROUPS = [("wide", 0.0, 1000)] + [(w, g, 500) for w in ("wide", "flat") for g in GN.DOSE]


def build(width, g, seed):
    sh = SY.SHAPES["cs1"]
    m0 = GN.m0_first(3)
    lam = GN.lam_first(3, g)
    lo, hi = WIDTH[width]
    rng1 = np.random.default_rng([GN.SEED + 95, 1 if width == "wide" else 0, GN.STEP[g], seed, 1])
    rng4 = np.random.default_rng([GN.SEED + 95, 1 if width == "wide" else 0, GN.STEP[g], seed, 4])
    writers, vols = [], []
    for i in range(sh["P"] + sh["O"]):
        nu = sh["Pu"] if i < sh["P"] else sh["Ou"]
        r_w = float(np.exp(rng1.uniform(np.log(lo), np.log(hi)))) if hi > lo else 1.0
        C = SY.writer_model(m0, SY.draw_D(m0, rng1), lam)["C"] if lam > 0 else m0["C"]
        lens = [[int(round(r_w * L)) for L in rng1.integers(sh["L"][0], sh["L"][1] + 1, size=sh["nseq"]).tolist()]
                for _ in range(nu)]
        smp = SY.Sampler(dict(kind="ar", pi=m0["pi"].copy(), A=m0["A"].copy(), H=m0["H"].copy(), C=C))
        units = []
        for ls in lens:
            ss = [smp.seq(rng4.random((L, 2))) for L in ls]
            units.append(dict(seqs=ss, pflag=[np.ones(len(x), dtype=bool) for x in ss]))
        writers.append(units)
    return writers, sh["P"]


def one(a):
    width, g, seed = a
    w, P = build(width, g, seed)
    sh = SY.SHAPES["cs1"]
    UC = EY.count_writers(w, GN.NSYM)
    out = dict(seed=seed, cells={})
    for k, gg in RE.CELLS["cs1"]:
        rng = np.random.default_rng([GN.SEED + 95, k, gg, seed])
        perms = EY.draw_perms(rng, P)
        T = EY.cell_tables(UC, P, sh["H"], k, gg)
        key = [GN.SEED + 95, 1 if width == "wide" else 0, GN.STEP[g], k, gg, seed]
        Te, nA, nB = equalize(T, key)
        out["cells"]["k%d_g%d" % (k, gg)] = dict(orig=score(T, perms), eq=score(Te, perms), nA=nA, nB=nB,
                                                 medA=float(np.median(T["NA"].reshape(P, -1).sum(1))),
                                                 medB=float(np.median(T["NB"].reshape(P, -1).sum(1))))
    return out


def main():
    argv = sys.argv[1:]
    jobs = 8
    if "--jobs" in argv:
        i = argv.index("--jobs")
        jobs = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    path = argv[0]
    GN.assert_clean()
    R = dict(code_hash=RE.code_hash(), seed0=SEED0, groups={})
    with ProcessPoolExecutor(jobs) as ex:
        for width, g, n in GROUPS:
            name = "cs1_%s_%s" % (width, repr(g))
            R["groups"][name] = list(ex.map(one, [(width, g, s) for s in range(SEED0, SEED0 + n)]))
            print("終わり: %s" % name, flush=True)
            json.dump(R, open(path, "w"))
    print("書いた: %s" % path)


if __name__ == "__main__":
    main()
