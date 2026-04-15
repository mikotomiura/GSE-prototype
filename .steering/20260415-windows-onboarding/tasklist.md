# タスクリスト — Windows Onboarding

> **Claude Code Windows への指示**: 本ファイルを上から順に実行してください。
> 各ステップの結果は `completion-log.md` に日時と共に記録。ブロッカー発生時は
> `blockers.md` に型・症状・暫定回避策を追記し、影響度に応じて判断を仰ぐ。

---

## Stage A: 環境構築 (30-60 分、初回のみ)

- [x] A-1: **Visual Studio 2022 Build Tools** をインストール
  - Microsoft 公式から Build Tools for Visual Studio 2022 を DL
  - Installer で "Desktop development with C++" ワークロードを選択
  - 検証: `where link.exe` で MSVC の link.exe が表示される
- [x] A-2: **Rust stable** をインストール
  - https://rustup.rs/ の rustup-init.exe を実行
  - デフォルト toolchain (stable-x86_64-pc-windows-msvc) を選択
  - 検証: `rustc --version`, `cargo --version`
- [x] A-3: **Node.js 22 LTS** をインストール
  - 検証: `node --version`, `npm --version`
- [x] A-4: **Git for Windows** をインストール (Git Bash 同梱)
  - インストーラで "Use Git from Windows Command Prompt" を選択
  - 検証: `git --version`
- [x] A-5: **SSH 鍵セットアップ** (GitHub 認証)
  - `ssh-keygen -t ed25519 -C "your_email@example.com"` で鍵生成
  - 公開鍵を GitHub アカウントに追加
  - 検証: `ssh -T git@github.com` で `Hi mikotomiura! You've successfully authenticated` 表示
- [x] A-6: **git 設定**
  ```powershell
  git config --global core.autocrlf input
  git config --global user.name "<your name>"
  git config --global user.email "<your email>"
  ```
- [x] A-7: **Python 3.10+** (gse-dataset スクリプト用)
  - 検証: `python --version`
  - `pip install jsonschema` (validate_schema.py 依存)

## Stage B: 両 repo の clone (5 分)

- [x] B-1: 作業ディレクトリ作成
  ```powershell
  mkdir $env:USERPROFILE\repos
  cd $env:USERPROFILE\repos
  ```
- [x] B-2: gse-prototype を clone
  ```powershell
  git clone git@github.com:mikotomiura/GSE-prototype.git
  ```
- [x] B-3: gse-dataset を clone
  ```powershell
  git clone git@github.com:mikotomiura/gse-dataset.git
  ```
- [x] B-4: 最新確認
  ```powershell
  cd $env:USERPROFILE\repos\GSE-prototype && git log --oneline -1   # => 720b2bb 以降
  cd $env:USERPROFILE\repos\gse-dataset && git log --oneline -1     # => 9d2c4ed 以降
  ```

## Stage C: Build + Test (20-30 分、初回は toolchain download で長い)

- [x] C-1: Rust ビルド
  ```powershell
  cd $env:USERPROFILE\repos\GSE-prototype\src-tauri
  cargo build --target x86_64-pc-windows-msvc
  ```
  期待: warning 0、`Finished dev profile`。初回は 10-15 分
- [x] C-2: 全テスト
  ```powershell
  cargo test --workspace --target x86_64-pc-windows-msvc
  ```
  期待: **51 tests passed, 0 failed**
- [x] C-3: Snapshot 回帰
  ```powershell
  cargo run --bin gse-replay --target x86_64-pc-windows-msvc -- tests\fixtures\minimal.ndjson --snapshot tests\snapshots\minimal.json
  ```
  期待: `OK: 15 snapshots match tests\snapshots\minimal.json`
- [x] C-4: Schema drift check
  ```powershell
  cargo run --bin emit_schema --target x86_64-pc-windows-msvc > $env:TEMP\emitted.json
  fc /b schema\current.json $env:TEMP\emitted.json
  ```
  期待: `FC: 相違点は検出されませんでした` (バイナリ一致)
- [x] C-5: Frontend 型検査
  ```powershell
  cd $env:USERPROFILE\repos\GSE-prototype
  npm install
  npx tsc --noEmit
  npm run build
  ```
  期待: エラー 0、Vite ビルド成功

## Stage D: 実機スモークテスト (15 分)

- [x] D-1: **Tauri dev 起動**
  ```powershell
  cd $env:USERPROFILE\repos\GSE-prototype
  npm run tauri dev
  ```
  期待: Dashboard ウィンドウが開く、Counter widget が表示される
- [x] D-2: **Counter 初期表示確認**
  - Widget に `GT: Flow 0  Inc 0  Stuck 0  Ctrl+Shift+Alt F/I/S` が見える
  - (macOS と違い、hint は Windows 表記 `Ctrl+Shift+Alt` で表示されるはず)
- [x] D-3: **Flow ラベル動作確認**
  - `Ctrl+Shift+Alt+F` を押す → Counter `Flow 0 → 1`
  - 2 秒以内に再押下 → デバウンスで Flow のまま (tracing logに `debounced`)
  - 3 秒以上空けて再押下 → `Flow 2`
- [x] D-4: **Incubation / Stuck 動作確認**
  - `Ctrl+Shift+Alt+I` を 1 回以上 (各 3 秒空けて)
  - `Ctrl+Shift+Alt+S` を 1 回以上
- [x] D-5: **セッション終了**
  - Dashboard の「セッション終了」ボタンを押して正常終了
- [x] D-6: **NDJSON 生成確認**
  ```powershell
  dir $env:USERPROFILE\Documents\GSE-sessions\ | Sort-Object LastWriteTime -Descending | Select-Object -First 3
  ```
  期待: 直近数分で生成された `gse_YYYYMMDD_HHMMSS.ndjson`
- [x] D-7: **NDJSON 内容確認**
  ```powershell
  $SESSION = (dir $env:USERPROFILE\Documents\GSE-sessions\gse_*.ndjson | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
  Get-Content $SESSION | Select-String '"hmm_version"'
  Get-Content $SESSION | Select-String '"type":"user_label"'
  ```
  期待: meta 行に `"hmm_version":"0.2.0"`、user_label 行が複数

## Stage E: Metrics 算出 + dataset repo commit (10 分)

- [x] E-1: Pretty-print 確認
  ```powershell
  cd $env:USERPROFILE\repos\GSE-prototype\src-tauri
  cargo run --bin gse-replay --target x86_64-pc-windows-msvc -- $SESSION --metrics
  ```
  期待: SessionMetrics が表示される、warnings 0
- [x] E-2: JSON 出力を gse-dataset に配置
  ```powershell
  $BASENAME = [System.IO.Path]::GetFileNameWithoutExtension($SESSION)
  $OUTDIR = "$env:USERPROFILE\repos\gse-dataset\metrics\P000\windows"
  mkdir $OUTDIR -ErrorAction SilentlyContinue
  cargo run --bin gse-replay --target x86_64-pc-windows-msvc -- $SESSION --metrics --json `
    | Out-File -FilePath "$OUTDIR\$BASENAME.metrics.json" -Encoding utf8NoBOM
  ```
  期待: `$OUTDIR\<basename>.metrics.json` が生成、JSON として parse 可能
- [x] E-3: Schema validate
  ```powershell
  cd $env:USERPROFILE\repos\gse-dataset
  python scripts/validate_schema.py $SESSION
  ```
  期待: `OK: <path>`
- [x] E-4: gse-dataset commit + push
  ```powershell
  cd $env:USERPROFILE\repos\gse-dataset
  git add metrics/P000/windows/
  $DATE = Get-Date -Format "yyyy-MM-dd"
  git commit -m "data(P000-windows): first session $DATE"
  git push origin main
  ```
  期待: push 成功、GitHub に反映

## Stage F: macOS 側での集約確認 (5 分、macOS 端末で実行)

> Windows 側作業終了後、macOS 側で以下を実行

- [ ] F-1: macOS 側の gse-dataset を pull
  ```bash
  cd /path/to/gse-dataset && git pull
  ```
- [ ] F-2: 集計スクリプトで Windows 分が含まれることを確認
  ```bash
  python scripts/aggregate_metrics.py
  ```
  期待: `session_count` が従来 2 → 3 以上に増加、`metrics/P000/windows/...` が `files:` に含まれる
- [ ] F-3: `--os` フィルタ検証
  ```bash
  python scripts/aggregate_metrics.py --os windows
  python scripts/aggregate_metrics.py --os macos
  ```
  期待: それぞれ当該 OS のみのセッションを集計

## Stage G: 完了処理 (10 分)

- [x] G-1: `completion-log.md` に記入
  - 実行日時 (Windows 側 / macOS 側)
  - Windows PC スペック (OS バージョン、CPU、キーボード配列)
  - Windows 側セッションファイル名
  - 発見したブロッカーの有無
  - 所要時間
- [x] G-2: 発見したブロッカーを `blockers.md` に記録
- [x] G-3: `.steering/20260415-windows-onboarding/tasklist.md` の全項目を `[x]` に
- [ ] G-4: gse-prototype で completion-log の記録を commit + push
  ```powershell
  cd $env:USERPROFILE\repos\GSE-prototype
  git add .steering/20260415-windows-onboarding/
  git commit -m "docs(windows): complete onboarding on $DATE"
  git push origin main
  ```

## Stage H: 定常運用プロトコル確立 (任意、30 分)

- [ ] H-1: `scripts/sync-session.ps1` 雛形を作成 (PowerShell、以降のセッションで
      上記 Stage E の E-2 〜 E-4 を 1 コマンド化)
- [ ] H-2: 初回運用で動作確認
- [ ] H-3: `docs/development-guidelines.md §10` に Windows コマンド例を追補

---

## トラブルシュート早見表

| 症状 | 原因候補 | 対処 |
|---|---|---|
| `cargo build` が `windows.lib not found` | Visual Studio Build Tools 未導入 | Stage A-1 を再実行、再起動 |
| `ssh -T git@github.com` が reject | SSH 鍵未登録 | GitHub Settings → SSH keys で公開鍵追加 |
| `git clone` で "Permission denied" | 同上、または agent 未起動 | `Start-Service ssh-agent; ssh-add` |
| `cargo run` で `link.exe: LNK1181` | MSVC linker が PATH にない | VS Developer PowerShell で起動するか、`vcvarsall.bat x64` |
| Dashboard 起動直後にクラッシュ | webview2 runtime 未導入 | Microsoft Edge WebView2 Runtime を別途インストール |
| Counter が更新されない | global-shortcut 登録失敗 | `%APPDATA%\logs\` の tracing ログで `register failed` を grep |
| `Ctrl+Shift+Alt+F` で別アプリが反応 | システム全体のショートカット衝突 | blockers.md に記録、必要なら lib.rs の Modifiers を変更 |
| schema drift CI FAIL | Windows で `cargo run --bin emit_schema` を実行したが差分あり | emit_schema 出力 (LF 末尾改行) を git 側が正規化、macOS 側で再生成推奨 |
| NDJSON に `\r\n` が混入 | `Out-File` のデフォルトが CRLF | `-Encoding utf8NoBOM` 付き、または `[System.IO.File]::WriteAllText()` |

## Claude Code 投入テンプレ (参考)

Windows 端末で Claude Code を立ち上げた際に以下を投げれば、上記 Stage A〜G を
自動進行できる想定:

```
GSE Phase 1 の Windows onboarding を実行してください。
手順は .steering/20260415-windows-onboarding/tasklist.md に従ってください。

前提:
- Windows 11 実機
- 管理者権限あり
- SSH 鍵は私が既に生成 or Claude Code にガイドしてもらう

ブロッカーに当たったら blockers.md に記録、私に判断を仰いでください。
各 Stage 完了時に completion-log.md を更新してください。
```
