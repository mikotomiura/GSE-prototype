"""P-PIN の探り: pinned.py を読み込み、読み込んだ 3 ファイルの SHA-256 が条件の値と一致すれば 0 で終わる（違えば pinned が 4 で止める）。

使い方: TAU_SCRIPTS=<読み込む元> python3 -I pin_probe.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinned  # noqa: E402

print(json.dumps(dict(pin_ok=pinned.PIN_OK, loaded_from=os.path.basename(pinned.TAU))))
sys.exit(0 if pinned.PIN_OK else 4)
