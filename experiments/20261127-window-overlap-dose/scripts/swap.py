"""S13 の fit.py・residual.py が読む "load" を、この試験の読み込み（load_dose）に差し替えてから、両方を読み込む（conditions D3）。

駆動の入口はどれも最初にこのモジュールを読み込む。macOS の spawn は子で主のモジュールの先頭を実行し直すので、
入口の先頭でここを読み込めば、差し替えは子（fit._init・ml.fit_pool_*）にも効く（selftest_dose の P-SWAP で確かめる）。
S13 の load.py が既に "load" の名で読み込まれていれば止める（差し替えが効かない）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import load_dose  # noqa: E402

if "load" in sys.modules and sys.modules["load"] is not load_dose:
    raise SystemExit("S13 の load.py が先に読み込まれている（差し替えが効かない）")
sys.modules["load"] = load_dose
import fit as F  # noqa: E402  S13 の fit.py（import load as L は load_dose を受ける）
import residual as R  # noqa: E402  S13 の residual.py
import pins  # noqa: E402
import masks  # noqa: E402

masks.kit_variants()  # kit の variants.py を読み込んでおく（P-PIN で照らす）
if F.L is not load_dose or R.L is not load_dose:
    raise SystemExit("差し替えが効いていない")
PIN = pins.check()
