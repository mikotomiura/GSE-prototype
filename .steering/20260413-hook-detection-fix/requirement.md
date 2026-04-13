# requirement: Windows キーボード検知不具合 & macOS Gatekeeper / Input Monitoring 修正

## 背景

v0.1.7 リリース後、2つの重大な問題が報告された:

1. **Windows**: アプリを開始してもキーボードの打鍵が一切検知されない。
   Smart App Control (SAC) でインストーラーがブロックされる問題は解決済み。
   アプリは起動するが、キーボード入力に対して反応しない。

2. **macOS**: ダウンロードしたアプリを開こうとすると「Appleは"gse-next"に
   マルウェアが含まれていないことを検証できませんでした」と表示され開けない。
   README の手順を全て実行しても解決しない。
   また、以前からの Input Monitoring 権限付与後もキーボード検知が動作しない
   問題も未解決。

## ゴール

- Windows 版でキーボード打鍵が正しく検知され、認知状態推定が動作する
- macOS 版で Gatekeeper をパスしてアプリが起動できる
- macOS 版で Input Monitoring 権限付与後にキーボード検知が動作する

## スコープ

### 含むもの
- Windows キーボードフック (`WH_KEYBOARD_LL`) の初期化・動作修正
- macOS Gatekeeper 回避手順の改善
- macOS Input Monitoring (CGEventTap) の署名/entitlements 対応
- CI ワークフローの macOS 署名設定
- README インストール手順の修正

### 含まないもの
- Apple Developer ID 署名 (有料、$99/年) の導入
- Windows EV コード署名証明書の導入
- HMM エンジン・分析ロジックの変更

## 受け入れ条件

- [x] Windows でアプリ起動後、キーボード打鍵が KEYBOARD ステータスに反映される
- [x] macOS で README 手順に従えば Gatekeeper をパスできる
- [x] macOS で Input Monitoring 権限付与後にキーボード検知が動作する
- [x] `cargo check` が Windows / macOS 両方でパスする
- [x] CI (GitHub Actions) で Windows NSIS / macOS DMG ビルドが成功する

## 関連ドキュメント

- docs/architecture.md — スレッドモデル・Hook Thread 設計
- docs/development-guidelines.md — コーディング規約・Git ワークフロー
- CLAUDE.md — 技術的制約 (windows crate, unsafe ルール, フックコールバック制約)
