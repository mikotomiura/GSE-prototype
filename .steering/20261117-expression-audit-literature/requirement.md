# expression-audit-literature（S-EA）

## 背景

研究全体のメタな整理（`.steering/_handoff/next-session-gse-research-meta-after-run1.md` の議題 1b）で、
4 面（読める所・読めない所・漏れる所・定義しだいの所）を「表現の文法」にも写し、表現も同じ漏れの検査で監査する案が出た。
その新規性の候補（表現の先行は「伝わるか・役に立つか」を問うが、「表現の見た目から元の記録や系の推論がどこまで推せるか」を実測で縛り設計の制約にするものは手薄ではないか）は Claude の見立てで、文献で確かめていない。
入口は `.steering/_handoff/next-session-gse-expression-audit-literature.md`（2026-11-17）。

## ゴール

回 1 の後のメタな整理の前に、議題 1b の新規性の候補が立つかを根拠つきで判断できる材料を作る。案を採るかはこのラウンドでは決めない。結果の向きを先に決めない。

## スコープ

### 含むもの
- 下位の問い 1〜4（引き継ぎの案のまま・2026-11-17 研究者が承認）の文献のラウンド 1 回（/literature-review）
- カード・references.md への登録・_index.md の 1 行・議題 1b への 1 段落の書き足し

### 含まないもの
- 案を採るかの判断・道具の設計への反映・作品の制作
- 回 1（手跡の机上の確かめ）が来たら、こちらは止めて回 1 を先にする

## 受け入れ条件

- [ ] docs/literature/20261117-expression-audit-precedent.md（落合 6 項目・3 票の検証・否決リスト）
- [ ] references.md に append-only（名前空間は問い 1・4 が V、問い 2・3 が P）・check_citations.py が「違反なし」
- [ ] _index.md に 1 行・議題 1b に先行の確かめの結果を 1 段落
- [ ] /cross-review（Codex を含む・送るのは設計の抜粋と書誌だけ）
- [ ] push と PR は研究者に確かめてから

## 関連ドキュメント

- docs/literature/20261115-three-checks-precedent.md（S-3C）
- docs/literature/20260921-data-portrait-and-lived-informatics.md
- 枝 docs/tangibility-design の docs/literature/20261018-handmark-nature-world.md（S-NW）

## 運用メモ
- /reimagine 適用: No
- 理由: 文献のラウンドで実装の設計判断を伴わない
