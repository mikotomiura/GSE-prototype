# 設計

## アプローチ

1. 文献: 枝の `docs/references.md` から P485〜P554 の行をそのまま写し、main の P484 の後に足す。足す前に、main の既存の行（P と V）との DOI・arXiv・URL の重なりを機械で照合する。カード 5 枚は枝からそのまま写す（カードが参照する `.steering/` が枝にしか無いことは、各カードの頭に 1 行の注記）。
2. 理論 §1.4: 枝の差分を基に、要件を ADR-048 D2・ADR-051 D3 の形に書き直す。
   - 条件 2「状態として読めない」→「系の判断を、許した行為の性質以上には漏らさない」。許す性質は速さ・リズム・止まり（打鍵）とポインタの動きの量。
   - 測り方: 予測器 A（許した性質だけ）と B（A＋見た目）を比べる（ADR-051 D3 の値はそちらを参照し、ここで繰り返さない）。
   - 反証の条件 3（全体の速さの経路）は D2 で許した漏れになったので外し、反証の条件を「自己認識が成り立つ写像のどれでも、B が A を許す幅を超えて上回る」に直す。
   - §9 の表と §10 も合わせる。
3. glossary: 枝の項を同じ形に書き直す。

## 変更対象

- docs/references.md・docs/literature/（5 枚＋_index）・docs/theory/measurement-terminating-practice-portraiture.md・docs/theory/README.md・docs/glossary.md
- 枝 `docs/tangibility-design` の docs/adr/ADR-040-handmark-input-not-recorded.md（冒頭の注）

## テスト戦略

- 本文の [Pn] がすべて references.md にあることを機械で確かめる。
- P485〜P554 が枝と byte 単位で同じであることを diff で確かめる。
- glossary の禁止用語の一覧に当たらないことを grep で確かめる。
