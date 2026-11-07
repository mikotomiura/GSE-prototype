# 論文 2（停滞の形）の原稿: 外枠 v8 → 原稿 → attack-me manuscript

## 背景

- 外枠 v8 は attack-me outline を 5 round 回して閉じた（`.steering/20261107-paper2-outline/decisions.md` 判断 15）。投稿先は JEDM で確定（判断 16）。
- 数は `experiments/20261107-stall-shape-multiverse/notes.md` と `results/` の集計値だけ。

## ゴール

外枠 v8 に沿って、英語・LaTeX（JEDM のテンプレート）で原稿の本文と補足（S1〜S9）を書き、paper-write の Step 2〜7 を通し、attack-me manuscript（Codex を加える・既知の未決の一覧を添える）を回す。

## スコープ

### 含むもの
- `papers/stall-shape-multiverse/manuscript/`（main.tex・sections・appendix・references.bib・build.sh・BUILD.md）と図の集計表（定義ごとの集計値だけ）。
- 語数の測定（`paper-write/length-log.md`）と 7 語の n-gram の重複の検査。
- attack-me manuscript と直し。

### 含まないもの
- 新しい計算（判断 15: 計算の結果を見て主張を替えない）。CS1 2021 の成績（判断 16）。
- 送付状・Zenodo・GitHub の公開・投稿（研究者に確かめる）。push・PR。

## 受け入れ条件

- [ ] 原稿がビルドでき（エラー 0・未定義の参照 0）、本文の語数が予算（6,500・上限 8,000）の中にある。
- [ ] 本文の数が notes.md と results/ の値と一致する（照合の記録）。
- [ ] 公開物の規則（GSE・内部の番号・[Vn]・パスを書かない）に違反しない。
- [ ] attack-me manuscript の記録と判定がある。

## 気をつけること

- 書き手ごとの値・CS1 のデータ・作文の本文を repo の外・外部の LLM へ出さない。Codex に渡すのは原稿の本文だけ。
- `.codex/budget.json` はステージしない。
