# 設計 (v1 — /reimagine 前の初版)

## 実装アプローチ

`gse-replay --metrics` の出力構造体 `SessionMetrics` (`analysis/metrics.rs`) に
**アウトカム指標フィールドを追加** (additive・後方互換)。算出は analysis/ 内の純粋関数で行い、
NDJSON からの収集 (paste/key/intervention イベント) は `bin/replay.rs` に collector を追加する
(既存 `collect_user_labels` / `collect_logged_feats` / `collect_key_timestamps` と同流儀)。

**重要な構造的事実**: 現状 `compute_session_metrics(labels, feats)` は paste/key を消費していない
(Paste の `timestamp()` は `None`・dead_code)。新指標には paste 文字数列・key(vk)列が必要なため、
新しい collector + 新しい純粋関数 `compute_outcome_metrics(...)` を追加し、`SessionMetrics` に
`outcome: Option<OutcomeMetrics>` をネストする (既存フィールド名・gse-dataset 利用側を壊さない)。

## 算出する指標 (v0.4 §4.1/§4.2)

### (b) 自力解決率
- `manual_contribution_ratio = manual_insert_chars / (manual_insert_chars + external_paste_chars_total)`
  - `manual_insert_chars` = 文字生成キー press 数 − backspace/delete press 数 (content-free, vk のみ)。
  - 分母 0 (キーも paste も無し) → `None` (NaN を出さない)。
- `productive_manual_recovery_rate` = Stuck 候補後 5 分以内に external paste なしで net_diff 正進行した割合。
  - **★設計フォーク (/reimagine 対象)**: 下記「要承認」参照。

### (a) AI依存度
- `external_paste_count` = paste 行数 (external_paste_chars が Some の行)。
- `large_paste_rate` = (external_paste_chars >= LARGE_THRESHOLD の paste 数) / external_paste_count。
- `paste_after_stuck_rate` = Stuck 候補後 AFTER_WINDOW 内の paste 数 / Stuck 候補数。
- `self_recovery_without_paste` = Stuck 候補のうち回復窓内に paste が無く回復した割合。
- `paste_count_per_hour` = external_paste_count / セッション時間(h) (補助指標)。

## 要承認の設計判断 (会話承認 — /reimagine で v2 と比較)

1. **`productive_manual_recovery_rate` の Stuck 候補トリガ** (4 案):
   - (i) `p_stuck >= 閾値` の feat (自動・GT 不要・連続検出に注意)
   - (ii) `user_label == stuck` (GT・最も解釈容易・パイロットで疎)
   - (iii) 介入発火 `intervention_decision.action != none` (運用的に意味あり・介入 OFF 時 0)
   - (iv) probe Q1 高 (主観・probe 配信時のみ)
   - **v1 推奨**: (ii) user_label=stuck を主・(i) を補助フォールバック。理由 = M3 Y価値検証の主旨は
     「ユーザーが行き詰まった後に自力回復したか」であり GT ラベルが最も解釈容易。
2. **net_diff 正進行の定義**: net_diff = 文字生成キー − backspace の純増。窓内 net_diff > 0
   (v1) か、閾値 (例 +20 chars) 超か。窓 = 5 分。
3. **閾値**: `LARGE_THRESHOLD` (large paste = 何文字以上)、`AFTER_WINDOW` (after_stuck = 何秒以内)。
   v1 推奨: LARGE = 50 chars、AFTER = 120 秒。
4. **フィールド命名と後方互換**: `SessionMetrics.outcome: Option<OutcomeMetrics>` でネスト追加。
   既存 confusion/per_class/f1 は不変 → gse-dataset 既存利用側は壊れない。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/metrics.rs` — `OutcomeMetrics` 構造体 + `compute_outcome_metrics()` 純粋関数追加。
  `SessionMetrics` に `outcome: Option<OutcomeMetrics>` 追加。
- `src-tauri/src/bin/replay.rs` — paste 行 collector (`collect_paste_events`)、key vk 列 collector
  (backspace 判別)、必要なら intervention collector。`--metrics` 経路で `compute_outcome_metrics` 呼び出し。
- `src-tauri/tests/fixtures/` — 新 golden fixture (paste/key/stuck を含む)。
- `src-tauri/tests/snapshots/` または replay.rs テスト — metrics golden 固定値。

### 新規作成するファイル
- なし (既存モジュール拡張のみ)。

## 影響範囲
- `--snapshot` (FeatSnapshot) は features 不触のため **byte-equal 不変**。
- 既存 metrics golden テスト (`collect_logged_feats_plus_metrics_matches_minimal_fixture` 等) は
  `outcome: None` または新フィールド追加で影響 → 期待値更新が必要 (additive)。
- gse-dataset の `metrics/P*/` 利用側: ネスト追加のみ・既存キー不変。

## 既存パターンとの整合性
- 純粋関数・Option で欠損安全 (既存 `detection_lead_ms_median: Option` と同様)。
- `tracing`/`anyhow`、`println!` 不使用。`analysis/` は OS 非依存。
- collector は `MAX_SESSION_BYTES` ガード・パース失敗スキップ (既存 collector と同様)。

## テスト戦略
- 単体: manual_insert_chars 導出 (char−backspace)、比率ゼロ割→None、recovery 判定の境界、
  large/after 閾値の境界、旧 NDJSON (external_paste_chars=null) で panic しない。
- 統合 (Replay-as-Truth): 新 golden fixture + `--metrics --json` 固定値スナップショット。
- `--snapshot` byte-equal 維持を既存テストで確認。

## ロールバック計画
- `outcome: Option` をネスト追加するだけなので、フィールド削除で旧挙動に戻る。
- golden fixture/スナップショットは新規追加なので削除で復旧。
