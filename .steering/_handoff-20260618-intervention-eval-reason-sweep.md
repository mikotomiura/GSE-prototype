# ハンドオフ: Phase 0 — intervention_eval を reason 別 + threshold sweep に拡張

> このファイルは「次セッションで最初に打ち込むプロンプト」の実体。
> 新セッションの 1 通目に以下だけ打てばよい:
>
> **「`.steering/_handoff-20260618-intervention-eval-reason-sweep.md` を読み、その指示に従ってタスクを開始して。CLAUDE.md のセッション開始行動規範を順守すること。」**

---

## 0. このタスクの位置づけ（前セッションの結論）

`.idea/need-opportunity-improvement-plan.md`（Need/Opportunity 推論改善提案）を厳密ジャッジした結果:

- 提案は**妥当**。現状コード記述もほぼ正確（文書側の事実誤り 1 件・統計脆弱性 2 件は前セッションで修正済み）。
- ただし**証拠ベースが薄い**（P000 単一被験者・計 65.4 分・nudge 34 回・TP 12 件）。
  個人内 holdout 校正（Phase 1+）は現データでは過学習する。
- よって **現データで着手可能なのは Phase 0（production 挙動を変えない評価基盤の増強）のみ**。
  本タスクは Phase 0 を実装する。Phase 1 以降（Need 校正・Opportunity 個人化・micro-randomization）には**進まない**。

参照必読:
- `.idea/need-opportunity-improvement-plan.md` §2.3 / §6 Phase 0 / §9
- `.steering/20260606-gse-v2-intervention-eval/results.md`（HIR=0.647 等の出所と限界）
- `.steering/20260606-gse-v2-intervention-eval/decisions.md`（D2 forward-fill / D5 回復窓 W）

## 1. ゴール（受け入れ条件）

**production の判定ロジック・閾値・schema を一切変えずに**、`intervention_eval.rs` を拡張し、
「`p_stuck` を振った時」と「reason 別」の HIR/Precision/recall/DC/Burden が出る計測器を作る。

完了基準（文書 §Phase0）:
- [ ] 現行 policy を再現できる（既存 replay snapshot と byte-equal 互換）。
- [ ] Nudge FP（有害 nudge）を **opportunity reason 別**に分解して上位原因を説明できる。
- [ ] `p_stuck` 閾値の変更候補を **3 案以内**に絞れる（sweep 表で根拠提示）。

## 2. 具体スコープ（5 項目）

現状 `src-tauri/src/analysis/intervention_eval.rs`（718 行）は (a) `decide()` の `reason`/`suppressed_by` を
捨てている（`:280` で `.decision.action` だけ拾う）、(b) 閾値が `intervention.rs` の `const` でハードコード、
の 2 つの穴がある。これを埋める。

1. **reason/suppressed_by を保持**: `decisions: Vec<(u64, InterventionAction)>`（`:268`）を
   `reason` / `suppressed_by` / `need_score` / `opportunity_score` も保持する構造体 Vec に拡張。
2. **opportunity reason を機械可読化（低リスク版）**: `OpportunityReason` enum
   （ShortPause / MediumPause / LongPause / PostBurstPause / CorrectionContext / ActiveTyping / None）を追加。
   `InterventionDecision` に持たせる場合は **必ず `#[serde(skip)]`** を付け、NDJSON schema に出さない
   （→ schema parity も data-privacy も影響ゼロ）。**schema へのフィールド追加（文書 Phase 2）はやらない**。
3. **reason 別混同行列 / HIR 分解（主目的）**: `BinaryConfusion`（`:84`）を reason 別に層別化
   （`HashMap<OpportunityReason, BinaryConfusion>` 等）。post_burst_pause / short_pause /
   correction_context それぞれの HIR を別個に出力する。
4. **threshold sweep**: 閾値を `const` から注入可能にする（`InterventionThresholds` config 構造体、
   **既定値は現行 const と同値**）。production は既定値で呼ぶ＝挙動不変。eval だけ sweep 値で呼ぶ。
   `p_stuck` を **0.50–0.90 を 0.05 刻み**で振り、各点の HIR/recall/precision/burden/DC を表で出す。
5. **CLI モードと出力**: `gse-replay` に sweep 出力モードを追加（既存 `--snapshot`/`--metrics`/
   `--intervention`/`--segments` の**相互排他ルールを順守**）。出力は reason 別・閾値別の表（pretty + JSON）。

## 3. 厳守すべき不変条件・制約

- ⚠️ **defer-run 回復起点の不変条件**（`intervention_eval.rs:382-385`）: DC 計算は
  `NUDGE_NEED_THRESHOLD >= 0.50` を前提とする。**sweep を 0.50 未満に下げると DC が壊れる**。
  sweep 範囲を 0.50–0.90 に限定する（下げる必要が出たら起点を run 終端の次 feat へ要変更し、根拠を decisions.md に記録）。
- **analysis/ 純粋性**: OS API を呼ばない。副作用なし純粋関数を維持（`intervention_eval.rs` の既存方針）。
- **schema drift 禁止**: `schema_dto.rs` / `schema/current.json` を変えない。enum は `#[serde(skip)]` で in-memory のみ。
  万一 schema に触れたら `/finish-task` の schema parity guard が停止させる。
- **Rust 規約**: `tracing` のみ（`println!`/`eprintln!` 禁止）、`anyhow::Result`、`any` 型なし、`winapi` 禁止。
- **replay 互換**: 既存ゴールデン snapshot が byte-equal で通ること（production 不変の証明）。
- **privacy**: 新規ログ/出力フィールドが入力内容・文書内容・URL・window title を含まないこと。
- **HMM_VERSION**: HMM 挙動を変えないので bump 不要（変えたら違反）。

## 4. スコープ外（やらないこと）

- production の閾値（0.60/0.70/0.35/0.45 等）・加点式・suppressor の**変更**。
- `need_score = p_stuck` の置換、`need_confidence` の production 投入。
- schema へのフィールド追加、`opportunity_components` の NDJSON 出力。
- Phase 1（Need 校正）/ Phase 3（低侵襲 context）/ Phase 4（micro-randomization）の実装。

## 5. セッション開始時の手順（CLAUDE.md 行動規範）

1. **`/start-task`** を起動し `20260618-intervention-eval-reason-sweep` を作成
   （requirement.md / design.md / tasklist.md に本ファイルの §1–§4 を反映）。
2. **docs 先読み**: `docs/architecture.md`（analysis 層境界）/ `docs/development-guidelines.md` §3（Replay-as-Truth）。
3. **必須 Skill 参照**: `rust-standards` / `architecture-rules`（新規 enum/構造体・モジュール境界）/
   `intervention-design`（介入 policy の意味）/ `hmm-analysis`（feat/obs の意味）/ `ml-workflow`（評価指標の根拠）。
   schema に触れる判断が出たら `data-privacy`。
4. **サブエージェント委譲**: 影響範囲調査=`impact-analyzer`（`InterventionDecision`/`calculate_opportunity` の参照元）、
   関連実装探索=`file-finder`。実装後レビューは `code-reviewer` + `security-checker` を**並列**起動。
5. 実装は **Sonnet**、設計判断が要れば Opus で Plan。

## 6. 検証（実装後・`/finish-task` 前）

- `cargo test --workspace`（新規 unit: reason 分類の正しさ・sweep の単調性/境界）
- `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`
  （既存 snapshot byte-equal = production 不変の証明）
- `cargo run --bin emit_schema` を `schema/current.json` と byte-equal 比較（drift なし確認）
- 新 sweep モードを P000 の 13 セッションに対し実行し、reason 別 HIR と閾値 sweep 表を `results` に出力
- privacy review: 新フィールド/出力が content を含まないこと

## 7. 完了処理

- `/finish-task`: steering 最終化 → テスト → **Step 3 で `/cross-review` 必須**
  （`code-reviewer` + `security-checker` + Codex の独立 diff レビュー）。
  ※ 本機は jq 未導入で Codex 系統がブロックされる場合あり → その場合は Claude 単独へ縮退し、
    **skip 理由を完了報告に明記**（既知の制約。memory: codex_review_needs_jq）。
- コミット: `feat(engine): Phase0 reason別/threshold sweep 評価基盤 (production 不変)` 系。
  `Refs: .steering/20260618-intervention-eval-reason-sweep/`。

## 8. アウトプット（このタスクが次に渡すもの）

- reason 別 HIR 分解（HIR=0.647 の犯人 reason 特定）
- `p_stuck` 0.50–0.90 sweep の Pareto 表
- 閾値変更候補 3 案以内 + 根拠
- → これらが揃って初めて Phase 1（Need 校正の着手是非）を holdout で判断できる。
