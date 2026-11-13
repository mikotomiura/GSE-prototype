"""m0 を作る（conditions.md D1・HP Z2・実データ）。B の compute.job_full をそのまま呼び、CoAuthor の全員の共通 ar3 を
基の倍率 α ∈ {1, 0.3, 0.1, 0.03} で当てる。母数は repo の外の npz に置き、値は表示も JSON にも書かない。

使い方: python3 -I fit_m0.py <coauthor_work_obs> <npz_out> <json_out> <jobs>
mode の ml・hmm2 を読み込むので、合成のコード（tau-extend の ml・hmm2）とは別のプロセスで走らせる。
"""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.realpath(os.path.join(HERE, "..", ".."))
B_DIR = os.path.join(EXP, "20261112-selection-split-and-smoothing", "scripts")
PINNED = {
    os.path.join(B_DIR, "compute.py"): "df2dcb291eb8b385d3d1c4492f40d60764c8132d725c66cd467ca3ccc1ecbd6b",
    os.path.join(B_DIR, "ab.py"): "6eb301ac3257083793056d098afb598b898aee0e1ce0f095a1a2d2f96b7508f0",
    os.path.join(B_DIR, "pinned4.py"): "fbc19b1e394147b48d9f209911ce84029600455046abd33bc2f71684d50c6b2c",
}
ALPHAS = ["1", "0.3", "0.1", "0.03"]
STRUCT = ("ar", 3)
KEYS = ("pi", "A", "H", "C")
SHAPES = dict(pi=(3,), A=(3, 3), H=(3, 26), C=(3, 26, 26))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def m0_checks(m):
    """形・有限・非負・行の和が 1（1e-9 以内）・確率 0 のセルの有無（値は返さない）。"""
    ok_shape = m.get("kind") == "ar" and all(np.shape(m[k]) == SHAPES[k] for k in KEYS)
    ok_fin = ok_shape and all(np.isfinite(m[k]).all() and (m[k] >= 0).all() for k in KEYS)
    ok_sum = ok_fin and all(np.abs(m[k].sum(-1) - 1).max() <= 1e-9 for k in KEYS)
    has_zero = bool(ok_fin and any((m[k] == 0).any() for k in KEYS))
    return dict(shape=bool(ok_shape), finite_nonneg=bool(ok_fin), rows_sum_1=bool(ok_sum), has_zero_cell=has_zero)


def main():
    path, npz_out, json_out, jobs = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    bad = sorted(os.path.relpath(p, EXP) for p, v in PINNED.items() if sha(p) != v)
    if bad:
        sys.exit("B のコードの SHA-256 が条件の値と違う: %r" % bad)
    sys.path.insert(0, B_DIR)
    import compute as CP  # noqa: E402  (ab・pinned4 が mode の ml・hmm2・data・hmm_b と summary を照らす)
    ml = CP.ml
    if CP.SEED != 2026110401 or STRUCT not in ml.STRUCTS or ml.SEQ_NO[STRUCT] != 5:
        sys.exit("B の SEED か構造の番号が条件と違う")
    t0 = time.time()
    with ProcessPoolExecutor(min(jobs, len(ALPHAS)), initializer=ml._init, initargs=({"coauthor": path}, CP.SEED, [])) as ex:
        ms = list(ex.map(CP.job_full, [dict(ds="coauthor", s=STRUCT, alpha=float(a), seed=CP.SEED) for a in ALPHAS]))
    sec = time.time() - t0
    arrs, checks = {}, {}
    for a, m in zip(ALPHAS, ms):
        checks[a] = m0_checks(m)
        for k in KEYS:
            arrs["a%s_%s" % (a, k)] = np.asarray(m[k], dtype=np.float64)
    if not all(c["shape"] and c["finite_nonneg"] and c["rows_sum_1"] for c in checks.values()):
        sys.exit("当てた m0 の形か行の和が条件と違う（値は表示しない）: %r" % checks)
    os.makedirs(os.path.dirname(os.path.abspath(npz_out)), exist_ok=True)
    with open(npz_out, "wb") as f:
        np.savez(f, **arrs)
    out = dict(alphas=ALPHAS, struct="ar3", seed=CP.SEED, npz_sha256=sha(npz_out), seconds=sec, checks=checks,
               b_code={os.path.relpath(p, EXP): v for p, v in PINNED.items()})
    with open(json_out, "w", newline="\n") as f:
        json.dump(out, f, indent=1)
    print("m0 を当てた（%d 倍率・%.0f 秒）。npz は repo の外" % (len(ALPHAS), sec), flush=True)


if __name__ == "__main__":
    main()
