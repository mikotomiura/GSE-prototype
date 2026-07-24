# ADR-002: domain-local inference と DomainAdapter 境界

- **ステータス**: Proposed（方向合意）。抽出の確定は Epic 2・Phase1 完了後。ADR-006 と一体で確定。
- **日付**: 2026-07-24
- **関連**: `domain-adapter-boundary.md`・設計書 §3.1/§3.3/§8.1/§8.2

## Context
現行は `input/`（OS 固有入力）が直接 `analysis/`（HMM）へ繋がり、Writing/Coding/Creative の分離が無い
（Epic 0: adapter 層 0 ファイル）。GSE v2 は「特徴抽出と較正を domain-local にし、共通化はログのメタ構造と
Decision Engine へ渡す proxy インターフェースのみ」に限る（設計書 §3.1 の制約）。異なるタスクの意味を早期に
同一化してはならない（Writing の Backspace と動画の Undo を同じ重みにしない）。

## Decision
`input/ → analysis/` の直結に **`DomainAdapter` trait を挟む**。各ドメインは domain-local な features/head を持ち、
出力は共通 `WorkStateEstimate`（uncertainty/evidence_quality 必須）で Decision Engine へ渡す。共通化は
`EventEnvelope`（外枠・ADR-005）と `WorkStateEstimate`（proxy IF）に限定する。

```rust
trait DomainAdapter { fn adapter_id(&self)->&'static str; fn task_kind(&self)->TaskKind;
    fn ingest(&mut self, e: PlatformEvent)->Vec<EventEnvelope>; fn feature_snapshot(&self)->DomainFeatureSnapshot;
    fn privacy_audit(&self)->PrivacyAuditResult; }
trait DomainInferenceHead { fn head_id(&self)->&'static str;
    fn infer(&mut self, f:&DomainFeatureSnapshot, c:&SessionContext)->WorkStateEstimate; }
```
最初の具体は **Writing Adapter**（現行 features/HMM の**動作非変更**抽出）。

## Alternatives
- **単一パイプラインのまま task_kind 分岐を散在**: 早期同一化の罠・保守困難。設計書 §3.1 に反する。却下。
- **全ドメインを一気に実装**: Agentic/Creative はエビデンス/feasibility 未確定（Epic 4/6）。段階抽出に留める。
- **共通特徴空間で早期一般化**: 設計書が明確に禁止（Backspace≠Undo）。cross-domain は head 出力以降でのみ（Phase4）。

## Consequences
- Writing Adapter 抽出は **replay --snapshot parity / calibration parity / HMM_VERSION 不変 / NDJSON 互換 /
  UI 不変**が acceptance（migration-risk-register・設計書 Step 2）＝**動作非変更リファクタ**。
- head 未較正時は強介入禁止（`domain-adapter-boundary.md §原則`）を Decision Engine と配線。
- β の所属（IME 代理 vs task_kind 選択）は **ADR-006** と同時確定（不可分）。

## Migration
1. Phase1 完了後。`engine.rs`/`features.rs` を Writing domain 配下（`adapters/writing/` or `analysis/legacy_hmm/`）へ論理隔離。
   これは**抽出のみ・挙動非変更＝`HMM_VERSION` 不変**（β 選択ロジックは変えない。task_kind→β 配線で bump するのは
   **ADR-006 Phase 2b の別サブフェーズ**で、本 ADR の抽出とは分ける）。
2. **replay 出力の byte-equal 一致**を CI 相当のローカル検証で必ず確認（`ml-workflow`/テスト方針）。
3. Coding Adapter は observe-only（Epic 4・第4ラウンド後）。Creative は feasibility のみ（Epic 6）。
