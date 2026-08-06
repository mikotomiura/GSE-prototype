# タスクリスト — replay-category

## 準備
- [x] 関連 docs 先読み (decisions.md D4/D6 / anonymization.md / anonymize.rs / dev-guidelines §3)
- [x] 影響範囲調査 (replay.rs Key パース・features.rs is_backspace 由来・loop_step repeat 検出・schema_dto)

## 実装
- [x] `ReplayEvent::Key` を vk: Option / category: Option 両対応に
- [x] `category_representative_vk` / `resolve_key_vk` を追加
- [x] `run_replay` Key アームを解決 VK で構築 (解決不能は warn skip)
- [x] `collect_key_events` Key アームを解決 VK で構築

## テスト
- [x] `category_representative_vk_roundtrips` (from_vk 逆写像 + is_backspace + is_text_producing 不変条件)
- [x] `replay_event_key_accepts_vk_and_category` (両 JSON 形)
- [x] `replay_anonymized_matches_raw_features` (minimal: timestamp 除く特徴量一致)
- [x] `replay_anonymized_matches_raw_features_all_categories` (全 category 網羅・特徴量一致)
- [x] `anonymized_metrics_text_producing_undercounts_other_folded_keys` (D-RC3 制約を明示ロック)
- [x] golden fixture `minimal.anon.ndjson` + `category_coverage.ndjson` 追加 + drift-guard テスト
- [x] `cargo test --workspace` 緑 (217) / bin 22 緑 / 既存 --snapshot byte-equal 不変 / emit_schema parity 不変

## レビュー
- [x] code-reviewer + security-checker 並列 (security: CRITICAL/HIGH なし)
- [x] code-reviewer CRITICAL (--metrics text-producing 発散) を D-RC3 で対応 (run_replay は exact・制約を文書化+テストロック)
- [x] /cross-review (Codex) — 新規 actionable は test 堅牢化 2 件 (checked_sub / anon 非空 assert) を採用
- [x] CRITICAL/HIGH 対応完了

## 完了処理
- [x] design.md 最終化 / decisions.md 作成 (D-RC1..D-RC4)
- [x] git commit (feature/replay-category be85b62) → PR #29
