# intervention_eval を reason 別 + threshold sweep に拡張 (Phase 0)

## 背景

`.idea/need-opportunity-improvement-plan.md`（Need/Opportunity 推論改善提案）を厳密ジャッジした結果:

- 提案は妥当。現状コード記述もほぼ正確（文書側の事実誤り 1 件・統計脆弱性 2 件は前セッションで修正済み）。
- ただし証拠ベースが薄い（P000 単一被験者・計 65.4 分・nudge 34 回・TP 12 件）。
  個人内 holdout 校正（Phase 1+）は現データでは過学習する。
- よって現データで着手可能なのは **Phase 0（production 挙動を変えない評価基盤の増強）のみ**。

現状 `intervention_eval.rs`（718 行）には穴が 2 つある:
(a) `decide()` の `reason`/`suppressed_by` を捨てている（`:280` で `.decision.action` だけ拾う）、
(b) 閾値が `intervention.rs` の `const` でハードコードされ sweep できない。

既存評価 (`.steering/20260606-gse-v2-intervention-eval/results.md`): HIR=0.647 / Wall=0 /
PROTECT suppression=0.994 / DC=0.933 / STALL recall=0.073。HIR=0.647 の犯人 reason が不明。

## ゴール

**production の判定ロジック・閾値・schema を一切変えずに**、`intervention_eval.rs` を拡張し、
「`p_stuck` を振った時」と「reason 別」の HIR/Precision/recall/DC/Burden が出る計測器を作る。

## スコープ

### 含むもの
1. reason/suppressed_by/need_score/opportunity_score を保持する構造体 Vec へ拡張。
2. `OpportunityReason` enum を機械可読化（`InterventionDecision` に持たせる場合は `#[serde(skip)]` 必須）。
3. reason 別混同行列 / HIR 分解（`HashMap<OpportunityReason, BinaryConfusion>` 等）。
4. threshold sweep: 閾値を注入可能な `InterventionThresholds` config に（既定値 = 現行 const）。
   `p_stuck` を 0.50–0.90 を 0.05 刻みで振り、各点の HIR/recall/precision/burden/DC を表で出す。
5. `gse-replay` に sweep 出力モードを追加（既存モードとの相互排他ルール順守）。reason 別・閾値別の表（pretty + JSON）。

### 含まないもの
- production の閾値（0.60/0.70/0.35/0.45 等）・加点式・suppressor の変更。
- `need_score = p_stuck` の置換、`need_confidence` の production 投入。
- schema へのフィールド追加、`opportunity_components` の NDJSON 出力。
- Phase 1（Need 校正）/ Phase 3（低侵襲 context）/ Phase 4（micro-randomization）の実装。

## 受け入れ条件

- [ ] 現行 policy を再現できる（既存 replay snapshot と byte-equal 互換）。
- [ ] Nudge FP（有害 nudge）を opportunity reason 別に分解して上位原因を説明できる。
- [ ] `p_stuck` 閾値の変更候補を 3 案以内に絞れる（sweep 表で根拠提示）。
- [ ] `cargo test --workspace` 通過（reason 分類・sweep の単調性/境界の新規 unit 含む）。
- [ ] `emit_schema` 出力が `schema/current.json` と byte-equal（drift なし）。
- [ ] privacy: 新フィールド/出力が content（入力内容・文書内容・URL・window title）を含まない。

## 厳守すべき不変条件・制約

- ⚠️ **defer-run 回復起点の不変条件**（`intervention_eval.rs:382-385`）: DC 計算は
  `NUDGE_NEED_THRESHOLD >= 0.50` を前提。sweep を 0.50 未満に下げると DC が壊れる。
  sweep 範囲を **0.50–0.90 に限定**する。
- analysis/ 純粋性: OS API を呼ばない。副作用なし純粋関数を維持。
- schema drift 禁止: `schema_dto.rs` / `schema/current.json` を変えない。enum は `#[serde(skip)]` で in-memory のみ。
- Rust 規約: `tracing` のみ、`anyhow::Result`、`any` 型なし、`winapi` 禁止。
- replay 互換: 既存ゴールデン snapshot が byte-equal で通ること。
- HMM_VERSION: HMM 挙動を変えないので bump 不要。

## 関連ドキュメント

- `.idea/need-opportunity-improvement-plan.md` §2.3 / §6 Phase 0 / §9
- `.steering/20260606-gse-v2-intervention-eval/results.md`（HIR=0.647 等の出所と限界）
- `.steering/20260606-gse-v2-intervention-eval/decisions.md`（D2 forward-fill / D5 回復窓 W）
- `docs/architecture.md`（analysis 層境界）/ `docs/development-guidelines.md` §3（Replay-as-Truth）

## 運用メモ
- /reimagine 適用: No
- 理由: ハンドオフ (`_handoff-20260618-intervention-eval-reason-sweep.md`) が設計を詳細に規定済み。
  複数の非自明な設計案を比較する局面ではなく、評価基盤の増設（production 不変）であり方針は確定している。
