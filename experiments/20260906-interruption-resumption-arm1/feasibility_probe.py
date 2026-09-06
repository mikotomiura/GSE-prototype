#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M1 離席候補アームの **実行可能性プローブ**。

⚠️★★★ **これはアウトカムの本解析ではない。** ★ 「そもそも N があるか」「被験者間で
どれだけ偏るか」を数えるだけである。★ 系自身の離席判定を通しておらず、`p_stuck`
トリガーも `intervention_enabled` の層別も掛けていない。
→ ★ 出力を効果量として読まないこと (`notes.md` §3 / §7)。

⚠️★★★ **本スクリプトは NDJSON を repo に書き出さない。** 出力は集計値のみ。
★ ファイル名 (= 擬似 ID ＋ セッション開始時刻) は **JSON に入れない**
(experiments/_template/README.md の security-checker HIGH)。
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

# ★ 一次: src-tauri/src/analysis/intervention.rs:10 `const AWAY_IDLE_MS: u64 = 180_000;`
AWAY_IDLE_MS = 180_000
# ★ 一次: src-tauri/src/analysis/metrics.rs `recovery_window_ms: 5 * 60 * 1000`
RECOVERY_WINDOW_MS = 5 * 60 * 1000

# ⚠️★★★ 被験者 ID の在り処は **2 通りある** (2026-09-06 実測):
#   - `raw/<コホート名>/P999_gse_20000101_000000.ndjson` -> ★ **ファイル名の接頭辞**
#   - `raw/P999/gse_20000101_000000.ndjson`              -> ★ **親ディレクトリ名**
# ⚠️ ファイル名だけを見ると、後者のコホートが丸ごと `UNKNOWN` に落ちる
#   (★ 本スクリプトの最初の版で実際に 13 本落ちた)。
#
# ⚠️★★★ **上の例は架空名である** (`P999` / 2000-01-01)。★ 実ファイル名は
#   **擬似 ID ＋ 打鍵セッションの開始日時そのもの**なので、
#   ⚠️ **コメントにも書かない** (`scripts/secrets-filter.sh` が exit 2 で止める)。
PID = re.compile(r"^(P\d+)")


def participant_of(path: Path) -> str:
    m = PID.match(path.name)
    if m:
        return m.group(1)
    m = PID.match(path.parent.name)
    if m:
        return m.group(1)
    return "UNKNOWN"


def scan(root: Path) -> dict:
    """1 ディレクトリを走査して集計値を返す（★ `main` と `selftest` の共通部）。"""
    files = sorted(root.rglob("*.ndjson"))
    per_pid_events: collections.Counter = collections.Counter()
    per_pid_files: collections.Counter = collections.Counter()
    gaps: list[int] = []
    receipt_after: list[bool] = []
    n_paste_lines = 0
    n_malformed = 0            # ⚠️ 壊れた行 (code-reviewer M-5)
    n_boundary_crossing = 0    # ⚠️ セッション境界を跨いだ gap (code-reviewer M-6)

    for path in files:
        pid = participant_of(path)
        per_pid_files[pid] += 1

        keys: list[int] = []
        pastes: list[int] = []
        boundaries: list[int] = []
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    # ⚠️ 黙って捨てない (code-reviewer M-5)。`capabilities_gate.py` は
                    #   `malformed_lines` を出しており、こちらだけ落とすと非対称になる。
                    n_malformed += 1
                    continue
                kind = obj.get("type")
                # ★★★ セッション境界を拾う (code-reviewer M-6)。
                #   ⚠️ アプリの再起動を挟んだ打鍵間隔を「離席候補」と読むと**偽陽性**になる。
                if kind == "session_start":
                    if isinstance(obj.get("t"), (int, float)):
                        boundaries.append(int(obj["t"]))
                elif kind == "meta":
                    for key in ("session_start", "session_end"):
                        if isinstance(obj.get(key), (int, float)):
                            boundaries.append(int(obj[key]))
                ts = obj.get("t")
                if not isinstance(ts, (int, float)):
                    continue
                if kind == "key":
                    keys.append(int(ts))
                elif kind == "paste":
                    pastes.append(int(ts))
                    n_paste_lines += 1
        keys.sort()
        pastes.sort()
        boundaries.sort()
        for a, b in zip(keys, keys[1:]):
            gap = b - a
            if gap < AWAY_IDLE_MS:
                continue
            # ⚠️★★★ 境界を跨ぐ gap は**離席ではない**可能性があるので主系列から外す。
            if any(a < t < b for t in boundaries):
                n_boundary_crossing += 1
                continue
            gaps.append(gap)
            per_pid_events[pid] += 1
            receipt_after.append(any(b <= p <= b + RECOVERY_WINDOW_MS for p in pastes))

    return {
        "files": files, "per_pid_events": per_pid_events, "per_pid_files": per_pid_files,
        "gaps": gaps, "receipt_after": receipt_after, "n_paste_lines": n_paste_lines,
        "n_malformed": n_malformed, "n_boundary": n_boundary_crossing,
        "n_events": len(gaps),
    }


def selftest() -> int:
    """⚠️★★★ 検査が空回りしていないかを **合成データ**で確かめる。

    ★ 実データでは `excluded_boundary_crossing = 0` になる。⚠️ **これだけ見ると
    「境界ガードが効いている」のか「そもそも動いていない」のか区別できない**
    (`verify-before-claiming` ルール 5b)。→ ★ 3 状態を作って試す。
    """
    import tempfile

    def write(dirpath: Path, name: str, rows: list[dict]) -> None:
        with (dirpath / name).open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    print("=== selftest: 境界ガード / 壊れた行の計数 ===")
    failures = 0
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "P999"
        root.mkdir(parents=True)

        # (1) 境界なし: 200s の gap は離席候補として **数えられる**
        write(root, "a.ndjson", [
            {"type": "key", "t": 1_000_000},
            {"type": "key", "t": 1_200_000},
        ])
        r1 = scan(Path(td))
        ok1 = r1["n_events"] == 1 and r1["n_boundary"] == 0
        print(f"  [1] 境界なしの 200s gap    -> events={r1['n_events']} boundary={r1['n_boundary']} "
              f"{'PASS' if ok1 else 'FAIL'}")
        failures += 0 if ok1 else 1

        # (2) 境界あり: 同じ gap の途中に session_start が入ると **除外される**
        write(root, "a.ndjson", [
            {"type": "key", "t": 1_000_000},
            {"type": "session_start", "t": 1_100_000},
            {"type": "key", "t": 1_200_000},
        ])
        r2 = scan(Path(td))
        ok2 = r2["n_events"] == 0 and r2["n_boundary"] == 1
        print(f"  [2] 境界を跨ぐ 200s gap    -> events={r2['n_events']} boundary={r2['n_boundary']} "
              f"{'PASS' if ok2 else 'FAIL (ガードが空回り)'}")
        failures += 0 if ok2 else 1

        # (3) 壊れた行を黙って捨てていないか
        with (root / "a.ndjson").open("a", encoding="utf-8") as fh:
            fh.write("{これは JSON ではない\n")
        r3 = scan(Path(td))
        ok3 = r3["n_malformed"] == 1
        print(f"  [3] 壊れた行 1 行          -> malformed={r3['n_malformed']} "
              f"{'PASS' if ok3 else 'FAIL (黙って捨てている)'}")
        failures += 0 if ok3 else 1

    print(f"=== selftest: {'OK' if failures == 0 else str(failures) + ' 件 FAIL'} ===")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="NDJSON を含むディレクトリ")
    ap.add_argument("--out", default="results/feasibility.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.input:
        print("--input か --selftest のどちらかが要ります", file=sys.stderr)
        return 2

    root = Path(args.input)
    res = scan(root)
    files = res["files"]
    if not files:
        print(f"NDJSON が見つかりません: {root}", file=sys.stderr)
        return 2
    per_pid_events = res["per_pid_events"]; per_pid_files = res["per_pid_files"]
    gaps = res["gaps"]; receipt_after = res["receipt_after"]
    n_paste_lines = res["n_paste_lines"]
    n_malformed = res["n_malformed"]; n_boundary_crossing = res["n_boundary"]

    n = len(gaps)
    out = {
        "kind": "feasibility_probe",
        "warning": "⚠️★★★ アウトカムの推定値ではない。系の離席判定・p_stuck トリガー・"
                   "介入割付のいずれも通していない粗い数え上げである。",
        "thresholds": {"away_idle_ms": AWAY_IDLE_MS, "receipt_window_ms": RECOVERY_WINDOW_MS},
        "corpus": {
            "ndjson_files": len(files),
            "participants": len(per_pid_files),
            "files_per_participant": dict(sorted(per_pid_files.items())),
            "paste_lines_total": n_paste_lines,
            "malformed_lines": n_malformed,
        },
        "resumption_events": {
            "n": n,
            "participants_contributing": len(per_pid_events),
            "per_participant": dict(sorted(per_pid_events.items())),
            "excluded_boundary_crossing": n_boundary_crossing,
            "gap_seconds": {
                "median": round(statistics.median(gaps) / 1000, 1) if gaps else None,
                "p90": round(sorted(gaps)[int(0.9 * n)] / 1000, 1) if n else None,
                "max": round(max(gaps) / 1000, 1) if gaps else None,
            },
        },
        # ⚠️★★★ 下の 2 値は **本セッションで既に見てしまった**。
        #   → notes.md §7-1: 本アームを事後に「事前登録」へ格上げしてはならない。
        "already_seen_raw_rate": {
            "receipt_within_window": sum(receipt_after),
            "n": n,
            "rate": (sum(receipt_after) / n) if n else None,
            "caveat": "⚠️ 素の比率。R0/R0'/R1 のいずれでもなく、回復判定 (p_flow) を含まない。",
        },
    }

    outpath = Path(args.out)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"NDJSON {len(files)} 本 / 被験者 {len(per_pid_files)} 名")
    print(f"離席候補 → 再開 事象: {n}  (寄与 {len(per_pid_events)} 名)")
    print(f"  被験者別: {dict(sorted(per_pid_events.items()))}")
    if n:
        print(f"  gap 秒 median={out['resumption_events']['gap_seconds']['median']} "
              f"p90={out['resumption_events']['gap_seconds']['p90']}")
    print("-> results/feasibility.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
