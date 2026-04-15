# 開発ガイドライン

## 1. コーディング規約

### Rust

- **エラーハンドリング**: アプリケーションレベルでは `anyhow::Result` を使用。ライブラリ的なモジュールでは `thiserror` を検討。
- **ログ**: `tracing` クレートを使用（`tracing::info!`, `tracing::warn!`, `tracing::error!`）。`println!` や `eprintln!` は使わない。
- **unsafe ブロック**: Win32 API / macOS フレームワーク FFI 呼び出しに限定し、ラッパー構造体または関数内に隔離する。unsafe の理由をコメントで明記する。
- **Windows API**: `windows` crate (v0.58+) のみ使用。`winapi` crate は禁止。
- **macOS API**: `core-graphics` (0.24) + `core-foundation` (0.10) を使用。低レベル FFI は `#[link]` で直接宣言（ApplicationServices, Carbon, System）。
- **命名**: Rust 標準の snake_case。型は PascalCase。定数は SCREAMING_SNAKE_CASE。
- **フォーマット**: `cargo fmt` に従う。

### TypeScript / React

- **命名**: コンポーネントは PascalCase、変数・関数は camelCase。
- **依存最小化**: 新しいライブラリ追加前に、既存依存で代替可能か確認。
- **型安全**: `any` の使用を避ける。Tauri IPC のレスポンスにも型を付ける。
- **状態管理**: React 組み込みの useState / useRef で十分な場合は外部ライブラリを使わない。

### コメント

- **書くべき場面**: HMM パラメータの根拠（論文参照）、unsafe の安全性説明、非自明なアルゴリズム選択の理由
- **書くべきでない場面**: コードから明らかな処理内容、TODO を放置（修正するか Issue にする）
- **フォーマット**: `//` で単行。ブロックコメントは `///` (doc comment) のみ。

### プラットフォーム別開発環境

- **Windows**: Windows 11, Visual Studio Build Tools (C++ workload — windows crate のコンパイルに必要)
- **macOS**: macOS 13 Ventura 以降, Xcode Command Line Tools
  - TCC 権限はバイナリ変更時にリセットが必要 (`tccutil reset ListenEvent [bundle-id]`)
  - ad-hoc 署名では CDHash が不安定で Input Monitoring が機能しない場合あり
  - quarantine 属性 (`com.apple.quarantine`) が未署名ビルドをブロックする場合は `xattr -cr` で除去
- **共通**: Rust stable, Node.js (Frontend), `cargo tauri dev` で開発

### プラットフォーム固有コーディングガイド

- **条件コンパイル**: `#[cfg(target_os = "windows")]` / `#[cfg(target_os = "macos")]` で分岐
- **モジュール振り分け**: `#[path = "hook_macos.rs"]` で OS 固有実装ファイルを指定
- **共有状態**: 共通ファイル (hook.rs) にアトミック変数、プラットフォーム固有ロジックは `*_{platform}.rs` に配置
- **キーコード統一**: macOS CGKeyCode は hook 層で Windows VK コードに変換。analysis 層は VK コードのみ扱う
- **GCD dispatch ルール**: TIS API, AXIsProcessTrustedWithOptions など macOS メインスレッド必須 API は `dispatch_sync_f` でメイン GCD キューへ dispatch。メインスレッドからの dispatch_sync_f 呼び出しはデッドロックするため禁止

## 2. Git ワークフロー

### ブランチ戦略

- **メインブランチ**: `main` — 常にビルド可能な状態を維持
- **作業ブランチの命名**: `[type]/[task-name]`
  - type: `feature`, `fix`, `refactor`, `docs`, `chore`
  - 例: `feature/onnx-inference`, `fix/ime-polling-crash`

### コミットメッセージ

```
[type]([scope]): [短い説明]

- 変更内容 1
- 変更内容 2

Refs: .steering/[YYYYMMDD]-[task-name]/
```

- **type**: feat, fix, refactor, docs, chore, test
- **scope**: engine, hook, ime, wall, frontend, logger 等
- **例**: `feat(engine): add ONNX Runtime inference path`

### バージョニング

- README の changelog でバージョンを管理（v2.0〜v2.21+）
- コミットメッセージ末尾に `(vX.XX)` を付与（重要な機能変更時）

## 3. テスト方針

### 基本原則: リプレイ CLI を回帰保護の中心に据える (Replay-as-Truth)

GSE はゴールデンセッション NDJSON を入力に `gse-replay` CLI で `analysis::loop_step::step()` を再実行し、`FeatSnapshot` 列の **byte-equal 一致** をもって回帰保護する。リプレイ CLI 1 本で以下の 5 役を兼ねる:

1. 単体テスト (`cargo test` 内の `analysis::features` / `analysis::engine` のピンポイント検証)
2. 統合テスト（沈黙 3 状態機構・Silence-break protection・1Hz ゲート進行の end-to-end 挙動）
3. 回帰テスト（チューニング変更が既存セッション挙動に与える影響を数値で検出）
4. Ground Truth 評価（Phase 1 以降、UserLabel 付きセッションでの precision/recall 算出）
5. パラメータチューニング（同一セッションを異なる定数で再実行し差分を見る）

詳細は `.steering/20260414-improvement-roadmap/design.md` §0.2 および本ガイドラインで規定する。

### 使い方

```bash
# スナップショット生成（初回のみ）
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson > tests/snapshots/minimal.json

# 回帰検証（CI / 手動）
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
# → "OK: N snapshots match ..." で exit 0、差分時は "MISMATCH: ..." で exit 1

# GT メトリクス算出（Phase 1 Task 2、UserLabel 付きセッション向け）
cargo run --bin gse-replay -- <session.ndjson> --metrics         # pretty-print
cargo run --bin gse-replay -- <session.ndjson> --metrics --json  # 構造化 JSON
# --metrics と --snapshot は排他。--json は --metrics 併用時のみ有効。
```

### 範囲区分

| 種類 | 範囲 | 優先度 | 備考 |
|---|---|---|---|
| 単体テスト | `analysis::features` / `analysis::engine` / `analysis::metrics` / `logger` | 高 | 純粋な計算ロジック。両 OS 共通 |
| リプレイ回帰 | `analysis::loop_step::step()` + ゴールデン NDJSON (`--snapshot`) | **最高** | Phase 0 以降の回帰保護の背骨 |
| GT メトリクス | `analysis::metrics` + UserLabel 付き NDJSON (`--metrics` / `--metrics --json`) | 高 | Phase 1 以降、GT セッションの定量評価 (混同行列 / F1 / 中央値)。`--snapshot` と排他 |
| Schema drift check | `emit_schema` 出力 vs `src-tauri/schema/current.json` の byte-equal | **最高** | Phase 1、gse-dataset との schema 整合を機械的にブロック |
| 統合テスト | `lib.rs` のスレッド連携 | 中 | crossbeam channel のモック可能だがコスト高。リプレイで代替 |
| E2E テスト | Tauri アプリ全体 | 低 | OS フックの自動テストは困難。実機手動 |

### `gse-replay` サブコマンドの使い分け (Phase 1)

- **`gse-replay <s>`**: FeatSnapshot 列を JSON 配列で stdout に出す (ゴールデン生成用)
- **`gse-replay <s> --snapshot <golden.json>`**: ゴールデンと byte-equal 比較、差分で exit 1
- **`gse-replay <s> --metrics`**: UserLabel × FeatSnapshot の集計を pretty-print 出力
- **`gse-replay <s> --metrics --json`**: 同じ集計を構造化 JSON で出力 (gse-dataset 共有用)
- **`--metrics` と `--snapshot` は排他** (用途が異なる、両指定で exit 2)
- **`--json` は `--metrics` 併用必須** (生 snapshot 出力には使わない)

### テストの方針

- `analysis/` モジュールは OS 非依存なので、通常の `#[cfg(test)]` + `cargo test` で両 OS 共通に検証可能
- `input/` モジュールは OS フックに依存するため、統合テストは実機で手動確認
- **HMM 挙動を変える変更（遷移行列・放出行列・α 値・摩擦フロア等）を加えた際は**:
  1. `analysis::engine::HMM_VERSION` を SemVer で bump（MAJOR/MINOR/PATCH は engine.rs 冒頭コメント参照）
  2. `gse-replay` でゴールデンスナップショットを再生成
  3. 差分が**意図通り**であることを `.steering/` に記録
  4. 無関係な差分が出たら変更を見直す（意図せぬ副作用の検知）
- セッションログ (NDJSON) の事後分析スクリプトが実質的な回帰テストとして機能

### macOS 固有のテスト考慮事項

- **CGKeyCode → VK マッピング**: 純粋関数のため `cargo test` で単体テスト可能
- **IME 状態機械**: モックイベントで単体テスト可能
- **TCC 権限テスト**: OS システムダイアログのため自動化不可。手動テスト手順を `.steering/` に記録
- **macOS フックの実機テスト**: `cargo tauri dev` でアプリを起動し、Dashboard の診断パネル（hook_active, callback_count, consecutive_tap_failures, using_accessibility_fallback）で動作確認

### CI/CD パイプライン（目標）

現時点では CI/CD 未構成。目標構成:

- **GitHub Actions**: matrix ビルド（windows-latest, macos-latest）
- **Windows ジョブ**: `cargo build`, `cargo clippy`, `cargo test`（analysis/ 単体テスト）
- **macOS ジョブ**: 同上 + TCC 権限テストは自動化不可（手動検証）
- **Frontend ジョブ**: `npm ci && npm run build`
- **将来**: `cargo tauri build` によるディストリビューションアーティファクト生成

## 4. レビュー基準

### 必須チェック

- [ ] `cargo build` が成功する（Windows + macOS 両方でビルド可能）
- [ ] `cargo clippy` の警告がない（または理由付きで `#[allow]`）
- [ ] フックコールバック内にブロッキング処理がない（Windows WH_KEYBOARD_LL / macOS CGEventTap 共通制約）
- [ ] unsafe ブロックに安全性コメントがある
- [ ] Windows: `windows` crate のみ使用（winapi 禁止）/ macOS: `core-graphics` + `core-foundation` + 必要な `#[link]` 宣言
- [ ] macOS: GCD メインキュー必須 API（TIS\*, AXIsProcessTrustedWithOptions）は `dispatch_sync_f` を使用
- [ ] プラットフォーム固有コードは `input/` + `sensors/` に閉じている（`analysis/` に OS API なし）

### 推奨チェック

- [ ] HMM パラメータ変更時はセッションログで事後検証済み
- [ ] 新機能にはユースケースの記述がある
- [ ] エラー条件が tracing で適切にログ出力されている
- [ ] Tauri IPC 失敗時に安全なデフォルト値にフォールバックしている

## 5. パフォーマンス指針

### 厳守事項

- **フックコールバック**: Atomic 操作 + channel send のみ。Mutex ロック、I/O、メモリアロケーション禁止。Windows (WH_KEYBOARD_LL) と macOS (CGEventTap) で同一制約。
- **1Hz ゲート**: Analysis スレッドの recv_timeout で実現。累積ドリフトを防止するため絶対時刻ベースで管理。
- **EWMA 計算**: f64 演算のみ。ヒープアロケーションなし。

### 監視ポイント

- crossbeam channel の try_send 失敗率（warn ログで追跡）
- Logger の 5 秒フラッシュ間隔が I/O 負荷を許容範囲に保っているか
- Wall Server の HTTP レスポンス時間（スマートフォン UX に影響）

## 6. 依存ライブラリの追加基準

新しい crate / npm パッケージを追加する前に確認:

- [ ] 既存の依存で代替できないか？
- [ ] メンテナンスが活発か？（最終リリースが 1 年以内）
- [ ] ライセンスは MIT / Apache-2.0 互換か？
- [ ] コンパイル時間への影響は許容範囲か？（Rust の場合特に重要）
- [ ] `windows` crate の feature flags は必要最小限か？
- [ ] macOS 依存: `Cargo.toml` の `[target.'cfg(target_os = "macos")'.dependencies]` に追加し、ビルド対象外プラットフォームに影響しないことを確認

## 7. セキュリティ指針

- **キーストロークデータ**: VK コードのみ記録。文字内容（Unicode テキスト）は一切記録しない。
- **セッションログ（リアルタイム運用）**: ローカルファイルシステムに保存。リアルタイム推定中の外部送信は行わない。
- **セッションログ（学習データ収集）**: ML モデル学習のためにセッションログを外部に送信する場合は、以下を必須とする:
  - ユーザーの明示的同意（オプトイン）
  - VK コードの匿名化（キー種別カテゴリへの変換等）
  - 送信先・保存期間の明示
  - 送信タイミングはセッション終了後のバッチ処理（リアルタイム送信禁止）
- **Wall Server**: ランダムトークンによるアクセス制御。ローカルネットワークのみ。Win: ファイアウォールルールでポートを動的管理 / mac: 追加管理不要。
- **macOS TCC 権限**: Input Monitoring / Accessibility 権限は最小限の範囲でリクエストする。`tccutil reset` コマンドによるリカバリパスを維持する。
- **Tauri CSP**: `default-src 'self'; style-src 'self' 'unsafe-inline'` — 外部リソースの読み込みを禁止。

## 8. 禁止事項

- ❌ `winapi` crate の使用（`windows` crate v0.58+ のみ）
- ❌ フックコールバック内でのブロッキング操作（Windows WH_KEYBOARD_LL / macOS CGEventTap 共通）
- ❌ グローバル TSF フック（ITfThreadMgr）の使用（UIPI でブロック）
- ❌ キーストロークの文字内容（Unicode テキスト）の記録
- ❌ リアルタイム推定中のセッションデータ外部送信（学習データ収集はセッション終了後にオプトインで許可）
- ❌ `println!` / `eprintln!` の使用（`tracing` を使う）
- ❌ `any` 型の多用（TypeScript）
- ❌ `analysis/` モジュール内での macOS フレームワーク（core-graphics, Carbon 等）の直接呼び出し
- ❌ メインスレッド上での `dispatch_sync_f` 呼び出し（デッドロックの原因）

## 9. Claude Code Hooks (自動強制ガード)

`.claude/settings.json` で設定された hook が、本ガイドラインの一部を **PreToolUse 段階で機械的にブロック** する。新規参加者が「なぜ Edit/Write が拒否されたか」を理解するための仕様メモ。

### 強制ブロック (PreToolUse)

| Hook | 対象 | ブロック条件 |
|---|---|---|
| `pre-edit-steering.sh` | `src-tauri/src/**/*.rs` / `src/**/*.ts(x)` | 直近 7 日内に `.steering/[YYYYMMDD]-*/` が無い、または `requirement.md` / `design.md` / `tasklist.md` のいずれかが欠落 → ブロック。`/start-task` 実行で解消。 |
| `pre-edit-banned.sh` | `*.rs` (tests/ 除く) | `println!` / `eprintln!` の混入 → ブロック (本ガイドライン §8) |
| `pre-edit-banned.sh` | `Cargo.toml` | `winapi` crate の追加 → ブロック (§8) |
| `pre-edit-banned.sh` | `src-tauri/src/analysis/**/*.rs` | `use windows::` / `use core_graphics::` / `use core_foundation::` / `use objc2::` / `use cocoa::` → ブロック (§8 - OS 依存は input/ または sensors*.rs に閉じる) |

### リマインダ (UserPromptSubmit)

毎ターン、CLAUDE.md 精読 + `/reimagine`・`/start-task` 想起のリマインダが注入される。

### 後段チェック (Stop)

`stop-check.sh` がターン終了時に `cargo clippy` (Rust 変更時) と `tsc --noEmit` (TS 変更時) を実行し、エラーがあれば出力。

### Hook 自体を編集する場合

`.claude/hooks/*.sh` の修正後は手動で `bash .claude/hooks/<script>.sh < <test-input.json>` で動作確認すること。テストは `.steering/20260415-dev-env-setup/setup-log.md` を参照。

## 10. Session データ管理 (gse-dataset 連携)

セッション NDJSON は **プライバシー観点から本リポジトリには絶対にコミットしない**。
データは別リポジトリ [mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset)
(private) で管理する。

### 10.1 共有の主役: `metrics.json`

Phase 1 方針 (`.steering/20260415-dataset-repo-setup/`) により、端末間で共有する
アーティファクトは `gse-replay --metrics --json` の出力のみ。生 NDJSON / anonymized
NDJSON は端末ローカル保持、git 経路を使わない。

- metrics.json は ~1 KB/session、集計値と中央値のみで個人情報を含まない
- Phase 2a Go/No-Go 判定 (Stuck precision 平均 ≥ 0.6) はこの集計で行う
- anonymized NDJSON の git 管理化は Phase 2 (ML 訓練データ準備) 時に再判断

### 10.2 各端末でのワークフロー

```bash
# 0) 初回のみ: セッションログの保存先を gse-dataset 側に向ける (任意、推奨)
#    shell rc (bash: ~/.bashrc, zsh: ~/.zshrc, PowerShell: $PROFILE) に永続化推奨
export GSE_DATASET=/path/to/gse-dataset   # macOS/Linux
# PowerShell: [Environment]::SetEnvironmentVariable('GSE_DATASET', 'C:\gse-dataset', 'User')
# → 未設定の場合は ~/Documents/GSE-sessions/ に fallback

# 1) セッション取得 (macOS/Windows どちらでも)
npm run tauri dev  # Dashboard で作業、⌘⇧⌥ F/I/S (macOS) / Ctrl+Shift+Alt+F/I/S でラベル
# → $GSE_DATASET/raw/P000/gse_YYYYMMDD_HHMMSS.ndjson (env 設定時)
#    または ~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson (fallback)
# 起動時 tracing log で resolved_log_dir と source を確認できる

# 2) メトリクス算出 + gse-dataset に配置
cd src-tauri
SESSION=$GSE_DATASET/raw/P000/gse_YYYYMMDD_HHMMSS.ndjson  # or Documents 下
cargo run --bin gse-replay -- $SESSION --metrics --json \
  > /path/to/gse-dataset/metrics/P000/<macos|windows>/$(basename $SESSION .ndjson).metrics.json

# 3) gse-dataset で commit + push
cd /path/to/gse-dataset
git add metrics/
git commit -m "data(P000-<os>): add $(date +%Y-%m-%d) sessions"
git push
```

**ショートカット (推奨)**: 上記 Step 2 + 3 は `scripts/sync-session.*` で 1 コマンド化されている:

```bash
# macOS / Linux
./scripts/sync-session.sh ~/Documents/GSE-sessions/gse_*.ndjson
./scripts/sync-session.sh $GSE_DATASET/raw/P000/gse_*.ndjson --no-commit  # dry-run

# Windows (実行ポリシー拒否時は -ExecutionPolicy Bypass を追加)
pwsh -NoProfile -File scripts\sync-session.ps1 `
    -SessionPath C:\gse-dataset\raw\P000\gse_*.ndjson
pwsh -NoProfile -File scripts\sync-session.ps1 `
    -SessionPath ... -NoCommit  # dry-run
```

両 script は同じ I/O 契約 (位置引数 1 / `--output-dir` / `--no-commit` / exit code 0-3) に揃えてある。
内部で `gse-replay --metrics --json` → `validate_schema.py` → `git add/commit/push` を順に実行し、
各 Step の exit code を伝搬する。

#### 10.2.1 PowerShell 5.1 script を書くときの注意 (2026-04-16 判明)

`scripts/sync-session.ps1` 実装中に、以下の挙動を複数回踏んだ。将来 `scripts/*.ps1`
を追加・編集する際に同じ落とし穴を避けるための記録:

- **`$PSCommandPath` / `$PSScriptRoot` / `$MyInvocation.MyCommand.Path` / `$env:TEMP` / `$env:TMP` が null/空**
  になる invocation パスが存在する (Git Bash → `powershell.exe` ブリッジで特に顕著)。
  → repo root や temp path は**パラメータ化**して呼び出し元から明示的に受け取る。
  例: `[string]$RepoRoot = $(if ($env:GSE_PROTOTYPE_ROOT) { $env:GSE_PROTOTYPE_ROOT } else { 'C:\GSE-prototype' })`
- **`$LASTEXITCODE` が CmdletBinding + 変数代入の組合せで消費され null 化**する。
  → native cmd の成否判定は **LASTEXITCODE に頼らず、出力ファイルのサイズ + `ConvertFrom-Json` での parseability 検証** を推奨。
- **`Join-Path $a $b` が条件により空を返す**事例あり。
  → `-Path` / `-ChildPath` の名前付き引数指定か、もっとシンプルに文字列結合 `"$a\$b"` で回避。
- **変数 interpolation が初回アクセスまで null に見える**ケースあり。
  → 使う前に 1 度 `Write-Host "[debug] var=$var"` で pre-access してから本体で参照する。
- **`> $file` リダイレクト出力は UTF-16 BOM でエンコードされる** (git diff に BOM が混入)。
  → 変数にキャプチャしてから `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))` で UTF-8 NoBOM へ書く。

これらは `scripts/sync-session.ps1` 内のコメントにも併記済み。bash 側 (`sync-session.sh`) は
`set -euo pipefail` + `bash -n` 構文チェックで十分堅牢 (同種の問題は発生せず)。

### 10.3 Schema 管理 (機械生成)

NDJSON スキーマは gse-prototype の Rust 型 (`src-tauri/src/schema_dto.rs`) が
単一の真実。`cargo run --bin emit_schema` で `src-tauri/schema/current.json` に
出力し、gse-dataset 側の `schema/current.json` に同じ内容をコピーする。

- schema/v1.json / v2.json / … の手書きバージョニング方式は **廃止**
- CI (`.github/workflows/ci.yml` の `check` ジョブ) が `emit_schema` の現在出力と
  `src-tauri/schema/current.json` を diff して drift を機械的にブロックする
- `schema_dto.rs` を更新したら: (1) `cargo run --bin emit_schema > schema/current.json`
  (2) gse-dataset 側にコピー (3) 両 repo を同期 commit

### 10.4 プライバシー原則

- `raw/` ディレクトリは gse-dataset 側の `.gitignore` で永続的に除外
- 外部被験者 P001+ のデータは暗号化ローカル保管、GitHub (private 含む) 経路を使わない
- `anonymize.py` はスクリプトとして存在するが、Phase 1 では出力を commit しない
