# タスクリスト
- [x] 本体（`o1LinksRows_` / `o1ReadLinksManual_` / `o1BuildLinksTab_` / `refreshO1LinksTab`・`buildO1MgmtSheet` から呼ぶ）
- [x] テスト §18（16 ケース・全 245）・偽シートの拡張（clear / setValues / getDisplayValues）・下限 240
- [x] 変異 9 件（全 79 件が赤）（最初は「運営シートの ID の検査を外す」がすり抜けた → 理由の文面とロスターと同じ ID のケースで捕まえた）
- [x] O1 の配布前ゲート 24/24
- [x] 運営ワークフローの docx に反映（版 2）
- [x] レビュー（code-reviewer ＋ security-checker）→ 指摘を反映（decisions.md 判断 2）。⚠️ Codex は 2026-10-07 の予算超過で不可
- [x] 各リンクに「いつ・誰が使うか」の列（判断 4）・テスト全 249・変異全 80 件が赤
- [ ] PR・CI・マージ
- [ ] 研究者: Apps Script に貼り直し → `refreshO1LinksTab()` を実行 → 「提出物の受取フォルダ」を手で貼る
