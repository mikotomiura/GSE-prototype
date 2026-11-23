"""P-SAME の片側: 前の試験のディレクトリ（experiments/20261104-timeseries-tau-extend/scripts/）の em_writer を、
合成の書き手に前の試験と同じ並べ（structs = None）で走らせる（selftest.py が別のプロセスで呼ぶ・合成のデータだけ）。

使い方: python3 -I same_old.py <in.pkl> <out.pkl>
in.pkl: dict(mut, writers, pools（4 構造）, seed, H, ks)。書き手の乱数は [seed + 10, 書き手の番号]（selftest の em_job と同じ）。
前の試験のコードは変えない。読むだけ。
"""
import os
import pickle
import sys

OLD = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../20261104-timeseries-tau-extend/scripts"))
sys.path.insert(0, OLD)
import numpy as np  # noqa: E402
import ml as old_ml  # noqa: E402

assert os.path.realpath(os.path.dirname(old_ml.__file__)) == OLD, "前の試験の ml.py を読めていない"


def main(pin, pout):
    a = pickle.load(open(pin, "rb"))
    old_ml.set_mut(a["mut"])
    out = []
    for w, units in enumerate(a["writers"]):
        rng = np.random.default_rng([a["seed"] + 10, w])
        out.append(old_ml.em_writer(units, a["H"], a["ks"], a["pools"], rng))
    pickle.dump(out, open(pout, "wb"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
