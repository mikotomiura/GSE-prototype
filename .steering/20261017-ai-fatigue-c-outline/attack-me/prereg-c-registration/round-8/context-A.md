# context A（査読者と監査役に渡す）

## 対象物
- stage: prereg（OSF に GSRR の様式で登録する前の、方法論のレビューの登録の下書き）・round 8
- 登録の先: OSF Registries（GSRR の様式）。投稿先の雑誌は未定。
- 対象: TRACE リポジトリのコミット 05e31ac の登録版（草稿 0.20・2026-10-20）と、その添付・外枠 11 版・草稿。
- round 8 は差分に絞る。round 7 で読んだ 0.19 の全文に、査読が指摘を出した。研究者が直す一覧を承認し、設計の 6 点を決めた。それを直した差分（下の diff）を重く見る。直しの後にかけた 2 系統のコードと文書のレビューの直しも、同じ差分に入っている。
- 差分の外は round 7 までに読んである。直しが指摘を消したか、直しが差分の外と食い違わないか、直しが新しい穴を作っていないかを見る。

## 読んでよいファイルの一覧（これだけ）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-8/diff-round7-fixes.md
  - 差分。round 7 の直し（TRACE 059664b → 05e31ac）。word-diff・差分の塊 74。登録版・コードブック・添付 6 の call.md と README・外枠・草稿 main.tex・表 tables.tex・図 figure1.tex。
- /Users/johnd/TRACE/registration-en.md
  - 対象物の全文。英語・草稿 0.20・20,066 語。差分の文脈を確かめるために読む。
- /Users/johnd/TRACE/codebook-c2b-en.md
- /Users/johnd/TRACE/registration-attachments/ai-screening/instructions.md（0.19 から変えていない）
- /Users/johnd/TRACE/registration-attachments/ai-screening/call.md
- /Users/johnd/TRACE/registration-attachments/ai-screening/README.md
- /Users/johnd/TRACE/registration-attachments/coding-form/columns.md（符号化の様式の列の説明・道具が作る）
- /Users/johnd/TRACE/manuscript/outline.md（外枠 11 版・8,335 語。差分が名指す範囲を中心に）
- /Users/johnd/TRACE/manuscript/draft/main.tex・tables.tex・figure1.tex（差分が名指す範囲を中心に）

一覧に無いもの（読まない）: TRACE の脚本（`scripts/`）・AI の出力（`check-34.csv`）・検索の書き出しと記録の一覧・候補の一覧・反例集。登録版がこれらを名指していても、中身は確かめられないものとして扱う。

## 規程の一次の抜粋（GSRR の様式の論文）
- 出典: van den Akker, O. R., et al. (2023). *Systematic Reviews*, 12, 170. doi:10.1186/s13643-023-02281-7。
- 照合: round 7（2026-10-20）で Europe PMC の全文 XML（PMC10514995）を取り直した（SHA-256 は round 1 と同じ c8408c10…）。round 8 は同じ日なので取り直していない。下の 3 つの文が逐語で在る（照合済み）。
- 逐語 1: "If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason)."
- 逐語 2: "You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review."
- 逐語 3: "If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration"
- 規定なし: 分量の上限（取得した範囲の原文に該当の文が無い）。

## 測った値（wc -w）

| 対象 | 語数 |
|---|---|
| 対象物（登録版 0.20） | 20,066 語。参考文献 14 本。[at registration] の欄 9 か所 |
| 1 つ前の版（0.19） | 18,082 語 |
| 差分のファイル | 15,314 語・差分の塊 74 |
