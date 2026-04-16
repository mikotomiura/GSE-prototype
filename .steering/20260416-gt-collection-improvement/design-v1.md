# 設計 v1: ハイブリッド (事後セグメントレビュー + マッチウィンドウ拡大 + レビューマーカー)

## 実装アプローチ

3 つの施策を組み合わせて GT 収集品質を改善する:

### 施策 1: LABEL_MATCH_WINDOW_MS 拡大 (1000→3000ms)
- 現在の detection lead median = -696ms で、ラベルの多くが 1s 窓から漏れている
- 3s に拡大しても HMM は 1Hz 更新なので高々 3 候補、状態遷移リスクは低い
- 即時実行可能な Quick Win

### 施策 2: レビューマーカー hotkey (Cmd+Shift+Option+R)
- `{"type":"review_marker","t":...}` をログに記録
- 認知状態の判断は不要、「ここを後で見返したい」というブックマーク行為のみ
- 事後レビュー (施策 3) の手がかりになる

### 施策 3: gse-replay --review (事後セグメントレビュー)
- セッション NDJSON を 30 秒セグメントに分割
- 各セグメントの活動指標を表示 (打鍵数, median FT, pause 数, correction rate, silence 長)
- レビューマーカーがあるセグメントをハイライト
- ユーザーが stdin で F/I/S を入力
- `.labels.ndjson` サイドカーファイルに出力
- `gse-replay --metrics --labels <file>` でサイドカーラベルを既存ラベルと統合

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/metrics.rs` — LABEL_MATCH_WINDOW_MS 定数を 1000→3000 に変更
- `src-tauri/src/bin/replay.rs` — --review モード追加、--labels オプション追加、collect_user_labels を拡張
- `src-tauri/src/lib.rs` — レビューマーカー hotkey 登録 (global_shortcut handler 拡張)
- `src-tauri/src/logger.rs` — LogEntry::ReviewMarker バリアント追加、NDJSON フォーマット追加

### 新規作成するファイル
- なし (既存ファイルの拡張のみ)

### 削除するファイル
- なし

## 影響範囲

- `gse-replay --metrics` の出力値が変わる (ウィンドウ拡大で warnings 減少、confusion matrix 変動)
- 既存の snapshot テストの golden 値が変わる可能性あり → 再生成が必要
- ラベルフォーマットに `"source"` フィールド追加だが、既存パースは serde default で無視するので後方互換

## 既存パターンとの整合性

- replay.rs の既存 --metrics / --json フラグパターンに倣って --review / --labels を追加
- LogEntry の新バリアント追加は logger.rs の既存パターン (UserLabel, ImeState 等) に従う
- hotkey 登録は lib.rs の既存 shortcuts 配列拡張パターンに従う

## テスト戦略

- 単体テスト: collect_user_labels がサイドカーファイルを正しく統合するか
- 統合テスト: 既存 fixture (phase1_minimal.ndjson) + サイドカーラベルでメトリクス算出
- E2E: 実セッション 1 件で --review → --metrics --labels のパイプラインを通す
- 既存 snapshot テスト: LABEL_MATCH_WINDOW_MS 変更後に再生成

## ロールバック計画

- LABEL_MATCH_WINDOW_MS は定数 1 行の変更なので即戻し可能
- --review / --labels は新規追加のみで既存機能に影響しない
- レビューマーカー hotkey は追加のみ
