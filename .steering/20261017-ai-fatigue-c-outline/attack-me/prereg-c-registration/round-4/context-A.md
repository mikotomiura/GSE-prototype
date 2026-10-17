# context A（査読者と監査役に渡す）

## 対象物
- stage: prereg（OSF に GSRR の様式で登録する前の、方法論のレビューの登録の下書き）・round 4
- 登録の先: OSF Registries（GSRR の様式）。投稿先の雑誌は未定。
- ★ round 4 は差分に絞る: round 3 が読んだのは草稿 0.3。その指摘を直した 0.4 から、いまの 0.9 までの差分（下の diff）を重く見る。差分の外は round 3 までに読んであるので、差分が差分の外と食い違う所・差分が新しく作った穴だけを見る。

## 読んでよいファイルの一覧（これだけ）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-4/diff-0.4-to-0.9.md （差分・草稿 0.4〈コミット 5088718d〉→ 草稿 0.9〈コミット 40c7e017〉・word-diff）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md （対象物の全文・英語・草稿 0.9・8117 語・GSRR の 65 項目に 1 対 1。差分の文脈を確かめるために読む）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/codebook-c2b-en.md （C2b のコードブック・版 2・登録の添付。0.4 から変わっていない）
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/outline.md （原稿の外枠・版 2。0.7 から登録の添付 5 になった。差分が名指す範囲〈抄録の規則・範囲の規則・表〉だけ参照する）

## 規程の一次の抜粋（GSRR の様式の論文）
- 出典: van den Akker, O. R., et al. (2023). Increasing the transparency of systematic reviews: presenting a generalized registration form. *Systematic Reviews*, 12, 170. doi:10.1186/s13643-023-02281-7。本文は Europe PMC の全文 XML（PMC10514995）を round 1 で取得し、下の文が本文に逐語で在ることを確かめた（照合済み）。round 4 で同じ XML を取り直し（2026-10-17・SHA-256 は round 1 と同じ c8408c10…）、3 つの文が逐語で在ることを確かめた。
- 逐語 1: "If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason)."
- 逐語 2: "You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review."
- 逐語 3: "If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration"
- 規定なし: 分量の上限（取得した範囲の原文に該当の文が無い）。
- 報告の手引き（対象物が名指す）: Murad & Wang 2017・PRISMA 2020。本文は渡さない。

## 測った値
- 対象物: 8117 語（wc -w）。参考文献 10 本。差分のファイル 3491 語・差分の塊 42。
