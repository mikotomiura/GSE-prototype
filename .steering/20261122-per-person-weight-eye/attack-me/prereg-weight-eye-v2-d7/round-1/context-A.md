# context-A（査読者と監査役の両方に渡す）

## 対象物

- stage: prereg（事前登録の追記の下書き・凍結の前）。対象物は commit 5c9ee5e5。
- 対象物: `/Users/johnd/GSE-prototype-weight-eye/experiments/20261126-per-person-weight-eye-v2/conditions.md` の末尾の節「追記 1: D7 実データの読みの基準」（52 行目から末尾・3,543 字）。その前の節（v2 の v1 との差分）と v1 の conditions.md は、すでに凍結した条件で、追記の前提として読む（追記の外の穴は、追記の読みを変えるときだけ挙げる）。
- 位置づけ: 合成の較正（V1・D5・D6）はすでに回し終え、結果は notes にある。実データ（CoAuthor・CS1）はまだ読んでいない。この追記は、実データを読む前に、実データの読み方を 1 通りに固定するためのもの。v2 は探索の版で、確認の主張には使わない、と条件に書いてある。
- 投稿先: 未定（論文 3 の補足に入れる探索の分析）。投稿規程は無いので、評価表 e は「投稿先未定」として点を付けない。

## 読んでよいファイルの一覧（これだけ・すべて補足の印。prereg なので本文の上限は無い）

- /Users/johnd/GSE-prototype-weight-eye/experiments/20261126-per-person-weight-eye-v2/conditions.md   （対象物を含む）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261126-per-person-weight-eye-v2/notes.md   （v2 の V1・D5・D6 の結果）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261126-per-person-weight-eye-v2/SEED
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261126-per-person-weight-eye-v2/scripts/eye.py   （目・揃え・入れ替えの実装）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261126-per-person-weight-eye-v2/scripts/run_eye.py   （セルと計画）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261122-per-person-weight-eye/conditions.md   （v1 の条件・D1〜D9・追記 1〜3）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261122-per-person-weight-eye/notes.md   （v1 の結果）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261104-timeseries-tau-extend/scripts/data.py   （split の定義）
- /Users/johnd/GSE-prototype-weight-eye/experiments/20261104-timeseries-tau-extend/scripts/ml.py   （pool_units の定義）
- /Users/johnd/GSE-prototype-weight-eye/papers/per-person-learning/manuscript/supplement.tex   （論文 3 の補足・公開済みのプレプリントの一部。S2 がデータの単位、S10 が論文 3 の検出率）

## 測った値

- 追記の文字数 3,543（wc -m）。v2 の conditions.md 全体 6,353 字。実データの読み込みのコードはまだ無い（凍結の後に別のタスクで書く）。
