# context A（査読者と監査役に渡す）

## 対象物
- stage: prereg（OSF に GSRR の様式で登録する前の、方法論のレビューの登録の下書き）・round 6
- 登録の先: OSF Registries（GSRR の様式）。投稿先の雑誌は未定。
- round 6 は差分に絞る。round 5 で読んだ 0.10 → 0.11 の書き換えに、査読が指摘を出した。研究者が直す一覧を承認し、それを直した差分（下の diff）を重く見る。
- 主な直し:
  1. 添付 6 から AI のウェブの閲覧を外し、探索の 34 件に当て直した（3 回目）。
  2. 中心は最終で A か B。
  3. 両者の保留と符号の食い違いの扱い。
  4. E5 の連結を選別で決める。
  5. 束と記録の時刻。
  6. 両者が同じ規則で判定する。
  7. 較正の改訂の根拠と n < 5。
  8. 感度分析 5 の手順と、行えないとき（行わず逸脱として報告）。
  9. 限界の追加。
- 差分の外は round 5 までに読んである。直しが指摘を消したか、直しが別の所と食い違わないかだけを見る。

## 読んでよいファイルの一覧（これだけ）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-6/diff-round5-fixes.md
  - 差分。round 5 の直し（コミット 1139499c → 5fd670fd）。word-diff。
  - 登録版・添付 6・外枠・原稿の草稿 main.tex・表の枠 tables.tex・図 1 figure1.tex を含む。
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md
  - 対象物の全文。英語・草稿 0.11（round 5 の直しの後）・12101 語・GSRR の 65 項目に 1 対 1。
  - 差分の文脈を確かめるために読む。
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-attachments/ai-screening/instructions.md
  - 登録の添付 6。AI の選別者への指示。英語・1199 語。
  - 登録の前に探索の 34 件に 3 回当てた。これは 3 回目に使った版（ウェブの閲覧を外した版）。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/outline.md
  - 原稿の外枠・登録の添付 5。
  - 差分が名指す範囲（範囲の規則・抄録の規則・方法と結果の節・主張と根拠の表・表の枠）だけ参照する。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/draft/main.tex
  - 原稿の草稿。差分が名指す範囲（抄録・方法・限界・宣言）だけ参照する。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/draft/tables.tex
  - 表の枠。表 3・4・13 だけ参照する。
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/draft/figure1.tex
  - 図 1（流れ図）。

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
| 対象物（登録版） | 12101 語。参考文献 11 本 |
| 添付 6 | 1199 語 |
| 差分のファイル | 8595 語・差分の塊 28 |
