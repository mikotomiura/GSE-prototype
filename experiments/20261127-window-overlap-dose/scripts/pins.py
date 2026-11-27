"""読み込むコードの SHA-256 を照らす（conditions D3・V1 P-PIN）。

照らすのは実際に読み込んだモジュールの __file__（決め打ちのパスではない）。S13 の fit.py・residual.py・load.py・pinned.py と、
pinned.py が読む tau-extend の hmm2.py・data.py・ml.py と、kit の variants.py。
tau-extend の 3 つは S13 の pinned.py も自分で照らす（外れれば終了コード 4）。ここではそれに加えて全部を同じ表で照らす。
外れれば終了コード 4 で止める（PIN_REPORT_ONLY=1 のときは止めずに結果だけを返す）。
"""
import hashlib
import os
import sys

PIN = {
    "S13/fit.py": "1a385200648e494edaaf0faf455f9b459a8a3aa454a3fac6fe37ec26e37c4a0c",
    "S13/residual.py": "fe805fbbd504a2d204e50c39b29171340dc08087a459f7709844d029665b1017",
    "S13/load.py": "d1daf1532caff1a192ac10d8e5e14caa41cde5587f386638e6cacf236573f092",
    "S13/pinned.py": "60dcf6b0b6519208421eab087d14903e84b908e148460e29f1c3df0d86bcb5fb",
    "tau/hmm2.py": "d71f4c206789b2dd33e2acc1569ac69a75006be2d33de227f7f094456a3966bc",
    "tau/data.py": "dd93d58b5f942e72a89c77023237eb22f9e6cfa5849aa4e318b74990f6d182e5",
    "tau/ml.py": "93a3935cef367f1702d2aa4d51715b428945be3dd29a1962aa7aaecaaf64701c",
    "kit/variants.py": "8910312a2c9b067490ac1d746495feccc4b3b74688fc00a46456660130437807",
}


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def loaded_files():
    """読み込まれたモジュールの __file__（読み込んでいないものは None）。"""
    m = sys.modules
    get = lambda n: getattr(m.get(n), "__file__", None)  # noqa: E731
    return {"S13/fit.py": get("fit"), "S13/residual.py": get("residual"), "S13/load.py": get("load13"),
            "S13/pinned.py": get("pinned"), "tau/hmm2.py": get("hmm2"), "tau/data.py": get("data"), "tau/ml.py": get("ml"),
            "kit/variants.py": get("variants")}


def check(exit_on_fail=True):
    files = loaded_files()
    got = {k: (sha(p) if p else None) for k, p in files.items()}
    ok = all(got[k] == v for k, v in PIN.items())
    if not ok and exit_on_fail and os.environ.get("PIN_REPORT_ONLY") != "1":
        sys.stderr.write("P-PIN: 読み込んだファイルの SHA-256 が条件の値と違う: %s\n"
                         % ", ".join(k for k in PIN if got[k] != PIN[k]))
        sys.exit(4)
    return dict(pin_ok=ok, loaded_sha256=got, loaded_from={k: (os.path.relpath(p, os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "../../..")) if p else None) for k, p in files.items()})
