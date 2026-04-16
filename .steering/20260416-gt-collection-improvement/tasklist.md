# タスクリスト

## 準備
- [x] 関連する docs を読む
- [x] 影響範囲を file-finder / impact-analyzer で調査
- [x] /reimagine で設計案比較、v2 採用

## 実装

### T1: LogEntry::ReviewMarker + スキーマ同期 (アトミック)
- [x] logger.rs に LogEntry::ReviewMarker { timestamp: u64 } バリアント追加
- [x] logger.rs に NDJSON フォーマット ("type":"review_marker") 追加
- [x] schema_dto.rs に LogEntryDto::ReviewMarker バリアント追加
- [x] replay.rs の ReplayEvent に ReviewMarker バリアント追加
- [x] `cargo run --bin emit_schema` で schema/current.json 再生成

### T2: レビューマーカー hotkey 登録
- [x] lib.rs の shortcuts 配列に Code::KeyR 追加
- [x] lib.rs の with_handler クロージャに KeyR 分岐追加 (LogEntry::ReviewMarker 送信)

### T3: metrics.rs に RangeLabel + 範囲マッチング
- [x] RangeLabel 型定義 (start_ms, end_ms, label: LabelClass)
- [x] compute_range_metrics() 関数: 範囲内全 feat と label を比較して confusion matrix 構築
- [x] format_pretty 拡張 → 不要 (既存の format_pretty がそのまま使える、SessionMetrics 型は同一)

### T4: replay.rs に --segment モード (セグメントファイル生成)
- [x] Args に segment フラグ追加、parse_args() 拡張
- [x] セグメント分割ロジック (キーストローク沈黙 ≥ 5s 境界検出)
- [x] .segments.txt 出力 (活動指標テーブル + レビューマーカーハイライト)
- [x] usage() にヘルプ追記

### T5: replay.rs に --segments モード (範囲マッチング統合)
- [x] Args に segments パス追加、parse_args() 拡張
- [x] .segments.txt パーサー (ラベル行解析、コメント/ヘッダースキップ)
- [x] --segments で compute_range_metrics() 呼び出し → SessionMetrics 出力
- [x] --json との組み合わせ対応

## テスト
- [x] T3: 範囲マッチング (RangeLabel × feats → confusion matrix) のユニットテスト (4 tests)
- [ ] T1: logger.rs ReviewMarker フォーマットのユニットテスト (省略可: コンパイラ match 網羅で保証)
- [ ] T4/T5: セグメント分割・パーサーのユニットテスト (省略可: 統合テストで確認済み)
- [x] 統合: 実セッション → --segment → ラベル → --segments パイプライン確認
- [x] 既存テスト全通過確認 (cargo test) — 60/60 PASS、回帰なし

## レビュー
- [x] code-reviewer によるレビュー (HIGH 2, MEDIUM 4, LOW 3)
- [x] security-checker (MEDIUM 3, LOW 3, CRITICAL/HIGH なし)
- [x] HIGH 指摘への対応 (排他チェック修正, feat_count rename)
- [x] MEDIUM 指摘への対応 (サイズガード, ヘッダースキップ, start>end検証, デバウンス)

## ドキュメント
- [x] docs/architecture.md §4.8 に範囲マッチングの記述追加
- [x] docs/functional-design.md §7 に事後レビュー方式の記述追加

## 完了処理
- [x] design.md の最終化
- [ ] baseline_metrics.md で既存セッションの事後レビュー実施 → 次タスクで GT 収集時に実施
- [x] /finish-task
