# Blockers — Windows Onboarding

Windows 実機での検証中に発見したブロッカー・回避策を記録する。初期は空。

## テンプレ

```
### [YYYY-MM-DD] <タイトル>

- **症状**: 何が起きたか
- **再現手順**: 再現性の有無と再現コマンド
- **根本原因**: 判明していれば記載、不明なら「未解明」
- **暫定回避策**: タスクを進めるための迂回手段
- **影響範囲**: Windows 固有 / 両 OS / 特定ハードウェアのみ 等
- **恒久対応**: 後続タスクで対応する場合、担当タスクへのリンク
```

---

## 既知の懸念事項 (実機検証前の予測、実測で確認する項目)

### 懸念1: SmartScreen アラート

- **予測症状**: `cargo tauri dev` で起動する未署名バイナリに Windows Defender SmartScreen が反応する可能性
- **暫定回避策**: SmartScreen ダイアログで「詳細情報 → 実行」を選択
- **恒久対応**: タグ push 時の `build-windows` ジョブで NSIS installer が生成されるが、これも未署名。Phase 2+ で署名証明書導入を検討

### 懸念2: グローバルホットキー衝突

- **予測症状**: `Ctrl+Shift+Alt+F/I/S` が IME 切替・他アプリのショートカットと衝突
- **暫定回避策**: 別キーに変更 (例: F9/F10/F11) する場合は `lib.rs` の `Modifiers` + `Code` を修正し、両 OS で合意
- **恒久対応**: 企業 PC や日本語 IME 利用時の推奨キーマップを blockers.md で収集、必要なら設定可能化

### 懸念3: Webview2 Runtime 未導入

- **予測症状**: Dashboard 起動直後にクラッシュ (`WebView2Loader.dll` not found 等)
- **暫定回避策**: Microsoft Edge WebView2 Runtime を別途インストール
- **恒久対応**: `tauri.conf.json` の `bundle.windows.webviewInstallMode` で自動導入設定 (既に `downloadBootstrapper` がデフォルト)

### 懸念4: グループポリシー制約

- **予測症状**: 企業管理下の Windows で `RegisterHotKey` が失敗、または Hook 登録が拒否される
- **暫定回避策**: 個人 PC での検証を優先
- **恒久対応**: エンタープライズ展開時に検討

### 懸念5: JIS キーボードでの修飾子衝突

- **予測症状**: JIS 配列で `Ctrl+Shift+Alt+F` が特殊文字入力と衝突
- **暫定回避策**: US 配列で検証、JIS 固有の issue は個別記録
- **恒久対応**: キー配列に応じた動的修飾子切替 (Phase 2+)

---

## 実機で発見したブロッカー

(空 — 実機検証後に追記)
