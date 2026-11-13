"""D の複製の一覧と規則・分解の最頻値の評価・sens の合成と手順を写さずに読み込む（conditions.md V1 P-HASH）。
SHA-256 が違えば止める。pinned5（D）が sens の 4 つと較正を、pinned2（分解）が sens の 4 つと mode の hmm2 を照らす。
実データは読まない（m0 は fit_m0.py が別のプロセスで作る）。
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.realpath(os.path.join(HERE, "..", ".."))
TEN_DIR = os.path.join(EXP, "20261112-sensitivity-ten-seeds", "scripts")
DEC_DIR = os.path.join(EXP, "20261111-sensitivity-mode-decomposition", "scripts")
D_REPS = os.path.join(EXP, "20261112-sensitivity-ten-seeds", "results", "replicates")
MODE_SUMMARY = os.path.join(EXP, "20261106-tau-mode-candidate", "results", "summary.json")
PINNED = {
    os.path.join(TEN_DIR, "ten.py"): "0071816b5d12b73e5a6a96641c579a80830116e0a9165bc890a8fe900fea289a",
    os.path.join(TEN_DIR, "pinned5.py"): "7f8674c4fe13befe825bfbacff1309bd58234f13654f3bc8168e2783ab3b8574",
    os.path.join(DEC_DIR, "decomp.py"): "5e0f34e46ea26b91f271e9971ba443cd6024720a445201d428d22ddb51e48453",
    os.path.join(DEC_DIR, "pinned2.py"): "5ddb752fd33b550c7c6adfdb249a2cb25fa98eb2df4319228f45f4b34e12ceb9",
    MODE_SUMMARY: "b775d7cf08b9b826fac31a74a7d5048030aa67119da58e42ff19f9f358c18865",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


_bad = sorted(os.path.relpath(p, EXP) for p, v in PINNED.items() if sha(p) != v)
if _bad:
    sys.exit("読み込むコードか集計の SHA-256 が条件の値と違う: %r" % _bad)
sys.path.append(TEN_DIR)
sys.path.append(DEC_DIR)
import decomp as DC  # noqa: E402,F401
import pinned2  # noqa: E402
import pinned5  # noqa: E402
import ten as TEN  # noqa: E402,F401
from pinned2 import AN, DT, H, HM, RS, SY, ml  # noqa: E402,F401

if pinned5.SY is not SY or pinned5.RS is not RS or pinned5.ml is not ml:
    sys.exit("D と分解が別々の sens の加群を読み込んだ")


def hashes():
    h = {os.path.relpath(p, EXP): v for p, v in PINNED.items()}
    h.update({"ten-seeds:" + k: v for k, v in pinned5.hashes().items()})
    h.update({"decomp:" + k: v for k, v in pinned2.hashes().items()})
    return h
