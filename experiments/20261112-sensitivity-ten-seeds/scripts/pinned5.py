"""感度の合成（sens）のコードと較正を写さずに読み込む（conditions.md D1・D2）。SHA-256 が違えば止める。"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SENS = os.path.realpath(os.path.join(HERE, "..", "..", "20261110-per-person-sensitivity"))
SRC = os.path.join(SENS, "scripts")
CALIB = os.path.join(SENS, "results", "calibration.json")
SENS_REPS = os.path.join(SENS, "results", "replicates")
PINNED = {
    "synth.py": "41c60dd5ec954f6d1bd526560c318f96847641533e31f3826f099fb443d64ee3",
    "run_synth.py": "103ad29bcae6eee2b7c95fa117906a7098399effe494203b00775b7f2d951f5f",
    "pinned.py": "02317ec7174be93aa60c18a022ba411d5652cc1f97aab7fd1c0408e254ab8006",
    "analysis.py": "ce20b5855bbe89cbe635f6af40e6f5993f9cb0ff3e47d8771ccd7bbfdfb3f4ef",
}
CALIB_SHA = "d8c8c55f05e03f70e6c44b49789af4b46c95f3d6f99bcd570851a8bb2fe3f18d"
SENS_SEED = 2026111001
SENS_CODE_HASH = "bff1edd9fe9a8bd3fa9e30cfff64ed86bc4abc3afdc280145ed42c7b1534c27c"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hashes():
    h = {f: sha(os.path.join(SRC, f)) for f in PINNED}
    h["results/calibration.json"] = sha(CALIB)
    return h


_h = hashes()
_want = dict(PINNED, **{"results/calibration.json": CALIB_SHA})
if _h != _want:
    sys.exit("sens のコードか較正の SHA-256 が条件の値と違う: %r" % sorted(f for f in _h if _h[f] != _want[f]))
_c = json.load(open(CALIB))
if _c.get("seed") != SENS_SEED or _c.get("code_hash") != SENS_CODE_HASH:
    sys.exit("sens の calibration.json の seed か code_hash が条件の値と違う")
sys.path.append(SRC)  # 自分の scripts を先に（同じ名前の selftest.py などに影されない・レビュー LOW 11）
import analysis as AN  # noqa: E402,F401
import run_synth as RS  # noqa: E402,F401
import synth as SY  # noqa: E402,F401
from pinned import ml  # noqa: E402,F401


def calibration():
    return {int(k): v for k, v in _c["cal"].items()}
