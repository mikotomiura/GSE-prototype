# タスクリスト — Phase 1 Task 2: Metrics 算出エンジン

## 準備
- [x] `.steering/20260415-phase1-ground-truth/design.md` の metrics 関連セクション再読
- [x] `src-tauri/src/bin/replay.rs` の既存 `--snapshot` 実装を読む（L106-213）
- [x] Task 1（ground-truth）が commit 済みであることを確認

## 実装
- [x] M2-1: `src-tauri/src/analysis/snapshot.rs` 新規 or `replay.rs` の `FeatSnapshot` 型を `analysis::metrics` から参照できる形に整理（Open 点を決着）
- [x] M2-2: `src-tauri/src/analysis/metrics.rs` 新規作成
  - [x] `LabelClass` / `ConfusionMatrix` / `ClassMetrics` / `SessionMetrics` / `UserLabelEvent` 型定義
  - [x] `compute_recovered_at(stuck_ts, feats, window_ms, p_flow_threshold)`
  - [x] `compute_session_metrics(labels, feats)`（混同行列 / F1 / 中央値）
  - [x] HMM argmax のタイブレーク（Flow > Incubation > Stuck）
- [x] M2-3: `analysis/mod.rs` に `pub mod metrics;` 追加
- [x] M2-4: `bin/replay.rs` の `ReplayEvent` に `UserLabel` バリアント追加、NDJSON パース分岐
- [x] M2-5: `Args` 構造体に `metrics: bool` / `json: bool` 追加、手書きパーサ拡張
- [x] M2-6: `main()` に metrics 分岐追加、`--snapshot` との排他チェック
- [x] M2-7: pretty-print 関数実装（design の出力形式に準拠）
- [x] M2-8: JSON 出力（`serde_json::to_string_pretty`）
- [x] M2-9: UserLabel 欠落セッション対応（警告 + 空集計、panic なし）
- [x] M2-10: `.steering/20260415-phase1-ground-truth/baseline_metrics.md` 雛形作成（テーブルヘッダのみ + 記入手順コメント）

## テスト
- [x] T-M1: `compute_recovered_at` 境界値 4 ケース（正常 / 窓超過 / 連続 Stuck / 空 feats）
- [x] T-M2: `compute_session_metrics` 合成 4 ケース（全正解 / 完全逆転 / 空 / timestamp ずれ）
- [x] T-M3: `cargo test -p gse-next --lib analysis::metrics` 全 PASS
- [x] T-M4: `cargo test --workspace` 退行ゼロ
- [x] T-M5: `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` byte-equal 維持
- [x] T-M6: `--metrics --snapshot` 併用で exit 非ゼロ + Usage エラー

## レビュー
- [x] R-M1: `code-reviewer` 起動（Rust スコープ）
- [x] R-M2: HIGH 指摘対応

## ドキュメント
- [x] D-M1: `docs/development-guidelines.md` に `--metrics` の使い方を追記（Replay-as-Truth セクション拡張）
- [x] D-M2: `README.md` / `README.ja.md` に `gse-replay --metrics` サンプル追加

## 完了処理
- [x] design.md の Open 点（FeatSnapshot 配置 / argmax 定義 / リード・ラグ定義）に実装確定状態を追記
- [x] decisions.md 作成（上記 Open 点の決着根拠）
- [x] git commit: `feat(gt): offline metrics computation (--metrics, --json) (Phase 1 task 2/3)`
