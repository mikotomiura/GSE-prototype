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
| 2026-04-15 | `gse_20260415_080214.ndjson` | 6/4/0 | 0.000 | 0.000 | n/a | -3119 | 0 | 初回実機検証。F/I ラベリングのみ、HMM 全誤判定 |
| 2026-04-15 | `gse_20260415_080921.ndjson` | 0/0/2 | 0.222 | 0.500 | n/a | +2383 | 0 | Stuck 単独検証。1/2 件一致、HMM が 2.4s 先行 |

## 集計サマリ（Phase 2a Go/No-Go 判断）

> 10 件溜まった時点で更新。Phase 2a 着手可否の根拠として使う。

- セッション件数: 2 / 10
- Flow ラベル総数: 6
- Incubation ラベル総数: 4
- Stuck ラベル総数: 2
- Stuck precision 平均: 1.0（n=2、Phase 2a Go 条件: **≥ 0.6**、現時点達成だがサンプル少）
- Stuck recall 平均: 0.5
- Stuck recovery median 全体: n/a（2 件とも 15 分以内に p_flow > 0.5 未到達）

## 観察メモ

### 2026-04-15 初回検証
- **Flow/Inc セッション (gse_20260415_080214)**: HMM が Flow/Inc を一度も argmax 選択しなかった。セッション開始直後の均等分布 `[1/3, 1/3, 1/3]` からユーザー自認よりも早く Inc/Stuck 側に振れていた → Phase 2a で Synthetic Friction を「真の摩擦兆候があった沈黙のみ」に再設計する動機として強い
- **Stuck セッション (gse_20260415_080921)**: 2 件中 1 件で HMM も Stuck を当てた。lead +2.4s は妥当な反応時間
- **detection_lead_ms の定義見直し (M1)**: 初版 `find()` で +50s、`min_by_key(abs_diff)` に修正して -3.1s / +2.4s と現実的な値に
- サンプル数 n=2 は Phase 2a Go 判断には不十分、**最低 5 セッション × 3 クラス (F/I/S 各 ≥5 件)** まで運用を続けて収集
