# context A（査読者と監査役に渡す）

## 対象物
- stage: prereg（OSF に GSRR の様式で登録する前の、方法論のレビューの登録の下書き）・round 5
- 登録の先: OSF Registries（GSRR の様式）。投稿先の雑誌は未定。
- round 5 は差分に絞る。round 4 で読んだのは草稿 0.9 で、その指摘は 0.10 で直した。0.10 から 0.11 への書き換え（下の diff）を重く見る。変わったのは次の 4 点。
  1. 追加候補の選別を、第 1 著者と AI の選別者（Claude Opus）の独立の 2 者で行う。食い違いは第 1 著者が決める。
  2. コードは第 1 著者 1 人で、4 週以上あけて 2 回行う（2 人の独立のコードをやめた）。
  3. 較正は、主の集合から抽出せず、探索の集合の全研究で行う。
  4. 原稿の草稿ができた後に、著者 2 人で全文の段を選び直し、感度分析 5 にする。
- 差分の外は round 4 までに読んである。差分の外との食い違いと、差分が新しく作った穴だけを見る。

## 読んでよいファイルの一覧（これだけ）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-5/diff-0.10-to-0.11.md
  - 差分。草稿 0.10（コミット 7838b0ec）から 0.11（コミット 1139499c）まで。word-diff。
  - 登録版・外枠・原稿の草稿 main.tex・表の枠 tables.tex を含む。
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md
  - 対象物の全文。英語・草稿 0.11・10968 語・GSRR の 65 項目に 1 対 1。
  - 差分の文脈を確かめるために読む。
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-attachments/ai-screening/instructions.md
  - 登録の添付 6。AI の選別者への指示。英語・1195 語。
  - 登録の前に探索の 34 件に 2 回当てた。1 回目の後に Q4 の 1 文を足した版がこれ。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/outline.md
  - 原稿の外枠・登録の添付 5。
  - 差分が名指す範囲（範囲の規則・抄録の規則・方法と結果の節・主張と根拠の表・表の枠）だけ参照する。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/draft/main.tex
  - 原稿の草稿。差分が名指す範囲（抄録・方法・限界・宣言）だけ参照する。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
  - 表の枠。表 3・4・13 だけ参照する。

## 規程の一次の抜粋（GSRR の様式の論文）
- 出典: van den Akker, O. R., et al. (2023). Increasing the transparency of systematic reviews: presenting a generalized registration form. *Systematic Reviews*, 12, 170. doi:10.1186/s13643-023-02281-7。
- 照合: round 5 で Europe PMC の全文 XML（PMC10514995）を取り直した（2026-10-17・SHA-256 は round 1 と同じ c8408c10…）。下の 3 つの文が逐語で在ることを確かめた（照合済み）。
- 逐語 1: "If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason)."
- 逐語 2: "You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review."
- 逐語 3: "If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration"
- 規定なし: 分量の上限（取得した範囲の原文に該当の文が無い）。
- 報告の手引き（対象物が名指す）: Murad & Wang 2017・PRISMA 2020。本文は渡さない。

## 測った値（wc -w）

| 対象 | 語数 |
|---|---|
| 対象物（登録版） | 10968 語。参考文献 11 本 |
| 添付 6 | 1195 語 |
| 差分のファイル | 13174 語・差分の塊 40 |
