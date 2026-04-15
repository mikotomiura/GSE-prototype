# Windows Onboarding — design

## 実装アプローチ

macOS 側で既に完成している実装とワークフローを、**Windows 固有の違い**
(`#[cfg]` 分岐、パス区切り、CRLF、Build Tools 依存、ホットキー修飾子) を吸収する
翻訳層として記述する。新規コード開発は不要。

## Windows 固有の翻訳ポイント

### 1. 修飾子キーの自動切替 (既に実装済み)

`lib.rs` の `#[cfg]` 分岐:
```rust
#[cfg(target_os = "macos")]
let mods = Modifiers::SUPER | Modifiers::SHIFT | Modifiers::ALT;
#[cfg(not(target_os = "macos"))]
let mods = Modifiers::CONTROL | Modifiers::SHIFT | Modifiers::ALT;
```

Windows では自動的に `Ctrl+Shift+Alt+F/I/S` が登録される。確認のみ。

### 2. セッションログのパス

- macOS: `~/Documents/GSE-sessions/gse_*.ndjson`
- Windows: `%USERPROFILE%\Documents\GSE-sessions\gse_*.ndjson`

logger.rs は `dirs::document_dir()` を使っている想定。確認のみ。

### 3. 改行コード対策

- CI は `.gitattributes` で `schema/current.json` と metrics JSON を LF 固定
- Windows 側開発者は `git config --global core.autocrlf input` を事前設定
- emit_schema 出力を Windows 側で再生成すると LF で書かれる (`writeln!` は OS 改行ではなく `\n`)、しかし Cargo toolchain が変わると念のため drift check する

### 4. Build Tools

`windows` crate (v0.58+) のコンパイルに C++ toolchain 必要:
- Visual Studio 2022 Build Tools をインストール (Community エディションでも可)
- ワークロード: "Desktop development with C++"
- これなしでは `cargo build` が初回で失敗する

### 5. PowerShell vs cmd.exe vs WSL

推奨は **Git Bash または PowerShell**。WSL でも動くが TAURI の Webview2 ブリッジが
Linux 扱いになる可能性があるため native Windows shell を使う。

コマンド例は本タスクでは PowerShell で記述する:
```powershell
cd $env:USERPROFILE\repos\GSE-prototype\src-tauri
cargo run --bin gse-replay -- $env:USERPROFILE\Documents\GSE-sessions\gse_*.ndjson --metrics --json `
  | Out-File -FilePath $env:USERPROFILE\repos\gse-dataset\metrics\P000\windows\gse_*.metrics.json -Encoding utf8
```

## 変更対象

### 新規作成するファイル (gse-prototype 側)
- `.steering/20260415-windows-onboarding/requirement.md`
- `.steering/20260415-windows-onboarding/design.md` (本ファイル)
- `.steering/20260415-windows-onboarding/tasklist.md`
- `.steering/20260415-windows-onboarding/blockers.md` (Windows 検証中に発見したブロッカー記録用、初期は空)
- `.steering/20260415-windows-onboarding/completion-log.md` (完了時に記入)
- `scripts/sync-session.ps1` (optional、PowerShell ショートカット)

### 修正するファイル
なし (既存実装は Windows 対応済み)

### 削除するファイル
なし

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| gse-prototype コード | NONE | Windows 対応は既に実装済み | — |
| gse-dataset コード | NONE | OS 別ディレクトリ対応済み | — |
| CI | NONE | 既存の check (windows-latest) ジョブが既に緑化想定 | push 後の Actions で確認 |
| 既存 macOS 運用 | NONE | Windows 側だけ追加される、macOS 側操作は変更なし | — |

## 既存パターンとの整合性

- `.steering/<date>-<task>/` 構造に従う
- `requirement.md` / `design.md` / `tasklist.md` の必須 3 ファイル + `blockers.md` (任意)
- macOS 側 `verification_log.md` (Phase 1 Task 3) と同じ「実測値を記入する」形式を Windows 版で再利用

## テスト戦略

- **受け入れテスト**: requirement.md の受け入れ条件チェックリスト全項目を満たすこと
- **回帰保護**: 既存 snapshot test + schema drift check が Windows で緑化すれば、コード側の Windows 対応は保証される (CI 経由)
- **実機でしか検証できないもの**:
  - global-shortcut の `RegisterHotKey` 実発火
  - Dashboard の Webview2 表示
  - Input Monitoring/Accessibility に相当する Windows 側権限ダイアログ (実際には Windows では UAC や管理者権限は不要、global-shortcut は user scope)

## ロールバック計画

- Windows で重大な issue が発見された場合:
  1. `blockers.md` に記録
  2. 影響が Phase 1 全体に及ぶなら gse-prototype 側で hotfix (macOS 側レビュー後に main へ)
  3. 影響が Windows 固有の local 環境なら回避策を tasklist に追記
- データ面のロールバック: 誤って生 NDJSON を commit してしまった場合、`git filter-branch` で除去 (だが `.gitignore` で raw/ が ignored のため起きない想定)

## 既知の Open 点

- **Windows Defender / SmartScreen**: `cargo tauri dev` は未署名バイナリなので初回起動時にアラートが出る可能性。実機で発見したら `blockers.md` に記録
- **Input Monitoring 相当**: Windows は macOS の TCC 的な権限ダイアログを出さない (global hook は user scope で動く)。起動時の `hook_active` フラグの挙動を Dashboard 診断パネルで確認
- **Corp PC のグループポリシー**: 企業管理下の PC ではグローバルホットキー登録が制限される可能性。個人 PC での検証を推奨
- **キーボード配列 (JIS vs US)**: JIS キーボードでは `Ctrl+Shift+Alt+F` が IME 切替と衝突する可能性。衝突時は tasklist で別キーへの変更を検討
