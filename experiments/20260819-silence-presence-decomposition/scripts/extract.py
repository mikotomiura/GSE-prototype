#!/usr/bin/env python
"""NDJSON -> 沈黙ギャップ表 ＋ 5 分窓の時間内訳（L1 / L2 の素材）。

★ 本スクリプトは **モデルを一切当てない**。測った量だけを出す。
⚠️★★★ 出力に **ファイル名・絶対パス・OS ユーザー名を 1 つも書かない**
（`data-privacy` / S5C-D8 / `expression-power` の security-checker M1）。
参加者は `pid`（`P0nn`）、セッションは **整数の連番**でのみ識別する。

## 測定の原理（`preregistration.md §1`）

`src-tauri/src/input/liveness.rs:86-103` の `step()`:

    !session_active || hook_event_seen  -> starved_ms = 0      (打鍵でリセット)
    !system_input_seen                  -> 凍結 (prev のまま)   (入力皆無)
    それ以外                             -> starved_ms += tick  (在席×非打鍵)

→ `starved_ms` = 「沈黙のあいだ入力デバイスに触れていた累積時間」。

`src-tauri/src/lib.rs:2923` が `if health == prev_health && !rehook { continue; }` で
間引くので、NDJSON に出る `hook_health` 行は 3 種類だけ:

    alive=true , starved_ms≈30000  … Suspect 到達 (30 秒)
    alive=false, starved_ms≈120000 … Down 到達 (120 秒) ＋ rehook=true
    alive=true , starved_ms=peak   … 打鍵で閉じた復帰行 (peak を搬送)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# ★ 窓抽出は既存実装を再利用する（切り方を再発明して差が出ると上流と比較できない）。
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(
    0,
    os.path.abspath(os.path.join(_HERE, "..", "..", "20260815-expression-power", "scripts")),
)
from block_variance import window_counts, _input_manifest  # noqa: E402

TICK_MS = 1000  # src-tauri/src/lib.rs:2832 `const TICK_MS: u64 = 1000;`
# 復帰行はギャップ終端の「次の tick」で出る。★ 余裕を見て 3 tick まで探す。
RECOVERY_SEARCH_MS = 3 * TICK_MS

PROBE_TYPES = ("probe_assignment", "realtime_label", "vignette_response")


def is_backspace(vk: int) -> bool:
    """`src-tauri/src/bin/replay.rs:428` の逐語複製 (Windows 規約)。"""
    return vk == 0x08 or vk == 0x2E


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_records(path: str) -> dict:
    """1 ファイルを 1 パスで読み、必要なレコードだけを取り出す。

    ★ `window_counts()` と **同じ t0 規約**を使う (`meta.session_start` があればそれ、
    無ければ最初の `t`)。⚠️ ここがずれると窓が 1 つずれて上流と比較できない。
    """
    t0 = None
    last_t = None
    session_end = None
    presses: list[tuple[int, int]] = []  # (t, vk)
    health: list[dict] = []
    session_starts: list[int] = []
    probes: list[int] = []

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            typ = o.get("type")
            if typ == "meta":
                if t0 is None and o.get("session_start") is not None:
                    t0 = o.get("session_start")
                if o.get("session_end") is not None:
                    session_end = o.get("session_end")
                continue
            t = o.get("t")
            if t is None:
                continue
            if t0 is None:
                t0 = t
            last_t = t
            if typ == "key":
                if o.get("press") is True:
                    presses.append((int(t), int(o.get("vk", -1))))
            elif typ == "hook_health":
                health.append(
                    {
                        "t": int(t),
                        "alive": bool(o.get("alive", True)),
                        "starved_ms": int(o.get("starved_ms", 0)),
                        "rehook": bool(o.get("rehook", False)),
                        "dropped": int(o.get("dropped", 0)),
                    }
                )
            elif typ == "session_start":
                session_starts.append(int(t))
            elif typ in PROBE_TYPES:
                probes.append(int(t))

    return {
        "t0": t0,
        "last_t": last_t,
        "session_end": session_end,
        "presses": presses,
        "health": health,
        "session_starts": session_starts,
        "probes": probes,
    }


def t0_features(presses: list[tuple[int, int]], gap_start: int, cfg: dict) -> dict:
    """沈黙ギャップ直前 `t0_lookback_ms` の打鍵統計 (= T0 基線の共変量)。

    ⚠️★★★ `feat` 行の `keys` / `bs_keys` は **使わない**。
    Tier 0 配線は 2026-08-16 で、Phase1 コホートのログは**それ以前**である
    (`personalization-and-online-learning.md §5.2` 逐語「旧 NDJSON には本フィールドが無い」)。
    → `key` 行から直接数え直す。
    """
    lo = gap_start - int(cfg["t0_lookback_ms"])
    win = [(t, vk) for (t, vk) in presses if lo <= t <= gap_start]
    n = len(win)
    n_bs = sum(1 for (_, vk) in win if is_backspace(vk))
    ikis = [win[i][0] - win[i - 1][0] for i in range(1, n)]

    if ikis:
        s = sorted(ikis)
        m = len(s)
        iki_med = float(s[m // 2]) if m % 2 == 1 else (s[m // 2 - 1] + s[m // 2]) / 2.0
    else:
        iki_med = 0.0

    # バースト長 = 連続 FT < burst_gap_ms の平均文字数 (F4 と同じ考え方)
    burst_gap = int(cfg["t0_burst_gap_ms"])
    bursts: list[int] = []
    run = 1
    for d in ikis:
        if d < burst_gap:
            run += 1
        else:
            bursts.append(run)
            run = 1
    if n > 0:
        bursts.append(run)
    burst_len = (sum(bursts) / len(bursts)) if bursts else 0.0

    pause_ms = int(cfg["t0_pause_ms"])
    n_pause = sum(1 for d in ikis if d >= pause_ms)

    # ⚠️★★★ **欠測を 0 に倒さない**（code-reviewer HIGH）。
    #   打鍵 1 件以下では IKI が定義できず、`0.0` は「無限に速い打鍵」＝ 尺度の速い端と衝突する。
    #   ★ **長い沈黙の直後のギャップほど T0 が壊れる**ので、そのまま入れると
    #   **提案（presence）が勝ちやすい方向のバイアス**になる。
    # → ★ **指示変数を立て、値は 0 のまま置く。**
    #   ⚠️ 旧コメントは「下流が train fold の中央値で埋める」と書いていたが
    #   **`analyze.py` はそれをしていなかった**（宣言と実装の矛盾・codex cross-review 中）。
    #   ★ **補完は不要である**: 罰則なし線形モデルでは、欠測時の値が**定数**（ここでは 0）なら
    #   `β_value·0 + β_ind·1 = β_ind` となり、指示変数が欠測行の切片を自由に吸収する。
    #   ＝ **中央値補完と予測が厳密に一致する**。→ 実装を変えず、コメントを事実へ直した。
    return {
        "t0_keys": n,
        "t0_bs_rate": (n_bs / n) if n else 0.0,
        "t0_bs_rate_missing": 1.0 if n == 0 else 0.0,
        "t0_iki_med_ms": iki_med,
        "t0_iki_missing": 1.0 if not ikis else 0.0,
        "t0_burst_len": burst_len,
        "t0_burst_missing": 1.0 if n == 0 else 0.0,
        "t0_pause_count": n_pause,
    }


def gap_presence(health: list[dict], gap_start: int, gap_end: int, cfg: dict) -> dict:
    """1 ギャップの presence を `hook_health` 行から再構成する。

    戻り値:
      suspect_t   … Suspect (30 秒) 到達の**時刻**。無ければ None
      down_t      … Down (120 秒) 到達の**時刻**。無ければ None
      rehook      … このギャップ中に測定器がフックを再設置したか
      dropped_any … `dropped > 0` の行があったか (除外規則 E3)
      presence_ms … 在席×非打鍵の累積時間。復帰行の peak を優先
      presence_known … presence_ms が確定値か (False なら [0, suspect_ms) の区間打ち切り)
    """
    suspect_ms = int(cfg["suspect_ms"])
    down_ms = int(cfg["down_ms"])

    # ⚠️★★★ **前のギャップの復帰行が次のギャップに漏れ込む**（自己検査 S1a が検出）。
    #   復帰行はギャップ終端の次の tick に出るので、直後のギャップの内側に落ちる。
    # → ★ **物理制約で弾く**: `starved_ms = S` を報告する行は `t - S` から積み始めている。
    #   `t - gap_start < S` なら、その starvation エピソードは**このギャップより前に始まっている**
    #   ＝ このギャップのものではない。
    in_span = [h for h in health if gap_start < h["t"] < gap_end]
    inside = [h for h in in_span if (h["t"] - gap_start) >= h["starved_ms"]]
    rejected = len(in_span) - len(inside)
    suspect_t = None
    down_t = None
    rehook = False
    dropped_any = False
    max_inside = 0

    # ⚠️★★★ **`dropped` は累積カウンタである**（`hook.rs:140` の `EVENTS_DROPPED: AtomicU64` を
    #   `lib.rs:2883` がそのまま搬送する）。★ `> 0` で判定すると「起動以降に一度でも落ちた」を
    #   「このギャップで落ちた」と読み違え、**最初の drop 以降の `hook_health` 行を持つギャップ**
    #   ＝ presence の高いギャップだけを系統的に除外してしまう（code-reviewer HIGH）。
    # → ★ **直前の行との差分**で判定する。
    prev_dropped = None
    for h in health:
        if h["t"] <= gap_start:
            prev_dropped = h["dropped"]
    for h in inside:
        if prev_dropped is not None and h["dropped"] > prev_dropped:
            dropped_any = True
        prev_dropped = h["dropped"]
        if h["rehook"]:
            rehook = True
        max_inside = max(max_inside, h["starved_ms"])
        if not h["alive"]:
            if down_t is None:
                down_t = h["t"]
        else:
            if suspect_t is None and suspect_ms <= h["starved_ms"] < down_ms:
                suspect_t = h["t"]

    # ★ 復帰行はギャップ終端の**次の tick**で出る (`lib.rs:2951` が peak を搬送)。
    # ⚠️★★★ **コメントが言う制約を実装していなかった**（codex cross-review 高）。
    #   旧版は `(t - gap_start) >= starved_ms` しか見ておらず、復帰行の探索が
    #   `gap_end + 3s` まで許すため **`presence_ms > duration_ms` が入り得た**
    #   （tick 量子化で peak がギャップ長を最大 1 tick 超えうる）。
    #   → ★ `presence_ratio > 1` という無意味な値になり L2 分類も壊れる。
    # ★ **上限も明示的に課す**。超過は tick 量子化の範囲（1 tick）までを許容し、
    #   それを超えたら**採用しない**（＝ 別エピソードの行とみなす）。
    duration = gap_end - gap_start
    presence_ms = None
    for h in health:
        if (
            gap_end <= h["t"] <= gap_end + RECOVERY_SEARCH_MS
            and h["alive"]
            and (h["t"] - gap_start) >= h["starved_ms"]
            and h["starved_ms"] <= duration + TICK_MS
        ):
            # ★ 量子化ぶんの超過は切り詰める（`presence_ratio <= 1` を不変条件にする）
            presence_ms = min(h["starved_ms"], duration)
            break

    # ⚠️★★★ **「確定値」と「下界」を混同しない**（code-reviewer HIGH）。
    #   復帰行があれば peak = 確定値。無ければ観測済みの最大値は**下界**にすぎない。
    if presence_ms is not None:
        presence_kind = "exact"
    elif inside:
        presence_ms = min(max_inside, duration)   # ★ 同じ不変条件
        presence_kind = "lower_bound"     # ★ 復帰行が無い（右側打ち切り等）
    else:
        presence_ms = 0
        presence_kind = "interval_censored"  # ★ [0, suspect_ms) のどこか
    presence_known = presence_kind == "exact"

    return {
        "suspect_t": suspect_t,
        "down_t": down_t,
        "rehook": rehook,
        "dropped_any": dropped_any,
        "presence_ms": presence_ms,
        "presence_known": presence_known,
        "presence_kind": presence_kind,
        # ★ 物理制約で弾いた行数。⚠️ 非ゼロは「仕様が変わった / 時刻源がずれた」の警報である
        #   （`t` は SystemTime・`starved_ms` は Instant 由来なので NTP 巻き戻しで不等式が破れうる）。
        "health_lines_rejected": rejected,
    }


def extract_file(path: str, pid: str, sess_idx: int, cfg: dict) -> dict:
    rec = read_records(path)
    if rec["t0"] is None or rec["last_t"] is None or not rec["presses"]:
        return {"gaps": [], "windows": [], "excluded": {}, "n_session_starts": 0}

    gap_min = int(cfg["gap_min_ms"])
    win_ms = int(cfg["window_minutes"]) * 60 * 1000
    t0 = rec["t0"]

    # ★ 計測開始 = 最初の `session_start` 行 (無ければ t0)。それ以前の打鍵は測っていない。
    meas_start = rec["session_starts"][0] if rec["session_starts"] else t0
    presses = [(t, vk) for (t, vk) in rec["presses"] if t >= meas_start]
    if not presses:
        return {"gaps": [], "windows": [], "excluded": {}, "n_session_starts": len(rec["session_starts"])}

    file_end = rec["session_end"] if rec["session_end"] is not None else rec["last_t"]

    # --- 候補ギャップ (末尾の打ち切りギャップを含む) -------------------------
    raw: list[tuple[int, int, bool]] = []  # (start, end, event)
    for i in range(len(presses) - 1):
        raw.append((presses[i][0], presses[i + 1][0], True))
    # ⚠️★★★ **先頭ギャップ（計測開始 -> 最初の打鍵）を落とすと沈黙を過小評価する。**
    #   実測: このずれは中央値 180 秒・最大 97 分あり、`session_start` は既に押されている
    #   （= 計測中に 1 打も打っていない時間）。★ 本研究が問題にしている区間そのものである。
    #   ⚠️ ただし **前方に打鍵が無いので T0 特徴量が作れない** -> L3 には使えない。
    #   → ★ **別枠 `leading_gaps` に入れ、L1/L2 の記述にのみ使う**（L3 は触らない）。
    leading_raw = []
    if presses[0][0] - meas_start >= gap_min:
        leading_raw.append((meas_start, presses[0][0]))
    if file_end > presses[-1][0]:
        raw.append((presses[-1][0], file_end, False))  # ★ 右側打ち切り

    excluded = {"E1_session_boundary": 0, "E2_probe": 0, "E3_dropped": 0, "too_short": 0}
    gaps = []
    # ⚠️ 除外したギャップの**時間**が窓内訳から消えると沈黙が過小評価される
    #   （分母には残るため・code-reviewer MEDIUM）。→ 別バケットで残す。
    excluded_spans: list[tuple[int, int]] = []
    # ⚠️★★★ **計器の有無を「測る信号自身」で判定してはならない**（code-reviewer HIGH）。
    #   `lib.rs:2923` は状態変化時にしか `hook_health` を出さないので、
    #   ★ **計器はあるが presence が終始 30 秒未満だったセッションも 0 行**になる。
    #   `len(health) > 0` で判定すると、そのセッションが `unknown` に倒れ、
    #   ⚠️ **`silence_void_only_ms`（真に入力皆無）が構造的に 0 にしかならない**
    #   ＝ 測りたい対象がこの実装では永遠に測れない。
    # → ★ **独立な標識で判定する**: セッションの記録時刻が計器の導入日以降か。
    #   ★ 行が 1 つでもあれば当然「計器あり」なので、それは上書きで真にする。
    instrument_since = int(cfg["instrument_since_utc_ms"])
    instrument_present = bool(rec["health"]) or (t0 is not None and t0 >= instrument_since)

    for (gs, ge, event) in raw:
        if ge - gs < gap_min:
            excluded["too_short"] += 1
            continue
        # E1: セッション境界 (再開/ローテート) をまたぐ
        if any(gs < st < ge for st in rec["session_starts"]):
            excluded["E1_session_boundary"] += 1
            excluded_spans.append((gs, ge))
            continue
        # E2: プローブ提示・応答を含む (装置由来の沈黙)
        if any(gs < pt < ge for pt in rec["probes"]):
            excluded["E2_probe"] += 1
            excluded_spans.append((gs, ge))
            continue

        pres = gap_presence(rec["health"], gs, ge, cfg)
        if pres["dropped_any"]:
            excluded["E3_dropped"] += 1
            excluded_spans.append((gs, ge))
            continue

        g = {
            "pid": pid,
            "session": sess_idx,
            # ⚠️★★★ **「Suspect 行が無い」を「入力皆無」と読んではならない。**
            #   計器 (`liveness.rs` = 2026-08-09) より前に収集されたログには `hook_health` 行が
            #   1 行も無い。★ その場合の presence は **void ではなく unknown** である。
            "presence_observable": instrument_present,
            "start_offset_ms": gs - t0,  # ★ 絶対時刻を出さない (来歴の匿名化)
            "duration_ms": ge - gs,
            "event": event,  # True = 打鍵で終了 / False = 右側打ち切り
            "suspect_at_ms": (pres["suspect_t"] - gs) if pres["suspect_t"] is not None else None,
            "down_at_ms": (pres["down_t"] - gs) if pres["down_t"] is not None else None,
            "rehook": pres["rehook"],
            "presence_ms": pres["presence_ms"],
            "presence_known": pres["presence_known"],
            "presence_kind": pres["presence_kind"],
            "health_lines_rejected": pres["health_lines_rejected"],
            "window_index": int((gs - t0) // win_ms),
        }
        g.update(t0_features(presses, gs, cfg))
        gaps.append(g)

    # --- 先頭ギャップ（L1/L2 専用・T0 を持たないので L3 には渡さない）-----------
    leading_gaps = []
    for (gs, ge) in leading_raw:
        if any(gs < st < ge for st in rec["session_starts"][1:]):
            continue
        if any(gs < pt < ge for pt in rec["probes"]):
            continue
        pres = gap_presence(rec["health"], gs, ge, cfg)
        if pres["dropped_any"]:
            continue
        leading_gaps.append(
            {
                "pid": pid,
                "session": sess_idx,
                "presence_observable": instrument_present,
                "start_offset_ms": gs - t0,
                "duration_ms": ge - gs,
                "event": True,
                "suspect_at_ms": (pres["suspect_t"] - gs) if pres["suspect_t"] is not None else None,
                "down_at_ms": (pres["down_t"] - gs) if pres["down_t"] is not None else None,
                "rehook": pres["rehook"],
                "presence_ms": pres["presence_ms"],
                "presence_known": pres["presence_known"],
                "presence_kind": pres["presence_kind"],
                "health_lines_rejected": pres["health_lines_rejected"],
                "window_index": int((gs - t0) // win_ms),
                "leading": True,
            }
        )

    # --- L2: 5 分窓の時間内訳 ------------------------------------------------
    # ★ ギャップは窓をまたぐので、**重なり長で厳密に按分**する
    #   (ギャップ内での presence の時間位置は分からないので、
    #    presence の按分はせず「Suspect が出たギャップか」で窓時間を色分けする)。
    counts = window_counts(path, int(cfg["window_minutes"]))
    windows = []
    for wi, kd in enumerate(counts):
        w_lo = t0 + wi * win_ms
        w_hi = w_lo + win_ms
        sil = 0
        sil_presence = 0
        sil_void = 0
        sil_unknown = 0
        sil_leading = 0
        sil_excluded = 0
        for (egs, ege) in excluded_spans:
            ov = max(0, min(ege, w_hi) - max(egs, w_lo))
            if ov > 0:
                sil_excluded += ov
        for g in leading_gaps:
            gs = t0 + g["start_offset_ms"]
            ge = gs + g["duration_ms"]
            ov = max(0, min(ge, w_hi) - max(gs, w_lo))
            if ov > 0:
                sil_leading += ov
        for g in gaps:
            gs = t0 + g["start_offset_ms"]
            ge = gs + g["duration_ms"]
            ov = max(0, min(ge, w_hi) - max(gs, w_lo))
            if ov <= 0:
                continue
            sil += ov
            if not g["presence_observable"]:
                # ⚠️★★★ 計器が無い = **unknown**。void に倒すと
                #   「入力皆無だった」と読まれる（= 沈黙して間違った結果を出す）。
                sil_unknown += ov
            elif g["suspect_at_ms"] is not None:
                sil_presence += ov
            else:
                sil_void += ov
        windows.append(
            {
                "pid": pid,
                "session": sess_idx,
                "window_index": wi,
                "keydowns": kd,
                "window_ms": win_ms,
                "silence_ms": sil,
                "silence_with_presence_ms": sil_presence,
                "silence_void_only_ms": sil_void,
                "silence_unknown_ms": sil_unknown,
                # ★ 先頭ギャップ（計測開始 -> 最初の打鍵）。上の 3 つとは**排他**。
                "silence_leading_ms": sil_leading,
                # ★ E1/E2/E3 で落としたギャップの時間（★ 上のどれとも排他）
                "silence_excluded_ms": sil_excluded,
            }
        )

    return {
        "gaps": gaps,
        "leading_gaps": leading_gaps,
        "windows": windows,
        "excluded": excluded,
        "n_session_starts": len(rec["session_starts"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat-dir", required=True, help="Phase1 生 NDJSON の平置きディレクトリ (repo 外)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = load_config(args.config)

    paths = sorted(
        os.path.join(args.flat_dir, f)
        for f in os.listdir(args.flat_dir)
        if f.endswith(".ndjson")
    )
    if not paths:
        print("!! .ndjson が 1 つも無い", file=sys.stderr)
        return 2

    by_pid: dict[str, list[str]] = {}
    for p in paths:
        base = os.path.basename(p)
        pid = base.split("_", 1)[0] if "_" in base else "UNKNOWN"
        by_pid.setdefault(pid, []).append(p)

    all_gaps: list[dict] = []
    all_leading: list[dict] = []
    all_windows: list[dict] = []
    excluded_total = {"E1_session_boundary": 0, "E2_probe": 0, "E3_dropped": 0, "too_short": 0}
    multi_session_files = 0

    for pid in sorted(by_pid):
        # ★ セッション番号は「そのファイルの先頭 t0 の順位」= 決定的かつファイル名非依存。
        entries = []
        for p in by_pid[pid]:
            rec_t0 = read_records(p)["t0"]
            entries.append((rec_t0 if rec_t0 is not None else 0, p))
        entries.sort()
        for idx, (_, p) in enumerate(entries):
            out = extract_file(p, pid, idx, cfg)
            all_gaps.extend(out["gaps"])
            all_leading.extend(out["leading_gaps"])
            all_windows.extend(out["windows"])
            for k, v in out["excluded"].items():
                excluded_total[k] = excluded_total.get(k, 0) + v
            if out["n_session_starts"] > 1:
                multi_session_files += 1

    payload = {
        "schema": "silence-presence-extract/v1",
        "config": cfg,
        "input_manifest": _input_manifest(paths),
        "participants": sorted(by_pid),
        "n_files": len(paths),
        "multi_session_files": multi_session_files,
        "excluded": excluded_total,
        "n_gaps": len(all_gaps),
        "n_leading_gaps": len(all_leading),
        "n_windows": len(all_windows),
        "gaps": all_gaps,
        "leading_gaps": all_leading,
        "windows": all_windows,
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"gaps={len(all_gaps)} leading={len(all_leading)} "
          f"windows={len(all_windows)} excluded={excluded_total}")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except OSError:
        # ⚠️★ traceback には**入力の絶対パスがそのまま出る**（S5C-D8 の機序）。
        #   → パスを表示せずに落とす。
        print("!! 入力ディレクトリ/ファイルを読めない（パスは表示しない）", file=sys.stderr)
        rc = 5
    raise SystemExit(rc)
