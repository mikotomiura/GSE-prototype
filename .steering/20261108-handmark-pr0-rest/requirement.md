# handmark-pr0-rest —— 手跡の PR 0 の残り（glossary・理論 §1.4・文献）を main へ

## 背景

手跡を main に入れる計画（ADR-051 D7・PR #399・2026-11-08 マージ）の PR 0 のうち、ADR-050・ADR-051 は main に入った。残りは、枝 `docs/tangibility-design` にしか無い glossary の「手跡」・理論の文書の §1.4・文献 [P485]〜[P554] と文献カード 5 枚である（ADR-048 Migration 2・ADR-051 Migration 1）。引き継ぎは `.steering/_handoff/next-session-gse-handmark-mac.md` の節 B（`docs/handmark-to-main-plan` 枝の版）。

## ゴール

main の文書だけで、手跡の語・理論上の要件・その根拠の文献がたどれる。要件は ADR-048 D2 と ADR-051 D3 に合っている。

## スコープ

### 含むもの
- `docs/glossary.md` に「手跡」の項（ADR-048 D2 を反映・ADR-050／ADR-051 を参照）
- `docs/theory/measurement-terminating-practice-portraiture.md` に §1.4 と関わる節（§5.2・§9・§10・§12 の注記）を、本文を D2 に合わせて書き直して持ち込む
- `docs/references.md` に [P485]〜[P554] の 70 本を同じ番号で、`docs/literature/` にカード 5 枚と `_index.md` の 5 行
- `docs/theory/README.md` の 1 行
- 枝 `docs/tangibility-design` の ADR-040 の冒頭に「main で ADR-050 に振り直した」注（枝へのコミット）

### 含まないもの
- コードの変更（PR 1 以降）
- ADR-048・ADR-050・ADR-051 の本文の書き換え
- 段 1 の事前登録の改訂
- 枝の `.steering/` の作業記録の持ち込み（参照は「枝にある」と注記する）

## 受け入れ条件

- [ ] §1.4 の二つの条件・測り方・反証の条件・§9 の表が、ADR-048 D2（許す行為の性質＝速さ・リズム・止まり、要件は許した情報を超えて系の判断を漏らさない）と ADR-051 D3（ポインタの量も許す）に食い違わない
- [ ] glossary の「手跡」が同じ要件を述べ、禁止用語に当たらない
- [ ] main の本文が引く [Pn] がすべて references.md にあり、P485〜P554 が枝と同じ書誌で、DOI が main の既存の行と重ならない（重なれば重複の節の規約に従う）
- [ ] 本文から枝にしか無いファイルを指すときは、そのことを書いている
- [ ] code-reviewer と /cross-review（Codex を加える）を通る

## 関連ドキュメント

- docs/adr/ADR-048-handmark-as-counterpart-of-abstention.md（D2・Migration 2）
- docs/adr/ADR-050-handmark-input-not-recorded.md・ADR-051-handmark-in-stage1-late-period.md（D3・Migration 1）

## 運用メモ
- /reimagine 適用: No
- 理由: 決まった ADR-048 D2・ADR-051 D3 を文書に反映する作業で、設計の分岐が無い（研究者の選択）
