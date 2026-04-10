# 設計

## 実装アプローチ

- Rust バックエンドは変更しない（クロスプラットフォーム統合済み）
- フロントエンドのロジックは完成済みのため、CSS 補完とバグ修正に限定する
- macOS 版リポのクローン不要（既存デザイン言語から一貫して設計）

## 変更対象

### 修正するファイル
- `src/App.css` — 9 クラス追加（permission-banner 系 5、QR/Wall 系 4）、`.wall-url` → `.qr-url` リネーム、`.scramble-animation` 削除
- `src/App.tsx` — handleStart エラー時に return 追加、hookActive エラーフォールバックを false に修正
- `index.html` — タイトルを "GSE" に変更
- `package.json` — 未使用 @tauri-apps/plugin-opener を削除

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 影響範囲

フロントエンド（src/）のみ。バックエンド（src-tauri/src/）は変更しない。

## 既存パターンとの整合性

- typescript-standards skill に従う
- Tauri IPC は invoke / listen パターンを踏襲

## テスト戦略

- 単体テスト: コンポーネントの描画テスト
- 統合テスト: IPC モックを使ったコンポーネント動作確認
- E2E テスト: 必要に応じて

## ロールバック計画

git revert で元に戻す。フロントエンド限定の変更なのでバックエンドへの影響なし。
