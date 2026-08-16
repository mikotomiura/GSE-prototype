#!/usr/bin/env python3
"""Step 1 — `gse-replay` の snapshot JSON を TouchDesigner の Table DAT が読める CSV へ変換する。

依存: **標準ライブラリのみ**（`20260810-.../design.md` §3 Step 2 の要求）。

⚠️★★ 入力の作り方（ドキュメントの記述が誤っていたので実測で訂正した）:

    ✗ cargo run --bin gse-replay -- <ndjson> --snapshot out.json
        → `--snapshot <file>` は **既存スナップショットとの比較モード**であり、出力はしない。
          ファイルが無いと `MISMATCH: cannot read ...` で exit 1 になる（実測 2026-08-11）。

    ✓ cargo run --bin gse-replay -- <ndjson> > out.json
        → **デフォルトが stdout への JSON 配列出力**（`src-tauri/src/bin/replay.rs:9-10` の逐語）。

使い方:

    cd src-tauri
    cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson > snap.json
    python .steering/20260811-expression-prototype-step0/scripts/snapshot_to_csv.py snap.json out.csv

★ 出力する列は `FeatSnapshot` の全 15 列 ＋ 派生 2 列（`t_rel_s` / `dt_s`）。
  `FeatSnapshot` は **content-free**（キーストローク内容を含まない）ので、
  制作ツールへ渡してよい唯一の形である（`data-privacy` / `docs/development-guidelines.md` §10）。
"""

from __future__ import annotations

import csv
import json
import os
import sys

# FeatSnapshot の列（src-tauri/src/analysis/loop_step.rs の FeatSnapshot と同順）
SNAPSHOT_COLUMNS = [
    "timestamp",
    "f1",
    "f3",
    "f4",
    "f5",
    "f6",
    "p_flow",
    "p_inc",
    "p_stuck",
    "raw_x",
    "raw_y",
    "ewma_x",
    "ewma_y",
    "obs",
    "alpha",
]

# 表現層が読む派生列。
#   t_rel_s : セッション先頭からの相対秒（TD 側で時間軸に使う）
#   dt_s    : 直前サンプルからの経過秒
#             ★ 1.0 固定ではない —— 実測で 2.691 s のギャップが存在した
#               (tests/fixtures/phase1_ime_heavy.ndjson)。
#             ⚠️★ S0-D10: **この列は人間が読むための注記であって、計算の入力ではない。**
#               expr_smooth.py は `t_rel_s` の差分から経過時間を再計算する
#               （時刻の真実を 2 系統持たないため）。dt_s と t_rel_s が食い違ったら t_rel_s が正。
DERIVED_COLUMNS = ["t_rel_s", "dt_s"]


def load_snapshot(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(
            f"{path}: 期待した形は JSON 配列だが {type(data).__name__} だった。"
            " `--snapshot` を付けずに実行した出力か確認すること。"
        )
    if not data:
        raise ValueError(f"{path}: 行が 0 件。入力 NDJSON が空でないか確認すること。")

    # ⚠️★ 先頭行だけを検証しない —— 2 件目以降が列を欠くと to_rows() が素の KeyError で落ちる。
    #   FeatSnapshot は Rust の単一 struct から serde で吐かれるので実運用では踏みにくいが、
    #   「レビューできる道具として残す」前提なら全行を見る（Claude/Codex 両者の指摘）。
    for i, rec in enumerate(data):
        if not isinstance(rec, dict):
            raise ValueError(f"{path}: {i} 番目の要素が object でない（{type(rec).__name__}）")
        missing = [c for c in SNAPSHOT_COLUMNS if c not in rec]
        if missing:
            raise ValueError(f"{path}: {i} 番目に FeatSnapshot の列が無い: {missing}")
        if not isinstance(rec["timestamp"], (int, float)):
            raise ValueError(f"{path}: {i} 番目の timestamp が数値でない: {rec['timestamp']!r}")

    # ★ 時刻の単調増加。逆行・重複は下流（expr_smooth）で架空の経過時間に化けるので、ここで落とす。
    for i in range(1, len(data)):
        if data[i]["timestamp"] <= data[i - 1]["timestamp"]:
            raise ValueError(
                f"{path}: timestamp が単調増加でない"
                f"（{i - 1} 番目 {data[i - 1]['timestamp']} -> {i} 番目 {data[i]['timestamp']}）"
            )
    return data


def to_rows(snapshot: list[dict]) -> list[dict]:
    t0 = snapshot[0]["timestamp"]
    rows = []
    prev_ts = None
    for rec in snapshot:
        ts = rec["timestamp"]
        row = {c: rec[c] for c in SNAPSHOT_COLUMNS}
        row["t_rel_s"] = round((ts - t0) / 1000.0, 3)
        # 先頭行の dt は定義できない。0 ではなく空欄にして、下流に「無い」と伝える。
        row["dt_s"] = "" if prev_ts is None else round((ts - prev_ts) / 1000.0, 3)
        rows.append(row)
        prev_ts = ts
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        print("usage: snapshot_to_csv.py <snapshot.json> <out.csv>", file=sys.stderr)
        return 2

    src, dst = argv[1], argv[2]
    if os.path.realpath(src) == os.path.realpath(dst):
        print(f"error: 入力と出力が同じファイルである: {src}", file=sys.stderr)
        return 2
    # ⚠️★ try は読み込みだけでなく **書き込みまで**包む。
    #   初版は load_snapshot だけを包んでいたので、出力先ディレクトリが無いと
    #   素の FileNotFoundError トレースバックが出ていた（2 回目のレビューで指摘・実測で確認）。
    columns = SNAPSHOT_COLUMNS + DERIVED_COLUMNS
    try:
        snapshot = load_snapshot(src)
        rows = to_rows(snapshot)
        # TD の Table DAT は CRLF を嫌わないが、git 差分を安定させるため LF に固定する。
        with open(dst, "w", encoding="utf-8", newline="\n") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    dts = [r["dt_s"] for r in rows if r["dt_s"] != ""]
    span = rows[-1]["t_rel_s"]
    print(f"wrote {dst}: {len(rows)} rows x {len(columns)} cols, span {span} s")
    if dts:
        uniq = sorted(set(dts))
        print(f"  dt_s: min={min(dts)} max={max(dts)} distinct={uniq[:8]}")
        if max(dts) > 1.5:
            print(
                f"  ★ 注意: dt が {max(dts)} s まで開いている。"
                " 表現層の平滑化は固定 alpha ではなく dt を見る形にすること。"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
