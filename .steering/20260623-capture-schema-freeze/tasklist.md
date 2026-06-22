# タスクリスト

## ブランチ
- [x] main 基点で `feature/capture-schema-freeze` を作成

## ① Paste external_paste_chars (CD1)
- [x] `logger.rs` `LogEntry::Paste` に `external_paste_chars: Option<u64>` + format/match 更新
- [x] `lib.rs` ペースト処理でクリップボード長取得→即破棄→`Some(n)` で emit (フック外・専用スレッド CD5)
- [x] `schema_dto.rs` `Paste` に `external_paste_chars: Option<u64>`
- [x] `bin/replay.rs` `ReplayEvent::Paste` に `Option` フィールド (後方互換)

## ② InterventionResponse / dismiss_reason (0.8)
- [x] `logger.rs` 新 enum `DismissReason` (as_str/parse) + `LogEntry::InterventionResponse` + format/match
- [x] `schema_dto.rs` `DismissReasonDto` + `LogEntryDto::InterventionResponse`
- [x] `lib.rs` `record_intervention_dismiss` に `reason` 引数追加 → logger へ emit
- [x] `src/components/Overlay.tsx` Nudge に 4択 dismiss UI + invoke 配線 (+ App.css)

## ③ SessionMeta.condition (0.11)
- [x] `logger.rs` 新 enum `Condition` + `SessionMeta` フィールド + format 更新
- [x] `schema_dto.rs` `ConditionDto` + `SessionMeta.condition: Option<ConditionDto>`
- [x] `lib.rs` `record_session_meta` 引数追加 / `src/App.tsx` invoke 更新

## ④ label_pool (0.4, CD2)
- [x] `logger.rs` 新 enum `LabelPool` + `SessionMeta.label_pool`
- [x] `schema_dto.rs` `LabelPoolDto` + `SessionMeta.label_pool: Option<LabelPoolDto>`
- [x] `lib.rs` / `App.tsx` 配線

## テスト・検証
- [x] 単体: 新 enum round-trip / format テスト追加
- [x] `cargo test --workspace` パス (206/206)
- [x] `emit_schema` 再生成 → `src-tauri/schema/current.json` 更新
- [x] gse-dataset 側 schema コピー → `check_schema_parity.py` exit 0
- [x] `gse-replay --snapshot` byte-equal (FeatSnapshot 不変)
- [x] fixture に新 variant 行追加 → replay panic なし
- [x] frontend `tsc --noEmit` / `cargo clippy` クリーン

## レビュー・完了
- [x] code-reviewer + security-checker 並列 (CRITICAL/HIGH なし・中身非漏洩を確認)
- [x] レビュー指摘対応 (CD5 スレッド逃がし / CD6 arboard default-features=false / clipboard warn)
- [x] docs 更新 (glossary に新 5 用語追加)
- [x] /finish-task で /cross-review (jq 導入後 Claude ∥ Codex 両系統正常完了。HIGH=A1/A2/A3 を同期読みで解消、A5 テスト追加、A4 文書化)
- [x] git commit (Refs 付き、`0043380`)
