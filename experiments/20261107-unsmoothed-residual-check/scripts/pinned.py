"""tau-extend の数式のコード（hmm2.py・data.py・ml.py）を写さずに読み込み、SHA-256 を照らす（conditions D3・P-PIN）。

読み込んだモジュールの __file__ のハッシュを照らす（決め打ちのパスではなく、実際に読み込んだファイル）。
外れれば止める（終了コード 4）。TAU_SCRIPTS で読み込む元を替えられる（selftest の m51 が 1 バイト変えた写しを渡す）。
ml.py は読み込み時に自分のディレクトリを sys.path の頭に入れるので、読み込みの後に外して末尾に置き直す
（この実験の report.py・repro_check.py・selftest.py が tau-extend の同名のファイルに隠れないように）。
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.realpath(os.path.join(HERE, "../../20261104-timeseries-tau-extend/scripts"))
TAU = os.path.realpath(os.environ.get("TAU_SCRIPTS", DEFAULT))
PIN = {
    "hmm2.py": "d71f4c206789b2dd33e2acc1569ac69a75006be2d33de227f7f094456a3966bc",
    "data.py": "dd93d58b5f942e72a89c77023237eb22f9e6cfa5849aa4e318b74990f6d182e5",
    "ml.py": "93a3935cef367f1702d2aa4d51715b428945be3dd29a1962aa7aaecaaf64701c",
}


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


if HERE not in sys.path:
    sys.path.insert(0, HERE)
sys.path.insert(1, TAU)
import data as DT  # noqa: E402
import hmm2 as H  # noqa: E402
import hmm_b  # noqa: E402
import ml  # noqa: E402

sys.path[:] = [p for p in sys.path if os.path.realpath(p) != TAU] + [TAU]
if sys.path[0] != HERE:
    sys.path.remove(HERE)
    sys.path.insert(0, HERE)

LOADED = {"hmm2.py": H.__file__, "data.py": DT.__file__, "ml.py": ml.__file__}
SHA = {k: sha(p) for k, p in LOADED.items()}
SHA["hmm_b.py"] = sha(hmm_b.__file__)  # 固定の対象ではない（記録だけ）
PIN_OK = all(SHA[k] == v for k, v in PIN.items()) and all(
    os.path.realpath(os.path.dirname(p)) == TAU for p in LOADED.values())
if not PIN_OK and os.environ.get("PIN_REPORT_ONLY") != "1":
    sys.stderr.write("P-PIN: 読み込んだ tau-extend のファイルの SHA-256 が条件の値と違う\n")
    sys.exit(4)
