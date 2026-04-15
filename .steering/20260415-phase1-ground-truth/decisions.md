# Decisions — Phase 1 Task 1: Backend ログ基盤 + GT 入力経路

## D1: `/reimagine` v2 を採用 — 「汚染源を発生させない」方針

### 背景
初期案 (design-v1.md) は `CognitiveStateEngine` に「Ground Truth 入力中は emit をフリーズ」フラグを追加する案だった。`/reimagine` で v2 を再生成し、production path を一切触らない方針に切り替えた。

### 採用理由
- **production path 汚染ゼロ**: engine / features / hook / loop_step に変更が入らないため、Task 1 の変更は Task 2/3（metrics 算出・Counter UI）の挙動を変えない。
- **派生値はオフライン計算**: `recovered_at` を production で計算すると閾値定数 (例: p_stuck < 0.30) が engine に漏れる。v2 では `recovered_at: None` で記録し、`gse-replay --metrics`（Task 2）で純粋関数として後付け計算する。HMM 再チューニング時に過去ログを再処理できる。
- **テスト容易性**: `format_user_label_line` を純粋関数として切り出し、logger.rs の `#[cfg(test)]` で 8 本の境界値ユニットテストを独立記述できる。

### v2 スコープ
1. `UserLabelKind` enum + `LogEntry::UserLabel` バリアント（logger.rs）
2. `record_label_internal` 共通ヘルパー（lib.rs, Tauri コマンド + ホットキー両経路で共用）
3. `tauri-plugin-global-shortcut` 導入 + capability 3→2 件（是正後）
4. 2 秒デバウンス（race-free: `compare_exchange`）

## D2: デバウンスは `compare_exchange` ループ（race-free）

### 背景
初版は `LAST_LABEL_MS.load() → 比較 → store()` の非アトミック実装。Tauri コマンド経路とホットキー経路がほぼ同時発火すると両方通過してログが重複する TOCTOU レースがあった（code-reviewer / security-checker 双方が MEDIUM 指摘）。

### 対応
`LAST_LABEL_MS.compare_exchange(last, now, Relaxed, Relaxed)` ループで「now 書き込みに勝ったスレッドだけ通す」race-free 実装に変更。実害は重複 1 件と小さいが、race 再現テストが困難で回帰検知しづらいため即時修正した。

## D3: `global-shortcut:allow-is-registered` 権限を削除

### 背景
capabilities/default.json に register/unregister/is-registered の 3 件を追加していたが、`is-registered` は現状未使用。将来 Dashboard から照会する具体計画もない。

### 対応
YAGNI に従い削除。register / unregister の 2 件に縮小（最小権限原則）。必要になった時点で追加する。

## D4: `record_user_label` の Tauri イベント emit 失敗を warn に記録

### 背景
初版は `let _ = app.emit(...)` で結果を捨てていたが、ホットキー経路は `match { Err(e) => tracing::warn!(...) }` で記録していた。非対称。

### 対応
`if let Err(e) = app.emit(...) { tracing::warn!("user_label_recorded emit failed: {}", e); }` で両経路の観測性を揃えた。

## 参考: スキップした指摘

- **`record_user_label` の Tauri コマンド unit test 欠如** — code-reviewer 提案。却下: AppHandle モックが必要で overhead 大、本体ロジック（parse / format / debounce）は logger.rs の 8 本ユニットテスト + `record_label_internal` のシンプルさでカバー済み。E2E は Task 3 (`phase1-counter-ui/`) で実施。

## レビューサマリ

- code-reviewer: HIGH 0, MEDIUM 3（すべて対応済: D2/D4 + is-registered）, LOW 少数
- security-checker: HIGH 0, MEDIUM 1（D2 で対応済）, LOW のみ
- プライバシー規約: 文字内容記録なし、ラベルは enum 3 値 + サーバー側 timestamp のみ
