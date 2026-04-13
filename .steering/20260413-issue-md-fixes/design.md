# 設計

## 実装アプローチ

3 つの問題を「配布パイプライン修正」と「UI 診断強化」の 2 軸で解決する。
フックロジック (hook_windows.rs / hook_macos.rs) は前回タスクで修正済みのため変更しない。

### macOS 根本修正: CI codesign + Entitlements

CI の `codesign` 再署名ステップが `--entitlements` を省略しているバグを修正する。
これにより Entitlements.plist の内容 (allow-unsigned-executable-memory, disable-library-validation,
allow-jit) が DMG 内のバイナリに正しく埋め込まれる。

### Windows 代替配布: ポータブル .exe

Smart App Control が NSIS インストーラーをブロックするため、
リリースバイナリ (gse-next.exe) もアーティファクトとして提供する。

### UI 診断強化

Dashboard.tsx にプラットフォーム別の段階的ガイダンスを追加し、
ユーザーが自力で問題を解決できるようにする。
lib.rs に get_diagnostics コマンドを追加しバグ報告を容易にする。

## 変更対象

### 修正するファイル
- `src-tauri/Entitlements.plist` — allow-jit 追加
- `.github/workflows/ci.yml` — macOS codesign 修正 + Windows portable 追加
- `src/components/Dashboard.tsx` — 診断ガイダンス強化
- `src-tauri/src/lib.rs` — get_diagnostics コマンド追加
- `src-tauri/tauri.conf.json` — バージョンバンプ 0.1.12 → 0.1.13

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 影響範囲

- macOS: DMG 内のバイナリ署名が変わる。entitlements が追加される。
- Windows: Release に portable .exe が追加される (既存 NSIS は変更なし)。
- Frontend: Dashboard のフック状態警告バナーが改善される。
- Backend: get_diagnostics コマンドが追加される (既存コマンドに影響なし)。

## 既存パターンとの整合性

- Tauri コマンド: 既存の get_hook_status / get_keyboard_idle_ms と同じパターン
- CI: 既存の build-windows / build-macos ジョブ構造を維持
- Dashboard: 既存の permission-banner コンポーネント内に拡張

## テスト戦略

- cargo check でコンパイル確認
- npm run build でフロントエンドビルド確認
- CI YAML の構文検証
- macOS: 次回 tag push 後に codesign -d --entitlements - で確認 (手動)

## ロールバック計画

git revert で全変更を元に戻せる。CI 変更は既存ジョブの修正のみで新ジョブ追加なし。
