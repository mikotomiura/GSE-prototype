# issue.md 3 問題修正 (Windows SAC / macOS Gatekeeper / macOS Input Monitoring)

## 背景

issue.md に報告された 3 つの配布・権限問題により、ユーザーがアプリを正常に使用できない:

1. **Windows**: NSIS インストーラーが Smart App Control (SAC) にブロックされ起動不可
2. **macOS**: Gatekeeper が「マルウェア検証不可」と表示しアプリを開けない
3. **macOS**: Input Monitoring 権限バナーが表示され続け、打鍵検知が動作しない (Stuck 92.1%)

根本原因として、CI の macOS `codesign` 再署名ステップが entitlements を渡しておらず、
hardened runtime の entitlements が剥がれている致命的バグを特定済み。

## ゴール

- macOS ビルドの entitlements が正しく埋め込まれた状態で配布される
- Windows ユーザーが SAC 環境でもポータブル .exe で起動できる
- 両プラットフォームで問題発生時の診断ガイダンスが UI に表示される

## スコープ

### 含むもの
- CI ワークフロー修正 (macOS codesign + Windows portable)
- Entitlements.plist 修正 (allow-jit 追加)
- Dashboard UI の診断ガイダンス強化
- get_diagnostics Tauri コマンド追加
- バージョンバンプ (0.1.12 → 0.1.13)

### 含まないもの
- Apple Developer 証明書の取得・Notarization 対応
- Windows EV 証明書の取得・コード署名
- hook_windows.rs / hook_macos.rs のフックロジック変更 (修正済み)
- HMM エンジン・分析ロジックの変更

## 受け入れ条件

- [x] Entitlements.plist に allow-jit が含まれる
- [ ] CI の macOS codesign ステップが --entitlements 付きで再署名する
- [ ] CI の Windows ビルドがポータブル .exe をアーティファクトに含む
- [ ] Dashboard に macOS/Windows 別の診断ガイダンスが表示される
- [ ] get_diagnostics コマンドが hook_active, OS, arch を返す
- [ ] cargo check が通る

## 関連ドキュメント

- .claude/plans/cozy-snuggling-brooks.md (承認済みプラン)
- .steering/20260413-hook-detection-fix/ (前回の hook 修正タスク)
- docs/architecture.md のスレッドモデル
