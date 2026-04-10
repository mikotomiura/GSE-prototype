# frontend-merge

## 背景

GSE プロジェクトは Tauri 2.0 + Rust (Backend) + React/TypeScript (Frontend) で構成される。
macOS との統合を視野に入れたフロントエンド実装が未完成であり、
Windows と macOS の両プラットフォームで動作するUI層を完成させる必要がある。

## ゴール

GSE フロントエンド（React/TypeScript）の実装を完了させ、
macOS・Windows 両プラットフォームで正常に動作する状態にする。

## スコープ

### 含むもの
- React/TypeScript の UI コンポーネント実装
- Tauri IPC (invoke / listen) を通じたバックエンドとの連携
- クロスプラットフォーム対応（macOS / Windows）
- Dashboard, Overlay などのメイン画面
- 介入 UI（Nudge, Wall 等）のフロントエンド部分

### 含まないもの
- Rust バックエンドエンジン（HMM 認知状態推定、フック、IME 等）
- analysis/ モジュールの実装
- Windows API / macOS API の直接呼び出し

## 受け入れ条件

- [ ] 主要 UI コンポーネントが実装されている
- [ ] Tauri IPC 経由でバックエンドと正常に通信できる
- [ ] macOS / Windows 両環境でビルドが通る
- [ ] ビジュアルが機能仕様（functional-design.md）と一致している

## 関連ドキュメント

- docs/functional-design.md — 機能要件・介入フロー
- docs/architecture.md — Tauri IPC・スレッドモデル
- docs/repository-structure.md — src/ 配下のファイル配置
