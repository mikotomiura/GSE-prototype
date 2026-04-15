# Phase 1 Baseline Metrics（GT 付きセッション集計）

> **記入手順**:
> 1. GT 付きセッションを取ったら `~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson` を特定
> 2. `cd src-tauri && ~/.cargo/bin/cargo run --bin gse-replay -- <session.ndjson> --metrics` で pretty-print 出力を取得
> 3. 下表に 1 行追加（**手作業で良い、10 件未満はスクリプト化不要**）
> 4. 10 件以上溜まった時点で Phase 2a 着手判断（Go/No-Go: Stuck precision が平均 0.6 以上）
> 5. 機械可読形式が必要になったら `--metrics --json` を tee で保存して `jq` で集計

## セッション一覧

| Date | Session file | Labels (F/I/S) | Macro F1 | Micro F1 | Stuck recovery median (s) | Detection lead median (ms) | Warnings | Note |
|---|---|---|---|---|---|---|---|---|
| _YYYY-MM-DD_ | `gse_XXX.ndjson` | _F/I/S_ | _0.00_ | _0.00_ | _n/a_ | _n/a_ | _0_ | _初回検証など_ |

## 集計サマリ（Phase 2a Go/No-Go 判断）

> 10 件溜まった時点で更新。Phase 2a 着手可否の根拠として使う。

- セッション件数: _0 / 10_
- Flow ラベル総数: _0_
- Incubation ラベル総数: _0_
- Stuck ラベル総数: _0_
- Stuck precision 平均: _n/a_（Phase 2a Go 条件: **≥ 0.6**）
- Stuck recall 平均: _n/a_
- Stuck recovery median 全体: _n/a_

## 観察メモ

> 運用中に気づいた傾向・外れ値・再現性のない挙動をここに追記する。
