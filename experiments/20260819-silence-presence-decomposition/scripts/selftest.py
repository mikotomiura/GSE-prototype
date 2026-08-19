#!/usr/bin/env python
"""自己検査。★ **本解析より先に回す。落ちたら結果を書かない。**

⚠️★★★ S2 / S3 を実データより先に通さないと、
「差が出なかった」と「検出器が壊れていた」が区別できない。

    S1a  再構成の正しさ（合成 NDJSON を手計算値と突き合わせる）
    S1b  窓の切り方が上流 `block_variance.window_counts()` と完全一致
    S2   H0 真  … presence と再開が独立 -> 勝ち幅が 0 近傍
    S3   H0 偽  … presence が再開を駆動 -> 勝ち幅が正
    S4   打ち切りゼロの合成データで 上界 == 下界
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(
    0,
    os.path.abspath(os.path.join(_HERE, "..", "..", "20260815-expression-power", "scripts")),
)

from block_variance import window_counts  # noqa: E402
import extract  # noqa: E402
import analyze  # noqa: E402

CFG = json.load(open(os.path.join(_HERE, "..", "config.json"), encoding="utf-8"))

FAILURES: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {detail}")
        FAILURES.append(f"{label} {detail}")


# --------------------------------------------------------------------------
# S1a: 再構成の正しさ
# --------------------------------------------------------------------------
def s1a() -> None:
    print("S1a 再構成の正しさ（手計算値との一致）")
    t0 = 1_000_000
    lines = [
        {"type": "meta", "session_start": t0, "hmm_version": "0.4.0"},
        {"type": "session_start", "t": t0},
        # --- ギャップ A: 60 秒・Suspect あり（40 秒時点）・打鍵で終了 -------------
        {"type": "key", "t": t0 + 1_000, "vk": 65, "press": True},
        {"type": "hook_health", "t": t0 + 41_000, "alive": True, "starved_ms": 30_000,
         "rehook": False, "dropped": 0},
        {"type": "hook_health", "t": t0 + 62_000, "alive": True, "starved_ms": 50_000,
         "rehook": False, "dropped": 0},  # ★ 復帰行（peak=50s）。t は gap_end の次 tick
        {"type": "key", "t": t0 + 61_000, "vk": 66, "press": True},
        # --- ギャップ B: 200 秒・Down あり（150 秒時点）・打鍵で終了 --------------
        {"type": "hook_health", "t": t0 + 95_000, "alive": True, "starved_ms": 30_000,
         "rehook": False, "dropped": 0},
        {"type": "hook_health", "t": t0 + 185_000, "alive": False, "starved_ms": 120_000,
         "rehook": True, "dropped": 0},
        {"type": "hook_health", "t": t0 + 262_000, "alive": True, "starved_ms": 190_000,
         "rehook": False, "dropped": 0},
        {"type": "key", "t": t0 + 261_000, "vk": 67, "press": True},
        # --- ギャップ C: 40 秒・hook_health 行なし（= 入力皆無）------------------
        {"type": "key", "t": t0 + 301_000, "vk": 8, "press": True},
        {"type": "meta", "session_end": t0 + 400_000},
    ]
    lines.sort(key=lambda o: o.get("t", o.get("session_start", o.get("session_end", 0))))

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "synth-a.ndjson")
        with open(p, "w", encoding="utf-8") as fh:
            for o in lines:
                fh.write(json.dumps(o) + "\n")
        out = extract.extract_file(p, "P999", 0, CFG)

    gaps = sorted(out["gaps"], key=lambda g: g["start_offset_ms"])
    check(len(gaps) == 4, "ギャップ数 = 4（A/B/C ＋ 末尾の打ち切り）", f"got {len(gaps)}")
    if len(gaps) < 3:
        return

    a, b, c = gaps[0], gaps[1], gaps[2]
    check(a["duration_ms"] == 60_000, "A の長さ = 60000ms", f"got {a['duration_ms']}")
    check(a["suspect_at_ms"] == 40_000, "A の Suspect 到達 = 40000ms", f"got {a['suspect_at_ms']}")
    check(a["down_at_ms"] is None, "A に Down は無い", f"got {a['down_at_ms']}")
    check(a["presence_ms"] == 50_000, "A の peak = 50000ms", f"got {a['presence_ms']}")
    check(a["event"] is True, "A は打鍵で終了")

    check(b["duration_ms"] == 200_000, "B の長さ = 200000ms", f"got {b['duration_ms']}")
    check(b["suspect_at_ms"] == 34_000, "B の Suspect 到達 = 34000ms", f"got {b['suspect_at_ms']}")
    check(b["down_at_ms"] == 124_000, "B の Down 到達 = 124000ms", f"got {b['down_at_ms']}")
    check(b["rehook"] is True, "B は rehook を含む")
    check(b["presence_ms"] == 190_000, "B の peak = 190000ms", f"got {b['presence_ms']}")

    check(c["duration_ms"] == 40_000, "C の長さ = 40000ms", f"got {c['duration_ms']}")
    check(c["suspect_at_ms"] is None, "C に Suspect は無い（入力皆無）", f"got {c['suspect_at_ms']}")
    check(c["presence_kind"] == "interval_censored",
          "C の presence は区間打ち切り", f"got {c['presence_kind']}")
    check(a["presence_kind"] == "exact", "A の presence は確定値", f"got {a['presence_kind']}")

    tail = gaps[3]
    check(tail["event"] is False, "末尾ギャップは右側打ち切り")

    # T0: A の直前 30 秒には打鍵が 1 件（t0+1000）だけ
    check(a["t0_keys"] == 1, "A の T0 打鍵数 = 1", f"got {a['t0_keys']}")
    # C の直前 30 秒には打鍵が 1 件（t0+261000）。vk=67 なので BS 率 0
    check(c["t0_bs_rate"] == 0.0, "C の T0 BS 率 = 0", f"got {c['t0_bs_rate']}")


# --------------------------------------------------------------------------
# S1c: ⚠️★★★ 計器が無いログを「入力皆無」と報告しない（fail-silent の固定）
# --------------------------------------------------------------------------
def s1c() -> None:
    print("S1c 計器 (hook_health) が無いログは void でなく unknown になる")
    t0 = 9_000_000
    lines = [
        {"type": "meta", "session_start": t0, "hmm_version": "0.4.0"},
        {"type": "session_start", "t": t0},
        {"type": "key", "t": t0 + 1_000, "vk": 65, "press": True},
        # ★ hook_health 行を **1 行も置かない**（= 2026-08-09 より前のログ）
        {"type": "key", "t": t0 + 121_000, "vk": 66, "press": True},
        # ★ 5 分窓が 1 つ以上完成するまで伸ばす（window_counts は欠けた最後の窓を捨てる）
        {"type": "key", "t": t0 + 400_000, "vk": 67, "press": True},
        {"type": "meta", "session_end": t0 + 700_000},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "synth-c.ndjson")
        with open(p, "w", encoding="utf-8") as fh:
            for o in lines:
                fh.write(json.dumps(o) + chr(10))
        out = extract.extract_file(p, "P997", 0, CFG)

    gaps = out["gaps"]
    check(len(gaps) >= 1, "ギャップが 1 つ以上", f"got {len(gaps)}")
    if not gaps:
        return
    g = gaps[0]
    check(g["presence_observable"] is False, "presence_observable = False")
    check(len(out["windows"]) >= 1, "5 分窓が 1 つ以上", f"got {len(out['windows'])}")
    if not out["windows"]:
        return
    w = out["windows"][0]
    check(w["silence_unknown_ms"] > 0, "沈黙時間が unknown に入る",
          f"unknown={w['silence_unknown_ms']}")
    check(w["silence_void_only_ms"] == 0,
          "⚠️ 沈黙時間を void に倒していない（= 『入力皆無だった』と誤報しない）",
          f"void={w['silence_void_only_ms']}")


# --------------------------------------------------------------------------
# S1b: 窓の切り方が上流と完全一致
# --------------------------------------------------------------------------
def s1b() -> None:
    print("S1b 窓の切り方が上流 window_counts() と一致")
    t0 = 5_000_000
    rng = np.random.default_rng(20260819)
    lines = [{"type": "meta", "session_start": t0, "hmm_version": "0.4.0"},
             {"type": "session_start", "t": t0}]
    t = t0
    for _ in range(400):
        t += int(rng.integers(100, 4_000))
        lines.append({"type": "key", "t": t, "vk": 65, "press": True})
    lines.append({"type": "meta", "session_end": t + 10_000})

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "synth-b.ndjson")
        with open(p, "w", encoding="utf-8") as fh:
            for o in lines:
                fh.write(json.dumps(o) + "\n")
        out = extract.extract_file(p, "P998", 0, CFG)
        upstream = window_counts(p, int(CFG["window_minutes"]))

    mine = [w["keydowns"] for w in out["windows"]]
    check(mine == upstream, "窓ごとの keydown 数が完全一致",
          f"mine={mine[:5]}... upstream={upstream[:5]}...")


# --------------------------------------------------------------------------
# S2 / S3: 検出器が動くか
# --------------------------------------------------------------------------
def synth_gaps(n_per_pid: int, effect: float, seed: int) -> list[dict]:
    """合成ギャップ。`effect` > 0 なら presence が再開を早める。"""
    rng = np.random.default_rng(seed)
    gaps = []
    for pid in ("P001", "P002", "P003", "P004", "P005"):
        for _ in range(n_per_pid):
            has_presence = bool(rng.integers(0, 2))
            # 基準ハザード（10 秒ビンあたり）
            h = 0.10 * (1.0 + effect if has_presence else 1.0)
            h = min(h, 0.9)
            k = 0
            while k < 200 and rng.random() > h:
                k += 1
            dur = 30_000 + (k + 1) * int(CFG["bin_ms"])
            gaps.append(
                {
                    "pid": pid,
                    "session": 0,
                    "start_offset_ms": 0,
                    "duration_ms": int(dur),
                    "event": True,
                    "suspect_at_ms": 30_000 if has_presence else None,
                    "down_at_ms": None,
                    "rehook": False,
                    "presence_ms": dur if has_presence else 0,
                    "presence_known": True,
                    "presence_kind": "exact",
                    "presence_observable": True,
                    "t0_iki_missing": 0.0,
                    "t0_burst_missing": 0.0,
                    "window_index": 0,
                    "t0_keys": float(rng.integers(0, 60)),
                    "t0_bs_rate": float(rng.random() * 0.3),
                    "t0_iki_med_ms": float(rng.integers(100, 400)),
                    "t0_burst_len": float(rng.random() * 5),
                    "t0_pause_count": float(rng.integers(0, 5)),
                }
            )
    return gaps


def delta_for(gaps: list[dict]) -> dict:
    rows = analyze.build_rows(gaps, CFG, "lower")
    return analyze.loso(rows, int(CFG["horizon_primary_ms"]))


def s2_s3() -> None:
    tol = float(CFG["selftest_null_tolerance"])
    ratio_min = float(CFG["selftest_alt_min_ratio"])

    print("S2 H0 真（presence と再開は独立）-> 勝ち幅が 0 近傍")
    r_null = delta_for(synth_gaps(120, effect=0.0, seed=101))
    d_null = r_null["delta_vs_t0_mean"]
    check(abs(d_null) < tol, f"|Δ| < {tol}", f"Δ={d_null:+.6f}")

    # ⚠️★★ **S3 に「絶対値の閾値」を置かない。**
    #   per-bin ハザードの Brier は基準率が低いと改善幅も小さくなるので、
    #   絶対値の閾値はスケール依存の恣意的な定数になる（★ 初版はそこで誤検知した）。
    #   → ★ **尺度に依存しない 2 条件**にする:
    #     (i)  5 名すべてで符号が正（検出器が偶然でなく応答している）
    #     (ii) 帰無の |Δ| の ratio_min 倍以上
    print("S3 H0 偽（presence が再開を駆動）-> 勝ち幅が正・符号が全員一致")
    r_alt = delta_for(synth_gaps(120, effect=4.0, seed=202))
    d_alt = r_alt["delta_vs_t0_mean"]
    n_pos = r_alt["delta_vs_t0_n_positive"]
    n_par = r_alt["n_participants"]
    check(n_pos == n_par, f"全 {n_par} 名で Δ > 0", f"positive={n_pos}/{n_par}")
    check(
        d_alt > ratio_min * abs(d_null),
        f"Δ_alt > {ratio_min} × |Δ_null|",
        f"Δ_alt={d_alt:+.6f} |Δ_null|={abs(d_null):.6f}",
    )


# --------------------------------------------------------------------------
# S4: 打ち切りゼロなら上界 == 下界
# --------------------------------------------------------------------------
def s4b() -> None:
    """★ `standardize()` のアフィン不変性は「時間ダミー 3 本が全行を分割する」ことに依存する。

    ⚠️ 将来 `build_rows()` の区分定義を変えるとこの前提が黙って崩れる（code-reviewer LOW）。
    """
    print("S4b 時間区分ダミー 3 本が全行をちょうど 1 つずつ被覆する")
    gaps = synth_gaps(20, effect=0.5, seed=404)
    rows = analyze.build_rows(gaps, CFG, "lower")
    X = rows["X"]
    ok = X.shape[0] > 0 and bool(np.allclose(X[:, :3].sum(axis=1), 1.0))
    check(ok, "時間ダミーの行和がすべて 1",
          f"rows={X.shape[0]} sums={set(X[:, :3].sum(axis=1).tolist()) if X.shape[0] else 'n/a'}")


def s5_codex() -> None:
    """★ `/cross-review`（Codex）が指摘した 3 つの境界を固定する。

    ⚠️ 指摘は「本コホートでは発火しない」が **構造としては実在**したものなので、
    再発防止のテストを置く（★ 直したことを忘れて戻さないため）。
    """
    print("S5 cross-review 指摘の境界（presence 上限 / 露出ゼロ / results 生成）")

    # (1) presence_ms は duration を超えない
    t0 = 3_000_000
    lines = [
        {"type": "meta", "session_start": t0, "hmm_version": "0.4.0"},
        {"type": "session_start", "t": t0},
        {"type": "key", "t": t0 + 1_000, "vk": 65, "press": True},
        {"type": "key", "t": t0 + 61_000, "vk": 66, "press": True},
        # ★ 復帰行が **ギャップ長 (60s) を超える peak (63s)** を報告するケース
        {"type": "hook_health", "t": t0 + 62_000, "alive": True, "starved_ms": 63_000,
         "rehook": False, "dropped": 0},
        {"type": "key", "t": t0 + 400_000, "vk": 67, "press": True},
        {"type": "meta", "session_end": t0 + 700_000},
    ]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "synth-d.ndjson")
        with open(p, "w", encoding="utf-8") as fh:
            for o in lines:
                fh.write(json.dumps(o) + chr(10))
        out = extract.extract_file(p, "P996", 0, CFG)
    bad = [g for g in out["gaps"] if g["presence_ms"] > g["duration_ms"]]
    check(not bad, "presence_ms が duration_ms を超えない",
          f"違反 {len(bad)} 件")

    # (2) duration == gap_min ちょうどは露出ゼロとして数えられる
    g30 = dict(synth_gaps(1, effect=0.0, seed=1)[0])
    g30["duration_ms"] = int(CFG["gap_min_ms"])
    rows = analyze.build_rows([g30], CFG, "lower")
    check(rows["n_gaps_zero_exposure"] == 1,
          "duration == gap_min は露出ゼロとして計上される",
          f"got {rows['n_gaps_zero_exposure']}")

    # (3) run.sh が results/ を作る
    run_sh = io.open(os.path.join(_HERE, "..", "run.sh"), encoding="utf-8").read()
    check("mkdir -p results" in run_sh, "run.sh が results/ を作る")


def s4() -> None:
    print("S4 打ち切りゼロの合成データで 上界 == 下界")
    gaps = synth_gaps(40, effect=0.8, seed=303)  # ★ すべて event=True
    lo = analyze.build_rows(gaps, CFG, "lower")
    up = analyze.build_rows(gaps, CFG, "upper")
    same_rows = lo["X"].shape == up["X"].shape and np.array_equal(lo["X"], up["X"])
    same_y = np.array_equal(lo["y"], up["y"])
    check(same_rows and same_y, "行列と目的変数が完全一致",
          f"lower={lo['X'].shape} upper={up['X'].shape}")


def main() -> int:
    print("== 自己検査 (silence-presence-decomposition) ==")
    s1a()
    s1b()
    s1c()
    s2_s3()
    s4()
    s4b()
    s5_codex()
    print()
    if FAILURES:
        print(f"!! {len(FAILURES)} 件失敗:")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("全項目 ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
