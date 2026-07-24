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
- RQ-2 (agentic coding 過信検出) / RQ-3 (accountability) の実証 → deep-research 第4ラウンド。
- 理論接地の学習効果トラック (consolidation 実装) → research-positioning §8・Phase3 以降。
- Phase 1.5 挿入に伴う WBS 期間再配分 → 研究者判断 (wbs-verification-halfyear.md §改訂予定)。
