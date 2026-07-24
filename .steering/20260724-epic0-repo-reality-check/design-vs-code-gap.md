# design-vs-code-gap — 改善設計書 v0.1 と現行コードの差分

> Epic 0 成果物 (2/4)。◎=実装済み / ○=名前違い・分解形で実装 / △=部分 / ✗=未実装 / 記録=schema のみ。

## v2 概念の実装状況

| 設計書の概念 | 状態 | 現行の実体 | 備考 |
|---|---|---|---|
| `p_stuck`（Need の素） | ◎ | intervention.rs `need_score = p_stuck` | 10 ファイルで参照 |
| Need / Opportunity 分離 | ◎ | `need_score` / `opportunity_score` を別計算 | 設計書の中核が既に実装済み |
| `none` / `defer` 第一級 | ◎ | `InterventionAction::{None,Defer}` | 設計書 §3.7 の要求を満たす |
| cooldown / daily_cap / recent_dismiss | ◎ | intervention.rs 定数 + reset ロジック | |
| Monk Mode | ◎ | intervention.rs `monk_mode: bool` → **Wall を抑制** | ★§12-1 解決: Monk Mode = **介入拒否**（強介入許可ではない）。`apply_wall_suppressions` で "monk_mode" を suppressed_by に push |
| `breakpoint_score` | ○ | `OpportunityReason`（post_burst_pause / short/medium/long pause / correction_after_pause） | 単一スコアでなく理由 enum に分解。設計書の breakpoint 合成式は未実装 |
| `receptivity` | ○ | cooldown + daily_cap + recent_dismiss + idle gate の合成 | **統合 receptivity スコアは未実装**（分解形で機能）。§12-4 解決: ルール名のみでなく機構は実在 |
| `task_kind` | 記録 | logger/schema の enum 4 変種。session_meta に記録 | ★**HMM β に未配線**（β は ime_open で切替・engine.rs は task_kind 非受領）。分析パイプラインで dead_code |
| calibration mode | ○ | `Condition::BlindCalibration` + `intervention_enabled` gate + `LabelPool` | 設計書の `calibration_mode: bool` 単体ではなく condition/pool で表現 |
| dismiss 理由分類 | △ | NotStuck/WantToStruggle/JustClose/Silent/EarlyUnlock/Completed | 設計書 §3.6 の `let_me_struggle`=WantToStruggle ◎ / `emergency_unlock`=EarlyUnlock ◎ / **`bad_timing` ✗ / `not_helpful` ✗** |
| `WorkIntent`(SelfDirected/Obligatory/LowIntent) | ✗ | なし | 設計書 §3.2 の新規概念。Session Context 層ごと未実装 |
| `SupportConsent`(ObserveOnly/Light/Strong) | ✗ | なし | 同上 |
| `EventEnvelope` / `EventFamily` | ✗ | なし | 設計書 §3.4 の共通イベント外枠。未実装 |
| Domain `adapter` / DomainAdapter trait | ✗ | なし | input/ が直接 analysis/ へ。Writing/Coding/Creative の分離なし |
| `uncertainty` / `evidence_quality` | ✗ | なし | WorkStateEstimate の必須フィールド (設計書 §3.5)。未実装 |
| `agency_balance` 等 coding proxy | ✗ | なし | Adapter B。設計書 §3.3 |
| Accountability Extension | ✗ | なし | 設計書 §4 |

## 旧 Flow/Incubation/Stuck 三状態表示の残存 ★設計書 §2.3「捨てる主張」対象

- `src/App.tsx:65-98` — `cognitiveState { flow, incubation, stuck }` 型と初期値が残存。
- `src/App.tsx:195` — `setCognitiveState({ flow:1.0, ... })`。
- `src/components/Dashboard.tsx:22` — `type LabelKind = "flow"|"incubation"|"stuck"`。
- `src/components/Dashboard.tsx:189-190` — `flow>=incubation && flow>=stuck ? 'Flow' : ...` で**三状態ラベルを算出・表示**。
- **ただし calibration blind（week1）では非表示に gate されている**（Dashboard.tsx:51 コメント「較正モードでモデル出力を非表示」）。
- → 設計書 §2.3 は「Flow/Incubation/Stuck を正確に分類する」主張の削除を要求。**表示ロジックは debug/非 blind 経路に残存**しており、v2 では連続 proxy 表示へ置換 or 歴史的説明へ降格が要る。

## Phase1 argumentative lock (設計書 §1.1・非変更対象)
- `src/App.tsx:12-17` — `TASK_KINDS` を `argumentative` のみに制限（他 3 種はコメントアウト）。
- `src/App.tsx:114` — 既定 `taskKind="argumentative"`。`:308` 見出し「Phase1 は論述に固定」。
- 復元手順は `.steering/20260629-lock-task-kind-argumentative/restore-task-kind-buttons-prompt.md`。
- **Phase1 完了まで変更禁止**（C-index の task_kind 交絡回避）。

## 設計書 §12 未決事項のコードによる解決状況
| # | 未決事項 | Epic 0 での解決 |
|---|---|---|
| 1 | Monk Mode は介入拒否か強介入許可か | **解決: 介入拒否（Wall 抑制）** |
| 2 | task_kind の現 enum と migration | **解決: 4 変種・schema/logger に実在・β 未配線** |
| 3 | Writing HMM 出力を v2 proxy へどう写像 | 未解決（設計判断・Epic 1 ADR） |
| 4 | receptivity 実装済みか名前のみか | **解決: 機構は cooldown/daily_cap/recent_dismiss で実在・統合スコアは未実装** |
| 5 | window title を読まず focus_role 取得可能か | 未解決（input/ の調査要・Epic 4） |
| 6-8 | agentic coding / creative の対象環境 | 未解決（エビデンス不足・第4ラウンド待ち） |
| 9 | Session Context がプローブを増やしすぎないか | 未解決（設計判断） |
| 10 | Phase1 Kill 時の Writing Adapter 維持コスト | 未解決（Phase1 結果待ち） |
