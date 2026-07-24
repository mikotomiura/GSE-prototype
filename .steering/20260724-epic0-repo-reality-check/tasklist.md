# tasklist: Epic 0 — Repository Reality Check

- [x] 現行ディレクトリ・主要モジュールの実在パスを確定 → repo-inventory.md
- [x] v2 概念の実装状況表 (Need/Opportunity/receptivity/cooldown/daily_cap/recent_dismiss/
      Monk Mode/task_kind/none/defer/EventEnvelope/adapter/uncertainty) → design-vs-code-gap.md
- [x] 旧 Flow/Incubation/Stuck 三状態表示の残存箇所を特定 (App.tsx / Dashboard.tsx)
- [x] Phase1 argumentative lock・NDJSON schema・replay/golden・HMM_VERSION の位置を特定
- [x] 設計書 §12 未決事項のコード解決 (Monk Mode=介入拒否 / task_kind=β 未配線 / receptivity=分解形)
- [x] Phase1 を壊すリスクと移行順序 → migration-risk-register.md
- [x] ADR 候補 + Epic/issue ロードマップ → adr-and-issue-roadmap.md
- [x] コード変更ゼロを確認 (src-tauri/ src/ に差分なし)

## 主要な発見 (要点)
1. **設計書の「中核」は既に実装済み**: Need/Opportunity 分離・none/defer 第一級・cooldown/daily_cap/
   recent_dismiss はコードに実在。設計書 §3.7 の要求の多くは新規実装でなく整理。
2. **task_kind は HMM β に未配線** (β は ime_open 切替)。Phase2 マルチタスク化の第一の分岐点 (ADR-006)。
3. **完全に未実装なのは Session Context 層**: WorkIntent/SupportConsent/EventEnvelope/adapter/
   uncertainty/evidence_quality (0 ファイル)。ここが Epic 2-4 の主要な新規実装。
4. **Monk Mode = 介入拒否** (Wall 抑制)、強介入許可ではない (§12-1 解決)。
5. 旧三状態表示は Dashboard.tsx に残存するが calibration blind で gate 済み。v2 で降格が要る。

## 次アクション (Phase1 完了後)
Epic 1 (ADR + 改善設計書の docs/ SSOT 昇格・コード変更なし) から。特に ADR-006 (task_kind→β) を先に決める。
Epic 4 (Agentic Coding) は deep-research 第4ラウンドのエビデンス確認後。
