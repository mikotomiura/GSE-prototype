# タスクリスト: Phase 2a Synthetic Friction — 比例キャリーフォワード

## 準備
- [x] requirement.md 記入済み
- [x] /reimagine 実行 (v2 採用)
- [x] impact-analyzer で波及分析完了

## 実装

### T1: AnalysisState に pre_silence_features 追加 (loop_step.rs)
- [x] `AnalysisState` に `pub pre_silence_features: Option<Features>` フィールド追加
- [x] `new()` で `pre_silence_features: None` 初期化
- [x] `reset()` で `self.pre_silence_features = None` クリア追加
- [x] TypingPath ブランチで `state.pre_silence_features = Some(features.clone())` キャプチャ

### T2: make_silence_observation を文脈対応に (features.rs)
- [x] シグネチャ変更: `pre_silence: Option<&Features>` パラメータ追加
- [x] 文脈ありの場合: 比例キャリーフォワード式で F3/F6 合成
- [x] 文脈なしの場合: 現行の時間ベースランプにフォールバック
- [x] SilencePath の呼び出し更新 (loop_step.rs:310)

### T3: TransitionPath の摩擦フロアを文脈ベースに (loop_step.rs)
- [x] `pre_silence_features` を参照して F3/F6 フロアを計算
- [x] 文脈なし時は現行ロジックをフォールバック維持

### T4: HMM_VERSION bump (engine.rs)
- [x] バージョンコメント更新 (0.2.0 → 0.3.0)

## テスト

### T5: 既存テスト更新 (features.rs)
- [x] 7 テストのシグネチャを `(silence_secs, None)` に更新 (フォールバック互換)
- [x] 文脈あり版のテストケース追加 (clean → F3/F6 ≈ 0)
- [x] 文脈あり版のテストケース追加 (high friction → F3/F6 高)
- [x] 境界テスト: silence_secs = 2.0, 32.0 + below 2s with context

### T6: ゴールデンスナップショット再生成
- [x] `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson > tests/snapshots/minimal.json`
- [x] diff: snapshot[9] の f6 が 0.00133→0.0 に変化 (TransitionPath の文脈ベースフロア適用結果)

### T7: GT 回帰テスト
- [x] Windows 5 セッションで `gse-replay --segments` before/after 比較
- [x] 全セッション metrics が変更前と完全一致 (replay はログ済み feat を使用するため影響なし)
- [x] 回帰なし確認済み

### T8: cargo test 全通過
- [x] `cargo test` 全 69 件 PASS

## レビュー
- [x] code-reviewer (HIGH 1, MEDIUM 4, LOW 3)
- [x] HIGH: Features に Copy derive 追加
- [x] MEDIUM: SilencePath/TransitionPath の式の違いにコメント追記
- [x] MEDIUM: silence-break protection で pre_silence_features クリア追加
- [x] MEDIUM: ctx 入力値を .clamp(0.0, 1.0) でガード

## ドキュメント
- [x] docs/architecture.md §4.10 の摩擦フロア比較表更新 (Phase 2a 比例キャリーフォワード反映)

## 完了処理
- [x] /finish-task
