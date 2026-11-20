# handmark-coexistence-design —— 手跡の具体的な設計案と、手跡の全体の整理のスライド

## 背景
2026-11-20、S-CX（`docs/literature/20261120-handmark-coexistence-concept.md`・枝 docs/handmark-coexistence-survey）で、共存感覚の一般の形は既にある（Lupton の digital data companion species [P594]）が、作業中にそばで動く表示の経験として測ったもの・判断を運ばない表示で測ったもの・自他を動かす変数を比べたものは見つからなかった。研究者はこの形で手跡の具体的な設計案を一度立てると決めた（2026-11-20）。ADR-051 D6 は、手跡ありの日の同期・共存の項目の文を「文献のラウンドの後に決める」としており、S-CX がそのラウンドに当たる。

## ゴール
- 手跡の設計案（由来・他者性のつまみ・守りの 3 層、測り方、進める順、決めていないこと）を `.steering/` に 1 本の文書として立てる。研究の決定はしない（ADR は書かない）。
- 手跡の全体の整理（何であるか・決まっていること・今の実装・文献から分かったこと・設計案・これから）を、既存のスライド（`docs/slides/project-overview/`・tpl・Klee One・deckkit）と同じ形の 1 本にし、pptx と PDF を `G:\マイドライブ\Doe_Systems\Reserch_production\GSE\slides` に置く。テンプレートは研究者が `c:\deck-temp\deck_temp.pptx` を指定した。

## スコープ外
- ADR・実装・日の問いの項目の確定（案を出すまで）・未踏の提案書の文
- 既存の 4 本のスライドの変更

## 受け入れ条件
- [x] `.steering/20261120-handmark-coexistence-design/design-proposal.md`
- [x] `docs/slides/project-overview/build_handmark.py` で組んだ `GSE_handmark_design.pptx` と PDF
- [x] 描画を画像で見て、重なり・はみ出しを直した
- [x] Drive の slides に pptx と PDF を置いた
- [x] /cross-review（設計案とスライドの文の範囲）
- [ ] push（S-CX の枝の上にあるので PR は S-EA・S-CX の後）

## 運用メモ
- /reimagine 適用: No
- 理由: 設計案は研究者の決定の材料で、採否を決めない。案の比べ（つまみ 3 つ）は文書の中で並べる
