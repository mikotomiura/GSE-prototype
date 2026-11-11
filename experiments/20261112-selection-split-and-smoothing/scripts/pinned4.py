"""最頻値の試験（mode）のコードと summary を写さずに読み込む（conditions.md D1）。SHA-256 が違えば止める。"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.realpath(os.path.join(HERE, "..", "..", "20261106-tau-mode-candidate", "scripts"))
MODE_SUMMARY = os.path.realpath(os.path.join(HERE, "..", "..", "20261106-tau-mode-candidate", "results", "summary.json"))
PINNED = {
    "ml.py": "1cf816f8148066c5135867306fd5a8bc129b9dfc0e0705a158f9728cac47d265",
    "hmm2.py": "f0e0888f8212d5887c6356b7451771370c4d3117404a304f20ecddfb156dfa0a",
    "data.py": "dd93d58b5f942e72a89c77023237eb22f9e6cfa5849aa4e318b74990f6d182e5",
    "hmm_b.py": "f86cca1fd864a29998c94c8ca451f6b5d060113ce4538f10f6d3d6d02fffff8a",
}
MODE_SUMMARY_SHA = "b775d7cf08b9b826fac31a74a7d5048030aa67119da58e42ff19f9f358c18865"
SEED = 2026110401


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hashes():
    h = {f: sha(os.path.join(SRC, f)) for f in PINNED}
    h["results/summary.json"] = sha(MODE_SUMMARY)
    return h


_h = hashes()
_want = dict(PINNED, **{"results/summary.json": MODE_SUMMARY_SHA})
if _h != _want:
    sys.exit("mode のコードか summary の SHA-256 が条件の値と違う: %r" % sorted(f for f in _h if _h[f] != _want[f]))
sys.path.append(SRC)  # 自分の scripts を先に（同じ名前の selftest.py などに影されない・レビュー LOW 11）
import hmm2 as H  # noqa: E402,F401
import ml  # noqa: E402,F401
