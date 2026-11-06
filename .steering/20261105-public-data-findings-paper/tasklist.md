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
- [x] OSF で凍結（プロジェクト cm4ru・1 つ目の登録 https://osf.io/mrkxt）
- [x] 2 段の本計算（開始 https://osf.io/hfvy7 → 変換の照合で中断 → 逸脱 1 https://osf.io/fqgcp → 開始 https://osf.io/ajg2x → 完走 4a30ce6e・H1 支持）
- [x] 結果と来歴を OSF の 5 つ目の登録に（https://osf.io/uj6cy・2026-11-06）
- [x] 付録 F の探索（CS1 2021 年版・KLiCKe）・引きの種の幅の記述
- [x] 付録 F の CoAuthor（橋渡し X6・X7・門 G1/G2・/cross-review の直し ed548609）
- [x] 外枠を結果の後に確定（判断 24）→ attack-me outline round 1（major）→ 直し（判断 25）
- [x] 関連研究の 3 つの柱の /literature-review（未登録の文献だけ・判断 26・[V427]〜[V464]）
- [x] 休止の位置の探索 X8（判断 27・df14c58d）
- [x] attack-me outline round 2（major・判断 28）→ v3
- [x] attack-me outline round 3（major・C2 を手順と限界へ・判断 29）→ v4
- [x] 文献 [V465]（判断 30）→ attack-me outline round 4（major・査読者 3 人 minor・E 直してから・判断 31）→ v5
- [x] attack-me outline round 5（major・査読者 3 人と Codex は minor・E 直してから）→ 研究者の判断で閉じた → v6（判断 32）
- [ ] 草稿の前に数えるもの（条件を先にコミット・判断 32）: 複数の文字の編集の出来事の割合・信号の全時間の挙動・3 区分の実効の書き手
- [ ] 原稿（JEDM・英語・MacTeX）
- [ ] round 6 に渡す未決: 境界の較正で、138 人を復元で引く版は誤って同等とする割合が信号ごとに 3.0〜4.8%（名目の 2.5% を超える）。非復元の版は 0.2〜1.6%。判定は 2 つの信号の両方なので合わせた割合はこれより小さいが、どちらの引き方を読むかは決めていない
- [x] 草案 v7（E と監査役の本文の指摘・外枠・付録 F）
- [ ] attack-me round 6（回す前に研究者に聞く）→ 英語版 → OSF で凍結
- [ ] 計算（Mac）
