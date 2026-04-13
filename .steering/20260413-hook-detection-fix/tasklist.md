# タスクリスト

## 準備
- [x] issue.md とスクリーンショットの確認
- [x] docs/architecture.md でスレッドモデル確認（事後）
- [x] docs/development-guidelines.md で規約確認（事後）
- [x] hook_windows.rs / hook_macos.rs / hook.rs / lib.rs の精読
- [x] CI ワークフロー (ci.yml) の確認
- [x] tauri.conf.json の確認

## 調査
- [x] Windows: git log で hook_windows.rs の変更履歴を確認 → 初回統合以来変更なし
- [x] Windows: スタンドアロン診断テスト作成・実行 → API 自体は正常動作を実証
- [x] macOS: entitlements / 署名設定の確認 → 未設定を確認
- [x] macOS: xattr コマンドの再帰性確認 → -d は非再帰、-dr が必要

## 実装 (v0.1.8 — HOOK_ACTIVE 共通化)
- [x] hook.rs: HOOK_ACTIVE の #[cfg(target_os = "macos")] 削除
- [x] hook_windows.rs: HOOK_ACTIVE import、自動復旧ループ追加
- [x] lib.rs: get_hook_status を統一実装に変更
- [x] Dashboard.tsx: Windows 向けエラーバナー追加
- [x] Entitlements.plist 新規作成
- [x] tauri.conf.json: macOS bundle 設定追加
- [x] ci.yml: APPLE_SIGNING_IDENTITY 追加
- [x] README.md / README.ja.md: xattr 修正 + トラブルシューティング追加
- [x] cargo check 成功確認

## 実装 (v0.1.9 — GetModuleHandleW)
- [x] Cargo.toml: Win32_System_LibraryLoader feature 追加
- [x] hook_windows.rs: GetModuleHandleW + PeekMessageW 事前初期化
- [x] README: macOS Gatekeeper 両エラーメッセージ文書化
- [x] cargo check 成功確認

## 実装 (v0.1.10 — PeekMessageW ポーリング)
- [x] hook_windows.rs: GetMessageW → PeekMessageW + PM_REMOVE ポーリング
- [x] README: xattr -d → xattr -dr (再帰フラグ追加)
- [x] cargo check 成功確認

## 実装 (v0.1.11 — フック初期化タイミング修正)
- [x] lib.rs: init_hook() を tauri::Builder.run() 前 → setup() 内に移動
- [x] lib.rs: IME ポーリング初期化も setup() 内に移動
- [x] README: codesign --force --deep --sign - 手順追加
- [x] cargo check 成功確認

## レビュー
- [x] code-reviewer によるレビュー（1回目: CRITICAL/HIGH 指摘 → 修正、2回目: 全パス）
- [x] security-checker によるレビュー（既存の wall_server.rs 問題を検出、今回スコープ外）

## 実装 (v0.1.12 — PRESSED_KEYS Mutex 完全除去)
- [x] hook_windows.rs: PRESSED_KEYS (Mutex<HashSet>) をフックコールバックから完全除去
- [x] lib.rs: 分析スレッドに pressed_keys HashSet 追加 (cfg(windows) ガード)
- [x] ci.yml: macOS ビルドに codesign 再署名ステップ追加
- [x] code-reviewer で CLAUDE.md 完全準拠を確認
- [x] cargo check 成功確認

## ドキュメント
- [x] README.md / README.ja.md 更新
- [x] .steering/ 作業記録作成（事後）

## 完了処理
- [x] git commit (4回: v0.1.8, v0.1.9, v0.1.10, v0.1.11)
- [x] git push + tag push
- [x] GitHub Actions リリースビルド確認
