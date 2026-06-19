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

# v2 介入ポリシーのオフライン反実仮想評価（gse-v2-intervention-eval）
cargo run --bin gse-replay -- <session.ndjson> --intervention        # pretty-print
cargo run --bin gse-replay -- <session.ndjson> --intervention --json # 構造化 JSON
# logged feat を decide() で時刻順ステップし HIR/Precision/DC/Burden を算出。
# --metrics/--segment/--segments/--snapshot と相互排他。--json は併用時のみ有効。
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
- **`gse-replay <s> --intervention [--json]`**: v2 介入ポリシーを反実仮想リプレイし
  HIR/Precision/DC/Burden を算出 (gse-v2-intervention-eval、`analysis::intervention_eval`)。
  logged feat の p_stuck/f3/f4/f6 で `decide()` を時刻順ステップ、GT は point label を
  forward-fill で区間化。**screening 用途**（GT 仮定依存、詳細は steering の decisions.md/results.md）
- **モード系フラグ (`--metrics` / `--segment` / `--segments` / `--snapshot` / `--intervention`) は相互排他** (両指定で exit 2)
- **`--json` は `--metrics` / `--segments` / `--intervention` 併用必須** (生 snapshot 出力には使わない)

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

### CI/CD パイプライン

GitHub Actions (`.github/workflows/ci.yml`) で構成済み。`push` (main / `feature/*`)・`pull_request` (main)・`v*` タグで起動する:

- **`check` ジョブ**: matrix ビルド (windows / macOS target)。`cargo build` → `cargo test --workspace` → スナップショット回帰 (`gse-replay --snapshot`) → schema drift check (`emit_schema` vs `schema/current.json`)
- **`frontend-check` ジョブ**: `npm ci` → TypeScript 型チェック → Vite production ビルド
- **`build-windows` / `build-macos` ジョブ**: `v*` タグ時のみ。Tauri アプリをビルドし NSIS / portable exe / DMG をアーティファクト化 (macOS は entitlements 付き再署名)
- **`release` ジョブ**: 両ビルド成功後に GitHub Release を作成

> **運用上の注意**: GitHub Actions の無料枠 (3000 時間) を超過したため、現状はクラウド CI が利用できず、**ローカル検証で代替**している (`cargo test --workspace` / `gse-replay --snapshot` / `emit_schema` diff を手元で実行)。TCC 権限テストは元々自動化不可で実機手動検証。

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
- **Tauri CSP**: `default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'` (`src-tauri/tauri.conf.json`) — 外部リソースの読み込みを禁止。`img-src` の `data:` は QR コード等のインライン画像のため許可。
- **Tauri capabilities (権限管理)**: Tauri 2.0 では v1 allowlist を使わず `src-tauri/capabilities/default.json` で権限を宣言する (main + overlay + global-shortcut)。新しい IPC コマンドやプラグイン権限を足すときはここを編集する。

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

`.claude/settings.json` で設定された hook が 3 層構造で動作する。全層の出力はユーザーと Claude の双方に明示される。

### Preflight 層 (UserPromptSubmit)

毎ターン `preflight.sh` が自動実行し、プロジェクト状態を 2 行で表示:

```
[preflight] task: 20260416-hook-visibility-improvement (3/3) | reimagine: applied
[preflight] git: 2 uncommitted
```

チェック項目:
- `.steering/` タスクディレクトリの存在と必須 3 ファイル (requirement.md, design.md, tasklist.md)
- `design.md` がテンプレートのままかどうか
- `/reimagine` 適用状態 (design-v1.md の有無 + requirement.md の運用メモ)
- 未コミット変更数

Preflight 層は **BLOCK しない** (WARNING のみ)。プロンプト送信自体をブロックすると作業不能になるため。

### Guard 層 (PreToolUse) — 強制ブロック

Edit/Write/MultiEdit 時に 2 つの guard スクリプトが順に実行。パス時は `[guard] PASS` を明示表示、違反時は `BLOCKED` で編集を拒否:

| Hook | 対象 | ブロック条件 |
|---|---|---|
| `pre-edit-steering.sh` | `src-tauri/src/**/*.rs` / `src/**/*.ts(x)` | 直近 7 日内に `.steering/[YYYYMMDD]-*/` が無い、または `requirement.md` / `design.md` / `tasklist.md` のいずれかが欠落 → ブロック。`/start-task` 実行で解消。 |
| `pre-edit-banned.sh` | `*.rs` (tests/ 除く) | `println!` / `eprintln!` の混入 → ブロック (本ガイドライン §8) |
| `pre-edit-banned.sh` | `Cargo.toml` | `winapi` crate の追加 → ブロック (§8) |
| `pre-edit-banned.sh` | `src-tauri/src/analysis/**/*.rs` | `use windows::` / `use core_graphics::` / `use core_foundation::` / `use objc2::` / `use cocoa::` → ブロック (§8 - OS 依存は input/ または sensors*.rs に閉じる) |

### Report 層 (PostToolUse / Stop)

- **PostToolUse**: `post-fmt.sh` が Edit/Write 後に `cargo fmt` を実行。フォーマット変更があった場合のみ `[fmt] cargo fmt applied` を表示
- **Stop**: `stop-check.sh` がセッション終了時に `cargo clippy` (Rust 変更時) と `tsc --noEmit` (TS 変更時) を実行し、エラーがあれば出力

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

# 0.5) 参加者 ID は既定で自動付与される (env 設定は任意)
# env を何も設定しなくても、初回起動時に端末ごとに一意な不透明 ID
# (P + 12桁hex、例 Pa3f9c2e1b7d0) が自動生成され ~/.gse/participant_id に永続化される。
# 以降の起動は同じ ID を再利用するため、複数被験者が各自の端末で操作しても P000 に衝突しない。
#
# 研究者が ID を明示割当したい場合のみ env で上書きする (env 値は永続化されない):
export GSE_PARTICIPANT_ID=P003   # logger の主変数。raw/<id>/ を切替
# 既存 sync スクリプトと共有する GSE_PID を設定済みなら logger もそれを読む。
#
# 解決順: 永続化値 (~/.gse/participant_id) → GSE_PARTICIPANT_ID → GSE_PID
#         → 自動生成+永続化 → P000 (生成/書込失敗時のみ)。
# ID は [A-Za-z0-9_-] のみ・1..=64 文字 (パストラバーサル防止)。不正値・Windows 予約名
# (CON/NUL 等) は拒否され次候補へフォールバックする。
#
# リセット (別 ID で採り直す): 永続化ファイルを削除すると次回起動で再生成される。
rm ~/.gse/participant_id          # macOS/Linux
# PowerShell: Remove-Item $HOME\.gse\participant_id
#
# 注意: 自動生成 ID は不透明なため、ID→被験者の対応表は研究者が別途管理する。また現状の
# sync スクリプト (sync-session/sync-all) は GSE_PID 前提で metrics/<id>/ を決めるため、
# 自動生成 ID には未追従 (raw と metrics で ID が乖離し得る)。追従は別タスクで対応予定。

# 1) セッション取得 (macOS/Windows どちらでも)
npm run tauri dev  # Dashboard で作業、⌘⇧⌥ F/I/S (macOS) / Ctrl+Shift+Alt+F/I/S でラベル
# → $GSE_DATASET/raw/<participant_id>/gse_YYYYMMDD_HHMMSS.ndjson (env 設定時、既定 P000)
#    または ~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson (fallback)
# 起動時 tracing log で resolved_log_dir / participant_id / source を確認できる

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

**バッチ同期 (複数セッションを一括処理)**: `scripts/sync-all.*` で fallback → raw コピー + 全未処理ファイルの metrics 生成 + 1 commit/push をまとめて行える:

```bash
# macOS / Linux
./scripts/sync-all.sh                    # fallback → raw → metrics → commit+push
./scripts/sync-all.sh --no-commit        # dry-run
./scripts/sync-all.sh --fallback /path   # fallback ディレクトリを指定

# Windows
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sync-all.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\sync-all.ps1 -NoCommit
```

バッチ同期の **Step 0** として `scripts/check_schema_parity.py` が自動で走り、
gse-prototype 側 `src-tauri/schema/current.json` と gse-dataset 側
`schema/current.json` の JSON 意味同値を検証する。ドリフト検出時は
Step 1 以降に進まず、修復コマンド例を出力して停止する。詳細は §10.3 を参照。

#### 10.2.1 PowerShell 5.1 script を書くときの注意 (2026-04-16 判明)

`scripts/sync-session.ps1` 実装中に、以下の挙動を複数回踏んだ。将来 `scripts/*.ps1`
を追加・編集する際に同じ落とし穴を避けるための記録:

- **`$PSCommandPath` / `$PSScriptRoot` / `$MyInvocation.MyCommand.Path` / `$PSHOME` / `$env:TEMP` / `$env:TMP` が null/空**
  になる invocation パスが存在する (Git Bash → `powershell.exe` ブリッジで特に顕著)。
  → repo root や temp path は**パラメータ化**して呼び出し元から明示的に受け取る。
  例: `[string]$RepoRoot = $(if ($env:GSE_PROTOTYPE_ROOT) { $env:GSE_PROTOTYPE_ROOT } else { 'C:\GSE-prototype' })`
  → `$PSHOME` も空になる事象を 2026-04-17 に `sync-all.ps1` が子 PS を起動する際にも確認。
    → 子 PS の解決は `Get-Command pwsh` → `$PSHOME\pwsh.exe` → `$PSHOME\powershell.exe` →
    `$env:windir\System32\WindowsPowerShell\v1.0\powershell.exe` (x64 前提) の順で回避。
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
- **tier-1 check**: CI (`.github/workflows/ci.yml` の `check` ジョブ) が
  `emit_schema` の現在出力と `src-tauri/schema/current.json` を diff して
  repo 内 drift を機械的にブロック
- **tier-2 check**: `scripts/check_schema_parity.py` が
  `src-tauri/schema/current.json` と gse-dataset 側 `schema/current.json` の
  cross-repo drift をバッチ同期の Step 0 で検出 (詳細は §10.3.1)
- `schema_dto.rs` を更新したら: (1) `cargo run --bin emit_schema > schema/current.json`
  (2) gse-dataset 側にコピー (3) 両 repo を同期 commit

#### 10.3.1 バッチ同期時の cross-repo drift guard (2026-04-17 導入)

tier-1 CI check は repo 内の drift のみ対象で、`src-tauri/schema/current.json`
→ `gse-dataset/schema/current.json` のコピー忘れは検知できない。
2026-04-16 の Phase 2b 実装でこの第 3 ステップが抜け、翌日のバッチ同期で初めて
顕在化した事例を受け、pre-flight check を導入した。

- 実装: `scripts/check_schema_parity.py` (Python 3.9+ 依存、標準ライブラリのみ)
- 呼出し箇所は 2 段の多層防御:
  - **tier-2 (バッチ同期時)**: `scripts/sync-all.ps1` / `scripts/sync-all.sh`
    が Step 0 として実行。既に閉じた過去タスクの drift もここで catch する。
  - **tier-3 (タスク閉じ時)**: `.claude/commands/finish-task.md` Step 3 が
    並列検査として実行。`schema_dto.rs` / `current.json` を touch した
    タスクのクローズ時点で検出する (2026-04-17 導入)。tier-3 の呼出しは
    `/add-feature` / `/fix-bug` / `/refactor` → `/finish-task` の延長で
    自動的に走る。drift 検出時は Step 4 (commit 提案) に進まず停止する。
- Python 環境前提 (tier-2 / tier-3 共通):
  - Windows: `python` が PATH にある前提 (python.org 版または `py -3` alias)
  - macOS/Linux: `python3` → `python` の順にフォールバック
  - tier-3 (bash / Git Bash) 側は OS を問わず `python3` があればそれを優先
- 比較粒度: JSON 意味同値 (`json.load` + キーソート正規化)
  - CRLF/LF 差異・キー順序揺れは drift 扱いしない (false positive 回避)
  - variant (tagged enum の `type` 値 + `const` 単一値) の missing / extra を個別列挙
- 単体テスト: `scripts/tests/test_check_schema_parity.py` (unittest, 12 ケース)
- Exit code:
  - `0` parity OK / `1` drift 検出 / `2` prototype 側 schema 不在
  - `3` dataset 側 schema 不在 / `4` I/O or JSON parse エラー
- `--machine-readable` オプション:
  - stdout 最終行に `HELPER_EXITCODE=<n>` (0..4) を必ず出力
  - PowerShell 5.1 の `-File` invocation では `$LASTEXITCODE` が不安定なため、
    shell 側はこのセンチネルを regex で parse して exit code を確定する
  - bash 側は `|| rc=$?` で直接取れるのでセンチネル依存なし (使っても害なし)

手動で helper を単体実行することも可:
```
python scripts/check_schema_parity.py --dataset C:/gse-dataset
python scripts/check_schema_parity.py --dataset C:/gse-dataset --machine-readable
```

ロジックを Python 1 本に集約しているため、将来の拡張 (tier-1 への応用・
variant 互換性判定など) は helper 側のみ編集する。ps1/sh は薄い呼出しラッパ。

### 10.4 プライバシー原則

- `raw/` ディレクトリは gse-dataset 側の `.gitignore` で永続的に除外
- 外部被験者 P001+ のデータは暗号化ローカル保管、GitHub (private 含む) 経路を使わない
- `anonymize.py` はスクリプトとして存在するが、Phase 1 では出力を commit しない
