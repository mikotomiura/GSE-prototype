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
- [ ] ラウンドを単独でコミット

## 本数と主張
- [ ] 1 本か 2 本かを研究者に聞く
- [ ] 読者と変えたいこと（paper-write Step 0）
- [ ] 主張と新規性の初回案 → /reimagine → 比べて確定
- [ ] 濃くする道（§4）のどれを足すか
- [ ] O1 の部分を使うか

## 完了処理
- [ ] /cross-review
- [ ] /finish-task
