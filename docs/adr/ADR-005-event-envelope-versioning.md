# ADR-005: Event Envelope の schema versioning

- **ステータス**: Proposed（方向合意）。確定は Epic 2/5・Phase1 完了後。
- **日付**: 2026-07-24
- **関連**: `domain-adapter-boundary.md §Layer 2`・設計書 §3.4/§8

## Context
v2 は全ドメイン共通の**イベント外枠** `EventEnvelope` / `EventFamily` を導入する（設計書 §3.4）。現行実態（Epic 0）:
`schema_dto.rs` は **schemars ベースで `emit_schema` により JSON Schema を機械生成**し、`schema/current.json` と
byte-equal 比較で **CI が drift 検知**する。`EventEnvelope`/`EventFamily` は未実装（新規追加）。NDJSON schema は
Phase1 の**凍結対象**（変更すると gse-dataset 連携・CI drift が破綻）。

## Decision
`EventEnvelope`（`schema_version: u16` を持つ）と `EventFamily` を **additive** に導入する。既存 NDJSON schema は
**変更せず**、新イベント族は新フィールド/新レコードとして加える。`adapter_id`/`adapter_version`/`schema_version` で
バージョンを明示し、`EventFamily` は「分析上の同一性を保証しない・データ配管と監査の共通分類」と定義する。

## Alternatives
- **既存 schema を作り直す（breaking）**: Phase1 凍結・gse-dataset 連携・golden を破壊。却下。
- **envelope を作らずドメインごと個別 schema**: 監査・replay の共通基盤が持てない。共通外枠のみ導入する。
- **`EventFamily` に分析的意味を持たせる**: Backspace≠Undo の早期同一化に逆行（設計書 §3.4 設計判断）。禁止。

## Consequences
- `emit_schema` の出力に additive 差分が出る → `schema/current.json` を**意図的に**再生成し diff を記録する
  （Phase1 完了後・migration-risk-register）。それまで着手しない。
- 本文非保存の禁止事項（raw text/clipboard/prompt/code/window title/path/URL/repo name/PII）を envelope の
  `privacy_class` と `privacy_audit()`（ADR-002）で機械的に担保する（`data-privacy` Skill）。

## Migration
1. Phase1 完了まで schema を触らない（凍結）。
2. Epic 2（Writing Adapter）で `EventEnvelope` を additive 導入 → `emit_schema` diff を確認し `.steering/` に記録。
3. Gate 群の schema 化（Gate D/S/H）は Epic 5 で本 envelope 上に構築。
