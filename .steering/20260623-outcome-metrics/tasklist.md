# タスクリスト — outcome-metrics (v2 採用)

## 実装 (metrics.rs)
- [x] `OutcomeConfig`(既定値+根拠) / `StuckTrigger` / `StuckEpisode` / `OutcomeMetrics` /
      `PasteEvent` / `KeyPress` 型を追加
- [x] `is_text_producing(vk)` / `is_backspace(vk)` content-free 述語を追加
- [x] `segment_stuck_episodes(feats, cfg)` (merge-gap 統合) を追加
- [x] `compute_outcome_metrics(...)` (a)(b) 指標算出 (`compute_recovered_at` 再利用)
- [x] `SessionMetrics.outcome: Option<OutcomeMetrics>` 追加 (既存構築箇所は None)
- [x] format_pretty に outcome 行追加
- [x] 単体テスト (episode 統合境界 / manual_insert_chars / ゼロ割→None / 真理値表 / null 耐性)
- [x] excluded_paste_count 追加 (code-reviewer MEDIUM 対応)

## 実装 (replay.rs)
- [x] `collect_paste_events()` / `collect_key_events()` collector 追加 (size guard・skip)
- [x] `--metrics` 経路で outcome を算出し attach・pretty/json 両出力
- [x] tests/fixtures/outcome_metrics.ndjson golden (stuck→paste / stuck→manual-recovery)
- [x] `--metrics --json` outcome 固定値スナップショットテスト (Replay-as-Truth)

## テスト
- [x] cargo test --workspace パス (220 passed)
- [x] features/loop_step 不触 → FeatSnapshot 構造不変 (snapshot 意味不変)
- [x] emit_schema byte-equal (NDJSON schema 不変・parity 不要)
- [x] clippy 新規コードに警告なし (既存 abs_diff/median 等は対象外)

## レビュー
- [x] code-reviewer + security-checker 並列: CRITICAL/HIGH なし。MEDIUM 2 件対応
      (excluded_paste_count 追加 / 行長は脅威モデル明記で受容 CD-OM6)

## ドキュメント
- [x] functional-design.md (UC-OM1) / glossary.md (4 用語) 追記

## 完了処理
- [x] decisions.md 作成 (CD-OM1〜6)
- [ ] /finish-task で /cross-review (Claude ∥ Codex)・git コミット
