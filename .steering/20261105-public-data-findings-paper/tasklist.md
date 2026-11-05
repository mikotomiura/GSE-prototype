# タスクリスト

## 場面ごとの道具（完了前に照合する）

| 場面 | 使うもの |
|---|---|
| 文献の調べ | /literature-review・Sonnet のサブエージェントを問いごとに並列（入れ子禁止・締切つき） |
| 取れない一次資料 | 著者のページ・リポジトリ・OA を探す。curl で取れない URL は Chrome |
| カード・出典 | literature-card・citation-ssot（append はメインが直列）・check_citations.py |
| 逐語の照合 | メインが一次を開く（verify-before-claiming） |
| 研究者の判断 | AskUserQuestion（日本語・1 問ずつ・推奨と理由） |
| 主張の確定 | paper-write Step 0 → /reimagine |
| 原稿の攻撃 | attack-me（Codex を加えるかを先に聞く） |
| 完了 | /cross-review・/finish-task（docs だけの PR は [skip ci]・push は研究者の手元） |

## 文献のラウンド
- [x] 下位の問いの分け方を決める（判断 1）
- [x] Q1〜Q4 を並列に調べる
- [x] 主要な主張の逐語を一次で照合する
- [x] 3 票の検証・カード作成
- [x] references.md に登録（V413 から・P485〜P554 は避ける）
- [x] _index.md に追記・research-positioning への還元の判断（還元は本数と主張の確定の後に回す）
- [x] check_citations.py: 違反は V386〜V412 の欠番 1 件だけ（判断 3・S-DQ の合流で消える）
- [x] ラウンドを単独でコミット（1f6fe10b）

## 本数と主張
- [x] 1 本か 2 本かを研究者に聞く（判断 4）
- [x] 読者と変えたいこと（判断 5）
- [x] 主張と新規性の初回案 → /reimagine → 比べて確定（判断 9）
- [x] 濃くする道（判断 6・4 つとも）
- [x] O1 の部分を使うか（判断 7・使わない・計算は Mac）

## 完了処理
- [ ] /cross-review
- [ ] /finish-task

## 次の段（論文 1）
- [x] 投稿先の適合（`paper-write/venue-fit.md`・判断 8・JEDM）
- [x] JEDM の最近の論文 3〜5 本の長さと節の並び・テンプレートの確認（Step 0 の残り・6 本・中央値約 10,200 語・上限の規定なし・予算は `paper-write/length-log.md`）
- [x] 主張と新規性の初回案（Step 1）→ /reimagine → 比べて確定（判断 9・`paper-write/outline.md`）
- [x] 事前登録の草案（判断 10・`paper-write/prereg-draft.md`）
- [x] attack-me round 1（Codex あり・major・判断 11）→ 草案 v2
- [x] 凍結の前の計算 2 つ（`experiments/20261105-findings-paper1-prefreeze/`）→ 草案 v3 に値・付録 A・版を入れる（判断 12）
- [x] attack-me round 2（major・判断 13）→ 確認のスクリプトと空回し（09f33230）→ 草案 v4（dad32265）
- [x] attack-me round 3（major・査読者は major 1・minor 2・判断 14）
- [ ] 判断 14 の直し・P8 の感度の全部・空回しのやり直し・草案 v5（引き継ぎ `_handoff/next-session-gse-public-data-findings-paper-4.md`）
- [x] attack-me round 4・5（判断 16〜18）
- [x] 判断 18 の 3 点（正の順位・H3 を記述・手順を 2 段）をスクリプト・手順・草案に入れる（引き継ぎ `_handoff/next-session-gse-public-data-findings-paper-5.md`）
- [x] 判断 18 の既定の直し（床にない対の始点版・較正の復元抽出・H2 の負例の感度・課題の中の比べと書き手均等・休止の中の記述・門の揺らぎの鍵・注記の番号）と selftest
- [x] /cross-review（cec6c31b 以降）→ 直す（判断 19）
- [x] conditions-5.md をコミット → 見た書き手の空回し（計算 5・照合は全て通過・共通の値は計算 4 と同じ）→ 付録 C
- [x] 2 段の手順の予行（仮の取り置きの clone・1 回目で完走のコミットの欠陥を見つけて直し、やり直して全段通過）
- [x] 計算 6・7（較正の合わせた割合・最も不利な配置・再標本の種を本番に合わせる）
- [x] attack-me round 6〜8（Codex あり・判断 21〜23・round 7・8 と minor で閉じた）
- [x] 英語版（訳・v9・v10 への合わせ・独立の意味の照合・機械の照合のスクリプトと変異の試し）・manifest の作り直し（19 行）
- [x] /cross-review（7b5d28f4 以降・照合のスクリプトの偽陰性と DONE の初期化を直した）
- [ ] OSF で凍結（新しいプロジェクト・1 つ目の登録）
- [ ] 2 段の本計算（2 つ目の登録に start.json・3 つ目の登録に結果）
- [ ] 付録 F の探索・引きの種の幅の記述
- [ ] round 6 に渡す未決: 境界の較正で、138 人を復元で引く版は誤って同等とする割合が信号ごとに 3.0〜4.8%（名目の 2.5% を超える）。非復元の版は 0.2〜1.6%。判定は 2 つの信号の両方なので合わせた割合はこれより小さいが、どちらの引き方を読むかは決めていない
- [x] 草案 v7（E と監査役の本文の指摘・外枠・付録 F）
- [ ] attack-me round 6（回す前に研究者に聞く）→ 英語版 → OSF で凍結
- [ ] 計算（Mac）
