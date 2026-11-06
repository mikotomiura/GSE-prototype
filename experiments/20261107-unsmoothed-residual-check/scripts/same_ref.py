"""P-SAME の相手: tau-extend の em_writer を、tau-extend のディレクトリのコードで別のプロセスとして回す。

使い方: python3 -I same_ref.py <in.pkl> <out.pkl>
in.pkl: dict(writers, pools, seed, H, ks)。乱数は tau-extend と同じ [seed + 10, w]・並べは tau-extend の本計算と同じ
（structs = None・折り目あり）。
"""
import os
import pickle
import sys

TAU = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../20261104-timeseries-tau-extend/scripts"))
sys.path.insert(0, TAU)
import numpy as np  # noqa: E402
import ml  # noqa: E402

d = pickle.load(open(sys.argv[1], "rb"))
ml.set_mut([])
out = []
for w, units in enumerate(d["writers"]):
    rng = np.random.default_rng([d["seed"] + 10, w])
    out.append(ml.em_writer(units, d["H"], d["ks"], d["pools"], rng, structs=None, do_folds=True))
pickle.dump(dict(results=out, ml_file=os.path.realpath(ml.__file__)), open(sys.argv[2], "wb"))
