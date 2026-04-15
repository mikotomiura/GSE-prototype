# 開発環境セットアップ

## 背景

クリーンチェックアウト直後の `main` (commit `0ac8cd3`) ブランチにおいて、
`node_modules/` が存在せず、Tauri CLI (`npm run tauri ...`) が使えない状態だった。
また、`cargo build --target aarch64-apple-darwin` で `unused_mut` warning が 1 件、
`npm audit` で high 脆弱性が 2 件残っていた。
本タスクは、これらを解消し、開発に着手できる清潔な状態を作る。

## ゴール

- `npm install` 完了し Tauri CLI が起動できる
- `cargo build --target aarch64-apple-darwin` が warning 0 で通る
- `npx tsc --noEmit` がパスする
- `npm audit` が 0 vulnerabilities

## スコープ

### 含むもの
- npm 依存のインストール
- npm パッチレベル脆弱性の修正
- macOS ビルド時の `unused_mut` warning 解消
- 作業ログのドキュメント化

### 含まないもの
- `npm run tauri dev` での実機起動確認（次タスク）
- Windows ビルド検証（CI / 別環境）
- CI ワークフロー整備

## 受け入れ条件

- [x] `npm install` が成功し `node_modules/.bin/tauri` が存在
- [x] `npm audit` が 0 vulnerabilities
- [x] `cargo build --target aarch64-apple-darwin` が warning 0
- [x] `npx tsc --noEmit` がパス
- [x] `.steering/20260415-dev-env-setup/` に作業記録一式

## 関連ドキュメント

- `CLAUDE.md` — 技術的制約、サブエージェント活用ルール
- `docs/development-guidelines.md` — 規約
- メモリ: macOS ビルドコマンド `cargo build --target aarch64-apple-darwin`
