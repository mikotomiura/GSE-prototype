"""作業 = 様式の混ぜ方として、作業の切り替えの時刻が分かっている合成の記録を作る（auto-context-task-level）。

1 段目の生成器（`experiments/20261121-auto-context-segmentation/gen_synth.py`）の様式（`REGIMES`）を使う。
6〜15 分ごとに様式を入れ替え、その入れ替え方（どの様式がどれだけ出るか）を作業ごとに変える。
合成の記録は実データに混ぜない。

- `positive`: 3 つの作業を 60〜150 分ごとに切り替える（約 16 時間）。
- `negative`: 作業が 1 つ（同じ混ぜ方で様式が入れ替わる）。陽性の基準で判定すると落ちるはずの入力（= 作業の切り替えを消した入力）。

照合の経路の確かめのために、次も書く（`--out-dir` の下）。
- `diary_match.json`: 作業の記録が真の作業と一致する
- `diary_mismatch.json`: 真と無関係な区切りと名前（落ちるはず）
- `diary_few.json`: 区切りが 2 つだけ（届く p が下限に届かず、判定できないはず）
- `commits_match.json`: 作業ごとの worktree の名前で、作業の中にコミットを散らす（記述の経路）
宣言（`session_meta` の `task_kind`）は作業の始まりごとに書き、真の作業と一致させる（記述の経路）。

使い方:
    python3 -I gen_synth_task.py --kind positive --seed 20261121 --out-dir work/synth_positive
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "acs_gen_synth", HERE.parent / "20261121-auto-context-segmentation" / "gen_synth.py")
g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g1)

T0 = 1_700_000_000_000
TASKS = {
    "X": {"mix": {"typing_ja": 0.6, "editing": 0.3, "pointer": 0.1}, "task_kind": "argumentative",
          "worktree": "repo-x"},
    "Y": {"mix": {"pointer": 0.5, "switching": 0.4, "editing": 0.1}, "task_kind": "vibe_coding",
          "worktree": "repo-y"},
    "Z": {"mix": {"editing": 0.5, "switching": 0.25, "typing_ja": 0.25}, "task_kind": "other",
          "worktree": "repo-z"},
    "N": {"mix": {"typing_ja": 0.3, "pointer": 0.25, "switching": 0.2, "editing": 0.25},
          "task_kind": "other", "worktree": "repo-n"},
}
FILE_SPLIT_S = 5 * 3600  # 記録を約 5 時間ごとのファイルに分ける（作業の区切りとは揃えない）
LONG_IDLE_S = 90 * 60  # 1 回だけ挟む長い無操作（列のリセットが起きる長さ）


def plan_blocks(kind: str, rng: random.Random) -> list[tuple[str, int]]:
    if kind == "positive":
        order = ["X", "Y", "Z", "X", "Z", "Y", "X", "Y", "Z"]
    elif kind == "negative":
        order = ["N"] * 9
    else:
        raise SystemExit(f"unknown kind: {kind}")
    return [(t, rng.randint(60, 150) * 60) for t in order]


def plan_styles(blocks: list[tuple[str, int]], rng: random.Random) -> list[tuple[str, str, int]]:
    """(作業, 様式 or idle, 秒) の列。作業の中で 6〜15 分ごとに様式を引き、ときどき短い無操作を挟む。"""
    out: list[tuple[str, str, int]] = []
    for bi, (task, dur) in enumerate(blocks):
        mix = TASKS[task]["mix"]
        names, weights = zip(*mix.items())
        left = dur
        while left > 0:
            if rng.random() < 0.08:
                d = min(left, rng.randint(5, 15) * 60)
                out.append((task, "idle", d))
                left -= d
                continue
            d = min(left, rng.randint(6, 15) * 60)
            out.append((task, rng.choices(names, weights=weights)[0], d))
            left -= d
        if bi == 2:
            out.append((task, "idle", LONG_IDLE_S))
    return out


def _stamp(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y%m%d_%H%M%S")


def build(kind: str, seed: int) -> tuple[list[tuple[int, list[dict]]], dict]:
    rng = random.Random(seed)
    blocks = plan_blocks(kind, rng)
    styles = plan_styles(blocks, rng)
    files: list[tuple[int, list[dict]]] = []
    cur: list[dict] = []
    file_start = None
    t_sec = 1
    ime_on = None
    task_now = None
    truth_blocks: list[dict] = []

    def open_file(t_ms: int, task: str) -> None:
        nonlocal cur, file_start, ime_on
        if cur:
            files.append((file_start, cur))
        cur, file_start, ime_on = [], t_ms, None
        cur += [
            {"type": "meta", "session_start": t_ms, "hmm_version": "0.5.0", "app_version": "synthetic",
             "capabilities": g1.CAPABILITIES},
            {"type": "session_start", "t": t_ms},
            {"type": "session_meta", "track": "main", "task_kind": TASKS[task]["task_kind"], "monk_mode": False,
             "intervention_enabled": False, "condition": None, "label_pool": None, "head_id": "writing",
             "ts": t_ms},
        ]

    since_split = 0
    for task, style, dur in styles:
        for _ in range(dur):
            base = T0 + t_sec * 1000
            if file_start is None or since_split >= FILE_SPLIT_S:
                open_file(base, task)
                since_split = 0
            if task != task_now:
                if truth_blocks:
                    truth_blocks[-1]["end_ms"] = base
                truth_blocks.append({"task": task, "start_ms": base, "end_ms": None})
                if task_now is not None and cur[-1].get("type") != "session_meta":
                    cur.append({"type": "session_meta", "track": "main", "task_kind": TASKS[task]["task_kind"],
                                "monk_mode": False, "intervention_enabled": False, "condition": None,
                                "label_pool": None, "head_id": "writing", "ts": base})
                task_now = task
            if style != "idle":
                r = g1.REGIMES[style]
                if ime_on is not r["ime"]:
                    cur.append({"type": "ime_state", "t": base, "on": r["ime"], "active": False})
                    ime_on = r["ime"]
                n = g1._poisson(rng, r["key_rate"])
                offs = sorted(rng.randint(1, 950) for _ in range(n))
                vks, ws = zip(*r["vk_mix"])
                for o in offs:
                    vk = rng.choices(vks, weights=ws)[0]
                    cur.append({"type": "key", "t": base + o, "vk": vk, "press": True})
                    cur.append({"type": "key", "t": base + o + 40, "vk": vk, "press": False})
                if rng.random() < r["pointer_p"]:
                    cur.append({"type": "pointer_bin", "t": base + 1000, "moved": rng.randint(1, 5),
                                "buttons": rng.randint(0, 1), "wheel": 0})
                if rng.random() < r["focus_p"]:
                    cur.append({"type": "focus_transition", "t": base + rng.randint(0, 999)})
            cur.append({"type": "feat", "t": base + 999, "f1": 0, "f3": 0, "f4": 0, "f5": 0, "f6": 0,
                        "p_flow": 0.34, "p_inc": 0.33, "p_stuck": 0.33, "raw_x": 0, "raw_y": 0,
                        "ewma_x": 0, "ewma_y": 0, "obs": 0, "alpha": 0.3})
            t_sec += 1
            since_split += 1
    truth_blocks[-1]["end_ms"] = T0 + t_sec * 1000
    files.append((file_start, cur))
    for _, lines in files:
        lines.sort(key=lambda d: d.get("t", d.get("ts", d.get("session_start", 0))))
    truth = {"kind": kind, "seed": seed, "blocks": truth_blocks, "styles": [list(s) for s in styles]}
    return files, truth


def diaries(truth: dict, rng: random.Random) -> dict[str, dict]:
    blocks = truth["blocks"]
    t_start, t_end = blocks[0]["start_ms"], blocks[-1]["end_ms"]
    match = [{"start_ms": b["start_ms"], "task": f"task {b['task']}", "pc": "Mac"} for b in blocks]
    # 真と無関係: 100 分ごとに P/Q/R を順に回す（始まりを 50 分ずらす）。
    mismatch = []
    t = t_start
    names = ["P", "Q", "R"]
    i = 0
    while t < t_end:
        mismatch.append({"start_ms": t, "task": f"task {names[i % 3]}", "pc": "Mac"})
        t += (50 if i == 0 else 100) * 60_000
        i += 1
    mid = (t_start + t_end) // 2
    few = [{"start_ms": t_start, "task": "task P", "pc": "Mac"}, {"start_ms": mid, "task": "task Q", "pc": "Mac"}]
    commits = []
    for b in blocks:
        t = b["start_ms"] + rng.randint(5, 25) * 60_000
        while t < b["end_ms"]:
            commits.append({"t_ms": t, "unit": TASKS[b["task"]]["worktree"]})
            t += rng.randint(10, 40) * 60_000
    return {
        "diary_match.json": {"entries": match, "end_ms": t_end},
        "diary_mismatch.json": {"entries": mismatch, "end_ms": t_end},
        "diary_few.json": {"entries": few, "end_ms": t_end},
        "commits_match.json": {"commits": commits},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=["positive", "negative"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out-dir", required=True, type=Path)
    a = ap.parse_args()
    files, truth = build(a.kind, a.seed)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for start, lines in files:
        p = a.out_dir / f"gse_o1_{_stamp(start)}.ndjson"
        p.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
        paths.append(str(p))
    (a.out_dir / "truth.json").write_text(json.dumps(truth, indent=1) + "\n", encoding="utf-8")
    for name, doc in diaries(truth, random.Random(a.seed + 1)).items():
        (a.out_dir / name).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    (a.out_dir / "files.json").write_text(json.dumps(paths, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
