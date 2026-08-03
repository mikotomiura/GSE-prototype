# Intervention Decision Engine — Layer 5-7 (SSOT)

> **ステータス**: Accepted（方向性・Need/Opportunity/none/defer は既に実装済み）。`gse-v2-overview.md` の
> Layer 5-7 を詳述する。Consent 軸の新設と reason code ログ化は Epic 3（Phase1 完了後）。
> 昇格元: 設計書 §3.6 / §3.7 / §8.3。現行実態: Epic 0 `repo-inventory.md`。

## Layer 5: Opportunity と Receptivity（設計書 §3.6）

GSE v2 の中心として維持する。**現行 `intervention.rs` で既に分解形で実装済み**。

### Opportunity（現行 = `OpportunityReason` enum）
設計書の合成式は**初期ルール baseline の考え方**であり固定式ではない:
```text
breakpoint_score = post_burst_pause + boundary_event + stable_focus
                 + no_active_drag_or_selection + no_active_scroll + return_to_primary_workspace
```
現行実装は単一スコアでなく理由 enum（8 変種）に分解: `LowOpportunity / ShortPause / MediumPause / LongPause /
ActiveTyping / PostBurstPause / CorrectionAfterPause / ActiveCorrectionLoop`（`intervention.rs:59-68`・in-memory のみ、
評価層 `intervention_eval` が reason 別 HIR/Precision の層別化に使う）。統合 `breakpoint_score` 化するかは
**ADR-007** で扱う（現状維持を推奨）。

### Receptivity（現行 = 分解形で機能）
候補入力: recent dismiss / dismiss reason / cooldown / daily cap / time of day / intervention history /
support consent / Monk Mode / current active operation / prior annoyance / task kind / evidence quality。

現行実装は **cooldown + daily_cap + recent_dismiss + idle gate の合成**（統合 receptivity スコアは未実装）。
統合スコア化 vs 分解維持は **ADR-007**。
⚠️ **Receptivity は Layer 5 の概念であり、Layer 4 の潜在状態に置かない**（入力がシステム状態と履歴であって
潜在状態からの放出ではないため、放出モデルが書けない）。**ADR-009 でこの層の所属を再確認済み**。⚠️ `support_consent` は行動指標でなく**自己申告**（[V43] 逆風）のため、
receptivity の**主軸に据えない**（`gse-v2-overview.md §5`）。

### Dismiss reason（設計書 §3.6・現行 `DismissReason`）
最低限分ける: `not_stuck` / `let_me_struggle` / `bad_timing` / `not_helpful` / `silent_dismiss` / `emergency_unlock`。

| 設計書 | 現行 `DismissReason` | 状態 |
|---|---|---|
| not_stuck | NotStuck | ◎ |
| let_me_struggle | WantToStruggle | ◎（**GSE 固有の成功信号**として別集計・失敗ログではない） |
| emergency_unlock | EarlyUnlock | ◎ |
| silent_dismiss | Silent | ◎ |
| bad_timing | — | ✗ 追加候補（additive・Epic 3） |
| not_helpful | — | ✗ 追加候補（additive・Epic 3） |

他に現行は `JustClose / Completed / IdleTimeout(予約)` を持つ。追加は additive（migration-risk-register）。

---

## Layer 6: Intervention Decision Engine（設計書 §3.7）

### 入力/出力案
```rust
struct DecisionInput {
    work_state: WorkStateEstimate,
    breakpoint_score: f32,
    receptivity: f32,
    support_consent: SupportConsent,   // 新規（Consent 軸）
    task_kind: TaskKind,
    recent_dismiss: Option<DismissReason>,
    cooldown_active: bool,
    daily_cap_reached: bool,
    monk_mode: bool,
    calibration_mode: bool,
}

enum InterventionAction {
    None,                              // ◎ 実装済（第一級）
    Defer,                             // ◎ 実装済（第一級）
    Nudge { template_id: String },     // ◎（現行は template_id なし）
    Zen { duration_profile: String },  // Zen Timer（現行 Wall 内 Zen）
    Wall { profile_id: String },       // ◎
}
```
現行 `InterventionAction` = `None / Nudge / Wall / Defer`。`none`/`defer` は**第一級で実装済み**。

### 最低ルール（設計書 §3.7）
```text
calibration_mode == true            → none
intervention_enabled == false       → none
monk_mode == true                   → none   ※ Monk Mode = 介入拒否（Epic 0 で SSOT 確定）
support_consent == ObserveOnly      → none   ※ 新規（倫理・自律性ゲート・効果主張ではない）
daily_cap_reached || cooldown_active→ none
evidence_quality が低い             → none または defer
Need 高 / breakpoint 低             → defer
Need 中〜高 / breakpoint 高 / receptivity 高 → nudge
強介入(Wall/Zen)                    → StrongSupportOptIn かつ domain head 較正済みの場合のみ
```

### 重要（設計書の思想・エビデンス整合）
- `none` は消極的 fallback でなく**第一級の判断**。`defer` は「見逃し」でなく **Opportunity を守る判断**。
  → [V43]（行動指標が受容性を予測・自己申告は予測せず）と整合し、GSE の中核を支える。
- **Wall は v2 Core の必須機能でなく高リスクの実験介入**。`stuck_likelihood` 単独で Wall を発火しない。
- **動機が低いことを理由に Wall や義務感 UI を出さない**（動機不足 ≠ 停滞・設計書 §1.4）。
- Consent 軸（`ObserveOnly → none`）は**倫理・自律性ゲート**であって効果エビデンスではない（過大主張しない）。

### 現行閾値（凍結対象・変更禁止・参考）
`NUDGE_NEED=0.60` / `WALL_NEED=0.70` / `WALL_SLACK=0.50` / `NUDGE_OPP=0.35` / `WALL_OPP=0.45`。
cooldown / daily_cap / recent_dismiss / idle≥180s で介入全停止。`InterventionThresholds`（`new_with_thresholds`）で
sweep 可能。Phase1 完了まで**定数変更禁止**（migration-risk-register）。

---

## Layer 7: Outcome & Harm Evaluation（設計書 §6 Gate 群）

現行 = `metrics.rs`（paste/self-recovery）+ `intervention_eval.rs`（HIR/Precision/sweep）。harm は HIR のみ（部分実装）。
Gate D（Demand・新規）/ Gate S（Sensing・新規）/ Gate H（Harm・新規・拒否権）の schema 化は **Epic 5**。
**Gate H が悪化した場合、X1 が Go でも介入機能は Go としない**（設計書 §6・wbs §改訂予定）。

---

## Decision Engine の pure function 化（設計書 §8.3・Epic 3）

```rust
fn decide(input: &DecisionInput, policy: &PolicyConfig) -> DecisionOutput;
```
現行 `intervention.rs` は既に Need/Opportunity を分離し `new_with_thresholds` で threshold 注入可 = **pure 化の入口はある**。
ただし `InterventionPolicyState` は day_index / nudge・wall count / last_*_at_ms / wall_accum_ms / current_action /
last_log_key 等 **十数個の可変状態**を持つため、pure `decide()` への切り出しは「容易」ではなく **state（cooldown/cap/履歴）と
純粋判定を分離する設計作業**を要する。主作業は **Consent 軸の新設**と **decision reason code のログ化**。

### Epic 3 acceptance（migration-risk-register / 設計書 Step 3）
- 同一入力に対する既存 action を **golden test で再現**（`none`/`defer` の観測可能性は既に enum で確保済み）。
- `none`/`defer` の理由コードを記録・dismiss reason を構造化・**`policy_version` をログに刻印**。

→ 境界整理と Consent 軸の判断は **ADR-004**。

---

## 関連文書
- 上位: `docs/architecture/gse-v2-overview.md`
- 入力側（Layer 0-3）: `docs/architecture/domain-adapter-boundary.md`
- 判断: `docs/adr/ADR-004`（decision engine boundary）／`ADR-007`（receptivity 統合 vs 分解）
- 現行実態: `.steering/20260724-epic0-repo-reality-check/repo-inventory.md`
