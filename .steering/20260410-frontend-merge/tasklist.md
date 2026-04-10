# タスクリスト

## 準備
- [x] docs/functional-design.md を読む
- [x] docs/architecture.md を読む（IPC セクション）
- [x] src/ 配下の現状を file-finder で調査
- [x] 未実装コンポーネントの洗い出し

## 実装
- [x] App.css: permission-banner 系 CSS クラス追加（5 クラス）
- [x] App.css: QR/Wall 系 CSS クラス追加（4 クラス）+ .wall-url → .qr-url リネーム + .scramble-animation 削除
- [x] App.tsx: handleStart エラー時に return 追加（macOS 権限なし時のバグ修正）
- [x] App.tsx: hookActive エラーフォールバックを false に修正
- [x] index.html: タイトルを "GSE" に変更
- [x] package.json: 未使用 @tauri-apps/plugin-opener を削除 + npm install

## テスト
- [x] npm run build でビルド成功確認（TypeScript + Vite）
- [ ] ビルドが macOS でも通ることを確認（CI / GitHub Actions）

## レビュー
- [x] code-reviewer によるレビュー
- [x] HIGH 指摘への対応（capabilities/default.json から opener:default 削除）
- [x] MEDIUM 指摘への対応（.qr-url セレクタ specificity 修正、@keyframes bounce 削除）

## ドキュメント
- [x] docs の更新（不要と判断）

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の作成
- [ ] git commit
