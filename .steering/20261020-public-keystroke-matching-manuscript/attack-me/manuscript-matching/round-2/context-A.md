# context A（査読者と監査役の両方に渡す・stage: manuscript・round 2・変更箇所だけ）

対象物は commit 92c0cadb（branch docs/public-keystroke-matching-manuscript）の原稿。round 1 の後に直した原稿の、**今回変えた箇所だけ**を見る。

## 今回変えた箇所（ここだけを査読する）
公開のコンペ（Kaggle）の記録は本文を q で隠して公開された。そのデータの出どころについて、KLiCKe コーパスの著者から「コンペのデータは KLiCKe を公開する前に KLiCKe のコーパスから取った」と知らされた（personal communication）。本研究はコンペのデータを使っておらず、二つの公開を照合も突き合わせもしていない。この説明を原稿の次の箇所に入れた:
1. /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/introduction.tex 19〜20 行目（第 2 段落に 1 文）
2. /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex 104〜111 行目（§3.3 "Texts on the same prompts" の段落の後半）
3. /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/ethics.tex 24〜30 行目（"The competition data" の段落）と 40〜44 行目（"Stakeholders" の段落の最後の文）
4. /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/outline.md の主張と根拠の対応表の 1 行（"The competition data were drawn from the KLiCKe corpus …"）と倫理の計画の 1 項

周りの文脈（§3 全体・倫理の節全体・序論全体）は読んでよいが、指摘は変えた箇所と、その変更が周りの文と食い違うところに限る。round 1 で直した他の箇所は対象外。
結果（§7）はまだ無い。空欄 [...] は欠陥にしない。投稿版では personal communication の日付を外す（二重盲検のため。camera-ready で戻す）。

## 読んでよいファイルの一覧
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/main.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/introduction.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/data.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/discussion.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/ethics.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/open-science.tex
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/references.bib
- /Users/johnd/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/outline.md
- /Users/johnd/GSE-wt-matching-manuscript/experiments/20261012-public-keystroke-matching/preregistration.en.md （事前登録の正の版）

## 測った値（2026-10-24）
- ビルド: エラー 0・未定義の参照 0・未定義の引用 0・overfull 2（round 1 の後と同じ）。§3.3 は節番号 3.3（"Who holds the texts"）。

## 投稿規程の一次の抜粋（2026-10-24 に curl で取り直し、逐語を照合済み）
- authors-2027.php（https://petsymposium.org/authors-2027.php）:
  - "The first page must clearly state how the work is relevant to real-world privacy applications."
  - "This section should include a justification of the ethics of the work and information about whether the work was submitted to an external ethics panel such as an IRB or the Tor Research Safety Board. Research that is deemed to not have met adequate ethical standards may be rejected on those grounds."
