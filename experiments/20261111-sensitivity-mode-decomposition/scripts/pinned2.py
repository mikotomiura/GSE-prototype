"""感度の合成（sens）と最頻値の試験（mode）のコードを写さずに読み込む（conditions.md D2）。SHA-256 が違えば止める。

- sens の scripts/（synth・run_synth・pinned・analysis）。sens の pinned が tau-extend の 4 つを照らす。
- mode の hmm2.py を別の名前（hmm2_mode）で読み込む。使うのは mode_of・pred_logprob_zero・Data・pred_logprob だけ。
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.realpath(os.path.join(HERE, "..", ".."))
SENS = os.path.join(EXP, "20261110-per-person-sensitivity", "scripts")
MODE_HMM2 = os.path.join(EXP, "20261106-tau-mode-candidate", "scripts", "hmm2.py")
PINNED = {
    os.path.join(SENS, "synth.py"): "41c60dd5ec954f6d1bd526560c318f96847641533e31f3826f099fb443d64ee3",
    os.path.join(SENS, "run_synth.py"): "103ad29bcae6eee2b7c95fa117906a7098399effe494203b00775b7f2d951f5f",
    os.path.join(SENS, "pinned.py"): "02317ec7174be93aa60c18a022ba411d5652cc1f97aab7fd1c0408e254ab8006",
    os.path.join(SENS, "analysis.py"): "ce20b5855bbe89cbe635f6af40e6f5993f9cb0ff3e47d8771ccd7bbfdfb3f4ef",
    MODE_HMM2: "f0e0888f8212d5887c6356b7451771370c4d3117404a304f20ecddfb156dfa0a",
}
REP_SEED = 2026111001
REP_CODE_HASH = "bff1edd9fe9a8bd3fa9e30cfff64ed86bc4abc3afdc280145ed42c7b1534c27c"


def hashes():
    return {os.path.relpath(p, EXP): hashlib.sha256(open(p, "rb").read()).hexdigest() for p in PINNED}


_bad = {os.path.relpath(p, EXP): v for p, v in PINNED.items()
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != v}
if _bad:
    sys.exit("読み込むコードの SHA-256 が条件の値と違う: %r" % sorted(_bad))
sys.path.insert(0, SENS)
import analysis as AN  # noqa: E402,F401
import pinned as PS  # noqa: E402,F401  (sens の pinned。tau-extend の 4 つを照らす)
import run_synth as RS  # noqa: E402,F401
import synth as SY  # noqa: E402,F401
from pinned import DT, H, ml  # noqa: E402,F401

_spec = importlib.util.spec_from_file_location("hmm2_mode", MODE_HMM2)
HM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(HM)
