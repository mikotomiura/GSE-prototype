# 設計

## 実装アプローチ

### Windows キーボード検知

段階的に原因を絞り込み、4回の修正を経て根本原因を特定・修正した。

**根本原因**: `init_hook()` が `tauri::Builder.run()` の前に呼ばれていたため、
Tauri のランタイム初期化（ウィンドウシステム、tokio、WebView2）がフックを無効化していた。

**修正**: フック初期化を `setup()` クロージャ内に移動し、Tauri 初期化完了後に実行。

追加で以下も改善:
- `GetMessageW` (ブロッキング) → `PeekMessageW` ポーリング（診断テストで実証済み）
- `HINSTANCE::default()` (NULL) → `GetModuleHandleW(None)` で実モジュールハンドル取得
- `PeekMessageW` による事前メッセージキュー初期化
- `HOOK_ACTIVE` フラグを全プラットフォーム共通化
- `get_hook_status` を実際のフック状態を返すように変更
- フック失敗時の自動復旧ループ追加

### macOS Gatekeeper / Input Monitoring

**Gatekeeper 問題**: 未署名アプリに対する macOS 14+ の厳格化への対応。

- `xattr -d` → `xattr -dr` (再帰的に quarantine のみ削除)
- `codesign --force --deep --sign -` でローカル ad-hoc 再署名
- `Entitlements.plist` 追加 (CGEventTap 用 entitlements)
- Tauri 設定に `bundle.macOS.entitlements` 追加
- CI で `APPLE_SIGNING_IDENTITY: "-"` を明示

## 変更対象

### 修正したファイル
- `src-tauri/src/input/hook_windows.rs` — PeekMessageW ポーリング、GetModuleHandleW、自動復旧ループ
- `src-tauri/src/input/hook.rs` — HOOK_ACTIVE の cfg(target_os) 削除
- `src-tauri/src/lib.rs` — フック初期化を setup() に移動、get_hook_status 統一
- `src-tauri/tauri.conf.json` — macOS bundle 設定、バージョン更新
- `src-tauri/Cargo.toml` — Win32_System_LibraryLoader feature 追加
- `src/components/Dashboard.tsx` — Windows 向けエラーバナー追加
- `.github/workflows/ci.yml` — macOS 署名環境変数
- `README.md` / `README.ja.md` — インストール手順・トラブルシューティング

### 新規作成したファイル
- `src-tauri/Entitlements.plist` — macOS entitlements (CGEventTap 用)

## 影響範囲

- Hook Thread: 初期化タイミングが変更 (Tauri setup 後に遅延)
- IME Polling Thread: 同様に setup 後に初期化
- Analysis Thread: 影響なし (setup 前からドレインモードで待機)
- Frontend: hookActive バナーの表示ロジック拡張

## 既存パターンとの整合性

- macOS 版 `hook_macos.rs` の自動復旧ループパターンを Windows 版に適用
- `HOOK_ACTIVE` フラグを macOS と同じ方式で Windows にも展開
- Tauri `setup()` クロージャ内でのスレッド生成は既存パターン (overlay window 生成) と整合

## テスト戦略

- **診断テスト**: `/tmp/hook_test/` にスタンドアロン Windows API テストを作成・実行
  - `SetWindowsHookExW` + `PeekMessageW` + `SendInput` で 10/10 イベント捕捉成功
  - このテストにより Windows API 自体の問題を除外し、Tauri 統合の問題に焦点を絞った
- **ビルド検証**: `cargo check` でコンパイル確認 (全修正で成功)
- **E2E**: ユーザーによるリリースビルドでの検証待ち

## ロールバック計画

`git revert` で各コミットを個別に戻せる:
- `85e1346` — setup() 移動 (最重要修正)
- `8daa930` — PeekMessageW ポーリング
- `a87aab3` — GetModuleHandleW
- `01e09f9` — HOOK_ACTIVE 共通化
