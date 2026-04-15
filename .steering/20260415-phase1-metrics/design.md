# Phase 1 Task 2: Metrics 算出エンジン — design

> 本 design は Phase 1 全体の v2 設計（`.steering/20260415-phase1-ground-truth/design.md`）から Task 2 スコープを抽出・具体化したもの。新たな `/reimagine` は不要。

## 実装アプローチ

### 純粋関数中心

- すべての算出ロジックを `analysis/metrics.rs` の純粋関数群にまとめる（副作用なし、analysis/ 純粋性維持）
- テストは合成 ReplayEvent 列 + 合成 FeatSnapshot 列で網羅
- `recovered_at` は記録時ではなく算出時に計算するため、閾値変更で再計算可能

### 出力 surface

- `gse-replay --metrics <ndjson>`: 人間可読の pretty-print（混同行列 + F1 + 中央値）
- `gse-replay --metrics --json <ndjson>`: `SessionMetrics` 構造体を `serde_json::to_string_pretty` でシリアライズ
- 両者は同じ `SessionMetrics` から派生（単一ソース）

## 変更対象

### 新規作成するファイル

- `src-tauri/src/analysis/metrics.rs` — 純粋計算モジュール

### 修正するファイル

- `src-tauri/src/analysis/mod.rs` — `pub mod metrics;` 追加
- `src-tauri/src/bin/replay.rs`
  - `ReplayEvent` enum に `UserLabel { timestamp, label: String, recovered_at: Option<u64> }` 追加
  - NDJSON パース分岐で `"type":"user_label"` を認識
  - `Args` に `metrics: bool` / `json: bool` 追加、手書きパーサ拡張
  - `main()` に `metrics` 分岐、`--snapshot` との排他チェック
- `.steering/20260415-phase1-ground-truth/baseline_metrics.md` — 雛形新規作成

### 削除するファイル
なし

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| `tests/snapshots/minimal.json` | NONE | 純粋追加、既存バリアント出力不変 | T-regression で確認 |
| `analysis/mod.rs` の既存 `pub mod` | LOW | 1 行追加のみ | — |
| `replay.rs` 既存 `--snapshot` 動作 | LOW | 排他チェックを入口に追加するだけ | T-snapshot で確認 |
| UserLabel 欠落セッションへの実行 | MEDIUM | サンプル 0 件でゼロ除算リスク | ガード + 警告出力 |

## 既存パターンとの整合性

- **純粋モジュール配置**: `analysis/features.rs` と同じ「外部依存なし、`#[cfg(test)]` で自己完結」パターン
- **CLI 手書きパーサ**: `replay.rs:106-150` の `--snapshot` 実装をコピーして `--metrics` / `--json` を追加
- **NDJSON バリアント追加**: 既存 `ReplayEvent::Feat` と同形式（`serde_json::from_str` で Value 読取り → フィールド抽出）
- **排他フラグチェック**: `main()` 冒頭で Args 検証し、両立禁止の組み合わせは Usage エラーで即 exit

## metrics.rs の API 素案

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum LabelClass { Flow, Incubation, Stuck }

#[derive(Debug, Clone, Serialize)]
pub struct ConfusionMatrix {
    /// matrix[i][j] = 正解 i, 推定 j の件数
    pub matrix: [[u32; 3]; 3],
}

#[derive(Debug, Clone, Serialize)]
pub struct SessionMetrics {
    pub total_labels: u32,
    pub confusion: ConfusionMatrix,
    pub per_class: [ClassMetrics; 3], // Flow / Incubation / Stuck の順
    pub macro_f1: f64,
    pub micro_f1: f64,
    pub detection_lead_ms_median: Option<i64>, // 負: ラグ、正: リード
    pub stuck_recovery_ms_median: Option<u64>,
    pub warnings: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct ClassMetrics {
    pub class: LabelClass,
    pub precision: f64,
    pub recall: f64,
    pub f1: f64,
    pub support: u32,
}

pub struct UserLabelEvent {
    pub timestamp: u64,
    pub label: LabelClass,
}

/// Stuck ラベル以降、p_flow > threshold に達する最初の FeatSnapshot 時刻を返す。
/// window_ms を超えて到達しない場合は None。
pub fn compute_recovered_at(
    stuck_ts: u64,
    feats: &[FeatSnapshot],
    window_ms: u64,
    p_flow_threshold: f64,
) -> Option<u64>;

/// 混同行列・precision/recall/F1・中央値を算出する主関数。
pub fn compute_session_metrics(
    labels: &[UserLabelEvent],
    feats: &[FeatSnapshot],
) -> SessionMetrics;
```

**FeatSnapshot** は `bin/replay.rs` で既に定義済み。`analysis::metrics` は `FeatSnapshot` 構造体への参照を受け取るので、`replay.rs` から import する形で設計（または共通の型を `analysis::snapshot` に置いて両者から参照）。

## HMM argmax と UserLabel の突き合わせロジック

- 各 UserLabel に対し、その timestamp を含む 1 秒区間の FeatSnapshot を選ぶ（ごく近い timestamp のもの）
- 存在しない場合は警告に追加して推定クラスを未知扱い（confusion には計上しない）
- 推定クラス = `[p_flow, p_inc, p_stuck]` の argmax

## リード/ラグ時間の算出

- 各 UserLabel `l` について、ラベル前後 60 秒区間を走査
- `l.label` と同じクラスが HMM argmax になっている最初の FeatSnapshot を探す
- 時刻差 = feat_ts - label_ts（負 → ラグ、正 → リード）
- セッション全体で中央値を算出

## Stuck 回復時間

- 各 Stuck ラベルに対し `compute_recovered_at(ts, feats, 15*60*1000, 0.5)` を呼び出し
- 非 None の値の中央値

## pretty-print 出力形式（暫定）

```
SessionMetrics
  Total labels: 12 (Flow:6, Inc:3, Stuck:3)
  Macro F1: 0.72
  Micro F1: 0.75
  Per-class:
    Flow       P=0.83  R=0.83  F1=0.83  support=6
    Incubation P=0.67  R=0.67  F1=0.67  support=3
    Stuck      P=0.67  R=0.67  F1=0.67  support=3
  Confusion (rows = truth, cols = pred):
                Flow   Inc    Stuck
    Flow          5     1      0
    Incubation    1     2      0
    Stuck         0     1      2
  Detection lead median: +3200 ms  (positive = HMM leads user)
  Stuck recovery median: 48000 ms
  Warnings: 0
```

## テスト戦略

- T-M1 Unit: `compute_recovered_at`
  - 正常ケース（Stuck 後 10s で p_flow > 0.5 → Some(ts)）
  - 窓超過ケース（15 分以内に p_flow > 0.5 が来ない → None）
  - 連続 Stuck（2 つ目の Stuck までに回復した場合の扱い）
  - 空 feats（`&[]` → None）
- T-M2 Unit: `compute_session_metrics`
  - 全正解合成ケース（F1 = 1.0）
  - 完全逆転ケース（F1 = 0.0）
  - UserLabel 0 件（空 SessionMetrics、warnings に記載、panic なし）
  - FeatSnapshot と timestamp ずれ（警告にカウント）
- T-regression: `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` で byte-equal 維持
- 手動: 実セッション NDJSON に対する pretty-print / JSON 出力

## ロールバック計画

- `analysis/metrics.rs` を削除 + `mod.rs` の `pub mod metrics;` 削除
- `replay.rs` の変更を git revert
- logger.rs / lib.rs には影響なし（Task 1 の範囲に閉じている）

## 既知の Open 点

- **FeatSnapshot の配置**: 現在 `bin/replay.rs` 内で定義されている。`analysis::metrics` がこれに依存するため、`analysis/snapshot.rs` に移動するか、replay.rs に置いたまま metrics は `replay.rs` から型を借りる形にするか要検討。v2 設計では「純粋関数」の位置付けから前者が望ましい。実装時に確定。
- **HMM argmax の一意性保証**: 同率時のタイブレーク（稀だが発生しうる）。Flow > Incubation > Stuck の固定順で一意化。
- **リード/ラグの定義**: 「同じクラスが出た最初の時刻」より「確率が 0.5 を超えた最初の時刻」の方が安定するかもしれない。初期実装では argmax 方式、実データで再検討。
