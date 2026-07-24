# 要件: Epic 0 — Repository Reality Check (Post-Phase1 再設計の下地)

## 背景
`GSE_Post_Phase1_Improvement_Design_v0.1.md`（~/Downloads・docs/ 未昇格）の提案を実装に落とす前に、
**現行コードを真実源として設計書との差分を確定**する。改善設計書 §10 Epic 0 / §11 の最初のプロンプトに対応。

## ゴール
- コード変更を**一切行わず**、以下を成果物として確定する:
  1. `repo-inventory.md` — 現行ディレクトリ・主要モジュールの実在パスと役割
  2. `design-vs-code-gap.md` — 設計書が要求する v2 概念の実装済み/未実装/名前違い表
  3. `migration-risk-register.md` — Phase1 を壊す可能性のある変更点・移行リスク
  4. `adr-and-issue-roadmap.md` — ADR 候補一覧 + Epic/issue 単位の実装ロードマップ

## 受け入れ条件
- [ ] コード変更ゼロ（`src-tauri/` `src/` に差分なし）。成果物は `.steering/` docs のみ。
- [ ] 設計書の全 v2 概念（Need/Opportunity/receptivity/cooldown/daily_cap/recent_dismiss/Monk Mode/
      task_kind/none/defer/calibration mode/EventEnvelope/adapter/uncertainty）の実装状況を明記。
- [ ] 旧 Flow/Incubation/Stuck 三状態表示の残存箇所を特定。
- [ ] Phase1 argumentative lock・NDJSON schema・replay/golden・HMM_VERSION の位置を特定。
- [ ] 設計書 §12 未決事項 10 件のうち、コードで解決できるものを解決（特に Monk Mode の意味）。

## 非対象
- コード変更・リファクタリング（Epic 2 以降）。
- 改善設計書の docs/ SSOT 昇格（Phase1 完了 + 本 Epic 0 + 承認の後）。

## 調査方法
Read/Grep/Glob/Bash による read-only 走査（サブエージェント/workflow 不使用）。コミット 9a5e18a (origin/main) 時点。
