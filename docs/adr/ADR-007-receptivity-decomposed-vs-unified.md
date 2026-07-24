# ADR-007: receptivity を統合スコア化するか分解形を維持するか

- **ステータス**: Accepted（**分解形の維持を推奨**）。再訪は Epic 3。
- **日付**: 2026-07-24
- **関連**: `intervention-decision-engine.md §Layer 5`・設計書 §3.6

## Context
設計書 §3.6 は receptivity の候補入力を列挙する（recent dismiss / dismiss reason / cooldown / daily cap /
time of day / intervention history / support consent / Monk Mode / current active operation / prior annoyance /
task kind / evidence quality）。現行実態（Epic 0）: receptivity は **単一スコアでなく cooldown + daily_cap +
recent_dismiss + idle gate の合成（分解形）**で機能。統合 receptivity スコアは未実装。

## Decision
**分解形（個別ゲートの合成）を維持する**。単一の連続 `receptivity` スコアには**集約しない**。

## Alternatives
- **統合スコア化（`receptivity: f32` 一本）**: `DecisionInput` の見た目は単純だが、(i) 各ゲートの発火理由が
  観測不能になり decision reason code（ADR-004）と相性が悪い、(ii) `support_consent`（自己申告）を
  連続重みで混ぜると [V43] の逆風を受ける、(iii) 閾値 sweep の解釈が難しくなる。却下。
- **完全分解（合成もしない）**: 現行が既に合成ゲートで機能しており、意思決定に最低限の合成は要る。過剰。

## Consequences
- 各抑制の理由（cooldown/daily_cap/recent_dismiss/idle/Monk Mode/Consent）が**観測可能なまま**残り、
  `intervention_eval.rs` の判断性能分析・reason code ログと整合。
- `support_consent` は連続重みでなく**硬いゲート**（`ObserveOnly → none`・ADR-004）として扱える。
- 将来「効果がある統合指標」を作りたくなったら**専用のエビデンス確認が先**（現状は根拠なし）。

## Migration
1. 現行の分解ゲート構造を維持（Phase1 凍結と両立・ゼロ変更）。
2. Epic 3 で reason code をログ化する際、各ゲートを個別フラグとして残す。
3. 統合スコア化は本 ADR を Superseding する将来 ADR + エビデンスが揃うまで着手しない。
