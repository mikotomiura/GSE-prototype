# タスクリスト

## 場面ごとの道具（完了前に照合する）
- 設計の判断 → AskUserQuestion（済み・判断 1）
- 実験 → reproducibility-discipline（conditions を計算の前にコミット・seed・provenance）
- コード → 完了時に code-reviewer ＋ /cross-review（Codex には条件・コード・集計値だけ）

## 条件と作り
- [x] requirement・design・decisions（判断 1・2）
- [x] conditions.md・README・SEED・env・run.sh・mutate.sh・scripts
- [x] 門 W1・W2 緑・変異 w1・w2 が赤・3 反復の配管の通し（W4 は反復の数の違いで FAIL が正しい）
- [x] conditions とコードをコミット（計算の前）

## 計算
- [x] 本計算（run.sh・108 セル × 400 反復）・W4 緑
- [x] report（規則の答え）・記述の節を足した（判断 3）

## 記録
- [x] notes.md（結果・規則の答え・読まないこと）
- [ ] 完了時の code-reviewer ＋ /cross-review・指摘の直し
- [ ] 研究者が規則の答えを見て S1-E8 の値を決める
- [ ] push（PR は exp/gse-coauthor-ml-improve が main に入った後・研究者に確かめてから）
