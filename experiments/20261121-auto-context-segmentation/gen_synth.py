"""陽性対照・陰性対照の合成の記録を作る（auto-context-segmentation）。

切り替えの時刻と文脈が分かっている NDJSON を作り、真の値を別の JSON に書く。
合成の記録は実データに混ぜない（`.steering/20261121-auto-context-segmentation/decisions.md` 判断 2）。

- `positive`: 4 種類の文脈を既知の時刻で切り替える。途中に長い無操作を 1 回挟む。
- `negative`: 1 種類の文脈だけ（境界は無操作の 1 回だけ）。陽性の基準で判定すると落ちるはずの入力
  （= 境界を消した入力）として使う。

使い方:
    python3 -I gen_synth.py --kind positive --seed 20261121 --out-ndjson X.ndjson --out-truth X.truth.json
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

T0 = 1_700_000_000_000
CAPABILITIES = {
    "unconditional": ["feat", "ime_state", "key", "paste", "recording_pause", "review_marker",
                      "session_meta", "session_start", "user_label", "vignette_response"],
    "threshold_gated": ["hook_health", "starve_window"],
    "config_gated": ["focus_transition", "ime_shadow", "intervention_decision", "intervention_response",
                     "pointer_bin", "probe_assignment", "realtime_label", "secure_input"],
}

# 文脈ごとの 1 秒あたりの振る舞い。
#   key_rate: 1 秒あたりの press の期待値 / vk_mix: (vk, 重み) / ime: IME モード
#   pointer_p: その秒にポインタの活動がある確率 / focus_p: その秒にフォーカス遷移がある確率
REGIMES = {
    "typing_ja": {"key_rate": 4.0, "vk_mix": [(0x41, 70), (0x20, 15), (0x0D, 3), (0x08, 7), (0xBE, 5)],
                  "ime": True, "pointer_p": 0.03, "focus_p": 0.002},
    "pointer": {"key_rate": 0.2, "vk_mix": [(0x28, 40), (0x26, 30), (0x0D, 30)],
                "ime": False, "pointer_p": 0.85, "focus_p": 0.02},
    "switching": {"key_rate": 1.0, "vk_mix": [(0x41, 40), (0xA2, 30), (0x09, 20), (0x0D, 10)],
                  "ime": False, "pointer_p": 0.35, "focus_p": 0.12},
    "editing": {"key_rate": 2.5, "vk_mix": [(0x41, 45), (0x08, 20), (0x25, 10), (0x27, 10), (0xBA, 10),
                                             (0x09, 5)],
                "ime": False, "pointer_p": 0.08, "focus_p": 0.005},
}


def _poisson(rng: random.Random, lam: float) -> int:
    # Knuth（小さい λ だけを使う）。
    import math

    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def build(kind: str, seed: int, task_kind: str = "argumentative", start_offset_min: int = 0,
          only: str | None = None, minutes: int = 40) -> tuple[list[dict], dict]:
    """`only` を渡すと、その 1 つの文脈だけで 40 分の記録を作る（宣言の照合の経路を通す確かめ用）。"""
    rng = random.Random(seed)
    t0 = T0 + start_offset_min * 60_000
    if only is not None:
        plan = [(only, minutes * 60)]
    elif kind == "positive":
        names = ["typing_ja", "pointer", "switching", "editing"]
        plan: list[tuple[str, int]] = []
        for rep in range(3):
            order = names[:]
            rng.shuffle(order)
            for nm in order:
                plan.append((nm, rng.randint(8, 16) * 60))
            if rep == 0:
                plan.append(("idle", 7 * 60))
    elif kind == "negative":
        plan = [("editing", 40 * 60), ("idle", 7 * 60), ("editing", 40 * 60)]
    else:
        raise SystemExit(f"unknown kind: {kind}")

    lines: list[dict] = [
        {"type": "meta", "session_start": t0, "hmm_version": "0.5.0", "app_version": "synthetic",
         "capabilities": CAPABILITIES},
        {"type": "session_start", "t": t0},
        {"type": "session_meta", "track": "main", "task_kind": task_kind, "monk_mode": False,
         "intervention_enabled": False, "condition": None, "label_pool": None, "head_id": "writing",
         "ts": t0},
    ]
    truth_segments = []
    t_sec = 1
    ime_on = None
    for nm, dur in plan:
        seg_start = t0 + t_sec * 1000
        for _ in range(dur):
            base = t0 + t_sec * 1000
            if nm != "idle":
                r = REGIMES[nm]
                if ime_on is not r["ime"]:
                    lines.append({"type": "ime_state", "t": base, "on": r["ime"], "active": False})
                    ime_on = r["ime"]
                n = _poisson(rng, r["key_rate"])
                offs = sorted(rng.randint(1, 950) for _ in range(n))
                vks, ws = zip(*r["vk_mix"])
                for o in offs:
                    vk = rng.choices(vks, weights=ws)[0]
                    lines.append({"type": "key", "t": base + o, "vk": vk, "press": True})
                    lines.append({"type": "key", "t": base + o + 40, "vk": vk, "press": False})
                if rng.random() < r["pointer_p"]:
                    lines.append({"type": "pointer_bin", "t": base + 1000, "moved": rng.randint(1, 5),
                                  "buttons": rng.randint(0, 1), "wheel": 0})
                if rng.random() < r["focus_p"]:
                    lines.append({"type": "focus_transition", "t": base + rng.randint(0, 999)})
            # feat 行は 1 秒ごと（idle を含む）。p_* は文脈と無関係な一定値にする。
            lines.append({"type": "feat", "t": base + 999, "f1": 0, "f3": 0, "f4": 0, "f5": 0, "f6": 0,
                          "p_flow": 0.34, "p_inc": 0.33, "p_stuck": 0.33, "raw_x": 0, "raw_y": 0,
                          "ewma_x": 0, "ewma_y": 0, "obs": 0, "alpha": 0.3})
            t_sec += 1
        truth_segments.append({"context": nm, "start_ms": seg_start, "end_ms": t0 + t_sec * 1000})

    lines.sort(key=lambda d: d.get("t", d.get("ts", d.get("session_start", 0))))
    truth = {"kind": kind, "seed": seed, "segments": truth_segments}
    return lines, truth


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=["positive", "negative"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out-ndjson", required=True, type=Path)
    ap.add_argument("--out-truth", required=True, type=Path)
    ap.add_argument("--task-kind", default="argumentative")
    ap.add_argument("--start-offset-min", type=int, default=0)
    ap.add_argument("--only", choices=sorted(REGIMES))
    ap.add_argument("--minutes", type=int, default=40, help="--only のときの長さ（分）")
    a = ap.parse_args()
    lines, truth = build(a.kind, a.seed, a.task_kind, a.start_offset_min, a.only, a.minutes)
    a.out_ndjson.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
    a.out_truth.write_text(json.dumps(truth, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
