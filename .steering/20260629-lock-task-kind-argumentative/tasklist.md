# タスクリスト

## 実装
- [x] `TASK_KINDS` を論述のみに制限（他 3 種はコメントアウト保持）
- [x] 見出しに「Phase1 は論述に固定」を明記

## テスト
- [x] `npx tsc --noEmit` 通過
- [ ] 手動: スタート画面で論述固定・session_meta.task_kind=argumentative（実機/被験者ビルドで確認）

## 完了処理
- [ ] git commit（feat/fix・scope=frontend）
- [ ] 分析プロンプトに「論述以外を除外するフィルタ」節を追記（収集前データの混入保険）
