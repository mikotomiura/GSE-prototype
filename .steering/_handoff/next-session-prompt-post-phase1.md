GSE の Post-Phase1 再設計を実装フェーズへ進める。**実装タスクなので必ず `/start-task` を先に実行**し
`.steering/` に記録すること。いきなりコードを書かず、下記を読んで現状を突き合わせてから着手する。

## 0. 前提の確認（先にやる）
- `git fetch` して origin/main に PR #69（docs 再整備）・#70（Epic 0 実態調査）がマージ済みか確認する。
  未マージなら先にレビュー/マージするか、その旨を私に確認する。
- **Phase1 が完了しているか確認する**。未完了なら実装は Phase1 の凍結対象に触れない範囲（＝コード変更なしの
  Epic 1）に限定する。凍結対象＝NDJSON schema(schema_dto.rs/schema/current.json)・HMM_VERSION(engine.rs)・
  介入閾値(intervention.rs 定数)・probe_scheduler・App.tsx の argumentative lock・preregistration-v0.3.md。

## 1. まず読む（この順で）
1. `.steering/20260724-epic0-repo-reality-check/` の 4 点（repo-inventory / design-vs-code-gap /
   migration-risk-register / adr-and-issue-roadmap）。**現行コードの実態と実装計画の真実源**。
2. `~/Downloads/GSE_Post_Phase1_Improvement_Design_v0.1.md`（改善設計書・docs 未昇格の提案）。
3. `docs/research-positioning.md` §1/§8/§9（理論接地＝**機会保存**。学習効果は将来トラック。§0 の層構造）。
4. `docs/wbs-verification-halfyear.md`（26週 WBS + §改訂予定：Phase 1.5 挿入・Gate D/S/H 追加）。
5. 該当 Skill：`implementation-workflow`（共通骨格）/ `architecture-rules`（レイヤー分離・analysis/ に OS API 禁止）/
   `rust-standards` / `typescript-standards` / `git-workflow` / `data-privacy`（本文非保存）。

## 2. Epic 0 で確定した重要事実（前提として持つ）
- 設計書の中核（Need/Opportunity 分離・none/defer 第一級・cooldown/daily_cap/recent_dismiss）は**既に実装済み**。
  新規実装でなく整理が主。
- **task_kind は HMM β に未配線**（β は engine.rs で ime_open 切替、task_kind は engine に渡っていない）。
  Phase2 マルチタスク化の第一分岐点＝**ADR-006 を先に決める**。
- 完全未実装は Session Context 層（WorkIntent/SupportConsent/EventEnvelope/adapter/uncertainty＝0 ファイル）。
- Monk Mode = 介入拒否（Wall 抑制）。旧 Flow/Incubation/Stuck 三状態表示は Dashboard.tsx に残存（v2 で降格要）。

## 3. エビデンスの温度（過大主張しない・重要）
deep-research 3ラウンドで検証済みの判定を守る：
- **実証で支持**：`none`/`defer` 第一級化 [V43]、Motivation Generator を標準実装しない（実行意図 d=.36→.15 [P21]・
  ナッジ補正後 d≈0 [V40]）、Gate D は低継続率を桁の prior に [V41][V42]。
- **未検証（効果を主張しない・設計/思想として扱う）**：Session Context（[V43] は自己申告が受容性を予測しない逆風）、
  Accountability Extension（設計書 §4）、Agentic Coding の過信 proxy（設計書 §3.3・Adapter B）。
  → これらは「効くはず」で実装せず、covariate/倫理ゲート/feasibility の枠に留めるか、deep-research 第4ラウンド
  （RQ-2/RQ-3 専用）でエビデンスを取ってから判断する。
- 理論接地は**機会保存**（反射的オフロードを減らし自力解決の機会を保存＝行動指標で測定）。「摩擦が能力を育てる」
  学習効果は主張しない（[P12]Kapur は「守るべき困難の存在根拠」に限定）。

## 4. 着手（推奨順・adr-and-issue-roadmap.md に対応）
Phase1 完了が前提。**Epic 1（コード変更なし）から**：
1. 改善設計書を `docs/` へ SSOT 昇格（`docs/architecture/gse-v2-overview.md` 等・設計書 §7.1）。
2. **ADR-006（task_kind→β 配線 or IME 代理を正とするか）を最初に決める**。Context/Decision/Alternatives/
   Consequences/Migration を書く。他の ADR-001〜007 も起票。
3. その後 Epic 2（Writing Adapter 抽出＝engine/features を動作非変更で domain 配下へ・replay --snapshot parity が
   acceptance）→ Epic 3（intervention.rs に Consent 軸追加）。
4. Epic 4（Agentic Coding）は第4ラウンドのエビデンス確認後に feasibility から。

## 5. 進め方
- 実装は「調査→設計→（reimagine で代替案）→実装→テスト→レビュー」。難所は Plan Mode + Opus。
- 動作非変更リファクタ（Epic 2）は `cargo run --bin gse-replay -- ... --snapshot` の byte-equal 一致を必ず確認。
- 完了時は `/finish-task` + `/cross-review`（Codex 独立レビュー）を回す。
- 迷ったら推測で実装せず私に確認する（曖昧な指示への推測実装は禁止）。

まず上記 1 を読み、`/start-task` で最初のタスク（Epic 1 = ADR 起票 + SSOT 昇格、または Phase1 未完なら
その旨の確認）を切って、着手計画を私に提示してから進めること。
