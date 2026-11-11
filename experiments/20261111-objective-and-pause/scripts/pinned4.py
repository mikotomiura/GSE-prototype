"""計算 3（sel）のコードを写さずに読み込む（conditions.md D1）。SHA-256 が違えば止める。
sel は pinned3 を通して mode の ml.py・hmm2.py・data.py・hmm_b.py と mode の summary.json を照らす。"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEL_DIR = os.path.realpath(os.path.join(HERE, "..", "..", "20261111-mode-in-selection", "scripts"))
SEL_SUMMARY = os.path.realpath(os.path.join(HERE, "..", "..", "20261111-mode-in-selection", "results", "summary.json"))
PINNED = {
    "sel.py": "68772f23418703d5727da5c60993788c0f3c4638ab731eb2185ab866d5372a39",
    "pinned3.py": "72c8ad1dc4e785d4a4c0ecc9efbcdc84dcb0ab2fc17262d9a3f083fff406573c",
}
SEL_SUMMARY_SHA = "bd80a809018759cf353e3a677245297d3e27aadd2cdadfcdd4f0cd5e1b9b1b1a"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hashes():
    h = {f: sha(os.path.join(SEL_DIR, f)) for f in PINNED}
    h["sel/results/summary.json"] = sha(SEL_SUMMARY)
    return h


_h = hashes()
_want = dict(PINNED, **{"sel/results/summary.json": SEL_SUMMARY_SHA})
if _h != _want:
    sys.exit("計算 3 のコードか summary の SHA-256 が条件の値と違う: %r" % sorted(f for f in _h if _h[f] != _want[f]))
sys.path.insert(0, SEL_DIR)
import pinned3  # noqa: E402,F401  （mode のハッシュを照らす）
import sel as SEL  # noqa: E402,F401
from pinned3 import H, ml  # noqa: E402,F401

SEED = pinned3.SEED


def all_hashes():
    return dict(hashes(), **{"mode/" + k: v for k, v in pinned3.hashes().items()})
