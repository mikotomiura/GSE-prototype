---
name: citation-ssot
description: >
  外部の理論・手法・文献を参照する文章 (research-positioning.md / functional-design.md /
  architecture.md / 実験 notes / 論文ドラフト) を書く・編集する時に必須参照。本文の該当箇所に
  inline [n] を付け、docs/references.md (中央書誌 SSOT) に append-only で登録する。採番は末尾の
  次番号、[n] は恒久 ID、削除は tombstone、番号の再利用禁止、重複防止キーは DOI/arXiv/正規化 URL、
  書誌未確定は provisional 状態。「設計理由を書く」「手法を引用する」「先行研究に言及する」
  「参考文献をまとめる」「References を作る」時に起動する。引用規約の SSOT は docs/references.md。
allowed-tools: Read, Edit, Grep
---

# Citation SSOT Discipline

## このスキルの目的
設計書・論文の主張に出典を機械的に紐づけ、参考文献を `docs/references.md` 一箇所に集約する。
「最後に References を手で並べる」のではなく、書きながら [n] を付け SSOT を append する。
本 skill は規約を再定義せず、`docs/references.md` の採番ルールを作業時に発火させる。

## 名前空間（GSE 固有・重要）
GSE の references.md は **2 つの局所書誌を名前空間付きで統合**している:
`[Pn]` = 提案の理論基盤書誌 / `[Vn]` = ユーザー検証 v0.4 の方法論書誌。
新規引用はどちらの名前空間かを選び `[Pn]`/`[Vn]` で付ける。両書誌に既出の文献は references.md の「重複」列で相互リンク済み。
append-only / 恒久 ID / renumber 禁止 / tombstone は**名前空間ごと**に守る。

## 主要なルール（SSOT: docs/references.md）
### ルール 1: 主張のたびに inline [Pn]/[Vn]
理論・手法・先行研究に依拠する記述には、その場で該当名前空間の [Pn]/[Vn] を付ける。
### ルール 2: references.md は append-only
新規は該当名前空間の末尾の次番号。既存番号を renumber しない（inline 番号を安定させる）。
### ルール 3: [n] は恒久 ID
表示順ではない。削除は行を残し tombstone（撤回）とし、番号を再利用しない。
### ルール 4: 重複防止
DOI / arXiv ID / 正規化 URL を key にして二重登録を防ぐ。
### ルール 5: 書誌未確定は provisional
DOI/版/URL が未確認なら状態を `provisional` で登録し、確認後 `active` に上げる（捏造した URL を書かない）。
### ルール 6: 整合
本文の全 [n] が references.md に実在し、references.md の各 active 行に「使用箇所」がある。

## 良い例 / 悪い例
- ✅ 「提案は不便益 [1] を行動センシングへ拡張する」+ references.md に [1] が append 済み
- ❌ 本文に出典なしで主張し、最後にまとめて手で参考文献を貼る（SSOT 二重化 → drift）
- ❌ 既存 [2] を消して番号を詰める（inline [n] が全部ずれる）
- ❌ 未確認の DOI/URL をでっち上げる（provisional で登録し確認に回す）

## チェックリスト
- [ ] 外部根拠の各記述に [n] が付いているか
- [ ] [n] は末尾追加（renumber していない）か
- [ ] key（DOI/arXiv/URL）で重複していないか
- [ ] 本文の [n] が references.md に実在するか
- [ ] 書誌未確定は provisional にしたか（捏造していないか）

## 補足資料
- `examples.md` — 良い引用 / 悪い引用の具体例集

## 関連する他の Skill
- literature-card — 文献カード作成時に出典をここへ登録
- reproducibility-discipline — 実験 notes の借用手法 [n] 登録
