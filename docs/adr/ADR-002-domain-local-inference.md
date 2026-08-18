# ADR-002: domain-local inference と DomainAdapter 境界

- **ステータス**: **Accepted（研究者採択 2026-08-18・ADR-006 と同時確定）**。
  ⚠️ ただし **trait の範囲を限定して採択した**（下記「採択時の限定」）。実装は
  `.steering/20260818-adr006-head-extraction-wiring/`（2a = 抽出 / 2b = 配線の 2 コミット）。
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

### ⚠️ 採択時の限定（2026-08-18・研究者採択）

★ **実装したのは `DomainInferenceHead` のみで、`DomainAdapter` は Epic 4/5 へ送った。**
さらに `DomainInferenceHead` のシグネチャも上記逐語とは違う形にした。

| 項目 | ADR 逐語 | 実装（2026-08-18） | 理由 |
|---|---|---|---|
| `DomainAdapter` | `ingest` / `feature_snapshot` / `privacy_audit` を含む | ★ **立てていない** | 今回の 2 head（Writing / Coding v0）は**同じ `Features` を消費する**ので `ingest` を分ける必要がない。`ingest` は input 層に食い込むため、実装者が 1 つしか無い状態で境界の形を固定することになる |
| `DomainInferenceHead` | `infer(&mut self, &DomainFeatureSnapshot, &SessionContext) -> WorkStateEstimate` | ★ `head_id()` / `latent_axes(&self, &Features, ime_open)` / `applies_backspace_penalty(&self, ime_open)` | `WorkStateEstimate`（`uncertainty` / `evidence_quality` 必須）は **Decision Engine 境界（ADR-004）とセット**で入れるべきもの。現行 engine に `evidence_quality` の消費者がまだ無い |

★ **`DomainInferenceHead` を trait 化する根拠は Coding head v0 の追加で実際に立った**（実装者が 2 つになった）。
`DomainAdapter` の方は 2 つ目の実装者（Coding Adapter・Epic 4 observe-only）が現れた時点で立てる。
根拠は `.steering/20260818-adr006-head-extraction-wiring/decisions.md` **D-8**。

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

> ★ **2026-08-18: step 1 / step 2 は実施済み。** `HMM_VERSION` は 2a で `0.3.0` 据え置き、
> 2b で `0.4.0` へ bump した。ゴールデンは既存 4 本が byte-equal のまま、新規 1 本を追加して 5 本。
> 実測は `.steering/20260818-adr006-head-extraction-wiring/diff-intent-2b.md`。

1. Phase1 完了後（★ Phase1 は **2026-08-18 に収集打ち切りで終了**。verdict = `inconclusive` /
   GATE3 = `DataInsufficient`）。`engine.rs`/`features.rs` を Writing domain 配下（`adapters/writing/` or `analysis/legacy_hmm/`）へ論理隔離。
   これは**抽出のみ・挙動非変更＝`HMM_VERSION` 不変**（β 選択ロジックは変えない。task_kind→β 配線で bump するのは
   **ADR-006 Phase 2b の別サブフェーズ**で、本 ADR の抽出とは分ける）。
2. **replay 出力の byte-equal 一致**を CI 相当のローカル検証で必ず確認（`ml-workflow`/テスト方針）。
3. Coding Adapter は observe-only（Epic 4・第4ラウンド後）。Creative は feasibility のみ（Epic 6）。
