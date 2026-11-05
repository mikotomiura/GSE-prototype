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
- [ ] 主張と新規性の初回案 → /reimagine → 比べて確定
- [x] 濃くする道（判断 6・4 つとも）
- [x] O1 の部分を使うか（判断 7・使わない・計算は Mac）

## 完了処理
- [ ] /cross-review
- [ ] /finish-task

## 次の段（論文 1）
- [x] 投稿先の適合（`paper-write/venue-fit.md`・判断 8・JEDM）
- [ ] JEDM の最近の論文 3〜5 本の長さと節の並び・テンプレートの確認（Step 0 の残り）
- [ ] 主張と新規性の初回案（Step 1）→ /reimagine → 比べて確定
- [ ] 事前登録の草案（判断 6 の 4 つの計算・同等性の幅を先に決める）→ attack-me（Codex を加えるかを先に聞く）→ OSF で凍結
- [ ] 計算（Mac）
