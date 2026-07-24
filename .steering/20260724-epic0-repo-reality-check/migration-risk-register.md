# migration-risk-register — Phase1 を壊すリスクと移行順序

> Epic 0 成果物 (3/4)。改善設計書 §9 移行戦略に対応。

## 最優先の不変条件 (Step 0: Phase1 を壊さない)
Phase1 完了までは以下を**変更禁止**。破ると収集済み/収集中データが無効化する。

| 凍結対象 | 実体 | 破ると何が起きるか |
|---|---|---|
| NDJSON schema | `schema_dto.rs` → `emit_schema` → `schema/current.json` | CI drift 検知が fail・gse-dataset 連携破綻 |
| HMM 挙動 | `engine.rs` `HMM_VERSION` / `loop_step.rs` | ゴールデン (replay --snapshot) 不一致・C-index 再現不能 |
| 介入閾値 | `intervention.rs` の NEED/OPPORTUNITY 定数 | Phase2/3 の判断性能評価の基準がずれる |
| プローブ機構 | `probe_scheduler.rs` (λ/cap/gap) | ラベル収量が変わり GATE2 の解釈が変わる |
| argumentative lock | `App.tsx` TASK_KINDS | 非論述混入で C-index が task_kind 交絡 |
| PreReg 契約 | `preregistration-v0.3.md` (PreReg-1..8/GATE1-3) | forking paths・確証性喪失 |

## 移行リスク (Phase1 完了後の Epic 2 以降)

| リスク | 影響度 | 対象 | 緩和 |
|---|---|---|---|
| engine を legacy_hmm/ へ隔離すると replay 出力が変わる | **高** | engine.rs / loop_step.rs | 動作非変更リファクタに限定・replay --snapshot parity を acceptance に (設計書 Step 2) |
| task_kind enum 変更で schema drift | 高 | schema_dto.rs TaskKindDto | enum は維持 (4 変種)・追加のみ。emit_schema diff を必ず確認 |
| 三状態表示の削除が calibration UI gating に波及 | 中 | Dashboard.tsx:189-190 / App.tsx:65-98 | blind gate ロジックと表示ロジックを分離してから削除。calibration parity をテスト |
| WorkStateEstimate に uncertainty 追加で FeatSnapshot schema 変更 | 中 | schema_dto.rs / loop_step.rs | Phase1 後・HMM_VERSION bump とセットで。additive フィールドに留める |
| Session Context (WorkIntent/SupportConsent) 追加でプローブ増 | 中 | 新規 UI + logger | §12-9 抵触。プローブ予算を先に設計 (改善設計書 §3.2 は「一打二打で終える」) |
| dismiss 理由に bad_timing/not_helpful 追加で DismissReason schema 変更 | 低 | logger.rs DismissReason | Phase1 後・additive。EarlyUnlock/WantToStruggle は既存流用 |
| Decision Engine の pure function 化 | 低 | intervention.rs | 既に `new_with_thresholds` で分離済み・golden test 追加で安全 |

## 移行順序 (設計書 §9 を現行コードに接地)
1. **Step 0 (現在〜Phase1 完了)**: 上記凍結を維持。Epic 0 (本調査) のみ。
2. **Step 1 (Phase1 完了直後)**: ADR + docs SSOT 昇格 (コード変更なし)。改善設計書を docs/ へ。
3. **Step 2**: Writing Adapter 抽出 = engine/features を **動作非変更**で domain 配下へ論理隔離。
   Acceptance: replay parity / calibration parity / HMM_VERSION 不変 / NDJSON 互換 / UI 不変。
4. **Step 3**: Decision Engine 境界整理 (Need/Opportunity/Receptivity/Consent 分離)。
   現状 intervention.rs は Need/Opportunity 分離済み・pure 化は容易。Consent は新規。
5. **Step 4**: Session Context (WorkIntent/SupportConsent) 最小 UI + ログ。
6. **Step 5**: Agentic Coding observe-only Adapter (介入発火なし)。
7. **Step 6**: Phase 1.5 / Phase 2A で実ユーザー探索。

## Phase1 の verdict による分岐 (設計書 §5)
- **Go**: Writing Adapter の X1 証拠として保存 → Step 2 以降へ。
- **Inconclusive / DataInsufficient**: Writing 探索継続。全体再設計とは分離。
- **Kill**: Writing Head/HMM の破綻。**GSE 全体の Kill とはしない**。Adapter 抽象化はむしろ有効
  (Writing Head を差し替え可能にする)。§12-10 (維持コスト) を要判断。
