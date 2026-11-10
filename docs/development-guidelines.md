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
  - quarantine 属性 (`com.apple.quarantine`) が未署名ビルドをブロックする場合は
    ★ **`xattr -dr com.apple.quarantine <path>`** で除去する
    （⚠️ ★ **`xattr -cr` は使わない** — 全属性を消して**署名を無効化する恐れ**がある。
    `README.md:147` / `README.ja.md:147` / `docs/participant-setup-guide.md:41` が明示的に禁止しており、
    ここだけが `-cr` のまま食い違っていた。2026-08-04 に是正）
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
- **scope**: engine, hook, ime, overlay, frontend, logger, probe 等（⚠️ **2026-09-01: `wall` を削除** — ADR-015 D1 で該当層が消滅）
- **例**: `feat(engine): add ONNX Runtime inference path`

### バージョニング

- ⚠️★★★ **2026-09-01 訂正 —— README に changelog 節は存在しない。**
  ★ **リリース版は `package.json` / `src-tauri/Cargo.toml` / `src-tauri/tauri.conf.json` の 3 点を同値に保つ**
  （実測 2026-09-01: いずれも `0.1.30`）。`v*` タグ push で `ci.yml` の release job が発火する。
  ★ 設計上の v2.x 系譜は `docs/design-history.md` を正とする（⚠️ **履歴文書であり現行仕様ではない**）
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

⚠️★★★ **`cd src-tauri` を忘れると必ず失敗する。** ★ `Cargo.toml` は **repo 直下に無く `src-tauri/` にある**
（実測 2026-09-01: `ls Cargo.toml` → *No such file or directory*）。repo 直下で叩くと
`error: could not find 'Cargo.toml' in <repo> or any parent directory` で**即座に空振りする**。
→ ★ repo 直下から動かずに叩くなら `--manifest-path src-tauri/Cargo.toml` を付ける（`run.sh` はこの形）。

```bash
cd src-tauri   # ★★★ 以下はすべて src-tauri/ から実行する

# スナップショット生成（初回のみ）
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson > tests/snapshots/minimal.json

# 回帰検証（CI / 手動）
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
# → "OK: N snapshots match ..." で exit 0、差分時は "MISMATCH: ..." で exit 1

# GT メトリクス算出（Phase 1 Task 2、UserLabel 付きセッション向け）
cargo run --bin gse-replay -- <session.ndjson> --metrics         # pretty-print
cargo run --bin gse-replay -- <session.ndjson> --metrics --json  # 構造化 JSON
# ⚠️ 2026-11-07 更新 — モード系フラグは 13 本が相互排他（src-tauri/src/bin/replay.rs の parse_args_from）:
#   --metrics / --segment / --segments / --snapshot / --intervention / --invitation
#   / --probes / --day-questions / --calibration / --sweep / --nudge-diag / --corr-floor / --features
# --json はこのうち --metrics / --segments / --intervention / --calibration
#   / --sweep / --nudge-diag / --corr-floor と併用できる（--snapshot とは併用不可）。

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
- **`gse-replay <s1> [s2 ...] --probes [--utc-offset-secs <N>] [--day-state <path>]`**: 段 1 の問いの行を記録から調停器を回し直して照合（JSON・`s1_replay.rs`）。`--day-questions --utc-offset-secs <N>` は日の問いの回答の後の押下の数。記録・状態ファイルが不正なら exit 1 で stdout は空
- **モード系フラグは相互排他**（13 本・一覧は上のコードブロックのコメント・両指定は exit 1 で stdout は空）
- **`--json` は `--metrics` / `--segments` / `--intervention` 併用必須** (生 snapshot 出力には使わない)

### テストの方針

- `analysis/` モジュールは OS 非依存なので、通常の `#[cfg(test)]` + `cargo test` で両 OS 共通に検証可能
- `input/` モジュールは OS フックに依存するため、統合テストは実機で手動確認
  - ⚠️★★★ **Tauri アプリ本体を実機で手動起動して UI を確認する時、ビルドは
    `npm run tauri build -- --no-bundle`（または `npm run tauri dev`）を使う。
    素の `cargo build --release`（`cargo build --release --features package` も含む）は
    `custom-protocol` Cargo feature が付かず、release プロファイルでもメインウィンドウが
    Vite devUrl (`http://localhost:1420`) 依存のまま残る**（2026-09-09 実機で発覚・
    `.steering/20260904-windows-orphan-verify/decisions.md` 判断3）。この feature は
    `Cargo.toml` に列挙されておらず `tauri-cli` が暗黙で付与するため、bare cargo では
    再現されない。★ **実配布ビルド（CI の `npx tauri build`）はこの経路を通っており無傷。**
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

### ⚠️★★ OS ごとに規則が違うロジックは、**両 OS に対のテストを置く**

`cargo test --workspace` は **CI の matrix で Windows と macOS の両方**で走る。したがって
`#[cfg]` を付けないテストは **両 OS で実行される**。ここで 2 通りの失敗がある:

1. **片方の OS の規則を、両 OS で走らせてしまう**
   → 手元 (macOS) では緑、⚠️ **Windows CI で赤**。
   ★ 2026-08-10 に実際に出した (`liveness::macos_tick_tests` が macOS の許容幅を前提に
   していたのに `cfg` で閉じておらず、Windows の等値比較で落ちた)。
2. ★★ **`cfg` で閉じて満足してしまう**
   → その OS では走らなくなるだけで、⚠️ **もう片方の規則は未検証のまま残る**。
   「CI が緑」は「両方の規則を確かめた」を意味しない。

→ **規約**: OS ごとに実装が分岐する関数を単体テストするときは、
`#[cfg(all(test, target_os = "windows"))]` と `#[cfg(all(test, target_os = "macos"))]` の
**両方**にモジュールを置き、★ **それぞれの OS の規則を肯定形で固定する**。
片方にしか書けない場合は、⚠️ **書けない理由をコメントに残す**
(例: TCC ダイアログのように自動化できない)。

現状の実例は `input/liveness.rs` の `tick_indicates_input`
(Windows = 等値比較 / macOS = 250 ms の許容幅) を参照。

⚠️ ★ OS API を直接呼ぶ関数 (`input/clipboard.rs::clipboard_char_count` / `input/observe_windows.rs` 等) はこの規約の対象外である
(純関数ではないので単体テストの形にならない)。実機手動確認を `.steering/` に残すこと。

### CI/CD パイプライン

⚠️★★★ **2026-09-12 追記 —— workflow は 2 枚ある。** ★ 長らく `ci.yml` 1 枚だったので、
「CI」と言ったら `ci.yml` のことだという前提が各所に残っている。**数えてから読むこと。**

| ファイル | 起動 | 役割 |
|---|---|---|
| `.github/workflows/ci.yml` | `push` (main / `feature/*`)・`pull_request` (main)・`v*` タグ・手動 | ビルド / テスト / 回帰 / リリース |
| ★ `.github/workflows/supply-chain.yml` | **週次 `schedule`**・手動・⚠️ **`paths` 限定の PR** | 供給網の検知 (F-1 / F-2) |

GitHub Actions (`.github/workflows/ci.yml`) で構成済み。`push` (main / `feature/*`)・`pull_request` (main)・`v*` タグで起動する:

- **`check` ジョブ**: matrix ビルド。⚠️★★★ **2026-09-01 訂正 —— runner は self-hosted 実機である。**
  macOS 側は `runs-on: [self-hosted, gse-mac]`、Windows 側は `decide-win-runner` が probe して
  self-hosted `gse-win` ↔ hosted `windows-latest` を切り替える（★ offline なら 30 秒で hosted へ fallback・`ci.yml:129-176`）。
  ⚠️★★★ **2026-09-12 追記 —— 旧文が落としていた 2 ステップ**（★ 前後に足されたのに、ここが追随していなかった）:
  **env 前提の検査**（`redact_home_path` の env 経路テストが無音で skip しないための門・R-4）
  → `cargo build --target` → **`cargo test --features package --workspace --target`**（★ 旧文は `--features package` が抜けていた）
  → スナップショット回帰 (`gse-replay --snapshot`) → schema drift check (`emit_schema`)
  → **clippy ゲート**（`cargo clippy --all-targets --features package --target -- -D warnings`・R-1・2026-09-12 追加）
  ⚠️ **clippy は `-D warnings` なので、toolchain が上がって新 lint が増えると
  コード差分ゼロでも赤くなりうる**。★ そのときは **lint 修正が先**で、`-D warnings` を外して逃げない。
- **`frontend-check` ジョブ** (`runs-on: ubuntu-latest` ＝ ★ **ここだけ hosted**):
  `npm ci` → TypeScript 型チェック → Vite production ビルド →
  ⚠️★★★ **2026-09-01 追記 —— 旧文が落としていた 3 群 5 ステップ**:
  ビネット構成検査 (`check_vignettes.py --self-test` ＋ 本検査・PreReg-1) →
  capabilities gate (`capabilities_gate.py --self-test` ＋ `python3 -m unittest scripts.tests.test_capabilities_gate`) →
  シェル移植性ゲート (`bash scripts/check-shell-portability.sh`) →
  ★ **supply-chain 検査器のテスト** (F-1 / F-2) →
  ★ **workflow 不変条件ゲート** (`check_workflow_invariants.py --self-test` ＋ 本検査 ＋ unittest・F-8 / F-9。
  ⚠️ permissions の**広さ** / third-party の SHA 固定 / `supply-chain.yml` が hosted であることを検査する)
- **`build-windows` / `build-macos` ジョブ**: `v*` タグ時のみ。Windows は **portable exe** (`--no-bundle`)、macOS は **DMG** をアーティファクト化 (macOS は entitlements 付き再署名 ＋ 研究者専用 CLI の strip)
- ★ **`supply-chain` workflow** (`.github/workflows/supply-chain.yml`・**別ファイル**・`ubuntu-latest`):
  3 層を 1 job で検査する —— **toolchain** (`scripts/check_toolchain_advisories.py` が
  `rust-toolchain.toml` の `channel` を rust-lang/rust の advisory と突合) /
  **Rust 依存 630 crate** (`scripts/check_dependency_audit.py` = cargo-audit のラッパー) /
  **npm 本番依存** (`npm audit --omit=dev`)。
  ⚠️★★★ **これは「門」ではなく「信号」である** —— ★ `main` に branch protection が無い
  (2026-09-12 実測: `404 Branch not protected`) ので、赤でもマージは機械的に止まらない。
  ★ 要は **週次 `schedule`** である (⚠️ 新しい advisory は**コード差分ゼロで現れる**ので、
  PR 発火だけでは永久に気づかない)。⚠️ PR 発火は `Cargo.lock` / `rust-toolchain.toml` /
  `package-lock.json` / 検査器そのものを触ったときだけ。
  ★ 検査器の unittest は **`frontend-check` でも**走る (⚠️ `paths` 限定では
  「依存を触らない PR」で 1 度も走らないため)。★ 同じ 3 本は手元でも回せる
  (`docs/verification-runbook.md` §1 (g))。
- **`release` ジョブ**: 両ビルド成功後に GitHub Release を作成。★ **公開するのは 5 アセットだけ** — 被験者向け `gse-next.exe` / `gse-submit.exe` / `*.dmg` と、研究者専用 `gse-unpack(.exe)`。⚠️ NSIS インストーラと `gse-package` は **Phase1 で使われなかったので配らない** (2026-08-03)

> **運用上の注意**: ⚠️★★★ **2026-09-01 訂正 —— 「クラウド CI が動いている」は半分だけ正しい。**
> ★ **self-hosted 実機 (`gse-win` / `gse-mac`) へ移ったのは `check` と `build-macos` だけである。**
> ⚠️ **`build-windows` は意図的に hosted (`windows-latest`) のまま**（`ci.yml:405-410` 逐語:
> 「**本ジョブは hosted のまま**にする。理由: (a) タグ push / 手動発火でしか走らないので恒常的な支出ではない、
> (b) リリース成果物を作るジョブであり、⚠️ **G-GEAR が途中で落ちるとリリースが壊れる**」）。
> ★ **`frontend-check` も hosted (`ubuntu-latest`)**
> (`gse-win` / `gse-mac`) へ移行済みである（移行理由は `ci.yml:138-150` の 2026-08-26 hosted outage の実測コメント）。
> ⚠️ **したがって self-hosted 機の電源・スリープが CI の前提になっている。** offline 時に fallback するのは Windows 側だけで、
> **mac 側は fallback 無しで無条件に self-hosted を指す**（`ci.yml:264` の `runs-on` 三項式）。
> （旧文: 2026-08-10 に PR #94 で `check` (windows / macOS) と `frontend-check` の実行を確認。リリースビルドも v0.1.25 で success)。
> 過去に無料枠超過で run が数秒で落ちた時期があり、その頃の記述が「CI 利用不可」のまま各所に残っていたので訂正する。
> ★ **手元の検証は CI の代替にならない**: macOS では `hook_windows.rs` が 1 行もコンパイルされず、逆に OS 別テストは相手側の OS でも走る (上節)。**両方を回すこと。**
> TCC 権限テストは元々自動化不可で実機手動検証。

## 4. レビュー基準

### 必須チェック

- [ ] `cargo build` が成功する（Windows + macOS 両方でビルド可能）
- [ ] `cargo clippy` の警告がない（または理由付きで `#[allow]`）
- [ ] フックコールバック内にブロッキング処理がない（Windows WH_KEYBOARD_LL / macOS CGEventTap 共通制約）
- [ ] unsafe ブロックに安全性コメントがある
- [ ] Windows: `windows` crate のみ使用（winapi 禁止）/ macOS: `core-graphics` + `core-foundation` + 必要な `#[link]` 宣言
- [ ] macOS: GCD メインキュー必須 API（TIS\*, AXIsProcessTrustedWithOptions）は `dispatch_sync_f` を使用
- [ ] **`analysis/` に OS API が無い**（OS 依存は `input/` + `sensors*.rs` + `overlay_panel.rs` + `lib.rs` の `#[cfg]` ブロックに限る）
      ⚠️ **2026-09-01 訂正 —— `sensors/` というディレクトリは無い**（実体は `src-tauri/src/sensors.rs` / `sensors_macos.rs`）。
      ★ かつ `lib.rs` / `overlay_panel.rs` にも OS API があるので「`input/` + `sensors/` に閉じている」は不成立。
      ★ **不変なのは「`analysis/` に置かない」**であり、これは `pre-edit-banned.sh` が機械ブロックしている

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
- ⚠️★★★ **2026-09-01 訂正 —— GSE は現在いかなるローカル HTTP ポートも開かない。**
  旧文はここに「**Wall Server**: ランダムトークンによるアクセス制御。ローカルネットワークのみ…」と書いていたが、
  `wall_server.rs` は **ADR-015 D1 で削除**され、依存 `tiny_http` / `qrcode` も除去済みである。
  ★ **存在しない攻撃面をセキュリティ節に書き続けるのは、実在する経路から目を逸らす**ので消す。
  → ★ 現行の外部送信経路は **提出パス 1 本のみ**（`packaging.rs` で age 暗号化 → `submission.rs` が
  被験者の確認 `.ok` を要求 → `.age.sent`）。⚠️ **PC ↔ スマホの境界を作るときは ADR-017 D4 の S1–S6 を満たすこと。**
- **macOS TCC 権限**: Input Monitoring / Accessibility 権限は最小限の範囲でリクエストする。`tccutil reset` コマンドによるリカバリパスを維持する。
- **Tauri CSP**: `default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'` (`src-tauri/tauri.conf.json`) — 外部リソースの読み込みを禁止。`img-src` の `data:` は QR コード等のインライン画像のため許可。
- **Tauri capabilities (権限管理)**: Tauri 2.0 では v1 allowlist を使わず `src-tauri/capabilities/default.json` で権限を宣言する (main + overlay + global-shortcut)。新しい IPC コマンドやプラグイン権限を足すときはここを編集する。

## 8. 禁止事項

- ❌ `winapi` crate の使用（`windows` crate v0.58+ のみ）
- ❌ フックコールバック内でのブロッキング操作（Windows WH_KEYBOARD_LL / macOS CGEventTap 共通）
- ❌ グローバル TSF フック（`ITfThreadMgr`）の使用 —— ⚠️★★★ **2026-09-01 訂正: 理由は UIPI ではない。**
  ★ **API 構造上不可能**である（`ITfThreadMgr::Activate` は逐語「Activates TSF for the **calling thread**」であり、
  `ITfSource::AdviseSink` に**リモート対象を指定する引数が構文上存在しない**）。詳細は `docs/agent-shared.md` 制約 7
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
# 注意: 自動生成 ID は不透明なため、ID→被験者の対応表は研究者が別途管理する。
# sync スクリプト (sync-session/sync-all) は自動生成 ID に追従済み (2026-06-19):
# raw/<id>/ のディレクトリ名から PID を導出して metrics/<id>/ に対応付けるため、
# raw と metrics の ID は構造的に一致する (GSE_PID 設定は不要)。詳細は下記バッチ同期と
# .steering/20260619-sync-auto-participant-id/ を参照。

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

**バッチ同期 (複数セッションを一括処理)**: `scripts/sync-all.*` で fallback → raw コピー + 全未処理ファイルの metrics 生成 + 1 commit/push をまとめて行える。`raw/*/` を **participant ごとに反復**し、各ディレクトリ名 (= PID) から `metrics/<PID>/` を決めるため、複数被験者の raw を 1 回でそれぞれ正しい metrics に振り分けられる (ディレクトリ名は logger と同じ allowlist `[A-Za-z0-9_-]`,1..=64 + Windows 予約名拒否 で検証し、不正名はスキップ)。fallback dir の平坦な NDJSON は端末ローカルの PID (`GSE_PID` → `~/.gse/participant_id` → `P000`) で `raw/<id>/` にコピーされる:

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
- **非 ASCII (日本語コメント等) を含む `.ps1` は UTF-8 BOM 付きで保存する** (2026-06-19 判明)。
  PS 5.1 は BOM 無しスクリプトを `[Text.Encoding]::Default` (本機は **CP932/Shift-JIS**) で読むため、
  日本語のバイト列が誤って `#>` を生成し `<# .. #>` comment-based help を途中で閉じる等の parse 破壊が
  起こる (`powershell.exe -File` 実行も同経路で壊れる)。「どの日本語を書くか」で parse 可否が変わる
  脆さなので、ソース `.ps1` は UTF-8 BOM で保存し UTF-8 読みを強制する (これは上記 ① の*出力ファイル*の
  UTF-16 BOM とは別物。ソースの UTF-8 BOM は必須対応)。検証: `[Management.Automation.Language.Parser]::ParseFile(...)`
  が errors 0 を返すこと。

これらは `scripts/sync-session.ps1` 内のコメントにも併記済み。

⚠️★★★ **2026-08-29 訂正: 旧文「bash 側 (`sync-session.sh`) は `set -euo pipefail` +
`bash -n` 構文チェックで十分堅牢 (同種の問題は発生せず)」は反証された。**

★ bash 側も **同型 (日本語のバイト列でパースが変わる) を踏んでいた**:

- ⚠️ macOS 標準の bash は **3.2** で、**多バイト文字を変数名の一部として読む**。
  変数を `${...}` で括らずに書き、その直後に全角括弧を置くと、
  「変数名 + 括弧のバイト」という存在しない変数になり `set -u` で落ちる。
- ⚠️ 実害: `sync-session.sh` の **O1 ガードが `exit 4` に到達できず `exit 1` を返していた**
  (`docs/o1-deletion-ledger.md` §4 の約束を支える番人)。
- ⚠️★ **`bash -n` はこれを検出できない** (実測: 違反ファイルに対し **rc=0**)。
  構文は正しく、**実行時に unbound variable になる**ので構文検査の管轄外である。
- ⚠️ `set -euo pipefail` は「落ちること」を保証するだけで、**落ちる場所を選べない**。
  今回はエラーメッセージを出す行で落ちたため、**exit code の契約ごと壊れた**。

★ **規約**: シェルスクリプトでは **`$name` の直後に多バイト文字が来るなら `${name}` と括る**。
`${` を見た bash は閉じ `}` まで変数名として読むので、後続バイトの解釈に依存しない
(bash 3.2 / 5.x / git-bash / zsh で同じ結果)。

★ **機械で見張る**: `scripts/check-shell-portability.sh` が repo 全体を走査する
(陽性/陰性対照つき)。CI の `frontend-check` と `check-o1-release-readiness.sh` から呼ばれる。
⚠️ 見ているのは**この 1 型だけ**であり、BSD/GNU のコマンド差 (`od` / `sed -i` / `tr` / `grep`)
などは対象外である (スクリプト冒頭に「見ていないもの」を列挙してある)。

詳細: `.steering/20260829-macos-shell-portability/`

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

#### 10.3.2 ⚠️★★★ 解析側が知っておくべき欠測・意味の落とし穴

★ schema が additive なので**古いログも新しい schema で通る**。⚠️ **通ることと、
値が同じ意味を持つことは別**である。★ 解析 (Python / DuckDB / notebook) を書く前に読むこと。

| フィールド | 導入 | ⚠️ 落とし穴 |
|---|---|---|
| `feat.keys` / `feat.bs_keys` | **2026-08-16 (Tier 0 配線)** | ★★★ **それ以前のログには存在しない。** `gse-replay --metrics` は欠測を **`0`** として読むので、**「実測 0 打」と区別できない**。★ 該当セッションでは `gse-replay` が `feat entries have no keys/bs_keys (pre-Tier0-wiring log)` を warn する。⚠️ **`progress_proxy` (= `keys − bs_keys`) をそのセッションから計算しないこと。** |
| `feat.keys` / `feat.bs_keys` | 同上 | ★★★ **累積カウンタではない。窓の右端は `t` ではなく「最後の打鍵時刻」**である。**沈黙中は同じ値が毎秒くり返し出る**（実測: `tests/snapshots/deep_silence.json` は 44 行連続で `keys=12`）。→ ⚠️ **feat 行をまたいで足し上げると同じ打鍵を数十回二重計上する。** |
| `feat.keys` / `feat.bs_keys` | 同上 | ⚠️ **IME 変換中の打鍵は数えない**（特徴量ウィンドウ自体が IME ポーズ中は蓄積しない）。★ 日本語入力主体のセッションでは系統的に過小になる。 |
| `feat.keys` / `feat.bs_keys` | 同上 | ⚠️ **リングバッファ 600 イベント（実質 ~300 打）で頭打ち**になる。BS 長押し等で超えると過小計上 ＋ 窓長が 30 秒未満に切り詰められる。 |
| `paste.external_paste_chars` | capture-schema-freeze 以前 | ⚠️ 取得不能時は `null`。`0` ではない。 |

★ 意味の正本は `src-tauri/src/analysis/loop_step.rs` の `FeatSnapshot::keys` の doc コメント。

### 10.4 プライバシー原則

- `raw/` ディレクトリは gse-dataset 側の `.gitignore` で永続的に除外
- 外部被験者 P001+ のデータは暗号化ローカル保管、GitHub (private 含む) 経路を使わない
- `anonymize.py` はスクリプトとして存在するが、Phase 1 では出力を commit しない

### 10.5 ⚠️★★★ 収集済み信号を使う解析は、**最初に `capabilities` を機械判定する** (ADR-013)

> **SSOT**: `docs/adr/ADR-013-collection-self-description.md` D1 / Migration 3・4。
> **実装**: `scripts/capabilities_gate.py` (`--self-test` つき) / `src-tauri/src/capabilities.rs`。

#### なぜ規約ではなくコードなのか

⚠️ **「計器がコホートを跨げなかった」失敗は既に 2 件起きている。**

1. `feat.keys` / `feat.bs_keys` の配線は **2026-08-16**。★ Phase1 ログはそれ以前なので**存在しない**。
2. `hook_health` / `starved_ms` は Phase1 コホート (63 ファイル) に **1 行も無い**
   —— 記録期間 2026-07-04〜07-24 に対し `input/liveness.rs` の追加は **2026-08-09**
   (＝ **収集の 16 日後**)。

★ 教訓の逐語: **「既存ログにある」は *現行コードが出す* の意味であって、
*対象コホートにある* の意味ではない。**

⚠️ これは「規約が無かった」失敗ではない —— ★ **規約は書いてあったのに適用しなかった**。
→ ⚠️ 人が適用し忘れられる形のままでは 3 件目が起きるので、**検査をコードにする**。

#### 判定表 (3 群 ＋「表に無い」)

| `meta.capabilities` の群 | 該当行 0 行の意味 |
|---|---|
| `unconditional` | ★ **信号が無かった** (測れて、無かった) |
| `threshold_gated` | ⚠️ **判定不能** —— 閾値未達と区別できない (`hook_health` / `starve_window`) |
| `config_gated` | ⚠️★★★ **判定不能** —— 設定で送出元ごと止まっていた可能性 (例: **G1 では probe 系が常に 0 行**) |
| どれにも無い | ⚠️ **計器が無かった** (★ 過去 2 件の失敗はここ) |
| どれにも無いが **≥1 行ある** | ⚠️ **宣言のバグ** → `meta.app_version` で追跡する |

⚠️ **旧ログには `capabilities` キー自体が無い** → ★ 「**計器が無かった**」に倒す。
⚠️ **`hmm_version` では代用できない** —— HMM の版であって「何を記録できるか」ではない。
⚠️★★ **新旧が混ざったコホートは `MIXED` で止める** —— 「一部のファイルにだけ計器がある」
状態で平均を取ると、★ 過去 2 件と同じ結論の誤りが**より見つけにくい形**で再生産される。

#### 使い方 (★ 前処理の**先頭**に置く)

```bash
# ⚠️ PYTHONUTF8=1 必須 (Windows コンソールは cp932)
PYTHONUTF8=1 python scripts/capabilities_gate.py "$GSE_DATASET/raw" \
  --require key --require feat --require starve_window
echo $?    # ★ 0 以外なら 0 行を誤読しうる。⚠️ `| tail` にパイプすると $? が tail のものになる
```

Python の解析からは `preflight()` を **1 行目で**呼ぶ:

```python
from capabilities_gate import preflight
preflight([dataset_dir], required=["key", "starve_window"])   # ⚠️ 誤読しうるなら例外
```

★ `experiments/_template/run.sh` の **Step 0** がこれである。⚠️ **消さないこと。**

#### 「判定不能」を受け入れる場合

★ `--allow-undecidable` を付けてよいのは、**解析が明示的にそれを受け入れる**ときだけである。
⚠️ その場合、`notes.md` の結論は「**無かった**」ではなく **「判定不能」**と書く。
★ 書き分けないなら、フラグを付ける意味が無い。
