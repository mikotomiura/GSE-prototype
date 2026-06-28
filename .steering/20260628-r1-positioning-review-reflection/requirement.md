# R1 研究ポジショニング — レビュー指摘の反映（Physical Anchor 除く）

## 背景

2026-06-28、研究トラック土台 Phase R1（`/setup-research-framing` 相当）を成熟プロジェクトに後付け生成した
（`docs/research-positioning.md` / `references.md` / `experiment-tracking.md` / `literature/_index.md` /
`experiments/` / 研究 3 skill）。その後、研究としての妥当性・整合性を **二重レビュー**:

- **Codex (gpt-5.5)** — `run-codex-consult` 相当（secrets-filter 通過）で研究妥当性の独立第二意見。
- **Claude サブエージェント** — ground-truth（functional-design / glossary / v0.4 / WBS）との突合。

両者が **独立に一致**した指摘（X1 の土台・H-X2 の弱さ・H-Y の交絡・新規性の置き場所）＋スコープ/企画性評価を得た。
範囲が広く WBS にも波及するため、本タスクとして別途実施する。**Physical Anchor は実装予定**のため、
縮退を勧める指摘 C は**除外**する。

レビュー全文の根拠は本会話ログ（および下記 design.md）に集約。R1 成果物は**全て未コミット**。

## ゴール

レビュー指摘 **A・B・D・E・F・G・H・I・J・K・L**（C を除く）を R1 docs と glossary に反映し、
研究ポジショニングが (1) 主張と検証の整合、(2) 非 overclaim、(3) 中央書誌との整合 を満たす状態にする。

## スコープ

### 含むもの
- `docs/research-positioning.md` / `docs/references.md` / `docs/experiment-tracking.md` / `docs/glossary.md` の編集
- 編集後の再レビュー（code-reviewer + `/cross-review`）と引用整合の再検証

### 含まないもの
- **指摘 C（Physical Anchor のスコープ縮退）** — PA は実装予定のため §9 等の PA 記述は今回いじらない
- **Phase 1 のセッション収集コード・NDJSON schema の変更** — 指摘 A は後段分析/文言のみで収集不変（design.md 参照）
- 実装系（`src-tauri/` / `src/`）の機能変更

## 受け入れ条件

- [ ] 指摘 A・B・D・E・F・G・H・I・J・K・L を反映（C は意図的にスキップと明記）
- [ ] 全 inline `[Pn]`/`[Vn]` が `references.md` に実在（grep 再検証）
- [ ] overclaim 語（「F/I/S を分類」「認知状態を読む」等）が残っていない（grep）
- [ ] `MhD` が `glossary.md` に登録済み（指摘 F）
- [ ] 指摘 A-1 の「p_stuck 正当化方針」をユーザーに確認済み（研究判断）
- [ ] code-reviewer + `/cross-review`（Codex）で再レビュー、HIGH 指摘に対応
- [ ] `/finish-task` で steering 最終化・コミット

## 関連ドキュメント / ground truth

- `docs/functional-design.md`（機能3/4/7・§2.x 較正・Need=p_stuck・Opportunity=timing の真値）
- `docs/glossary.md`（用語 SSOT・MhD 未登録）
- `Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md`（X1/X2/Y・GATE・AB-BA・MRT）
- `docs/wbs_検証用docs/GSE_マイルストーン_WBS_半年版_v2.docx`（M0–M5・26週。textutil で txt 変換して読む）
- `docs/[提案プロジェクト補足資料]GSE_proposal_参考文献.md`（P 名前空間の出所）
- `docs/preregistration-v0.3.md`（PreReg-1..8・GATE 閾値の根拠候補）

## 付録: 新セッション着手プロンプト（自己完結・冒頭に貼る用）

> 本 steering を読めば足りるが、文脈ゼロ起動用に圧縮版を残す。

```text
GSE 研究トラック docs（Phase R1 成果物・未コミット）にレビュー指摘を反映する。docs/glossary のみの編集で
Phase 1 のセッション収集コード・schema は変更しない。Physical Anchor の指摘 C は除外。
詳細・指摘 A–L・ground truth・確定済み前提・完了基準は
.steering/20260628-r1-positioning-review-reflection/{requirement,design,decisions,tasklist}.md を読むこと。
着手前に指摘 A-1（p_stuck の正当化方針: 象限 high-Q1×low-Q2 を stuck 相当とみなす vs 補助 self-marker）を
ユーザーに1問だけ確認してから編集を始める。secrets-filter/wrapper は bash 経由（scripts/*.sh が +x 欠落）。
```
