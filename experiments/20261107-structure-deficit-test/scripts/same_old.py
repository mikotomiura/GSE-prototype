"""P-SAME の片側: 前の試験のディレクトリの em_writer を、合成の書き手に前の試験と同じ並べで走らせる
（selftest.py が別のプロセスで呼ぶ・合成のデータだけ・前の試験のコードは変えない。読むだけ）。

使い方: python3 -I same_old.py <tau|mli> <in.pkl> <out.pkl>
  tau = experiments/20261104-timeseries-tau-extend/scripts（hmm3・ar1〜ar3・全 τ・hmm6・hmm10 の乱数を捨てる）
  mli = experiments/20261104-coauthor-ml-improve/scripts（6 構造・τ ∈ {0, 100, 1,000, 10,000}）
in.pkl: dict(writers, pools（6 構造）, seed, H, ks)。書き手の乱数は [seed + 10, 書き手の番号]。
"""
import os
import pickle
import sys

DIRS = {"tau": "20261104-timeseries-tau-extend", "mli": "20261104-coauthor-ml-improve"}
which = sys.argv[1]
OLD = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", DIRS[which], "scripts"))
sys.path.insert(0, OLD)
import numpy as np  # noqa: E402
import ml as old_ml  # noqa: E402

assert os.path.realpath(os.path.dirname(old_ml.__file__)) == OLD, "前の試験の ml.py を読めていない"


def main(pin, pout):
    a = pickle.load(open(pin, "rb"))
    out = []
    for w, units in enumerate(a["writers"]):
        rng = np.random.default_rng([a["seed"] + 10, w])
        out.append(old_ml.em_writer(units, a["H"], a["ks"], a["pools"], rng))
    pickle.dump(out, open(pout, "wb"))


if __name__ == "__main__":
    main(sys.argv[2], sys.argv[3])
