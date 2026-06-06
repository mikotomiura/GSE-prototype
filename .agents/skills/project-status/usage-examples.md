# project-status 使用例

## 典型的な呼び出しタイミング

### セッション開始時
```
現在の作業状況を教えて
```
→ project-status が git 状態・進行中タスク・未コミット変更を一括レポート

### コンテキストが不明になったとき
```
今どこまで進んでいたっけ？
```
→ .steering/ の最新 tasklist.md と git log から状況を復元

### タスク切り替え前
```
現在の作業状況を確認してから /clear する
```
→ 未コミット変更・未完了チェックボックスを確認してから切り替え

## 期待されるレポート形式

```
## 現状サマリ
feat(engine): XXX の実装中 (v2.22 相当)

## 進行中の作業
- .steering/20260410-xxx/tasklist.md: 3/7 完了
- 未コミット変更: src-tauri/src/analysis/engine.rs, src/Dashboard.tsx

## 注意すべき点
- engine.rs に未コミット変更あり (cargo fmt 済か確認)
- tasklist.md に未完了タスク 4 件

## 推奨される次のアクション
1. engine.rs の変更をコミット
2. tasklist.md の次のタスクに着手
```

## 動的データ取得の仕組み

このスキルは `context: fork` + `agent: Explore` により、
スキル内の bash コードブロックを実際に実行してリアルタイムデータを取得する。
静的なスキルと異なり、毎回最新の git / ファイル状態を反映する。
