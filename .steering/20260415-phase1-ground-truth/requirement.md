# Phase 1: Ground Truth 収集基盤

## 背景

`.steering/20260414-improvement-roadmap/` で策定したハイブリッド採用版ロードマップの Phase 0（Replay & Guard）が 2026-04-15 時点で完了した（条件付き Go：5 条件中 3 達成、条件 1/2 は Phase 1 GT 収集の副産物として並列消化と決定済み、条件 5 は実機確認のみ残）。

現状の HMM 推定エンジン（Flow / Incubation / Stuck の 3 状態推定）は `analysis/loop_step.rs` に抽出され、`gse-replay` CLI で NDJSON から再現可能な状態になった。しかし **HMM 出力が実際のユーザー認知状態をどれだけ正しく推定できているかの定量指標が存在しない**。このまま Phase 2a（Synthetic Friction 再設計）や Phase 3（LR 判断ゲート）へ進むと、改善の効果を数値で判定できず、主観評価で意思決定を重ねるリスクがある。

## ゴール

自分のセッション中にリアルタイムで正解ラベル（Flow / Incubation / Stuck）を付与し、NDJSON に `UserLabel` として記録する仕組みを構築する。さらに `gse-replay --metrics` で HMM 推定との混同行列・precision / recall / F1・検出リード/ラグ時間・Stuck 回復時間中央値を算出できるようにする。GT 付きセッションを 10 件以上収集し、Phase 2a 以降の改善効果を数値で判定するベースラインを確立する。

## スコープ

### 含むもの
- `LogEntry::UserLabel { timestamp, label, recovered_at }` の追加（`logger.rs`）
- GT 付与用 Tauri コマンド（ラベル記録 + エンジン一時停止）
- OS グローバルホットキー (`Cmd+Shift+Option+F/I/S`) + 2 秒デバウンスによる GT 付与
- Dashboard の読み取り専用 counter widget（Flow/Inc/Stuck のラベル数表示 + ショートカット hint）
- Stuck ラベルの `recovered_at` 自動補完（`p_flow` 閾値到達時）
- `gse-replay --metrics` サブコマンド（混同行列 / precision / recall / F1 / リード・ラグ / Stuck 回復時間中央値）
- ベースライン precision / recall の `baseline_metrics.md` への記録
- Phase 0 ゴールデンスナップショット（`tests/snapshots/minimal.json`）の退行チェック

### 含まないもの
- Phase 2a 以降の Synthetic Friction 再設計・文脈ゲート実装
- IME Shadow Features（Phase 2b）
- LR 判断ゲート（Phase 3）
- Lv3 Thought Scaffold UI（Phase 4）
- `macos-input-monitoring-fix`（Phase 1 完了後に別タスクとして着手）
- Phase 0 P0-10 実データ snapshot 3 件の本体切り出し（データ収集期間中に並列消化するが、本タスクの受け入れ条件には含めない）
- 外部テスター募集・実地データ収集の運用
- XGBoost / 1D-CNN などの高度 ML モデル学習

## 受け入れ条件

- [ ] GT 付きセッション ≥ 10 件が `sessions/` 配下に蓄積
- [ ] `gse-replay --metrics <session.ndjson>` が混同行列・precision / recall / F1・検出リード/ラグ・Stuck 回復時間中央値を出力
- [ ] `.steering/20260415-phase1-ground-truth/baseline_metrics.md` にベースライン数値が記録
- [ ] ラベル記録行為が HMM 入力を汚染しないことを実機で確認済み（ホットキー発火前後の keystroke stream に異常がないこと）
- [ ] Phase 0 ゴールデンスナップショット（`tests/snapshots/minimal.json`）の byte-equal 維持
- [ ] `cargo test --workspace` 全 PASS（既存 28 + 新規追加分）
- [ ] `code-reviewer` + `security-checker` の HIGH 指摘すべて対応済み

## 関連ドキュメント

- `.steering/20260414-improvement-roadmap/tasklist.md` L132-183（Phase 1 元タスク定義）
- `.steering/20260414-improvement-roadmap/design.md`（ハイブリッド採用版全体設計）
- `docs/architecture.md` §4.7（沈黙 3 状態機構）
- `docs/functional-design.md`（Lv1/Lv2 介入仕様）
- `docs/development-guidelines.md`（Replay-as-Truth 方針）

## 運用メモ

- **/reimagine 適用: Yes → 実行済み（2026-04-15）、v2 採用**
- **v2 による解決事項**:
  1. GT 付与 UX → **OS グローバルホットキー**採用（5 秒ホールド不採用、Flow を壊さない設計）
  2. IPC 設計 → **単一コマンド `record_user_label`** 採用（`set_engine_paused` は追加しない）
  3. Stuck 回復検出 → **`gse-replay --metrics` 実行時のオフライン純粋関数**で後付け計算（production path 変更なし）
  4. メトリクス算出 → **Rust 内蔵 + `--json` + オプショナル Python ヘルパー** の 2 層
- **根拠ドキュメント**: `design-comparison.md`, `design-v1.md`（退避済み）, `design.md`（v2 確定版）
