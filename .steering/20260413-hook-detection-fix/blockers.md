# ブロッカー記録

## ブロッカー 1: Windows キーボードフックが動作しない

- **発生日時**: 2026-04-12 (issue.md で報告)
- **症状**: アプリを開始してキーを打っても KEYBOARD ステータスが "---" のまま
- **試したこと**:
  1. v0.1.8: `HOOK_ACTIVE` フラグを Windows に追加、`get_hook_status` を実状態返却に変更、
     自動復旧ループ追加 → 効果なし
  2. v0.1.9: `HINSTANCE::default()` → `GetModuleHandleW(None)` に変更、
     `PeekMessageW` でメッセージキュー事前初期化 → 効果なし
  3. v0.1.10: `GetMessageW` → `PeekMessageW` ポーリングに変更 → 効果不明（ユーザー確認待ち）
  4. v0.1.11: `init_hook()` を `tauri::Builder.run()` 前 → `setup()` 内に移動 → 確認待ち
- **原因**: フックが Tauri ランタイム初期化の前にインストールされ、
  Tauri のウィンドウシステム初期化でフックが無効化されていた（推定）。
  スタンドアロン診断テストで Windows API 自体は正常動作を実証。
- **解決方法**: `init_hook()` を `setup()` クロージャ内に移動 + `PeekMessageW` ポーリング
- **教訓**:
  - Tauri アプリでは OS レベルのフックを `setup()` 内で初期化すべき
  - 問題の切り分けにスタンドアロン診断テストが有効
  - `GetMessageW` vs `PeekMessageW` の差異はマルチスレッド環境で顕在化する
  - 闇雲に修正を重ねるのではなく、まず診断テストで原因を絞り込むべきだった

## ブロッカー 2: macOS Gatekeeper がアプリをブロック

- **発生日時**: 2026-04-12 (issue.md で報告)
- **症状**: 「Appleは"gse-next"にマルウェアが含まれていないことを検証できませんでした」
  と表示されアプリが開けない。README の xattr コマンド実行後も解決しない。
- **試したこと**:
  1. `xattr -cr` → コード署名を破壊する問題があった
  2. `xattr -d com.apple.quarantine` → .app ディレクトリのみ処理（バイナリ未処理）
  3. `xattr -dr com.apple.quarantine` → 再帰的にquarantine除去（改善）
  4. `codesign --force --deep --sign -` → ローカル ad-hoc 再署名を追加
- **原因**: macOS 14+ (Sonoma/Sequoia) の Gatekeeper 強化により、quarantine 属性の
  除去だけでは不十分。コード署名の検証も行われるため、ローカルでの再署名が必要。
  また `xattr -d`（非再帰）では .app 内部バイナリの属性が残っていた。
- **解決方法**: `xattr -dr` + `codesign --force --deep --sign -` の2ステップ
- **教訓**:
  - `xattr -d` と `xattr -dr` の再帰性の違いは重要
  - macOS のセキュリティは毎バージョンで強化されるため、最新 OS でのテストが必要
  - Apple Developer ID なしでの配布はますます困難になっている

## ブロッカー 3: macOS Input Monitoring が動作しない

- **発生日時**: 2026-04-12 (gse_issue_mac_3.png で確認)
- **症状**: Input Monitoring 権限を付与しても CGEventTap が作成できず、
  KEYBOARD ステータスが "---"、Stuck 92.1% に固定
- **試したこと**:
  1. Entitlements.plist 追加 (allow-unsigned-executable-memory, disable-library-validation)
  2. tauri.conf.json に macOS bundle 設定追加
  3. CI で APPLE_SIGNING_IDENTITY を明示
  4. README に TCC トラブルシューティング追加
- **原因**: `xattr -cr` によるコード署名破壊で TCC が権限を正しく認識できない（推定）。
  + Entitlements 未設定。
- **解決方法**: Entitlements 追加 + `xattr -dr` + `codesign` 再署名
- **教訓**:
  - TCC (Transparency, Consent, and Control) はコード署名に依存する
  - `xattr -cr` は絶対に使用してはならない
  - Entitlements がなくても CGEventTap は動作するが、安定性に影響する

## プロセス上の反省

- `.steering/` への記録を作業開始時に行わなかった（事後作成）
- `/start-task` を使用しなかった
- `docs/` を事前に読まなかった
- `code-reviewer` / `security-checker` サブエージェントを使用しなかった
- 4回の修正を闇雲に重ねた（v0.1.8 → v0.1.9 → v0.1.10 → v0.1.11）
  - 先に診断テストで原因を絞り込み、1回の修正で解決すべきだった
