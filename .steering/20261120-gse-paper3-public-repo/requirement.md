# 要件 —— 論文 3（per-person-learning）の公開 repo を組む

## 背景
論文 3 の Code availability に `https://github.com/mikotomiura/per-person-keystroke-models` と Zenodo の予約 DOI
10.5281/zenodo.24395569 を入れた（判断 46）。公開は投稿の直前（研究者の選択）。棚卸しは
`.steering/20261120-gse-paper3-springer-presubmit/inventory/`。引き継ぎは `.steering/_handoff/next-session-gse-paper3-public-repo.md`。

## ゴール
`~/per-person-keystroke-models` に、論文の S8 の解析と確かめのコード・条件と記録・集計と合成の値・kit・原稿の tex を
組み、漏れの検査と self-test を通した状態で、公開（GitHub の public と Zenodo の publish）の承認を研究者に求める。

## 受け入れ条件
- 写す一覧は assemble.sh が単一の記録（何度でも作り直せる）。
- 実在の書き手ごとの値を含まない（休止の割合の min/max 6 個は外す）。GSE の docs・.steering は入れない。投稿先と状態を書かない。
- tools/verify.sh が 0（漏れの検査＋陽性対照・pinned の鎖・kit の selftest と適合検査）。
- README.md / README.ja.md・LICENSE 3 本・CITATION.cff・.zenodo.json・conditions の英語の要約。
- レビュー（security-checker・/cross-review）の指摘に対応。
- 公開は研究者の承認の後。
