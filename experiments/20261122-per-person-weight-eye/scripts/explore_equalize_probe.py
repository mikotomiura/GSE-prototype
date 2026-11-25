"""探索（門の判定に使わない・判断 47）: 本人の A と B の遷移の数を、書き手のあいだで揃えると、量の差による拾いすぎが消えるか。

使い方: python3 -I explore_equalize_probe.py <out_json> [--n 200] [--jobs 8]
- 1 複製で、元の目（D1・D2 どおり）と揃えた目を、同じ生成・同じ入れ替えで並べて出す（対の比べ）。
- 揃え方: セルごとに、書き手 v の NA_v（と NB_v）の遷移を、パネルの最小の総数まで、重複なしで間引く
  （多変量の超幾何。乱数は [SEED + 93, 筋, 形, k, g, 種, 側, v]）。共有の表 S と占有 π は元のまま。
- 種は 910000 から（報告の組 2000〜2999・前の探索 900000〜900159 と重ならない）。第 2 の帰無（npz）は扱わない。
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

SEED0 = 910000
GROUPS = ([("volume", sh, 0.0) for sh in ("coauthor", "cs1")] + [("stack", sh, 0.0) for sh in ("coauthor", "cs1")]
          + [("dose", sh, 0.0) for sh in ("coauthor", "cs1")] + [("dose", "coauthor", g) for g in GN.DOSE])


def thin(N, n, rng):
    flat = N.ravel()
    if flat.sum() == n:
        return N.copy()
    return rng.multivariate_hypergeometric(flat, n).reshape(N.shape)


def equalize(T, key):
    T = dict(T)
    NA, NB = T["NA"], T["NB"]
    nA, nB = int(NA.reshape(len(NA), -1).sum(1).min()), int(NB.reshape(len(NB), -1).sum(1).min())
    NA2 = np.array([thin(NA[v], nA, np.random.default_rng(key + [0, v])) for v in range(len(NA))])
    NB2 = np.array([thin(NB[v], nB, np.random.default_rng(key + [1, v])) for v in range(len(NB))])
    T["NA"], T["NB"] = NA2, NB2
    T["PA"] = np.array([EY.own_table(NA2[w], T["Ss"][w]) for w in range(len(NA2))])
    T["PB"] = np.array([EY.own_table(NB2[v], T["Ss"][v]) for v in range(len(NB2))])
    return T, nA, nB


def score(T, perms):
    S3 = EY.sims(T)
    out = {}
    for e in EY.EYES:
        c = EY.score_matrix(S3[e])
        p, W = EY.p_sampled(c, perms)
        out[e] = dict(p=p, auc_mean=float(EY.auc_rows(c).mean()))
    return out


def one(a):
    strand, shape, step, seed = a
    r = dict(null=1, strand=strand, shape=shape, step=step, seed=seed)
    w, P = GN.make(r)
    sh = GN.SY.SHAPES[shape]
    UC = EY.count_writers(w, GN.NSYM)
    out = dict(seed=seed, cells={})
    for k, g in RE.CELLS[shape]:
        rng = np.random.default_rng([GN.SEED, 1, GN.STRAND[strand], RE.SHAPE_NO[shape], k, g, seed])
        perms = EY.draw_perms(rng, P)
        T = EY.cell_tables(UC, P, sh["H"], k, g)
        key = [GN.SEED + 93, GN.STRAND[strand], RE.SHAPE_NO[shape], k, g, seed]
        Te, nA, nB = equalize(T, key)
        out["cells"]["k%d_g%d" % (k, g)] = dict(orig=score(T, perms), eq=score(Te, perms), nA=nA, nB=nB,
                                                 medA=float(np.median(T["NA"].reshape(P, -1).sum(1))),
                                                 medB=float(np.median(T["NB"].reshape(P, -1).sum(1))))
    return out


def main():
    argv = sys.argv[1:]
    opt = {}
    for key in ("--n", "--jobs"):
        if key in argv:
            i = argv.index(key)
            opt[key] = int(argv[i + 1])
            argv = argv[:i] + argv[i + 2:]
    path, n, jobs = argv[0], opt.get("--n", 200), opt.get("--jobs", 8)
    GN.assert_clean()
    R = dict(code_hash=RE.code_hash(), n=n, seed0=SEED0, groups={})
    with ProcessPoolExecutor(jobs) as ex:
        for strand, shape, step in GROUPS:
            g = "null1_%s_%s_%s" % (strand, shape, repr(step))
            R["groups"][g] = list(ex.map(one, [(strand, shape, step, s) for s in range(SEED0, SEED0 + n)]))
            print("終わり: %s" % g, flush=True)
            json.dump(R, open(path, "w"))
    print("書いた: %s" % path)


if __name__ == "__main__":
    main()
