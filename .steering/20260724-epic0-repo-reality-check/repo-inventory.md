# repo-inventory — 現行コード実態 (origin/main 9a5e18a・2026-07-24)

> Epic 0 成果物 (1/4)。read-only 走査。パスはすべて実在確認済み。

## ディレクトリ構造 (実在)

### backend `src-tauri/src/`
```
lib.rs               統合・IPC・スレッド起動・介入 gate (safe_default)
main.rs              エントリ
schema_dto.rs        NDJSON JSON Schema の DTO 定義 (emit_schema の真実源)
logger.rs            NDJSON ロガー + enum 定義 (TaskKind/DismissReason/Condition/LabelPool)
wall_server.rs       Lv2 Wall の HTTP エンドポイント
overlay_panel.rs     介入 overlay パネル (Tauri window 制御)
participant_id.rs    P-ID 検証
packaging.rs         age 暗号 (feature=package で隔離)
sensors.rs / sensors_{macos,windows}.rs   センサー dispatcher (platform-specific)

analysis/            ← OS 非依存の推論・介入コア
  mod.rs
  features.rs        5 特徴量抽出 (F1/F3/F4/F5/F6)
  engine.rs          HMM (Forward Algorithm)・HMM_VERSION・β dual baseline
  loop_step.rs       1Hz ゲート・FeatSnapshot 生成 (HMM 挙動の一部)
  intervention.rs    Need×Opportunity 判定・InterventionAction・閾値定数
  intervention_eval.rs   判断性能評価 (HIR/Precision/sweep)
  calibration_eval.rs    C-index・回答率・latency (GATE2/GATE3 算出)
  cohort.rs          被験者横断判定 (cohort_verdict)
  metrics.rs         アウトカム指標 (paste/self-recovery)
  probe_scheduler.rs ランダムプローブ (λ/cap/gap)
  anonymize.rs       匿名化

input/               ← OS 固有入力キャプチャ (platform-specific)
  hook.rs / hook_{macos,windows}.rs
  ime.rs / ime_{macos,windows}.rs
  clipboard.rs
  mod.rs

bin/                 gse-{cohort,replay,submit,package,unpack} + emit_schema
```

### frontend `src/`
```
App.tsx              メイン UI・週セレクタ (week1_blind/week2_intervention)・TASK_KINDS
components/
  Dashboard.tsx      較正 UI・三状態表示 (calibration blind で gate)
  Overlay.tsx        Nudge/Wall 介入カード
  ProbeCard.tsx      ランダムプローブ回答 UI
  VignetteTest.tsx   GATE1 尺度理解テスト
probeTypes.ts        probe 型 (TaskKind 4 変種含む)
```

### test 基盤
```
src-tauri/tests/fixtures/*.ndjson   9 本 (minimal/calib_subject_s1-3/phase1_*/outcome_metrics 等)
src-tauri/schema/current.json       NDJSON JSON Schema (emit_schema と byte-equal 比較で drift 検知)
bin/replay.rs --snapshot            ゴールデン比較経路
engine.rs HMM_VERSION               HMM 挙動変更時に bump → ゴールデン再生成
```

## 4 層と実装境界の対応 (設計書 §3.1 の現行版)
| 設計書の層 | 現行実装 | 状態 |
|---|---|---|
| [3] Domain Event Adapter | **なし**（input/ が直接 analysis/ へ） | v2-redesign 提案のみ |
| [4] Work-State Proxy | `features.rs` → `engine.rs` (HMM) → `loop_step.rs` | 実装済み (Writing 前提) |
| [5] Opportunity & Receptivity | `intervention.rs` の opportunity_score + cooldown/daily_cap/recent_dismiss | 実装済み (receptivity は分解形) |
| [6] Intervention Decision Engine | `intervention.rs` `InterventionAction{None,Nudge,Wall,Defer}` | 実装済み |
| [7] Outcome & Harm Evaluation | `metrics.rs` + `intervention_eval.rs` | 部分実装 (harm は HIR のみ) |

## 主要 enum の実在 (schema_dto.rs / logger.rs)
- `TaskKind` = Argumentative / Correspondence / Creative / VibeCoding（4 変種・schema と logger の両方）
- `InterventionAction` = None / Nudge / Wall / **Defer**（none/defer は第一級で実装済み）
- `DismissReason` = NotStuck / WantToStruggle / JustClose / Silent / EarlyUnlock / Completed / IdleTimeout(予約)
- `Condition` = BlindCalibration / A / B / Nudge / Defer / Baseline
- `LabelPool` = calibration_blind / post_intervention（X1 判定は前者のみ）
- `OpportunityReason` = LowOpportunity / ShortPause / MediumPause / LongPause / PostBurstPause / CorrectionAfterPause (+2)

## 介入発火条件 (intervention.rs 定数・実装準拠)
- `NUDGE_NEED_THRESHOLD = 0.60` / `WALL_NEED_THRESHOLD = 0.70` / `WALL_SLACK_THRESHOLD = 0.50`
- `NUDGE_OPPORTUNITY_THRESHOLD = 0.35` / `WALL_OPPORTUNITY_THRESHOLD = 0.45`
- cooldown / daily_cap / recent_dismiss / idle≥180s で介入全停止（WBS §7 と一致）
- 閾値は `InterventionThresholds` で sweep 可能（`new_with_thresholds`）

## β dual baseline の実態 (engine.rs:278-311) ★重要
- β は **`ime_open` (日本語 IME on/off) で切替**: `ime_open=true → β_writing` / `false → β_coding`。
- **`task_kind` は engine.rs に渡っていない**（`analysis/*.rs` 内で task_kind 参照ゼロ）。
  → task_kind→β 配線は**未実装**。β 選択は IME 状態が代理。
