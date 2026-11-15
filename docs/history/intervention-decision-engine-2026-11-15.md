> **履歴の文書（2026-11-15 に移した）。** 元のパスは `docs/architecture/intervention-decision-engine.md`。現行の根拠に使わない（ADR-053）。現行は `docs/research-positioning.md`・`docs/architecture/gse-design-map.md`・`docs/adr/`。
> 写しの元: main `6fdd4023`。本文は移す前のまま変えていない。

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
support consent / current active operation / prior annoyance / task kind / evidence quality。
（⚠️ **2026-09-01: 候補から `Monk Mode` を削除** — ADR-015 D2 で削除済み。再導入には新規 ADR が要る）

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
| emergency_unlock | — | ✗ **2026-08-23 に削除**（ADR-015 D1 が Wall 応答 `early_unlock` / `completed` / `idle_timeout` を削除）。再導入には新規 ADR |
| silent_dismiss | Silent | ◎ |
| bad_timing | — | ✗ 追加候補（additive・Epic 3） |
| not_helpful | — | ✗ 追加候補（additive・Epic 3） |

★ **2026-09-01 訂正 —— 現行の `DismissReason` は `NotStuck / WantToStruggle / JustClose / Silent` の 4 値のみ**（実測 `logger.rs:216-221` / `schema_dto.rs:496-501`）。⚠️ **旧文の `Completed` / `IdleTimeout(予約)` は存在しない** ——`schema_dto.rs:493` 逐語「**Wall 応答 (`early_unlock` / `completed` / `idle_timeout`) は 2026-08-23 に削除した**」。★ かつ `completed` は **ADR-018 D3 で UI・表現層・ログのいずれにも置かない語**になった。追加は additive（migration-risk-register）。

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
    Zen { duration_profile: String },  // ✗ 未実装（Zen Timer は ADR-015 D1 で削除済み）
    Wall { profile_id: String },       // ✗ 2026-08-23 に全削除（ADR-015 D1）
}
```
⚠️★★★ **2026-09-01 訂正 —— 現行 `InterventionAction` は `None / Nudge / Defer` の 3 値である**
（実測: `src-tauri/src/analysis/intervention.rs:16-20`）。`none`/`defer` は**第一級で実装済み**。
> ⚠️ **旧文は「現行 `InterventionAction` = `None / Nudge / Wall / Defer`」と書き、
> enum ブロックでも `Wall` に `◎`（＝ 実装済の凡例）を付けていた。**
> ★ **Wall / Zen Timer は ADR-015（2026-08-23）D1 で全削除された** ——
> `InterventionAction::Wall` / Wall 閾値 6 種 / `wall_accum_ms` / daily cap / cooldown / `force_wall` が対象。
> ⚠️★★★ **本節は「入力/出力*案*」なので将来案として挙げること自体は禁じないが、
> 復活させるなら新規 ADR が要る**（★ ADR-015 は削除を決定した ADR であり、上書きには同格の決定が要る）。

### 最低ルール（設計書 §3.7）
```text
calibration_mode == true            → none
intervention_enabled == false       → none
support_consent == ObserveOnly      → none   ※ 新規（倫理・自律性ゲート・効果主張ではない）
daily_cap_reached || cooldown_active→ none
evidence_quality が低い             → none または defer
Need 高 / breakpoint 低             → defer
Need 中〜高 / breakpoint 高 / receptivity 高 → nudge
強介入（★ 現行は存在しない）        → 将来 Wall/Zen 相当を再導入するなら新規 ADR ＋ StrongSupportOptIn ＋ domain head 較正済み
```
> ⚠️★★★ **2026-09-01 訂正 —— 最低ルールから `monk_mode == true → none` の行を削除した。**
> ★ **Monk Mode は ADR-015 D2 で削除済み**（`src-tauri/src/` に `monk_mode` は 0 ヒット）。
> ⚠️ かつ旧文の「**Monk Mode = 介入拒否（Epic 0 で SSOT 確定）**」という理解自体が
> **ADR-015 Context-3 で否定されている** —— 逐語「**Monk Mode は Wall を無効化するだけ**」
> 「**Nudge は引き続き表示される**」。★ **つまり「介入拒否」ではなかった。**
> ⚠️ `DecisionInput` 案の `monk_mode: bool` フィールドも、再導入には新規 ADR が要る。

### 重要（設計書の思想・エビデンス整合）
- `none` は消極的 fallback でなく**第一級の判断**。`defer` は「見逃し」でなく **Opportunity を守る判断**。
  → [V43]（行動指標が受容性を予測・自己申告は予測せず）と整合し、GSE の中核を支える。
- ⚠️★★★ **Wall は 2026-08-23 に全削除された（ADR-015 D1）。** ★ 原則としては維持する ——
  **将来の強介入を `stuck_likelihood` 単独で発火させてはならない**（高リスクの実験介入として扱う）。
- **動機が低いことを理由に強介入や義務感 UI を出さない**（動機不足 ≠ 停滞・設計書 §1.4）。
- Consent 軸（`ObserveOnly → none`）は**倫理・自律性ゲート**であって効果エビデンスではない（過大主張しない）。

### 現行閾値（参考）
⚠️★★★ **2026-09-01 訂正 —— 実在する閾値定数は 2 本だけである**
（実測: `src-tauri/src/analysis/intervention.rs:3-4`）:
`NUDGE_NEED_THRESHOLD=0.60` / `NUDGE_OPPORTUNITY_THRESHOLD=0.35`。
⚠️ **旧文が挙げていた `WALL_NEED=0.70` / `WALL_SLACK=0.50` / `WALL_OPP=0.45` は存在しない**
（ADR-015 D1 の「Wall 閾値 6 種」削除に含まれる）。
★ その他の実在定数: `NUDGE_COOLDOWN_MS=10 分` / `RECENT_DISMISS_MS=20 分` / `NUDGE_DAILY_CAP=6` /
`AWAY_IDLE_MS=180_000`（idle≥180s で介入全停止）。
`InterventionThresholds`（`new_with_thresholds`）で sweep 可能。
★ **加えて評価専用の veto** `correction_f4_floor` / `correction_f6_floor` が `InterventionThresholds` にある
（既定 `None` ＝ production 不変。`intervention.rs:99-107` / 適用は `:273-288` で `suppressed_by` へ push し `Defer` へ落とす）。
> ⚠️ **2026-09-01 訂正 —— 旧文の「Phase1 完了まで定数変更禁止」は前提が失効した。**
> ★ **2026-08-18 に Phase1 は収集打ち切りで終了し、凍結は解除された**（`docs/adr/README.md`）。
> ★ **定数は現在も未変更**だが、それは「変更禁止だから」ではなく「まだ触っていない」からである。

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
ただし `InterventionPolicyState` は day_index / nudge_count_today / last_*_at_ms / wall_accum_ms / current_action /
last_log_key 等 **十数個の可変状態**を持つため、pure `decide()` への切り出しは「容易」ではなく **state（cooldown/cap/履歴）と
純粋判定を分離する設計作業**を要する。主作業は **Consent 軸の新設**と **decision reason code のログ化**。

### Epic 3 acceptance（migration-risk-register / 設計書 Step 3）
- 同一入力に対する既存 action を **golden test で再現**（`none`/`defer` の観測可能性は既に enum で確保済み）。
- `none`/`defer` の理由コードを記録・dismiss reason を構造化・**`policy_version` をログに刻印**。

→ 境界整理と Consent 軸の判断は **ADR-004**。

---

## ⚠️ 見直し候補（未決）

> ★ 本節は**決定ではなく、未決の登録**である。★ 決めるときは ADR で決める（⚠️ 本節を根拠に実装しない）。
> `intervention-design` Skill の冒頭から参照される。

### R-1. ⚠️ Nudge の時期（と有無）を本人が統制する経路（2026-09-20 登録）

- **登録の一次**: `.steering/20260919-theory-ssot-promotion/decisions.md` **判断 4 #5**（研究者判断「見直し候補に載せる」）。起票は ADR-035 Consequences（「未決として起票する: Nudge の時期を本人が統制する経路」）。

| 項目 | 内容 |
|---|---|
| 何が問題か | ★ [P386] §2 の警告 —— 状態に合わせて働きかけること（逐語 *"only at the specific times of day they were thought to be most afflicted"*）は操作として非難されうる —— は、招待より先に**現行の Nudge**（Stuck 推定時に出す）に当たる（`docs/research-positioning.md` §3・S2 の追記）。★ 防御線として挙がっているのは透明性と本人の統制（[P380]・[P385]） |
| 既決との関係 | ★ **ADR-035（Proposed）は招待（Physical Anchor の PC 面）だけが対象**で、Nudge については何も決めていない（ADR-035「最初に固定する切り分け」・Consequences）。★ 近い既存の仕組みは 2 つあるが、どちらも本項の答えではない: ① ADR-004 の Consent 軸（`support_consent == ObserveOnly → none`）—— **有無**の側の候補だが**未実装**（Epic 3）／ ② セッションが宣言する `intervention_enabled`（`session_meta`・スタート画面の第 1 週 / 第 2 週）—— 研究の条件（`condition` / `labelPool`）と一体で選ぶもので、⚠️ **時期**を本人が選ぶ経路ではない（`src/App.tsx` の `PHASE_WEEKS`） |
| いつまでに決めるか | ★ **Nudge を被験者に出す研究を設計する前**（`docs/research-positioning.md` §6 の M3 = Phase 2 の Y 価値（AB/BA）・M4 = Phase 3 の X2 介入機会（MRT））。⚠️ 割付（AB/BA・MRT）と本人の統制は衝突しうる —— ★ 招待の側では ADR-035 D1「本人が止めた区間は研究の条件が有効でも出さない」（段 3 判断 4 #3 で例外なしと確認）を決め、解析での数え方を解析計画へ回した。★ Nudge で同じ形を採るかは本項で決める |
| いまは効いていない理由 | ★ 現在の G1 と O1 では **Nudge を出さない**: G1 は起動モード「第 1 週（blind 較正）」で介入を全部 gate する（`experiments/20260801-controlled-friction-task/protocol.md`・`INTERVENTION_ENABLED=false`）—— ⚠️ **手順と既定値（`src/App.tsx` の既定は第 1 週）で守っており、コードでは強制しない**（G1 モードでも週の選択は出る・バックエンドは G1 モードで介入を止めない）／ O1 は判断 O1-5（`src-tauri/src/lib.rs` が `INTERVENTION_ENABLED` を明示的に `false` にする —— ★ コードで強制）。⚠️ 通常モードのビルドでは第 2 週（Nudge が出る）を選べる。~~研究者本人のパイロット（`EH2`）や開発者の日常利用が「Nudge を被験者に出す研究」に入るかは未決（→ 研究者へ）~~ → ★ **2026-09-20 研究者判断: 入らない**（研究者本人・開発者は「被験者」ではない。`.steering/20260920-g1-o1-inventory/decisions.md` 判断 4）。★ したがって本項の締切は**本人・開発者の利用を止めない**。⚠️ ただし `EH2` の制限（**本人による計器・手順の確認であり、外部知覚の証拠にしない**）はそのまま効く —— ★ 本人で Nudge を出して得た所見を「効いた / 受け入れられた」の証拠にしない。⚠️ **G1 の第 1 週の守り方を緩めるものでもない**（上記のとおりコードでは強制していない） |
| ⚠️ 書いてはいけないこと | ⚠️ 「Nudge は dismiss できるので本人が統制している」—— ★ RP §3 が「opt-in と dismiss があるから自律性を脅かさない」を否決したのと同じ向き（dismiss は出た後の応答であって、出す時期の統制ではない） |

---

## 関連文書
- 上位: `docs/architecture/gse-v2-overview.md`
- 入力側（Layer 0-3）: `docs/architecture/domain-adapter-boundary.md`
- 判断: `docs/adr/ADR-004`（decision engine boundary）／`ADR-007`（receptivity 統合 vs 分解）
- 現行実態: `.steering/20260724-epic0-repo-reality-check/repo-inventory.md`
