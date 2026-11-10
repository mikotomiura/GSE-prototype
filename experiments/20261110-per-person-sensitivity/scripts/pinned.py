"""tau-extend の当てはめと選びのコードを写さずに読み込む（conditions.md D3）。SHA-256 が違えば止める。"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.realpath(os.path.join(HERE, "..", "..", "20261104-timeseries-tau-extend", "scripts"))
PINNED = {
    "hmm2.py": "d71f4c206789b2dd33e2acc1569ac69a75006be2d33de227f7f094456a3966bc",
    "data.py": "dd93d58b5f942e72a89c77023237eb22f9e6cfa5849aa4e318b74990f6d182e5",
    "ml.py": "93a3935cef367f1702d2aa4d51715b428945be3dd29a1962aa7aaecaaf64701c",
    "hmm_b.py": "f86cca1fd864a29998c94c8ca451f6b5d060113ce4538f10f6d3d6d02fffff8a",
}


def hashes():
    return {f: hashlib.sha256(open(os.path.join(SRC, f), "rb").read()).hexdigest() for f in PINNED}


_h = hashes()
if _h != PINNED:
    sys.exit("tau-extend のコードの SHA-256 が条件の値と違う: %r" % {f: v for f, v in _h.items() if v != PINNED[f]})
sys.path.insert(0, SRC)
import data as DT  # noqa: E402,F401
import hmm2 as H  # noqa: E402,F401
import ml  # noqa: E402,F401
