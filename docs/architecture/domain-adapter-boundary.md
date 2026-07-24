# Domain Adapter 境界 — Layer 0-3 (SSOT)

> **ステータス**: Proposed（方向性）。`gse-v2-overview.md` の Layer 0-3 を詳述する。実装は Epic 2（Writing 抽出）/
> Epic 3.5（Session Context）/ Epic 4（Agentic）で、いずれも **Phase1 完了後**。本書は trait/schema の**案**であり
> 確定は各実装時の ADR に委ねる。昇格元: 設計書 §3.2–3.5 / §8.1 / §8.2。

## Layer 0: Session Context（設計書 §3.2）

### 目的
動機不足・義務的作業・開始困難・作業中停滞を**区別するための最小文脈**を取得する。**動機を生成しない**。

### フィールド案
```rust
enum WorkIntent { SelfDirected, Obligatory, LowIntent, Unspecified }
enum SupportConsent { ObserveOnly, LightSupport, StrongSupportOptIn }

struct SessionContext {
    task_kind: TaskKind,          // 現行 enum（Argumentative/Correspondence/Creative/VibeCoding）を流用
    work_intent: WorkIntent,      // 新規
    support_consent: SupportConsent, // 新規
    accountability_opt_in: bool,  // 新規（core 外・ADR-003）
    calibration_mode: bool,       // 現行 Condition::BlindCalibration に対応
    intervention_enabled: bool,   // 現行 gate に対応
}
```

### ⚠️ エビデンス状態（最重要・過大主張の禁止）
`WorkIntent`/`SupportConsent` は **3 ラウンドのサーヴェイで一度も直接検証されていない**。[V43] は
**受動観測の行動指標が受容性を予測し、自己申告指標は予測しなかった**ことを示す逆風。よって:

- receptivity の**主軸は行動指標**（cooldown/idle/recent_dismiss・既実装）に置き、Session Context は**従**。
- 採用の正当化は **効果ではなく次の 2 つのみ**:
  1. **交絡切り分け（covariate）**: `LowIntent` を記録し「need 高 = 詰まり」でなく「low intent」を事後区別。
  2. **倫理・自律性ゲート**: `ObserveOnly → 介入 none`。
- 「効くはず」で receptivity の重み付けに組み込まない。効果ある層として拡張したいなら**専用エビデンス確認が先**。

詳細: `docs/research-positioning.md §8`・`gse-v2-overview.md §5`・**ADR-002**。

### UI 原則（§3.2・厳守）
一打/二打で終える・目標文を書かせない・if-then 計画を標準機能にしない・選択結果を常時表示しない・
`LowIntent` を失敗扱いしない・LightSupport を選べば軽支援可・動機を推定値として断定しない。
**非目標**: 作業意欲の生成／義務感の強化／連続日数・ポイントによる強制／低意欲を認知的異常として分類。

> プローブ予算: Session Context は較正プローブと別枠で増えるため、設計書 §12-9（プローブ過多）に抵触しないよう
> **一打二打で終える**制約を先に設計する（migration-risk-register）。

---

## Layer 1: Domain Event Adapter（設計書 §3.3）

`input/` が直接 `analysis/` へ繋がる現状に、`DomainAdapter` trait を挟んで Writing/Coding/Creative を分離する。

### Adapter A: Writing（現行 Phase1 実装の位置づけ直し）
- **維持する入力**: keystroke timing / correction / pause / burst / silence / IME composition・confirmation /
  paste count・size / session boundary。
- **段階的に追加する候補**: selection size・churn / caret movement / scroll / undo・redo / editor focus・return / boundary keys。
- **位置づけ**: Phase1 の HMM・F1/F3/F4/F5/F6 は Writing Adapter の baseline。HMM は補助 head。出力は
  Flow/Incubation/Stuck の断定でなく v2 proxy。Phase1 の確証結果は他ドメインへ直接転移しない（**ADR-001**）。

### Adapter B: Agentic Coding（次の探索・observe-only）
- **理由**: 実利用者の主要作業に近く、accept/reject/test/revert 等の観測可能な節目がある。
- **観測候補**: agent request / response start・end / diff opened / review duration / accept・partial・reject /
  manual edit after accept / test・build / success・failure / revert / repeated prompt pattern / tool wait / focus 遷移。
- **内容非保存**: プロンプト・コード・diff・エラーメッセージ本文、リポジトリ名・ファイル名を保存しない（既定）。
  量・時間・種別・成功失敗・遷移のみ。
- **domain-local proxy 候補**: `blind_acceptance_likelihood` / `review_depth_proxy` / `repeated_prompt_loop` /
  `manual_recovery` / `agent_wait` / `agency_balance` / `test_feedback_utilization`。
- ⚠️ **エビデンス状態**: 過信検出は第4ラウンド（RQ-2）で**証拠ゼロ**。`agency_balance` は**善悪スコアにしない**
  （AI 操作量と人間操作量の構成を記述する proxy）。着手前に「過信を行動イベントのみで検出できるか」の
  エビデンス確認が必須。それまで feasibility（取得可能イベント・privacy threat model）に留める（**Epic 4**）。

### Adapter C: Creative Editing（feasibility のみ）
動画編集・デザイン・3D を一括実装しない。まず一アプリに限定した feasibility study。長い無打鍵が正常・
試行錯誤とデッドループの境界が作品文脈依存・OS レベルイベントだけでは意味不足・プラグイン方式が必要になりうる。
**Phase2 では実装でなく取得可能イベントとプライバシー境界の調査を主目的**にする（**Epic 6**・優先度最低）。

### DomainAdapter trait 案（§8.1）
```rust
trait DomainAdapter {
    fn adapter_id(&self) -> &'static str;
    fn task_kind(&self) -> TaskKind;
    fn ingest(&mut self, event: PlatformEvent) -> Vec<EventEnvelope>;
    fn feature_snapshot(&self) -> DomainFeatureSnapshot;
    fn privacy_audit(&self) -> PrivacyAuditResult;
}
```
→ trait 抽出の詳細・Writing 抽出の acceptance（replay parity）は **ADR-002** と Epic 2。

---

## Layer 2: Privacy Boundary + 共通 Event Envelope（設計書 §3.4）

全ドメインで共通化するのは**イベントの外枠のみ**。

```rust
struct EventEnvelope {
    schema_version: u16,
    session_id: String,
    relative_ts_ms: u64,
    task_kind: TaskKind,
    adapter_id: String,
    adapter_version: String,
    event_family: EventFamily,
    magnitude_bucket: Option<MagnitudeBucket>,
    result: Option<EventResult>,
    source_role: SourceRole,
    privacy_class: PrivacyClass,
}

enum EventFamily {
    Generate, Revise, Inspect, Navigate, Compare, Execute,
    Accept, Reject, Revert, Wait, Pause, Boundary,
}
```

### 禁止事項（記録してはならない）
raw text / clipboard text / prompt text / code text / file contents / window title / full path / URL /
project・repository name / participant identifying metadata。→ `data-privacy` Skill・`docs/glossary.md` 禁止用語。

### 設計判断
`EventFamily` は**分析上の同一性を保証しない**。あくまでデータ配管と監査の共通分類である
（Writing の Backspace と動画編集の Undo を同じ重みにしない・§3.1 制約）。
schema versioning（additive・schemars 既存基盤）は **ADR-005**。

---

## Layer 3-4: Domain-local Feature と v2 Work-State Proxy（設計書 §3.5）

各 Adapter/Head は次の形式で Decision Engine へ渡す。

```rust
struct WorkStateEstimate {
    friction_score: f32,
    stuck_likelihood: f32,
    engagement_score: f32,
    incubation_like_pause: f32,
    flow_like_continuation: f32,
    uncertainty: f32,        // 必須
    evidence_quality: f32,   // 必須
    model_head_id: String,
    model_version: String,
}

trait DomainInferenceHead {
    fn head_id(&self) -> &'static str;
    fn infer(&mut self, features: &DomainFeatureSnapshot, context: &SessionContext) -> WorkStateEstimate;
}
```

### 原則
- `uncertainty` を必須にする。evidence quality が低い場合は介入を弱める（`none`/`defer`）。
- domain head が**未較正の場合、強介入を禁止**する。
- Phase1 の Writing HMM 出力を直接共通スコアとして扱わない。
- **task_kind ごとに baseline と閾値を分ける**／個人 baseline と task baseline を分離する。
  → ★現行は β を `ime_open` で切替え **task_kind 非配線**。この配線を正とするかは **ADR-006**（最優先）。

---

## 関連文書
- 上位: `docs/architecture/gse-v2-overview.md`
- 介入側（Layer 5-7）: `docs/architecture/intervention-decision-engine.md`
- 判断: `docs/adr/ADR-002`（domain-local inference）／`ADR-005`（event envelope）／`ADR-006`（task_kind→β）
- 現行実態: `.steering/20260724-epic0-repo-reality-check/design-vs-code-gap.md`
