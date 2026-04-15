# Phase 1 Task 2/3: Metrics 算出エンジン

## 背景

Phase 1 Task 1（`.steering/20260415-phase1-ground-truth/`）で `LogEntry::UserLabel` の記録基盤と OS グローバルホットキー入力経路が整った。しかし記録されたラベルと HMM 推定結果を**定量比較する算出基盤がまだ存在しない**。`gse-replay` は現状 `--snapshot` による byte-equal 回帰保護のみで、precision / recall / F1 等の分類メトリクスを吐かない。

Phase 2a（Synthetic Friction 再設計）以降で「アルゴ変更前後でどれだけ改善したか」を数値根拠付きで判定するには、先に Phase 1 で**混同行列 + 検出リード/ラグ + Stuck 回復時間**を安定的に算出できる CLI が必要。

## ゴール

`gse-replay --metrics <session.ndjson>` を実行すると、UserLabel と FeatSnapshot ストリームを突き合わせて以下を算出・出力する:

- 3×3 混同行列（正解 UserLabel × HMM argmax）
- 各クラスの precision / recall / F1 + macro / micro 平均
- 検出リード/ラグ時間の中央値（HMM が各ラベル時刻の前後でどれだけ先行/遅延して高確率を出したか）
- Stuck 回復時間の中央値（Stuck ラベル以降、`p_flow > 0.5` に達するまでの時間）

`--json` フラグで構造化 JSON を標準出力に吐き、Python ヘルパー（別セッションで追加可）や多セッション集計スクリプトから消費できるようにする。`recovered_at` はログ記録時ではなく**この metrics 計算時にオフライン純粋関数で後付け算出**する。

## スコープ

### 含むもの
- `src-tauri/src/analysis/metrics.rs` 新規（純粋計算モジュール、analysis/ 純粋性維持）
  - `compute_recovered_at(stuck_ts, feats, window_ms) -> Option<u64>`
  - `compute_session_metrics(labels, feats) -> SessionMetrics`
  - `SessionMetrics` / `ConfusionMatrix` / `LabelClass` を `serde::Serialize` 付与で定義
- `src-tauri/src/bin/replay.rs` 拡張
  - `ReplayEvent::UserLabel` バリアント追加（NDJSON `"type":"user_label"` 分岐）
  - `Args` に `metrics: bool` / `json: bool` フィールド追加
  - `--metrics` と `--snapshot` の排他チェック（両指定は Usage エラー）
  - `--metrics` 単体: pretty-print 出力、`--metrics --json`: `serde_json::to_string_pretty`
  - UserLabel 欠落セッションに対する警告 + 空集計対応（panic 禁止）
- `.steering/20260415-phase1-ground-truth/baseline_metrics.md` 雛形作成（テーブルヘッダのみ、運用フェーズで埋める）
- ユニットテスト: `compute_recovered_at` 境界値 + `compute_session_metrics` 合成ケース

### 含まないもの
- Task 1（logger.rs / record_user_label / global-shortcut）の範囲 → 既に実装済み
- Task 3（Dashboard counter widget / E2E / Phase 1 最終レビュー）→ 別タスク
- Python ヘルパー (`ml/analyze.py`) → Phase 1 データ収集後に必要性が見えてから別タスクで
- 多セッション集計機能
- Phase 2a 以降のアルゴリズム改善

## 受け入れ条件

- [ ] `cargo test -p gse-next --lib analysis::metrics` で新規テスト全 PASS
- [ ] `cargo run --bin gse-replay -- <session.ndjson> --metrics` が pretty-print 出力
- [ ] `cargo run --bin gse-replay -- <session.ndjson> --metrics --json` が構造化 JSON 出力
- [ ] `--metrics --snapshot` 併用時に Usage エラーで exit 非ゼロ
- [ ] UserLabel 0 件 NDJSON への `--metrics` 実行で警告 + 空集計（panic なし）
- [ ] Phase 0 ゴールデン `tests/snapshots/minimal.json` byte-equal 維持
- [ ] `baseline_metrics.md` 雛形が配置され、記入手順がコメントで明示されている
- [ ] code-reviewer HIGH 指摘ゼロ

## 関連ドキュメント

- `.steering/20260415-phase1-ground-truth/design.md`（Phase 1 v2 全体設計、特に metrics 関連セクション）
- `.steering/20260415-phase1-ground-truth/design-comparison.md`（v1/v2 比較、採用根拠）
- `src-tauri/src/bin/replay.rs`（既存 `--snapshot` 実装、手書きパーサパターン）
- `src-tauri/src/analysis/loop_step.rs`（FeatSnapshot 構造、Phase 0 で抽出済み）
- `docs/development-guidelines.md`（Replay-as-Truth 方針）

## 運用メモ

- **/reimagine 適用: No**
- **理由**: 設計は Phase 1 全体（Task 1 の design.md v2）で `/reimagine` 済み。Task 2 はそこで採用された「オフライン純粋関数 + Rust 内蔵 + JSON 出力」方針を具体化する実装タスクであり、新たなアーキテクチャ判断はない。
- **前提**: Task 1 が commit 済み（Task 2 は Task 1 の `LogEntry::UserLabel` 定義に依存）
