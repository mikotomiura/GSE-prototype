# ADR-004: Decision Engine 境界（pure function 化）と Consent 軸の新設

- **ステータス**: Accepted（境界方針）。Consent 軸の実装は Epic 3・Phase1 完了後。
- **日付**: 2026-07-24
- **関連**: `intervention-decision-engine.md`・設計書 §3.7/§8.3/Step 3

## Context
GSE v2 は Need / Opportunity / Receptivity / Consent / Policy を分離し、Decision Engine を replay 可能な
純粋関数にすることを求める（設計書 §8.3）。現行実態（Epic 0）:
- `intervention.rs` は **Need（`need_score=p_stuck`）と Opportunity（`opportunity_score`）を既に分離**。
- 閾値は `InterventionThresholds` により `new_with_thresholds` で注入可能 = **pure 化の入口はある**
  （ただし `InterventionPolicyState` は day_index/cooldown/cap/履歴など十数個の可変状態を持ち、
  純粋 `decide()` への切り出しは state と判定の分離設計を要する。「容易」ではない）。
- `InterventionAction{None,Nudge,Wall,Defer}` で **`none`/`defer` は第一級実装済み**。
- **Consent 軸（`SupportConsent`）は未実装**。decision reason code のログ化・`policy_version` 刻印は未実装。

## Decision
Decision Engine を `fn decide(input: &DecisionInput, policy: &PolicyConfig) -> DecisionOutput` の**純粋関数**に整理する。
主作業は (1) **Consent 軸の新設**（`SupportConsent==ObserveOnly → none`）、(2) **decision reason code のログ化**、
(3) **`policy_version` のログ刻印**。Need/Opportunity は既存分離を維持。

> ⚠️ Consent ゲート（`ObserveOnly → none`）は**倫理・自律性の原則**による正当化であり、**効果エビデンスではない**
> （`gse-v2-overview.md §5`）。`support_consent` は自己申告なので receptivity の主軸には据えない（[V43] 逆風）。

## Alternatives
- **現状維持（Consent なし）**: opt-in の倫理ゲートを持てない。研究倫理上不可。却下。
- **Consent を receptivity スコアに溶かす**: 自己申告を主軸化し [V43] に反する。分離した硬いゲートにする。
- **大規模リライト**: 既に分離済みのため過剰。既存構造の pure 化 + Consent 追加に留める。

## Consequences
- golden test / offline replay / MRT simulation / threshold sensitivity / policy version 比較が容易になる（設計書 §8.3）。
- `DismissReason` に `bad_timing`/`not_helpful` を additive 追加（schema 変更・低リスク・migration-risk-register）。
- `none`/`defer` の観測可能性は既に enum で確保済み → reason code を足すのみ。

## Migration
1. Phase1 完了後（`intervention.rs` 閾値定数は凍結・**変更しない**）。
2. `decide()` を pure function 化し **既存 action を golden test で再現**（動作非変更）。
3. `SupportConsent` を `DecisionInput` に追加し `ObserveOnly → none` ゲートを実装。
4. reason code + `policy_version` をログへ（logger schema は additive・`emit_schema` diff 確認）。
