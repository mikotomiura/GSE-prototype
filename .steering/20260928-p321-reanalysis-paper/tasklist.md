# タスクリスト — p321-reanalysis-paper

## 1. 準備
- [x] 引き継ぎと一次資料（判断 16・`notes.md` §4 §9・references [P321] [P433] [P434]・`data.md`）を読む
- [x] grill: 投稿先 = EASE 2027 Short／主系列 = 正式版（条件つき）／範囲 = 解析＋外枠／プレプリントは規程確認後（判断 1–4）
- [x] ブランチ `docs/p321-reanalysis-paper`（origin/main から）
- [x] 用語集に 2 語を追加

## 2. 正式版パッケージ
- [x] figshare を実ブラウザで開き、ファイル名・サイズを示して承認を得てダウンロード
- [x] v1 との差分を特定（`rowData.json`・コードブックはバイト同一／`interviews .pdf` のみ追加）
- [x] [P433] の Consult の報告値を定義ごとに当て、単一規則では再現できないことを確認（判断 7）
- [ ] `docs/references.md` [P433] の gloss に追記

## 3. 解析（新リポジトリ）
- [x] 別リポジトリ作成（判断 6）
- [x] 定義を `config.json` に凍結してコミット（判断 5）
- [x] 転記 A と本文ベースの追加分
- [ ] 転記 B（独立 subagent）を受け取り、A と照合
- [x] 解析コード・`run.sh`（自己検査は B 以外すべて緑）
- [ ] `bash run.sh` exit 0・結果の確認・コミット
- [ ] 旧実験（2026-09-06）の値との一致確認（strict / DF1）

## 4. 位置づけのサーヴェイ
- [ ] `/literature-review` 1 ラウンド（help-seeking・debugging の観察研究・outcome の定義と中止の混入）

## 5. 外枠
- [ ] `outline.md`（主張 ↔ 根拠の対応表・6 頁の節構成）

## 6. 完了
- [ ] `/finish-task`（レビュー・`/cross-review`・コミット・PR）
