# 引き継ぎ —— 論文 3 の公開 repo（GitHub と Zenodo）を組み、投稿の直前に公開する

> 作成: 2026-11-20。このメモを一次資料にしない。決まったことは `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 46、作業記録は `.steering/20261120-gse-paper3-springer-presubmit/`（棚卸しは `inventory/inventory.csv` と `inventory/report.md`）。

## 0. 入口の文
```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-public-repo.md を読んで、論文 3 の公開 repo を組んでください。
```

## 1. 決まっていること（研究者の選択・2026-11-20）
- 公開は「投稿の直前」。repo の名前は `mikotomiura/per-person-keystroke-models`（本文の Code availability に入れ済み）。
- Zenodo の下書き 24395569 で DOI 10.5281/zenodo.24395569 を予約済み（未公開・API で作った・token は ~/zenodo/zenodo_token.txt で表示しない）。
- 中身: kit（hashes を含む）・当てはめのコード・後の確かめのコード・集計の値と合成の値・tex。`.steering/` と GSE の docs は入れない。投稿先と状態は書かない（補足 supplement.tex の `\journalline` は公開の写しでは空にする）。
- 手本は public の `mikotomiura/stall-runup-equivalence`（LICENSE-MIT・LICENSE-APACHE・LICENSE-docs〔CC BY 4.0〕・.zenodo.json・CITATION.cff・README.md と README.ja.md・docs/media の図と gif）。

## 2. 棚卸しで分かった手当て（inventory/report.md）
- 実在の書き手ごとの値を含む結果は 0 件。ただし `20261111-objective-and-pause/results/summary.json` の休止の割合の min/max（1 人分の値）は外す。
- コード 129 件: 日本語のコメント・メッセージを英訳。GSE の名・判断の番号・`.steering`・ADR・round・作業機の名を除く。`DATA_DIR` の既定値（`$HOME/gse-public-data`）を外し必須の引数か環境変数に。
- 13 の外への依存: `experiments/20261031-coauthor-pre-request-signal/scripts`（build_obs.py・build_cs1.py が import）、`20261102-public-data-landscape`（CoAuthor の取り置き・analyze_cs1）。同梱するか kit に吸収する。
- S8 の確かめ 2（構造の補い・S12）は origin/main の `experiments/20261107-structure-deficit-test` にあり、この worktree に無い。取り込む。
- pinned*.py の SHA-256 は英訳でずれる。公開版で取り直し、取り直した版で self-test が緑になることを確かめる（壊して赤も見る）。
- conditions.md・notes.md（日本語・内部の語）は入れるなら英語の要約に（手本は docs/conditions-summary.md）。
- tables.md 系の日本語の見出し、results の provenance の鍵名（gse_replay）・klicke のパス表記を直す。

## 3. 終わったら
- 公開の前に中身の一覧（ファイルの木と大きさ）を研究者に AskUserQuestion で見せ、GitHub の public 化と Zenodo の publish の承認を取る。publish の前に unsubmitted・ファイルの md5・題・種別を assert（memory: zenodo-api-token-and-draft-doi）。公開アーカイブの漏れの道（コミットのメッセージ・作者メール・派生値）も見る（memory: archive-publish-leak-channels）。
- 投稿のときは supplement.pdf を ESM_1.pdf の名前で出す（規程: 連番のファイル名）。
