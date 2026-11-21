"""1 段目（`experiments/20261121-auto-context-segmentation/`）を読み出すだけの橋渡し（auto-context-task-level）。

1 段目のファイルは書き換えない。1 段目の `config.json`・`SEED` もそのまま使う（判断 7・design.md）。
人ごとのファイルを窓に集めて時刻の順につなぎ、1 段目の様式の名前（平滑化の前と後）を返す。
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STAGE1_DIR = HERE.parent / "20261121-auto-context-segmentation"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# 1 段目の evaluate.py は `import acs_core` を行うので、先に 1 段目のディレクトリを path に足す。
sys.path.insert(0, str(STAGE1_DIR))
core = _load("acs_core", STAGE1_DIR / "acs_core.py")
ev1 = _load("acs_evaluate", STAGE1_DIR / "evaluate.py")


@dataclass
class Person:
    win: "core.Windows"
    seams: np.ndarray  # 長さ m + 1
    decl: list  # 窓ごとの宣言（None = 無し）
    state: list  # 窓ごとの推定状態（None = 無し）
    res: "core.Result"  # 1 段目の結果（raw_labels・labels・gmm_k）
    relative_files: int
    overlap: dict


def stage1_config() -> dict:
    return ev1.load_config()


def load_person(pid: str, files: list[Path], work: Path) -> Person:
    """1 段目の `evaluate_person` の前半（窓に集める・相対時刻の置き直し・つなぐ）と同じ手順。"""
    cfg = stage1_config()
    parts = []
    relative_files = 0
    cursor = None
    for f in sorted(files, key=ev1.file_order_key):
        env = work / pid / (f.stem + ".features.json")
        try:
            ev1.run_features(f, env)
            w = core.make_windows(core.load_envelope(env), cfg["window_s"])
        finally:
            env.unlink(missing_ok=True)  # 封筒は大きく、共有しない中間成果物なので残さない
        side = ev1.read_side(f)
        if len(w.start_ms) and int(w.start_ms[0]) < ev1.RELATIVE_EPOCH_LIMIT_MS:
            relative_files += 1
            offset = (cursor + ev1.RELATIVE_GAP_MS if cursor is not None else ev1.RELATIVE_EPOCH_LIMIT_MS) \
                - int(w.start_ms[0])
            w, side = ev1.shift_windows(w, offset), ev1.shift_side(side, offset)
        if len(w.end_ms):
            cursor = int(w.end_ms[-1]) if cursor is None else max(cursor, int(w.end_ms[-1]))
        parts.append((w, ev1.per_window_decl(w, side["decl"]), ev1.per_window_state(w, side["feats"])))
    side_by_start: dict[int, tuple] = {}
    for w, d, st in parts:
        for i, s0 in enumerate(w.start_ms):
            side_by_start[int(s0)] = (d[i], st[i])
    win, seams, overlap = core.concat_windows([w for w, *_ in parts])
    decl = [side_by_start[int(s0)][0] for s0 in win.start_ms]
    state = [side_by_start[int(s0)][1] for s0 in win.start_ms]
    res = core.segment_person(win, cfg, cfg["seed"], seams)
    return Person(win, seams, decl, state, res, relative_files, overlap)
