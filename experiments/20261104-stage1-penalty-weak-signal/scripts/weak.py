"""段 1 の罰の強さ —— 係数の倍率を変えた合成（conditions.md W0〜W2）。

前の実験の sim.py（experiments/20261104-stage1-penalty-synthetic/scripts/）を書き換えずに読み込み、
sim.BETA を倍率つきで置いてから sim.calib_a・sim.one_rep を呼ぶ。

使い方: python3 -I -X utf8 weak.py SEED OUT JOBS [--reps 400] [--mutate w1] [--run-id ID]
反復ごとの値を OUT/raw/<セル>.npz に書く（git に入れない）。集計と規則は report_weak.py。

変異（conditions W3・MUT_W に入る）:
  w1: 係数 1 倍のセルの乱数の流れの番号をずらす（前の主のセルと別の流れになる）
  w2: 倍率を sim.BETA に入れない（どの強さも 1 倍になる）
  w3: ワーカーの _job で倍率を置かない（親で置いた値のまま・spawn のワーカーでは 1 倍）
  w4: ワーカーの _job で係数 1 倍のときだけ係数を 1.0001 倍にする（番号と切片は同じで値だけがずれる）
"""
import hashlib
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "20261104-stage1-penalty-synthetic", "scripts"))
sys.path.insert(0, SIM_DIR)
import sim  # noqa: E402

BASE_BETA = sim.BETA.copy()
SCALES = [1.0, 0.5, 0.25]
ID_BASE = {1.0: 0, 0.5: 400, 0.25: 500}  # 1 倍は前の主のセルと同じ番号（再現の門 W1・W4）
MUT_W = set()


def set_scale(k):
    """sim の大域の係数を倍率 k にする（w2 は倍率を入れない）。"""
    if "w2" in MUT_W:
        k = 1.0
    sim.BETA = BASE_BETA * k


def cell_id(main_id, k):
    off = ID_BASE[k]
    if "w1" in MUT_W and k == 1.0:
        off = 600
    return off + main_id


def cells(seed):
    """主の格子の信号ありのセル × 倍率。main_id は前の実験の主のセルの番号。"""
    al = sim.acells()
    out = []
    for k in SCALES:
        set_scale(k)
        a_of = {c: sim.calib_a(seed, i, *c) for i, c in enumerate(al) if c[2] and c[3] == "main"}
        i = 0
        for n in sim.NS:
            for r in sim.RATES:
                for sd in sim.SDS:
                    for sig in sim.SIGNALS:
                        if sig:
                            out.append(dict(id=cell_id(i, k), main_id=i, scale=k, set="main", n=n, rate=r, sd=sd,
                                            signal=True, kind="main", a=a_of[(r, sd, True, "main")]))
                        i += 1
    set_scale(1.0)
    return out


def _job(args):
    cell, rep, seed, mut = args
    MUT_W.clear()
    MUT_W.update(mut)
    sim.MUT.clear()
    if "w3" not in MUT_W:
        set_scale(cell["scale"])
    if "w4" in MUT_W and cell["scale"] == 1.0:
        sim.BETA = BASE_BETA * 1.0001  # 切片とセルの番号は変えず、ワーカーの係数だけをずらす
    return sim.one_rep(cell, rep, seed)


def run_cells(seed, cl, reps, jobs, mut=()):
    out = {}
    with Pool(jobs) as pool:
        for c in cl:
            res = pool.map(_job, [(c, r, seed, tuple(mut)) for r in range(reps)], chunksize=8)
            out[c["id"]] = (c, sim.stack(res))
    return out


def main(argv):
    seed, out, jobs = int(argv[0]), argv[1], int(argv[2])
    opt = dict(zip(argv[3::2], argv[4::2]))
    reps = int(opt.get("--reps", 400))
    mut = [m for m in opt.get("--mutate", "").split(",") if m]
    MUT_W.update(mut)
    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    cl = cells(seed)
    res = run_cells(seed, cl, reps, jobs, mut)
    sha = {}
    for cid, (c, arr) in res.items():
        fn = os.path.join(raw, f"cell{cid:03d}.npz")
        np.savez_compressed(fn, **arr)
        sha[os.path.basename(fn)] = hashlib.sha256(open(fn, "rb").read()).hexdigest()
    with open(os.path.join(raw, "cells.json"), "w") as f:
        json.dump(dict(seed=seed, reps=reps, mutate=mut, run_id=opt.get("--run-id"), scales=SCALES,
                       taus=[str(t) for t in sim.TAUS], cells=[c for c, _ in res.values()], sha256=sha),
                  f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
