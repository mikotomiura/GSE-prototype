# adr-and-issue-roadmap — ADR 候補と実装ロードマップ

> Epic 0 成果物 (4/4)。改善設計書 §7.1 / §10 に対応。**すべて Phase1 完了 + 承認が前提**。

## ADR 候補一覧 (各 ADR は Context/Decision/Alternatives/Consequences/Migration を記載)

| ADR | 主題 | Epic 0 で判明した前提 | 難度 |
|---|---|---|---|
| ADR-001 | HMM を Writing baseline へ降格 | engine.rs は既に OS 非依存・β dual baseline を持つ。三状態表示 (Dashboard.tsx:189) の降格が主作業 | 中 |
| ADR-002 | domain-local inference / Adapter 境界 | adapter/ 層は完全に不在。input/→analysis/ 直結を DomainAdapter trait で挟む新設 | 高 |
| ADR-003 | Accountability を core 外に分離 | 該当コードなし。新規 extension。エビデンス未確定 (第4ラウンド待ち) | 中 |
| ADR-004 | Decision Engine 境界 (pure function 化) | intervention.rs は Need/Opportunity 分離済・`new_with_thresholds` で threshold 注入可。Consent 軸のみ新規 | 低 |
| ADR-005 | Event Envelope schema versioning | schema_dto.rs は既に schemars ベース。EventEnvelope/EventFamily は新規追加 | 中 |
| ADR-006 | task_kind → β baseline 配線 or 分離の決定 | ★β は現状 ime_open 切替で task_kind 非配線。配線するか「IME 状態が代理」を正とするか要判断 | 中 |
| ADR-007 | receptivity 統合スコア化 or 分解維持 | cooldown/daily_cap/recent_dismiss は実在。統合スコア化するか現状維持か | 低 |

## Epic 単位のロードマップ (設計書 §10 を現行コードに接地)

### Epic 0: Repository Reality Check ← 本タスクで完了
成果物 4 点 (本 .steering/)。コード変更なし。

### Epic 1: Architecture ADR (Phase1 完了直後・コード変更なし)
- 改善設計書を `docs/` へ SSOT 昇格（`docs/architecture/gse-v2-overview.md` 等）。
- ADR-001〜007 を作成。特に **ADR-006 (task_kind→β)** は Phase2 のマルチタスク化の前提。
- 依存: Phase1 完了 + 研究者承認。

### Epic 2: Writing Adapter Extraction (動作非変更)
- `engine.rs` / `features.rs` を Writing domain 配下へ論理隔離 (`analysis/legacy_hmm/` or `adapters/writing/`)。
- Acceptance: replay --snapshot parity / calibration parity / HMM_VERSION 不変 / NDJSON 互換 / UI 不変。
- 依存: Epic 1。**リスク高** (migration-risk-register 参照)。

### Epic 3: Intervention Decision Refactor
- intervention.rs から Need/Opportunity/Receptivity/Consent を個別テスト可能に。
- 現状 Need/Opportunity は分離済 → 主作業は **Consent 軸の新設** と decision reason code のログ化。
- `none`/`defer` の観測可能性は既に enum で確保済み。
- Acceptance: golden test で既存 action 再現 / policy_version をログ刻印。

### Epic 4: Agentic Coding Discovery (observe-only)
- ⚠️ **第4ラウンド (RQ-2) で証拠ゼロ**。着手前に「過信を行動イベントのみで検出できるか」の
  エビデンス確認が必須。それまでは feasibility 調査 (取得可能イベント・privacy threat model) に留める。
- §12-5 (window title を読まず focus_role 取得可能か) は input/ の調査が必要。

### Epic 3.5: Session Context 層 (WorkIntent / SupportConsent) ※効果は未検証・控えめに扱う
> ⚠️ **エビデンス状態の正直な明記 (Epic 0 の判断)**: Session Context は **3 ラウンドのサーヴェイで
> 一度も直接検証されておらず、「効くと判明した」証拠は存在しない**。改善設計書 §9 Step 4 の位置づけ
> (独立 Epic でなく一作業) が実は妥当。当初これを「解析計画の一部」として独立 Epic へ格上げしかけたが、
> 下記の逆風を踏まえ **効果を主張しない控えめな層**に戻す。
- **未実装 (0 ファイル)**: `WorkIntent`(SelfDirected/Obligatory/LowIntent/Unspecified)・
  `SupportConsent`(ObserveOnly/LightSupport/StrongSupportOptIn)・`accountability_opt_in`。
- **★逆風の証拠 (最重要)**: [V43] (JMIR 2026・3-0) は「**受動観測の行動指標が受容性を予測し、自己申告指標は
  予測しなかった (P>.10)**」を示した。WorkIntent/SupportConsent はまさに**自己申告**であり、
  **receptivity の主軸に据えるのは証拠が逆を向く**。receptivity は行動指標 (cooldown/idle/recent_dismiss 等・
  既実装) を主とし、Session Context は従に留める。
- **効果ではない 2 つの正当化 (これのみで採用可否を判断する)**:
  1. **交絡の切り分け (解析 covariate)**: `WorkIntent=LowIntent` を記録し「need 高は詰まりでなく低意欲」を
     事後区別する (改善設計書 §1.4 の動機不足 vs 停滞の混同)。**効果の主張でなく H-Y 解釈の共変量**。
  2. **倫理・自律性ゲート**: `SupportConsent==ObserveOnly → 介入 none`。研究倫理・opt-in の原則で正当化。
     **効果エビデンスではない**。
- **やらないこと**: Session Context を「GSE をよく効かせる装置」と位置づけない (改善設計書 §1.4 も
  「動機づけ層でなく文脈の明示層」と明記)。UI 制約 (§3.2: 一打二打・目標文を書かせない・常時表示しない・
  LowIntent を失敗扱いしない) を厳守。
- **依存/順序**: Epic 3 (Consent 軸を介入 gate に) と同時か直後・**Phase1 完了後**・schema は additive・
  プローブ増を §12-9 に照らし最小化。もし「効果がある層」として拡張したいなら **専用のエビデンス確認が先**
  (現状は未検証)。
- **per-task adapter との関係**: `task_kind` は文脈フィールドだが `WorkIntent`/`SupportConsent` とは別軸。
  task_kind→β/adapter (ADR-006/Epic 2) と intent/consent→gate は**直交する軸**として扱う。

### Epic 5: Evaluation Pipeline v2
- Gate D/S/X1/X2/Y/H の schema 化。現状 X1 (calibration_eval) / X2 (intervention_eval) / Y (metrics) は実在。
- **新規は Gate D (Demand) と Gate H (Harm)**。Gate D の閾値は in-the-wild ベンチ ([V41][V42]) を桁の prior に。
- cross-domain contamination guard (label_pool の思想を task_kind 間へ拡張)。

### Epic 6: Creative Editing Feasibility
- 一アプリ限定の feasibility のみ。実装せず Go/Defer/Kill 判定。優先度最低。

## Phase1 完了後の「着手の第一手」推奨
1. **Phase1 verdict を確定** (Go/Inconclusive/Kill/DataInsufficient)。
2. **Epic 1 (ADR + SSOT 昇格)** — コード変更なしで安全に始められる。改善設計書を docs/ へ。
3. **ADR-006 (task_kind→β)** を先に決める — Phase2 のマルチタスク化・Adapter 抽象化の分岐点。
4. その後 Epic 2 (Writing Adapter 抽出・動作非変更) → Epic 3 (Consent 軸追加)。
5. Epic 4 (Agentic Coding) は **第4ラウンドのエビデンス確認後**に feasibility から。

## 未解決 (エビデンス/判断待ち・本 Epic 0 の射程外)
- **Session Context (WorkIntent/SupportConsent) の効果は未検証**。採用の正当化は「交絡の切り分け (covariate)」と
  「倫理・自律性ゲート」のみで、効果主張はしない。[V43] は自己申告が受容性を予測しないことを示す逆風あり。
  効果ある層として拡張するなら専用エビデンス確認が先 (Epic 3.5)。
- RQ-2 (agentic coding 過信検出) / RQ-3 (accountability) の実証 → deep-research 第4ラウンド。
- 理論接地の学習効果トラック (consolidation 実装) → research-positioning §8・Phase3 以降。
- Phase 1.5 挿入に伴う WBS 期間再配分 → 研究者判断 (wbs-verification-halfyear.md §改訂予定)。
